#!/usr/bin/env python3
# Filename: mediapipe/plot_skeleton.py
# Animated 3D playback of a landmark CSV produced by extract_landmarks_to_csv.py.
#
# Reads the per-frame camera-frame XYZ columns and animates the torso/arm
# skeleton in a matplotlib 3D axis. Consumes the CSV (not the bag), so it
# stays decoupled from the extraction stage.
#
# Usage:
#   python plot_skeleton.py                       # newest CSV in output/, interactive window
#   python plot_skeleton.py --csv output/foo.csv --save output/foo.mp4
#   python plot_skeleton.py --step 3 --speed 2    # lighter/faster playback

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter

LANDMARKS = ["left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
             "left_wrist", "right_wrist", "left_hip", "right_hip"]

BONES = [
    ("left_shoulder", "right_shoulder"),
    ("left_hip", "right_hip"),
    ("left_shoulder", "left_hip"),
    ("right_shoulder", "right_hip"),
    ("left_shoulder", "left_elbow"),
    ("left_elbow", "left_wrist"),
    ("right_shoulder", "right_elbow"),
    ("right_elbow", "right_wrist"),
]

LEFT_COLOR, RIGHT_COLOR, TORSO_COLOR = "tab:blue", "tab:red", "0.4"


def bone_color(a, b):
    if a.startswith("left") and b.startswith("left"):
        return LEFT_COLOR
    if a.startswith("right") and b.startswith("right"):
        return RIGHT_COLOR
    return TORSO_COLOR


def load_frames(csv_path, step):
    df = pd.read_csv(csv_path)
    missing = [n for n in LANDMARKS if f"{n}_x" not in df.columns]
    if missing:
        sys.exit(f"[ERROR] CSV lacks columns for: {missing}")
    df = df.iloc[::step].reset_index(drop=True)
    # (F, L, 3) camera frame; NaN where depth was missing
    pts = np.stack([df[[f"{n}_x", f"{n}_y", f"{n}_z"]].to_numpy(float) for n in LANDMARKS], axis=1)
    return df["frame"].to_numpy(), df["time_s"].to_numpy(), pts


def to_plot_coords(pts):
    """Camera frame (X right, Y down, Z forward) -> plot axes so the person
    stands upright: plot x = X, plot y = Z (depth away), plot z = -Y (up)."""
    return np.stack([pts[..., 0], pts[..., 2], -pts[..., 1]], axis=-1)


def main():
    script_dir = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Animate a landmark CSV as a 3D skeleton.")
    ap.add_argument("--csv", default=None,
                    help="Landmark CSV (default: newest *_landmarks_*.csv in output/)")
    ap.add_argument("--save", default=None,
                    help="Write animation to .mp4 (ffmpeg) or .gif instead of only showing it")
    ap.add_argument("--step", type=int, default=1, help="Use every Nth frame (default 1)")
    ap.add_argument("--speed", type=float, default=1.0, help="Playback speed multiplier")
    ap.add_argument("--no-show", action="store_true", help="Skip the interactive window")
    args = ap.parse_args()

    if args.csv:
        csv_path = Path(args.csv)
    else:
        candidates = sorted((script_dir / "output").glob("*_landmarks.csv"),
                            key=lambda p: p.stat().st_mtime)
        if not candidates:
            sys.exit("[ERROR] No *_landmarks.csv in output/ — run extract_landmarks_to_csv.py first")
        csv_path = candidates[-1]
    if not csv_path.exists():
        sys.exit(f"[ERROR] CSV not found: {csv_path}")

    frames, times, pts = load_frames(csv_path, args.step)
    p = to_plot_coords(pts)
    n_frames = len(frames)
    dt = float(np.nanmedian(np.diff(times))) if n_frames > 1 else 1 / 30
    interval_ms = max(1, int(dt * 1000 / args.speed))
    print(f"[INFO] {csv_path.name}: {n_frames} frames, dt={dt*1000:.1f} ms, "
          f"playback interval {interval_ms} ms")

    # Fixed axis limits over the whole clip, equal aspect so lengths aren't skewed
    lo = np.nanpercentile(p.reshape(-1, 3), 1, axis=0) - 0.1
    hi = np.nanpercentile(p.reshape(-1, 3), 99, axis=0) + 0.1
    center, half = (lo + hi) / 2, np.max(hi - lo) / 2

    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(111, projection="3d")
    ax.set_xlim(center[0] - half, center[0] + half)
    ax.set_ylim(center[1] - half, center[1] + half)
    ax.set_zlim(center[2] - half, center[2] + half)
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel("X (m, right)")
    ax.set_ylabel("Z (m, depth)")
    ax.set_zlabel("-Y (m, up)")
    ax.view_init(elev=15, azim=-75)

    idx = {n: i for i, n in enumerate(LANDMARKS)}
    bone_lines = [ax.plot([], [], [], lw=3, color=bone_color(a, b))[0] for a, b in BONES]
    joints, = ax.plot([], [], [], "o", ms=5, color="k")
    title = ax.set_title("")

    def update(f):
        q = p[f]
        for line, (a, b) in zip(bone_lines, BONES):
            seg = q[[idx[a], idx[b]]]
            line.set_data_3d(seg[:, 0], seg[:, 1], seg[:, 2])
        joints.set_data_3d(q[:, 0], q[:, 1], q[:, 2])
        title.set_text(f"{csv_path.stem}  |  frame {frames[f]}  t={times[f]:.2f}s  "
                       f"(blue=left, red=right)")
        return [*bone_lines, joints, title]

    anim = FuncAnimation(fig, update, frames=n_frames, interval=interval_ms, blit=False)

    if args.save:
        save_path = Path(args.save)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        fps = max(1, int(round(1 / dt * args.speed)))
        if save_path.suffix == ".mp4":
            writer = FFMpegWriter(fps=fps, bitrate=2000)
        elif save_path.suffix == ".gif":
            writer = PillowWriter(fps=min(fps, 30))
        else:
            sys.exit("[ERROR] --save must end in .mp4 or .gif")
        print(f"[INFO] Writing {save_path} at {fps} fps ...")
        anim.save(save_path, writer=writer)
        print(f"[+] Saved: {save_path}")

    if not args.no_show:
        plt.show()


if __name__ == "__main__":
    main()
