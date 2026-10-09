#!/usr/bin/env python3
"""Appendix E figures (V7 rewrite round).

  appE_fig_detect.png  the three markers detected on the pinned
                       worked-example frame (frame 533 of the R5 primary
                       recording): the full frame with each detection
                       outlined and its recovered axes drawn, and one
                       zoom panel per marker with the four refined
                       corners in detection order.
  appE_fig_lobes.png   the two poses a planar target admits: the
                       schematic pair on the left, and on the right the
                       solver's own two solutions for one recorded
                       detection, reprojected into image pixels. The
                       detection is the wall marker on the worked-example
                       frame itself (frame 533): on the rail recording the
                       extractor records its near-degenerate ambiguity
                       flag for the wall marker on 898 of 900 frames.
                       Both panels use that one pair, so the drawn
                       geometry and the quoted numbers come from the same
                       solve.

Detection uses the project settings (DICT_5X5_50, AprilTag corner
refinement) and the pose comes from the same IPPE square solver and the
same marker sizes as the frozen extractor.

Output: writing/v7/figures/appE_fig_detect.png, appE_fig_lobes.png
Run:    python writing/v7/scripts/make_appE_figs.py
"""
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import cv2
from matplotlib.patches import Polygon

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v7" / "figures"
SRC = FIG / "src" / "r6b_frame00533.png"
META = (REPO / "v1" / "aruco" / "output"
        / "recording_20260831_065553_aruco_raw.meta.json")

meta = json.loads(META.read_text())
sizes = {int(k): v["size_m"] for k, v in meta["markers"].items()}
roles = {int(k): v["role"] for k, v in meta["markers"].items()}
intr = meta["color_intrinsics"]
K = np.array([[intr["fx"], 0, intr["ppx"]],
              [0, intr["fy"], intr["ppy"]],
              [0, 0, 1]], dtype=np.float64)
D = np.zeros((5, 1))
print("marker sizes (m):", sizes, "roles:", roles)

# Figure E.2 draws the solver's own pair on a recorded detection. The
# extractor flags a detection as near-degenerate when its two solutions
# sit less than 40 degrees apart; the wall marker carries that flag on
# the worked-example frame of the rail recording, so the same frame serves.
LOBE_FRAME = 533
LOBE_ID = 0
LOBE_SRC = FIG / "src" / ("r6b_frame%05d.png" % LOBE_FRAME)
RAW_CSV = (REPO / "v1" / "aruco" / "output"
           / "recording_20260831_065553_aruco_raw.csv")

img = cv2.cvtColor(cv2.imread(str(SRC)), cv2.COLOR_BGR2RGB)
aruco = cv2.aruco
params = aruco.DetectorParameters()
params.cornerRefinementMethod = aruco.CORNER_REFINE_APRILTAG
detector = aruco.ArucoDetector(
    aruco.getPredefinedDictionary(aruco.DICT_5X5_50), params)
corners, ids, _ = detector.detectMarkers(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY))
found = {int(i): c.reshape(4, 2) for i, c in zip(ids.flatten(), corners)}
print("detected markers:", sorted(found))

# ---- Figure E.1: detections and recovered axes ----------------------------
label = {0: "wall (id 0)", 1: "object (id 1)", 2: "desk (id 2)"}
corner_colors = ["#e63946", "#f4a261", "#2a9d8f", "#457b9d"]

fig = plt.figure(figsize=(8.4, 7.4))
gs = fig.add_gridspec(2, 3, height_ratios=[2.1, 1.0], hspace=0.08, wspace=0.06)
ax = fig.add_subplot(gs[0, :])
ax.imshow(img)
ax.axis("off")
ax.set_title("(a) full frame: the three detected markers with their "
             "recovered axes", fontsize=10)

