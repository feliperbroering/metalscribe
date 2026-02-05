"""Registro de adaptadores de transcrição."""

from enum import Enum
from typing import TYPE_CHECKING, Dict, Type

if TYPE_CHECKING:
    from metalscribe.adapters.base import TranscriptAdapter


class TranscriptFormat(Enum):
    """Formatos de transcrição suportados."""

    VOXTRAL = "voxtral"
    # Futuros: DEEPGRAM, ASSEMBLYAI, WHISPER_EXTERNAL, etc.


# Registro de adaptadores (preenchido em runtime via decorators)
_ADAPTER_REGISTRY: Dict[TranscriptFormat, Type["TranscriptAdapter"]] = {}


def register_adapter(format: TranscriptFormat):
    """Decorator para registrar um adaptador."""

    def decorator(cls):
        _ADAPTER_REGISTRY[format] = cls
        return cls

    return decorator


def get_adapter(format: TranscriptFormat) -> Type["TranscriptAdapter"]:
    """Retorna a classe do adaptador para o formato."""
    return _ADAPTER_REGISTRY[format]


def get_all_adapters() -> Dict[TranscriptFormat, Type["TranscriptAdapter"]]:
    """Retorna todos os adaptadores registrados."""
    return _ADAPTER_REGISTRY.copy()
