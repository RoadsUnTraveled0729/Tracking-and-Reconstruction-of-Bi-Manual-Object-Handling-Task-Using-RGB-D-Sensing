#!/usr/bin/env python3
"""Three slow, fixed-camera stages of the verified two-link elbow geometry.

The construction imports the existing illustrative geometry without modifying
it. V9 Section 5.5, Eqs. 5.8-5.12. The wrist is an inferred target and the prior
direction selects an elbow from a 3D circle; neither is a new measurement.
Native slide text supplies the exact equations and assumptions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

import recovery_geometry as source
import teaching_flow as drawing

DURATION = 36
SCALE = 1800.0
ORIGIN = np.array([320.0, 600.0])


def project(points):
    p = np.asarray(points)
    return np.stack([ORIGIN[0]+SCALE*(p @ source.RIGHT),
                     ORIGIN[1]-SCALE*(p @ source.UP)], axis=-1)


def line(d, points, color, width=9):
    d.line([tuple(point) for point in project(points)], fill=color, width=width, joint="curve")


def point(d, value, color, radius=23, hollow=False):
    x, y = project(value)
    d.ellipse((x-radius, y-radius, x+radius, y+radius),
              fill=drawing.BG if hollow else color, outline=color, width=6)


def remembered_direction(d):
    a, b = project([source.SHOULDER, source.SHOULDER+source.L1*source.MEMORY*1.15])
    v = b-a; length = np.linalg.norm(v); u = v/length
    for offset in range(0, int(length)-24, 34):
        d.line([tuple(a+u*offset), tuple(a+u*min(offset+18, length-24))],
                fill=drawing.AMBER, width=8)
    side = np.array([-u[1], u[0]])
    d.polygon([tuple(b), tuple(b-u*30+side*15), tuple(b-u*30-side*15)], fill=drawing.AMBER)


def frame(t, selected_only=False):
    phase = 2 if selected_only else min(2, int(t/12))
    im, d = drawing.base("", phase+1, 3)
    if selected_only:
        drawing.TEXT.clear()
    geometry_marks = [(source.SHOULDER, 25), (source.WRIST, 25)]
    if phase >= 1:
        line(d, source.CIRCLE, drawing.TEAL, 8)
        geometry_marks.extend((p, 5) for p in source.CIRCLE)
    if phase == 1:
        # Three valid alternatives held for four seconds each. They are not an
        # elbow trajectory and do not imply a changing camera or measured arm.
        sample = [12, 68, 132][min(2, int((t-12)/4))]
        elbow = source.CIRCLE[sample]
        line(d, [source.SHOULDER, elbow, source.WRIST], "#A9B6C3", 9)
        point(d, elbow, drawing.TEAL, 25)
        geometry_marks.append((elbow, 25))
        drawing.text(d, (900, 780, 1395, 905), "ELBOWS", 90, drawing.TEAL, True)
    if phase == 2:
        remembered_direction(d)
        drawing.text(d, (60, 940, 600, 1040), "PRIOR", 90, drawing.AMBER, True)
        progress = 1.0 if selected_only else drawing.smooth((t-28)/3)
        if progress > 0:
            # Reveal the two-link construction while keeping its endpoints fixed.
            if progress < .5:
                p = source.SHOULDER+(source.ELBOW-source.SHOULDER)*(progress*2)
                line(d, [source.SHOULDER, p], drawing.INK, 13)
            else:
                p = source.ELBOW+(source.WRIST-source.ELBOW)*((progress-.5)*2)
                line(d, [source.SHOULDER, source.ELBOW, p], drawing.INK, 13)
            point(d, source.ELBOW, drawing.AMBER, 26)
            geometry_marks.append((source.ELBOW, 26))
            drawing.text(d, (925, 790, 1395, 915), "ELBOW", 90, drawing.AMBER, True)
            ep = project(source.ELBOW)
            d.line((tuple(ep+np.array([28, 0])), (900, float(ep[1]))), fill=drawing.LINE, width=4)
    point(d, source.SHOULDER, drawing.INK, 25)
    point(d, source.WRIST, drawing.TEAL, 25, hollow=True)
    drawing.text(d, (35, 110, 715, 210), "SHOULDER", 90, drawing.INK, True)
    d.line(((300, 215), (320, 567)), fill=drawing.LINE, width=4)
    drawing.text(d, (915, 435, 1405, 657), "WRIST\nTARGET", 90, drawing.TEAL, True)
    wp = project(source.WRIST)
    d.line((tuple(wp+np.array([30, -5])), (900, 570)), fill=drawing.LINE, width=4)
    # Check actual candidate markers and the projected locus against glyph
    # bounds, rather than checking only text-to-text intersections.
    for world, radius in geometry_marks:
        px, py = project(world)
        for item in drawing.TEXT:
            bounds = item[-1]
            dx = px-np.clip(px, bounds[0], bounds[2])
            dy = py-np.clip(py, bounds[1], bounds[3])
            if dx*dx+dy*dy < (radius+8)**2:
                raise ValueError(f"Geometry touches label: {item[2]}")
    return drawing.finish(im)


def main(preview_only=False):
    geometry = source.validate_geometry()
    bound = project(source.CIRCLE)
    assert bound[:, 0].min() > 0 and bound[:, 0].max() < drawing.W
    assert bound[:, 1].min() > 230 and bound[:, 1].max() < drawing.H-80
    drawing.OUT.mkdir(parents=True, exist_ok=True)
    frame(35.9, selected_only=True).save(drawing.OUT/"teaching_elbow_selected.png")
    report = drawing.export_asset("teaching_elbow", frame, DURATION, preview_only,
        {"sources": ["writing/v9/Thesis_V9.pdf",
                     "presentation/defense_2026/anim/recovery_geometry.py"],
         "thesis_reference": "V9 Section5.5, Eqs.5.8-5.12",
         "geometry": geometry,
         "geometry_label_clearance": "PASS: all projected locus points and visible candidate markers avoid glyph bounds by at least8px",
         "geometry_source": "presentation/defense_2026/anim/recovery_geometry.py",
         "geometry_source_sha256": hashlib.sha256(Path(source.__file__).read_bytes()).hexdigest(),
         "elbow_generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         "stages": ["0-12 s: known shoulder and object-derived wrist target",
                    "12-24 s: three valid elbow alternatives, four-second holds",
                    "24-36 s: prior direction; three-second construction; five-second final hold"],
         "camera": "Fixed orthographic projection of the same verified 3D geometry"})
    report["selected_still_sha256"] = hashlib.sha256((drawing.OUT/"teaching_elbow_selected.png").read_bytes()).hexdigest()
    (drawing.REVIEW/"teaching_elbow_checks.json").write_text(json.dumps(report, indent=2)+"\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--preview-only", action="store_true")
    main(ap.parse_args().preview_only)
