#!/usr/bin/env python3
"""Select the "perfect frame" of the recordings bank for the journal worked example.

Milestone M2 of the journal track (journal/DECISIONS.md J-005, J-006).

Reads every .bag in recordings/ (sorted by name, legacy symlinks skipped),
runs MediaPipe PoseLandmarker (heavy model, VIDEO mode, the settings of the
frozen extractor v1/mediapipe/extract_landmarks_to_csv.py) on every
STRIDE-th colour frame, and scores each frame:

  vis_min8      min visibility over the 8 model landmarks (L11-L16, L23, L24)
  vis_min_face  min visibility over the face landmarks L0..L10
  margin_ok     the 8 model landmarks and L0 (nose) lie inside the image with
                at least MARGIN_FRAC of the width/height on each side
  depth_ok      single-pixel aligned depth > 0 at all 8 model landmarks
  sharpness     variance of cv2.Laplacian (CV_64F) of the grey colour image
  tpose         max over both arms of |v_shoulder - v_elbow| and
                |v_elbow - v_wrist| (pixels) divided by |u11 - u12| (pixels)

Gates: vis_min8 >= VIS_GATE, margin_ok, depth_ok. Ranking among gated frames:
vis_min8 descending, then sharpness descending. A refinement pass at stride 1
scores every frame in +-WINDOW frames around the top REFINE_TOP distinct
coarse windows and the best coarse T-pose window (tpose <= TPOSE_GATE). In
that pass MediaPipe runs on every frame from the start of the bag, so a
refined frame carries the landmarks the frozen extractor (stride 1) would
produce; the final picks come from the refined (fine) rows.

Outputs (all under journal/):
  data/perfect_frame_candidates.csv   every scored frame, both passes
  data/perfect_frame.json             overall pick, full record
  data/perfect_frame_tpose.json       T-pose pick, full record (if any)
  figures/perfect_frame_rgb.png       untouched colour frame of the overall pick
  figures/perfect_frame_tpose_rgb.png untouched colour frame of the T-pose pick
  figures/perfect_frame_overlay.png   8 landmarks and connections on the pick
  figures/candidates_contact.png      top CONTACT_TILES distinct windows

Run from the repository root:
  /home/luo/anaconda3/bin/python journal/scripts/select_perfect_frame.py
  (add --figures-only to redraw the overlay PNGs from the saved JSON and
  RGB files without reading the bags)

Second stage (J-010), run after the default run:
  /home/luo/anaconda3/bin/python journal/scripts/select_perfect_frame.py --depth-clean
reads data/perfect_frame_candidates.csv, plays each bag with gated rows once
and samples the aligned depth in a DC_WINDOW x DC_WINDOW window at each of
the 8 landmark pixels of every gated row (no MediaPipe: the pixels come from
the CSV). depth_clean8 = every window has valid fraction >= DC_VALID_FRAC
and std <= DC_STD_MAX_M. The best coarse-only clean candidates get a
stride-1 pass ('fine2', the default fine pass's procedure); the picks are
re-ranked over the fine and fine2 rows that pass the J-005 gates and
depth_clean8. Writes data/perfect_frame_candidates_depth.csv,
data/perfect_frame_candidates_fine2.csv, the three pick JSON and PNG files,
figures/perfect_frame_depth_check8.png and figures/candidates_contact.png.

v1/ is read for its settings only; nothing in it is imported or edited.
"""

import csv
import importlib.metadata
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pyrealsense2 as rs
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

sys.dont_write_bytecode = True

REPO = Path(__file__).resolve().parents[2]
BANK = REPO / "recordings"
JOURNAL = REPO / "journal"
DATA_DIR = JOURNAL / "data"
FIG_DIR = JOURNAL / "figures"

# Model file: the heavy variant the frozen extractor resolves by default
# (v1/mediapipe/extract_landmarks_to_csv.py: --model default "heavy",
# resolve_model -> script_dir/models/pose_landmarker_heavy.task).
MODEL_PATH = REPO / "v1" / "mediapipe" / "models" / "pose_landmarker_heavy.task"

# MediaPipe settings copied from extract_landmarks_to_csv.py lines 85-89.
MP_NUM_POSES = 1
MP_DET_CONF = 0.3
MP_PRES_CONF = 0.3
MP_TRACK_CONF = 0.3
# CPU delegate: the bank processing used CPU (presentation/defense_2026/
# bank_processing/README.md, "Processing and identity"); chosen here for
# run-to-run determinism (J-005).
MP_DELEGATE = mp_python.BaseOptions.Delegate.CPU

# Depth window of the frozen extractor (--depth-window default 5,
# extract_landmarks_to_csv.py line 190), used for the pipeline-style xyz.
DEPTH_WINDOW = 5

# Selection constants: every one is this brief's choice (J-005, UNCERTAIN).
STRIDE = 5            # coarse pass: every 5th colour frame
VIS_GATE = 0.9        # vis_min8 gate
MARGIN_FRAC = 0.03    # 3 % image margin on each side
TPOSE_GATE = 0.15     # tpose score threshold
WINDOW = 25           # refinement half-window, colour frames
REFINE_TOP = 3        # number of distinct overall windows refined
CONTACT_TILES = 12    # tiles in candidates_contact.png

# Depth-clean stage (--depth-clean, J-010, UNCERTAIN): constants of the
# depth-clean brief (2026-10-07). DC_STD_MAX_M sits between the clean-patch
# stds measured at R7_235402 frame 662 (2.2 mm body, 6.4 mm at L23) and the
# contaminated L24 (35.8 mm).
DC_WINDOW = 9         # depth window side, pixels, centred on (u_int, v_int)
DC_VALID_FRAC = 0.95  # min fraction of the DC_WINDOW^2 pixels with depth > 0
DC_STD_MAX_M = 0.008  # max population std of the valid depths, metres
DC_REFINE_TOP = 5     # coarse-only clean candidates given a stride-1 pass

MODEL_LMS = [11, 12, 13, 14, 15, 16, 23, 24]
FACE_LMS = list(range(0, 11))
N_LMS = 33
CONNECTIONS = [(11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
               (11, 23), (12, 24), (23, 24)]
LANDMARK_NAMES = {
    0: "nose", 11: "left_shoulder", 12: "right_shoulder",
    13: "left_elbow", 14: "right_elbow", 15: "left_wrist", 16: "right_wrist",
    23: "left_hip", 24: "right_hip",
}


# ---------------------------------------------------------------- reading

def list_bags():
    """All real .bag files in the bank, sorted by name; symlinks skipped
    (the 3 legacy symlinks point at bags already in the folder)."""
    return sorted(p for p in BANK.glob("*.bag") if p.is_file() and not p.is_symlink())


def make_landmarker():
    options = mp_vision.PoseLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(MODEL_PATH),
                                           delegate=MP_DELEGATE),
        running_mode=mp_vision.RunningMode.VIDEO,
        num_poses=MP_NUM_POSES,
        min_pose_detection_confidence=MP_DET_CONF,
        min_pose_presence_confidence=MP_PRES_CONF,
        min_tracking_confidence=MP_TRACK_CONF,
    )
    return mp_vision.PoseLandmarker.create_from_options(options)


def open_bag(bag_path):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(str(bag_path), repeat_playback=False)
    profile = pipeline.start(config)
    device = profile.get_device()
    device.as_playback().set_real_time(False)
    cprof = profile.get_stream(rs.stream.color).as_video_stream_profile()
    intr = cprof.get_intrinsics()
    depth_scale = device.first_depth_sensor().get_depth_scale()
    align = rs.align(rs.stream.color)
    return pipeline, align, intr, cprof.format(), depth_scale


def intrinsics_dict(intr, depth_scale):
    return {"fx": intr.fx, "fy": intr.fy, "ppx": intr.ppx, "ppy": intr.ppy,
            "width": intr.width, "height": intr.height,
            "model": str(intr.model), "coeffs": list(intr.coeffs),
            "depth_scale_m_per_unit": depth_scale}


