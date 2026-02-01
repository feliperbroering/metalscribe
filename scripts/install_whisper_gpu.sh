#!/bin/bash
# Script para instalar whisper.cpp com suporte Metal GPU

set -e

echo "Instalando whisper.cpp com suporte Metal GPU..."

# Verifica se Homebrew está instalado
if ! command -v brew &> /dev/null; then
    echo "Homebrew não encontrado. Instalando..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Tenta instalar via Homebrew primeiro
if brew install whisper.cpp 2>/dev/null; then
    echo "✓ whisper.cpp instalado via Homebrew"
    exit 0
fi

# Se não funcionar, compila do source
echo "Compilando whisper.cpp do source..."

CACHE_DIR="$HOME/.cache/metalscribe"
WHISPER_DIR="$CACHE_DIR/whisper.cpp"

mkdir -p "$CACHE_DIR"

if [ ! -d "$WHISPER_DIR" ]; then
    echo "Clonando repositório whisper.cpp..."
    git clone https://github.com/ggerganov/whisper.cpp.git "$WHISPER_DIR"
fi

cd "$WHISPER_DIR"
echo "Compilando com suporte Metal..."
make clean || true
make WHISPER_METAL=1

if [ -f "$WHISPER_DIR/whisper" ]; then
    echo "✓ whisper.cpp compilado com sucesso"
    echo "Para usar, adicione ao PATH ou crie symlink:"
    echo "  sudo ln -s $WHISPER_DIR/whisper /usr/local/bin/whisper"
else
    echo "✗ Erro ao compilar whisper.cpp"
    exit 1
fi
