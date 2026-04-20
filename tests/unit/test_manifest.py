"""Tests for the provenance manifest writer."""

from __future__ import annotations

import json
from pathlib import Path

from labflow.manifest import Manifest, write_manifest


def test_manifest_basic_fields():
    m = Manifest(
        experiment="ou_stationary",
        run_id="2026-04-22-14-30-00-abc123",
        config_rendered={"tau": 10.0, "seed": 42},
        seed=42,
        system="local-workstation",
    )
    d = m.to_dict()
    assert d["experiment"] == "ou_stationary"
    assert d["seed"] == 42
    assert d["labflow_version"]


def test_write_manifest_creates_json(tmp_path: Path):
    m = Manifest(
        experiment="test",
        run_id="test-run",
        config_rendered={"x": 1},
        seed=0,
        system="local-workstation",
    )
    out = write_manifest(m, tmp_path)
    assert out.exists()
    loaded = json.loads(out.read_text())
    assert loaded["experiment"] == "test"
