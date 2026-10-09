#!/usr/bin/env python3
"""One right-column layout for the kinematics pages 13-20.

2026-09-24 round 2: pages 13-16 are now the four merged pages of the
unified_four collection (torso frame, shoulder swing, shoulder twist, elbow).
Their model panel draws the parent frame dim and the rotated frame bright at
the page's joint, with a grey 3D arc carrying the parent axis onto the
rotated axis (rotation_pair, compose). Pages 17-20 (bank_kinematics.py) keep
their earlier kinds and pixels.

Top: the exact inference RGB frame with the landmark overlay. Bottom-left:
the same Camera-prime model points projected with the recording's own
pinhole (after undoing the Camera/Camera-prime reflection), on black, so the
lower skeleton is congruent with the overlay up to one fixed per-clip
similarity (uniform scale plus offset). Bottom-right: a fixed-geometry 2D
plane with the page's quantity.

Every panel, label slot and font size is constant across the eight pages.
Only the per-clip model scale/offset is fitted, once per clip, from all of
its selected frames; it never follows individual frames.
"""
from __future__ import annotations

import hashlib

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from coordinate_axes import (AXIS_COLORS, CAMERA_TO_CAMERA_PRIME as F,
                             draw_triad, make_pinhole_projector, overlay_mask)

W, H, FPS = 1440, 1200, 30
CAMERA_RECT = (336, 64, 1104, 640)
CAMERA_SCALE = 1.2
SOURCE_SIZE = (640, 480)
MODEL_RECT = (20, 700, 800, 1190)
MODEL_FIT = (40, 800, 780, 1175)
PLANE_RECT = (830, 700, 1420, 1190)
PLANE_ORIGIN = np.array([1010., 965.])
PLANE_UNIT_PX = 125.
SIDE_X = 1232
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
SMALL = 28
PANEL_HEADING = 30
FOCUS_WHITE = '#FFFFFF'
FADED_WHITE = '#CFCFCF'
GREY_EDGE = '#656565'
ARC_GREY = '#C8C8C8'
BORDER = '#3A3A3A'
ROOT_AXIS_M = .15
JOINT_AXIS_M = .075
REFERENCE_AXIS_M = .075
REFERENCE_DIM = .55
# Merged pages (editorial drawing sizes, chosen by viewing frames at slide
# size; DECISIONS.md D-090): parent/rotated triad axis length, arc radius,
# model fit box below the three model-panel text rows, and the widths of the
# focus bone and of the bright X axis drawn on top of it.
PAIR_AXIS_M = .12
ARC_M = .08
MODEL_FIT_FOUR = (40, 830, 780, 1175)
# Merged pages draw the model on a layer clipped to this box (inside the
# panel border, below the three text rows), so the arm close-up of pages
# 14-16 may run past it without touching the other panels.
MODEL_CLIP = (22, 826, 798, 1188)
ARM_NAMES = ('right_shoulder', 'right_elbow', 'right_wrist')
FOUR_FOCUS_WIDTH = {'model': 12, 'camera': 8}
FOUR_X_WIDTH = {'model': 4, 'camera': 3}
NAMES = ['left_hip', 'right_hip', 'left_shoulder', 'right_shoulder',
         'left_elbow', 'right_elbow', 'left_wrist', 'right_wrist']
EDGES = [('left_hip', 'right_hip'), ('left_hip', 'left_shoulder'),
         ('right_hip', 'right_shoulder'), ('left_shoulder', 'right_shoulder'),
         ('left_shoulder', 'left_elbow'), ('left_elbow', 'left_wrist'),
         ('right_shoulder', 'right_elbow'), ('right_elbow', 'right_wrist')]
UPPER = ('right_shoulder', 'right_elbow')
FORE = ('right_elbow', 'right_wrist')
# Pages 13-16: the four merged pages (unified_four). Pages 17-20: the
# bank_revision_v2 films (bank_kinematics.py), unchanged.
KINDS = {
    13: 'torso_frame', 14: 'swing_rotation', 15: 'twist_rotation', 16: 'elbow_rotation',
    17: 'shoulder_swing', 18: 'shoulder_twist', 19: 'elbow_angles', 20: 'observability'}
FOUR_KINDS = ('torso_frame', 'swing_rotation', 'twist_rotation', 'elbow_rotation')
# Which earlier bottom-right plane each merged page reuses.
PLANE_KIND = {'swing_rotation': 'shoulder_swing', 'twist_rotation': 'shoulder_twist',
              'elbow_rotation': 'elbow_angles'}
TITLES = {13: 'Torso frame', 14: 'Shoulder swing', 15: 'Shoulder twist', 16: 'Elbow',
          17: 'Shoulder swing',
          18: 'Forearm plane and shoulder twist', 19: 'Elbow angles',
          20: 'Straight-arm twist observability'}
ORIGIN_TEXT = {13: 'Ring: L24 origin; torso L11 L12 L23 L24',
               14: 'Arm close-up. Dim: root at L12; bright: swing',
               15: 'Arm close-up. Dim: swing at L14; bright: arm',
               16: 'Arm close-up. Dim: arm at L14; bright: elbow',
               17: 'Ring: elbow, swing basis; dim: L12',
               18: 'Ring: elbow, swing basis',
               19: 'Ring: L14, elbow parent',
               20: 'Ring: elbow, swing basis'}


def font(size):
    return ImageFont.truetype(FONT, size)


