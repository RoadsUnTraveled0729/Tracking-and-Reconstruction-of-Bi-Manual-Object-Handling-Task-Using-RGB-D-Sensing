#!/usr/bin/env python3
"""Draw source-backed coordinate conventions without altering source photographs.

These static diagrams explain origins and basis changes. Illustrative lengths,
poses and viewing angles are not measurements, except grasp_offset, which is
drawn on one recorded R7 frame from pinned tables; its values are measured on
that frame and remain illustrative, not a thesis result. tpose_reference shows
the thesis Figure 3.5 (copied) above a schematic MediaPipe T-pose drawn from
constants only, with no measured data. Run with
--only KEY to regenerate single figures. The shared axis renderer also
serves the source-synchronized movies, so axis colour never changes by page.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from anim.coordinate_axes import (AXIS_COLORS, CAMERA_TO_CAMERA_PRIME,
                                  CANONICAL_ROOT, draw_triad,
                                  make_orthographic_projector,
                                  make_pinhole_projector, view_matrix)

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OUT = HERE / 'figures' / 'coordinate_frames'
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SIZE = (1440, 1200)
WHITE = '#FFFFFF'
GRAY = '#BBBBBB'
RULE = '#666666'
RECORDS = []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def label(draw, value, xy, *, size=48, fill=WHITE, anchor='la'):
    font = ImageFont.truetype(FONT, size)
    bounds = draw.textbbox(xy, value, font=font, anchor=anchor)
    if min(bounds[0], bounds[1]) < 0 or bounds[2] > SIZE[0] or bounds[3] > SIZE[1]:
        raise ValueError(f'Figure text outside canvas: {value}: {bounds}')
    draw.text(xy, value, font=font, fill=fill, anchor=anchor)
    return list(bounds)


def arrow(draw, a, b, fill=WHITE, width=5):
    a, b = np.asarray(a, float), np.asarray(b, float)
    draw.line([tuple(a), tuple(b)], fill=fill, width=width)
    unit = (b-a)/np.linalg.norm(b-a)
    side = np.array([-unit[1], unit[0]])
    draw.polygon([tuple(b), tuple(b-20*unit+9*side), tuple(b-20*unit-9*side)], fill=fill)


def dot(draw, xy, radius=8, fill=WHITE):
    x, y = xy
    draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=fill)


def canvas():
    im = Image.new('RGB', SIZE, '#000000')
    return im, ImageDraw.Draw(im)


def triad(draw, origin, basis, project, length, frame, *, held=False, role='frame origin'):
    row = draw_triad(draw, origin, basis, project, length, label_px=48,
                     line_width=6, held=held)
    row.update(frame=frame, role=role)
    return row


def save(key, im, frames, source, **extra):
    dest = OUT / (key+'.png')
    im.save(dest)
    RECORDS.append({'key': key, 'path': str(dest.relative_to(REPO)),
                    'sha256': sha(dest), 'dimensions_px': list(im.size),
                    'classification': 'explanatory static diagram; not experimental output',
                    'source': source, 'frames': frames, **extra})


def ry(deg):
    a = math.radians(deg)
    return np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0],
                     [-math.sin(a), 0, math.cos(a)]])


def rx(deg):
    a = math.radians(deg)
    return np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)],
                     [0, math.sin(a), math.cos(a)]])


def camera_frames():
    im, draw = canvas()
    frames = []
    for top, name, basis, meaning in [
            (0, 'Camera', CAMERA_TO_CAMERA_PRIME, 'Right-handed; Y image-down'),
            (600, "Camera-prime", np.eye(3), 'Left-handed; Y image-up')]:
        label(draw, name, (70, top+42))
        label(draw, meaning, (620, top+74), size=46)
        origin_y=top+315+(50 if top else 0)
        project = make_orthographic_projector(view_matrix(-35, 20), np.zeros(3), 640, (365, origin_y))
        frames.append(triad(draw, np.zeros(3), basis, project, .32, name))
        dot(draw, (365, origin_y))
        label(draw, 'Optical origin', (620, top+330))
        if not top:
            draw.line((55, 583, 1385, 583), fill=RULE, width=2)
    save('camera_frames', im, frames, 'Thesis V9 Section 3.1, Eq. 3.1, pp. 21-22',
         reference_coordinates='Camera-prime for both displayed bases',
         explanation='Separate views of the same optical origin; F reverses only Y and has determinant -1.')


# Page 12 (DECISIONS.md D-106): the thesis V9 Figure 3.5 copied unchanged
# above a schematic MediaPipe upper-body T-pose drawn only from the constants
# below. Nothing in the lower half reads a landmark table, a bag or a photo.
TPOSE_THESIS_FIGURE = 'writing/v9/figures/ch3_fig_tpose_a.png'
TPOSE_THESIS_CAPTION = ('Figure 3.5. The reference configuration: the subject in the T-pose with a frame '
                        'at each landmark. All frames share the root orientation, right arm along +x, '
                        'left arm along -x.')
TPOSE_THESIS_COPY = 'thesis_fig3_5_reference_pose.png'
# Editorial layout (px): the box the thesis figure is fitted into, the rule
# between the halves, and the schematic's L24 position and scale.
TPOSE_FIGURE_BOX = (40, 70, 1400, 590)
TPOSE_RULE_Y = 604
TPOSE_ORIGIN_PX = (600., 1090.)
TPOSE_PX_PER_M = 600.
# Schematic landmark positions in the root frame {L24} (m): X toward the
# person's right, Y up, Z forward. The torso is the trapezoid 12-11-23-24,
# shoulders wider than hips, centred on one vertical axis (DECISIONS.md D-107):
# shoulder width 0.35 = median of the four committed
# eval/reports/recording_*_offset_fit.json segment_lengths_m.shoulder_width
# (0.351, 0.317, 0.377, 0.344); hip width 0.20 = median of the same four
# recordings' MediaPipe hip-to-hip median in v1/mediapipe/output (0.202,
# 0.198, 0.191, 0.212; tables not committed). Torso height 0.50, upper arm
# 0.28 and forearm 0.26 stay editorial (D-106). Every arm point has Y = 0.50,
# the shoulder height, so both arms are exactly horizontal.
TPOSE_SHOULDER_WIDTH_M = 0.35
TPOSE_HIP_WIDTH_M = 0.20
TPOSE_TORSO_HEIGHT_M = 0.50
TPOSE_UPPER_ARM_M = 0.28
TPOSE_FOREARM_M = 0.26
_axis = -TPOSE_HIP_WIDTH_M/2                     # torso centre line, X in {L24}
_r_sh = round(_axis+TPOSE_SHOULDER_WIDTH_M/2, 6)  # L12, the right shoulder
_l_sh = round(_axis-TPOSE_SHOULDER_WIDTH_M/2, 6)  # L11, the left shoulder
_h = TPOSE_TORSO_HEIGHT_M
TPOSE_SCHEMATIC_ROOT_M = {
    11: (_l_sh, _h, 0.), 12: (_r_sh, _h, 0.),
    13: (round(_l_sh-TPOSE_UPPER_ARM_M, 6), _h, 0.), 14: (round(_r_sh+TPOSE_UPPER_ARM_M, 6), _h, 0.),
    15: (round(_l_sh-TPOSE_UPPER_ARM_M-TPOSE_FOREARM_M, 6), _h, 0.),
    16: (round(_r_sh+TPOSE_UPPER_ARM_M+TPOSE_FOREARM_M, 6), _h, 0.),
    23: (-TPOSE_HIP_WIDTH_M, 0., 0.), 24: (0., 0., 0.)}
TPOSE_TORSO = [(11, 12), (12, 24), (24, 23), (23, 11)]
TPOSE_RIGHT_ARM = [(12, 14), (14, 16)]
TPOSE_LEFT_ARM = [(11, 13), (13, 15)]
# Grey torso and dim left arm use GREY_EDGE of anim/unified_panels.py; the
# right arm uses its FOCUS_WHITE.
TPOSE_GREY_EDGE = '#656565'
TPOSE_TRIAD_M = {24: .15, 12: .10, 14: .10}
# Z points at the viewer, so in this front view it is drawn as a blue ring
# around the origin dot (the out-of-page symbol) with its letter upper right,
# clear of the edges; the X letters sit above the arm line instead of on it.
TPOSE_Z_RING_PX = 17
TPOSE_AXIS_LABEL_OFFSET = {'X': (0., -30.), 'Z': (32., -32.)}
# At L24 the edge 12-24 now slants in from the upper left and would touch the
# default Y letter, so that one letter moves right of the Y tip (D-107).
TPOSE_FRAME_LABEL_OFFSET = {24: {'Y': (16., -14.)}}
# Minimum gap (px) kept between any label box and a skeleton edge, on top of
# the edge half-width; editorial (D-107), checked in tpose_reference().
TPOSE_LABEL_EDGE_GAP_PX = 4
# Point labels: (landmark, text, offset from the dot px, anchor). L16 sits
# left of its dot on the arm line, the others below their dots; L12 and L11
# shift outward, off the torso edges that slant inward below them.
TPOSE_POINT_LABELS = [(16, 'L16: point', (-20., 0.), 'rm'), (14, 'L14', (0., 28.), 'ma'),
                      (12, 'L12', (-14., 28.), 'ra'), (11, 'L11', (14., 28.), 'la'),
                      (13, 'L13', (0., 28.), 'ma'), (15, 'L15', (0., 28.), 'ma'),
                      (24, 'L24', (0., 28.), 'ma'), (23, 'L23', (0., 28.), 'ma')]
TPOSE_TEXT = [('Root (0, 180, 0) deg', WHITE), ('All arm coordinates zero', WHITE),
              ('Right arm +X, left arm -X', WHITE), ('Schematic, not measured', GRAY)]
TPOSE_TEXT_XY = (840, 900)


def tpose_reference():
    im, draw = canvas()
    source = REPO/TPOSE_THESIS_FIGURE
    copied = OUT/TPOSE_THESIS_COPY
    if not copied.exists():
        shutil.copyfile(source, copied)
    if sha(copied) != sha(source):
        raise ValueError('The copied thesis figure differs from writing/v9.')
    label(draw, 'Thesis Figure 3.5: reference pose', (40, 10), size=44)
    x0, y0, x1, y1 = TPOSE_FIGURE_BOX
    with Image.open(copied) as figure:
        native = figure.size
        rgb = figure.convert('RGB')
    scale = min((x1-x0)/native[0], (y1-y0)/native[1])
    shown = (round(native[0]*scale), round(native[1]*scale))
    # One uniform scale; rounding changes the aspect by under one pixel.
    if abs(shown[0]/shown[1]-native[0]/native[1]) > 1/min(shown):
        raise ValueError('Thesis figure would be distorted.')
    at = ((x0+x1-shown[0])//2, y0+(y1-y0-shown[1])//2)
    im.paste(rgb.resize(shown, Image.Resampling.LANCZOS), at)
    draw.line((40, TPOSE_RULE_Y, 1400, TPOSE_RULE_Y), fill=RULE, width=2)
    label(draw, 'Schematic MediaPipe T-pose, front view', (40, TPOSE_RULE_Y+14), size=44)
    # Front orthographic view of Camera-prime: screen right is +X, up is +Y.
    points = {n: CANONICAL_ROOT@np.array(p, float) for n, p in TPOSE_SCHEMATIC_ROOT_M.items()}
    project = make_orthographic_projector(np.eye(3), np.zeros(3), TPOSE_PX_PER_M, TPOSE_ORIGIN_PX)
    px = {n: project(p) for n, p in points.items()}
    arm_y = {float(px[n][1]) for n in (11, 12, 13, 14, 15, 16)}
    if len(arm_y) != 1:
        raise ValueError('Schematic arms are not horizontal at shoulder height.')
    shoulder_px = float(px[11][0]-px[12][0])
    hip_px = float(px[23][0]-px[24][0])
    if not (shoulder_px > hip_px > 0 and
            abs((px[11][0]+px[12][0])-(px[23][0]+px[24][0])) < 1e-6):
        raise ValueError('Schematic torso is not a centred trapezoid with shoulders wider than hips.')
    for edges, fill, width in [(TPOSE_TORSO, TPOSE_GREY_EDGE, 4), (TPOSE_LEFT_ARM, TPOSE_GREY_EDGE, 6),
                               (TPOSE_RIGHT_ARM, WHITE, 6)]:
        for a, b in edges:
            draw.line([tuple(px[a]), tuple(px[b])], fill=fill, width=width)
    frames = []
    for n in (24, 12, 14):
        row = draw_triad(draw, points[n], CANONICAL_ROOT, project, TPOSE_TRIAD_M[n], label_px=40,
                         line_width=6, label_offsets={**TPOSE_AXIS_LABEL_OFFSET,
                                                      **TPOSE_FRAME_LABEL_OFFSET.get(n, {})})
        u, v = px[n]
        r = TPOSE_Z_RING_PX
        draw.ellipse((u-r, v-r, u+r, v+r), outline=AXIS_COLORS['Z'], width=4)
        row.update(frame=f'L{n}', role='root origin' if n == 24 else 'frame origin',
                   z_symbol='ring around the origin: Z toward the viewer')
        frames.append(row)
    for n in points:
        dot(draw, px[n], 8)
    bounds = []
    for n, text, (dx, dy), anchor in TPOSE_POINT_LABELS:
        bounds.append(label(draw, text, (px[n][0]+dx, px[n][1]+dy), size=40, anchor=anchor))
    tx, ty = TPOSE_TEXT_XY
    bounds += [label(draw, text, (tx, ty+i*44), size=34, fill=fill) for i, (text, fill) in enumerate(TPOSE_TEXT)]
    for box in bounds:
        if box[1] < TPOSE_RULE_Y:
            raise ValueError(f'Schematic label crosses into the thesis half: {box}')
    # No label box (point, axis or text) may touch a skeleton edge.
    for box in bounds+[b for row in frames for b in row['label_bounds']]:
        for edges, width in [(TPOSE_TORSO, 4), (TPOSE_LEFT_ARM, 6), (TPOSE_RIGHT_ARM, 6)]:
            pad = width/2+TPOSE_LABEL_EDGE_GAP_PX
            for a, b in edges:
                pa, pb = np.asarray(px[a], float), np.asarray(px[b], float)
                for t in np.linspace(0., 1., int(np.linalg.norm(pb-pa))+2):
                    x, y = pa+t*(pb-pa)
                    if box[0]-pad <= x <= box[2]+pad and box[1]-pad <= y <= box[3]+pad:
                        raise ValueError(f'Schematic label {box} touches edge L{a}-L{b}.')
    save('tpose_reference', im, frames,
         'Thesis V9 Sections 3.2.2-3.3.3, Figure 3.5, pp. 27-30',
         classification='thesis figure copy above an illustrative schematic; not experimental output',
         thesis_figure={'source': TPOSE_THESIS_FIGURE, 'source_sha256': sha(source),
                        'copy': str(copied.relative_to(REPO)), 'sha256': sha(copied),
                        'thesis_builder': 'writing/v9/scripts/build_ch3.py (IMG FIGC / "ch3_fig_tpose_a.png")',
                        'caption': TPOSE_THESIS_CAPTION, 'native_px': list(native),
                        'displayed_px': list(shown), 'displayed_at_px': list(at),
                        'fit': 'uniform scale into the box, Lanczos resampling, no crop',
                        'box_px': list(TPOSE_FIGURE_BOX)},
         schematic=True, note='illustrative schematic, not a measurement',
         schematic_constants={'landmarks_root_m': {str(n): list(p) for n, p in TPOSE_SCHEMATIC_ROOT_M.items()},
                              'landmarks_camera_prime_m': {str(n): p.tolist() for n, p in points.items()},
                              'landmarks_px': {str(n): p.tolist() for n, p in px.items()},
                              'projection': 'orthographic front view of Camera-prime (view rows = identity)',
                              'px_per_m': TPOSE_PX_PER_M, 'l24_origin_px': list(TPOSE_ORIGIN_PX),
                              'torso_edges': TPOSE_TORSO, 'right_arm_edges': TPOSE_RIGHT_ARM,
                              'left_arm_edges': TPOSE_LEFT_ARM,
                              'colours': {'right_arm': WHITE, 'left_arm': TPOSE_GREY_EDGE,
                                          'torso': TPOSE_GREY_EDGE, 'landmarks': WHITE},
                              'triad_lengths_m': {str(n): v for n, v in TPOSE_TRIAD_M.items()},
                              'z_ring_px': TPOSE_Z_RING_PX, 'frame_label_offsets_px': {str(k): v for k, v in TPOSE_FRAME_LABEL_OFFSET.items()},
                              'label_edge_gap_px': TPOSE_LABEL_EDGE_GAP_PX, 'text': [t for t, _ in TPOSE_TEXT],
                              'torso_shape': 'trapezoid, shoulders wider than hips, centred on one vertical axis',
                              'widths_m': {'shoulder': TPOSE_SHOULDER_WIDTH_M, 'hip': TPOSE_HIP_WIDTH_M},
                              'widths_px': {'shoulder': shoulder_px, 'hip': hip_px},
                              'widths_source': ('DECISIONS.md D-107: shoulder = median of the four committed '
                                                'eval/reports/recording_*_offset_fit.json shoulder_width values; '
                                                'hip = median of the same recordings\' MediaPipe hip-to-hip '
                                                'medians (v1/mediapipe/output, not committed)'),
                              'proportions': ('torso widths per D-107; torso height 0.50 m, upper arm 0.28 m '
                                              'and forearm 0.26 m editorial, no data source (D-106)')},
         label_bounds=bounds,
         canonical_root_matrix=CANONICAL_ROOT.tolist(),
         root_euler_degrees=[0, 180, 0], arm_coordinates='all zero',
         wrist_orientation='not drawn; unobserved')


def scene_mapping():
    im, draw = canvas()
    swap = np.array([[1., 0., 0.], [0., 0., 1.], [0., 1., 0.]])
    gravity = rx(-20)
    frames = []
    rows = [('World', gravity@swap, 'Desk-marker origin', 'Right-handed'),
            ('Unity', gravity, 'Same marker origin', 'Y/Z swap S'),
            ('Scene', np.eye(3), 'Floor below desk marker', 'Gravity G; translation t_f')]
    for i, (name, basis, origin_label, operation) in enumerate(rows):
        top = i*400
        label(draw, name, (60, top+28))
        project = make_orthographic_projector(view_matrix(25, 15), np.zeros(3), 730, (340, top+236))
        frames.append(triad(draw, np.zeros(3), basis, project, .22, name))
        dot(draw, (340, top+236))
        label(draw, origin_label, (620, top+140), size=46)
        label(draw, operation, (620, top+219), size=44, fill=GRAY)
        if i<2:
            draw.line((55, top+390, 1385, top+390), fill=RULE, width=2)
    save('scene_mapping', im, frames,
         'Thesis V9 Sections 6.2, 6.4, Eqs. 6.1 and 6.6, pp. 72, 78',
         reference_coordinates='Scene directions in three separated explanatory views',
         translation_explanation='World and Unity share the desk-marker origin; Scene is on the floor directly below it.',
         illustrative_gravity_degrees=-20,
         numeric_geometry='The chosen tilt illustrates the transformation; it is not a calibrated recording value.')


def object_frames():
    im, draw = canvas()
    label(draw, 'Right-handed marker frames', (55, 28))
    camera = np.zeros(3); world = np.array([-.55, -.2, .8]); obj = np.array([.5, -.1, .9])
    project = make_orthographic_projector(view_matrix(18, -18), [.05, -.05, .45], 790, (770, 500))
    frames = []
    for name, origin, basis in [('Camera', camera, CAMERA_TO_CAMERA_PRIME),
                               ('World', world, CAMERA_TO_CAMERA_PRIME@rx(25)),
                               ('Object', obj, CAMERA_TO_CAMERA_PRIME@rx(-15)@ry(-25))]:
        frames.append(triad(draw, origin, basis, project, .22, name))
        dot(draw, project(origin))
    for end in [world, obj]:
        a, b = project(camera), project(end)
        arrow(draw, a+.22*(b-a), b-.12*(b-a), GRAY, 3)
    label(draw, 'Camera', (1040, 210))
    label(draw, 'Optical origin', (1040, 275), size=44)
    label(draw, 'World', (65, 900))
    label(draw, 'Desk marker', (65, 965), size=44)
    label(draw, 'Object', (1040, 870))
    label(draw, 'Moving marker', (1040, 935), size=42)
    label(draw, 'Z: normal to each marker face', (70, 1090))
    save('object_frames', im, frames, 'Thesis V9 Sections 2.2, 4.1, Eq. 4.1',
         reference_coordinates='Illustrative Camera-prime display coordinates; Camera, World and Object are right-handed frames. Positions and marker orientations are not fitted data.')


# Page 24: one recorded R7 holding frame, the same measured displacement shown
# in the camera image (left) and in MappedMarker coordinates (right).
# Sources are the pinned tables that presentation/v9/anim/video1_overlay.py
# reads for VIDEO-1; nothing is re-detected. Values are measured on one frame
# and are illustrative, not a thesis result.
GRASP_STEM = 'recording_20260909_000024'
# Frame choice: DECISIONS.md D-068 (right hand on the cube, clean offset
# update, same frame as the page 25 poster in media/provenance/matched_evidence.json).
GRASP_FRAME = 630
# Thesis swap S: MappedMarker keeps the marker origin and exchanges Y and Z,
# so its Y follows the marker-face normal (anim/axes_inputs.py S).
MAPPED_SWAP = np.array([[1., 0., 0.], [0., 0., 1.], [0., 1., 0.]])
# 45 mm printed cube marker (AGENTS.md marker size; the size the pinned
# aruco_raw_scaled table was rescaled with, video1_overlay.py MARKERS).
CUBE_MARKER_M = 0.045
# Cube side: eval/output/scene_calibration_r7c.json scene_geometry.object_cube_size_m.
GRASP_CALIBRATION = 'eval/output/scene_calibration_r7c.json'
# Image crop around the hand and cube (640x480 source pixels); editorial.
GRASP_CROP = (125, 145, 395, 400)
GRASP_PHOTO_BOX = (20, 96, 720, 757)


def grasp_inputs():
    import pandas as pd
    paths = {'landmarks': REPO/f'v1/mediapipe/output/{GRASP_STEM}_landmarks_raw.csv',
             'landmarks_meta': REPO/f'v1/mediapipe/output/{GRASP_STEM}_landmarks_raw.meta.json',
             'marker_poses': REPO/f'eval/output/{GRASP_STEM}_aruco_raw_scaled.csv',
             'failure_mask': REPO/'eval/output/recovery_r7/failure_mask.csv',
             'rgb_provenance': HERE/'media/provenance/axes_r7_rgb.json',
             'matched_evidence': HERE/'media/provenance/matched_evidence.json',
             'calibration': REPO/GRASP_CALIBRATION}
    n = GRASP_FRAME
    lm = pd.read_csv(paths['landmarks']).set_index('frame').loc[n]
    ar = pd.read_csv(paths['marker_poses']).set_index('frame').loc[n]
    fm = pd.read_csv(paths['failure_mask']).set_index('frame').loc[n]
    intrinsics = json.loads(paths['landmarks_meta'].read_text())['color_intrinsics']
    if any(abs(c) > 0 for c in intrinsics['coeffs']):
        raise ValueError('Pinhole drawing assumes zero distortion coefficients.')
    # Same acceptance rule as VIDEO-1: pose present, detector flag 0, arm not masked.
    if int(lm['has_pose']) != 1 or int(lm['right_wrist_src']) != 0 or int(fm['fail_arm_R']) != 0:
        raise ValueError('Right wrist is not a clean measurement on the grasp frame.')
    if int(ar['m1_detected']) != 1:
        raise ValueError('Cube marker is not detected on the grasp frame.')
    rotation = np.array([[ar[f'm1_r{i}{j}'] for j in (1, 2, 3)] for i in (1, 2, 3)], float)
    origin = np.array([ar['m1_tx'], ar['m1_ty'], ar['m1_tz']], float)
    wrist = np.array([lm['right_wrist_x'], lm['right_wrist_y'], lm['right_wrist_z']], float)
    mapped = rotation@MAPPED_SWAP
    displacement = wrist-origin
    local = mapped.T@displacement            # Eq. 5.2: h = R^T (p_wr - o)
    # RGB: the bag-decoded cache is accepted only when its bytes match the
    # committed extraction record; a verified copy is kept beside the figure.
    rgb_record = {r['frame']: r for r in json.loads(paths['rgb_provenance'].read_text())['frames']}[n]
    copied = OUT/f'grasp_source_r7_f{n:05d}.png'
    if not copied.exists():
        shutil.copyfile(Path('/tmp/defense_matched_r7')/f'frame_{n:04d}.png', copied)
    if sha(copied) != rgb_record['sha256']:
        raise ValueError('Grasp source RGB does not match the recorded bag decode.')
    evidence = {r['frame']: r for r in json.loads(paths['matched_evidence'].read_text())['grasp']['records']}[n]
    pipeline = np.array(evidence['object_local_observation_m'], float)
    cube = float(json.loads(paths['calibration'].read_text())['scene_geometry']['object_cube_size_m'])
    return {'paths': paths, 'intrinsics': intrinsics, 'rotation': rotation, 'origin': origin,
            'wrist': wrist, 'mapped': mapped, 'displacement': displacement, 'local': local,
            'rgb': copied, 'rgb_record': rgb_record, 'pipeline_local': pipeline, 'cube': cube,
            'reproj_px': float(ar['m1_reproj_px']), 'time_s': float(lm['time_s'])}


def boxed_label(draw, lines, xy, *, size=40, fill=WHITE):
    font = ImageFont.truetype(FONT, size)
    x, y = xy
    boxes = [draw.textbbox((x, y+i*(size+8)), line, font=font) for i, line in enumerate(lines)]
    x0 = min(b[0] for b in boxes)-12; y0 = min(b[1] for b in boxes)-10
    x1 = max(b[2] for b in boxes)+12; y1 = max(b[3] for b in boxes)+10
    draw.rectangle((x0, y0, x1, y1), fill='#000000')
    return [label(draw, line, (x, y+i*(size+8)), size=size, fill=fill) for i, line in enumerate(lines)]


def grasp_offset():
    data = grasp_inputs()
    k = data['intrinsics']
    im, draw = canvas()
    # Left panel: recorded frame, cropped and scaled without colour change.
    c0, r0, c1, r1 = GRASP_CROP
    x0, y0, x1, y1 = GRASP_PHOTO_BOX
    scale = (x1-x0)/(c1-c0)
    if abs((y1-y0)/(r1-r0)-scale) > .01:
        raise ValueError('Grasp crop and panel box must keep the pixel aspect.')
    with Image.open(data['rgb']) as source:
        photo = source.convert('RGB').crop(GRASP_CROP).resize((x1-x0, y1-y0), Image.Resampling.LANCZOS)
    im.paste(photo, (x0, y0))
    project = make_pinhole_projector(k, scale=scale, offset=(x0-c0*scale, y0-r0*scale))
    label(draw, f'Recorded frame {GRASP_FRAME}', (x0, 24), size=44)
    face = [data['origin']+data['rotation']@np.array([sx, sy, 0.])*CUBE_MARKER_M/2
            for sx, sy in [(-1, 1), (1, 1), (1, -1), (-1, -1)]]
    draw.polygon([tuple(project(v)) for v in face], outline=GRAY, width=3)
    o_px, w_px = project(data['origin']), project(data['wrist'])
    arrow(draw, o_px, w_px, WHITE, 6)
    frames = [triad(draw, data['origin'], data['mapped'], project, CUBE_MARKER_M, 'MappedMarker',
                    role='cube marker origin o_k; measured pose')]
    dot(draw, o_px, 7)
    dot(draw, w_px, 11)
    draw.ellipse((w_px[0]-11, w_px[1]-11, w_px[0]+11, w_px[1]+11), outline='#000000', width=2)
    # Label box sits in the image's upper-left, clear of the arrow and triad.
    left_labels = boxed_label(draw, ['Scene displacement', 'p_wr - o_k'], (x0+24, y0+24))
    if left_labels[0][2]+12 >= min(o_px[0], w_px[0])-20 and left_labels[-1][3]+10 >= w_px[1]-20:
        raise ValueError('Displacement label would cover the arrow.')
    left_labels.append(label(draw, 'White point: measured wrist L16', (x0, 790), size=40))
    left_labels.append(label(draw, 'Axes: cube marker at o_k', (x0, 850), size=40))
    draw.line((737, 96, 737, 900), fill=RULE, width=2)
    # Right panel: the same vector in MappedMarker coordinates, cube drawn
    # axis-aligned with the marker face (normal +Y) toward the viewer.
    label(draw, 'MappedMarker coordinates', (770, 24), size=44)
    toward = np.array([.42, .30, .86]); toward /= np.linalg.norm(toward)
    right = np.cross([0., 1., 0.], toward); right /= np.linalg.norm(right)
    up = np.cross(toward, right)
    # Display space is x right, y up, z toward the viewer; MappedMarker X->x, Z->y, Y->z.
    to_display = np.array([[1., 0., 0.], [0., 0., 1.], [0., 1., 0.]])
    view = np.stack([right, up, toward])@to_display
    local = data['local']
    model = make_orthographic_projector(view, local/2, 2350, (1075, 470))
    half = data['cube']/2
    corner = lambda x, y, z: np.array([x*half, (y-1)*half, z*half])
    for face_pts, shade in [([corner(-1, 1, -1), corner(1, 1, -1), corner(1, 1, 1), corner(-1, 1, 1)], '#262626'),
                            ([corner(1, 1, -1), corner(1, -1, -1), corner(1, -1, 1), corner(1, 1, 1)], '#1A1A1A'),
                            ([corner(-1, 1, 1), corner(1, 1, 1), corner(1, -1, 1), corner(-1, -1, 1)], '#303030')]:
        draw.polygon([tuple(model(v)) for v in face_pts], fill=shade, outline=GRAY, width=3)
    marker = [np.array([sx, 0., sz])*CUBE_MARKER_M/2 for sx, sz in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
    draw.polygon([tuple(model(v)) for v in marker], fill='#0A0A0A', outline=WHITE, width=2)
    frames.append(triad(draw, np.zeros(3), np.eye(3), model, .07, 'MappedMarker',
                        role='same cube marker origin; object-local basis'))
    arrow(draw, model(np.zeros(3)), model(local), WHITE, 6)
    dot(draw, model(np.zeros(3)), 7)
    dot(draw, model(local), 11)
    tip = model(local)
    right_labels = boxed_label(draw, ['h_k (object-local)'], (tip[0]-330, tip[1]-78))
    cm = local*100
    for i, (name, value) in enumerate(zip('XYZ', cm)):
        right_labels.append(label(draw, f'{name}  {value:+.1f} cm', (790, 790+i*56), size=42,
                                  fill=AXIS_COLORS[name]))
    for bounds in left_labels:
        if bounds[2] > 730:
            raise ValueError(f'Left-panel text crosses the divider: {bounds}')
    # The slide caption states 'same displacement, two coordinate descriptions'.
    draw.line((20, 1010, 1420, 1010), fill=RULE, width=2)
    label(draw, f'Measured on R7 frame {GRASP_FRAME}, illustrative', (20, 1040), size=40, fill=GRAY)
    label(draw, 'Single-frame values; not a thesis result', (20, 1104), size=40, fill=GRAY)
    paths = data['paths']
    save('grasp_offset', im, frames, 'Thesis V9 Section 5.3, Eq. 5.2; Section 6.2, Eq. 6.1',
         classification='explanatory figure drawn on one recorded frame; values measured on that frame and illustrative, not a thesis result',
         recording=GRASP_STEM, source_frame=GRASP_FRAME, source_time_s=data['time_s'],
         source_tables={key: {'path': str(p.relative_to(REPO)), 'sha256': sha(p)} for key, p in paths.items()},
         source_rgb={'delivered_source': str(data['rgb'].relative_to(REPO)), 'sha256': sha(data['rgb']),
                     'bag_decode_record': data['rgb_record'], 'crop_px': list(GRASP_CROP),
                     'panel_box_px': list(GRASP_PHOTO_BOX), 'colour_adjustments': 'none'},
         intrinsics=k, reference_coordinates='left: Camera (recorded image); right: MappedMarker',
         marker_face='MappedMarker X/Z plane; positive Y normal toward the camera',
         mapped_swap_S=MAPPED_SWAP.tolist(), cube_marker_size_m=CUBE_MARKER_M, cube_size_m=data['cube'],
         marker_reprojection_px=data['reproj_px'],
         marker_origin_camera_m=data['origin'].tolist(), wrist_camera_m=data['wrist'].tolist(),
         marker_rotation_camera=data['rotation'].tolist(),
         displacement_camera_m=data['displacement'].tolist(),
         offset_mappedmarker_m=local.tolist(), offset_mappedmarker_printed_cm=[round(float(v), 1) for v in cm],
         offset_formula='h_k = (R_cam_marker S)^T (p_wr - o_k); invariant to the rigid change from Camera to Scene',
         pipeline_offset_mappedmarker_m=data['pipeline_local'].tolist(),
         pipeline_offset_source='media/provenance/matched_evidence.json grasp record, frozen filtered Scene inputs',
         pipeline_difference_cm=float(np.linalg.norm(data['pipeline_local']-local)*100),
         label_bounds={'left': left_labels, 'right': right_labels},
         geometry='Measured on one frame and illustrative. Raw per-frame inputs (VIDEO-1 tables); the thesis estimate is the clean-sample mean, not this single observation.')


def wrist_target():
    im, draw = canvas()
    frames=[]
    for top, name, basis, explain in [
            (0, 'Scene', np.eye(3), 'Object pose + stored local offset'),
            (650, 'Camera-prime', ry(-20)@rx(25), 'One common arm-solve reference')]:
        project=make_orthographic_projector(view_matrix(25,12), np.zeros(3), 660, (330,top+320))
        frames.append(triad(draw,np.zeros(3),basis,project,.24,name,
                            role='basis legend; actual origin is outside the local construction'))
        label(draw,name+' directions',(60,top+40))
        label(draw,explain,(570,top+245),size=43)
        label(draw,'Inferred wrist target',(570,top+330),size=43)
    arrow(draw,(330,485),(330,620))
    label(draw,'Undo the fixed Scene mapping',(490,520),size=43)
    label(draw,'Direction keys; origins outside view',(440,1110),size=43,fill=GRAY)
    save('wrist_target',im,frames,'Thesis V9 Section 5.4, Eq. 5.7 and p. 58; Sections 6.2, 6.4',
         reference_coordinates='Separate explanatory views; no measured calibration rotation is implied.',
         point_transform='Undo floor translation, G, S and calibrated camera relation, then apply F.',
         target_status='inferred constraint, not a new wrist observation')


def recovery(key, selected):
    im,draw=canvas()
    label(draw,'Illustrative reachable geometry',(55,28))
    shoulder=np.zeros(3); wrist=np.array([.58,0.,0.]); l1,l2=.38,.34
    d=(l1*l1+.58*.58-l2*l2)/(2*.58)
    radius=math.sqrt(l1*l1-d*d); centre=np.array([d,0.,0.])
    project=make_orthographic_projector(view_matrix(14,12), [.3,0.,0.], 1620,(740,600))
    ring=[centre+radius*np.array([0.,math.cos(t),math.sin(t)]) for t in np.linspace(0,2*math.pi,200)]
    draw.line([tuple(project(v)) for v in ring],fill=GRAY,width=4)
    draw.line([tuple(project(shoulder)),tuple(project(wrist))],fill=RULE,width=3)
    elbow=centre+radius*np.array([0.,.8,.6])
    draw.line([tuple(project(shoulder)),tuple(project(elbow)),tuple(project(wrist))],fill=WHITE,width=5)
    for p in [shoulder,wrist,elbow]:dot(draw,project(p),9)
    if selected:
        arrow(draw,project(centre),project(elbow),WHITE,5)
        label(draw,'Prior-selected elbow',(540,125))
    else:label(draw,'One possible elbow',(560,125))
    label(draw,'Shoulder',(60,765))
    label(draw,'Wrist target',(1030,765))
    label(draw,'Circle of valid elbows',(615,1020))
    legend=make_orthographic_projector(view_matrix(25,12),np.zeros(3),470,(245,1010))
    frames=[triad(draw,np.zeros(3),np.eye(3),legend,.22,'Camera-prime',
                   role='basis legend; optical origin outside this close-up')]
    label(draw,'Camera-prime directions',(50,1110),size=40,fill=GRAY)
    save(key,im,frames,'Thesis V9 Section 5.5, Eqs. 5.8-5.12',
         reference_coordinates='Camera-prime; legend does not relocate its optical origin',
         geometry='Illustrative lengths and reachable target, not recording measurements.',
         endpoint_distance=.58,upper_arm=l1,forearm=l2,
         length_residuals=[float(np.linalg.norm(elbow-shoulder)-l1),float(np.linalg.norm(elbow-wrist)-l2)],
         selected_by_prior=selected)


def rig_frames():
    im,draw=canvas();frames=[]
    rows=[('Scene anchor',np.eye(3),'Camera-prime into Scene'),
          ('Segment chain',ry(-25)@rx(15),'Root, shoulder, elbow'),
          ('Bone rest axes',ry(-20)@rx(35),'Captured constant; rig-specific')]
    for i,(name,basis,explain) in enumerate(rows):
        top=i*400
        label(draw,name,(60,top+25))
        project=make_orthographic_projector(view_matrix(25,12),np.zeros(3),730,(330,top+275))
        frames.append(triad(draw,np.zeros(3),basis,project,.18,name,
                            role='illustrative orientation factor; origins are not equated'))
        label(draw,explain,(590,top+186),size=44)
        if i<2:draw.line((55,top+390,1385,top+390),fill=RULE,width=2)
    save('rig_frames',im,frames,'Thesis V9 Section 6.3, Eqs. 6.4-6.5, p. 75',
         geometry='Separate illustrative orientation factors; no measured rig bone rest rotation claimed.',
         factor_order='Scene anchor on left; kinematic segment rotation; captured bone rest rotation on right')


def anchor_factorization():
    im,draw=canvas();frames=[]
    rotation=ry(-30)@rx(25)
    swap=np.array([[1.,0.,0.],[0.,0.,1.],[0.,1.,0.]])
    anchor=rx(35)@ry(15)
    object_mapped=swap@rotation@swap
    body_anchored=anchor@rotation
    for top,title,left,right,result,explain in [
            (0,'Object orientation','Object in World (RH)','MappedMarker in Unity (LH)',
             object_mapped,'Coordinate views: swap both bases'),
            (600,'Body orientation','Segment in Camera-prime (LH)','Segment in Scene (LH)',
             body_anchored,'Illustrative proper anchor A; multiply on the left')]:
        label(draw,title,(55,top+20))
        for x,basis,name in [(300,rotation,left),(1080,result,right)]:
            project=make_orthographic_projector(view_matrix(25,12),np.zeros(3),630,(x,top+275))
            frames.append(triad(draw,np.zeros(3),basis,project,.22,name,role='separate explanatory basis relation'))
        arrow(draw,(590,top+265),(825,top+265))
        label(draw,left,(55,top+432),size=40)
        label(draw,right,(780,top+432),size=40)
        label(draw,explain,(55,top+518),size=44,fill=GRAY)
        if not top:draw.line((55,590,1385,590),fill=RULE,width=2)
    save('anchor_factorization',im,frames,'Thesis V9 Section 6.2, Eqs. 6.1-6.3; Section 6.3, Eq. 6.5',
         geometry='Separate coordinate views of exact products using an illustrative nontrivial R and arbitrary proper anchor A; neither matrix is a recording calibration.',
         illustrative_rotation_R=rotation.tolist(),axis_swap_S=swap.tolist(),
         object_product_S_R_S=object_mapped.tolist(),illustrative_proper_anchor_A=anchor.tolist(),
         body_product_A_R=body_anchored.tolist(),
         handedness={'World':'right','Object':'right','Unity':'left','MappedMarker':'left',
                     'Camera-prime':'left','Scene':'left','body_segment':'left'})


FIGURES = {'camera_frames': camera_frames, 'tpose_reference': tpose_reference,
           'scene_mapping': scene_mapping, 'object_frames': object_frames,
           'grasp_offset': grasp_offset, 'wrist_target': wrist_target,
           'elbow_constraints': lambda: recovery('elbow_constraints', False),
           'elbow_prior': lambda: recovery('elbow_prior', True),
           'rig_frames': rig_frames, 'anchor_factorization': anchor_factorization}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--only', choices=sorted(FIGURES), action='append',
                        help='Regenerate only these figures and replace their records in the existing manifest.')
    args = parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    keys = args.only or list(FIGURES)
    for key in keys:
        FIGURES[key]()
    assets = RECORDS
    if args.only:
        previous = json.loads((OUT/'manifest.json').read_text())['assets']
        fresh = {r['key']: r for r in RECORDS}
        assets = [fresh.pop(r['key'], r) for r in previous]+list(fresh.values())
    source=REPO/'writing/v9/Thesis_V9.pdf'
    report={'status':'PASS','generator':str(Path(__file__).resolve().relative_to(REPO)),
            'generator_sha256':sha(__file__),'source_pdf':str(source.relative_to(REPO)),
            'source_pdf_sha256':sha(source),'axis_renderer':'presentation/defense_2026/anim/coordinate_axes.py',
            'axis_renderer_sha256':sha(HERE/'anim/coordinate_axes.py'),
            'axis_colors':AXIS_COLORS,'assets':assets,
            'scope':'Static instructional geometry; grasp_offset is drawn on one recorded R7 frame with values measured on that frame, illustrative only. Recorded data and numerical results are unchanged.'}
    (OUT/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'Wrote {len(RECORDS)} coordinate figures and their provenance manifest.')


if __name__=='__main__':main()
