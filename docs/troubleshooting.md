# Troubleshooting - metalscribe

## Common Issues

### whisper.cpp not found

**Symptom**: `whisper.cpp not found`

**Solution**:
```bash
metalscribe doctor --setup
# or
bash scripts/install_whisper_gpu.sh
```

### pyannote.audio not found

**Symptom**: `pyannote.audio is not configured`

**Solution**:
```bash
metalscribe doctor --setup
# or
bash scripts/install_diarization_gpu.sh
```

### HuggingFace token not configured

**Symptom**: `HuggingFace token not found`

**Solution**:
```bash
export HF_TOKEN=your_token_here
# or
export HUGGINGFACE_TOKEN=your_token_here
```

### Metal/MPS not available

**Symptom**: Processing is very slow

**Check**:
```bash
metalscribe doctor --check-only
```

**Note**: Metal/MPS is only available on macOS. On other systems, processing will be slower.

### Audio conversion error

**Symptom**: `Failed to convert audio`

**Solution**:
1. Check if ffmpeg is installed: `brew install ffmpeg`
2. Check if audio file is corrupted
3. Try manual conversion: `ffmpeg -i input.m4a -ar 16000 -ac 1 output.wav`

### Timeout in transcription/diarization

**Symptom**: `Command exceeded timeout`

**Solution**:
- Very long files may need more time
- Default timeout is 1 hour
- For larger files, consider splitting the audio

## Logs and Debug

### Verbose Mode

Run commands with `--verbose` to see detailed logs:

```bash
metalscribe run --input audio.m4a --verbose
```

### Timings File

The `run` command generates `*.timings.log` with timing for each step.

## Support

For more help, open an issue on GitHub.
