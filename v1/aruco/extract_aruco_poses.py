#!/usr/bin/env python3
# Filename: aruco/extract_aruco_poses.py
# Pipeline B, stage 1: bag playback -> ArUco detection -> per-marker pose CSV.
#
# Reads a RealSense .bag recording offline (as fast as possible, not real
# time), detects the scene's ArUco markers on every color frame, solves each
# marker's full 6-DOF pose in the camera frame with solvePnP(IPPE_SQUARE),
# and writes one CSV row per frame with translation (meters) + rotation
# matrix (row-major r11..r33) per marker. Conventions: ARUCO_MODEL.md.
#
# Scene (user-confirmed, matches the printed markers):
#   id 0 wall   150 mm  static
#   id 2 desk    50 mm  static (world anchor downstream)
#   id 1 object  50 mm  moving
#
# Rotations are matrices end to end; the OpenCV Rodrigues rvec is converted
# immediately and never exported. A marker missing from a frame writes empty
# cells (honest gap, same policy as Pipeline A). The aligned depth at the
# marker center (5x5 nonzero median) is exported as m{id}_depth_z purely as
# an independent cross-check of the PnP translation scale.
#
# Usage:
#   python extract_aruco_poses.py --bag ../Video/recording_20260328_021733.bag
#   python extract_aruco_poses.py --bag <file> --max-frames 60

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pyrealsense2 as rs

from frames import MARKERS, MARKER_IDS

ARUCO_DICT_NAME = "DICT_5X5_50"
ARUCO_DICT_ID = cv2.aruco.DICT_5X5_50


def open_bag(bag_path: Path):
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(str(bag_path), repeat_playback=False)
    profile = pipeline.start(config)
    profile.get_device().as_playback().set_real_time(False)
    intrinsics = (profile.get_stream(rs.stream.color)
                  .as_video_stream_profile().get_intrinsics())
    color_format = profile.get_stream(rs.stream.color).format()
    align = rs.align(rs.stream.color)
    return pipeline, align, intrinsics, color_format


def camera_matrices(intr):
    K = np.array([[intr.fx, 0.0, intr.ppx],
                  [0.0, intr.fy, intr.ppy],
                  [0.0, 0.0, 1.0]], dtype=np.float64)
    dist = np.array(list(intr.coeffs)[:5], dtype=np.float64)
    return K, dist


def square_object_points(size_m):
    """Corner order must match cv2.aruco detections (TL, TR, BR, BL in the
    marker's own frame: x right, y up, z out of the plane toward the viewer)
    — the exact layout SOLVEPNP_IPPE_SQUARE requires."""
    h = size_m / 2.0
    return np.array([[-h,  h, 0.0],
                     [ h,  h, 0.0],
                     [ h, -h, 0.0],
                     [-h, -h, 0.0]], dtype=np.float64)


# A planar square seen near fronto-parallel has TWO PnP solutions ("lobes"
# mirrored about the line of sight). Whether reprojection error can pick
# the true one depends on how DEGENERATE the pair is, measured by the
# angle between the two solutions (~2x the viewing tilt):
#   - lobes far apart  (desk 64 deg, object 62 deg): well-conditioned,
#     reprojection reliably prefers the true lobe (ratio 2.2-3.9);
#   - lobes close      (wall 23 deg, fronto-parallel at ~32 px): the ratio
#     is systematically BIASED — it "decisively" (up to 2.2x) prefers the
#     mirror lobe on 815/837 frames (checked against plumbness and the
#     unrefined-corner solve). No ratio threshold works here.
# So: below AMBIG_SEP_DEG of lobe separation, reprojection is ignored and
# the lobe is chosen by CONTINUITY with the previous frame, seeded once by
# plumbness against the tabletop-derived gravity (upright-mounting
# assumption for wall-hung markers; margin ~5 vs ~18 deg off plumb).
AMBIG_SEP_DEG = 40.0

AMBIG_CLEAR = 0        # single solution, or lobes far apart (reprojection)
AMBIG_GRAVITY = 1      # near-degenerate: continuity/gravity chose
AMBIG_NO_GRAVITY = 2   # near-degenerate and no reference yet -> took sol0

