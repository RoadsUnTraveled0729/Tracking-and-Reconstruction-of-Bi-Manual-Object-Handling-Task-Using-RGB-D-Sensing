"""Stage 3: fit the wrist-to-box-center offset from R4's carry segments.

Inputs: the R4 filtered landmark CSV, the R4 filtered object-world
CSV, and scene_calibration_r4.json - never the old recording's fit.
Uses the vendored carry/grip core (eval/offset/carry.py). The fit is
per hand, on held frames only (marker measured AND box carried AND
this hand nearest AND wrist sample raw).

Also recomputes the subject's segment lengths from R4 (the sphere
fallback in stage 5 needs the forearm lengths) and compares them with
the pinned R1 values.

Usage:
    python eval/offset/fit_offset.py [--stem STEM] [--calib PATH]

Outputs eval/reports/<stem>_offset_fit.json and _offset_fit.png.
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
import carry
import paths

PINNED_R1_FOREARM = {"forearm_R": 0.185, "forearm_L": 0.232}


def load_tracks(stem, calib_path):
    calib = json.loads(Path(calib_path).read_text())
    world = carry.LeveledWorld(calib)
    lm = pd.read_csv(paths.MP_OUT / f"{stem}_landmarks_filtered.csv")
    ofil = pd.read_csv(paths.object_world_filtered(stem))
    n = min(len(lm), len(ofil))
    lm, ofil = lm.iloc[:n], ofil.iloc[:n]
    obj, R_obj = world.object_world(
        ofil[["unity_px", "unity_py", "unity_pz"]].to_numpy(),
        ofil[["unity_ex", "unity_ey", "unity_ez"]].to_numpy())
    det = ofil["detected"].to_numpy() == 1
    wr = {s: world.wrist_world(
        lm[[f"{s}_wrist_x", f"{s}_wrist_y", f"{s}_wrist_z"]].to_numpy())
        for s in ("left", "right")}
    wrist_flag = {s: lm[f"{s}_wrist_flag"].to_numpy()
                  for s in ("left", "right")}
    t = ofil["time_s"].to_numpy()
    return calib, world, lm, obj, R_obj, det, wr, wrist_flag, t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R4_STEM)
    ap.add_argument("--calib", default=str(paths.r4_calib()))
    args = ap.parse_args()
    stem = args.stem

    calib, world, lm, obj, R_obj, det, wr, wrist_flag, t = \
        load_tracks(stem, args.calib)
    n = len(obj)
    center = world.box_center(obj, R_obj)

    # Motion envelope from the stage-1 inspection (manipulation phase);
    # holding is classified per hand independently (E-005/E-006) - the
    # vendored R1 nearest-wrist rule misassigns during the occluded
    # hand-over.
    insp = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_inspection.json").read_text())
    envelope = insp["phases"]["manipulation"]
    carried = carry.rest_referenced_carried(obj, world, envelope)
    fit = {}
    for side in ("left", "right"):
        f_ok = carry.forearm_ok(lm, side)
        hold = carry.holding_mask(center, wr[side], wrist_flag[side], det,
                                  carried, f_ok)
        d_loc = np.einsum("nij,ni->nj", R_obj, wr[side] - obj)
        if hold.sum() == 0:
            fit[side] = {"hold": hold, "mu": None, "sd": None,
                         "d_loc": d_loc,
                         "resid": np.full(n, np.nan)}
            continue
        mu = d_loc[hold].mean(axis=0)
        sd = d_loc[hold].std(axis=0)
        pred = obj + np.einsum("nij,j->ni", R_obj, mu)
        fit[side] = {"hold": hold, "mu": mu, "sd": sd, "d_loc": d_loc,
                     "resid": np.linalg.norm(pred - wr[side], axis=1)}

    carry_segs = []
    idx = np.flatnonzero(carried)
    if idx.size:
        brk = np.flatnonzero(np.diff(idx) > 1)
        starts = np.r_[idx[0], idx[brk + 1]]
        stops = np.r_[idx[brk], idx[-1]]
        carry_segs = [[int(a), int(b)] for a, b in zip(starts, stops)]

    segs = carry.seg_lengths(lm)

    report = {
        "stem": stem,
        "calib": args.calib,
        "frames": n,
        "carried_frames": int(carried.sum()),
        "carry_segments": carry_segs,
        "hold_radius_m": carry.HOLD_RADIUS,
        "neither_hand_measurable_frames": int(
            (carried & ~fit["left"]["hold"] & ~fit["right"]["hold"]).sum()),
        "per_hand": {},
        "segment_lengths_m": {k: round(v, 3) for k, v in segs.items()},
        "pinned_r1_forearm_m": PINNED_R1_FOREARM,
    }
    print(f"=== {stem}: grip fit on carry segments ===")
    print(f"  carried on {int(carried.sum())}/{n} frames, "
          f"{len(carry_segs)} segments")
    for side in ("left", "right"):
        f = fit[side]
        if f["mu"] is None:
            print(f"  {side}-holding: no held frames")
            report["per_hand"][side] = None
            continue
        hold = f["hold"]
        r = f["resid"][hold]
        mag_center = np.linalg.norm(wr[side] - center, axis=1)[hold]
        report["per_hand"][side] = {
            "held_frames": int(hold.sum()),
            "mu_cm": [round(float(v) * 100, 1) for v in f["mu"]],
            "std_cm": [round(float(v) * 100, 1) for v in f["sd"]],
            "resid_median_cm": round(float(np.median(r)) * 100, 1),
            "resid_p95_cm": round(float(np.percentile(r, 95)) * 100, 1),
            "wrist_to_center_median_cm":
                round(float(np.median(mag_center)) * 100, 1),
            "wrist_to_center_p95_cm":
                round(float(np.percentile(mag_center, 95)) * 100, 1),
        }
        print(f"  {side}-holding ({int(hold.sum())} frames): "
              f"mu ({f['mu'][0]*100:+.1f}, {f['mu'][1]*100:+.1f}, "
              f"{f['mu'][2]*100:+.1f}) cm, std ({f['sd'][0]*100:.1f}, "
              f"{f['sd'][1]*100:.1f}, {f['sd'][2]*100:.1f}) cm; "
              f"residual median {np.median(r)*100:.1f} cm, "
              f"p95 {np.percentile(r, 95)*100:.1f} cm")
    print("  segment lengths (m):",
          {k: round(v, 3) for k, v in segs.items()})
    for k, pinned in PINNED_R1_FOREARM.items():
        print(f"  {k}: R4 {segs[k]:.3f} m vs pinned R1 {pinned:.3f} m "
              f"(delta {abs(segs[k]-pinned)*100:.1f} cm)")

    paths.EVAL_REPORTS.mkdir(parents=True, exist_ok=True)
    out_json = paths.EVAL_REPORTS / f"{stem}_offset_fit.json"
    out_json.write_text(json.dumps(report, indent=1))
    print(f"[+] {out_json}")

    # --- plot-first rendering ---
    fig, axes = plt.subplots(3, 1, figsize=(13, 9), sharex=True)
    ax = axes[0]
    for side, c in (("left", "tab:red"), ("right", "tab:blue")):
        mag = np.linalg.norm(wr[side] - center, axis=1)
        ax.plot(t, mag * 100, c=c, lw=0.8, label=f"{side} wrist")
        hold = fit[side]["hold"]
        ax.plot(t[hold], mag[hold] * 100, ".", c=c, ms=2)
    for a, b in carry_segs:
        ax.axvspan(t[a], t[b], color="k", alpha=0.06)
    ax.set_ylabel("|wrist - box center| (cm)")
    ax.set_ylim(0, 60)
    ax.legend(fontsize=8)
    ax.set_title(f"{stem}: offset magnitude (dots = held frames, "
                 "shading = carried)")
    ax = axes[1]
    for side, ls in (("left", "-"), ("right", "--")):
        d = fit[side]["d_loc"]
        hold = fit[side]["hold"]
        for j, (axname, c) in enumerate(zip(("x", "normal", "z"),
                                            ("tab:green", "tab:orange",
                                             "tab:purple"))):
            y = np.where(hold, d[:, j], np.nan)
            ax.plot(t, y * 100, ls, c=c, lw=0.9,
                    label=f"{side} {axname}" if side == "left" else None)
    ax.set_ylabel("object-frame offset (cm)")
    ax.legend(fontsize=8, ncol=3)
    ax = axes[2]
    for k, c in (("forearm_R", "tab:blue"), ("forearm_L", "tab:red")):
        a_, b_ = ("right_elbow", "right_wrist") if k == "forearm_R" \
            else ("left_elbow", "left_wrist")
        pa = lm[[f"{a_}_x", f"{a_}_y", f"{a_}_z"]].to_numpy()
        pb = lm[[f"{b_}_x", f"{b_}_y", f"{b_}_z"]].to_numpy()
        L = np.linalg.norm(pa - pb, axis=1)
        ax.plot(t, L * 100, c=c, lw=0.8, label=k)
        ax.axhline(segs[k] * 100, c=c, ls=":", lw=1)
    ax.set_ylabel("forearm length (cm)")
    ax.set_xlabel("time (s)")
    ax.set_ylim(0, 50)
    ax.legend(fontsize=8)
    fig.tight_layout()
    out_png = paths.EVAL_REPORTS / f"{stem}_offset_fit.png"
    fig.savefig(out_png, dpi=120)
    print(f"[+] {out_png}")


if __name__ == "__main__":
    main()
