"""Utilities for extracting metadata from markdown files."""

from __future__ import annotations

import re


def extract_language_from_metadata(content: str) -> str | None:
    """
    Extract the prompt_language from markdown file metadata.

    Looks for a line matching "prompt_language: <value>" in the metadata
    section (before the first "---" separator).

    Args:
        content: The markdown file content.

    Returns:
        The prompt_language value if found, None otherwise.
    """
    lines = content.split("\n")
    for line in lines:
        if line.strip() == "---":
            break
        # Match: - **prompt_language**: pt-BR
        match = re.match(r"[-*\s]*\*?\*?prompt_language\*?\*?:\s*(.+)", line, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None
