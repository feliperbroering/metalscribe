"""Detecção automática de formato de transcrição."""

import logging
from typing import Type

from metalscribe.adapters.base import TranscriptAdapter
from metalscribe.adapters.registry import TranscriptFormat, get_all_adapters

logger = logging.getLogger(__name__)


def detect_format(data: dict) -> TranscriptFormat | None:
    """
    Detecta automaticamente o formato do JSON.

    Itera sobre todos os adaptadores registrados e retorna
    o primeiro que reconhecer o formato.

    Args:
        data: JSON carregado como dict

    Returns:
        TranscriptFormat ou None se não reconhecido
    """
    for format, adapter in get_all_adapters().items():
        if adapter.detect(data):
            logger.debug(f"Formato detectado: {format.value}")
            return format
    return None


def get_adapter_for_data(data: dict) -> Type[TranscriptAdapter] | None:
    """
    Retorna o adaptador apropriado para o JSON.

    Args:
        data: JSON carregado como dict

    Returns:
        Classe do adaptador ou None
    """
    for format, adapter in get_all_adapters().items():
        if adapter.detect(data):
            return adapter
    return None
