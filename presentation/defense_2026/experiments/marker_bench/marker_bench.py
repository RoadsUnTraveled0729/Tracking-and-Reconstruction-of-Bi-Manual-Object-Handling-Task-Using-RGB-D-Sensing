"""ArUco vs AprilTag detector benchmark on real background frames.

Synthetic markers with known corners are composited onto real 640x480
frames of the R6b recording, degraded with blur and noise, and passed
to three detector configurations (four runs):

  aruco_5x5        OpenCV ArucoDetector, DICT_5X5_50, pinned settings
                   (default DetectorParameters + CORNER_REFINE_APRILTAG,
                   as v1/aruco/extract_aruco_poses.py) on a 5x5 marker
  cv_apriltag36h11 the same OpenCV detector with DICT_APRILTAG_36h11
                   on a tag36h11 marker (dictionary swap, same detector)
  pupil_dec2       pupil-apriltags (AprilTag 3 C library), tag36h11,
                   library defaults (quad_decimate 2.0)
  pupil_dec1       pupil-apriltags, tag36h11, quad_decimate 1.0

Every constant is documented in presentation/defense_2026/DECISIONS.md D-134 to D-148.

Usage:
  python marker_bench.py                 # full run (writes results)
  python marker_bench.py --quick         # small smoke run, no outputs
  python marker_bench.py --plot-only     # redraw chart from results.csv
"""
import argparse
import csv
import json
import os
import platform
import sys
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import numpy as np  # noqa: E402
import cv2  # noqa: E402

HERE = Path(__file__).resolve().parent
FRAME_DIR = Path("/tmp/defense_2026_causal/camera")

# ---- constants (sources in presentation/defense_2026/DECISIONS.md D-134 to D-148) ----
SEED = 20260928
N_FRAMES = 50
SIZES_PX = [24, 32, 48, 64, 96, 128]
TILTS_DEG = [0, 30, 45]
BLUR_SIGMAS = [0.0, 0.8, 1.5]
NOISE_SIGMAS = [0.0, 4.0, 8.0]
TIMING_REPS = 3            # timed detections per image and detector
WARMUP_DETECTIONS = 20     # per detector, excluded from timing
FOCAL_PX = 607.56          # fx of the D435 colour stream, 640x480
SUPERSAMPLE = 4            # render at 4x then INTER_AREA downsample
PASTE_BOX = 240            # square region reserved for the pasted marker
REAL_MARKER_MARGIN = 12    # px kept free around every real marker
MATCH_RADIUS_FRAC = 0.5    # centroid gate, fraction of target side
MARKER_ID = 1
CPU_CORE = 2               # process pinned to this logical core

DETECTORS = ["aruco_5x5", "cv_apriltag36h11", "pupil_dec2", "pupil_dec1",
             "aruco_5x5_norefine"]
MAIN_DETECTORS = DETECTORS[:4]   # the norefine run is a timing reference
LABELS = {
    "aruco_5x5": "OpenCV ArUco, DICT_5X5_50 (pinned)",
    "cv_apriltag36h11": "OpenCV ArUco detector, DICT_APRILTAG_36h11",
    "pupil_dec2": "AprilTag 3 (pupil-apriltags), decimate 2",
    "pupil_dec1": "AprilTag 3 (pupil-apriltags), decimate 1",
    "aruco_5x5_norefine": "OpenCV ArUco, DICT_5X5_50, default (no refine)",
}


def pinned_params():
    p = cv2.aruco.DetectorParameters()
    p.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_APRILTAG
    return p


def make_detectors():
    import pupil_apriltags as pa
    d = {
        "aruco_5x5": cv2.aruco.ArucoDetector(
            cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50),
            pinned_params()),
        "cv_apriltag36h11": cv2.aruco.ArucoDetector(
            cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11),
            pinned_params()),
        "aruco_5x5_norefine": cv2.aruco.ArucoDetector(
            cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50),
            cv2.aruco.DetectorParameters()),
        "pupil_dec2": pa.Detector(families="tag36h11", nthreads=1),
        "pupil_dec1": pa.Detector(families="tag36h11", nthreads=1,
                                  quad_decimate=1.0),
    }
    return d


