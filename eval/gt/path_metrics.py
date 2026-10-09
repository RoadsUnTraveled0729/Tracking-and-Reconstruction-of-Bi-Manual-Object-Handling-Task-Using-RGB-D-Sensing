"""Pure geometry for the labeled-path evaluation (stage 1).

point_to_segment / point_to_path: distance from a measured box-center
position to the surveyed path. detect_dwells: automatic dwell
detection on the box-center track (sustained low speed), never
hand-picked frames. load_path: schema validation for
labeled_path.json.

Unit tests: eval/gt/test_path_metrics.py.
"""

import json

import numpy as np


def load_path(path_file):
    """Validate and return the path description. Raises ValueError on
    structural problems; missing coordinates are allowed (pending
    survey) and flagged via the 'complete' key."""
    spec = json.load(open(path_file))
    if spec.get("frame") != "desk_marker_world" or spec.get("units") != "m":
        raise ValueError("path file must declare desk_marker_world / m")
    ids = [w["id"] for w in spec["waypoints"]]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate waypoint ids")
    by_id = {w["id"]: w for w in spec["waypoints"]}
    for s in spec["segments"]:
        if s["from"] not in by_id or s["to"] not in by_id:
            raise ValueError(f"segment references unknown waypoint: {s}")
        if s.get("type", "line") != "line":
            raise ValueError(f"unsupported segment type: {s['type']}")
        ca = s.get("constrained_axes")
        if ca is not None and not set(ca) <= {"x", "y", "z"}:
            raise ValueError(f"bad constrained_axes: {ca}")
    complete = all(
        w.get("xyz") is not None and np.all(np.isfinite(w["xyz"]))
        for w in spec["waypoints"])
    spec["complete"] = complete
    spec["by_id"] = by_id
    return spec


def point_to_segment(p, a, b):
    """Distance from point p to segment [a, b] (clamped projection).

    Returns (distance, t, residual) with t in [0, 1] the projection
    parameter and residual = p - closest_point (world axes)."""
    p, a, b = (np.asarray(v, float) for v in (p, a, b))
    ab = b - a
    denom = float(np.dot(ab, ab))
    t = 0.0 if denom == 0 else float(np.clip(np.dot(p - a, ab) / denom, 0.0, 1.0))
    q = a + t * ab
    r = p - q
    return float(np.linalg.norm(r)), t, r


def point_to_path(p, spec):
    """Nearest segment of the path. Returns (segment_index, distance,
    residual_vec, per_axis) where per_axis maps axis name -> residual
    component for the segment's constrained axes only (None when the
    segment declares no constraint set)."""
    best = None
    for i, s in enumerate(spec["segments"]):
        a = spec["by_id"][s["from"]]["xyz"]
        b = spec["by_id"][s["to"]]["xyz"]
        dist, t, r = point_to_segment(p, a, b)
        if best is None or dist < best[1]:
            best = (i, dist, r, s)
    i, dist, r, s = best
    ca = s.get("constrained_axes")
    per_axis = None
    if ca is not None:
        per_axis = {ax: float(r["xyz".index(ax)]) for ax in ca}
    return i, dist, r, per_axis


def detect_dwells(t, xyz, v_thresh=0.02, min_dur_s=0.5, smooth_win=5,
                  valid=None):
    """Dwell events: sustained runs where the smoothed speed of the
    (filtered) box-center track stays below v_thresh (m/s).

    valid: optional bool mask restricting which frames may dwell
    (e.g. the carried mask, so resting at the parked spot does not
    count). Returns a list of dicts."""
    t = np.asarray(t, float)
    xyz = np.asarray(xyz, float)
    n = len(t)
    v = np.full(n, np.nan)
    dt = np.gradient(t)
    g = np.gradient(xyz, axis=0) / dt[:, None]
    v[:] = np.linalg.norm(g, axis=1)
    if smooth_win > 1:
        k = np.ones(smooth_win) / smooth_win
        vpad = np.convolve(v, k, mode="same")
        v = vpad
    slow = v < v_thresh
    if valid is not None:
        slow &= np.asarray(valid, bool)
    events = []
    idx = np.flatnonzero(slow)
    if idx.size == 0:
        return events
    brk = np.flatnonzero(np.diff(idx) > 1)
    starts = np.r_[idx[0], idx[brk + 1]]
    stops = np.r_[idx[brk], idx[-1]]
    fps = 1.0 / np.median(dt)
    for a, b in zip(starts, stops):
        if (b - a + 1) / fps < min_dur_s:
            continue
        seg = xyz[a:b + 1]
        events.append({
            "start": int(a), "stop": int(b),
            "frames": int(b - a + 1),
            "duration_s": round(float(t[b] - t[a]), 2),
            "mean_xyz": [round(float(v_), 4) for v_ in np.nanmean(seg, 0)],
            "std_xyz_mm": [round(float(v_) * 1000, 1)
                           for v_ in np.nanstd(seg, 0)],
        })
    return events


def match_dwells_to_waypoints(dwells, spec, radius=0.08):
    """Nearest-waypoint assignment within radius (m). Returns list of
    (dwell_index, waypoint_id or None, distance or None)."""
    out = []
    for i, d in enumerate(dwells):
        p = np.array(d["mean_xyz"])
        best_id, best_dist = None, None
        for w in spec["waypoints"]:
            if w.get("xyz") is None:
                continue
            dist = float(np.linalg.norm(p - np.array(w["xyz"])))
            if best_dist is None or dist < best_dist:
                best_id, best_dist = w["id"], dist
        if best_dist is not None and best_dist > radius:
            best_id, best_dist = None, best_dist
        out.append((i, best_id, best_dist))
    return out
