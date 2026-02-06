# Architecture

## Overview

metalscribe is a Python CLI for audio transcription and speaker diarization on macOS, leveraging Metal and MPS for GPU acceleration. It integrates `whisper.cpp` (transcription) and `pyannote.audio` (diarization), with optional LLM-based refinement using Claude.

## Processing Pipeline

1. **Audio Conversion** — `ffmpeg` converts input to WAV 16kHz mono
2. **Transcription** — `whisper.cpp` (Metal GPU) generates text segments with timestamps
3. **Diarization** — `pyannote.audio` (MPS GPU) identifies speaker segments
4. **Merge** — O(N+M) algorithm combines transcription and diarization by timestamp overlap
5. **Export** — Generates JSON, SRT, and Markdown outputs
6. **Refine (LLM)** — Corrects ASR errors and improves punctuation using Claude
7. **Format (LLM)** — Structures the transcription into a meeting document (summary, action items, etc.)

### Alternative Entry Point: Import Transcript

External transcripts (e.g., Voxtral) can be imported via `--import-transcript`, skipping steps 1–4 and starting directly at Export (step 5). See the adapter system in `src/metalscribe/adapters/`.

## Code Structure

```
src/metalscribe/
├── cli.py                  # Entry point (Click)
├── config.py               # Configuration, constants, path management
├── commands/               # CLI command implementations
│   ├── doctor.py           #   System dependency checker/installer
│   ├── context.py          #   Domain context file management
│   ├── transcribe.py       #   Whisper transcription
│   ├── diarize.py          #   Pyannote diarization
│   ├── combine.py          #   Merge transcript + diarization
│   ├── run.py              #   Full local pipeline (steps 1-5)
│   ├── run_meeting.py      #   Full pipeline + LLM (steps 1-7)
│   ├── refine.py           #   LLM refinement (step 6)
│   └── format_meeting.py   #   LLM meeting formatting (step 7)
├── core/                   # Business logic
│   ├── whisper.py          #   whisper.cpp wrapper
│   ├── pyannote.py         #   pyannote.audio wrapper (isolated venv)
│   ├── merge.py            #   Merge algorithm
│   ├── audio.py            #   Audio conversion (ffmpeg)
│   ├── setup.py            #   Dependency installation
│   ├── checks.py           #   System checks
│   ├── refine.py           #   LLM refine logic
│   ├── format_meeting.py   #   LLM format logic
│   └── models.py           #   Data models (TranscriptSegment, etc.)
├── adapters/               # External transcript importers
│   ├── importer.py         #   Entry point: import_transcript()
│   ├── registry.py         #   TranscriptFormat enum + adapter registry
│   ├── base.py             #   TranscriptAdapter base class
│   ├── detector.py         #   Automatic format detection
│   └── formats/            #   Individual format adapters
│       └── voxtral.py      #     Voxtral adapter
├── llm/                    # LLM integration (claude-agent-sdk)
│   ├── provider.py         #   LLMProvider with query/stream
│   ├── auth.py             #   OAuth authentication
│   └── exceptions.py       #   LLM error types
├── exporters/              # Output formatters
│   ├── json_exporter.py
│   ├── srt_exporter.py
│   └── markdown_exporter.py
└── parsers/                # Tool output parsers
    ├── whisper_parser.py
    └── diarize_parser.py
```

## Output File Naming

The pipeline produces numbered output files:

```
{basename}_01_transcript.json       # Whisper transcription
{basename}_02_diarize.json          # Pyannote diarization
{basename}_03_merged.md             # Merged transcript + diarization
{basename}_04_refined.md            # LLM-refined transcription
{basename}_05_formatted-meeting.md  # LLM-formatted meeting document
{basename}_06_timings.log           # Execution timing
```

When using `--import-transcript`, files start at step 3 (steps 1–2 are skipped).
