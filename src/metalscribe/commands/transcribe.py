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
    type=click.Choice(
        [
            "tiny",
            "tiny.en",
            "tiny-q5_1",
            "tiny.en-q5_1",
            "tiny-q8_0",
            "base",
            "base.en",
            "base-q5_1",
            "base.en-q5_1",
            "base-q8_0",
            "small",
            "small.en",
            "small.en-tdrz",
            "small-q5_1",
            "small.en-q5_1",
            "small-q8_0",
            "medium",
            "medium.en",
            "medium-q5_0",
            "medium.en-q5_0",
            "medium-q8_0",
            "large-v1",
            "large-v2",
            "large-v2-q5_0",
            "large-v2-q8_0",
            "large-v3",
            "large-v3-q5_0",
            "large-v3-turbo",
            "large-v3-turbo-q5_0",
            "large-v3-turbo-q8_0",
        ],
        case_sensitive=False,
    ),
    default="large-v3-q5_0",
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
    help="Output JSON file (default: input_01_transcript.json)",
)
@click.option(
    "--limit",
    type=float,
    default=None,
    help="Limit audio processing to X minutes (for testing)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose mode",
)
def transcribe(input: Path, model: str, lang: str, output: Path, limit: float, verbose: bool) -> None:
    """Transcribes audio using whisper.cpp."""
    setup_logging(verbose=verbose)

    import time

    start_time = time.time()

    # Convert audio
    wav_path = input.with_suffix(".wav")
    convert_to_wav_16k(input, wav_path, limit_minutes=limit)
    conversion_time = time.time() - start_time
    log_timing("Audio conversion", conversion_time)

    # Determine outputs
    if output is None:
        metalscribe_output = input.parent / f"{input.stem}_01_transcript.json"
        # Use input stem for raw whisper outputs
        whisper_base = input.parent / input.stem
    else:
        metalscribe_output = output
        # Derive whisper base from output
        whisper_base = output.parent / output.stem
    
    # Check for collision on JSON
    if metalscribe_output == whisper_base.with_suffix(".json"):
        whisper_base = output.parent / f"{output.stem}_raw"

    # Transcribe
    transcribe_start = time.time()
    segments = run_transcription(
        wav_path, model_name=model, language=lang, output_base=whisper_base, verbose=verbose
    )
    transcribe_time = time.time() - transcribe_start
    log_timing("Transcription", transcribe_time)

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

    export_json(merged_segments, metalscribe_output)

    total_time = time.time() - start_time
    log_timing("Total", total_time)

    console.print(f"[green]✓ Transcription complete: {metalscribe_output}[/green]")
    console.print(f"[blue]  Raw Whisper outputs saved to: {whisper_base}.*[/blue]")
