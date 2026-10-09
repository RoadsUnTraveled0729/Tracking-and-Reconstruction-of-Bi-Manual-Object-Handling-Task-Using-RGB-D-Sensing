#!/usr/bin/env python3
"""Hand-over analysis of the two-hand rail take (supervisor round 6,
C50; E-034).

The right hand carries the cube to the rail and slides it to about the
middle; the left hand takes it over and slides it to the far end. This
tool reads the pinned chain's outputs for the take (levelled object
track, filtered landmarks, failure mask, recovery angles) and reports:

  - which hand is at the cube on each frame: a measured wrist within
    the hold radius of the cube centre (eval/offset/carry.HOLD_RADIUS)
    on a carried frame; the forward-kinematics wrist of the recovery
    solve stands in where the wrist was not measured (on such a frame
    the FK wrist may itself come from the object-conditioned estimate,
    which sits near the cube by construction; the report counts the
    substitute frames, and on r7 both boundary frames of the handover
    use measured wrists);
  - the hand-over interval on the rail: from the first slide frame on
    which the left hand is at the cube to the last on which the right
    hand is, and where along the rail it happens;
  - the object-to-rail error per part of the slide (right hand, the
    hand-over, left hand): the perpendicular distance of the marker
    origin to the line fitted to ALL slide samples (eval/gt/
    eval_rail_scenario.py), so the parts share one reference;
  - both wrists through the kinematic model (moving_window_check.fk_wrist
    on eval/output/recovery_<alias>/angles_recovery.csv, the measured
    shoulders and the calibrated lengths), their distance to the rail
    line and to the marker origin while that hand slides;
  - the failure mask, the torso preparation and the joint-group states
    over each part, and the object track's undetected or bridged frames.

Offline geometry over the finished track; the solves it reads are the
causal ones of the pinned chain. Outputs eval/reports/<alias>_handover
.json, .md and .png. Run: python eval/failure/handover_analysis.py
--stem STEM
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
for sub in ("", "../common", "../offset", "../gt", "../../v1/kinematics"):
    sys.path.insert(0, str((HERE / sub).resolve()))
import paths                                   # noqa: E402
import carry                                   # noqa: E402
import eval_rail_scenario as ers               # noqa: E402
import recovery_core as rc                     # noqa: E402
from moving_window_check import fk_wrist       # noqa: E402
from root_frame import unity_from_sensor       # noqa: E402

ANGLE_COLS = ["root_ex", "root_ey", "root_ez", "Rsh_y", "Rsh_z", "Rsh_tau",
              "Rel_y", "Rel_z", "Lsh_y", "Lsh_z", "Lsh_tau", "Lel_y", "Lel_z"]
FLIP = np.array([1.0, -1.0, 1.0])
GROUPS = {"right": (1, 2, 3), "left": (4, 5, 6)}   # swing, twist, elbow


def runs(mask):
    out, on = [], False
    for i, b in enumerate(mask):
        if b and not on:
            on, s = True, i
        elif not b and on:
            on = False
            out.append((s, i - 1))
    if on:
        out.append((s, len(mask) - 1))
    return out


def stats_cm(v):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    if v.size == 0:
        return {"n": 0}
    return {"n": int(v.size), "median": round(float(np.median(v)) * 100, 2),
            "p95": round(float(np.percentile(v, 95)) * 100, 2),
            "max": round(float(v.max()) * 100, 2)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R7_STEM)
    args = ap.parse_args()
    stem = args.stem
    alias = paths.ALIAS[stem]

    inp = rc.build_inputs(stem)
    n, t, lm, world, seg_len = inp["n"], inp["t"], inp["lm_df"], inp["world"], inp["seg_len"]
    center, carried, det = inp["center"], inp["carried"], inp["det"]
    track = ers.load_track(stem)
    seg = ers.segment(track)
    xyz = track["xyz"]
    assert np.array_equal(track["frame"], np.arange(len(xyz)))
    rail = np.asarray(seg["rail"], int)
    c, d, along_rail, _, _ = ers.fit_line(xyz[rail])
    if d[0] < 0:
        d, along_rail = -d, -along_rail
    a0 = along_rail.min()

    def along(P):
        return (P - c) @ d - a0

    def perp(P):
        v = P - c
        return np.linalg.norm(v - np.outer(v @ d, d), axis=1)

    # measured wrists (levelled world) and the recovery-solve FK wrists
    ang_df = pd.read_csv(paths.EVAL_OUT / f"recovery_{alias}" / "angles_recovery.csv")
    assert len(ang_df) >= n and np.array_equal(ang_df["frame"].to_numpy()[:n], np.arange(n)), \
        "angles_recovery.csv does not cover the landmark table frame for frame"
    angles = ang_df[ANGLE_COLS].to_numpy(float)[:n]
    tags = ang_df[[f"tag_{k}" for k in range(7)]].to_numpy(int)[:n]
    wr_meas, wr_fk, wr_flag = {}, {}, {}
    for side in rc.SIDES:
        cam = lm[[f"{side}_wrist_x", f"{side}_wrist_y", f"{side}_wrist_z"]].to_numpy(float)[:n]
        wr_meas[side] = world.wrist_world(cam)
        wr_flag[side] = lm[f"{side}_wrist_src"].to_numpy(int)[:n]
        key = "R" if side == "right" else "L"
        Lu, Lf = seg_len[f"upper_arm_{key}"], seg_len[f"forearm_{key}"]
        sh_cam = lm[[f"{side}_shoulder_x", f"{side}_shoulder_y", f"{side}_shoulder_z"]].to_numpy(float)[:n]
        sh = np.array([unity_from_sensor(v) for v in sh_cam])
        fk = np.full((n, 3), np.nan)
        for i in range(n):
            if np.isfinite(sh[i]).all() and np.isfinite(angles[i]).all():
                fk[i] = world.wrist_world((fk_wrist(angles, i, sh, Lu, Lf, side) * FLIP)[None, :])[0]
        wr_fk[side] = fk
    # hand at the cube: measured wrist where measured, FK wrist otherwise
    near, dist, substitute = {}, {}, {}
    for side in rc.SIDES:
        w = wr_meas[side].copy()
        miss = ~np.isfinite(w).all(axis=1) | (wr_flag[side] != 0)
        w[miss] = wr_fk[side][miss]
        substitute[side] = miss
        dist[side] = np.linalg.norm(w - center, axis=1)
        with np.errstate(invalid="ignore"):
            near[side] = carried & det & (dist[side] < carry.HOLD_RADIUS)
    fk_vs_meas = {side: stats_cm(np.linalg.norm(wr_fk[side] - wr_meas[side], axis=1)[wr_flag[side] == 0])
                  for side in rc.SIDES}

    # parts of the slide: the contiguous frame span from the first to the
    # last slide sample (an undetected frame inside the span belongs to the
    # part its frame number falls in; the rail statistics skip it as NaN)
    on_rail = np.zeros(n, bool)
    on_rail[rail[0]:rail[-1] + 1] = True
    left_in = int(np.flatnonzero(on_rail & near["left"])[0])
    right_out = int(np.flatnonzero(on_rail & near["right"])[-1])
    assert left_in < right_out, "no overlap: the left hand arrives after the right hand left"
    part = np.full(n, "", dtype=object)
    part[on_rail & (np.arange(n) < left_in)] = "right"
    part[on_rail & (np.arange(n) >= left_in) & (np.arange(n) <= right_out)] = "handover"
    part[on_rail & (np.arange(n) > right_out)] = "left"
    both = on_rail & near["left"] & near["right"]
    assert len(runs(both)) == 1 and runs(both)[0] == (left_in, right_out), \
        f"both hands at the cube is not one contiguous run: {runs(both)}"
    hand = np.full(n, "none", dtype=object)
    hand[near["right"] & ~near["left"]] = "right"
    hand[near["left"] & ~near["right"]] = "left"
    hand[near["right"] & near["left"]] = "both"

    fm = pd.read_csv(paths.EVAL_OUT / f"recovery_{alias}" / "failure_mask.csv").iloc[:n]
    fail = {k: fm[f"fail_{k}"].to_numpy().astype(bool) for k in ("arm_L", "arm_R", "torso")}
    obj_df = pd.read_csv(paths.object_world_filtered(stem)).iloc[:n]
    assert "filled" in obj_df, "the cleaned object track carries the filled column"
    filled = obj_df["filled"].to_numpy().astype(bool)
    undetected = ~det
    # hip depth against the shoulder midpoint, camera frame (the E-027
    # signature), over the frames on which the root leaves constrained
    lm_z = {k: lm[f"{k}_z"].to_numpy(float)[:n] for k in ("left_hip", "right_hip", "left_shoulder", "right_shoulder")}
    smid_z = 0.5 * (lm_z["left_shoulder"] + lm_z["right_shoulder"])
    replaced = tags[:, 0] == 2

    speed = np.full(n, np.nan)
    ok = np.isfinite(xyz).all(axis=1)
    dt = np.diff(t)
    sp = np.linalg.norm(np.diff(xyz, axis=0), axis=1) / dt
    speed[1:] = np.where(ok[1:] & ok[:-1], sp, np.nan)

    parts = {}
    for name, holder in (("right", "right"), ("handover", None), ("left", "left")):
        m = part == name
        idx = np.flatnonzero(m)
        P = xyz[idx]
        e = perp(P)
        al = along(P)
        al = al[np.isfinite(al)]
        rec = {"frames": [int(idx[0]), int(idx[-1])], "n": int(len(idx)),
               "n_marker": int(np.isfinite(e).sum()),
               "time_s": [round(float(t[idx[0]]), 2), round(float(t[idx[-1]]), 2)],
               "along_rail_cm": [round(float(al.min()) * 100, 1), round(float(al.max()) * 100, 1)],
               "travel_cm": round(float(np.ptp(al)) * 100, 1),
               "perp_cm": stats_cm(e),
               "vertical_cm": stats_cm(np.abs((P - c)[:, 1] - ((P - c) @ d) * d[1])),
               "speed_median_cm_s": round(float(np.nanmedian(speed[idx])) * 100, 1),
               "undetected_frames": int(undetected[idx].sum()),
               "bridged_frames": int(filled[idx].sum()),
               "fail_frames": {k: int(fail[k][idx].sum()) for k in fail},
               "root_constrained_frames": int((tags[idx, 0] == 2).sum())}
        for side in rc.SIDES:
            g = GROUPS[side]
            rec[f"{side}_arm_states"] = {
                "swing": {s: int((tags[idx, g[0]] == v).sum()) for v, s in ((0, "measured"), (1, "held"), (2, "constrained"))},
                "twist": {s: int((tags[idx, g[1]] == v).sum()) for v, s in ((0, "measured"), (1, "held"), (2, "constrained"))},
                "elbow": {s: int((tags[idx, g[2]] == v).sum()) for v, s in ((0, "measured"), (1, "held"), (2, "constrained"))}}
            at = idx[near[side][idx]]
            rec[f"{side}_fk_wrist_to_line_cm"] = stats_cm(perp(wr_fk[side][idx]))
            rec[f"{side}_fk_wrist_to_marker_cm"] = stats_cm(np.linalg.norm(wr_fk[side][idx] - xyz[idx], axis=1))
            rec[f"{side}_fk_wrist_to_marker_at_cube_cm"] = stats_cm(np.linalg.norm(wr_fk[side][at] - xyz[at], axis=1))
            rec[f"{side}_wrist_at_cube_frames"] = int(near[side][idx].sum())
            rec[f"{side}_wrist_substituted_frames"] = int(substitute[side][idx].sum())
        parts[name] = rec

    hand_over = {
        "left_hand_arrives_frame": left_in, "right_hand_leaves_frame": right_out,
        "duration_s": round(float(t[right_out] - t[left_in]), 2),
        "both_at_cube_frames": int(both.sum()),
        "both_at_cube_runs": [[int(a), int(b)] for a, b in runs(both)],
        "along_rail_at_arrival_cm": round(float(along(xyz[left_in:left_in + 1])[0]) * 100, 1),
        "along_rail_at_release_cm": round(float(along(xyz[right_out:right_out + 1])[0]) * 100, 1),
        "rail_extent_cm": round(float(np.ptp(along_rail)) * 100, 1),
        "cube_travel_during_cm": parts["handover"]["travel_cm"],
        "cube_still_frames_during": int((speed[left_in:right_out + 1] < 2 * ers.DWELL_SPEED_M_S).sum()),
    }
    grip = json.loads((paths.EVAL_OUT / f"recovery_{alias}" / "grip_episodes.json").read_text())
    hip_depth = {k: {"min_m": round(float(np.nanmin((lm_z[k] - smid_z)[replaced])), 3),
                     "median_m": round(float(np.nanmedian((lm_z[k] - smid_z)[replaced])), 3)}
                 for k in ("left_hip", "right_hip")} if replaced.any() else {}
    summary = {
        "stem": stem, "alias": alias,
        "frame": "gravity-levelled desk world (x along the rail, y up, z away from the camera); centimetres in the statistics",
        "rail_line": {"n_slide_frames": int(len(rail)), "first": int(rail[0]), "last": int(rail[-1]),
                      "extent_cm": hand_over["rail_extent_cm"],
                      "perp_all_cm": stats_cm(perp(xyz[rail])),
                      "desk_level_m": float(seg["desk_y"]), "rail_level_m": float(seg["rail_y"]),
                      "rail_above_desk_cm": round(float(seg["rail_y"] - seg["desk_y"]) * 100, 2)},
        "hip_depth_minus_shoulder_mid_on_replaced_frames": hip_depth,
        "wrist_substituted_frames_whole_take": {s: int(substitute[s].sum()) for s in rc.SIDES},
        "handover_boundary_wrists_measured": bool(not substitute["left"][left_in] and not substitute["right"][right_out]),
        "hand_over": hand_over,
        "parts": parts,
        "grip_episodes": grip["episodes"],
        "hand_at_cube_frames_whole_take": {h: int((hand == h).sum()) for h in ("right", "left", "both", "none")},
        "fk_vs_measured_wrist_cm": fk_vs_meas,
        "failure_windows": {k: [[int(a), int(b)] for a, b in runs(fail[k])] for k in fail},
        "torso_replaced_runs": [[int(a), int(b)] for a, b in runs(tags[:, 0] == 2)],
        "object_track": {"undetected_frames": [int(i) for i in np.flatnonzero(undetected)],
                         "bridged_runs": [[int(a), int(b)] for a, b in runs(filled)]},
        "lengths_m": {k: seg_len[k] for k in ("upper_arm_R", "forearm_R", "upper_arm_L", "forearm_L")},
    }
    rep = paths.EVAL_REPORTS / f"{alias}_handover"
    rep.with_suffix(".json").write_text(json.dumps(summary, indent=1))
    pd.DataFrame({"frame": np.arange(n), "time_s": t, "part": part, "hand": hand,
                  "along_cm": np.where(ok, along(np.nan_to_num(xyz)) * 100, np.nan),
                  "perp_cm": np.where(ok, perp(np.nan_to_num(xyz)) * 100, np.nan),
                  "dist_right_cm": dist["right"] * 100, "dist_left_cm": dist["left"] * 100,
                  **{f"fk_{s}_{ax}": wr_fk[s][:, k] for s in rc.SIDES for k, ax in enumerate("xyz")},
                  **{f"meas_{s}_{ax}": wr_meas[s][:, k] for s in rc.SIDES for k, ax in enumerate("xyz")},
                  "root_tag": tags[:, 0]}).to_csv(rep.with_suffix(".csv"), index=False, float_format="%.4f")

    L = []
    a = L.append
    a(f"# Hand-over analysis: {stem} ({alias})")
    a("")
    a("Right hand carries and slides the cube to the middle of the rail, the")
    a("left hand takes over and slides it to the far end (supervisor round 6,")
    a("C50). Hand at the cube: a wrist within the hold radius of the cube")
    a("centre on a carried frame (measured wrist, or the recovery solve's")
    a("forward-kinematics wrist where the wrist was not measured). Errors are")
    a("perpendicular distances of the marker origin to the line fitted to all")
    a("slide samples (eval_rail_scenario.py), levelled by the carried-over")
    a("gravity of the recording of 2026-08-31 (E-034).")
    a("")
    r = summary["rail_line"]
    a(f"- slide frames {r['first']}-{r['last']} ({r['n_slide_frames']} frames), extent {r['extent_cm']} cm, "
      f"perpendicular median {r['perp_all_cm']['median']} / p95 {r['perp_all_cm']['p95']} / max {r['perp_all_cm']['max']} cm")
    h = hand_over
    a(f"- hand-over: left hand at the cube from frame {h['left_hand_arrives_frame']}, right hand until frame "
      f"{h['right_hand_leaves_frame']} ({h['duration_s']} s; both at the cube on {h['both_at_cube_frames']} frames, runs {h['both_at_cube_runs']}); "
      f"at {h['along_rail_at_arrival_cm']} to {h['along_rail_at_release_cm']} cm along the {h['rail_extent_cm']} cm slide; the cube moves "
      f"{h['cube_travel_during_cm']} cm meanwhile and is still on {h['cube_still_frames_during']} frames")
    a("")
    a("| part | frames | n | along rail (cm) | travel (cm) | perp median / p95 / max (cm) | vertical median (cm) | undetected / bridged | fail L / R / torso | root constrained |")
    a("|---|---|---|---|---|---|---|---|---|---|")
    for name in ("right", "handover", "left"):
        p = parts[name]
        a(f"| {name} | {p['frames'][0]}-{p['frames'][1]} | {p['n']} | {p['along_rail_cm'][0]} to {p['along_rail_cm'][1]} | {p['travel_cm']} | "
          f"{p['perp_cm']['median']} / {p['perp_cm']['p95']} / {p['perp_cm']['max']} | {p['vertical_cm']['median']} | "
          f"{p['undetected_frames']} / {p['bridged_frames']} | {p['fail_frames']['arm_L']} / {p['fail_frames']['arm_R']} / {p['fail_frames']['torso']} | {p['root_constrained_frames']} |")
    a("")
    a("Model wrists (forward kinematics of the recovery solve) per part:")
    a("")
    a("| part | side | at cube (frames) | wrist to rail line median / p95 (cm), whole part | wrist to marker origin median / p95 (cm), at the cube only | swing measured / held / constrained, whole part | twist m / h / c, whole part | elbow m / h / c, whole part |")
    a("|---|---|---|---|---|---|---|---|")
    for name in ("right", "handover", "left"):
        p = parts[name]
        for side in rc.SIDES:
            s = p[f"{side}_arm_states"]
            m = p[f"{side}_fk_wrist_to_marker_at_cube_cm"]
            a(f"| {name} | {side} | {p[f'{side}_wrist_at_cube_frames']} | {p[f'{side}_fk_wrist_to_line_cm']['median']} / {p[f'{side}_fk_wrist_to_line_cm']['p95']} | "
              f"{m.get('median', 'n/a')} / {m.get('p95', 'n/a')} | "
              f"{s['swing']['measured']} / {s['swing']['held']} / {s['swing']['constrained']} | {s['twist']['measured']} / {s['twist']['held']} / {s['twist']['constrained']} | "
              f"{s['elbow']['measured']} / {s['elbow']['held']} / {s['elbow']['constrained']} |")
    a("")
    a(f"- FK wrist against the measured wrist (measured frames): right median {fk_vs_meas['right']['median']} / p95 {fk_vs_meas['right']['p95']} cm, "
      f"left median {fk_vs_meas['left']['median']} / p95 {fk_vs_meas['left']['p95']} cm")
    a(f"- grip episodes (state machine): {json.dumps({s: [[e['start'], e['stop']] for e in grip['episodes'][s]] for s in rc.SIDES})}")
    a(f"- failure windows: {json.dumps(summary['failure_windows'])}")
    a(f"- torso replaced (root constrained) runs: {summary['torso_replaced_runs']}; hip depth minus shoulder-mid depth on those frames (m): {json.dumps(hip_depth)}")
    a(f"- rail level {seg['rail_y']:.4f} m, desk level {seg['desk_y']:.4f} m, rail above desk {summary['rail_line']['rail_above_desk_cm']} cm; wrists substituted by the FK wrist: {summary['wrist_substituted_frames_whole_take']}, handover boundary wrists measured: {summary['handover_boundary_wrists_measured']}")
    a(f"- object track: undetected {summary['object_track']['undetected_frames']}, bridged runs {summary['object_track']['bridged_runs']}")
    a("")
    rep.with_suffix(".md").write_text("\n".join(L))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(3, 1, figsize=(11, 9), sharex=True)
    cols = {"right": "tab:blue", "left": "tab:green", "both": "tab:purple", "none": "0.7"}
    axes[0].scatter(t, np.where(ok, along(np.nan_to_num(xyz)) * 100, np.nan), c=[cols[x] for x in hand], s=4)
    axes[0].set_ylabel("along rail (cm)")
    axes[0].axvspan(t[left_in], t[right_out], color="0.9", zorder=0)
    axes[1].plot(t, dist["right"] * 100, "tab:blue", lw=0.8, label="right wrist to cube centre")
    axes[1].plot(t, dist["left"] * 100, "tab:green", lw=0.8, label="left wrist to cube centre")
    axes[1].axhline(carry.HOLD_RADIUS * 100, color="k", lw=0.6, ls="--")
    axes[1].set_ylabel("cm")
    axes[1].legend(fontsize=8)
    axes[1].axvspan(t[left_in], t[right_out], color="0.9", zorder=0)
    axes[2].plot(t, np.where(on_rail, perp(np.nan_to_num(xyz)) * 100, np.nan), "k", lw=0.8)
    axes[2].set_ylabel("perp to rail line (cm)")
    axes[2].set_xlabel("time (s)")
    axes[2].axvspan(t[left_in], t[right_out], color="0.9", zorder=0)
    for k, cc in (("torso", "tab:red"), ("arm_L", "tab:green"), ("arm_R", "tab:blue")):
        for a_, b_ in runs(fail[k]):
            axes[2].axvspan(t[a_], t[b_], color=cc, alpha=0.15)
    fig.suptitle(f"{alias}: hand at the cube (blue right, green left, purple both), the hand-over shaded")
    plt.tight_layout()
    plt.savefig(rep.with_suffix(".png"), dpi=120)
    print(f"PASS: {rep.with_suffix('.md')}")
    print("  " + "\n  ".join(L[10:17]))


if __name__ == "__main__":
    main()
