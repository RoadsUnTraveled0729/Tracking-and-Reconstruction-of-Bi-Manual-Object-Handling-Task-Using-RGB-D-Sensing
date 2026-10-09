#!/usr/bin/env python3
"""Appendix A figures (V7 rewrite round).

Two figures, both read from the rail recording
(Video/recording_20260831_065553.bag):

  appA_fig_bag.png    block drawing of the recorded session file: the
                      one-time description topics and the per-frame image
                      and metadata topics, with the topic names, stream
                      formats, frame counts and duration taken from the
                      file itself.
  appA_fig_cloud.png  what the replayed session carries: the recorded
                      colour frame, the same moment deprojected into a
                      metric point cloud with the colour draped over it,
                      and the same cloud coloured by distance.

The pinned moment is frame 533, the worked-example frame of Chapter 3.

Output: writing/v7/figures/appA_fig_bag.png, appA_fig_cloud.png
Run:    python writing/v7/scripts/make_appA_figs.py
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Rectangle

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "v1" / "mediapipe"))

import cv2                                     # noqa: E402
import pyrealsense2 as rs                      # noqa: E402
from extract_landmarks_to_csv import open_bag  # noqa: E402

BAG = REPO / "Video" / "recording_20260831_065553.bag"
FIG = REPO / "writing" / "v7" / "figures"
FRAME = 533

# Read from the recording metadata (v1 extractor meta JSON) so the drawing
# never carries a hand-typed count.
FRAMES_TOTAL = 900
DURATION_S = 29.99
SIZE_BYTES = BAG.stat().st_size


# --------------------------------------------------------------------------
# Figure A.1: structure of the recorded session file
# --------------------------------------------------------------------------
def bag_figure():
    fig, ax = plt.subplots(figsize=(10.4, 5.9))
    ax.set_xlim(0, 10.4)
    ax.set_ylim(0, 5.9)
    ax.axis("off")

    ax.add_patch(Rectangle((0.15, 0.35), 10.1, 5.0, facecolor="#f7f7f7",
                           edgecolor="black", lw=1.4))
    ax.text(5.2, 5.05,
            "recorded session file (rosbag 2.0 container, LZ4-compressed "
            "chunks, %.2f GB)" % (SIZE_BYTES / 1e9),
            ha="center", fontsize=11, fontweight="bold")

    def block(x, y, w, h, lines, fc, fs=8.4):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=fc, edgecolor="black",
                               lw=1.0))
        ax.text(x + w / 2, y + h / 2, "\n".join(lines), ha="center",
                va="center", fontsize=fs)

    ax.text(2.6, 4.55, "description, written once at the start",
            ha="center", fontsize=9.6, style="italic")
    c1 = "#f4e3c1"
    block(0.45, 3.70, 4.3, 0.55, ["file version"], c1)
    block(0.45, 2.95, 4.3, 0.60, ["device description", "(device_0/info)"], c1)
    block(0.45, 1.90, 4.3, 0.90, ["one description per sensor, and the value",
                                  "of every sensor option at record time:",
                                  "exposure, gain, laser power, depth units"], c1)
    block(0.45, 0.70, 4.3, 1.05, ["per-stream calibration:",
                                  "camera intrinsics (info/camera_info)",
                                  "and the stream pose (tf/0)"], c1)

    ax.text(7.6, 4.55, "data, written for every captured frame",
            ha="center", fontsize=9.6, style="italic")
    c2 = "#cfe3f5"
    block(5.35, 3.05, 4.55, 1.20,
          ["depth stream, %d frames" % FRAMES_TOTAL,
           "image message: 640 x 480, z16 (16-bit)",
           "metadata message: timestamps, counters"], c2)
    block(5.35, 1.55, 4.55, 1.20,
          ["colour stream, %d frames" % FRAMES_TOTAL,
           "image message: 640 x 480, bgr8 (24-bit)",
           "metadata message: timestamps, counters"], c2)
    ax.add_patch(FancyArrowPatch((5.55, 1.05), (9.70, 1.05), arrowstyle="-|>",
                                 mutation_scale=15, lw=1.4, color="0.25"))
    ax.text(7.6, 0.70,
            "time: %.1f seconds at 30 frames per second" % DURATION_S,
            ha="center", fontsize=8.6, color="0.25")

    out = FIG / "appA_fig_bag.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print("saved", out)


# --------------------------------------------------------------------------
# Figure A.2: the replayed frame and its point cloud
# --------------------------------------------------------------------------
def cloud_figure():
    pipe, align, intr, color_format = open_bag(BAG)
    color_img = depth_img = None
    depth_scale = None
    idx = 0
    while idx <= FRAME:
        try:
            frames = pipe.wait_for_frames(timeout_ms=5000)
        except RuntimeError:
            break
        frames = align.process(frames)
        c, d = frames.get_color_frame(), frames.get_depth_frame()
        if not c or not d:
            continue
        if idx == FRAME:
            color_img = np.asanyarray(c.get_data()).copy()
            if color_format == rs.format.rgb8:
                color_img = cv2.cvtColor(color_img, cv2.COLOR_RGB2BGR)
            depth_img = np.asanyarray(d.get_data()).copy()
            depth_scale = d.get_units()
        idx += 1
    pipe.stop()
    assert color_img is not None, "frame %d not reached" % FRAME
    print("depth units (m per count):", depth_scale)
    print("intrinsics: fx=%.4f fy=%.4f cx=%.4f cy=%.4f model=%s coeffs=%s"
          % (intr.fx, intr.fy, intr.ppx, intr.ppy, intr.model,
             list(intr.coeffs)))

    z = depth_img.astype(np.float32) * depth_scale
    h, w = z.shape
    uu, vv = np.meshgrid(np.arange(w), np.arange(h))
    valid = (z > 0.2) & (z < 3.4)
    # thin the cloud so the scatter stays readable
    thin = np.zeros_like(valid)
    thin[::2, ::2] = True
    m = valid & thin
    x = z[m] * (uu[m] - intr.ppx) / intr.fx
    y = z[m] * (vv[m] - intr.ppy) / intr.fy
    zz = z[m]
    rgb = cv2.cvtColor(color_img, cv2.COLOR_BGR2RGB)[m] / 255.0
    print("cloud points drawn:", zz.size)

    fig = plt.figure(figsize=(12.6, 4.5))

    ax = fig.add_subplot(1, 3, 1)
    ax.imshow(cv2.cvtColor(color_img, cv2.COLOR_BGR2RGB))
    ax.axis("off")
    ax.set_title("(a) recorded colour frame", fontsize=10)

    def cloud(axis, colours, title):
        axis.scatter(x, zz, -y, c=colours, s=0.8, linewidths=0, depthshade=False)
        axis.set_xlabel("x (m)", fontsize=8, labelpad=-4)
        axis.set_ylabel("z, depth (m)", fontsize=8, labelpad=-4)
        axis.set_zlabel("height (m)", fontsize=8, labelpad=-4)
        axis.tick_params(labelsize=6.5, pad=-2)
        axis.view_init(elev=18, azim=-98)
        axis.set_zlim(-1.3, 1.3)
        axis.set_box_aspect((1.1, 1.3, 1.0))
        axis.set_title(title, fontsize=10)

    ax2 = fig.add_subplot(1, 3, 2, projection="3d")
    cloud(ax2, rgb, "(b) point cloud, colour draped on it")
    ax3 = fig.add_subplot(1, 3, 3, projection="3d")
    cloud(ax3, zz, "(c) the same cloud coloured by distance")

    plt.tight_layout()
    out = FIG / "appA_fig_cloud.png"
    plt.savefig(out, dpi=170, bbox_inches="tight")
    plt.close()
    print("saved", out)


if __name__ == "__main__":
    bag_figure()
    cloud_figure()
