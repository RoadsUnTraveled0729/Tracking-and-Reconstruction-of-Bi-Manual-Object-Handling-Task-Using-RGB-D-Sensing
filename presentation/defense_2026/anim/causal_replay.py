#!/usr/bin/env python3
# Filename: presentation/defense_2026/anim/causal_replay.py
"""A source-grounded visualization of the saved R6b causal run.

This is an adaptation of presentation/v9/anim/video3_causal.py for the
fresh defence deck. It is not a live-camera capture or a Unity recording.
The camera frames come from Video/recording_20260831_065553.bag, the angles,
compute bars and group states from v2/output/v2_person_dump_r6b_full.csv,
and merger states from v2/output/v2_integrate_dump_r6b_full.csv. These CSVs
are saved local outputs; the run summary is pinned in
v2/dataset/r6b_probe_baseline.txt and Thesis V9 Section 8.4.

Source-clock cadence is derived from source timestamps, not wall-clock
throughput. Blue means CONSTRAINED, which may include geometry recovery or
change limiting. rec_right only establishes that an object estimate was
supplied to the solver; it does not establish actual use for a joint.
The stick figure uses the saved rig lengths, with a pinned pelvis and a
camera-facing projection. Upper arms use swing-state colour and forearms
use elbow-state colour; the chips separately report all seven groups.

The derivative preserves the original 21-second selection, frames 269-898,
and fixes labels without changing scientific code or scientific outputs.
Run with base Python: causal_replay.py all. The extract stage uses v3rt.
Temporary frame caches live under /tmp/defense_2026_causal/.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
PROVENANCE = ROOT / "presentation" / "defense_2026" / "media" / "provenance"
PERSON_CSV = PROVENANCE / "v2_person_dump_r6b_full.csv"
INTEG_CSV = PROVENANCE / "v2_integrate_dump_r6b_full.csv"
RIG_CSV = PROVENANCE / "rig_dimensions.csv"
STEM = "recording_20260831_065553"          # R6b, eval/README.md alias table
BAG = ROOT / "Video" / f"{STEM}.bag"

OUT_DIR = ROOT / "presentation" / "defense_2026" / "media"
FRAME_DIR = Path("/tmp/defense_2026_causal/frames")
CAM_DIR = Path("/tmp/defense_2026_causal/camera")
MASTER = OUT_DIR / "masters" / "causal_replay.mp4"
EMBED = OUT_DIR / "causal_replay.mp4"
POSTER = OUT_DIR / "causal_replay.png"

V3RT_PYTHON = "/home/luo/anaconda3/envs/v3rt/bin/python"

# ---------------------------------------------------------------- window
# Chosen window, justified in the task report:
#   frames 269..898 (630 frames, 20.98 s on the time_s clock) contain the
#   only long right-arm rebuild of the run, frames 550..642 (93 frames,
#   3.07 s), which is the "natural wrist gap" window of Chapter 8
#   (writing/v9/figures/ch8_compare.json, window "natural wrist gap",
#   frames 540..650). The window ends at 898 because the bag yields 899
#   aligned colour+depth pairs (indices 0..898) while the person dump has
#   900 rows; the dump's frame column is still consecutive with no gaps.
START_FRAME = 269
DURATION_S = 21.0
NOMINAL_FPS = 30                            # recorded nominal rate; the
                                            # measured mean over the window
                                            # is 29.98 fps from time_s

# --------------------------------------------------------------- palette
ACCENT = (36, 104, 218)                      # fresh deck blue
PAGE = (247, 249, 252)
WHITE = (255, 255, 255)
BORDER = (198, 202, 208)
INK = (21, 35, 50)
MUTED = (112, 118, 126)
GRID = (226, 229, 233)
C_MEASURED = (96, 108, 120)
C_HELD = (199, 129, 29)
C_CONSTR = ACCENT
C_INTERP = (140, 162, 188)
C_BLEND = (118, 86, 150)
FILL_MEASURED = (242, 244, 246)
FILL_HELD = (252, 238, 218)
FILL_CONSTR = (221, 229, 241)

# Group order and the 0/1/2 encoding: v2/common/person_shm_v2.py L15-21
GROUP_NAMES = ["root", "R swing", "R twist", "R elbow",
               "L swing", "L twist", "L elbow"]
TAG_WORDS = {0: "measured", 1: "held", 2: "constrained"}
TAG_COLOUR = {0: C_MEASURED, 1: C_HELD, 2: C_CONSTR}
TAG_FILL = {0: FILL_MEASURED, 1: FILL_HELD, 2: FILL_CONSTR}
# Merger states: v2/integration/v2_integrate.py L97
STATE_WORDS = {0: "measured", 1: "interpolated", 2: "held", 3: "blended"}
STATE_COLOUR = {0: C_MEASURED, 1: C_INTERP, 2: C_HELD, 3: C_BLEND}

# 30 fps budget, v2/dataset/r6b_probe_baseline.txt ("30 fps budget 33.3 ms")
BUDGET_MS = 1000.0 / 30.0
STRIP_N = 90                                # scrolling strip length, frames

# Caption quote, verbatim reading of Thesis V9 Section 8.4: "the causal
# structure consumed all 900 frames of the recording at its recorded pace,
# sustaining about 29 frames per second, with none dropped".
CAPTION = ("Logged causal run, replayed. Source-clock cadence is not throughput. "
           "Thesis Sec. 8.4: about 29 fps over 900 frames, none dropped.")

# ---------------------------------------------------------------- canvas
W, H = 1920, 1080
MARGIN = 14
COL_W = 936
COL_X = (MARGIN, MARGIN + COL_W + 20)
ROW1_Y, ROW1_H = 14, 592
ROW2_Y, ROW2_H = 620, 376
CAP_Y, CAP_H = 1010, 70
TITLE_H = 34

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_PATH_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_FONTS: dict = {}


def font(size, bold=False):
    key = (size, bold)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(
            FONT_PATH_B if bold else FONT_PATH, size)
    return _FONTS[key]


# ------------------------------------------------------------ kinematics
# Rotation helpers copied (not imported) from v1/kinematics/shoulder.py
# L30-42 and eval/offset/carry.py L32-41; v1/ and eval/ are read-only.
def _rx(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def _ry(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def _rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def recompose_zxy(deg):
    """Unity ZXY-applied Euler degrees -> R = Ry.Rx.Rz (carry.py L32-41)."""
    x, y, z = np.radians(np.asarray(deg, float))
    return _ry(y) @ _rx(x) @ _rz(z)


def arm_dirs(sh_deg, elb_deg, side):
    """Root-basis unit directions of upper arm and forearm.

    Copied from eval/inspect/check_v1_overlay.py L47-66 (fk_arm_dirs).
    """
    ty, tz, tau = np.radians(np.asarray(sh_deg, float))
    ey, ez = np.radians(np.asarray(elb_deg, float))
    if side == "right":
        rsw = _ry(ty) @ _rz(tz)
        rarm = rsw @ _rx(tau)
        upper = rsw @ np.array([1.0, 0, 0])
        fore = rarm @ (_ry(ey) @ _rz(ez) @ np.array([1.0, 0, 0]))
    else:
        rsw = _ry(-ty) @ _rz(-tz)
        rarm = rsw @ _rx(tau)
        upper = rsw @ np.array([-1.0, 0, 0])
        fore = rarm @ (_ry(-ey) @ _rz(-ez) @ np.array([-1.0, 0, 0]))
    return upper, fore


def rig_lengths():
    """Segment lengths of the rig used for this recording, in metres."""
    d = pd.read_csv(RIG_CSV).set_index("segment")["meters"].to_dict()
    return {
        "shoulder_width": float(d["shoulder_width"]),
        "torso": float(d["torso_hip_to_midshoulder"]),
        "upper_R": float(d["upper_arm_R"]),
        "fore_R": float(d["forearm_R"]),
        "upper_L": float(d["upper_arm_L"]),
        "fore_L": float(d["forearm_L"]),
    }


def skeleton(angles, rig):
    """Joint positions in the root frame, pelvis at the origin.

    angles: (N, 13) PSA5 rows a0..a12 of the person dump. Returns a dict of
    (N, 3) arrays for pelvis, mid, shoulder_R/L, elbow_R/L, wrist_R/L and
    the head centre.
    """
    n = len(angles)
    out = {k: np.zeros((n, 3)) for k in
           ("pelvis", "mid", "shR", "shL", "elR", "elL",
            "wrR", "wrL", "head")}
    half = rig["shoulder_width"] / 2.0
    for i in range(n):
        rot = recompose_zxy(angles[i, :3])
        mid = rot @ np.array([0.0, rig["torso"], 0.0])
        sh_r = mid + rot @ np.array([half, 0.0, 0.0])
        sh_l = mid + rot @ np.array([-half, 0.0, 0.0])
        up_r, fo_r = arm_dirs(angles[i, 3:6], angles[i, 6:8], "right")
        up_l, fo_l = arm_dirs(angles[i, 8:11], angles[i, 11:13], "left")
        el_r = sh_r + rig["upper_R"] * (rot @ up_r)
        el_l = sh_l + rig["upper_L"] * (rot @ up_l)
        out["mid"][i] = mid
        out["shR"][i] = sh_r
        out["shL"][i] = sh_l
        out["elR"][i] = el_r
        out["elL"][i] = el_l
        out["wrR"][i] = el_r + rig["fore_R"] * (rot @ fo_r)
        out["wrL"][i] = el_l + rig["fore_L"] * (rot @ fo_l)
        out["head"][i] = mid + rot @ np.array([0.0, 0.16, 0.0])
    return out


# ------------------------------------------------------------ primitives
def panel(draw, x, y, w, h, title):
    """White panel with a thin grey border and a plain-word title."""
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=WHITE, outline=BORDER)
    draw.text((x + 14, y + 9), title, font=font(21, True), fill=ACCENT)
    draw.line([(x + 14, y + TITLE_H - 3), (x + w - 14, y + TITLE_H - 3)],
              fill=GRID, width=1)
    return x + 14, y + TITLE_H + 4, w - 28, h - TITLE_H - 16


def text_w(s, f):
    return f.getbbox(s)[2] - f.getbbox(s)[0]


def chip(draw, x, y, w, h, name, state):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=5,
                           fill=TAG_FILL[state], outline=TAG_COLOUR[state],
                           width=2 if state == 2 else 1)
    draw.text((x + 8, y + 6), name, font=font(13), fill=MUTED)
    draw.text((x + 8, y + 24), TAG_WORDS[state], font=font(15, True),
              fill=TAG_COLOUR[state])


# ---------------------------------------------------------------- panels
def draw_camera(img, draw, cam_path, frame_no, box):
    x, y, w, h = box
    draw.text((x, y + 2), f"{STEM}.bag, colour, frame {frame_no}",
              font=font(15), fill=MUTED)
    top = y + 24
    area_h = h - 24
    if cam_path is not None and cam_path.exists():
        src = Image.open(cam_path).convert("RGB")
        scale = min(w / src.width, area_h / src.height)
        new = (int(src.width * scale), int(src.height * scale))
        src = src.resize(new, Image.LANCZOS)
        px = x + (w - new[0]) // 2
        py = top + (area_h - new[1]) // 2
        img.paste(src, (px, py))
        draw.rectangle([px, py, px + new[0] - 1, py + new[1] - 1],
                       outline=BORDER)
    else:
        draw.text((x + 10, top + area_h // 2 - 10),
                  "colour frame not available in this build",
                  font=font(20), fill=MUTED)


def draw_reconstruction(draw, sk, i, tags, rec_right, box, extent):
    x, y, w, h = box
    draw.text((x, y + 2),
              "solved angles a0..a12, camera-facing view, pelvis pinned",
              font=font(15), fill=MUTED)
    top = y + 24
    area_h = h - 24 - 54
    (xmin, xmax, ymin, ymax) = extent
    scale = min(w / (xmax - xmin), area_h / (ymax - ymin))
    ox = x + (w - (xmax - xmin) * scale) / 2.0
    oy = top + (area_h - (ymax - ymin) * scale) / 2.0

    def pt(p):
        # Root-frame x maps straight to screen x, which puts the subject's
        # right arm on the viewer's left, the same side as in the camera
        # panel. y is up in the root frame and down on screen.
        return (ox + (p[0] - xmin) * scale,
                oy + (ymax - p[1]) * scale)

    # ground line at the pelvis height
    py = pt(sk["pelvis"][i])[1]
    draw.line([(x, py), (x + w, py)], fill=GRID, width=1)

    # Blue means CONSTRAINED, which does not by itself prove object recovery.
    # rec_right reports an available object estimate, not its actual use.
    # Source: v2/person/v2_person.py dump_rows construction.
    # Right wrist trail, last 45 frames, coloured by the right-elbow tag.
    trail0 = max(0, i - 45)
    for j in range(trail0, i + 1):
        c = C_CONSTR if tags[j, 3] == 2 else (170, 176, 184)
        r = 2 if tags[j, 3] != 2 else 3
        cx, cy = pt(sk["wrR"][j])
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)

    torso = [pt(sk["pelvis"][i]), pt(sk["mid"][i])]
    draw.line(torso, fill=INK, width=7)
    draw.line([pt(sk["shR"][i]), pt(sk["shL"][i])], fill=INK, width=7)
    hx, hy = pt(sk["head"][i])
    hr = 0.085 * scale
    draw.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], outline=INK, width=5)

    def arm(sh, el, wr, tag_sw, tag_el):
        c_up = TAG_COLOUR[int(tag_sw)]
        c_fo = TAG_COLOUR[int(tag_el)]
        lw_up = 9 if tag_sw == 2 else 7
        lw_fo = 9 if tag_el == 2 else 7
        draw.line([pt(sh), pt(el)], fill=c_up, width=lw_up)
        draw.line([pt(el), pt(wr)], fill=c_fo, width=lw_fo)
        for p, r in ((sh, 6), (el, 6), (wr, 8)):
            cx, cy = pt(p)
            draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c_fo)

    # Upper-arm direction is the swing; the forearm uses the elbow state.
    # Twist states remain separately visible in the seven group chips.
    arm(sk["shL"][i], sk["elL"][i], sk["wrL"][i], tags[i, 4], tags[i, 6])
    arm(sk["shR"][i], sk["elR"][i], sk["wrR"][i], tags[i, 1], tags[i, 3])

    # legend and status
    ly = y + h - 48
    items = [("measured", C_MEASURED), ("held", C_HELD),
             ("constrained", C_CONSTR)]
    lx = x
    for label, col in items:
        draw.line([(lx, ly + 8), (lx + 26, ly + 8)], fill=col, width=6)
        draw.text((lx + 32, ly), label, font=font(15), fill=INK)
        lx += 32 + text_w(label, font(15)) + 26
    if tags[i, 3] == 2 and rec_right[i] == 1:
        msg, col = ("right elbow constrained; object estimate supplied", ACCENT)
    elif rec_right[i] == 1:
        msg, col = ("object estimate supplied; see group states below", MUTED)
    else:
        msg, col = "no object estimate supplied; see group states below", MUTED
    draw.text((x, ly + 24), msg, font=font(16, True), fill=col)


def draw_landmark(draw, i, compute, tags, rec_right, box):
    x, y, w, h = box
    draw.text((x, y + 2),
              f"per-frame compute of the last {STRIP_N} frames (ms), "
              f"30 fps budget {BUDGET_MS:.1f} ms",
              font=font(15), fill=MUTED)
    now = f"compute now: {float(compute[i]):5.2f} ms"
    draw.text((x + w - text_w(now, font(17, True)), y), now,
              font=font(17, True), fill=INK)
    top = y + 24
    bar_h = 176
    full_ms = 36.0
    base = top + bar_h
    draw.line([(x, base), (x + w, base)], fill=BORDER, width=1)
    by = base - bar_h * (BUDGET_MS / full_ms)
    for seg in range(0, w, 12):
        draw.line([(x + seg, by), (x + min(seg + 7, w), by)],
                  fill=C_HELD, width=2)
    draw.text((x + w - 108, by + 4), f"{BUDGET_MS:.1f} ms",
              font=font(14), fill=C_HELD)

    step = w / float(STRIP_N)
    bw = max(3.0, step - 2.2)
    for k in range(STRIP_N):
        j = i - (STRIP_N - 1 - k)
        if j < 0:
            continue
        v = float(compute[j])
        bh = max(1.0, bar_h * min(v, full_ms) / full_ms)
        bx = x + k * step
        col = C_CONSTR if tags[j, 3] == 2 else (158, 166, 176)
        draw.rectangle([bx, base - bh, bx + bw, base], fill=col)
    cy = base + 16
    cw, cgap = 124, 4
    for g in range(7):
        chip(draw, x + g * (cw + cgap), cy, cw, 50,
             GROUP_NAMES[g], int(tags[i, g]))
    if tags[i, 3] == 2 and rec_right[i] == 1:
        msg, col = ("right elbow constrained; object estimate supplied"), ACCENT
    elif rec_right[i] == 1:
        msg, col = ("object estimate supplied; group states describe the solve"), MUTED
    else:
        msg, col = "no object estimate supplied; group states describe the solve", MUTED
    draw.text((x, cy + 58), msg, font=font(16, True), fill=col)


def draw_merger(draw, tick_idx, p_state, o_state, box,
                frame_no, fps_roll, dropped, ticks, clip_t):
    x, y, w, h = box
    draw.text((x, y + 2),
              f"merger stream, last {STRIP_N} ticks",
              font=font(15), fill=MUTED)
    top = y + 26
    rows = (("person", p_state), ("object", o_state))
    for r, (label, arr) in enumerate(rows):
        ry = top + r * 34
        draw.text((x, ry + 4), label, font=font(14), fill=MUTED)
        x0 = x + 58
        rw = w - 58
        rstep = rw / float(STRIP_N)
        rcw = max(3.0, rstep - 1.2)
        for k in range(STRIP_N):
            j = tick_idx - (STRIP_N - 1 - k)
            if j < 0:
                continue
            col = STATE_COLOUR[int(arr[j])]
            draw.rectangle([x0 + k * rstep, ry, x0 + k * rstep + rcw,
                            ry + 22], fill=col)
    ly = top + 72
    lx = x
    for code in (0, 1, 2, 3):
        draw.rectangle([lx, ly, lx + 16, ly + 12], fill=STATE_COLOUR[code])
        draw.text((lx + 22, ly - 3), STATE_WORDS[code], font=font(14),
                  fill=MUTED)
        lx += 22 + text_w(STATE_WORDS[code], font(14)) + 20

    ty = ly + 28
    lines = [
        (f"frame {frame_no}", True),
        (f"source-clock cadence: {fps_roll:.2f} fps", True),
        (f"dropped frames in window: {dropped}", True),
        (f"ticks: {ticks}", True),
    ]
    col_x = (x, x + 460)
    for n, (line, bold) in enumerate(lines):
        draw.text((col_x[n % 2], ty + (n // 2) * 30), line,
                  font=font(22, bold), fill=INK)
    draw.text((x, ty + 64), f"clip time {clip_t:5.2f} s",
              font=font(16), fill=MUTED)


# ---------------------------------------------------------------- stages
def stage_extract(start, count, force=False):
    """Cache the window's colour frames as JPEG. Needs pyrealsense2."""
    CAM_DIR.mkdir(parents=True, exist_ok=True)
    wanted = [CAM_DIR / f"cam_{f:06d}.jpg" for f in range(start, start + count)]
    if not force and all(p.exists() for p in wanted):
        print(f"[extract] cache complete: {len(wanted)} frames")
        return
    sys.path.insert(0, str(ROOT / "v3" / "replay"))
    from bag_source import BagSource                      # noqa: E402
    import cv2                                            # noqa: E402
    last = start + count - 1
    n = 0
    with BagSource(str(BAG), paced=False) as src:
        for idx, _t, color, _depth in src.frames():
            if idx > last:
                break
            if idx >= start:
                cv2.imwrite(str(CAM_DIR / f"cam_{idx:06d}.jpg"), color,
                            [int(cv2.IMWRITE_JPEG_QUALITY), 95])
                n += 1
    print(f"[extract] wrote {n} colour frames to {CAM_DIR}")


