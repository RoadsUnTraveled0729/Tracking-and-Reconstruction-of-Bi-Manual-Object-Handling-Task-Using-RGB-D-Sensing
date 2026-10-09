"""S2: quaternion prediction with damped velocity decay (V3_PLAN.md
Phase 4, cheapest candidate; the advanced-math robustness claim).

Per joint (root, R/L shoulder, R/L elbow) the state is a unit
quaternion plus an angular-velocity rotvec estimated from consecutive
measurements. While a joint is measured, output = measurement and the
velocity updates (EMA). While unobservable, the quaternion propagates
by the decayed velocity (q <- q * qexp(w), w <- lambda * w), so motion
continues plausibly and dies out instead of freezing instantly
(baseline) or diverging (undamped). On reacquisition the output
approaches the measurement along the geodesic with a per-frame step
cap, so the baseline's teleport snap is structurally impossible; the
group reports ESTIMATED until converged.

Twist handling uses the swing-twist decomposition about the arm axis
(+x): when the swing is measured but the twist is unobservable
(straight elbow or blocked wrist), the measured swing is combined with
the predicted twist -- the measured part is never discarded.

M4 additions (each off in the legacy configuration, which reproduces
the pre-M4 output bit-for-bit): a causal smoother per track between
the measurement and the step cap (strategies/smoother_base.py,
D-029), warm start from the first measurement (D-031), and step caps
derived from the active scenario manifest's teleport budgets with an
absolute cap of D-021 (D-032).

All tunables live in the config s2_quat_prediction block.
"""
import json
from pathlib import Path

import numpy as np

from bench.metrics import ESTIMATED, GROUP_NAMES, LOST, MEASURED
from bench.paths import repo_path
from core import convert, solver_q
from core.representation import (QUAT_ID, angle_between, hemisphere, qconj,
                                 qexp, qlog, qmul, qrotate, quat_about,
                                 slerp)
from strategies.smoother_base import (NoSmoother, TRACK_KINDS,
                                      build_smoother)
from strategies.strategy_base import (OcclusionStrategy, StrategyOutput,
                                      register)
from strategies.vendor_rest import root_rest_quat

_X = np.array([1.0, 0.0, 0.0])
_Y = np.array([0.0, 1.0, 0.0])
_Z = np.array([0.0, 0.0, 1.0])
G = {name: i for i, name in enumerate(GROUP_NAMES)}


def project_v1_swing(q):
    """Nearest quat on v1's swing manifold Ry(ty)*Rz(tz): re-derive
    (ty, tz) from where q carries the arm axis and recompose. The
    geometric swing-twist decomposition about x is NOT this manifold
    (Ry*Rz itself has an x quat component), and mixing the two made
    swing blend steps leak into the extracted twist angle (measured:
    r_twist stepped 2.83 deg vs its 2.49 budget with both tracks
    individually capped)."""
    a = qrotate(q, _X)
    tz = np.arcsin(float(np.clip(a[1], -1.0, 1.0)))
    ty = (0.0 if 1.0 - abs(a[1]) < convert.GIMBAL_EPS
          else float(np.arctan2(-a[2], a[0])))
    return qmul(quat_about(_Y, ty), quat_about(_Z, tz))


