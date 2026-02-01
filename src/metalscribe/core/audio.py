"""Conversão de áudio."""

import logging
from pathlib import Path

from metalscribe.config import ExitCode
from metalscribe.utils.subprocess import run_command

logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = {
    ".m4a",
    ".mp3",
    ".mp4",
    ".flac",
    ".ogg",
    ".webm",
    ".aac",
    ".wma",
    ".aiff",
    ".wav",
}


def convert_to_wav_16k(input_path: Path, output_path: Path) -> None:
    """
    Converte áudio para WAV 16kHz mono usando ffmpeg.

    Args:
        input_path: Caminho do arquivo de entrada
        output_path: Caminho do arquivo WAV de saída

    Raises:
        SystemExit: Se conversão falhar
    """
    if not input_path.exists():
        logger.error(f"Arquivo não encontrado: {input_path}")
        exit(ExitCode.INVALID_INPUT)

    suffix = input_path.suffix.lower()
    if suffix not in SUPPORTED_FORMATS:
        logger.warning(f"Formato {suffix} pode não ser suportado")

    logger.info(f"Convertendo {input_path} para WAV 16kHz mono...")

    # ffmpeg -i input -ar 16000 -ac 1 output.wav
    run_command(
        [
            "ffmpeg",
            "-i",
            str(input_path),
            "-ar",
            "16000",  # Sample rate 16kHz
            "-ac",
            "1",  # Mono
            "-y",  # Sobrescrever se existir
            str(output_path),
        ]
    )

    if not output_path.exists():
        logger.error(f"Falha ao converter áudio: {output_path}")
        exit(ExitCode.AUDIO_CONVERSION_FAILED)

    logger.info(f"Áudio convertido: {output_path}")
