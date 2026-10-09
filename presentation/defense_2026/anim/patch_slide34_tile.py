#!/usr/bin/env python3
"""Slide 34 tile 1002 wording (D-392, final step).

2026-10-06 (Milestone B follow-up). patch_slide34_wording.py set tile 1002 to
"45-frame windows, slow motion", which measures 4.863 in at 22 pt in a
4.01 in box and wraps (review/slide34_wording_patch.json, measured_wraps).
The master decision shortens it to "45-frame slow windows". Raw zip + lxml
edit with the helpers of patch_results_pictures.py: only the a:t of the one
run changes, its formatting is kept.

Guards: the pptx must be the output of patch_slide33_film.py
(review/slide33_film_patch.json new sha256) and tile 1002 must hold the old
text, so the script refuses to run twice. Every other zip entry is written
with its original bytes and ZipInfo; the zip-entry comparison must show only
ppt/slides/slide34.xml changed. Record: review/slide34_tile_patch.json.

Run from the repository root with the thesis Python:

    /home/luo/anaconda3/bin/python -B presentation/defense_2026/anim/patch_slide34_tile.py
"""
import hashlib
import json
import os
import sys
from pathlib import Path
from zipfile import ZipFile

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import patch_results_pictures as H  # noqa: E402  (helpers: read, dump, shape, geom, ...)

N, EMU = H.N, H.EMU
HERE, ROOT, PPTX = H.HERE, H.ROOT, H.PPTX
S34 = H.S34
RECORD = HERE / 'review' / 'slide34_tile_patch.json'
PREV_RECORD = HERE / 'review' / 'slide33_film_patch.json'
TILE = 1002
OLD_TEXT = '45-frame windows, slow motion'   # set by patch_slide34_wording.py (D-392)
NEW_TEXT = '45-frame slow windows'           # master decision, Milestone B follow-up
TILE_PT = 22                                 # tile size used in slide34_wording_patch.json


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def main():
    old_bytes = PPTX.read_bytes()
    expected = json.loads(PREV_RECORD.read_text())['new']['sha256']
    if sha(old_bytes) != expected:
        raise SystemExit(f'ERROR: pptx {sha(old_bytes)} is not the slide 33 film output {expected}; '
                         'patched before?')
    with ZipFile(PPTX) as z:
        infos = z.infolist()
        data = {i.filename: z.read(i.filename) for i in infos}
    before = {i.filename: i.CRC for i in infos}

    r = H.read(data, S34)
    sp = H.shape(r, TILE)
    paras = sp.findall('.//p:txBody/a:p', N)
    runs = sp.findall('.//p:txBody/a:p/a:r', N)
    if len(paras) != 1 or len(runs) != 1:
        raise SystemExit(f'ERROR: shape {TILE} is not one paragraph with one run')
    t = runs[0].find('a:t', N)
    if t.text != OLD_TEXT:
        raise SystemExit(f'ERROR: shape {TILE} text {t.text!r} != {OLD_TEXT!r}; patched before?')
    t.text = NEW_TEXT
    data[S34] = H.dump(r)

    from PIL import ImageFont
    f22 = ImageFont.truetype(H.FONT_FILE, TILE_PT * 100)
    box_in = H.geom(sp)[2] / EMU
    measure = {'old_text_in': round(f22.getlength(OLD_TEXT) / 7200, 3),
               'new_text_in': round(f22.getlength(NEW_TEXT) / 7200, 3),
               'box_in': round(box_in, 3), 'pt': TILE_PT, 'font': os.path.basename(H.FONT_FILE)}

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
    if changed != [S34] or added or dropped:
        tmp.unlink()
        raise SystemExit(f'ERROR: unexpected zip-entry changes: {changed} {added} {dropped}')
    os.replace(tmp, PPTX)
    new_bytes = PPTX.read_bytes()
    record = {
        'purpose': 'Slide 34 tile 1002 shortened so it does not wrap (D-392 final step).',
        'generator': str(Path(__file__).resolve().relative_to(ROOT)),
        'generator_sha256': sha(Path(__file__).read_bytes()),
        'helpers': str(Path(H.__file__).resolve().relative_to(ROOT)),
        'pptx': str(PPTX.relative_to(ROOT)),
        'old': {'sha256': sha(old_bytes), 'bytes': len(old_bytes), 'entries': len(before)},
        'new': {'sha256': sha(new_bytes), 'bytes': len(new_bytes), 'entries': len(after)},
        'zip_entry_comparison': {'changed_crc': changed, 'added': added, 'removed': dropped,
                                 'unchanged_entries': len(before) - len(changed)},
        'edit': {'shape_id': TILE, 'old': OLD_TEXT, 'new': NEW_TEXT, 'measured_width': measure},
        'powerpoint_view': 'not verified (author check)',
    }
    RECORD.write_text(json.dumps(record, indent=2, ensure_ascii=True) + '\n', encoding='ascii')
    print(json.dumps(record['old']), json.dumps(record['new']))
    print(json.dumps(record['zip_entry_comparison']), json.dumps(measure))


if __name__ == '__main__':
    main()
