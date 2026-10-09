"""Shared drawing helpers for coordinate-frame overlays on colour frames.

Used by make_ch2_frames_fig.py (Chapter 2, the scene and its frames) and
make_ch4_figs.py (Chapter 4 figures). One pinhole projector and one axis
drawer, so the two chapters draw frames the same way.
"""
import numpy as np

AXC = {"x": "#c1121f", "y": "#2a9d8f", "z": "#3b6fb6"}


def project(pts_cam, intr):
    """Pixel coordinates of camera-frame points through the colour intrinsics.

    intr is the color_intrinsics dict of the recording metadata (fx, fy,
    ppx, ppy). No distortion model: the pipeline reads the aligned colour
    stream, whose intrinsics are rectified."""
    pts_cam = np.asarray(pts_cam, dtype=float)
    z = pts_cam[:, 2]
    u = intr["fx"] * pts_cam[:, 0] / z + intr["ppx"]
    v = intr["fy"] * pts_cam[:, 1] / z + intr["ppy"]
    return np.stack([u, v], axis=1)


def draw_axes(ax, T, length, label, intr, label_dxy=(0, 0), fs=10,
              nudge=None, lw=2.0):
    """Draw the three axes of the camera-frame pose T on an image axis.

    Returns the pixel position of the frame origin, so a caller can hang
    arrows between frames on it."""
    o = T[:3, 3]
    tips = np.stack([o + T[:3, i] * length for i in range(3)])
    uv = project(np.vstack([o[None, :], tips]), intr)
    # label offsets keep the two nearly collinear axes readable when one
    # of them points away from the camera and projects short
    if nudge is None:
        nudge = {"x": (10, 4), "y": (-13, 2), "z": (12, -4)}
    for i, nm in enumerate("xyz"):
        ax.annotate("", xy=uv[i + 1], xytext=uv[0],
                    arrowprops=dict(arrowstyle="-|>", color=AXC[nm],
                                    lw=lw, mutation_scale=12))
        ax.text(uv[i + 1, 0] + nudge[nm][0], uv[i + 1, 1] + nudge[nm][1],
                nm, color=AXC[nm], fontsize=10, weight="bold",
                ha="center", va="center")
    if label:
        ax.text(uv[0, 0] + label_dxy[0], uv[0, 1] + label_dxy[1], label,
                fontsize=fs, weight="bold", color="black",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.6",
                          alpha=0.88))
    return uv[0]
