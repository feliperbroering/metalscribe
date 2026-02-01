"""Comando doctor para verificação e setup."""

import logging

import click
from rich.console import Console
from rich.table import Table

from metalscribe.core.checks import (
    check_ffmpeg,
    check_hf_token,
    check_homebrew,
    check_metal_available,
    check_mps_available,
    check_platform,
    check_pyannote_installation,
    check_python,
    check_whisper_installation,
)
from metalscribe.core.setup import setup_pyannote, setup_whisper

console = Console()
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--check-only",
    is_flag=True,
    help="Apenas verifica dependências, não faz setup",
)
@click.option(
    "--setup",
    is_flag=True,
    help="Configura dependências faltantes",
)
def doctor(check_only: bool, setup: bool) -> None:
    """Verifica e configura dependências do metalscribe."""
    checks = [
        check_platform(),
        check_homebrew(),
        check_python(),
        check_ffmpeg(),
        check_whisper_installation(),
        check_pyannote_installation(),
        check_metal_available(),
        check_mps_available(),
        check_hf_token(),
    ]

    table = Table(title="Status das Dependências")
    table.add_column("Componente", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Mensagem", style="white")

    all_ok = True
    for check in checks:
        status = "✓" if check.status else "✗"
        status_style = "green" if check.status else "red"
        table.add_row(
            check.name,
            f"[{status_style}]{status}[/{status_style}]",
            check.message,
        )
        if not check.status:
            all_ok = False
            if check.fix_hint:
                table.add_row("", "", f"[dim]{check.fix_hint}[/dim]")

    console.print(table)

    if all_ok:
        console.print("[green]✓ Todas as dependências estão instaladas![/green]")
        return

    if check_only:
        console.print(
            "[yellow]Algumas dependências estão faltando. Execute 'metalscribe doctor --setup' para configurar.[/yellow]"
        )
        return

    if setup:
        console.print("[cyan]Iniciando setup...[/cyan]")

        # Setup whisper
        whisper_check = check_whisper_installation()
        if not whisper_check.status:
            console.print("[cyan]Configurando whisper.cpp...[/cyan]")
            try:
                setup_whisper()
                console.print("[green]✓ whisper.cpp configurado[/green]")
            except Exception as e:
                console.print(f"[red]✗ Erro ao configurar whisper.cpp: {e}[/red]")
                raise click.Abort()

        # Setup pyannote
        pyannote_check = check_pyannote_installation()
        if not pyannote_check.status:
            console.print("[cyan]Configurando pyannote.audio...[/cyan]")
            try:
                setup_pyannote()
                console.print("[green]✓ pyannote.audio configurado[/green]")
            except Exception as e:
                console.print(f"[red]✗ Erro ao configurar pyannote.audio: {e}[/red]")
                raise click.Abort()

        console.print("[green]✓ Setup concluído![/green]")
    else:
        console.print(
            "[yellow]Execute 'metalscribe doctor --setup' para configurar dependências faltantes.[/yellow]"
        )
