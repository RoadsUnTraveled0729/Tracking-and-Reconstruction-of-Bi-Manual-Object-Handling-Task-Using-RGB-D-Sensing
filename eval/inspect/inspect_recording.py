"""Stage 1 inspection of a recording from its raw extractor outputs.

Reads the ArUco raw CSV and the MediaPipe raw CSV (plus both meta
JSONs) produced by the frozen v1 extractors, segments the recording
into the four scenario phases (entry / approach / manipulation /
retreat), and reports coverage, visibility, and an occlusion-event
inventory per phase and globally.

Hard check: if the desk anchor marker (id 2) is not detected in every
frame, the report is stamped ANCHOR FAIL and the exit code is 1 - the
world frame depends on it and downstream processing must not start.

Usage:
    python eval/inspect/inspect_recording.py [--stem STEM]

Outputs eval/reports/<stem>_inspection.json and .md.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
import paths

# Phase segmentation constants. PRESENCE_MIN_RUN discards momentary
# pose flickers at the scene edges; MOVE_WINDOW/MOVE_DIST match the
# carry classifier in v1/integration/analyze_object_offset.py (3 cm
# of marker travel over 7 frames = "moving").
PRESENCE_MIN_RUN = 15
MOVE_WINDOW = 7
MOVE_DIST = 0.03


def runs_of(mask):
    """Maximal [start, stop] (inclusive) runs where mask is True."""
    idx = np.flatnonzero(mask)
    if idx.size == 0:
        return []
    breaks = np.flatnonzero(np.diff(idx) > 1)
    starts = np.r_[idx[0], idx[breaks + 1]]
    stops = np.r_[idx[breaks], idx[-1]]
    return list(zip(starts.tolist(), stops.tolist()))


def segment_phases(person_present, obj_moving, n):
    """Return dict phase -> [start, stop] inclusive frame ranges."""
    present_runs = [r for r in runs_of(person_present)
                    if r[1] - r[0] + 1 >= PRESENCE_MIN_RUN]
    if not present_runs:
        return None
    person_start = present_runs[0][0]
    person_stop = present_runs[-1][1]
    moving = np.flatnonzero(obj_moving)
    if moving.size == 0:
        return {"entry": [0, person_start - 1] if person_start > 0 else None,
                "approach": [person_start, person_stop],
                "manipulation": None,
                "retreat": [person_stop + 1, n - 1] if person_stop < n - 1 else None,
                "person_present": [person_start, person_stop]}
    manip = [int(moving[0]), int(moving[-1])]
    return {
        "entry": [0, person_start - 1] if person_start > 0 else None,
        "approach": [person_start, manip[0] - 1] if manip[0] > person_start else None,
        "manipulation": manip,
        "retreat": [manip[1] + 1, n - 1] if manip[1] < n - 1 else None,
        "person_present": [person_start, person_stop],
    }


def in_phase(frame_idx, phase_range):
    return (phase_range is not None
            and phase_range[0] <= frame_idx <= phase_range[1])


def phase_slice(arr, rng):
    return arr[rng[0]:rng[1] + 1] if rng is not None else arr[0:0]


def gap_events(mask_bad, entity, kind, phases, fps):
    """Events from a bad-mask; cause=out-of-scene for landmark runs
    fully inside entry/retreat."""
    events = []
    for start, stop in runs_of(mask_bad):
        dur = stop - start + 1
        tags = [name for name in ("entry", "approach", "manipulation",
                                  "retreat")
                if phases.get(name) is not None
                and not (stop < phases[name][0] or start > phases[name][1])]
        out_of_scene = (kind.startswith("landmark")
                        and all(t in ("entry", "retreat") for t in tags))
        events.append({
            "entity": entity, "kind": kind,
            "start": int(start), "stop": int(stop),
            "frames": int(dur), "seconds": round(dur / fps, 2),
            "phases": tags,
            "cause": "out-of-scene" if out_of_scene else "uncls",
        })
    return events


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R4_STEM)
    args = ap.parse_args()
    stem = args.stem

    aruco = pd.read_csv(paths.ARUCO_OUT / f"{stem}_aruco_raw.csv")
    lm = pd.read_csv(paths.MP_OUT / f"{stem}_landmarks_raw.csv")
    ameta = json.load(open(paths.ARUCO_OUT / f"{stem}_aruco_raw.meta.json"))
    lmeta = json.load(open(paths.MP_OUT / f"{stem}_landmarks_raw.meta.json"))

    n = len(aruco)
    assert len(lm) == n, f"row mismatch: aruco {n} vs landmarks {len(lm)}"
    t = aruco["time_s"].to_numpy()
    duration = float(t[-1] - t[0])
    fps = (n - 1) / duration if duration > 0 else 30.0

    # --- phase segmentation ---
    person_present = lm["has_pose"].to_numpy().astype(bool)
    obj = aruco[["m1_tx", "m1_ty", "m1_tz"]].to_numpy()
    obj_det = aruco["m1_detected"].to_numpy().astype(bool)
    obj_f = obj.copy()
    obj_f[~obj_det] = np.nan
    obj_ff = pd.DataFrame(obj_f).ffill().bfill().to_numpy()
    disp = np.zeros(n)
    disp[MOVE_WINDOW:] = np.linalg.norm(
        obj_ff[MOVE_WINDOW:] - obj_ff[:-MOVE_WINDOW], axis=1)
    obj_moving = disp > MOVE_DIST
    phases = segment_phases(person_present, obj_moving, n)
    assert phases is not None, "no sustained person presence found"

    # --- per-marker coverage ---
    def marker_stats(rng):
        out = {}
        for mid, name in [(0, "wall"), (1, "object"), (2, "desk")]:
            det = phase_slice(aruco[f"m{mid}_detected"].to_numpy(), rng)
            det = det.astype(bool)
            gaps = runs_of(~det)
            off = rng[0] if rng else 0
            out[f"m{mid}_{name}"] = {
                "frames": int(det.size),
                "detected": int(det.sum()),
                "coverage_pct": round(100.0 * det.mean(), 2) if det.size else None,
                "gaps": [[int(a + off), int(b + off)] for a, b in gaps],
            }
        return out

    # --- per-landmark visibility / src ---
    def landmark_stats(rng):
        out = {}
        for name in paths.LANDMARKS:
            src = phase_slice(lm[f"{name}_src"].to_numpy(), rng)
            vis = phase_slice(lm[f"{name}_vis"].to_numpy(), rng)
            pose = phase_slice(person_present, rng)
            m = pose  # src is meaningful only when a pose exists
            tot = int(m.sum())
            s = src[m]
            v = vis[m]
            out[name] = {
                "pose_frames": tot,
                "pct_ok": round(100.0 * np.mean(s == 0), 2) if tot else None,
                "pct_low_vis": round(100.0 * np.mean(s == 1), 2) if tot else None,
                "pct_no_depth": round(100.0 * np.mean(s == 2), 2) if tot else None,
                "vis_median": round(float(np.nanmedian(v)), 3) if tot else None,
                "vis_p10": round(float(np.nanpercentile(v, 10)), 3) if tot else None,
            }
        return out

    named_phases = [(k, phases[k]) for k in
                    ("entry", "approach", "manipulation", "retreat")]
    report = {
        "stem": stem,
        "frames": n,
        "duration_s": round(duration, 2),
        "fps": round(fps, 2),
        "resolution": "640x480",
        "frames_with_pose": int(person_present.sum()),
        "phases": {k: v for k, v in phases.items()},
        "phase_stats": {},
        "global": {"markers": marker_stats(None if False else [0, n - 1]),
                   "landmarks": landmark_stats([0, n - 1])},
    }
    for name, rng in named_phases:
        if rng is None:
            report["phase_stats"][name] = None
            continue
        report["phase_stats"][name] = {
            "range": rng,
            "seconds": round((rng[1] - rng[0] + 1) / fps, 2),
            "markers": marker_stats(rng),
            "landmarks": landmark_stats(rng),
        }

    # --- occlusion event inventory v0 ---
    events = []
    for mid, name in [(0, "wall"), (1, "object"), (2, "desk")]:
        bad = ~aruco[f"m{mid}_detected"].to_numpy().astype(bool)
        events += gap_events(bad, f"marker_{name}", "marker-not-detected",
                             phases, fps)
    no_pose_bad = ~person_present
    events += gap_events(no_pose_bad, "pose", "landmark-no-pose", phases, fps)
    for name in paths.LANDMARKS:
        src = lm[f"{name}_src"].to_numpy()
        bad = person_present & (src != 0)
        events += gap_events(bad, name, "landmark-blocked", phases, fps)
    events.sort(key=lambda e: e["start"])
    report["events"] = events
    report["event_summary"] = {
        "total": len(events),
        "out_of_scene": sum(e["cause"] == "out-of-scene" for e in events),
        "unclassified": sum(e["cause"] == "uncls" for e in events),
        "longest_in_scene": max(
            (e for e in events if e["cause"] != "out-of-scene"),
            key=lambda e: e["frames"], default=None),
    }

    # --- wrist liveness per phase ---
    report["wrist_live"] = {}
    for pname, rng in named_phases:
        if rng is None:
            continue
        row = {}
        for w in ("left_wrist", "right_wrist"):
            src = phase_slice(lm[f"{w}_src"].to_numpy(), rng)
            pose = phase_slice(person_present, rng)
            row[w] = round(100.0 * np.mean((src == 0) & pose), 2)
        report["wrist_live"][pname] = row

    # --- desk anchor hard check ---
    desk_gaps = report["global"]["markers"]["m2_desk"]["gaps"]
    anchor_ok = len(desk_gaps) == 0
    report["anchor_check"] = {
        "ok": anchor_ok,
        "gaps": desk_gaps,
        "verdict": "PASS: desk anchor detected in every frame" if anchor_ok
        else "FAIL: desk anchor occluded - STOP, world frame unreliable",
    }

    # --- representative-frame shortlist (manipulation phase only) ---
    shortlist = []
    if phases["manipulation"] is not None:
        a, b = phases["manipulation"]
        all_markers = np.ones(n, dtype=bool)
        for mid in (0, 1, 2):
            all_markers &= aruco[f"m{mid}_detected"].to_numpy().astype(bool)
        all_lm_ok = person_present.copy()
        min_vis = np.full(n, np.inf)
        for name in paths.LANDMARKS:
            all_lm_ok &= lm[f"{name}_src"].to_numpy() == 0
            min_vis = np.minimum(min_vis, lm[f"{name}_vis"].to_numpy())
        max_reproj = np.zeros(n)
        for mid in (0, 1, 2):
            r = aruco[f"m{mid}_reproj_px"].to_numpy()
            max_reproj = np.maximum(max_reproj, np.nan_to_num(r, nan=99.0))
        cand = np.flatnonzero(all_markers & all_lm_ok)
        cand = cand[(cand >= a) & (cand <= b)]
        order = sorted(cand, key=lambda f: (-min_vis[f], max_reproj[f]))
        shortlist = [{"frame": int(f),
                      "time_s": round(float(t[f]), 2),
                      "min_landmark_vis": round(float(min_vis[f]), 3),
                      "max_marker_reproj_px": round(float(max_reproj[f]), 3)}
                     for f in order[:10]]
        report["candidate_frames_total"] = int(cand.size)
    report["representative_shortlist"] = shortlist

    paths.EVAL_REPORTS.mkdir(parents=True, exist_ok=True)
    out_json = paths.EVAL_REPORTS / f"{stem}_inspection.json"
    with open(out_json, "w") as f:
        json.dump(report, f, indent=1)

    # --- markdown summary ---
    md = [f"# Inspection: {stem}", "",
          f"Frames {n}, duration {duration:.2f} s, {fps:.2f} fps, 640x480.",
          f"Frames with pose: {int(person_present.sum())} "
          f"({100.0 * person_present.mean():.1f} percent).", "",
          "## Anchor check", "", report["anchor_check"]["verdict"], "",
          "## Phases", ""]
    for pname, rng in named_phases:
        if rng is None:
            md.append(f"- {pname}: absent")
        else:
            md.append(f"- {pname}: frames {rng[0]}-{rng[1]} "
                      f"({(rng[1] - rng[0] + 1) / fps:.1f} s)")
    md += ["", "## Marker coverage (global)", ""]
    for key, s in report["global"]["markers"].items():
        md.append(f"- {key}: {s['detected']}/{s['frames']} "
                  f"({s['coverage_pct']} percent), {len(s['gaps'])} gaps")
    md += ["", "## Landmark status (percent of pose frames, global)", "",
           "| landmark | ok | low_vis | no_depth | vis median | vis p10 |",
           "|---|---|---|---|---|---|"]
    for name, s in report["global"]["landmarks"].items():
        md.append(f"| {name} | {s['pct_ok']} | {s['pct_low_vis']} | "
                  f"{s['pct_no_depth']} | {s['vis_median']} | {s['vis_p10']} |")
    md += ["", "## Occlusion events", "",
           f"Total {len(events)}; out-of-scene "
           f"{report['event_summary']['out_of_scene']}; in-scene "
           f"{report['event_summary']['unclassified']}.", ""]
    in_scene = [e for e in events if e["cause"] != "out-of-scene"]
    in_scene.sort(key=lambda e: -e["frames"])
    md += ["Longest 15 in-scene events:", "",
           "| entity | kind | frames | span | seconds | phases |", "|---|---|---|---|---|---|"]
    for e in in_scene[:15]:
        md.append(f"| {e['entity']} | {e['kind']} | {e['frames']} | "
                  f"{e['start']}-{e['stop']} | {e['seconds']} | "
                  f"{'/'.join(e['phases'])} |")
    md += ["", "## Wrist liveness per phase (percent ok)", ""]
    for pname, row in report["wrist_live"].items():
        md.append(f"- {pname}: left {row['left_wrist']}, "
                  f"right {row['right_wrist']}")
    md += ["", "## Representative-frame shortlist (manipulation phase)", ""]
    for c in shortlist:
        md.append(f"- frame {c['frame']} (t={c['time_s']} s, min vis "
                  f"{c['min_landmark_vis']}, max reproj "
                  f"{c['max_marker_reproj_px']} px)")
    out_md = paths.EVAL_REPORTS / f"{stem}_inspection.md"
    out_md.write_text("\n".join(md) + "\n")

    print(f"[+] {out_json}")
    print(f"[+] {out_md}")
    print(report["anchor_check"]["verdict"])
    sys.exit(0 if anchor_ok else 1)


if __name__ == "__main__":
    main()
