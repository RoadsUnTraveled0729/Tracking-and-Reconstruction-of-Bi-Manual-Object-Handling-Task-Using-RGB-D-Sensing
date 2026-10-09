#!/usr/bin/env python3
# Filename: realtime/integration/run_realtime.py
"""Launcher for the real-time demo: spawns Pipeline A and Pipeline B as
independent processes (they share nothing but the bag file), then runs the
merger in this process. One Ctrl-C tears everything down.

  [A] mediapipe/realtime_person.py  -> /dev/shm/rt_person   (PSR1)
  [B] aruco/realtime_object.py      -> /dev/shm/rt_object   (PSB2)
  [I] realtime_integrate.py         -> /dev/shm/aruco_scene (PSB3, once)
                                       /dev/shm/integrated_scene (PSI1)

Unity's IntegratedSceneReceiver bootstraps from those two regions exactly
as in the offline demo — no Unity change.

Usage:
  python run_realtime.py [--bag ../Video/recording_20260224_083945.bag]
      [--profile] [--dump] [--max-frames N]
"""
import argparse
import os
import signal
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                 # repo root
PY = sys.executable


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bag", default=str(ROOT / "Video/recording_20260224_083945.bag"))
    ap.add_argument("--calib", default=str(ROOT / "aruco/output/scene_calibration.json"))
    ap.add_argument("--profile", action="store_true")
    ap.add_argument("--dump", action="store_true",
                    help="write rt_*_dump.csv from both pipelines")
    ap.add_argument("--max-frames", type=int, default=None)
    ap.add_argument("--start-delay", type=float, default=0.0,
                    help="hold the start barrier this long after both "
                         "pipelines are ready (lets a screen capture start "
                         "before playback; trim = mtime(/dev/shm/rt_go) "
                         "minus capture start)")
    args = ap.parse_args()

    # stale regions from a previous run would satisfy the merger's wait_for
    sync = "/dev/shm/rt_go"
    for p in ("/dev/shm/rt_person", "/dev/shm/rt_object", sync,
              sync + ".ready.person", sync + ".ready.object"):
        Path(p).unlink(missing_ok=True)

    a_cmd = [PY, str(HERE.parent / "person/realtime_person.py"),
             "--bag", args.bag, "--sync-file", sync]
    b_cmd = [PY, str(HERE.parent / "object/realtime_object.py"),
             "--bag", args.bag, "--calib", args.calib, "--sync-file", sync]
    if args.profile:
        a_cmd.append("--profile")
        b_cmd.append("--profile")
    if args.dump:
        a_cmd += ["--dump-csv", str(HERE.parent / "output/rt_person_dump.csv")]
        b_cmd += ["--dump-csv", str(HERE.parent / "output/rt_object_dump.csv")]
    if args.max_frames:
        a_cmd += ["--max-frames", str(args.max_frames)]
        b_cmd += ["--max-frames", str(args.max_frames)]

    procs = [subprocess.Popen(a_cmd), subprocess.Popen(b_cmd)]
    try:
        # release the start barrier once both pipelines finished init
        import time
        t0 = time.monotonic()
        while not (Path(sync + ".ready.person").exists()
                   and Path(sync + ".ready.object").exists()):
            if time.monotonic() - t0 > 60:
                raise RuntimeError("pipelines never became ready")
            if any(p.poll() is not None for p in procs):
                raise RuntimeError("a pipeline exited during init")
            time.sleep(0.02)
        if args.start_delay:
            time.sleep(args.start_delay)
        Path(sync).touch()
        print("[launcher] both pipelines ready — playback started")
        rc = subprocess.call([PY, str(HERE / "realtime_integrate.py"),
                              "--calib", args.calib])
    except KeyboardInterrupt:
        rc = 130
    finally:
        for p in procs:
            if p.poll() is None:
                p.send_signal(signal.SIGINT)
        for p in procs:
            try:
                p.wait(timeout=10)
            except subprocess.TimeoutExpired:
                p.kill()
    sys.exit(rc)


if __name__ == "__main__":
    main()
