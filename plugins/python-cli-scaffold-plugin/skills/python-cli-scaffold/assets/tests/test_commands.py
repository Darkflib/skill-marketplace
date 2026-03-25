"""
Tests for CLI commands.
"""

from click.testing import CliRunner

from app.cli import cli


def test_version():
    """Test version command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["version"])
    
    assert result.exit_code == 0
    assert "Version" in result.output


def test_greet():
    """Test greet command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["example", "greet", "--name", "Alice", "--count", "2"])
    
    assert result.exit_code == 0
    assert "Hello Alice!" in result.output


def test_help():
    """Test help output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    
    assert result.exit_code == 0
    assert "{{PROJECT_NAME}}" in result.output
