#!/usr/bin/env python3
"""Unattended Unity capture for the R5 pose check (eval/unity_check/).

Drives the whole loop with no human at the keyboard:

  1. clears the capture output and the play-mode flags;
  2. arms EvalFrameDump (/tmp/r5_capture_on) and EvalPlayBootstrap
     (/tmp/r5_autoplay_on);
  3. starts send_scene_r5.py in --loop -- BOTH /dev/shm files must exist
     before Unity enters play mode, because IntegratedSceneReceiver only
     self-spawns when it finds them at Play start and never re-maps;
  4. writes the rig sizing side channel (/tmp/r5_rig_sizing, E-036) from
     the recording's eval/reports/<alias>_rig_sizing.json, so that
     IntegratedSceneReceiver sizes the avatar for the recording replayed
     (arm segment medians of the offset fit, trunk length by the E-035
     rule) instead of carrying another recording's constants;
  5. launches the editor (it opens Assets/Scenes/rig.unity and presses Play
     itself via EvalPlayBootstrap);
  6. waits until the PNGs under /tmp/r5_frames cover the streamed frames
     (the dumper names each PNG by the applied stream frame, so coverage is
     just the count of distinct filenames); a C# compile error in the
     editor log abandons the run with a non-zero exit;
  7. stops play mode, quits the editor, stops the sender, removes the
     sizing file, and copies the receiver's logs of this run
     (unity_person_log.csv, unity_object_log.csv, rig_dimensions.csv,
     rig_sizing_used.txt) into --out next to integrated_stream.csv.

Usage:
  python eval/unity_check/run_unity_capture.py                 # v1 solve
  python eval/unity_check/run_unity_capture.py --angles-csv ...
  python eval/unity_check/run_unity_capture.py --stem <stem> --sizing <json>
"""
import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "eval"))
from common import paths as P  # noqa: E402

CAPTURE_FLAG = Path("/tmp/r5_capture_on")
FRAMES_DIR = Path("/tmp/r5_frames")
PLAY_ON = Path("/tmp/r5_autoplay_on")
PLAY_STOP = Path("/tmp/r5_autoplay_stop")
PLAY_QUIT = Path("/tmp/r5_autoplay_quit")
PLAY_STATE = Path("/tmp/r5_autoplay_state")
EDITOR_LOG = Path("/tmp/r5_unity_editor.log")
SENDER_LOG = Path("/tmp/r5_sender.log")
SIZING_FLAG = Path("/tmp/r5_rig_sizing")     # read by IntegratedSceneReceiver
RUNTIME_OUT = REPO / "v1" / "integration" / "output"
RUNTIME_LOGS = ("unity_person_log.csv", "unity_object_log.csv",
                "rig_dimensions.csv", "rig_sizing_used.txt")


def unity_binary():
    version = (REPO / "Unity" / "ProjectSettings"
               / "ProjectVersion.txt").read_text().split()[1]
    path = Path(os.path.expanduser(
        f"~/Unity/Hub/Editor/{version}/Editor/Unity"))
    if not path.exists():
        sys.exit(f"FAIL: Unity {version} not found at {path}")
    return str(path)


def editor_pids():
    out = subprocess.run(["pgrep", "-f", f"Editor/Unity.*{REPO / 'Unity'}"],
                         capture_output=True, text=True).stdout.split()
    return [int(p) for p in out]


def state():
    try:
        return json.loads(PLAY_STATE.read_text())
    except Exception:
        return {}


def frame_count():
    try:
        return sum(1 for _ in FRAMES_DIR.glob("f*.png"))
    except OSError:
        return 0


def sizing_default(stem):
    """eval/reports/<alias>_rig_sizing.json for a stem of paths.ALIAS."""
    alias = P.ALIAS.get(stem)
    if alias is None:
        sys.exit(f"FAIL: unknown recording stem {stem!r}; add it to "
                 "eval/common/paths.ALIAS or pass --sizing")
    return P.EVAL_REPORTS / f"{alias}_rig_sizing.json"


def compile_errors():
    """Lines of the editor log that report a C# compile error."""
    try:
        text = EDITOR_LOG.read_text(errors="replace")
    except OSError:
        return []
    return [line for line in text.splitlines() if "error CS" in line]