for mid, quad in found.items():
    L = sizes[mid]
    obj = np.array([[-L / 2, L / 2, 0], [L / 2, L / 2, 0],
                    [L / 2, -L / 2, 0], [-L / 2, -L / 2, 0]])
    ok, rvecs, tvecs, _ = cv2.solvePnPGeneric(
        obj, quad.astype(np.float64), K, D, flags=cv2.SOLVEPNP_IPPE_SQUARE)
    rvec, tvec = rvecs[0], tvecs[0]
    R, _ = cv2.Rodrigues(rvec)
    print("id %d role %-6s t=(%+.4f, %+.4f, %+.4f) range=%.4f m"
          % (mid, roles[mid], tvec[0], tvec[1], tvec[2],
             float(np.linalg.norm(tvec))))
    ax.add_patch(Polygon(quad, closed=True, fill=False, ec="#ffd60a", lw=2.0))
    axis_len = L * 0.9
    pts, _ = cv2.projectPoints(
        np.float32([[0, 0, 0], [axis_len, 0, 0], [0, axis_len, 0],
                    [0, 0, axis_len]]), rvec, tvec, K, D)
    pts = pts.reshape(-1, 2)
    for k, col in enumerate(("#c1121f", "#2a9d8f", "#0077b6")):
        ax.plot([pts[0, 0], pts[k + 1, 0]], [pts[0, 1], pts[k + 1, 1]],
                color=col, lw=2.0)
    cen = quad.mean(axis=0)
    ax.text(cen[0], cen[1] - 34, label[mid], fontsize=9, color="white",
            ha="center",
            bbox=dict(boxstyle="round,pad=0.25", fc="black", alpha=0.72))

for k, mid in enumerate((0, 2, 1)):
    quad = found[mid]
    cen = quad.mean(axis=0)
    half = max(quad[:, 0].ptp(), quad[:, 1].ptp()) * 0.9 + 12
    x0, x1 = int(cen[0] - half), int(cen[0] + half)
    y0, y1 = int(cen[1] - half), int(cen[1] + half)
    axz = fig.add_subplot(gs[1, k])
    axz.imshow(img[max(y0, 0):y1, max(x0, 0):x1])
    axz.axis("off")
    axz.set_title("(%s) %s" % (chr(98 + k), label[mid]), fontsize=10)
    for j, (u, v) in enumerate(quad):
        axz.plot(u - x0, v - y0, "o", ms=7, mec="black", mfc=corner_colors[j])
        axz.annotate(str(j), (u - x0 + 5, v - y0 - 5), fontsize=9,
                     color="white",
                     bbox=dict(boxstyle="round,pad=0.15", fc="black",
                               alpha=0.72))

out1 = FIG / "appE_fig_detect.png"
plt.savefig(out1, dpi=200, bbox_inches="tight")
plt.close()
print("saved", out1)

# ---- Figure E.2: the two-solution geometry -------------------------------
recorded_flag = None
with RAW_CSV.open() as fh:
    for row in csv.DictReader(fh):
        if int(row["frame"]) == LOBE_FRAME:
            recorded_flag = row["m%d_ambig" % LOBE_ID]
            break
print("frame %d marker %d (%s): recorded ambiguity flag %s"
      % (LOBE_FRAME, LOBE_ID, roles[LOBE_ID], recorded_flag))

img_b = cv2.cvtColor(cv2.imread(str(LOBE_SRC)), cv2.COLOR_BGR2RGB)
c_b, i_b, _ = detector.detectMarkers(cv2.cvtColor(img_b, cv2.COLOR_RGB2GRAY))
quad = {int(i): c.reshape(4, 2) for i, c in zip(i_b.flatten(), c_b)}[LOBE_ID]
quad = quad.astype(np.float64)
Lb = sizes[LOBE_ID]
obj_b = np.array([[-Lb / 2, Lb / 2, 0], [Lb / 2, Lb / 2, 0],
                  [Lb / 2, -Lb / 2, 0], [-Lb / 2, -Lb / 2, 0]])
