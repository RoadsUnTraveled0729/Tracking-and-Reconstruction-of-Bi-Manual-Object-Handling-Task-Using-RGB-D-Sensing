#!/usr/bin/env python3
"""Chapter 4 figures (V8 rewrite round).

Four figures, all from the rail recording (rail-only round, 2026-09-01):

  ch4_fig_frames.png   the three coordinate frames of object tracking,
                       drawn on the pinned scene frame 533 by projecting
                       each calibrated or detected pose through the real
                       colour intrinsics.
  ch4_fig_scene.png    the calibrated scene in one 3D view: world origin,
                       camera, tabletop plane, gravity, and the clean
                       object path.  The box axes are the world axes
                       levelled against the measured gravity, which is
                       why they are labelled "levelled".
  ch4_fig_track.png    the object track before and after the three-stage
                       track filter, per world axis.
  ch4_fig_clean.png    the cleaning step at the one undetected frame (786): the
                       detections, the filtered track that holds the
                       previous pose across the gap, and the cleaned
                       track a consumer reads.

Run: python writing/v8/scripts/make_ch4_figs.py
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import cv2

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "v1" / "aruco"))
sys.path.insert(0, str(REPO / "eval" / "offset"))
from frames import rt_from_row, make_T, inv_T  # noqa: E402
import carry  # noqa: E402

STEM = "recording_20260831_065553"
EOUT = REPO / "eval" / "output"
FIG = REPO / "writing" / "v8" / "figures"
SRC = FIG / "src" / "r6b_frame00533.png"
SCENE_FRAME = 533

calib = json.loads((EOUT / "scene_calibration_r6bc.json").read_text())
meta = json.loads((EOUT / f"{STEM}_aruco_raw_scaled.meta.json").read_text())
# the image overlay uses the UNSCALED detections: the E-009a scale acts
# along the camera ray, so marker centres project to the same pixels,
# but the axis tips do not.
raw = pd.read_csv(REPO / "v1" / "aruco" / "output" / f"{STEM}_aruco_raw.csv")
track = pd.read_csv(EOUT / f"{STEM}_scaled_object_world.csv")
filt = pd.read_csv(EOUT / f"{STEM}_scaled_object_world_filtered.csv")
clean = pd.read_csv(EOUT / f"{STEM}_scaled_object_world_filtered_clean.csv")

from frame_draw import AXC, project as _project, draw_axes as _draw_axes  # noqa: E402

INTR = meta["color_intrinsics"]


# ---------------------------------------------------------------------
# Figure 1: the three frames on the real image (helpers shared with the
# Chapter 2 frames figure in frame_draw.py)
# ---------------------------------------------------------------------
def project(pts_cam):
    return _project(pts_cam, INTR)


def draw_axes(ax, T, length, label, label_dxy=(0, 0), fs=10):
    return _draw_axes(ax, T, length, label, INTR, label_dxy=label_dxy, fs=fs)


img = cv2.cvtColor(cv2.imread(str(SRC)), cv2.COLOR_BGR2RGB)
row = raw[raw.frame == SCENE_FRAME].iloc[0]
T_cam_desk_unscaled = make_T(*rt_from_row(row, 2))
T_cam_obj = make_T(*rt_from_row(row, 1))

fig, ax = plt.subplots(figsize=(8.0, 6.0))
ax.imshow(img)
draw_axes(ax, T_cam_desk_unscaled, 0.09, "world frame W\n(desk marker)",
          label_dxy=(-190, 22))
draw_axes(ax, T_cam_obj, 0.055, "object frame O", label_dxy=(30, -62))
# the camera frame is the viewpoint of the image itself
ax.annotate("camera frame C: the viewpoint of this image\n"
            "(x right, y down, z into the scene)",
            xy=(20, 26), fontsize=9.5,
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.6",
                      alpha=0.9))
ax.set_axis_off()
fig.tight_layout()
fig.savefig(FIG / "ch4_fig_frames.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("saved", FIG / "ch4_fig_frames.png")


# ---------------------------------------------------------------------
# Figure 2: the calibrated scene in one 3D view (gravity-leveled)
# ---------------------------------------------------------------------
world = carry.LeveledWorld(calib)
obj_u = clean[["unity_px", "unity_py", "unity_pz"]].to_numpy()
ok = np.isfinite(obj_u).all(axis=1)
path = world.level(obj_u[ok])
tt = clean["time_s"].to_numpy()[ok]

Pm = carry.P  # unity <-> world axis swap used by the analysis helpers
cam = world.level(world.cam_pos)[0]
drop = calib["scene_geometry"]["origin_above_tabletop_m"]

fig = plt.figure(figsize=(8.6, 6.4))
ax = fig.add_subplot(111, projection="3d")

# the working volume sets the extent; the wall marker sits 2.8 m away and
# enters the drawing only through the gravity direction it defines
xs = [min(path[:, 0].min(), cam[0]) - 0.10, max(path[:, 0].max(), cam[0]) + 0.10]
zs = [min(path[:, 2].min(), cam[2]) - 0.10, max(path[:, 2].max(), cam[2]) + 0.10]
X, Z = np.meshgrid(np.linspace(xs[0], xs[1], 2), np.linspace(zs[0], zs[1], 2))
ax.plot_surface(X, Z, np.full_like(X, -drop), color="#d8c49a", alpha=0.30,
                shade=False)

sc = ax.scatter(path[:, 0], path[:, 2], path[:, 1], c=tt, cmap="viridis",
                s=3.0, depthshade=False)
cb = fig.colorbar(sc, ax=ax, shrink=0.55, pad=0.10)
cb.set_label("time (s)", fontsize=9)

# the world frame axes, drawn where they really point: the desk marker
# card sits on a tilted stand, so its z axis is not the vertical
L = 0.16
for i, nm in enumerate("xyz"):
    e = np.zeros(3)
    e[i] = 1.0
    v = world.G @ (Pm @ e) * L
    ax.quiver(0, 0, 0, v[0], v[2], v[1], color=AXC[nm], lw=2.2,
              arrow_length_ratio=0.20)
    ax.text(v[0] * 1.22, v[2] * 1.22, v[1] * 1.22, nm, color=AXC[nm],
            fontsize=11, weight="bold")
ax.scatter([0], [0], [0], s=70, color="black", depthshade=False)
ax.text(-0.06, -0.30, -0.045, "world origin\n(desk marker)", fontsize=9,
        ha="center")

# gravity, measured from the wall marker, is a separate direction
ax.quiver(0, 0, 0, 0, 0, 0.22, color="#1d3557", lw=1.8, ls="--",
          arrow_length_ratio=0.16)
ax.text(-0.085, 0.0, 0.235, "gravity", fontsize=9.5, color="#1d3557")

ax.scatter([cam[0]], [cam[2]], [cam[1]], s=95, marker="^",
           color="#6a4c93", depthshade=False)
ax.text(cam[0] + 0.03, cam[2], cam[1] + 0.03, "camera", fontsize=9.5,
        color="#6a4c93")
ax.text(xs[0] + 0.02, zs[0] + 0.02, 0.004, "tabletop plane", fontsize=8.5,
        color="#7a6a45")

ax.set_xlabel("levelled x (m)")
ax.set_ylabel("levelled z (m)")
ax.set_zlabel("height (m)", labelpad=6)
ax.set_title("The calibrated scene and the clean object path", fontsize=10)
ax.view_init(elev=24, azim=-58)
ax.set_xlim(xs)
ax.set_ylim(zs)
ax.set_zlim(-drop - 0.02, 0.42)
ax.set_box_aspect((np.ptp(xs), np.ptp(zs), 0.55))
fig.savefig(FIG / "ch4_fig_scene.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("saved", FIG / "ch4_fig_scene.png")


# ---------------------------------------------------------------------
# Figure 3: the track filter, per world axis
# ---------------------------------------------------------------------
t = track["time_s"].to_numpy()
det_raw = track["detected"].to_numpy() == 1
raw_xyz = track[["tx", "ty", "tz"]].to_numpy()
raw_xyz[~det_raw] = np.nan
fil_xyz = filt[["tx", "ty", "tz"]].to_numpy()
filled = filt["filled"].to_numpy() == 1
det_f = filt["detected"].to_numpy() == 1
held = (~det_f) & (~filled)

names = ["x (m)", "y (m)", "z (m)"]
fig, axes = plt.subplots(3, 1, figsize=(9.0, 6.4), sharex=True,
                         constrained_layout=True)
for c in range(3):
    a = axes[c]
    a.plot(t, raw_xyz[:, c], color="0.72", lw=1.0, label="raw world track")
    a.plot(t, fil_xyz[:, c], color="#3b6fb6", lw=1.2, label="filtered track")
    if filled.any():
        a.plot(t[filled], fil_xyz[filled, c], ".", color="#c25a1e", ms=4.5,
               label="bridged sample")
    if held.any():
        a.plot(t[held], fil_xyz[held, c], ".", color="#6a4c93", ms=4.5,
               label="held sample")
    a.set_ylabel(names[c], fontsize=9)
    a.grid(True, color="0.92", lw=0.5)
    a.set_axisbelow(True)
    for s in ("top", "right"):
        a.spines[s].set_visible(False)
axes[0].legend(loc="upper left", fontsize=8, frameon=False, ncol=3)
axes[2].set_xlabel("time (s)")
axes[0].set_title("Object track in the world frame, before and after the "
                  "three filter stages", fontsize=10)
fig.savefig(FIG / "ch4_fig_track.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("saved", FIG / "ch4_fig_track.png")


# ---------------------------------------------------------------------
# Figure 4: the cleaning step at the one undetected frame
# ---------------------------------------------------------------------
lo, hi = 770, 805
sl = slice(lo, hi)
tt = filt["time_s"].to_numpy()[sl]
# the cleaning step blanks the pose columns the consumers read (unity_p*),
# which for the x axis carry the same world x as tx; reading tx from the
# clean track would show the blanked rows as if they had been kept
rx = track["unity_px"].to_numpy()[sl]
det_r = track["detected"].to_numpy()[sl] == 1
fx = filt["unity_px"].to_numpy()[sl]
det_f = filt["detected"].to_numpy()[sl] == 1
fill_f = filt["filled"].to_numpy()[sl] == 1
kept = clean["detected"].to_numpy()[sl] == 1
cx = clean["unity_px"].to_numpy()[sl]

held_f = (~det_f) & (~fill_f)
rej = det_f & ~kept

hold = np.empty_like(cx)
last = np.nan
for i in range(len(cx)):
    if np.isfinite(cx[i]):
        last = cx[i]
    hold[i] = last

fig, axes = plt.subplots(2, 1, figsize=(9.0, 5.6), sharex=True,
                         constrained_layout=True)
a = axes[0]
a.plot(tt[det_r], rx[det_r], "o", color="0.55", ms=5.0, mfc="none",
       label="marker detected")
a.plot(tt, fx, color="#3b6fb6", lw=1.3, label="track entering the cleaning step")
a.plot(tt[held_f], fx[held_f], ".", color="#6a4c93", ms=6,
       label="undetected row, previous pose held")
if fill_f.any():
    a.plot(tt[fill_f], fx[fill_f], ".", color="#c25a1e", ms=6,
           label="undetected row, gap bridged")
if rej.any():
    a.plot(tt[rej], fx[rej], "X", color="#c1121f", ms=11,
           label="detected but implausible: rejected")
a.set_ylabel("world x (m)", fontsize=9)
a.legend(loc="lower left", fontsize=8, frameon=False, ncol=2)
a.set_title("The cleaning step at the one undetected frame", fontsize=10)

b = axes[1]
b.plot(tt, hold, color="#2a9d8f", lw=1.6,
       label="the clean track a consumer reads, last kept pose held")
b.plot(tt[kept], cx[kept], "o", color="#2a9d8f", ms=4.0, mfc="white",
       label="kept sample")
b.set_ylabel("world x (m)", fontsize=9)
b.set_xlabel("time (s)")
b.legend(loc="lower left", fontsize=8, frameon=False)

vals = np.concatenate([rx[det_r], fx, hold[np.isfinite(hold)]])
pad = 0.12 * (vals.max() - vals.min() + 1e-6)
for a in axes:
    a.grid(True, color="0.92", lw=0.5)
    a.set_axisbelow(True)
    for sp in ("top", "right"):
        a.spines[sp].set_visible(False)
    a.set_ylim(vals.min() - 2.2 * pad, vals.max() + pad)
fig.savefig(FIG / "ch4_fig_clean.png", dpi=200, bbox_inches="tight")
plt.close(fig)
print("saved", FIG / "ch4_fig_clean.png")
