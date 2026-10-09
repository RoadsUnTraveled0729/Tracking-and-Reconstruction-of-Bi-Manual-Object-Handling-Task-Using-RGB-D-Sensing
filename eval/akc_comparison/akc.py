"""Arm Kinematic Correction (AKC): a re-implementation for comparison.

Source method: C. Kwok, K. Koenig and Y. Hu, "Seeing Through Occlusion:
Deterministic Arm Kinematic Correction for Robot Teleoperation",
arXiv 2606.19240, June 2026. No code was released; this module is
written from the paper's text:

- Section II-C (Stage 3, temporal landmark filtering): visibility gate
  0.7; the depth of a proximal joint (elbow, shoulder) whose 2-D
  projection lies within 5 % of the image width of the wrist is
  discarded; constant-velocity Kalman filter per landmark, Eq. (1)-(3),
  R = diag(sx^2, sy^2, sz^2), sz >> sx, sy; EKF soft bone-length
  constraint, Eq. (4)-(6).
- Section II-D (Stage 4, AKC): wrist kept; elbow and shoulder depth
  from the Pythagorean relation, Eq. (7)-(8), four candidates;
  negative-radicand fallback, Eq. (9); shrink l' = s l during the
  candidate search (Section II-D2); cost c = sum w_j m_j, Eq. (10)-(15),
  w4 = w5 = 100. The chosen branch is output by the same relation at
  the unscaled lengths (AKC-053; output_shrunk=True keeps the
  search-time points).
- Section III-E: weight sets W_a, W_b, W_c.

Gaps the paper leaves open, filled here (each is an UNCERTAIN entry in
eval/akc_comparison/DECISIONS.md; none was tuned on scored data):

- Q, dt, P0 and the covariance magnitudes (AKC-008 .. AKC-012);
- the partial (x, y only) Kalman update when depth is discarded
  (AKC-013);
- the EKF constraint noise sigma_l, the order of the constraints and
  their anchor (the Stage-3 filtered wrist, AKC-015, AKC-016, AKC-056);
- the penalty k of m5 and the definition of the elbow angle theta
  (AKC-022, AKC-023);
- correction every frame, no feedback into the Kalman filter, m3 = 0
  on the first frame, m4 = 0 without the other shoulder (AKC-024 ..
  AKC-027);
- metres as the unit of every cost term (AKC-028);
- the "ray" variant, which keeps the landmark pixel and solves on its
  camera ray instead of fixing x, y (AKC-018).

Pure numpy; no repository imports. Coordinates: camera frame, metres,
x right, y down, z forward (RealSense convention).
"""
import sys

sys.dont_write_bytecode = True

from dataclasses import dataclass, field  # noqa: E402

import numpy as np  # noqa: E402

# Color-stream intrinsics of every recording (AKC-002); source:
# v1/mediapipe/output/<stem>_landmarks_raw.meta.json, zero distortion.
INTRINSICS = dict(fx=607.561279296875, fy=607.0150756835938,
                  cx=323.93756103515625, cy=248.0174102783203,
                  width=640, height=480)
VIS_MIN = 0.7      # paper Section II-C (AKC-003)
PROX_FRAC = 0.05   # paper Section II-C, fraction of image width (AKC-004)

# A1 defaults of the approved plan (AKC-008 .. AKC-015).
DEFAULT_KF = dict(dt=0.03336, sigma_a=5.0, sigma_xy=0.01, sigma_z=0.05)
DEFAULT_SIGMA_L = 0.02

ARM_JOINTS = ("shoulder", "elbow", "wrist")


# --------------------------------------------------------------------------
# Camera geometry
# --------------------------------------------------------------------------

def project(p, K=INTRINSICS):
    """Camera-frame xyz (metres) -> pixel (u, v)."""
    x, y, z = (float(c) for c in p)
    return np.array([K["fx"] * x / z + K["cx"], K["fy"] * y / z + K["cy"]])


def deproject(u, v, z, K=INTRINSICS):
    """Pixel (u, v) at depth z -> camera-frame xyz."""
    z = float(z)
    return np.array([(float(u) - K["cx"]) * z / K["fx"],
                     (float(v) - K["cy"]) * z / K["fy"], z])


