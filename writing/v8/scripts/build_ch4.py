#!/usr/bin/env python3
"""Build writing/v8/Chapter_4_Object_Tracking.docx (V8 rewrite round).

Chapter 4 against the V8 TOC: 4.1 Static Scene Calibration, 4.2 World
Anchoring and Camera Placement Invariance, 4.3 Filtering and Cleaning
the Object Track, 4.4 Worked Example.

Method only (skill_set/thesis-structure-rules.md): no validation
results, no accuracy or error numbers, no coverage counts.  Detection
and planar pose recovery point to Appendix E, deprojection of depth
pixels to Appendix D, the Unity axis conversion to Chapter 6, and the
trajectory evaluation to Chapter 7.

Every printed number comes from writing/v7/scripts/ch4_numbers.py,
which recomputes it from the rail-recording artifacts (raw scaled ArUco
detections, scene_calibration_r6bc.json after the E-024 wall-lobe fix,
the filtered and the cleaned object track). Rail-only round 2026-09-01:
the worked example uses the scene frame of Figure 2.5 (frame 533, the
Chapter 3 worked-example frame) for the transformation chain and the
one undetected frame of the recording (frame 786, bridged by the filter
and blanked by the cleaning rule; frame 779 a despiked-and-bridged
detection kept with its flag) for the filtering and the cleaning step.
The rule of E-019 rejects no detected sample on this recording; the
held case (a run longer than the bridging limit) does not occur here
and is described as the case the occlusion scenario of Chapter 7 shows.
The old loop-recording example (frame 1236, handover frames 1065-1105)
is in git history before this round.

Figures: writing/v8/scripts/make_ch4_figs.py.
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

from eqn import r, nor, sub, sup, hat, frac, mat, d, eqArr, \
    add_display_eq, add_display_math, add_inline_math

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v8" / "figures"

H1, H2, H3, P, IMG, CAP, TBL, EQ = "h1", "h2", "h3", "p", "img", "cap", "tbl", "eq"
MATH = "mth"  # displayed, unnumbered worked-example mathematics
PM = "pm"     # paragraph mixing text runs and inline math


def T(t):
    return ("t", t)


def X(f):
    return ("m", f)


# --- equation-fragment shorthands ---
TCW = sub(r("T"), nor("CW"))
TCO = sub(r("T"), nor("CO"))
TWO = sub(r("T"), nor("WO"))
TWC = sub(r("T"), nor("WC"))
RT = sup(r("R"), r("T"))


def bar(e):
    """Overbar accent (mean matrix); the shared equation helpers have none."""
    return ('<m:acc><m:accPr><m:chr m:val="\u0304"/></m:accPr>'
            f'<m:e>{e}</m:e></m:acc>')


p_i = sub(r("p"), r("i"))
p_l = sub(r("p"), nor("last"))
R_i = sub(r("R"), r("i"))
R_l = sub(r("R"), nor("last"))
t_i = sub(r("t"), r("i"))
t_l = sub(r("t"), nor("last"))
v_max = sub(r("v"), nor("max"))
w_max = sub(r("w"), nor("max"))
zeroT = sup(r("0"), r("T"))


Mbar = bar(r("M"))


def num_mat(rows):
    return mat([[r(c) for c in row] for row in rows])


content = [
(H1, "Chapter 4: Object Tracking and Scene Reconstruction"),

(P, "Chapter 2 left the marker branch at its raw product: for every colour frame, the pose of each detected marker relative to the camera. Those poses are enough to draw a marker on an image and nothing more. Chapter 2 also fixed the static part of the scene, the desk marker as the world frame and the wall marker as the vertical, in the calibration of Section 2.2.2. This chapter turns the per-frame marker poses into the one thing the rest of the thesis consumes from Pipeline B: a clean track of the carried object, expressed in the world frame attached to the desk instead of to the camera, so that the camera's placement never enters the result."),

(P, "Section 4.1 builds the transformation chain that carries the moving object into the world frame, and shows why camera placement drops out of it. Section 4.2 covers how the object track is filtered and the single cleaning step that closes the marker branch. A worked example on measured frames closes the chapter. Appendix E covers how a detection becomes a pose: the detection stages, the sub-pixel corner refinement, the planar pose estimation, and the two-solution ambiguity that appears when a marker is nearly face-on. This chapter describes how those poses are used."),

(H2, "4.1 World Anchoring and Camera Placement Invariance"),

(P, "The static calibration of Section 2.2.2 fixed the world frame at the desk marker and listed the frozen scene quantities in Table 2.3. Every pose the detector returns is expressed relative to the camera, which is the wrong frame for a reconstruction. Consider the same cube resting at the same place on the desk, recorded twice with the camera set up in two different corners of the room. Nothing in the scene has changed, yet the camera-relative pose of the cube differs between the two recordings, and a reconstruction driven by that pose would put the cube in a different place each time. The object must be expressed relative to something fixed in the scene instead, and the fixed reference chosen here is the desk marker's own frame, the world frame W. The chain therefore involves three frames, and Figure 2.5 draws all three on one measured frame: the camera frame C, the world frame W at the desk marker, and the object frame O on the cube, which moves with it."),

(PM, [T("Each pose is packaged as the 4 by 4 homogeneous transformation of Chapter 3, with the rotation in the top left block and the translation in the top right column. The anchor and the object pose are both available on any frame on which the cube is seen. The calibrated anchor "),
      X(TCW), T(" maps a point of the world frame into camera coordinates, and the per-frame object pose "),
      X(TCO), T(" maps a point of the object frame into camera coordinates. The chain must deliver "),
      X(TWO), T(", the object as seen from the world. Only one path connects the two frames, from the object into the camera and from the camera into the world, and walking it gives")]),

(EQ, TWO + r(" = ") + sup(TCW, r("−1")) + r(" ") + TCO, "4.1"),

(PM, [T("The first factor reverses the direction of the calibrated transformation. Inverting a homogeneous transformation is cheap enough to derive in two lines rather than hand to a general matrix inverse. Suppose the inverse has the same rigid form, some rotation followed by some translation d. Multiplying the candidate against the original and requiring the identity gives two conditions, one per block. The rotation blocks must multiply to the identity, which the transpose achieves, because a rotation matrix is orthonormal. The translation blocks must satisfy "),
      X(RT + r(" ") + r("t") + r(" + ") + r("d") + r(" = 0")),
      T(", and moving the first term to the right side gives "), X(r("d") + r(" = −") + RT + r(" ") + r("t")),
      T(". The inverse is therefore a transpose and one matrix-vector product:")]),

(EQ, r("T") + r(" = ") + mat([[r("R"), r("t")], [zeroT, r("1")]]) + r(",        ") +
     sup(r("T"), r("−1")) + r(" = ") +
     mat([[RT, r("−") + RT + r(" ") + r("t")], [zeroT, r("1")]]), "4.2"),

(PM, [T("Applied to the anchor, the inverse has a direct physical reading. Its translation column is the camera's own position in the world frame, so the camera pose in the reconstructed scene, "),
      X(TWC), T(", comes out of the anchoring, and nothing measures it separately. Chapter 6 places the sensor in the Unity scene at that pose.")]),

(P, "The chain makes the reconstruction independent of where the camera is set up. Both measured transformations change when the camera is placed somewhere else. The camera frame, however, enters the chain twice, once as the destination of the object pose and once as the source of the inverted anchor. The two contributions cancel, and the remainder depends only on where the cube is relative to the desk. The two contributions cancel only if the anchor and the object pose are measured from the same camera position. On a recording the anchor is the frozen one of Section 2.2.2, measured over the calibration window, so the reconstruction is invariant to where the camera was placed before that window and not to a camera moved after it. The camera stands on a fixed support at the desk edge for the whole session, and the recording is made that way. The camera cancels whether or not the anchor is frozen; the anchor is frozen for the noise reason of Section 2.2.2."),

(P, "The world frame and the Unity frame are defined in Section 2.2.1, and Chapter 6 converts the poses from one to the other before anything is drawn. This section produces one world-frame object pose per frame. That conversion is developed in Chapter 6. This section produces one world-frame object pose per frame."),

(H2, "4.2 Filtering and Cleaning the Object Track"),

(P, "The world-frame track is complete, in the sense that it holds one entry per frame with a flag saying whether the marker was seen, but it is not yet fit to drive a reconstruction. The track passes two stages, in order. The first is a signal filter, the counterpart for Pipeline B of the landmark filtering of Section 2.5. The second is a single cleaning step against marker failure."),

(P, "The signal filter treats the same three cases as the landmark filter, with rotation added to each. Case A, a spiked sample, is caught by a rolling Hampel test on position [53], [54]. A spiked pose solution is wrong as a whole, so its rotation is dropped along with its position. Case B, a short run of missing samples, is bridged: position along a straight line in time, and rotation along the shortest turn from one endpoint rotation to the other, taken in proportion to the elapsed time. A run at either end of the recording has a valid pose on one side only, so it holds a fixed pose instead of inventing one: the first valid pose of the recording at the start, the last valid pose at the end. A run in the interior that is longer than the bridging limit holds the previous valid pose for its whole length, which is the nearest valid pose before the run. Case C, jitter, is smoothed. Position goes through a Savitzky-Golay filter, which fits a low-order polynomial over a sliding window and takes its value at the centre [46]. Rotation goes through a rolling chordal mean, which is equation (2.1) applied to a short window instead of to the calibration window. The detection flag passes through every stage unchanged. A row on which the marker was never seen therefore stays marked as not detected whether the filter bridged it or held it. A sample the despike step invalidated keeps the flag it came in with while carrying the pose the bridge wrote over it. The raw track is written to its own output and never modified. Figure 4.1 shows the track before and after the filter."),

(IMG, FIG / "ch4_fig_track.png", 6.3),
(CAP, "Figure 4.1. The object track in the world frame before and after the signal filter, one panel per world axis. The grey line is the track as detected. The blue line is the filtered track, and the orange dots mark the eleven rows it bridges: ten detections the despike step invalidated, all in the jitter of the rail slide, and the one frame on which the marker is not seen. The marker is seen on 899 of the 900 frames, so no row is held."),

(P, "On the recording the hand never covers the marker, and the one undetected frame is bridged. The held case has a physical cause the recording does not show: when a hand closes over the printed marker, the detector returns nothing for a run of frames longer than the bridging limit, the filter holds rather than bridges, and the track stays where the cube was last seen until it is seen again. The occlusion scenario of Chapter 7 contains such runs."),

(P, "Holding leaves two cases for the end of the branch, and neither leaves a mark on the detection flag. The first is drift. A detected row beside a held run is smoothed together with that run, because the smoothing window crosses the boundary. Its pose can therefore drift from the detection on its own frame while the row goes on carrying the detected flag. The second is a partly covered marker, a case the recording does not show either: such a marker may still decode, and the pose that comes back from it need not be right. A stage that judges the poses themselves therefore has to close the branch."),

(P, "The response is a single cleaning step at the end of the marker branch, the only mechanism in the system that exists for marker failure. The despike step of the filter replaces an isolated outlier with an interpolated pose; the cleaning rule is the only stage that removes one. No later stage carries marker logic of its own: the recovery of Chapter 5, the streaming of Chapter 6, and the evaluation of Chapter 7 all read the same cleaned track. The marker is a standard input to this work, and the difficulty of the reconstruction lies on the person side, so the marker branch is kept to one filter."),

(P, "The rule is physical and carries no tuning to a particular recording. Walking the track forward, a sample is kept only if the marker was detected, its pose is finite, and it is separated from the last kept sample by no more than the task's slow movement can produce in the time between the two. Writing i for the candidate sample and last for the most recent kept one,"),

(EQ, eqArr(
    d(p_i + r(" − ") + p_l, "|", "|") + r(" ≤ ") + v_max + r(" ") +
    d(t_i + r(" − ") + t_l),
    nor("angle") + d(sup(R_l, r("T")) + r(" ") + R_i) + r(" ≤ ") + w_max +
    r(" ") + d(t_i + r(" − ") + t_l)), "4.3"),

# src: eval/common/clean_object_track.py, V_MAX = 1.0 and W_MAX_DEG = 400.0;
#      the numeric rates and their per-frame allowances are not printed
#      (skill_set/thesis-structure-rules.md rule 1)
(PM, [T("The two bounds are rates rather than fixed steps. "), X(v_max),
      T(" bounds the linear step and "), X(w_max),
      T(" the angular step. Each is written as an allowance per unit of elapsed time, so the allowance between a kept sample and a candidate grows with the time between them. The reference is always the last kept sample rather than the previous row. A rejected sample therefore never becomes the reference for the next decision, and one bad pose cannot drag the track along behind it. Scaling the allowance by the elapsed time means a real occlusion, during which the cube does travel, does not make the rule refuse the marker when it is detected again. Both bounds are round values chosen with a margin of about two over the largest step the clean parts of the recording show, so the rule fires only on poses that no carried cube could have reached. The rule is a guard, and on a recording whose detections are all plausible it rejects nothing.")]),

(P, "A sample that fails the test has its pose columns blanked and its detection flag cleared, and so does every row on which the marker was never detected in the first place. The blanked columns are the pose columns every consumer reads. A consumer therefore reads filtered poses on the kept rows and blanks elsewhere, and on a blanked row it holds the last kept pose and flags it as held. Figure 4.2 shows both sides of the step around the one undetected frame of the recording."),

(IMG, FIG / "ch4_fig_clean.png", 6.3),
(CAP, "Figure 4.2. The cleaning step around the one undetected frame, world x against time. The upper panel is the track entering the step: the grey circles are the frames on which the marker was detected, the blue line is the filtered track, and the orange dots are the rows the filter bridges, one despiked detection at frame 779 and the undetected frame 786. The lower panel is the cleaned track a consumer reads, with the pose of the last kept sample held across the blanked row. The two panels differ only over the row that carries no detection."),

(H2, "4.3 Worked Example"),

(P, "The chapter is carried end to end by frames of the recording. The transformation chain runs on the scene image of Figure 2.5, frame 533, the worked-example frame of Chapter 3. On that frame the participant holds the cube against the rail and its marker is cleanly detected. The cleaning step runs on the one frame of the recording on which the marker is not detected, frame 786, in the middle of the rail slide. The same convention as Chapter 3 applies: values are computed from the unrounded pipeline data and printed rounded, so recomputing a step by hand from the printed inputs can differ in the last digit. Positions are printed in metres and matrix entries as plain numbers, both to four decimals, and lengths read off against the scene are printed in centimetres or millimetres to one decimal."),  # src: writing/v7/scripts/ch4_numbers.py (rail recording, frames 533 and 786)

(P, "The calibration window comes first. Averaging the ten desk rotations of the window element by element gives"),
(MATH, Mbar + r(" = ") + num_mat([  # src: writing/v7/scripts/ch4_numbers.py, element-wise mean over eval/output/recording_20260831_065553_aruco_raw_scaled.csv
    ["0.9997", "−0.0014", "−0.0243"],
    ["−0.0219", "−0.4832", "−0.8752"],
    ["−0.0105", "0.8755", "−0.4831"]])),
(P, "which is not a rotation matrix: its determinant is not exactly one, and its columns are only nearly perpendicular. Equation (2.1) projects it back. Because the ten input rotations disagree so little, the projected matrix reads the same to four decimals while now being exactly orthonormal, with a determinant of one and no entry moved by more than 0.000002:"),  # src: writing/v7/scripts/ch4_numbers.py (det A = 0.999996; |R - A| max 1.44e-06)
(MATH, r("R") + r(" = ") + num_mat([  # src: writing/v7/scripts/ch4_numbers.py (chordal mean of the same ten rotations)
    ["0.9997", "−0.0014", "−0.0243"],
    ["−0.0219", "−0.4832", "−0.8752"],
    ["−0.0105", "0.8755", "−0.4831"]])),
(PM, [T("The mean of the same ten translations is (0.0235, 0.1874, 0.5525) m. The calibrated desk marker therefore sits 55.3 cm in front of the camera, 18.7 cm below it and 2.4 cm to its right. Rotation and translation together are the frozen anchor "),  # src: writing/v7/scripts/ch4_numbers.py, mean of the ten desk translations; matches T_cam_desk in eval/output/scene_calibration_r6bc.json
      X(TCW), T(", and every world-frame value in the rest of the thesis is expressed relative to it.")]),

(P, "The scene description of Table 2.3 comes from the same calibration. Gravity, taken from the wall marker, reads (-0.0212, 0.5300, 0.8477) in world coordinates. Its angle to the world z axis is the arccosine of its z component, 32.04 degrees, which is the tilt of the desk marker card on its stand. The world origin sits 3.8 mm below the fitted tabletop plane. The calibration takes the measured edge of 70 mm, supplied as an option, rather than reading it from the rest height."),  # src: eval/output/scene_calibration_r6bc.json scene_geometry (gravity_up_world, desk_stand_tilt_deg 32.04, origin_above_tabletop_m -0.0038, object_cube_size_m 0.07 supplied via --cube-size)

(P, "The inverse anchor of equation (4.2) is next. Transposing the rotation and applying it to the negated translation gives"),
(MATH, eqArr(  # src: writing/v7/scripts/ch4_numbers.py, inverse of T_cam_desk in eval/output/scene_calibration_r6bc.json
    RT + r(" = ") + num_mat([
        ["0.9997", "−0.0219", "−0.0105"],
        ["−0.0014", "−0.4832", "0.8755"],
        ["−0.0243", "−0.8752", "−0.4831"]]),
    r("−") + RT + r(" ") + r("t") + r(" = (−0.0135, −0.3931, 0.4315)"))),
(P, "That translation is the camera's own position in the world frame. Read against the measured scene, it places the camera 58.4 cm from the world origin and 15.4 cm above the fitted tabletop plane. Figure 2.5 shows that low viewpoint across the working area."),  # src: writing/v7/scripts/ch4_numbers.py (58.4 cm from the world origin, 15.4 cm above the tabletop plane)

(P, "The chain of equation (4.1) runs on the scene image. The object marker is detected there with camera-frame translation"),
(MATH, sub(r("t"), nor("CO")) + r(" = (−0.2095, 0.1560, 1.0229) m")),  # src: writing/v7/scripts/ch4_numbers.py, frame 533 of eval/output/recording_20260831_065553_aruco_raw_scaled.csv
(P, "The cube therefore stands 106 cm from the camera, on the rail in front of the participant. Multiplying the inverse anchor by that frame's object transformation splits into one product per block. The world rotation is the transposed anchor rotation applied to the object rotation. The world translation is that same transposed rotation applied to the object translation, plus the camera position already computed:"),  # src: writing/v7/scripts/ch4_numbers.py (range from the camera 1.06 m)

(MATH, eqArr(
    sub(r("R"), nor("WO")) + r(" = ") + RT + r(" ") + sub(r("R"), nor("CO")),
    sub(r("t"), nor("WO")) + r(" = ") + RT + r(" ") + sub(r("t"), nor("CO")) + r(" + ") + sub(r("t"), nor("WC")))),

(P, "The first product, the transposed anchor rotation applied to the object translation, gives (−0.2236, 0.8204, −0.6256) m. Adding the camera position (−0.0135, −0.3931, 0.4315) m to it gives the world translation, and the rotation product gives the world rotation:"),  # src: R^T t_CO = t_WO - t_WC from the printed values (-0.2371+0.0135, 0.4273+0.3931, -0.1941-0.4315)
(MATH, eqArr(  # src: writing/v7/scripts/ch4_numbers.py, world object pose on frame 533
    sub(r("t"), nor("WO")) + r(" = (−0.2371, 0.4273, −0.1941) m"),
    sub(r("R"), nor("WO")) + r(" = ") + num_mat([
        ["0.9975", "0.0133", "0.0697"],
        ["0.0528", "0.5178", "−0.8539"],
        ["−0.0475", "0.8554", "0.5158"]]))),
(P, "Projected onto the measured gravity direction, the marker centre stands 6.3 cm above the fitted tabletop plane. The cube is held against the rail at that instant, which puts its centre 7.3 cm above the tabletop, and the difference is within what the coarse fitted plane resolves at that distance from the desk marker. The rotation is a proper rotation, as the chain guarantees, and it is the orientation the cube presents to the desk rather than to the camera."),  # src: writing/v7/scripts/ch4_numbers.py (6.3 cm above the tabletop plane; rail 3.8 cm + half cube 3.5 cm)

(P, "The cleaning step closes the example. The object marker is seen on frame 785, at world x 0.0304 m, and again on frame 787, at 0.0341 m, and the detector returns nothing on frame 786 between them. The gap is one frame, inside the bridging limit of eight, so the filter bridges it, and the bridged position on frame 786 sits 1.0 mm from the mean of the two detections beside it. The smoothing window pulls the two kept rows away from their own detections by 13.5 and 13.7 mm, almost all of it in the two axes across the slide, where the detections jitter from frame to frame and the filter follows their trend. Seven frames before the undetected frame, on frame 779, the despike step had invalidated a detection 20.6 mm off the trend and the bridge had written a pose over it; that row keeps its detected flag and carries the bridged pose."),  # src: writing/v7/scripts/ch4_numbers.py, frames 783-789 of eval/output/recording_20260831_065553_scaled_object_world.csv against ..._filtered.csv and ..._filtered_clean.csv; frame 779 dev 20.6 mm

(P, "The rule then walks the filtered track. Frame 786 stands 3.3 mm and 1.18 degrees from the last kept sample, frame 785, well inside the allowance, but the marker was never seen on it, so the row is blanked. Frame 787 stands 4.9 mm and 0.58 degrees from frame 785, two frame intervals later, and is kept. The rule rejects no detected sample anywhere in the recording. A consumer reading the cleaned track sees the pose of frame 785 held across frame 786, marked as held, and the filtered pose on frame 787, as the lower panel of Figure 4.2 shows."),  # src: writing/v7/scripts/ch4_numbers.py (cleaning decision around frame 786; rejected: none; blanked: [786])

(P, "The chapter ends with two products. The frozen scene description places the desk, the gravity direction, the tabletop, the camera, and the object's size in one frame fixed to the desk. The cleaned object track gives, for every frame, either a measured world pose of the cube or a marked gap. Chapter 5 uses the track as the independent measurement that constrains pose recovery while the landmark branch is failing, Chapter 6 streams both products into the reconstruction, and Chapter 7 compares the track against the reference path of Section 7.1."),

]

doc = Document()
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(12)

for item in content:
    kind = item[0]
    if kind == H1:
        doc.add_heading(item[1], level=1)
    elif kind == H2:
        doc.add_heading(item[1], level=2)
    elif kind == H3:
        doc.add_heading(item[1], level=3)
    elif kind == P:
        doc.add_paragraph(item[1])
    elif kind == PM:
        p = doc.add_paragraph()
        for typ, val in item[1]:
            if typ == "t":
                p.add_run(val)
            else:
                add_inline_math(p, val)
    elif kind == EQ:
        add_display_eq(doc, item[1], item[2])
    elif kind == MATH:
        add_display_math(doc, item[1])
    elif kind == IMG:
        path = Path(item[1])
        assert path.exists(), f"missing figure: {path}"
        doc.add_picture(str(path), width=Inches(item[2]))
    elif kind == CAP:
        p = doc.add_paragraph(item[1])
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.italic = True
    elif kind == TBL:
        rows = item[1]
        t = doc.add_table(rows=len(rows), cols=len(rows[0]))
        t.style = "Table Grid"
        for i, row_ in enumerate(rows):
            for j, c in enumerate(row_):
                cell = t.cell(i, j)
                cell.text = c
                for par in cell.paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(10)
                        if i == 0:
                            run.font.bold = True

out = REPO / "writing" / "v8" / "Chapter_4_Object_Tracking.docx"
doc.save(out)
print("saved", out, "| items:", len(content))
