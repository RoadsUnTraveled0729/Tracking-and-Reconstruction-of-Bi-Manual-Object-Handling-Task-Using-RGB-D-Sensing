"""Synthetic-arm tests for akc.py.

Run: /home/luo/anaconda3/bin/python eval/akc_comparison/test_akc.py
(prints PASS / FAIL per check, exits 1 on any FAIL); also collectable
by pytest. Fixture constants are logged in DECISIONS.md AKC-031.
"""
import sys

sys.dont_write_bytecode = True

import copy  # noqa: E402
import math  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import akc  # noqa: E402

FAIL = []
K = akc.INTRINSICS
DT = 0.03336                       # AKC-008
L_U, L_F = 0.25, 0.23              # brief (synthetic arm)
SHOULDER = np.array([0.15, -0.10, 1.05])
OTHER_SHOULDER = np.array([-0.21, -0.10, 1.07])   # AKC-031
L_S = float(np.linalg.norm(SHOULDER - OTHER_SHOULDER))
LENGTHS = dict(l_f=L_F, l_u=L_U, l_s=L_S)


def check(name, ok):
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    if not ok:
        FAIL.append(name)


def _unit(v):
    return v / np.linalg.norm(v, axis=-1, keepdims=True)


def synth_arm(n=200, away=False):
    """Shoulder fixed; elbow and wrist on smooth curves with exact bone
    lengths; the arm reaches toward the camera (AKC-031). away=True
    mirrors the z components of both bone directions, so the arm points
    away from the camera and the true elbow and shoulder lie on the "-"
    root of the paper's relation (AKC-057)."""
    t = np.arange(n) * DT
    zs = -1.0 if away else 1.0
    u = _unit(np.stack([0.25 + 0.10 * np.sin(2 * np.pi * 0.5 * t),
                        0.45 + 0.10 * np.cos(2 * np.pi * 0.4 * t),
                        zs * (-0.85 + 0.25 * np.sin(2 * np.pi * 0.8 * t))],
                       1))
    f = _unit(np.stack([0.05 + 0.10 * np.sin(2 * np.pi * 0.7 * t),
                        -0.20 + 0.15 * np.sin(2 * np.pi * 0.6 * t),
                        zs * (-0.95 + 0.0 * t)], 1))
    S = np.tile(SHOULDER, (n, 1))
    E = S + L_U * u
    W = E + L_F * f
    return S, E, W


def _z_sep(anchor, point, length, s):
    """z separation of the two ray roots through `point` about anchor at
    length s * length; None when fewer than two roots."""
    d = point / np.linalg.norm(point)
    r = akc.ray_sphere_roots(d, anchor, s * length)
    if len(r) < 2:
        return None
    return abs((r[1] - r[0]) * d[2])


def _hand_roots(anchor, ref, uv, length, s, mode):
    """Both search-time candidates written out from the paper's relation,
    independently of akc._candidates (AKC-057): literal = x, y of the
    pixel lifted at the reference depth, z = anchor_z -/+ sqrt((s l)^2 -
    dx^2 - dy^2); ray = t d with t = b -/+ sqrt(b^2 - |c|^2 + (s l)^2),
    b = d . c. Returns [minus, plus] or None when there are not two."""
    fx, fy, cx, cy = K["fx"], K["fy"], K["cx"], K["cy"]
    lp = s * length
    a = np.asarray(anchor, float)
    if mode == "literal":
        z = float(ref[2])
        x = (uv[0] - cx) * z / fx
        y = (uv[1] - cy) * z / fy
        rad = lp * lp - (x - a[0]) ** 2 - (y - a[1]) ** 2
        if rad <= 0.0:
            return None
        q = math.sqrt(rad)
        return [np.array([x, y, a[2] - q]), np.array([x, y, a[2] + q])]
    d = np.array([(uv[0] - cx) / fx, (uv[1] - cy) / fy, 1.0])
    d = d / math.sqrt(float(d @ d))
    b = float(d @ a)
    disc = b * b - float(a @ a) + lp * lp
    if disc <= 0.0 or b - math.sqrt(disc) <= 0.0:
        return None
    return [(b - math.sqrt(disc)) * d, (b + math.sqrt(disc)) * d]


# (1) projection -----------------------------------------------------------

def test_projection():
    n0 = len(FAIL)
    rng = np.random.default_rng(0)
    worst = 0.0
    for _ in range(100):
        p = np.array([rng.uniform(-0.5, 0.5), rng.uniform(-0.4, 0.4),
                      rng.uniform(0.4, 3.0)])
        uv = akc.project(p, K)
        q = akc.deproject(uv[0], uv[1], p[2], K)
        d = akc.ray(uv[0], uv[1], K)
        worst = max(worst, float(np.linalg.norm(q - p)),
                    float(np.linalg.norm(d * np.linalg.norm(p) - p)))
    check(f"(1) project/deproject/ray round trip, max err {worst:.1e} "
          f"< 1e-9", worst < 1e-9)
    # Hand case: d = z axis, center (0.3, 0, 2), r = 0.5 -> b = 2,
    # disc = 4 - 4.09 + 0.25 = 0.16 -> t = 1.6, 2.4.
    r = akc.ray_sphere_roots([0, 0, 1], [0.3, 0, 2], 0.5)
    check("(1) ray_sphere_roots hand case [1.6, 2.4]",
          len(r) == 2 and abs(r[0] - 1.6) < 1e-12 and abs(r[1] - 2.4) < 1e-12)
    check("(1) ray_sphere_roots miss -> []",
          akc.ray_sphere_roots([0, 0, 1], [0.6, 0, 2], 0.5) == [])
    check("(1) ray_sphere_roots camera inside sphere -> one root",
          len(akc.ray_sphere_roots([0, 0, 1], [0, 0, 0.1], 0.5)) == 1)
    assert len(FAIL) == n0, FAIL[n0:]


