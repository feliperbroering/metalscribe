# metalscribe

100% local CLI for audio transcription and speaker diarization with Metal/MPS GPU acceleration on macOS.

## Features

- 🎤 **Transcription**: Uses `whisper.cpp` with Metal GPU acceleration
- 👥 **Diarization**: Identifies speakers using `pyannote.audio` with MPS GPU acceleration
- 📝 **Multiple formats**: Generates JSON, SRT, and Markdown
- ⚡ **100% Local**: Everything runs on your machine, no external service dependencies (except optional LLM refinement)
- ✨ **Optional Refinement**: Use LLM to refine transcriptions and correct ASR errors
- 🚀 **Performance**: Efficient O(N+M) merge algorithm

## Requirements

- macOS (with Metal/MPS support)
- Python 3.11+
- Homebrew
- ffmpeg
- HuggingFace token (for pyannote.audio)

## Installation

### Via Homebrew (Recommended)

```bash
# Add tap
brew tap feliperbroering/metalscribe https://github.com/feliperbroering/metalscribe.git

# Install (everything is automatic!)
brew install metalscribe
# This will:
# 1. Install Python 3.11, ffmpeg, PyTorch, pyannote.audio
# 2. Compile whisper.cpp with Metal GPU support
# 3. Download models (~2-5 GB depending on choices)
# Total time: 15-40 minutes (first time only)

# Verify installation
metalscribe --version
```

**What gets installed:**
- ✅ Python 3.11
- ✅ ffmpeg
- ✅ PyTorch (with Metal GPU support)
- ✅ pyannote.audio
- ✅ whisper.cpp (compiled with Metal)
- ✅ Whisper models (you choose during install)
- ✅ pyannote models (cached in `~/.cache/huggingface/`)

**First run is slower (~15-40 min) because:**
- PyTorch binary download (~200MB)
- whisper.cpp compilation with Metal GPU support (~10 min)
- Whisper model download (500MB-1.5GB depending on size)
- pyannote cache setup

**Subsequent runs are instant** — everything is cached locally.

**Need HuggingFace token for diarization?**
- Free account at https://huggingface.co
- Token during install, or set `export HF_TOKEN="..."`

### From Source

```bash
# Clone the repository
git clone https://github.com/feliperbroering/metalscribe
cd metalscribe

# Install the project
pip install -e .

# Configure dependencies
metalscribe doctor --setup
```

## Quick Start

```bash
# Check dependencies
metalscribe doctor --check-only

# Configure environment (first time)
metalscribe doctor --setup

# Complete pipeline (recommended)
metalscribe run --input audio.m4a --model medium --speakers 2

# Or use individual commands
metalscribe transcribe --input audio.m4a --model medium --lang en
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

### `metalscribe transcribe`

Transcribes audio using whisper.cpp.

```bash
metalscribe transcribe --input audio.m4a --model medium --lang en
```

**Available models**: `tiny`, `base`, `small`, `medium`, `large-v3`

### `metalscribe diarize`

Identifies speakers using pyannote.audio.

```bash
metalscribe diarize --input audio.m4a --speakers 2
```

### `metalscribe combine`

Combines transcription and diarization results.

```bash
metalscribe combine --transcript transcript.json --diarize diarize.json
```

### `metalscribe run`

Complete pipeline: transcription + diarization + merge + export.

```bash
metalscribe run --input audio.m4a --model medium --speakers 2
```

Automatically generates:
- `audio_final.json` - Structured JSON
- `audio_final.srt` - SRT subtitles
- `audio_final.md` - Readable Markdown
- `audio_final.timings.log` - Timing log

### `metalscribe refine`

Refines markdown transcription using LLM to correct ASR errors, improve punctuation, and preserve natural speech style.

```bash
# Refine using OpenAI (default)
export OPENAI_API_KEY="your-key-here"
metalscribe refine --input transcript.md

# Refine using Anthropic
export ANTHROPIC_API_KEY="your-key-here"
metalscribe refine --input transcript.md --provider anthropic

# Specify model and output file
metalscribe refine --input transcript.md --output refined.md --model gpt-4o
```

**Features:**
- Corrects phonetic and semantic errors
- Preserves informal style, slang, and contractions
- Improves punctuation while maintaining natural prosody
- Removes hallucinations and robotic repetitions
- Maintains speaker structure and timestamps

**Requirements:**
- API key (OpenAI or Anthropic) configured via environment variable or `--api-key`
- `httpx` dependency installed (included automatically)

## Supported Audio Formats

m4a, mp3, mp4, flac, ogg, webm, aac, wma, aiff, wav

## Performance

For 1 hour of audio:
- Conversion: ~6s
- Transcription (medium): ~12 min
- Diarization: ~10 min
- Merge: <100ms
- **Total: ~22 min**

## Documentation

- [Technical Specification](docs/TECHSPEC.md)
- [API Reference](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)

## Development

```bash
# Install in development mode
pip install -e .

# Run CLI
metalscribe --version

# Run tests
pytest tests/
```

## Installation Scripts

Helper scripts are available in `scripts/`:

```bash
bash scripts/install_whisper_gpu.sh      # Installs whisper.cpp
bash scripts/install_diarization_gpu.sh  # Installs pyannote.audio
bash scripts/install_all.sh               # Installs everything
```

## License

MIT

## Author

Felipe R. Broering