def run_detector(name, det, gray):
    """Return list of (id, corners 4x2 float64) and elapsed seconds."""
    if name.startswith("pupil"):
        t0 = time.perf_counter()
        res = det.detect(gray)
        dt = time.perf_counter() - t0
        out = [(r.tag_id, np.asarray(r.corners, dtype=np.float64))
               for r in res]
    else:
        t0 = time.perf_counter()
        corners, ids, _ = det.detectMarkers(gray)
        dt = time.perf_counter() - t0
        out = []
        if ids is not None:
            for c, i in zip(corners, ids.ravel()):
                out.append((int(i), c.reshape(4, 2).astype(np.float64)))
    return out, dt


# ---------------- rendering ----------------

def marker_canvas(kind, module_px=32):
    """Marker image (black square with data) plus one-module white quiet
    zone. Returns image and the black-square side in canvas pixels and
    its offset in the canvas."""
    if kind == "aruco":
        dic = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)
        n_mod = 7
    else:
        dic = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_36h11)
        n_mod = 8
    side = n_mod * module_px
    img = cv2.aruco.generateImageMarker(dic, MARKER_ID, side, borderBits=1)
    canvas = np.full((side + 2 * module_px, side + 2 * module_px), 255,
                     np.uint8)
    canvas[module_px:module_px + side, module_px:module_px + side] = img
    return canvas, side, module_px


def true_corners(center, side_px, tilt_deg, roll_deg):
    """Projected outer black-square corners (TL, TR, BR, BL in the marker
    frame) in output pixel-centre coordinates. The marker (side S) sits
    at depth Z = f*S/side_px, is tilted about its vertical axis by
    tilt_deg and rolled in-plane by roll_deg."""
    S = 1.0
    Z = FOCAL_PX * S / side_px
    h = S / 2.0
    P = np.array([[-h, -h, 0], [h, -h, 0], [h, h, 0], [-h, h, 0]], float)
    t = np.deg2rad(tilt_deg)
    r = np.deg2rad(roll_deg)
    Ry = np.array([[np.cos(t), 0, np.sin(t)], [0, 1, 0],
                   [-np.sin(t), 0, np.cos(t)]])
    Rz = np.array([[np.cos(r), -np.sin(r), 0], [np.sin(r), np.cos(r), 0],
                   [0, 0, 1]])
    X = (Rz @ Ry @ P.T).T + np.array([0, 0, Z])
    uv = FOCAL_PX * X[:, :2] / X[:, 2:3]
    return uv + np.asarray(center, float)


