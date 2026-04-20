"""Abstract env resolver + backend registry."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, ClassVar


class ResolverError(RuntimeError):
    """Raised when resolver setup or lookup fails."""


class EnvResolver(ABC):
    """Abstract interface for an env backend.

    Concrete subclasses implement:
        - activate_command(project_root): shell line to activate
        - install_command(project_root): shell line to install deps
        - lock_file_path(project_root): path to the lock/spec file
        - verify(project_root): boolean — is env actually usable right now?
    """

    backend: ClassVar[str] = ""

    def __init__(self, config: dict[str, Any]):
        if not self.backend:
            raise TypeError(f"{type(self).__name__} must set class attribute `backend`")
        self.config = config

    @abstractmethod
    def activate_command(self, project_root: str) -> str: ...

    @abstractmethod
    def install_command(self, project_root: str) -> str: ...

    @abstractmethod
    def lock_file_path(self, project_root: str) -> str | None: ...

    @abstractmethod
    def verify(self, project_root: str) -> bool: ...


_REGISTRY: dict[str, type[EnvResolver]] = {}


def register_resolver(cls: type[EnvResolver]) -> type[EnvResolver]:
    """Class decorator: register a resolver by its `backend` attribute."""
    if not cls.backend:
        raise ResolverError(f"{cls.__name__} must set `backend` attribute")
    _REGISTRY[cls.backend] = cls
    return cls


def get_resolver(backend: str, config: dict[str, Any]) -> EnvResolver:
    """Look up a resolver by backend name and instantiate it."""
    if backend not in _REGISTRY:
        raise ResolverError(f"unknown backend {backend!r}. Registered: {list(_REGISTRY)}")
    return _REGISTRY[backend](config)