# (2) exact recovery when only z is hidden ---------------------------------

def test_exact_recovery():
    n0 = len(FAIL)
    S, E, W = synth_arm()
    for mode in ("ray", "literal"):
        worst = 0.0
        for i in range(0, 200, 5):
            r = akc.akc_correct(W[i], E[i], S[i], akc.project(E[i], K),
                                akc.project(S[i], K), None, None, None,
                                LENGTHS, akc.W_A, mode, K)
            worst = max(worst, float(np.linalg.norm(r["e"] - E[i])),
                        float(np.linalg.norm(r["s"] - S[i])))
        check(f"(2) {mode}: true pixel + true wrist + ref = truth -> exact "
              f"elbow and shoulder, max err {worst:.1e} < 1e-9",
              worst < 1e-9)
    # Shrunk search (W_b s = 0.8, W_c s = 0.9): the full-length output on
    # the chosen branch recovers the truth exactly (AKC-053).
    for w, name in ((akc.W_B, "W_b"), (akc.W_C, "W_c")):
        for mode in ("ray", "literal"):
            worst = 0.0
            n_resc = 0
            for i in range(0, 200, 5):
                r = akc.akc_correct(W[i], E[i], S[i], akc.project(E[i], K),
                                    akc.project(S[i], K), None, None, None,
                                    LENGTHS, w, mode, K)
                worst = max(worst, float(np.linalg.norm(r["e"] - E[i])),
                            float(np.linalg.norm(r["s"] - S[i])))
                n_resc += int(r["rescaled_e"]) + int(r["rescaled_s"])
            check(f"(2) {name} {mode} (s = {w.s}): true pixel + wrist + ref "
                  f"-> exact full-length elbow and shoulder, max err "
                  f"{worst:.1e} < 1e-9, radial rescale fallbacks {n_resc}",
                  worst < 1e-9 and n_resc == 0)
    # Literal with x, y deprojected at a wrong depth: error grows with dz.
    i = 50
    uv = akc.project(E[i], K)
    errs = []
    for dz in (0.0, 0.01, 0.02, 0.05, 0.10):
        ref = E[i] + np.array([0.0, 0.0, dz])
        c = akc.elbow_candidates(W[i], ref, uv, L_F, 1.0, "literal", K)
        errs.append(min(float(np.linalg.norm(p - E[i])) for p, _ in c))
    txt = ", ".join(f"{e * 100:.2f}" for e in errs)
    check(f"(2) literal, x,y at wrong depth dz = 0/1/2/5/10 cm -> elbow "
          f"error {txt} cm, strictly increasing",
          errs[0] < 1e-9 and all(b > a for a, b in zip(errs, errs[1:])))
    assert len(FAIL) == n0, FAIL[n0:]


# (2b) full-length output (AKC-053) ----------------------------------------

def test_full_length_output():
    n0 = len(FAIL)
    S, E, W = synth_arm()
    for mode in ("ray", "literal"):
        rng = np.random.default_rng(0)
        worst_full = worst_shr = 0.0
        same_search = True
        n_fb = n_resc = 0
        for i in range(200):
            ref_e = E[i] + rng.normal(0.0, 0.02, 3)
            ref_s = S[i] + rng.normal(0.0, 0.02, 3)
            args = (W[i], ref_e, ref_s, akc.project(E[i], K),
                    akc.project(S[i], K), None, None, OTHER_SHOULDER,
                    LENGTHS, akc.W_B, mode, K)
            r = akc.akc_correct(*args)
            q = akc.akc_correct(*args, output_shrunk=True)
            n_resc += int(r["rescaled_e"]) + int(r["rescaled_s"])
            worst_full = max(
                worst_full,
                abs(float(np.linalg.norm(r["e"] - W[i])) - L_F),
                abs(float(np.linalg.norm(r["s"] - r["e"])) - L_U))
            # output_shrunk: search-time points, s l when feasible, the
            # unscaled l on a fallback (Eq. 9).
            lf = (0.8 if q["feasible_e"] else 1.0) * L_F
            lu = (0.8 if q["feasible_s"] else 1.0) * L_U
            n_fb += int(not (q["feasible_e"] and q["feasible_s"]))
            worst_shr = max(
                worst_shr,
                abs(float(np.linalg.norm(q["e"] - W[i])) - lf),
                abs(float(np.linalg.norm(q["s"] - q["e"])) - lu))
            same_search &= bool(
                np.array_equal(q["e"], q["e_search"])
                and np.array_equal(q["s"], q["s_search"])
                and np.array_equal(r["e_search"], q["e_search"])
                and np.array_equal(r["s_search"], q["s_search"])
                and r["c"] == q["c"])
        check(f"(2b) {mode} s = 0.8: output |e - w| = l_f and |s - e| = "
              f"l_u, max dev {worst_full:.1e} m < 1e-12 (200 frames, "
              f"{n_resc} radial rescale fallbacks)", worst_full < 1e-12)
        check(f"(2b) {mode} s = 0.8, output_shrunk=True: lengths s l "
              f"(l on {n_fb} fallback frames), max dev {worst_shr:.1e} m "
              f"< 1e-12", worst_shr < 1e-12)
        check(f"(2b) {mode}: output_shrunk returns the search-time points; "
              f"search and cost identical in both settings", same_search)
    # AkcArm over a sequence: the search is the same with and without
    # output_shrunk (m3 uses the search-time points, AKC-054).
    _, _, _, frames, _ = _sequence()
    for mode in ("ray", "literal"):
        a = akc.AkcArm("right", LENGTHS, weights=akc.W_B, mode=mode)
        b = akc.AkcArm("right", LENGTHS, weights=akc.W_B, mode=mode,
                       output_shrunk=True)
        same = True
        dev = 0.0
        n_resc = 0
        for f in frames:
            obs = akc.occlusion_filter(f, "right", K)
            oa, ob = a.step(obs), b.step(obs)
            n_resc += int(oa.rescaled_e) + int(oa.rescaled_s)
            same &= bool(np.array_equal(oa.e_search, ob.e_search)
                         and np.array_equal(oa.s_search, ob.s_search)
                         and np.array_equal(ob.e, ob.e_search)
                         and oa.cost == ob.cost)
            dev = max(dev, abs(float(np.linalg.norm(oa.e - oa.w)) - L_F),
                      abs(float(np.linalg.norm(oa.s - oa.e)) - L_U))
        check(f"(2b) AkcArm {mode} W_b, 200 frames: search-time argmin and "
              f"cost identical with output_shrunk True / False; output "
              f"length dev {dev:.1e} m < 1e-12 ({n_resc} radial rescale "
              f"fallbacks)", same and dev < 1e-12)
    assert len(FAIL) == n0, FAIL[n0:]


