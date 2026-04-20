"""Snakemake integration hook.

For multi-step DAG pipelines (ingest → preprocess → analyze → report),
users can pair a labflow experiment with a Snakefile. This module provides
conveniences for calling Snakemake from within an experiment.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any


class SnakemakeIntegrationError(RuntimeError):
    pass


def run_snakemake(
    snakefile: str | Path,
    targets: list[str] | None = None,
    cores: int = 1,
    config: dict[str, Any] | None = None,
    profile: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Invoke Snakemake programmatically.

    Returns a dict with returncode, stdout, stderr, and parsed job summary if available.
    """
    if shutil.which("snakemake") is None:
        raise SnakemakeIntegrationError(
            "snakemake not installed. `pip install 'labflow[snakemake]'` or install directly."
        )
    cmd = ["snakemake", "--snakefile", str(snakefile), "--cores", str(cores)]
    if profile:
        cmd += ["--profile", profile]
    if config:
        for k, v in config.items():
            cmd += ["--config", f"{k}={v}"]
    if targets:
        cmd += list(targets)
    if dry_run:
        cmd += ["-n"]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "cmd": cmd,
    }
