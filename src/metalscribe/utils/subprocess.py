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
    stream_output: bool = False,
) -> subprocess.CompletedProcess:
    """
    Runs a command with timeout and logging.

    Args:
        cmd: List of command arguments
        timeout: Timeout in seconds
        cwd: Working directory
        env: Additional environment variables
        capture_output: If True, captures stdout and stderr (ignored if stream_output=True)
        check: If True, raises exception on error
        stream_output: If True, streams stdout/stderr to console in real-time

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
        if stream_output:
            # Stream output in real-time
            process = subprocess.Popen(
                cmd,
                cwd=str(cwd) if cwd else None,
                env=full_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            
            stdout_lines = []
            stderr_lines = []
            
            # Helper to read stream
            import threading
            
            def read_stream(stream, lines, echo_stream):
                for line in stream:
                    lines.append(line)
                    echo_stream.write(line)
                    echo_stream.flush()
            
            # Start threads to read stdout and stderr
            t_out = threading.Thread(target=read_stream, args=(process.stdout, stdout_lines, sys.stdout))
            t_err = threading.Thread(target=read_stream, args=(process.stderr, stderr_lines, sys.stderr))
            
            t_out.start()
            t_err.start()
            
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                t_out.join()
                t_err.join()
                raise subprocess.TimeoutExpired(cmd, timeout)
            
            t_out.join()
            t_err.join()
            
            stdout = "".join(stdout_lines)
            stderr = "".join(stderr_lines)
            
            return_code = process.returncode
            if check and return_code != 0:
                raise subprocess.CalledProcessError(return_code, cmd, output=stdout, stderr=stderr)
                
            return subprocess.CompletedProcess(cmd, return_code, stdout, stderr)

        else:
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
