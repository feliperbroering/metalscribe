"""Prompt loader with optional domain context injection."""

from __future__ import annotations

import re

from metalscribe.config import get_prompt_path

DOMAIN_CONTEXT_PATTERN = re.compile(
    r"## (?:DOMAIN CONTEXT|CONTEXTO DE DOMÍNIO)\s*\n+\{\{DOMAIN_CONTEXT\}\}.*?(?=\n## |\Z)",
    re.IGNORECASE | re.DOTALL,
)


def _strip_main_title(content: str) -> str:
    lines = content.split("\n")
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    if lines and not lines[0].strip():
        lines = lines[1:]
    return "\n".join(lines)


def _remove_domain_context_section(content: str) -> str:
    cleaned = DOMAIN_CONTEXT_PATTERN.sub("", content)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def load_prompt(
    prompt_name: str,
    language: str | None = None,
    domain_context: str = "",
) -> str:
    """
    Load prompt with optional domain context injection.

    If domain_context is non-empty: replaces {{DOMAIN_CONTEXT}} placeholder.
    If domain_context is empty: removes the entire DOMAIN CONTEXT section.
    """
    prompt_path = get_prompt_path(prompt_name, language)
    content = prompt_path.read_text(encoding="utf-8")
    content = _strip_main_title(content)

    cleaned_context = domain_context.strip()
    if cleaned_context:
        return content.replace("{{DOMAIN_CONTEXT}}", cleaned_context)

    cleaned = _remove_domain_context_section(content)
    return cleaned.replace("{{DOMAIN_CONTEXT}}", "")
