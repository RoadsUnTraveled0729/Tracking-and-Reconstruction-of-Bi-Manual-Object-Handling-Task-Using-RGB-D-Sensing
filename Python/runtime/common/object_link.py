#!/usr/bin/env python3
# Filename: runtime/common/object_link.py
"""B -> A object link + online grip tracker (E-014 live wiring).

Gives v2 Pipeline A the per-frame object-derived wrist estimate the
robust solver's obj input consumes (core/kinematics/occlusion_ext.py:
solve(points, obj)). Two pieces:

ObjectPoseReader
    Latest-wins seqlock read of Pipeline B's PSB2 packet, then the
    camera-frame object pose is reconstructed exactly:
      unity -> world: conjugate by the WORLD_TO_UNITY involution and
      recompose the ZXY euler (core/aruco/frames.py, both invertible);
      world -> camera: T_cam_desk from the scene calibration.
    A frame-skew guard treats the object as not-live for recovery when
    B's packet is more than SKEW_MAX frames away from A's frame.

GripTracker
    The causal grip machinery of the offline recovery
    (eval/failure/grip_state.py + eval/failure/recovery_core.py),
    reduced to its online form. One deliberate simplification versus
    offline (PoC scope, logged in the report): the grip offset mu is
    fitted directly in SOLVER SPACE - a rigid grip offset is constant
    in any fixed frame, so the leveled-world detour adds nothing live.
    Internally all geometry runs in the CAMERA frame (solver space is
    its y-flip F, applied at the boundary).

    Per hand, per frame (all causal):
      ENTER  after ENTER_FRAMES consecutive clean-holding frames
             (object live+carried, wrist measured, plausible forearm,
             |W - box center| < HOLD_RADIUS)
      STAY   through wrist failures (rigid-grasp persistence)
      EXIT   after EXIT_FRAMES consecutive frames of a cleanly
             measured wrist beyond RELEASE_RADIUS
      mu     running mean for MU_WARMUP clean frames, then EMA at
             MU_ALPHA; reset at each ENTER; frozen while the wrist is
             unclean (the report's time-local mu)
      D6     while holding, a measured wrist farther than GRIP_MAX
             from the box center is a wrong measurement: the caller
             drops it from the solve input and the object recovery
             takes over. The same frames advance the EXIT counter, so
             a real release confirms after EXIT_FRAMES (the bounded
             causality cost: up to EXIT_FRAMES frames of box-anchored
             wrist during a true release).
      w_hat  = obj + R_obj mu, published only while holding with a
             live marker and |mu| <= MU_MAX.

    "Carried" is the causal reduction of the offline rest-referenced
    test: the rest pose is the median of the first REST_N live object
    samples, carried = farther than REST_DIST from it. It gates ENTER
    only (never EXIT), so waypoint dwells do not churn episodes.

Runtime constants are collected in runtime_parameters.py. The recovery
algorithm and thresholds are preserved from the thesis implementation.
"""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for rel in ("core/aruco", "core/realtime/integration"):
    p = str(ROOT / rel)
    if p not in sys.path:
        sys.path.insert(0, p)

from frames import WORLD_TO_UNITY, make_T, recompose_zxy   # noqa: E402
from realtime_integrate import (PSB2_FMT, PSB2_MAGIC,      # noqa: E402
                                PSB2_SIZE, SeqReader, wait_for)
from runtime_parameters import (ENTER_FRAMES, EXIT_FRAMES,         # noqa: E402
                        MU_ALPHA, MU_WARMUP, RELEASE_RADIUS)
from runtime_parameters import FOREARM_TOL, HOLD_RADIUS, REST_DIST      # noqa: E402

# physical plausibility bounds (eval/failure/recovery_core.py, E-014b)
GRIP_MAX = 0.35          # m, = RELEASE_RADIUS
MU_MAX = 0.30            # m, |mu| beyond this is not a grip

SKEW_MAX = 3             # frames of A/B disagreement tolerated
REST_N = 30              # live samples defining the initial rest pose
F_FLIP = np.array([1.0, -1.0, 1.0])   # solver space <-> camera space

SIDES = ("left", "right")


class ObjectPoseReader:
    def __init__(self, shm_path, calib, timeout_s=30.0):
        wait_for(shm_path, timeout_s, "object")
        self.rd = SeqReader(shm_path, PSB2_FMT, PSB2_SIZE, PSB2_MAGIC)
        self.T_cam_desk = np.asarray(calib["T_cam_desk"], float)
        self.skews = []
        self.skew_dropped = 0

    def read(self, person_frame):
        """-> (p_cam, R_cam) or None (not live / stale / unreadable)."""
        d = self.rd.read()
        if d is None or not d[10]:      # PSB2: ..., pos 4:7, euler 7:10, live 10
            return None
        skew = d[2] - person_frame
        self.skews.append(skew)
        if abs(skew) > SKEW_MAX:
            self.skew_dropped += 1
            return None
        t_u = np.asarray(d[4:7], float)
        R_u = recompose_zxy(np.asarray(d[7:10], float))
        W = WORLD_TO_UNITY
        T = self.T_cam_desk @ make_T(W @ R_u @ W, W @ t_u)
        return T[:3, 3], T[:3, :3]


