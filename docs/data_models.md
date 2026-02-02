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
