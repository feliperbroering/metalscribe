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
- `--input, -i`: Audio file (required)
- `--model, -m`: Whisper model [default: large-v3]
- `--lang, -l`: Language code
- `--speakers, -s`: Number of speakers
- `--output, -o`: Output file prefix
- `--llm-model`: LLM model for refine and format-meeting (uses Claude Code default if not specified)
- `--yes, -y`: Skip token confirmation prompt for format-meeting
- `--verbose, -v`: Verbose mode

**Example**:
```bash
metalscribe run-meeting --input audio.m4a --model large-v3 --speakers 2
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
