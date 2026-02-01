"""Wrapper para pyannote.audio."""

import logging
import tempfile
from pathlib import Path
from typing import List, Optional

from metalscribe.config import ExitCode
from metalscribe.core.checks import validate_hf_token
from metalscribe.core.models import DiarizeSegment
from metalscribe.parsers.diarize_parser import parse_diarize_output
from metalscribe.utils.subprocess import run_command

logger = logging.getLogger(__name__)


def run_diarization(
    audio_path: Path,
    num_speakers: Optional[int] = None,
    output_json: Optional[Path] = None,
) -> List[DiarizeSegment]:
    """
    Executa diarização usando pyannote.audio com MPS GPU.

    Args:
        audio_path: Caminho do arquivo WAV 16kHz
        num_speakers: Número de speakers (opcional, auto-detecta se None)
        output_json: Caminho para salvar JSON (opcional)

    Returns:
        Lista de DiarizeSegment

    Raises:
        SystemExit: Se diarização falhar
    """
    venv_path = Path("pyannote_venv")
    python_path = venv_path / "bin" / "python"

    if not python_path.exists():
        logger.error("pyannote.audio não está configurado. Execute: metalscribe doctor --setup")
        exit(ExitCode.MISSING_DEPENDENCY)

    # Valida token
    token = validate_hf_token()

    # Prepara output JSON temporário se não fornecido
    if output_json is None:
        output_json = Path(tempfile.mktemp(suffix=".json"))

    logger.info("Executando diarização...")

    # Script Python inline para executar diarização
    script = f"""
import os
os.environ['HF_TOKEN'] = '{token}'

from pyannote.audio import Pipeline
import torch
import json

# Usa MPS se disponível
device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
print(f"Usando device: {{device}}")

# Carrega pipeline
pipeline = Pipeline.from_pretrained(
    "pyannote/speaker-diarization-3.1",
    use_auth_token=os.environ.get('HF_TOKEN')
)
pipeline.to(device)

# Executa diarização
audio_file = "{audio_path}"
diarization = pipeline(audio_file, num_speakers={num_speakers if num_speakers else "None"})

# Converte para formato JSON
output = {{
    "uri": audio_file,
    "annotation": {{
        "uri": audio_file,
        "timeline": [],
        "tracks": {{}}
    }}
}}

for turn, _, speaker in diarization.itertracks(yield_label=True):
    speaker_key = str(speaker)
    if speaker_key not in output["annotation"]["tracks"]:
        output["annotation"]["tracks"][speaker_key] = []

    output["annotation"]["tracks"][speaker_key].append({{
        "segment": {{
            "start": turn.start,
            "end": turn.end
        }}
    }})

# Salva JSON
with open("{output_json}", "w") as f:
    json.dump(output, f, indent=2)

print(f"Diarização concluída: {{len(output['annotation']['tracks'])}} speakers")
"""

    try:
        run_command(
            [str(python_path), "-c", script],
            timeout=3600,  # 1 hora timeout
        )

        if not output_json.exists():
            logger.error(f"JSON de output não encontrado: {output_json}")
            exit(ExitCode.DIARIZATION_FAILED)

        # Parseia resultado
        segments = parse_diarize_output(output_json)

        logger.info(f"Diarização concluída: {len(segments)} segmentos")
        return segments

    except Exception as e:
        logger.error(f"Erro na diarização: {e}")
        if hasattr(e, "stderr") and e.stderr:
            logger.error(f"stderr: {e.stderr}")
        exit(ExitCode.DIARIZATION_FAILED)
