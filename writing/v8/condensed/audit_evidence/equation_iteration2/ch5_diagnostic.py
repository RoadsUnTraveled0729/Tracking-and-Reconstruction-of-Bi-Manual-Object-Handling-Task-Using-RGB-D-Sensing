"""Independent Chapter 5 equation audit; writes only sibling ch5 evidence.

Run with /home/luo/anaconda3/bin/python -B <this file>.
Diagnostic sampling constants are coverage choices, not experiment thresholds.
The full-precision tolerance 1e-9 and serialized comparison tolerance 2e-6
are the established thesis diagnostics in D-072. Two-decimal checks use the
rounding half-unit 0.005, not a measurement acceptance threshold.
"""
import ast
import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
import numpy as np
import pandas as pd
from lxml import etree

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
for subdir in ("writing/v8/condensed/scripts", "writing/v8/scripts",
               "eval/failure", "eval/common", "eval/offset", "v1/kinematics"):
    sys.path.insert(0, str(REPO / subdir))
import carry
import grip_state
import paths
import recovery_core as rc
from fit_offset import load_tracks
from occlusion_ext import RobustChainSolver, TAG_CONSTRAINED

OUT = {"purpose": "Independent equation and worked-number audit, second iteration",
       "diagnostic_constants": {"seed": 513, "random_cases": 200,
                                "circle_samples": 721, "full_precision": 1e-9,
                                "serialized_tolerance": 2e-6,
                                "stored_angle_half_unit": .00005},
       "checks": {}, "observations": {}}
FILES = set()


def source(path):
    path = Path(path)
    FILES.add(path)
    return path


def check(name, condition, detail=None):
    OUT["checks"][name] = {"pass": bool(condition), "detail": detail}


def norm(v):
    return float(np.linalg.norm(v))


def close(a, b, tol=1e-9):
    return bool(np.allclose(a, b, atol=tol, rtol=0))


def rotation(rng):
    q, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    q[:, -1] *= np.linalg.det(q)
    return q


def scalar_plain(fragment):
    root = etree.fromstring(('<root xmlns:m="http://schemas.openxmlformats.org/'
                             'officeDocument/2006/math">' + fragment + '</root>').encode())
    return ''.join(root.itertext()).replace('\u200b', '')


# Evaluate only the declarative content, without running the DOCX builder.
builder = source(REPO / "writing/v8/condensed/scripts/build_ch5.py")
tree = ast.parse(builder.read_text())
content_node = next(node for node in tree.body if isinstance(node, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "content"
                            for t in node.targets))
namespace = {"__file__": str(builder)}
exec(compile(ast.Module(body=tree.body[:tree.body.index(content_node) + 1],
                        type_ignores=[]), str(builder), "exec"), namespace)
inventory = []
for idx, (item, node) in enumerate(zip(namespace["content"], content_node.value.elts)):
    kind = item[0]
    entry = {"content_index": idx, "source_line": node.lineno, "kind": kind}
    if kind in ("eq", "mth"):
        entry["text"] = scalar_plain(item[1])
        if kind == "eq":
            entry["number"] = item[2]
    elif kind == "pm":
        entry["text"] = ''.join(x if k == "t" else scalar_plain(x) for k, x in item[1])
        entry["inline_math_count"] = sum(k == "m" for k, _ in item[1])
    elif kind == "tbl":
        entry["rows"] = [[scalar_plain(x[1]) if isinstance(x, tuple) else x
                          for x in row] for row in item[1]]
    else:
        entry["text"] = str(item[1])
        if kind == "img":
            source(item[1])
    inventory.append(entry)
OUT["inventory"] = inventory
OUT["inventory_counts"] = {kind: sum(i["kind"] == kind for i in inventory)
                           for kind in sorted({i["kind"] for i in inventory})}
OUT["inventory_counts"]["inline_math"] = sum(i.get("inline_math_count", 0) for i in inventory)
check("all_twelve_numbered_equations", [i.get("number") for i in inventory if i["kind"] == "eq"]
      == [f"5.{n}" for n in range(1, 13)])

