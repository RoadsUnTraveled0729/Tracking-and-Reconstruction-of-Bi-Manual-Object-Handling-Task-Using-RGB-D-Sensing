#!/usr/bin/env python3
"""Chapter 7 figures: the wrist through the kinematic model in the world
frame (supervisor comments C35 and C36, reading (a)).

For every frame of the rail recording the right and left wrists are
placed by forward kinematics from the thirteen solved angles of the
recovery run (eval/output/recovery_r6b/angles_recovery.csv), the measured
shoulder position and the recording's calibrated segment lengths
(eval/failure/moving_window_check.fk_wrist, the same function the
synthetic-masking check uses). The solver-space result is carried into
the gravity-levelled desk world of Figure 7.1 (x along the rail, y up,
z away from the camera) by the same map that levels the landmarks
(eval/offset/carry.LeveledWorld.wrist_world), and drawn beside the
tracked object marker origin, the fitted rail line and the reference path of
eval/gt/eval_rail_scenario.py and make_ch7_rail_traj_fig.py.

The figures show trajectory consistency: the rail line is fitted to the
cube track, and the holding wrist sits at a grip offset from the cube,
so a wrist that runs parallel to the line at a steady offset is the
expected picture, not an independent accuracy measurement.

Outputs: writing/v8/condensed/figures/ch7_fig_wrist_traj.png
         writing/v8/condensed/figures/ch7_fig_combined.png
         writing/v8/condensed/figures/ch7_wrist_traj.json
Run:     python writing/v8/condensed/scripts/make_ch7_wrist_traj_fig.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[4]
for sub in ("eval/common", "eval/gt", "eval/offset", "eval/failure",
            "eval/inspect", "v1/kinematics"):
    sys.path.insert(0, str(REPO / sub))
import eval_rail_scenario as ers            # noqa: E402
import recovery_core as rc                  # noqa: E402
from moving_window_check import fk_wrist    # noqa: E402
from root_frame import unity_from_sensor    # noqa: E402

STEM = "recording_20260831_065553"
FIG_DIR = REPO / "writing" / "v8" / "condensed" / "figures"
OUT_TRAJ = FIG_DIR / "ch7_fig_wrist_traj.png"
OUT_COMB = FIG_DIR / "ch7_fig_combined.png"
OUT_JSON = FIG_DIR / "ch7_wrist_traj.json"
ANGLES = REPO / "eval" / "output" / "recovery_r6b" / "angles_recovery.csv"
WP = REPO / "eval" / "reports" / "r6b_waypoints.json"

ANGLE_COLS = ["root_ex", "root_ey", "root_ez", "Rsh_y", "Rsh_z", "Rsh_tau",
              "Rel_y", "Rel_z", "Lsh_y", "Lsh_z", "Lsh_tau", "Lel_y", "Lel_z"]
FLIP = np.array([1.0, -1.0, 1.0])

# ---------------------------------------------------------------- inputs
inp = rc.build_inputs(STEM)
world, lm, seg_len = inp["world"], inp["lm_df"], inp["seg_len"]
ang_df = pd.read_csv(ANGLES)
n = min(len(ang_df), inp["n"])
angles = ang_df[ANGLE_COLS].to_numpy(float)[:n]
tags = ang_df[[f"tag_{k}" for k in range(7)]].to_numpy(int)[:n]
frames = ang_df["frame"].to_numpy(int)[:n]

track = ers.load_track(STEM)
seg = ers.segment(track)
xyz = track["xyz"]                          # levelled marker centre, m
c, d, along, _, _ = ers.fit_line(xyz[seg["rail"]])
if d[0] < 0:
    d, along = -d, -along
ends = np.array([c + along.min() * d, c + along.max() * d])
wp = json.loads(WP.read_text())["waypoints"]
ref = np.array([wp[k] for k in ("start", "W1", "W2", "W3")])


def fk_side(side):
    """Forward-kinematics wrist of one side, levelled world, metres."""
    key = "R" if side == "right" else "L"
    Lu, Lf = seg_len[f"upper_arm_{key}"], seg_len[f"forearm_{key}"]
    sh_cam = lm[[f"{side}_shoulder_x", f"{side}_shoulder_y",
                 f"{side}_shoulder_z"]].to_numpy(float)[:n]
    sh = np.array([unity_from_sensor(v) for v in sh_cam])
    out = np.full((n, 3), np.nan)
    for i in range(n):
        if not np.isfinite(sh[i]).all() or not np.isfinite(angles[i]).all():
            continue
        w_sol = fk_wrist(angles, i, sh, Lu, Lf, side)
        out[i] = world.wrist_world((w_sol * FLIP)[None, :])[0]
    return out


wr_R = fk_side("right")
wr_L = fk_side("left")

# state of the right arm per frame from the group states
# (tag 1 = right shoulder swing, tag 3 = right elbow; 0 measured,
# 1 held, 2 constrained, the Chapter 6 order)
state = np.full(n, "measured", dtype=object)
state[(tags[:, 1] == 1) | (tags[:, 3] == 1)] = "held"
state[(tags[:, 1] == 2) | (tags[:, 3] == 2)] = "recovered"

# ---------------------------------------------------------------- numbers
rail_idx = np.asarray(seg["rail"], int)          # frame indices in the rail band
rail_frames = track["frame"][rail_idx]
sel = np.isin(frames, rail_frames)


def perp(P):
    v = P - c
    return np.linalg.norm(v - np.outer(v @ d, d), axis=1)


ok_R = sel & np.isfinite(wr_R).all(axis=1)
perp_R = perp(wr_R[ok_R]) * 100
cube_ok = np.isfinite(xyz).all(axis=1)
perp_cube = perp(xyz[rail_idx]) * 100
both = ok_R & cube_ok[:n]
offset = (wr_R[both] - xyz[:n][both]) * 100
numbers = {
    "stem": STEM,
    "frame": "gravity-levelled desk world (x along the rail, y up, z away from the camera), centimetres",
    "lengths_m": {k: seg_len[k] for k in ("upper_arm_R", "forearm_R", "upper_arm_L", "forearm_L")},
    "slide_frames": {"first": int(rail_frames.min()), "last": int(rail_frames.max()),
                     "n_cube": int(len(rail_idx)), "n_right_wrist": int(ok_R.sum())},
    "right_wrist_to_rail_line_cm": {"median": round(float(np.median(perp_R)), 1),
                                    "p95": round(float(np.percentile(perp_R, 95)), 1),
                                    "max": round(float(perp_R.max()), 1)},
    "cube_centre_to_rail_line_cm": {"median": round(float(np.median(perp_cube)), 1),
                                    "p95": round(float(np.percentile(perp_cube, 95)), 1)},
    "cube_to_right_wrist_offset_cm": {
        "mean_xyz": [round(float(v), 1) for v in offset.mean(axis=0)],
        "sd_xyz": [round(float(v), 1) for v in offset.std(axis=0)],
        "mean_distance": round(float(np.linalg.norm(offset, axis=1).mean()), 1),
        "sd_distance": round(float(np.linalg.norm(offset, axis=1).std()), 1)},
    "right_arm_states_on_slide": {s: int(((state == s) & sel).sum())
                                  for s in ("measured", "recovered", "held")},
    "right_arm_states_whole_take": {s: int((state == s).sum())
                                    for s in ("measured", "recovered", "held")},
}
assert numbers == json.loads(OUT_JSON.read_text()), "Existing evaluation values changed"
# Legacy JSON key names are retained to preserve the pinned report bytes.
# Both cube-named quantities refer to the marker origin, as load_track defines.
print(json.dumps(numbers, indent=1))

# ---------------------------------------------------------------- drawing
from draw_ch7_trajectories import draw

draw(FIG_DIR, wr_R, xyz[:n], frames, state, ref, ends, sel)
print("saved", OUT_TRAJ, "and", OUT_COMB)
