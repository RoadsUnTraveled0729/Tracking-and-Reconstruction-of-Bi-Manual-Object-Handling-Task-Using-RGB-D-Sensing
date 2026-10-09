#!/usr/bin/env python3
"""Standalone verification of the Chapter 7 evidence package.

The point of this script is independent checkability. It starts from the
committed coordinate pairs in audit_evidence/ch7_restructured and rebuilds
every published summary statistic from them, then asserts that what it
rebuilt equals what the corresponding JSON evidence file states. It never
reads a gitignored recording, so it runs on a clean checkout that has no
landmark CSV, no angle CSV, no Unity integrated stream and no calibration.

It is deliberately independent of the three harnesses that produced the
evidence. It imports nothing from them, uses no numpy and no pandas, and
implements the distance, the median, the 95th percentile and the maximum
in plain Python. The percentile definition under test is the one Section
7.1 states: linear interpolation between ordered observations.

What it checks:
  * every distance is recomputed from the stored coordinate columns, never
    taken from the stored per-row error column; the two must agree, so a
    pairs file whose error column disagrees with its own coordinates fails
  * every published median, p95, maximum and n is recomputed from those
    recomputed distances and compared with the JSON
  * internal consistency: frame sets against the stated n, scope nesting,
    object segment lengths against the stored waypoint coordinates,
    relative error against absolute over physical, derived phase-check
    quantities against the waypoint coordinates
  * cross-file identity: the same measured landmark in two pairs files,
    the rendered-rig block of bare_model.json against human.json
  * committed pinned reports where they exist: the Unity capture logs, the
    calibrated segment lengths, the manual label file, the loop recording
    report, the handover report, and the SHA256 of every provenance source
    still present

What it cannot check is reported as SKIP with the reason and the data that
would be required. Nothing is ever passed silently.

Run from the repository root with no arguments:
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/verify_ch7_restructured.py
Exit status is 1 if any check fails, otherwise 0.
"""
import csv
import hashlib
import json
import math
import sys
import textwrap
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
EVID = REPO / 'writing/v8/condensed/audit_evidence/ch7_restructured'

# Numerical-noise allowances. These cover double-precision arithmetic and
# nothing else: a real disagreement in any of these quantities is at least
# 1e-3 cm, six orders of magnitude above the allowance. They are never
# widened to absorb a discrepancy.
TOL_CM = 1e-9          # re-derived centimetre quantities
TOL_M = 1e-11          # re-derived metre quantities
TOL_UNIT = 1e-12       # dimensionless quantities: fractions, matrix entries

# Display-precision allowance, used only where the evidence stores a value
# already rounded to two decimals and the statistic was computed before that
# rounding. Half a display unit enters through the stored observations and
# half through the stored statistic, so the bound is 0.01 cm. This is a
# statement about stored precision, not a tolerance on a computation.
ROUND_CM = 0.01

PHYSICAL_CM = {'W1 to W2': 25.5, 'W2 to W3': 3.5, 'W3 to W4': 37.5}
AXES = 'xyz'

# Section 7.3.3. The four medians as brief fact 5 gives them and as the
# chapter prints them, keyed by the interval and the hand. The hold radius is
# eval/offset/carry.HOLD_RADIUS, 0.25 m, the gate that decides which frames
# count as at the cube; it is pinned here so the inclusion column is checked
# against the rule rather than against the evidence file's own copy of it.
SPATIAL_CM = {('right', 'right'): 15.77, ('handover', 'right'): 17.91,
              ('handover', 'left'): 15.85, ('left', 'left'): 14.08}
HOLD_RADIUS_CM = 25.0
# The author's approximate scalar tape measurement (brief fact 4) and the
# margin the chapter claims for it, "within about two centimetres". The second
# number is a printed claim under test, not a tolerance on a computation.
PHYSICAL_WRIST_MARKER_CM = 16.0
SPATIAL_CLAIM_CM = 2.0


# --------------------------------------------------------------------------
# statistics, implemented here rather than imported
# --------------------------------------------------------------------------
def percentile(values, q):
    """Linear interpolation between ordered observations (Section 7.1)."""
    ordered = sorted(values)
    n = len(ordered)
    if n == 0:
        raise ValueError('percentile of an empty sample')
    if n == 1:
        return float(ordered[0])
    position = (n - 1) * (q / 100.0)
    lower = int(math.floor(position))
    upper = min(lower + 1, n - 1)
    return float(ordered[lower]
                 + (ordered[upper] - ordered[lower]) * (position - lower))


def summarize(values):
    return dict(n=len(values), median=percentile(values, 50),
                p95=percentile(values, 95), maximum=float(max(values)))


def distance(row, first, second, scale=1.0):
    a = [float(row[first + '_' + x]) for x in AXES]
    b = [float(row[second + '_' + x]) for x in AXES]
    return math.dist(a, b) * scale


def mean_point(points):
    n = len(points)
    return [sum(p[k] for p in points) / n for k in range(3)]


def spread_mm(points):
    return [(max(p[k] for p in points) - min(p[k] for p in points)) * 1000
            for k in range(3)]


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------
def emit(text, indent=6, width=92):
    print(textwrap.fill(text, width=width, initial_indent=' ' * indent
                        if indent and not text.startswith(('PASS', 'SKIP', 'FAIL'))
                        else '',
                        subsequent_indent=' ' * max(indent, 6),
                        break_long_words=False, break_on_hyphens=False))


class Report:
    def __init__(self):
        self.passed = 0
        self.skipped = 0
        self.failed = 0
        self.skips = []
        self.failures = []

    def section(self, title):
        print('')
        print(title)
        print('-' * len(title))

    def skip(self, what, reason):
        self.skipped += 1
        self.skips.append((what, reason))
        emit('SKIP  %s' % what)
        emit('not verifiable here: %s' % reason, indent=8)

    def note(self, text):
        emit(text, indent=6)


class Group:
    """A set of related assertions reported on one line when they all hold."""

    def __init__(self, report, title):
        self.report = report
        self.title = title
        self.items = []
        self.worst = 0.0
        self.worst_unit = ''

    def check(self, label, ok, detail=''):
        self.items.append((bool(ok), label, detail))
        return bool(ok)

    def equal(self, label, got, want):
        return self.check(label, got == want, 'got %r want %r' % (got, want))

    def close(self, label, got, want, tol, unit='cm'):
        got = float(got)
        want = float(want)
        delta = abs(got - want)
        if delta > self.worst:
            self.worst = delta
            self.worst_unit = unit
        return self.check(label, delta <= tol,
                          'got %.17g want %.17g delta %.3g %s tol %.3g'
                          % (got, want, delta, unit, tol))

    def close_list(self, label, got, want, tol, unit='cm'):
        if len(got) != len(want):
            return self.check(label, False,
                              'length %d against %d' % (len(got), len(want)))
        ok = True
        for k, (a, b) in enumerate(zip(got, want)):
            ok = self.close('%s[%d]' % (label, k), a, b, tol, unit) and ok
        return ok

    def done(self, summary=None):
        bad = [item for item in self.items if not item[0]]
        good = len(self.items) - len(bad)
        self.report.passed += good
        self.report.failed += len(bad)
        if summary is None:
            summary = ', '.join(label for ok, label, _ in self.items if ok)
        if good:
            tail = ''
            if self.worst:
                tail = '  [worst delta %.3g %s]' % (self.worst, self.worst_unit)
            emit('PASS  %s: %d check%s, %s%s'
                 % (self.title, good, '' if good == 1 else 's', summary, tail))
        for _, label, detail in bad:
            emit('FAIL  %s: %s' % (self.title, label))
            emit(detail, indent=8)
            self.report.failures.append('%s: %s (%s)'
                                        % (self.title, label, detail))
        return not bad


def load_json(path):
    return json.loads(Path(path).read_text())


def load_csv(path):
    with open(path, newline='') as handle:
        return list(csv.DictReader(handle))


def group_rows(rows, keys):
    out = {}
    for row in rows:
        out.setdefault(tuple(row[k] for k in keys), []).append(row)
    return out


def counts(values):
    out = {}
    for value in values:
        out[str(value)] = out.get(str(value), 0) + 1
    return out


def check_stats(group, label, values, stated, tol=TOL_CM):
    group.equal(label + ' n', len(values), stated['n'])
    computed = summarize(values)
    for key in ('median', 'p95', 'maximum'):
        group.close('%s %s' % (label, key), computed[key], stated[key], tol)


