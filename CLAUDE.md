# Claude AI - Contexto do Projeto metalscribe

## Visão Geral

O metalscribe é um CLI Python que combina transcrição de áudio (whisper.cpp) e diarização (pyannote.audio) com aceleração GPU nativa no macOS usando Metal e MPS.

## Arquitetura

### Fluxo Principal

1. **Conversão de Áudio**: ffmpeg converte qualquer formato para WAV 16kHz mono
2. **Transcrição**: whisper.cpp com Metal GPU gera segmentos de texto com timestamps
3. **Diarização**: pyannote.audio com MPS GPU identifica quem fala quando
4. **Merge**: Algoritmo O(N+M) combina transcrição e diarização
5. **Export**: Gera JSON, SRT e Markdown

### Estrutura de Código

- `src/metalscribe/cli.py` - Entry point Click
- `src/metalscribe/config.py` - Configurações, paths, exit codes
- `src/metalscribe/commands/` - Comandos CLI
- `src/metalscribe/core/` - Lógica de negócio (whisper, pyannote, merge)
- `src/metalscribe/parsers/` - Parsers de output
- `src/metalscribe/exporters/` - Exportadores de formato

## Convenções

- Exit codes conforme spec (0-61)
- Logging estruturado com Rich
- Todos os comandos externos via subprocess com timeout
- Cache de modelos em `~/.cache/metalscribe/`
- Whisper instalado via Homebrew ou source build
- Pyannote em venv isolado em `pyannote_venv/`

## Dependências Externas

- `whisper.cpp` - Compilado com Metal support
- `pyannote.audio` 3.4.0 - Em venv Python separado
- `ffmpeg` - Via Homebrew

## Notas de Implementação

- Whisper models baixados do HuggingFace
- Pyannote requer token HF para modelos
- Merge usa algoritmo two-pointer para eficiência O(N+M)
- SRT inclui prefixo de speaker: `[SPEAKER_00] texto`
