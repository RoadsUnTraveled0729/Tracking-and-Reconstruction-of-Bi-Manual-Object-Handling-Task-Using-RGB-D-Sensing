"""Moving-window supplement to the E-014 synthetic evaluation.

The main harness (harness_recovery.py) carves 45-frame windows from
clean tracked holding stretches; on R5 those stretches sit at the
pause stations and at the wire handover, so the masked arm barely
moves and hold-last is competitive by construction, while the
handover windows change the grasp mid-outage - the technique's
stated worst case. This check adds the one tracked MOVING stretch
R5 admits (the right-hand desk slide, frames 858-931 minus the
torso-failure tail), masks it synthetically, and grades the methods
on both metrics:

  joint angles   wrap-aware error vs the unmasked solve (the prior-
                 conditioned swivel/twist dominates here)
  FK wrist       the forward-kinematics wrist position against the
                 measured wrist - the quantity the reconstruction
                 actually shows

Run: python eval/failure/moving_window_check.py [--stem STEM]
Writes eval/reports/<alias>_recovery_moving.{md,json}.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "common"))
sys.path.insert(0, str(HERE.parents[0] / "inspect"))

import paths                                # noqa: E402
import recovery_core as rc                  # noqa: E402
from check_v1_overlay import fk_arm_dirs    # noqa: E402
from root_frame import (unity_from_sensor,  # noqa: E402
                        recompose_zxy)

# The moving windows: inside the right-hand desk-slide grip episode
# (858-1088), after the 5-frame time-local-mu warm-up, ending before
# the torso-failure window at 896 begins to corrupt the truth root
# for the longer variant; truth arm motion over each window is
# ~50 deg (printed), i.e. these are genuinely moving outages.
WINDOWS = [("right", 865, 895), ("right", 870, 902)]
ARM_IDX = {"right": [3, 4, 5, 6], "left": [8, 9, 10, 11]}


def wrap(d):
    return (np.asarray(d, float) + 180.0) % 360.0 - 180.0


def fk_wrist(angles, i, sh, Lu, Lf, side):
    R_root = recompose_zxy(angles[i, :3])
    si = 3 if side == "right" else 8
    up, fo = fk_arm_dirs(angles[i, si:si + 3],
                         angles[i, si + 3:si + 5], side)
    e = sh[i] + Lu * (R_root @ up)
    return e + Lf * (R_root @ fo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R5_STEM)
    ap.add_argument("--eligible-only", action="store_true",
                    help="preselect all 45-frame harness windows before scoring; additive report")
    ap.add_argument("--side-only", action="store_true",
                    help="use the established one-handed rail eligibility")
    args = ap.parse_args()
    stem = args.stem
    alias = paths.ALIAS[stem]

    inp0 = rc.build_inputs(stem)
    truth = rc.run_variant(inp0, "plain")
    lm = inp0["lm_df"]
    out = {"stem": stem, "windows": []}
    if args.eligible_only:
        from harness_recovery import grip_context, select_windows, _runs
        ctx = grip_context(stem, inp0)
        selection = {side: select_windows(inp0, truth, ctx, side,
                                          side_only=args.side_only)
                     for side in rc.SIDES}
        windows = [(side, a, b) for side in rc.SIDES
                   for a, b in selection[side]["windows"]]
        out["policy"] = {"duration_frames": 45, "guard_frames": 15,
                         "maximum_windows_per_side": 8,
                         "side_only": args.side_only,
                         "motion_threshold": None,
                         "selection": "harness eligibility, chronological; before method errors"}
        out["selection"] = {}
        out["metric_scope"] = {
            "angle_columns": ARM_IDX,
            "angle_reference": "unmasked solve, including held twist; descriptive, not the harness live-column pooled metric",
            "wrist_reference": "measured wrist; FK includes calibrated lengths and carried solver state"}
        for side, selected in selection.items():
            out["selection"][side] = {
                k: value for k, value in selected.items() if k != "ok"}
            out["selection"][side]["all_eligible_runs"] = _runs(selected["ok"], 1)
            out["selection"][side]["eligible_frames"] = np.flatnonzero(selected["ok"]).tolist()
            from harness_recovery import ARM_BITS
            sw, _, el = ARM_BITS[side]
            fail = inp0["fail"][side] | inp0["fail"]["torso"]
            if not args.side_only:
                fail = fail | inp0["fail"]["left"] | inp0["fail"]["right"]
            criteria = {
                "instantaneous_holding": ctx[side]["hold_clean"],
                "episode_holding": inp0["holding"][side],
                "no_relevant_detector_failure": ~fail,
                "finite_object_wrist": np.isfinite(inp0["w_hat_solver"][side]).all(axis=1),
                "raw_wrist_sample": ctx[side]["wrist_flag0"],
                "reference_swing_live": (truth["mask"] & (1 << sw)) > 0,
                "reference_elbow_live": (truth["mask"] & (1 << el)) > 0}
            assert np.array_equal(np.logical_and.reduce(list(criteria.values())), selected["ok"])
            out["selection"][side]["criterion_exclusions"] = {
                name: {"count": int((~mask).sum()),
                       "frames": np.flatnonzero(~mask).tolist()}
                for name, mask in criteria.items()}
            for a, b in selected["windows"]:
                assert b-a+1 == 45 and selected["ok"][a:b+1].all()
        if stem == paths.R5_STEM:
            out["historical_windows"] = [
                {"side": side, "start": a, "stop": b,
                 "eligible_frames": int(selection[side]["ok"][a:b+1].sum()),
                 "total_frames": b-a+1}
                for side, a, b in WINDOWS]
        covered = [(side, i) for side, a, b in windows for i in range(a,b+1)]
        out["selected_frame_occurrences"] = len(covered)
        out["unique_selected_frames_by_side"] = len(set(covered))
        out["within_arm_overlap_occurrences"] = len(covered) - len(set(covered))
        out["unique_recording_frames"] = len({i for _, i in covered})
        out["cross_arm_shared_frames"] = len(
            {i for side, i in covered if side == "left"}
            & {i for side, i in covered if side == "right"})
        assert out["within_arm_overlap_occurrences"] == 0
        input_paths = [paths.lm_filtered(stem), paths.calib_for(stem),
                       paths.object_world_filtered(stem),
                       paths.EVAL_OUT / f"recovery_{alias}/failure_mask.csv",
                       paths.EVAL_REPORTS / f"{stem}_offset_fit.json",
                       paths.EVAL_REPORTS / f"{stem}_inspection.json"]
        input_paths += [paths.REPO / name for name in (
            "eval/failure/moving_window_check.py", "eval/failure/harness_recovery.py",
            "eval/failure/recovery_core.py", "eval/failure/grip_state.py",
            "eval/offset/carry.py", "eval/offset/fit_offset.py",
            "v1/kinematics/occlusion_ext.py", "v1/kinematics/occlusion.py")]
        out["inputs"] = [{"path": str(p.relative_to(paths.REPO)),
                           "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                          for p in input_paths]
        # Commit selection to disk before any masked method is evaluated.
        (paths.EVAL_REPORTS / f"{alias}_recovery_eligible_selection.json").write_text(
            json.dumps(out, indent=2) + "\n")
        intro = ("All chronologically selected 45-frame windows passing the existing "
                 "harness rules, selected before recovery errors were computed. "
                 "No motion threshold or duration retuning is applied. Every selected "
                 "window is reported, including stationary or unfavourable cases. "
                 "Reference swing and elbow groups must be live; twist may be held. "
                 "These are synthetic comparisons with the unmasked solve and measured "
                 "wrist, not independent anatomical ground truth. Windows do not overlap "
                 "within either arm. Simultaneous left/right windows share recording "
                 f"frames: {out['cross_arm_shared_frames']}; "
                 f"{len(covered)} arm-frame occurrences cover "
                 f"{out['unique_recording_frames']} distinct recording frames. "
                 "These windows are not independent trials.")
    elif stem == paths.R5_STEM:
        windows = WINDOWS
        intro = ("Synthetic arm masking on the one tracked MOVING holding "
                 "stretch (right-hand desk slide). Truth = unmasked solve. "
                 "Methods on identical masked inputs. Supplement to "
                 "r5_recovery_synthetic.md; see the docstring of "
                 "eval/failure/moving_window_check.py for why the main "
                 "harness's windows are motion-poor.")
    else:
        # any other recording: the windows the main harness carved
        # (eval/reports/<alias>_recovery_synthetic.json), so this check
        # adds the forward-kinematics wrist error for the same stretches
        rep = json.loads((paths.EVAL_REPORTS
                          / f"{alias}_recovery_synthetic.json").read_text())
        windows = [(side, int(a), int(b)) for side in rc.SIDES
                   for a, b in rep["selection"][side]["windows"]]
        intro = ("Synthetic arm masking on the windows carved by "
                 f"harness_recovery.py for this recording ({alias}_recovery_"
                 "synthetic.md). Truth = unmasked solve. Methods on "
                 "identical masked inputs. This check adds the forward-"
                 "kinematics wrist error of all three methods, the "
                 "quantity the reconstruction shows.")
    lines = [f"# Moving-window recovery check: {stem}", "", intro, ""]

    def metric(value, decimals=2):
        return float(value) if args.eligible_only else round(float(value), decimals)

    for side, a, b in windows:
        sl = inp0["seg_len"]
        Lu = sl[f"upper_arm_{'R' if side == 'right' else 'L'}"]
        Lf = sl[f"forearm_{'R' if side == 'right' else 'L'}"]
        sh = np.array([unity_from_sensor(v) for v in
                       lm[[f"{side}_shoulder_x", f"{side}_shoulder_y",
                           f"{side}_shoulder_z"]].to_numpy()])
        wm = np.array([unity_from_sensor(v) for v in
                       lm[[f"{side}_wrist_x", f"{side}_wrist_y",
                           f"{side}_wrist_z"]].to_numpy()])
        em = np.zeros(inp0["n"], bool)
        em[a:b + 1] = True
        inp = rc.build_inputs(stem, extra_fail={side: em})
        res = {"hold": rc.run_hold_baseline(inp),
               "masked": rc.run_variant(inp, "masked"),
               "recovery": rc.run_variant(inp, "recovery")}
        idx = ARM_IDX[side]
        w = slice(a, b + 1)
        motion = float(np.max(np.abs(wrap(
            truth["angles"][w][:, idx]
            - truth["angles"][a][None, idx]))))
        we = inp["w_hat_solver"][side]
        werr = np.linalg.norm(we[w] - wm[w], axis=1) * 100
        rec = {"side": side, "start": a, "stop": b,
               "truth_motion_deg": metric(motion, 1),
               "obj_wrist_err_cm": {
                   "median": metric(np.nanmedian(werr)),
                   "p95": metric(np.nanpercentile(werr, 95))},
               "methods": {}}
        lines += [f"## {side} {a}-{b} ({b - a + 1} frames, truth arm "
                  f"motion {motion:.0f} deg, object wrist estimate "
                  f"err median {np.nanmedian(werr):.1f} cm)", "",
                  "| method | angle med (deg) | angle p95 | angle max "
                  "| FK wrist med (cm) | p95 | max |",
                  "|---|---|---|---|---|---|---|"]
        for name, r in res.items():
            e = np.abs(wrap(r["angles"][w][:, idx]
                            - truth["angles"][w][:, idx]))
            fe = [np.linalg.norm(
                fk_wrist(r["angles"], i, sh, Lu, Lf, side) - wm[i]) * 100
                for i in range(a, b + 1)
                if np.isfinite(wm[i]).all()]
            rec["methods"][name] = {
                "angle_deg": {"median": metric(np.median(e)),
                              "p95": metric(np.percentile(e, 95)),
                              "max": metric(e.max())},
                "fk_wrist_cm": {"median": metric(np.median(fe)),
                                "p95": metric(np.percentile(fe, 95)),
                                "max": metric(max(fe))}}
            am, fm = rec["methods"][name]["angle_deg"], \
                rec["methods"][name]["fk_wrist_cm"]
            lines.append(f"| {name} | {am['median']:.2f} | {am['p95']:.2f} | "
                         f"{am['max']:.2f} | {fm['median']:.2f} | {fm['p95']:.2f} "
                         f"| {fm['max']:.2f} |")
        lines.append("")
        out["windows"].append(rec)
        print(f"[{side} {a}-{b}] motion {motion:.0f} deg, obj wrist "
              f"{np.nanmedian(werr):.1f} cm; FK wrist med: " +
              ", ".join(f"{k} {v['fk_wrist_cm']['median']}"
                        for k, v in rec["methods"].items()))

    lines += [
        "## Reading", ""]
    if args.eligible_only:
        lines += [
            "The motion column characterizes each eligible outage; it is not a "
            "selection criterion. The archived selection lists every eligible frame "
            "and run. No conclusion about large moving outages follows if all "
            "selected windows contain little movement. Direction fallback has a "
            "45-frame horizon, while the ordinary IK swivel prior persists without "
            "that expiry. Historical exploratory windows are retained separately.", ""]
    elif stem == paths.R5_STEM:
        lines += [
            "On a moving outage the hold-last wrist position runs away "
            "with the motion (max grows with window length) while the "
            "object-recovered wrist stays within a few centimeters of the "
            "true wrist - the object anchor is live, not a memory. In "
            "angle space the recovered twist is conditioned by the elbow "
            "swivel prior and can read worse than the smoothed memory "
            "methods on short windows; the recovered groups are tagged "
            "CONSTRAINED accordingly. The EMA memory method degrades "
            "toward hold as its memory goes stale (45-frame horizon), "
            "which is why the real 8-second failure windows - graded "
            "qualitatively in the overlay video - show hold/EMA leaving "
            "the body while the recovery follows the cube.", ""]
    else:
        lines += [
            "The reading above the tables is left to the consumer of the "
            "numbers: the truth arm motion per window (printed in each "
            "heading) says how far a held value can drift, and the FK "
            "wrist columns say what each method shows. The paragraph "
            "written for R5 (a fast desk slide, about 50 deg of arm "
            "travel per window) is not repeated here.", ""]

    suffix = "eligible" if args.eligible_only else "moving"
    md = paths.EVAL_REPORTS / f"{alias}_recovery_{suffix}.md"
    js = paths.EVAL_REPORTS / f"{alias}_recovery_{suffix}.json"
    md.write_text("\n".join(lines))
    js.write_text(json.dumps(out, indent=1) + "\n")
    print(f"[+] {md}")
    print(f"[+] {js}")


if __name__ == "__main__":
    main()