def ray(u, v, K=INTRINSICS):
    """Unit direction of the camera ray through pixel (u, v)."""
    d = np.array([(float(u) - K["cx"]) / K["fx"],
                  (float(v) - K["cy"]) / K["fy"], 1.0])
    return d / np.linalg.norm(d)


def ray_sphere_roots(d, center, radius):
    """Positive distances t with |t d - center| = radius, d a unit vector.

    Returns a sorted list of 0, 1 or 2 floats (a tangent ray gives one).
    Same quadratic as point_on_ray_at_distance in
    v3/replay/bone_projection.py:43-60 (read, not imported): with
    b = d . c the roots are t = b -/+ sqrt(b^2 - |c|^2 + r^2); here both
    positive roots are returned instead of the one nearest a prior.
    """
    d = np.asarray(d, float)
    c = np.asarray(center, float)
    b = float(np.dot(d, c))
    disc = b * b - float(np.dot(c, c)) + float(radius) ** 2
    if disc < 0.0:
        return []
    if disc == 0.0:
        roots = [b]
    else:
        r = float(np.sqrt(disc))
        roots = [b - r, b + r]
    return sorted(t for t in roots if t > 0.0)


# --------------------------------------------------------------------------
# Occlusion filter (Stage 3 input gate)
# --------------------------------------------------------------------------

@dataclass
class Obs:
    """One landmark observation: xyz (3,) or None, uv (2,) or None."""
    xyz: object = None
    uv: object = None
    vis: float = 0.0


def _arr(a, n):
    if a is None:
        return None
    a = np.asarray(a, float).reshape(n)
    return a if np.all(np.isfinite(a)) else None


def occlusion_filter(lms, side, K=INTRINSICS):
    """Paper Section II-C gate on one arm.

    lms: dict name -> (xyz | None, uv | None, vis) with names from
    "shoulder", "elbow", "wrist", "other_shoulder". side ("left" or
    "right") only labels the arm. Returns dict name -> Obs.

    - vis < VIS_MIN (or NaN) drops xyz and uv (AKC-003, AKC-006).
    - Missing uv with a given xyz is filled by projection (AKC-005).
    - The elbow or shoulder of this arm whose pixel lies closer than
      PROX_FRAC * width to the wrist pixel loses xyz, keeps uv
      (AKC-004, AKC-005). The rule needs a wrist pixel that passed the
      gate; other_shoulder is never tested.
    """
    if side not in ("left", "right"):
        raise ValueError(f"side must be left or right, got {side!r}")
    out = {}
    for name, item in lms.items():
        xyz, uv, vis = item
        xyz = _arr(xyz, 3)
        uv = _arr(uv, 2)
        vis = float(vis) if vis is not None else float("nan")
        if not vis >= VIS_MIN:
            xyz, uv = None, None
        if uv is None and xyz is not None:
            uv = project(xyz, K)
        out[name] = Obs(xyz=xyz, uv=uv, vis=vis)
    w = out.get("wrist")
    if w is not None and w.uv is not None:
        radius = PROX_FRAC * K["width"]
        for name in ("elbow", "shoulder"):
            o = out.get(name)
            if o is None or o.uv is None or o.xyz is None:
                continue
            if float(np.linalg.norm(o.uv - w.uv)) < radius:
                out[name] = Obs(xyz=None, uv=o.uv, vis=o.vis)
    return out


# --------------------------------------------------------------------------
# Stage 3: constant-velocity Kalman filter (paper Eq. 1-6)
# --------------------------------------------------------------------------

