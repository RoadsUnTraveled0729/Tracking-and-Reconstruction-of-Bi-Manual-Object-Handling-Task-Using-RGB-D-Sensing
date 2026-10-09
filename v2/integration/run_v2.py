#!/usr/bin/env python3
# Filename: v2/integration/run_v2.py
"""v2 launcher: capture broker + Pipeline A + Pipeline B (+ merger).

  [broker] v2/broker/capture_broker.py -> /dev/shm/rt_frames      (PSF1)
  [A]      v2/person/v2_person.py      -> /dev/shm/rt_person_v2   (PSR1)
  [B]      v2/object/v2_object.py      -> /dev/shm/rt_object_v2   (PSB2)
  [I]      v2/integration/v2_integrate.py
                                       -> /dev/shm/aruco_scene    (PSB3)
                                       -> /dev/shm/integrated_scene_v2 (PSI2)

Start barrier: every process touches <sync>.ready.<name> after init and
blocks until /dev/shm/rt_go_v2 exists; the launcher creates it when all
are ready, so the broker starts the device only when both consumers are
attached (same skew fix as v1, now also gating the one physical device).

With --calibrate (live sessions, or the bag dress rehearsal): the broker
is released FIRST, live_calibrate.py runs to produce
v2/output/scene_calibration_live.json from the stream, and only then are
the pipelines launched against that JSON.

Usage:
  python run_v2.py --source bag  [--dump] [--profile] [--no-merge]
  python run_v2.py --source live [--record out.bag] [--calibrate]
"""
import argparse
import signal
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                 # repo root
PY = sys.executable

RING = "/dev/shm/rt_frames"
SYNC = "/dev/shm/rt_go_v2"
SHM_PERSON = "/dev/shm/rt_person_v2"
SHM_OBJECT = "/dev/shm/rt_object_v2"
SHM_OUT = "/dev/shm/integrated_scene_v2"