def label(draw, xy, text, size=SMALL, fill='white', anchor=None, inside=None):
    box = draw.textbbox(xy, text, font=font(size), anchor=anchor)
    assert box[0] >= 0 and box[1] >= 0 and box[2] <= W and box[3] <= H, (text, box)
    if inside is not None:
        assert (box[0] >= inside[0] and box[1] >= inside[1] and
                box[2] <= inside[2] and box[3] <= inside[3]), (text, box, inside)
    draw.text(xy, text, font=font(size), fill=fill, anchor=anchor)
    return list(box)


def arrow(draw, a, b, fill='white', width=6):
    a, b = np.asarray(a, float), np.asarray(b, float)
    draw.line([tuple(a), tuple(b)], fill=fill, width=width)
    delta = b - a
    length = np.linalg.norm(delta)
    if length > 2:
        u = delta / length
        n = np.array([-u[1], u[0]])
        size = min(18., length * .25)
        draw.polygon([tuple(b), tuple(b - size * u + size * .45 * n),
                      tuple(b - size * u - size * .45 * n)], fill=fill)


def signed_arc(draw, origin, radius, start_deg, sweep_deg):
    """Screen-space arc; angles in screen coordinates (y down)."""
    count = max(2, int(abs(sweep_deg) / 3) + 1)
    angles = np.radians(start_deg + np.linspace(0, sweep_deg, count))
    points = np.asarray(origin) + radius * np.column_stack([np.cos(angles), np.sin(angles)])
    draw.line([tuple(p) for p in points], fill=ARC_GREY, width=3)
    if abs(sweep_deg) > 2:
        arrow(draw, points[-2], points[-1], ARC_GREY, 3)
    return points[-1].tolist()


def edge_colors(page):
    """Focus edge bright white, the other right-arm edge faded white, rest grey."""
    colors = {edge: GREY_EDGE for edge in EDGES}
    kind = KINDS[page]
    if kind in ('torso_axes', 'torso_transform', 'root_angles', 'torso_frame'):
        # Eqs. 3.7-3.8: the hip line and the L24-L12 vector define the basis.
        colors[('left_hip', 'right_hip')] = FOCUS_WHITE
        colors[('right_hip', 'right_shoulder')] = FOCUS_WHITE
    elif kind in ('arm_direction', 'shoulder_swing', 'swing_rotation'):
        colors[UPPER] = FOCUS_WHITE
        colors[FORE] = FADED_WHITE
    else:
        colors[FORE] = FOCUS_WHITE
        colors[UPPER] = FADED_WHITE
    return colors


def active_triads(page, row, points):
    """(origin, basis, length, dimmed) for the page's model frames."""
    root = np.asarray(row['root_basis'])
    swing = np.asarray(row['swing_basis'])
    arm = np.asarray(row['upper_arm_basis'])
    kind = KINDS[page]
    if kind in ('torso_axes', 'torso_transform', 'root_angles'):
        return [(points['right_hip'], root, ROOT_AXIS_M)]
    if kind == 'arm_direction':
        return [(points['right_shoulder'], root, JOINT_AXIS_M)]
    if kind == 'elbow_angles':
        return [(points['right_elbow'], arm, JOINT_AXIS_M)]
    return [(points['right_elbow'], swing, JOINT_AXIS_M)]


def reference_triads(page, row, points):
    """Dimmed reference frames drawn only in the model panel."""
    root = np.asarray(row['root_basis'])
    if KINDS[page] == 'torso_transform':
        return [(points['right_shoulder'], root, REFERENCE_AXIS_M),
                (points['left_shoulder'], root, REFERENCE_AXIS_M)]
    if KINDS[page] == 'shoulder_swing':
        return [(points['right_shoulder'], root, REFERENCE_AXIS_M)]
    return []


def triad_points(page, row, points):
    if KINDS[page] in FOUR_KINDS:
        return four_points(page, row, points)
    out = []
    for origin, basis, length in active_triads(page, row, points) + reference_triads(page, row, points):
        out.append(np.vstack([origin, origin + length * np.asarray(basis).T]))
    return np.vstack(out)


def source_pixels(intrinsics, xyz):
    """Pixel coordinates in the 640x480 recorded image for Camera-prime points."""
    return make_pinhole_projector(intrinsics, source_to_camera=F)(np.asarray(xyz, float))


def fit_model_view(page, records, intrinsics):
    """One fixed similarity for the whole clip, fitted to every selected frame."""
    xy = []
    # Merged pages 14-16 fit the right arm and its frames only (arm close-up);
    # every other page fits the whole eight-point skeleton.
    close_up = KINDS[page] in FOUR_KINDS and KINDS[page] != 'torso_frame'
    fitted = ARM_NAMES if close_up else NAMES
    for row in records.values():
        points = {k: np.asarray(v) for k, v in row['points_camera_prime_m'].items()}
        xy.append(source_pixels(intrinsics, np.vstack([points[n] for n in fitted])))
        xy.append(source_pixels(intrinsics, triad_points(page, row, points)))
    xy = np.vstack(xy)
    low, high = xy.min(axis=0), xy.max(axis=0)
    x0, y0, x1, y1 = MODEL_FIT_FOUR if KINDS[page] in FOUR_KINDS else MODEL_FIT
    # 30 px margin on each side leaves room for axis letters.
    scale = float(min((x1 - x0 - 60) / (high[0] - low[0]), (y1 - y0 - 60) / (high[1] - low[1])))
    center_src = (low + high) / 2
    offset = np.array([(x0 + x1) / 2, (y0 + y1) / 2]) - scale * center_src
    return {'projection': 'recording pinhole after Camera-prime reflection, then uniform scale and offset',
            'scale_px_per_source_px': scale, 'offset_px': offset.tolist(),
            'fitted_source_pixel_bounds': [low.tolist(), high.tolist()],
            'fit_rect': list(MODEL_FIT_FOUR if KINDS[page] in FOUR_KINDS else MODEL_FIT),
            'fitted_points': list(fitted) + ['page frames and arcs'],
            'clip_rect': list(MODEL_CLIP) if KINDS[page] in FOUR_KINDS else None}


