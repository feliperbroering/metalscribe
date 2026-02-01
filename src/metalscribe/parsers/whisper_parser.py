"""Parser de output do whisper.cpp."""

import json
import logging
from pathlib import Path
from typing import List

from metalscribe.core.models import TranscriptSegment

logger = logging.getLogger(__name__)


def parse_whisper_output(json_path: Path) -> List[TranscriptSegment]:
    """
    Parseia output JSON do whisper.cpp de forma tolerante.

    Args:
        json_path: Caminho do arquivo JSON de output

    Returns:
        Lista de TranscriptSegment normalizados

    Raises:
        ValueError: Se formato for inválido
    """
    with open(json_path) as f:
        data = json.load(f)

    segments = []

    # Suporta diferentes formatos de output do whisper
    if "transcription" in data:
        # Formato whisper.cpp CLI (usa 'transcription' e 'offsets' em ms)
        for seg in data["transcription"]:
            offsets = seg.get("offsets", {})
            start_ms = int(offsets.get("from", 0))
            end_ms = int(offsets.get("to", start_ms))
            text = seg.get("text", "").strip()

            # Ignora segmentos vazios ou placeholders
            if text and not text.startswith("[BLANK_AUDIO]"):
                segments.append(
                    TranscriptSegment(
                        start_ms=start_ms,
                        end_ms=end_ms,
                        text=text,
                    )
                )
    elif "segments" in data:
        # Formato padrão com segments (segundos)
        for seg in data["segments"]:
            start = float(seg.get("start", 0))
            end = float(seg.get("end", start))
            text = seg.get("text", "").strip()

            if text:
                segments.append(
                    TranscriptSegment(
                        start_ms=int(start * 1000),
                        end_ms=int(end * 1000),
                        text=text,
                    )
                )
    elif isinstance(data, list):
        # Formato alternativo: lista direta de segmentos
        for seg in data:
            start = float(seg.get("start", 0))
            end = float(seg.get("end", start))
            text = seg.get("text", "").strip()

            if text:
                segments.append(
                    TranscriptSegment(
                        start_ms=int(start * 1000),
                        end_ms=int(end * 1000),
                        text=text,
                    )
                )
    else:
        raise ValueError("Formato JSON inválido: esperado 'transcription', 'segments' ou lista")

    logger.info(f"Parseados {len(segments)} segmentos de transcrição")
    return segments
