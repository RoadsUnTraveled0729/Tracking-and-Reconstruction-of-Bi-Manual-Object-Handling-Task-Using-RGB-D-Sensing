#!/usr/bin/env python3
"""Large-label teaching animation of the thesis per-frame memory path.

Facts: Thesis V9 Sections 6.1 and 8.2-8.4; v2/common/shm_ring.py;
v2/common/person_shm_v2.py; v2/common/object_link.py;
v2/integration/v2_integrate.py. Image payloads are copied and verified.
The latest object record is asynchronous; the code accepts absolute
frame-index skew <= 3, not necessarily the same or an earlier frame.
The static PSB3 scene setup record is outside this per-frame animation.

Editorial choices: 16-second explanatory loop, 10-fps GIF, 30-fps MP4,
1280x720 pixels. Motion timings and field widths are not measurements.
No new experimental number is supplied by this graphic.

Run: /home/luo/anaconda3/bin/python presentation/defense_2026/anim/memory_flow.py
"""
from __future__ import annotations

import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "media"
TMP = Path("/tmp/defense_2026_memory")
W, H = 1280, 720
DURATION, FPS, GIF_FPS = 16.0, 30, 10
BG, WHITE, INK = "#F7F9FC", "#FFFFFF", "#152332"
NAVY, BLUE, AMBER, CYAN = "#112238", "#2468DA", "#C7811D", "#2CB2AC"
MUTED, LINE = "#536576", "#CBD5E0"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(n, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, n)


def text(d, xy, words, n=23, fill=INK, bold=False, anchor=None):
    d.text(xy, words, font=font(n, bold), fill=fill, anchor=anchor,
           spacing=7)


def box(d, rect, title, subtitle="", color=BLUE, fs=25, fill=WHITE):
    d.rounded_rectangle(rect, radius=15, fill=fill, outline=color, width=2)
    x0, y0, x1, y1 = rect
    text(d, ((x0+x1)/2, y0+22), title, fs, color, True, "mt")
    if subtitle:
        text(d, ((x0+x1)/2, y0+59), subtitle, 20, INK, False, "mt")


def arrow(d, pts, color=MUTED, width=3):
    d.line(pts, fill=color, width=width, joint="curve")
    x, y = pts[-1]
    px, py = pts[-2]
    a = math.atan2(y-py, x-px)
    tip = [(x, y), (x-12*math.cos(a-0.5), y-12*math.sin(a-0.5)),
           (x-12*math.cos(a+0.5), y-12*math.sin(a+0.5))]
    d.polygon(tip, fill=color)


def token(d, pts, u, label="n", color=BLUE):
    u = min(1.0, max(0.0, u))
    lengths = [math.dist(a, b) for a, b in zip(pts, pts[1:])]
    dist = u * sum(lengths)
    x, y = pts[-1]
    for a, b, length in zip(pts, pts[1:], lengths):
        if dist <= length:
            f = dist/length if length else 0
            x, y = a[0]+f*(b[0]-a[0]), a[1]+f*(b[1]-a[1])
            break
        dist -= length
    d.rounded_rectangle((x-25, y-22, x+25, y+22), radius=9,
                        fill=color, outline=WHITE, width=2)
    text(d, (x, y), label, 22, WHITE, True, "mm")


def chrome(title, subtitle):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    text(d, (44, 25), "PER-FRAME DATA FLOW", 17, BLUE, True)
    text(d, (1236, 25), "SCHEMATIC / TIMING NOT TO SCALE", 16,
         MUTED, False, "rt")
    text(d, (44, 69), title, 34, NAVY, True)
    text(d, (44, 118), subtitle, 22, MUTED)
    d.line((44, 661, 1236, 661), fill=LINE, width=1)
    text(d, (44, 680), "Thesis V9 Sections 6.1 and 8.2 | Static scene setup omitted", 17, MUTED)
    return im, d


