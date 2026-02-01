#!/bin/bash
# Script para instalar todas as dependências

set -e

echo "Instalando todas as dependências do metalscribe..."
echo ""

# Instala whisper.cpp
echo "=== Instalando whisper.cpp ==="
bash "$(dirname "$0")/install_whisper_gpu.sh"
echo ""

# Instala pyannote.audio
echo "=== Instalando pyannote.audio ==="
bash "$(dirname "$0")/install_diarization_gpu.sh"
echo ""

echo "✓ Todas as dependências instaladas!"
echo ""
echo "Execute 'metalscribe doctor --check-only' para verificar"
