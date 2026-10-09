#!/usr/bin/env python3
"""Decode source RGB for synchronized coordinate-frame exhibits, read only."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parents[1];ROOT=HERE.parents[1]
STEMS={'r7':'recording_20260909_000024','r5':'recording_20260825_222315'}


def extract(alias,first,last):
    import cv2
    sys.path.insert(0,str(ROOT))
    from v3.replay.bag_source import BagSource
    stem=STEMS[alias];cache=Path('/tmp')/f'defense_axes_rgb_{alias}';cache.mkdir(exist_ok=True)
    raw=ROOT/f'v1/mediapipe/output/{stem}_landmarks_raw.csv'
    times={int(r['frame']):float(r['time_s']) for r in csv.DictReader(raw.open())};records=[]
    with BagSource(ROOT/f'Video/{stem}.bag',paced=False) as source:
        for frame,time_s,colour,_ in source.frames(max_frames=last+1):
            if frame<first:continue
            assert colour.shape==(480,640,3) and abs(time_s-times[frame])<1e-6
            path=cache/f'frame_{frame:05d}.png';assert cv2.imwrite(str(path),colour)
            records.append({'frame':frame,'time_s':time_s,'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    assert [r['frame'] for r in records]==list(range(first,last+1))
    report={'status':'PASS','recording':stem,'first':first,'last':last,'source_csv':str(raw.relative_to(ROOT)),
            'source_csv_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'frames':records,
            'policy':'Original aligned-source color frames are decoded without tracking, estimation, recoloring or image editing.'}
    out=HERE/'media/provenance'/f'axes_{alias}_rgb.json';out.write_text(json.dumps(report,indent=2)+'\n',encoding='ascii')
    print('PASS RGB extraction',alias,len(records),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('alias',choices=STEMS);p.add_argument('--first',type=int,required=True);p.add_argument('--last',type=int,required=True);a=p.parse_args();extract(a.alias,a.first,a.last)
