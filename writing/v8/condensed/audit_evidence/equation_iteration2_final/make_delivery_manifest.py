"""Write the second thesis delivery's exact changed-file list and hashes.

The first pushed delivery is the immutable comparison baseline. The manifest
excludes its own hash to avoid circularity; Git identifies the containing
second-delivery commit. Run from the repository root after all report writes.
"""
import hashlib
import json
import subprocess
from pathlib import Path


OUT = Path(__file__).resolve().parent
REPO = OUT.parents[4]
BASELINE = "e69dfa62eda80bc0ba5d0c4607a3a183a69f71fb"
LIST = OUT / "changed_files_second_delivery.txt"
MANIFEST = OUT / "delivery_manifest.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, check=True,
                          capture_output=True, text=True).stdout.splitlines()


paths = set(git("diff", "--name-only", BASELINE))
paths.update(git("ls-files", "--others", "--exclude-standard"))
paths.update(path.relative_to(REPO).as_posix() for path in (LIST, MANIFEST))
outside = sorted(path for path in paths if not path.startswith("writing/v8/"))
assert not outside, f"Unexpected changes outside the thesis track: {outside}"
LIST.write_text("\n".join(sorted(paths)) + "\n")
baseline_paths = set(git("ls-tree", "-r", "--name-only", BASELINE, "--", "writing/v8"))
files = []
for name in sorted(paths):
    path = REPO / name
    if path == MANIFEST:
        continue
    assert path.is_file(), f"Unexpected deleted or non-file delivery path: {name}"
    files.append({"path": name, "status": "modified" if name in baseline_paths else "added",
                  "bytes": path.stat().st_size, "sha256": sha(path)})
identity = json.loads((OUT / "delivery_artifact_identity.json").read_text())
qa = json.loads((OUT / "pdf_global_qa.json").read_text())
assert qa["status"] == "PASS" and identity["pdf_sha256"] == qa["pdf_sha256"]
assert identity["count"] == 56 and not identity["scope_modified_paths_outside_v8"]
manifest = {
    "delivery": "Second authorized thesis delivery, 2026-09-13",
    "baseline_first_pushed_commit": BASELINE,
    "remote_destination": "origin/master",
    "history_policy": "Normal additive commit and fast-forward push; no force push.",
    "second_delivery_commit": "The commit containing writing/v8/condensed/DELIVERY_2026-09-13.md",
    "identify_commit_command": "git log -1 --format=%H -- writing/v8/condensed/DELIVERY_2026-09-13.md",
    "verify_remote_command": "git ls-remote origin refs/heads/master",
    "artifacts": {
        "writing/v8/Thesis_V8_Condensed.docx": identity["docx_sha256"],
        "writing/v8/Thesis_V8_Condensed.pdf": identity["pdf_sha256"],
    },
    "physical_pdf_pages": qa["pages"],
    "numbered_equations_reviewed": identity["count"],
    "changed_file_count_including_manifest": len(paths),
    "file_list": LIST.relative_to(REPO).as_posix(),
    "manifest_self_hash": "Omitted to avoid circularity; Git pins this manifest.",
    "files": files,
}
for name, expected in manifest["artifacts"].items():
    assert sha(REPO / name) == expected, f"Artifact changed since verification: {name}"
MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
print("PASS: wrote", len(paths), "changed paths and", len(files), "file hashes.")
print("Manifest SHA256:", sha(MANIFEST))
