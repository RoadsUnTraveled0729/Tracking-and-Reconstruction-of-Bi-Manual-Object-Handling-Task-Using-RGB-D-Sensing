# D-066 created the condensed Craig-labelled copy of the shared generator.
# D-070 corrected its scaled metric object glyph; D-073 uses Camera and the
# existing semantic frame names in every label and writes a condensed asset.
# Shared V8 generators and assets remain unchanged by this naming pass.
#!/usr/bin/env python3
"""Chapter 2 figure: the scene and its coordinate frames (round 4, C45).

Two panels from the rail recording (recording_20260831_065553):

  (a) the pinned scene frame 533 with the {Wall} marker frame, the world
      frame W on the desk marker and the {Object} frame on the cube,
      each projected through the colour intrinsics (frame_draw.py, the
      helpers shared with make_ch4_figs.py). The {Camera} frame is the
      viewpoint of the image. Arrows between the frames carry the names
      of the transformations of Table 2.2.
  (b) a top view of the same scene in final Scene coordinates:
      camera, desk marker (world origin), wall marker, cube at frame
      533, the clean object path, and the participant at the working
      distance, with the same frames and arrows.

Inputs: eval/output/scene_calibration_r6bc.json, the colour intrinsics
of eval/output/<stem>_aruco_raw_scaled.meta.json, the UNSCALED raw
detections v1/aruco/output/<stem>_aruco_raw.csv (the E-009a scale acts
along the camera ray, so marker centres project to the same pixels but
axis tips would not), the clean world track, and figures/src/r6b_frame00533.png.

Output: writing/v8/condensed/figures/ch2_fig_frames_craig.png
Run:    python writing/v8/condensed/scripts/make_ch2_frames_craig_fig.py
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
import numpy as np
import pandas as pd
import cv2

REPO = Path(__file__).resolve().parents[4]
# the shared helper modules stay where they are; this copy only borrows them
import sys as _sys
_sys.path.insert(0, str(REPO / "writing" / "v8" / "scripts"))
sys.path.insert(0, str(REPO / "v1" / "aruco"))
sys.path.insert(0, str(REPO / "eval" / "offset"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from frames import rt_from_row, make_T, inv_T  # noqa: E402
import carry  # noqa: E402
from frame_draw import AXC, draw_axes  # noqa: E402

STEM = "recording_20260831_065553"
EOUT = REPO / "eval" / "output"
FIG = REPO / "writing" / "v8" / "figures"
SRC = FIG / "src" / "r6b_frame00533.png"
SCENE_FRAME = 533
WALL_ID, OBJ_ID, DESK_ID = 0, 1, 2

calib = json.loads((EOUT / "scene_calibration_r6bc.json").read_text())
meta = json.loads((EOUT / f"{STEM}_aruco_raw_scaled.meta.json").read_text())
INTR = meta["color_intrinsics"]
raw = pd.read_csv(REPO / "v1" / "aruco" / "output" / f"{STEM}_aruco_raw.csv")
clean = pd.read_csv(EOUT / f"{STEM}_scaled_object_world_filtered_clean.csv")

row = raw[raw.frame == SCENE_FRAME].iloc[0]
T_cam_wall_raw = make_T(*rt_from_row(row, WALL_ID))
T_cam_desk_raw = make_T(*rt_from_row(row, DESK_ID))
T_cam_obj_raw = make_T(*rt_from_row(row, OBJ_ID))

TWALL = r"${}^{\mathrm{Camera}}_{\mathrm{Wall}}T$"
TOBJ = r"${}^{\mathrm{Camera}}_{\mathrm{Object}}T$"
TWORLD = r"${}^{\mathrm{Camera}}_{\mathrm{World}}T$"
TWO = r"${}^{\mathrm{World}}_{\mathrm{Object}}T$"

ARROW = dict(arrowstyle="-|>", color="#222222", lw=1.5, mutation_scale=14,
             shrinkA=4, shrinkB=6)
LBL = dict(fontsize=10.5, ha="center", va="center", color="#222222",
           bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="0.5", alpha=0.92))


def tarrow(ax, p0, p1, text, rad, tpos=0.5, tdxy=(0, 0)):
    """Curved arrow from p0 to p1 with a transformation label near it."""
    ax.annotate("", xy=p1, xytext=p0,
                arrowprops=dict(connectionstyle=f"arc3,rad={rad}", **ARROW))
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    mid = p0 + (p1 - p0) * tpos
    # offset the label off the chord in the direction the arc bulges
    chord = p1 - p0
    nrm = np.array([-chord[1], chord[0]])
    nrm = nrm / (np.linalg.norm(nrm) + 1e-9)
    lab = mid + nrm * rad * np.linalg.norm(chord) * 0.5 + np.asarray(tdxy)
    ax.text(lab[0], lab[1], text, **LBL)


fig = plt.figure(figsize=(13.2, 6.0))
gs = fig.add_gridspec(1, 2, width_ratios=[1.45, 1.0], wspace=0.04)

# ---------------------------------------------------------------- (a)
ax = fig.add_subplot(gs[0, 0])
img = cv2.cvtColor(cv2.imread(str(SRC)), cv2.COLOR_BGR2RGB)
ax.imshow(img)
uv_wall = draw_axes(ax, T_cam_wall_raw, 0.16, "{Wall} marker frame",
                    INTR, label_dxy=(-52, 64), fs=9.5)
uv_W = draw_axes(ax, T_cam_desk_raw, 0.09, "{World} frame\n(desk marker)",
                 INTR, label_dxy=(-175, 20), fs=9.5)
uv_O = draw_axes(ax, T_cam_obj_raw, 0.055, "{Object} frame",
                 INTR, label_dxy=(120, -34), fs=9.5)
c_box = (14, 14)
ax.text(c_box[0], c_box[1],
        "{Camera} frame\nthe viewpoint of this image\n(x right, y down, z into the scene)",
        fontsize=9.5, weight="bold", va="top", ha="left",
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="0.6", alpha=0.92))
c_anchor = (165, 78)
tarrow(ax, c_anchor, uv_wall, TWALL, rad=0.35, tpos=0.32,
       tdxy=(-34, -14))
tarrow(ax, c_anchor, uv_O, TOBJ, rad=-0.25, tpos=0.68, tdxy=(64, 0))
tarrow(ax, c_anchor, uv_W, TWORLD, rad=-0.35, tpos=0.62, tdxy=(0, 0))
tarrow(ax, uv_W, uv_O, TWO, rad=0.30, tpos=0.5, tdxy=(0, 0))
ax.set_xlim(0, img.shape[1])
ax.set_ylim(img.shape[0], 0)
ax.set_axis_off()
ax.set_title("(a) the frames on a colour frame of the recording", fontsize=10.5)

# ---------------------------------------------------------------- (b)
world = carry.LeveledWorld(calib)
Pm = carry.P
# D-082: include the actual floor placement; a top view discards only y.
floor_shift = np.array([0., calib["scene_geometry"]["origin_above_tabletop_m"]
                        + .03 + .69, 0.])
T_cam_desk = np.array(calib["T_cam_desk"])
T_cam_wall = np.array(calib["T_cam_wall"])
T_desk_cam = inv_T(T_cam_desk)
T_W_wall = T_desk_cam @ T_cam_wall
# D-070: panel (b) is metric; use the scaled detection with scaled calibration.
scaled = pd.read_csv(EOUT / f"{STEM}_aruco_raw_scaled.csv")
scaled_row = scaled[scaled.frame == SCENE_FRAME].iloc[0]
T_cam_obj_scaled = make_T(*rt_from_row(scaled_row, OBJ_ID))
T_W_obj = T_desk_cam @ T_cam_obj_scaled


def scene_point(p_world):
    return world.level(Pm @ np.asarray(p_world, float))[0] + floor_shift


def scene_direction(v_world):
    return (world.G @ (Pm @ np.asarray(v_world, float)))


def xz(p):
    return np.array([p[0], p[2]])


cam = xz(scene_point(T_desk_cam[:3, 3]))
wall = xz(scene_point(T_W_wall[:3, 3]))
obj = xz(scene_point(T_W_obj[:3, 3]))
origin = np.zeros(2)

obj_u = clean[["unity_px", "unity_py", "unity_pz"]].to_numpy()
ok = np.isfinite(obj_u).all(axis=1)
path = world.level(obj_u[ok]) + floor_shift

ax = fig.add_subplot(gs[0, 1])
ax.set_aspect("equal")
# desk: a plain rectangle round the working area, drawn to the desk edge
# at the camera
desk = Rectangle((-0.75, cam[1] + 0.02), 1.5, 1.30, fc="#e9dcc3", ec="0.55",
                 lw=1.0)
ax.add_patch(desk)
ax.text(-0.70, cam[1] + 1.22, "desk", fontsize=9, color="#7a6a45", ha="left")
# the wall behind the working area
ax.plot([-1.45, 0.95], [wall[1] + 0.02, wall[1] + 0.02], color="0.35", lw=3.0)
ax.text(0.9, wall[1] + 0.10, "wall", fontsize=9, color="0.35", ha="right")
# the participant, drawn at the working distance behind the desk
person = (0.0, cam[1] + 1.62)
ax.add_patch(Circle(person, 0.11, fc="#f2c9a0", ec="0.4", lw=1.0))
ax.plot([person[0] - 0.24, person[0] + 0.24], [person[1] + 0.02] * 2,
        color="0.4", lw=6.0, solid_capstyle="round")
ax.text(person[0] + 0.30, person[1], "participant", fontsize=9, color="0.3",
        va="center")
# the clean object path and the cube at the scene frame
ax.plot(path[:, 0], path[:, 2], color="0.65", lw=1.0, label="object path")
ax.add_patch(Rectangle(obj - 0.035, 0.07, 0.07, fc="white", ec="0.3", lw=1.0))


def glyph(ax, p, dirs, names, length=0.16, lw=2.0):
    for v, nm in zip(dirs, names):
        v2 = xz(v)
        n = np.linalg.norm(v2)
        if n < 1e-6:
            continue
        v2 = v2 / n * length
        ax.annotate("", xy=p + v2, xytext=p,
                    arrowprops=dict(arrowstyle="-|>", color=AXC[nm], lw=lw,
                                    mutation_scale=11))
        ax.text(*(p + v2 * 1.28), nm, color=AXC[nm], fontsize=9.5,
                weight="bold", ha="center", va="center")


# camera: its x axis and its z axis (forward), expressed in Scene
R_WC = T_desk_cam[:3, :3]
glyph(ax, cam, [scene_direction(R_WC[:, 0]), scene_direction(R_WC[:, 2])], ["x", "z"])
ax.plot(*cam, marker="^", ms=11, color="#6a4c93")
ax.text(cam[0] - 0.22, cam[1] - 0.16, "{Camera} frame", fontsize=9.5,
        weight="bold", ha="center", **{"bbox": LBL["bbox"]})
# world frame: x and y of the marker plane, expressed in Scene
glyph(ax, origin, [scene_direction([1, 0, 0]), scene_direction([0, 1, 0])], ["x", "y"])
ax.plot(0, 0, "s", ms=7, color="black")
ax.text(0.48, -0.36, "{World} frame\n(desk marker)", fontsize=9.5,
        weight="bold", ha="center", bbox=LBL["bbox"])
# wall marker: its x axis and its z axis (out of the face)
R_Ww = T_W_wall[:3, :3]
glyph(ax, wall, [scene_direction(R_Ww[:, 0]), scene_direction(R_Ww[:, 2])], ["x", "z"])
ax.plot(*wall, "s", ms=7, color="black")
ax.text(wall[0] + 0.05, wall[1] - 0.24, "{Wall} marker frame", fontsize=9.5,
        weight="bold", ha="left", bbox=LBL["bbox"])
# object: its x axis and z axis (out of the marker face)
R_Wo = T_W_obj[:3, :3]
glyph(ax, obj, [scene_direction(R_Wo[:, 0]), scene_direction(R_Wo[:, 2])], ["x", "z"],
      length=0.12)
ax.text(obj[0] - 0.30, obj[1] + 0.22, "{Object} frame", fontsize=9.5,
        weight="bold", ha="center", bbox=LBL["bbox"])

tarrow(ax, cam, wall, TWALL, rad=-0.25, tpos=0.62, tdxy=(-0.50, 0))
tarrow(ax, cam, origin, TWORLD, rad=0.45, tpos=0.5, tdxy=(-0.13, 0))
tarrow(ax, cam, obj, TOBJ, rad=-0.45, tpos=0.5, tdxy=(0.30, 0.08))
tarrow(ax, origin, obj, TWO, rad=0.35, tpos=0.5)

ax.set_xlim(-1.55, 1.05)
ax.set_ylim(cam[1] - 0.45, wall[1] + 0.30)
ax.set_xlabel("Scene x (m)", fontsize=9)
ax.set_ylabel("Scene z (m)", fontsize=9)
ax.tick_params(labelsize=8)
ax.grid(True, color="0.92", lw=0.5)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.set_title("(b) top view of the scene, from the calibrated poses",
             fontsize=10.5)

out = REPO / "writing/v8/condensed/figures/ch2_fig_frames_craig.png"
fig.savefig(out, dpi=200, bbox_inches="tight")
plt.close(fig)
print("saved", out)
print("cam", cam, "wall", wall, "obj", obj)
