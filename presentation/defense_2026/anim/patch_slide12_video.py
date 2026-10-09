#!/usr/bin/env python3
"""Replace the static figure on slide 12 with the chain-growth film (D-387).

2026-10-06 (plan declarative-stargazing-phoenix.md, step 2). Raw zip + lxml
edit in the manner of review/personal_review_20261005/patch_deck.py:

- slide 13's movie shape (p:pic with a:videoFile r:link and p14:media r:embed
  to the same mp4, blip to a poster PNG) and its p:timing block (video node,
  vol 80000, delay 0) are the template;
- slide 12's "Picture 10" (id 11) is replaced in place by that movie shape at
  the picture's own geometry, pointing at media/p12_chain_growth.mp4 and the
  poster media/p12_chain_growth_poster.png, added as new parts
  ppt/media/p12_chain_growth.mp4 and ppt/media/p12_chain_growth.png;
- ppt/media/image10.png is removed only when no relationship part names it;
- [Content_Types].xml is left as is (mp4 and png Defaults exist);
- every other zip entry is written with its original bytes and ZipInfo.

The pptx is rewritten in place; the zip-entry comparison (name, CRC) and the
old and new sha256 go to review/slide12_patch.json.

Run from the repository root with the thesis Python:

    /home/luo/anaconda3/bin/python -B presentation/defense_2026/anim/patch_slide12_video.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from copy import deepcopy
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

sys.dont_write_bytecode = True
from lxml import etree as E  # noqa: E402

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
PPTX = HERE / 'Thesis_Defence_2026.pptx'
MOVIE = HERE / 'media' / 'p12_chain_growth.mp4'
POSTER = HERE / 'media' / 'p12_chain_growth_poster.png'
PROVENANCE = HERE / 'media' / 'provenance' / 'p12_chain_growth.json'
RECORD = HERE / 'review' / 'slide12_patch.json'
MEDIA_PART = 'ppt/media/p12_chain_growth.mp4'
POSTER_PART = 'ppt/media/p12_chain_growth.png'
OLD_IMAGE = 'ppt/media/image10.png'
SLIDE, SLIDE_RELS = 'ppt/slides/slide12.xml', 'ppt/slides/_rels/slide12.xml.rels'
TEMPLATE, TEMPLATE_RELS = 'ppt/slides/slide13.xml', 'ppt/slides/_rels/slide13.xml.rels'
PICTURE_ID = '11'          # slide 12 "Picture 10" (exploration 2026-10-06)

N = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
     'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
     'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
     'p14': 'http://schemas.microsoft.com/office/powerpoint/2010/main'}
PR = 'http://schemas.openxmlformats.org/package/2006/relationships'
REL = {'media': 'http://schemas.microsoft.com/office/2007/relationships/media',
       'video': N['r'] + '/video', 'image': N['r'] + '/image'}
R_ID, R_LINK, R_EMBED = (f'{{{N["r"]}}}id', f'{{{N["r"]}}}link', f'{{{N["r"]}}}embed')


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def xml(blob):
    return E.fromstring(blob)


def dump(root):
    return E.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)


def main():
    old_bytes = PPTX.read_bytes()
    with ZipFile(PPTX) as z:
        infos = z.infolist()
        data = {i.filename: z.read(i.filename) for i in infos}
    # CRCs read now: ZipFile.writestr updates the ZipInfo objects it is given
    before = {i.filename: i.CRC for i in infos}
    for part in (MEDIA_PART, POSTER_PART):
        if part in data:
            raise SystemExit(f'ERROR: {part} already in the package; slide 12 was patched before')
    prov = json.loads(PROVENANCE.read_text())
    if prov['sha256'] != {'mp4': sha(MOVIE.read_bytes()), 'png': sha(POSTER.read_bytes())}:
        raise SystemExit('ERROR: film or poster differs from its provenance record')

    # template: slide 13 movie shape and timing
    t_root = xml(data[TEMPLATE])
    t_rels = {q.get('Id'): q for q in xml(data[TEMPLATE_RELS])}
    movies = [p for p in t_root.iter(f'{{{N["p"]}}}pic') if p.find('.//a:videoFile', N) is not None]
    if len(movies) != 1:
        raise SystemExit('ERROR: slide 13 does not have exactly one movie shape')
    movie = deepcopy(movies[0])
    vf = movie.find('.//a:videoFile', N)
    media = movie.find('.//p14:media', N)
    blip = movie.find('.//p:blipFill/a:blip', N)
    if media is None or blip is None:
        raise SystemExit('ERROR: template movie lacks p14:media or a blip')
    if not (t_rels[vf.get(R_LINK)].get('Type') == REL['video']
            and t_rels[media.get(R_EMBED)].get('Type') == REL['media']
            and t_rels[vf.get(R_LINK)].get('Target') == t_rels[media.get(R_EMBED)].get('Target')
            and t_rels[blip.get(R_EMBED)].get('Type') == REL['image']):
        raise SystemExit('ERROR: template relationships are not the video/media/poster convention')
    # every r: attribute in the template shape must be one of the three handled
    handled = {vf, media, blip}
    for el in movie.iter():
        for k, v in el.attrib.items():
            if k.startswith(f'{{{N["r"]}}}') and el not in handled and v != '':
                raise SystemExit(f'ERROR: template shape references another part: {el.tag} {k}={v}')
    timing = deepcopy(t_root.find('p:timing', N))
    if timing is None or len(timing.findall('.//p:video', N)) != 1:
        raise SystemExit('ERROR: slide 13 timing is not a single video node')

    # slide 12: replace Picture 10 in place, keep its geometry
    root = xml(data[SLIDE])
    if root.find('p:timing', N) is not None:
        raise SystemExit('ERROR: slide 12 already has a timing block')
    tree = root.find('p:cSld/p:spTree', N)
    pics = [p for p in tree.findall('p:pic', N) if p.find('.//p:cNvPr', N).get('id') == PICTURE_ID]
    if len(pics) != 1 or pics[0].find('.//p:cNvPr', N).get('name') != 'Picture 10':
        raise SystemExit('ERROR: slide 12 Picture 10 (id 11) not found')
    pic = pics[0]
    old_rid = pic.find('.//a:blip', N).get(R_EMBED)
    rels = xml(data[SLIDE_RELS])
    if [q.get('Target') for q in rels if q.get('Id') == old_rid] != ['../media/image10.png']:
        raise SystemExit('ERROR: Picture 10 does not point at image10.png')
    for q in list(rels):
        if q.get('Id') == old_rid:
            rels.remove(q)
    used = {int(q.get('Id')[3:]) for q in rels}
    free = (i for i in range(1, 100) if i not in used)
    rid = {k: f'rId{next(free)}' for k in ('media', 'video', 'image')}
    for kind, target in (('media', '../media/p12_chain_growth.mp4'), ('video', '../media/p12_chain_growth.mp4'),
                         ('image', '../media/p12_chain_growth.png')):
        E.SubElement(rels, f'{{{PR}}}Relationship', Id=rid[kind], Type=REL[kind], Target=target)
    media.set(R_EMBED, rid['media'])
    vf.set(R_LINK, rid['video'])
    blip.set(R_EMBED, rid['image'])
    cnv = movie.find('.//p:cNvPr', N)
    cnv.set('id', PICTURE_ID)
    cnv.set('name', 'p12_chain_growth.mp4')
    sppr = movie.find('p:spPr', N)
    sppr.replace(sppr.find('a:xfrm', N), deepcopy(pic.find('p:spPr/a:xfrm', N)))
    tree.replace(pic, movie)
    timing.find('.//p:spTgt', N).set('spid', PICTURE_ID)
    clr = root.find('p:clrMapOvr', N)
    clr.addnext(timing)
    data[SLIDE] = dump(root)
    data[SLIDE_RELS] = dump(rels)
    data[MEDIA_PART] = MOVIE.read_bytes()
    data[POSTER_PART] = POSTER.read_bytes()

    still_named = [n for n, b in data.items() if n.endswith('.rels') and b'image10.png' in b]
    removed = []
    if not still_named:
        del data[OLD_IMAGE]
        removed.append(OLD_IMAGE)

    # write: original entries in original order with their ZipInfo, new parts appended
    tmp = PPTX.with_name(PPTX.name + '.tmp')
    with ZipFile(tmp, 'w') as z:
        for info in infos:
            if info.filename in data:
                z.writestr(info, data[info.filename])
        for part in (MEDIA_PART, POSTER_PART):
            info = ZipInfo(part, date_time=infos[0].date_time)
            info.compress_type = ZIP_DEFLATED
            z.writestr(info, data[part])
    with ZipFile(tmp) as z:
        if z.testzip() is not None:
            raise SystemExit('ERROR: written zip fails its CRC test')
        after = {i.filename: i.CRC for i in z.infolist()}
    os.replace(tmp, PPTX)
    new_bytes = PPTX.read_bytes()
    changed = sorted(n for n in before if n in after and before[n] != after[n])
    added = sorted(n for n in after if n not in before)
    dropped = sorted(n for n in before if n not in after)
    media_names = [n for n in after if n.startswith('ppt/media/')]
    record = {
        'purpose': 'Slide 12 static figure replaced by the chain-growth film (D-387).',
        'generator': str(Path(__file__).resolve().relative_to(ROOT)),
        'generator_sha256': sha(Path(__file__).read_bytes()),
        'pptx': str(PPTX.relative_to(ROOT)),
        'old': {'sha256': sha(old_bytes), 'bytes': len(old_bytes), 'entries': len(before)},
        'new': {'sha256': sha(new_bytes), 'bytes': len(new_bytes), 'entries': len(after)},
        'zip_entry_comparison': {'changed_crc': changed, 'added': added, 'removed': dropped,
                                 'unchanged_entries': len(before) - len(changed) - len(dropped)},
        'media_counts_after': {'total': len(media_names),
                               'mp4': sum(n.endswith('.mp4') for n in media_names),
                               'png': sum(n.endswith('.png') for n in media_names)},
        'template': {'slide': TEMPLATE, 'shape': movies[0].find('.//p:cNvPr', N).get('name'),
                     'timing': 'p:video / p:cMediaNode vol 80000, cond delay 0'},
        'slide12_relationships': rid,
        'film_sha256': sha(data[MEDIA_PART]), 'poster_sha256': sha(data[POSTER_PART]),
        'playback_in_powerpoint': 'not verified (author check)',
    }
    RECORD.write_text(json.dumps(record, indent=2) + '\n', encoding='ascii')
    print(json.dumps(record['old']), json.dumps(record['new']))
    print(json.dumps(record['zip_entry_comparison']))
    print(json.dumps(record['media_counts_after']))


if __name__ == '__main__':
    main()
