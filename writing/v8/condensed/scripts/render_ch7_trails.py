#!/usr/bin/env python3
"""Render new Unity stills from the previous capture's saved stream.

The original video and tracking pipelines are never opened. Requires a
closed Unity editor. The opt-in view config is removed after the capture.
A run is accepted only when every still, record and receiver log was
written after the editor was launched; the accepted set is pinned in
manifest.json (SHA-256 per file plus the digest of the view config) and
the editor's capture lines are copied to capture.txt, both committed
beside the stills so validate_ch7_trails_revision.py can bind the
figure to this run.
"""
import argparse
import hashlib
import json
import os
import signal
import shutil
import subprocess
import sys
import time
from pathlib import Path

from ch7_trail_data import REPO, ROOT, SETUPS, write_view_config

sys.path.insert(0, str(REPO / "eval/unity_check"))
from run_unity_capture import editor_pids, unity_binary  # noqa: E402

# --alias selects the recording (ch7_trail_data.SETUPS): r6b, the recording
# of Chapter 2 (Figure 7.10, default, unchanged), or r7, the two-hand take
# (E-034), whose saved stream and stills live in their own folders and whose
# trunk length is passed to the receiver through /tmp/r5_torso_m as the
# sensor-view capture did (run_unity_capture.py --torso-m).
ALIAS = "r6b"
STREAM = SETUPS[ALIAS]["stream"]
STATE = Path("/tmp/r5_autoplay_state")
FLAGS = {name: Path("/tmp/r5_autoplay_" + name) for name in ("on", "stop", "quit")}
LOGDIR = SETUPS[ALIAS]["src"]
TORSO_M = {"r6b": None, "r7": 0.517}   # r6b: the receiver's built-in 0.576
TORSO_FLAG = Path("/tmp/r5_torso_m")
RUNTIME_LOGS = [REPO / "v1/integration/output" / name for name in
                ("unity_person_log.csv", "unity_object_log.csv", "rig_dimensions.csv")]


def select(alias):
    global ALIAS, STREAM, LOGDIR
    ALIAS = alias
    STREAM = SETUPS[alias]["stream"]
    LOGDIR = SETUPS[alias]["src"]


def replay():
    import pandas as pd
    from send_scene_r5 import ShmWriter, write_scene, P
    data = pd.read_csv(STREAM)
    calib = json.loads(P.calib_for(SETUPS[ALIAS]["stem"]).read_text())
    write_scene("/dev/shm/aruco_scene", calib)
    writer = ShmWriter("/dev/shm/integrated_scene")
    config = json.loads(Path("/tmp/ch7_trails_view.json").read_text())
    endpoints = {p["last"]: p["name"] for p in config["phases"]}
    started = time.time()
    print("Replaying saved stream:", STREAM, flush=True)
    while True:
        start = time.monotonic()
        for row in data.to_dict("records"):
            delay = start + row["time_s"] - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            writer.write(int(row["frame"]), row["time_s"],
                         [row[k] for k in ("pel_x", "pel_y", "pel_z")],
                         [row[f"a{i}"] for i in range(13)],
                         [row[k] for k in ("opx", "opy", "opz")],
                         [row[k] for k in ("oex", "oey", "oez")],
                         int(row["mask"]), int(row["obj_live"]))
            if int(row["frame"]) in endpoints:
                # Hold the exact saved endpoint until the renderer acknowledges it.
                # A zero-duration last frame can otherwise be skipped at loop wrap.
                path = LOGDIR / (endpoints[int(row["frame"])] + ".json")
                paused = time.monotonic()
                while not (path.exists() and path.stat().st_mtime > started):
                    if FLAGS["stop"].exists() or FLAGS["quit"].exists():
                        return
                    if time.monotonic() - paused > 600:
                        raise RuntimeError("No capture acknowledgement for saved endpoint")
                    time.sleep(0.1)
                start += time.monotonic() - paused
        print("Completed saved-stream pass", flush=True)


