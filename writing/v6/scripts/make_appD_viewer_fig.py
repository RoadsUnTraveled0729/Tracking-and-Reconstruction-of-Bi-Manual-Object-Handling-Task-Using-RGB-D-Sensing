"""Figure A.2: recorded camera view beside the vendor viewer's 3D views.

All three panels show the same moment of the evaluation recording,
t = 10.517 s (frameset 316), where the viewer was paused for the 3D
screenshots. Panel (a) is the colour frame extracted at that timestamp
from the bag itself (appD_viewer_camera.png, via pyrealsense2 playback);
(b) is the viewer's point cloud textured with the colour stream
(appD_viewer3d_screenshot.png); (c) the same cloud coloured by depth
(appD_viewer3d_depth.png). Screenshots captured 2026-08-05.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

FIGDIR = "/home/luo/Desktop/New_SandBox/writing/v6/figures/"
CAMERA = FIGDIR + "appD_viewer_camera.png"
SHOT_COLOR = FIGDIR + "appD_viewer3d_screenshot.png"
SHOT_DEPTH = FIGDIR + "appD_viewer3d_depth.png"

fig = plt.figure(figsize=(9.0, 7.6))
gs = fig.add_gridspec(2, 2, width_ratios=[1.05, 1.55],
                      height_ratios=[1.0, 1.55], hspace=0.14, wspace=0.05)

ax1 = fig.add_subplot(gs[0, 0])
ax1.imshow(mpimg.imread(CAMERA))
ax1.set_title("(a) recorded camera view", fontsize=10)
ax1.axis("off")

ax2 = fig.add_subplot(gs[0, 1])
ax2.imshow(mpimg.imread(SHOT_COLOR))
ax2.set_title("(b) viewer 3D view, colour texture", fontsize=10)
ax2.axis("off")

ax3 = fig.add_subplot(gs[1, :])
ax3.imshow(mpimg.imread(SHOT_DEPTH))
ax3.set_title("(c) viewer 3D view, coloured by depth", fontsize=10)
ax3.axis("off")

plt.savefig(FIGDIR + "appD_fig_viewer.png", dpi=150, bbox_inches="tight")
print("saved", FIGDIR + "appD_fig_viewer.png")
