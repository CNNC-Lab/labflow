# NEST scaling study (Brunel balanced random network)

Strong and weak scaling of a Brunel network in NEST, as labflow experiments. The
experiment (`experiments/brn_scaling.py`) records build and simulate wall-clock
times; you pick the regime by how you sweep it.

## Run

```bash
# from this directory (it contains experiments/)
# STRONG scaling — fixed problem, more cores:
labflow sweep brn_scaling n_total_fixed=50000 threads=1,2,4,8,16,24,48

# WEAK scaling — problem grows with cores (fixed work per core):
labflow sweep brn_scaling n_per_thread=2500 threads=1,2,4,8,16,24,48
```

On a cluster, submit instead of running locally:

```bash
labflow submit brn_scaling --system cluster-arm --partition normal \
    --nodes 1 --time 1:00:00 --account <account> -- n_total_fixed=50000 threads=48
```

## Analyze

```bash
python analyze.py outputs/brn_scaling --out scaling.png
```

Prints a table (build/sim/total time, speedup, efficiency) and writes a plot.
The script auto-detects the regime: constant `N` → strong (speedup + efficiency);
growing `N` → weak (efficiency = T₁ / Tₚ, ideal = 1).

## What to expect

- **Strong scaling** speedup rises with threads but saturates as serial overhead
  (build, RNG, communication) dominates — efficiency drops past the point where
  per-core work gets too small.
- **Weak scaling** efficiency stays near 1 while per-core work is constant, falling
  off when memory bandwidth or connectivity overhead grows super-linearly.

Single-node thread (OpenMP) scaling is the simplest study; multi-node MPI scaling
is the natural extension (NEST built `--with-mpi`, submit with `--nodes N` and an
MPI launcher in the system's SLURM template).
