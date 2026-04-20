"""Ray Tune HPO experiment template."""

from __future__ import annotations

from dataclasses import dataclass

from labflow import experiment


@dataclass
class EXPERIMENT_NAMEConfig:
    num_samples: int = 20
    resources_per_trial: dict = None
    seed: int = 42


@experiment(config=EXPERIMENT_NAMEConfig, tags=["hpo", "ray-tune"])
def EXPERIMENT_NAME(cfg: EXPERIMENT_NAMEConfig) -> dict:
    """TODO: describe this Ray Tune study."""
    # from ray import tune
    return {"num_samples": cfg.num_samples}
