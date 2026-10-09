"""Replay archived display packets verbatim; never solve or smooth pose data."""
from pathlib import Path
import argparse, csv, hashlib, json, sys, time, struct
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'eval/unity_check'))
from send_scene_r5 import ShmWriter,write_scene
SOURCE=ROOT/'eval/output/unity_check_r5/integrated_stream.csv'
CALIB=ROOT/'eval/output/scene_calibration_r5c.json'
EXPECTED='af952121f3438fca5cd153ad59f4ed1a1b488d5ef01e35b4f985404ccc5b2f60'

def packet_values(r):
 return (int(r['frame']),float(r['time_s']),[float(r['pel_'+c])for c in 'xyz'],[float(r['a'+str(i)])for i in range(13)],[float(r['op'+c])for c in 'xyz'],[float(r['oe'+c])for c in 'xyz'],int(r['mask']),int(r['obj_live']))

def main():
 p=argparse.ArgumentParser();p.add_argument('--speed',type=float,default=.25);p.add_argument('--loop',action='store_true');a=p.parse_args()
 assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==EXPECTED
 rows=list(csv.DictReader(SOURCE.open()));frames=[packet_values(r)for r in rows]
 assert [v[0]for v in frames]==list(range(2099))
 write_scene('/dev/shm/defense_axes_aruco_scene',json.loads(CALIB.read_text()))
 w=ShmWriter('/dev/shm/defense_axes_integrated_scene')
 while True:
  start=time.monotonic()
  for values in frames:
   delay=start+values[1]/a.speed-time.monotonic()
   if delay>0:time.sleep(delay)
   w.write(*values)
  if not a.loop:break
if __name__=='__main__':main()
