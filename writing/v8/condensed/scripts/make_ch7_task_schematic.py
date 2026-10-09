#!/usr/bin/env python3
"""Chapter 7 task schematics (supervisor C30 and C31).

Two figures:
  ch7_fig_protocol.png   how the subject performs the one-handed rail task,
                         in four drawn steps seen from the sensor (the view
                         of every colour frame in the thesis) with a top view
                         of the path beside them: grasp the cube on the desk,
                         lift it onto the rail, slide it along the rail,
                         release it at the far end. One hand, no handover.
  ch7_fig_stations.png   the object at its stations in the gravity-levelled
                         world frame of Figure 7.1 (x along the rail, y up,
                         z away from the sensor), drawn to the coordinates of
                         eval/reports/r6b_waypoints.json: the parked start,
                         W1 (foot of the lift), W2 (start of the rail) and W3
                         (far end), the cube as a 7 cm box at each, the marker
                         origin O with its axes on the face turned to the
                         sensor, the world frame W once at the desk marker,
                         the desk and the rail.

Sources: eval/reports/r6b_waypoints.json (waypoints, legs, rail line, desk
level), Chapter 2 Section 2.2.1 and Chapter 4 (object frame: origin at the
centre of the marker face, z out of the printed face, cube centre half an
edge behind it), Figure 7.1 (make_ch7_rail_traj_fig.py, axis convention).

Output: writing/v8/condensed/figures/ch7_fig_protocol.png
        writing/v8/condensed/figures/ch7_fig_stations.png
Run:    python writing/v8/condensed/scripts/make_ch7_task_schematic.py
"""
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch, Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

REPO = Path(__file__).resolve().parents[4]
FIGD = REPO / "writing" / "v8" / "condensed" / "figures"
WP = json.loads((REPO / "eval" / "reports" / "r6b_waypoints.json").read_text())

C_DESK, C_RAIL, C_CUBE, C_HAND, C_SENS = "#f1e3c8", "#c9a97a", "#f7f7f7", "#f2c9a8", "#cfd8e4"
CUBE = 0.07  # m, the cube edge


# ---------------------------------------------------------------- protocol
def subject(ax, cx, base_y, hand_at, scale=0.85, open_hand=False):
    """The subject seen from the sensor, standing behind the desk: head,
    shoulders and trunk (the desk hides the legs), the left arm hanging and
    the right arm (the viewer's left) reaching to hand_at."""
    s = scale
    ax.add_patch(Circle((cx, base_y + 1.62 * s), 0.15 * s, fc="white", ec="0.2", lw=1.1, zorder=3))
    trunk = Polygon([(cx - 0.34 * s, base_y + 1.42 * s), (cx + 0.34 * s, base_y + 1.42 * s),
                     (cx + 0.26 * s, base_y + 0.55 * s), (cx - 0.26 * s, base_y + 0.55 * s)],
                    closed=True, fc="#e9ecd8", ec="0.2", lw=1.1, zorder=2)
    ax.add_patch(trunk)
    shr = (cx - 0.32 * s, base_y + 1.38 * s)   # right shoulder, viewer's left
    shl = (cx + 0.32 * s, base_y + 1.38 * s)
    ax.plot([shl[0], shl[0] + 0.10 * s, shl[0] + 0.14 * s], [shl[1], shl[1] - 0.45 * s, shl[1] - 0.85 * s],
            color="0.2", lw=1.5, solid_capstyle="round", zorder=3)
    hx, hy = hand_at
    ex = 0.5 * (shr[0] + hx) - 0.12 * s
    ey = 0.5 * (shr[1] + hy) + 0.06 * s
    ax.plot([shr[0], ex, hx], [shr[1], ey, hy], color="0.2", lw=1.5, solid_capstyle="round", zorder=6)
    ax.add_patch(Circle((hx, hy), 0.055 * s, fc="white" if open_hand else C_HAND, ec="0.2", lw=0.9, zorder=7))


