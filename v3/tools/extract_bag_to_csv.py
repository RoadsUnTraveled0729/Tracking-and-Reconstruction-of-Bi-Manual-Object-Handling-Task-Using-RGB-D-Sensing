#!/usr/bin/env python3
"""V3 extraction: recorded .bag -> per-frame landmark CSV + meta.json.

The V3 counterpart of v1's mediapipe/extract_landmarks_to_csv.py:
RTMPose keypoints (scores, not visibility) + depth median +
deprojection, camera-frame meters, NO gating (scores and src codes
travel with every landmark; gate thresholds are fitted later from this
very file, D-006). This CSV is the substrate for the S-type scenarios,
the gate ROC, and the baseline grading.

Columns: frame, time_s, then per v1 landmark {name}_x/_y/_z (camera
frame, empty when no depth or out of frame), {name}_score, {name}_src
(0 ok, 2 no-depth, 3 out-of-frame), {name}_u, {name}_v; plus
det_ran, det_reasons (semicolon-joined), box_x0/y0/x1/y1.

Run under env v3rt:

    /home/luo/anaconda3/envs/v3rt/bin/python v3/tools/extract_bag_to_csv.py
"""
import argparse
import csv
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

V3_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V3_ROOT.parent
sys.path.insert(0, str(V3_ROOT))


def intrinsics_to_dict(i):
    return {"width": i.width, "height": i.height, "fx": i.fx, "fy": i.fy,
            "ppx": i.ppx, "ppy": i.ppy, "model": str(i.model),
            "coeffs": list(i.coeffs)}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(V3_ROOT / "configs/default.json"))
    ap.add_argument("--bag", default=None, help="default: config paths.bag")
    ap.add_argument("--variant", default=None,
                    help="named model variant from configs/"
                         "model_variants.json (default: config "
                         "model.variant); onnx hashes are verified "
                         "before the run (D-023)")
    ap.add_argument("--out-csv", default=None,
                    help="default: v3/output/extraction_<bagstem>__"
                         "<variant>.csv")
    ap.add_argument("--device", default="cuda", choices=("cuda", "cpu"))
    ap.add_argument("--max-frames", type=int, default=None)
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text())
    from detector.factory import apply_variant, verify_variant_files
    variant = args.variant or cfg["model"]["variant"]
    cfg = apply_variant(cfg, variant)
    if args.device == "cuda":
        from detector.rtmpose_detector import ensure_cuda_env
        ensure_cuda_env(cfg["model"].get("cuda_lib_dirs"))
    model_files = verify_variant_files(variant, REPO_ROOT)

    import numpy as np
    from core.skeleton import COCO_IDX, V1_LANDMARKS
    from detector.factory import build_detector
    from replay.bag_source import BagSource
    from replay.depth_sampler import lift_keypoints

    bag = args.bag or cfg["paths"]["bag"]
    out_csv = Path(args.out_csv) if args.out_csv else (
        V3_ROOT / "output"
        / f"extraction_{Path(bag).stem}__{variant}.csv")
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    src = BagSource(bag, paced=False)
    img_wh = (src.intrinsics.width, src.intrinsics.height)
    det = build_detector(cfg, str(REPO_ROOT), img_wh=img_wh,
                         device=args.device,
                         key_indices=sorted(COCO_IDX.values()))

    cols = ["frame", "time_s"]
    for n in V1_LANDMARKS:
        cols += [f"{n}_x", f"{n}_y", f"{n}_z", f"{n}_score", f"{n}_src",
                 f"{n}_u", f"{n}_v"]
    cols += ["det_ran", "det_reasons", "box_x0", "box_y0", "box_x1",
             "box_y1"]

    n_frames = found = det_runs = 0
    src_counts = {n: {2: 0, 3: 0} for n in V1_LANDMARKS}
    t_start = time.monotonic()
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for idx, t_s, color, depth in src.frames(args.max_frames):
            kp, sc, diag = det(color)
            det_runs += int(diag["det_ran"])
            row = [idx, f"{t_s:.6f}"]
            if kp is None:
                for n in V1_LANDMARKS:
                    row += ["", "", "", "", "", "", ""]
            else:
                found += 1
                lifted = lift_keypoints(kp, sc, depth, src.depth_scale,
                                        src.intrinsics, cfg["depth"]["window"])
                for n in V1_LANDMARKS:
                    e = lifted[n]
                    if e["src"] != 0:
                        src_counts[n][e["src"]] += 1
                    xyz = e["xyz"]
                    row += (["", "", ""] if xyz is None else
                            [f"{xyz[0]:.6f}", f"{xyz[1]:.6f}",
                             f"{xyz[2]:.6f}"])
                    row += [f"{e['score']:.4f}", e["src"]]
                    row += (["", ""] if e["px"] is None
                            else [e["px"][0], e["px"][1]])
            box = diag["box"]
            row += [int(diag["det_ran"]), ";".join(diag["det_reasons"])]
            row += (["", "", "", ""] if box is None
                    else [f"{v:.1f}" for v in box])
            w.writerow(row)
            n_frames += 1
    src.close()
    wall = time.monotonic() - t_start

    git_commit = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
        capture_output=True, text=True).stdout.strip()
    meta = {
        "bag": str(bag),
        "csv": str(out_csv),
        "created_unix": time.time(),
        "git_commit": git_commit,
        "config": args.config,
        "config_sha256": hashlib.sha256(
            Path(args.config).read_bytes()).hexdigest(),
        "device": args.device,
        "variant": variant,
        "model": {k: cfg["model"][k] for k in
                  ("variant", "backend", "det_onnx", "pose_onnx",
                   "det_input_size_wh", "pose_input_size_wh")},
        "model_files": model_files,
        "detect": cfg["detect"],
        "depth_window": cfg["depth"]["window"],
        "intrinsics": intrinsics_to_dict(src.intrinsics),
        "depth_scale": src.depth_scale,
        "frames": n_frames,
        "person_found": found,
        "det_runs": det_runs,
        "blocked": {n: {"no_depth": c[2], "out_of_frame": c[3]}
                    for n, c in src_counts.items()},
        "note": "camera-frame meters; scores are RTMPose localization "
                "confidence, NOT visibility; no gate applied (D-006)",
    }
    meta_path = out_csv.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2))

    no_depth = sum(c[2] for c in src_counts.values())
    oof = sum(c[3] for c in src_counts.values())
    print(f"frames {n_frames}, person found {found}, det runs {det_runs} "
          f"({100 * det_runs / max(1, n_frames):.1f} pct), wall {wall:.1f} s")
    print(f"blocked landmark samples: no_depth {no_depth}, "
          f"out_of_frame {oof} of {n_frames * 8} total")
    print(f"csv:  {out_csv}")
    print(f"meta: {meta_path}")


if __name__ == "__main__":
    main()
