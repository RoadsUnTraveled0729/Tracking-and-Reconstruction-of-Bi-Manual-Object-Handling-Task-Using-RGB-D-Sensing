#!/usr/bin/env python3
"""Chapter 3 kinematic schematic (V7 rewrite round, supervisor comment C9).

A robotics-course-style schematic of the modelled right arm, drawn the
way serial manipulators such as the PUMA robot are drawn: each solved
rotation is a revolute-joint cylinder whose axis is the rotation axis.
The shoulder is a cluster of three cylinders (swing azimuth about y,
swing elevation about z, twist about the upper-arm axis), the elbow is
one hinge cylinder (flexion), and the wrist ends the chain as a tracked
point with no joint. Every solved angle is labelled with the symbol the
text and the worked example use.

Output: writing/v7/figures/ch3_fig_schematic.png
Run:    python writing/v7/scripts/make_ch3_schematic.py
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import (FancyArrowPatch, FancyBboxPatch, Circle,
                                Ellipse, Arc, Rectangle)
from matplotlib.transforms import Affine2D

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v7" / "figures" / "ch3_fig_schematic.png"

C_LINK = "#4a4e69"
C_CYL = "#e9ecef"
C_CYLE = "#343a40"
C_ANGLE = "#7b2cbf"
C_FRAME = {"x": "#c1121f", "y": "#2a9d8f", "z": "#1d6fb8"}

fig, ax = plt.subplots(figsize=(9.6, 6.4))
ax.set_xlim(-0.4, 7.0)
ax.set_ylim(-0.7, 4.4)
ax.set_aspect("equal")
ax.axis("off")


def cylinder(cx, cy, angle_deg, length=0.62, radius=0.15, fc=C_CYL):
    """A 3D-looking revolute-joint cylinder centred at (cx, cy), axis at
    angle_deg in the page. Returns the two axis endpoints."""
    tr = Affine2D().rotate_deg_around(cx, cy, angle_deg) + ax.transData
    body = Rectangle((cx - length / 2, cy - radius), length, 2 * radius,
                     fc=fc, ec=C_CYLE, lw=1.4, transform=tr, zorder=6)
    ax.add_patch(body)
    for sx in (-1, 1):
        e = Ellipse((cx + sx * length / 2, cy), 0.42 * radius * 2, 2 * radius,
                    fc="white" if sx > 0 else fc, ec=C_CYLE, lw=1.4,
                    transform=tr, zorder=7)
        ax.add_patch(e)
    a = np.radians(angle_deg)
    u = np.array([np.cos(a), np.sin(a)])
    return (np.array([cx, cy]) - u * length / 2,
            np.array([cx, cy]) + u * length / 2)


def axis_arrow(p0, p1, ext=0.34, label=None, dl=(0.06, 0.06)):
    """Dash-dot joint axis through the cylinder, extended past both ends."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    u = (p1 - p0) / np.linalg.norm(p1 - p0)
    a, b = p0 - u * ext, p1 + u * ext
    ax.plot([a[0], b[0]], [a[1], b[1]], color=C_CYLE, lw=1.0,
            ls="-.", zorder=5)
    ax.add_patch(FancyArrowPatch(b - u * 0.10, b, arrowstyle="-|>",
                                 mutation_scale=10, color=C_CYLE, zorder=5))
    if label:
        ax.annotate(label, b + np.array(dl), fontsize=9, color=C_CYLE)


def rot_arrow(cx, cy, angle_deg, r=0.30, label=None, loff=(0.0, -0.5)):
    """Curved rotation arrow wrapped around a cylinder at (cx, cy)."""
    arc = Arc((cx, cy), 2 * r, 0.9 * r, angle=angle_deg + 90,
              theta1=200, theta2=500, color=C_ANGLE, lw=1.8, zorder=8)
    ax.add_patch(arc)
    t = np.radians(angle_deg + 90 + 140)
    tip = np.array([cx + r * np.cos(t), cy + 0.45 * r * np.sin(t)])
    ax.add_patch(FancyArrowPatch(tip + np.array([0.02, -0.06]), tip,
                                 arrowstyle="-|>", mutation_scale=9,
                                 color=C_ANGLE, zorder=8))
    if label:
        ax.annotate(label, (cx + loff[0], cy + loff[1]), fontsize=11,
                    color=C_ANGLE, ha="center")


# ----- torso plate with the root frame ---------------------------------
ax.add_patch(FancyBboxPatch((0.0, 0.3), 1.25, 3.3,
                            boxstyle="round,pad=0.06",
                            fc="#f1f3f5", ec=C_LINK, lw=1.6))
ax.text(0.62, 2.0, "torso\n(one rigid\nplate)", ha="center", va="center",
        fontsize=10, color=C_LINK)
hip = np.array([1.12, 0.55])
for dvec, lbl, key in [((0.55, 0.0), "x", "x"), ((0.0, 0.55), "y", "y"),
                       ((-0.30, -0.34), "z", "z")]:
    ax.add_patch(FancyArrowPatch(hip, hip + np.array(dvec),
                                 arrowstyle="-|>", mutation_scale=11,
                                 color=C_FRAME[key], lw=1.6, zorder=9))
    ax.annotate(lbl, hip + np.array(dvec) * 1.24, color=C_FRAME[key],
                fontsize=10, ha="center")
