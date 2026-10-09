#!/usr/bin/env python3
"""Publish a synthetic PSV3 stream so the V3 Unity scene can be
verified end to end before the Phase 3 runner exists.

The pattern: a standing figure whose right arm swings; every 4 seconds
the right-arm groups cycle MEASURED -> ESTIMATED -> LOST so all three
colors are visible (right side: normal orange -> amber -> red). The 13
angles are REAL: each frame is solved by core.solver_q + core.convert
on the synthetic landmarks, so this also exercises the Phase 2 path
end to end.

Run (any python with numpy; no onnxruntime needed):

    /home/luo/anaconda3/bin/python v3/tools/psv3_demo_writer.py

then press Play in Unity scene V3Scene. Stop with Ctrl-C (removes the
shm file).
"""
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core import convert, solver_q                     # noqa: E402
from replay.psv3 import PSV3Writer                     # noqa: E402

FPS = 30.0
STATUS_CYCLE_S = 4.0


def synthetic_points(t):
    """Standing figure, right arm swinging front-to-side, elbow bend."""
    lh = np.array([-0.15, 0.90, 0.0])
    rh = np.array([0.15, 0.90, 0.0])
    ls = np.array([-0.20, 1.45, 0.0])
    rs = np.array([0.20, 1.45, 0.0])
    # right arm: shoulder-anchored swing
    a = 0.9 * np.sin(2 * np.pi * t / 6.0)          # swing phase
    upper = 0.30 * np.array([np.cos(a) * 1.0, -0.2, np.sin(a)])
    re = rs + upper / np.linalg.norm(upper) * 0.30
    bend = 0.6 + 0.5 * np.sin(2 * np.pi * t / 3.7)
    fore = np.array([np.cos(a + bend), -0.1, np.sin(a + bend)])
    rw = re + fore / np.linalg.norm(fore) * 0.26
    # left arm: gentle idle sway
    b = 0.25 * np.sin(2 * np.pi * t / 5.0)
    le = ls + 0.30 * np.array([-np.cos(b), -0.3, np.sin(b)]) / np.linalg.norm(
        [np.cos(b), 0.3, np.sin(b)])
    lw = le + np.array([-0.05, -0.25, 0.05])
    return {"left_hip": lh, "right_hip": rh,
            "left_shoulder": ls, "right_shoulder": rs,
            "left_elbow": le, "left_wrist": lw,
            "right_elbow": re, "right_wrist": rw}


def main():
    w = PSV3Writer()
    print(f"[demo] publishing PSV3 to {w.path} at {FPS:.0f} Hz; Ctrl-C stops")
    frame = 0
    t0 = time.monotonic()
    try:
        while True:
            t = time.monotonic() - t0
            pts = synthetic_points(t)
            out = solver_q.solve_frame_q(pts)
            angles = convert.angles13(out["root"], out["r_sh"],
                                      out["r_elb"], out["l_sh"],
                                      out["l_elb"])
            phase = int(t / STATUS_CYCLE_S) % 3    # 0 MEAS 1 EST 2 LOST
            status = [0, phase, phase, phase, 0, 0, 0]
            w.write(frame, t, pts, angles, status)
            frame += 1
            time.sleep(max(0.0, (frame / FPS) - (time.monotonic() - t0)))
    except KeyboardInterrupt:
        pass
    finally:
        w.close(unlink=True)
        print(f"\n[demo] stopped after {frame} frames; shm removed")


if __name__ == "__main__":
    main()
