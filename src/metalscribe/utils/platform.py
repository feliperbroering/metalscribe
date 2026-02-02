"""Platform utilities."""

import platform
import sys


def is_macos() -> bool:
    """Checks if running on macOS."""
    return sys.platform == "darwin"


def is_arm64() -> bool:
    """Checks if running on ARM64 architecture."""
    return platform.machine() == "arm64"
