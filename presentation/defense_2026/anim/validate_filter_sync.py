#!/usr/bin/env python3
"""Independently check synchronized filter maps against recorded sources.

This reads delivered mappings, numerical traces and media. It does not call
the composite generator or rewrite recordings, figures or numerical inputs.
"""
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

import filter_demos

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
BRIEF = json.loads((HERE/"FILTER_SYNC_BRIEF.json").read_text())
AUDIT = json.loads((HERE/"media/provenance/recorded_context_source.json").read_text())
SOURCE = {row["frame"]: row for row in AUDIT["frames"]}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def inspect(name):
    report = json.loads((HERE/"review"/f"{name}_checks.json").read_text())
    assert report["status"] == report["full_decode"] == "PASS"
    spec = BRIEF["specs"][name]
    assert report["spec"] == spec
    for key in ("source_audit", "source_csv", "implementation", "generator", "numerical_helper", "frame_map", "trace_values"):
        assert sha(REPO/report[key]) == report[key+"_sha256"], key
    for key, ext in (("asset", "mp4"), ("poster", "png")):
        assert sha(REPO/report[key]) == report["sha256"][ext], report[key]
    assert report["dimensions"] == BRIEF["dimensions"] == [1440, 1200]
    assert Image.open(REPO/report["poster"]).size == (1440, 1200)
    assert report["poster_source_frame"] == spec["last"]
    rows = list(csv.DictReader((REPO/report["frame_map"]).open()))
    assert len(rows) == report["frames"]
    assert len(rows)/BRIEF["fps"] == report["duration_seconds"]
    assert [int(row["output_frame"]) for row in rows] == list(range(len(rows)))
    current = [int(row["source_frame"]) for row in rows]
    assert current == sorted(current)
    assert sorted(set(current)) == list(range(spec["first"], spec["last"]+1))
    for row in rows:
        idx = int(row["source_frame"]); stamp = SOURCE[idx]["recorded_relative_seconds"]
        assert int(row["plot_visible_through_frame"]) == idx
        assert row["camera_recorded_time_s"] == row["plot_cursor_recorded_time_s"]
        assert abs(float(row["camera_recorded_time_s"])-stamp) < 1e-10
        assert abs(float(row["output_time_s"])-int(row["output_frame"])/BRIEF["fps"]) < 1e-8
    progression = [row for row in rows if row["phase"] == "progression"]
    t0 = SOURCE[spec["first"]]["recorded_relative_seconds"]
    for j, row in enumerate(progression):
        idx = int(row["source_frame"]); clock = t0+j/BRIEF["fps"]*BRIEF["speed"]
        assert SOURCE[idx]["recorded_relative_seconds"] <= clock+1e-10
        if idx < spec["last"]:
            assert SOURCE[idx+1]["recorded_relative_seconds"] > clock-1e-10
    for phase, count, index in [
        ("initial_hold", BRIEF["initial_shared_hold_seconds"]*BRIEF["fps"], spec["first"]),
        ("final_hold", BRIEF["final_shared_hold_seconds"]*BRIEF["fps"], spec["last"]),
        ("event_hold", BRIEF["event_shared_hold_seconds"]*BRIEF["fps"] if spec["event"] is not None else 0, spec["event"]),
    ]:
        selected = [row for row in rows if row["phase"] == phase]
        assert len(selected) == count
        assert all(int(row["source_frame"]) == index for row in selected)
    trace = list(csv.DictReader((REPO/report["trace_values"]).open()))
    assert [int(row["source_frame"]) for row in trace] == list(range(spec["first"], spec["last"]+1))
    method = spec["method"]; axis = spec["axis"]
    result = filter_demos.DATA[method] if method in ("hampel", "gap") else filter_demos.DATA["outputs"][method]
    numeric_errors = []
    for row in trace:
        idx = int(row["source_frame"])
        assert abs(float(row["recorded_time_s"])-SOURCE[idx]["recorded_relative_seconds"]) < 1e-10
        for key, values in [("raw_value_m", filter_demos.DATA["pos"]), ("output_value_m", result)]:
            expected = values[idx, axis]
            if np.isfinite(expected):
                err = abs(float(row[key])-expected); assert err < 1e-10; numeric_errors.append(float(err))
            else:
                assert row[key] == ""
        assert int(row["flagged"]) == filter_demos.DATA["hampel_mask"][idx]
        assert int(row["inferred"]) == filter_demos.DATA["gap_mask"][idx]
        cache = Path(AUDIT["cache"])/f"cam_{idx:06d}.jpg"
        assert sha(cache) == SOURCE[idx]["cache_sha256"]
    visible = report["visible_point_checks"]
    assert sorted(set(row["source_frame"] for row in visible)) == list(range(spec["first"], spec["last"]+1))
    for row in visible:
        idx = row["source_frame"]; segment = slice(spec["first"], idx+1)
        assert row["camera_frame"] == row["visible_through_frame"] == idx
        assert row["future_samples_drawn"] == 0
        assert row["drawn_raw_finite"] == np.isfinite(filter_demos.DATA["pos"][segment, axis]).sum()
        assert row["drawn_output_finite"] == np.isfinite(result[segment, axis]).sum()
    samples = report["first_middle_last_decode_comparisons"]
    assert {0, len(rows)//2, len(rows)-1}.issubset({r["output_frame"] for r in samples})
    assert all(row["source_frame"] == int(rows[row["output_frame"]]["source_frame"]) for row in samples)
    assert all(row["mean_absolute_rgb_error"] < 3 for row in samples)
    return {"asset": name, "status": "PASS", "output_frames": len(rows),
            "source_frames": len(trace), "duration_seconds": report["duration_seconds"],
            "maximum_trace_csv_rounding_error_m": max(numeric_errors),
            "camera_plot_indices_and_timestamps_equal": True,
            "shared_holds_verified": True, "progression_uses_recorded_clock": True,
            "raw_gaps_preserved": True, "no_future_trace_samples": True,
            "source_cache_hashes_verified": True,
            "report_sha256": sha(HERE/"review"/f"{name}_checks.json"),
            "asset_sha256": report["sha256"]}


def main():
    rows = [inspect(name) for name in BRIEF["specs"]]
    previous = json.loads((HERE/"review/media_validation.json").read_text())
    for row in previous:
        assert sha(REPO/row["path"]) == row["sha256"], row["path"]
    result = {"status": "PASS", "assets": rows,
              "prior_media_hashes_unchanged": len(previous),
              "brief_sha256": sha(HERE/"FILTER_SYNC_BRIEF.json"),
              "generator_sha256": sha(HERE/"anim/filter_synchronized.py"),
              "validator_sha256": sha(__file__),
              "fresh_numerical_checks": {key: value for key, value in filter_demos.DATA["checks"].items()
                                         if key != "display_window_history"},
              "scope": "Independent map/trace/source/hash verification; encoding and sampled decoded-pixel comparisons are in the per-asset reports"}
    (HERE/"review/FILTER_SYNC_MAPPING_CHECK.json").write_text(json.dumps(result, indent=2)+"\n", encoding="ascii")
    print(f"PASS: {len(rows)} synchronized assets; all output maps and trace values match; {len(previous)} prior media unchanged")


if __name__ == "__main__":
    main()
