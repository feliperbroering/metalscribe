"""Parser for whisper.cpp output."""

import json
import logging
from pathlib import Path
from typing import List

from metalscribe.core.models import TranscriptSegment

logger = logging.getLogger(__name__)


def parse_whisper_output(json_path: Path) -> List[TranscriptSegment]:
    """
    Parses whisper.cpp JSON output tolerantly.

    Args:
        json_path: Path to JSON output file

    Returns:
        List of normalized TranscriptSegment

    Raises:
        ValueError: If format is invalid
    """
    with open(json_path) as f:
        data = json.load(f)

    segments = []

    # Supports different whisper output formats
    if "transcription" in data:
        # whisper.cpp CLI format (uses 'transcription' and 'offsets' in ms)
        for seg in data["transcription"]:
            offsets = seg.get("offsets", {})
            start_ms = int(offsets.get("from", 0))
            end_ms = int(offsets.get("to", start_ms))
            text = seg.get("text", "").strip()

            # Ignore empty segments or placeholders
            if text and not text.startswith("[BLANK_AUDIO]"):
                segments.append(
                    TranscriptSegment(
                        start_ms=start_ms,
                        end_ms=end_ms,
                        text=text,
                    )
                )
    elif "segments" in data:
        # Standard format with segments (seconds)
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
        # Alternative format: direct list of segments
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
        raise ValueError("Invalid JSON format: expected 'transcription', 'segments' or list")

    logger.info(f"Parsed {len(segments)} transcription segments")
    return segments
