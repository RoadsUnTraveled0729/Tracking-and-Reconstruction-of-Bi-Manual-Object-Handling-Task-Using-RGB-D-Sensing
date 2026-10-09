#!/usr/bin/env python3
"""Chapter 3 Figure 3.2: the camera frame and the reconstruction frames
(rebuilt 2026-08-31 after the user caught a mirrored camera frame; final
form per the user's direction of the same day).

Panel (a): a real front photograph of the D435 (Intel product image,
figures/src/d435_front.png; replace with the user's own front photo of
the laboratory unit any time) with the axes drawn MIRRORED, as a front
view demands: the librealsense convention is defined from behind the
camera (x image right, y down, z forward), so facing the camera the x
axis appears on the reader's left and z comes out of the page. The
module labels mirror too (Intel documentation: the left imager sits on
the right side when the camera faces you); the aperture identities are
pinned by measurement, the photographed spacings matching the 50 mm
imager baseline and the 14.8 mm depth-to-colour offset read from the
recordings' extrinsics. Origin at the colour lens (depth is aligned to
colour).

Panel (b): captured inside the Unity editor by
Unity/Assets/Editor/RootFrameShot.cs via run_rootframe_shot.py (edit
mode, no streaming): every scene element except the human rig hidden,
the rig's top-most parent node selected, and that node's coordinate
axes rendered at its origin. The node is axis-aligned with the Unity
world and the avatar stands in the T-pose, the model's reference
configuration. The chapter prose contrasts this with the MEASURED body
root frame, which rides the torso, and states why the reconstruction
is correct across the difference.

Output: writing/v7/figures/ch3_fig_sensor_unity.png
Run:    python writing/v7/scripts/make_ch3_sensor_fig.py
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "writing" / "v9" / "figures" / "ch2_fig_sensor_scene.png"

fig = plt.figure(figsize=(11, 4.6))

# --- (a) the camera from the FRONT: the axes mirror ---------------------
# The librealsense convention is defined from behind the camera (x image
# right, y down, z forward). On a front view the camera faces the reader,
# so x appears on the reader's LEFT and z comes out of the page. The
# module names mirror the same way (Intel documentation: the left imager
# is on the right side when the camera is viewed from the front). The
# colour camera is the rightmost aperture in the front view: the
# depth-to-colour extrinsic of the recordings places it 14.8 mm on the
# camera's left of the left imager, and the pipeline's origin is the
# colour lens (depth is aligned to colour).
FRONT = REPO / "writing" / "v9" / "figures" / "src" / "d435_front.png"
ax = fig.add_subplot(1, 2, 1)
im = Image.open(FRONT).convert("RGBA")
bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
im = Image.alpha_composite(bg, im).convert("RGB")
ax.imshow(im)
W, H = im.size
# apertures, viewer left -> right (mirrored names per the convention);
# positions measured on the photograph and consistent with the physical
# spacings (A-C = the 50 mm imager baseline, C-D = the 14.8 mm
# depth-to-colour offset of the recordings)
labels = [(0.215, "right imager", 1.10), (0.40, "IR projector", 1.24),
          (0.655, "left imager", 1.10),
          (0.78, "RGB colour camera (frame origin)", 1.24)]
for fx, txt, fy in labels:
    ax.annotate(txt, xy=(fx * W, 0.62 * H), xytext=(fx * W, fy * H),
                ha="center", va="top", fontsize=8.5, color="0.25",
                arrowprops=dict(arrowstyle="-", color="0.55", lw=0.8))
ox, oy = int(0.78 * W), int(0.52 * H)
L = int(0.17 * W)
ax.annotate("", xy=(ox - L, oy), xytext=(ox, oy),
            arrowprops=dict(arrowstyle="-|>", color="crimson", lw=2.8))
ax.text(ox - int(L * 0.62), oy - int(0.12 * H), "x (image right)",
        color="crimson", fontsize=11, weight="bold", ha="center")
ax.annotate("", xy=(ox, oy + int(L * 0.52)), xytext=(ox, oy),
            arrowprops=dict(arrowstyle="-|>", color="#1a7d1a", lw=2.8))
ax.text(ox + int(0.015 * W), oy + int(L * 0.52), "y (image down)",
        color="#1a7d1a", fontsize=11, weight="bold", va="center")
# z toward the reader: dot-in-circle at the origin
ax.plot([ox], [oy], marker="o", ms=14, mfc="none", mec="royalblue", mew=2.4)
ax.plot([ox], [oy], marker=".", ms=6, color="royalblue")
ax.text(ox + int(0.015 * W), oy - int(0.14 * H),
        "z (depth, out of the\npage toward the reader)",
        color="royalblue", fontsize=10, weight="bold")
ax.set_xlim(-0.02 * W, 1.10 * W)
ax.set_ylim(1.42 * H, -0.30 * H)
ax.axis("off")
ax.set_title("(a) D435 camera frame $\\mathcal{C}$ (right-handed), front "
             "view:\nthe camera faces the reader, so its image-right axis "
             "appears on the reader's left", fontsize=9.5)

# --- (b) the rig root frame, captured inside the Unity editor ----------
# Produced by Assets/Editor/RootFrameShot.cs (edit mode, no streaming):
# every scene element except the human rig is hidden, the rig's
# top-most parent node is selected, and that node's coordinate axes
# are rendered at its origin with Unity's gizmo colours (x red,
# y green, z blue). The node is axis-aligned with the Unity world; the
# avatar stands in the T-pose, the model's reference configuration.
ROOTSHOT = REPO / "writing" / "v9" / "figures" / "src" / "rig_root_frame_tpose.png"
ax = fig.add_subplot(1, 2, 2)
img = plt.imread(str(ROOTSHOT))
ax.imshow(img)
ax.axis("off")
# D-065: panel (b) carried a baked-in title naming the frame as U and
# placing its origin at the avatar rig root. Both are false: the formal
# frame is the Unity scene frame of Section 6.4 and its origin is on the
# drawn floor. The title is reduced to the panel letter and the caption
# carries the coordinate-system description. No frame claim is made here.
ax.set_title("(b)", fontsize=9.5)

plt.tight_layout()
plt.savefig(OUT, dpi=160, bbox_inches="tight")
print("saved", OUT)