class _JointTrack:
    """One quaternion track: measure/smooth/predict/cap state machine.

    projector: when set, the state is re-projected onto the swing
    manifold after every predicted or blended step. Without this,
    slerp/exp outputs acquire a parasitic twist component that the v1
    angle extraction re-attributes to the twist angle, whose combined
    step then exceeds the twist track's own cap (measured: r_twist
    stepped 2.83 deg vs its 2.49 budget at the elbow_long
    reacquisition).

    smoother (M4, strategies/smoother_base.py): applied to the
    measurement after the hemisphere alignment and before the step
    cap; "none" is the identity (bit-for-bit the pre-M4 track).
    warm_start (D-031): the first accepted measurement initializes the
    output instead of being approached from the rest pose.
    The step cap is the D-021 absolute cap on the output step; its
    value per track comes from derive_step_caps (D-032).
    """

    def __init__(self, q_rest, decay, step_cap_rad, vel_alpha,
                 projector=None, smoother=None, warm_start=False):
        self.q_rest = q_rest
        self.decay = decay
        self.step_cap = step_cap_rad
        self.vel_alpha = vel_alpha
        self.projector = projector
        self.smoother = smoother if smoother is not None else NoSmoother()
        self.warm_start = bool(warm_start)
        self.reset()

    def _project(self, q):
        return q if self.projector is None else self.projector(q)

    def reset(self):
        self.q = self.q_rest.copy()     # output state
        self.q_meas_prev = None         # last measurement
        self.w = np.zeros(3)            # rotvec / frame
        self.held = 0                   # frames since last measurement
        self.blending = False
        self.ever_measured = False
        self.capped = False             # diagnostics (cap activity)
        self.smoother.reset()

    def update(self, q_meas):
        """q_meas: unit quat or None. Returns (q_out, measured_now,
        converged): measured_now = a measurement arrived; converged =
        output equals the (smoothed) measurement (False mid-blend)."""
        self.capped = False
        if q_meas is None:
            self.held += 1
            if self.ever_measured:
                self.q = self._project(qmul(self.q, qexp(self.w)))
                self.w *= self.decay
                self.smoother.update(self.q, False)
            self.blending = False if not self.ever_measured else self.blending
            return self.q, False, False

        q_meas = hemisphere(q_meas, self.q)
        if self.q_meas_prev is not None and self.held == 0:
            w_new = qlog(qmul(qconj(self.q_meas_prev), q_meas))
            self.w = (1 - self.vel_alpha) * self.w + self.vel_alpha * w_new
        self.held = 0
        self.q_meas_prev = q_meas
        first = not self.ever_measured
        self.ever_measured = True

        target = self.smoother.update(q_meas, True)
        if target is not q_meas:
            target = hemisphere(target, self.q)

        if first and self.warm_start:
            self.q = target
            self.blending = False
            return self.q, True, True

        # Output continuity is unconditional: ANY implied step beyond
        # the cap is approached along the geodesic, not jumped -- this
        # covers reacquisition after a hold AND measurement-side
        # discontinuities (e.g. the v1 root reference switching
        # shoulders when one is occluded, measured at 2.29 deg on the
        # root_ref scenario, identical under hold-last). A capped
        # frame reports non-converged, hence ESTIMATED: the output
        # deviates from the raw measurement until it catches up.
        gap = angle_between(self.q, target)
        if gap <= self.step_cap:
            self.q = target
            self.blending = False
            return self.q, True, True
        self.blending = True
        self.capped = True      # diagnostics: the cap bound this step
        self.q = self._project(slerp(self.q, target, self.step_cap / gap))
        return self.q, True, False


CAP_KINDS = ("root", "swing", "twist", "elbow")


def derive_step_caps(s2, budgets):
    """Per-track step caps in deg, keyed "root", "r_swing", "l_swing",
    ... (D-032). s2: the config s2_quat_prediction block; budgets:
    {angle: teleport budget deg} from the active scenario manifest, or
    None for step_cap_source "fixed".

    fixed:    step_caps_deg[kind] for both sides (D-021 values).
    manifest: step_cap_budget_fraction x the smallest budget among the
              angles the track drives (step_cap_track_angles, "{s}"
              replaced by r / l); identically-zero angles (budget at
              the 1e-9 noise floor of bench.metrics.teleport_budget)
              are skipped because no step of the track moves them.
    """
    src = s2.get("step_cap_source", "fixed")
    keys = ["root"] + [f"{sd}_{k}" for sd in ("r", "l")
                       for k in CAP_KINDS[1:]]
    if src == "fixed":
        caps = s2["step_caps_deg"]
        return {k: float(caps[k.split("_")[-1]]) for k in keys}
    if src != "manifest":
        raise ValueError(f"unknown step_cap_source {src!r}")
    if budgets is None:
        raise ValueError("step_cap_source manifest needs the manifest "
                         "teleport budgets")
    frac = s2.get("step_cap_budget_fraction")
    angles = s2.get("step_cap_track_angles")
    if frac is None or angles is None:
        raise ValueError("step_cap_budget_fraction / step_cap_track_angles"
                         " null (D-006)")
    out = {}
    for k in keys:
        side, kind = (None, "root") if k == "root" else k.split("_")
        names = [a.replace("{s}", side or "") for a in angles[kind]]
        b = [float(budgets[a]) for a in names if float(budgets[a]) > 1e-6]
        if not b:
            raise ValueError(f"no non-degenerate budget for track {k}")
        out[k] = float(frac) * min(b)
    return out