def wait_ready(names, procs, timeout=90.0):
    t0 = time.monotonic()
    while not all(Path(SYNC + ".ready." + n).exists() for n in names):
        if time.monotonic() - t0 > timeout:
            raise RuntimeError(f"processes never became ready: {names}")
        if any(p.poll() not in (None, 0) for p in procs):
            raise RuntimeError("a process exited during init")
        time.sleep(0.02)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=("bag", "live"), default="bag")
    ap.add_argument("--bag", default=str(ROOT / "Video/recording_20260224_083945.bag"))
    ap.add_argument("--calib", default=str(ROOT / "v1/aruco/output/scene_calibration.json"))
    ap.add_argument("--calibrate", action="store_true",
                    help="calibrate the scene from the stream before "
                         "launching the pipelines (required for a live "
                         "session with a repositioned camera; on bag it "
                         "is the camera-free dress rehearsal)")
    ap.add_argument("--record", default=None,
                    help="live only: tee the session to this bag")
    ap.add_argument("--cube-size", type=float, default=None,
                    help="forwarded to live_calibrate.py when the cube "
                         "does not rest on the desk during calibration "
                         "(the pinned recording needs 0.07)")
    ap.add_argument("--profile", action="store_true")
    ap.add_argument("--robust-occlusion", action="store_true",
                    help="Pipeline A uses the robust occlusion solver "
                         "(v1/kinematics/occlusion_ext.py)")
    ap.add_argument("--dump", action="store_true",
                    help="write v2_*_dump.csv from all stages")
    ap.add_argument("--max-frames", type=int, default=None)
    ap.add_argument("--delay-frames", type=int, default=2)
    ap.add_argument("--start-delay", type=float, default=0.0,
                    help="hold the start barrier this long once everyone "
                         "is ready (lets a screen capture start first)")
    ap.add_argument("--no-merge", action="store_true",
                    help="skip the merger (pipeline bring-up/debug)")
    ap.add_argument("--object-recovery", action="store_true",
                    help="Pipeline A reads Pipeline B's object pose and "
                         "recovers a holding hand's lost wrist from it "
                         "(E-014 live; implies --robust-occlusion)")
    ap.add_argument("--plausibility-gate", action="store_true",
                    help="Pipeline B rejects physically implausible "
                         "object samples (E-019 live)")
    ap.add_argument("--display-lpf", action="store_true",
                    help="merger smooths the Unity packet (E-018; "
                         "dumps stay raw)")
    ap.add_argument("--probe-r5", action="store_true",
                    help="R5 real-time probe preset: R5 bag + true-size "
                         "calibration (make_r5_calib.py) + robust solver "
                         "+ object recovery + plausibility gate + "
                         "display smoother")
    args = ap.parse_args()
    if args.probe_r5:
        args.bag = str(ROOT / "Video/recording_20260825_222315.bag")
        args.calib = str(ROOT / "v2/output/scene_calibration_r5_v2.json")
        args.object_recovery = True
        args.plausibility_gate = True
        args.display_lpf = True
    if args.object_recovery:
        args.robust_occlusion = True

    for p in (RING, SHM_PERSON, SHM_OBJECT, SHM_OUT, SYNC,
              SYNC + ".ready.broker", SYNC + ".ready.person",
              SYNC + ".ready.object"):
        Path(p).unlink(missing_ok=True)

    out_dir = ROOT / "v2/output"
    out_dir.mkdir(exist_ok=True)

    broker_cmd = [PY, str(ROOT / "v2/broker/capture_broker.py"),
                  "--source", args.source, "--ring", RING,
                  "--sync-file", SYNC]
    if args.source == "bag":
        broker_cmd += ["--bag", args.bag]
    if args.record:
        broker_cmd += ["--record", args.record]
    if args.max_frames:
        broker_cmd += ["--max-frames", str(args.max_frames)]

    calib = args.calib

    procs = [subprocess.Popen(broker_cmd)]
    try:
        if args.calibrate:
            # broker first: the calibrator needs frames before A/B start
            wait_ready(["broker"], procs)
            if args.start_delay:
                time.sleep(args.start_delay)
            Path(SYNC).touch()
            print("[launcher] broker started -- calibrating the scene")
            calib = str(out_dir / "scene_calibration_live.json")
            cal_cmd = [PY, str(ROOT / "v2/calibration/live_calibrate.py"),
                       "--ring", RING, "--out", calib]
            if args.source == "bag":
                # dress rehearsal: no auto-exposure settle to skip, and
                # diff the result against the frozen offline calibration
                cal_cmd += ["--skip", "0", "--compare", args.calib]
            if args.cube_size is not None:
                cal_cmd += ["--cube-size", str(args.cube_size)]
            rc = subprocess.call(cal_cmd)
            if rc != 0:
                raise RuntimeError("live calibration failed")

        a_cmd = [PY, str(ROOT / "v2/person/v2_person.py")] \
            + (["--robust-occlusion"] if args.robust_occlusion else []) \
            + (["--object-recovery", "--obj-shm", SHM_OBJECT,
                "--calib", calib] if args.object_recovery else []) + [
                 "--ring", RING, "--shm", SHM_PERSON]
        b_cmd = [PY, str(ROOT / "v2/object/v2_object.py"),
                 "--ring", RING, "--shm", SHM_OBJECT, "--calib", calib] \
            + (["--plausibility-gate"] if args.plausibility_gate else [])
        if not args.calibrate:
            a_cmd += ["--sync-file", SYNC]
            b_cmd += ["--sync-file", SYNC]
        if args.profile:
            a_cmd.append("--profile")
            b_cmd.append("--profile")
        if args.dump:
            a_cmd += ["--dump-csv", str(out_dir / "v2_person_dump.csv")]
            b_cmd += ["--dump-csv", str(out_dir / "v2_object_dump.csv")]
        procs += [subprocess.Popen(a_cmd), subprocess.Popen(b_cmd)]

        if not args.calibrate:
            wait_ready(["broker", "person", "object"], procs)
            if args.start_delay:
                time.sleep(args.start_delay)
            Path(SYNC).touch()
            print("[launcher] broker + pipelines ready -- stream started")

        if args.no_merge:
            for p in procs[1:]:
                p.wait()
            rc = 0
        else:
            merge_cmd = [PY, str(HERE / "v2_integrate.py"),
                         "--calib", calib,
                         "--person", SHM_PERSON, "--object", SHM_OBJECT,
                         "--out", SHM_OUT,
                         "--delay-frames", str(args.delay_frames)] \
                + (["--display-lpf"] if args.display_lpf else [])
            if args.dump:
                merge_cmd += ["--dump-csv",
                              str(out_dir / "v2_integrate_dump.csv")]
            rc = subprocess.call(merge_cmd)
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
