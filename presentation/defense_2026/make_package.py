#!/usr/bin/env python3
"""Copy the final defence deliverables into a folder that can be shared as is.

The deliverables are the author's files, adopted byte for byte (D-381):
Thesis_Defence_2026.pptx, Thesis_Defence_2026_Speaker_Script.docx and
Thesis_Defence_2026_Outline_and_QA_Index.docx. Nothing here edits them.

--render writes the three still PDFs (skipping any whose recorded source
and PDF hashes still match, D-388) with LibreOffice (headless, an isolated
profile in a temporary directory, hidden slides exported) and records the
source and PDF hashes in review/RENDER_RECORD.json (D-383).

The default run writes package/Thesis_Defence_2026/ with the three files,
their three PDFs and a README.txt filled from PACKAGE_README.txt, and
package/MANIFEST.json with the size and sha256 of every copied file and the
git commit (D-108). No archive is created. It refuses to package when a PDF
is not the one RENDER_RECORD.json describes for the current source, or when
the PPTX links any file outside itself.

--self-test checks the clean-tree test in a throwaway git repository (D-351)
and copies nothing. --require-clean refuses a working tree whose package
inputs differ from the commit.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from string import Template
from xml.etree import ElementTree as ET


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
PACKAGE = HERE / "package"
FOLDER = PACKAGE / "Thesis_Defence_2026"
README_SOURCE = HERE / "PACKAGE_README.txt"
RENDER_RECORD = HERE / "review" / "RENDER_RECORD.json"
DECK = HERE / "Thesis_Defence_2026.pptx"
SCRIPT = HERE / "Thesis_Defence_2026_Speaker_Script.docx"
OUTLINE = HERE / "Thesis_Defence_2026_Outline_and_QA_Index.docx"
SOURCES = (DECK, SCRIPT, OUTLINE)
COPIED = tuple(p for s in SOURCES for p in (s, s.with_suffix(".pdf")))
README_MAX_LINES = 40  # brief for D-108: the README stays under 40 lines
# LibreOffice Impress export filter option: include the hidden slides in the
# PDF (same option as the retired render_deck.py, D-383).
IMPRESS_EXPORT = json.dumps({"ExportHiddenSlides": {"type": "boolean", "value": "true"}})
NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
      "rel": "http://schemas.openxmlformats.org/package/2006/relationships"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.run(["git", "-C", str(REPO), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def pdf_pages(path):
    info = subprocess.run(["pdfinfo", str(path)], check=True, capture_output=True, text=True).stdout
    return int(re.search(r"^Pages:\s+(\d+)", info, re.M).group(1))


def deck_facts():
    """Slides in presentation order with their hidden flag and text, the
    embedded MP4 count, and every external relationship (a finding)."""
    with zipfile.ZipFile(DECK) as package:
        names = package.namelist()
        external = []
        for name in names:
            if not name.endswith(".rels"):
                continue
            for rel in ET.fromstring(package.read(name)):
                if rel.get("TargetMode") == "External":
                    external.append("%s -> %s" % (name, rel.get("Target")))
        rels = {r.get("Id"): r.get("Target") for r in
                ET.fromstring(package.read("ppt/_rels/presentation.xml.rels"))}
        order = ET.fromstring(package.read("ppt/presentation.xml")).find("p:sldIdLst", NS)
        slides = []
        for number, entry in enumerate(order, 1):
            part = "ppt/" + rels[entry.get("{%s}id" % NS["r"])]
            root = ET.fromstring(package.read(part))
            texts = [t.text or "" for t in root.iter("{%s}t" % NS["a"])]
            slides.append({"page": number, "hidden": root.get("show") == "0", "text": texts})
    videos = sum(1 for n in names if n.startswith("ppt/media/") and n.lower().endswith(".mp4"))
    return slides, videos, external


def ranges(pages):
    """Page numbers as ranges, for example "47-77" or "2-3 and 49-76"."""
    runs = []
    for page in pages:
        if runs and page == runs[-1][1] + 1:
            runs[-1][1] = page
        else:
            runs.append([page, page])
    parts = ["%d" % a if a == b else "%d-%d" % (a, b) for a, b in runs]
    if not parts:
        return "none"
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]


def render():
    """LibreOffice PDFs of the three sources; the sources are never written.

    A PDF is skipped when RENDER_RECORD.json already records the same source
    sha256 for it and the PDF on disk still has the recorded PDF sha256 (D-388),
    so an unchanged source does not rewrite its PDF. Only the re-rendered
    entries of the record are replaced.
    """
    previous = {}
    if RENDER_RECORD.is_file():
        previous = {row["source"]: row for row in json.loads(RENDER_RECORD.read_text())["files"]}
    record = {"decision": "D-383", "rendered": datetime.now().astimezone().strftime("%Y-%m-%d"),
              "renderer": subprocess.run(["soffice", "--version"], check=True, capture_output=True,
                                         text=True).stdout.strip(),
              "impress_export_options": json.loads(IMPRESS_EXPORT), "files": []}
    skipped = set()
    with tempfile.TemporaryDirectory(prefix="defense-render-") as scratch:
        scratch = Path(scratch)
        for source in SOURCES:
            before = sha256(source)
            destination = source.with_suffix(".pdf")
            old = previous.get(source.name)
            if (old and old.get("source_sha256") == before and destination.is_file()
                    and sha256(destination) == old.get("pdf_sha256")):
                print("%-46s unchanged, skipped" % destination.name)
                record["files"].append(old)
                skipped.add(source.name)
                continue
            snapshot = scratch / source.name
            shutil.copyfile(source, snapshot)
            pdf_filter = ("pdf:impress_pdf_Export:" + IMPRESS_EXPORT) if source.suffix == ".pptx" else "pdf"
            subprocess.run(["soffice", "-env:UserInstallation=" + (scratch / "office-profile").as_uri(),
                            "--headless", "--convert-to", pdf_filter, "--outdir", str(scratch), str(snapshot)],
                           check=True, capture_output=True)
            rendered = scratch / (source.stem + ".pdf")
            if not rendered.is_file():
                raise SystemExit("ERROR: LibreOffice did not produce " + rendered.name)
            if sha256(source) != before:
                raise SystemExit("ERROR: %s changed during rendering" % source.name)
            shutil.copyfile(rendered, destination)
            record["files"].append({"source": source.name, "source_sha256": before, "pdf": destination.name,
                                    "pdf_sha256": sha256(destination), "pdf_pages": pdf_pages(destination)})
    if len(skipped) == len(SOURCES):
        print("All PDFs unchanged; %s not rewritten" % RENDER_RECORD.relative_to(REPO))
        return
    RENDER_RECORD.write_text(json.dumps(record, indent=2, ensure_ascii=True) + "\n")
    for row in record["files"]:
        print("%-46s %3d pages  %s" % (row["pdf"], row["pdf_pages"], row["pdf_sha256"]))
    print("Wrote %s" % RENDER_RECORD.relative_to(REPO))


def check_render(slides):
    """Each PDF must be the one RENDER_RECORD.json describes for the current
    source, and the deck PDF must carry every slide (hidden ones included)."""
    if not RENDER_RECORD.is_file():
        raise SystemExit("ERROR: missing %s; run make_package.py --render first" % RENDER_RECORD.name)
    record = {row["source"]: row for row in json.loads(RENDER_RECORD.read_text())["files"]}
    problems = []
    for source in SOURCES:
        row = record.get(source.name)
        pdf = source.with_suffix(".pdf")
        if row is None or row["source_sha256"] != sha256(source):
            problems.append("%s changed since it was rendered" % source.name)
        elif row["pdf_sha256"] != sha256(pdf) or row["pdf_pages"] != pdf_pages(pdf):
            problems.append("%s is not the recorded render" % pdf.name)
    if not problems and record[DECK.name]["pdf_pages"] != len(slides):
        problems.append("the deck PDF has %d pages for %d slides" % (record[DECK.name]["pdf_pages"], len(slides)))
    if problems:
        raise SystemExit("ERROR: run make_package.py --render first: " + "; ".join(problems))
    return record


def inputs_dirty(repo, paths, must_track=()):
    """D-351: True when any of paths differs from HEAD, is untracked, is staged,
    or (must_track) exists but is not tracked by git, ignored files included.
    `git diff --quiet HEAD` alone ignores untracked files."""
    status = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all", "--", *paths],
                            check=True, capture_output=True, text=True).stdout
    untracked = [p for p in must_track
                 if subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch", "--", p],
                                   capture_output=True).returncode != 0]
    return bool(status.strip()) or bool(untracked)


def clean_self_test():
    """D-351: clean, modified, untracked and ignored-but-required inputs in a throwaway repository."""
    failures = []
    with tempfile.TemporaryDirectory(prefix="package-clean-test-") as temp:
        repo = Path(temp)
        def git_t(*args):
            subprocess.run(["git", "-C", temp, "-c", "user.name=test", "-c", "user.email=test@example.invalid", *args],
                           check=True, capture_output=True)
        git_t("init", "-q")
        (repo / "deck.json").write_text("{}\n")
        (repo / ".gitignore").write_text("ignored_record.json\n")
        git_t("add", "deck.json", ".gitignore")
        git_t("commit", "-q", "-m", "base")
        if inputs_dirty(repo, ["deck.json", "required_record.json"]):
            failures.append("clean tree reported dirty")
        (repo / "required_record.json").write_text("{}\n")
        if not inputs_dirty(repo, ["deck.json", "required_record.json"], ["required_record.json"]):
            failures.append("untracked required record accepted")
        git_t("add", "required_record.json")
        if not inputs_dirty(repo, ["deck.json", "required_record.json"], ["required_record.json"]):
            failures.append("staged, uncommitted required record accepted")
        git_t("commit", "-q", "-m", "record")
        if inputs_dirty(repo, ["deck.json", "required_record.json"], ["required_record.json"]):
            failures.append("committed required record reported dirty")
        (repo / "deck.json").write_text("{\"x\": 1}\n")
        if not inputs_dirty(repo, ["deck.json"]):
            failures.append("modified tracked input accepted")
        git_t("checkout", "-q", "--", "deck.json")
        (repo / "ignored_record.json").write_text("{}\n")
        if not inputs_dirty(repo, ["ignored_record.json"], ["ignored_record.json"]):
            failures.append("ignored, untracked required input accepted")
    return failures


def render_readme(slides, record, commit_line, videos):
    """README.txt from PACKAGE_README.txt; every count comes from the files."""
    shown = [s["page"] for s in slides if not s["hidden"]]
    hidden = [s["page"] for s in slides if s["hidden"]]
    closing = [s["page"] for s in slides if not s["hidden"] and "".join(s["text"]).strip() == "Questions"]
    if len(closing) != 1:
        raise SystemExit("ERROR: expected one shown Questions page, found %s" % closing)
    readme = Template(README_SOURCE.read_text()).substitute(
        render_date=json.loads(RENDER_RECORD.read_text())["rendered"], git_commit=commit_line,
        total_pages=len(slides), shown_count=len(shown), hidden_count=len(hidden),
        shown_pages=ranges(shown), hidden_pages=ranges(hidden), closing_page=closing[0], video_count=videos,
        script_pages=record[SCRIPT.name]["pdf_pages"], outline_pages=record[OUTLINE.name]["pdf_pages"])
    if not readme.isascii() or len(readme.splitlines()) >= README_MAX_LINES:
        raise SystemExit("ERROR: README.txt must be ASCII and under %d lines" % README_MAX_LINES)
    return readme


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--render", action="store_true",
                        help="write the three PDFs with LibreOffice and review/RENDER_RECORD.json, then exit")
    parser.add_argument("--require-clean", action="store_true",
                        help="fail unless the copied files and the render record match the git commit")
    parser.add_argument("--self-test", action="store_true",
                        help="test the clean-tree check in a throwaway git repository, then exit")
    args = parser.parse_args()
    if args.self_test:
        failures = clean_self_test()
        for failure in failures:
            print("FAIL: %s" % failure)
        print("Clean-tree self-test: %s" % ("FAIL" if failures else "PASS (6 cases)"))
        sys.exit(1 if failures else 0)
    for path in SOURCES + (README_SOURCE,):
        if not path.is_file():
            raise SystemExit("ERROR: missing " + str(path))
    if args.render:
        render()
        return

    slides, videos, external = deck_facts()
    if external:
        raise SystemExit("ERROR: the PPTX links files outside itself: " + "; ".join(external))
    record = check_render(slides)

    commit = git("rev-parse", "--short=7", "HEAD")
    record_path = str(RENDER_RECORD.relative_to(REPO))
    tracked = [str(p.relative_to(REPO)) for p in COPIED + (README_SOURCE, Path(__file__).resolve())] + [record_path]
    dirty = inputs_dirty(REPO, tracked, [record_path])
    if dirty and args.require_clean:
        raise SystemExit("ERROR: the package inputs differ from commit %s; commit them first" % commit)
    commit_line = commit + (" (plus uncommitted working-tree changes to the package inputs)" if dirty else "")
    readme = render_readme(slides, record, commit_line, videos)

    FOLDER.mkdir(parents=True, exist_ok=True)
    expected = {p.name for p in COPIED} | {"README.txt"}
    extra = sorted(p.name for p in FOLDER.iterdir() if p.name not in expected)
    if extra:
        raise SystemExit("ERROR: unexpected files in %s: %s" % (FOLDER, ", ".join(extra)))
    for source in COPIED:
        shutil.copyfile(source, FOLDER / source.name)
        if sha256(FOLDER / source.name) != sha256(source):
            raise SystemExit("ERROR: copy mismatch for " + source.name)
    (FOLDER / "README.txt").write_text(readme)

    files = [{"file": p.name, "bytes": (FOLDER / p.name).stat().st_size, "sha256": sha256(FOLDER / p.name),
              "source": str(p.relative_to(REPO))} for p in COPIED]
    files.append({"file": "README.txt", "bytes": (FOLDER / "README.txt").stat().st_size,
                  "sha256": sha256(FOLDER / "README.txt"), "source": str(README_SOURCE.relative_to(REPO))})
    hidden = [s["page"] for s in slides if s["hidden"]]
    manifest = {"folder": str(FOLDER.relative_to(REPO)), "decision": ["D-108", "D-381", "D-383"],
                "git_commit": commit, "working_tree_differs_from_commit": dirty,
                "slides": len(slides), "shown_slides": len(slides) - len(hidden), "hidden_slides": len(hidden),
                "hidden_pages": ranges(hidden), "embedded_mp4_videos": videos, "external_relationships": 0,
                "pdf_pages": {row["pdf"]: row["pdf_pages"] for row in record.values()},
                "render_record": record_path,
                "verification": "sha256 of each copied file; PDF page counts; deck PDF pages equal slides; "
                                "embedded media playback not verified (D-383)",
                "total_bytes": sum(f["bytes"] for f in files), "files": files}
    (PACKAGE / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=True) + "\n")
    for f in files:
        print("%-46s %12d  %s" % (f["file"], f["bytes"], f["sha256"]))
    print("Wrote %s (%d bytes in %d files); manifest %s" %
          (FOLDER, manifest["total_bytes"], len(files), PACKAGE / "MANIFEST.json"))
    if dirty:
        print("WARNING: package inputs differ from commit %s; rerun after committing for a clean commit line" % commit)


if __name__ == "__main__":
    main()
