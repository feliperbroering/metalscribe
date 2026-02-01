"""Testes dos parsers."""

import json
import tempfile
from pathlib import Path

from metalscribe.parsers.diarize_parser import parse_diarize_output
from metalscribe.parsers.whisper_parser import parse_whisper_output


def test_whisper_parser_v1(fixtures_dir: Path):
    """Testa parser do whisper com formato v1."""
    json_path = fixtures_dir / "whisper_output_v1.json"
    segments = parse_whisper_output(json_path)

    assert len(segments) == 4
    assert segments[0].start_ms == 0
    assert segments[0].end_ms == 2500
    assert "Olá" in segments[0].text


def test_whisper_parser_list_format():
    """Testa parser do whisper com formato de lista."""
    data = [
        {"start": 0.0, "end": 1.5, "text": "Hello"},
        {"start": 1.5, "end": 3.0, "text": "World"},
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(data, f)
        json_path = Path(f.name)

    try:
        segments = parse_whisper_output(json_path)
        assert len(segments) == 2
        assert segments[0].text == "Hello"
        assert segments[1].text == "World"
    finally:
        json_path.unlink()


def test_diarize_parser_v1(fixtures_dir: Path):
    """Testa parser do pyannote com formato v1."""
    json_path = fixtures_dir / "diarize_output_v1.json"
    segments = parse_diarize_output(json_path)

    assert len(segments) == 4
    # Verifica que segmentos estão ordenados por tempo
    for i in range(len(segments) - 1):
        assert segments[i].start_ms <= segments[i + 1].start_ms

    # Verifica speakers
    speakers = set(seg.speaker for seg in segments)
    assert "SPEAKER_00" in speakers
    assert "SPEAKER_01" in speakers
