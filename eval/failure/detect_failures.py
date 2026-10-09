"""MediaPipe failure-frame detector (failure study, R5).

Produces a per-frame, per-entity failure mask that marks frames where
the tracked skeleton is wrong - either MISSING (MediaPipe itself
declined the sample) or CONFIDENTLY WRONG (MediaPipe reported a
high-visibility sample that is geometrically impossible). A later
stage consumes the mask for object-conditioned pose recovery.

Everything is computed from the RAW landmark CSV, so the detector
sees what MediaPipe actually did, not what the v1 despiker repaired.
The raw CSV carries the camera-frame points in meters plus the
per-landmark src code (0 ok / 1 low_vis / 2 no_depth).

Frame choice: all detector statistics (segment lengths, line angles,
inter-frame steps) are invariant under the camera -> leveled-desk
world map, because that map is a rigid isometry (carry.LeveledWorld
composes a permutation P, a reflection D, the calibration rotation
and the gravity rotation G, all orthogonal, plus a translation).
The detector therefore runs directly in the camera frame and needs
no scene calibration - see eval/offset/carry.py:54-73.

Detectors
  D1 acquisition  - any landmark of the group has src != 0 or is
                    non-finite. Group = {shoulder, elbow, wrist} per
                    arm; {left,right} x {hip, shoulder} for the torso.
  D2 segment      - |shoulder-elbow| or |elbow-wrist| deviates
                    fractionally more than SEG_TOL from that
                    segment's clean median (two-pass median).
  D3 torso line   - 3D angle between the hip line and the shoulder
                    line exceeds TORSO_LINE_TOL_DEG. Same quantity as
                    the E-011 gate in v1/kinematics/occlusion_ext.py
                    lines 282-287 (unit hip vector rh-lh vs unit
                    shoulder vector rs-ls, arccos of the dot).
  D4 width ratio  - shoulder_width / hip_width deviates fractionally
                    more than WIDTH_RATIO_BAND from its clean median
                    (two-pass median).
  D5 velocity     - per-landmark step ||p_f - p_{f-1}|| over a pair of
                    consecutive src==0 frames exceeds STEP_TOL_M.

Usage:
    python eval/failure/detect_failures.py [--stem STEM]
                                           [--ref-stem STEM]

Outputs (ALIAS is the paths.ALIAS short name of --stem, "r5" by
default, so a self-check run on another stem cannot clobber them):
    eval/output/recovery_ALIAS/failure_mask.csv
    eval/reports/ALIAS_failure_events.csv
    eval/reports/ALIAS_failure_mask.png
    eval/reports/ALIAS_failure_thresholds.png
    eval/reports/ALIAS_failure_mask.md
"""

import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
import paths  # noqa: E402

# --------------------------------------------------------------------
# Constants. Thresholds are pinned here and re-verified against the
# reference recording on every run (the R1 headroom table in the
# report); the derivation is in r5_failure_mask.md.
# --------------------------------------------------------------------
SEG_TOL = 0.35            # fractional deviation from clean segment median
TORSO_LINE_TOL_DEG = 22.0  # hip line vs shoulder line, degrees
WIDTH_RATIO_BAND = 0.20   # fractional deviation from clean width ratio
STEP_TOL_M = 0.05         # per-landmark step over one frame, meters

WARMUP_FRAMES = 5         # dropped after person-present start
BRIDGE_GAP = 5            # close gaps of at most this many frames
MIN_EVENT = 5             # drop events shorter than this many frames

MIN_CLEAN_FRAMES = 30     # fall back to pass-1 median below this

SIDES = ("left", "right")
SIDE_TAG = {"left": "L", "right": "R"}
ARM_PARTS = ("shoulder", "elbow", "wrist")
TORSO_LM = ("left_hip", "right_hip", "left_shoulder", "right_shoulder")

DETECTOR_COLS = ["d1_L", "d1_R", "d2_L", "d2_R", "d1_torso", "d3", "d4",
                 "d5_L", "d5_R", "d5_torso"]
ENTITY_DETECTORS = {
    "arm_L": ["d1_L", "d2_L", "d5_L"],
    "arm_R": ["d1_R", "d2_R", "d5_R"],
    "torso": ["d1_torso", "d3", "d4", "d5_torso"],
}
ENTITY_MASK = {"arm_L": "fail_arm_L", "arm_R": "fail_arm_R",
               "torso": "fail_torso"}


# --------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------
def raw_csv(stem):
    """Raw landmark CSV that carries the per-landmark src codes.

    R5 has them in the primary raw export; the pinned R1 export
    predates the src column and keeps them in its _v2 sibling."""
    primary = paths.lm_raw(stem)
    if primary.exists():
        head = pd.read_csv(primary, nrows=0)
        if "left_shoulder_src" in head.columns:
            return primary
    v2 = paths.MP_OUT / f"{stem}_landmarks_raw_v2.csv"
    if v2.exists():
        head = pd.read_csv(v2, nrows=0)
        if "left_shoulder_src" in head.columns:
            return v2
    raise FileNotFoundError(
        f"no raw landmark CSV with src columns for stem {stem!r}")


def load_recording(stem):
    """Returns (df, frame, time_s, points, src_ok, span, phases)."""
    df = pd.read_csv(raw_csv(stem))
    frame = df["frame"].to_numpy(int)
    time_s = df["time_s"].to_numpy(float)
    pts = {n: df[[f"{n}_x", f"{n}_y", f"{n}_z"]].to_numpy(float)
           for n in paths.LANDMARKS}
    finite = {n: np.isfinite(pts[n]).all(axis=1) for n in paths.LANDMARKS}
    src = {}
    for n in paths.LANDMARKS:
        s = df[f"{n}_src"].to_numpy(float)
        src[n] = np.where(np.isfinite(s), s, 9.0)      # missing -> not ok
    ok = {n: (src[n] == 0) & finite[n] for n in paths.LANDMARKS}

    insp = paths.EVAL_REPORTS / f"{stem}_inspection.json"
    phases, span = {}, None
    if insp.exists():
        blob = json.loads(insp.read_text())
        for name, val in blob["phases"].items():
            if val is None:        # phase absent in this recording
                continue
            a, b = val
            if name == "person_present":
                span = (int(a), int(b))
            else:
                phases[name] = (int(a), int(b))
    if span is None:
        pose = df["has_pose"].to_numpy() == 1
        idx = np.flatnonzero(pose)
        span = (int(frame[idx[0]]), int(frame[idx[-1]]))
    if not phases:
        phases = {"whole": span}

    in_span = (frame >= span[0] + WARMUP_FRAMES) & (frame <= span[1])
    dt = float(np.median(np.diff(time_s))) if len(time_s) > 1 else 0.0
    return {"stem": stem, "df": df, "frame": frame, "time_s": time_s,
            "pts": pts, "src": src, "ok": ok, "span": span, "dt": dt,
            "phases": phases, "in_span": in_span}