def draw_skeleton(draw, points, project, colors, dot=6, focus_width=6):
    for a, b in EDGES:
        color = colors[(a, b)]
        width = (focus_width if color == FOCUS_WHITE else 6) if color != GREY_EDGE else 4
        draw.line([tuple(project(points[a])), tuple(project(points[b]))], fill=color, width=width)
    for name in NAMES:
        u, v = project(points[name])
        draw.ellipse((u - dot, v - dot, u + dot, v + dot), fill='white')


def dim(color, factor=REFERENCE_DIM):
    return tuple(round(int(color[j:j + 2], 16) * factor) for j in (1, 3, 5))


def dim_triad(draw, origin, basis, project, length):
    screen = project(np.vstack([origin, origin + length * np.asarray(basis).T]))
    for i, name in enumerate('XYZ'):
        arrow(draw, screen[0], screen[i + 1], dim(AXIS_COLORS[name]), 3)
    return np.asarray(screen).tolist()


def plane_axes(draw, h_name, v_name, extent, h_color=None, v_color=None, h_text=None, v_text=None):
    o = PLANE_ORIGIN
    h_color = h_color or AXIS_COLORS[h_name]
    v_color = v_color or AXIS_COLORS[v_name]
    arrow(draw, o + [-150, 0], o + [170, 0], h_color, 4)
    arrow(draw, o + [0, 150], o + [0, -150], v_color, 4)
    boxes = [label(draw, tuple(o + [178, -18]), h_text or h_name, 36, h_color, inside=PLANE_RECT),
             label(draw, tuple(o + [-48, -186]), v_text or v_name, 36, v_color, inside=PLANE_RECT)]
    for sign in (-1, 1):
        tx = o + [sign * PLANE_UNIT_PX, 0]
        ty = o + [0, -sign * PLANE_UNIT_PX]
        draw.line([tuple(tx + [0, -6]), tuple(tx + [0, 6])], fill='white', width=2)
        draw.line([tuple(ty + [-6, 0]), tuple(ty + [6, 0])], fill='white', width=2)
        tick = f'{sign * extent:+.1f}'
        boxes.append(label(draw, tuple(tx + [-26, 12]), tick, SMALL, inside=PLANE_RECT))
        boxes.append(label(draw, tuple(ty + [12, -17]), tick, SMALL, inside=PLANE_RECT))
    boxes.append(label(draw, tuple(o + [-30, 10]), '0', SMALL, inside=PLANE_RECT))
    return boxes


def plane_vector(draw, horizontal, vertical, extent, fill='white', width=7):
    o = PLANE_ORIGIN
    unit = PLANE_UNIT_PX / extent
    tip = o + [horizontal * unit, -vertical * unit]
    arrow(draw, o, tip, fill, width)
    draw.ellipse((tip[0] - 6, tip[1] - 6, tip[0] + 6, tip[1] + 6), fill=fill)
    return tip


