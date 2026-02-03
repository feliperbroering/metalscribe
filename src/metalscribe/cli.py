"""CLI entry point using Click."""

import click

from metalscribe import __version__
from metalscribe.commands.combine import combine
from metalscribe.commands.diarize import diarize
from metalscribe.commands.doctor import doctor
from metalscribe.commands.format_meeting import format_meeting
from metalscribe.commands.refine import refine
from metalscribe.commands.run import run
from metalscribe.commands.run_meeting import run_meeting
from metalscribe.commands.transcribe import transcribe


@click.group()
@click.version_option(version=__version__, prog_name="metalscribe")
def main() -> None:
    """metalscribe - CLI for audio transcription and diarization with GPU."""
    pass


# Register commands
main.add_command(doctor)
main.add_command(transcribe)
main.add_command(diarize)
main.add_command(combine)
main.add_command(run)
main.add_command(run_meeting)
main.add_command(refine)
main.add_command(format_meeting)


@main.command()
def version() -> None:
    """Shows metalscribe version."""
    click.echo(f"metalscribe {__version__}")


if __name__ == "__main__":
    main()
