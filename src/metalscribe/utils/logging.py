"""Logging utilities."""

import logging
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

console = Console()


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to HH:MM:SS format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string in HH:MM:SS format
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


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