def plane_panel(draw, page, row):
    """Bottom-right quantity panel. Returns audit data and label boxes."""
    page_kind = KINDS[page]
    kind = PLANE_KIND.get(page_kind, page_kind)
    points = {k: np.asarray(v) for k, v in row['points_camera_prime_m'].items()}
    root = np.asarray(row['root_basis'])
    boxes = []
    arc = None
    side = []
    lines = ['', '']
    extent = 1.0
    out = {}
    if kind in ('torso_axes', 'torso_transform', 'root_angles', 'torso_frame'):
        heading = "Top view: Camera' X-Z plane"
        normal, normal_color = "Camera' Y: normal to this view", '#9A9A9A'
        boxes += plane_axes(draw, 'X', 'Z', extent, '#9A9A9A', '#9A9A9A', 'x', 'z')
        x_hat, z_hat = root[:, 0], root[:, 2]
        x_tip = plane_vector(draw, x_hat[0], x_hat[2], extent, AXIS_COLORS['X'], 7)
        z_tip = plane_vector(draw, z_hat[0], z_hat[2], extent, AXIS_COLORS['Z'], 7)
        side = [('Red: X-hat', AXIS_COLORS['X']), ('Blue: Z-hat', AXIS_COLORS['Z'])]
        out.update({'x_hat_xz': [float(x_hat[0]), float(x_hat[2])],
                    'z_hat_xz': [float(z_hat[0]), float(z_hat[2])],
                    'x_tip_px': x_tip.tolist(), 'z_tip_px': z_tip.tolist()})
        if kind == 'torso_axes':
            lines = ['Torso axes at L24, seen from above', '']
        elif kind == 'torso_frame':
            # Merged torso page: top view without an arc; root Euler readout.
            lines = ['Root angles (deg):',
                     f'x = {row["root_ex"]:.1f}, y = {row["root_ey"]:.1f}, z = {row["root_ez"]:.1f}']
        elif kind == 'torso_transform':
            p = points['right_hip']
            lines = ["L24 origin in Camera' (m):",
                     f'x = {p[0]:+.2f}, y = {p[1]:+.2f}, z = {p[2]:+.2f}']
            out['origin_m'] = p.tolist()
        else:
            # atan2(Z-hat x, Z-hat z) is exactly the Unity y angle (root_frame.py
            # euler_unity_zxy), so the arc from +z to the projected Z-hat is ey.
            arc = signed_arc(draw, PLANE_ORIGIN, 70, -90., row['root_ey'])
            side += [('Grey arc:', ARC_GREY), ('root y', ARC_GREY)]
            lines = ['Root angles (deg):',
                     f'x = {row["root_ex"]:.1f}, y = {row["root_ey"]:.1f}, z = {row["root_ez"]:.1f}']
            out['signed_angle_deg'] = float(row['root_ey'])
    elif kind in ('arm_direction', 'shoulder_swing'):
        upper = points['right_elbow'] - points['right_shoulder']
        local = root.T @ (upper / np.linalg.norm(upper))
        side = [('White: unit', 'white'), ('upper arm', 'white')]
        if kind == 'arm_direction':
            heading = 'Upper arm in L12: X-Y plane'
            normal, normal_color = 'Z: normal to this plane', AXIS_COLORS['Z']
            boxes += plane_axes(draw, 'X', 'Y', extent)
            tip = plane_vector(draw, local[0], local[1], extent)
            lines = ['Unit upper arm in L12:',
                     f'x = {local[0]:+.2f}, y = {local[1]:+.2f}, z = {local[2]:+.2f}']
            out.update({'horizontal_component': float(local[0]), 'vertical_component': float(local[1])})
        else:
            heading = 'Upper arm in L12: X-Z plane'
            normal, normal_color = 'Y: normal to this plane', AXIS_COLORS['Y']
            boxes += plane_axes(draw, 'X', 'Z', extent)
            tip = plane_vector(draw, local[0], local[2], extent)
            # Screen angle atan2(-a_z, a_x) equals swing y (Eq. 3.21).
            arc = signed_arc(draw, PLANE_ORIGIN, 70, 0., row['sh_y'])
            side += [('Grey arc:', ARC_GREY), ('swing y', ARC_GREY)]
            lines = [f'Swing y = {row["sh_y"]:.1f} deg (azimuth)',
                     f'Swing z = {row["sh_z"]:.1f} deg (elevation)']
            out.update({'horizontal_component': float(local[0]), 'vertical_component': float(local[2]),
                        'signed_angle_deg': float(row['sh_y'])})
        out.update({'unit_upper_arm_local': local.tolist(), 'projected_tip_px': tip.tolist()})
    else:
        fore = points['right_wrist'] - points['right_elbow']
        fore = fore / np.linalg.norm(fore)
        side = [('White: unit', 'white'), ('forearm', 'white')]
        if kind == 'elbow_angles':
            local = np.asarray(row['upper_arm_basis']).T @ fore
            h, v, h_name, v_name = float(local[0]), float(local[2]), 'X', 'Z'
            degrees = row['el_y']
            heading = 'L14 forearm direction: X-Z plane'
            normal, normal_color = 'Y: plane normal', AXIS_COLORS['Y']
            lines = [f'Elbow y = {degrees:.1f} deg', f'Elbow z = {row["el_z"]:.1f} deg']
        else:
            local = np.asarray(row['swing_basis']).T @ fore
            h, v, h_name, v_name = float(local[2]), float(local[1]), 'Z', 'Y'
            degrees = row['sh_twist']
            heading = 'After undoing swing: Y-Z plane'
            normal, normal_color = 'X: arm axis, normal to this plane', AXIS_COLORS['X']
            lines = ([f'Twist = {degrees:.1f} deg', ''] if kind == 'shoulder_twist' else
                     ['Observed perpendicular', f'fraction = {row["perpendicular_fraction"]:.4f}'])
            if page_kind == 'twist_rotation':
                lines = [f'Twist = {degrees:.1f} deg',
                         f'Perpendicular fraction = {row["perpendicular_fraction"]:.2f}']
        # One fixed scale per clip; the straight-arm page magnifies the small
        # component and states the range on the ticks.
        extent = .20 if kind == 'observability' else 1.0
        boxes += plane_axes(draw, h_name, v_name, extent)
        tip = plane_vector(draw, h, v, extent)
        if kind != 'observability':
            arc = signed_arc(draw, PLANE_ORIGIN, 70, 0., degrees)
            side += [('Grey arc:', ARC_GREY), ('elbow y' if kind == 'elbow_angles' else 'twist', ARC_GREY)]
        out.update({'unit_forearm_local': local.tolist(), 'horizontal_component': h,
                    'vertical_component': v, 'signed_angle_deg': float(degrees),
                    'projected_tip_px': tip.tolist()})
    boxes.append(label(draw, (845, 712), heading, PANEL_HEADING, inside=PLANE_RECT))
    boxes.append(label(draw, (845, 752), normal, SMALL, normal_color, inside=PLANE_RECT))
    for i, (text, color) in enumerate(side):
        boxes.append(label(draw, (SIDE_X, 800 + 36 * i), text, SMALL, color, inside=PLANE_RECT))
    if page_kind == 'twist_rotation':
        # Observability note (Section 5.5), folded in from the old page 20.
        for i, text in enumerate(['Straight arm:', 'fraction -> 0,', 'twist free', '(Section 5.5)']):
            boxes.append(label(draw, (SIDE_X, 968 + 36 * i), text, SMALL, '#AAAAAA', inside=PLANE_RECT))
    if kind == 'observability':
        boxes.append(label(draw, (SIDE_X, 950), 'Exact limit', SMALL, inside=PLANE_RECT))
        boxes.append(label(draw, (SIDE_X, 984), '(schematic)', SMALL, inside=PLANE_RECT))
        y = 1045
        draw.line([(SIDE_X + 10, y), (SIDE_X + 90, y), (SIDE_X + 170, y)], fill='#DDDDDD', width=7)
        for x in (SIDE_X + 10, SIDE_X + 90, SIDE_X + 170):
            draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill='white')
        draw.ellipse((SIDE_X + 76, y - 36, SIDE_X + 104, y + 36), outline='#AAAAAA', width=3)
        boxes.append(label(draw, (SIDE_X, 1086), 'Zero: twist', SMALL, inside=PLANE_RECT))
        boxes.append(label(draw, (SIDE_X, 1120), 'is free', SMALL, inside=PLANE_RECT))
    for i, text in enumerate(lines):
        if text:
            boxes.append(label(draw, (845, 1118 + 34 * i), text, SMALL, inside=PLANE_RECT))
    out.update({'coordinate_view': heading, 'axis_extent': extent, 'arc_end_px': arc,
                'projected_origin_px': PLANE_ORIGIN.tolist(), 'readouts': [t for t in lines if t]})
    return out, boxes


