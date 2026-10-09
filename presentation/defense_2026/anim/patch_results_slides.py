#!/usr/bin/env python3
"""Reduce results slides 33, 34 and 35 to what the spoken script says (D-389).

2026-10-06 (plan declarative-stargazing-phoenix.md, step 1). Raw zip + lxml
edit in the manner of patch_slide12_video.py and
review/personal_review_20261005/patch_deck.py. The deck has no a:tbl; every
table is a grid of text boxes and divider lines, so the edits are text
replacement, run colour changes and shape deletion:

- slide 33: title "Body, unoccluded: model and avatar"; the three bullets
  become model elbow, model wrist and rig; the four mini-table rows become
  model elbow, model wrist, rig elbow, rig wrist (same geometry); the grasp
  distance row and bullet are gone (thesis Chapter 7: model elbow median
  0.36 cm right and 1.08 cm left on the Table 7.4 frame sets);
- slide 34: all six data rows stay; the two intermediate rows (445-489) are
  amber E8B35A and bold, the other four data rows grey BBBBBB (both colours
  are the deck's own, slide 21); the caption names the spoken window;
- slide 35: the left-wrist panel, picture and label are deleted, the right
  picture and its label are centred in the right half, the reference
  sub-line names the right-wrist watch; ppt/media/image50.png is removed
  only when no relationship part names it any more.

Every other zip entry is written with its original bytes and ZipInfo. The
pptx is rewritten in place; the zip-entry comparison (name, CRC) and the old
and new sha256 go to review/results_slides_patch.json. The script refuses to
run twice (slide 33 title check).

Run from the repository root with the thesis Python:

    /home/luo/anaconda3/bin/python -B presentation/defense_2026/anim/patch_results_slides.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path
from zipfile import ZipFile

sys.dont_write_bytecode = True
from lxml import etree as E  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
PPTX = HERE / 'Thesis_Defence_2026.pptx'
RECORD = HERE / 'review' / 'results_slides_patch.json'
S33, S34, S35 = (f'ppt/slides/slide{n}.xml' for n in (33, 34, 35))
S35_RELS = 'ppt/slides/_rels/slide35.xml.rels'
LEFT_IMAGE = 'ppt/media/image50.png'

N = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
     'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
     'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
R_EMBED = f'{{{N["r"]}}}embed'
DOT = '\u00b7'  # the deck's own middle-dot separator (slide 34 caption)

OLD_TITLE_33 = 'Body, unoccluded: model, avatar and grasp distance'
NEW_TITLE_33 = 'Body, unoccluded: model and avatar'
# Colours: E8B35A is the deck's highlight / constrained colour and BBBBBB its
# secondary label grey; both read from ppt/slides/slide21.xml (3 and 5 uses).
AMBER, GREY = 'E8B35A', 'BBBBBB'


# Helpers copied from review/personal_review_20261005/patch_deck.py
# (read, save, sid, shapes, replace_shape_text), reformatted.
def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def read(data, part):
    return E.fromstring(data[part])


def save(data, part, root):
    data[part] = E.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)


def sid(s):
    q = s.find('.//p:cNvPr', N)
    return int(q.get('id')) if q is not None else -1


def shapes(r):
    return r.find('p:cSld/p:spTree', N)


def shape(r, ident):
    found = [s for s in shapes(r) if sid(s) == ident]
    if len(found) != 1:
        raise SystemExit(f'ERROR: shape id {ident} found {len(found)} times')
    return found[0]


def replace_shape_text(r, ident, txt):
    ts = shape(r, ident).findall('.//a:t', N)
    if not ts:
        raise SystemExit(f'ERROR: shape id {ident} has no text')
    ts[0].text = txt
    for t in ts[1:]:
        t.text = ''


def text(r, ident):
    return ''.join(t.text or '' for t in shape(r, ident).findall('.//a:t', N))


def set_runs(r, ident, colour, bold):
    """Colour (and bold flag) of every run of one shape, run formatting kept."""
    rprs = shape(r, ident).findall('.//a:r/a:rPr', N)
    if not rprs:
        raise SystemExit(f'ERROR: shape id {ident} has no runs')
    for rpr in rprs:
        fill = rpr.find('a:solidFill', N)
        if fill is None:
            fill = E.Element(f'{{{N["a"]}}}solidFill')
            ln = rpr.find('a:ln', N)
            if ln is not None:
                ln.addnext(fill)
            else:
                rpr.insert(0, fill)
        for child in list(fill):
            fill.remove(child)
        E.SubElement(fill, f'{{{N["a"]}}}srgbClr', val=colour)
        rpr.set('b', '1' if bold else '0')


def xfrm_off(s):
    return s.find('.//a:xfrm/a:off', N)


def xfrm_ext(s):
    return s.find('.//a:xfrm/a:ext', N)


def patch33(data):
    r = read(data, S33)
    if text(r, 2) != OLD_TITLE_33:
        raise SystemExit(f'ERROR: slide 33 title is {text(r, 2)!r}; already patched or not the expected deck')
    expected = {4: 'Model 0.83 / 2.34 cm', 6: 'Rig 5.3 to 6.8 cm', 8: 'Grasp 15.8 / 14.1 cm',
                15: 'Model wrist', 19: 'Rig elbow', 23: 'Rig wrist', 27: 'Wrist to marker'}
    for k, v in expected.items():
        if text(r, k) != v:
            raise SystemExit(f'ERROR: slide 33 id {k} is {text(r, k)!r}, expected {v!r}')
    # Values: thesis Chapter 7 (model elbow 0.36 / 1.08, model wrist 0.83 / 2.34;
    # Table 7.4 rig elbow 5.3 / 6.1, rig wrist 5.5 / 6.8).
    updates = {2: NEW_TITLE_33,
               4: 'Model elbow 0.36 / 1.08 cm', 6: 'Model wrist 0.83 / 2.34 cm', 8: 'Rig 5.3 to 6.8 cm',
               15: 'Model elbow', 16: '0.36', 17: '1.08',
               19: 'Model wrist', 20: '0.83', 21: '2.34',
               23: 'Rig elbow', 24: '5.3', 25: '6.1',
               27: 'Rig wrist', 28: '5.5', 29: '6.8'}
    for k, v in updates.items():
        replace_shape_text(r, k, v)
    save(data, S33, r)
    return {str(k): v for k, v in updates.items()}


def patch34(data):
    r = read(data, S34)
    rows = {'lower wrist': (17, 21), 'intermediate wrist': (23, 27), 'higher wrist': (29, 33),
            'lower elbow': (35, 39), 'intermediate elbow': (41, 45), 'higher elbow': (47, 51)}
    for name, (a, b) in rows.items():
        label = text(r, a)
        if label.lower().replace(',', '') != name:
            raise SystemExit(f'ERROR: slide 34 row {name} label is {label!r}')
        hi = name.startswith('intermediate')
        if hi and text(r, a + 1) != '445-489':
            raise SystemExit('ERROR: slide 34 intermediate row is not frames 445-489')
        for ident in range(a, b + 1):
            set_runs(r, ident, AMBER if hi else GREY, hi)
    old_caption = f'Right arm {DOT} 45 frames per window {DOT} reference: unmasked reconstruction {DOT} values in cm'
    if text(r, 52) != old_caption:
        raise SystemExit(f'ERROR: slide 34 caption is {text(r, 52)!r}')
    new_caption = old_caption + f' {DOT} spoken: intermediate window 445-489'
    replace_shape_text(r, 52, new_caption)
    save(data, S34, r)
    return {'amber_bold_ids': [i for n, (a, b) in rows.items() if n.startswith('intermediate')
                               for i in range(a, b + 1)],
            'grey_ids': [i for n, (a, b) in rows.items() if not n.startswith('intermediate')
                         for i in range(a, b + 1)],
            'caption_52': new_caption}


def patch35(data):
    r = read(data, S35)
    tree = shapes(r)
    if text(r, 1006) != 'Left wrist' or not text(r, 11).startswith('Frame 1462, left wrist'):
        raise SystemExit('ERROR: slide 35 left-wrist panel or label not as expected')
    left_pic = shape(r, 12)
    right_pic, right_label = shape(r, 10), shape(r, 9)
    if left_pic.find('.//p:cNvPr', N).get('name') != 'Picture 11':
        raise SystemExit('ERROR: slide 35 id 12 is not Picture 11')
    left_rid = left_pic.find('.//a:blip', N).get(R_EMBED)
    for ident in (1006, 1007, 12, 11):
        tree.remove(shape(r, ident))
    replace_shape_text(r, 1003, 'Watch landmark on the right wrist')
    # Centre of the right half: the caption id 26 spans the right content area
    # (x 5687568, cx 6044184); the picture is centred on that span.
    cap_off, cap_ext = xfrm_off(shape(r, 26)), xfrm_ext(shape(r, 26))
    centre = int(cap_off.get('x')) + int(cap_ext.get('cx')) / 2
    new_x = int(centre - int(xfrm_ext(right_pic).get('cx')) / 2)
    if new_x != 7096790:  # value stated in the approved plan
        raise SystemExit(f'ERROR: computed picture x {new_x} differs from the plan value 7096790')
    delta = new_x - int(xfrm_off(right_pic).get('x'))
    xfrm_off(right_pic).set('x', str(new_x))
    label_off = xfrm_off(right_label)
    label_off.set('x', str(int(label_off.get('x')) + delta))
    # the removed picture's relationship goes only when nothing else on the slide uses it
    still = [el for el in r.iter() for k, v in el.attrib.items()
             if k.startswith(f'{{{N["r"]}}}') and v == left_rid]
    if still:
        raise SystemExit(f'ERROR: {left_rid} still referenced on slide 35')
    save(data, S35, r)
    rels = read(data, S35_RELS)
    gone = [q for q in rels if q.get('Id') == left_rid]
    if [q.get('Target') for q in gone] != ['../media/image50.png']:
        raise SystemExit('ERROR: Picture 11 does not point at image50.png')
    rels.remove(gone[0])
    save(data, S35_RELS, rels)
    return {'deleted_ids': [1006, 1007, 12, 11], 'removed_relationship': left_rid,
            'picture_10_x': new_x, 'label_9_x': int(label_off.get('x')), 'x_delta': delta,
            'text_1003': 'Watch landmark on the right wrist'}


def main():
    old_bytes = PPTX.read_bytes()
    with ZipFile(PPTX) as z:
        infos = z.infolist()
        data = {i.filename: z.read(i.filename) for i in infos}
    before = {i.filename: i.CRC for i in infos}
    edits = {'slide33': patch33(data), 'slide34': patch34(data), 'slide35': patch35(data)}
    still_named = sorted(n for n, b in data.items() if n.endswith('.rels') and b'image50.png' in b)
    removed = []
    if not still_named:
        del data[LEFT_IMAGE]
        removed.append(LEFT_IMAGE)

    tmp = PPTX.with_name(PPTX.name + '.tmp')
    with ZipFile(tmp, 'w') as z:
        for info in infos:
            if info.filename in data:
                z.writestr(info, data[info.filename])
    with ZipFile(tmp) as z:
        if z.testzip() is not None:
            raise SystemExit('ERROR: written zip fails its CRC test')
        after = {i.filename: i.CRC for i in z.infolist()}
    changed = sorted(n for n in before if n in after and before[n] != after[n])
    added = sorted(n for n in after if n not in before)
    dropped = sorted(n for n in before if n not in after)
    allowed = {S33, S34, S35, S35_RELS}
    if set(changed) != allowed or added or set(dropped) - {LEFT_IMAGE}:
        tmp.unlink()
        raise SystemExit(f'ERROR: unexpected zip-entry changes: {changed} {added} {dropped}')
    os.replace(tmp, PPTX)
    new_bytes = PPTX.read_bytes()
    media_names = [n for n in after if n.startswith('ppt/media/')]
    record = {
        'purpose': 'Results slides 33-35 reduced to the spoken script (D-389).',
        'generator': str(Path(__file__).resolve().relative_to(ROOT)),
        'generator_sha256': sha(Path(__file__).read_bytes()),
        'pptx': str(PPTX.relative_to(ROOT)),
        'old': {'sha256': sha(old_bytes), 'bytes': len(old_bytes), 'entries': len(before)},
        'new': {'sha256': sha(new_bytes), 'bytes': len(new_bytes), 'entries': len(after)},
        'zip_entry_comparison': {'changed_crc': changed, 'added': added, 'removed': dropped,
                                 'unchanged_entries': len(before) - len(changed) - len(dropped)},
        'left_image_still_named_by': still_named,
        'media_counts_after': {'total': len(media_names),
                               'mp4': sum(n.endswith('.mp4') for n in media_names),
                               'png': sum(n.endswith('.png') for n in media_names)},
        'edits': edits,
        'colours_source': 'ppt/slides/slide21.xml (E8B35A highlight, BBBBBB secondary label)',
        'thesis_source': 'writing/v9/Chapter_7_Evaluation.docx (model elbow 0.36 / 1.08 cm; '
                         'model wrist 0.83 / 2.34 cm; Table 7.4 rig 5.3 / 6.1 and 5.5 / 6.8 cm)',
        'powerpoint_view': 'not verified (author check)',
    }
    RECORD.write_text(json.dumps(record, indent=2, ensure_ascii=True) + '\n', encoding='ascii')
    print(json.dumps(record['old']), json.dumps(record['new']))
    print(json.dumps(record['zip_entry_comparison']))
    print(json.dumps(record['media_counts_after']))


if __name__ == '__main__':
    main()
