"""Refine command - refine transcriptions using LLM."""

import logging
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from metalscribe.core.refine import get_language_warning, refine_markdown_file
from metalscribe.llm import (
    AuthenticationError,
    CLINotInstalledError,
    LLMError,
    SDKNotInstalledError,
)
from metalscribe.utils.logging import setup_logging

console = Console()
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True, path_type=Path),
    required=False,
    help="Markdown transcription file to refine",
)
@click.option(
    "--import-transcript",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Import external transcript JSON instead of MD file",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output refined markdown file (default: input_04_refined.md)",
)
@click.option(
    "--model",
    "-m",
    type=str,
    default=None,
    help="Specific model (uses Claude Code default if not specified)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose mode",
)
def refine(
    input: Path | None,
    import_transcript: Path | None,
    output: Path,
    model: str,
    verbose: bool,
) -> None:
    """
    Refine a markdown transcription using Claude Code.

    Uses OAuth authentication from Claude Code (no API key needed).
    If not authenticated, run: claude auth login

    The prompt language is automatically detected from the file's
    prompt_language metadata (set during transcription with --lang).
    Falls back to pt-BR if not specified.

    You can either:
    - Provide --input (markdown file) to refine existing markdown
    - Provide --import-transcript (JSON) to convert and refine external transcript

    \b
    Examples:
        metalscribe refine -i transcription.md
        metalscribe refine -i transcription.md -o refined.md
        metalscribe refine --import-transcript transcript.json -o refined.md
    """
    setup_logging(verbose=verbose)

    import tempfile
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

    # Handle import transcript mode
    if import_transcript:
        from metalscribe.adapters import import_transcript as import_transcript_func
        from metalscribe.config import DEFAULT_PROMPT_LANGUAGE, get_prompt_language
        from metalscribe.exporters.markdown_exporter import export_markdown

        console.print(f"[cyan]Importing transcript from: {import_transcript}[/cyan]")

        try:
            # Import segments
            merged = import_transcript_func(import_transcript)

            # Create temporary markdown file
            temp_md = Path(tempfile.mktemp(suffix=".md"))
            prompt_language = DEFAULT_PROMPT_LANGUAGE
            metadata = {
                "source": "imported",
                "import_file": str(import_transcript),
                "prompt_language": prompt_language,
            }
            export_markdown(merged, temp_md, title=import_transcript.stem, metadata=metadata)

            # Use temp markdown as input
            input = temp_md
            console.print(f"[dim]Converted to temporary markdown: {temp_md}[/dim]")

        except ValueError as e:
            console.print(f"[red]Error importing transcript: {e}[/red]")
            raise click.Abort()

    # Determine output file
    if output is None:
        # Extract the base name without the numbered suffix if present
        # e.g., "audio_03_merged.md" -> "audio"
        stem = input.stem
        if "_03_merged" in stem:
            base_name = stem.replace("_03_merged", "")
            output = input.parent / f"{base_name}_04_refined.md"
        else:
            # Fallback for files without the _03_merged pattern
            output = input.with_name(f"{stem}_04_refined.md")

    console.print("[cyan]Refining transcription...[/cyan]")
    console.print(f"[dim]Input: {input}[/dim]")
    console.print(f"[dim]Output: {output}[/dim]")

    try:
        language_used, language_source = refine_markdown_file(
            input_path=input,
            output_path=output,
            model=model,
        )

        # Show language notice after processing
        warning = get_language_warning(language_used, language_source)
        if warning:
            console.print()
            console.print(
                Panel(
                    f"[yellow]{warning}[/yellow]",
                    title="Language Notice",
                    border_style="yellow",
                )
            )

        elapsed = time.time() - start_time
        console.print(f"\n[green]✓ Refinement completed in {elapsed:.2f}s[/green]")
        console.print(f"[green]Output file: {output}[/green]")

    except (AuthenticationError, CLINotInstalledError, SDKNotInstalledError):
        # Setup guide already shown by LLM provider
        raise click.Abort()
    except LLMError as e:
        console.print(f"[red]LLM error: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        logger.exception("Error during refinement")
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()