def compose(page, frame, row, intrinsics, model_view, photo):
    """Render one 1440x1200 frame; returns the image and its audit record."""
    if KINDS[page] in FOUR_KINDS:
        return compose_four(page, frame, row, intrinsics, model_view, photo)
    im = Image.new('RGB', (W, H), 'black')
    d = ImageDraw.Draw(im)
    assert photo.size == SOURCE_SIZE
    im.paste(photo.resize((768, 576), Image.Resampling.LANCZOS), CAMERA_RECT[:2])
    before = im.crop(CAMERA_RECT)
    points = {k: np.asarray(v) for k, v in row['points_camera_prime_m'].items()}
    colors = edge_colors(page)
    camera = make_pinhole_projector(intrinsics, source_to_camera=F,
                                    scale=CAMERA_SCALE, offset=CAMERA_RECT[:2])
    scale = model_view['scale_px_per_source_px']
    offset = model_view['offset_px']
    model = make_pinhole_projector(intrinsics, source_to_camera=F, scale=scale, offset=offset)
    # Top: recorded frame with overlay.
    draw_skeleton(d, points, camera, colors)
    camera_triads = [draw_triad(d, o, b, camera, length, labels=False, line_width=5)
                     for o, b, length in active_triads(page, row, points)]
    mask, mask_info = overlay_mask(before, im.crop(CAMERA_RECT))
    # Bottom-left: the same points, same pinhole, black background.
    d.rectangle(MODEL_RECT, outline=BORDER, width=2)
    d.rectangle(PLANE_RECT, outline=BORDER, width=2)
    reference = [dim_triad(d, o, b, model, length) for o, b, length in reference_triads(page, row, points)]
    draw_skeleton(d, points, model, colors, dot=7)
    model_triads = []
    for o, b, length in active_triads(page, row, points):
        u, v = model(o)
        d.ellipse((u - 15, v - 15, u + 15, v + 15), outline='white', width=3)
        model_triads.append(draw_triad(d, o, b, model, length, labels=True, line_width=6, label_px=36))
    boxes = []
    boxes.append(label(d, (35, 712), 'Camera-view model', PANEL_HEADING, inside=MODEL_RECT))
    repaired = row['required_repaired_points']
    status = 'Filtered input' + (f' | Repaired: {repaired}' if repaired else '')
    boxes.append(label(d, (785, 714), status, SMALL, anchor='ra', inside=MODEL_RECT))
    boxes.append(label(d, (35, 752), ORIGIN_TEXT[page], SMALL, inside=MODEL_RECT))
    # Bottom-right: the page's quantity.
    plane, plane_boxes = plane_panel(d, page, row)
    boxes += plane_boxes
    # Header and fixed column labels.
    boxes.append(label(d, (35, 12), f'p{page:02d} | {TITLES[page]}', 39))
    boxes.append(label(d, (1405, 12), f'Frame {frame}', 39, anchor='ra'))
    boxes.append(label(d, (40, 83), 'Recorded input', 35))
    boxes.append(label(d, (40, 128), '0.5x playback', 33))
    for i, axis in enumerate('XYZ'):
        boxes.append(label(d, (43 + i * 68, 588), axis, 42, AXIS_COLORS[axis]))
    boxes.append(label(d, (40, 652), 'Same source frame and camera projection', 34))
    # Congruence: overlay and model pixels agree after removing each
    # panel's own scale and offset.
    xyz = np.vstack([points[n] for n in NAMES])
    top = (np.asarray(camera(xyz)) - CAMERA_RECT[:2]) / CAMERA_SCALE
    low = (np.asarray(model(xyz)) - np.asarray(offset)) / scale
    congruence = float(np.max(np.abs(top - low)))
    l12 = NAMES.index('right_shoulder')
    audit = {'source_frame': frame,
             'inference_rgb_sha256': row['source_rgb']['inference_rgb_sha256'],
             'camera_overlay': mask_info,
             'camera_overlay_mask_sha256': hashlib.sha256(mask.tobytes()).hexdigest(),
             'camera_triad': camera_triads[0], 'model_triad': model_triads[0],
             'reference_triads_px': reference, 'plane': plane,
             'l12_overlay_px': np.asarray(camera(points['right_shoulder'])).tolist(),
             'l12_model_px': np.asarray(model(points['right_shoulder'])).tolist(),
             'l12_source_px_from_overlay': top[l12].tolist(),
             'l12_source_px_from_model': low[l12].tolist(),
             'congruence_max_abs_source_px': congruence,
             'edge_colors': {f'{a}-{b}': c for (a, b), c in colors.items()},
             'label_bounds': boxes}
    return im, audit


