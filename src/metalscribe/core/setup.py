"""Dependency setup functions."""

import logging
import sys
import urllib.request
from pathlib import Path

from metalscribe.config import (
    WHISPER_MODELS,
    get_brew_prefix,
    get_cache_dir,
    get_pyannote_venv_path,
)
from metalscribe.core.checks import validate_hf_token
from metalscribe.utils.subprocess import run_command

logger = logging.getLogger(__name__)


def setup_whisper() -> None:
    """Configures whisper.cpp by compiling with Metal support."""
    brew_prefix = get_brew_prefix()
    whisper_path = brew_prefix / "bin" / "whisper"

    if whisper_path.exists():
        logger.info("whisper.cpp is already installed via Homebrew")
        return

    # Try to install via Homebrew first
    try:
        logger.info("Attempting to install whisper.cpp via Homebrew...")
        run_command(["brew", "install", "whisper.cpp"], check=False)
        if whisper_path.exists():
            logger.info("whisper.cpp installed via Homebrew")
            return
    except Exception as e:
        logger.debug(f"Homebrew install failed: {e}")

    # If not working, compile from source
    logger.info("Compiling whisper.cpp from source...")
    cache_dir = get_cache_dir()
    whisper_dir = cache_dir / "whisper.cpp"

    if not whisper_dir.exists():
        logger.info("Cloning whisper.cpp repository...")
        run_command(
            ["git", "clone", "https://github.com/ggerganov/whisper.cpp.git", str(whisper_dir)],
            cwd=cache_dir,
        )

    logger.info("Compiling with Metal support...")
    run_command(
        ["make", "clean"],
        cwd=whisper_dir,
        check=False,
    )
    run_command(
        ["make", "WHISPER_METAL=1"],
        cwd=whisper_dir,
    )

    # Create symlink or copy to a location in PATH
    whisper_bin = whisper_dir / "whisper"
    if whisper_bin.exists():
        # Try to create symlink in /usr/local/bin (may require sudo)
        local_bin = Path("/usr/local/bin")
        local_bin.mkdir(parents=True, exist_ok=True)
        try:
            if (local_bin / "whisper").exists():
                (local_bin / "whisper").unlink()
            (local_bin / "whisper").symlink_to(whisper_bin)
            logger.info(f"whisper.cpp installed at {local_bin / 'whisper'}")
        except PermissionError:
            logger.warning(
                f"Could not create symlink. Use: sudo ln -s {whisper_bin} /usr/local/bin/whisper"
            )


def download_whisper_model(model_name: str) -> Path:
    """Downloads Whisper model from HuggingFace."""
    if model_name not in WHISPER_MODELS:
        raise ValueError(f"Invalid model: {model_name}")

    model_info = WHISPER_MODELS[model_name]
    cache_dir = get_cache_dir()
    models_dir = cache_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    model_path = models_dir / model_info["filename"]

    if model_path.exists():
        logger.info(f"Model {model_name} already exists at {model_path}")
        return model_path

    logger.info(f"Downloading model {model_name}...")
    url = model_info["url"]

    def show_progress(block_num: int, block_size: int, total_size: int) -> None:
        downloaded = block_num * block_size
        percent = min(100, (downloaded * 100) // total_size) if total_size > 0 else 0
        print(f"\rProgress: {percent}%", end="", flush=True)

    urllib.request.urlretrieve(url, model_path, show_progress)
    print()  # New line after progress

    logger.info(f"Model downloaded: {model_path}")
    return model_path


def setup_pyannote() -> None:
    """Configures pyannote.audio in an isolated venv."""
    venv_path = get_pyannote_venv_path()

    if venv_path.exists():
        python_path = venv_path / "bin" / "python"
        if python_path.exists():
            # Check if already installed
            try:
                result = run_command(
                    [str(python_path), "-c", "import pyannote.audio"],
                    check=False,
                )
                if result.returncode == 0:
                    logger.info("pyannote.audio is already installed")
                    return
            except Exception:
                pass

    logger.info("Creating venv for pyannote.audio...")
    run_command([sys.executable, "-m", "venv", str(venv_path)])

    python_path = venv_path / "bin" / "python"

    logger.info("Updating pip...")
    run_command([str(python_path), "-m", "pip", "install", "--upgrade", "pip"])

    logger.info("Installing PyTorch with MPS support...")
    run_command(
        [
            str(python_path),
            "-m",
            "pip",
            "install",
            "torch",
            "torchaudio",
        ]
    )

    logger.info("Installing pyannote.audio...")
    # Validate token before installing
    validate_hf_token()

    run_command(
        [
            str(python_path),
            "-m",
            "pip",
            "install",
            "pyannote.audio==3.4.0",
        ]
    )

    # Check if MPS is available
    logger.info("Checking MPS support...")
    result = run_command(
        [
            str(python_path),
            "-c",
            "import torch; print('MPS available:', torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False)",
        ]
    )
    logger.info(f"MPS status: {result.stdout.strip()}")


def setup_claude_code_cli() -> None:
    """Installs Claude Code CLI via npm."""
    import shutil

    # Check if already installed
    if shutil.which("claude"):
        logger.info("Claude Code CLI is already installed")
        return

    # Check if npm is available
    npm_path = shutil.which("npm")
    if not npm_path:
        raise RuntimeError(
            "npm not found. Install Node.js first: brew install node"
        )

    logger.info("Installing Claude Code CLI via npm...")
    run_command([npm_path, "install", "-g", "@anthropic-ai/claude-code"])

    # Check installation
    if not shutil.which("claude"):
        raise RuntimeError("Failed to install Claude Code CLI")


def setup_claude_code_sdk() -> None:
    """Installs Claude Agent SDK via pip."""
    import sys

    try:
        import claude_agent_sdk  # noqa: F401

        logger.info("Claude Agent SDK is already installed")
        return
    except ImportError:
        pass

    logger.info("Installing Claude Agent SDK via pip...")
    run_command([sys.executable, "-m", "pip", "install", "claude-agent-sdk"])

    # Check installation
    try:
        import claude_agent_sdk  # noqa: F401

        logger.info("Claude Agent SDK installed successfully")
    except ImportError:
        raise RuntimeError("Failed to install Claude Agent SDK")
