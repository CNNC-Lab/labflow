"""uv env resolver."""

from __future__ import annotations

import shutil
from pathlib import Path

from labflow.resolvers.base import EnvResolver, register_resolver


@register_resolver
class UvResolver(EnvResolver):
    backend = "uv"

    def activate_command(self, project_root: str) -> str:
        return f"source {project_root}/.venv/bin/activate  # uv-managed venv"

    def install_command(self, project_root: str) -> str:
        return "uv sync"

    def lock_file_path(self, project_root: str) -> str | None:
        p = Path(project_root) / "uv.lock"
        return str(p) if p.exists() else None

    def verify(self, project_root: str) -> bool:
        return shutil.which("uv") is not None
