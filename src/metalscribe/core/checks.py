"""Dependency and system checks."""

import logging
import os
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from metalscribe.config import get_brew_prefix, get_pyannote_venv_path
from metalscribe.utils.platform import is_macos
from metalscribe.utils.subprocess import run_command

logger = logging.getLogger(__name__)


@dataclass
class CheckResult:
    """Result of a check."""

    name: str
    status: bool
    message: str
    fix_hint: Optional[str] = None


def check_platform() -> CheckResult:
    """Checks if running on macOS."""
    if is_macos():
        return CheckResult("macOS", True, f"macOS {platform.mac_ver()[0]}")
    return CheckResult(
        "macOS",
        False,
        f"Operating system: {platform.system()}",
        "metalscribe requires macOS for Metal/MPS GPU acceleration",
    )


def check_homebrew() -> CheckResult:
    """Checks if Homebrew is installed."""
    try:
        result = run_command(["brew", "--version"], check=False)
        if result.returncode == 0:
            version = result.stdout.split("\n")[0]
            return CheckResult("Homebrew", True, version)
        return CheckResult(
            "Homebrew",
            False,
            "Homebrew not found",
            'Install via: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        )
    except FileNotFoundError:
        return CheckResult(
            "Homebrew",
            False,
            "Homebrew not found",
            'Install via: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        )


def check_python() -> CheckResult:
    """Checks Python version."""
    version = platform.python_version()
    major, minor = map(int, version.split(".")[:2])
    if major == 3 and minor >= 11:
        return CheckResult("Python", True, f"Python {version}")
    return CheckResult(
        "Python",
        False,
        f"Python {version}",
        "Requires Python 3.11 or higher",
    )


def check_ffmpeg() -> CheckResult:
    """Checks if ffmpeg is installed."""
    try:
        result = run_command(["ffmpeg", "-version"], check=False)
        if result.returncode == 0:
            version_line = result.stdout.split("\n")[0]
            return CheckResult("ffmpeg", True, version_line)
        return CheckResult(
            "ffmpeg", False, "ffmpeg not found", "Install via: brew install ffmpeg"
        )
    except FileNotFoundError:
        return CheckResult(
            "ffmpeg", False, "ffmpeg not found", "Install via: brew install ffmpeg"
        )


def check_whisper_installation() -> CheckResult:
    """Checks if whisper.cpp is installed."""
    from metalscribe.config import get_cache_dir

    brew_prefix = get_brew_prefix()
    cache_dir = get_cache_dir()

    whisper_paths = [
        # Priority 1: locally compiled in cache
        cache_dir / "whisper.cpp" / "build" / "bin" / "whisper-cli",
        # Priority 2: Homebrew
        brew_prefix / "bin" / "whisper",
        brew_prefix / "bin" / "whisper-cli",
        # Priority 3: global paths
        Path("/usr/local/bin/whisper"),
        Path("/usr/local/bin/whisper-cli"),
    ]

    for whisper_path in whisper_paths:
        if whisper_path.exists():
            try:
                result = run_command([str(whisper_path), "--help"], check=False)
                if result.returncode == 0:
                    return CheckResult("whisper.cpp", True, f"Installed at {whisper_path}")
            except Exception:
                pass

    return CheckResult(
        "whisper.cpp",
        False,
        "whisper.cpp not found",
        "Run: metalscribe doctor --setup",
    )


def check_pyannote_installation() -> CheckResult:
    """Checks if pyannote.audio is installed."""
    venv_path = get_pyannote_venv_path()
    if not venv_path.exists():
        return CheckResult(
            "pyannote.audio",
            False,
            "Venv not found",
            "Run: metalscribe doctor --setup",
        )

    python_path = venv_path / "bin" / "python"
    if not python_path.exists():
        return CheckResult(
            "pyannote.audio",
            False,
            "Venv Python not found",
            "Run: metalscribe doctor --setup",
        )

    try:
        result = run_command(
            [str(python_path), "-c", "import pyannote.audio; print(pyannote.audio.__version__)"],
            check=False,
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return CheckResult("pyannote.audio", True, f"Version {version}")
    except Exception as e:
        logger.debug(f"Error checking pyannote: {e}")

    return CheckResult(
        "pyannote.audio",
        False,
        "pyannote.audio is not installed correctly",
        "Run: metalscribe doctor --setup",
    )


def check_metal_available() -> CheckResult:
    """Checks if Metal is available."""
    if not is_macos():
        return CheckResult("Metal GPU", False, "Metal is only available on macOS")

    try:
        # Check if Metal is available via system_profiler
        result = run_command(
            ["system_profiler", "SPDisplaysDataType"],
            check=False,
            capture_output=True,
        )
        if result.returncode == 0 and "Metal" in result.stdout:
            return CheckResult("Metal GPU", True, "Metal available")
    except Exception:
        pass

    # Assume available if on modern macOS
    return CheckResult("Metal GPU", True, "Metal available (assumed)")


def check_mps_available() -> CheckResult:
    """Checks if MPS (Metal Performance Shaders) is available."""
    if not is_macos():
        return CheckResult("MPS GPU", False, "MPS is only available on macOS")

    # Check in pyannote venv (where it will actually be used)
    venv_path = get_pyannote_venv_path()
    python_path = venv_path / "bin" / "python"
    if python_path.exists():
        try:
            result = run_command(
                [
                    str(python_path),
                    "-c",
                    "import torch; print('MPS:', torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False)",
                ],
                check=False,
            )
            if result.returncode == 0 and "True" in result.stdout:
                return CheckResult("MPS GPU", True, "MPS available in pyannote venv")
        except Exception:
            pass

    # If no venv, check if can be installed (modern macOS has MPS)
    # But mark as not verified until setup
    return CheckResult(
        "MPS GPU",
        False,
        "MPS not verified (pyannote venv not configured)",
        "Will be verified during pyannote setup",
    )


def check_hf_token() -> CheckResult:
    """Checks if HuggingFace token is configured."""
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if token:
        return CheckResult("HF Token", True, "Token configured")
    return CheckResult(
        "HF Token",
        False,
        "Token not found in HF_TOKEN or HUGGINGFACE_TOKEN",
        "Configure: export HF_TOKEN=your_token",
    )


def check_claude_code_cli() -> CheckResult:
    """Checks if Claude Code CLI is installed."""
    import shutil

    claude_path = shutil.which("claude")
    if claude_path:
        try:
            result = run_command(["claude", "--version"], check=False)
            if result.returncode == 0:
                version = result.stdout.strip()
                return CheckResult("Claude Code CLI", True, f"Installed ({version})")
        except Exception:
            pass
        return CheckResult("Claude Code CLI", True, f"Installed at {claude_path}")

    return CheckResult(
        "Claude Code CLI",
        False,
        "Claude Code CLI not found",
        "Run: metalscribe doctor --setup (or: npm install -g @anthropic-ai/claude-code)",
    )


def check_claude_code_sdk() -> CheckResult:
    """Checks if Claude Agent SDK is installed."""
    try:
        import claude_agent_sdk  # noqa: F401

        # Try to get version if available
        try:
            version = claude_agent_sdk.__version__
            return CheckResult("Claude Agent SDK", True, f"Version {version}")
        except AttributeError:
            return CheckResult("Claude Agent SDK", True, "Installed")
    except ImportError:
        return CheckResult(
            "Claude Agent SDK",
            False,
            "claude-agent-sdk not found",
            "Run: metalscribe doctor --setup (or: pip install claude-agent-sdk)",
        )


def check_claude_code_auth() -> CheckResult:
    """Checks if authenticated with Claude Code."""
    # First check if CLI is installed
    cli_check = check_claude_code_cli()
    if not cli_check.status:
        return CheckResult(
            "Claude Code Auth",
            False,
            "CLI not installed",
            "Run: metalscribe doctor --setup",
        )

    try:
        result = run_command(["claude", "auth", "status"], check=False)
        if result.returncode == 0:
            return CheckResult("Claude Code Auth", True, "Authenticated")
        return CheckResult(
            "Claude Code Auth",
            False,
            "Not authenticated",
            "Run: claude auth login",
        )
    except Exception:
        return CheckResult(
            "Claude Code Auth",
            False,
            "Could not check authentication",
            "Run: claude auth login",
        )


def validate_hf_token() -> Optional[str]:
    """Validates and returns HuggingFace token."""
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if not token:
        raise ValueError(
            "HuggingFace token not found. Set HF_TOKEN or HUGGINGFACE_TOKEN"
        )
    return token
