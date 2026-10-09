"""Validate the L24 root-frame construction and Unity Euler decode on real data.

Loads the filtered landmark CSV (RealSense sensor space), maps to Unity space
(x, -y, z), builds the root frame two ways (corrected vs. user sketch), and
decodes Unity ZXY-applied Euler angles. A person standing facing the camera
should decode to approximately (x=0, y=180, z=0) with the corrected build.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from root_frame import (build_root_frame, euler_unity_zxy, normalize,
                        recompose_zxy, unity_from_sensor)

DEFAULT_CSV = (Path(__file__).resolve().parent.parent / "mediapipe" / "output"
               / "recording_20260328_021733_landmarks_filtered.csv")
CSV = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV


def unity(df, name):
    """Sensor space -> Unity space: (x, -y, z)."""
    return unity_from_sensor(df[[f"{name}_x", f"{name}_y", f"{name}_z"]].to_numpy())


build_corrected = build_root_frame


def build_sketch(p23, p24, p12):
    """The user's unverified sketch: X=24->23, Y=X x (24->12), Z=X x Y."""
    x = normalize(p23 - p24)
    y = normalize(np.cross(x, p12 - p24))
    z = np.cross(x, y)
    return np.stack([x, y, z], axis=-1)


def main():
    df = pd.read_csv(CSV)
    df = df[df["has_pose"] == 1].reset_index(drop=True)
    p23, p24, p12 = unity(df, "left_hip"), unity(df, "right_hip"), unity(df, "right_shoulder")

    # --- synthetic reference pose: ideal upright person facing the sensor ---
    #   right hip on person's right (-X), left hip +X, shoulder above right hip
    q24 = np.array([[-0.15, 0.95, 1.70]])
    q23 = np.array([[+0.15, 0.95, 1.70]])
    q12 = np.array([[-0.18, 1.40, 1.70]])
    R_ref = build_corrected(q23, q24, q12)[0]
    e_ref = euler_unity_zxy(R_ref)
    R_ref_sketch = build_sketch(q23, q24, q12)[0]
    e_ref_sketch = euler_unity_zxy(R_ref_sketch)
    print("== Synthetic upright reference pose ==")
    print("corrected R (cols r,u,f):\n", np.round(R_ref, 4))
    print("corrected Euler (x,y,z) deg:", np.round(e_ref, 2), " expected ~ (0, 180, 0)")
    print("sketch    Euler (x,y,z) deg:", np.round(e_ref_sketch, 2))

    # --- real recording ---
    R = build_corrected(p23, p24, p12)
    det = np.linalg.det(R)
    orth = np.abs(np.einsum("nij,nik->njk", R, R) - np.eye(3)).max()
    e = euler_unity_zxy(R)
    print("\n== Real recording ({} frames with pose) ==".format(len(df)))
    print(f"det(R): min {det.min():.6f} max {det.max():.6f}   (proper rotation = +1)")
    print(f"max |R^T R - I|: {orth:.2e}   (orthonormality)")
    print("Euler mean  (x,y,z):", np.round(e.mean(axis=0), 2))
    print("Euler std   (x,y,z):", np.round(e.std(axis=0), 2))
    print("Euler frame0       :", np.round(e[0], 2))
    print("Euler range y      : [{:.1f}, {:.1f}]".format(e[:, 1].min(), e[:, 1].max()))

    # --- round-trip: decode -> recompose must reproduce R exactly ---
    errs = [np.abs(recompose_zxy(e[i]) - R[i]).max() for i in range(0, len(df), 50)]
    print(f"\nround-trip max |recompose(euler) - R|: {max(errs):.2e}")

    # gimbal-lock decode self-test on synthetic x=+90 and x=-90 rotations
    for xdeg in (90.0, -90.0):
        Rg = recompose_zxy(np.array([xdeg, 37.0, 0.0]))
        eg = euler_unity_zxy(Rg)
        rt = np.abs(recompose_zxy(eg) - Rg).max()
        print(f"gimbal x={xdeg:+.0f}: decoded {np.round(eg,2)}  round-trip err {rt:.2e}")


if __name__ == "__main__":
    main()