def load_logs():
    person = pd.read_csv(PERSON_CSV)
    integ = pd.read_csv(INTEG_CSV)
    return person, integ


def stage_render(start, count):
    person, integ = load_logs()
    frames = person["frame"].to_numpy(int)
    time_s = person["time_s"].to_numpy(float)
    compute = person["compute_ms"].to_numpy(float)
    tags = person[[f"tag_{g}" for g in range(7)]].to_numpy(int)
    rec_right = person["rec_right"].to_numpy(int)
    angles = person[[f"a{k}" for k in range(13)]].to_numpy(float)
    tau = integ["tau"].to_numpy(float)
    p_state = integ["p_state"].to_numpy(int)
    o_state = integ["o_state"].to_numpy(int)
    ticks_col = integ["tick"].to_numpy(int)

    end = start + count
    win = np.arange(start, end)
    # dropped frames in the window, from the frame column alone
    dropped = int((np.diff(frames[start:end]) - 1).sum())

    # Fixed drawing extent over the window, so the figure never jumps scale.
    rig = rig_lengths()
    sk = skeleton(angles, rig)
    joints = ("pelvis", "mid", "shR", "shL", "elR", "elL",
              "wrR", "wrL", "head")
    xs = np.concatenate([sk[k][start:end, 0] for k in joints])
    ys = np.concatenate([sk[k][start:end, 1] for k in joints])
    pad = 0.09
    extent = (xs.min() - pad, xs.max() + pad, ys.min() - pad, ys.max() + pad)

    missing = [int(frames[i]) for i in win
               if not (CAM_DIR / f"cam_{frames[i]:06d}.jpg").exists()]
    if missing:
        raise RuntimeError(f"Missing camera frames: {missing[:5]}; run extract first")
    if FRAME_DIR.exists():
        shutil.rmtree(FRAME_DIR)
    FRAME_DIR.mkdir(parents=True, exist_ok=True)

    t0 = time_s[start]
    for out_i, i in enumerate(win):
        img = Image.new("RGB", (W, H), PAGE)
        draw = ImageDraw.Draw(img)

        box = panel(draw, COL_X[0], ROW1_Y, COL_W, ROW1_H, "Camera")
        draw_camera(img, draw, CAM_DIR / f"cam_{frames[i]:06d}.jpg",
                    int(frames[i]), box)

        box = panel(draw, COL_X[1], ROW1_Y, COL_W, ROW1_H, "Reconstruction")
        draw_reconstruction(draw, sk, int(i), tags, rec_right, box, extent)

        box = panel(draw, COL_X[0], ROW2_Y, COL_W, ROW2_H, "Landmark branch")
        draw_landmark(draw, int(i), compute, tags, rec_right, box)

        # rolling frame rate over the last 30 frames of the recording clock
        fps_roll = 30.0 / (time_s[i] - time_s[i - 30])
        tick_idx = int(np.searchsorted(tau, time_s[i], side="right")) - 1
        tick_idx = max(0, min(tick_idx, len(tau) - 1))
        ticks = int(ticks_col[tick_idx]) + 1
        box = panel(draw, COL_X[1], ROW2_Y, COL_W, ROW2_H, "Merger")
        draw_merger(draw, tick_idx, p_state, o_state, box,
                    int(frames[i]), fps_roll, dropped, ticks,
                    float(time_s[i] - t0))

        draw.rectangle([0, CAP_Y, W - 1, H - 1], fill=ACCENT)
        f = font(21)
        draw.text(((W - text_w(CAPTION, f)) / 2, CAP_Y + 23), CAPTION,
                  font=f, fill=WHITE)

        img.save(FRAME_DIR / f"f{out_i:05d}.png")
        if out_i % 100 == 0:
            print(f"[render] {out_i}/{count}")
    print(f"[render] {count} frames -> {FRAME_DIR}")


