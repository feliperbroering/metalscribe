"""Context command group - manage domain context files."""

from __future__ import annotations

from importlib import resources
from pathlib import Path

import click
from rich.console import Console

from metalscribe.config import ExitCode
from metalscribe.core.context_validator import validate_context

console = Console()


def _load_template() -> str:
    template_path = resources.files("metalscribe") / "templates" / "context-template.md"
    return template_path.read_text(encoding="utf-8")


@click.group()
def context() -> None:
    """Manage domain context files for better transcription quality."""


@context.command("show")
def show() -> None:
    """Print the context template to stdout."""
    click.echo(_load_template())


@context.command("copy")
@click.argument("output", default="context.md", required=False, type=click.Path(path_type=Path))
@click.option("--force", "-f", is_flag=True)
def copy(output: Path, force: bool) -> None:
    """Copy the context template to a file."""
    if output.exists() and not force:
        console.print(f"[red]Arquivo já existe: {output} (use --force)[/red]")
        raise SystemExit(ExitCode.INVALID_INPUT)

    output.write_text(_load_template(), encoding="utf-8")
    console.print(f"[green]Template salvo em: {output}[/green]")


@context.command("validate")
@click.argument("file", type=click.Path(exists=True, path_type=Path))
def validate(file: Path) -> None:
    """Validate a context file."""
    content = file.read_text(encoding="utf-8")
    result = validate_context(content)

    for warning in result.warnings:
        console.print(f"[yellow]Aviso: {warning}[/yellow]")

    if result.errors:
        for error in result.errors:
            console.print(f"[red]Erro: {error}[/red]")
        raise SystemExit(ExitCode.INVALID_INPUT)

    console.print("[green]Contexto válido.[/green]")