rng = np.random.default_rng(513)
S = np.array([[1., 0, 0], [0, 0, 1], [0, 1, 0]])
F = np.diag([1., -1., 1.])
rot = np.array([rotation(rng) for _ in range(200)])
o = rng.normal(size=(200, 3))
hobs = rng.normal(size=(200, 3))
w = o + np.einsum("nij,nj->ni", rot, hobs)
back = np.einsum("nji,nj->ni", rot, w - o)
hmean = hobs.mean(axis=0)
hls = np.linalg.lstsq(rot.reshape(-1, 3), (w-o).reshape(-1), rcond=None)[0]
trial = rng.normal(size=3)
objective_world = float(np.square(w-o-np.einsum("nij,j->ni", rot, trial)).sum())
objective_local = float(np.square(hobs-trial).sum())
gradient = 2 * np.sum(hmean-hobs, axis=0)
check("5.1_5.2_offset_inverse", close(hobs, back), np.max(abs(hobs-back)).item())
check("5.3_least_squares_and_objective", close(hmean, hls) and abs(objective_world-objective_local) < 1e-9
      and norm(gradient) < 1e-9,
      {"mean_vs_lstsq": norm(hmean-hls), "objective_difference": objective_world-objective_local,
       "gradient_norm": norm(gradient), "hessian_eigenvalues": [400., 400., 400.]})
check("mapped_axes_and_chirality", close(S @ S, np.eye(3)) and np.linalg.det(S) == -1
      and np.linalg.det(F) == -1 and all(abs(np.linalg.det(S @ r @ S)-1)<1e-9 for r in rot))
old = np.array([1., 0, 0])
new = np.array([-1., 0, 0])
blend = .7 * old + .3 * new
check("5.5_normalization_safe_at_gain_0.30", norm(blend) >= .4 - 1e-15,
      {"minimum_denominator_from_reverse_triangle_inequality": .4,
       "equal_directions_denominator": 1., "opposite_directions_denominator": norm(blend)})
check("5.6_unit_memory_preserves_forearm_length", abs(norm((np.array([.4,.5,.6])+.205*old)-np.array([.4,.5,.6]))-.205)<1e-9)


# Independent sphere subtraction derivation, not the production cosine path.
def sphere_elbow(shoulder, wrist, L1, L2, prior):
    distance = norm(wrist-shoulder)
    direction = (wrist-shoulder)/distance
    along = (L1**2-L2**2+distance**2)/(2*distance)
    centre = shoulder + along*direction
    radius = np.sqrt(max(0., L1**2-along**2))
    projection = prior-np.dot(prior,direction)*direction
    return centre + radius*projection/norm(projection), centre, radius, direction, projection


solver = RobustChainSolver()
length_error = []
implementation_error = []
minimum_margins = []
for _ in range(200):
    shoulder = rng.normal(size=3)
    L1, L2 = rng.uniform(.1, .8, size=2)
    distance = rng.uniform(abs(L1-L2)+.001, L1+L2-.001)
    direction = rng.normal(size=3); direction /= norm(direction)
    wrist = shoulder+distance*direction
    prior = rng.normal(size=3); prior /= norm(prior)
    elbow, centre, radius, direction, projection = sphere_elbow(shoulder,wrist,L1,L2,prior)
    actual = solver._ik_elbow(shoulder,wrist,L1,L2,prior)
    n1 = projection/norm(projection)
    n2 = np.cross(direction,n1)
    theta = np.linspace(0,2*np.pi,721)
    candidates = centre+radius*(np.cos(theta)[:,None]*n1+np.sin(theta)[:,None]*n2)
    target = shoulder+L1*prior
    minimum_margins.append(float(np.min(np.sum((candidates-target)**2,axis=1))-norm(elbow-target)**2))
    implementation_error.append(norm(actual-elbow))
    length_error.extend([abs(norm(elbow-shoulder)-L1), abs(norm(elbow-wrist)-L2)])
check("5.8_5.12_random_reachable_geometry", max(length_error)<1e-9 and max(implementation_error)<1e-9
      and min(minimum_margins)>-1e-9,
      {"maximum_link_error_m":max(length_error), "maximum_implementation_difference_m":max(implementation_error),
       "minimum_sample_objective_margin_m2":min(minimum_margins)})
