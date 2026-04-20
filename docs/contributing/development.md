# Development

## Setup

```bash
git clone https://github.com/CNNC-Lab/labflow.git
cd labflow
pip install -e ".[dev,docs,snakemake]"
pre-commit install  # optional
```

## Testing

```bash
pytest                       # all tests
pytest tests/unit/ -v        # unit only
pytest tests/integration/ -v # integration
pytest --cov=labflow         # coverage
```

## Linting

```bash
ruff check .
ruff format .
```

## Docs

```bash
mkdocs serve   # live preview at http://localhost:8000
mkdocs build   # build static site
```

## Adding a new resolver

1. Create `src/labflow/resolvers/<name>.py` subclassing `EnvResolver`
2. Decorate the class with `@register_resolver`
3. Set `backend = "<name>"` class attribute
4. Implement `activate_command`, `install_command`, `lock_file_path`, `verify`
5. Import it in `resolvers/__init__.py`
6. Add a test in `tests/unit/test_resolvers.py`
7. Document it under `docs/guides/backends/<name>.md`

## Adding a new HPC system

Edit `~/.claude/contexts/hpc-systems.yaml` (or the test fixture). The schema is self-documenting.

## Adding a new experiment template

1. Create `src/labflow/templates/<name>/run.py` with an `EXPERIMENT_NAME` placeholder for the function name
2. Create `src/labflow/templates/<name>/README.md`
3. Add an entry in `tests/integration/test_cli.py::test_labflow_new`
4. Document under `docs/concepts/experiments.md`
