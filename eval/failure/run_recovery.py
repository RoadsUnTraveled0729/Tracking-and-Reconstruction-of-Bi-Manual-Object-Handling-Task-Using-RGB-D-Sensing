"""Run the object-conditioned recovery variants on a recording
(E-014 orchestrator).

Variants (recovery_core.py):
  hold      ChainFallbackSolver + failure-mask removal (pure hold-last)
  plain     RobustChainSolver, landmarks as-is (pre-study behavior)
  masked    RobustChainSolver + failure-mask removal (EMA recovery only)
  recovery  masked + the object-derived wrist input (the technique)

Writes per-variant CSVs (frame, time_s, 13 angles, live mask, 7 tags)
to eval/output/recovery_<alias>/ plus grip_episodes.json and a stdout
summary. The graded comparison lives in harness_recovery.py; this
script produces the tracks.

Run: python eval/failure/run_recovery.py [--stem STEM]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "common"))

import paths                     # noqa: E402
import recovery_core as rc       # noqa: E402

ANGLE_COLS = ["root_ex", "root_ey", "root_ez",
              "Rsh_y", "Rsh_z", "Rsh_tau", "Rel_y", "Rel_z",
              "Lsh_y", "Lsh_z", "Lsh_tau", "Lel_y", "Lel_z"]


def write_variant(out_dir, name, t, res):
    df = pd.DataFrame(res["angles"], columns=ANGLE_COLS)
    df.insert(0, "time_s", t)
    df.insert(0, "frame", np.arange(len(df)))
    df["live_mask"] = res["mask"]
    if "tags" in res:
        for g in range(7):
            df[f"tag_{g}"] = res["tags"][:, g]
    if "pelvis" in res:
        for k, ax in enumerate(("x", "y", "z")):
            df[f"pel_{ax}"] = res["pelvis"][:, k]
    p = out_dir / f"angles_{name}.csv"
    df.to_csv(p, index=False, float_format="%.4f")
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R5_STEM)
    args = ap.parse_args()
    stem = args.stem
    alias = paths.ALIAS[stem]
    out_dir = paths.EVAL_OUT / f"recovery_{alias}"
    out_dir.mkdir(parents=True, exist_ok=True)

    inputs = rc.build_inputs(stem)
    n, t = inputs["n"], inputs["t"]

    eps = {}
    for side in rc.SIDES:
        eps[side] = [{**{k: v for k, v in ep.items()
                         if k not in ("mu", "sd")},
                      "mu_cm": None if ep["mu"] is None
                      else [round(float(x) * 100, 2) for x in ep["mu"]],
                      "sd_cm": None if ep["sd"] is None
                      else [round(float(x) * 100, 2) for x in ep["sd"]]}
                     for ep in inputs["episode_fits"][side]]
    (out_dir / "grip_episodes.json").write_text(json.dumps({
        "stem": stem, "episodes": eps,
        "holding_frames": {s: int(inputs["holding"][s].sum())
                           for s in rc.SIDES},
        "estimate_frames": {s: int(np.isfinite(
            inputs["w_hat_solver"][s]).all(axis=1).sum())
            for s in rc.SIDES},
    }, indent=1))

    print(f"=== {stem}: object-conditioned recovery run ===")
    for side in rc.SIDES:
        print(f"  {side}: {len(inputs['episodes'][side])} grip episodes, "
              f"{int(inputs['holding'][side].sum())} holding frames, "
              f"{int(np.isfinite(inputs['w_hat_solver'][side]).all(axis=1).sum())} "
              f"object-wrist estimate frames")
        for ep in eps[side]:
            print(f"    ep {ep['start']}-{ep['stop']} "
                  f"({ep['n_clean']} clean) mu {ep['mu_cm']} cm "
                  f"[{ep['source']}]")
    for side in rc.SIDES:
        fa = inputs["fail"][side]
        print(f"  fail_{side}: {int(fa.sum())} frames "
              f"(D6 grip-plausibility: {inputs['d6_count'][side]})")

    res_hold = rc.run_hold_baseline(inputs)
    write_variant(out_dir, "hold", t, res_hold)
    for variant in ("plain", "masked", "recovery"):
        res = rc.run_variant(inputs, variant)
        p = write_variant(out_dir, variant, t, res)
        s = res["solver"]
        extra = (f", obj_recovered {s.obj_recovered}"
                 if s.obj_recovered else "")
        print(f"  [{variant}] gated {sum(s.gated.values())}, "
              f"recovered {sum(s.recovered.values())}{extra}")
        print(f"    -> {p}")


if __name__ == "__main__":
    main()