def smoother_params_for(s2, smoother):
    """Per-kind parameter dicts of the named smoother. smoother_params
    is either keyed by smoother name ({"quat_one_euro": {kind: {..}},
    "tangent_kf": {kind: {..}}}, D-038) or, legacy / sweep overrides,
    a flat {kind: {..}} dict for the selected smoother. The layout is
    decided by the keys: flat when every key (ignoring '_' comment keys)
    is a track kind, nested otherwise; a nested dict without a block for
    the selected smoother raises ValueError naming that block (D-006).
    'none' takes no parameters, so it gets {} when it has no block."""
    sp = s2.get("smoother_params") or {}
    keys = [k for k in sp if not str(k).startswith("_")]
    if all(k in TRACK_KINDS for k in keys):
        return sp
    sub = sp.get(smoother)
    if isinstance(sub, dict):
        return sub
    if smoother == "none" and sub is None:
        return {}
    raise ValueError(
        f"config s2_quat_prediction.smoother_params is keyed by smoother "
        f"name ({sorted(keys)}) but has no dict block "
        f"'smoother_params.{smoother}' for the selected smoother (D-006)")


def _with_decay(params, s2):
    """A copy of one kind's smoother params with decay_lambda defaulting
    to S2's decay_lambda (the tangent_kf velocity damping on unmeasured
    frames, D-038); other smoothers ignore the key."""
    if params is None:
        return None
    p = dict(params)
    if p.get("decay_lambda") is None:
        p["decay_lambda"] = float(s2["decay_lambda"])
    return p


def _manifest_budgets(cfg):
    path = repo_path(cfg["paths"]["scenario_manifest"])
    return json.loads(Path(path).read_text())["teleport_budget_deg"]


