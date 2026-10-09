"""Holding classification and grip episodes for the wrist-to-object
bench (D-036). Reimplemented from the thesis code (eval/ is read-only
for V3, D-007):

- moving_mask, rest_referenced_carried, forearm_ok, holding_mask:
  eval/offset/carry.py (functions of the same names; the carry
  classifier itself is copied there from
  v1/integration/analyze_object_offset.py lines 165-170, 185-198).
- grip_episodes: eval/failure/grip_state.py grip_episodes (causal
  enter/stay/exit state machine).
- hold_runs: eval/offset/analyze_offset_constancy.py main, the
  "per contiguous grip episode" split (gap > 15 frames starts a new
  episode, episodes under 30 frames dropped). THIS is the rule that
  produced the thesis R4 episodes (eval/reports/r4_stage4_ground_truth
  .md: right 254-388, 478-713, 1028-1112; left 674-832), not
  grip_episodes; tests/test_holding.py reproduces them.

forearm_ok takes elbow and wrist arrays instead of carry.py's
DataFrame, so it runs on either the thesis or the V3 CSV.
"""
import numpy as np

# Constants and their sources (D-036)
CONFIG = {
    "hold_radius_m": 0.25,      # carry.py HOLD_RADIUS (eval E-005/E-006)
    "forearm_tol": 0.30,        # carry.py FOREARM_TOL
    "rest_dist_m": 0.04,        # carry.py REST_DIST
    "move_k_frames": 7,         # carry.py K
    "move_dist_m": 0.03,        # carry.py MOVE_DIST
    "carry_height_m": 0.06,     # carry.py CARRY_HEIGHT
    "enter_frames": 5,          # grip_state.py ENTER_FRAMES
    "exit_frames": 5,           # grip_state.py EXIT_FRAMES
    "release_radius_m": 0.35,   # grip_state.py RELEASE_RADIUS
    "run_gap_frames": 15,       # analyze_offset_constancy.py (gap > 15)
    "run_min_frames": 30,       # analyze_offset_constancy.py (size < 30)
    "cube_m": 0.07,             # scene_geometry.object_cube_size_m
}


def moving_mask(obj, k=CONFIG["move_k_frames"],
                dist=CONFIG["move_dist_m"]):
    """carry.py moving_mask: displacement over k frames > dist,
    centred. NaN displacements (undetected marker) count as not
    moving."""
    n = len(obj)
    disp = np.linalg.norm(obj[k:] - obj[:-k], axis=1)
    moving = np.zeros(n, bool)
    with np.errstate(invalid="ignore"):
        moving[k // 2:k // 2 + len(disp)] = disp > dist
    return moving


def rest_referenced_carried(obj, height_above_table, envelope,
                            rest_dist=CONFIG["rest_dist_m"],
                            height=CONFIG["carry_height_m"]):
    """carry.py rest_referenced_carried: inside the manipulation
    envelope AND (away from both rest positions OR moving OR lifted).
    height_above_table: (N,) marker height above the tabletop."""
    n = len(obj)
    a, b = envelope
    inside = np.zeros(n, bool)
    inside[a:b + 1] = True
    rest_pre = np.nanmedian(obj[:a], axis=0) if a > 0 else None
    rest_post = np.nanmedian(obj[b + 1:], axis=0) if b + 1 < n else None
    away = np.ones(n, bool)
    with np.errstate(invalid="ignore"):
        for rest in (rest_pre, rest_post):
            if rest is not None and np.all(np.isfinite(rest)):
                away &= np.linalg.norm(obj - rest, axis=1) > rest_dist
        lifted = np.asarray(height_above_table) > height
    return inside & (away | moving_mask(obj) | lifted)


def forearm_ok(elbow, wrist, tol=CONFIG["forearm_tol"]):
    """carry.py forearm_ok on arrays: |elbow - wrist| within tol of its
    median over the recording (rejects depth-collapse frames)."""
    L = np.linalg.norm(np.asarray(elbow, float) - np.asarray(wrist, float),
                       axis=1)
    med = np.nanmedian(L)
    with np.errstate(invalid="ignore"):
        return np.abs(L - med) < tol * med


def holding_mask(center, wr, wrist_clean, det, carried, forearm_valid,
                 radius=CONFIG["hold_radius_m"]):
    """carry.py holding_mask with the v1 wrist_flag == 0 test passed
    in as a boolean wrist_clean."""
    mag = np.linalg.norm(wr - center, axis=1)
    with np.errstate(invalid="ignore"):
        near = mag < radius
    return (det & carried & near & np.asarray(wrist_clean, bool)
            & forearm_valid & np.isfinite(wr).all(axis=1))


def grip_episodes(hold_clean, carried, wrist_center_dist, wrist_clean,
                  enter=CONFIG["enter_frames"], exit_=CONFIG["exit_frames"],
                  release=CONFIG["release_radius_m"]):
    """grip_state.py grip_episodes (copied): causal per-hand state.
    Returns (holding bool array, [(start, stop) inclusive])."""
    n = len(hold_clean)
    holding = np.zeros(n, bool)
    episodes = []
    on = False
    enter_ctr = exit_ctr = 0
    start = 0
    for f in range(n):
        if not on:
            enter_ctr = enter_ctr + 1 if hold_clean[f] else 0
            if enter_ctr >= enter:
                on = True
                start = f - enter + 1
                holding[start:f + 1] = True
                exit_ctr = 0
        else:
            released = (not carried[f]) or (
                wrist_clean[f]
                and np.isfinite(wrist_center_dist[f])
                and wrist_center_dist[f] > release)
            exit_ctr = exit_ctr + 1 if released else 0
            if exit_ctr >= exit_:
                on = False
                stop = f - exit_
                episodes.append((start, stop))
                holding[stop + 1:f + 1] = False
                enter_ctr = 0
            else:
                holding[f] = True
    if on:
        episodes.append((start, n - 1))
    return holding, episodes


def hold_runs(hold, gap=CONFIG["run_gap_frames"],
              min_frames=CONFIG["run_min_frames"]):
    """analyze_offset_constancy.py episode split: indices of held
    frames, a gap > `gap` starts a new run, runs with fewer than
    `min_frames` held frames are dropped. Returns [(start, stop, n)]
    with stop inclusive and n = held frames inside."""
    idx = np.flatnonzero(hold)
    if idx.size == 0:
        return []
    brk = np.flatnonzero(np.diff(idx) > gap)
    starts = np.r_[idx[0], idx[brk + 1]]
    stops = np.r_[idx[brk], idx[-1]]
    out = []
    for a, b in zip(starts, stops):
        e = idx[(idx >= a) & (idx <= b)]
        if e.size < min_frames:
            continue
        out.append((int(a), int(b), int(e.size)))
    return out