# --------------------------------------------------------------------------
# 1. human rendered-rig errors
# --------------------------------------------------------------------------
def verify_human(rep):
    rep.section('[1] Human rendered-rig errors, Section 7.3 (D-031, D-040, D-043)')
    pairs = load_csv(EVID / 'human_pairs.csv')
    human = load_json(EVID / 'human.json')
    grouped = group_rows(pairs, ('recording', 'side', 'joint'))

    stated_keys = {(alias, name.split('_')[0], name.split('_')[1])
                   for alias, rec in human.items() for name in rec['joints']}
    g = Group(rep, 'human_pairs.csv against human.json')
    g.equal('group sets match', set(grouped), stated_keys)
    g.done()

    for key in sorted(grouped):
        alias, side, joint = key
        rows = grouped[key]
        stated = human[alias]['joints'][side + '_' + joint]
        g = Group(rep, 'human %s %s %s' % (alias, side, joint))
        frames = [int(r['frame']) for r in rows]
        g.equal('frames unique', len(set(frames)), len(frames))
        g.equal('frame set equals human.json frames',
                sorted(frames), sorted(stated['frames']))
        # Distances recomputed from the coordinate columns, never taken from
        # the stored error column.
        errors = [distance(r, 'measured', 'rig', 100.0) for r in rows]
        worst = max(abs(e - float(r['error_cm']))
                    for e, r in zip(errors, rows))
        g.check('stored error column matches its own coordinates',
                worst <= TOL_CM, 'worst row delta %.3g cm' % worst)
        check_stats(g, 'rendered rig error', errors, stated)
        g.equal('root output tag counts',
                counts(int(r['root_tag']) for r in rows),
                stated['root_output_tags'])
        g.done('n=%d, frame set, error column against its own coordinates, '
               'median, p95, maximum, root tags' % len(rows))

    # The reported distances are independent of the scene frame only if the
    # stored linear part is an isometry. It is orthogonal with determinant
    # -1, the handedness change from the right-handed camera frame to the
    # left-handed Unity frame, which preserves every distance.
    for alias, rec in sorted(human.items()):
        matrix = rec['camera_to_unity_linear']
        g = Group(rep, 'human %s camera-to-Unity linear part' % alias)
        for i in range(3):
            for j in range(3):
                dot = sum(matrix[k][i] * matrix[k][j] for k in range(3))
                g.close('orthonormal %d%d' % (i, j), dot, 1.0 if i == j else 0.0,
                        TOL_UNIT, 'unit')
        det = (matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
               - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
               + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]))
        g.close('determinant magnitude is 1, so the map is distance preserving',
                abs(det), 1.0, TOL_UNIT, 'unit')
        g.close('determinant is -1, the camera to Unity handedness change',
                det, -1.0, TOL_UNIT, 'unit')
        g.done()

    # The rig side of every pair against the committed Unity capture log.
    capture_src = REPO / 'writing/v8/condensed/figures/src'
    logs = {'r6b': capture_src / 'ch7_trails_revision/unity_person_log.csv',
            'r7': capture_src / 'ch7_handover_trails/unity_person_log.csv'}
    prefix = {('right', 'elbow'): 'rel', ('right', 'wrist'): 'rh',
              ('left', 'elbow'): 'lel', ('left', 'wrist'): 'lh'}
    for alias, path in sorted(logs.items()):
        if not path.exists():
            rep.skip('human %s rig coordinates against the Unity capture log'
                     % alias,
                     'the committed capture log %s is absent'
                     % path.relative_to(REPO))
            continue
        log = {int(r['frame']): r for r in load_csv(path)}
        g = Group(rep, 'human %s against %s' % (alias, path.name))
        g.equal('captured_frames equals the log length',
                human[alias]['captured_frames'], len(log))
        worst = 0.0
        missing = 0
        for key in sorted(k for k in grouped if k[0] == alias):
            for row in grouped[key]:
                entry = log.get(int(row['frame']))
                if entry is None:
                    missing += 1
                    continue
                tag = prefix[(key[1], key[2])]
                for axis in AXES:
                    worst = max(worst, abs(float(row['rig_' + axis])
                                           - float(entry[tag + '_' + axis])))
                worst = max(worst, abs(float(row['time_s'])
                                       - float(entry['time_s'])))
        g.equal('every scored frame appears in the log', missing, 0)
        g.check('rig coordinates and times equal the logged capture',
                worst <= TOL_M, 'worst delta %.3g m or s' % worst)
        g.done()

    rep.skip('human recording_frames, time_delta_s, pelvis_delta_m and '
             'hip_mapping_delta_m',
             'the synchronization checks of D-031 and D-034 need the raw and '
             'filtered landmark CSVs and the Unity integrated stream under '
             'eval/output, which are gitignored')
    rep.skip('human frame selection (the accepted-frame gate of D-031/D-032)',
             'acceptance needs the landmark source and flag columns, the '
             'failure mask, the person-present span and the detector warmup, '
             'all under eval/output')
    rep.skip('human measured landmark coordinates',
             'the measured column is the raw MediaPipe landmark mapped through '
             'the scene calibration; both the landmark CSV and '
             'scene_calibration_*.json are gitignored, so only the rigidity of '
             'the stored map is checked above')
    return human, grouped


# --------------------------------------------------------------------------
# 2. synthetic removal windows
# --------------------------------------------------------------------------
def verify_synthetic(rep):
    rep.section('[2] Synthetic removal windows, Section 7.3 (D-032)')
    pairs = load_csv(EVID / 'synthetic_pairs.csv')
    synthetic = load_json(EVID / 'synthetic.json')
    selection = load_json(EVID / 'synthetic_selection.json')

    g = Group(rep, 'synthetic.json selection block')
    g.check('selection equals synthetic_selection.json',
            synthetic['selection'] == selection)
    g.done()

    window_size = selection['duration_frames']
    candidates = selection['candidates']
    runs = selection['eligible_runs']
    g = Group(rep, 'synthetic candidate list')
    g.check('every candidate is %d frames' % window_size,
            all(c['stop'] - c['start'] + 1 == window_size for c in candidates))
    g.check('every candidate lies inside an eligible run',
            all(any(a <= c['start'] and c['stop'] <= b for a, b in runs)
                for c in candidates))
    g.check('candidate starts are unique and ordered',
            [c['start'] for c in candidates]
            == sorted({c['start'] for c in candidates}))
    expected = sum(max(0, b - a + 1 - window_size + 1) for a, b in runs)
    g.equal('candidate count equals every window position in the runs',
            len(candidates), expected)
    g.done()
    rep.note('candidate count %d equals the maximum possible, so the '
             'established-grip gate excluded no window inside the run'
             % len(candidates))

    # Replay the documented selection rule on the committed candidate list.
    def remaining(chosen):
        return [c for c in candidates
                if all(c['stop'] < x['start'] or c['start'] > x['stop']
                       for x in chosen)]

    low = min(candidates, key=lambda c: (c['excursion_cm'], c['start']))
    high = min(remaining([low]), key=lambda c: (-c['excursion_cm'], c['start']))
    values = sorted(c['excursion_cm'] for c in candidates)
    target = percentile(values, 50)
    mid = min(remaining([low, high]),
              key=lambda c: (abs(c['excursion_cm'] - target), c['start']))
    replayed = {'lower motion': low, 'intermediate motion': mid,
                'higher motion': high}
    g = Group(rep, 'synthetic selection rule replayed from the candidates')
    for entry in selection['selected']:
        chosen = replayed[entry['window']]
        g.equal('%s span' % entry['window'],
                (entry['start'], entry['stop']), (chosen['start'], chosen['stop']))
        g.close('%s excursion' % entry['window'],
                entry['excursion_cm'], chosen['excursion_cm'], TOL_CM)
    spans = [(e['start'], e['stop']) for e in selection['selected']]
    g.check('selected windows do not overlap',
            all(spans[i][1] < spans[j][0] or spans[j][1] < spans[i][0]
                for i in range(3) for j in range(i + 1, 3)))
    g.done()

    grouped = group_rows(pairs, ('window', 'method', 'joint'))
    stated_keys = {(r['window'], r['method'], r['joint'])
                   for r in synthetic['results']}
    g = Group(rep, 'synthetic_pairs.csv against synthetic.json')
    g.equal('group sets match', set(grouped), stated_keys)
    g.equal('result count', len(synthetic['results']), len(grouped))
    g.done()

    by_window = {e['window']: e for e in selection['selected']}
    for result in sorted(synthetic['results'],
                         key=lambda r: (r['window'], r['method'], r['joint'])):
        key = (result['window'], result['method'], result['joint'])
        rows = sorted(grouped[key], key=lambda r: int(r['frame']))
        g = Group(rep, 'synthetic %s / %s / %s' % key)
        g.equal('frames are the window span',
                [int(r['frame']) for r in rows],
                list(range(result['start'], result['stop'] + 1)))
        g.equal('window span matches the pinned selection',
                (result['start'], result['stop']),
                (by_window[result['window']]['start'],
                 by_window[result['window']]['stop']))
        errors = [distance(r, 'reference', 'reconstructed', 100.0) for r in rows]
        worst = max(abs(e - float(r['error_cm'])) for e, r in zip(errors, rows))
        g.check('stored error column matches its own coordinates',
                worst <= TOL_CM, 'worst row delta %.3g cm' % worst)
        check_stats(g, 'error', errors, result)
        g.done('n=%d, window span, error column against its own coordinates, '
               'median, p95, maximum' % len(rows))

    # The three methods are scored against one unmasked reference.
    for window in sorted(by_window):
        for joint in ('elbow', 'wrist'):
            g = Group(rep, 'synthetic %s %s shared reference' % (window, joint))
            per_method = {}
            for key, rows in grouped.items():
                if key[0] == window and key[2] == joint:
                    per_method[key[1]] = {
                        int(r['frame']): tuple(float(r['reference_' + a])
                                               for a in AXES) for r in rows}
            methods = sorted(per_method)
            base = per_method[methods[0]]
            for other in methods[1:]:
                g.check('%s reference identical to %s' % (other, methods[0]),
                        per_method[other] == base)
            if joint == 'wrist':
                rows = sorted(base.items())
                first = rows[0][1]
                excursion = max(math.dist(point, first)
                                for _, point in rows) * 100
                g.close('excursion recomputed from the reference wrist',
                        excursion, by_window[window]['excursion_cm'], TOL_CM)
            g.done()

    rep.skip('synthetic frame a-1, the sample immediately before each mask',
             'the harness asserts every method matches the reference on that '
             'frame, but it is outside the scored window and is not written to '
             'synthetic_pairs.csv')
    rep.skip('synthetic masking, fresh replay and grip-offset constancy',
             'these are properties of the solve, not of the emitted pairs; '
             'they need eval/failure/harness_recovery.py against the gitignored '
             'landmark and object CSVs')
    rep.skip('synthetic candidate excursions outside the three selected windows',
             'synthetic_pairs.csv holds reference coordinates only for the '
             'selected windows, so the other 164 candidate excursions are '
             'taken from synthetic_selection.json as pinned')


