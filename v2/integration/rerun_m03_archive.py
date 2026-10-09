"""Rerun corrected M03 validation from the committed rail input archive.

A validation exit code of 1 is expected: the historical replay fails the
lag and p95 bounds. This runner preserves that exit status and report.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--report-json', type=Path,
                    default=ROOT/'v2/dataset/m03_rail_corrected.json')
    args = ap.parse_args()
    archive = ROOT/'v2/dataset/m03_rail_inputs.zip'
    manifest = json.loads((ROOT/'v2/dataset/m03_rail_manifest.json').read_text())
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == manifest['archive_sha256']
    with tempfile.TemporaryDirectory(prefix='m03_rail_') as directory:
        work = Path(directory)
        with zipfile.ZipFile(archive) as z:
            z.extractall(work)
        for item in manifest['files']:
            assert hashlib.sha256((work/item['archive_path']).read_bytes()).hexdigest() == item['sha256']
        result = subprocess.run([
            sys.executable, str(ROOT/'v2/integration/validate_v2_r5.py'),
            '--alias', 'r6b', '--one-handed', '--input-dir', str(work/'live'),
            '--reference-dir', str(work/'reference'),
            '--report-json', str(args.report_json.resolve())])
        report = json.loads(args.report_json.read_text())
        # Normalize ephemeral paths so the committed output is reproducible.
        for entry in report['inputs']:
            entry['path'] = 'm03_rail_inputs.zip:' + str(Path(entry['path']).relative_to(work))
        report['provenance'] = manifest['provenance']
        report['archive_sha256'] = manifest['archive_sha256']
        args.report_json.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
