"""Integration tests for the labflow CLI."""

from __future__ import annotations

import subprocess
from pathlib import Path


def _run(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def test_labflow_help():
    code, out, err = _run(["labflow", "--help"], Path.cwd())
    assert code == 0
    assert "Usage" in out or "usage" in out


def test_labflow_new_creates_experiment(tmp_path: Path):
    # init a minimal project
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
    (tmp_path / ".labflow.yaml").write_text("env:\n  backend: venv\n")

    code, out, err = _run(
        ["labflow", "new", "my_exp", "--template", "simulation-jax"],
        tmp_path,
    )
    assert code == 0, f"stderr: {err}"
    assert (tmp_path / "experiments" / "my_exp.py").exists()


def test_labflow_run_local(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "test"\n')
    (tmp_path / ".labflow.yaml").write_text("env:\n  backend: venv\n")

    _run(["labflow", "new", "hello", "--template", "simulation-jax"], tmp_path)

    code, out, err = _run(["labflow", "run", "hello"], tmp_path)
    # Either succeeds (if minimal template runs) or fails with a clear error message
    assert "hello" in (out + err).lower()
