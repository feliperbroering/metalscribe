"""Combine command."""

import logging
from pathlib import Path

import click
from rich.console import Console

from metalscribe.core.merge import merge_segments
from metalscribe.exporters.markdown_exporter import export_markdown
from metalscribe.parsers.diarize_parser import parse_diarize_output
from metalscribe.parsers.whisper_parser import parse_whisper_output
from metalscribe.utils.logging import log_timing, setup_logging

console = Console()
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--transcript",
    "-t",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Transcription JSON file",
)
@click.option(
    "--diarize",
    "-d",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Diarization JSON file",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output files prefix (default: based on transcript)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose mode",
)
def combine(transcript: Path, diarize: Path, output: Path, verbose: bool) -> None:
    """Combines transcription and diarization results."""
    setup_logging(verbose=verbose)

    import time

    start_time = time.time()

    # Parse inputs
    console.print("[cyan]Loading files...[/cyan]")
    transcript_segments = parse_whisper_output(transcript)
    diarize_segments = parse_diarize_output(diarize)

    load_time = time.time() - start_time
    log_timing("Loading", load_time)

    # Merge
    console.print("[cyan]Merging segments...[/cyan]")
    merge_start = time.time()
    merged = merge_segments(transcript_segments, diarize_segments)
    merge_time = time.time() - merge_start
    log_timing("Merge", merge_time)

    # Determine output prefix
    # Extract base name from transcript file (remove _01_transcript.json)
    if output is None:
        stem = transcript.stem
        if "_01_transcript" in stem:
            base_name = stem.replace("_01_transcript", "")
        else:
            base_name = stem
        output = transcript.parent / base_name
    else:
        output = Path(output)

    # Export only merged markdown (no .json or .srt)
    console.print("[cyan]Exporting markdown...[/cyan]")
    export_start = time.time()

    merged_md_path = output.parent / f"{output.stem}_03_merged.md"
    export_markdown(merged, merged_md_path)

    export_time = time.time() - export_start
    log_timing("Export", export_time)

    total_time = time.time() - start_time
    log_timing("Total", total_time)

    console.print(f"[green]✓ Generated file: {merged_md_path}[/green]")
