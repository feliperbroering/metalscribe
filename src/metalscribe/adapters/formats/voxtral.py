"""Adaptador para formato Voxtral."""

from pathlib import Path
from typing import List

from metalscribe.adapters.base import TranscriptAdapter
from metalscribe.adapters.registry import TranscriptFormat, register_adapter
from metalscribe.core.models import MergedSegment


@register_adapter(TranscriptFormat.VOXTRAL)
class VoxtralAdapter(TranscriptAdapter):
    """Adaptador para formato Voxtral (voxtral-mini-latest, etc)."""

    # Gatilhos de detecção - qualquer um desses indica formato Voxtral
    TRIGGERS = [
        {"field": "model", "contains": "voxtral"},
        {"field": "segments[0].type", "equals": "transcription_segment"},
        {"field": "segments[0].speaker_id", "exists": True},
    ]

    @classmethod
    def detect(cls, data: dict) -> bool:
        """Detecta formato Voxtral."""
        # Gatilho 1: campo 'model' contém 'voxtral'
        if "voxtral" in data.get("model", "").lower():
            return True

        # Gatilho 2: segments com speaker_id e type específico
        segments = data.get("segments", [])
        if segments:
            first = segments[0]
            if first.get("type") == "transcription_segment":
                return True
            if "speaker_id" in first:
                return True

        return False

    @classmethod
    def parse(cls, data: dict) -> List[MergedSegment]:
        """Converte Voxtral JSON para MergedSegment."""
        segments = []
        for seg in data.get("segments", []):
            # start/end em segundos -> ms
            start_ms = int(seg.get("start", 0) * 1000)
            end_ms = int(seg.get("end", 0) * 1000)
            text = seg.get("text", "").strip()

            # speaker_id: "speaker_1" -> "SPEAKER_01"
            speaker_id = seg.get("speaker_id", "unknown")
            speaker = cls._normalize_speaker(speaker_id)

            if text:
                segments.append(
                    MergedSegment(
                        start_ms=start_ms,
                        end_ms=end_ms,
                        text=text,
                        speaker=speaker,
                    )
                )
        return segments

    @staticmethod
    def _normalize_speaker(speaker_id: str) -> str:
        """Normaliza speaker_id para formato SPEAKER_XX."""
        # "speaker_1" -> "SPEAKER_01"
        if speaker_id.startswith("speaker_"):
            num = speaker_id.split("_")[1]
            return f"SPEAKER_{int(num):02d}"
        return speaker_id.upper()

    @classmethod
    def get_schema_path(cls) -> Path:
        return Path(__file__).parent / "schemas" / "voxtral.json"
