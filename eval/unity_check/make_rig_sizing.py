#!/usr/bin/env python3
"""Per-recording avatar segment lengths for the Unity receiver
(eval/unity_check/, decision E-036).

IntegratedSceneReceiver.cs sizes the rig's four arm segments and its
trunk once at scene start. Until E-035 the arm lengths were the loop
recording's built-in constants and only the trunk could be overridden
per capture (/tmp/r5_torso_m, E-034). From E-036 on every replayed
recording supplies its own five lengths: this script produces them from
the recording's existing records and hands them to the receiver through
one plain-text side-channel file.

Inputs (nothing is recomputed from landmarks except the trunk):
  eval/reports/<stem>_offset_fit.json          segment_lengths_m, the
      median landmark-to-landmark arm lengths of eval/offset/carry.py
      seg_lengths() (3 dp), reused as they are;
  eval/output/recovery_<alias>/angles_recovery.csv   pel_x/y/z, the
      post-recovery hip midpoint written by eval/failure/run_recovery.py
      from recovery_core.run_variant; it lives in the solver's
      unity_from_sensor frame (v1/kinematics/root_frame.py: y negated
      relative to the landmark camera frame);
  eval/output/recovery_<alias>/failure_mask.csv      fail_torso;
  v1/mediapipe/output/<stem>_landmarks_filtered.csv  both shoulders.

Trunk rule (E-031, numbers in E-035): median over torso-clean frames
(fail_torso == 0, every value finite) of the distance from the recovery
pelvis, brought into the landmark camera frame by negating y, to the
measured mid-shoulder of the FILTERED landmarks. This reproduces the
recorded values to 4 dp (r6b 0.5745 on 620 frames, r7 0.5166 on 1173);
the raw landmarks give 0.5748 / 0.5165 and are not used.

Outputs:
  eval/reports/<alias>_rig_sizing.json    the record: lengths at 4 dp,
      rule text, trunk detail, SHA-256 of every input and of this file;
  /tmp/r5_rig_sizing (--write-flag)       key=value lines the receiver
      parses in Awake ('#' comments, InvariantCulture floats).

Usage:
  python eval/unity_check/make_rig_sizing.py --alias r6b
  python eval/unity_check/make_rig_sizing.py --stem recording_20260909_000024
  python eval/unity_check/make_rig_sizing.py --alias r6b --variants
  python eval/unity_check/make_rig_sizing.py --alias r6b --write-flag
  python eval/unity_check/make_rig_sizing.py --self-check

The launchers import compute_sizing(stem) and write_flag(json_path,
dest) from this module (same directory as run_unity_capture.py).
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "eval"))
from common import paths as P  # noqa: E402

THIS = Path(__file__).resolve()
RECOVERY_CORE = REPO / "eval" / "failure" / "recovery_core.py"
DEFAULT_FLAG = Path("/tmp/r5_rig_sizing")
ARM_KEYS = ("upper_arm_R", "forearm_R", "upper_arm_L", "forearm_L")
FLAG_KEYS = ARM_KEYS + ("torso",)
SHOULDERS = ("left_shoulder", "right_shoulder")
# solver (unity_from_sensor) frame -> landmark camera frame
SOLVER_TO_CAMERA = np.array([1.0, -1.0, 1.0])

RULE_ARMS = ("eval/reports/<stem>_offset_fit.json segment_lengths_m: "
             "median landmark-to-landmark distance over the recording "
             "(eval/offset/carry.py seg_lengths), reused at 3 dp")
RULE_TORSO = ("E-031/E-035: median over frames with fail_torso == 0 of "
              "the distance from the recovery pelvis (angles_recovery.csv "
              "pel_x/y/z, y negated into the landmark camera frame) to the "
              "measured mid-shoulder of the filtered landmarks")

# Documented values (eval/DECISIONS.md E-035) the self-check reproduces
EXPECTED = {"r6b": (0.5745, 620), "r7": (0.5166, 1173)}

# Whether an existing Unity capture replayed the recording with this
# trunk rule, and what that capture actually sized the rig with. The arm
# lengths of every capture so far were the receiver's built-in loop
# constants (0.256, 0.252, 0.262, 0.247 m; E-031 alternative D-005);
# E-036 is the first rule that passes them per recording.
USED_BY_CAPTURE = {"r6b": True, "r7": True, "r5": False}
CAPTURE_NOTES = {
    "r6b": ("E-031 to E-033 captures used the receiver default torsoM "
            "0.576 m (this rule evaluated 2026-09-07; E-035 records 0.5745 "
            "for it) and the receiver's loop arm constants, not this "
            "recording's arm lengths."),
    "r7": ("E-035 capture used --torso-m 0.517 m (this rule at 3 dp) "
           "through /tmp/r5_torso_m and the receiver's loop arm constants, "
           "not this recording's arm lengths."),
    "r5": ("The existing loop capture used torsoM 0.479 m, the offset-fit "
           "report's torso_hip_to_midshoulder (raw hip midpoint to "
           "mid-shoulder over all frames), a different pelvis definition "
           "from this rule; its arm lengths are the receiver's built-in "
           "constants, which are this recording's offset-fit values."),
}


def resolve(stem=None, alias=None):
    """(stem, alias) from either one, checked against paths.ALIAS."""
    if stem is None and alias is None:
        raise ValueError("give a stem or an alias")
    if stem is None:
        by_alias = {a: s for s, a in P.ALIAS.items()}
        if alias not in by_alias:
            raise ValueError(f"unknown alias {alias!r}; known: "
                             f"{sorted(by_alias)}")
        stem = by_alias[alias]
    found = P.ALIAS.get(stem)
    if found is None:
        raise ValueError(f"unknown recording stem {stem!r}; add it to "
                         "paths.ALIAS")
    if alias is not None and alias != found:
        raise ValueError(f"alias {alias!r} does not match stem {stem!r} "
                         f"({found!r})")
    return stem, found


def recovery_dir(alias):
    return P.EVAL_OUT / f"recovery_{alias}"


def offset_fit_path(stem):
    return P.EVAL_REPORTS / f"{stem}_offset_fit.json"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rel(path):
    """Repo-relative POSIX path when under the repo, else absolute."""
    path = Path(path).resolve()
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return str(path)


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def trunk_length(stem, alias, landmarks="filtered"):
    """The E-031 trunk rule. Returns (median_m, n_frames).

    landmarks: "filtered" is the rule; "raw" exists only for the
    --variants comparison printout."""
    lm_path = (P.lm_filtered(stem) if landmarks == "filtered"
               else P.lm_raw(stem))
    lm = pd.read_csv(lm_path)
    ang = pd.read_csv(recovery_dir(alias) / "angles_recovery.csv")
    msk = pd.read_csv(recovery_dir(alias) / "failure_mask.csv")
    if not (len(lm) == len(ang) == len(msk)
            and np.array_equal(lm["frame"].values, ang["frame"].values)
            and np.array_equal(msk["frame"].values, ang["frame"].values)):
        raise RuntimeError(
            f"{alias}: frame columns of {lm_path.name}, angles_recovery.csv "
            "and failure_mask.csv do not line up")
    pel = ang[["pel_x", "pel_y", "pel_z"]].to_numpy(dtype=float)
    pel = pel * SOLVER_TO_CAMERA
    ls, rs = (lm[[f"{s}_x", f"{s}_y", f"{s}_z"]].to_numpy(dtype=float)
              for s in SHOULDERS)
    d = np.linalg.norm(pel - 0.5 * (ls + rs), axis=1)
    ok = (msk["fail_torso"].to_numpy() == 0) & np.isfinite(d)
    if not ok.any():
        raise RuntimeError(f"{alias}: no torso-clean frame with a finite "
                           "pelvis and mid-shoulder")
    return float(np.median(d[ok])), int(ok.sum())


def compute_sizing(stem):
    """The rig-sizing record for one recording (the JSON's content)."""
    stem, alias = resolve(stem=stem)
    fit_path = offset_fit_path(stem)
    segs = json.loads(fit_path.read_text())["segment_lengths_m"]
    torso, n = trunk_length(stem, alias)
    lengths = {k: round(float(segs[k]), 4) for k in ARM_KEYS}
    lengths["torso"] = round(torso, 4)
    sources = [fit_path,
               recovery_dir(alias) / "angles_recovery.csv",
               recovery_dir(alias) / "failure_mask.csv",
               P.lm_filtered(stem),
               RECOVERY_CORE,
               THIS]
    return {
        "stem": stem,
        "alias": alias,
        "generated_utc": utc_now(),
        "rule": {"arms": RULE_ARMS, "torso": RULE_TORSO},
        "segment_lengths_m": lengths,
        "torso_detail": {
            "value_m": round(torso, 4),
            "n_frames": n,
            "mask": "fail_torso==0",
            "landmarks": "filtered",
            "pelvis": "recovery pelvis, y negated",
        },
        "used_by_capture": USED_BY_CAPTURE.get(alias, False),
        "capture_note": CAPTURE_NOTES.get(
            alias, "No Unity capture has replayed this recording."),
        "sources": [{"path": rel(p), "sha256": sha256(p)} for p in sources],
    }


def write_flag(json_path, dest=DEFAULT_FLAG):
    """Write the receiver's side-channel file from an existing record.

    Format (parsed by IntegratedSceneReceiver.cs as key=value lines,
    '#' comments, InvariantCulture floats):
      # written <ISO-8601 UTC> from eval/reports/<alias>_rig_sizing.json
      stem=<stem>
      upper_arm_R=0.0000 ... forearm_L=0.0000
      torso=0.0000
    """
    json_path = Path(json_path)
    rec = json.loads(json_path.read_text())
    seg = rec["segment_lengths_m"]
    lines = [f"# written {utc_now()} from {rel(json_path)}",
             f"stem={rec['stem']}"]
    lines += [f"{k}={float(seg[k]):.4f}" for k in FLAG_KEYS]
    dest = Path(dest)
    dest.write_text("\n".join(lines) + "\n")
    return dest


def self_check():
    """The trunk rule must reproduce the E-035 numbers to 4 dp."""
    ok = True
    for alias, (exp_v, exp_n) in EXPECTED.items():
        stem, _ = resolve(alias=alias)
        v, n = trunk_length(stem, alias)
        good = f"{v:.4f}" == f"{exp_v:.4f}" and n == exp_n
        ok = ok and good
        print(f"[self-check] {alias}: torso {v:.4f} m on {n} frames, "
              f"expected {exp_v:.4f} on {exp_n}: "
              f"{'PASS' if good else 'FAIL'}")
    print(f"[self-check] {'PASS' if ok else 'FAIL'}")
    return ok


def print_variants(stem, alias):
    """Alternative trunk definitions, for the record of why the rule is
    the one above (none of these is written anywhere)."""
    fit = json.loads(offset_fit_path(stem).read_text())["segment_lengths_m"]
    v_f, n_f = trunk_length(stem, alias, "filtered")
    v_r, n_r = trunk_length(stem, alias, "raw")
    print(f"[variants] {alias}: rule (filtered landmarks, recovery pelvis) "
          f"{v_f:.4f} m on {n_f} frames")
    print(f"[variants] {alias}: raw landmarks, recovery pelvis "
          f"{v_r:.4f} m on {n_r} frames (not used)")
    print(f"[variants] {alias}: offset-fit torso_hip_to_midshoulder, raw "
          f"hip midpoint over all frames "
          f"{fit['torso_hip_to_midshoulder']:.3f} m (not used)")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    which = ap.add_mutually_exclusive_group()
    which.add_argument("--stem", help="recording stem (paths.ALIAS)")
    which.add_argument("--alias", choices=sorted(set(P.ALIAS.values())))
    ap.add_argument("--out", default=None,
                    help="record path (default eval/reports/"
                         "<alias>_rig_sizing.json)")
    ap.add_argument("--self-check", action="store_true",
                    help="assert the trunk rule reproduces E-035 "
                         "(r6b 0.5745, r7 0.5166) and exit")
    ap.add_argument("--write-flag", nargs="?", const=str(DEFAULT_FLAG),
                    default=None, metavar="PATH",
                    help="write the receiver's side-channel file from "
                         f"the existing record (default {DEFAULT_FLAG})")
    ap.add_argument("--variants", action="store_true",
                    help="also print the raw-landmark and offset-fit "
                         "trunk values for comparison")
    args = ap.parse_args()

    if args.self_check:
        sys.exit(0 if self_check() else 1)
    if not (args.stem or args.alias):
        ap.error("--stem or --alias is required (or --self-check)")
    stem, alias = resolve(args.stem, args.alias)
    out = (Path(args.out) if args.out
           else P.EVAL_REPORTS / f"{alias}_rig_sizing.json")

    if args.write_flag is not None:
        if not out.exists():
            sys.exit(f"FAIL: {out} does not exist; run without "
                     "--write-flag first")
        dest = write_flag(out, Path(args.write_flag))
        print(f"[rig] wrote {dest} from {rel(out)}")
        print(dest.read_text(), end="")
        return

    rec = compute_sizing(stem)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rec, indent=1) + "\n")
    seg = rec["segment_lengths_m"]
    print(f"[rig] {alias} ({stem}): "
          + ", ".join(f"{k} {seg[k]:.4f}" for k in FLAG_KEYS)
          + f" m; torso on {rec['torso_detail']['n_frames']} frames; "
          f"used_by_capture {rec['used_by_capture']}")
    print(f"[rig] wrote {rel(out)}")
    if args.variants:
        print_variants(stem, alias)


if __name__ == "__main__":
    main()
