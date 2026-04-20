# labflow

[![CI](https://github.com/CNNC-Lab/labflow/actions/workflows/ci.yml/badge.svg)](https://github.com/CNNC-Lab/labflow/actions/workflows/ci.yml)
[![Docs](https://github.com/CNNC-Lab/labflow/actions/workflows/docs.yml/badge.svg)](https://cnnc-lab.github.io/labflow/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Opinionated scientific workflow manager** — thin glue over Hydra + Submitit + (optional) Snakemake for reproducible experiments and transparent SLURM submission.

Solves the NMSAT `parameters/computations` name-coupling pain: one experiment = one Python file + dataclass config. Parameter sweeps, SLURM submission, and provenance manifests are first-class.

## Quickstart

```bash
pip install -e 'git+https://github.com/CNNC-Lab/labflow.git#egg=labflow[dev]'

# in any project repo
labflow new ou_stationary --template simulation-jax
labflow run ou_stationary tau=5 sigma=2
labflow sweep ou_stationary tau=5,10,20 seed=0,1,2,3
labflow submit ou_stationary --system deucalion-arm --nodes 4 --time 2:00:00
labflow status
labflow report outputs/ou_stationary/<run-id>/
```

## Why labflow?

- **One file per experiment.** A dataclass config and a function — that's it.
- **Transparent SLURM.** Submit with `--system deucalion-arm --nodes 4` and labflow renders the Jinja2 template from the shared HPC system registry.
- **Backend-agnostic env management.** Conda, uv, poetry, venv, pixi, apptainer — each experiment can pick.
- **Provenance manifest per run.** Git SHA, env hash, seed, hardware, wall time — auto-written.
- **Lab-first.** Built for computational neuroscience workflows: NEST, JAX/diffrax/optax, JAXley, SBI, Optuna, marimo.

## Documentation

Full docs at [cnnc-lab.github.io/labflow](https://cnnc-lab.github.io/labflow/). Start with:

- [Install](https://cnnc-lab.github.io/labflow/getting-started/install/)
- [First experiment](https://cnnc-lab.github.io/labflow/getting-started/first-experiment/)
- [First SLURM submission](https://cnnc-lab.github.io/labflow/getting-started/first-slurm-submission/)
- [Migrating from NMSAT](https://cnnc-lab.github.io/labflow/guides/migrating-from-nmsat/)

## Spiritual predecessor

labflow is a clean-slate redesign inspired by [NMSAT](https://github.com/rcfduarte/nmsat) (Duarte, 2015+). NMSAT pioneered the "system registry + templated job scripts" pattern for scientific Python on HPC clusters; labflow modernizes it with YAML configs, Hydra composition, Submitit + SLURM native, and an env-backend resolver interface.

## Contributing

See [CONTRIBUTING.md](https://cnnc-lab.github.io/labflow/contributing/development/).

## Citation

If you use labflow in your research, please cite (see [`CITATION.cff`](CITATION.cff)).

## License

MIT — see [`LICENSE`](LICENSE).
