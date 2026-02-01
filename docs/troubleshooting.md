# Troubleshooting - metalscribe

## Problemas Comuns

### whisper.cpp não encontrado

**Sintoma**: `whisper.cpp não encontrado`

**Solução**:
```bash
metalscribe doctor --setup
# ou
bash scripts/install_whisper_gpu.sh
```

### pyannote.audio não encontrado

**Sintoma**: `pyannote.audio não está configurado`

**Solução**:
```bash
metalscribe doctor --setup
# ou
bash scripts/install_diarization_gpu.sh
```

### Token do HuggingFace não configurado

**Sintoma**: `Token do HuggingFace não encontrado`

**Solução**:
```bash
export HF_TOKEN=seu_token_aqui
# ou
export HUGGINGFACE_TOKEN=seu_token_aqui
```

### Metal/MPS não disponível

**Sintoma**: Processamento muito lento

**Verificação**:
```bash
metalscribe doctor --check-only
```

**Nota**: Metal/MPS só está disponível no macOS. Se estiver em outro sistema, o processamento será mais lento.

### Erro de conversão de áudio

**Sintoma**: `Falha ao converter áudio`

**Solução**:
1. Verifique se ffmpeg está instalado: `brew install ffmpeg`
2. Verifique se o arquivo de áudio está corrompido
3. Tente converter manualmente: `ffmpeg -i input.m4a -ar 16000 -ac 1 output.wav`

### Timeout na transcrição/diarização

**Sintoma**: `Comando excedeu timeout`

**Solução**:
- Arquivos muito longos podem precisar de mais tempo
- O timeout padrão é 1 hora
- Para arquivos maiores, considere dividir o áudio

## Logs e Debug

### Modo Verbose

Execute comandos com `--verbose` para ver logs detalhados:

```bash
metalscribe run --input audio.m4a --verbose
```

### Arquivo de Timings

O comando `run` gera `*.timings.log` com tempos de cada etapa.

## Suporte

Para mais ajuda, abra uma issue no GitHub.
