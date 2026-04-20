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
