#!/usr/bin/env python3
"""Make recorded context clips without rerunning tracking or experiments.

Run audit-source with the v3rt Python to check the existing R6b colour cache
against a read-only RealSense decode. Run build with the thesis Python.
All output timing is editorial and all rendered source content is retained
unless an explicitly documented crop removes empty background/pillarboxes.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
MEDIA = HERE / "media"
PROVENANCE = MEDIA / "provenance"
REVIEW = HERE / "review"
CACHE = Path("/tmp/defense_2026_causal/camera")
BAG = REPO / "Video/recording_20260831_065553.bag"
SOURCE_AUDIT = PROVENANCE / "recorded_context_source.json"
VIDEO1 = REPO / "presentation/v9/videos/embed/VIDEO-1.mp4"
R7UNITY = REPO / "presentation/v9/videos/HANDOVER_UNITY_R7.mp4"
FALLBACK = REPO / "v1/kinematics/dataset/occlusion_masked/unity_occlusion_fallback.mp4"
RAWCSV = PROVENANCE / "filter_demo_raw_r6b.csv"
FILTER_WINDOWS = {
    "filter_hampel_context": (28, 46),
    "filter_gap_context": (679, 692),
    "filter_butterworth_context": (28, 110),
    "filter_one_euro_context": (28, 180),
    "filter_candidate_context": (28, 56),
}
CAMERA_WINDOWS = {
    "filter_hampel_context": (0, 179),
    "filter_gap_context": (600, 749),
    "filter_butterworth_context": (0, 209),
    "filter_one_euro_context": (0, 209),
    "filter_candidate_context": (0, 179),
}
FPS = 30


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def relative(path):
    return str(Path(path).relative_to(REPO))


def run(args):
    subprocess.run([str(a) for a in args], check=True)


def probe(path):
    return json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)
    ]))


def write_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2) + "\n", encoding="ascii")


def audit_source():
    """Verify frame indices, timestamps and cached pixels from the bag."""
    import cv2
    sys.path.insert(0, str(REPO))
    from v3.replay.bag_source import BagSource

    raw = {int(row["frame"]): float(row["time_s"])
           for row in csv.DictReader(RAWCSV.open())}
    records = []
    with BagSource(str(BAG), paced=False) as source:
        for idx, time_s, colour, depth in source.frames():
            path = CACHE / ("cam_%06d.jpg" % idx)
            if not path.exists():
                raise AssertionError("Missing previously extracted colour cache: " + str(path))
            success, encoded = cv2.imencode(".jpg", colour, [cv2.IMWRITE_JPEG_QUALITY, 95])
            assert success
            exact = hashlib.sha256(encoded.tobytes()).hexdigest() == sha(path)
            assert exact, "Cached colour differs from independent bag decode at frame %d" % idx
            assert colour.shape == (480, 640, 3)
            assert depth.shape == (480, 640)
            difference = abs(float(time_s) - raw[idx])
            records.append({"frame": idx, "recorded_relative_seconds": float(time_s),
                            "cache_sha256": sha(path), "cache_matches_decode": exact,
                            "csv_time_difference_seconds": difference})
    assert len(records) > 712
    # CSV times are printed to six decimals; agreement checks the selected
    # indexing but does not assert synchronized playback with the teaching GIF.
    maximum = max(row["csv_time_difference_seconds"] for row in records)
    assert maximum <= 0.000001, "Decoded timestamps do not match the pinned CSV indices"
    result = {
        "status": "PASS", "source_bag": relative(BAG), "source_sha256": sha(BAG),
        "source_decoder": "v3/replay/bag_source.py (read-only import)",
        "source_decoder_sha256": sha(REPO / "v3/replay/bag_source.py"),
        "original_extraction": "anim/causal_replay.py extract --start-frame 0 --duration 30",
        "cache": str(CACHE), "cache_encoding": "JPEG quality 95, OpenCV",
        "native_colour_width": 640, "native_colour_height": 480,
        "decoded_frames": len(records), "source_csv": relative(RAWCSV),
        "source_csv_sha256": sha(RAWCSV),
        "maximum_csv_time_difference_seconds": maximum,
        "interpretation": "Read-only decoding and cache audit; no detector or experiment rerun.",
        "tail_limit": "899 decoded colour/depth pairs; no new dropped-frame measurement is inferred.",
        "frames": records,
    }
    write_json(SOURCE_AUDIT, result)
    print("PASS: %d colour frames match independent bag decode; CSV times agree" % len(records))


def finish_asset(name, width, height, duration, frames, poster_time=0):
    path = MEDIA / (name + ".mp4")
    poster = path.with_suffix(".png")
    run(["ffmpeg", "-y", "-v", "error", "-ss", str(poster_time), "-i", path,
         "-frames:v", "1", poster])
    run(["ffmpeg", "-v", "error", "-i", path, "-f", "null", "-"])
    info = probe(path)
    video = [stream for stream in info["streams"] if stream["codec_type"] == "video"]
    assert len(video) == 1 and len(info["streams"]) == 1
    stream = video[0]
    assert (stream["width"], stream["height"]) == (width, height)
    assert stream["codec_name"] == "h264" and stream["pix_fmt"] == "yuv420p"
    assert stream["r_frame_rate"] == "30/1"
    assert int(stream["nb_frames"]) == frames
    assert abs(float(info["format"]["duration"]) - duration) < 0.0001
    from PIL import Image
    assert Image.open(poster).size == (width, height)
    return {
        "asset": relative(path), "poster": relative(poster), "sha256": sha(path),
        "poster_sha256": sha(poster), "width": width, "height": height,
        "duration_seconds": duration, "frames": frames, "fps": FPS,
        "codec": "h264", "pixel_format": "yuv420p", "audio": False,
        "poster_time_seconds": poster_time, "full_decode": "PASS",
    }


def encode_camera(name, frame_map, source_info, poster_index):
    """Repeat original JPEG frames; do not synthesize intermediate motion."""
    duration = len(frame_map) / FPS
    records = {row["frame"]: row for row in source_info["frames"]}
    unique = sorted(set(frame_map))
    for idx in unique:
        assert sha(CACHE / ("cam_%06d.jpg" % idx)) == records[idx]["cache_sha256"]
    with tempfile.TemporaryDirectory(prefix="defense_recorded_context_") as folder:
        directory = Path(folder)
        for position, idx in enumerate(frame_map):
            os.link(CACHE / ("cam_%06d.jpg" % idx), directory / ("%06d.jpg" % position))
        run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
             "-i", directory / "%06d.jpg", "-frames:v", str(len(frame_map)), "-an",
             "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", MEDIA / (name + ".mp4")])
    mapping_path = PROVENANCE / (name + "_frames.csv")
    with mapping_path.open("w", newline="", encoding="ascii") as stream:
        writer = csv.writer(stream)
        writer.writerow(["output_frame", "output_time_s", "source_frame", "source_recorded_time_s"])
        for position, idx in enumerate(frame_map):
            writer.writerow([position, "%.6f" % (position / FPS), idx,
                             "%.9f" % records[idx]["recorded_relative_seconds"]])
    result = finish_asset(name, 640, 480, duration, len(frame_map), poster_index / FPS)
    result.update({
        "evidence_class": "recorded RGB camera context",
        "source": source_info["source_bag"], "source_sha256": source_info["source_sha256"],
        "source_first_frame": unique[0], "source_last_frame": unique[-1],
        "source_first_time_seconds": records[unique[0]]["recorded_relative_seconds"],
        "source_last_time_seconds": records[unique[-1]]["recorded_relative_seconds"],
        "source_unique_frames": len(unique), "native_content_resolution": [640, 480],
        "crop": None, "resize": None, "intermediate_frame_synthesis": False,
        "frame_map": relative(mapping_path), "frame_map_sha256": sha(mapping_path),
        "qualification": "Recorded task context. Playback is not synchronized to the explanatory animation or an instrumented pipeline trace.",
    })
    return result


def encode_video(name, source, start_frame, frame_count, crop, width, height, poster_time=0):
    # Frame-based trim makes the range unambiguous for 30 fps source videos.
    filters = "trim=start_frame=%d:end_frame=%d,setpts=PTS-STARTPTS" % (
        start_frame, start_frame + frame_count)
    if crop:
        filters += "," + crop
    path = MEDIA / (name + ".mp4")
    run(["ffmpeg", "-y", "-v", "error", "-i", source, "-vf", filters,
         "-frames:v", str(frame_count), "-r", str(FPS), "-an", "-c:v", "libx264",
         "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
         "-movflags", "+faststart", path])
    result = finish_asset(name, width, height, frame_count / FPS, frame_count, poster_time)
    result.update({"source": relative(source), "source_sha256": sha(source),
                   "source_video_first_frame": start_frame,
                   "source_video_last_frame": start_frame + frame_count - 1,
                   "source_video_start_seconds": start_frame / FPS,
                   "source_video_end_exclusive_seconds": (start_frame + frame_count) / FPS,
                   "playback": "Original encoded 30 fps; no holds or retiming.",
                   "spatial_filter": crop, "intermediate_frame_synthesis": False})
    return result


def build():
    MEDIA.mkdir(parents=True, exist_ok=True)
    PROVENANCE.mkdir(parents=True, exist_ok=True)
    source_info = json.loads(SOURCE_AUDIT.read_text())
    assert source_info["status"] == "PASS"
    assert sha(BAG) == source_info["source_sha256"]
    results = []
    for name, (first, last) in CAMERA_WINDOWS.items():
        # A wider contiguous interval gives visible task motion. Half-speed
        # playback repeats each original frame twice, without long holds.
        # The companion numerical plot uses its separate, shorter crop.
        frame_map = [idx for idx in range(first, last + 1) for _ in range(2)]
        assert set(frame_map) == set(range(first, last + 1))
        result = encode_camera(name, frame_map, source_info, 0)
        result["playback"] = {
            "editorial_duration_seconds": len(frame_map) / FPS,
            "speed_relative_to_nominal_30fps": 0.5,
            "initial_hold_seconds": 0, "final_hold_seconds": 0,
            "method": "Each original frame repeated twice; no optical-flow interpolation.",
            "synchronization": "Not synchronized with the independently staged filter plot.",
        }
        result["companion_plot_source_frames_inclusive"] = list(FILTER_WINDOWS[name])
        result["filter_context_scope"] = (
            "Same pinned recording, wider contiguous context around the separately listed plot crop. "
            "Camera image does not display or validate the filter's 3D output.")
        if name == "filter_candidate_context":
            result["intentional_reuse"] = "Shared context for Savitzky-Golay and moving-median candidate demonstrations."
        results.append(result)

    frame_map = list(range(353, 713))
    result = encode_camera("frame_context", frame_map, source_info, frame_map.index(533))
    result["playback"] = "Original indexed frames at nominal 30 fps; recorded timestamps remain in the frame map."
    result["featured_source_frame"] = 533
    result["qualification"] = "Actual R6b camera context containing frame 533. This is not a recording of the memory operations or their timing."
    results.append(result)

    result = encode_video("grip_episode_context", VIDEO1, 0, 180,
                          "crop=960:720:160:0", 960, 720)
    result.update({"evidence_class": "recorded R7 RGB with saved-data overlays",
                   "recording_first_frame": 600, "recording_last_frame": 779,
                   "native_camera_content_resolution": [640, 480],
                   "crop_description": "Black pillarboxes only; existing overlay image is preserved.",
                   "qualification": "Recorded holding context, not grip-state instrumentation or a wholly clean interval. The saved overlay suppresses rejected/masked arm landmarks; right-wrist depth is missing on 705-707 and torso is flagged on 651-758, although torso masking is not drawn.",
                   "source_definition": "presentation/v9/anim/video1_overlay.py"})
    results.append(result)

    result = encode_video("wrist_prediction_context", R7UNITY, 660, 360,
                          "crop=1440:1080:240:0,scale=640:480", 640, 480)
    result.update({"evidence_class": "archived Unity reconstruction replay",
                   "recording_first_frame": 660, "recording_last_frame": 1019,
                   "native_render_content_resolution": [640, 480],
                   "crop_description": "Remove black pillarboxes and return the previously enlarged 4:3 render to native size.",
                   "rig_provenance": "eval/reports/r7_rig_sizing.json: torso override 0.517 m with loop arm constants; not this recording's fitted arm lengths.",
                   "qualification": "Qualitative object/wrist motion context. It does not validate the inferred wrist target, is not the Table 7.4 capture, and is not live-camera validation. Legacy red spheres do not distinguish held and constrained states.",
                   "source_definition": "presentation/v9/anim/handover_unity_clip.py"})
    results.append(result)

    result = encode_video("held_fallback_context", FALLBACK, 75, 240,
                          "crop=960:720:400:170", 960, 720, poster_time=3)
    result.update({"evidence_class": "recorded Unity replay of deliberately masked landmarks",
                   "native_screen_recording_resolution": [1760, 968],
                   "crop_description": "A 960x720 window around the avatar, removing empty background without scaling.",
                   "qualification": "Legacy PSA5 combined masked 20260224 replay: red markers identify held joints. This is deliberate landmark masking, not natural occlusion or object-assisted reconstruction. Video time is not mapped to source experiment frame IDs.",
                   "source_definition": "v1/kinematics/dataset/README.md and occlusion_masked/scenarios.json",
                   "visual_selection": "Encoded video 2.5-10.5 s: held-joint markers are visible around 5.5-6.5 s, followed by resumed motion."})
    results.append(result)

    source_docs = [
        REPO / "v1/kinematics/dataset/README.md",
        REPO / "v1/kinematics/dataset/occlusion_masked/scenarios.json",
        REPO / "eval/reports/r7_rig_sizing.json",
        REPO / "presentation/v9/anim/video1_overlay.py",
        REPO / "presentation/v9/anim/handover_unity_clip.py",
        HERE / "FILTER_DEMO_BRIEF.json",
    ]
    report = {
        "status": "PASS", "scope": "Nine recorded context clips; no detector, reconstruction or experiment rerun.",
        "generator": relative(Path(__file__)), "generator_sha256": sha(__file__),
        "source_audit": relative(SOURCE_AUDIT), "source_audit_sha256": sha(SOURCE_AUDIT),
        "source_documents": [{"path": relative(p), "sha256": sha(p)} for p in source_docs],
        "checks": ["Every R6b cache frame matches a fresh read-only bag decode.",
                   "R6b decoded frame times agree with the pinned CSV to its printed precision.",
                   "Every selected camera frame is original; repeats are fully mapped.",
                   "Every MP4 decodes completely and has the declared frame count/duration.",
                   "All MP4s contain one silent H.264 yuv420p 30 fps stream.",
                   "Posters have the declared output dimensions and saved hashes."],
        "limits": ["Context playback is not synchronized with the explanatory animations.",
                   "No clip supplies a new quantitative accuracy or latency result.",
                   "PowerPoint playback and the proportion of demo pages require final deck validation."],
        "clips": results,
    }
    write_json(REVIEW / "RECORDED_CONTEXT_CHECK.json", report)
    write_json(PROVENANCE / "recorded_context.json", report)
    print("PASS: %d recorded context clips and posters; complete decode and provenance" % len(results))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["audit-source", "build"])
    args = parser.parse_args()
    audit_source() if args.action == "audit-source" else build()
