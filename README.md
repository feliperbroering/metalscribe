# metalscribe

CLI 100% local para transcrição e diarização de áudio com aceleração GPU Metal/MPS no macOS.

## Características

- 🎤 **Transcrição**: Usa `whisper.cpp` com aceleração Metal GPU
- 👥 **Diarização**: Identifica locutores usando `pyannote.audio` com aceleração MPS GPU
- 📝 **Múltiplos formatos**: Gera JSON, SRT e Markdown
- ⚡ **100% Local**: Tudo roda na sua máquina, sem dependências de serviços externos (exceto refinamento opcional com LLM)
- ✨ **Refinamento opcional**: Use LLM para refinar transcrições e corrigir erros de ASR
- 🚀 **Performance**: Algoritmo de merge O(N+M) eficiente

## Requisitos

- macOS (com suporte Metal/MPS)
- Python 3.11+
- Homebrew
- ffmpeg
- Token do HuggingFace (para pyannote.audio)

## Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd metalscribe

# Instale o projeto
pip install -e .

# Configure dependências
metalscribe doctor --setup
```

## Uso Rápido

```bash
# Verificar dependências
metalscribe doctor --check-only

# Configurar ambiente (primeira vez)
metalscribe doctor --setup

# Pipeline completo (recomendado)
metalscribe run --input audio.m4a --model medium --speakers 2

# Ou use comandos individuais
metalscribe transcribe --input audio.m4a --model medium --lang pt
metalscribe diarize --input audio.m4a --speakers 2
metalscribe combine --transcript transcript.json --diarize diarize.json
```

## Comandos

### `metalscribe doctor`

Verifica e configura dependências do sistema.

```bash
metalscribe doctor --check-only  # Apenas verifica
metalscribe doctor --setup       # Configura dependências faltantes
```

### `metalscribe transcribe`

Transcreve áudio usando whisper.cpp.

```bash
metalscribe transcribe --input audio.m4a --model medium --lang pt
```

**Modelos disponíveis**: `tiny`, `base`, `small`, `medium`, `large-v3`

### `metalscribe diarize`

Identifica locutores usando pyannote.audio.

```bash
metalscribe diarize --input audio.m4a --speakers 2
```

### `metalscribe combine`

Combina resultados de transcrição e diarização.

```bash
metalscribe combine --transcript transcript.json --diarize diarize.json
```

### `metalscribe run`

Pipeline completo: transcrição + diarização + merge + export.

```bash
metalscribe run --input audio.m4a --model medium --speakers 2
```

Gera automaticamente:
- `audio_final.json` - JSON estruturado
- `audio_final.srt` - Legendas SRT
- `audio_final.md` - Markdown legível
- `audio_final.timings.log` - Log de timings

### `metalscribe refine`

Refina uma transcrição markdown usando LLM para corrigir erros de ASR, melhorar pontuação e preservar o estilo natural da fala.

```bash
# Refinar usando OpenAI (padrão)
export OPENAI_API_KEY="sua-chave-aqui"
metalscribe refine --input transcricao.md

# Refinar usando Anthropic
export ANTHROPIC_API_KEY="sua-chave-aqui"
metalscribe refine --input transcricao.md --provider anthropic

# Especificar modelo e arquivo de saída
metalscribe refine --input transcricao.md --output refinada.md --model gpt-4o
```

**Características:**
- Corrige erros fonéticos e semânticos (ex: "concerto" → "conserto")
- Preserva estilo informal, gírias e contrações
- Melhora pontuação mantendo prosódia natural
- Remove alucinações e repetições robóticas
- Mantém estrutura de falantes e timestamps

**Requisitos:**
- Chave de API (OpenAI ou Anthropic) configurada via variável de ambiente ou `--api-key`
- Dependência `httpx` instalada (incluída automaticamente)

## Formatos de Áudio Suportados

m4a, mp3, mp4, flac, ogg, webm, aac, wma, aiff, wav

## Performance

Para 1 hora de áudio:
- Conversão: ~6s
- Transcrição (medium): ~12 min
- Diarização: ~10 min
- Merge: <100ms
- **Total: ~22 min**

## Documentação

- [Technical Specification](docs/TECHSPEC.md)
- [API Reference](docs/api.md)
- [Troubleshooting](docs/troubleshooting.md)

## Desenvolvimento

```bash
# Instalar em modo desenvolvimento
pip install -e .

# Executar CLI
metalscribe --version

# Executar testes
pytest tests/
```

## Scripts de Instalação

Scripts auxiliares estão disponíveis em `scripts/`:

```bash
bash scripts/install_whisper_gpu.sh      # Instala whisper.cpp
bash scripts/install_diarization_gpu.sh  # Instala pyannote.audio
bash scripts/install_all.sh               # Instala tudo
```

## Licença

MIT

## Autor

Felipe R. Broering
