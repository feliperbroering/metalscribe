"""Testes de configuração."""

from pathlib import Path

from metalscribe.config import ExitCode, get_brew_prefix, get_cache_dir


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
