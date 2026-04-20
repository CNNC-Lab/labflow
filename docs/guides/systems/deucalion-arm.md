# Deucalion ARM partition

Fujitsu A64FX, 48-core, 32 GB per node. Partitions: `dev-arm` (4h, ≤2 nodes), `normal-arm` (48h, ≤128 nodes), `large-arm` (72h, ≤512 nodes).

## Submitting

```bash
labflow submit my_experiment --system deucalion-arm --partition normal \
    --nodes 4 --time 2:00:00 --account myaccount
```

## Container strategy

Native ARM compile via Fujitsu `FJSVstclanga` or GNU + `-march=native`. Do NOT use x86 wheels — ARM jobs must be compiled from source. Apptainer recipes for NEST-ARM are in `~/.claude/contexts/hpc-templates/apptainer/nest-arm.def`.

## EESSI

Available via `source /cvmfs/software.eessi.io/versions/2023.06/init/bash` — pre-compiled optimized software stack.

## Gotchas

- Jobs MUST run from `/projects/$project` (not `/home`, quota 25 GB)
- `OMP_PROC_BIND=TRUE` and `--hint=nomultithread` for OpenMP performance
- `OMP_NUM_THREADS=${SLURM_CPUS_PER_TASK}` pattern
