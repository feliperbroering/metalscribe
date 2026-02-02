"""Wrapper for pyannote.audio."""

import logging
import tempfile
from pathlib import Path
from typing import List, Optional

from metalscribe.config import ExitCode, get_pyannote_venv_path
from metalscribe.core.checks import validate_hf_token
from metalscribe.core.models import DiarizeSegment
from metalscribe.parsers.diarize_parser import parse_diarize_output
from metalscribe.utils.subprocess import run_command

logger = logging.getLogger(__name__)


def run_diarization(
    audio_path: Path,
    num_speakers: Optional[int] = None,
    output_json: Optional[Path] = None,
) -> List[DiarizeSegment]:
    """
    Runs diarization using pyannote.audio with MPS GPU.

    Args:
        audio_path: Path to WAV 16kHz file
        num_speakers: Number of speakers (optional, auto-detects if None)
        output_json: Path to save JSON (optional)

    Returns:
        List of DiarizeSegment

    Raises:
        SystemExit: If diarization fails
    """
    venv_path = get_pyannote_venv_path()
    python_path = venv_path / "bin" / "python"

    if not python_path.exists():
        logger.error("pyannote.audio is not configured. Run: metalscribe doctor --setup")
        exit(ExitCode.MISSING_DEPENDENCY)

    # Validate token
    token = validate_hf_token()

    # Prepare temporary output JSON if not provided
    if output_json is None:
        output_json = Path(tempfile.mktemp(suffix=".json"))

    logger.info("Running diarization...")

    # Inline Python script to run diarization
    script = f"""
import os
os.environ['HF_TOKEN'] = '{token}'

from pyannote.audio import Pipeline
import torch
import json

# Use MPS if available
device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
print(f"Using device: {{device}}")

# Load pipeline
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=os.environ.get('HF_TOKEN')
)
pipeline.to(device)

# Run diarization
audio_file = "{audio_path}"
diarization = pipeline(audio_file, num_speakers={num_speakers if num_speakers else "None"})

# Convert to JSON format
output = {{
    "uri": audio_file,
    "annotation": {{
        "uri": audio_file,
        "timeline": [],
        "tracks": {{}}
    }}
}}

for turn, _, speaker in diarization.itertracks(yield_label=True):
    speaker_key = str(speaker)
    if speaker_key not in output["annotation"]["tracks"]:
        output["annotation"]["tracks"][speaker_key] = []

    output["annotation"]["tracks"][speaker_key].append({{
        "segment": {{
            "start": turn.start,
            "end": turn.end
        }}
    }})

# Save JSON
with open("{output_json}", "w") as f:
    json.dump(output, f, indent=2)

print(f"Diarization complete: {{len(output['annotation']['tracks'])}} speakers")
"""

    try:
        run_command(
            [str(python_path), "-c", script],
            timeout=3600,  # 1 hour timeout
        )

        if not output_json.exists():
            logger.error(f"Output JSON not found: {output_json}")
            exit(ExitCode.DIARIZATION_FAILED)

        # Parse result
        segments = parse_diarize_output(output_json)

        logger.info(f"Diarization complete: {len(segments)} segments")
        return segments

    except Exception as e:
        logger.error(f"Error during diarization: {e}")
        if hasattr(e, "stderr") and e.stderr:
            logger.error(f"stderr: {e.stderr}")
        exit(ExitCode.DIARIZATION_FAILED)
