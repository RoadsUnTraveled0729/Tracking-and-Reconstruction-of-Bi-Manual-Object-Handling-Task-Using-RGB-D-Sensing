#!/usr/bin/env python3
"""Evaluate an object track against the raised-rail path (the
no-occlusion scenario recordings, 2026-08-31 setup).

The scenario: the cube starts parked on the desk, is lifted onto a
straight horizontal wooden rail, and is slid along the rail to its far
end. The rail physically constrains the slide, so the designed path of
the slide is a straight line at rail height; the ground truth of this
scenario is that line, the way the drawn path was the ground truth of
the waypoint scenario (eval/gt/detect_waypoints.py, which stays pinned
to that recording's 7-station step plan).

Segmentation is geometric, not tuned:
  - the track is first levelled by the calibrated gravity (the desk-
    marker frame it is stored in is tilted about 32 deg), so "height"
    below is the true vertical;
  - the rail height is the upper mode of the height histogram of the
    detected track (desk level and rail level are the two modes);
  - rail frames are frames within half a cube size (3.5 cm) of that
    mode, after the first sustained arrival in the band;
  - the parked segment is the initial low-speed span at desk level;
    the lift is what lies between.

The rail line is fit to the rail frames by total least squares (first
principal component), and the errors reported are perpendicular
distances of the tracked cube centre to that line. This is offline
geometry over the finished track; no causality is claimed.

Outputs: eval/reports/<alias>_rail_eval.md, .json, and a one-glance
figure <alias>_rail_eval.png (3D main panel, projections secondary).
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1] / "common"))
sys.path.insert(0, str(HERE.parents[1] / "offset"))
import paths  # noqa: E402
from carry import LeveledWorld  # noqa: E402

CUBE_HALF_M = 0.035          # half of the 70 mm cube: the band width
DWELL_SPEED_M_S = 0.02       # below this the cube is considered at rest


def load_track(stem):
    """Marker-centre track in the GRAVITY-LEVELLED desk world (x, y up,
    z), metres, origin at the desk marker. The stored world track is the
    desk-marker frame, whose card sits on a stand tilted about 32 deg
    from vertical, so its axes are not level; the calibrated gravity
    (the wall marker's in-plane up axis, eval/offset/carry.LeveledWorld)
    rotates the track so that y is the true vertical before any height
    reasoning below. Same frame as detect_waypoints.py's leveled_xyz.
    """
    df = pd.read_csv(paths.object_world_filtered(stem))
    unity = df[["unity_px", "unity_py", "unity_pz"]].apply(
        pd.to_numeric, errors="coerce").to_numpy(float)
    valid = np.isfinite(unity).all(axis=1) & (df["detected"].to_numpy() == 1)
    calib = json.loads(Path(paths.calib_for(stem)).read_text())
    world = LeveledWorld(calib)
    xyz = np.full_like(unity, np.nan)
    xyz[valid] = world.level(unity[valid])
    return {"frame": df["frame"].to_numpy(int),
            "time_s": df["time_s"].to_numpy(float),
            "xyz": xyz, "valid": valid,
            "gravity_unity": [round(float(v), 4) for v in world.g],
            "calib": str(paths.calib_for(stem))}


def segment(track):
    """Split valid frames into parked / lift / rail spans (frame indices)."""
    v, xyz, t = track["valid"], track["xyz"], track["time_s"]
    idx = np.flatnonzero(v)
    y = xyz[idx, 1]
    # two height modes: desk level (parked) and rail level
    hist, edges = np.histogram(y, bins=40)
    centers = 0.5 * (edges[:-1] + edges[1:])
    lo_mode = centers[np.argmax(hist * (centers <= np.median(y)))]
    hi_mode = centers[np.argmax(hist * (centers > np.median(y)))]
    in_band = np.abs(y - hi_mode) <= CUBE_HALF_M
    # first sustained arrival: first index from which the cube stays in
    # the band for at least 1 s of valid frames
    run, arrive = 0, None
    for k, b in enumerate(in_band):
        run = run + 1 if b else 0
        if run >= 30:
            arrive = k - run + 1
            break
    if arrive is None:
        raise SystemExit("no sustained arrival at rail height; not a "
                         "rail recording?")
    # parked: initial desk-level low-speed span
    speed = np.zeros(len(idx))
    dt = np.diff(t[idx])
    speed[1:] = np.linalg.norm(np.diff(xyz[idx], axis=0), axis=1) / dt
    parked_end = 0
    for k in range(len(idx)):
        if np.abs(y[k] - lo_mode) > CUBE_HALF_M or speed[k] > 2 * DWELL_SPEED_M_S:
            parked_end = k
            break
    rail = idx[arrive:][in_band[arrive:]]
    return {"idx": idx, "parked": idx[:parked_end],
            "lift": idx[parked_end:arrive], "rail": rail,
            "desk_y": float(lo_mode), "rail_y": float(hi_mode)}


def fit_line(P):
    c = P.mean(axis=0)
    _, S, Vt = np.linalg.svd(P - c, full_matrices=False)
    d = Vt[0]
    t = (P - c) @ d
    resid_vec = (P - c) - np.outer(t, d)
    return c, d, t, resid_vec, S / np.sqrt(len(P))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", required=True)
    args = ap.parse_args()
    stem = args.stem
    alias = paths.ALIAS[stem]
    track = load_track(stem)
    seg = segment(track)
    xyz, t = track["xyz"], track["time_s"]

    c, d, along, resid_vec, sigma = fit_line(xyz[seg["rail"]])
    if d[0] < 0:
        d = -d
        along = -along
    resid = np.linalg.norm(resid_vec, axis=1)
    v_res = np.abs(resid_vec[:, 1])                    # vertical part
    h_res = np.sqrt(resid_vec[:, 0]**2 + resid_vec[:, 2]**2)
    tilt = float(np.degrees(np.arcsin(abs(d[1]) / np.linalg.norm(d))))

    # traversal structure along the rail
    rt = t[seg["rail"]]
    vt = np.diff(along) / np.diff(rt)
    moving = np.abs(vt) > 0.03
    sgn = np.sign(vt[moving])
    flips = int((np.diff(sgn) != 0).sum()) if sgn.size else 0

    # lift segment straightness (secondary; the lift is free-space)
    lift = {}
    if len(seg["lift"]) >= 10:
        _, dl, tl, rl_vec, _ = fit_line(xyz[seg["lift"]])
        lift = {"n": int(len(seg["lift"])),
                "travel_cm": round(float(np.ptp(tl)) * 100, 1),
                "tilt_from_vertical_deg": round(float(np.degrees(
                    np.arccos(abs(dl[1]) / np.linalg.norm(dl)))), 1),
                "resid_median_cm": round(float(np.median(
                    np.linalg.norm(rl_vec, axis=1))) * 100, 2)}

    out = {
        "stem": stem, "scenario": "no-occlusion rail (2026-08-31 setup)",
        "frame": "gravity-levelled desk world (y up), from " + track["calib"],
        "gravity_up_unity": track["gravity_unity"],
        "frames_total": int(len(track["frame"])),
        "frames_valid": int(track["valid"].sum()),
        "desk_height_m": round(seg["desk_y"], 4),
        "rail_height_m": round(seg["rail_y"], 4),
        "parked_frames": int(len(seg["parked"])),
        "lift": lift,
        "rail": {
            "n": int(len(seg["rail"])),
            "span_s": [round(float(rt[0]), 2), round(float(rt[-1]), 2)],
            "travel_cm": round(float(np.ptp(along)) * 100, 1),
            "tilt_from_horizontal_deg": round(tilt, 2),
            "pca_sigma_cm": [round(float(s) * 100, 2) for s in sigma],
            "perp_median_cm": round(float(np.median(resid)) * 100, 2),
            "perp_p95_cm": round(float(np.percentile(resid, 95)) * 100, 2),
            "perp_max_cm": round(float(resid.max()) * 100, 2),
            "vertical_median_cm": round(float(np.median(v_res)) * 100, 2),
            "horizontal_median_cm": round(float(np.median(h_res)) * 100, 2),
            "direction_flips_moving": flips,
        },
    }

    rep = paths.EVAL_REPORTS / f"{alias}_rail_eval"
    rep.with_suffix(".json").write_text(json.dumps(out, indent=1))

    lines = []
    a = lines.append
    a(f"# Rail-path evaluation: {stem} ({alias})")
    a("")
    a("Scenario: no occlusion. The cube is lifted from the desk onto a")
    a("straight horizontal rail and slid to its far end; the rail is the")
    a("physical ground-truth path of the slide. Errors are perpendicular")
    a("distances of the tracked cube centre to the total-least-squares")
    a("line through the rail-segment samples. Offline geometry, no")
    a("causality claimed. Segmentation: rail height is the upper mode of")
    a("the height histogram, band = half a cube (3.5 cm). Frame: the")
    a("gravity-levelled desk world (y = true vertical from the calibrated")
    a("wall marker), not the tilted desk-marker frame the track is stored in.")
    a("")
    a(f"- frames: {out['frames_valid']}/{out['frames_total']} tracked")
    a(f"- desk level {out['desk_height_m']*100:.1f} cm, rail level "
      f"{out['rail_height_m']*100:.1f} cm above the desk-marker origin")
    a(f"- parked {out['parked_frames']} frames; lift "
      f"{lift.get('n', 0)} frames, travel {lift.get('travel_cm', 0)} cm, "
      f"tilt from vertical {lift.get('tilt_from_vertical_deg', 'NA')} deg")
    r = out["rail"]
    a(f"- rail segment: {r['n']} frames over t = {r['span_s'][0]} to "
      f"{r['span_s'][1]} s, travel {r['travel_cm']} cm, line tilt from "
      f"horizontal {r['tilt_from_horizontal_deg']} deg")
    a("")
    a("Rail-line error of the tracked centre:")
    a("")
    a("| statistic | value |")
    a("|---|---|")
    a(f"| perpendicular median | {r['perp_median_cm']} cm |")
    a(f"| perpendicular p95 | {r['perp_p95_cm']} cm |")
    a(f"| perpendicular max | {r['perp_max_cm']} cm |")
    a(f"| vertical component median | {r['vertical_median_cm']} cm |")
    a(f"| horizontal component median | {r['horizontal_median_cm']} cm |")
    a(f"| direction reversals while moving | {r['direction_flips_moving']} |")
    a("")
    a("The perpendicular error mixes tracking error with how the cube")
    a("rides against the rail; the rail constrains the hand, so this is")
    a("the tightest ground truth the setup provides.")
    a("")
    rep.with_suffix(".md").write_text("\n".join(lines))

    # one-glance figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    P = xyz[track["valid"]]
    Tv = t[track["valid"]]
    fig = plt.figure(figsize=(12, 5.2))
    ax = fig.add_subplot(121, projection="3d")
    sc = ax.scatter(P[:, 0], P[:, 2], P[:, 1], c=Tv, s=3, cmap="viridis")
    R = xyz[seg["rail"]]
    lo, hi = along.min(), along.max()
    ends = np.array([c + lo * d, c + hi * d])
    ax.plot(ends[:, 0], ends[:, 2], ends[:, 1], "r-", lw=2,
            label="fitted rail line")
    ax.set_xlabel("x (m)")
    ax.set_ylabel("z (m)")
    ax.set_zlabel("y up (m)")
    ax.set_title(f"{alias}: track and rail line (colour = time)")
    ax.legend(loc="upper left", fontsize=8)
    fig.colorbar(sc, ax=ax, shrink=0.55, label="time (s)")
    ax2 = fig.add_subplot(222)
    ax2.plot(along * 100, resid_vec[:, 1] * 100, ".", ms=2)
    ax2.axhline(0, color="r", lw=1)
    ax2.set_ylabel("vertical dev (cm)")
    ax2.set_title("deviation from rail line vs position along rail")
    ax3 = fig.add_subplot(224)
    h_signed = resid_vec[:, 2]
    ax3.plot(along * 100, h_signed * 100, ".", ms=2)
    ax3.axhline(0, color="r", lw=1)
    ax3.set_xlabel("along rail (cm)")
    ax3.set_ylabel("depth dev (cm)")
    plt.tight_layout()
    png = rep.with_suffix(".png")
    plt.savefig(png, dpi=130)
    print("PASS: rail evaluation written")
    print("  report:", rep.with_suffix(".md"))
    print("  figure:", png)
    print("  rail perp median %.2f cm  p95 %.2f cm  travel %.1f cm  "
          "tilt %.2f deg" % (r["perp_median_cm"], r["perp_p95_cm"],
                             r["travel_cm"], r["tilt_from_horizontal_deg"]))


if __name__ == "__main__":
    main()
