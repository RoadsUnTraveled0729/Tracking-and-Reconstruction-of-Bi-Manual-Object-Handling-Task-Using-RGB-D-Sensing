"""Robust chain layer: skeleton-constraint gating + recovery for
EVERY link of the kinematic chain.

Extends the validated hold-last baseline (occlusion.py, unmodified)
by composition, applying ONE principle uniformly at every segment of
the chain the model is built on - a skeleton segment has a fixed
length, so:

  GATE     an endpoint whose measured segment lengths are physically
           impossible is converted from wrong to missing (depth
           substitution keeps 2D visibility high, so the visibility
           gate cannot catch it; R4 evidence, eval/reports/
           r4_stage5_occlusion.md);
  RECOVER  a missing endpoint with a surviving neighbor is placed at
           the calibrated segment length from that neighbor, along an
           EMA memory of its last measured direction, for a bounded
           horizon.

Applied proximal to distal so recoveries chain exactly like the
solve does:

  hips           rigid pair (hip width): one missing hip is recovered
                 from the other along the remembered hip-line - the
                 ROOT FRAME keeps solving. Both hips missing -> hold.
  shoulders      rigid pair (shoulder width): a missing shoulder (the
                 root's tilt reference and the arm chain's anchor) is
                 recovered from the other shoulder the same way.
  elbows         sphere of the upper-arm length around the shoulder
                 (measured or recovered).
  wrists         sphere of the forearm length around the elbow
                 (measured or recovered).

Pair-violation attribution: when a pair's width is wrong, the torso
diagonals decide which endpoint to gate (each hip/shoulder is checked
against its calibrated distance to the opposite midpoint); if no
single endpoint can be blamed, nothing is gated - the layer never
guesses about measurements it keeps.

Torso line-consistency gate: the torso is rigid (ASSUMPTIONS.md A2),
so the hip line and the shoulder line stay near-parallel - 18.9 deg
maximum over the whole clean R1 recording, against 30-59 deg during
the R4 corruption windows (hands/cube crossing in front of the torso
poison the landmark depth samples while 2D visibility stays ~0.98
and the pair width barely stretches, so neither the visibility gate
nor the width gate can fire; R4 shows BOTH variants - hip-line
corruption at 18-20 s and shoulder-line corruption at 34.5-36 s).
When the two lines disagree by more than line_tol_deg (default 20,
above everything R1 ever does):
  - the corrupt PAIR is the one whose line direction deviates more
    from its own EMA direction memory (corruption moves one line
    away from its history; a real turn moves both lines together and
    never trips the disagreement gate);
  - a single endpoint of that pair blamed by its torso diagonal is
    gated (the normal pair recovery rebuilds it);
  - otherwise both endpoints are rebuilt around their measured
    midpoint along the pair's direction memory, which while gated is
    steered toward the OTHER (surviving) line, so a real turn during
    a gated stretch is still followed. Positions stay live; only the
    line orientation is constrained. Dependent groups demoted, tags
    CONSTRAINED.
The gate has hysteresis (trip line_tol_deg, release
line_release_deg): R4's corruption plateaus hover just under the
trip level after the initial spike, so once tripped the constraint
holds until the two lines actually re-agree. Clean data is
unaffected - a recording that never trips never enters the held
state.

Steady-occluder hip repair (E-027): a hip hidden behind the desk keeps
a usable pixel, but its depth sample belongs to the surface in front
of the body (the desk edge or the rail), and that offset is STEADY from
the first frame, so neither the depth-jump gate nor the line gate nor
the online length calibration can see it - they all learn the
occluder as the baseline. The memory-free signature is the trunk
itself: at a desk the hips sit within about 10 cm of the shoulder
midpoint's camera depth (loop recording, clean torso frames: p01 -0.10
m, p99 +0.10 m), while a hip on the rail reads 0.20-0.36 m nearer (frames 12-631). A
hip nearer the camera than the shoulder midpoint by more than lean_tol
(default 0.15 m, a backward trunk lean of about 17 degrees over a
0.5 m trunk, which a desk task does not produce) is gated as a depth
on an occluder and placed back on its own camera ray at the shoulder
midpoint's depth, an upright trunk (the trunk diagonal cannot fix the
depth: it is nearly vertical, so its sphere meets the ray almost
tangentially). The gate runs after the E-011b gates, on hips they left
in place, so the validated memory repair keeps priority where a jump
was seen. Tag CONSTRAINED on the root.

Angle-parameter stabilization (E-012): two solved parameters lose
observability smoothly, and near the singular pose measurement noise
is amplified into wild parameter swings that the exact-epsilon
guards in the model cannot catch:
  - shoulder twist tau at a straight elbow (1/sin(flexion)
    amplification, ASSUMPTIONS.md A4): below flex_min_deg (default
    15) of elbow flexion the twist is HELD and its bit cleared -
    the same semantics the inner solver already applies at exact
    unobservability, widened to the noise-aware threshold (R4 tau
    steps reach 162 deg/frame at 10-15 deg flexion; R1 right-arm
    flexion never drops below 30, so clean data never engages it);
  - swing yaw theta_y at a vertical arm (Ry becomes rotation about
    the arm axis, R4 yaw steps reach 94 deg/frame above 85 deg of
    elevation) is NOT held - a freeze was tried and rejected: it
    keeps the swing bit live while the output diverges from the
    measurement (up to 27 cm of FK wrist error on nominally live
    frames). The slew limit below bounds the flips honestly instead.
The twist hold has hysteresis (release at flex_release_deg) so it
releases onto trustworthy measurements, not the first frame past
the engage threshold.
All remaining arm-parameter discontinuities - re-lock snaps after a
hold, demotion snaps into constrained recovery, constrained-recovery
wobble - are bounded by a wrap-aware slew limit of rate_limit_deg
(default 15) per frame on every arm parameter (theta_y, theta_z,
tau, ey; 15 deg/frame = 450 deg/s, above any real desk-manipulation
motion; R1's fastest clean right-side step is 11.4). Honesty: while
the limiter is actively clamping, the output is not the
measurement, so the affected group's bit is cleared and its tag set
CONSTRAINED until the output converges. The root is excluded (the
E-011 line gate owns root robustness).

Honesty: any joint group whose supporting landmarks were recovered
keeps its live-mask bit CLEAR and its tag reads CONSTRAINED. Segment
lengths calibrate online (median of the first calib_frames clean
samples per segment) or are passed in. Direction memories update only
from fully measured frames (no feedback from recoveries). All state
is causal. With gating and recovery disabled the output is
bit-identical to ChainFallbackSolver (validate_occlusion_ext.py).

Constant-velocity extrapolation in angle space was evaluated and
rejected (eval/reports/r4_table63_equiv.md) and is deliberately
absent.

Object-conditioned recovery (E-014): when the caller supplies a
per-frame object-derived wrist estimate (the tracked object's pose
plus the fitted grip offset, computed eval-side - the solver never
sees the object or the calibration), the missing-wrist and
missing-elbow recoveries upgrade from memory to measurement-anchored
geometry:
  wrist   a missing wrist whose hand is holding the object is placed
          at the supplied estimate (a live function of the measured
          object pose, not a memory);
  elbow   a missing elbow with BOTH neighbors available (shoulder
          measured or pair-recovered, wrist measured or
          object-recovered) is placed by closed-form two-link IK:
          it lies on the circle of intersection of the two spheres
          |E-S| = upper-arm length and |E-W| = forearm length; the
          point on that circle is chosen by continuity - the
          projection of the upper-arm EMA direction memory onto the
          circle - with a gravity-down anatomical prior as the
          no-memory fallback. Out-of-reach wrists degrade smoothly:
          the cosine is clipped, collapsing the circle onto the S-W
          axis (straight arm).
The block is gated on the obj argument: solve(points) with no obj is
bit-identical to the pre-E-014 layer (validated). Recovered joints
demote their dependent groups to CONSTRAINED exactly like every
other recovery in this layer.

API:
    solver = RobustChainSolver()                    # online calibration
    solver = RobustChainSolver(seg_len={...})       # measured lengths
    angles13, live_mask, tags = solver.solve(points)
    angles13, live_mask, tags = solver.solve(points, obj=obs)
        # obs = {"right": wrist_point_or_None,
        #        "left":  wrist_point_or_None} in the same space as
        # points; a side is present only while that hand HOLDS the
        # tracked object (grip episodes are the caller's judgment)

tags per live-mask group (root, R_swing, R_twist, R_elbow, L_swing,
L_twist, L_elbow): 0 MEASURED, 1 HELD, 2 CONSTRAINED.
"""
import numpy as np

