"""Deterministic CSV replay: extraction CSV -> causal filter -> Unity
flip -> occlusion strategy -> per-frame angles + statuses.

This is the grading path (V3_PLAN.md Phase 3): S-type truth is the
run of the IDENTICAL stateful pipeline on the unmasked CSV -- one
code path, the only difference being which file is read. No
onnxruntime needed here; masked cells are empty in the CSV exactly
like v1's masked datasets.

The realtime paced mode (bag -> detector -> depth -> same tail) comes
with the latency campaign; run_csv is deliberately free of any
detector dependency so grading and tests stay install-free.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

V3_ROOT = Path(__file__).resolve().parents[1]
if str(V3_ROOT) not in sys.path:
    sys.path.insert(0, str(V3_ROOT))

from core.skeleton import V1_LANDMARKS                    # noqa: E402
from replay.bone_projection import build_projector        # noqa: E402
from replay.causal_filter import CausalLandmarkFilter     # noqa: E402

SENSOR_TO_UNITY = np.array([1.0, -1.0, 1.0])


def run_csv(csv_path, cfg, strategy):
    """Replay a (possibly masked) extraction CSV through the causal
    pipeline. Returns a DataFrame: frame, time_s, the 13 angles by
    name, status_<group> per group, n_missing (blocked landmark
    count that frame), and the filtered, flipped landmarks the
    strategy received as <name>_fx/_fy/_fz (Unity space, NaN when the
    filter returned nothing). The strategy is reset() first."""
    from bench.metrics import ANGLE_NAMES, GROUP_NAMES

    df = pd.read_csv(csv_path)
    filt = CausalLandmarkFilter(cfg["filter"])
    bones = build_projector(cfg)   # D-030; None unless bones.project
    strategy.reset()

    rows = []
    for _, row in df.iterrows():
        points = {}
        scores = {}
        missing = 0
        raws = {}
        for name in V1_LANDMARKS:
            v = np.array([row.get(f"{name}_x", np.nan),
                          row.get(f"{name}_y", np.nan),
                          row.get(f"{name}_z", np.nan)], dtype=float)
            raws[name] = None if np.any(np.isnan(v)) else v
        if bones is not None:
            # lift-time placement: the CSV holds the raw lift
            # (extract_bag_to_csv.py runs lift_keypoints without a
            # projector), so the projection runs here before the filter
            raws = bones(raws)
        for name in V1_LANDMARKS:
            raw = raws[name]
            f = filt(name, raw)               # camera frame, causal
            if f is None:
                missing += 1
                points[name] = None
            else:
                points[name] = f * SENSOR_TO_UNITY
            sc = row.get(f"{name}_score", np.nan)
            scores[name] = float(sc) if not pd.isna(sc) else float("nan")
        # snapshot before update: the record is what the strategy got
        fcols = {}
        for name in V1_LANDMARKS:
            p = points[name]
            for c, ax in enumerate("xyz"):
                fcols[f"{name}_f{ax}"] = (float(p[c]) if p is not None
                                          else float("nan"))
        out = strategy.update(float(row["time_s"]), points, scores)
        rec = {"frame": int(row["frame"]), "time_s": float(row["time_s"]),
               "n_missing": missing}
        for j, an in enumerate(ANGLE_NAMES):
            rec[an] = out.angles13[j]
        for g, gn in enumerate(GROUP_NAMES):
            rec[f"status_{gn}"] = out.status[g]
        # causal twist observability of the measurement the strategy
        # solved this frame (S2 diagnostics; NaN for strategies that do
        # not report it). Informational: the D-033 teleport gate uses
        # the oracle's twist_ok on the unmasked CSV (bench/grade.py)
        for sd in ("r", "l"):
            v = out.diagnostics.get(f"{sd}_twist_ok")
            rec[f"{sd}_twist_ok"] = float("nan") if v is None else float(v)
        rec.update(fcols)
        rows.append(rec)
    return pd.DataFrame(rows)
