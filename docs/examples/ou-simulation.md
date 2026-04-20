# Example: OU stationary

Verify the Ornstein-Uhlenbeck stationary distribution ~ N(0, σ²/2λ) analytically and empirically.

```python
# experiments/ou_stationary.py
from dataclasses import dataclass
import jax
import jax.numpy as jnp
from labflow import experiment


@dataclass
class OuConfig:
    tau: float = 10.0
    sigma: float = 1.0
    T: float = 1000.0
    dt: float = 0.01
    seed: int = 42


@experiment(config=OuConfig, tags=["ou", "validation"])
def ou_stationary(cfg):
    """Verify OU stationary ~ N(0, σ²/(2/τ))."""
    n_steps = int(cfg.T / cfg.dt)
    key = jax.random.PRNGKey(cfg.seed)

    def step(x, key_t):
        drift = -x / cfg.tau
        diffusion = cfg.sigma * jnp.sqrt(cfg.dt) * jax.random.normal(key_t)
        return x + drift * cfg.dt + diffusion, x

    keys = jax.random.split(key, n_steps)
    _, trajectory = jax.lax.scan(step, 0.0, keys)

    burn_in = n_steps // 10
    empirical_var = float(jnp.var(trajectory[burn_in:]))
    theoretical_var = cfg.sigma ** 2 / (2 / cfg.tau)

    return {
        "empirical_var": empirical_var,
        "theoretical_var": theoretical_var,
        "relative_error": abs(empirical_var - theoretical_var) / theoretical_var,
    }
```

Run:

```bash
labflow run ou_stationary tau=5 sigma=1 T=10000
```
