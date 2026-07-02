# Migrating from NMSAT

NMSAT (Duarte, 2015+) pioneered the "system registry + templated job scripts" pattern in computational neuroscience. labflow retains the DNA and modernizes the stack.

## Conceptual mapping

| NMSAT concept | labflow equivalent |
|---|---|
| `defaults/paths.py` (Python dict) | `~/.claude/contexts/hpc-systems.yaml` |
| `defaults/cluster_templates/*_jdf.sh` | `labflow`'s bundled `src/labflow/templates/slurm/*.sbatch.j2` |
| `projects/<p>/parameters/<name>.py` | part of `experiments/<name>.py` (dataclass) |
| `projects/<p>/computations/<name>.py` | part of `experiments/<name>.py` (function) |
| `main.py run_experiment(...)` | `labflow run <name>` |
| NMSAT's custom `process_template` | Jinja2 native |
| Generated `submit_jobs.py` per sweep | Submitit + SLURM array jobs |

## Step-by-step migration

1. **Extract one experiment.** Pick one from `projects/<p>/computations/<name>.py`.
2. **Fuse config + code.** Copy the parameter dict from `parameters/<name>.py` into a `@dataclass` at the top of a new `experiments/<name>.py`. Copy the computation function body below it, re-implemented to take a dataclass instance.
3. **Decorate.** Add `@experiment(config=YourConfig, tags=[...])`.
4. **Scaffold if needed.** `labflow new <name> --template simulation-nest` gives you a working NEST scaffold you can fill.
5. **Register systems.** Copy relevant entries from `paths.py` into `hpc-systems.yaml`, converting cluster-specific details (partition names, modules).
6. **Translate the SLURM template.** NMSAT's `{{ placeholder }}` → Jinja2 `{{ placeholder }}` (mostly identical). Lift verbatim; add Jinja2 conditionals for ARM vs. x86 vs. GPU specifics.
7. **Submit.** `labflow submit <name> --system <s>`.

## What's gained

- **No duplication.** One file per experiment.
- **Python 3.12, not 2.7.** Modern type hints, dataclasses, PRNG APIs.
- **Apptainer containers by default on HPC.** No more "my MPI doesn't match your MPI".
- **Provenance manifest per run.** NMSAT relied on filename conventions.
- **Real Jinja2.** No custom substitutor.
- **SLURM array jobs.** One sbatch per sweep, N tasks — far cheaper than NMSAT's N individual sbatch files.

## What's different

- Python 2 → Python 3.11+. Existing NMSAT code needs 2to3 + manual adjustment.
- PyNEST API has evolved (seed handling, `local_num_threads`).
- labflow does not attempt to be a replacement for NMSAT's `input_architect`, `net_architect`, or `signals` modules. These domain-specific libraries are separate projects.
