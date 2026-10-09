#!/usr/bin/env python3
"""Path-only adapter for the repository's unchanged v1 overlay checker.

The checker has no --csv argument. A presentation-local input tree supplies
its expected filenames; ROOT is redirected only after its frozen imports.
No numerical checker function or threshold is replaced.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--page', type=int, required=True)
    parser.add_argument('--bag', required=True)
    args = parser.parse_args()
    source = ROOT / 'eval/inspect/check_v1_overlay.py'
    spec = importlib.util.spec_from_file_location('frozen_v1_overlay_checker', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    local_root = HERE / 'checker_inputs'
    inputs = local_root / 'v1/mediapipe/output'
    inputs.mkdir(parents=True, exist_ok=True)
    folder = HERE / f'p{args.page:02d}'
    stem = f'bank_p{args.page:02d}'
    files = {'filtered': (folder / 'landmarks_filtered.csv', inputs / f'{stem}_landmarks_filtered.csv'),
             'meta': (folder / 'landmarks_raw.meta.json', inputs / f'{stem}_landmarks_raw.meta.json')}
    for src, dst in files.values():
        shutil.copyfile(src, dst)
        assert sha(src) == sha(dst)
    module.ROOT = local_root
    out = folder / 'v1_overlay_check'
    sys.argv = [str(source), '--stem', stem, '--bag', args.bag,
                '--solver', 'both', '--video-solver', 'baseline', '--out', str(out)]
    module.main()
    report = {'status': 'COMPLETED', 'page': args.page,
        'qualification': 'The unchanged checker produces diagnostic FK overlays and residuals, not an external-accuracy verdict.',
        'adapter': {'path': str(Path(__file__)), 'sha256': sha(__file__)},
        'frozen_checker': {'path': str(source), 'sha256': sha(source)},
        'path_adaptation': 'Only module.ROOT redirects expected CSV/meta paths into a track-local input tree; --bag and --out are explicit.',
        'numeric_logic_changed': False,
        'inputs': {k: {'original': str(a), 'copy': str(b), 'sha256': sha(a)} for k, (a, b) in files.items()},
        'outputs': {p.name: {'path': str(p), 'sha256': sha(p)} for p in out.iterdir() if p.is_file()}}
    (folder / 'v1_overlay_check.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
