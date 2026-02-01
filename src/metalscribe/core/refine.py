"""Módulo de refinamento de transcrições usando LLM."""

import logging
import os
from pathlib import Path
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


def load_refine_prompt() -> str:
    """
    Carrega o prompt de refinamento do arquivo markdown.

    Extrai o conteúdo do prompt removendo apenas o título principal,
    mas mantendo a estrutura markdown para melhor legibilidade pelo LLM.
    """
    prompt_path = Path(__file__).parent.parent.parent.parent / "docs" / "prompts" / "refine.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt não encontrado: {prompt_path}")
    content = prompt_path.read_text(encoding="utf-8")

    # Remove apenas o título principal "# Prompt de Refinamento de Transcrições"
    # mas mantém toda a estrutura markdown restante
    lines = content.split("\n")
    # Pula a primeira linha se for título
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    # Remove linha vazia inicial se houver
    if lines and not lines[0].strip():
        lines = lines[1:]

    return "\n".join(lines)


def call_openai_api(
    prompt: str, text: str, api_key: Optional[str] = None, model: str = "gpt-4o-mini"
) -> str:
    """
    Chama a API da OpenAI para refinar o texto.

    Args:
        prompt: Prompt do sistema
        text: Texto a ser refinado
        api_key: Chave da API (ou usa OPENAI_API_KEY do ambiente)
        model: Modelo a usar (padrão: gpt-4o-mini)

    Returns:
        Texto refinado
    """
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY não configurada. Configure a variável de ambiente ou passe --api-key"
        )

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        "temperature": 0.3,
    }

    logger.info(f"Chamando OpenAI API com modelo {model}...")
    with httpx.Client(timeout=300.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]


def call_anthropic_api(
    prompt: str, text: str, api_key: Optional[str] = None, model: str = "claude-3-5-sonnet-20241022"
) -> str:
    """
    Chama a API da Anthropic para refinar o texto.

    Args:
        prompt: Prompt do sistema
        text: Texto a ser refinado
        api_key: Chave da API (ou usa ANTHROPIC_API_KEY do ambiente)
        model: Modelo a usar (padrão: claude-3-5-sonnet-20241022)

    Returns:
        Texto refinado
    """
    api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY não configurada. Configure a variável de ambiente ou passe --api-key"
        )

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "max_tokens": 8192,
        "system": prompt,
        "messages": [
            {"role": "user", "content": text},
        ],
    }

    logger.info(f"Chamando Anthropic API com modelo {model}...")
    with httpx.Client(timeout=300.0) as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["content"][0]["text"]


def refine_text(
    text: str,
    provider: str = "openai",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    prompt_path: Optional[Path] = None,
) -> str:
    """
    Refina um texto usando LLM.

    Args:
        text: Texto a ser refinado
        provider: Provedor LLM ("openai" ou "anthropic")
        api_key: Chave da API (opcional, usa variável de ambiente se não fornecido)
        model: Modelo específico (opcional, usa padrão do provedor)
        prompt_path: Caminho para prompt customizado (opcional)

    Returns:
        Texto refinado
    """
    # Carrega prompt
    if prompt_path:
        prompt = prompt_path.read_text(encoding="utf-8")
    else:
        prompt = load_refine_prompt()

    # Usa o prompt completo (LLMs lidam bem com markdown estruturado)
    system_prompt = prompt

    # Chama API apropriada
    provider = provider.lower()
    if provider == "openai":
        model = model or "gpt-4o-mini"
        return call_openai_api(system_prompt, text, api_key=api_key, model=model)
    elif provider == "anthropic":
        model = model or "claude-3-5-sonnet-20241022"
        return call_anthropic_api(system_prompt, text, api_key=api_key, model=model)
    else:
        raise ValueError(f"Provedor não suportado: {provider}. Use 'openai' ou 'anthropic'")


def refine_markdown_file(
    input_path: Path,
    output_path: Path,
    provider: str = "openai",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    chunk_size: int = 10000,
) -> None:
    """
    Refina um arquivo markdown de transcrição, preservando estrutura e metadados.

    Args:
        input_path: Caminho do arquivo markdown de entrada
        output_path: Caminho do arquivo markdown de saída
        provider: Provedor LLM
        api_key: Chave da API
        model: Modelo específico
        chunk_size: Tamanho máximo de cada chunk para processar (caracteres)
    """
    content = input_path.read_text(encoding="utf-8")

    # Separa header/metadados do conteúdo principal
    # O formato do metalscribe tem: título, metadados, "---", e depois o conteúdo
    lines = content.split("\n")
    header_lines = []
    body_start_idx = 0

    # Encontra onde termina o header (linha "---")
    for i, line in enumerate(lines):
        if line.strip() == "---":
            body_start_idx = i + 1
            break
        header_lines.append(line)

    header = "\n".join(header_lines) if header_lines else ""
    body_lines = lines[body_start_idx:] if body_start_idx < len(lines) else lines
    body = "\n".join(body_lines).strip()

    if not body:
        logger.warning("Nenhum conteúdo encontrado para refinar. Copiando arquivo original.")
        output_path.write_text(content, encoding="utf-8")
        return

    # Processa o corpo
    logger.info(f"Processando {len(body)} caracteres de conteúdo...")
    refined_body = refine_text(body, provider=provider, api_key=api_key, model=model)

    # Reconstrói arquivo preservando header
    if header:
        output_content = header + "\n\n" + refined_body
    else:
        output_content = refined_body

    output_path.write_text(output_content, encoding="utf-8")
    logger.info(f"Arquivo refinado salvo em: {output_path}")
