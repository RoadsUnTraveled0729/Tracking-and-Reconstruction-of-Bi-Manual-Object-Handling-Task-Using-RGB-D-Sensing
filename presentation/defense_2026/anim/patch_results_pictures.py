#!/usr/bin/env python3
"""Add the two results pictures to slides 33 and 34 (D-390).

2026-10-06 (plan declarative-stargazing-phoenix.md, step 3, assumptions A1,
A2, A5). Raw zip + lxml edit in the manner of patch_results_slides.py and
patch_slide12_video.py; every moved or resized shape keeps its run formatting
(only a:off and a:ext change):

- slide 33: the Unity video (id 30) moves right so its right edge meets the
  right edge of the caption id 31 (x 8644432 EMU = 9.454 in, plan "x 9.45");
  the FK still media/p33_fk_overlay.png goes in as a new picture (id 35) at
  x 6.0, y 1.2 in, 3.3 in wide at its own 4:3 aspect (3.3 x 2.475 in); a
  label (id 36, a copy of caption id 31: 16 pt DejaVu Sans) sits under it at
  y 3.75 in, 3.3 in wide, as ONE paragraph (master decision 4, 2026-10-06);
- slide 34 (master decisions 3, 2026-10-06): the Frames column is deleted
  (header id 12, cells 18, 24, 30, 36, 42, 48); the remaining grid cells
  (ids 11, 13-15 and the cells among 17-51) get sz=1400 on every a:rPr
  (colours and bold kept) and an explicit column layout from x 0.5 in to
  7.6 in (COLUMNS below); the header bar id 9 and the grid lines ids 10, 16,
  22, 28, 34, 40, 46 are set to 7.1 in wide; caption id 52, the footer rule
  id 53 and the tiles 1002-1004 keep their geometry; y and heights are
  unchanged; the figure media/p34_masked_comparison.png goes in as a new
  picture (id 1005) at x 7.8, y 2.35 in, 5.0 x 3.85 in;
- two new parts ppt/media/p33_fk_overlay.png and
  ppt/media/p34_masked_comparison.png, one image relationship each on the two
  slides; [Content_Types].xml already has a png Default.

Every other zip entry is written with its original bytes and ZipInfo. The
zip-entry comparison (name, CRC) and old and new sha256 go to
review/results_pictures_patch.json. The script refuses to run twice.

Run from the repository root with the thesis Python:

    /home/luo/anaconda3/bin/python -B presentation/defense_2026/anim/patch_results_pictures.py
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

sys.dont_write_bytecode = True
from lxml import etree as E  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
PPTX = HERE / 'Thesis_Defence_2026.pptx'
RECORD = HERE / 'review' / 'results_pictures_patch.json'
S33, S34 = 'ppt/slides/slide33.xml', 'ppt/slides/slide34.xml'
R33, R34 = 'ppt/slides/_rels/slide33.xml.rels', 'ppt/slides/_rels/slide34.xml.rels'
PIC33 = HERE / 'media' / 'p33_fk_overlay.png'
PIC34 = HERE / 'media' / 'p34_masked_comparison.png'
PART33, PART34 = 'ppt/media/p33_fk_overlay.png', 'ppt/media/p34_masked_comparison.png'
PROV = {PIC33: HERE / 'media' / 'provenance' / 'p33_fk_overlay.json',
        PIC34: HERE / 'media' / 'provenance' / 'p34_masked_comparison.json'}

N = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
     'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
     'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
PR = 'http://schemas.openxmlformats.org/package/2006/relationships'
IMAGE_REL = N['r'] + '/image'
EMU = 914400

# Geometry (approved plan assumptions A1 and A2), in EMU.
S33_STILL = dict(x=int(6.0 * EMU), y=int(1.2 * EMU), cx=int(3.3 * EMU))   # cy from 4:3 below
S33_LABEL_Y = int(3.75 * EMU)
S33_LABEL = 'Python FK on the RGB frame: green measured, red and blue FK arms'   # master decision 4
S34_FIG = dict(x=int(7.8 * EMU), y=int(2.35 * EMU), cx=int(5.0 * EMU), cy=int(3.85 * EMU))
S34_GRID_RIGHT = int(7.6 * EMU)
GRID_LEFT = 457200                         # header bar id 9 x (0.5 in), read below
GRID_WIDTH = S34_GRID_RIGHT - GRID_LEFT    # 7.1 in: bar id 9 and the grid lines
GRID_LINES = (9, 10, 16, 22, 28, 34, 40, 46)
FRAMES_COL = (12, 18, 24, 30, 36, 42, 48)  # deleted: header 'Frames' and its six cells
# Rows: header ids 11-15, data rows start at 17, 23, ..., 47 (five cells each, Frames second).
ROWS = [(11, 13, 14, 15)] + [(b, b + 2, b + 3, b + 4) for b in range(17, 48, 6)]
CELL_SZ = '1400'                           # master decision 3: 14 pt grid
# Column widths in inches, left to right (Motion / joint, Hold-last, Direction memory,
# Object-assisted), sum 7.1 in. Master decision 3 named 2.5 / 1.4 / 1.8 / 1.4; at 14 pt
# DejaVu Sans 'Object-assisted' measures 1.50 in and 'Direction memory' 1.75 in, and the
# bold amber 'Intermediate, elbow' 2.22 in (PIL ImageFont.getlength on DejaVuSans.ttf and
# DejaVuSans-Bold.ttf), so the last two headers cannot sit on one line in 1.4 / 1.8 in.
# Minimum widths with the 0.1 in inset and 0.05 in spare: 2.37 / 1.01 / 1.90 / 1.65 in.
# Worker deviation (reported, UNCERTAIN): 2.45 / 1.05 / 1.95 / 1.65 in, the 0.16 in left
# over spread over the first three columns (fit check in patch34()).
COLUMNS = (2.45, 1.05, 1.95, 1.65)
CELL_INSET = 0.1                           # in; the original grid used 0.187 in (judgement)
FONT_FILE = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'   # fc-match 'DejaVu Sans'
FONT_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'   # fc-match 'DejaVu Sans:bold'
FIT_SPARE = 0.05                           # in; minimum slack after the text (judgement)


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def read(data, part):
    return E.fromstring(data[part])


def dump(root):
    return E.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)


def sid(s):
    q = s.find('.//p:cNvPr', N)
    return int(q.get('id')) if q is not None else -1


def tree_of(r):
    return r.find('p:cSld/p:spTree', N)


def shape(r, ident):
    found = [s for s in tree_of(r) if sid(s) == ident]
    if len(found) != 1:
        raise SystemExit(f'ERROR: shape id {ident} found {len(found)} times')
    return found[0]


def off(s):
    return s.find('.//a:xfrm/a:off', N)


def ext(s):
    return s.find('.//a:xfrm/a:ext', N)


def geom(s):
    o, e = off(s), ext(s)
    return [int(o.get('x')), int(o.get('y')), int(e.get('cx')), int(e.get('cy'))]


def png_size(blob):
    if blob[:8] != b'\x89PNG\r\n\x1a\n':
        raise SystemExit('ERROR: not a PNG')
    return int.from_bytes(blob[16:20], 'big'), int.from_bytes(blob[20:24], 'big')


def add_rel(rels, target):
    used = {int(q.get('Id')[3:]) for q in rels}
    rid = f'rId{next(i for i in range(1, 1000) if i not in used)}'
    E.SubElement(rels, f'{{{PR}}}Relationship', Id=rid, Type=IMAGE_REL, Target=target)
    return rid


def picture(ident, name, descr, rid, x, y, cx, cy):
    P, A, R = (f'{{{N[k]}}}' for k in ('p', 'a', 'r'))
    pic = E.Element(P + 'pic', nsmap={'p': N['p'], 'a': N['a'], 'r': N['r']})
    nv = E.SubElement(pic, P + 'nvPicPr')
    E.SubElement(nv, P + 'cNvPr', id=str(ident), name=name, descr=descr)
    E.SubElement(E.SubElement(nv, P + 'cNvPicPr'), A + 'picLocks', noChangeAspect='1')
    E.SubElement(nv, P + 'nvPr')
    bf = E.SubElement(pic, P + 'blipFill')
    E.SubElement(bf, A + 'blip', {R + 'embed': rid})
    E.SubElement(E.SubElement(bf, A + 'stretch'), A + 'fillRect')
    sp = E.SubElement(pic, P + 'spPr')
    xf = E.SubElement(sp, A + 'xfrm')
    E.SubElement(xf, A + 'off', x=str(x), y=str(y))
    E.SubElement(xf, A + 'ext', cx=str(cx), cy=str(cy))
    E.SubElement(E.SubElement(sp, A + 'prstGeom', prst='rect'), A + 'avLst')
    return pic


def patch33(data):
    r = read(data, S33)
    if any(sid(s) in (35, 36) for s in tree_of(r)):
        raise SystemExit('ERROR: slide 33 already has ids 35/36; patched before')
    video, caption = shape(r, 30), shape(r, 31)
    if not video.find('.//p:cNvPr', N).get('name').startswith('p47-Fresh_Unity_Handover'):
        raise SystemExit('ERROR: slide 33 id 30 is not the Unity handover video')
    v0 = geom(video)
    c = geom(caption)
    new_vx = c[0] + c[2] - v0[2]               # right edge = caption right edge
    off(video).set('x', str(new_vx))
    w, h = png_size(data[PART33])
    cy = round(S33_STILL['cx'] * h / w)
    rels = read(data, R33)
    rid = add_rel(rels, '../media/p33_fk_overlay.png')
    pic = picture(35, 'p33_fk_overlay.png',
                  'Python forward kinematics drawn over the RGB frame: green measured landmarks, '
                  'red and blue FK arms', rid, S33_STILL['x'], S33_STILL['y'], S33_STILL['cx'], cy)
    label = copy.deepcopy(caption)
    cnv = label.find('.//p:cNvPr', N)
    cnv.set('id', '36')
    cnv.set('name', 'TextBox 35')
    off(label).set('x', str(S33_STILL['x']))
    off(label).set('y', str(S33_LABEL_Y))
    ext(label).set('cx', str(S33_STILL['cx']))
    paras = label.findall('.//p:txBody/a:p', N)
    if len(paras) != 1 or len(paras[0].findall('a:r', N)) != 1:
        raise SystemExit('ERROR: caption id 31 is not one paragraph with one run')
    paras[0].find('a:r/a:t', N).text = S33_LABEL
    tree = tree_of(r)
    caption.addprevious(pic)
    caption.addprevious(label)
    data[S33], data[R33] = dump(r), dump(rels)
    return {'video_30': {'old': v0, 'new': geom(video)},
            'picture_35': geom(pic), 'picture_rid': rid, 'png_px': [w, h],
            'label_36': {'geometry': geom(label), 'text': S33_LABEL, 'formatting': 'copy of caption id 31'},
            'shape_count': len(tree)}


def patch34(data):
    r = read(data, S34)
    if any(sid(s) == 1005 for s in tree_of(r)):
        raise SystemExit('ERROR: slide 34 already has id 1005; patched before')
    bar = shape(r, 9)
    g = geom(bar)
    if g[0] != GRID_LEFT or g[2] != 11274552:
        raise SystemExit(f'ERROR: header bar id 9 geometry {g} not as expected')
    if abs(sum(COLUMNS) * EMU - GRID_WIDTH) > 1:
        raise SystemExit(f'ERROR: COLUMNS sum {sum(COLUMNS)} in != grid width')
    from PIL import ImageFont
    font = {False: ImageFont.truetype(FONT_FILE, int(CELL_SZ)),   # size in 1/100 pt -> width / 7200 in
            True: ImageFont.truetype(FONT_BOLD, int(CELL_SZ))}
    tree = tree_of(r)
    moved, removed, fit = {}, {}, {}
    for ident in FRAMES_COL:
        sp = shape(r, ident)
        removed[str(ident)] = ''.join(t.text or '' for t in sp.findall('.//a:t', N))
        tree.remove(sp)
    for ident in GRID_LINES:
        sp = shape(r, ident)
        old = geom(sp)
        if old[0] != GRID_LEFT:
            raise SystemExit(f'ERROR: grid line {ident} does not start at the grid left edge')
        ext(sp).set('cx', str(GRID_WIDTH))
        moved[str(ident)] = {'old': old, 'new': geom(sp)}
    edges = [GRID_LEFT]
    for w_in in COLUMNS:
        edges.append(edges[-1] + round(w_in * EMU))
    edges[-1] = S34_GRID_RIGHT
    for row in ROWS:
        for col, ident in enumerate(row):
            sp = shape(r, ident)
            old = geom(sp)
            x = edges[col] + round(CELL_INSET * EMU)
            cx = edges[col + 1] - x
            off(sp).set('x', str(x))
            ext(sp).set('cx', str(cx))
            rprs = sp.findall('.//a:rPr', N)
            if not rprs:
                raise SystemExit(f'ERROR: cell {ident} has no a:rPr')
            for rp in rprs:
                rp.set('sz', CELL_SZ)
            text = ''.join(t.text or '' for t in sp.findall('.//a:t', N))
            bold = any(rp.get('b') == '1' for rp in rprs)
            text_in = font[bold].getlength(text) / 7200
            slack = cx / EMU - text_in
            fit[str(ident)] = {'text': text, 'bold': bold, 'text_in': round(text_in, 3),
                               'slack_in': round(slack, 3)}
            if slack < FIT_SPARE:
                raise SystemExit(f'ERROR: cell {ident} {text!r} does not fit: {fit[str(ident)]}')
            moved[str(ident)] = {'old': old, 'new': geom(sp)}
    right = max(v['new'][0] + v['new'][2] for v in moved.values())
    if abs(right - S34_GRID_RIGHT) > 1:
        raise SystemExit(f'ERROR: grid right edge {right} != {S34_GRID_RIGHT}')
    if geom(shape(r, 52)) != [457200, 5742432, 11274552, 402336]:
        raise SystemExit('ERROR: caption id 52 geometry changed')
    w, h = png_size(data[PART34])
    if abs(w / h - S34_FIG['cx'] / S34_FIG['cy']) > 1e-3:
        raise SystemExit(f'ERROR: figure aspect {w}x{h} differs from the slot')
    rels = read(data, R34)
    rid = add_rel(rels, '../media/p34_masked_comparison.png')
    pic = picture(1005, 'p34_masked_comparison.png',
                  'Controlled removal, frames 445-489: removed right elbow and wrist, the three recovered '
                  'chains on the RGB frame, and the error per frame', rid, **S34_FIG)
    shape(r, 53).addprevious(pic)
    data[S34], data[R34] = dump(r), dump(rels)
    return {'columns_in': list(COLUMNS), 'column_edges_emu': edges, 'cell_inset_in': CELL_INSET,
            'cell_sz': CELL_SZ, 'grid_right_emu': right, 'removed_frames_column': removed,
            'moved': moved, 'text_fit': fit, 'picture_1005': geom(pic),
            'picture_rid': rid, 'png_px': [w, h],
            'unchanged': 'caption id 52, footer rule id 53, tiles 1002-1004, title id 2, footer ids 54-55'}


def main():
    for pic, prov in PROV.items():
        if json.loads(prov.read_text())['sha256']['png'] != sha(pic.read_bytes()):
            raise SystemExit(f'ERROR: {pic.name} differs from its provenance record')
    old_bytes = PPTX.read_bytes()
    with ZipFile(PPTX) as z:
        infos = z.infolist()
        data = {i.filename: z.read(i.filename) for i in infos}
    before = {i.filename: i.CRC for i in infos}
    for part in (PART33, PART34):
        if part in data:
            raise SystemExit(f'ERROR: {part} already in the package; patched before')
    data[PART33], data[PART34] = PIC33.read_bytes(), PIC34.read_bytes()
    edits = {'slide33': patch33(data), 'slide34': patch34(data)}

    tmp = PPTX.with_name(PPTX.name + '.tmp')
    with ZipFile(tmp, 'w') as z:
        for info in infos:
            z.writestr(info, data[info.filename])
        for part in (PART33, PART34):
            info = ZipInfo(part, date_time=infos[0].date_time)
            info.compress_type = ZIP_DEFLATED
            z.writestr(info, data[part])
    with ZipFile(tmp) as z:
        if z.testzip() is not None:
            raise SystemExit('ERROR: written zip fails its CRC test')
        after = {i.filename: i.CRC for i in z.infolist()}
    changed = sorted(n for n in before if n in after and before[n] != after[n])
    added = sorted(n for n in after if n not in before)
    dropped = sorted(n for n in before if n not in after)
    if set(changed) != {S33, S34, R33, R34} or set(added) != {PART33, PART34} or dropped:
        tmp.unlink()
        raise SystemExit(f'ERROR: unexpected zip-entry changes: {changed} {added} {dropped}')
    os.replace(tmp, PPTX)
    new_bytes = PPTX.read_bytes()
    media_names = [n for n in after if n.startswith('ppt/media/')]
    record = {
        'purpose': 'Slide 33 FK still and slide 34 masked-comparison figure added (D-390).',
        'generator': str(Path(__file__).resolve().relative_to(ROOT)),
        'generator_sha256': sha(Path(__file__).read_bytes()),
        'pptx': str(PPTX.relative_to(ROOT)),
        'old': {'sha256': sha(old_bytes), 'bytes': len(old_bytes), 'entries': len(before)},
        'new': {'sha256': sha(new_bytes), 'bytes': len(new_bytes), 'entries': len(after)},
        'zip_entry_comparison': {'changed_crc': changed, 'added': added, 'removed': dropped,
                                 'unchanged_entries': len(before) - len(changed)},
        'media_counts_after': {'total': len(media_names),
                               'mp4': sum(n.endswith('.mp4') for n in media_names),
                               'png': sum(n.endswith('.png') for n in media_names)},
        'pictures': {PART33: sha(data[PART33]), PART34: sha(data[PART34])},
        'edits': edits,
        'powerpoint_view': 'not verified (author check)',
    }
    RECORD.write_text(json.dumps(record, indent=2, ensure_ascii=True) + '\n', encoding='ascii')
    print(json.dumps(record['old']), json.dumps(record['new']))
    print(json.dumps(record['zip_entry_comparison']))
    print(json.dumps(record['media_counts_after']))


if __name__ == '__main__':
    main()
