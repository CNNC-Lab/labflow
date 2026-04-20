"""Pixi env resolver."""

from __future__ import annotations

import shutil
from pathlib import Path

from labflow.resolvers.base import EnvResolver, register_resolver


@register_resolver
class PixiResolver(EnvResolver):
    backend = "pixi"

    def activate_command(self, project_root: str) -> str:
        return f"cd {project_root} && pixi shell"

    def install_command(self, project_root: str) -> str:
        return f"cd {project_root} && pixi install"

    def lock_file_path(self, project_root: str) -> str | None:
        p = Path(project_root) / "pixi.lock"
        return str(p) if p.exists() else None

    def verify(self, project_root: str) -> bool:
        return shutil.which("pixi") is not None