boundary = {}
for name, L1, L2, distance, prior in [
    ("outer_tangent",.317,.205,.522,[0,-1,0]),
    ("inner_tangent_upper_longer",.317,.205,.112,[0,-1,0]),
    ("beyond_outer",.317,.205,.7,[0,-1,0]),
    ("inside_inner_upper_longer",.317,.205,.05,[0,-1,0]),
    ("inside_inner_forearm_longer",.205,.317,.05,[0,-1,0]),
    ("parallel_memory_downward_fallback",.317,.205,.4,[1,0,0]),
    ("coincident_unequal_links",.317,.205,0,[0,-1,0]),
    ("coincident_equal_links",.25,.25,0,[0,-1,0])]:
    shoulder=np.zeros(3);wrist=np.array([distance,0.,0.])
    elbow=solver._ik_elbow(shoulder,wrist,L1,L2,np.array(prior,float))
    boundary[name]={"L1":L1,"L2":L2,"distance":distance,"elbow":elbow,
                    "upper_length":None if elbow is None else norm(elbow-shoulder),
                    "forearm_length":None if elbow is None else norm(elbow-wrist)}
OUT["observations"]["ik_boundaries"] = boundary
check("5.8_5.12_boundaries_match_declared_fallback", boundary["coincident_unequal_links"]["elbow"] is None
      and boundary["coincident_equal_links"]["elbow"] is None
      and abs(boundary["beyond_outer"]["upper_length"]-.317)<1e-9
      and abs(boundary["inside_inner_upper_longer"]["forearm_length"]-.267)<1e-9)
near=[]
for gap in (.01,.001,.0001,.00001):
    L1,L2=.317,.205;distance=L1+L2-gap
    cosine=(L1**2+distance**2-L2**2)/(2*L1*distance)
    derivative=-(1-(L1**2-L2**2)/distance**2)/(2*L1*np.sqrt(1-cosine**2))
    near.append({"distance":distance,"dj_dr_rad_per_m":derivative})
OUT["observations"]["straight_arm_derivative"] = near
check("5.9_sensitivity_grows_near_extension", all(abs(near[i+1]["dj_dr_rad_per_m"])>abs(near[i]["dj_dr_rad_per_m"]) for i in range(3)))


# Concrete proof that the EMA target and the last measured elbow differ.
shoulder=np.zeros(3);wrist=np.array([.4,0.,0.]);last_elbow=np.array([0.,-.317,0.])
memory=np.array([0.,0.,1.])
elbow,centre,radius,direction,projection=sphere_elbow(shoulder,wrist,.317,.205,memory)
actual_last_minimizer,_,_,_,_=sphere_elbow(shoulder,wrist,.317,.205,last_elbow/.317)
OUT["observations"]["5.12_memory_target_not_last_elbow"]={
    "shoulder":shoulder,"wrist":wrist,"ema_direction":memory,"last_measured_elbow":last_elbow,
    "memory_choice":elbow,"closest_to_last_measured":actual_last_minimizer,
    "memory_choice_distance_to_last":norm(elbow-last_elbow),
    "alternative_distance_to_last":norm(actual_last_minimizer-last_elbow)}


# Current implementation uses a child-visibility counter, not segment-memory age.
stale=RobustChainSolver(seg_len={"forearm_R":.205})
stale.u["forearm_R"]=np.array([1.,0,0]);stale.k["right_wrist"]=1
p={};recovered=set()
stale._try_recover(p,"right_wrist",np.zeros(3),"forearm_R","forearm_R",recovered)
OUT["observations"]["memory_counter_scope"]={"child_unmeasured_count":1,
    "direction_update_age_example":100,"recovered_despite_old_direction": bool(recovered),
    "explanation":"A wrist can remain measured while its elbow is absent, resetting child k without refreshing forearm direction."}
for missing in (45,46):
    stale.k["right_wrist"]=missing;p={};recovered=set()
    stale._try_recover(p,"right_wrist",np.zeros(3),"forearm_R","forearm_R",recovered)
    OUT["observations"][f"memory_horizon_at_{missing}"] = bool(recovered)


