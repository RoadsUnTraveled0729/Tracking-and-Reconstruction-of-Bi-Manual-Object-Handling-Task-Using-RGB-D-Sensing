"""Detector factory, pose backends and the named model-variant table
(D-023).

The detector call contract is unchanged for every backend:

    det = build_detector(cfg, repo_root, img_wh, device, key_indices)
    kp17, scores17, diag = det(frame_bgr)

kp17 is (17, 2) pixels in COCO order, scores17 is (17,), diag carries
det_ran, det_reasons, box and frame; kp17 and scores17 are None when no
person is available this frame.

config model.backend selects the pose backend:

  rtmpose  top-down rtmlib RTMPose on a 17-keypoint (body7 / COCO)
           model; YOLOX person box scheduled by BoxTracker.
  rtmw     top-down rtmlib RTMPose on a 133-keypoint COCO-WholeBody
           model (RTMW); the first 17 keypoints are the COCO body
           keypoints in COCO order and are the only ones returned.
  rtmo     bottom-up rtmlib RTMO on the whole frame (no person
           detector); the largest-area person is kept and the diag box
           is synthesised from its keypoint extent with the same
           box_from_keypoints rule BoxTracker uses between detections.

The rtmw and rtmo paths are exercised only with stub models in M1 (no
model on disk yet); see D-023.

configs/model_variants.json names concrete model combinations; each
entry pins its end2end.onnx files by sha256 and size. apply_variant()
overlays one entry onto the config's model block.
"""
import copy
import hashlib
import json
import os
from pathlib import Path

import numpy as np

V3_ROOT = Path(__file__).resolve().parents[1]
VARIANTS_PATH = V3_ROOT / "configs" / "model_variants.json"

BACKENDS = ("rtmpose", "rtmw", "rtmo")
# number of keypoints each backend's model must emit; the leading 17
# are COCO body keypoints in COCO order for all three (COCO-WholeBody
# keeps the COCO-17 body block first).
BACKEND_N_KPTS = {"rtmpose": 17, "rtmw": 133, "rtmo": 17}
N_BODY = 17
VARIANT_FIELDS = ("backend", "pose_onnx", "pose_input_size_wh",
                  "det_onnx", "det_input_size_wh")


# ---------------------------------------------------------------- backends

class TopDownPoseBackend:
    """Top-down pose on one person box.

    model: an rtmlib RTMPose-like callable model(img, [box]) ->
    (keypoints (1, K, 2), scores (1, K)). n_kpts: the K the model must
    emit (checked on every call, so a variant pointing at the wrong
    model fails loudly instead of returning shifted keypoints)."""

    needs_box = True

    def __init__(self, model, n_kpts=N_BODY):
        self.model = model
        self.n_kpts = int(n_kpts)

    @property
    def session(self):
        return self.model.session

    def __call__(self, img, box):
        kp, sc = self.model(img, [box])
        kp = np.asarray(kp)
        sc = np.asarray(sc)
        if kp.shape[1] != self.n_kpts or sc.shape[1] != self.n_kpts:
            raise ValueError(f"pose model emitted {kp.shape[1]} keypoints,"
                             f" backend expects {self.n_kpts}")
        return kp[0, :N_BODY], sc[0, :N_BODY]


class WholebodyBackend(TopDownPoseBackend):
    """RTMW: 133 COCO-WholeBody keypoints, sliced to the body 17."""

    def __init__(self, model):
        super().__init__(model, n_kpts=BACKEND_N_KPTS["rtmw"])


class RTMOBackend:
    """Bottom-up RTMO on the whole frame; ignores the box argument.

    model: an rtmlib RTMO-like callable model(img) -> (keypoints
    (N, 17, 2), scores (N, 17)); rtmlib returns one all-zero person
    when nothing passes its score threshold. min_score: the keypoint
    score below which a point does not count toward a person's extent
    (config detect.kpt_min_score, the same threshold BoxTracker uses).
    """

    needs_box = False

    def __init__(self, model, min_score):
        self.model = model
        self.n_kpts = BACKEND_N_KPTS["rtmo"]
        self.min_score = float(min_score)

    @property
    def session(self):
        return self.model.session

    def __call__(self, img, box=None):
        kp, sc = self.model(img)
        kp = np.asarray(kp, dtype=float).reshape(-1, self.n_kpts, 2)
        sc = np.asarray(sc, dtype=float).reshape(-1, self.n_kpts)
        best, best_area = None, 0.0
        for i in range(kp.shape[0]):
            sel = kp[i][sc[i] >= self.min_score]
            if sel.shape[0] < 2:
                continue
            ext = sel.max(axis=0) - sel.min(axis=0)
            area = float(ext[0] * ext[1])
            if best is None or area > best_area:
                best, best_area = i, area
        if best is None:
            return None, None
        return kp[best], sc[best]


