"""Numbers for the Chapter 5 worked example (Section 5.6).

Runs the real recovery pipeline (eval/failure/recovery_core.py on top
of v1/kinematics/occlusion_ext.py) on the rail recording, exactly as
eval/failure/run_recovery.py produced eval/output/recovery_r6b/, and
prints every intermediate quantity of one failure frame:

  Case B  the lost right wrist placed from the measured object pose
          and the carried hand-object offset, equation (5.7), then
          carried into person space by the calibrated transformation;
  Case C  the right elbow placed by two-link inverse kinematics,
          equations (5.8)-(5.12), on the remembered upper-arm direction.

Every value is taken from the pipeline state at that frame and then
re-derived by hand from the chapter equations, and the two are
compared. The angles the re-run produces are compared with the stored
angles_recovery.csv row, which proves the re-run is the pipeline.

Inputs (the ones recovery_core.build_inputs reads for this stem):
  v1/mediapipe/output/<stem>_landmarks_filtered.csv   filtered landmarks
  eval/output/<stem>_scaled_object_world_filtered_clean.csv  object track
  eval/output/scene_calibration_r6bc.json             scene calibration
  eval/reports/<stem>_offset_fit.json                 segment lengths L1, L2
  eval/reports/<stem>_inspection.json                 manipulation envelope
  eval/output/recovery_r6b/failure_mask.csv           failure masks

Run:  python writing/v8/scripts/ch5_worked_example.py [--frame F] [--scan]

Frame used in the chapter: 560 (t = 18.68 s), ten frames into the
right-wrist window that starts at frame 550, 17 frames after the
Chapter 3 worked-example frame 533. --scan prints the whole window.
No frame of this recording exercises Case A cleanly: the marker is
measured on every flagged right-arm frame, and the only wrist
recoveries not anchored on the object (frames 7-24) have the whole
arm flagged, so the elbow there comes from the memory as well.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[3]
for sub in ("eval/failure", "eval/common", "eval/offset", "v1/kinematics"):
    sys.path.insert(0, str(REPO / sub))

import paths                                   # noqa: E402
import carry                                   # noqa: E402
import grip_state                              # noqa: E402
import recovery_core as rc                     # noqa: E402
from fit_offset import load_tracks             # noqa: E402
from occlusion_ext import RobustChainSolver    # noqa: E402

SIDE = "right"
SH, EL, WR = "right_shoulder", "right_elbow", "right_wrist"
USEG, FSEG = "upper_arm_R", "forearm_R"


def fmt(v, nd=2):
    v = np.atleast_1d(np.asarray(v, float))
    return "(" + ", ".join(f"{x:.{nd}f}" for x in v) + ")"


def build(stem):
    """recovery_core.build_inputs plus the per-frame offset it does
    not return (recomputed with the same calls, then checked)."""
    inp = rc.build_inputs(stem)
    calib, world, lm_df, obj_lev, R_lev, det, wr, wrist_flag, t = \
        load_tracks(stem, str(paths.calib_for(stem)))
    n = inp["n"]
    side = SIDE
    d_loc = np.einsum("nij,ni->nj", R_lev, wr[side] - obj_lev)
    forearm = carry.forearm_ok(lm_df, side)
    hold_clean = carry.holding_mask(
        inp["center"], wr[side], wrist_flag[side], det, inp["carried"],
        forearm) & ~inp["fail"][side]
    # note: build_inputs computes hold_clean with the fail mask BEFORE
    # the D6 grip-plausibility frames are added; D6 frames are removed
    # from hold_clean there only through fail (pre-D6). Recompute the
    # same way: fail without D6 is the detector CSV mask.
    fm = pd.read_csv(paths.EVAL_OUT / f"recovery_{paths.ALIAS[stem]}"
                     / "failure_mask.csv").iloc[:n]
    fail_pre = fm["fail_arm_R"].to_numpy().astype(bool)
    hold_clean = carry.holding_mask(
        inp["center"], wr[side], wrist_flag[side], det, inp["carried"],
        forearm) & ~fail_pre
    mu = grip_state.time_local_mu(d_loc, hold_clean, inp["episodes"][side])
    mu_ep = grip_state.per_frame_mu(n, inp["episode_fits"][side])
    gaps = ~np.isfinite(mu).all(axis=1)
    mu[gaps] = mu_ep[gaps]
    w_lev = obj_lev + np.einsum("nij,nj->ni", R_lev, mu)
    w_sol = rc._leveled_to_solver_space(w_lev, world)
    ok = np.isfinite(w_sol).all(axis=1) & np.isfinite(
        inp["w_hat_solver"][side]).all(axis=1)
    err = np.abs(w_sol[ok] - inp["w_hat_solver"][side][ok]).max()
    assert err < 1e-9, f"offset recomputation differs by {err}"
    return inp, dict(world=world, obj=obj_lev, R=R_lev, det=det,
                     wr_lev=wr[side], wrist_flag=wrist_flag[side],
                     mu=mu, d_loc=d_loc, hold_clean=hold_clean,
                     w_lev=w_lev, w_sol=w_sol, lm_df=lm_df, fm=fm, t=t)


def run_to(inp, frame):
    """Re-run the recovery variant up to `frame`; return the solver
    state just before that frame's solve and the outputs after it."""
    solver = RobustChainSolver(seg_len=dict(inp["seg_len"]))
    lm_df = inp["lm_df"]
    for i, (_, row) in enumerate(lm_df.iterrows()):
        fr = {s: bool(inp["fail"][s][i]) for s in rc.SIDES}
        pts = rc.solver_points(row, fr)
        obs = {s: (inp["w_hat_solver"][s][i]
                   if np.isfinite(inp["w_hat_solver"][s][i]).all()
                   else None) for s in rc.SIDES}
        if i == frame:
            before = dict(u=dict((k, v.copy()) for k, v in solver.u.items()),
                          k=dict(solver.k), L=dict(solver.L),
                          pts={k: v.copy() for k, v in pts.items()},
                          obs={k: (None if v is None else np.array(v))
                               for k, v in obs.items()},
                          obj_rec=dict(solver.obj_recovered),
                          rec=dict(solver.recovered))
        out = solver.solve(pts, obj=obs)
        if i == frame:
            after = dict(angles=out[0].copy(), mask=int(out[1]),
                         tags=out[2].copy(),
                         pts={k: (None if v is None else v.copy())
                              for k, v in solver.last_points.items()},
                         obj_rec=dict(solver.obj_recovered),
                         rec=dict(solver.recovered))
            return before, after
    raise ValueError("frame beyond recording")


