"""Funções de setup de dependências."""

import logging
import sys
import urllib.request
from pathlib import Path

from metalscribe.config import WHISPER_MODELS, get_brew_prefix, get_cache_dir
from metalscribe.core.checks import validate_hf_token
from metalscribe.utils.subprocess import run_command

logger = logging.getLogger(__name__)


def setup_whisper() -> None:
    """Configura whisper.cpp compilando com suporte Metal."""
    brew_prefix = get_brew_prefix()
    whisper_path = brew_prefix / "bin" / "whisper"

    if whisper_path.exists():
        logger.info("whisper.cpp já está instalado via Homebrew")
        return

    # Tenta instalar via Homebrew primeiro
    try:
        logger.info("Tentando instalar whisper.cpp via Homebrew...")
        run_command(["brew", "install", "whisper.cpp"], check=False)
        if whisper_path.exists():
            logger.info("whisper.cpp instalado via Homebrew")
            return
    except Exception as e:
        logger.debug(f"Homebrew install falhou: {e}")

    # Se não funcionar, compila do source
    logger.info("Compilando whisper.cpp do source...")
    cache_dir = get_cache_dir()
    whisper_dir = cache_dir / "whisper.cpp"

    if not whisper_dir.exists():
        logger.info("Clonando repositório whisper.cpp...")
        run_command(
            ["git", "clone", "https://github.com/ggerganov/whisper.cpp.git", str(whisper_dir)],
            cwd=cache_dir,
        )

    logger.info("Compilando com suporte Metal...")
    run_command(
        ["make", "clean"],
        cwd=whisper_dir,
        check=False,
    )
    run_command(
        ["make", "WHISPER_METAL=1"],
        cwd=whisper_dir,
    )

    # Cria symlink ou copia para um local no PATH
    whisper_bin = whisper_dir / "whisper"
    if whisper_bin.exists():
        # Tenta criar symlink em /usr/local/bin (pode precisar sudo)
        local_bin = Path("/usr/local/bin")
        local_bin.mkdir(parents=True, exist_ok=True)
        try:
            if (local_bin / "whisper").exists():
                (local_bin / "whisper").unlink()
            (local_bin / "whisper").symlink_to(whisper_bin)
            logger.info(f"whisper.cpp instalado em {local_bin / 'whisper'}")
        except PermissionError:
            logger.warning(
                "Não foi possível criar symlink. Use: sudo ln -s {whisper_bin} /usr/local/bin/whisper"
            )


def download_whisper_model(model_name: str) -> Path:
    """Baixa modelo do Whisper do HuggingFace."""
    if model_name not in WHISPER_MODELS:
        raise ValueError(f"Modelo inválido: {model_name}")

    model_info = WHISPER_MODELS[model_name]
    cache_dir = get_cache_dir()
    models_dir = cache_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    model_path = models_dir / model_info["filename"]

    if model_path.exists():
        logger.info(f"Modelo {model_name} já existe em {model_path}")
        return model_path

    logger.info(f"Baixando modelo {model_name}...")
    url = model_info["url"]

    def show_progress(block_num: int, block_size: int, total_size: int) -> None:
        downloaded = block_num * block_size
        percent = min(100, (downloaded * 100) // total_size) if total_size > 0 else 0
        print(f"\rProgresso: {percent}%", end="", flush=True)

    urllib.request.urlretrieve(url, model_path, show_progress)
    print()  # Nova linha após progresso

    logger.info(f"Modelo baixado: {model_path}")
    return model_path


def setup_pyannote() -> None:
    """Configura pyannote.audio em venv isolado."""
    venv_path = Path("pyannote_venv")

    if venv_path.exists():
        python_path = venv_path / "bin" / "python"
        if python_path.exists():
            # Verifica se já está instalado
            try:
                result = run_command(
                    [str(python_path), "-c", "import pyannote.audio"],
                    check=False,
                )
                if result.returncode == 0:
                    logger.info("pyannote.audio já está instalado")
                    return
            except Exception:
                pass

    logger.info("Criando venv para pyannote.audio...")
    run_command([sys.executable, "-m", "venv", str(venv_path)])

    python_path = venv_path / "bin" / "python"

    logger.info("Atualizando pip...")
    run_command([str(python_path), "-m", "pip", "install", "--upgrade", "pip"])

    logger.info("Instalando PyTorch com suporte MPS...")
    run_command(
        [
            str(python_path),
            "-m",
            "pip",
            "install",
            "torch",
            "torchaudio",
        ]
    )

    logger.info("Instalando pyannote.audio...")
    # Valida token antes de instalar
    validate_hf_token()

    run_command(
        [
            str(python_path),
            "-m",
            "pip",
            "install",
            "pyannote.audio==3.4.0",
        ]
    )

    # Verifica se MPS está disponível
    logger.info("Verificando suporte MPS...")
    result = run_command(
        [
            str(python_path),
            "-c",
            "import torch; print('MPS available:', torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False)",
        ]
    )
    logger.info(f"MPS status: {result.stdout.strip()}")
