#!/usr/bin/env python3
"""Manual wrist labelling for the natural-failure evaluation.

User direction 2026-08-26: the recovered wrist is verified against
manual labels on the natural failure windows. This tool walks the
frames extracted by extract_label_frames.py, shows the colour image,
and takes one click per wanted wrist. The aligned depth at the click
(median of a small patch) is deprojected through the colour intrinsics
into camera space, the same space as the landmark CSV and the
recovered wrist, so eval_labeled_recovery.py can compare them.

Keys:  left click  = place the wrist label for the side shown
       n / space   = next frame      b = previous frame
       s           = skip this frame (no label)
       u           = undo the label on this frame
       j           = jump to the next frame that still needs a label
       q / Esc     = save and quit
--stride N labels every N-th listed frame of each side (the clean
reference frames and frames already labelled are always kept), for a
smaller set: --stride 4 on frames_r5 is every twentieth recording frame.
Progress is saved after every click; rerun to continue.

Input:  eval/output/label_frames_r5/  (png, depth npy, meta.json)
Output: eval/output/label_frames_r5/labels.json
Run:    python eval/failure/label_wrists.py [--dir DIR]
        (the tracked sets live in eval/labels/frames_<alias>/; pass --dir)

Where to click (2026-09-06): a fixed visible mark on the wrist, the same
mark on every frame of a set. Rail set: the cuff seam of the jacket
sleeve, centred across the arm. Loop set: the wrist jewellery, the bead
bracelet on the left wrist and the watch on the right, centred where it
crosses the arm. Skip (s) only when the cube hides the mark completely.

Depth under the click: the median of a small patch, widened step by
step (up to MAX_SEARCH pixels, about 1.6 cm at 1 m) when the depth
image has a hole there, which it often has on dark beads and on the arm
silhouette; the click pixel stays the label position, only the depth
comes from the nearest valid neighbours. Where those neighbours mix two
surfaces (the arm against the background or the cube, spread over
MIXED_M) the surface with more pixels is kept, the nearer one on a tie;
the spread, the rule and the search radius are stored so the grading
can report such labels, and the label is shown as MIXED on screen so the
click can be redone on clean skin beside the mark.
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np

PATCH = 2            # depth median over (2*PATCH+1)^2 pixels
SCALE = 2            # display magnification
MIXED_M = 0.05       # patch spread above which two surfaces are assumed
NEAR_M = 0.03        # the near surface: pixels within this of the minimum
MAX_SEARCH = 10      # widen the patch up to this radius when depth is missing
MIN_VALID = 4        # stop widening once this many valid pixels are found


def deproject(u, v, depth_img, intr, depth_scale):
    # Dark beads and the arm silhouette leave holes in the depth image,
    # so the patch is widened step by step until a few valid pixels
    # exist; the click pixel itself stays the label position, only the
    # depth is taken from the nearest valid neighbours (6 px is about
    # 1 cm at 1 m).
    valid = np.zeros(0)
    r = PATCH
    for r in range(PATCH, MAX_SEARCH + 1):
        y0, y1 = max(0, v - r), min(depth_img.shape[0], v + r + 1)
        x0, x1 = max(0, u - r), min(depth_img.shape[1], u + r + 1)
        patch = depth_img[y0:y1, x0:x1].astype(float)
        valid = patch[patch > 0] * depth_scale
        if valid.size >= MIN_VALID:
            break
    if valid.size == 0:
        return None
    spread = float(valid.max() - valid.min())
    mixed = spread > MIXED_M
    rule = "single"
    used = valid
    if mixed:
        # two surfaces under the click (arm against background, or arm
        # against the cube): keep the one with more pixels among the
        # nearest valid ones, the nearer one on a tie
        near = valid[valid <= valid.min() + NEAR_M]
        far = valid[valid >= valid.max() - NEAR_M]
        used, rule = ((near, "majority_near") if near.size >= far.size
                      else (far, "majority_far"))
    z = float(np.median(used))
    x = (u - intr["ppx"]) / intr["fx"] * z
    y = (v - intr["ppy"]) / intr["fy"] * z
    return {"u": int(u), "v": int(v), "depth_m": round(z, 4),
            "xyz_cam": [round(x, 4), round(y, 4), round(z, 4)],
            "depth_valid_px": int(valid.size), "depth_search_px": int(r),
            "depth_spread_m": round(spread, 4), "mixed_surface": bool(mixed),
            "depth_rule": rule, "depth_used_px": int(used.size)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=None)
    ap.add_argument("--stride", type=int, default=1,
                    help="label every STRIDE-th listed frame of each side "
                         "(clean_frames are always kept); frames already "
                         "labelled are kept too")
    args = ap.parse_args()
    here = Path(__file__).resolve().parent
    d = Path(args.dir) if args.dir else \
        here.parents[1] / "eval" / "output" / "label_frames_r5"
    meta = json.loads((d / "meta.json").read_text())
    intr, dscale = meta["intrinsics"], meta["depth_scale"]
    frames = sorted(int(f) for f in meta["frames"])
    out = d / "labels.json"
    labels = json.loads(out.read_text()) if out.exists() else {}
    if args.stride > 1:
        clean = set(int(f) for f in meta.get("clean_frames", {}))
        keep = set(clean) | set(int(f) for f in labels)
        for side in ("left", "right"):
            run = [f for f in frames
                   if side in meta["frames"][str(f)] and f not in clean]
            keep |= set(run[::args.stride])
        frames = [f for f in frames if f in keep]
        print(f"[info] stride {args.stride}: {len(frames)} frames to visit")

    def save():
        out.write_text(json.dumps(labels, indent=1))

    state = {"i": 0, "click": None, "msg": "", "msg_ttl": 0}
    # start at the first frame without a label
    for k, f in enumerate(frames):
        if str(f) not in labels:
            state["i"] = k
            break

    def on_mouse(ev, x, y, flags, param):
        if ev == cv2.EVENT_LBUTTONDOWN:
            state["click"] = (x // SCALE, y // SCALE)

    win = "label wrists"
    cv2.namedWindow(win)
    cv2.setMouseCallback(win, on_mouse)
    while True:
        f = frames[state["i"]]
        sides = meta["frames"][str(f)]
        img = cv2.imread(str(d / f"f{f:05d}.png"))
        depth = np.load(d / f"f{f:05d}_depth.npy")
        lab = labels.get(str(f), {})
        side = next((s for s in sides if s not in lab), None)
        disp = cv2.resize(img, None, fx=SCALE, fy=SCALE,
                          interpolation=cv2.INTER_NEAREST)
        for s, L in lab.items():
            if L is None:
                continue
            p = (L["u"] * SCALE, L["v"] * SCALE)
            cv2.circle(disp, p, 8, (0, 255, 0), 2)
            cv2.putText(disp, s, (p[0] + 10, p[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        head = (f"frame {f}  [{state['i'] + 1}/{len(frames)}]  "
                + (f"click the {side.upper()} wrist" if side
                   else "done - n next, j next unlabelled"))
        cv2.putText(disp, head, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 0, 0), 4)
        cv2.putText(disp, head, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (0, 255, 255), 2)
        if state["msg_ttl"] > 0:
            state["msg_ttl"] -= 1
            cv2.putText(disp, state["msg"], (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4)
            cv2.putText(disp, state["msg"], (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow(win, disp)
        key = cv2.waitKey(30) & 0xFF
        if state["click"] is not None and side is not None:
            u, v = state["click"]
            state["click"] = None
            L = deproject(u, v, depth, intr, dscale)
            if L is None:
                print(f"[warn] frame {f}: no valid depth within "
                      f"{MAX_SEARCH} px of ({u},{v}), click again nearby",
                      flush=True)
                state["msg"] = (f"NO DEPTH within {MAX_SEARCH} px of the "
                                "click: click the skin right beside it")
                state["msg_ttl"] = 60
                continue
            labels.setdefault(str(f), {})[side] = L
            save()
            print(f"[+] frame {f} {side}: {L['xyz_cam']} m"
                  + (f"  [mixed surfaces, spread {L['depth_spread_m']:.2f} m,"
                     f" nearest kept from {L['depth_used_px']} px;"
                     " re-click a few px inside the arm if this looks wrong]"
                     if L["mixed_surface"] else ""), flush=True)
            # show the placed label for a moment before moving on, so
            # the click is visibly acknowledged
            p = (L["u"] * SCALE, L["v"] * SCALE)
            cv2.circle(disp, p, 8, (0, 255, 0), 2)
            msg = (f"saved {side} wrist, depth {L['depth_m']:.3f} m"
                   + ("  MIXED SURFACE: u to undo, re-click inside the arm"
                      if L["mixed_surface"] else ""))
            cv2.putText(disp, msg, (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 0, 0), 4)
            cv2.putText(disp, msg, (10, 60), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 255, 0), 2)
            cv2.imshow(win, disp)
            cv2.waitKey(600)
            if all(s in labels[str(f)] for s in sides):
                state["i"] = min(state["i"] + 1, len(frames) - 1)
            continue
        state["click"] = None
        if key in (ord("n"), ord(" ")):
            state["i"] = min(state["i"] + 1, len(frames) - 1)
        elif key == ord("b"):
            state["i"] = max(state["i"] - 1, 0)
        elif key == ord("j"):
            todo = [k for k in range(state["i"] + 1, len(frames))
                    if any(s2 not in labels.get(str(frames[k]), {})
                           for s2 in meta["frames"][str(frames[k])])]
            if todo:
                state["i"] = todo[0]
            else:
                print("[info] no frame after this one needs a label")
        elif key == ord("s"):
            labels[str(f)] = {s: None for s in sides}
            save()
            state["i"] = min(state["i"] + 1, len(frames) - 1)
        elif key == ord("u"):
            labels.pop(str(f), None)
            save()
        elif key in (ord("q"), 27):
            break
    save()
    done = sum(1 for v in labels.values() for L in v.values() if L)
    print(f"[+] saved {out}: {done} wrist labels, "
          f"{sum(1 for v in labels.values() if all(L is None for L in v.values()))} skipped")


if __name__ == "__main__":
    main()
