"""Local launcher: run the experiment in-process, write manifest."""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from labflow.manifest import Manifest, write_manifest
from labflow.registry import SystemSpec


class LocalLauncher:
    def __init__(self, spec: SystemSpec, output_root: Path | None = None):
        self.spec = spec
        self.output_root = Path(output_root or Path.cwd() / "outputs")

    def run(self, func: Callable[..., dict], config: dict[str, Any]) -> dict[str, Any]:
        run_id = f"{datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')}-{uuid.uuid4().hex[:6]}"
        exp_name = getattr(func, "__name__", "unknown")
        run_dir = self.output_root / exp_name / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        returned = func(config) if callable(func) else None

        manifest = Manifest(
            experiment=exp_name,
            run_id=run_id,
            config_rendered=config if isinstance(config, dict) else vars(config),
            seed=config.get("seed", 0) if isinstance(config, dict) else getattr(config, "seed", 0),
            system=self.spec.name,
            returned=returned if isinstance(returned, dict) else None,
        )
        write_manifest(manifest, run_dir)

        return {"run_dir": str(run_dir), "run_id": run_id, "returned": returned}
