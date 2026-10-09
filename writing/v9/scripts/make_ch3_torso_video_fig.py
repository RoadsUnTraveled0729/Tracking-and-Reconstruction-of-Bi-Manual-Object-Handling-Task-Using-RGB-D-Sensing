#!/usr/bin/env python3
"""Build the real-video torso-frame illustration for Figure 3.4.

The figure uses frame 1400 of the two-hand rail recording. Every landmark,
vector, and axis endpoint is computed from the selected filtered landmark row
and colour intrinsics pinned in a compact source record. The RGB pixels are
preserved under the overlays.

Run with the thesis Python. Outputs:
  writing/v9/figures/ch3_fig_torso_video.png
Input/provenance:
  writing/v9/audit_evidence/figure_3_4_video/source.json
"""

import hashlib
import json
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


REPO = Path(__file__).resolve().parents[3]
STEM = "recording_20260909_000024"
FRAME = 1400

IMAGE = REPO / "writing/v9/figures/src/r7_frame01400.png"
OUT = REPO / "writing/v9/figures/ch3_fig_torso_video.png"
SOURCE_RECORD = REPO / "writing/v9/audit_evidence/figure_3_4_video/source.json"

CAMERA_TO_CAMERA_PRIME = np.array([1.0, -1.0, 1.0])
INK = (32, 37, 43)
WHITE = (255, 255, 255)
HIP = (39, 48, 186)
SPINE = (0, 151, 202)
X_AXIS = (45, 48, 201)
Y_AXIS = (74, 128, 34)
Z_AXIS = (154, 94, 35)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def project(point, intrinsics):
    x, y, z = point
    if z <= 0:
        raise ValueError("a plotted camera-space point is behind the camera")
    return (
        int(round(intrinsics["fx"] * x / z + intrinsics["ppx"])),
        int(round(intrinsics["fy"] * y / z + intrinsics["ppy"])),
    )


