#!/usr/bin/env python3
"""Slide 33 still: the Python forward-kinematics skeleton over the RGB frame (D-390).

2026-10-06 (plan declarative-stargazing-phoenix.md, step 1). The only tool in
the repository that draws the Python FK chain over the colour frame is
eval/inspect/check_v1_overlay.py (green = measured landmarks, red = FK right
arm, blue = FK left arm, magenta = root forward arrow). This script

1. runs check_v1_overlay.py on the handover recording (stem
   recording_20260909_000024, the R7 bag) with the baseline solver into a work
   directory outside the repository (default: a scratch folder given by
   --work). The baseline run is used rather than the existing
   eval/output/v1_check/v1_overlay_recovery.mp4 (also R7, 1499 frames)
   because the recovery render adds the object-derived wrist cross and a red
   failure banner that the slide label does not explain;
2. checks the overlay video has 1499 frames at 640 x 480 (the landmark CSV
   length);
3. decodes frame FRAME (0-based index; the burned-in counter reads f630) to
   media/p33_fk_overlay.png with unchanged decoded pixels;
4. writes media/provenance/p33_fk_overlay.json (command, mp4 and png
   sha256, frame choice and its evidence).

Frame choice (FRAME = 630, 21.01 s): inside the right-hand-alone interval
426-863 of writing/v9/audit_evidence/ch7_restructured/spatial_check.json;
spatial_check_pairs.csv marks the right wrist at frame 630 included (hold
distance 14.56 cm < 25 cm hold radius), so the right hand holds the cube; all
eight landmarks carry src 0 (measured) in the filtered CSV, so the frame is
unoccluded; the magenta root arrow is short there and does not cross the arms
(frames 600-780 viewed on a contact sheet, 2026-10-06).

Run from the repository root with the thesis Python:

    /home/luo/anaconda3/bin/python -B presentation/defense_2026/anim/fk_overlay_still.py --work DIR
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
STEM = 'recording_20260909_000024'
BAG = ROOT / 'Video' / f'{STEM}.bag'
ARCHIVE_BAG = ROOT / 'recordings' / 'R7_rail_handover_two_hand_accepted_20260909_000024.bag'
CSV = ROOT / 'v1' / 'mediapipe' / 'output' / f'{STEM}_landmarks_filtered.csv'
PAIRS = ROOT / 'writing' / 'v9' / 'audit_evidence' / 'ch7_restructured' / 'spatial_check_pairs.csv'
SPATIAL = ROOT / 'writing' / 'v9' / 'audit_evidence' / 'ch7_restructured' / 'spatial_check.json'
OVERLAY = ROOT / 'eval' / 'inspect' / 'check_v1_overlay.py'
OUT_PNG = HERE / 'media' / 'p33_fk_overlay.png'
OUT_JSON = HERE / 'media' / 'provenance' / 'p33_fk_overlay.json'
FRAME = 630               # chosen frame, see the module docstring
N_FRAMES = 1499           # rows of the filtered landmark CSV (checked below)
SIZE = (640, 480)         # colour stream of the R7 bag (landmark meta.json)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', required=True, help='directory for the overlay run (outside the repo)')
    args = ap.parse_args()
    work = Path(args.work).resolve()
    work.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(CSV)
    if len(df) != N_FRAMES or int(df.loc[FRAME, 'frame']) != FRAME:
        raise SystemExit(f'ERROR: {CSV.name} has {len(df)} rows or frame {FRAME} misnumbered')
    src = {c: int(df.loc[FRAME, c]) for c in df.columns if c.endswith('_src')}
    if any(v != 0 for v in src.values()):
        raise SystemExit(f'ERROR: frame {FRAME} has a non-measured landmark: {src}')
    pairs = pd.read_csv(PAIRS)
    row = pairs[(pairs.side == 'right') & (pairs.frame == FRAME)]
    if len(row) != 1 or int(row.included.iloc[0]) != 1 or row.part.iloc[0] != 'right':
        raise SystemExit(f'ERROR: frame {FRAME} is not an included right-hand-alone frame')
    interval = json.loads(SPATIAL.read_text())['intervals']['right']['frames']
    if not interval[0] <= FRAME <= interval[1]:
        raise SystemExit(f'ERROR: frame {FRAME} outside the right-hand-alone interval {interval}')

    cmd = ['/home/luo/anaconda3/bin/python', '-B', str(OVERLAY.relative_to(ROOT)), '--stem', STEM,
           '--solver', 'baseline', '--out', str(work)]
    run = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)
    mp4 = work / 'v1_overlay_baseline.mp4'

    cap = cv2.VideoCapture(str(mp4))
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    if n != N_FRAMES or size != SIZE:
        raise SystemExit(f'ERROR: overlay video has {n} frames at {size}')
    img = None
    for i in range(FRAME + 1):          # sequential decode, no seek inaccuracy
        ok, img = cap.read()
        if not ok:
            raise SystemExit(f'ERROR: decode failed at frame {i}')
    cap.release()
    if not cv2.imwrite(str(OUT_PNG), img):
        raise SystemExit('ERROR: PNG write failed')
    back = cv2.imread(str(OUT_PNG))
    if not np.array_equal(back, img):
        raise SystemExit('ERROR: PNG differs from the decoded frame')

    record = {
        'status': 'PASS',
        'slide': 33,
        'kind': 'fk_overlay_still',
        'purpose': 'Slide 33: the Python forward-kinematics skeleton drawn over the RGB frame '
                   '(author request 2026-10-06, D-390).',
        'asset': str(OUT_PNG.relative_to(ROOT)),
        'dimensions': list(SIZE),
        'sha256': {'png': sha(OUT_PNG), 'source_mp4': sha(mp4)},
        'bytes': {'png': OUT_PNG.stat().st_size, 'source_mp4': mp4.stat().st_size},
        'recording': {'stem': STEM, 'alias': 'r7 (handover)', 'bag': str(BAG.relative_to(ROOT)),
                      'archive_bag': str(ARCHIVE_BAG.relative_to(ROOT)),
                      'bag_bytes': BAG.stat().st_size},
        'source_mp4': {'path': str(mp4), 'kept_in_repo': False,
                       'frames': n, 'fps': 30, 'codec': 'libx264 CRF 22 yuv420p (check_v1_overlay.py)',
                       'command': ' '.join(cmd), 'cwd': str(ROOT),
                       'stdout_tail': run.stdout.strip().splitlines()[-6:]},
        'frame': {'index': FRAME, 'burned_in_label': f'f{FRAME}', 'time_s': float(df.loc[FRAME, 'time_s']),
                  'decode': 'OpenCV sequential read of frames 0..index; PNG pixels equal the decoded frame'},
        'why_this_frame': {
            'statement': 'Right hand holds the cube and nothing is occluded: inside the right-hand-alone '
                         'interval, included for the right wrist in the spatial check, all landmarks measured, '
                         'short root arrow clear of both arms (contact sheet of frames 600-780 viewed).',
            'right_hand_alone_interval': interval,
            'interval_source': str(SPATIAL.relative_to(ROOT)) + ' intervals.right.frames',
            'pairs_row': {'source': str(PAIRS.relative_to(ROOT)), 'side': 'right', 'part': 'right',
                          'included': 1, 'hold_distance_cm': round(float(row.hold_distance_cm.iloc[0]), 2),
                          'hold_radius_cm': 25.0},
            'landmark_src_codes': src,
        },
        'legend': {'green': 'measured MediaPipe landmarks (filtered, sensor frame)',
                   'red': 'FK right arm (baseline ChainFallbackSolver angles)',
                   'blue': 'FK left arm', 'magenta': 'root forward arrow from the pelvis midpoint'},
        'not_used': {'path': 'eval/output/v1_check/v1_overlay_recovery.mp4',
                     'sha256': '0bd8c07b4ce310ed4a492a1e2dfecef68668fc6c0949334ff08bce3f51fd0b39',
                     'why': 'R7 as well (1499 frames; frame 450 matches writing/v9/figures/src/'
                            'r7_frame00450.png), but rendered with --recovery: object-derived wrist cross '
                            'and failure banner not covered by the slide label'},
        'inputs': {str(p.relative_to(ROOT)): sha(p) for p in (OVERLAY, CSV, PAIRS, SPATIAL)},
        'generator': str(Path(__file__).resolve().relative_to(ROOT)),
        'generator_sha256': sha(Path(__file__).resolve()),
    }
    OUT_JSON.write_text(json.dumps(record, indent=2, ensure_ascii=True) + '\n', encoding='ascii')
    print(json.dumps({'png': record['sha256']['png'], 'mp4': record['sha256']['source_mp4'], 'frame': FRAME}))


if __name__ == '__main__':
    main()
