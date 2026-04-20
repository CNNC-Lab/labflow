# Your first labflow experiment

## Scaffold

```bash
cd your-project-repo/
labflow new ou_stationary --template simulation-jax
```

This creates `experiments/ou_stationary.py` with a minimal JAX scaffold.

## Inspect

```python
# experiments/ou_stationary.py
from dataclasses import dataclass
from labflow import experiment

@dataclass
class OuStationaryConfig:
    tau: float = 10.0
    sigma: float = 1.0
    T: float = 1000.0
    dt: float = 0.01
    seed: int = 42

@experiment(config=OuStationaryConfig, tags=["jax", "simulation"])
def ou_stationary(cfg):
    """Verify OU stationary ~ N(0, σ²/2λ)."""
    import jax
    import jax.numpy as jnp
    key = jax.random.PRNGKey(cfg.seed)
    # ... your simulation
    return {"theoretical_var": cfg.sigma**2 / (2 / cfg.tau)}
```

## Run

```bash
labflow run ou_stationary
```

Output:

```
Run complete. Output: outputs/ou_stationary/2026-04-22-14-30-00-abc123/
Returned: {'theoretical_var': 50.0}
```

## Inspect the manifest

```bash
labflow manifest outputs/ou_stationary/2026-04-22-14-30-00-abc123/
```

## Override parameters

```bash
labflow run ou_stationary tau=5 sigma=2
```