from occlusion import ChainFallbackSolver

TAG_MEASURED, TAG_HELD, TAG_CONSTRAINED = 0, 1, 2
N_GROUPS = 7

# E-020: elbow clearance from the pelvis -> shoulder-mid axis, as a
# fraction of the measured shoulder width. Strictest clean p1 across
# R5 and R1, both sides, with 20 percent slack
# (eval/failure/derive_limit_bounds.py, eval/reports/r5_limit_bounds.md).
TORSO_RADIUS_FRAC = 0.334

# Directed segments, proximal parent -> distal child.
ARM_SEGS = [
    ("right_shoulder", "right_elbow", "upper_arm_R"),
    ("right_elbow", "right_wrist", "forearm_R"),
    ("left_shoulder", "left_elbow", "upper_arm_L"),
    ("left_elbow", "left_wrist", "forearm_L"),
]
PAIRS = [
    ("left_hip", "right_hip", "hip_width"),
    ("left_shoulder", "right_shoulder", "shoulder_width"),
]
# torso diagonals used for pair attribution: joint -> (opposite
# midpoint endpoints, segment name)
DIAGONALS = {
    "left_hip": (("left_shoulder", "right_shoulder"), "torso_hip_L"),
    "right_hip": (("left_shoulder", "right_shoulder"), "torso_hip_R"),
    "left_shoulder": (("left_hip", "right_hip"), "torso_sh_L"),
    "right_shoulder": (("left_hip", "right_hip"), "torso_sh_R"),
}
# landmark -> live-mask bits that consume it (occlusion.py contract);
# the root's shoulder reference is resolved dynamically in solve().
DEPENDENT_BITS = {
    "left_hip": [0],
    "right_hip": [0],
    "right_shoulder": [1, 2, 3],
    "right_elbow": [1, 2, 3],
    "right_wrist": [2, 3],
    "left_shoulder": [4, 5, 6],
    "left_elbow": [4, 5, 6],
    "left_wrist": [5, 6],
}


