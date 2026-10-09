"""Stage 4 driver, stage-1 half: ArUco box center vs the labeled path.

Works in the desk-marker world frame (the frame the steel-ruler
survey is defined in; the object_world unity columns already live
there). While labeled_path.json has null geometry the driver runs in
geometry-pending mode: dwell detection and dwell-cluster positions
are produced (these are the numbers to compare against the survey),
path-error tables print PENDING SURVEY.

Usage:
    python eval/gt/analyze_gt_path.py [--stem STEM]

Outputs eval/reports/<stem>_stage1_path.{json,md}.
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
import carry
import path_metrics as pm
import paths
from fit_offset import load_tracks

# Dwell thresholds: proposed from the R4 speed histogram (see
# plot_path.py output and eval/DECISIONS.md E-008), not hand-picked.
V_THRESH = 0.02     # m/s
MIN_DUR_S = 0.5
SMOOTH_WIN = 5


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R4_STEM)
    ap.add_argument("--path-file", default=str(HERE / "labeled_path.json"))
    args = ap.parse_args()
    stem = args.stem

    spec = pm.load_path(args.path_file)
    calib, world, lm, obj_lev, R_lev, det, wr, wrist_flag, t = \
        load_tracks(stem, str(paths.calib_for(stem)))

    # Desk-marker (unleveled) frame track for the path comparison.
    import pandas as pd
    ofil = pd.read_csv(paths.object_world_filtered(stem))
    n = min(len(ofil), len(obj_lev))
    obj_u = ofil[["unity_px", "unity_py", "unity_pz"]].to_numpy()[:n]
    R_u = np.array([carry.recompose_zxy(e) for e in
                    ofil[["unity_ex", "unity_ey", "unity_ez"]].to_numpy()[:n]])
    center_u = obj_u + R_u @ np.array([0.0, -world.cube / 2.0, 0.0])

    insp = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_inspection.json").read_text())
    envelope = insp["phases"]["manipulation"]
    carried = carry.rest_referenced_carried(obj_lev[:n], world, envelope)

    dwells = pm.detect_dwells(t[:n], center_u, V_THRESH, MIN_DUR_S,
                              SMOOTH_WIN, valid=carried)
    report = {
        "stem": stem,
        "path_file": args.path_file,
        "survey_complete": spec["complete"],
        "dwell_params": {"v_thresh_mps": V_THRESH, "min_dur_s": MIN_DUR_S,
                         "smooth_win": SMOOTH_WIN},
        "dwells": dwells,
    }
    md = [f"# Stage-1 path analysis: {stem}", ""]

    print(f"=== {stem}: box center vs labeled path ===")
    print(f"  survey geometry: "
          f"{'COMPLETE' if spec['complete'] else 'PENDING SURVEY'}")
    print(f"  dwells detected on carried frames "
          f"(v < {V_THRESH*100:.0f} cm/s for >= {MIN_DUR_S} s):")
    md += ["## Dwells (desk-marker frame, m)", "",
           "Automatically detected: speed below "
           f"{V_THRESH*100:.0f} cm/s sustained {MIN_DUR_S} s or longer, "
           "carried frames only.", "",
           "| # | frames | dur (s) | mean xyz (m) | std (mm) |",
           "|---|---|---|---|---|"]
    for i, d in enumerate(dwells):
        print(f"    {i}: frames {d['start']}-{d['stop']} "
              f"({d['duration_s']} s) at {d['mean_xyz']} "
              f"std {d['std_xyz_mm']} mm")
        md.append(f"| {i} | {d['start']}-{d['stop']} | {d['duration_s']} | "
                  f"{d['mean_xyz']} | {d['std_xyz_mm']} |")

    if spec["complete"]:
        sel = np.flatnonzero(carried)
        rows = []
        for f in sel:
            i, dist, r, per_axis = pm.point_to_path(center_u[f], spec)
            rows.append((f, i, dist, per_axis))
        dists = np.array([r[2] for r in rows])
        report["point_to_path_cm"] = {
            "median": round(float(np.median(dists)) * 100, 2),
            "p95": round(float(np.percentile(dists, 95)) * 100, 2),
        }
        per_seg = {}
        for f, i, dist, per_axis in rows:
            per_seg.setdefault(i, []).append(dist)
        report["per_segment_cm"] = {
            str(i): {"n": len(v),
                     "median": round(float(np.median(v)) * 100, 2),
                     "p95": round(float(np.percentile(v, 95)) * 100, 2)}
            for i, v in sorted(per_seg.items())}
        matches = pm.match_dwells_to_waypoints(dwells, spec)
        report["dwell_matches"] = matches
        # survey-vs-calibration closure
        ws = spec.get("wall_marker_surveyed", {})
        if ws.get("xyz") is not None:
            wall_cal = np.array(
                calib["poses_world"]["wall"]["unity_position"])
            delta = np.array(ws["xyz"]) - wall_cal
            report["closure_wall_mm"] = {
                "delta": [round(float(v) * 1000, 1) for v in delta],
                "norm": round(float(np.linalg.norm(delta)) * 1000, 1),
                "sigma_mm": None if ws.get("sigma_m") is None
                else ws["sigma_m"] * 1000,
            }
        md += ["", "## Point-to-path error",
               "", f"median {report['point_to_path_cm']['median']} cm, "
               f"p95 {report['point_to_path_cm']['p95']} cm "
               f"over {len(rows)} carried frames"]
    else:
        report["point_to_path_cm"] = "PENDING SURVEY"
        report["closure_wall_mm"] = "PENDING SURVEY"
        print("  point-to-path error tables: PENDING SURVEY")
        md += ["", "## Point-to-path error", "", "PENDING SURVEY - fill "
               "eval/gt/labeled_path.json with the surveyed geometry and "
               "rerun. The dwell positions above are the measured cluster "
               "centers to survey against."]

    paths.EVAL_REPORTS.mkdir(parents=True, exist_ok=True)
    out_json = paths.EVAL_REPORTS / f"{stem}_stage1_path.json"
    out_json.write_text(json.dumps(report, indent=1))
    (paths.EVAL_REPORTS / f"{stem}_stage1_path.md").write_text(
        "\n".join(md) + "\n")
    print(f"[+] {out_json}")


if __name__ == "__main__":
    main()
