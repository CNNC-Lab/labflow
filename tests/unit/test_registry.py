"""Tests for experiment registry + system registry."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

from labflow.registry import ExperimentRegistry, SystemRegistry, experiment


def test_experiment_decorator_registers_function():
    @dataclass
    class Cfg:
        x: float = 1.0

    @experiment(config=Cfg, tags=["test"])
    def my_exp(cfg: Cfg) -> dict:
        return {"x": cfg.x}

    assert "my_exp" in ExperimentRegistry.list()
    meta = ExperimentRegistry.get("my_exp")
    assert meta.config_cls is Cfg
    assert "test" in meta.tags


def test_experiment_decorator_preserves_callable():
    @dataclass
    class Cfg:
        x: float = 2.0

    @experiment(config=Cfg)
    def other_exp(cfg: Cfg) -> dict:
        return {"doubled": cfg.x * 2}

    result = other_exp(Cfg(x=5.0))
    assert result == {"doubled": 10.0}


def test_system_registry_loads_yaml(tmp_path: Path):
    yaml_content = {
        "version": 1.0,
        "systems": {
            "local": {
                "queueing_system": None,
                "arch": "x86_64",
                "node": {"cores": 8, "memory_gb": 16, "gpus": 0},
                "env": {"backend": "conda", "default_name": "base"},
            },
        },
    }
    yaml_path = tmp_path / "hpc-systems.yaml"
    yaml_path.write_text(yaml.safe_dump(yaml_content))

    reg = SystemRegistry.from_path(yaml_path)
    assert "local" in reg.list()
    sys = reg.get("local")
    assert sys.arch == "x86_64"
    assert sys.node["cores"] == 8
    assert sys.env["backend"] == "conda"


def test_system_registry_missing_system_raises(tmp_path: Path):
    yaml_path = tmp_path / "hpc-systems.yaml"
    yaml_path.write_text(yaml.safe_dump({"version": 1.0, "systems": {}}))
    reg = SystemRegistry.from_path(yaml_path)
    with pytest.raises(KeyError, match="nonexistent"):
        reg.get("nonexistent")
