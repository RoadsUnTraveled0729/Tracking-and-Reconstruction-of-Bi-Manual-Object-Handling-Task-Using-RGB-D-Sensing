#!/usr/bin/env python3
"""Make the overlay-free task clip for the introduction page.

Two recorded segments, played at the native 30 fps with a hard cut between
them: the R6b one-hand rail pass (Video/recording_20260831_065553.bag) and
the R7 two-hand handover (Video/recording_20260909_000024.bag). Frames are
decoded read-only with v3/replay/bag_source.py, so run this with the v3rt
Python (pyrealsense2):

    /home/luo/anaconda3/envs/v3rt/bin/python \
        presentation/defense_2026/anim/raw_task_context.py

The only drawing is a one-line caption in the bottom-left corner. The first
frames of both bags carry a burned-in landmark drawing (R6b frames 0-12, R7
frames 0-14, measured 2026-09-27; see DECISIONS.md); the selected ranges
start after it and every selected frame is checked for that drawing.
No detector, reconstruction or experiment is rerun.
"""
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from recorded_context import BAG as R6B_BAG  # noqa: E402
from recorded_context import FPS, MEDIA, REPO, finish_asset, relative, sha  # noqa: E402

R7_BAG = REPO / "Video/recording_20260909_000024.bag"
ARCHIVE_INDEX = REPO / "eval/recordings_archive/index.json"
STILLS = REPO / "writing/v9/figures/src"
NAME = "raw_task_context"
WIDTH, HEIGHT = 640, 480

# Inclusive source frame ranges (BagSource frame index). Chosen by visual
# inspection of contact sheets, 2026-09-27; see DECISIONS.md.
SEGMENTS = [
    {"key": "r6b", "bag": R6B_BAG, "first": 13, "last": 898,
     "caption": "R6b rail task: recorded RGB, no overlays",
     "stills": [95, 505, 700]},
    {"key": "r7", "bag": R7_BAG, "first": 690, "last": 1199,
     "caption": "R7 handover: recorded RGB, no overlays",
     "stills": [700, 950, 1042]},
]

# Burned-in landmark drawing guard. Dot colours (BGR) sampled from the
# drawing on R6b frame 1. Measured 2026-09-27 over every frame of both bags
# with a per-channel tolerance of 40: drawn frames count 475-706 matching
# pixels, all later frames at most 30 (R6b) and 64 (R7, the light-blue
# sticker on the left cabinet). 200 separates the two populations.
OVERLAY_DOT_BGR = (np.array([230, 216, 0]), np.array([0, 136, 255]))
OVERLAY_TOLERANCE = 40
OVERLAY_MAX_PIXELS = 200

# Caption: editorial constants (no data source). The box must stay left of
# the desk marker card, whose left edge is at x = 318 px (R6b frame 1) and
# 319 px (R7 frame 0) on rows 440-470: first pixel with all channels above
# 200, measured 2026-09-27.
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_PX = 13
PAD_X, PAD_Y = 6, 4
MARKER_LEFT_PX = 318
CAPTION_ALPHA = 0.60

# Poster: the R6b lift frame 505 used by the deck's evaluation stills.
POSTER_SOURCE = ("r6b", 505)


def overlay_pixels(bgr):
    pixels = bgr.astype(np.int16)
    return int(sum((np.abs(pixels - colour).max(axis=2) < OVERLAY_TOLERANCE).sum()
                   for colour in OVERLAY_DOT_BGR))


def caption_layer(text):
    """Return (box, rgba) for a caption box at the bottom-left corner."""
    font = ImageFont.truetype(FONT, FONT_PX)
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    left, top, right, bottom = probe.textbbox((0, 0), text, font=font)
    box_w = right - left + 2 * PAD_X
    box_h = bottom - top + 2 * PAD_Y
    assert box_w < MARKER_LEFT_PX, "Caption would cover the desk marker: " + text
    layer = Image.new("RGBA", (box_w, box_h), (0, 0, 0, int(round(255 * CAPTION_ALPHA))))
    ImageDraw.Draw(layer).text((PAD_X - left, PAD_Y - top), text, font=font,
                               fill=(255, 255, 255, 255))
    return (0, HEIGHT - box_h, box_w, HEIGHT), layer


