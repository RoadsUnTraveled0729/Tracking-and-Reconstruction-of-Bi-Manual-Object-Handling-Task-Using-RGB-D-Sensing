#!/usr/bin/env python3
"""Run an exact frozen extractor copy with one logging-only hook.

The hook records the exact RGB array passed to MediaPipe in the same loop.
It does not change inference, timestamps, gates, deprojection, or CSV rows.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ORIGINAL = ROOT / 'v1/mediapipe/extract_landmarks_to_csv.py'


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--page', required=True, type=int)
    parser.add_argument('--bag', required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--model', required=True)
    args = parser.parse_args()
    out = Path(args.out)
    folder = out.parent
    cache = Path('/tmp/defense_bank_rgb') / f'p{args.page:02d}'
    cache.mkdir(parents=True, exist_ok=True)
    source_dir = HERE / 'sources'
    source_dir.mkdir(parents=True, exist_ok=True)
    source = ORIGINAL.read_text()
    needle = '            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.ascontiguousarray(rgb))'
    assert source.count(needle) == 1
    altered = source.replace(needle, '            _bank_record_input(frame_count, frames, color_frame, depth_frame, rgb, rel_s)\n' + needle)
    copy = source_dir / 'extract_landmarks_logged.py'
    copy.write_text(altered)
    diff = ''.join(difflib.unified_diff(source.splitlines(True), altered.splitlines(True),
                                      fromfile=str(ORIGINAL), tofile=str(copy)))
    (source_dir / 'extractor_logging_only.diff').write_text(diff)
    records = []

    def record(index, frames, color, depth, rgb, rel_s):
        import numpy as np
        from PIL import Image
        array = np.ascontiguousarray(rgb)
        path = cache / f'frame_{index:05d}.png'
        Image.fromarray(array, 'RGB').save(path)
        records.append({
            'frame': index, 'relative_time_s': float(rel_s),
            'frameset_timestamp_ms': float(frames.get_timestamp()),
            'color_hardware_frame_number': int(color.get_frame_number()),
            'color_timestamp_ms': float(color.get_timestamp()),
            'color_timestamp_domain': str(color.get_frame_timestamp_domain()),
            'depth_hardware_frame_number': int(depth.get_frame_number()),
            'depth_timestamp_ms': float(depth.get_timestamp()),
            'rgb_shape': list(array.shape),
            'inference_rgb_sha256': hashlib.sha256(array.tobytes()).hexdigest(),
            'cached_png': str(path), 'cached_png_sha256': digest(path)})

    previous = sys.argv
    sys.argv = [str(ORIGINAL), '--bag', args.bag, '--out', args.out,
                '--model', args.model, '--delegate', 'cpu',
                '--min-vis', '0.5', '--depth-window', '5']
    namespace = {'__name__': '__main__', '__file__': str(ORIGINAL),
                 '_bank_record_input': record}
    try:
        exec(compile(altered, str(copy), 'exec'), namespace)
    finally:
        sys.argv = previous
    import pandas as pd
    df = pd.read_csv(out)
    assert len(df) == len(records)
    assert df['frame'].tolist() == [r['frame'] for r in records]
    assert max(abs(df['time_s'].iloc[i] - r['relative_time_s'])
               for i, r in enumerate(records)) <= 0.00000051
    manifest = {
        'status': 'COMPLETE', 'page': args.page, 'frames': len(records),
        'sources': {key: {'path': str(path), 'sha256': digest(path)} for key, path in
                    {'bag': Path(args.bag), 'model': Path(args.model),
                     'frozen_extractor': ORIGINAL, 'instrumented_copy': copy,
                     'logging_adapter': Path(__file__),
                     'logging_diff': source_dir / 'extractor_logging_only.diff'}.items()},
        'raw_csv': {'path': str(out), 'sha256': digest(out)},
        'raw_metadata': {'path': str(out.with_suffix('.meta.json')),
                         'sha256': digest(out.with_suffix('.meta.json'))},
        'clock_check': 'Exact in-process enumeration and relative time agree with the CSV.',
        'records': records}
    (folder / 'inference_frame_map.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f'LOGGED {len(records)} exact inference frames for p{args.page:02d}', flush=True)


if __name__ == '__main__':
    main()
