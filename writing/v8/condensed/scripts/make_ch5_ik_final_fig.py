#!/usr/bin/env python3
"""Chapter 5 figure: the two-link elbow reconstruction, drawn in 3D.

The elbow lies on the intersection of the sphere of the upper-arm length
about the shoulder and the sphere of the forearm length about the wrist.
That intersection is a circle whose axis is the shoulder-to-wrist line,
and the one remaining freedom, where on the circle the elbow sits, is
fixed by projecting the direction memory of the upper arm onto it.

The main panel is a 3D view because the construction is a 3D one. Each
sphere is drawn and labelled as the band of its own surface that
surrounds the meeting, swept about the shoulder-to-wrist line: a whole
sphere would bury the circle and the bones, a single arc does not read
as a surface at all. The inset looks straight down the
shoulder-to-wrist line, where the circle appears as a circle and the
projection step is a single stroke. Every label is the symbol used in
Section 5.5, and the key gives each symbol its word.

Output: writing/v8/condensed/figures/ch5_fig_ik.png
Run:    python writing/v8/condensed/scripts/make_ch5_ik_final_fig.py
"""
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle as Circle2D, FancyArrowPatch

REPO = Path(__file__).resolve().parents[4]
OUT = REPO / "writing" / "v8" / "condensed" / "figures" / "ch5_fig_ik.png"

C_INK = "#22223b"
C_BONE = "#3f4257"
C_CIRC = "#7b2cbf"
C_MEM = "#e07a1f"
C_OBJ = "#1d6fb8"
C_SPH1 = "#7a8896"      # sphere about the shoulder
C_SPH2 = "#b09a86"      # sphere about the wrist

# --- geometry ---------------------------------------------------------
# Section 5.5 notation: b is the shoulder-to-wrist vector, r its length,
# b-hat its unit vector, j the angle at the shoulder, p_c and r_c the
# circle centre and radius, n1/n2 the circle's basis, u-hat the
# direction memory of the upper arm.
S = np.array([0.0, 0.0, 0.0])
W = np.array([0.24, -0.19, 0.0])
L1, L2 = 0.26, 0.25

bvec = W - S
r = float(np.linalg.norm(bvec))
bh = bvec / r
ca = float(np.clip((L1 ** 2 + r ** 2 - L2 ** 2) / (2 * L1 * r), -1, 1))
j_sh = float(np.arccos(ca))
pc = S + L1 * ca * bh
rho = L1 * float(np.sqrt(max(0.0, 1 - ca * ca)))
j_wr = float(np.arccos(np.clip((L2 ** 2 + r ** 2 - L1 ** 2) / (2 * L2 * r),
                               -1, 1)))

# circle plane basis n1, n2 of equation (5.10)
n1 = np.array([0.0, 0.0, 1.0])
n1 = n1 - (n1 @ bh) * bh
n1 /= np.linalg.norm(n1)
n2 = np.cross(bh, n1)

phi = np.linspace(0, 2 * np.pi, 360)
circ = pc[:, None] + rho * (np.outer(n1, np.cos(phi))
                            + np.outer(n2, np.sin(phi)))

# the direction memory of the upper arm and the elbow it selects
u_mem = np.array([0.10, -0.72, 0.68])
u_mem /= np.linalg.norm(u_mem)
perp = u_mem - (u_mem @ bh) * bh
E = pc + rho * perp / np.linalg.norm(perp)

fig = plt.figure(figsize=(11.4, 5.9))

# --- main panel -------------------------------------------------------
ax = fig.add_axes([0.00, 0.02, 0.63, 0.94], projection="3d")
ax.view_init(elev=20, azim=3)
ax.set_axis_off()

# the arm plane, which orients the angle marker at the shoulder
n_plane = np.cross(bh, (E - pc) / rho)
g1 = bh
g2 = np.cross(n_plane, g1)
g2 /= np.linalg.norm(g2)
if (E - S) @ g2 < 0:
    g2 = -g2


def cap(centre, radius, axis, polar, pad=0.62, nt=44, np_=88):
    """The spherical cap of `radius` about `centre` whose rim reaches
    `polar` radians off `axis`, drawn a little past the rim. Each
    sphere is shown as the cap that carries the intersection circle: a
    whole sphere would bury the circle and the two bones."""
    k = axis / np.linalg.norm(axis)
    m1 = np.cross(k, [0.0, 0.0, 1.0])
    if np.linalg.norm(m1) < 1e-6:
        m1 = np.cross(k, [0.0, 1.0, 0.0])
    m1 /= np.linalg.norm(m1)
    m2 = np.cross(k, m1)
    t = np.linspace(0.0, polar + pad, nt)[:, None]
    ph = np.linspace(0.0, 2 * np.pi, np_)[None, :]
    dirs = (np.cos(t) * k[:, None, None]
            + np.sin(t) * (np.cos(ph) * m1[:, None, None]
                           + np.sin(ph) * m2[:, None, None]))
    q = np.asarray(centre)[:, None, None] + radius * dirs
    return q[0], q[1], q[2]


