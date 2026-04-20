# Deucalion GPU partitions

4× NVIDIA A100 per node (40 GB or 80 GB variants). Partitions: `normal-a100-40`, `normal-a100-80`. Non-exclusive by default.

## GPU billing rule

**1 GPU = 32 CPUs allocated**. labflow enforces `cpus-per-task = 32 × --gpus`.

```bash
labflow submit my_experiment --system deucalion-gpu-a100-40 \
    --partition normal --nodes 1 --gpus 2 --time 2:00:00
```

## Container

CUDA-enabled Apptainer images in `/share/apps-x86/containers/enroot/`. For JAX: build from `jax-gpu.def` template.
