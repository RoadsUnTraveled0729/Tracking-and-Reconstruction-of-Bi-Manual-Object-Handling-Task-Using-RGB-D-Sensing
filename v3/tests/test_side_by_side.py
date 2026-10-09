"""M8a side-by-side films (tools/side_by_side.py, tools/render_rig.py;
D-039): projection, cube geometry, frame picking, occlusion summary,
a 20-frame smoke film and the manifest schema."""
import copy
import json
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from tools import render_rig as rr
from tools import side_by_side as sbs

V3 = Path(__file__).resolve().parents[1]
INTR = {"fx": 600.0, "fy": 610.0, "ppx": 320.0, "ppy": 240.0}


def test_projection_known_point():
    """Unity (0.1, -0.05, 1.0) is camera optical (0.1, 0.05, 1.0):
    u = 600 * 0.1 + 320 = 380, v = 610 * 0.05 + 240 = 270.5 in the
    640x480 source, x 1.2 in the 768x576 panel."""
    uv = rr.unity_projector(INTR)(np.array([0.1, -0.05, 1.0]))
    assert np.allclose(uv, [380.0 * 1.2, 270.5 * 1.2], atol=1e-12)
    uv_c = rr.camera_projector(INTR)(np.array([0.1, 0.05, 1.0]))
    assert np.allclose(uv_c, uv, atol=1e-12)
    bad = rr.unity_projector(INTR)(np.array([[0.0, 0.0, -1.0],
                                             [np.nan, 0.0, 1.0]]))
    assert np.isnan(bad).all()


def test_projection_matches_realsense():
    rs = pytest.importorskip("pyrealsense2")
    metas = sorted((V3 / "output" / "clean").glob("*__rtmpose-l.meta.json"))
    if not metas:
        pytest.skip("no extraction meta.json")
    m = json.loads(metas[0].read_text())["intrinsics"]
    assert all(c == 0 for c in m["coeffs"])
    ri = rs.intrinsics()
    ri.width, ri.height = m["width"], m["height"]
    ri.fx, ri.fy, ri.ppx, ri.ppy = m["fx"], m["fy"], m["ppx"], m["ppy"]
    ri.model = rs.distortion.inverse_brown_conrady
    ri.coeffs = [0.0] * 5
    rng = np.random.default_rng(39)
    P = np.c_[rng.uniform(-0.5, 0.5, (50, 2)), rng.uniform(0.5, 2.5, 50)]
    ours = rr.camera_projector(m)(P) / rr.CAMERA_SCALE
    ref = np.array([rs.rs2_project_point_to_pixel(ri, list(p)) for p in P])
    assert np.max(np.abs(ours - ref)) < 1e-3


def test_cube_centre_matches_aruco_source():
    """Camera-frame cube centre -> levelled world equals
    bench/aruco_source.py box_center (carry.py) on R4."""
    from bench import aruco_source as src
    if not src.aruco_csv(src.STEMS["r4"]).exists():
        pytest.skip("R4 ArUco CSV absent")
    world = src.load_world("r4")
    obj = src.read_object(src.STEMS["r4"], world)
    idx = np.flatnonzero(obj["det"])[::50]
    assert idx.size > 5
    for i in idx:
        c_cam, corners = rr.cube_geometry(obj["obj_cam"][i], obj["R_cam"][i],
                                          world.cube)
        c_world = world.world_from_cam(c_cam)[0]
        assert np.max(np.abs(c_world - obj["center"][i])) < 1e-9
        # the eight corners are cube/2 * sqrt(3) from the centre
        d = np.linalg.norm(corners - c_cam, axis=1)
        assert np.allclose(d, world.cube / 2 * np.sqrt(3), atol=1e-9)


def test_pick_contact_frames():
    S = np.zeros((200, 7), int)
    S[80:120, 1] = 1            # one estimated episode 80..119
    S[95:100, 2] = 2
    picks, ep = sbs.pick_contact_frames(S)
    assert ep == (80, 119)
    tags = [t for t, _ in picks]
    assert tags == ["clean"] * 2 + ["entering"] * 2 + ["during"] * 2 \
        + ["reacquiring"] * 2
    idx = dict(zip(range(8), [i for _, i in picks]))
    assert (idx[2], idx[3]) == (79, 80)
    assert 80 <= idx[4] < idx[5] <= 119
    assert (idx[6], idx[7]) == (120, 120 + sbs.REACQ_SETTLE_FRAMES)
    assert all(S[i].max() == 0 for _, i in picks[:2])
    picks, ep = sbs.pick_contact_frames(np.zeros((50, 7), int))
    assert ep is None and len(picks) == 8


