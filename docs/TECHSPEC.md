# Technical Specification - metalscribe

## Architecture

### Processing Flow

```
Input Audio (m4a, mp3, etc.)
    ↓
ffmpeg → WAV 16kHz mono
    ↓
    ├─→ whisper.cpp (Metal GPU) → transcript.json
    └─→ pyannote.audio (MPS GPU) → diarize.json
    ↓
merge_segments() (O(N+M) algorithm)
    ↓
Export: JSON, SRT, Markdown
```

## Main Components

### Core

- **audio.py**: Audio conversion via ffmpeg
- **whisper.py**: whisper.cpp wrapper
- **pyannote.py**: pyannote.audio wrapper
- **merge.py**: O(N+M) merge algorithm
- **checks.py**: Dependency verification
- **setup.py**: Dependency setup

### Parsers

- **whisper_parser.py**: Parses whisper.cpp JSON (format-tolerant)
- **diarize_parser.py**: Parses pyannote.audio JSON

### Exporters

- **json_exporter.py**: Exports structured JSON
- **srt_exporter.py**: Exports SRT with speaker prefix
- **markdown_exporter.py**: Exports readable Markdown

## Merge Algorithm

The merge algorithm uses two-pointer for O(N+M) efficiency:

1. Iterates over transcription segments (ordered by time)
2. For each segment, finds diarization segment with highest overlap
3. Calculates overlap ratio: `overlap_duration / transcript_duration`
4. Assigns speaker from diarization segment with highest overlap

## Output Formats

### JSON

```json
{
  "metadata": {...},
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

```
1
00:00:00,000 --> 00:00:02,500
[SPEAKER_00] Hello, welcome
```

### Markdown

```markdown
# Transcription

## SPEAKER_00
**[00:00]** Hello, welcome
```

## External Dependencies

- **whisper.cpp**: Compiled with `WHISPER_METAL=1`
- **pyannote.audio 3.4.0**: In isolated venv with PyTorch MPS
- **ffmpeg**: Via Homebrew

## Expected Performance

For 1 hour of audio:
- Conversion: ~6s
- Transcription (medium): ~12 min
- Diarization: ~10 min
- Merge: <100ms
- **Total: ~22 min**
