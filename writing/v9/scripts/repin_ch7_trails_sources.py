#!/usr/bin/env python3
"""Rewrite writing/v9/ch7_trails_source_hashes.json for the same key list.

validate_ch7_trails_revision.py asserts that forty protected source files
still carry the size and sha256 recorded in that file: the recording, the
filtered landmarks, the cleaned object track, the scene calibration, the
recovery angles, the saved trails and stream, the waypoints, the wrist
trajectory record and the archived stills. Only readers of that file exist
in the repository, so this script is the missing re-pinning mechanism.

E-037 re-ran the rail sensor-view capture with the per-recording avatar
sizing of E-036, which replaced five archived stills
(figures/src/r6b_unity_f000{95,114,505,700,898}.png). Their recorded
digests are therefore stale by construction, and the validator stops on the
first one.

The key list is FIXED: exactly the keys already in the file, in their
existing order. This script never adds a protected file, never drops one,
and never removes a check; it only recomputes size and sha256 from the file
each key names, and refuses to write anything if a key's file is missing. It
prints every key whose digest moved so the change is auditable.

Run from the repository root, then re-run the validator:
    /home/luo/anaconda3/bin/python writing/v9/scripts/repin_ch7_trails_sources.py
    /home/luo/anaconda3/bin/python writing/v9/scripts/validate_ch7_trails_revision.py
"""
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
HASHES = REPO / 'writing/v9/ch7_trails_source_hashes.json'


def digest(path):
    hasher = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def main():
    protected = json.loads(HASHES.read_text())
    missing = [key for key in protected if not (REPO / key).exists()]
    if missing:
        raise SystemExit('refusing to rewrite: protected sources are missing: '
                         + ', '.join(missing))

    changed = []
    for key, recorded in protected.items():
        path = REPO / key
        new = {'bytes': path.stat().st_size, 'sha256': digest(path)}
        if new != {k: recorded[k] for k in new if k in recorded}:
            # Copy before mutating, so the printed "old" is the value that
            # was actually recorded and not the value just written.
            changed.append((key, dict(recorded), new))
            # Keep whatever other fields the record carries; replace only
            # the two the validator checks.
            recorded.update(new)

    for key, old, new in changed:
        print(f'repin {key}\n'
              f'  old {old["sha256"]}  {old["bytes"]} bytes\n'
              f'  new {new["sha256"]}  {new["bytes"]} bytes')
    if changed:
        HASHES.write_text(json.dumps(protected, indent=2) + '\n')
        print(f'wrote {HASHES.relative_to(REPO)}: '
              f'{len(changed)} of {len(protected)} keys re-pinned, key list unchanged')
    else:
        print(f'all {len(protected)} protected sources already match; file untouched')


if __name__ == '__main__':
    main()
