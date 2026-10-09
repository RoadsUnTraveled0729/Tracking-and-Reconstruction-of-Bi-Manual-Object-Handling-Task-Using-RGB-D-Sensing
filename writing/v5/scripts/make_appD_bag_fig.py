"""Figure D.1: structure of the recorded session file, drawn as blocks.

Everything shown was read from the evaluation recording itself
(Video/recording_20260224_083945.bag): rosbag 2.0 magic, LZ4 chunk
compression, the topic tree (file version, device info, per-sensor info +
options, per-stream camera_info and tf, per-frame image data + metadata),
899 frames per stream, 30.0 s, 640x480 z16/bgr8 at 30 fps.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

OUT = "/home/luo/Desktop/New_SandBox/writing/v5/figures/"

fig, ax = plt.subplots(figsize=(10.2, 5.8))
ax.set_xlim(0, 10.2)
ax.set_ylim(0, 5.8)
ax.axis("off")

# outer container
ax.add_patch(Rectangle((0.15, 0.35), 9.9, 4.9, facecolor="#f7f7f7",
                       edgecolor="black", lw=1.4))
ax.text(5.1, 4.95, "recorded bag file (rosbag 2.0 container, LZ4-compressed chunks)",
        ha="center", fontsize=11, fontweight="bold")

def block(x, y, w, h, lines, fc, fs=8.6):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor="black", lw=1.0))
    ax.text(x + w / 2, y + h / 2, "\n".join(lines), ha="center", va="center", fontsize=fs)

# ---- left half: one-time description, written at the start ---------------
ax.text(2.55, 4.45, "description, written once at the start",
        ha="center", fontsize=9.6, style="italic")
C1 = "#f4e3c1"
block(0.45, 3.55, 4.2, 0.6, ["file version"], C1)
block(0.45, 2.80, 4.2, 0.6, ["device description"], C1)
block(0.45, 1.80, 4.2, 0.85, ["sensor descriptions and the value of",
                              "every sensor option at record time",
                              "(exposure, gain, laser power, ...)"], C1)
block(0.45, 0.70, 4.2, 0.95, ["per-stream calibration:",
                              "camera intrinsics (camera_info)",
                              "and stream pose (tf)"], C1)

# ---- right half: per-frame messages --------------------------------------
ax.text(7.45, 4.45, "data, written per captured frame",
        ha="center", fontsize=9.6, style="italic")
C2 = "#cfe3f5"
block(5.25, 2.95, 4.4, 1.2, ["depth stream, 899 frames",
                             "image message: 640 x 480, z16 (16-bit)",
                             "metadata message: timestamps, counters"], C2)
block(5.25, 1.45, 4.4, 1.2, ["colour stream, 899 frames",
                             "image message: 640 x 480, bgr8 (24-bit)",
                             "metadata message: timestamps, counters"], C2)
ax.add_patch(FancyArrowPatch((5.45, 0.95), (9.45, 0.95), arrowstyle="-|>",
                             mutation_scale=15, lw=1.4, color="0.25"))
ax.text(7.45, 0.62, "time: 30.0 seconds at 30 frames per second",
        ha="center", fontsize=8.6, color="0.25")

plt.tight_layout()
plt.savefig(OUT + "appD_fig_bag.png", dpi=150, bbox_inches="tight")
print("saved", OUT + "appD_fig_bag.png")
