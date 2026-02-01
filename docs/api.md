# API Reference - metalscribe

## Comandos CLI

### `metalscribe doctor`

Verifica e configura dependências.

**Opções**:
- `--check-only`: Apenas verifica, não faz setup
- `--setup`: Configura dependências faltantes

**Exemplo**:
```bash
metalscribe doctor --check-only
metalscribe doctor --setup
```

### `metalscribe transcribe`

Transcreve áudio usando whisper.cpp.

**Opções**:
- `--input, -i`: Arquivo de áudio (obrigatório)
- `--model, -m`: Modelo (tiny, base, small, medium, large-v3) [padrão: medium]
- `--lang, -l`: Código de idioma (ex: pt, en)
- `--output, -o`: Arquivo JSON de saída
- `--verbose, -v`: Modo verbose

**Exemplo**:
```bash
metalscribe transcribe --input audio.m4a --model medium --lang pt
```

### `metalscribe diarize`

Identifica locutores usando pyannote.audio.

**Opções**:
- `--input, -i`: Arquivo de áudio (obrigatório)
- `--speakers, -s`: Número de speakers (opcional)
- `--output, -o`: Arquivo JSON de saída
- `--verbose, -v`: Modo verbose

**Exemplo**:
```bash
metalscribe diarize --input audio.m4a --speakers 2
```

### `metalscribe combine`

Combina resultados de transcrição e diarização.

**Opções**:
- `--transcript, -t`: Arquivo JSON de transcrição (obrigatório)
- `--diarize, -d`: Arquivo JSON de diarização (obrigatório)
- `--output, -o`: Prefixo dos arquivos de saída
- `--verbose, -v`: Modo verbose

**Exemplo**:
```bash
metalscribe combine --transcript transcript.json --diarize diarize.json
```

### `metalscribe run`

Pipeline completo: transcrição + diarização + merge + export.

**Opções**:
- `--input, -i`: Arquivo de áudio (obrigatório)
- `--model, -m`: Modelo do Whisper [padrão: medium]
- `--lang, -l`: Código de idioma
- `--speakers, -s`: Número de speakers
- `--output, -o`: Prefixo dos arquivos de saída
- `--verbose, -v`: Modo verbose

**Exemplo**:
```bash
metalscribe run --input audio.m4a --model medium --speakers 2
```

## Módulos Python

### `metalscribe.core.audio`

```python
from metalscribe.core.audio import convert_to_wav_16k

convert_to_wav_16k(input_path: Path, output_path: Path) -> None
```

### `metalscribe.core.whisper`

```python
from metalscribe.core.whisper import run_transcription

segments = run_transcription(
    audio_path: Path,
    model_name: str = "medium",
    language: Optional[str] = None,
    output_json: Optional[Path] = None,
) -> List[TranscriptSegment]
```

### `metalscribe.core.pyannote`

```python
from metalscribe.core.pyannote import run_diarization

segments = run_diarization(
    audio_path: Path,
    num_speakers: Optional[int] = None,
    output_json: Optional[Path] = None,
) -> List[DiarizeSegment]
```

### `metalscribe.core.merge`

```python
from metalscribe.core.merge import merge_segments

merged = merge_segments(
    transcript_segments: List[TranscriptSegment],
    diarize_segments: List[DiarizeSegment],
) -> List[MergedSegment]
```

### `metalscribe.exporters`

```python
from metalscribe.exporters import export_json, export_srt, export_markdown

export_json(segments: List[MergedSegment], output_path: Path, metadata: Optional[dict] = None)
export_srt(segments: List[MergedSegment], output_path: Path)
export_markdown(segments: List[MergedSegment], output_path: Path, title: Optional[str] = None, metadata: Optional[dict] = None)
```

## Modelos de Dados

### `TranscriptSegment`

```python
@dataclass
class TranscriptSegment:
    start_ms: int
    end_ms: int
    text: str
```

### `DiarizeSegment`

```python
@dataclass
class DiarizeSegment:
    start_ms: int
    end_ms: int
    speaker: str
```

### `MergedSegment`

```python
@dataclass
class MergedSegment:
    start_ms: int
    end_ms: int
    text: str
    speaker: str
```
