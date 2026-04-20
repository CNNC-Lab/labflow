# Install

## Requirements

- Python ≥ 3.11
- git

## Install from source (recommended during v0.1)

```bash
git clone https://github.com/CNNC-Lab/labflow.git ~/repos/labflow
cd ~/repos/labflow
pip install -e ".[dev,docs,snakemake]"
```

Verify:

```bash
labflow --version
# 0.1.0
```

## Optional backends

- **conda**: install Miniforge or Miniconda and ensure `conda` is on PATH.
- **uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **apptainer**: apt package or build from source; v1.3+ recommended.
- **pixi**: `curl -fsSL https://pixi.sh/install.sh | bash`

## HPC systems registry

labflow reads `~/.claude/contexts/hpc-systems.yaml` by default. On the workstation, this is a symlink to the vault-side file maintained by the `hpc-engineer` agent. See [HPC systems registry](../concepts/hpc-systems-registry.md).
