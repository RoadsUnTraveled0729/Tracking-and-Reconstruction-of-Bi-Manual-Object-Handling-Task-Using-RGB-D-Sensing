#!/usr/bin/env python3
"""Charts for the AKC comparison, read from eval/akc_comparison/results/*.csv
only (run_akc_comparison.py writes them). Plain matplotlib, labels only.

Run:  /home/luo/anaconda3/bin/python eval/akc_comparison/charts.py
"""
import sys

sys.dont_write_bytecode = True

from pathlib import Path  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

RES = Path(__file__).resolve().parent / "results"
META = {"Software": None, "Creator": None}   # stable PNG bytes
DPI = 120


def save(fig, name):
    fig.tight_layout()
    fig.savefig(RES / name, dpi=DPI, metadata=META)
    plt.close(fig)
    print(f"OK: wrote results/{name}")


def grouped(ax, labels, series, ylabel):
    x = np.arange(len(labels))
    w = 0.8 / max(1, len(series))
    for i, (name, vals) in enumerate(series.items()):
        ax.bar(x + (i - (len(series) - 1) / 2) * w, vals, w, label=name)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylabel(ylabel)
    ax.legend()


def chart_p1():
    df = pd.read_csv(RES / "p1_synthetic_elbow.csv")
    d = df[(df.window == "pooled") & (df["mask"] == "M-E")
           & (df.mask_mode == "MASK_ALL") & (df.joint == "elbow")]
    order = ["hold-last", "KF-only", "AKC-literal", "AKC-ray", "AKC-EKF",
             "ours-memory", "ours-IK"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, ref in zip(axes, ("R-self", "R-meas")):
        g = d[d.reference == ref].set_index("method").reindex(order)
        grouped(ax, order, {"median": g["median"].to_numpy(),
                            "rmse_3d": g["rmse_3d"].to_numpy()},
                "elbow error (cm)")
        ax.set_title(f"P1 r7 right, M-E MASK_ALL, 3 windows pooled, {ref}")
    save(fig, "chart_p1_elbow_error.png")


def chart_outage():
    df = pd.read_csv(RES / "p1_outage_sweep.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, ref in zip(axes, ("R-self", "R-meas")):
        for m, g in df[df.reference == ref].groupby("method", sort=False):
            ax.plot(g.duration, g["median"], marker="o", label=m)
        ax.set_xlabel("outage duration (frames, anchored at 445)")
        ax.set_ylabel("median elbow error (cm)")
        ax.set_title(f"P1 outage sweep, r7 right, M-E MASK_ALL, {ref}")
        ax.legend()
    save(fig, "chart_p1_outage.png")


def chart_p2():
    a = pd.read_csv(RES / "p2a_wrist_synthetic.csv")
    b = pd.read_csv(RES / "p2b_natural_labels.csv")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.4))
    d = a[(a.joint == "wrist") & (a.reference == "R-self")]
    wins = list(dict.fromkeys(d.window))
    methods = list(dict.fromkeys(d.method))
    series = {w: d[d.window == w].set_index("method").reindex(methods)
              ["median"].to_numpy() for w in wins}
    grouped(axes[0], methods, series, "median wrist error (cm)")
    axes[0].set_title("P2a r7 right S1_arm, R-self, per window")
    s = b[(b.kind == "summary") & (b.group == "failure")
          & (b.input.isin(["pinned", "vis0"]))]
    methods = ["ours-hold_fk", "ours-plain_fk", "ours-recovery_fk",
               "ours-recovered", "AKC-ray", "AKC-ray-fm", "AKC-hybrid",
               "AKC-hybrid-fm"]
    series = {side: s[s.side == side].set_index("method").reindex(methods)
              ["median"].to_numpy() for side in ("right", "left")}
    grouped(axes[1], methods, series, "median |wrist - label| (cm)")
    axes[1].set_title("P2b r5 labelled failure frames (right n=4, left n=16)")
    save(fig, "chart_p2_wrist.png")


def chart_arm_length():
    df = pd.read_csv(RES / "arm_length_range.csv")
    d = df[df.region == "full"]
    methods = ["raw", "KF-only", "AKC-literal", "AKC-ray", "ours"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, seg in zip(axes, ("forearm", "upper")):
        labels, series = methods, {}
        for rec in ("r5", "r6b", "r7"):
            for side in ("right", "left"):
                g = d[(d.recording == rec) & (d.side == side)]
                series[f"{rec} {side}"] = g.set_index("method").reindex(
                    methods)[f"{seg}_range_cm"].to_numpy()
        grouped(ax, labels, series, f"{seg} length range (cm)")
        ax.set_title(f"{seg} length range, full unmasked runs")
    save(fig, "chart_arm_length.png")


def chart_sweep():
    df = pd.read_csv(RES / "kf_sweep.csv")
    d = df[(df.method == "AKC") & (df.reference == "R-self")]
    labels = [f"{p}={v}" for p, v in zip(d.param, d.value)]
    fig, ax = plt.subplots(figsize=(8, 7))
    y = np.arange(len(d))
    ax.barh(y, d["median"].to_numpy())
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel("median elbow error (cm), 3 windows pooled, R-self")
    ax.set_title("AKC sweep, r7 right, M-E MASK_ALL (reported, not tuned)")
    save(fig, "chart_kf_sweep.png")


def main():
    chart_p1()
    for fn, f in ((chart_outage, "p1_outage_sweep.csv"),
                  (chart_p2, "p2b_natural_labels.csv"),
                  (chart_arm_length, "arm_length_range.csv"),
                  (chart_sweep, "kf_sweep.csv")):
        if (RES / f).exists():
            fn()


if __name__ == "__main__":
    main()