nsol, rvecs_b, tvecs_b, errs_b = cv2.solvePnPGeneric(
    obj_b, quad, K, D, flags=cv2.SOLVEPNP_IPPE_SQUARE)
if nsol < 2:
    raise SystemExit("the chosen detection returned a single solution")
Rs = [cv2.Rodrigues(r)[0] for r in rvecs_b[:2]]
proj = [cv2.projectPoints(obj_b, rvecs_b[k], tvecs_b[k], K, D)[0].reshape(4, 2)
        for k in range(2)]

normal_deg = float(np.degrees(np.arccos(np.clip(
    float(np.dot(Rs[0][:, 2], Rs[1][:, 2])), -1.0, 1.0))))
rot_deg = float(np.degrees(np.arccos(np.clip(
    0.5 * (float(np.trace(Rs[0].T @ Rs[1])) - 1.0), -1.0, 1.0))))
gaps = np.linalg.norm(proj[0] - proj[1], axis=1)
sep_px = float(gaps.max())
worst = int(np.argmax(gaps))
side_px = float(np.mean([np.linalg.norm(quad[j] - quad[(j + 1) % 4])
                         for j in range(4)]))
range_m = float(np.linalg.norm(tvecs_b[0]))
print("normals %.2f deg apart, rotation between the two poses %.2f deg"
      % (normal_deg, rot_deg))
print("largest corner separation %.3f px, mean side %.2f px, range %.3f m"
      % (sep_px, side_px, range_m))
print("reprojection error per solution: %.3f px, %.3f px"
      % (float(errs_b[0]), float(errs_b[1])))

COL_A, COL_B = "#c1121f", "#0077b6"
fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6))

# (a) the geometry, drawn at the tilt the recorded pair actually holds
tilt = normal_deg / 2.0
ax = axes[0]
ax.set_xlim(-0.45, 3.5)
ax.set_ylim(-1.25, 0.95)
ax.axis("off")
ax.scatter([0], [0], color="black", s=55, marker="s")
ax.text(0.02, -0.20, "camera centre", fontsize=8.5, ha="center")
ax.plot([0, 3.05], [0, 0], color="0.55", ls="--", lw=1.1)
ax.text(0.80, 0.06, "viewing ray", fontsize=8.5, color="0.45")
cen = np.array([2.30, 0.0])
for angle, col, name in ((tilt, COL_A, "pose A: tilted toward the camera"),
                         (-tilt, COL_B, "pose B: tilted away from the camera")):
    t = np.radians(angle)
    dirv = np.array([np.cos(t + np.pi / 2), np.sin(t + np.pi / 2)])
    a, b = cen - 0.55 * dirv, cen + 0.55 * dirv
    ax.plot([a[0], b[0]], [a[1], b[1]], color=col, lw=3.4)
    nrm = np.array([np.cos(t), np.sin(t)]) * 0.62
    tail = cen - nrm
    ax.annotate("", xy=tuple(tail), xytext=tuple(cen),
                arrowprops=dict(arrowstyle="-|>", color=col, lw=1.5))
    ax.text(tail[0] - 0.06, tail[1] + (-0.13 if angle > 0 else 0.13),
            "normal", fontsize=8.0, color=col, ha="center")
    tip = a if a[0] > b[0] else b
    ax.text(tip[0] + 0.09, tip[1], name, fontsize=8.6, color=col,
            ha="left", va="center")
ax.text(1.55, -0.92,
        "the two planes are mirror images about the viewing ray",
        fontsize=8.8, ha="center")
ax.text(1.55, -1.10,
        "drawn at the tilt of the recorded pair, whose normals differ by "
        "%.1f degrees" % normal_deg,
        fontsize=8.8, ha="center", color="0.35")
ax.set_title("(a) the two planar pose interpretations", fontsize=10)

