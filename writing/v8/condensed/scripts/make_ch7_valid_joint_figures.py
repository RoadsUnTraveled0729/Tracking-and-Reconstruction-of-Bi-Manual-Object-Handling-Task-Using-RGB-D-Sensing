#!/usr/bin/env python3
"""Plot only the coordinate pairs used by the Chapter 7 rig evaluation."""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
data = pd.read_csv(HERE / 'audit_evidence/ch7_restructured/human_pairs.csv')
plt.rcParams.update({'font.family': 'DejaVu Serif', 'font.size': 9})

for alias, sides in (('r6b', ['right']), ('r7', ['right', 'left'])):
    fig = plt.figure(figsize=(10, 4.2 * len(sides)), layout='constrained')
    # D-076: separate upper 3D-axis labels from the lower-row titles.
    # This changes layout only; all coordinate data and axis limits stay fixed.
    fig.get_layout_engine().set(hspace=0.16)
    for row, side in enumerate(sides):
        for col, joint in enumerate(('elbow', 'wrist')):
            ax = fig.add_subplot(len(sides), 2, row * 2 + col + 1, projection='3d')
            samples = data[(data.recording == alias) & (data.side == side)
                           & (data.joint == joint)].sort_values('frame')
            points = []
            for prefix, color, label in (('measured', '#2369a4', 'Measured landmark'),
                                         ('rig', '#b64425', 'Unity rig joint')):
                p = samples[[prefix + '_' + a for a in 'xyz']].to_numpy() * 100
                points.append(p)
                # Points avoid visually inventing motion across uncaptured frames.
                ax.scatter(p[:, 0], p[:, 2], p[:, 1], s=6, color=color,
                           alpha=0.6, label=label, depthshade=False)
            allp = np.concatenate(points)[:, [0, 2, 1]]
            lo, hi = allp.min(axis=0), allp.max(axis=0)
            center = (lo + hi) / 2
            span = max(hi - lo) * 1.1
            for setlim, c in zip((ax.set_xlim, ax.set_ylim, ax.set_zlim), center):
                setlim(c - span / 2, c + span / 2)
            ax.set_box_aspect((1, 1, 1))
            ax.set_xlabel('Scene x (cm)')
            ax.set_ylabel('Scene z (cm)')
            ax.set_zlabel('Scene y (cm)')
            ax.set_title(f'{side.capitalize()} {joint}, n = {len(samples)}')
            ax.view_init(elev=22, azim=-62)
            ax.legend(loc='upper left', fontsize=8)
    out = HERE / 'figures' / f'ch7_valid_joints_{alias}.png'
    fig.savefig(out, dpi=200, bbox_inches='tight', pad_inches=0.2)
    plt.close(fig)
    print('PASS:', out)
