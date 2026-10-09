#!/usr/bin/env python3
"""Trails of the two-hand rail take (r7, supervisor round 6 C50, E-034)
for the Chapter 7 presentation renderer, in DISPLAY AXES (the local
frame of the scene's ArucoWorld node), the same convention and the same
function chain as make_ch7_trails.py uses for the recording of
Chapter 2, extended to the left wrist:

  reference   the reference path start -> W1 -> W2 -> W3
              (eval/reports/r7_waypoints.json), static;
  cube        the tracked marker origin, one point per detected frame
              (the clean object track's unity columns);
  wrist       the model RIGHT wrist by forward kinematics of the
              recovery angles (eval/output/recovery_r7/
              angles_recovery.csv), the measured right shoulder and the
              take's calibrated lengths;
  wrist_left  the model LEFT wrist, the same way.

This script writes only the tracked record eval/reports/unity_check_r7/
trails.txt; it never arms /tmp/r5_trails.txt (TrajectoryTrails.cs), so
it is safe to run while a sensor-view capture is in progress. The
render path is ch7_trail_data.write_view_config(alias="r7") and
render_ch7_trails.py --alias r7.

Run: python writing/v8/condensed/scripts/make_ch7_handover_trails.py
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
import recovery_core as rc                  # noqa: E402
from moving_window_check import fk_wrist    # noqa: E402
from root_frame import unity_from_sensor    # noqa: E402
import paths                                # noqa: E402 (eval/common)

STEM = paths.R7_STEM
ALIAS = paths.ALIAS[STEM]
ANGLES = REPO / "eval" / "output" / f"recovery_{ALIAS}" / "angles_recovery.csv"
WP = REPO / "eval" / "reports" / f"{ALIAS}_waypoints.json"
OUT_REC = REPO / "eval" / "reports" / f"unity_check_{ALIAS}" / "trails.txt"

ANGLE_COLS = ["root_ex", "root_ey", "root_ez", "Rsh_y", "Rsh_z", "Rsh_tau",
              "Rel_y", "Rel_z", "Lsh_y", "Lsh_z", "Lsh_tau", "Lel_y", "Lel_z"]
FLIP = np.array([1.0, -1.0, 1.0])

# colours as in make_ch7_trails.py; the left wrist in purple (the
# presentation renderer applies its own colours by state)
STYLE = {"reference": ((0.84, 0.15, 0.16), 0.010),
         "cube": ((0.17, 0.63, 0.17), 0.008),
         "wrist": ((0.12, 0.47, 0.71), 0.008),
         "wrist_left": ((0.58, 0.40, 0.74), 0.008)}


def main():
    inp = rc.build_inputs(STEM)
    world, lm, seg_len = inp["world"], inp["lm_df"], inp["seg_len"]
    GT = world.G.T                                 # levelled -> display axes

    wp = json.loads(WP.read_text())["waypoints"]
    ref_lev = np.array([wp[k] for k in ("start", "W1", "W2", "W3")])
    ref = (GT @ ref_lev.T).T

    df = pd.read_csv(paths.object_world_filtered(STEM))
    u = df[["unity_px", "unity_py", "unity_pz"]].apply(pd.to_numeric, errors="coerce").to_numpy(float)
    ok = np.isfinite(u).all(axis=1) & (df["detected"].to_numpy() == 1)
    cube = u[ok]
    cube_frames = df["frame"].to_numpy(int)[ok]
    ang_df = pd.read_csv(ANGLES)
    n = min(len(ang_df), inp["n"])
    angles = ang_df[ANGLE_COLS].to_numpy(float)[:n]
    frames = ang_df["frame"].to_numpy(int)[:n]
    out = {}
    # the same points the hand-over analysis holds, as a check
    ho = pd.read_csv(REPO / "eval" / "reports" / f"{ALIAS}_handover.csv")
    for side, key, name in (("right", "R", "wrist"), ("left", "L", "wrist_left")):
        Lu, Lf = seg_len[f"upper_arm_{key}"], seg_len[f"forearm_{key}"]
        sh_cam = lm[[f"{side}_shoulder_x", f"{side}_shoulder_y", f"{side}_shoulder_z"]].to_numpy(float)[:n]
        sh = np.array([unity_from_sensor(v) for v in sh_cam])
        wr = np.full((n, 3), np.nan)
        for i in range(n):
            if not np.isfinite(sh[i]).all() or not np.isfinite(angles[i]).all():
                continue
            w_sol = fk_wrist(angles, i, sh, Lu, Lf, side)
            wr[i] = world.wrist_world((w_sol * FLIP)[None, :])[0]
        okw = np.isfinite(wr).all(axis=1)
        out[name] = ((GT @ wr[okw].T).T, frames[okw])
        ref_fk = ho[[f"fk_{side}_x", f"fk_{side}_y", f"fk_{side}_z"]].to_numpy(float)[:n]
        assert np.nanmax(np.abs(ref_fk[okw] - wr[okw])) < 1e-3   # the csv is written to 4 decimals

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
    emit("wrist", *out["wrist"])
    emit("wrist_left", *out["wrist_left"])
    OUT_REC.parent.mkdir(parents=True, exist_ok=True)
    OUT_REC.write_text("\n".join(lines) + "\n")
    print(f"reference {len(ref)} points; cube {len(cube)} points (frames {cube_frames.min()}..{cube_frames.max()}); "
          f"wrist {len(out['wrist'][0])} points; wrist_left {len(out['wrist_left'][0])} points")
    print("display-axes reference path:", np.round(ref, 3).tolist())
    print("wrote", OUT_REC)


if __name__ == "__main__":
    main()