# --------------------------------------------------------------------------
# 3. bare kinematic-model errors
# --------------------------------------------------------------------------
def verify_bare_model(rep, human, human_groups):
    rep.section('[3] Bare kinematic-model wrist and elbow errors '
                '(D-039 to D-043)')
    pairs = load_csv(EVID / 'bare_model_pairs.csv')
    bare = load_json(EVID / 'bare_model.json')
    grouped = group_rows(pairs, ('recording', 'side', 'joint', 'scope'))

    stated_keys = set()
    for alias, rec in bare['recordings'].items():
        for name in rec['joints']:
            side, joint = name.split('_')
            for scope in ('section_7_3_frame_set', 'recording_wide_accepted'):
                stated_keys.add((alias, side, joint, scope))
    g = Group(rep, 'bare_model_pairs.csv against bare_model.json')
    g.equal('group sets match', set(grouped), stated_keys)
    g.done()

    for key in sorted(grouped):
        alias, side, joint, scope = key
        rows = grouped[key]
        stated = bare['recordings'][alias]['joints'][side + '_' + joint][scope]
        g = Group(rep, 'bare model %s %s %s %s' % key)
        frames = [int(r['frame']) for r in rows]
        g.equal('frames unique', len(set(frames)), len(frames))
        g.equal('frame set equals the stated frames',
                sorted(frames), sorted(stated['frames']))
        g.equal('n equals the row count', stated['n'], len(rows))
        raw = [distance(r, 'model', 'measured', 100.0) for r in rows]
        filt = [distance(r, 'model', 'measured_filtered', 100.0) for r in rows]
        worst = max(max(abs(a - float(r['error_cm'])) for a, r in zip(raw, rows)),
                    max(abs(b - float(r['error_vs_filtered_cm']))
                        for b, r in zip(filt, rows)))
        g.check('stored error columns match their own coordinates',
                worst <= TOL_CM, 'worst row delta %.3g cm' % worst)
        check_stats(g, 'vs raw measured', raw, stated['vs_raw_measured'])
        check_stats(g, 'vs filtered measured', filt,
                    stated['vs_filtered_measured'])
        held = [a for a, r in zip(raw, rows) if int(r['twist_tag']) == 1]
        measured = [a for a, r in zip(raw, rows) if int(r['twist_tag']) == 0]
        # Tag 2 is the constrained twist output. It belongs to neither side of
        # the split, so the two counts need not add up to n.
        constrained = [a for a, r in zip(raw, rows) if int(r['twist_tag']) == 2]
        g.equal('twist held frame count', len(held), stated['twist_held_frames'])
        g.equal('twist measured frame count', len(measured),
                stated['twist_measured_frames'])
        g.equal('measured plus held plus constrained accounts for every row',
                len(held) + len(measured) + len(constrained), len(rows))
        if constrained:
            g.check('%d constrained twist frames are in neither split block'
                    % len(constrained), True)
        if held:
            check_stats(g, 'twist held', held,
                        stated['vs_raw_measured_twist_held'])
        else:
            g.equal('twist held block is empty',
                    stated['vs_raw_measured_twist_held'], {'n': 0})
        if measured:
            check_stats(g, 'twist measured', measured,
                        stated['vs_raw_measured_twist_measured'])
        else:
            g.equal('twist measured block is empty',
                    stated['vs_raw_measured_twist_measured'], {'n': 0})
        g.equal('root output tag counts',
                counts(int(r['root_tag']) for r in rows),
                stated['output_tags']['root'])
        g.equal('twist output tag counts',
                counts(int(r['twist_tag']) for r in rows),
                stated['output_tags']['twist'])
        g.done('n=%d, frame set, both error columns against their own '
               'coordinates, median, p95 and maximum against the raw and the '
               'filtered reference, twist split (%d measured, %d held, %d '
               'constrained), root and twist tag counts'
               % (len(rows), len(measured), len(held), len(constrained)))

    for alias, rec in sorted(bare['recordings'].items()):
        for name in sorted(rec['joints']):
            side, joint = name.split('_')
            entry = rec['joints'][name]
            g = Group(rep, 'bare model %s %s scope relations' % (alias, name))
            subset = set(entry['section_7_3_frame_set']['frames'])
            whole = set(entry['recording_wide_accepted']['frames'])
            g.check('capture subset is contained in the accepted frames',
                    subset <= whole,
                    '%d frames outside' % len(subset - whole))
            g.check('capture subset is no larger than the recording-wide set',
                    len(subset) <= len(whole))
            g.check('accepted frames do not exceed the recording length',
                    len(whole) <= rec['recording_frames'])
            g.check('capture subset does not exceed the captured frames',
                    len(subset) <= rec['captured_frames'])
            # The rendered-rig block must be human.json, on the same frames.
            stated = entry['rendered_rig_same_frames']
            reference = human[alias]['joints'][name]
            g.equal('rendered_rig_same_frames n', stated['n'], reference['n'])
            for stat in ('median', 'p95', 'maximum'):
                g.close('rendered_rig_same_frames %s' % stat,
                        stated[stat], reference[stat], 0.0)
            g.equal('capture subset frames equal the human_pairs frames',
                    sorted(subset),
                    sorted(int(r['frame'])
                           for r in human_groups[(alias, side, joint)]))
            g.done('scope nesting, frame counts against the recording and the '
                   'capture, rendered rig block equals human.json, capture '
                   'subset frames equal the human_pairs frames')

            # The same measured landmark appears in both pairs files; the two
            # scene maps must put it in the same place.
            g = Group(rep, 'bare model %s %s measured landmark against '
                           'human_pairs.csv' % (alias, name))
            other = {int(r['frame']): r for r in human_groups[(alias, side, joint)]}
            worst = 0.0
            for row in grouped[(alias, side, joint, 'section_7_3_frame_set')]:
                mate = other[int(row['frame'])]
                for axis in AXES:
                    worst = max(worst, abs(float(row['measured_' + axis])
                                           - float(mate['measured_' + axis])))
            g.check('raw measured coordinates identical in both files',
                    worst <= TOL_M, 'worst delta %.3g m' % worst)
            g.done()

    # Calibrated and avatar segment lengths, against their committed sources.
    rig_files = {'r6b': 'ch7_trails_revision', 'r7': 'ch7_handover_trails'}
    for alias, rec in sorted(bare['recordings'].items()):
        fit = REPO / ('eval/reports/%s_offset_fit.json' % rec['stem'])
        if fit.exists():
            g = Group(rep, 'bare model %s calibrated segment lengths' % alias)
            g.equal('equal to %s segment_lengths_m' % fit.name,
                    rec['calibrated_segment_lengths_m'],
                    load_json(fit)['segment_lengths_m'])
            g.done()
        else:
            rep.skip('bare model %s calibrated segment lengths' % alias,
                     'the pinned fit %s is absent' % fit.name)
        rig = (REPO / 'writing/v8/condensed/figures/src'
               / rig_files[alias] / 'rig_dimensions.csv')
        if rig.exists():
            stored = {r['segment']: float(r['meters']) for r in load_csv(rig)}
            g = Group(rep, 'bare model %s rendered rig segment lengths' % alias)
            g.equal('equal to the captured rig_dimensions.csv',
                    {k: round(v, 9) for k, v in
                     rec['rendered_rig_segment_lengths_m'].items()},
                    {k: round(v, 9) for k, v in stored.items()})
            g.check('D-043: avatar arm lengths are not the calibrated lengths',
                    any(abs(stored[k] - rec['calibrated_segment_lengths_m'][k])
                        > 1e-6 for k in ('upper_arm_R', 'upper_arm_L',
                                         'forearm_R', 'forearm_L')))
            g.done()
        else:
            rep.skip('bare model %s rendered rig segment lengths' % alias,
                     'the captured rig_dimensions.csv is absent')

    # The values Chapter 9 previously printed.
    old = bare['chapter_9_previous_values']
    handover = REPO / 'eval/reports/r7_handover.json'
    g = Group(rep, 'bare model chapter_9_previous_values')
    for side in ('left', 'right'):
        pinned = old['pinned_report'][side]
        g.equal('%s n' % side, old[side]['n'], pinned['n'])
        g.close('%s median rounds to the pinned value' % side,
                round(old[side]['median'], 2), pinned['median'], 0.0)
        g.close('%s p95 rounds to the pinned value' % side,
                round(old[side]['p95'], 2), pinned['p95'], 0.0)
        g.close('%s maximum rounds to the pinned value' % side,
                round(old[side]['maximum'], 2), pinned['max'], 0.0)
    g.check('reproduced flag is set', old['reproduced'] is True)
    if handover.exists():
        g.equal('pinned_report equals eval/reports/r7_handover.json',
                old['pinned_report'],
                load_json(handover)['fk_vs_measured_wrist_cm'])
    g.done()
    if not handover.exists():
        rep.skip('chapter_9_previous_values against its pinned report',
                 'eval/reports/r7_handover.json is absent')
    rep.skip('chapter_9_previous_values recomputation',
             'the superseded definition scores the whole recording against the '
             'filtered landmark, and no pairs file carries those frames; only '
             'the rounding relation to the pinned report is checked')
    rep.skip('bare model display_filter reproduction',
             'the low-pass reproduction of D-039 compares angles_recovery.csv '
             'with the Unity integrated stream, both gitignored')
    rep.skip('bare model swing and elbow output tag counts',
             'bare_model_pairs.csv stores the root and twist tags only, so the '
             'swing and elbow columns of output_tags are taken as pinned')
    rep.skip('bare model forward kinematics',
             'the model coordinates come from the solved angles, the measured '
             'shoulder and the calibrated segment lengths; the angle CSV and '
             'the landmark CSV are gitignored, so the model column is verified '
             'only for internal consistency')
    return bare


