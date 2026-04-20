"""Provenance manifest — one JSON per run, written to outputs/<exp>/<ts>/manifest.json.

Captures enough state for byte-exact reproduction when seed + env + hardware allow.
Schema v1 (2026-04-20); future versions bump `schema_version`.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


@dataclass
class Manifest:
    experiment: str
    run_id: str
    config_rendered: dict[str, Any]
    seed: int
    system: str
    labflow_version: str = ""
    schema_version: int = SCHEMA_VERSION
    timestamp_utc: str = ""
    git_commit: str | None = None
    git_dirty: bool | None = None
    config_hash: str = ""
    env: dict[str, Any] = field(default_factory=dict)
    hardware: dict[str, Any] = field(default_factory=dict)
    resources_requested: dict[str, Any] = field(default_factory=dict)
    resources_used: dict[str, Any] = field(default_factory=dict)
    slurm_job_id: str | None = None
    container_hash: str | None = None
    outputs: list[str] = field(default_factory=list)
    returned: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.labflow_version:
            from labflow import __version__

            self.labflow_version = __version__
        if not self.timestamp_utc:
            self.timestamp_utc = datetime.now(UTC).isoformat()
        if not self.config_hash:
            self.config_hash = _hash_dict(self.config_rendered)
        if self.git_commit is None:
            self.git_commit, self.git_dirty = _git_state()
        if not self.hardware:
            self.hardware = _hardware_info()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _hash_dict(d: dict[str, Any]) -> str:
    serialized = json.dumps(d, sort_keys=True, default=str).encode()
    return f"sha256:{hashlib.sha256(serialized).hexdigest()}"


def _git_state() -> tuple[str | None, bool | None]:
    try:
        commit = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
        status = (
            subprocess.check_output(["git", "status", "--porcelain"], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
        return commit, bool(status)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None, None


def _hardware_info() -> dict[str, Any]:
    return {
        "arch": platform.machine(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count(),
    }


def write_manifest(manifest: Manifest, run_dir: Path) -> Path:
    """Write manifest.json atomically to run_dir."""
    run_dir.mkdir(parents=True, exist_ok=True)
    out = run_dir / "manifest.json"
    tmp = run_dir / "manifest.json.tmp"
    tmp.write_text(json.dumps(manifest.to_dict(), indent=2, default=str))
    tmp.replace(out)
    return out