def iterate_bag(bag_path, wanted):
    """Plays the bag once and yields (frame_index, frames, ctx) for every
    colour frame whose index satisfies wanted(index). frame_index counts the
    framesets that carry both a colour and a depth frame, as the frozen
    extractor's 'frame' column does. ctx carries intrinsics and timing."""
    pipeline, align, intr, cfmt, depth_scale = open_bag(bag_path)
    ctx = {"intr": intr, "cfmt": cfmt, "depth_scale": depth_scale,
           "align": align, "first_ts": None, "frames_seen": 0,
           "dup_color_numbers": 0}
    last_num = None
    idx = 0
    try:
        while True:
            try:
                frames = pipeline.wait_for_frames(timeout_ms=5000)
            except RuntimeError:
                break  # end of bag
            cf = frames.get_color_frame()
            df = frames.get_depth_frame()
            if not cf or not df:
                continue
            num = cf.get_frame_number()
            if num == last_num:
                ctx["dup_color_numbers"] += 1
            last_num = num
            if ctx["first_ts"] is None:
                ctx["first_ts"] = frames.get_timestamp()
            if wanted(idx):
                yield idx, frames, ctx
            idx += 1
            ctx["frames_seen"] = idx
    finally:
        pipeline.stop()


# ---------------------------------------------------------------- scoring

def sample_depth_window(depth_img, depth_scale, u, v, window):
    """Median of nonzero returns in a window x window patch (metres), the
    frozen extractor's sample_depth (lines 116-126)."""
    r = window // 2
    patch = depth_img[max(0, v - r):v + r + 1, max(0, u - r):u + r + 1]
    nz = patch[patch > 0]
    if nz.size == 0:
        return 0.0
    return float(np.median(nz)) * depth_scale


def process_frame(bag_name, idx, frames, ctx, landmarker, last_ts, pass_name):
    """Runs MediaPipe on one frameset. Returns (record or None, bgr image,
    new last_ts). record is None when no pose is detected."""
    intr = ctx["intr"]
    w, h = intr.width, intr.height
    aligned = ctx["align"].process(frames)
    cf = aligned.get_color_frame()
    df = aligned.get_depth_frame()
    color = np.asanyarray(cf.get_data()).copy()
    if ctx["cfmt"] == rs.format.rgb8:
        rgb = color
        bgr = cv2.cvtColor(color, cv2.COLOR_RGB2BGR)
    else:
        bgr = color
        rgb = cv2.cvtColor(color, cv2.COLOR_BGR2RGB)
    ts_ms = frames.get_timestamp()
    rel_s = (ts_ms - ctx["first_ts"]) / 1000.0
    mp_ts = max(int(rel_s * 1000), last_ts + 1)
    result = landmarker.detect_for_video(
        mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb)), mp_ts)
    if not result or not result.pose_landmarks:
        return None, bgr, mp_ts

    lms = result.pose_landmarks[0]
    depth_img = np.asanyarray(df.get_data())
    ds = ctx["depth_scale"]
    rec = {"bag": bag_name, "pass": pass_name, "frame_index": idx,
           "hw_frame_number": int(cf.get_frame_number()),
           "timestamp_ms": ts_ms, "time_s": rel_s,
           "intrinsics": intrinsics_dict(intr, ds), "landmarks": {}, "model": {}}
    for i in range(N_LMS):
        lm = lms[i]
        rec["landmarks"][i] = {
            "x": float(lm.x), "y": float(lm.y), "z": float(lm.z),
            "u": float(lm.x) * w, "v": float(lm.y) * h,
            "visibility": float(lm.visibility), "presence": float(lm.presence)}
    depth_ok = True
    for i in MODEL_LMS:
        lm = rec["landmarks"][i]
        # Integer pixel as the frozen extractor computes it (line 150).
        ui, vi = int(lm["x"] * w), int(lm["y"] * h)
        inside = 0 <= ui < w and 0 <= vi < h
        d_px = float(depth_img[vi, ui]) * ds if inside else 0.0
        d_w5 = sample_depth_window(depth_img, ds, ui, vi, DEPTH_WINDOW) if inside else 0.0
        xyz_px = (list(rs.rs2_deproject_pixel_to_point(intr, [ui, vi], d_px))
                  if d_px > 0 else None)
        xyz_w5 = (list(rs.rs2_deproject_pixel_to_point(intr, [ui, vi], d_w5))
                  if d_w5 > 0 else None)
        rec["model"][i] = {"u_int": ui, "v_int": vi,
                           "depth_px_m": d_px, "xyz_px_m": xyz_px,
                           "depth_med5_m": d_w5, "xyz_med5_m": xyz_w5}
        if d_px <= 0:
            depth_ok = False

    L = rec["landmarks"]
    vis_min8 = min(L[i]["visibility"] for i in MODEL_LMS)
    vis_min_face = min(L[i]["visibility"] for i in FACE_LMS)
    margin_ok = all(MARGIN_FRAC <= L[i]["x"] <= 1.0 - MARGIN_FRAC and
                    MARGIN_FRAC <= L[i]["y"] <= 1.0 - MARGIN_FRAC
                    for i in MODEL_LMS + [0])
    grey = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    sharpness = float(cv2.Laplacian(grey, cv2.CV_64F).var())
    sw = abs(L[11]["u"] - L[12]["u"])
    dv = max(abs(L[11]["v"] - L[13]["v"]), abs(L[13]["v"] - L[15]["v"]),
             abs(L[12]["v"] - L[14]["v"]), abs(L[14]["v"] - L[16]["v"]))
    tpose = dv / sw if sw > 0 else float("inf")
    gated = vis_min8 >= VIS_GATE and margin_ok and depth_ok
    # Informational, not gates (J-005): the brief's head test uses L0 only;
    # head_in asks all face landmarks L0..L10 to keep the same MARGIN_FRAC.
    face_top_y = min(L[i]["y"] for i in FACE_LMS)
    head_in = all(MARGIN_FRAC <= L[i]["x"] <= 1.0 - MARGIN_FRAC and
                  MARGIN_FRAC <= L[i]["y"] <= 1.0 - MARGIN_FRAC for i in FACE_LMS)
    # Mean hip depth minus mean shoulder depth (5x5 median, metres). Strongly
    # negative = the hip pixels see something in front of the body (desk,
    # rail, cube, hands), the case thesis Section 2.6 prepares hip depth for.
    M = rec["model"]
    dd = [M[i]["depth_med5_m"] for i in (11, 12, 23, 24)]
    hip_minus_shoulder = ((dd[2] + dd[3]) / 2 - (dd[0] + dd[1]) / 2) if min(dd) > 0 else float("nan")
    rec["scores"] = {"vis_min8": vis_min8, "vis_min_face": vis_min_face,
                     "margin_ok": margin_ok, "depth_ok": depth_ok,
                     "sharpness": sharpness, "tpose": tpose,
                     "shoulder_px_width": sw, "gated": gated,
                     "tpose_ok": gated and tpose <= TPOSE_GATE,
                     "face_top_y": face_top_y, "head_in": head_in,
                     "headin_ok": gated and head_in,
                     "hip_minus_shoulder_depth_m": hip_minus_shoulder}
    return rec, bgr, mp_ts


def rank_key(rec):
    """Sort key: vis_min8 desc, sharpness desc, then bag and frame for a
    deterministic tie break."""
    s = rec["scores"]
    return (-s["vis_min8"], -s["sharpness"], rec["bag"], rec["frame_index"])


def distinct_windows(recs, n):
    """Greedy pick of up to n records in rank order whose +-WINDOW windows do
    not overlap any already picked window in the same bag."""
    out = []
    for r in sorted(recs, key=rank_key):
        if all(r["bag"] != o["bag"] or abs(r["frame_index"] - o["frame_index"]) > 2 * WINDOW
               for o in out):
            out.append(r)
            if len(out) == n:
                break
    return out


# ---------------------------------------------------------------- outputs

