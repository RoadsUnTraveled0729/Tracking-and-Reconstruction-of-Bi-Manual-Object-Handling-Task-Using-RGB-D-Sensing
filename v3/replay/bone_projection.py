"""Bone-length-constrained depth lifting (D-030).

Stateful, causal, per recording. Arm chains per side: shoulder ->
elbow (upper arm), elbow -> wrist (forearm). Calibration: each bone's
length is the median over the first bones.calibrate_frames frames on
which both of its ends were lifted (finite camera-frame xyz).
Afterwards, when a lifted bone's length deviates from the calibrated
length by more than bones.tolerance (fraction), the DISTAL point is
moved along ITS OWN CAMERA RAY (origin -> lifted point, i.e. the
deprojection ray of its pixel) to the point at exactly the calibrated
length from the proximal point, choosing the intersection nearest the
lifted depth. The pixel therefore never moves; only its depth is
corrected, which is where the error lives (depth-median noise and
depth bleed at the limb silhouette). When the ray misses the sphere
(the pixel is too far from the proximal point for any depth), the
distal point goes to the ray point closest to the proximal point (the
feasible point nearest the constraint) and the case is counted.
The upper arm is corrected first and the forearm is then measured
from the corrected elbow.

Pure numpy (no pyrealsense2) so the CSV replay (replay/runner.py)
applies the identical projection to extraction CSV rows; realtime
applies it inside replay/depth_sampler.lift_keypoints. Coordinates:
camera frame, metres, BEFORE the Unity flip (the flip is a reflection
and preserves lengths, but the ray must be the camera ray).

Score gate: depth.min_score is present in the config and null (D-017:
no score gate until occlusion data exist); the projector does not read
scores.
"""
import numpy as np

CHAINS = (("right_shoulder", "right_elbow", "right_wrist"),
          ("left_shoulder", "left_elbow", "left_wrist"))
BONES = tuple((a, b) for sh, el, wr in CHAINS for a, b in ((sh, el),
                                                            (el, wr)))


def _finite(p):
    return p is not None and bool(np.all(np.isfinite(p)))


def point_on_ray_at_distance(p_dist, p_prox, length):
    """Point s * d on the ray d = p_dist / |p_dist| with |s d - p_prox|
    = length, the root nearest s0 = |p_dist|. Returns (point,
    feasible)."""
    p_dist = np.asarray(p_dist, float)
    p_prox = np.asarray(p_prox, float)
    s0 = float(np.linalg.norm(p_dist))
    d = p_dist / s0
    b = float(np.dot(d, p_prox))
    disc = b * b - float(np.dot(p_prox, p_prox)) + length * length
    if disc < 0.0:
        return b * d, False
    r = np.sqrt(disc)
    cands = [s for s in (b - r, b + r) if s > 0.0]
    if not cands:
        return b * d, False
    s = min(cands, key=lambda c: abs(c - s0))
    return s * d, True


class BoneLengthProjector:
    def __init__(self, calibrate_frames, tolerance):
        if calibrate_frames is None or tolerance is None:
            raise ValueError("bones.calibrate_frames / bones.tolerance "
                             "null (D-006)")
        self.n_cal = int(calibrate_frames)
        self.tol = float(tolerance)
        if self.n_cal < 1 or self.tol < 0:
            raise ValueError("bad bones config")
        self.reset()

    def reset(self):
        self.samples = {b: [] for b in BONES}
        self.length = {b: None for b in BONES}
        self.n_projected = {b: 0 for b in BONES}
        self.n_infeasible = {b: 0 for b in BONES}

    @property
    def calibrated(self):
        return all(v is not None for v in self.length.values())

    def __call__(self, points):
        """points: {name: (3,) camera-frame xyz or None}. Returns a new
        dict with corrected distal points (inputs are not modified)."""
        out = {k: (None if v is None else np.asarray(v, float))
               for k, v in points.items()}
        for chain in CHAINS:
            for a, b in ((chain[0], chain[1]), (chain[1], chain[2])):
                pa, pb = out.get(a), out.get(b)
                if not (_finite(pa) and _finite(pb)):
                    continue
                cur = float(np.linalg.norm(pb - pa))
                key = (a, b)
                if self.length[key] is None:
                    self.samples[key].append(cur)
                    if len(self.samples[key]) >= self.n_cal:
                        self.length[key] = float(np.median(self.samples[key]))
                    continue
                L = self.length[key]
                if abs(cur / L - 1.0) <= self.tol:
                    continue
                q, ok = point_on_ray_at_distance(pb, pa, L)
                out[b] = q
                self.n_projected[key] += 1
                self.n_infeasible[key] += (not ok)
        return out


def build_projector(cfg):
    """BoneLengthProjector from config bones, or None when
    bones.project is false."""
    bones = cfg.get("bones", {})
    if not bones.get("project", False):
        return None
    return BoneLengthProjector(bones.get("calibrate_frames"),
                               bones.get("tolerance"))
