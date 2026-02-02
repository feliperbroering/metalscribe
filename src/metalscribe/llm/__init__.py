"""LLM Provider module - Claude Code SDK."""

from .auth import (
    check_authenticated,
    check_cli_installed,
    check_sdk_installed,
    ensure_authenticated,
    verify_setup,
)
from .exceptions import (
    AuthenticationError,
    CLINotInstalledError,
    LLMError,
    SDKNotInstalledError,
)
from .provider import LLMProvider, LLMResponse, get_provider

__all__ = [
    # Provider
    "LLMProvider",
    "LLMResponse",
    "get_provider",
    # Auth
    "check_authenticated",
    "check_cli_installed",
    "check_sdk_installed",
    "ensure_authenticated",
    "verify_setup",
    # Exceptions
    "LLMError",
    "AuthenticationError",
    "CLINotInstalledError",
    "SDKNotInstalledError",
]