# (3) candidate selection --------------------------------------------------

def test_selection():
    n0 = len(FAIL)
    for away in (False, True):
        S, E, W = synth_arm(away=away)
        fix = "away" if away else "toward"
        minus_e = int(np.sum(E[:, 2] < W[:, 2]))
        minus_s = int(np.sum(S[:, 2] < E[:, 2]))
        want = 200 if away else 0
        check(f"(3) fixture '{fix}': true elbow on the '-' root (z_e < z_w) "
              f"in {minus_e}/200 frames, true shoulder on the '-' root "
              f"(z_s < z_e) in {minus_s}/200 (need {want})",
              minus_e == want and minus_s == want)
        for w, name in ((akc.W_A, "W_a"), (akc.W_B, "W_b"),
                        (akc.W_C, "W_c")):
            for mode in ("ray", "literal"):
                rng = np.random.default_rng(0)
                n_ok = n_used = n3 = 0
                worst = 0.0
                for i in range(200):
                    se = _z_sep(W[i], E[i], L_F, w.s)
                    ss = _z_sep(E[i], S[i], L_U, w.s)
                    ref_e = E[i] + rng.normal(0.0, 0.02, 3)
                    ref_s = S[i] + rng.normal(0.0, 0.02, 3)
                    if se is None or ss is None or se < 0.10 or ss < 0.10:
                        continue
                    uv_e, uv_s = akc.project(E[i], K), akc.project(S[i], K)
                    # Expected branch from the hand-written roots: the
                    # root nearer the truth, elbow first, then the
                    # shoulder about that elbow.
                    he = _hand_roots(W[i], ref_e, uv_e, L_F, w.s, mode)
                    if he is None:
                        continue
                    e_true = min(he, key=lambda p: np.linalg.norm(p - E[i]))
                    hs = _hand_roots(e_true, ref_s, uv_s, L_U, w.s, mode)
                    if hs is None:
                        continue
                    s_true = min(hs, key=lambda p: np.linalg.norm(p - S[i]))
                    # Expected candidate count: two shoulder roots per
                    # elbow root, one (Eq. 9 fallback) when the hand
                    # solve about that elbow root has no two roots.
                    n_exp = sum(1 if _hand_roots(e, ref_s, uv_s, L_U, w.s,
                                                 mode) is None else 2
                                for e in he)
                    r = akc.akc_correct(W[i], ref_e, ref_s, uv_e, uv_s, None,
                                        None, OTHER_SHOULDER, LENGTHS, w,
                                        mode, K)
                    dev = max(float(np.linalg.norm(r["e_search"] - e_true)),
                              float(np.linalg.norm(r["s_search"] - s_true)))
                    worst = max(worst, dev)
                    n_used += 1
                    n3 += int(n_exp == 3)
                    n_ok += int(dev < 1e-12 and r["n_candidates"] == n_exp)
                check(f"(3) {fix} {name} {mode}: argmin (search-time "
                      f"points, AKC-053) equals the hand-computed true "
                      f"branch under 2 cm reference noise, candidate count "
                      f"as computed by hand (3 in {n3} frames: the wrong "
                      f"elbow's shoulder falls back), in {n_ok}/{n_used} "
                      f"frames, max dev {worst:.1e} m (need all, >= 50 "
                      f"frames, < 1e-12)", n_used >= 50 and n_ok == n_used)
    # Hand-computed literal case on the '-' branch (arm pointing away):
    # wrist (0, 0, 1); elbow x, y (0.10, 0.05) -> sqrt(0.23^2 - 0.10^2 -
    # 0.05^2) = sqrt(0.0404); shoulder dx, dy (0.05, -0.20) about the
    # elbow -> sqrt(0.25^2 - 0.05^2 - 0.20^2) = sqrt(0.02).
    q_e = 0.20099751242241780          # sqrt(0.0404)
    q_s = 0.14142135623730950          # sqrt(0.02)
    p_w = np.array([0.0, 0.0, 1.0])
    e_minus = np.array([0.10, 0.05, 1.0 - q_e])
    e_plus = np.array([0.10, 0.05, 1.0 + q_e])
    s_minus = np.array([0.15, -0.15, 1.0 - q_e - q_s])
    lens = dict(l_f=0.23, l_u=0.25, l_s=L_S)
    ce = akc.elbow_candidates(p_w, [0.10, 0.05, 0.85], None, 0.23, 1.0,
                              "literal", K)
    check("(3) literal hand case: elbow candidates [(0.10, 0.05, "
          "1 - sqrt(0.0404)), (0.10, 0.05, 1 + sqrt(0.0404))], both "
          "feasible, to 1e-12",
          len(ce) == 2 and all(f for _, f in ce)
          and np.allclose(ce[0][0], e_minus, rtol=0, atol=1e-12)
          and np.allclose(ce[1][0], e_plus, rtol=0, atol=1e-12))
    cs = akc.shoulder_candidates(e_minus, [0.15, -0.15, 0.70], None, 0.25,
                                 1.0, "literal", K)
    check("(3) literal hand case: shoulder candidates about the '-' elbow "
          "at z_e -/+ sqrt(0.02), to 1e-12",
          len(cs) == 2
          and np.allclose(cs[0][0], s_minus, rtol=0, atol=1e-12)
          and np.allclose(cs[1][0], s_minus + [0, 0, 2 * q_s], rtol=0,
                          atol=1e-12))
    r = akc.akc_correct(p_w, [0.10, 0.05, 0.80], [0.15, -0.15, 0.62], None,
                        None, None, None, None, lens, akc.W_A, "literal", K)
    check(f"(3) literal hand case, W_a: argmin and output are the '-' "
          f"elbow and '-' shoulder (err {np.linalg.norm(r['e'] - e_minus):.1e}"
          f" / {np.linalg.norm(r['s'] - s_minus):.1e} m < 1e-12)",
          np.linalg.norm(r["e"] - e_minus) < 1e-12
          and np.linalg.norm(r["s"] - s_minus) < 1e-12)
    # m1 alone decides (w1 = 1, all other weights 0): ref_e is nearer the
    # '+' elbow, ref_s nearer the '-' elbow; c = |e_plus - ref_e| =
    # sqrt(0.0404) - 0.15 by hand.
    w_m1 = akc.AkcWeights(w1=1.0, w2=0.0, w3=0.0, s=1.0, w4=0.0, w5=0.0)
    r = akc.akc_correct(p_w, [0.10, 0.05, 1.15], [0.15, -0.15, 0.70], None,
                        None, None, None, None, lens, w_m1, "literal", K)
    check(f"(3) m1 alone decides: '+' elbow chosen (z {r['e_search'][2]:.4f}"
          f"), c = {r['c']:.6f} = sqrt(0.0404) - 0.15 to 1e-12",
          np.allclose(r["e_search"], e_plus, rtol=0, atol=1e-12)
          and abs(r["c"] - (q_e - 0.15)) < 1e-12)
    # m3 alone decides (w3 = 1): the previous choice sits 3 mm (elbow) and
    # 4 mm (shoulder) from the ('+' elbow, '+' shoulder) configuration;
    # ref_e at the '-' elbow would win under m1; c = 0.003 + 0.004.
    w_m3 = akc.AkcWeights(w1=0.0, w2=0.0, w3=1.0, s=1.0, w4=0.0, w5=0.0)
    s_pp = np.array([0.15, -0.15, 1.0 + q_e + q_s])
    r = akc.akc_correct(p_w, e_minus, [0.15, -0.15, 0.70], None, None,
                        e_plus + [0.003, 0.0, 0.0], s_pp + [0.0, 0.004, 0.0],
                        None, lens, w_m3, "literal", K)
    check(f"(3) m3 alone decides: ('+', '+') chosen, c = {r['c']:.6f} = "
          f"0.007 to 1e-12",
          np.allclose(r["e_search"], e_plus, rtol=0, atol=1e-12)
          and np.allclose(r["s_search"], s_pp, rtol=0, atol=1e-12)
          and abs(r["c"] - 0.007) < 1e-12)
    S, E, W = synth_arm()
    # m5: an over-flexed (theta < 40 deg) configuration closer to the
    # references loses to a plausible one.
    p_e = np.array([0.0, 0.0, 1.0])
    p_w = p_e + L_F * np.array([1.0, 0.0, 0.0])
    a30, a120 = np.radians(30.0), np.radians(120.0)
    s_fold = p_e + L_U * np.array([np.cos(a30), np.sin(a30), 0.0])
    s_ok = p_e + L_U * np.array([np.cos(a120), np.sin(a120), 0.0])
    c_f, t_f = akc.cost(p_e, s_fold, p_e, s_fold, None, None, None, p_w,
                        L_S, akc.W_C)
    c_o, t_o = akc.cost(p_e, s_ok, p_e, s_fold, None, None, None, p_w,
                        L_S, akc.W_C)
    check(f"(3) m5: theta {t_f['theta']:.0f} deg -> m5 = k, theta "
          f"{t_o['theta']:.0f} deg -> 0; folded cost {c_f:.0f} > plausible "
          f"{c_o:.2f} although m2 favours the folded one",
          t_f["m5"] == 100.0 and t_o["m5"] == 0.0 and c_f > c_o
          and t_f["m2"] < t_o["m2"])
    s_straight = p_e - L_U * np.array([1.0, 0.0, 0.0])
    _, t_s = akc.cost(p_e, s_straight, p_e, s_straight, None, None, None,
                      p_w, L_S, akc.W_C)
    check(f"(3) m5: straight arm theta {t_s['theta']:.1f} deg is inside "
          f"[40, 180] (m5 = 0)", t_s["m5"] == 0.0)
    # m4: wrong shoulder root rejected when m2 cannot tell (ref_s at the
    # midpoint of the two roots).
    picked = None
    for i in range(200):
        ss = _z_sep(E[i], S[i], L_U, 1.0)
        if ss is not None and ss >= 0.10:
            picked = i
            break
    i = picked
    uv_s = akc.project(S[i], K)
    cs = akc.shoulder_candidates(E[i], S[i], uv_s, L_U, 1.0, "ray", K)
    mid = 0.5 * (cs[0][0] + cs[1][0])
    wrong = max(cs, key=lambda c: np.linalg.norm(c[0] - S[i]))[0]
    _, t_w = akc.cost(E[i], wrong, E[i], mid, None, None, OTHER_SHOULDER,
                      W[i], L_S, akc.W_A)
    r = akc.akc_correct(W[i], E[i], mid, akc.project(E[i], K), uv_s, None,
                        None, OTHER_SHOULDER, LENGTHS, akc.W_A, "ray", K)
    check(f"(3) m4: wrong shoulder root has m4 = {t_w['m4'] * 100:.1f} cm; "
          f"argmin picks the true root (err "
          f"{np.linalg.norm(r['s'] - S[i]):.1e})",
          t_w["m4"] > 0.01 and np.linalg.norm(r["s"] - S[i]) < 1e-9)
    # m4 alone flips the argmin: w5 = 0 (m5 cannot act), w1 = 100 with
    # ref_e at the true elbow (the elbow root is fixed), ref_s 60 % of the
    # way toward the wrong shoulder root so m2 prefers it; with w4 = 100
    # the true root wins, with w4 = 0 the wrong root wins.
    ref_bias = S[i] + 0.6 * (wrong - S[i])
    for w4, want in ((100.0, "true"), (0.0, "wrong")):
        ww = akc.AkcWeights(w1=100.0, w2=8.0, w3=18.0, s=1.0, w4=w4,
                            w5=0.0)
        r = akc.akc_correct(W[i], E[i], ref_bias, akc.project(E[i], K),
                            uv_s, None, None, OTHER_SHOULDER, LENGTHS, ww,
                            "ray", K)
        target = S[i] if want == "true" else wrong
        check(f"(3) m4 flip (w5 = 0, ref_s biased to the wrong root): "
              f"w4 = {w4:.0f} picks the {want} shoulder root (err "
              f"{np.linalg.norm(r['s'] - target):.1e})",
              np.linalg.norm(r["s"] - target) < 1e-9)
    assert len(FAIL) == n0, FAIL[n0:]


