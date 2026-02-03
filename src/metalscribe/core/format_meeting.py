"""Module for formatting meeting transcriptions using LLM."""

import logging
from pathlib import Path
from typing import Optional

from metalscribe.config import DEFAULT_PROMPT_LANGUAGE, DEFAULT_FORMAT_MEETING_MODEL
from metalscribe.core.prompt_loader import load_prompt
from metalscribe.llm import LLMProvider
from metalscribe.utils.metadata import extract_language_from_metadata

logger = logging.getLogger(__name__)

# Defaults for token estimation
DEFAULT_CHARS_PER_TOKEN = 4
DEFAULT_OUTPUT_MULTIPLIER = 1.8

# Pricing per 1K tokens (USD) - for estimation only
PRICING = {
    "default": {"input": 0.015, "output": 0.075},
}


def load_format_meeting_prompt(language: Optional[str] = None, domain_context: str = "") -> str:
    """
    Load the format-meeting prompt from the markdown file.

    Returns the content removing only the main title, keeping the markdown
    structure for better LLM readability.

    Args:
        language: Language code (e.g., "pt-BR"). Uses default if None.
        domain_context: Optional domain context to inject.

    Returns:
        The prompt content as string.
    """
    return load_prompt("format-meeting", language=language, domain_context=domain_context)


def get_language_warning(language: str, source: str = "default") -> Optional[str]:
    """
    Get a warning message about the prompt language if applicable.

    Args:
        language: The language being used.
        source: Where the language came from ("default", "file", "cli").

    Returns:
        Warning message or None if no warning needed.
    """
    if language == "pt-BR":
        if source == "file":
            return (
                f"Using prompt language: {language} (from file metadata). "
                "Prompt is optimized for Brazilian Portuguese."
            )
        else:
            return (
                f"Using prompt language: {language}. "
                "Prompt is optimized for Brazilian Portuguese. "
                "Results may vary for content in other languages."
            )
    return None


def estimate_tokens(text: str, prompt: str) -> dict:
    """
    Estimate tokens for the API call.

    Args:
        text: The input text to be processed
        prompt: The system prompt

    Returns:
        Dictionary with token estimates and cost estimation
    """
    input_tokens = (len(text) + len(prompt)) // DEFAULT_CHARS_PER_TOKEN
    output_tokens_estimate = int(input_tokens * DEFAULT_OUTPUT_MULTIPLIER)

    pricing = PRICING["default"]
    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens_estimate / 1000) * pricing["output"]

    return {
        "input_tokens": input_tokens,
        "output_tokens_estimate": output_tokens_estimate,
        "total_tokens_estimate": input_tokens + output_tokens_estimate,
        "input_cost_usd": input_cost,
        "output_cost_usd": output_cost,
        "total_cost_usd": input_cost + output_cost,
    }


def format_meeting_text(
    text: str,
    model: Optional[str] = None,
    language: Optional[str] = None,
    domain_context: str = "",
) -> str:
    """
    Format a meeting transcription text using LLM.

    Args:
        text: Text to be formatted
        model: Specific model (optional)
        language: Language code for prompt (optional)
        domain_context: Optional domain context to inject.

    Returns:
        Formatted text
    """
    prompt = load_format_meeting_prompt(language, domain_context=domain_context)

    # Build full message with prompt and text
    full_text = f"{prompt}\n\n---\n\nTRANSCRIPTION TO FORMAT:\n\n{text}"

    # Use Opus 4.5 with thinking as default if no model specified
    effective_model = model if model is not None else DEFAULT_FORMAT_MEETING_MODEL
    provider = LLMProvider(model=effective_model)
    response = provider.query(text=full_text)
    return response.text


def format_meeting_file(
    input_path: Path,
    output_path: Path,
    model: Optional[str] = None,
    language: Optional[str] = None,
    domain_context: str = "",
) -> tuple[str, str]:
    """
    Format a meeting transcription markdown file.

    Args:
        input_path: Input markdown file path
        output_path: Output markdown file path
        model: Specific model
        language: Language code for prompt (overrides file metadata)
        domain_context: Optional domain context to inject.

    Returns:
        Tuple of (language_used, language_source) where source is "file", "cli", or "default"
    """
    content = input_path.read_text(encoding="utf-8")

    # Extract language from file metadata if not provided
    language_source = "default"
    if language:
        language_source = "cli"
    else:
        file_language = extract_language_from_metadata(content)
        if file_language:
            language = file_language
            language_source = "file"
        else:
            language = DEFAULT_PROMPT_LANGUAGE

    # Separate header/metadata from main content
    # metalscribe format has: title, metadata, "---", then content
    lines = content.split("\n")
    header_lines = []
    body_start_idx = 0

    # Find where header ends (line "---")
    for i, line in enumerate(lines):
        if line.strip() == "---":
            body_start_idx = i + 1
            break
        header_lines.append(line)

    body_lines = lines[body_start_idx:] if body_start_idx < len(lines) else lines
    body = "\n".join(body_lines).strip()

    if not body:
        logger.warning("No content found to format. Copying original file.")
        output_path.write_text(content, encoding="utf-8")
        return language, language_source

    # Process the body
    logger.info(f"Processing {len(body)} characters of content...")
    formatted_body = format_meeting_text(
        body,
        model=model,
        language=language,
        domain_context=domain_context,
    )

    # The format-meeting prompt produces a complete document, so we use it directly
    output_path.write_text(formatted_body, encoding="utf-8")
    logger.info(f"Formatted file saved to: {output_path}")

    return language, language_source
