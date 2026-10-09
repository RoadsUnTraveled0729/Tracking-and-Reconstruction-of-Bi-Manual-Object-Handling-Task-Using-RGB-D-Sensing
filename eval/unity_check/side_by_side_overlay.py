#!/usr/bin/env python3
"""Unity render next to the OVERLAY video (R5).

Left  : the Unity sensor-POV half of side_by_side.mp4 (HUD kept).
Right : the same stream frame of the recovery overlay video
        (check_v1_overlay.py --recovery: measured landmarks, solved
        skeleton, recovered joints), with its own HUD band.
Both sources index frames by the stream frame number from 0, verified
by image matching at frames 100, 1000, 2000 (offset 0).

Run: python eval/unity_check/side_by_side_overlay.py
Out: eval/output/unity_check_r5/side_by_side_overlay.mp4
"""
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

REPO = Path(__file__).resolve().parents[2]
SBS = REPO / "eval/output/unity_check_r5/side_by_side.mp4"
OVL = REPO / "eval/output/recovery_r5_overlay/v1_overlay_recovery.mp4"
OUT = REPO / "eval/output/unity_check_r5/side_by_side_overlay.mp4"
BAND = 26
FONT = cv2.FONT_HERSHEY_SIMPLEX


def stamp(img, text):
    out = np.zeros((img.shape[0] + BAND, img.shape[1], 3), np.uint8)
    out[BAND:] = img
    cv2.putText(out, text, (8, BAND - 8), FONT, 0.55, (255, 255, 255), 1,
                cv2.LINE_AA)
    return out


def main():
    S, O = cv2.VideoCapture(str(SBS)), cv2.VideoCapture(str(OVL))
    fps = S.get(cv2.CAP_PROP_FPS)
    tmp = OUT.with_suffix(".raw.mp4")
    w = None
    i = 0
    while True:
        oks, s = S.read()
        oko, o = O.read()
        if not oks or not oko:
            break
        left = s[:, :640]

        right = stamp(o, f"VIDEO + OVERLAY  f{i:05d}")
        frame = np.hstack([left, right])
        if w is None:
            w = cv2.VideoWriter(str(tmp), cv2.VideoWriter_fourcc(*"mp4v"),
                                fps, (frame.shape[1], frame.shape[0]))
        w.write(frame)
        i += 1
    w.release()
    # re-encode to H.264 for browser playback
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "23",
                        str(OUT)])
    if r.returncode == 0:
        tmp.unlink()
    else:
        tmp.rename(OUT)
        print("[warn] ffmpeg unavailable; wrote mp4v")
    print(f"[+] {i} frames -> {OUT}")


if __name__ == "__main__":
    main()
