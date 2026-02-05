"""Entry point para importação de transcrições externas."""

import json
import logging
from pathlib import Path
from typing import List

from metalscribe.adapters.detector import detect_format, get_adapter_for_data
from metalscribe.adapters.registry import TranscriptFormat
from metalscribe.core.models import MergedSegment

logger = logging.getLogger(__name__)


def import_transcript(json_path: Path) -> List[MergedSegment]:
    """
    Importa transcrição de arquivo JSON externo.

    Detecta automaticamente o formato e converte para MergedSegment.

    Args:
        json_path: Caminho para o arquivo JSON

    Returns:
        Lista de MergedSegment

    Raises:
        ValueError: Se formato não for reconhecido
    """
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    format = detect_format(data)
    if not format:
        supported = [f.value for f in TranscriptFormat]
        raise ValueError(
            f"Formato de transcrição não reconhecido: {json_path}\n"
            f"Formatos suportados: {supported}"
        )

    logger.info(f"Formato detectado: {format.value}")

    adapter = get_adapter_for_data(data)
    segments = adapter.parse(data)

    logger.info(f"Importados {len(segments)} segmentos de {json_path.name}")
    return segments
