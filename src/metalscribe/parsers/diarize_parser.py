"""Parser de output do pyannote.audio."""

import json
import logging
from pathlib import Path
from typing import List

from metalscribe.core.models import DiarizeSegment

logger = logging.getLogger(__name__)


def parse_diarize_output(json_path: Path) -> List[DiarizeSegment]:
    """
    Parseia output JSON do pyannote.audio.

    Args:
        json_path: Caminho do arquivo JSON de output

    Returns:
        Lista de DiarizeSegment normalizados

    Raises:
        ValueError: Se formato for inválido
    """
    with open(json_path) as f:
        data = json.load(f)

    segments = []

    # Formato pyannote: annotation.tracks[SPEAKER_XX] = [{"segment": {"start": X, "end": Y}}]
    if "annotation" in data:
        annotation = data["annotation"]
        if "tracks" in annotation:
            for speaker, track_segments in annotation["tracks"].items():
                for item in track_segments:
                    if "segment" in item:
                        seg = item["segment"]
                        start = float(seg.get("start", 0))
                        end = float(seg.get("end", start))

                        segments.append(
                            DiarizeSegment(
                                start_ms=int(start * 1000),
                                end_ms=int(end * 1000),
                                speaker=speaker,
                            )
                        )
    else:
        raise ValueError("Formato JSON inválido: esperado 'annotation.tracks'")

    # Ordena por tempo de início
    segments.sort(key=lambda s: s.start_ms)

    logger.info(f"Parseados {len(segments)} segmentos de diarização")
    return segments
