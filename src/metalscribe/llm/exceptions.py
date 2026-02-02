"""LLM module exceptions."""


class LLMError(Exception):
    """Base error for LLM module."""

    pass


class AuthenticationError(LLMError):
    """Authentication error with Claude Code."""

    pass


class SDKNotInstalledError(LLMError):
    """Claude Agent SDK not installed."""

    pass


class CLINotInstalledError(LLMError):
    """Claude Code CLI not installed."""

    pass
