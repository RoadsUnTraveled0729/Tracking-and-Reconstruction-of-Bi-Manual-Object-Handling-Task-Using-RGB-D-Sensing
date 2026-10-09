#!/usr/bin/env python3
"""GPU-vs-CPU / vectorization benchmark for the 13-angle kinematic solve.

Answers, with measurements (REALTIME.md quotes these):
  1. What does numpy vectorization buy over the per-frame scalar loop?
  2. Does running the L/R arm solves in parallel threads help?
  3. Does numba JIT help?
  4. CPU or GPU (CuPy / torch) — at the real-time batch size (N=1) and at
     offline batch sizes? GPU timed both WITH host<->device transfer (the
     real-time case always pays it) and with data resident on device.
  5. The ArUco per-frame stage (detectMarkers + IPPE): does threading help?
     (OpenCV releases the GIL in C++ calls, so frame-level threads can
     genuinely overlap — unlike the tiny numpy solve.)

All numeric arms are verified against shoulder_vec.solve_all_vec (which is
itself gated ≤ 1e-10 deg against the scalar reference) before timing.

Usage:
    python bench_solver.py [--sizes 1 10 100 1000 10000 100000]
                           [--no-aruco] [--out output/bench_solver]
Writes <out>.csv + <out>.png.
"""
import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                 # repo root (realtime/bench/ -> repo)
DEG = 180.0 / np.pi
GIMBAL_EPS = 1e-8
TWIST_EPS = 1e-6

LANDMARKS = ("left_hip", "right_hip", "left_shoulder", "right_shoulder",
             "left_elbow", "right_elbow", "left_wrist", "right_wrist")


# ------------------------------------------------------------------ data

def load_landmarks(n):
    """Real recording landmarks (Unity space), tiled to n frames."""
    import sys
    sys.path.insert(0, str(ROOT / "kinematics"))
    from root_frame import unity_from_sensor
    df = pd.read_csv(ROOT / "mediapipe/output/"
                     "recording_20260224_083945_landmarks_filtered_v2.csv")
    P = {}
    valid = np.ones(len(df), bool)
    for name in LANDMARKS:
        xyz = df[[f"{name}_x", f"{name}_y", f"{name}_z"]].to_numpy(float)
        P[name] = unity_from_sensor(xyz)
        valid &= np.isfinite(xyz).all(axis=1)
    idx = np.flatnonzero(valid)
    reps = int(np.ceil(n / len(idx)))
    sel = np.tile(idx, reps)[:n]
    return [np.ascontiguousarray(P[name][sel]) for name in LANDMARKS]


# ------------------------------------------------- backend-generic solve
# Closed-form component version of the full 13-angle solve — no matrix
# stacks, so the identical code runs on numpy, CuPy, and torch arrays.
# Elementary rotations applied componentwise:
#   Ry(t)v = ( c vx + s vz,  vy, -s vx + c vz)
#   Rz(t)v = ( c vx - s vy,  s vx + c vy, vz)
#   Rx(t)v = ( vx,  c vy - s vz,  s vy + c vz)

