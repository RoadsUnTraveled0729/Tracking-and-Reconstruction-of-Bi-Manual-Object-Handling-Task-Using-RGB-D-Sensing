#!/usr/bin/env python3
"""Compose the D-080 qualitative video/Unity examples as Figures 7.5 and 7.6.

All selected sources are pinned by SHA256 in
audit_evidence/remove_intermediate_frame/ch7_visual_examples_sources.json.
The three formerly ignored handover Unity PNGs have byte-identical local
copies under figures/src/ch7_visual_examples, so regeneration needs no Unity
session or ignored input. Every image retains its complete sensor view.

Run from the repository root:
    MPLCONFIGDIR=/tmp/ch7_restructured_mpl XDG_CACHE_HOME=/tmp/ch7_restructured_cache \
    /home/luo/anaconda3/bin/python writing/v9/scripts/make_ch7_visual_examples.py
"""
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image

HERE = Path(__file__).resolve().parent.parent
REPO = Path(__file__).resolve().parents[3]
AUDIT = HERE / 'audit_evidence/remove_intermediate_frame'
SOURCES = AUDIT / 'ch7_visual_examples_sources.json'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    spec = json.loads(SOURCES.read_text())
    plt.rcParams.update({'font.family': 'DejaVu Serif', 'font.size': 9})
    outputs = {}
    for alias, recording in spec['recordings'].items():
        # Layout dimensions and spacing serve readability only (D-080).
        # Three full 4:3 image rows fit the thesis page at 6.5-inch width.
        fig, axes = plt.subplots(3, 2, figsize=(6.8, 8.1))
        fig.subplots_adjust(left=0.015, right=0.985, bottom=0.012, top=0.941,
                            wspace=0.025, hspace=0.13)
        fig.text(0.253, 0.978, 'Recorded video', ha='center', va='top', fontsize=11)
        fig.text(0.747, 0.978, 'Unity sensor view', ha='center', va='top', fontsize=11)
        used = []
        for row_index, row in enumerate(recording['rows']):
            axes[row_index, 0].set_title(
                f"({chr(ord('a') + row_index)}) {row['phase']}, frame {row['frame']}",
                loc='left', fontsize=9, pad=4)
            for column, key in enumerate(('recorded_video', 'unity')):
                entry = row[key]
                source = REPO / entry['path']
                assert digest(source) == entry['sha256'], source
                with Image.open(source) as original:
                    assert list(original.size) == row['size_pixels'], source
                    pixels = original.copy()
                ax = axes[row_index, column]
                ax.imshow(pixels, interpolation='none')
                ax.set_xticks([])
                ax.set_yticks([])
                for spine in ax.spines.values():
                    spine.set_edgecolor('0.45')
                    spine.set_linewidth(0.6)
                used.append({'frame': row['frame'], 'column': key,
                             'source': entry['path'], 'sha256': digest(source),
                             'source_pixels': row['size_pixels'],
                             'crop': None, 'geometric_adjustment': None})
        output = HERE / 'figures' / recording['figure']
        fig.savefig(output, dpi=200, facecolor='white')
        plt.close(fig)
        outputs[alias] = {'figure_number': recording['figure_number'],
                          'path': output.relative_to(REPO).as_posix(),
                          'sha256': digest(output), 'sources': used}
        print('PASS:', output)
    report = {'decision': spec['decision'], 'sources_manifest': SOURCES.relative_to(REPO).as_posix(),
              'sources_manifest_sha256': digest(SOURCES),
              'generator': Path(__file__).resolve().relative_to(REPO).as_posix(),
              'generator_sha256': digest(Path(__file__)),
              'validation': 'All 12 source images match their pinned SHA256 and dimensions; no input image is modified.',
              'outputs': outputs}
    provenance = AUDIT / 'ch7_visual_examples_provenance.json'
    provenance.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS:', provenance)


if __name__ == '__main__':
    main()