# Five observations override the episode/global fallback even when fewer than 15.
dlocal=np.column_stack([np.linspace(.01,.02,10),np.zeros(10),np.zeros(10)])
global_mu=np.array([.12,0,0]);episodes=[(0,9)];clean=np.ones(10,bool)
fits=grip_state.fit_episode_mu(episodes,dlocal,clean,global_mu)
local=grip_state.time_local_mu(dlocal,clean,episodes)
combined=local.copy();gaps=~np.isfinite(combined).all(axis=1)
combined[gaps]=grip_state.per_frame_mu(10,fits)[gaps]
OUT["observations"]["short_episode_fallback_scope"]={"episode_fit_source":fits[0]["source"],
    "clean_count":10,"global_mu":global_mu,"combined_offset":combined,
    "global_fallback_frame_indices":np.flatnonzero(gaps),"first_local_frame_index":4}


# Full recording inputs and fresh solver replay. All arithmetic below is derived
# here; no values are imported from the existing worked-example diagnostic.
for stem in (paths.R6B_STEM,paths.R5_STEM):
    inp=rc.build_inputs(stem)
    calib,world,lm,obj,R,det,wr,flags,t=load_tracks(stem,str(paths.calib_for(stem)))
    n=inp["n"]
    fm_path=source(paths.EVAL_OUT/f"recovery_{paths.ALIAS[stem]}"/"failure_mask.csv")
    fm=pd.read_csv(fm_path).iloc[:n]
    for path in (paths.calib_for(stem),paths.MP_OUT/f"{stem}_landmarks_filtered.csv",
                 paths.object_world_filtered(stem),paths.EVAL_REPORTS/f"{stem}_offset_fit.json",
                 paths.EVAL_REPORTS/f"{stem}_inspection.json"):
        source(path)
    overlap={}
    for side in ("left","right"):
        global_hold=carry.holding_mask(inp["center"],wr[side],flags[side],det,inp["carried"],carry.forearm_ok(lm,side))
        failures=fm["fail_arm_"+("L" if side=="left" else "R")].to_numpy(bool)
        overlap[side]={"global_fit_hold_frames":int(global_hold.sum()),
                       "overlap_with_cleaned_arm_failure_mask":int((global_hold&failures).sum()),
                       "first_overlap_frames":np.flatnonzero(global_hold&failures)[:20],
                       "actual_episode_fits":[{"start":e["start"],"stop":e["stop"],"n_clean":e["n_clean"],"source":e["source"]} for e in inp["episode_fits"][side]]}
    OUT["observations"][f"global_fit_mask_{stem}"]=overlap
    if stem!=paths.R6B_STEM:
        report=json.loads((paths.EVAL_REPORTS/f"{stem}_offset_fit.json").read_text())
        check("5.3_loop_scatter_pinned",report["per_hand"]["left"]["std_cm"]==[7.0,2.7,6.3],report["per_hand"]["left"])
        continue
    f=560;solver=RobustChainSolver(seg_len=dict(inp["seg_len"]))
    for i,row in lm.iloc[:f+1].iterrows():
        pts=rc.solver_points(row,{s:bool(inp["fail"][s][i]) for s in rc.SIDES})
        obs={s:inp["w_hat_solver"][s][i] if np.isfinite(inp["w_hat_solver"][s][i]).all() else None for s in rc.SIDES}
        if i==f:
            memory=solver.u["upper_arm_R"].copy();shoulder=pts["right_shoulder"].copy()
            memory_k=solver.k["right_elbow"]
        angles,mask,tags=solver.solve(pts,obj=obs)
    row=lm.iloc[f]
    forearm_vec=lm[[f"right_wrist_{x}" for x in "xyz"]].to_numpy()-lm[[f"right_elbow_{x}" for x in "xyz"]].to_numpy()
    forearm_len=np.linalg.norm(forearm_vec,axis=1);forearm_median=np.nanmedian(forearm_len)
    clean=det&inp["carried"]&(flags["right"]==0)&(np.linalg.norm(wr["right"]-inp["center"],axis=1)<.25)&(abs(forearm_len-forearm_median)<.30*forearm_median)&~fm["fail_arm_R"].to_numpy(bool)
    episode=next((a,b) for a,b in inp["episodes"]["right"] if a<=f<=b)
    acc=[];h=None
    for i in range(episode[0],f+1):
        if clean[i]:
            measurement=R[i].T@(wr["right"][i]-obj[i])
            if h is None:
                acc.append(measurement)
                if len(acc)==5:h=np.mean(acc,axis=0)
            else:h=.98*h+.02*measurement
    last_clean=int(np.flatnonzero(clean[:f+1])[-1])
    rotated=R[f]@h;wlevel=obj[f]+rotated
    T_world_camera=np.linalg.inv(np.array(calib["T_cam_desk"]))
    T_level_camera_prime=np.eye(4)
    T_level_camera_prime[:3,:3]=world.G@S@T_world_camera[:3,:3]@F
    T_level_camera_prime[:3,3]=world.G@S@T_world_camera[:3,3]
    T_camera_prime_level=np.linalg.inv(T_level_camera_prime)
    wp=(T_camera_prime_level@np.r_[wlevel,1])[:3]
    L1,L2=inp["seg_len"]["upper_arm_R"],inp["seg_len"]["forearm_R"]
    elbow,centre,radius,bhat,perp=sphere_elbow(shoulder,wp,L1,L2,memory)
    distance=norm(wp-shoulder);cosine=(L1**2+distance**2-L2**2)/(2*L1*distance)
    lastrow=lm.iloc[549]
    lastw=lastrow[[f"right_wrist_{x}" for x in "xyz"]].to_numpy(float)*[1,-1,1]
    laste=lastrow[[f"right_elbow_{x}" for x in "xyz"]].to_numpy(float)*[1,-1,1]
    stored_path=source(paths.EVAL_OUT/"recovery_r6b"/"angles_recovery.csv")
    stored=pd.read_csv(stored_path).iloc[f]
    anglecols=["root_ex","root_ey","root_ez","Rsh_y","Rsh_z","Rsh_tau","Rel_y","Rel_z","Lsh_y","Lsh_z","Lsh_tau","Lel_y","Lel_z"]
    object_df=pd.read_csv(paths.object_world_filtered(stem))
    objrow=object_df.iloc[f]
    Rworld=objrow[[f"r{i}{j}" for i in (1,2,3) for j in (1,2,3)]].to_numpy(float).reshape(3,3)
    raw_origin=objrow[["tx","ty","tz"]].to_numpy(float)
    worked={"frame":f,"time_s":t[f],"shoulder":shoulder,"L1":L1,"L2":L2,"object_origin_levelled":obj[f],
       "R_levelled_mappedmarker":R[f],"h":h,"h_norm":norm(h),"last_clean_offset":last_clean,"R_h":rotated,
       "w_levelled":wlevel,"T_levelled_camera_prime":T_level_camera_prime,"T_camera_prime_levelled":T_camera_prime_level,
       "w_camera_prime":wp,"b":wp-shoulder,"r":distance,"reach_ratio":distance/(L1+L2),"bhat":bhat,
       "cos_j":cosine,"j_degrees":float(np.degrees(np.arccos(cosine))),"centre":centre,"radius":radius,
       "diameter":2*radius,"memory":memory,"memory_counter_before_frame":memory_k,"u_dot_bhat":float(memory@bhat),
       "u_perp":perp,"u_perp_norm":norm(perp),"elbow":elbow,"upper_length":norm(elbow-shoulder),
       "forearm_length":norm(elbow-wp),"last_wrist_distance_m":norm(wp-lastw),"last_elbow_distance_m":norm(elbow-laste),
       "upper_direction_to_memory_degrees":float(np.degrees(np.arccos(np.clip(np.dot((elbow-shoulder)/L1,memory),-1,1)))),
       "flexion_geometry_degrees":float(np.degrees(np.arccos(np.clip(np.dot(elbow-shoulder,wp-elbow)/(L1*L2),-1,1)))),
       "angles":angles,"tags":tags,"maximum_stored_angle_difference_degrees":float(np.max(abs(angles-stored[anglecols].to_numpy(float)))),
       "tilt_degrees":float(np.degrees(np.arccos(world.g@np.array([0.,1,0]))))}
    OUT["worked_example"]=worked
    check("5.6_frame_chain_from_calibration",close(T_camera_prime_level[:3,:3],np.linalg.inv(world.M)@world.G.T)
          and close(T_camera_prime_level[:3,3],-np.linalg.inv(world.M)@world.cam_pos)
          and close(wp,inp["w_hat_solver"]["right"][f]) and close(wp,solver.last_points["right_wrist"])
          and close(T_camera_prime_level@T_level_camera_prime,np.eye(4)))
    check("5.6_object_world_swap_level",close(obj[f],world.G@S@raw_origin)
          and close(R[f],world.G@S@Rworld@S,2e-6),
          {"serialized_matrix_max_diff":np.max(abs(R[f]-world.G@S@Rworld@S)).item()})
    check("5.6_independent_ik_vs_pipeline",close(elbow,solver.last_points["right_elbow"]),norm(elbow-solver.last_points["right_elbow"]))
    # angles_recovery.csv stores four decimal places: use half a stored unit,
    # independently of the full-precision analytic geometry checks above.
    check("5.6_stored_angles_and_tags",worked["maximum_stored_angle_difference_degrees"]<=.00005
          and list(tags[:4])==[TAG_CONSTRAINED]*4,
          worked["maximum_stored_angle_difference_degrees"])
    printed={"shoulder":[-.16,.34,1.32],"object_origin_levelled":[-.22,.08,.45],
       "R_levelled_mappedmarker":[[1,.03,.04],[-.04,-.09,.99],[.03,-1,-.09]],
       "h":[.01,-.04,.05],"h_norm":.07,"R_h":[.01,.06,.04],"w_levelled":[-.21,.13,.48],
       "T_camera_prime_levelled":[[1,-.04,.02,.02],[.04,1,-.05,-.19],[-.02,.05,1,.55],[0,0,0,1]],
       "w_camera_prime":[-.19,-.09,1.04],"b":[-.02,-.43,-.27],"r":.51,"bhat":[-.04,-.84,-.54],
       "cos_j":.98,"centre":[-.18,.07,1.15],"radius":.06,"memory":[-.11,-.91,-.39],
       "u_dot_bhat":.98,"u_perp":[-.07,-.09,.14],"u_perp_norm":.18,"elbow":[-.20,.05,1.20]}
    rounding={k:{"max_difference":float(np.max(abs(np.asarray(worked[k])-v))),
                 "within_half_0.01":bool(np.max(abs(np.asarray(worked[k])-v))<=.005+1e-12)} for k,v in printed.items()}
    OUT["worked_rounding"]=rounding
    check("5.6_all_printed_two_decimal_quantities",all(v["within_half_0.01"] for v in rounding.values()),rounding)
    check("5.6_scalar_worked_numbers",round(worked["j_degrees"],1)==11.0
          and round(worked["upper_direction_to_memory_degrees"],1)==.7
          and round(-worked["flexion_geometry_degrees"],1)==-28.1
          and round(1000*worked["last_elbow_distance_m"])==6
          and round(100*worked["last_wrist_distance_m"])==3
          and round(100*worked["reach_ratio"])==97)


for path in (REPO/"writing/v8/Thesis_V8_Condensed.docx",REPO/"writing/v8/Thesis_V8_Condensed.pdf",
             REPO/"writing/v8/condensed/Chapter_5_Pose_Recovery.docx",
             REPO/"writing/v8/condensed/DECISIONS.md",REPO/"writing/v8/condensed/DELIVERY_2026-09-12.md"):
    source(path)
for module in list(sys.modules.values()):
    file=getattr(module,"__file__",None)
    if file and Path(file).is_relative_to(REPO):source(file)
FILES.add(Path(__file__).resolve())
OUT["input_hashes"]={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(FILES)}
OUT["summary"]={"pass":sum(v["pass"] for v in OUT["checks"].values()),
                "fail":sum(not v["pass"] for v in OUT["checks"].values())}


def encode(value):
    if isinstance(value,np.ndarray):return value.tolist()
    if isinstance(value,np.generic):return value.item()
    raise TypeError(type(value).__name__)


(HERE/"ch5_diagnostic.json").write_text(json.dumps(OUT,indent=2,default=encode,ensure_ascii=True)+"\n")
print(json.dumps(OUT["summary"]))
for name,result in OUT["checks"].items():
    print(("PASS" if result["pass"] else "FAIL")+" "+name)
