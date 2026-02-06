# API Reference - metalscribe

## CLI Commands

### `metalscribe doctor`

Checks and configures dependencies.

**Options**:
- `--check-only`: Only check, do not setup
- `--setup`: Configure missing dependencies

**Example**:
```bash
metalscribe doctor --check-only
metalscribe doctor --setup
```

### `metalscribe transcribe`

Transcribes audio using whisper.cpp.

**Options**:
- `--input, -i`: Audio file (required)
- `--model, -m`: Model (tiny, base, small, medium, large-v3) [default: large-v3]
- `--lang, -l`: Language code (e.g., pt, en)
- `--output, -o`: Output JSON file
- `--verbose, -v`: Verbose mode

**Example**:
```bash
metalscribe transcribe --input audio.m4a --model large-v3 --lang en
```

### `metalscribe diarize`

Identifies speakers using pyannote.audio.

**Options**:
- `--input, -i`: Audio file (required)
- `--speakers, -s`: Number of speakers (optional)
- `--output, -o`: Output JSON file
- `--verbose, -v`: Verbose mode

**Example**:
```bash
metalscribe diarize --input audio.m4a --speakers 2
```

### `metalscribe combine`

Combines transcription and diarization results.

**Options**:
- `--transcript, -t`: Transcription JSON file (required)
- `--diarize, -d`: Diarization JSON file (required)
- `--output, -o`: Output file prefix
- `--verbose, -v`: Verbose mode

**Example**:
```bash
metalscribe combine --transcript transcript.json --diarize diarize.json
```

### `metalscribe context`

Manage domain context files for improved transcription quality. Context files provide terminology, proper nouns, and domain knowledge to the LLM refinement stage.

**Subcommands**:
- `show`: Display the context template
- `copy <path>`: Copy template to a file for editing
- `validate <path>`: Validate a context file

**Examples**:
```bash
# Show the context template
metalscribe context show

# Copy template to a file
metalscribe context copy my-context.md

# Validate a context file
metalscribe context validate my-context.md
```

### `metalscribe run`

Complete pipeline: transcription + diarization + merge + export.

**Options**:
- `--input, -i`: Audio file (required)
- `--model, -m`: Whisper model [default: large-v3]
- `--lang, -l`: Language code
- `--speakers, -s`: Number of speakers
- `--output, -o`: Output file prefix
- `--verbose, -v`: Verbose mode

**Example**:
```bash
metalscribe run --input audio.m4a --model large-v3 --speakers 2
```

### `metalscribe run-meeting`

Complete pipeline with LLM refinement and meeting formatting: transcription + diarization + merge + export + refine + format-meeting.

**Prerequisite:** Authenticate with `claude auth login`.

**Options**:
- `--input, -i`: Audio file (mutually exclusive with `--import-transcript`)
- `--import-transcript`: External transcript JSON (skips transcription/diarization steps)
- `--model, -m`: Whisper model [default: large-v3]
- `--lang, -l`: Language code
- `--speakers, -s`: Number of speakers
- `--output, -o`: Output file prefix
- `--context, -c`: Domain context file for improved transcription quality
- `--llm-model`: LLM model for refine and format-meeting (uses Claude Code default if not specified)
- `--yes, -y`: Skip token confirmation prompt for format-meeting
- `--limit`: Limit audio processing to X minutes (for testing)
- `--verbose, -v`: Verbose mode

**Examples**:
```bash
# From audio file (full pipeline)
metalscribe run-meeting --input audio.m4a --model large-v3 --speakers 2

# From external transcript JSON
metalscribe run-meeting --import-transcript transcript.json --context domain.md --yes

# With all options
metalscribe run-meeting --input audio.m4a --context domain.md --llm-model claude-3-5-sonnet-20241022 --yes
```

**Supported Import Formats**:
- **Voxtral**: Automatically detected from JSON structure
- Additional formats can be added via the adapter system (see `src/metalscribe/adapters/`)

### `metalscribe refine`

Refines markdown transcription using LLM to correct ASR errors, improve punctuation, and preserve natural speech style.

**Prerequisite:** Authenticate with `claude auth login`.

**Options**:
- `--input, -i`: Markdown transcription file (mutually exclusive with `--import-transcript`)
- `--import-transcript`: External transcript JSON (converts to markdown automatically)
- `--output, -o`: Output refined markdown file [default: input_04_refined.md]
- `--model, -m`: Specific model (uses Claude Code default if not specified)
- `--verbose, -v`: Verbose mode

