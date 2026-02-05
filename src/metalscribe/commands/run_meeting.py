"""Run meeting command - full pipeline with refine and format-meeting."""

import logging
import tempfile
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from metalscribe.config import DEFAULT_LANGUAGE, DEFAULT_PROMPT_LANGUAGE, get_prompt_language
from metalscribe.core.audio import convert_to_wav_16k
from metalscribe.core.context_validator import validate_context
from metalscribe.core.format_meeting import (
    estimate_tokens,
    format_meeting_file,
    get_language_warning,
    load_format_meeting_prompt,
)
from metalscribe.core.merge import merge_segments
from metalscribe.core.pyannote import run_diarization
from metalscribe.core.refine import get_language_warning as get_refine_language_warning
from metalscribe.core.refine import refine_markdown_file
from metalscribe.core.whisper import run_transcription
from metalscribe.exporters.json_exporter import (
    export_diarize_json,
    export_transcript_json,
)
from metalscribe.exporters.markdown_exporter import export_markdown
from metalscribe.llm import (
    AuthenticationError,
    CLINotInstalledError,
    LLMError,
    SDKNotInstalledError,
)
from metalscribe.utils.audio_info import get_audio_duration
from metalscribe.utils.logging import format_duration, log_timing, setup_logging
from metalscribe.utils.metadata import extract_language_from_metadata

console = Console()
logger = logging.getLogger(__name__)


