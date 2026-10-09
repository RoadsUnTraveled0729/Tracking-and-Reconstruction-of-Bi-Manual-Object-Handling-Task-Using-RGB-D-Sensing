# D-082: Scene positions are drawn from the same origin on the floor.
#!/usr/bin/env python3
"""Chapter 5 figure: the schematic for equations (5.1) and (5.2)
(supervisor comment C23, round of 2026-09-05).

(a) A clean frame: the marker-origin and wrist positions are measured in
Scene coordinates, including the same recording-specific floor placement.
Grey position vectors start at the Scene origin on the drawn floor; their
difference is the purple displacement. The transpose of the
Scene/MappedMarker rotation expresses it in MappedMarker.
(b) A later frame: the same offset is rotated into Scene and added to
the new marker-origin position, predicting the hidden wrist. The two
full Craig expressions match equations (5.2) and (5.1), respectively.

Drawing style follows make_ch5_grip_fig.py of the v7 round.

Output: writing/v9/figures/ch5_fig_offset.png
Run:    python writing/v9/scripts/make_ch5_offset_final_fig.py
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Rectangle
from matplotlib.transforms import Affine2D

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v9" / "figures" / "ch5_fig_offset.png"

C_LM = "#22223b"
C_BONE = "#4a4e69"
C_OBJ = "#1d6fb8"
C_MU = "#7b2cbf"
C_W = "#2a9d8f"
C_GHOST = "#adb5bd"
C_NOTE = "#343a40"

fig = plt.figure(figsize=(10.4, 5.3))
axa = fig.add_axes([0.01, 0.04, 0.48, 0.88])
axb = fig.add_axes([0.51, 0.04, 0.48, 0.88])
for ax in (axa, axb):
    ax.axis("off")
    ax.set_xlim(-0.9, 5.9)
    ax.set_ylim(-1.35, 5.15)
    ax.set_aspect("equal")


def cube(ax, c, ang, s=1.05):
    """The marked cube at centre c turned by ang degrees; returns the
    mapped marker frame (origin, x unit, y unit) in page units."""
    tr = Affine2D().rotate_deg_around(c[0], c[1], ang) + ax.transData
    ax.add_patch(Rectangle((c[0] - s / 2, c[1] - s / 2), s, s,
                           fc="#cfe3f7", ec=C_OBJ, lw=2.0, transform=tr,
                           zorder=3))
    ax.add_patch(Rectangle((c[0] - s / 4, c[1] - s / 4), s / 2, s / 2,
                           fc="white", ec=C_OBJ, lw=1.2, transform=tr,
                           zorder=4))
    a = np.radians(ang)
    ux = np.array([np.cos(a), np.sin(a)])
    uy = np.array([-np.sin(a), np.cos(a)])
    return np.asarray(c, float), ux, uy


def frame_axes(ax, o, ux, uy, L=1.0, lab=("", ""), color=C_OBJ, fs=10,
               lw=1.6):
    for u, t in ((ux, lab[0]), (uy, lab[1])):
        ax.add_patch(FancyArrowPatch(o, o + L * u, arrowstyle="-|>",
                                     mutation_scale=12, color=color,
                                     lw=lw, zorder=6))
        if t:
            ax.annotate(t, o + (L + 0.28) * u, fontsize=fs, color=color,
                        ha="center", va="center", zorder=7)


def wrist_hand(ax, w, color=C_LM):
    ax.add_patch(Circle(w, 0.115, fc=color, ec=color, lw=1.5, zorder=8))


def origin_dot(ax, o):
    ax.add_patch(Circle(o, 0.085, fc=C_OBJ, ec="white", lw=1.2, zorder=9))
    ax.annotate(r"${}^{\mathrm{Scene}}o$", o + np.array([-0.35, 0.35]), fontsize=11,
                color=C_OBJ, ha="center", va="center",
                bbox=dict(fc="white", ec="none", pad=0.4), zorder=9)


def scene_axes(ax):
    o = np.array([-0.35, -0.95])
    ax.plot([-0.65, 5.65], [o[1], o[1]], color=C_GHOST, lw=1.2, zorder=0)
    frame_axes(ax, o, np.array([1.0, 0.0]), np.array([0.0, 1.0]), L=0.8,
               lab=("$x$", "$y$"), color=C_BONE, fs=10, lw=1.4)
    ax.annotate("{Scene} origin on the drawn floor", (1.15, -1.23), fontsize=8.5,
                color=C_BONE, ha="left", va="center")
    return o


def position_vectors(ax, scene_origin, marker_origin, wrist):
    """Absolute Scene positions, sharing the floor-based origin."""
    for point in (marker_origin, wrist):
        ax.add_patch(FancyArrowPatch(scene_origin, point, arrowstyle="-|>",
                                     mutation_scale=11, color=C_GHOST,
                                     lw=1.3, zorder=1))


# =====================================================================
# (a) a clean frame: the offset is read off
# =====================================================================
scene_origin_a = scene_axes(axa)
cA = np.array([1.30, 2.90])
oA, uxA, uyA = cube(axa, cA, 12.0)
frame_axes(axa, oA, uxA, uyA, lab=("", "$y$"))
# the x label sits beside the axis, off the projection line that runs
# along it
axa.annotate("$x$", oA + 1.28 * uxA + 0.30 * uyA, fontsize=10,
             color=C_OBJ, ha="center", va="center", zorder=7)
axa.annotate("{MappedMarker} axes", (3.10, 4.08),
             fontsize=9.5, color=C_OBJ, ha="center", va="center")
origin_dot(axa, oA)

# the wrist, sitting off the cube along the mapped marker axes
hx, hy = 1.90, -1.25
wA = oA + hx * uxA + hy * uyA
position_vectors(axa, scene_origin_a, oA, wA)
axa.plot([wA[0], wA[0] + 0.75], [wA[1], wA[1] - 0.85], color=C_BONE,
         lw=3.0, solid_capstyle="round", zorder=5)
wrist_hand(axa, wA)
axa.annotate("measured wrist\n" + r"${}^{\mathrm{Scene}}p_{wr}$", wA + np.array([0.20, 0.12]),
             fontsize=9.5, color=C_LM, ha="left", va="center")

# The displacement is the difference of the two Scene position vectors.
axa.add_patch(FancyArrowPatch(oA, wA, arrowstyle="-|>", mutation_scale=14,
                              color=C_MU, lw=2.4, zorder=7))
axa.annotate(r"${}^{\mathrm{Scene}}p_{wr} - {}^{\mathrm{Scene}}o$" + "\n(floor translation cancels)", (3.60, 0.55),
             fontsize=9.5, color=C_MU, ha="center", va="center")

# its components along the mapped marker axes (dashed projection lines)
fx = oA + hx * uxA
axa.plot([oA[0], fx[0]], [oA[1], fx[1]], color=C_MU, lw=1.2, ls="--",
         zorder=6)
axa.plot([fx[0], wA[0]], [fx[1], wA[1]], color=C_MU, lw=1.2, ls="--",
         zorder=6)
axa.annotate(r"${}^{\mathrm{MappedMarker}}h_k = "
             r"({}^{\mathrm{Scene}}_{\mathrm{MappedMarker}}R_k)^{T}"
             r"({}^{\mathrm{Scene}}p_{wr,k} - {}^{\mathrm{Scene}}o_k)$",
             (2.50, 4.75), fontsize=9, color=C_MU, ha="center", va="center")

axa.set_title("(a) A clean frame: the offset is read off, equation (5.2)",
              fontsize=10.5, color=C_LM)

# =====================================================================
# (b) a later frame: the same offset predicts the wrist
# =====================================================================
scene_origin_b = scene_axes(axb)
cB = np.array([2.75, 2.45])
oB, uxB, uyB = cube(axb, cB, -35.0)
frame_axes(axb, oB, uxB, uyB, lab=("$x$", "$y$"))
origin_dot(axb, oB)

wB = oB + hx * uxB + hy * uyB
position_vectors(axb, scene_origin_b, oB, wB)
# the hidden wrist: open circle, dashed forearm
axb.plot([wB[0], wB[0] + 0.55], [wB[1], wB[1] - 0.95], color=C_GHOST,
         lw=3.0, ls=(0, (2, 2)), solid_capstyle="round", zorder=5)
axb.add_patch(Circle(wB, 0.13, fc="white", ec=C_W, lw=2.2, zorder=8))
axb.annotate("recovered wrist\n" + r"${}^{\mathrm{Scene}}w$", wB + np.array([0.22, 0.10]), fontsize=9.5,
             color=C_W, ha="left", va="center")

# the offset carried along the new mapped marker axes
axb.add_patch(FancyArrowPatch(oB, wB, arrowstyle="-|>", mutation_scale=14,
                              color=C_MU, lw=2.4, ls="--", zorder=7))
axb.annotate("offset $h$ carried\nby the new axes", 0.5 * (oB + wB) + np.array([-2.25, 0.05]),
             fontsize=9.5, color=C_MU, ha="left", va="center",
             bbox=dict(fc="white", ec="none", pad=0.5), zorder=7)
axb.annotate(r"${}^{\mathrm{Scene}}w = {}^{\mathrm{Scene}}o + "
             r"{}^{\mathrm{Scene}}_{\mathrm{MappedMarker}}R\,{}^{\mathrm{MappedMarker}}h$",
             (2.50, 4.75), fontsize=9, color=C_W, ha="center", va="center")
axb.annotate("grey arrows: Scene\nposition vectors",
             (-0.35, 3.80), fontsize=8.5, color=C_NOTE, ha="left",
             va="center")

axb.set_title("(b) A later frame: the same offset predicts the wrist, equation (5.1)",
              fontsize=10.5, color=C_LM)

fig.savefig(OUT, dpi=200, facecolor="white")
print("saved", OUT)