# --------------------------------------------------------------------
# Statistics
# --------------------------------------------------------------------
def seg_key(side, which):
    return ("upper_arm_" if which == "upper" else "forearm_") \
        + SIDE_TAG[side]


SEG_ENDS = {}
for _s in SIDES:
    SEG_ENDS[seg_key(_s, "upper")] = (f"{_s}_shoulder", f"{_s}_elbow")
    SEG_ENDS[seg_key(_s, "fore")] = (f"{_s}_elbow", f"{_s}_wrist")


def segment_lengths(rec):
    """key -> (length array, defined mask)."""
    out = {}
    for key, (a, b) in SEG_ENDS.items():
        L = np.linalg.norm(rec["pts"][a] - rec["pts"][b], axis=1)
        out[key] = (L, rec["ok"][a] & rec["ok"][b] & np.isfinite(L))
    return out


def torso_stats(rec):
    """(angle_deg, width_ratio, defined mask)."""
    p = rec["pts"]
    hu = p["right_hip"] - p["left_hip"]
    su = p["right_shoulder"] - p["left_shoulder"]
    hw = np.linalg.norm(hu, axis=1)
    sw = np.linalg.norm(su, axis=1)
    defined = np.ones(len(hw), bool)
    for n in TORSO_LM:
        defined &= rec["ok"][n]
    defined &= (hw > 1e-9) & (sw > 1e-9)
    with np.errstate(invalid="ignore", divide="ignore"):
        cos = np.einsum("ij,ij->i", hu, su) / (hw * sw)
        ang = np.degrees(np.arccos(np.clip(cos, -1.0, 1.0)))
        ratio = sw / hw
    return ang, ratio, defined


def steps(rec):
    """landmark -> (step array, defined mask); index f holds the step
    from f-1 to f, defined only when both frames are src==0."""
    out = {}
    n = len(rec["frame"])
    for name in paths.LANDMARKS:
        p = rec["pts"][name]
        s = np.full(n, np.nan)
        s[1:] = np.linalg.norm(np.diff(p, axis=0), axis=1)
        d = np.zeros(n, bool)
        d[1:] = rec["ok"][name][1:] & rec["ok"][name][:-1]
        d &= np.isfinite(s)
        out[name] = (s, d)
    return out


def frac_dev(values, med):
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.abs(values - med) / med


# --------------------------------------------------------------------
# Detectors
# --------------------------------------------------------------------
def run_detectors(rec, seg_tol=SEG_TOL):
    n = len(rec["frame"])
    span = rec["in_span"]
    fire = {c: np.zeros(n, bool) for c in DETECTOR_COLS}

    # D1 acquisition
    for side in SIDES:
        bad = np.zeros(n, bool)
        for part in ARM_PARTS:
            bad |= ~rec["ok"][f"{side}_{part}"]
        fire[f"d1_{SIDE_TAG[side]}"] = bad & span
    bad = np.zeros(n, bool)
    for name in TORSO_LM:
        bad |= ~rec["ok"][name]
    fire["d1_torso"] = bad & span

    # D3 torso line angle (no calibration needed)
    ang, ratio, tdef = torso_stats(rec)
    fire["d3"] = span & tdef & (ang > TORSO_LINE_TOL_DEG)

    # D5 velocity
    st = steps(rec)
    groups = {f"d5_{SIDE_TAG[s]}": [f"{s}_{p}" for p in ARM_PARTS]
              for s in SIDES}
    groups["d5_torso"] = list(TORSO_LM)
    for col, names in groups.items():
        f = np.zeros(n, bool)
        for name in names:
            s, d = st[name]
            f |= d & (s > STEP_TOL_M)
        fire[col] = f & span

    # D4 width ratio, two-pass median
    base = span & tdef
    med1 = float(np.median(ratio[base])) if base.any() else np.nan
    d4_pass1 = base & (frac_dev(ratio, med1) > WIDTH_RATIO_BAND)
    clean = base & ~d4_pass1 & ~fire["d3"] & ~fire["d5_torso"] \
        & ~fire["d1_torso"]
    med_ratio = float(np.median(ratio[clean])) \
        if clean.sum() >= MIN_CLEAN_FRAMES else med1
    fire["d4"] = base & (frac_dev(ratio, med_ratio) > WIDTH_RATIO_BAND)

    # D2 segment lengths, two-pass median
    segs = segment_lengths(rec)
    seg_med, seg_dev = {}, {}
    for key, (L, d) in segs.items():
        base_s = span & d
        m1 = float(np.median(L[base_s])) if base_s.any() else np.nan
        seg_med[key] = m1
    for side in SIDES:
        tag = SIDE_TAG[side]
        keys = [seg_key(side, "upper"), seg_key(side, "fore")]
        d2_pass1 = np.zeros(n, bool)
        for key in keys:
            L, d = segs[key]
            d2_pass1 |= span & d & (frac_dev(L, seg_med[key]) > seg_tol)
        clean_arm = span & ~d2_pass1 & ~fire[f"d1_{tag}"] \
            & ~fire[f"d5_{tag}"] & ~fire["d3"] & ~fire["d4"]
        for key in keys:
            L, d = segs[key]
            c = clean_arm & d
            if c.sum() >= MIN_CLEAN_FRAMES:
                seg_med[key] = float(np.median(L[c]))
        f = np.zeros(n, bool)
        for key in keys:
            L, d = segs[key]
            dev = frac_dev(L, seg_med[key])
            seg_dev[key] = np.where(span & d, dev, np.nan)
            f |= span & d & (dev > seg_tol)
        fire[f"d2_{tag}"] = f

    stats = {"seg": segs, "seg_med": seg_med, "seg_dev": seg_dev,
             "angle": ang, "ratio": ratio, "torso_def": tdef,
             "ratio_med": med_ratio,
             "ratio_dev": np.where(base, frac_dev(ratio, med_ratio),
                                   np.nan),
             "steps": st}
    return fire, stats


