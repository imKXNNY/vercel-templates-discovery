import subprocess
import sys


def test_semantic_command_help():
    result = subprocess.run(
        [sys.executable, "-m", "vercel_templates.cli", "semantic", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "semantic" in result.stdout


def test_search_semantic_flag_help():
    result = subprocess.run(
        [sys.executable, "-m", "vercel_templates.cli", "search", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "--semantic" in result.stdout