# (b) the same pair reprojected onto the detection it came from
ax = axes[1]
ax.set_aspect("equal")
c = quad.mean(axis=0)
half = max(quad[:, 0].ptp(), quad[:, 1].ptp()) * 1.25 + 8
# the crop sits right of the marker, which keeps the magnified corner
# clear of the outlines it is taken from
cx, cy = c[0] + 0.30 * half, c[1] + 0.08 * half
x0, x1 = int(cx - half), int(cx + half)
y0, y1 = int(cy - half), int(cy + half)
ax.imshow(img_b[y0:y1, x0:x1], interpolation="nearest",
          extent=(x0 - 0.5, x1 - 0.5, y1 - 0.5, y0 - 0.5))
for q, col, lab in ((proj[0], COL_A, "pose A reprojected"),
                    (proj[1], COL_B, "pose B reprojected")):
    ax.add_patch(Polygon(q, closed=True, fill=False, ec=col, lw=1.6,
                         label=lab))
ax.plot(quad[:, 0], quad[:, 1], "o", ms=4.5, mec="black", mfc="white",
        ls="none", label="detected corners")
ax.set_xlim(x0 - 0.5, x1 - 0.5)
ax.set_ylim(y1 - 0.5, y0 - 0.5)
ax.set_xlabel("image column (pixels)", fontsize=8.5)
ax.set_ylabel("image row (pixels)", fontsize=8.5)
ax.tick_params(labelsize=7)
ax.text(0.03, 0.03,
        "normals %.1f degrees apart\noutlines at most %.2f pixels apart\n"
        "sides averaging %.1f pixels"
        % (normal_deg, sep_px, side_px),
        transform=ax.transAxes, fontsize=8.6, va="bottom", ha="left",
        bbox=dict(boxstyle="round,pad=0.32", fc="white", ec="0.6",
                  alpha=0.88))

# the corner that separates most, magnified until the gap is visible
zc = 0.5 * (proj[0][worst] + proj[1][worst])
zhalf = 1.4
axz = ax.inset_axes([0.60, 0.50, 0.38, 0.38])
axz.imshow(img_b[y0:y1, x0:x1], interpolation="nearest",
           extent=(x0 - 0.5, x1 - 0.5, y1 - 0.5, y0 - 0.5))
for q, col in ((proj[0], COL_A), (proj[1], COL_B)):
    axz.add_patch(Polygon(q, closed=True, fill=False, ec=col, lw=1.6))
axz.plot(quad[worst, 0], quad[worst, 1], "o", ms=5, mec="black", mfc="white")
axz.set_xlim(zc[0] - zhalf, zc[0] + zhalf)
axz.set_ylim(zc[1] + zhalf, zc[1] - zhalf)
axz.set_xticks([])
axz.set_yticks([])
bar = 1.0 / (2 * zhalf)          # one image pixel in axes fraction
axz.add_patch(plt.Rectangle((0.04, 0.04), bar + 0.10, 0.22,
                            transform=axz.transAxes, fc="white",
                            ec="none", alpha=0.85, zorder=4))
axz.plot([0.09, 0.09 + bar], [0.10, 0.10], color="black", lw=1.6,
         transform=axz.transAxes, zorder=5)
axz.text(0.09 + bar / 2, 0.13, "1 pixel", fontsize=7.5, ha="center",
         va="bottom", transform=axz.transAxes, zorder=5)
axz.set_title("the widest corner, magnified", fontsize=8.0, pad=3)
ax.indicate_inset_zoom(axz, edgecolor="0.3")
ax.legend(fontsize=8.5, loc="upper center", bbox_to_anchor=(0.5, -0.14),
          ncol=3, frameon=False)
ax.set_title("(b) both solutions for the wall marker on frame %d, "
             "drawn in image pixels" % LOBE_FRAME, fontsize=10)

plt.tight_layout()
out2 = FIG / "appE_fig_lobes.png"
plt.savefig(out2, dpi=180, bbox_inches="tight")
plt.close()
print("saved", out2)