class CVKalman:
    """Constant-velocity Kalman filter on one landmark, state [p, pdot]."""

    def __init__(self, dt, sigma_a, sigma_xy, sigma_z, v0_sigma=1.0):
        self.dt = float(dt)
        self.sigma_a = float(sigma_a)
        self.sigma_xy = float(sigma_xy)
        self.sigma_z = float(sigma_z)
        self.v0_sigma = float(v0_sigma)
        I3 = np.eye(3)
        self.A = np.block([[I3, self.dt * I3], [np.zeros((3, 3)), I3]])
        g = np.array([0.5 * self.dt ** 2, self.dt])
        q = self.sigma_a ** 2 * np.outer(g, g)
        self.Q = np.block([[q[0, 0] * I3, q[0, 1] * I3],
                           [q[1, 0] * I3, q[1, 1] * I3]])
        self.R = np.diag([self.sigma_xy ** 2, self.sigma_xy ** 2,
                          self.sigma_z ** 2])
        self.H = np.hstack([I3, np.zeros((3, 3))])
        self.x = None
        self.P = None
        self.last_K = None
        self.last_source = None

    @property
    def initialised(self):
        return self.x is not None

    @property
    def p(self):
        return None if self.x is None else self.x[:3].copy()

    def init(self, xyz):
        self.x = np.concatenate([np.asarray(xyz, float), np.zeros(3)])
        self.P = np.diag([self.sigma_xy ** 2, self.sigma_xy ** 2,
                          self.sigma_z ** 2] + [self.v0_sigma ** 2] * 3)

    def predict(self):
        self.x = self.A @ self.x
        self.P = self.A @ self.P @ self.A.T + self.Q
        return self.x[:3].copy(), self.P.copy()

    def _update(self, z, H, R):
        y = z - H @ self.x
        S = H @ self.P @ H.T + R
        Kg = np.linalg.solve(S, H @ self.P).T      # P H^T S^-1 (S symmetric)
        self.x = self.x + Kg @ y
        self.P = (np.eye(6) - Kg @ H) @ self.P
        self.P = 0.5 * (self.P + self.P.T)
        self.last_K = Kg
        return self.x[:3].copy()

    def update_xyz(self, xyz):
        return self._update(np.asarray(xyz, float), self.H, self.R)

    def update_xy(self, xy):
        """Partial update on x, y only; z is left to the prediction."""
        return self._update(np.asarray(xy, float)[:2], self.H[:2],
                            self.R[:2, :2])

    def step(self, obs, K=INTRINSICS):
        """One frame. Returns the estimate p_hat, or None before the first
        full xyz observation."""
        if self.x is None:
            if obs is not None and obs.xyz is not None:
                self.init(obs.xyz)
                self.last_source = "measured"
                return self.p
            self.last_source = None
            return None
        p_pred, _ = self.predict()
        if obs is not None and obs.xyz is not None:
            self.last_source = "measured"
            return self.update_xyz(obs.xyz)
        if obs is not None and obs.uv is not None:
            xy = deproject(obs.uv[0], obs.uv[1], p_pred[2], K)[:2]
            self.last_source = "partial"
            return self.update_xy(xy)
        self.last_source = "kf_pred"
        return p_pred

    def constrain_length(self, anchor_xyz, length, sigma_l):
        """EKF soft constraint |p - anchor| = length, paper Eq. (4)-(6)."""
        if self.x is None:
            return None
        diff = self.x[:3] - np.asarray(anchor_xyz, float)
        h = float(np.linalg.norm(diff))
        if h <= 1e-12:
            return self.p
        Hc = np.concatenate([diff / h, np.zeros(3)])[None, :]
        S = float((Hc @ self.P @ Hc.T)[0, 0]) + float(sigma_l) ** 2
        if not S > 0.0:
            return self.p
        Kc = (self.P @ Hc.T) / S
        self.x = self.x + Kc[:, 0] * (float(length) - h)
        self.P = (np.eye(6) - Kc @ Hc) @ self.P
        self.P = 0.5 * (self.P + self.P.T)
        return self.p


# --------------------------------------------------------------------------
# Stage 4: AKC candidates and cost (paper Eq. 7-15)
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class AkcWeights:
    w1: float
    w2: float
    w3: float
    s: float
    w4: float = 100.0
    w5: float = 100.0
    k: float = 100.0
    theta_deg: tuple = (40.0, 180.0)


W_A = AkcWeights(w1=0.0, w2=8.0, w3=18.0, s=1.0)
W_B = AkcWeights(w1=0.0, w2=14.0, w3=12.0, s=0.8)
W_C = AkcWeights(w1=1.0, w2=19.0, w3=20.0, s=0.9)


def _unit(v):
    n = float(np.linalg.norm(v))
    if n <= 0.0:
        raise ValueError("zero-length direction in the AKC fallback")
    return v / n


