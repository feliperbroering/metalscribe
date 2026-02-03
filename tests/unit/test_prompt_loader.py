"""Tests for prompt loader with domain context injection."""

from __future__ import annotations

from metalscribe.core import prompt_loader
from metalscribe.core.prompt_loader import load_prompt


def test_load_prompt_injects_domain_context():
    prompt = load_prompt("format-meeting", language="pt-BR", domain_context="Contexto X")
    assert "Contexto X" in prompt
    assert "{{DOMAIN_CONTEXT}}" not in prompt


def test_load_prompt_removes_domain_context_section_when_empty():
    prompt = load_prompt("format-meeting", language="pt-BR", domain_context="")
    assert "## CONTEXTO DE DOMÍNIO" not in prompt
    assert "## CONTEXTO DA TRANSCRIÇÃO" in prompt
    assert "{{DOMAIN_CONTEXT}}" not in prompt


def test_load_prompt_removes_domain_context_when_last_section(tmp_path, monkeypatch):
    content = (
        "# Title\n\n"
        "## INTRO\n\n"
        "Texto inicial.\n\n"
        "## CONTEXTO DE DOMÍNIO\n\n"
        "{{DOMAIN_CONTEXT}}\n"
    )
    prompt_path = tmp_path / "prompt.md"
    prompt_path.write_text(content, encoding="utf-8")

    monkeypatch.setattr(
        prompt_loader,
        "get_prompt_path",
        lambda *_args, **_kwargs: prompt_path,
    )

    result = load_prompt("ignored", domain_context="")
    assert "CONTEXTO DE DOMÍNIO" not in result
    assert "Texto inicial." in result
