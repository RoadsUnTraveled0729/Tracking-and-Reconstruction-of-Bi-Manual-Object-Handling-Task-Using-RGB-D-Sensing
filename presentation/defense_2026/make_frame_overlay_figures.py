#!/usr/bin/env python3
"""Draw coordinate-frame overlays on faded photographs for the frame_figure slot.

Each figure is described by one JSON spec in figures/coordinate_frames/overlay/
(spec_<name>.json): the photographs (panels), the frames to draw, marked
points, lines and label texts. The photograph is resized into its box and
multiplied by 0.5 (the page-30 fade of eval/failure/make_label_compare_fig.py,
render_panel: rint(img * (1 - fade)) with fade 0.5); every overlay is drawn
afterwards at full strength.

A frame is "projected" when its pose comes from a pinned calibrated source
(ArUco marker poses of the frozen chain, the scene calibration, the Unity
receiver log) and is pushed through the camera model of its panel. It is
"illustrative" when its anchor and axis directions are declared in the spec.
Every frame's mode, pose source and anchor are written to overlay/manifest.json.

A panel may instead be a plain diagram panel ("background": "plain"): no
photograph, the deck's black background (build_deck.py: black background
000000), and only illustrative frames, outline shapes and texts drawn on it
(round 10, D-316). A spec may set its own canvas size ("canvas_px") as long as
the labels keep the 16 pt effective floor in the frame_figure box (checked).

Run from the repository root with the thesis Python:

    /home/luo/anaconda3/bin/python presentation/defense_2026/make_frame_overlay_figures.py --measure-tpose
    /home/luo/anaconda3/bin/python presentation/defense_2026/make_frame_overlay_figures.py

--measure-tpose runs MediaPipe PoseLandmarker (the v1 heavy model, IMAGE mode,
CPU) once on tpose_source.jpg and writes overlay/tpose_landmarks_mediapipe.json,
which the T-pose specs read for their landmark anchors. The default run renders
all six figures and the manifest. The source photographs are only read.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
from anim.coordinate_axes import AXIS_COLORS  # noqa: E402  shared semantic colours

OUT = HERE / 'figures' / 'coordinate_frames' / 'overlay'
FIGURES = ['static_markers', 'camera_frames', 'landmark_frames', 'torso_root', 'object_world',
           'scene_mapping', 'rig_frames']
LANDMARK_JSON = OUT / 'tpose_landmarks_mediapipe.json'
TPOSE_PHOTO = 'presentation/defense_2026/figures/coordinate_frames/tpose_source.jpg'
MP_MODEL = 'v1/mediapipe/models/pose_landmarker_heavy.task'
MP_LANDMARKS = [11, 12, 13, 14, 15, 16, 23, 24]

# Deck geometry (build_deck.py, kind frame_figure): the figure is fitted into
# a 6.61 x 5.00 in box, or 6.61 x 4.75 in when the caption takes three lines.
CANVAS = (1440, 1200)            # size of the existing schematics in figures/coordinate_frames/
BOX_IN = [(6.61, 5.00), (6.61, 4.75)]
TARGET_PT = 16.0                 # knowledge/deck_fonts.md: target for regenerated images
PX_PER_IN_WORST = max(max(CANVAS[0] / w, CANVAS[1] / h) for w, h in BOX_IN)
LABEL_PX = math.ceil(TARGET_PT / 72.0 * PX_PER_IN_WORST)   # 57 px
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'  # build_deck.py TYPEFACE
FADE = 0.5                       # page-30 fade (figures/recovery/manifest.json, --fade 0.5)
LINE_W = 7
HEAD_LEN, HEAD_HALF = 26, 12
STROKE = 3
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SOFT = (225, 225, 225)
Z_RING_R = 20
LABEL_MARGIN = 4
# D-303 (round 9 code review M4): largest accepted distance between a marker
# origin projected from its calibrated or per-frame pose and the pinned
# detector's corner mean on the same frame (World, Object and Wall checks in
# reprojection_checks). The value 1.0 px was set by the review brief; the
# recorded residuals at build 67 are 0.72, 0.02 and 0.08 px. The two Unity
# checks compare with hand-measured anchors in a rendered Unity frame and are
# recorded without this bound.
REPROJECTION_BOUND_PX = 1.0

S_SWAP = np.array([[1., 0, 0], [0, 0, 1], [0, 1, 0]])   # thesis Eq. 6.1
F_FLIP = np.diag([1., -1., 1.])                         # thesis Eq. 3.1


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    return str(Path(path).resolve().relative_to(REPO))


def rp(path):
    return REPO / path


def hexrgb(value):
    value = value.lstrip('#')
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def font(size=LABEL_PX):
    return ImageFont.truetype(FONT, size)


# --------------------------------------------------------------------------
# measurement of the T-pose landmarks (MediaPipe, same model as v1)
# --------------------------------------------------------------------------

def measure_tpose():
    import mediapipe as mp
    from mediapipe.tasks import python as mp_python
    from mediapipe.tasks.python import vision as mp_vision
    bgr = cv2.imread(str(rp(TPOSE_PHOTO)), cv2.IMREAD_COLOR)
    if bgr is None:
        raise FileNotFoundError(TPOSE_PHOTO)
    rgb = np.ascontiguousarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))
    h, w = rgb.shape[:2]
    # Options follow v1/mediapipe/extract_landmarks_to_csv.py make_landmarker
    # (num_poses 1, confidences 0.3); IMAGE mode because this is one photograph,
    # CPU so the result does not depend on a GPU driver.
    options = mp_vision.PoseLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(rp(MP_MODEL)),
                                           delegate=mp_python.BaseOptions.Delegate.CPU),
        running_mode=mp_vision.RunningMode.IMAGE, num_poses=1,
        min_pose_detection_confidence=0.3, min_pose_presence_confidence=0.3)
    with mp_vision.PoseLandmarker.create_from_options(options) as landmarker:
        result = landmarker.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
    if len(result.pose_landmarks) != 1:
        raise RuntimeError('MediaPipe did not return exactly one pose on the T-pose photo')
    pose = result.pose_landmarks[0]
    rows = {}
    for i in MP_LANDMARKS:
        p = pose[i]
        rows[str(i)] = {'x_px': round(p.x * w, 3), 'y_px': round(p.y * h, 3),
                        'visibility': round(p.visibility, 4), 'presence': round(p.presence, 4)}
    record = {
        'purpose': 'Measured landmark pixels on the T-pose photograph for the overlay anchors; '
                   'no landmark is hand-placed.',
        'photo': TPOSE_PHOTO, 'photo_sha256': sha(rp(TPOSE_PHOTO)), 'photo_px': [w, h],
        'exif_orientation': Image.open(rp(TPOSE_PHOTO)).getexif().get(274),
        'detector': 'MediaPipe PoseLandmarker (Tasks API)', 'mediapipe_version': mp.__version__,
        'model': MP_MODEL, 'model_sha256': sha(rp(MP_MODEL)),
        'options': {'running_mode': 'IMAGE', 'delegate': 'CPU', 'num_poses': 1,
                    'min_pose_detection_confidence': 0.3, 'min_pose_presence_confidence': 0.3},
        'options_source': 'v1/mediapipe/extract_landmarks_to_csv.py make_landmarker (confidences, num_poses, model)',
        'pixel_convention': 'normalized x * width, y * height of the full photograph',
        'landmarks': rows,
        'command': '/home/luo/anaconda3/bin/python presentation/defense_2026/make_frame_overlay_figures.py --measure-tpose',
    }
    OUT.mkdir(parents=True, exist_ok=True)
    LANDMARK_JSON.write_text(json.dumps(record, indent=1) + '\n')
    print('wrote', rel(LANDMARK_JSON))


# --------------------------------------------------------------------------
# pinned pose sources
# --------------------------------------------------------------------------

class Sources:
    """Loads the pinned calibrated inputs once and records every file read."""

    def __init__(self):
        self.read = {}

    def note(self, path):
        p = rp(path)
        self.read[path] = {'sha256': sha(p), 'bytes': p.stat().st_size}
        return p

    def json(self, path):
        return json.loads(self.note(path).read_text())

    def csv_row(self, path, frame):
        import csv
        with open(self.note(path)) as fh:
            for row in csv.DictReader(fh):
                if int(row['frame']) == int(frame):
                    return row
        raise KeyError(f'frame {frame} not in {path}')

    # camera-from-desk (the World frame) from the scene calibration
    def cam_from_world(self, calib):
        T = np.array(self.json(calib)['T_cam_desk'], float)
        return T[:3, :3], T[:3, 3]

    def gravity_G(self, calib):
        """Shortest rotation carrying the calibrated gravity (display axes) onto
        the scene vertical: the operator G of thesis Eq. 6.6 (Unity
        Quaternion.FromToRotation in ArucoSceneReceiver.cs)."""
        up = np.array(self.json(calib)['scene_geometry']['gravity_up_unity'], float)
        up = up / np.linalg.norm(up)
        y = np.array([0., 1., 0.])
        v = np.cross(up, y)
        s, c = np.linalg.norm(v), float(up @ y)
        vx = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
        return np.eye(3) + vx + vx @ vx * ((1 - c) / s ** 2)

    def floor_tf(self, pose):
        """tf of Eq. 6.6 from the receiver log: the spine bone position minus
        G S applied to the streamed pelvis carried into the world."""
        Rcw, tcw = self.cam_from_world(pose['calibration'])
        G = self.gravity_G(pose['calibration'])
        row = self.csv_row(pose['person_log'], pose['frame'])
        pel = np.array([float(row['pel_' + c]) for c in 'xyz'])
        hip = np.array([float(row['hip_' + c]) for c in 'xyz'])
        world = Rcw.T @ (F_FLIP @ pel - tcw)
        return hip - G @ S_SWAP @ world

    def scene_to_cam(self, pose):
        Rcw, tcw = self.cam_from_world(pose['calibration'])
        G = self.gravity_G(pose['calibration'])
        tf = self.floor_tf(pose)
        return lambda P: Rcw @ (S_SWAP @ G.T @ (np.asarray(P, float) - tf)) + tcw, Rcw @ S_SWAP @ G.T

    def resolve(self, pose):
        """Returns (origin_cam, basis_cam columns, info) for a projected frame."""
        kind = pose['type']
        if kind == 'calibration_world':
            R, t = self.cam_from_world(pose['calibration'])
            return t, R, {'pose': 'T_cam_desk of the scene calibration (World = desk marker id 2 frame)'}
        if kind == 'calibration_marker':
            # a static marker's calibrated pose held by the scene calibration,
            # e.g. T_cam_wall (thesis WallCameraR, Section 2.2.2: the wall
            # marker's in-plane up axis is the gravity reference)
            T = np.array(self.json(pose['calibration'])[pose['key']], float)
            return T[:3, 3], T[:3, :3], {'pose': f'{pose["key"]} of the scene calibration'}
        if kind == 'aruco_row':
            row = self.csv_row(pose['csv'], pose['frame'])
            m = pose['marker']
            if int(float(row[f'm{m}_detected'])) != 1:
                raise ValueError(f'marker {m} not detected on frame {pose["frame"]}')
            R = np.array([[float(row[f'm{m}_r{i}{j}']) for j in (1, 2, 3)] for i in (1, 2, 3)])
            t = np.array([float(row[f'm{m}_t{c}']) for c in 'xyz'])
            return t, R, {'pose': f'camera-from-marker {m}, frame {pose["frame"]}',
                          'ambig_code': row[f'm{m}_ambig'], 'reproj_px': float(row[f'm{m}_reproj_px'])}
        if kind == 'scene':
            to_cam, basis = self.scene_to_cam(pose)
            Rcw, tcw = self.cam_from_world(pose['calibration'])
            origin_true = to_cam(np.zeros(3))
            tf = self.floor_tf(pose)
            info = {'pose': 'Scene = G S World + tf (Eq. 6.6); axes carried into the camera by S G^T',
                    'G': self.gravity_G(pose['calibration']).round(6).tolist(),
                    'tf_m': [round(float(v), 6) for v in tf],
                    'scene_origin_cam_m': origin_true.round(6).tolist()}
            if pose.get('anchor') == 'desk_marker':
                info['anchor'] = 'drawn at the desk-marker origin; the Scene origin lies on the floor outside the view'
                return tcw, basis, info
            return origin_true, basis, info
        if kind == 'rig_segment':
            to_cam, _ = self.scene_to_cam(pose)
            log = self.csv_row(pose['person_log'], pose['frame'])
            stream = self.csv_row(pose['stream'], pose['frame'])
            a = [float(stream[f'a{i}']) for i in range(13)]
            R_root = ry(a[1]) @ rx(a[0]) @ rz(a[2])          # Eq. 3.15, IntegratedSceneReceiver qRoot
            R_sh = ry(a[3]) @ rz(a[4]) @ rx(a[5])            # Eq. 3.18, qSh (right side)
            R_el = ry(a[6]) @ rz(a[7])                       # qElb (right side)
            chain = {'root': R_root, 'L14': R_root @ R_sh, 'L16': R_root @ R_sh @ R_el}
            joint = {'root': 'hip', 'L14': 'rel', 'L16': 'rh'}[pose['segment']]
            P = to_cam([float(log[f'{joint}_{c}']) for c in 'xyz'])
            basis = F_FLIP @ chain[pose['segment']]
            info = {'pose': f'segment {pose["segment"]}: Camera\' rotation from the streamed angles '
                            f'(Eq. 6.4), carried to the camera by F; origin = rig joint {joint} of the receiver log',
                    'angles_deg': [round(v, 4) for v in a], 'origin_joint': joint}
            # check: segment first axis against the rendered bone direction
            bone = {'L14': ('rsh', 'rel'), 'L16': ('rel', 'rh')}.get(pose['segment'])
            if bone:
                p0 = to_cam([float(log[f'{bone[0]}_{c}']) for c in 'xyz'])
                p1 = to_cam([float(log[f'{bone[1]}_{c}']) for c in 'xyz'])
                d = (p1 - p0) / np.linalg.norm(p1 - p0)
                info['x_axis_vs_rig_bone_deg'] = round(math.degrees(math.acos(np.clip(d @ basis[:, 0], -1, 1))), 3)
            return P, basis, info
        raise ValueError('unknown pose type ' + kind)

    def point(self, spec):
        """A projected point in the camera frame (for marked points)."""
        if spec['type'] == 'rig_joint':
            to_cam, _ = self.scene_to_cam(spec)
            log = self.csv_row(spec['person_log'], spec['frame'])
            return to_cam([float(log[f'{spec["joint"]}_{c}']) for c in 'xyz'])
        raise ValueError(spec['type'])


def rx(d):
    a = math.radians(d)
    return np.array([[1, 0, 0], [0, math.cos(a), -math.sin(a)], [0, math.sin(a), math.cos(a)]])


def ry(d):
    a = math.radians(d)
    return np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])


def rz(d):
    a = math.radians(d)
    return np.array([[math.cos(a), -math.sin(a), 0], [math.sin(a), math.cos(a), 0], [0, 0, 1]])


# --------------------------------------------------------------------------
# panels: photo -> box, camera model
# --------------------------------------------------------------------------

class Panel:
    def __init__(self, spec, sources):
        self.spec = spec
        self.box = spec['box_px']
        self.plain = spec.get('background') == 'plain'
        self.K = None
        if self.plain:
            # D-316: a diagram panel without a photograph; only illustrative
            # content may be drawn on it (no camera model, no projection).
            if any(k in spec for k in ('photo', 'crop_px', 'camera')):
                raise ValueError(f'plain panel {spec["id"]} declares a photo, crop or camera')
            self.photo, self.crop, self.sx, self.sy = None, None, 1.0, 1.0
            return
        self.photo = spec['photo']
        self.crop = spec['crop_px']
        cw, ch = self.crop[2] - self.crop[0], self.crop[3] - self.crop[1]
        bw, bh = self.box[2] - self.box[0], self.box[3] - self.box[1]
        self.sx, self.sy = bw / cw, bh / ch
        if abs(self.sx - self.sy) > 1e-9:
            raise ValueError(f'panel {spec["id"]}: crop and box aspect differ')
        cam = spec.get('camera')
        if cam and cam['type'] == 'recording_intrinsics':
            ci = sources.json(cam['meta'])['color_intrinsics']
            if any(abs(c) > 0 for c in ci['coeffs']):
                raise ValueError('non-zero distortion is not modelled here')
            self.K = (ci['fx'], ci['fy'], ci['ppx'], ci['ppy'])
            self.camera_note = f'{cam["meta"]} color_intrinsics (distortion coefficients all zero)'
        elif cam and cam['type'] == 'unity_sensor':
            fov = sources.json(cam['calibration'])['scene_geometry']['sensor_fov_y_deg']
            f = (480 / 2) / math.tan(math.radians(fov) / 2)
            self.K = (f, f, 320.0, 240.0)
            self.camera_note = (f'Unity sensor POV camera: vertical field of view {fov:.6f} deg from '
                                f'{cam["calibration"]} (ArucoSceneReceiver.cs pov.fieldOfView), 640x480, '
                                'centred principal point, square pixels')

    def contains(self, box):
        x0, y0, x1, y1 = self.box
        return box[0] >= x0 and box[1] >= y0 and box[2] <= x1 and box[3] <= y1

    def to_canvas(self, uv):
        if self.plain:
            raise ValueError(f'plain panel {self.spec["id"]} has no photo pixels')
        uv = np.asarray(uv, float)
        return np.array([self.box[0] + (uv[0] - self.crop[0]) * self.sx,
                         self.box[1] + (uv[1] - self.crop[1]) * self.sy])

    def project(self, P):
        P = np.asarray(P, float)
        if P[2] <= 0:
            raise ValueError('point behind the camera')
        fx, fy, cx, cy = self.K
        return self.to_canvas([fx * P[0] / P[2] + cx, fy * P[1] / P[2] + cy])

    def render(self):
        rgb = np.asarray(Image.open(rp(self.photo)).convert('RGB'))
        x0, y0, x1, y1 = self.crop
        sub = rgb[y0:y1, x0:x1]
        bw, bh = self.box[2] - self.box[0], self.box[3] - self.box[1]
        interp = cv2.INTER_CUBIC if bw >= sub.shape[1] else cv2.INTER_AREA
        img = cv2.resize(sub, (bw, bh), interpolation=interp)
        faded = np.clip(np.rint(img.astype(np.float64) * (1.0 - FADE)), 0, 255).astype(np.uint8)
        return faded, 'INTER_CUBIC' if interp == cv2.INTER_CUBIC else 'INTER_AREA'


# --------------------------------------------------------------------------
# drawing
# --------------------------------------------------------------------------

class MirroredDraw:
    """An ImageDraw that repeats every drawing call on a mode-L mask with fill,
    outline and stroke set to 255, so the mask marks every pixel a shape, frame,
    point or text touched (D-336). The coloured drawing is unchanged."""
    DRAWING = ('line', 'polygon', 'ellipse', 'rectangle', 'text')

    def __init__(self, image, mask):
        self._draw = ImageDraw.Draw(image)
        self._mask = ImageDraw.Draw(mask)

    def __getattr__(self, name):
        real = getattr(self._draw, name)
        if name not in self.DRAWING:
            return real

        def mirrored(*args, **kwargs):
            real(*args, **kwargs)
            marked = {k: (255 if k in ('fill', 'outline', 'stroke_fill') and v is not None else v)
                      for k, v in kwargs.items()}
            if name == 'text' and 'fill' not in marked:
                marked['fill'] = 255
            getattr(self._mask, name)(*args, **marked)
        return mirrored


class Canvas:
    def __init__(self, size=CANVAS):
        self.size = tuple(size)
        self.im = Image.new('RGB', self.size, BLACK)
        self.drawn = Image.new('L', self.size, 0)
        self.draw = MirroredDraw(self.im, self.drawn)
        self.text_boxes = []

    def arrow(self, a, b, fill, width=LINE_W, dashed=False):
        a, b = np.asarray(a, float), np.asarray(b, float)
        d = b - a
        n = np.linalg.norm(d)
        if n < 1e-6:
            return
        u = d / n
        side = np.array([-u[1], u[0]])
        shaft_end = b - u * HEAD_LEN * 0.8
        if dashed:
            pos, on = 0.0, True
            while pos < n - HEAD_LEN:
                seg = min(pos + 22, n - HEAD_LEN * 0.8)
                if on:
                    self.draw.line([tuple(a + u * pos), tuple(a + u * seg)], fill=fill, width=width)
                pos, on = seg, not on
        else:
            self.draw.line([tuple(a), tuple(shaft_end)], fill=fill, width=width)
        self.draw.polygon([tuple(b), tuple(b - HEAD_LEN * u + HEAD_HALF * side),
                           tuple(b - HEAD_LEN * u - HEAD_HALF * side)], fill=fill)

    def line(self, a, b, fill, width=5, dashed=False):
        a, b = np.asarray(a, float), np.asarray(b, float)
        if not dashed:
            self.draw.line([tuple(a), tuple(b)], fill=fill, width=width)
            return
        d = b - a
        n = np.linalg.norm(d)
        u = d / n
        pos, on = 0.0, True
        while pos < n:
            seg = min(pos + 20, n)
            if on:
                self.draw.line([tuple(a + u * pos), tuple(a + u * seg)], fill=fill, width=width)
            pos, on = seg, not on

    def dot(self, xy, r=9, fill=WHITE, outline=BLACK):
        x, y = xy
        self.draw.ellipse((x - r, y - r, x + r, y + r), fill=fill, outline=outline, width=3)

    def z_symbol(self, xy, kind, fill):
        x, y = xy
        r = Z_RING_R
        self.draw.ellipse((x - r, y - r, x + r, y + r), outline=fill, width=5)
        if kind == 'into':      # tail of an arrow: a cross in the ring
            k = r * 0.62
            self.draw.line([(x - k, y - k), (x + k, y + k)], fill=fill, width=5)
            self.draw.line([(x - k, y + k), (x + k, y - k)], fill=fill, width=5)
        elif kind == 'out':     # tip of an arrow: a dot in the ring
            self.draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=fill)

    def text(self, value, xy, fill=WHITE, anchor='mm', owner=''):
        f = font()
        box = self.draw.textbbox(tuple(xy), value, font=f, anchor=anchor, stroke_width=STROKE)
        if box[0] < 0 or box[1] < 0 or box[2] > self.size[0] or box[3] > self.size[1]:
            raise ValueError(f'text outside the canvas: {value!r} {box}')
        for other, obox in self.text_boxes:
            if not (box[2] + LABEL_MARGIN <= obox[0] or obox[2] + LABEL_MARGIN <= box[0]
                    or box[3] + LABEL_MARGIN <= obox[1] or obox[3] + LABEL_MARGIN <= box[1]):
                raise ValueError(f'labels overlap: {value!r} {box} and {other!r} {obox}')
        self.draw.text(tuple(xy), value, font=f, fill=fill, anchor=anchor,
                       stroke_width=STROKE, stroke_fill=BLACK)
        self.text_boxes.append((value, list(box)))
        return [int(v) for v in box]


def draw_shape(cv, sh):
    """Outline shapes of a plain diagram panel (camera body, shoulders, head)."""
    colour = tuple(sh.get('rgb', SOFT))
    w = sh.get('width', 5)
    pts = sh['canvas_px']
    if sh['type'] == 'ellipse':
        cv.draw.ellipse(tuple(pts), outline=colour, width=w)
    elif sh['type'] == 'rect':
        cv.draw.rectangle(tuple(pts), outline=colour, width=w)
    elif sh['type'] == 'polygon':
        cv.draw.polygon([tuple(p) for p in pts], outline=colour, width=w)
    elif sh['type'] == 'line':
        cv.line(pts[0], pts[1], colour, width=w, dashed=sh.get('dashed', False))
    else:
        raise ValueError('unknown shape ' + sh['type'])
    flat = np.asarray(pts, float).reshape(-1, 2)
    return [float(flat[:, 0].min()), float(flat[:, 1].min()), float(flat[:, 0].max()), float(flat[:, 1].max())]


def axis_label_xy(origin, tip, offset=None):
    if offset is not None:
        return np.asarray(tip, float) + np.asarray(offset, float)
    d = np.asarray(tip, float) - np.asarray(origin, float)
    n = np.linalg.norm(d)
    return np.asarray(tip, float) + (d / n * 40 if n > 1 else np.array([40., -40.]))


def draw_frame(cv, fr, origin_px, tips_px, z_symbol=None, ring_axis='Z'):
    """Draws a triad from canvas origin and tip pixels; returns label boxes."""
    labels = fr.get('axis_labels', {'X': 'X', 'Y': 'Y', 'Z': 'Z'})
    offsets = fr.get('axis_label_offsets', {})
    boxes = {}
    order = fr.get('draw_order', ['Z', 'Y', 'X'])
    for name in order:
        if name in tips_px:
            cv.arrow(origin_px, tips_px[name], hexrgb(AXIS_COLORS[name]))
    if z_symbol:
        cv.z_symbol(origin_px, z_symbol, hexrgb(AXIS_COLORS[ring_axis]))   # the ring marks the origin
    else:
        cv.dot(origin_px, r=8)
    for name in ['X', 'Y', 'Z']:
        if name not in labels:
            continue
        if name in tips_px:
            xy = axis_label_xy(origin_px, tips_px[name], offsets.get(name))
        else:
            xy = np.asarray(origin_px, float) + np.asarray(offsets[name], float)
        anchor = fr.get('axis_label_anchors', {}).get(name, 'mm')
        boxes[name] = cv.text(labels[name], xy, fill=hexrgb(AXIS_COLORS[name]), anchor=anchor)
    if 'name_label' in fr:
        nl = fr['name_label']
        boxes['name'] = cv.text(nl['text'], np.asarray(origin_px) + np.asarray(nl['offset']),
                                anchor=nl.get('anchor', 'mm'))
    return boxes


def landmark_px(lm, i):
    row = lm['landmarks'][str(i)]
    return np.array([row['x_px'], row['y_px']])


def label_pt(canvas):
    """Effective size of the shared label em in the worst frame_figure box."""
    return min(LABEL_PX * min(w / canvas[0], h / canvas[1]) * 72 for w, h in BOX_IN)


def render_figure(name, sources):
    spec_path = OUT / f'spec_{name}.json'
    spec = json.loads(spec_path.read_text())
    sources.note(rel(spec_path))
    size = tuple(spec.get('canvas_px', CANVAS))
    if label_pt(size) < TARGET_PT:
        raise ValueError(f'{name}: canvas {size} puts the labels below {TARGET_PT} pt')
    cv = Canvas(size)
    panels = {}
    panel_rows = []
    base = np.zeros((size[1], size[0], 3), np.uint8)
    for p in spec['panels']:
        panel = Panel(p, sources)
        x0, y0, x1, y1 = p['box_px']
        if x0 < 0 or y0 < 0 or x1 > size[0] or y1 > size[1]:
            raise ValueError(f'panel {p["id"]} leaves the canvas')
        if panel.plain:
            panels[p['id']] = panel
            panel_rows.append({'id': p['id'], 'background': 'plain', 'box_px': p['box_px'],
                               'fill_rgb': list(BLACK),
                               'note': 'diagram panel, no photograph; deck background 000000 (build_deck.py)'})
            continue
        sources.note(p['photo'])
        faded, interp = panel.render()
        x0, y0, x1, y1 = p['box_px']
        base[y0:y1, x0:x1] = faded
        panels[p['id']] = panel
        row = {'id': p['id'], 'photo': p['photo'], 'photo_sha256': sha(rp(p['photo'])),
               'crop_px': p['crop_px'], 'box_px': p['box_px'], 'scale': panel.sx,
               'resample': 'cv2.' + interp, 'fade': FADE}
        if p.get('photo_source'):
            row['photo_source'] = p['photo_source']
            row['photo_source_sha256'] = sha(rp(p['photo_source']))
            row['byte_identical_to_source'] = row['photo_source_sha256'] == row['photo_sha256']
        if panel.K is not None:
            row['camera_model'] = {'fx': panel.K[0], 'fy': panel.K[1], 'cx': panel.K[2], 'cy': panel.K[3],
                                   'source': panel.camera_note}
        panel_rows.append(row)
    cv.im = Image.fromarray(base)
    cv.draw = MirroredDraw(cv.im, cv.drawn)
    lm = None
    if spec.get('landmarks'):
        lm = json.loads(LANDMARK_JSON.read_text())
        sources.note(rel(LANDMARK_JSON))
        if lm['photo_sha256'] != sha(rp(lm['photo'])):
            raise ValueError('T-pose landmark measurement is stale')

    def anchor_of(item, panel):
        if 'anchor_canvas_px' in item:
            return np.asarray(item['anchor_canvas_px'], float)
        if 'anchor_photo_px' in item:
            return panel.to_canvas(item['anchor_photo_px'])
        if 'landmark' in item:
            return panel.to_canvas(landmark_px(lm, item['landmark']))
        raise ValueError('no anchor')

    # shapes and lines first, then points, frames and texts on top
    shape_rows = []
    for sh in spec.get('shapes', []):
        panel = panels[sh['panel']]
        if not panel.plain:
            raise ValueError('outline shapes are drawn on plain diagram panels only')
        bbox = draw_shape(cv, sh)
        if not panel.contains(bbox):
            raise ValueError(f'shape {sh.get("name")} leaves its panel {sh["panel"]}')
        shape_rows.append({'shape': sh.get('name', sh['type']), 'panel': sh['panel'], 'mode': 'illustrative',
                           'bbox_px': [round(v, 1) for v in bbox]})
    for ln in spec.get('lines', []):
        panel = panels[ln['panel']]
        a = panel.to_canvas(landmark_px(lm, ln['from'])) if 'from' in ln else np.asarray(ln['from_canvas_px'])
        b = panel.to_canvas(landmark_px(lm, ln['to'])) if 'to' in ln else np.asarray(ln['to_canvas_px'])
        colour = tuple(ln.get('rgb', SOFT))
        if ln.get('arrow'):
            cv.arrow(a, b, colour, width=ln.get('width', 5), dashed=ln.get('dashed', False))
        else:
            cv.line(a, b, colour, width=ln.get('width', 5), dashed=ln.get('dashed', False))
        if 'label' in ln:
            mid = (a + b) / 2 + np.asarray(ln['label']['offset'], float)
            cv.text(ln['label']['text'], mid, fill=tuple(ln['label'].get('rgb', WHITE)))

    frame_rows = []
    for fr in spec.get('frames', []):
        panel = panels[fr['panel']]
        row = {'frame': fr['name'], 'panel': fr['panel'], 'overlay_mode': fr['mode'],
               'source': fr.get('thesis_source', '')}
        if fr['mode'] == 'projected':
            P0, B, info = sources.resolve(fr['pose'])
            L = fr['length_m']
            o = panel.project(P0)
            tips = {n: panel.project(P0 + L * B[:, i]) for i, n in enumerate('XYZ')}
            row.update(pose_type=fr['pose']['type'],
                       pose_sources=sorted({v for k, v in fr['pose'].items()
                                            if isinstance(v, str) and ('/' in v)}),
                       pose_detail=info, origin_cam_m=[round(float(v), 6) for v in P0],
                       basis_cam_columns=B.round(6).tolist(), determinant=round(float(np.linalg.det(B)), 6),
                       length_m=L)
            zsym = None
        else:
            o = anchor_of(fr, panel)
            L = fr['length_px']
            if panel.plain and 'anchor_canvas_px' not in fr:
                raise ValueError(f'{fr["name"]}: a plain-panel frame needs a canvas anchor')
            if fr.get('axes_from') == 'torso_2d':
                p23, p24, p12 = (panel.to_canvas(landmark_px(lm, i)) for i in (23, 24, 12))
                x = (p24 - p23) / np.linalg.norm(p24 - p23)                 # Eq. 3.7 in the image plane
                s = p12 - p24                                                # Eq. 3.8
                yv = s - (s @ x) * x                                         # in-plane part of Eqs. 3.9-3.10
                yv = yv / np.linalg.norm(yv)
                dirs = {'X': x, 'Y': yv}
                row['axes_construction'] = ('in-image: X along L23->L24 (Eq. 3.7), Y = in-plane part of '
                                            's = L12 - L24 orthogonal to X; Z toward the viewer is not '
                                            'measurable in one photograph and is drawn as a ring')
            else:
                dirs = {k: np.asarray(v, float) / np.linalg.norm(v) for k, v in fr['axes_canvas'].items()}
            # optional per-axis scale, e.g. a foreshortened oblique depth axis
            scale = fr.get('axis_length_scale', {})
            tips = {k: o + L * scale.get(k, 1.0) * v for k, v in dirs.items()}
            zsym = fr.get('z_symbol')
            row.update(anchor_source=fr.get('anchor_note', ''), length_px=L,
                       axis_directions_canvas={k: [round(float(c), 6) for c in v] for k, v in dirs.items()},
                       z_symbol=zsym, axis_length_scale=scale)
            if fr.get('z_symbol_axis'):
                row['ring_axis'] = fr['z_symbol_axis']   # the ring marks this axis (top views: Y)
        boxes = draw_frame(cv, fr, o, tips, zsym, fr.get('z_symbol_axis', 'Z'))
        if panel.plain and not all(panel.contains(b) for b in boxes.values()):
            raise ValueError(f'{fr["name"]}: a label leaves its panel {fr["panel"]}')
        row.update(origin_px=[round(float(v), 2) for v in o],
                   endpoints_px={k: [round(float(c), 2) for c in v] for k, v in tips.items()},
                   label_boxes=boxes)
        frame_rows.append(row)

    point_rows = []
    for pt in spec.get('points', []):
        panel = panels[pt['panel']]
        if 'projected' in pt:
            xy = panel.project(sources.point(pt['projected']))
            mode = 'projected'
        else:
            xy = anchor_of(pt, panel)
            mode = 'measured' if 'landmark' in pt else 'illustrative'
        cv.dot(xy, r=pt.get('radius', 10), fill=tuple(pt.get('rgb', WHITE)))
        box = None
        if 'label' in pt:
            box = cv.text(pt['label']['text'], xy + np.asarray(pt['label']['offset'], float),
                          anchor=pt['label'].get('anchor', 'mm'), fill=tuple(pt['label'].get('rgb', WHITE)))
        point_rows.append({'point': pt.get('name', pt.get('label', {}).get('text')), 'mode': mode,
                           'xy_px': [round(float(v), 2) for v in xy], 'label_box': box,
                           **({'landmark': pt['landmark']} if 'landmark' in pt else {})})

    text_rows = []
    fmt = {}
    for fr in spec.get('frames', []):
        if fr['mode'] == 'projected' and fr['pose']['type'] == 'scene':
            fmt['floor_d_cm'] = f'{sources.floor_tf(fr["pose"])[1] * 100:.1f}'
    for tx in spec.get('texts', []):
        value = tx['text'].format(**fmt)
        box = cv.text(value, tx['xy'], anchor=tx.get('anchor', 'la'), fill=tuple(tx.get('rgb', WHITE)))
        if 'panel' in tx and not panels[tx['panel']].contains(box):
            raise ValueError(f'text {value!r} leaves its panel {tx["panel"]}')
        text_rows.append({'text': value, 'box': box, **({'panel': tx['panel']} if 'panel' in tx else {})})

    # checks on the fade: outside every drawn pixel the output equals the faded base
    out = np.asarray(cv.im)
    changed = np.any(out != base, axis=-1)
    photo_mask = np.zeros(changed.shape, bool)
    for p in spec['panels']:
        if p.get('background') == 'plain':
            continue
        x0, y0, x1, y1 = p['box_px']
        photo_mask[y0:y1, x0:x1] = True
    if photo_mask.any():
        fade_check = {'base_max_value': int(base[photo_mask].max()),
                      'expected_max_value': int(np.rint(255 * (1 - FADE))),
                      'photo_pixels_unchanged_fraction': round(float((~changed & photo_mask).sum() / photo_mask.sum()), 4)}
        if fade_check['base_max_value'] > fade_check['expected_max_value']:
            raise ValueError('fade check failed')
    else:
        fade_check = {'photo_panels': 0, 'note': 'plain diagram only; no photograph to fade'}
    # D-336: outside the photo boxes, every pixel that no shape, frame, point
    # or text drew (MirroredDraw mask) must be the pure black deck background
    # in the output image.
    undrawn_plain = ~photo_mask & (np.asarray(cv.drawn) == 0)
    if not np.all(out[undrawn_plain] == 0):
        raise ValueError('plain panel area is not the black deck background where nothing was drawn')
    dest = OUT / spec['output']
    cv.im.save(dest, format='PNG')
    return {'name': name, 'output': rel(dest), 'sha256': sha(dest), 'bytes': dest.stat().st_size,
            'pixel_size': list(cv.im.size), 'spec': rel(spec_path), 'spec_sha256': sha(spec_path),
            'spec_used': spec, 'thesis_source': spec.get('thesis_source', ''),
            'panels': panel_rows, 'frames': frame_rows, 'points': point_rows, 'texts': text_rows,
            'shapes': shape_rows, 'label_effective_pt_worst_box': round(label_pt(size), 2),
            'fade_check': fade_check}


def reprojection_checks(sources):
    """Projected marker origins against the pinned detector run on the deck copy
    of frame 505, and projected rig/desk anchors against the page-24 measurements."""
    img = cv2.imread(str(rp('presentation/defense_2026/figures/coordinate_frames/r6b_frame00505.png')))
    det = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50))
    params = cv2.aruco.DetectorParameters()
    params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_APRILTAG
    det.setDetectorParameters(params)
    corners, ids, _ = det.detectMarkers(img)
    found = {int(i): c.reshape(4, 2).mean(0) for i, c in zip(ids.ravel(), corners)}
    meta = sources.json('eval/output/recording_20260831_065553_aruco_raw_scaled.meta.json')['color_intrinsics']
    K = (meta['fx'], meta['fy'], meta['ppx'], meta['ppy'])

    def proj(P, K):
        return np.array([K[0] * P[0] / P[2] + K[2], K[1] * P[1] / P[2] + K[3]])
    out = {'detector': 'cv2.aruco.ArucoDetector DICT_5X5_50, CORNER_REFINE_APRILTAG (pinned settings, '
                       'knowledge/marker_facts.md), corner mean', 'opencv': cv2.__version__}
    calib = 'eval/output/scene_calibration_r6bc.json'
    csvp = 'eval/output/recording_20260831_065553_aruco_raw_scaled.csv'
    t_world = sources.resolve({'type': 'calibration_world', 'calibration': calib})[0]
    t_obj = sources.resolve({'type': 'aruco_row', 'csv': csvp, 'frame': 505, 'marker': 1})[0]
    t_wall = sources.resolve({'type': 'calibration_marker', 'calibration': calib, 'key': 'T_cam_wall'})[0]
    bounded = [('world_origin_vs_desk_marker', t_world, 2), ('object_origin_vs_cube_marker', t_obj, 1),
               ('wall_origin_vs_wall_marker', t_wall, 0)]
    out['residual_bound_px'] = {'bound_px': REPROJECTION_BOUND_PX, 'applies_to': [key for key, _, _ in bounded],
                                'rule': 'the generator raises when a bounded residual exceeds bound_px (D-303); '
                                        'the unity_* checks are recorded without a bound'}
    for key, P, mid in bounded:
        uv = proj(P, K)
        out[key] = {'projected_px': uv.round(2).tolist(), 'detected_px': found[mid].round(2).tolist(),
                    'residual_px': round(float(np.linalg.norm(uv - found[mid])), 2)}
        if not float(np.linalg.norm(uv - found[mid])) <= REPROJECTION_BOUND_PX:
            raise ValueError(f'{key}: reprojection residual {out[key]["residual_px"]} px exceeds '
                             f'{REPROJECTION_BOUND_PX} px (D-303)')
    # D-318 (round 10): the page-7 overlay projects the same calibrated World
    # and Wall poses on the matched still of R6b frame 533 (JPEG); the pinned
    # detector on that still bounds both residuals the same way.
    still = 'presentation/defense_2026/media/matched/r6b_frame_533.jpg'
    corners, ids, _ = det.detectMarkers(cv2.imread(str(rp(still))))
    found533 = {int(i): c.reshape(4, 2).mean(0) for i, c in zip(ids.ravel(), corners)}
    out['frame_533_still'] = still
    for key, P, mid in [('frame533_world_origin_vs_desk_marker', t_world, 2),
                        ('frame533_wall_origin_vs_wall_marker', t_wall, 0)]:
        uv = proj(P, K)
        res = float(np.linalg.norm(uv - found533[mid]))
        out[key] = {'projected_px': uv.round(2).tolist(), 'detected_px': found533[mid].round(2).tolist(),
                    'residual_px': round(res, 2)}
        out['residual_bound_px']['applies_to'].append(key)
        if not res <= REPROJECTION_BOUND_PX:
            raise ValueError(f'{key}: reprojection residual {res:.2f} px exceeds {REPROJECTION_BOUND_PX} px (D-303)')
    fov = sources.json(calib)['scene_geometry']['sensor_fov_y_deg']
    f = 240 / math.tan(math.radians(fov) / 2)
    KU = (f, f, 320.0, 240.0)
    anchors = sources.json('presentation/defense_2026/figures/coordinate_frames/anchored_photos.json')
    out['unity_reference'] = ('page-24 measured anchors in r6b_unity_f00505.png (anchored_photos.json '
                              'anchor_measurement): desk marker corner mean (345.5, 443.0), red pelvis sphere '
                              'centroid (340.0, 347.7)')
    out['unity_anchor_text'] = anchors['anchor_measurement']
    uv = proj(t_world, KU)
    out['unity_world_origin_vs_desk_marker'] = {'projected_px': uv.round(2).tolist(), 'measured_px': [345.5, 443.0],
                                                'residual_px': round(float(np.linalg.norm(uv - [345.5, 443.0])), 2)}
    rig = {'type': 'rig_joint', 'calibration': calib,
           'person_log': 'eval/output/unity_check_r6b_v9/unity_person_log.csv', 'frame': 505, 'joint': 'hip'}
    uv = proj(sources.point(rig), KU)
    out['unity_pelvis_vs_red_sphere'] = {'projected_px': uv.round(2).tolist(), 'measured_px': [340.0, 347.7],
                                         'residual_px': round(float(np.linalg.norm(uv - [340.0, 347.7])), 2),
                                         'note': 'the held sphere sits slightly in front of the bone along the '
                                                 'line of sight (thesis Section 6.3), so its centre projects '
                                                 'near the bone origin'}
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--measure-tpose', action='store_true',
                    help='run MediaPipe on tpose_source.jpg and write the landmark JSON, then stop')
    ap.add_argument('--only', choices=FIGURES, action='append', help='render only these figures')
    args = ap.parse_args()
    if args.measure_tpose:
        measure_tpose()
        return
    sources = Sources()
    names = args.only or FIGURES
    rows = [render_figure(n, sources) for n in names]
    for r in rows:
        print(f'{r["output"]}  {r["sha256"]}')
    if args.only:
        print('manifest not written (--only)')
        return
    checks = reprojection_checks(sources)
    inputs = {k: v for k, v in sorted(sources.read.items())}
    manifest = {
        'purpose': ('Coordinate-frame overlays on faded photographs and plain diagram panels for the '
                    'frame_figure slot (round 8, M2a; plain panels and the page-7 static markers round 10, M2a).'),
        'generator': rel(Path(__file__)), 'generator_sha256': sha(Path(__file__)),
        'axis_renderer_colours': 'presentation/defense_2026/anim/coordinate_axes.py AXIS_COLORS',
        'axis_colors': AXIS_COLORS,
        'command': ['/home/luo/anaconda3/bin/python presentation/defense_2026/make_frame_overlay_figures.py --measure-tpose',
                    '/home/luo/anaconda3/bin/python presentation/defense_2026/make_frame_overlay_figures.py'],
        'working_directory': 'repository root',
        'interpreter': sys.executable, 'python': platform.python_version(),
        'library_versions': {'opencv': cv2.__version__, 'numpy': np.__version__,
                             'pillow': Image.__version__},
        'fade': {'factor': FADE, 'operation': 'rint(resized_photo * (1 - 0.5)), overlays drawn afterwards',
                 'source': 'eval/failure/make_label_compare_fig.py render_panel; figures/recovery/manifest.json --fade 0.5'},
        'label_size': {'font': FONT, 'em_px': LABEL_PX, 'canvas_px': list(CANVAS),
                       'deck_boxes_in': BOX_IN,
                       'effective_pt': {f'{w}x{h} in box': round(LABEL_PX * min(w / CANVAS[0], h / CANVAS[1]) * 72, 2)
                                        for w, h in BOX_IN},
                       'rule': 'effective pt = em_px / (source px per placed inch) * 72 (knowledge/deck_fonts.md)'},
        'overlay_modes': {'projected': 'axes pushed through the panel camera model from a pinned calibrated pose',
                          'illustrative': 'anchor and axis directions declared in the spec (anchors may be measured)'},
        'inputs': inputs,
        'reprojection_checks': checks,
        'outputs': rows,
    }
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=1) + '\n')
    print('wrote', rel(OUT / 'manifest.json'))


if __name__ == '__main__':
    main()
