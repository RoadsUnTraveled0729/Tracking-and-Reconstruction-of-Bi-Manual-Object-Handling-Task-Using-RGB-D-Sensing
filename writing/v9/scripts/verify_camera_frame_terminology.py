#!/usr/bin/env python3
"""Audit final camera-frame terminology and classify historical repository hits.

This checks text and embedded asset identity, not rendered image appearance.
The repository scan includes ignored historical drafts and never rewrites them.
"""
import argparse
import ast
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import subprocess
from zipfile import ZipFile

from lxml import etree

REPO = Path(__file__).resolve().parents[3]
CONDENSED = REPO / "writing/v9"
EVIDENCE = CONDENSED / "audit_evidence/final_completion"
NS = {"m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
      "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
FIGURES = ["ch2_fig_frames_craig.png", "ch3_fig_flow.png",
           "ch3_fig_colocated.png", "ch5_fig_flow.png", "ch5_fig_offset.png",
           "ch6_fig_frames.png", "ch7_unity_trajectories_r6b.png", "ch7_unity_trajectories_r7.png",
           "ch7_object_waypoints_r6b.png", "ch7_object_waypoints_r7.png",
           "ch3_fig_torso_video.png", "ch7_visual_examples_r6b.png",
           "ch7_visual_examples_r7.png", "ch5_fig_ik.png",
           "ch2_fig_sensor_scene.png", "ch3_fig_swing_twist.png",
           "ch7_video_context_r6b.png", "ch7_video_context_r7.png",
           "ch7_failure_context.png", "ch7_natural_proxy_left.png",
           "ch7_natural_proxy_right.png"]
REPOSITORY_PATTERN = (r"person[ -]space|\{Person\}|\{Sensor\}|\{P\}|"
                      r"\b(?:frame|space)\s+P\b|\^Person\b|"
                      r"nor\(['\"]Person['\"]\)|levelled|leveled")
PRINTED_PATTERN = re.compile(r"person[ -]space|\{Person\}|\{Sensor\}|\{P\}|"
                             r"\b(?:frame|space)\s+P\b|levelled|leveled|"
                             r"GravityAligned|LeveledScene|DisplayLevelled|WorldLevel", re.IGNORECASE)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def category(path):
    if re.match(r"writing/v[1-7]/", path):
        return "archived thesis drafts (preserved)"
    if path.startswith("v1/") or (path.startswith("Unity/") and "/V3/" not in path):
        return "frozen implementation and shared Unity provenance (preserved)"
    if path == "writing/v9/scripts/verify_camera_frame_terminology.py":
        return "verification search patterns (intentional)"
    if path.startswith("writing/v9/scripts/"):
        filename = Path(path).name
        if filename in {"ch7_trail_data.py", "make_ch7_handover_fig.py",
                        "make_ch7_task_schematic.py", "make_ch7_wrist_traj_fig.py",
                        "make_ch7_trails.py", "make_ch7_handover_trails.py"}:
            return "superseded Chapter 7 figure tooling (historical; not embedded)"
        if filename in {"evaluate_ch7_object.py", "evaluate_ch7_spatial_check.py",
                        "verify_ch7_restructured.py"}:
            return "pinned evidence generators and checks (historical coordinate metadata retained)"
        if filename in {"verify_final_frames.py", "make_ch2_frames_craig_fig.py"}:
            return "frozen helper identifiers in current consumers (Scene conversion is explicit)"
        return "current condensed scripts (review each match)"
    if path.startswith("writing/v9/audit_evidence/"):
        return "audit evidence and historical diagnostic vocabulary (preserved)"
    if path.startswith("writing/v9/") and path.endswith(".md"):
        return "condensed decision and revision records (append-only history)"
    if path.startswith("writing/v9/"):
        return "other condensed artifacts (review each match)"
    if path.startswith("writing/v8/"):
        return "non-condensed V8 sources and records (separate build/history)"
    return "other repository source or record (review in context)"


def scan_repository():
    # Restrict to source/documentation text. Include ignored historical drafts;
    # omit dependency caches, Git internals and this scan's own generated log.
    command = ["rg", "--json", "--hidden", "--no-ignore", "-i",
               "-g", "*.py", "-g", "*.md", "-g", "*.cs", "-g", "*.txt"]
    excluded = [".git", "__pycache__", "node_modules", ".venv", "venv",
                ".cache", "Library", "Temp", "obj"]
    for folder in excluded:
        command.extend(["-g", f"!**/{folder}/**"])
    command.extend(["-g", "!**/stale_repository_terms.txt", REPOSITORY_PATTERN, "."])
    result = subprocess.run(command, cwd=REPO, text=True, capture_output=True)
    if result.returncode not in (0, 1):
        raise RuntimeError(result.stderr)
    grouped = defaultdict(list)
    for line in result.stdout.splitlines():
        item = json.loads(line)
        if item["type"] != "match":
            continue
        data = item["data"]
        path = data["path"]["text"].removeprefix("./")
        label = category(path)
        # Preserve explicitly historical module revision records without
        # assuming their line numbers survive a later supported correction.
        if path.startswith("writing/v9/scripts/build_") and path.endswith(".py"):
            tree = ast.parse((REPO / path).read_text())
            if ast.get_docstring(tree) and data["line_number"] <= tree.body[0].end_lineno:
                label = "historical builder revision docstrings (preserved; later decisions supersede)"
        grouped[label].append({"path": path, "line": data["line_number"],
            "text": data["lines"]["text"].rstrip("\n"),
            "matches": [match["match"]["text"] for match in data["submatches"]]})
    lines = ["Repository terminology search; historical matches are not deleted.",
             "Scope: tracked, untracked and ignored .py/.md/.cs/.txt files.",
             "Excluded: Git internals, dependency caches and this generated log.",
             "Standalone frame P is searched by explicit frame syntax; ordinary",
             "position P and unrelated variables require contextual classification.",
             "Command: " + " ".join(repr(arg) for arg in command), ""]
    counts = {}
    for label, matches in sorted(grouped.items()):
        files = len({match["path"] for match in matches})
        counts[label] = {"matching_lines": len(matches), "files": files}
        lines.extend([f"CATEGORY: {label}", f"FILES: {files}; MATCHING LINES: {len(matches)}"])
        for match in matches:
            lines.append(f"{match['path']}:{match['line']}: {match['text']}")
        lines.append("")
    output = EVIDENCE / "stale_repository_terms.txt"
    output.write_text("\n".join(lines).rstrip() + "\n")
    return {"status": "CLASSIFIED (historical occurrences expected)",
            "counts": counts, "report": str(output.relative_to(REPO)),
            "report_sha256": digest(output.read_bytes())}


def main():
    global EVIDENCE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--docx", type=Path,
                        default=REPO / "writing/v9/Thesis_V9.docx")
    parser.add_argument("--skip-repository", action="store_true")
    parser.add_argument("--evidence-dir", type=Path, default=EVIDENCE)
    args = parser.parse_args()
    EVIDENCE = args.evidence_dir.resolve()
    with ZipFile(args.docx) as archive:
        root = etree.fromstring(archive.read("word/document.xml"))
        media = {name: digest(archive.read(name)) for name in archive.namelist()
                 if name.startswith("word/media/")}
        all_parts = []
        for name in archive.namelist():
            if name.startswith("word/") and name.endswith(".xml"):
                xml = etree.fromstring(archive.read(name))
                for para in xml.xpath(".//w:p", namespaces=NS):
                    text = "".join(para.xpath(".//w:t/text() | .//m:t/text()", namespaces=NS))
                    if PRINTED_PATTERN.search(text):
                        all_parts.append({"part": name, "text": text})
    paragraphs = ["".join(p.xpath(".//w:t/text() | .//m:t/text()", namespaces=NS))
                  for p in root.xpath(".//w:p", namespaces=NS)]
    stale = [{"paragraph": index, "text": text}
             for index, text in enumerate(paragraphs) if PRINTED_PATTERN.search(text)]
    old_math = root.xpath(".//m:t[text()='Person' or text()='Sensor'] | "
                          ".//m:sPre/m:sub//m:t[text()='P'] | "
                          ".//m:sPre/m:sup//m:t[text()='P']", namespaces=NS)
    math_names = Counter(root.xpath(".//m:sPre/m:sub//m:t/text() | "
                                    ".//m:sPre/m:sup//m:t/text()", namespaces=NS))
    position_p = len(root.xpath(".//m:sPre/m:e//m:t[text()='P']", namespaces=NS))
    checks = [{"label": "no stale printed frame terminology", "pass": not stale,
               "matches": stale},
              {"label": "no old Person/Sensor/P frame math labels", "pass": not old_math,
               "count": len(old_math)},
              {"label": "explicit Camera and Camera' Craig labels present",
               "pass": bool(math_names["Camera"] and math_names["Camera'"]),
               "Camera": math_names["Camera"], "Camera_prime": math_names["Camera'"]},
              {"label": "Craig position P remains distinct from frame names",
               "pass": position_p > 0, "preserved_position_P_count": position_p},
              {"label": "all Word parts exclude removed and replacement frame names",
               "pass": not all_parts, "matches": all_parts},
              {"label": "final Scene frame appears in Craig notation",
               "pass": bool(math_names["Scene"]), "count": math_names["Scene"]}]
    for filename in FIGURES:
        path = CONDENSED / "figures" / filename
        sha = digest(path.read_bytes())
        embedded = [name for name, value in media.items() if value == sha]
        checks.append({"label": "current corrected image embedded: " + filename,
                       "pass": bool(embedded), "sha256": sha, "media": embedded})
    result = {"status": "PASS" if all(check["pass"] for check in checks) else "FAIL",
              "docx": str(args.docx.resolve()), "docx_sha256": digest(args.docx.read_bytes()),
              "checks": checks,
              "limitations": ["Image hashes establish asset identity, not visual correctness.",
                  "Ordinary P position symbols and person record names remain valid.",
                  "Historical source terminology remains as provenance; see classified scan."]}
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    if not args.skip_repository:
        result["repository_scan"] = scan_repository()
    output = EVIDENCE / "camera_terminology.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return result["status"] != "PASS"


if __name__ == "__main__":
    raise SystemExit(main())