# (4) negative radicand ----------------------------------------------------

def test_fallback():
    n0 = len(FAIL)
    p_w = np.array([0.0, 0.0, 1.0])
    ref = p_w + np.array([1.3 * L_F, 0.0, 0.05])
    for mode in ("literal", "ray"):
        for s in (1.0, 0.8):
            c = akc.elbow_candidates(p_w, ref, None, L_F, s, mode, K)
            ok = (len(c) == 1 and c[0][1] is False
                  and abs(np.linalg.norm(c[0][0] - p_w) - L_F) < 1e-12)
            check(f"(4) {mode} s={s}: wrist beyond l_f -> fallback with "
                  f"|p_e - p_w| = l_f (unscaled) to 1e-12", ok)
    ref_b = p_w + np.array([0.85 * L_F, 0.0, 0.05])       # literal
    a = np.arcsin(0.9 * L_F)                              # ray, |p_w| = 1
    ref_r = 1.02 * np.array([np.sin(a), 0.0, np.cos(a)])
    for mode, rb in (("literal", ref_b), ("ray", ref_r)):
        c1 = akc.elbow_candidates(p_w, rb, None, L_F, 1.0, mode, K)
        c8 = akc.elbow_candidates(p_w, rb, None, L_F, 0.8, mode, K)
        check(f"(4) {mode}: borderline case feasible at s=1.0 (2 cands), "
              f"infeasible at s=0.8 (fallback)",
              len(c1) == 2 and all(f for _, f in c1)
              and len(c8) == 1 and c8[0][1] is False)
    # Full-length output, radial rescale fallback (AKC-053): ray mode, the
    # chosen near elbow root moves toward the camera at l_f, which puts
    # the camera inside the l_u shoulder sphere: 2 roots at search time,
    # 1 at full length -> the shoulder falls back and is flagged.
    lens = dict(l_f=0.23, l_u=0.25, l_s=0.36)
    pw = np.array([0.0, 0.0, 0.45])
    ref_e = np.array([0.0, 0.0, 0.3])
    ref_s = 0.45 * _unit(np.array([0.3, 0.0, 1.0]))
    ce = akc.elbow_candidates(pw, ref_e, None, lens["l_f"], 0.8, "ray", K)
    cs = akc.shoulder_candidates(ce[0][0], ref_s, None, lens["l_u"], 0.8,
                                 "ray", K)
    best = dict(e=ce[0][0], s=cs[1][0], feasible_e=True, feasible_s=True,
                j_e=0, n_e=len(ce), j=1, n_s=len(cs))
    pe, ps, re, rs = akc.full_length_chain(pw, best, ref_e, ref_s, None,
                                           None, lens, akc.W_B, "ray", K)
    check(f"(4) full-length output, shoulder root count 2 -> 1: radial "
          f"rescale flagged for the shoulder only, elbow on its ray at l_f "
          f"(z {pe[2]:.3f}), lengths exact to 1e-12",
          len(ce) == 2 and len(cs) == 2 and not re and rs
          and abs(pe[2] - (0.45 - 0.23)) < 1e-12
          and abs(np.linalg.norm(pe - pw) - lens["l_f"]) < 1e-12
          and abs(np.linalg.norm(ps - pe) - lens["l_u"]) < 1e-12)
    assert len(FAIL) == n0, FAIL[n0:]


