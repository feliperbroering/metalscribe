"""LLM Provider using Claude Code SDK."""

import asyncio
import logging
from dataclasses import dataclass
from typing import AsyncIterator, Optional

from metalscribe.config import DEFAULT_LLM_MODEL

from .auth import ensure_authenticated
from .exceptions import LLMError

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """LLM response."""

    text: str
    duration_ms: Optional[int] = None
    model: Optional[str] = None


class LLMProvider:
    """
    LLM Provider using Claude Code SDK.

    Uses OAuth authentication via `claude auth login` - no API keys needed.

    Example:
        provider = LLMProvider()
        response = provider.query(
            prompt="Translate to Portuguese:",
            text="Hello, world!",
        )
        print(response.text)
    """

    def __init__(
        self,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        """
        Initialize the provider.

        Args:
            model: Model to use (optional, uses DEFAULT_LLM_MODEL from config or Claude Code default)
            system_prompt: Default system prompt (can be overridden in query)
        """
        # Use provided model, or fall back to config default, or None (Claude Code SDK default)
        self.model = model or DEFAULT_LLM_MODEL
        self.system_prompt = system_prompt
        self._verified = False

    def _ensure_setup(self) -> None:
        """Ensure setup is complete (lazy verification)."""
        if not self._verified:
            ensure_authenticated(auto_guide=True)
            self._verified = True

    async def _async_query(
        self,
        text: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> LLMResponse:
        """Execute async query."""
        from claude_agent_sdk import ClaudeAgentOptions, query
        from claude_agent_sdk.types import AssistantMessage, ResultMessage, TextBlock

        effective_system = system_prompt or self.system_prompt or ""
        effective_model = model or self.model

        # Enable thinking mode for Opus 4.5 (supports extended thinking)
        # Default thinking budget: 10000 tokens for deep reasoning
        max_thinking_tokens = 10000 if (effective_model and "opus-4-5" in effective_model.lower()) else None
        
        options = ClaudeAgentOptions(
            system_prompt=effective_system,
            model=effective_model,
            allowed_tools=[],  # No tools needed for text processing
            max_thinking_tokens=max_thinking_tokens,  # Enable thinking mode for Opus 4.5
        )

        full_text = ""
        duration_ms = None

        model_info = f" with model {effective_model}" if effective_model else " (using Claude Code default)"
        logger.info(f"Querying Claude Code{model_info}...")

        async for message in query(prompt=text, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        full_text += block.text
            elif isinstance(message, ResultMessage):
                if message.is_error:
                    raise LLMError(f"Claude Code error: {message.result}")
                duration_ms = message.duration_ms
                logger.info(f"Claude Code completed in {duration_ms}ms")

        return LLMResponse(
            text=full_text,
            duration_ms=duration_ms,
            model=effective_model,
        )

    def query(
        self,
        text: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> LLMResponse:
        """
        Execute a query to the LLM.

        Args:
            text: Text to be processed (user message)
            system_prompt: System prompt (overrides default)
            model: Model (overrides default)

        Returns:
            LLMResponse with generated text
        """
        self._ensure_setup()

        return asyncio.run(
            self._async_query(
                text=text,
                system_prompt=system_prompt,
                model=model,
            )
        )

    async def stream(
        self,
        text: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """
        Stream response from LLM.

        Yields:
            Text chunks as they are generated
        """
        self._ensure_setup()

        from claude_agent_sdk import ClaudeAgentOptions, query
        from claude_agent_sdk.types import AssistantMessage, TextBlock

        effective_system = system_prompt or self.system_prompt or ""
        effective_model = model or self.model

        # Enable thinking mode for Opus 4.5 (supports extended thinking)
        # Default thinking budget: 10000 tokens for deep reasoning
        max_thinking_tokens = 10000 if (effective_model and "opus-4-5" in effective_model.lower()) else None
        
        options = ClaudeAgentOptions(
            system_prompt=effective_system,
            model=effective_model,
            allowed_tools=[],
            max_thinking_tokens=max_thinking_tokens,  # Enable thinking mode for Opus 4.5
        )

        async for message in query(prompt=text, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        yield block.text


# Singleton for convenient use
_default_provider: Optional[LLMProvider] = None


def get_provider(
    model: Optional[str] = None,
    system_prompt: Optional[str] = None,
) -> LLMProvider:
    """
    Get LLM Provider instance.

    For simple use, can reuse singleton instance.
    For specific configurations, creates new instance.
    """
    global _default_provider

    if model is None and system_prompt is None:
        if _default_provider is None:
            _default_provider = LLMProvider()
        return _default_provider

    return LLMProvider(model=model, system_prompt=system_prompt)
