#!/bin/bash
# Script to install all dependencies

set -e

echo "Installing all metalscribe dependencies..."
echo ""

# Install whisper.cpp
echo "=== Installing whisper.cpp ==="
bash "$(dirname "$0")/install_whisper_gpu.sh"
echo ""

# Install pyannote.audio
echo "=== Installing pyannote.audio ==="
bash "$(dirname "$0")/install_diarization_gpu.sh"
echo ""

echo "✓ All dependencies installed!"
echo ""
echo "Run 'metalscribe doctor --check-only' to verify"
