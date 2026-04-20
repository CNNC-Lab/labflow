"""marimo notebook exploration template.

marimo notebooks are pure .py files (not .ipynb) with reactive execution.
This wrapper lets labflow track and run them as experiments.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass

from labflow import experiment


@dataclass
class EXPERIMENT_NAMEConfig:
    notebook: str = "EXPERIMENT_NAME.marimo.py"
    headless: bool = True
    seed: int = 42


@experiment(config=EXPERIMENT_NAMEConfig, tags=["marimo", "exploration"])
def EXPERIMENT_NAME(cfg: EXPERIMENT_NAMEConfig) -> dict:
    """TODO: run the marimo notebook headlessly."""
    if cfg.headless:
        proc = subprocess.run(
            ["marimo", "run", cfg.notebook],
            capture_output=True,
            text=True,
            timeout=600,
        )
        return {"returncode": proc.returncode, "stdout_tail": proc.stdout[-500:]}
    return {"notebook": cfg.notebook, "note": "set headless=True to execute"}
