"""Read the pinned Chapter 7 trails without rerunning or filtering them.

Default alias r6b: the recording of Chapter 2 (Figure 7.10), byte-identical
to the earlier single-recording version of this module. Alias r7: the
two-hand rail take (E-034, Chapter 7 hand-over section), whose trails file
carries a fourth path, the model left wrist, and whose panel intervals are
the parts of the hand-over analysis (eval/reports/r7_handover.json)."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[4]
ROOT = REPO / "writing/v8/condensed"
TRAILS = REPO / "eval/reports/unity_check_r6b_trails/trails.txt"
ANGLES = REPO / "eval/output/recovery_r6b/angles_recovery.csv"
WAYPOINTS = REPO / "eval/reports/r6b_waypoints.json"
sys.path.insert(0, str(REPO / "eval/common"))
sys.path.insert(0, str(REPO / "eval/offset"))
import paths  # noqa: E402
from carry import LeveledWorld  # noqa: E402

SETUPS = {
    "r6b": {"stem": paths.R6B_STEM, "trails": TRAILS, "angles": ANGLES,
            "waypoints": WAYPOINTS, "handover": None,
            "src": ROOT / "figures/src/ch7_trails_revision",
            "view": ROOT / "figures/ch7_trails_view.json",
            "stream": REPO / "eval/output/unity_check_r6b_trails/integrated_stream.csv",
            "figure": ROOT / "figures/ch7_fig_unity_trails.png",
            "compose": ROOT / "figures/ch7_trails_compose.json"},
    "r7": {"stem": paths.R7_STEM,
           "trails": REPO / "eval/reports/unity_check_r7/trails.txt",
           "angles": REPO / "eval/output/recovery_r7/angles_recovery.csv",
           "waypoints": REPO / "eval/reports/r7_waypoints.json",
           "handover": REPO / "eval/reports/r7_handover.json",
           "src": ROOT / "figures/src/ch7_handover_trails",
           "view": ROOT / "figures/ch7_handover_view.json",
           "stream": REPO / "eval/output/unity_check_r7/integrated_stream.csv",
           "figure": ROOT / "figures/ch7_fig_handover_trails.png",
           "compose": ROOT / "figures/ch7_handover_compose.json"},
}


def load(alias="r6b"):
    setup = SETUPS[alias]
    result = {}
    name = None
    for line in setup["trails"].read_text().splitlines():
        fields = line.split()
        if not fields or fields[0].startswith("#"):
            continue
        if fields[0] == "path":
            name = fields[1]
            result[name] = {"points": [], "frames": []}
        elif fields[0] == "p":
            result[name]["points"].append([float(v) for v in fields[1:4]])
            result[name]["frames"].append(int(fields[4]))
    for path in result.values():
        path["points"] = np.asarray(path["points"])
        path["frames"] = np.asarray(path["frames"])
    ang = pd.read_csv(setup["angles"]).set_index("frame")
    # group states: tag_1 / tag_3 right swing and elbow, tag_4 / tag_6 left
    for key, cols in (("wrist", ["tag_1", "tag_3"]), ("wrist_left", ["tag_4", "tag_6"])):
        if key not in result:
            continue
        frames = result[key]["frames"]
        tags = ang.loc[frames, cols].to_numpy(int)
        states = np.zeros(len(frames), dtype=int)
        states[(tags == 1).any(axis=1)] = 1
        states[(tags == 2).any(axis=1)] = 2
        result[key]["states"] = states
    wp = json.loads(setup["waypoints"].read_text())
    turns = wp["track_turns"]
    if setup["handover"] is None:
        result["phases"] = [
            {"name": "carry", "first": turns["parked_frames"][1] + 1,
             "last": turns["lift_begins_frame"] - 1},
            {"name": "lift", "first": turns["lift_begins_frame"],
             "last": turns["rail_reached_frame"] - 1},
            {"name": "slide", "first": turns["rail_reached_frame"],
             "last": turns["last_frame"]},
        ]
    else:
        # the parts of the hand-over analysis: the right hand from the end
        # of the parked span (carry, lift and its slide), the hand-over,
        # the left hand to the end of the recording
        parts = json.loads(setup["handover"].read_text())["parts"]
        result["phases"] = [
            {"name": "right", "first": turns["parked_frames"][1] + 1,
             "last": parts["right"]["frames"][1], "title": "Right hand"},
            {"name": "handover", "first": parts["handover"]["frames"][0],
             "last": parts["handover"]["frames"][1], "title": "Hand-over"},
            {"name": "left", "first": parts["left"]["frames"][0],
             "last": turns["last_frame"], "title": "Left hand"},
        ]
    result["world"] = LeveledWorld(json.loads(paths.calib_for(setup["stem"]).read_text()))
    return result


def intervals(frames, selected):
    """Inclusive runs of selected consecutive frame numbers."""
    runs = []
    for frame in np.asarray(frames)[np.asarray(selected)]:
        frame = int(frame)
        if runs and frame == runs[-1][1] + 1:
            runs[-1][1] = frame
        else:
            runs.append([frame, frame])
    return runs


def write_view_config(alias="r6b"):
    setup = SETUPS[alias]
    data = load(alias)
    def points(name):
        path = data[name]
        states = path.get("states", np.zeros(len(path["frames"]), int))
        return [{"x": float(p[0]), "y": float(p[1]), "z": float(p[2]),
                 "frame": int(f), "state": int(s)}
                for p, f, s in zip(path["points"], path["frames"], states)]
    config = {
        "outputDirectory": str(setup["src"]),
        "reference": points("reference"), "marker": points("cube"),
        "wrist": points("wrist"), "phases": data["phases"],
        "cameraDirection": {"x": 0.6, "y": 1.2, "z": -1.5},
        "margin": 1.4, "referenceWidth": 0.002, "trackWidth": 0.003,
        "waypointSize": 0.01, "dashLength": 0.02, "dashGap": 0.012,
        "avatarAlpha": 0.18, "width": 1200, "height": 800,
    }
    if "wrist_left" in data:
        config["wristLeft"] = points("wrist_left")
    out = setup["view"]
    out.write_text(json.dumps(config, indent=2) + "\n")
    Path("/tmp/ch7_trails_view.json").write_text(out.read_text())
    print("Prepared saved-data view:", out)


if __name__ == "__main__":
    write_view_config(sys.argv[1] if len(sys.argv) > 1 else "r6b")
