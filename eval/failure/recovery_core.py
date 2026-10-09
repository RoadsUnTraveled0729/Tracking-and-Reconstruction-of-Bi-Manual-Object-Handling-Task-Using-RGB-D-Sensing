"""Shared per-frame pipeline for object-conditioned recovery (E-014).

Assembles, for one recording, everything RobustChainSolver needs to
run with the obj input:

  1. filtered landmarks (solver points, unity_from_sensor space)
  2. the failure mask (eval/failure/detect_failures.py output):
     failed arms have their elbow+wrist landmarks REMOVED before the
     solve - the study established those measurements are wrong, and
     the layer treats wrong-as-missing (its own gates catch what the
     offline detectors catch, but the offline mask is the graded
     reference, so the caller applies it explicitly)
  3. grip episodes + per-episode grip offsets (grip_state.py) and the
     per-frame object-derived wrist estimate
     w_hat = obj + R_obj mu  (leveled world), converted to the
     solver's point space (leveled world -> camera -> unity flip)
  4. calibrated segment lengths (the recording's offset-fit report)

Solve variants:
  plain     the robust solve exactly as check_v1_overlay runs it
  masked    + failure-mask landmark removal (recovery source: EMA
            memories only - what the pre-E-014 layer could do)
  recovery  + the obj input (object-conditioned wrist + IK elbow)

The masked/recovery pair isolates the contribution of the object.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "common"))
sys.path.insert(0, str(HERE.parents[0] / "offset"))
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "v1" / "kinematics"))

import paths                                   # noqa: E402
import carry                                   # noqa: E402
import grip_state                              # noqa: E402
from fit_offset import load_tracks             # noqa: E402
from occlusion import (ChainFallbackSolver,    # noqa: E402
                       points_from_row)
from occlusion_ext import RobustChainSolver    # noqa: E402
from root_frame import unity_from_sensor       # noqa: E402

SIDES = ("left", "right")
ARM_LM = {"left": ("left_elbow", "left_wrist"),
          "right": ("right_elbow", "right_wrist")}

# Physical plausibility bounds of a held object (video-independent:
# a hand gripping the cube keeps the wrist near it, whatever the
# recording). D6: a measured wrist farther than GRIP_MAX from the box
# center DURING a grip episode is a wrong measurement, not a release
# (releases are detected by the state machine's clean-exit rule at
# grip_state.RELEASE_RADIUS with hysteresis). MU_MAX bounds the grip
# offset itself: an estimate placing the wrist farther than this from
# the marker origin is discarded rather than used for recovery.
GRIP_MAX = 0.35          # m, matches grip_state.RELEASE_RADIUS
MU_MAX = 0.30            # m, |mu| beyond this is not a grip


def _leveled_to_solver_space(w_lev, world):
    """Invert LeveledWorld.wrist_world, then apply the solver's
    unity_from_sensor flip (same chain as fusion_display.py)."""
    Ginv = world.G.T
    Minv = np.linalg.inv(world.M)
    w_cam = (Minv @ (Ginv @ np.atleast_2d(w_lev).T
                     - world.cam_pos[:, None])).T * [1.0, -1.0, 1.0]
    return np.array([unity_from_sensor(w) for w in w_cam])


def build_inputs(stem, extra_fail=None):
    """Everything needed to run the solve variants on one recording.

    extra_fail: optional dict side -> bool array ORed into the
    detector failure mask (synthetic masking for the E-013 harness);
    masked frames are treated exactly like detected failures - removed
    from the solve input, excluded from grip-offset fitting."""
    calib_path = str(paths.calib_for(stem))
    calib, world, lm_df, obj_lev, R_lev, det, wr, wrist_flag, t = \
        load_tracks(stem, calib_path)
    n = len(obj_lev)

    insp = json.loads(
        (paths.EVAL_REPORTS / f"{stem}_inspection.json").read_text())
    envelope = insp["phases"]["manipulation"]
    carried = carry.rest_referenced_carried(obj_lev, world, envelope)
    center = world.box_center(obj_lev, R_lev)

    # failure mask (detect_failures.py output)
    alias = paths.ALIAS[stem]
    fm_csv = paths.EVAL_OUT / f"recovery_{alias}" / "failure_mask.csv"
    fm = pd.read_csv(fm_csv).iloc[:n]
    fail = {"left": fm["fail_arm_L"].to_numpy().astype(bool),
            "right": fm["fail_arm_R"].to_numpy().astype(bool),
            "torso": fm["fail_torso"].to_numpy().astype(bool)}
    if extra_fail:
        for side, m in extra_fail.items():
            fail[side] = fail[side] | np.asarray(m, bool)[:n]

    # grip episodes + per-episode offsets, per hand
    fit = json.loads((paths.EVAL_REPORTS /
                      f"{stem}_offset_fit.json").read_text())
    seg_len = {k: float(v) for k, v in fit["segment_lengths_m"].items()}
    holding, episodes, ep_fits, w_hat_solver = {}, {}, {}, {}
    d6_count = {}
    for side in SIDES:
        d_loc = np.einsum("nij,ni->nj", R_lev, wr[side] - obj_lev)
        wrist_ok = (wrist_flag[side] == 0) & ~fail[side]
        forearm = carry.forearm_ok(lm_df, side)
        hold_clean = carry.holding_mask(
            center, wr[side], wrist_flag[side], det, carried,
            forearm) & ~fail[side]
        dist = np.linalg.norm(wr[side] - center, axis=1)
        holding[side], episodes[side] = grip_state.grip_episodes(
            hold_clean, carried, dist, wrist_ok)
        # D6 grip-plausibility gate: while this hand HOLDS the object
        # (episode state, which excludes release transitions - the
        # state machine retro-clears the exit frames), a measured
        # wrist farther than GRIP_MAX from the box center is a wrong
        # measurement - you cannot hold an object with the wrist that
        # far away. Flagged like any other failure: the wrist is
        # removed and the object recovery takes over.
        with np.errstate(invalid="ignore"):
            d6 = (holding[side] & carried & det
                  & (wrist_flag[side] == 0) & (dist > GRIP_MAX))
        fail[side] = fail[side] | d6
        d6_count[side] = int(d6.sum())
        # per_hand[side] is None when this hand never held the object
        # in the recording (e.g. a one-handed task)
        mu_glob = (fit["per_hand"].get(side) or {}).get("mu_cm")
        ep_fits[side] = grip_state.fit_episode_mu(
            episodes[side], d_loc, hold_clean,
            None if mu_glob is None
            else np.asarray(mu_glob, float) / 100.0)
        # time-local mu (tracks regrips, frozen through failures);
        # per-episode mean only where the local estimate has not
        # warmed up yet
        mu = grip_state.time_local_mu(d_loc, hold_clean,
                                      episodes[side])
        mu_ep = grip_state.per_frame_mu(n, ep_fits[side])
        gaps = ~np.isfinite(mu).all(axis=1)
        mu[gaps] = mu_ep[gaps]
        w_lev = obj_lev + np.einsum("nij,nj->ni", R_lev, mu)
        w_sol = _leveled_to_solver_space(w_lev, world)
        # estimate is valid only while holding, with a measured
        # marker, and only for a physically plausible grip offset
        with np.errstate(invalid="ignore"):
            mu_ok = np.linalg.norm(mu, axis=1) <= MU_MAX
        valid = (holding[side] & det & mu_ok
                 & np.isfinite(w_sol).all(axis=1))
        w_sol[~valid] = np.nan
        w_hat_solver[side] = w_sol

    return {
        "stem": stem, "n": n, "t": t, "lm_df": lm_df,
        "world": world, "carried": carried, "center": center,
        "det": det, "fail": fail, "holding": holding,
        "episodes": episodes, "episode_fits": ep_fits,
        "d6_count": d6_count,
        "w_hat_solver": w_hat_solver, "seg_len": seg_len,
    }


def solver_points(row, fail_row=None):
    """points_from_row + unity flip; drops failed arms' elbow+wrist."""
    pts = {k: unity_from_sensor(v)
           for k, v in points_from_row(row).items()
           if np.all(np.isfinite(v))}
    if fail_row:
        for side in SIDES:
            if fail_row.get(side):
                for name in ARM_LM[side]:
                    pts.pop(name, None)
    return pts


