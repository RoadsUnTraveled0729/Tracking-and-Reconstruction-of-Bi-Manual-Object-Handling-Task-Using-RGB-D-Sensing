#!/usr/bin/env python3
"""Read-only checks for CH7_TRAILS_REVIEW.md; print evidence to stdout."""
from hashlib import sha256
from math import dist
from pathlib import Path
from zipfile import ZipFile


REPO = Path(__file__).resolve().parents[3]
RECORD = REPO / "eval/reports/unity_check_r6b_trails/trails.txt"
FIGURE = REPO / "writing/v9/figures/ch7_fig_unity_trails.png"
DOCUMENTS = (
    "writing/v9/Chapter_7_Evaluation.docx",
    "writing/v9/Thesis_V9.docx",
)


def main():
    print("Chapter 7 trail audit: saved outputs only; no pipeline rerun")
    print("Record:", RECORD.relative_to(REPO))
    print("Record SHA256:", sha256(RECORD.read_bytes()).hexdigest())
    paths = {}
    current = None
    for line in RECORD.read_text().splitlines():
        parts = line.split()
        if not parts or parts[0].startswith("#"):
            continue
        if parts[0] == "path":
            current = parts[1]
            paths[current] = {"mode": parts[6], "points": []}
        elif parts[0] == "p":
            if current is None:
                raise ValueError("Point appears before a path header")
            paths[current]["points"].append(
                (int(parts[4]), tuple(float(x) for x in parts[1:4]))
            )

    for name, path in paths.items():
        points = path["points"]
        print(f"Path {name}: {len(points)} points; {path['mode']}")
        if path["mode"] != "frames":
            continue
        frames = [f for f, _ in points]
        print("  Frame range:", min(frames), max(frames))
        print("  Missing frames inside range:",
              sorted(set(range(min(frames), max(frames) + 1)) - set(frames)))
        print("  Strictly increasing frames:",
              all(b > a for a, b in zip(frames, frames[1:])))
        pairs = list(zip(points, points[1:]))
        if pairs:
            a, b = max(pairs, key=lambda pair: dist(pair[0][1], pair[1][1]))
            print("  Largest stored adjacent position change at frames:", a[0], b[0])
            print("  Source display-axis coordinates in metres:", a[1], "->", b[1])
            print("  This identifies the largest stored adjacent change; abnormality and cause are not established.")

    digest = sha256(FIGURE.read_bytes()).hexdigest()
    print("Figure SHA256:", digest)
    for document in DOCUMENTS:
        with ZipFile(REPO / document) as archive:
            matches = [
                name for name in archive.namelist()
                if name.startswith("word/media/")
                and sha256(archive.read(name)).hexdigest() == digest
            ]
        print(document, "contains exact current trail PNG:", bool(matches), matches)
        if not matches:
            raise ValueError(f"Current trail image is absent from {document}")


if __name__ == "__main__":
    main()