def label(image, point, text, offset, colour=INK):
    target = (point[0] + offset[0], point[1] + offset[1])
    cv2.line(image, point, target, colour, 1, cv2.LINE_AA)
    (width, height), baseline = cv2.getTextSize(
        text, cv2.FONT_HERSHEY_SIMPLEX, 0.56, 1
    )
    x = target[0] + (5 if offset[0] >= 0 else -width - 5)
    y = target[1] + (height // 2)
    cv2.rectangle(
        image,
        (x - 4, y - height - 4),
        (x + width + 4, y + baseline + 4),
        WHITE,
        -1,
        cv2.LINE_AA,
    )
    cv2.putText(
        image, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.56,
        colour, 1, cv2.LINE_AA
    )


def landmark(image, point):
    cv2.circle(image, point, 7, WHITE, -1, cv2.LINE_AA)
    cv2.circle(image, point, 7, INK, 2, cv2.LINE_AA)


def arrow(image, start, stop, colour, thickness=3):
    cv2.arrowedLine(
        image, start, stop, colour, thickness, cv2.LINE_AA,
        tipLength=0.075
    )


def main():
    source_record = json.loads(SOURCE_RECORD.read_text())
    if source_record["recording"]["stem"] != STEM:
        raise RuntimeError("source record has an unexpected recording stem")
    if source_record["recording"]["frame_index"] != FRAME:
        raise RuntimeError("source record has an unexpected frame index")
    expected_image_hash = source_record["sources"]["rgb_frame"]["sha256"]
    actual_image_hash = sha256(IMAGE)
    if actual_image_hash != expected_image_hash:
        raise RuntimeError(
            f"pinned RGB frame changed: found {actual_image_hash}, expected {expected_image_hash}"
        )

    source = cv2.imread(str(IMAGE), cv2.IMREAD_COLOR)
    if source is None:
        raise RuntimeError(f"could not read {IMAGE}")
    if source.shape[:2] != (480, 640):
        raise RuntimeError(f"unexpected RGB frame shape: {source.shape}")

    intrinsics = source_record["intrinsics"]
    row = source_record["selected_filtered_row"]
    if row["frame"] != FRAME or row["has_pose"] != 1:
        raise RuntimeError(f"frame {FRAME} has no detected pose")

    camera = {}
    points = {}
    for landmark_name, record in row["landmarks"].items():
        point = np.asarray(record["camera_xyz_m"], dtype=float)
        camera[landmark_name] = point
        points[landmark_name] = project(point, intrinsics)
        if points[landmark_name] != tuple(record["projected_pixel_xy"]):
            raise RuntimeError(f"projection changed for {landmark_name}")

    camera_prime = {
        name: CAMERA_TO_CAMERA_PRIME * point
        for name, point in camera.items()
    }
    hip_vector = camera_prime["L24"] - camera_prime["L23"]
    x_axis = hip_vector / np.linalg.norm(hip_vector)
    spine_vector = camera_prime["L12"] - camera_prime["L24"]
    z_axis = np.cross(x_axis, spine_vector)
    z_axis = z_axis / np.linalg.norm(z_axis)
    y_axis = np.cross(z_axis, x_axis)
    axes = {"x": x_axis, "y": y_axis, "z": z_axis}

    origin_camera = camera["L24"]
    axis_camera_endpoints = {
        name: origin_camera
        + source_record["plotted_geometry"]["axis_projection_length_m"]
        * CAMERA_TO_CAMERA_PRIME * axis
        for name, axis in axes.items()
    }
    axis_pixels = {
        name: project(endpoint, intrinsics)
        for name, endpoint in axis_camera_endpoints.items()
    }
    expected_geometry = source_record["plotted_geometry"]
    computed_vectors = {
        "p24_minus_p23": hip_vector,
        "p12_minus_p24": spine_vector,
    }
    for name, values in computed_vectors.items():
        if not np.allclose(values, expected_geometry["input_vectors_camera_prime_m"][name], atol=1e-12):
            raise RuntimeError(f"input vector changed for {name}")
    for name, values in axes.items():
        if not np.allclose(values, expected_geometry["unit_axes_camera_prime"][name], atol=1e-12):
            raise RuntimeError(f"derived axis changed for {name}")
        expected_endpoint = expected_geometry["axis_endpoints"][name]
        if not np.allclose(axis_camera_endpoints[name], expected_endpoint["camera_xyz_m"], atol=1e-12):
            raise RuntimeError(f"axis endpoint changed for {name}")
        if axis_pixels[name] != tuple(expected_endpoint["pixel_xy"]):
            raise RuntimeError(f"axis projection changed for {name}")

    panel_a = source.copy()
    arrow(panel_a, points["L23"], points["L24"], HIP)
    arrow(panel_a, points["L24"], points["L12"], SPINE)
    for point in points.values():
        landmark(panel_a, point)
    label(panel_a, points["L12"], "L12  right shoulder", (20, -18))
    label(panel_a, points["L23"], "L23  left hip", (18, 27))
    label(panel_a, points["L24"], "L24  right hip", (-18, 29))
    cv2.putText(
        panel_a, "p24 - p23", (317, 286), cv2.FONT_HERSHEY_SIMPLEX,
        0.54, HIP, 2, cv2.LINE_AA
    )
    cv2.putText(
        panel_a, "s = p12 - p24", (165, 190), cv2.FONT_HERSHEY_SIMPLEX,
        0.54, SPINE, 2, cv2.LINE_AA
    )

    panel_b = source.copy()
    origin = points["L24"]
    for name, colour in (("x", X_AXIS), ("y", Y_AXIS), ("z", Z_AXIS)):
        arrow(panel_b, origin, axis_pixels[name], colour)
    landmark(panel_b, origin)
    label(panel_b, origin, "L24  origin", (-17, 31))
    label(panel_b, axis_pixels["x"], "x  subject right", (20, -29), X_AXIS)
    label(panel_b, axis_pixels["y"], "y  trunk up", (18, -14), Y_AXIS)
    label(panel_b, axis_pixels["z"], "z  forward", (36, -29), Z_AXIS)

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    figure, axes_plot = plt.subplots(1, 2, figsize=(11, 4.3), facecolor="white")
    for axis, panel, title in (
        (axes_plot[0], panel_a, "(a) Recorded torso landmarks and input vectors"),
        (axes_plot[1], panel_b, "(b) Derived torso frame at L24"),
    ):
        axis.imshow(cv2.cvtColor(panel, cv2.COLOR_BGR2RGB))
        axis.set_title(title, fontsize=11, loc="left", pad=6)
        axis.axis("off")
    figure.subplots_adjust(left=0.01, right=0.99, top=0.91, bottom=0.08, wspace=0.025)
    figure.text(
        0.5, 0.025,
        "Subject right appears on the viewer's left. Axes are 0.30 m for projection.",
        ha="center", va="bottom", fontsize=9, color="#30343a"
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUT, dpi=240, facecolor="white")
    plt.close(figure)

    print("saved", OUT)


if __name__ == "__main__":
    main()
