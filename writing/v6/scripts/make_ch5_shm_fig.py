"""Figure 5.2: how the shared memory transport works, drawn as a memory block.

The layout is the real PSI1 integrated packet of integration/
send_integrated_scene.py: struct format <IIif3f13f3f3fHH, 108 bytes,
offsets 0/4/8/12/16/28/80/92/104/106. The writer and reader protocols are
the seqlock described in Chapter 5: counter odd while writing, even when
stable; the reader copies, re-checks, and discards a torn copy.
Supervisor request (2026-08-03): illustrate the memory operations with a
block representing the memory.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

OUT = "/home/luo/Desktop/New_SandBox/writing/v6/figures/"

# (byte range label, field label, kind)  kind: hdr = seqlock header, pay = payload
FIELDS = [
    ("0-3",     "magic code 'PSI1'",              "hdr"),
    ("4-7",     "sequence counter",               "hdr"),
    ("8-11",    "frame index",                    "pay"),
    ("12-15",   "timestamp (seconds)",            "pay"),
    ("16-27",   "pelvis position (3 floats)",     "pay"),
    ("28-79",   "13 joint angles (13 floats)",    "pay"),
    ("80-91",   "object position (3 floats)",     "pay"),
    ("92-103",  "object Euler angles (3 floats)", "pay"),
    ("104-105", "joint live mask",                "pay"),
    ("106-107", "object live flag",               "pay"),
]

COL_HDR = "#f4c7a1"
COL_PAY = "#cfe3f5"

fig, ax = plt.subplots(figsize=(10.2, 6.2))
ax.set_xlim(0, 10.2)
ax.set_ylim(0, 6.2)
ax.axis("off")

# ---- central memory block ----------------------------------------------
bx, bw = 3.85, 2.75
top, cell_h = 5.35, 0.42
for i, (rng, label, kind) in enumerate(FIELDS):
    y = top - (i + 1) * cell_h
    ax.add_patch(Rectangle((bx, y), bw, cell_h, facecolor=COL_HDR if kind == "hdr" else COL_PAY,
                           edgecolor="black", lw=1.0))
    ax.text(bx + 0.07, y + cell_h / 2, rng, ha="left", va="center", fontsize=7.2, color="0.3")
    ax.text(bx + 0.62 + (bw - 0.62) / 2, y + cell_h / 2, label,
            ha="center", va="center", fontsize=8.6)
ax.text(bx + bw / 2, top + 0.34, "shared memory file, one record, 108 bytes",
        ha="center", fontsize=10, fontweight="bold")
ax.text(bx + 0.07, top + 0.05, "byte", ha="left", va="center", fontsize=7.2, color="0.3")

bot = top - len(FIELDS) * cell_h
# legend swatches under the block
ax.add_patch(Rectangle((bx, bot - 0.55), 0.28, 0.28, facecolor=COL_HDR, edgecolor="black", lw=0.8))
ax.text(bx + 0.36, bot - 0.41, "seqlock header", va="center", fontsize=8.2)
ax.add_patch(Rectangle((bx + 1.45, bot - 0.55), 0.28, 0.28, facecolor=COL_PAY, edgecolor="black", lw=0.8))
ax.text(bx + 1.45 + 0.36, bot - 0.41, "payload", va="center", fontsize=8.2)

# ---- writer (left) ------------------------------------------------------
wx, wy, ww, wh = 0.15, 2.6, 3.0, 2.1
ax.add_patch(Rectangle((wx, wy), ww, wh, facecolor="#e8f2e2", edgecolor="black", lw=1.2))
ax.text(wx + ww / 2, wy + wh - 0.3, "Python sender", ha="center", fontsize=10, fontweight="bold")
ax.text(wx + ww / 2, wy + wh - 0.62, "one write per frame", ha="center", fontsize=8.4, style="italic")
ax.text(wx + 0.18, wy + wh - 1.02, "1.  counter + 1  (odd: busy)", fontsize=8.8, va="center")
ax.text(wx + 0.18, wy + wh - 1.40, "2.  write the payload fields", fontsize=8.8, va="center")
ax.text(wx + 0.18, wy + wh - 1.78, "3.  counter + 1  (even: stable)", fontsize=8.8, va="center")

# ---- reader (right) -----------------------------------------------------
rx, ry, rw, rh = 7.0, 2.35, 3.05, 2.6
ax.add_patch(Rectangle((rx, ry), rw, rh, facecolor="#ede6f4", edgecolor="black", lw=1.2))
ax.text(rx + rw / 2, ry + rh - 0.3, "Unity receiver", ha="center", fontsize=10, fontweight="bold")
ax.text(rx + rw / 2, ry + rh - 0.62, "one read per rendered frame", ha="center", fontsize=8.4, style="italic")
ax.text(rx + 0.15, ry + rh - 1.02, "1.  read the counter", fontsize=8.8, va="center")
ax.text(rx + 0.15, ry + rh - 1.40, "2.  copy the whole record", fontsize=8.8, va="center")
ax.text(rx + 0.15, ry + rh - 1.78, "3.  read the counter again", fontsize=8.8, va="center")
ax.text(rx + 0.15, ry + rh - 2.16, "4.  even and unchanged: keep;", fontsize=8.8, va="center")
ax.text(rx + 0.42, ry + rh - 2.44, "otherwise discard and retry", fontsize=8.8, va="center")

# ---- arrows -------------------------------------------------------------
mid = (top + bot) / 2
ax.add_patch(FancyArrowPatch((wx + ww + 0.05, mid + 0.25), (bx - 0.06, mid + 0.25),
                             arrowstyle="-|>", mutation_scale=16, lw=1.6, color="#3a7d34"))
ax.text((wx + ww + bx) / 2, mid + 0.44, "write", ha="center", fontsize=8.6, color="#3a7d34")
ax.add_patch(FancyArrowPatch((bx + bw + 0.06, mid - 0.25), (rx - 0.05, mid - 0.25),
                             arrowstyle="-|>", mutation_scale=16, lw=1.6, color="#5b3d8f"))
ax.text((bx + bw + rx) / 2, mid - 0.06, "copy", ha="center", fontsize=8.6, color="#5b3d8f")

ax.text(5.1, 0.28, "one writer, one reader, no locks: a read torn by a concurrent write "
                   "is detected by the counter and simply retried",
        ha="center", fontsize=8.8, style="italic", color="0.2")

plt.tight_layout()
plt.savefig(OUT + "ch5_fig_shm.png", dpi=150, bbox_inches="tight")
print("saved", OUT + "ch5_fig_shm.png")
