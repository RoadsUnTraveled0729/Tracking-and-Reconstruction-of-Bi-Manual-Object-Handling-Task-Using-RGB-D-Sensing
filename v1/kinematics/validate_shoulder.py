"""Validate the right-shoulder swing-twist solve (KINEMATIC_MODEL.md §6).

A. Known poses with hand-derived expected angles (incl. gimbal + straight
   elbow behavior).
B. Numeric refutation of the thesis-draft twist formula (12->16 projected
   onto the ZX plane): it cannot even distinguish twist +90 from -90 deg.
C. Both synthetic datasets (shoulder_only, shoulder_torso) decoded through
   the FULL pipeline (sensor CSV -> Unity -> root frame -> shoulder solve)
   against ground truth.

Run: python validate_shoulder.py  (regenerates output/ datasets if missing)
"""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from root_frame import build_root_frame, euler_unity_zxy, unity_from_sensor, wrap_deg
from shoulder import (recompose_shoulder, solve_left_arm, solve_right_arm,
                      solve_right_shoulder, _rx, _ry, _rz)

HERE = Path(__file__).resolve().parent
OUT = HERE / "output"
L_UA, L_FA = 0.31, 0.28
X, Z = np.array([1.0, 0, 0]), np.array([0, 0, 1.0])
FAILURES = []


def check(label, got, expected, tol=1e-9):
    got, expected = np.asarray(got, float), np.asarray(expected, float)
    err = np.nanmax(np.abs(wrap_deg(got - expected)))
    ok = err <= tol
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}: got {np.round(got, 6)} "
          f"expected {np.round(expected, 6)} (max err {err:.2e} deg)")
    if not ok:
        FAILURES.append(label)


def make_pose(ty, tz, tw, ey=-90.0, ez=0.0,
              R_root=np.diag([-1.0, 1.0, -1.0])):
    """Build Unity-space p12/p14/p16 for given joint angles under R_root."""
    p12_local = np.array([0.19, 0.50, 0.0])
    R_swing = _ry(np.radians(ty)) @ _rz(np.radians(tz))
    R_sh = recompose_shoulder((ty, tz, tw))
    R_elb = _ry(np.radians(ey)) @ _rz(np.radians(ez))
    p14_local = p12_local + L_UA * (R_swing @ X)
    p16_local = p14_local + L_FA * (R_sh @ (R_elb @ X))
    return (R_root @ p12_local, R_root @ p14_local, R_root @ p16_local)


def part_a():
    print("A. Known poses (torso at reference (0,180,0))")
    R_root = np.diag([-1.0, 1.0, -1.0])   # person upright facing the sensor

    for label, truth in [
        ("rest T-pose, elbow forward           ", (0.0, 0.0, 0.0)),
        ("arm forward horizontal               ", (-90.0, 0.0, 0.0)),
        ("arm 30 deg up                        ", (0.0, 30.0, 0.0)),
        ("internal rotation 90 (forearm down)  ", (0.0, 0.0, 90.0)),
        ("external rotation 90 (forearm up)    ", (0.0, 0.0, -90.0)),
        ("combined (35, -25, 50)               ", (35.0, -25.0, 50.0)),
    ]:
        ang, ok = solve_right_shoulder(*make_pose(*truth), R_root)
        assert ok, label
        check(label.strip(), ang, truth)

    # Gimbal: arm straight up, generated with theta_y = 30. Azimuth is
    # unobservable; convention theta_y := 0 and the axial 30 deg must fold
    # into the twist.
    ang, ok = solve_right_shoulder(*make_pose(30.0, 90.0, 0.0), R_root)
    assert ok
    check("gimbal arm-up: y folds into twist", ang, (0.0, 90.0, 30.0))

    # Straight elbow: forearm parallel to the arm axis -> twist must be
    # flagged unobservable, swing still exact.
    p12, p14, _ = make_pose(20.0, 10.0, 0.0)
    p16 = p14 + (p14 - p12) * (L_FA / L_UA)
    ang, ok = solve_right_shoulder(p12, p14, p16, R_root)
    flagged = (not ok) and np.isnan(ang[2])
    print(f"  [{'PASS' if flagged else 'FAIL'}] straight elbow: twist "
          f"flagged unobservable (twist_ok={ok}, twist={ang[2]})")
    if ok or not np.isnan(ang[2]):
        FAILURES.append("straight elbow flag")
    check("straight elbow: swing still exact", ang[:2], (20.0, 10.0))


