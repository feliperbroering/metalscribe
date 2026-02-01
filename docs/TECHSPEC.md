# Technical Specification - metalscribe

## Arquitetura

### Fluxo de Processamento

```
Áudio de Entrada (m4a, mp3, etc.)
    ↓
ffmpeg → WAV 16kHz mono
    ↓
    ├─→ whisper.cpp (Metal GPU) → transcript.json
    └─→ pyannote.audio (MPS GPU) → diarize.json
    ↓
merge_segments() (algoritmo O(N+M))
    ↓
Export: JSON, SRT, Markdown
```

## Componentes Principais

### Core

- **audio.py**: Conversão de áudio via ffmpeg
- **whisper.py**: Wrapper para whisper.cpp
- **pyannote.py**: Wrapper para pyannote.audio
- **merge.py**: Algoritmo de combinação O(N+M)
- **checks.py**: Verificação de dependências
- **setup.py**: Setup de dependências

### Parsers

- **whisper_parser.py**: Parseia JSON do whisper.cpp (tolerante a formatos)
- **diarize_parser.py**: Parseia JSON do pyannote.audio

### Exporters

- **json_exporter.py**: Exporta JSON estruturado
- **srt_exporter.py**: Exporta SRT com prefixo de speaker
- **markdown_exporter.py**: Exporta Markdown legível

## Algoritmo de Merge

O algoritmo de merge usa two-pointer para eficiência O(N+M):

1. Itera sobre segmentos de transcrição (ordenados por tempo)
2. Para cada segmento, encontra segmento de diarização com maior overlap
3. Calcula overlap ratio: `overlap_duration / transcript_duration`
4. Atribui speaker do segmento de diarização com maior overlap

## Formatos de Saída

### JSON

```json
{
  "metadata": {...},
  "segments": [
    {
      "start_ms": 0,
      "end_ms": 2500,
      "text": "Olá, bem-vindo",
      "speaker": "SPEAKER_00"
    }
  ]
}
```

### SRT

```
1
00:00:00,000 --> 00:00:02,500
[SPEAKER_00] Olá, bem-vindo
```

### Markdown

```markdown
# Transcrição

## SPEAKER_00
**[00:00]** Olá, bem-vindo
```

## Dependências Externas

- **whisper.cpp**: Compilado com `WHISPER_METAL=1`
- **pyannote.audio 3.4.0**: Em venv isolado com PyTorch MPS
- **ffmpeg**: Via Homebrew

## Performance Esperada

Para 1 hora de áudio:
- Conversão: ~6s
- Transcrição (medium): ~12 min
- Diarização: ~10 min
- Merge: <100ms
- **Total: ~22 min**
