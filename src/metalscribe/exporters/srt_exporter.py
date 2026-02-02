"""SRT Exporter."""

import logging
from pathlib import Path
from typing import List

from metalscribe.core.models import MergedSegment

logger = logging.getLogger(__name__)


def format_timestamp(ms: int) -> str:
    """Formats timestamp in SRT format (HH:MM:SS,mmm)."""
    total_seconds = ms // 1000
    milliseconds = ms % 1000

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def export_srt(segments: List[MergedSegment], output_path: Path) -> None:
    """
    Exports segments to SRT with speaker prefix.

    Format: [SPEAKER_00] text

    Args:
        segments: List of merged segments
        output_path: Output SRT file path
    """
    with open(output_path, "w", encoding="utf-8") as f:
        for idx, seg in enumerate(segments, 1):
            start_time = format_timestamp(seg.start_ms)
            end_time = format_timestamp(seg.end_ms)

            # Speaker prefix as per spec section 6.3
            text_with_speaker = f"[{seg.speaker}] {seg.text}"

            f.write(f"{idx}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text_with_speaker}\n")
            f.write("\n")

    logger.info(f"SRT exported: {output_path}")
