"""Testes de configuração."""

from pathlib import Path

import pytest

from metalscribe.config import (
    DEFAULT_PROMPT_LANGUAGE,
    SUPPORTED_PROMPT_LANGUAGES,
    ExitCode,
    get_brew_prefix,
    get_cache_dir,
    get_prompt_path,
    get_prompts_dir,
)


def test_exit_codes():
    """Testa valores dos exit codes."""
    assert ExitCode.SUCCESS == 0
    assert ExitCode.GENERAL_ERROR == 1
    assert ExitCode.MISSING_DEPENDENCY == 2
    assert ExitCode.AUDIO_CONVERSION_FAILED == 10
    assert ExitCode.TRANSCRIPTION_FAILED == 20
    assert ExitCode.DIARIZATION_FAILED == 30
    assert ExitCode.MERGE_FAILED == 40
    assert ExitCode.EXPORT_FAILED == 50
    assert ExitCode.INVALID_INPUT == 60
    assert ExitCode.TIMEOUT == 61


def test_get_cache_dir():
    """Testa que get_cache_dir retorna um Path válido."""
    cache_dir = get_cache_dir()
    assert isinstance(cache_dir, Path)
    assert "metalscribe" in str(cache_dir)


def test_get_brew_prefix():
    """Testa que get_brew_prefix retorna um Path válido."""
    brew_prefix = get_brew_prefix()
    assert isinstance(brew_prefix, Path)
    # Deve ser /opt/homebrew (arm64) ou /usr/local (intel)
    assert str(brew_prefix) in ["/opt/homebrew", "/usr/local"]


def test_default_prompt_language():
    """Testa que o idioma padrão está configurado."""
    assert DEFAULT_PROMPT_LANGUAGE == "pt-BR"


def test_supported_prompt_languages():
    """Testa que a lista de idiomas suportados inclui pt-BR."""
    assert "pt-BR" in SUPPORTED_PROMPT_LANGUAGES
    assert len(SUPPORTED_PROMPT_LANGUAGES) >= 1


def test_get_prompts_dir():
    """Testa que get_prompts_dir retorna um Path válido."""
    prompts_dir = get_prompts_dir()
    assert isinstance(prompts_dir, Path)
    assert prompts_dir.exists()
    assert "prompts" in str(prompts_dir)


def test_get_prompt_path_default_language():
    """Testa que get_prompt_path retorna o caminho correto para o idioma padrão."""
    path = get_prompt_path("refine")
    assert isinstance(path, Path)
    assert path.exists()
    assert "pt-BR" in str(path)
    assert path.name == "refine.md"


def test_get_prompt_path_explicit_language():
    """Testa que get_prompt_path aceita idioma explícito."""
    path = get_prompt_path("format-meeting", language="pt-BR")
    assert isinstance(path, Path)
    assert path.exists()
    assert "pt-BR" in str(path)
    assert path.name == "format-meeting.md"


def test_get_prompt_path_unsupported_language():
    """Testa que get_prompt_path levanta erro para idioma não suportado."""
    with pytest.raises(ValueError) as exc_info:
        get_prompt_path("refine", language="en-US")
    assert "not supported" in str(exc_info.value)
    assert "en-US" in str(exc_info.value)
