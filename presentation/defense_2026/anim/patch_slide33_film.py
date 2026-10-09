#!/usr/bin/env python3
"""Put the synchronised three-panel film on slide 33 (plan Milestone C).

2026-10-06 (plan declarative-stargazing-phoenix.md, Milestone C, "Slide 33").
Raw zip + lxml edit with the helpers of patch_results_pictures.py and the
media-part technique of patch_slide12_video.py:

- the FK still (picture id 35) and its label (text box id 36) are deleted;
- the movie shape id 30 keeps its XML relationship ids; its relationships
  (p14:media r:embed and a:videoFile r:link) are retargeted to the new part
  ppt/media/p33_three_panel.mp4 and its blip relationship to the new poster
  part ppt/media/p33_three_panel.png; the still's image relationship is
  removed; a:srcRect is removed (the film is shown whole); the shape is
  renamed p33_three_panel.mp4 and placed in the slide 13-15 film box
  (x 6.525, y 1.2, w 6.0 in; h = w * 640 / 1440 = 2.667 in);
- a caption text box (id 37, a copy of caption id 31: 16 pt DejaVu Sans,
  white, one paragraph) goes under the film at y 4.0 in, 6.0 in wide, with
  the text CAPTION below;
- caption id 31, the p:timing block (spid 30) and every other shape are kept;
- the old parts ppt/media/media15.mp4, ppt/media/image48.png and
  ppt/media/p33_fk_overlay.png are removed only when no relationship part
  names them after the edit;
- [Content_Types].xml is left as is (mp4 and png Defaults exist).

Every other zip entry is written with its original bytes and ZipInfo. The
zip-entry comparison (name, CRC) and old and new sha256 go to
review/slide33_film_patch.json. The script refuses to run twice.

Run from the repository root with the thesis Python:

    /home/luo/anaconda3/bin/python -B presentation/defense_2026/anim/patch_slide33_film.py
"""
from __future__ import annotations

import copy
import json
import os
import sys
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lxml import etree as E  # noqa: E402

from patch_results_pictures import (  # noqa: E402
    EMU, N, PR, dump, ext, geom, off, png_size, read, sha, shape, sid, tree_of)

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
PPTX = HERE / 'Thesis_Defence_2026.pptx'
RECORD = HERE / 'review' / 'slide33_film_patch.json'
MOVIE = HERE / 'media' / 'p33_three_panel.mp4'
POSTER = HERE / 'media' / 'p33_three_panel_poster.png'
PROVENANCE = HERE / 'media' / 'provenance' / 'p33_three_panel.json'
MEDIA_PART = 'ppt/media/p33_three_panel.mp4'
POSTER_PART = 'ppt/media/p33_three_panel.png'
OLD_PARTS = ('ppt/media/media15.mp4', 'ppt/media/image48.png', 'ppt/media/p33_fk_overlay.png')
SLIDE, SLIDE_RELS = 'ppt/slides/slide33.xml', 'ppt/slides/_rels/slide33.xml.rels'

N14 = dict(N, p14='http://schemas.microsoft.com/office/powerpoint/2010/main')
REL = {'media': 'http://schemas.microsoft.com/office/2007/relationships/media',
       'video': N['r'] + '/video', 'image': N['r'] + '/image'}
R_LINK, R_EMBED = f'{{{N["r"]}}}link', f'{{{N["r"]}}}embed'

VIDEO_ID, CAPTION_ID, STILL_ID, LABEL_ID, NEW_CAPTION_ID = 30, 31, 35, 36, 37
OLD_VIDEO_NAME = 'p47-Fresh_Unity_Handover_With_Model_Axes.mp4'
NEW_VIDEO_NAME = 'p33_three_panel.mp4'
FILM_PX = (1440, 640)                      # ffprobe and provenance 'dimensions' of the film
# Film box of slides 13-15 (their movie shapes: x 5966460, y 1097280, cx 5486400 EMU),
# plan Milestone C: x 6.525, y 1.2, w 6.0 in; height from the 1440:640 aspect.
FILM = dict(x=5966460, y=1097280, cx=5486400)
FILM['cy'] = FILM['cx'] * FILM_PX[1] // FILM_PX[0]      # 2438400 EMU = 2.667 in, exact
CAPTION_Y = int(4.0 * EMU)                 # plan Milestone C: caption below the film at y 4.0 in
CAPTION = 'Recorded RGB, Python forward kinematics and Unity avatar, same frame'   # plan text
FONT_FILE = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'   # fc-match 'DejaVu Sans'


