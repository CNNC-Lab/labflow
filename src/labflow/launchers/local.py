"""Local launcher: run the experiment in-process, write manifest."""

from __future__ import annotations

import json
import uuid
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any

from labflow.context import config_label, reset_output_dir, set_output_dir
from labflow.manifest import Manifest, write_manifest
from labflow.registry import SystemSpec


class LocalLauncher:
    def __init__(self, spec: SystemSpec, output_root: Path | None = None):
        self.spec = spec
        self.output_root = Path(output_root or Path.cwd() / "outputs")

    def run(self, func: Callable[..., dict], config: dict[str, Any]) -> dict[str, Any]:
        run_id = f"{datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')}-{uuid.uuid4().hex[:6]}"
        exp_name = getattr(func, "__name__", "unknown")
        # Optional `label` groups variants: <output_root>/<exp>/<label>/<run-id>/.
        # Without a label, fall back to the archival <output_root>/<exp>/<run-id>/.
        label = config_label(config)
        parts = [exp_name, str(label), run_id] if label else [exp_name, run_id]
        run_dir = self.output_root.joinpath(*parts)
        run_dir.mkdir(parents=True, exist_ok=True)

        # Bind the run dir so the experiment can write figures/artifacts beside the
        # manifest via labflow.current_output_dir().
        token = set_output_dir(run_dir)
        try:
            returned = func(config) if callable(func) else None
        finally:
            reset_output_dir(token)

        # Dump returned results as results.json (str fallback for now; binary/array
        # serialisation — DataFrames, ndarrays — is a documented follow-up).
        if isinstance(returned, dict):
            (run_dir / "results.json").write_text(json.dumps(returned, indent=2, default=str))

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
