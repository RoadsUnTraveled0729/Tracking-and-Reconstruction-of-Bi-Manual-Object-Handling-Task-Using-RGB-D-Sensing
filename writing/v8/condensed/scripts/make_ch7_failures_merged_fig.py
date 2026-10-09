#!/usr/bin/env python3
"""Condensed build: merge the two rejection timelines into one figure.

REPEATED_MATERIAL_MAP.md section 4 lists Figure 7.4 (rail recording) and
Figure 7.5 (loop recording) as the same figure type, one per recording,
to be merged into a single two-panel figure. Both panels are the frozen
drawings produced by writing/v7/scripts/make_ch7_rail_failures_fig.py and
writing/v7/scripts/make_ch7_figs.py; this script only stacks them, so no
plotted value changes and supervisor comment C39 (both timelines kept) is
still answered.

Inputs:  writing/v7/figures/ch7_fig_failures_rail.png  (upper panel)
         writing/v7/figures/ch7_fig_failures.png       (lower panel)
Output:  writing/v8/condensed/figures/ch7_fig_failures_both.png
Run:     python3 writing/v8/condensed/scripts/make_ch7_failures_merged_fig.py
"""
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[4]
SRC = REPO / "writing" / "v7" / "figures"
OUT = REPO / "writing" / "v8" / "condensed" / "figures"
GUTTER = 24  # white rows between the two panels

top = Image.open(SRC / "ch7_fig_failures_rail.png").convert("RGB")
bottom = Image.open(SRC / "ch7_fig_failures.png").convert("RGB")

width = max(top.width, bottom.width)
height = top.height + GUTTER + bottom.height
canvas = Image.new("RGB", (width, height), "white")
canvas.paste(top, ((width - top.width) // 2, 0))
canvas.paste(bottom, ((width - bottom.width) // 2, top.height + GUTTER))

OUT.mkdir(parents=True, exist_ok=True)
path = OUT / "ch7_fig_failures_both.png"
canvas.save(path, dpi=(200, 200))
print("saved", path, canvas.size)