def overview():
    im, d = chrome("Shared-memory transport of RGB-D and pose data",
                   "Separate image and pose records connect capture, processing branches and Unity.")
    box(d, (44, 302, 190, 413), "Capture", "RGB + depth", fs=25)
    box(d, (226, 302, 390, 413), "Frame ring", "8 slots", fs=24)
    box(d, (433, 206, 626, 317), "Person", "detect + recover", fs=26)
    box(d, (433, 457, 626, 568), "Object", "marker pose", color=CYAN, fs=26)
    box(d, (668, 206, 812, 317), "PSR2", "84 bytes", fs=26)
    box(d, (668, 457, 812, 568), "PSB2", "44 bytes", color=CYAN, fs=26)
    box(d, (856, 302, 998, 413), "Merger", "buffer + pair", fs=25)
    box(d, (1040, 238, 1236, 349), "PSI2", "112 bytes", fs=26)
    box(d, (1040, 457, 1236, 568), "Unity", "rendered scene", fs=26)
    for p in [[(190, 357), (226, 357)], [(390, 340), (413, 340), (413, 260), (433, 260)],
              [(390, 376), (413, 376), (413, 512), (433, 512)],
              [(626, 260), (668, 260)], [(626, 512), (668, 512)],
              [(812, 260), (833, 260), (833, 330), (856, 330)],
              [(812, 512), (833, 512), (833, 382), (856, 382)],
              [(998, 357), (1019, 357), (1019, 292), (1040, 292)],
              [(1138, 349), (1138, 457)]]:
        arrow(d, p)
    arrow(d, [(739, 457), (739, 369), (530, 369), (530, 317)], AMBER)
    text(d, (622, 389), "Latest object state", 19, AMBER, True, "mt")
    text(d, (44, 608), "Branches run independently; shared indices identify the captured instant.", 23, INK)
    return im


def capture(t):
    im, d = chrome("Image publication and consistency checks",
                   "Odd/even sequence counters identify in-progress and committed writes.")
    box(d, (44, 181, 243, 299), "Frame n", "RGB + depth", fs=27)
    box(d, (308, 181, 566, 299), "Capture process", "align + timestamp", fs=26)
    arrow(d, [(243, 239), (308, 239)])
    arrow(d, [(566, 239), (649, 239)])
    d.rounded_rectangle((649, 179, 1236, 329), radius=15, fill=WHITE, outline=BLUE, width=2)
    text(d, (674, 194), "Shared ring: 8 slots", 26, BLUE, True)
    # The highlighted slot denotes n modulo 8; its numeric position is symbolic.
    for i in range(8):
        x = 674+i*66
        fc = "#DFEAFE" if i == 4 else BG
        d.rounded_rectangle((x, 245, x+57, 299), radius=6, fill=fc, outline=LINE, width=1)
        text(d, (x+28, 271), "n" if i == 4 else "", 22, BLUE, True, "mm")
    if t < 1.0:
        token(d, [(160, 336), (560, 336), (942, 336)], t)
    phase = min(3, int(t / 1.5))
    steps = ["Write begins: the selected slot has an odd sequence counter.",
             "Payload write: frame index, timestamps, RGB and aligned depth.",
             "Commit: even sequence, then publication count advances.",
             "Read: copy payload, then verify sequence and frame index."]
    text(d, (44, 360), steps[phase], 27, NAVY, True)
    text(d, (44, 406), "Selected slot: index = n mod 8", 22, MUTED)
    specs = [(44, 184, "sequence", "ODD" if phase < 2 else "EVEN", AMBER if phase < 2 else BLUE),
             (184, 508, "metadata", "frame n + timestamps", BLUE),
             (508, 870, "colour payload", "RGB bytes", BLUE),
             (870, 1236, "depth payload", "aligned uint16 depth", CYAN)]
    for x0, x1, heading, value, col in specs:
        d.rectangle((x0, 449, x1, 540), fill=WHITE, outline=col, width=2)
        text(d, ((x0+x1)/2, 462), heading, 20, MUTED, False, "mt")
        text(d, ((x0+x1)/2, 501), value, 22, col, True, "mm")
    if phase == 3:
        arrow(d, [(417, 541), (417, 570)], BLUE)
        arrow(d, [(909, 541), (909, 570)], CYAN)
        box(d, (170, 572, 631, 637), "Person: copy + verify", fs=23)
        box(d, (709, 572, 1202, 637), "Object: copy + verify", color=CYAN, fs=23)
    else:
        text(d, (44, 584), "Readers accept only an unchanged even sequence and the expected index.", 22, MUTED)
        text(d, (44, 620), "A slow reader can lose whole frames. The writer does not wait.", 21, MUTED)
    return im


