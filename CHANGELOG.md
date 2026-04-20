# Changelog

All notable changes to `labflow` are documented here. Format adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] — 2026-04-20

### Added
- Initial release.
- `@experiment` decorator with dataclass config + tag registry.
- Env resolver interface: conda, uv, poetry, venv, pixi, apptainer.
- SystemRegistry reading `~/.claude/contexts/hpc-systems.yaml`.
- Local launcher (Submitit local executor) + SLURM launcher (Submitit + Jinja2 templates).
- CLI: `new`, `run`, `sweep`, `submit`, `status`, `report`, `manifest`.
- 8 experiment templates: simulation-{nest, jax, jaxley}, analysis-pipeline, hpo-{optuna, ray}, sbi-inference, marimo-exploration.
- Provenance manifest writer.
- Optional Snakemake integration hook.
- MkDocs-Material documentation.
- CI (GitHub Actions: ruff + pytest + coverage) + docs deployment.
