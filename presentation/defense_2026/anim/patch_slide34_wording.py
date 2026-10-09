#!/usr/bin/env python3
"""Slide 34 wording, columns and three-case figure (D-392).

2026-10-06 (plan declarative-stargazing-phoenix.md, Milestone B). Raw zip +
lxml edit with the helpers of patch_results_pictures.py; every changed text
keeps its run formatting (only a:t, a:off and a:ext change):

- row labels ids 17/23/29 and 35/41/47 (wrist rows, then elbow rows, in the
  order lower, intermediate, higher motion) become "Wrist travel <v> cm,
  wrist|elbow" with v = 0.6, 2.8, 5.1, the reference wrist excursion of the
  three windows in thesis Table 7.5 (writing/v9/Chapter_7_Evaluation.docx,
  rows Lower 490-534 0.6, Intermediate 445-489 2.8, Higher 557-601 5.1);
- header id 11 "Motion / joint" -> "Window / joint";
- the column headers keep the method names: the deck's case letters (slides
  19-23) are Case A missing wrist (direction memory), Case B grasping wrist
  (object), Case C missing elbow (two lengths + direction memory), and the
  hold-last fallback (slide 24) has no letter, so the plan's alternative
  applies: tile 1003 "Three recovery methods" -> "Three recovery cases";
- tile 1002 "45-frame windows" -> "45-frame windows, slow motion";
- caption id 52 -> the plan text;
- the picture part ppt/media/p34_masked_comparison.png gets the bytes of the
  regenerated three-case figure (same 1500 x 1155 px aspect); picture id
  1005 shrinks to 4.6 in wide at its own aspect, top kept at y 2.35 in and its
  right edge set on the caption / footer-rule right edge (12.83 in), and its
  descr is rewritten for the new figure;
- the grid (header bar id 9, lines, cells) is relaid from x 0.5 in to 0.1 in
  left of the figure, columns COLUMNS below, so that no cell wraps at 14 pt
  (PIL measurement as in patch_results_pictures.py).

Every other zip entry is written with its original bytes and ZipInfo. The
zip-entry comparison and old and new sha256 go to
review/slide34_wording_patch.json. The script refuses to run twice.

Run from the repository root with the thesis Python:

    /home/luo/anaconda3/bin/python -B presentation/defense_2026/anim/patch_slide34_wording.py
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
import patch_results_pictures as H  # noqa: E402  (helpers: read, dump, shape, geom, off, ext, ...)

N, EMU = H.N, H.EMU
HERE, ROOT, PPTX = H.HERE, H.ROOT, H.PPTX
RECORD = HERE / 'review' / 'slide34_wording_patch.json'
S34, R34, PART34, PIC34 = H.S34, H.R34, H.PART34, H.PIC34
PROV34 = HERE / 'media' / 'provenance' / 'p34_masked_comparison.json'
MIDDOT = '\u00b7'

# Text replacements: id -> (expected current text, new text).
TRAVEL = ('0.6', '2.8', '5.1')   # thesis Table 7.5, reference wrist excursion (cm)
TEXTS = {
    11: ('Motion / joint', 'Window / joint'),
    17: ('Lower, wrist', f'Wrist travel {TRAVEL[0]} cm, wrist'),
    23: ('Intermediate, wrist', f'Wrist travel {TRAVEL[1]} cm, wrist'),
    29: ('Higher, wrist', f'Wrist travel {TRAVEL[2]} cm, wrist'),
    35: ('Lower, elbow', f'Wrist travel {TRAVEL[0]} cm, elbow'),
    41: ('Intermediate, elbow', f'Wrist travel {TRAVEL[1]} cm, elbow'),
    47: ('Higher, elbow', f'Wrist travel {TRAVEL[2]} cm, elbow'),
    1002: ('45-frame windows', '45-frame windows, slow motion'),
    1003: ('Three recovery methods', 'Three recovery cases'),
    52: (f'Right arm {MIDDOT} 45 frames per window {MIDDOT} reference: unmasked reconstruction '
         f'{MIDDOT} values in cm {MIDDOT} spoken: intermediate window 445-489',
         f'Right arm {MIDDOT} one slow recording {MIDDOT} 45 frames per window {MIDDOT} '
         f'reference: unmasked reconstruction {MIDDOT} cm {MIDDOT} spoken: wrist travel 2.8 cm'),
}
OLD_PNG_SHA = '2181352bca9c8998eefbb7b559f996b3e45441157eed71c7dee38505afcea00a'  # D-390 figure
OLD_FIG = [7132320, 2148840, 4572000, 3520440]   # id 1005 as D-390 placed it (7.8, 2.35, 5.0 x 3.85 in)
FIG_CX = int(4.6 * EMU)        # plan Milestone B: the figure may shrink to 4.6 in wide
FIG_GAP = int(0.1 * EMU)       # in between grid right edge and figure (D-390 used 0.2; judgement)
FIG_DESCR = ('Controlled removal, window 445-489, frame 489: the three recovery cases side by side '
             '(hold last, direction memory, object-assisted), white reference chain, removed elbow '
             'and wrist ringed in red, each case\'s recovered chain and its window wrist median')
# Column widths in inches (Window / joint, Hold-last, Direction memory, Object-assisted).
# Minimum = text + 0.1 in inset + 0.05 in spare, PIL getlength at 14 pt DejaVu Sans:
# bold 'Wrist travel 2.8 cm, elbow' 2.886 in -> 3.036; 'Hold-last' 0.864 -> 1.014;
# 'Direction memory' 1.753 -> 1.903; 'Object-assisted' 1.500 -> 1.650; sum 7.603 in.
# Grid width = 12.83 - 4.6 - 0.1 - 0.5 = 7.63 in; the 0.027 in left over spread (judgement).
COLUMNS = (3.04, 1.02, 1.91, 1.66)
ROWS = H.ROWS


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def text_of(sp):
    return ''.join(t.text or '' for t in sp.findall('.//a:t', N))


def set_text(sp, old, new):
    runs = sp.findall('.//p:txBody/a:p/a:r', N)
    if len(sp.findall('.//p:txBody/a:p', N)) != 1 or len(runs) != 1:
        raise SystemExit(f'ERROR: shape {H.sid(sp)} is not one paragraph with one run')
    cur = runs[0].find('a:t', N).text
    if cur != old:
        raise SystemExit(f'ERROR: shape {H.sid(sp)} text {cur!r} != expected {old!r}; patched before?')
    runs[0].find('a:t', N).text = new


def patch(data):
    r = H.read(data, S34)
    texts = {}
    for ident, (old, new) in TEXTS.items():
        set_text(H.shape(r, ident), old, new)
        texts[str(ident)] = {'old': old, 'new': new}

    # Figure geometry: 4.6 in wide at the PNG aspect, right edge on the caption right edge.
    pic = H.shape(r, 1005)
    if H.geom(pic) != OLD_FIG:
        raise SystemExit(f'ERROR: picture 1005 geometry {H.geom(pic)} != {OLD_FIG}')
    cap = H.geom(H.shape(r, 52))
    w, h = H.png_size(data[PART34])
    fig_x = cap[0] + cap[2] - FIG_CX
    fig_cy = round(FIG_CX * h / w)
    H.off(pic).set('x', str(fig_x))
    H.ext(pic).set('cx', str(FIG_CX))
    H.ext(pic).set('cy', str(fig_cy))
    pic.find('.//p:cNvPr', N).set('descr', FIG_DESCR)
    grid_right = fig_x - FIG_GAP
    grid_width = grid_right - H.GRID_LEFT
    if abs(sum(COLUMNS) * EMU - grid_width) > 1:
        raise SystemExit(f'ERROR: COLUMNS sum {sum(COLUMNS)} in != grid width {grid_width / EMU} in')

    from PIL import ImageFont
    font = {False: ImageFont.truetype(H.FONT_FILE, int(H.CELL_SZ)),
            True: ImageFont.truetype(H.FONT_BOLD, int(H.CELL_SZ))}
    moved, fit = {}, {}
    for ident in H.GRID_LINES:
        sp = H.shape(r, ident)
        old = H.geom(sp)
        if old[0] != H.GRID_LEFT:
            raise SystemExit(f'ERROR: grid line {ident} does not start at the grid left edge')
        H.ext(sp).set('cx', str(grid_width))
        moved[str(ident)] = {'old': old, 'new': H.geom(sp)}
    edges = [H.GRID_LEFT]
    for w_in in COLUMNS:
        edges.append(edges[-1] + round(w_in * EMU))
    edges[-1] = grid_right
    for row in ROWS:
        for col, ident in enumerate(row):
            sp = H.shape(r, ident)
            old = H.geom(sp)
            x = edges[col] + round(H.CELL_INSET * EMU)
            cx = edges[col + 1] - x
            H.off(sp).set('x', str(x))
            H.ext(sp).set('cx', str(cx))
            rprs = sp.findall('.//a:rPr', N)
            if any(rp.get('sz') != H.CELL_SZ for rp in rprs):
                raise SystemExit(f'ERROR: cell {ident} is not at 14 pt')
            text = text_of(sp)
            bold = any(rp.get('b') == '1' for rp in rprs)
            text_in = font[bold].getlength(text) / 7200
            slack = cx / EMU - text_in
            fit[str(ident)] = {'text': text, 'bold': bold, 'text_in': round(text_in, 3),
                               'cell_in': round(cx / EMU, 3), 'slack_in': round(slack, 3)}
            if slack < H.FIT_SPARE:
                raise SystemExit(f'ERROR: cell {ident} {text!r} does not fit: {fit[str(ident)]}')
            moved[str(ident)] = {'old': old, 'new': H.geom(sp)}
    right = max(v['new'][0] + v['new'][2] for v in moved.values())
    if abs(right - grid_right) > 1:
        raise SystemExit(f'ERROR: grid right edge {right} != {grid_right}')
    for ident in (52, 53, 2, 54, 55, 1004):
        moved.setdefault(str(ident), {'unchanged': H.geom(H.shape(r, ident))})

    # Long texts outside the grid: report their measured width (wrapping allowed, recorded).
    f22 = ImageFont.truetype(H.FONT_FILE, 2200)
    f16 = ImageFont.truetype(H.FONT_FILE, 1600)
    wraps = {
        '1002': {'text_in': round(f22.getlength(TEXTS[1002][1]) / 7200, 3),
                 'box_in': round(H.geom(H.shape(r, 1002))[2] / EMU, 3), 'pt': 22},
        '1003': {'text_in': round(f22.getlength(TEXTS[1003][1]) / 7200, 3),
                 'box_in': round(H.geom(H.shape(r, 1003))[2] / EMU, 3), 'pt': 22},
        '52': {'text_in': round(f16.getlength(TEXTS[52][1]) / 7200, 3),
               'old_text_in': round(f16.getlength(TEXTS[52][0]) / 7200, 3),
               'box_in': round(cap[2] / EMU, 3), 'pt': 16},
    }
    data[S34] = H.dump(r)
    return {'texts': texts, 'columns_in': list(COLUMNS), 'column_edges_emu': edges,
            'grid_right_emu': grid_right, 'grid_width_in': round(grid_width / EMU, 4),
            'cell_inset_in': H.CELL_INSET, 'fit_spare_in': H.FIT_SPARE, 'cell_sz': H.CELL_SZ,
            'text_fit': fit, 'measured_wraps': wraps,
            'picture_1005': {'old': OLD_FIG, 'new': H.geom(pic), 'png_px': [w, h], 'descr': FIG_DESCR},
            'geometry': moved}


def main():
    prov = json.loads(PROV34.read_text())
    new_png = PIC34.read_bytes()
    if prov['sha256']['png'] != sha(new_png):
        raise SystemExit('ERROR: p34_masked_comparison.png differs from its provenance record')
    if prov.get('mode') != 'three-case':
        raise SystemExit('ERROR: provenance does not describe the three-case figure')
    old_bytes = PPTX.read_bytes()
    with ZipFile(PPTX) as z:
        infos = z.infolist()
        data = {i.filename: z.read(i.filename) for i in infos}
    before = {i.filename: i.CRC for i in infos}
    old_part = sha(data[PART34])
    if old_part == sha(new_png):
        raise SystemExit('ERROR: the package already holds the three-case figure; patched before')
    if old_part != OLD_PNG_SHA:
        raise SystemExit(f'ERROR: package figure {old_part} is not the D-390 figure')
    users = [n for n in data if n.endswith('.rels') and b'p34_masked_comparison.png' in data[n]]
    if users != [R34]:
        raise SystemExit(f'ERROR: figure part referenced by {users}, expected only {R34}')
    data[PART34] = new_png
    edits = patch(data)

    tmp = PPTX.with_name(PPTX.name + '.tmp')
    with ZipFile(tmp, 'w') as z:
        for info in infos:
            z.writestr(info, data[info.filename])
    with ZipFile(tmp) as z:
        if z.testzip() is not None:
            tmp.unlink()
            raise SystemExit('ERROR: written zip fails its CRC test')
        after = {i.filename: i.CRC for i in z.infolist()}
    changed = sorted(n for n in before if n in after and before[n] != after[n])
    added = sorted(n for n in after if n not in before)
    dropped = sorted(n for n in before if n not in after)
    if not set(changed) <= {S34, R34, PART34} or S34 not in changed or PART34 not in changed \
            or added or dropped:
        tmp.unlink()
        raise SystemExit(f'ERROR: unexpected zip-entry changes: {changed} {added} {dropped}')
    os.replace(tmp, PPTX)
    new_bytes = PPTX.read_bytes()
    record = {
        'purpose': 'Slide 34 row labels by wrist travel, case wording, caption and three-case figure (D-392).',
        'generator': str(Path(__file__).resolve().relative_to(ROOT)),
        'generator_sha256': sha(Path(__file__).read_bytes()),
        'helpers': str(Path(H.__file__).resolve().relative_to(ROOT)),
        'pptx': str(PPTX.relative_to(ROOT)),
        'old': {'sha256': sha(old_bytes), 'bytes': len(old_bytes), 'entries': len(before)},
        'new': {'sha256': sha(new_bytes), 'bytes': len(new_bytes), 'entries': len(after)},
        'zip_entry_comparison': {'changed_crc': changed, 'added': added, 'removed': dropped,
                                 'unchanged_entries': len(before) - len(changed)},
        'picture_part': {'part': PART34, 'old_sha256': old_part, 'new_sha256': sha(new_png),
                         'provenance': str(PROV34.relative_to(ROOT))},
        'case_letters': {'source': 'slides 19, 21-24 titles',
                         'found': {'A': 'missing wrist: elbow + direction memory',
                                   'B': 'grasping wrist: tracked object + stored offset',
                                   'C': 'missing elbow: two lengths + direction memory',
                                   'hold last': 'no letter (slide 24, no support)'},
                         'decision': 'column headers keep the method names; tile 1003 says cases'},
        'travel_source': 'writing/v9/Chapter_7_Evaluation.docx Table 7.5 (0.6, 2.8, 5.1 cm)',
        'edits': edits,
        'powerpoint_view': 'not verified (author check)',
    }
    RECORD.write_text(json.dumps(record, indent=2, ensure_ascii=True) + '\n', encoding='ascii')
    print(json.dumps(record['old']), json.dumps(record['new']))
    print(json.dumps(record['zip_entry_comparison']))


if __name__ == '__main__':
    main()
