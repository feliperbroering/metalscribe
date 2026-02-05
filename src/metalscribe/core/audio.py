"""Audio conversion."""

import logging
from pathlib import Path

from metalscribe.config import ExitCode
from metalscribe.utils.subprocess import run_command

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = {
    ".m4a",
    ".mp3",
    ".mp4",
    ".flac",
    ".ogg",
    ".webm",
    ".aac",
    ".wma",
    ".aiff",
    ".wav",
}


def convert_to_wav_16k(input_path: Path, output_path: Path, limit_minutes: float | None = None) -> None:
    """
    Converts audio to WAV 16kHz mono using ffmpeg.

    Args:
        input_path: Input file path
        output_path: Output WAV file path
        limit_minutes: Optional limit in minutes to process

    Raises:
        SystemExit: If conversion fails
    """
    if not input_path.exists():
        logger.error(f"File not found: {input_path}")
        exit(ExitCode.INVALID_INPUT)

    suffix = input_path.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        logger.warning(f"Format {suffix} might not be supported")

    logger.info(f"Converting {input_path} to WAV 16kHz mono...")

    # ffmpeg -i input -ar 16000 -ac 1 output.wav
    cmd = [
        "ffmpeg",
        "-i",
        str(input_path),
        "-ar",
        "16000",  # Sample rate 16kHz
        "-ac",
        "1",  # Mono
    ]

    if limit_minutes:
        limit_seconds = int(limit_minutes * 60)
        logger.info(f"Limiting audio to {limit_minutes} minutes ({limit_seconds} seconds)")
        cmd.extend(["-t", str(limit_seconds)])

    cmd.extend([
        "-y",  # Overwrite if exists
        str(output_path),
    ])

    run_command(cmd)

    if not output_path.exists():
        logger.error(f"Failed to convert audio: {output_path}")
        exit(ExitCode.AUDIO_CONVERSION_FAILED)

    logger.info(f"Audio converted: {output_path}")