def fresh(path, since):
    return path.exists() and path.stat().st_mtime > since


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_manifest(config, launched):
    """Pin the accepted capture: every artefact of this run and the config it used."""
    names = [p["name"] + ext for p in config["phases"] for ext in (".png", ".json")]
    names += [path.name for path in RUNTIME_LOGS if (LOGDIR / path.name).exists()]
    manifest = {"launched": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(launched)),
                "view_config_sha256": digest(SETUPS[ALIAS]["view"]),
                "files": {name: {"bytes": (LOGDIR / name).stat().st_size,
                                 "sha256": digest(LOGDIR / name)} for name in names}}
    (LOGDIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    lines = [line for line in (LOGDIR / "editor.log").read_text(errors="replace").splitlines()
             if "[Chapter7TrailView] captured" in line]
    (LOGDIR / "capture.txt").write_text(
        "Editor capture lines of the accepted run (editor.log is not committed), launched "
        + manifest["launched"] + "\n" + "\n".join(lines) + "\n")
    print("Manifest written:", LOGDIR / "manifest.json", len(names), "files")


def shutdown(process, timeout):
    """Wait for a process, escalating to terminate and kill; never raises,
    so the cleanup after it (log restore, flag removal) always runs."""
    for action, wait in ((None, timeout), (process.terminate, 30), (process.kill, 10)):
        if action is not None:
            action()
        try:
            process.wait(timeout=wait)
            return
        except subprocess.TimeoutExpired:
            continue
    print("WARNING: process", process.pid, "did not exit", flush=True)


def state():
    if not STATE.exists():
        return {}
    try:
        return json.loads(STATE.read_text())
    except json.JSONDecodeError:
        return {}  # The editor writes the status file while it is read.


def main():
    if editor_pids():
        raise RuntimeError("An editor is open; refusing to disturb its scene")
    if Path("/tmp/r5_capture_on").exists() or Path("/tmp/r5_trails.txt").exists():
        raise RuntimeError("Another capture mode is armed; refusing to overwrite it")
    write_view_config(ALIAS)
    config = json.loads(SETUPS[ALIAS]["view"].read_text())
    LOGDIR.mkdir(parents=True, exist_ok=True)
    for flag in FLAGS.values():
        flag.unlink(missing_ok=True)
    STATE.unlink(missing_ok=True)
    TORSO_FLAG.unlink(missing_ok=True)
    if TORSO_M[ALIAS]:
        TORSO_FLAG.write_text(f"{TORSO_M[ALIAS]:.4f}\n")
    sender = editor = None
    captured = False
    stale = []
    # The frozen receiver uses fixed scratch-log paths. Preserve existing logs
    # before it opens them, then archive this capture's logs and restore them.
    previous_logs = {path: path.read_bytes() if path.exists() else None for path in RUNTIME_LOGS}
    launched = None
    try:
        with (LOGDIR / "sender.log").open("w") as slog:
            sender = subprocess.Popen([sys.executable, __file__, "--replay", "--alias", ALIAS], stdout=slog,
                                      stderr=subprocess.STDOUT, start_new_session=True)
        # Readiness comes from both mappings existing and a running sender.
        deadline = time.monotonic() + 60
        while not all(Path("/dev/shm", name).exists() for name in ("aruco_scene", "integrated_scene")):
            if sender.poll() is not None or time.monotonic() > deadline:
                raise RuntimeError("Saved-stream sender failed to become ready; see sender.log")
            time.sleep(0.2)
        FLAGS["on"].write_text("ch7 presentation\n")
        launched = time.time()  # everything accepted below must be written after this
        editor = subprocess.Popen([unity_binary(), "-projectPath", str(REPO / "Unity"),
                                   "-logFile", str(LOGDIR / "editor.log")],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
                                  env=dict(os.environ, DISPLAY=os.environ.get("DISPLAY", ":0")),
                                  start_new_session=True)
        deadline = time.monotonic() + 600
        expected = [LOGDIR / (p["name"] + ".json") for p in config["phases"]]
        while True:
            ready = [p for p in expected if fresh(p, launched)]
            if len(ready) == len(expected):
                break
            if editor.poll() is not None or sender.poll() is not None:
                raise RuntimeError("Capture process exited before all phase stills were written")
            if time.monotonic() > deadline:
                raise RuntimeError("Capture deadline reached; see editor.log")
            print("Waiting for phase stills:", len(ready), "/", len(expected), state(), flush=True)
            time.sleep(5)
        for phase, path in zip(config["phases"], expected):
            record = json.loads(path.read_text())
            if record["appliedFrame"] != phase["last"]:
                raise RuntimeError("Captured frame does not match the phase endpoint")
            if not fresh(path.with_suffix(".png"), launched):
                raise RuntimeError("Still not written by this run: " + path.with_suffix(".png").name)
        print("PASS: all phase stills captured at the requested saved frames", flush=True)
        captured = True
    finally:
        # The existing editor bootstrap also requires this flag for stop/quit.
        # Leave it present until the editor has acknowledged shutdown.
        FLAGS["stop"].write_text("stop\n")
        deadline = time.monotonic() + 120
        while editor is not None and editor.poll() is None and state().get("playing"):
            if time.monotonic() > deadline:
                break
            time.sleep(1)
        FLAGS["quit"].write_text("quit\n")
        if editor is not None:
            shutdown(editor, 120)
        if sender is not None and sender.poll() is None:
            os.killpg(sender.pid, signal.SIGTERM)
            shutdown(sender, 30)
        for path, previous in previous_logs.items():
            # Archive only what this run wrote; a leftover log must not pass as evidence.
            if launched is not None and fresh(path, launched):
                shutil.copy2(path, LOGDIR / path.name)
            else:
                stale.append(path.name)
            if previous is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(previous)
        Path("/tmp/ch7_trails_view.json").unlink(missing_ok=True)
        TORSO_FLAG.unlink(missing_ok=True)
        for flag in FLAGS.values():
            flag.unlink(missing_ok=True)
    if captured:
        if stale:
            raise RuntimeError("Receiver logs not written by this run: " + ", ".join(sorted(stale)))
        write_manifest(config, launched)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay", action="store_true")
    parser.add_argument("--alias", default="r6b", choices=sorted(SETUPS))
    args = parser.parse_args()
    select(args.alias)
    replay() if args.replay else main()
