#!/usr/bin/env python3
"""Explain the real V2 record layouts, resampling and guarded Unity reads.

The bytes and reader/writer steps are traced to the sources in SOURCE_FILES.
Drawing widths are not to byte scale. Sample values, animation timing and
sequence values 10/11/12 are illustrative. This is not a measured schedule or a proof of
memory ordering on every platform. All labels are ASCII and measured before
drawing. The two race cases are independent examples, explicitly labelled.

Run: /home/luo/anaconda3/bin/python presentation/defense_2026/anim/memory_records.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import subprocess
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
OUT = HERE / "media"
REVIEW = HERE / "review"
W, H = 1600, 900
SIZE = (1280, 720)
DURATION, FPS, MP4_FPS = 44, 10, 30
BG, WHITE = "#F7F9FC", "#FFFFFF"
INK, MUTED, LINE = "#152332", "#536477", "#CAD4E1"
BLUE, TEAL, AMBER, RED, PURPLE = "#2468DA", "#178A85", "#B36D15", "#AD393B", "#7753A3"
PALE = {BLUE: "#EAF1FD", TEAL: "#E3F4F1", AMBER: "#FBF0DF",
        RED: "#FBEAEC", PURPLE: "#F0EAF7", INK: "#EBEFF4", MUTED: "#F1F3F6"}
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
CHECKS, MIN_FONT = 0, 100
REDUCTIONS = set()
TEXT_COMMANDS, MOVING_AREAS = [], []
TEXT_LAYER = 0
HIDDEN_LABELS = 0
SEGMENT = None
PARTS = [
    {"name": "memory_layout", "start": 0, "duration": 18,
     "title": "Image and pose record layouts", "stages": [0, 1]},
    {"name": "memory_combine", "start": 18, "duration": 10,
     "title": "Resampling and combined-record construction", "stages": [2, 3]},
    {"name": "memory_race", "start": 28, "duration": 16,
     "title": "Python / Unity shared-memory consistency checks", "stages": [4]},
]
SOURCE_FILES = [
    "v2/common/shm_ring.py", "v2/common/person_shm_v2.py",
    "v1/realtime/integration/realtime_integrate.py",
    "v2/integration/v2_integrate.py",
    "Unity/Assets/Scripts/IntegratedSceneReceiverV2.cs",
]
FORMATS = {
    "PSF1_global": ("<IIIIiiIdd4f5fiII", 92, 128),
    "PSF1_slot_header": ("<IiIdd", 28, 32),
    "PSR2": ("<IIif3f13fHH", 84, 84),
    "PSB2": ("<IIif3f3fH2x", 44, 44),
    "PSI2": ("<IIif3f13f3f3fHHHH", 112, 112),
}


@lru_cache(maxsize=100)
def font(size, bold=False, mono=False):
    name = "DejaVuSansMono" if mono else "DejaVuSans"
    return ImageFont.truetype(str(FONT_DIR / (name + ("-Bold" if bold else "") + ".ttf")), size)


def fit(d, rect, value, size=28, color=INK, bold=False, mono=False,
        align="center", minimum=22):
    """Measure each label and assert its complete glyph bounds stay in rect."""
    global CHECKS, MIN_FONT
    assert value.isascii(), value
    x0, y0, x1, y1 = rect
    assert 0 <= x0 <= x1 <= W and 0 <= y0 <= y1 <= H, rect
    for chosen in range(size, minimum - 1, -1):
        f = font(chosen, bold, mono)
        box = d.multiline_textbbox((0, 0), value, font=f, spacing=7, align=align)
        tw, th = box[2] - box[0], box[3] - box[1]
        if tw <= x1 - x0 and th <= y1 - y0:
            break
    else:
        raise ValueError(f"Label does not fit {rect}: {value!r}")
    x = x0 if align == "left" else x0 + (x1 - x0 - tw) / 2
    y = y0 + (y1 - y0 - th) / 2
    xy = (x - box[0], y - box[1])
    actual = d.multiline_textbbox(xy, value, font=f, spacing=7, align=align)
    assert actual[0] >= x0 - .01 and actual[1] >= y0 - .01, (value, actual, rect)
    assert actual[2] <= x1 + .01 and actual[3] <= y1 + .01, (value, actual, rect)
    # Draw text after all moving rectangles are known. A partially occluded
    # background label is suppressed in full, avoiding stray glyph fragments.
    TEXT_COMMANDS.append((d, xy, value, f, color, align, actual, TEXT_LAYER))
    CHECKS += 1
    MIN_FONT = min(MIN_FONT, chosen)
    if chosen != size:
        REDUCTIONS.add((value, size, chosen))


def panel(d, rect, color=LINE, fill=WHITE, width=2, radius=10):
    d.rounded_rectangle(rect, radius=radius, fill=fill, outline=color, width=width)


def cell(d, rect, top, bottom, color=BLUE, active=True, size=28):
    x0, y0, x1, y1 = rect
    panel(d, rect, color if active else LINE, PALE[color] if active else WHITE)
    fit(d, (x0+10, y0+9, x1-10, y0+(y1-y0)*.54), top, size, color, True)
    fit(d, (x0+10, y0+(y1-y0)*.56, x1-10, y1-9), bottom, 23, MUTED)


def arrow(d, a, b, color=LINE, width=4):
    d.line((a, b), fill=color, width=width)
    th = math.atan2(b[1]-a[1], b[0]-a[0])
    d.polygon([b, (b[0]-13*math.cos(th-.5), b[1]-13*math.sin(th-.5)),
               (b[0]-13*math.cos(th+.5), b[1]-13*math.sin(th+.5))], fill=color)


def centre(rect):
    return ((rect[0]+rect[2])/2, (rect[1]+rect[3])/2)


def moving(d, source, target, u, title, detail, color, width=260, height=82):
    global TEXT_LAYER
    u = max(0, min(1, u))
    u = u*u*(3-2*u)
    a, b = centre(source), centre(target)
    x, y = a[0]+u*(b[0]-a[0]), a[1]+u*(b[1]-a[1])
    rect = (x-width/2, y-height/2, x+width/2, y+height/2)
    MOVING_AREAS.append(rect)
    TEXT_LAYER = len(MOVING_AREAS)
    cell(d, rect, title, detail, color, size=26)
    TEXT_LAYER = 0


def draw_labels():
    """Prevent moving tiles from exposing fragments of underlying labels."""
    global HIDDEN_LABELS
    for d, xy, value, f, color, align, bounds, layer in TEXT_COMMANDS:
        covered = any(
            bounds[0] < rect[2]+2 and bounds[2] > rect[0]-2 and
            bounds[1] < rect[3]+2 and bounds[3] > rect[1]-2
            for i, rect in enumerate(MOVING_AREAS, start=1) if i > layer)
        if covered:
            HIDDEN_LABELS += 1
        else:
            d.multiline_text(xy, value, font=f, fill=color, spacing=7, align=align)


def base(t, stage, subtitle):
    global TEXT_COMMANDS, MOVING_AREAS, TEXT_LAYER
    TEXT_COMMANDS, MOVING_AREAS, TEXT_LAYER = [], [], 0
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    title = SEGMENT["title"] if SEGMENT else "Shared-memory records: extraction, resampling and safe reads"
    fit(d, (48, 25, 1552, 82), title, 42, INK, True, align="left")
    fit(d, (48, 91, 1552, 121), subtitle, 27, MUTED, align="left")
    labels = ["IMAGE SLOT", "EXTRACT FIELDS", "RESAMPLE", "PACK PSI2", "READ SAFELY"]
    stages = SEGMENT["stages"] if SEGMENT else list(range(5))
    active = stages.index(stage)
    chosen_labels = [labels[s] for s in stages]
    if SEGMENT and SEGMENT["name"] == "memory_race":
        chosen_labels = ["ODD AT START", "WRITE DURING READ", "RETRY + VERIFY"]
        active = 0 if t < 31 else 1 if t < 38 else 2
    nav_width = 1510/len(chosen_labels)
    for i, label in enumerate(chosen_labels):
        x0, x1 = 48+i*nav_width, 48+(i+1)*nav_width-8
        panel(d, (x0, 140, x1, 181), BLUE if i == active else LINE,
              PALE[BLUE] if i == active else WHITE, 2, 7)
        fit(d, (x0+7, 148, x1-7, 173), str(i+1)+"  "+label, 23, BLUE if i == active else MUTED, i == active)
    fit(d, (48, 850, 1552, 876),
        "SCHEMATIC: drawing widths are not to byte scale; timing and sequence examples are illustrative.  V9 6.1/6.5; V2 + Unity.",
        21, MUTED, align="left", minimum=21)
    d.rectangle((0, 893, W, 899), fill=LINE)
    progress = (t-SEGMENT["start"])/SEGMENT["duration"] if SEGMENT else t/DURATION
    d.rectangle((0, 893, W*max(0, min(progress, 1)), 899), fill=BLUE)
    return im, d


def caption(d, first, second="", color=INK):
    panel(d, (48, 744, 1552, 832), LINE, WHITE)
    fit(d, (68, 756, 1532, 787), first, 29, color, True)
    if second:
        fit(d, (68, 793, 1532, 819), second, 25, MUTED)


def image_slot(t):
    im, d = base(t, 0, "PSF1: global configuration, then an eight-slot ring of image frames")
    fit(d, (50, 202, 1550, 235), "Global header: 128 B, including PSF1 magic, image dimensions and colour format", 29, INK, True)
    fit(d, (50, 242, 1550, 269), "One selected slot: 32 B metadata + colour bytes + depth bytes", 27, MUTED)
    sequence = "seq = 10" if t < 1.1 else "seq = 11" if t < 3.65 else "seq = 12"
    seqcolor = AMBER if 1.1 <= t < 3.65 else TEAL
    fields = [
        ((60, 284, 310, 378), sequence, "0: u32", seqcolor),
        ((326, 284, 556, 378), "frame n", "4: i32", BLUE),
        ((572, 284, 782, 378), "pad", "8: u32", MUTED),
        ((798, 284, 1068, 378), "hardware time", "12: f64, ms", PURPLE),
        ((1084, 284, 1364, 378), "monotonic time", "20: f64, seconds", PURPLE),
        ((1380, 284, 1540, 378), "reserved", "28-31", MUTED),
    ]
    for rect, top, sub, c in fields:
        cell(d, rect, top, sub, c)
    colour = (60, 414, 790, 519)
    depth = (814, 414, 1540, 519)
    cell(d, colour, "Colour: u8[H, W, 3]", "offset 32; ordering from global header", BLUE, t >= 1.3, 30)
    cell(d, depth, "Depth: u16[H, W]", "offset 32 + 3*W*H", TEAL, t >= 2.3, 30)
    if 1.3 <= t < 2.3:
        moving(d, (60, 381, 330, 405), colour, (t-1.3), "colour bytes", "write payload", BLUE, 290)
    if 2.3 <= t < 3.3:
        moving(d, (1240, 381, 1540, 405), depth, t-2.3, "depth bytes", "write payload", TEAL, 290)
    left, right = (120, 603, 720, 714), (880, 603, 1480, 714)
    # Both branches copy the complete colour/depth pair from the selected slot.
    d.line(((70, 533), (1530, 533)), fill=LINE, width=3)
    d.line(((800, 533), (800, 556), (430, 556)), fill=LINE, width=3)
    d.line(((800, 556), (1160, 556)), fill=LINE, width=3)
    arrow(d, (430, 556), (430, 592), BLUE)
    arrow(d, (1160, 556), (1160, 592), TEAL)
    cell(d, left, "Person process: private copy", "colour + depth; verify seq and frame n", BLUE, t >= 5.2, 29)
    cell(d, right, "Object process: private copy", "colour + depth; verify seq and frame n", TEAL, t >= 6.2, 29)
    if 4.1 <= t < 5.2:
        moving(d, colour, left, (t-4.1)/1.1, "copied bytes", "u8 colour + u16 depth", BLUE, 350)
    if 5.2 <= t < 6.3:
        moving(d, depth, right, (t-5.2)/1.1, "copied bytes", "u8 colour + u16 depth", TEAL, 350)
    if t < 1.1:
        caption(d, "A stable slot has an even sequence value.", "Offsets are byte offsets within this slot; metadata occupies 32 B.")
    elif t < 3.65:
        caption(d, "Writer sets the sequence odd, then writes metadata and image payloads.", "Readers do not accept a slot while its first sequence value is odd.", AMBER)
    elif t < 4.1:
        caption(d, "Writer commits with an even sequence, then advances the publication count.", "The global publication counter is separate from the slot's sequence value.", TEAL)
    else:
        caption(d, "Each branch copies the payload, then verifies unchanged even sequence + expected frame.", "Only the private copy is processed. A slow reader can skip overwritten frames.")
    return im


def record_row(d, y, name, size, color, object_record=False, selected=None):
    fit(d, (60, y, 955, y+36), f"{name}: {size} B shared record", 31, color, True, align="left")
    x = [60, 364, 668]
    rects = [(xx, y+49+row*97, xx+287, y+136+row*97) for row in range(2) for xx in x]
    if object_record:
        fields = [("magic / seq", "0 / 4: u32"), ("frame / time_s", "8: i32; 12: f32"),
                  ("object position", "16-27: 3 x f32"), ("object Euler", "28-39: 3 x f32"),
                  ("live", "40: u16"), ("padding", "42-43: 2 B")]
    else:
        fields = [("magic / seq", "0 / 4: u32"), ("frame / time_s", "8: i32; 12: f32"),
                  ("pelvis", "16-27: 3 x f32"), ("angles", "28-79: 13 x f32"),
                  ("live mask", "80: u16"), ("group tags", "82: u16")]
    for i, (rect, (top, sub)) in enumerate(zip(rects, fields)):
        cell(d, rect, top, sub, color if i != 0 else MUTED, selected == i, 27)
    bx = (1090, y, 1540, y+233)
    panel(d, bx, color, PALE[color])
    fit(d, (1107, y+10, 1523, y+41), "Object buffer" if object_record else "Person buffer", 30, color, True)
    items = (["time_s + frame index", "position: 3 values", "Euler: 3 values", "admit only if live == 1"]
             if object_record else ["time_s + frame index", "pelvis: 3 values", "angles: 13 values", "mask + unpacked tags"])
    dests = []
    for i, label in enumerate(items):
        r = (1108, y+51+i*43, 1522, y+88+i*43)
        panel(d, r, color, WHITE, 1, 4)
        fit(d, (r[0]+8, r[1]+6, r[2]-8, r[3]-6), label, 24, INK)
        dests.append(r)
    arrow(d, (972, y+119), (1074, y+119), color)
    return rects, dests


def extraction(t):
    u = t-8
    im, d = base(t, 1, "Read a stable record, unpack typed fields, and keep timestamped samples in separate buffers")
    person_moves = [(1, 0, "frame / time", "i32 + f32"), (2, 1, "pelvis", "3 x f32"),
                    (3, 2, "angles", "13 x f32"), (4, 3, "mask / tags", "u16 / 7 states")]
    object_moves = [(1, 0, "frame / time", "i32 + f32"), (2, 1, "object position", "3 x f32"),
                    (3, 2, "object Euler", "3 x f32"), (4, 3, "live gate", "u16 == 1")]
    p_index = min(int(max(0, u-.7)/1.0), 3) if .7 <= u < 4.7 else None
    o_index = min(int(max(0, u-5.5)/1.0), 3) if 5.5 <= u < 9.5 else None
    pr, pb = record_row(d, 207, "PSR2 person", 84, BLUE,
                        selected=person_moves[p_index][0] if p_index is not None else None)
    ob, ot = record_row(d, 483, "PSB2 object", 44, TEAL, True,
                        selected=object_moves[o_index][0] if o_index is not None else None)
    if p_index is not None:
        a, b, title, detail = person_moves[p_index]
        moving(d, pr[a], pb[b], (u-.7)-p_index, title, detail, BLUE)
    if o_index is not None:
        a, b, title, detail = object_moves[o_index]
        moving(d, ob[a], ot[b], (u-5.5)-o_index, title, detail, TEAL)
    caption(d, "Verify magic and sequence around the read; admit only a new source frame per stream.",
            "Header guards are checked. Pose fields are extracted; input headers and padding are not combined.")
    return im


def resample(t):
    u = t-18
    im, d = base(t, 2, "Evaluate the two independent sample buffers at one render timestamp tau")
    fit(d, (65, 204, 1535, 242), "tau = estimated session time - configured delay", 33, INK, True)
    fit(d, (65, 251, 1535, 281), "The tested launcher uses two frame intervals; this is a buffering choice, not measured latency.", 26, MUTED)
    for y, color, title, data, rule in [
        (317, BLUE, "Person", "pelvis + 13 angles", "Pelvis: linear.  Angles: wrap-aware.  Mask: AND.  Tags: per-group maximum."),
        (499, TEAL, "Object", "position + orientation", "Position: linear.  Rotation: SO(3) geodesic, then converted back to Euler angles."),
    ]:
        left, mid, right = (70, y, 455, y+90), (610, y, 990, y+90), (1145, y, 1530, y+90)
        cell(d, left, title + " at t_a", data, color, False, 29)
        cell(d, right, title + " at t_b", data, color, False, 29)
        cell(d, mid, title + " at tau", "t_a < tau < t_b", color, u >= 2.5, 29)
        arrow(d, (465, y+45), (595, y+45), color)
        arrow(d, (1135, y+45), (1005, y+45), color)
        fit(d, (70, y+105, 1530, y+137), rule, 26, color)
        if .6 < u < 2.5:
            moving(d, left, mid, (u-.6)/1.9, title + " fields", "sample before tau", color, 280)
            moving(d, right, mid, (u-.6)/1.9, title + " fields", "sample after tau", color, 280)
    caption(d, "The merger resamples values; it does not concatenate two input structs.",
            "This panel shows a permitted interpolation bracket. Exact/near samples, holds and return blends are separate cases.")
    return im


def psi_layout(d, top=326, emphasize=None):
    xs = [60, 436, 812, 1188]
    headers = [(x, top, x+352, top+74) for x in xs]
    for rect, a, b in zip(headers, ["PSI2 magic", "sequence", "NEW tick", "NEW tau"],
                          ["0: u32", "4: u32", "8: i32", "12: f32"]):
        cell(d, rect, a, b, PURPLE, emphasize == "header", 27)
    person = [(60, top+90, 790, top+175), (812, top+90, 1540, top+175)]
    cell(d, person[0], "person pelvis", "16-27: 3 x f32", BLUE, emphasize == "person", 29)
    cell(d, person[1], "person angles", "28-79: 13 x f32", BLUE, emphasize == "person", 29)
    objects = [(60, top+191, 790, top+276), (812, top+191, 1540, top+276)]
    cell(d, objects[0], "object position", "80-91: 3 x f32", TEAL, emphasize == "object", 29)
    cell(d, objects[1], "object Euler angles", "92-103: 3 x f32", TEAL, emphasize == "object", 29)
    states = [(x, top+292, x+352, top+372) for x in xs]
    for rect, a, b in zip(states, ["person mask", "object live", "merger flags", "group tags"],
                          ["104: u16", "106: u16", "108: u16", "110: u16"]):
        cell(d, rect, a, b, AMBER, emphasize == "states", 27)
    return headers, person, objects, states


def pack(t):
    u = t-23
    im, d = base(t, 3, "Pack a fresh 112-byte PSI2 record after resampling; all offsets below are bytes")
    p, o = (60, 215, 790, 298), (812, 215, 1540, 298)
    cell(d, p, "Resampled person fields", "pelvis, angles, mask and tags", BLUE, True, 30)
    cell(d, o, "Resampled object fields", "position and orientation; merger live state", TEAL, True, 30)
    active = "person" if u < 1.5 else "object" if u < 3 else "states" if u < 4 else "header"
    headers, person, objects, states = psi_layout(d, emphasize=active)
    if .15 <= u < 1.5:
        moving(d, p, person[0], (u-.15)/1.35, "pelvis", "3 x f32", BLUE)
        moving(d, p, person[1], (u-.15)/1.35, "angles", "13 x f32", BLUE)
    elif 1.5 <= u < 3:
        moving(d, o, objects[0], (u-1.5)/1.5, "object position", "3 x f32", TEAL)
        moving(d, o, objects[1], (u-1.5)/1.5, "object Euler", "3 x f32", TEAL)
    elif 3 <= u < 4:
        moving(d, p, states[0], u-3, "person mask", "u16", AMBER)
        moving(d, o, states[1], u-3, "object live", "u16", AMBER)
    caption(d, "PSI2 has a new output tick and render time; it does not retain the two source frame IDs.",
            "State and interpolation flags accompany the pose. Optional display smoothing can affect outgoing person values.")
    return im


def race(t):
    r = t-28
    im, d = base(t, 4, "Python publishes PSI2; Unity checks consistency before applying any typed fields")
    case_a = r < 3
    heading = "CASE A: first sequence is odd" if case_a else "CASE B: an independent example - a write starts during a read"
    fit(d, (52, 198, 1548, 237), heading, 30, AMBER if case_a else INK, True)
    cols = [(50, 257, 410, 724), (525, 257, 1045, 724), (1160, 257, 1550, 724)]
    for rect, heading, color in zip(cols, ["PYTHON WRITER", "SHARED PSI2", "UNITY READER"], [BLUE, PURPLE, TEAL]):
        panel(d, rect, color, WHITE)
        fit(d, (rect[0]+14, 270, rect[2]-14, 309), heading, 31, color, True)
    odd = case_a or 6 <= r < 8
    seq = 11 if odd else 10 if r < 6 else 12
    seqc = AMBER if odd else TEAL
    seqrect = (548, 328, 1022, 406)
    cell(d, seqrect, f"sequence = {seq}", "offset 4: u32; odd = writing", seqc, True, 33)
    person_version = "B" if case_a or r >= 6.5 else "A"
    object_version = "B" if case_a or r >= 7.1 else "A"
    shared = [
        ((548, 418, 1022, 486), "tick / tau", "8: i32 / 12: f32", PURPLE),
        ((548, 495, 1022, 563), "pelvis + 13 angles [" + person_version + "]", "16-79: f32 fields", BLUE),
        ((548, 572, 1022, 640), "object pose [" + object_version + "]", "80-103: f32 fields", TEAL),
        ((548, 649, 1022, 717), "mask / live / flags / tags", "104-111: four u16", AMBER),
    ]
    for rect, a, b, c in shared:
        cell(d, rect, a, b, c, True, 24)
    arrow(d, (416, 448), (513, 448), BLUE)
    arrow(d, (1055, 530), (1147, 530), TEAL)
    writer_lines = (["seq <- 11 (odd)", "write packed payload", "seq <- 12 (even)"]
                    if case_a or r >= 6 else ["Stable record", "seq = 10 (even)", "No write yet"])
    for i, line in enumerate(writer_lines):
        highlighted = (i == 0 and odd) or (i == 2 and r >= 8)
        color = AMBER if i == 0 and odd else TEAL if i == 2 and r >= 8 else INK
        fit(d, (68, 350+i*75, 392, 390+i*75), line, 27, color, highlighted)
    fit(d, (68, 595, 392, 705), "A = prior values\nB = new values\n(illustrative labels)", 24, MUTED)
    local = (1178, 414, 1532, 613)
    panel(d, local, TEAL if r >= 13 else LINE, PALE[TEAL] if r >= 13 else BG)
    if case_a:
        fit(d, (1178, 331, 1532, 393), "s1 = 11: ODD", 31, AMBER, True)
        fit(d, (1191, 435, 1519, 587), "SKIP fields\nRetry the read", 30, AMBER, True)
        fit(d, (1178, 640, 1532, 700), "No pose is applied.", 25, MUTED)
        if .2 < r < 1.25:
            moving(d, seqrect, (1178, 331, 1532, 393), (r-.2)/1.05, "s1 = 11", "first sequence", AMBER, 230)
        caption(d, "An odd first sequence means the writer is busy: Unity skips all payload fields.",
                "Unity makes up to three attempts per Update. If every attempt fails, the displayed pose remains unchanged.", AMBER)
    else:
        if r < 6:
            first, state, last = "s1 = 10: EVEN", "Read typed fields\ninto local values", "Check magic first."
        elif r < 7.1:
            first, state, last = "s1 was 10", "Person A is local\nWriter is updating", "Still not applied."
        elif r < 8:
            first, state, last = "s1 was 10", "Person A + object B\nPossible mixed read", "Still not applied."
        elif r < 10:
            first, state, last = "s2 = 12 != 10", "REJECT\nDiscard local read", "Keep displayed pose."
        elif r < 13:
            first, state, last = "Retry: s1 = 12", "Read all fields\ninto fresh locals", "s2 = 12: unchanged"
        else:
            first, state, last = "s1 = s2 = 12", "ACCEPT new tick\nApply person + object", "Magic also verified."
        color = RED if 8 <= r < 10 else TEAL if r >= 13 else INK
        fit(d, (1178, 331, 1532, 393), first, 29, color, True)
        fit(d, (1191, 438, 1519, 585), state, 28, color, True)
        fit(d, (1178, 637, 1532, 702), last, 25, MUTED)
        if 3.4 <= r < 4.35:
            moving(d, seqrect, (1178, 331, 1532, 393), (r-3.4)/.95, "s1 = 10", "even + valid magic", PURPLE, 300)
        elif 4.4 <= r < 5.55:
            moving(d, shared[1][0], local, (r-4.4)/1.15, "person values", "typed f32 reads", BLUE, 290)
        elif 7.15 <= r < 7.95:
            moving(d, shared[2][0], local, (r-7.15)/.8, "object values B", "typed f32 reads", TEAL, 290)
        elif 8 <= r < 8.9:
            moving(d, seqrect, (1178, 331, 1532, 393), (r-8)/.9, "s2 = 12", "sequence changed", RED, 290)
        elif 10.4 <= r < 11.4:
            moving(d, shared[1][0], local, r-10.4, "person fields", "typed local values", BLUE, 290)
        elif 11.4 <= r < 12.4:
            moving(d, shared[2][0], local, r-11.4, "object + state", "typed local values", TEAL, 290)
        if 6 <= r < 7:
            moving(d, (68, 415, 392, 471), shared[1][0], r-6, "new person fields", "Python writes", BLUE, 305)
        if 7 <= r < 8:
            moving(d, (68, 490, 392, 546), shared[2][0], r-7, "new object fields", "Python writes", TEAL, 305)
        if r < 6:
            caption(d, "Unity first reads sequence 10, then reads typed fields into local variables.",
                    "The shared-memory region can change between individual reads; values are not yet applied.")
        elif r < 8:
            caption(d, "During that read, Python publishes 11 (odd), writes the payload, then commits 12 (even).",
                    "This is a possible interleaving, not a measured thread schedule or a mutex lock.", AMBER)
        elif r < 10:
            caption(d, "The second sequence is 12, not 10: Unity rejects the local values and retries.",
                    "Rejected values never reach ApplyPerson or ApplyObject. The previously displayed pose remains.", RED)
        else:
            caption(d, "A retry reads 12 before and after the typed fields: matching even values pass the check.",
                    "Only a valid, new tick is applied. If all three attempts fail, the previous displayed pose is retained.", TEAL)
    return im


def render(t):
    if t >= DURATION-.5:
        t = 0.0
    if t < 8:
        im = image_slot(t)
    elif t < 18:
        im = extraction(t)
    elif t < 23:
        im = resample(t)
    elif t < 28:
        im = pack(t)
    else:
        im = race(t)
    draw_labels()
    return im.resize(SIZE, Image.Resampling.LANCZOS)


def verify_sources():
    texts = {p: (ROOT/p).read_text() for p in SOURCE_FILES}
    all_text = "\n".join(texts.values())
    proof = {}
    for name, (fmt, used, allocated) in FORMATS.items():
        assert fmt in all_text, (name, fmt)
        assert struct.calcsize(fmt) == used, (name, fmt)
        proof[name] = {"struct_format": fmt, "packed_bytes": used, "allocated_bytes": allocated}
    cs = texts[SOURCE_FILES[-1]]
    for marker in ["ReadUInt32(4)", "ReadInt32(8)", "ReadSingle(12)",
                   "ReadSingle(16)", "ReadSingle(28 + 4 * i)",
                   "ReadSingle(80)", "ReadSingle(92)",
                   "ReadUInt16(104)", "ReadUInt16(106)",
                   "ReadUInt16(108)", "ReadUInt16(110)",
                   "if (iview.ReadUInt32(4) == seq0) return true;",
                   "attempt < 3"]:
        assert marker in cs, marker
    proof["source_sha256"] = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCE_FILES}
    return proof


def export_parts(proof):
    """Keep the overview separate and publish three focused instructional loops."""
    global SEGMENT
    reports = []
    for part in PARTS:
        SEGMENT = part
        name, duration, start = part["name"], part["duration"], part["start"]
        def part_frame(t):
            return render(start + (0 if t >= duration-.5 else t))
        contact = Image.new("RGB", (320*4, 180*2))
        for i in range(8):
            local_time = i*(duration-.7)/7
            im = part_frame(local_time)
            im.save(REVIEW/f"{name}_check_{i:02d}.png")
            contact.paste(im.resize((320, 180)), ((i%4)*320, (i//4)*180))
        contact.save(REVIEW/f"{name}_contact.png")
        palette = contact.quantize(colors=240, method=Image.Quantize.MEDIANCUT)
        part_frame(0).save(OUT/f"{name}.png")
        movie = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{SIZE[0]}x{SIZE[1]}", "-r", str(MP4_FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT/f"{name}.mp4")],
            stdin=subprocess.PIPE)
        frames = []
        for i in range(duration*FPS):
            im = part_frame(i/FPS)
            frames.append(im.quantize(palette=palette, dither=Image.Dither.NONE))
            raw = im.tobytes()
            for _ in range(MP4_FPS//FPS):
                movie.stdin.write(raw)
        movie.stdin.close()
        assert movie.wait() == 0, name
        frames[0].save(OUT/f"{name}.gif", save_all=True, append_images=frames[1:],
                       duration=1000//FPS, loop=0, optimize=True, disposal=1)
        reports.append({"name": name, "duration_s": duration, "source_start_s": start,
                        "source_end_s": start+duration, "title": part["title"]})
        print(f"PASS: {name}, {duration} s, GIF + silent H.264 + poster", flush=True)
    SEGMENT = None
    proof.update({"parts": reports, "text_bounds_checks": CHECKS,
                  "minimum_font_at_drawing_scale": MIN_FONT,
                  "font_reductions": sorted(REDUCTIONS), "output_size": SIZE,
                  "gif_nominal_fps": FPS, "mp4_encoded_fps": MP4_FPS,
                  "loop_hold_s": .5, "all_text_inside_measured_container": True,
                  "overlapped_labels_suppressed": HIDDEN_LABELS,
                  "label_policy": "Suppress whole labels if an incoming tile intersects their measured glyph bounds."})
    (REVIEW/"memory_detail_layout.json").write_text(json.dumps(proof, indent=2)+"\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gif-only", action="store_true")
    ap.add_argument("--check-only", action="store_true")
    ap.add_argument("--split-only", action="store_true",
                    help="Export the three separate slide assets from verified phase renderers")
    args = ap.parse_args()
    OUT.mkdir(exist_ok=True)
    REVIEW.mkdir(exist_ok=True)
    proof = verify_sources()
    if args.split_only:
        export_parts(proof)
        return
    samples = [0, 2, 5, 8.5, 10.5, 15.5, 19.5, 22, 24, 26.5, 29.5, 32.5, 35, 37, 39, 42]
    thumbs = Image.new("RGB", (320*4, 180*4))
    for i, t in enumerate(samples):
        im = render(t)
        im.save(REVIEW/f"memory_records_{t:04.1f}.png")
        thumbs.paste(im.resize((320, 180)), ((i%4)*320, (i//4)*180))
    thumbs.save(REVIEW/"memory_records_contact.png")
    palette = thumbs.quantize(colors=240, method=Image.Quantize.MEDIANCUT)
    frames = []
    movie = None
    if not args.gif_only and not args.check_only:
        movie = subprocess.Popen([
            "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{SIZE[0]}x{SIZE[1]}", "-r", str(MP4_FPS), "-i", "-",
            "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT/"memory_records.mp4")],
            stdin=subprocess.PIPE)
    render(0).save(OUT/"memory_records.png")
    for i in range(DURATION*FPS):
        im = render(i/FPS)
        if not args.check_only:
            frames.append(im.quantize(palette=palette, dither=Image.Dither.NONE))
        if movie is not None:
            # A 10-Hz schematic is stored in a standard 30-fps H.264 stream.
            raw = im.tobytes()
            for _ in range(MP4_FPS//FPS):
                movie.stdin.write(raw)
    if movie is not None:
        movie.stdin.close()
        assert movie.wait() == 0, "ffmpeg failed"
    if not args.check_only:
        frames[0].save(OUT/"memory_records.gif", save_all=True, append_images=frames[1:],
                       duration=1000//FPS, loop=0, optimize=True, disposal=1)
    proof.update({"duration_s": DURATION, "gif_nominal_fps": FPS, "mp4_encoded_fps": MP4_FPS,
                  "output_size": SIZE, "drawing_size": [W, H], "text_bounds_checks": CHECKS,
                  "minimum_font_at_drawing_scale": MIN_FONT, "font_reductions": sorted(REDUCTIONS),
                  "schematic_sequence_examples": [10, 11, 12],
                  "race_cases": ["odd at start: skip payload", "changed during read: reject, retry, accept stable new tick"],
                  "model_claim": "Source-traced consistency check; no claim of formal memory ordering proof.",
                  "overlapped_labels_suppressed": HIDDEN_LABELS,
                  "label_policy": "Suppress whole labels if an incoming tile intersects their measured glyph bounds."})
    (REVIEW/"memory_records_layout.json").write_text(json.dumps(proof, indent=2)+"\n")
    print(json.dumps({"status": "PASS", "text_bounds_checks": CHECKS, "min_font": MIN_FONT,
                      "font_reductions": len(REDUCTIONS), "duration_s": DURATION}))


if __name__ == "__main__":
    main()
