"""Stage-5 comparison harness: hold-last vs cv-extrap vs sphere.

Part A (synthetic): the six R4 masked scenarios. Truth = the unmasked
base CSV solved by the plain v1 solver. Per scenario and method:
angle error vs truth inside the window on the expected-held groups
(median/p95/max deg) and the reacquisition step (largest per-frame
output jump in the 5 frames after the window vs the largest truth
step there).

Part B (real): the solvers run causally over the full R4 filtered
CSV. For the long left-wrist occlusion during the left-hand carry
(box held), the sphere method's injected wrist and the hold-point
baseline (last valid wrist held) are graded in point space against
the stage-2 reference chain box_center + fitted grip offset -
evaluation reference only, never a fill. cv-extrap has no native
point output; it is graded on continuity only.

Also runs a regression guard: hold-last on the pinned R1 masked
datasets must keep live groups exact vs its own truth and held groups
constant (the validate_occlusion semantics).

Run: python eval/occlusion/harness.py
Outputs eval/reports/r4_table63_equiv.md (+ .json).
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "common"))
sys.path.insert(0, str(HERE.parents[0] / "offset"))
import carry
import paths
import solvers as sv
from fit_offset import load_tracks

sys.path.insert(0, str(paths.REPO / "v1" / "kinematics"))
from root_frame import unity_from_sensor  # noqa: E402

EXPECT_HELD = {
    "wrist_short": ["R_twist", "R_elbow"],
    "wrist_long": ["R_twist", "R_elbow"],
    "elbow_long": ["R_swing", "R_twist", "R_elbow"],
    "hip": ["root"],
    "root_ref": ["R_swing", "R_twist", "R_elbow"],
    "pose_loss": list(sv.BIT_NAMES),
}
GROUP_OF = {name: i for i, name in enumerate(sv.BIT_NAMES)}

METHODS = {
    "hold": lambda ctx: sv.HoldLast(),
    "cv": lambda ctx: sv.CVAngleFallback(horizon=10),
    "sphere": lambda ctx: sv.SphereWristFallback(ctx["forearm"]),
}


def wrap(a):
    return (np.asarray(a, float) + 180.0) % 360.0 - 180.0


def solve_csv(df, solver):
    n = len(df)
    angles = np.zeros((n, 13))
    masks = np.zeros(n, int)
    tags = np.zeros((n, sv.N_GROUPS), int)
    inj = {"left": np.full((n, 3), np.nan), "right": np.full((n, 3), np.nan)}
    for i, (_, row) in enumerate(df.iterrows()):
        pts = {k: unity_from_sensor(v)
               for k, v in sv.points_from_row(row).items()
               if np.all(np.isfinite(v))}
        angles[i], masks[i], tags[i] = solver.solve(pts)
        if isinstance(solver, sv.SphereWristFallback):
            for side in ("left", "right"):
                if solver.last_injection[side] is not None:
                    inj[side][i] = solver.last_injection[side]
    return angles, masks, tags, inj


def window_metrics(a_method, a_truth, start, stop, held_groups):
    idx = [i for g in held_groups for i in sv.GROUP_IDX[GROUP_OF[g]]]
    err = np.abs(wrap(a_method[start:stop, idx] - a_truth[start:stop, idx]))
    post = slice(stop, min(stop + 5, len(a_method)))
    step_m = np.max(np.abs(wrap(np.diff(a_method[stop - 1:post.stop],
                                        axis=0))))
    step_t = np.max(np.abs(wrap(np.diff(a_truth[stop - 1:post.stop],
                                        axis=0))))
    return {
        "median_deg": round(float(np.median(err)), 2),
        "p95_deg": round(float(np.percentile(err, 95)), 2),
        "max_deg": round(float(np.max(err)), 2),
        "reacq_step_deg": round(float(step_m), 2),
        "truth_step_deg": round(float(step_t), 2),
    }


def part_a(ctx):
    man = json.loads((paths.EVAL_OUT / "occlusion_r4"
                      / "scenarios_r4.json").read_text())
    bases = {"filtered": pd.read_csv(man["base_filtered"]),
             "raw": pd.read_csv(man["base_raw"])}
    truths = {}
    for src, df in bases.items():
        a, _, _, _ = solve_csv(df, sv.HoldLast())
        truths[src] = a
    out = {}
    for name, s in man["scenarios"].items():
        df = pd.read_csv(s["csv"])
        row = {}
        for mname, make in METHODS.items():
            a, m, tg, _ = solve_csv(df, make(ctx))
            row[mname] = window_metrics(a, truths[s["source"]],
                                        s["start"], s["stop"],
                                        EXPECT_HELD[name])
        out[name] = {"window": [s["start"], s["stop"] - 1],
                     "held_groups": EXPECT_HELD[name], "methods": row}
        print(f"  {name:12s} " + "  ".join(
            f"{k}: med {v['median_deg']:6.2f} p95 {v['p95_deg']:7.2f} "
            f"reacq {v['reacq_step_deg']:6.2f}" for k, v in row.items()))
    return out


def part_b(ctx):
    stem = paths.R4_STEM
    df = pd.read_csv(paths.R4_LM_FILTERED)
    calib, world, lm, obj, R_obj, det, wr, wrist_flag, t = \
        load_tracks(stem, str(paths.r4_calib()))
    fitrep = json.loads((paths.EVAL_REPORTS
                         / f"{stem}_offset_fit.json").read_text())
    mu_left = np.array(fitrep["per_hand"]["left"]["mu_cm"]) / 100.0
    pred_left = obj + np.einsum("nij,j->ni", R_obj, mu_left)

    # the long left-wrist occlusion during the left-hand carry
    ev_a, ev_b = 833, 1096
    n = len(df)

    _, _, _, inj = solve_csv(df, sv.SphereWristFallback(ctx["forearm"]))
    # hold-point baseline: last valid measured wrist held
    w = lm[["left_wrist_x", "left_wrist_y", "left_wrist_z"]].to_numpy()
    valid = np.isfinite(w).all(axis=1) & (wrist_flag["left"] == 0)
    w_hold = pd.DataFrame(np.where(valid[:, None], w, np.nan)) \
        .ffill().to_numpy()
    w_hold_lev = world.wrist_world(w_hold)
    # sphere injections arrive in Unity(person) space -> same transform
    inj_lev = {s: world.wrist_world(inj[s]) for s in ("left",)}

    sel = np.zeros(n, bool)
    sel[ev_a:ev_b + 1] = True
    sel &= det[:n]
    sphere_ok = sel & np.isfinite(inj_lev["left"]).all(axis=1)
    res = {}
    for label, track, m in (
            ("hold_point", w_hold_lev,
             sel & np.isfinite(w_hold_lev).all(axis=1)),
            ("sphere", inj_lev["left"], sphere_ok),
            ("hold_point_same_frames", w_hold_lev,
             sphere_ok & np.isfinite(w_hold_lev).all(axis=1))):
        d = np.linalg.norm(track[m] - pred_left[m], axis=1) * 100
        res[label] = {
            "n": int(m.sum()),
            "median_cm": round(float(np.median(d)), 1) if m.sum() else None,
            "p95_cm": round(float(np.percentile(d, 95)), 1)
            if m.sum() else None,
        }
        print(f"  real left-wrist occlusion {ev_a}-{ev_b}: {label} vs "
              f"box+offset: {res[label]}")
    res["reference"] = ("box_center + fitted left grip offset; evaluation "
                        "reference only (stage-2 chain), never a fill")
    res["caveat"] = ("the left grip offset was fitted on measured frames "
                     "outside this window; regrips inside the window are "
                     "not observable, so these numbers bound rather than "
                     "measure the wrist error")
    return {"left_wrist_833_1096": res}


def regression_guard():
    man_file = (paths.REPO / "v1" / "kinematics" / "dataset"
                / "occlusion_masked" / "scenarios.json")
    # The pinned manifest predates the v1/ folder move; remap its
    # absolute paths on load (the pinned file itself stays untouched).
    man = json.loads(man_file.read_text().replace(
        "New_SandBox/kinematics/", "New_SandBox/v1/kinematics/"))
    # the masked CSVs themselves live in the pinned dataset dir
    for s in man["scenarios"].values():
        s["csv"] = str(man_file.parent / Path(s["csv"]).name)
    base = pd.read_csv(man["base_filtered"])
    truth, _, _, _ = solve_csv(base, sv.HoldLast())
    s = man["scenarios"]["wrist_long"]
    df = pd.read_csv(s["csv"])
    a, m, tg, _ = solve_csv(df, sv.HoldLast())
    live_idx = [i for g in ("root", "R_swing", "L_swing", "L_twist",
                            "L_elbow")
                for i in sv.GROUP_IDX[GROUP_OF[g]]]
    win = slice(s["start"], s["stop"])
    live_err = np.max(np.abs(wrap(a[win][:, live_idx]
                                  - truth[win][:, live_idx])))
    held_idx = [i for g in EXPECT_HELD["wrist_long"]
                for i in sv.GROUP_IDX[GROUP_OF[g]]]
    held_const = np.max(np.abs(np.diff(a[win][:, held_idx], axis=0)))
    post_err = np.max(np.abs(wrap(a[s["stop"]:] - truth[s["stop"]:])))
    ok = live_err < 1e-9 and held_const < 1e-9 and post_err < 1e-9
    print(f"  R1 wrist_long regression: live exact {live_err:.2e}, "
          f"held const {held_const:.2e}, recovery {post_err:.2e} "
          f"-> {'PASS' if ok else 'FAIL'}")
    return bool(ok)


def main():
    fitrep = json.loads((paths.EVAL_REPORTS
                         / f"{paths.R4_STEM}_offset_fit.json").read_text())
    seg = fitrep["segment_lengths_m"]
    ctx = {"forearm": {"right": seg["forearm_R"], "left": seg["forearm_L"]}}

    print("=== regression guard (pinned R1 masked data, hold-last) ===")
    guard_ok = regression_guard()
    print("\n=== part A: synthetic scenarios on R4 ===")
    a = part_a(ctx)
    print("\n=== part B: real occlusion events ===")
    b = part_b(ctx)

    report = {"regression_guard_pass": guard_ok, "synthetic": a, "real": b}
    out_json = paths.EVAL_REPORTS / "r4_table63_equiv.json"
    out_json.write_text(json.dumps(report, indent=1))

    md = ["# Table 6.3 equivalent: occlusion handling on R4",
          "",
          "Synthetic scenarios (R1 designs at R4 fractions; angle error",
          "vs the unmasked truth on the expected-held groups, deg):", "",
          "| scenario | window | held groups | hold med/p95 | "
          "cv med/p95 | sphere med/p95 | reacq step h/c/s (truth) |",
          "|---|---|---|---|---|---|---|"]
    for name, s in a.items():
        r = s["methods"]
        md.append(
            f"| {name} | {s['window'][0]}-{s['window'][1]} | "
            f"{','.join(s['held_groups'])} | "
            f"{r['hold']['median_deg']} / {r['hold']['p95_deg']} | "
            f"{r['cv']['median_deg']} / {r['cv']['p95_deg']} | "
            f"{r['sphere']['median_deg']} / {r['sphere']['p95_deg']} | "
            f"{r['hold']['reacq_step_deg']} / {r['cv']['reacq_step_deg']}"
            f" / {r['sphere']['reacq_step_deg']} "
            f"({r['hold']['truth_step_deg']}) |")
    md += ["", "Real long left-wrist occlusion (frames 833-1096, box in "
           "the left hand), point space vs box_center + fitted grip "
           "offset:", ""]
    rb = b["left_wrist_833_1096"]
    md += [f"- hold-point baseline: median {rb['hold_point']['median_cm']} "
           f"cm, p95 {rb['hold_point']['p95_cm']} cm "
           f"({rb['hold_point']['n']} frames)",
           f"- sphere-constrained: median {rb['sphere']['median_cm']} cm, "
           f"p95 {rb['sphere']['p95_cm']} cm ({rb['sphere']['n']} frames; "
           f"needs a live elbow - the left elbow is also occluded for "
           f"most of this event)",
           f"- hold-point on the same {rb['hold_point_same_frames']['n']} "
           f"frames: median {rb['hold_point_same_frames']['median_cm']} "
           f"cm, p95 {rb['hold_point_same_frames']['p95_cm']} cm",
           f"- cv-extrap: no native point output; graded on angle "
           f"continuity in the synthetic table",
           "", f"Note: {rb['caveat']}.",
           "", f"Regression guard on pinned R1 masked data: "
           f"{'PASS' if guard_ok else 'FAIL'}."]
    (paths.EVAL_REPORTS / "r4_table63_equiv.md").write_text(
        "\n".join(md) + "\n")
    print(f"\n[+] {out_json}")
    print(f"[+] {paths.EVAL_REPORTS / 'r4_table63_equiv.md'}")


if __name__ == "__main__":
    main()