# ---------------------------------------------------------------------------
# Merged pages 13-16 (unified_four): parent frame dim, rotated frame bright.
# ---------------------------------------------------------------------------

def rot_x(deg):
    a = np.radians(deg)
    return np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])


def rot_y(deg):
    a = np.radians(deg)
    return np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])


def rot_z(deg):
    a = np.radians(deg)
    return np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])


def angle_deg(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.degrees(np.arctan2(np.linalg.norm(np.cross(a, b)), np.dot(a, b))))


def samples(degrees):
    return np.linspace(0., 1., max(2, int(abs(degrees) / 3) + 1))


def rotation_pair(page, row, points):
    """Parent and rotated frame of a merged page, with the 3D arc directions.

    Swing (page 14): the arc is the great circle from the root X axis to the
    swing X axis (the single rotation that carries the parent X onto the upper
    arm); its label is the angle between the two axes. Twist (page 15): the
    arc is Rx(t * twist) applied to the swing Z axis about the shared X axis.
    Elbow (page 16): the arc is arm @ Ry(t * el_y) then Rz(t * el_z) applied to
    the arm X axis, which ends on the forearm; the label is el_y.
    """
    kind = KINDS[page]
    root = np.asarray(row['root_basis'])
    swing = np.asarray(row['swing_basis'])
    arm = np.asarray(row['upper_arm_basis'])
    if kind == 'torso_frame':
        return {'origin': points['right_hip'], 'parent': None, 'rotated': root,
                'lengths': [ROOT_AXIS_M] * 3, 'bone': None, 'arc_dirs': None, 'arc_value': None,
                'arc_text': 'No parent: the root is the first frame', 'arc_name': None}
    if kind == 'swing_rotation':
        bone = points['right_elbow'] - points['right_shoulder']
        px, rx = root[:, 0], swing[:, 0]
        theta = angle_deg(px, rx)
        n = np.cross(px, rx)
        if np.linalg.norm(n) < 1e-12:
            dirs = np.vstack([px, rx])
        else:
            n = n / np.linalg.norm(n)
            t = np.radians(theta) * samples(theta)
            dirs = np.outer(np.cos(t), px) + np.outer(np.sin(t), np.cross(n, px))
        return {'origin': points['right_shoulder'], 'parent': root, 'rotated': swing,
                'lengths': [float(np.linalg.norm(bone)), PAIR_AXIS_M, PAIR_AXIS_M],
                'bone': (points['right_shoulder'], points['right_elbow']), 'arc_dirs': dirs,
                'arc_axis': 0, 'arc_value': theta, 'arc_name': 'swing',
                'arc_text': f'Grey arc: swing = {theta:.1f} deg'}
    if kind == 'twist_rotation':
        tau = float(row['sh_twist'])
        dirs = np.vstack([swing @ rot_x(t * tau) @ [0., 0., 1.] for t in samples(tau)])
        # The bright X continues the upper arm beyond L14; no bone ends at its tip.
        return {'origin': points['right_elbow'], 'parent': swing, 'rotated': arm,
                'lengths': [PAIR_AXIS_M] * 3,
                'bone': (points['right_shoulder'], points['right_elbow']), 'bone_ends_at_tip': False,
                'arc_dirs': dirs, 'arc_axis': 2, 'arc_value': tau, 'arc_name': 'twist',
                'arc_text': f'Grey arc: twist = {tau:.1f} deg'}
    elbow = np.asarray(row['elbow_basis'])
    bone = points['right_wrist'] - points['right_elbow']
    ey, ez = float(row['el_y']), float(row['el_z'])
    dirs = [arm @ rot_y(t * ey) @ [1., 0., 0.] for t in samples(ey)]
    if abs(ez) > 0:
        dirs += [arm @ rot_y(ey) @ rot_z(t * ez) @ [1., 0., 0.] for t in samples(ez)[1:]]
    return {'origin': points['right_elbow'], 'parent': arm, 'rotated': elbow,
            'lengths': [float(np.linalg.norm(bone)), PAIR_AXIS_M, PAIR_AXIS_M],
            'bone': (points['right_elbow'], points['right_wrist']), 'arc_dirs': np.vstack(dirs),
            'arc_axis': 0, 'arc_value': ey, 'arc_name': 'elbow y',
            'arc_text': f'Grey arc: elbow y = {ey:.1f} deg'}


def pair_checks(pair):
    """Rotated X against the bone direction and arc end against the rotated axis (deg)."""
    out = {}
    if pair['bone'] is not None:
        a, b = pair['bone']
        out['rotated_x_vs_bone_deg'] = angle_deg(pair['rotated'][:, 0], b - a)
    if pair['arc_dirs'] is not None:
        axis = pair['arc_axis']
        out['arc_start_vs_parent_deg'] = angle_deg(pair['arc_dirs'][0], pair['parent'][:, axis])
        out['arc_end_vs_rotated_deg'] = angle_deg(pair['arc_dirs'][-1], pair['rotated'][:, axis])
        if pair['arc_name'] == 'swing':
            out['arc_label_vs_axes_deg'] = abs(pair['arc_value'] - angle_deg(pair['parent'][:, 0], pair['rotated'][:, 0]))
    return out