def _ok(v):
    return v is not None and bool(np.all(np.isfinite(v)))


class RobustChainSolver:
    def __init__(self, seg_len=None, forearm_len=None, gate_tol=0.30,
                 dir_alpha=0.3, horizon=45, calib_frames=60,
                 line_tol_deg=20.0, line_release_deg=10.0,
                 flex_min_deg=15.0, flex_release_deg=25.0,
                 rate_limit_deg=15.0, z_tol=0.10, elbow_limits=False,
                 lean_tol=0.15, hip_hold=False):
        self.inner = ChainFallbackSolver()
        self.gate_tol = gate_tol
        self.line_tol_deg = line_tol_deg
        self.line_release_deg = line_release_deg
        self._line_on = None          # width key of the tripped pair
        self.flex_min_deg = flex_min_deg
        self.flex_release_deg = flex_release_deg
        self.rate_limit_deg = rate_limit_deg
        self._prev_angles = None      # previous OUTPUT angles
        self._prev_mask = 0
        self._tau_hold = {}           # side -> flexion-hysteresis state
        self.stabilized = {}          # param key -> intervention count
        self.stab_frames = {}         # side -> [frame, ...]
        self.alpha = dir_alpha
        self.H = horizon
        self.calib_frames = calib_frames
        self.L = dict(seg_len) if seg_len else {}
        if forearm_len:                       # convenience alias
            self.L.setdefault("forearm_L", forearm_len["left"])
            self.L.setdefault("forearm_R", forearm_len["right"])
        self._samples = {}
        # direction memories: directed arm segments + pair lines
        self.u = {}
        # frames since the joint was last actually measured
        self.k = {}
        self.gated = {}                       # landmark -> count
        self.gated_frames = {}                # landmark -> [frame, ...]
        self.recovered = {}                   # landmark -> count
        self.recovered_frames = {}            # landmark -> [frame, ...]
        self.obj_recovered = {}               # E-014 source -> count
        self.z_tol = z_tol
        self.elbow_limits = elbow_limits      # E-020, opt-in
        self.limit_applied = 0                # capsule interventions
        self.zmem = {}                        # torso landmark -> EMA depth
        self.ray_fixed = {}                   # E-011b repair -> count
        self.z_gated = {}                     # depth-jump gate -> count
        self.lean_tol = lean_tol              # E-027 occluder gate (m)
        self.occluder_gated = {}              # hip -> count
        self.occluder_fixed = {}              # hip -> count
        # E-034 hip hold (opt-in): a hip the torso gates reject, or one
        # the detector does not report, is held at its last ACCEPTED
        # position instead of being placed on its camera ray. Rests on
        # the assumption that the subject does not move while handling
        # the object, so the last clean hip position is still the true
        # one; the root yaw is then frozen with the hip line while the
        # measured shoulders keep the trunk lean live.
        self.hip_hold = hip_hold
        self.pmem = {}                        # hip -> last accepted point
        self.hip_held = {}                    # hip -> count
        self._frame = -1

    # ---- length calibration -------------------------------------------
    def _observe(self, name, length):
        if name in self.L:
            return
        s = self._samples.setdefault(name, [])
        s.append(length)
        if len(s) >= self.calib_frames:
            self.L[name] = float(np.median(s))

    def _bad(self, name, length):
        return (self.gate_tol is not None and name in self.L
                and abs(length - self.L[name])
                > self.gate_tol * self.L[name])

    # ---- helpers ------------------------------------------------------
    @staticmethod
    def _mid(p, a, b):
        return 0.5 * (p[a] + p[b]) if _ok(p.get(a)) and _ok(p.get(b)) \
            else None

    def _gate(self, p, name):
        p[name] = None
        self.gated[name] = self.gated.get(name, 0) + 1
        self.gated_frames.setdefault(name, []).append(self._frame)

    def _learn_dir(self, key, a, b):
        d = b - a
        n = float(np.linalg.norm(d))
        if n < 1e-9:
            return
        u = d / n
        prev = self.u.get(key)
        self.u[key] = u if prev is None else \
            (1 - self.alpha) * prev + self.alpha * u
        self.u[key] /= np.linalg.norm(self.u[key])

    def _torso_capsule(self, p):
        """(pelvis, shoulder_mid, radius) of the torso clearance
        capsule, or None when the torso is not fully available (the
        limit never guesses). Radius = TORSO_RADIUS_FRAC of the
        current shoulder width (subject-scaled)."""
        pts = [p.get(k) for k in ("left_hip", "right_hip",
                                  "left_shoulder", "right_shoulder")]
        if not all(_ok(q) for q in pts):
            return None
        lh, rh, ls, rs = pts
        width = float(np.linalg.norm(ls - rs))
        return (0.5 * (lh + rh), 0.5 * (ls + rs),
                TORSO_RADIUS_FRAC * width)

    @staticmethod
    def _capsule_clear(E, cap):
        a, b, radius = cap
        ab = b - a
        t = float(np.clip(np.dot(E - a, ab)
                          / max(float(np.dot(ab, ab)), 1e-12), 0.0, 1.0))
        return float(np.linalg.norm(E - (a + t * ab))) >= radius

    def _ik_elbow(self, S, W, L1, L2, mem_dir, p=None):
        """Closed-form two-link elbow (E-014): intersection circle of
        the spheres |E-S| = L1 and |E-W| = L2, swivel chosen as the
        projection of mem_dir (the upper-arm EMA, unit shoulder ->
        elbow) onto the circle; gravity-down anatomical prior when no
        usable memory. Out-of-reach and over-folded wrists clip the
        cosine, collapsing the circle onto the S-W axis. Returns the
        elbow point, or None only if S and W coincide.

        E-020 (opt-in, elbow_limits=True and p supplied): the swivel
        circle is pruned by the torso-capsule clearance - if the
        prior's point penetrates the capsule, the feasible point
        angularly nearest the prior is returned instead; an
        all-infeasible circle falls back to the prior unchanged (the
        limit never reduces availability). Of the manipulator-style
        limits only this one survives derivation: elbow flexion is
        identical at every swivel angle (cosine law - the clip already
        bounds it), and a shoulder-twist box rejects genuinely
        measured poses (eval/reports/r5_limit_bounds.md)."""
        d = W - S
        r = float(np.linalg.norm(d))
        if r < 1e-9:
            return None
        dh = d / r
        ca = np.clip((L1 * L1 + r * r - L2 * L2) / (2.0 * L1 * r),
                     -1.0, 1.0)
        c = S + L1 * ca * dh
        rho = L1 * float(np.sqrt(max(0.0, 1.0 - ca * ca)))
        if rho < 1e-9:
            return c
        candidates = [] if mem_dir is None else [np.asarray(mem_dir)]
        candidates += [np.array([0.0, -1.0, 0.0]),
                       np.array([0.0, 0.0, 1.0])]
        prior = c
        for n in candidates:
            perp = n - float(n @ dh) * dh
            m = float(np.linalg.norm(perp))
            if m > 1e-9:
                prior = c + rho * perp / m
                break
        if not self.elbow_limits or p is None or prior is c:
            return prior
        cap = self._torso_capsule(p)
        if cap is None or self._capsule_clear(prior, cap):
            return prior
        u1 = (prior - c) / rho
        u2 = np.cross(dh, u1)
        best, best_cos = None, -2.0
        for phi in np.radians(np.arange(10.0, 360.0, 10.0)):
            cand = c + rho * (np.cos(phi) * u1 + np.sin(phi) * u2)
            if self._capsule_clear(cand, cap) and np.cos(phi) > best_cos:
                best, best_cos = cand, float(np.cos(phi))
        if best is None:
            return prior
        self.limit_applied += 1
        return best

    def _try_recover(self, p, child, anchor_pt, dir_key, seg_name,
                     recovered, sign=1.0):
        """Place child at the calibrated length from the anchor along
        the direction memory, unless the memory is staler than the
        horizon (k ticks every unmeasured frame in solve())."""
        if (anchor_pt is None or dir_key not in self.u
                or seg_name not in self.L):
            return
        if self.H and self.k.get(child, 0) > self.H:
            return
        p[child] = anchor_pt + sign * self.L[seg_name] * self.u[dir_key]
        recovered.add(child)
        self.recovered[child] = self.recovered.get(child, 0) + 1
        self.recovered_frames.setdefault(child, []).append(self._frame)

    # ---- the layer ----------------------------------------------------
    def solve(self, points, obj=None):
        self._frame += 1
        p = {k: (np.asarray(v, float) if v is not None else None)
             for k, v in points.items()}
        recovered = set()

        # 1. GATE, proximal to distal.
        # pairs (hips, shoulders): width violated -> blame via diagonals
        ray_fix = {}          # E-011b: gated joint -> (ray, partner, width)
        line_rays = None      # E-011b: whole-line repair inputs

        def _ray(pt):
            return pt / pt[2] if pt is not None and pt[2] > 0.05 else None

        occl = {}
        smid0 = self._mid(p, "left_shoulder", "right_shoulder")

        for a, b, width in PAIRS:
            if _ok(p.get(a)) and _ok(p.get(b)):
                w = float(np.linalg.norm(p[a] - p[b]))
                self._observe(width, w)
                if self._bad(width, w):
                    blames = []
                    for j in (a, b):
                        (m1, m2), dseg = DIAGONALS[j]
                        mid = self._mid(p, m1, m2)
                        if mid is not None and dseg in self.L:
                            d = float(np.linalg.norm(p[j] - mid))
                            if self._bad(dseg, d):
                                blames.append(j)
                    if len(blames) == 1:
                        j = blames[0]
                        r = _ray(p[j])
                        if r is not None:
                            ray_fix[j] = (r, b if j == a else a, width)
                        self._gate(p, j)
                    # ambiguous -> keep both (never guess)
        # torso line-consistency (rigid torso): hip vs shoulder line
        line_rebuild = None            # (pair a, pair b, width key, mid)
        lh_, rh_ = p.get("left_hip"), p.get("right_hip")
        ls_, rs_ = p.get("left_shoulder"), p.get("right_shoulder")
        if (self.line_tol_deg is not None
                and all(_ok(v) for v in (lh_, rh_, ls_, rs_))):
            hu, su = rh_ - lh_, rs_ - ls_
            nh, ns = np.linalg.norm(hu), np.linalg.norm(su)
            if nh > 1e-9 and ns > 1e-9:
                hu, su = hu / nh, su / ns
                ang = np.degrees(np.arccos(
                    np.clip(float(hu @ su), -1.0, 1.0)))
                have_mem = ("hip_width" in self.u
                            and "shoulder_width" in self.u)
                trip = ang > self.line_tol_deg and have_mem
                held = (self._line_on is not None
                        and ang > self.line_release_deg)
                if not trip and not held:
                    self._line_on = None
                if trip or held:
                    if trip and self._line_on is None:
                        def _dev(u_now, key):
                            return np.degrees(np.arccos(np.clip(
                                float(u_now @ self.u[key]), -1.0, 1.0)))
                        self._line_on = (
                            "hip_width" if _dev(hu, "hip_width")
                            >= _dev(su, "shoulder_width")
                            else "shoulder_width")
                    if self._line_on == "hip_width":
                        a, b, width = "left_hip", "right_hip", "hip_width"
                        steer = su
                    else:
                        a, b, width = ("left_shoulder", "right_shoulder",
                                       "shoulder_width")
                        steer = hu
                    blames = []
                    for j in (a, b):
                        (m1, m2), dseg = DIAGONALS[j]
                        mid = self._mid(p, m1, m2)
                        if mid is not None and dseg in self.L:
                            d = float(np.linalg.norm(p[j] - mid))
                            if self._bad(dseg, d):
                                blames.append(j)
                    if len(blames) == 1:
                        j = blames[0]
                        r = _ray(p[j])
                        if r is not None:
                            ray_fix[j] = (r, b if j == a else a, width)
                        self._gate(p, j)
                    elif width in self.L:
                        # whole line suspect: preferred repair is
                        # ray-based (E-011b, step 3): the PIXEL
                        # directions of both endpoints stay reliable
                        # when the depth corrupts, so both are placed
                        # on their own rays at remembered depths,
                        # scaled so the pair width is the calibrated
                        # one. Fallback (no depth memory yet): keep
                        # the measured midpoint, steer the line
                        # memory toward the surviving line, rebuild
                        # along it.
                        line_rays = (a, b, width, _ray(p[a]),
                                     _ray(p[b]))
                        line_rebuild = (a, b, width,
                                        0.5 * (p[a] + p[b]))
                        # E-034: a hip pair with an accepted position
                        # to return to keeps its line memory too (the
                        # hold below returns the last accepted hips,
                        # whose line IS the memory)
                        if not (self.hip_hold and width == "hip_width"
                                and any(j in self.pmem for j in (a, b))):
                            prev = self.u[width]
                            u = (1 - self.alpha) * prev + self.alpha * steer
                            self.u[width] = u / np.linalg.norm(u)
                        self._gate(p, a)
                        self._gate(p, b)
        # depth-jump gate (E-011b): consensus corruption - both torso
        # lines poisoned TOGETHER - keeps the lines agreeing, so the
        # line gate above cannot fire (its documented residual
        # limitation). But the corruption is a DEPTH jump at a
        # standing pixel: a torso landmark whose camera depth leaves
        # its EMA memory by more than z_tol in effect teleported
        # (10 cm/frame = 3 m/s), which no real torso does. Plot-first
        # threshold: clean deviations reach 2.5 cm on R1 and p99
        # ~5 cm on R5's clean-torso frames; corrupt R5 hips sit at a
        # median 23 cm. Gated joints are repaired on their rays in
        # step 3 - a whole pair through the hybrid line rebuild, a
        # single joint individually.
        if self.z_tol is not None:
            for a, b, width in PAIRS:
                flags = [j for j in (a, b)
                         if _ok(p.get(j)) and j in self.zmem
                         and abs(float(p[j][2]) - self.zmem[j])
                         > self.z_tol]
                # the pair rebuild needs the calibrated width and the
                # line memory; before calibration completes, fall back
                # to the per-joint ray repairs below
                if (len(flags) == 2 and line_rebuild is None
                        and width in self.L and width in self.u):
                    line_rays = (a, b, width, _ray(p[a]), _ray(p[b]))
                    line_rebuild = (a, b, width, 0.5 * (p[a] + p[b]))
                    for j in flags:
                        self._gate(p, j)
                        self.z_gated[j] = self.z_gated.get(j, 0) + 1
                else:
                    for j in flags:
                        r = _ray(p[j])
                        if r is not None and j not in ray_fix:
                            ray_fix[j] = (r, b if j == a else a, width)
                        self._gate(p, j)
                        self.z_gated[j] = self.z_gated.get(j, 0) + 1
        # E-027 steady-occluder hip gate: runs after the E-011b gates, on
        # hips they left in place, so their validated memory repair keeps
        # priority where a jump was seen and this gate catches only the
        # steady offset no memory can see
        if self.lean_tol is not None and smid0 is not None:
            for j in ("left_hip", "right_hip"):
                if _ok(p.get(j)) and \
                        float(p[j][2] - smid0[2]) < -self.lean_tol:
                    r = _ray(p[j])
                    if r is not None:
                        occl[j] = r
                    self._gate(p, j)
                    self.occluder_gated[j] = \
                        self.occluder_gated.get(j, 0) + 1
        # torso diagonal lengths calibrate + solo-diagonal gating
        for j, ((m1, m2), dseg) in DIAGONALS.items():
            mid = self._mid(p, m1, m2)
            if _ok(p.get(j)) and mid is not None:
                d = float(np.linalg.norm(p[j] - mid))
                self._observe(dseg, d)
        # arm segments: proximal endpoint is trusted, gate the distal
        for parent, child, seg in ARM_SEGS:
            if _ok(p.get(parent)) and _ok(p.get(child)):
                L = float(np.linalg.norm(p[child] - p[parent]))
                self._observe(seg, L)
                if self._bad(seg, L):
                    self._gate(p, child)

        # 2. learn direction memories from fully measured geometry
        for a, b, width in PAIRS:
            if _ok(p.get(a)) and _ok(p.get(b)):
                self._learn_dir(width, p[a], p[b])   # a -> b line
        for parent, child, seg in ARM_SEGS:
            if _ok(p.get(parent)) and _ok(p.get(child)):
                self._learn_dir(seg, p[parent], p[child])
        # depth memories of the torso landmarks (E-011b): EMA of the
        # camera-axis depth, updated only from measured (ungated)
        # frames, consumed by the ray repairs in step 3
        for a, b, _w in PAIRS:
            for j in (a, b):
                if _ok(p.get(j)):
                    z = float(p[j][2])
                    prev = self.zmem.get(j)
                    self.zmem[j] = z if prev is None else \
                        (1 - self.alpha) * prev + self.alpha * z
        # E-034: last accepted hip positions (no blending: the hold
        # returns exactly the last clean sample)
        if self.hip_hold:
            for j in ("left_hip", "right_hip"):
                if _ok(p.get(j)):
                    self.pmem[j] = p[j].copy()
        for name in DEPENDENT_BITS:
            if _ok(p.get(name)):
                self.k[name] = 0
            else:
                self.k[name] = self.k.get(name, 0) + 1

        # 3. RECOVER, proximal to distal (recoveries may chain)
        def _mark(j):
            recovered.add(j)
            self.recovered[j] = self.recovered.get(j, 0) + 1
            self.recovered_frames.setdefault(j, []).append(self._frame)

        # E-011b ray repair: a joint gated for corrupt DEPTH keeps a
        # reliable PIXEL direction, so it is placed back on its own
        # camera ray at its remembered depth. The pair width is NOT
        # forced onto the repair: the apparent width varies 10-15
        # percent with pose in this data, and rescaling to the
        # calibrated median was measured to inject ~10 cm of common
        # depth error - rigidity stays a detector, not a projector.
        def _ray_repair(j, r):
            zm = self.zmem.get(j)
            if r is None or zm is None:
                return False
            p[j] = zm * r
            _mark(j)
            self.ray_fixed[j] = self.ray_fixed.get(j, 0) + 1
            return True

        # E-034 hip hold: a rejected or unreported hip returns to its
        # last accepted position; the ray, occluder and pair repairs
        # below then leave it alone (a pair rebuild of the hip line is
        # cancelled: the held line IS the remembered line).
        if self.hip_hold:
            held_now = []
            for j in ("left_hip", "right_hip"):
                if not _ok(p.get(j)) and j in self.pmem:
                    p[j] = self.pmem[j].copy()
                    _mark(j)
                    self.hip_held[j] = self.hip_held.get(j, 0) + 1
                    held_now.append(j)
            if held_now and line_rebuild is not None \
                    and line_rebuild[0] == "left_hip":
                # the pair rebuild would overwrite a held hip; a hip
                # without a memory yet falls to the single-hip pair
                # recovery from the held one below
                line_rebuild = None
                line_rays = None
            for j in held_now:
                ray_fix.pop(j, None)
                occl.pop(j, None)

        # E-027 repair: the gated hip on its own ray at the shoulder
        # midpoint's depth, an upright trunk. The trunk diagonal cannot
        # fix the depth instead: it is nearly vertical, so its sphere
        # meets the hip ray almost tangentially and the depth is ill-
        # conditioned (swings of tens of centimetres on the loop
        # recording). The upright placement is wrong by the trunk's
        # lean, at most the 10 cm the clean data shows.
        for j, r in occl.items():
            if j in recovered or smid0 is None:
                continue
            p[j] = float(smid0[2]) * r
            _mark(j)
            self.occluder_fixed[j] = self.occluder_fixed.get(j, 0) + 1

        for j, (r, partner, width) in ray_fix.items():
            if j not in recovered:
                _ray_repair(j, r)
        # line-gated pair: preferred repair (E-011b) separates what
        # each source is good for. POSITION comes from the rays at
        # remembered depths (the pair midpoint - this is what removes
        # the pelvis depth wobble; verified to 0.2 cm on synthetic
        # depth corruption). ORIENTATION comes from the repaired
        # ray direction passed through the line's EMA memory: raw
        # per-frame ray directions carry the pixel wobble of
        # hands crossing in front of the torso, the EMA attenuates
        # it while still following a genuine turn. Fallback (no
        # depth memory yet): measured midpoint + steered memory.
        if line_rebuild is not None:
            a, b, width, mid = line_rebuild
            done = False
            if line_rays is not None:
                _, _, _, ra, rb = line_rays
                za, zb = self.zmem.get(a), self.zmem.get(b)
                if ra is not None and rb is not None \
                        and za is not None and zb is not None:
                    qa, qb = za * ra, zb * rb
                    d = qb - qa
                    nrm = float(np.linalg.norm(d))
                    if nrm > 1e-9:
                        u = (1 - self.alpha) * self.u[width] \
                            + self.alpha * (d / nrm)
                        self.u[width] = u / np.linalg.norm(u)
                        half = 0.5 * self.L[width] * self.u[width]
                        m2 = 0.5 * (qa + qb)
                        p[a] = m2 - half
                        p[b] = m2 + half
                        for j in (a, b):
                            _mark(j)
                            self.ray_fixed[j] = \
                                self.ray_fixed.get(j, 0) + 1
                        done = True
            if not done:
                half = 0.5 * self.L[width] * self.u[width]
                p[a] = mid - half
                p[b] = mid + half
                for j in (a, b):
                    _mark(j)
        for a, b, width in PAIRS:
            if _ok(p.get(a)) and not _ok(p.get(b)):
                self._try_recover(p, b, p[a], width, width, recovered)
            elif _ok(p.get(b)) and not _ok(p.get(a)):
                self._try_recover(p, a, p[b], width, width, recovered,
                                  sign=-1.0)
        # object-conditioned recovery (E-014), gated on the obj input:
        # wrist from the object-derived estimate, then elbow by two-link
        # IK between its surviving neighbors. Runs before the EMA arm
        # recoveries so a measurement-anchored placement wins over a
        # memory-based one; whatever it cannot place falls through.
        if obj is not None:
            for side, sh, el, wr, useg, fseg in (
                    ("right", "right_shoulder", "right_elbow",
                     "right_wrist", "upper_arm_R", "forearm_R"),
                    ("left", "left_shoulder", "left_elbow",
                     "left_wrist", "upper_arm_L", "forearm_L")):
                w_obj = obj.get(side)
                if not _ok(p.get(wr)) and _ok(w_obj):
                    p[wr] = np.asarray(w_obj, float)
                    recovered.add(wr)
                    self.recovered[wr] = self.recovered.get(wr, 0) + 1
                    self.recovered_frames.setdefault(wr, []).append(
                        self._frame)
                    key = f"{side}_wrist_obj"
                    self.obj_recovered[key] = \
                        self.obj_recovered.get(key, 0) + 1
                if (not _ok(p.get(el)) and _ok(p.get(sh))
                        and _ok(p.get(wr))
                        and useg in self.L and fseg in self.L):
                    # conditioning guard: near full extension the
                    # cosine law's flexion is ill-conditioned (the
                    # derivative of flexion w.r.t. the shoulder-wrist
                    # distance diverges as r -> L1+L2), so a
                    # centimeter of wrist-estimate error becomes tens
                    # of degrees of flexion. Above REACH_COND of full
                    # reach, prefer the elbow direction memory (if
                    # fresh) and keep the wrist anchored at the
                    # estimate; the IK remains the fallback.
                    r_sw = float(np.linalg.norm(p[wr] - p[sh]))
                    reach = self.L[useg] + self.L[fseg]
                    e = None
                    if (r_sw > 0.98 * reach and useg in self.u
                            and (not self.H
                                 or self.k.get(el, 0) <= self.H)):
                        e = p[sh] + self.L[useg] * self.u[useg]
                    if e is None:
                        e = self._ik_elbow(p[sh], p[wr], self.L[useg],
                                           self.L[fseg],
                                           self.u.get(useg), p)
                    if e is not None:
                        p[el] = e
                        recovered.add(el)
                        self.recovered[el] = \
                            self.recovered.get(el, 0) + 1
                        self.recovered_frames.setdefault(el, []).append(
                            self._frame)
                        key = f"{side}_elbow_ik"
                        self.obj_recovered[key] = \
                            self.obj_recovered.get(key, 0) + 1
        for parent, child, seg in ARM_SEGS:
            if _ok(p.get(parent)) and not _ok(p.get(child)):
                self._try_recover(p, child, p[parent], seg, seg,
                                  recovered)

        # 4. the unchanged kinematic solve
        angles, mask = self.inner.solve(p)
        tags = np.array([TAG_MEASURED if mask & (1 << g) else TAG_HELD
                         for g in range(N_GROUPS)])

        # 5. honesty: demote every group that consumed a recovery
        demote = set()
        for name in recovered:
            demote.update(DEPENDENT_BITS[name])
        # the root's tilt reference is the right shoulder when present
        root_ref = ("right_shoulder" if _ok(p.get("right_shoulder"))
                    else "left_shoulder")
        if root_ref in recovered:
            demote.add(0)
        for g in demote:
            if mask & (1 << g):
                mask &= ~(1 << g)
                tags[g] = TAG_CONSTRAINED

        # 6. angle-parameter stabilization (docstring, E-012):
        # observability holds at the two smooth singularities + a
        # wrap-aware slew limit, re-lock exempted.
        def _wrap(a):
            return (a + 180.0) % 360.0 - 180.0

        def _stab(side, key):
            self.stabilized[f"{key}"] = self.stabilized.get(key, 0) + 1
            self.stab_frames.setdefault(side, []).append(self._frame)

        if self._prev_angles is not None:
            prev = self._prev_angles
            for side, ty_i, thz_i, tau_i, ey_i, sw_bit, tw_bit, el_bit, \
                    sw_g, tw_g, el_g in (
                    ("right_arm", 3, 4, 5, 6, 1 << 1, 1 << 2, 1 << 3,
                     1, 2, 3),
                    ("left_arm", 8, 9, 10, 11, 1 << 4, 1 << 5, 1 << 6,
                     4, 5, 6)):
                # twist observability hold, flexion hysteresis
                if self.flex_min_deg is not None:
                    f = abs(angles[ey_i])
                    hold = self._tau_hold.get(side, False)
                    if hold and f > self.flex_release_deg:
                        hold = False
                    elif not hold and f < self.flex_min_deg:
                        hold = True
                    self._tau_hold[side] = hold
                    if hold and mask & tw_bit:
                        angles[tau_i] = prev[tau_i]
                        mask &= ~tw_bit
                        tags[tw_g] = TAG_HELD
                        _stab(side, f"{side}_tau_flex_hold")
                # universal slew limit; clamping means the output is
                # not the measurement -> demote while catching up
                if self.rate_limit_deg is not None:
                    for j, bit, g in ((ty_i, sw_bit, sw_g),
                                      (thz_i, sw_bit, sw_g),
                                      (tau_i, tw_bit, tw_g),
                                      (ey_i, el_bit, el_g)):
                        d = _wrap(angles[j] - prev[j])
                        if abs(d) > self.rate_limit_deg:
                            angles[j] = _wrap(prev[j] + np.clip(
                                d, -self.rate_limit_deg,
                                self.rate_limit_deg))
                            if mask & bit:
                                mask &= ~bit
                                tags[g] = TAG_CONSTRAINED
                            _stab(side, f"{side}_rate_limit")
        self._prev_angles = angles.copy()
        self._prev_mask = int(mask)
        # post-recovery input points (diagnostics + downstream pelvis)
        self.last_points = p
        return angles, mask, tags
