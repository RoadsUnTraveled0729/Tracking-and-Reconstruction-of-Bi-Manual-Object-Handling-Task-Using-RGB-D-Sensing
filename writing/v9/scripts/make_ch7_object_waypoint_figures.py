#!/usr/bin/env python3
"""Plot the reconstructed marker-centre trajectory of each recording with the
pinned W1 to W4 waypoints marked.

The handover recording also carries the transfer between the hands as a marked
waypoint H, in the same marker style as W1 to W4. Its frame window is the
recorded both-hands-at-the-cube run of eval/reports/r7_handover.json (left hand
arrives to right hand leaves); its position is the mean of the accepted samples
in that window, the estimator W1 and W4 already use. The rail recording has no
handover and is unchanged.

Only reconstructed quantities are drawn. The physical route is not registered
into the calibrated world frame (D-030, D-035), so no physical path, no
physical waypoint and no tape length appears in either figure.

Coordinates are final Scene positions (D-082): the stored unity_p* columns
already contain S times the World position, so pScene = G*pStored + t_f.
The proper rotation G aligns the calibrated gravity direction with Scene y;
t_f = (0, d, 0) places the displayed floor at Scene y = 0. The recording's
d is its calibrated marker-to-table offset plus the receiver's desk thickness
and leg height. Every waypoint is recomputed from the unchanged selected
samples and checked against the pinned position plus this same translation.
The pinned experimental evidence and waypoint selection are not rewritten.

Run from the repository root:
    MPLCONFIGDIR=/tmp/ch7_restructured_mpl XDG_CACHE_HOME=/tmp/ch7_restructured_cache \
    /home/luo/anaconda3/bin/python writing/v9/scripts/make_ch7_object_waypoint_figures.py
"""
import json
import hashlib
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
REPO = Path(__file__).resolve().parents[3]
for folder in ('eval/common', 'eval/unity_check'):
    sys.path.insert(0, str(REPO / folder))

import paths
from check_unity_log import from_to_rotation, DESK_THICK, LEG_H

OBJECT = json.loads((HERE / 'audit_evidence/ch7_restructured/object.json').read_text())
EVIDENCE_DIR = HERE / 'audit_evidence/ch7_object_3d'
BASELINE_REVISION = 'b52235513477f5d44a4b790d52858b12a934b4b9'
BASELINE_GENERATOR_SHA256 = 'ef04239992cddeccb203b62050d88391ca3621f33c5e1bc10f0f313412787b1c'
EXPECTED_INPUT_SHA256 = {
    'writing/v9/audit_evidence/ch7_restructured/object.json':
        '9b6835fca5dde6e892f8a1ad09a420dd239f32c27044a6179a1968f2fa1bd9fd',
    'eval/output/recording_20260831_065553_scaled_object_world_filtered_clean.csv':
        'a96561ddc789b14be74a2acdf768b44c8d6faeeef8134f033d25fc69adbf7d4a',
    'eval/output/scene_calibration_r6bc.json':
        'b889d84be75fed40b6add38f0b247fc34f362392a5e705949c69587ae235f5c6',
    'eval/output/recording_20260909_000024_scaled_object_world_filtered_clean.csv':
        '7f00506a2b9f01fd21b4852c7edac8817b79260b230dcda5f65af316b48ecabd',
    'eval/output/scene_calibration_r7c.json':
        '5516a93781e05f109ede67883932310b9bfc4727f7c9479ec34ae2c0210d96cc',
    # Re-pinned at commit e6e87c6 (E-036), which added --person-log,
    # --object-log and --frames-dir command-line overrides to that checker.
    # The three names imported here are byte-identical across that commit:
    # from_to_rotation, DESK_THICK = 0.03 and LEG_H = 0.69. The superseded
    # pin is kept below and the constants are asserted before plotting.
    'eval/unity_check/check_unity_log.py':
        '71bbf518e304a94ba81d64c685a70bb6142e011b7df9a86de89010e055c2b0f8',
    'eval/common/paths.py':
        '1271913fdb926ead2cb3d801308bba1a0e7c9876fe417fdb707d2e99c237b0ef',
    'eval/reports/r7_handover.json':
        '8e4588a6d216c5a98fb13e2eeb43d4638298a64b636f95b7619e71b5ef9a115c',
}
SUPERSEDED_INPUT_SHA256 = {
    'eval/unity_check/check_unity_log.py':
        'd93811a74a347421ef29bcc9419e9b2100ebfb606d6c609865b137e0ab56a44c',
}
BASELINE_ARRAY_SHA256 = {
    'r6b': {
        'accepted_frames_int64_le':
            'c82326cbaa7c9fdba57ea580ba02f1bab690191a990f10050906b5bb468f417b',
        'scene_xyz_cm_float64_le':
            'c11ae1e39f0a52cda6b8ad2814bbf6a9e72175ea0c0280d115bbf2948c9ac574',
    },
    'r7': {
        'accepted_frames_int64_le':
            '544423cbe90f4626c11f2c0847e6109efc7648cd5db7a6dd8c6247c4f2db6c2c',
        'scene_xyz_cm_float64_le':
            '8dfc8a963ce4be40f456805383b771c8b70a0597fb8cdf0c5c19f6a342e982f1',
    },
}
FIGURE_SIZE_IN = (10.2, 7.2)
FIGURE_DPI = 220
plt.rcParams.update({'font.family': 'DejaVu Serif', 'font.size': 14})
TRACK_COLOR = '#2369a4'
MARK_COLOR = '#b64425'
TITLES = {'r6b': 'Rail recording', 'r7': 'Handover recording'}
# The handover waypoint exists only in the handover recording.
HANDOVER_ALIAS = 'r7'
HANDOVER_REPORT = 'eval/reports/r7_handover.json'
HANDOVER_NAME = 'H'
HANDOVER_LEGEND = 'Handover position (H)'
# Label offsets in points, chosen per panel so the labels never collide.
OFFSETS = {
    'xy': {'W1': (9, -4), 'W2': (-34, -4), 'W3': (-6, 9), 'W4': (-6, -15),
           'H': (-4, 10)},
    'xz': {'W1': (9, -4), 'W2': (-8, -15), 'W3': (5, 6), 'W4': (5, -13),
           'H': (-4, 10)},
}
# Scene-coordinate label displacements keep W2 and W3 separate in perspective.
OFFSETS_3D_CM = {
    'W1': (3.0, -1.0, -1.0),
    'W2': (-8.0, -5.0, -4.0),
    'W3': (1.0, 2.0, 1.0),
    'W4': (-5.0, 4.0, 0.0),
    'H': (-1.0, -5.0, 0.5),
}


