"""Wrapper for whisper.cpp."""

import logging
import tempfile
from pathlib import Path
from typing import List, Optional

from metalscribe.config import ExitCode, get_brew_prefix
from metalscribe.core.models import TranscriptSegment
from metalscribe.core.setup import download_whisper_model
from metalscribe.parsers.whisper_parser import parse_whisper_output
from metalscribe.utils.subprocess import run_command

logger = logging.getLogger(__name__)


def run_transcription(
    audio_path: Path,
    model_name: str = "large-v3",
    language: Optional[str] = None,
    output_json: Optional[Path] = None,
) -> List[TranscriptSegment]:
    """
    Runs transcription using whisper.cpp with Metal GPU.

    Args:
        audio_path: Path to WAV 16kHz file
        model_name: Model name (tiny, base, small, medium, large-v3)
        language: Language code (optional, e.g., 'pt')
        output_json: Path to save JSON (optional)

    Returns:
        List of TranscriptSegment

    Raises:
        SystemExit: If transcription fails
    """
    # Find whisper binary
    from metalscribe.config import get_cache_dir

    brew_prefix = get_brew_prefix()
    cache_dir = get_cache_dir()

    whisper_paths = [
        # Priority 1: locally compiled in cache
        cache_dir / "whisper.cpp" / "build" / "bin" / "whisper-cli",
        # Priority 2: Homebrew
        brew_prefix / "bin" / "whisper",
        brew_prefix / "bin" / "whisper-cli",
        # Priority 3: global paths
        Path("/usr/local/bin/whisper"),
        Path("/usr/local/bin/whisper-cli"),
    ]

    whisper_bin = None
    for path in whisper_paths:
        if path.exists():
            whisper_bin = path
            break

    if not whisper_bin:
        logger.error("whisper.cpp not found. Run: metalscribe doctor --setup")
        exit(ExitCode.MISSING_DEPENDENCY)

    # Download model if needed
    model_path = download_whisper_model(model_name)

    # Prepare output JSON
    if output_json is None:
        output_json = Path(tempfile.mktemp(suffix=".json"))

    # Remove .json extension for -of (whisper adds automatically)
    output_base = str(output_json).rsplit(".json", 1)[0]

    logger.info(f"Transcribing with model {model_name}...")

    # Whisper command: whisper -m model.ggml -f audio.wav -oj -of output_base
    cmd = [
        str(whisper_bin),
        "-m",
        str(model_path),
        "-f",
        str(audio_path),
        "-oj",  # Output JSON
        "-of",  # Output file path (without extension)
        output_base,
    ]

    if language:
        cmd.extend(["-l", language])

    # Run transcription
    try:
        run_command(cmd, timeout=3600)  # 1 hour timeout

        if not output_json.exists():
            logger.error(f"Output JSON not found: {output_json}")
            exit(ExitCode.TRANSCRIPTION_FAILED)

        # Parse result
        segments = parse_whisper_output(output_json)

        logger.info(f"Transcription complete: {len(segments)} segments")
        return segments

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        exit(ExitCode.TRANSCRIPTION_FAILED)