# --------------------------------------------------------------------------
# 4. object segment lengths
# --------------------------------------------------------------------------
def verify_object(rep):
    rep.section('[4] Object segment lengths, Section 7.2 (D-035, D-036)')
    pairs = load_csv(EVID / 'object_pairs.csv')
    obj = load_json(EVID / 'object.json')
    rule = obj['detection_rule']
    band_mm = rule['parameters']['departure_band_m'] * 1000

    g = Group(rep, 'object physical reference')
    g.equal('reference lengths of D-035 and brief fact 2',
            {k.replace('_', ' to '): v
             for k, v in rule['physical_reference_cm'].items()}, PHYSICAL_CM)
    g.equal('resolution is 1 mm', rule['physical_resolution_mm'], 1.0)
    g.done()

    grouped = group_rows(pairs, ('recording', 'waypoint'))
    for alias, rec in sorted(obj['recordings'].items()):
        positions = {}
        for name in ('W1', 'W2', 'W3', 'W4'):
            rows = sorted(grouped[(alias, name)], key=lambda r: int(r['frame']))
            stated = rec['waypoints'][name]
            points = [[float(r[a + '_m']) for a in AXES] for r in rows]
            g = Group(rep, 'object %s %s' % (alias, name))
            frames = [int(r['frame']) for r in rows]
            g.equal('n_samples equals the row count', stated['n_samples'], len(rows))
            g.equal('first frame', stated['first_frame'], frames[0])
            g.equal('last frame', stated['last_frame'], frames[-1])
            g.equal('frames strictly increasing', frames, sorted(set(frames)))
            excluded = set(rec['samples']['excluded_frames'])
            span = [f for f in range(frames[0], frames[-1] + 1)
                    if f not in excluded]
            g.equal('interval holds every accepted frame it spans', frames, span)
            g.equal('estimator label matches the sample count',
                    stated['estimator'],
                    'single transition sample' if len(rows) == 1
                    else 'mean of accepted samples')
            g.close_list('position is the mean of those samples',
                         mean_point(points), stated['position_m'], TOL_M, 'm')
            g.close_list('spread', spread_mm(points), stated['spread_mm'],
                         TOL_M * 1000, 'mm')
            g.done('%d sample%s, first and last frame, no accepted frame '
                   'missing from the interval, estimator label, position as '
                   'the mean of those samples, spread'
                   % (len(rows), '' if len(rows) == 1 else 's'))
            positions[name] = mean_point(points)

        g = Group(rep, 'object %s waypoint ordering' % alias)
        order = [rec['waypoints'][w]['first_frame'] for w in ('W1', 'W2', 'W3', 'W4')]
        last = [rec['waypoints'][w]['last_frame'] for w in ('W1', 'W2', 'W3', 'W4')]
        g.check('W1 < W2 < W3 < W4 in frame order',
                all(last[k] < order[k + 1] for k in range(3)))
        g.done()

        g = Group(rep, 'object %s sample accounting' % alias)
        samples = rec['samples']
        g.equal('accepted equals total minus excluded',
                samples['accepted'],
                samples['frames_total'] - len(samples['excluded_frames']))
        g.equal('excluded frame list is unique',
                len(set(samples['excluded_frames'])),
                len(samples['excluded_frames']))
        for reason in ('not_detected', 'filled', 'non_finite_position'):
            g.check('%s count does not exceed the excluded list' % reason,
                    samples[reason] <= len(samples['excluded_frames']))
        g.done()

        for segment in rec['segments']:
            first, second = segment['segment'].split(' to ')
            g = Group(rep, 'object %s %s' % (alias, segment['segment']))
            delta = [positions[second][k] - positions[first][k] for k in range(3)]
            g.close_list('delta_m from the waypoint coordinates',
                         delta, segment['delta_m'], TOL_M, 'm')
            length = math.dist(positions[first], positions[second]) * 100
            g.close('reconstructed length', length,
                    segment['reconstructed_cm'], TOL_CM)
            g.close('physical reference', segment['physical_cm'],
                    PHYSICAL_CM[segment['segment']], 0.0)
            g.close('absolute error', abs(length - segment['physical_cm']),
                    segment['absolute_error_cm'], TOL_CM)
            g.close('relative error is absolute over physical',
                    100 * segment['absolute_error_cm'] / segment['physical_cm'],
                    segment['relative_error_pct'], TOL_UNIT, 'percent')
            biggest = max(range(3), key=lambda k: abs(delta[k]))
            g.equal('dominant axis', AXES[biggest], segment['dominant_axis'])
            g.close('dominant fraction',
                    abs(delta[biggest]) / sum(abs(d) for d in delta),
                    segment['dominant_fraction'], TOL_UNIT, 'unit')
            g.done('delta and length from the waypoint coordinates, physical '
                   'reference, absolute error, relative error as absolute '
                   'over physical, dominant axis and fraction')

        phase = rec['phase_confirmation']
        heights = [positions[w][1] for w in ('W1', 'W2', 'W3', 'W4')]
        segments = rec['segments']
        g = Group(rep, 'object %s phase confirmation, derived quantities' % alias)
        g.equal('W1 first frame of track',
                phase['W1']['evidence']['first_frame_of_track'],
                rec['waypoints']['W1']['first_frame'])
        g.equal('W1 boundary frame', phase['W1']['evidence']['boundary_frame'],
                rec['waypoints']['W1']['last_frame'])
        g.close_list('W1 opening run spread',
                     phase['W1']['evidence']['opening_run_spread_mm'],
                     rec['waypoints']['W1']['spread_mm'], 0.0, 'mm')
        g.close('W1 height above the final level',
                (heights[0] - heights[3]) * 100,
                phase['W1']['evidence']['height_above_final_level_cm'], TOL_CM)
        g.equal('W1 passes recomputed',
                bool(rec['waypoints']['W1']['last_frame']
                     < rec['waypoints']['W2']['first_frame']
                     and max(rec['waypoints']['W1']['spread_mm']) <= band_mm * 3),
                phase['W1']['passes'])
        g.equal('W2 boundary frame', phase['W2']['evidence']['boundary_frame'],
                rec['waypoints']['W2']['first_frame'])
        for label, value in (('height_change_W1_to_W2_cm', heights[1] - heights[0]),
                             ('height_change_W2_to_W3_cm', heights[2] - heights[1]),
                             ('height_change_W3_to_W4_cm', heights[3] - heights[2])):
            g.close('W2 evidence %s' % label, value * 100,
                    phase['W2']['evidence'][label], TOL_CM)
        g.equal('W2 passes recomputed',
                bool(abs(heights[2] - heights[1]) > abs(heights[1] - heights[0])
                     and abs(heights[2] - heights[1]) > abs(heights[3] - heights[2])
                     and segments[1]['dominant_axis'] == 'y'),
                phase['W2']['passes'])
        g.equal('W3 boundary frame', phase['W3']['evidence']['boundary_frame'],
                rec['waypoints']['W3']['first_frame'])
        g.check('W3 axis-dominance half of the pass rule',
                segments[2]['dominant_axis'] == 'x')
        g.equal('W4 interval', phase['W4']['evidence']['interval'],
                [rec['waypoints']['W4']['first_frame'],
                 rec['waypoints']['W4']['last_frame']])
        g.equal('W4 n_samples', phase['W4']['evidence']['n_samples'],
                rec['waypoints']['W4']['n_samples'])
        g.close_list('W4 interval spread',
                     phase['W4']['evidence']['interval_spread_mm'],
                     rec['waypoints']['W4']['spread_mm'], 0.0, 'mm')
        g.close('W4 lateral travel from W3',
                (positions['W4'][0] - positions['W3'][0]) * 100,
                phase['W4']['evidence']['lateral_travel_W3_to_W4_cm'], TOL_CM)
        g.equal('W4 passes recomputed',
                bool(rec['waypoints']['W4']['first_frame']
                     > rec['waypoints']['W3']['first_frame']
                     and positions['W4'][0] > positions['W3'][0]),
                phase['W4']['passes'])
        dominance = phase['segment_axis_dominance']
        for segment, expected in zip(segments, ('z', 'y', 'x')):
            block = dominance[segment['segment']]
            g.equal('%s dominance block axis' % segment['segment'],
                    block['dominant_axis'], segment['dominant_axis'])
            g.close('%s dominance block fraction' % segment['segment'],
                    block['fraction'], segment['dominant_fraction'], 0.0, 'unit')
            g.equal('%s expected axis' % segment['segment'],
                    block['expected'], expected)
            g.equal('%s observed axis equals the expected phase axis'
                    % segment['segment'], segment['dominant_axis'], expected)
        g.done('boundary frames, opening and closing intervals, the four '
               'height changes, the lateral travel, the recomputed W1, W2 and '
               'W4 pass rules, and the segment axis dominance block')

        def caveat(item):
            return next(c for c in rec['caveats'] if c['item'] == item)

        g = Group(rep, 'object %s caveats, derived quantities' % alias)
        band = caveat('detector-selection band')['segments']
        for segment in segments:
            g.close('%s reported length in the band block' % segment['segment'],
                    band[segment['segment']]['reported_cm'],
                    segment['reconstructed_cm'], 0.0)
            g.check('%s band contains the reported length' % segment['segment'],
                    band[segment['segment']]['minimum_cm']
                    <= segment['reconstructed_cm']
                    <= band[segment['segment']]['maximum_cm'])
        g.equal('W2 and W3 are single samples',
                [rec['waypoints'][w]['n_samples'] for w in ('W2', 'W3')], [1, 1])
        averaging = caveat('W1 and W4 averaging intervals')
        g.close_list('W1 spread in the caveat', averaging['W1_spread_mm'],
                     rec['waypoints']['W1']['spread_mm'], 0.0, 'mm')
        g.close_list('W4 spread in the caveat', averaging['W4_spread_mm'],
                     rec['waypoints']['W4']['spread_mm'], 0.0, 'mm')
        w4rows = sorted(grouped[(alias, 'W4')], key=lambda r: int(r['frame']))
        w4 = [[float(r[a + '_m']) for a in AXES] for r in w4rows]
        steps = [math.dist(w4[k], w4[k + 1]) for k in range(len(w4) - 1)]
        worst = max(range(len(steps)), key=lambda k: steps[k])
        g.close('largest single-sample step inside W4',
                steps[worst] * 1000, averaging['W4_largest_step_mm'],
                TOL_M * 1000, 'mm')
        g.equal('frames of that step',
                averaging['W4_largest_step_between_frames'],
                [int(w4rows[worst]['frame']), int(w4rows[worst + 1]['frame'])])
        g.done('the reported length inside its detector-selection band, the '
               'single-sample W2 and W3, the W1 and W4 spreads, and the '
               'largest single-sample step inside W4 with its frames')

    rep.skip('object waypoint detection itself',
             'the velocity estimate, the pre-transition levels, the half-peak '
             'frames and the departure search run over the whole marker track '
             'in eval/output/*_object_world_filtered_clean.csv, which is '
             'gitignored; object_pairs.csv holds only the samples behind the '
             'four waypoints')
    rep.skip('object detector sensitivity block',
             'every perturbed variant re-detects the boundaries on the full '
             'track, so the minimum, maximum and spread of the selection band '
             'are taken from object.json as pinned')
    rep.skip('object fitted-line scatter',
             'the scatter spans every accepted sample between two waypoints; '
             'those intermediate samples are not in object_pairs.csv')
    rep.skip('object rigid_invariance block',
             'it compares the levelled positions with the stored tx, ty, tz of '
             'the gitignored track; object_pairs.csv carries the levelled frame '
             'only')
    rep.skip('object phase evidence that depends on the detector state',
             'the pre-rise and pre-slide levels, the velocity peaks, the '
             'half-peak and coarse-onset frames, the rise-completion frame and '
             'the local depth spread around W2 and W3 all need the full track')