def make_pose_backend(cfg, repo_root, device):
    """Load the rtmlib model for cfg model.backend (deferred import:
    needs onnxruntime)."""
    mo = cfg["model"]
    backend = mo.get("backend")
    if backend not in BACKENDS:
        raise ValueError(f"config model.backend = {backend!r}; expected "
                         f"one of {BACKENDS} (D-023)")
    for key in ("pose_onnx", "pose_input_size_wh"):
        if mo.get(key) is None:
            raise ValueError(f"config model.{key} is null; pin it before "
                             "building the detector (D-006)")
    pose_path = os.path.join(repo_root, mo["pose_onnx"])
    pw, ph = mo["pose_input_size_wh"]
    if backend == "rtmo":
        from rtmlib import RTMO
        # RTMO.preprocess indexes model_input_size as (h, w)
        model = RTMO(pose_path, model_input_size=(ph, pw), device=device)
        return RTMOBackend(model, cfg["detect"]["kpt_min_score"])
    from rtmlib import RTMPose
    # rtmlib RTMPose takes (w, h), as in rtmlib's own Body.MODE table
    model = RTMPose(pose_path, model_input_size=(pw, ph), device=device)
    if backend == "rtmw":
        return WholebodyBackend(model)
    return TopDownPoseBackend(model, n_kpts=BACKEND_N_KPTS["rtmpose"])


def make_person_detector(cfg, repo_root, device):
    """YOLOX person detector for the top-down backends."""
    from rtmlib.tools.object_detection import YOLOX
    mo = cfg["model"]
    for key in ("det_onnx", "det_input_size_wh"):
        if mo.get(key) is None:
            raise ValueError(f"config model.{key} is null; pin it before "
                             "building the detector (D-006)")
    dw, dh = mo["det_input_size_wh"]
    # YOLOX preprocess is (h, w)-indexed, as in rtmlib's Body.MODE table
    return YOLOX(os.path.join(repo_root, mo["det_onnx"]),
                 model_input_size=(dh, dw), device=device)


def build_detector(cfg, repo_root, img_wh, device="cuda",
                   key_indices=None):
    """The one entry point callers use; returns an RTMPoseDetector
    whose pose backend follows cfg model.backend."""
    from detector.rtmpose_detector import RTMPoseDetector
    return RTMPoseDetector(cfg, repo_root, img_wh, device=device,
                           key_indices=key_indices)


# ----------------------------------------------------------- variant table

def load_variants(path=VARIANTS_PATH):
    with open(path) as f:
        return json.load(f)["variants"]


def apply_variant(cfg, name, variants=None):
    """Deep copy of cfg with variant `name` overlaid on cfg['model']."""
    variants = load_variants() if variants is None else variants
    if name not in variants:
        raise KeyError(f"unknown model variant {name!r}; known: "
                       f"{sorted(variants)}")
    v = variants[name]
    out = copy.deepcopy(cfg)
    out["model"]["variant"] = name
    for key in VARIANT_FIELDS:
        out["model"][key] = v[key]
    return out


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def verify_variant_files(name, repo_root, variants=None):
    """Hash every onnx of variant `name` against the table; raises on
    a missing file or a mismatch. Returns {role: {path, sha256,
    size_bytes}} for provenance records."""
    variants = load_variants() if variants is None else variants
    v = variants[name]
    out = {}
    for role in ("pose", "det"):
        rel = v[f"{role}_onnx"]
        if rel is None:
            continue
        p = Path(repo_root) / rel
        if not p.exists():
            raise FileNotFoundError(f"variant {name}: {role} onnx missing:"
                                    f" {p}")
        digest = sha256_file(p)
        if digest != v[f"{role}_sha256"]:
            raise ValueError(f"variant {name}: {role} onnx sha256 "
                             f"{digest} != pinned {v[role + '_sha256']}")
        out[role] = {"path": rel, "sha256": digest,
                     "size_bytes": p.stat().st_size}
    return out