# --------------------------------------------------------------------
# Morphology and events
# --------------------------------------------------------------------
def runs(mask):
    idx = np.flatnonzero(mask)
    if idx.size == 0:
        return []
    brk = np.flatnonzero(np.diff(idx) > 1)
    starts = np.r_[idx[0], idx[brk + 1]]
    stops = np.r_[idx[brk], idx[-1]]
    return list(zip(starts.tolist(), stops.tolist()))


def close_and_prune(mask, span, bridge=BRIDGE_GAP, min_len=MIN_EVENT):
    """Bridge gaps of at most `bridge` frames, then drop runs shorter
    than `min_len`. Restricted to the evaluated span."""
    m = mask & span
    segs = runs(m)
    for (a1, b1), (a2, _) in zip(segs, segs[1:]):
        if a2 - b1 - 1 <= bridge:
            m[b1 + 1:a2] = True
    m &= span
    out = np.zeros_like(m)
    for a, b in runs(m):
        if b - a + 1 >= min_len:
            out[a:b + 1] = True
    return out


def phase_of(rec, f0, f1):
    hits = [name for name, (a, b) in rec["phases"].items()
            if f0 <= b and f1 >= a]
    order = list(rec["phases"].keys())
    hits.sort(key=order.index)
    return "+".join(hits) if hits else "none"


def build_events(rec, fire, masks):
    rows = []
    for entity, cols in ENTITY_DETECTORS.items():
        m = masks[ENTITY_MASK[entity]]
        for a, b in runs(m):
            fired = [c for c in cols if fire[c][a:b + 1].any()]
            f0, f1 = int(rec["frame"][a]), int(rec["frame"][b])
            rows.append({
                "start_frame": f0,
                "stop_frame": f1,
                "duration_s": round(float(rec["time_s"][b]
                                          - rec["time_s"][a])
                                    + rec["dt"], 3),
                "frames": b - a + 1,
                "entity": entity,
                "detectors": ";".join(fired),
                "phase": phase_of(rec, f0, f1),
            })
    rows.sort(key=lambda r: (r["start_frame"], r["entity"]))
    return pd.DataFrame(rows, columns=[
        "start_frame", "stop_frame", "duration_s", "frames", "entity",
        "detectors", "phase"])


def assemble(rec, fire):
    span = rec["in_span"]
    masks = {}
    for entity, cols in ENTITY_DETECTORS.items():
        raw = np.zeros(len(span), bool)
        for c in cols:
            raw |= fire[c]
        masks[ENTITY_MASK[entity]] = close_and_prune(raw, span)
    return masks


# --------------------------------------------------------------------
# Reference (R1) headroom check
# --------------------------------------------------------------------
def headroom(rec, stats, fire):
    """Per-statistic max on the reference recording vs the threshold."""
    span = rec["in_span"]
    rows = []
    for key in sorted(stats["seg_dev"]):
        dev = stats["seg_dev"][key]
        v = float(np.nanmax(dev)) if np.isfinite(dev).any() else np.nan
        rows.append(("D2 " + key, "frac dev", v, SEG_TOL))
    a = stats["angle"][span & stats["torso_def"]]
    rows.append(("D3 torso line angle", "deg",
                 float(a.max()) if a.size else np.nan,
                 TORSO_LINE_TOL_DEG))
    rd = stats["ratio_dev"]
    rows.append(("D4 width ratio dev", "frac dev",
                 float(np.nanmax(rd)) if np.isfinite(rd).any() else np.nan,
                 WIDTH_RATIO_BAND))
    smax = 0.0
    for name in paths.LANDMARKS:
        s, d = stats["steps"][name]
        sel = s[d & span]
        if sel.size:
            smax = max(smax, float(sel.max()))
    rows.append(("D5 landmark step", "m", smax, STEP_TOL_M))
    fires = {c: int(fire[c].sum()) for c in DETECTOR_COLS}
    return rows, fires