@click.command("run-meeting")
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True, path_type=Path),
    required=False,
    help="Input audio file",
)
@click.option(
    "--import-transcript",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Import external transcript JSON (skips audio/transcription/diarization)",
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
    "--llm-model",
    type=str,
    default=None,
    help="LLM model for refine and format-meeting (uses Claude Code default if not specified)",
)
@click.option(
    "--context",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Domain context file for improved transcription quality",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip token confirmation prompt for format-meeting",
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
def run_meeting(
    input: Path | None,
    import_transcript: Path | None,
    model: str,
    lang: str,
    speakers: int,
    output: Path,
    llm_model: str,
    context: Path | None,
    yes: bool,
    limit: float,
    verbose: bool,
) -> None:
    """
    Complete pipeline: transcription + diarization + merge + export + refine + format-meeting.

    This command runs the full pipeline including LLM-based refinement and meeting formatting.
    Requires Claude Code authentication (run: claude auth login).

    You can either:
    - Provide --input (audio file) to run full transcription pipeline
    - Provide --import-transcript (JSON) to skip transcription and start from existing transcript
    """
    setup_logging(verbose=verbose)

    import time

    start_time = time.time()

    # Validate input options
    if not input and not import_transcript:
        console.print("[red]Error: Must provide either --input or --import-transcript[/red]")
        raise click.Abort()

    if input and import_transcript:
        console.print(
            "[red]Error: Cannot use both --input and --import-transcript simultaneously[/red]"
        )
        raise click.Abort()

    domain_context = ""
    if context:
        domain_context = context.read_text(encoding="utf-8")
        console.print(
            f"[cyan]Using context file: {context} ({len(domain_context)} chars)[/cyan]"
        )

        # Validate context and show warnings
        validation = validate_context(domain_context)
        for warning in validation.warnings:
            console.print(f"[yellow]Context warning: {warning}[/yellow]")
        if not validation.is_valid:
            for error in validation.errors:
                console.print(f"[red]Context error: {error}[/red]")
            console.print(
                "[red]Context file has validation errors. "
                "Run 'metalscribe context validate' for details.[/red]"
            )
            raise click.Abort()

    # Determine output prefix
    if output is None:
        # Use input stem as base for output files
        if import_transcript:
            output = import_transcript.parent / import_transcript.stem
        else:
            output = input.parent / input.stem
    else:
        output = Path(output)

    # Branch: Import transcript or run full pipeline
    if import_transcript:
        # Import mode: skip Steps 1-4
        console.print(f"[cyan]Importing transcript from: {import_transcript}[/cyan]")
        from metalscribe.adapters import import_transcript as import_transcript_func

        try:
            import_start = time.time()
            merged = import_transcript_func(import_transcript)
            import_time = time.time() - import_start
            log_timing("Import", import_time)
        except ValueError as e:
            console.print(f"[red]Error importing transcript: {e}[/red]")
            raise click.Abort()

        # Export merged markdown
        console.print("[cyan]Exporting imported transcript...[/cyan]")
        export_start = time.time()
        merged_md_path = output.parent / f"{output.stem}_03_merged.md"

        # Resolve prompt language (use CLI arg or default)
        prompt_language = get_prompt_language(lang) if lang else DEFAULT_PROMPT_LANGUAGE

        metadata = {
            "source": "imported",
            "import_file": str(import_transcript),
            "prompt_language": prompt_language,
        }
        if lang:
            metadata["language"] = lang

        export_markdown(merged, merged_md_path, title=output.stem, metadata=metadata)
        export_time = time.time() - export_start
        log_timing("Export", export_time)

        # Set timing variables for later use (not applicable in import mode)
        convert_time = None
        transcribe_time = None
        diarize_time = None
        merge_time = None
        audio_duration = None

    else:
        # Normal mode: run full pipeline
        # Get audio duration to calculate RTF
        # Note: If limited, we should use the limit as duration for RTF calc if it's smaller than actual duration
        actual_duration = get_audio_duration(input)
        audio_duration = actual_duration
        if limit:
            limit_seconds = limit * 60
            if limit_seconds < actual_duration:
                audio_duration = limit_seconds

        # Step 1: Audio conversion
        console.print("[cyan]Step 1: Converting audio...[/cyan]")
        wav_path = Path(tempfile.mktemp(suffix=".wav"))
        convert_start = time.time()
        convert_to_wav_16k(input, wav_path, limit_minutes=limit)
        convert_time = time.time() - convert_start
        convert_rtf = convert_time / audio_duration if audio_duration > 0 else None
        log_timing("Conversion", convert_time, rtf=convert_rtf)

        # Step 2: Transcription
        console.print("[cyan]Step 2: Transcribing...[/cyan]")
        transcript_json = Path(tempfile.mktemp(suffix=".json"))
        transcript_base = transcript_json.parent / transcript_json.stem
        transcribe_start = time.time()
        transcript_segments = run_transcription(
            wav_path,
            model_name=model,
            language=lang,
            output_base=transcript_base,
            verbose=verbose,
        )
        transcribe_time = time.time() - transcribe_start
        transcribe_rtf = transcribe_time / audio_duration if audio_duration > 0 else None
        log_timing("Transcription", transcribe_time, rtf=transcribe_rtf)

        # Step 3: Diarization
        console.print("[cyan]Step 3: Diarizing...[/cyan]")
        diarize_json = Path(tempfile.mktemp(suffix=".json"))
        diarize_start = time.time()
        diarize_segments = run_diarization(
            wav_path, num_speakers=speakers, output_json=diarize_json
        )
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

        # New naming convention:
        # 1. audio_01_transcript.json
        # 2. audio_02_diarize.json
        # 3. audio_03_merged.md
        transcript_json_path = output.parent / f"{output.stem}_01_transcript.json"
        diarize_json_path = output.parent / f"{output.stem}_02_diarize.json"
        merged_md_path = output.parent / f"{output.stem}_03_merged.md"

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
        export_transcript_json(
            transcript_segments, transcript_json_path, metadata=transcript_metadata
        )

        # Export diarization only (speaker info only)
        diarize_metadata = {
            "num_speakers": speakers or "auto",
            "input_file": str(input),
        }
        export_diarize_json(diarize_segments, diarize_json_path, metadata=diarize_metadata)

        # Export merged markdown only (no .json or .srt)
        export_markdown(merged, merged_md_path, title=input.stem, metadata=metadata)

        export_time = time.time() - export_start
        log_timing("Export", export_time)

    # Step 6: Refine
    console.print("\n[cyan]Step 6: Refining transcription...[/cyan]")
    refine_start = time.time()
    refined_md_path = output.parent / f"{output.stem}_04_refined.md"

    try:
        language_used, language_source = refine_markdown_file(
            input_path=merged_md_path,
            output_path=refined_md_path,
            model=llm_model,
            domain_context=domain_context,
        )

        # Show language notice
        warning = get_refine_language_warning(language_used, language_source)
        if warning:
            console.print()
            console.print(
                Panel(
                    f"[yellow]{warning}[/yellow]",
                    title="Language Notice",
                    border_style="yellow",
                )
            )

        refine_time = time.time() - refine_start
        log_timing("Refine", refine_time)
        console.print("[green]✓ Refinement completed[/green]")

    except (AuthenticationError, CLINotInstalledError, SDKNotInstalledError):
        console.print("[red]LLM authentication required. Run: claude auth login[/red]")
        raise click.Abort()
    except LLMError as e:
        console.print(f"[red]LLM error during refinement: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        logger.exception("Error during refinement")
        console.print(f"[red]Error during refinement: {e}[/red]")
        raise click.Abort()

    # Step 7: Format Meeting
    console.print("\n[cyan]Step 7: Formatting meeting...[/cyan]")
    format_start = time.time()
    formatted_md_path = output.parent / f"{output.stem}_05_formatted-meeting.md"

    try:
        # Extract language from refined file metadata
        refined_content = refined_md_path.read_text(encoding="utf-8")
        file_language = extract_language_from_metadata(refined_content)
        language = file_language or prompt_language or DEFAULT_PROMPT_LANGUAGE
        language_source = "file" if file_language else ("cli" if lang else "default")

        # Show language notice
        warning = get_language_warning(language, language_source)
        if warning:
            console.print()
            console.print(
                Panel(
                    f"[yellow]{warning}[/yellow]",
                    title="Language Notice",
                    border_style="yellow",
                )
            )

        # Extract body (skip header)
        lines = refined_content.split("\n")
        body_start_idx = 0
        for i, line in enumerate(lines):
            if line.strip() == "---":
                body_start_idx = i + 1
                break
        body = "\n".join(lines[body_start_idx:]).strip()

        if not body:
            console.print("[red]Error: No content found in refined file.[/red]")
            raise click.Abort()

        # Load prompt for estimation
        prompt = load_format_meeting_prompt(language, domain_context=domain_context)

        # Estimate tokens
        estimates = estimate_tokens(body, prompt)

        # Display token estimate
        console.print()
        table = Table(title="Token Estimate", show_header=True)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right")
        table.add_row("Input tokens", f"~{estimates['input_tokens']:,}")
        table.add_row("Output tokens (est.)", f"~{estimates['output_tokens_estimate']:,}")
        table.add_row("Total tokens (est.)", f"~{estimates['total_tokens_estimate']:,}")
        table.add_row("", "")
        table.add_row("Estimated cost", f"${estimates['total_cost_usd']:.2f} USD")
        console.print(table)

        # Confirmation prompt
        if not yes:
            console.print()
            console.print(
                Panel(
                    "[yellow]This operation may consume significant tokens.[/yellow]\n"
                    "Use --yes flag to skip this confirmation.",
                    title="Warning",
                    border_style="yellow",
                )
            )
            if not click.confirm("Do you want to proceed?", default=False):
                console.print("[dim]Operation cancelled.[/dim]")
                raise click.Abort()

        console.print()
        console.print("[cyan]Processing...[/cyan]")

        format_meeting_file(
            input_path=refined_md_path,
            output_path=formatted_md_path,
            model=llm_model,
            language=language,
            domain_context=domain_context,
        )

        format_time = time.time() - format_start
        log_timing("Format Meeting", format_time)
        console.print("[green]✓ Formatting completed[/green]")

    except (AuthenticationError, CLINotInstalledError, SDKNotInstalledError):
        console.print("[red]LLM authentication required. Run: claude auth login[/red]")
        raise click.Abort()
    except LLMError as e:
        console.print(f"[red]LLM error during formatting: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        logger.exception("Error during formatting")
        console.print(f"[red]Error during formatting: {e}[/red]")
        raise click.Abort()

    # Timings log (06_timings.log)
    timings_log = output.parent / f"{output.stem}_06_timings.log"
    total_time = time.time() - start_time
    total_rtf = total_time / audio_duration if audio_duration and audio_duration > 0 else None
    with open(timings_log, "w") as f:
        if import_transcript:
            # Import mode timings
            f.write("Mode: Import transcript\n")
            f.write(f"Import file: {import_transcript}\n\n")
            f.write(f"Import: {format_duration(import_time)} ({import_time:.2f}s)\n")
        else:
            # Normal mode timings
            f.write(f"Audio duration: {format_duration(audio_duration)} ({audio_duration:.2f}s)\n")
            f.write(f"\nConversion: {format_duration(convert_time)} ({convert_time:.2f}s)")
            if convert_rtf:
                f.write(f" (RTF: {convert_rtf:.3f})")
            f.write(f"\nTranscription: {format_duration(transcribe_time)} ({transcribe_time:.2f}s)")
            if transcribe_rtf:
                f.write(f" (RTF: {transcribe_rtf:.3f})")
            f.write(f"\nDiarization: {format_duration(diarize_time)} ({diarize_time:.2f}s)")
            if diarize_rtf:
                f.write(f" (RTF: {diarize_rtf:.3f})")
            f.write(f"\nMerge: {format_duration(merge_time)} ({merge_time:.2f}s)\n")

        f.write(f"Export: {format_duration(export_time)} ({export_time:.2f}s)\n")
        f.write(f"Refine: {format_duration(refine_time)} ({refine_time:.2f}s)\n")
        f.write(f"Format Meeting: {format_duration(format_time)} ({format_time:.2f}s)\n")
        f.write(f"\nTotal: {format_duration(total_time)} ({total_time:.2f}s)")
        if total_rtf:
            f.write(f" (RTF: {total_rtf:.3f})")
        f.write("\n")

    log_timing("Total", total_time)

    console.print("\n[green]✓ Pipeline complete![/green]")
    console.print("[green]Generated files:[/green]")
    if not import_transcript:
        console.print(f"  - {transcript_json_path}")
        console.print(f"  - {diarize_json_path}")
    console.print(f"  - {merged_md_path}")
    console.print(f"  - {refined_md_path}")
    console.print(f"  - {formatted_md_path}")
    console.print(f"  - {timings_log}")
