# Reproduction and verification

Run commands from this release repository root. `python3 -B
release/reviewer_smoke.py` uses only the standard library and checks release
bytes, source accounting and deck media relationships. It does not rerun
scientific measurements or certify document appearance.

The source workstation uses /home/luo/anaconda3/bin/python (Python 3.11) for
thesis/evaluation; required modules include NumPy, pandas, SciPy,
python-docx, lxml, OpenCV, MediaPipe and pyrealsense2 as applicable. V3 uses
a separate conda environment named v3rt and external detector weights. The
release does not install or modify either environment. Recorded dependency
versions and commands remain in the track documentation and
knowledge/external_references.md; a universal fresh-machine environment
has not been demonstrated.

The current manuscript checker dependency closure includes chapter DOCX
files, citation tables, V9 scripts/figures, and the committed submission
baseline/navigation. With the existing scientific Python and Poppler
(pdftohtml/pdftotext) available:

```bash
python -B writing/v9/scripts/check_style.py
python -B writing/v9/scripts/check_refs.py
python -B writing/v9/scripts/verify_submission.py
python -B thesis/check_limits.py
python -B presentation/defense_2026/build_speaker_script.py --check
python -B presentation/defense_2026/make_package.py --self-test
```

The submission checker rewrites validation.json and layout.html. Confirm
those outputs still match the manifest afterwards with reviewer_smoke.py.
The full V9 build instructions are in writing/v9/README.md. Archived V8
binaries and historical authoring task files are deliberately absent;
archived script inclusion does not establish that every past manuscript
can be rebuilt.

Full extraction/replay needs the original .bag recordings in Video/ (and
recordings/ where documented). These recordings and V3 weights are local
excluded data; there is no release download. Historical code retains
absolute /home/luo/Desktop/New_SandBox and bimanual-tracking paths and source
output paths. Their original aliases resolve on the source workstation;
they do not automatically resolve on another machine. Do not run archived
scripts blindly: some write to those legacy locations or expect absent
intermediate outputs. Establish appropriate paths and obtain data before
attempting full reproduction. Pinned scientific output logs are retained;
new logs do not substitute for the recorded evidence.

Unity Editor 6000.3.19f1 is the recorded editor. Open Unity/ only after
providing the required dependencies and checking the track-specific paths.
Package manifests/locks are retained, but generated Library/Temp caches are
excluded. Packages may need network restoration. The MCP package is an
existing optional development dependency, not a reviewer-smoke requirement.
No editor startup, physical camera, fresh model execution, LibreOffice
regeneration, or native Word/PowerPoint playback is certified by the
standard-library smoke check. The final PPTX embeds its media; PDF copies
cannot play films.