# (5) Kalman filter --------------------------------------------------------

def test_kalman():
    n0 = len(FAIL)
    p0 = np.array([0.1, -0.2, 1.0])
    v = np.array([0.3, -0.1, -0.5])
    kf = akc.CVKalman(DT, 0.0, 1e-9, 1e-9, v0_sigma=1.0)
    worst = 0.0
    for k in range(40):
        truth = p0 + v * k * DT
        if k >= 2:
            pred = copy.deepcopy(kf).predict()[0]
            worst = max(worst, float(np.linalg.norm(pred - truth)))
        kf.step(akc.Obs(xyz=truth, vis=1.0), K)
    check(f"(5) noise-free CV truth predicted after two updates "
          f"(sigma_a 0, sigma 1e-9), max err {worst:.1e} < 1e-9",
          worst < 1e-9)
    kf = akc.CVKalman(**akc.DEFAULT_KF)
    errs = []
    for k in range(300):
        truth = p0 + v * k * DT
        if k >= 2:
            pred = copy.deepcopy(kf).predict()[0]
            errs.append(float(np.linalg.norm(pred - truth)))
        kf.step(akc.Obs(xyz=truth, vis=1.0), K)
    check(f"(5) defaults: CV prediction error decays, frame 2 "
          f"{errs[0] * 100:.2f} cm -> frame 299 {errs[-1]:.1e} m < 1e-6",
          errs[-1] < 1e-6 and errs[-1] < errs[0])
    # Partial update keeps z at the prediction.
    kf = akc.CVKalman(**akc.DEFAULT_KF)
    for k in range(10):
        kf.step(akc.Obs(xyz=p0 + v * k * DT, vis=1.0), K)
    pred = copy.deepcopy(kf).predict()[0]
    uv = akc.project(p0 + v * 10 * DT + np.array([0.01, 0.0, 0.0]), K)
    out = kf.step(akc.Obs(uv=uv, vis=1.0), K)
    check("(5) partial xy update: z equals the prediction exactly, x moves",
          out[2] == pred[2] and abs(out[0] - pred[0]) > 1e-4
          and kf.last_source == "partial")
    pred = copy.deepcopy(kf).predict()[0]
    out = kf.step(None, K)
    out2 = kf.step(akc.Obs(vis=0.0), K)
    check("(5) missing frame returns the prediction",
          np.array_equal(out, pred) and kf.last_source == "kf_pred"
          and out2 is not None)
    kf = akc.CVKalman(**akc.DEFAULT_KF)
    for _ in range(300):
        kf.step(akc.Obs(xyz=p0, vis=1.0), K)
    gx, gz = kf.last_K[0, 0], kf.last_K[2, 2]
    check(f"(5) sigma_z = 5 sigma_xy: steady-state z gain {gz:.3f} < x gain "
          f"{gx:.3f}", gz < gx)
    # Q by hand: white acceleration, G = [dt^2 / 2, dt] per axis.
    kf = akc.CVKalman(DT, 5.0, 0.01, 0.05)
    g = np.array([DT ** 2 / 2.0, DT])
    q2 = 5.0 ** 2 * np.array([[g[0] * g[0], g[0] * g[1]],
                              [g[1] * g[0], g[1] * g[1]]])
    q_exp = np.kron(q2, np.eye(3))
    a_exp = np.kron(np.array([[1.0, DT], [0.0, 1.0]]), np.eye(3))
    check(f"(5) Q = sigma_a^2 G G^T with G = [dt^2/2, dt] (pos-pos "
          f"{q_exp[0, 0]:.3e}, pos-vel {q_exp[0, 3]:.3e}, vel-vel "
          f"{q_exp[3, 3]:.3e}) and A = [[I, dt I], [0, I]], rtol 1e-12",
          np.allclose(kf.Q, q_exp, rtol=1e-12, atol=0.0)
          and np.allclose(kf.A, a_exp, rtol=1e-12, atol=0.0))
    # Partial update lifts the pixel at the predicted depth: a filter at
    # rest at z = 1.5 m with a near-unit gain (sigma 1e-9) must give
    # x = (u - cx) 1.5 / fx, y = (v - cy) 1.5 / fy.
    kf = akc.CVKalman(DT, 5.0, 1e-9, 1e-9)
    kf.init([0.0, 0.0, 1.5])
    out = kf.step(akc.Obs(uv=np.array([400.0, 300.0]), vis=1.0), K)
    x_exp = (400.0 - K["cx"]) * 1.5 / K["fx"]
    y_exp = (300.0 - K["cy"]) * 1.5 / K["fy"]
    check(f"(5) partial update at predicted depth 1.5 m: x {out[0]:.6f} = "
          f"(u - cx) 1.5 / fx {x_exp:.6f}, y {out[1]:.6f} = {y_exp:.6f} "
          f"(1e-9), z stays 1.5",
          abs(out[0] - x_exp) < 1e-9 and abs(out[1] - y_exp) < 1e-9
          and out[2] == 1.5 and kf.last_source == "partial")
    check("(5) before the first xyz the filter returns None",
          akc.CVKalman(**akc.DEFAULT_KF).step(akc.Obs(uv=uv, vis=1.0), K)
          is None)
    assert len(FAIL) == n0, FAIL[n0:]


