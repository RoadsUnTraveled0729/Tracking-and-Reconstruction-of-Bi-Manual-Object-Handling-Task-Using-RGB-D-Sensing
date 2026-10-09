#!/usr/bin/env python3
"""Turn slide 39 "Limitations" into the system's assumptions and their consequences (D-391).

2026-10-06 (plan declarative-stargazing-phoenix.md, Milestone A). Raw zip + lxml
edit in the manner of anim/patch_results_slides.py, whose helpers are reused
here. The slide 39 table is a grid of text boxes and divider lines (no a:tbl):

- header cells 13 / 14 become "Assumption" / "Consequence";
- rows 16/17, 19/20, 22/23 and 25/26 become the four assumptions (static
  scene, uncertain inputs, object size, rigid torso) and their consequences;
- row 5 (cells 28, 29) and the divider below it (connector 27) are deleted;
- caption 30 and footer 32 name thesis Chapter 9 and Sections 2.2.2, 3.2.1
  and 4.1 instead of Table 9.1.

Text goes into the first a:t of each shape and the other runs are blanked, so
the run formatting (16 pt DejaVu Sans in the cells and caption, 10.5 pt in the
footer) stays. Every other zip entry is written with its original bytes and
ZipInfo. The pptx is rewritten in place; the zip-entry comparison (name, CRC)
and the old and new sha256 and sizes go to review/slide39_patch.json. The
script refuses to run twice (header text check).

Run from the repository root with the thesis Python:

    /home/luo/anaconda3/bin/python -B presentation/defense_2026/anim/patch_slide39_limitations.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from zipfile import ZipFile

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from patch_results_slides import N, read, replace_shape_text, save, sha, shape, shapes, text  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
PPTX = HERE / 'Thesis_Defence_2026.pptx'
RECORD = HERE / 'review' / 'slide39_patch.json'
S39 = 'ppt/slides/slide39.xml'
DOT = '\u00b7'  # the deck's own middle-dot separator (slide 39 cells)

# Old texts, read from the deck at dc59533 (refusal checks).
OLD = {13: 'Scope', 14: 'Current boundary',
       16: 'Participants and motion', 17: f'One subject {DOT} three slow recordings',
       19: 'Object reference', 20: f'Endpoint separations {DOT} route not registered in World',
       22: 'Body proportions', 23: f'Landmark-based lengths {DOT} 5.9 cm elbow landmark offset',
       25: 'Occlusion recovery', 26: 'Different outcomes across hands and grip conditions',
       28: 'Online deployment', 29: f'Recorded replay {DOT} live sensor validation pending',
       30: 'Thesis Table 9.1.', 32: 'Undergraduate thesis | Chapter 9; Table 9.1; Section 8.5'}

# New texts: the approved plan, Milestone A (exact wording).
NEW = {13: 'Assumption', 14: 'Consequence',
       16: 'Static scene',
       17: f'Camera, desk and wall calibrated once and held fixed {DOT} moving any of them means recalibrating',
       19: 'Uncertain inputs',
       20: f'Rejected or held, never estimated {DOT} a held value carries its error into later frames',
       22: 'Object size',
       23: f'Small handheld object {DOT} a large one hides landmarks, the hips L23 and L24 first, '
           'and the root frame drifts',
       25: 'Rigid torso',
       26: f'One plate from hips and shoulders {DOT} trunk bend or twist is not modelled',
       30: f'System assumptions and their consequences {DOT} thesis Chapter 9; Sections 2.2.2, 3.2.1, 4.1',
       32: 'Undergraduate thesis | Chapter 9; Sections 2.2.2, 3.2.1, 4.1'}
DELETE = (28, 29, 27)  # row 5 cells and the divider below it (connector 27, y 5614993 EMU)


def patch39(data):
    r = read(data, S39)
    if text(r, 13) == NEW[13]:
        raise SystemExit('ERROR: slide 39 header already reads "Assumption"; already patched')
    for k, v in OLD.items():
        if text(r, k) != v:
            raise SystemExit(f'ERROR: slide 39 id {k} is {text(r, k)!r}, expected {v!r}')
    conn = shape(r, 27)
    if conn.find('.//p:cNvPr', N).get('name') != 'Connector 26':
        raise SystemExit('ERROR: slide 39 id 27 is not Connector 26')
    for k, v in NEW.items():
        replace_shape_text(r, k, v)
    tree = shapes(r)
    for ident in DELETE:
        tree.remove(shape(r, ident))
    save(data, S39, r)
    return {'texts': {str(k): v for k, v in NEW.items()}, 'deleted_ids': list(DELETE)}


def main():
    old_bytes = PPTX.read_bytes()
    with ZipFile(PPTX) as z:
        infos = z.infolist()
        data = {i.filename: z.read(i.filename) for i in infos}
    before = {i.filename: i.CRC for i in infos}
    edits = patch39(data)

    tmp = PPTX.with_name(PPTX.name + '.tmp')
    with ZipFile(tmp, 'w') as z:
        for info in infos:
            z.writestr(info, data[info.filename])
    with ZipFile(tmp) as z:
        if z.testzip() is not None:
            raise SystemExit('ERROR: written zip fails its CRC test')
        after = {i.filename: i.CRC for i in z.infolist()}
    changed = sorted(n for n in before if n in after and before[n] != after[n])
    added = sorted(n for n in after if n not in before)
    dropped = sorted(n for n in before if n not in after)
    if changed != [S39] or added or dropped:
        tmp.unlink()
        raise SystemExit(f'ERROR: unexpected zip-entry changes: {changed} {added} {dropped}')
    os.replace(tmp, PPTX)
    new_bytes = PPTX.read_bytes()
    record = {
        'purpose': 'Slide 39 Limitations as system assumptions and their consequences (D-391).',
        'generator': str(Path(__file__).resolve().relative_to(ROOT)),
        'generator_sha256': sha(Path(__file__).read_bytes()),
        'pptx': str(PPTX.relative_to(ROOT)),
        'old': {'sha256': sha(old_bytes), 'bytes': len(old_bytes), 'entries': len(before)},
        'new': {'sha256': sha(new_bytes), 'bytes': len(new_bytes), 'entries': len(after)},
        'zip_entry_comparison': {'changed_crc': changed, 'added': added, 'removed': dropped,
                                 'unchanged_entries': len(before) - len(changed) - len(dropped)},
        'old_texts': {str(k): v for k, v in OLD.items()},
        'edits': edits,
        'text_source': 'plan declarative-stargazing-phoenix.md, Milestone A (approved 2026-10-06)',
        'thesis_source': 'writing/v9: static scene Sections 2.2.2 and 4.1; discard/hold Sections 2.5 and 4.2, '
                         'Chapter 9 bullets 3, 5, 6; hidden hips and root drift Section 3.2.1 and Chapter 9 '
                         'bullet 4 (thesis names the desk; "small object" is the author\'s claim); rigid torso '
                         'Section 3.2.1 and Chapter 9 bullet 5',
        'powerpoint_view': 'not verified (author check)',
    }
    RECORD.write_text(json.dumps(record, indent=2, ensure_ascii=True) + '\n', encoding='ascii')
    print(json.dumps(record['old']), json.dumps(record['new']))
    print(json.dumps(record['zip_entry_comparison']))


if __name__ == '__main__':
    main()
