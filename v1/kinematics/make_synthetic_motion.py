"""Generate a synthetic landmark dataset with KNOWN root rotations.

A rigid upper body (8 landmarks in the person's own frame) is rotated by a
scripted trajectory of Unity Euler angles, placed in front of a virtual
sensor, and written out in SENSOR space using the exact CSV layout of the
MediaPipe extractor. Because the injected angles are known, the whole
pipeline (sensor->Unity mapping, root-frame build, Euler decode) can be
verified against ground truth, and the animation can be compared visually
(matplotlib and the Unity rig must show the same motion).

Trajectory (30 fps, 30 s, 900 frames), deviations from the reference pose
(x=0, y=180, z=0 = standing upright facing the sensor):
  0-8 s   yaw   +/-30 deg   (turning left/right)
  8-16 s  pitch +/-20 deg   (bowing forward/back)
  16-24 s roll  +/-20 deg   (leaning right/left)
  24-30 s all three combined, smaller amplitudes
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from root_frame import recompose_zxy, wrap_deg

FPS = 30
DURATION_S = 30.0

# Landmark offsets in the person's own frame: columns [right, up, forward],
# meters, origin at the hip midpoint. Arms in T-pose so rotations read clearly.
BODY = {
    "left_shoulder":  (-0.19, 0.50, 0.00),
    "right_shoulder": (+0.19, 0.50, 0.00),
    "left_elbow":     (-0.50, 0.50, 0.00),
    "right_elbow":    (+0.50, 0.50, 0.00),
    "left_wrist":     (-0.78, 0.50, 0.00),
    "right_wrist":    (+0.78, 0.50, 0.00),
    "left_hip":       (-0.15, 0.00, 0.00),
    "right_hip":      (+0.15, 0.00, 0.00),
}
HIP_MID_UNITY = np.array([0.0, -0.30, 1.70])  # camera-relative, like real data


def trajectory(t):
    """Ground-truth Euler deviations (dx, dyaw, dz) in degrees at time t."""
    dx = dyaw = dz = 0.0
    if t < 8.0:
        dyaw = 30.0 * np.sin(2 * np.pi * t / 8.0)
    elif t < 16.0:
        dx = 20.0 * np.sin(2 * np.pi * (t - 8.0) / 8.0)
    elif t < 24.0:
        dz = 20.0 * np.sin(2 * np.pi * (t - 16.0) / 8.0)
    else:
        u = 2 * np.pi * (t - 24.0) / 6.0
        dyaw, dx, dz = 15.0 * np.sin(u), 10.0 * np.sin(2 * u), 10.0 * np.cos(u)
    return dx, dyaw, dz


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    out_dir = Path(__file__).resolve().parent / "output"
    ap.add_argument("--out-dir", type=Path, default=out_dir)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    local = np.array([BODY[k] for k in BODY])  # (8, 3)
    n = int(FPS * DURATION_S)
    rows, truth = [], []
    for i in range(n):
        t = i / FPS
        dx, dyaw, dz = trajectory(t)
        e = np.array([dx, 180.0 + dyaw, dz])
        R = recompose_zxy(e)
        p_unity = HIP_MID_UNITY + local @ R.T          # rotate, then place
        p_sensor = p_unity * np.array([1.0, -1.0, 1.0])  # Unity -> sensor (y flip)

        row = {"frame": i, "time_s": round(t, 4), "has_pose": 1}
        for j, name in enumerate(BODY):
            row[f"{name}_x"] = p_sensor[j, 0]
            row[f"{name}_y"] = p_sensor[j, 1]
            row[f"{name}_z"] = p_sensor[j, 2]
            row[f"{name}_vis"] = 1.0
        rows.append(row)
        truth.append({"frame": i, "time_s": round(t, 4),
                      "euler_x": wrap_deg(e[0]), "euler_y": wrap_deg(e[1]),
                      "euler_z": wrap_deg(e[2])})

    lm_path = args.out_dir / "synthetic_landmarks.csv"
    truth_path = args.out_dir / "synthetic_angles_truth.csv"
    pd.DataFrame(rows).to_csv(lm_path, index=False)
    pd.DataFrame(truth).to_csv(truth_path, index=False)
    print(f"wrote {lm_path} ({n} frames)")
    print(f"wrote {truth_path}")


if __name__ == "__main__":
    main()
