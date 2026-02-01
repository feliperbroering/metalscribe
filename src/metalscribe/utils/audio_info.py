"""Utilitários para obter informações de áudio."""

import json
import logging
from pathlib import Path

from metalscribe.utils.subprocess import run_command

logger = logging.getLogger(__name__)


def get_audio_duration(audio_path: Path) -> float:
    """
    Obtém duração do áudio em segundos usando ffprobe.

    Args:
        audio_path: Caminho do arquivo de áudio

    Returns:
        Duração em segundos
    """
    try:
        result = run_command(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "json",
                str(audio_path),
            ]
        )

        data = json.loads(result.stdout)
        duration = float(data["format"]["duration"])
        return duration
    except Exception as e:
        logger.warning(f"Não foi possível obter duração do áudio: {e}")
        return 0.0
