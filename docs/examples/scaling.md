# NEST scaling study

A worked **strong** and **weak** scaling study of a Brunel balanced random network
in NEST, expressed entirely as labflow experiments. Source:
[`examples/scaling/`](https://github.com/CNNC-Lab/labflow/tree/main/examples/scaling).

One experiment (`brn_scaling`) builds and simulates the network and records build +
simulate wall-clock times. You choose the regime by **how you sweep** it.

## Strong scaling — fix the problem, add cores

```bash
labflow sweep brn_scaling n_total_fixed=50000 threads=1,2,4,8,16,24,48
```

Total network size is constant; only the thread count changes. Speedup is
`T(1) / T(p)`; parallel efficiency is `speedup / p`.

## Weak scaling — grow the problem with the cores

```bash
labflow sweep brn_scaling n_per_thread=2500 threads=1,2,4,8,16,24,48
```

Total size grows with threads (`N = n_per_thread × threads`), so the work per core
is constant. Weak efficiency is `T(1) / T(p)` — ideally flat at 1.

## On a cluster

```bash
labflow submit brn_scaling --system cluster-arm --partition normal \
    --nodes 1 --time 1:00:00 --account <account> -- n_total_fixed=50000 threads=48
```

Each run writes a `manifest.json` with the returned timings and full provenance
(git SHA, config, seed, hardware, wall time).

## Analyze

```bash
python examples/scaling/analyze.py outputs/brn_scaling --out scaling.png
```

The analyzer reads every run manifest, auto-detects strong vs. weak, prints a table
(build / sim / total time, speedup, efficiency) and saves speedup + efficiency
curves.

!!! tip "Extending to multi-node"
    Single-node OpenMP thread scaling is the simplest study. For multi-node MPI
    scaling, build NEST `--with-mpi`, give your system's SLURM template an MPI
    launcher (`srun`/`mpirun`), and submit with `--nodes N`.
