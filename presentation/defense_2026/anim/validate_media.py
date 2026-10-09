#!/usr/bin/env python3
"""Decode all fresh presentation media and preserve technical metadata.

This verifies local files, not playback in PowerPoint on the defence host.
It never changes scientific source files or any movie/GIF.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from functools import lru_cache
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
EXPECTED_SECONDS = {
    "causal_replay": 21, "frame_journey": 36, "grasp_offset": 14,
    "recovery_geometry": 11, "memory_flow": 16, "memory_records": 44,
    "memory_layout": 18, "memory_combine": 10, "memory_race": 16,
    "method_grasp_context": 14, "method_occlusion_context": 11,
    # 1396 native frames at 30 fps (anim/raw_task_context.py SEGMENTS).
    "raw_task_context": 1396 / 30,
    # 510 native frames at 30 fps (anim/raw_handover_task.py SEGMENT, D-304).
    "raw_handover_task": 510 / 30,
    # 240 frames at 30 fps (anim/chain_growth.py TIMELINE, slide 12, D-387).
    "p12_chain_growth": 240 / 30,
    # 1498 frames 0-1497 at 30 fps (anim/three_panel_fk.py FIRST..LAST, slide 33, D-393).
    "p33_three_panel": 1498 / 30,
}
STAGED_SECONDS = {
    "teaching_frame_journey": 48, "teaching_memory_copy": 40,
    "teaching_merge": 40, "teaching_read_write": 48, "teaching_elbow": 36,
    "filter_hampel": 36, "filter_gap": 36, "filter_butterworth": 36,
    "filter_one_euro": 36, "filter_savgol": 36, "filter_median": 36,
    "teaching_memory_copy_restrained": 40, "teaching_merge_restrained": 40,
    "teaching_read_write_restrained": 48,
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@lru_cache(maxsize=14)
def staged_report(name):
    """Require the exact documented new assets; legacy loop checks stay strict."""
    report_path = HERE/"review"/f"{name}_checks.json"
    report = json.loads(report_path.read_text())
    assert report["status"] == "PASS", report_path
    assert report["dimensions"] == [1440, 1080], report_path
    assert report["editorial_duration_seconds"] == STAGED_SECONDS[name], report_path
    assert report["loop_transition"] == "Final held teaching stage restarts at stage one", report_path
    assert report["generator_sha256"] == sha256(HERE/"anim/teaching_flow.py"), report_path
    if name.endswith("_restrained"):
        assert report["variant_generator_sha256"] == sha256(HERE/"anim/teaching_restrained.py"), report_path
        assert report["min_font_px"] == 48, report_path
    elif name == "teaching_elbow":
        assert report["elbow_generator_sha256"] == sha256(HERE/"anim/elbow_steps.py"), report_path
        assert report["geometry_source_sha256"] == sha256(ROOT/report["geometry_source"]), report_path
    elif name.startswith("filter_"):
        assert report["filter_generator_sha256"] == sha256(HERE/"anim/filter_demos.py"), report_path
        assert report["source_csv_sha256"] == sha256(ROOT/report["sources"][0]), report_path
        assert report["implementation_sha256"] == sha256(ROOT/report["sources"][2]), report_path
        assert report["numerical_checks"]["saved_metadata_sha256"] == sha256(ROOT/report["sources"][1]), report_path
    assert report["sha256"]["png"] == sha256(HERE/"media"/f"{name}.png"), report_path
    return report


@lru_cache(maxsize=1)
def recorded_contexts():
    manifest_path = HERE/"media/provenance/recorded_context.json"
    if not manifest_path.exists(): return {}
    manifest = json.loads(manifest_path.read_text())
    assert manifest["status"] == "PASS", manifest_path
    assert manifest["generator_sha256"] == sha256(ROOT/manifest["generator"]), manifest_path
    assert manifest["source_audit_sha256"] == sha256(ROOT/manifest["source_audit"]), manifest_path
    for row in manifest["clips"]:
        assert row["poster_sha256"] == sha256(ROOT/row["poster"]), row["poster"]
    return {row["asset"]: row for row in manifest["clips"]}


@lru_cache(maxsize=1)
def synchronized_filters():
    brief = HERE/"FILTER_SYNC_BRIEF.json"
    if not brief.exists():
        return {}
    from validate_filter_sync import inspect as inspect_synchronization
    names = json.loads(brief.read_text())["specs"]
    return {f"presentation/defense_2026/media/{name}.mp4": inspect_synchronization(name)
            for name in names}


@lru_cache(maxsize=1)
def matched_composites():
    report_path = HERE/"review/MATCHED_EVIDENCE_CHECK.json"
    if not report_path.exists():
        return {}
    report = json.loads(report_path.read_text())
    review_path = HERE/"review/MATCHED_INDEPENDENT_REVIEW.json"
    review = json.loads(review_path.read_text())
    assert report["status"] == review["status"] == "PASS"
    assert report["generator_sha256"] == review["generator_sha256"] == sha256(HERE/"anim/matched_evidence.py")
    assert report["evidence_manifest_sha256"] == review["manifest_sha256"] == sha256(ROOT/report["evidence_manifest"])
    assert review["generation_report_sha256"] == sha256(report_path)
    assert review["review_script_sha256"] == sha256(HERE/"anim/validate_matched_sources.py")
    reviewed = {row["asset"]: row for row in review["assets"]}
    for row in report["assets"]:
        assert row["full_decode"] == "PASS"
        assert row["sha256"] == reviewed[row["name"]]["sha256"]
        assert row["poster_sha256"] == sha256(ROOT/row["poster"])
        assert row["frame_map_sha256"] == sha256(ROOT/row["frame_map"])
    return {row["path"]: row for row in report["assets"]}


def inspect(path):
    info = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]))
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    row = {"path": str(path.relative_to(ROOT)), "width": video["width"],
           "height": video["height"], "codec": video["codec_name"],
           "pix_fmt": video["pix_fmt"], "frame_rate": video["r_frame_rate"],
           "duration_s": float(info["format"]["duration"]), "bytes": path.stat().st_size,
           "audio_streams": sum(s["codec_type"] == "audio" for s in info["streams"]),
           "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
    assert row["audio_streams"] == 0, path
    expected = STAGED_SECONDS.get(path.stem, EXPECTED_SECONDS.get(path.stem))
    if path.stem in STAGED_SECONDS:
        report = staged_report(path.stem)
        assert row["sha256"] == report["sha256"][path.suffix[1:]], path
        assert (row["width"], row["height"]) == (1440, 1080), row
        row["documented_source_hashes_verified"] = True
        row["check_report"] = f"presentation/defense_2026/review/{path.stem}_checks.json"
    context = recorded_contexts().get(row["path"])
    if context:
        expected = context["duration_seconds"]
        assert row["sha256"] == context["sha256"], row
        assert (row["width"], row["height"]) == (context["width"], context["height"]), row
        row["recorded_context_manifest_verified"] = True
    synchronized = synchronized_filters().get(row["path"])
    if synchronized:
        expected = synchronized["duration_seconds"]
        assert row["sha256"] == synchronized["asset_sha256"]["mp4"], row
        assert (row["width"], row["height"]) == (1440, 1200), row
        row["synchronized_camera_plot_maps_verified"] = True
        row["synchronization_check_report_sha256"] = synchronized["report_sha256"]
    matched = matched_composites().get(row["path"])
    if matched:
        expected = matched["duration_s"]
        assert row["sha256"] == matched["sha256"], row
        assert (row["width"], row["height"]) == (matched["width"], matched["height"]), row
        row["matched_source_frame_maps_verified"] = True
        row["matched_source_review_sha256"] = sha256(HERE/"review/MATCHED_INDEPENDENT_REVIEW.json")
    if expected is not None:
        assert abs(row["duration_s"] - expected) < .01, row
    if path.suffix == ".gif":
        im = Image.open(path)
        first = im.convert("RGB").tobytes()
        duration = 0
        for i in range(im.n_frames):
            im.seek(i)
            im.load()
            assert im.size == (row["width"], row["height"]), path
            duration += im.info.get("duration", 0)
        row.update({"stored_gif_frames": im.n_frames, "gif_duration_ms": duration,
                    "gif_loop": im.info.get("loop"),
                    "same_first_last": first == im.convert("RGB").tobytes()})
        assert row["gif_loop"] == 0, row
        # The overview has an explicit end-to-start restart. The separately
        # generated method/detail loops promise an identical closing image.
        if path.stem in STAGED_SECONDS:
            assert not row["same_first_last"], row
            row["loop_classification"] = "Documented staged restart after a held final stage"
        elif path.stem != "frame_journey":
            assert row["same_first_last"], row
            row["loop_classification"] = "Legacy identical first and last images"
        else:
            row["loop_classification"] = "Original frame overview: explicit end-to-start restart"
        if expected is not None:
            assert duration == expected*1000, row
        im.close()
    else:
        assert row["codec"] == "h264" and row["pix_fmt"] == "yuv420p", row
        assert row["frame_rate"] == "30/1", row
        subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"], check=True)
    row["decode_pass"] = True
    return row


def main():
    paths = sorted(p for p in (HERE/"media").rglob("*") if p.suffix in (".gif", ".mp4"))
    rows = []
    old_path = HERE/"review/media_validation.json"
    old = {row["path"]: row["sha256"] for row in json.loads(old_path.read_text())} if old_path.exists() else {}
    for path in paths:
        row = inspect(path)
        if (row["path"] in old and path.stem not in STAGED_SECONDS
                and row["path"] not in recorded_contexts()
                and row["path"] not in synchronized_filters()
                and row["path"] not in matched_composites()):
            assert row["sha256"] == old[row["path"]], path
            row["prior_legacy_hash_unchanged"] = True
        rows.append(row)
        print(f"PASS: {path.name}; {row['duration_s']:g} s; {row['width']}x{row['height']}", flush=True)
    (HERE/"review/media_validation.json").write_text(json.dumps(rows, indent=2)+"\n")
    print(f"PASS: {len(rows)} assets; report review/media_validation.json")


if __name__ == "__main__":
    main()
