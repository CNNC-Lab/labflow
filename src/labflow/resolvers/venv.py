"""Plain venv resolver (HPC fallback)."""

from __future__ import annotations

import shutil
from pathlib import Path

from labflow.resolvers.base import EnvResolver, register_resolver


@register_resolver
class VenvResolver(EnvResolver):
    backend = "venv"

    def activate_command(self, project_root: str) -> str:
        location = self.config.get("location", f"{project_root}/venv")
        python_module = self.config.get("python_module")
        prefix = f"module load {python_module} && " if python_module else ""
        return f"{prefix}source {location}/bin/activate"

    def install_command(self, project_root: str) -> str:
        location = self.config.get("location", f"{project_root}/venv")
        req = Path(project_root) / "requirements.txt"
        if req.exists():
            return f"python -m venv {location} && source {location}/bin/activate && pip install -r {req}"
        return f"python -m venv {location}"

    def lock_file_path(self, project_root: str) -> str | None:
        for candidate in ("requirements.txt", "requirements.lock"):
            p = Path(project_root) / candidate
            if p.exists():
                return str(p)
        return None

    def verify(self, project_root: str) -> bool:
        return shutil.which("python") is not None