def _candidates(anchor, ref, uv, length, s, mode, K):
    anchor = np.asarray(anchor, float)
    ref = np.asarray(ref, float)
    lp = float(s) * float(length)
    if mode == "literal":
        r = ref.copy()
        if uv is not None:
            r = deproject(uv[0], uv[1], ref[2], K)
        rad = lp * lp - (r[0] - anchor[0]) ** 2 - (r[1] - anchor[1]) ** 2
        if rad >= 0.0:
            q = float(np.sqrt(rad))
            return [(np.array([r[0], r[1], anchor[2] - q]), True),
                    (np.array([r[0], r[1], anchor[2] + q]), True)]
        dir_ref = r
    elif mode == "ray":
        d = ray(uv[0], uv[1], K) if uv is not None else _unit(ref)
        roots = ray_sphere_roots(d, anchor, lp)
        if roots:
            return [(t * d, True) for t in roots]
        dir_ref = ref
    else:
        raise ValueError(f"mode must be 'literal' or 'ray', got {mode!r}")
    # Paper Eq. (9): unscaled length along the reference direction.
    return [(anchor + _unit(dir_ref - anchor) * float(length), False)]


def elbow_candidates(p_w, ref_e, uv_e, l_f, s, mode, K=INTRINSICS):
    """Elbow candidates about the wrist, paper Eq. (7) and (9)."""
    return _candidates(p_w, ref_e, uv_e, l_f, s, mode, K)


def shoulder_candidates(p_e, ref_s, uv_s, l_u, s, mode, K=INTRINSICS):
    """Shoulder candidates about one elbow candidate, Eq. (8) and (9)."""
    return _candidates(p_e, ref_s, uv_s, l_u, s, mode, K)


def elbow_angle_deg(p_e, p_s, p_w):
    """Unsigned angle at the elbow between (s - e) and (w - e), degrees."""
    a = np.asarray(p_s, float) - np.asarray(p_e, float)
    b = np.asarray(p_w, float) - np.asarray(p_e, float)
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na <= 0.0 or nb <= 0.0:
        return float("nan")
    c = float(np.clip(np.dot(a, b) / (na * nb), -1.0, 1.0))
    return float(np.degrees(np.arccos(c)))


def cost(p_e, p_s, ref_e, ref_s, prev_e, prev_s, other_s, p_w, l_s, w):
    """Weighted cost of one configuration, paper Eq. (10)-(15).

    Returns (c, dict m1..m5, theta). m3 = 0 when prev is None (AKC-026);
    m4 = 0 when other_s is None (AKC-027); a NaN theta (degenerate
    geometry) counts as outside the range.
    """
    p_e = np.asarray(p_e, float)
    p_s = np.asarray(p_s, float)
    m1 = float(np.linalg.norm(p_e - np.asarray(ref_e, float)))
    m2 = float(np.linalg.norm(p_s - np.asarray(ref_s, float)))
    if prev_e is None or prev_s is None:
        m3 = 0.0
    else:
        m3 = float(np.linalg.norm(p_e - np.asarray(prev_e, float))
                   + np.linalg.norm(p_s - np.asarray(prev_s, float)))
    if other_s is None:
        m4 = 0.0
    else:
        m4 = abs(float(l_s) - float(np.linalg.norm(
            p_s - np.asarray(other_s, float))))
    theta = elbow_angle_deg(p_e, p_s, p_w)
    lo, hi = w.theta_deg
    m5 = 0.0 if (lo <= theta <= hi) else float(w.k)
    c = w.w1 * m1 + w.w2 * m2 + w.w3 * m3 + w.w4 * m4 + w.w5 * m5
    return float(c), dict(m1=m1, m2=m2, m3=m3, m4=m4, m5=m5,
                          theta=theta)


def _branch_at_length(anchor, ref, uv, length, mode, j, n, K):
    """Root j of the paper's relation (Eq. 7 / 8, or the ray roots) at the
    unscaled `length`; None when the solve has no root, falls back, or
    gives a root count other than the search-time count n."""
    cs = _candidates(anchor, ref, uv, length, 1.0, mode, K)
    if len(cs) != n or not all(f for _, f in cs):
        return None
    return cs[j][0]


