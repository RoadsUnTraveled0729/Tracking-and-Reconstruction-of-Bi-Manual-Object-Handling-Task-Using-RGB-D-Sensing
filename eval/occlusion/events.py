"""Refined real-occlusion event inventory (stage 5a).

Takes the stage-1 inspection events and adds: overlap with carry
segments and grip episodes (was the box in a hand during the event),
and a cause tag refined by context. Writes the flat CSV the thesis
table draws from.

Run: python eval/occlusion/events.py
Output: eval/reports/r4_occlusion_events.csv
"""

import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "common"))
import paths


def overlaps(a, b, spans):
    return any(not (b < s or a > e) for s, e in spans)


def main():
    stem = paths.R4_STEM
    insp = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_inspection.json").read_text())
    fit = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_offset_fit.json").read_text())
    constancy = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_stage2_constancy.json").read_text())
    carry_spans = [tuple(s) for s in fit["carry_segments"]]
    episodes = {side: [tuple(e["frames"]) for e in
                       (constancy["per_hand"][side] or {})
                       .get("episodes", [])]
                for side in ("left", "right")}

    rows = []
    for e in insp["events"]:
        cause = e["cause"]
        during_carry = overlaps(e["start"], e["stop"], carry_spans)
        side = ("left" if e["entity"].startswith("left") else
                "right" if e["entity"].startswith("right") else "")
        during_grip = bool(side) and overlaps(e["start"], e["stop"],
                                              episodes.get(side, []))
        if cause == "uncls":
            if e["entity"] in ("left_wrist", "left_elbow") and during_carry:
                cause = "carried-box-blocks-left-arm"
            elif e["entity"] == "marker_wall" and "approach" in e["phases"]:
                cause = "person-crosses-wall-marker"
            elif e["entity"] == "marker_object" and during_carry:
                cause = "object-marker-view-loss"
        rows.append({
            "entity": e["entity"], "kind": e["kind"],
            "start": e["start"], "stop": e["stop"],
            "frames": e["frames"], "seconds": e["seconds"],
            "phases": "/".join(e["phases"]), "cause": cause,
            "during_carry": int(during_carry),
            "during_grip_episode": int(during_grip),
        })

    out = paths.EVAL_REPORTS / "r4_occlusion_events.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    in_scene = [r for r in rows if r["cause"] != "out-of-scene"]
    print(f"[+] {out}: {len(rows)} events "
          f"({len(in_scene)} in scene, "
          f"{sum(r['during_carry'] for r in in_scene)} during carry)")


if __name__ == "__main__":
    main()