# (6) occlusion filter -----------------------------------------------------

def test_occlusion_filter():
    n0 = len(FAIL)
    xw = np.array([0.0, 0.0, 0.8])
    uvw = akc.project(xw, K)
    xs = np.array([0.1, -0.3, 1.0])
    xe = np.array([0.2, -0.1, 0.9])

    def lms(uv_e, vis_e=0.9, uv_s=None):
        return {"wrist": (xw, uvw, 0.95), "elbow": (xe, uv_e, vis_e),
                "shoulder": (xs, uv_s, 0.95),
                "other_shoulder": (xs + [-0.35, 0, 0], None, 0.95)}

    far = uvw + np.array([100.0, 0.0])
    o = akc.occlusion_filter(lms(far, vis_e=0.69), "right", K)
    check("(6) vis 0.69 drops xyz and uv",
          o["elbow"].xyz is None and o["elbow"].uv is None)
    o = akc.occlusion_filter(lms(far, vis_e=0.70), "right", K)
    check("(6) vis 0.70 keeps the landmark", o["elbow"].xyz is not None)
    o = akc.occlusion_filter(lms(uvw + np.array([31.0, 0.0])), "right", K)
    check("(6) elbow 31 px from wrist: uv kept, xyz dropped",
          o["elbow"].xyz is None and o["elbow"].uv is not None
          and o["wrist"].xyz is not None)
    o = akc.occlusion_filter(lms(uvw + np.array([0.0, 33.0])), "right", K)
    check("(6) elbow 33 px from wrist: xyz and uv kept",
          o["elbow"].xyz is not None and o["elbow"].uv is not None)
    o = akc.occlusion_filter(lms(far, uv_s=far + np.array([5.0, 0.0])),
                             "left", K)
    check("(6) shoulder 5 px from elbow (both far from wrist): both kept",
          o["elbow"].xyz is not None and o["shoulder"].xyz is not None)
    o = akc.occlusion_filter(lms(far), "right", K)
    check("(6) missing uv filled by projection",
          np.allclose(o["shoulder"].uv, akc.project(xs, K), atol=1e-12))
    assert len(FAIL) == n0, FAIL[n0:]


