"""Run command - full pipeline."""

import logging
import tempfile
from pathlib import Path

import click
from rich.console import Console

from metalscribe.config import DEFAULT_LANGUAGE, get_prompt_language
from metalscribe.core.audio import convert_to_wav_16k
from metalscribe.core.merge import merge_segments
from metalscribe.core.pyannote import run_diarization
from metalscribe.core.whisper import run_transcription
from metalscribe.exporters.json_exporter import (
    export_diarize_json,
    export_json,
    export_transcript_json,
)
from metalscribe.exporters.markdown_exporter import export_markdown
from metalscribe.exporters.srt_exporter import export_srt
from metalscribe.utils.audio_info import get_audio_duration
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
    default=DEFAULT_LANGUAGE,
    help=f"Language code (e.g., pt, en). Default: {DEFAULT_LANGUAGE}",
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
    help="Output files prefix (default: based on input)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose mode",
)
def run(input: Path, model: str, lang: str, speakers: int, output: Path, verbose: bool) -> None:
    """Full pipeline: transcription + diarization + merge + export."""
    setup_logging(verbose=verbose)

    import time

    start_time = time.time()

    # Determine output prefix
    if output is None:
        # Remove extension and add _merged suffix
        output = input.parent / f"{input.stem}_merged"
    else:
        output = Path(output)

    # Get audio duration to calculate RTF
    audio_duration = get_audio_duration(input)

    # Step 1: Audio conversion
    console.print("[cyan]Step 1: Converting audio...[/cyan]")
    wav_path = Path(tempfile.mktemp(suffix=".wav"))
    convert_start = time.time()
    convert_to_wav_16k(input, wav_path)
    convert_time = time.time() - convert_start
    convert_rtf = convert_time / audio_duration if audio_duration > 0 else None
    log_timing("Conversion", convert_time, rtf=convert_rtf)

    # Step 2: Transcription
    console.print("[cyan]Step 2: Transcribing...[/cyan]")
    transcript_json = Path(tempfile.mktemp(suffix=".json"))
    transcribe_start = time.time()
    transcript_segments = run_transcription(
        wav_path, model_name=model, language=lang, output_json=transcript_json
    )
    transcribe_time = time.time() - transcribe_start
    transcribe_rtf = transcribe_time / audio_duration if audio_duration > 0 else None
    log_timing("Transcription", transcribe_time, rtf=transcribe_rtf)

    # Step 3: Diarization
    console.print("[cyan]Step 3: Diarizing...[/cyan]")
    diarize_json = Path(tempfile.mktemp(suffix=".json"))
    diarize_start = time.time()
    diarize_segments = run_diarization(wav_path, num_speakers=speakers, output_json=diarize_json)
    diarize_time = time.time() - diarize_start
    diarize_rtf = diarize_time / audio_duration if audio_duration > 0 else None
    log_timing("Diarization", diarize_time, rtf=diarize_rtf)

    # Step 4: Merge
    console.print("[cyan]Step 4: Combining...[/cyan]")
    merge_start = time.time()
    merged = merge_segments(transcript_segments, diarize_segments)
    merge_time = time.time() - merge_start
    log_timing("Merge", merge_time)

    # Step 5: Export
    console.print("[cyan]Step 5: Exporting...[/cyan]")
    export_start = time.time()

    json_path = output.with_suffix(".json")
    srt_path = output.with_suffix(".srt")
    md_path = output.with_suffix(".md")
    transcript_json_path = output.parent / f"{output.stem}_transcript.json"
    diarize_json_path = output.parent / f"{output.stem}_diarize.json"

    # Resolve prompt language from Whisper language code
    prompt_language = get_prompt_language(lang)

    metadata = {
        "model": model,
        "language": lang,
        "prompt_language": prompt_language,
        "num_speakers": speakers or "auto",
        "input_file": str(input),
    }

    # Export transcription only (without speaker info)
    transcript_metadata = {
        "model": model,
        "language": lang,
        "input_file": str(input),
    }
    export_transcript_json(transcript_segments, transcript_json_path, metadata=transcript_metadata)

    # Export diarization only (speaker info only)
    diarize_metadata = {
        "num_speakers": speakers or "auto",
        "input_file": str(input),
    }
    export_diarize_json(diarize_segments, diarize_json_path, metadata=diarize_metadata)

    # Export merged results
    export_json(merged, json_path, metadata=metadata)
    export_srt(merged, srt_path)
    export_markdown(merged, md_path, title=input.stem, metadata=metadata)

    export_time = time.time() - export_start
    log_timing("Export", export_time)

    # Timings log
    timings_log = output.with_suffix(".timings.log")
    total_time = time.time() - start_time
    total_rtf = total_time / audio_duration if audio_duration > 0 else None
    with open(timings_log, "w") as f:
        f.write(f"Audio duration: {audio_duration:.2f}s\n")
        f.write(f"\nConversion: {convert_time:.2f}s")
        if convert_rtf:
            f.write(f" (RTF: {convert_rtf:.3f})")
        f.write(f"\nTranscription: {transcribe_time:.2f}s")
        if transcribe_rtf:
            f.write(f" (RTF: {transcribe_rtf:.3f})")
        f.write(f"\nDiarization: {diarize_time:.2f}s")
        if diarize_rtf:
            f.write(f" (RTF: {diarize_rtf:.3f})")
        f.write(f"\nMerge: {merge_time:.2f}s\n")
        f.write(f"Export: {export_time:.2f}s\n")
        f.write(f"\nTotal: {total_time:.2f}s")
        if total_rtf:
            f.write(f" (RTF: {total_rtf:.3f})")
        f.write("\n")

    log_timing("Total", total_time)

    console.print("\n[green]✓ Pipeline complete![/green]")
    console.print("[green]Generated files:[/green]")
    console.print(f"  - {transcript_json_path} (transcription only)")
    console.print(f"  - {diarize_json_path} (diarization only)")
    console.print(f"  - {json_path} (merged)")
    console.print(f"  - {srt_path}")
    console.print(f"  - {md_path}")
    console.print(f"  - {timings_log}")
