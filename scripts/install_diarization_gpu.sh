#!/bin/bash
# Script para instalar pyannote.audio com suporte MPS GPU

set -e

echo "Instalando pyannote.audio com suporte MPS GPU..."

# Verifica token do HuggingFace
if [ -z "$HF_TOKEN" ] && [ -z "$HUGGINGFACE_TOKEN" ]; then
    echo "✗ Erro: Token do HuggingFace não configurado"
    echo "Configure: export HF_TOKEN=seu_token"
    exit 1
fi

VENV_PATH="pyannote_venv"

# Cria venv se não existir
if [ ! -d "$VENV_PATH" ]; then
    echo "Criando venv..."
    python3 -m venv "$VENV_PATH"
fi

PYTHON="$VENV_PATH/bin/python"

echo "Atualizando pip..."
"$PYTHON" -m pip install --upgrade pip

echo "Instalando PyTorch com suporte MPS..."
"$PYTHON" -m pip install torch torchaudio

echo "Instalando pyannote.audio..."
"$PYTHON" -m pip install pyannote.audio==3.4.0

echo "Verificando suporte MPS..."
"$PYTHON" -c "import torch; print('MPS available:', torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False)"

echo "✓ pyannote.audio instalado com sucesso"