# (7) EKF length constraint ------------------------------------------------

def test_ekf():
    n0 = len(FAIL)
    anchor = np.array([0.0, 0.0, 1.0])
    # Isotropic position covariance: P u is parallel to u, so the
    # linearised step lands on the sphere and repeats are no-ops.
    kf = akc.CVKalman(DT, 5.0, 0.03, 0.03)
    kf.step(akc.Obs(xyz=[0.3, 0.1, 1.05], vis=1.0), K)
    kf.step(akc.Obs(xyz=[0.31, 0.1, 1.04], vis=1.0), K)
    for _ in range(50):
        kf.constrain_length(anchor, L_F, 1e-9)
    err = abs(float(np.linalg.norm(kf.p - anchor)) - L_F)
    check(f"(7) repeated EKF constraint, isotropic P, sigma_l 1e-9: "
          f"||p - a| - l| = {err:.1e} < 1e-6", err < 1e-6)
    # Default anisotropic P (sigma_z = 5 sigma_xy): one step moves off
    # the radial direction, so it reduces but does not close the gap;
    # repeated hard steps converge slowly (AKC-016).
    kf = akc.CVKalman(**akc.DEFAULT_KF)
    kf.step(akc.Obs(xyz=[0.3, 0.1, 1.05], vis=1.0), K)
    kf.step(akc.Obs(xyz=[0.31, 0.1, 1.04], vis=1.0), K)
    e0 = abs(float(np.linalg.norm(kf.p - anchor)) - L_F)
    kf.constrain_length(anchor, L_F, 1e-6)
    e1 = abs(float(np.linalg.norm(kf.p - anchor)) - L_F)
    check(f"(7) default anisotropic P, one step, sigma_l 1e-6: length "
          f"error {e0 * 100:.2f} -> {e1 * 100:.2f} cm (reduced)", e1 < e0)
    kf2 = akc.CVKalman(**akc.DEFAULT_KF)
    kf2.step(akc.Obs(xyz=[0.3, 0.1, 1.05], vis=1.0), K)
    h0 = float(np.linalg.norm(kf2.p - anchor))
    kf2.constrain_length(anchor, L_F, 0.02)
    h1 = float(np.linalg.norm(kf2.p - anchor))
    check(f"(7) one soft update (sigma_l 0.02) moves toward l: "
          f"{h0:.4f} -> {h1:.4f} (l = {L_F})",
          abs(h1 - L_F) < abs(h0 - L_F) and abs(h1 - L_F) > 1e-4)
    # Anchors inside AkcArm (AKC-056): "filtered" ties the elbow to the
    # Kalman wrist, "raw" to the measured wrist p_w; the shoulder is tied
    # to the constrained elbow in both.
    _, _, _, frames, _ = _sequence()
    for anchor in ("filtered", "raw"):
        arm = akc.AkcArm("right", LENGTHS, ekf=True, ekf_anchor=anchor)
        rec = {"elbow": [], "shoulder": []}
        for j in ("elbow", "shoulder"):
            def wrapped(a, length, sigma_l, _j=j,
                        _orig=arm.kf[j].constrain_length):
                ref_j = "wrist" if _j == "elbow" else "elbow"
                rec[_j].append((np.array(a, float),
                                arm.kf[ref_j].p.copy()))
                return _orig(a, length, sigma_l)
            arm.kf[j].constrain_length = wrapped
        n_kf = n_meas = n_sh = 0
        for fi, f in enumerate(frames):
            obs = akc.occlusion_filter(f, "right", K)
            k = len(rec["elbow"])
            arm.step(obs)
            # frame 0 initialises the wrist filter at the measurement, so
            # the two anchors coincide there; it is not counted.
            if len(rec["elbow"]) == k or fi == 0:
                continue
            a_used, kf_w = rec["elbow"][-1]
            n_kf += int(np.array_equal(a_used, kf_w))
            n_meas += int(np.array_equal(a_used, obs["wrist"].xyz))
            a_s, kf_e = rec["shoulder"][-1]
            n_sh += int(np.array_equal(a_s, kf_e))
        n = len(rec["elbow"]) - 1
        want_kf, want_meas = (n, 0) if anchor == "filtered" else (0, n)
        check(f"(7) AkcArm ekf_anchor={anchor!r}: elbow anchor = Kalman "
              f"wrist in {n_kf}/{n}, = measured wrist in {n_meas}/{n}; "
              f"shoulder anchor = constrained elbow in {n_sh}/{n}",
              n >= 190 and n_kf == want_kf and n_meas == want_meas
              and n_sh == n)
    try:
        akc.AkcArm("right", LENGTHS, ekf=True, ekf_anchor="bogus")
        bad = False
    except ValueError:
        bad = True
    check("(7) unknown ekf_anchor raises ValueError", bad)
    assert len(FAIL) == n0, FAIL[n0:]


