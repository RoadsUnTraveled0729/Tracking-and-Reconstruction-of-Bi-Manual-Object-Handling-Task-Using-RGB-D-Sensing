from pathlib import Path
import json, numpy as np

B=Path(__file__).resolve().parent
G=B.parent/'fable_repair_20261005/capture/geometry'
c=json.loads((B.parent/'fable_repair_20261005/diagnostic_sources/v2/output/scene_calibration_r6b_v2.json').read_text())
old=json.loads((G/'measured_table_geometry.json').read_text())
I=old['intrinsics']; n=np.array(old['plane_normal_camera']); point=np.array(old['plane_point_camera'])
T=np.linalg.inv(np.array(c['T_cam_desk'])); P=np.array([[1,0,0],[0,0,1],[0,1,0]])
up=np.array(old['plane_normal_world_unity']); side=np.array(old['rail_direction_world_unity']); forward=np.cross(side,up)
def intersect(uv):
    uv=np.array(uv); rays=np.column_stack(((uv[:,0]-I['ppx'])/I['fx'],(uv[:,1]-I['ppy'])/I['fy'],np.ones(len(uv))))
    pc=rays*((point@n)/(rays@n))[:,None]
    return (P@(T[:3,:3]@pc.T+T[:3,3,None])).T

# The side edges remain visible despite missing depth on the white sheet.
# Intersect those image rays with the calibrated table plane, rather than
# treating holes in depth as physical cuts in the tabletop.
left=intersect([[25,465],[90,425],[145,393],[177,375]])
right=intersect([[630,435],[560,407],[480,375]])
rear=intersect([[181,371],[476,371]])
front=intersect([[0,479],[639,479]])
lo=float(np.median(left@side)); hi=float(np.median(right@side))
back=float(np.mean(rear@forward)); near=float(np.min(front@forward))
height=float(np.array(old['plane_point_world_unity'])@up)
corners=np.array([lo*side+near*forward+height*up,lo*side+back*forward+height*up,hi*side+back*forward+height*up,hi*side+near*forward+height*up])
report={'table_corners_local_m':corners.tolist(),'width_m':hi-lo,'visible_depth_m':back-near,'left_edge_pixels':[[25,465],[90,425],[145,393],[177,375]],'right_edge_pixels':[[630,435],[560,407],[480,375]],'rear_edge_pixels':[[181,371],[476,371]],'front_scope':'Image-clipped near extent; physical front edge is outside the recording.','table_plane':'Original calibration retained. Visible straight sides constrain a rectangular display surface.','wall':'Original marker plane and marker pose retained; wall mesh spans the task region instead of being horizontally centred on the offset marker.','legs':'Standard-height display geometry, not an estimated measurement.','body_and_object_stream':'Unchanged.'}
(B/'scene_geometry.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
