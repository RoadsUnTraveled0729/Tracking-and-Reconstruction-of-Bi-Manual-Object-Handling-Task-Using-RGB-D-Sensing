#!/usr/bin/env python3
"""Make the overlay-free R7 handover clip for the task-video page (round 10).

Round 10 (author, 2026-09-30): the task-video page plays the handover
recording only, without the R6b rail pass. This wrapper reuses the
round-3 generator anim/raw_task_context.py, which it does not modify: the
same bag-hash check against the archive index, burned-in landmark drawing
guard, still-frame identity check, encoder settings and full-decode check
(recorded_context.finish_asset). The old clip media/raw_task_context.mp4
and its committee copy are not touched.

Build 71 (D-320): the clip carries no drawing at all. The round-3
generator burns a one-line caption into the bottom-left corner, which the
slide then had to cover with a black rectangle. This wrapper therefore
runs its own frame loop with the base module's helpers and writes the
decoded source colour frames unchanged: no caption, no box, no text. The
caption-only check of the base (the caption box must stay left of the
desk marker) has nothing to check here. No drawing is applied by
construction: the bytes written to the encoder are the decoded BagSource
frame converted to RGB order, with no drawing call in between. This is a
property of the code, not a measured check (D-335, build 74: the build-71
comparison of that array with a copy of itself and the two equal sha256
digests over the same bytes could not fail and were removed). What is
checked: the bag sha256 equals the archive index, no burned-in landmark
drawing in the source frames (the base module's colour-pixel bound), the
three stills are pixel-identical to the reference stills, and the full
decode of the film has the declared frame count. H.264 (CRF 18, yuv420p)
compresses the frames, as for every other film; the decoded film is not
compared with the source pixels (no sourced tolerance exists).

It then writes the committee copy for page 4 (byte-identical film and
poster), its source-frame map and its provenance JSON under
committee_materials/unified_revision/. Run with the v3rt Python
(pyrealsense2):

    /home/luo/anaconda3/envs/v3rt/bin/python \
        presentation/defense_2026/anim/raw_handover_task.py

Window (DECISIONS.md D-304): R7 (Video/recording_20260909_000024.bag)
BagSource frames 690-1199 inclusive, the R7 segment of the round-3 clip
(D-110): the right hand sliding the cube, the left hand arriving at about
frame 870, both hands on the cube at about 885-1005, the right hand
released by about 1020, the left-hand slide to the far end and the left
hand lifting off at about 1185.
"""
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import raw_task_context as base  # noqa: E402

NAME = "raw_handover_task"
STEM = "p04-Raw_Handover_Task"
PAGE = 4
# D-304: same R7 range and stills as the round-3 clip (D-110). No caption (D-320).
SEGMENT = {"key": "r7", "bag": base.R7_BAG, "first": 690, "last": 1199,
           "stills": [700, 950, 1042]}
# D-304: poster at R7 frame 950, both hands on the cube (transfer).
POSTER_SOURCE = ("r7", 950)
OUT = base.REPO / "presentation/defense_2026/committee_materials/unified_revision"


def rel(path):
    return str(Path(path).resolve().relative_to(base.REPO))


