#!/usr/bin/env python3
"""Chapter 8 figures: where the live output differs from the offline pass
on the rail recording (Chapter 8 rewrite, 2026-09-07).

Two figures, no accuracy statistics printed on either:
  ch8_fig_traces.png    the right elbow flexion and shoulder elevation of
                        the offline recovery pass (angles_recovery.csv) and
                        of the live run (v2_person_dump_r6b_full.csv) on the
                        same frame axis, in three windows: the lift onto the
                        rail (the causal filter lags the zero-phase chain),
                        the natural wrist gap (both paths rebuild the wrist
                        from the object, with different grip offsets), and
                        the release at the end of the take (the live grip
                        tracker keeps the wrist anchored after the offline
                        state machine has released it). Bands mark the frames
                        on which each path reports the right elbow as
                        constrained. Chosen windows (2026-09-07 scan of the
                        per-frame differences): the start of the take, where
                        the offline mask rebuilt the arm on frames 7 to 24
                        while the live path held it, so the low-flexion twist
                        hold froze twists about 42 degrees apart for the rest
                        of the take; the lift and the onset of the wrist gap,
                        where the live path starts rebuilding at frame 537
                        and the offline pass at 550; and the gap itself,
                        where the two grip offsets (episode mean offline,
                        running mean live) put the rebuilt elbow up to about
                        24 degrees apart.
  ch8_fig_overlays.png  the colour frame with the offline chain and the live
                        chain (shoulder, elbow, wrist by forward kinematics
                        from each path's angles, on the measured shoulder of
                        the frame) at three frames, one per window.
  ch8_compare.json      the windows, the frames and, for the writer only,
                        the per-window median and largest angle differences.

The merger of the live run held no person tick mid-run (its 29 held ticks
are the warm-up and the tail), so no hold or bridge case is drawn.

Run: python writing/v8/condensed/scripts/make_ch8_compare_figs.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

REPO = Path(__file__).resolve().parents[4]
for sub in ("eval/common", "eval/gt", "eval/offset", "eval/failure",
            "eval/inspect", "v1/kinematics"):
    sys.path.insert(0, str(REPO / sub))
import recovery_core as rc                       # noqa: E402
from moving_window_check import fk_wrist         # noqa: E402
from check_v1_overlay import fk_arm_dirs         # noqa: E402
from carry import recompose_zxy                  # noqa: E402
from root_frame import unity_from_sensor         # noqa: E402

STEM = "recording_20260831_065553"
FIG_DIR = REPO / "writing" / "v8" / "condensed" / "figures"
SRC = FIG_DIR / "src"
OUT_TR = FIG_DIR / "ch8_fig_traces.png"
OUT_OV = FIG_DIR / "ch8_fig_overlays.png"
OUT_JS = FIG_DIR / "ch8_compare.json"
OFF = REPO / "eval" / "output" / "recovery_r6b" / "angles_recovery.csv"
LIVE = REPO / "v2" / "output" / "v2_person_dump_r6b_full.csv"
META = REPO / "eval" / "labels" / "frames_r6b" / "meta.json"

COLS = ["root_ex", "root_ey", "root_ez", "Rsh_y", "Rsh_z", "Rsh_tau",
        "Rel_y", "Rel_z", "Lsh_y", "Lsh_z", "Lsh_tau", "Lel_y", "Lel_z"]
FLIP = np.array([1.0, -1.0, 1.0])

off = pd.read_csv(OFF).set_index("frame")
live = pd.read_csv(LIVE).set_index("frame")
live_ang = live[[f"a{k}" for k in range(13)]].to_numpy(float)
off_ang = off[COLS].to_numpy(float)
frames = off.index.to_numpy(int)
assert (live.index.to_numpy(int) == frames).all()
off_con = off["tag_3"].to_numpy(int) == 2          # right elbow constrained
live_con = live["tag_3"].to_numpy(int) == 2
off_rec = off["tag_3"].to_numpy(int) == 2
live_rec = live["rec_right"].to_numpy(int) == 1     # object estimate reached the solver


def wrap(d):
    return (np.asarray(d, float) + 180.0) % 360.0 - 180.0



def _runs(idx):
    """Consecutive runs of frame numbers as (first, last) pairs."""
    idx = np.asarray(idx, int)
    if len(idx) == 0:
        return []
    cuts = np.where(np.diff(idx) > 1)[0]
    starts = np.r_[idx[0], idx[cuts + 1]]
    ends = np.r_[idx[cuts], idx[-1]]
    return list(zip(starts, ends))


def _bands(ax, fr, mask, fc, hatch, label):
    first = True
    for s0, s1 in _runs(fr[mask]):
        ax.axvspan(s0 - 0.5, s1 + 0.5, facecolor=fc, edgecolor="0.4" if hatch else "none",
                   hatch=hatch, lw=0.0, alpha=0.6 if fc != "none" else 1.0,
                   label=label if first else None)
        first = False


WINDOWS = [("start of the take", 0, 60),
           ("lift and gap onset", 470, 560),
           ("natural wrist gap", 540, 650)]
ANGLES = [("Rel_y", 6, "right elbow flexion (deg)"),
          ("Rsh_tau", 5, "right shoulder twist (deg)")]

# ---------------------------------------------------------------- traces
fig, axes = plt.subplots(len(ANGLES), len(WINDOWS), figsize=(12.6, 6.2),
                         sharex="col")
report = {"stem": STEM, "windows": []}
for j, (name, f0, f1) in enumerate(WINDOWS):
    sel = (frames >= f0) & (frames <= f1)
    w = {"name": name, "frames": [f0, f1], "angles": {}}
    for i, (col, k, label) in enumerate(ANGLES):
        ax = axes[i, j]
        a_off = off_ang[sel, k]
        a_live = live_ang[sel, k]
        fr = frames[sel]
        # bands: offline constrained (grey), live constrained (hatched amber)
        _bands(ax, fr, off_con[sel], "0.82", None, "offline: elbow rebuilt")
        _bands(ax, fr, live_con[sel], "none", "//", "live: elbow rebuilt")
        ax.plot(fr, a_off, color="tab:blue", lw=1.6, label="offline pass")
        ax.plot(fr, a_live, color="tab:orange", lw=1.4, ls="--", label="live path")
        if i == 0:
            ax.set_title(f"{name}, frames {f0} to {f1}", fontsize=10)
        if j == 0:
            ax.set_ylabel(label)
        if i == len(ANGLES) - 1:
            ax.set_xlabel("frame")
        ax.grid(True, lw=0.4, alpha=0.5)
        d = np.abs(wrap(a_off - a_live))
        w["angles"][col] = {"median_abs_diff_deg": round(float(np.nanmedian(d)), 1),
                            "max_abs_diff_deg": round(float(np.nanmax(d)), 1),
                            "frame_of_max": int(fr[int(np.nanargmax(d))])}
    w["offline_constrained_frames"] = int(off_con[sel].sum())
    w["live_constrained_frames"] = int(live_con[sel].sum())
    w["live_object_estimate_frames"] = int(live_rec[sel].sum())
    report["windows"].append(w)
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
proxies = [Patch(facecolor="0.82", edgecolor="none", alpha=0.6, label="offline pass: elbow rebuilt"),
           Patch(facecolor="none", edgecolor="0.4", hatch="//", label="live path: elbow rebuilt"),
           Line2D([], [], color="tab:blue", lw=1.6, label="offline pass"),
           Line2D([], [], color="tab:orange", lw=1.4, ls="--", label="live path")]
fig.legend(handles=proxies, loc="lower center", ncol=4, fontsize=9, frameon=False)
plt.subplots_adjust(left=0.07, right=0.99, top=0.93, bottom=0.14, wspace=0.22, hspace=0.12)
plt.savefig(OUT_TR, dpi=170)
plt.close(fig)
print("saved", OUT_TR)

# ---------------------------------------------------------------- overlays
inp = rc.build_inputs(STEM)
lm, seg_len = inp["lm_df"], inp["seg_len"]
Lu, Lf = seg_len["upper_arm_R"], seg_len["forearm_R"]
K = json.loads(META.read_text())["intrinsics"]
sh_cam = lm[["right_shoulder_x", "right_shoulder_y", "right_shoulder_z"]].to_numpy(float)
sh_sol = np.array([unity_from_sensor(v) for v in sh_cam])


def chain(angles, i):
    R_root = recompose_zxy(angles[i, :3])
    up, fo = fk_arm_dirs(angles[i, 3:6], angles[i, 6:8], "right")
    e = sh_sol[i] + Lu * (R_root @ up)
    wv = e + Lf * (R_root @ fo)
    return np.array([sh_sol[i], e, wv])


def project(P_sol):
    P = P_sol * FLIP                         # back to the camera frame
    u = K["fx"] * P[:, 0] / P[:, 2] + K["ppx"]
    v = K["fy"] * P[:, 1] / P[:, 2] + K["ppy"]
    return u, v


OV_FRAMES = [(18, "start of the take"), (548, "onset of the wrist gap"),
             (595, "inside the wrist gap")]
fig, axes = plt.subplots(1, 3, figsize=(12.6, 3.9))
report["overlay_frames"] = []
for ax, (f, moment) in zip(axes, OV_FRAMES):
    cand = SRC / f"r6b_frame{f:05d}.png"
    if not cand.exists():
        cand = REPO / "eval" / "labels" / "frames_r6b" / f"f{f:05d}.png"
    img = mpimg.imread(cand)
    ax.imshow(img)
    i = int(np.where(frames == f)[0][0])
    for A, col, lab, ls in ((off_ang, "tab:blue", "offline pass", "-"),
                            (live_ang, "tab:orange", "live path", "--")):
        P = chain(A, i)
        u, v = project(P)
        ax.plot(u, v, color=col, lw=2.4, ls=ls, marker="o", ms=5, label=lab)
    ax.set_xlim(0, img.shape[1]); ax.set_ylim(img.shape[0], 0)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(f"frame {f}, {moment}", fontsize=10)
    d_w = float(np.linalg.norm(chain(off_ang, i)[2] - chain(live_ang, i)[2]) * 100)
    report["overlay_frames"].append({"frame": f, "moment": moment,
                                     "wrist_offline_vs_live_cm": round(d_w, 1),
                                     "offline_elbow_constrained": bool(off_con[i]),
                                     "live_elbow_constrained": bool(live_con[i]),
                                     "live_object_estimate": bool(live_rec[i])})
axes[0].legend(loc="lower left", fontsize=9)
plt.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.02, wspace=0.03)
plt.savefig(OUT_OV, dpi=170)
plt.close(fig)
print("saved", OUT_OV)

# hold or bridge case check on the merger dump
it = pd.read_csv(REPO / "v2" / "output" / "v2_integrate_dump_r6b_full.csv")
held = it[it.p_state == 2]
report["merger_person_held_ticks"] = int(len(held))
report["merger_person_held_tau_range_s"] = [round(float(held.tau.min()), 2), round(float(held.tau.max()), 2)]
report["merger_person_held_midrun"] = int(((held.tau > 1.0) & (held.tau < 29.0)).sum())
OUT_JS.write_text(json.dumps(report, indent=1))
print(json.dumps(report, indent=1))