def part_b():
    print("\nB. Draft twist formula refutation (12->16 onto ZX plane)")
    R_root = np.diag([-1.0, 1.0, -1.0])
    print("  pose: arm at rest (out to the right), elbow 90 deg; only the")
    print("  true twist changes. Draft: atan2(w_x, w_z), w = local(p16-p12).")
    rows = []
    for tw in (0.0, 90.0, -90.0):
        p12, p14, p16 = make_pose(0.0, 0.0, tw)
        w = R_root.T @ (p16 - p12)
        draft = np.degrees(np.arctan2(w[0], w[2]))
        ang, _ = solve_right_shoulder(p12, p14, p16, R_root)
        rows.append((tw, draft, ang[2]))
        print(f"    true twist {tw:+6.1f}  ->  draft {draft:+8.3f}   "
              f"correct {ang[2]:+8.3f}")
    same = abs(rows[1][1] - rows[2][1]) < 1e-9
    print(f"  [{'PASS' if same else 'FAIL'}] draft gives the SAME value for "
          f"+90 and -90 deg twist ({rows[1][1]:.3f}) -> direction of axial")
    print("         rotation is invisible in a plane containing the axis.")
    if not same:
        FAILURES.append("draft refutation")


def part_c():
    print("\nC. Full-pipeline decode vs ground truth on all datasets")
    if not (OUT / "arm_both_landmarks.csv").exists():
        subprocess.run([sys.executable,
                        str(HERE / "make_synthetic_shoulder_motion.py")],
                       check=True)
    for name in ("shoulder_only", "shoulder_torso", "elbow_only",
                 "arm_full", "arm_both"):
        lm = pd.read_csv(OUT / f"{name}_landmarks.csv")
        tr = pd.read_csv(OUT / f"{name}_truth.csv")
        errs_sh, errs_root, errs_el, errs_l = [], [], [], []
        for i in range(len(lm)):
            row = lm.iloc[i]
            p = {k: unity_from_sensor([row[f"{k}_x"], row[f"{k}_y"], row[f"{k}_z"]])
                 for k in ("left_hip", "right_hip", "right_shoulder",
                           "right_elbow", "right_wrist", "left_shoulder",
                           "left_elbow", "left_wrist")}
            R_root = build_root_frame(p["left_hip"], p["right_hip"],
                                      p["right_shoulder"])
            e_root = euler_unity_zxy(R_root)
            sh, el, ok = solve_right_arm(p["right_shoulder"],
                                         p["right_elbow"],
                                         p["right_wrist"], R_root)
            lsh, lel, _ = solve_left_arm(p["left_shoulder"],
                                         p["left_elbow"],
                                         p["left_wrist"], R_root)
            assert ok, f"{name} frame {i}: twist unexpectedly unobservable"
            t = tr.iloc[i]
            errs_root.append(np.abs(wrap_deg(
                e_root - np.array([t.root_x, t.root_y, t.root_z]))))
            errs_sh.append(np.abs(wrap_deg(
                sh - np.array([t.sh_y, t.sh_z, t.sh_twist]))))
            errs_el.append(np.abs(wrap_deg(
                el - np.array([t.elbow_y, t.elbow_z]))))
            errs_l.append(np.abs(wrap_deg(
                np.r_[lsh, lel] - np.array([t.l_sh_y, t.l_sh_z, t.l_sh_twist,
                                            t.l_elbow_y, t.l_elbow_z]))))
        e_r, e_s = np.max(errs_root), np.max(errs_sh)
        e_e, e_l = np.max(errs_el), np.max(errs_l)
        ok = e_r < 1e-9 and e_s < 1e-9 and e_e < 1e-9 and e_l < 1e-9
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {len(lm)} frames, "
              f"max err root {e_r:.3e} / R shoulder {e_s:.3e} / "
              f"R elbow {e_e:.3e} / LEFT arm {e_l:.3e} deg")
        if not ok:
            FAILURES.append(name)


