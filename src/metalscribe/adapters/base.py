"""Classe base para adaptadores de transcrição."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from metalscribe.core.models import MergedSegment


class TranscriptAdapter(ABC):
    """Classe base para adaptadores de transcrição."""

    # Gatilhos de detecção - lista de condições para identificar o formato
    # Exemplo: [{"field": "model", "contains": "voxtral"}]
    TRIGGERS: List[dict] = []

    @classmethod
    @abstractmethod
    def detect(cls, data: dict) -> bool:
        """
        Verifica se o JSON corresponde a este formato.

        Args:
            data: JSON carregado como dict

        Returns:
            True se o formato for reconhecido
        """
        pass

    @classmethod
    @abstractmethod
    def parse(cls, data: dict) -> List[MergedSegment]:
        """
        Converte o JSON para lista de MergedSegment.

        Args:
            data: JSON carregado como dict

        Returns:
            Lista de MergedSegment prontos para exportação
        """
        pass

    @classmethod
    def get_schema_path(cls) -> Path | None:
        """Retorna path do schema JSON para validação (opcional)."""
        return None

    @classmethod
    def validate(cls, data: dict) -> bool:
        """Valida JSON contra o schema (se disponível)."""
        schema_path = cls.get_schema_path()
        if schema_path and schema_path.exists():
            # Opcional: usar jsonschema para validar
            pass
        return True
