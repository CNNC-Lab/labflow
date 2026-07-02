"""SLURM launcher: render Jinja2 sbatch script + delegate to Submitit SlurmExecutor.

For `--dry-run`: render only, print script to stdout.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from labflow.registry import SystemSpec

DEFAULT_TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "slurm"


def render_sbatch(
    spec: SystemSpec,
    partition_key: str,
    job_name: str,
    account: str,
    walltime: str,
    nodes: int,
    ntasks_per_node: int,
    cpus_per_task: int,
    mem: str,
    output_dir: str,
    entry_point: str,
    container: str | None = None,
    template_name: str | None = None,
    template_dir: Path | None = None,
    extra: dict[str, Any] | None = None,
) -> str:
    """Render the SLURM batch script from the system's Jinja2 template."""
    template_dir = template_dir or DEFAULT_TEMPLATE_DIR
    template_name = (template_name or spec.template) + ".sbatch.j2"

    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(enabled_extensions=()),
        keep_trailing_newline=True,
    )
    tpl = env.get_template(template_name)

    partition = spec.partitions.get(partition_key, {}).get("name", partition_key)
    modules = list(spec.modules.get("mpi", []))
    modules += list(spec.modules.get("compiler", []))

    context = {
        "job_name": job_name,
        "account": account,
        "partition": partition,
        "walltime": walltime,
        "nodes": nodes,
        "ntasks_per_node": ntasks_per_node,
        "cpus_per_task": cpus_per_task,
        "mem": mem,
        "exclusive": spec.exclusive,
        "output_dir": output_dir,
        "project_scratch": spec.scratch or output_dir,
        "modules": modules,
        "eessi": spec.eessi_available,
        "eessi_init": spec.eessi_init or "",
        "entry_point": entry_point,
        "container": container,
    }
    if extra:
        context.update(extra)
    return tpl.render(**context)


class SlurmLauncher:
    def __init__(self, spec: SystemSpec, output_root: Path | None = None):
        self.spec = spec
        self.output_root = Path(output_root or Path.cwd() / "outputs")

    def render_only(self, **kwargs) -> str:
        """--dry-run: return the rendered sbatch script without submitting."""
        return render_sbatch(self.spec, **kwargs)

    def submit(self, func, config: dict[str, Any], **slurm_kwargs):
        """Submit via Submitit. See labflow.cli:cmd_submit for the CLI-level call."""
        import submitit

        executor = submitit.SlurmExecutor(folder=str(self.output_root / "submitit"))
        partition = self.spec.partitions.get(slurm_kwargs.get("partition_key", "normal"), {}).get(
            "name"
        )
        executor.update_parameters(
            partition=partition,
            time=slurm_kwargs.get("walltime", "1:00:00"),
            nodes=slurm_kwargs.get("nodes", 1),
            ntasks_per_node=slurm_kwargs.get("ntasks_per_node", 1),
            cpus_per_task=slurm_kwargs.get("cpus_per_task", 1),
            mem=slurm_kwargs.get("mem", "4G"),
            account=slurm_kwargs.get("account", ""),
        )
        job = executor.submit(func, config)
        return {"job_id": job.job_id, "submitit_job": job}
