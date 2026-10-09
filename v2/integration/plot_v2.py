#!/usr/bin/env python3
# Filename: v2/integration/plot_v2.py
"""Plot the v2 merger's behaviour BEFORE any Unity run (repo rule,
DECISIONS 2026-07-19: plot in python before Unity).

Three panels from the --dump CSVs of a full bag run:
  1. object unity x over the whole session: measured pipeline samples as
     points, merger output as a line, held ticks red, bridge/blend amber
  2. zoom on one 3-frame occlusion (frames 547-549): hold, then the
     flagged blend ramp to reacquisition
  3. person angle a4 zoom: the steady-tick resampling between measured
     samples (the delay buffer replacing arrival-order re-emission)

Output: v2/output/v2_interp_plot.png
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

MEASURED, INTERP, HELD, BLEND = 0, 1, 2, 3


def main():
    out = ROOT / "v2/output"
    o = pd.read_csv(out / "v2_object_dump.csv")
    p = pd.read_csv(out / "v2_person_dump.csv")
    it = pd.read_csv(out / "v2_integrate_dump.csv")

    fig, axes = plt.subplots(3, 1, figsize=(11, 10))

    def draw_object(ax, sel):
        om = o[(o.live == 1)]
        ax.plot(om.time_s, om.ux, ".", color="0.55", markersize=3,
                label="measured samples (pipeline B)")
        states = it.o_state.to_numpy()
        for st, color, lbl in ((HELD, "tab:red", "held"),
                               (BLEND, "tab:orange", "blend")):
            m = it[states == st]
            ax.plot(m.tau, m.ox, "s", color=color, markersize=4,
                    label=f"{lbl} ticks")
        bridge = it[(it["flags"].to_numpy() & 32) > 0]
        ax.plot(bridge.tau, bridge.ox, "^", color="tab:orange",
                markersize=5, label="bridged dropout")
        ax.plot(it.tau, it.ox, "-", color="black", linewidth=0.8,
                label="merger output (30 Hz ticks)")
        ax.set_ylabel("object unity x (m)")
        if sel is not None:
            ax.set_xlim(sel)
            lo, hi = sel
            seg = it[(it.tau >= lo) & (it.tau <= hi)]
            if len(seg):
                pad = 0.15 * (seg.ox.max() - seg.ox.min() + 1e-3)
                ax.set_ylim(seg.ox.min() - pad, seg.ox.max() + pad)

    draw_object(axes[0], None)
    axes[0].set_title("Object track: merger output over measured samples "
                      "(full session)")
    axes[0].legend(loc="upper right", fontsize=8)

    draw_object(axes[1], (18.0, 18.7))
    axes[1].set_title("Zoom: 3-frame occlusion at frames 547-549 -- "
                      "hold (red), blend ramp (orange), reacquisition")

    ax = axes[2]
    ax.plot(p.time_s, p.a4, ".", color="0.55", markersize=4,
            label="measured samples (pipeline A)")
    ax.plot(it.tau, it.a4, "-", color="black", linewidth=0.8,
            label="merger output")
    pm = it[it.p_state == MEASURED]
    ax.plot(pm.tau, pm.a4, "o", markersize=4, fillstyle="none",
            color="tab:blue", label="measured-hit ticks")
    ax.set_xlim(13.0, 13.6)
    seg = it[(it.tau >= 13.0) & (it.tau <= 13.6)]
    if len(seg):
        pad = 0.15 * (seg.a4.max() - seg.a4.min() + 1e-3)
        ax.set_ylim(seg.a4.min() - pad, seg.a4.max() + pad)
    ax.set_ylabel("angle a4 (deg)")
    ax.set_xlabel("session time (s)")
    ax.set_title("Zoom: person angle resampled on the steady output tick")
    ax.legend(loc="upper right", fontsize=8)

    for ax in axes[:2]:
        ax.set_xlabel("session time (s)")
    fig.tight_layout()
    dst = out / "v2_interp_plot.png"
    fig.savefig(dst, dpi=140)
    print(f"[png] {dst}")


if __name__ == "__main__":
    main()
