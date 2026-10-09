"""Tests for bench/oracle.py (D-024): the offline zero-phase oracle.

Synthetic tests run everywhere (numpy, pandas, scipy). The
reproduction tests read the defence-film bank read-only and skip when
it is absent:
- the film's raw MediaPipe landmarks (bank_processing/p19 = page 16,
  right_elbow; p17 = page 14, 180042) through the V3 reimplementation
  must give the film's landmarks_filtered.csv to the CSV rounding of
  that file (%.6f -> 5e-7 m) with identical provenance flags;
- the oracle angles must reproduce the film's derived right-arm and
  root angles (unified_four/pNN/derived_kinematics.csv) to 0.01 deg
  in the film window (the film solved the %.6f-rounded filtered file;
  the bound covers that rounding: measured max 0.0041 deg, twist p16),
  and solving the film's filtered file directly must match to 1e-8 deg.
"""
import copy
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from bench import oracle
from bench.metrics import best_lag, wrap_deg
from core.skeleton import V1_LANDMARKS

V3_ROOT = Path(__file__).resolve().parents[1]
REPO = V3_ROOT.parent
BANK = REPO / "presentation/defense_2026/bank_processing"
# (film page, extraction folder, window start, window stop inclusive);
# windows from configs/clean_windows.json (D-025)
FILM = {16: ("p19", 180, 540), 14: ("p17", 3, 109)}
FILM_ANGLES = {"sh_y": "r_swing_y", "sh_z": "r_swing_z",
               "sh_twist": "r_twist", "el_y": "r_elbow_y",
               "el_z": "r_elbow_z", "root_ex": "root_x",
               "root_ey": "root_y", "root_ez": "root_z"}
CSV_ROUND_M = 5e-7 + 1e-12   # half the last digit of %.6f


@pytest.fixture(scope="module")
def cfg():
    with open(V3_ROOT / "configs/default.json") as f:
        return json.load(f)


def _pose_df(n, fs=30.0, motion=None):
    """Synthetic extraction: a fixed plausible pose (camera frame),
    optionally plus motion(name, t) -> (n, 3) offsets."""
    base = {
        "left_shoulder": [0.30, -0.35, 2.00],
        "right_shoulder": [-0.10, -0.35, 2.01],
        "left_elbow": [0.55, -0.31, 1.96],
        "right_elbow": [-0.36, -0.29, 1.98],
        "left_wrist": [0.77, -0.36, 1.94],
        "right_wrist": [-0.57, -0.27, 1.90],
        "left_hip": [0.23, 0.17, 1.93],
        "right_hip": [0.02, 0.18, 1.90],
    }
    t = np.arange(n) / fs
    cols = {"frame": np.arange(n), "time_s": t}
    for name in V1_LANDMARKS:
        p = np.tile(np.asarray(base[name], dtype=float), (n, 1))
        if motion is not None:
            p = p + motion(name, t)
        for c, ax in enumerate("xyz"):
            cols[f"{name}_{ax}"] = p[:, c]
    return pd.DataFrame(cols)


# ---------------------------------------------------------------- config

def test_oracle_block_matches_film_settings(cfg):
    o = cfg["oracle"]
    # bank_axes_kinematics.py lines 217-220 + filter_landmarks.py
    assert o["hampel_window"] == 7
    assert o["hampel_k"] == 3.0
    assert o["hampel_floor_m"] == 0.02
    assert o["hampel_min_periods"] == 3
    assert o["mad_scale"] == 1.4826
    assert o["max_gap"] == 5
    assert o["edge_fill"] == 0
    assert o["butter_order"] == 4
    assert o["cutoff_hz"] == 3.0
    assert o["fs"] == "median_dt"


def test_null_oracle_value_fails_loudly(cfg):
    bad = copy.deepcopy(cfg)
    bad["oracle"]["cutoff_hz"] = None
    with pytest.raises(ValueError):
        oracle.filter_landmarks(_pose_df(40), bad)
    bad = copy.deepcopy(cfg)
    del bad["oracle"]
    with pytest.raises(KeyError):
        oracle.filter_landmarks(_pose_df(40), bad)


# ---------------------------------------------------------- synthetic

