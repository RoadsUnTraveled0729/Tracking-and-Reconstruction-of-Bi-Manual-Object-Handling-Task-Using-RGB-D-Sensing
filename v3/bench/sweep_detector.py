#!/usr/bin/env python3
"""Detector sweep: det_freq {5, 15, 30} x named model variants.

Variants come from configs/model_variants.json (--pose-variants, D-023);
the default pair rtmpose-m (YOLOX-tiny) and rtmpose-m_yolox-m reproduces
the original D-016 sweep over YOLOX {tiny, m}.

Closes the two UNCERTAIN halves of D-008: is det_freq 15 justified,
and does YOLOX-tiny's box hold up against yolox-m? Non-paced playback
(deterministic coverage; the detector-stage latency distribution does
not depend on arrival pacing), warmup excluded per bench.json.

Reported per combination:
  found        frames with a person / total
  det_pct      frames that ran detection (scheduled + triggers)
  lat p50/p99  detector-stage per-frame latency, ms, post-warmup
  score_med    median over frames of the eight-landmark mean score
  box_step_p95 p95 of per-frame pose-box center step, px (stability;
               lower = steadier crop between consecutive frames)

Run under env v3rt (CUDA libs on LD_LIBRARY_PATH).
"""
import argparse
import json
import sys
import time
from pathlib import Path

V3_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V3_ROOT.parent
sys.path.insert(0, str(V3_ROOT))

def run_combo(cfg, bag, det_freq, variant, device, warmup, variants):
    import numpy as np
    from core.skeleton import COCO_IDX
    from detector.factory import apply_variant, build_detector
    from replay.bag_source import BagSource

    cfg = apply_variant(cfg, variant, variants)
    cfg["detect"]["det_freq"] = det_freq

    src = BagSource(bag, paced=False)
    det = build_detector(cfg, str(REPO_ROOT),
                         img_wh=(src.intrinsics.width,
                                 src.intrinsics.height),
                         device=device,
                         key_indices=sorted(COCO_IDX.values()))
    lat, scores, centers = [], [], []
    n = found = det_runs = 0
    for idx, t_s, color, depth in src.frames():
        t0 = time.perf_counter()
        kp, sc, diag = det(color)
        lat.append((time.perf_counter() - t0) * 1000)
        det_runs += int(diag["det_ran"])
        if kp is not None:
            found += 1
            scores.append(float(np.mean(sc[5:13])))
            box = diag["box"]
            if box is not None:
                centers.append([(box[0] + box[2]) / 2,
                                (box[1] + box[3]) / 2])
        n += 1
    src.close()

    lat = np.asarray(lat)[warmup:]
    steps = np.linalg.norm(np.diff(np.asarray(centers), axis=0), axis=1)
    return {
        "det_freq": det_freq, "variant": variant,
        "found": found, "frames": n,
        "det_pct": 100.0 * det_runs / max(1, n),
        "p50": float(np.percentile(lat, 50)),
        "p99": float(np.percentile(lat, 99)),
        "max": float(lat.max()),
        "score_med": float(np.median(scores)),
        "box_step_p95": float(np.percentile(steps, 95)),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(V3_ROOT / "configs/default.json"))
    ap.add_argument("--bag", default=None)
    ap.add_argument("--det-freqs", default="5,15,30")
    ap.add_argument("--pose-variants", default="rtmpose-m,rtmpose-m_yolox-m",
                    help="comma-separated names from configs/"
                         "model_variants.json; each file is hash-checked "
                         "before its run")
    ap.add_argument("--device", default="cuda", choices=("cuda", "cpu"))
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text())
    if args.device == "cuda":
        from detector.rtmpose_detector import ensure_cuda_env
        ensure_cuda_env(cfg["model"].get("cuda_lib_dirs"))

    from detector.factory import load_variants, verify_variant_files
    variants = load_variants()
    names = args.pose_variants.split(",")
    for name in names:
        if name not in variants:
            raise SystemExit(f"unknown variant {name!r}; known: "
                             f"{sorted(variants)}")
        verify_variant_files(name, REPO_ROOT, variants)

    bag = args.bag or cfg["paths"]["bag"]
    warmup = json.loads((V3_ROOT / "configs/bench.json").read_text())[
        "latency"]["warmup_frames"]

    print(f"bag: {bag}")
    print(f"warmup excluded: {warmup} frames; non-paced playback; "
          f"device {args.device}")
    w = max(len(n) for n in names)
    print(f"{'freq':>4} {'variant':>{w}} {'found':>9} {'det_pct':>7} "
          f"{'p50':>6} {'p99':>6} {'max':>7} {'score':>6} {'boxstep':>8}")
    for variant in names:
        for det_freq in (int(v) for v in args.det_freqs.split(",")):
            r = run_combo(cfg, bag, det_freq, variant, args.device, warmup,
                          variants)
            print(f"{r['det_freq']:>4} {r['variant']:>{w}} "
                  f"{r['found']:>4}/{r['frames']:<4} "
                  f"{r['det_pct']:>6.1f} {r['p50']:>6.2f} {r['p99']:>6.2f} "
                  f"{r['max']:>7.2f} {r['score_med']:>6.3f} "
                  f"{r['box_step_p95']:>8.2f}")


if __name__ == "__main__":
    main()
