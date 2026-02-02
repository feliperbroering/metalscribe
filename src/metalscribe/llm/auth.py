"""Claude Code authentication verification and setup guide."""

import shutil
import subprocess
from typing import Tuple

from rich.console import Console
from rich.panel import Panel

from .exceptions import AuthenticationError, CLINotInstalledError, SDKNotInstalledError

console = Console()


def check_sdk_installed() -> bool:
    """Check if claude-agent-sdk is installed."""
    try:
        import claude_agent_sdk  # noqa: F401

        return True
    except ImportError:
        return False


def check_cli_installed() -> bool:
    """Check if Claude Code CLI is installed."""
    return shutil.which("claude") is not None


def check_authenticated() -> bool:
    """Check if user is authenticated with Claude Code."""
    try:
        result = subprocess.run(
            ["claude", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def verify_setup() -> Tuple[bool, str]:
    """
    Verify complete Claude Code setup.

    Returns:
        Tuple of (success, error_type if any)
    """
    if not check_cli_installed():
        return False, "cli_not_installed"
    if not check_sdk_installed():
        return False, "sdk_not_installed"
    if not check_authenticated():
        return False, "not_authenticated"
    return True, ""


def show_setup_guide(error_type: str) -> None:
    """Show setup guide based on error type."""

    if error_type == "cli_not_installed":
        console.print(
            Panel(
                "[bold red]Claude Code CLI not installed[/bold red]\n\n"
                "To install, run:\n\n"
                "[cyan]npm install -g @anthropic-ai/claude-code[/cyan]\n\n"
                "After installing, authenticate with:\n\n"
                "[cyan]claude auth login[/cyan]",
                title="Setup Required",
                border_style="yellow",
            )
        )

    elif error_type == "sdk_not_installed":
        console.print(
            Panel(
                "[bold red]Claude Agent SDK not installed[/bold red]\n\n"
                "To install, run:\n\n"
                "[cyan]pip install claude-agent-sdk[/cyan]\n\n"
                "Or, if using metalscribe via pip:\n\n"
                "[cyan]pip install metalscribe[llm][/cyan]",
                title="Setup Required",
                border_style="yellow",
            )
        )

    elif error_type == "not_authenticated":
        console.print(
            Panel(
                "[bold yellow]Authentication required[/bold yellow]\n\n"
                "To authenticate with Claude Code, run:\n\n"
                "[cyan]claude auth login[/cyan]\n\n"
                "This will open your browser for OAuth authentication.\n"
                "No API key needed!",
                title="Authentication",
                border_style="yellow",
            )
        )


def ensure_authenticated(auto_guide: bool = True) -> None:
    """
    Ensure user is authenticated with Claude Code.

    Args:
        auto_guide: If True, automatically show setup guide

    Raises:
        CLINotInstalledError: If CLI is not installed
        SDKNotInstalledError: If SDK is not installed
        AuthenticationError: If not authenticated
    """
    success, error_type = verify_setup()

    if success:
        return

    if auto_guide:
        show_setup_guide(error_type)

    if error_type == "cli_not_installed":
        raise CLINotInstalledError(
            "Claude Code CLI not installed. "
            "Install with: npm install -g @anthropic-ai/claude-code"
        )
    elif error_type == "sdk_not_installed":
        raise SDKNotInstalledError(
            "Claude Agent SDK not installed. "
            "Install with: pip install claude-agent-sdk"
        )
    elif error_type == "not_authenticated":
        raise AuthenticationError(
            "Not authenticated with Claude Code. " "Run: claude auth login"
        )
