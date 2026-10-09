"""Pure-numpy tests for the replay modules (no pyrealsense2 device,
no onnxruntime): depth sampling and the causal filter."""
import json
from pathlib import Path

import numpy as np
import pytest

from replay.causal_filter import CausalLandmarkFilter, OneEuro
from replay.depth_sampler import sample_depth

V3_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def filter_cfg():
    with open(V3_ROOT / "configs" / "default.json") as f:
        return json.load(f)["filter"]


def test_sample_depth_median_and_holes():
    depth = np.zeros((10, 10), dtype=np.uint16)
    depth[4:7, 4:7] = [[100, 200, 300], [400, 500, 600], [700, 800, 900]]
    # median over the nonzero values of the 5x5 patch centered at (5,5)
    assert sample_depth(depth, 0.001, 5, 5, 5) == pytest.approx(0.5)
    # window 1 reproduces the single-pixel sample
    assert sample_depth(depth, 0.001, 4, 4, 1) == pytest.approx(0.1)
    # all-zero patch = depth hole
    assert sample_depth(depth, 0.001, 1, 1, 3) == 0.0
    # zeros inside the window are excluded, not averaged in
    depth2 = np.zeros((10, 10), dtype=np.uint16)
    depth2[5, 5] = 1000
    assert sample_depth(depth2, 0.001, 5, 5, 5) == pytest.approx(1.0)
    # clamped at the image border: no exception
    assert sample_depth(depth, 0.001, 0, 0, 5) == 0.0


def test_one_euro_first_sample_passthrough_and_smoothing():
    f = OneEuro(30.0, 1.0, 1.0)
    assert f(5.0) == 5.0
    rng = np.random.default_rng(0)
    base = 2.0
    f2 = OneEuro(30.0, 1.0, 0.0)
    outs = [f2(base + rng.normal(scale=0.05)) for _ in range(300)]
    assert np.std(outs[50:]) < 0.05                # tighter than the noise


def test_causal_filter_passthrough_and_missing(filter_cfg):
    filt = CausalLandmarkFilter(filter_cfg)
    assert filt("right_wrist", None) is None
    out = filt("right_wrist", np.array([0.1, 0.2, 0.5]))
    assert np.allclose(out, [0.1, 0.2, 0.5])       # first sample seeds


def test_causal_filter_rejects_spike_then_accepts_motion(filter_cfg):
    filt = CausalLandmarkFilter(filter_cfg)
    p = np.array([0.0, 0.0, 1.0])
    for _ in range(8):
        filt("right_wrist", p)                     # fill the window
    spike = p + np.array([0.0, 0.0, 0.5])          # 500 mm jump
    assert filt("right_wrist", spike) is None      # rejected
    assert filt("right_wrist", p) is not None      # normal sample passes
    # a persistent jump is real motion: after max_rejects rejections
    # the window reseeds and the sample is accepted
    rejected = 0
    out = None
    for _ in range(filter_cfg["despike_max_rejects"] + 1):
        out = filt("right_wrist", spike)
        if out is None:
            rejected += 1
    assert rejected == filter_cfg["despike_max_rejects"]
    assert out is not None


def test_causal_filter_small_motion_never_rejected(filter_cfg):
    filt = CausalLandmarkFilter(filter_cfg)
    p = np.array([0.0, 0.0, 1.0])
    for i in range(60):
        out = filt("left_elbow", p + [0.0, 0.0, 0.0005 * i])  # 0.5 mm/frame
        assert out is not None
