#!/usr/bin/env python3
"""Source-matched torso, grasp and frame-533 teaching evidence.

No detector, kinematic solver or experiment is rerun. Read-only decoding
provides RGB. Frozen functions reconstruct the saved grasp input, and saved
V2 dumps provide the frame-533 records. Animation time is editorial.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parents[1]
REPO = HERE.parents[1]
MEDIA = HERE / "media"
MATCHED = MEDIA / "matched"
PROV = MEDIA / "provenance"
REVIEW = HERE / "review"
R7 = "recording_20260909_000024"
R6B = "recording_20260831_065553"
CACHE7 = Path("/tmp/defense_matched_r7")
CACHE6 = Path("/tmp/defense_2026_causal/camera")
W, H, FPS = 1440, 1200, 30
BG, INK, MUTED = "#FFFFFF", "#22313D", "#52606B"
BLUE, OBSERVED, AMBER = "#386C8C", "#7A858D", "#AB783B"
TEAL = INK
PALE = "#DCE2E6"
FONT = Path("/usr/share/fonts/truetype/dejavu")


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def rel(path):
    return str(Path(path).relative_to(REPO))


def write_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="ascii")


def font(size=48, bold=False):
    return ImageFont.truetype(str(FONT / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")), size)


def text(draw, xy, value, size=48, color=INK, bold=False, anchor=None):
    assert value.isascii(), value
    bounds = draw.textbbox(xy, value, font=font(size, bold), anchor=anchor)
    assert min(bounds[:2]) >= 0 and bounds[2] <= W and bounds[3] <= H, (value, bounds)
    draw.text(xy, value, font=font(size, bold), fill=color, anchor=anchor)


def arrow(draw, a, b, color, width=8):
    a, b = np.asarray(a, float), np.asarray(b, float)
    draw.line([tuple(a), tuple(b)], fill=color, width=width)
    u = b-a
    length = np.linalg.norm(u)
    if length < 1:
        return
    u /= length
    n = np.array([-u[1], u[0]])
    draw.polygon([tuple(b), tuple(b-23*u+10*n), tuple(b-23*u-10*n)], fill=color)


def project(p, intrinsics):
    p = np.asarray(p, float)
    assert np.isfinite(p).all() and p[2] > 0
    return np.array([intrinsics["fx"]*p[0]/p[2]+intrinsics["ppx"],
                     intrinsics["fy"]*p[1]/p[2]+intrinsics["ppy"]])


def extract_r7():
    """Run with v3rt Python; read-only bag access, no pose estimation."""
    import cv2
    sys.path.insert(0, str(REPO))
    from v3.replay.bag_source import BagSource
    CACHE7.mkdir(exist_ok=True)
    lm = {int(r["frame"]): float(r["time_s"]) for r in csv.DictReader(
        (REPO / f"v1/mediapipe/output/{R7}_landmarks_raw.csv").open())}
    records = []
    with BagSource(REPO / f"Video/{R7}.bag", paced=False) as source:
        for idx, time_s, colour, depth in source.frames(max_frames=781):
            if idx == 100 or 600 <= idx <= 780:
                assert colour.shape == (480, 640, 3)
                assert abs(time_s-lm[idx]) < 1e-6
                path = CACHE7 / ("frame_%04d.png" % idx)
                assert cv2.imwrite(str(path), colour)
                records.append({"frame": idx, "time_s": time_s, "csv_time_s": lm[idx],
                                "shape": list(colour.shape), "path": str(path), "sha256": sha(path)})
    write_json(CACHE7 / "extraction.json", records)
    print("PASS: extracted source-matched R7 RGB", len(records))


def derive():
    """Use exact frozen grasp-input functions; never call run_variant/solve."""
    import pandas as pd
    sys.path.insert(0, str(REPO / "eval/failure"))
    import recovery_core as rc
    import carry
    import grip_state
    from fit_offset import load_tracks
    MATCHED.mkdir(parents=True, exist_ok=True)
    PROV.mkdir(exist_ok=True)
    REVIEW.mkdir(exist_ok=True)
    meta = json.loads((REPO / f"v1/mediapipe/output/{R7}_landmarks_raw.meta.json").read_text())
    k = meta["color_intrinsics"]
    raw = pd.read_csv(REPO / f"v1/mediapipe/output/{R7}_landmarks_raw.csv").set_index("frame")
    extraction = {r["frame"]: r for r in json.loads((CACHE7 / "extraction.json").read_text())}
    for idx in [100, *range(600, 741)]:
        assert sha(CACHE7 / ("frame_%04d.png" % idx)) == extraction[idx]["sha256"]
        assert abs(extraction[idx]["time_s"]-raw.loc[idx, "time_s"]) < 1e-6
    torso_path = MATCHED / "torso_r7_f00100.png"
    shutil.copyfile(CACHE7 / "frame_0100.png", torso_path)
    row = raw.loc[100]
    corners = []
    for idx in [11, 12, 24, 23, 13, 14, 15, 16]:
        name = meta["landmark_names"][str(idx)]
        p = row[[name+"_"+a for a in "xyz"]].to_numpy(float)
        assert int(row[name+"_src"]) == 0
        corners.append({"id": idx, "name": name, "label": name.replace("_", " ").title()+" L"+str(idx),
                        "camera_xyz_m": p.tolist(), "source_uv_px": project(p, k).tolist(),
                        "visibility": float(row[name+"_vis"]), "source_flag": int(row[name+"_src"])})
    fm = pd.read_csv(REPO / "eval/output/recovery_r7/failure_mask.csv")
    assert int(fm.iloc[100]["fail_torso"]) == 0
    torso = {"image": rel(torso_path), "sha256": sha(torso_path), "width": 640, "height": 480,
             "frame": 100, "time_s": float(row["time_s"]), "crop": None, "pixel_edits": None,
             "landmarks": corners, "quadrilateral_order": [11, 12, 24, 23],
             "basis_origin": 24, "basis_input_ids": [24, 23, 12],
             "mapping": "slide_x=image_left+u*image_width/640; slide_y=image_top+v*image_height/480",
             "qualification": "Four anatomical landmarks bound the torso plate; three landmarks define its basis. Anatomical left appears on image right. Points are reprojected saved RGB-D observations, not manual anatomical ground truth."}
    inputs = rc.build_inputs(R7)
    calib, world, lm, obj, rot, det, wrists, flags, times = load_tracks(R7, str(REPO / "eval/output/scene_calibration_r7c.json"))
    frozen = json.loads((REPO / "eval/output/recovery_r7/grip_episodes.json").read_text())
    assert [list(e) for e in inputs["episodes"]["right"]] == [[e["start"], e["stop"]] for e in frozen["episodes"]["right"]]
    side = "right"
    local = np.einsum("nij,ni->nj", rot, wrists[side]-obj)
    clean = carry.holding_mask(inputs["center"], wrists[side], flags[side], det,
                              inputs["carried"], carry.forearm_ok(lm, side)) & ~fm["fail_arm_R"].to_numpy(bool)
    mu = grip_state.time_local_mu(local, clean, inputs["episodes"][side])
    ep = grip_state.per_frame_mu(len(lm), inputs["episode_fits"][side])
    missing = ~np.isfinite(mu).all(axis=1)
    mu[missing] = ep[missing]
    estimated = obj + np.einsum("nij,nj->ni", rot, mu)
    solver = rc._leveled_to_solver_space(estimated, world)
    np.testing.assert_allclose(solver[600:741], inputs["w_hat_solver"][side][600:741], atol=1e-12)
    # Camera-prime and camera differ only in y sign, exactly as the frozen helper.
    camera_estimate = solver * [1, -1, 1]
    camera_object = rc._leveled_to_solver_space(obj, world) * [1, -1, 1]
    records = []
    for idx in range(600, 741):
        p = lm.iloc[idx][[side+"_wrist_"+a for a in "xyz"]].to_numpy(float)
        valid_observation = bool(clean[idx])
        if idx in [705,706,707]:
            assert int(raw.loc[idx, "right_wrist_src"]) == 2
            assert not clean[idx]
            np.testing.assert_array_equal(mu[idx], mu[704])
        records.append({"frame": idx, "time_s": float(times[idx]), "rgb_sha256": extraction[idx]["sha256"],
                        "raw_wrist_source": int(raw.loc[idx, "right_wrist_src"]),
                        "filtered_wrist_flag": int(flags[side][idx]), "clean_offset_update": valid_observation,
                        "holding": bool(inputs["holding"][side][idx]),
                        "object_local_observation_m": local[idx].tolist() if valid_observation else None,
                        "object_local_estimate_m": mu[idx].tolist(),
                        "marker_origin_leveled_world_m": obj[idx].tolist(), "marker_rotation_leveled_world": rot[idx].tolist(),
                        "estimated_wrist_leveled_world_m": estimated[idx].tolist(),
                        "marker_uv_px": project(camera_object[idx], k).tolist(),
                        "wrist_input_uv_px": project(p, k).tolist() if valid_observation else None,
                        "wrist_estimate_uv_px": project(camera_estimate[idx], k).tolist(),
                        "right_shoulder_camera_prime_m": (lm.iloc[idx][["right_shoulder_"+a for a in "xyz"]].to_numpy(float)*[1,-1,1]).tolist(),
                        "right_wrist_target_camera_prime_m": solver[idx].tolist(),
                        "segment_lengths_m": inputs["seg_len"],
                        "direction_memory": None})
    # Each display frame maps to one source frame. Repeats slow playback or
    # deliberately freeze BOTH views; neither view runs on another timeline.
    grasp_map = []
    for idx in range(600, 741):
        grasp_map.extend([idx]*2)
        if idx == 705:
            grasp_map.extend([idx]*(4*FPS))
    grasp_map.extend([740]*(2*FPS))
    source6 = json.loads((PROV / "recorded_context_source.json").read_text())
    frame6 = {r["frame"]: r for r in source6["frames"]}
    for idx in range(383, 534):
        assert sha(CACHE6 / ("cam_%06d.jpg" % idx)) == frame6[idx]["cache_sha256"]
    image6 = MATCHED / "r6b_frame_533.jpg"
    shutil.copyfile(CACHE6 / "cam_000533.jpg", image6)
    lm6 = pd.read_csv(REPO / f"v1/mediapipe/output/{R6B}_landmarks_raw.csv").set_index("frame")
    k6 = json.loads((REPO / f"v1/mediapipe/output/{R6B}_landmarks_raw.meta.json").read_text())["color_intrinsics"]
    hip = []
    for idx,name in [(11,"left_shoulder"),(12,"right_shoulder"),(23,"left_hip"),(24,"right_hip")]:
        p = lm6.loc[533,[name+"_"+a for a in "xyz"]].to_numpy(float)
        hip.append({"id": idx,"name":name,"camera_xyz_m":p.tolist(),"source_uv_px":project(p,k6).tolist(),
                    "source_flag": int(lm6.loc[533,name+"_src"])})
    person = pd.read_csv(REPO / "v2/output/v2_person_dump_r6b_full.csv").set_index("frame")
    object_df = pd.read_csv(REPO / "v2/output/v2_object_dump_r6b_full.csv").set_index("frame")
    merger = pd.read_csv(REPO / "v2/output/v2_integrate_dump_r6b_full.csv").set_index("tick")
    p533, o533, merged = person.loc[533].to_dict(), object_df.loc[533].to_dict(), merger.loc[533].to_dict()
    assert int(p533["mask"]) == 122 and [int(p533["tag_"+str(i)]) for i in range(7)] == [2,0,1,0,0,0,0]
    assert int(o533["live"]) == 1 and int(object_df.loc[532,"live"]) == 1
    assert [int(merged[a]) for a in ["p_f0","p_f1","o_f0","o_f1"]] == [532,533,532,533]
    assert int(merged["flags"]) == 3 and int(merged["tags"]) == 18
    assert abs(p533["time_s"]-frame6[533]["recorded_relative_seconds"]) < 1e-6
    trace_map = list(range(383,533)) + [533]*(39*FPS)
    source_paths = [REPO/f"Video/{R7}.bag",REPO/f"Video/{R6B}.bag",
                    REPO/f"v1/mediapipe/output/{R7}_landmarks_raw.csv",
                    REPO/f"v1/mediapipe/output/{R7}_landmarks_raw.meta.json",
                    REPO/f"v1/mediapipe/output/{R7}_landmarks_filtered.csv",
                    REPO/f"v1/mediapipe/output/{R6B}_landmarks_raw.csv",
                    REPO/f"v1/mediapipe/output/{R6B}_landmarks_raw.meta.json",
                    REPO/f"eval/output/{R7}_scaled_object_world_filtered_clean.csv",
                    REPO/"eval/output/scene_calibration_r7c.json",REPO/"eval/output/recovery_r7/failure_mask.csv",
                    REPO/"eval/output/recovery_r7/grip_episodes.json",
                    REPO/"eval/failure/grip_state.py",REPO/"eval/failure/recovery_core.py",
                    REPO/"eval/offset/carry.py",REPO/"eval/offset/fit_offset.py",
                    REPO/"v2/output/v2_person_dump_r6b_full.csv",REPO/"v2/output/v2_object_dump_r6b_full.csv",
                    REPO/"v2/output/v2_integrate_dump_r6b_full.csv",REPO/"v2/common/shm_ring.py",
                    REPO/"writing/v9/Thesis_V9.pdf"]
    data = {"status":"PASS","sources":[{"path":rel(p),"sha256":sha(p)} for p in source_paths],
            "torso":torso,"hip_example":{"image":rel(image6),"sha256":sha(image6),"frame":533,
             "width":640,"height":480,"crop":None,"landmarks":hip,"time_s":frame6[533]["recorded_relative_seconds"],
             "qualification":"Original decoded colour; raw hip points precede depth preparation. Visible-surface depth is not anatomical depth."},
            "grasp":{"records":records,"output_source_frames":grasp_map,"fps":FPS,"duration_s":len(grasp_map)/FPS,
             "episode":[290,1063],"matched_source_time":True,"poster_source_frame":630,
             "timing":"0.5x source playback; additional 4 s freeze at frame 705 and 2 s final freeze. Both panels always use the same source frame.",
             "qualification":"Recorded RGB above; projections and object-local x/z view below are derived from the same frozen offline inputs. A target is offered to the solve, not proof that the final solver used it or anatomical ground truth. Stored offset freezes through the depth loss."},
            "frame_journey":{"source_frame":533,"source_time_s":frame6[533]["recorded_relative_seconds"],
             "person_record":p533,"object_record":o533,"merger_tick":533,"merger_record":merged,
             "output_source_frames":trace_map,"fps":FPS,"duration_s":len(trace_map)/FPS,
             "slot":533%8,"slot_bytes":1536032,"colour_bytes":921600,"depth_bytes":614400,
             "qualification":"The recorded RGB plays frames 383-532 at 30 fps, then visibly freezes on 533. All capture/branch values belong to 533. Merger input includes 532; its output tick is a separate counter, coincidentally also 533 here. Staged arrows are explanatory, not recorded scheduler events or latency."},
            "checks":{"raw_rgb_read_only_decode":"PASS","source_times_match_csv":"PASS",
             "four_torso_landmarks_accepted":"PASS","right_grip_episode_matches_saved_report":"PASS",
             "wrist_target_matches_frozen_build_inputs":"PASS","offset_freezes_at_705_707":"PASS",
             "frame533_records_match_saved_dumps":"PASS","no_detector_or_solver_run":True}}
    write_json(PROV / "matched_evidence.json",data)
    print("PASS: native torso overlay and matched-source derivations exported")
    return data


def ring(draw, p, color, radius=12):
    x,y=p
    draw.ellipse((x-radius,y-radius,x+radius,y+radius),fill="white",outline=color,width=7)


def add_elbow_constraints(data):
    """Ideal two-length intersection only; no saved execution prior exists."""
    circles=[];maximum=0.0
    for r in data["grasp"]["records"]:
        shoulder=np.asarray(r["right_shoulder_camera_prime_m"])
        wrist=np.asarray(r["right_wrist_target_camera_prime_m"])
        upper=r["segment_lengths_m"]["upper_arm_R"]
        fore=r["segment_lengths_m"]["forearm_R"]
        distance=float(np.linalg.norm(wrist-shoulder))
        reachable=abs(upper-fore)<=distance<=upper+fore and distance>0
        item={"frame":r["frame"],"reachable":reachable,"distance_m":distance,
              "upper_arm_m":upper,"forearm_m":fore,"prior":None,"selected_elbow":None}
        if reachable:
            b=(wrist-shoulder)/distance
            a=(upper*upper-fore*fore+distance*distance)/(2*distance)
            radius=float(np.sqrt(max(0.0,upper*upper-a*a)))
            center=shoulder+a*b
            seed=np.array([1.,0,0]) if abs(b[0])<.9 else np.array([0.,1,0])
            e1=np.cross(b,seed);e1/=np.linalg.norm(e1);e2=np.cross(b,e1)
            theta=np.linspace(0,2*np.pi,121)
            circle=center+radius*(np.cos(theta)[:,None]*e1+np.sin(theta)[:,None]*e2)
            residual=max(float(np.max(np.abs(np.linalg.norm(circle-shoulder,axis=1)-upper))),
                         float(np.max(np.abs(np.linalg.norm(circle-wrist,axis=1)-fore))))
            assert residual<1e-12
            maximum=max(maximum,residual)
            item.update({"center_camera_prime_m":center.tolist(),"normal_camera_prime":b.tolist(),
                         "radius_m":radius,"axial_distance_m":float(a),
                         "circle_point_max_length_residual_m":residual})
        circles.append(item)
    data["elbow_constraints"]={"records":circles,"output_source_frames":data["grasp"]["output_source_frames"],
                               "fps":FPS,"duration_s":data["grasp"]["duration_s"],
                               "maximum_length_residual_m":maximum,
                               "view":"Endpoint-aligned oblique orthographic view, not the RGB camera projection.",
                               "qualification":"The recorded elbow is measured in this interval. This illustration asks what endpoints alone constrain; it does not claim an actual missing-elbow event, selected runtime prior or final solver result. The ideal circle precedes near-extension and continuity guards."}
    write_json(PROV/"matched_evidence.json",data)
    return data


def elbow_frame(data,out_index):
    source_frame=data["grasp"]["output_source_frames"][out_index]
    r=data["grasp"]["records"][source_frame-600]
    c=data["elbow_constraints"]["records"][source_frame-600]
    im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
    mode="freeze" if 212<=out_index<332 or out_index>=402 else "0.5x playback"
    text(d,(45,18),"R7  |  frame %d  |  %.3f s  |  %s"%(source_frame,r["time_s"],mode),48)
    photo=Image.open(CACHE7/("frame_%04d.png"%source_frame)).convert("RGB").resize((896,672),Image.Resampling.LANCZOS)
    im.paste(photo,(272,86))
    intrinsics=json.loads((REPO/f"v1/mediapipe/output/{R7}_landmarks_raw.meta.json").read_text())["color_intrinsics"]
    shoulder_camera=np.array(r["right_shoulder_camera_prime_m"])*[1,-1,1]
    sp=project(shoulder_camera,intrinsics)*1.4+[272,86]
    wp=np.asarray(r["wrist_estimate_uv_px"])*1.4+[272,86]
    ring(d,sp,OBSERVED,11);ring(d,wp,BLUE,13)
    text(d,(45,806),"Endpoint constraints alone",48)
    if not c["reachable"]:
        text(d,(135,966),"No circle: the fixed lengths cannot reach this target.",48,AMBER)
        return im
    # Coordinates in the endpoint-aligned basis preserve all 3-D constraints;
    # the final 2-D map is explicitly an oblique diagram view.
    origin=np.array([235.,1045.]);scale=1370.
    draw_point=lambda x,y=0,z=0: origin+scale*np.array([x+.25*y+.35*z,-.93*y+.4*z])
    theta=np.linspace(0,2*np.pi,121)
    circle=[tuple(draw_point(c["axial_distance_m"],c["radius_m"]*np.cos(t),c["radius_m"]*np.sin(t))) for t in theta]
    end=draw_point(c["distance_m"])
    d.line([tuple(origin),tuple(end)],fill=PALE,width=3)
    d.line(circle,fill=BLUE,width=5)
    ring(d,origin,OBSERVED,11);ring(d,end,BLUE,13)
    text(d,(origin[0],1120),"Shoulder",48,anchor="mt")
    text(d,(end[0],1120),"Wrist target",48,anchor="mt")
    text(d,(1050,933),"Elbow circle",44)
    text(d,(1050,1015),"Prior needed",44)
    text(d,(70,868),"Same source frame; ideal two-length geometry",44,MUTED)
    return im


def grasp_frame(data, source_frame, out_index=None):
    rec = data["grasp"]["records"][source_frame-600]
    im = Image.new("RGB", (W,H), BG)
    d = ImageDraw.Draw(im)
    missing=rec["raw_wrist_source"]==2
    paused=(212 <= out_index < 332 or out_index >= 402) if out_index is not None else source_frame in [705,740]
    mode="freeze" if paused else "0.5x playback"
    text(d,(45,18),"R7  |  frame %d  |  %.3f s  |  %s"%(source_frame,rec["time_s"],mode),48)
    photo=Image.open(CACHE7/("frame_%04d.png"%source_frame)).convert("RGB").resize((896,672),Image.Resampling.LANCZOS)
    im.paste(photo,(272,86))
    scale=896/640
    xy=lambda key: np.array(rec[key])*scale+[272,86]
    marker=xy("marker_uv_px");pred=xy("wrist_estimate_uv_px")
    arrow(d,marker,pred,BLUE,7)
    ring(d,marker,INK,10);ring(d,pred,BLUE,13)
    if rec["wrist_input_uv_px"] is not None:
        ring(d,xy("wrist_input_uv_px"),OBSERVED,8)
    state="Missing depth: offset held" if missing else "Clean wrist input updates the offset"
    if not missing and not rec["clean_offset_update"]:
        state="Input gated: offset held"
    text(d,(70,782),state,48,AMBER if missing or not rec["clean_offset_update"] else INK)
    text(d,(70,851),"Object-local x/z projection; y omitted",48)
    # This is a labelled 2-D projection of exact 3-D source quantities.
    # Limits are editorial display limits in cm, not a data/solver threshold.
    origin=np.array([485,1140.0])
    factor=10.0
    plot=lambda h:origin+np.array([h[0]*100*factor,-h[2]*100*factor])
    d.line((190,1140,825,1140),fill=PALE,width=3)
    d.line((485,905,485,1140),fill=PALE,width=3)
    text(d,(825,1145),"x (cm)",44,MUTED)
    text(d,(335,910),"z (cm)",44,MUTED)
    for v in [-20,-10,0,10,20]:
        x=485+v*factor
        d.line((x,1133,x,1147),fill=MUTED,width=2)
        text(d,(x,1175),str(v),44,MUTED,anchor="mm")
    for v in [10,20]:
        y=1140-v*factor
        d.line((478,y,492,y),fill=MUTED,width=2)
        text(d,(510,y),str(v),44,MUTED,anchor="lm")
    h=rec["object_local_estimate_m"]
    arrow(d,origin,plot(h),BLUE)
    ring(d,origin,INK,10);ring(d,plot(h),BLUE,13)
    if rec["object_local_observation_m"] is not None:
        ring(d,plot(rec["object_local_observation_m"]),OBSERVED,8)
    for y,c,label in [(922,INK,"Marker origin"),(1006,OBSERVED,"Wrist input"),(1090,BLUE,"Wrist estimate")]:
        ring(d,(996,y+25),c,11)
        text(d,(1035,y),label,44,INK)
    return im


TRACE_STAGES=[
    (0,5,"Recorded task",["Recording plays","Approach frame 533"],"play"),
    (5,10,"Select one capture",["RGB + aligned depth","640 x 480"],"disk"),
    (10,16,"Publish frame 533",["PSF1 slot 5","1,536,032 bytes"],"shared"),
    (16,22,"Two verified private copies",["Person branch","Object branch"],"copies"),
    (22,29,"Two records for frame 533",["PSR2: 84 bytes","PSB2: 44 bytes"],"records"),
    (29,37,"Resample source frames 532 + 533",["One render time","17.750923 s"],"merge"),
    (37,44,"Publish one combined pose",["PSI2: 112 bytes","Unity applies transforms"],"unity"),
]


def block(d, rect, first, second, color=BLUE):
    x0,y0,x1,y1=rect
    d.rounded_rectangle(rect,radius=10,fill="white",outline=PALE,width=4)
    first_offset,second_offset=(18,82) if y1-y0<170 else (30,106)
    for value,size,offset,color in [(first,48,first_offset,INK),(second,44,second_offset,MUTED)]:
        point=((x0+x1)/2,y0+offset)
        bounds=d.textbbox(point,value,font=font(size),anchor="mt")
        assert bounds[0]>=x0+4 and bounds[2]<=x1-4 and bounds[1]>=y0+4 and bounds[3]<=y1-4,(value,bounds,rect)
        text(d,point,value,size,color,anchor="mt")


def progress(value, start=0.16, stop=0.80):
    """Editorial motion only: reserve a readable hold before and after travel."""
    amount=float(np.clip((value-start)/(stop-start),0,1))
    return amount*amount*(3-2*amount)


def along_path(points, amount):
    points=np.asarray(points,float)
    lengths=np.linalg.norm(np.diff(points,axis=0),axis=1)
    remaining=float(amount)*float(lengths.sum())
    for idx,length in enumerate(lengths):
        if remaining<=length:
            return points[idx]+(points[idx+1]-points[idx])*(remaining/length)
        remaining-=length
    return points[-1]


def payload(d, center, label, color=OBSERVED, show_label=True):
    """A data tile stays below card headings; its width is not a byte scale."""
    x,y=np.asarray(center,float)
    rect=(x-130,y-32,x+130,y+32)
    assert 0<=rect[0]<rect[2]<=W and 0<=rect[1]<rect[3]<=H
    d.rounded_rectangle(rect,radius=9,fill=BG,outline=color,width=4)
    if show_label:
        bounds=d.textbbox((x,y),label,font=font(40),anchor="mm")
        assert bounds[0]>=rect[0]+8 and bounds[2]<=rect[2]-8
        assert bounds[1]>=rect[1]+5 and bounds[3]<=rect[3]-5
        text(d,(x,y),label,40,INK,anchor="mm")


def copy_payload(d, points, amount, label="RGB-D", color=OBSERVED,
                 moving_label=None):
    """The source tile remains intact; a duplicate travels to its destination."""
    location=along_path(points,amount)
    source=np.asarray(points[0],float)
    # Avoid partially superimposed glyphs while the duplicate emerges.
    separated=abs(location[0]-source[0])>270 or abs(location[1]-source[1])>78
    payload(d,location,moving_label or label,color,show_label=separated)
    payload(d,source,label,color)


def trace_frame(data, out_index):
    source_frame=data["frame_journey"]["output_source_frames"][out_index]
    t=out_index/FPS
    stage=next(s for s in TRACE_STAGES if s[0]<=t<s[1])
    im=Image.new("RGB",(W,H),BG);d=ImageDraw.Draw(im)
    selected=source_frame==533
    mode="selected and frozen" if selected else "original playback"
    text(d,(45,18),"R6b  |  frame %d  |  %s"%(source_frame,mode),48)
    photo=Image.open(CACHE6/("cam_%06d.jpg"%source_frame)).convert("RGB").resize((896,672),Image.Resampling.LANCZOS)
    im.paste(photo,(272,86))
    headings={"play":"Play to the selected capture", "disk":"One capture contains colour and depth", "shared":"Publish the selected capture once", "copies":"Both branches copy frame 533", "records":"Images become two derived records", "merge":"Frame 533 joins frame 532 in the merger", "unity":"Apply the combined pose in Unity"}
    phase=stage[4]
    elapsed=(t-stage[0])/(stage[1]-stage[0])
    text(d,(45,806),headings[phase],48)
    if phase=="play":
        block(d,(80,900,640,1088),"Recorded RGB-D","On disk")
        arrow(d,(675,994),(755,994),MUTED)
        block(d,(790,900,1350,1088),"Selected capture","Frame 533")
    elif phase=="disk":
        block(d,(80,900,640,1088),"On disk","")
        arrow(d,(675,994),(755,994),MUTED)
        block(d,(790,900,1350,1088),"Capture","")
        copy_payload(d,[(360,1039),(1070,1039)],progress(elapsed))
    elif phase=="shared":
        block(d,(80,900,640,1088),"Capture","")
        arrow(d,(675,994),(755,994),MUTED)
        block(d,(790,900,1350,1088),"Shared RAM","")
        copy_payload(d,[(360,1039),(1070,1039)],progress(elapsed))
    elif phase=="copies":
        block(d,(40,924,445,1112),"Shared frame","")
        block(d,(565,886,1360,1028),"Person private copy","")
        block(d,(565,1045,1360,1187),"Object private copy","")
        source=(242,1064)
        person_path=[source,(550,1064),(550,994),(962,994)]
        object_path=[source,(550,1064),(550,1147),(962,1147)]
        first=progress(elapsed,0.08,0.43)
        second=progress(elapsed,0.53,0.88)
        if first>0:
            copy_payload(d,person_path,first)
        if second>0:
            copy_payload(d,object_path,second)
        payload(d,source,"RGB-D")
    elif phase=="records":
        block(d,(45,900,680,1088),"Person","")
        block(d,(750,900,1385,1088),"Object","")
        amount=progress(elapsed)
        person_label="RGB-D" if elapsed<0.30 else "Landmarks" if elapsed<0.65 else "Angles"
        object_label="RGB-D" if elapsed<0.30 else "Marker" if elapsed<0.65 else "Pose"
        color=OBSERVED if elapsed<0.30 else BLUE
        payload(d,along_path([(210,1039),(515,1039)],amount),person_label,color)
        payload(d,along_path([(915,1039),(1220,1039)],amount),object_label,color)
        text(d,(200,1125),"Both saved records retain source frame 533.",44,MUTED)
    elif phase=="merge":
        block(d,(45,900,680,1088),"Buffered records","")
        arrow(d,(690,994),(750,994),MUTED)
        block(d,(775,900,1390,1088),"Combined state","")
        copy_payload(d,[(362,1039),(1082,1039)],progress(elapsed),"532 + 533",BLUE,
                     moving_label="Records" if elapsed<0.55 else "Pose")
        text(d,(180,1125),"Adjacent frames are resampled; the RGB stays frozen.",44,MUTED)
    elif phase=="unity":
        block(d,(45,900,680,1088),"Combined state","")
        arrow(d,(690,994),(750,994),MUTED)
        block(d,(775,900,1390,1088),"Unity","")
        copy_payload(d,[(362,1039),(1082,1039)],progress(elapsed),"Pose",BLUE)
        text(d,(200,1125),"The output is a new pose, not an unchanged frame.",44,MUTED)
    if phase not in ["copies","records","merge","unity"]:
        text(d,(160,1125),"Illustrative order; timing is not a latency measurement.",44,MUTED)
    return im


def preview(data):
    grasp_frame(data,630).save(REVIEW/"matched_grasp_preview.png")
    grasp_frame(data,705).save(REVIEW/"matched_grasp_missing_preview.png")
    trace_frame(data,12*FPS).save(REVIEW/"matched_frame_preview.png")
    trace_frame(data,32*FPS).save(REVIEW/"matched_frame_merge_preview.png")
    print("PASS: matched evidence previews")


def encode(data,only=None):
    results=[]
    for name,section,renderer,poster_idx in [
        ("matched_grasp","grasp",lambda i:grasp_frame(data,data["grasp"]["output_source_frames"][i],i),60),
        ("matched_frame_journey","frame_journey",lambda i:trace_frame(data,i),12*FPS),
        ("matched_elbow_constraints","elbow_constraints",lambda i:elbow_frame(data,i),212)]:
        mapping=data[section]["output_source_frames"]
        out=MEDIA/(name+".mp4")
        if only is None or only==name:
            p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","rgb24",
                                "-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264",
                                "-preset","medium","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",str(out)],stdin=subprocess.PIPE)
            for idx in range(len(mapping)):
                image=renderer(idx)
                p.stdin.write(image.tobytes())
            p.stdin.close()
            assert p.wait()==0
            renderer(poster_idx).save(out.with_suffix(".png"))
        poster=out.with_suffix(".png")
        assert out.exists() and poster.exists()
        subprocess.run(["ffmpeg","-v","error","-i",str(out),"-f","null","-"],check=True)
        info=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-of","json",str(out)]))
        stream=info["streams"][0]
        assert len(info["streams"])==1 and stream["codec_name"]=="h264"
        assert [stream["width"],stream["height"]]==[W,H] and int(stream["nb_frames"])==len(mapping)
        map_path=PROV/(name+"_frames.csv")
        with map_path.open("w",newline="",encoding="ascii") as f:
            writer=csv.writer(f);writer.writerow(["output_frame","output_time_s","source_frame","same_frame_both_panels"])
            for idx,src in enumerate(mapping):writer.writerow([idx,"%.6f"%(idx/FPS),src,True])
        results.append({"name":name,"path":rel(out),"poster":rel(poster),"sha256":sha(out),"poster_sha256":sha(poster),
                        "duration_s":len(mapping)/FPS,"frames":len(mapping),"width":W,"height":H,"fps":FPS,
                        "frame_map":rel(map_path),"frame_map_sha256":sha(map_path),"full_decode":"PASS"})
        print("PASS:",name,len(mapping),"frames",flush=True)
    report={"status":"PASS","evidence_manifest":rel(PROV/"matched_evidence.json"),
            "evidence_manifest_sha256":sha(PROV/"matched_evidence.json"),"generator_sha256":sha(Path(__file__)),
            "assets":results,"checks":data["checks"],
            "payload_motion":{"status":"schematic, not a runtime or latency trace",
                              "stage_intervals_s":[[s[0],s[1],s[4]] for s in TRACE_STAGES],
                              "general_motion_fraction":[0.16,0.80],
                              "person_copy_motion_fraction":[0.08,0.43],
                              "object_copy_motion_fraction":[0.53,0.88],
                              "derived_type_change_fractions":[0.30,0.65],
                              "merge_type_change_fraction":0.55,
                              "interpolation":"cubic smoothstep along reserved card-body paths",
                              "source_retention":"Shared RGB-D is drawn intact throughout both private-copy handoffs.",
                              "byte_scale":False},
            "limits":["No anatomical ground truth or new accuracy result.","Grasp target is not final-solver-use proof.",
                      "Camera freezes and slow motion are labelled editorial changes.","Frame-trace arrow order is schematic, not a scheduler/latency recording."]}
    write_json(REVIEW/"MATCHED_EVIDENCE_CHECK.json",report)


def main():
    parser=argparse.ArgumentParser();parser.add_argument("stage",choices=["extract","derive","preview","build","elbow"])
    args=parser.parse_args()
    if args.stage=="extract":return extract_r7()
    if args.stage=="derive":data=add_elbow_constraints(derive());preview(data);return
    data=json.loads((PROV/"matched_evidence.json").read_text())
    if args.stage=="preview":preview(data)
    elif args.stage=="elbow":
        data=add_elbow_constraints(data)
        elbow_frame(data,212).save(REVIEW/"matched_elbow_preview.png")
    else:encode(data)


if __name__=="__main__":main()