def encode_raw():
    """Encode the selected source frames unchanged; return the segment record."""
    from v3.replay.bag_source import BagSource  # noqa: E402 (needs REPO on path)

    seg = SEGMENT
    output = base.MEDIA / (NAME + ".mp4")
    # Same encoder settings as raw_task_context.py main().
    encoder = subprocess.Popen([
        "ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", "%dx%d" % (base.WIDTH, base.HEIGHT), "-framerate", str(base.FPS), "-i", "-", "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output)],
        stdin=subprocess.PIPE)
    bag_sha = base.sha(seg["bag"])
    assert bag_sha == base.archive_sha(seg["bag"]), "Bag hash differs from archive index"
    source_digest = hashlib.sha256()
    times, still_checks, worst_overlay = [], [], 0
    poster_position = None
    with BagSource(str(seg["bag"]), paced=False) as source:
        for idx, time_s, colour, _depth in source.frames(max_frames=seg["last"] + 1):
            if idx < seg["first"]:
                continue
            assert colour.shape == (base.HEIGHT, base.WIDTH, 3)
            count = base.overlay_pixels(colour)
            assert count <= base.OVERLAY_MAX_PIXELS, "Landmark drawing on %s frame %d" % (seg["key"], idx)
            worst_overlay = max(worst_overlay, count)
            rgb = np.ascontiguousarray(colour[:, :, ::-1])
            source_digest.update(rgb.tobytes())
            if idx in seg["stills"]:
                still = np.asarray(Image.open(base.STILLS / ("%s_frame%05d.png" % (seg["key"], idx))).convert("RGB"))
                assert np.array_equal(still, rgb), "Frame index mismatch at %s %d" % (seg["key"], idx)
                still_checks.append(idx)
            if (seg["key"], idx) == POSTER_SOURCE:
                poster_position = len(times)
            # D-320, D-335: the decoded frame itself (RGB order) is written to the encoder.
            encoder.stdin.write(rgb.tobytes())
            times.append(time_s)
    encoder.stdin.close()
    assert encoder.wait() == 0, "ffmpeg failed"
    count = seg["last"] - seg["first"] + 1
    assert len(times) == count, "Short decode for " + seg["key"]
    assert sorted(still_checks) == seg["stills"]
    steps = np.diff(times)
    asset = base.finish_asset(NAME, base.WIDTH, base.HEIGHT, count / base.FPS, count, poster_position / base.FPS)
    record = {
        "recording": seg["key"], "source": base.relative(seg["bag"]), "source_sha256": bag_sha,
        "first_frame": seg["first"], "last_frame": seg["last"], "frames": count,
        "output_seconds": count / base.FPS,
        "recorded_seconds": [round(times[0], 6), round(times[-1], 6)],
        "recorded_step_ms": [round(1000 * steps.min(), 3), round(1000 * steps.max(), 3)],
        "stills_pixel_identical": still_checks,
        "max_overlay_colour_pixels": worst_overlay,
        "source_rgb_sha256": source_digest.hexdigest(),
    }
    print(json.dumps(dict(asset, segment=record), indent=2))
    return record


def main():
    record = encode_raw()
    master = base.MEDIA / (NAME + ".mp4")
    master_poster = master.with_suffix(".png")
    video = OUT / "videos" / (STEM + ".mp4")
    poster = OUT / "posters" / (STEM + ".png")
    shutil.copyfile(master, video)
    shutil.copyfile(master_poster, poster)
    assert base.sha(video) == base.sha(master) and base.sha(poster) == base.sha(master_poster)
    frames = SEGMENT["last"] - SEGMENT["first"] + 1
    probe = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
        "stream=width,height,codec_name,pix_fmt,r_frame_rate,nb_read_frames:format=duration",
        "-of", "json", str(video)]))
    stream = probe["streams"][0]
    assert int(stream["nb_read_frames"]) == frames
    frame_map = OUT / "provenance" / (STEM + "_source_frames.csv")
    with frame_map.open("w", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["output_frame", "recording", "source_bag", "source_frame"])
        for position in range(frames):
            writer.writerow([position, "r7", rel(SEGMENT["bag"]), SEGMENT["first"] + position])
    provenance = {
        "status": "PASS", "page": PAGE, "source_page": PAGE, "kind": "recording",
        "filename_stem": STEM, "asset": rel(video), "poster": rel(poster),
        "sha256": {"mp4": base.sha(video), "png": base.sha(poster)},
        "byte_identical_copy_of": {"asset": rel(master), "asset_sha256": base.sha(master),
                                   "poster": rel(master_poster), "poster_sha256": base.sha(master_poster)},
        "generator": rel(Path(__file__)), "generator_sha256": base.sha(Path(__file__)),
        "base_generator": rel(Path(base.__file__)), "base_generator_sha256": base.sha(Path(base.__file__)),
        "generator_command": "/home/luo/anaconda3/envs/v3rt/bin/python presentation/defense_2026/anim/raw_handover_task.py",
        "decode_check": {"width": stream["width"], "height": stream["height"], "codec": stream["codec_name"],
                         "pix_fmt": stream["pix_fmt"], "frame_rate": stream["r_frame_rate"],
                         "nb_read_frames": int(stream["nb_read_frames"]),
                         "container_duration_s": round(float(probe["format"]["duration"]), 6)},
        "frames": frames, "fps": base.FPS, "duration_s": frames / base.FPS,
        "dimensions": [base.WIDTH, base.HEIGHT],
        "segments": [{"recording": "r7", "source_bag": rel(SEGMENT["bag"]),
                      "archive_index_sha256": base.archive_sha(SEGMENT["bag"]),
                      "first_frame": SEGMENT["first"], "last_frame": SEGMENT["last"], "frames": frames,
                      "first_output_frame": 0,
                      "recorded_seconds": record["recorded_seconds"],
                      "recorded_step_ms": record["recorded_step_ms"],
                      "stills_pixel_identical": record["stills_pixel_identical"],
                      "max_overlay_colour_pixels": record["max_overlay_colour_pixels"]}],
        "poster_source_frame": list(POSTER_SOURCE),
        "frame_map": rel(frame_map), "frame_map_sha256": base.sha(frame_map),
        "drawing": ("none by construction: the generator writes each decoded source colour frame (RGB order) "
                    "to the encoder with no drawing call, so no caption, box or text (D-320). This is a "
                    "property of the code, not a measured comparison (D-335)."),
        "checks": {"bag_sha256_equals_archive_index": True,
                   "stills_pixel_identical_to_reference": record["stills_pixel_identical"],
                   "max_overlay_colour_pixels": record["max_overlay_colour_pixels"],
                   "full_decode_frames": int(stream["nb_read_frames"]), "declared_frames": frames},
        "source_rgb_sha256": record["source_rgb_sha256"],
        "encoder": "libx264 CRF 18, preset medium, yuv420p (lossy, as every film); the decoded film is not "
                   "compared with the source pixels",
        "role": "Recorded R7 handover, raw colour, no overlays; no tracking or reconstruction result.",
        "decision": "presentation/defense_2026/DECISIONS.md D-304, D-320",
    }
    path = OUT / "provenance" / (STEM + ".json")
    path.write_text(json.dumps(provenance, indent=2) + "\n")
    print("PASS: %s; %d frames; %.3f s" % (rel(video), frames, frames / base.FPS))


if __name__ == "__main__":
    sys.path.insert(0, str(base.REPO))
    main()
