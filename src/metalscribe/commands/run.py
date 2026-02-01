"""Comando run - pipeline completo."""

import logging
import tempfile
from pathlib import Path

import click
from rich.console import Console

from metalscribe.core.audio import convert_to_wav_16k
from metalscribe.core.merge import merge_segments
from metalscribe.core.pyannote import run_diarization
from metalscribe.core.whisper import run_transcription
from metalscribe.exporters.json_exporter import export_json
from metalscribe.exporters.markdown_exporter import export_markdown
from metalscribe.exporters.srt_exporter import export_srt
from metalscribe.utils.audio_info import get_audio_duration
from metalscribe.utils.logging import log_timing, setup_logging

console = Console()
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Arquivo de áudio de entrada",
)
@click.option(
    "--model",
    "-m",
    type=click.Choice(["tiny", "base", "small", "medium", "large-v3"], case_sensitive=False),
    default="medium",
    help="Modelo do Whisper",
)
@click.option(
    "--lang",
    "-l",
    type=str,
    default=None,
    help="Código de idioma (ex: pt, en)",
)
@click.option(
    "--speakers",
    "-s",
    type=int,
    default=None,
    help="Número de speakers (opcional, auto-detecta se não especificado)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Prefixo dos arquivos de saída (padrão: baseado no input)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Modo verbose",
)
def run(input: Path, model: str, lang: str, speakers: int, output: Path, verbose: bool) -> None:
    """Pipeline completo: transcrição + diarização + merge + export."""
    setup_logging(verbose=verbose)

    import time

    start_time = time.time()

    # Determina prefixo de output
    if output is None:
        output = input.with_suffix("").with_suffix("_final")
    else:
        output = Path(output)

    # Obtém duração do áudio para calcular RTF
    audio_duration = get_audio_duration(input)

    # Etapa 1: Conversão de áudio
    console.print("[cyan]Etapa 1: Convertendo áudio...[/cyan]")
    wav_path = Path(tempfile.mktemp(suffix=".wav"))
    convert_start = time.time()
    convert_to_wav_16k(input, wav_path)
    convert_time = time.time() - convert_start
    convert_rtf = convert_time / audio_duration if audio_duration > 0 else None
    log_timing("Conversão", convert_time, rtf=convert_rtf)

    # Etapa 2: Transcrição
    console.print("[cyan]Etapa 2: Transcrevendo...[/cyan]")
    transcript_json = Path(tempfile.mktemp(suffix=".json"))
    transcribe_start = time.time()
    transcript_segments = run_transcription(
        wav_path, model_name=model, language=lang, output_json=transcript_json
    )
    transcribe_time = time.time() - transcribe_start
    transcribe_rtf = transcribe_time / audio_duration if audio_duration > 0 else None
    log_timing("Transcrição", transcribe_time, rtf=transcribe_rtf)

    # Etapa 3: Diarização
    console.print("[cyan]Etapa 3: Diarizando...[/cyan]")
    diarize_json = Path(tempfile.mktemp(suffix=".json"))
    diarize_start = time.time()
    diarize_segments = run_diarization(wav_path, num_speakers=speakers, output_json=diarize_json)
    diarize_time = time.time() - diarize_start
    diarize_rtf = diarize_time / audio_duration if audio_duration > 0 else None
    log_timing("Diarização", diarize_time, rtf=diarize_rtf)

    # Etapa 4: Merge
    console.print("[cyan]Etapa 4: Combinando...[/cyan]")
    merge_start = time.time()
    merged = merge_segments(transcript_segments, diarize_segments)
    merge_time = time.time() - merge_start
    log_timing("Merge", merge_time)

    # Etapa 5: Export
    console.print("[cyan]Etapa 5: Exportando...[/cyan]")
    export_start = time.time()

    json_path = output.with_suffix(".json")
    srt_path = output.with_suffix(".srt")
    md_path = output.with_suffix(".md")

    metadata = {
        "model": model,
        "language": lang or "auto",
        "num_speakers": speakers or "auto",
        "input_file": str(input),
    }

    export_json(merged, json_path, metadata=metadata)
    export_srt(merged, srt_path)
    export_markdown(merged, md_path, title=input.stem, metadata=metadata)

    export_time = time.time() - export_start
    log_timing("Export", export_time)

    # Timings log
    timings_log = output.with_suffix(".timings.log")
    total_time = time.time() - start_time
    total_rtf = total_time / audio_duration if audio_duration > 0 else None
    with open(timings_log, "w") as f:
        f.write(f"Duração do áudio: {audio_duration:.2f}s\n")
        f.write(f"\nConversão: {convert_time:.2f}s")
        if convert_rtf:
            f.write(f" (RTF: {convert_rtf:.3f})")
        f.write(f"\nTranscrição: {transcribe_time:.2f}s")
        if transcribe_rtf:
            f.write(f" (RTF: {transcribe_rtf:.3f})")
        f.write(f"\nDiarização: {diarize_time:.2f}s")
        if diarize_rtf:
            f.write(f" (RTF: {diarize_rtf:.3f})")
        f.write(f"\nMerge: {merge_time:.2f}s\n")
        f.write(f"Export: {export_time:.2f}s\n")
        f.write(f"\nTotal: {total_time:.2f}s")
        if total_rtf:
            f.write(f" (RTF: {total_rtf:.3f})")
        f.write("\n")

    log_timing("Total", total_time)

    console.print("\n[green]✓ Pipeline concluído![/green]")
    console.print("[green]Arquivos gerados:[/green]")
    console.print(f"  - {json_path}")
    console.print(f"  - {srt_path}")
    console.print(f"  - {md_path}")
    console.print(f"  - {timings_log}")
