#!/usr/bin/env python3
"""Slide 33 three-panel film: recorded RGB, Python FK skeleton, Unity avatar.

2026-10-06 (plan declarative-stargazing-phoenix.md, Milestone C, D-393). One
film of recording r7 (recording_20260909_000024, two-hand rail handover),
frames 0-1497 at 30 fps, three 480 x 640 portrait panels side by side:

  left    the recorded colour frame, decoded from the bag with
          v3/replay/bag_source.py BagSource(paced=False), a fixed 3:4 crop
          around the person (chosen once from frame 630);
  middle  a matplotlib 3D skeleton computed here by forward kinematics
          (v3/core/fk.py) from the stream Unity rendered
          (unity_capture/r7/integrated_stream.csv: pelvis point and the 13
          angles) with the r7 segment lengths of unity_capture/r7/
          rig_dimensions.csv, in Camera' coordinates (sensor frame with y
          reversed), fixed view elev 15 azim -75 (v1/mediapipe/
          plot_skeleton.py), fixed limits over the recording;
  right   the Unity master unity_capture/r7/Fresh_Unity_R7_Model_Axes.mp4
          (1440 x 1080, frame n = source frame n), cropped to the same
          region as the RGB panel, scaled by 1440 / 640 = 2.25.

Frame map: output frame n = recording colour frame n = stream frame n =
Unity master frame n (identity). Checked here: the BagSource timestamps equal
the stream time_s, and unity_person_log.csv time_s equals the stream time_s.

FK check: on ten frames sampled evenly over 0-1497 the Python FK wrists
(and elbows and shoulders) are compared with the wrists Unity logged
(unity_person_log.csv, mapped from Unity world into Camera' by the anchor
rotation of unity_capture/validate_axes_capture.py); tolerance 1 cm (plan).

Run from the repository root with the thesis Python:

    MPLCONFIGDIR=<scratch> /home/luo/anaconda3/bin/python -B \
        presentation/defense_2026/anim/three_panel_fk.py [--review-dir DIR]

Writes media/p33_three_panel.mp4, media/p33_three_panel_poster.png (frame
630) and media/provenance/p33_three_panel.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'v3' / 'core'))
sys.path.insert(0, str(ROOT / 'v3' / 'replay'))
sys.path.insert(0, str(ROOT / 'eval'))

import matplotlib  # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from scipy.spatial.transform import Rotation  # noqa: E402

import fk  # noqa: E402  (v3/core/fk.py)
from bag_source import BagSource  # noqa: E402  (v3/replay/bag_source.py)
from common import paths  # noqa: E402  (eval/common/paths.py)

STEM = 'recording_20260909_000024'
CAPTURE = HERE / 'unity_capture' / 'r7'
STREAM = CAPTURE / 'integrated_stream.csv'
PERSON_LOG = CAPTURE / 'unity_person_log.csv'
RIG = CAPTURE / 'rig_dimensions.csv'
MASTER = CAPTURE / 'Fresh_Unity_R7_Model_Axes.mp4'
CAPTURE_MANIFEST = CAPTURE / 'capture_manifest.json'
BAG = ROOT / 'recordings' / 'R7_rail_handover_two_hand_accepted_20260909_000024.bag'
LANDMARKS = ROOT / 'v1' / 'mediapipe' / 'output' / f'{STEM}_landmarks_filtered.csv'
CALIB = paths.calib_for(STEM)
MOVIE = HERE / 'media' / 'p33_three_panel.mp4'
POSTER = HERE / 'media' / 'p33_three_panel_poster.png'
PROVENANCE = HERE / 'media' / 'provenance' / 'p33_three_panel.json'
FONT = Path(matplotlib.get_data_path()) / 'fonts' / 'ttf' / 'DejaVuSans.ttf'

# Frames, rate and encoder. 1498 frames 0-1497: the frames the Unity master
# holds (capture_manifest.json source_frames, count 1498) and the colour
# frames BagSource yields. FPS 30 and the encoder: anim/bank_axes_kinematics.py
# build() (libx264 preset slow, CRF 19, yuv420p, faststart), as in
# anim/chain_growth.py.
FIRST, LAST = 0, 1497
FPS = 30
CRF = 19
POSTER_FRAME = 630  # plan, Milestone C (the frame the D-390 still used)

# Geometry of the film (plan, Milestone C Design): 1440 x 640, three
# 480 x 640 panels. Title band: 52 px of each panel (display choice, this
# script); the scaled 3:4 crop fills the 588 rows below it from its top, so
# the bottom 52 rows of the scaled crop (desk front edge) are not shown.
W, H = 1440, 640
PW, PH = 480, 640
BAND = 52
TITLE_PX, NOTE_PX, COUNTER_PX = 34, 20, 26  # display choices, this script
TITLES = ['Recorded RGB', 'Python FK', 'Unity avatar']

# RGB crop (x0, y0, x1, y1) in the 640 x 480 colour frame: full height, 3:4
# (360 x 480). Chosen once from frame 630: the person spans about x 215-495
# there (viewed), so x 160-520 keeps both hands with margin and keeps most of
# the cube at its start position (x about 130-200 at frame 0). x0 is a
# multiple of 4 so that the Unity crop (times 2.25) is integer.
RGB_SIZE = (640, 480)
RGB_CROP = (160, 0, 520, 480)
UNITY_SIZE = (1440, 1080)
UNITY_SCALE = UNITY_SIZE[0] / RGB_SIZE[0]  # 2.25: SensorPOVCamera renders the sensor view at 1440 x 1080
UNITY_CROP = tuple(int(round(v * UNITY_SCALE)) for v in RGB_CROP)

# Colours: deck axis colours (anim/coordinate_axes.py AXIS_COLORS via
# anim/chain_growth.py LAYERS): L24 red #FF4040, L23 and shoulders green
# #40E070, elbows blue #408CFF, wrists amber #E8B35A (slide 21 accent); bones
# white (plan).
RED, GREEN, BLUE, AMBER, WHITE = '#FF4040', '#40E070', '#408CFF', '#E8B35A', '#FFFFFF'
# View: v1/mediapipe/plot_skeleton.py view_init(elev=15, azim=-75), equal box.
ELEV, AZIM = 15, -75
LIMIT_STEP_M = 0.05  # half-range rounded up to 5 cm (display choice, this script)
# FK check (plan): ten frames, 1 cm.
CHECK_FRAMES = [int(v) for v in np.linspace(FIRST, LAST, 10).round()]
CHECK_TOL_M = 0.01


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    path = Path(path).resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def verify_inputs():
    """Every Unity capture input must still have the bytes its manifest pins."""
    manifest = json.loads(CAPTURE_MANIFEST.read_text())
    pinned = {CAPTURE / name: digest for name, digest in manifest['outputs'].items()}
    pinned[LANDMARKS] = manifest['sources'][rel(LANDMARKS)]
    pinned[CALIB] = manifest['sources'][rel(CALIB)]
    for path in [STREAM, PERSON_LOG, RIG, MASTER, LANDMARKS, CALIB]:
        if sha(path) != pinned[path]:
            raise ValueError(f'{rel(path)} differs from capture_manifest.json')
    return {rel(p): sha(p) for p in [STREAM, PERSON_LOG, RIG, MASTER, CAPTURE_MANIFEST, LANDMARKS,
                                     CALIB, ROOT / 'v3/core/fk.py', ROOT / 'v3/replay/bag_source.py',
                                     ROOT / 'v3/vendor/v1/root_frame.py', ROOT / 'v3/vendor/v1/shoulder.py']}


def anchor_rotation():
    """Camera' -> Unity world rotation: unity_capture/validate_axes_capture.py
    anchor = G @ S @ R_desk_cam @ F (IntegratedSceneReceiver.cs PersonAnchor)."""
    cal = json.loads(CALIB.read_text())
    world_camera = np.linalg.inv(np.asarray(cal['T_cam_desk']))
    S = np.eye(3)[[0, 2, 1]]
    F = np.diag([1.0, -1.0, 1.0])
    g = np.asarray(cal['scene_geometry']['gravity_up_unity'], float)
    g /= np.linalg.norm(g)
    G = Rotation.align_vectors([[0, 1, 0]], [g])[0].as_matrix()
    return G @ S @ world_camera[:3, :3] @ F


def rig_lengths():
    rig = pd.read_csv(RIG).set_index('segment')['meters']
    return {k: float(rig[k]) for k in ['upper_arm_R', 'forearm_R', 'upper_arm_L', 'forearm_L',
                                       'shoulder_width', 'torso_hip_to_midshoulder']}


def hip_width():
    """Median L23-L24 distance of the filtered r7 landmarks on frames where
    both hips are measured (src 0) and unfiltered-raw (flag 0)."""
    d = pd.read_csv(LANDMARKS)
    ok = ((d.left_hip_src == 0) & (d.right_hip_src == 0) & (d.left_hip_flag == 0)
          & (d.right_hip_flag == 0))
    r = d.loc[ok, ['right_hip_x', 'right_hip_y', 'right_hip_z']].to_numpy(float)
    l = d.loc[ok, ['left_hip_x', 'left_hip_y', 'left_hip_z']].to_numpy(float)
    w = np.linalg.norm(r - l, axis=1)
    w = w[np.isfinite(w)]
    return float(np.median(w)), int(len(w))


def build_model():
    stream = pd.read_csv(STREAM).set_index('frame')
    frames = np.arange(FIRST, LAST + 1)
    log = pd.read_csv(PERSON_LOG)
    dup = log[log.frame.duplicated(keep=False)]
    cols = [c for c in log.columns if c not in ('frame', 'time_s')]
    dup_spread = float(dup.groupby('frame')[cols].agg(lambda x: x.max() - x.min()).max().max()) if len(dup) else 0.0
    log = log.drop_duplicates('frame').set_index('frame').sort_index()
    if not set(frames) <= set(log.index) or not set(frames) <= set(stream.index):
        raise ValueError('stream or Unity person log does not cover frames 0-1497')
    A = stream.loc[frames, [f'a{i}' for i in range(13)]].to_numpy(float)
    pel = stream.loc[frames, ['pel_x', 'pel_y', 'pel_z']].to_numpy(float)
    if not (np.isfinite(A).all() and np.isfinite(pel).all()):
        raise ValueError('non-finite stream values')
    time_stream = stream.loc[frames, 'time_s'].to_numpy(float)
    time_log_err = float(np.abs(log.loc[frames, 'time_s'].to_numpy(float) - time_stream).max())
    pel_log_err = float(np.abs(log.loc[frames, ['pel_x', 'pel_y', 'pel_z']].to_numpy(float) - pel).max())

    # Unity world -> Camera': X_cam' = R_a^T (X_world - t), t = the anchor
    # position, recovered as the median of hip_world - R_a pel (the receiver
    # pins the hip bone to anchor.TransformPoint(pel)).
    Ra = anchor_rotation()
    hip_w = log.loc[frames, ['hip_x', 'hip_y', 'hip_z']].to_numpy(float)
    t_all = hip_w - pel @ Ra.T
    t = np.median(t_all, axis=0)
    t_spread = float(np.abs(t_all - t).max())

    def unity(prefix):
        return (log.loc[frames, [f'{prefix}_{a}' for a in 'xyz']].to_numpy(float) - t) @ Ra

    u = {k: unity(k) for k in ['rsh', 'lsh', 'rel', 'lel', 'rh', 'lh']}
    L = rig_lengths()
    # Shoulders: pelvis point plus a constant offset in the root frame
    # (fk.hip_shoulder_offset, D-037 anchor b), measured from the rig's
    # rendered shoulders; the per-frame spread shows the rig torso is rigid.
    off_r, n_r = fk.hip_shoulder_offset(A, pel, u['rsh'])
    off_l, n_l = fk.hip_shoulder_offset(A, pel, u['lsh'])
    R = fk.root_matrices(A)
    spread_r = float(np.abs(np.einsum('nji,nj->ni', R, u['rsh'] - pel) - off_r).max())
    spread_l = float(np.abs(np.einsum('nji,nj->ni', R, u['lsh'] - pel) - off_l).max())
    sh_r = fk.hip_anchor(A, pel, off_r)
    sh_l = fk.hip_anchor(A, pel, off_l)
    el_r, wr_r = fk.fk_arm_series(A, 'right', L['upper_arm_R'], L['forearm_R'], sh_r)
    el_l, wr_l = fk.fk_arm_series(A, 'left', L['upper_arm_L'], L['forearm_L'], sh_l)
    # Hips: the pelvis point is the solver's hip midpoint
    # (eval/unity_check/send_scene_r5.py) and the root x axis is the unit
    # vector L23 -> L24 (v3/vendor/v1/root_frame.py build_root_frame), so
    # L24 / L23 = pel +/- (hip width / 2) R_root[:, 0].
    hw, hw_n = hip_width()
    l24 = pel + 0.5 * hw * R[:, :, 0]
    l23 = pel - 0.5 * hw * R[:, :, 0]
    joints = {'L24': l24, 'L23': l23, 'L12': sh_r, 'L11': sh_l, 'L14': el_r, 'L13': el_l,
              'L16': wr_r, 'L15': wr_l}
    for k, v in joints.items():
        if not np.isfinite(v).all():
            raise ValueError(f'non-finite FK joint {k}')

    def errs(a, b):
        return np.linalg.norm(a - b, axis=1)

    pairs = {'right_wrist': (wr_r, u['rh']), 'left_wrist': (wr_l, u['lh']),
             'right_elbow': (el_r, u['rel']), 'left_elbow': (el_l, u['lel']),
             'right_shoulder': (sh_r, u['rsh']), 'left_shoulder': (sh_l, u['lsh'])}
    sampled = []
    for f in CHECK_FRAMES:
        i = f - FIRST
        sampled.append({'frame': f, **{f'{k}_error_cm': round(float(errs(a[i:i + 1], b[i:i + 1])[0]) * 100, 6)
                                       for k, (a, b) in pairs.items()}})
    wrist_max = max(max(r['right_wrist_error_cm'], r['left_wrist_error_cm']) for r in sampled)
    check = {
        'statement': ('Python FK (fk.hip_anchor shoulders, fk.fk_arm elbows and wrists, r7 rig lengths) '
                      'against the joints Unity logged in unity_person_log.csv, mapped into Camera\'.'),
        'frames': CHECK_FRAMES, 'tolerance_cm': CHECK_TOL_M * 100,
        'max_wrist_error_cm_sampled': wrist_max,
        'status': 'PASS' if wrist_max <= CHECK_TOL_M * 100 else 'FAIL',
        'sampled': sampled,
        'all_frames_max_error_cm': {k: float(errs(a, b).max()) * 100 for k, (a, b) in pairs.items()},
        'unity_world_to_camera_prime': {
            'rotation': 'validate_axes_capture.py anchor = G S R_desk_cam F', 'R_anchor': Ra.tolist(),
            'anchor_position_m': t.tolist(), 'anchor_position_max_spread_m': t_spread},
        'shoulder_offsets_root_frame_m': {'right': off_r.tolist(), 'left': off_l.tolist(),
                                          'frames': [n_r, n_l],
                                          'max_spread_m': {'right': spread_r, 'left': spread_l}},
        'stream_vs_log': {'max_time_s_difference': time_log_err, 'max_pelvis_difference_m': pel_log_err,
                          'duplicate_log_rows': int(len(dup)), 'duplicate_rows_max_difference': dup_spread},
    }
    if check['status'] != 'PASS':
        print(f'BLOCKER: FK check failed, max sampled wrist error {wrist_max:.4f} cm', file=sys.stderr)
    model = {'lengths_m': L, 'hip_width_m': hw, 'hip_width_frames': hw_n,
             'hip_width_source': (f'{rel(LANDMARKS)}: median |right_hip - left_hip| over frames with '
                                  'both hips src 0 and flag 0 (display geometry only)'),
             'pelvis': 'integrated_stream.csv pel_x..z, the solver hip midpoint after the display smoother'}
    return joints, check, model, time_stream


# Plot coordinates: matplotlib (X, Y, Z) = Camera' (x, z, y), so depth runs
# into the view and y is up, as in v1/mediapipe/plot_skeleton.py.
BONES = [('L24', 'L23'), ('L24', 'L12'), ('L23', 'L11'), ('L12', 'L11'),
         ('L12', 'L14'), ('L14', 'L16'), ('L11', 'L13'), ('L13', 'L15')]
GROUPS = [(['L24'], RED, 11), (['L23', 'L12', 'L11'], GREEN, 9), (['L14', 'L13'], BLUE, 9),
          (['L16', 'L15'], AMBER, 9)]


def plot_xyz(p):
    p = np.asarray(p)
    return p[..., 0], p[..., 2], p[..., 1]


def limits(joints):
    pts = np.concatenate([np.stack(plot_xyz(v), axis=-1) for v in joints.values()])
    lo, hi = pts.min(0), pts.max(0)
    centre = (lo + hi) / 2
    half = float(np.ceil((hi - lo).max() / 2 / LIMIT_STEP_M) * LIMIT_STEP_M)
    return centre, half, lo, hi


class SkeletonPanel:
    """Fixed Agg canvas: static axes drawn once, joints redrawn per frame."""

    def __init__(self, joints, width, height):
        self.joints = joints
        self.centre, self.half, self.lo, self.hi = limits(joints)
        plt.rcParams['font.family'] = 'DejaVu Sans'
        self.fig = plt.figure(figsize=(width / 100, height / 100), dpi=100, facecolor='black')
        # Axes box placed so that the y label at the right edge stays inside
        # the panel and the x label clears the frame counter (viewed at frame
        # 630; display choice, this script).
        ax = self.fig.add_axes([-0.12, 0.04, 1.12, 1.03], projection='3d', facecolor='black')
        c, h = self.centre, self.half
        ax.set_xlim(c[0] - h, c[0] + h)
        ax.set_ylim(c[1] - h, c[1] + h)
        ax.set_zlim(c[2] - h, c[2] + h)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=ELEV, azim=AZIM)
        grey = '#9A9A9A'
        for axis, name in [(ax.xaxis, 'x (m)'), (ax.yaxis, 'z (m)'), (ax.zaxis, 'y (m)')]:
            axis.set_pane_color((0.06, 0.06, 0.06, 1.0))
            axis._axinfo['grid']['color'] = (0.3, 0.3, 0.3, 1.0)
            axis.line.set_color(grey)
            axis.set_major_locator(matplotlib.ticker.MultipleLocator(0.2))
            axis.label.set_color('white')
            axis.label.set_fontsize(15)
            axis.set_label_text(name)
        ax.tick_params(colors=grey, labelsize=10)
        self.ax = ax
        self.bones = [ax.plot([], [], [], color=WHITE, lw=3.0, solid_capstyle='round')[0] for _ in BONES]
        self.dots = [ax.plot([], [], [], 'o', color=col, ms=ms, mec='black', mew=0.8)[0]
                     for _, col, ms in GROUPS]
        for a in self.bones + self.dots:
            a.set_visible(False)
        self.fig.canvas.draw()
        self.background = self.fig.canvas.copy_from_bbox(self.fig.bbox)
        for a in self.bones + self.dots:
            a.set_visible(True)

    def render(self, i):
        canvas = self.fig.canvas
        canvas.restore_region(self.background)
        for line, (a, b) in zip(self.bones, BONES):
            x, y, z = plot_xyz(np.stack([self.joints[a][i], self.joints[b][i]]))
            line.set_data_3d(x, y, z)
            self.ax.draw_artist(line)
        for dot, (names, _, _) in zip(self.dots, GROUPS):
            x, y, z = plot_xyz(np.stack([self.joints[n][i] for n in names]))
            dot.set_data_3d(x, y, z)
            self.ax.draw_artist(dot)
        return np.asarray(canvas.buffer_rgba())[:, :, :3].copy()


class UnityReader:
    """Sequential raw RGB frames of the Unity master through ffmpeg."""

    def __init__(self, path, size):
        self.size = size
        self.nbytes = size[0] * size[1] * 3
        self.proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'rawvideo',
                                      '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)

    def read(self):
        buf = self.proc.stdout.read(self.nbytes)
        if len(buf) != self.nbytes:
            return None
        return np.frombuffer(buf, np.uint8).reshape(self.size[1], self.size[0], 3)

    def close(self):
        rest = self.proc.stdout.read()
        self.proc.stdout.close()
        self.proc.wait()
        return len(rest) // self.nbytes


def crop_panel(img, box):
    x0, y0, x1, y1 = box
    im = Image.fromarray(np.ascontiguousarray(img[y0:y1, x0:x1]))
    im = im.resize((PW, PW * (y1 - y0) // (x1 - x0)), Image.LANCZOS)
    return np.asarray(im)[:PH - BAND]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--review-dir', type=Path, help='also save frames 0, 630 and 1200 as PNG here')
    args = ap.parse_args()
    if (RGB_CROP[2] - RGB_CROP[0]) * 4 != (RGB_CROP[3] - RGB_CROP[1]) * 3:
        raise ValueError('RGB crop is not 3:4')
    if any(abs(v * UNITY_SCALE - round(v * UNITY_SCALE)) > 1e-9 for v in RGB_CROP):
        raise ValueError('Unity crop is not integer')
    inputs = verify_inputs()
    joints, check, model, time_stream = build_model()
    sk = SkeletonPanel(joints, PW, PH - BAND)
    font_title = ImageFont.truetype(str(FONT), TITLE_PX)
    font_note = ImageFont.truetype(str(FONT), NOTE_PX)
    font_counter = ImageFont.truetype(str(FONT), COUNTER_PX)

    MOVIE.parent.mkdir(parents=True, exist_ok=True)
    PROVENANCE.parent.mkdir(parents=True, exist_ok=True)
    command = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
               '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264',
               '-preset', 'slow', '-crf', str(CRF), '-threads', '2', '-pix_fmt', 'yuv420p',
               '-movflags', '+faststart', str(MOVIE)]
    writer = subprocess.Popen(command, stdin=subprocess.PIPE)
    unity = UnityReader(MASTER, UNITY_SIZE)
    wanted = {0, POSTER_FRAME, 1200}
    review, poster, bag_times, overlay_frames = {}, None, [], []
    n_written = 0
    with BagSource(BAG, paced=False) as bag:
        for idx, t_s, color_bgr, _depth in bag.frames():
            if idx > LAST:
                break
            if idx != n_written:
                raise ValueError(f'bag frame index {idx} out of sequence')
            bag_times.append(t_s)
            rgb = np.ascontiguousarray(color_bgr[:, :, ::-1])
            if rgb.shape[:2] != (RGB_SIZE[1], RGB_SIZE[0]):
                raise ValueError(f'unexpected colour frame size {rgb.shape}')
            # Burned-in landmark drawing in the recorded stream: count of the
            # overlay's orange dot colour (diagnostic only, never altered).
            r, g, b = (rgb[:, :, k].astype(np.int16) for k in range(3))
            orange = int(((r > 220) & (g > 110) & (g < 170) & (b < 60)).sum())
            if orange:
                overlay_frames.append([idx, orange])
            urgb = unity.read()
            if urgb is None:
                raise ValueError(f'Unity master ended before frame {idx}')
            frame = np.zeros((H, W, 3), np.uint8)
            frame[BAND:, 0:PW] = crop_panel(rgb, RGB_CROP)
            frame[BAND:, PW:2 * PW] = sk.render(idx - FIRST)
            frame[BAND:, 2 * PW:3 * PW] = crop_panel(urgb, UNITY_CROP)
            im = Image.fromarray(frame)
            draw = ImageDraw.Draw(im)
            for k, title in enumerate(TITLES):
                draw.text((k * PW + PW / 2, BAND / 2), title, font=font_title, fill='white', anchor='mm')
            draw.text((PW + 12, BAND + 8), "axes: Camera', m", font=font_note, fill='#BBBBBB', anchor='la')
            draw.text((PW + 12, H - 12), f'frame {idx}', font=font_counter, fill='white', anchor='ld')
            writer.stdin.write(im.tobytes())
            if idx == POSTER_FRAME:
                poster = im.copy()
            if args.review_dir and idx in wanted:
                args.review_dir.mkdir(parents=True, exist_ok=True)
                path = args.review_dir / f'p33_frame_{idx:04d}.png'
                im.save(path)
                review[idx] = str(path)
            n_written += 1
    unity_left = unity.close()
    writer.stdin.close()
    if writer.wait() != 0:
        raise RuntimeError('ffmpeg failed')
    if n_written != LAST - FIRST + 1:
        raise ValueError(f'wrote {n_written} frames, expected {LAST - FIRST + 1}')
    bag_dt = float(np.abs(np.asarray(bag_times) - time_stream).max())
    if bag_dt > 1e-5:
        raise ValueError(f'bag timestamps differ from stream time_s by {bag_dt} s')
    if unity_left != 0:
        raise ValueError(f'Unity master holds {unity_left} frames beyond {LAST}')
    poster.save(POSTER, format='PNG')
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(MOVIE), '-f', 'null', '-'], check=True)
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries',
        'stream=codec_name,pix_fmt,width,height,nb_read_frames,r_frame_rate,duration',
        '-of', 'json', str(MOVIE)]))['streams'][0]
    if int(probe['nb_read_frames']) != n_written or [probe['width'], probe['height']] != [W, H]:
        raise ValueError(f'decode check failed: {probe}')

    report = {
        'status': 'PASS' if check['status'] == 'PASS' else 'FK_CHECK_FAIL',
        'slide': 33, 'kind': 'three_panel_fk_film',
        'purpose': ('Slide 33: recorded RGB, the Python forward-kinematics skeleton and the Unity avatar, '
                    'synchronised frame by frame (author request 2026-10-06, plan Milestone C, D-393).'),
        'asset': rel(MOVIE), 'poster': rel(POSTER), 'poster_is': f'frame {POSTER_FRAME}',
        'frames': n_written, 'first_frame': FIRST, 'last_frame': LAST, 'fps': FPS,
        'duration_s': n_written / FPS, 'dimensions': [W, H],
        'sha256': {'mp4': sha(MOVIE), 'png': sha(POSTER)},
        'bytes': {'mp4': MOVIE.stat().st_size, 'png': POSTER.stat().st_size},
        'recording': {'stem': STEM, 'alias': 'r7 (handover)', 'bag': rel(BAG),
                      'bag_bytes': BAG.stat().st_size, 'same_bytes_as': 'Video/recording_20260909_000024.bag',
                      'decode': 'v3/replay/bag_source.py BagSource(paced=False).frames(), colour stream BGR8 '
                                'reversed to RGB, one sequential pass'},
        'frame_map': {
            'statement': ('Identity: output frame n = bag colour frame n (BagSource idx) = integrated_stream.csv '
                          'frame n = unity_person_log.csv frame n = Unity master frame n, n = 0..1497.'),
            'bag_vs_stream_max_time_difference_s': bag_dt,
            'log_vs_stream_max_time_difference_s': check['stream_vs_log']['max_time_s_difference'],
            'unity_master': ('frame n = source frame n per unity_capture/r7/capture_manifest.json '
                             'source_frames (0-1497, none missing); master read sequentially, '
                             f'{n_written} frames used, {unity_left} left over'),
            'stream_frame_1498': 'present in integrated_stream.csv, not in the master or the bag decode; not used',
        },
        'inputs': inputs,
        'layout': {
            'panels': [{'title': TITLES[k], 'x': [k * PW, (k + 1) * PW], 'y': [0, H]} for k in range(3)],
            'title_band_px': BAND, 'title_px': TITLE_PX, 'note_px': NOTE_PX, 'counter_px': COUNTER_PX,
            'font': 'DejaVu Sans (' + rel(FONT) + ')',
            'band_note': ('Each 3:4 crop is scaled to 480 x 640 and its top 588 rows fill the panel below the '
                          '52 px title band; the bottom 52 scaled rows (desk front edge) are not shown.'),
        },
        'crop_boxes': {
            'rgb': {'box_xyxy': list(RGB_CROP), 'source_size': list(RGB_SIZE), 'aspect': '3:4',
                    'scale': PW / (RGB_CROP[2] - RGB_CROP[0]),
                    'visible_source_rows': [RGB_CROP[1], RGB_CROP[1] + (PH - BAND) * (RGB_CROP[2] - RGB_CROP[0]) // PW],
                    'chosen_from_frame': POSTER_FRAME,
                    'why': 'person spans about x 215-495 at frame 630; both hands kept with margin, cube start '
                           'position (x about 130-200 at frame 0) mostly kept'},
            'unity': {'box_xyxy': list(UNITY_CROP), 'source_size': list(UNITY_SIZE), 'aspect': '3:4',
                      'scale': PW / (UNITY_CROP[2] - UNITY_CROP[0]),
                      'rule': 'RGB box times 2.25 (1440 / 640): the calibrated SensorPOVCamera renders the sensor view'},
            'resample': 'PIL LANCZOS',
        },
        'skeleton': {
            'coordinates': "Camera' (sensor frame with y reversed; solver space of v3/core/fk.py)",
            'plot_axes': "matplotlib X = x, Y = z (depth), Z = y (up); labels 'x (m)', 'z (m)', 'y (m)'",
            'view': {'elev': ELEV, 'azim': AZIM, 'box_aspect': [1, 1, 1],
                     'source': 'v1/mediapipe/plot_skeleton.py view_init(elev=15, azim=-75)'},
            'axis_limits_m': {'centre_plot_xyz': sk.centre.tolist(), 'half_range': sk.half,
                              'x': [sk.centre[0] - sk.half, sk.centre[0] + sk.half],
                              'z': [sk.centre[1] - sk.half, sk.centre[1] + sk.half],
                              'y': [sk.centre[2] - sk.half, sk.centre[2] + sk.half],
                              'data_min_plot_xyz': sk.lo.tolist(), 'data_max_plot_xyz': sk.hi.tolist(),
                              'rule': 'equal cube over all joints of frames 0-1497, half range rounded up to 0.05 m'},
            'colours': {'L24 root': RED, 'L23 and shoulders L12, L11': GREEN, 'elbows L14, L13': BLUE,
                        'wrists L16, L15': AMBER, 'bones': WHITE, 'background': 'black',
                        'source': 'anim/chain_growth.py LAYERS (deck axis colours, slide 21 amber)'},
            'bones': [list(b) for b in BONES],
            'model': model,
            'fk': ('shoulders = fk.hip_anchor(pelvis, offset), offset = fk.hip_shoulder_offset of the rig shoulders; '
                   'elbows and wrists = fk.fk_arm with rig_dimensions.csv upper_arm and forearm lengths'),
        },
        'fk_check': check,
        'recorded_overlay': {
            'finding': ('The recorded colour stream itself carries a burned-in landmark drawing on its first '
                        'frames; shown as recorded, not altered.'),
            'detector': 'count of pixels with R > 220, 110 < G < 170, B < 60 (the drawing\'s orange dots)',
            'frames_with_count': overlay_frames[:100],
            'frames_with_count_total': len(overlay_frames),
        },
        'decode_check': probe,
        'encoding': {'command': command[:-1] + ['<asset>'],
                     'source': 'anim/bank_axes_kinematics.py build() ffmpeg call (as anim/chain_growth.py)'},
        'review_frames': {str(k): v for k, v in review.items()},
        'generator': rel(Path(__file__)), 'generator_sha256': sha(Path(__file__)),
        'command': 'MPLCONFIGDIR=<scratch> /home/luo/anaconda3/bin/python -B presentation/defense_2026/anim/three_panel_fk.py',
        'interpreter': sys.executable, 'python': platform.python_version(),
        'matplotlib': matplotlib.__version__,
        'playback_in_powerpoint': 'not verified (author check)',
    }
    PROVENANCE.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='ascii')
    print(f'{report["status"]}: {rel(MOVIE)} {n_written} frames, {n_written / FPS:.3f} s, {report["sha256"]["mp4"]}')
    print(f'FK check: max sampled wrist error {check["max_wrist_error_cm_sampled"]:.6f} cm over {CHECK_FRAMES}')
    for k, v in review.items():
        print(f'review frame {k}: {v}')


if __name__ == '__main__':
    main()