def floor_translation(calibration):
    """Receiver floor placement in metres, including its decorative desk size.

    ArucoSceneReceiver.BuildDeferredScene projects both desk-centre endpoints
    onto the same tabletop plane. After G, their shared y coordinate is the
    negative calibrated offset. Thus its floor placement is exactly this sum.
    The constants are imported from the existing receiver checker.
    """
    d = (calibration['scene_geometry']['origin_above_tabletop_m']
         + DESK_THICK + LEG_H)
    return np.array([0., d, 0.])


def scene_samples(alias):
    """Accepted marker-centre samples in final Scene coordinates, in cm."""
    record = OBJECT['recordings'][alias]
    df = pd.read_csv(REPO / record['track'])
    calib = json.loads((REPO / record['calibration']).read_text())
    unity = df[['unity_px', 'unity_py', 'unity_pz']].apply(
        pd.to_numeric, errors='coerce').to_numpy(float)
    accepted = (np.isfinite(unity).all(axis=1) & (df['detected'].to_numpy() == 1)
                & ~(df['filled'].to_numpy() == 1))
    assert paths.ALIAS[record['stem']] == alias
    assert int(accepted.sum()) == record['samples']['accepted']
    gravity = np.asarray(calib['scene_geometry']['gravity_up_unity'], float)
    gravity /= np.linalg.norm(gravity)
    G = from_to_rotation(gravity, np.array([0., 1., 0.]))
    translation = floor_translation(calib)
    scene = (G @ unity[accepted].T).T + translation
    return (scene * 100, df.frame.to_numpy(int)[accepted], record,
            translation * 100)


def waypoints(xyz, frames, record, translation_cm):
    """Recompute each pinned waypoint position from the accepted samples."""
    out = {}
    for name, entry in record['waypoints'].items():
        inside = (frames >= entry['first_frame']) & (frames <= entry['last_frame'])
        assert int(inside.sum()) == entry['n_samples'], (name, inside.sum())
        position = xyz[inside].mean(axis=0)
        pinned = np.asarray(entry['position_m'], float) * 100 + translation_cm
        assert np.allclose(position, pinned, atol=1e-6), (name, position, pinned)
        out[name] = position
    return out


