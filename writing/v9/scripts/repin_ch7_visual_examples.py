#!/usr/bin/env python3
"""Regenerate the r6b pins of ch7_visual_examples_sources.json (E-038).

Figure 7.5 is the rail recording's sensor-view stills at frames 95, 505 and
700. E-037 re-ran that capture with the per-recording avatar sizing of
E-036, and E-038 re-ran it again once the arm match moved the elbow and
wrist joints along their bones instead of scaling the bones, so
writing/v9/figures/src/r6b_unity_f000{95,505,700}.png are new bytes and the
sha256 that make_ch7_visual_examples.py asserts no longer match. No script in the repository writes that manifest (the generator only
reads and asserts it), so this script is the missing re-pinning mechanism.

Scope, by author decision (E-037, unchanged for E-038): the r6b entry ONLY. Figure 7.6 keeps its
old r7 sources and pins, so nothing under recordings.r7 is touched, and
neither is shared_evidence. The script reports, without changing them, any
r7 or shared entry whose file no longer hashes to its pin, so a stale r7
pin is escalated rather than quietly corrected.

Nothing is invented and nothing is widened: every sha256 is recomputed from
the file the manifest itself names, every image's recorded size_pixels is
re-measured from the image, the pinned frame numbers and phases are left
exactly as they are, and the r6b capture_context is rewritten from the
capture's own record, writing/v9/figures/src/r6b_unity_sensor/
rig_sizing_used.txt, plus the current decision identifier. If a listed r6b file is
missing, the script stops instead of dropping the entry.

Run from the repository root, then re-run make_ch7_visual_examples.py:
    /home/luo/anaconda3/bin/python writing/v9/scripts/repin_ch7_visual_examples.py
"""
import hashlib
import json
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[3]
MANIFEST = (REPO / 'writing/v9/audit_evidence/remove_intermediate_frame'
            / 'ch7_visual_examples_sources.json')
SIZING = REPO / 'writing/v9/figures/src/r6b_unity_sensor/rig_sizing_used.txt'
ALIAS = 'r6b'
DECISION = 'E-038'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resolve(relative_path):
    path = REPO / relative_path
    if not path.exists():
        raise SystemExit(f'listed source is missing: {relative_path}')
    return path


def repin_entry(entry, label, changes):
    """Recompute the sha256 of one {path, sha256, ...} entry in place."""
    path = resolve(entry['path'])
    new = digest(path)
    if entry['sha256'] != new:
        changes.append((label, entry['path'], entry['sha256'], new))
        entry['sha256'] = new
    # An entry that records where the bytes came from carries the same
    # digest under original_sha256 when the copy is byte-identical; keep
    # that relationship true instead of leaving a stale second copy.
    if entry.get('original_path') == entry['path']:
        if entry.get('original_sha256') != new:
            changes.append((label + '.original', entry['path'],
                            entry.get('original_sha256'), new))
            entry['original_sha256'] = new
    return path


def capture_context():
    """The r6b capture context, read from the capture's own sizing record."""
    fields = dict(line.split('=', 1) for line in
                  SIZING.read_text().split() if '=' in line)
    lengths = ', '.join(
        f'{name} {fields["requested_" + name]} m' for name in
        ('upper_arm_R', 'forearm_R', 'upper_arm_L', 'forearm_L', 'torso'))
    return (
        f'Sensor-view capture of recovery_{ALIAS} re-run on 2026-09-14 under '
        f'Decision {DECISION} with the per-recording avatar sizing of E-036, '
        f'replacing the E-037 capture of the same day. The rig carried the '
        f'replayed recording’s own landmark geometry, as the capture '
        f'recorded it in {SIZING.relative_to(REPO).as_posix()} for stem '
        f'{fields["stem"]}: {lengths}. Logs, stream and stills are archived '
        f'under writing/v9/figures/src/r6b_unity_sensor/ and '
        f'writing/v9/figures/src/r6b_unity_f*.png. These images are '
        f'qualitative examples; no identity with the trajectory-table '
        f'capture is asserted.')


def main():
    spec = json.loads(MANIFEST.read_text())
    recording = spec['recordings'][ALIAS]
    changes, untouched = [], []

    for entry in recording['evidence']:
        repin_entry(entry, f'{ALIAS}.evidence', changes)
    for row in recording['rows']:
        for key in ('recorded_video', 'unity'):
            path = repin_entry(row[key], f"{ALIAS}.frame{row['frame']}.{key}",
                               changes)
            with Image.open(path) as image:
                size = list(image.size)
            if row['size_pixels'] != size:
                changes.append((f"{ALIAS}.frame{row['frame']}.size_pixels",
                                row[key]['path'], row['size_pixels'], size))
                row['size_pixels'] = size

    old_context = recording['capture_context']
    new_context = capture_context()
    if old_context != new_context:
        changes.append((f'{ALIAS}.capture_context', '(text)', old_context,
                        new_context))
        recording['capture_context'] = new_context

    # Report only: out of scope by author decision.
    for entry in spec['shared_evidence']:
        actual = digest(resolve(entry['path']))
        if actual != entry['sha256']:
            untouched.append(('shared_evidence', entry['path'],
                              entry['sha256'], actual))
    for entry in spec['recordings']['r7']['evidence']:
        actual = digest(resolve(entry['path']))
        if actual != entry['sha256']:
            untouched.append(('r7.evidence', entry['path'], entry['sha256'],
                              actual))
    for row in spec['recordings']['r7']['rows']:
        for key in ('recorded_video', 'unity'):
            actual = digest(resolve(row[key]['path']))
            if actual != row[key]['sha256']:
                untouched.append((f"r7.frame{row['frame']}.{key}",
                                  row[key]['path'], row[key]['sha256'],
                                  actual))

    for label, path, old, new in changes:
        print(f'repin {label} {path}\n  old {old}\n  new {new}')
    if changes:
        MANIFEST.write_text(json.dumps(spec, indent=2) + '\n')
        print(f'wrote {MANIFEST.relative_to(REPO)} '
              f'({len(changes)} {ALIAS} pins regenerated)')
    else:
        print(f'every {ALIAS} pin already matched; file untouched')

    for label, path, old, new in untouched:
        print(f'ESCALATE (left unchanged, out of scope) {label} {path}\n'
              f'  pinned {old}\n  actual {new}')
    print(f'PASS: {ALIAS} pins regenerated from the archived capture; '
          f'{len(untouched)} out-of-scope mismatch(es) reported, not changed')


if __name__ == '__main__':
    main()