# NOTE a depth-plane normal fitted INSIDE the ambiguous marker's own quad
# was tried first and rejected: at 3 m on a ~32 px quad the fitted normal
# is >30 deg biased and consistently picked the WRONG lobe (checked against
# the tabletop-derived gravity below). Ambiguity only bites on small/far
# markers, exactly where local depth is useless.


def estimate_tabletop(depth_img, depth_scale, quads_px, intr, window=3):
    """Tabletop plane from depth: ONE plane fitted to depth samples in
    annuli around the given marker quads. The DESK marker rests on the
    desk by design, so its annulus is always valid; the object's annulus
    is only meaningful while the box rests on the desk (the caller gates
    it — a hand-held box sweeps the person instead). Samples > 5 cm from
    their own annulus' median depth are rejected (stand, box, hands,
    clutter). Returns (up unit vector against gravity, plane centroid,
    per-annulus centroids, n_samples) or None. The resulting up vector is
    only a SEED for lobe disambiguation (needs ~10 deg accuracy); the
    authoritative gravity is the wall marker's in-plane up axis
    (physically plumb), applied in calibrate_scene.py.
    """
    groups = []
    for quad in quads_px:
        q = np.asarray(quad, dtype=np.float64).reshape(4, 2)
        c = q.mean(axis=0)
        e = max(q.max(axis=0) - q.min(axis=0)) / 2.0
        samples = []
        for du in np.arange(-4.0 * e, 4.0 * e + 1, max(2.0, e / 4.0)):
            for dv in np.arange(-4.0 * e, 4.0 * e + 1, max(2.0, e / 4.0)):
                if max(abs(du), abs(dv)) < 2.2 * e:
                    continue  # exclude the card / the whole box around it
                u, v = int(round(c[0] + du)), int(round(c[1] + dv))
                if not (0 <= u < depth_img.shape[1] and 0 <= v < depth_img.shape[0]):
                    continue
                d = sample_depth(depth_img, depth_scale, u, v, window)
                if d > 0:
                    samples.append((float(u), float(v), d))
        if len(samples) < 30:
            continue
        med = np.median([s[2] for s in samples])
        local = [rs.rs2_deproject_pixel_to_point(intr, [u, v], d)
                 for u, v, d in samples if abs(d - med) < 0.05]
        if len(local) >= 30:
            groups.append(np.array(local))
    if len(groups) < len(quads_px):
        return None
    P = np.vstack(groups)

    def fit(P):
        C = P.mean(axis=0)
        n = np.linalg.svd(P - C)[2][2]
        return C, n

    # Robust refit: clutter a few cm off the desk (paper stacks, box top,
    # bowl rim) passes a median gate but not shrinking residual gates.
    C, nrm = fit(P)
    for gate in (0.015, 0.008):
        keep = np.abs((P - C) @ nrm) < gate
        if keep.sum() < 60:
            break
        P = P[keep]
        C, nrm = fit(P)
    up = nrm if nrm[1] < 0 else -nrm  # camera Y is down: up has negative y
    centroids = []
    for g in groups:
        keep = np.abs((g - C) @ nrm) < 0.02
        centroids.append(g[keep].mean(axis=0) if keep.sum() >= 10 else g.mean(axis=0))
    return up, C, centroids, len(P)


