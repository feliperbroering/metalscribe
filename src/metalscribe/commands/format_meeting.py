"""format-meeting command - Format meeting transcriptions into professional documents."""

import logging
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from metalscribe.config import DEFAULT_PROMPT_LANGUAGE
from metalscribe.core.format_meeting import (
    estimate_tokens,
    extract_language_from_metadata,
    format_meeting_file,
    get_language_warning,
    load_format_meeting_prompt,
)
from metalscribe.llm import (
    AuthenticationError,
    CLINotInstalledError,
    LLMError,
    SDKNotInstalledError,
)
from metalscribe.utils.logging import setup_logging

console = Console()
logger = logging.getLogger(__name__)


@click.command("format-meeting")
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Input markdown transcription file",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Output formatted markdown file (default: input_formatted-meeting.md)",
)
@click.option(
    "--model",
    "-m",
    type=str,
    default=None,
    help="Specific model (uses Claude Code default if not specified)",
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Skip token confirmation prompt",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose mode",
)
def format_meeting(
    input: Path,
    output: Path,
    model: str,
    yes: bool,
    verbose: bool,
) -> None:
    """
    Format a meeting transcription into a professional structured document.

    Uses OAuth authentication from Claude Code (no API key needed).
    If not authenticated, run: claude auth login

    The prompt language is automatically detected from the file's
    prompt_language metadata (set during transcription with --lang).
    Falls back to pt-BR if not specified.

    The generated document includes:

    \b
    - Executive summary
    - Participant identification
    - Topic breakdown with timestamps
    - Action items extraction
    - Full structured transcription

    WARNING: This command can consume significant tokens. Token estimates
    are displayed before processing, and confirmation is required unless
    --yes flag is used.

    \b
    Examples:
        metalscribe format-meeting -i meeting.md
        metalscribe format-meeting -i meeting.md -o formatted.md
        metalscribe format-meeting -i meeting.md --yes
    """
    setup_logging(verbose=verbose)

    import time

    start_time = time.time()

    # Determine output file
    if output is None:
        output = input.with_name(f"{input.stem}_formatted-meeting.md")

    console.print("\n[cyan bold]Format Meeting[/cyan bold] - Claude Code")
    console.print(f"[dim]Input: {input}[/dim]")
    console.print(f"[dim]Output: {output}[/dim]")

    try:
        content = input.read_text(encoding="utf-8")

        # Extract language from file metadata
        file_language = extract_language_from_metadata(content)
        language = file_language or DEFAULT_PROMPT_LANGUAGE
        language_source = "file" if file_language else "default"

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
        lines = content.split("\n")
        body_start_idx = 0
        for i, line in enumerate(lines):
            if line.strip() == "---":
                body_start_idx = i + 1
                break
        body = "\n".join(lines[body_start_idx:]).strip()

        if not body:
            console.print("[red]Error: No content found in input file.[/red]")
            raise click.Abort()

        # Load prompt for estimation
        prompt = load_format_meeting_prompt(language)

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
            input_path=input,
            output_path=output,
            model=model,
            language=language,
        )

        elapsed = time.time() - start_time
        console.print(f"\n[green]✓ Formatting completed in {elapsed:.2f}s[/green]")
        console.print(f"[green]Output file: {output}[/green]")

    except (AuthenticationError, CLINotInstalledError, SDKNotInstalledError):
        # Setup guide already shown by LLM provider
        raise click.Abort()
    except LLMError as e:
        console.print(f"[red]LLM error: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        logger.exception("Error during formatting")
        console.print(f"[red]Error: {e}[/red]")
        raise click.Abort()
