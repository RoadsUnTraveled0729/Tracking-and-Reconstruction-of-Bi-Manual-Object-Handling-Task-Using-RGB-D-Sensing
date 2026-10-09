#!/usr/bin/env python3
"""Build the Chapter 7 (Evaluation) figures into writing/v7/figures/.

Every panel is regenerated from the frozen R5 artifacts so the chapter
figures carry the same numbers as the reports:

  ch7_fig_failures.png   detector mask timeline over the recording
                         (eval/output/recovery_r5/failure_mask.csv,
                          eval/reports/r5_failure_mask.md)
  ch7_fig_waypoints.png  3D loop, the 8 waypoints, the ideal polyline,
                         and the point-to-path distance over time
                         (eval/gt/labeled_path_r5.json,
                          eval/reports/r5_waypoint_eval.md). The speed
                         and threshold-sweep panels of the report
                         figure are dropped: the thesis carries no
                         speed values (thesis-structure-rules rule 1).
  ch7_fig_torso.png      root yaw and pelvis depth through the worst
                         torso corruption window, with the depth-jump
                         gate and ray repair disabled and enabled
                         (E-011b in eval/DECISIONS.md)
  ch7_fig_recovery.png   per-frame wrist position error of the three
                         methods over the two moving outages
                         (eval/reports/r5_recovery_moving.md)
  ch7_fig_overlay.png    two stills from the reprojection overlays
                         inside the long left-arm failure window

Run: python writing/v7/scripts/make_ch7_figs.py [--only NAME ...]
"""
import argparse
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                       # noqa: E402
import pandas as pd                      # noqa: E402

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v7" / "figures"
FIG.mkdir(parents=True, exist_ok=True)
for sub in ("eval/common", "eval/gt", "eval/failure", "eval/inspect",
            "eval/offset", "v1/kinematics"):
    sys.path.insert(0, str(REPO / sub))

STEM = "recording_20260825_222315"
ALIAS = "r5"
RECOV = REPO / "eval" / "output" / f"recovery_{ALIAS}"
REPORTS = REPO / "eval" / "reports"

plt.rcParams.update({"font.size": 9, "axes.titlesize": 10,
                     "figure.dpi": 200, "savefig.dpi": 200,
                     "font.family": "DejaVu Sans"})


def runs(mask):
    """Contiguous True runs of a bool mask as (start, stop) inclusive."""
    idx = np.flatnonzero(mask)
    if idx.size == 0:
        return []
    brk = np.flatnonzero(np.diff(idx) > 1)
    return list(zip(np.r_[idx[0], idx[brk + 1]].tolist(),
                    np.r_[idx[brk], idx[-1]].tolist()))


