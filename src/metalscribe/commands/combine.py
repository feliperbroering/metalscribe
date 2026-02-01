"""Comando de combinação."""

import logging
from pathlib import Path

import click
from rich.console import Console

from metalscribe.core.merge import merge_segments
from metalscribe.exporters.json_exporter import export_json
from metalscribe.exporters.markdown_exporter import export_markdown
from metalscribe.exporters.srt_exporter import export_srt
from metalscribe.parsers.diarize_parser import parse_diarize_output
from metalscribe.parsers.whisper_parser import parse_whisper_output
from metalscribe.utils.logging import log_timing, setup_logging

console = Console()
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--transcript",
    "-t",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Arquivo JSON de transcrição",
)
@click.option(
    "--diarize",
    "-d",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Arquivo JSON de diarização",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Prefixo dos arquivos de saída (padrão: baseado no transcript)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Modo verbose",
)
def combine(transcript: Path, diarize: Path, output: Path, verbose: bool) -> None:
    """Combina resultados de transcrição e diarização."""
    setup_logging(verbose=verbose)

    import time

    start_time = time.time()

    # Parseia inputs
    console.print("[cyan]Carregando arquivos...[/cyan]")
    transcript_segments = parse_whisper_output(transcript)
    diarize_segments = parse_diarize_output(diarize)

    load_time = time.time() - start_time
    log_timing("Carregamento", load_time)

    # Merge
    console.print("[cyan]Combinando segmentos...[/cyan]")
    merge_start = time.time()
    merged = merge_segments(transcript_segments, diarize_segments)
    merge_time = time.time() - merge_start
    log_timing("Merge", merge_time)

    # Determina prefixo de output
    if output is None:
        output = transcript.with_suffix("").with_suffix("_final")
    else:
        output = Path(output)

    # Exporta formatos
    console.print("[cyan]Exportando formatos...[/cyan]")
    export_start = time.time()

    json_path = output.with_suffix(".json")
    srt_path = output.with_suffix(".srt")
    md_path = output.with_suffix(".md")

    export_json(merged, json_path)
    export_srt(merged, srt_path)
    export_markdown(merged, md_path)

    export_time = time.time() - export_start
    log_timing("Export", export_time)

    total_time = time.time() - start_time
    log_timing("Total", total_time)

    console.print("[green]✓ Arquivos gerados:[/green]")
    console.print(f"  - {json_path}")
    console.print(f"  - {srt_path}")
    console.print(f"  - {md_path}")
