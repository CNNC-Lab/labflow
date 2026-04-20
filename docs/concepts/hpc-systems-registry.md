# HPC systems registry

labflow reads `~/.claude/contexts/hpc-systems.yaml`. Each entry is a SystemSpec with:

- `queueing_system`: `slurm` or null (local)
- `arch`, `node` (cores, memory_gb, gpus)
- `partitions` (dev / normal / large)
- `env` (backend + per-backend config)
- `modules` (mpi, compiler, cuda)
- `scratch` path (absolute, with `${project}` interpolation)
- `template` (default Jinja2 template name)

See the full schema in the design spec: `Assets/claude/docs/specs/2026-04-20-scientific-software-infrastructure-design.md` §6.
