"""Figure 2.1 (v5): system flow diagram with the developing chapter named on
every stage (user request 2026-08-04: the graph did not show all the related
chapters). Layout carried from the fig-2.1 block of
writing/v2/scripts/make_ch2_figs.py; the ".bag" file-name mention is dropped
per skill rule 11. Adds a note pointing at Chapter 6 (evaluation) and
Chapter 7 (real-time variant).
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

FIG = "/home/luo/Desktop/New_SandBox/writing/v6/figures"


def box(ax, x, y, w, h, text, fc):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012",
                                fc=fc, ec="0.25", lw=1.1))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=8.4)


def arrow(ax, x0, y0, x1, y1, text=None):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=13, color="0.2", lw=1.2))
    if text:
        ax.text((x0+x1)/2 + 0.005, (y0+y1)/2, text, fontsize=7.3,
                color="0.25", ha="left")


fig, ax = plt.subplots(figsize=(10.5, 5.6))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
C_SENS, C_A, C_B, C_F = "#dbe9f6", "#e3f2df", "#fdeeda", "#ece1f2"
box(ax, 0.02, 0.42, 0.15, 0.16, "RealSense D435\nrecording, 640x480\nat 30 fps (Chapter 2)", C_SENS)
box(ax, 0.22, 0.42, 0.15, 0.16, "Frame replay +\ndepth-to-color\nalignment (Chapter 2)", C_SENS)
box(ax, 0.44, 0.68, 0.16, 0.15, "MediaPipe Pose,\n8 upper-body landmarks\n+ visibility (Chapter 2)", C_A)
box(ax, 0.64, 0.68, 0.15, 0.15, "Depth fusion +\nvalidity gating +\nfilter (Chapter 2)", C_A)
box(ax, 0.82, 0.68, 0.16, 0.15, "Kinematic solver,\njoint angles\n(Chapter 3)", C_A)
box(ax, 0.44, 0.17, 0.16, 0.15, "ArUco detection,\nplanar pose per\nmarker (Chapter 4)", C_B)
box(ax, 0.64, 0.17, 0.15, 0.15, "Scene calibration\n+ world anchoring\n(Chapter 4)", C_B)
box(ax, 0.82, 0.17, 0.16, 0.15, "Object track\nfilter, world frame\n(Chapter 4)", C_B)
box(ax, 0.70, 0.42, 0.13, 0.15, "Data fusion,\nshared frame index\n(Chapter 4)", C_F)
box(ax, 0.86, 0.42, 0.12, 0.15, "Unity scene\n(Chapter 5)", C_F)
arrow(ax, 0.17, 0.50, 0.22, 0.50)
arrow(ax, 0.37, 0.53, 0.44, 0.74, "color + depth")
arrow(ax, 0.37, 0.47, 0.44, 0.26, "color")
arrow(ax, 0.60, 0.755, 0.64, 0.755)
arrow(ax, 0.79, 0.755, 0.82, 0.755)
arrow(ax, 0.895, 0.68, 0.77, 0.57)
arrow(ax, 0.60, 0.245, 0.64, 0.245)
arrow(ax, 0.79, 0.245, 0.82, 0.245)
arrow(ax, 0.895, 0.32, 0.77, 0.43)
arrow(ax, 0.83, 0.495, 0.86, 0.495)
ax.text(0.735, 0.60, "shared memory / UDP (Chapter 5)", fontsize=7.3,
        color="0.25", ha="right")
ax.text(0.02, 0.30, "Chapter 6 evaluates the two pipelines\n"
                    "against each other; Chapter 7 builds\n"
                    "a real-time variant of this whole flow.",
        fontsize=8.2, color="0.3", style="italic", va="top")
ax.text(0.52, 0.93, "Pipeline A: person tracking", fontsize=9.5, color="#3a6b35")
ax.text(0.52, 0.055, "Pipeline B: scene and object tracking", fontsize=9.5, color="#8a5a1e")
plt.tight_layout()
plt.savefig(FIG + "/fig1_system_flow.png", dpi=150)
print("saved", FIG + "/fig1_system_flow.png")
