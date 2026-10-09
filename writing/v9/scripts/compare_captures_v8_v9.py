#!/usr/bin/env python3
"""Compare the Chapter 7 capture evidence of V8 with the V9 re-runs (E-036).

The V8 Unity captures sized the avatar with the loop recording's built-in
arm constants, so the rendered-joint errors of Tables 7.3 and 7.4 carried a
configuration mismatch on top of the display path. E-036 sizes the rig per
replayed recording, and the three captures are re-run. This script puts the
two evidence packages side by side:

  old  writing/v8/condensed/audit_evidence/ch7_restructured/human.json
       and bare_model.json, with the rig_dimensions.csv archived beside the
       V8 stills;
  new  writing/v9/audit_evidence/ch7_restructured/ and the V9 archives.

It writes capture_comparison_v8_v9.json and .md into the V9 evidence
folder: per recording, side and joint the reported n, median, p95 and
maximum of both runs and their difference, and the rendered rig dimensions
of both runs against the sizing the recording asks for.

This is a summary comparison, not a frame-matched one. Each capture writes
one row per Unity Update of a wall-clock sender, so the two runs accept
different frame subsets of the same recording; a difference in n is
expected and a difference in a statistic mixes the new rig with the new
subset. Nothing here is recomputed from coordinates: both sides are read as
the evidence files report them.

Usage:
  /home/luo/anaconda3/bin/python writing/v9/scripts/compare_captures_v8_v9.py
  ... --old-root writing/v8/condensed --new-root writing/v9 --out-dir DIR
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OLD_ROOT = REPO / 'writing/v8/condensed'
NEW_ROOT = REPO / 'writing/v9'
EVIDENCE = 'audit_evidence/ch7_restructured'
FOLDERS = {'r6b': 'ch7_trails_revision', 'r7': 'ch7_handover_trails'}
STATS = ('n', 'median', 'p95', 'maximum')
# bare_model.json scopes and references, in the order Chapter 7 reports them
SCOPES = ('section_7_3_frame_set', 'recording_wide_accepted')
REFERENCES = ('vs_raw_measured', 'vs_filtered_measured')
# E-036 sizing json key -> rig_dimensions.csv row (DumpRigDimensions)
RIG_ROWS = {'upper_arm_R': 'upper_arm_R', 'upper_arm_L': 'upper_arm_L',
            'forearm_R': 'forearm_R', 'forearm_L': 'forearm_L',
            'torso': 'torso_hip_to_midshoulder'}
CAVEAT = ('The two captures do not share a frame set. The dumper writes one '
          'row per Unity Update while the sender streams on the wall clock, '
          'so each run keeps a different subset of the recording and the '
          'accepted frames differ. Read this as a comparison of reported '
          'summaries, not as a per-frame difference: a change in n is '
          'expected, and a change in a statistic carries both the new rig '
          'sizing and the new frame subset.')

SOURCES = []


def read_json(path):
    SOURCES.append(path)
    return json.loads(Path(path).read_text())


def read_rig(path):
    """rig_dimensions.csv (segment,meters) as {segment: float}, or None."""
    path = Path(path)
    if not path.exists():
        return None
    SOURCES.append(path)
    rows = {}
    for line in path.read_text().splitlines()[1:]:
        if line.strip():
            segment, value = line.split(',', 1)
            rows[segment] = float(value)
    return rows


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    path = Path(path).resolve()
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return str(path)


def delta(old, new):
    """One quantity of both runs. delta is new minus old, None if either
    side is absent."""
    pair = {'old': old, 'new': new,
            'delta': None if old is None or new is None else new - old}
    return pair


def block(old, new):
    """The four reported statistics of one error distribution."""
    old = old or {}
    new = new or {}
    return {stat: delta(old.get(stat), new.get(stat)) for stat in STATS}


def compare_human(old, new):
    result = {}
    for alias in sorted(set(old) | set(new)):
        o, n = old.get(alias, {}), new.get(alias, {})
        joints = sorted(set(o.get('joints', {})) | set(n.get('joints', {})))
        result[alias] = {
            'captured_frames': delta(o.get('captured_frames'),
                                     n.get('captured_frames')),
            'recording_frames': delta(o.get('recording_frames'),
                                      n.get('recording_frames')),
            'joints': {joint: block(o.get('joints', {}).get(joint),
                                    n.get('joints', {}).get(joint))
                       for joint in joints},
        }
        for side in ('old', 'new'):
            record = (o if side == 'old' else n).get('rig_sizing')
            if record is not None:
                result[alias].setdefault('rig_sizing_guard', {})[side] = record
    return result


def compare_bare(old, new):
    result = {}
    for alias in sorted(set(old) | set(new)):
        o, n = old.get(alias, {}), new.get(alias, {})
        joints = sorted(set(o.get('joints', {})) | set(n.get('joints', {})))
        entry = {'captured_frames': delta(o.get('captured_frames'),
                                          n.get('captured_frames')),
                 'joints': {}}
        for joint in joints:
            oj, nj = o.get('joints', {}).get(joint, {}), n.get('joints', {}).get(joint, {})
            scopes = {}
            for scope in SCOPES:
                os_, ns_ = oj.get(scope, {}), nj.get(scope, {})
                scopes[scope] = {reference: block(os_.get(reference),
                                                  ns_.get(reference))
                                 for reference in REFERENCES}
                scopes[scope]['twist_held_frames'] = delta(
                    os_.get('twist_held_frames'), ns_.get('twist_held_frames'))
                scopes[scope]['twist_measured_frames'] = delta(
                    os_.get('twist_measured_frames'),
                    ns_.get('twist_measured_frames'))
            scopes['rendered_rig_same_frames'] = block(
                oj.get('rendered_rig_same_frames'),
                nj.get('rendered_rig_same_frames'))
            entry['joints'][joint] = scopes
        result[alias] = entry
    return result


def compare_rig(old_root, new_root):
    """Rendered rig dimensions of both runs, against the sizing asked for."""
    result = {}
    for alias, folder in sorted(FOLDERS.items()):
        old = read_rig(old_root / 'figures/src' / folder / 'rig_dimensions.csv')
        new = read_rig(new_root / 'figures/src' / folder / 'rig_dimensions.csv')
        sizing_path = REPO / f'eval/reports/{alias}_rig_sizing.json'
        requested = (read_json(sizing_path)['segment_lengths_m']
                     if sizing_path.exists() else {})
        by_row = {row: requested[key] for key, row in RIG_ROWS.items()
                  if key in requested}
        rows = {}
        for row in sorted(set(old or {}) | set(new or {})):
            rows[row] = dict(delta((old or {}).get(row), (new or {}).get(row)),
                             requested=by_row.get(row))
        result[alias] = {
            'folder': folder,
            'old': rel(old_root / 'figures/src' / folder / 'rig_dimensions.csv'),
            'new': rel(new_root / 'figures/src' / folder / 'rig_dimensions.csv'),
            'sizing': rel(sizing_path) if sizing_path.exists() else None,
            'rows': rows,
        }
    return result


def fmt(value, places=2):
    return '' if value is None else f'{value:.{places}f}'


def stat_columns(entry, places=2):
    """n old/new then median, p95 and maximum as old, new and difference."""
    cells = [fmt(entry['n']['old'], 0), fmt(entry['n']['new'], 0)]
    for stat in ('median', 'p95', 'maximum'):
        cells += [fmt(entry[stat]['old'], places),
                  fmt(entry[stat]['new'], places),
                  fmt(entry[stat]['delta'], places)]
    return cells


def table(lines, header, rows):
    lines.append('| ' + ' | '.join(header) + ' |')
    lines.append('|' + '|'.join(['---'] * len(header)) + '|')
    for row in rows:
        lines.append('| ' + ' | '.join(row) + ' |')
    lines.append('')


def write_markdown(path, report):
    stat_head = ['n old', 'n new', 'median old', 'median new', 'median delta',
                 'p95 old', 'p95 new', 'p95 delta',
                 'max old', 'max new', 'max delta']
    lines = ['# Chapter 7 capture evidence: V8 against V9 (E-036)', '',
             'Old: `%s`  ' % report['old_root'],
             'New: `%s`  ' % report['new_root'],
             'Written: %s' % report['generated_utc'], '',
             '## What this comparison is', '', report['caveat'], '',
             'All error statistics are centimetres; rig dimensions are metres. '
             'Deltas are new minus old.', '']
    lines += ['## Rendered rig errors against the measured landmark '
              '(human.json, Tables 7.3 and 7.4)', '']
    for alias, entry in sorted(report['human'].items()):
        lines.append('### %s' % alias)
        lines.append('')
        lines.append('Captured frames %s to %s of %s recorded frames.'
                     % (fmt(entry['captured_frames']['old'], 0),
                        fmt(entry['captured_frames']['new'], 0),
                        fmt(entry['recording_frames']['new']
                            if entry['recording_frames']['new'] is not None
                            else entry['recording_frames']['old'], 0)))
        lines.append('')
        table(lines, ['joint'] + stat_head,
              [[joint] + stat_columns(stats)
               for joint, stats in sorted(entry['joints'].items())])
    lines += ['## Bare model errors (bare_model.json)', '']
    for alias, entry in sorted(report['bare_model'].items()):
        lines.append('### %s' % alias)
        lines.append('')
        rows = []
        for joint, scopes in sorted(entry['joints'].items()):
            for scope in SCOPES:
                for reference in REFERENCES:
                    rows.append([joint, scope, reference]
                                + stat_columns(scopes[scope][reference]))
            rows.append([joint, 'rendered rig, same frames', 'vs_raw_measured']
                        + stat_columns(scopes['rendered_rig_same_frames']))
        table(lines, ['joint', 'scope', 'reference'] + stat_head, rows)
    lines += ['## Rendered rig dimensions', '',
              'The sizing column is the length '
              '`eval/reports/<alias>_rig_sizing.json` asks the receiver for '
              '(E-036). The V8 captures were made before that rule, so their '
              'arm rows carry the loop recording constants.', '']
    for alias, entry in sorted(report['rig_dimensions'].items()):
        lines.append('### %s (%s)' % (alias, entry['folder']))
        lines.append('')
        table(lines, ['segment', 'old m', 'new m', 'delta m', 'sizing m'],
              [[row, fmt(values['old'], 6), fmt(values['new'], 6),
                fmt(values['delta'], 6), fmt(values['requested'], 4)]
               for row, values in sorted(entry['rows'].items())])
    lines += ['## Sources', '']
    table(lines, ['file', 'sha256'],
          [[entry['path'], entry['sha256']] for entry in report['sources']])
    Path(path).write_text('\n'.join(lines) + '\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--old-root', type=Path, default=OLD_ROOT,
                    help='thesis tree of the old captures (default '
                         'writing/v8/condensed)')
    ap.add_argument('--new-root', type=Path, default=NEW_ROOT,
                    help='thesis tree of the new captures (default writing/v9)')
    ap.add_argument('--out-dir', type=Path, default=None,
                    help='output folder (default <new-root>/' + EVIDENCE + ')')
    args = ap.parse_args()

    old_root, new_root = args.old_root.resolve(), args.new_root.resolve()
    out_dir = (args.out_dir or new_root / EVIDENCE).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    old_human = read_json(old_root / EVIDENCE / 'human.json')
    new_human = read_json(new_root / EVIDENCE / 'human.json')
    old_bare = read_json(old_root / EVIDENCE / 'bare_model.json')['recordings']
    new_bare = read_json(new_root / EVIDENCE / 'bare_model.json')['recordings']

    report = {
        'purpose': 'Chapter 7 capture evidence of V8 against the V9 re-runs '
                   '(E-036 per-recording avatar sizing)',
        'generated_utc': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'old_root': rel(old_root),
        'new_root': rel(new_root),
        'units': 'error statistics in centimetres, rig dimensions in metres; '
                 'delta is new minus old',
        'caveat': CAVEAT,
        'human': compare_human(old_human, new_human),
        'bare_model': compare_bare(old_bare, new_bare),
        'rig_dimensions': compare_rig(old_root, new_root),
    }
    report['sources'] = [{'path': rel(path), 'sha256': digest(path)}
                         for path in sorted(set(SOURCES))]
    report['sources'].append({'path': rel(__file__), 'sha256': digest(__file__)})
    (out_dir / 'capture_comparison_v8_v9.json').write_text(
        json.dumps(report, indent=2, allow_nan=False) + '\n')
    write_markdown(out_dir / 'capture_comparison_v8_v9.md', report)

    changed = 0
    for alias, entry in sorted(report['human'].items()):
        for joint, stats in sorted(entry['joints'].items()):
            for stat in STATS:
                value = stats[stat]['delta']
                if value:
                    changed += 1
                    print('human %s %s %s: %+.4f' % (alias, joint, stat, value))
    print('human.json: %d of %d reported statistics differ'
          % (changed, sum(len(e['joints']) for e in report['human'].values())
             * len(STATS)))
    print('wrote', rel(out_dir / 'capture_comparison_v8_v9.json'))
    print('wrote', rel(out_dir / 'capture_comparison_v8_v9.md'))


if __name__ == '__main__':
    main()