@register
class S2QuatPrediction(OcclusionStrategy):
    name = "s2_quat_prediction"

    def __init__(self, cfg):
        s2 = cfg["strategy"]["s2_quat_prediction"]
        for key in ("decay_lambda", "velocity_ema_alpha"):
            if s2.get(key) is None:
                raise ValueError(f"config s2_quat_prediction.{key} is "
                                 "null (D-006)")
        if s2.get("step_cap_source", "fixed") == "fixed" and \
                s2.get("step_caps_deg") is None:
            raise ValueError("config s2_quat_prediction.step_caps_deg is "
                             "null (D-006)")
        budgets = (_manifest_budgets(cfg)
                   if s2.get("step_cap_source", "fixed") == "manifest"
                   else None)
        self.step_caps_deg = derive_step_caps(s2, budgets)
        smoother = s2.get("smoother", "none")
        sparams = smoother_params_for(s2, smoother)
        freq = float(cfg["filter"]["freq_hz"])
        warm = bool(s2.get("warm_start", False))

        def mk(kind, q_rest, side=None):
            proj = project_v1_swing if kind in ("swing",) else None
            sproj = (project_v1_swing if kind in ("swing", "elbow")
                     else None)
            key = kind if side is None else f"{side}_{kind}"
            return _JointTrack(q_rest, float(s2["decay_lambda"]),
                               np.radians(self.step_caps_deg[key]),
                               float(s2["velocity_ema_alpha"]),
                               projector=proj,
                               smoother=build_smoother(
                                   smoother, kind,
                                   _with_decay(sparams.get(kind), s2),
                                   freq, projector=sproj),
                               warm_start=warm)
        self._mk = mk
        self.lost_after = int(cfg["status"]["lost_after_frames"])
        self.reset()

    def reset(self):
        # separate tracks per STATUS GROUP: swing and twist are
        # independent state machines, so a returning wrist blends the
        # twist through the step cap instead of snapping it inside a
        # composite shoulder quat (first-grade teleport bug). Caps are
        # per track kind (and per side under step_cap_source manifest):
        # the root drives the tightest-budget angles and also couples
        # into every arm angle through the solve chain.
        self.root = self._mk("root", root_rest_quat())
        self.arms = {s: {k: self._mk(k, QUAT_ID, side=s)
                         for k in ("swing", "twist", "elbow")}
                     for s in ("r", "l")}

    def _status(self, track, measured_now, converged):
        if measured_now:
            return MEASURED if converged else ESTIMATED
        return ESTIMATED if track.held <= self.lost_after else LOST

    def update(self, t, points, scores):
        p = {k: (np.asarray(v, float) if v is not None else None)
             for k, v in points.items()}
        ok = {k: (p.get(k) is not None
                  and bool(np.all(np.isfinite(p[k]))))
              for k in ("left_hip", "right_hip", "left_shoulder",
                        "right_shoulder", "left_elbow", "right_elbow",
                        "left_wrist", "right_wrist")}
        status = np.empty(len(GROUP_NAMES), dtype=int)

        # root: measured when both hips + either shoulder are present
        ref = (p["right_shoulder"] if ok["right_shoulder"]
               else p["left_shoulder"] if ok["left_shoulder"] else None)
        q_root_meas = None
        if ok["left_hip"] and ok["right_hip"] and ref is not None:
            q_root_meas = solver_q.solve_root_q(
                p["left_hip"], p["right_hip"], ref)
        q_root, mnow, conv = self.root.update(q_root_meas)
        status[G["root"]] = self._status(self.root, mnow, conv)

        out_q = {"root": q_root}
        diag = {"root_held": self.root.held}
        for side, solver, names in (
                ("r", solver_q.solve_right_arm_q,
                 ("right_shoulder", "right_elbow", "right_wrist")),
                ("l", solver_q.solve_left_arm_q,
                 ("left_shoulder", "left_elbow", "left_wrist"))):
            sh_n, el_n, wr_n = names
            tr = self.arms[side]
            gs, gt, ge = (G[f"{side.upper()}_swing"],
                          G[f"{side.upper()}_twist"],
                          G[f"{side.upper()}_elbow"])
            swing_meas = twist_q_meas = q_el_meas = None
            diag[f"{side}_twist_ok"] = False
            if ok[sh_n] and ok[el_n]:
                wr = p[wr_n] if ok[wr_n] else \
                    p[el_n] + (p[el_n] - p[sh_n])          # v1 fake wrist
                q_sh_full, q_el, twist_ok = solver(
                    p[sh_n], p[el_n], wr, q_root)
                # split in v1's OWN factorization Ry*Rz*Rx so the
                # extracted tt depends on the twist track alone
                ty, tz, tt = np.radians(convert.shoulder_angles(q_sh_full))
                swing_meas = qmul(quat_about(_Y, ty), quat_about(_Z, tz))
                if twist_ok and ok[wr_n]:
                    twist_q_meas = quat_about(_X, tt)
                    diag[f"{side}_twist_ok"] = True
                if ok[wr_n]:
                    q_el_meas = q_el

            q_sw, sw_now, sw_conv = tr["swing"].update(swing_meas)
            q_tw, tw_now, tw_conv = tr["twist"].update(twist_q_meas)
            q_el, el_now, el_conv = tr["elbow"].update(q_el_meas)
            status[gs] = self._status(tr["swing"], sw_now, sw_conv)
            status[gt] = self._status(tr["twist"], tw_now, tw_conv)
            status[ge] = self._status(tr["elbow"], el_now, el_conv)
            out_q[f"{side}_sh"] = qmul(q_sw, q_tw)
            out_q[f"{side}_elb"] = q_el

        angles = convert.angles13(out_q["root"], out_q["r_sh"],
                                  out_q["r_elb"], out_q["l_sh"],
                                  out_q["l_elb"])
        return StrategyOutput(angles, status, diag)
