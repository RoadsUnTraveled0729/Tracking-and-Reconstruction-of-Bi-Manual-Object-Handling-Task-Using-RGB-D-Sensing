"""Generate the ArUco marker card textures the Unity scene renders on
its marker plates (ArucoSceneReceiver.MarkerPlate; user request
2026-08-26). Same dictionary the pipeline detects (DICT_5X5_50, ids
0 wall / 1 object / 2 desk), drawn as the printed card: the black
marker square centered on a white margin (the margin is ~10 percent
of the card per side, matching the physical prints closely enough
for display).

Run: python eval/unity_check/make_marker_textures.py
Writes eval/output/markers/aruco_id{0,1,2}.png
"""
import sys
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "common"))
import paths  # noqa: E402

OUT = paths.EVAL_OUT / "markers"
MARKER_PX = 250
MARGIN_PX = 25


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
    for mid in (0, 1, 2):
        m = cv2.aruco.generateImageMarker(d, mid, MARKER_PX)
        card = np.full((MARKER_PX + 2 * MARGIN_PX,) * 2, 255, np.uint8)
        card[MARGIN_PX:MARGIN_PX + MARKER_PX,
             MARGIN_PX:MARGIN_PX + MARKER_PX] = m
        f = OUT / f"aruco_id{mid}.png"
        cv2.imwrite(str(f), card)
        print(f"[+] {f}")


if __name__ == "__main__":
    main()
