# Deucalion x86 partition

2× AMD EPYC 7742, 128-core, 256 GB per node. Partitions: `dev-x86`, `normal-x86`, `large-x86`.

## Submitting

```bash
labflow submit my_experiment --system deucalion-x86 --partition normal \
    --nodes 2 --time 2:00:00
```

EESSI NOT available on x86 partition — use native compile or pip venv.
