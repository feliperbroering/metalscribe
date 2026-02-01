"""Utilitários de plataforma."""

import platform
import sys


def is_macos() -> bool:
    """Verifica se está rodando no macOS."""
    return sys.platform == "darwin"


def is_arm64() -> bool:
    """Verifica se está em arquitetura ARM64."""
    return platform.machine() == "arm64"
