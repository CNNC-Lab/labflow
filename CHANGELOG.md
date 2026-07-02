# Changelog

All notable changes to `labflow` are documented here. Format adheres to [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Fixed
- SLURM sbatch Jinja2 templates (`cpu-mpi`, `cpu-openmp`, `gpu-single`, `gpu-multi`, `optuna-array`, `base`) are now bundled with the package at `src/labflow/templates/slurm/`, instead of being read from `~/.claude/contexts/hpc-templates/slurm` on the invoking user's home directory. The old default silently required every collaborator to have a personal copy of one maintainer's dotfiles, producing `TemplateNotFound` for anyone else on a shared cluster account. `render_sbatch(..., template_dir=...)` still accepts an explicit override for local customization.

## [0.2.0] — 2026-05-30

### Fixed
- `labflow run` now passes the **dataclass config instance** to experiments (was `vars(cfg)`, a dict), matching the `@experiment` contract and the `new` scaffold. Fixes `AttributeError: 'dict' object has no attribute …` on any experiment using attribute access.

### Changed
- **Slimmer default install.** `hydra-core` / `omegaconf` / `hydra-submitit-launcher` moved to an optional `[hydra]` extra (not yet used in core; deferred to a future config-composition feature). This removes an `antlr4-python3-runtime` version pin that conflicted with NEST/NESTML, so labflow can now be installed alongside NEST/NESTML in a single environment. Core deps: `submitit`, `jinja2`, `pyyaml`, `click`, `rich`, `gitpython`.
- Documentation generalized to any SLURM cluster (ARM / x86 / GPU example system pages).

### Added
- `examples/scaling/` — strong and weak scaling study of a Brunel balanced random network in NEST, end-to-end as labflow experiments, with a scaling analysis.
- `labflow sweep` implemented — runs a cross-product of parameter values as individual tracked runs (was a placeholder).
- `balanced_random_network` worked example.

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
