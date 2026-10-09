#!/usr/bin/env python3
"""Figures redrawn for the condensed Chapter 3.

Two changes the repeated-material map asks for, made without touching the
originals in writing/v8/figures:

1. ch3_fig_chain_segments.png: the chain photograph (old Figure 3.3) and the
   arm-segment photograph (old Figure 3.8) are the same worked-example image
   drawn twice, so they become one two-panel figure.
2. ch3_fig_tpose_a.png: panel (b) of the old Figure 3.5, the avatar in the
   T-pose, duplicates Figure 2.4(b), so only the laboratory panel survives.

Output: writing/v8/condensed/figures/
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
SRC = REPO / "writing" / "v8" / "figures"
OUT = REPO / "writing" / "v8" / "condensed" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

# --- 1. the two worked-example photographs as one two-panel figure ---
chain = Image.open(OUT / "ch3_fig_chain_photo.png")
arm = Image.open(SRC / "ch3_fig_arm_photo.png")

fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.2))
for ax, im, title in ((axes[0], chain, "(a) the chain of frames"),
                      (axes[1], arm, "(b) the four arm segments")):
    ax.imshow(im)
    ax.set_title(title, fontsize=15, loc="left")
    ax.axis("off")
fig.subplots_adjust(left=0.005, right=0.995, top=0.93, bottom=0.01, wspace=0.02)
fig.savefig(OUT / "ch3_fig_chain_segments.png", dpi=150)
plt.close(fig)

# --- 2. the laboratory panel of the reference-configuration figure ---
tpose = Image.open(SRC / "ch3_fig_tpose.png")
tpose.crop((12, 44, 840, 866)).save(OUT / "ch3_fig_tpose_a.png")

print("wrote", OUT / "ch3_fig_chain_segments.png")
print("wrote", OUT / "ch3_fig_tpose_a.png")
