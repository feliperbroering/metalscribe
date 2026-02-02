"""Subprocess execution utilities."""

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
    Runs a command with timeout and logging.

    Args:
        cmd: List of command arguments
        timeout: Timeout in seconds
        cwd: Working directory
        env: Additional environment variables
        capture_output: If True, captures stdout and stderr
        check: If True, raises exception on error

    Returns:
        CompletedProcess with command result

    Raises:
        subprocess.TimeoutExpired: If timeout is exceeded
        subprocess.CalledProcessError: If check=True and command fails
    """
    logger.debug(f"Running: {' '.join(cmd)}")

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
        logger.error(f"Command exceeded {timeout}s timeout: {' '.join(cmd)}")
        raise
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed with code {e.returncode}: {' '.join(cmd)}")
        if e.stderr:
            logger.error(f"stderr: {e.stderr[:500]}")
        raise
    except FileNotFoundError:
        logger.error(f"Command not found: {cmd[0]}")
        sys.exit(ExitCode.MISSING_DEPENDENCY)