def run_variant(inputs, variant, seg_len=None, solver_kwargs=None):
    """Run one solve variant over the recording.

    solver_kwargs: optional RobustChainSolver options for a study run
    (compare_hip_hold.py passes hip_hold=True); None keeps the pinned
    configuration every report was produced with.

    Returns dict with angles (n,13), mask (n,), tags (n,7), and the
    solver object (for its intervention counters)."""
    n = inputs["n"]
    lm_df = inputs["lm_df"]
    sl = dict(seg_len or inputs["seg_len"])
    solver = RobustChainSolver(seg_len=sl, **(solver_kwargs or {}))
    angles = np.zeros((n, 13))
    masks = np.zeros(n, int)
    tags = np.zeros((n, 7), int)
    pelvis = np.full((n, 3), np.nan)
    use_mask = variant in ("masked", "recovery")
    use_obj = variant == "recovery"
    for i, (_, row) in enumerate(lm_df.iterrows()):
        fr = ({side: bool(inputs["fail"][side][i]) for side in SIDES}
              if use_mask else None)
        pts = solver_points(row, fr)
        if use_obj:
            obs = {side: (inputs["w_hat_solver"][side][i]
                          if np.isfinite(
                              inputs["w_hat_solver"][side][i]).all()
                          else None)
                   for side in SIDES}
            out = solver.solve(pts, obj=obs)
        else:
            out = solver.solve(pts)
        angles[i], masks[i], tags[i] = out
        # pelvis from the POST-RECOVERY hips (the E-011b ray repair
        # replaces depth-corrupt hips, so this pelvis does not carry
        # their depth wobble; the raw-landmark midpoint does)
        lh = solver.last_points.get("left_hip")
        rh = solver.last_points.get("right_hip")
        if lh is not None and rh is not None \
                and np.all(np.isfinite(lh)) and np.all(np.isfinite(rh)):
            pelvis[i] = 0.5 * (lh + rh)
    return {"angles": angles, "mask": masks, "tags": tags,
            "pelvis": pelvis, "solver": solver}


def run_hold_baseline(inputs):
    """ChainFallbackSolver with failure-mask removal: the plain
    hold-last answer to the failure frames."""
    n = inputs["n"]
    solver = ChainFallbackSolver()
    angles = np.zeros((n, 13))
    masks = np.zeros(n, int)
    for i, (_, row) in enumerate(inputs["lm_df"].iterrows()):
        fr = {side: bool(inputs["fail"][side][i]) for side in SIDES}
        angles[i], masks[i] = solver.solve(solver_points(row, fr))
    return {"angles": angles, "mask": masks}
