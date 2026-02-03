"""Module for refining transcriptions using LLM."""

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


def load_refine_prompt(language: Optional[str] = None) -> str:
    """
    Load the refine prompt from the markdown file.

    Extracts prompt content removing only the main title,
    but keeping the markdown structure for better LLM readability.

    Args:
        language: Language code (e.g., "pt-BR"). Uses default if None.

    Returns:
        The prompt content as string.
    """
    prompt_path = get_prompt_path("refine", language)
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


def refine_text(
    text: str,
    model: Optional[str] = None,
    prompt_path: Optional[Path] = None,
    language: Optional[str] = None,
) -> str:
    """
    Refine text using LLM via Claude Code.

    Args:
        text: Text to be refined
        model: Specific model (optional)
        prompt_path: Path to custom prompt (optional)
        language: Language code for prompt (optional)

    Returns:
        Refined text
    """
    # Load prompt
    if prompt_path:
        prompt = prompt_path.read_text(encoding="utf-8")
    else:
        prompt = load_refine_prompt(language)

    provider = LLMProvider(model=model, system_prompt=prompt)
    response = provider.query(text=text)
    return response.text


def refine_markdown_file(
    input_path: Path,
    output_path: Path,
    model: Optional[str] = None,
    chunk_size: int = 10000,
    language: Optional[str] = None,
) -> tuple[str, str]:
    """
    Refine a markdown transcription file, preserving structure and metadata.

    Args:
        input_path: Input markdown file path
        output_path: Output markdown file path
        model: Specific model
        chunk_size: Maximum chunk size to process (characters, not used yet)
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

    header = "\n".join(header_lines) if header_lines else ""
    body_lines = lines[body_start_idx:] if body_start_idx < len(lines) else lines
    body = "\n".join(body_lines).strip()

    if not body:
        logger.warning("No content found to refine. Copying original file.")
        output_path.write_text(content, encoding="utf-8")
        return language, language_source

    # Process the body
    logger.info(f"Processing {len(body)} characters of content...")
    refined_body = refine_text(body, model=model, language=language)

    # Reconstruct file preserving header
    if header:
        output_content = header + "\n\n" + refined_body
    else:
        output_content = refined_body

    output_path.write_text(output_content, encoding="utf-8")
    logger.info(f"Refined file saved to: {output_path}")

    return language, language_source