def estimate_tabletop_between(depth_img, depth_scale, quad_desk, quad_obj,
                              intr, window=3):
    """Tabletop plane from the desk surface BETWEEN the desk marker and the
    object marker: the image rectangle spanning both quads horizontally
    (plus one card width of margin each side), from the bottom of the
    object card down to the top of the desk card, so the cards themselves
    are excluded. Preferred over the annulus fit
    when both markers are detected. The annuli fail when the desk marker
    sits at the front edge of the desk (the annulus then reaches the desk
    edge, the stand and the floor: on the rail recording every annulus
    fit is 50-88 deg off vertical, this rectangle 4-5 deg). Same robust
    refit as estimate_tabletop. Returns (up unit vector, centroid,
    n_samples) or None when the region is too small or too sparse.
    """
    q1 = np.asarray(quad_obj, dtype=np.float64).reshape(4, 2)
    q2 = np.asarray(quad_desk, dtype=np.float64).reshape(4, 2)
    margin = float(q1[:, 0].max() - q1[:, 0].min())   # one object-card width
    umin = int(min(q1[:, 0].min(), q2[:, 0].min()) - margin)
    umax = int(max(q1[:, 0].max(), q2[:, 0].max()) + margin)
    vmin, vmax = int(q1[:, 1].max()), int(q2[:, 1].min())
    if vmax - vmin < 20 or umax - umin < 20:
        return None
    pts = []
    for v in range(max(0, vmin), min(depth_img.shape[0], vmax), 4):
        for u in range(max(0, umin), min(depth_img.shape[1], umax), 4):
            d = sample_depth(depth_img, depth_scale, u, v, window)
            if d > 0:
                pts.append(rs.rs2_deproject_pixel_to_point(intr, [u, v], d))
    if len(pts) < 100:
        return None
    P = np.array(pts)

    def fit(P):
        C = P.mean(axis=0)
        return C, np.linalg.svd(P - C)[2][2]

    C, nrm = fit(P)
    for gate in (0.015, 0.008):
        keep = np.abs((P - C) @ nrm) < gate
        if keep.sum() < 60:
            break
        P = P[keep]
        C, nrm = fit(P)
    up = nrm if nrm[1] < 0 else -nrm
    return up, C, len(P)


def rot_angle_deg(Ra, Rb):
    return float(np.degrees(np.arccos(np.clip(
        0.5 * (np.trace(Ra.T @ Rb) - 1.0), -1.0, 1.0))))


class LobeTracker:
    """Per-marker lobe disambiguation state (policy in the header above).

    Keeps an outlier-gated reference rotation: the chosen solution only
    updates the reference when it is within GATE_DEG of it, so a single
    corrupted detection (person clipping the marker) cannot poison the
    reference and lock the wrong lobe for the following frames — exactly
    the failure observed when 3 wild wall frames took the reprojection
    path. Genuine large motion re-acquires: immediately when the lobes
    are well separated (reprojection trustworthy), after REACQUIRE_AFTER
    consecutive far-from-reference frames otherwise.
    """
    GATE_DEG = 30.0
    REACQUIRE_AFTER = 5

    def __init__(self):
        self.ref = None
        self.miss = 0

    def choose(self, Rs, sep, gravity_up):
        """Returns (index, ambig code) among candidate rotations Rs."""
        if len(Rs) == 1:
            if rot_angle_deg(self.ref, Rs[0]) < self.GATE_DEG if self.ref is not None else True:
                self.ref, self.miss = Rs[0], 0
            return 0, AMBIG_CLEAR
        near_degenerate = sep < AMBIG_SEP_DEG
        if self.ref is not None:
            d = [rot_angle_deg(self.ref, R) for R in Rs]
            k = int(np.argmin(d))
            if d[k] < self.GATE_DEG:
                self.ref, self.miss = Rs[k], 0
                return k, AMBIG_GRAVITY if near_degenerate else AMBIG_CLEAR
            if not near_degenerate:  # trustworthy re-acquisition via reprojection
                self.ref, self.miss = Rs[0], 0
                return 0, AMBIG_CLEAR
            self.miss += 1  # wild near-degenerate frame: keep the reference
            if self.miss >= self.REACQUIRE_AFTER:
                self.ref, self.miss = Rs[k], 0
            return k, AMBIG_GRAVITY
        if not near_degenerate:
            self.ref = Rs[0]
            return 0, AMBIG_CLEAR
        if gravity_up is not None:
            k = int(np.argmax([np.dot(R[:, 1], gravity_up) for R in Rs]))
            self.ref = Rs[k]
            return k, AMBIG_GRAVITY
        return 0, AMBIG_NO_GRAVITY  # no reference of any kind yet


