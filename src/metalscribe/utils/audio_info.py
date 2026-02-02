"""Audio information utilities."""

import json
import logging
from pathlib import Path

from metalscribe.utils.subprocess import run_command

logger = logging.getLogger(__name__)


def get_audio_duration(audio_path: Path) -> float:
    """
    Gets audio duration in seconds using ffprobe.

    Args:
        audio_path: Audio file path

    Returns:
        Duration in seconds
    """
    try:
        result = run_command(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
                str(audio_path),
            ]
        )

        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
        return duration
    except Exception as e:
        logger.warning(f"Could not get audio duration: {e}")
        return 0.0
