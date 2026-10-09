#!/usr/bin/env python3
"""Hip hold (E-034) against the pinned ray repair on one recording.

The user's proposal (2026-09-09): people do not move while handling the
object, so a hip whose depth the hand or the object takes can be frozen
at its last known value. RobustChainSolver(hip_hold=True) does that
(v1/kinematics/occlusion_ext.py); the pinned layer places the rejected
hip on its camera ray at the remembered depth instead (E-011b, E-027).
This study runs the recovery variant both ways on the same inputs and
reports, over the frames on which either policy replaced a hip:

  - root angle spread (p95 - p5, and the standard deviation) per policy,
    against the raw hips (the hold-last solve, no preparation);
  - pelvis drift (largest distance from the window's first value) per
    policy, and the mean separation of the two pelvis tracks;
  - the measured shoulder-midpoint drift over the same frames (the
    shoulders stay measured, so this is the evidence for or against the
    no-move assumption on that window);
  - the forward-kinematics wrist separation between the two policies
    (the world wrist is nearly independent of the root policy);
  - how many of the thirteen angles differ, and by how much, over the
    whole recording (what a thesis number would see).

Offline, causal solves, no lookahead. Report: eval/reports/
<alias>_hip_hold.md, .json, .png. Run: python eval/failure/
compare_hip_hold.py --stem STEM
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "common"))
sys.path.insert(0, str(HERE.parents[0] / "offset"))
sys.path.insert(0, str(HERE.parents[1] / "v1" / "kinematics"))

import paths                                   # noqa: E402
import recovery_core as rc                     # noqa: E402
from moving_window_check import fk_wrist       # noqa: E402
from root_frame import unity_from_sensor       # noqa: E402

ANGLE_COLS = ["root_ex", "root_ey", "root_ez", "Rsh_y", "Rsh_z", "Rsh_tau",
              "Rel_y", "Rel_z", "Lsh_y", "Lsh_z", "Lsh_tau", "Lel_y", "Lel_z"]
CHANGED_DEG = 0.05      # an angle counts as changed between the policies above this


def wrap(a):
    return (np.asarray(a, float) + 180.0) % 360.0 - 180.0


def runs(mask):
    out, on = [], False
    for i, b in enumerate(mask):
        if b and not on:
            on, s = True, i
        elif not b and on:
            on = False
            out.append((s, i - 1))
    if on:
        out.append((s, len(mask) - 1))
    return out


def spread(a):
    a = wrap(a - np.median(a))
    return float(np.percentile(a, 95) - np.percentile(a, 5)), float(a.std())


def drift(p):
    ok = np.isfinite(p).all(axis=1)
    if ok.sum() < 2:
        return float("nan")
    q = p[ok]
    return float(np.linalg.norm(q - q[0], axis=1).max())


def lm_points(lm, name):
    v = lm[[f"{name}_x", f"{name}_y", f"{name}_z"]].to_numpy(float)
    return np.array([unity_from_sensor(r) for r in v])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R7_STEM)
    args = ap.parse_args()
    stem = args.stem
    alias = paths.ALIAS[stem]
    inp = rc.build_inputs(stem)
    n, lm, seg_len = inp["n"], inp["lm_df"], inp["seg_len"]

    ray = rc.run_variant(inp, "recovery")
    hold = rc.run_variant(inp, "recovery", solver_kwargs={"hip_hold": True})
    raw = rc.run_hold_baseline(inp)
    s_ray, s_hold = ray["solver"], hold["solver"]

    replaced = np.zeros(n, bool)
    for s in (s_ray, s_hold):
        for j in ("left_hip", "right_hip"):
            replaced[s.recovered_frames.get(j, [])] = True
    windows = runs(replaced)

    sh = {"right": lm_points(lm, "right_shoulder"),
          "left": lm_points(lm, "left_shoulder")}
    smid = 0.5 * (sh["right"] + sh["left"])

    def fk(res, side):
        Lu = seg_len[f"upper_arm_{'R' if side == 'right' else 'L'}"]
        Lf = seg_len[f"forearm_{'R' if side == 'right' else 'L'}"]
        return np.array([fk_wrist(res["angles"], i, sh[side], Lu, Lf, side)
                         for i in range(n)])

    wr = {p: {side: fk(res, side) for side in rc.SIDES}
          for p, res in (("ray", ray), ("hold", hold))}

    per_window = []
    for a, b in windows:
        sl = slice(a, b + 1)
        row = {"frames": [int(a), int(b)], "n": int(b - a + 1)}
        for name, res in (("raw", raw), ("ray", ray), ("hold", hold)):
            ang = res["angles"][sl]
            row[name] = {}
            for i, k in enumerate(("root_ex", "root_ey", "root_ez")):
                sp, sd = spread(ang[:, i])
                row[name][k] = {"spread_deg": round(sp, 2), "std_deg": round(sd, 2)}
            if "pelvis" in res:
                row[name]["pelvis_drift_cm"] = round(
                    drift(res["pelvis"][sl]) * 100, 2)
        row["shoulder_mid_drift_cm"] = round(drift(smid[sl]) * 100, 2)
        sep = np.linalg.norm(ray["pelvis"][sl] - hold["pelvis"][sl], axis=1)
        row["pelvis_separation_cm"] = {
            "median": round(float(np.nanmedian(sep)) * 100, 2),
            "max": round(float(np.nanmax(sep)) * 100, 2)}
        row["fk_wrist_separation_cm"] = {
            side: {"median": round(float(np.nanmedian(np.linalg.norm(
                wr["ray"][side][sl] - wr["hold"][side][sl], axis=1))) * 100, 2),
                   "max": round(float(np.nanmax(np.linalg.norm(
                wr["ray"][side][sl] - wr["hold"][side][sl], axis=1))) * 100, 2)}
            for side in rc.SIDES}
        per_window.append(row)

    d = wrap(ray["angles"] - hold["angles"])
    changed = np.abs(d) > CHANGED_DEG
    whole = {
        "frames_replaced": int(replaced.sum()),
        "frames_any_angle_changed": int(changed.any(axis=1).sum()),
        "per_angle_max_abs_deg": {k: round(float(np.abs(d[:, i]).max()), 2)
                                  for i, k in enumerate(ANGLE_COLS)},
        "per_angle_median_abs_deg_on_replaced": {
            k: round(float(np.median(np.abs(d[replaced, i]))), 2)
            for i, k in enumerate(ANGLE_COLS)} if replaced.any() else {},
        "root_tag_constrained_frames": {
            "ray": int((ray["tags"][:, 0] == 2).sum()),
            "hold": int((hold["tags"][:, 0] == 2).sum())},
        "solver_counters": {
            "ray": {"gated": {k: int(v) for k, v in s_ray.gated.items()},
                    "ray_fixed": {k: int(v) for k, v in s_ray.ray_fixed.items()},
                    "occluder_fixed": {k: int(v) for k, v in
                                       s_ray.occluder_fixed.items()}},
            "hold": {"gated": {k: int(v) for k, v in s_hold.gated.items()},
                     "hip_held": {k: int(v) for k, v in s_hold.hip_held.items()},
                     "ray_fixed": {k: int(v) for k, v in s_hold.ray_fixed.items()}}},
    }
    out = {"stem": stem, "alias": alias, "windows": per_window,
           "whole_recording": whole}
    rep = paths.EVAL_REPORTS / f"{alias}_hip_hold"
    rep.with_suffix(".json").write_text(json.dumps(out, indent=1))

    L = []
    a = L.append
    a(f"# Hip hold (E-034) against the ray repair: {stem} ({alias})")
    a("")
    a("Three root policies on the same masked landmarks: raw (the hips as")
    a("measured, hold-last solve), ray (the pinned preparation: a rejected")
    a("hip on its camera ray at the remembered depth, E-011b/E-027), hold")
    a("(the rejected or unreported hip frozen at its last accepted")
    a("position, hip_hold=True). Windows are the frames on which either")
    a("policy replaced a hip. Spread is p95 minus p5 about the median.")
    a("")
    for w in per_window:
        a(f"## Frames {w['frames'][0]}-{w['frames'][1]} ({w['n']} frames)")
        a("")
        a("| policy | root_ex spread / std (deg) | root_ey spread / std | "
          "root_ez spread / std | pelvis drift (cm) |")
        a("|---|---|---|---|---|")
        for name in ("raw", "ray", "hold"):
            r = w[name]
            a(f"| {name} | {r['root_ex']['spread_deg']} / "
              f"{r['root_ex']['std_deg']} | {r['root_ey']['spread_deg']} / "
              f"{r['root_ey']['std_deg']} | {r['root_ez']['spread_deg']} / "
              f"{r['root_ez']['std_deg']} | "
              f"{r.get('pelvis_drift_cm', 'n/a')} |")
        a("")
        a(f"- measured shoulder-midpoint drift over the window: "
          f"{w['shoulder_mid_drift_cm']} cm")
        a(f"- pelvis separation ray vs hold: median "
          f"{w['pelvis_separation_cm']['median']} cm, max "
          f"{w['pelvis_separation_cm']['max']} cm")
        fs = w["fk_wrist_separation_cm"]
        a(f"- forward-kinematics wrist separation ray vs hold: right median "
          f"{fs['right']['median']} / max {fs['right']['max']} cm, left "
          f"median {fs['left']['median']} / max {fs['left']['max']} cm")
        a("")
    a("## Whole recording")
    a("")
    a(f"- frames with a replaced hip: {whole['frames_replaced']}; frames "
      f"where any of the thirteen angles differs by more than {CHANGED_DEG} deg "
      f"between the policies: {whole['frames_any_angle_changed']}")
    a(f"- largest per-angle difference (deg): "
      + ", ".join(f"{k} {v}" for k, v in whole["per_angle_max_abs_deg"].items()))
    a(f"- root tagged constrained: ray {whole['root_tag_constrained_frames']['ray']}, "
      f"hold {whole['root_tag_constrained_frames']['hold']} frames")
    a(f"- solver counters: {json.dumps(whole['solver_counters'])}")
    a("")
    rep.with_suffix(".md").write_text("\n".join(L))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    t = inp["t"]
    fig, axes = plt.subplots(4, 1, figsize=(11, 9), sharex=True)
    for i, k in enumerate(("root_ex", "root_ey", "root_ez")):
        for name, res, c in (("raw", raw, "0.6"), ("ray", ray, "tab:blue"),
                             ("hold", hold, "tab:orange")):
            axes[i].plot(t, wrap(res["angles"][:, i]
                                 - np.median(ray["angles"][:, i])), c,
                         lw=0.8, label=name)
        axes[i].set_ylabel(f"{k} (deg, about median)")
    for a0, b0 in windows:
        for ax in axes:
            ax.axvspan(t[a0], t[b0], color="0.9", zorder=0)
    axes[0].legend(loc="upper right", fontsize=8)
    axes[3].plot(t, ray["pelvis"][:, 2], "tab:blue", lw=0.8, label="ray")
    axes[3].plot(t, hold["pelvis"][:, 2], "tab:orange", lw=0.8, label="hold")
    hz = 0.5 * (lm_points(lm, "left_hip")[:, 2] + lm_points(lm, "right_hip")[:, 2])
    axes[3].plot(t, hz, "0.6", lw=0.8, label="raw hip midpoint")
    axes[3].set_ylabel("pelvis depth (m)")
    axes[3].set_xlabel("time (s)")
    axes[3].legend(loc="upper right", fontsize=8)
    fig.suptitle(f"{alias}: root under the three hip policies "
                 "(grey bands: a hip was replaced)")
    plt.tight_layout()
    plt.savefig(rep.with_suffix(".png"), dpi=120)
    print(f"PASS: {rep.with_suffix('.md')}")
    for w in per_window:
        print(f"  frames {w['frames'][0]}-{w['frames'][1]}: root_ey spread "
              f"raw {w['raw']['root_ey']['spread_deg']} / ray "
              f"{w['ray']['root_ey']['spread_deg']} / hold "
              f"{w['hold']['root_ey']['spread_deg']} deg; root_ex "
              f"{w['raw']['root_ex']['spread_deg']} / "
              f"{w['ray']['root_ex']['spread_deg']} / "
              f"{w['hold']['root_ex']['spread_deg']}; pelvis drift ray "
              f"{w['ray']['pelvis_drift_cm']} hold {w['hold']['pelvis_drift_cm']} "
              f"cm; shoulder-mid drift {w['shoulder_mid_drift_cm']} cm")
    print(f"  whole: angles changed on {whole['frames_any_angle_changed']} "
          f"frames; max per angle {whole['per_angle_max_abs_deg']}")


if __name__ == "__main__":
    main()