def handover_mark(alias, xyz, frames):
    """Marker centre over the recorded transfer between the hands.

    Nothing is invented here. The window is the both-hands-at-the-cube run
    recorded in eval/reports/r7_handover.json, and the position is the mean of
    the accepted samples inside it, the same estimator as the W1 and W4
    intervals. The two window boundaries are recorded alongside it.
    """
    if alias != HANDOVER_ALIAS:
        return {}, None
    report = json.loads((REPO / HANDOVER_REPORT).read_text())['hand_over']
    first = int(report['left_hand_arrives_frame'])
    last = int(report['right_hand_leaves_frame'])
    assert [[first, last]] == report['both_at_cube_runs']
    inside = (frames >= first) & (frames <= last)
    position = xyz[inside].mean(axis=0)
    record = {
        'source': HANDOVER_REPORT,
        'definition': ('hand_over.both_at_cube_runs: left hand arrives to '
                       'right hand leaves'),
        'window_first_frame': first,
        'window_last_frame': last,
        'window_frames': last - first + 1,
        'n_accepted_samples': int(inside.sum()),
        'estimator': 'mean of accepted samples',
        'scene_position_cm': position.tolist(),
        'scene_position_at_first_frame_cm':
            xyz[frames == first][0].tolist(),
        'scene_position_at_last_frame_cm': xyz[frames == last][0].tolist(),
        'spread_mm': ((xyz[inside].max(axis=0) - xyz[inside].min(axis=0))
                      * 10).tolist(),
    }
    return {HANDOVER_NAME: position}, record


def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_array(values, dtype):
    """Hash a canonical little-endian contiguous representation."""
    canonical = np.ascontiguousarray(values, dtype=dtype)
    return hashlib.sha256(canonical.tobytes()).hexdigest()


def panel_2d(ax, xyz, marks, vertical, ylabel, equal, key):
    ax.scatter(xyz[:, 0], xyz[:, vertical], s=3, color=TRACK_COLOR, alpha=0.45,
               linewidths=0, label='Accepted marker-centre sample')
    for i, (name, position) in enumerate(marks.items()):
        if name == HANDOVER_NAME:
            label = HANDOVER_LEGEND
        else:
            label = 'Waypoint position' if i == 0 else None
        ax.plot(position[0], position[vertical], marker='D', markersize=6.5,
                markerfacecolor='white', markeredgewidth=1.5, color=MARK_COLOR,
                linestyle='none', label=label)
        ax.annotate(name, (position[0], position[vertical]), color=MARK_COLOR,
                    textcoords='offset points', xytext=OFFSETS[key][name],
                    fontsize=13.5, fontweight='semibold')
    ax.set_xlabel('Scene x (cm)')
    ax.set_ylabel(ylabel)
    ax.grid(True, color='#d9d9d9', linewidth=0.5)
    ax.set_axisbelow(True)
    ax.margins(x=0.10, y=0.16)
    ax.tick_params(labelsize=13.5)
    if equal:
        ax.set_aspect('equal', adjustable='box')


def panel_3d(ax, xyz, marks):
    """Draw Scene x-z-y so Matplotlib's screen-vertical axis is Scene y."""
    ax.scatter(xyz[:, 0], xyz[:, 2], xyz[:, 1], s=5, color=TRACK_COLOR,
               alpha=0.45, linewidths=0, depthshade=False)
    for name, position in marks.items():
        ax.scatter(position[0], position[2], position[1], s=52, marker='D',
                   facecolor='white', edgecolor=MARK_COLOR, linewidth=1.5,
                   depthshade=False)
        dx, dy, dz = OFFSETS_3D_CM[name]
        ax.text(position[0] + dx, position[2] + dz, position[1] + dy, name,
                color=MARK_COLOR, fontsize=13.5, fontweight='semibold')

    # All three axes use the same numerical span and the same box dimension.
    # One centimetre therefore has the same display scale in every direction.
    plotted = np.vstack([xyz, np.vstack(list(marks.values()))])
    centre = (plotted.min(axis=0) + plotted.max(axis=0)) / 2
    span = float(np.ptp(plotted, axis=0).max() * 1.14)
    half = span / 2
    ax.set_xlim(centre[0] - half, centre[0] + half)
    ax.set_ylim(centre[2] - half, centre[2] + half)
    ax.set_zlim(centre[1] - half, centre[1] + half)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=22, azim=-56)
    ax.set_xlabel('Scene x (cm)', labelpad=9)
    ax.set_ylabel('Scene z (cm)', labelpad=9)
    ax.set_zlabel('Scene y (cm)', labelpad=9)
    ax.tick_params(labelsize=13.5, pad=1)
    ax.grid(True)
    return span


