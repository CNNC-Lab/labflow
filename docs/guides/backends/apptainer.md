# Apptainer backend

Common on ARM and GPU clusters. Build images locally with `singularity build --fakeroot`, push to `/projects/$project/containers/`.

## Recipe templates

`~/.claude/contexts/hpc-templates/apptainer/` contains recipes for:
- `nest-arm.def` — NEST for an ARM cluster
- `nest-x86.def` — NEST for an x86 cluster
- `jax-gpu.def` — JAX + CUDA for a GPU cluster
- `pytorch-gpu.def` — PyTorch + CUDA for a GPU cluster

## Usage

```yaml
# .labflow.yaml (project root)
env:
  backend: apptainer
  image: /projects/myproj/containers/nest-arm.sif
```
