"""Conda env resolver."""

from __future__ import annotations

import shutil
from pathlib import Path

from labflow.resolvers.base import EnvResolver, register_resolver


@register_resolver
class CondaResolver(EnvResolver):
    backend = "conda"

    def activate_command(self, project_root: str) -> str:
        name = self.config.get("default_name", "base")
        activation = self.config.get("activation")
        if activation:
            return activation
        return f"conda activate {name}"

    def install_command(self, project_root: str) -> str:
        lock = self.lock_file_path(project_root)
        if lock and Path(lock).exists():
            return f"conda-lock install --name {self.config.get('default_name', 'base')} {lock}"
        env_file = Path(project_root) / "environment.yml"
        if env_file.exists():
            return f"conda env update -n {self.config.get('default_name', 'base')} -f {env_file}"
        return f"conda env create -n {self.config.get('default_name', 'base')} --yes"

    def lock_file_path(self, project_root: str) -> str | None:
        for candidate in ("conda-lock.yml", "environment.lock.yml"):
            p = Path(project_root) / candidate
            if p.exists():
                return str(p)
        return None

    def verify(self, project_root: str) -> bool:
        return shutil.which("conda") is not None