# --------------------------------------------------------------- 1
def fig_failures():
    fm = pd.read_csv(RECOV / "failure_mask.csv")
    t = fm["time_s"].to_numpy()
    insp = json.loads((REPORTS / f"{STEM}_inspection.json").read_text())
    ph = insp["phases"]

    rows = [("torso", "fail_torso", "tab:purple"),
            ("left arm", "fail_arm_L", "tab:blue"),
            ("right arm", "fail_arm_R", "tab:red")]

    span0 = ph["person_present"][0] + 5      # the report's 5-frame warmup
    step, half = 1.6, 0.30
    ypos = [(len(rows) - 1 - k) * step for k in range(len(rows))]

    fig, ax = plt.subplots(figsize=(9.0, 3.1))
    for k, (label, col, colour) in enumerate(rows):
        y = ypos[k]
        m = fm[col].to_numpy().astype(bool)
        ax.add_patch(plt.Rectangle((t[0], y - half), t[-1] - t[0], 2 * half,
                                   facecolor="0.93", edgecolor="none"))
        for a, b in runs(m):
            ax.add_patch(plt.Rectangle((t[a], y - half),
                                       max(t[b] - t[a], 0.08), 2 * half,
                                       facecolor=colour, edgecolor="none"))
        pct = 100.0 * m[span0:].mean()
        ax.text(t[-1] + 0.6, y, f"{pct:.1f}%", va="center", fontsize=8.5,
                color=colour)

    for a, b in [ph["approach"], ph["manipulation"]]:
        ax.axvline(t[a], color="0.55", lw=0.8, ls=":")
    ax.text(t[ph["approach"][0]] + 0.4, ypos[0] + 0.90, "approach",
            fontsize=8, color="0.35")
    ax.text(t[ph["manipulation"][0]] + 0.4, ypos[0] + 0.90, "manipulation",
            fontsize=8, color="0.35")

    ann = [(1182, 1544, ypos[0], "one hip depth off the wrong surface"),
           (1427, 1668, ypos[1], "left elbow and wrist blocked"),
           (1775, 1893, ypos[2], "right elbow blocked")]
    for a, b, y, label in ann:
        ax.annotate(label, xy=(0.5 * (t[a] + t[b]), y + half),
                    xytext=(0.5 * (t[a] + t[b]), y + 0.62),
                    ha="center", fontsize=7.5, color="0.2",
                    arrowprops=dict(arrowstyle="-", lw=0.7, color="0.4"))

    ax.set_yticks(ypos)
    ax.set_yticklabels([r[0] for r in rows])
    ax.set_ylim(-0.9, ypos[0] + 1.25)
    ax.set_xlim(t[0], t[-1] + 3.2)
    ax.set_xlabel("time (s)")
    ax.set_title("frames the failure detectors reject, over the recording")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.tight_layout()
    out = FIG / "ch7_fig_failures.png"
    fig.savefig(out)
    plt.close(fig)
    print("wrote", out)


