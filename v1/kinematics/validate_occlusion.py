"""Validate the blocked-landmark chain fallback (KINEMATIC_MODEL.md §10).

Truth = the unmasked solve of the same verified recording, so every check
is exact:

  1. Coverage: every scenario yields output on ALL frames (the old policy
     dropped whole frames on any missing landmark).
  2. Mask correctness: the per-joint live mask matches the §10 landmark
     requirements exactly, inside and outside the masked window.
  3. Live joints stay EXACT: identical inputs -> identical angles (<=1e-9
     deg vs truth; joints solved against a held/alternate root are checked
     exactly against an independent recomputation instead).
  4. Held joints: constant at the last pre-window value; drift vs truth is
     reported (it equals the true motion during the gap, not an error).
  5. Recovery: every frame after the window matches truth exactly.
  6. wrist_short: a 3-frame gap in the RAW csv is repaired by the filter
     (flag 2), no joint holds, angles near truth.
  7. Gate consistency (low-vis unit check, v2 raw csv): _src==1 cells have
     empty xyz and vis < 0.5; _src==0 cells have xyz and vis >= 0.5.

Run after make_masked_dataset.py:
  python validate_occlusion.py [--manifest output/occlusion/scenarios.json]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from occlusion import (BIT_L_ELBOW, BIT_L_SWING, BIT_L_TWIST, BIT_R_ELBOW,
                       BIT_R_SWING, BIT_R_TWIST, BIT_ROOT, MASK_ALL,
                       ChainFallbackSolver)
from root_frame import build_root_frame, unity_from_sensor, wrap_deg
from send_arm_angles import compute_angles
from shoulder import solve_left_arm, solve_right_arm

JOINTS = {  # name -> (mask bit, indices into the 13-angle vector)
    "root": (BIT_ROOT, [0, 1, 2]),
    "R_swing": (BIT_R_SWING, [3, 4]),
    "R_twist": (BIT_R_TWIST, [5]),
    "R_elbow": (BIT_R_ELBOW, [6, 7]),
    "L_swing": (BIT_L_SWING, [8, 9]),
    "L_twist": (BIT_L_TWIST, [10]),
    "L_elbow": (BIT_L_ELBOW, [11, 12]),
}
EXACT = 1e-9  # deg; identical inputs must give identical angles

# scenario -> joints expected to HOLD inside the window
EXPECT_HELD = {
    "wrist_long": {"R_twist", "R_elbow"},
    "elbow_long": {"R_swing", "R_twist", "R_elbow"},
    "hip": {"root"},
    "root_ref": {"R_swing", "R_twist", "R_elbow"},
    "pose_loss": set(JOINTS),
}

npass = nfail = 0


def check(label, ok, detail=""):
    global npass, nfail
    npass, nfail = npass + ok, nfail + (not ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}{': ' + detail if detail else ''}")


def angles_by_frame(csv_path):
    return {r[0]: (np.array(r[2:15]), r[15]) for r in compute_angles(csv_path)}


def landmark_points(csv_path):
    """frame -> {name: unity xyz} straight from the csv (NaN kept)."""
    df = pd.read_csv(csv_path)
    names = ["left_hip", "right_hip", "left_shoulder", "right_shoulder",
             "left_elbow", "right_elbow", "left_wrist", "right_wrist"]
    return {int(r["frame"]): {k: unity_from_sensor(
        [r[f"{k}_x"], r[f"{k}_y"], r[f"{k}_z"]]) for k in names}
        for _, r in df.iterrows()}


def diff_deg(a, b):
    return np.max(np.abs(wrap_deg(np.asarray(a) - np.asarray(b))))


def check_scenario(name, sc, truth, base_points):
    start, stop = sc["start"], sc["stop"]
    print(f"\n=== {name}: {sc['landmarks'] if len(sc['landmarks']) < 8 else 'ALL'} "
          f"masked, frames {start}-{stop - 1} ===")
    got = angles_by_frame(sc["csv"])
    held_names = EXPECT_HELD[name]

    check("coverage: output on every frame", set(got) == set(truth),
          f"{len(got)}/{len(truth)}")

    # 2. masks
    mask_ok = True
    for fr, (_, m) in got.items():
        tm = truth[fr][1]
        exp = tm & ~sum(JOINTS[j][0] for j in held_names) \
            if start <= fr < stop else tm
        if m != exp:
            mask_ok = False
            print(f"    frame {fr}: mask {m} expected {exp}")
            break
    check("live mask matches §10 requirements on every frame", mask_ok)

    # 3-4. inside the window
    live_err = 0.0
    hold_ok = True
    drift = {j: 0.0 for j in held_names}
    hold_ref = {j: truth[start - 1][0][JOINTS[j][1]] for j in held_names} \
        if start > 0 else {}
    for fr in range(start, stop):
        gv = got[fr][0]
        tv = truth[fr][0]
        for j, (_, idx) in JOINTS.items():
            if j in held_names:
                if diff_deg(gv[idx], hold_ref[j]) > EXACT:
                    hold_ok = False
                drift[j] = max(drift[j], diff_deg(tv[idx], hold_ref[j]))
            elif name not in ("hip", "root_ref"):
                live_err = max(live_err, diff_deg(gv[idx], tv[idx]))
    if name not in ("hip", "root_ref"):
        check("live joints exact vs truth inside window", live_err <= EXACT,
              f"max {live_err:.2e} deg")
    check("held joints constant at last pre-window value", hold_ok)
    for j in sorted(held_names):
        print(f"    held {j}: true motion during gap (drift) "
              f"{drift[j]:.1f} deg")

    # scenario-specific: joints solved against a held/alternate root must
    # equal an independent recomputation with that root.
    if name == "hip":
        solver = ChainFallbackSolver()
        err = 0.0
        for fr in range(start):  # replay to get the held root state
            p = {k: v for k, v in base_points[fr].items()}
            solver.solve(p)
        R_held = solver.R_root.copy()
        for fr in range(start, stop):
            p = base_points[fr]
            sh, el, _ = solve_right_arm(p["right_shoulder"], p["right_elbow"],
                                        p["right_wrist"], R_held)
            lsh, lel, _ = solve_left_arm(p["left_shoulder"], p["left_elbow"],
                                         p["left_wrist"], R_held)
            exp = np.concatenate([sh, el, lsh, lel])
            err = max(err, diff_deg(got[fr][0][3:], exp))
        check("arms live against the HELD root (independent recompute)",
              err <= EXACT, f"max {err:.2e} deg")
    if name == "root_ref":
        err = 0.0
        dev = 0.0
        for fr in range(start, stop):
            p = base_points[fr]
            R_alt = build_root_frame(p["left_hip"], p["right_hip"],
                                     p["left_shoulder"])
            lsh, lel, _ = solve_left_arm(p["left_shoulder"], p["left_elbow"],
                                         p["left_wrist"], R_alt)
            exp = np.concatenate([lsh, lel])
            err = max(err, diff_deg(got[fr][0][8:], exp))
            dev = max(dev, diff_deg(got[fr][0][:3], truth[fr][0][:3]))
        check("root live via LEFT shoulder + left arm exact against it",
              err <= EXACT, f"max {err:.2e} deg")
        check("either-shoulder root deviation small (shoulder-line component "
              "discarded by the cross)", dev < 5.0, f"max {dev:.2f} deg")

    # 5. recovery
    rec_err = max(diff_deg(got[fr][0], truth[fr][0])
                  for fr in range(stop, max(truth) + 1))
    check("recovery: all frames after the window exact vs truth",
          rec_err <= EXACT, f"max {rec_err:.2e} deg")


def check_wrist_short(sc, truth, base_filtered, script_dir):
    start, stop = sc["start"], sc["stop"]
    print(f"\n=== wrist_short: R wrist masked in RAW, frames "
          f"{start}-{stop - 1} -> filter repairs ===")
    refiltered = Path(sc["csv"]).with_name("masked_wrist_short_filtered.csv")
    r = subprocess.run([sys.executable,
                        str(script_dir.parent / "mediapipe" / "filter_landmarks.py"),
                        "--csv", sc["csv"], "--out", str(refiltered)],
                       capture_output=True, text=True)
    check("filter run", r.returncode == 0, r.stderr.strip()[-200:] if r.returncode else "")
    df = pd.read_csv(refiltered)
    win = df[(df["frame"] >= start) & (df["frame"] < stop)]
    check("masked frames repaired as flag 2 (missing interpolated)",
          (win["right_wrist_flag"] == 2).all())
    base = pd.read_csv(base_filtered)
    bwin = base[(base["frame"] >= start) & (base["frame"] < stop)]
    dmm = 1000 * np.linalg.norm(
        win[["right_wrist_x", "right_wrist_y", "right_wrist_z"]].to_numpy(float)
        - bwin[["right_wrist_x", "right_wrist_y", "right_wrist_z"]].to_numpy(float),
        axis=1).max()
    check("interpolated wrist within 10 mm of the unmasked filtered wrist",
          dmm < 10.0, f"max {dmm:.2f} mm")
    got = angles_by_frame(str(refiltered))
    mask_ok = all(got[fr][1] == truth[fr][1] for fr in range(start, stop))
    check("no joint holds (gap fully repaired before the solver)", mask_ok)
    aerr = max(diff_deg(got[fr][0], truth[fr][0]) for fr in range(start, stop))
    check("window angles near truth (interpolation error only)", aerr < 2.0,
          f"max {aerr:.2f} deg")


def check_gate_consistency(v2_raw):
    print(f"\n=== low-vis gate consistency on {Path(v2_raw).name} ===")
    df = pd.read_csv(v2_raw)
    df = df[df["has_pose"] == 1]
    ok_gate = ok_present = True
    n_lv = 0
    for name in ["left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
                 "left_wrist", "right_wrist", "left_hip", "right_hip"]:
        src = pd.to_numeric(df[f"{name}_src"], errors="coerce")
        vis = df[f"{name}_vis"].to_numpy(float)
        has_xyz = df[[f"{name}_x", f"{name}_y", f"{name}_z"]].notna().all(axis=1).to_numpy()
        lv = (src == 1).to_numpy()
        n_lv += int(lv.sum())
        ok_gate &= bool((~has_xyz[lv]).all() and (vis[lv] < 0.5).all())
        ok0 = (src == 0).to_numpy()
        ok_present &= bool(has_xyz[ok0].all() and (vis[ok0] >= 0.5).all())
    check("every _src=1 cell: xyz empty AND vis < 0.5", ok_gate, f"{n_lv} cells")
    check("every _src=0 cell: xyz present AND vis >= 0.5", ok_present)


def main():
    here = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path,
                    default=here / "output" / "occlusion" / "scenarios.json")
    ap.add_argument("--v2-raw", type=Path, default=here.parent / "mediapipe" /
                    "output" / "recording_20260224_083945_landmarks_raw_v2.csv")
    args = ap.parse_args()
    with open(args.manifest) as f:
        manifest = json.load(f)

    print(f"truth: unmasked solve of {Path(manifest['base_filtered']).name}")
    truth = angles_by_frame(manifest["base_filtered"])
    base_points = landmark_points(manifest["base_filtered"])

    for name, sc in manifest["scenarios"].items():
        if name == "wrist_short":
            check_wrist_short(sc, truth, manifest["base_filtered"], here)
        else:
            check_scenario(name, sc, truth, base_points)

    if args.v2_raw.exists():
        check_gate_consistency(args.v2_raw)

    print(f"\n{'ALL PASS' if nfail == 0 else 'FAILURES PRESENT'} "
          f"({npass} checks, {nfail} failed)")
    sys.exit(1 if nfail else 0)


if __name__ == "__main__":
    main()
