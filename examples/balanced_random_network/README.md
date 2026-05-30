# balanced_random_network — labflow example

A Brunel (2000) balanced random network in NEST, written as a labflow experiment. Generic — it
exists to demonstrate the labflow experiment format end-to-end, nothing project-specific.

```bash
conda activate nest-dev
pip install -e ~/repos/labflow

# from this directory:
labflow run balanced_random_network                 # defaults (1000 E + 250 I, g=5, eta=2)
labflow run balanced_random_network g=6 eta=2.5     # inhibition-dominated, mean-driven
labflow sweep balanced_random_network g=4,5,6       # sweep relative inhibition
labflow submit balanced_random_network --system deucalion-arm --time 0:30:00 --dry-run

# without labflow:
python -c "from run import balanced_random_network, BRNConfig as C; print(balanced_random_network(C(g=6.0)))"
```

Returns `{mean_rate_hz, mean_cv_isi, nu_ext_hz, ...}`. In the asynchronous-irregular regime expect
`mean_cv_isi ≈ 1` and a low-but-nonzero `mean_rate_hz`. Full walkthrough: vault
`Research/compartmentalized-learning/HOWTO-labflow.md`.