# (8) determinism and masked-frame behaviour -------------------------------

def _sequence():
    S, E, W = synth_arm(200)
    rng = np.random.default_rng(0)
    frames = []
    for i in range(200):
        f = {}
        for name, p in (("shoulder", S[i]), ("elbow", E[i]), ("wrist", W[i]),
                        ("other_shoulder", OTHER_SHOULDER)):
            uv = akc.project(p, K) + rng.normal(0.0, 0.5, 2)
            z = p[2] + rng.normal(0.0, 0.005)
            f[name] = (akc.deproject(uv[0], uv[1], z, K), uv, 0.99)
        frames.append(f)
    masked = set(range(100, 120))
    for i in masked:                          # MASK_Z: pixel kept
        frames[i]["elbow"] = (None, frames[i]["elbow"][1], 0.99)
    return S, E, W, frames, masked


def _run(frames, mode, weights):
    arm = akc.AkcArm("right", LENGTHS, weights=weights, mode=mode)
    outs = []
    for f in frames:
        obs = akc.occlusion_filter(f, "right", K)
        outs.append(arm.step(obs))
    return outs


def _pack(outs):
    rows = []
    for o in outs:
        rows.append(np.concatenate([o.e, o.s, o.w, o.ref_e, o.ref_s,
                                    [o.cost, o.n_candidates]]
                                   + [[o.terms[k]] for k in
                                      ("m1", "m2", "m3", "m4", "m5")]))
    return np.array(rows)


def test_determinism():
    n0 = len(FAIL)
    S, E, W, frames, masked = _sequence()
    a = _pack(_run(frames, "ray", akc.W_A))
    b = _pack(_run(frames, "ray", akc.W_A))
    check(f"(8) two AkcArm runs on 200 frames bit-identical "
          f"({a.size} values)", a.tobytes() == b.tobytes())
    outs = _run(frames, "ray", akc.W_A)
    idx = sorted(masked)
    e_akc = np.array([np.linalg.norm(outs[i].e - E[i]) for i in idx])
    kf = akc.CVKalman(**akc.DEFAULT_KF)
    e_kf = []
    for i, f in enumerate(frames):
        obs = akc.occlusion_filter(f, "right", K)
        p = kf.step(obs["elbow"], K)
        if i in masked:
            e_kf.append(float(np.linalg.norm(p - E[i])))
    e_kf = np.array(e_kf)
    e_w = np.array([np.linalg.norm(outs[i].w - W[i]) for i in idx])
    check(f"(8) ray mode, W_a, 20 depth-masked elbow frames: median elbow "
          f"error {np.median(e_akc) * 100:.2f} cm < 1 cm",
          np.median(e_akc) < 0.01)
    check(f"(8) masked elbow error bounded by the kept raw wrist error: "
          f"max {e_akc.max() * 100:.2f} cm <= wrist max "
          f"{e_w.max() * 100:.2f} cm + 1 mm",
          e_akc.max() <= e_w.max() + 0.001)
    check(f"(8) KF-only elbow error grows over the gap: "
          f"{e_kf[0] * 100:.2f} cm -> {e_kf[-1] * 100:.2f} cm "
          f"(last > first, last > 1 cm)",
          e_kf[-1] > e_kf[0] and e_kf[-1] > 0.01)
    srcs = {outs[i].src["elbow"] for i in idx}
    check(f"(8) masked elbow frames sourced from AKC ({sorted(srcs)})",
          srcs == {"akc"})
    finite = True
    for kw in (dict(mode="literal"), dict(ekf=True), dict(feedback=True),
               dict(always_correct=False), dict(weights=akc.W_C)):
        arm = akc.AkcArm("right", LENGTHS, **kw)
        for f in frames:
            o = arm.step(akc.occlusion_filter(f, "right", K))
            finite &= bool(np.all(np.isfinite(o.e)) and
                           np.all(np.isfinite(o.s)))
    check("(8) literal / ekf / feedback / always_correct=False / W_c "
          "variants run and stay finite", finite)
    stats = akc.arm_length_stats(np.array([o.e for o in outs]),
                                 np.array([o.s for o in outs]),
                                 np.array([o.w for o in outs]))
    check(f"(8) arm_length_stats: forearm range "
          f"{stats['forearm_range']:.1e} m, upper range "
          f"{stats['upper_range']:.1e} m (s = 1 -> fixed lengths, < 1e-9)",
          stats["n"] == 200 and stats["forearm_range"] < 1e-9
          and stats["upper_range"] < 1e-9)
    assert len(FAIL) == n0, FAIL[n0:]


TESTS = (test_projection, test_exact_recovery, test_full_length_output,
         test_selection,
         test_fallback, test_kalman, test_occlusion_filter, test_ekf,
         test_determinism)


def main():
    for t in TESTS:
        try:
            t()
        except AssertionError:
            pass
    print(f"=== {'ALL PASS' if not FAIL else 'FAILED'} "
          f"({len(FAIL)} failures) ===")
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
