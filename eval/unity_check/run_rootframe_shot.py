#!/usr/bin/env python3
"""Unattended Scene-view screenshot of the rig root with Unity's own
transform gizmo (thesis Figure 3.2(b)).

Edit-mode only: no streaming and no play mode. Launches the editor with
/tmp/r5_rootshot_on armed; Assets/Editor/RootFrameShot.cs hides
everything but the rig, selects its top-most parent with the local Move
gizmo, frames it, and writes the Scene-view pixels to
/tmp/r5_rootshot.png. This script waits for the PNG and closes the
editor.

Usage:
  python eval/unity_check/run_rootframe_shot.py
"""
import argparse
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "eval" / "unity_check"))
import run_unity_capture as ruc          # noqa: E402  (unity_binary)

SHOT_FLAG = Path("/tmp/r5_rootshot_on")
SHOT_PNG = Path("/tmp/r5_rootshot.png")
SHOT_STATE = Path("/tmp/r5_rootshot_state")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-minutes", type=float, default=8.0)
    args = ap.parse_args()

    for f in (SHOT_PNG, SHOT_STATE):
        f.unlink(missing_ok=True)
    SHOT_FLAG.touch()

    editor = subprocess.Popen(
        [ruc.unity_binary(), "-projectPath", str(REPO / "Unity")],
        stdout=open("/tmp/r5_rootshot_editor.log", "w"),
        stderr=subprocess.STDOUT)
    print("[shot] editor launching; waiting for", SHOT_PNG)

    t0 = time.time()
    ok = False
    while time.time() - t0 < args.max_minutes * 60:
        if SHOT_PNG.exists() and SHOT_PNG.stat().st_size > 10000:
            ok = True
            break
        state = SHOT_STATE.read_text().strip() if SHOT_STATE.exists() else "-"
        print(f"[wait] {int(time.time()-t0):4d}s  {state}")
        time.sleep(5)

    time.sleep(2)
    if editor.poll() is None:
        editor.terminate()
        try:
            editor.wait(timeout=30)
        except subprocess.TimeoutExpired:
            editor.kill()
    SHOT_FLAG.unlink(missing_ok=True)
    if not ok:
        sys.exit("FAIL: no screenshot produced")
    print("[shot] DONE:", SHOT_PNG)


if __name__ == "__main__":
    main()