def solve_marker_pose(corners_px, size_m, K, dist, gravity_up, tracker):
    """Full 6-DOF pose of one marker in the camera frame.

    Returns (R 3x3, t meters, mean corner reprojection error px, ambig code)
    or None. Lobe choice per the AMBIG_SEP_DEG policy above, with the
    tracker holding the outlier-gated continuity reference.
    """
    obj = square_object_points(size_m)
    img = np.asarray(corners_px, dtype=np.float64).reshape(4, 2)
    nsol, rvecs, tvecs, errs = cv2.solvePnPGeneric(
        obj, img, K, dist, flags=cv2.SOLVEPNP_IPPE_SQUARE)
    if nsol == 0:
        return None
    Rs = [cv2.Rodrigues(r)[0] for r in rvecs[:nsol]]  # matrices from here on
    sep = rot_angle_deg(Rs[0], Rs[1]) if nsol > 1 else 180.0
    k, ambig = tracker.choose(Rs, sep, gravity_up)
    proj, _ = cv2.projectPoints(obj, rvecs[k], tvecs[k], K, dist)
    reproj = float(np.mean(np.linalg.norm(proj.reshape(4, 2) - img, axis=1)))
    return Rs[k], tvecs[k].reshape(3), reproj, ambig


def sample_depth(depth_img, depth_scale, u, v, window):
    """Median of the nonzero depth returns in a window x window neighborhood
    around (u, v), in meters. 0.0 when every pixel is a zero return."""
    r = window // 2
    patch = depth_img[max(0, v - r):v + r + 1, max(0, u - r):u + r + 1]
    nz = patch[patch > 0]
    if nz.size == 0:
        return 0.0
    return float(np.median(nz)) * depth_scale


def intrinsics_to_dict(intr):
    return {"width": intr.width, "height": intr.height,
            "fx": intr.fx, "fy": intr.fy, "ppx": intr.ppx, "ppy": intr.ppy,
            "model": str(intr.model), "coeffs": list(intr.coeffs)}


