#!/usr/bin/env python3
"""Build the bounded Chapter 7 supporting-image restoration package.

The three video strips are composed from committed colour-frame extracts. The
two diagnostic figures are byte-for-byte copies of their committed sources,
so their overlays and numerical labels are not redrawn or altered.
"""
import hashlib
import json
import math
import shutil
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
CONDENSED = REPO / "writing" / "v8" / "condensed"
FIGURES = CONDENSED / "figures"
FRAME_SOURCE = FIGURES / "src"

STRIPS = {
    "ch7_video_context_r6b.png": {
        "source_dir": FRAME_SOURCE,
        "pattern": "r6b_frame{frame:05d}.png",
        "panel_letters": False,
        "panels": [
            (95, "Object acquisition"),
            (505, "Lift"),
            (700, "Rail slide"),
            (898, "Far end"),
        ],
    },
    "ch7_video_context_r7.png": {
        "source_dir": FRAME_SOURCE,
        "pattern": "r7_frame{frame:05d}.png",
        "panel_letters": False,
        "panels": [
            (700, "Right-hand slide"),
            (950, "Two-hand transfer"),
            (1042, "Left-hand slide"),
            (1200, "Far end"),
        ],
    },
    "ch7_failure_context.png": {
        "source_dir": REPO / "eval" / "labels" / "frames_r5",
        "pattern": "f{frame:05d}.png",
        "panel_letters": True,
        "panels": [
            (1427, "Left arm"),
            (1462, "Left wrist absent"),
            (1777, "Left arm"),
            (1890, "Right arm"),
        ],
    },
}

COPIES = {
    "ch7_natural_proxy_left.png": FIGURES / "ch7_fig_label_f1462.png",
    "ch7_natural_proxy_right.png": FIGURES / "ch7_fig_label_f1890.png",
}

