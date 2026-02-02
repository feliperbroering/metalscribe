"""Merge algorithm for transcription and diarization."""

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
    Calculates overlap ratio between two segments.

    Returns:
        Overlap ratio (0.0 to 1.0)
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
    Merges transcription and diarization segments using O(N+M) two-pointer algorithm.

    For each transcription segment, finds the diarization segment with highest overlap
    and assigns the corresponding speaker.

    Args:
        transcript_segments: Transcription segments sorted by time
        diarize_segments: Diarization segments sorted by time

    Returns:
        List of MergedSegment with text and speaker
    """
    if not transcript_segments:
        return []

    if not diarize_segments:
        # If no diarization, return transcription without speaker
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

        # Find diarization segment with highest overlap
        # Uses two-pointer: starts from where it stopped (diarize_idx) and advances
        for i in range(diarize_idx, len(diarize_segments)):
            diarize_seg = diarize_segments[i]

            # If diarize is too early, skip
            if diarize_seg.end_ms < transcript_seg.start_ms:
                diarize_idx = i + 1
                continue

            # If diarize is too late, stop
            if diarize_seg.start_ms > transcript_seg.end_ms:
                break

            # Calculate overlap
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

    logger.info(f"Merge complete: {len(merged)} combined segments")
    return merged
