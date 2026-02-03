#!/bin/bash
# Script to install whisper.cpp with Metal GPU support

set -e

echo "Installing whisper.cpp with Metal GPU support..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Try installing via Homebrew first
if brew install whisper.cpp 2>/dev/null; then
    echo "✓ whisper.cpp installed via Homebrew"
    exit 0
fi

# If that doesn't work, compile from source
echo "Compiling whisper.cpp from source..."

CACHE_DIR="$HOME/.cache/metalscribe"
WHISPER_DIR="$CACHE_DIR/whisper.cpp"

mkdir -p "$CACHE_DIR"

if [ ! -d "$WHISPER_DIR" ]; then
    echo "Cloning whisper.cpp repository..."
    git clone https://github.com/ggerganov/whisper.cpp.git "$WHISPER_DIR"
fi

cd "$WHISPER_DIR"
echo "Compiling with Metal support..."
make clean || true
make WHISPER_METAL=1

if [ -f "$WHISPER_DIR/whisper" ]; then
    echo "✓ whisper.cpp compiled successfully"
    echo "To use, add to PATH or create symlink:"
    echo "  sudo ln -s $WHISPER_DIR/whisper /usr/local/bin/whisper"
else
    echo "✗ Error compiling whisper.cpp"
    exit 1
fi
