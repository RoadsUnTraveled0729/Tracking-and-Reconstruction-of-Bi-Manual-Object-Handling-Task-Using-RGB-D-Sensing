#!/usr/bin/env python3
"""Single-clock camera/plot demonstrations from preserved R6b samples.

The whole retrospective filter result is calculated before cropping. Each
displayed trace stops at the camera's exact source frame, including holds.
Offline outputs can use later samples; display alignment is not online
availability or a new accuracy/latency experiment. Frozen helpers are read
only through filter_demos. Earlier separate-context assets are untouched.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import filter_demos as filters

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
MEDIA, REVIEW = HERE / "media", HERE / "review"
PROVENANCE = MEDIA / "provenance"
CACHE = Path("/tmp/defense_2026_causal/camera")
AUDIT_PATH = PROVENANCE / "recorded_context_source.json"
AUDIT = json.loads(AUDIT_PATH.read_text())
SOURCE = {row["frame"]: row for row in AUDIT["frames"]}
FPS, SPEED = 30, 0.5
START_HOLD, EVENT_HOLD, FINAL_HOLD = 3, 4, 5
W, H = 1440, 1200
CAMERA_BOX = (400, 0, 1040, 480)
PLOT = (185, 665, 1380, 1040)
INK, MUTED, RAW, OUTPUT = "#22313D", "#52606B", "#7A858D", "#386C8C"
ACCENT, GRID, BG = "#AB783B", "#DCE2E6", "#FFFFFF"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SPECS = {
    "filter_hampel_sync": dict(method="hampel", axis=2, first=450, last=549, event=537),
    "filter_gap_sync": dict(method="gap", axis=0, first=650, last=749, event=685),
    "filter_butterworth_sync": dict(method="butter", axis=2, first=25, last=179, event=None),
    "filter_one_euro_sync": dict(method="oneeuro", axis=2, first=25, last=179, event=None),
    "filter_savgol_sync": dict(method="savgol", axis=2, first=25, last=179, event=None),
    "filter_median_sync": dict(method="median", axis=2, first=25, last=179, event=None),
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return str(Path(path).relative_to(REPO))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n", encoding="ascii")


def numerical_provenance():
    # The helper's old display crop began at 28. Its numerical checks remain
    # valid, but that old display-history sentence does not describe this cut.
    return {key: value for key, value in filters.DATA["checks"].items()
            if key != "display_window_history"}


def initialization(spec):
    if spec["method"] == "oneeuro":
        return "Window 25-179 begins at valid-run initialization on frame 25 after missing frames 11-24; full-sequence processing resets there, and each later output uses only the received prefix."
    if spec["method"] in ("butter", "savgol", "median"):
        return "The complete valid run 25-549 is processed before displaying frames 25-179; offline outputs can depend on samples later than the visible cursor."
    if spec["method"] == "hampel":
        return "The full recorded sequence supplies centred Hampel neighbourhoods before the display crop 450-549; this is retrospective rejection."
    return "Full-recording endpoint-based interpolation precedes display crop 650-749; missing frames 681-684 use endpoints 680 and 685, while missing frames 674 and 678 also appear as distinct inferred samples."


@lru_cache(maxsize=10)
def font(size):
    return ImageFont.truetype(FONT_PATH, size)


def label(draw, box, text, size=48, color=INK, align="left", boxes=None):
    x0, y0, x1, y1 = box
    f = font(size); bounds = draw.textbbox((0, 0), text, font=f)
    tw, th = bounds[2] - bounds[0], bounds[3] - bounds[1]
    assert tw <= x1 - x0 and th <= y1 - y0, (text, box, tw, th)
    x = x0 if align == "left" else (x0 + x1 - tw) / 2 if align == "center" else x1 - tw
    y = (y0 + y1 - th) / 2
    actual = (x, y, x + tw, y + th)
    if boxes is not None:
        for old in boxes:
            overlap = min(actual[2], old[2]) > max(actual[0], old[0]) and min(actual[3], old[3]) > max(actual[1], old[1])
            assert not overlap, (text, actual, old)
        boxes.append(actual)
    draw.text((x - bounds[0], y - bounds[1]), text, font=f, fill=color)


def frame_map(spec):
    indices = np.arange(spec["first"], spec["last"] + 1)
    times = np.array([SOURCE[int(i)]["recorded_relative_seconds"] for i in indices])
    step = float(np.median(np.diff(times)))
    count = math.ceil(((times[-1] - times[0] + step) / SPEED) * FPS)
    active = []
    for j in range(count):
        clock = times[0] + j / FPS * SPEED
        at = min(len(indices) - 1, max(0, int(np.searchsorted(times, clock, side="right") - 1)))
        active.append(int(indices[at]))
    assert sorted(set(active)) == indices.tolist()
    rows = [(spec["first"], "initial_hold")] * (START_HOLD * FPS)
    event_added = False
    for j, idx in enumerate(active):
        rows.append((idx, "progression"))
        if idx == spec["event"] and (j == len(active)-1 or active[j+1] != idx):
            rows.extend([(idx, "event_hold")] * (EVENT_HOLD * FPS)); event_added = True
    rows.extend([(spec["last"], "final_hold")] * (FINAL_HOLD * FPS))
    assert event_added == (spec["event"] is not None)
    assert all(a[0] <= b[0] for a, b in zip(rows, rows[1:]))
    return rows


class Composite:
    def __init__(self, name):
        self.name, self.spec = name, SPECS[name]
        self.first, self.last = self.spec["first"], self.spec["last"]
        self.axis = self.spec["axis"]
        self.frames = np.arange(self.first, self.last + 1)
        self.times = np.array([SOURCE[int(i)]["recorded_relative_seconds"] for i in self.frames])
        self.raw = filters.DATA["pos"][self.first:self.last+1, self.axis]
        method = self.spec["method"]
        result = filters.DATA[method] if method in ("hampel", "gap") else filters.DATA["outputs"][method]
        self.output = result[self.first:self.last+1, self.axis]
        low = min(float(np.nanmin(self.raw)), float(np.nanmin(self.output)))
        high = max(float(np.nanmax(self.raw)), float(np.nanmax(self.output)))
        margin = max((high-low)*0.16, 0.002)
        self.ymin, self.ymax = low-margin, high+margin
        self.trace_checks = []
        for idx in self.frames:
            row = SOURCE[int(idx)]
            assert row["cache_matches_decode"]
            assert sha(CACHE/f"cam_{idx:06d}.jpg") == row["cache_sha256"]
            assert abs(row["recorded_relative_seconds"]-filters.DATA["times"][idx]) <= 1e-6

    def xy(self, times, values):
        a, b, c, d = PLOT
        return (a+(np.asarray(times)-self.times[0])/(self.times[-1]-self.times[0])*(c-a),
                d-(np.asarray(values)-self.ymin)/(self.ymax-self.ymin)*(d-b))

    def trace(self, draw, times, values, color, width):
        valid = np.isfinite(values)
        changes = np.flatnonzero(np.diff(np.r_[False, valid, False]))
        for start, stop in zip(changes[::2], changes[1::2]):
            x, y = self.xy(times[start:stop], values[start:stop])
            points = list(zip(x, y))
            if len(points) > 1:
                draw.line(points, fill=color, width=width, joint="curve")
            elif len(points):
                px, py = points[0]; draw.ellipse((px-4, py-4, px+4, py+4), fill=color)

    def render(self, idx, phase="progression"):
        assert self.first <= idx <= self.last
        count = idx-self.first+1
        im = Image.new("RGB", (W, H), BG)
        camera = Image.open(CACHE/f"cam_{idx:06d}.jpg").convert("RGB")
        assert camera.size == (640, 480)
        im.paste(camera, CAMERA_BOX[:2])
        draw = ImageDraw.Draw(im); boxes = []
        label(draw, (32, 145, 365, 202), "R6b recording", 40, MUTED, boxes=boxes)
        label(draw, (32, 215, 365, 270), "0.5x playback" if phase == "progression" else "Shared pause", 40, MUTED, boxes=boxes)
        label(draw, (1080, 145, 1408, 202), f"Frame {idx}", 40, MUTED, boxes=boxes)
        label(draw, (1080, 215, 1408, 270), f"{SOURCE[idx]['recorded_relative_seconds']:.3f} s", 40, MUTED, boxes=boxes)
        if self.spec["method"] == "hampel":
            draw.line((40, 326, 64, 350), fill=ACCENT, width=4)
            draw.line((40, 350, 64, 326), fill=ACCENT, width=4)
            label(draw, (88, 309, 365, 366), "Rejected", 40, MUTED, boxes=boxes)
        elif self.spec["method"] == "gap":
            draw.ellipse((41, 327, 63, 349), fill=BG, outline=OUTPUT, width=4)
            label(draw, (88, 309, 365, 366), "Inferred", 40, MUTED, boxes=boxes)
        caption = "Right wrist; causal output" if self.spec["method"] == "oneeuro" else "Right wrist; offline output"
        label(draw, (180, 500, 1380, 560), caption, 40, MUTED, "center", boxes)
        label(draw, (35, 581, 400, 637), "Camera x (m)" if self.axis == 0 else "Depth (m)", 48, INK, boxes=boxes)
        draw.line((515, 610, 590, 610), fill=RAW, width=9)
        label(draw, (612, 581, 850, 637), "Input", 48, INK, boxes=boxes)
        draw.line((935, 610, 1010, 610), fill=OUTPUT, width=6)
        label(draw, (1032, 581, 1380, 637), "Output", 48, INK, boxes=boxes)
        a, b, c, d = PLOT
        for value in np.linspace(self.ymin, self.ymax, 3):
            _, yy = self.xy(self.times[0], value)
            draw.line((a, yy, c, yy), fill=GRID, width=2)
            label(draw, (10, yy-29, 163, yy+29), f"{value:.2f}", 44, MUTED, "right", boxes)
        draw.line((a, b, a, d, c, d), fill=MUTED, width=2)
        for tm in [self.times[0], (self.times[0]+self.times[-1])/2, self.times[-1]]:
            xx, _ = self.xy(tm, self.ymin)
            draw.line((xx, d, xx, d+10), fill=MUTED, width=2)
            label(draw, (max(2, xx-100), 1066, min(W-2, xx+100), 1122), f"{tm:.2f}", 44, MUTED, "center", boxes)
        label(draw, (330, 1132, 1230, 1193), "Recorded time (s)", 46, INK, "center", boxes)
        shown_times = self.times[:count]
        self.trace(draw, shown_times, self.raw[:count], RAW, 9)
        self.trace(draw, shown_times, self.output[:count], OUTPUT, 5)
        xx, _ = self.xy(self.times[count-1], self.ymin)
        draw.line((xx, b, xx, d), fill=ACCENT, width=2)
        marked = []
        if self.spec["method"] == "hampel":
            for j in range(count):
                source_idx = self.first+j
                if filters.DATA["hampel_mask"][source_idx] and np.isfinite(self.raw[j]):
                    x, y = self.xy(self.times[j], self.raw[j]); r = 12
                    draw.line((x-r, y-r, x+r, y+r), fill=ACCENT, width=5)
                    draw.line((x-r, y+r, x+r, y-r), fill=ACCENT, width=5)
                    marked.append(source_idx)
        elif self.spec["method"] == "gap":
            for j in range(count):
                source_idx = self.first+j
                if filters.DATA["gap_mask"][source_idx] and np.isfinite(self.output[j]):
                    x, y = self.xy(self.times[j], self.output[j]); r = 9
                    draw.ellipse((x-r, y-r, x+r, y+r), fill=BG, outline=OUTPUT, width=4)
                    marked.append(source_idx)
        for values, color, radius in [(self.raw, RAW, 9), (self.output, OUTPUT, 6)]:
            if np.isfinite(values[count-1]):
                x, y = self.xy(self.times[count-1], values[count-1])
                draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)
        # Values, including repaired/offline results, are never drawn beyond
        # the displayed camera frame. The fixed axes alone span the full crop.
        assert len(shown_times) == count and self.frames[count-1] == idx
        self.trace_checks.append({"source_frame": idx, "camera_frame": idx,
            "visible_through_frame": int(self.frames[count-1]), "cursor_recorded_time_s": float(shown_times[-1]),
            "drawn_raw_finite": int(np.isfinite(self.raw[:count]).sum()),
            "drawn_output_finite": int(np.isfinite(self.output[:count]).sum()),
            "special_sample_frames": marked, "future_samples_drawn": 0,
            "label_count": len(boxes)})
        return im


def preview(names):
    for name in names:
        c = Composite(name)
        c.render(c.last, "final_hold").save(REVIEW/f"{name}_preview.png")
        if c.spec["event"] is not None:
            c.render(c.spec["event"], "event_hold").save(REVIEW/f"{name}_event_preview.png")
        print(f"PREVIEW: {name}; {len(frame_map(c.spec))/FPS:.3f} s", flush=True)


def build(name):
    c = Composite(name); mapping = frame_map(c.spec)
    path, poster = MEDIA/f"{name}.mp4", MEDIA/f"{name}.png"
    map_path, trace_path = PROVENANCE/f"{name}_frames.csv", PROVENANCE/f"{name}_trace.csv"
    with map_path.open("w", newline="", encoding="ascii") as stream:
        writer = csv.writer(stream)
        writer.writerow(["output_frame", "output_time_s", "source_frame", "camera_recorded_time_s", "plot_visible_through_frame", "plot_cursor_recorded_time_s", "phase"])
        for j, (idx, phase) in enumerate(mapping):
            tm = SOURCE[idx]["recorded_relative_seconds"]
            writer.writerow([j, f"{j/FPS:.9f}", idx, f"{tm:.12f}", idx, f"{tm:.12f}", phase])
    with trace_path.open("w", newline="", encoding="ascii") as stream:
        writer = csv.writer(stream); writer.writerow(["source_frame", "recorded_time_s", "raw_value_m", "output_value_m", "flagged", "inferred"])
        for j, idx in enumerate(c.frames):
            value = lambda v: "" if not np.isfinite(v) else f"{v:.12f}"
            writer.writerow([idx, f"{c.times[j]:.12f}", value(c.raw[j]), value(c.output[j]),
                             int(filters.DATA["hampel_mask"][idx]), int(filters.DATA["gap_mask"][idx])])
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pixel_format", "rgb24",
        "-video_size", f"{W}x{H}", "-framerate", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
        "-preset", "fast", "-crf", "17", "-threads", "2", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(path)], stdin=subprocess.PIPE)
    last_key, pixels = None, None
    for idx, phase in mapping:
        key = (idx, phase == "progression")
        if key != last_key:
            pixels = c.render(idx, phase).tobytes(); last_key = key
        proc.stdin.write(pixels)
    proc.stdin.close(); assert proc.wait() == 0
    c.render(c.last, "final_hold").save(poster)
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"], check=True)
    info = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))
    assert len(info["streams"]) == 1
    vs = info["streams"][0]
    assert (vs["width"], vs["height"], vs["codec_name"], vs["pix_fmt"], vs["r_frame_rate"]) == (W, H, "h264", "yuv420p", "30/1")
    assert int(vs["nb_frames"]) == len(mapping)
    assert abs(float(info["format"]["duration"])-len(mapping)/FPS) < 0.001
    sampled = sorted(set([0, len(mapping)//2, len(mapping)-1] + [j for j,(idx,phase) in enumerate(mapping) if phase == "event_hold"][:1]))
    comparisons = []
    for j in sampled:
        idx, phase = mapping[j]
        raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"select=eq(n\\,{j})", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"])
        actual = np.frombuffer(raw, np.uint8).reshape((H, W, 3))
        expected = np.asarray(c.render(idx, phase))
        error = np.abs(actual.astype(float)-expected)
        mean = float(error.mean()); assert mean < 3.0, (name, j, mean)
        comparisons.append({"output_frame": j, "source_frame": idx, "phase": phase,
                            "mean_absolute_rgb_error": mean, "expected_rgb_sha256": hashlib.sha256(expected.tobytes()).hexdigest()})
    assert all(row["camera_frame"] == row["visible_through_frame"] and row["future_samples_drawn"] == 0 for row in c.trace_checks)
    report = {"status": "PASS", "asset": relative(path), "poster": relative(poster),
        "sha256": {"mp4": sha(path), "png": sha(poster)}, "dimensions": [W,H], "frames": len(mapping),
        "duration_seconds": len(mapping)/FPS, "fps": FPS, "speed": SPEED,
        "shared_holds_seconds": {"initial": START_HOLD, "event": EVENT_HOLD if c.spec["event"] is not None else 0, "final": FINAL_HOLD},
        "spec": c.spec, "poster_source_frame": c.last, "poster_recorded_time_s": float(c.times[-1]),
        "source_camera_native_dimensions": [640,480], "camera_output_box": list(CAMERA_BOX),
        "source_audit": relative(AUDIT_PATH), "source_audit_sha256": sha(AUDIT_PATH),
        "source_csv": filters.BRIEF["source_csv"], "source_csv_sha256": filters.DATA["checks"]["source_csv_sha256"],
        "implementation": filters.BRIEF["implementation"], "implementation_sha256": filters.DATA["checks"]["implementation_sha256"],
        "generator": relative(Path(__file__)), "generator_sha256": sha(__file__),
        "numerical_helper": relative(Path(filters.__file__)), "numerical_helper_sha256": sha(filters.__file__),
        "frame_map": relative(map_path), "frame_map_sha256": sha(map_path),
        "trace_values": relative(trace_path), "trace_values_sha256": sha(trace_path),
        "numerical_checks": numerical_provenance(), "display_initialization": initialization(c.spec), "landmark": "right_wrist",
        "source_clock": "Audited bag-relative timestamp for both camera and plotted samples",
        "display_rule": "Only samples up through the displayed camera source frame are drawn; both components share every hold",
        "processing_scope": "Isolated operation on recorded input; full raw valid runs precede cropping; offline outputs are retrospective",
        "interpretation": "Time-locked playback of recorded camera pixels and calculated samples; not a recording of online filter execution or new accuracy validation",
        "visible_point_checks": c.trace_checks, "first_middle_last_decode_comparisons": comparisons,
        "full_decode": "PASS", "pixel_comparison": "Lossy H264 comparison to source-composed RGB; mean absolute channel difference below 3/255",
        "layout": "Normal-weight 48px legend, 44px ticks; no internal title; native camera pixels retained; measured text bounds and label separation",
        "future_trace_samples_drawn": 0, "source_frames_checked": len(c.frames)}
    write_json(REVIEW/f"{name}_checks.json", report)
    print(f"PASS: {name}; {len(mapping)} frames; {len(mapping)/FPS:.3f} s", flush=True)
    return report


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["preview", "build"])
    ap.add_argument("--asset", choices=list(SPECS))
    args = ap.parse_args(); names = [args.asset] if args.asset else list(SPECS)
    assert filters.DATA["checks"] == json.loads((REVIEW/"FILTER_DEMO_CHECK.json").read_text())["numerical"]
    write_json(HERE/"FILTER_SYNC_BRIEF.json", {
        "scope": "Synchronized recorded-camera and calculated right-wrist traces; no new validation experiment",
        "replaces_for_current_deck": "Separate unsynchronized camera/context and staged filter panels; originals retained",
        "dimensions": [W,H], "camera_native_dimensions": [640,480], "fps": FPS,
        "speed": SPEED, "initial_shared_hold_seconds": START_HOLD,
        "event_shared_hold_seconds": EVENT_HOLD, "final_shared_hold_seconds": FINAL_HOLD,
        "specs": SPECS, "parameters": filters.BRIEF["parameters"],
        "parameters_source": "FILTER_DEMO_BRIEF.json and preserved saved filter metadata",
        "timing_status": "Editorial: 30fps quantization, 0.5x progression, and shared holds are not processing latency",
        "clock": "Camera and curve use the same audited source frame and bag-relative timestamp",
        "offline_scope": "Retrospective output appears at its sample time; this is not online availability",
        "gap_scope": "Window 650-749 also contains single missing samples 674 and 678; the four-frame focus is 681-684",
        "camera_overlay": "No new inferred wrist marker; original camera pixels are unchanged",
        "source_audit": relative(AUDIT_PATH), "source_audit_sha256": sha(AUDIT_PATH)})
    if args.action == "preview":
        preview(names); return
    reports = [build(name) for name in names]
    if len(reports) == len(SPECS):
        write_json(REVIEW/"FILTER_SYNCHRONIZED_CHECK.json", {"status": "PASS", "assets": reports,
            "source_parameters_unchanged": True, "previous_media_preserved": True,
            "synchronization": "One composite MP4 and one output-to-source mapping per method; no independent video/GIF clocks",
            "all_camera_and_curve_source_indices_equal": True, "all_future_trace_counts_zero": True})


if __name__ == "__main__":
    main()
