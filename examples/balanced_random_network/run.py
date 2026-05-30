"""Balanced random network (Brunel 2000) in NEST — a generic labflow example.

A sparse random network of excitatory + inhibitory integrate-and-fire neurons
driven by external Poisson input. The canonical test bed for asynchronous-irregular
(AI) cortical-like activity. Nothing project-specific — it exists to show the labflow
experiment format end-to-end.

The `@experiment` decorator registers this function under the name `balanced_random_network`.
labflow discovers it, injects an instance of `BRNConfig` built from CLI overrides, runs it,
and writes the returned dict + a provenance manifest to the run directory.

Run it:
    labflow run balanced_random_network                 # defaults
    labflow run balanced_random_network g=6 eta=2.5     # Hydra-style overrides
    labflow sweep balanced_random_network g=4,5,6 eta=1.5,2.0   # cross-product sweep
    labflow submit balanced_random_network --system cluster-arm --nodes 1 --time 0:30:00

Without labflow (plain Python, fast iteration):
    python -c "from run import balanced_random_network, BRNConfig as C; \
               print(balanced_random_network(C(g=6.0)))"

Requires the `nest-dev` conda env on the workstation (NEST 3.x), or an Apptainer image
with NEST on an HPC cluster.
"""

from __future__ import annotations

from dataclasses import dataclass

from labflow import experiment


@dataclass
class BRNConfig:
    # network size
    n_exc: int = 1000  # excitatory neurons
    n_inh: int = 250  # inhibitory neurons (N_E:N_I = 4:1)
    epsilon: float = 0.1  # connection probability (sparse random)
    # synapse
    J: float = 0.1  # excitatory PSP amplitude (mV)
    g: float = 5.0  # relative inhibitory strength (J_inh = -g*J); g>4 => inhibition-dominated
    delay_ms: float = 1.5  # synaptic delay
    # external drive (expressed relative to rheobase rate nu_thresh)
    eta: float = 2.0  # external rate as a multiple of threshold rate (eta>1 => mean-driven)
    # neuron (iaf_psc_delta, Brunel defaults)
    tau_m_ms: float = 20.0
    V_th_mV: float = 20.0
    V_reset_mV: float = 0.0
    t_ref_ms: float = 2.0
    C_m_pF: float = 250.0
    # simulation
    simulation_time_ms: float = 1000.0
    threads: int = 4
    seed: int = 42


@experiment(config=BRNConfig, tags=["nest", "simulation", "spiking", "example"])
def balanced_random_network(cfg: BRNConfig) -> dict:
    """Simulate a Brunel balanced random network; return population firing statistics."""
    import nest
    import numpy as np

    # Thread discipline: configure the kernel BEFORE Create().
    nest.ResetKernel()
    nest.SetKernelStatus(
        {
            "local_num_threads": cfg.threads,
            "rng_seed": cfg.seed,
            "resolution": 0.1,
            "print_time": False,
        }
    )

    # --- derived parameters ---
    n_total = cfg.n_exc + cfg.n_inh
    c_exc = int(cfg.epsilon * cfg.n_exc)  # in-degree from excitatory pop
    c_inh = int(cfg.epsilon * cfg.n_inh)  # in-degree from inhibitory pop
    J_inh = -cfg.g * cfg.J

    # External Poisson rate that drives a neuron to threshold in isolation (Brunel eq.),
    # then scaled by eta. nu_thresh = V_th / (J * tau_m) converted to spikes/s.
    nu_thresh = cfg.V_th_mV / (cfg.J * cfg.tau_m_ms) * 1e3  # Hz
    nu_ext = cfg.eta * nu_thresh
    p_rate = nu_ext * c_exc  # total external rate (Hz) onto each neuron

    neuron_params = {
        "tau_m": cfg.tau_m_ms,
        "V_th": cfg.V_th_mV,
        "V_reset": cfg.V_reset_mV,
        "t_ref": cfg.t_ref_ms,
        "C_m": cfg.C_m_pF,
        "E_L": 0.0,
        "V_m": 0.0,
    }

    # --- build ---
    nest.SetDefaults("iaf_psc_delta", neuron_params)
    exc = nest.Create("iaf_psc_delta", cfg.n_exc)
    inh = nest.Create("iaf_psc_delta", cfg.n_inh)
    noise = nest.Create("poisson_generator", params={"rate": p_rate})
    spikes_exc = nest.Create("spike_recorder")

    nest.CopyModel("static_synapse", "exc_syn", {"weight": cfg.J, "delay": cfg.delay_ms})
    nest.CopyModel("static_synapse", "inh_syn", {"weight": J_inh, "delay": cfg.delay_ms})

    # external drive to all neurons
    nest.Connect(noise, exc + inh, syn_spec="exc_syn")
    # recurrent excitatory + inhibitory (fixed in-degree random connectivity)
    nest.Connect(exc, exc + inh, {"rule": "fixed_indegree", "indegree": c_exc}, "exc_syn")
    nest.Connect(inh, exc + inh, {"rule": "fixed_indegree", "indegree": c_inh}, "inh_syn")
    # record a subset of excitatory neurons
    n_rec = min(cfg.n_exc, 100)
    nest.Connect(exc[:n_rec], spikes_exc)

    nest.Simulate(cfg.simulation_time_ms)

    # --- analysis: mean rate, CV of ISI, a coarse synchrony proxy ---
    events = spikes_exc.get("events")
    times = np.asarray(events["times"])
    senders = np.asarray(events["senders"])
    duration_s = cfg.simulation_time_ms / 1e3
    mean_rate_hz = float(len(times) / (n_rec * duration_s)) if n_rec else 0.0

    cvs = []
    for nid in np.unique(senders):
        st = np.sort(times[senders == nid])
        if st.size >= 3:
            isi = np.diff(st)
            if isi.mean() > 0:
                cvs.append(isi.std() / isi.mean())
    mean_cv_isi = float(np.mean(cvs)) if cvs else 0.0

    return {
        "n_total": n_total,
        "nu_ext_hz": float(nu_ext),
        "mean_rate_hz": mean_rate_hz,
        "mean_cv_isi": mean_cv_isi,  # ~1.0 => irregular (AI regime); «1 => regular
        "n_recorded": n_rec,
        "n_spikes": int(times.size),
    }
