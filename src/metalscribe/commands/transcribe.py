"""Transcription command."""

import logging
from pathlib import Path

import click
from rich.console import Console

from metalscribe.core.audio import convert_to_wav_16k
from metalscribe.core.models import MergedSegment
from metalscribe.core.whisper import run_transcription
from metalscribe.exporters.json_exporter import export_json
from metalscribe.utils.logging import log_timing, setup_logging

console = Console()
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Input audio file",
)
@click.option(
    "--model",
    "-m",
    type=click.Choice(["tiny", "base", "small", "medium", "large-v3"], case_sensitive=False),
    default="large-v3",
    help="Whisper model",
)
@click.option(
    "--lang",
    "-l",
    type=str,
    default=None,
    help="Language code (e.g., pt, en)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output JSON file (default: input_transcript.json)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose mode",
)
def transcribe(input: Path, model: str, lang: str, output: Path, verbose: bool) -> None:
    """Transcribes audio using whisper.cpp."""
    setup_logging(verbose=verbose)

    import time

    start_time = time.time()

    # Convert audio
    wav_path = input.with_suffix(".wav")
    convert_to_wav_16k(input, wav_path)
    conversion_time = time.time() - start_time
    log_timing("Audio conversion", conversion_time)

    # Transcribe
    transcribe_start = time.time()
    segments = run_transcription(wav_path, model_name=model, language=lang)
    transcribe_time = time.time() - transcribe_start
    log_timing("Transcription", transcribe_time)

    # Export JSON
    if output is None:
        output = input.with_suffix("").with_suffix("_transcript.json")

    # Convert to MergedSegment (no speaker)
    merged_segments = [
        MergedSegment(
            start_ms=seg.start_ms,
            end_ms=seg.end_ms,
            text=seg.text,
            speaker="UNKNOWN",
        )
        for seg in segments
    ]

    export_json(merged_segments, output)

    total_time = time.time() - start_time
    log_timing("Total", total_time)

    console.print(f"[green]✓ Transcription complete: {output}[/green]")
