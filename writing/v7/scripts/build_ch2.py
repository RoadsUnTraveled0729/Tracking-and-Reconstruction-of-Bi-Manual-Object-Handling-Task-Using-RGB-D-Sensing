#!/usr/bin/env python3
"""Build writing/v7/Chapter_2_Experimental_Setup.docx (V7 rewrite round).

Chapter 2 "Experimental Setup and Data Acquisition" against the V7 TOC:
2.1 The Recording Setup, 2.2 Pose Landmarks from MediaPipe, 2.3 Object
Pose from ArUco Markers, 2.4 Signal Filtering. Environment only (user
direction 2026-09-01): the reference paths and the waypoints of both
recordings live at the start of Chapter 7, and the rail dimension
figure (ch2_fig_rail_dims.png) moved there with them. The rail lies
FLAT (a 2-by-4: 3.8 cm tall, top face 8.8 cm wide; E-024). Marker size:
45 mm is the printed size (fact), 50 mm the size declared to the
detector. Rail-only round (2026-09-01, user direction): the thesis is
based on the rail recording recording_20260831_065553 (900 frames,
30 s) alone; the R5 loop recording appears only in Chapter 7's
occlusion evaluation and is not mentioned here. All example figures
(setup, MediaPipe, ArUco, filters) come from rail frame 533 and the
rail landmark CSVs. Filter parameters per the run metadata: hampel
window 7, k 3, floor 2 cm, gaps to 5 frames, Butterworth 3 Hz order 4
zero-phase; edge backfill disabled.
Supervisor comments addressed: C4 (setup photographs + user study
objective), C6 (filters named, justified, referenced, results shown),
C8 (filter panel split into separate larger figures).
Figures: writing/v7/figures/. Citations: writing/v7/references.md
numbering ([1]-[52] frozen, [53]-[57] appended).
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, Inches

H1, H2, P = "h1", "h2", "p"
CAP, TBL, LIN, IMG = "cap", "tbl", "lin", "img"

REPO = Path(__file__).resolve().parents[3]
FIG = REPO / "writing" / "v7" / "figures"

# Rail-only round: the rail recording (ground truth by construction) is
# the only recording of the chapter. The loop recording belongs to
# Chapter 7's occlusion evaluation and is introduced there.
F_RAILS, F_SETUP, F_FLOW = 1, 2, 3
F_MP, F_ARUCO, F_DESP, F_GAP, F_SMOOTH = 4, 5, 6, 7, 8

content = [
(H1, "Chapter 2: Experimental Setup and Data Acquisition"),

(P, f"This chapter describes the physical experiment and the data it produces. It covers the recording setup, the pose landmarks from MediaPipe, the object poses from the ArUco markers, and the filtering of the landmark signals. Later chapters use the outputs defined here."),

(H2, "2.1 The Recording Setup"),

# 2.1 rewritten on the user's outline (2026-09-02): controlled-lab
# opening, one table of the scene objects, the 2 m range argument from
# the Intel D400 tuning guide [58], no field-of-view sentence, and no
# Appendix D pointer here (appendix order = first appearance in body;
# Appendix D is first cited in Section 2.2, user decision 2026-09-02).
(P, f"The recording was done in a controlled laboratory setting, to avoid the inconsistent lighting and background that would affect the detection accuracy of the ArUco markers and of MediaPipe. One participant moves a cube along the desk and then along a wooden rail with one hand; Chapter 7 defines the reference path of this task and compares the tracked trajectory against it. Figure 2.{F_RAILS}(a) shows the arrangement in one photograph taken from above the desk, and panels (b) and (c) show the scene from behind the RGB-D camera and a colour frame of the recording. Table 2.1 lists the objects in the scene."),

(IMG, FIG / "ch2_fig_rail_setup.png", 6.3),
(CAP, f"Figure 2.{F_RAILS}. The recording setup. (a) The working area drawn on grid paper, with the rail, the cube at its start position, the desk marker, and the spirit level used to level the rail. (b) The scene from behind the RGB-D camera. (c) A colour frame of the recording, with the cube part way along the rail in the participant's right hand."),

# src: marker sizes and the 0.9 scale -> eval/common/marker_size.py, E-009a;
#      45 mm is the printed size (user measured, 2026-09-01), 50 mm the
#      declared size. Rail 38.7 x 8.8 x 3.8 cm lying flat (E-024).
(TBL, [["Object", "Role", "ArUco ID", "Dictionary", "Printed size (mm)", "Declared size (mm)", "Physical dimensions"],
       ["Wall marker", "Static; gravity reference", "0", "5 by 5", "150", "150", "-"],
       ["Desk marker", "Static; world origin", "2", "5 by 5", "45", "50", "-"],
       ["Object marker", "Dynamic; tracked cube", "1", "5 by 5", "45", "50", "Cube: 70 mm per side"],
       ["Wooden rail", "Reference object", "-", "-", "-", "-", "387 by 88 by 38 mm, lying flat"]]),
(CAP, f"Table 2.1. The objects in the scene. All markers are from the OpenCV 5 by 5 dictionary. The printed size is the measured black square; the declared size is the value given to the detector. A recovered distance scales with the size the detector is given, so every translation recovered from the desk and object markers is multiplied by 45 divided by 50, a factor of 0.90, before any object pose is used."),

(P, f"Figure 2.{F_SETUP} labels the parts of the scene in a colour frame from the sensor. The camera is an Intel RealSense D435 on a fixed support at the desk edge, facing the participant at a working distance of around 1.3 metres. Throughout the whole experiment, the measured person is intentionally kept within 2 metres of the camera. A scene farther from the camera can hold more content, but the depth error of the sensor grows with the square of the distance [37], [38], [58]."),

(IMG, FIG / "ch2_fig_setup.png", 6.3),
(CAP, f"Figure 2.{F_SETUP}. The experimental setup, seen from the RGB-D camera: the participant at the desk, the rail on the drawn working area, the carried cube, and the three ArUco markers (wall, desk, and object)."),

(P, f"The recording is stored as a bag file, the recording format of the Intel RealSense SDK. Each frame carries a colour image and a depth image aligned to it, and a shared frame index marks simultaneous person and object measurements. Appendix A describes the recording procedure and the file structure."),

(P, f"Figure 2.{F_FLOW} gives the overview of the system's data flow from the recording into two parallel pipelines. Pipeline A, called the landmark branch in later chapters, tracks the person through landmark detection, depth fusion, filtering, and the kinematic solver of Chapter 3. Its pose recovery stage is developed in Chapter 5. Pipeline B, the marker branch, tracks the scene and object through marker detection, scene calibration, and the world anchoring developed in Chapter 4. Pipeline B supplies the independent measurements that Chapter 5 recovers from and Chapter 7 evaluates against. The measurements stay independent only as long as the branches share no processing stage. Chapter 6 merges the finished processing data by frame index at the streaming stage and sends them to Unity. Both pipelines run on the one workstation listed in Appendix B."),

(IMG, FIG / "ch2_fig_flow.png", 6.3),
(CAP, f"Figure 2.{F_FLOW}. Overall data flow of the system. Pipeline A (top) tracks the person, Pipeline B (bottom) tracks the scene and object, and the two meet at the streaming stage. Each block names the chapter that develops it."),

(H2, "2.2 Pose Landmarks from MediaPipe"),

(P, f"Pipeline A starts with MediaPipe Pose, an open-source detector from the MediaPipe framework [28] that runs in real time on ordinary hardware. For each colour frame, it first locates the person and then regresses 33 body landmarks from the face to the feet. Landmark indices are fixed. The pipeline can therefore select the eight required upper-body points directly: shoulders L11 and L12, elbows L13 and L14, wrists L15 and L16, and hips L23 and L24. Every result includes image coordinates, an appearance-derived depth estimate, and a visibility score between 0 and 1. Appendix C gives the detector architecture, the steps that extract the landmarks, and a numerical example."),

(P, f"The pipeline uses only a subset of MediaPipe's output. Because MediaPipe estimates depth from 2D appearance rather than physical sensor measurements, those values are discarded in favour of depth readings from the aligned RealSense stream. Using camera intrinsics, each landmark pixel is then projected into metric 3D coordinates (Appendix D). Landmarks with visibility scores below 0.50 are treated as missing data to stop the system from reporting coordinates for occluded points. Figure 2.{F_MP} illustrates the full detector output on a sample recording frame."),

(IMG, FIG / "ch2_fig_mediapipe.png", 6.3),
(CAP, f"Figure 2.{F_MP}. MediaPipe Pose output on a mid-task frame of the recording. The eight numbered landmarks (shoulders, elbows, wrists, hips) are the ones this system consumes; the other 25 landmarks are drawn unnumbered. The leg landmarks below the desk edge are detector guesses for body parts the desk occludes, and the visibility gate removes such points."),

(H2, "2.3 Object Pose from ArUco Markers"),

(P, f"Pipeline B gets its measurements from ArUco fiducial markers [29], which feature black square borders framing unique binary ID grids. The detector spots candidate square outlines, reads the embedded ID, and refines the four corners down to subpixel precision. Once supplied with the marker's physical side length, it solves the planar Perspective-n-Point problem [52] to resolve both position and orientation in a single pass."),

# The marker table lives in Section 2.1 (Table 2.1) since 2026-09-02;
# the old duplicate table here is removed.
(P, f"Three markers establish the workspace, as listed in Table 2.1 and shown detected in Figure 2.{F_ARUCO}. The wall marker (ID 0, 150 mm) is mounted on a plumb wall and provides a vertical gravity reference, sized up simply because it sits farthest from the sensor. The object marker (ID 1, 45 mm) is directly attached to the front face of the cube. The table marker (ID 2, 45 mm) acts as the world origin, so tracking camera poses relative to the workspace keeps the 3D reconstruction independent of the placement of the camera. Chapter 4 walks through the static calibration step used to average and freeze the baseline poses of the stationary markers, while Appendix E covers corner detection, planar ambiguity, and rotation matrix conversion."),

(IMG, FIG / "ch2_fig_aruco.png", 6.3),
(CAP, f"Figure 2.{F_ARUCO}. ArUco detections on a mid-task frame of the recording: (a) the three detected markers in the full frame; (b) to (d) each marker enlarged, with its four detected corners drawn in detection order."),

(H2, "2.4 Signal Filtering"),

(P, f"The raw 3D landmark trajectories carry three kinds of error:"),

(LIN, f"Case A, spikes: an isolated sample jumps far off the local trajectory for one frame, from a depth speckle or a momentary false detection."),
(LIN, f"Case B, gaps: a few consecutive samples are missing, because the visibility gate of Section 2.2 blocked them or the depth sample was invalid."),
(LIN, f"Case C, jitter: every sample carries small broadband noise from detection and depth measurement."),

(P, f"A single smoothing filter cannot solve all three kinds of errors. If a filter is strong enough to remove a sharp spike, it also distorts fast motion. At the same time, no smoothing filter can fill in missing data gaps. The pipeline therefore handles each case in a separate stage."),

(P, f"Case A is handled by a rolling Hampel test. The Hampel identifier [53] spots outliers by checking how far a point drifts from the local median. It works well on time-series data because a sudden spike will not pull the median off track the way it pulls a mean [54]. In this setup, the test looks across a 7-frame window with a threshold set to three robust standard deviations. That value is calculated by multiplying the window's median absolute deviation by 1.4826 (Appendix F). A baseline floor of 2 centimetres prevents small sensor noise from triggering the test when a person is standing still. As movement speeds up, the threshold widens automatically, so rapid hand motions are never flagged as errors. Any spike the test flags is discarded and marked as missing data, which then passes into case B. Figure 2.{F_DESP} shows the test in action, catching a wrist spike that jumped 2.94 centimetres off track in a single frame."),

(IMG, FIG / "ch2_fig_filter_despike.png", 6.0),
(CAP, f"Figure 2.{F_DESP}. Despiking result on the right wrist of the recording: per-axis raw and filtered trajectories, with the sample flagged by the Hampel test marked."),

(P, f"Linear interpolation handles case B. Interior gaps no longer than 5 frames, a sixth of a second, are filled along a straight line between the two valid endpoints. Longer gaps remain missing, and the pose recovery of Chapter 5 handles them. The recovery restores a joint from the object or from the rest of the arm where a measurement anchors it. Where nothing anchors it, the last angle is held. Figure 2.{F_GAP} shows bridged wrist dropouts from the recording."),

(IMG, FIG / "ch2_fig_filter_gap.png", 6.0),
(CAP, f"Figure 2.{F_GAP}. Gap-bridging result on the right wrist of the recording: short gaps are filled by interpolation, and the replaced samples are marked."),

(P, f"A zero-phase Butterworth low-pass filter then treats case C. The filter follows the design procedure of [55]. The Butterworth family has a flat passband, so it passes the motion without ripple [56]. A fourth-order filter with a 3 Hz cutoff runs forward and backward over the recording [57]. The two passes cancel the phase delay and preserve event timing. Deliberate upper-body motion lies below roughly 5 Hz, so the cutoff leaves the motion intact and removes the jitter. The backward pass needs the whole recording, so the filter can only run offline. The real-time alternative is the One Euro filter [40], a causal low-pass filter that adapts its cutoff to how fast the signal is changing. Chapter 8 measures the lag and the angle cost of the causal filter against the offline one. Appendix F compares the candidate smoothers side by side: the Butterworth filter used here, the Savitzky-Golay filter, the rolling median, and the One Euro filter. The Savitzky-Golay filter fits a low-order polynomial over a sliding window [46], and the rolling median replaces each sample by the median of its neighbours. Figure 2.{F_SMOOTH} shows the raw jitter against the filtered track."),

(IMG, FIG / "ch2_fig_filter_smooth.png", 6.0),
(CAP, f"Figure 2.{F_SMOOTH}. Smoothing result on the right-wrist depth of the recording: the raw and filtered tracks over an eight-second span, with the shaded window enlarged below."),

(P, f"The preprocessing writes a separate output and never modifies the raw data. The unfiltered baseline therefore stays available for the evaluation of Chapter 7 to compare against. Every repaired sample keeps a flag, which separates measured data from filled-in data for later stages. The object track from Pipeline B is cleaned by its own stage, described in Chapter 4."),

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
    elif kind == P:
        doc.add_paragraph(item[1])
    elif kind == LIN:
        p = doc.add_paragraph(item[1])
        p.paragraph_format.left_indent = Inches(0.3)
    elif kind == CAP:
        p = doc.add_paragraph(item[1])
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.italic = True
    elif kind == IMG:
        path = Path(item[1])
        assert path.exists(), f"missing figure: {path}"
        doc.add_picture(str(path), width=Inches(item[2]))
    elif kind == TBL:
        rows = item[1]
        t = doc.add_table(rows=len(rows), cols=len(rows[0]))
        t.style = "Table Grid"
        for i, r in enumerate(rows):
            for j, c in enumerate(r):
                cell = t.cell(i, j)
                cell.text = c
                for par in cell.paragraphs:
                    for run in par.runs:
                        run.font.size = Pt(10)
                        if i == 0:
                            run.font.bold = True

out = REPO / "writing" / "v7" / "Chapter_2_Experimental_Setup.docx"
doc.save(out)
print("saved", out, "| items:", len(content))
