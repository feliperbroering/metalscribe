"""Diarization command."""

import logging
from pathlib import Path

import click
from rich.console import Console

from metalscribe.core.audio import convert_to_wav_16k
from metalscribe.core.pyannote import run_diarization
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
    "--speakers",
    "-s",
    type=int,
    default=None,
    help="Number of speakers (optional, auto-detects if not specified)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output JSON file (default: input_02_diarize.json)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose mode",
)
def diarize(input: Path, speakers: int, output: Path, verbose: bool) -> None:
    """Identifies speakers using pyannote.audio."""
    setup_logging(verbose=verbose)

    import time

    start_time = time.time()

    # Convert audio
    wav_path = input.with_suffix(".wav")
    convert_to_wav_16k(input, wav_path)
    conversion_time = time.time() - start_time
    log_timing("Audio conversion", conversion_time)

    # Diarize
    diarize_start = time.time()
    segments = run_diarization(wav_path, num_speakers=speakers)
    diarize_time = time.time() - diarize_start
    log_timing("Diarization", diarize_time)

    # Export JSON
    if output is None:
        output = input.parent / f"{input.stem}_02_diarize.json"

    # Convert to exportable format
    from metalscribe.core.models import MergedSegment

    merged_segments = [
        MergedSegment(
            start_ms=seg.start_ms,
            end_ms=seg.end_ms,
            text="",  # Diarization has no text
            speaker=seg.speaker,
        )
        for seg in segments
    ]

    export_json(merged_segments, output)

    total_time = time.time() - start_time
    log_timing("Total", total_time)

    console.print(f"[green]✓ Diarization complete: {output}[/green]")