# --------------------------------------------------------------- 2
def fig_waypoints():
    import detect_waypoints as dw
    import path_metrics as pm

    track = dw.load_center_track(STEM)
    spec = pm.load_path(REPO / "eval" / "gt" / "labeled_path_r5.json")
    frames, dists, _segidx, overall, seg_stats = dw.path_errors(track, spec)

    t = track["t"]
    clev = track["center_lev"]
    h = track["height"]
    vidx = np.flatnonzero(track["valid"])
    P = np.array([w["leveled_xyz"] for w in spec["waypoints"]])
    Ph = np.array([w["height_above_table_m"] for w in spec["waypoints"]])

    fig = plt.figure(figsize=(10.4, 5.4))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.75, 1.0],
                          left=0.02, right=0.965, top=0.90, bottom=0.12,
                          wspace=0.16)

    ax = fig.add_subplot(gs[0, 0], projection="3d")
    ctx = track["carried"] & ~track["loop"] & track["detected"]
    ax.scatter(clev[ctx, 0], clev[ctx, 2], h[ctx], s=2, color="0.82",
               label="pick-up and set-down", depthshade=False)
    ax.scatter(clev[vidx, 0], clev[vidx, 2], h[vidx], s=3.5,
               color="tab:blue", depthshade=False,
               label="measured cube path")
    Pc = np.vstack([P, P[:1]])
    Phc = np.r_[Ph, Ph[0]]
    ax.plot(Pc[:, 0], Pc[:, 2], Phc, "--", color="crimson", lw=1.8,
            label="designed path")
    ax.scatter(P[:, 0], P[:, 2], Ph, s=150, facecolor="white",
               edgecolor="crimson", linewidth=1.8, depthshade=False,
               label="waypoint", zorder=10)
    for k, (p, phh) in enumerate(zip(P, Ph)):
        ax.text(p[0], p[2], phh, str(k + 1), ha="center", va="center",
                fontsize=9, color="crimson", fontweight="bold", zorder=11)
    gx = np.linspace(clev[vidx, 0].min() - 0.05,
                     clev[vidx, 0].max() + 0.05, 2)
    gz = np.linspace(clev[vidx, 2].min() - 0.05,
                     clev[vidx, 2].max() + 0.05, 2)
    GX, GZ = np.meshgrid(gx, gz)
    ax.plot_surface(GX, GZ, np.zeros_like(GX), color="0.85", alpha=0.35,
                    linewidth=0)
    ax.text(gx[0], gz[0], 0.0, "desk", fontsize=8, color="0.4")
    ax.set_xlabel("x (m), operator's left")
    ax.set_ylabel("z (m), away from camera")
    ax.set_zlabel("height above desk (m)")
    ax.set_yticks([0.25, 0.35, 0.45, 0.55])
    ax.set_box_aspect((np.ptp(clev[vidx, 0]) + 0.1,
                       np.ptp(clev[vidx, 2]) + 0.1,
                       np.ptp(h[vidx]) + 0.1))
    ax.view_init(elev=28, azim=-55)
    ax.legend(loc="upper left", fontsize=7.5, framealpha=0.9)
    ax.set_title("the measured cube path against the eight designed "
                 "waypoints\n(1 start, 2 back, 3 handover, 4 left, "
                 "5 forward, 6 lift top, 7 wire handover, 8 wire left)",
                 fontsize=9)

    ax2 = fig.add_subplot(gs[0, 1])
    tv = t[frames]
    brk = np.flatnonzero(np.diff(frames) > 1)
    xs = np.insert(tv.astype(float), brk + 1, np.nan)
    ys = np.insert(dists * 100.0, brk + 1, np.nan)
    ax2.plot(xs, ys, lw=0.9, color="tab:blue")
    med = float(np.median(dists)) * 100
    p95 = float(np.percentile(dists, 95)) * 100
    ax2.axhline(med, color="0.2", lw=1.0,
                label=f"median {med:.2f} cm")
    ax2.axhline(p95, color="0.2", lw=1.0, ls=":",
                label=f"p95 {p95:.2f} cm")
    ax2.set_xlabel("time (s)")
    ax2.set_ylabel("distance to the designed path (cm)")
    ax2.set_title("point-to-path distance over the loop", fontsize=9)
    ax2.legend(fontsize=8, framealpha=0.9)
    ax2.grid(alpha=0.25)
    ax2.annotate("closing descent:\nthe two unpaused corners",
                 xy=(tv[np.argmax(dists)], dists.max() * 100),
                 xytext=(0.30, 0.72), textcoords="axes fraction",
                 fontsize=7.5, color="0.2",
                 arrowprops=dict(arrowstyle="->", lw=0.7, color="0.4"))
    out = FIG / "ch7_fig_waypoints.png"
    fig.savefig(out)
    plt.close(fig)
    print("wrote", out,
          "| median %.2f cm p95 %.2f cm max %.2f cm over %d frames"
          % (med, p95, dists.max() * 100, len(dists)))


# --------------------------------------------------------------- 3
def _torso_tracks():
    """Root yaw and pelvis depth with the ray repair off and on."""
    import recovery_core as rc
    from occlusion_ext import RobustChainSolver
    from occlusion import points_from_row
    from root_frame import unity_from_sensor

    inp = rc.build_inputs(STEM)
    n, lm = inp["n"], inp["lm_df"]

    def run(z_tol):
        solver = RobustChainSolver(seg_len=dict(inp["seg_len"]),
                                   z_tol=z_tol)
        yaw = np.zeros(n)
        pel = np.full((n, 3), np.nan)
        for i, (_, row) in enumerate(lm.iterrows()):
            a, _, _ = solver.solve(rc.solver_points(row))
            yaw[i] = a[1]
            lh = solver.last_points.get("left_hip")
            rh = solver.last_points.get("right_hip")
            if lh is not None and rh is not None \
                    and np.all(np.isfinite(lh)) and np.all(np.isfinite(rh)):
                pel[i] = 0.5 * (lh + rh)
        return yaw, pel

    yaw_off, _ = run(None)
    yaw_on, pel_on = run(0.10)

    raw = np.full((n, 3), np.nan)
    for i, (_, row) in enumerate(lm.iterrows()):
        p = points_from_row(row)
        lh, rh = p.get("left_hip"), p.get("right_hip")
        if lh is not None and rh is not None \
                and np.all(np.isfinite(lh)) and np.all(np.isfinite(rh)):
            raw[i] = 0.5 * (unity_from_sensor(lh) + unity_from_sensor(rh))
    t = np.asarray(inp["t"])[:n]
    return t, yaw_off, yaw_on, raw[:, 2], pel_on[:, 2]


