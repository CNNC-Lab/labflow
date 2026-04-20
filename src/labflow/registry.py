"""Experiment registry + HPC system registry.

ExperimentRegistry — discovered via the @experiment decorator. Holds:
    - name (function __name__)
    - callable (the function itself)
    - config_cls (the dataclass type)
    - tags (list[str])
    - docstring

SystemRegistry — loaded from ~/.claude/contexts/hpc-systems.yaml. Holds per-system:
    - arch, queueing_system, partitions, node specs
    - env backend config
    - modules, eessi flag, scratch path
    - default Jinja2 template name
"""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar

import yaml

DEFAULT_SYSTEMS_YAML = Path.home() / ".claude" / "contexts" / "hpc-systems.yaml"


@dataclass
class ExperimentMeta:
    """Metadata for a registered experiment."""

    name: str
    func: Callable[..., dict]
    config_cls: type
    tags: list[str] = field(default_factory=list)
    doc: str = ""


class ExperimentRegistry:
    """Class-level registry of @experiment-decorated functions."""

    _registry: ClassVar[dict[str, ExperimentMeta]] = {}

    @classmethod
    def register(cls, meta: ExperimentMeta) -> None:
        if meta.name in cls._registry:
            raise ValueError(f"Experiment {meta.name!r} already registered")
        cls._registry[meta.name] = meta

    @classmethod
    def get(cls, name: str) -> ExperimentMeta:
        if name not in cls._registry:
            raise KeyError(f"Experiment {name!r} not found. Registered: {list(cls._registry)}")
        return cls._registry[name]

    @classmethod
    def list(cls) -> list[str]:
        return sorted(cls._registry)

    @classmethod
    def clear(cls) -> None:
        """Used only in tests."""
        cls._registry.clear()


def experiment(
    *,
    config: type,
    tags: list[str] | None = None,
) -> Callable[[Callable[..., dict]], Callable[..., dict]]:
    """Decorator: register a function as a labflow experiment.

    Usage:
        @experiment(config=OUConfig, tags=["stochastic"])
        def ou_stationary(cfg: OUConfig) -> dict:
            ...
    """

    def decorator(func: Callable[..., dict]) -> Callable[..., dict]:
        meta = ExperimentMeta(
            name=func.__name__,
            func=func,
            config_cls=config,
            tags=list(tags or []),
            doc=func.__doc__ or "",
        )
        ExperimentRegistry.register(meta)
        return func

    return decorator


def sweep(**params: Any) -> dict[str, list]:
    """Declarative sweep helper.

    Usage:
        sweep(tau=[5, 10, 20], seed=[0, 1, 2])
    Returns:
        {"tau": [5, 10, 20], "seed": [0, 1, 2]}
    """
    return {k: (v if isinstance(v, list) else [v]) for k, v in params.items()}


@dataclass
class SystemSpec:
    """One HPC system entry loaded from hpc-systems.yaml."""

    name: str
    queueing_system: str | None
    arch: str
    node: dict[str, Any]
    env: dict[str, Any]
    partitions: dict[str, dict] = field(default_factory=dict)
    modules: dict[str, list] = field(default_factory=dict)
    eessi_available: bool = False
    eessi_init: str | None = None
    scratch: str | None = None
    template: str = "cpu-mpi"
    exclusive: bool = True
    cpus_per_gpu: int | None = None
    login_host: str | None = None
    ssh_alias: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)


class SystemRegistry:
    """Registry of HPC systems loaded from YAML."""

    def __init__(self, systems: dict[str, SystemSpec], version: float = 1.0) -> None:
        self._systems = systems
        self.version = version

    @classmethod
    def from_path(cls, path: Path | None = None) -> SystemRegistry:
        """Load registry from a YAML file. Defaults to ~/.claude/contexts/hpc-systems.yaml."""
        path = path or DEFAULT_SYSTEMS_YAML
        if not path.exists():
            raise FileNotFoundError(
                f"HPC systems registry not found at {path}. "
                f"Create it (schema in spec §6) or pass path= explicitly."
            )
        data = yaml.safe_load(path.read_text())
        version = data.get("version", 1.0)
        systems = {}
        for name, s in (data.get("systems") or {}).items():
            systems[name] = SystemSpec(
                name=name,
                queueing_system=s.get("queueing_system"),
                arch=s.get("arch", "x86_64"),
                node=s.get("node", {}),
                env=s.get("env", {}),
                partitions=s.get("partitions", {}),
                modules=s.get("modules", {}),
                eessi_available=s.get("eessi_available", False),
                eessi_init=s.get("eessi_init"),
                scratch=s.get("scratch"),
                template=s.get("template", "cpu-mpi"),
                exclusive=s.get("exclusive", True),
                cpus_per_gpu=s.get("cpus_per_gpu"),
                login_host=s.get("login_host"),
                ssh_alias=s.get("ssh_alias"),
                raw=s,
            )
        return cls(systems, version=version)

    def get(self, name: str) -> SystemSpec:
        if name not in self._systems:
            raise KeyError(f"System {name!r} not in registry. Known: {list(self._systems)}")
        return self._systems[name]

    def list(self) -> list[str]:
        return sorted(self._systems)

    def resolve_scratch(self, name: str, project: str | None = None) -> str:
        """Substitute ${project} in scratch path."""
        sys = self.get(name)
        if sys.scratch is None:
            return os.getcwd()
        project = project or os.environ.get("LABFLOW_PROJECT", "default")
        return sys.scratch.replace("${project}", project)
