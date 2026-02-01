"""Algoritmo de merge de transcrição e diarização."""

import logging
from typing import List

from metalscribe.core.models import DiarizeSegment, MergedSegment, TranscriptSegment

logger = logging.getLogger(__name__)


def calculate_overlap_ratio(
    transcript_start: int,
    transcript_end: int,
    diarize_start: int,
    diarize_end: int,
) -> float:
    """
    Calcula ratio de overlap entre dois segmentos.

    Returns:
        Ratio de overlap (0.0 a 1.0)
    """
    overlap_start = max(transcript_start, diarize_start)
    overlap_end = min(transcript_end, diarize_end)

    if overlap_start >= overlap_end:
        return 0.0

    overlap_duration = overlap_end - overlap_start
    transcript_duration = transcript_end - transcript_start

    if transcript_duration == 0:
        return 0.0

    return overlap_duration / transcript_duration


def merge_segments(
    transcript_segments: List[TranscriptSegment],
    diarize_segments: List[DiarizeSegment],
) -> List[MergedSegment]:
    """
    Combina segmentos de transcrição e diarização usando algoritmo O(N+M) two-pointer.

    Para cada segmento de transcrição, encontra o segmento de diarização com maior overlap
    e atribui o speaker correspondente.

    Args:
        transcript_segments: Segmentos de transcrição ordenados por tempo
        diarize_segments: Segmentos de diarização ordenados por tempo

    Returns:
        Lista de MergedSegment com texto e speaker
    """
    if not transcript_segments:
        return []

    if not diarize_segments:
        # Se não há diarização, retorna transcrição sem speaker
        return [
            MergedSegment(
                start_ms=seg.start_ms,
                end_ms=seg.end_ms,
                text=seg.text,
                speaker="UNKNOWN",
            )
            for seg in transcript_segments
        ]

    merged = []
    diarize_idx = 0

    for transcript_seg in transcript_segments:
        best_speaker = "UNKNOWN"
        best_overlap = 0.0

        # Procura segmento de diarização com maior overlap
        # Usa two-pointer: começa de onde parou (diarize_idx) e avança
        for i in range(diarize_idx, len(diarize_segments)):
            diarize_seg = diarize_segments[i]

            # Se diarize está muito antes, pode pular
            if diarize_seg.end_ms < transcript_seg.start_ms:
                diarize_idx = i + 1
                continue

            # Se diarize está muito depois, pode parar
            if diarize_seg.start_ms > transcript_seg.end_ms:
                break

            # Calcula overlap
            overlap = calculate_overlap_ratio(
                transcript_seg.start_ms,
                transcript_seg.end_ms,
                diarize_seg.start_ms,
                diarize_seg.end_ms,
            )

            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = diarize_seg.speaker

        merged.append(
            MergedSegment(
                start_ms=transcript_seg.start_ms,
                end_ms=transcript_seg.end_ms,
                text=transcript_seg.text,
                speaker=best_speaker,
            )
        )

    logger.info(f"Merge concluído: {len(merged)} segmentos combinados")
    return merged
