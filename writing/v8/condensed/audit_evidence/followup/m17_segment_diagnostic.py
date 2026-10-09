"""Read-only matched arm calibration study for thesis audit M17.

Run with thesis Python. Inputs remain unchanged. Writes only the requested JSON.
No anatomical truth or same-pose matching is available; 'clean' means detector
acceptance, not independently validated anatomical joint centres.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
import pandas as pd


def summary(values, mask=None):
    a = np.asarray(values, float)
    if mask is not None:
        a = a[mask]
    a = a[np.isfinite(a)]
    if not len(a):
        return {"n": 0, "median": None, "p05": None, "p95": None}
    return {"n": int(len(a)), "median": float(np.median(a)),
            "p05": float(np.percentile(a, 5)),
            "p95": float(np.percentile(a, 95))}


def digest(path, root):
    return {"path": str(path.relative_to(root)), "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, default=Path.cwd())
    ap.add_argument("--out", type=Path, default=Path("/tmp/m17_segment_diagnostic.json"))
    args = ap.parse_args()
    root = args.repo.resolve()
    for d in ("eval/common", "eval/offset", "eval/failure"):
        sys.path.insert(0, str(root / d))
    import carry
    import paths
    import detect_failures as dfail
    output = {
        "purpose": "M17: reproduce calibrated lengths and compare same-side, same-rule statistics",
        "units": "metres unless a key states otherwise; distribution quantiles are descriptive, not confidence intervals",
        "policies": {
            "whole_filtered": "carry.seg_lengths: finite filtered endpoint distance median over the whole track, independently for each segment; no source, interpolation or failure exclusion",
            "detector_second_pass_raw": "Exact run_detectors SEG_TOL=0.35 two-pass raw segment medians; clean_arm excludes first-pass D2, D1-arm, D5-arm, D3 and D4 after WARMUP_FRAMES=5; fallback to first median below MIN_CLEAN_FRAMES=30",
            "same_side_acquisition_clean": "After detector warmup; all three same-side raw landmarks have src=0 and finite coordinates; all three filtered landmarks have flag=0 and finite coordinates",
            "same_side_strict_clean": "Acquisition-clean plus no per-frame D1/D2/D5 of the same arm and no D1/D3/D4/D5 of torso, before morphology; identical rule per recording",
            "phase_subsets": "Use the existing inspection report phase intervals, without selecting by length or error",
            "no_matching_claim": "The same clean-selection procedure does not produce matched physical poses or matched camera views",
        },
        "sources": [], "recordings": {},
    }
    for alias, stem in (("loop", paths.R5_STEM), ("rail", paths.R6B_STEM)):
        rawpath = paths.lm_raw(stem)
        filteredpath = paths.lm_filtered(stem)
        meta = json.loads(rawpath.with_suffix(".meta.json").read_text())
        fmeta = json.loads(filteredpath.with_suffix(".meta.json").read_text())
        rec = dfail.load_recording(stem)
        raw = rec["df"]
        filtered = pd.read_csv(filteredpath)
        assert np.array_equal(raw.frame, filtered.frame)
        fire, stats = dfail.run_detectors(rec)
        fitpath = paths.EVAL_REPORTS / f"{stem}_offset_fit.json"
        fit = json.loads(fitpath.read_text())
        for p in (rawpath, filteredpath, rawpath.with_suffix(".meta.json"),
                  filteredpath.with_suffix(".meta.json"), fitpath,
                  paths.EVAL_REPORTS / f"{stem}_inspection.json"):
            output["sources"].append(digest(p, root))
        measured = carry.seg_lengths(filtered)
        rounded = {k: round(v, 3) for k, v in measured.items()}
        assert rounded == fit["segment_lengths_m"], (stem, rounded, fit["segment_lengths_m"])
        one = {"stem": stem, "frames": int(len(raw)),
               "whole_filtered_segment_medians_m": measured,
               "pinned_segment_lengths_m": fit["segment_lengths_m"],
               "pinned_values_reproduced": True,
               "detector_second_pass_raw_medians_m": stats["seg_med"],
               "metadata": {k: meta[k] for k in ("model", "delegate", "min_vis", "depth_window", "color_intrinsics", "coordinate_frame")},
               "filter_params": fmeta["params"], "arms": {}}
        for side, tag in (("left", "L"), ("right", "R")):
            names = [f"{side}_{p}" for p in ("shoulder", "elbow", "wrist")]
            acq = rec["in_span"].copy()
            for name in names:
                acq &= rec["ok"][name]
                acq &= filtered[f"{name}_flag"].to_numpy() == 0
                acq &= np.isfinite(filtered[[f"{name}_{a}" for a in "xyz"]].to_numpy()).all(axis=1)
            excluded = [f"d1_{tag}", f"d2_{tag}", f"d5_{tag}", "d1_torso", "d3", "d4", "d5_torso"]
            strict = acq.copy()
            for col in excluded:
                strict &= ~fire[col]
            keys = [f"upper_arm_{tag}", f"forearm_{tag}"]
            pass1bad = np.zeros(len(raw), bool)
            for key in keys:
                length, defined = stats["seg"][key]
                base = rec["in_span"] & defined
                med1 = float(np.median(length[base]))
                pass1bad |= base & (np.abs(length - med1) / med1 > dfail.SEG_TOL)
            pass2 = (rec["in_span"] & ~pass1bad & ~fire[f"d1_{tag}"]
                     & ~fire[f"d5_{tag}"] & ~fire["d3"] & ~fire["d4"])
            arm = {"n_acquisition_clean": int(acq.sum()),
                   "n_strict_clean": int(strict.sum()),
                   "strict_clean_frame_ids": rec["frame"][strict].tolist(),
                   "detector_second_pass_counts": {key: int((pass2 & stats["seg"][key][1]).sum()) for key in keys},
                   "measurements": {}}
            for data_name, data in (("raw", raw), ("filtered", filtered)):
                pts = [data[[f"{name}_{a}" for a in "xyz"]].to_numpy(float) for name in names]
                sh, el, wr = pts
                upper, fore = el-sh, wr-el
                Lu, Lf = np.linalg.norm(upper, axis=1), np.linalg.norm(fore, axis=1)
                sw = wr-sh
                with np.errstate(divide="ignore", invalid="ignore"):
                    frac = np.sum(upper*sw, axis=1) / np.sum(sw*sw, axis=1)
                    off = np.linalg.norm(upper-frac[:, None]*sw, axis=1)
                    bend = np.degrees(np.arccos(np.clip(np.sum(upper*fore, axis=1) / (Lu*Lf), -1, 1)))
                quantities = {
                    "upper_arm_m": Lu, "forearm_m": Lf, "sum_segment_lengths_m": Lu+Lf,
                    "shoulder_wrist_m": np.linalg.norm(sw, axis=1),
                    "upper_transverse_xy_m": np.linalg.norm(upper[:, :2], axis=1),
                    "fore_transverse_xy_m": np.linalg.norm(fore[:, :2], axis=1),
                    "elbow_minus_shoulder_depth_m": upper[:, 2],
                    "wrist_minus_elbow_depth_m": fore[:, 2],
                    "shoulder_depth_m": sh[:, 2], "elbow_depth_m": el[:, 2],
                    "wrist_depth_m": wr[:, 2], "elbow_projection_fraction_on_shoulder_wrist": frac,
                    "elbow_distance_from_shoulder_wrist_line_m": off,
                    "geometric_elbow_flexion_deg": bend,
                }
                arm["measurements"][data_name] = {}
                for criterion, mask in (("acquisition_clean", acq), ("strict_clean", strict)):
                    arm["measurements"][data_name][criterion] = {name: summary(v, mask) for name, v in quantities.items()}
                arm["measurements"][data_name]["strict_clean_by_phase"] = {}
                for phase, (a, b) in rec["phases"].items():
                    p = strict & (rec["frame"] >= a) & (rec["frame"] <= b)
                    arm["measurements"][data_name]["strict_clean_by_phase"][phase] = {
                        "frames": [int(a), int(b)],
                        **{name: summary(quantities[name], p) for name in ("upper_arm_m", "forearm_m", "geometric_elbow_flexion_deg")}}
            one["arms"][side] = arm
        output["recordings"][alias] = one
    output["comparison"] = {}
    for side in ("left", "right"):
        comp = {}
        for data_name in ("raw", "filtered"):
            for criterion in ("acquisition_clean", "strict_clean"):
                loop = output["recordings"]["loop"]["arms"][side]["measurements"][data_name][criterion]
                rail = output["recordings"]["rail"]["arms"][side]["measurements"][data_name][criterion]
                comp[f"{data_name}_{criterion}_rail_minus_loop_median_m"] = {
                    key: rail[key]["median"] - loop[key]["median"]
                    for key in ("upper_arm_m", "forearm_m", "sum_segment_lengths_m")
                    if rail[key]["median"] is not None and loop[key]["median"] is not None}
        output["comparison"][side] = comp
    riglog = root / "v1/integration/output/rig_dimensions.csv"
    rig = pd.read_csv(riglog).set_index("segment").meters.to_dict()
    output["avatar"] = {"cached_measured_rig_dimensions_m": rig,
                         "provenance_caveat": "Existing gitignored rig log has no recording/frame metadata; it verifies a cached rig sizing, not identity of a particular figure capture.",
                         "source_defaults": {"upper_arm_R": 0.256, "forearm_R": 0.252,
                                             "upper_arm_L": 0.262, "forearm_L": 0.247,
                                             "torso_hip_to_midshoulder": 0.479},
                         "bootstrap": "IntegratedSceneReceiver.cs creates itself at runtime with these source defaults; no serialized override found in tracked scene files"}
    for path in (root / "eval/offset/carry.py", root / "eval/failure/detect_failures.py",
                 root / "eval/failure/recovery_core.py", root / "Unity/Assets/Scripts/IntegratedSceneReceiver.cs", riglog):
        output["sources"].append(digest(path, root))
    args.out.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    print(args.out)
    for alias, rec in output["recordings"].items():
        print(alias, "whole", rec["pinned_segment_lengths_m"], "detector", rec["detector_second_pass_raw_medians_m"])
        for side in ("left", "right"):
            arm = rec["arms"][side]
            m = arm["measurements"]["raw"]["strict_clean"]
            print(alias, side, "strict n", arm["n_strict_clean"],
                  {k: m[k] for k in ("upper_arm_m", "forearm_m", "sum_segment_lengths_m", "elbow_minus_shoulder_depth_m", "wrist_minus_elbow_depth_m", "geometric_elbow_flexion_deg")})


if __name__ == "__main__":
    main()
