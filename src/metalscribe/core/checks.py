"""Checks de dependências e sistema."""

import logging
import os
import platform
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from metalscribe.config import get_brew_prefix
from metalscribe.utils.platform import is_macos
from metalscribe.utils.subprocess import run_command

logger = logging.getLogger(__name__)


@dataclass
class CheckResult:
    """Resultado de um check."""

    name: str
    status: bool
    message: str
    fix_hint: Optional[str] = None


def check_platform() -> CheckResult:
    """Verifica se está rodando no macOS."""
    if is_macos():
        return CheckResult("macOS", True, f"macOS {platform.mac_ver()[0]}")
    return CheckResult(
        "macOS",
        False,
        f"Sistema operacional: {platform.system()}",
        "metalscribe requer macOS para aceleração GPU Metal/MPS",
    )


def check_homebrew() -> CheckResult:
    """Verifica se Homebrew está instalado."""
    try:
        result = run_command(["brew", "--version"], check=False)
        if result.returncode == 0:
            version = result.stdout.split("\n")[0]
            return CheckResult("Homebrew", True, version)
        return CheckResult(
            "Homebrew",
            False,
            "Homebrew não encontrado",
            'Instale via: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        )
    except FileNotFoundError:
        return CheckResult(
            "Homebrew",
            False,
            "Homebrew não encontrado",
            'Instale via: /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
        )


def check_python() -> CheckResult:
    """Verifica versão do Python."""
    version = platform.python_version()
    major, minor = map(int, version.split(".")[:2])
    if major == 3 and minor >= 11:
        return CheckResult("Python", True, f"Python {version}")
    return CheckResult(
        "Python",
        False,
        f"Python {version}",
        "Requer Python 3.11 ou superior",
    )


def check_ffmpeg() -> CheckResult:
    """Verifica se ffmpeg está instalado."""
    try:
        result = run_command(["ffmpeg", "-version"], check=False)
        if result.returncode == 0:
            version_line = result.stdout.split("\n")[0]
            return CheckResult("ffmpeg", True, version_line)
        return CheckResult(
            "ffmpeg", False, "ffmpeg não encontrado", "Instale via: brew install ffmpeg"
        )
    except FileNotFoundError:
        return CheckResult(
            "ffmpeg", False, "ffmpeg não encontrado", "Instale via: brew install ffmpeg"
        )


def check_whisper_installation() -> CheckResult:
    """Verifica se whisper.cpp está instalado."""
    from metalscribe.config import get_cache_dir

    brew_prefix = get_brew_prefix()
    cache_dir = get_cache_dir()

    whisper_paths = [
        # Prioridade 1: compilado localmente no cache
        cache_dir / "whisper.cpp" / "build" / "bin" / "whisper-cli",
        # Prioridade 2: Homebrew
        brew_prefix / "bin" / "whisper",
        brew_prefix / "bin" / "whisper-cli",
        # Prioridade 3: paths globais
        Path("/usr/local/bin/whisper"),
        Path("/usr/local/bin/whisper-cli"),
    ]

    for whisper_path in whisper_paths:
        if whisper_path.exists():
            try:
                result = run_command([str(whisper_path), "--help"], check=False)
                if result.returncode == 0:
                    return CheckResult("whisper.cpp", True, f"Instalado em {whisper_path}")
            except Exception:
                pass

    return CheckResult(
        "whisper.cpp",
        False,
        "whisper.cpp não encontrado",
        "Execute: metalscribe doctor --setup",
    )


def check_pyannote_installation() -> CheckResult:
    """Verifica se pyannote.audio está instalado."""
    venv_path = Path("pyannote_venv")
    if not venv_path.exists():
        return CheckResult(
            "pyannote.audio",
            False,
            "Venv não encontrado",
            "Execute: metalscribe doctor --setup",
        )

    python_path = venv_path / "bin" / "python"
    if not python_path.exists():
        return CheckResult(
            "pyannote.audio",
            False,
            "Python do venv não encontrado",
            "Execute: metalscribe doctor --setup",
        )

    try:
        result = run_command(
            [str(python_path), "-c", "import pyannote.audio; print(pyannote.audio.__version__)"],
            check=False,
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            return CheckResult("pyannote.audio", True, f"Versão {version}")
    except Exception as e:
        logger.debug(f"Erro ao verificar pyannote: {e}")

    return CheckResult(
        "pyannote.audio",
        False,
        "pyannote.audio não está instalado corretamente",
        "Execute: metalscribe doctor --setup",
    )


def check_metal_available() -> CheckResult:
    """Verifica se Metal está disponível."""
    if not is_macos():
        return CheckResult("Metal GPU", False, "Metal só está disponível no macOS")

    try:
        # Verifica se Metal está disponível via system_profiler
        result = run_command(
            ["system_profiler", "SPDisplaysDataType"],
            check=False,
            capture_output=True,
        )
        if result.returncode == 0 and "Metal" in result.stdout:
            return CheckResult("Metal GPU", True, "Metal disponível")
    except Exception:
        pass

    # Assume disponível se estiver no macOS moderno
    return CheckResult("Metal GPU", True, "Metal disponível (assumido)")


def check_mps_available() -> CheckResult:
    """Verifica se MPS (Metal Performance Shaders) está disponível."""
    if not is_macos():
        return CheckResult("MPS GPU", False, "MPS só está disponível no macOS")

    # Verifica no venv do pyannote (onde realmente será usado)
    venv_path = Path("pyannote_venv")
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
                return CheckResult("MPS GPU", True, "MPS disponível no venv pyannote")
        except Exception:
            pass

    # Se não há venv, verifica se pode ser instalado (macOS moderno tem MPS)
    # Mas marca como não verificado até o setup
    return CheckResult(
        "MPS GPU",
        False,
        "MPS não verificado (venv pyannote não configurado)",
        "Será verificado durante setup do pyannote",
    )


def check_hf_token() -> CheckResult:
    """Verifica se token do HuggingFace está configurado."""
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if token:
        return CheckResult("HF Token", True, "Token configurado")
    return CheckResult(
        "HF Token",
        False,
        "Token não encontrado em HF_TOKEN ou HUGGINGFACE_TOKEN",
        "Configure: export HF_TOKEN=seu_token",
    )


def validate_hf_token() -> Optional[str]:
    """Valida e retorna token do HuggingFace."""
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    if not token:
        raise ValueError(
            "Token do HuggingFace não encontrado. Configure HF_TOKEN ou HUGGINGFACE_TOKEN"
        )
    return token
