"""Utilitários para execução de subprocessos."""

import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from metalscribe.config import ExitCode

logger = logging.getLogger(__name__)


def run_command(
    cmd: List[str],
    timeout: Optional[int] = None,
    cwd: Optional[Path] = None,
    env: Optional[dict] = None,
    capture_output: bool = True,
    check: bool = True,
) -> subprocess.CompletedProcess:
    """
    Executa um comando com timeout e logging.

    Args:
        cmd: Lista de argumentos do comando
        timeout: Timeout em segundos
        cwd: Diretório de trabalho
        env: Variáveis de ambiente adicionais
        capture_output: Se True, captura stdout e stderr
        check: Se True, levanta exceção em caso de erro

    Returns:
        CompletedProcess com resultado do comando

    Raises:
        subprocess.TimeoutExpired: Se timeout for excedido
        subprocess.CalledProcessError: Se check=True e comando falhar
    """
    logger.debug(f"Executando: {' '.join(cmd)}")

    full_env = None
    if env:
        full_env = {**os.environ, **env}

    try:
        result = subprocess.run(
            cmd,
            timeout=timeout,
            cwd=str(cwd) if cwd else None,
            env=full_env,
            capture_output=capture_output,
            text=True,
            check=check,
        )
        if result.stdout:
            logger.debug(f"stdout: {result.stdout[:500]}")
        return result
    except subprocess.TimeoutExpired:
        logger.error(f"Comando excedeu timeout de {timeout}s: {' '.join(cmd)}")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Comando falhou com código {e.returncode}: {' '.join(cmd)}")
        if e.stderr:
            logger.error(f"stderr: {e.stderr[:500]}")
        raise
    except FileNotFoundError:
        logger.error(f"Comando não encontrado: {cmd[0]}")
        sys.exit(ExitCode.MISSING_DEPENDENCY)
