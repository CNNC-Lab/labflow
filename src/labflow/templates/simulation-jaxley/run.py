"""Jaxley compartmental simulation template."""

from __future__ import annotations

from dataclasses import dataclass

from labflow import experiment


@dataclass
class EXPERIMENT_NAMEConfig:
    n_compartments: int = 4
    simulation_time_ms: float = 100.0
    dt: float = 0.025
    seed: int = 42


@experiment(config=EXPERIMENT_NAMEConfig, tags=["jaxley", "compartmental"])
def EXPERIMENT_NAME(cfg: EXPERIMENT_NAMEConfig) -> dict:
    """TODO: describe this Jaxley simulation."""
    # import jaxley as jx  # install from https://github.com/mackelab/jaxley
    return {"n_compartments": cfg.n_compartments}
