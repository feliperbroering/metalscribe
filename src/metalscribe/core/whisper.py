"""Wrapper para whisper.cpp."""

import logging
import tempfile
from pathlib import Path
from typing import List, Optional

from metalscribe.config import ExitCode, get_brew_prefix
from metalscribe.core.models import TranscriptSegment
from metalscribe.core.setup import download_whisper_model
from metalscribe.parsers.whisper_parser import parse_whisper_output
from metalscribe.utils.subprocess import run_command

logger = logging.getLogger(__name__)


def run_transcription(
    audio_path: Path,
    model_name: str = "medium",
    language: Optional[str] = None,
    output_json: Optional[Path] = None,
) -> List[TranscriptSegment]:
    """
    Executa transcrição usando whisper.cpp com Metal GPU.

    Args:
        audio_path: Caminho do arquivo WAV 16kHz
        model_name: Nome do modelo (tiny, base, small, medium, large-v3)
        language: Código de idioma (opcional, ex: 'pt')
        output_json: Caminho para salvar JSON (opcional)

    Returns:
        Lista de TranscriptSegment

    Raises:
        SystemExit: Se transcrição falhar
    """
    # Encontra binário do whisper
    from metalscribe.config import get_cache_dir

    brew_prefix = get_brew_prefix()
    cache_dir = get_cache_dir()

    whisper_paths = [
        # Prioridade 1: compilado localmente no cache
        cache_dir / "whisper.cpp" / "build" / "bin" / "whisper-cli",
        # Prioridade 2: Homebrew
        brew_prefix / "bin" / "whisper",
        brew_prefix / "bin" / "whisper-cli",
        # Prioridade 3: paths globais
        Path("/usr/local/bin/whisper"),
        Path("/usr/local/bin/whisper-cli"),
    ]

    whisper_bin = None
    for path in whisper_paths:
        if path.exists():
            whisper_bin = path
            break

    if not whisper_bin:
        logger.error("whisper.cpp não encontrado. Execute: metalscribe doctor --setup")
        exit(ExitCode.MISSING_DEPENDENCY)

    # Baixa modelo se necessário
    model_path = download_whisper_model(model_name)

    # Prepara output JSON
    if output_json is None:
        output_json = Path(tempfile.mktemp(suffix=".json"))

    # Remove extensão .json para -of (whisper adiciona automaticamente)
    output_base = str(output_json).rsplit(".json", 1)[0]

    logger.info(f"Transcrevendo com modelo {model_name}...")

    # Comando whisper: whisper -m model.ggml -f audio.wav -oj -of output_base
    cmd = [
        str(whisper_bin),
        "-m",
        str(model_path),
        "-f",
        str(audio_path),
        "-oj",  # Output JSON
        "-of",  # Output file path (without extension)
        output_base,
    ]

    if language:
        cmd.extend(["-l", language])

    # Executa transcrição
    try:
        run_command(cmd, timeout=3600)  # 1 hora timeout

        if not output_json.exists():
            logger.error(f"JSON de output não encontrado: {output_json}")
            exit(ExitCode.TRANSCRIPTION_FAILED)

        # Parseia resultado
        segments = parse_whisper_output(output_json)

        logger.info(f"Transcrição concluída: {len(segments)} segmentos")
        return segments

    except Exception as e:
        logger.error(f"Erro na transcrição: {e}")
        exit(ExitCode.TRANSCRIPTION_FAILED)