def step_panel(ax, k, title, cube_xy, hand, arrow=None, open_hand=False):
    ax.set_xlim(-1.6, 1.6)
    ax.set_ylim(-0.25, 2.15)
    ax.set_aspect("equal")
    ax.axis("off")
    # desk seen from the sensor, the rail along its far edge
    ax.add_patch(Polygon([(-1.55, 0.0), (1.55, 0.0), (1.15, 0.62), (-1.15, 0.62)],
                         closed=True, fc=C_DESK, ec="0.35", lw=1.0, zorder=1))
    ax.add_patch(Rectangle((-1.05, 0.58), 2.10, 0.09, fc=C_RAIL, ec="0.3", lw=0.9, zorder=4))
    ax.text(1.20, 0.62, "rail", fontsize=7.5, ha="left", va="center", color="0.25")
    ax.add_patch(Rectangle((-0.16, 0.06), 0.32, 0.16, fc="white", ec="0.2", lw=0.8, zorder=2))
    ax.text(0.0, -0.10, "desk marker", fontsize=6.5, ha="center", va="center", color="0.25")
    subject(ax, 0.42, 0.62, hand, open_hand=open_hand)
    cx, cy = cube_xy
    ax.add_patch(Rectangle((cx - 0.11, cy), 0.22, 0.22, fc=C_CUBE, ec="0.2", lw=1.0, zorder=5))
    ax.add_patch(Rectangle((cx - 0.07, cy + 0.04), 0.14, 0.14, fc="none", ec="0.2", lw=0.8, zorder=5,
                           hatch="xx"))
    if arrow is not None:
        ax.add_patch(FancyArrowPatch(arrow[0], arrow[1], arrowstyle="-|>", mutation_scale=12,
                                     color="tab:red", lw=1.4, zorder=8, ls="--"))
    ax.set_title(f"{k}. {title}", fontsize=9.5, loc="left")


def protocol_figure():
    fig = plt.figure(figsize=(9.8, 4.8))
    gs = fig.add_gridspec(2, 3, width_ratios=[1, 1, 1.0], wspace=0.05, hspace=0.30)
    ax1 = fig.add_subplot(gs[0, 0]); ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0]); ax4 = fig.add_subplot(gs[1, 1])
    axt = fig.add_subplot(gs[:, 2])
    step_panel(ax1, 1, "grasp the cube on the desk", (-0.85, 0.18), (-0.85, 0.44))
    step_panel(ax2, 2, "carry it back and lift it onto the rail", (-0.85, 0.67), (-0.85, 0.93),
               arrow=((-0.62, 0.30), (-0.62, 0.62)))
    step_panel(ax3, 3, "slide it along the rail", (0.0, 0.67), (0.0, 0.93),
               arrow=((-0.62, 1.05), (0.62, 1.05)))
    step_panel(ax4, 4, "release it at the far end", (0.85, 0.67), (0.62, 1.05), open_hand=True)
    # top view of the path: the sensor at the bottom, x to the right, z up the page
    axt.set_aspect("equal"); axt.axis("off")
    axt.set_xlim(-0.56, 0.46); axt.set_ylim(-0.30, 0.74)
    axt.text(-0.55, 0.70, "top view: x to the right, z away from the sensor", fontsize=7.8, ha="left")
    axt.add_patch(Rectangle((-0.5, 0.0), 0.9, 0.55, fc=C_DESK, ec="0.35", lw=1.0))
    rl = WP["rail_line"]
    # the fitted depth is the marker origin's; the cube body, and so the rail
    # under it, sits half an edge farther from the sensor
    rail_z = rl["depth_m"] + CUBE / 2
    axt.add_patch(Rectangle((rl["x_from_m"], rail_z - 0.02), rl["x_to_m"] - rl["x_from_m"], 0.04,
                            fc=C_RAIL, ec="0.3", lw=0.9))
    axt.text((rl["x_from_m"] + rl["x_to_m"]) / 2, rail_z + 0.03, "rail", fontsize=7.5, ha="center", va="bottom", color="0.25")
    axt.add_patch(Rectangle((-0.06, -0.27), 0.12, 0.07, fc=C_SENS, ec="0.25", lw=1.0))
    axt.text(0.0, -0.235, "sensor", fontsize=7.5, ha="center", va="center")
    axt.add_patch(Rectangle((-0.03, 0.03), 0.06, 0.04, fc="white", ec="0.2", lw=0.8))
    axt.annotate("", xy=(0.09, 0.05), xytext=(0.0, 0.05), arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=1.1))
    axt.annotate("", xy=(0.0, 0.14), xytext=(0.0, 0.05), arrowprops=dict(arrowstyle="-|>", color="tab:blue", lw=1.1))
    axt.text(0.10, 0.045, "x", fontsize=7, va="center"); axt.text(0.008, 0.145, "z", fontsize=7)
    axt.text(0.13, 0.11, "W, the desk marker", fontsize=6.8, ha="left", va="center")
    W = {k: np.array(v) for k, v in WP["waypoints"].items()}
    path = np.vstack([W["start"], W["W1"], W["W3"]])
    axt.plot(path[:, 0], path[:, 2], color="tab:red", lw=1.6, ls="--")
    for k in ("start", "W1", "W3"):
        w = W[k]
        axt.add_patch(Rectangle((w[0] - CUBE / 2, w[2]), CUBE, CUBE, fc=C_CUBE, ec="0.2", lw=0.9, zorder=4))
    axt.text(W["start"][0], W["start"][2] - 0.06, "start", fontsize=7.5, ha="center", va="center", weight="bold")
    axt.text(W["W1"][0] - 0.05, W["W1"][2] + 0.035, "W1, W2\nabove it", fontsize=7.0, ha="right", va="center", weight="bold")
    axt.text(W["W3"][0], W["W3"][2] + CUBE + 0.03, "W3", fontsize=7.5, ha="center", va="bottom", weight="bold")
    axt.annotate("", xy=(W["W1"][0], W["W1"][2] - 0.05), xytext=(W["start"][0], W["start"][2] + 0.05),
                 arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=1.2))
    axt.annotate("", xy=(W["W3"][0] - 0.05, W["W3"][2]), xytext=(W["W1"][0] + 0.05, W["W1"][2]),
                 arrowprops=dict(arrowstyle="-|>", color="tab:red", lw=1.2))
    plt.savefig(FIGD / "ch7_fig_protocol.png", dpi=200, bbox_inches="tight")
    print("saved", FIGD / "ch7_fig_protocol.png")