def fig_torso():
    t, yaw_off, yaw_on, z_raw, z_rep = _torso_tracks()
    a, b = 956, 1130                       # the worst torso window
    lo, hi = max(a - 90, 0), min(b + 90, len(t) - 1)
    sl = slice(lo, hi + 1)

    def centred(y):
        m = np.degrees(np.arctan2(np.mean(np.sin(np.radians(y[a:b + 1]))),
                                  np.mean(np.cos(np.radians(y[a:b + 1])))))
        return (y - m + 180.0) % 360.0 - 180.0

    fig, axes = plt.subplots(2, 1, figsize=(8.6, 5.0), sharex=True)
    ax = axes[0]
    ax.axvspan(t[a], t[b], color="0.90", zorder=0)
    ax.plot(t[sl], centred(yaw_off)[sl], lw=1.0, color="tab:red",
            label="depth-jump check disabled")
    ax.plot(t[sl], centred(yaw_on)[sl], lw=1.4, color="tab:blue",
            label="depth-jump check and ray repair active")
    ax.set_ylabel("root yaw (deg)")
    # legend placed above the axes: inside the panel it covered the yaw
    # minimum at the left edge of the shaded window
    ax.legend(fontsize=8, ncol=2, loc="lower left",
              bbox_to_anchor=(0.0, 1.0), frameon=False)
    ax.grid(alpha=0.25)

    ax = axes[1]
    ax.axvspan(t[a], t[b], color="0.90", zorder=0)
    ax.plot(t[sl], 100 * z_raw[sl], lw=1.0, color="tab:red",
            label="pelvis from the measured hips")
    ax.plot(t[sl], 100 * z_rep[sl], lw=1.4, color="tab:blue",
            label="pelvis from the repaired hips")
    ax.set_ylabel("pelvis depth (cm)")
    ax.set_xlabel("time (s)")
    ax.legend(fontsize=8, ncol=2, loc="lower left",
              bbox_to_anchor=(0.0, 1.0), frameon=False)
    ax.grid(alpha=0.25)

    fig.suptitle("the torso through the longest depth-corruption window "
                 "(shaded)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 0.955))
    out = FIG / "ch7_fig_torso.png"
    fig.savefig(out)
    plt.close(fig)

    def spread(y):
        v = centred(y)[a:b + 1]
        return v.max() - v.min()
    print("wrote", out,
          "| window %d-%d yaw spread off %.1f deg -> on %.1f deg; "
          "pelvis depth spread raw %.1f cm -> repaired %.1f cm"
          % (a, b, spread(yaw_off), spread(yaw_on),
             100 * (np.nanmax(z_raw[a:b + 1]) - np.nanmin(z_raw[a:b + 1])),
             100 * (np.nanmax(z_rep[a:b + 1]) - np.nanmin(z_rep[a:b + 1]))))


# --------------------------------------------------------------- 4
def fig_recovery():
    import recovery_core as rc
    from moving_window_check import WINDOWS, fk_wrist
    from root_frame import unity_from_sensor

    inp0 = rc.build_inputs(STEM)
    lm = inp0["lm_df"]
    t = np.asarray(inp0["t"])

    fig, axes = plt.subplots(1, len(WINDOWS), figsize=(9.0, 3.2),
                             sharey=True)
    styles = {"hold": ("tab:red", "hold the last angles", 1.0, "-"),
              "masked": ("0.45", "direction memory", 1.0, "--"),
              "recovery": ("tab:blue", "object-conditioned recovery",
                           1.5, "-")}
    summary = {}
    for k, (side, a, b) in enumerate(WINDOWS):
        sl_len = inp0["seg_len"]
        Lu = sl_len[f"upper_arm_{'R' if side == 'right' else 'L'}"]
        Lf = sl_len[f"forearm_{'R' if side == 'right' else 'L'}"]
        sh = np.array([unity_from_sensor(v) for v in
                       lm[[f"{side}_shoulder_x", f"{side}_shoulder_y",
                           f"{side}_shoulder_z"]].to_numpy()])
        wm = np.array([unity_from_sensor(v) for v in
                       lm[[f"{side}_wrist_x", f"{side}_wrist_y",
                           f"{side}_wrist_z"]].to_numpy()])
        em = np.zeros(inp0["n"], bool)
        em[a:b + 1] = True
        inp = rc.build_inputs(STEM, extra_fail={side: em})
        res = {"hold": rc.run_hold_baseline(inp),
               "masked": rc.run_variant(inp, "masked"),
               "recovery": rc.run_variant(inp, "recovery")}
        ax = axes[k]
        for name, r in res.items():
            colour, label, lw, ls = styles[name]
            # frames without a measured wrist carry no error, exactly as
            # the moving-window report scores them
            e = np.array([np.linalg.norm(
                fk_wrist(r["angles"], i, sh, Lu, Lf, side) - wm[i]) * 100
                if np.isfinite(wm[i]).all() else np.nan
                for i in range(a, b + 1)])
            ax.plot(t[a:b + 1] - t[a], e, color=colour, lw=lw, ls=ls,
                    label=label)
            summary.setdefault(name, []).append(
                (float(np.nanmedian(e)), float(np.nanmax(e))))
        ax.set_xlabel("time since the landmarks were removed (s)")
        ax.grid(alpha=0.25)
        ax.set_title(f"outage {k + 1}: right arm, {b - a + 1} frames",
                     fontsize=9)
    axes[0].set_ylabel("wrist position error (cm)")
    axes[0].legend(fontsize=8, framealpha=0.9)
    fig.tight_layout()
    out = FIG / "ch7_fig_recovery.png"
    fig.savefig(out)
    plt.close(fig)
    print("wrote", out)
    for name, vals in summary.items():
        print("   %-9s median %s cm, max %s cm" % (
            name, [round(v[0], 2) for v in vals],
            [round(v[1], 2) for v in vals]))


# --------------------------------------------------------------- 5
BURN_IN_ROWS = 30      # rows of debug text at the top of the overlays


def fig_overlay(frame=1520):
    import cv2
    pairs = [(REPO / "eval/output/v1_check_r5/v1_overlay_baseline.mp4",
              "landmarks taken as measured"),
             (REPO / "eval/output/recovery_r5_overlay/"
                     "v1_overlay_recovery.mp4",
              "failed landmarks removed and recovered")]
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.6))
    for ax, (path, label) in zip(axes, pairs):
        cap = cv2.VideoCapture(str(path))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame)
        ok, img = cap.read()
        cap.release()
        assert ok, f"could not read frame {frame} of {path}"
        # the overlay renderer burns a debug line (frame index, time, mask
        # word) into the top-left corner at y = 20; crop that strip off
        img = img[BURN_IN_ROWS:, :]
        ax.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        ax.set_title(label, fontsize=9)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.tight_layout()
    out = FIG / "ch7_fig_overlay.png"
    fig.savefig(out)
    plt.close(fig)
    print("wrote", out, "| frame", frame)


BUILDERS = {"failures": fig_failures, "waypoints": fig_waypoints,
            "torso": fig_torso, "recovery": fig_recovery,
            "overlay": fig_overlay}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", choices=sorted(BUILDERS))
    args = ap.parse_args()
    for name in (args.only or sorted(BUILDERS)):
        BUILDERS[name]()