# --------------------------------------------------------------------------
# 5. natural occlusion summary
# --------------------------------------------------------------------------
def verify_natural(rep):
    rep.section('[5] Natural occlusion wrist proxies, Section 7.3 (D-033)')
    natural = load_json(EVID / 'natural.json')
    rows = natural['rows']
    summary = natural['summary']

    g = Group(rep, 'natural.json row accounting')
    g.equal('row count', len(rows), 27)
    g.equal('groups are clean and failure',
            sorted({r['group'] for r in rows}), ['clean', 'failure'])
    g.equal('sides are left and right',
            sorted({r['side'] for r in rows}), ['left', 'right'])
    g.check('no row is marked mixed_surface',
            all(r['mixed_surface'] is False for r in rows))
    g.done()

    for side in ('left', 'right'):
        clean = [r['measured_cm'] for r in rows
                 if r['side'] == side and r['group'] == 'clean']
        g = Group(rep, 'natural clean %s' % side)
        g.equal('n equals the clean row count', summary['clean'][side]['n'],
                len(clean))
        g.check('every clean row carries a measured distance',
                all(v is not None for v in clean))
        if all(v is not None for v in clean):
            computed = summarize(clean)
            for stat, key in (('median', 'median'), ('p95', 'p95'),
                              ('maximum', 'maximum')):
                g.close('%s recomputed from the stored rows' % stat,
                        computed[stat], summary['clean'][side][key], ROUND_CM)
        g.done()
        failure = [r for r in rows
                   if r['side'] == side and r['group'] == 'failure']
        for method in ('plain_fk', 'hold_fk', 'recovery_fk'):
            values = [r[method + '_cm'] for r in failure]
            g = Group(rep, 'natural failure %s %s' % (side, method))
            g.equal('n equals the failure row count',
                    summary['failure'][side][method]['n'], len(values))
            g.check('every failure row carries a value',
                    all(v is not None for v in values))
            if all(v is not None for v in values):
                computed = summarize(values)
                for stat in ('median', 'p95', 'maximum'):
                    g.close('%s recomputed from the stored rows' % stat,
                            computed[stat], summary['failure'][side][method][stat],
                            ROUND_CM)
            g.done()
    rep.note('the natural rows and the natural summary are both stored at two '
             'decimals, so the recomputation above uses the %.2f cm display '
             'allowance, not the %.0e cm arithmetic tolerance' % (ROUND_CM, TOL_CM))

    pinned = REPO / 'eval/reports/r5_recovery_labeled.json'
    if pinned.exists():
        source = load_json(pinned)
        g = Group(rep, 'natural.json against eval/reports/r5_recovery_labeled.json')
        g.equal('rows are the pinned rows',
                [{k: v for k, v in r.items()} for r in rows],
                [{k: (None if isinstance(v, float) and v != v else v)
                  for k, v in r.items()} for r in source['rows']])
        for side in ('left', 'right'):
            block = source['summary']['clean'][side]['measured']
            g.equal('clean %s equals the pinned block' % side,
                    summary['clean'][side],
                    dict(n=block['n'], median=block['median'],
                         p95=block['p95'], maximum=block['max']))
            for method in ('plain_fk', 'hold_fk', 'recovery_fk'):
                block = source['summary']['failure'][side][method]
                g.equal('failure %s %s equals the pinned block' % (side, method),
                        summary['failure'][side][method],
                        dict(n=block['n'], median=block['median'],
                             p95=block['p95'], maximum=block['max']))
        g.done()
    else:
        rep.skip('natural summary against its pinned report',
                 'eval/reports/r5_recovery_labeled.json is absent')

    labels = REPO / 'eval/labels/frames_r5/labels.json'
    meta = REPO / 'eval/labels/frames_r5/meta.json'
    if labels.exists() and meta.exists():
        clicked = load_json(labels)
        clean_frames = {(int(frame), side)
                        for frame, sides in load_json(meta)['clean_frames'].items()
                        for side in sides}
        g = Group(rep, 'natural rows against the committed manual labels')
        worst = 0.0
        missing = 0
        for row in rows:
            label = clicked.get(str(row['frame']), {}).get(row['side'])
            if label is None:
                missing += 1
                continue
            point = label['xyz_cam']
            stored = row['truth_solver']
            # The solver frame negates the sensor y axis.
            worst = max(worst, abs(stored[0] - point[0]),
                        abs(stored[1] + point[1]), abs(stored[2] - point[2]))
            if label['mixed_surface'] != row['mixed_surface']:
                missing += 1
        g.equal('every row has a usable label', missing, 0)
        g.check('truth_solver is the clicked point with the sensor y axis '
                'negated', worst <= TOL_M, 'worst delta %.3g m' % worst)
        g.equal('clean rows are exactly the frames meta.json calls clean',
                {(r['frame'], r['side']) for r in rows if r['group'] == 'clean'},
                clean_frames)
        g.check('no failure row is a clean frame',
                not ({(r['frame'], r['side']) for r in rows
                      if r['group'] == 'failure'} & clean_frames))
        g.done()
    else:
        rep.skip('natural rows against the manual label file',
                 'eval/labels/frames_r5 is absent')

    g = Group(rep, 'natural left failure label set, brief fact 7')
    frames = sorted(r['frame'] for r in rows
                    if r['side'] == 'left' and r['group'] == 'failure')
    g.equal('16 labels: 14 at five-frame spacing from 1427, plus 1777 and 1787',
            frames, list(range(1427, 1493, 5)) + [1777, 1787])
    g.done()

    rep.skip('natural per-row distances',
             'each row distance compares a filtered or model wrist with the '
             'clicked proxy; the filtered landmark CSV and the angle CSVs are '
             'gitignored, so the rows are verified against the committed label '
             'file and the pinned report but are not recomputed')


# --------------------------------------------------------------------------
# 6. loop-recording detection coverage
# --------------------------------------------------------------------------
def expand_runs(runs):
    frames = []
    for run in runs:
        frames.extend(range(run['first_frame'], run['last_frame'] + 1))
    return frames


def overlap(first, second):
    """Frame intervals present in both episode lists."""
    out = []
    for a in first:
        for b in second:
            low, high = max(a[0], b[0]), min(a[1], b[1])
            if low <= high:
                out.append([low, high])
    return sorted(out)


