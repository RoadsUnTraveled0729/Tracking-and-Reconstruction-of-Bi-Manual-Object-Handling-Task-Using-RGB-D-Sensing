"""Plot-first check for the Stage 1 inspection.

Renders (a) a coverage timeline: one row per marker and landmark,
colored by per-frame status, with phase boundaries; (b) the marker
pixel tracks overlaid on a sampled color frame from the bag, so the
detections can be eyeballed against the physical scene.

Usage:
    python eval/inspect/plot_coverage.py [--stem STEM] [--frame N]
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
import paths

STATUS_COLORS = {0: "#2a7e2a", 1: "#d98a00", 2: "#4444cc", 3: "#bbbbbb",
                 4: "#cc2222"}
# 0 ok(green) 1 low_vis(amber) 2 no_depth(blue) 3 no pose(grey)
# 4 marker not detected(red)


def color_frame_from_bag(bag, frame_idx):
    import pyrealsense2 as rs
    cfg = rs.config()
    cfg.enable_device_from_file(str(bag), repeat_playback=False)
    pipe = rs.pipeline()
    prof = pipe.start(cfg)
    prof.get_device().as_playback().set_real_time(False)
    img = None
    for i in range(frame_idx + 1):
        fs = pipe.wait_for_frames(5000)
        if i == frame_idx:
            img = np.asanyarray(fs.get_color_frame().get_data()).copy()
    pipe.stop()
    return img[:, :, ::-1]  # bgr8 -> rgb


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R4_STEM)
    ap.add_argument("--frame", type=int, default=None,
                    help="frame for the overlay (default: shortlist top)")
    args = ap.parse_args()
    stem = args.stem

    aruco = pd.read_csv(paths.ARUCO_OUT / f"{stem}_aruco_raw.csv")
    lm = pd.read_csv(paths.MP_OUT / f"{stem}_landmarks_raw.csv")
    insp = json.load(open(paths.EVAL_REPORTS / f"{stem}_inspection.json"))
    n = len(aruco)
    pose = lm["has_pose"].to_numpy().astype(bool)

    rows = []
    for mid, name in [(0, "wall"), (1, "object"), (2, "desk")]:
        det = aruco[f"m{mid}_detected"].to_numpy().astype(bool)
        rows.append((f"marker {name} (id {mid})",
                     np.where(det, 0, 4)))
    for name in paths.LANDMARKS:
        src = lm[f"{name}_src"].to_numpy().astype(float)
        status = np.where(pose, src, 3).astype(int)
        rows.append((name, status))

    fig, ax = plt.subplots(figsize=(14, 5.5))
    for i, (label, status) in enumerate(rows):
        for code in np.unique(status):
            idx = np.flatnonzero(status == code)
            ax.scatter(idx, np.full(idx.size, len(rows) - 1 - i),
                       s=4, marker="|", color=STATUS_COLORS[int(code)],
                       linewidths=0.8)
    ax.set_yticks(range(len(rows)))
    ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=8)
    for pname in ("entry", "approach", "manipulation", "retreat"):
        rng = insp["phases"].get(pname)
        if rng:
            ax.axvline(rng[0], color="k", lw=0.6, ls="--")
            ax.text(rng[0] + 4, len(rows) - 0.4, pname, fontsize=7)
    ax.set_xlim(0, n)
    ax.set_xlabel("frame")
    ax.set_title(f"{stem}: per-frame status "
                 "(green ok, amber low-vis, blue no-depth, grey no pose, "
                 "red marker missing)")
    fig.tight_layout()
    out1 = paths.EVAL_REPORTS / f"{stem}_coverage_timeline.png"
    fig.savefig(out1, dpi=130)
    plt.close(fig)
    print(f"[+] {out1}")

    frame_idx = args.frame
    if frame_idx is None:
        sl = insp.get("representative_shortlist") or [{"frame": n // 2}]
        frame_idx = sl[0]["frame"]
    img = color_frame_from_bag(paths.VIDEO / f"{stem}.bag", frame_idx)
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.imshow(img)
    for mid, name, c in [(0, "wall", "cyan"), (1, "object", "yellow"),
                         (2, "desk", "magenta")]:
        det = aruco[f"m{mid}_detected"].to_numpy().astype(bool)
        u = aruco[f"m{mid}_u"].to_numpy()[det]
        v = aruco[f"m{mid}_v"].to_numpy()[det]
        ax.plot(u, v, ".", ms=1.5, color=c, alpha=0.4)
        row = aruco.iloc[frame_idx]
        if row[f"m{mid}_detected"]:
            ax.plot(row[f"m{mid}_u"], row[f"m{mid}_v"], "o", ms=10,
                    mfc="none", mec=c, mew=2)
            ax.annotate(f"{name} (id {mid})",
                        (row[f"m{mid}_u"], row[f"m{mid}_v"]),
                        textcoords="offset points", xytext=(10, 10),
                        color=c, fontsize=9)
    ax.set_title(f"{stem} frame {frame_idx}: marker centers "
                 "(dots = full-recording track, circles = this frame)")
    ax.axis("off")
    fig.tight_layout()
    out2 = paths.EVAL_REPORTS / f"{stem}_marker_overlay.png"
    fig.savefig(out2, dpi=130)
    plt.close(fig)
    print(f"[+] {out2}")


if __name__ == "__main__":
    main()
