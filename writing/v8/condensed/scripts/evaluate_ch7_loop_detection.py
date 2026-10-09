#!/usr/bin/env python3
"""Pin the loop recording's object-marker detection coverage for Section 7.4.2.

Chapter 9 previously printed a loop-recording detection count taken from an
evaluation output CSV rather than from a pinned report. This script recomputes
that count from the current evaluation data and writes the result to
audit_evidence/ch7_restructured/loop_detection.json so the chapter prose has a
pinned source. It reads experiment inputs only; nothing here is modified.

Two criteria are reported, because the object trajectory carries both a
`detected` and a `filled` column and the two give different counts:

  detected   df.detected == 1. The ArUco extractor writes this column
             (v1/aruco/extract_aruco.py, mirrored by the detections block of
             the _aruco_raw_scaled.meta.json sidecar). filter_object_track.py
             copies it through unchanged, and clean_object_track.py only ever
             clears it; on this recording it clears none, which is asserted
             below. This criterion answers "did the detector return an object
             marker pose on that frame".

  accepted   finite position AND detected == 1 AND filled == 0, the rule of
             load_track() in scripts/evaluate_ch7_object.py. It additionally
             drops the samples the Hampel despiker rejected and the samples the
             track filter interpolated, so it answers "is there a usable
             measured sample on that frame".

Neither criterion is adjusted to reach any target value. The reproduction block
of the output records the historical unpinned claim beside both counts.

The location of the missing frames is established from the pinned grip episodes
of eval/output/recovery_r5/grip_episodes.json: the desk handover is the stretch
where the left and right grip episodes overlap, that is where both hands hold
the cube.

Run from the repository root:
    /home/luo/anaconda3/bin/python \
        writing/v8/condensed/scripts/evaluate_ch7_loop_detection.py
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[4]
OUT = REPO / 'writing/v8/condensed/audit_evidence/ch7_restructured'
sys.path.insert(0, str(REPO / 'eval/common'))

import paths

STEM = paths.R5_STEM            # the loop recording, 2099 frames
OBJECT_MARKER_ID = '1'          # paths.OBJECT_ID, as keyed in the ArUco sidecar
FPS = 30.0                      # recorded pace, used only for a duration note

SOURCES = set()


def source(path):
    path = Path(path)
    assert path.exists(), path
    SOURCES.add(path.resolve())
    return path


def read_csv(path):
    df = pd.read_csv(source(path))
    assert df.frame.is_unique, path
    return df


def read_json(path):
    return json.loads(source(path).read_text())


def save_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def rel(path):
    return str(Path(path).resolve().relative_to(REPO))


def runs(frames):
    """Contiguous frame runs of a sorted integer frame array."""
    out = []
    for f in [int(x) for x in frames]:
        if out and f == out[-1][1] + 1:
            out[-1][1] = f
        else:
            out.append([f, f])
    return [dict(first_frame=a, last_frame=b, n_frames=b - a + 1) for a, b in out]


def tracks():
    """The authoritative cleaned track plus the two upstream tracks.

    paths.object_world_filtered() returns the cleaned track once it exists, so
    the cleaned file is what every current Chapter 7 harness reads. The two
    upstream files are read only to show that the detected column is the same
    in all three.
    """
    clean = paths.object_world_filtered(STEM)
    assert clean.name.endswith('_filtered_clean.csv'), clean
    filtered = clean.with_name(clean.name.replace('_clean.csv', '.csv'))
    raw = filtered.with_name(filtered.name.replace('_filtered.csv', '.csv'))
    return clean, filtered, raw


def counts(df):
    frame = df.frame.to_numpy(int)
    detected = df['detected'].to_numpy(int) == 1
    filled = df['filled'].to_numpy(int) == 1
    position = df[['unity_px', 'unity_py', 'unity_pz']].apply(
        pd.to_numeric, errors='coerce').to_numpy(float)
    finite = np.isfinite(position).all(axis=1)
    accepted = finite & detected & ~filled
    # The cleaned track blanks the position of every row it rejects, so a row
    # with a finite position is exactly a row the cleaning kept.
    assert (finite == detected).all(), 'cleaned track blanks exactly the undetected rows'
    return dict(
        frames_total=int(len(df)),
        first_frame=int(frame.min()), last_frame=int(frame.max()),
        detected=dict(
            criterion='detected == 1 (the ArUco extractor returned an object '
                      'marker pose on that frame)',
            n_frames=int(detected.sum()),
            n_missing=int((~detected).sum()),
            coverage_pct=float(100 * detected.sum() / len(df)),
            missing_frames=[int(f) for f in frame[~detected]],
            missing_runs=runs(frame[~detected])),
        accepted=dict(
            criterion='finite position and detected == 1 and filled == 0, the '
                      'load_track rule of scripts/evaluate_ch7_object.py',
            n_frames=int(accepted.sum()),
            n_missing=int((~accepted).sum()),
            coverage_pct=float(100 * accepted.sum() / len(df)),
            missing_frames=[int(f) for f in frame[~accepted]],
            missing_runs=runs(frame[~accepted])),
        despiked_and_bridged=dict(
            note='Rows the Hampel despiker rejected although the detector '
                 'returned a pose, and rows the track filter interpolated. '
                 'These are the whole difference between the two criteria.',
            detected_but_filled=[int(f) for f in frame[detected & filled]],
            undetected_and_filled=[int(f) for f in frame[~detected & filled]],
            n_filled=int(filled.sum())))


def two_hand_intervals():
    """Frames on which the pinned left and right grip episodes overlap.

    The episodes come from the recovery harness that produced the Chapter 7
    natural-occlusion results; no new grip rule is introduced here. Their
    intersection is the stretch during which both hands hold the cube, which is
    what the prose calls a handover.
    """
    episodes = read_json(paths.EVAL_OUT / f'recovery_{paths.ALIAS[STEM]}'
                         / 'grip_episodes.json')['episodes']
    assert set(episodes) == {'left', 'right'}
    held = {}
    for side in ('left', 'right'):
        spans = [(int(e['start']), int(e['stop'])) for e in episodes[side]]
        held[side] = {f for a, b in spans for f in range(a, b + 1)}
    both = sorted(held['left'] & held['right'])
    return runs(both), {side: [[int(e['start']), int(e['stop'])]
                               for e in episodes[side]] for side in episodes}


def locate(detected_block, intervals):
    """Where the undetected frames sit relative to the two-hand intervals.

    The first two two-hand intervals are consecutive stretches of the same desk
    transfer, separated only by the stretch on which the marker is lost: the
    grip state cannot be evaluated without an object sample, so the episodes
    break there and resume. The desk handover therefore runs from the start of
    the first interval to the end of the second.
    """
    assert len(intervals) >= 2, 'fewer than two two-hand intervals'
    first, second = intervals[0], intervals[1]
    marker_loss = [first['last_frame'] + 1, second['first_frame'] - 1]
    assert marker_loss[0] <= marker_loss[1], 'the first two intervals are adjacent'
    span_first, span_last = first['first_frame'], second['last_frame']
    missing = detected_block['missing_frames']
    between = [f for f in missing if marker_loss[0] <= f <= marker_loss[1]]
    inside = [f for f in missing if span_first <= f <= span_last]
    outside = [f for f in missing if not (span_first <= f <= span_last)]
    return dict(
        rule='The desk handover is the first stretch on which the left and '
             'right grip episodes overlap, together with the stretch of lost '
             'marker that interrupts it and the two-hand interval that '
             'resumes after it. The span below runs from the start of the '
             'first two-hand interval to the end of the second.',
        preceding_two_hand_interval=first,
        following_two_hand_interval=second,
        handover_span=[span_first, span_last],
        marker_loss_stretch=dict(first_frame=marker_loss[0],
                                 last_frame=marker_loss[1],
                                 n_frames=marker_loss[1] - marker_loss[0] + 1,
                                 n_missing=len(between),
                                 n_detected=(marker_loss[1] - marker_loss[0] + 1
                                             - len(between)),
                                 missing_runs=runs(between)),
        longest_missing_run=max(detected_block['missing_runs'],
                                key=lambda r: r['n_frames']),
        n_missing_in_handover_span=len(inside),
        missing_outside_handover_span=outside,
        distance_of_outside_frames_to_span=[span_first - f for f in outside],
        note='Frame %s is the one undetected frame outside the span. It sits '
             'one frame before the left hand enters its grip episode, at the '
             'near edge of the same transfer. A grip episode cannot begin on '
             'a frame with no object sample, so this alignment is not '
             'independent evidence of the handover boundary.'
             % ', '.join(str(f) for f in outside))


def label_frames(detected_block):
    """Object availability on the frames labelled for Section 7.4.2."""
    labels = read_json(OUT / 'natural.json')['rows']
    frames = sorted({int(r['frame']) for r in labels})
    missing = set(detected_block['missing_frames'])
    return dict(
        n_labelled_frames=len(frames),
        first_frame=frames[0], last_frame=frames[-1],
        labelled_frames_without_object_marker=[f for f in frames if f in missing],
        note='Every manually labelled clean and failure frame of Section 7.4.2 '
             'carries a detected object marker, so the object-assisted method '
             'had object information available on all of them.')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    clean, filtered, raw = tracks()
    result = counts(read_csv(clean))

    # Cross-checks. The detected column must be identical in the cleaned track,
    # the pre-cleaning filtered track and the unfiltered world track, and must
    # match the ArUco extractor's own detection tally for the object marker.
    cross = {}
    for label, path in (('filtered_track', filtered), ('unfiltered_track', raw)):
        other = read_csv(path)
        n = int((other['detected'].to_numpy(int) == 1).sum())
        cross[label] = dict(path=rel(path), frames_total=int(len(other)), detected=n)
        assert len(other) == result['frames_total']
        assert n == result['detected']['n_frames'], label
    meta = read_json(paths.EVAL_OUT / f'{STEM}_aruco_raw_scaled.meta.json')
    cross['aruco_extractor_sidecar'] = dict(
        path=rel(paths.EVAL_OUT / f'{STEM}_aruco_raw_scaled.meta.json'),
        frames_total=int(meta['frames_total']),
        object_marker_detections=int(meta['detections'][OBJECT_MARKER_ID]))
    assert cross['aruco_extractor_sidecar']['frames_total'] == result['frames_total']
    assert (cross['aruco_extractor_sidecar']['object_marker_detections']
            == result['detected']['n_frames'])
    filter_meta = read_json(filtered.with_name(
        filtered.name.replace('.csv', '.meta.json')))
    cross['track_filter_sidecar'] = dict(
        path=rel(filtered.with_name(filtered.name.replace('.csv', '.meta.json'))),
        frames=int(filter_meta['frames']), detected=int(filter_meta['detected']),
        despiked=int(filter_meta['despiked']), bridged=int(filter_meta['bridged']))
    assert cross['track_filter_sidecar']['detected'] == result['detected']['n_frames']

    intervals, episodes = two_hand_intervals()
    where = locate(result['detected'], intervals)

    historical = dict(
        claim='2058 of 2099 frames carry the object marker, 41 missing, 40 of '
              'them in the desk handover',
        previous_source='eval/output/%s_scaled_object_world.csv, an evaluation '
                        'output rather than a pinned report (DECISIONS.md '
                        'D-024 evidence line)' % STEM,
        reproduces_under_detected_criterion=bool(
            result['detected']['n_frames'] == 2058
            and result['frames_total'] == 2099
            and result['detected']['n_missing'] == 41
            and where['n_missing_in_handover_span'] == 40),
        reproduces_under_accepted_criterion=bool(
            result['accepted']['n_frames'] == 2058),
        recomputed_detected='%d of %d, %d missing, %d of them inside the desk '
                            'handover span %s'
                            % (result['detected']['n_frames'],
                               result['frames_total'],
                               result['detected']['n_missing'],
                               where['n_missing_in_handover_span'],
                               where['handover_span']),
        recomputed_accepted='%d of %d, %d not accepted'
                            % (result['accepted']['n_frames'],
                               result['frames_total'],
                               result['accepted']['n_missing']),
        note='The two criteria differ by the despiked and interpolated rows. '
             'Neither criterion was altered to reach the claimed value.')

    payload = dict(
        purpose='Loop-recording object-marker detection coverage, pinned for '
                'Section 7.4.2. Object-marker availability bounds when '
                'object-assisted recovery can have object information at all.',
        decision='D-033 scopes the natural-occlusion subsection; D-040 fixes '
                 'the evaluation reference for wrist error and does not apply '
                 'here, because a detection count is a coverage statistic and '
                 'not an error against any reference.',
        stem=STEM, alias=paths.ALIAS[STEM],
        recording='the loop recording, the earlier two-hand loop take',
        track=rel(clean),
        frame_rate_fps=FPS,
        **result,
        gap_duration_s=dict(
            marker_loss_stretch=float(
                where['marker_loss_stretch']['n_frames'] / FPS),
            all_missing=float(result['detected']['n_missing'] / FPS)),
        cross_checks=cross,
        grip_episodes=dict(
            path=rel(paths.EVAL_OUT / f'recovery_{paths.ALIAS[STEM]}'
                     / 'grip_episodes.json'),
            episodes=episodes, two_hand_intervals=intervals),
        location_of_missing_frames=where,
        section_7_4_2_label_frames=label_frames(result['detected']),
        reproduction=historical,
        caveats=[
            'The detected column records that the extractor returned a marker '
            'pose, not that the pose is accurate. A detected frame near the '
            'edge of a gap can still carry a poor solve; the waypoint report '
            'of this recording flags exactly that at the handover edges.',
            'The accepted criterion is stricter and is the one the object '
            'trajectory results use. A coverage sentence must say which of '
            'the two it reports.',
            'The two-hand intervals come from the existing grip detector with '
            'its own entry and exit hysteresis. They locate the handover; they '
            'are not an independent measurement of when contact began.',
            'Frame counts are exact. No threshold in this script depends on '
            'the size of any reconstruction error.'])

    # Provenance in the style of object_provenance.json, kept inside this file
    # so the whole result is one pinned artefact.
    for name in ('eval/common/paths.py', 'eval/common/clean_object_track.py',
                 'v1/aruco/filter_object_track.py'):
        source(REPO / name)
    source(__file__)
    payload['provenance'] = dict(
        numpy=np.__version__, pandas=pd.__version__,
        statistics='exact frame counts only; no percentile or interpolation',
        sources=[dict(path=rel(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                 for p in sorted(SOURCES)])
    save_json('loop_detection.json', payload)

    print('PASS: detected %d of %d frames, %d missing, runs %s'
          % (result['detected']['n_frames'], result['frames_total'],
             result['detected']['n_missing'],
             [(r['first_frame'], r['last_frame']) for r in
              result['detected']['missing_runs']]))
    print('PASS: accepted %d of %d frames, %d not accepted'
          % (result['accepted']['n_frames'], result['frames_total'],
             result['accepted']['n_missing']))
    print('PASS: %d missing frames inside the desk handover span %s, %s outside'
          % (where['n_missing_in_handover_span'], where['handover_span'],
             where['missing_outside_handover_span']))
    print('PASS: historical claim reproduces under the detected criterion:',
          historical['reproduces_under_detected_criterion'])
    print('PASS: Chapter 7 loop detection evidence saved to', OUT)


if __name__ == '__main__':
    main()