def solve_all_generic(xp, p23, p24, p11, p12, p13, p14, p15, p16):
    def dot(a, b):
        return (a * b).sum(-1)

    def norm3(v):
        return v / xp.sqrt(dot(v, v))[..., None]

    def cross(a, b):
        return xp.stack([a[:, 1] * b[:, 2] - a[:, 2] * b[:, 1],
                         a[:, 2] * b[:, 0] - a[:, 0] * b[:, 2],
                         a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0]], -1)

    # root frame columns
    r = norm3(p24 - p23)
    s = p12 - p24
    f = norm3(cross(r, s))
    u = cross(f, r)

    def to_root(v):     # R_root^T v
        return xp.stack([dot(r, v), dot(u, v), dot(f, v)], -1)

    # root Unity-ZXY euler from columns [r|u|f] (workspace far from lock)
    ex = -xp.arcsin(xp.clip(f[:, 1], -1.0, 1.0))
    ey_r = xp.arctan2(f[:, 0], f[:, 2])
    ez_r = xp.arctan2(r[:, 1], u[:, 1])

    def arm(su, sf):
        """su/sf: upper-arm / forearm vectors in the parent basis."""
        a = norm3(su)
        sz = xp.clip(a[:, 1], -1.0, 1.0)
        th_z = xp.arcsin(sz)
        gim = (1.0 - xp.abs(sz)) < GIMBAL_EPS
        th_y = xp.where(gim, xp.zeros_like(sz), xp.arctan2(-a[:, 2], a[:, 0]))
        # un-swing the forearm: fp = Rz(-th_z) Ry(-th_y) sf
        cy, sy = xp.cos(th_y), xp.sin(th_y)
        v0 = cy * sf[:, 0] - sy * sf[:, 2]
        v1 = sf[:, 1]
        v2 = sy * sf[:, 0] + cy * sf[:, 2]
        cz, szn = xp.cos(th_z), xp.sin(th_z)
        f0 = cz * v0 + szn * v1
        f1 = -szn * v0 + cz * v1
        f2 = v2
        perp = xp.sqrt(f1 * f1 + f2 * f2)
        ok = perp >= TWIST_EPS * xp.sqrt(dot(sf, sf))
        th_t = xp.where(ok, xp.arctan2(-f1, f2), xp.zeros_like(perp))
        # elbow: g = Rx(-th_t) fp
        ct, st = xp.cos(th_t), xp.sin(th_t)
        g0 = f0
        g1 = ct * f1 + st * f2
        g2 = -st * f1 + ct * f2
        gn = xp.sqrt(g0 * g0 + g1 * g1 + g2 * g2)
        e_z = xp.arcsin(xp.clip(g1 / gn, -1.0, 1.0))
        e_y = xp.arctan2(-g2 / gn, g0 / gn)
        return th_y, th_z, th_t, e_y, e_z, ok

    ry, rz_, rt, rey, rez, rok = arm(to_root(p14 - p12), to_root(p16 - p14))
    lu = to_root(p13 - p11)
    lf = to_root(p15 - p13)
    # sagittal mirror: flip x
    lu = xp.stack([-lu[:, 0], lu[:, 1], lu[:, 2]], -1)
    lf = xp.stack([-lf[:, 0], lf[:, 1], lf[:, 2]], -1)
    ly, lz, lt, ley, lez, lok = arm(lu, lf)

    out = xp.stack([ex, ey_r, ez_r, ry, rz_, rt, rey, rez,
                    ly, lz, lt, ley, lez], -1) * DEG
    return out, rok, lok


# ---------------------------------------------------------- numba kernel

