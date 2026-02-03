"""Validation helpers for domain context files.

This module provides validation for domain context files used to improve
transcription quality. It checks for required sections and common issues.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Final

__all__ = ["ValidationResult", "validate_context"]

# Required sections with their Portuguese and English heading patterns
REQUIRED_SECTIONS: Final[dict[str, list[str]]] = {
    "Área de Conhecimento": [r"^##\s+Área de Conhecimento\b", r"^##\s+Knowledge Area\b"],
    "Glossário": [r"^##\s+Glossário\b", r"^##\s+Glossary\b"],
    "Nomes e Entidades": [r"^##\s+Nomes e Entidades\b", r"^##\s+Proper Nouns\b"],
}

# Pattern to detect unfilled placeholders in the template
PLACEHOLDER_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\[(ex|example):|\[(term|acronym)\]", re.IGNORECASE
)

# Pattern to detect HTML comments
HTML_COMMENT_PATTERN: Final[re.Pattern[str]] = re.compile(r"<!--.*?-->", re.DOTALL)


@dataclass(slots=True)
class ValidationResult:
    """Result of validating a domain context file.

    Attributes:
        errors: List of validation errors (missing required sections).
        warnings: List of warnings (placeholders, empty tables, HTML comments).
        is_valid: True if there are no errors (warnings don't affect validity).
    """

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    is_valid: bool = True


def _has_heading(content: str, patterns: list[str]) -> bool:
    """Check if content contains any of the heading patterns."""
    return any(
        re.search(pattern, content, flags=re.IGNORECASE | re.MULTILINE)
        for pattern in patterns
    )


def _extract_section(content: str, heading_pattern: str) -> str | None:
    """Extract the content of a section by its heading pattern."""
    match = re.search(heading_pattern, content, flags=re.IGNORECASE | re.MULTILINE)
    if not match:
        return None
    section_start = match.end()
    next_heading = re.search(r"^##\s+", content[section_start:], flags=re.MULTILINE)
    section_end = section_start + next_heading.start() if next_heading else len(content)
    return content[section_start:section_end]


def _glossary_has_empty_table(content: str) -> bool:
    """Check if the glossary section has a table with no data rows."""
    section = _extract_section(content, r"^##\s+Glossário\b|^##\s+Glossary\b")
    if not section:
        return False

    table_lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if len(table_lines) < 2:
        return False

    # Check if second line is separator (|---|---|)
    if not re.match(r"^\|\s*-", table_lines[1]):
        return False

    # Count data lines (excluding header and separator)
    data_lines = [
        line
        for index, line in enumerate(table_lines)
        if index not in (0, 1) and line.strip("| ").strip()
    ]
    return len(data_lines) == 0


def validate_context(content: str) -> ValidationResult:
    """Validate a domain context file.

    Checks for:
    - Required sections: Área de Conhecimento, Glossário, Nomes e Entidades
    - Unfilled placeholders from template (warnings)
    - HTML comments that should be removed (warnings)
    - Empty glossary tables (warnings)

    Args:
        content: The full text content of the context file.

    Returns:
        ValidationResult with errors, warnings, and validity status.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # Check required sections
    for label, patterns in REQUIRED_SECTIONS.items():
        if not _has_heading(content, patterns):
            errors.append(f"Seção obrigatória ausente: {label}")

    # Check for unfilled placeholders
    if PLACEHOLDER_PATTERN.search(content):
        warnings.append("Há placeholders de exemplo no arquivo.")

    # Check for HTML comments
    if HTML_COMMENT_PATTERN.search(content):
        warnings.append("Há comentários HTML no arquivo.")

    # Check for empty glossary table
    if _glossary_has_empty_table(content):
        warnings.append("Tabela de glossário sem linhas de dados.")

    return ValidationResult(errors=errors, warnings=warnings, is_valid=not errors)
