#!/usr/bin/env python3
"""Slow, sparse teaching diagrams for the methodology slides.

All motion and durations are editorial, not measured execution or latency.
The detailed byte layouts remain in memory_records.py and its source audit.
This module writes only new teaching_* assets. Original diagrams are retained.

Source semantics: V9 Sections 6.1 and 6.5; v2/common/shm_ring.py;
v2/integration/v2_integrate.py; IntegratedSceneReceiverV2.cs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT, REVIEW = ROOT / "media", ROOT / "review"
W, H = 1440, 1080
FPS, GIF_FPS = 30, 10
BG, INK, MUTED, LINE = "#FFFFFF", "#152332", "#617184", "#CBD5DF"
TEAL, AMBER = "#087F83", "#A7680C"
PALE_TEAL, PALE_AMBER, PALE_INK = "#EAF5F4", "#FBF1DF", "#F1F4F7"
TEXT, OBSCURERS, METRICS = [], [], {}
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans"
DURATIONS = {"teaching_frame_journey": 48, "teaching_memory_copy": 40,
             "teaching_merge": 40, "teaching_read_write": 48}
SOURCES = ["v2/common/shm_ring.py", "v2/common/person_shm_v2.py",
           "v2/integration/v2_integrate.py",
           "Unity/Assets/Scripts/IntegratedSceneReceiverV2.cs"]


@lru_cache(maxsize=32)
def font(size, bold=False):
    return ImageFont.truetype(FONT_PATH + ("-Bold" if bold else "") + ".ttf", size)


def text(d, rect, value, size=90, color=INK, bold=False, layer=0, align="center"):
    """Queue a fitted label; incoming tiles suppress complete covered labels."""
    assert value.isascii(), value
    assert size >= 84 or (value == "Schematic" and size == 42), (value, size)
    if value.isupper():
        value = "\n".join(line.capitalize() for line in value.splitlines())
    x0, y0, x1, y1 = rect
    b = d.multiline_textbbox((0, 0), value, font=font(size, bold), spacing=12, align=align)
    tw, th = b[2]-b[0], b[3]-b[1]
    if tw > x1-x0 or th > y1-y0:
        raise ValueError(f"Text does not fit: {value!r}, {tw}x{th}, {rect}")
    x = x0 if align == "left" else x0+(x1-x0-tw)/2
    y = y0+(y1-y0-th)/2
    xy = (x-b[0], y-b[1])
    actual = d.multiline_textbbox(xy, value, font=font(size, bold), spacing=12, align=align)
    if min(actual[:2]) < 0 or actual[2] > W or actual[3] > H:
        raise ValueError((value, actual))
    TEXT.append((d, xy, value, size, color, bold, layer, align, actual))


def finish(im):
    visible = []
    for d, xy, value, size, color, bold, layer, align, b in TEXT:
        if any(z > layer and b[0] < r[2]+2 and b[2] > r[0]-2 and
               b[1] < r[3]+2 and b[3] > r[1]-2 for z, r in OBSCURERS):
            continue
        d.multiline_text(xy, value, font=font(size, bold), fill=color, spacing=12, align=align)
        visible.append((value, b))
    for i, (value, b) in enumerate(visible):
        for other, c in visible[i+1:]:
            if b[0] < c[2] and b[2] > c[0] and b[1] < c[3] and b[3] > c[1]:
                raise ValueError(f"Visible text overlap: {value!r} / {other!r}")
    count = sum(len(value.split()) for value, _ in visible)
    METRICS["max_visible_words"] = max(METRICS.get("max_visible_words", 0), count)
    METRICS["min_font_px"] = min(METRICS.get("min_font_px", 1000),
                                  *(item[3] for item in TEXT))
    if count > 32:
        raise ValueError(f"Too many visible words: {count}")
    METRICS["checked_frames"] = METRICS.get("checked_frames", 0)+1
    return im


def base(title, stage, count):
    # Slide-native text carries the full title, scientific caveat and sources.
    TEXT.clear(); OBSCURERS.clear()
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    text(d, (55, 30, 1050, 135), "Schematic", 42, MUTED, align="left")
    text(d, (1130, 30, 1390, 135), f"{stage} / {count}", 90, MUTED)
    return im, d


def block(d, rect, title, color=INK):
    d.rounded_rectangle(rect, radius=18, fill=BG, outline=color, width=5)
    x0, y0, x1, y1 = rect
    text(d, (x0+18, y0+20, x1-18, y0+140), title, 90, color, True)


def arrow(d, a, b, color=LINE, width=7):
    d.line((a, b), fill=color, width=width)
    angle = math.atan2(b[1]-a[1], b[0]-a[0])
    d.polygon([b, (b[0]-26*math.cos(angle-.48), b[1]-26*math.sin(angle-.48)),
               (b[0]-26*math.cos(angle+.48), b[1]-26*math.sin(angle+.48))], fill=color)


def tile(d, center, label, color=TEAL, width=490, height=250, layer=0):
    x, y = center; rect = (x-width/2, y-height/2, x+width/2, y+height/2)
    if layer: OBSCURERS.append((layer, rect))
    d.rounded_rectangle(rect, radius=12, fill=PALE_TEAL if color == TEAL else PALE_AMBER
                        if color == AMBER else PALE_INK, outline=color, width=4)
    text(d, (rect[0]+14, rect[1]+12, rect[2]-14, rect[3]-12), label,
         90, color, True, layer=layer)


def smooth(u):
    u = max(0.0, min(1.0, u)); return u*u*(3-2*u)


def transfer(d, a, b, progress, label, color=TEAL, width=490, height=250):
    u = smooth(progress)
    center = (a[0]+(b[0]-a[0])*u, a[1]+(b[1]-a[1])*u)
    tile(d, center, label, color, width, height, layer=100)


def overview(t):
    phase = min(3, int(t/12)); local = t-phase*12
    labels = [("FILE", "MEMORY", "COLOUR\nDEPTH", "COLOUR\nDEPTH"),
              ("MEMORY", "TRACKERS", "FRAME", "PERSON\nOBJECT"),
              ("POSES", "ALIGN", "PERSON\nOBJECT", "TIME t"),
              ("SCENE", "UNITY", "POSE", "POSE")]
    left, right, payload, result = labels[phase]
    im, d = base("", phase+1, 4)
    block(d, (55, 260, 650, 875), left)
    block(d, (790, 260, 1385, 875), right, TEAL)
    a, b = (352, 620), (1088, 620)
    arrow(d, (660, 620), (780, 620), TEAL)
    tile(d, a, payload)
    if local >= 7: tile(d, b, result)
    elif local >= 4: transfer(d, a, b, (local-4)/3, payload)
    return finish(im)


def memory_copy(t):
    phase = min(3, int(t/10)); local = t-phase*10
    im, d = base("", phase+1, 4)
    centers = [(365, 900), (720, 385), (1075, 900)]
    for rect, title, color in [((90, 650, 640, 1040), "PERSON", TEAL),
                              ((445, 170, 995, 510), "SHARED", INK),
                              ((800, 650, 1350, 1040), "OBJECT", TEAL)]:
        block(d, rect, title, color)
    tile(d, centers[1], "FRAME", INK, 455, 145)
    if phase > 1 or (phase == 1 and local >= 6): tile(d, centers[0], "FRAME", TEAL, 455, 145)
    if phase > 2 or (phase == 2 and local >= 6): tile(d, centers[2], "FRAME", TEAL, 455, 145)
    if phase == 1:
        arrow(d, (575, 530), (405, 625), TEAL)
        if 4 <= local < 6: transfer(d, centers[1], centers[0], (local-4)/2, "FRAME", TEAL, 455, 145)
    if phase == 2:
        arrow(d, (865, 530), (1035, 625), TEAL)
        if 4 <= local < 6: transfer(d, centers[1], centers[2], (local-4)/2, "FRAME", TEAL, 455, 145)
    return finish(im)


def history(d, rect, title, color, selected=False, target=.60):
    block(d, rect, title, color)
    x0, y0, x1, y1 = rect; y = y1-90
    xs = np.linspace(x0+100, x1-100, 5)
    d.line((xs[0], y, xs[-1], y), fill=LINE, width=7)
    for x in xs: d.ellipse((x-18, y-18, x+18, y+18), fill=color)
    if selected:
        x = x0+(x1-x0)*target
        d.line((x, y-70, x, y+45), fill=AMBER, width=8)
        d.ellipse((x-26, y-26, x+26, y+26), fill=BG, outline=AMBER, width=7)


def merge(t):
    phase = min(3, int(t/10)); local = t-phase*10
    im, d = base("", phase+1, 4)
    if phase < 2:
        top, bottom = (85, 190, 1355, 545), (85, 650, 1355, 1005)
        history(d, top, "PERSON", INK)
        history(d, bottom, "OBJECT", TEAL)
        if phase == 1:
            x = 85+1270*(.42+.18*smooth((local-4)/2))
            # Separate markers share x, but do not cross either stream label.
            d.line((x, 365, x, 515), fill=AMBER, width=8)
            d.line((x, 825, x, 970), fill=AMBER, width=8)
            for y in (455, 915): d.ellipse((x-27, y-27, x+27, y+27), fill=BG, outline=AMBER, width=7)
            text(d, (x+40, 556, x+155, 645), "t", 90, AMBER, True)
    elif phase == 2:
        block(d, (50, 240, 640, 515), "PERSON", INK)
        block(d, (50, 625, 640, 900), "OBJECT", TEAL)
        block(d, (800, 240, 1390, 965), "SCENE", TEAL)
        sources = [(345, 430), (345, 815)]; targets = [(1095, 535), (1095, 795)]
        for a, b, label, color in zip(sources, targets, ["PERSON", "OBJECT"], [INK, TEAL]):
            tile(d, a, "POSE", color, 480, 120)
            arrow(d, (665, a[1]), (775, b[1]), color)
            if local >= 6: tile(d, b, label, color, 490, 170)
            elif local >= 4: transfer(d, a, b, (local-4)/2, label, color, 490, 170)
    else:
        block(d, (170, 220, 1270, 1010), "SCENE POSE", TEAL)
        tile(d, (720, 525), "PERSON", INK, 890, 165)
        tile(d, (720, 745), "OBJECT", TEAL, 890, 165)
        text(d, (255, 874, 1185, 980), "TIME + STATES", 90, INK, True)
    return finish(im)


def read_write(t):
    case = 1 if t < 24 else 2
    im, d = base("", case, 2)
    if t < 8:
        heading="BUSY"; states=[("WRITING", AMBER), ("UPDATING", AMBER), ("SKIP", AMBER)]
    elif t < 14:
        heading="READY"; states=[("READY", TEAL), ("POSE", TEAL), ("READ\nCHECK", INK)]
    elif t < 24:
        heading="CHECK PASSES"; states=[("READY", TEAL), ("POSE", TEAL), ("ACCEPT", TEAL)]
    elif t < 32:
        heading="READ STARTS"; states=[("READY", TEAL), ("POSE", TEAL), ("READING", INK)]
    elif t < 40:
        heading="DATA CHANGES"; states=[("WRITING", AMBER), ("CHANGED", AMBER), ("RETRY", AMBER)]
    else:
        heading="IF RETRIES FAIL"; states=[("WRITING", AMBER), ("UPDATING", AMBER), ("OLD\nPOSE", AMBER)]
    text(d, (60, 150, 1380, 255), heading, 90, AMBER if case == 2 or t < 8 else TEAL, True)
    for rect, label in [((55, 295, 665, 650), "PYTHON"), ((775, 295, 1385, 650), "SHARED"),
                        ((405, 700, 1035, 1060), "UNITY")]: block(d, rect, label)
    centers=[(360, 535), (1080, 535), (720, 938)]
    for center, (label, color) in zip(centers, states):
        tile(d, center, label, color, 560, 190 if "\n" in label else 150)
    if 12 <= t < 14: transfer(d, centers[1], centers[2], (t-12)/2, "LOCAL", TEAL, 500, 150)
    if 28 <= t < 30: transfer(d, centers[1], centers[2], (t-28)/2, "LOCAL", TEAL, 500, 150)
    return finish(im)


RENDERERS = {"teaching_frame_journey": overview, "teaching_memory_copy": memory_copy,
             "teaching_merge": merge, "teaching_read_write": read_write}


def build_palette(render, duration):
    # Shared quantization prevents palette shimmer and preserves crisp text edges.
    samples = [render(float(t)) for t in np.linspace(0, duration-.1, 8)]
    mosaic = Image.new("RGB", (W*4, H*2), BG)
    for i, im in enumerate(samples): mosaic.paste(im, ((i%4)*W, (i//4)*H))
    return mosaic.quantize(colors=240, method=Image.Quantize.MEDIANCUT)


def export_asset(name, render, duration, preview_only=False, extra_report=None):
    OUT.mkdir(parents=True, exist_ok=True); REVIEW.mkdir(parents=True, exist_ok=True)
    METRICS.clear()
    preview_times = [0, duration*.15, duration*.30, duration*.48, duration*.65, duration-.1]
    for i, t in enumerate(preview_times): render(t).save(REVIEW/f"{name}_stage_{i+1:02d}.png")
    render(0).save(OUT/f"{name}.png")
    report = {"name": name, "dimensions": [W, H], "editorial_duration_seconds": duration,
              "editorial_gif_fps": GIF_FPS, "mp4_fps": FPS,
              "timing_scope": "Teaching holds and movement; not measured system timing",
              "loop_transition": "Final held teaching stage restarts at stage one",
              "sources": SOURCES, "status": "PREVIEW"}
    if extra_report: report.update(extra_report)
    if preview_only:
        report.update(METRICS)
        (REVIEW/f"{name}_checks.json").write_text(json.dumps(report, indent=2)+"\n")
        print(f"PASS: {name} preview and text layout", flush=True); return report
    palette = build_palette(render, duration)
    frames, durations = [], []
    previous = None
    for i in range(int(duration*GIF_FPS)):
        im = render(i/GIF_FPS).quantize(palette=palette, dither=Image.Dither.NONE)
        digest = hashlib.sha256(im.tobytes()).digest()
        if digest == previous:
            durations[-1] += 1000//GIF_FPS
        else:
            frames.append(im); durations.append(1000//GIF_FPS); previous = digest
    frames[0].save(OUT/f"{name}.gif", save_all=True, append_images=frames[1:],
                   duration=durations, loop=0, disposal=1, optimize=True)
    del frames
    print(f"PASS: {name} GIF encoded", flush=True)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
           "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags",
           "+faststart", str(OUT/f"{name}.mp4")]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(int(duration*FPS)): proc.stdin.write(render(i/FPS).tobytes())
    proc.stdin.close()
    if proc.wait(): raise RuntimeError(f"MP4 encode failed: {name}")
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(OUT/f"{name}.mp4"),
                    "-f", "null", "-"], check=True)
    gif = Image.open(OUT/f"{name}.gif"); elapsed = 0; compare_count = 0
    for i in range(gif.n_frames):
        gif.seek(i); current = gif.convert("RGB"); current.load()
        expected = render(elapsed/1000).quantize(palette=palette,
                        dither=Image.Dither.NONE).convert("RGB")
        if not np.array_equal(np.asarray(current), np.asarray(expected)):
            raise ValueError(f"Decoded GIF mismatch: {name}, frame {i}, {elapsed} ms")
        elapsed += gif.info["duration"]; compare_count += 1
    if elapsed != duration*1000 or gif.info.get("loop") != 0:
        raise ValueError(f"Incorrect GIF timing: {name}, {elapsed}")
    probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries",
        "stream=codec_name,width,height,pix_fmt,r_frame_rate:format=duration", "-of", "json",
        str(OUT/f"{name}.mp4")]))
    report.update(METRICS)
    report.update({"status": "PASS", "gif_decoded_frames": compare_count,
                   "gif_duration_ms": elapsed, "gif_loop": 0,
                   "gif_quantized_source_comparison": "PASS: every stored frame",
                   "mp4_full_decode": "PASS", "mp4_probe": probe,
                   "sha256": {ext: hashlib.sha256((OUT/f"{name}.{ext}").read_bytes()).hexdigest()
                              for ext in ("gif", "mp4", "png")},
                   "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    (REVIEW/f"{name}_checks.json").write_text(json.dumps(report, indent=2)+"\n")
    print(f"PASS: {name}, {duration} s, full GIF/MP4 decode and source comparison", flush=True)
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--preview-only", action="store_true")
    ap.add_argument("--asset", choices=list(RENDERERS)); args = ap.parse_args()
    names = [args.asset] if args.asset else list(RENDERERS)
    for key in names:
        export_asset(key, RENDERERS[key], DURATIONS[key], args.preview_only)
