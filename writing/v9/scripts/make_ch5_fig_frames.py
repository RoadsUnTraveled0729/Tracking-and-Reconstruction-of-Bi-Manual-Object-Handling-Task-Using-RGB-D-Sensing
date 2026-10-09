#!/usr/bin/env python3
"""Chapter 5 Figure 5.6: the two frames of the worked example, side by side.

Author decision of 2026-09-15: Section 5.6 shows the last clean frame and
the solved frame together, so the reader sees what state the example
carries and what it rebuilds.

  (a) frame 549, the last clean wrist frame before the occlusion window:
      the right shoulder, elbow and wrist are all measured.
  (b) frame 560, the frame the example solves, ten frames into the window:
      the right shoulder is measured, the elbow and the wrist were removed
      by the detectors of Section 5.2 and are rebuilt by Cases B and C.

Both panels take the same crop and the same scale, drawn in the style of
the Chapter 2 and Chapter 4 colour-frame figures: the RGB pixels are kept
and the object marker frame is projected through the colour intrinsics
with the shared helper frame_draw.py.

Points drawn (person space {Camera'}, metres), all from the verified
ch5_worked_example.py run of frame 560 saved with the orchestrator's
independent check; no value is recomputed here and none is printed in the
figure:

  frame 549  shoulder (-0.1643,  0.3357, 1.3148)   measured
             elbow    (-0.1998,  0.0504, 1.1935)   measured
             wrist    (-0.1969, -0.1095, 1.0229)   measured
  frame 560  shoulder (-0.1641,  0.3362, 1.3162)   measured
             elbow    (-0.2010,  0.0450, 1.1966)   rebuilt, Case C
             wrist    (-0.1856, -0.0912, 1.0441)   rebuilt, Case B

{Camera'} is {Camera} with its y axis flipped (equation (3.1)), so a point
is carried back to the raw camera frame by negating y before projecting,
as make_ch3_torso_video_fig.py does.

Inputs:
  writing/v9/figures/src/r6b_frame00549.png
  writing/v9/figures/src/r6b_frame00560.png
      colour frames of the rail recording, read from
      Video/recording_20260831_065553.bag with the reader of
      make_ch7_frame_strip.py (--extract writes 549 if it is missing)
  v1/aruco/output/recording_20260831_065553_aruco_raw.csv
      the unscaled raw marker detections; the E-009a scale acts along the
      camera ray, so marker centres project to the same pixels
  eval/output/recording_20260831_065553_aruco_raw_scaled.meta.json
      the colour intrinsics

Output: writing/v9/figures/ch5_fig_frames_549_560.png at 5.0 inches wide,
the narrowed figure width of this round.

Run: python writing/v9/scripts/make_ch5_fig_frames.py [--extract]
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import cv2

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / "v1" / "aruco"))
from frames import rt_from_row, make_T  # noqa: E402
from frame_draw import draw_axes  # noqa: E402

STEM = "recording_20260831_065553"
FIG = REPO / "writing" / "v9" / "figures"
SRC = FIG / "src"
OUT = FIG / "ch5_fig_frames_549_560.png"
BAG = REPO / "Video" / f"{STEM}.bag"
OBJ_ID = 1

CLEAN_FRAME, SOLVED_FRAME = 549, 560
FIG_WIDTH_IN = 5.0

# person space {Camera'}; see the docstring for the provenance of each row
ARM = {
    CLEAN_FRAME: {
        "shoulder": (-0.1643, 0.3357, 1.3148),
        "elbow": (-0.1998, 0.0504, 1.1935),
        "wrist": (-0.1969, -0.1095, 1.0229),
    },
    SOLVED_FRAME: {
        "shoulder": (-0.1641, 0.3362, 1.3162),
        "elbow": (-0.2010, 0.0450, 1.1966),
        "wrist": (-0.1856, -0.0912, 1.0441),
    },
}
REBUILT = {CLEAN_FRAME: (), SOLVED_FRAME: ("elbow", "wrist")}

MEASURED_C = "#f4a300"
REBUILT_C = "#c1121f"
INK = "#1f242b"


def extract_missing():
    """Grab any colour frame this figure needs that is not in figures/src."""
    want = {f for f in (CLEAN_FRAME, SOLVED_FRAME)
            if not (SRC / f"r6b_frame{f:05d}.png").exists()}
    if not want:
        print("colour frames already extracted")
        return
    sys.path.insert(0, str(REPO / "v1" / "mediapipe"))
    sys.path.insert(0, str(REPO / "eval" / "common"))
    from extract_landmarks_to_csv import open_bag  # noqa: E402
    import pyrealsense2 as rs  # noqa: E402
    SRC.mkdir(parents=True, exist_ok=True)
    pipe, align, _intr, color_format = open_bag(BAG)
    idx = 0
    while idx <= max(want):
        try:
            frames = pipe.wait_for_frames(timeout_ms=5000)
        except RuntimeError:
            break
        frames = align.process(frames)
        color = frames.get_color_frame()
        if not color:
            continue
        if idx in want:
            img = np.asanyarray(color.get_data())
            if color_format == rs.format.rgb8:
                img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            cv2.imwrite(str(SRC / f"r6b_frame{idx:05d}.png"), img)
            print("wrote", SRC / f"r6b_frame{idx:05d}.png")
        idx += 1


def project(pt_cam, intr):
    x, y, z = pt_cam
    return (intr["fx"] * x / z + intr["ppx"], intr["fy"] * y / z + intr["ppy"])


def to_camera(pt_person):
    """Undo the y flip of equation (3.1): {Camera'} back to {Camera}."""
    x, y, z = pt_person
    return (x, -y, z)


def arm_pixels(frame, intr):
    return {name: project(to_camera(p), intr)
            for name, p in ARM[frame].items()}


def main():
    meta = json.loads(
        (REPO / "eval" / "output" / f"{STEM}_aruco_raw_scaled.meta.json").read_text())
    intr = meta["color_intrinsics"]
    raw = pd.read_csv(REPO / "v1" / "aruco" / "output" / f"{STEM}_aruco_raw.csv")

    px = {f: arm_pixels(f, intr) for f in (CLEAN_FRAME, SOLVED_FRAME)}
    marker = {}
    for f in (CLEAN_FRAME, SOLVED_FRAME):
        row = raw[raw.frame == f].iloc[0]
        if row[f"m{OBJ_ID}_detected"] != 1.0:
            raise SystemExit(f"the object marker is not detected on frame {f}")
        marker[f] = make_T(*rt_from_row(row, OBJ_ID))

    # one crop for both panels, around everything either panel draws
    xs, ys = [], []
    for f in (CLEAN_FRAME, SOLVED_FRAME):
        for u, v in px[f].values():
            xs.append(u)
            ys.append(v)
        o = marker[f][:3, 3]
        u, v = project(o, intr)
        xs.append(u)
        ys.append(v)
    pad = 95
    x0 = max(0, int(min(xs) - pad))
    x1 = min(intr["width"], int(max(xs) + pad))
    y0 = max(0, int(min(ys) - pad * 0.55))
    y1 = min(intr["height"], int(max(ys) + pad * 0.75))

    panel_w, panel_h = x1 - x0, y1 - y0
    height_in = FIG_WIDTH_IN * panel_h / (2.0 * panel_w) * 1.06
    fig, axes = plt.subplots(1, 2, figsize=(FIG_WIDTH_IN, height_in))
    fig.subplots_adjust(left=0.004, right=0.996, top=0.995, bottom=0.055,
                        wspace=0.018)

    for ax, f, tag in ((axes[0], CLEAN_FRAME, "a"), (axes[1], SOLVED_FRAME, "b")):
        img = cv2.imread(str(SRC / f"r6b_frame{f:05d}.png"))
        if img is None:
            raise SystemExit(f"missing colour frame for {f}; run with --extract")
        ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        ax.set_xlim(x0, x1)
        ax.set_ylim(y1, y0)
        ax.set_xticks([])
        ax.set_yticks([])
        for s in ax.spines.values():
            s.set_color("0.55")
            s.set_linewidth(0.6)

        draw_axes(ax, marker[f], 0.045, "O", intr, label_dxy=(0, 26), fs=6,
                  nudge={"x": (7, 3), "y": (-9, 2), "z": (8, -3)}, lw=1.1)

        pts = px[f]
        rebuilt = REBUILT[f]
        for a, b in (("shoulder", "elbow"), ("elbow", "wrist")):
            style = "--" if (a in rebuilt or b in rebuilt) else "-"
            colour = REBUILT_C if (a in rebuilt or b in rebuilt) else MEASURED_C
            ax.plot([pts[a][0], pts[b][0]], [pts[a][1], pts[b][1]],
                    style, color=colour, lw=1.5, zorder=3)
        for name, (u, v) in pts.items():
            if name in rebuilt:
                ax.plot(u, v, "o", ms=5.0, mfc="none", mec=REBUILT_C,
                        mew=1.6, zorder=4)
            else:
                ax.plot(u, v, "o", ms=4.6, mfc=MEASURED_C, mec="white",
                        mew=0.8, zorder=4)

        sh = pts["shoulder"]
        ax.annotate("shoulder", xy=sh, xytext=(sh[0] + 12, sh[1] - 12),
                    fontsize=5.6, color=INK,
                    bbox=dict(boxstyle="round,pad=0.16", fc="white",
                              ec="0.7", lw=0.4, alpha=0.9))
        el, wr = pts["elbow"], pts["wrist"]
        for name, (u, v) in (("elbow", el), ("wrist", wr)):
            label = name + (" rebuilt" if name in rebuilt else "")
            ax.annotate(label, xy=(u, v), xytext=(u + 13, v),
                        fontsize=5.6,
                        color=REBUILT_C if name in rebuilt else INK,
                        va="center",
                        bbox=dict(boxstyle="round,pad=0.16", fc="white",
                                  ec="0.7", lw=0.4, alpha=0.9))

        ax.text(0.5, -0.045, f"({tag}) frame {f}", transform=ax.transAxes,
                ha="center", va="top", fontsize=7.2, color=INK)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=300)
    plt.close(fig)
    print("saved", OUT, f"({FIG_WIDTH_IN} in wide)")


if __name__ == "__main__":
    if "--extract" in sys.argv:
        extract_missing()
    main()
