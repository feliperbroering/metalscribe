"""JSON Exporter."""

import json
import logging
from pathlib import Path
from typing import List, Optional

from metalscribe.core.models import DiarizeSegment, MergedSegment, TranscriptSegment

logger = logging.getLogger(__name__)


def export_json(
    segments: List[MergedSegment], output_path: Path, metadata: Optional[dict] = None
) -> None:
    """
    Exports segments to JSON as per spec section 2.3.

    Args:
        segments: List of merged segments
        output_path: Output JSON file path
        metadata: Additional metadata (optional)
    """
    output = {
        "metadata": metadata or {},
        "segments": [
            {
                "start_ms": seg.start_ms,
                "end_ms": seg.end_ms,
                "text": seg.text,
                "speaker": seg.speaker,
            }
            for seg in segments
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"JSON exported: {output_path}")


def export_transcript_json(
    segments: List[TranscriptSegment], output_path: Path, metadata: Optional[dict] = None
) -> None:
    """
    Exports transcription segments (without speaker info) to JSON.

    Args:
        segments: List of transcription segments
        output_path: Output JSON file path
        metadata: Additional metadata (optional)
    """
    output = {
        "metadata": metadata or {},
        "segments": [
            {
                "start_ms": seg.start_ms,
                "end_ms": seg.end_ms,
                "text": seg.text,
            }
            for seg in segments
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"Transcription JSON exported: {output_path}")


def export_diarize_json(
    segments: List[DiarizeSegment], output_path: Path, metadata: Optional[dict] = None
) -> None:
    """
    Exports diarization segments (speaker info only) to JSON.

    Args:
        segments: List of diarization segments
        output_path: Output JSON file path
        metadata: Additional metadata (optional)
    """
    output = {
        "metadata": metadata or {},
        "segments": [
            {
                "start_ms": seg.start_ms,
                "end_ms": seg.end_ms,
                "speaker": seg.speaker,
            }
            for seg in segments
        ],
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    logger.info(f"Diarization JSON exported: {output_path}")
