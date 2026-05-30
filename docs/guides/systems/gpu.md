# GPU clusters

Example: a SLURM cluster with NVIDIA GPU nodes (e.g. A100 40/80 GB). Define it in your
registry and submit by its `--system` name.

## GPU billing rule

Many sites bill a fixed number of CPUs per GPU. If your registry entry sets
`cpus_per_gpu`, labflow enforces `cpus-per-task = cpus_per_gpu × --gpus` so you request
(and are billed) consistently.

```bash
labflow submit my_experiment --system cluster-gpu \
    --partition normal --nodes 1 --gpus 2 --time 2:00:00 --account <account>
```

## Container

Use a CUDA-enabled Apptainer image, or your site's prebuilt GPU containers. For JAX,
start from the `simulation-jax` template and a CUDA base image.

See [HPC systems registry](../../concepts/hpc-systems-registry.md) for the entry schema.
