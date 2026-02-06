# metalscribe

Python CLI for audio transcription + diarization on macOS (Metal/MPS GPU). Uses whisper.cpp, pyannote.audio, and Claude for LLM refinement.

## Documentation Index

| Document | Contents |
|----------|----------|
| `docs/architecture.md` | Pipeline stages, code structure, file naming |
| `docs/development.md` | Conventions, dependencies, LLM integration, testing |
| `docs/api.md` | CLI commands and Python API reference |
| `docs/data_models.md` | Data structures, merge algorithm, adapter system |
| `docs/troubleshooting.md` | Common issues and debugging |
| `docs/prompts/README.md` | Prompt engineering, language system, adding languages |

## Source Map

```
src/metalscribe/
  cli.py, config.py
  commands/  run.py run_meeting.py transcribe.py diarize.py combine.py refine.py format_meeting.py context.py doctor.py
  core/      whisper.py pyannote.py merge.py audio.py setup.py checks.py refine.py format_meeting.py models.py
  adapters/  importer.py registry.py base.py detector.py formats/{voxtral.py}
  llm/       provider.py auth.py exceptions.py
  exporters/ json_exporter.py srt_exporter.py markdown_exporter.py
  parsers/   whisper_parser.py diarize_parser.py
```
