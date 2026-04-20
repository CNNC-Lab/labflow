# Apptainer backend

Default for Deucalion. Build images locally with `singularity build --fakeroot`, push to `/projects/$project/containers/`.

## Recipe templates

`~/.claude/contexts/hpc-templates/apptainer/` contains recipes for:
- `nest-arm.def` — NEST for Deucalion ARM
- `nest-x86.def` — NEST for Deucalion x86
- `jax-gpu.def` — JAX + CUDA for Deucalion GPU
- `pytorch-gpu.def` — PyTorch + CUDA for Deucalion GPU

## Usage

```yaml
# .labflow.yaml (project root)
env:
  backend: apptainer
  image: /projects/myproj/containers/nest-arm.sif
```