ax.plot(*hip, "o", ms=5, color="black", zorder=9)
ax.text(hip[0] + 0.30, hip[1] - 0.06, "root frame at the\nright hip (L24)",
        fontsize=9, color="black", va="top")

# ----- geometry of the chain -------------------------------------------
S = np.array([1.75, 3.05])            # shoulder joint centre
E = np.array([4.05, 2.15])            # elbow joint centre
W = np.array([5.45, 0.70])            # wrist point
u_arm = (E - S) / np.linalg.norm(E - S)
arm_deg = np.degrees(np.arctan2(u_arm[1], u_arm[0]))

# links first, so cylinders sit on top
ax.plot([S[0], E[0]], [S[1], E[1]], color=C_LINK, lw=7,
        solid_capstyle="round", zorder=2)
ax.plot([E[0], W[0]], [E[1], W[1]], color=C_LINK, lw=7,
        solid_capstyle="round", zorder=2)
ax.plot([1.25, S[0]], [S[1], S[1]], color=C_LINK, lw=7,
        solid_capstyle="round", zorder=2)
ax.text(3.05, 3.10, "upper arm (L12 to L14)", fontsize=9.5, color=C_LINK,
        rotation=arm_deg, rotation_mode="anchor")
ax.text(4.55, 1.98, "forearm (L14 to L16)", fontsize=9.5, color=C_LINK,
        rotation=np.degrees(np.arctan2((W - E)[1], (W - E)[0])),
        rotation_mode="anchor")

# ----- shoulder: three revolute cylinders (like the PUMA base cluster) --
# 1) swing azimuth about the vertical y axis
c1 = S + np.array([0.0, 0.72])
p0, p1 = cylinder(*c1, 90)
axis_arrow(p0, p1, label="y")
rot_arrow(*c1, 90, label="$\\theta_y$  swing azimuth", loff=(1.45, -0.08))
# 2) swing elevation about z (axis out of the page: drawn as a disc)
ax.add_patch(Circle(S, 0.20, fc=C_CYL, ec=C_CYLE, lw=1.4, zorder=6))
ax.plot(*S, marker="o", ms=4, color=C_CYLE, zorder=7)
ax.add_patch(Arc(S, 0.62, 0.62, theta1=-30, theta2=245,
                 color=C_ANGLE, lw=1.8, zorder=8))
tip = S + 0.31 * np.array([np.cos(np.radians(-30)), np.sin(np.radians(-30))])
ax.add_patch(FancyArrowPatch(tip + np.array([-0.05, -0.04]), tip,
                             arrowstyle="-|>", mutation_scale=9,
                             color=C_ANGLE, zorder=8))
ax.annotate("$\\theta_z$  swing elevation\n(axis z, out of the page)",
            S + np.array([-2.05, -0.42]), fontsize=11, color=C_ANGLE)
# 3) twist about the upper-arm axis
c3 = S + u_arm * 1.05
p0, p1 = cylinder(*c3, arm_deg, length=0.58, radius=0.13)
axis_arrow(p0, p1, ext=0.30)
rot_arrow(*c3, arm_deg, r=0.26,
          label="$\\theta_t$  twist about\nthe arm axis", loff=(0.15, -0.78))
ax.annotate("shoulder (L12): three solved rotations", xy=S + np.array([-0.05, 0.20]),
            xytext=(2.6, 4.15), fontsize=10, color="#c1121f",
            arrowprops=dict(arrowstyle="->", color="#c1121f", lw=1.2))

# ----- elbow: one hinge cylinder ---------------------------------------
hinge_deg = arm_deg + 90
p0, p1 = cylinder(*E, hinge_deg, length=0.56, radius=0.13)
axis_arrow(p0, p1, ext=0.28)
rot_arrow(*E, hinge_deg, r=0.26,
          label="$e_y$  elbow flexion\n(zero = straight arm)",
          loff=(-0.15, -0.95))
ax.annotate("elbow (L14): one solved rotation", xy=E + np.array([0.12, 0.28]),
            xytext=(4.35, 3.35), fontsize=10, color="#c1121f",
            arrowprops=dict(arrowstyle="->", color="#c1121f", lw=1.2))
# zero direction: the extended upper-arm axis
ext = E + u_arm * 1.35
ax.plot([E[0], ext[0]], [E[1], ext[1]], color="#adb5bd", lw=1.2, ls=":",
        zorder=1)

# ----- wrist: tracked point --------------------------------------------
ax.plot(*W, "o", ms=12, color="black", zorder=8)
ax.text(W[0] + 0.16, W[1] + 0.02,
        "wrist (L16): tracked 3D point,\nno joint solved here",
        fontsize=10, color="black", va="center")

# ----- note block -------------------------------------------------------
ax.text(-0.25, -0.32,
        "Each solved rotation is drawn as a revolute-joint cylinder whose dash-dot line is its rotation axis.\n"
        "Four solved angles per arm: shoulder swing $\\theta_y$, $\\theta_z$, shoulder twist $\\theta_t$, elbow flexion $e_y$.\n"
        "Zero reference: the T-pose, with the right arm along the root frame's +x axis (dotted grey line at the elbow).",
        fontsize=9.5, color="0.25", va="top")

plt.tight_layout()
plt.savefig(OUT, dpi=200, bbox_inches="tight")
print("saved", OUT)
