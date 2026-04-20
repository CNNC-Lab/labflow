"""Tests for env resolver interface + individual backends."""

from __future__ import annotations

import pytest

from labflow.resolvers.base import EnvResolver, ResolverError, get_resolver


def test_get_resolver_for_known_backend():
    r = get_resolver("conda", {"default_name": "nest-dev"})
    assert r.backend == "conda"


def test_get_resolver_unknown_raises():
    with pytest.raises(ResolverError, match="unknown backend"):
        get_resolver("nonexistent-backend", {})


def test_base_resolver_is_abstract():
    with pytest.raises(TypeError):
        EnvResolver({})


def test_uv_resolver():
    r = get_resolver("uv", {})
    assert r.backend == "uv"
    assert "uv" in r.activate_command("/tmp")


def test_poetry_resolver():
    r = get_resolver("poetry", {})
    assert r.backend == "poetry"


def test_venv_resolver():
    r = get_resolver("venv", {"python_module": "Python/3.12.3"})
    assert r.backend == "venv"
    cmd = r.activate_command("/tmp/my-project")
    assert "activate" in cmd


def test_pixi_resolver():
    r = get_resolver("pixi", {})
    assert r.backend == "pixi"


def test_apptainer_resolver():
    r = get_resolver("apptainer", {"image_registry": "/projects/x/containers"})
    assert r.backend == "apptainer"


def test_conda_resolver_commands(tmp_path):
    r = get_resolver("conda", {"default_name": "nest-dev"})
    assert "nest-dev" in r.activate_command(str(tmp_path))
    # No lock file → falls back to create
    install = r.install_command(str(tmp_path))
    assert "conda" in install
    assert r.lock_file_path(str(tmp_path)) is None
    # verify returns bool
    assert isinstance(r.verify(str(tmp_path)), bool)


def test_conda_resolver_with_lock(tmp_path):
    (tmp_path / "conda-lock.yml").write_text("name: test")
    r = get_resolver("conda", {"default_name": "nest-dev"})
    assert r.lock_file_path(str(tmp_path)) is not None
    install = r.install_command(str(tmp_path))
    assert "conda-lock install" in install


def test_conda_resolver_with_env_yml(tmp_path):
    (tmp_path / "environment.yml").write_text("name: test")
    r = get_resolver("conda", {"default_name": "nest-dev"})
    install = r.install_command(str(tmp_path))
    assert "conda env update" in install


def test_conda_resolver_with_custom_activation():
    r = get_resolver("conda", {"default_name": "base", "activation": "my-custom-activation"})
    assert r.activate_command("/tmp") == "my-custom-activation"


def test_uv_resolver_install_and_lock(tmp_path):
    r = get_resolver("uv", {})
    assert r.install_command(str(tmp_path)) == "uv sync"
    assert r.lock_file_path(str(tmp_path)) is None
    (tmp_path / "uv.lock").write_text("")
    assert r.lock_file_path(str(tmp_path)) is not None
    assert isinstance(r.verify(str(tmp_path)), bool)


def test_poetry_resolver_commands(tmp_path):
    r = get_resolver("poetry", {})
    assert "poetry shell" in r.activate_command(str(tmp_path))
    assert "poetry install" in r.install_command(str(tmp_path))
    assert r.lock_file_path(str(tmp_path)) is None
    (tmp_path / "poetry.lock").write_text("")
    assert r.lock_file_path(str(tmp_path)) is not None
    assert isinstance(r.verify(str(tmp_path)), bool)


def test_pixi_resolver_commands(tmp_path):
    r = get_resolver("pixi", {})
    assert "pixi shell" in r.activate_command(str(tmp_path))
    assert "pixi install" in r.install_command(str(tmp_path))
    assert r.lock_file_path(str(tmp_path)) is None
    (tmp_path / "pixi.lock").write_text("")
    assert r.lock_file_path(str(tmp_path)) is not None
    assert isinstance(r.verify(str(tmp_path)), bool)


def test_venv_resolver_commands(tmp_path):
    r = get_resolver("venv", {"python_module": "Python/3.12.3"})
    cmd = r.activate_command(str(tmp_path))
    assert "module load Python/3.12.3" in cmd
    assert "activate" in cmd
    # install without requirements.txt
    install = r.install_command(str(tmp_path))
    assert "python -m venv" in install
    # install with requirements.txt
    (tmp_path / "requirements.txt").write_text("")
    install2 = r.install_command(str(tmp_path))
    assert "pip install -r" in install2
    # lock_file_path detection
    assert r.lock_file_path(str(tmp_path)) is not None
    assert isinstance(r.verify(str(tmp_path)), bool)


def test_venv_resolver_no_python_module(tmp_path):
    r = get_resolver("venv", {})
    cmd = r.activate_command(str(tmp_path))
    assert "module load" not in cmd
    assert "activate" in cmd


def test_apptainer_resolver_commands(tmp_path):
    # No image set
    r = get_resolver("apptainer", {})
    cmd = r.activate_command(str(tmp_path))
    assert "No apptainer image" in cmd
    # With an image set
    image_path = tmp_path / "test.sif"
    image_path.write_bytes(b"fake sif content")
    r2 = get_resolver("apptainer", {"image": str(image_path)})
    assert "apptainer exec" in r2.activate_command(str(tmp_path))
    assert "apptainer build" in r2.install_command(str(tmp_path))
    # lock_file_path: returns image path if exists
    assert r2.lock_file_path(str(tmp_path)) == str(image_path)
    # image_hash returns sha256:...
    h = r2.image_hash()
    assert h is not None and h.startswith("sha256:")
    # When no image, lock_file_path + image_hash return None
    assert r.lock_file_path(str(tmp_path)) is None
    assert r.image_hash() is None
    assert isinstance(r2.verify(str(tmp_path)), bool)


def test_register_resolver_rejects_missing_backend():
    from labflow.resolvers.base import EnvResolver, ResolverError, register_resolver

    class BrokenResolver(EnvResolver):
        backend = ""

        def activate_command(self, project_root: str) -> str:
            return ""

        def install_command(self, project_root: str) -> str:
            return ""

        def lock_file_path(self, project_root: str) -> str | None:
            return None

        def verify(self, project_root: str) -> bool:
            return False

    with pytest.raises(ResolverError, match="must set `backend`"):
        register_resolver(BrokenResolver)
