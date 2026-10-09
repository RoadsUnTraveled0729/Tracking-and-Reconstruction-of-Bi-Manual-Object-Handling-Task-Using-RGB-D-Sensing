"""Validate the universal robust chain layer (occlusion_ext.py).

Check families:
1. Baseline equivalence: with gating and recovery disabled, angles
   and mask are bit-identical to ChainFallbackSolver over the pinned
   R1 filtered recording.
2. Clean-data neutrality: root + right-arm output equals the baseline
   on every frame where no right-side landmark was gated or
   recovered (R1's right side is clean apart from a few MediaPipe
   warm-up frames whose forearm reads 0.26-0.34 m; the left wrist is
   genuinely noisy and left-side gating there is the feature
   working).
3. Segment-gate unit: a wrist teleported onto the elbow (depth
   collapse) is gated, recovered on the sphere with CONSTRAINED tags
   and clear bits, and clean data restores MEASURED.
4. R1 masked scenarios - every chain level:
   - wrist_long  (wrist gap)    : sphere recovery beats hold
   - elbow_long  (elbow gap)    : elbow recovered from the shoulder,
                                  chain re-solves; beats hold
   - hip         (one hip gap)  : hip recovered from the other hip
                                  along the hip line; ROOT keeps
                                  solving; beats hold
   - root_ref    (shoulder gap) : shoulder recovered from the other
                                  shoulder; root + arm keep solving;
                                  beats hold
   - pose_loss   (all gone)     : nothing to anchor -> identical to
                                  hold (outside gated frames)
   Recovered groups must be honest: live bits clear, tags
   CONSTRAINED, and exact re-lock after each window.
7. Object-conditioned recovery (E-014): an empty obj input is inert;
   a masked wrist placed from a true object estimate reproduces the
   measured angles exactly; a masked elbow+wrist recovers near-true
   by two-link IK; recovery beats hold-last on a moving arm;
   out-of-reach estimates clamp finitely to a straight arm.

Run: python v1/kinematics/validate_occlusion_ext.py
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from occlusion import ChainFallbackSolver, points_from_row  # noqa: E402
from occlusion_ext import (RobustChainSolver, TAG_CONSTRAINED,  # noqa: E402
                           TAG_MEASURED)
from root_frame import unity_from_sensor  # noqa: E402

FAILURES = []
RIGHT_SIDE = ("right_shoulder", "right_elbow", "right_wrist",
              "left_hip", "right_hip")
R = list(range(0, 8))                        # root + right-arm columns


def check(name, ok, detail=""):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}"
          + (f" -- {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def wrap(a):
    return (np.asarray(a, float) + 180.0) % 360.0 - 180.0


def run(df, solver):
    n = len(df)
    angles = np.zeros((n, 13))
    masks = np.zeros(n, int)
    tags = np.zeros((n, 7), int)
    for i, (_, row) in enumerate(df.iterrows()):
        pts = {k: unity_from_sensor(v)
               for k, v in points_from_row(row).items()
               if np.all(np.isfinite(v))}
        out = solver.solve(pts)
        if len(out) == 3:
            angles[i], masks[i], tags[i] = out
        else:
            angles[i], masks[i] = out
    return angles, masks, tags


def right_affected(solver, n):
    m = np.zeros(n, bool)
    for name in RIGHT_SIDE:
        m[solver.gated_frames.get(name, [])] = True
        m[solver.recovered_frames.get(name, [])] = True
    for f in getattr(solver, "stab_frames", {}).get("right_arm", []):
        if f < n:
            m[f] = True
    return m


def off_solver():
    """Every robust feature disabled -> must equal the baseline."""
    return RobustChainSolver(gate_tol=None, horizon=0,
                             line_tol_deg=None, flex_min_deg=None,
                             rate_limit_deg=None)


def main():
    base_csv = (HERE / "dataset" / "real_20260224"
                / "recording_20260224_083945_landmarks_filtered.csv")
    df = pd.read_csv(base_csv)

    print("=== 1+2. baseline equivalence and clean-data neutrality ===")
    a0, m0, _ = run(df, ChainFallbackSolver())
    off = off_solver()
    a1, m1, _ = run(df, off)
    check("disabled robust solver is bit-identical to baseline",
          np.array_equal(a0, a1) and np.array_equal(m0, m1),
          f"max |dA| {np.max(np.abs(a0 - a1)):.2e}")
    on = RobustChainSolver()
    a2, m2, t2 = run(df, on)
    aff = right_affected(on, len(df))
    check("root + right arm equal baseline outside right-affected "
          "frames", np.allclose(a2[~aff][:, R], a0[~aff][:, R],
                                atol=1e-9),
          f"{int(aff.sum())} right-affected frames")
    check("right-side interventions are rare on clean R1 "
          "(< 3 percent)", aff.mean() < 0.03,
          f"gated {on.gated}, recovered { {k: v for k, v in on.recovered.items()} }")

    print("\n=== 3. segment-gate unit (synthetic depth collapse) ===")
    s = RobustChainSolver(
        seg_len={"forearm_L": 0.23, "forearm_R": 0.22}, horizon=10)
    base_pts = {k: unity_from_sensor(v)
                for k, v in points_from_row(df.iloc[100]).items()
                if np.all(np.isfinite(v))}
    for _ in range(5):
        s.solve(base_pts)
    bad = dict(base_pts)
    bad["right_wrist"] = bad["right_elbow"] + np.array([0.0, 0.0, 1e-4])
    _, mask_bad, tags_bad = s.solve(bad)
    check("collapsed wrist is gated", s.gated.get("right_wrist") == 1)
    check("gated wrist recovered on the sphere with CONSTRAINED tags",
          s.recovered.get("right_wrist") == 1
          and tags_bad[2] == TAG_CONSTRAINED
          and tags_bad[3] == TAG_CONSTRAINED
          and not (mask_bad & (1 << 2)) and not (mask_bad & (1 << 3)))
    good_again = s.solve(base_pts)
    check("clean wrist restores MEASURED tags",
          good_again[2][2] == TAG_MEASURED
          and good_again[2][3] == TAG_MEASURED)

    print("\n=== 4. R1 masked scenarios, every chain level ===")
    # Truth for the robust layer is its own unmasked run; assertions
    # are made on the scenario's affected groups, excluding frames
    # where a right-side intervention fired in the clean run too.
    man_file = HERE / "dataset" / "occlusion_masked" / "scenarios.json"
    man = json.loads(man_file.read_text())
    seg_len = {"forearm_L": 0.232, "forearm_R": 0.185}
    tr_solver = RobustChainSolver(seg_len=dict(seg_len))
    truth_r, _, _ = run(df, tr_solver)
    aff_clean = right_affected(tr_solver, len(df))

    # scenario -> (affected angle idx, groups expected CONSTRAINED)
    SCEN = {
        "wrist_long": ([5, 6], (2, 3)),
        "elbow_long": ([3, 4, 5, 6], (1, 2, 3)),
        "hip": ([0, 1, 2], (0,)),
        "root_ref": ([3, 4, 5, 6], (0, 1, 2, 3)),
        "pose_loss": (list(range(0, 8)), ()),
    }
    for name, (idx, groups) in SCEN.items():
        sc = man["scenarios"][name]
        mdf = pd.read_csv(man_file.parent / Path(sc["csv"]).name)
        ah, mh, _ = run(mdf, ChainFallbackSolver())
        solver = RobustChainSolver(seg_len=dict(seg_len))
        ar, mr, tr = run(mdf, solver)
        aff_m = right_affected(solver, len(ar)) | aff_clean
        win = np.zeros(len(ar), bool)
        win[sc["start"]:sc["stop"]] = True
        if groups:
            eh = np.abs(wrap(ah[win][:, idx] - a0[win][:, idx]))
            er = np.abs(wrap(ar[win][:, idx] - truth_r[win][:, idx]))
            check(f"{name}: recovery beats hold (p95)",
                  np.percentile(er, 95) < np.percentile(eh, 95),
                  f"robust {np.percentile(er, 95):.2f} deg vs hold "
                  f"{np.percentile(eh, 95):.2f} deg")
            hon = all(all(tr[f][g] == TAG_CONSTRAINED
                          and not (int(mr[f]) & (1 << g))
                          for g in groups)
                      for f in np.flatnonzero(win))
            check(f"{name}: recovered groups honest (bits clear, "
                  "tags CONSTRAINED)", hon)
        else:
            same = np.array_equal(ar[~aff_m & ~win][:, R],
                                  ah[~aff_m & ~win][:, R])
            in_win = np.array_equal(ar[win][:, R], ah[win][:, R])
            check(f"{name}: identical to hold (nothing to anchor)",
                  same and in_win)
        post = ~win & (np.arange(len(ar)) >= sc["stop"]) & ~aff_m
        derr = np.max(np.abs(wrap(ar[post][:, R] - truth_r[post][:, R]))) \
            if post.any() else 0.0
        check(f"{name}: exact right-side re-lock after the window",
              derr < 1e-9, f"max {derr:.2e} deg")

    print("\n=== 5. root line-consistency gate (synthetic hip-depth "
          "corruption) ===")
    # R4 failure mode replayed on R1: corrupt both hips' DEPTH in
    # opposite directions, pixel-preserving (a wrong depth sample
    # moves the 3D point along its camera ray - the pixel stays
    # true; scaling the whole camera-frame point by (z+dz)/z models
    # exactly that), rotating the hip line ~30-50 deg against the
    # shoulder line while the width stays within the width gate.
    W0, W1 = 300, 420
    cdf = df.copy()
    for i in range(W0, W1):
        for lm_name, dz in (("left_hip", 0.10), ("right_hip", -0.10)):
            z = cdf.loc[cdf.index[i], f"{lm_name}_z"]
            s = (z + dz) / z
            for ax in ("x", "y", "z"):
                cdf.loc[cdf.index[i], f"{lm_name}_{ax}"] *= s
    ah, _, _ = run(cdf, ChainFallbackSolver())
    solver = RobustChainSolver(seg_len=dict(seg_len))
    ar, mr, tr = run(cdf, solver)
    win = np.zeros(len(ar), bool)
    win[W0:W1] = True
    fired = sum(1 for f in solver.gated_frames.get("left_hip", [])
                if W0 <= f < W1)
    check("line gate fires inside the corruption window",
          fired > 0.9 * (W1 - W0), f"{fired}/{W1 - W0} frames")
    eh = np.abs(wrap(ah[win][:, [0, 1, 2]] - a0[win][:, [0, 1, 2]]))
    er = np.abs(wrap(ar[win][:, [0, 1, 2]] - truth_r[win][:, [0, 1, 2]]))
    check("line recovery beats trusting corrupt hips (root p95)",
          np.percentile(er, 95) < 0.5 * np.percentile(eh, 95),
          f"robust {np.percentile(er, 95):.2f} deg vs corrupt "
          f"{np.percentile(eh, 95):.2f} deg")
    check("ray repair keeps the root within 10 deg p95 under depth "
          "corruption (E-011b)", np.percentile(er, 95) < 10.0,
          f"root p95 {np.percentile(er, 95):.2f} deg, ray repairs "
          f"{solver.ray_fixed} (position from rays; orientation "
          "through the EMA, which lags the genuine rotation in this "
          "window - the deliberate wobble-vs-lag trade)")
    rec = [f for f in solver.recovered_frames.get("left_hip", [])
           if W0 <= f < W1]
    hon = all(tr[f][0] == TAG_CONSTRAINED and not (int(mr[f]) & 1)
              for f in rec)
    check("line-recovered root honest (bit clear, tag CONSTRAINED)",
          hon and len(rec) > 0, f"{len(rec)} recovered frames")
    post = ~win & (np.arange(len(ar)) >= W1) \
        & ~right_affected(solver, len(ar)) & ~aff_clean
    derr = np.max(np.abs(wrap(ar[post][:, R] - truth_r[post][:, R]))) \
        if post.any() else 0.0
    check("exact right-side re-lock after the corruption",
          derr < 1e-9, f"max {derr:.2e} deg")

    print("\n=== 5b. line gate, shoulder-side corruption (R4 34.5-36 s "
          "mode) ===")
    W0, W1 = 500, 620
    cdf = df.copy()
    for i in range(W0, W1):
        for lm_name, dz in (("left_shoulder", 0.10),
                            ("right_shoulder", -0.10)):
            z = cdf.loc[cdf.index[i], f"{lm_name}_z"]
            s = (z + dz) / z
            for ax in ("x", "y", "z"):
                cdf.loc[cdf.index[i], f"{lm_name}_{ax}"] *= s
    ah, _, _ = run(cdf, ChainFallbackSolver())
    solver = RobustChainSolver(seg_len=dict(seg_len))
    ar, mr, tr = run(cdf, solver)
    win = np.zeros(len(ar), bool)
    win[W0:W1] = True
    fired = sum(1 for f in solver.gated_frames.get("left_shoulder", [])
                if W0 <= f < W1)
    hips_spared = sum(1 for f in solver.gated_frames.get("left_hip", [])
                      if W0 <= f < W1)
    check("shoulder line blamed, hips spared",
          fired > 0.9 * (W1 - W0) and hips_spared == 0,
          f"shoulders {fired}/{W1 - W0}, hips {hips_spared}")
    idx = [0, 1, 2, 3, 4, 8, 9]
    eh = np.abs(wrap(ah[win][:, idx] - a0[win][:, idx]))
    er = np.abs(wrap(ar[win][:, idx] - truth_r[win][:, idx]))
    check("shoulder-line recovery beats trusting corrupt shoulders "
          "(p95)", np.percentile(er, 95) < 0.7 * np.percentile(eh, 95),
          f"robust {np.percentile(er, 95):.2f} deg vs corrupt "
          f"{np.percentile(eh, 95):.2f} deg")
    rec = [f for f in solver.recovered_frames.get("left_shoulder", [])
           if W0 <= f < W1]
    hon = all(tr[f][g] == TAG_CONSTRAINED and not (int(mr[f]) & (1 << g))
              for f in rec for g in (0, 1, 4))
    check("shoulder-line recovery honest (root + both swings "
          "CONSTRAINED)", hon and len(rec) > 0,
          f"{len(rec)} recovered frames")

    print("\n=== 6. angle-parameter stabilization (E-012) ===")
    lh = np.array([-0.12, 0.0, 0.0])
    rh = np.array([0.12, 0.0, 0.0])
    ls = np.array([-0.18, 0.5, 0.0])
    rs = np.array([0.18, 0.5, 0.0])

    def right_arm_pose(flex_deg, tau_deg):
        fx, tu = np.radians(flex_deg), np.radians(tau_deg)
        elb = rs + 0.27 * np.array([1.0, 0.0, 0.0])
        fdir = (np.cos(fx) * np.array([1.0, 0, 0])
                + np.sin(fx) * (-np.sin(tu) * np.array([0, 1.0, 0])
                                + np.cos(tu) * np.array([0, 0, 1.0])))
        return {"left_hip": lh, "right_hip": rh, "left_shoulder": ls,
                "right_shoulder": rs, "right_elbow": elb,
                "right_wrist": elb + 0.22 * fdir}

    s = RobustChainSolver()
    for _ in range(5):
        out = s.solve(right_arm_pose(40.0, 0.0))
    tau0 = out[0][5]
    held_ok = True
    for phi in (0.0, 60.0, 140.0, -120.0, 90.0):
        a, m, tg = s.solve(right_arm_pose(10.0, phi))
        held_ok &= (abs(a[5] - tau0) < 1e-9 and not (m & (1 << 2))
                    and tg[2] == 1)
    check("twist held below flex_min (bit clear, tag HELD, value "
          "constant under wild raw twist)", held_ok,
          f"stabilized {s.stabilized}")
    a, m, tg = s.solve(right_arm_pose(40.0, 30.0))
    mid_ok = (abs(a[5] - 15.0) < 1.0 and not (m & (1 << 2))
              and tg[2] == 2)
    a, m, _ = s.solve(right_arm_pose(40.0, 30.0))
    check("twist re-lock slews to the measured value (honest "
          "CONSTRAINED during catch-up, live once converged)",
          mid_ok and abs(a[5] - 30.0) < 1.0 and bool(m & (1 << 2)),
          f"tau -> {a[5]:.2f}")

    s = RobustChainSolver()
    for _ in range(3):
        out = s.solve(right_arm_pose(40.0, 0.0))

    def hanging_pose(phi_deg, flex_deg=20.0):
        phi, fx = np.radians(phi_deg), np.radians(flex_deg)
        ed = np.array([0.05 * np.cos(phi), -1.0, 0.05 * np.sin(phi)])
        elb = rs + 0.27 * ed / np.linalg.norm(ed)
        fdir = np.array([np.sin(fx) * np.cos(phi), -np.cos(fx),
                         np.sin(fx) * np.sin(phi)])
        return {"left_hip": lh, "right_hip": rh, "left_shoulder": ls,
                "right_shoulder": rs, "right_elbow": elb,
                "right_wrist": elb + 0.22 * fdir / np.linalg.norm(fdir)}

    for _ in range(8):        # let the slew limiter walk theta_z down
        a_prev, _, _ = s.solve(hanging_pose(0.0))
    ok = True
    for phi in (70.0, 160.0, -110.0):
        a, m, tg = s.solve(hanging_pose(phi))
        step = abs(wrap(a[3] - a_prev[3]))
        ok &= step <= 15.0 + 1e-6
        if step > 14.0:               # actively clamping -> demoted
            ok &= not (m & (1 << 1)) and tg[1] == 2
        a_prev = a
    check("vertical-arm azimuth flips slew-bounded (<= 15 deg/frame, "
          "demoted while clamping)", ok,
          f"theta_z {a[4]:.1f} deg, stabilized {s.stabilized}")

    s = RobustChainSolver()
    for _ in range(3):
        s.solve(right_arm_pose(40.0, 0.0))
    a, m, tg = s.solve(right_arm_pose(40.0, 25.0))
    step1, demoted = a[5], (not (m & (1 << 2)) and tg[2] == 2)
    a, m, _ = s.solve(right_arm_pose(40.0, 25.0))
    check("slew limit clamps a 25 deg twist jump to 15 (demoted) "
          "then converges (live)", abs(step1 - 15.0) < 1.0 and demoted
          and abs(a[5] - 25.0) < 1.0 and bool(m & (1 << 2)),
          f"steps {step1:.1f} -> {a[5]:.1f}")

    print("\n=== 6b. hip hold (E-034, opt-in) ===")
    # the section-6 fixture sits at camera depth 0, where no camera ray
    # exists; the hip repairs act on rays, so this block moves the same
    # body 1 m in front of the camera
    # pair widths are given so the torso line gate can act on the whole
    # pair from the first frame (it otherwise waits for 60 calibration
    # samples); the diagonals stay uncalibrated, so no single hip is blamed
    SEG_T = {"upper_arm_R": 0.27, "forearm_R": 0.22,
             "upper_arm_L": 0.27, "forearm_L": 0.22,
             "hip_width": 0.24, "shoulder_width": 0.36}
    OFF = np.array([0.0, 0.0, 1.0])

    def far(pose):
        return {k: v + OFF for k, v in pose.items()}

    s_off = RobustChainSolver(seg_len=dict(SEG_T))
    s_on = RobustChainSolver(seg_len=dict(SEG_T), hip_hold=True)
    clean = far(right_arm_pose(40.0, 0.0))
    for _ in range(4):
        s_off.solve(dict(clean))
        a_ref, m_ref, _ = s_on.solve(dict(clean))
    # both hips 25 cm nearer (the hand's depth) AND the hip line rolled
    # (one hip pixel up, the other down), so the ray repair (new pixel
    # rays at the remembered depth) rolls the root while the hold (the
    # last accepted points) returns the clean one: the two policies must
    # give different roots, and only the hold the clean one
    bad = dict(clean)
    bad["right_hip"] = clean["right_hip"] + np.array([0.0, 0.08, -0.25])
    bad["left_hip"] = clean["left_hip"] + np.array([0.0, -0.08, -0.25])
    a_off, m_off, tg_off = s_off.solve(dict(bad))
    a_on, m_on, tg_on = s_on.solve(dict(bad))
    held_pts = {j: s_on.last_points[j] for j in ("left_hip", "right_hip")}
    check("hip hold: both hips return to their last accepted position "
          "(exact), root CONSTRAINED, and the default layer's root differs",
          all(np.allclose(held_pts[j], clean[j]) for j in held_pts)
          and s_on.hip_held == {"left_hip": 1, "right_hip": 1}
          and not (m_on & 1) and tg_on[0] == TAG_CONSTRAINED
          and np.allclose(a_on[:3], a_ref[:3], atol=1e-9)
          and not np.allclose(a_off[:3], a_ref[:3], atol=0.5),
          f"root {a_on[:3].round(3)} vs clean {a_ref[:3].round(3)}; "
          f"default layer root {a_off[:3].round(3)} "
          f"(gated {sorted(s_off.gated)})")
    check("hip hold: the ray, occluder and line repairs left the held "
          "hips alone", s_on.ray_fixed == {} and s_on.occluder_fixed == {}
          and s_on.gated.get("left_hip", 0) == 1
          and s_on.gated.get("right_hip", 0) == 1
          and sum(s_off.ray_fixed.values()) == 2,
          f"hold counters ray_fixed {s_on.ray_fixed} occluder_fixed "
          f"{s_on.occluder_fixed}; default ray_fixed {s_off.ray_fixed}")
    a_on, m_on, tg_on = s_on.solve(dict(clean))
    check("hip hold: clean frame re-locks the root MEASURED",
          bool(m_on & 1) and tg_on[0] == TAG_MEASURED
          and np.allclose(a_on[:3], a_ref[:3], atol=1e-9))
    miss = dict(clean)
    del miss["right_hip"]
    a_on, m_on, tg_on = s_on.solve(miss)
    check("hip hold: an unreported hip is held too (root solves, "
          "CONSTRAINED)", not (m_on & 1) and tg_on[0] == TAG_CONSTRAINED
          and np.allclose(a_on[:3], a_ref[:3], atol=1e-9)
          and s_on.hip_held["right_hip"] == 2)
    # the hip LINE blamed by the torso line gate (both hips swung 35 deg
    # about the trunk axis while the shoulders stay): the whole-pair
    # rebuild is cancelled, both hips are held, and the hip direction
    # memory is not steered toward the shoulder line meanwhile
    s_on.solve(dict(clean))
    u_before = s_on.u["hip_width"].copy()
    c, sn = np.cos(np.radians(35.0)), np.sin(np.radians(35.0))
    swung = dict(clean)
    for j in ("left_hip", "right_hip"):
        x = clean[j][0]
        swung[j] = np.array([x * c, 0.0, x * sn]) + OFF
    a_on, m_on, tg_on = s_on.solve(swung)
    conds = {"held": s_on.hip_held["left_hip"] >= 2,
             "no_ray_fix": s_on.ray_fixed == {},
             "left_at_clean": np.allclose(s_on.last_points["left_hip"], clean["left_hip"]),
             "right_at_clean": np.allclose(s_on.last_points["right_hip"], clean["right_hip"]),
             "memory_kept": np.allclose(s_on.u["hip_width"], u_before),
             "root_clean": np.allclose(a_on[:3], a_ref[:3], atol=1e-9),
             "constrained": tg_on[0] == TAG_CONSTRAINED}
    check("hip hold: a line-gated hip pair is held, not rebuilt, and its "
          "line memory stays put", all(conds.values()),
          f"{conds} gated {s_on.gated} line_on {s_on._line_on}")

    print("\n=== 7. object-conditioned recovery (E-014) ===")
    SEG = {"upper_arm_R": 0.27, "forearm_R": 0.22,
           "upper_arm_L": 0.27, "forearm_L": 0.22}
    NO_OBJ = {"right": None, "left": None}

    # 7a. an empty obj input is inert on fully measured frames
    sa = RobustChainSolver(seg_len=dict(SEG))
    sb = RobustChainSolver(seg_len=dict(SEG))
    ok = True
    for flex in (40.0, 50.0, 60.0):
        oa = sa.solve(right_arm_pose(flex, 10.0))
        ob = sb.solve(right_arm_pose(flex, 10.0), obj=NO_OBJ)
        ok &= (np.array_equal(oa[0], ob[0]) and oa[1] == ob[1]
               and np.array_equal(oa[2], ob[2]))
    check("empty obj input inert on measured frames", ok)

    # 7b. masked wrist placed at the object estimate: exact angles,
    # honest demotion of the wrist-dependent groups
    s = RobustChainSolver(seg_len=dict(SEG))
    for _ in range(5):
        a_ref, m_ref, _ = s.solve(right_arm_pose(40.0, 10.0))
    full = right_arm_pose(40.0, 10.0)
    w_true = full.pop("right_wrist")
    a, m, tg = s.solve(full, obj={"right": w_true, "left": None})
    check("object wrist recovery exact when the estimate is true "
          "(bits clear, tags CONSTRAINED)",
          np.allclose(a, a_ref, atol=1e-9)
          and s.obj_recovered.get("right_wrist_obj") == 1
          and not (m & (1 << 2)) and not (m & (1 << 3))
          and tg[2] == TAG_CONSTRAINED and tg[3] == TAG_CONSTRAINED,
          f"max |dA| {np.max(np.abs(a - a_ref)):.2e}")

    # 7c. masked elbow AND wrist: two-link IK from the object wrist,
    # swivel from the upper-arm memory, near-true angles
    s = RobustChainSolver(seg_len=dict(SEG))
    for _ in range(5):
        a_ref, _, _ = s.solve(right_arm_pose(40.0, 10.0))
    full = right_arm_pose(40.0, 10.0)
    w_true = full.pop("right_wrist")
    full.pop("right_elbow")
    a, m, tg = s.solve(full, obj={"right": w_true, "left": None})
    arm_idx = [3, 4, 5, 6]
    err = np.max(np.abs(wrap(a[arm_idx] - a_ref[arm_idx])))
    check("IK elbow recovery near-true from object wrist alone "
          "(all arm groups demoted)", err < 5.0
          and s.obj_recovered.get("right_elbow_ik") == 1
          and all(tg[g] == TAG_CONSTRAINED for g in (1, 2, 3)),
          f"max arm-angle error {err:.2f} deg")

    # 7d. recovery beats hold-last while the arm keeps moving
    def masked(pose):
        q = dict(pose)
        w = q.pop("right_wrist")
        q.pop("right_elbow")
        return q, w

    sweep = [right_arm_pose(f, 5.0) for f in
             np.linspace(40.0, 100.0, 13)]
    s = RobustChainSolver(seg_len=dict(SEG))
    hold = ChainFallbackSolver()
    for pose in sweep[:3]:
        a_r, _, _ = s.solve(pose)
        hold.solve(pose)
    truth = ChainFallbackSolver()
    e_rec, e_hold = [], []
    for pose in sweep[:3]:
        truth.solve(pose)
    for pose in sweep[3:]:
        a_t, _ = truth.solve(pose)
        q, w = masked(pose)
        a_r, _, _ = s.solve(q, obj={"right": w, "left": None})
        a_h, _ = hold.solve(q)
        e_rec.append(np.max(np.abs(wrap(a_r[arm_idx] - a_t[arm_idx]))))
        e_hold.append(np.max(np.abs(wrap(a_h[arm_idx] - a_t[arm_idx]))))
    check("moving-arm recovery beats hold-last",
          max(e_rec) < 0.5 * max(e_hold),
          f"recovery max {max(e_rec):.1f} deg vs hold "
          f"{max(e_hold):.1f} deg")

    # 7d2. conditioning guard: near full extension a small outward
    # bias of the wrist estimate must NOT snap the elbow straight -
    # the fresh elbow memory takes over above 98 percent of reach
    s = RobustChainSolver(seg_len=dict(SEG))
    for _ in range(5):
        a_ref, _, _ = s.solve(right_arm_pose(20.0, 5.0))
    q = right_arm_pose(20.0, 5.0)
    w_true = q.pop("right_wrist")
    q.pop("right_elbow")
    sh_pt = q["right_shoulder"]
    d = w_true - sh_pt
    w_biased = sh_pt + d * (1.0 + 0.02 / np.linalg.norm(d))
    a, m, tg = s.solve(q, obj={"right": w_biased, "left": None})
    flex_err = abs(wrap(a[6] - a_ref[6]))
    e_ik = s._ik_elbow(sh_pt, w_biased, SEG["upper_arm_R"],
                       SEG["forearm_R"], None)
    on_axis_ik = np.linalg.norm(np.cross(e_ik - sh_pt, w_biased - sh_pt))
    check("near-extension guard: biased wrist estimate keeps flexion "
          "near truth instead of snapping straight",
          flex_err < 8.0 and on_axis_ik < 1e-9,
          f"flexion error {flex_err:.1f} deg (raw IK would have "
          f"straightened the arm)")

    # 7e. out-of-reach object wrist collapses to a straight arm,
    # finite output
    s = RobustChainSolver(seg_len=dict(SEG))
    for _ in range(5):
        s.solve(right_arm_pose(40.0, 10.0))
    q = right_arm_pose(40.0, 10.0)
    q.pop("right_wrist")
    q.pop("right_elbow")
    far = q["right_shoulder"] + np.array([1.5, 0.0, 0.0])
    a, m, tg = s.solve(q, obj={"right": far, "left": None})
    e = s._ik_elbow(q["right_shoulder"], far, 0.27, 0.22, None)
    on_axis = np.linalg.norm(
        np.cross(e - q["right_shoulder"], far - q["right_shoulder"]))
    check("out-of-reach wrist: elbow clamps onto the S-W axis, "
          "finite angles", np.all(np.isfinite(a)) and on_axis < 1e-9,
          f"axis distance {on_axis:.2e}")

    # ---- 8. E-020 elbow joint limits (torso-capsule swivel pruning) --

    # 8a. feasible prior -> limits are a no-op (identical output)
    s_off = RobustChainSolver(seg_len=dict(SEG))
    s_on = RobustChainSolver(seg_len=dict(SEG), elbow_limits=True)
    for _ in range(5):
        s_off.solve(right_arm_pose(40.0, 10.0))
        s_on.solve(right_arm_pose(40.0, 10.0))
    q = right_arm_pose(40.0, 10.0)
    q.pop("right_elbow")
    a0, m0, t0 = s_off.solve(dict(q))
    a1, m1, t1 = s_on.solve(dict(q))
    check("E-020: limits are a no-op when the prior is feasible",
          np.allclose(a0, a1) and m0 == m1
          and s_on.limit_applied == 0,
          f"max angle diff {np.max(np.abs(a0 - a1)):.2e} deg, "
          f"interventions {s_on.limit_applied}")

    # 8b. cross-body reach, no memory: the gravity prior lands the
    # elbow inside the torso capsule; limits move it to the feasible
    # arc
    torso = {"left_hip": np.array([-0.09, -0.5, 0.5]),
             "right_hip": np.array([0.09, -0.5, 0.5]),
             "left_shoulder": np.array([-0.17, 0.0, 0.5]),
             "right_shoulder": np.array([0.17, 0.0, 0.5])}
    S = torso["right_shoulder"]
    W = np.array([-0.2, -0.3, 0.55])
    s_off = RobustChainSolver(seg_len=dict(SEG))
    s_on = RobustChainSolver(seg_len=dict(SEG), elbow_limits=True)
    cap = s_on._torso_capsule(torso)
    e_prior = s_off._ik_elbow(S, W, 0.27, 0.25, None, torso)
    e_lim = s_on._ik_elbow(S, W, 0.27, 0.25, None, torso)
    check("E-020: infeasible gravity prior is moved out of the torso "
          "capsule",
          (not s_off._capsule_clear(e_prior, cap))
          and s_on._capsule_clear(e_lim, cap)
          and s_on.limit_applied == 1
          and np.linalg.norm(e_lim - e_prior) > 0.02,
          f"prior clear {s_off._capsule_clear(e_prior, cap)}, "
          f"limited clear {s_on._capsule_clear(e_lim, cap)}, "
          f"moved {np.linalg.norm(e_lim - e_prior) * 100:.1f} cm")

    # 8c. all-infeasible circle falls back to the prior unchanged
    # (test-only wide torso makes the capsule swallow the circle)
    wide = dict(torso)
    wide["left_shoulder"] = np.array([-0.5, 0.0, 0.5])
    wide["right_shoulder"] = np.array([0.5, 0.0, 0.5])
    s_on2 = RobustChainSolver(seg_len=dict(SEG), elbow_limits=True)
    e_fb = s_on2._ik_elbow(S, W, 0.27, 0.25, None, wide)
    check("E-020: an all-infeasible circle returns the prior "
          "unchanged (never reduces availability)",
          np.allclose(e_fb, e_prior) and s_on2.limit_applied == 0,
          f"fallback-prior distance "
          f"{np.linalg.norm(e_fb - e_prior):.2e} m")

    print(f"\n=== {'ALL PASS' if not FAILURES else 'FAILED'} "
          f"({len(FAILURES)} failures) ===")
    sys.exit(1 if FAILURES else 0)


if __name__ == "__main__":
    main()