# the two spheres of equation (5.7), as translucent surfaces
ax.plot_surface(*cap(S, L1, bh, j_sh), color=C_SPH1, alpha=0.22,
                linewidth=0, edgecolors="none", rcount=9, ccount=22,
                shade=False, zorder=2)
ax.plot_surface(*cap(W, L2, -bh, j_wr), color=C_SPH2, alpha=0.22,
                linewidth=0, edgecolors="none", rcount=9, ccount=22,
                shade=False, zorder=2)

# shoulder-to-wrist axis, intersection circle, radius, bones
ax.plot([S[0], W[0]], [S[1], W[1]], [S[2], W[2]], color=C_INK, lw=1.5,
        ls=(0, (6, 4)), zorder=5)
ax.plot(*circ, color=C_CIRC, lw=3.2, zorder=6)
ax.plot([pc[0], E[0]], [pc[1], E[1]], [pc[2], E[2]], color=C_CIRC,
        lw=1.8, zorder=7)
ax.plot([S[0], E[0]], [S[1], E[1]], [S[2], E[2]], color=C_BONE, lw=5.5,
        zorder=8, solid_capstyle="round")
ax.plot([E[0], W[0]], [E[1], W[1]], [E[2], W[2]], color=C_BONE, lw=5.5,
        zorder=8, solid_capstyle="round")

# the angle j at the shoulder
ta = np.linspace(0, j_sh, 40)
arca = S[:, None] + 0.085 * (np.outer(g1, np.cos(ta)) + np.outer(g2, np.sin(ta)))
ax.plot(*arca, color=C_INK, lw=1.3, zorder=9)

# the direction memory from the shoulder and its projection onto the circle
mem_end = S + 1.35 * L1 * u_mem
ax.plot([S[0], mem_end[0]], [S[1], mem_end[1]], [S[2], mem_end[2]],
        color=C_MEM, lw=2.6, zorder=7)
ax.plot([mem_end[0], E[0]], [mem_end[1], E[1]], [mem_end[2], E[2]],
        color=C_MEM, lw=1.5, ls=(0, (2, 3)), zorder=7)

for p, col, size in ((S, C_INK, 66), (W, C_OBJ, 66), (E, C_CIRC, 76),
                     (pc, C_CIRC, 34)):
    ax.scatter(*p, s=size, c=[col], edgecolors="white", linewidths=1.4,
               depthshade=False, zorder=10)


def lab(p, text, off, color=C_INK, fs=13.5):
    q = np.asarray(p, float) + np.asarray(off, float)
    ax.text(q[0], q[1], q[2], text, color=color, fontsize=fs,
            ha="center", va="center", zorder=12)


lab(S, "$p_{\\mathrm{sh}}$", (0.0, 0.058, 0.020))
lab(W, "$p_{\\mathrm{wr}}$", (0.0, -0.058, -0.022), C_OBJ)
lab(E, "$p_{\\mathrm{el}}$", (0.0, -0.048, 0.042), C_CIRC)
lab(pc, "$p_{\\mathrm{c}}$", (0.0, -0.030, -0.052), C_CIRC)
lab(0.5 * (pc + E), "$r_{\\mathrm{c}}$", (0.0, 0.042, 0.0), C_CIRC)
lab(0.5 * (S + E), "$L_1$", (0.0, 0.048, 0.012), C_BONE)
lab(0.5 * (E + W), "$L_2$", (0.0, -0.034, 0.024), C_BONE)
lab(0.78 * S + 0.22 * W, "$r$", (0.0, 0.010, -0.050))
lab(mem_end, "$\\widehat{u}$", (0.0, -0.036, 0.040), C_MEM)
lab(S + 0.115 * (np.cos(0.5 * j_sh) * g1 + np.sin(0.5 * j_sh) * g2),
    "$j$", (0.0, 0.0, 0.0))

# name the two spheres in the panel corners, clear of the geometry
ax.text2D(0.02, 0.20, "sphere of radius $L_2$\nabout $p_{\\mathrm{wr}}$",
          transform=ax.transAxes, fontsize=11, color=C_SPH2,
          ha="left", va="center")
ax.text2D(0.98, 0.20, "sphere of radius $L_1$\nabout $p_{\\mathrm{sh}}$",
          transform=ax.transAxes, fontsize=11, color=C_SPH1,
          ha="right", va="center")

