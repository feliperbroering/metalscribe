"""Parser for pyannote.audio output."""

import json
import logging
from pathlib import Path
from typing import List

from metalscribe.core.models import DiarizeSegment

logger = logging.getLogger(__name__)


def parse_diarize_output(json_path: Path) -> List[DiarizeSegment]:
    """
    Parses pyannote.audio JSON output.

    Args:
        json_path: Path to JSON output file

    Returns:
        List of normalized DiarizeSegment

    Raises:
        ValueError: If format is invalid
    """
    with open(json_path) as f:
        data = json.load(f)

    segments = []

    # pyannote format: annotation.tracks[SPEAKER_XX] = [{"segment": {"start": X, "end": Y}}]
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
        raise ValueError("Invalid JSON format: expected 'annotation.tracks'")

    # Sort by start time
    segments.sort(key=lambda s: s.start_ms)

    logger.info(f"Parsed {len(segments)} diarization segments")
    return segments
