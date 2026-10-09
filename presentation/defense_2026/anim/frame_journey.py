#!/usr/bin/env python3
"""Animate one recorded frame through disk, processes and shared memory.

Scientific source: Thesis V9 Sections 6.1, 6.5 and 8.2; Table 6.2.
Frame 533 was published in slot 5 at 17.78 s. The two branches copied it.
The merger subsequently interpolated frames 532 and 533 at render time
17.75 s. The motion below is a conceptual ordering, not a scheduler trace.
Only the processing times in the thesis are measurements; animation time
is deliberately expanded. Static calibration PSB3 is omitted.

Editorial choices are logged in presentation/defense_2026/DECISIONS.md D-015.
Run with the thesis Python. --gif-only avoids the optional MP4 encode.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "media"
W, H = 1600, 900
OUT_SIZE = (1280, 720)
DURATION, GIF_FPS, MOVIE_FPS = 36, 10, 30
BG = "#F6F8FB"
WHITE = "#FFFFFF"
INK = "#172B40"
MUTED = "#526479"
LINE = "#CAD3DF"
BLUE = "#245BB5"
TEAL = "#087F83"
PURPLE = "#704B9D"
AMBER = "#A26613"
PALE = {BLUE: "#E7EFFC", TEAL: "#E1F3F1", PURPLE: "#EEE7F8", AMBER: "#FAEFD9", INK: "#E7ECF2"}
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
LAYOUT_CHECKS = 0
FONT_REDUCTIONS = set()
LABELS = []
TILES = []


@lru_cache(maxsize=100)
def font(size, bold=False, mono=False):
    name = "DejaVuSansMono" if mono else "DejaVuSans"
    return ImageFont.truetype(str(FONT_DIR / (name + ("-Bold" if bold else "") + ".ttf")), size)


def text(d, xy, value, size=24, color=INK, bold=False, anchor=None, mono=False):
    assert value.isascii(), value
    f = font(size, bold, mono)
    bounds = d.textbbox(xy, value, font=f, anchor=anchor, spacing=7)
    LABELS.append((xy, value, f, color, anchor, bounds, None))


def fitted(d, rect, value, size=24, color=INK, bold=False, mono=False,
           align="center", minimum=17, tile=None):
    """Place text using measured glyph bounds inside the supplied content area."""
    global LAYOUT_CHECKS
    assert value.isascii(), value
    x0, y0, x1, y1 = rect
    for chosen in range(size, minimum-1, -1):
        f = font(chosen, bold, mono)
        bx0, by0, bx1, by1 = f.getbbox(value)
        if bx1-bx0 <= x1-x0 and by1-by0 <= y1-y0:
            break
    else:
        raise ValueError("Text does not fit its container: " + value)
    left = x0 if align == "left" else x0 + ((x1-x0)-(bx1-bx0))/2
    top = y0 + ((y1-y0)-(by1-by0))/2
    xy = (left-bx0, top-by0)
    actual = d.textbbox(xy, value, font=f)
    assert actual[0] >= x0-.1 and actual[1] >= y0-.1, (value, actual, rect)
    assert actual[2] <= x1+.1 and actual[3] <= y1+.1, (value, actual, rect)
    LABELS.append((xy, value, f, color, None, actual, tile))
    LAYOUT_CHECKS += 1
    if chosen != size:
        FONT_REDUCTIONS.add((value, size, chosen))


NODES = {
    "disk": (36, 175, 218, 291),
    "capture": (282, 175, 506, 291),
    "ring": (575, 145, 828, 321),
    "person": (895, 125, 1140, 233),
    "object": (895, 324, 1140, 432),
    "psr": (1220, 125, 1475, 233),
    "psb": (1220, 324, 1475, 432),
    "merger": (1120, 499, 1480, 607),
    "combined": (705, 499, 1035, 607),
    "unity": (265, 499, 615, 607),
}


def centre(key):
    x0, y0, x1, y1 = NODES[key]
    return ((x0 + x1) / 2, (y0 + y1) / 2)


PATHS = {
    "disk_capture": [centre("disk"), centre("capture")],
    "capture_ring": [centre("capture"), centre("ring")],
    "ring_person": [centre("ring"), (858, 233), (858, 179), centre("person")],
    "ring_object": [centre("ring"), (858, 233), (858, 378), centre("object")],
    "person_psr": [centre("person"), centre("psr")],
    "object_psb": [centre("object"), centre("psb")],
    "object_link": [centre("psb"), (1180, 378), (1180, 273), (1018, 273), centre("person")],
    "psr_merger": [centre("psr"), (1500, 179), (1500, 464), (1387, 464), (1387, 548)],
    "psb_merger": [centre("psb"), (1300, 378), (1300, 548)],
    "merger_combined": [centre("merger"), centre("combined")],
    "combined_unity": [centre("combined"), centre("unity")],
}

CONNECTIONS = {
    "disk_capture": [(218, 233), (282, 233)],
    "capture_ring": [(506, 233), (575, 233)],
    "ring_person": [(828, 233), (858, 233), (858, 179), (895, 179)],
    "ring_object": [(828, 233), (858, 233), (858, 378), (895, 378)],
    "person_psr": [(1140, 179), (1220, 179)],
    "object_psb": [(1140, 378), (1220, 378)],
    "object_link": [(1220, 378), (1180, 378), (1180, 273), (1018, 273), (1018, 233)],
    "psr_merger": [(1475, 179), (1500, 179), (1500, 464), (1387, 464), (1387, 499)],
    "psb_merger": [(1300, 432), (1300, 499)],
    "merger_combined": [(1120, 548), (1035, 548)],
    "combined_unity": [(705, 548), (615, 548)],
}


def arrow(d, pts, color=LINE, width=3, dashed=False):
    if dashed:
        for a, b in zip(pts, pts[1:]):
            length = math.dist(a, b)
            for s in range(0, int(length), 15):
                lo, hi = s / length, min(s + 8, length) / length
                p = (a[0] + lo*(b[0]-a[0]), a[1] + lo*(b[1]-a[1]))
                q = (a[0] + hi*(b[0]-a[0]), a[1] + hi*(b[1]-a[1]))
                d.line((p, q), fill=color, width=width)
    else:
        d.line(pts, fill=color, width=width, joint="curve")
    a, b = pts[-2:]
    angle = math.atan2(b[1]-a[1], b[0]-a[0])
    d.polygon([b, (b[0]-11*math.cos(angle-.45), b[1]-11*math.sin(angle-.45)),
               (b[0]-11*math.cos(angle+.45), b[1]-11*math.sin(angle+.45))], fill=color)


def point_on(pts, u):
    lengths = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    dist = max(0, min(1, u)) * sum(lengths)
    for a, b, length in zip(pts, pts[1:], lengths):
        if dist <= length:
            f = dist/length if length else 0
            return a[0] + f*(b[0]-a[0]), a[1] + f*(b[1]-a[1])
        dist -= length
    return pts[-1]


def packet(d, path, u, first, second="frame 533", color=BLUE):
    u = max(0, min(1, u))
    smooth = u*u*(3-2*u)
    x, y = point_on(PATHS[path], smooth)
    tile_id = len(TILES)
    TILES.append((x-95, y-38, x+95, y+38))
    # Every moving object is a labelled rectangular payload, not a particle.
    d.rounded_rectangle((x-95, y-38, x+95, y+38), radius=8,
                        fill=PALE[color], outline=color, width=3)
    d.rectangle((x-94, y-37, x+94, y-30), fill=color)
    fitted(d, (x-83, y-26, x+83, y-1), first, 22, color, True, tile=tile_id)
    fitted(d, (x-83, y+7, x+83, y+28), second, 20, INK, mono=True, tile=tile_id)


def node(d, key, heading, sub, kind="PROCESS", color=BLUE, active=False):
    x0, y0, x1, y1 = NODES[key]
    d.rounded_rectangle((x0, y0, x1, y1), radius=9,
                        fill=PALE[color] if active else WHITE,
                        outline=color if active else LINE, width=4 if active else 2)
    fitted(d, (x0+14, y0+9, x1-14, y0+27), kind, 15, color, True,
           align="left", minimum=15)
    fitted(d, (x0+14, y0+37, x1-14, y0+66), heading, 25, INK, True)
    fitted(d, (x0+14, y0+73, x1-14, y1-9), sub, 20, MUTED)


STAGES = [
    (0, 2, "One recorded frame; successive data representations",
     "RGB-D recording on disk", "Follow frame 533 through the system.",
     "Labelled blocks = data", "Outlined blocks = processes or shared memory.", []),
    (2, 5, "1. Read the recorded colour and depth messages",
     "Disk: recorded .bag", "Colour message + depth message",
     "Capture process input", "Recorded images and sensor timestamps", ["disk", "capture"]),
    (5, 8, "2. Align depth to colour and assign frame metadata",
     "Colour + depth images", "Two image grids from the same capture",
     "Aligned RGB-D frame 533", "RGB | aligned depth | index | timestamp", ["capture"]),
    (8, 11, "3. Publish the frame into shared RAM",
     "Aligned frame 533", "Capture time: 17.78 s on the session clock",
     "PSF1 ring buffer: slot 5", "533 mod 8 = 5 | RGB-D + metadata", ["capture", "ring"]),
    (11, 14, "4. Each branch copies and verifies the same frame",
     "Shared RAM: slot 5", "Reading copies the slot; capture can overwrite it later.",
     "Two verified process-local copies", "Check unchanged even sequence + frame index.", ["ring", "person", "object"]),
    (14, 17, "5. Images become 3D measurements and object pose",
     "Person: pixels + aligned depth", "8 landmarks -> 3D points in the camera frame",
     "Object: marker corners + calibration", "Object position + orientation -> PSB2 (44 B)", ["person", "object", "psb"]),
    (17, 20, "6. The person branch can use an accepted object record",
     "Latest accepted object pose: index k", "Asynchronous link; |k - 533| <= 3",
     "Object-derived wrist target", "Available during a grip; use remains conditional.", ["person", "psb"]),
    (20, 23, "7. Kinematic reconstruction publishes a person record",
     "3D landmarks + reconstruction state", "Root frame -> arm angles; recovery if required",
     "PSR2: frame 533 (84 B)", "Pelvis | 13 angles | live bits | group states", ["person", "psr"]),
    (23, 26, "8. The merger reads the person and object records",
     "PSR2 + PSB2 in shared RAM", "Separate streams retain their frame indices.",
     "Merger: recent samples", "Frames 532 and 533 bracket the render time.", ["psr", "psb", "merger"]),
    (26, 29, "9. Resample both streams at one render time",
     "Buffered records: 532 and 533", "Recorded example: interpolate both streams.",
     "PSI2: combined record (112 B)", "Render time 17.75 s | person + object + states", ["merger", "combined"]),
    (29, 32, "10. Unity reads the combined pose record",
     "PSI2: one render-time record", "Reconstructed poses and measurement states",
     "Unity scene", "Apply transforms to the avatar and tracked object.", ["combined", "unity"]),
    (32, 36, "One frame contributes to a reconstructed scene",
     "Images -> measurements -> pose records", "Data contents change at processing steps.",
     "Recorded frame != rendered tick", "The final scene can interpolate adjacent frames.", ["unity"]),
]


def payload_panel(d, stage):
    _, _, title, a, b, c, e, _ = stage
    d.rounded_rectangle((36, 645, 1564, 842), radius=12, fill=WHITE, outline=LINE, width=2)
    fitted(d, (60, 657, 1540, 698), title, 28, INK, True, align="left", minimum=24)
    d.line((60, 708, 1540, 708), fill=LINE, width=1)
    fitted(d, (62, 721, 782, 753), a, 24, BLUE, True, align="left", minimum=20)
    fitted(d, (62, 766, 782, 803), b, 21, MUTED, align="left", minimum=18)
    fitted(d, (855, 721, 1538, 753), c, 24, TEAL, True, align="left", minimum=20)
    fitted(d, (855, 766, 1538, 803), e, 21, MUTED, align="left", minimum=18)
    arrow(d, [(800, 755), (832, 755)], MUTED, 3)


def frame(t, poster=False):
    LABELS.clear()
    TILES.clear()
    stage = next(s for s in STAGES if s[0] <= t < s[1]) if not poster else STAGES[0]
    active = stage[-1]
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    text(d, (36, 27), "Single-frame data flow", 42, INK, True)
    text(d, (36, 85), "Recorded frame 533: disk, shared memory and processing", 25, MUTED)
    text(d, (1564, 31), "SCHEMATIC ANIMATION", 18, MUTED, True, "rt")
    text(d, (1564, 62), "Motion is not measured execution timing", 17, MUTED, False, "rt")

    # Connections are underneath the blocks; the trajectory is persistent.
    for name, path in CONNECTIONS.items():
        arrow(d, path, AMBER if name == "object_link" else "#9CAABA", 3,
              dashed=(name == "object_link"))
    node(d, "disk", ".bag file", "RGB + depth", "DISK", INK, "disk" in active)
    node(d, "capture", "Capture", "read + align", color=BLUE, active="capture" in active)
    node(d, "person", "Person branch", "landmarks -> angles", color=BLUE, active="person" in active)
    node(d, "object", "Object branch", "marker -> pose", color=TEAL, active="object" in active)
    node(d, "psr", "PSR2: person", "frame 533 | 84 bytes", "SHARED RAM", BLUE, "psr" in active)
    node(d, "psb", "PSB2: object", "frame index | 44 bytes", "SHARED RAM", TEAL, "psb" in active)
    node(d, "merger", "Temporal merger", "buffer + resample", color=PURPLE, active="merger" in active)
    node(d, "combined", "PSI2: combined pose", "render time | 112 bytes", "SHARED RAM", PURPLE, "combined" in active)
    node(d, "unity", "Unity receiver", "transforms -> scene", color=PURPLE, active="unity" in active)

    x0, y0, x1, y1 = NODES["ring"]
    d.rounded_rectangle((x0, y0, x1, y1), radius=10,
                        fill=PALE[BLUE] if "ring" in active else WHITE,
                        outline=BLUE if "ring" in active else LINE, width=4 if "ring" in active else 2)
    fitted(d, (x0+14, y0+9, x1-14, y0+27), "SHARED RAM", 15, BLUE, True, align="left", minimum=15)
    fitted(d, (x0+14, y0+39, x1-14, y0+68), "PSF1: frame ring", 24, INK, True)
    fitted(d, (x0+10, y0+76, x1-10, y0+103), "8 slots | colour + depth", 17, MUTED)
    for i in range(8):
        x = x0+16+i*28
        lit = i == 5 and t >= 8
        d.rectangle((x, y0+113, x+24, y0+147), fill=BLUE if lit else BG, outline=LINE)
        text(d, (x+12, y0+130), str(i), 18, WHITE if lit else MUTED, lit, "mm")

    text(d, (1016, 282), "object-pose link", 17, AMBER, True, "mt")
    text(d, (590, 363), "The two branches read independently.", 18, MUTED, False, "mt")
    text(d, (590, 391), "Copies do not remove the shared frame.", 18, MUTED, False, "mt")
    text(d, (46, 519), "DATA", 17, BLUE, True)
    d.rounded_rectangle((46, 549, 216, 596), radius=6, fill=PALE[BLUE], outline=BLUE, width=2)
    text(d, (131, 572), "frame 533", 18, BLUE, True, "mm", mono=True)

    if not poster:
        if 2 <= t < 5:
            packet(d, "disk_capture", (t-2)/3, "RGB + depth")
        elif 5 <= t < 8:
            text(d, (394, 331), "align + timestamp", 19, BLUE, True, "mt")
        elif 8 <= t < 11:
            packet(d, "capture_ring", min(1, (t-8)/1.8), "aligned RGB-D") if t < 9.8 else None
            state = "ODD: write payload" if t < 10.1 else "EVEN: ready to copy"
            text(d, (702, 335), state, 19, AMBER if t < 10.1 else BLUE, True, "mt")
        elif 11 <= t < 14:
            packet(d, "ring_person", (t-11)/3, "RGB-D copy")
            packet(d, "ring_object", (t-11)/3, "RGB-D copy", color=TEAL)
        elif 14 <= t < 17:
            if t >= 14.5:
                packet(d, "object_psb", (t-14.5)/2.5, "object pose", color=TEAL)
        elif 17 <= t < 20:
            packet(d, "object_link", (t-17)/3, "object pose", "index k", AMBER)
        elif 20 <= t < 23:
            packet(d, "person_psr", (t-20)/3, "angles + state")
        elif 23 <= t < 26:
            packet(d, "psr_merger", (t-23)/3, "person record")
            packet(d, "psb_merger", (t-23)/3, "object record", color=TEAL)
        elif 26 <= t < 29:
            packet(d, "merger_combined", (t-26)/3, "sampled pose", "t = 17.75 s", PURPLE)
        elif 29 <= t < 32:
            packet(d, "combined_unity", (t-29)/3, "scene pose", "render tick", PURPLE)
        elif t >= 32:
            text(d, (802, 458), "RGB-D -> 3D measurements -> pose records -> scene", 24, INK, True, "mm")

    payload_panel(d, stage)
    # Progress is a teaching timeline, never a profiler timeline.
    d.rectangle((36, 620, 1564, 626), fill=LINE)
    d.rectangle((36, 620, 36+1528*t/DURATION, 626), fill=BLUE)
    text(d, (36, 867), "Source: Thesis V9 Sections 6.1 and 6.5, Table 6.2 | Static calibration record omitted", 17, MUTED)
    text(d, (1564, 867), "36-second explanatory loop", 17, MUTED, False, "rt")
    # A travelling field replaces an intersected label temporarily. Do not
    # leave fragments of a system label visible around the payload card.
    for xy, value, f, color, anchor, bounds, own_tile in LABELS:
        blockers = TILES if own_tile is None else TILES[own_tile+1:]
        intersects = any(bounds[0] < b[2] and bounds[2] > b[0]
                         and bounds[1] < b[3] and bounds[3] > b[1]
                         for b in blockers)
        if not intersects:
            d.text(xy, value, font=f, fill=color, anchor=anchor, spacing=7)
    return im.resize(OUT_SIZE, Image.Resampling.LANCZOS)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gif-only", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    frame(0, poster=True).save(OUT / "frame_journey.png")
    # One common palette keeps flat diagram colours stable throughout the loop.
    palette_source = Image.new("RGB", (1280, 720*4))
    for i, t in enumerate((0, 12, 18, 28)):
        palette_source.paste(frame(t), (0, i*720))
    palette = palette_source.quantize(colors=240, method=Image.Quantize.MEDIANCUT)
    images = [frame(i/GIF_FPS).quantize(palette=palette, dither=Image.Dither.NONE)
              for i in range(DURATION*GIF_FPS)]
    images[0].save(OUT / "frame_journey.gif", save_all=True, append_images=images[1:],
                   duration=1000//GIF_FPS, loop=0, disposal=1, optimize=True)
    (HERE / "review" / "FRAME_JOURNEY_LAYOUT.json").write_text(json.dumps({
        "status": "PASS", "bounded_labels_checked": LAYOUT_CHECKS,
        "font_reductions": [{"text": s, "requested": a, "used": b}
                            for s, a, b in sorted(FONT_REDUCTIONS)],
        "method": "Measured glyph bounds checked against each node, packet and caption container",
        "moving_labels": "Overlapped background labels are suppressed to prevent stray letter fragments",
    }, indent=2) + "\n")
    print("PASS: frame_journey.gif and frame_journey.png", flush=True)
    review = Path("/tmp/defense_frame_journey_review")
    review.mkdir(parents=True, exist_ok=True)
    for t in (4, 9, 12.5, 15.5, 18.5, 21.5, 24.5, 27.5, 30.5, 34):
        frame(t).save(review / ("frame_journey_check_%02d.png" % t))
    if not args.gif_only:
        command = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                   "-s", "1280x720", "-r", str(MOVIE_FPS), "-i", "-", "-an", "-c:v", "libx264",
                   "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                   str(OUT / "frame_journey.mp4")]
        process = subprocess.Popen(command, stdin=subprocess.PIPE)
        for i in range(DURATION*MOVIE_FPS):
            process.stdin.write(frame(i/MOVIE_FPS).tobytes())
        process.stdin.close()
        if process.wait():
            raise RuntimeError("Frame-journey MP4 encode failed")
        print("PASS: frame_journey.mp4", flush=True)


if __name__ == "__main__":
    main()
