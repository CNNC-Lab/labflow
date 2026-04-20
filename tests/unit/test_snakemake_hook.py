"""Tests for the optional Snakemake integration hook."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from labflow.snakemake_hook import SnakemakeIntegrationError, run_snakemake


def test_run_snakemake_missing_binary_raises():
    """When snakemake is not on PATH, we raise a clear error."""
    with (
        patch("labflow.snakemake_hook.shutil.which", return_value=None),
        pytest.raises(SnakemakeIntegrationError, match="snakemake not installed"),
    ):
        run_snakemake(snakefile="Snakefile")


def test_run_snakemake_builds_command():
    """Verify command assembly without actually invoking snakemake."""

    class _FakeProc:
        returncode = 0
        stdout = "done"
        stderr = ""

    captured = {}

    def _fake_run(cmd, capture_output=True, text=True):
        captured["cmd"] = cmd
        return _FakeProc()

    with (
        patch("labflow.snakemake_hook.shutil.which", return_value="/usr/bin/snakemake"),
        patch("labflow.snakemake_hook.subprocess.run", side_effect=_fake_run),
    ):
        result = run_snakemake(
            snakefile="workflow/Snakefile",
            targets=["all"],
            cores=4,
            config={"input": "data/"},
            profile="slurm",
            dry_run=True,
        )

    assert result["returncode"] == 0
    cmd = captured["cmd"]
    assert "snakemake" in cmd[0]
    assert "--snakefile" in cmd
    assert "workflow/Snakefile" in cmd
    assert "--cores" in cmd
    assert "4" in cmd
    assert "--profile" in cmd
    assert "slurm" in cmd
    assert "--config" in cmd
    assert any("input=data/" in s for s in cmd)
    assert "-n" in cmd
    assert "all" in cmd
