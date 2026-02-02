"""Logging utilities."""

import logging
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

console = Console()


def setup_logging(verbose: bool = False, log_file: Optional[Path] = None) -> None:
    """Configures logging with Rich."""
    level = logging.DEBUG if verbose else logging.INFO

    handlers = [RichHandler(console=console, rich_tracebacks=True)]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=handlers,
    )


def log_timing(stage: str, duration: float, rtf: Optional[float] = None) -> None:
    """Logs timing for a step."""
    msg = f"[green]✓[/green] {stage}: {duration:.2f}s"
    if rtf is not None:
        msg += f" (RTF: {rtf:.3f})"
    console.print(msg)
