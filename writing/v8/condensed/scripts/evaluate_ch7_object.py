#!/usr/bin/env python3
"""Pin the Section 7.2 object segment lengths without modifying experiment inputs.

Decision D-035 supplies the physical reference: the ArUco marker centre is the
measured point in both recordings, the three physical segment separations are
25.5, 3.5 and 37.5 cm, and the measurement resolution is 1 mm. The waypoint
frames are identified independently per recording from that recording's own
marker-centre motion. The previously stored route corners
(eval/reports/*_waypoints.json) and the fitted rail line are never used to place
a waypoint; the fitted line appears only in the separate scatter statistics.

Conventions follow scripts/evaluate_ch7_restructured.py: the emitted coordinate
pairs are the reproducible numerical record, every input is hashed, and no
exclusion rule depends on the size of any resulting error.

Run from the repository root:
    MPLCONFIGDIR=/tmp/ch7_restructured_mpl XDG_CACHE_HOME=/tmp/ch7_restructured_cache \
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/evaluate_ch7_object.py
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[4]
OUT = REPO / 'writing/v8/condensed/audit_evidence/ch7_restructured'
for folder in ('eval/common', 'eval/offset', 'v1/kinematics'):
    sys.path.insert(0, str(REPO / folder))

import paths
from carry import LeveledWorld

# Physical reference (D-035; REVISION_2026-09-11_BRIEF.md fact 2 records the
# same three tape lengths). Same values for both recordings: the author states
# the physical setup is identical.
PHYSICAL_CM = {'W1_W2': 25.5, 'W2_W3': 3.5, 'W3_W4': 37.5}
RESOLUTION_MM = 1.0

# Detection parameters. Fixed before any length was computed; the sensitivity
# block below reports what happens when each one is perturbed.
HALF_WINDOW = 7        # valid samples each side of the velocity estimate
ONSET_FRAC = 0.05      # fraction of a transition's peak axis velocity
BAND_M = 0.005         # departure band of the phase-boundary refinement, metres
SUSTAIN = 5            # valid samples a departure must persist to count
LEVEL_SAMPLES = 15     # samples used for a local pre-transition level

SOURCES = set()


def source(path):
    path = Path(path)
    SOURCES.add(path.resolve())
    return path


def read_json(path):
    return json.loads(source(path).read_text())


def save_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def stats_cm(values):
    values = np.asarray(values, float)
    assert values.size and np.isfinite(values).all()
    return dict(n=int(values.size), median=float(np.median(values)),
                p95=float(np.percentile(values, 95, method='linear')),
                maximum=float(values.max()))


def load_track(stem):
    """Marker-centre track in the gravity-levelled desk world, metres.

    The stored unity_p* columns are the object marker pose translation, i.e.
    the ArUco marker centre on the cube face, in the desk-marker world. The
    same LeveledWorld rotation that eval/gt/eval_rail_scenario.py applies (the
    calibrated gravity up axis taken to +y) is reused so positions are directly
    comparable with the existing reports. That rotation, and the permutation
    that produced unity_p* from the stored tx/ty/tz, are isometries, so every
    segment LENGTH below is invariant to the choice of frame; only the axis
    decompositions and the scatter components depend on it.
    """
    df = pd.read_csv(source(paths.object_world_filtered(stem)))
    assert df.frame.is_unique
    calib = read_json(paths.calib_for(stem))
    world = LeveledWorld(calib)
    unity = df[['unity_px', 'unity_py', 'unity_pz']].apply(
        pd.to_numeric, errors='coerce').to_numpy(float)
    finite = np.isfinite(unity).all(axis=1)
    detected = df['detected'].to_numpy() == 1
    filled = df['filled'].to_numpy() == 1
    accepted = finite & detected & ~filled
    raw = df[['tx', 'ty', 'tz']].to_numpy(float)
    return dict(
        stem=stem, alias=paths.ALIAS[stem], frame=df.frame.to_numpy(int),
        time_s=df.time_s.to_numpy(float), accepted=accepted,
        xyz=world.level(unity[accepted]), raw=raw[accepted],
        f=df.frame.to_numpy(int)[accepted], t=df.time_s.to_numpy(float)[accepted],
        excluded=dict(
            frames_total=int(len(df)),
            accepted=int(accepted.sum()),
            not_detected=int((~detected).sum()),
            filled=int(filled.sum()),
            non_finite_position=int((~finite).sum()),
            excluded_frames=[int(x) for x in df.frame.to_numpy(int)[~accepted]]),
        gravity_up_unity=[float(v) for v in world.g],
        calibration=str(Path(paths.calib_for(stem)).relative_to(REPO)),
        track=str(Path(paths.object_world_filtered(stem)).relative_to(REPO)))


def velocity(P, t, h):
    n = len(P)
    lo = np.clip(np.arange(n) - h, 0, n - 1)
    hi = np.clip(np.arange(n) + h, 0, n - 1)
    return (P[hi] - P[lo]) / (t[hi] - t[lo])[:, None]


def first_departure(P, band, sustain):
    """Last index of the opening run that stays within band of the first sample."""
    far = np.linalg.norm(P - P[0], axis=1) > band
    run = 0
    for k, flag in enumerate(far):
        run = run + 1 if flag else 0
        if run >= sustain:
            return k - run + 1 - 1
    return len(P) - 1


def transition(v_axis, q_axis, lo, hi, frac, band, level_samples):
    """Locate one motion transition on one axis inside the index span [lo, hi].

    Returns the coarse velocity bracket, the local pre-transition level, the
    refined boundary index (the last sample before the motion begins) and the
    index at which the axis has completed the move. Nothing here uses a
    physical length.
    """
    span = v_axis[lo:hi + 1]
    peak = float(span.max())
    half = lo + int(np.flatnonzero(span >= 0.5 * peak)[0])
    half_last = lo + int(np.flatnonzero(span >= 0.5 * peak)[-1])
    low = np.flatnonzero(v_axis[lo:half + 1] <= frac * peak)
    coarse = lo + int(low[-1]) if low.size else lo
    a = max(lo, coarse - level_samples + 1)
    level = float(np.median(q_axis[a:coarse + 1]))
    below = np.flatnonzero(q_axis[lo:half + 1] <= level + band)
    boundary = lo + int(below[-1]) if below.size else coarse
    tail = np.flatnonzero(v_axis[half_last:hi + 1] <= frac * peak)
    done = half_last + int(tail[0]) if tail.size else hi
    return dict(peak=peak, half=half, half_last=half_last, coarse=coarse,
                level=level, boundary=boundary, done=done)


def detect(track, half_window=HALF_WINDOW, frac=ONSET_FRAC, band=BAND_M,
           sustain=SUSTAIN, level_samples=LEVEL_SAMPLES):
    """Identify W1 to W4 from the recording's own marker-centre motion.

    W1  last sample of the opening run that stays within band of the first
        accepted sample, i.e. the last sample before the first translation.
    W2  last sample before the vertical rise begins.
    W3  last sample before the leftward translation begins.
    W4  first sample after the last leftward motion ends; the reported
        position is the mean of that sample to the end of the track.
    """
    P, t = track['xyz'], track['t']
    n = len(P)
    V = velocity(P, t, half_window)
    i1 = first_departure(P, band, sustain)
    rise = transition(V[:, 1], P[:, 1], i1, n - 1, frac, band, level_samples)
    slide = transition(V[:, 0], P[:, 0], rise['done'], n - 1, frac, band,
                       level_samples)
    i2, i3, i4 = rise['boundary'], slide['boundary'], slide['done']
    assert i1 < i2 < i3 < i4 < n
    return dict(index=dict(W1=i1, W2=i2, W3=i3, W4=i4), rise=rise, slide=slide,
                velocity_peaks=dict(vertical=rise['peak'], lateral=slide['peak']))


def waypoints(track, det):
    """Reconstructed waypoint positions and the samples behind each one."""
    P, f = track['xyz'], track['f']
    i = det['index']
    spans = {'W1': (0, i['W1']), 'W2': (i['W2'], i['W2']),
             'W3': (i['W3'], i['W3']), 'W4': (i['W4'], len(P) - 1)}
    out = {}
    for name, (a, b) in spans.items():
        block = P[a:b + 1]
        out[name] = dict(
            first_frame=int(f[a]), last_frame=int(f[b]), n_samples=int(b - a + 1),
            estimator=('mean of accepted samples' if b > a
                       else 'single transition sample'),
            position_m=[float(v) for v in block.mean(axis=0)],
            spread_mm=[float(v) * 1000 for v in np.ptp(block, axis=0)],
            index=(a, b))
    return out


def lengths(points):
    rows = []
    for a, b in (('W1', 'W2'), ('W2', 'W3'), ('W3', 'W4')):
        pa = np.asarray(points[a], float)
        pb = np.asarray(points[b], float)
        delta = pb - pa
        phys = PHYSICAL_CM[a + '_' + b]
        rec = float(np.linalg.norm(delta)) * 100
        abs_err = abs(rec - phys)
        rows.append(dict(
            segment=a + ' to ' + b, physical_cm=phys, reconstructed_cm=rec,
            absolute_error_cm=abs_err, relative_error_pct=100 * abs_err / phys,
            delta_m=[float(v) for v in delta],
            dominant_axis='xyz'[int(np.argmax(np.abs(delta)))],
            dominant_fraction=float(np.abs(delta).max() / np.abs(delta).sum())))
    return rows


def fit_line(P):
    """Orthogonal least squares (equations 7.2 to 7.4)."""
    c = P.mean(axis=0)
    _, S, Vt = np.linalg.svd(P - c, full_matrices=False)
    u = Vt[0]
    resid = (P - c) - np.outer((P - c) @ u, u)
    return c, u, resid, S / np.sqrt(len(P))


def scatter(track, det, first, last):
    a, b = det['index'][first], det['index'][last]
    P = track['xyz'][a:b + 1]
    if len(P) < 3:
        return None
    c, u, resid, sigma = fit_line(P)
    d = np.linalg.norm(resid, axis=1) * 100
    return dict(
        span_frames=[int(track['f'][a]), int(track['f'][b])], **stats_cm(d),
        pca_sigma_cm=[float(s) * 100 for s in sigma],
        direction=[float(v) for v in (u if u[0] >= 0 else -u)],
        tilt_from_horizontal_deg=float(np.degrees(np.arcsin(abs(u[1])))),
        centroid_m=[float(v) for v in c],
        vertical_component_median_cm=float(np.median(np.abs(resid[:, 1])) * 100),
        note='Descriptive scatter about the trajectory own fitted line; not a '
             'physical accuracy measure. The component split and the tilt '
             'depend on the levelled frame, the distances d_i do not.')


def phase_check(track, det, points, segs):
    """Confirm each detected boundary sits in the intended task phase."""
    P = track['xyz']
    i = det['index']
    f = track['f']
    y = [points[w]['position_m'][1] for w in ('W1', 'W2', 'W3', 'W4')]
    checks = {
        'W1': dict(
            rule='Last accepted sample of the opening run that stays within '
                 '%.0f mm of the first accepted sample for %d consecutive '
                 'samples.' % (BAND_M * 1000, SUSTAIN),
            evidence=dict(
                first_frame_of_track=int(f[0]), boundary_frame=int(f[i['W1']]),
                opening_run_spread_mm=points['W1']['spread_mm'],
                height_above_final_level_cm=float((y[0] - y[3]) * 100)),
            passes=bool(i['W1'] < i['W2'] and
                        max(points['W1']['spread_mm']) <= BAND_M * 1000 * 3)),
        'W2': dict(
            rule='Last accepted sample whose levelled height is within %.0f mm '
                 'of the local pre-rise level, searched back from the half-peak '
                 'of the vertical velocity.' % (BAND_M * 1000),
            evidence=dict(
                pre_rise_level_m=det['rise']['level'],
                vertical_velocity_peak_m_s=det['rise']['peak'],
                half_peak_frame=int(f[det['rise']['half']]),
                coarse_onset_frame=int(f[det['rise']['coarse']]),
                boundary_frame=int(f[i['W2']]),
                boundary_at_half_peak=bool(i['W2'] == det['rise']['half']),
                height_above_pre_rise_level_mm=float(
                    (P[i['W2'], 1] - det['rise']['level']) * 1000),
                rise_completed_frame=int(f[det['rise']['done']]),
                height_change_W2_to_W3_cm=float((y[2] - y[1]) * 100),
                height_change_W1_to_W2_cm=float((y[1] - y[0]) * 100),
                height_change_W3_to_W4_cm=float((y[3] - y[2]) * 100)),
            passes=bool(abs(y[2] - y[1]) > abs(y[1] - y[0]) and
                        abs(y[2] - y[1]) > abs(y[3] - y[2]) and
                        segs[1]['dominant_axis'] == 'y')),
        'W3': dict(
            rule='Last accepted sample whose lateral coordinate is within %.0f '
                 'mm of the local pre-slide level, searched back from the '
                 'half-peak of the lateral velocity after the rise completes.'
                 % (BAND_M * 1000),
            evidence=dict(
                pre_slide_level_m=det['slide']['level'],
                lateral_velocity_peak_m_s=det['slide']['peak'],
                half_peak_frame=int(f[det['slide']['half']]),
                coarse_onset_frame=int(f[det['slide']['coarse']]),
                boundary_frame=int(f[i['W3']]),
                boundary_at_half_peak=bool(i['W3'] == det['slide']['half']),
                lateral_beyond_pre_slide_level_mm=float(
                    (P[i['W3'], 0] - det['slide']['level']) * 1000),
                rise_completed_before_W3=bool(det['rise']['done'] <= i['W3'])),
            passes=bool(det['rise']['done'] <= i['W3'] and
                        segs[2]['dominant_axis'] == 'x')),
        'W4': dict(
            rule='First accepted sample after the last lateral half-peak at '
                 'which the lateral velocity falls to %.0f%% of its peak; the '
                 'position is the mean of that sample to the end of the track.'
                 % (ONSET_FRAC * 100),
            evidence=dict(
                last_half_peak_frame=int(f[det['slide']['half_last']]),
                interval=[int(f[i['W4']]), int(f[-1])],
                n_samples=points['W4']['n_samples'],
                interval_spread_mm=points['W4']['spread_mm'],
                lateral_travel_W3_to_W4_cm=float(
                    (points['W4']['position_m'][0] -
                     points['W3']['position_m'][0]) * 100)),
            passes=bool(i['W4'] > i['W3'] and
                        points['W4']['position_m'][0] >
                        points['W3']['position_m'][0])),
    }
    checks['segment_axis_dominance'] = {
        s['segment']: dict(dominant_axis=s['dominant_axis'],
                           fraction=s['dominant_fraction'],
                           expected=exp)
        for s, exp in zip(segs, ('z', 'y', 'x'))}
    checks['expected_pattern'] = ('depth for W1 to W2, vertical for W2 to W3, '
                                 'lateral for W3 to W4')
    return checks


def sensitivity(track):
    """Detector-selection uncertainty, reported as required by D-035.

    Three independent perturbations: the detection parameters, a shift of each
    identified boundary by a few frames, and replacing the two single-frame
    transition samples by a local mean. Nothing here is used to choose the
    reported values.
    """
    base = detect(track)
    base_pts = waypoints(track, base)
    base_L = [r['reconstructed_cm'] for r in
              lengths({k: v['position_m'] for k, v in base_pts.items()})]
    P, n = track['xyz'], len(track['xyz'])
    rows = []

    def record(kind, label, pts):
        L = lengths(pts)
        rows.append(dict(
            kind=kind, label=label,
            lengths_cm=[r['reconstructed_cm'] for r in L],
            phase_ok=bool([r['dominant_axis'] for r in L] == ['z', 'y', 'x'])))

    for h in (5, 7, 10):
        for frac in (0.02, 0.05, 0.10):
            for band in (0.002, 0.005, 0.010, 0.020):
                try:
                    d = detect(track, half_window=h, frac=frac, band=band)
                    p = waypoints(track, d)
                except (AssertionError, IndexError):
                    rows.append(dict(kind='parameters',
                                     label='h=%d frac=%.2f band=%.0fmm' %
                                           (h, frac, band * 1000),
                                     lengths_cm=None, phase_ok=False))
                    continue
                record('parameters', 'h=%d frac=%.2f band=%.0fmm' %
                       (h, frac, band * 1000),
                       {k: v['position_m'] for k, v in p.items()})
    for shift in (-10, -5, -2, 2, 5, 10):
        for name in ('W1', 'W2', 'W3', 'W4'):
            pts = {k: v['position_m'] for k, v in base_pts.items()}
            a, b = base_pts[name]['index']
            a2, b2 = min(max(a + shift, 0), n - 1), min(max(b + shift, 0), n - 1)
            if a2 > b2:
                continue
            pts[name] = [float(v) for v in P[a2:b2 + 1].mean(axis=0)]
            record('boundary shift %d frames' % abs(shift),
                   '%s %+d frames' % (name, shift), pts)
    for w in (3, 7, 15):
        pts = {k: v['position_m'] for k, v in base_pts.items()}
        for name in ('W2', 'W3'):
            a = base_pts[name]['index'][0]
            pts[name] = [float(v) for v in
                         P[max(0, a - w):min(n, a + w + 1)].mean(axis=0)]
        record('local mean at W2 and W3', 'plus or minus %d frames' % w, pts)

    def block(selected, failed):
        arr = np.asarray(selected, float)
        return dict(n_variants=int(len(selected)), n_excluded=int(failed),
                    minimum_cm=[float(v) for v in arr.min(axis=0)],
                    maximum_cm=[float(v) for v in arr.max(axis=0)],
                    spread_cm=[float(v) for v in np.ptp(arr, axis=0)],
                    median_cm=[float(v) for v in np.median(arr, axis=0)])

    summary = {}
    kinds = ['parameters', 'boundary shift 2 frames', 'boundary shift 5 frames',
             'boundary shift 10 frames', 'local mean at W2 and W3']
    for kind in kinds:
        group = [r for r in rows if r['kind'] == kind]
        good = [r['lengths_cm'] for r in group
                if r['lengths_cm'] is not None and r['phase_ok']]
        summary[kind] = block(good, len(group) - len(good))
    good = [r['lengths_cm'] for r in rows
            if r['lengths_cm'] is not None and r['phase_ok']]
    summary['combined'] = dict(reported_cm=base_L,
                               **block(good, len(rows) - len(good)))
    few = [r['lengths_cm'] for r in rows
           if r['lengths_cm'] is not None and r['phase_ok']
           and r['kind'] in ('parameters', 'boundary shift 2 frames',
                             'boundary shift 5 frames')]
    summary['rule_plus_few_frames'] = dict(reported_cm=base_L, **block(few, 0))
    return dict(
        segments=['W1 to W2', 'W2 to W3', 'W3 to W4'],
        exclusion='A variant is excluded from a summary only when its own '
                  'segment axis pattern is no longer depth, vertical, lateral, '
                  'that is when the perturbed detector no longer identifies '
                  'the three task phases. No variant is excluded because of '
                  'the size of its error.',
        summary=summary, variants=rows)


def invariance_check(track, det, points):
    """Lengths are unchanged if the stored tx/ty/tz are used instead."""
    raw, i = track['raw'], det['index']
    spans = {'W1': (0, i['W1']), 'W2': (i['W2'], i['W2']),
             'W3': (i['W3'], i['W3']), 'W4': (i['W4'], len(raw) - 1)}
    q = {k: raw[a:b + 1].mean(axis=0) for k, (a, b) in spans.items()}
    out = {}
    for a, b in (('W1', 'W2'), ('W2', 'W3'), ('W3', 'W4')):
        levelled = float(np.linalg.norm(
            np.asarray(points[b]['position_m']) -
            np.asarray(points[a]['position_m']))) * 100
        stored = float(np.linalg.norm(q[b] - q[a])) * 100
        out[a + ' to ' + b] = dict(levelled_cm=levelled, stored_frame_cm=stored,
                                   difference_cm=abs(levelled - stored))
    assert max(v['difference_cm'] for v in out.values()) < 1e-9
    return out


def caveats(track, det, points, segs, sens):
    """Everything the prose has to disclose beside these numbers."""
    P, f = track['xyz'], track['f']
    i = det['index']
    band = sens['summary']['rule_plus_few_frames']
    step = np.linalg.norm(np.diff(P[i['W4']:], axis=0), axis=1)
    worst = int(np.argmax(step))
    out = []
    out.append(dict(
        item='detector-selection band',
        text='Reported lengths carry the detector-selection band below: the '
             'spread over the detection parameters and over boundary shifts '
             'of two and five accepted samples, with variants that no longer '
             'reproduce the depth, vertical, lateral phase pattern excluded.',
        segments={s['segment']: dict(reported_cm=s['reconstructed_cm'],
                                     minimum_cm=band['minimum_cm'][k],
                                     maximum_cm=band['maximum_cm'][k])
                  for k, s in enumerate(segs)}))
    out.append(dict(
        item='single-sample transition waypoints',
        text='W2 and W3 are single accepted samples, as the waypoint '
             'definitions require. Each therefore carries the instantaneous '
             'depth error of that one sample rather than an averaged value.',
        local_depth_spread_mm=dict(
            W2=float(np.ptp(P[max(0, i['W2'] - 7):i['W2'] + 8, 2]) * 1000),
            W3=float(np.ptp(P[max(0, i['W3'] - 7):i['W3'] + 8, 2]) * 1000))))
    out.append(dict(
        item='W1 and W4 averaging intervals',
        text='W1 and W4 are means over the opening and closing intervals. '
             'The largest single-sample step inside the W4 interval is given '
             'below; a large value means the closing interval is not a single '
             'settled cluster.',
        W1_spread_mm=points['W1']['spread_mm'],
        W4_spread_mm=points['W4']['spread_mm'],
        W4_largest_step_mm=float(step[worst] * 1000),
        W4_largest_step_between_frames=[int(f[i['W4'] + worst]),
                                        int(f[i['W4'] + worst + 1])]))
    out.append(dict(
        item='boundary resolved only to the velocity half-peak',
        text='Where the flag is true the departure band does not separate the '
             'boundary from the half-peak of that axis velocity, so the '
             'reported sample is the latest the search allows and the true '
             'boundary lies at or before it.',
        W2=bool(i['W2'] == det['rise']['half']),
        W3=bool(i['W3'] == det['slide']['half'])))
    out.append(dict(
        item='frame dependence',
        text='Segment lengths are invariant under the levelling rotation and '
             'the stored axis permutation, verified in rigid_invariance. The '
             'fitted-line scatter components, the line tilt and the axis '
             'dominance used for the phase checks are properties of the '
             'levelled frame and are not invariant.'))
    out.append(dict(
        item='scatter is not accuracy',
        text='The fitted-line distances describe how the reconstructed samples '
             'lie about a line fitted to those same samples. They are a '
             'within-recording comparison and are reported separately from the '
             'physical length errors.'))
    return out


def evaluate(stem):
    track = load_track(stem)
    det = detect(track)
    points = waypoints(track, det)
    segs = lengths({k: v['position_m'] for k, v in points.items()})
    rows = []
    for name, wp in points.items():
        a, b = wp['index']
        for k in range(a, b + 1):
            rows.append(dict(recording=track['alias'], waypoint=name,
                             frame=int(track['f'][k]), time_s=float(track['t'][k]),
                             x_m=float(track['xyz'][k, 0]),
                             y_m=float(track['xyz'][k, 1]),
                             z_m=float(track['xyz'][k, 2])))
    sens = sensitivity(track)
    result = dict(
        stem=stem, alias=track['alias'],
        track=track['track'], calibration=track['calibration'],
        frame='gravity-levelled desk world (x, y up, z away from the camera), '
              'metres; LeveledWorld rotation of eval/offset/carry.py, the same '
              'transform eval/gt/eval_rail_scenario.py applies',
        gravity_up_unity=track['gravity_up_unity'],
        measured_point='ArUco object marker centre (the unity_p* marker pose '
                       'translation), not the cube centre and not an edge',
        samples=track['excluded'],
        waypoints={k: {kk: vv for kk, vv in v.items() if kk != 'index'}
                   for k, v in points.items()},
        segments=segs,
        phase_confirmation=phase_check(track, det, points, segs),
        rigid_invariance=invariance_check(track, det, points),
        scatter=dict(
            rail_W3_to_W4=scatter(track, det, 'W3', 'W4'),
            depth_push_W1_to_W2=scatter(track, det, 'W1', 'W2'),
            rise_W2_to_W3=scatter(track, det, 'W2', 'W3')),
        sensitivity=sens,
        caveats=caveats(track, det, points, segs, sens))
    return result, rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rule = dict(
        decision='D-035',
        physical_reference_cm=PHYSICAL_CM,
        physical_resolution_mm=RESOLUTION_MM,
        physical_reference_note='Tape measurement supplied by the author; the '
                                'same three separations apply to both '
                                'recordings because the physical setup is '
                                'identical. Never called ground truth.',
        waypoint_definitions=dict(
            W1='marker-centre position before the first translation begins',
            W2='marker-centre position at the end of the first translation, '
               'the last sample before the vertical rise begins',
            W3='marker-centre position at the end of the vertical rise, the '
               'last sample before the leftward translation begins',
            W4='final marker-centre position after the leftward translation'),
        sample_acceptance='detected = 1, filled = 0, finite unity_p*; no '
                          'exclusion depends on the size of any error',
        local_motion_only='Boundaries come from the recording own marker-centre '
                          'motion. The stored waypoint reports and the fitted '
                          'rail line are not used to place any waypoint, and no '
                          'parameter was adjusted to improve agreement with the '
                          'physical lengths.',
        estimator=dict(
            velocity='centred difference over ' + str(HALF_WINDOW) +
                     ' accepted samples each side, per axis, metres per second',
            coarse_bracket='half of the transition peak axis velocity',
            coarse_onset='last sample at or below %.0f%% of that peak'
                         % (ONSET_FRAC * 100),
            local_level='median of the axis coordinate over the %d samples '
                        'ending at the coarse onset' % LEVEL_SAMPLES,
            boundary='last sample at or below the local level plus %.0f mm'
                     % (BAND_M * 1000),
            W1='last sample of the opening run that stays within %.0f mm of '
               'the first accepted sample for %d consecutive samples; the '
               'position is the mean of that opening run'
               % (BAND_M * 1000, SUSTAIN),
            W4='first sample after the last lateral half-peak at which the '
               'lateral velocity falls to %.0f%% of its peak; the position is '
               'the mean of that sample to the end of the track'
               % (ONSET_FRAC * 100),
            W2_W3='single transition samples, as the waypoint definitions '
                  'require; no dwell is assumed at either'),
        parameters=dict(half_window_samples=HALF_WINDOW, onset_fraction=ONSET_FRAC,
                        departure_band_m=BAND_M, sustain_samples=SUSTAIN,
                        level_samples=LEVEL_SAMPLES),
        equations='7.1 for the lengths and errors, 7.2 to 7.4 for the fitted '
                  'line scatter, as written in CH7_RESTRUCTURED.txt',
        frame_note='Segment lengths are invariant under the levelling rotation '
                   'and under the stored permutation, so a rigid-frame '
                   'ambiguity cannot change them; this is verified numerically '
                   'in rigid_invariance. The scatter components, the line tilt '
                   'and the axis-dominance phase checks are frame dependent.')
    payload = dict(decision='D-035', detection_rule=rule, recordings={})
    pairs = []
    for stem in (paths.R6B_STEM, paths.R7_STEM):
        result, rows = evaluate(stem)
        payload['recordings'][result['alias']] = result
        pairs.extend(rows)
        print('PASS: %s waypoints %s' % (
            result['alias'],
            {k: (v['first_frame'], v['last_frame'])
             for k, v in result['waypoints'].items()}), flush=True)
        for seg in result['segments']:
            print('   %s  physical %.1f  reconstructed %.2f  absolute %.2f  '
                  'relative %.2f%%' % (seg['segment'], seg['physical_cm'],
                                       seg['reconstructed_cm'],
                                       seg['absolute_error_cm'],
                                       seg['relative_error_pct']), flush=True)
    pd.DataFrame(pairs).to_csv(OUT / 'object_pairs.csv', index=False)
    save_json('object.json', payload)

    source(REPO / 'eval/common/paths.py')
    source(REPO / 'eval/offset/carry.py')
    source(REPO / 'eval/gt/eval_rail_scenario.py')
    source(REPO / 'v1/kinematics/root_frame.py')
    source(__file__)
    save_json('object_provenance.json', dict(
        numpy=np.__version__, pandas=pd.__version__,
        percentile='numpy.percentile, linear interpolation',
        sources=[dict(path=str(p.relative_to(REPO)),
                      sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                 for p in sorted(SOURCES)]))
    print('PASS: Chapter 7 object evidence saved to', OUT)


if __name__ == '__main__':
    main()
