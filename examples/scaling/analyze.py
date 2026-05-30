"""Turn brn_scaling run manifests into a scaling table + plot.

Usage:
    python analyze.py outputs/brn_scaling            # point at the experiment's run root
    python analyze.py outputs/brn_scaling --out scaling.png

Auto-detects the regime: if total network size is constant across runs it reports
STRONG scaling (speedup + parallel efficiency); if it grows with thread count it
reports WEAK scaling (efficiency = T1 / Tp, ideal = 1).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_runs(root: Path) -> list[dict]:
    runs = []
    for mf in sorted(root.rglob("manifest.json")):
        m = json.loads(mf.read_text())
        r = m.get("returned") or {}
        if "n_threads" in r and "total_time_s" in r:
            runs.append(r)
    # one row per thread count (keep the fastest if duplicates)
    by_p: dict[int, dict] = {}
    for r in runs:
        p = r["n_threads"]
        if p not in by_p or r["total_time_s"] < by_p[p]["total_time_s"]:
            by_p[p] = r
    return [by_p[p] for p in sorted(by_p)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path, help="run root, e.g. outputs/brn_scaling")
    ap.add_argument("--out", type=Path, default=Path("scaling.png"))
    args = ap.parse_args()

    runs = load_runs(args.root)
    if not runs:
        print(f"No brn_scaling manifests under {args.root}")
        return 1

    sizes = {r["n_total"] for r in runs}
    weak = len(sizes) > 1
    regime = "WEAK" if weak else "STRONG"

    base = runs[0]
    t1, p1 = base["total_time_s"], base["n_threads"]

    print(f"\n{regime} scaling  ({len(runs)} points, baseline p={p1})\n")
    hdr = f"{'threads':>7} {'N':>9} {'build_s':>9} {'sim_s':>9} {'total_s':>9} "
    hdr += f"{'efficiency':>11}" if weak else f"{'speedup':>8} {'efficiency':>11}"
    print(hdr)
    xs, ys_speedup, ys_eff = [], [], []
    for r in runs:
        p = r["n_threads"]
        speedup = t1 / r["total_time_s"]  # vs baseline threads
        if weak:
            eff = t1 / r["total_time_s"]  # ideal weak: time constant -> eff 1
            line = (
                f"{p:>7} {r['n_total']:>9} {r['build_time_s']:>9.3f} "
                f"{r['sim_time_s']:>9.3f} {r['total_time_s']:>9.3f} {eff:>11.3f}"
            )
        else:
            eff = speedup / (p / p1)  # ideal strong: speedup = p/p1
            line = (
                f"{p:>7} {r['n_total']:>9} {r['build_time_s']:>9.3f} "
                f"{r['sim_time_s']:>9.3f} {r['total_time_s']:>9.3f} {speedup:>8.2f} {eff:>11.3f}"
            )
        print(line)
        xs.append(p)
        ys_speedup.append(speedup)
        ys_eff.append(eff)

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 2 if not weak else 1, figsize=(10, 4) if not weak else (5, 4))
        axes = ax if not weak else [ax]
        if not weak:
            axes[0].plot(xs, ys_speedup, "o-", label="measured")
            axes[0].plot(xs, [x / p1 for x in xs], "k--", label="ideal")
            axes[0].set(xlabel="threads", ylabel="speedup", title="Strong scaling — speedup")
            axes[0].legend()
            axes[1].plot(xs, ys_eff, "o-")
            axes[1].axhline(1.0, ls="--", c="k")
            axes[1].set(
                xlabel="threads",
                ylabel="parallel efficiency",
                ylim=(0, 1.1),
                title="Strong scaling — efficiency",
            )
        else:
            axes[0].plot(xs, ys_eff, "o-")
            axes[0].axhline(1.0, ls="--", c="k")
            axes[0].set(
                xlabel="threads (N grows ∝ threads)",
                ylabel="weak efficiency (T₁/Tₚ)",
                ylim=(0, 1.2),
                title="Weak scaling",
            )
        fig.tight_layout()
        fig.savefig(args.out, dpi=130)
        print(f"\nPlot -> {args.out}")
    except ImportError:
        print("\n(matplotlib not installed — table only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
