#!/usr/bin/env python3
# Filename: integration/analyze_object_offset.py
"""Why doesn't the object sit exactly in the rig's hand? (OBJECT_OFFSET.md)

Whole-video (all 899 frames) analysis of the offset between Pipeline B's
tracked object and (a) Pipeline A's wrist landmark, (b) the Unity rig's
hand bone, on recording_20260224_083945 (person carries the 70 mm cube).

Answers, with numbers:
  1. Is the offset constant? — In the WORLD frame the offset vector rotates
     with the hand/box, so no; its MAGNITUDE is nearly constant; expressed
     in the OBJECT'S OWN frame it is a tight, constant vector (the rigid
     grip geometry).
  2. Decoupling: subtract the mean object-frame offset -> the residual is
     the trajectory accuracy of the whole system (both pipelines through
     the calibrated anchor).
  3. The rig-hand offset additionally contains the rig's proportion error
     (FBX bone lengths vs the measured person) — quantified separately.

Everything is computed in the LEVELED desk world (gravity = +y), the same
frame the Unity receiver renders. Plot first, then read the printed stats.

Outputs:
  output/object_offset_analysis.png
  stdout: all summary statistics quoted in OBJECT_OFFSET.md

Usage:
  python analyze_object_offset.py [--stem recording_20260224_083945]
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent

P = np.array([[1, 0, 0], [0, 0, 1], [0, 1, 0]], float)
D = np.diag([1.0, -1.0, 1.0])
DESK_THICK, LEG_H = 0.03, 0.69          # ArucoSceneReceiver constants


def recompose_zxy(deg):
    """Unity ZXY-applied Euler degrees -> R = Ry·Rx·Rz (KINEMATIC_MODEL.md §4)."""
    x, y, z = np.radians(np.asarray(deg, dtype=float))
    cx, sx, cy, sy, cz, sz = np.cos(x), np.sin(x), np.cos(y), np.sin(y), np.cos(z), np.sin(z)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


def from_to_rotation(a, b):
    v, c = np.cross(a, b), float(np.dot(a, b))
    s = np.linalg.norm(v)
    if s < 1e-12:
        return np.eye(3) if c > 0 else -np.eye(3)
    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]]) / s
    return np.eye(3) + s * K + (1 - c) * (K @ K)


def stats(v, name, unit="cm", f=100.0):
    v = np.asarray(v, float)
    v = v[np.isfinite(v)]
    print(f"  {name:44s} median {np.median(v)*f:6.1f} {unit}, "
          f"mean {v.mean()*f:6.1f}, p95 {np.percentile(v, 95)*f:6.1f}, "
          f"max {v.max()*f:6.1f}")
    return np.median(v), np.percentile(v, 95)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stem", default="recording_20260224_083945")
    args = ap.parse_args()

    calib = json.loads((HERE.parent / "aruco" / "output" / "scene_calibration.json").read_text())
    stream = pd.read_csv(HERE / "output" / "integrated_stream.csv")
    lm = pd.read_csv(HERE.parent / "mediapipe" / "output"
                     / f"{args.stem}_landmarks_filtered_v2.csv")
    ofil = pd.read_csv(HERE.parent / "aruco" / "output"
                       / f"{args.stem}_object_world_filtered.csv")
    oraw = pd.read_csv(HERE.parent / "aruco" / "output"
                       / f"{args.stem}_object_world.csv")
    plog = pd.read_csv(HERE / "output" / "unity_person_log.csv") \
        .drop_duplicates("frame", keep="last").set_index("frame") \
        .reindex(stream.frame.values)

    n = len(stream)
    t = stream.time_s.values
    T_dc = np.linalg.inv(np.array(calib["T_cam_desk"]))
    R_dc, t_dc = T_dc[:3, :3], T_dc[:3, 3]
    M = P @ R_dc @ D                     # person space -> ArucoWorld-local
    cam_pos = P @ t_dc
    g = np.array(calib["scene_geometry"]["gravity_up_unity"])
    g /= np.linalg.norm(g)
    G = from_to_rotation(g, np.array([0.0, 1.0, 0.0]))   # level the world
    drop = calib["scene_geometry"]["origin_above_tabletop_m"]
    cube = calib["scene_geometry"]["object_cube_size_m"]

    lev = lambda p: (G @ np.atleast_2d(p).T).T             # local -> leveled

    # --- tracks in the leveled desk world -----------------------------------
    obj = lev(stream[["opx", "opy", "opz"]].values)         # MARKER center
    R_obj = np.array([G @ recompose_zxy(e)
                      for e in stream[["oex", "oey", "oez"]].values])
    # cube geometric center: marker centered on a face, body half an edge
    # along -normal (receiver draws it at local -up * cube/2)
    cube_c = obj + R_obj @ np.array([0.0, -cube / 2.0, 0.0])
    det = stream.obj_live.values == 1                       # marker measured

    wr = {}
    for side in ("left", "right"):
        w = lm[[f"{side}_wrist_x", f"{side}_wrist_y", f"{side}_wrist_z"]].values
        wr[side] = lev((M @ (w * [1, -1, 1]).T).T + cam_pos)
    wrist_flag = {s: lm[f"{s}_wrist_flag"].values for s in ("left", "right")}

    # rig hands: Unity world -> leveled (subtract the receiver's floor drop,
    # recomputed from first principles exactly like validate_integration.py)
    on_plane = -g * drop
    proj = lambda q: q - g * float(np.dot(q - on_plane, g))
    obj0_local = stream[["opx", "opy", "opz"]].values[0]
    center = (proj(np.zeros(3)) + proj(obj0_local)) / 2.0
    floor_pt = center - g * (DESK_THICK + LEG_H)
    world_pos = np.array([0.0, -(G @ floor_pt)[1], 0.0])
    hand = {"right": plog[["rh_x", "rh_y", "rh_z"]].values - world_pos,
            "left": plog[["lh_x", "lh_y", "lh_z"]].values - world_pos}

    # --- 1. which hand holds the box ----------------------------------------
    print("=== 1. holding hand (whole video, 899 frames) ===")
    dists = np.stack([np.linalg.norm(obj - wr[s], axis=1)
                      for s in ("left", "right")])
    with np.errstate(invalid="ignore"):
        dnear = np.nanmin(dists, axis=0)
        nearer = np.nanargmin(np.where(np.isfinite(dists), dists, np.inf), axis=0)
    frac_r = float((nearer == 1).mean())
    print(f"  nearest wrist: right on {frac_r*100:.0f}% of frames, "
          f"left on {(1-frac_r)*100:.0f}% (both hands cup the box in the "
          f"recording; the nearer one stands in as the grip reference)")
    wrist_near = np.where((nearer == 1)[:, None], wr["right"], wr["left"])
    hand_near = np.where((nearer == 1)[:, None], hand["right"], hand["left"])

    # --- 2. the offset in the WORLD frame ------------------------------------
    print("\n=== 2. offset in the world frame (object MARKER - nearest wrist) ===")
    d_w = obj - wrist_near
    stats(dnear, "|marker - wrist| distance")
    stats(np.linalg.norm(cube_c - wrist_near, axis=1), "|cube center - wrist| distance")
    print("  per-axis mean ± std (cm):",
          "  ".join(f"{ax}: {m*100:+.1f} ± {s*100:.1f}"
                    for ax, m, s in zip("xyz", np.nanmean(d_w, 0), np.nanstd(d_w, 0))))
    ang = np.degrees(np.arctan2(d_w[:, 0], d_w[:, 2]))
    ok = np.isfinite(ang)
    print(f"  offset direction (azimuth) swings {np.nanpercentile(ang[ok], 2.5):+.0f}"
          f" .. {np.nanpercentile(ang[ok], 97.5):+.0f} deg over the video")
    print("  -> NOT a constant world-frame vector: length ~constant, direction rotates")

    # The offset relationship only EXISTS while the box is in the hand.
    # The person parks it on the desk mid-video (t ~13.5-23 s) and the hands
    # leave — no grip to model there. Resting is unambiguous in the object's
    # own height: on the desk the marker center sits half a cube edge
    # (3.5 cm) above the tabletop; carried, it rides 15-25 cm above it.
    K = 7
    disp = np.linalg.norm(obj[K:] - obj[:-K], axis=1)
    moving = np.zeros(n, bool)
    moving[K // 2:K // 2 + len(disp)] = disp > 0.03
    h_table = obj[:, 1] + drop              # leveled height above tabletop
    carried = (h_table > 0.06) | moving
    print(f"\n  [carried vs resting] carried on {int(carried.sum())}/{n} frames "
          f"(marker > 6 cm above the tabletop or in motion); while resting "
          f"the nearest-wrist distance runs up to "
          f"{np.nanmax(dnear[~carried])*100:.0f} cm (hand simply leaves the box)")

    # --- 3. the offset in the OBJECT's frame (decoupled) ---------------------
    # The person carries the box sometimes in the left hand, sometimes the
    # right (nearest wrist switches at t ~6.5-8.5 s). Each hand has its OWN
    # rigid grip geometry, so the constant vector is fitted PER HOLDING
    # HAND: frames where that hand is the nearest one, box carried, marker
    # measured, wrist raw.
    print("\n=== 3. offset in the object's own frame: d = R_objT (wrist - marker) ===")
    print("  (per holding hand, carried frames only — a grip vector is "
          "meaningless while the box rests on the desk)")
    d_loc = {s: np.einsum("nij,ni->nj", R_obj, wr[s] - obj)
             for s in ("left", "right")}
    hold = {}
    mus = {}
    for si, side in enumerate(("left", "right")):
        hold[side] = det & carried & (nearer == si) \
            & (wrist_flag[side] == 0) & np.isfinite(d_loc[side]).all(axis=1)
        mu = d_loc[side][hold[side]].mean(axis=0)
        sd = d_loc[side][hold[side]].std(axis=0)
        mus[side] = mu
        print(f"  {side}-holding ({int(hold[side].sum()):3d} frames): "
              f"mean [x, normal, z] = ({mu[0]*100:+5.1f}, {mu[1]*100:+5.1f}, "
              f"{mu[2]*100:+5.1f}) cm, std = ({sd[0]*100:.1f}, {sd[1]*100:.1f}, "
              f"{sd[2]*100:.1f}) cm")
    print(f"  -> along the marker normal both hands sit ~9-11 cm behind the "
          f"marker: the cube face->center is {cube/2*100:.1f} cm of that, the "
          f"rest is the far half of the box + palm to the wrist joint")
    print("  -> tight std per hand = each grip is rigid; the world-frame "
          "swing was just this fixed vector rotating with the box")

    # --- 4. decouple & residual = system trajectory accuracy -----------------
    print("\n=== 4. residual after decoupling the constant grip vector(s) ===")
    resid = np.full(n, np.nan)
    for side in ("left", "right"):
        pred = obj + np.einsum("nij,j->ni", R_obj, mus[side])
        r_side = np.linalg.norm(pred - wr[side], axis=1)
        resid[hold[side]] = r_side[hold[side]]
        stats(r_side[hold[side]], f"residual, {side}-holding frames")
    acc = np.isfinite(resid)
    stats(resid[acc], "residual, all carried frames")
    rms = float(np.sqrt(np.nanmean(resid[acc] ** 2)))
    print(f"  RMS {rms*100:.1f} cm over {int(acc.sum())} carried frames — the "
          f"two-pipeline agreement through the anchor; the right-holding "
          f"stretch (wrist fully visible to the sensor) shows the floor "
          f"(~1 cm), the left-holding stretch adds MediaPipe wrist noise "
          f"(that wrist is half-occluded by the carried box)")
    print("  (while the box rests on the desk there is no grip relationship "
          "to measure: the hands leave, |marker-wrist| runs to "
          f"{np.nanmax(dnear[~carried])*100:.0f} cm)")
    # velocity agreement
    v_obj = obj[K:] - obj[:-K]
    v_wr = wrist_near[K:] - wrist_near[:-K]
    mv = moving[K // 2:K // 2 + len(v_obj)] \
        & np.isfinite(v_wr).all(axis=1) & np.isfinite(v_obj).all(axis=1)
    r_mov = float(np.corrcoef(v_obj[mv].ravel(), v_wr[mv].ravel())[0, 1])
    m = np.isfinite(v_wr).all(axis=1) & np.isfinite(v_obj).all(axis=1)
    r_all = float(np.corrcoef(v_obj[m].ravel(), v_wr[m].ravel())[0, 1])
    print(f"  velocity Pearson r: {r_mov:.3f} while carried "
          f"({r_all:.3f} over the whole video — diluted by the resting "
          f"stretch where both tracks are just noise around zero velocity)")

    # --- 5. the rig's hand: grip offset + proportion error -------------------
    print("\n=== 5. rig hand (Unity FK) vs object and vs the wrist landmark ===")
    d_hand = np.linalg.norm(obj - hand_near, axis=1)
    stats(d_hand, "|marker - rig hand| distance")
    d_hw = {s: np.linalg.norm(hand[s] - wr[s], axis=1) for s in ("left", "right")}
    stats(d_hw["right"], "rig R hand vs R wrist landmark")
    stats(d_hw["left"], "rig L hand vs L wrist landmark")
    print("  -> the rig-hand error is dominated by the FBX proportions "
          "(see rig_dimensions.csv vs the person)")

    # --- figure ---------------------------------------------------------------
    fig, axes = plt.subplots(5, 1, figsize=(13, 15), sharex=True,
                             constrained_layout=True)
    ax = axes[0]
    ax.plot(t, dnear * 100, color="#3b6fb6", lw=1.2, label="|marker − nearest wrist|")
    ax.plot(t, np.linalg.norm(cube_c - wrist_near, axis=1) * 100, color="#7aa6d9",
            lw=1.0, label="|cube center − wrist|")
    ax.plot(t, d_hand * 100, color="#c25a1e", lw=1.2, label="|marker − rig hand|")
    ax.fill_between(t, 0, 1, where=~carried, transform=ax.get_xaxis_transform(),
                    color="0.92", label="box resting on the desk")
    ax.set_ylabel("distance (cm)")
    ax.legend(loc="upper left", fontsize=8, frameon=False, ncol=2)
    ax.set_title("object-to-hand distance, whole video", fontsize=10)

    ax = axes[1]
    for c, (ax_name, col) in enumerate(zip(("x (right)", "y (up)", "z (fwd)"),
                                           ("#3b6fb6", "#c25a1e", "#4a9070"))):
        ax.plot(t, d_w[:, c] * 100, color=col, lw=1.0, label=ax_name)
    ax.set_ylabel("offset (cm)")
    ax.legend(loc="upper left", fontsize=8, frameon=False, ncol=3)
    ax.set_title("offset components in the WORLD frame — they swing as the box "
                 "is carried and turned (not a constant vector)", fontsize=10)

    for axi, side in ((2, "left"), (3, "right")):
        ax = axes[axi]
        for c, (ax_name, col) in enumerate(zip(("marker x", "marker normal",
                                                "marker z"),
                                               ("#3b6fb6", "#c25a1e", "#4a9070"))):
            y = np.where(hold[side], d_loc[side][:, c], np.nan)
            ax.plot(t, y * 100, color=col, lw=1.0, label=ax_name)
            ax.axhline(mus[side][c] * 100, color=col, lw=0.6, ls="--")
        ax.set_ylabel("offset (cm)")
        if axi == 2:
            ax.legend(loc="upper left", fontsize=8, frameon=False, ncol=3)
        ax.set_title(f"the SAME offset in the OBJECT's own frame, {side}-holding "
                     "frames — flat = constant rigid grip vector (dashed: mean)",
                     fontsize=10)

    ax = axes[4]
    y = np.where(acc, resid, np.nan)
    ax.plot(t, y * 100, color="#3b6fb6", lw=1.0, label="residual after decoupling")
    ax.axhline(np.median(resid[acc]) * 100, color="k", lw=0.6, ls="--",
               label=f"median {np.median(resid[acc])*100:.1f} cm")
    ax.set_ylabel("residual (cm)")
    ax.set_xlabel("time (s)")
    ax.legend(loc="upper left", fontsize=8, frameon=False)
    ax.set_title("wrist predicted from the object pose + that hand's constant "
                 "grip vector: what remains is the two-pipeline trajectory "
                 "accuracy", fontsize=10)

    for ax in axes:
        ax.grid(True, color="0.92", lw=0.5)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.suptitle(f"{args.stem}: object vs hand — offset decoupling", fontsize=12)
    out = HERE / "output" / "object_offset_analysis.png"
    fig.savefig(out, dpi=110)
    print(f"\n[+] {out}")

    # --- 6. rig proportions vs person vs scene -------------------------------
    print("\n=== 6. rig proportions vs the measured person ===")
    rig = pd.read_csv(HERE / "output" / "rig_dimensions.csv") \
        .set_index("segment")["meters"]

    def seg(a, b):
        pa = lm[[f"{a}_x", f"{a}_y", f"{a}_z"]].values
        pb = lm[[f"{b}_x", f"{b}_y", f"{b}_z"]].values
        return float(np.nanmedian(np.linalg.norm(pa - pb, axis=1)))

    mid = lambda a, b: (lm[[f"{a}_x", f"{a}_y", f"{a}_z"]].values
                        + lm[[f"{b}_x", f"{b}_y", f"{b}_z"]].values) / 2
    torso = float(np.nanmedian(np.linalg.norm(
        mid("left_shoulder", "right_shoulder") - mid("left_hip", "right_hip"), axis=1)))
    person = {
        "shoulder_width": seg("left_shoulder", "right_shoulder"),
        "upper_arm_R": seg("right_shoulder", "right_elbow"),
        "upper_arm_L": seg("left_shoulder", "left_elbow"),
        "forearm_R": seg("right_elbow", "right_wrist"),
        "forearm_L": seg("left_elbow", "left_wrist"),
        "torso_hip_to_midshoulder": torso,
    }
    print(f"  {'segment':26s} {'rig (m)':>8s} {'person (m)':>10s} {'ratio':>6s}")
    ratios = []
    for k, pv in person.items():
        rv = float(rig[k])
        ratios.append(rv / pv)
        print(f"  {k:26s} {rv:8.3f} {pv:10.3f} {rv/pv:6.2f}")
    print(f"  rig rest hip height: {float(rig['hip_height_rest']):.3f} m "
          f"(scene desk top is at {DESK_THICK + LEG_H:.2f} m)")
    if "applied_scale" in rig.index:
        print(f"  (FBX authored {float(rig['rig_rest_height_raw']):.2f} m tall; "
              f"display-scaled x{float(rig['applied_scale']):.3f} at spawn to a "
              f"1.70 m person — dims above are post-scale)")
    print(f"  -> mean remaining ratio {np.mean(ratios):.2f}x: overall scale is "
          f"handled at spawn; what remains is the rig's NON-uniform "
          f"proportions (forearm ratio {float(rig['forearm_R'])/person['forearm_R']:.2f}x) "
          f"— only per-bone retargeting could remove it")
    arm_r = (rig["upper_arm_R"] + rig["forearm_R"]) \
        - (person["upper_arm_R"] + person["forearm_R"])
    print(f"  arm-length surplus (R, shoulder->wrist): {arm_r*100:+.1f} cm — the "
          f"scale of the rig-hand-vs-object gap when the arm points at the box")


if __name__ == "__main__":
    main()