def run(cmd):
    print("[cmd]", " ".join(str(c) for c in cmd))
    subprocess.run([str(c) for c in cmd], check=True)


def stage_encode(fps, poster_offset):
    MASTER.parent.mkdir(parents=True, exist_ok=True)
    EMBED.parent.mkdir(parents=True, exist_ok=True)
    POSTER.parent.mkdir(parents=True, exist_ok=True)
    run(["ffmpeg", "-y", "-framerate", fps, "-start_number", 0,
         "-i", FRAME_DIR / "f%05d.png",
         "-c:v", "libx264", "-preset", "slow", "-crf", 20,
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", MASTER])
    run(["ffmpeg", "-y", "-i", MASTER,
         "-vf", "scale=1280:720:flags=lanczos",
         "-c:v", "libx264", "-preset", "slow", "-crf", 26,
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", EMBED])
    shutil.copyfile(FRAME_DIR / f"f{poster_offset:05d}.png", POSTER)
    print(f"[poster] frame offset {poster_offset} -> {POSTER}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("stage", choices=["extract", "render", "encode", "all"])
    ap.add_argument("--start-frame", type=int, default=START_FRAME)
    ap.add_argument("--duration", type=float, default=DURATION_S,
                    help="clip duration in seconds at the nominal rate")
    ap.add_argument("--fps", type=int, default=NOMINAL_FPS)
    ap.add_argument("--poster-frame", type=int, default=596,
                    help="absolute dump frame used for the poster; the "
                         "default sits inside the rebuild 550..642")
    ap.add_argument("--force-extract", action="store_true")
    args = ap.parse_args()

    count = int(round(args.duration * args.fps))
    if args.stage == "extract":
        stage_extract(args.start_frame, count, args.force_extract)
        return
    if args.stage == "render":
        stage_render(args.start_frame, count)
        return
    if args.stage == "encode":
        stage_encode(args.fps, args.poster_frame - args.start_frame)
        return
    if os.path.exists(V3RT_PYTHON):
        run([V3RT_PYTHON, __file__, "extract",
             "--start-frame", args.start_frame, "--duration", args.duration,
             "--fps", args.fps])
    else:
        print(f"[warn] {V3RT_PYTHON} missing; camera panels will be blank")
    stage_render(args.start_frame, count)
    stage_encode(args.fps, args.poster_frame - args.start_frame)


if __name__ == "__main__":
    main()
