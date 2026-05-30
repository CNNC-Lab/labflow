# ARM (aarch64) clusters

Example: an ARM SLURM cluster (e.g. Fujitsu A64FX nodes). You describe the system
**once** in your registry (`~/.claude/contexts/hpc-systems.yaml`); labflow renders the
SLURM script from that entry. The `--system` name is whatever you call it there.

## Submit

```bash
labflow submit my_experiment --system cluster-arm --partition normal \
    --nodes 4 --time 2:00:00 --account <account>
```

## ARM-specific notes

- **Compile native.** Don't rely on x86 wheels — build from source for `aarch64`, or
  use an Apptainer image compiled for the target CPU (e.g. GCC `-mcpu=<cpu>`).
- **OpenMP placement.** Set `OMP_PROC_BIND=TRUE` and
  `OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}` for thread-scaling performance.
- **Run from scratch.** Jobs should run from the parallel filesystem (your registry's
  `scratch:` path), not `$HOME`.

See [HPC systems registry](../../concepts/hpc-systems-registry.md) for the entry schema.
