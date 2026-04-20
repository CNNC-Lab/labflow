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