def test_occlusion_summary_step_at_reacquisition():
    n = 100
    A = np.zeros((n, 13))
    A[:, 6] = np.linspace(-90, -60, n)          # r_elbow_y ramp 0.303/frame
    A[60:, 6] += 2.0                            # a 2 deg jump at frame 60
    S = np.zeros((n, 7), int)
    S[40:60, 3] = 1                             # R_elbow estimated 40..59
    bend = {"right": np.full(n, 60.0), "left": np.full(n, 60.0)}
    budgets = {a: 4.0 for a in sbs.ANGLE_NAMES}
    out = sbs.occlusion_summary({"A": A, "status": S, "bend": bend},
                                budgets, 30.0, first_valid=0)
    g = out["R_elbow"]
    assert g["estimated_runs"] == 1 and g["estimated_len"] == [20]
    (rq,) = g["reacquisitions"]
    assert rq["frame_local"] == 60 and rq["step_angle"] == "r_elbow_y"
    assert rq["step_deg"] == pytest.approx(2.0 + 30.0 / 99, abs=1e-9)
    assert rq["gated_ratio"] == pytest.approx(rq["step_deg"] / 4.0)
    assert out["R_swing"]["reacquisitions"] == []
    # twist steps at a bend below the threshold are exempt
    A2 = A.copy()
    A2[60:, 5] += 50.0
    S2 = S.copy()
    S2[40:60, 2] = 1
    bend2 = {"right": np.full(n, 10.0), "left": np.full(n, 60.0)}
    out2 = sbs.occlusion_summary({"A": A2, "status": S2, "bend": bend2},
                                 budgets, 30.0)
    assert out2["R_twist"]["reacquisitions"][0]["gated_ratio"] == 0.0
    assert out2["R_twist"]["reacquisitions"][0]["step_deg"] == \
        pytest.approx(50.0)
    # the warmup excludes early steps
    out3 = sbs.occlusion_summary({"A": A, "status": S, "bend": bend},
                                 budgets, 30.0, first_valid=70)
    assert out3["R_elbow"]["reacquisitions"] == []
    assert out3["_warmup"]["warmup_max_ratio"] == pytest.approx(
        (2.0 + 30.0 / 99) / 4.0)


def _smoke_sources():
    src = sbs.resolve("right_elbow", "rtmpose-l")
    if not src["csv"].exists():
        pytest.skip("clean-window extraction CSV absent")
    if src["bag"] is None or not Path(src["bag"]).exists():
        pytest.skip("clean-window bag absent")
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        pytest.skip("ffmpeg absent")
    pytest.importorskip("pyrealsense2")
    return src


def test_smoke_film_20_frames(tmp_path):
    _smoke_sources()
    r = subprocess.run(
        [sys.executable, str(V3 / "tools" / "side_by_side.py"),
         "--recording", "right_elbow", "--start", "180", "--stop", "199",
         "--no-pin", "--out-dir", str(tmp_path)],
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr
    film = tmp_path / "side_by_side_right_elbow__rtmpose-l.mp4"
    info = sbs.probe(film)
    assert info["frames"] == 20
    assert (info["width"], info["height"]) == (1536, 576)
    assert info["codec"] == "h264" and info["pix_fmt"] == "yuv420p"
    assert info["r_frame_rate"] == "30/1"
    side = json.loads(film.with_suffix(".json").read_text())
    assert side["frames"] == 20 and side["start"] == 180
    assert side["max_abs_dt_bag_vs_csv_s"] < 0.5 * side["source_period_s"]
    fr = side["status_fractions"]
    assert set(fr) == set(sbs.GROUP_NAMES)
    # nothing pinned by a --no-pin run
    assert side["contact_sheet"] is None


def _fake_manifest():
    fr = {g: {"measured": 0.5, "estimated": 0.25, "lost": 0.25,
              "frames": 4} for g in sbs.GROUP_NAMES}
    film = {"name": "x", "kind": "clean", "stem": "x", "variant": "v",
            "film": "v3/output/side_by_side/x.mp4", "film_sha256": "0" * 64,
            "film_bytes": 1, "duration_s": 1.0, "frames": 30, "fps": 30.0,
            "half_speed": False, "start": 0, "stop": 29,
            "status_fractions": fr, "config_sha256": "0" * 64,
            "contact_sheet": None}
    return {"schema": sbs.SCHEMA, "created": "now", "git_commit": "abc",
            "variant": "v", "encoder": sbs.ENCODER, "films": [film]}


def test_manifest_schema_validator():
    m = _fake_manifest()
    assert sbs.validate_manifest(m)
    for broken in ("schema", "films"):
        b = copy.deepcopy(m)
        del b[broken]
        with pytest.raises(ValueError):
            sbs.validate_manifest(b)
    b = copy.deepcopy(m)
    del b["films"][0]["film_sha256"]
    with pytest.raises(ValueError):
        sbs.validate_manifest(b)
    b = copy.deepcopy(m)
    b["films"][0]["status_fractions"]["root"]["lost"] = 0.5
    with pytest.raises(ValueError):
        sbs.validate_manifest(b)


def test_pinned_manifest():
    if not sbs.MANIFEST.exists():
        pytest.skip("manifest not pinned yet")
    m = json.loads(sbs.MANIFEST.read_text())
    sbs.validate_manifest(m)
    names = [f["name"] for f in m["films"] if not f["half_speed"]]
    assert names == list(sbs.RECORDING_ORDER + sbs.CLEAN_ORDER)
    for f in m["films"]:
        cs = f["contact_sheet"]
        p = V3.parent / cs["path"]
        assert p.exists() and p.stat().st_size <= sbs.CONTACT_MAX_BYTES
        assert sbs.sha256(p) == cs["sha256"]
        assert len(cs["frames"]) == 8
        assert f["frames"] == f["stop"] - f["start"] + 1
