#!/usr/bin/env python3
"""Live sensor view of a running v2 stack: a READ-ONLY consumer of the
PSF1 frame ring (/dev/shm/rt_frames). Shows the aligned color stream
and a depth colormap side by side in one window, with frame index,
hardware timestamp, and display fps overlaid. It never opens the
camera (the broker owns the device) and never writes to the ring, so
it can attach and detach at any time without disturbing the pipelines.

Run alongside any live or bag session:
    python v2/common/ring_viewer.py            # q or ESC to close
    python v2/common/ring_viewer.py --snapshot out.png   # also save the
                                               # first composed frame

Exits on its own when the broker signals EOF on the ring.
"""
import argparse
import sys
import time
from pathlib import Path

import cv2
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shm_ring import DEFAULT_PATH, FrameRingReader  # noqa: E402

RGB8 = 2  # int(rs.format.rgb8); bgr8 is 6 -- frames pass through as-is
DEPTH_MAX_M = 3.0


def compose(sample, reader, fps):
    color = sample.color
    if reader.color_format == RGB8:
        color = cv2.cvtColor(color, cv2.COLOR_RGB2BGR)
    d_m = sample.depth.astype(np.float32) * reader.depth_scale
    d8 = np.clip(d_m / DEPTH_MAX_M, 0.0, 1.0)
    d8 = (255 - d8 * 255).astype(np.uint8)          # near = bright
    d8[sample.depth == 0] = 0                       # no return = black
    dvis = cv2.applyColorMap(d8, cv2.COLORMAP_TURBO)
    dvis[sample.depth == 0] = 0
    vis = np.hstack([color, dvis])
    cv2.putText(vis, f"frame {sample.frame_idx}  hw {sample.hw_ts_ms:.0f} ms"
                f"  view {fps:.1f} fps", (10, 24),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(vis, f"depth 0-{DEPTH_MAX_M:.0f} m", (color.shape[1] + 10, 24),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    return vis


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--path", default=DEFAULT_PATH)
    ap.add_argument("--wait", type=float, default=60.0,
                    help="seconds to wait for the ring to appear")
    ap.add_argument("--snapshot", default=None,
                    help="save the first composed frame to this PNG")
    args = ap.parse_args()

    print(f"[viewer] waiting for ring {args.path} (up to {args.wait:.0f} s)")
    reader = FrameRingReader(args.path, wait_s=args.wait)
    print(f"[viewer] attached: {reader.width}x{reader.height}, depth scale "
          f"{reader.depth_scale} m/unit")

    last_c, shown = 0, 0
    t_fps, n_fps, fps = time.monotonic(), 0, 0.0
    try:
        while True:
            try:
                last_c, sample = reader.latest(last_c, timeout_s=5.0)
            except TimeoutError:
                print("[viewer] ring writer silent, closing")
                break
            if sample is None:
                print("[viewer] ring EOF, closing")
                break
            n_fps += 1
            now = time.monotonic()
            if now - t_fps >= 1.0:
                fps = n_fps / (now - t_fps)
                t_fps, n_fps = now, 0
            vis = compose(sample, reader, fps)
            if args.snapshot and shown == 0:
                cv2.imwrite(args.snapshot, vis)
                print(f"[viewer] snapshot -> {args.snapshot}")
            shown += 1
            cv2.imshow("v2 sensor view", vis)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        cv2.destroyAllWindows()
    print(f"[viewer] closed after {shown} frames")


if __name__ == "__main__":
    main()
