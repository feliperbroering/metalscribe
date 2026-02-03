#!/bin/bash
# Script to install pyannote.audio with MPS GPU support

set -e

echo "Installing pyannote.audio with MPS GPU support..."

# Check HuggingFace token
if [ -z "$HF_TOKEN" ] && [ -z "$HUGGINGFACE_TOKEN" ]; then
    echo "✗ Error: HuggingFace token not configured"
    echo "Configure: export HF_TOKEN=your_token"
    exit 1
fi

VENV_PATH="pyannote_venv"

# Create venv if it doesn't exist
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating venv..."
    python3 -m venv "$VENV_PATH"
fi

PYTHON="$VENV_PATH/bin/python"

echo "Updating pip..."
"$PYTHON" -m pip install --upgrade pip

echo "Installing PyTorch with MPS support..."
"$PYTHON" -m pip install torch torchaudio

echo "Installing pyannote.audio..."
"$PYTHON" -m pip install pyannote.audio==3.4.0

echo "Verifying MPS support..."
"$PYTHON" -c "import torch; print('MPS available:', torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False)"

echo "✓ pyannote.audio installed successfully"
