#!/usr/bin/env python3
"""Thesis figure: the plain MediaPipe solve against the object-conditioned
recovery on manually labelled failure frames.

For every requested frame and every side labelled on it two panels are
drawn side by side on copies of the tracked colour frame
(eval/labels/frames_<alias>/fNNNNN.png, 640x480):

  left   "MediaPipe (plain solve)": the shoulder-elbow-wrist chain that
         the angles of angles_plain.csv place (forward kinematics, the
         tracker's rig), plus MediaPipe's raw wrist of that frame as a
         hollow circle where MediaPipe returned one
  right  "Object-conditioned recovery": the same chain from
         angles_recovery.csv, plus the object-derived wrist estimate
         (recovery_core.build_inputs, w_hat_solver) as a cross

Both panels carry the manual label (filled square with a thin outline)
and a bottom line with the frame number and the distance in cm from the
label to the wrist shown in that panel. The distances are recomputed
here in the solver space exactly as eval_labeled_recovery.py computes
plain_fk_cm, recovery_fk_cm and recovered_cm, and are printed next to
the values of eval/reports/<alias>_recovery_labeled.json when that
report exists.

Geometry: landmarks and labels live in the RealSense colour camera frame
(metres); the solver space is that frame with y flipped
(root_frame.unity_from_sensor). Solver-space points are flipped back and
projected with the colour intrinsics of meta.json (pinhole, no
distortion): u = fx x / z + ppx, v = fy y / z + ppy.

Needs the angle CSVs of eval/output/recovery_<alias>/ (run_recovery.py)
and the pipeline inputs, so it runs on the machine that holds them. The
frame is upscaled 2x (cubic) before anything is drawn so lines and text
stay crisp at 200 dpi; --crop X0 Y0 X1 Y1 (original pixels) zooms on a
region, e.g. the arm.

Presentation options (defaults reproduce the thesis figures unchanged):
--fade F blends the photograph toward black by F (0 = unchanged,
1 = black) before any overlay is drawn, so the chain, label, circle and
cross keep full strength; --titles PLAIN RECOVERY replaces the two
panel titles; --bottom FMT replaces the bottom line (str.format with
frame, side and d, the distance in cm); --strip-ink dark draws the
title and bottom strips as white text on black instead of black on
white.

Run: python eval/failure/make_label_compare_fig.py --stem STEM
         --frames 560 620 [--labels FILE] [--out DIR]
         [--crop X0 Y0 X1 Y1] [--legend tr|tl|br|bl|none]
         [--text-scale F] [--fade F] [--titles PLAIN RECOVERY]
         [--bottom FMT] [--strip-ink light|dark] [--repo PATH]
Writes <out>/<alias>_label_compare_f<frame>.png (default out:
eval/reports/). --repo names the repository root when the script is run
from a copy outside it (default: derived from this file's location).
"""
import argparse
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import cv2
import numpy as np
import pandas as pd

ANGLE_COLS = ["root_ex", "root_ey", "root_ez", "Rsh_y", "Rsh_z", "Rsh_tau",
              "Rel_y", "Rel_z", "Lsh_y", "Lsh_z", "Lsh_tau", "Lel_y", "Lel_z"]
SCALE = 2                    # upscale factor applied before drawing
TITLES = {"plain": "MediaPipe (plain solve)",
          "recovery": "Object-conditioned recovery"}

# Colours (BGR). The blue chain with a white halo and the amber label
# square with a black outline differ in hue for colour print and in
# luminance for greyscale print; the hollow circle (MediaPipe wrist) and
# the cross (object estimate) differ from both by shape.
C_CHAIN = (200, 90, 0)       # blue
C_HALO = (255, 255, 255)
C_LABEL = (0, 159, 230)      # amber
C_MP = (115, 158, 0)         # bluish green
C_BLACK = (0, 0, 0)
C_WHITE = (255, 255, 255)
FONT = cv2.FONT_HERSHEY_SIMPLEX


class _ShoulderAt:
    """Indexable stand-in so fk_wrist(angles, i, sh, ...) can take one
    shoulder position for frame i without a full (n, 3) array."""
    def __init__(self, p):
        self.p = np.asarray(p, float)

    def __getitem__(self, i):
        return self.p