def four_points(page, row, points):
    pair = rotation_pair(page, row, points)
    o = np.asarray(pair['origin'])
    out = [o[None], o + np.asarray(pair['lengths'])[:, None] * pair['rotated'].T]
    if pair['parent'] is not None:
        out.append(o + PAIR_AXIS_M * pair['parent'].T)
    if pair['arc_dirs'] is not None:
        out.append(o + ARC_M * pair['arc_dirs'])
    return np.vstack(out)


def axes_lines(draw, origin, basis, lengths, project, widths, colors):
    """Y and Z first, X last (on top of the bone it lies along)."""
    screen = np.asarray(project(np.vstack([origin, origin + np.asarray(lengths)[:, None] * np.asarray(basis).T])))
    for i in (1, 2, 0):
        arrow(draw, screen[0], screen[i + 1], colors['XYZ'[i]], widths['XYZ'[i]])
    return screen


def arc_polyline(draw, origin, dirs, project):
    pts = np.asarray(project(np.asarray(origin) + ARC_M * np.asarray(dirs)))
    draw.line([tuple(p) for p in pts], fill=ARC_GREY, width=3)
    tangent = pts[-1] - pts[max(0, len(pts) - 3)]
    if np.linalg.norm(tangent) > 1:
        u = tangent / np.linalg.norm(tangent)
        n = np.array([-u[1], u[0]])
        size = 14.
        draw.polygon([tuple(pts[-1]), tuple(pts[-1] - size * u + size * .45 * n),
                      tuple(pts[-1] - size * u - size * .45 * n)], fill=ARC_GREY)
    return pts.tolist()


