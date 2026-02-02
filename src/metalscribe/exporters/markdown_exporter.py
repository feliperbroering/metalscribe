"""Markdown Exporter."""

import logging
from pathlib import Path
from typing import List, Optional

from metalscribe.core.models import MergedSegment

logger = logging.getLogger(__name__)


def format_timestamp_md(ms: int) -> str:
    """Formats timestamp in readable format (HH:MM:SS)."""
    total_seconds = ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def export_markdown(
    segments: List[MergedSegment],
    output_path: Path,
    title: Optional[str] = None,
    metadata: Optional[dict] = None,
) -> None:
    """
    Exports segments to readable Markdown.

    Args:
        segments: List of merged segments
        output_path: Output Markdown file path
        title: Document title (optional)
        metadata: Additional metadata (optional)
    """
    with open(output_path, "w", encoding="utf-8") as f:
        # Header
        if title:
            f.write(f"# {title}\n\n")
        else:
            f.write("# Transcription\n\n")

        # Metadata
        if metadata:
            f.write("## Metadata\n\n")
            for key, value in metadata.items():
                f.write(f"- **{key}**: {value}\n")
            f.write("\n")

        # Total duration
        if segments:
            total_duration = segments[-1].end_ms - segments[0].start_ms
            duration_str = format_timestamp_md(total_duration)
            f.write(f"**Total duration**: {duration_str}\n\n")

        f.write("---\n\n")

        # Segments
        current_speaker = None
        for seg in segments:
            # Group by speaker
            if seg.speaker != current_speaker:
                if current_speaker is not None:
                    f.write("\n")
                f.write(f"## {seg.speaker}\n\n")
                current_speaker = seg.speaker

            timestamp = format_timestamp_md(seg.start_ms)
            f.write(f"**[{timestamp}]** {seg.text}\n\n")

    logger.info(f"Markdown exported: {output_path}")
