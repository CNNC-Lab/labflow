"""In-process CliRunner tests for labflow CLI (boost coverage of cli.py)."""

from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from labflow.cli import main
from labflow.registry import ExperimentRegistry


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "labflow" in result.output.lower()


def test_cli_new_creates_file(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["new", "my_exp", "--template", "analysis-pipeline", "--project-root", str(tmp_path)],
    )
    assert result.exit_code == 0, result.output
    assert (tmp_path / "experiments" / "my_exp.py").exists()
    content = (tmp_path / "experiments" / "my_exp.py").read_text()
    assert "my_exp" in content


def test_cli_new_rejects_unknown_template(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["new", "foo", "--template", "does-not-exist", "--project-root", str(tmp_path)],
    )
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_cli_new_refuses_overwrite(tmp_path: Path):
    runner = CliRunner()
    # First creation
    r1 = runner.invoke(
        main,
        ["new", "dupe", "--template", "analysis-pipeline", "--project-root", str(tmp_path)],
    )
    assert r1.exit_code == 0, r1.output
    # Second should refuse
    r2 = runner.invoke(
        main,
        ["new", "dupe", "--template", "analysis-pipeline", "--project-root", str(tmp_path)],
    )
    assert r2.exit_code == 1
    assert "already exists" in r2.output.lower()


def test_cli_run_missing_experiment(tmp_path: Path):
    """labflow run with no experiments/ dir → experiment not found."""
    # Clear registry so stale test-registered experiments don't pollute this
    ExperimentRegistry.clear()
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["run", "no_such_experiment", "--project-root", str(tmp_path)],
    )
    assert result.exit_code == 1
    assert "not found" in result.output.lower()


def test_cli_report_missing_manifest(tmp_path: Path):
    runner = CliRunner()
    result = runner.invoke(main, ["report", str(tmp_path)])
    assert result.exit_code == 1
    assert "no manifest" in result.output.lower()


def test_cli_manifest_prints_file(tmp_path: Path):
    (tmp_path / "manifest.json").write_text('{"experiment": "x", "run_id": "r1"}')
    runner = CliRunner()
    result = runner.invoke(main, ["manifest", str(tmp_path)])
    assert result.exit_code == 0
    assert "experiment" in result.output


def test_cli_sweep_unknown_experiment(tmp_path):
    # sweep now discovers experiments and errors clearly on an unknown name
    # (the cross-product run path is shared with `run` via `_run_one`).
    runner = CliRunner()
    result = runner.invoke(main, ["sweep", "nope", "tau=5,10", "--project-root", str(tmp_path)])
    assert result.exit_code == 1
    assert "not found" in result.output.lower()