def csv_header():
    head = ["pass", "bag", "frame_index", "hw_frame_number", "timestamp_ms", "time_s",
            "vis_min8", "vis_min_face", "margin_ok", "depth_ok", "sharpness",
            "tpose", "shoulder_px_width", "gated", "tpose_ok",
            "face_top_y", "head_in", "headin_ok", "hip_minus_shoulder_depth_m"]
    for i in range(N_LMS):
        head += [f"L{i}_{k}" for k in ("x", "y", "u", "v", "z", "vis", "pres")]
    for i in MODEL_LMS:
        head += [f"L{i}_u_int", f"L{i}_v_int", f"L{i}_depth_px_m",
                 f"L{i}_Xpx", f"L{i}_Ypx", f"L{i}_Zpx", f"L{i}_depth_med5_m",
                 f"L{i}_X", f"L{i}_Y", f"L{i}_Z"]
    return head


def csv_row(rec):
    s = rec["scores"]
    row = [rec["pass"], rec["bag"], rec["frame_index"], rec["hw_frame_number"],
           f"{rec['timestamp_ms']:.3f}", f"{rec['time_s']:.6f}",
           f"{s['vis_min8']:.6f}", f"{s['vis_min_face']:.6f}", int(s["margin_ok"]),
           int(s["depth_ok"]), f"{s['sharpness']:.3f}", f"{s['tpose']:.6f}",
           f"{s['shoulder_px_width']:.3f}", int(s["gated"]), int(s["tpose_ok"]),
           f"{s['face_top_y']:.6f}", int(s["head_in"]), int(s["headin_ok"]),
           f"{s['hip_minus_shoulder_depth_m']:.4f}"]
    for i in range(N_LMS):
        L = rec["landmarks"][i]
        row += [f"{L['x']:.6f}", f"{L['y']:.6f}", f"{L['u']:.3f}", f"{L['v']:.3f}",
                f"{L['z']:.6f}", f"{L['visibility']:.6f}", f"{L['presence']:.6f}"]
    for i in MODEL_LMS:
        m = rec["model"][i]
        xp = m["xyz_px_m"] or ["", "", ""]
        xw = m["xyz_med5_m"] or ["", "", ""]
        row += [m["u_int"], m["v_int"], f"{m['depth_px_m']:.6f}"]
        row += [f"{c:.6f}" if c != "" else "" for c in xp]
        row += [f"{m['depth_med5_m']:.6f}"]
        row += [f"{c:.6f}" if c != "" else "" for c in xw]
    return row


def json_record(rec, run_info):
    out = {
        "bag": rec["bag"], "pass": rec["pass"], "frame_index": rec["frame_index"],
        "frame_index_definition": ("0-based count of framesets with colour and depth, "
                                   "as the 'frame' column of v1/mediapipe/"
                                   "extract_landmarks_to_csv.py"),
        "hw_frame_number": rec["hw_frame_number"],
        "timestamp_ms": rec["timestamp_ms"], "time_s_from_bag_start": rec["time_s"],
        "intrinsics": rec["intrinsics"],
        "coordinate_frame": "camera (colour): X right, Y down, Z forward, metres",
        "landmarks": {
            str(i): dict(name=LANDMARK_NAMES.get(i, f"L{i}"), **rec["landmarks"][i])
            for i in range(N_LMS)},
        "landmarks_note": ("x, y normalised image coordinates; u = x*width, v = y*height "
                           "(pixels, float); z MediaPipe relative depth (not metres)"),
        "model_landmarks": {str(i): dict(name=LANDMARK_NAMES[i], **rec["model"][i])
                            for i in MODEL_LMS},
        "model_landmarks_note": (
            "u_int, v_int = int(x*width), int(y*height) as the frozen extractor; "
            "depth_px_m = aligned depth at that single pixel; xyz_px_m = "
            "rs2_deproject_pixel_to_point at (u_int, v_int) with depth_px_m; "
            "depth_med5_m and xyz_med5_m = the same with the 5x5 median of nonzero "
            "returns (the frozen extractor's --depth-window 5 default, the values "
            "the thesis pipeline uses)"),
        "scores": rec["scores"],
        "selection": run_info,
    }
    return out


def draw_overlay(bgr, rec):
    """8 model landmarks, their connections and Lnn labels on a copy of the
    frame. Labels go on the outer side of the body; a label that would
    overlap an earlier label or a landmark dot is moved to the next
    candidate position (below, then the inner side), so no two overlap."""
    img = bgr.copy()
    L = rec["landmarks"]
    pt = {i: (int(round(L[i]["u"])), int(round(L[i]["v"]))) for i in MODEL_LMS}
    for a, b in CONNECTIONS:
        cv2.line(img, pt[a], pt[b], (255, 255, 255), 3, cv2.LINE_AA)
        cv2.line(img, pt[a], pt[b], (0, 200, 255), 1, cv2.LINE_AA)
    for i in MODEL_LMS:
        cv2.circle(img, pt[i], 5, (0, 0, 0), -1, cv2.LINE_AA)
        cv2.circle(img, pt[i], 4, (0, 255, 0), -1, cv2.LINE_AA)
    cx = np.mean([pt[i][0] for i in MODEL_LMS])
    h, w = img.shape[:2]
    taken = [(x - 6, y - 6, x + 6, y + 6) for x, y in pt.values()]

    def overlaps(r):
        return any(r[0] < q[2] and q[0] < r[2] and r[1] < q[3] and q[1] < r[3] for q in taken)

    for i in MODEL_LMS:
        x, y = pt[i]
        label = f"L{i}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        outer = 1 if x >= cx else -1
        cands = []
        for side in (outer, -outer):
            tx = x + 8 if side > 0 else x - 8 - tw
            cands += [(tx, y - 8), (tx, y + 8 + th), (tx, y - 22), (tx, y + 22 + th)]
        rect = None
        for tx, ty in cands:
            tx = min(max(tx, 2), w - tw - 3)
            ty = min(max(ty, th + 4), h - 4)
            r = (tx - 2, ty - th - 3, tx + tw + 2, ty + 3)
            if not overlaps(r):
                rect = r
                break
        if rect is None:  # every candidate overlaps: keep the first one
            tx, ty = cands[0]
            rect = (tx - 2, ty - th - 3, tx + tw + 2, ty + 3)
        taken.append(rect)
        cv2.rectangle(img, rect[:2], rect[2:], (0, 0, 0), -1)
        cv2.putText(img, label, (rect[0] + 2, rect[3] - 3), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 1, cv2.LINE_AA)
    return img


def redraw_overlays():
    """--figures-only: redraw the overlay PNGs from the saved JSON records and
    the saved untouched RGB PNGs, without reading any bag."""
    pairs = [("perfect_frame", "perfect_frame"), ("perfect_frame_tpose", "perfect_frame_tpose"),
             ("perfect_frame_headin", "perfect_frame_headin")]
    for js, fig in pairs:
        jp, rp = DATA_DIR / f"{js}.json", FIG_DIR / f"{fig}_rgb.png"
        if not (jp.exists() and rp.exists()):
            continue
        d = json.load(open(jp))
        rec = {"landmarks": {int(k): v for k, v in d["landmarks"].items()}}
        cv2.imwrite(str(FIG_DIR / f"{fig}_overlay.png"), draw_overlay(cv2.imread(str(rp)), rec))
        print(f"[FIG] {fig}_overlay.png redrawn from {jp.name}")