# tight, true-aspect view box around everything drawn
cap1 = np.array(cap(S, L1, bh, j_sh)).reshape(3, -1)
cap2 = np.array(cap(W, L2, -bh, j_wr)).reshape(3, -1)
allpts = np.column_stack(
    [circ, cap1, cap2, np.column_stack([S, W, E, pc, mem_end])])
lo, hi = allpts.min(axis=1), allpts.max(axis=1)
ctr, span = 0.5 * (lo + hi), (hi - lo)
span = np.maximum(span * 1.06, 0.10)
ax.set_xlim(ctr[0] - span[0] / 2, ctr[0] + span[0] / 2)
ax.set_ylim(ctr[1] - span[1] / 2, ctr[1] + span[1] / 2)
ax.set_zlim(ctr[2] - span[2] / 2, ctr[2] + span[2] / 2)
ax.set_box_aspect(tuple(span))
ax.set_title("The elbow lies on the circle where the two spheres meet",
             fontsize=12.5, color=C_INK, y=0.94)

# --- inset: the circle seen along the shoulder-to-wrist line ----------
axi = fig.add_axes([0.645, 0.42, 0.28, 0.50])
axi.set_aspect("equal")
axi.axis("off")
axi.set_xlim(-1.80, 1.80)
axi.set_ylim(-1.70, 1.80)
axi.add_patch(Circle2D((0, 0), 1.0, fc="none", ec=C_CIRC, lw=2.8))
axi.scatter([0], [0], s=32, c=[C_CIRC], zorder=5)
ang = np.radians(56.0)
Ei = np.array([np.cos(ang), np.sin(ang)])
mi = np.array([np.cos(np.radians(78.0)), np.sin(np.radians(78.0))]) * 1.50
axi.add_patch(FancyArrowPatch((0, 0), tuple(mi), arrowstyle="-|>",
                              mutation_scale=14, color=C_MEM, lw=2.4))
axi.plot([0, Ei[0]], [0, Ei[1]], color=C_CIRC, lw=1.8)
axi.plot([mi[0], Ei[0]], [mi[1], Ei[1]], color=C_MEM, lw=1.5,
         ls=(0, (2, 3)))
axi.scatter(*Ei, s=76, c=[C_CIRC], edgecolors="white", linewidths=1.2,
            zorder=6)
axi.text(Ei[0] + 0.18, Ei[1] - 0.08, "$p_{\\mathrm{el}}$", fontsize=13.5,
         color=C_CIRC, ha="left", va="center")
axi.text(mi[0] + 0.12, mi[1] + 0.06, "$\\widehat{u}$", fontsize=13.5,
         color=C_MEM, ha="left", va="center")
axi.text(-0.16, -0.22, "$p_{\\mathrm{c}}$", fontsize=13.5, color=C_CIRC,
         ha="right", va="center")
axi.text(0.56, 0.40, "$r_{\\mathrm{c}}$", fontsize=13.5, color=C_CIRC,
         ha="center", va="center")
axi.set_title("seen along the shoulder-to-wrist line", fontsize=11.5,
              color=C_INK, y=1.00)
axi.text(0, -1.42, "the chosen elbow is closest to the position\n"
                   "predicted from the current shoulder and\n"
                   "the remembered upper-arm direction",
         fontsize=9.8, color="#343a40", ha="center", va="center")

# --- symbol key -------------------------------------------------------
axk = fig.add_axes([0.635, 0.03, 0.35, 0.34])
axk.axis("off")
axk.set_xlim(0, 1)
axk.set_ylim(0, 1)
key = [
    ("$p_{\\mathrm{sh}},\\ p_{\\mathrm{el}},\\ p_{\\mathrm{wr}}$",
     "shoulder, elbow, wrist", C_INK),
    ("$L_1,\\ L_2$", "upper-arm and forearm lengths", C_BONE),
    ("$b,\\ \\widehat{b}$", "the dashed vector and its direction", C_INK),
    ("$r$", "its length, shoulder to wrist", C_INK),
    ("$j$", "angle at the shoulder", C_INK),
    ("$p_{\\mathrm{c}},\\ r_{\\mathrm{c}}$", "circle centre and radius",
     C_CIRC),
    ("$\\widehat{u}$", "direction memory of the upper arm", C_MEM),
]
for i, (sym, word, col) in enumerate(key):
    y = 0.94 - 0.138 * i
    axk.text(0.30, y, sym, fontsize=12.0, color=col, ha="right",
             va="center")
    axk.text(0.35, y, word, fontsize=10.2, color=C_INK, ha="left",
             va="center")

fig.savefig(OUT, dpi=200, facecolor="white")
print("saved", OUT)
