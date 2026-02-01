"""Testes do algoritmo de merge."""

from metalscribe.core.merge import merge_segments
from metalscribe.core.models import DiarizeSegment, TranscriptSegment


def test_merge_basic():
    """Testa merge básico."""
    transcript = [
        TranscriptSegment(start_ms=0, end_ms=2500, text="Olá, bem-vindo"),
        TranscriptSegment(start_ms=2500, end_ms=5800, text="Hoje vamos falar"),
    ]

    diarize = [
        DiarizeSegment(start_ms=0, end_ms=2500, speaker="SPEAKER_00"),
        DiarizeSegment(start_ms=2500, end_ms=5800, speaker="SPEAKER_01"),
    ]

    merged = merge_segments(transcript, diarize)

    assert len(merged) == 2
    assert merged[0].speaker == "SPEAKER_00"
    assert merged[1].speaker == "SPEAKER_01"


def test_merge_no_diarize():
    """Testa merge sem diarização."""
    transcript = [
        TranscriptSegment(start_ms=0, end_ms=2500, text="Olá, bem-vindo"),
    ]

    merged = merge_segments(transcript, [])

    assert len(merged) == 1
    assert merged[0].speaker == "UNKNOWN"


def test_merge_overlap():
    """Testa merge com overlap parcial."""
    transcript = [
        TranscriptSegment(start_ms=0, end_ms=3000, text="Texto longo"),
    ]

    diarize = [
        DiarizeSegment(start_ms=0, end_ms=2000, speaker="SPEAKER_00"),
        DiarizeSegment(start_ms=2000, end_ms=3000, speaker="SPEAKER_01"),
    ]

    merged = merge_segments(transcript, diarize)

    assert len(merged) == 1
    # Deve escolher o speaker com maior overlap
    assert merged[0].speaker in ["SPEAKER_00", "SPEAKER_01"]
