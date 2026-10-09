#!/usr/bin/env python3
"""Compose two Chapter 7 Unity trajectory figures from saved evidence.

The layout is the accepted native composition. The outer legend calls the
constructed dashed path a "Schematic scene guide", and the superseded outer
Start/W1/W2/W3 annotations are omitted. This script does not render Unity,
replay a recording, recompute a trail, or change captured pixels.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
REPO = Path(__file__).resolve().parents[4]
SCRIPTS = REPO / "writing/v9/scripts"
FIGURES = REPO / "writing/v9/figures"


TABLE_SCOPE = REPO / "writing/v9/audit_evidence/ch7_restructured/human.json"
TABLE_SCOPE_SHA256 = "50735fe852f47a5c40a4e467da741b1359855382adb4b43b5955be2d0f3ef90b"
NATIVE_COMPOSER = SCRIPTS / "make_ch7_trails_fig.py"
NATIVE_COMPOSER_SHA256 = "b1de125653fdd4f9cdd6abe78e338548bb560be7de9eb1cef7fef889b992496e"
MARGIN = (60, 45, 50, 80)

ASSETS = {
    "r6b": {
        "output": "ch7_unity_trajectories_r6b.png",
        "layout_reference": REPO / "writing/v9/figures/ch7_fig_unity_trails.png",
        "layout_reference_sha256": "26075ee8090b4ebe9174d3cca34f7f0259d281ef60e41a521336e76243e080e0",
        "compose": REPO / "writing/v9/figures/ch7_trails_compose.json",
        "compose_sha256": "5794dbc60c212583c08d8208a4110b7045336a670a1412b1f98e1da81102b3d1",
        "capture": REPO / "writing/v9/figures/src/ch7_trails_revision/manifest.json",
        "capture_sha256": "4bb762435276cfae60e6a01dcb49bcfacab1686eccc70facc1d589dd6014269f",
        "capture_dir": REPO / "writing/v9/figures/src/ch7_trails_revision",
        "view": REPO / "writing/v9/figures/ch7_trails_view.json",
        "view_sha256": "50f67d739498093977fb940f809cbfa1fb20a6221f8deb38f82bd3ddb5ba5d99",
        "trails": REPO / "eval/reports/unity_check_r6b_trails/trails.txt",
        "trails_sha256": "4b21f03ddc86b0771664d8bbb628dcd9eb7cd49766ac5a7a7a53ece480b382ef",
        "historical_states": REPO / "eval/output/recovery_r6b/angles_recovery.csv",
        "historical_states_sha256": "8f617768b38db2ecac55b135303f8bd8f0273615a8732079e68868f5047e1d74",
        "intervals": REPO / "eval/reports/r6b_waypoints.json",
        "intervals_sha256": "82cd85d4ccef9ea5306ba9fb31ff5a4ec08858be607cc122964a715457f964ec",
        "phases": [
            {"name": "carry", "first": 92, "last": 500, "record": "carry.json"},
            {"name": "lift", "first": 501, "last": 528, "record": "lift.json"},
            {"name": "slide", "first": 529, "last": 899, "record": "slide.json"},
        ],
        "paths": ["cube", "wrist"],
        "held_legend": False,
        "expected_dimensions_px": [1565, 1468],
        "table_samples": {"right_elbow": 102, "right_wrist": 102},
        "caption": (
            "Figure 7.3. Single-hand rail task in the saved Unity trajectory view. "
            "The panels show the saved marker-origin and model-wrist trails over "
            "the carry (frames 92-500), lift (501-528) and slide (529-899) "
            "intervals; the avatar and cube are posed at each interval's final "
            "frame. The dashed line is a schematic scene guide, not a surveyed "
            "or registered physical path. These task-interval trails provide "
            "qualitative context and are not the elbow and wrist samples used in "
            "Table 7.3."
        ),
    },
    "r7": {
        "output": "ch7_unity_trajectories_r7.png",
        "layout_reference": REPO / "writing/v9/figures/ch7_fig_handover_trails.png",
        "layout_reference_sha256": "58917dce92479e4678b466e25e5830b11531f1a6a0661090d49a0829d3594e99",
        "compose": REPO / "writing/v9/figures/ch7_handover_compose.json",
        "compose_sha256": "b4048cab276670979d89a2eca850ad71c4288e6f73d1a05526854eca6cb1ca5a",
        "capture": REPO / "writing/v9/figures/src/ch7_handover_trails/manifest.json",
        "capture_sha256": "c3c89f31b8252594822aca1fcf8bc635dd9ff92e5175344ab579e5c69eef9283",
        "capture_dir": REPO / "writing/v9/figures/src/ch7_handover_trails",
        "view": REPO / "writing/v9/figures/ch7_handover_view.json",
        "view_sha256": "e9362022f74aa35ea1b65b00f4c7dc23fcd652e586bd8131f3089597e54029a7",
        "trails": REPO / "eval/reports/unity_check_r7/trails.txt",
        "trails_sha256": "2e39a7af22e652996091defc05c09641b2046cad1f1af3cf4370eb2aedb8ec68",
        "historical_states": REPO / "eval/output/recovery_r7/angles_recovery.csv",
        "historical_states_sha256": "0c7406ac547b23b28e48a48236cf0538da3d59c5953fcca60487a9d78f91aeae",
        "intervals": REPO / "eval/reports/r7_waypoints.json",
        "intervals_sha256": "4b20560b7e651eb127828b597ebb0c76b82ede5a4a7a0f3c174c131b16f20faa",
        "handover_intervals": REPO / "eval/reports/r7_handover.json",
        "handover_intervals_sha256": "8e4588a6d216c5a98fb13e2eeb43d4638298a64b636f95b7619e71b5ef9a115c",
        "phases": [
            {"name": "right hand", "first": 137, "last": 863, "record": "right.json"},
            {"name": "hand-over", "first": 864, "last": 1022, "record": "handover.json"},
            {"name": "left hand", "first": 1023, "last": 1498, "record": "left.json"},
        ],
        "paths": ["cube", "wrist", "wrist_left"],
        "held_legend": True,
        "expected_dimensions_px": [1511, 1468],
        "table_samples": {"right_elbow": 650, "right_wrist": 650, "left_elbow": 589, "left_wrist": 589},
        "caption": (
            "Figure 7.4. Handover task in the saved Unity trajectory view. The "
            "panels show the saved marker-origin and right- and left-model-wrist "
            "trails over the right-hand (frames 137-863), hand-over (864-1022) "
            "and left-hand (1023-1498) intervals; the avatar and cube are posed at "
            "each interval's final frame. The dashed line is a schematic scene "
            "guide, not a surveyed or registered physical path. These task-interval "
            "trails provide qualitative context and are not the arm-specific "
            "elbow and wrist samples used in Table 7.4."
        ),
    },
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def verify_hash(path: Path, expected: str) -> None:
    actual = digest(path)
    if actual != expected:
        raise RuntimeError(f"Hash mismatch for {relative(path)}: {actual}")


def content_window(stills: list[Image.Image]) -> tuple[int, int, int, int]:
    rows, cols = [], []
    for still in stills:
        rgb = np.asarray(still.convert("RGB")).astype(int)
        drawn = ((rgb.max(-1) - rgb.min(-1)) > 60) | (rgb.max(-1) < 90)
        row, col = np.where(drawn)
        rows += [row.min(), row.max()]
        cols += [col.min(), col.max()]
    width, height = stills[0].size
    return (max(min(cols) - MARGIN[0], 0), max(min(rows) - MARGIN[1], 0),
            min(max(cols) + MARGIN[2] + 1, width), min(max(rows) + MARGIN[3] + 1, height))


def trail_frames(path: Path) -> dict[str, set[int]]:
    result: dict[str, set[int]] = {}
    current = ""
    for line in path.read_text().splitlines():
        fields = line.split()
        if not fields or fields[0].startswith("#"):
            continue
        if fields[0] == "path":
            current = fields[1]
            result[current] = set()
        elif fields[0] == "p":
            result[current].add(int(fields[4]))
    return result


def verify_sources(alias: str, spec: dict) -> None:
    for key in ("layout_reference", "compose", "capture", "view", "trails", "intervals"):
        verify_hash(spec[key], spec[f"{key}_sha256"])
    if spec["historical_states"].exists():
        verify_hash(spec["historical_states"], spec["historical_states_sha256"])
    if "handover_intervals" in spec:
        verify_hash(spec["handover_intervals"], spec["handover_intervals_sha256"])
    compose_record = json.loads(spec["compose"].read_text())
    capture_record = json.loads(spec["capture"].read_text())
    if compose_record["figure_sha256"] != spec["layout_reference_sha256"]:
        raise RuntimeError(f"Native composition does not bind the {alias} layout reference")
    if compose_record["manifest_sha256"] != spec["capture_sha256"]:
        raise RuntimeError(f"Native composition does not bind the {alias} capture manifest")
    if capture_record["view_config_sha256"] != spec["view_sha256"]:
        raise RuntimeError(f"Capture does not bind the {alias} view configuration")
    for name, record in capture_record["files"].items():
        source = spec["capture_dir"] / name
        verify_hash(source, record["sha256"])
        if source.stat().st_size != record["bytes"]:
            raise RuntimeError(f"Size mismatch for {relative(source)}")
    for phase in spec["phases"]:
        record = json.loads((spec["capture_dir"] / phase["record"]).read_text())
        actual = (record["first"], record["last"], record["appliedFrame"])
        expected = (phase["first"], phase["last"], phase["last"])
        if actual != expected:
            raise RuntimeError(f"Unexpected capture record for {alias} {phase['name']}")


def compose(alias: str, spec: dict) -> tuple[list[int], list[int]]:
    figure = plt.figure(figsize=(8.4, 7.4))
    if alias == "r6b":
        grid = figure.add_gridspec(2, 2, height_ratios=[1, 2], hspace=0.16, wspace=0.05)
        axes = [figure.add_subplot(grid[0, 0]), figure.add_subplot(grid[0, 1]), figure.add_subplot(grid[1, :])]
    else:
        grid = figure.add_gridspec(2, 2, height_ratios=[2, 1], hspace=0.16, wspace=0.05)
        axes = [figure.add_subplot(grid[0, :]), figure.add_subplot(grid[1, 0]), figure.add_subplot(grid[1, 1])]

    phases = spec["phases"]
    records = [json.loads((spec["capture_dir"] / phase["record"]).read_text()) for phase in phases]
    stills = [Image.open(spec["capture_dir"] / Path(phase["record"]).with_suffix(".png")) for phase in phases]
    cameras = {(record["orthographicSize"], tuple(record["cameraPosition"].values()), tuple(record["cameraTarget"].values())) for record in records}
    if len(cameras) != 1 or len({still.size for still in stills}) != 1:
        raise RuntimeError(f"Inconsistent saved camera or still size for {alias}")
    crop = content_window(stills)

    for label, axis, phase, record, still in zip("abc", axes, phases, records, stills):
        _, height = still.size
        image = still.crop(crop)
        axis.imshow(image)
        axis.set_title(f"({label}) {phase.get('title', phase['name'].capitalize())}: frames {phase['first']}-{phase['last']}", fontsize=12, loc="left")
        bar_px = 0.1 * height / (2 * record["orthographicSize"])
        x, y = image.width * 0.80 - bar_px / 2, image.height * 0.93
        axis.plot([x, x + bar_px], [y, y], color="0.15", lw=2)
        axis.text(x + bar_px / 2, y - image.height * 0.035, "10 cm", ha="center", fontsize=10,
                  bbox=dict(fc="white", ec="none", alpha=0.9, pad=1.5))
        axis.set_axis_off()

    guide = Line2D([], [], color="0.2", ls="--", label="Schematic scene guide")
    if alias == "r7":
        handles = [guide, Line2D([], [], color="tab:green", label="Marker origin"),
                   Line2D([], [], color="tab:blue", label="Right wrist: measured input"),
                   Line2D([], [], color="tab:orange", label="Right wrist: rebuilt"),
                   Line2D([], [], color="tab:purple", label="Left wrist: measured input"),
                   Line2D([], [], color="tab:pink", label="Left wrist: rebuilt")]
        if spec["held_legend"]:
            handles.append(Line2D([], [], color="0.45", label="Either wrist: held"))
        columns = 3 if len(handles) > 6 else 2
    else:
        handles = [guide, Line2D([], [], color="tab:green", label="Marker origin"),
                   Line2D([], [], color="tab:blue", label="Wrist: measured input"),
                   Line2D([], [], color="tab:orange", label="Wrist: rebuilt")]
        columns = 2
    figure.legend(handles=handles, loc="lower center", ncol=columns, fontsize=11, frameon=False)
    figure.subplots_adjust(left=0.02, right=0.98, top=0.96, bottom=0.09 if columns == 2 else 0.12)
    output = FIGURES / spec["output"]
    figure.savefig(output, dpi=200, bbox_inches="tight", pad_inches=0.05)
    plt.close(figure)
    for still in stills:
        still.close()
    with Image.open(output) as image:
        dimensions = list(image.size)
    if dimensions != spec["expected_dimensions_px"]:
        raise RuntimeError(f"Unexpected output dimensions for {alias}: {dimensions}")
    return [int(value) for value in crop], dimensions


def sample_manifest(spec: dict) -> dict:
    frames = trail_frames(spec["trails"])
    result = {}
    for phase in spec["phases"]:
        expected = phase["last"] - phase["first"] + 1
        result[phase["name"]] = {
            path_name: {"present": sum(frame in frames[path_name] for frame in range(phase["first"], phase["last"] + 1)), "interval_frames": expected}
            for path_name in spec["paths"]
        }
    return result


def main() -> None:
    verify_hash(NATIVE_COMPOSER, NATIVE_COMPOSER_SHA256)
    verify_hash(TABLE_SCOPE, TABLE_SCOPE_SHA256)
    table_scope = json.loads(TABLE_SCOPE.read_text())
    for alias, spec in ASSETS.items():
        verify_sources(alias, spec)
        actual = {name: table_scope[alias]["joints"][name]["n"] for name in spec["table_samples"]}
        if actual != spec["table_samples"]:
            raise RuntimeError(f"Table sample counts changed for {alias}: {actual}")

    outputs = {}
    for alias, spec in ASSETS.items():
        crop, dimensions = compose(alias, spec)
        output = FIGURES / spec["output"]
        outputs[alias] = {
            "output": relative(output), "output_sha256": digest(output), "dimensions_px": dimensions,
            "layout_reference_composite": relative(spec["layout_reference"]),
            "layout_reference_sha256": spec["layout_reference_sha256"],
            "source_compose_manifest": relative(spec["compose"]), "capture_manifest": relative(spec["capture"]),
            "source_hashes": {
                relative(spec["compose"]): spec["compose_sha256"],
                relative(spec["capture"]): spec["capture_sha256"],
                relative(spec["view"]): spec["view_sha256"],
                relative(spec["trails"]): spec["trails_sha256"],
                relative(spec["intervals"]): spec["intervals_sha256"],
                **(
                    {relative(spec["handover_intervals"]): spec["handover_intervals_sha256"]}
                    if "handover_intervals" in spec else {}
                ),
            },
            "historical_optional_source_hashes": {
                relative(spec["historical_states"]): spec["historical_states_sha256"],
            },
            "crop_px": crop,
            "saved_capture_frames": [{"phase": phase["name"], "interval": [phase["first"], phase["last"]], "posed_frame": phase["last"]} for phase in spec["phases"]],
            "trajectory_samples_by_interval": sample_manifest(spec),
            "table_valid_landmark_samples": spec["table_samples"],
            "contains": ["marker-origin trail", "model-wrist trail", "Unity endpoint pose", "schematic scene guide"],
            "does_not_contain": ["elbow trail", "surveyed physical path", "registered physical waypoint coordinates", "superseded outer Start/W1/W2/W3 annotations", "the exact valid-landmark subset used by the table"],
            "suggested_caption": spec["caption"],
        }
    manifest = {
        "schema_version": 1,
        "policy": "Existing recorded scenes only; no new capture, experiment, or fabricated scene content.",
        "composition_change": "Outer legend changed from Waypoint reference to Schematic scene guide, and superseded outer Start/W1/W2/W3 annotations were omitted; saved Unity rasters and recorded trails are unchanged.",
        "native_composer": relative(NATIVE_COMPOSER), "native_composer_sha256": NATIVE_COMPOSER_SHA256,
        "table_scope_source": relative(TABLE_SCOPE), "table_scope_source_sha256": TABLE_SCOPE_SHA256,
        "assets": outputs,
    }
    (HERE / "sources.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print("PASS: composed and verified two Chapter 7 Unity trajectory figures")


if __name__ == "__main__":
    main()
