"""Projection and drawing helpers for the M8a side-by-side films (D-039).

COPIED, not imported (plan A4: presentation code is never a V3
dependency), from the defence renderer:

- project_pinhole, make_pinhole_projector, CAMERA_TO_CAMERA_PRIME,
  AXIS_COLORS, FONT_PATH: presentation/defense_2026/anim/coordinate_axes.py
  (project_pinhole is adapted to return NaN for points that cannot be
  projected instead of raising, because a film frame must still render
  when one point is missing or behind the camera).
- CAMERA_SCALE 1.2 (640x480 source -> 768x576 panel), the LANCZOS
  resize, FOCUS_WHITE, BORDER and the label/skeleton drawing pattern:
  presentation/defense_2026/anim/unified_panels.py (CAMERA_RECT, compose,
  draw_skeleton, label).

Coordinate conventions: rig points are in the solver (Unity) space,
i.e. camera optical with y flipped (vendor/v1/root_frame.py
unity_from_sensor); CAMERA_TO_CAMERA_PRIME maps them back to the
camera-optical frame before the pinhole. The recordings' colour
intrinsics carry zero distortion coefficients (every extraction
.meta.json: model inverse_brown_conrady, coeffs all 0), so the plain
pinhole equals rs2_project_point_to_pixel (tests/test_side_by_side.py).

Status colours (D-013 vocabulary, values from
Unity/Assets/Scripts/V3/V3PersonReceiver.cs estimatedColor and
lostColor, converted to 8-bit by round(255 x c)); MEASURED is drawn
white (brief M8a) rather than the Unity side colours.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# --- copied constants -------------------------------------------------------
AXIS_COLORS = {"X": "#FF4040", "Y": "#40E070", "Z": "#408CFF"}  # coordinate_axes.py
FONT_PATH = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")  # coordinate_axes.py
CAMERA_TO_CAMERA_PRIME = np.diag([1.0, -1.0, 1.0])               # coordinate_axes.py
SOURCE_SIZE = (640, 480)                                         # unified_panels.py
PANEL_SIZE = (768, 576)                                          # unified_panels.py CAMERA_RECT
CAMERA_SCALE = 1.2                                               # unified_panels.py
FOCUS_WHITE = "#FFFFFF"                                          # unified_panels.py
BORDER = "#3A3A3A"                                               # unified_panels.py

# --- status colours (D-013; V3PersonReceiver.cs) ----------------------------
MEASURED_RGB = (255, 255, 255)
ESTIMATED_RGB = (230, 166, 26)     # Color(0.9, 0.65, 0.1)
LOST_RGB = (217, 26, 26)           # Color(0.85, 0.1, 0.1)
STATUS_RGB = (MEASURED_RGB, ESTIMATED_RGB, LOST_RGB)

# --- editorial drawing constants (D-039, chosen by viewing frames) ----------
BACKGROUND_RGB = (16, 16, 16)
CUBE_RGB = (64, 140, 255)          # AXIS_COLORS["Z"]
REF_DOT_RGB = (120, 120, 120)
BONE_WIDTH = 6
TORSO_WIDTH = 4
JOINT_RADIUS = 6
THIN_WIDTH = 2
KP_RADIUS = 4

_FONT_CACHE = {}


def font(size):
    if size not in _FONT_CACHE:
        _FONT_CACHE[size] = ImageFont.truetype(str(FONT_PATH), size)
    return _FONT_CACHE[size]


def project_pinhole(points_camera_m, intrinsics):
    """Camera-optical points (..., 3) -> pixels (..., 2) in the source
    image. Copied from coordinate_axes.py project_pinhole; non-finite
    points or points with z <= 0 give NaN instead of an exception."""
    p = np.asarray(points_camera_m, dtype=float)
    if p.shape[-1] != 3:
        raise ValueError("points must have a last axis of 3")
    ok = np.isfinite(p).all(axis=-1) & (p[..., 2] > 0)
    z = np.where(ok, p[..., 2], 1.0)
    uv = np.stack((intrinsics["fx"] * p[..., 0] / z + intrinsics["ppx"],
                   intrinsics["fy"] * p[..., 1] / z + intrinsics["ppy"]),
                  axis=-1)
    uv[~ok] = np.nan
    return uv


def make_pinhole_projector(intrinsics, *, source_to_camera=None,
                           scale=1.0, offset=(0.0, 0.0)):
    """Copied from coordinate_axes.py make_pinhole_projector (the
    translation argument dropped; unused here)."""
    transform = (np.eye(3) if source_to_camera is None
                 else np.asarray(source_to_camera, float))

    def project(points):
        camera = np.asarray(points, float) @ transform.T
        return project_pinhole(camera, intrinsics) * scale + np.asarray(offset)
    return project


def unity_projector(intrinsics):
    """Solver (Unity) space points -> panel pixels (768x576)."""
    return make_pinhole_projector(intrinsics,
                                  source_to_camera=CAMERA_TO_CAMERA_PRIME,
                                  scale=CAMERA_SCALE)


def camera_projector(intrinsics):
    """Camera-optical points -> panel pixels (768x576)."""
    return make_pinhole_projector(intrinsics, scale=CAMERA_SCALE)


def cube_geometry(t_cam, R_cam, cube_m):
    """Marker pose (camera optical, OpenCV marker axes: z out of the
    face) -> (centre (3,), corners (8, 3)) of the cube behind the
    marker. The centre is marker origin + R (0, 0, -cube/2), which is
    bench/aruco_source.py box_center's (0, -cube/2, 0) in the P-swapped
    Unity marker frame (P = [[1,0,0],[0,0,1],[0,1,0]], carry.py)."""
    t = np.asarray(t_cam, float)
    R = np.asarray(R_cam, float)
    h = cube_m / 2.0
    local = np.array([[sx * h, sy * h, sz]
                      for sz in (0.0, -cube_m)
                      for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    corners = t + local @ R.T
    return t + R @ np.array([0.0, 0.0, -h]), corners


CUBE_EDGES = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7),
              (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]


def finite_xy(p):
    return p is not None and bool(np.all(np.isfinite(p)))


def draw_segment(draw, a, b, fill, width):
    if finite_xy(a) and finite_xy(b):
        draw.line([tuple(a), tuple(b)], fill=fill, width=width)


def draw_dot(draw, p, r, fill=None, outline=None, width=1):
    if finite_xy(p):
        u, v = p
        draw.ellipse((u - r, v - r, u + r, v + r), fill=fill,
                     outline=outline, width=width)


def draw_cube(draw, corners_px, fill=CUBE_RGB, width=2):
    for i, j in CUBE_EDGES:
        draw_segment(draw, corners_px[i], corners_px[j], fill, width)


def label(draw, xy, text, size, fill=(255, 255, 255), anchor=None,
          stroke=0):
    """unified_panels.py label without the page-bounds assertion; an
    optional black stroke keeps text legible over the photo."""
    draw.text(xy, text, font=font(size), fill=fill, anchor=anchor,
              stroke_width=stroke, stroke_fill=(0, 0, 0))


def photo_panel(color_bgr):
    """BGR uint8 640x480 bag frame -> RGB PIL image at the panel size
    (unified_panels.py compose: LANCZOS resize to 768x576)."""
    img = Image.fromarray(np.ascontiguousarray(color_bgr[:, :, ::-1]))
    if img.size != SOURCE_SIZE:
        raise ValueError(f"source frame {img.size} != {SOURCE_SIZE}")
    return img.resize(PANEL_SIZE, Image.Resampling.LANCZOS)


def dark_panel():
    return Image.new("RGB", PANEL_SIZE, BACKGROUND_RGB)