def rel_by_id(rels, rid):
    found = [q for q in rels if q.get('Id') == rid]
    if len(found) != 1:
        raise SystemExit(f'ERROR: relationship {rid} found {len(found)} times')
    return found[0]


def patch(data):
    r = read(data, SLIDE)
    tree = tree_of(r)
    ids = [sid(s) for s in tree]
    if NEW_CAPTION_ID in ids or STILL_ID not in ids:
        raise SystemExit('ERROR: slide 33 already has id 37 or lacks the still id 35; patched before')
    video, caption = shape(r, VIDEO_ID), shape(r, CAPTION_ID)
    still, label = shape(r, STILL_ID), shape(r, LABEL_ID)
    cnv = video.find('.//p:cNvPr', N)
    if cnv.get('name') != OLD_VIDEO_NAME:
        raise SystemExit(f'ERROR: slide 33 id 30 is {cnv.get("name")!r}, not the Unity handover video')
    vf = video.find('.//a:videoFile', N)
    media = video.find('.//p14:media', N14)
    blip = video.find('p:blipFill/a:blip', N)
    if vf is None or media is None or blip is None:
        raise SystemExit('ERROR: id 30 lacks a:videoFile, p14:media or a blip')
    rels = read(data, SLIDE_RELS)
    rid = {'video': vf.get(R_LINK), 'media': media.get(R_EMBED), 'image': blip.get(R_EMBED),
           'still': still.find('.//a:blip', N).get(R_EMBED)}
    old_targets = {k: rel_by_id(rels, v).get('Target') for k, v in rid.items()}
    expect = {'video': '../media/media15.mp4', 'media': '../media/media15.mp4',
              'image': '../media/image48.png', 'still': '../media/p33_fk_overlay.png'}
    if old_targets != expect:
        raise SystemExit(f'ERROR: slide 33 relationship targets {old_targets} not as expected')
    for kind in ('video', 'media', 'image'):
        if rel_by_id(rels, rid[kind]).get('Type') != REL[kind]:
            raise SystemExit(f'ERROR: relationship {rid[kind]} is not of type {kind}')
    # every r: attribute value on the slide: the three movie ids may appear only on the movie
    uses = {}
    for el in r.iter():
        for k, v in el.attrib.items():
            if k.startswith(f'{{{N["r"]}}}') and v:
                uses.setdefault(v, []).append(el)
    for kind in ('video', 'media', 'image'):
        if any(not any(a is el for a in video.iter()) for el in uses[rid[kind]]):
            raise SystemExit(f'ERROR: {rid[kind]} is used outside the movie shape')
    if len(uses[rid['still']]) != 1:
        raise SystemExit('ERROR: the still relationship is used more than once')

    v0, s0, l0 = geom(video), geom(still), geom(label)
    label_text = ''.join(t.text or '' for t in label.findall('.//a:t', N))
    tree.remove(still)
    tree.remove(label)
    rels.remove(rel_by_id(rels, rid['still']))
    rel_by_id(rels, rid['video']).set('Target', '../media/p33_three_panel.mp4')
    rel_by_id(rels, rid['media']).set('Target', '../media/p33_three_panel.mp4')
    rel_by_id(rels, rid['image']).set('Target', '../media/p33_three_panel.png')
    src = video.find('p:blipFill/a:srcRect', N)
    src_old = dict(src.attrib) if src is not None else None
    if src is not None:
        src.getparent().remove(src)
    cnv.set('name', NEW_VIDEO_NAME)
    off(video).set('x', str(FILM['x']))
    off(video).set('y', str(FILM['y']))
    ext(video).set('cx', str(FILM['cx']))
    ext(video).set('cy', str(FILM['cy']))

    new_cap = copy.deepcopy(caption)
    ncnv = new_cap.find('.//p:cNvPr', N)
    ncnv.set('id', str(NEW_CAPTION_ID))
    ncnv.set('name', f'TextBox {NEW_CAPTION_ID - 1}')
    paras = new_cap.findall('.//p:txBody/a:p', N)
    if len(paras) != 1 or len(paras[0].findall('a:r', N)) != 1:
        raise SystemExit('ERROR: caption id 31 is not one paragraph with one run')
    paras[0].find('a:r/a:t', N).text = CAPTION
    rpr = paras[0].find('a:r/a:rPr', N)
    lnspc = int(paras[0].find('a:pPr/a:lnSpc/a:spcPts', N).get('val'))   # 1/100 pt
    from PIL import ImageFont
    text_in = ImageFont.truetype(FONT_FILE, int(rpr.get('sz'))).getlength(CAPTION) / 7200
    lines = 1 if text_in <= FILM['cx'] / EMU else 2
    if text_in > 2 * FILM['cx'] / EMU * 0.9:
        raise SystemExit(f'ERROR: caption {text_in:.2f} in may not fit in two lines')
    cap_cy = int(geom(caption)[3]) if lines == 2 else round(lnspc / 7200 * EMU)
    off(new_cap).set('x', str(FILM['x']))
    off(new_cap).set('y', str(CAPTION_Y))
    ext(new_cap).set('cx', str(FILM['cx']))
    ext(new_cap).set('cy', str(cap_cy))
    if CAPTION_Y < FILM['y'] + FILM['cy']:
        raise SystemExit('ERROR: caption overlaps the film')
    if CAPTION_Y + cap_cy > geom(caption)[1]:
        raise SystemExit('ERROR: new caption overlaps caption id 31')
    video.addnext(new_cap)

    timing = r.findall('p:timing//p:spTgt', N)
    if [t.get('spid') for t in timing] != [str(VIDEO_ID)]:
        raise SystemExit('ERROR: slide 33 timing does not target only id 30')
    data[SLIDE], data[SLIDE_RELS] = dump(r), dump(rels)
    return {'deleted': {'picture_35': {'geometry': s0, 'rid': rid['still'],
                                       'target': old_targets['still']},
                        'label_36': {'geometry': l0, 'text': label_text}},
            'video_30': {'old_name': OLD_VIDEO_NAME, 'new_name': NEW_VIDEO_NAME,
                         'old_geometry': v0, 'new_geometry': geom(video),
                         'new_geometry_in': [round(v / EMU, 4) for v in geom(video)],
                         'srcRect_removed': src_old,
                         'relationship_ids_kept': {k: rid[k] for k in ('video', 'media', 'image')},
                         'old_targets': {k: old_targets[k] for k in ('video', 'media', 'image')},
                         'new_targets': {'video': '../media/p33_three_panel.mp4',
                                         'media': '../media/p33_three_panel.mp4',
                                         'image': '../media/p33_three_panel.png'}},
            'caption_37': {'geometry': geom(new_cap), 'text': CAPTION,
                           'formatting': 'copy of caption id 31', 'text_width_in': round(text_in, 3),
                           'lines': lines},
            'caption_31': {'geometry': geom(caption), 'unchanged': True},
            'timing_spid': str(VIDEO_ID),
            'shape_ids_after': [sid(s) for s in tree if sid(s) > 0]}