def branches(t):
    im, d = chrome("Pose-record exchange and delayed rendering",
                   "The person branch can read the latest accepted object state for recovery.")
    # Geometry is deliberately spacious. Packet sizes are facts; visual widths are not.
    box(d, (44, 275, 231, 390), "Frame ring", "copied frame n", fs=25)
    box(d, (291, 179, 581, 295), "Person branch", "landmarks + recovery", fs=26)
    box(d, (291, 453, 581, 569), "Object branch", "markers + world pose", color=CYAN, fs=26)
    box(d, (646, 179, 854, 295), "PSR2: 84 B", "angles + states", fs=25)
    box(d, (646, 453, 854, 569), "PSB2: 44 B", "pose + live bit", color=CYAN, fs=25)
    box(d, (918, 254, 1236, 370), "Merger -> PSI2", "112 B combined record", fs=26)
    box(d, (918, 453, 1236, 569), "Unity receiver", "reads the pose record", fs=26)
    paths = [[(231, 304), (260, 304), (260, 237), (291, 237)],
             [(231, 364), (260, 364), (260, 510), (291, 510)],
             [(581, 237), (646, 237)], [(581, 510), (646, 510)],
             [(854, 237), (885, 237), (885, 282), (918, 282)],
             [(854, 510), (885, 510), (885, 342), (918, 342)],
             [(1078, 370), (1078, 453)]]
    for p in paths:
        arrow(d, p)
    link = [(750, 453), (750, 344), (436, 344), (436, 295)]
    arrow(d, link, AMBER)
    text(d, (635, 378), "Latest accepted object state", 20, AMBER, True, "mt")
    text(d, (635, 409), "Asynchronous; same index not guaranteed", 17, MUTED, False, "mt")
    text(d, (44, 584), "n: captured frame    k: latest object record    t: output tick", 18, MUTED)
    text(d, (44, 614), "Merger render time trails capture by two frame intervals; latency was not measured.", 22, NAVY)
    # This is a structural tour, not a scheduler trace. k explicitly differs from n.
    if t < 1.8:
        token(d, paths[0], t/1.8, "n", BLUE)
        token(d, paths[1], t/1.8, "n", CYAN)
    elif t < 3.6:
        token(d, link, (t-1.8)/1.8, "k", AMBER)
    elif t < 5.2:
        token(d, paths[2], (t-3.6)/1.6, "n", BLUE)
        token(d, paths[3], (t-3.6)/1.6, "n", CYAN)
    elif t < 6.5:
        token(d, paths[4], (t-5.2)/1.3, "p", BLUE)
        token(d, paths[5], (t-5.2)/1.3, "o", CYAN)
    else:
        token(d, paths[6], (t-6.5)/1.5, "t", BLUE)
    return im


def frame(t):
    if t < 0.8 or t >= 14.8:
        return overview()
    if t < 6.8:
        return capture(t-0.8)
    return branches(t-6.8)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    # Rendering directly to rawvideo keeps temporary storage bounded.
    command = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
               "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
               str(OUT / "memory_flow.mp4")]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    for i in range(int(DURATION*FPS)):
        process.stdin.write(frame(i/FPS).tobytes())
    process.stdin.close()
    if process.wait():
        raise RuntimeError("memory-flow MP4 encode failed")
    gifs = [frame(i/GIF_FPS) for i in range(int(DURATION*GIF_FPS))]
    gifs[-1] = gifs[0].copy()
    gifs[0].save(OUT / "memory_flow.gif", save_all=True, append_images=gifs[1:],
                 duration=int(1000/GIF_FPS), loop=0, disposal=2, optimize=False)
    overview().save(OUT / "memory_flow.png")
    print("PASS: memory_flow.mp4, memory_flow.gif, memory_flow.png")


if __name__ == "__main__":
    main()
