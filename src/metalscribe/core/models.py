"""Modelos de dados para transcrição e diarização."""

from dataclasses import dataclass


@dataclass
class TranscriptSegment:
    """Segmento de transcrição com timestamps."""

    start_ms: int
    end_ms: int
    text: str


@dataclass
class DiarizeSegment:
    """Segmento de diarização com speaker."""

    start_ms: int
    end_ms: int
    speaker: str


@dataclass
class MergedSegment:
    """Segmento combinado com transcrição e speaker."""

    start_ms: int
    end_ms: int
    text: str
    speaker: str
