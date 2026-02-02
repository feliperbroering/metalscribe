# Troubleshooting - metalscribe

## Common Issues

### whisper.cpp not found

**Symptom**: Error message stating `whisper.cpp not found`.

**Solution**:
The internal wrapper requires `whisper` binary.
Run the setup command to compile/install it automatically:
```bash
metalscribe doctor --setup
```

### pyannote.audio not found or configured

**Symptom**: `pyannote.audio is not configured` or import errors.

**Solution**:
Metalscribe manages `pyannote.audio` in a dedicated virtual environment to ensure it uses the correct PyTorch version with MPS support.
```bash
metalscribe doctor --setup
```

### HuggingFace token not configured

**Symptom**: `HuggingFace token not found` during diarization or setup.

**Solution**:
Pyannote models require an accepted user agreement on HuggingFace.
1.  Get a token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens).
2.  Export it:
    ```bash
    export HF_TOKEN="your_token_here"
    ```

### Metal/MPS not available

**Symptom**: Processing is very slow (CPU speed).

**Check**:
```bash
metalscribe doctor --check-only
```
Look for "Metal GPU" and "MPS GPU" status. Note that Metal/MPS is only available on macOS.

### Audio conversion error

**Symptom**: `Failed to convert audio` or ffmpeg errors.

**Solution**:
1.  Ensure `ffmpeg` is installed: `brew install ffmpeg`
2.  Check if the input file is corrupted.
3.  Try converting manually to verify:
    ```bash
    ffmpeg -i input.m4a -ar 16000 -ac 1 output.wav
    ```

### LLM Authentication Errors

**Symptom**: Errors related to authentication when running `refine` or `format-meeting`.

**Solution**:
Metalscribe uses `claude-agent-sdk` which relies on Claude Code authentication.
Run:
```bash
claude auth login
```

## Logs and Debugging

### Verbose Mode

Use the `--verbose` (or `-v`) flag with any command to see detailed logs, including subprocess outputs.

```bash
metalscribe run --input audio.m4a --verbose
```

### Timings File

The `run` command automatically generates a `*.timings.log` file alongside the output. This file contains precise duration and Real-Time Factor (RTF) for each stage of the pipeline.
