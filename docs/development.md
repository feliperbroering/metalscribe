# Development Guide

## Conventions

- **Language**: Python 3.11+
- **Type Hints**: Strictly enforced
- **Style**: Ruff (line-length 100, see `pyproject.toml` for full config)
- **Error Handling**: Custom `ExitCode` enum in `config.py`
- **Logging**: `rich` library for user-facing output; `logging` for debug

## External Dependencies

### whisper.cpp

C++ implementation of OpenAI Whisper. Must be compiled with Metal GPU support.

- Installed via Homebrew or compiled from source by `metalscribe doctor --setup`
- Binary must be available as `whisper-cli` in PATH or Homebrew prefix
- Models downloaded to `~/.cache/metalscribe/models/`

### pyannote.audio

Speaker diarization library. Installed in a **dedicated virtual environment** (`~/.cache/metalscribe/pyannote_venv/`) to avoid dependency conflicts and ensure PyTorch MPS support.

- Requires a HuggingFace token (`HF_TOKEN`) with accepted model agreements
- Managed entirely by `metalscribe doctor --setup`

### ffmpeg

Required for audio conversion (any format → WAV 16kHz mono).

```bash
brew install ffmpeg
```

## LLM Integration

The project uses `claude-agent-sdk` to interface with Anthropic's Claude models.

- **Authentication**: OAuth via `claude auth login` (no API keys needed)
- **Default Models**: Configured per-command in `config.py`:
  - `refine`: `claude-opus-4-6` (with extended thinking)
  - `format-meeting`: `claude-opus-4-6` (with extended thinking)
- **Thinking Mode**: Automatically enabled for Opus 4.5/4.6 via `max_thinking_tokens` in `provider.py`
- **Prompts**: Stored in `docs/prompts/{lang}/` (e.g., `pt-BR/refine.md`)
- **Language Handling**: Maps Whisper codes (e.g., `pt`) to BCP 47 codes (e.g., `pt-BR`) for prompt selection

## Testing

```bash
# Run all tests
pytest tests/

# Run specific test suites
pytest tests/unit/
pytest tests/integration/
```

- **Unit Tests**: `tests/unit/`
- **Integration Tests**: `tests/integration/`
- **Fixtures**: `tests/fixtures/`

## Adding New Transcript Formats

The adapter system makes it easy to add support for new external transcript formats:

1. Add the format to `TranscriptFormat` enum in `adapters/registry.py`
2. Create an adapter class in `adapters/formats/` with `@register_adapter` decorator
3. Implement `detect()` and `parse()` methods
4. Import the adapter in `adapters/__init__.py`

See `adapters/formats/voxtral.py` for a reference implementation and `docs/api.md` for the full API.
