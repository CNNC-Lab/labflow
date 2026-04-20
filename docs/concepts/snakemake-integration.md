# Snakemake integration

For multi-step DAG pipelines, pair an `analysis-pipeline` labflow experiment with a `Snakefile`.

```python
from labflow import experiment
from labflow.snakemake_hook import run_snakemake

@experiment(config=PipelineConfig, tags=["pipeline", "snakemake"])
def my_pipeline(cfg):
    result = run_snakemake(
        snakefile="workflow/Snakefile",
        cores=cfg.n_cores,
        config={"input_dir": cfg.input_path, "output_dir": cfg.output_path},
    )
    return {"returncode": result["returncode"]}
```

See [Snakemake docs](https://snakemake.readthedocs.io/) for rule authoring.