def full_length_chain(p_w, best, ref_e, ref_s, uv_e, uv_s, lengths, w,
                      mode, K=INTRINSICS):
    """Output the chosen branch at the unscaled lengths (AKC-053).

    Order: elbow first, then shoulder about the output elbow, so the
    returned chain satisfies |p_e - p_w| = l_f and |p_s - p_e| = l_u.
    Each joint is solved with the paper's own relation at the unscaled
    length on the branch the search chose (root index j of the same
    enumeration: literal = same x, y and the chosen sign of the square
    root; ray = same pixel ray, same root order). A branch feasible at
    l' = s l is feasible at l about the same anchor (the radicand only
    grows), which covers the elbow; the shoulder anchor moves from the
    search-time elbow to the output elbow, which in literal mode keeps
    x, y and hence dx, dy, and in ray mode can in principle change the
    root count.
    Radial rescale fallback, counted in the returned flags: when the
    full-length solve of a branch that was feasible at search time has
    no root or a different root count, the joint is placed at
    anchor + unit(cand - anchor) l, with cand the search-time candidate
    rebuilt about the output anchor at l' (index j when the rebuilt set
    has the search-time count, else the candidate nearest the search-time
    point, AKC-055). A joint that already fell back at search time
    (Eq. 9) takes the same radial path, which for the elbow returns the
    Eq. 9 point; it is not counted.
    Returns (p_e, p_s, rescaled_e, rescaled_s).
    """
    p_w = np.asarray(p_w, float)
    l_f, l_u = lengths["l_f"], lengths["l_u"]

    def radial(anchor, ref, uv, length, j, n, point):
        cs = _candidates(anchor, ref, uv, length, w.s, mode, K)
        if len(cs) == n:
            cand = cs[j][0]
        else:
            point = np.asarray(point, float)
            cand = min(cs, key=lambda c: float(np.linalg.norm(c[0]
                                                              - point)))[0]
        return anchor + _unit(cand - anchor) * length

    p_e = None
    if best["feasible_e"]:
        p_e = _branch_at_length(p_w, ref_e, uv_e, l_f, mode, best["j_e"],
                                best["n_e"], K)
    resc_e = bool(best["feasible_e"] and p_e is None)
    if p_e is None:
        p_e = radial(p_w, ref_e, uv_e, l_f, best["j_e"], best["n_e"],
                     best["e"])
    p_s = None
    if best["feasible_s"]:
        p_s = _branch_at_length(p_e, ref_s, uv_s, l_u, mode, best["j"],
                                best["n_s"], K)
    resc_s = bool(best["feasible_s"] and p_s is None)
    if p_s is None:
        p_s = radial(p_e, ref_s, uv_s, l_u, best["j"], best["n_s"],
                     best["s"])
    return p_e, p_s, resc_e, resc_s


def akc_correct(p_w, ref_e, ref_s, uv_e, uv_s, prev_e, prev_s, other_s,
                lengths, w, mode, K=INTRINSICS, output_shrunk=False):
    """Candidate search and argmin over elbow x shoulder (up to 2 x 2).

    The search and the cost use the candidates at l' = s l (paper
    Section II-D2: cost on the candidates). The chosen branch is then
    output at the unscaled lengths (full_length_chain, AKC-053) unless
    output_shrunk, which returns the search-time points (the M2
    behaviour, AKC-051).

    Returns dict e, s (output), e_search, s_search (argmin points at
    l'), feasible_e, feasible_s (search-time), rescaled_e, rescaled_s
    (radial rescale fallback used, full_length_chain), n_candidates, c,
    terms.
    Ties keep the first configuration in enumeration order (elbow root
    ascending, then shoulder root ascending; AKC-029).
    """
    best = None
    n = 0
    ce = elbow_candidates(p_w, ref_e, uv_e, lengths["l_f"], w.s, mode, K)
    for j_e, (e, fe) in enumerate(ce):
        cs = shoulder_candidates(e, ref_s, uv_s, lengths["l_u"], w.s, mode,
                                 K)
        for j, (s_, fs) in enumerate(cs):
            n += 1
            c, terms = cost(e, s_, ref_e, ref_s, prev_e, prev_s, other_s,
                            p_w, lengths["l_s"], w)
            if best is None or c < best["c"]:
                best = dict(e=e, s=s_, feasible_e=fe, feasible_s=fs, c=c,
                            terms=terms, j=j, n_s=len(cs), j_e=j_e,
                            n_e=len(ce))
    best["n_candidates"] = n
    best["e_search"], best["s_search"] = best["e"], best["s"]
    best["rescaled_e"] = best["rescaled_s"] = False
    if not output_shrunk:
        (best["e"], best["s"], best["rescaled_e"],
         best["rescaled_s"]) = full_length_chain(
            p_w, best, ref_e, ref_s, uv_e, uv_s, lengths, w, mode, K)
    return best


