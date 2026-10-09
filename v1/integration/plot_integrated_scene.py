#!/usr/bin/env python3
# Filename: integration/plot_integrated_scene.py
"""Draw the integrated scene in Python BEFORE sending anything to Unity.

Renders, in the gravity-aligned desk world (the exact frame the Unity
receiver builds): the desk top, the wall, the floor, the sensor pose,
the object trajectory, both wrist trajectories, the pelvis track and the
person's root axes (right/up/forward). If something is physically wrong
(person not facing the desk, legs in the table, tilted geometry) it is
visible HERE, with numbers, before Unity ever gets the data.

Outputs:
  output/scene_preview.png     3D perspective + top view
  prints: person-facing angle vs the desk/sensor, desk-edge vs pelvis
          clearance, wall verticality — the sanity numbers.

Usage:
  python plot_integrated_scene.py [--stem recording_20260224_083945]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent

P = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]], float)
D = np.diag([1.0, -1.0, 1.0])
DESK_THICK, LEG_H = 0.03, 0.69


def recompose_zxy(deg):
    x, y, z = np.radians(np.asarray(deg, dtype=float))
    cx, sx, cy, sy, cz, sz = np.cos(x), np.sin(x), np.cos(y), np.sin(y), np.cos(z), np.sin(z)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


def from_to_rotation(a, b):
    v, c = np.cross(a, b), float(np.dot(a, b))
    s = np.linalg.norm(v)
    if s < 1e-12:
        return np.eye(3) if c > 0 else -np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]) / s
    return np.eye(3) + s * K + (1 - c) * (K @ K)


def mpl(p):
    """Unity scene coords -> matplotlib (X=right, Y=depth, Z=up)."""
    p = np.asarray(p)
    return p[..., [0, 2, 1]]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stem", default="recording_20260224_083945")
    args = ap.parse_args()

    calib = json.loads((HERE.parent / "aruco" / "output" / "scene_calibration.json").read_text())
    stream = pd.read_csv(HERE / "output" / "integrated_stream.csv")
    lm = pd.read_csv(HERE.parent / "mediapipe" / "output"
                     / f"{args.stem}_landmarks_filtered_v2.csv")

    T_dc = np.linalg.inv(np.array(calib["T_cam_desk"]))
    R_dc, t_dc = T_dc[:3, :3], T_dc[:3, 3]
    M = P @ R_dc @ D                      # person space -> world-unity (local)
    cam_pos = P @ t_dc
    R_cam_u = P @ R_dc @ P
    g = np.array(calib["scene_geometry"]["gravity_up_unity"])
    g /= np.linalg.norm(g)
    G = from_to_rotation(g, np.array([0.0, 1.0, 0.0]))  # gravity alignment
    geom = calib["scene_geometry"]
    drop = geom["origin_above_tabletop_m"]
    cube = geom["object_cube_size_m"]

    S = lambda p: (G @ np.atleast_2d(p).T).T.squeeze()  # local -> leveled scene

    # scene points -----------------------------------------------------------
    obj = stream[["opx", "opy", "opz"]].values
    live = stream.obj_live.values == 1
    pel = stream[["pel_x", "pel_y", "pel_z"]].values
    pel_s = S((M @ pel.T).T + cam_pos)
    obj_s = S(obj)
    wr = {}
    for side in ("left", "right"):
        w = lm[[f"{side}_wrist_x", f"{side}_wrist_y", f"{side}_wrist_z"]].values
        wr[side] = S((M @ (w * [1, -1, 1]).T).T + cam_pos)
    cam_s = S(cam_pos)
    # person root axes from the streamed root Euler (PA space)
    fwd_s, up_s = [], []
    for i in range(len(stream)):
        Rr = recompose_zxy(stream.loc[i, ["a0", "a1", "a2"]].values)
        fwd_s.append(S(M @ Rr[:, 2]))
        up_s.append(S(M @ Rr[:, 1]))
    fwd_s, up_s = np.array(fwd_s), np.array(up_s)

    # desk / wall / floor geometry (same construction as the receiver) -------
    on_plane = S(-g * drop)
    up = np.array([0.0, 1.0, 0.0])
    proj = lambda q: q - up * float(np.dot(q - on_plane, up))
    projO, projB = proj(S(np.zeros(3))), proj(obj_s[live][0])
    span = projB - projO
    x_ax = span / np.linalg.norm(span)
    z_ax = np.cross(x_ax, up)
    desk_near = projO - x_ax * 0.30
    desk_far = projB + x_ax * 0.05
    desk_c = (desk_near + desk_far) / 2

    def rect(center, a, b, la, lb):
        return np.array([center + a * la / 2 + b * lb / 2, center + a * la / 2 - b * lb / 2,
                         center - a * la / 2 - b * lb / 2, center - a * la / 2 + b * lb / 2,
                         center + a * la / 2 + b * lb / 2])

    desk_len = float(np.linalg.norm(desk_far - desk_near))
    desk_poly = rect(desk_c, x_ax, z_ax, desk_len, 1.4)
    wall_pos = S(np.array(calib["poses_world"]["wall"]["unity_position"]))
    Rw = np.array(calib["poses_world"]["wall"]["T_world"])[:3, :3]
    wall_x, wall_v = S(P @ Rw[:, 0]), S(P @ Rw[:, 1])   # width axis, vertical axis
    floor_y = float(np.dot(desk_c, up)) - DESK_THICK - LEG_H
    wall_h = float(np.dot(wall_pos, up)) - floor_y + 0.8
    wall_c = wall_pos + wall_v * (0.8 - wall_h / 2)
    wall_poly = rect(wall_c, wall_x, wall_v, 3.0, wall_h)
    floor_poly = rect(desk_c - up * (np.dot(desk_c, up) - floor_y),
                      x_ax, z_ax, 6.0, 6.0)

    # sanity numbers ---------------------------------------------------------
    print("=== sanity numbers (all in the leveled desk world) ===")
    wall_vert = np.degrees(np.arccos(np.clip(abs(np.dot(wall_v, up)), -1, 1)))
    print(f"wall in-plane vertical axis vs up : {wall_vert:.4f} deg (0 = plumb)")
    to_sensor = cam_s - pel_s
    to_sensor[:, 1] = 0
    to_sensor /= np.linalg.norm(to_sensor, axis=1, keepdims=True)
    fh = fwd_s.copy()
    fh[:, 1] = 0
    fh /= np.linalg.norm(fh, axis=1, keepdims=True)
    face_ang = np.degrees(np.arccos(np.clip(np.sum(fh * to_sensor, axis=1), -1, 1)))
    print(f"person forward vs pelvis->sensor  : mean {face_ang.mean():.1f} deg, "
          f"p95 {np.percentile(face_ang, 95):.1f} deg (small = facing desk/sensor)")
    up_tilt = np.degrees(np.arccos(np.clip(up_s @ up, -1, 1)))
    print(f"person up-axis vs gravity up      : mean {up_tilt.mean():.1f} deg, "
          f"max {up_tilt.max():.1f} deg")
    far_edge_d = np.dot(pel_s - desk_far[None, :], x_ax)
    print(f"pelvis beyond desk far edge       : min {far_edge_d.min()*100:+.1f} cm "
          f"(negative = legs INSIDE the desk footprint)")
    h_pel = pel_s @ up - np.dot(on_plane, up)
    print(f"pelvis height above tabletop      : {h_pel.min():+.3f}..{h_pel.max():+.3f} m")

    # figure -----------------------------------------------------------------
    fig = plt.figure(figsize=(16, 8))
    idx = np.linspace(0, len(stream) - 1, 8).astype(int)
    for spi, (elev, azim, title) in enumerate(
            [(22, -55, "perspective"), (88, -90, "top view")]):
        ax = fig.add_subplot(1, 2, spi + 1, projection="3d")
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
        for poly, col, al in ((floor_poly, "0.6", 0.25), (desk_poly, "peru", 0.55),
                              (wall_poly, "tan", 0.4)):
            q = mpl(poly)
            ax.add_collection3d(Poly3DCollection([q[:-1]], color=col, alpha=al))
            ax.plot(q[:, 0], q[:, 1], q[:, 2], color=col, lw=1)
        o = mpl(obj_s[live])
        ax.plot(o[:, 0], o[:, 1], o[:, 2], "-", color="orange", lw=1.5,
                label=f"object ({cube*1000:.0f} mm cube)")
        for side, col in (("left", "tab:blue"), ("right", "tab:red")):
            w = mpl(wr[side])
            ax.plot(w[:, 0], w[:, 1], w[:, 2], "-", color=col, lw=0.8,
                    alpha=0.8, label=f"{side} wrist")
        pm = mpl(pel_s)
        ax.plot(pm[:, 0], pm[:, 1], pm[:, 2], "-", color="k", lw=1.2, label="pelvis")
        for i in idx:
            a, f, u = mpl(pel_s[i]), mpl(fwd_s[i] * 0.35), mpl(up_s[i] * 0.35)
            ax.quiver(*a, *f, color="g", lw=2)
            ax.quiver(*a, *u, color="m", lw=1)
        c = mpl(cam_s)
        ax.scatter(*c, color="navy", s=60, marker="s", label="sensor")
        opt = mpl(S(R_cam_u @ np.array([0, 1, 0])) * 0.4)
        ax.quiver(*c, *opt, color="navy", lw=2)
        ax.set_title(f"{title} — green=person fwd, magenta=person up, navy=optical axis")
        ax.set_xlabel("x (m)"); ax.set_ylabel("z depth (m)"); ax.set_zlabel("y up (m)")
        ax.set_box_aspect((1, 1, 0.7))
        if spi == 0:
            ax.legend(loc="upper left", fontsize=8)
        ax.view_init(elev=elev, azim=azim)
    fig.suptitle(f"{args.stem}: integrated scene preview (leveled desk world)")
    out = HERE / "output" / "scene_preview.png"
    fig.tight_layout()
    fig.savefig(out, dpi=110)
    print(f"[+] {out}")


if __name__ == "__main__":
    main()