def test_constant_input_is_identity(cfg):
    df = _pose_df(120)
    filt, flags, fs = oracle.filter_landmarks(df, cfg)
    assert fs == pytest.approx(30.0)
    raw = oracle.read_landmarks(df)
    for name in V1_LANDMARKS:
        assert np.max(np.abs(filt[name] - raw[name])) < 1e-12
        assert np.all(flags[name] == oracle.FLAG_RAW)
    a_or = oracle.solve_table(df, filt)
    a_raw = oracle.solve_table(df, raw)
    from bench.metrics import ANGLE_NAMES
    A = a_or[list(ANGLE_NAMES)].to_numpy()
    R = a_raw[list(ANGLE_NAMES)].to_numpy()
    assert np.all(np.isfinite(A))
    assert np.max(np.abs(wrap_deg(A - R))) < 1e-9
    assert np.max(np.abs(wrap_deg(A - A[0]))) < 1e-9


def _amp_ratio(freq_hz, amp=0.005, n=900, fs=30.0, cfg=None):
    """Steady-state amplitude ratio of the full landmark filter on a
    sinusoid of one axis (edges excluded)."""
    def motion(name, t):
        m = np.zeros((len(t), 3))
        if name == "right_wrist":
            m[:, 0] = amp * np.sin(2 * np.pi * freq_hz * t)
        return m
    df = _pose_df(n, fs, motion)
    filt, flags, _ = oracle.filter_landmarks(df, cfg)
    assert np.all(flags["right_wrist"] == oracle.FLAG_RAW)  # no Hampel hit
    core = slice(n // 4, 3 * n // 4)
    x_in = oracle.read_landmarks(df)["right_wrist"][core, 0]
    x_out = filt["right_wrist"][core, 0]
    return np.std(x_out - x_out.mean()) / np.std(x_in - x_in.mean())


def test_sinusoid_attenuation_at_cutoff(cfg):
    # filtfilt squares |H|: at the 3 Hz cutoff |H|^2 = 1/2 exactly
    assert _amp_ratio(3.0, cfg=cfg) == pytest.approx(0.5, abs=0.01)
    assert _amp_ratio(0.5, cfg=cfg) > 0.99
    assert _amp_ratio(8.0, cfg=cfg) < 0.01


def test_zero_lag_by_construction(cfg):
    def motion(name, t):
        m = np.zeros((len(t), 3))
        if name == "right_elbow":
            m[:, 1] = 0.004 * np.sin(2 * np.pi * 1.0 * t)
        return m
    df = _pose_df(600, 30.0, motion)
    filt, _, _ = oracle.filter_landmarks(df, cfg)
    x_in = oracle.read_landmarks(df)["right_elbow"][60:-60, 1]
    x_out = filt["right_elbow"][60:-60, 1]
    lag, _ = best_lag(x_out * 1000, x_in * 1000, max_lag=10)
    assert lag == 0
    # an asymmetric bump keeps its centroid (zero phase, not only a
    # symmetric-signal coincidence)
    n = 301
    t = np.arange(n) / 30.0
    bump = np.zeros((n, 3))
    k = np.arange(n) - 140.0
    bump[:, 2] = 0.01 * np.exp(-np.clip(k, 0.0, None) / 8.0) * (k >= 0)
    bump[:, 2] += 0.01 * np.exp(-0.5 * ((np.arange(n) - 150) / 12.0) ** 2)
    out = oracle.butter_segments(bump, 1.0 / np.median(np.diff(t)), 4, 3.0)
    c_in = np.sum(np.arange(n) * bump[:, 2]) / np.sum(bump[:, 2])
    c_out = np.sum(np.arange(n) * out[:, 2]) / np.sum(out[:, 2])
    assert abs(c_out - c_in) < 1e-3


def test_hampel_removes_spike_and_interpolates(cfg):
    df = _pose_df(60)
    df.loc[30, "right_wrist_x"] += 0.10          # 10 cm spike
    filt, flags, _ = oracle.filter_landmarks(df, cfg)
    assert flags["right_wrist"][30] == oracle.FLAG_GLITCH_INTERP
    assert np.sum(flags["right_wrist"] != oracle.FLAG_RAW) == 1
    # constant neighbours -> interpolated value is the constant
    assert filt["right_wrist"][30, 0] == pytest.approx(
        df.loc[29, "right_wrist_x"], abs=1e-12)


def test_small_deviation_below_floor_kept(cfg):
    df = _pose_df(60)
    df.loc[30, "right_wrist_x"] += 0.019         # under the 0.02 m floor
    _, flags, _ = oracle.filter_landmarks(df, cfg)
    assert np.all(flags["right_wrist"] == oracle.FLAG_RAW)


def test_gap_fill_limits(cfg):
    df = _pose_df(80)
    df.loc[20:24, ["left_elbow_x", "left_elbow_y", "left_elbow_z"]] = np.nan
    df.loc[40:45, ["right_elbow_x", "right_elbow_y", "right_elbow_z"]] = np.nan
    df.loc[0:1, ["left_hip_x", "left_hip_y", "left_hip_z"]] = np.nan
    filt, flags, _ = oracle.filter_landmarks(df, cfg)
    assert np.all(flags["left_elbow"][20:25] == oracle.FLAG_MISS_INTERP)
    assert np.all(np.isfinite(filt["left_elbow"][20:25]))
    assert np.all(flags["right_elbow"][40:46] == oracle.FLAG_MISS)  # 6 > 5
    assert np.all(np.isnan(filt["right_elbow"][40:46]))
    assert np.all(flags["left_hip"][0:2] == oracle.FLAG_MISS)       # edge
    # the unsolvable frames carry NaN angles only for the dead groups
    tab = oracle.solve_table(df, filt)
    assert np.isnan(tab.loc[42, "r_elbow_y"])
    assert np.isnan(tab.loc[42, "r_twist"])
    assert np.isfinite(tab.loc[42, "l_elbow_y"])
    assert np.isnan(tab.loc[0, "root_x"]) and np.isnan(tab.loc[0, "l_swing_y"])


# ------------------------------------------------ film reproduction

def _need(path):
    if not Path(path).exists():
        pytest.skip(f"not on disk: {path}")


@pytest.mark.parametrize("page", sorted(FILM))
def test_reproduces_film_filtered_file(cfg, page):
    ext, s0, s1 = FILM[page]
    raw_p = BANK / ext / "landmarks_raw.csv"
    ref_p = BANK / ext / "landmarks_filtered.csv"
    _need(raw_p)
    _need(ref_p)
    raw = pd.read_csv(raw_p)
    ref = pd.read_csv(ref_p)
    filt, flags, _ = oracle.filter_landmarks(raw, cfg)
    for name in V1_LANDMARKS:
        r = ref[[f"{name}_{a}" for a in "xyz"]].to_numpy(float)
        assert np.array_equal(np.isnan(filt[name]), np.isnan(r)), name
        assert np.nanmax(np.abs(filt[name] - r)) <= CSV_ROUND_M, name
        assert np.array_equal(flags[name], ref[f"{name}_flag"].to_numpy()), name
        w = slice(s0, s1 + 1)
        assert np.all(np.isfinite(filt[name][w])), name


@pytest.mark.parametrize("page", sorted(FILM))
def test_oracle_angles_reproduce_film_angles(cfg, page):
    ext, s0, s1 = FILM[page]
    raw_p = BANK / ext / "landmarks_raw.csv"
    filt_p = BANK / ext / "landmarks_filtered.csv"
    film_p = BANK / f"unified_four/p{page}/derived_kinematics.csv"
    for p in (raw_p, filt_p, film_p):
        _need(p)
    film = pd.read_csv(film_p).set_index("frame").loc[s0:s1]
    o = oracle.oracle_angles(raw_p, cfg)
    fdf = pd.read_csv(filt_p)
    solved = oracle.solve_table(fdf, oracle.read_landmarks(fdf))
    w = slice(s0, s1 + 1)
    for fa, va in FILM_ANGLES.items():
        ref = film[fa].to_numpy(float)
        d_or = np.abs(wrap_deg(o[va].to_numpy()[w] - ref))
        d_sv = np.abs(wrap_deg(solved[va].to_numpy()[w] - ref))
        assert np.max(d_or) < 0.01, (fa, np.max(d_or))
        assert np.max(d_sv) < 1e-8, (fa, np.max(d_sv))


def test_raw_angles_have_no_filtering(cfg, tmp_path):
    df = _pose_df(60)
    df.loc[30, "right_wrist_x"] += 0.10
    p = tmp_path / "x.csv"
    df.to_csv(p, index=False)
    raw = oracle.raw_angles(p)
    orc = oracle.oracle_angles(p, cfg)
    # the spike moves the raw twist/elbow at frame 30, not the oracle
    assert abs(raw.loc[30, "r_elbow_y"] - raw.loc[29, "r_elbow_y"]) > 1.0
    assert abs(orc.loc[30, "r_elbow_y"] - orc.loc[29, "r_elbow_y"]) < 1e-9
    assert orc.attrs["fs_hz"] == pytest.approx(30.0)