def compose_four(page, frame, row, intrinsics, model_view, photo):
    """Merged pages 13-16: same panels as compose, rotation pair in the model."""
    im = Image.new('RGB', (W, H), 'black')
    d = ImageDraw.Draw(im)
    assert photo.size == SOURCE_SIZE
    im.paste(photo.resize((768, 576), Image.Resampling.LANCZOS), CAMERA_RECT[:2])
    before = im.crop(CAMERA_RECT)
    points = {k: np.asarray(v) for k, v in row['points_camera_prime_m'].items()}
    colors = edge_colors(page)
    camera = make_pinhole_projector(intrinsics, source_to_camera=F,
                                    scale=CAMERA_SCALE, offset=CAMERA_RECT[:2])
    scale = model_view['scale_px_per_source_px']
    offset = model_view['offset_px']
    model = make_pinhole_projector(intrinsics, source_to_camera=F, scale=scale, offset=offset)
    pair = rotation_pair(page, row, points)
    checks = pair_checks(pair)
    if pair['bone'] is not None:
        assert checks['rotated_x_vs_bone_deg'] < 1e-3, (page, frame, checks)
    if pair['arc_dirs'] is not None:
        assert max(checks['arc_start_vs_parent_deg'], checks['arc_end_vs_rotated_deg']) < 1e-3, (page, frame, checks)
    torso = pair['parent'] is None
    o = np.asarray(pair['origin'])
    bright = {a: AXIS_COLORS[a] for a in 'XYZ'}
    # Top: recorded frame with overlay; only the bright (rotated) triad.
    draw_skeleton(d, points, camera, colors, focus_width=6 if torso else FOUR_FOCUS_WIDTH['camera'])
    if torso:
        camera_triad = draw_triad(d, o, pair['rotated'], camera, pair['lengths'][0], labels=False, line_width=5)
        camera_screen = np.vstack([camera_triad['origin_px'], camera_triad['endpoints_px']])
    else:
        camera_screen = axes_lines(d, o, pair['rotated'], pair['lengths'], camera,
                                   {'X': FOUR_X_WIDTH['camera'], 'Y': 4, 'Z': 4}, bright)
        camera_triad = {'origin_px': camera_screen[0].tolist(), 'endpoints_px': camera_screen[1:].tolist()}
    mask, mask_info = overlay_mask(before, im.crop(CAMERA_RECT))
    # Bottom-left: parent dim, skeleton, rotated bright, arc, ring; drawn on a
    # layer and pasted clipped to MODEL_CLIP.
    d.rectangle(MODEL_RECT, outline=BORDER, width=2)
    d.rectangle(PLANE_RECT, outline=BORDER, width=2)
    panel_image, panel_draw = im, d
    im = Image.new('RGB', (W, H), 'black')
    d = ImageDraw.Draw(im)
    reference = []
    if not torso:
        reference = [axes_lines(d, o, pair['parent'], [PAIR_AXIS_M] * 3, model, {a: 4 for a in 'XYZ'},
                                {a: dim(AXIS_COLORS[a]) for a in 'XYZ'}).tolist()]
        for i in (1, 2):
            # Dim letters for the parent Y and Z tips.
            tip = np.asarray(reference[0][i + 1])
            delta = tip - np.asarray(reference[0][0])
            xy = tip + delta / max(np.linalg.norm(delta), 1) * 18
            d.text(tuple(xy), 'XYZ'[i], font=font(28), anchor='mm', fill=dim(AXIS_COLORS['XYZ'[i]]))
    draw_skeleton(d, points, model, colors, dot=7, focus_width=6 if torso else FOUR_FOCUS_WIDTH['model'])
    letter_boxes = []
    if torso:
        model_triad = draw_triad(d, o, pair['rotated'], model, pair['lengths'][0], labels=True,
                                 line_width=6, label_px=36)
        model_screen = np.vstack([model_triad['origin_px'], model_triad['endpoints_px']])
        arc = None
    else:
        model_screen = axes_lines(d, o, pair['rotated'], pair['lengths'], model,
                                  {'X': FOUR_X_WIDTH['model'], 'Y': 6, 'Z': 6}, bright)
        arc = arc_polyline(d, o, pair['arc_dirs'], model)
        f36 = font(36)
        for i, name in ((1, 'Y'), (2, 'Z')):
            delta = model_screen[i + 1] - model_screen[0]
            xy = model_screen[i + 1] + delta / max(np.linalg.norm(delta), 1) * 20
            letter_boxes.append(list(d.textbbox(tuple(xy), name, font=f36, anchor='mm')))
            d.text(tuple(xy), name, font=f36, anchor='mm', fill=AXIS_COLORS[name], stroke_width=1, stroke_fill='black')
        # X letter beside the X axis, on the side away from the Y tip.
        delta = model_screen[1] - model_screen[0]
        u = delta / max(np.linalg.norm(delta), 1)
        n = np.array([-u[1], u[0]])
        if np.dot(n, model_screen[2] - model_screen[0]) > 0:
            n = -n
        xy = model_screen[0] + .6 * delta + 28 * n if pair['bone'] is not None and pair.get('bone_ends_at_tip', True) \
            else model_screen[1] + u * 20
        letter_boxes.append(list(d.textbbox(tuple(xy), 'X', font=f36, anchor='mm')))
        d.text(tuple(xy), 'X', font=f36, anchor='mm', fill=AXIS_COLORS['X'], stroke_width=1, stroke_fill='black')
        model_triad = {'origin_px': model_screen[0].tolist(), 'endpoints_px': model_screen[1:].tolist(),
                       'lengths_m': list(map(float, pair['lengths']))}
    u0, v0 = model(o)
    d.ellipse((u0 - 15, v0 - 15, u0 + 15, v0 + 15), outline='white', width=3)
    panel_image.paste(im.crop(MODEL_CLIP), MODEL_CLIP[:2])
    im, d = panel_image, panel_draw
    boxes = [label(d, (35, 712), 'Camera-view model', PANEL_HEADING, inside=MODEL_RECT)]
    repaired = row['required_repaired_points']
    status = 'Filtered input' + (f' | Repaired: {repaired}' if repaired else '')
    boxes.append(label(d, (785, 714), status, SMALL, anchor='ra', inside=MODEL_RECT))
    boxes.append(label(d, (35, 752), ORIGIN_TEXT[page], SMALL, inside=MODEL_RECT))
    boxes.append(label(d, (35, 788), pair['arc_text'], SMALL, ARC_GREY, inside=MODEL_RECT))
    plane, plane_boxes = plane_panel(d, page, row)
    boxes += plane_boxes
    boxes.append(label(d, (35, 12), f'p{page:02d} | {TITLES[page]}', 39))
    boxes.append(label(d, (1405, 12), f'Frame {frame}', 39, anchor='ra'))
    boxes.append(label(d, (40, 83), 'Recorded input', 35))
    boxes.append(label(d, (40, 128), '0.5x playback', 33))
    for i, axis in enumerate('XYZ'):
        boxes.append(label(d, (43 + i * 68, 588), axis, 42, AXIS_COLORS[axis]))
    boxes.append(label(d, (40, 652), 'Same source frame and camera projection', 34))
    xyz = np.vstack([points[n] for n in NAMES])
    top = (np.asarray(camera(xyz)) - CAMERA_RECT[:2]) / CAMERA_SCALE
    low = (np.asarray(model(xyz)) - np.asarray(offset)) / scale
    congruence = float(np.max(np.abs(top - low)))
    l12 = NAMES.index('right_shoulder')
    bone_end = None
    if pair['bone'] is not None and pair.get('bone_ends_at_tip', True):
        bone_end = {'camera_px': np.asarray(camera(pair['bone'][1])).tolist(),
                    'model_px': np.asarray(model(pair['bone'][1])).tolist()}
    audit = {'source_frame': frame,
             'inference_rgb_sha256': row['source_rgb']['inference_rgb_sha256'],
             'camera_overlay': mask_info,
             'camera_overlay_mask_sha256': hashlib.sha256(mask.tobytes()).hexdigest(),
             'camera_triad': camera_triad, 'model_triad': model_triad,
             'reference_triads_px': reference, 'plane': plane,
             'rotation_pair': {'origin_m': o.tolist(),
                               'parent_basis': None if torso else pair['parent'].tolist(),
                               'rotated_basis': pair['rotated'].tolist(),
                               'rotated_lengths_m': list(map(float, pair['lengths'])),
                               'bright_x_tip_camera_px': camera_screen[1].tolist(),
                               'bright_x_tip_model_px': model_screen[1].tolist(),
                               'bone_end_px': bone_end,
                               'arc_model_px': arc, 'arc_name': pair['arc_name'],
                               'arc_value_deg': pair['arc_value'], 'arc_text': pair['arc_text'],
                               'checks_deg': checks, 'axis_letter_bounds': letter_boxes},
             'l12_overlay_px': np.asarray(camera(points['right_shoulder'])).tolist(),
             'l12_model_px': np.asarray(model(points['right_shoulder'])).tolist(),
             'l12_source_px_from_overlay': top[l12].tolist(),
             'l12_source_px_from_model': low[l12].tolist(),
             'congruence_max_abs_source_px': congruence,
             'edge_colors': {f'{a}-{b}': c for (a, b), c in colors.items()},
             'label_bounds': boxes}
    return im, audit