def composite(bg_gray, kind, corners_out, levels):
    """Warp the marker so its black-square outer corners land on
    corners_out (pixel-centre convention) and paste onto bg_gray."""
    canvas, side, off = marker_canvas(kind)
    k = SUPERSAMPLE
    # outer edges of the black square in canvas pixel-centre coords
    src_sq = np.array([[off - 0.5, off - 0.5], [off + side - 0.5, off - 0.5],
                       [off + side - 0.5, off + side - 0.5],
                       [off - 0.5, off + side - 0.5]], np.float64)
    # working crop in output coords
    x0 = int(np.floor(corners_out[:, 0].min())) - 40
    y0 = int(np.floor(corners_out[:, 1].min())) - 40
    x1 = int(np.ceil(corners_out[:, 0].max())) + 40
    y1 = int(np.ceil(corners_out[:, 1].max())) + 40
    W, H = x1 - x0, y1 - y0
    # output coord x_out -> supersampled coord x_ss = k*(x_out-x0)+(k-1)/2
    dst_ss = k * (corners_out - np.array([x0, y0])) + (k - 1) / 2.0
    Hm = cv2.getPerspectiveTransform(src_sq.astype(np.float32),
                                     dst_ss.astype(np.float32))
    lo, hi = levels
    tex = (lo + (hi - lo) * (canvas.astype(np.float32) / 255.0))
    warped = cv2.warpPerspective(tex, Hm, (W * k, H * k),
                                 flags=cv2.INTER_LINEAR,
                                 borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    alpha = cv2.warpPerspective(np.ones_like(tex), Hm, (W * k, H * k),
                                flags=cv2.INTER_LINEAR,
                                borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    warped = cv2.resize(warped, (W, H), interpolation=cv2.INTER_AREA)
    alpha = cv2.resize(alpha, (W, H), interpolation=cv2.INTER_AREA)
    # pad so that the working crop never leaves the frame (only the
    # zero-alpha margin of the crop can extend past the border)
    P = max(0, -x0, -y0, x1 - bg_gray.shape[1], y1 - bg_gray.shape[0])
    out = np.pad(bg_gray.astype(np.float32), P, mode="edge")
    region = out[y0 + P:y1 + P, x0 + P:x1 + P]
    region[:] = alpha * warped + (1 - alpha) * region
    return out[P:P + bg_gray.shape[0], P:P + bg_gray.shape[1]].copy()


def degrade(img_f32, blur_sigma, noise_sigma, rng):
    if blur_sigma > 0:
        img_f32 = cv2.GaussianBlur(img_f32, (0, 0), blur_sigma)
    if noise_sigma > 0:
        img_f32 = img_f32 + rng.normal(0.0, noise_sigma, img_f32.shape)
    return np.clip(np.rint(img_f32), 0, 255).astype(np.uint8)


# ---------------- scene preparation ----------------

def real_marker_quads(gray):
    det = cv2.aruco.ArucoDetector(
        cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50),
        pinned_params())
    corners, ids, _ = det.detectMarkers(gray)
    return [] if ids is None else [c.reshape(4, 2) for c in corners]


def measure_levels(frames):
    """Dark/bright grey levels of the real printed markers (10th and 90th
    percentile inside each detected real marker quad, median over all)."""
    lo, hi = [], []
    for g in frames:
        for q in real_marker_quads(g):
            m = np.zeros(g.shape, np.uint8)
            cv2.fillConvexPoly(m, np.rint(q).astype(np.int32), 1)
            v = g[m > 0]
            if v.size > 50:
                lo.append(np.percentile(v, 10))
                hi.append(np.percentile(v, 90))
    return float(np.median(lo)), float(np.median(hi)), len(lo)


def choose_frames_and_boxes(rng):
    paths = sorted(FRAME_DIR.glob("cam_*.jpg"))
    order = rng.permutation(len(paths))
    chosen = []
    for idx in order:
        g = cv2.imread(str(paths[idx]), cv2.IMREAD_GRAYSCALE)
        quads = real_marker_quads(g)
        boxes = []
        for q in quads:
            boxes.append((q[:, 0].min() - REAL_MARKER_MARGIN,
                          q[:, 1].min() - REAL_MARKER_MARGIN,
                          q[:, 0].max() + REAL_MARKER_MARGIN,
                          q[:, 1].max() + REAL_MARKER_MARGIN))
        Hh, Ww = g.shape
        ok = None
        for _ in range(200):
            cx = rng.uniform(PASTE_BOX / 2, Ww - PASTE_BOX / 2)
            cy = rng.uniform(PASTE_BOX / 2, Hh - PASTE_BOX / 2)
            bx = (cx - PASTE_BOX / 2, cy - PASTE_BOX / 2,
                  cx + PASTE_BOX / 2, cy + PASTE_BOX / 2)
            if all(bx[2] < b[0] or bx[0] > b[2] or bx[3] < b[1] or bx[1] > b[3]
                   for b in boxes):
                ok = (cx, cy)
                break
        if ok is None:
            continue
        roll = rng.uniform(0.0, 90.0)
        chosen.append(dict(path=paths[idx], gray=g, center=ok, roll=roll,
                           n_real=len(quads)))
        if len(chosen) == N_FRAMES:
            break
    return chosen


# ---------------- metrics ----------------

def corner_error(det_c, true_c):
    """Signed corner differences (4x2, detected - true), taking the corner
    ordering (cyclic shift and winding direction) that minimises the mean
    Euclidean error, because the libraries use different conventions."""
    best, best_e = None, None
    for cand in (det_c, det_c[::-1]):
        for s in range(4):
            d = np.roll(cand, s, axis=0) - true_c
            e = np.linalg.norm(d, axis=1).mean()
            if best is None or e < best_e:
                best, best_e = d, e
    return best


def match(dets, true_c, side_px, want_id):
    """The detection of want_id closest to the true centroid, within the
    gate, else None. Also returns the number of other detections."""
    tc = true_c.mean(axis=0)
    hit, others = None, 0
    for i, c in dets:
        d = np.linalg.norm(c.mean(axis=0) - tc)
        if i == want_id and d < MATCH_RADIUS_FRAC * side_px and hit is None:
            hit = c
        else:
            others += 1
    return hit, others


# ---------------- main ----------------

def environment(levels, n_level_markers, chosen):
    cpu = "unknown"
    with open("/proc/cpuinfo") as f:
        for line in f:
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    import pupil_apriltags
    try:
        from importlib.metadata import version
        pv = version("pupil-apriltags")
    except Exception:
        pv = getattr(pupil_apriltags, "__version__", "unknown")
    return {
        "cpu": cpu,
        "logical_cpus": os.cpu_count(),
        "affinity": sorted(os.sched_getaffinity(0)),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "opencv": cv2.__version__,
        "numpy": np.__version__,
        "pupil_apriltags": pv,
        "cv2_num_threads": cv2.getNumThreads(),
        "pupil_nthreads": 1,
        "loadavg_start": os.getloadavg(),
        "seed": SEED,
        "frames_dir": str(FRAME_DIR),
        "frames_used": [c["path"].name for c in chosen],
        "real_markers_per_used_frame": [c["n_real"] for c in chosen],
        "marker_grey_levels_lo_hi": levels,
        "marker_grey_levels_from_n_real_markers": n_level_markers,
        "timing_input": "grayscale uint8 640x480; colour conversion excluded",
    }


def pct(a, q):
    return float(np.percentile(a, q)) if len(a) else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--plot-only", action="store_true")
    args = ap.parse_args()
    if args.plot_only:
        from plot_marker_bench import plot
        plot(HERE / "summary.csv", HERE / "chart_marker_bench.png")
        return

    try:
        os.sched_setaffinity(0, {CPU_CORE})
    except (AttributeError, OSError):
        pass
    cv2.setNumThreads(1)
    rng = np.random.default_rng(SEED)
    chosen = choose_frames_and_boxes(rng)
    lo, hi, n_lv = measure_levels([c["gray"] for c in chosen])
    levels = (lo, hi)
    print(f"[INFO] {len(chosen)} frames, marker grey levels {lo:.1f}/{hi:.1f}"
          f" from {n_lv} real markers")

    sizes, tilts, blurs, noises = SIZES_PX, TILTS_DEG, BLUR_SIGMAS, NOISE_SIGMAS
    frames = chosen
    reps = TIMING_REPS
    if args.quick:
        sizes, tilts, blurs, noises = [48, 128], [0, 45], [0.0], [0.0]
        frames = chosen[:5]
        reps = 1

    dets = make_detectors()
    # warm-up, excluded from timing
    g0 = frames[0]["gray"]
    for name in DETECTORS:
        for _ in range(WARMUP_DETECTIONS):
            run_detector(name, dets[name], g0)

    env = environment(levels, n_lv, chosen)
    rows = []
    t_start = time.time()
    n_cond = len(sizes) * len(tilts) * len(blurs) * len(noises)
    ci = 0
    for side in sizes:
        for tilt in tilts:
            for blur in blurs:
                for noise in noises:
                    ci += 1
                    acc = {n: dict(t=[], signed=[], hits=0, others=0)
                           for n in DETECTORS}
                    for fi, fr in enumerate(frames):
                        tc = true_corners(fr["center"], side, tilt, fr["roll"])
                        seed = (SEED, side, tilt, int(blur * 10),
                                int(noise), fi)
                        imgs = {}
                        for kind in ("aruco", "april"):
                            comp = composite(fr["gray"], kind, tc, levels)
                            imgs[kind] = degrade(
                                comp, blur, noise,
                                np.random.default_rng(list(seed)))
                        for rep in range(reps):
                            for name in DETECTORS:
                                img = imgs["aruco" if name.startswith("aruco")
                                           else "april"]
                                out, dt = run_detector(name, dets[name], img)
                                a = acc[name]
                                a["t"].append(dt * 1e3)
                                if rep == 0:
                                    hit, others = match(out, tc, side,
                                                        MARKER_ID)
                                    a["others"] += others
                                    if hit is not None:
                                        a["hits"] += 1
                                        a["signed"].append(
                                            corner_error(hit, tc))
                    for name in DETECTORS:
                        a = acc[name]
                        sg = (np.concatenate(a["signed"]) if a["signed"]
                              else np.zeros((0, 2)))
                        err = np.linalg.norm(sg, axis=1)
                        bias = sg.mean(axis=0) if len(sg) else \
                            np.array([np.nan, np.nan])
                        err_db = np.linalg.norm(sg - bias, axis=1)
                        rows.append(dict(
                            detector=name, side_px=side, tilt_deg=tilt,
                            blur_sigma=blur, noise_sigma=noise,
                            n_frames=len(frames),
                            detection_rate=a["hits"] / len(frames),
                            corner_err_mean_px=float(err.mean()) if err.size
                            else float("nan"),
                            corner_err_p95_px=pct(err, 95),
                            corner_bias_x_px=float(bias[0]),
                            corner_bias_y_px=float(bias[1]),
                            corner_err_debiased_mean_px=float(err_db.mean())
                            if err_db.size else float("nan"),
                            corner_err_debiased_p95_px=pct(err_db, 95),
                            time_median_ms=pct(a["t"], 50),
                            time_p95_ms=pct(a["t"], 95),
                            n_timings=len(a["t"]),
                            other_detections_per_frame=a["others"]
                            / len(frames)))
                    if ci % 9 == 0 or args.quick:
                        el = time.time() - t_start
                        print(f"[INFO] condition {ci}/{n_cond} "
                              f"elapsed {el:.0f} s", flush=True)
    wall = time.time() - t_start
    env["loadavg_end"] = os.getloadavg()
    env["wall_time_s"] = wall
    env["timing_reps_per_image"] = reps

    if args.quick:
        for r in rows:
            print({k: (round(v, 3) if isinstance(v, float) else v)
                   for k, v in r.items()})
        return

    keys = list(rows[0].keys())
    with open(HERE / "results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v)
                        for k, v in r.items()})
    write_summary(rows)
    with open(HERE / "environment.json", "w") as f:
        json.dump(env, f, indent=2)
    from plot_marker_bench import plot
    plot(HERE / "summary.csv", HERE / "chart_marker_bench.png")
    print(f"[INFO] done in {wall:.0f} s")


