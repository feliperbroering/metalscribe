"""Tests for domain context validation."""

from __future__ import annotations

from metalscribe.core.context_validator import validate_context


def _valid_context() -> str:
    return (
        "## Área de Conhecimento\n\n"
        "Domínio: Saúde.\n\n"
        "## Glossário\n\n"
        "| Termo | Significado | Erros ASR comuns |\n"
        "|-------|-------------|------------------|\n"
        "| hipertensão | pressão alta | hiper tensão |\n\n"
        "## Nomes e Entidades\n\n"
        "| Nome/Entidade | Tipo | Erros ASR comuns |\n"
        "|---------------|------|------------------|\n"
        "| Ana Souza | pessoa | Ana Sousa |\n"
    )


def test_validate_context_missing_sections():
    content = "## Área de Conhecimento\n\nDomínio: X"
    result = validate_context(content)
    assert not result.is_valid
    assert any("Glossário" in error for error in result.errors)
    assert any("Nomes e Entidades" in error for error in result.errors)


def test_validate_context_placeholders_warning():
    content = _valid_context() + "\n\n[Ex: exemplo de placeholder]\n"
    result = validate_context(content)
    assert result.is_valid
    assert result.warnings


def test_validate_context_html_comment_warning():
    content = _valid_context() + "\n\n<!-- comentário -->\n"
    result = validate_context(content)
    assert result.is_valid
    assert any("coment" in warning.lower() for warning in result.warnings)


def test_validate_context_empty_glossary_warning():
    content = (
        "## Área de Conhecimento\n\nDomínio: Saúde.\n\n"
        "## Glossário\n\n"
        "| Termo | Significado | Erros ASR comuns |\n"
        "|-------|-------------|------------------|\n\n"
        "## Nomes e Entidades\n\n"
        "| Nome/Entidade | Tipo | Erros ASR comuns |\n"
        "|---------------|------|------------------|\n"
        "| Ana Souza | pessoa | Ana Sousa |\n"
    )
    result = validate_context(content)
    assert result.is_valid
    assert any("glossário" in warning.lower() for warning in result.warnings)
