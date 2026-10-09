#!/usr/bin/env python3
"""Chapter 6 figure: the shared memory drawn as memory blocks (supervisor
request of 2026-08-03, figure dropped between V6 and V7, restored 2026-09-07
at the user's request).

(a) The frame buffer (PSF1, v2/common/shm_ring.py): a 128 byte header and
    eight slots of 1,536,032 bytes each (32 byte slot header, 640 x 480 x 3
    bytes of colour, 640 x 480 x 2 bytes of depth). Frame n goes to slot
    n mod 8; the example slot holds frame 533 of the rail recording.
(b) The combined record (PSI2, v2/integration/v2_integrate.py, 112 bytes)
    with its byte offsets, the writer's protocol on the left and the
    reader's on the right (the sequence counter is odd while a write is in
    progress and even when the record is stable).

Output: writing/v9/figures/ch6_fig_buffer.png (Figure 6.2) and
        ch6_fig_records.png (Figure 6.3), one memory block each
Run:    python writing/v9/scripts/make_ch6_memory_fig.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

REPO = Path(__file__).resolve().parents[3]
OUT_BUF = REPO / "writing" / "v9" / "figures" / "ch6_fig_buffer.png"
OUT_REC = REPO / "writing" / "v9" / "figures" / "ch6_fig_records.png"

COL_HDR = "#f4c7a1"   # sequence counter header
COL_PAY = "#cfe3f5"   # payload
COL_IMG = "#dcebd2"   # image bytes
COL_META = "#ece4f2"  # buffer header
FS = 7.8

# ---------------------------------------------------------------- (a) frame buffer
fig = plt.figure(figsize=(6.4, 7.0)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 6.0); ax.set_ylim(-0.15, 6.85); ax.axis("off")
x0, w = 0.15, 1.6
ax.text(x0 + w / 2, 6.62, "12.3 MB shared memory file", ha="center", fontsize=FS, va="center")
y = 6.5; hh = 0.42
ax.add_patch(Rectangle((x0, y - hh), w, hh, facecolor=COL_META, edgecolor="black", lw=0.9))
ax.text(x0 + w / 2, y - hh / 2, "header, 128 bytes", ha="center", va="center", fontsize=FS)
sh = 0.5
for s_ in range(8):
    ys = y - hh - (s_ + 1) * sh
    ax.add_patch(Rectangle((x0, ys), w, sh, facecolor="#f3f3f3" if s_ != 4 else COL_PAY, edgecolor="black", lw=0.9))
    label = f"slot {s_}"
    if s_ == 5: label = "slot 5: frame 533"
    elif s_ == 4: label = "slot 4: frame 532"
    elif s_ == 6: label = "slot 6: frame 526"
    ax.text(x0 + w / 2, ys + sh / 2, label, ha="center", va="center", fontsize=FS - 0.2)
ybot_col = y - hh - 8 * sh
ax.text(x0 + w / 2, ybot_col - 0.2, "frame n goes to slot n mod 8;\nframe 534 will overwrite slot 6", ha="center", va="top", fontsize=FS - 0.8, style="italic", color="0.25")

hx, hw = 2.2, 3.65; ch = 0.3
fields_h = [("0-3", "code 'PSF1'"), ("4-11", "version, slot count 8"), ("12-27", "slot size, image width and height"),
            ("28-43", "depth scale, hardware time of frame 0"), ("44-79", "intrinsics and distortion"),
            ("80-87", "end flag, frames published so far")]
ax.text(hx, 6.62, "header", fontsize=FS, va="center")
for i, (rng, lab) in enumerate(fields_h):
    yy = 6.5 - (i + 1) * ch
    ax.add_patch(Rectangle((hx, yy), hw, ch, facecolor=COL_META, edgecolor="black", lw=0.7))
    ax.text(hx + 0.06, yy + ch / 2, rng, fontsize=FS - 1.4, va="center", color="0.3")
    ax.text(hx + 0.65, yy + ch / 2, lab, fontsize=FS - 0.4, va="center")

sx, sw = 2.2, 3.65
fields_s = [("0-3", "slot sequence counter", COL_HDR), ("4-7", "frame index 533", COL_PAY),
            ("8-15", "padding", COL_PAY), ("16-23", "hardware timestamp", COL_PAY), ("24-31", "arrival time", COL_PAY),
            ("32-921,631", "colour, 640 x 480 x 3 bytes", COL_IMG), ("921,632-1,536,031", "depth, 640 x 480 x 2 bytes", COL_IMG)]
ytop = 4.15
ax.text(sx, ytop + 0.18, "one slot, 1,536,032 bytes", fontsize=FS, va="center")
for i, (rng, lab, col) in enumerate(fields_s):
    yy = ytop - (i + 1) * ch
    ax.add_patch(Rectangle((sx, yy), sw, ch, facecolor=col, edgecolor="black", lw=0.7))
    ax.text(sx + 0.06, yy + ch / 2, rng, fontsize=FS - 1.8, va="center", color="0.3")
    ax.text(sx + 1.35, yy + ch / 2, lab, fontsize=FS - 0.4, va="center")
ys4 = y - hh - 5 * sh + sh / 2
ax.add_patch(FancyArrowPatch((x0 + w + 0.03, ys4), (sx - 0.04, ytop - 0.15), arrowstyle="-", lw=0.8, color="0.4",
                             connectionstyle="arc3,rad=-0.2"))
ybot = ytop - len(fields_s) * ch
ax.text(0.15, ybot - 0.95, "capture process, per frame: raise the slot counter to odd, copy colour and depth,\nraise it to the next even value, then raise the count of frames published in the header",
        fontsize=FS - 0.6, va="top", color="#2f6b2a")
ly = ybot - 0.45
for k, (col, lab) in enumerate(((COL_META, "header"), (COL_HDR, "slot counter"), (COL_PAY, "slot fields"), (COL_IMG, "images"))):
    lx = (2.2, 3.15, 4.25, 5.25)[k]
    ax.add_patch(Rectangle((lx, ly), 0.2, 0.2, facecolor=col, edgecolor="black", lw=0.7))
    ax.text(lx + 0.26, ly + 0.1, lab, fontsize=FS - 1.2, va="center")
ax.text(0.15, ybot - 1.55, "each branch: find the newest published slot, copy it, read the slot counter\nagain; even and unchanged keeps the copy, anything else discards it.\nA slow reader is lapped after eight frames and loses whole frames.",
        fontsize=FS - 0.6, va="top", color="#5b3d8f")

plt.savefig(OUT_BUF, dpi=170, bbox_inches="tight"); print("saved", OUT_BUF); plt.close(fig)

# ---------------------------------------------------------------- (b) combined record
fig = plt.figure(figsize=(7.6, 6.2)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 7.6); ax.set_ylim(0.4, 6.85); ax.axis("off")
FIELDS = [("0-3", "code 'PSI2'", "hdr"), ("4-7", "sequence counter", "hdr"), ("8-11", "tick index", "pay"),
          ("12-15", "render time (s)", "pay"), ("16-27", "pelvis position (3 floats)", "pay"),
          ("28-79", "13 joint angles (13 floats)", "pay"), ("80-91", "object position (3 floats)", "pay"),
          ("92-103", "object Euler angles (3 floats)", "pay"), ("104-105", "live bits, 7 groups", "pay"),
          ("106-107", "object live bit", "pay"), ("108-109", "interpolation, blend flags", "pay"),
          ("110-111", "group states, 2 bits each", "pay")]
bx, bw = 2.45, 2.7; top, cell_h = 6.45, 0.37
ax.text(bx + bw / 2, top + 0.17, "one record, 112 bytes", ha="center", fontsize=FS, va="center")
for i, (rng, lab, kind) in enumerate(FIELDS):
    yy = top - (i + 1) * cell_h
    ax.add_patch(Rectangle((bx, yy), bw, cell_h, facecolor=COL_HDR if kind == "hdr" else COL_PAY, edgecolor="black", lw=0.8))
    ax.text(bx + 0.06, yy + cell_h / 2, rng, fontsize=FS - 1.6, va="center", color="0.3")
    ax.text(bx + 0.72 + (bw - 0.72) / 2, yy + cell_h / 2, lab, fontsize=FS - 1.0, va="center", ha="center")
bot = top - len(FIELDS) * cell_h
wx, wy, ww, wh = 0.05, 3.35, 1.95, 1.8
ax.add_patch(Rectangle((wx, wy), ww, wh, facecolor="#e8f2e2", edgecolor="black", lw=1.0))
ax.text(wx + ww / 2, wy + wh - 0.24, "merger (writer)", ha="center", fontsize=FS + 0.2, fontweight="bold")
ax.text(wx + ww / 2, wy + wh - 0.5, "one write per tick", ha="center", fontsize=FS - 0.8, style="italic")
for k, line in enumerate(["1. counter + 1 (odd: busy)", "2. write the payload", "3. counter + 1 (even: stable)"]):
    ax.text(wx + 0.08, wy + wh - 0.86 - 0.32 * k, line, fontsize=FS - 1.0, va="center")
rx, ry, rw, rh = 5.6, 3.1, 1.95, 2.05
ax.add_patch(Rectangle((rx, ry), rw, rh, facecolor="#ede6f4", edgecolor="black", lw=1.0))
ax.text(rx + rw / 2, ry + rh - 0.24, "Unity receiver", ha="center", fontsize=FS + 0.2, fontweight="bold")
ax.text(rx + rw / 2, ry + rh - 0.5, "one read per rendered frame", ha="center", fontsize=FS - 0.8, style="italic")
for k, line in enumerate(["1. read the counter", "2. copy the whole record", "3. read the counter again", "4. even and unchanged: keep,", "    otherwise discard, retry"]):
    ax.text(rx + 0.07, ry + rh - 0.84 - 0.28 * k, line, fontsize=FS - 1.1, va="center")
ya = 4.3
ax.add_patch(FancyArrowPatch((wx + ww + 0.04, ya), (bx - 0.04, ya), arrowstyle="-|>", mutation_scale=12, lw=1.3, color="#3a7d34"))
ax.text((wx + ww + bx) / 2, ya + 0.17, "write", ha="center", fontsize=FS - 1.2, color="#3a7d34")
ax.add_patch(FancyArrowPatch((bx + bw + 0.04, ya), (rx - 0.04, ya), arrowstyle="-|>", mutation_scale=12, lw=1.3, color="#5b3d8f"))
ax.text((bx + bw + rx) / 2, ya + 0.17, "copy", ha="center", fontsize=FS - 1.2, color="#5b3d8f")
ly = bot - 0.5
for k, (col, lab) in enumerate(((COL_HDR, "sequence counter header"), (COL_PAY, "payload"))):
    lx = (1.6, 4.2)[k]
    ax.add_patch(Rectangle((lx, ly), 0.24, 0.24, facecolor=col, edgecolor="black", lw=0.7))
    ax.text(lx + 0.32, ly + 0.12, lab, fontsize=FS - 0.7, va="center")
ax.text(3.8, ly - 0.4, "the person record (84 bytes), the object record (44) and the scene record (100) follow the same\npattern, code, counter, frame or tick, payload; every writer and reader runs the two protocols shown here",
        ha="center", fontsize=FS - 0.8, style="italic", color="0.25", va="top")

plt.savefig(OUT_REC, dpi=170, bbox_inches="tight"); print("saved", OUT_REC); plt.close(fig)