def write_summary(rows):
    """Per detector and size, aggregated over the 27 tilt x blur x noise
    conditions.
    - detection_rate: mean over conditions; detection_rate_min: worst one.
    - corner errors: mean over the conditions with at least one detection
      of the per-condition values (n_cond_detected says how many).
    - *_common: the same, restricted to the conditions in which all four
      main detectors reach detection rate >= 0.5 at this size, so detectors are
      compared on the same images.
    - time_median_ms / time_p95_ms: median across conditions of the
      per-condition median and p95 (each from n_frames x reps timings)."""
    out = []
    by = {}
    for r in rows:
        by[(r["detector"], r["side_px"], r["tilt_deg"], r["blur_sigma"],
            r["noise_sigma"])] = r

    def cond(r):
        return (r["tilt_deg"], r["blur_sigma"], r["noise_sigma"])

    for name in DETECTORS:
        for side in SIZES_PX:
            rs = [r for r in rows if r["detector"] == name
                  and r["side_px"] == side]
            if not rs:
                continue
            det = [r for r in rs if r["detection_rate"] > 0]
            common = [r for r in det if all(
                by[(n, side) + cond(r)]["detection_rate"] >= 0.5
                for n in MAIN_DETECTORS)]

            def m(lst, key):
                v = [x[key] for x in lst if not np.isnan(x[key])]
                return float(np.mean(v)) if v else float("nan")
            out.append(dict(
                detector=name, label=LABELS[name], side_px=side,
                n_conditions=len(rs), n_cond_detected=len(det),
                n_cond_common=len(common),
                detection_rate=float(np.mean([r["detection_rate"]
                                              for r in rs])),
                detection_rate_min=float(np.min([r["detection_rate"]
                                                 for r in rs])),
                time_median_ms=float(np.median([r["time_median_ms"]
                                                for r in rs])),
                time_p95_ms=float(np.median([r["time_p95_ms"] for r in rs])),
                corner_err_mean_px=m(det, "corner_err_mean_px"),
                corner_err_p95_px=m(det, "corner_err_p95_px"),
                corner_bias_x_px=m(det, "corner_bias_x_px"),
                corner_bias_y_px=m(det, "corner_bias_y_px"),
                corner_err_debiased_mean_px=m(det,
                                              "corner_err_debiased_mean_px"),
                corner_err_debiased_p95_px=m(det,
                                             "corner_err_debiased_p95_px"),
                corner_err_mean_px_common=m(common, "corner_err_mean_px"),
                corner_err_debiased_mean_px_common=m(
                    common, "corner_err_debiased_mean_px"),
                other_detections_per_frame=float(np.mean(
                    [r["other_detections_per_frame"] for r in rs]))))
    keys = list(out[0].keys())
    with open(HERE / "summary.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in out:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v)
                        for k, v in r.items()})


if __name__ == "__main__":
    main()
