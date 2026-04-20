"""Simulation-based inference template (sbi-python)."""

from __future__ import annotations

from dataclasses import dataclass

from labflow import experiment


@dataclass
class EXPERIMENT_NAMEConfig:
    n_simulations: int = 1000
    method: str = "SNPE"  # SNPE | SNLE | SNRE
    seed: int = 42


@experiment(config=EXPERIMENT_NAMEConfig, tags=["sbi", "inference"])
def EXPERIMENT_NAME(cfg: EXPERIMENT_NAMEConfig) -> dict:
    """TODO: describe this SBI experiment."""
    # from sbi.inference import SNPE, SNLE, SNRE
    return {"method": cfg.method, "n_simulations": cfg.n_simulations}
