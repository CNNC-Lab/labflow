"""Tests for local and SLURM launchers."""

from __future__ import annotations

from pathlib import Path

from labflow.launchers import get_launcher
from labflow.launchers.local import LocalLauncher
from labflow.registry import SystemSpec


def test_get_local_launcher():
    spec = SystemSpec(name="local", queueing_system=None, arch="x86_64", node={}, env={})
    launcher = get_launcher(spec)
    assert isinstance(launcher, LocalLauncher)


def test_local_launcher_runs_callable(tmp_path: Path):
    spec = SystemSpec(name="local", queueing_system=None, arch="x86_64", node={}, env={})
    launcher = LocalLauncher(spec, output_root=tmp_path)

    def my_func(cfg: dict) -> dict:
        return {"doubled": cfg["x"] * 2}

    result = launcher.run(my_func, {"x": 5})
    assert result["returned"] == {"doubled": 10}
    assert Path(result["run_dir"]).exists()
    assert (Path(result["run_dir"]) / "manifest.json").exists()


def test_slurm_render_template(tmp_path: Path):
    from labflow.launchers.slurm import render_sbatch

    (tmp_path / "cpu-mpi.sbatch.j2").write_text(
        """#!/bin/bash
#SBATCH --job-name={{ job_name }}
#SBATCH --partition={{ partition }}
#SBATCH --nodes={{ nodes }}
{% for m in modules %}module load {{ m }}
{% endfor %}
{{ entry_point }}
"""
    )

    spec = SystemSpec(
        name="cluster-arm",
        queueing_system="slurm",
        arch="aarch64",
        node={"cores": 48, "memory_gb": 32, "gpus": 0},
        env={"backend": "apptainer"},
        partitions={"normal": {"name": "normal-arm", "max_nodes": 128, "time_limit_h": 48}},
        modules={"mpi": ["OpenMPI/5.0.3-GCC-13.3.0"]},
        eessi_available=True,
        scratch="/projects/xyz",
        template="cpu-mpi",
        exclusive=True,
    )
    rendered = render_sbatch(
        spec,
        partition_key="normal",
        job_name="test",
        account="acc",
        walltime="1:00:00",
        nodes=2,
        ntasks_per_node=48,
        cpus_per_task=1,
        mem="32G",
        output_dir="/projects/xyz/outputs/test",
        entry_point="python run.py",
        template_dir=tmp_path,
    )
    assert "#SBATCH" in rendered
    assert "normal-arm" in rendered
    assert "OpenMPI" in rendered


def test_default_template_dir_is_bundled_with_package():
    """Templates ship inside the installed package, not a user's home dotfiles.

    Regression test for TemplateNotFound on any account other than the one that
    happened to have ~/.claude/contexts/hpc-templates/slurm populated.
    """
    import labflow
    from labflow.launchers.slurm import DEFAULT_TEMPLATE_DIR

    assert Path(labflow.__file__).parent / "templates" / "slurm" == DEFAULT_TEMPLATE_DIR
    assert ".claude" not in str(DEFAULT_TEMPLATE_DIR)
    assert (DEFAULT_TEMPLATE_DIR / "cpu-mpi.sbatch.j2").exists()


def test_slurm_render_template_uses_bundled_default():
    """render_sbatch works out of the box with no template_dir override."""
    from labflow.launchers.slurm import render_sbatch

    spec = SystemSpec(
        name="deucalion-arm",
        queueing_system="slurm",
        arch="aarch64",
        node={"cores": 48, "memory_gb": 32, "gpus": 0},
        env={"backend": "apptainer"},
        partitions={"normal": {"name": "normal-arm", "max_nodes": 128, "time_limit_h": 48}},
        modules={"mpi": ["OpenMPI/5.0.3-GCC-13.3.0"]},
        eessi_available=True,
        scratch="/projects/xyz",
        template="cpu-mpi",
        exclusive=True,
    )
    rendered = render_sbatch(
        spec,
        partition_key="normal",
        job_name="test",
        account="acc",
        walltime="1:00:00",
        nodes=2,
        ntasks_per_node=48,
        cpus_per_task=1,
        mem="32G",
        output_dir="/projects/xyz/outputs/test",
        entry_point="run.py",
    )
    assert "#SBATCH --job-name=test" in rendered
    assert "normal-arm" in rendered
    assert "srun --hint=nomultithread python run.py" in rendered