def make_numba_kernel():
    import numba as nb

    @nb.njit(cache=True, fastmath=False)
    def kern(p23, p24, p11, p12, p13, p14, p15, p16, out):
        n = p23.shape[0]
        for i in range(n):
            # root
            rx = p24[i, 0] - p23[i, 0]
            ry_ = p24[i, 1] - p23[i, 1]
            rz = p24[i, 2] - p23[i, 2]
            rn = (rx * rx + ry_ * ry_ + rz * rz) ** 0.5
            rx, ry_, rz = rx / rn, ry_ / rn, rz / rn
            sx = p12[i, 0] - p24[i, 0]
            sy = p12[i, 1] - p24[i, 1]
            sz_ = p12[i, 2] - p24[i, 2]
            fx = ry_ * sz_ - rz * sy
            fy = rz * sx - rx * sz_
            fz = rx * sy - ry_ * sx
            fn = (fx * fx + fy * fy + fz * fz) ** 0.5
            fx, fy, fz = fx / fn, fy / fn, fz / fn
            ux = fy * rz - fz * ry_
            uy = fz * rx - fx * rz
            uz = fx * ry_ - fy * rx
            v = fy
            if v > 1.0:
                v = 1.0
            elif v < -1.0:
                v = -1.0
            out[i, 0] = -np.arcsin(v) * DEG
            out[i, 1] = np.arctan2(fx, fz) * DEG
            out[i, 2] = np.arctan2(ry_, uy) * DEG

            for side in range(2):
                if side == 0:
                    ax = p14[i, 0] - p12[i, 0]
                    ay = p14[i, 1] - p12[i, 1]
                    az = p14[i, 2] - p12[i, 2]
                    bx = p16[i, 0] - p14[i, 0]
                    by = p16[i, 1] - p14[i, 1]
                    bz = p16[i, 2] - p14[i, 2]
                else:
                    ax = p13[i, 0] - p11[i, 0]
                    ay = p13[i, 1] - p11[i, 1]
                    az = p13[i, 2] - p11[i, 2]
                    bx = p15[i, 0] - p13[i, 0]
                    by = p15[i, 1] - p13[i, 1]
                    bz = p15[i, 2] - p13[i, 2]
                # to root basis
                m = -1.0 if side == 1 else 1.0
                ua0 = (rx * ax + ry_ * ay + rz * az) * m
                ua1 = ux * ax + uy * ay + uz * az
                ua2 = fx * ax + fy * ay + fz * az
                fa0 = (rx * bx + ry_ * by + rz * bz) * m
                fa1 = ux * bx + uy * by + uz * bz
                fa2 = fx * bx + fy * by + fz * bz
                an = (ua0 * ua0 + ua1 * ua1 + ua2 * ua2) ** 0.5
                a0, a1, a2 = ua0 / an, ua1 / an, ua2 / an
                v = a1
                if v > 1.0:
                    v = 1.0
                elif v < -1.0:
                    v = -1.0
                th_z = np.arcsin(v)
                if 1.0 - abs(v) < GIMBAL_EPS:
                    th_y = 0.0
                else:
                    th_y = np.arctan2(-a2, a0)
                cy = np.cos(th_y)
                sy2 = np.sin(th_y)
                v0 = cy * fa0 - sy2 * fa2
                v1 = fa1
                v2 = sy2 * fa0 + cy * fa2
                cz = np.cos(th_z)
                szn = np.sin(th_z)
                f0 = cz * v0 + szn * v1
                f1 = -szn * v0 + cz * v1
                f2 = v2
                perp = (f1 * f1 + f2 * f2) ** 0.5
                fnorm = (fa0 * fa0 + fa1 * fa1 + fa2 * fa2) ** 0.5
                if perp >= TWIST_EPS * fnorm:
                    th_t = np.arctan2(-f1, f2)
                else:
                    th_t = 0.0
                ct = np.cos(th_t)
                st = np.sin(th_t)
                g0 = f0
                g1 = ct * f1 + st * f2
                g2 = -st * f1 + ct * f2
                gn = (g0 * g0 + g1 * g1 + g2 * g2) ** 0.5
                v = g1 / gn
                if v > 1.0:
                    v = 1.0
                elif v < -1.0:
                    v = -1.0
                e_z = np.arcsin(v)
                e_y = np.arctan2(-g2 / gn, g0 / gn)
                off = 3 + side * 5
                out[i, off + 0] = th_y * DEG
                out[i, off + 1] = th_z * DEG
                out[i, off + 2] = th_t * DEG
                out[i, off + 3] = e_y * DEG
                out[i, off + 4] = e_z * DEG

    return kern


# ------------------------------------------------------------- timing

def timeit(fn, repeats, warmup=3):
    for _ in range(warmup):
        fn()
    ts = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t0)
    return float(np.median(ts))


