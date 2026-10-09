"""Central path constants for the eval/ track.

One place for the R4 stems and the v1 output locations so every eval
tool agrees on where inputs live. The v1 tree is frozen: it is only
ever read from here, never written except through its own extractors'
documented --out defaults.
"""

from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[2]

# Recordings
R5_STEM = "recording_20260825_222315"   # primary, occlusion scenario (user-selected 2026-08-26)
R4_STEM = "recording_20260825_070152"
R4_BACKUP_STEM = "recording_20260825_070032"
R1_STEM = "recording_20260224_083945"
# No-occlusion scenario takes (recorded 2026-08-31, 30 s each; the
# evaluation separates a without-occlusion and a with-occlusion
# scenario, R5 being the occlusion one)
R6A_STEM = "recording_20260831_065504"
R6B_STEM = "recording_20260831_065553"
# Two-hand rail take (recorded 2026-09-09 00:00, 50 s, 1499 frames;
# supervisor round 6, C50): the right hand slides the cube to the
# middle of the rail, the left hand takes over to the far end. The
# seven earlier takes of the same night are not used (user 2026-09-09).
R7_STEM = "recording_20260909_000024"
VIDEO = REPO / "Video"
R4_BAG = VIDEO / f"{R4_STEM}.bag"
R5_BAG = VIDEO / f"{R5_STEM}.bag"

# Short aliases used in calibration filenames and report prefixes
ALIAS = {R1_STEM: "r1", R4_STEM: "r4", R5_STEM: "r5",
         R6A_STEM: "r6a", R6B_STEM: "r6b", R7_STEM: "r7"}

# v1 pipeline outputs (produced by the frozen extractors, gitignored)
ARUCO_OUT = REPO / "v1" / "aruco" / "output"
MP_OUT = REPO / "v1" / "mediapipe" / "output"
R4_ARUCO_RAW = ARUCO_OUT / f"{R4_STEM}_aruco_raw.csv"
R4_ARUCO_META = ARUCO_OUT / f"{R4_STEM}_aruco_raw.meta.json"
R4_LM_RAW = MP_OUT / f"{R4_STEM}_landmarks_raw.csv"
R4_LM_META = MP_OUT / f"{R4_STEM}_landmarks_raw.meta.json"
R4_LM_FILTERED = MP_OUT / f"{R4_STEM}_landmarks_filtered.csv"
R4_OBJECT_WORLD = ARUCO_OUT / f"{R4_STEM}_object_world.csv"
R4_OBJECT_WORLD_FILTERED = ARUCO_OUT / f"{R4_STEM}_object_world_filtered.csv"
R4_CALIB = ARUCO_OUT / "scene_calibration_r4.json"

# Marker-size-corrected artifacts (E-009). Once these exist they are
# the authoritative R4 object track and calibration; the uncorrected
# ones remain for comparison.
EVAL = Path(__file__).resolve().parents[1]
R4_CALIB_SCALED = EVAL / "output" / "scene_calibration_r4c.json"
R4_OBJECT_WORLD_FILTERED_SCALED = (
    EVAL / "output" / f"{R4_STEM}_scaled_object_world_filtered.csv")


def r4_calib():
    return R4_CALIB_SCALED if R4_CALIB_SCALED.exists() else R4_CALIB


# Stem-generic accessors (R5 onward; R4/R1 constants above are kept so
# the pinned R4 reports stay reproducible byte-for-byte)
def bag(stem):
    return VIDEO / f"{stem}.bag"


def aruco_raw(stem):
    return ARUCO_OUT / f"{stem}_aruco_raw.csv"


def aruco_meta(stem):
    return ARUCO_OUT / f"{stem}_aruco_raw.meta.json"


def lm_raw(stem):
    return MP_OUT / f"{stem}_landmarks_raw.csv"


def lm_meta(stem):
    return MP_OUT / f"{stem}_landmarks_raw.meta.json"


def lm_filtered(stem):
    return MP_OUT / f"{stem}_landmarks_filtered.csv"


def lm_raw_vis0(stem):
    return EVAL / "output" / f"{stem}_landmarks_raw_vis0.csv"


def calib_for(stem):
    """Authoritative scene calibration for a stem: the marker-size-
    corrected one under eval/output/ when it exists, else the plain v1
    one. Naming follows the r4/r4c pattern via ALIAS."""
    alias = ALIAS.get(stem)
    if alias is None:
        raise ValueError(f"unknown recording stem {stem!r}; add it to "
                         "paths.ALIAS")
    if alias == "r1":
        return R1_CALIB
    scaled = EVAL / "output" / f"scene_calibration_{alias}c.json"
    plain = ARUCO_OUT / f"scene_calibration_{alias}.json"
    return scaled if scaled.exists() else plain


def object_world_filtered(stem):
    scaled = EVAL / "output" / f"{stem}_scaled_object_world_filtered.csv"
    base = scaled if scaled.exists() \
        else ARUCO_OUT / f"{stem}_object_world_filtered.csv"
    # cleaned track (clean_object_track.py: handover corruption
    # removed) is authoritative once it exists
    clean = base.with_name(base.stem + "_clean.csv")
    return clean if clean.exists() else base

# Pinned R1 references (read-only regression baselines)
R1_CALIB = ARUCO_OUT / "scene_calibration.json"

# eval/ locations
EVAL = REPO / "eval"
EVAL_OUT = EVAL / "output"          # large regenerable files, gitignored
EVAL_REPORTS = EVAL / "reports"     # small pinned summaries, committed
R4_LM_RAW_VIS0 = EVAL_OUT / f"{R4_STEM}_landmarks_raw_vis0.csv"

# Marker roles (mirrors v1/aruco/frames.py, values asserted at import
# time against the frozen source so drift is impossible)
WALL_ID, OBJECT_ID, DESK_ID = 0, 1, 2

LANDMARKS = [
    "left_shoulder", "right_shoulder",
    "left_elbow", "right_elbow",
    "left_wrist", "right_wrist",
    "left_hip", "right_hip",
]


def _assert_frames_agree():
    import sys
    sys.path.insert(0, str(REPO / "v1" / "aruco"))
    import frames
    assert frames.WORLD_ID == DESK_ID
    assert frames.OBJECT_ID == OBJECT_ID
    assert set(frames.MARKER_IDS) == {WALL_ID, OBJECT_ID, DESK_ID}


_assert_frames_agree()