def copy_runtime_logs(out_dir, since):
    """Copy the receiver's logs written during this run into out_dir.

    A file older than the run is a leftover of an earlier capture and is
    left where it is, so the capture folder never carries another
    recording's rig."""
    for name in RUNTIME_LOGS:
        src = RUNTIME_OUT / name
        if not src.exists():
            print(f"[run] WARNING: {src} was not written", flush=True)
            continue
        if src.stat().st_mtime < since:
            print(f"[run] WARNING: {src} predates this run; not copied",
                  flush=True)
            continue
        shutil.copy2(src, out_dir / name)
        print(f"[run] copied {name} into {out_dir}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stem", default=P.R5_STEM)
    ap.add_argument("--angles-csv", default=None)
    ap.add_argument("--out", default=str(P.EVAL_OUT / "unity_check_r5"))
    ap.add_argument("--coverage", type=float, default=0.995,
                    help="stop once this fraction of streamed frames has a PNG")
    ap.add_argument("--max-minutes", type=float, default=25.0)
    ap.add_argument("--sizing", default=None,
                    help="rig sizing json of the recording replayed (E-036; "
                         "segment_lengths_m in metres, from "
                         "make_rig_sizing.py), written to /tmp/r5_rig_sizing "
                         "for IntegratedSceneReceiver during this capture "
                         "only; default: eval/reports/<alias>_rig_sizing.json "
                         "for --stem")
    args = ap.parse_args()

    # Resolve the sizing before anything is armed: a capture without it
    # would render an unsized rig and only a warning in the editor log
    # would tell.
    sizing = Path(args.sizing) if args.sizing else sizing_default(args.stem)
    if not sizing.exists():
        sys.exit(f"FAIL: rig sizing json {sizing} is missing; produce it with "
                 "eval/unity_check/make_rig_sizing.py before the capture")
    try:
        from make_rig_sizing import write_flag
    except ImportError as e:
        sys.exit("FAIL: eval/unity_check/make_rig_sizing.py is needed to "
                 f"write {SIZING_FLAG}: {e}")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    dump_csv = out_dir / "integrated_stream.csv"

    if editor_pids():
        sys.exit("FAIL: a Unity editor is already running on this project; "
                 "close it (or stop it) before an unattended capture")

    for f in (PLAY_STOP, PLAY_QUIT, PLAY_STATE, SIZING_FLAG):
        f.unlink(missing_ok=True)
    shutil.rmtree(FRAMES_DIR, ignore_errors=True)
    FRAMES_DIR.mkdir(parents=True)
    CAPTURE_FLAG.write_text("r5\n")
    PLAY_ON.write_text("r5\n")

    cmd = [sys.executable, str(REPO / "eval/unity_check/send_scene_r5.py"),
           "--stem", args.stem, "--loop", "--dump-csv", str(dump_csv)]
    if args.angles_csv:
        cmd += ["--angles-csv", args.angles_csv]
    print("[run] sender:", " ".join(cmd), flush=True)
    slog = open(SENDER_LOG, "wb")
    sender = subprocess.Popen(cmd, stdout=slog, stderr=slog, cwd=str(REPO),
                              start_new_session=True)

    # The sender solves before it streams; wait for both shm files.
    deadline = time.time() + 300
    while time.time() < deadline:
        if (Path("/dev/shm/aruco_scene").exists()
                and Path("/dev/shm/integrated_scene").exists()):
            break
        if sender.poll() is not None:
            sys.exit(f"FAIL: sender exited early; see {SENDER_LOG}")
        time.sleep(1)
    else:
        sys.exit("FAIL: sender never produced the shm files")
    n_stream = len([1 for _ in dump_csv.open()]) - 1
    print(f"[run] streaming {n_stream} frames; shm ready", flush=True)

    t_run = time.time()
    failure = None
    try:
        # Written just before the editor starts so the receiver's
        # freshness test (one hour) sees a file of this capture.
        flag = write_flag(sizing, SIZING_FLAG)
        print(f"[run] rig sizing {sizing} written to {flag}", flush=True)

        env = dict(os.environ, DISPLAY=os.environ.get("DISPLAY", ":0"))
        with open(EDITOR_LOG, "wb") as log:
            subprocess.Popen([unity_binary(), "-projectPath", str(REPO / "Unity")],
                             stdout=log, stderr=log, env=env, start_new_session=True)
        print(f"[run] editor launching (log {EDITOR_LOG})", flush=True)

        t0 = time.time()
        hard_deadline = t0 + args.max_minutes * 60
        last_n, stalled_since = -1, time.time()
        while time.time() < hard_deadline:
            n = frame_count()
            st = state()
            if n != last_n:
                last_n, stalled_since = n, time.time()
            if n and n >= args.coverage * n_stream:
                print(f"[run] coverage reached: {n}/{n_stream}", flush=True)
                break
            # A script that does not compile leaves the previous build's
            # receiver, or none, in play mode; nothing captured under it
            # can be trusted, so the run is abandoned here.
            errs = compile_errors()
            if errs:
                failure = ("compile error in the editor log: "
                           + errs[0].strip())
                print(f"[run] {failure}; aborting", flush=True)
                break
            # A play session that has been running a while and stopped producing
            # new frames is finished replaying (or wedged) either way.
            if st.get("playing") and n and time.time() - stalled_since > 180:
                print(f"[run] no new frames for 180 s at {n}/{n_stream}", flush=True)
                break
            if not editor_pids() and time.time() - t0 > 120:
                print("[run] editor exited unexpectedly", flush=True)
                break
            print(f"[wait] {int(time.time()-t0):4d}s  frames {n}/{n_stream}  "
                  f"state {st}", flush=True)
            time.sleep(10)

        print("[run] stopping play mode", flush=True)
        PLAY_STOP.write_text("stop\n")
        deadline = time.time() + 120
        while time.time() < deadline and state().get("playing"):
            time.sleep(2)
        PLAY_QUIT.write_text("quit\n")
        deadline = time.time() + 180
        while time.time() < deadline and editor_pids():
            time.sleep(2)
        for pid in editor_pids():
            os.kill(pid, signal.SIGTERM)
    finally:
        try:
            os.killpg(os.getpgid(sender.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass
        slog.close()
        # The sizing file is per capture: a leftover would size the next
        # capture, of any recording, with this one's lengths.
        CAPTURE_FLAG.unlink(missing_ok=True)
        PLAY_ON.unlink(missing_ok=True)
        SIZING_FLAG.unlink(missing_ok=True)

    n = frame_count()
    print(f"[run] DONE: {n} PNGs in {FRAMES_DIR} for {n_stream} streamed "
          f"frames ({100.0*n/max(n_stream,1):.1f}%)", flush=True)
    copy_runtime_logs(out_dir, t_run)
    if failure:
        sys.exit(f"FAIL: {failure}; see {EDITOR_LOG}")


if __name__ == "__main__":
    main()
