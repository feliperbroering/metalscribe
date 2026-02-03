"""Tests for context CLI commands."""

from __future__ import annotations

from click.testing import CliRunner

from metalscribe.commands.context import context
from metalscribe.config import ExitCode


def _valid_context() -> str:
    return (
        "## Área de Conhecimento\n\n"
        "Domínio: Saúde.\n\n"
        "## Glossário\n\n"
        "| Termo | Significado | Erros ASR comuns |\n"
        "|-------|-------------|------------------|\n"
        "| hipertensão | pressão alta | hiper tensão |\n\n"
        "## Nomes e Entidades\n\n"
        "| Nome/Entidade | Tipo | Erros ASR comuns |\n"
        "|---------------|------|------------------|\n"
        "| Ana Souza | pessoa | Ana Sousa |\n"
    )


def test_context_show_outputs_template():
    runner = CliRunner()
    result = runner.invoke(context, ["show"])
    assert result.exit_code == 0
    assert "Domain Context Template" in result.output


def test_context_copy_creates_file(tmp_path):
    runner = CliRunner()
    output = tmp_path / "context.md"
    result = runner.invoke(context, ["copy", str(output)])
    assert result.exit_code == 0
    assert output.exists()


def test_context_copy_refuses_overwrite(tmp_path):
    runner = CliRunner()
    output = tmp_path / "context.md"
    output.write_text("existing", encoding="utf-8")
    result = runner.invoke(context, ["copy", str(output)])
    assert result.exit_code == ExitCode.INVALID_INPUT


def test_context_validate_exit_codes(tmp_path):
    runner = CliRunner()
    valid_file = tmp_path / "valid.md"
    invalid_file = tmp_path / "invalid.md"

    valid_file.write_text(_valid_context(), encoding="utf-8")
    invalid_file.write_text("## Área de Conhecimento\n\nDomínio: X", encoding="utf-8")

    valid_result = runner.invoke(context, ["validate", str(valid_file)])
    assert valid_result.exit_code == 0

    invalid_result = runner.invoke(context, ["validate", str(invalid_file)])
    assert invalid_result.exit_code == ExitCode.INVALID_INPUT
