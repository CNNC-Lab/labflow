# Configs and overrides

## Writing configs

Use a Python `@dataclass`. Fields become both typed config and Hydra-compatible YAML.

## CLI overrides

```bash
labflow run exp_name tau=5 sigma=2
```

Each `key=value` pair overrides the default. Values cast to the dataclass field's type.

## Hydra integration (v0.2)

In v0.2 we wire Hydra directly: `--multirun tau=5,10,20` → SLURM array job or local parallel via Submitit.
