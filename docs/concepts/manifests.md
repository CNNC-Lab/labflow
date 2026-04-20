# Provenance manifests

Every run writes `outputs/<exp>/<run-id>/manifest.json` with:

- `labflow_version`, `schema_version`
- `experiment`, `run_id`, `timestamp_utc`
- `git_commit`, `git_dirty`
- `config_rendered`, `config_hash`, `seed`
- `env` (backend, lockfile_hash, Python version, packages)
- `hardware` (arch, CPU, memory, GPU)
- `resources_requested`, `resources_used`
- `slurm_job_id`, `container_hash`
- `outputs` (list of output files), `returned` (function return value if dict)

Replay a run → re-hash config + env + git + seed → compare to this manifest.