**Examples**:
```bash
# Refine markdown file
metalscribe refine --input transcript.md

# Refine from external transcript JSON
metalscribe refine --import-transcript transcript.json --output refined.md

# With specific model
metalscribe refine --input transcript.md --model claude-3-5-sonnet-20241022
```

### `metalscribe format-meeting`

Transforms meeting transcriptions into professional structured documents.

**Prerequisite:** Authenticate with `claude auth login`.

**Options**:
- `--input, -i`: Markdown transcription file (mutually exclusive with `--import-transcript`)
- `--import-transcript`: External transcript JSON (converts to markdown automatically)
- `--output, -o`: Output formatted markdown file [default: input_05_formatted-meeting.md]
- `--context, -c`: Domain context file for improved quality
- `--model, -m`: Specific model (uses Claude Code default if not specified)
- `--yes, -y`: Skip token confirmation prompt
- `--verbose, -v`: Verbose mode

**Examples**:
```bash
# Format markdown file
metalscribe format-meeting --input meeting.md --yes

# Format from external transcript JSON with context
metalscribe format-meeting --import-transcript transcript.json --context domain.md --yes

# With specific model
metalscribe format-meeting --input meeting.md --model claude-3-5-sonnet-20241022 --yes
```

## Python Modules

### `metalscribe.core.audio`

```python
from metalscribe.core.audio import convert_to_wav_16k

convert_to_wav_16k(input_path: Path, output_path: Path) -> None
```

### `metalscribe.core.whisper`

```python
from metalscribe.core.whisper import run_transcription

segments = run_transcription(
    audio_path: Path,
    model_name: str = "large-v3",
    language: Optional[str] = None,
    output_json: Optional[Path] = None,
) -> List[TranscriptSegment]
```

### `metalscribe.core.pyannote`

```python
from metalscribe.core.pyannote import run_diarization

segments = run_diarization(
    audio_path: Path,
    num_speakers: Optional[int] = None,
    output_json: Optional[Path] = None,
) -> List[DiarizeSegment]
```

### `metalscribe.core.merge`

```python
from metalscribe.core.merge import merge_segments

merged = merge_segments(
    transcript_segments: List[TranscriptSegment],
    diarize_segments: List[DiarizeSegment],
) -> List[MergedSegment]
```

### `metalscribe.exporters`

```python
from metalscribe.exporters import export_json, export_srt, export_markdown

export_json(segments: List[MergedSegment], output_path: Path, metadata: Optional[dict] = None)
export_srt(segments: List[MergedSegment], output_path: Path)
export_markdown(segments: List[MergedSegment], output_path: Path, title: Optional[str] = None, metadata: Optional[dict] = None)
```

### `metalscribe.adapters`

```python
from metalscribe.adapters import import_transcript, detect_format, TranscriptFormat

# Import external transcript (auto-detects format)
segments = import_transcript(json_path: Path) -> List[MergedSegment]

# Detect format manually
format = detect_format(data: dict) -> TranscriptFormat | None

# Available formats
TranscriptFormat.VOXTRAL  # Voxtral transcription services
```

**Adding New Formats:**

```python
from metalscribe.adapters import TranscriptAdapter, register_adapter, TranscriptFormat
from metalscribe.core.models import MergedSegment

@register_adapter(TranscriptFormat.YOUR_FORMAT)
class YourFormatAdapter(TranscriptAdapter):
    @classmethod
    def detect(cls, data: dict) -> bool:
        # Return True if data matches your format
        return "your_identifier" in data
    
    @classmethod
    def parse(cls, data: dict) -> List[MergedSegment]:
        # Convert your format to MergedSegment list
        segments = []
        for item in data["items"]:
            segments.append(MergedSegment(
                start_ms=item["start"] * 1000,
                end_ms=item["end"] * 1000,
                text=item["text"],
                speaker=item["speaker"],
            ))
        return segments
```

## Data Models

### `TranscriptSegment`

```python
@dataclass
class TranscriptSegment:
    start_ms: int
    end_ms: int
    text: str
```

### `DiarizeSegment`

```python
@dataclass
class DiarizeSegment:
    start_ms: int
    end_ms: int
    speaker: str
```

### `MergedSegment`

```python
@dataclass
class MergedSegment:
    start_ms: int
    end_ms: int
    text: str
    speaker: str
```