PLACEMENTS = {
    "ch7_video_context_r6b.png": {
        "section": "7.2.1 Single-Hand Rail Task",
        "placement": "Immediately before the current rail object-trajectory figure; root may combine the strip above that plot.",
        "caption": "Single-hand rail recording: video strip for object acquisition, lift, rail slide and far-end placement. Frames 95, 505, 700 and 898 provide task context; the trajectory panels below show the evaluated waypoints.",
    },
    "ch7_video_context_r7.png": {
        "section": "7.2.2 Handover Task",
        "placement": "Immediately before the current handover object-trajectory figure; root may combine the strip above that plot.",
        "caption": "Handover recording: video strip for the right-hand slide, two-hand transfer, left-hand slide and far-end placement. Frames 700, 950, 1042 and 1200 provide task context; the trajectory panels below show the evaluated waypoints.",
    },
    "ch7_failure_context.png": {
        "section": "7.4.2 Natural Occlusion",
        "placement": "After the natural-occlusion recording and manual-proxy protocol are introduced, before Table 7.8.",
        "caption": "Loop recording: retained natural-failure frames for the left and right arms, including no MediaPipe left-wrist observation at frame 1462. The wrist proxy remains visible for manual labelling; these real-video samples are separate from the synthetic removal of Section 7.4.1.",
    },
    "ch7_natural_proxy_left.png": {
        "section": "7.4.2 Natural Occlusion",
        "placement": "After Table 7.9 as the first qualitative natural-occlusion example.",
        "caption": "Natural-occlusion example, loop frame 1462, left wrist. The square is the manual wrist proxy, the blue chain is the reconstructed arm, and the cross is the object-derived wrist estimate. With no MediaPipe wrist observation, the plain-solve and object-assisted wrist-to-proxy distances are 14.0 and 13.7 centimetres. This frame is an example, not a population statistic.",
    },
    "ch7_natural_proxy_right.png": {
        "section": "7.4.2 Natural Occlusion",
        "placement": "Immediately after the frame-1462 example.",
        "caption": "Natural-occlusion example, loop frame 1890, right wrist. The symbols follow the preceding figure. The object-assisted reconstructed wrist is 5.0 centimetres from the manual proxy, against 14.0 centimetres for the plain solve; the object-derived wrist estimate itself is shown by the cross. This frame is a favourable example, not a population statistic.",
    },
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def compose_strip(out_name, spec):
    panels = []
    inputs = []
    tags = "abcd"
    for tag, (frame, label) in zip(tags, spec["panels"]):
        path = spec["source_dir"] / spec["pattern"].format(frame=frame)
        image = Image.open(path).convert("RGB")
        title = f"({tag}) {label}" if spec["panel_letters"] else label
        panels.append((image, title, f"Frame {frame}"))
        inputs.append(path)

    panel_width = 640
    panel_height = 480
    title_height = 114
    title_font_px = 50
    gutter = 12
    canvas = Image.new(
        "RGB",
        (len(panels) * panel_width + (len(panels) - 1) * gutter,
         panel_height + title_height),
        "white",
    )
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", title_font_px
    )
    for index, (image, title, frame_line) in enumerate(panels):
        if image.size != (panel_width, panel_height):
            raise ValueError(f"Unexpected source size {image.size} for {inputs[index]}")
        x = index * (panel_width + gutter)
        for line in (title, frame_line):
            left, _, right, _ = font.getbbox(line)
            if right - left > panel_width - 16:
                raise ValueError(f"Title does not fit at {title_font_px}px: {line}")
        canvas.paste(image, (x, title_height))
        draw.text((x + 7, 1), title, font=font, fill="black")
        draw.text((x + 7, 56), frame_line, font=font, fill="black")

    output = FIGURES / out_name
    canvas.save(output, dpi=(200, 200), optimize=True)
    return inputs


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    label_report = REPO / "eval" / "reports" / "r5_recovery_labeled.json"
    rows = {
        row["frame"]: row
        for row in json.loads(label_report.read_text(encoding="utf-8"))["rows"]
        if row["frame"] in {1427, 1462, 1777, 1890}
    }
    expected_sides = {1427: "left", 1462: "left", 1777: "left", 1890: "right"}
    assert set(rows) == set(expected_sides)
    assert all(rows[frame]["side"] == side and rows[frame]["group"] == "failure"
               for frame, side in expected_sides.items())
    assert math.isnan(rows[1462]["measured_cm"])
    assert round(rows[1462]["plain_fk_cm"], 1) == 14.0
    assert round(rows[1462]["recovery_fk_cm"], 1) == 13.7
    assert round(rows[1890]["plain_fk_cm"], 1) == 14.0
    assert round(rows[1890]["recovery_fk_cm"], 1) == 5.0

    sources = {}
    for out_name, spec in STRIPS.items():
        sources[out_name] = compose_strip(out_name, spec)
    for out_name, source in COPIES.items():
        shutil.copyfile(source, FIGURES / out_name)
        sources[out_name] = [source]

    records = []
    for out_name in [*STRIPS, *COPIES]:
        output = FIGURES / out_name
        record = {
            "file": out_name,
            "output_path": str(output.relative_to(REPO)),
            **PLACEMENTS[out_name],
            "pixel_size": list(Image.open(output).size),
            "sha256": sha256(output),
            "sources": [
                {
                    "path": str(path.relative_to(REPO)),
                    "sha256": sha256(path),
                }
                for path in sources[out_name]
            ],
        }
        if out_name in STRIPS:
            width_in = 6.1
            font_px = 50
            record["presentation"] = {
                "nominal_label_font_px": font_px,
                "label_font_pt_at_6_1_in_width": round(
                    font_px * width_in * 72 / Image.open(output).width, 2
                ),
                "height_in_at_6_1_in_width": round(
                    Image.open(output).height * width_in / Image.open(output).width,
                    3,
                ),
                "title_lines": 2,
                "source_frame_pixels_resized_or_cropped": False,
            }
        if out_name in {
            "ch7_failure_context.png",
            "ch7_natural_proxy_left.png",
            "ch7_natural_proxy_right.png",
        }:
            record["sample_evidence"] = {
                "path": str(label_report.relative_to(REPO)),
                "sha256": sha256(label_report),
            }
        records.append(record)
    manifest = {
        "scope": "Chapter 7 supporting visual restoration only",
        "claims": [
            "All panels come from committed recorded-video, Unity, or diagnostic images.",
            "No measurement, plotted value, overlay, or captured scene content was fabricated or retouched.",
            "Both manual-label figures are byte-for-byte copies of their source figures.",
        ],
        "figures": records,
    }
    (HERE / "supporting_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(f"PASS: built {len(records)} supporting image groups")
    for record in records:
        print(f"PASS: {record['file']} {record['pixel_size']} {record['sha256']}")
    print("PASS: supporting_manifest.json")


if __name__ == "__main__":
    main()