def part_d():
    print("\nD. Elbow swing (§7): known poses + ez-redundancy")
    R_root = np.diag([-1.0, 1.0, -1.0])
    for label, args, exp_sh, exp_el in [
        ("straight arm (ey=0): twist:=0, elbow 0", (0, 0, 0, 0.0), (0, 0, 0), (0, 0)),
        ("elbow right angle (rest pose)          ", (0, 0, 0, -90.0), (0, 0, 0), (-90, 0)),
        ("elbow -45 with twist 30                ", (0, 0, 30, -45.0), (0, 0, 30), (-45, 0)),
        ("full combo (35,-25,50) elbow -120      ", (35, -25, 50, -120.0), (35, -25, 50), (-120, 0)),
    ]:
        ty, tz, tw, ey = args
        sh, el, _ = solve_right_arm(*make_pose(ty, tz, tw, ey=ey), R_root)
        check(label.strip() + " [shoulder]", sh, exp_sh)
        check(label.strip() + " [elbow]", el, exp_el)

    # Redundancy: injecting ez=30 at zero twist must decode as twist -30
    # with ez=0 - the SAME physical forearm direction, re-attributed.
    p12, p14, p16 = make_pose(0, 0, 0, ey=-90.0, ez=30.0)
    sh, el, _ = solve_right_arm(p12, p14, p16, R_root)
    check("injected ez=30 re-attributed to twist", np.r_[sh, el],
          (0.0, 0.0, -30.0, -90.0, 0.0))
    # and the recomposed forearm direction is identical either way
    d_inj = recompose_shoulder((0, 0, 0)) @ (
        _ry(np.radians(-90.0)) @ _rz(np.radians(30.0)) @ X)
    d_dec = recompose_shoulder(sh) @ (
        _ry(np.radians(el[0])) @ _rz(np.radians(el[1])) @ X)
    err = np.max(np.abs(d_inj - d_dec))
    print(f"  [{'PASS' if err < 1e-12 else 'FAIL'}] same forearm direction "
          f"both parameterizations (max diff {err:.2e})")
    if err >= 1e-12:
        FAILURES.append("ez redundancy direction")


def make_left_pose(ty, tz, tw, ey=-90.0, R_root=np.diag([-1.0, 1.0, -1.0])):
    """Left-arm points from mirror-convention angles: world chain
    Ry(-θy)·Rz(-θz)·Rx(θτ)·Ry(-ey), rest arm -x̂ (§9)."""
    p11 = np.array([-0.19, 0.50, 0.0])
    R_sw = _ry(np.radians(-ty)) @ _rz(np.radians(-tz))
    p13 = p11 + L_UA * (R_sw @ -X)
    R_full = R_sw @ _rx(np.radians(tw)) @ _ry(np.radians(-ey))
    p15 = p13 + L_FA * (R_full @ -X)
    return (R_root @ p11, R_root @ p13, R_root @ p15)


def part_e():
    print("\nE. LEFT arm via sagittal mirror (§9)")
    R_root = np.diag([-1.0, 1.0, -1.0])
    for label, args in [
        ("rest T-pose, elbow forward     ", (0, 0, 0, -90.0)),
        ("arm forward horizontal          ", (-90, 0, 0, -90.0)),
        ("arm 30 deg up                   ", (0, 30, 0, -90.0)),
        ("internal rotation 90            ", (0, 0, 90, -90.0)),
        ("straight arm                    ", (0, 0, 0, 0.0)),
        ("asymmetric combo (35,-25,50,-120)", (35, -25, 50, -120.0)),
    ]:
        ty, tz, tw, ey = args
        sh, el, _ = solve_left_arm(*make_left_pose(ty, tz, tw, ey), R_root)
        check("L " + label.strip(), np.r_[sh, el], (ty, tz, tw, ey, 0.0))

    # mirror-symmetry: physically mirrored right/left poses must decode to
    # the SAME angle numbers
    args = (25.0, -40.0, 35.0, -75.0)
    rsh, rel, _ = solve_right_arm(*make_pose(args[0], args[1], args[2],
                                             ey=args[3]), R_root)
    lsh, lel, _ = solve_left_arm(*make_left_pose(*args), R_root)
    check("mirror pair decodes identically", np.r_[lsh, lel], np.r_[rsh, rel])


def main():
    part_a()
    part_b()
    part_d()
    part_e()
    part_c()
    print(f"\n{'ALL PASS' if not FAILURES else 'FAILURES: ' + str(FAILURES)}")
    sys.exit(1 if FAILURES else 0)


if __name__ == "__main__":
    main()
