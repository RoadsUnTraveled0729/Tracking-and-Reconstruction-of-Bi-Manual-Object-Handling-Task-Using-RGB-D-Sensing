"""PSV3 writer round-trip and demo-pattern solve (no Unity needed)."""
import struct

import numpy as np
import pytest

from replay import psv3


def read_packet(path):
    with open(path, "rb") as f:
        return struct.unpack(psv3.FMT, f.read(psv3.SIZE))


def test_layout_matches_reader_contract():
    assert psv3.SIZE == 172
    assert psv3.MAGIC == 0x33565350
    assert len(psv3.LANDMARK_ORDER) == 8


def test_write_and_parse_roundtrip(tmp_path):
    p = str(tmp_path / "v3_person_test")
    w = psv3.PSV3Writer(p)
    pts = {name: np.array([i, i + 0.5, i + 0.25])
           for i, name in enumerate(psv3.LANDMARK_ORDER)}
    angles = np.arange(13, dtype=float)
    status = [0, 1, 2, 0, 1, 2, 0]
    w.write(7, 1.25, pts, angles, status)

    vals = read_packet(p)
    assert vals[0] == psv3.MAGIC
    assert vals[1] % 2 == 0                      # stable seq
    assert vals[2] == 7
    assert vals[3] == pytest.approx(1.25)
    flat = vals[4:4 + 24]
    assert flat[0:3] == pytest.approx((0.0, 0.5, 0.25))
    assert flat[21:24] == pytest.approx((7.0, 7.5, 7.25))
    assert vals[28:41] == pytest.approx(tuple(range(13)))
    assert list(vals[41:48]) == status
    w.close(unlink=True)


def test_write_validates_inputs(tmp_path):
    w = psv3.PSV3Writer(str(tmp_path / "v3_person_test2"))
    pts = {n: np.zeros(3) for n in psv3.LANDMARK_ORDER}
    with pytest.raises(ValueError):
        w.write(0, 0.0, pts, np.zeros(12), [0] * 7)
    with pytest.raises(ValueError):
        w.write(0, 0.0, pts, np.zeros(13), [0] * 6)
    with pytest.raises(ValueError):
        w.write(0, 0.0, pts, np.zeros(13), [0, 0, 0, 0, 0, 0, 5])
    # missing landmark -> NaN in the packet, not an error
    del pts["right_wrist"]
    w.write(0, 0.0, pts, np.zeros(13), [0] * 7)
    w.close(unlink=True)


def test_demo_pattern_solves_finite_angles():
    from tools.psv3_demo_writer import synthetic_points
    from core import convert, solver_q
    for t in np.linspace(0.0, 12.0, 25):
        pts = synthetic_points(t)
        out = solver_q.solve_frame_q(pts)
        assert all(out[k] is not None
                   for k in ("root", "r_sh", "r_elb", "l_sh", "l_elb")), t
        angles = convert.angles13(out["root"], out["r_sh"], out["r_elb"],
                                  out["l_sh"], out["l_elb"])
        assert np.all(np.isfinite(angles)), t
