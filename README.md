# metalscribe

100% local CLI for audio transcription and speaker diarization with Metal/MPS GPU acceleration on macOS.

## Features

- 🎤 **Transcription**: Uses `whisper.cpp` with Metal GPU acceleration
- 👥 **Diarization**: Identifies speakers using `pyannote.audio` with MPS GPU acceleration
- 📝 **Multiple formats**: Generates JSON, SRT, and Markdown
- ⚡ **100% Local**: Core processing runs locally on your machine with no external dependencies
- ✨ **Optional Refinement**: Use LLM (Claude) to refine transcriptions and correct ASR errors
- 🚀 **Performance**: Efficient O(N+M) merge algorithm

## Requirements

- macOS (with Metal/MPS support)
- Python 3.11+
- Homebrew
- ffmpeg
- HuggingFace token (for pyannote.audio)
- Claude Code (optional, for LLM refinement)

## Installation

### From Source (Recommended for Developers)

```bash
# Clone the repository
git clone https://github.com/feliperbroering/metalscribe
cd metalscribe

# Install the project
pip install -e .

# Configure dependencies
metalscribe doctor --setup
```

### Initial Setup

After installation, verify and configure your environment:

1. **Check dependencies:**
   ```bash
   metalscribe doctor --check-only
   ```

2. **Setup external components (whisper.cpp, pyannote):**
   ```bash
   metalscribe doctor --setup
   ```

3. **Configure HuggingFace Token (for diarization):**
   Get a free token at https://huggingface.co/settings/tokens
   ```bash
   export HF_TOKEN="your_token_here"
   ```

4. **Authenticate with Claude (for LLM features):**
   ```bash
   # Install Claude Code CLI if not already installed
   npm install -g @anthropic-ai/claude-code
   
   # Login
   claude auth login
   ```

## Quick Start

```bash
# Complete pipeline (recommended)
metalscribe run --input audio.m4a --model large-v3 --speakers 2

# Or use individual commands
metalscribe transcribe --input audio.m4a --model large-v3 --lang en
metalscribe diarize --input audio.m4a --speakers 2
metalscribe combine --transcript transcript.json --diarize diarize.json
```

## Commands

### `metalscribe doctor`

Checks and configures system dependencies.

```bash
metalscribe doctor --check-only  # Just check
metalscribe doctor --setup       # Configure missing dependencies
```

### `metalscribe run`

Complete pipeline: transcription + diarization + merge + export.

```bash
metalscribe run --input audio.m4a --model large-v3 --speakers 2
```

Automatically generates:
- `*_transcript.json`: Transcription only (without speaker info)
- `*_diarize.json`: Diarization only (speaker info only)
- `*_merged.json`: Merged structured JSON (transcription + diarization)
- `*_merged.srt`: SRT subtitles
- `*_merged.md`: Readable Markdown
- `*.timings.log`: Performance timing log

### `metalscribe run-meeting`

Complete pipeline with LLM refinement and meeting formatting: transcription + diarization + merge + export + refine + format-meeting.

**Prerequisite:** Authenticate with `claude auth login`.

```bash
metalscribe run-meeting --input audio.m4a --model large-v3 --speakers 2
```

Automatically generates all files from `run` plus:
- `*_refined.md`: Refined transcription (corrected ASR errors, improved punctuation)
- `*_formatted-meeting.md`: Professional meeting document (summary, action items, etc.)

**Options:**
- `--llm-model`: Specify LLM model (uses Claude Code default if not specified)
- `--yes, -y`: Skip token confirmation prompt for format-meeting

### `metalscribe refine`

Refines markdown transcription using LLM to correct ASR errors, improve punctuation, and preserve natural speech style.

**Prerequisite:** Authenticate with `claude auth login`.

```bash
# Refine using default model
metalscribe refine --input transcript.md

# Specify model and output file
metalscribe refine --input transcript.md --output refined.md --model claude-3-5-sonnet-20241022
```

**Features:**
- Corrects phonetic and semantic errors
- Preserves informal style, slang, and contractions
- Improves punctuation while maintaining natural prosody
- Removes hallucinations and robotic repetitions
- Maintains speaker structure and timestamps

### `metalscribe format-meeting`

Transforms meeting transcriptions into professional structured documents.

**Prerequisite:** Authenticate with `claude auth login`.

```bash
# Format meeting transcription
metalscribe format-meeting --input meeting.md

# Skip confirmation prompt
metalscribe format-meeting --input meeting.md --yes
```

**Output includes:**
- Executive summary
- Participants table with inferred names and roles
- Topics discussed with timestamps
- Action items table
- Full structured transcription

## LLM Configuration

The LLM commands (`refine` and `format-meeting`) use **Claude Code** for authentication and execution.

### Language Support

Language is a global setting that flows through the entire pipeline.
When you run `metalscribe run --lang pt`, the system:
1. Uses Portuguese for Whisper transcription
2. Automatically selects the corresponding prompt (e.g., `pt-BR`) for LLM refinement

**Available Prompts:**
- `pt-BR` (Brazilian Portuguese) - Default
- Support for other languages can be added in `docs/prompts/`

## Documentation

- [Technical Specification](docs/TECHSPEC.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Prompt Engineering](docs/prompts/README.md)

## Development

```bash
# Install in development mode
pip install -e .

# Run tests
pytest tests/
```

## License

MIT

## Author

Felipe R. Broering