def axis_display_record(ax, fig, xlim, ylim):
    bounds = ax.get_position().bounds
    box_inches = [bounds[2] * fig.get_figwidth(),
                  bounds[3] * fig.get_figheight()]
    horizontal_span = float(xlim[1] - xlim[0])
    vertical_span = float(ylim[1] - ylim[0])
    return {
        'figure_fraction_bounds': [float(v) for v in bounds],
        'plot_box_inches': box_inches,
        'axis_limits_cm': {'horizontal': list(map(float, xlim)),
                           'vertical': list(map(float, ylim))},
        'display_inches_per_scene_cm': {
            'horizontal': box_inches[0] / horizontal_span,
            'vertical': box_inches[1] / vertical_span,
        },
    }


def main():
    actual_hashes = {name: sha256_file(REPO / name)
                     for name in EXPECTED_INPUT_SHA256}
    assert actual_hashes == EXPECTED_INPUT_SHA256, (actual_hashes,
                                                     EXPECTED_INPUT_SHA256)
    # The imported geometry contract, checked rather than assumed.
    assert (DESK_THICK, LEG_H) == (0.03, 0.69), (DESK_THICK, LEG_H)
    provenance = {
        'scope': 'Chapter 7 object-waypoint figure layout only',
        'baseline_revision': BASELINE_REVISION,
        'baseline_generator_sha256': BASELINE_GENERATOR_SHA256,
        'input_sha256': actual_hashes,
        'input_hashes_match_baseline_evidence': not SUPERSEDED_INPUT_SHA256,
        'input_hash_changes_since_baseline_evidence': {
            name: {'baseline_sha256': digest,
                   'current_sha256': actual_hashes[name],
                   'reason': ('commit e6e87c6 (E-036) added command-line log '
                              'overrides; from_to_rotation, DESK_THICK and '
                              'LEG_H are unchanged and asserted at run time')}
            for name, digest in SUPERSEDED_INPUT_SHA256.items()},
        'inputs_added_since_baseline_evidence': {
            'eval/reports/r7_handover.json':
                'recorded handover window for the H waypoint of Figure 7.2'},
        'numeric_pipeline': (
            'scene_samples, floor_translation and waypoints are unchanged from '
            'the baseline generator; only the Matplotlib layout is revised.'),
        'layout': {
            'figure_size_inches': list(FIGURE_SIZE_IN),
            'dpi': FIGURE_DPI,
            'grid': 'two rows by two columns; right 3D axis spans both rows',
            'grid_width_ratios': [1.0, 1.58],
            'upper_left': 'Scene x versus Scene y; independent display scales',
            'lower_left': 'Scene x versus Scene z; equal metric display scale',
            'right': ('3D Scene x-z-y mapping, so Scene y is screen vertical; '
                      'equal axis spans and cubic box give equal metric scale'),
            'camera': {'elevation_deg': 22, 'azimuth_deg': -56},
            '3d_waypoint_label_offsets_scene_xyz_cm': OFFSETS_3D_CM,
            'handover_waypoint': (
                'the handover recording adds the transfer between the hands as '
                'waypoint H, in the waypoint marker style, with its own legend '
                'entry; the rail recording is unchanged'),
            'source_font_points': 14,
            'smallest_label_font_points': 13.5,
            'embedding': {
                'at_6.1_in_width': {
                    'scale': 6.1 / FIGURE_SIZE_IN[0],
                    'height_inches': FIGURE_SIZE_IN[1] * 6.1 / FIGURE_SIZE_IN[0],
                    'base_font_points': 14 * 6.1 / FIGURE_SIZE_IN[0],
                    'smallest_label_font_points': 13.5 * 6.1 / FIGURE_SIZE_IN[0],
                },
                'at_6.5_in_width': {
                    'scale': 6.5 / FIGURE_SIZE_IN[0],
                    'height_inches': FIGURE_SIZE_IN[1] * 6.5 / FIGURE_SIZE_IN[0],
                    'base_font_points': 14 * 6.5 / FIGURE_SIZE_IN[0],
                    'smallest_label_font_points': 13.5 * 6.5 / FIGURE_SIZE_IN[0],
                },
            },
        },
        'recordings': {},
    }
    for alias in ('r6b', 'r7'):
        xyz, frames, record, translation_cm = scene_samples(alias)
        marks = waypoints(xyz, frames, record, translation_cm)
        handover, handover_record = handover_mark(alias, xyz, frames)
        drawn = {**marks, **handover}
        frame_hash = sha256_array(frames, '<i8')
        xyz_hash = sha256_array(xyz, '<f8')
        assert frame_hash == BASELINE_ARRAY_SHA256[alias][
            'accepted_frames_int64_le']
        assert xyz_hash == BASELINE_ARRAY_SHA256[alias][
            'scene_xyz_cm_float64_le']
        fig = plt.figure(figsize=FIGURE_SIZE_IN)
        grid = fig.add_gridspec(2, 2, width_ratios=(1.0, 1.58),
                                height_ratios=(0.78, 1.22),
                                left=0.09, right=0.985, bottom=0.235, top=0.85,
                                wspace=0.14, hspace=0.78)
        ax_xy = fig.add_subplot(grid[0, 0])
        ax_xz = fig.add_subplot(grid[1, 0])
        ax_3d = fig.add_subplot(grid[:, 1], projection='3d')
        panel_2d(ax_xy, xyz, drawn, 1, 'Scene y (cm)', False, 'xy')
        panel_2d(ax_xz, xyz, drawn, 2, 'Scene z (cm)', True, 'xz')
        cube_span_cm = panel_3d(ax_3d, xyz, drawn)
        ax_xy.set_title('(a) x-y', fontsize=14.5, pad=4)
        ax_xz.set_title('(b) x-z', fontsize=14.5, pad=4)
        ax_3d.set_title('(c) 3D Scene', fontsize=14.5, pad=2)
        fig.suptitle(f"{TITLES[alias]}, {record['samples']['accepted']} accepted samples",
                     fontsize=15, y=0.965)
        handles, labels = ax_xy.get_legend_handles_labels()
        fig.legend(handles, labels, loc='lower center', ncol=len(labels),
                   fontsize=13.5,
                   framealpha=0.95, bbox_to_anchor=(0.51, 0.01),
                   handletextpad=0.5, columnspacing=1.4)
        fig.canvas.draw()
        out = HERE / 'figures' / f'ch7_object_waypoints_{alias}.png'
        fig.savefig(out, dpi=FIGURE_DPI)

        waypoint_records = {}
        for name, position in marks.items():
            entry = record['waypoints'][name]
            selected = frames[(frames >= entry['first_frame']) &
                              (frames <= entry['last_frame'])]
            pinned = np.asarray(entry['position_m'], float) * 100 + translation_cm
            waypoint_records[name] = {
                'selection_first_frame': entry['first_frame'],
                'selection_last_frame': entry['last_frame'],
                'selected_accepted_frames': selected.tolist(),
                'n_samples': entry['n_samples'],
                'source_position_m': entry['position_m'],
                'computed_scene_position_cm': position.tolist(),
                'pinned_scene_position_cm': pinned.tolist(),
                'max_abs_coordinate_difference_cm':
                    float(np.max(np.abs(position - pinned))),
            }
        provenance['recordings'][alias] = {
            'accepted_samples': int(len(xyz)),
            'accepted_frame_first': int(frames[0]),
            'accepted_frame_last': int(frames[-1]),
            'accepted_frames_sha256_int64_le': frame_hash,
            'scene_xyz_cm_sha256_float64_le': xyz_hash,
            'accepted_frames_match_baseline_generator': True,
            'scene_xyz_cm_match_baseline_generator': True,
            'scene_xyz_cm_min': xyz.min(axis=0).tolist(),
            'scene_xyz_cm_max': xyz.max(axis=0).tolist(),
            'floor_translation_cm': translation_cm.tolist(),
            'waypoints': waypoint_records,
            'handover_waypoint': handover_record,
            'segments_unchanged': record['segments'],
            'display': {
                'xy': axis_display_record(ax_xy, fig, ax_xy.get_xlim(),
                                          ax_xy.get_ylim()),
                'xz': axis_display_record(ax_xz, fig, ax_xz.get_xlim(),
                                          ax_xz.get_ylim()),
                '3d_equal_axis_span_cm': cube_span_cm,
                '3d_limits_cm': {
                    'scene_x': list(map(float, ax_3d.get_xlim())),
                    'scene_z': list(map(float, ax_3d.get_ylim())),
                    'scene_y_up': list(map(float, ax_3d.get_zlim())),
                },
            },
            'output': {
                'path': str(out.relative_to(REPO)),
                'width_pixels': int(FIGURE_SIZE_IN[0] * FIGURE_DPI),
                'height_pixels': int(FIGURE_SIZE_IN[1] * FIGURE_DPI),
                'sha256': sha256_file(out),
            },
        }
        plt.close(fig)
        print('PASS:', out)

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    evidence = EVIDENCE_DIR / 'provenance.json'
    evidence.write_text(json.dumps(provenance, indent=2) + '\n')
    print('PASS:', evidence)


if __name__ == '__main__':
    main()
