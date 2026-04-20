"""Optuna HPO experiment template."""

from __future__ import annotations

from dataclasses import dataclass

from labflow import experiment


@dataclass
class EXPERIMENT_NAMEConfig:
    n_trials: int = 50
    study_name: str = "EXPERIMENT_NAME"
    storage: str | None = None  # sqlite:///study.db for distributed
    seed: int = 42


@experiment(config=EXPERIMENT_NAMEConfig, tags=["hpo", "optuna"])
def EXPERIMENT_NAME(cfg: EXPERIMENT_NAMEConfig) -> dict:
    """TODO: describe this Optuna study."""
    import optuna

    def objective(trial):
        x = trial.suggest_float("x", -10, 10)
        y = trial.suggest_float("y", -10, 10)
        return (x - 2) ** 2 + (y + 3) ** 2

    study = optuna.create_study(direction="minimize", study_name=cfg.study_name, storage=cfg.storage)
    study.optimize(objective, n_trials=cfg.n_trials)
    return {
        "best_value": study.best_value,
        "best_params": study.best_params,
        "n_trials": len(study.trials),
    }
