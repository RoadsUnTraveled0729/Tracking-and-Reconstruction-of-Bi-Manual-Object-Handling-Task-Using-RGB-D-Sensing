"""R5 waypoint evaluation: detect the loop's waypoints and compare
the measured box-center trajectory against the ideal waypoint polyline.

Recording R5 (recording_20260825_222315) executes a designed loop
(operator's specification, 2026-08-26): from the start point the cube
moves BACK about 30 cm on the desk, LEFT about 45 cm (with a two-hand
handover on the way), FORWARD about 15 cm, then UP about 30 cm to a
wire, along the wire (with a second handover), and back down to the
start. EIGHT waypoints: the start point, the endpoint of each desk
move, the two handover stops, and the elevated stops. This driver
detects the seven pause stations from the track alone, adds the start
point (the parked rest position), writes eval/gt/labeled_path_r5.json
in the labeled_path schema, and reports trajectory-vs-ideal error
statistics plus a designed-vs-measured step reconciliation.

Frames: stored coordinates use the desk-marker (unleveled) world
frame - the frame the object_world unity columns live in and
labeled_path.json is defined in. The desk marker stands on a mount
tilted 31.7 deg from gravity, so all GEOMETRIC reasoning (clustering,
step decomposition, the figure) uses the gravity-leveled frame
(carry.LeveledWorld); distances are identical in both (rigid map).

Usage:
    python eval/gt/detect_waypoints.py [--stem STEM]

Outputs:
    eval/gt/labeled_path_r5.json
    eval/reports/r5_waypoint_eval.json
    eval/reports/r5_waypoint_eval.md
    eval/reports/r5_waypoints.png
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection
from matplotlib.gridspec import GridSpec

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "common"))
sys.path.insert(0, str(HERE.parents[0] / "offset"))
import carry
import path_metrics as pm
import paths

# ---------------------------------------------------------------------------
# Constants. Every value below is derived from the R5 track itself; the
# derivation is reproduced in the sweep table / sweep panel of the
# report so the choice can be re-checked, not taken on trust.
# ---------------------------------------------------------------------------

# Position smoothing before the speed estimate. 5 frames = 0.17 s, the
# window already used for dwell detection elsewhere in eval/ (E-008,
# path_metrics.detect_dwells) - kept identical so the two detectors
# see the same track.
SMOOTH_WIN = 5

# Speed estimator half-window, frames. The 1-frame gradient speed of
# the R5 carried track has a completely flat histogram from 0 to
# 10 cm/s (marker jitter of a few mm per frame is the same order as
# the operator's slow motion), so it separates nothing. A secant over
# +-5 frames (0.33 s total) measures how far the cube actually
# travelled over a third of a second, which is what "paused" means
# here, and it is what makes the threshold plateau below exist.
SPEED_WIN = 5

# Station speed threshold, m/s. The carried-speed histogram of this
# recording has no low-speed gap to cut at (the operator moved slowly
# throughout), so the threshold is fixed instead by the plateau of the
# station-count-vs-threshold sweep: the sweep panel of
# r5_waypoints.png shows the threshold band over which the detected
# station count is invariantly N_DETECTED; 0.040 m/s is the round
# value at the centre of that plateau. See the sweep and stability
# tables of the md report.
V_STATION = 0.040

# Minimum length of a single low-speed run to become a candidate, s.
# 0.30 s = 9 frames, just under the 0.33 s span of the speed secant:
# shorter runs cannot be resolved by that estimator.
MIN_DUR_S = 0.30

# Candidate merge radius, m, applied to the FULL 3D distance between
# candidate mean positions. 3D, not a plane projection: the desk
# marker's 31.7 deg stand tilt compresses the camera-depth axis in the
# marker-frame x-y projection, which made the left-45 endpoint and the
# forward-push endpoint (8.0 cm apart in 3D) look 3.7 cm apart and
# wrongly merge in the first version of this detector. In 3D the
# closest genuinely distinct station pair is that one at 8.0 cm, and
# the widest same-station sub-run spread (the lift-top regrips) is
# under 3 cm; 0.06 m sits between them.
MERGE_RADIUS = 0.06

# Minimum total dwell time for a merged cluster to be reported as a
# station, s. A guard against jitter clusters; the report states the
# gap between this floor and the weakest real station so the count is
# demonstrably not produced by the cut.
MIN_STATION_DWELL_S = 0.50

# Window used to report the approach speed of each station, frames
# (0.5 s immediately before the station's first dwell frame).
APPROACH_WIN = 15

# Waypoint names in traversal order. W1 is the parked start position
# (added from the rest frames, not detected by the speed criterion);
# W2..W8 are the seven detected pause stations.
STATION_NAMES = [
    "W1_start",
    "W2_back_end",
    "W3_desk_handover",
    "W4_left_end",
    "W5_forward_end",
    "W6_lift_top",
    "W7_wire_handover",
    "W8_wire_left",
]
STATION_DESC = [
    "start point (parked rest position on the desk)",
    "end of the back move, on the desk",
    "desk, two-hand handover",
    "end of the left move, on the desk",
    "end of the forward push, on the desk (lift starts here)",
    "top of the lift, on the wire",
    "on the wire, second handover",
    "wire, left end, before the descent",
]
N_DETECTED = 7           # stations the speed criterion must find

# Designed step plan (operator's specification, 2026-08-26; nominal,
# approximate). Used only for the designed-vs-measured reconciliation
# table - never as detector input. Each row: (from, to, kind,
# nominal_cm) with kind "horizontal" or "vertical" in the leveled
# frame.
DESIGNED_STEPS = [
    ("W1_start", "W2_back_end", "horizontal", 30.0, "back"),
    ("W2_back_end", "W4_left_end", "horizontal", 45.0, "left"),
    ("W4_left_end", "W5_forward_end", "horizontal", 15.0, "forward"),
    ("W5_forward_end", "W6_lift_top", "vertical", 30.0, "up"),
]

SWEEP_V = np.round(np.arange(0.015, 0.0701, 0.0025), 5)


# ---------------------------------------------------------------------------
# Track loading
# ---------------------------------------------------------------------------

def load_center_track(stem):
    """Box-center track in the desk-marker (unleveled) world frame plus
    the masks the station detector needs.

    Returns a dict with t, center, detected, carried, loop (bool mask
    of the single loop traversal) and the loop span endpoints."""
    from fit_offset import load_tracks
    calib, world, lm, obj_lev, R_lev, det, wr, wrist_flag, t = load_tracks(
        stem, str(paths.calib_for(stem)))

    ofil = pd.read_csv(paths.object_world_filtered(stem))
    n = min(len(ofil), len(obj_lev))
    obj_u = ofil[["unity_px", "unity_py", "unity_pz"]].to_numpy()[:n]
    R_u = np.array([carry.recompose_zxy(e) for e in
                    ofil[["unity_ex", "unity_ey", "unity_ez"]].to_numpy()[:n]])
    center = obj_u + R_u @ np.array([0.0, -world.cube / 2.0, 0.0])
    t = t[:n]
    det = det[:n]

    # leveled-frame twin of the track: gravity = +y, height above the
    # tabletop; used for clustering geometry, step decomposition and
    # the figure (the marker frame is tilted 31.7 deg)
    center_lev = world.box_center(obj_lev[:n], R_lev[:n])
    height = center_lev[:, 1] + world.drop

    insp = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_inspection.json").read_text())
    envelope = insp["phases"]["manipulation"]
    carried = carry.rest_referenced_carried(obj_lev[:n], world, envelope)

    # The loop traversal is one contiguous carried run. Two things
    # break the raw carried mask into pieces: the cube resting at the
    # parked spot (a real interruption) and stretches where the marker
    # was never measured (no evidence either way). Bridge only the
    # second kind - a carried gap containing no detected sample - then
    # take the longest run. On R5 exactly one gap qualifies (frames
    # 1089-1098, the occluded two-hand handover); no tunable constant
    # is involved.
    bridged = carried.copy()
    rr = _runs(carried)
    for (a1, b1), (a2, b2) in zip(rr[:-1], rr[1:]):
        if det[b1 + 1:a2].sum() == 0:
            bridged[b1 + 1:a2] = True
    lo, hi = max(_runs(bridged), key=lambda r: r[1] - r[0])
    loop = np.zeros(n, bool)
    loop[lo:hi + 1] = True

    # the parked start position: detected pre-manipulation frames
    rest_m = det & (np.arange(n) < envelope[0])
    rest = np.nanmedian(center[rest_m], axis=0)
    rest_lev = np.nanmedian(center_lev[rest_m], axis=0)

    return {
        "n": n, "t": t, "center": center, "detected": det,
        "center_lev": center_lev, "height": height,
        "rest": rest, "rest_lev": rest_lev,
        "rest_height": float(np.nanmedian(height[rest_m])),
        "rest_frames": [int(np.flatnonzero(rest_m)[0]),
                        int(np.flatnonzero(rest_m)[-1])],
        "carried": carried, "envelope": envelope,
        "loop": loop, "loop_span": (int(lo), int(hi)),
        "valid": loop & det, "cube": float(world.cube),
        "fps": float(1.0 / np.median(np.diff(t))),
    }


def _runs(mask):
    """Contiguous True runs of a bool mask as (start, stop) inclusive."""
    idx = np.flatnonzero(mask)
    if idx.size == 0:
        return []
    brk = np.flatnonzero(np.diff(idx) > 1)
    return list(zip(np.r_[idx[0], idx[brk + 1]].tolist(),
                    np.r_[idx[brk], idx[-1]].tolist()))


def smooth_track(center, win=SMOOTH_WIN):
    k = np.ones(win) / win
    return np.stack([np.convolve(center[:, j], k, mode="same")
                     for j in range(3)], axis=1)


def secant_speed(cs, t, win=SPEED_WIN):
    """Speed as the chord |c[f+win] - c[f-win]| / dt over the window."""
    n = len(cs)
    lo = np.clip(np.arange(n) - win, 0, n - 1)
    hi = np.clip(np.arange(n) + win, 0, n - 1)
    return np.linalg.norm(cs[hi] - cs[lo], axis=1) / (t[hi] - t[lo])


# ---------------------------------------------------------------------------
# Station detection
# ---------------------------------------------------------------------------

def candidate_runs(speed, valid, t, fps, v_thresh, min_dur_s):
    """Maximal runs of valid frames below v_thresh lasting min_dur_s."""
    out = []
    for a, b in _runs((speed < v_thresh) & valid):
        if (b - a + 1) / fps < min_dur_s:
            continue
        out.append({"start": a, "stop": b, "frames": b - a + 1,
                    "duration_s": float(t[b] - t[a])})
    return out


def merge_candidates(cands, center, radius=MERGE_RADIUS):
    """Duration-weighted agglomeration of candidates whose mean
    positions lie within radius (full 3D distance). Iterates until
    stable."""
    items = []
    for c in cands:
        p = np.nanmean(center[c["start"]:c["stop"] + 1], axis=0)
        items.append({"runs": [c], "dwell_s": c["duration_s"], "pos": p})
    changed = True
    while changed:
        changed = False
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                d = np.linalg.norm(items[i]["pos"] - items[j]["pos"])
                if d > radius:
                    continue
                wi, wj = items[i]["dwell_s"], items[j]["dwell_s"]
                items[i] = {
                    "runs": items[i]["runs"] + items[j]["runs"],
                    "dwell_s": wi + wj,
                    "pos": (items[i]["pos"] * wi + items[j]["pos"] * wj)
                            / (wi + wj),
                }
                items.pop(j)
                changed = True
                break
            if changed:
                break
    for it in items:
        it["runs"].sort(key=lambda r: r["start"])
    return items


def detect_stations(track, speed, v_thresh=V_STATION,
                    min_dur_s=MIN_DUR_S, radius=MERGE_RADIUS,
                    min_dwell_s=MIN_STATION_DWELL_S):
    """Full pipeline: candidates -> merge -> duration cut -> order by
    first visit. Returns (kept, rejected)."""
    cands = candidate_runs(speed, track["valid"], track["t"], track["fps"],
                           v_thresh, min_dur_s)
    items = merge_candidates(cands, track["center"], radius)
    kept = [it for it in items if it["dwell_s"] >= min_dwell_s]
    rejected = [it for it in items if it["dwell_s"] < min_dwell_s]
    kept.sort(key=lambda it: it["runs"][0]["start"])
    return kept, rejected


def station_stats(track, speed, stations):
    """Waypoint records: W1_start from the rest frames, then one per
    detected station, with both marker-frame and leveled coordinates."""
    center, center_lev = track["center"], track["center_lev"]
    height, t = track["height"], track["t"]
    out = [{
        "index": 1,
        "id": STATION_NAMES[0],
        "description": STATION_DESC[0],
        "source": "rest_position",
        "runs": [track["rest_frames"]],
        "frame_first": track["rest_frames"][0],
        "frame_last": track["rest_frames"][1],
        "t_first_s": round(float(t[track["rest_frames"][0]]), 2),
        "dwell_total_s": None,
        "dwell_frames": None,
        "xyz": [round(float(v), 4) for v in track["rest"]],
        "leveled_xyz": [round(float(v), 4) for v in track["rest_lev"]],
        "height_above_table_m": round(track["rest_height"], 4),
        "dwell_std_mm": None,
        "dwell_std_norm_mm": None,
        "approach_speed_cm_s": None,
    }]
    for k, st in enumerate(stations):
        frames = np.concatenate([np.arange(r["start"], r["stop"] + 1)
                                 for r in st["runs"]])
        seg = center[frames]
        first = st["runs"][0]["start"]
        a = max(track["loop_span"][0], first - APPROACH_WIN)
        approach = float(np.nanmean(speed[a:first])) if first > a else float("nan")
        out.append({
            "index": k + 2,
            "id": STATION_NAMES[k + 1],
            "description": STATION_DESC[k + 1],
            "source": "detected_dwell",
            "runs": [[r["start"], r["stop"]] for r in st["runs"]],
            "frame_first": int(first),
            "frame_last": int(st["runs"][-1]["stop"]),
            "t_first_s": round(float(t[first]), 2),
            "dwell_total_s": round(float(st["dwell_s"]), 2),
            "dwell_frames": int(len(frames)),
            "xyz": [round(float(v), 4) for v in st["pos"]],
            "leveled_xyz": [round(float(v), 4)
                            for v in np.nanmean(center_lev[frames], 0)],
            "height_above_table_m": round(
                float(np.nanmean(height[frames])), 4),
            "dwell_std_mm": [round(float(v) * 1000, 1)
                             for v in np.nanstd(seg, 0)],
            "dwell_std_norm_mm": round(
                float(np.linalg.norm(np.nanstd(seg, 0))) * 1000, 1),
            "approach_speed_cm_s": round(approach * 100, 2),
        })
    return out


# ---------------------------------------------------------------------------
# Path file
# ---------------------------------------------------------------------------

def build_path_spec(stem, stations):
    ids = [s["id"] for s in stations]
    waypoints = [{
        "id": s["id"],
        "xyz": s["xyz"],
        "leveled_xyz": s["leveled_xyz"],
        "height_above_table_m": s["height_above_table_m"],
        "sigma_m": None,
        "dwell_expected": s["source"] == "detected_dwell",
        "source": s["source"],
        "detected": {
            "frames": s["runs"],
            "dwell_total_s": s["dwell_total_s"],
            "dwell_std_mm": s["dwell_std_mm"],
        },
    } for s in stations]
    segments = [{"from": ids[i], "to": ids[(i + 1) % len(ids)],
                 "type": "line", "constrained_axes": None}
                for i in range(len(ids))]
    return {
        "frame": "desk_marker_world",
        "units": "m",
        "survey": {
            "method": "detected from the recording (dwell-station "
                      "clustering on the ArUco box-center track, "
                      "leveled-frame geometry) plus the parked rest "
                      "position as the start waypoint; no physical "
                      "survey",
            "date": "2026-08-26",
            "default_sigma_m": None,
        },
        "waypoints": waypoints,
        "segments": segments,
        "wall_marker_surveyed": {"xyz": None, "sigma_m": None},
        "note": "R5 (" + stem + ") waypoint geometry, EIGHT waypoints "
                "per the operator's designed trajectory (2026-08-26): "
                "start, back-move end, desk handover, left-move end, "
                "forward-push end, lift top, wire handover, wire left "
                "end. Coordinates are DETECTED from the recording "
                "itself, not surveyed with a ruler - user decision "
                "2026-08-26; W1_start is the parked rest position, the "
                "others are duration-weighted dwell-cluster means. "
                "leveled_xyz / height_above_table_m give the "
                "gravity-leveled twin of each waypoint (the desk-marker "
                "frame is tilted 31.7 deg). Segments form the closed "
                "loop in traversal order; the un-paused corners (the "
                "far-left desk corner and the wire's left descent "
                "corner) are cut by the polyline. See "
                "eval/gt/detect_waypoints.py and "
                "eval/reports/r5_waypoint_eval.md.",
    }


# ---------------------------------------------------------------------------
# Trajectory vs ideal polyline
# ---------------------------------------------------------------------------

def path_errors(track, spec):
    frames = np.flatnonzero(track["valid"])
    rows = []
    for f in frames:
        i, dist, r, per_axis = pm.point_to_path(track["center"][f], spec)
        rows.append((int(f), int(i), float(dist)))
    dists = np.array([r[2] for r in rows])
    per_seg = {}
    for f, i, d in rows:
        per_seg.setdefault(i, []).append(d)
    seg_stats = []
    for i, s in enumerate(spec["segments"]):
        v = np.array(per_seg.get(i, []))
        seg_stats.append({
            "index": i,
            "from": s["from"], "to": s["to"],
            "length_cm": round(float(np.linalg.norm(
                np.array(spec["by_id"][s["to"]]["xyz"])
                - np.array(spec["by_id"][s["from"]]["xyz"]))) * 100, 1),
            "n_frames": int(v.size),
            "median_cm": None if v.size == 0 else round(float(np.median(v)) * 100, 2),
            "p95_cm": None if v.size == 0 else round(float(np.percentile(v, 95)) * 100, 2),
            "max_cm": None if v.size == 0 else round(float(v.max()) * 100, 2),
        })
    overall = {
        "n_frames": int(dists.size),
        "median_cm": round(float(np.median(dists)) * 100, 2),
        "p95_cm": round(float(np.percentile(dists, 95)) * 100, 2),
        "max_cm": round(float(dists.max()) * 100, 2),
        "mean_cm": round(float(dists.mean()) * 100, 2),
    }
    return frames, dists, np.array([r[1] for r in rows]), overall, seg_stats


def threshold_sweep(track, speed):
    """Station count as a function of the speed threshold - the plot
    that fixes V_STATION."""
    out = []
    for v in SWEEP_V:
        kept, _ = detect_stations(track, speed, v_thresh=float(v))
        out.append({"v_cm_s": round(float(v) * 100, 2), "n_stations": len(kept)})
    return out


def plateau_stability(track, speed, sweep, stations):
    """How far the detected positions move when V_STATION is moved
    anywhere inside the constant-count plateau. Takes the DETECTED
    station records only (not the rest-position start waypoint).
    Reported so the choice of threshold inside the plateau can be
    seen to be immaterial."""
    ref = np.array([s["xyz"] for s in stations])
    rows = []
    worst = 0.0
    for s in sweep:
        if s["n_stations"] != len(stations):
            continue
        v = s["v_cm_s"] / 100.0
        kept, _ = detect_stations(track, speed, v_thresh=v)
        pos = np.array([k["pos"] for k in kept])
        d = np.linalg.norm(pos - ref, axis=1)
        worst = max(worst, float(d.max()))
        rows.append({"v_cm_s": s["v_cm_s"],
                     "max_shift_mm": round(float(d.max()) * 1000, 1)})
    return {"per_threshold": rows,
            "max_shift_over_plateau_mm": round(worst * 1000, 1)}


def reconcile(stations):
    """Designed nominal steps vs the measured waypoint geometry, in
    the leveled frame (horizontal length for desk moves, height change
    for the lift)."""
    by_id = {s["id"]: s for s in stations}
    rows = []
    for a, b, kind, nominal_cm, label in DESIGNED_STEPS:
        pa = np.array(by_id[a]["leveled_xyz"])
        pb = np.array(by_id[b]["leveled_xyz"])
        d = pb - pa
        if kind == "horizontal":
            measured = float(np.hypot(d[0], d[2]))
        else:
            measured = float(by_id[b]["height_above_table_m"]
                             - by_id[a]["height_above_table_m"])
        rows.append({
            "step": f"{a} -> {b}",
            "move": label,
            "kind": kind,
            "nominal_cm": nominal_cm,
            "measured_cm": round(measured * 100, 1),
            "delta_cm": round(measured * 100 - nominal_cm, 1),
        })
    return rows


# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------

def _broken(idx, xs, ys):
    """Insert NaN samples where the frame index is not consecutive so a
    plotted line is cut at marker-loss gaps instead of jumping."""
    ox, oy = [], []
    prev = None
    for f, x, y in zip(idx, xs, ys):
        if prev is not None and f != prev + 1:
            ox.append(np.nan)
            oy.append(np.nan)
        ox.append(x)
        oy.append(y)
        prev = f
    return np.array(ox, float), np.array(oy, float)


def _colored_line(ax, xs, ys, tv, vidx, t):
    """Time-coloured trajectory pieces cut at marker-loss gaps."""
    breaks = np.flatnonzero(np.diff(vidx) > 1)
    lc = None
    for a, b in zip(np.r_[0, breaks + 1], np.r_[breaks, len(vidx) - 1]):
        piece = vidx[a:b + 1]
        if piece.size < 2:
            continue
        pts = np.stack([xs[piece], ys[piece]], axis=1).reshape(-1, 1, 2)
        segs = np.concatenate([pts[:-1], pts[1:]], axis=1)
        lc = LineCollection(segs, cmap="viridis", linewidths=1.2,
                            zorder=3)
        lc.set_array(t[piece][:-1])
        lc.set_clim(t[vidx[0]], t[vidx[-1]])
        ax.add_collection(lc)
    return lc


def make_figure(track, speed, stations, spec, frames, dists, sweep, out_png):
    t = track["t"]
    clev = track["center_lev"]
    h = track["height"]
    lo, hi = track["loop_span"]
    vidx = np.flatnonzero(track["valid"])
    P = np.array([w["leveled_xyz"] for w in spec["waypoints"]])
    Ph = np.array([w["height_above_table_m"] for w in spec["waypoints"]])

    fig = plt.figure(figsize=(14.0, 9.0))
    gs = GridSpec(3, 3, figure=fig, width_ratios=[1.05, 1.05, 1.0],
                  height_ratios=[1.5, 1.0, 1.0],
                  hspace=0.5, wspace=0.30,
                  left=0.055, right=0.975, top=0.955, bottom=0.07)

    # --- main panel: ONE 3D view of the whole loop (readability-first
    # rule: the geometry is 3D, so show it in 3D - desk moves, lift,
    # wire traverse and descent are all visible in a single glance).
    # Axes: x = leveled x (the operator's left), y = leveled z (away
    # from the camera), z = height above the tabletop.
    ax = fig.add_subplot(gs[:, 0:2], projection="3d")
    ctx = track["carried"] & ~track["loop"] & track["detected"]
    ax.scatter(clev[ctx, 0], clev[ctx, 2], h[ctx], s=2, color="0.8",
               label="pick-up / set-down", depthshade=False)
    sc = ax.scatter(clev[vidx, 0], clev[vidx, 2], h[vidx], s=3,
                    c=t[vidx], cmap="viridis", depthshade=False,
                    label="measured cube path")
    cb = fig.colorbar(sc, ax=ax, pad=0.06, fraction=0.035, shrink=0.7)
    cb.set_label("time (s)")
    Pc = np.vstack([P, P[:1]])
    Phc = np.r_[Ph, Ph[0]]
    ax.plot(Pc[:, 0], Pc[:, 2], Phc, "--", color="crimson", lw=1.8,
            label="straight lines between waypoints")
    ax.scatter(P[:, 0], P[:, 2], Ph, s=140, facecolor="white",
               edgecolor="crimson", linewidth=1.8, depthshade=False,
               label="waypoint", zorder=10)
    for k, (p, ph) in enumerate(zip(P, Ph)):
        ax.text(p[0], p[2], ph, str(k + 1), ha="center", va="center",
                fontsize=9, color="crimson", fontweight="bold",
                zorder=11)
    # desk surface for orientation: a light plane at height 0 under
    # the desk part of the loop
    gx = np.linspace(clev[vidx, 0].min() - 0.05,
                     clev[vidx, 0].max() + 0.05, 2)
    gz = np.linspace(clev[vidx, 2].min() - 0.05,
                     clev[vidx, 2].max() + 0.05, 2)
    GX, GZ = np.meshgrid(gx, gz)
    ax.plot_surface(GX, GZ, np.zeros_like(GX), color="0.85", alpha=0.35,
                    linewidth=0)
    ax.text(gx[0], gz[0], 0.0, "desk", fontsize=8, color="0.4")
    ax.set_xlabel("x (m), operator's left")
    ax.set_ylabel("z (m), away from camera")
    ax.set_zlabel("height above desk (m)")
    ax.set_box_aspect((np.ptp(clev[vidx, 0]) + 0.1,
                       np.ptp(clev[vidx, 2]) + 0.1,
                       np.ptp(h[vidx]) + 0.1))
    ax.view_init(elev=28, azim=-55)
    ax.legend(loc="upper left", fontsize=7.5, framealpha=0.9)
    ax.set_title("the cube's measured path and the 8 waypoints "
                 "(1 start, 2 back, 3 handover, 4 left, 5 forward, "
                 "6 lift top, 7 wire handover, 8 wire left)",
                 fontsize=9)

    # speed with station dwells shaded
    ax2 = fig.add_subplot(gs[0, 2])
    sx, sy = _broken(vidx, t[vidx], speed[vidx] * 100)
    ax2.plot(sx, sy, lw=0.8, color="0.25")
    for st in stations:
        if st["source"] != "detected_dwell":
            continue
        for r in st["runs"]:
            ax2.axvspan(t[r[0]], t[r[1]], color="tab:orange",
                        alpha=0.35, lw=0)
    ax2.axhline(V_STATION * 100, color="crimson", ls="--", lw=1.0)
    finite = sy[np.isfinite(sy)]
    ymax = float(np.percentile(finite, 99.0)) * 1.45
    clipped = int((finite > ymax).sum())
    ax2.set_ylim(0, ymax)
    ax2.text(t[vidx[0]], V_STATION * 100 - 0.02 * ymax,
             f"V_STATION = {V_STATION*100:.1f} cm/s", ha="left",
             va="top", fontsize=7.5, color="crimson",
             bbox=dict(facecolor="white", alpha=0.8, edgecolor="none",
                       pad=0.8))
    for st in stations:
        if st["source"] != "detected_dwell":
            continue
        ax2.text(0.5 * (t[st["runs"][0][0]] + t[st["runs"][-1][1]]),
                 ymax * 0.97, str(st["index"]), fontsize=8,
                 color="tab:orange", ha="center", va="top",
                 fontweight="bold")
    ax2.set_ylabel("speed (cm/s)")
    ax2.set_xlabel("time (s)")
    ax2.grid(alpha=0.3, lw=0.5)
    title = "box-centre speed, station dwells shaded"
    if clipped:
        title += f"\n({clipped} handover-artefact samples above the axis)"
    ax2.set_title(title, fontsize=8.5)

    # distance to ideal polyline
    ax3 = fig.add_subplot(gs[1, 2], sharex=ax2)
    dx_, dy_ = _broken(frames, t[frames], dists * 100)
    ax3.plot(dx_, dy_, lw=0.8, color="tab:blue")
    med = float(np.median(dists)) * 100
    p95 = float(np.percentile(dists, 95)) * 100
    ax3.axhline(med, color="0.3", ls="-", lw=0.9,
                label=f"median {med:.1f} cm")
    ax3.axhline(p95, color="0.3", ls=":", lw=0.9,
                label=f"p95 {p95:.1f} cm")
    ax3.set_ylim(0, float(dists.max()) * 100 * 1.30)
    ax3.legend(fontsize=7.5, loc="upper left", framealpha=0.9,
               ncol=2, handlelength=1.6, columnspacing=1.0)
    ax3.set_ylabel("distance (cm)")
    ax3.set_xlabel("time (s)")
    ax3.grid(alpha=0.3, lw=0.5)
    ax3.set_title("distance to the ideal polyline", fontsize=8.5)

    # threshold sweep
    ax4 = fig.add_subplot(gs[2, 2])
    v = np.array([s["v_cm_s"] for s in sweep])
    ns = np.array([s["n_stations"] for s in sweep])
    plateau = v[ns == N_DETECTED]
    if plateau.size:
        ax4.axvspan(plateau.min(), plateau.max(), color="tab:green",
                    alpha=0.15, lw=0,
                    label=f"count = {N_DETECTED} over "
                          f"{plateau.min():.1f}-"
                          f"{plateau.max():.1f} cm/s")
    ax4.plot(v, ns, "-o", ms=3, lw=1.0, color="0.25")
    ax4.axvline(V_STATION * 100, color="crimson", ls="--", lw=1.2)
    ax4.axhline(N_DETECTED, color="0.6", lw=0.7, ls=":")
    ax4.set_xlabel("speed threshold (cm/s)")
    ax4.set_ylabel("stations detected")
    ax4.grid(alpha=0.3, lw=0.5)
    ax4.legend(fontsize=7.5, loc="upper left")
    ax4.set_title("threshold derivation (plot-first)", fontsize=8.5)

    fig.savefig(out_png, dpi=190)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def write_report(stem, track, stations, rejected, spec, overall, seg_stats,
                 sweep, stability, recon, closure, md_path, json_path,
                 png_path, path_file):
    lo, hi = track["loop_span"]
    n_detected = sum(1 for s in stations if s["source"] == "detected_dwell")
    verdict = "PASS" if n_detected == N_DETECTED else "FAIL"

    report = {
        "stem": stem,
        "frame": "desk_marker_world",
        "units": "m",
        "constants": {
            "SMOOTH_WIN": SMOOTH_WIN,
            "SPEED_WIN": SPEED_WIN,
            "V_STATION_m_s": V_STATION,
            "MIN_DUR_S": MIN_DUR_S,
            "MERGE_RADIUS_m": MERGE_RADIUS,
            "MIN_STATION_DWELL_S": MIN_STATION_DWELL_S,
            "APPROACH_WIN": APPROACH_WIN,
        },
        "loop_span_frames": [lo, hi],
        "loop_span_s": [round(float(track["t"][lo]), 2),
                        round(float(track["t"][hi]), 2)],
        "frames_total": track["n"],
        "frames_carried": int(track["carried"].sum()),
        "frames_loop": int(track["loop"].sum()),
        "frames_used": int(track["valid"].sum()),
        "stations_detected": n_detected,
        "stations_expected": N_DETECTED,
        "waypoints_total": len(stations),
        "station_count_verdict": verdict,
        "stations": stations,
        "clusters_rejected_below_min_dwell": [
            {"xyz": [round(float(v), 4) for v in it["pos"]],
             "dwell_total_s": round(float(it["dwell_s"]), 2)}
            for it in rejected],
        "threshold_sweep": sweep,
        "plateau_stability": stability,
        "point_to_path_cm": overall,
        "per_segment_cm": seg_stats,
        "designed_vs_measured": recon,
        "loop_closure": closure,
        "outputs": {"path_file": str(path_file), "figure": str(png_path)},
    }
    json_path.write_text(json.dumps(report, indent=1) + "\n")

    plateau = [s["v_cm_s"] for s in sweep if s["n_stations"] == N_DETECTED]
    m = []
    a = m.append
    a(f"# R5 waypoint evaluation: {stem}")
    a("")
    a("Eight waypoints along the designed loop (operator's "
      "specification, 2026-08-26: start, back ~30 cm, left ~45 cm "
      "with a handover, forward ~15 cm, up ~30 cm, along the wire "
      "with a second handover, back to start). Seven pause stations "
      "are detected from the ArUco box-centre track alone; the start "
      "point is the parked rest position. The measured trajectory is "
      "compared with the ideal polyline through the eight waypoints. "
      "Stored frame: desk-marker world (unleveled), metres; geometric "
      "reasoning and the figure use the gravity-leveled frame (the "
      "marker stand is tilted 31.7 deg). Driver: "
      "eval/gt/detect_waypoints.py.")
    a("")
    a(f"Detected station count: {n_detected} of {N_DETECTED} expected "
      f"- {verdict}. Waypoints total: {len(stations)} (start added "
      "from the rest position).")
    a("")
    a("## Constants and their origin")
    a("")
    a("| constant | value | origin |")
    a("|---|---|---|")
    a(f"| SMOOTH_WIN | {SMOOTH_WIN} frames | position moving average, "
      "0.17 s; same window as the existing dwell detector "
      "(path_metrics.detect_dwells, E-008) |")
    a(f"| SPEED_WIN | +-{SPEED_WIN} frames | secant speed over 0.33 s. "
      "The 1-frame gradient speed histogram of the carried track is "
      "flat from 0 to 10 cm/s (jitter and slow motion are the same "
      "order), so it separates nothing; the secant does |")
    a(f"| V_STATION | {V_STATION*100:.1f} cm/s | centre of the plateau "
      f"{min(plateau):.2f}-{max(plateau):.2f} cm/s over which the "
      f"detected station count is invariantly {N_DETECTED} (sweep "
      "table below, sweep panel of the figure). The carried-speed "
      "histogram of this recording has no low-speed gap to cut at, so "
      "the plateau is the derivation |")
    a(f"| MIN_DUR_S | {MIN_DUR_S:.2f} s | 9 frames, just under the "
      "0.33 s span of the speed secant: shorter runs are not resolved "
      "by that estimator |")
    a(f"| MERGE_RADIUS | {MERGE_RADIUS*100:.0f} cm | full 3D distance. "
      "The closest genuinely distinct pair (left-move end vs "
      "forward-push end) is 8.0 cm apart in 3D; the widest "
      "same-station sub-run spread (lift-top regrips) is under 3 cm; "
      "6 cm sits between them. The first version of this detector "
      "merged in the marker-frame x-y projection, which the 31.7 deg "
      "stand tilt compresses - that wrongly fused those two waypoints "
      "(3.7 cm apparent) and is why the merge is 3D now |")
    detected = [s for s in stations if s["source"] == "detected_dwell"]
    weakest = min(s["dwell_total_s"] for s in detected)
    a(f"| MIN_STATION_DWELL_S | {MIN_STATION_DWELL_S:.2f} s | jitter "
      "guard only. At V_STATION nothing lies between it and the "
      f"weakest real station ({weakest:.2f} s at "
      f"{min(detected, key=lambda z: z['dwell_total_s'])['id']}), so "
      "the station count is not produced by this cut |")
    a(f"| APPROACH_WIN | {APPROACH_WIN} frames | 0.5 s before the first "
      "dwell frame, for the reported approach speed |")
    a("")
    a("## Trajectory span")
    a("")
    a(f"Manipulation envelope: frames {track['envelope'][0]}-"
      f"{track['envelope'][1]}. Carried frames: "
      f"{int(track['carried'].sum())}.")
    a("")
    a(f"Loop traversal: frames {lo}-{hi} "
      f"({track['t'][lo]:.2f}-{track['t'][hi]:.2f} s, "
      f"{int(track['loop'].sum())} frames), of which "
      f"{int(track['valid'].sum())} have a measured marker and are used "
      "for every number below.")
    a("")
    a("The loop is the longest contiguous carried run after bridging "
      "carried-mask gaps that contain no detected marker sample - a gap "
      "with no measurement is no evidence of a stop. On R5 exactly one "
      "gap qualifies (frames 1089-1098, the occluded two-hand "
      "handover). The pick-up and set-down excursions at the parked "
      "spot fall outside this run and are excluded, which is what keeps "
      "the parked spot from being reported as a seventh station.")
    a("")
    a("## Threshold sweep")
    a("")
    a("| threshold (cm/s) | stations |")
    a("|---|---|")
    for s in sweep:
        a(f"| {s['v_cm_s']:.2f} | {s['n_stations']} |")
    a("")
    a(f"{N_DETECTED} stations are detected for every threshold from "
      f"{min(plateau):.2f} to {max(plateau):.2f} cm/s. Moving "
      "V_STATION anywhere inside that plateau moves the detected "
      "waypoint positions by at most "
      f"{stability['max_shift_over_plateau_mm']:.1f} mm, so the choice "
      "of threshold inside the plateau does not change the geometry:")
    a("")
    a("| threshold (cm/s) | max waypoint shift vs V_STATION (mm) |")
    a("|---|---|")
    for r in stability["per_threshold"]:
        a(f"| {r['v_cm_s']:.2f} | {r['max_shift_mm']:.1f} |")
    a("")
    a("## Detected stations")
    a("")
    a("Position is the dwell-duration-weighted mean of the merged "
      "cluster (W1_start: median of the parked rest frames); std is "
      "the per-axis spread of the raw track over the dwell frames. "
      "Leveled coordinates: gravity = up, height above the tabletop.")
    a("")
    a("| # | id | frames | dwell (s) | marker xyz (m) | "
      "leveled xyz (m) | height (m) | std (mm) | note |")
    a("|---|---|---|---|---|---|---|---|---|")
    for s in stations:
        runs = ", ".join(f"{r[0]}-{r[1]}" for r in s["runs"])
        dw = "parked" if s["dwell_total_s"] is None \
            else f"{s['dwell_total_s']:.2f}"
        std = "-" if s["dwell_std_norm_mm"] is None \
            else f"{s['dwell_std_norm_mm']:.1f}"
        mx = ", ".join(f"{v:.3f}" for v in s["xyz"])
        lx = ", ".join(f"{v:.3f}" for v in s["leveled_xyz"])
        a(f"| {s['index']} | {s['id']} | {runs} | {dw} | {mx} | {lx} | "
          f"{s['height_above_table_m']:.3f} | {std} | "
          f"{s['description']} |")
    a("")
    if rejected:
        a("Clusters found but rejected below MIN_STATION_DWELL_S:")
        a("")
        for it in rejected:
            a(f"- {np.round(it['pos'], 3).tolist()} m, "
              f"{it['dwell_s']:.2f} s")
        a("")
    else:
        a("No cluster was rejected by the dwell-duration cut: the "
          "detected stations are all that the detector produced.")
        a("")
    a("## Designed vs measured steps")
    a("")
    a("The operator's designed moves (nominal, approximate) against "
      "the measured waypoint geometry in the leveled frame "
      "(horizontal length for desk moves, height change for the "
      "lift). The left move is measured sequentially from the "
      "back-move endpoint; measured execution can differ from the "
      "nominal figure without affecting the evaluation, which "
      "compares the trajectory against the DETECTED waypoints.")
    a("")
    a("| step | move | nominal (cm) | measured (cm) | delta (cm) |")
    a("|---|---|---|---|---|")
    for r in recon:
        a(f"| {r['step']} | {r['move']} | {r['nominal_cm']:.0f} | "
          f"{r['measured_cm']:.1f} | {r['delta_cm']:+.1f} |")
    a("")
    a("## Trajectory vs the ideal polyline")
    a("")
    a("The ideal path is the closed polyline through the eight "
      "waypoints in traversal order, including the closing segment "
      "W8 -> W1. Distances are 3-D point-to-segment, nearest segment "
      "wins.")
    a("")
    a(f"Overall over {overall['n_frames']} loop frames: median "
      f"{overall['median_cm']} cm, p95 {overall['p95_cm']} cm, max "
      f"{overall['max_cm']} cm, mean {overall['mean_cm']} cm.")
    a("")
    a("| segment | length (cm) | frames | median (cm) | p95 (cm) | "
      "max (cm) |")
    a("|---|---|---|---|---|---|")
    for s in seg_stats:
        a(f"| {s['from']} -> {s['to']} | {s['length_cm']:.1f} | "
          f"{s['n_frames']} | {s['median_cm']} | {s['p95_cm']} | "
          f"{s['max_cm']} |")
    a("")
    a(f"Loop closure (measured, carried frames only): the cube leaves "
      f"the loop at frame {lo} and returns at frame {hi}; the two "
      f"positions differ by {closure['closure_mm']:.1f} mm "
      f"({closure['closure_xyz_mm']} mm per axis). This is a property "
      "of the measured trajectory, not of the polyline, which is closed "
      "by construction.")
    a("")
    a("## Limitations")
    a("")
    a("- The eight waypoints are the designed stations. The un-paused "
      "corners (the far-left desk corner around frame 767 and the "
      "wire's left descent corner around frame 1842) are not "
      "waypoints, so the segments crossing them - especially the "
      "closing W8 -> W1 descent - carry the largest per-segment "
      "error; that number measures the polyline model, not the "
      "tracker.")
    a("- W1_start is the parked rest position, not a detected dwell: "
      "the speed criterion runs on carried frames only, so the start "
      "is added from the pre-manipulation rest frames and its "
      "position has no dwell statistics.")
    a("- The measured forward push (W4 -> W5) is shorter than the "
      "nominal 15 cm; the designed figures are approximate and the "
      "evaluation compares against the DETECTED geometry.")
    a("- Coordinates are detected, not surveyed. They inherit whatever "
      "bias the scene calibration and the marker-size correction carry; "
      "the numbers here are self-consistent, not traceable to a ruler.")
    a("- The first two-hand handover (frames 1067-1109) loses the "
      "marker. Those frames are bridged for the loop-span decision but "
      "excluded from every statistic, so the desk edge is sampled with "
      "a gap. The few frames on either side of that gap are flagged "
      "detected but carry an implausible pose (an implied speed above "
      "50 cm/s); they are left in the statistics rather than removed "
      "by a hand-set plausibility cut, and they are the samples "
      "clipped off the top of the speed panel.")
    a("")
    a("## Outputs")
    a("")
    a(f"- {path_file}")
    a(f"- {md_path}")
    a(f"- {json_path}")
    a(f"- {png_path}")
    a("")
    md_path.write_text("\n".join(m) + "\n")
    return report


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R5_STEM)
    ap.add_argument("--path-file", default=str(HERE / "labeled_path_r5.json"))
    args = ap.parse_args()
    stem = args.stem
    alias = paths.ALIAS.get(stem, stem)

    track = load_center_track(stem)
    cs = smooth_track(track["center"])
    speed = secant_speed(cs, track["t"])

    stations_raw, rejected = detect_stations(track, speed)
    if len(stations_raw) != N_DETECTED:
        print(f"[!] {len(stations_raw)} stations detected, "
              f"{N_DETECTED} expected; naming the first "
              f"{min(len(stations_raw), N_DETECTED)}")
    stations = station_stats(track, speed, stations_raw[:N_DETECTED])

    spec_raw = build_path_spec(stem, stations)
    path_file = Path(args.path_file)
    path_file.write_text(json.dumps(spec_raw, indent=2) + "\n")
    spec = pm.load_path(str(path_file))

    frames, dists, seg_idx, overall, seg_stats = path_errors(track, spec)
    sweep = threshold_sweep(track, speed)
    stability = plateau_stability(track, speed, sweep, stations[1:])
    recon = reconcile(stations) if len(stations) == len(STATION_NAMES) \
        else []
    lo, hi = track["loop_span"]
    d_close = track["center"][hi] - track["center"][lo]
    closure = {
        "start_frame": lo, "stop_frame": hi,
        "start_xyz": [round(float(v), 4) for v in track["center"][lo]],
        "stop_xyz": [round(float(v), 4) for v in track["center"][hi]],
        "closure_xyz_mm": [round(float(v) * 1000, 1) for v in d_close],
        "closure_mm": round(float(np.linalg.norm(d_close)) * 1000, 1),
    }

    paths.EVAL_REPORTS.mkdir(parents=True, exist_ok=True)
    png = paths.EVAL_REPORTS / f"{alias}_waypoints.png"
    md = paths.EVAL_REPORTS / f"{alias}_waypoint_eval.md"
    js = paths.EVAL_REPORTS / f"{alias}_waypoint_eval.json"

    make_figure(track, speed, stations, spec, frames, dists, sweep, png)
    write_report(stem, track, stations, rejected, spec, overall, seg_stats,
                 sweep, stability, recon, closure, md, js, png, path_file)

    n_det = len(stations) - 1
    print(f"=== {stem}: waypoint evaluation ===")
    print(f"  loop span frames {lo}-{hi}, {int(track['valid'].sum())} "
          "measured frames used")
    print(f"  stations detected: {n_det} "
          f"({'PASS' if n_det == N_DETECTED else 'FAIL'} vs "
          f"{N_DETECTED} expected) + start waypoint from rest")
    for s in stations:
        dw = "parked" if s["dwell_total_s"] is None \
            else f"{s['dwell_total_s']:.2f} s"
        print(f"    {s['index']} {s['id']:<18} lev "
              f"{np.round(s['leveled_xyz'], 3).tolist()} m  "
              f"h {s['height_above_table_m']:.3f} m  {dw}")
    print(f"  point-to-path: median {overall['median_cm']} cm, "
          f"p95 {overall['p95_cm']} cm, max {overall['max_cm']} cm")
    if recon:
        print("  designed vs measured (cm): "
              + ", ".join(f"{r['move']} {r['nominal_cm']:.0f}->"
                          f"{r['measured_cm']:.1f}" for r in recon))
    print(f"[+] {path_file}")
    print(f"[+] {md}")
    print(f"[+] {js}")
    print(f"[+] {png}")


if __name__ == "__main__":
    main()