def verify_loop_detection(rep):
    """Optional: the coverage file another evidence pass added beside these.

    It carries counts rather than coordinate pairs, so only its own
    arithmetic and its agreement with natural.json can be checked here. The
    block degrades to a SKIP rather than an error if the file is absent or
    is shaped differently, because it is produced by a separate harness.
    """
    rep.section('[6] Loop-recording object-marker coverage (Section 7.4.2)')
    path = EVID / 'loop_detection.json'
    if not path.exists():
        rep.skip('loop_detection.json',
                 'the file is not part of this evidence directory')
        return
    data = load_json(path)
    needed = ('frames_total', 'first_frame', 'last_frame', 'detected',
              'accepted', 'despiked_and_bridged', 'gap_duration_s',
              'location_of_missing_frames', 'section_7_4_2_label_frames',
              'frame_rate_fps')
    if any(key not in data for key in needed):
        rep.skip('loop_detection.json internal consistency',
                 'the file does not carry the blocks this check expects, so '
                 'nothing is asserted about it rather than asserting the wrong '
                 'thing')
        return

    total = data['frames_total']
    g = Group(rep, 'loop_detection.json frame accounting')
    g.equal('frames_total spans first to last frame',
            total, data['last_frame'] - data['first_frame'] + 1)
    for name in ('detected', 'accepted'):
        block = data[name]
        missing = block['missing_frames']
        g.equal('%s counts add to the total' % name,
                block['n_frames'] + block['n_missing'], total)
        g.equal('%s missing list length' % name, len(missing), block['n_missing'])
        g.equal('%s missing list is unique and ordered' % name,
                missing, sorted(set(missing)))
        g.close('%s coverage per cent' % name,
                100.0 * block['n_frames'] / total, block['coverage_pct'],
                TOL_UNIT, 'percent')
        g.equal('%s missing runs cover exactly the missing frames' % name,
                expand_runs(block['missing_runs']), missing)
        g.check('%s run lengths are consistent' % name,
                all(run['n_frames'] == run['last_frame'] - run['first_frame'] + 1
                    for run in block['missing_runs']))
    g.check('the accepted rule is at least as strict as the detected rule',
            set(data['detected']['missing_frames'])
            <= set(data['accepted']['missing_frames']))
    filled = data['despiked_and_bridged']
    g.equal('filled rows add up',
            len(filled['detected_but_filled']) + len(filled['undetected_and_filled']),
            filled['n_filled'])
    g.equal('accepted misses are the detected misses plus the despiked rows',
            data['accepted']['n_missing'],
            data['detected']['n_missing'] + len(filled['detected_but_filled']))
    g.done('frame totals, both coverage criteria with their missing lists, '
           'runs and percentages, and the despiked and bridged accounting')

    place = data['location_of_missing_frames']
    g = Group(rep, 'loop_detection.json handover span')
    span = place['handover_span']
    g.equal('span runs from the first to the second two-hand interval',
            span, [place['preceding_two_hand_interval']['first_frame'],
                   place['following_two_hand_interval']['last_frame']])
    for key in ('preceding_two_hand_interval', 'following_two_hand_interval',
                'marker_loss_stretch', 'longest_missing_run'):
        block = place[key]
        g.equal('%s length' % key, block['n_frames'],
                block['last_frame'] - block['first_frame'] + 1)
    stretch = place['marker_loss_stretch']
    g.equal('marker loss stretch splits into detected and missing',
            stretch['n_detected'] + stretch['n_missing'], stretch['n_frames'])
    missing = data['detected']['missing_frames']
    inside = [f for f in missing if span[0] <= f <= span[1]]
    outside = [f for f in missing if not span[0] <= f <= span[1]]
    g.equal('missing frames inside the handover span',
            place['n_missing_in_handover_span'], len(inside))
    g.equal('missing frames outside the handover span',
            place['missing_outside_handover_span'], outside)
    g.equal('distance of each outside frame to the span',
            place['distance_of_outside_frames_to_span'],
            [min(abs(f - span[0]), abs(f - span[1])) for f in outside])
    g.equal('marker loss stretch missing frames',
            stretch['n_missing'],
            len([f for f in missing
                 if stretch['first_frame'] <= f <= stretch['last_frame']]))
    runs = data['detected']['missing_runs']
    longest = max(runs, key=lambda run: (run['n_frames'], -run['first_frame']))
    g.equal('longest missing run', place['longest_missing_run'], longest)
    g.close('marker loss stretch duration',
            stretch['n_frames'] / data['frame_rate_fps'],
            data['gap_duration_s']['marker_loss_stretch'], TOL_UNIT, 'second')
    g.close('total missing duration',
            data['detected']['n_missing'] / data['frame_rate_fps'],
            data['gap_duration_s']['all_missing'], TOL_UNIT, 'second')
    g.done('the span endpoints, every interval length, the split of the marker '
           'loss stretch, the frames inside and outside the span with their '
           'distances, the longest missing run and both gap durations')

    episodes = data.get('grip_episodes', {}).get('episodes')
    intervals = data.get('grip_episodes', {}).get('two_hand_intervals')
    if episodes and intervals is not None:
        g = Group(rep, 'loop_detection.json two-hand intervals')
        g.equal('intervals are the overlap of the left and right episodes',
                [[i['first_frame'], i['last_frame']] for i in intervals],
                overlap(episodes['left'], episodes['right']))
        g.check('interval lengths are consistent',
                all(i['n_frames'] == i['last_frame'] - i['first_frame'] + 1
                    for i in intervals))
        g.done()

    labels = data['section_7_4_2_label_frames']
    natural = load_json(EVID / 'natural.json')
    frames = sorted(r['frame'] for r in natural['rows'])
    g = Group(rep, 'loop_detection.json label frames against natural.json')
    g.equal('labelled frame count', labels['n_labelled_frames'], len(frames))
    g.equal('first labelled frame', labels['first_frame'], frames[0])
    g.equal('last labelled frame', labels['last_frame'], frames[-1])
    g.equal('labelled frames without an object marker',
            labels['labelled_frames_without_object_marker'],
            sorted(set(frames) & set(missing)))
    g.done()

    if 'provenance' in data and 'sources' in data['provenance']:
        ok = bad = absent = 0
        broken = []
        for entry in data['provenance']['sources']:
            source = REPO / entry['path']
            if not source.exists():
                absent += 1
                continue
            if hashlib.sha256(source.read_bytes()).hexdigest() == entry['sha256']:
                ok += 1
            else:
                bad += 1
                broken.append(entry['path'])
        g = Group(rep, 'loop_detection.json source hashes')
        g.check('%d of %d recorded sources still hash as recorded'
                % (ok, len(data['provenance']['sources'])), bad == 0,
                'mismatched: %s' % ', '.join(broken))
        g.done()
        if absent:
            rep.skip('loop_detection.json: %d of %d recorded sources are absent'
                     % (absent, len(data['provenance']['sources'])),
                     'they are gitignored local inputs under eval/output, so a '
                     'clean checkout cannot hash them')

    rep.skip('loop_detection.json coverage counts themselves',
             'the detected, accepted, despiked and bridged counts come from the '
             'gitignored object track and its sidecars; this file carries no '
             'coordinate pairs, so only its own arithmetic and its agreement '
             'with natural.json are checked')


# --------------------------------------------------------------------------
# 7. human-object spatial check, Section 7.3.3
# --------------------------------------------------------------------------
def finite(value):
    return not (math.isnan(value) or math.isinf(value))


def agrees(rows, stored_column, computed):
    """Worst delta between a stored column and its recomputation.

    Returns (worst finite delta, number of rows where one side is defined and
    the other is not). A row where both are non-finite agrees: the coordinates
    it was built from are absent, and the stored column says so.
    """
    worst = 0.0
    mismatched = 0
    for row, value in zip(rows, computed):
        stored = float(row[stored_column])
        if not finite(value) or not finite(stored):
            mismatched += finite(value) != finite(stored)
            continue
        worst = max(worst, abs(value - stored))
    return worst, mismatched