class _Hand:
    __slots__ = ("on", "enter_ctr", "exit_ctr", "mu", "mu_n",
                 "episodes", "start", "d6_count")

    def __init__(self):
        self.on = False
        self.enter_ctr = 0
        self.exit_ctr = 0
        self.mu = None
        self.mu_n = 0
        self.episodes = []
        self.start = 0
        self.d6_count = 0


class GripTracker:
    def __init__(self, cube_size_m):
        self.center_off = np.array([0.0, -cube_size_m / 2.0, 0.0])
        self.rest_buf = []
        self.rest0 = None
        self.hands = {s: _Hand() for s in SIDES}

    def update(self, frame, points, obj_cam, forearm_len):
        """One causal step.

        frame        A's stream frame index
        points       solver-space landmark dict (pre-solve)
        obj_cam      (p_cam, R_cam) from ObjectPoseReader, or None
        forearm_len  dict side -> calibrated forearm length or None

        Returns (obs, d6): obs = {side: solver-space w_hat or None}
        for solver.solve(obj=...); d6 = set of sides whose measured
        wrist must be dropped from the solve input this frame.
        """
        obs = {s: None for s in SIDES}
        d6 = set()
        live = obj_cam is not None
        if live:
            p_obj, R_obj = obj_cam
            if self.rest0 is None:
                self.rest_buf.append(p_obj)
                if len(self.rest_buf) >= REST_N:
                    self.rest0 = np.median(np.asarray(self.rest_buf), 0)
            carried = (self.rest0 is not None
                       and np.linalg.norm(p_obj - self.rest0) > REST_DIST)
            center = p_obj + R_obj @ self.center_off
        else:
            carried = False
            center = None

        for side in SIDES:
            h = self.hands[side]
            w_sol = points.get(f"{side}_wrist")
            e_sol = points.get(f"{side}_elbow")
            wrist_meas = w_sol is not None and np.all(np.isfinite(w_sol))
            fa_ok = True
            L = forearm_len.get(side)
            if wrist_meas and e_sol is not None and L:
                fl = np.linalg.norm(np.asarray(w_sol) - np.asarray(e_sol))
                fa_ok = abs(fl - L) < FOREARM_TOL * L
            dist = (np.linalg.norm(F_FLIP * np.asarray(w_sol) - center)
                    if (live and wrist_meas) else None)

            if not h.on:
                clean_hold = (live and carried and wrist_meas and fa_ok
                              and dist is not None and dist < HOLD_RADIUS)
                h.enter_ctr = h.enter_ctr + 1 if clean_hold else 0
                if h.enter_ctr >= ENTER_FRAMES:
                    h.on = True
                    h.start = frame
                    h.mu = None
                    h.mu_n = 0
                    h.exit_ctr = 0
            else:
                releasing = (dist is not None and fa_ok
                             and dist > RELEASE_RADIUS)
                h.exit_ctr = h.exit_ctr + 1 if releasing else 0
                if h.exit_ctr >= EXIT_FRAMES:
                    h.on = False
                    h.episodes.append([h.start, frame])
                    h.enter_ctr = 0
                    continue
                if dist is not None and dist > GRIP_MAX:
                    d6.add(side)          # wrong measurement, not release
                    h.d6_count += 1
                elif live and wrist_meas and fa_ok:
                    m = F_FLIP * np.asarray(w_sol) - p_obj
                    m = R_obj.T @ m       # marker-local grip offset
                    if h.mu is None:
                        h.mu = m.copy()
                        h.mu_n = 1
                    elif h.mu_n < MU_WARMUP:
                        h.mu_n += 1
                        h.mu += (m - h.mu) / h.mu_n
                    else:
                        h.mu += MU_ALPHA * (m - h.mu)
                        h.mu_n += 1
                if (live and h.mu is not None and h.mu_n >= MU_WARMUP
                        and np.linalg.norm(h.mu) <= MU_MAX):
                    obs[side] = F_FLIP * (p_obj + R_obj @ h.mu)
        return obs, d6

    def close(self, frame):
        for side in SIDES:
            h = self.hands[side]
            if h.on:
                h.episodes.append([h.start, frame])
                h.on = False

    def summary(self):
        return {side: {"episodes": h.episodes, "d6": h.d6_count}
                for side, h in self.hands.items()}
