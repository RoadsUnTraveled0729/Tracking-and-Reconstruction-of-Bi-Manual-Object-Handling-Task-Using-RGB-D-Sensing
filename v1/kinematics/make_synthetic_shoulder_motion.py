"""Generate synthetic datasets with KNOWN right-arm joint angles.

Four datasets (30 fps, 30 s, 900 frames each), written in SENSOR space with
the extractor's CSV layout plus a ground-truth angle CSV:

1. shoulder_only  — torso fixed at the reference pose (0,180,0); the right
   arm moves through scripted (θy, θz, θτ) trajectories with the elbow held
   at 90° flexion (ey = -90, forearm rest ∝ local +z) so twist is observable.
2. shoulder_torso — the SAME arm trajectory composed with a moving root
   (yaw/pitch/roll sweeps overlapping the arm phases), so the solve is
   tested under a non-trivial, time-varying parent frame.
3. elbow_only     — torso and shoulder swing fixed; elbow flexion ey sweeps,
   then shoulder twist rotates the flexion plane, then both together.
4. arm_full       — torso + shoulder (all three) + elbow flexion all moving
   simultaneously; the 24-30 s phase has every angle nonzero at once.
5. arm_both       — torso + BOTH arms (mirror-convention left angles, §9),
   left on deliberately different phases from the right so no symmetry
   masks a sign error.

Shoulder trajectory (deviations from rest = arm out to the right):
  0-8 s   θy ±60°  (horizontal swing, forward/back)
  8-16 s  θz ±60°  (elevation up/down, stays clear of the ±90° gimbal)
  16-24 s θτ ±80°  (axial twist, internal/external rotation)
  24-30 s all three combined, smaller amplitudes
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from root_frame import recompose_zxy, wrap_deg
from shoulder import recompose_shoulder, _rx, _ry, _rz  # noqa: F401 (rx unused)

FPS = 30
DURATION_S = 30.0

TORSO = {
    "left_shoulder":  (-0.19, 0.50, 0.00),
    "right_shoulder": (+0.19, 0.50, 0.00),
    "left_elbow":     (-0.50, 0.50, 0.00),
    "left_wrist":     (-0.78, 0.50, 0.00),
    "left_hip":       (-0.15, 0.00, 0.00),
    "right_hip":      (+0.15, 0.00, 0.00),
}
L_UA, L_FA = 0.31, 0.28            # upper-arm / forearm lengths (m)
HIP_MID_UNITY = np.array([0.0, -0.30, 1.70])
COLUMNS = ["left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
           "left_wrist", "right_wrist", "left_hip", "right_hip"]
X, Z = np.array([1.0, 0, 0]), np.array([0, 0, 1.0])


def shoulder_traj(t):
    """Ground-truth (θy, θz, θτ) in degrees at time t."""
    ty = tz = tw = 0.0
    if t < 8.0:
        ty = 60.0 * np.sin(2 * np.pi * t / 8.0)
    elif t < 16.0:
        tz = 60.0 * np.sin(2 * np.pi * (t - 8.0) / 8.0)
    elif t < 24.0:
        tw = 80.0 * np.sin(2 * np.pi * (t - 16.0) / 8.0)
    else:
        u = 2 * np.pi * (t - 24.0) / 6.0
        ty, tz, tw = 40.0 * np.sin(u), 30.0 * np.sin(2 * u), 45.0 * np.cos(u)
    return ty, tz, tw


def elbow_traj_only(t):
    """(shoulder (ty,tz,tw), elbow ey) for the elbow_only dataset."""
    ty = tz = tw = 0.0
    ey = -90.0
    if t < 10.0:
        ey = -80.0 + 70.0 * np.cos(2 * np.pi * t / 10.0)   # -10 .. -150
    elif t < 20.0:
        tw = 80.0 * np.sin(2 * np.pi * (t - 10.0) / 10.0)  # plane rotates
    else:
        u = 2 * np.pi * (t - 20.0) / 10.0
        ey = -90.0 + 45.0 * np.cos(u)
        tw = 60.0 * np.sin(u)
    return (ty, tz, tw), ey


def elbow_traj_full(t):
    """Elbow flexion ey for the arm_full dataset (never exactly straight)."""
    return -90.0 + 50.0 * np.sin(2 * np.pi * t / 7.0)      # -140 .. -40


def left_traj(t):
    """LEFT arm (θy, θz, θτ, ey), phases distinct from the right arm."""
    ty = 45.0 * np.sin(2 * np.pi * t / 9.0)
    tz = 35.0 * np.sin(2 * np.pi * t / 5.5)
    tw = 40.0 * np.sin(2 * np.pi * t / 6.5)
    ey = -70.0 + 40.0 * np.sin(2 * np.pi * t / 8.0)         # -110 .. -30
    return ty, tz, tw, ey


def left_arm_points(p11, ty, tz, tw, ey):
    """L13/L15 person-frame points from mirror-convention left angles:
    world chain = M·R·M = flip signs of y/z angles, keep twist; rest -x̂."""
    ry, rz = np.radians(-ty), np.radians(-tz)
    rt, rey = np.radians(tw), np.radians(-ey)
    R_sw = _ry(ry) @ _rz(rz)
    p13 = p11 + L_UA * (R_sw @ -X)
    R_full = R_sw @ _rx(rt) @ _ry(rey)
    p15 = p13 + L_FA * (R_full @ -X)
    return p13, p15


def root_traj(t):
    """Root Euler deviations (dx, dyaw, dz) in degrees at time t."""
    dx = dyaw = dz = 0.0
    if t < 8.0:
        dyaw = 25.0 * np.sin(2 * np.pi * t / 8.0)
    elif t < 16.0:
        dx = 15.0 * np.sin(2 * np.pi * (t - 8.0) / 8.0)
    elif t < 24.0:
        dz = 15.0 * np.sin(2 * np.pi * (t - 16.0) / 8.0)
    else:
        u = 2 * np.pi * (t - 24.0) / 6.0
        dyaw, dx, dz = 12.0 * np.sin(u), 8.0 * np.sin(2 * u), 8.0 * np.cos(u)
    return dx, dyaw, dz


def generate(name, with_torso, out_dir, elbow_mode="fixed90", left_moving=False):
    n = int(FPS * DURATION_S)
    rows, truth = [], []
    for i in range(n):
        t = i / FPS
        if elbow_mode == "elbow_only":
            (ty, tz, tw), ey = elbow_traj_only(t)
        else:
            ty, tz, tw = shoulder_traj(t)
            ey = elbow_traj_full(t) if elbow_mode == "full" else -90.0
        dx, dyaw, dz = root_traj(t) if with_torso else (0.0, 0.0, 0.0)
        e_root = np.array([dx, 180.0 + dyaw, dz])
        R_root = recompose_zxy(e_root)

        R_swing = _ry(np.radians(ty)) @ _rz(np.radians(tz))
        R_sh = recompose_shoulder((ty, tz, tw))
        local = dict(TORSO)
        p12 = np.array(TORSO["right_shoulder"])
        p14 = p12 + L_UA * (R_swing @ X)                   # upper arm: swing only
        p16 = p14 + L_FA * (R_sh @ (_ry(np.radians(ey)) @ X))  # forearm: + elbow
        local["right_elbow"], local["right_wrist"] = p14, p16

        lty, ltz, ltw, ley = left_traj(t) if left_moving else (0.0, 0.0, 0.0, 0.0)
        p11 = np.array(TORSO["left_shoulder"])
        p13, p15 = left_arm_points(p11, lty, ltz, ltw, ley)
        local["left_elbow"], local["left_wrist"] = p13, p15

        pts = np.array([local[k] for k in COLUMNS])
        p_unity = HIP_MID_UNITY + pts @ R_root.T
        p_sensor = p_unity * np.array([1.0, -1.0, 1.0])

        row = {"frame": i, "time_s": round(t, 4), "has_pose": 1}
        for j, lname in enumerate(COLUMNS):
            row[f"{lname}_x"] = p_sensor[j, 0]
            row[f"{lname}_y"] = p_sensor[j, 1]
            row[f"{lname}_z"] = p_sensor[j, 2]
            row[f"{lname}_vis"] = 1.0
        rows.append(row)
        truth.append({"frame": i, "time_s": round(t, 4),
                      "root_x": wrap_deg(e_root[0]),
                      "root_y": wrap_deg(e_root[1]),
                      "root_z": wrap_deg(e_root[2]),
                      "sh_y": ty, "sh_z": tz, "sh_twist": tw,
                      "elbow_y": ey, "elbow_z": 0.0,
                      "l_sh_y": lty, "l_sh_z": ltz, "l_sh_twist": ltw,
                      "l_elbow_y": ley, "l_elbow_z": 0.0})

    lm = out_dir / f"{name}_landmarks.csv"
    tr = out_dir / f"{name}_truth.csv"
    pd.DataFrame(rows).to_csv(lm, index=False)
    pd.DataFrame(truth).to_csv(tr, index=False)
    print(f"wrote {lm} ({n} frames)")
    print(f"wrote {tr}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-dir", type=Path,
                    default=Path(__file__).resolve().parent / "output")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    generate("shoulder_only", with_torso=False, out_dir=args.out_dir)
    generate("shoulder_torso", with_torso=True, out_dir=args.out_dir)
    generate("elbow_only", with_torso=False, out_dir=args.out_dir,
             elbow_mode="elbow_only")
    generate("arm_full", with_torso=True, out_dir=args.out_dir,
             elbow_mode="full")
    generate("arm_both", with_torso=True, out_dir=args.out_dir,
             elbow_mode="full", left_moving=True)


if __name__ == "__main__":
    main()