def main():
    prov = json.loads(PROVENANCE.read_text())
    movie, poster = MOVIE.read_bytes(), POSTER.read_bytes()
    if prov['sha256'] != {'mp4': sha(movie), 'png': sha(poster)}:
        raise SystemExit('ERROR: film or poster differs from its provenance record')
    if png_size(poster) != FILM_PX or prov['dimensions'] not in ([1440, 640], '1440x640', {'width': 1440, 'height': 640}):
        raise SystemExit(f'ERROR: poster {png_size(poster)} or film {prov["dimensions"]} is not 1440x640')
    if RECORD.exists():
        raise SystemExit(f'ERROR: {RECORD.name} exists; slide 33 was patched before')
    old_bytes = PPTX.read_bytes()
    with ZipFile(PPTX) as z:
        infos = z.infolist()
        data = {i.filename: z.read(i.filename) for i in infos}
    # CRCs read now: ZipFile.writestr updates the ZipInfo objects it is given
    before = {i.filename: i.CRC for i in infos}
    for part in (MEDIA_PART, POSTER_PART):
        if part in data:
            raise SystemExit(f'ERROR: {part} already in the package; slide 33 was patched before')
    edits = patch(data)
    data[MEDIA_PART], data[POSTER_PART] = movie, poster

    removed, kept = [], {}
    for part in OLD_PARTS:
        name = part.rsplit('/', 1)[1].encode()
        naming = [n for n, b in data.items() if n.endswith('.rels') and name in b]
        if naming:
            kept[part] = naming
        else:
            removed.append(part)
            del data[part]

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
            tmp.unlink()
            raise SystemExit('ERROR: written zip fails its CRC test')
        after = {i.filename: i.CRC for i in z.infolist()}
    changed = sorted(n for n in before if n in after and before[n] != after[n])
    added = sorted(n for n in after if n not in before)
    dropped = sorted(n for n in before if n not in after)
    if (set(changed) != {SLIDE, SLIDE_RELS} or set(added) != {MEDIA_PART, POSTER_PART}
            or set(dropped) != set(removed) or not set(dropped) <= set(OLD_PARTS)):
        tmp.unlink()
        raise SystemExit(f'ERROR: unexpected zip-entry changes: {changed} {added} {dropped}')
    os.replace(tmp, PPTX)
    new_bytes = PPTX.read_bytes()
    media_names = [n for n in after if n.startswith('ppt/media/')]
    record = {
        'purpose': 'Slide 33 FK still and label removed; movie id 30 retargeted to the '
                   'synchronised three-panel film with a caption below it (plan Milestone C).',
        'generator': str(Path(__file__).resolve().relative_to(ROOT)),
        'generator_sha256': sha(Path(__file__).read_bytes()),
        'helpers': 'presentation/defense_2026/anim/patch_results_pictures.py',
        'pptx': str(PPTX.relative_to(ROOT)),
        'old': {'sha256': sha(old_bytes), 'bytes': len(old_bytes), 'entries': len(before)},
        'new': {'sha256': sha(new_bytes), 'bytes': len(new_bytes), 'entries': len(after)},
        'zip_entry_comparison': {'changed_crc': changed, 'added': added, 'removed': dropped,
                                 'unchanged_entries': len(before) - len(changed) - len(dropped)},
        'old_parts_kept_because_named': kept,
        'media_counts_after': {'total': len(media_names),
                               'mp4': sum(n.endswith('.mp4') for n in media_names),
                               'png': sum(n.endswith('.png') for n in media_names)},
        'film': {'part': MEDIA_PART, 'sha256': sha(data[MEDIA_PART]),
                 'source': str(MOVIE.relative_to(ROOT))},
        'poster': {'part': POSTER_PART, 'sha256': sha(data[POSTER_PART]),
                   'source': str(POSTER.relative_to(ROOT))},
        'provenance': {'path': str(PROVENANCE.relative_to(ROOT)),
                       'sha256': sha(PROVENANCE.read_bytes())},
        'constants': {
            'film_box_emu': FILM,
            'film_box_source': 'slides 13-15 movie shapes x 5966460, y 1097280, cx 5486400 EMU '
                               '(plan Milestone C: x 6.525, y 1.2, w 6.0 in); cy from 1440:640',
            'caption_y_emu': CAPTION_Y, 'caption_y_source': 'plan Milestone C (y 4.0 in)',
            'caption_text_source': 'plan Milestone C',
            'caption_font': FONT_FILE + ' (fc-match DejaVu Sans), width check only'},
        'edits': edits,
        'playback_in_powerpoint': 'not verified (author check)',
    }
    RECORD.write_text(json.dumps(record, indent=2, ensure_ascii=True) + '\n', encoding='ascii')
    print(json.dumps(record['old']), json.dumps(record['new']))
    print(json.dumps(record['zip_entry_comparison']))
    print(json.dumps(record['media_counts_after']))


if __name__ == '__main__':
    main()
