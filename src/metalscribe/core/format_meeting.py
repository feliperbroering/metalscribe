"""Module for formatting meeting transcriptions using LLM."""

import logging
import re
from pathlib import Path
from typing import Optional

from metalscribe.config import (
    DEFAULT_PROMPT_LANGUAGE,
    get_prompt_path,
)
from metalscribe.llm import LLMProvider

logger = logging.getLogger(__name__)


def extract_language_from_metadata(content: str) -> Optional[str]:
    """
    Extract the prompt_language from markdown file metadata.

    Args:
        content: The markdown file content.

    Returns:
        The prompt_language value if found, None otherwise.
    """
    # Look for prompt_language in metadata section (before ---)
    lines = content.split("\n")
    for line in lines:
        if line.strip() == "---":
            break
        # Match: - **prompt_language**: pt-BR
        match = re.match(r"[-*\s]*\*?\*?prompt_language\*?\*?:\s*(.+)", line, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

# Defaults for token estimation
DEFAULT_CHARS_PER_TOKEN = 4
DEFAULT_OUTPUT_MULTIPLIER = 1.8

# Pricing per 1K tokens (USD) - for estimation only
PRICING = {
    "default": {"input": 0.015, "output": 0.075},
}


def load_format_meeting_prompt(language: Optional[str] = None) -> str:
    """
    Load the format-meeting prompt from the markdown file.

    Returns the content removing only the main title, keeping the markdown
    structure for better LLM readability.

    Args:
        language: Language code (e.g., "pt-BR"). Uses default if None.

    Returns:
        The prompt content as string.
    """
    prompt_path = get_prompt_path("format-meeting", language)
    content = prompt_path.read_text(encoding="utf-8")

    # Remove only the main title
    # but keep the entire markdown structure
    lines = content.split("\n")
    # Skip the first line if it's a title
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    # Remove initial empty line if present
    if lines and not lines[0].strip():
        lines = lines[1:]

    return "\n".join(lines)


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
) -> str:
    """
    Format a meeting transcription text using LLM.

    Args:
        text: Text to be formatted
        model: Specific model (optional)
        language: Language code for prompt (optional)

    Returns:
        Formatted text
    """
    prompt = load_format_meeting_prompt(language)

    # Build full message with prompt and text
    full_text = f"{prompt}\n\n---\n\nTRANSCRIPTION TO FORMAT:\n\n{text}"

    provider = LLMProvider(model=model)
    response = provider.query(text=full_text)
    return response.text


def format_meeting_file(
    input_path: Path,
    output_path: Path,
    model: Optional[str] = None,
    language: Optional[str] = None,
) -> tuple[str, str]:
    """
    Format a meeting transcription markdown file.

    Args:
        input_path: Input markdown file path
        output_path: Output markdown file path
        model: Specific model
        language: Language code for prompt (overrides file metadata)

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
    formatted_body = format_meeting_text(body, model=model, language=language)

    # The format-meeting prompt produces a complete document, so we use it directly
    output_path.write_text(formatted_body, encoding="utf-8")
    logger.info(f"Formatted file saved to: {output_path}")

    return language, language_source
