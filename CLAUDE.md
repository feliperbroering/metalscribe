# Claude AI - metalscribe Project Context

## Overview

metalscribe is a Python CLI that combines audio transcription (whisper.cpp) and speaker diarization (pyannote.audio) with native GPU acceleration on macOS using Metal and MPS.

## Architecture

### Main Flow

1. **Audio Conversion**: ffmpeg converts any format to WAV 16kHz mono
2. **Transcription**: whisper.cpp with Metal GPU generates text segments with timestamps
3. **Diarization**: pyannote.audio with MPS GPU identifies who speaks when
4. **Merge**: O(N+M) algorithm combines transcription and diarization
5. **Export**: Generates JSON, SRT, and Markdown

### Code Structure

- `src/metalscribe/cli.py` - Click entry point
- `src/metalscribe/config.py` - Configuration, paths, exit codes
- `src/metalscribe/commands/` - CLI commands
- `src/metalscribe/core/` - Business logic (whisper, pyannote, merge)
- `src/metalscribe/parsers/` - Output parsers
- `src/metalscribe/exporters/` - Format exporters

## Conventions

- Exit codes per spec (0-61)
- Structured logging with Rich
- All external commands via subprocess with timeout
- Model cache in `~/.cache/metalscribe/`
- Whisper installed via Homebrew or source build
- Pyannote in isolated venv at `pyannote_venv/`

## External Dependencies

- `whisper.cpp` - Compiled with Metal support
- `pyannote.audio` 3.4.0 - In separate Python venv
- `ffmpeg` - Via Homebrew

## Implementation Notes

- Whisper models downloaded from HuggingFace
- Pyannote requires HF token for models
- Merge uses two-pointer algorithm for O(N+M) efficiency
- SRT includes speaker prefix: `[SPEAKER_00] text`
