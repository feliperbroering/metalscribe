"""Configuração de fixtures pytest."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def fixtures_dir() -> Path:
    """Retorna o diretório de fixtures."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def whisper_output_v1(fixtures_dir: Path) -> dict:
    """Fixture com output do whisper em formato v1."""
    with open(fixtures_dir / "whisper_output_v1.json") as f:
        return json.load(f)


@pytest.fixture
def diarize_output_v1(fixtures_dir: Path) -> dict:
    """Fixture com output do pyannote em formato v1."""
    with open(fixtures_dir / "diarize_output_v1.json") as f:
        return json.load(f)
