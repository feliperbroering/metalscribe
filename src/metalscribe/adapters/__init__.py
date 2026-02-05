"""Adaptadores para importação de transcrições externas."""

from metalscribe.adapters.base import TranscriptAdapter
from metalscribe.adapters.detector import detect_format
from metalscribe.adapters.importer import import_transcript
from metalscribe.adapters.registry import TranscriptFormat, register_adapter

# Importa adaptadores para registrá-los
from metalscribe.adapters.formats import voxtral  # noqa: F401

__all__ = [
    "TranscriptFormat",
    "TranscriptAdapter",
    "register_adapter",
    "import_transcript",
    "detect_format",
]
