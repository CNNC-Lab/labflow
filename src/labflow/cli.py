"""labflow command-line interface."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.table import Table

from labflow import __version__
from labflow.launchers import get_launcher
from labflow.launchers.slurm import render_sbatch
from labflow.registry import ExperimentRegistry, SystemRegistry

console = Console()
TEMPLATES_ROOT = Path(__file__).parent / "templates"


def _load_project_config(project_root: Path) -> dict:
    p = project_root / ".labflow.yaml"
    if p.exists():
        return yaml.safe_load(p.read_text()) or {}
    return {}


def _discover_experiments(experiments_dir: Path) -> None:
    """Import every .py in experiments/ so @experiment decorators fire."""
    if not experiments_dir.exists():
        return
    for py in experiments_dir.rglob("*.py"):
        if py.name.startswith("_"):
            continue
        spec = importlib.util.spec_from_file_location(py.stem, py)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[py.stem] = mod
            try:
                spec.loader.exec_module(mod)
            except Exception as e:
                console.print(f"[yellow]Warning: failed to import {py}: {e}[/yellow]")


@click.group()
@click.version_option(__version__)
def main():
    """labflow — opinionated scientific workflow manager."""


@main.command()
@click.argument("name")
@click.option("--template", default="simulation-jax", help="Experiment template name")
@click.option("--project-root", type=click.Path(path_type=Path), default=Path.cwd())
def new(name: str, template: str, project_root: Path):
    """Scaffold a new experiment from a template."""
    src = TEMPLATES_ROOT / template
    if not src.exists():
        console.print(f"[red]Template {template!r} not found in {TEMPLATES_ROOT}[/red]")
        available = [p.name for p in TEMPLATES_ROOT.iterdir() if p.is_dir()]
        console.print(f"Available: {', '.join(available)}")
        sys.exit(1)

    experiments_dir = project_root / "experiments"
    experiments_dir.mkdir(parents=True, exist_ok=True)

    dst = experiments_dir / f"{name}.py"
    if dst.exists():
        console.print(f"[red]{dst} already exists — refusing to overwrite[/red]")
        sys.exit(1)

    src_file = src / "run.py"
    if src_file.exists():
        content = src_file.read_text().replace("EXPERIMENT_NAME", name)
        dst.write_text(content)
    else:
        # Fallback: minimal template
        dst.write_text(
            f'"""Experiment: {name}."""\n\n'
            "from dataclasses import dataclass\n\n"
            "from labflow import experiment\n\n\n"
            "@dataclass\n"
            f"class {name.title().replace('_', '')}Config:\n"
            "    x: float = 1.0\n"
            "    seed: int = 42\n\n\n"
            f"@experiment(config={name.title().replace('_', '')}Config)\n"
            f"def {name}(cfg) -> dict:\n"
            '    """TODO: describe this experiment."""\n'
            '    return {"x": cfg.x}\n'
        )

    console.print(f"[green]Created {dst}[/green]")


@main.command()
@click.argument("experiment_name")
@click.argument("overrides", nargs=-1)
@click.option("--project-root", type=click.Path(path_type=Path), default=Path.cwd())
@click.option("--system", default="local-workstation")
def run(experiment_name: str, overrides: tuple[str], project_root: Path, system: str):
    """Run an experiment locally (or via configured system) with optional Hydra overrides (key=value)."""
    _discover_experiments(project_root / "experiments")
    if experiment_name not in ExperimentRegistry.list():
        console.print(f"[red]Experiment {experiment_name!r} not found[/red]")
        console.print(f"Registered: {ExperimentRegistry.list()}")
        sys.exit(1)

    meta = ExperimentRegistry.get(experiment_name)
    # Apply overrides naively (k=v parsing) — Hydra integration deferred to v0.2
    cfg = meta.config_cls()
    for ov in overrides:
        if "=" in ov:
            k, v = ov.split("=", 1)
            if hasattr(cfg, k):
                cur = getattr(cfg, k)
                try:
                    v_cast = type(cur)(v)
                except Exception:
                    v_cast = v
                setattr(cfg, k, v_cast)

    reg = SystemRegistry.from_path()
    spec = reg.get(system)
    launcher = get_launcher(spec, output_root=project_root / "outputs")
    result = launcher.run(meta.func, vars(cfg))
    console.print(f"[green]Run complete.[/green] Output: {result['run_dir']}")
    if result.get("returned"):
        console.print(f"Returned: {result['returned']}")


@main.command()
@click.argument("experiment_name")
@click.argument("sweep_spec", nargs=-1)
def sweep(experiment_name: str, sweep_spec: tuple[str]):
    """Sweep parameters (e.g., tau=5,10,20 seed=0,1,2). v0.1 runs locally serially; Hydra multirun in v0.2."""
    console.print(f"[yellow]Sweep for {experiment_name}[/yellow]")
    console.print(f"Params: {sweep_spec}")
    # v0.1 minimal: just expand the product and call run()
    # (Full Hydra multirun integration is a v0.2 enhancement.)
    console.print("[yellow]v0.1: local serial sweep not yet wired. Coming in v0.2.[/yellow]")


@main.command()
@click.argument("experiment_name")
@click.option("--system", required=True)
@click.option("--partition", default="normal")
@click.option("--account", required=False, default="", envvar="SLURM_ACCOUNT")
@click.option("--nodes", type=int, default=1)
@click.option("--time", "walltime", default="1:00:00")
@click.option("--mem", default="16G")
@click.option("--dry-run", is_flag=True)
@click.option("--project-root", type=click.Path(path_type=Path), default=Path.cwd())
def submit(
    experiment_name: str,
    system: str,
    partition: str,
    account: str,
    nodes: int,
    walltime: str,
    mem: str,
    dry_run: bool,
    project_root: Path,
):
    """Submit an experiment to a SLURM system."""
    reg = SystemRegistry.from_path()
    spec = reg.get(system)
    if spec.queueing_system != "slurm":
        console.print(f"[red]System {system!r} is not a SLURM system[/red]")
        sys.exit(1)

    ntasks_per_node = spec.node.get("cores", 1)
    cpus_per_task = 1
    gpus = spec.node.get("gpus", 0)
    if gpus and spec.cpus_per_gpu:
        cpus_per_task = spec.cpus_per_gpu
        ntasks_per_node = gpus

    run_dir = f"{spec.scratch or '/tmp'}/outputs/{experiment_name}"
    entry_point = f"python -m labflow.cli run {experiment_name} --system {system}"

    rendered = render_sbatch(
        spec,
        partition_key=partition,
        job_name=f"labflow-{experiment_name}",
        account=account,
        walltime=walltime,
        nodes=nodes,
        ntasks_per_node=ntasks_per_node,
        cpus_per_task=cpus_per_task,
        mem=mem,
        output_dir=run_dir,
        entry_point=entry_point,
    )

    if dry_run:
        console.print("[bold]Rendered SLURM script:[/bold]")
        console.print(rendered)
        return

    # Actual submission — write to temp file, sbatch, return job id
    import subprocess
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".sbatch", delete=False) as f:
        f.write(rendered)
        sbatch_path = f.name
    # If system has an ssh_alias, run sbatch remotely
    if spec.ssh_alias:
        proc = subprocess.run(
            ["ssh", spec.ssh_alias, "sbatch", "-"],
            input=rendered,
            capture_output=True,
            text=True,
        )
    else:
        proc = subprocess.run(["sbatch", sbatch_path], capture_output=True, text=True)

    if proc.returncode == 0:
        console.print(f"[green]{proc.stdout.strip()}[/green]")
    else:
        console.print(f"[red]sbatch failed:\n{proc.stderr}[/red]")
        sys.exit(proc.returncode)


@main.command()
@click.option("--system", default=None)
def status(system: str | None):
    """Show queue status on the configured system."""
    reg = SystemRegistry.from_path()
    if system:
        systems = [reg.get(system)]
    else:
        systems = [reg.get(s) for s in reg.list() if reg.get(s).queueing_system == "slurm"]

    for spec in systems:
        if spec.ssh_alias:
            import subprocess

            r = subprocess.run(
                ["ssh", spec.ssh_alias, "squeue", "--me"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            console.print(f"[bold]{spec.name}:[/bold]")
            console.print(r.stdout or "(empty)")


@main.command()
@click.argument("run_path")
def report(run_path: str):
    """Print a brief summary of a run (manifest + returned)."""
    p = Path(run_path)
    manifest_path = p / "manifest.json" if p.is_dir() else p
    if not manifest_path.exists():
        console.print(f"[red]No manifest at {manifest_path}[/red]")
        sys.exit(1)
    m = json.loads(manifest_path.read_text())
    t = Table(title=f"Run: {m.get('run_id', 'unknown')}")
    t.add_column("Key")
    t.add_column("Value")
    for k in ("experiment", "system", "git_commit", "seed", "timestamp_utc"):
        t.add_row(k, str(m.get(k, "")))
    console.print(t)
    if m.get("returned"):
        console.print(f"Returned: {m['returned']}")


@main.command()
@click.argument("run_path")
def manifest(run_path: str):
    """Print the full manifest JSON."""
    p = Path(run_path)
    manifest_path = p / "manifest.json" if p.is_dir() else p
    console.print(manifest_path.read_text())


if __name__ == "__main__":
    main()