# --------------------------------------------------------------------------
# Per-arm pipeline
# --------------------------------------------------------------------------

@dataclass
class AkcOut:
    e: object = None
    s: object = None
    w: object = None
    src: dict = field(default_factory=dict)
    n_candidates: int = 0
    terms: dict = field(default_factory=dict)
    cost: float = float("nan")
    feasible: bool = True
    corrected: bool = False
    ref_e: object = None      # Stage 3 (KF or EKF) elbow estimate
    ref_s: object = None      # Stage 3 shoulder estimate
    ref_w: object = None      # Stage 3 wrist estimate
    e_search: object = None   # argmin elbow at l' = s l (AKC-053)
    s_search: object = None   # argmin shoulder at l' = s l
    rescaled_e: bool = False  # radial rescale fallback (AKC-053)
    rescaled_s: bool = False


class AkcArm:
    """Stage 3 + Stage 4 for one arm, causal, one call per frame."""

    def __init__(self, side, lengths, weights=W_C, kf=None, mode="ray",
                 always_correct=True, feedback=False, ekf=False,
                 sigma_l=DEFAULT_SIGMA_L, K=INTRINSICS,
                 output_shrunk=False, ekf_anchor="filtered"):
        """output_shrunk=True outputs the search-time points at s l (the
        M2 behaviour, AKC-051); the default outputs the chosen branch at
        the unscaled lengths (AKC-053).

        ekf_anchor (ekf=True only): "filtered" (default, AKC-056) anchors
        the elbow length constraint on the Stage-3 Kalman wrist estimate,
        the paper's h(x) = |p_i - p_j| between filtered landmarks; "raw"
        anchors it on the Stage-4 wrist p_w (the measured wrist when
        present, AKC-021), the M2 behaviour. The shoulder constraint is
        anchored on the constrained elbow in both settings."""
        if side not in ("left", "right"):
            raise ValueError(f"side must be left or right, got {side!r}")
        if mode not in ("literal", "ray"):
            raise ValueError(f"mode must be 'literal' or 'ray', got {mode!r}")
        if ekf_anchor not in ("filtered", "raw"):
            raise ValueError("ekf_anchor must be 'filtered' or 'raw', got "
                             f"{ekf_anchor!r}")
        for key in ("l_f", "l_u", "l_s"):
            if key not in lengths or lengths[key] is None:
                raise ValueError(f"lengths[{key!r}] missing")
        self.side = side
        self.lengths = {k: float(v) for k, v in lengths.items()}
        self.w = weights
        self.kf_cfg = dict(DEFAULT_KF if kf is None else kf)
        self.mode = mode
        self.always_correct = bool(always_correct)
        self.feedback = bool(feedback)
        self.ekf = bool(ekf)
        self.sigma_l = float(sigma_l)
        self.K = K
        self.output_shrunk = bool(output_shrunk)
        self.ekf_anchor = ekf_anchor
        self.kf = {j: CVKalman(**self.kf_cfg) for j in ARM_JOINTS}
        self.kf_other = CVKalman(**self.kf_cfg)
        self.prev_e = None
        self.prev_s = None

    def step(self, obs, wrist_override=None, other_shoulder=None):
        """obs: dict name -> Obs (already occlusion-filtered).

        other_shoulder: an Obs (filtered by this arm's own KF) or an
        (3,) xyz used as is; when None, obs.get("other_shoulder") is used
        (AKC-027).
        """
        K = self.K
        get = obs.get
        ref = {j: self.kf[j].step(get(j), K) for j in ARM_JOINTS}
        other = other_shoulder if other_shoulder is not None \
            else get("other_shoulder")
        if isinstance(other, Obs) or other is None:
            other_ref = self.kf_other.step(other, K)
        else:
            other_ref = _arr(other, 3)

        ow = get("wrist")
        src = {}
        if ow is not None and ow.xyz is not None:
            p_w, src["wrist"] = np.asarray(ow.xyz, float), "measured"
        elif wrist_override is not None and _arr(wrist_override, 3) \
                is not None:
            p_w, src["wrist"] = _arr(wrist_override, 3), "override"
        elif ref["wrist"] is not None:
            p_w, src["wrist"] = ref["wrist"], "kf_pred"
        else:
            p_w, src["wrist"] = None, "none"

        # EKF soft length constraints, paper Eq. (4)-(6). The elbow is
        # tied to the Stage-3 (Kalman) wrist, falling back to p_w only
        # while the wrist filter is uninitialised (AKC-056); "raw" ties it
        # to p_w (AKC-016, AKC-021). The shoulder is tied to the
        # constrained elbow.
        anchor_w = p_w
        if self.ekf_anchor == "filtered" and ref["wrist"] is not None:
            anchor_w = ref["wrist"]
        if self.ekf and anchor_w is not None and ref["elbow"] is not None:
            ref["elbow"] = self.kf["elbow"].constrain_length(
                anchor_w, self.lengths["l_f"], self.sigma_l)
            if ref["shoulder"] is not None:
                ref["shoulder"] = self.kf["shoulder"].constrain_length(
                    ref["elbow"], self.lengths["l_u"], self.sigma_l)

        out = AkcOut(w=p_w, ref_e=ref["elbow"], ref_s=ref["shoulder"],
                     ref_w=ref["wrist"])
        oe, os_ = get("elbow"), get("shoulder")
        fully = (oe is not None and oe.xyz is not None
                 and os_ is not None and os_.xyz is not None)

        def kf_src(j):
            s = self.kf[j].last_source
            return "none" if s is None else ("kf_pred" if s == "partial"
                                             else s)

        can = (p_w is not None and ref["elbow"] is not None
               and ref["shoulder"] is not None)
        if can and (self.always_correct or not fully):
            r = akc_correct(p_w, ref["elbow"], ref["shoulder"],
                            None if oe is None else oe.uv,
                            None if os_ is None else os_.uv,
                            self.prev_e, self.prev_s, other_ref,
                            self.lengths, self.w, self.mode, K,
                            output_shrunk=self.output_shrunk)
            out.e, out.s = r["e"], r["s"]
            out.e_search, out.s_search = r["e_search"], r["s_search"]
            out.rescaled_e, out.rescaled_s = r["rescaled_e"], r["rescaled_s"]
            src["elbow"] = "akc" if r["feasible_e"] else "fallback"
            src["shoulder"] = "akc" if r["feasible_s"] else "fallback"
            out.n_candidates = r["n_candidates"]
            out.terms = r["terms"]
            out.cost = r["c"]
            out.feasible = bool(r["feasible_e"] and r["feasible_s"])
            out.corrected = True
            if self.feedback:
                self.kf["elbow"].update_xyz(out.e)
                self.kf["shoulder"].update_xyz(out.s)
        else:
            out.e, out.s = ref["elbow"], ref["shoulder"]
            src["elbow"] = kf_src("elbow")
            src["shoulder"] = kf_src("shoulder")
        out.src = src
        # m3 compares search-time candidates with the previous search-time
        # choice, so the search is the same as with output_shrunk (AKC-054);
        # frames without a correction carry the Kalman estimate as before.
        pe = out.e if out.e_search is None else out.e_search
        ps = out.s if out.s_search is None else out.s_search
        if pe is not None:
            self.prev_e = np.asarray(pe, float).copy()
        if ps is not None:
            self.prev_s = np.asarray(ps, float).copy()
        return out


# --------------------------------------------------------------------------
# Metrics
# --------------------------------------------------------------------------

def arm_length_stats(e, s, w):
    """Forearm |e - w| and upper-arm |s - e| statistics (metres) over the
    rows where all three joints are finite (paper Table VI mirror)."""
    e, s, w = (np.asarray(a, float).reshape(-1, 3) for a in (e, s, w))
    ok = np.all(np.isfinite(e), 1) & np.all(np.isfinite(s), 1) \
        & np.all(np.isfinite(w), 1)
    out = {"n": int(ok.sum())}
    for name, a, b in (("forearm", e, w), ("upper", s, e)):
        if ok.any():
            L = np.linalg.norm(a[ok] - b[ok], axis=1)
            out.update({f"{name}_min": float(L.min()),
                        f"{name}_max": float(L.max()),
                        f"{name}_range": float(L.max() - L.min()),
                        f"{name}_std": float(L.std())})
        else:
            for k in ("min", "max", "range", "std"):
                out[f"{name}_{k}"] = float("nan")
    return out
