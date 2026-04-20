# labflow

**Opinionated scientific workflow manager** — thin glue over Hydra + Submitit + (optional) Snakemake for reproducible experiments and transparent SLURM submission on heterogeneous HPC clusters.

## What it solves

1. **NMSAT duplication pain.** One experiment = one Python file + dataclass config. No more `parameters/name.py` + `computations/name.py` coupled by string matching.
2. **Transparent HPC submission.** `labflow submit ou_stationary --system deucalion-arm --nodes 4` renders the right Jinja2 template, respects Deucalion-specific rules (GPU billing, `/projects/` scratch, ed25519 SSH, `OMP_PROC_BIND=TRUE`), and submits.
3. **Env backend freedom.** Conda, uv, poetry, venv, pixi, apptainer — each project can pick what fits. Backends implement a single resolver interface.
4. **Provenance by default.** Every run writes a manifest.json with git SHA, env hash, seed, hardware, wall time, container hash.

## For whom

Computational-science labs running scientific Python on local workstations + HPC clusters, especially where experiments need sweeps, provenance, and portable submission.

## Stack it's built for

- **Simulation**: NEST/NESTML, Arbor, Brian2, JAX + diffrax + optax, JAXley, NEURON, bmtk
- **Inference/HPO**: SBI + BayesFlow, Optuna, Ray Tune, Ax
- **Analysis**: numpy/scipy/pandas/sklearn, marimo notebooks
- **HPC**: SLURM via Submitit; Apptainer/Singularity containers; Deucalion-first

## Next steps

- [Install →](getting-started/install.md)
- [First experiment →](getting-started/first-experiment.md)
