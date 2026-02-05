# Technical Specification - metalscribe

## Data Models

The core data structures used throughout the pipeline are defined in `src/metalscribe/core/models.py`.

### `TranscriptSegment`
Represents a single segment from the Whisper transcription.

```python
@dataclass
class TranscriptSegment:
    start_ms: int
    end_ms: int
    text: str
```

### `DiarizeSegment`
Represents a speaker segment identified by Pyannote.

```python
@dataclass
class DiarizeSegment:
    start_ms: int
    end_ms: int
    speaker: str
```

### `MergedSegment`
The final output segment after combining transcription and diarization.

```python
@dataclass
class MergedSegment:
    start_ms: int
    end_ms: int
    text: str
    speaker: str
```

## Merge Algorithm

The merge process (`src/metalscribe/core/merge.py`) combines transcription and diarization streams. Since both streams are sorted by time, we use an efficient O(N+M) two-pointer algorithm.

1.  Iterate through each `TranscriptSegment`.
2.  Maintain a pointer to the current `DiarizeSegment`.
3.  For the current transcription segment, scan forward in the diarization list to find overlapping segments.
4.  Calculate the overlap duration between the transcription segment and candidate diarization segments.
5.  Assign the speaker from the diarization segment with the **highest overlap ratio**.
    *   `overlap_ratio = overlap_duration / transcript_duration`
6.  If no overlap is found, assign `UNKNOWN`.

## Transcript Import System

The adapter system (`src/metalscribe/adapters/`) enables importing transcriptions from external services, bypassing the transcription and diarization steps.

### Architecture

```
adapters/
├── importer.py       # Entry point: import_transcript()
├── registry.py       # TranscriptFormat enum + adapter registry
├── base.py           # TranscriptAdapter base class
├── detector.py       # Automatic format detection
└── formats/
    └── voxtral.py    # Voxtral format adapter
```

### How It Works

1. **Detection**: `detect_format()` iterates through registered adapters and calls their `detect()` method
2. **Parsing**: The appropriate adapter's `parse()` method converts the external format to `List[MergedSegment]`
3. **Output**: Returns standardized `MergedSegment` objects ready for export

### Supported Formats

**Voxtral** (`TranscriptFormat.VOXTRAL`):
- Detected by: `model` field containing "voxtral" or segments with `speaker_id`
- Converts: seconds to milliseconds, `speaker_1` to `SPEAKER_01`

### Adding New Formats

1. Add to `TranscriptFormat` enum
2. Create adapter class with `@register_adapter(TranscriptFormat.YOUR_FORMAT)`
3. Implement `detect()` and `parse()` methods
4. Import in `adapters/__init__.py`

The system automatically registers and uses the new adapter.

## Output Formats

### JSON
Structured dump of the internal `MergedSegment` list, preserving all timing information.

```json
{
  "metadata": { ... },
  "segments": [
    {
      "start_ms": 0,
      "end_ms": 2500,
      "text": "Hello, welcome",
      "speaker": "SPEAKER_00"
    }
  ]
}
```

### SRT
Standard subtitle format. Timestamps are formatted as `HH:MM:SS,mmm`. Speaker labels are prepended to the text.

```
1
00:00:00,000 --> 00:00:02,500
[SPEAKER_00] Hello, welcome
```

### Markdown
Human-readable format optimized for reading and LLM processing. Segments are grouped by speaker to reduce visual noise.

```markdown
# Transcription

## SPEAKER_00
**[00:00]** Hello, welcome
```
