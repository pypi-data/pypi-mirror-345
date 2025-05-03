import subprocess
import sys
import os
import pytest

SCRIPT_PATH = os.path.abspath("run_concurrently.py")

def test_single_command_success():
    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, "echo 'Hello, World!'"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 0
    assert "Hello, World!" in result.stdout

def test_multiple_commands_success():
    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, "echo 'First'", "echo 'Second'"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert result.returncode == 0
    assert "First" in result.stdout
    assert "Second" in result.stdout
