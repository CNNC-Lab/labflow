"""Launchers for labflow: local (Submitit local executor) + SLURM (Submitit SLURM executor + Jinja2)."""

from labflow.launchers.local import LocalLauncher
from labflow.launchers.slurm import SlurmLauncher
from labflow.registry import SystemSpec


def get_launcher(spec: SystemSpec, **kwargs):
    """Dispatch on SystemSpec.queueing_system."""
    if spec.queueing_system is None:
        return LocalLauncher(spec, **kwargs)
    if spec.queueing_system == "slurm":
        return SlurmLauncher(spec, **kwargs)
    raise ValueError(f"Unsupported queueing system: {spec.queueing_system}")


__all__ = ["LocalLauncher", "SlurmLauncher", "get_launcher"]