def verify_spatial_check(rep):
    """Section 7.3.3 rebuilt from coordinates rather than read from a report.

    The four medians were pinned in eval/reports/r7_handover.json and nowhere
    else until spatial_check_pairs.csv was written, so this section is what
    brings the subsection inside the guarantee the rest of the package has.
    Everything here is recomputed from the stored coordinate columns: the
    wrist to marker distance, the hold distance that decides which frames are
    at the cube, the inclusion column, the interval boundaries, and the four
    medians.
    """
    rep.section('[7] Human-object spatial check, Section 7.3.3 '
                '(D-038, brief facts 4 and 5)')
    pairs_path = EVID / 'spatial_check_pairs.csv'
    json_path = EVID / 'spatial_check.json'
    if not pairs_path.exists() or not json_path.exists():
        rep.skip('Section 7.3.3 wrist to marker medians, rebuilt from '
                 'coordinates',
                 'spatial_check_pairs.csv and spatial_check.json are not in '
                 'this evidence directory, so the four medians can be '
                 'compared with the pinned report below but not rebuilt')
        return
    pairs = load_csv(pairs_path)
    data = load_json(json_path)
    stated = {(entry['part'], entry['side']): entry for entry in data['groups']}
    grouped = group_rows(pairs, ('part', 'side'))

    g = Group(rep, 'spatial_check_pairs.csv against spatial_check.json')
    g.equal('group sets match', set(grouped), set(stated))
    g.equal('every row belongs to the one recording',
            {row['recording'] for row in pairs}, {data['alias']})
    g.equal('the four published groups are present',
            set(SPATIAL_CM) <= set(stated), True)
    g.close('recorded hold radius', data['inclusion_rule']['hold_radius_cm'],
            HOLD_RADIUS_CM, TOL_CM)
    g.close('recorded physical reference',
            data['definitions']['physical_reference_cm'],
            PHYSICAL_WRIST_MARKER_CM, 0.0)
    g.done()

    def hold_point(row):
        """The point the inclusion test measures from.

        The measured wrist where the extractor returned one, the model wrist
        where it did not. The substituted column records which.
        """
        return 'model_wrist' if int(row['substituted']) else 'measured_wrist'

    near_frames = {'left': set(), 'right': set()}
    for key in sorted(grouped):
        part, side = key
        rows = sorted(grouped[key], key=lambda r: int(r['frame']))
        entry = stated[key]
        g = Group(rep, 'spatial check %s part, %s hand' % key)
        frames = [int(row['frame']) for row in rows]
        g.equal('frames unique', len(set(frames)), len(frames))
        g.equal('frames are the whole interval',
                frames, list(range(entry['first_frame'],
                                   entry['last_frame'] + 1)))
        g.equal('row count', entry['rows'], len(rows))
        g.equal('phase label', {row['phase'] for row in rows}, {entry['phase']})

        # Distances recomputed from the coordinate columns, never taken from
        # the stored columns.
        distances = [distance(row, 'model_wrist', 'marker', 100.0)
                     for row in rows]
        worst, mismatched = agrees(rows, 'distance_cm', distances)
        g.equal('stored distance column is defined exactly where its own '
                'coordinates are', mismatched, 0)
        g.check('stored distance column matches its own coordinates',
                worst <= TOL_CM, 'worst row delta %.3g cm' % worst)
        holds = [distance(row, hold_point(row), 'cube_centre', 100.0)
                 for row in rows]
        worst, mismatched = agrees(rows, 'hold_distance_cm', holds)
        g.equal('stored hold distance is defined exactly where its own '
                'coordinates are', mismatched, 0)
        g.check('stored hold distance matches its own coordinates',
                worst <= TOL_CM, 'worst row delta %.3g cm' % worst)

        # The inclusion rule, replayed on the stored per-frame states. The
        # carried and detected classifications come from the whole object
        # track and are taken as stored; everything the rule does with them is
        # recomputed here.
        rebuilt, atcube = [], []
        for row, hold, value in zip(rows, holds, distances):
            at = (int(row['carried']) == 1 and int(row['detected']) == 1
                  and finite(hold) and hold < HOLD_RADIUS_CM)
            atcube.append(at)
            rebuilt.append(at and finite(value))
        g.equal('inclusion column equals the rule replayed on the stored '
                'states', [int(x) for x in rebuilt],
                [int(row['included']) for row in rows])
        g.equal('n_included equals the included row count',
                entry['n_included'], sum(rebuilt))
        g.check('no row is excluded for the size of its distance',
                all('distance' not in row['exclusion_reason']
                    or 'not finite' in row['exclusion_reason']
                    for row in rows if not int(row['included'])))
        g.equal('every included row records no exclusion reason',
                {row['exclusion_reason'] for row in rows
                 if int(row['included'])} - {''}, set())
        g.equal('every excluded row records a reason',
                [row['frame'] for row in rows
                 if not int(row['included']) and not row['exclusion_reason']],
                [])
        near_frames[side] |= {int(row['frame'])
                              for row, at in zip(rows, atcube) if at}

        included = [value for value, keep in zip(distances, rebuilt) if keep]
        if included:
            check_stats(g, 'wrist to marker centre', included, entry)
            published = SPATIAL_CM.get(key)
            if published is not None:
                g.close('median rounds to the published %.2f cm' % published,
                        round(entry['median'], 2), published, 0.0)
                g.close('published_cm field', entry['published_cm'],
                        published, 0.0)
        else:
            g.equal('empty group states n of zero', entry['n'], 0)
            g.equal('an empty group is not one of the published medians',
                    key in SPATIAL_CM, False)
        g.done('%d row%s, whole interval, distance and hold distance against '
               'their own coordinates, inclusion rule replayed, %d included, '
               'median, p95 and maximum'
               % (len(rows), '' if len(rows) == 1 else 's', sum(rebuilt)))

    # The intervals, re-derived from the stored at-the-cube states rather than
    # read from the file. The transfer runs from the first frame on which the
    # left hand is at the cube to the last on which the right hand is.
    intervals = data['intervals']
    g = Group(rep, 'spatial check interval boundaries')
    g.equal('left hand arrives', min(near_frames['left']),
            intervals['left_hand_arrives_frame'])
    g.equal('right hand leaves', max(near_frames['right']),
            intervals['right_hand_leaves_frame'])
    span = intervals['rail_span']
    covered = sorted({int(row['frame']) for row in pairs})
    g.equal('the rows cover the rail span exactly',
            covered, list(range(span[0], span[1] + 1)))
    for part, (first, last) in (('right', (span[0],
                                           intervals['left_hand_arrives_frame'] - 1)),
                                ('handover', (intervals['left_hand_arrives_frame'],
                                              intervals['right_hand_leaves_frame'])),
                                ('left', (intervals['right_hand_leaves_frame'] + 1,
                                          span[1]))):
        g.equal('%s interval re-derived from the at-the-cube states' % part,
                intervals[part]['frames'], [first, last])
        for side in ('left', 'right'):
            g.equal('%s part, %s hand spans that interval' % (part, side),
                    (stated[(part, side)]['first_frame'],
                     stated[(part, side)]['last_frame']), (first, last))
    g.check('no hand is at the cube outside the rail span',
            all(span[0] <= frame <= span[1]
                for side in near_frames for frame in near_frames[side]))
    g.check('the right hand is never at the cube after it leaves',
            max(near_frames['right']) == intervals['right_hand_leaves_frame'])
    g.check('the left hand is never at the cube before it arrives',
            min(near_frames['left']) == intervals['left_hand_arrives_frame'])
    g.done('the transfer boundaries, the three intervals they imply, the rail '
           'span coverage, and that neither hand is at the cube outside its '
           'own intervals')

    # D-038 restricts the physical comparison to the two hand-alone medians.
    g = Group(rep, 'spatial check grading, D-038')
    for key, entry in sorted(stated.items()):
        graded = entry['graded_against_physical_reference']
        g.equal('%s part, %s hand graded flag' % key, graded,
                entry['phase'] == 'hand_alone' and key in SPATIAL_CM)
        if graded:
            delta = abs(entry['median'] - PHYSICAL_WRIST_MARKER_CM)
            g.check('%s part, %s hand median is within the %.0f cm the '
                    'chapter claims of the %.0f cm physical reference'
                    % (key[0], key[1], SPATIAL_CLAIM_CM,
                       PHYSICAL_WRIST_MARKER_CM),
                    delta <= SPATIAL_CLAIM_CM, 'delta %.2f cm' % delta)
    g.equal('the two transfer medians are not graded',
            [entry['graded_against_physical_reference']
             for key, entry in sorted(stated.items())
             if entry['phase'] == 'transfer'], [False, False])
    g.equal('exactly two medians are graded',
            sum(1 for entry in stated.values()
                if entry['graded_against_physical_reference']), 2)
    g.done('the graded flag of every group, the two transfer medians left '
           'ungraded, and both graded medians against the physical reference')

    handover = REPO / 'eval/reports/r7_handover.json'
    if handover.exists():
        parts = load_json(handover)['parts']
        g = Group(rep, 'spatial_check.json against eval/reports/r7_handover.json')
        for key, entry in sorted(stated.items()):
            if key not in SPATIAL_CM:
                continue
            block = parts[key[0]]['%s_fk_wrist_to_marker_at_cube_cm' % key[1]]
            g.equal('%s part, %s hand n' % key, entry['n'], block['n'])
            for name, other in (('median', 'median'), ('p95', 'p95'),
                                ('maximum', 'max')):
                g.close('%s part, %s hand %s rounds to the pinned value'
                        % (key[0], key[1], name),
                        round(entry[name], 2), block[other], 0.0)
        g.equal('the file records that the pinned report reproduces',
                data['reproduces_pinned_report'], True)
        g.done()
    else:
        rep.skip('spatial_check.json against its pinned report',
                 'eval/reports/r7_handover.json is absent')

    ok = bad = absent = 0
    broken = []
    for entry in data['provenance']['sources']:
        path = REPO / entry['path']
        if not path.exists():
            absent += 1
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() == entry['sha256']:
            ok += 1
        else:
            bad += 1
            broken.append(entry['path'])
    g = Group(rep, 'spatial_check.json source hashes')
    g.equal('recorded percentile definition',
            data['provenance']['percentile'],
            'numpy.percentile, linear interpolation')
    g.check('%d of %d recorded sources still hash as recorded'
            % (ok, len(data['provenance']['sources'])), bad == 0,
            'mismatched: %s' % ', '.join(broken))
    g.done()
    if absent:
        rep.skip('spatial_check.json: %d of %d recorded sources are absent'
                 % (absent, len(data['provenance']['sources'])),
                 'they are gitignored local inputs under eval/output and '
                 'v1/mediapipe/output, so a clean checkout cannot hash them')

    rep.skip('spatial check carried and detected states',
             'both are per-frame classifications of the whole object track: '
             'carried needs the manipulation phase of the inspection report '
             'and the rest clusters, detected needs the cleaned track; they '
             'are stored per row and the inclusion rule is replayed on them, '
             'but they are not rebuilt here')
    rep.skip('spatial check rail span endpoints',
             'the slide detector of eval/gt/eval_rail_scenario.segment runs '
             'over the whole marker track; the transfer boundaries inside the '
             'span are re-derived above, the span itself is taken as pinned')
    rep.skip('spatial check coordinate columns',
             'the model wrist comes from the solved angles, the measured '
             'shoulder and the calibrated lengths, the measured wrist from the '
             'filtered landmark CSV, and the marker centre and cube centre '
             'from the cleaned object track and the scene calibration; all '
             'those inputs are gitignored, so the coordinates are verified '
             'only for internal consistency')


