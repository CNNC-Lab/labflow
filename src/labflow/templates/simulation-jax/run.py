"""JAX simulation experiment template.

Defines a minimal JAX simulation with PRNG key discipline, JIT compilation,
and optional diffrax integration. Replace the body with your actual science.
"""

from __future__ import annotations

from dataclasses import dataclass

import jax
import jax.numpy as jnp

from labflow import experiment


@dataclass
class EXPERIMENT_NAMEConfig:
    """Parameters for the EXPERIMENT_NAME experiment."""
    tau: float = 10.0
    sigma: float = 1.0
    T: float = 1000.0
    dt: float = 0.01
    seed: int = 42


@experiment(config=EXPERIMENT_NAMEConfig, tags=["jax", "simulation"])
def EXPERIMENT_NAME(cfg: EXPERIMENT_NAMEConfig) -> dict:
    """TODO: describe this experiment.

    Theory: reference the governing equation(s) here (e.g. Eq. 2.15 of paper X).
    """
    key = jax.random.PRNGKey(cfg.seed)
    n_steps = int(cfg.T / cfg.dt)
    # Example: OU process
    key, subkey = jax.random.split(key)
    noise = jax.random.normal(subkey, shape=(n_steps,))
    x = jnp.zeros(n_steps)
    # TODO: replace with your simulation
    return {
        "empirical_var": float(jnp.var(noise)),
        "theoretical_var": cfg.sigma ** 2 / (2 / cfg.tau),
        "n_steps": n_steps,
    }
