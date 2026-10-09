"""Detection scheduling: pose-box reuse with periodic + triggered
re-detects (V3_PLAN.md Phase 1).

Pure numpy, no onnxruntime: the tracker only decides WHEN the person
detector must run and maintains the crop box between detections from
the previous frame's keypoints. All thresholds come from the config
detect block; nothing is hardcoded here.

Per-frame protocol (RTMPoseDetector drives this):

    reasons = tracker.needs_detect()
    if reasons: tracker.note_detection(run_detector())   # may be None
    box = tracker.box                                    # None = no person
    kp, sc = pose(box) if box else none
    tracker.note_pose(kp, sc)                            # prepares next frame
"""
import numpy as np


def box_from_keypoints(kp_px, scores, min_score, margin, img_wh):
    """Crop box for the NEXT frame from this frame's keypoints.

    kp_px: (K, 2) pixel keypoints; scores: (K,); points with score <
    min_score are excluded. Needs at least 2 confident points, else
    None. The tight box is expanded by `margin` x its larger side on
    every edge, then clamped to the image. Returns [x0, y0, x1, y1]
    floats or None.
    """
    kp_px = np.asarray(kp_px, dtype=float)
    scores = np.asarray(scores, dtype=float)
    sel = kp_px[scores >= min_score]
    if sel.shape[0] < 2:
        return None
    x0, y0 = sel.min(axis=0)
    x1, y1 = sel.max(axis=0)
    pad = margin * max(x1 - x0, y1 - y0)
    w, h = img_wh
    return [max(0.0, x0 - pad), max(0.0, y0 - pad),
            min(float(w), x1 + pad), min(float(h), y1 + pad)]


def _area(box):
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


class BoxTracker:
    """Decides detect-vs-track each frame and carries the crop box.

    Re-detect triggers (reasons reported for diagnostics):
      no_box     no current box (start of stream, or person was lost)
      scheduled  det_freq frames elapsed since the last detection
      low_score  mean keypoint score (over key_indices) below
                 reacquire_score for reacquire_frames consecutive frames
      area_jump  pose-box area changed by more than box_area_jump x
                 between consecutive frames
      border     pose box NEWLY touched an image border edge (person
                 moving out of frame or crop starting to clip). Rising
                 edge only: steady contact does not refire -- measured
                 on the pinned recording the head sits at the top edge
                 for the whole session, and level-triggered border
                 contact degenerated to detect-every-frame (D-012).
    """

    def __init__(self, img_wh, det_freq=15, margin=0.25,
                 kpt_min_score=0.3, reacquire_score=0.35,
                 reacquire_frames=2, box_area_jump=2.0,
                 key_indices=None, border_eps_px=2.0):
        self.img_wh = (float(img_wh[0]), float(img_wh[1]))
        self.det_freq = int(det_freq)
        self.margin = float(margin)
        self.kpt_min_score = float(kpt_min_score)
        self.reacquire_score = float(reacquire_score)
        self.reacquire_frames = int(reacquire_frames)
        self.box_area_jump = float(box_area_jump)
        self.key_indices = (None if key_indices is None
                            else np.asarray(key_indices, dtype=int))
        self.border_eps_px = float(border_eps_px)
        self.reset()

    def reset(self):
        self.box = None
        self._since_det = 0
        self._low_streak = 0
        self._prev_area = None
        self._border = False
        self._area_jumped = False
        self._touched_edges = set()

    def needs_detect(self):
        """Reasons the detector must run this frame; empty = track."""
        reasons = []
        if self.box is None:
            reasons.append("no_box")
        if self._since_det >= self.det_freq:
            reasons.append("scheduled")
        if self._low_streak >= self.reacquire_frames:
            reasons.append("low_score")
        if self._area_jumped:
            reasons.append("area_jump")
        if self._border:
            reasons.append("border")
        return reasons

    def note_detection(self, box):
        """Record a detector result (box or None = no person found).

        The detector box is a fresh anchor: triggers clear, and the
        area baseline resets to None so the next pose box is not
        compared against the detector's loose box (their areas differ
        by construction; comparing them refired area_jump after every
        detection, D-012)."""
        self.box = list(box) if box is not None else None
        self._since_det = 0
        self._low_streak = 0
        self._prev_area = None
        self._border = False
        self._area_jumped = False

    def note_pose(self, kp_px, scores):
        """Record this frame's pose result; prepares the next frame's
        crop box and triggers. Call with None, None when no pose ran
        (no box this frame)."""
        self._since_det += 1
        if kp_px is None:
            self.box = None
            return
        scores = np.asarray(scores, dtype=float)
        key = (scores if self.key_indices is None
               else scores[self.key_indices])
        if float(key.mean()) < self.reacquire_score:
            self._low_streak += 1
        else:
            self._low_streak = 0

        box = box_from_keypoints(kp_px, scores, self.kpt_min_score,
                                 self.margin, self.img_wh)
        if box is None:
            self.box = None
            return
        area = _area(box)
        if self._prev_area is not None and self._prev_area > 0:
            ratio = area / self._prev_area
            self._area_jumped = (ratio > self.box_area_jump
                                 or ratio < 1.0 / self.box_area_jump)
        self._prev_area = area
        w, h = self.img_wh
        e = self.border_eps_px
        edges = set()
        if box[0] <= e:
            edges.add("left")
        if box[1] <= e:
            edges.add("top")
        if box[2] >= w - e:
            edges.add("right")
        if box[3] >= h - e:
            edges.add("bottom")
        self._border = bool(edges - self._touched_edges)  # rising edge
        self._touched_edges = edges
        self.box = box
