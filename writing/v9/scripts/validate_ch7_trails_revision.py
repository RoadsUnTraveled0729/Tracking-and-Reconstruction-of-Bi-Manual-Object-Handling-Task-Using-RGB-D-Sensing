#!/usr/bin/env python3
"""Verify source preservation, phase captures and embedded figure identity."""
import hashlib
import json
from zipfile import ZipFile

import numpy as np
import pandas as pd
from ch7_trail_data import ANGLES, REPO, ROOT, load, intervals


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    protected = json.loads((ROOT / "ch7_trails_source_hashes.json").read_text())
    for name, original in protected.items():
        path = REPO / name
        assert path.stat().st_size == original["bytes"], name
        assert digest(path) == original["sha256"], name
    print(f"PASS: {len(protected)} source files unchanged, including original recording and saved results")

    data = load()
    config = json.loads((ROOT / "figures/ch7_trails_view.json").read_text())
    assert config["phases"] == data["phases"]
    for name, stored_name in (("marker", "cube"), ("wrist", "wrist"), ("reference", "reference")):
        points = np.array([[p[k] for k in ("x", "y", "z")] for p in config[name]])
        frames = np.array([p["frame"] for p in config[name]])
        assert np.array_equal(points, data[stored_name]["points"]), name
        assert np.array_equal(frames, data[stored_name]["frames"]), name
    assert np.array_equal([p["state"] for p in config["wrist"]], data["wrist"]["states"])
    # The drawn states are measured (0) and rebuilt (2) only. A held group
    # (tag 1) would need its own display style; check the source tags
    # directly, because load() lets a rebuilt tag override a held one.
    tags = pd.read_csv(ANGLES).set_index("frame").loc[data["wrist"]["frames"], ["tag_1", "tag_3"]].to_numpy(int)
    assert not (tags == 1).any(), "Held state requires its own display style"
    assert set(np.unique(tags)) <= {0, 2}, "Unexpected tag value in the right swing or elbow group"
    print("PASS: every exported point, frame and wrist state equals its saved source")
    print("Recovery intervals:", intervals(data["wrist"]["frames"], data["wrist"]["states"] == 2))

    source = ROOT / "figures/src/ch7_trails_revision"
    # The accepted capture is pinned by render_ch7_trails.py: every still,
    # record and receiver log at its recorded digest, and the view config
    # the stills were rendered from. A stale still or log cannot pass.
    manifest = json.loads((source / "manifest.json").read_text())
    assert manifest["view_config_sha256"] == digest(ROOT / "figures/ch7_trails_view.json"), "View config changed since the capture"
    for name, entry in manifest["files"].items():
        path = source / name
        assert path.stat().st_size == entry["bytes"] and digest(path) == entry["sha256"], name
    for phase in data["phases"]:
        for ext in (".png", ".json"):
            assert phase["name"] + ext in manifest["files"], phase["name"] + ext
    for name in ("unity_object_log.csv", "unity_person_log.csv"):
        assert name in manifest["files"], name
    print(f"PASS: capture manifest of {manifest['launched']} matches {len(manifest['files'])} files and the view config")
    compose = json.loads((ROOT / "figures/ch7_trails_compose.json").read_text())
    assert compose["manifest_sha256"] == digest(source / "manifest.json"), "Figure 7.10 was composed from another capture"
    assert compose["figure_sha256"] == digest(ROOT / "figures/ch7_fig_unity_trails.png"), "Figure 7.10 changed since it was composed"
    print("PASS: Figure 7.10 composed from this capture")
    stream = pd.read_csv(REPO / "eval/output/unity_check_r6b_trails/integrated_stream.csv").set_index("frame")
    obj = pd.read_csv(source / "unity_object_log.csv").set_index("frame")
    person = pd.read_csv(source / "unity_person_log.csv").set_index("frame")
    camera = None
    for phase in data["phases"]:
        record = json.loads((source / (phase["name"] + ".json")).read_text())
        frame = phase["last"]
        assert record["appliedFrame"] == frame
        assert record["first"] == phase["first"] and record["last"] == frame
        current_camera = [record[k] for k in ("cameraPosition", "cameraTarget", "orthographicSize")]
        if camera is None:
            camera = current_camera
        assert camera == current_camera, "Camera changed between panels"
        # Frozen receiver logs six decimals; 1 micrometre allows their rounding
        # plus float32 packet conversion. This is serialization, not accuracy.
        assert np.allclose(obj.loc[frame, ["px", "py", "pz"]],
                           stream.loc[frame, ["opx", "opy", "opz"]], atol=1e-6, rtol=0)
        assert np.allclose(person.loc[frame, ["pel_x", "pel_y", "pel_z"]],
                           stream.loc[frame, ["pel_x", "pel_y", "pel_z"]], atol=1e-6, rtol=0)
        assert (source / (phase["name"] + ".png")).exists()
        print(f"PASS: {phase['name']} frames {phase['first']}-{frame}, saved endpoint pose applied")

    for path in (ROOT / "Chapter_7_Evaluation.docx", REPO / "writing/v9/Thesis_V9.docx"):
        with ZipFile(path) as archive:
            hashes = {hashlib.sha256(archive.read(name)).hexdigest()
                      for name in archive.namelist() if name.startswith("word/media/")}
        for image in ("ch7_fig_rail_traj.png", "ch7_fig_wrist_traj.png", "ch7_fig_combined.png", "ch7_fig_unity_trails.png"):
            assert digest(ROOT / "figures" / image) in hashes, (path, image)
        print("PASS: revised trajectory figures embedded exactly in", path.name)
    print("PASS: preservation and presentation checks complete; no new accuracy result claimed")


if __name__ == "__main__":
    main()
