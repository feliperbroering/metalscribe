"""Module for refining transcriptions using LLM."""

import logging
from pathlib import Path
from typing import Optional

from metalscribe.config import DEFAULT_PROMPT_LANGUAGE, DEFAULT_REFINE_MODEL
from metalscribe.core.prompt_loader import load_prompt
from metalscribe.llm import LLMProvider
from metalscribe.utils.metadata import extract_language_from_metadata

logger = logging.getLogger(__name__)


def load_refine_prompt(language: Optional[str] = None, domain_context: str = "") -> str:
    """
    Load the refine prompt from the markdown file.

    Extracts prompt content removing only the main title,
    but keeping the markdown structure for better LLM readability.

    Args:
        language: Language code (e.g., "pt-BR"). Uses default if None.
        domain_context: Optional domain context to inject.

    Returns:
        The prompt content as string.
    """
    return load_prompt("refine", language=language, domain_context=domain_context)


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
    domain_context: str = "",
) -> str:
    """
    Refine text using LLM via Claude Code.

    Args:
        text: Text to be refined
        model: Specific model (optional)
        prompt_path: Path to custom prompt (optional)
        language: Language code for prompt (optional)
        domain_context: Optional domain context to inject.

    Returns:
        Refined text
    """
    # Load prompt
    if prompt_path:
        prompt = prompt_path.read_text(encoding="utf-8")
    else:
        prompt = load_refine_prompt(language, domain_context=domain_context)

    # Use Opus 4.6 thinking as default if no model specified
    effective_model = model if model is not None else DEFAULT_REFINE_MODEL
    provider = LLMProvider(model=effective_model, system_prompt=prompt)
    response = provider.query(text=text)
    return response.text


def refine_markdown_file(
    input_path: Path,
    output_path: Path,
    model: Optional[str] = None,
    chunk_size: int = 10000,
    language: Optional[str] = None,
    domain_context: str = "",
) -> tuple[str, str]:
    """
    Refine a markdown transcription file, preserving structure and metadata.

    Args:
        input_path: Input markdown file path
        output_path: Output markdown file path
        model: Specific model
        chunk_size: Maximum chunk size to process (characters, not used yet)
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

    header = "\n".join(header_lines) if header_lines else ""
    body_lines = lines[body_start_idx:] if body_start_idx < len(lines) else lines
    body = "\n".join(body_lines).strip()

    if not body:
        logger.warning("No content found to refine. Copying original file.")
        output_path.write_text(content, encoding="utf-8")
        return language, language_source

    # Process the body
    logger.info(f"Processing {len(body)} characters of content...")
    refined_body = refine_text(
        body,
        model=model,
        language=language,
        domain_context=domain_context,
    )

    # Reconstruct file preserving header
    if header:
        output_content = header + "\n\n" + refined_body
    else:
        output_content = refined_body

    output_path.write_text(output_content, encoding="utf-8")
    logger.info(f"Refined file saved to: {output_path}")

    return language, language_source
