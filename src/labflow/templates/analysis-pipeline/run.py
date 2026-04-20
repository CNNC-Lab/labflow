"""Data-analysis pipeline template.

Ingest → preprocess → analyze → report. Pure-Python; no HPC required.
Pair with Snakemake for multi-step DAG pipelines.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from labflow import experiment


@dataclass
class EXPERIMENT_NAMEConfig:
    input_path: str = "data/raw/"
    output_path: str = "data/processed/"
    seed: int = 42


@experiment(config=EXPERIMENT_NAMEConfig, tags=["analysis", "pipeline"])
def EXPERIMENT_NAME(cfg: EXPERIMENT_NAMEConfig) -> dict:
    """TODO: describe this analysis pipeline."""
    in_dir = Path(cfg.input_path)
    out_dir = Path(cfg.output_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    files = sorted(in_dir.glob("*.csv")) if in_dir.exists() else []
    return {"n_input_files": len(files), "output_path": str(out_dir)}
