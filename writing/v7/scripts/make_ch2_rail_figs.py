#!/usr/bin/env python3
"""Chapter 2 rail-scenario figures (scenario separation round, 2026-08-31).

Two composites from the laboratory photographs of the no-occlusion rail
setup (writing/v7/figures/src/rail_*.jpg, supplied by the user
2026-08-31) and one colour frame of the rail recording:

  ch2_fig_rail_setup.png  (a) the drawn working area from above, with
                          the rail and the cube at its start; (b) the
                          scene from behind the sensor; (c) a frame of
                          the rail recording with the slide under way.
  ch2_fig_rail_dims.png   (a) the tape along the rail; (b) the tape
                          upright against the rail resting on its edge.

Output: writing/v7/figures/ch2_fig_rail_setup.png, ch2_fig_rail_dims.png
Run:    python writing/v7/scripts/make_ch2_rail_figs.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

REPO = Path(__file__).resolve().parents[3]
SRC = REPO / "writing" / "v7" / "figures" / "src"
OUT = REPO / "writing" / "v7" / "figures"


def panel(ax, path, letter):
    im = Image.open(path)
    im.thumbnail((1400, 1400))
    ax.imshow(im)
    ax.axis("off")
    ax.set_title(f"({letter})", fontsize=11, loc="left")


def call(ax, text, xy, xytext):
    ax.annotate(text, xy=xy, xytext=xytext, fontsize=8.2, color="white",
                ha="left", va="center",
                bbox=dict(boxstyle="round,pad=0.3", fc="black", alpha=0.72),
                arrowprops=dict(arrowstyle="->", color="#ffd60a", lw=1.5))


# --- setup composite ---------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(12.6, 4.4))
panel(axes[0], SRC / "rail_setup_top.jpg", "a")
# thumbnail of 4032x3024 -> 1400x1050
call(axes[0], "drawn working area\n45 by 30 cm", (770, 480), (830, 300))
call(axes[0], "rail", (330, 750), (450, 620))
call(axes[0], "cube with its\nobject marker", (120, 720), (60, 500))
call(axes[0], "spirit level", (60, 280), (150, 160))
call(axes[0], "desk marker", (330, 55), (430, 120))

panel(axes[1], SRC / "rail_setup_wide.jpg", "b")
# portrait 3024x4032 -> 1050x1400
call(axes[1], "RGB-D camera", (540, 1310), (600, 1200))
call(axes[1], "desk marker", (560, 950), (640, 1050))
call(axes[1], "rail and the\ncarried cube", (600, 690), (330, 560))

panel(axes[2], SRC / "r6b_frame00750.jpg", "c")
# 640x480 frame, cube mid-rail in the right hand
call(axes[2], "cube sliding\nalong the rail", (330, 335), (420, 240))
plt.tight_layout()
plt.savefig(OUT / "ch2_fig_rail_setup.png", dpi=180, bbox_inches="tight")
plt.close(fig)

# --- dimensions composite ----------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.2))
panel(axes[0], SRC / "rail_length_measure.jpg", "a")
panel(axes[1], SRC / "rail_height_measure.jpg", "b")
plt.tight_layout()
plt.savefig(OUT / "ch2_fig_rail_dims.png", dpi=180, bbox_inches="tight")
print("saved", OUT / "ch2_fig_rail_setup.png")
print("saved", OUT / "ch2_fig_rail_dims.png")