# --------------------------------------------------------------------------
# 8. provenance and published values
# --------------------------------------------------------------------------
def verify_provenance(rep):
    rep.section('[8] Provenance of the recorded inputs')
    for name in ('provenance.json', 'object_provenance.json', 'bare_model.json'):
        data = load_json(EVID / name)
        g = Group(rep, '%s percentile definition' % name)
        g.equal('recorded definition',
                data['percentile'], 'numpy.percentile, linear interpolation')
        g.done()
        ok = bad = absent = 0
        broken = []
        for entry in data['sources']:
            path = REPO / entry['path']
            if not path.exists():
                absent += 1
                continue
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest == entry['sha256']:
                ok += 1
            else:
                bad += 1
                broken.append(entry['path'])
        g = Group(rep, '%s source hashes' % name)
        g.check('%d of %d recorded sources still hash as recorded'
                % (ok, len(data['sources'])), bad == 0,
                'mismatched: %s' % ', '.join(broken))
        g.done()
        if absent:
            rep.skip('%s: %d of %d recorded sources are absent'
                     % (name, absent, len(data['sources'])),
                     'they are gitignored local inputs under eval/output, so a '
                     'clean checkout cannot hash them')

    rep.section('[9] Published values, recomputed from the pairs')
    human = load_json(EVID / 'human.json')
    bare = load_json(EVID / 'bare_model.json')['recordings']

    def wrist(alias, side, scope, key='vs_raw_measured'):
        return bare[alias]['joints'][side + '_wrist'][scope][key]

    subset = 'section_7_3_frame_set'
    wide = 'recording_wide_accepted'
    g = Group(rep, 'D-041 bare model at both scopes')
    for side, median, n in (('right', 0.83, 650), ('left', 2.34, 589)):
        g.close('capture subset %s median' % side,
                round(wrist('r7', side, subset)['median'], 2), median, 0.0)
        g.equal('capture subset %s n' % side, wrist('r7', side, subset)['n'], n)
    for side, median, n in (('right', 1.03, 1156), ('left', 1.03, 1095)):
        g.close('recording wide %s median' % side,
                round(wrist('r7', side, wide)['median'], 2), median, 0.0)
        g.equal('recording wide %s n' % side, wrist('r7', side, wide)['n'], n)
    for scope, share in ((subset, 55), (wide, 41)):
        block = bare['r7']['joints']['left_wrist'][scope]
        g.equal('left held twist share %s' % scope,
                round(100 * block['twist_held_frames'] / block['n']), share)
    g.done()

    g = Group(rep, 'D-040 evaluation reference convention')
    for side, raw, filt in (('right', 0.83, 0.73), ('left', 2.34, 2.30)):
        g.close('%s against the raw measured wrist' % side,
                round(wrist('r7', side, subset)['median'], 2), raw, 0.0)
        g.close('%s against the filtered measured wrist' % side,
                round(wrist('r7', side, subset, 'vs_filtered_measured')['median'], 2),
                filt, 0.0)
    g.done()

    g = Group(rep, 'D-042 rail recording bare model value')
    g.close('rail right wrist median on the capture subset',
            round(wrist('r6b', 'right', subset)['median'], 2), 6.78, 0.0)
    for scope in (subset, wide):
        block = bare['r6b']['joints']['right_wrist'][scope]
        g.equal('rail right wrist twist held on every accepted frame %s' % scope,
                block['twist_held_frames'], block['n'])
        g.equal('rail right wrist root constrained on every accepted frame %s'
                % scope, block['output_tags']['root'], {'2': block['n']})
        g.equal('rail right wrist has no measured twist frame %s' % scope,
                block['twist_measured_frames'], 0)
    medians = [wrist('r7', side, scope, 'vs_raw_measured_twist_' + state)['median']
               for side in ('right', 'left') for scope in (subset, wide)
               for state in ('measured',)
               if wrist('r7', side, scope,
                        'vs_raw_measured_twist_measured')['n']]
    held = [wrist('r7', side, scope, 'vs_raw_measured_twist_held')['median']
            for side in ('right', 'left') for scope in (subset, wide)
            if wrist('r7', side, scope, 'vs_raw_measured_twist_held')['n']]
    g.check('twist measured medians lie in the stated 0.6 to 0.9 cm span',
            0.55 <= min(medians) and max(medians) < 0.95,
            'span %.2f to %.2f cm' % (min(medians), max(medians)))
    g.check('twist held medians lie in the stated 2.3 to 2.8 cm span',
            2.25 <= min(held) and max(held) < 2.85,
            'span %.2f to %.2f cm' % (min(held), max(held)))
    g.done()

    g = Group(rep, 'Table 7.4 rendered rig medians (D-031)')
    for side, median in (('right', 5.71), ('left', 6.87)):
        g.close('handover %s wrist median' % side,
                round(human['r7']['joints'][side + '_wrist']['median'], 2),
                median, 0.0)
    g.done()

    # Section 7.3.3. The chapter prints these four from spatial_check.json,
    # which section [7] rebuilt from the coordinate pairs; the pinned report
    # is checked beside it rather than in its place.
    spatial = EVID / 'spatial_check.json'
    if spatial.exists():
        stated = {(entry['part'], entry['side']): entry
                  for entry in load_json(spatial)['groups']}
        g = Group(rep, 'Section 7.3.3 wrist to marker medians (D-038, brief '
                       'fact 5), from the rebuilt evidence')
        for key, median in sorted(SPATIAL_CM.items()):
            g.close('%s hand in the %s interval' % (key[1], key[0]),
                    round(stated[key]['median'], 2), median, 0.0)
        g.done()
    else:
        rep.skip('Section 7.3.3 wrist to marker medians from the rebuilt '
                 'evidence', 'spatial_check.json is absent')
    handover = REPO / 'eval/reports/r7_handover.json'
    if handover.exists():
        parts = load_json(handover)['parts']
        g = Group(rep, 'Section 7.3.3 wrist to marker medians, against the '
                       'pinned report')
        for key, median in sorted(SPATIAL_CM.items()):
            block = '%s_fk_wrist_to_marker_at_cube_cm' % key[1]
            g.close('%s hand in the %s interval' % (key[1], key[0]),
                    parts[key[0]][block]['median'], median, 0.0)
        g.done()
    else:
        rep.skip('Section 7.3.3 wrist to marker medians against the pinned '
                 'report', 'eval/reports/r7_handover.json is absent')
    rep.skip('the approximately 16 cm physical wrist to marker reference',
             'it is an author tape measurement (brief fact 4), not a computed '
             'quantity')


def main():
    rep = Report()
    print('Chapter 7 restructured evidence: standalone verification')
    print('Repository root: %s' % REPO)
    print('Evidence:        %s' % EVID.relative_to(REPO))
    print('Inputs:          the committed coordinate pairs and JSON evidence, '
          'plus committed')
    print('                 pinned reports and capture logs where they exist. '
          'No gitignored')
    print('                 recording is read, so a clean checkout gives the '
          'same result')
    print('                 with more SKIP lines.')
    print('Tolerances:      %.0e cm and %.0e m on re-derived arithmetic, %.0e '
          'on dimensionless' % (TOL_CM, TOL_M, TOL_UNIT))
    print('                 quantities. These are numerical-noise allowances '
          'only. Where the')
    print('                 evidence stores two decimals, a %.2f cm display '
          'allowance is used' % ROUND_CM)
    print('                 instead and is named on the line that uses it.')
    print('Statistics:      median, p95 and maximum are recomputed here in '
          'plain Python from')
    print('                 distances recomputed from the coordinate columns. '
          'Percentiles use')
    print('                 linear interpolation between ordered observations '
          '(Section 7.1).')

    if not EVID.is_dir():
        print('\nFAIL  evidence directory %s is missing' % EVID)
        return 1

    human, human_groups = verify_human(rep)
    verify_synthetic(rep)
    verify_bare_model(rep, human, human_groups)
    verify_object(rep)
    verify_natural(rep)
    verify_loop_detection(rep)
    verify_spatial_check(rep)
    verify_provenance(rep)

    print('')
    print('Summary')
    print('-------')
    print('PASS %d' % rep.passed)
    print('SKIP %d' % rep.skipped)
    print('FAIL %d' % rep.failed)
    print('')
    print('Not verifiable from the committed evidence (%d):' % rep.skipped)
    for what, reason in rep.skips:
        emit('  - %s' % what, indent=0)
        emit(reason, indent=8)
    if rep.failures:
        print('')
        print('Failures (%d):' % rep.failed)
        for failure in rep.failures:
            emit('  - %s' % failure, indent=8)
        return 1
    print('')
    print('Every published statistic reachable from the committed coordinate '
          'pairs was')
    print('recomputed independently and agrees with the evidence files.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