def bench_solvers(sizes):
    import sys
    sys.path.insert(0, str(HERE))                  # shoulder_vec (this dir)
    sys.path.insert(0, str(ROOT / "kinematics"))   # scalar reference
    from root_frame import build_root_frame, euler_unity_zxy
    from shoulder import solve_left_arm, solve_right_arm
    from shoulder_vec import solve_all_vec

    rows = []
    data_max = load_landmarks(max(sizes))

    # --- verify the generic closed-form solve against shoulder_vec once
    ref, rok_ref, lok_ref = solve_all_vec(*load_landmarks(899))
    got, rok_g, lok_g = solve_all_generic(np, *load_landmarks(899))
    ref = np.where(np.isnan(ref), 0.0, ref)  # vec keeps th_t via t_eff: none NaN
    d = np.max(np.abs(got - ref))
    assert d < 1e-10, f"generic solve deviates {d}"
    assert np.array_equal(rok_g, rok_ref) and np.array_equal(lok_g, lok_ref)
    print(f"[verify] generic closed-form == shoulder_vec: max delta {d:.2e} deg")

    # numba
    try:
        kern = make_numba_kernel()
        d8 = load_landmarks(899)
        out = np.empty((899, 13))
        kern(*d8, out)
        dn = np.max(np.abs(out - ref))
        assert dn < 1e-10, f"numba deviates {dn}"
        print(f"[verify] numba kernel == reference: max delta {dn:.2e} deg")
    except Exception as e:  # pragma: no cover
        kern = None
        print(f"[skip] numba: {e}")

    # cupy
    try:
        import cupy as cp
        got_g, _, _ = solve_all_generic(cp, *[cp.asarray(a) for a in load_landmarks(899)])
        dg = float(cp.max(cp.abs(got_g - cp.asarray(ref))))
        assert dg < 1e-9, f"cupy deviates {dg}"
        print(f"[verify] cupy == reference: max delta {dg:.2e} deg")
    except Exception as e:
        cp = None
        print(f"[skip] cupy: {e}")

    # torch
    try:
        import torch
        tdev = "cuda" if torch.cuda.is_available() else None
        tt = [torch.from_numpy(a) for a in load_landmarks(899)]
        got_t, _, _ = solve_all_generic(torch, *tt)
        dt = float((got_t - torch.from_numpy(ref)).abs().max())
        assert dt < 1e-9, f"torch deviates {dt}"
        print(f"[verify] torch == reference: max delta {dt:.2e} deg "
              f"(cuda {'available' if tdev else 'UNAVAILABLE'})")
    except Exception as e:
        torch = None
        tdev = None
        print(f"[skip] torch: {e}")

    from concurrent.futures import ThreadPoolExecutor
    pool = ThreadPoolExecutor(2)

    for n in sizes:
        data = [a[:n] for a in data_max]
        reps = max(5, min(200, int(2e6 / max(n, 1))))

        # scalar reference loop (cap the size — O(n) python)
        if n <= 10000:
            def scalar():
                for i in range(n):
                    Rr = build_root_frame(data[0][i], data[1][i], data[3][i])
                    euler_unity_zxy(Rr)
                    solve_right_arm(data[3][i], data[5][i], data[7][i], Rr)
                    solve_left_arm(data[2][i], data[4][i], data[6][i], Rr)
            rows.append(("scalar-loop", n, timeit(scalar, max(3, reps // 20))))

        rows.append(("numpy-vec", n,
                     timeit(lambda: solve_all_generic(np, *data), reps)))

        # L/R arms in 2 threads (root on the main thread, then split)
        def threaded():
            from root_frame import normalize
            r = normalize(data[1] - data[0])
            s = data[3] - data[1]
            f = normalize(np.cross(r, s))
            u = np.cross(f, r)
            R_root = np.stack([r, u, f], -1)
            fut_r = pool.submit(_arm_np, data[3], data[5], data[7], R_root, False)
            fut_l = pool.submit(_arm_np, data[2], data[4], data[6], R_root, True)
            fut_r.result(), fut_l.result()
        rows.append(("numpy+2threads-LR", n, timeit(threaded, reps)))

        if kern is not None:
            out = np.empty((n, 13))
            rows.append(("numba-njit", n,
                         timeit(lambda: kern(*data, out), reps)))

        if cp is not None:
            def cupy_xfer():
                dd = [cp.asarray(a) for a in data]
                o, _, _ = solve_all_generic(cp, *dd)
                cp.asnumpy(o)
            rows.append(("cupy+transfer", n, timeit(cupy_xfer, reps)))
            dd = [cp.asarray(a) for a in data]

            def cupy_res():
                solve_all_generic(cp, *dd)
                cp.cuda.runtime.deviceSynchronize()
            rows.append(("cupy-resident", n, timeit(cupy_res, reps)))

        if torch is not None and tdev:
            def torch_xfer():
                dd = [torch.from_numpy(a).to(tdev) for a in data]
                o, _, _ = solve_all_generic(torch, *dd)
                o.cpu().numpy()
            rows.append(("torch-cuda+transfer", n, timeit(torch_xfer, reps)))
            dd = [torch.from_numpy(a).to(tdev) for a in data]

            def torch_res():
                solve_all_generic(torch, *dd)
                torch.cuda.synchronize()
            rows.append(("torch-cuda-resident", n, timeit(torch_res, reps)))
        if torch is not None:
            tt = [torch.from_numpy(a) for a in data]
            rows.append(("torch-cpu", n,
                         timeit(lambda: solve_all_generic(torch, *tt), reps)))

        done = {r[0] for r in rows if r[1] == n}
        print(f"[bench] N={n}: " + ", ".join(
            f"{name} {t*1e6/max(n,1):.2f} us/fr"
            for name, nn, t in rows if nn == n))
    pool.shutdown()
    return pd.DataFrame(rows, columns=["impl", "n", "seconds"])


def _arm_np(psh, pel, pwr, R_root, mirror):
    """Single-arm numpy solve used by the threaded variant."""
    def dot(a, b):
        return (a * b).sum(-1)
    r, u, f = R_root[..., 0], R_root[..., 1], R_root[..., 2]

    def to_root(v):
        out = np.stack([dot(r, v), dot(u, v), dot(f, v)], -1)
        if mirror:
            out[:, 0] = -out[:, 0]
        return out
    su = to_root(pel - psh)
    sf = to_root(pwr - pel)
    a = su / np.sqrt(dot(su, su))[:, None]
    sz = np.clip(a[:, 1], -1, 1)
    th_z = np.arcsin(sz)
    th_y = np.where(1 - np.abs(sz) < GIMBAL_EPS, 0.0,
                    np.arctan2(-a[:, 2], a[:, 0]))
    cy, sy = np.cos(th_y), np.sin(th_y)
    v0 = cy * sf[:, 0] - sy * sf[:, 2]
    v1 = sf[:, 1]
    v2 = sy * sf[:, 0] + cy * sf[:, 2]
    cz, szn = np.cos(th_z), np.sin(th_z)
    f0, f1, f2 = cz * v0 + szn * v1, -szn * v0 + cz * v1, v2
    perp = np.hypot(f1, f2)
    ok = perp >= TWIST_EPS * np.sqrt(dot(sf, sf))
    th_t = np.where(ok, np.arctan2(-f1, f2), 0.0)
    ct, st = np.cos(th_t), np.sin(th_t)
    g0, g1, g2 = f0, ct * f1 + st * f2, -st * f1 + ct * f2
    gn = np.sqrt(g0 * g0 + g1 * g1 + g2 * g2)
    return (th_y, th_z, th_t, np.arctan2(-g2 / gn, g0 / gn),
            np.arcsin(np.clip(g1 / gn, -1, 1)), ok)


# ------------------------------------------------------------- aruco bench

def bench_aruco(n_frames=60):
    """detectMarkers + IPPE per frame on real bag frames: serial vs threads."""
    import cv2
    import pyrealsense2 as rs
    from concurrent.futures import ThreadPoolExecutor

    bag = ROOT / "Video/recording_20260224_083945.bag"
    if not bag.exists():
        print("[skip] aruco bench: bag not found")
        return None
    pipeline = rs.pipeline()
    cfg = rs.config()
    cfg.enable_device_from_file(str(bag), repeat_playback=False)
    profile = pipeline.start(cfg)
    profile.get_device().as_playback().set_real_time(False)
    frames_bgr = []
    intr = None
    try:
        while len(frames_bgr) < n_frames:
            fs = pipeline.wait_for_frames(timeout_ms=5000)
            c = fs.get_color_frame()
            if not c:
                continue
            if intr is None:
                intr = c.profile.as_video_stream_profile().intrinsics
            frames_bgr.append(np.asanyarray(c.get_data()).copy())
    finally:
        pipeline.stop()

    K = np.array([[intr.fx, 0, intr.ppx], [0, intr.fy, intr.ppy], [0, 0, 1]])
    dist = np.array(intr.coeffs[:5], float)
    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
    par = cv2.aruco.DetectorParameters()
    par.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_APRILTAG
    det = cv2.aruco.ArucoDetector(d, par)
    SIZES = {0: 0.150, 1: 0.050, 2: 0.050}

    def obj_pts(size):
        h = size / 2
        return np.array([[-h, h, 0], [h, h, 0], [h, -h, 0], [-h, -h, 0]],
                        dtype=np.float32)

    def pnp(corners, mid):
        cv2.solvePnPGeneric(obj_pts(SIZES[mid]), corners, K, dist,
                            flags=cv2.SOLVEPNP_IPPE_SQUARE)

    def process(img, pnp_pool=None):
        corners, ids, _ = det.detectMarkers(img)
        if ids is None:
            return
        jobs = [(c.reshape(4, 2), int(i)) for c, i in zip(corners, ids.ravel())
                if int(i) in SIZES]
        if pnp_pool is None:
            for c, i in jobs:
                pnp(c, i)
        else:
            list(pnp_pool.map(lambda ji: pnp(*ji), jobs))

    res = {}
    t = timeit(lambda: [process(f) for f in frames_bgr], 5)
    res["serial"] = t / len(frames_bgr)

    with ThreadPoolExecutor(3) as pp:
        t = timeit(lambda: [process(f, pp) for f in frames_bgr], 5)
        res["pnp-3threads"] = t / len(frames_bgr)

    with ThreadPoolExecutor(2) as fp:
        t = timeit(lambda: list(fp.map(process, frames_bgr)), 5)
        res["frames-2threads"] = t / len(frames_bgr)

    print("[aruco] per-frame ms: " +
          ", ".join(f"{k} {v*1e3:.2f}" for k, v in res.items()))
    return res


# ------------------------------------------------------------- plotting

INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
SURFACE = "#fcfcfb"
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # categorical slots 1-4


def plot(df, aruco, out_png):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), facecolor=SURFACE)
    for ax in axes:
        ax.set_facecolor(SURFACE)
        for sp in ("top", "right"):
            ax.spines[sp].set_visible(False)
        for sp in ("left", "bottom"):
            ax.spines[sp].set_color(GRID)
        ax.tick_params(colors=MUTED, labelsize=9)
        ax.grid(True, color=GRID, linewidth=0.8, alpha=0.7)
        ax.set_axisbelow(True)

    # (1) per-frame latency at N=1 — single-hue bars (magnitude compare)
    ax = axes[0]
    d1 = df[df.n == 1].sort_values("seconds")
    y = np.arange(len(d1))
    ax.barh(y, d1.seconds * 1e6, color=C[0], height=0.62)
    ax.set_yticks(y, d1.impl, fontsize=9, color=INK)
    ax.set_xscale("log")
    ax.set_xlabel("per-frame latency at N = 1 (µs, log)", color=MUTED, fontsize=9)
    ax.set_title("Real-time case: one frame at a time",
                 color=INK, fontsize=10, loc="left")
    for yi, v in zip(y, d1.seconds * 1e6):
        ax.text(v * 1.15, yi, f"{v:,.0f}", va="center", fontsize=8, color=INK)
    ax.invert_yaxis()

    # (2) CPU arms vs batch size
    ax = axes[1]
    cpu = ["numpy-vec", "numpy+2threads-LR", "numba-njit", "scalar-loop"]
    for i, impl in enumerate(cpu):
        dd = df[df.impl == impl].sort_values("n")
        if not len(dd):
            continue
        ax.plot(dd.n, dd.seconds / dd.n * 1e6, color=C[i], lw=2,
                marker="o", ms=4, label=impl)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("batch size N (frames)", color=MUTED, fontsize=9)
    ax.set_ylabel("µs per frame (log)", color=MUTED, fontsize=9)
    ax.set_title("CPU implementations", color=INK, fontsize=10, loc="left")
    ax.legend(fontsize=8, frameon=False, labelcolor=INK)

    # (3) GPU arms vs batch size (+ numpy-vec as the CPU baseline)
    ax = axes[2]
    gpu = ["cupy+transfer", "cupy-resident", "torch-cuda+transfer",
           "torch-cuda-resident"]
    styles = ["-", "--", "-", "--"]
    cols = [C[1], C[1], C[2], C[2]]
    dd = df[df.impl == "numpy-vec"].sort_values("n")
    ax.plot(dd.n, dd.seconds / dd.n * 1e6, color=C[0], lw=2, marker="o",
            ms=4, label="numpy-vec (CPU baseline)")
    for impl, stl, col in zip(gpu, styles, cols):
        dd = df[df.impl == impl].sort_values("n")
        if not len(dd):
            continue
        ax.plot(dd.n, dd.seconds / dd.n * 1e6, color=col, lw=2, ls=stl,
                marker="o", ms=4, label=impl)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("batch size N (frames)", color=MUTED, fontsize=9)
    ax.set_ylabel("µs per frame (log)", color=MUTED, fontsize=9)
    ax.set_title("GPU vs the CPU baseline", color=INK, fontsize=10, loc="left")
    ax.legend(fontsize=8, frameon=False, labelcolor=INK)

    note = ""
    if aruco:
        note = ("ArUco stage (detect+IPPE, ms/frame): " +
                ", ".join(f"{k} {v*1e3:.2f}" for k, v in aruco.items()))
    fig.suptitle("13-angle kinematic solve — implementation benchmark",
                 color=INK, fontsize=12, x=0.01, ha="left")
    if note:
        fig.text(0.01, 0.005, note, color=MUTED, fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    fig.savefig(out_png, dpi=150, facecolor=SURFACE)
    print(f"[plot] {out_png}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+",
                    default=[1, 10, 100, 1000, 10000, 100000])
    ap.add_argument("--no-aruco", action="store_true")
    ap.add_argument("--out", default=str(HERE.parent / "output/bench_solver"))
    args = ap.parse_args()

    df = bench_solvers(args.sizes)
    aruco = None if args.no_aruco else bench_aruco()

    out = Path(args.out)
    out.parent.mkdir(exist_ok=True)
    rows = df.copy()
    rows["us_per_frame"] = rows.seconds / rows.n * 1e6
    if aruco:
        for k, v in aruco.items():
            rows = pd.concat([rows, pd.DataFrame(
                [{"impl": f"aruco-{k}", "n": 1, "seconds": v,
                  "us_per_frame": v * 1e6}])], ignore_index=True)
    rows.to_csv(f"{out}.csv", index=False)
    print(f"[csv] {out}.csv")
    plot(df, aruco, f"{out}.png")

    # conclusion
    n1 = rows[rows.n == 1].set_index("impl").us_per_frame
    print("\n=== conclusion (N=1, the real-time case) ===")
    for k in n1.sort_values().index:
        print(f"  {k:24s} {n1[k]:12,.1f} us/frame")


if __name__ == "__main__":
    main()
