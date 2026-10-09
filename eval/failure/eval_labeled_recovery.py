#!/usr/bin/env python3
"""Grade the object-conditioned wrist recovery against manual labels.

The natural failure windows have no tracked truth (E-013), so the
truth here is the wrist the user clicked on the colour frame
(label_wrists.py) with the aligned depth as third coordinate. Every
label is manual; nothing here places a label.

For every labelled frame and side the distance in cm between the label
and each of these is reported:
  recovered   the object-derived wrist estimate, equation (5.7)
              (recovery_core.build_inputs, w_hat_solver)
  measured    MediaPipe's own wrist on that frame (the one the detectors
              rejected; absent where MediaPipe declined the sample)
  hold        the last accepted wrist measurement before the frame,
              what a hold-last solver keeps showing
  plain_fk    the wrist that the plain solve's angles place (forward
              kinematics), the MediaPipe rig of the overlay video
  hold_fk     the same for the hold-last solve
  recovery_fk the same for the recovery solve
The *_fk columns need the angle CSVs of eval/output/recovery_<alias>/
(run_recovery.py) and the raw shoulder of that frame; they are skipped
where either is missing.

Frames listed under "clean_frames" in meta.json lie outside the failure
mask, where the tracker is trusted; they are reported separately as a
check of the reference: how far the manual label sits from the wrist
MediaPipe measured on a good frame, and from the object estimate there.

All comparisons are made in the solver (person) space, which is the
camera frame with y flipped (root_frame.unity_from_sensor); the labels
are stored in camera space and converted here.

Writes eval/reports/<alias>_recovery_labeled.{md,json}.
Run: python eval/failure/eval_labeled_recovery.py [--stem STEM] [--labels FILE]
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
sys.path.insert(0, str(HERE.parents[0] / "inspect"))
sys.path.insert(0, str(HERE.parents[1] / "v1" / "kinematics"))

import paths                       # noqa: E402
import recovery_core as rc         # noqa: E402
from moving_window_check import fk_wrist   # noqa: E402
from root_frame import unity_from_sensor   # noqa: E402

ANGLE_COLS = ["root_ex", "root_ey", "root_ez", "Rsh_y", "Rsh_z", "Rsh_tau",
              "Rel_y", "Rel_z", "Lsh_y", "Lsh_z", "Lsh_tau", "Lel_y", "Lel_z"]
METHODS = ["recovered", "measured", "hold", "plain_fk", "hold_fk",
           "recovery_fk"]


def stat(v):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return {"n": 0}
    return {"n": int(v.size), "median": round(float(np.median(v)), 2),
            "p95": round(float(np.percentile(v, 95)), 2),
            "max": round(float(v.max()), 2)}


def find_labels(alias, override):
    if override:
        return Path(override)
    tracked = HERE.parents[0] / "labels" / f"frames_{alias}" / "labels.json"
    if tracked.exists():
        return tracked
    return paths.EVAL_OUT / f"label_frames_{alias}" / "labels.json"


def load_angles(alias):
    out = {}
    for name, fn in (("plain", "angles_plain.csv"), ("hold", "angles_hold.csv"),
                     ("recovery", "angles_recovery.csv")):
        p = paths.EVAL_OUT / f"recovery_{alias}" / fn
        if p.exists():
            out[name] = pd.read_csv(p)[ANGLE_COLS].to_numpy(float)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R5_STEM)
    ap.add_argument("--labels", default=None,
                    help="labels.json (default: eval/labels/frames_<alias>/)")
    args = ap.parse_args()
    alias = paths.ALIAS[args.stem]
    lpath = find_labels(alias, args.labels)
    labels = json.loads(lpath.read_text())
    meta_p = lpath.parent / "meta.json"
    clean = set()
    if meta_p.exists():
        clean = set(int(k) for k in
                    json.loads(meta_p.read_text()).get("clean_frames", {}))

    inp = rc.build_inputs(args.stem)
    lm = inp["lm_df"]
    angles = load_angles(alias)
    sl = inp["seg_len"]

    def lm_pt(f, name):
        v = lm.loc[f, [f"{name}_x", f"{name}_y", f"{name}_z"]].to_numpy(float)
        return unity_from_sensor(v) if np.all(np.isfinite(v)) \
            else np.full(3, np.nan)

    rows = []
    for fs, per_side in sorted(labels.items(), key=lambda kv: int(kv[0])):
        f = int(fs)
        for side, L in per_side.items():
            if L is None:
                continue
            truth = unity_from_sensor(np.asarray(L["xyz_cam"], float))
            est = {"recovered": inp["w_hat_solver"][side][f],
                   "measured": lm_pt(f, f"{side}_wrist")}
            fail = inp["fail"][side]
            hold = np.full(3, np.nan)
            for g in range(f - 1, -1, -1):
                if not fail[g]:
                    cand = lm_pt(g, f"{side}_wrist")
                    if np.all(np.isfinite(cand)):
                        hold = cand
                        break
            est["hold"] = hold
            sh = lm_pt(f, f"{side}_shoulder")
            Lu = sl[f"upper_arm_{'R' if side == 'right' else 'L'}"]
            Lf = sl[f"forearm_{'R' if side == 'right' else 'L'}"]
            for name in ("plain", "hold", "recovery"):
                A = angles.get(name)
                est[f"{name}_fk"] = (fk_wrist(A, f, _ShoulderAt(sh), Lu, Lf, side)
                                     if A is not None and np.all(np.isfinite(sh))
                                     else np.full(3, np.nan))
            d = lambda p: (float(np.linalg.norm(p - truth)) * 100.0
                           if np.all(np.isfinite(p)) else float("nan"))
            rows.append({"frame": f, "side": side,
                         "group": "clean" if f in clean else "failure",
                         "truth_solver": truth.round(4).tolist(),
                         "mixed_surface": bool(L.get("mixed_surface", False)),
                         **{f"{k}_cm": round(d(est[k]), 2) for k in METHODS}})
    if not rows:
        print("[warn] no labels found in", lpath)
        return

    summary = {}
    for group in ("failure", "clean"):
        gr = [r for r in rows if r["group"] == group]
        if not gr:
            continue
        summary[group] = {}
        for side in sorted({r["side"] for r in gr}) + ["all"]:
            rs = gr if side == "all" else [r for r in gr if r["side"] == side]
            summary[group][side] = {k: stat([r[f"{k}_cm"] for r in rs])
                                    for k in METHODS}
            summary[group][side]["n_labels"] = len(rs)
            summary[group][side]["n_mixed_surface"] = \
                int(sum(r["mixed_surface"] for r in rs))

    out = paths.EVAL_REPORTS / f"{alias}_recovery_labeled"
    out.with_suffix(".json").write_text(
        json.dumps({"stem": args.stem, "labels": str(lpath),
                    "n_labels": len(rows), "summary": summary,
                    "rows": rows}, indent=1))
    n_fail = sum(r["group"] == "failure" for r in rows)
    n_clean = len(rows) - n_fail
    md = [f"# Recovered wrist against manual labels ({alias.upper()})", "",
          f"Recording: {args.stem}. Labels: {n_fail} wrists clicked by the "
          "user on natural failure-window frames inside grip episodes and "
          f"{n_clean} on clean frames outside the failure mask (the reference "
          "check). Truth is the clicked pixel deprojected with the aligned "
          "depth. Errors in cm, in the solver space. Methods: recovered = "
          "object-derived wrist estimate; measured = MediaPipe wrist on that "
          "frame; hold = last accepted MediaPipe wrist before the frame; "
          "plain_fk / hold_fk / recovery_fk = the wrist the angles of the "
          "plain, hold-last and recovery solves place.", ""]
    for group, title in (("failure", "Natural failure windows"),
                         ("clean", "Clean frames (reference check)")):
        if group not in summary:
            continue
        md += [f"## {title}", "", "| side | method | n | median | p95 | max |",
               "|---|---|---|---|---|---|"]
        for side, s in summary[group].items():
            for k in METHODS:
                st = s[k]
                if st["n"]:
                    md.append(f"| {side} | {k} | {st['n']} | {st['median']} "
                              f"| {st['p95']} | {st['max']} |")
        md.append("")
    md += ["## Per frame", "", "| frame | side | group | " +
           " | ".join(METHODS) + " | mixed |",
           "|---|---|---|" + "---|" * len(METHODS) + "---|"]
    for r in rows:
        md.append(f"| {r['frame']} | {r['side']} | {r['group']} | " +
                  " | ".join("" if not np.isfinite(r[f"{k}_cm"])
                             else f"{r[f'{k}_cm']:.1f}" for k in METHODS) +
                  f" | {'yes' if r['mixed_surface'] else ''} |")
    md.append("")
    out.with_suffix(".md").write_text("\n".join(md))
    print("\n".join(md[:40]))
    print("[+] wrote", out.with_suffix(".md"))


class _ShoulderAt:
    """Indexable stand-in so fk_wrist(angles, i, sh, ...) can take one
    shoulder position for frame i without a full (n, 3) array."""
    def __init__(self, p):
        self.p = np.asarray(p, float)

    def __getitem__(self, i):
        return self.p


if __name__ == "__main__":
    main()