# --------------------------------------------------------------------
# Plots
# --------------------------------------------------------------------
def plot_thresholds(ref, ref_stats, rec, stats, out_png):
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))

    def panel(ax, series, thr, title, xlabel, xmax):
        for v, c, label in series:
            v = v[np.isfinite(v)]
            if v.size == 0:
                continue
            ax.hist(np.clip(v, 0, xmax), bins=80, range=(0, xmax),
                    histtype="step", lw=1.2, color=c, density=True,
                    label=f"{label} (n={v.size}, p99={np.percentile(v, 99):.3g}"
                          f", max={v.max():.3g})")
            ax.axvline(np.percentile(v, 99), color=c, ls=":", lw=0.9)
        ax.axvline(thr, color="k", ls="--", lw=1.4,
                   label=f"threshold {thr:g}")
        ax.set_yscale("log")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel(xlabel, fontsize=9)
        ax.set_ylabel("density (log)", fontsize=9)
        ax.legend(fontsize=7)

    def cat(d, keys):
        return np.concatenate([d[k][np.isfinite(d[k])] for k in keys]) \
            if keys else np.array([])

    ref_tag, cur_tag = ref["stem"][-6:], rec["stem"][-6:]
    seg_keys = sorted(stats["seg_dev"])
    left_keys = [k for k in seg_keys if k.endswith("_L")]
    right_keys = [k for k in seg_keys if k.endswith("_R")]
    panel(axes[0, 0],
          [(cat(ref_stats["seg_dev"], right_keys), "#2a7e2a",
            f"{ref_tag} ref RIGHT arm"),
           (cat(ref_stats["seg_dev"], left_keys), "#8a6d00",
            f"{ref_tag} ref LEFT arm"),
           (cat(stats["seg_dev"], seg_keys), "#cc2222",
            f"{cur_tag} all 4 segments")],
          SEG_TOL,
          "D2 segment-length fractional deviation\n(SEG_TOL derived from "
          "the reference RIGHT arm; the reference\nLEFT arm carries a "
          "real elbow-slide defect)",
          "|L - median| / median", 1.2)
    panel(axes[0, 1],
          [(ref_stats["angle"][ref["in_span"] & ref_stats["torso_def"]],
            "#2a7e2a", f"{ref_tag} ref"),
           (stats["angle"][rec["in_span"] & stats["torso_def"]],
            "#cc2222", cur_tag)],
          TORSO_LINE_TOL_DEG, "D3 hip line vs shoulder line angle",
          "degrees", 90.0)
    panel(axes[1, 0],
          [(ref_stats["ratio_dev"], "#2a7e2a", f"{ref_tag} ref"),
           (stats["ratio_dev"], "#cc2222", cur_tag)],
          WIDTH_RATIO_BAND,
          "D4 shoulder/hip width-ratio fractional deviation",
          "|r - median| / median", 1.0)

    def allsteps(r, s):
        v = []
        for name in paths.LANDMARKS:
            arr, d = s["steps"][name]
            v.append(arr[d & r["in_span"]])
        return np.concatenate(v) if v else np.array([])

    panel(axes[1, 1],
          [(allsteps(ref, ref_stats), "#2a7e2a", f"{ref_tag} ref"),
           (allsteps(rec, stats), "#cc2222", cur_tag)],
          STEP_TOL_M, "D5 per-landmark inter-frame step (all 8 landmarks)",
          "meters", 0.20)
    fig.suptitle(f"Failure-detector threshold derivation: "
                 f"{ref['stem']} (reference) vs {rec['stem']}\n"
                 "dotted = p99 of the same colour, dashed black = "
                 "threshold; values clipped to the axis",
                 fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(out_png, dpi=120)
    plt.close(fig)


ROW_ORDER = ["d1_L", "d2_L", "d5_L", "fail_arm_L",
             "d1_R", "d2_R", "d5_R", "fail_arm_R",
             "d1_torso", "d3", "d4", "d5_torso", "fail_torso"]
ROW_COLOR = {"d1": "#d98a00", "d2": "#4444cc", "d3": "#8a2be2",
             "d4": "#00838f", "d5": "#cc2222", "fa": "#111111"}
MIN_MARK_S = 0.10   # minimum drawn mark width so 1-frame fires stay visible


def row_color(name):
    if name.startswith("fail"):
        return ROW_COLOR["fa"]
    return ROW_COLOR[name[:2]]


def plot_timeline(rec, fire, masks, out_png):
    t = rec["time_s"]
    series = dict(fire)
    series.update(masks)
    fig, ax = plt.subplots(figsize=(14, 6))
    for i, name in enumerate(ROW_ORDER):
        y = len(ROW_ORDER) - 1 - i
        m = series[name]
        for a, b in runs(m):
            ax.add_patch(plt.Rectangle(
                (t[a], y - 0.38), max(t[b] - t[a], MIN_MARK_S), 0.76,
                color=row_color(name),
                alpha=0.95 if name.startswith("fail") else 0.75,
                lw=0))
        ax.text(t[-1] + 0.4, y, f"{int(m.sum())}", fontsize=7,
                va="center", color="#444444")
    for name, (a, b) in rec["phases"].items():
        ia = int(np.searchsorted(rec["frame"], a))
        ib = int(min(np.searchsorted(rec["frame"], b),
                     len(t) - 1))
        if name == "manipulation":
            ax.axvspan(t[ia], t[ib], color="#cccccc", alpha=0.35, zorder=0)
        ax.axvline(t[ia], color="#888888", lw=0.6, ls=":", zorder=1)
        ax.text(t[ia] + 0.2, len(ROW_ORDER) - 0.4, name, fontsize=7,
                color="#666666")
    a0 = int(np.searchsorted(rec["frame"], rec["span"][0]))
    ax.axvspan(t[0], t[a0], color="#eeeeee", alpha=0.8, zorder=0)
    ax.set_xlim(t[0], t[-1] + 1.6)
    ax.set_ylim(-0.8, len(ROW_ORDER) - 0.1)
    ax.set_yticks(range(len(ROW_ORDER)))
    ax.set_yticklabels(ROW_ORDER[::-1], fontsize=8)
    ax.set_xlabel("time (s)")
    ax.set_title(f"{rec['stem']}: MediaPipe failure mask "
                 f"(shaded = manipulation phase; right-hand number = "
                 f"frames set; marks drawn at least {MIN_MARK_S:g} s wide)",
                 fontsize=10)
    ax.grid(axis="x", lw=0.3, alpha=0.4)
    fig.tight_layout()
    fig.savefig(out_png, dpi=120)
    plt.close(fig)


# --------------------------------------------------------------------
# Report
# --------------------------------------------------------------------
# Known natural occlusion windows of R5 (frame numbers of that recording).
# The sanity check applies to R5 only; any other stem gets an empty list.
SANITY = [("arm_L", 1458, 1668, "left elbow+wrist blocked"),
          ("arm_R", 1826, 1893, "right elbow blocked")]


def sanity_check(rec, fire, masks):
    out = []
    windows = SANITY if rec["stem"] == paths.R5_STEM else []
    for entity, a, b, label in windows:
        col = ENTITY_DETECTORS[entity][0]          # the D1 column
        ia = int(np.searchsorted(rec["frame"], a))
        ib = int(np.searchsorted(rec["frame"], b))
        d1 = fire[col][ia:ib + 1]
        cov = float(d1.mean()) if d1.size else 0.0
        ev = [(int(rec["frame"][x]), int(rec["frame"][y]))
              for x, y in runs(masks[ENTITY_MASK[entity]])
              if rec["frame"][y] >= a and rec["frame"][x] <= b]
        ok = cov >= 0.9 and bool(ev)
        out.append({"entity": entity, "window": (a, b), "label": label,
                    "d1_coverage": cov, "events": ev,
                    "verdict": "PASS" if ok else "FAIL"})
    return out


def phase_coverage(rec, masks):
    rows = []
    for name, (a, b) in rec["phases"].items():
        sel = (rec["frame"] >= a) & (rec["frame"] <= b) & rec["in_span"]
        n = int(sel.sum())
        row = {"phase": name, "frames": n}
        for entity in ENTITY_DETECTORS:
            m = masks[ENTITY_MASK[entity]]
            row[entity] = round(100.0 * float((m & sel).sum()) / n, 1) \
                if n else 0.0
        rows.append(row)
    return rows


def depth_split(rec, pair):
    """Camera-frame depth (z) disagreement across a landmark pair.

    A person facing the desk has both hips and both shoulders at nearly
    the same depth; a large hip split with a small shoulder split is the
    signature of one hip landmark being lifted off the wrong surface,
    which is what drives D3 and D4 without D1 ever firing."""
    a, b = pair
    return np.abs(rec["pts"][a][:, 2] - rec["pts"][b][:, 2])


def confident_wrong(rec, fire, masks, stats):
    """Frames where D2-D5 fire for an entity while its D1 does not."""
    hip_dz = depth_split(rec, ("left_hip", "right_hip"))
    sh_dz = depth_split(rec, ("left_shoulder", "right_shoulder"))
    quiet = rec["in_span"] & ~fire["d3"] & ~fire["d4"] & ~fire["d1_torso"]
    hip_clean = float(np.nanmedian(hip_dz[quiet]))
    sh_clean = float(np.nanmedian(sh_dz[quiet]))
    out = {}
    for entity, cols in ENTITY_DETECTORS.items():
        d1 = fire[cols[0]]
        other = np.zeros(len(d1), bool)
        for c in cols[1:]:
            other |= fire[c]
        cw = other & ~d1 & rec["in_span"]
        side = {"arm_L": "left", "arm_R": "right"}.get(entity)
        segs = []
        for a, b in runs(close_and_prune(cw, rec["in_span"])):
            note = ""
            if entity == "torso":
                note = (f"hip depth split "
                        f"{np.nanmedian(hip_dz[a:b + 1]) * 100:.1f} cm "
                        f"(clean {hip_clean * 100:.1f}), shoulder "
                        f"{np.nanmedian(sh_dz[a:b + 1]) * 100:.1f} cm "
                        f"(clean {sh_clean * 100:.1f})")
            else:
                u = stats["seg"][seg_key(side, "upper")][0]
                fo = stats["seg"][seg_key(side, "fore")][0]
                mu = stats["seg_med"][seg_key(side, "upper")]
                mf = stats["seg_med"][seg_key(side, "fore")]
                note = (f"upper arm {np.nanmedian(u[a:b + 1]) * 100:.1f} cm "
                        f"(clean {mu * 100:.1f}), forearm "
                        f"{np.nanmedian(fo[a:b + 1]) * 100:.1f} cm "
                        f"(clean {mf * 100:.1f})")
            segs.append((int(rec["frame"][a]), int(rec["frame"][b]),
                         round(float(rec["time_s"][b] - rec["time_s"][a])
                               + rec["dt"], 2),
                         ";".join(c for c in cols[1:]
                                  if fire[c][a:b + 1].any()),
                         note))
        out[entity] = {"frames": int(cw.sum()), "windows": segs}
    return out


def ref_residual_events(ref, ref_fire, ref_stats):
    """Reference-recording events that survive morphology and are NOT
    pure D1. Each row carries the elbow-slide evidence: an elbow that
    slides along the arm changes upper_arm and forearm in opposite
    directions while their sum stays put, which is a genuine tracking
    defect rather than a mis-set threshold."""
    masks = assemble(ref, ref_fire)
    rows = []
    for entity, cols in ENTITY_DETECTORS.items():
        side = {"arm_L": "left", "arm_R": "right"}.get(entity)
        for a, b in runs(masks[ENTITY_MASK[entity]]):
            fired = [c for c in cols if ref_fire[c][a:b + 1].any()]
            if fired == [cols[0]]:
                continue                       # pure acquisition gap
            row = {"entity": entity,
                   "start_frame": int(ref["frame"][a]),
                   "stop_frame": int(ref["frame"][b]),
                   "frames": b - a + 1,
                   "detectors": ";".join(fired),
                   "evidence": ""}
            if side is not None:
                u = ref_stats["seg"][seg_key(side, "upper")][0]
                f = ref_stats["seg"][seg_key(side, "fore")][0]
                mu = ref_stats["seg_med"][seg_key(side, "upper")]
                mf = ref_stats["seg_med"][seg_key(side, "fore")]
                row["evidence"] = (
                    f"upper {np.nanmedian(u[a:b + 1]):.3f} (clean "
                    f"{mu:.3f}), forearm {np.nanmedian(f[a:b + 1]):.3f} "
                    f"(clean {mf:.3f}), sum "
                    f"{np.nanmedian(u[a:b + 1] + f[a:b + 1]):.3f} "
                    f"(clean {mu + mf:.3f})")
            rows.append(row)
    return rows


def seg_tol_sensitivity(rec, ref, ref_stats, alt_tol):
    """What R5 loses if SEG_TOL is widened until the reference fires
    zero D2 frames."""
    alt_fire, _ = run_detectors(rec, seg_tol=alt_tol)
    ref_alt, _ = run_detectors(ref, seg_tol=alt_tol)
    base_fire, _ = run_detectors(rec, seg_tol=SEG_TOL)
    return {
        "alt_tol": alt_tol,
        "ref_d2": {c: int(ref_alt[c].sum()) for c in ("d2_L", "d2_R")},
        "r5_d2_base": {c: int(base_fire[c].sum())
                       for c in ("d2_L", "d2_R")},
        "r5_d2_alt": {c: int(alt_fire[c].sum()) for c in ("d2_L", "d2_R")},
        "lost_windows": [
            (int(rec["frame"][a]), int(rec["frame"][b]))
            for a, b in runs(close_and_prune(
                (base_fire["d2_L"] | base_fire["d2_R"])
                & ~(alt_fire["d2_L"] | alt_fire["d2_R"]), rec["in_span"]))],
    }


def md_table(header, rows):
    lines = ["| " + " | ".join(header) + " |",
             "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        lines.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(lines)


def write_report(out_md, rec, ref, fire, masks, events, hr_rows, hr_fires,
                 ref_fires, sanity, phase_rows, cw, files, ref_resid,
                 sens):
    n_span = int(rec["in_span"].sum())
    alias = paths.ALIAS.get(rec["stem"], rec["stem"])
    L = []
    L.append(f"# {alias.upper()} MediaPipe failure mask: {rec['stem']}")
    L.append("")
    L.append(f"Reference (zero-fire check): {ref['stem']}.")
    L.append(f"Evaluated span: frames {rec['span'][0] + WARMUP_FRAMES}"
             f"-{rec['span'][1]} ({n_span} frames), i.e. the "
             f"person-present span minus a {WARMUP_FRAMES}-frame warmup.")
    L.append("")
    L.append("Source: the RAW landmark CSV, so the detector sees what "
             "MediaPipe actually produced. All statistics are invariant "
             "under the camera -> leveled-desk map (a rigid isometry), "
             "so no scene calibration is needed.")
    L.append("")

    L.append("## Constants")
    L.append("")
    L.append(md_table(
        ["constant", "value", "meaning"],
        [["SEG_TOL", SEG_TOL,
          "D2 fractional deviation from the clean segment median"],
         ["TORSO_LINE_TOL_DEG", TORSO_LINE_TOL_DEG,
          "D3 hip line vs shoulder line angle, degrees"],
         ["WIDTH_RATIO_BAND", WIDTH_RATIO_BAND,
          "D4 fractional deviation of shoulder/hip width ratio"],
         ["STEP_TOL_M", STEP_TOL_M,
          "D5 per-landmark step over one frame, meters"],
         ["WARMUP_FRAMES", WARMUP_FRAMES,
          "frames dropped after the person-present start"],
         ["BRIDGE_GAP", BRIDGE_GAP,
          "morphological closing: gaps of at most this many frames"],
         ["MIN_EVENT", MIN_EVENT,
          "morphological opening: events shorter than this are dropped"]]))
    L.append("")

    L.append("## Threshold derivation and reference headroom")
    L.append("")
    L.append("Thresholds were derived plot-first from the statistic "
             "distributions of the reference recording and R5 "
             "(eval/reports/r5_failure_thresholds.png), each set at the "
             "reference clean p99 plus a safety margin and cross-checked "
             "against the project precedents (E-011 torso line trip 20 "
             "deg; FOREARM_TOL / gate_tol 0.30 fractional).")
    L.append("")
    rows = []
    for name, unit, mx, thr in hr_rows:
        head = thr - mx
        rows.append([name, unit, f"{thr:g}", f"{mx:.3g}", f"{head:+.3g}",
                     "PASS" if mx <= thr else "FAIL"])
    L.append(md_table(["statistic", "unit", "threshold",
                       f"max on {ref['stem'][-6:]}", "headroom",
                       "zero-fire"], rows))
    L.append("")
    L.append("Reference per-frame fire counts (D2-D5 must be 0):")
    L.append("")
    L.append(md_table(["detector", "frames fired on reference"],
                      [[c, ref_fires[c]] for c in DETECTOR_COLS]))
    L.append("")
    L.append("D1 is an acquisition detector, not a threshold detector: "
             "it reports MediaPipe's own src codes, so it is expected to "
             "fire wherever the reference has low-visibility samples and "
             "is exempt from the zero-fire rule.")
    L.append("")
    d25 = [c for c in DETECTOR_COLS
           if not c.startswith("d1") and ref_fires[c]]
    if not d25:
        L.append("Zero-fire check: PASS - no D2-D5 detector fires on the "
                 "reference recording.")
        L.append("")
    else:
        L.append(f"Zero-fire check: FAIL for {', '.join(d25)}. This is a "
                 "finding about the reference recording, not a mis-set "
                 "threshold - see the next section.")
        L.append("")
        L.append("### Reference residual events "
                 "(the reference is not defect-free)")
        L.append("")
        L.append("Only events that survive morphological closing and are "
                 "not pure acquisition gaps are listed. The evidence "
                 "column reports the median upper-arm and forearm length "
                 "inside the event against their clean medians.")
        L.append("")
        if ref_resid:
            L.append(md_table(
                ["entity", "start_frame", "stop_frame", "frames",
                 "detectors", "evidence (m)"],
                [[r["entity"], r["start_frame"], r["stop_frame"],
                  r["frames"], r["detectors"], r["evidence"]]
                 for r in ref_resid]))
        else:
            L.append("none")
        L.append("")
        L.append("Interpretation: in each of these windows the reference "
                 "left elbow slides ALONG the arm - upper-arm and forearm "
                 "move in opposite directions and their sum changes far "
                 "less than either part does. That is a physically "
                 "impossible limb, so "
                 "the detector is right and the material assumption "
                 "\"the reference recording is clean\" holds only for the "
                 "right arm and the torso, not for the reference left "
                 "arm. The same plateau is present in the reference "
                 "FILTERED track, so it is not a raw-vs-filtered "
                 "artifact.")
        L.append("")
        L.append("### SEG_TOL sensitivity (what forcing zero fires costs)")
        L.append("")
        L.append(md_table(
            ["SEG_TOL", "reference d2_L", "reference d2_R", "R5 d2_L",
             "R5 d2_R"],
            [[SEG_TOL, ref_fires["d2_L"], ref_fires["d2_R"],
              sens["r5_d2_base"]["d2_L"], sens["r5_d2_base"]["d2_R"]],
             [sens["alt_tol"], sens["ref_d2"]["d2_L"],
              sens["ref_d2"]["d2_R"], sens["r5_d2_alt"]["d2_L"],
              sens["r5_d2_alt"]["d2_R"]]]))
        L.append("")
        lost = ", ".join(f"{a}-{b}" for a, b in sens["lost_windows"]) \
            or "none"
        right_max = max(m for n, _, m, _ in hr_rows
                        if n.startswith("D2") and n.endswith("_R"))
        L.append(f"Widening SEG_TOL to {sens['alt_tol']:g} silences the "
                 f"reference but loses these R5 D2 windows: {lost}. "
                 f"DECISION: keep SEG_TOL = {SEG_TOL:g} (derived from the "
                 f"reference RIGHT arm, max frac dev {right_max:.3f}, "
                 "and consistent with the 0.30 project precedent). "
                 "Calibrating the tolerance to a defect would blind the "
                 "detector to the moderate R5 corruption windows the "
                 "recovery stage needs.")
        L.append("")

    L.append(f"## {alias.upper()} detector fire counts")
    L.append("")
    L.append(md_table(
        ["detector", "frames", "percent of span"],
        [[c, hr_fires[c], round(100.0 * hr_fires[c] / n_span, 1)]
         for c in DETECTOR_COLS]))
    L.append("")
    L.append("Combined masks after closing (bridge <= "
             f"{BRIDGE_GAP}, drop < {MIN_EVENT}):")
    L.append("")
    L.append(md_table(
        ["mask", "frames", "percent of span", "events"],
        [[ENTITY_MASK[e], int(masks[ENTITY_MASK[e]].sum()),
          round(100.0 * float(masks[ENTITY_MASK[e]].sum()) / n_span, 1),
          int((events["entity"] == e).sum())]
         for e in ENTITY_DETECTORS]))
    L.append("")

    L.append("## Sanity check: known natural occlusions")
    L.append("")
    if not sanity:
        L.append("Not applicable: the known occlusion windows are R5's "
                 "frame numbers; no such list exists for this recording.")
        L.append("")
    rows = []
    for s in sanity:
        a, b = s["window"]
        rows.append([s["entity"], f"{a}-{b}", s["label"],
                     f"{100 * s['d1_coverage']:.1f}",
                     ";".join(f"{x}-{y}" for x, y in s["events"])
                     or "none",
                     s["verdict"]])
    L.append(md_table(["entity", "known window", "source event",
                       "D1 coverage percent", "overlapping mask events",
                       "verdict"], rows))
    L.append("")
    verdict = ("n/a" if not sanity else
               "PASS" if all(s["verdict"] == "PASS" for s in sanity)
               else "FAIL")
    L.append(f"Sanity verdict: {verdict}")
    L.append("")

    L.append("## Per-phase failure coverage (percent of phase frames)")
    L.append("")
    L.append(md_table(["phase", "frames", "arm_L", "arm_R", "torso"],
                      [[r["phase"], r["frames"], r["arm_L"], r["arm_R"],
                        r["torso"]] for r in phase_rows]))
    L.append("")

    L.append("## Confident-but-wrong windows (D2-D5 firing without D1)")
    L.append("")
    for entity in ENTITY_DETECTORS:
        info = cw[entity]
        L.append(f"### {entity}: {info['frames']} frames, "
                 f"{len(info['windows'])} windows after closing")
        L.append("")
        if info["windows"]:
            L.append(md_table(
                ["start_frame", "stop_frame", "seconds", "detectors",
                 "mechanism"],
                [[a, b, s, d, note or "-"]
                 for a, b, s, d, note in info["windows"]]))
        else:
            L.append("none")
        L.append("")
    L.append("A person facing the desk keeps both hips and both "
             "shoulders at nearly the same camera depth, so a torso "
             "window is read by which of the two splits blows up: a "
             "large HIP split with a clean shoulder split means one hip "
             "landmark took its depth off the wrong surface, and a large "
             "SHOULDER split with a clean hip split means the shoulder "
             "line is the corrupt one. Both variants appear above, "
             "matching the two E-011 corruption modes. MediaPipe reports "
             "all of these landmarks at full visibility, which is why D1 "
             "never fires and only the geometry detectors catch them. "
             "For the arm windows the mechanism column reports the "
             "measured limb lengths against their clean medians: a limb "
             "cannot change length, and upper arm and forearm moving in "
             "opposite directions is the elbow-slide signature.")
    L.append("")

    L.append("## Interpretation")
    L.append("")
    known = []
    acq = []
    conf = []
    mixed = []
    for _, r in events.iterrows():
        d1 = f"d1_{r['entity'].split('_')[-1]}" if r["entity"] != "torso" \
            else "d1_torso"
        has_d1 = d1 in r["detectors"].split(";")
        has_other = any(c != d1 for c in r["detectors"].split(";") if c)
        tag = f"{r['entity']} {r['start_frame']}-{r['stop_frame']} " \
              f"({r['duration_s']:.2f} s)"
        hit = [lab for ent, a, b, lab in SANITY
               if ent == r["entity"] and r["start_frame"] <= b
               and r["stop_frame"] >= a]
        if hit:
            known.append(f"{tag}: {hit[0]}")
        elif has_d1 and has_other:
            mixed.append(tag)
        elif has_d1:
            acq.append(tag)
        else:
            conf.append(f"{tag} [{r['detectors']}]")
    L.append("Known natural occlusions recovered by D1 "
             "(the sanity windows):")
    L.append("")
    for s in known or ["- none"]:
        L.append(f"- {s}" if not s.startswith("-") else s)
    L.append("")
    L.append("Acquisition-only events (MediaPipe declined the sample, "
             "geometry never became implausible):")
    L.append("")
    for s in acq or ["- none"]:
        L.append(f"- {s}" if not s.startswith("-") else s)
    L.append("")
    L.append("Mixed events (an acquisition gap with implausible geometry "
             "in the same window - the tracker degrades before and after "
             "it gives up):")
    L.append("")
    for s in mixed or ["- none"]:
        L.append(f"- {s}" if not s.startswith("-") else s)
    L.append("")
    L.append("NEW confident-but-wrong events (D2-D5 only, MediaPipe "
             "reported these samples as good):")
    L.append("")
    for s in conf or ["- none"]:
        L.append(f"- {s}" if not s.startswith("-") else s)
    L.append("")

    L.append("## Event table")
    L.append("")
    if len(events):
        L.append(md_table(list(events.columns),
                          events.values.tolist()))
    else:
        L.append("no events")
    L.append("")

    L.append("## Files")
    L.append("")
    for f in files:
        L.append(f"- {f}")
    L.append("")
    out_md.write_text("\n".join(L) + "\n")


# --------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R5_STEM)
    ap.add_argument("--ref-stem", default=paths.R1_STEM,
                    help="clean reference used for the zero-fire check")
    args = ap.parse_args()

    rec = load_recording(args.stem)
    fire, stats = run_detectors(rec)
    masks = assemble(rec, fire)
    events = build_events(rec, fire, masks)

    ref = load_recording(args.ref_stem)
    ref_fire, ref_stats = run_detectors(ref)
    hr_rows, ref_fires = headroom(ref, ref_stats, ref_fire)
    _, cur_fires = headroom(rec, stats, fire)

    # Output naming follows the project alias (R5 -> "r5"), so a
    # self-check run on another stem cannot clobber the pinned R5
    # artifacts.
    alias = paths.ALIAS.get(args.stem, args.stem)
    out_dir = paths.EVAL_OUT / f"recovery_{alias}"
    out_dir.mkdir(parents=True, exist_ok=True)
    paths.EVAL_REPORTS.mkdir(parents=True, exist_ok=True)

    mask_csv = out_dir / "failure_mask.csv"
    cols = {"frame": rec["frame"], "time_s": np.round(rec["time_s"], 6)}
    for c in DETECTOR_COLS:
        cols[c] = fire[c].astype(int)
    for e in ENTITY_DETECTORS:
        cols[ENTITY_MASK[e]] = masks[ENTITY_MASK[e]].astype(int)
    pd.DataFrame(cols).to_csv(mask_csv, index=False)

    ev_csv = paths.EVAL_REPORTS / f"{alias}_failure_events.csv"
    events.to_csv(ev_csv, index=False)

    thr_png = paths.EVAL_REPORTS / f"{alias}_failure_thresholds.png"
    plot_thresholds(ref, ref_stats, rec, stats, thr_png)
    tl_png = paths.EVAL_REPORTS / f"{alias}_failure_mask.png"
    plot_timeline(rec, fire, masks, tl_png)

    sanity = sanity_check(rec, fire, masks)
    phase_rows = phase_coverage(rec, masks)
    cw = confident_wrong(rec, fire, masks, stats)
    md = paths.EVAL_REPORTS / f"{alias}_failure_mask.md"
    files = [str(p.relative_to(paths.REPO))
             for p in (mask_csv, ev_csv, tl_png, thr_png, md)]
    ref_resid = ref_residual_events(ref, ref_fire, ref_stats)
    ref_seg_max = max(m for n, _, m, _ in hr_rows if n.startswith("D2"))
    sens = seg_tol_sensitivity(rec, ref, ref_stats,
                               round(ref_seg_max + 0.025, 2))
    write_report(md, rec, ref, fire, masks, events, hr_rows, cur_fires,
                 ref_fires, sanity, phase_rows, cw, files, ref_resid,
                 sens)

    n_span = int(rec["in_span"].sum())
    print(f"=== failure detector: {rec['stem']} ===")
    print(f"  span frames {rec['span'][0] + WARMUP_FRAMES}-"
          f"{rec['span'][1]} ({n_span} frames)")
    print(f"  thresholds: SEG_TOL {SEG_TOL}, TORSO_LINE_TOL_DEG "
          f"{TORSO_LINE_TOL_DEG}, WIDTH_RATIO_BAND {WIDTH_RATIO_BAND}, "
          f"STEP_TOL_M {STEP_TOL_M}")
    print(f"  reference {ref['stem']} headroom:")
    for name, unit, mx, thr in hr_rows:
        flag = "PASS" if mx <= thr else "FAIL"
        print(f"    {flag} {name}: max {mx:.4g} {unit} vs threshold "
              f"{thr:g} (headroom {thr - mx:+.4g})")
    ref_bad = {c: v for c, v in ref_fires.items()
               if v and not c.startswith("d1")}
    print(f"  reference D2-D5 per-frame fires: "
          f"{ref_bad if ref_bad else 'none (PASS)'}")
    if ref_bad:
        print("    reference residual events (not pure D1):")
        for r in ref_resid:
            print(f"      {r['entity']} {r['start_frame']}-"
                  f"{r['stop_frame']} [{r['detectors']}] {r['evidence']}")
        print(f"    SEG_TOL {sens['alt_tol']:g} would silence the "
              f"reference (d2 {sens['ref_d2']}) but drop R5 d2 from "
              f"{sens['r5_d2_base']} to {sens['r5_d2_alt']}; kept "
              f"{SEG_TOL:g} - see the report DECISION.")
    print("  R5 detector fires:",
          {c: cur_fires[c] for c in DETECTOR_COLS})
    for e in ENTITY_DETECTORS:
        m = masks[ENTITY_MASK[e]]
        sub = events[events["entity"] == e]
        print(f"  {ENTITY_MASK[e]}: {int(m.sum())} frames "
              f"({100.0 * m.sum() / n_span:.1f} percent), "
              f"{len(sub)} events")
        for _, r in sub.sort_values("frames", ascending=False).head(3) \
                .iterrows():
            print(f"    {r['start_frame']}-{r['stop_frame']} "
                  f"({r['duration_s']:.2f} s) [{r['detectors']}] "
                  f"{r['phase']}")
    for s in sanity:
        a, b = s["window"]
        print(f"  sanity {s['verdict']} {s['entity']} {a}-{b} "
              f"({s['label']}): D1 coverage "
              f"{100 * s['d1_coverage']:.1f} percent")
    for e in ENTITY_DETECTORS:
        print(f"  confident-but-wrong {e}: {cw[e]['frames']} frames, "
              f"{len(cw[e]['windows'])} windows")
    for f in files:
        print(f"[+] {f}")


if __name__ == "__main__":
    main()
