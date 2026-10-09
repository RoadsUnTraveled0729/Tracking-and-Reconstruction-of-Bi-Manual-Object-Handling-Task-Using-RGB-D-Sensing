"""Plot-first renderings for the stage-4 path analysis.

(a) Box-center trajectory in the desk-marker frame (three projections)
with dwell clusters marked; (b) speed histogram justifying the dwell
threshold; (c) speed vs time with dwell shading.

Usage: python eval/gt/plot_path.py [--stem STEM]
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "common"))
sys.path.insert(0, str(HERE.parents[0] / "offset"))
import carry
import paths
from analyze_gt_path import MIN_DUR_S, SMOOTH_WIN, V_THRESH
from fit_offset import load_tracks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R4_STEM)
    args = ap.parse_args()
    stem = args.stem

    calib, world, lm, obj_lev, R_lev, det, wr, wrist_flag, t = \
        load_tracks(stem, str(paths.r4_calib()))
    ofil = pd.read_csv(paths.object_world_filtered(stem))
    n = min(len(ofil), len(obj_lev))
    obj_u = ofil[["unity_px", "unity_py", "unity_pz"]].to_numpy()[:n]
    R_u = np.array([carry.recompose_zxy(e) for e in
                    ofil[["unity_ex", "unity_ey", "unity_ez"]].to_numpy()[:n]])
    center = obj_u + R_u @ np.array([0.0, -world.cube / 2.0, 0.0])
    insp = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_inspection.json").read_text())
    carried = carry.rest_referenced_carried(
        obj_lev[:n], world, insp["phases"]["manipulation"])
    rep = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_stage1_path.json").read_text())
    dwells = rep["dwells"]

    dt = np.gradient(t[:n])
    v = np.linalg.norm(np.gradient(center, axis=0) / dt[:, None], axis=1)
    v = np.convolve(v, np.ones(SMOOTH_WIN) / SMOOTH_WIN, mode="same")

    fig = plt.figure(figsize=(15, 9))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.3, 1])
    axs = [fig.add_subplot(gs[0, i]) for i in range(3)]
    pairs = [(0, 1, "x (right)", "y (up-ish)"),
             (0, 2, "x (right)", "z (fwd)"),
             (2, 1, "z (fwd)", "y (up-ish)")]
    for ax, (i, j, xl, yl) in zip(axs, pairs):
        ax.plot(center[~carried, i], center[~carried, j], ".", ms=1,
                color="0.75", label="not carried")
        ax.plot(center[carried, i], center[carried, j], ".", ms=1.5,
                color="tab:blue", label="carried")
        for k, d in enumerate(dwells):
            m = d["mean_xyz"]
            ax.plot(m[i], m[j], "o", ms=9, mfc="none", mec="tab:red", mew=2)
            ax.annotate(str(k), (m[i], m[j]), textcoords="offset points",
                        xytext=(6, 6), color="tab:red", fontsize=9)
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        ax.set_aspect("equal")
        ax.grid(alpha=0.3)
    axs[0].legend(fontsize=8, markerscale=4)
    axs[0].set_title("box center, desk-marker frame (m); "
                     "red = dwell clusters")

    ax = fig.add_subplot(gs[1, 0])
    ax.hist(v[carried] * 100, bins=80, range=(0, 40), color="tab:blue")
    ax.axvline(V_THRESH * 100, color="tab:red", ls="--",
               label=f"dwell threshold {V_THRESH*100:.0f} cm/s")
    ax.set_xlabel("smoothed speed (cm/s), carried frames")
    ax.set_ylabel("frames")
    ax.legend(fontsize=8)

    ax = fig.add_subplot(gs[1, 1:])
    ax.plot(t[:n], v * 100, lw=0.8)
    ax.axhline(V_THRESH * 100, color="tab:red", ls="--")
    for d in dwells:
        ax.axvspan(t[d["start"]], t[d["stop"]], color="tab:red", alpha=0.15)
    ax.set_xlabel("time (s)")
    ax.set_ylabel("speed (cm/s)")
    ax.set_ylim(0, 50)
    ax.set_title(f"box-center speed; shaded = detected dwells "
                 f"(>= {MIN_DUR_S} s below threshold)")

    fig.tight_layout()
    out = paths.EVAL_REPORTS / f"{stem}_path_overview.png"
    fig.savefig(out, dpi=120)
    print(f"[+] {out}")


if __name__ == "__main__":
    main()
