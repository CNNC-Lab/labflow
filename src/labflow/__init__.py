"""labflow — opinionated scientific workflow manager.

Thin glue over Hydra + Submitit + (optional) Snakemake.
Solves the NMSAT parameters/computations duplication pain:
one experiment = one Python file (optionally + YAML) with a dataclass config.

Public API:
    - experiment: decorator to register an experiment function
    - sweep: helper for Hydra multirun declarations
    - SystemRegistry: loads ~/.claude/contexts/hpc-systems.yaml
    - ExperimentRegistry: auto-discovers @experiment-decorated functions

CLI:
    - labflow new <name> [--template T]
    - labflow run <experiment> [hydra overrides]
    - labflow sweep <experiment> <params>
    - labflow submit <experiment> --system <S> [--nodes N] [--time T]
    - labflow status [--system S]
    - labflow report <run-id>
    - labflow manifest <run-id>
"""

from labflow.context import current_output_dir
from labflow.registry import ExperimentRegistry, SystemRegistry, experiment, sweep

__version__ = "0.1.0"
__all__ = [
    "ExperimentRegistry",
    "SystemRegistry",
    "__version__",
    "current_output_dir",
    "experiment",
    "sweep",
]
