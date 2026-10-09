#!/usr/bin/env python3
"""Chapter 7 figure of the hand-over on the rail (supervisor round 6,
C50; E-034): the marker origin along the rail against the recorded
frame with the hand at the cube, and the slide seen from above and from
the side with the fitted rail line, the marker origin and BOTH model
wrists.

Inputs are the pinned analysis outputs of the two-hand take, read and
drawn without recomputation:
  eval/reports/r7_handover.csv   per frame: part (right / handover /
                                 left), hand at the cube, position along
                                 the rail, perpendicular deviation, the
                                 forward-kinematics wrists of the recovery
                                 solve (levelled world, metres)
  eval/reports/r7_handover.json  the hand-over frames and the per-part
                                 statistics quoted in the text
  eval/output/recovery_r7/angles_recovery.csv   the joint-group states
                                 (tag_1/tag_3 right swing and elbow,
                                 tag_4/tag_6 left), as Figure 7.7 uses
  eval/reports/r7_waypoints.json the fitted rail line
The wrist colours follow Figure 7.7 for the right wrist (blue measured,
orange rebuilt, grey held) and add purple (measured) and pink (rebuilt)
for the left wrist, the pair the Unity trail figure of the same take
uses; a held group is grey on either wrist. The fitted rail line is the
total-least-squares line of eval_rail_scenario.py between its first and
last slide sample, projected into each view (it has a small plan-view
yaw, so a constant-depth segment would misplace it).

Output: writing/v9/figures/ch7_fig_handover_traj.png
Run:    python writing/v9/scripts/make_ch7_handover_fig.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

REPO = Path(__file__).resolve().parents[3]
for sub in ("eval/common", "eval/gt", "eval/offset"):
    sys.path.insert(0, str(REPO / sub))
import paths                       # noqa: E402
import eval_rail_scenario as ers   # noqa: E402
FIG_DIR = REPO / "writing" / "v9" / "figures"
OUT = FIG_DIR / "ch7_fig_handover_traj.png"
HO_CSV = REPO / "eval" / "reports" / "r7_handover.csv"
HO_JSON = REPO / "eval" / "reports" / "r7_handover.json"
ANGLES = REPO / "eval" / "output" / "recovery_r7" / "angles_recovery.csv"
WP = REPO / "eval" / "reports" / "r7_waypoints.json"

COL = {"right": {"measured": "tab:blue", "rebuilt": "tab:orange", "held": "0.45"},
       "left": {"measured": "tab:purple", "rebuilt": "tab:pink", "held": "0.45"}}
HAND_COL = {"right": "tab:blue", "both": "tab:purple", "left": "tab:green",
            "none": "0.6"}


def states(tags, side):
    """The three states of Figure 7.7 (make_ch7_wrist_traj_fig.py): held when
    the swing or elbow group is held, rebuilt when either is constrained."""
    swing, elbow = (1, 3) if side == "right" else (4, 6)
    s = np.full(len(tags), "measured", dtype=object)
    s[(tags[:, swing] == 1) | (tags[:, elbow] == 1)] = "held"
    s[(tags[:, swing] == 2) | (tags[:, elbow] == 2)] = "rebuilt"
    return s


def segments(ax, xy, frames, keep, st, side):
    for i in range(len(xy) - 1):
        if not (keep[i] and keep[i + 1]) or frames[i + 1] != frames[i] + 1:
            continue
        if not np.isfinite(xy[i:i + 2]).all():
            continue
        ax.plot(xy[i:i + 2, 0], xy[i:i + 2, 1], color=COL[side][st[i]], lw=1.1)


def main():
    df = pd.read_csv(HO_CSV)
    ho = json.loads(HO_JSON.read_text())
    wp = json.loads(WP.read_text())
    tags = pd.read_csv(ANGLES)[[f"tag_{k}" for k in range(7)]].to_numpy(int)[:len(df)]
    frames = df["frame"].to_numpy(int)
    part = df["part"].fillna("").to_numpy(object)   # empty = not on the rail band
    hand = df["hand"].fillna("none").to_numpy(object)
    on_rail = part != ""
    along = df["along_cm"].to_numpy(float)
    perp = df["perp_cm"].to_numpy(float)
    f_in, f_out = ho["hand_over"]["left_hand_arrives_frame"], ho["hand_over"]["right_hand_leaves_frame"]
    first_task = wp["track_turns"]["parked_frames"][1] + 1

    wr = {s: df[[f"fk_{s}_x", f"fk_{s}_y", f"fk_{s}_z"]].to_numpy(float) * 100 for s in ("right", "left")}
    at_cube = {"right": np.isin(hand, ["right", "both"]) & on_rail,
               "left": np.isin(hand, ["left", "both"]) & on_rail}
    st = {s: states(tags, s) for s in ("right", "left")}
    # the levelled marker origin and the fitted rail line, as the analysis
    # computed them (eval_rail_scenario: total least squares over the slide
    # samples); the line is drawn between its first and last sample
    track = ers.load_track(paths.R7_STEM)
    seg = ers.segment(track)
    xyz = track["xyz"][:len(df)] * 100
    c, d, along_fit, _, _ = ers.fit_line(track["xyz"][seg["rail"]])
    ends = np.array([c + along_fit.min() * d, c + along_fit.max() * d]) * 100

    fig = plt.figure(figsize=(9.2, 7.4), layout="constrained")
    grid = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.25], hspace=0.12, wspace=0.18)

    # (a) along the rail against the frame, coloured by the hand at the cube
    ax = fig.add_subplot(grid[0, 0])
    sel = on_rail & (frames >= first_task)
    for h, c in HAND_COL.items():
        m = sel & (hand == h)
        ax.scatter(frames[m], along[m], s=3, color=c, label=None)
    ax.axvspan(f_in, f_out, color="0.92", zorder=0)
    ax.set_xlabel("Recorded frame", fontsize=11)
    ax.set_ylabel("Along the rail (cm)", fontsize=11)
    ax.set_title("(a) Marker origin along the rail", loc="left", fontsize=12)
    ax.grid(alpha=0.2)
    ax.tick_params(labelsize=10)
    ax.text(0.5 * (f_in + f_out), ax.get_ylim()[0] + 2, "hand-over", ha="center", fontsize=9, color="0.3")

    # (b) perpendicular deviation against the frame
    ax = fig.add_subplot(grid[0, 1])
    for h, c in HAND_COL.items():
        m = sel & (hand == h)
        ax.scatter(frames[m], perp[m], s=3, color=c)
    ax.axvspan(f_in, f_out, color="0.92", zorder=0)
    ax.set_xlabel("Recorded frame", fontsize=11)
    ax.set_ylabel("Distance to the rail line (cm)", fontsize=11)
    ax.set_title("(b) Marker origin off the fitted line", loc="left", fontsize=12)
    ax.grid(alpha=0.2)
    ax.tick_params(labelsize=10)

    # (c) and (d): the slide from above and from the side with both wrists
    m_on = xyz.copy()
    m_on[~on_rail] = np.nan
    for col, (dim, title, ylab) in enumerate(((2, "(c) Slide from above", "z (cm)"),
                                              (1, "(d) Slide from the side", "y (cm)"))):
        ax = fig.add_subplot(grid[1, col])
        ax.plot(ends[:, 0], ends[:, dim], color="0.2", ls="--", lw=1)
        ax.plot(m_on[:, 0], m_on[:, dim], color="tab:green", lw=1)
        for s in ("right", "left"):
            segments(ax, wr[s][:, [0, dim]], frames, at_cube[s], st[s], s)
        ax.set_title(title, loc="left", fontsize=12)
        ax.set_xlabel("x (cm)", fontsize=11)
        ax.set_ylabel(ylab, fontsize=11)
        ax.set_aspect("equal", adjustable="box")
        ax.grid(alpha=0.2)
        ax.tick_params(labelsize=10)

    handles = [Line2D([], [], marker="o", ls="", color=HAND_COL["right"], label="Right hand at the cube"),
               Line2D([], [], marker="o", ls="", color=HAND_COL["both"], label="Both hands at the cube"),
               Line2D([], [], marker="o", ls="", color=HAND_COL["left"], label="Left hand at the cube"),
               Line2D([], [], marker="o", ls="", color=HAND_COL["none"], label="No hand at the cube"),
               Line2D([], [], color="0.2", ls="--", label="Fitted rail line"),
               Line2D([], [], color="tab:green", label="Marker origin"),
               Line2D([], [], color=COL["right"]["measured"], label="Right wrist: measured input"),
               Line2D([], [], color=COL["right"]["rebuilt"], label="Right wrist: rebuilt"),
               Line2D([], [], color=COL["left"]["measured"], label="Left wrist: measured input"),
               Line2D([], [], color=COL["left"]["rebuilt"], label="Left wrist: rebuilt"),
               Line2D([], [], color="0.45", label="Either wrist: held")]
    fig.legend(handles=handles, loc="outside lower center", ncol=3, fontsize=9.5, frameon=False)
    fig.savefig(OUT, dpi=200, bbox_inches="tight", pad_inches=0.05)
    print("saved", OUT)


if __name__ == "__main__":
    main()