def archive_sha(bag):
    rows = json.loads(ARCHIVE_INDEX.read_text())
    rows = rows if isinstance(rows, list) else rows.get("recordings", [])
    matches = [row["sha256"] for row in rows if row.get("old_name") == bag.name]
    assert len(matches) == 1, "No unique archive index entry for " + bag.name
    return matches[0]


def main():
    from v3.replay.bag_source import BagSource  # noqa: E402 (needs REPO on path)

    output = MEDIA / (NAME + ".mp4")
    encoder = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", "%dx%d" % (WIDTH, HEIGHT), "-framerate", str(FPS), "-i", "-", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output)],
        stdin=subprocess.PIPE)
    written = 0
    poster_position = None
    segments = []
    for seg in SEGMENTS:
        bag_sha = sha(seg["bag"])
        assert bag_sha == archive_sha(seg["bag"]), "Bag hash differs from archive index"
        box, layer = caption_layer(seg["caption"])
        times, still_checks, worst_overlay = [], [], 0
        with BagSource(str(seg["bag"]), paced=False) as source:
            for idx, time_s, colour, _depth in source.frames(max_frames=seg["last"] + 1):
                if idx < seg["first"]:
                    continue
                assert colour.shape == (HEIGHT, WIDTH, 3)
                count = overlay_pixels(colour)
                assert count <= OVERLAY_MAX_PIXELS, "Landmark drawing on %s frame %d" % (seg["key"], idx)
                worst_overlay = max(worst_overlay, count)
                rgb = np.ascontiguousarray(colour[:, :, ::-1])
                if idx in seg["stills"]:
                    still = np.asarray(Image.open(STILLS / ("%s_frame%05d.png" % (seg["key"], idx))).convert("RGB"))
                    assert np.array_equal(still, rgb), "Frame index mismatch at %s %d" % (seg["key"], idx)
                    still_checks.append(idx)
                if (seg["key"], idx) == POSTER_SOURCE:
                    poster_position = written
                frame = Image.fromarray(rgb).convert("RGBA")
                frame.alpha_composite(layer, dest=box[:2])
                encoder.stdin.write(frame.convert("RGB").tobytes())
                times.append(time_s)
                written += 1
        count = seg["last"] - seg["first"] + 1
        assert len(times) == count, "Short decode for " + seg["key"]
        steps = np.diff(times)
        assert sorted(still_checks) == seg["stills"]
        segments.append({
            "recording": seg["key"], "source": relative(seg["bag"]), "source_sha256": bag_sha,
            "first_frame": seg["first"], "last_frame": seg["last"], "frames": count,
            "output_seconds": count / FPS,
            "recorded_seconds": [round(times[0], 6), round(times[-1], 6)],
            "recorded_step_ms": [round(1000 * steps.min(), 3), round(1000 * steps.max(), 3)],
            "caption": seg["caption"], "caption_box_px": list(box),
            "stills_pixel_identical": still_checks,
            "max_overlay_colour_pixels": worst_overlay,
        })
    encoder.stdin.close()
    assert encoder.wait() == 0, "ffmpeg failed"
    result = finish_asset(NAME, WIDTH, HEIGHT, written / FPS, written, poster_position / FPS)
    result.update({"segments": segments, "poster_source_frame": list(POSTER_SOURCE),
                   "generator": relative(Path(__file__)), "generator_sha256": sha(__file__)})
    print(json.dumps(result, indent=2))
    print("PASS: %s; %d frames; %.3f s" % (relative(output), written, written / FPS))


if __name__ == "__main__":
    sys.path.insert(0, str(REPO))
    main()
