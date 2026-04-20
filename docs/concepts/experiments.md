# Experiments

A labflow experiment is:

1. A `@dataclass` config (the "parameters" — single source of truth)
2. A function decorated with `@experiment(config=...)` (the "computation")

Both live in ONE file. No name-coupling. Config fields include a `seed: int` — required for reproducibility.

## Minimal example

```python
from dataclasses import dataclass
from labflow import experiment

@dataclass
class HelloConfig:
    name: str = "world"
    seed: int = 42

@experiment(config=HelloConfig, tags=["hello"])
def hello(cfg):
    return {"greeting": f"Hello, {cfg.name}!"}
```

## Registry

All `@experiment`-decorated functions are discovered on first `labflow` invocation via recursive import of `experiments/*.py`. See `labflow.registry.ExperimentRegistry`.
