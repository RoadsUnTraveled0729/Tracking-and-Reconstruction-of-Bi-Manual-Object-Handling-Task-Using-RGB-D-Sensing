"""End-to-end realtime verification: paced bag -> RTMPose detector ->
depth lift -> causal filter -> strategy -> PSV3 (Unity) + latency.

This is the whole-design check: the SAME pinned recording, played at
recorded pacing like a live camera, through the complete V3 chain,
with per-stage and total latency measured against the 33.3 ms budget
and the PSV3 stream feeding the isolated V3Scene if Unity is playing.

Run under env v3rt:
    /home/luo/anaconda3/envs/v3rt/bin/python v3/replay/realtime.py
        [--strategy s2_quat_prediction] [--no-shm]
"""
import argparse
import json
import sys
import time
from pathlib import Path

V3_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V3_ROOT.parent
sys.path.insert(0, str(V3_ROOT))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default=str(V3_ROOT / "configs/default.json"))
    ap.add_argument("--bag", default=None)
    ap.add_argument("--strategy", default="s2_quat_prediction")
    ap.add_argument("--device", default="cuda", choices=("cuda", "cpu"))
    ap.add_argument("--no-shm", action="store_true",
                    help="skip the PSV3 writer (pure latency run)")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text())
    if args.device == "cuda":
        from detector.rtmpose_detector import ensure_cuda_env
        ensure_cuda_env(cfg["model"].get("cuda_lib_dirs"))

    import numpy as np
    from core.skeleton import COCO_IDX, V1_LANDMARKS
    from detector.factory import build_detector
    from replay.bag_source import BagSource
    from replay.causal_filter import CausalLandmarkFilter
    from replay.bone_projection import build_projector
    from replay.depth_sampler import lift_keypoints
    from replay.psv3 import PSV3Writer
    from strategies.strategy_base import build
    import strategies.baseline_hold        # noqa: F401
    import strategies.s2_quat_prediction   # noqa: F401

    bag = args.bag or cfg["paths"]["bag"]
    src = BagSource(bag, paced=True)
    det = build_detector(cfg, str(REPO_ROOT),
                         img_wh=(src.intrinsics.width,
                                 src.intrinsics.height),
                         device=args.device,
                         key_indices=sorted(COCO_IDX.values()))
    filt = CausalLandmarkFilter(cfg["filter"])
    bones = build_projector(cfg)   # D-030; None unless bones.project
    strat = build(args.strategy, cfg)
    strat.reset()
    psv3 = None if args.no_shm else PSV3Writer()
    flip = np.array([1.0, -1.0, 1.0])

    stages = {k: [] for k in ("detect", "depth", "filter", "strategy",
                              "publish", "total")}
    n = found = 0
    t_wall0 = time.monotonic()
    for idx, t_s, color, depth in src.frames():
        t0 = time.perf_counter()
        kp, sc, diag = det(color)
        t1 = time.perf_counter()
        points, scores = {}, {}
        if kp is not None:
            found += 1
            lifted = lift_keypoints(kp, sc, depth, src.depth_scale,
                                    src.intrinsics, cfg["depth"]["window"],
                                    bones=bones)
        t2 = time.perf_counter()
        for name in V1_LANDMARKS:
            raw = None
            if kp is not None:
                e = lifted[name]
                raw = None if e["xyz"] is None else np.asarray(e["xyz"])
                scores[name] = e["score"]
            f = filt(name, raw)
            points[name] = None if f is None else f * flip
        t3 = time.perf_counter()
        out = strat.update(t_s, points, scores)
        t4 = time.perf_counter()
        if psv3 is not None:
            psv3.write(idx, t_s, points, out.angles13, out.status)
        t5 = time.perf_counter()
        stages["detect"].append(t1 - t0)
        stages["depth"].append(t2 - t1)
        stages["filter"].append(t3 - t2)
        stages["strategy"].append(t4 - t3)
        stages["publish"].append(t5 - t4)
        stages["total"].append(t5 - t0)
        n += 1
    wall = time.monotonic() - t_wall0
    src.close()
    if psv3 is not None:
        psv3.close(unlink=True)

    warmup = json.loads((V3_ROOT / "configs/bench.json").read_text())[
        "latency"]["warmup_frames"]
    budget = cfg["budget"]["frame_ms"]
    print(f"bag: {bag}")
    print(f"strategy {args.strategy}, device {args.device}, paced "
          f"playback; frames {n}, person found {found}, wall {wall:.1f} s "
          f"({n / wall:.1f} fps sustained)")
    print(f"per-stage latency ms (excluding {warmup} warmup frames):")
    print(f"{'stage':>9} {'p50':>7} {'p95':>7} {'p99':>7} {'max':>8}")
    for name, ts in stages.items():
        a = np.asarray(ts[warmup:]) * 1e3
        print(f"{name:>9} {np.percentile(a, 50):>7.2f} "
              f"{np.percentile(a, 95):>7.2f} "
              f"{np.percentile(a, 99):>7.2f} {a.max():>8.2f}")
    total_p99 = float(np.percentile(
        np.asarray(stages["total"][warmup:]) * 1e3, 99))
    verdict = "PASS" if total_p99 <= budget else "FAIL"
    print(f"budget check: total p99 {total_p99:.2f} ms vs {budget} ms "
          f"-> {verdict}")


if __name__ == "__main__":
    main()
