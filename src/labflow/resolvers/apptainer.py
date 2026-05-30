"""Apptainer / Singularity container resolver (common HPC default)."""

from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

from labflow.resolvers.base import EnvResolver, register_resolver


@register_resolver
class ApptainerResolver(EnvResolver):
    backend = "apptainer"

    def activate_command(self, project_root: str) -> str:
        image = self.config.get("image")
        if not image:
            return "# No apptainer image configured; set env.image in .labflow.yaml"
        return f"apptainer exec {image}"

    def install_command(self, project_root: str) -> str:
        recipe = self.config.get("recipe", f"{project_root}/containers/labflow.def")
        image = self.config.get("image", f"{project_root}/containers/labflow.sif")
        return f"apptainer build --fakeroot {image} {recipe}"

    def lock_file_path(self, project_root: str) -> str | None:
        image = self.config.get("image")
        if image and Path(image).exists():
            return image
        return None

    def verify(self, project_root: str) -> bool:
        return shutil.which("apptainer") is not None or shutil.which("singularity") is not None

    def image_hash(self) -> str | None:
        """SHA256 of the image file, for manifest inclusion."""
        image = self.config.get("image")
        if not image or not Path(image).exists():
            return None
        h = hashlib.sha256()
        with open(image, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return f"sha256:{h.hexdigest()}"
