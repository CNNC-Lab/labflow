# Design: run outputs, experiment labels, and parameter scans

**Status:** agreed design; a minimal slice was implemented 2026-06-02 (see *Implemented*).
The rest is open work for a dedicated session.

## Context

Downstream projects (e.g. hetsyn neuron *profiling*) need **navigable, per-variant**
outputs — one canonical place per experiment+variant — whereas labflow's native model
is **archival**: `outputs/<exp>/<timestamp>-<uuid>/`, discovered by reading manifests.
This design reconciles the two without abandoning provenance.

## Decisions (agreed)

1. **Run-dir layout** `{output_root}/<exp>/<label>/<run-id>/`. `label` groups variants
   (human-readable, set per run); the timestamped `<run-id>` keeps archival history
   *within* each label. No `label` → `{output_root}/<exp>/<run-id>/` (unchanged).
   `output_root` from `.labflow.yaml` (default `outputs`; hetsyn sets `data`).
2. Each run dir holds **`manifest.json`** (provenance) + **`results.json`** (returned
   dict) + the experiment's **figures/artifacts**.
3. **Run-dir handoff**: `labflow.current_output_dir()` (a contextvar bound by the
   launcher) lets the experiment write artifacts beside the manifest — without changing
   the `fn(cfg)->dict` contract or chdir-ing (which would break config-relative paths).
4. **Parameter scans / HPO → Optuna**, not `labflow sweep`: one run = one study;
   `GridSampler` for exhaustive grids, TPE for HPO; `study.db` + per-trial artifacts in
   the run dir → "one folder, all combinations." `labflow sweep` stays the scatter
   option (independent/parallel runs, one manifest each).

## Implemented (2026-06-02, minimal slice — **local launcher only**)

- `labflow/context.py` — `current_output_dir()` + launcher-side `set/reset_output_dir`
  + `config_label`.
- `LocalLauncher.run` — inserts `<label>` into the run dir; binds `current_output_dir`
  around the experiment fn; dumps `results.json`.
- `cli._run_one` — `output_root` read from `.labflow.yaml` (`output_root:` key).
- `labflow/__init__.py` — exports `current_output_dir`.

## Open problems (dedicated session)

1. **SLURM launcher parity.** `SlurmLauncher.submit` runs the experiment on the node via
   submitit; the label/run-dir/`current_output_dir`/`results.json` logic added to
   `LocalLauncher` must be replicated for the remote path (run dir created + bound +
   manifest/results written where the job runs / on shared storage). **Factor the
   run-dir + context + manifest + results logic into a shared helper used by both
   launchers** rather than duplicating.
2. **Distributed Optuna (shared study).** Once a study is initiated, independent parallel
   jobs (e.g. a SLURM array) should all feed the **same** study. Optuna supports this via
   shared `storage` (**RDB — postgres/mysql — recommended** for true concurrency; sqlite
   only with care: file locking, never on networked FS). Tension with per-run dirs: the
   study storage must live **above** the run dir (study-level, e.g.
   `{output_root}/<exp>/<label>/study.{db|url}` or a `studies/` area), shared by all
   contributing jobs, while each job keeps its own run dir for artifacts. Introduce a
   "study" concept spanning runs (stable storage URL + `study_name`; jobs call
   `optuna.load_study(...).optimize(...)`); provide a helper/config convention for the
   shared storage path + a way to launch N array jobs against it.
3. **Results serialization beyond JSON.** `returned` is often DataFrames / dicts with
   ndarrays — JSON is lossy and bloated. Add a serialization layer: detect non-JSON
   values and save as artifacts (ndarray→`.npz`, DataFrame→`.parquet`, arbitrary→
   `.pkl`/joblib), keep `results.json` for the JSON-able summary + references, and record
   artifact paths in the manifest `outputs`. Consider a `labflow.save_result(obj, name)`
   helper exposed to experiments (writes into `current_output_dir()`).
4. *(Optional)* **Grouped `sweep`.** If Optuna `GridSampler` is insufficient for some
   coarse grids, add a grouped-sweep mode: one parent `…/<label>/<sweep-id>/` with a
   per-combo subdir (named by the varied params) + a sweep-level summary.

## Downstream usage (hetsyn)

Set `.labflow.yaml` `output_root: data`; experiments add a `label` field, write figures
to `labflow.current_output_dir()`, and return a results dict (labflow writes
`manifest.json` + `results.json`).