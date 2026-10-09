"""bench/aruco_source.py: camera -> levelled world object pose against
the thesis's own world track, rigidity, and the V3/ArUco frame
alignment (D-035)."""
import json

import numpy as np
import pandas as pd
import pytest

from bench import aruco_source as src

V3 = src.V3_ROOT


def _need(*paths):
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        pytest.skip(f"inputs absent: {missing}")


def test_object_world_matches_thesis_track():
    """Raw scaled ArUco -> levelled world equals the thesis path
    (<stem>_scaled_object_world.csv through carry.py object_world).
    Position to 1e-9 m; rotation to 1e-5 (the ArUco CSV stores the
    camera rotation with 6 decimals, the thesis track was computed from
    full precision)."""
    stem = src.STEMS["r4"]
    ow_csv = src.EVAL_OUT / f"{stem}_scaled_object_world.csv"
    _need(src.aruco_csv(stem), ow_csv, src.calib_path("r4"))
    world = src.load_world("r4")
    o = src.read_object(stem, world)
    ow = pd.read_csv(ow_csv)
    d = ow["detected"].to_numpy() == 1
    assert np.array_equal(o["det"], d)
    obj, R = world.object_world(
        ow[["unity_px", "unity_py", "unity_pz"]].to_numpy()[d],
        ow[["unity_ex", "unity_ey", "unity_ez"]].to_numpy()[d])
    assert np.max(np.abs(o["obj"][d] - obj)) < 1e-9
    assert np.max(np.abs(o["R_obj"][d] - R)) < 1e-5
    assert np.isnan(o["obj"][~d]).all()


def test_world_transform_is_rigid_and_centre_offset():
    _need(src.calib_path("r4"))
    world = src.load_world("r4")
    rng = np.random.default_rng(0)
    p = rng.normal(size=(50, 3))
    q = world.world_from_cam(p)
    dp = np.linalg.norm(p[1:] - p[:-1], axis=1)
    dq = np.linalg.norm(q[1:] - q[:-1], axis=1)
    assert np.max(np.abs(dp - dq)) < 1e-12
    Rc = np.array([np.linalg.qr(rng.normal(size=(3, 3)))[0]
                   for _ in range(20)])
    Rc *= np.sign(np.linalg.det(Rc))[:, None, None]
    Rw = world.rot_from_cam(Rc)
    assert np.allclose(np.linalg.det(Rw), 1.0)
    c = world.box_center(q[:20], Rw)
    assert np.allclose(np.linalg.norm(c - q[:20], axis=1), world.cube / 2)


@pytest.mark.parametrize("alias", ["r4", "r5", "r6b", "r7"])
def test_frame_alignment_within_half_frame(alias):
    """V3 extraction frame i and ArUco row i are the same frameset:
    time_s agrees within half a frame on every frame (D-035)."""
    stem = src.STEMS[alias]
    cfg = json.loads((V3 / "configs/default.json").read_text())
    variant = cfg["model"]["variant"]
    csv = V3 / "output/objects" / f"extraction_{stem}__{variant}.csv"
    _need(csv, src.aruco_csv(stem), src.calib_path(alias))
    df = pd.read_csv(csv, usecols=["frame", "time_s"])
    obj = src.align(src.read_object(stem, src.load_world(alias)),
                    df["frame"].to_numpy())
    al = src.check_alignment(obj["time_s"], df["time_s"].to_numpy())
    assert al["ok"], al
    assert al["n"] == len(df)
