"""Testes dos exporters."""

import json
import tempfile
from pathlib import Path

from metalscribe.core.models import MergedSegment
from metalscribe.exporters.json_exporter import export_json
from metalscribe.exporters.markdown_exporter import export_markdown
from metalscribe.exporters.srt_exporter import export_srt, format_timestamp


def test_format_timestamp():
    """Testa formatação de timestamp para SRT."""
    assert format_timestamp(0) == "00:00:00,000"
    assert format_timestamp(1500) == "00:00:01,500"
    assert format_timestamp(62500) == "00:01:02,500"
    assert format_timestamp(3661500) == "01:01:01,500"


def test_export_json():
    """Testa exportação JSON."""
    segments = [
        MergedSegment(start_ms=0, end_ms=2500, text="Olá", speaker="SPEAKER_00"),
        MergedSegment(start_ms=2500, end_ms=5000, text="Mundo", speaker="SPEAKER_01"),
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        output_path = Path(f.name)

    try:
        export_json(segments, output_path, metadata={"model": "medium"})

        with open(output_path) as f:
            data = json.load(f)

        assert "metadata" in data
        assert data["metadata"]["model"] == "medium"
        assert "segments" in data
        assert len(data["segments"]) == 2
        assert data["segments"][0]["speaker"] == "SPEAKER_00"
    finally:
        output_path.unlink()


def test_export_srt():
    """Testa exportação SRT."""
    segments = [
        MergedSegment(start_ms=0, end_ms=2500, text="Olá", speaker="SPEAKER_00"),
        MergedSegment(start_ms=2500, end_ms=5000, text="Mundo", speaker="SPEAKER_01"),
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".srt", delete=False) as f:
        output_path = Path(f.name)

    try:
        export_srt(segments, output_path)

        with open(output_path) as f:
            content = f.read()

        assert "1\n" in content
        assert "00:00:00,000 --> 00:00:02,500" in content
        assert "[SPEAKER_00] Olá" in content
        assert "[SPEAKER_01] Mundo" in content
    finally:
        output_path.unlink()


def test_export_markdown():
    """Testa exportação Markdown."""
    segments = [
        MergedSegment(start_ms=0, end_ms=2500, text="Olá", speaker="SPEAKER_00"),
        MergedSegment(start_ms=2500, end_ms=5000, text="Mundo", speaker="SPEAKER_01"),
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        output_path = Path(f.name)

    try:
        export_markdown(segments, output_path, title="Teste")

        with open(output_path) as f:
            content = f.read()

        assert "# Teste" in content
        assert "SPEAKER_00" in content
        assert "SPEAKER_01" in content
        assert "[00:00]" in content
    finally:
        output_path.unlink()
