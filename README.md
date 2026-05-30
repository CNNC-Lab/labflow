# labflow

[![CI](https://github.com/CNNC-Lab/labflow/actions/workflows/ci.yml/badge.svg)](https://github.com/CNNC-Lab/labflow/actions/workflows/ci.yml)
[![Docs](https://github.com/CNNC-Lab/labflow/actions/workflows/docs.yml/badge.svg)](https://cnnc-lab.github.io/labflow/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)

**One experiment = one Python file + one dataclass.** labflow turns that into
reproducible runs, parameter sweeps, and transparent SLURM submission — with a
provenance manifest written for every run, automatically.

No glue scripts, no name-coupled `parameters/` + `computations/` modules, no
hand-edited batch files. Write the science once; run it locally or on any SLURM
cluster with the same command.

```bash
pip install labflow

labflow new my_sim --template simulation-nest     # scaffold an experiment
labflow run my_sim threads=8 g=5.0                # run locally, tracked
labflow sweep my_sim g=4,5,6 seed=0,1,2           # cross-product sweep
labflow submit my_sim --system cluster-arm --nodes 4 --time 2:00:00   # → SLURM
labflow report outputs/my_sim/<run-id>/           # results + provenance
```

## Why labflow?

- **One file per experiment.** A `@experiment` function that takes a config dataclass and returns a dict. That's the whole contract.
- **Run anywhere, unchanged.** The same experiment runs in-process locally or as a SLURM job — only `--system` changes. Systems are described once in a small YAML registry; labflow renders the batch script from a Jinja2 template.
- **Provenance for free.** Every run writes `manifest.json`: git SHA, config, seed, system, hardware, wall time, results.
- **Backend-agnostic environments.** conda · uv · poetry · venv · pixi · apptainer — each experiment picks via a one-method resolver interface.
- **Sweeps + HPO.** Built-in cross-product sweeps; templates for Optuna and Ray Tune.
- **Lab-grade defaults.** Designed for scientific Python on HPC: NEST/NESTML, JAX + diffrax + optax, JAXley, SBI, Optuna, marimo.

Lightweight by default — the core depends only on `submitit`, `jinja2`, `pyyaml`,
`click`, `rich`, and `gitpython`. Hydra-based config composition is an optional
extra (`pip install labflow[hydra]`).

## Worked example: NEST scaling study

`examples/scaling/` runs **strong** and **weak** scaling of a Brunel balanced
random network in NEST, as labflow experiments — submit the sweep, collect the
manifests, and get speedup/efficiency curves. See
[the scaling example](https://cnnc-lab.github.io/labflow/examples/scaling/).

## Documentation

Full docs: **[cnnc-lab.github.io/labflow](https://cnnc-lab.github.io/labflow/)**

- [Install](https://cnnc-lab.github.io/labflow/getting-started/install/)
- [First experiment](https://cnnc-lab.github.io/labflow/getting-started/first-experiment/)
- [First SLURM submission](https://cnnc-lab.github.io/labflow/getting-started/first-slurm-submission/)
- [HPC systems registry](https://cnnc-lab.github.io/labflow/concepts/hpc-systems-registry/) — how to add your cluster

## Spiritual predecessor

A clean-slate redesign inspired by [NMSAT](https://github.com/rcfduarte/nmsat)
(Duarte, 2015+), which pioneered the "system registry + templated job scripts"
pattern for scientific Python on HPC. labflow modernizes it: YAML configs,
Submitit + SLURM, and an env-backend resolver interface.

## Citation

If labflow helps your research, please cite it — see [`CITATION.cff`](CITATION.cff).

## License

MIT — see [`LICENSE`](LICENSE).
