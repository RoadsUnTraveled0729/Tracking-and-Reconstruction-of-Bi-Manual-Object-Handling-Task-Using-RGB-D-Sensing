#!/usr/bin/env python3
"""Trails for the Unity scene (supervisor C36 reading (b), decision D9,
user direction 2026-09-07 "do it if you can").

Writes the three trajectories of Figure 7.8 as polylines in DISPLAY AXES
(the local frame of the "ArucoWorld" node of the Unity scene, which the
receiver levels by the calibrated gravity and drops to the floor), so
that Unity/Assets/Scripts/TrajectoryTrails.cs can draw them as trails
inside the reconstruction during an unattended capture
(eval/unity_check/run_unity_capture.py):

  reference  the reference path of the cube, start -> W1 -> W2 -> W3
             (eval/reports/r6b_waypoints.json), static;
  cube       the tracked marker origin of the cube, one point per
             detected frame (the clean object track's unity columns,
             the same values the object record streams);
  wrist      the right wrist placed by the kinematic model from the
             recovery angles, one point per frame, exactly the points
             of make_ch7_wrist_traj_fig.py (fk_wrist on
             eval/output/recovery_r6b/angles_recovery.csv, carried into
             the levelled world and back out of the levelling here).

The levelled world of the evaluation is G applied to display axes
(eval/offset/carry.LeveledWorld.level), and the scene's ArucoWorld
rotation is the same FromToRotation(gravity, up), so display = G^T times
levelled and the trails land on the drawn cube and desk.

Outputs: /tmp/r5_trails.txt (read by TrajectoryTrails.cs at Play start)
         eval/reports/unity_check_r6b_trails/trails.txt (the tracked record)
Run:     python writing/v8/condensed/scripts/make_ch7_trails.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[4]
for sub in ("eval/common", "eval/gt", "eval/offset", "eval/failure",
            "eval/inspect", "v1/kinematics"):
    sys.path.insert(0, str(REPO / sub))
import eval_rail_scenario as ers            # noqa: E402
import recovery_core as rc                  # noqa: E402
from moving_window_check import fk_wrist    # noqa: E402
from root_frame import unity_from_sensor    # noqa: E402
import paths                                # noqa: E402 (eval/common)

STEM = "recording_20260831_065553"
ANGLES = REPO / "eval" / "output" / "recovery_r6b" / "angles_recovery.csv"
WP = REPO / "eval" / "reports" / "r6b_waypoints.json"
OUT_TMP = Path("/tmp/r5_trails.txt")
OUT_REC = REPO / "eval" / "reports" / "unity_check_r6b_trails" / "trails.txt"   # tracked record (eval/output is ignored by git)

ANGLE_COLS = ["root_ex", "root_ey", "root_ez", "Rsh_y", "Rsh_z", "Rsh_tau",
              "Rel_y", "Rel_z", "Lsh_y", "Lsh_z", "Lsh_tau", "Lel_y", "Lel_z"]
FLIP = np.array([1.0, -1.0, 1.0])

# colours of Figure 7.8 (matplotlib tab colours), width in metres
STYLE = {"reference": ((0.84, 0.15, 0.16), 0.010),
         "cube": ((0.17, 0.63, 0.17), 0.008),
         "wrist": ((0.12, 0.47, 0.71), 0.008)}

inp = rc.build_inputs(STEM)
world, lm, seg_len = inp["world"], inp["lm_df"], inp["seg_len"]
GT = world.G.T                                     # levelled -> display axes

# ---- reference path (levelled world, metres) -> display axes
wp = json.loads(WP.read_text())["waypoints"]
ref_lev = np.array([wp[k] for k in ("start", "W1", "W2", "W3")])
ref = (GT @ ref_lev.T).T

# ---- cube marker origin, display axes straight from the clean track
df = pd.read_csv(paths.object_world_filtered(STEM))
u = df[["unity_px", "unity_py", "unity_pz"]].apply(pd.to_numeric, errors="coerce").to_numpy(float)
ok = np.isfinite(u).all(axis=1) & (df["detected"].to_numpy() == 1)
cube = u[ok]
cube_frames = df["frame"].to_numpy(int)[ok]
# the same points through the evaluation's levelling and back, as a check
lev = world.level(cube)
back = (GT @ lev.T).T
assert np.abs(back - cube).max() < 1e-9

# ---- right wrist through the kinematic model (make_ch7_wrist_traj_fig.py)
ang_df = pd.read_csv(ANGLES)
n = min(len(ang_df), inp["n"])
angles = ang_df[ANGLE_COLS].to_numpy(float)[:n]
frames = ang_df["frame"].to_numpy(int)[:n]
Lu, Lf = seg_len["upper_arm_R"], seg_len["forearm_R"]
sh_cam = lm[["right_shoulder_x", "right_shoulder_y", "right_shoulder_z"]].to_numpy(float)[:n]
sh = np.array([unity_from_sensor(v) for v in sh_cam])
wr = np.full((n, 3), np.nan)
for i in range(n):
    if not np.isfinite(sh[i]).all() or not np.isfinite(angles[i]).all():
        continue
    w_sol = fk_wrist(angles, i, sh, Lu, Lf, "right")
    wr[i] = world.wrist_world((w_sol * FLIP)[None, :])[0]
okw = np.isfinite(wr).all(axis=1)
wrist = (GT @ wr[okw].T).T
wrist_frames = frames[okw]

lines = ["# trails in display axes (ArucoWorld local frame), metres; "
         "path <name> <r> <g> <b> <width_m> <static|frames>, then p <x> <y> <z> <frame>"]


def emit(name, pts, fr):
    (r, g, b), w = STYLE[name]
    lines.append(f"path {name} {r:.2f} {g:.2f} {b:.2f} {w:.3f} {'frames' if fr is not None else 'static'}")
    for k, p in enumerate(pts):
        f = int(fr[k]) if fr is not None else -1
        lines.append(f"p {p[0]:.4f} {p[1]:.4f} {p[2]:.4f} {f}")


emit("reference", ref, None)
emit("cube", cube, cube_frames)
emit("wrist", wrist, wrist_frames)
text = "\n".join(lines) + "\n"
OUT_TMP.write_text(text)
OUT_REC.parent.mkdir(parents=True, exist_ok=True)
OUT_REC.write_text(text)
print(f"reference {len(ref)} points; cube {len(cube)} points (frames {cube_frames.min()}..{cube_frames.max()}); "
      f"wrist {len(wrist)} points (frames {wrist_frames.min()}..{wrist_frames.max()})")
print("display-axes reference path:", np.round(ref, 3).tolist())
print("wrote", OUT_TMP, "and", OUT_REC)
