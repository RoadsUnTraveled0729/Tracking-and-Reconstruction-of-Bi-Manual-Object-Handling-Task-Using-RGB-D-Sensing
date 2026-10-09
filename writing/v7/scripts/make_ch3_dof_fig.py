#!/usr/bin/env python3
"""Chapter 3 seven-DOF arm figure (V7 rewrite round).

The provenance figure for the arm model, drawn after the standard
robotics illustration the supervisor referenced: (a) the seven
rotational degrees of freedom of a human arm, labelled q1 to q7 on the
arm itself; (b) the equivalent serial chain of revolute joints in the
PUMA convention. The four rotations this thesis solves (q1 to q4) are
drawn in the accent colour; the wrist triple (q5 to q7) is grey, since
it is not observable from the landmark set and the wrist is carried as
a tracked point.

Output: writing/v7/figures/ch3_fig_dof.png
Run:    python writing/v7/scripts/make_ch3_dof_fig.py
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
OUT = REPO / "writing" / "v7" / "figures" / "ch3_fig_dof.png"

C_SOLVED = "#7b2cbf"
C_UNSOLV = "#868e96"
C_LINK = "#4a4e69"
C_CYL = "#e9ecef"
C_CYLE = "#343a40"

fig, (axA, axB) = plt.subplots(1, 2, figsize=(10.6, 6.2),
                               gridspec_kw={"width_ratios": [1.15, 1.0]})
for a in (axA, axB):
    a.set_aspect("equal")
    a.axis("off")


def qlabel(a, x, y, n, color):
    a.add_patch(Circle((x, y), 0.16, fc="white", ec=color, lw=1.6, zorder=9))
    a.text(x, y, f"q{n}", fontsize=9.5, ha="center", va="center",
           color=color, zorder=10)


def rot_arc(a, cx, cy, w, h, angle, t1, t2, color, tip_at_end=True):
    a.add_patch(Arc((cx, cy), w, h, angle=angle, theta1=t1, theta2=t2,
                    color=color, lw=1.8, zorder=8))
    t = np.radians(angle + (t2 if tip_at_end else t1))
    tip = np.array([cx + (w / 2) * np.cos(t), cy + (h / 2) * np.sin(t)])
    a.add_patch(FancyArrowPatch(tip + np.array([0.03, -0.06]), tip,
                                arrowstyle="-|>", mutation_scale=9,
                                color=color, zorder=8))


# ======================= (a) the human arm =============================
axA.set_xlim(-0.6, 5.6)
axA.set_ylim(-0.8, 5.4)
axA.set_title("(a) the seven rotations of a human arm", fontsize=11)

# torso edge
axA.add_patch(FancyBboxPatch((-0.35, 0.2), 1.05, 4.4,
                             boxstyle="round,pad=0.06",
                             fc="#f1f3f5", ec=C_LINK, lw=1.5))
axA.text(0.17, 2.4, "torso", fontsize=10, color=C_LINK, ha="center")

S = np.array([1.15, 4.05])
E = np.array([3.05, 2.95])
W = np.array([4.35, 1.65])
H = W + 0.75 * (W - E) / np.linalg.norm(W - E)

for p0, p1 in [(np.array([0.7, 4.05]), S), (S, E), (E, W), (W, H)]:
    axA.plot([p0[0], p1[0]], [p0[1], p1[1]], color=C_LINK, lw=7,
             solid_capstyle="round", zorder=2)
axA.add_patch(Circle(S, 0.16, fc="white", ec=C_LINK, lw=1.8, zorder=4))
axA.add_patch(Circle(E, 0.13, fc="white", ec=C_LINK, lw=1.8, zorder=4))
axA.plot(*W, "o", ms=9, color="black", zorder=4)
axA.text(H[0] + 0.12, H[1] - 0.12, "hand", fontsize=9, color=C_LINK)
axA.text(S[0] - 0.05, S[1] + 0.75, "shoulder", fontsize=9.5, color=C_LINK,
         ha="center")
axA.text(E[0] + 0.30, E[1] + 0.28, "elbow", fontsize=9.5, color=C_LINK)
axA.text(W[0] - 0.02, W[1] + 0.30, "wrist", fontsize=9.5, color=C_LINK)

# q1: swing the arm forward/back (about the vertical axis)
rot_arc(axA, S[0], S[1], 1.5, 0.5, 0, 190, 350, C_SOLVED)
qlabel(axA, S[0] - 0.95, S[1] - 0.42, 1, C_SOLVED)
# q2: raise/lower the arm (in-page arc at the shoulder)
rot_arc(axA, S[0], S[1], 1.9, 1.9, 0, -55, -5, C_SOLVED)
qlabel(axA, S[0] + 1.25, S[1] - 0.05, 2, C_SOLVED)
# q3: roll about the upper-arm axis
mid = S + 0.52 * (E - S)
ang_ua = np.degrees(np.arctan2((E - S)[1], (E - S)[0]))
rot_arc(axA, mid[0], mid[1], 0.42, 0.9, ang_ua, 120, 420, C_SOLVED)
qlabel(axA, mid[0] - 0.55, mid[1] - 0.55, 3, C_SOLVED)
# q4: elbow flexion
rot_arc(axA, E[0], E[1], 1.5, 1.5, 0, -95, -45, C_SOLVED)
qlabel(axA, E[0] - 0.25, E[1] - 1.10, 4, C_SOLVED)
# q5: forearm roll (pronation)
midf = E + 0.72 * (W - E)
ang_fa = np.degrees(np.arctan2((W - E)[1], (W - E)[0]))
rot_arc(axA, midf[0], midf[1], 0.38, 0.8, ang_fa, 120, 420, C_UNSOLV)
qlabel(axA, midf[0] + 0.30, midf[1] + 0.55, 5, C_UNSOLV)
# q6: wrist bend
rot_arc(axA, W[0], W[1], 1.2, 1.2, 0, -100, -55, C_UNSOLV)
qlabel(axA, W[0] - 0.45, W[1] - 0.95, 6, C_UNSOLV)
# q7: wrist turn
midh = W + 0.45 * (H - W)
rot_arc(axA, midh[0], midh[1], 0.34, 0.72, ang_fa, 120, 420, C_UNSOLV)
qlabel(axA, midh[0] + 0.72, midh[1] + 0.35, 7, C_UNSOLV)

# ================ (b) the equivalent serial chain ======================
axB.set_xlim(-1.8, 4.2)
axB.set_ylim(-0.8, 5.4)
axB.set_title("(b) the equivalent serial chain\n(PUMA convention)", fontsize=11)


def cyl(a, cx, cy, angle_deg, length=0.62, radius=0.16, color=C_CYLE):
    tr = Affine2D().rotate_deg_around(cx, cy, angle_deg) + a.transData
    a.add_patch(Rectangle((cx - length / 2, cy - radius), length, 2 * radius,
                          fc=C_CYL, ec=color, lw=1.4, transform=tr, zorder=6))
    for sx in (-1, 1):
        a.add_patch(Ellipse((cx + sx * length / 2, cy), 0.34 * radius * 2,
                            2 * radius, fc="white" if sx > 0 else C_CYL,
                            ec=color, lw=1.4, transform=tr, zorder=7))
    u = np.array([np.cos(np.radians(angle_deg)), np.sin(np.radians(angle_deg))])
    c = np.array([cx, cy])
    e0, e1 = c - u * (length / 2 + 0.22), c + u * (length / 2 + 0.22)
    a.plot([e0[0], e1[0]], [e0[1], e1[1]], color=color, lw=0.9, ls="-.",
           zorder=5)


chain_x = 0.55
ys = [4.75, 4.05, 3.35, 2.45, 1.55, 0.90, 0.25]
angles = [90, 0, 90, 0, 90, 0, 90]
colors = [C_SOLVED] * 4 + [C_UNSOLV] * 3
labels = ["q1  shoulder swing", "q2  shoulder swing", "q3  upper-arm roll",
          "q4  elbow flexion", "q5  forearm roll", "q6  wrist bend",
          "q7  wrist turn"]

# spine of the chain
axB.plot([chain_x] * 2, [ys[-1] - 0.35, ys[0] + 0.35], color=C_LINK, lw=5,
         solid_capstyle="round", zorder=2)
for y, angd, col, lab in zip(ys, angles, colors, labels):
    cyl(axB, chain_x, y, angd, color=col)
    n = labels.index(lab) + 1
    qlabel(axB, chain_x - 1.15, y, n, col)
    axB.text(chain_x + 0.95, y, lab.split("  ")[1], fontsize=9.5, color=col,
             va="center")

# group brackets
for y0, y1, name, col in [(3.05, 5.05, "shoulder", C_SOLVED),
                          (2.15, 2.75, "elbow", C_SOLVED),
                          (-0.05, 1.85, "wrist", C_UNSOLV)]:
    axB.plot([chain_x + 2.45] * 2, [y0, y1], color=col, lw=1.2)
    axB.text(chain_x + 2.55, (y0 + y1) / 2, name, fontsize=9.5, color=col,
             va="center")

# end effector
axB.add_patch(FancyArrowPatch((chain_x, ys[-1] - 0.35),
                              (chain_x, ys[-1] - 0.75),
                              arrowstyle="-|>", mutation_scale=12,
                              color=C_LINK, zorder=3))
axB.text(chain_x + 0.15, ys[-1] - 0.68, "hand", fontsize=9, color=C_LINK)

# legend
fig.text(0.5, 0.045,
         "purple: the four rotations this thesis solves (q1, q2 = shoulder swing, "
         "q3 = shoulder twist, q4 = elbow flexion).\n"
         "grey: the wrist triple, not observable from the eight body landmarks; "
         "the wrist is carried as a tracked 3D point.",
         fontsize=9.5, color="0.25", ha="center")

plt.tight_layout(rect=(0, 0.09, 1, 1))
plt.savefig(OUT, dpi=200, bbox_inches="tight")
print("saved", OUT)
