# Env resolvers

Each backend implements the `EnvResolver` interface (in `labflow.resolvers.base`):

```python
class EnvResolver(ABC):
    backend: ClassVar[str]
    def activate_command(self, project_root: str) -> str: ...
    def install_command(self, project_root: str) -> str: ...
    def lock_file_path(self, project_root: str) -> str | None: ...
    def verify(self, project_root: str) -> bool: ...
```

Supported backends (v0.1): `conda`, `uv`, `poetry`, `venv`, `pixi`, `apptainer`.

Register a new one with `@register_resolver` on your subclass. See [Adding a resolver](../contributing/development.md).
