"""NEST simulation experiment template.

For workstation dev: expects nest-dev conda env (per HOWTO-NEST-dev.md).
For Deucalion: paired with an Apptainer image containing NEST.
"""

from __future__ import annotations

from dataclasses import dataclass

from labflow import experiment


@dataclass
class EXPERIMENT_NAMEConfig:
    n_neurons: int = 1000
    simulation_time_ms: float = 1000.0
    threads: int = 4
    seed: int = 42


@experiment(config=EXPERIMENT_NAMEConfig, tags=["nest", "simulation", "spiking"])
def EXPERIMENT_NAME(cfg: EXPERIMENT_NAMEConfig) -> dict:
    """TODO: describe this NEST simulation."""
    import nest

    nest.ResetKernel()
    nest.SetKernelStatus({
        "local_num_threads": cfg.threads,
        "rng_seed": cfg.seed,
        "print_time": False,
    })
    neurons = nest.Create("iaf_psc_alpha", cfg.n_neurons)
    spike_rec = nest.Create("spike_recorder")
    nest.Connect(neurons, spike_rec)
    # TODO: replace with your network
    nest.Simulate(cfg.simulation_time_ms)
    n_spikes = nest.GetStatus(spike_rec, "n_events")[0]
    return {"n_spikes": int(n_spikes), "n_neurons": cfg.n_neurons}