# ---------------------------------------------------------------- stations
def cube_faces(center, edge, face_toward_sensor=True):
    c = np.asarray(center); h = edge / 2.0
    x, y, z = c
    v = np.array([[x - h, y - h, z - h], [x + h, y - h, z - h], [x + h, y + h, z - h], [x - h, y + h, z - h],
                  [x - h, y - h, z + h], [x + h, y - h, z + h], [x + h, y + h, z + h], [x - h, y + h, z + h]])
    faces = [[v[0], v[1], v[2], v[3]], [v[4], v[5], v[6], v[7]], [v[0], v[1], v[5], v[4]],
             [v[2], v[3], v[7], v[6]], [v[1], v[2], v[6], v[5]], [v[0], v[3], v[7], v[4]]]
    return faces


def stations_figure():
    W = {k: np.array(v) for k, v in WP["waypoints"].items()}
    rl = WP["rail_line"]
    desk_top = WP["desk_level_m"] - CUBE / 2.0
    fig = plt.figure(figsize=(9.6, 6.2))
    ax = fig.add_subplot(111, projection="3d")
    # matplotlib 3d axes: x -> x, y -> z (depth), z -> height, as Figure 7.1
    def P(p):
        return (p[0], p[2], p[1])
    # desk top
    dx0, dx1, dz0, dz1 = -0.45, 0.35, 0.0, 0.56
    ax.add_collection3d(Poly3DCollection([[(dx0, dz0, desk_top), (dx1, dz0, desk_top), (dx1, dz1, desk_top), (dx0, dz1, desk_top)]],
                                         fc=C_DESK, ec="0.5", lw=0.6, alpha=0.55))
    # rail as a box along x at the fitted depth, from the desk top to the rail top
    rail_top = rl["height_m"] - CUBE / 2.0
    # the fitted depth locates the marker origin; the cube body and the rail under it sit half an edge behind it
    rx0, rx1, rz0, rz1 = rl["x_from_m"], rl["x_to_m"], rl["depth_m"] + CUBE / 2 - 0.02, rl["depth_m"] + CUBE / 2 + 0.02
    rv = [(rx0, rz0, desk_top), (rx1, rz0, desk_top), (rx1, rz1, desk_top), (rx0, rz1, desk_top),
          (rx0, rz0, rail_top), (rx1, rz0, rail_top), (rx1, rz1, rail_top), (rx0, rz1, rail_top)]
    rf = [[rv[0], rv[1], rv[5], rv[4]], [rv[4], rv[5], rv[6], rv[7]], [rv[1], rv[2], rv[6], rv[5]], [rv[0], rv[3], rv[7], rv[4]], [rv[3], rv[2], rv[6], rv[7]]]
    ax.add_collection3d(Poly3DCollection(rf, fc=C_RAIL, ec="0.35", lw=0.6, alpha=0.9))
    # reference path
    ref = np.vstack([W["start"], W["W1"], W["W2"], W["W3"]])
    ax.plot(ref[:, 0], ref[:, 2], ref[:, 1], color="tab:red", lw=2.0, ls="--")
    # cubes at the stations with the marker origin O and its axes
    for k, lab in (("start", "start"), ("W1", "W1"), ("W2", "W2"), ("W3", "W3")):
        o = W[k]  # pinned waypoints locate the marker origin
        c = o + np.array([0.0, 0.0, CUBE / 2.0])
        faces = [[P(p) for p in f] for f in cube_faces(c, CUBE)]
        ax.add_collection3d(Poly3DCollection(faces, fc=C_CUBE, ec="0.25", lw=0.7, alpha=0.30))
        m = 0.0225                                    # the 45 mm printed square
        sq = [P(o + np.array([-m, -m, -0.0005])), P(o + np.array([m, -m, -0.0005])),
              P(o + np.array([m, m, -0.0005])), P(o + np.array([-m, m, -0.0005]))]
        ax.add_collection3d(Poly3DCollection([sq], fc="0.25", ec="0.1", lw=0.5, alpha=0.9))
        ax.scatter(*P(o), s=30, color="k", zorder=12)
        L = 0.06
        ax.plot(*zip(P(o), P(o + np.array([L, 0, 0]))), color="tab:red", lw=2.0, zorder=11)
        ax.plot(*zip(P(o), P(o + np.array([0, L, 0]))), color="tab:green", lw=2.0, zorder=11)
        ax.plot(*zip(P(o), P(o + np.array([0, 0, -L]))), color="tab:blue", lw=2.0, zorder=11)
        if lab == "W1":
            ax.text(c[0] + 0.07, c[2] - 0.06, c[1] - 0.03, lab, fontsize=9.5, weight="bold", ha="center")
        elif lab == "start":
            ax.text(c[0] - 0.03, c[2] - 0.08, c[1] + 0.03, lab, fontsize=9.5, weight="bold", ha="center")
        else:
            ax.text(c[0], c[2], c[1] + CUBE * 0.8, lab, fontsize=9.5, weight="bold", ha="center")
    from matplotlib.lines import Line2D
    proxies = [Line2D([0], [0], color="tab:red", lw=2.0, ls="--", label="reference path"),
               Line2D([0], [0], color="k", marker="o", lw=0, label="marker origin O, on the face turned to the sensor"),
               Line2D([0], [0], color="tab:red", lw=2.0, label="x axis of O and of W"),
               Line2D([0], [0], color="tab:green", lw=2.0, label="y axis (up)"),
               Line2D([0], [0], color="tab:blue", lw=2.0, label="z axis (out of the marker face)")]
    # world frame at the desk marker
    Lw = 0.08
    ax.plot([0, Lw], [0, 0], [0, 0], color="tab:red", lw=2.2)
    ax.plot([0, 0], [0, Lw], [0, 0], color="tab:blue", lw=2.2)
    ax.plot([0, 0], [0, 0], [0, Lw], color="tab:green", lw=2.2)
    ax.text(Lw, 0, 0, "x", fontsize=8); ax.text(0, Lw, 0, "z", fontsize=8); ax.text(0, 0, Lw, "y", fontsize=8)
    ax.text(-0.30, -0.10, 0.0, "W, the desk marker", fontsize=8.5, weight="bold")
    ax.text(-0.42, -0.19, 0.0, "sensor side", fontsize=8, color="0.3")
    ax.set_xlim(-0.45, 0.35); ax.set_ylim(-0.2, 0.56); ax.set_zlim(-0.05, 0.16)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("z (m), away from the camera")
    ax.set_zlabel("height (m)", labelpad=6)
    ax.set_box_aspect((0.80, 0.76, 0.21))
    ax.view_init(elev=30, azim=-62)
    ax.legend(handles=proxies, loc="upper right", fontsize=7.2, framealpha=0.95)
    ax.zaxis.set_rotate_label(False)
    ax.set_zlabel("height (m)", rotation=90, labelpad=4)
    fig.subplots_adjust(left=0.0, right=0.92, top=1.0, bottom=0.0)
    plt.savefig(FIGD / "ch7_fig_stations.png", dpi=180, bbox_inches="tight", pad_inches=0.15)
    print("saved", FIGD / "ch7_fig_stations.png")


if __name__ == "__main__":
    protocol_figure()
    stations_figure()