def contact_sheet(tiles, cap=72):
    """tiles: list of (bgr, caption lines). 4 columns, tiles scaled to 320x240;
    cap = caption height in pixels (17 px per line)."""
    tw, th = 320, 240
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    sheet = np.full((rows * (th + cap), cols * tw, 3), 255, np.uint8)
    for k, (bgr, lines) in enumerate(tiles):
        r, c = divmod(k, cols)
        x0, y0 = c * tw, r * (th + cap)
        sheet[y0:y0 + th, x0:x0 + tw] = cv2.resize(bgr, (tw, th), interpolation=cv2.INTER_AREA)
        cv2.rectangle(sheet, (x0, y0), (x0 + tw - 1, y0 + th + cap - 1), (160, 160, 160), 1)
        for j, line in enumerate(lines):
            cv2.putText(sheet, line, (x0 + 4, y0 + th + 15 + 17 * j),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
    return sheet


def short_bag(name, n=40):
    """Bag stem shortened in the middle so the session prefix and the
    distinguishing suffix (capture stamp or old name) both stay visible."""
    stem = name[:-4] if name.endswith(".bag") else name
    if len(stem) <= n:
        return stem
    keep = (n - 3) // 2
    return stem[:keep] + "..." + stem[-(n - 3 - keep):]


# ---------------------------------------------------------------- main

def main():
    t_start = time.time()
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    if not MODEL_PATH.exists():
        sys.exit(f"[ERROR] model file missing: {MODEL_PATH}")
    bags = list_bags()
    print(f"[INFO] {len(bags)} bags in {BANK}; STRIDE={STRIDE} VIS_GATE={VIS_GATE} "
          f"MARGIN_FRAC={MARGIN_FRAC} TPOSE_GATE={TPOSE_GATE} WINDOW={WINDOW}", flush=True)

    coarse = []
    failed = []
    summary = []
    for bag in bags:
        t0 = time.time()
        recs = []
        n_proc = 0
        try:
            landmarker = make_landmarker()
            last_ts = -1
            ctx = None
            for idx, frames, ctx in iterate_bag(bag, lambda i: i % STRIDE == 0):
                n_proc += 1
                rec, _, last_ts = process_frame(bag.name, idx, frames, ctx,
                                                landmarker, last_ts, "coarse")
                if rec is not None:
                    recs.append(rec)
            landmarker.close()
        except Exception as e:  # a bag that fails to open is logged and skipped
            failed.append((bag.name, repr(e)))
            print(f"[ERROR] {bag.name}: {e!r}", flush=True)
            continue
        gated = [r for r in recs if r["scores"]["gated"]]
        best_vis = max((r["scores"]["vis_min8"] for r in recs), default=float("nan"))
        best_sharp = max((r["scores"]["sharpness"] for r in gated), default=float("nan"))
        seen = ctx["frames_seen"] if ctx else 0
        dups = ctx["dup_color_numbers"] if ctx else 0
        summary.append((bag.name, seen, n_proc, len(recs), len(gated), best_vis, best_sharp))
        print(f"[BAG] {bag.name}: seen {seen} (dup colour numbers {dups}), processed {n_proc}, "
              f"scored {len(recs)}, gated {len(gated)}, best vis_min8 {best_vis:.4f}, "
              f"best gated sharpness {best_sharp:.1f}, {time.time() - t0:.1f} s", flush=True)
        coarse.extend(recs)
    t_coarse = time.time() - t_start

    coarse_gated = [r for r in coarse if r["scores"]["gated"]]
    coarse_tpose = [r for r in coarse if r["scores"]["tpose_ok"]]
    if not coarse_gated:
        sys.exit("[ERROR] no frame passes the gates; nothing to select")
    top_windows = distinct_windows(coarse_gated, REFINE_TOP)
    # T-pose: the top REFINE_TOP distinct windows, not only the best one: the
    # best coarse T-pose window can lose its gate at stride 1 (J-005).
    tpose_windows = distinct_windows(coarse_tpose, REFINE_TOP)
    coarse_headin = [r for r in coarse if r["scores"]["headin_ok"]]
    headin_window = sorted(coarse_headin, key=rank_key)[0] if coarse_headin else None
    contact_windows = distinct_windows(coarse_gated, CONTACT_TILES)

    # Refinement segments per bag: union of +-WINDOW intervals.
    centres = [(r["bag"], r["frame_index"]) for r in top_windows]
    centres += [(r["bag"], r["frame_index"]) for r in tpose_windows]
    if headin_window is not None:
        centres.append((headin_window["bag"], headin_window["frame_index"]))
    segs = {}
    for b, f in centres:
        segs.setdefault(b, []).append([max(0, f - WINDOW), f + WINDOW])
    for b in segs:
        merged = []
        for lo, hi in sorted(segs[b]):
            if merged and lo <= merged[-1][1] + 1:
                merged[-1][1] = max(merged[-1][1], hi)
            else:
                merged.append([lo, hi])
        segs[b] = merged
    print("[INFO] refinement centres: " +
          "; ".join(f"{b} #{f}" for b, f in centres), flush=True)
    print("[INFO] refinement segments: " +
          "; ".join(f"{b} {lo}-{hi}" for b in sorted(segs) for lo, hi in segs[b]), flush=True)

    # Frames whose images the contact sheet needs and that are not refined.
    grab = {}
    for r in contact_windows:
        grab.setdefault(r["bag"], set()).add(r["frame_index"])

    fine = []
    images = {}  # (bag, frame_index, pass) -> bgr
    hw_check = []
    for bag_name in sorted(set(segs) | set(grab)):
        bag = BANK / bag_name
        bag_segs = segs.get(bag_name, [])
        bag_grab = grab.get(bag_name, set())

        # The fine pass runs MediaPipe on every colour frame from frame 0 up to
        # the last refined frame, with one VIDEO-mode landmarker per bag, so the
        # landmarks of a refined frame are the ones the frozen extractor
        # (stride 1 from the bag start, same model and settings) would produce
        # with the CPU delegate. A fresh landmarker started at the window gives
        # different visibilities (tracking history), see J-005.
        run_to = max((hi for _, hi in bag_segs), default=-1)

        def wanted(i, bag_grab=bag_grab, run_to=run_to):
            return i <= run_to or i in bag_grab

        landmarker = make_landmarker() if bag_segs else None
        last_ts = -1
        for idx, frames, ctx in iterate_bag(bag, wanted):
            if idx <= run_to:
                rec, bgr, last_ts = process_frame(bag_name, idx, frames, ctx,
                                                  landmarker, last_ts, "fine")
                in_seg = any(lo <= idx <= hi for lo, hi in bag_segs)
                if rec is not None and in_seg:
                    fine.append(rec)
                    images[(bag_name, idx, "fine")] = bgr
            if idx in bag_grab:
                aligned = ctx["align"].process(frames)
                color = np.asanyarray(aligned.get_color_frame().get_data()).copy()
                bgr = color if ctx["cfmt"] != rs.format.rgb8 else cv2.cvtColor(color, cv2.COLOR_RGB2BGR)
                images[(bag_name, idx, "coarse")] = bgr
                hw_check.append((bag_name, idx, int(frames.get_color_frame().get_frame_number())))
        if landmarker is not None:
            landmarker.close()
    t_fine = time.time() - t_start - t_coarse

    # Frame-index consistency between the two playbacks: the hardware frame
    # number must match for the re-read coarse frames.
    coarse_hw = {(r["bag"], r["frame_index"]): r["hw_frame_number"] for r in coarse}
    hw_check += [(r["bag"], r["frame_index"], r["hw_frame_number"]) for r in fine
                 if (r["bag"], r["frame_index"]) in coarse_hw]
    mism = [(b, i, h, coarse_hw.get((b, i))) for b, i, h in hw_check if coarse_hw.get((b, i)) != h]
    print(f"[CHECK] re-read frames {len(hw_check)}, hardware frame number mismatches {len(mism)}",
          flush=True)

    fine_gated = [r for r in fine if r["scores"]["gated"]]
    fine_tpose = [r for r in fine if r["scores"]["tpose_ok"]]
    if not fine_gated:
        sys.exit("[ERROR] no refined frame passes the gates")
    pick = sorted(fine_gated, key=rank_key)[0]
    pick_t = sorted(fine_tpose, key=rank_key)[0] if fine_tpose else None
    fine_headin = [r for r in fine if r["scores"]["headin_ok"]]
    pick_h = sorted(fine_headin, key=rank_key)[0] if fine_headin else None

    # Candidates CSV: every scored frame, both passes.
    with open(DATA_DIR / "perfect_frame_candidates.csv", "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(csv_header())
        for r in coarse + fine:
            wr.writerow(csv_row(r))

    run_s = time.time() - t_start
    run_info = {
        "script": "journal/scripts/select_perfect_frame.py",
        "model_file": str(MODEL_PATH.relative_to(REPO)),
        "mediapipe_version": mp.__version__, "pyrealsense2_version": importlib.metadata.version("pyrealsense2"),
        "delegate": "CPU", "num_poses": MP_NUM_POSES,
        "min_pose_detection_confidence": MP_DET_CONF,
        "min_pose_presence_confidence": MP_PRES_CONF,
        "min_tracking_confidence": MP_TRACK_CONF,
        "stride": STRIDE, "vis_gate": VIS_GATE, "margin_frac": MARGIN_FRAC,
        "tpose_gate": TPOSE_GATE, "window": WINDOW, "refine_top": REFINE_TOP,
        "ranking": "gated (vis_min8 >= vis_gate, margin_ok, depth_ok); vis_min8 desc, sharpness desc",
        "bags_processed": len(summary), "bags_failed": failed,
        "coarse_scored": len(coarse), "coarse_gated": len(coarse_gated),
        "fine_scored": len(fine), "fine_gated": len(fine_gated),
        "refinement_centres": [{"bag": b, "frame_index": i} for b, i in centres],
        "hw_frame_number_mismatches": len(mism),
        "run_time_s": round(run_s, 1),
        "run_time_coarse_s": round(t_coarse, 1), "run_time_fine_s": round(t_fine, 1),
        "run_date": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(DATA_DIR / "perfect_frame.json", "w") as f:
        json.dump(json_record(pick, run_info), f, indent=2)
    cv2.imwrite(str(FIG_DIR / "perfect_frame_rgb.png"),
                images[(pick["bag"], pick["frame_index"], "fine")])
    cv2.imwrite(str(FIG_DIR / "perfect_frame_overlay.png"),
                draw_overlay(images[(pick["bag"], pick["frame_index"], "fine")], pick))
    if pick_t is not None:
        with open(DATA_DIR / "perfect_frame_tpose.json", "w") as f:
            json.dump(json_record(pick_t, run_info), f, indent=2)
        cv2.imwrite(str(FIG_DIR / "perfect_frame_tpose_rgb.png"),
                    images[(pick_t["bag"], pick_t["frame_index"], "fine")])
        cv2.imwrite(str(FIG_DIR / "perfect_frame_tpose_overlay.png"),
                    draw_overlay(images[(pick_t["bag"], pick_t["frame_index"], "fine")], pick_t))
    # Alternative pick with all face landmarks inside the margin (head_in),
    # informational: written for the author's choice, not the brief's pick.
    if pick_h is not None:
        with open(DATA_DIR / "perfect_frame_headin.json", "w") as f:
            json.dump(json_record(pick_h, run_info), f, indent=2)
        cv2.imwrite(str(FIG_DIR / "perfect_frame_headin_rgb.png"),
                    images[(pick_h["bag"], pick_h["frame_index"], "fine")])
        cv2.imwrite(str(FIG_DIR / "perfect_frame_headin_overlay.png"),
                    draw_overlay(images[(pick_h["bag"], pick_h["frame_index"], "fine")], pick_h))

    # Contact sheet: best frame of each of the top CONTACT_TILES distinct
    # coarse windows; a refined window shows its best fine frame instead.
    tile_recs = []
    for r in contact_windows:
        in_win = [x for x in fine_gated if x["bag"] == r["bag"]
                  and abs(x["frame_index"] - r["frame_index"]) <= WINDOW]
        tile_recs.append(sorted(in_win, key=rank_key)[0] if in_win else r)
    tile_recs = sorted(tile_recs, key=rank_key)
    tiles = []
    for k, r in enumerate(tile_recs):
        s = r["scores"]
        img = images[(r["bag"], r["frame_index"], r["pass"])]
        tiles.append((img, [f"#{k + 1} {short_bag(r['bag'])}",
                            f"frame {r['frame_index']} ({r['pass']})  vis_min8 {s['vis_min8']:.4f}",
                            f"sharpness {s['sharpness']:.1f}  tpose {s['tpose']:.3f}",
                            f"face_top_y {s['face_top_y']:.3f}  hip-sh dz {s['hip_minus_shoulder_depth_m']:.3f} m"]))
    cv2.imwrite(str(FIG_DIR / "candidates_contact.png"), contact_sheet(tiles))

    print("\n[SUMMARY] bag | seen | processed | scored | gated | best vis_min8 | best gated sharpness")
    for row in summary:
        print(f"  {row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]} | {row[5]:.4f} | {row[6]:.1f}")
    print(f"[SUMMARY] failed bags: {failed if failed else 'none'}")
    for label, r in (("PICK", pick), ("TPOSE", pick_t), ("HEADIN", pick_h)):
        if r is None:
            print(f"[{label}] none")
            continue
        s = r["scores"]
        print(f"[{label}] {r['bag']} frame {r['frame_index']} hw {r['hw_frame_number']} "
              f"t {r['time_s']:.3f} s: vis_min8 {s['vis_min8']:.6f} vis_min_face "
              f"{s['vis_min_face']:.6f} sharpness {s['sharpness']:.2f} tpose {s['tpose']:.4f} "
              f"face_top_y {s['face_top_y']:.4f} head_in {s['head_in']} "
              f"hip-shoulder depth {s['hip_minus_shoulder_depth_m']:.3f} m")
    print("[CONTACT] " + "; ".join(f"{r['bag']} #{r['frame_index']}" for r in tile_recs))
    print(f"[TIME] coarse {t_coarse:.1f} s, fine {t_fine:.1f} s, total {run_s:.1f} s")


# ---------------------------------------------------------------- depth-clean stage

CANDIDATES_CSV = DATA_DIR / "perfect_frame_candidates.csv"
FINE2_CSV = DATA_DIR / "perfect_frame_candidates_fine2.csv"
DC_CSV = DATA_DIR / "perfect_frame_candidates_depth.csv"
DC_KEY = f"depth_win{DC_WINDOW}"


def depth_window_stats(depth_img, depth_scale, u, v, window=DC_WINDOW):
    """Valid fraction, median, population std and max-min (metres) of the
    nonzero aligned depth in a window x window patch centred on (u, v).
    Patch pixels outside the image count as invalid."""
    r = window // 2
    patch = depth_img[max(0, v - r):v + r + 1, max(0, u - r):u + r + 1]
    vals = patch[patch > 0].astype(np.float64) * depth_scale
    frac = vals.size / float(window * window)
    if vals.size == 0:
        nan = float("nan")
        return {"valid_frac": 0.0, "median_m": nan, "std_m": nan, "range_m": nan}
    return {"valid_frac": frac, "median_m": float(np.median(vals)),
            "std_m": float(np.std(vals)), "range_m": float(vals.max() - vals.min())}


def add_depth_clean(rec, depth_img, depth_scale):
    """Samples the DC_WINDOW window at each of the 8 landmark pixels of rec
    (u_int, v_int from the scoring pass) and adds the frame-level values
    depth_clean8, depth_std_max8 and depth_valid_min8 to rec['scores']."""
    st = {i: depth_window_stats(depth_img, depth_scale, rec["model"][i]["u_int"],
                                rec["model"][i]["v_int"]) for i in MODEL_LMS}
    stds = [s["std_m"] for s in st.values()]
    rec["depth_win"] = st
    rec["scores"]["depth_clean8"] = all(s["valid_frac"] >= DC_VALID_FRAC and s["std_m"] <= DC_STD_MAX_M
                                        for s in st.values())
    rec["scores"]["depth_std_max8"] = float("inf") if any(np.isnan(stds)) else max(stds)
    rec["scores"]["depth_valid_min8"] = min(s["valid_frac"] for s in st.values())


def rec_from_row(row):
    """Rebuilds a scored record from a candidates CSV row (dict of strings).
    Values carry the CSV's rounding (6 decimals for x, y, visibility and
    metres); intrinsics are not in the CSV and are added from the bag."""
    def flag(k):
        return row[k] == "1"

    def triple(keys):
        vals = [row[k] for k in keys]
        return [float(x) for x in vals] if all(vals) else None

    rec = {"bag": row["bag"], "pass": row["pass"], "frame_index": int(row["frame_index"]),
           "hw_frame_number": int(row["hw_frame_number"]),
           "timestamp_ms": float(row["timestamp_ms"]), "time_s": float(row["time_s"]),
           "landmarks": {}, "model": {}}
    for i in range(N_LMS):
        rec["landmarks"][i] = {
            "x": float(row[f"L{i}_x"]), "y": float(row[f"L{i}_y"]),
            "z": float(row[f"L{i}_z"]), "u": float(row[f"L{i}_u"]), "v": float(row[f"L{i}_v"]),
            "visibility": float(row[f"L{i}_vis"]), "presence": float(row[f"L{i}_pres"])}
    for i in MODEL_LMS:
        rec["model"][i] = {
            "u_int": int(row[f"L{i}_u_int"]), "v_int": int(row[f"L{i}_v_int"]),
            "depth_px_m": float(row[f"L{i}_depth_px_m"]),
            "xyz_px_m": triple([f"L{i}_Xpx", f"L{i}_Ypx", f"L{i}_Zpx"]),
            "depth_med5_m": float(row[f"L{i}_depth_med5_m"]),
            "xyz_med5_m": triple([f"L{i}_X", f"L{i}_Y", f"L{i}_Z"])}
    rec["scores"] = {
        "vis_min8": float(row["vis_min8"]), "vis_min_face": float(row["vis_min_face"]),
        "margin_ok": flag("margin_ok"), "depth_ok": flag("depth_ok"),
        "sharpness": float(row["sharpness"]), "tpose": float(row["tpose"]),
        "shoulder_px_width": float(row["shoulder_px_width"]), "gated": flag("gated"),
        "tpose_ok": flag("tpose_ok"), "face_top_y": float(row["face_top_y"]),
        "head_in": flag("head_in"), "headin_ok": flag("headin_ok"),
        "hip_minus_shoulder_depth_m": float(row["hip_minus_shoulder_depth_m"])}
    return rec


def row_strings(rec):
    """rec as the candidates CSV would store it: {column: string}."""
    return dict(zip(csv_header(), (str(x) for x in csv_row(rec))))


def walk_depth(bag_name, recs_by_idx):
    """Plays one bag once at stride 1 and, at every frame index in
    recs_by_idx {index: [records]}, samples the aligned depth around each
    record's 8 landmark pixels. Returns the hardware frame number
    mismatches against the CSV."""
    want = set(recs_by_idx)
    last = max(want)
    mism = 0
    gen = iterate_bag(BANK / bag_name, lambda i: i in want)
    try:
        for idx, frames, ctx in gen:
            hw = int(frames.get_color_frame().get_frame_number())
            aligned = ctx["align"].process(frames)
            depth = np.asanyarray(aligned.get_depth_frame().get_data())
            for rec in recs_by_idx[idx]:
                mism += rec["hw_frame_number"] != hw
                add_depth_clean(rec, depth, ctx["depth_scale"])
            if idx >= last:
                break
    finally:
        gen.close()
    return mism


def merge_segments(centres):
    """centres [(bag, frame_index)] -> {bag: merged [[lo, hi]]} of the
    +-WINDOW intervals (the default fine pass's rule)."""
    segs = {}
    for b, f in centres:
        segs.setdefault(b, []).append([max(0, f - WINDOW), f + WINDOW])
    for b in segs:
        merged = []
        for lo, hi in sorted(segs[b]):
            if merged and lo <= merged[-1][1] + 1:
                merged[-1][1] = max(merged[-1][1], hi)
            else:
                merged.append([lo, hi])
        segs[b] = merged
    return segs


def fine2_pass(segs, fine_rows):
    """Stride-1 pass with the default fine pass's procedure (one VIDEO-mode
    landmarker per bag, MediaPipe on every frame from frame 0), pass name
    'fine2'. Frames that already have a default fine row keep that row; for
    them the fine2 result is compared with it column by column (a
    determinism check). Gated fine2 records get their depth-clean values.
    Returns (records, checked, mismatched)."""
    out, checked, mism = [], 0, 0
    for bag_name in sorted(segs):
        bag_segs = segs[bag_name]
        run_to = max(hi for _, hi in bag_segs)
        landmarker = make_landmarker()
        last_ts = -1
        t0 = time.time()
        gen = iterate_bag(BANK / bag_name, lambda i, run_to=run_to: i <= run_to)
        try:
            for idx, frames, ctx in gen:
                rec, _, last_ts = process_frame(bag_name, idx, frames, ctx,
                                                landmarker, last_ts, "fine2")
                in_seg = any(lo <= idx <= hi for lo, hi in bag_segs)
                if rec is not None and in_seg:
                    old = fine_rows.get((bag_name, idx))
                    if old is not None:
                        new = row_strings(rec)
                        checked += 1
                        mism += any(new[k] != old[k] for k in new if k != "pass")
                    else:
                        if rec["scores"]["gated"]:
                            aligned = ctx["align"].process(frames)
                            add_depth_clean(rec, np.asanyarray(aligned.get_depth_frame().get_data()),
                                            ctx["depth_scale"])
                        out.append(rec)
                if idx >= run_to:
                    break
        finally:
            gen.close()
            landmarker.close()
        print(f"[FINE2] {bag_name}: segments {bag_segs}, MediaPipe on frames 0-{run_to}, "
              f"{time.time() - t0:.1f} s", flush=True)
    return out, checked, mism


def grab_frames(need, depth_for):
    """need {bag: set(frame_index)}: colour images (BGR) of those frames,
    aligned depth (raw units) for the (bag, index) pairs in depth_for,
    colour intrinsics per bag and the hardware colour frame numbers."""
    images, depths, intr, hws = {}, {}, {}, {}
    for bag_name in sorted(need):
        want = need[bag_name]
        last = max(want)
        gen = iterate_bag(BANK / bag_name, lambda i, want=want: i in want)
        try:
            for idx, frames, ctx in gen:
                aligned = ctx["align"].process(frames)
                color = np.asanyarray(aligned.get_color_frame().get_data()).copy()
                images[(bag_name, idx)] = (cv2.cvtColor(color, cv2.COLOR_RGB2BGR)
                                           if ctx["cfmt"] == rs.format.rgb8 else color)
                hws[(bag_name, idx)] = int(frames.get_color_frame().get_frame_number())
                if (bag_name, idx) in depth_for:
                    depths[(bag_name, idx)] = (np.asanyarray(aligned.get_depth_frame().get_data()).copy(),
                                               ctx["depth_scale"])
                intr[bag_name] = intrinsics_dict(ctx["intr"], ctx["depth_scale"])
                if idx >= last:
                    break
        finally:
            gen.close()
    return images, depths, intr, hws


def dc_json_record(rec, intr, run_info):
    """json_record plus the depth-window values of the 8 landmarks."""
    out = json_record(dict(rec, intrinsics=intr), run_info)
    for i in MODEL_LMS:
        out["model_landmarks"][str(i)][DC_KEY] = rec["depth_win"][i]
    out["model_landmarks_note"] += (
        f"; {DC_KEY} = valid_frac, median_m, std_m (population std) and range_m (max - min) "
        f"of the nonzero aligned depth in the {DC_WINDOW}x{DC_WINDOW} window centred on "
        "(u_int, v_int) (journal/DECISIONS.md J-010)")
    out["values_source"] = ("journal/data/perfect_frame_candidates.csv or _fine2.csv row "
                            "(6 decimals); intrinsics read from the bag")
    return out


def mark_unpicked(path, recs, label):
    """No row passes for this pick: the existing record (an earlier J-005
    pick) stays, with a depth_clean_stage block that says so and carries its
    own depth-window values, so it is not mistaken for a depth-clean pick."""
    if not path.exists():
        print(f"[{label}] none, and no earlier record at {path.name}")
        return
    d = json.load(open(path))
    note = {"status": (f"no fine or fine2 row passes the J-005 gates, the {label} condition and "
                       "depth_clean8 (journal/DECISIONS.md J-010); this record is the earlier J-005 "
                       "pick, kept for reference, and is not a depth-clean pick")}
    match = [r for r in recs if r["bag"] == d["bag"] and r["frame_index"] == d["frame_index"]
             and r["pass"] == d["pass"] and "depth_win" in r]
    if match:
        r = match[0]
        note.update({k: r["scores"][k] for k in ("depth_clean8", "depth_std_max8", "depth_valid_min8")})
        note[DC_KEY] = {f"L{i}": r["depth_win"][i] for i in MODEL_LMS}
    d["depth_clean_stage"] = note
    with open(path, "w") as f:
        json.dump(d, f, indent=2)
    print(f"[{label}] none; {path.name} kept (earlier pick) with a depth_clean_stage note")


def depth_check_figure(bgr, depth_raw, depth_scale, rec, title, out_path):
    """RGB and aligned-depth crops (80x80) around each of the 8 landmark
    pixels, the DC_WINDOW window drawn, its median and std printed."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    D = depth_raw.astype(np.float64) * depth_scale
    rgb = bgr[..., ::-1]
    h, w = D.shape
    half, r = 40, DC_WINDOW // 2
    cmap = matplotlib.colormaps["turbo"].copy()
    cmap.set_bad("black")
    fig, axs = plt.subplots(4, 4, figsize=(15, 15.5), dpi=100)
    for k, i in enumerate(MODEL_LMS):
        row, col = divmod(k, 2)
        a, b = axs[row, 2 * col], axs[row, 2 * col + 1]
        m, st = rec["model"][i], rec["depth_win"][i]
        u, v = m["u_int"], m["v_int"]
        x0, x1, y0, y1 = max(0, u - half), min(w, u + half), max(0, v - half), min(h, v + half)
        ext = (x0 - 0.5, x1 - 0.5, y1 - 0.5, y0 - 0.5)
        a.imshow(rgb[y0:y1, x0:x1], extent=ext, interpolation="nearest")
        med = st["median_m"]
        im = b.imshow(np.ma.masked_equal(D[y0:y1, x0:x1], 0), extent=ext, cmap=cmap,
                      vmin=med - 0.15, vmax=med + 0.15, interpolation="nearest")
        for ax in (a, b):
            ax.add_patch(Rectangle((u - r - 0.5, v - r - 0.5), DC_WINDOW, DC_WINDOW,
                                   fill=False, ec="magenta", lw=1.5))
            ax.plot([u], [v], marker="+", color="red", ms=10, mew=1.5)
            ax.tick_params(labelsize=7)
        ok = st["valid_frac"] >= DC_VALID_FRAC and st["std_m"] <= DC_STD_MAX_M
        a.set_title(f"L{i} {LANDMARK_NAMES[i]}, pixel ({u}, {v})\nRGB, red + = landmark pixel",
                    fontsize=9)
        b.set_title(f"depth [m]: pixel {D[v, u]:.3f}, {DC_WINDOW}x{DC_WINDOW} median {med:.3f}\n"
                    f"std {st['std_m'] * 1000:.1f} mm, max-min {st['range_m'] * 1000:.0f} mm, "
                    f"valid {st['valid_frac'] * 100:.0f} % -> {'PASS' if ok else 'FAIL'}", fontsize=9)
        fig.colorbar(im, ax=b, fraction=0.046, pad=0.04).ax.tick_params(labelsize=7)
    fig.suptitle(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(out_path, metadata={"Software": None})
    plt.close(fig)


def depth_clean_stage():
    """--depth-clean (J-010): depth-window gate on top of the J-005 gates,
    a stride-1 'fine2' pass for the best coarse-only clean candidates, the
    re-ranked picks and their outputs. MediaPipe runs only in the fine2
    pass; every other landmark pixel comes from the candidates CSV."""
    t_start = time.time()
    if not CANDIDATES_CSV.exists():
        sys.exit(f"[ERROR] {CANDIDATES_CSV} missing: run the default stage first")
    with open(CANDIDATES_CSV, newline="") as f:
        rows = list(csv.DictReader(f))
    fine_rows = {(r["bag"], int(r["frame_index"])): r for r in rows if r["pass"] == "fine"}
    gated = [rec_from_row(r) for r in rows if r["gated"] == "1"]
    print(f"[INFO] {len(rows)} candidate rows, {len(gated)} gated; DC_WINDOW={DC_WINDOW} "
          f"DC_VALID_FRAC={DC_VALID_FRAC} DC_STD_MAX_M={DC_STD_MAX_M} DC_REFINE_TOP={DC_REFINE_TOP}",
          flush=True)

    # 1. Depth windows at every gated row, one stride-1 playback per bag.
    by_bag = {}
    for r in gated:
        by_bag.setdefault(r["bag"], {}).setdefault(r["frame_index"], []).append(r)
    hw_mism = 0
    for bag_name in sorted(by_bag):
        t0 = time.time()
        hw_mism += walk_depth(bag_name, by_bag[bag_name])
        recs = [r for lst in by_bag[bag_name].values() for r in lst]
        n_clean = sum(r["scores"].get("depth_clean8", False) for r in recs)
        print(f"[DEPTH] {bag_name}: gated rows {len(recs)}, depth_clean8 {n_clean}, "
              f"{time.time() - t0:.1f} s", flush=True)
    missing = [r for r in gated if "depth_win" not in r]
    t_walk = time.time() - t_start
    print(f"[CHECK] depth walk: hardware frame number mismatches {hw_mism}, "
          f"gated rows not reached {len(missing)}", flush=True)

    # 2. Coarse-only clean candidates get a stride-1 pass: the literal top
    # DC_REFINE_TOP, the top DC_REFINE_TOP distinct windows, the top
    # REFINE_TOP distinct T-pose windows and the best head-in window.
    clean = [r for r in gated if r["scores"].get("depth_clean8")]
    coarse_only = [r for r in clean if r["pass"] == "coarse"
                   and (r["bag"], r["frame_index"]) not in fine_rows]
    groups = [("top", sorted(coarse_only, key=rank_key)[:DC_REFINE_TOP]),
              ("distinct", distinct_windows(coarse_only, DC_REFINE_TOP)),
              ("tpose", distinct_windows([r for r in coarse_only if r["scores"]["tpose_ok"]],
                                         REFINE_TOP)),
              ("headin", sorted([r for r in coarse_only if r["scores"]["headin_ok"]],
                                key=rank_key)[:1])]
    centres = []
    for label, lst in groups:
        for r in lst:
            print(f"[CENTRE] {label}: {r['bag']} #{r['frame_index']} vis_min8 "
                  f"{r['scores']['vis_min8']:.6f} sharpness {r['scores']['sharpness']:.2f}", flush=True)
            if (r["bag"], r["frame_index"]) not in centres:
                centres.append((r["bag"], r["frame_index"]))
    segs = merge_segments(centres)
    fine2, det_checked, det_mism = fine2_pass(segs, fine_rows)
    # Round-trip through the CSV representation so every record carries the
    # same rounding whatever pass it comes from.
    fine2_rt = []
    for r in fine2:
        rt = rec_from_row(row_strings(r))
        if "depth_win" in r:
            rt["depth_win"] = r["depth_win"]
            for k in ("depth_clean8", "depth_std_max8", "depth_valid_min8"):
                rt["scores"][k] = r["scores"][k]
        fine2_rt.append(rt)
    with open(FINE2_CSV, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(csv_header())
        for r in fine2:
            wr.writerow(csv_row(r))
    t_fine2 = time.time() - t_start - t_walk
    print(f"[CHECK] fine2: {len(fine2)} new rows, {det_checked} frames re-scored that have a "
          f"default fine row, column mismatches {det_mism}", flush=True)

    # 3. Depth CSV for every gated row of the three passes.
    all_gated = gated + [r for r in fine2_rt if r["scores"]["gated"]]
    head = ["pass", "bag", "frame_index", "hw_frame_number", "depth_clean8",
            "depth_std_max8", "depth_valid_min8"]
    for i in MODEL_LMS:
        head += [f"L{i}_w{DC_WINDOW}_{k}" for k in ("valid_frac", "median_m", "std_m", "range_m")]
    with open(DC_CSV, "w", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(head)
        for r in all_gated:
            if "depth_win" not in r:
                continue
            s = r["scores"]
            row = [r["pass"], r["bag"], r["frame_index"], r["hw_frame_number"],
                   int(s["depth_clean8"]), f"{s['depth_std_max8']:.6f}", f"{s['depth_valid_min8']:.4f}"]
            for i in MODEL_LMS:
                st = r["depth_win"][i]
                row += [f"{st['valid_frac']:.4f}", f"{st['median_m']:.6f}", f"{st['std_m']:.6f}",
                        f"{st['range_m']:.6f}"]
            wr.writerow(row)

    # 4. Re-rank and pick from the fine and fine2 rows.
    clean_all = [r for r in all_gated if r["scores"].get("depth_clean8")]
    fine_clean = [r for r in clean_all if r["pass"] in ("fine", "fine2")]
    if not fine_clean:
        sys.exit("[ERROR] no fine row passes the gates and depth_clean8")
    pick = sorted(fine_clean, key=rank_key)[0]
    tp = [r for r in fine_clean if r["scores"]["tpose_ok"]]
    pick_t = sorted(tp, key=rank_key)[0] if tp else None
    hi = [r for r in fine_clean if r["scores"]["headin_ok"]]
    pick_h = sorted(hi, key=rank_key)[0] if hi else None
    tile_recs = distinct_windows(clean_all, CONTACT_TILES)

    picks = [("perfect_frame", "PICK", pick), ("perfect_frame_tpose", "TPOSE", pick_t),
             ("perfect_frame_headin", "HEADIN", pick_h)]
    need = {}
    for r in tile_recs + [p for _, _, p in picks if p is not None]:
        need.setdefault(r["bag"], set()).add(r["frame_index"])
    pkey = (pick["bag"], pick["frame_index"])
    images, depths, intr, hws = grab_frames(need, {pkey})
    grab_mism = sum(hws[(r["bag"], r["frame_index"])] != r["hw_frame_number"]
                    for r in tile_recs + [p for _, _, p in picks if p is not None])

    prev = DATA_DIR / "perfect_frame.json"
    prev_sel = json.load(open(prev)).get("selection") if prev.exists() else None
    if isinstance(prev_sel, dict) and "default_run" in prev_sel:
        prev_sel = prev_sel["default_run"]
    run_s = time.time() - t_start
    run_info = {
        "default_run": prev_sel,
        "depth_clean_stage": {
            "script": "journal/scripts/select_perfect_frame.py --depth-clean",
            "dc_window": DC_WINDOW, "dc_valid_frac": DC_VALID_FRAC, "dc_std_max_m": DC_STD_MAX_M,
            "dc_refine_top": DC_REFINE_TOP,
            "ranking": ("gated (J-005) and depth_clean8 (every landmark window: valid_frac >= "
                        "dc_valid_frac and std_m <= dc_std_max_m); vis_min8 desc, sharpness desc; "
                        "picks from fine and fine2 rows"),
            "gated_rows": len(all_gated), "depth_clean_rows": len(clean_all),
            "fine_clean_rows": len(fine_clean),
            "fine2_centres": [{"bag": b, "frame_index": i} for b, i in centres],
            "fine2_rows": len(fine2), "fine2_determinism_checked": det_checked,
            "fine2_determinism_mismatches": det_mism,
            "hw_frame_number_mismatches": hw_mism + grab_mism,
            "run_time_s": round(run_s, 1), "run_date": time.strftime("%Y-%m-%d %H:%M:%S")},
    }
    for stem, label, r in picks:
        if r is None:
            mark_unpicked(DATA_DIR / f"{stem}.json", all_gated, label)
            continue
        img = images[(r["bag"], r["frame_index"])]
        with open(DATA_DIR / f"{stem}.json", "w") as f:
            json.dump(dc_json_record(r, intr[r["bag"]], run_info), f, indent=2)
        cv2.imwrite(str(FIG_DIR / f"{stem}_rgb.png"), img)
        cv2.imwrite(str(FIG_DIR / f"{stem}_overlay.png"), draw_overlay(img, r))
    depth_raw, ds = depths[pkey]
    depth_check_figure(images[pkey], depth_raw, ds, pick,
                       f"{pick['bag']} frame {pick['frame_index']} (hw {pick['hw_frame_number']}, "
                       f"{pick['pass']}): {DC_WINDOW}x{DC_WINDOW} depth windows (magenta) at the 8 "
                       f"landmarks; gate valid >= {DC_VALID_FRAC:.2f}, std <= {DC_STD_MAX_M * 1000:.0f} mm",
                       FIG_DIR / "perfect_frame_depth_check8.png")
    tiles = []
    for k, r in enumerate(tile_recs):
        s = r["scores"]
        tiles.append((images[(r["bag"], r["frame_index"])],
                      [f"#{k + 1} {short_bag(r['bag'])}",
                       f"frame {r['frame_index']} ({r['pass']})  vis_min8 {s['vis_min8']:.4f}",
                       f"sharpness {s['sharpness']:.1f}  tpose {s['tpose']:.3f}",
                       f"face_top_y {s['face_top_y']:.3f}  hip-sh dz {s['hip_minus_shoulder_depth_m']:.3f} m",
                       f"depth std max8 {s['depth_std_max8'] * 1000:.1f} mm  valid min "
                       f"{s['depth_valid_min8']:.2f}"]))
    cv2.imwrite(str(FIG_DIR / "candidates_contact.png"), contact_sheet(tiles, cap=89))

    # 5. Report.
    def line(r):
        s = r["scores"]
        return (f"{r['bag']} #{r['frame_index']} ({r['pass']}) hw {r['hw_frame_number']} "
                f"t {r['time_s']:.3f} s: vis_min8 {s['vis_min8']:.6f} vis_min_face "
                f"{s['vis_min_face']:.6f} sharpness {s['sharpness']:.2f} tpose {s['tpose']:.4f} "
                f"face_top_y {s['face_top_y']:.4f} head_in {int(s['head_in'])} hip-sh "
                f"{s['hip_minus_shoulder_depth_m']:.3f} m depth_std_max8 "
                f"{s['depth_std_max8'] * 1000:.1f} mm depth_valid_min8 {s['depth_valid_min8']:.3f}")
    by_pass = {}
    for r in all_gated:
        c = by_pass.setdefault(r["pass"], [0, 0])
        c[0] += 1
        c[1] += bool(r["scores"].get("depth_clean8"))
    print("[COUNT] gated / depth_clean8 per pass: " +
          "; ".join(f"{p} {c[0]} / {c[1]}" for p, c in sorted(by_pass.items())))
    print("[TOP10] rows, all passes, gated and depth_clean8:")
    for k, r in enumerate(sorted(clean_all, key=rank_key)[:10]):
        print(f"  {k + 1:2d} {line(r)}")
    print("[TOP10] distinct windows:")
    for k, r in enumerate(tile_recs[:10]):
        print(f"  {k + 1:2d} {line(r)}")
    for _, label, r in picks:
        print(f"[{label}] " + (line(r) if r is not None else "none"))
    for i in MODEL_LMS:
        st = pick["depth_win"][i]
        print(f"[PICK-DEPTH] L{i}: valid {st['valid_frac']:.3f} median {st['median_m']:.4f} m "
              f"std {st['std_m'] * 1000:.2f} mm max-min {st['range_m'] * 1000:.1f} mm")
    print(f"[CHECK] grab pass hardware frame number mismatches {grab_mism}")
    print(f"[TIME] depth walk {t_walk:.1f} s, fine2 {t_fine2:.1f} s, total {run_s:.1f} s")


if __name__ == "__main__":
    if "--figures-only" in sys.argv[1:]:
        redraw_overlays()
    elif "--depth-clean" in sys.argv[1:]:
        depth_clean_stage()
    else:
        main()