def main():
    script_dir = Path(__file__).resolve().parent
    ap = argparse.ArgumentParser(description="Extract ArUco marker poses from a RealSense .bag to CSV.")
    ap.add_argument("--bag", required=True, help="Path to the .bag recording")
    ap.add_argument("--out", default=None,
                    help="Output CSV path (default: output/<bag-stem>_aruco_raw.csv)")
    ap.add_argument("--max-frames", type=int, default=None,
                    help="Stop after N frames (for smoke tests)")
    ap.add_argument("--depth-window", type=int, default=5,
                    help="Depth cross-check sampled as median of nonzero returns "
                         "in an NxN window at the marker center (default: 5)")
    args = ap.parse_args()
    if args.depth_window < 1 or args.depth_window % 2 == 0:
        sys.exit(f"[ERROR] --depth-window must be odd and >= 1, got {args.depth_window}")

    bag_path = Path(args.bag).resolve()
    if not bag_path.exists():
        sys.exit(f"[ERROR] Bag file not found: {bag_path}")
    out_csv = Path(args.out) if args.out else script_dir / "output" / f"{bag_path.stem}_aruco_raw.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out_meta = out_csv.with_suffix(".meta.json")

    det_params = cv2.aruco.DetectorParameters()
    # Subpixel corners via the AprilTag refiner: measured desk-marker pose
    # scatter drops from integer-pixel-locked 0.00 (false stability) to a
    # true 0.4 mm / 0.17 deg, wall position scatter 37 -> 7 mm.
    det_params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_APRILTAG
    detector = cv2.aruco.ArucoDetector(
        cv2.aruco.getPredefinedDictionary(ARUCO_DICT_ID), det_params)

    pipeline, align, intrinsics, color_format = open_bag(bag_path)
    K, dist = camera_matrices(intrinsics)
    print(f"[INFO] Bag opened: {bag_path.name} "
          f"({intrinsics.width}x{intrinsics.height}, color format {color_format})")
    print(f"[INFO] Dictionary {ARUCO_DICT_NAME}, markers: "
          + ", ".join(f"id{i}={MARKERS[i][0]} {MARKERS[i][1]*1000:.0f}mm"
                      for i in MARKER_IDS))

    header = ["frame", "time_s"]
    for mid in MARKER_IDS:
        p = f"m{mid}"
        header += [f"{p}_detected", f"{p}_tx", f"{p}_ty", f"{p}_tz"]
        header += [f"{p}_r{i}{j}" for i in (1, 2, 3) for j in (1, 2, 3)]
        header += [f"{p}_reproj_px", f"{p}_ambig", f"{p}_u", f"{p}_v", f"{p}_depth_z"]

    frame_count = 0
    det_counts = {mid: 0 for mid in MARKER_IDS}
    ambig_counts = {mid: {AMBIG_GRAVITY: 0, AMBIG_NO_GRAVITY: 0} for mid in MARKER_IDS}
    # Scene gravity seed from the tabletop around the desk marker:
    # accumulated over the first 10 desk detections, then frozen. The
    # object annulus joins only when its plane agrees with the desk-only
    # fit (i.e. the box actually rests on the desk, not in a hand).
    grav_samples, grav_pts_desk, grav_pts_obj = [], [], []
    seed_source = "desk-marker annulus"
    gravity_up = None
    tabletop_point_desk = None
    tabletop_point_obj = None
    trackers = {mid: LobeTracker() for mid in MARKER_IDS}
    first_ts_ms = None
    t_start = time.time()

    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        while args.max_frames is None or frame_count < args.max_frames:
            try:
                frames = pipeline.wait_for_frames(timeout_ms=5000)
            except RuntimeError:
                break  # end of bag
            aligned = align.process(frames)
            color_frame = aligned.get_color_frame()
            depth_frame = aligned.get_depth_frame()
            if not color_frame or not depth_frame:
                continue

            ts_ms = frames.get_timestamp()
            if first_ts_ms is None:
                first_ts_ms = ts_ms
            rel_s = (ts_ms - first_ts_ms) / 1000.0

            color = np.asanyarray(color_frame.get_data())
            gray = cv2.cvtColor(color, cv2.COLOR_RGB2GRAY
                                if color_format == rs.format.rgb8
                                else cv2.COLOR_BGR2GRAY)
            corners_list, ids, _ = detector.detectMarkers(gray)
            found = {}
            if ids is not None:
                for c, mid in zip(corners_list, ids.flatten()):
                    if int(mid) in MARKERS:
                        found[int(mid)] = c

            depth_img = np.asanyarray(depth_frame.get_data())
            depth_scale = depth_frame.get_units()

            if len(grav_samples) < 10 and 2 in found:
                est = estimate_tabletop(depth_img, depth_scale, [found[2]],
                                        intrinsics, args.depth_window)
                if est is not None:
                    up_sample = est[0]
                    grav_pts_desk.append(est[2][0])
                    between = None
                    if 1 in found:
                        between = estimate_tabletop_between(
                            depth_img, depth_scale, found[2], found[1],
                            intrinsics, args.depth_window)
                    if between is not None:
                        # the desk surface between the two cards: the
                        # preferred seed (see estimate_tabletop_between)
                        up_sample = between[0]
                        seed_source = "between-markers plane"
                    elif 1 in found:
                        est2 = estimate_tabletop(depth_img, depth_scale,
                                                 [found[2], found[1]],
                                                 intrinsics, args.depth_window)
                        if est2 is not None and float(np.degrees(np.arccos(
                                np.clip(np.dot(est[0], est2[0]), -1, 1)))) < 15.0:
                            # box rests on the desk: the two-annuli fit has a
                            # much longer baseline -> better seed normal
                            up_sample = est2[0]
                            grav_pts_obj.append(est2[2][1])
                    grav_samples.append(up_sample)
                    up = np.mean(grav_samples, axis=0)
                    gravity_up = up / np.linalg.norm(up)
                    tabletop_point_desk = np.mean(grav_pts_desk, axis=0)
                    if grav_pts_obj:
                        tabletop_point_obj = np.mean(grav_pts_obj, axis=0)

            row = [frame_count, f"{rel_s:.6f}"]
            for mid in MARKER_IDS:
                if mid in found:
                    pose = solve_marker_pose(found[mid], MARKERS[mid][1], K, dist,
                                             gravity_up, trackers[mid])
                else:
                    pose = None
                if pose is None:
                    row += [0] + [""] * 17
                    continue
                R, t, reproj, ambig = pose
                det_counts[mid] += 1
                if ambig:
                    ambig_counts[mid][ambig] += 1
                u, v = np.asarray(found[mid]).reshape(4, 2).mean(axis=0)
                u, v = int(round(u)), int(round(v))
                dz = sample_depth(depth_img, depth_scale, u, v, args.depth_window)
                row += [1]
                row += [f"{x:.6f}" for x in t]
                row += [f"{x:.9f}" for x in R.flatten()]
                row += [f"{reproj:.4f}", ambig, u, v, f"{dz:.6f}"]
            writer.writerow(row)

            frame_count += 1
            if frame_count % 100 == 0:
                print(f"[>] {frame_count} frames "
                      f"({frame_count / (time.time() - t_start):.1f} fps)")

    pipeline.stop()

    meta = {
        "source_bag": str(bag_path),
        "output_csv": str(out_csv),
        "aruco_dict": ARUCO_DICT_NAME,
        "markers": {str(mid): {"role": MARKERS[mid][0],
                               "size_m": MARKERS[mid][1]} for mid in MARKER_IDS},
        "pose_method": "solvePnPGeneric IPPE_SQUARE on the 4 corners (full "
                       "6-DOF); two-lobe ambiguity by lobe separation: "
                       f"lobes >= {AMBIG_SEP_DEG} deg apart trust "
                       "reprojection (sol0), near-degenerate lobes use "
                       "outlier-gated continuity seeded by plumbness "
                       "against the tabletop-derived gravity",
        "corner_refinement": "CORNER_REFINE_APRILTAG",
        "depth_window": args.depth_window,
        "frames_total": frame_count,
        "detections": {str(mid): det_counts[mid] for mid in MARKER_IDS},
        "ambiguous_resolved": {
            str(mid): {"by_gravity": ambig_counts[mid][AMBIG_GRAVITY],
                       "no_gravity_took_sol0": ambig_counts[mid][AMBIG_NO_GRAVITY]}
            for mid in MARKER_IDS},
        "ambig_legend": {"0": "clear", "1": "gravity tiebreak", "2": "ambiguous, no gravity, sol0"},
        "tabletop": None if gravity_up is None else {
            "up_cam": [float(x) for x in gravity_up],
            "point_desk_cam": [float(x) for x in tabletop_point_desk],
            "point_obj_cam": None if tabletop_point_obj is None
                             else [float(x) for x in tabletop_point_obj],
            "frames_averaged": len(grav_samples),
            "obj_frames_averaged": len(grav_pts_obj),
            "seed_source": seed_source,
            "note": "up_cam: SEED gravity from the plane fitted to the "
                    "desk-marker depth annulus (authoritative gravity = "
                    "wall marker in-plane up, calibrate_scene.py). "
                    "point_desk_cam: tabletop point at the desk marker. "
                    "point_obj_cam: tabletop point AT THE OBJECT (cube "
                    "height reference), only when the object annulus "
                    "agreed with the desk plane (box resting, not held); "
                    "camera frame",
        },
        "color_intrinsics": intrinsics_to_dict(intrinsics),
        "coordinate_frame": "camera (color): X right, Y down, Z forward, meters; "
                            "R,t map marker-frame points into the camera frame",
        "export_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        "elapsed_s": round(time.time() - t_start, 1),
    }
    with open(out_meta, "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\n[+] Done: {frame_count} frames ({time.time() - t_start:.1f}s)")
    if gravity_up is not None:
        print(f"[+] tabletop gravity (camera frame): {np.round(gravity_up, 4).tolist()} "
              f"from {len(grav_samples)} frames")
    for mid in MARKER_IDS:
        a = ambig_counts[mid]
        print(f"[+] id{mid} ({MARKERS[mid][0]}): {det_counts[mid]}/{frame_count} detections"
              f" (ambiguous: {a[AMBIG_GRAVITY]} gravity-resolved, {a[AMBIG_NO_GRAVITY]} sol0)")
    print(f"[+] CSV:  {out_csv}")
    print(f"[+] Meta: {out_meta}")


if __name__ == "__main__":
    main()
