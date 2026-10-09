#!/usr/bin/env python3
"""Reference path of a rail recording, the definition of E-024 (user,
2026-09-01), written for any rail take.

  leg 1  from the parked start straight back, away from the camera
         (z only), to W1, the foot of the lift at the rail's depth;
  leg 2  straight up (y only) to W2, the start of the rail at rail
         height;
  leg 3  along the rail (x only) to W3, the far end of the rail.

The corners come from the physical geometry, not from the track's own
corners: the parked start (mean of the parked frames), the depth and
height of the line fitted to the slide samples, and the far end of that
line. Track, segmentation, levelling and the line fit come from
eval/gt/eval_rail_scenario.py. The same computation produced
eval/reports/r6b_waypoints.json through writing/v7/scripts/
make_ch7_rail_traj_fig.py; this tool writes <alias>_waypoints.json for
the later takes (r7, the two-hand take, E-034) without touching the
pinned r6b file.

Run: python eval/gt/rail_waypoints.py --stem STEM
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
import paths                       # noqa: E402
import eval_rail_scenario as ers   # noqa: E402


def waypoints(stem):
    track = ers.load_track(stem)
    seg = ers.segment(track)
    xyz, fr = track["xyz"], track["frame"]
    idx = seg["idx"]
    P = xyz[idx]
    desk_y = seg["desk_y"]
    start = xyz[seg["parked"]].mean(axis=0)
    c, d, along, _, _ = ers.fit_line(xyz[seg["rail"]])
    if d[0] < 0:
        d, along = -d, -along
    ends = np.array([c + along.min() * d, c + along.max() * d])
    rail_y, rail_z, x_end = float(c[1]), float(c[2]), float(ends[1, 0])
    W = {"start": start,
         "W1": np.array([start[0], start[1], rail_z]),
         "W2": np.array([start[0], rail_y, rail_z]),
         "W3": np.array([x_end, rail_y, rail_z])}
    legs = {"leg1_back_cm": float(rail_z - start[2]) * 100,
            "leg2_up_cm": float(rail_y - start[1]) * 100,
            "leg3_rail_cm": float(x_end - start[0]) * 100}
    h = np.convolve(P[:, 1], np.ones(9) / 9, mode="same")
    k_lift = int(np.flatnonzero(h > desk_y + 0.01)[0])
    k_rail = int(np.flatnonzero(h >= rail_y - 0.005)[0])
    turns = {"lift_begins_frame": int(fr[idx[k_lift]]),
             "rail_reached_frame": int(fr[idx[k_rail]]),
             "last_frame": int(fr[idx[-1]]),
             "parked_frames": [int(fr[seg["parked"][0]]),
                               int(fr[seg["parked"][-1]])]}
    return {
        "stem": stem,
        "frame": "gravity-levelled desk world (x, y up, z away from the "
                 "camera), metres",
        "definition": {
            "leg1": "from the parked start straight back (z only) to W1, "
                    "the foot of the lift at the depth of the fitted rail line",
            "leg2": "straight up (y only) to W2, the start of the rail at "
                    "the height of the fitted rail line",
            "leg3": "along the rail (x only) to W3, the far end of the "
                    "fitted rail line"},
        "waypoints": {k: [round(float(v), 4) for v in W[k]] for k in W},
        "legs_cm": {k: round(v, 2) for k, v in legs.items()},
        "rail_line": {"height_m": round(rail_y, 4), "depth_m": round(rail_z, 4),
                      "x_from_m": round(float(ends[0, 0]), 4),
                      "x_to_m": round(x_end, 4)},
        "desk_level_m": round(desk_y, 4), "track_turns": turns}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R7_STEM)
    args = ap.parse_args()
    alias = paths.ALIAS[args.stem]
    if alias == "r6b":
        sys.exit("r6b_waypoints.json is pinned (make_ch7_rail_traj_fig.py)")
    spec = waypoints(args.stem)
    out = paths.EVAL_REPORTS / f"{alias}_waypoints.json"
    out.write_text(json.dumps(spec, indent=1))
    for k in ("start", "W1", "W2", "W3"):
        print("%-5s x=%+.3f y=%+.3f z=%+.3f" % (k, *spec["waypoints"][k]))
    print("legs (cm):", spec["legs_cm"], "| track turns:", spec["track_turns"])
    print("[+]", out)


if __name__ == "__main__":
    main()