def scan(inp, ex, frames):
    print("frame  time   det  fail_L  k_el  r/(L1+L2)  |mu|   elbow src")
    for f in frames:
        b, a = run_to(inp, f)
        ik = a["obj_rec"].get("right_elbow_ik", 0) - \
            b["obj_rec"].get("right_elbow_ik", 0)
        wo = a["obj_rec"].get("right_wrist_obj", 0) - \
            b["obj_rec"].get("right_wrist_obj", 0)
        S = b["pts"].get(SH)
        W = b["obs"][SIDE]
        r = np.linalg.norm(W - S) if S is not None and W is not None \
            else np.nan
        reach = b["L"][USEG] + b["L"][FSEG]
        print(f"{f:5d} {ex['t'][f]:6.2f}  {int(ex['det'][f])}    "
              f"{int(inp['fail']['left'][f])}     {b['k'].get(EL, 0):3d}   "
              f"{r / reach:6.3f}   {np.linalg.norm(ex['mu'][f]):.3f}  "
              f"wrist_obj={wo} elbow_ik={ik}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stem", default=paths.R6B_STEM)
    ap.add_argument("--frame", type=int, default=560)
    ap.add_argument("--scan", action="store_true")
    args = ap.parse_args()
    stem = args.stem
    inp, ex = build(stem)
    n = inp["n"]
    fail, hold, det = inp["fail"][SIDE], inp["holding"][SIDE], ex["det"]
    cand = fail & hold & det & np.isfinite(inp["w_hat_solver"][SIDE]).all(axis=1)
    idx = np.where(cand)[0]
    print(f"stem {stem}, {n} frames; right wrist flagged while holding "
          f"with the marker measured: {len(idx)} frames "
          f"[{idx.min()}..{idx.max()}]")
    print("segment lengths (m):", inp["seg_len"])
    print("right grip episodes:", inp["episodes"][SIDE])
    for ep in inp["episode_fits"][SIDE]:
        print("  episode fit:", ep["start"], ep["stop"], ep["n_clean"],
              None if ep["mu"] is None else fmt(ep["mu"], 4), ep["source"])
    if args.scan:
        scan(inp, ex, idx)
        return

    f = args.frame
    b, a = run_to(inp, f)
    L1, L2 = b["L"][USEG], b["L"][FSEG]
    print(f"\n=== frame {f}, t = {ex['t'][f]:.2f} s ===")
    fmrow = ex["fm"].iloc[f]
    print("detectors:", {c: int(fmrow[c]) for c in ex["fm"].columns
                         if c.startswith(("d", "fail"))})
    row = ex["lm_df"].iloc[f]
    print("right wrist src/vis/flag:", row["right_wrist_src"],
          row["right_wrist_vis"], row.get("right_wrist_flag"))
    print("right elbow src/vis:", row["right_elbow_src"], row["right_elbow_vis"])
    print("points entering the layer (person space, failed arm removed):")
    for k_, v in b["pts"].items():
        print(f"  {k_:15s} {fmt(v, 4)}")

    # ---- Case B: wrist from the object ---------------------------------
    o = ex["obj"][f]
    R = ex["R"][f]
    h = ex["mu"][f]
    print("\n-- Case B, equation (5.7) --")
    print("object origin o (levelled world, m):", fmt(o, 4))
    print("R_obj rows:", [fmt(rw, 4) for rw in R])
    print("offset h (object axes, m):", fmt(h, 4), " |h| =",
          f"{np.linalg.norm(h):.4f}")
    src = "episode mean" if not np.isfinite(
        grip_state.time_local_mu(ex["d_loc"], ex["hold_clean"],
                                 inp["episodes"][SIDE])[f]).all() \
        else "time-local recursive estimate (5.4), frozen through the window"
    print("offset source:", src)
    # frames since last clean update
    last_clean = np.where(ex["hold_clean"][:f])[0]
    print("last clean offset update frame:", last_clean.max() if len(last_clean) else None)
    w_lev = o + R @ h
    print("w = o + R_obj h (levelled world):", fmt(w_lev, 4),
          " pipeline:", fmt(ex["w_lev"][f], 4))
    world = ex["world"]
    A = np.linalg.inv(world.M) @ world.G.T
    tvec = -np.linalg.inv(world.M) @ world.cam_pos
    w_P = A @ w_lev + tvec
    print("levelled world -> person space: rotation block")
    for rw in A:
        print("   ", fmt(rw, 4))
    print("  translation:", fmt(tvec, 4), " det:", f"{np.linalg.det(A):.3f}")
    print("w in person space (hand):", fmt(w_P, 4),
          " pipeline w_hat_solver:", fmt(inp["w_hat_solver"][SIDE][f], 4),
          " solver wrist after solve:", fmt(a["pts"][WR], 4))
    # measured (flagged) wrist, for the record
    wm = np.array([row["right_wrist_x"], -row["right_wrist_y"], row["right_wrist_z"]])
    print("the flagged measured wrist (person space):", fmt(wm, 4))

    # ---- Case C: elbow by two-link IK ---------------------------------
    print("\n-- Case C, equations (5.8)-(5.12) --")
    S = b["pts"][SH]
    print("shoulder p_sh:", fmt(S, 4), " L1 =", f"{L1:.4f}", " L2 =", f"{L2:.4f}")
    bvec = w_P - S
    rr = np.linalg.norm(bvec)
    bh = bvec / rr
    print("b = w - p_sh:", fmt(bvec, 4), " r =", f"{rr:.4f}",
          " r/(L1+L2) =", f"{rr / (L1 + L2):.4f}", " b_hat:", fmt(bh, 4))
    cj = (L1 * L1 + rr * rr - L2 * L2) / (2 * L1 * rr)
    print("cos j =", f"{cj:.4f}", " j =", f"{np.degrees(np.arccos(np.clip(cj, -1, 1))):.2f} deg")
    cjc = np.clip(cj, -1.0, 1.0)
    pc = S + L1 * cjc * bh
    rc_ = L1 * np.sqrt(max(0.0, 1 - cjc * cjc))
    print("p_c:", fmt(pc, 4), " r_c =", f"{rc_:.4f}")
    u = b["u"].get(USEG)
    print("remembered upper-arm direction u_hat:", None if u is None else fmt(u, 4),
          " frames since elbow measured k =", b["k"].get(EL))
    uperp = u - (u @ bh) * bh
    print("u_perp = u - (u.b_hat) b_hat:", fmt(uperp, 4), " |u_perp| =",
          f"{np.linalg.norm(uperp):.4f}", " u.b_hat =", f"{u @ bh:.4f}")
    E = pc + rc_ * uperp / np.linalg.norm(uperp)
    print("p_el (hand):", fmt(E, 4), " pipeline elbow:", fmt(a["pts"][EL], 4),
          " diff (mm):", f"{1000 * np.linalg.norm(E - a['pts'][EL]):.3f}")
    print("check |p_el - p_sh| =", f"{np.linalg.norm(E - S):.4f}",
          " |p_el - w| =", f"{np.linalg.norm(E - w_P):.4f}")
    # a basis n1, n2 and the turn angle s, for equation (5.11)
    n1_ = uperp / np.linalg.norm(uperp)
    n2_ = np.cross(bh, n1_)
    print("basis n1 (along u_perp):", fmt(n1_, 4), " n2 = b_hat x n1:", fmt(n2_, 4),
          " (s = 0 at the chosen point)")
    # angle between remembered direction and the placed upper arm
    ua = (E - S) / L1
    print("placed upper-arm direction:", fmt(ua, 4), " angle to memory:",
          f"{np.degrees(np.arccos(np.clip(ua @ u, -1, 1))):.2f} deg")
    # elbow flexion implied
    fl = np.degrees(np.arccos(np.clip(((E - S) @ (w_P - E)) / (L1 * L2), -1, 1)))
    print("angle between upper arm and forearm:", f"{fl:.2f} deg")
    # what the pipeline did
    print("\nobj-recovery counters this frame:",
          {k: a["obj_rec"].get(k, 0) - b["obj_rec"].get(k, 0)
           for k in ("right_wrist_obj", "right_elbow_ik")})
    print("tags (root, Rsw, Rtw, Rel, Lsw, Ltw, Lel):", a["tags"].tolist(),
          " live mask:", a["mask"])

    # ---- angles vs the stored csv ------------------------------------
    stored = pd.read_csv(paths.EVAL_OUT / f"recovery_{paths.ALIAS[stem]}"
                         / "angles_recovery.csv").iloc[f]
    cols = ["root_ex", "root_ey", "root_ez", "Rsh_y", "Rsh_z", "Rsh_tau",
            "Rel_y", "Rel_z", "Lsh_y", "Lsh_z", "Lsh_tau", "Lel_y", "Lel_z"]
    diff = np.abs(a["angles"] - stored[cols].to_numpy(float)).max()
    print(f"\nre-run angles vs stored angles_recovery.csv row {f}: max |diff| "
          f"= {diff:.4f} deg  (stored tags "
          f"{[int(stored[f'tag_{g}']) for g in range(7)]})")
    print("right arm angles (Rsh_y, Rsh_z, Rsh_tau, Rel_y, Rel_z):",
          fmt(a["angles"][3:8], 2))
    # the last measured elbow and wrist before the window
    lastm = None
    for g in range(f - 1, -1, -1):
        if not inp["fail"][SIDE][g]:
            lastm = g
            break
    print("last frame with the right arm measured:", lastm)
    if lastm is not None:
        rowm = ex["lm_df"].iloc[lastm]
        for nm in (SH, EL, WR):
            v = np.array([rowm[f"{nm}_x"], -rowm[f"{nm}_y"], rowm[f"{nm}_z"]])
            print(f"  {nm} at frame {lastm}: {fmt(v, 4)}")


if __name__ == "__main__":
    main()
