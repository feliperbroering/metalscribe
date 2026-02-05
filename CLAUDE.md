# Developer Context - metalscribe

## Overview

metalscribe is a Python CLI for audio transcription and diarization on macOS, leveraging Metal and MPS for GPU acceleration. It integrates `whisper.cpp` (transcription) and `pyannote.audio` (diarization), followed by an optional LLM-based refinement stage using Claude.

## Architecture

### Processing Pipeline

1.  **Audio Conversion**: `ffmpeg` converts input to WAV 16kHz mono.
2.  **Transcription**: `whisper.cpp` (Metal GPU) generates text segments with timestamps.
3.  **Diarization**: `pyannote.audio` (MPS GPU) identifies speaker segments.
4.  **Merge**: A generic O(N+M) algorithm combines transcription and diarization results based on timestamp overlap.
5.  **Export**: Generates outputs in JSON, SRT, and Markdown formats.
6.  **Refine (LLM)**: Corrects ASR errors and improves punctuation using Claude (via `claude-agent-sdk`).
7.  **Format (LLM)**: Structures the transcription into a meeting document (summary, action items, etc.).

**Alternative Entry Point:**
- **Import Transcript**: External transcripts (e.g., Voxtral) can be imported via `--import-transcript`, skipping steps 1-4 and starting directly at Export (step 5).

### Code Structure

-   `src/metalscribe/`
    -   `cli.py`: Main entry point using `click`.
    -   `config.py`: Configuration, constants, and path management.
    -   `commands/`: Implementation of CLI commands (`run`, `run_meeting`, `transcribe`, `diarize`, `refine`, etc.).
    -   `core/`: Core business logic.
        -   `whisper.py`: Wrapper for `whisper.cpp` CLI.
        -   `pyannote.py`: Wrapper for `pyannote.audio` (runs in isolated venv).
        -   `merge.py`: Merge algorithm implementation.
        -   `setup.py`: Dependency installation and setup logic.
    -   `adapters/`: External transcript importers (extensible via adapter pattern).
        -   `importer.py`: Entry point for importing external transcripts.
        -   `registry.py`: Format registry and enum.
        -   `base.py`: Base adapter class.
        -   `detector.py`: Automatic format detection.
        -   `formats/`: Individual format adapters (Voxtral, etc.).
    -   `llm/`: LLM integration using `claude-agent-sdk`.
    -   `parsers/`: Parsers for tool outputs (Whisper JSON, Pyannote JSON).
    -   `exporters/`: Output formatters (SRT, Markdown, JSON).

## Conventions

-   **Language**: Python 3.11+.
-   **Type Hints**: Strictly enforced.
-   **Style**: Ruff default settings (line-length 100).
-   **Error Handling**: Custom `ExitCode` enum in `config.py`.
-   **Logging**: `rich` library for user-facing output; structured logs for debugging.

## External Dependencies

-   **whisper.cpp**: Must be compiled with `WHISPER_METAL=1`. Can be installed via Homebrew or compiled from source by `metalscribe doctor`.
-   **pyannote.audio**: Installed in a dedicated virtual environment (`~/.cache/metalscribe/pyannote_venv`) to avoid dependency conflicts and ensure PyTorch MPS support.
-   **ffmpeg**: Required for audio conversion.

## LLM Integration

The project uses `claude-agent-sdk` to interface with Anthropic's Claude models.
-   **Auth**: OAuth via `claude auth login`.
-   **Prompts**: Stored in `docs/prompts/{lang}/`.
-   **Language Handling**: Maps Whisper language codes (e.g., `pt`) to BCP 47 codes (e.g., `pt-BR`) to select the appropriate prompt.

## Testing

-   **Unit Tests**: `tests/unit/`
-   **Integration Tests**: `tests/integration/`
-   **Fixtures**: `tests/fixtures/`

Run tests with: `pytest tests/`
