"""CLI entry point usando Click."""

import click

from metalscribe import __version__
from metalscribe.commands.combine import combine
from metalscribe.commands.diarize import diarize
from metalscribe.commands.doctor import doctor
from metalscribe.commands.refine import refine
from metalscribe.commands.run import run
from metalscribe.commands.transcribe import transcribe


@click.group()
@click.version_option(version=__version__, prog_name="metalscribe")
def main() -> None:
    """metalscribe - CLI para transcrição e diarização de áudio com GPU."""
    pass


# Registra comandos
main.add_command(doctor)
main.add_command(transcribe)
main.add_command(diarize)
main.add_command(combine)
main.add_command(run)
main.add_command(refine)


@main.command()
def version() -> None:
    """Mostra a versão do metalscribe."""
    click.echo(f"metalscribe {__version__}")


if __name__ == "__main__":
    main()
