"""Brunel balanced random network — a scaling benchmark for NEST, as a labflow experiment.

The same experiment drives both kinds of scaling study; you choose by *how you sweep*:

  Strong scaling  — fix the problem, add cores:
      labflow sweep brn_scaling n_total_fixed=50000 threads=1,2,4,8,16,24,48

  Weak scaling    — grow the problem with the cores (fixed work per core):
      labflow sweep brn_scaling n_per_thread=2500 threads=1,2,4,8,16,24,48

Each run records build and simulate wall-clock times; `analyze.py` turns the run
manifests into speedup (strong) and efficiency (weak) curves.

Network: Brunel (2000) sparse random net of iaf_psc_delta neurons, 80% excitatory /
20% inhibitory, inhibition-dominated (g>4), mean-driven external Poisson (eta>1).
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from labflow import experiment


@dataclass
class ScalingConfig:
    # --- scaling controls ---
    threads: int = 1            # OpenMP threads (local_num_threads)
    n_per_thread: int = 2500    # WEAK scaling: total neurons = n_per_thread * threads
    n_total_fixed: int = 0      # STRONG scaling: if >0, use this fixed total (ignores n_per_thread)
    # --- network ---
    epsilon: float = 0.1        # connection probability (sparse random)
    g: float = 5.0              # relative inhibitory strength (J_inh = -g*J)
    eta: float = 2.0            # external rate as multiple of threshold rate
    J: float = 0.1              # excitatory PSP amplitude (mV)
    delay_ms: float = 1.5
    # --- neuron (Brunel iaf_psc_delta defaults) ---
    tau_m_ms: float = 20.0
    V_th_mV: float = 20.0
    V_reset_mV: float = 0.0
    t_ref_ms: float = 2.0
    C_m_pF: float = 250.0
    # --- simulation ---
    simulation_time_ms: float = 1000.0
    seed: int = 42


@experiment(config=ScalingConfig, tags=["nest", "benchmark", "scaling"])
def brn_scaling(cfg: ScalingConfig) -> dict:
    """Build + simulate a Brunel network; return sizes and wall-clock timings."""
    import nest

    n_total = cfg.n_total_fixed if cfg.n_total_fixed > 0 else cfg.n_per_thread * cfg.threads
    n_exc = (n_total * 4) // 5
    n_inh = n_total - n_exc
    c_exc = max(1, int(cfg.epsilon * n_exc))   # excitatory in-degree
    c_inh = max(1, int(cfg.epsilon * n_inh))   # inhibitory in-degree

    # External drive: rate relative to the network's threshold (rheobase) rate.
    nu_th = cfg.V_th_mV / (cfg.J * c_exc * cfg.tau_m_ms)      # kHz (mV / (mV*ms))
    nu_ext = cfg.eta * nu_th
    p_rate_hz = 1000.0 * nu_ext * c_exc                      # Poisson generator rate (Hz)

    nest.ResetKernel()
    nest.SetKernelStatus({
        "local_num_threads": cfg.threads,   # set BEFORE Create()
        "rng_seed": cfg.seed,
        "resolution": 0.1,
        "print_time": False,
        "overwrite_files": True,
    })

    neuron_params = {
        "tau_m": cfg.tau_m_ms, "V_th": cfg.V_th_mV, "V_reset": cfg.V_reset_mV,
        "t_ref": cfg.t_ref_ms, "C_m": cfg.C_m_pF, "E_L": 0.0, "V_m": 0.0,
    }

    # ---- build phase (timed) ----
    t0 = time.perf_counter()
    nest.SetDefaults("iaf_psc_delta", neuron_params)
    exc = nest.Create("iaf_psc_delta", n_exc)
    inh = nest.Create("iaf_psc_delta", n_inh)
    noise = nest.Create("poisson_generator", params={"rate": p_rate_hz})
    sr = nest.Create("spike_recorder")

    j_exc = cfg.J
    j_inh = -cfg.g * cfg.J
    nest.CopyModel("static_synapse", "exc", {"weight": j_exc, "delay": cfg.delay_ms})
    nest.CopyModel("static_synapse", "inh", {"weight": j_inh, "delay": cfg.delay_ms})

    nest.Connect(noise, exc, syn_spec="exc")
    nest.Connect(noise, inh, syn_spec="exc")
    # record from up to 50 excitatory neurons (rate estimate)
    n_rec = min(50, n_exc)
    nest.Connect(exc[:n_rec], sr)

    nest.Connect(exc, exc + inh, {"rule": "fixed_indegree", "indegree": c_exc}, "exc")
    nest.Connect(inh, exc + inh, {"rule": "fixed_indegree", "indegree": c_inh}, "inh")
    build_time_s = time.perf_counter() - t0

    # ---- simulate phase (timed) ----
    t1 = time.perf_counter()
    nest.Simulate(cfg.simulation_time_ms)
    sim_time_s = time.perf_counter() - t1

    n_events = nest.GetStatus(sr)[0]["n_events"]
    mean_rate_hz = n_events / (n_rec * cfg.simulation_time_ms / 1000.0) if n_rec else 0.0

    return {
        "n_total": int(n_total),
        "n_exc": int(n_exc),
        "n_inh": int(n_inh),
        "n_threads": int(cfg.threads),
        "build_time_s": round(build_time_s, 4),
        "sim_time_s": round(sim_time_s, 4),
        "total_time_s": round(build_time_s + sim_time_s, 4),
        "mean_rate_hz": round(mean_rate_hz, 3),
        "neurons_per_core": int(n_total / cfg.threads),
    }
