"""Configurações, constantes e utilitários de sistema."""

import os
import platform
from enum import IntEnum
from pathlib import Path


class ExitCode(IntEnum):
    """Exit codes conforme spec seção 5.2."""

    SUCCESS = 0
    GENERAL_ERROR = 1
    MISSING_DEPENDENCY = 2
    AUDIO_CONVERSION_FAILED = 10
    TRANSCRIPTION_FAILED = 20
    DIARIZATION_FAILED = 30
    MERGE_FAILED = 40
    EXPORT_FAILED = 50
    INVALID_INPUT = 60
    TIMEOUT = 61


def get_cache_dir() -> Path:
    """Retorna o diretório de cache do usuário."""
    cache_home = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    cache_dir = Path(cache_home) / "metalscribe"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_brew_prefix() -> Path:
    """Retorna o prefix do Homebrew."""
    if platform.machine() == "arm64":
        return Path("/opt/homebrew")
    return Path("/usr/local")


# Modelos Whisper disponíveis
WHISPER_MODELS = {
    "tiny": {
        "filename": "ggml-tiny.bin",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin",
    },
    "base": {
        "filename": "ggml-base.bin",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
    },
    "small": {
        "filename": "ggml-small.bin",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
    },
    "medium": {
        "filename": "ggml-medium.bin",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin",
    },
    "large-v3": {
        "filename": "ggml-large-v3.bin",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin",
    },
}
