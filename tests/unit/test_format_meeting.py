"""Tests for the format-meeting command and core module."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from metalscribe.core.format_meeting import (
    PRICING,
    estimate_tokens,
    format_meeting_file,
    format_meeting_text,
    load_format_meeting_prompt,
)


class TestLoadFormatMeetingPrompt:
    """Tests for loading the format-meeting prompt."""

    def test_load_prompt_returns_string(self):
        """Test that the prompt is loaded as a string."""
        prompt = load_format_meeting_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_load_prompt_contains_expected_content(self):
        """Test that the prompt contains expected sections."""
        prompt = load_format_meeting_prompt()
        # Check for key sections from the prompt
        assert "SYSTEM ROLE" in prompt
        assert "CONTEXTO" in prompt
        assert "ESTRUTURA DO DOCUMENTO DE SAÍDA" in prompt
        assert "SUMÁRIO EXECUTIVO" in prompt
        assert "PONTOS DE AÇÃO" in prompt

    def test_load_prompt_removes_title(self):
        """Test that the main title is removed from the prompt."""
        prompt = load_format_meeting_prompt()
        # The title "# format.md — ..." should be removed
        assert not prompt.startswith("# format.md")


class TestEstimateTokens:
    """Tests for token estimation."""

    def test_estimate_tokens_basic(self):
        """Test basic token estimation."""
        text = "Hello world" * 100  # 1100 chars
        prompt = "System prompt" * 100  # 1300 chars

        estimates = estimate_tokens(text, prompt)

        assert "input_tokens" in estimates
        assert "output_tokens_estimate" in estimates
        assert "total_tokens_estimate" in estimates
        assert "input_cost_usd" in estimates
        assert "output_cost_usd" in estimates
        assert "total_cost_usd" in estimates

    def test_estimate_tokens_calculation(self):
        """Test that token estimation calculates correctly."""
        # 4000 chars should be ~1000 tokens
        text = "a" * 2000
        prompt = "b" * 2000

        estimates = estimate_tokens(text, prompt)

        # Input should be around 1000 tokens (4000 chars / 4 chars per token)
        assert estimates["input_tokens"] == 1000
        # Output estimate should be 1.8x input
        assert estimates["output_tokens_estimate"] == 1800
        # Total should be input + output
        assert estimates["total_tokens_estimate"] == 2800

    def test_estimate_tokens_cost_calculation(self):
        """Test that cost estimation is reasonable."""
        text = "a" * 40000  # 10K tokens
        prompt = "b" * 40000  # 10K tokens

        estimates = estimate_tokens(text, prompt)

        # 20K input tokens at $0.015/1K = $0.30
        # 36K output tokens at $0.075/1K = $2.70
        # Total should be $3.00
        assert estimates["input_cost_usd"] == pytest.approx(0.30, abs=0.01)
        assert estimates["output_cost_usd"] == pytest.approx(2.70, abs=0.01)
        assert estimates["total_cost_usd"] == pytest.approx(3.00, abs=0.02)

    def test_estimate_tokens_empty_text(self):
        """Test estimation with empty text."""
        estimates = estimate_tokens("", "prompt")

        assert estimates["input_tokens"] >= 0
        assert estimates["total_cost_usd"] >= 0


class TestDefaultValues:
    """Tests for default configuration values."""

    def test_pricing_structure(self):
        """Test that pricing has correct structure."""
        assert "default" in PRICING
        assert "input" in PRICING["default"]
        assert "output" in PRICING["default"]
        assert PRICING["default"]["input"] > 0
        assert PRICING["default"]["output"] > 0


class TestLLMProviderIntegration:
    """Tests for LLM provider integration."""

    @patch("metalscribe.core.format_meeting.LLMProvider")
    def test_format_meeting_text_uses_llm_provider(self, mock_provider_class):
        """Test that format_meeting_text uses LLMProvider correctly."""
        # Setup mock
        mock_provider_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Formatted text"
        mock_provider_instance.query.return_value = mock_response
        mock_provider_class.return_value = mock_provider_instance

        result = format_meeting_text(text="Raw transcription", model="test-model")

        # Verify LLMProvider was called
        mock_provider_class.assert_called_once_with(model="test-model")
        mock_provider_instance.query.assert_called_once()
        assert result == "Formatted text"


class TestFormatMeetingText:
    """Tests for the format_meeting_text function."""

    @patch("metalscribe.core.format_meeting.LLMProvider")
    @patch("metalscribe.core.format_meeting.load_format_meeting_prompt")
    def test_format_meeting_text_loads_prompt(self, mock_load_prompt, mock_provider_class):
        """Test that format_meeting_text loads and uses the prompt."""
        mock_load_prompt.return_value = "Test prompt"
        mock_provider_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "Formatted text"
        mock_provider_instance.query.return_value = mock_response
        mock_provider_class.return_value = mock_provider_instance

        result = format_meeting_text(text="Raw transcription", model=None)

        mock_load_prompt.assert_called_once_with(None)
        mock_provider_instance.query.assert_called_once()
        # Verify prompt is included in the query (query is called with text=...)
        call_kwargs = mock_provider_instance.query.call_args[1]
        call_text = call_kwargs.get("text", "")
        assert "Test prompt" in call_text
        assert "Raw transcription" in call_text
        assert result == "Formatted text"


class TestFormatMeetingFile:
    """Tests for the format_meeting_file function."""

    @patch("metalscribe.core.format_meeting.format_meeting_text")
    def test_format_meeting_file_reads_and_writes(self, mock_format_text, tmp_path):
        """Test that file is read and written correctly."""
        # Create input file
        input_file = tmp_path / "input.md"
        input_file.write_text(
            "# Meeting\n\n## Metadata\n\n- Date: 2025-01-01\n\n---\n\nSPEAKER_00: Hello"
        )

        output_file = tmp_path / "output.md"

        mock_format_text.return_value = "# Formatted Meeting\n\nFormatted content"

        format_meeting_file(
            input_path=input_file,
            output_path=output_file,
            model=None,
        )

        # Verify output was written
        assert output_file.exists()
        content = output_file.read_text()
        assert "Formatted" in content
        # Verify format_meeting_text was called with body content
        mock_format_text.assert_called_once()
        assert "SPEAKER_00: Hello" in mock_format_text.call_args[0][0]

    @patch("metalscribe.core.format_meeting.format_meeting_text")
    def test_format_meeting_file_empty_content(self, mock_format_text, tmp_path):
        """Test handling of file with no content after header."""
        # Create input file with only header
        input_file = tmp_path / "input.md"
        input_file.write_text("# Meeting\n\n## Metadata\n\n---\n")

        output_file = tmp_path / "output.md"

        format_meeting_file(
            input_path=input_file,
            output_path=output_file,
            model=None,
        )

        # Should copy original file when no content
        mock_format_text.assert_not_called()
        assert output_file.exists()
        assert output_file.read_text() == input_file.read_text()

    @patch("metalscribe.core.format_meeting.format_meeting_text")
    def test_format_meeting_file_preserves_header_separation(self, mock_format_text, tmp_path):
        """Test that header is separated from body correctly."""
        input_file = tmp_path / "input.md"
        input_file.write_text(
            "# Meeting Title\n\n## Metadata\n\n- Key: Value\n\n---\n\nBody content here"
        )

        output_file = tmp_path / "output.md"
        mock_format_text.return_value = "Formatted body"

        format_meeting_file(
            input_path=input_file,
            output_path=output_file,
            model=None,
        )

        # Verify only body was sent to format_meeting_text
        call_args = mock_format_text.call_args[0][0]
        assert "Body content here" in call_args
        assert "Meeting Title" not in call_args
        assert "Metadata" not in call_args
