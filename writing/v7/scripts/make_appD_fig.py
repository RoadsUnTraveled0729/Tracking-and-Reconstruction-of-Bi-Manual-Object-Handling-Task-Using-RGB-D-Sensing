#!/usr/bin/env python3
"""Appendix D figure: pinhole projection and depth-to-colour alignment.

  (a) the pinhole geometry the intrinsic matrix describes: a scene point,
      the ray to the camera centre, and the pixel where that ray crosses
      the image plane.
  (b) how the two imagers of the sensor are brought onto one pixel grid,
      so that a colour pixel and the depth value at the same coordinates
      describe the same physical point.

The intrinsics printed in the drawing are the factory values carried by
the rail recording, read from the extractor metadata.

Output: writing/v7/figures/appD_fig_alignment.png
Run:    python writing/v7/scripts/make_appD_fig.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v7" / "figures"
META = (REPO / "v1" / "mediapipe" / "output"
        / "recording_20260831_065553_landmarks_raw.meta.json")

intr = json.loads(META.read_text())["color_intrinsics"]
print("intrinsics:", intr)

fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.3))

# ---- (a) pinhole geometry -------------------------------------------------
ax = axes[0]
ax.set_xlim(-0.7, 3.3)
ax.set_ylim(-1.35, 1.35)
ax.axis("off")
ax.scatter([0], [0], color="black", s=48, marker="s")
ax.annotate("camera centre", (0, 0), textcoords="offset points",
            xytext=(-8, -18), fontsize=8.5)
ax.add_patch(FancyArrowPatch((0, 0), (1.0, 0), arrowstyle="-|>",
                             mutation_scale=12, color="#0077b6"))
ax.text(1.03, 0.04, "z, the optical axis", fontsize=8.5, color="#0077b6")
ax.add_patch(FancyArrowPatch((0, 0), (0, -0.75), arrowstyle="-|>",
                             mutation_scale=12, color="#2a9d8f"))
ax.text(0.04, -0.86, "y, downward in the image", fontsize=8.5, color="#2a9d8f")
ax.plot([0.75, 0.75], [-1.05, 1.05], color="0.3", lw=1.5)
ax.text(0.72, 1.12, "image plane", fontsize=8.5)
scene = (2.7, 0.95)
ax.scatter(*scene, color="#c1121f", s=34)
ax.text(scene[0] + 0.06, scene[1], "scene point p = (x, y, z)", fontsize=8.5)
ax.plot([0, scene[0]], [0, scene[1]], color="0.55", ls="--", lw=1.0)
s = 0.75 / scene[0]
ax.scatter([0.75], [scene[1] * s], color="#c1121f", s=26, marker="x")
ax.text(0.80, scene[1] * s - 0.03, "pixel (u, v)", fontsize=8.5)
ax.set_title("(a) pinhole projection geometry", fontsize=10)

# ---- (b) depth-to-colour alignment ---------------------------------------
ax = axes[1]
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis("off")
ax.add_patch(FancyBboxPatch((0.35, 3.45), 3.0, 1.9,
                            boxstyle="round,pad=0.05", fc="#dbe9f6", ec="0.3"))
ax.text(1.85, 4.40, "depth imager\n%d x %d\n(infrared stereo pair)"
        % (intr["width"], intr["height"]), ha="center", fontsize=8.4)
ax.add_patch(FancyBboxPatch((0.35, 0.60), 3.0, 1.9,
                            boxstyle="round,pad=0.05", fc="#e3f2df", ec="0.3"))
ax.text(1.85, 1.55, "colour camera\n%d x %d\nfx %.1f  fy %.1f\ncx %.1f  cy %.1f"
        % (intr["width"], intr["height"], intr["fx"], intr["fy"],
           intr["ppx"], intr["ppy"]), ha="center", fontsize=8.4)
ax.add_patch(FancyBboxPatch((5.7, 2.0), 4.0, 2.0,
                            boxstyle="round,pad=0.05", fc="#fdeeda", ec="0.3"))
ax.text(7.7, 3.0, "aligned depth image\non the same %d x %d pixel grid\n"
        "as the colour image" % (intr["width"], intr["height"]),
        ha="center", fontsize=8.4)
ax.add_patch(FancyArrowPatch((3.45, 4.30), (5.70, 3.45), arrowstyle="-|>",
                             mutation_scale=13, color="0.2"))
ax.text(3.70, 4.42, "lift to 3D, move through the\nknown offset between the\n"
        "imagers, project with the\ncolour intrinsics", fontsize=7.5)
ax.add_patch(FancyArrowPatch((3.45, 1.60), (5.70, 2.50), arrowstyle="-|>",
                             mutation_scale=13, color="0.2"))
ax.text(3.75, 1.20, "supplies the target pixel grid", fontsize=7.5)
ax.set_title("(b) depth-to-colour alignment", fontsize=10)

plt.tight_layout()
out = FIG / "appD_fig_alignment.png"
plt.savefig(out, dpi=170, bbox_inches="tight")
print("saved", out)
