# First SLURM submission

Requires a configured system in `~/.claude/contexts/hpc-systems.yaml` (see [HPC systems registry](../concepts/hpc-systems-registry.md)).

```bash
labflow submit ou_stationary --system deucalion-arm --partition normal \
    --nodes 2 --time 2:00:00 --account myaccount
```

Use `--dry-run` to inspect the rendered sbatch script without submitting:

```bash
labflow submit ou_stationary --system deucalion-arm --dry-run
```