def default_repo():
    """eval/failure/<this file> -> repository root; None when the script
    runs from a copy that sits too shallow for that (e.g. /tmp)."""
    parents = Path(__file__).resolve().parents
    return str(parents[2]) if len(parents) > 2 else None


def load_pipeline(repo):
    """Import the project modules relative to the repository root."""
    repo = Path(repo).resolve()
    for sub in ("eval/failure", "eval/common", "eval/inspect",
                "v1/kinematics"):
        sys.path.insert(0, str(repo / sub))
    import paths                                        # noqa: E402
    import recovery_core as rc                          # noqa: E402
    from moving_window_check import fk_wrist            # noqa: E402
    from check_v1_overlay import fk_arm_dirs            # noqa: E402
    from root_frame import (unity_from_sensor,          # noqa: E402
                            recompose_zxy)
    return SimpleNamespace(paths=paths, rc=rc, fk_wrist=fk_wrist,
                           fk_arm_dirs=fk_arm_dirs,
                           unity_from_sensor=unity_from_sensor,
                           recompose_zxy=recompose_zxy)


def find_labels(P, alias, override):
    if override:
        return Path(override)
    tracked = Path(P.paths.REPO) / "eval" / "labels" / f"frames_{alias}" \
        / "labels.json"
    if tracked.exists():
        return tracked
    return P.paths.EVAL_OUT / f"label_frames_{alias}" / "labels.json"


def load_angles(P, alias):
    out = {}
    for name in ("plain", "recovery"):
        p = P.paths.EVAL_OUT / f"recovery_{alias}" / f"angles_{name}.csv"
        if not p.exists():
            sys.exit(f"missing {p} (run eval/failure/run_recovery.py)")
        out[name] = pd.read_csv(p)[ANGLE_COLS].to_numpy(float)
    return out


def fk_chain(P, angles, i, sh, Lu, Lf, side):
    """Elbow and wrist that the angles of frame i place, solver space
    (same arithmetic as moving_window_check.fk_wrist, which is used as
    the check for the wrist)."""
    R_root = P.recompose_zxy(angles[i, :3])
    si = 3 if side == "right" else 8
    up, fo = P.fk_arm_dirs(angles[i, si:si + 3], angles[i, si + 3:si + 5],
                           side)
    elbow = sh + Lu * (R_root @ up)
    wrist = elbow + Lf * (R_root @ fo)
    ref = P.fk_wrist(angles, i, _ShoulderAt(sh), Lu, Lf, side)
    assert np.allclose(wrist, ref), "fk_chain disagrees with fk_wrist"
    return elbow, wrist


def project(p_solver, K, crop):
    """Solver-space point -> pixel of the upscaled, cropped panel."""
    if p_solver is None or not np.all(np.isfinite(p_solver)):
        return None
    x, y, z = float(p_solver[0]), -float(p_solver[1]), float(p_solver[2])
    if z <= 0.05:
        return None
    u = K["fx"] * x / z + K["ppx"]
    v = K["fy"] * y / z + K["ppy"]
    return (int(round((u - crop[0]) * SCALE)),
            int(round((v - crop[1]) * SCALE)))


# --- drawing primitives (pixel sizes are given at 640x480, times SCALE)

def draw_chain(img, pts):
    w = 3 * SCALE
    segs = [(a, b) for a, b in zip(pts[:-1], pts[1:])
            if a is not None and b is not None]
    for a, b in segs:
        cv2.line(img, a, b, C_HALO, w + 2 * SCALE, cv2.LINE_AA)
    for a, b in segs:
        cv2.line(img, a, b, C_CHAIN, w, cv2.LINE_AA)
    r = 4 * SCALE
    for p in pts:
        if p is not None:
            cv2.circle(img, p, r + SCALE, C_HALO, -1, cv2.LINE_AA)
            cv2.circle(img, p, r, C_CHAIN, -1, cv2.LINE_AA)


def draw_label(img, p):
    h = 6 * SCALE
    tl, br = (p[0] - h, p[1] - h), (p[0] + h, p[1] + h)
    cv2.rectangle(img, tl, br, C_LABEL, -1)
    cv2.rectangle(img, tl, br, C_BLACK, SCALE)


