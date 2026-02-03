"""Configuration, constants, and system utilities."""

import os
import platform
from importlib import resources
from enum import IntEnum
from pathlib import Path


class ExitCode(IntEnum):
    """Exit codes as per spec section 5.2."""

    SUCCESS = 0
    GENERAL_ERROR = 1
    MISSING_DEPENDENCY = 2
    AUDIO_CONVERSION_FAILED = 10
    TRANSCRIPTION_FAILED = 20
    DIARIZATION_FAILED = 30
    MERGE_FAILED = 40
    EXPORT_FAILED = 50
    INVALID_INPUT = 60
    TIMEOUT = 61


def get_cache_dir() -> Path:
    """Returns the user cache directory."""
    cache_home = os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache")
    cache_dir = Path(cache_home) / "metalscribe"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_pyannote_venv_path() -> Path:
    """Returns the pyannote.audio venv path in cache."""
    return get_cache_dir() / "pyannote_venv"


def get_brew_prefix() -> Path:
    """Returns the Homebrew prefix."""
    if platform.machine() == "arm64":
        return Path("/opt/homebrew")
    return Path("/usr/local")


# Available Whisper models
WHISPER_MODELS = {
    "tiny": {
        "filename": "ggml-tiny.bin",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.bin",
    },
    "base": {
        "filename": "ggml-base.bin",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-base.bin",
    },
    "small": {
        "filename": "ggml-small.bin",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-small.bin",
    },
    "medium": {
        "filename": "ggml-medium.bin",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-medium.bin",
    },
    "large-v3": {
        "filename": "ggml-large-v3.bin",
        "url": "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3.bin",
    },
}

# Default LLM models for refine and format-meeting commands
# These are the model identifiers accepted by claude-agent-sdk
# Can use aliases ("sonnet", "opus") or full names ("claude-sonnet-4-5", "claude-opus-4-5")
DEFAULT_REFINE_MODEL = "claude-sonnet-4-5"  # Sonnet 4.5 for refine command
DEFAULT_FORMAT_MEETING_MODEL = "claude-opus-4-5"  # Opus 4.5 with thinking for format-meeting

# Legacy: Default LLM model (deprecated, use command-specific defaults above)
# None means use Claude Code SDK default model
# Can be overridden via METALSCRIBE_DEFAULT_LLM_MODEL environment variable
# If set to empty string, also uses SDK default
_env_model = os.environ.get("METALSCRIBE_DEFAULT_LLM_MODEL")
DEFAULT_LLM_MODEL = _env_model if _env_model and _env_model.strip() else None

# Global default language (Whisper code)
# Can be overridden via METALSCRIBE_DEFAULT_LANGUAGE environment variable
DEFAULT_LANGUAGE = os.environ.get("METALSCRIBE_DEFAULT_LANGUAGE") or "pt"

# Mapping from Whisper codes to prompt codes (BCP 47)
# Whisper uses ISO 639-1 codes (pt, en, es), prompts use BCP 47 (pt-BR, en-US, es-ES)
LANGUAGE_MAPPING = {
    "pt": "pt-BR",
    "en": "en-US",
    "es": "es-ES",
    "fr": "fr-FR",
    "de": "de-DE",
    "it": "it-IT",
    "ja": "ja-JP",
    "ko": "ko-KR",
    "zh": "zh-CN",
    # Add more languages as needed
}

# Languages with available prompts
SUPPORTED_PROMPT_LANGUAGES = ["pt-BR"]

# Default prompt language (derived from DEFAULT_LANGUAGE)
DEFAULT_PROMPT_LANGUAGE = LANGUAGE_MAPPING.get(DEFAULT_LANGUAGE, "pt-BR")


def get_prompt_language(whisper_lang: str | None = None) -> str:
    """
    Converts Whisper language code to prompt code.

    Args:
        whisper_lang: Whisper language code (e.g., "pt", "en").
                      If None, uses DEFAULT_LANGUAGE.

    Returns:
        Prompt code (e.g., "pt-BR", "en-US")
    """
    lang = whisper_lang or DEFAULT_LANGUAGE
    prompt_lang = LANGUAGE_MAPPING.get(lang, DEFAULT_PROMPT_LANGUAGE)

    # If mapped language has no prompts, use default
    if prompt_lang not in SUPPORTED_PROMPT_LANGUAGES:
        return DEFAULT_PROMPT_LANGUAGE

    return prompt_lang


def get_prompts_dir() -> Path:
    """Returns the base prompts directory."""
    prompts_dir = resources.files("metalscribe") / "prompts"
    if isinstance(prompts_dir, Path):
        return prompts_dir

    fallback_dir = Path(__file__).resolve().parent / "prompts"
    if not fallback_dir.exists():
        raise FileNotFoundError("Prompts directory not found in package resources.")
    return fallback_dir


def get_prompt_path(prompt_name: str, language: str | None = None) -> Path:
    """
    Returns the path for a specific prompt.

    Args:
        prompt_name: Prompt name (e.g., "refine", "format-meeting")
        language: BCP 47 language code (e.g., "pt-BR") or Whisper (e.g., "pt").
                  Uses DEFAULT_PROMPT_LANGUAGE if None.

    Returns:
        Path to the prompt file

    Raises:
        ValueError: If language is not supported
        FileNotFoundError: If prompt does not exist
    """
    # If Whisper code (2 letters), convert to BCP 47
    if language and len(language) == 2:
        lang = get_prompt_language(language)
    else:
        lang = language or DEFAULT_PROMPT_LANGUAGE

    if lang not in SUPPORTED_PROMPT_LANGUAGES:
        raise ValueError(
            f"Language '{lang}' not supported for prompts. "
            f"Available: {', '.join(SUPPORTED_PROMPT_LANGUAGES)}"
        )

    prompt_path = get_prompts_dir() / lang / f"{prompt_name}.md"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")

    return prompt_path
