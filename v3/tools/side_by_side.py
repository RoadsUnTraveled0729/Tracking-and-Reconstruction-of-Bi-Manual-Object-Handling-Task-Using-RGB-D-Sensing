#!/usr/bin/env python3
"""M8a side-by-side films: camera frame with the RTMPose overlay (left)
beside the V3 reconstruction drawn from the 13 angles (right), the same
bag frame in both panels (D-039).

Per film, the FULL V3 stack of the default config runs on the whole
extraction CSV from frame 0 (replay/runner.py run_csv: causal landmark
filter, Unity flip, S2 s2_quat_prediction with warm start, D-032 caps
on the D-033 manifest, the configured smoother (tangent_kf, D-038),
13 angles, per-group honesty statuses 0 measured / 1 estimated /
2 lost). The rendered range is then sliced out.

Left panel (768x576): the bag colour frame (BagSource, BGR -> RGB,
LANCZOS to 768x576) with the RTMPose keypoints of the eight v1
landmarks from the extraction CSV (<name>_u/_v; filled = depth sampled,
hollow = depth hole) and the eight-landmark skeleton drawn thin. The
other nine COCO keypoints are not stored in the extraction CSV and are
not drawn.

Right panel (768x576, dark): the rig in the same camera view (bag
intrinsics from the extraction .meta.json, pinhole, zero distortion):
torso = hip-shoulder quadrilateral of the causally filtered landmarks
the strategy received (held at the last valid value while missing);
upper arm and forearm = core/fk.py fk_arm from the 13 angles, anchored
at the filtered shoulder, bone lengths = per-recording medians of the
oracle-filtered landmarks (D-037). Colours per group status: white
measured, amber estimated, red lost (D-013); torso = root, upper arm =
swing, forearm = worse of twist and elbow. The measured (raw CSV) wrist
is a faint grey ring; the ArUco object cube (bench/aruco_source.py,
camera optical, 45 mm scale, 0.07 m cube) is drawn when the marker is
detected (R4-R7 only; the clean windows have no ArUco CSV). A status
strip (current group statuses) and a status timeline with a cursor sit
at the bottom.

Output: v3/output/side_by_side/side_by_side_<label>__<variant>[__half].mp4
(1536x576, H.264 yuv420p, libx264 preset slow crf 20, +faststart, the
encoder settings of presentation/defense_2026/anim/causal_replay.py
stage_encode), a sidecar JSON next to it, the contact sheet
v3/dataset/phase5_side_by_side_<label>.png, and (after every run) the
manifest v3/dataset/phase5_side_by_side_manifest.json and the occlusion
summary v3/dataset/phase5_side_by_side_summary.txt rebuilt from every
sidecar present.

Usage (base anaconda python has pyrealsense2):
  python tools/side_by_side.py --recording r4
  python tools/side_by_side.py --recording all
  python tools/side_by_side.py --recording right_elbow --half-speed
Labels: r4 r5 r6b r7 (or their recording_<date> stems) and the clean
window names of configs/clean_windows.json (or their bag stems).
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw

V3_ROOT = Path(__file__).resolve().parents[1]
REPO = V3_ROOT.parent
if str(V3_ROOT) not in sys.path:
    sys.path.insert(0, str(V3_ROOT))

from bench import aruco_source                             # noqa: E402
from bench.metrics import (ANGLE_NAMES, GROUP_ANGLES,       # noqa: E402
                           GROUP_NAMES, wrap_deg)
from bench.oracle import filter_landmarks                  # noqa: E402
from bench.paths import apply_overrides, repo_path, repo_rel  # noqa: E402
from core import fk                                        # noqa: E402
from tools import render_rig as rr                         # noqa: E402

OUT_DIR = V3_ROOT / "output" / "side_by_side"
DATASET = V3_ROOT / "dataset"
MANIFEST = DATASET / "phase5_side_by_side_manifest.json"
SUMMARY = DATASET / "phase5_side_by_side_summary.txt"
SCHEMA = "v3.side_by_side.v1"

RECORDING_ORDER = ("r4", "r5", "r6b", "r7")
CLEAN_ORDER = ("right_elbow", "180042", "right_arm_test",
               "arms_outstretched")

# Encoder settings: presentation/defense_2026/anim/causal_replay.py
# stage_encode (master film): libx264, preset slow, crf 20, yuv420p,
# +faststart.
ENCODER = {"codec": "libx264", "preset": "slow", "crf": 20,
           "pix_fmt": "yuv420p", "movflags": "+faststart"}

# Film and contact-sheet constants (D-039; sources there).
LEAD_IN_S = 1.0            # brief M8a: clean windows plus 1 s lead-in
REACQ_SETTLE_FRAMES = 10   # contact sheet: 2nd "reacquiring" frame offset (editorial)
REACQ_WINDOW_FRAMES = 30   # summary: max step over the 1 s after reacquisition
CONTACT_TILE = (768, 288)  # contact sheet tile = half-size composite
CONTACT_MAX_BYTES = 1_500_000   # brief M8a
# start-of-stream warmup excluded from the step statistics:
# configs/bench.json latency.warmup_frames (the bench's warmup rule)
WARMUP_FRAMES = json.loads((V3_ROOT / "configs" / "bench.json")
                           .read_text())["latency"]["warmup_frames"]

NAMES = ("left_hip", "right_hip", "left_shoulder", "right_shoulder",
         "left_elbow", "right_elbow", "left_wrist", "right_wrist")
# eight-landmark skeleton edges: unified_panels.py EDGES
EDGES = (("left_hip", "right_hip"), ("left_hip", "left_shoulder"),
         ("right_hip", "right_shoulder"), ("left_shoulder", "right_shoulder"),
         ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"),
         ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"))
TORSO = (("left_hip", "right_hip"), ("left_hip", "left_shoulder"),
         ("right_hip", "right_shoulder"), ("left_shoulder", "right_shoulder"))
GIDX = {g: i for i, g in enumerate(GROUP_NAMES)}
SIDE_GROUPS = {"right": ("R_swing", "R_twist", "R_elbow"),
               "left": ("L_swing", "L_twist", "L_elbow")}
CHIP_LABELS = ("root", "R swing", "R twist", "R elbow", "L swing",
               "L twist", "L elbow")
KP_RGB = (64, 224, 112)          # AXIS_COLORS["Y"], coordinate_axes.py
SKEL_THIN_RGB = (235, 235, 235)


# --------------------------------------------------------------------------
# sources
# --------------------------------------------------------------------------

def sha256(path, n=None):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    d = h.hexdigest()
    return d if n is None else d[:n]


def resolve(label, variant):
    """label -> source dict: name, kind (recording | clean), stem, csv,
    meta, bag, alias (ArUco) or None, window (start, stop) or None."""
    stems = aruco_source.STEMS
    for alias, stem in stems.items():
        if label in (alias, stem):
            csv = V3_ROOT / "output" / "objects" / \
                f"extraction_{stem}__{variant}.csv"
            return _with_meta({"name": alias, "kind": "recording",
                               "stem": stem, "csv": csv, "alias": alias,
                               "window": None})
    wins = json.loads((V3_ROOT / "configs" / "clean_windows.json")
                      .read_text())
    if not wins.get("stop_inclusive"):
        raise ValueError("clean_windows.json must declare stop_inclusive")
    for w in wins["windows"]:
        bstem = Path(w["bag"]).stem
        if label in (w["name"], bstem):
            csv = V3_ROOT / "output" / "clean" / \
                f"extraction_{bstem}__{variant}.csv"
            return _with_meta({"name": w["name"], "kind": "clean",
                               "stem": bstem, "csv": csv, "alias": None,
                               "window": (int(w["start"]), int(w["stop"])),
                               "bag_sha256": w.get("sha256")})
    raise ValueError(f"unknown recording {label!r}")


def _with_meta(src):
    meta_path = src["csv"].with_suffix(".meta.json")
    src["meta"] = json.loads(meta_path.read_text()) if meta_path.exists() \
        else None
    if src["meta"] is not None:
        bag = Path(src["meta"]["bag"])
        # recorded relative bag paths are relative to v3/ (the
        # extractor's working directory; e.g. ../Video/<stem>.bag)
        src["bag"] = bag if bag.is_absolute() else (V3_ROOT / bag).resolve()
    else:
        src["bag"] = None
    return src


def load_config(config_path, variant, manifest, sets):
    cfg = apply_overrides(json.loads(Path(config_path).read_text()), sets)
    if manifest is None:
        if cfg["model"]["variant"] != variant:
            raise SystemExit(f"[ERROR] config variant "
                             f"{cfg['model']['variant']} != --variant "
                             f"{variant}; pass --manifest")
        manifest = str(repo_path(cfg["paths"]["scenario_manifest"]))
    cfg["paths"]["scenario_manifest"] = manifest
    return cfg


def config_hash(cfg):
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()
                          ).hexdigest()


def run_stack(csv, cfg, strategy="s2_quat_prediction"):
    from replay.runner import run_csv
    from strategies.strategy_base import build
    import strategies.baseline_hold        # noqa: F401
    import strategies.s2_quat_prediction   # noqa: F401
    return run_csv(csv, cfg, build(strategy, cfg))


def held(arr):
    """Forward-fill non-finite rows of an (N, 3) array with the last
    finite row (rows before the first finite one stay NaN)."""
    out = np.array(arr, float)
    last = None
    for i in range(len(out)):
        if np.all(np.isfinite(out[i])):
            last = out[i].copy()
        elif last is not None:
            out[i] = last
    return out


def bone_lengths(df, cfg):
    """Per-side (Lu, Lf) = median over the recording of the oracle-
    filtered |shoulder - elbow| and |elbow - wrist| (D-037; the norm is
    invariant to the Unity flip)."""
    filt, _, _ = filter_landmarks(df, cfg)
    out = {}
    for side in ("right", "left"):
        s, e, w = (filt[f"{side}_{j}"] for j in ("shoulder", "elbow",
                                                  "wrist"))
        out[side] = (float(np.nanmedian(np.linalg.norm(s - e, axis=1))),
                     float(np.nanmedian(np.linalg.norm(e - w, axis=1))))
    return out


def build_rig(tab, df, cfg):
    """Per-frame rig in Unity space from the stack output: dict with
    torso landmarks (held), FK elbows and wrists per side, bone
    lengths, raw measured wrists (camera frame), angles, statuses."""
    A = tab[list(ANGLE_NAMES)].to_numpy(dtype=float)
    status = tab[[f"status_{g}" for g in GROUP_NAMES]].to_numpy(dtype=int)
    filt_u = {n: held(tab[[f"{n}_f{a}" for a in "xyz"]].to_numpy(float))
              for n in NAMES}
    bones = bone_lengths(df, cfg)
    rig = {"A": A, "status": status, "torso": filt_u, "bones": bones,
           "elbow": {}, "wrist": {}, "bend": {}}
    for side in ("right", "left"):
        Lu, Lf = bones[side]
        el, wr = fk.fk_arm_series(A, side, Lu, Lf,
                                  filt_u[f"{side}_shoulder"])
        rig["elbow"][side], rig["wrist"][side] = el, wr
        si = fk.SIDE_INDEX[side]
        bend = np.full(len(A), np.nan)
        for i, a in enumerate(A):
            if np.all(np.isfinite(a[si:si + 5])):
                up, fore = fk.arm_dirs(a[si:si + 3], a[si + 3:si + 5], side)
                bend[i] = np.degrees(np.arccos(np.clip(np.dot(up, fore),
                                                       -1.0, 1.0)))
        rig["bend"][side] = bend
    rig["meas_wrist_cam"] = {
        side: df[[f"{side}_wrist_{a}" for a in "xyz"]].to_numpy(float)
        for side in ("right", "left")}
    return rig


def load_object(src, frames):
    """ArUco marker pose per V3 frame (camera optical) and cube size,
    or None when the recording has no ArUco CSV."""
    if src["alias"] is None:
        return None
    world = aruco_source.load_world(src["alias"])
    obj = aruco_source.align(aruco_source.read_object(src["stem"], world),
                             frames)
    return {"det": obj["det"], "t_cam": obj["obj_cam"],
            "R_cam": obj["R_cam"], "cube_m": float(world.cube),
            "center_world": obj["center"], "world": world,
            "time_s": obj["time_s"]}


# --------------------------------------------------------------------------
# status analysis
# --------------------------------------------------------------------------

def runs_of(mask):
    """Contiguous True runs of a bool array -> [(start, stop_incl)]."""
    m = np.asarray(mask, bool).astype(np.int8)
    d = np.diff(np.r_[0, m, 0])
    starts = np.flatnonzero(d == 1)
    stops = np.flatnonzero(d == -1) - 1
    return list(zip(starts.tolist(), stops.tolist()))


def status_fractions(status):
    n = len(status)
    return {g: {"measured": float(np.mean(status[:, j] == 0)),
                "estimated": float(np.mean(status[:, j] == 1)),
                "lost": float(np.mean(status[:, j] == 2)),
                "frames": int(n)}
            for j, g in enumerate(GROUP_NAMES)}


def pick_contact_frames(status):
    """Eight local indices: two clean, two entering occlusion, two
    during, two reacquiring (D-039 rule). Occlusion = any group not
    MEASURED. Episode = the longest occlusion run that has a clean frame
    before and after it inside the range (else the longest run).
    Returns (list of (tag, idx)), episode or None."""
    n = len(status)
    occ = status.max(axis=1) > 0
    eps = runs_of(occ)
    clean_runs = runs_of(~occ)
    picks = []
    if clean_runs:
        a, b = max(clean_runs, key=lambda r: r[1] - r[0])
        L = b - a + 1
        picks += [("clean", a + L // 3), ("clean", a + (2 * L) // 3)]
    if not eps:
        # no occlusion in range: eight evenly spaced frames
        idx = np.linspace(0, n - 1, 8).round().astype(int)
        return [("clean", int(i)) for i in idx], None
    inner = [e for e in eps if e[0] > 0 and e[1] < n - 1]
    a, b = max(inner or eps, key=lambda r: r[1] - r[0])
    L = b - a + 1
    picks += [("entering", max(a - 1, 0)), ("entering", a),
              ("during", a + L // 3), ("during", a + (2 * L) // 3),
              ("reacquiring", min(b + 1, n - 1)),
              ("reacquiring", min(b + 1 + REACQ_SETTLE_FRAMES, n - 1))]
    if len(picks) < 8:          # no clean run at all
        picks = [("during", a)] * (8 - len(picks)) + picks
    return picks, (int(a), int(b))


def occlusion_summary(rig, budgets, twist_min_bend, first_valid=0):
    """Per group: episodes of ESTIMATED and LOST runs, the largest
    per-frame angle step at each reacquisition (first MEASURED frame
    after a non-measured run) and over the REACQ_WINDOW_FRAMES after
    it, relative to the D-033 budget. Twist steps with a causal bend
    below twist_min_bend on either frame are reported but flagged
    exempt, as D-033 exempts them (here the bend comes from the causal
    output angles, not from the oracle). Steps into local frames
    before first_valid (the start-of-stream warmup, bench.json
    latency.warmup_frames) are excluded from every step statistic and
    reported separately as warmup_max_ratio."""
    A, S = rig["A"], rig["status"]
    n = len(A)
    steps = np.zeros((n, len(ANGLE_NAMES)))
    if n > 1:
        steps[1:] = np.abs(wrap_deg(np.diff(A, axis=0)))
    budget = np.array([budgets[a] for a in ANGLE_NAMES])
    ratio = np.divide(steps, budget, out=np.zeros_like(steps),
                      where=budget > 1e-6)   # elbow_z budget 1e-9 = floor
    exempt = np.zeros_like(steps, bool)
    for side, an in (("right", "r_twist"), ("left", "l_twist")):
        b = rig["bend"][side]
        ok = np.r_[False, (b[1:] >= twist_min_bend) & (b[:-1] >= twist_min_bend)]
        exempt[:, ANGLE_NAMES.index(an)] = ~ok
    gated = np.where(exempt, 0.0, ratio)
    fv = int(max(0, min(first_valid, n)))
    warm_max = float(gated[:fv].max()) if fv > 0 else 0.0
    steps[:fv] = 0.0
    gated[:fv] = 0.0
    out = {"_warmup": {"first_valid_local": fv,
                       "warmup_max_ratio": warm_max}}
    for j, g in enumerate(GROUP_NAMES):
        cols = list(GROUP_ANGLES[j])
        s = S[:, j]
        est = [(a, b) for a, b in runs_of(s == 1)]
        lost = [(a, b) for a, b in runs_of(s == 2)]
        reacq = []
        for a, b in runs_of(s != 0):
            t = b + 1
            if t >= n or a == 0 or t < fv:
                continue     # not reacquired in range / starts unmeasured
                             # / inside the warmup
            w1 = min(n, t + REACQ_WINDOW_FRAMES)
            c = cols[int(np.argmax(gated[t, cols]))]
            cw = np.unravel_index(np.argmax(gated[t:w1][:, cols]),
                                  (w1 - t, len(cols)))
            reacq.append({
                "frame_local": int(t), "episode_len": int(b - a + 1),
                "max_status": int(s[a:b + 1].max()),
                "step_deg": float(steps[t, cols].max()),
                "step_angle": ANGLE_NAMES[int(cols[int(np.argmax(steps[t, cols]))])],
                "gated_ratio": float(gated[t, c]),
                "gated_angle": ANGLE_NAMES[c],
                "window_gated_ratio": float(gated[t:w1][:, cols].max()),
                "window_angle": ANGLE_NAMES[cols[cw[1]]],
                "window_frame_local": int(t + cw[0]),
            })
        out[g] = {
            "estimated_runs": len(est),
            "estimated_len": [b - a + 1 for a, b in est],
            "lost_runs": len(lost),
            "lost_len": [b - a + 1 for a, b in lost],
            "reacquisitions": reacq,
            "film_max_gated_ratio": float(gated[:, cols].max()),
            "film_max_frame_local": int(np.unravel_index(
                np.argmax(gated[:, cols]), (n, len(cols)))[0]),
            "film_max_angle": ANGLE_NAMES[cols[int(np.unravel_index(
                np.argmax(gated[:, cols]), (n, len(cols)))[1])]],
            "film_max_status": int(S[np.unravel_index(
                np.argmax(gated[:, cols]), (n, len(cols)))[0], j]),
            "film_over_budget_frames": int((gated[:, cols] > 1.0)
                                           .any(axis=1).sum()),
        }
    return out


# --------------------------------------------------------------------------
# drawing
# --------------------------------------------------------------------------

def status_timeline(status, width, row_h=3):
    """(7 * row_h, width, 3) uint8 image: per group, status colour per
    frame, resampled to width pixels (nearest)."""
    n = len(status)
    cols = np.minimum((np.arange(width) * n) // width, n - 1)
    pal = np.array(rr.STATUS_RGB, np.uint8)
    rows = [np.repeat(pal[status[cols, g]][None], row_h, axis=0)
            for g in range(status.shape[1])]
    return np.concatenate(rows, axis=0)


def header(draw, left, right, sub=None, sub_y=None):
    """Title band at the top; the optional legend line sits low in the
    panel (sub_y) so it never covers the shoulders, which are near the
    top edge in R4-R7."""
    draw.rectangle((0, 0, rr.PANEL_SIZE[0], 30), fill=(0, 0, 0))
    rr.label(draw, (10, 6), left, 17)
    rr.label(draw, (rr.PANEL_SIZE[0] - 10, 6), right, 17, anchor="ra")
    if sub:
        rr.label(draw, (10, sub_y), sub, 14, fill=(215, 215, 215), stroke=2)


def draw_left(color_bgr, row, stamp, variant):
    img = rr.photo_panel(color_bgr)
    d = ImageDraw.Draw(img)
    px = {}
    for n in NAMES:
        u, v = row.get(f"{n}_u", np.nan), row.get(f"{n}_v", np.nan)
        px[n] = (np.array([u, v], float) * rr.CAMERA_SCALE
                 if np.isfinite(u) and np.isfinite(v) else None)
    for a, b in EDGES:
        rr.draw_segment(d, px[a], px[b], SKEL_THIN_RGB, rr.THIN_WIDTH)
    for n in NAMES:
        src = row.get(f"{n}_src", np.nan)
        if src == 0:
            rr.draw_dot(d, px[n], rr.KP_RADIUS, fill=KP_RGB)
        else:
            rr.draw_dot(d, px[n], rr.KP_RADIUS, outline=KP_RGB, width=2)
    header(d, f"Camera frame + RTMPose ({variant}) keypoints", stamp,
           "8 v1 landmarks: filled dot = depth sampled, ring = depth hole",
           rr.PANEL_SIZE[1] - 24)
    return img


def draw_right(i, rig, obj, proj_u, proj_c, timeline, cursor_x, stamp,
               smoother):
    img = rr.dark_panel()
    d = ImageDraw.Draw(img)
    S = rig["status"][i]
    col = [rr.STATUS_RGB[int(s)] for s in S]
    # object cube (camera optical)
    if obj is not None and obj["det"][i]:
        _, corners = rr.cube_geometry(obj["t_cam"][i], obj["R_cam"][i],
                                      obj["cube_m"])
        rr.draw_cube(d, proj_c(corners))
    # torso quadrilateral (root status)
    T = {n: proj_u(rig["torso"][n][i]) for n in NAMES}
    for a, b in TORSO:
        rr.draw_segment(d, T[a], T[b], col[GIDX["root"]], rr.TORSO_WIDTH)
    for n in ("left_hip", "right_hip"):
        rr.draw_dot(d, T[n], rr.JOINT_RADIUS - 2, fill=col[GIDX["root"]])
    # arms from FK
    for side in ("right", "left"):
        sw, tw, el = (GIDX[g] for g in SIDE_GROUPS[side])
        c_up = col[sw]
        c_fore = rr.STATUS_RGB[int(max(S[tw], S[el]))]
        sh = T[f"{side}_shoulder"]
        elb = proj_u(rig["elbow"][side][i])
        wr = proj_u(rig["wrist"][side][i])
        mw = proj_c(rig["meas_wrist_cam"][side][i])
        rr.draw_dot(d, mw, 7, outline=rr.REF_DOT_RGB, width=2)
        rr.draw_segment(d, sh, elb, c_up, rr.BONE_WIDTH)
        rr.draw_segment(d, elb, wr, c_fore, rr.BONE_WIDTH)
        rr.draw_dot(d, sh, rr.JOINT_RADIUS, fill=col[GIDX["root"]])
        rr.draw_dot(d, elb, rr.JOINT_RADIUS, fill=c_up)
        rr.draw_dot(d, wr, rr.JOINT_RADIUS, fill=c_fore)
    header(d, f"V3 rig: S2 + {smoother}, 13 angles -> FK", stamp,
           "white measured, amber estimated, red lost; grey ring = "
           "measured wrist; blue = ArUco cube", rr.PANEL_SIZE[1] - 82)
    # status chips
    W, H = rr.PANEL_SIZE
    chip_w, chip_h, y0 = 100, 22, H - 58
    x0 = (W - 7 * chip_w - 6 * 6) // 2
    for g in range(7):
        x = x0 + g * (chip_w + 6)
        d.rectangle((x, y0, x + chip_w, y0 + chip_h), fill=col[g])
        rr.label(d, (x + chip_w // 2, y0 + chip_h // 2), CHIP_LABELS[g], 13,
                 fill=(0, 0, 0), anchor="mm")
    # timeline with cursor
    ty = H - 28
    tl = Image.fromarray(timeline)
    img.paste(tl, (10, ty))
    d.line([(10 + cursor_x, ty - 3), (10 + cursor_x, ty + timeline.shape[0] + 2)],
           fill=(0, 200, 255), width=2)
    return img


def compose(left, right):
    out = Image.new("RGB", (2 * rr.PANEL_SIZE[0], rr.PANEL_SIZE[1]))
    out.paste(left, (0, 0))
    out.paste(right, (rr.PANEL_SIZE[0], 0))
    d = ImageDraw.Draw(out)
    d.line([(rr.PANEL_SIZE[0], 0), (rr.PANEL_SIZE[0], rr.PANEL_SIZE[1])],
           fill=rr.BORDER, width=2)
    return out


def contact_sheet(tiles, title, path):
    """tiles: list of (caption, PIL composite). 2 columns x 4 rows of
    half-size composites with a caption band; saved as a 256-colour
    PNG; the tile is shrunk further if the file exceeds the size cap."""
    tw, th = CONTACT_TILE
    for shrink in (1.0, 0.85, 0.7, 0.6):
        w, h = int(tw * shrink), int(th * shrink)
        cap = 22
        sheet = Image.new("RGB", (2 * w, 36 + 4 * (h + cap)), (0, 0, 0))
        d = ImageDraw.Draw(sheet)
        rr.label(d, (8, 8), title, 18)
        for k, (caption, im) in enumerate(tiles):
            r, c = divmod(k, 2)
            x, y = c * w, 36 + r * (h + cap)
            rr.label(d, (x + 6, y + 3), caption, 14)
            sheet.paste(im.resize((w, h), Image.Resampling.LANCZOS),
                        (x, y + cap))
        q = sheet.quantize(colors=256, method=Image.Quantize.MEDIANCUT,
                           dither=Image.Dither.NONE)
        q.save(path, optimize=True)
        if path.stat().st_size <= CONTACT_MAX_BYTES:
            return {"tile_px": [w, h], "bytes": path.stat().st_size}
    raise RuntimeError(f"{path}: contact sheet above {CONTACT_MAX_BYTES} B")


# --------------------------------------------------------------------------
# film
# --------------------------------------------------------------------------

def ffmpeg_cmd(out_path, fps, half_speed, size):
    in_rate = fps / 2.0 if half_speed else fps
    return ["ffmpeg", "-y", "-loglevel", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{size[0]}x{size[1]}", "-framerate", f"{in_rate:g}",
            "-i", "-",
            "-r", f"{fps:g}",
            "-c:v", ENCODER["codec"], "-preset", ENCODER["preset"],
            "-crf", str(ENCODER["crf"]), "-pix_fmt", ENCODER["pix_fmt"],
            "-movflags", ENCODER["movflags"], str(out_path)]


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-count_frames", "-show_entries",
                        "stream=codec_name,pix_fmt,width,height,r_frame_rate,"
                        "nb_read_frames:format=duration", "-of", "json",
                        str(path)], capture_output=True, text=True,
                       check=True)
    j = json.loads(r.stdout)
    s = j["streams"][0]
    return {"codec": s["codec_name"], "pix_fmt": s["pix_fmt"],
            "width": int(s["width"]), "height": int(s["height"]),
            "r_frame_rate": s["r_frame_rate"],
            "frames": int(s["nb_read_frames"]),
            "duration_s": float(j["format"]["duration"])}


def make_film(label, args, cfg, pin=True, out_dir=OUT_DIR):
    from replay.bag_source import BagSource
    src = resolve(label, args.variant)
    if not src["csv"].exists():
        raise FileNotFoundError(src["csv"])
    if src["bag"] is None or not Path(src["bag"]).exists():
        raise FileNotFoundError(f"bag for {label}: {src['bag']}")
    df = pd.read_csv(src["csv"])
    frames = df["frame"].to_numpy(dtype=int)
    if not np.array_equal(frames, np.arange(len(frames))):
        raise ValueError(f"{src['csv']}: frames are not 0..n-1")
    t_csv = df["time_s"].to_numpy(float)
    period = float(np.median(np.diff(t_csv)))
    lead = int(round(LEAD_IN_S * args.fps))
    if src["window"] is not None:
        start = max(0, src["window"][0] - lead)
        stop = src["window"][1]
    else:
        start, stop = 0, len(df) - 1
    if args.start is not None:
        start = args.start
    if args.stop is not None:
        stop = args.stop
    if not (0 <= start <= stop < len(df)):
        raise ValueError(f"range {start}..{stop} outside 0..{len(df) - 1}")

    t0 = time.monotonic()
    tab = run_stack(src["csv"], cfg)
    if not np.array_equal(tab["frame"].to_numpy(dtype=int), frames):
        raise ValueError("runner frames differ from the CSV")
    rig = build_rig(tab, df, cfg)
    obj = load_object(src, frames)
    if obj is not None:
        al = aruco_source.check_alignment(obj["time_s"], t_csv)
        if not al["ok"]:
            raise ValueError(f"{label}: ArUco and V3 time_s disagree")
    intr = src["meta"]["intrinsics"]
    if any(abs(c) > 0 for c in intr["coeffs"]):
        raise ValueError("non-zero distortion: the pinhole projector "
                         "would not match rs2_project_point_to_pixel")
    proj_u = rr.unity_projector(intr)
    proj_c = rr.camera_projector(intr)

    sl = slice(start, stop + 1)
    S = rig["status"][sl]
    n = len(S)
    picks, episode = pick_contact_frames(S)
    want = {start + i: tag for tag, i in picks}
    tl_w = rr.PANEL_SIZE[0] - 20
    timeline = status_timeline(S, tl_w)
    man = json.loads(Path(cfg["paths"]["scenario_manifest"]).read_text())
    if "twist_min_bend_deg" not in man:
        raise ValueError("scenario manifest has no twist_min_bend_deg "
                         "(D-033 manifests carry it)")
    occ = occlusion_summary(
        {"A": rig["A"][sl], "status": S,
         "bend": {sd: b[sl] for sd, b in rig["bend"].items()}},
        man["teleport_budget_deg"], float(man["twist_min_bend_deg"]),
        first_valid=WARMUP_FRAMES - start)
    smoother = cfg["strategy"]["s2_quat_prediction"].get("smoother", "none")

    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = "__half" if args.half_speed else ""
    film = out_dir / f"side_by_side_{src['name']}__{args.variant}{suffix}.mp4"
    size = (2 * rr.PANEL_SIZE[0], rr.PANEL_SIZE[1])
    proc = subprocess.Popen(ffmpeg_cmd(film, args.fps, args.half_speed, size),
                            stdin=subprocess.PIPE)
    captured = {}
    max_dt = 0.0
    written = 0
    try:
        with BagSource(src["bag"], paced=False) as bag:
            for idx, t_s, color, _depth in bag.frames(stop + 1):
                if idx < start:
                    continue
                dt = abs(t_s - t_csv[idx])
                max_dt = max(max_dt, dt)
                if dt > 0.5 * period:
                    raise ValueError(f"frame {idx}: bag t {t_s:.6f} vs CSV "
                                     f"{t_csv[idx]:.6f}")
                i = idx - start
                stamp = f"frame {idx} | t {t_csv[idx]:7.3f} s"
                left = draw_left(color, df.iloc[idx], stamp, args.variant)
                right = draw_right(idx, rig, obj, proj_u, proj_c, timeline,
                                   (i * tl_w) // n, stamp, smoother)
                comp = compose(left, right)
                proc.stdin.write(comp.tobytes())
                written += 1
                if idx in want:
                    captured[idx] = comp
    finally:
        proc.stdin.close()
        rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ffmpeg exited {rc}")
    if written != n:
        raise ValueError(f"wrote {written} frames, expected {n}")
    info = probe(film)
    wall = time.monotonic() - t0

    contact = None
    if pin:
        tiles = []
        for tag, i in picks:
            f = start + i
            st = "".join("MEL"[s] for s in S[i])
            tiles.append((f"{tag}: frame {f} (status {st})", captured[f]))
        cpath = DATASET / f"phase5_side_by_side_{src['name']}.png"
        c = contact_sheet(
            tiles, f"{src['name']} ({src['stem']}), {args.variant}, "
                   f"S2 + {smoother}; status letters root R_sw R_tw R_el "
                   f"L_sw L_tw L_el (M/E/L)", cpath)
        contact = {"path": repo_rel(cpath), "sha256": sha256(cpath),
                   **c, "frames": [{"tag": t, "frame": start + i}
                                   for t, i in picks]}

    rec = {
        "name": src["name"], "kind": src["kind"], "stem": src["stem"],
        "variant": args.variant, "strategy": "s2_quat_prediction",
        "smoother": smoother,
        "csv": repo_rel(src["csv"]), "csv_sha256": sha256(src["csv"]),
        "bag": str(src["bag"]), "bag_sha256_recorded": src.get("bag_sha256"),
        "film": repo_rel(film), "film_sha256": sha256(film),
        "film_bytes": film.stat().st_size,
        "half_speed": bool(args.half_speed), "fps": args.fps,
        "source_period_s": period,
        "start": int(start), "stop": int(stop),
        "window": list(src["window"]) if src["window"] else None,
        "lead_in_frames": int(src["window"][0] - start)
        if src["window"] else 0,
        "frames": int(n), "probe": info,
        "duration_s": info["duration_s"],
        "max_abs_dt_bag_vs_csv_s": max_dt,
        "bones_m": {s: list(v) for s, v in rig["bones"].items()},
        "object": None if obj is None else {
            "detected_frames": int(obj["det"][sl].sum()),
            "cube_m": obj["cube_m"]},
        "status_fractions": status_fractions(S),
        "occlusion_episode_local": episode,
        "occlusion": occ,
        "contact_sheet": contact,
        "config_sha256": config_hash(cfg),
        "manifest": repo_rel(cfg["paths"]["scenario_manifest"]),
        "render_constants_sha256": render_constants_hash(),
        "wall_s": wall,
    }
    side = film.with_suffix(".json")
    side.write_text(json.dumps(rec, indent=1))
    print(f"[OK] {src['name']}: {n} frames {start}..{stop}, "
          f"{info['duration_s']:.2f} s, {rec['film_bytes'] / 1e6:.1f} MB, "
          f"max |dt| {max_dt * 1e3:.3f} ms, wall {wall:.0f} s -> {film}")
    return rec


def render_constants_hash():
    keys = {"encoder": ENCODER, "lead_in_s": LEAD_IN_S,
            "reacq_settle": REACQ_SETTLE_FRAMES,
            "reacq_window": REACQ_WINDOW_FRAMES,
            "panel": rr.PANEL_SIZE, "scale": rr.CAMERA_SCALE,
            "status_rgb": rr.STATUS_RGB, "bg": rr.BACKGROUND_RGB,
            "cube_rgb": rr.CUBE_RGB, "bone_w": rr.BONE_WIDTH,
            "torso_w": rr.TORSO_WIDTH, "joint_r": rr.JOINT_RADIUS}
    return hashlib.sha256(json.dumps(keys, sort_keys=True).encode()
                          ).hexdigest()


# --------------------------------------------------------------------------
# manifest and summary
# --------------------------------------------------------------------------

FILM_KEYS = ("name", "kind", "stem", "variant", "film", "film_sha256",
             "film_bytes", "duration_s", "frames", "fps", "half_speed",
             "start", "stop", "status_fractions", "config_sha256",
             "contact_sheet")


def validate_manifest(m):
    """Raise ValueError when the manifest does not follow SCHEMA."""
    for k in ("schema", "created", "git_commit", "variant", "encoder",
              "films"):
        if k not in m:
            raise ValueError(f"manifest missing {k}")
    if m["schema"] != SCHEMA:
        raise ValueError(f"schema {m['schema']} != {SCHEMA}")
    if not isinstance(m["films"], list) or not m["films"]:
        raise ValueError("manifest has no films")
    for f in m["films"]:
        miss = [k for k in FILM_KEYS if k not in f]
        if miss:
            raise ValueError(f"film {f.get('name')} missing {miss}")
        if len(f["film_sha256"]) != 64:
            raise ValueError(f"film {f['name']}: bad sha256")
        if f["frames"] <= 0 or f["duration_s"] <= 0:
            raise ValueError(f"film {f['name']}: empty")
        for g in GROUP_NAMES:
            fr = f["status_fractions"][g]
            tot = fr["measured"] + fr["estimated"] + fr["lost"]
            if abs(tot - 1.0) > 1e-9:
                raise ValueError(f"film {f['name']} {g}: fractions sum "
                                 f"{tot}")
    return True


def sidecars(variant, out_dir=OUT_DIR):
    order = RECORDING_ORDER + CLEAN_ORDER
    recs = []
    for name in order:
        for suffix in ("", "__half"):
            p = out_dir / f"side_by_side_{name}__{variant}{suffix}.json"
            if p.exists():
                recs.append(json.loads(p.read_text()))
    return recs


def write_manifest(recs, variant, path=MANIFEST):
    commit = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    films = []
    for r in recs:
        films.append({k: r[k] for k in FILM_KEYS} | {
            "csv": r["csv"], "csv_sha256": r["csv_sha256"], "bag": r["bag"],
            "window": r["window"], "lead_in_frames": r["lead_in_frames"],
            "manifest": r["manifest"],
            "render_constants_sha256": r["render_constants_sha256"],
            "max_abs_dt_bag_vs_csv_s": r["max_abs_dt_bag_vs_csv_s"],
            "probe": r["probe"], "bones_m": r["bones_m"],
            "object": r["object"]})
    m = {"schema": SCHEMA,
         "created": time.strftime("%Y-%m-%d %H:%M:%S"),
         "git_commit": commit, "variant": variant,
         "tool": "v3/tools/side_by_side.py (D-039)",
         "encoder": ENCODER,
         "note": "films are gitignored (v3/output/side_by_side/); sha256 "
                 "identifies the exact file; config_sha256 = sha256 of the "
                 "sorted-key JSON of the effective config (default.json "
                 "with the variant's scenario manifest)",
         "films": films}
    validate_manifest(m)
    path.write_text(json.dumps(m, indent=1) + "\n")
    return m


def summary_lines(recs):
    L = ["V3 M8a side-by-side films: occlusion summary (tools/side_by_side.py,"
         " D-039)",
         "Per film and group: fractions measured/estimated/lost (M/E/L, "
         "percent of rendered frames); ESTIMATED and LOST runs (count, "
         "length min/median/max frames); reacquisitions = first MEASURED "
         "frame after a non-measured run inside the film (a run that starts "
         "on the film's first frame is not counted); step = largest "
         "per-frame |angle step| of the group's angles at that frame; "
         "ratio = step / D-033 budget (twist steps at a causal elbow bend "
         f"< the manifest's twist_min_bend_deg are exempt, as in D-033); "
         f"win = largest ratio over the {REACQ_WINDOW_FRAMES} frames from "
         "the reacquisition; film max = largest gated ratio over every "
         "frame of the film (frame, angle, group status there); over = "
         "frames with a gated ratio > 1. Steps into the first "
         f"{WARMUP_FRAMES} frames of the stream (configs/bench.json "
         "latency.warmup_frames; the person entering the view) are "
         "excluded and their max ratio is printed as warmup.", ""]
    for r in recs:
        if r["half_speed"]:
            continue
        L.append(f"=== {r['name']} ({r['stem']}): frames {r['start']}.."
                 f"{r['stop']} ({r['frames']}), {r['variant']}, S2 + "
                 f"{r['smoother']}, film {r['duration_s']:.2f} s ===")
        worst = []
        wu = r["occlusion"]["_warmup"]
        if wu["first_valid_local"] > 0:
            L.append(f"  warmup: local frames < {wu['first_valid_local']} "
                     f"excluded; max gated ratio there "
                     f"{wu['warmup_max_ratio']:.2f}")
        for g in GROUP_NAMES:
            o = r["occlusion"][g]
            fr = r["status_fractions"][g]

            def rl(x):
                return (f"{len(x)} [{min(x)}/{int(np.median(x))}/{max(x)}]"
                        if x else "0")
            rq = o["reacquisitions"]
            if rq:
                b = max(rq, key=lambda q: q["gated_ratio"])
                bw = max(rq, key=lambda q: q["window_gated_ratio"])
                rtxt = (f"reacq {len(rq)}: max step {max(q['step_deg'] for q in rq):.2f}"
                        f" deg, max ratio {b['gated_ratio']:.2f} "
                        f"({b['gated_angle']} @ {r['start'] + b['frame_local']}),"
                        f" win {bw['window_gated_ratio']:.2f}")
                worst.append((b["gated_ratio"], g, b, r["start"]))
            else:
                rtxt = "reacq 0"
            L.append(f"  {g:>8} M/E/L {100 * fr['measured']:5.1f}/"
                     f"{100 * fr['estimated']:5.1f}/{100 * fr['lost']:5.1f}"
                     f"  E runs {rl(o['estimated_len'])}  L runs "
                     f"{rl(o['lost_len'])}  {rtxt}  film max "
                     f"{o['film_max_gated_ratio']:.2f} ("
                     f"{o['film_max_angle']} @ "
                     f"{r['start'] + o['film_max_frame_local']}, status "
                     f"{'MEL'[o['film_max_status']]}) over "
                     f"{o['film_over_budget_frames']}")
        tot = sum(r["occlusion"][g]["film_over_budget_frames"]
                  for g in GROUP_NAMES)
        fm = max(GROUP_NAMES,
                 key=lambda g: r["occlusion"][g]["film_max_gated_ratio"])
        fo = r["occlusion"][fm]
        if worst:
            w = max(worst, key=lambda x: x[0])
            ww = max(r["occlusion"][g]["reacquisitions"][k]["window_gated_ratio"]
                     for g in GROUP_NAMES
                     for k in range(len(r["occlusion"][g]["reacquisitions"])))
            L.append(f"  headline: at the reacquisition frame the largest step "
                     f"is {w[0]:.2f} x budget ({w[1]}, {w[2]['gated_angle']}, "
                     f"frame {w[3] + w[2]['frame_local']}, "
                     f"{w[2]['step_deg']:.2f} deg after a "
                     f"{w[2]['episode_len']}-frame episode), "
                     f"{'within' if w[0] <= 1.0 else 'ABOVE'} the D-033 "
                     f"budget; within {REACQ_WINDOW_FRAMES} frames after a "
                     f"reacquisition {ww:.2f} x; whole film "
                     f"{fo['film_max_gated_ratio']:.2f} x ({fo['film_max_angle']}"
                     f" @ {r['start'] + fo['film_max_frame_local']}, status "
                     f"{'MEL'[fo['film_max_status']]}); frames over budget "
                     f"(any group, gated) {tot}")
        else:
            L.append(f"  headline: no reacquisition inside the film; whole "
                     f"film {fo['film_max_gated_ratio']:.2f} x budget; frames "
                     f"over budget (any group, gated) {tot}")
        L.append("")
    return L


# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--recording", required=True,
                    help="label, comma list, or 'all' (R4-R7 + clean "
                         "windows)")
    ap.add_argument("--variant", default="rtmpose-l")
    ap.add_argument("--config", default=str(V3_ROOT / "configs/default.json"))
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--start", type=int, default=None,
                    help="first frame (default 0, or window start - 1 s)")
    ap.add_argument("--stop", type=int, default=None,
                    help="last frame, inclusive")
    ap.add_argument("--fps", type=float, default=30.0)
    ap.add_argument("--half-speed", action="store_true")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    ap.add_argument("--no-pin", action="store_true",
                    help="skip the contact sheet, manifest and summary")
    ap.add_argument("--summary-only", action="store_true",
                    help="rebuild the manifest and summary from the "
                         "sidecars already in --out-dir; render nothing")
    args = ap.parse_args()

    cfg = load_config(args.config, args.variant, args.manifest, args.set)
    labels = (list(RECORDING_ORDER + CLEAN_ORDER)
              if args.recording == "all" else args.recording.split(","))
    out_dir = Path(args.out_dir)
    for lab in ([] if args.summary_only else labels):
        make_film(lab, args, cfg, pin=not args.no_pin, out_dir=out_dir)
    if args.no_pin:
        return
    recs = sidecars(args.variant, out_dir)
    write_manifest(recs, args.variant)
    lines = summary_lines(recs)
    SUMMARY.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"wrote {MANIFEST}\nwrote {SUMMARY}")


if __name__ == "__main__":
    main()