def draw_hollow_circle(img, p):
    r, t = 8 * SCALE, 2 * SCALE
    cv2.circle(img, p, r, C_BLACK, t + 2, cv2.LINE_AA)
    cv2.circle(img, p, r, C_MP, t, cv2.LINE_AA)


def draw_cross(img, p):
    a, t = 9 * SCALE, 2 * SCALE
    arms = [((p[0] - a, p[1]), (p[0] + a, p[1])),
            ((p[0], p[1] - a), (p[0], p[1] + a))]
    for p0, p1 in arms:
        cv2.line(img, p0, p1, C_BLACK, t + 2 * SCALE, cv2.LINE_AA)
    for p0, p1 in arms:
        cv2.line(img, p0, p1, C_WHITE, t, cv2.LINE_AA)


def text_size(fs, th):
    (w, h), base = cv2.getTextSize("Hg", FONT, fs, th)
    return h, base


def draw_legend(img, entries, corner, fs, th):
    """Semi-opaque white box with one marker sample and text per entry."""
    if corner == "none" or not entries:
        return
    h, base = text_size(fs, th)
    pad, gap = max(int(0.6 * h), 6 * SCALE), int(0.5 * h)
    # the marker samples keep their fixed pixel size, so a row must hold
    # the largest of them even when the text is small (narrow crops)
    marker = 2 * (9 * SCALE + 2 * SCALE)
    sample_w = max(int(3.2 * h), marker)
    row_h = max(h + base, marker)
    line_h = row_h + gap
    tw = max(cv2.getTextSize(t, FONT, fs, th)[0][0] for _, t in entries)
    bw = pad + sample_w + pad + tw + pad
    bh = pad + len(entries) * line_h - gap + pad
    H, W = img.shape[:2]
    m = 6 * SCALE
    x0 = m if corner in ("tl", "bl") else W - m - bw
    y0 = m if corner in ("tl", "tr") else H - m - bh
    x0, y0 = max(0, x0), max(0, y0)
    over = img.copy()
    cv2.rectangle(over, (x0, y0), (x0 + bw, y0 + bh), C_WHITE, -1)
    cv2.addWeighted(over, 0.85, img, 0.15, 0, img)
    cv2.rectangle(img, (x0, y0), (x0 + bw, y0 + bh), C_BLACK, 1)
    y = y0 + pad
    for kind, text in entries:
        cy = y + row_h // 2
        cx = x0 + pad + sample_w // 2
        if kind == "chain":
            r = 5 * SCALE
            draw_chain(img, [(x0 + pad + r, cy),
                             (x0 + pad + sample_w - r, cy)])
        elif kind == "label":
            draw_label(img, (cx, cy))
        elif kind == "mp":
            draw_hollow_circle(img, (cx, cy))
        elif kind == "cross":
            draw_cross(img, (cx, cy))
        cv2.putText(img, text, (x0 + pad + sample_w + pad, cy + h // 2),
                    FONT, fs, C_BLACK, th, cv2.LINE_AA)
        y += line_h


def strip(width, text, fs, th, ink="light"):
    """White strip with black text (ink "dark": black strip with white
    text), placed above or below a panel; the text is shrunk when it
    would not fit the width."""
    h, base = text_size(fs, th)
    sh = h + base + int(1.2 * h)
    tw = cv2.getTextSize(text, FONT, fs, th)[0][0]
    if tw > width - 1.2 * h:
        fs *= (width - 1.2 * h) / tw
        th = max(1, int(round(fs * 2)))
    bg, fg = (C_BLACK, C_WHITE) if ink == "dark" else (C_WHITE, C_BLACK)
    s = np.full((sh, width, 3), bg[0], np.uint8)
    cv2.putText(s, text, (int(0.6 * h), int(0.6 * h) + h), FONT, fs,
                fg, th, cv2.LINE_AA)
    return s


def render_panel(frame_img, crop, variant, chain_pts, label_pt, mp_pt,
                 cross_pt, mp_present, bottom, legend, fs, th,
                 fade=0.0, titles=None, ink="light"):
    x0, y0, x1, y1 = crop
    img = cv2.resize(frame_img[y0:y1, x0:x1], None, fx=SCALE, fy=SCALE,
                     interpolation=cv2.INTER_CUBIC)
    if fade > 0:
        # blend the photograph toward black; overlays are drawn afterwards
        img = np.clip(np.rint(img.astype(np.float64) * (1.0 - fade)),
                      0, 255).astype(np.uint8)
    draw_chain(img, chain_pts)
    if mp_pt is not None:
        draw_hollow_circle(img, mp_pt)
    if cross_pt is not None:
        draw_cross(img, cross_pt)
    if label_pt is not None:
        draw_label(img, label_pt)
    if variant == "plain":
        entries = [("chain", "plain-solve arm (FK)"),
                   ("mp", "MediaPipe wrist" if mp_present
                    else "MediaPipe wrist: none"),
                   ("label", "manual label")]
    else:
        entries = [("chain", "recovery arm (FK)"),
                   ("cross", "object wrist estimate"),
                   ("label", "manual label")]
    lfs = 0.8 * fs
    draw_legend(img, entries, legend, lfs, max(1, int(round(lfs * 2))))
    W = img.shape[1]
    title = (titles or TITLES)[variant]
    return np.vstack([strip(W, title, fs, th, ink), img,
                      strip(W, bottom, fs, th, ink)])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", default=default_repo(),
                    help="repository root (default: from this file's path)")
    ap.add_argument("--stem", required=True)
    ap.add_argument("--frames", type=int, nargs="+", required=True)
    ap.add_argument("--labels", default=None,
                    help="labels.json (default: eval/labels/frames_<alias>/)")
    ap.add_argument("--out", default=None,
                    help="output directory (default: eval/reports)")
    ap.add_argument("--crop", type=int, nargs=4, default=None,
                    metavar=("X0", "Y0", "X1", "Y1"),
                    help="region to draw, original pixels (default: full)")
    ap.add_argument("--legend", default="tr",
                    choices=["tl", "tr", "bl", "br", "none"])
    ap.add_argument("--text-scale", type=float, default=1.0,
                    help="multiplier on the text size")
    ap.add_argument("--fade", type=float, default=0.0,
                    help="blend the photograph toward black by this "
                         "fraction before drawing overlays (default 0)")
    ap.add_argument("--titles", nargs=2, default=None,
                    metavar=("PLAIN", "RECOVERY"),
                    help="panel titles (default: the thesis titles)")
    ap.add_argument("--bottom", default=None, metavar="FMT",
                    help="bottom line, str.format with frame, side, d "
                         "(default: the thesis line)")
    ap.add_argument("--strip-ink", default="light",
                    choices=["light", "dark"],
                    help="strip colours: light (thesis) or dark")
    args = ap.parse_args()
    if not 0.0 <= args.fade <= 1.0:
        sys.exit("--fade must lie in [0, 1]")
    titles = (dict(zip(("plain", "recovery"), args.titles))
              if args.titles else None)
    if args.repo is None:
        sys.exit("--repo PATH is needed when the script runs from a copy "
                 "outside the repository")

    P = load_pipeline(args.repo)
    alias = P.paths.ALIAS[args.stem]
    lpath = find_labels(P, alias, args.labels)
    labels = json.loads(lpath.read_text())
    meta = json.loads((lpath.parent / "meta.json").read_text())
    K = meta["intrinsics"]
    frame_dir = lpath.parent
    out_dir = Path(args.out) if args.out else P.paths.EVAL_REPORTS
    out_dir.mkdir(parents=True, exist_ok=True)

    report = {}
    rp = P.paths.EVAL_REPORTS / f"{alias}_recovery_labeled.json"
    if rp.exists():
        for r in json.loads(rp.read_text())["rows"]:
            report[(r["frame"], r["side"])] = r

    inp = P.rc.build_inputs(args.stem)
    lm = inp["lm_df"]
    sl = inp["seg_len"]
    angles = load_angles(P, alias)

    def lm_pt(f, name):
        v = lm.loc[f, [f"{name}_x", f"{name}_y", f"{name}_z"]].to_numpy(float)
        return P.unity_from_sensor(v) if np.all(np.isfinite(v)) \
            else np.full(3, np.nan)

    def dist_cm(p, truth):
        return (float(np.linalg.norm(p - truth)) * 100.0
                if np.all(np.isfinite(p)) else float("nan"))

    def fmt(d):
        return "n/a" if not np.isfinite(d) else f"{d:.2f} cm"

    for f in args.frames:
        per_side = labels.get(str(f), {})
        sides = [s for s, L in per_side.items() if L is not None]
        if not sides:
            print(f"[warn] frame {f}: no label in {lpath}, skipped")
            continue
        img_path = frame_dir / f"f{f:05d}.png"
        frame_img = cv2.imread(str(img_path))
        if frame_img is None:
            print(f"[warn] frame {f}: missing {img_path}, skipped")
            continue
        H, W = frame_img.shape[:2]
        crop = tuple(args.crop) if args.crop else (0, 0, W, H)
        crop = (max(0, crop[0]), max(0, crop[1]),
                min(W, crop[2]), min(H, crop[3]))
        pw = (crop[2] - crop[0]) * SCALE
        # text height about 2.5 percent of the panel width, so print
        # size does not depend on the crop
        fs = max(0.5, 0.025 * pw / 22.0) * args.text_scale
        th = max(1, int(round(fs * 2)))

        rows = []
        for side in sides:
            L = per_side[side]
            truth = P.unity_from_sensor(np.asarray(L["xyz_cam"], float))
            sh = lm_pt(f, f"{side}_shoulder")
            if not np.all(np.isfinite(sh)):
                print(f"[warn] frame {f} {side}: no shoulder landmark, "
                      "skipped")
                continue
            Lu = sl[f"upper_arm_{'R' if side == 'right' else 'L'}"]
            Lf = sl[f"forearm_{'R' if side == 'right' else 'L'}"]
            mp_w = lm_pt(f, f"{side}_wrist")
            w_obj = inp["w_hat_solver"][side][f]
            chains = {name: fk_chain(P, angles[name], f, sh, Lu, Lf, side)
                      for name in ("plain", "recovery")}
            d = {name: dist_cm(chains[name][1], truth) for name in chains}
            d["recovered"] = dist_cm(w_obj, truth)
            d["measured"] = dist_cm(mp_w, truth)

            line = (f"[{f} {side}] plain_fk {fmt(d['plain'])} | "
                    f"recovery_fk {fmt(d['recovery'])} | "
                    f"recovered {fmt(d['recovered'])} | "
                    f"measured {fmt(d['measured'])}")
            r = report.get((f, side))
            if r is not None:
                line += (f"   (report: plain_fk {r['plain_fk_cm']:.2f}, "
                         f"recovery_fk {r['recovery_fk_cm']:.2f}, "
                         f"recovered {r['recovered_cm']:.2f})")
            print(line)

            label_pt = project(truth, K, crop)
            mp_present = np.all(np.isfinite(mp_w))
            panels = []
            for name in ("plain", "recovery"):
                elbow, wrist = chains[name]
                pts = [project(p, K, crop) for p in (sh, elbow, wrist)]
                bottom = f"frame {f}, {side} wrist: label to wrist " \
                         f"{d[name]:.1f} cm" if args.bottom is None else \
                    args.bottom.format(frame=f, side=side, d=d[name])
                panels.append(render_panel(
                    frame_img, crop, name, pts, label_pt,
                    project(mp_w, K, crop) if name == "plain" else None,
                    project(w_obj, K, crop) if name == "recovery" else None,
                    mp_present, bottom, args.legend, fs, th,
                    args.fade, titles, args.strip_ink))
            gap_ink = 0 if args.strip_ink == "dark" else 255
            gap = np.full((panels[0].shape[0], 8 * SCALE, 3), gap_ink,
                          np.uint8)
            rows.append(np.hstack([panels[0], gap, panels[1]]))
        if not rows:
            continue
        vgap = np.full((8 * SCALE, rows[0].shape[1], 3),
                       0 if args.strip_ink == "dark" else 255, np.uint8)
        fig = rows[0]
        for r in rows[1:]:
            fig = np.vstack([fig, vgap, r])
        out = out_dir / f"{alias}_label_compare_f{f}.png"
        cv2.imwrite(str(out), fig)
        print(f"[+] wrote {out} ({fig.shape[1]}x{fig.shape[0]})")


if __name__ == "__main__":
    main()
