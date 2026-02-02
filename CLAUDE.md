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
6. **Refine** (optional): LLM corrects ASR errors, improves punctuation
7. **Format Meeting** (optional): LLM transforms transcription into structured meeting document

### Code Structure

- `src/metalscribe/cli.py` - Click entry point
- `src/metalscribe/config.py` - Configuration, paths, exit codes
- `src/metalscribe/commands/` - CLI commands
- `src/metalscribe/core/` - Business logic (whisper, pyannote, merge)
- `src/metalscribe/llm/` - LLM provider module (Claude Code SDK)
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

## LLM Commands

LLM commands use Claude Code with OAuth authentication (no API keys required).

### Authentication (One-time Setup)

```bash
# Install Claude Code CLI
npm install -g @anthropic-ai/claude-code

# Install Python SDK
pip install claude-agent-sdk

# Authenticate (opens browser for OAuth)
claude auth login
```

The commands will show a helpful setup guide if any component is missing.

### Global Language Configuration

Language is a **global setting** that flows through the entire pipeline:

1. Set language at transcription time with `--lang pt` (Whisper code)
2. The system maps to prompt language: `pt` → `pt-BR`
3. Language is saved in file metadata (`prompt_language: pt-BR`)
4. LLM commands (`refine`, `format-meeting`) automatically use the file's language

```
Whisper codes → Prompt codes
pt → pt-BR (Brazilian Portuguese) ✅ Available
en → en-US (American English) 🚧 Planned
es → es-ES (Spanish) 🚧 Planned
```

**Default**: If no language specified, uses `pt` (Portuguese).

Configure via:
- CLI flag: `metalscribe run -i audio.mp3 --lang pt`
- Environment variable: `METALSCRIBE_DEFAULT_LANGUAGE=pt`

### Prompt Languages

LLM prompts are organized by language in `docs/prompts/{language}/`:

```
docs/prompts/
├── pt-BR/              # Brazilian Portuguese (default)
│   ├── refine.md
│   └── format-meeting.md
└── README.md           # Instructions for adding new languages
```

**Note**: Current prompts are optimized for Brazilian Portuguese. A warning is displayed when using these commands.

### refine

Corrects ASR errors while preserving speech style:

```bash
metalscribe refine -i transcription.md
metalscribe refine -i transcription.md -o refined.md
metalscribe refine -i transcription.md --model claude-sonnet-4-20250514
```

Language is automatically detected from the file's `prompt_language` metadata.

### format-meeting

Transforms transcription into a professional meeting document:

```bash
metalscribe format-meeting -i meeting.md
metalscribe format-meeting -i meeting.md --yes  # skip confirmation
```

Features:
- Auto-detects language from file metadata
- Shows token estimation before processing
- Requires user confirmation (unless --yes flag)
- Outputs: executive summary, participants table, topics, action items, full structured transcript
