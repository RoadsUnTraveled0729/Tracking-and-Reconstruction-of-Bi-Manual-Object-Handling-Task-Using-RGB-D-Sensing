#!/usr/bin/env python3
"""Compose the Unity phase stills of Figure 7.10; the camera video is never opened.

Run render_ch7_trails.py first (closed editor). Every panel is the same
window cut from the same fixed orthographic view: the window is the union
of the drawn content (trajectories, waypoint marks, cube) over the three
stills plus a margin, measured from the pixels, so it follows the capture
rather than hand-tuned coordinates; the cut removes the empty wall and
desk bands only. Labels use the waypoint viewport positions logged by
Unity; the scale bar comes from the logged orthographic size, which must
be identical in the three records. Presentation only (D-019).
"""
import hashlib
import json
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image
from ch7_trail_data import ROOT, SETUPS, load

# argument: the recording alias (ch7_trail_data.SETUPS); r6b, the recording
# of Chapter 2 (Figure 7.10, default), or r7, the two-hand take (E-034),
# whose panels are the right hand, the hand-over and the left hand and
# whose legend carries the left wrist.
ALIAS = sys.argv[1] if len(sys.argv) > 1 else "r6b"
OUT = SETUPS[ALIAS]["figure"]
SRC = SETUPS[ALIAS]["src"]
COMPOSE = SETUPS[ALIAS]["compose"]
MARGIN = (60, 45, 50, 80)  # pixels kept left, above, right and below the drawn content


def content_window(stills):
    """Union bounding box of the coloured or dark pixels (trajectories,
    waypoint marks, cube) over the stills, plus MARGIN, clipped to the image."""
    rows, cols = [], []
    for still in stills:
        rgb = np.asarray(still.convert("RGB")).astype(int)
        drawn = ((rgb.max(-1) - rgb.min(-1)) > 60) | (rgb.max(-1) < 90)
        r, c = np.where(drawn)
        rows += [r.min(), r.max()]; cols += [c.min(), c.max()]
    width, height = stills[0].size
    return (max(min(cols) - MARGIN[0], 0), max(min(rows) - MARGIN[1], 0),
            min(max(cols) + MARGIN[2] + 1, width), min(max(rows) + MARGIN[3] + 1, height))


data = load(ALIAS)
fig = plt.figure(figsize=(8.4, 7.4))
if ALIAS == "r6b":
    # two short intervals above, the long slide below at twice the magnification
    grid = fig.add_gridspec(2, 2, height_ratios=[1, 2], hspace=0.16, wspace=0.05)
    axes = [fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1]), fig.add_subplot(grid[1, :])]
else:
    # the long right-hand interval above at twice the magnification, the
    # hand-over and the left-hand slide below, in the order of the task
    grid = fig.add_gridspec(2, 2, height_ratios=[2, 1], hspace=0.16, wspace=0.05)
    axes = [fig.add_subplot(grid[0, :]), fig.add_subplot(grid[1, 0]), fig.add_subplot(grid[1, 1])]
phases = data["phases"]
records = [json.loads((SRC / (phase["name"] + ".json")).read_text()) for phase in phases]
stills = [Image.open(SRC / (phase["name"] + ".png")) for phase in phases]
cameras = {(r["orthographicSize"], tuple(r["cameraPosition"].values()), tuple(r["cameraTarget"].values())) for r in records}
assert len(cameras) == 1, "The three stills must share one camera"
assert len({s.size for s in stills}) == 1, "The three stills must share one size"
CROP = content_window(stills)
print("crop window (left, top, right, bottom):", CROP)
for label, ax, phase, rec, still in zip("abc", axes, phases, records, stills):
    assert rec["appliedFrame"] == phase["last"]
    width, height = still.size
    image = still.crop(CROP)
    ax.imshow(image)
    ax.set_title(f"({label}) {phase.get('title', phase['name'].capitalize())}: "
                 f"frames {phase['first']}-{phase['last']}", fontsize=12, loc="left")
    for name, v, offset in zip(("Start", "W1", "W2", "W3"), rec["waypointViewport"],
                               ((0, -16), (-40, -12), (-40, 14), (-30, -22))):
        x, y = v["x"] * width - CROP[0], (1 - v["y"]) * height - CROP[1]
        ax.annotate(name, xy=(x, y), xytext=offset, textcoords="offset points",
                    fontsize=10, ha="center", va="center", color="0.1",
                    bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.92),
                    arrowprops=dict(arrowstyle="-", color="0.25", lw=0.6))
    # Orthographic scale in the image plane; the projection is uniform, so
    # 0.1 m spans this many pixels anywhere in the still.
    bar_px = 0.1 * height / (2 * rec["orthographicSize"])
    x, y = image.width * 0.80 - bar_px / 2, image.height * 0.93
    ax.plot([x, x + bar_px], [y, y], color="0.15", lw=2)
    ax.text(x + bar_px / 2, y - image.height * 0.035, "10 cm", ha="center", fontsize=10,
            bbox=dict(fc="white", ec="none", alpha=0.9, pad=1.5))
    ax.set_axis_off()
if "wrist_left" in data:
    first = phases[0]["first"]
    drawn_states = set()
    for key in ("wrist", "wrist_left"):
        sel = data[key]["frames"] >= first
        drawn_states |= set(int(v) for v in np.unique(data[key]["states"][sel]))
    handles = [Line2D([], [], color="0.2", ls="--", label="Waypoint reference"),
               Line2D([], [], color="tab:green", label="Marker origin"),
               Line2D([], [], color="tab:blue", label="Right wrist: measured input"),
               Line2D([], [], color="tab:orange", label="Right wrist: rebuilt"),
               Line2D([], [], color="tab:purple", label="Left wrist: measured input"),
               Line2D([], [], color="tab:pink", label="Left wrist: rebuilt")]
    if 1 in drawn_states:
        handles.append(Line2D([], [], color="0.45", label="Either wrist: held"))
    ncol = 3 if len(handles) > 6 else 2
else:
    handles = [Line2D([], [], color="0.2", ls="--", label="Waypoint reference"),
               Line2D([], [], color="tab:green", label="Marker origin"),
               Line2D([], [], color="tab:blue", label="Wrist: measured input"),
               Line2D([], [], color="tab:orange", label="Wrist: rebuilt")]
    ncol = 2
fig.legend(handles=handles, loc="lower center", ncol=ncol, fontsize=11, frameon=False)
fig.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.09 if ncol == 2 else 0.12)
fig.savefig(OUT, dpi=200, bbox_inches="tight", pad_inches=0.05)
# Record which capture this composition used, so the validator can tell a
# figure composed from an earlier capture from one composed from the
# manifest on disk.
COMPOSE.write_text(json.dumps({
    "manifest_sha256": hashlib.sha256((SRC / "manifest.json").read_bytes()).hexdigest(),
    "crop": [int(v) for v in CROP],
    "figure_sha256": hashlib.sha256(OUT.read_bytes()).hexdigest()}, indent=2) + "\n")
print("saved", OUT)
