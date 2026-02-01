"""Comando refine - refinamento de transcrições usando LLM."""

import logging
from pathlib import Path

import click
from rich.console import Console

from metalscribe.core.refine import refine_markdown_file
from metalscribe.utils.logging import setup_logging

console = Console()
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--input",
    "-i",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Arquivo markdown de transcrição a ser refinado",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    default=None,
    help="Arquivo markdown de saída refinado (padrão: input_refined.md)",
)
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["openai", "anthropic"], case_sensitive=False),
    default="openai",
    help="Provedor LLM a usar (padrão: openai)",
)
@click.option(
    "--api-key",
    type=str,
    default=None,
    help="Chave da API (opcional, usa variável de ambiente se não fornecido)",
)
@click.option(
    "--model",
    "-m",
    type=str,
    default=None,
    help="Modelo específico (padrão depende do provedor)",
)
@click.option(
    "--chunk-size",
    type=int,
    default=10000,
    help="Tamanho máximo de chunk para processar (caracteres, padrão: 10000)",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Modo verbose",
)
def refine(
    input: Path,
    output: Path,
    provider: str,
    api_key: str,
    model: str,
    chunk_size: int,
    verbose: bool,
) -> None:
    """
    Refina uma transcrição markdown usando LLM para corrigir erros de ASR.

    Requer configuração de API key via variável de ambiente:
    - OPENAI_API_KEY para provider 'openai'
    - ANTHROPIC_API_KEY para provider 'anthropic'

    Exemplos:
        metalscribe refine -i transcricao.md
        metalscribe refine -i transcricao.md -o refinada.md --provider anthropic
        metalscribe refine -i transcricao.md --model gpt-4o
    """
    setup_logging(verbose=verbose)

    import time

    start_time = time.time()

    # Determina arquivo de saída
    if output is None:
        output = input.with_name(f"{input.stem}_refined.md")

    console.print(f"[cyan]Refinando transcrição usando {provider}...[/cyan]")
    console.print(f"[dim]Entrada: {input}[/dim]")
    console.print(f"[dim]Saída: {output}[/dim]")

    try:
        refine_markdown_file(
            input_path=input,
            output_path=output,
            provider=provider,
            api_key=api_key,
            model=model,
            chunk_size=chunk_size,
        )

        elapsed = time.time() - start_time
        console.print(f"\n[green]✓ Refinamento concluído em {elapsed:.2f}s[/green]")
        console.print(f"[green]Arquivo gerado: {output}[/green]")
    except ValueError as e:
        console.print(f"[red]Erro: {e}[/red]")
        raise click.Abort()
    except Exception as e:
        logger.exception("Erro durante refinamento")
        console.print(f"[red]Erro durante refinamento: {e}[/red]")
        raise click.Abort()
