#!/usr/bin/env python3
"""Chapter 7 figure: colour frames of the recording above the Unity
reconstruction of the same moments (supervisor C37).

The four moments are those of the frame strip (ch7_frames_strip.json):
the grasp on the desk, the lift onto the rail, the slide and the far end.
The Unity renders come from the unattended sensor-view capture of the
recovery stream (eval/unity_check/run_unity_capture.py --stem
recording_20260831_065553 --angles-csv eval/output/recovery_r6b/
angles_recovery.csv, 2026-09-07), one PNG per streamed frame, copied to
figures/src/r6b_unity_f{frame:05d}.png so the figure rebuilds without
Unity. The colour frames are figures/src/r6b_frame{frame:05d}.png
(make_ch7_frame_strip.py --extract).

The 2026-09-07 capture places the red held-group spheres on their
joints from the sensor view (Unity/Assets/Scripts/HeldMarkers.cs); the
earlier captures of frames 114 and 700 pushed them toward the editor's
main camera and they floated beside the body.

Output: writing/v9/figures/ch7_fig_unity_pairs.png
Run:    python writing/v9/scripts/make_ch7_unity_pairs.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

REPO = Path(__file__).resolve().parents[3]
FIGD = REPO / "writing" / "v9" / "figures"
SRC = FIGD / "src"
OUT = FIGD / "ch7_fig_unity_pairs.png"
CHOICE = FIGD / "ch7_frames_strip.json"

spec = json.loads(CHOICE.read_text())
panels = spec["panels"]
n = len(panels)
fig, axes = plt.subplots(2, n, figsize=(3.2 * n, 5.3))
for col, p in enumerate(panels):
    frame = p["frame"]
    colour = Image.open(SRC / f"r6b_frame{frame:05d}.png")
    unity = Image.open(SRC / f"r6b_unity_f{frame:05d}.png").crop((0, 0, 640, 480))
    for row, (img, what) in enumerate(((colour, "colour frame"),
                                       (unity, "reconstruction"))):
        ax = axes[row, col]
        ax.imshow(img)
        ax.set_xticks([]); ax.set_yticks([])
        for side in ax.spines.values():
            side.set_edgecolor("0.4"); side.set_linewidth(0.9)
        ax.set_title(f"({p['tag']}) {p['label']}, frame {frame}: {what}",
                     fontsize=8.6, loc="left", pad=4)
plt.tight_layout(w_pad=0.6, h_pad=0.9)
plt.savefig(OUT, dpi=200, bbox_inches="tight")
print("saved", OUT)
