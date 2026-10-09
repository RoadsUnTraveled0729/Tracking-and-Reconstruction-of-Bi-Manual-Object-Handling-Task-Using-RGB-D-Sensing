#!/usr/bin/env python3
"""Build writing/v4/Chapter_2_Background.docx.

Supervisor round of 2026-08-03: opener loses the appendix meta-paragraph and
the thesis roadmap (moved to Section 1.4); new sections introduce the basic
tools with real figures (experimental setup, MediaPipe landmarks, ArUco
markers), with internals still in the Appendix; the five-way filter
comparison (old Table 2.3) is removed as out of scope; old 2.1.4 Sampling
Rate Overview deleted. Section order: 2.1.1 setup and recordings,
2.1.2 MediaPipe, 2.1.3 ArUco, 2.1.4 replay, 2.1.5 smoothing.
Figures: 2.1 flow, 2.2 setup, 2.3 MediaPipe, 2.4 ArUco, 2.5 filter QC.
Tables: 2.1 recordings, 2.2 markers.
"""
from docx import Document
from docx.shared import Pt, Inches

FIG = "/home/luo/Desktop/New_SandBox/writing/v2/figures/"
FIG4 = "/home/luo/Desktop/New_SandBox/writing/v5/figures/"
H1, H2, H3, P, IMG, CAP, TBL = "h1", "h2", "h3", "p", "img", "cap", "tbl"
LIN = "lin"

content = [
(H1, "Chapter 2: Background"),

(P, "This chapter sets up the experimental environment of the thesis and the conventions that every later chapter relies on. It describes the physical capture setup and the recorded data, introduces the three sensing tools (the RGB-D camera, the MediaPipe pose detector, and the ArUco fiducial markers), explains the preprocessing applied before any modeling, and covers the basic mechanisms by which processed results reach the Unity environment."),

(P, "Figure 2.1 shows the overall data flow. A recorded RealSense session feeds two parallel processing pipelines. Pipeline A tracks the person: landmark detection, depth fusion, filtering, and the kinematic solver of Chapter 3; later chapters refer to it as the landmark branch. Pipeline B tracks the scene and the object: marker detection, scene calibration, and world anchoring, developed in Chapter 4; later chapters call it the marker branch. The two pipelines share nothing except the recording itself. This independence is deliberate: Pipeline B serves as the measurement source against which Pipeline A is evaluated in Chapter 6, so any shared processing would compromise the comparison. The pipelines converge only at the data fusion stage, which pairs their outputs frame by frame and streams the combined record to Unity (Chapter 5)."),

(IMG, "/home/luo/Desktop/New_SandBox/writing/v5/figures/fig1_system_flow.png", 6.3),
(CAP, "Figure 2.1. Overall data flow of the system. Pipeline A (top) tracks the person, Pipeline B (bottom) tracks the scene and object, and the two meet only at the data fusion stage. Each block names the chapter that develops it."),

(P, "One rule, called Data Integrity in this thesis, governs the whole pipeline: every reported value must state whether it was measured or filled in. A sample that fails a check is converted to a missing value, not passed on as a guess. Missing values are filled only through designated mechanisms, such as holding the last valid value or interpolating across a short gap, and every filled value keeps a flag that marks it as not measured. This rule governs the visibility gating of the landmark detector (Section 2.1.2), the gap handling of Chapter 4, the live masking of Chapter 5, and the state indicators of the final reconstruction."),

(H2, "2.1 Data Acquisition and Preprocessing"),

(H3, "2.1.1 Experimental Setup and Recordings"),

(P, "The physical test environment is a desk against a wall, shown in Figure 2.2 from the camera's own viewpoint. The subject stands at the desk and performs the manipulation tasks with a 70 millimetre cube. The camera is mounted on a fixed support at the desk edge at approximately chest height, facing the subject at a working distance of 1.5 to 2 metres. This distance is a compromise. Moving closer improves both the pixel resolution on the landmarks and the depth accuracy, since depth noise grows with distance squared, but it risks the extended arms leaving the field of view (55.6 by 43.1 degrees from the colour intrinsics). The chosen distance keeps the whole upper body and the working surface in view throughout the tasks."),

(IMG, FIG4 + "ch2_fig_setup.png", 6.3),
(CAP, "Figure 2.2. The experimental setup, seen from the RGB-D camera: the person at the desk carrying the 70 mm cube, the desk surface, and the three ArUco markers (wall, desk, and object) whose roles are listed in Table 2.2."),

(P, "Three recordings are used in this thesis, each 899 frames (about 30 seconds) at 640 by 480 pixels and 30 frames per second, a frame interval of 33.3 milliseconds:"),
(TBL, [["Recording", "Setup", "Use"],
       ["Recording 1", "standing subject carries the cube (1.94 m of travel), parking it on the desk mid-recording; camera at desk edge", "primary evaluation recording"],
       ["Recording 2", "standing subject, arms moving, object untouched", "kinematic validation on real data"],
       ["Recording 3", "seated subject, object untouched, camera mounted high, desk marker on a tilted stand", "cross-validation of the marker pipeline"]]),
(CAP, "Table 2.1. The three recordings. Frame 100 of Recording 1, the evaluation recording, is the running example of this thesis."),

(P, "The acquisition procedure behind these recordings, and the structure of the bag file each one is stored in, are described in Appendix A."),

(H3, "2.1.2 Pose Landmarks from MediaPipe"),

(P, "Pipeline A begins with MediaPipe Pose, an open-source body landmark detector from the MediaPipe framework [26] that runs in real time on ordinary hardware. Given a colour image, the detector first finds the person, then regresses a fixed set of 33 body landmarks covering the whole body from face to feet. The output is structured: landmark k is always the same body point, in the same order, so the eight upper-body landmarks used in this work (shoulders 11 and 12, elbows 13 and 14, wrists 15 and 16, hips 23 and 24) are read off directly by index. Each landmark carries image coordinates, a depth estimate inferred from image appearance, and a visibility score between 0 and 1 that rates the detector's confidence that the landmark is visible."),

(P, "Two of those outputs are treated with care. The appearance-based depth estimate is not used at all; depth comes from the RealSense depth stream instead, sampled at each landmark's pixel and back-projected through the camera intrinsics into a metric 3D position (Appendix B). And a landmark whose visibility score falls below 0.5 is recorded as missing rather than kept, following the Data Integrity rule, because the detector still emits a position for landmarks it cannot see. Figure 2.3 shows the detector's output on the running example frame. Appendix C describes the detector's two-stage architecture, the extraction procedure, and a worked numerical example."),

(IMG, FIG4 + "ch2_fig_mediapipe.png", 6.3),
(CAP, "Figure 2.3. MediaPipe Pose output on frame 100 of the evaluation recording. The eight numbered landmarks (shoulders, elbows, wrists, hips) are the ones this system consumes; the other 25 of the 33 are drawn unnumbered. The leg landmarks below the desk edge are detector guesses for body parts the desk occludes, and the visibility gate removes such points."),

(H3, "2.1.3 Fiducial Markers (ArUco)"),

(P, "Pipeline B rests on ArUco fiducial markers [27]. An ArUco marker is a printed square: a black border around a small black-and-white grid that encodes an integer identity. The detector finds square outlines in the image, reads the grid to identify the marker, and refines the four corners to sub-pixel accuracy. Because the marker's printed size is known, the four corners determine the marker's pose relative to the camera, position and orientation together, through a planar Perspective-n-Point solution. A single detection therefore answers two questions at once: which marker is seen, and where it is."),

(P, "Three markers define the measured scene, with the roles listed in Table 2.2 and the detections on the running example frame shown in Figure 2.4. The world coordinate frame is anchored at the desk marker, so every pose in the reconstruction, including the camera's own, is expressed relative to the desk; this makes the reconstruction independent of where the camera stands. The wall marker carries the single physical assumption of the setup: the wall is plumb, so the marker's in-plane up axis defines the gravity direction. The wall marker is larger because pose accuracy degrades with apparent size; at 3.4 metres it spans only about 32 pixels even at 150 millimetres. The object marker rides on one face of the carried cube. Camera placement relative to the anchor marker matters more than marker size at these scales; Chapter 6 reports that comparison. Scene calibration, which averages the static marker poses over the first ten detections and freezes them, is developed in Chapter 4, and Appendix D covers the detection stages, the planar pose ambiguity, and the conversion from the detector's rotation format to a rotation matrix."),

(TBL, [["ID", "Size (mm)", "Location", "Role"],
       ["0", "150", "wall", "static; assumed plumb; defines the gravity direction"],
       ["2", "50", "desk", "static; world anchor: origin of the world frame"],
       ["1", "50", "object (one face of the 70 mm cube)", "dynamic; the tracked object"]]),
(CAP, "Table 2.2. ArUco marker configuration. All markers are from the OpenCV 5 by 5 dictionary."),

(IMG, FIG + "fig4_aruco_frame100.png", 6.3),
(CAP, "Figure 2.4. ArUco detections on frame 100 of the evaluation recording: detected corners and identities, with each marker's pose axes drawn from its Perspective-n-Point solution."),

(H3, "2.1.4 Recorded Session Replay and Frame Extraction"),

(P, "Each capture session is stored as a recorded session file, the RealSense container format that holds the synchronized colour and depth streams together with timestamps and the calibration metadata, including the factory camera intrinsics listed in Appendix B. The offline pipeline replays the recording one frame at a time. Because processing is offline, replay does not need to keep pace with the original 30 frames per second; each frame is read, aligned, processed completely by both branches, and only then is the next frame requested. This removes all time pressure and makes every result exactly repeatable, which allows the strict validation methodology of the later chapters. Appendix A describes the capture procedure, the structure of the bag file that stores each session, and how a recording is inspected in the vendor's viewer. The real-time variant of the system, where this luxury disappears, is the subject of Chapter 7."),

(P, "One replay detail affects correctness. MediaPipe's video mode requires timestamps that always increase in whole milliseconds, while replayed timestamps can repeat or jitter, so each timestamp is clamped to be at least one millisecond after the one before it. Both branches consume the same frame sequence from the same recording, so a single frame index identifies simultaneous person and object measurements throughout the system; this shared index makes the data fusion of Chapter 4 a pairing operation rather than a resampling problem."),

(H3, "2.1.5 Signal Smoothing"),

(P, "The raw 3D landmark trajectories carry three distinct kinds of error, and the preprocessing treats each with a dedicated stage rather than one catch-all filter:"),
(LIN, "1. Case A, spikes: an isolated sample jumps far off the local path for one frame, from a depth speckle or a momentary mis-detection."),
(LIN, "2. Case B, gaps: a few consecutive samples are missing entirely, because the visibility gate of Section 2.1.2 blocked them."),
(LIN, "3. Case C, jitter: every sample carries small broadband noise from detection and depth measurement."),
(P, "The three cases need different treatments, because a smoother strong enough to flatten a case A spike would also distort genuine fast motion, and no smoother can fill a case B gap."),

(P, "Case A is handled by a Hampel despike: over a rolling 11-frame window, a sample is flagged as a spike when it departs from the local median by more than three robust standard deviations, with an absolute floor of 2 centimetres so that noise-level wiggle at rest is never flagged. Because the threshold adapts to the local motion, fast genuine movement raises it and is not flagged. Flagged samples are invalidated and join the missing data of case B. Case B is filled by interpolation: interior gaps of at most 5 frames (167 milliseconds) are linearly interpolated between their valid endpoints, a designated substitute with bounded error over a short occlusion. Longer gaps stay missing, because inventing positions across long gaps is the job of the occlusion handling in Chapter 3, in angle space rather than point space. Gaps at the recording boundary are backfilled with the nearest valid sample, which removed a 60.3 degree single-frame snap that the warm-up gap otherwise produced in the streamed output. Case C is smoothed with a low-pass Butterworth filter, cutoff 3 Hz, run forward and then backward over the recording so the net phase shift is exactly zero and motion peaks stay where they happened. Voluntary upper-body motion lies below roughly 5 Hz, so the cutoff passes the deliberate reach-and-carry motion of these tasks while removing broadband noise. A causal filter designed for interactive tracking, such as the One Euro filter [40], must lag behind fast motion because it can only look backward; the offline pipeline avoids that lag entirely by filtering in both directions, and the causal alternative returns in the real-time system of Chapter 7, where looking forward is impossible. Figure 2.5 shows the filter chain's effect on the evaluation recording."),

(IMG, FIG + "fig6_filter_qc.png", 6.3),
(CAP, "Figure 2.5. Filter quality-control plot for the evaluation recording: per-axis raw and filtered trajectories with flagged glitches and repaired gaps."),

(P, "The smoothing stage follows the Data Integrity rule. The raw data is never modified; the filter writes a separate output. Every repaired sample keeps a flag that marks it as repaired, so later stages can always tell measured data from filled-in data. Smoothing must not invent geometry: the filter is checked to move measured samples by less than the raw measurement jitter."),

(H2, "2.2 Unity-Python Communication Preliminaries"),

(H3, "2.2.1 UDP Protocol Basics and Packet Structure"),

(P, "The processing pipeline runs in Python; the graphical reconstruction runs in Unity. The two are separate processes, so the per-frame results must cross a process boundary. The bridge supports two transports that share one packet format. The first is UDP, the connectionless datagram protocol: the sender transmits each frame's record as one datagram to a local port, and the receiver reads whole datagrams as they arrive. UDP is simple and has the right semantics for pose streaming, because each packet is a complete self-contained state and a lost or reordered packet should simply be superseded by the next one rather than retransmitted. The second transport is shared memory: the sender writes the same record into a small memory-backed region provided by the operating system, guarded by a sequence counter that is odd while a write is in progress and even when the record is stable, so the reader can detect and retry a torn read. Shared memory is the default in this work because it has lower latency and lets the newest frame overwrite the previous one with no queueing."),

(P, "The landmark packet is a fixed 180-byte little-endian record: a four-byte magic identifier, a sequence counter (used by the shared-memory transport), the frame index, the frame time in seconds, the landmark count, and then eight landmark blocks of {landmark id, x, y, z, valid flag}. The valid flag carries the data integrity convention of the landmark extraction (Appendix C) across the process boundary, so Unity knows which landmarks are measured and which are missing in each frame. The integrated system of Chapter 5 extends this pattern with a packet that carries the person state and the object state together in a single record, which makes desynchronization between them structurally impossible."),

(H3, "2.2.2 Frame Synchronization Overview"),

(P, "During offline replay the sender paces packets to the recorded timestamps, so Unity receives frames at the original 30 frames per second regardless of how fast the offline processing ran. Synchronization between the person data and the object data requires no clock at all: both branches are indexed by the same frame number from the same recording, so fusion is exact pairing by construction. The remaining synchronization concern is between the sender's 30 Hz update rate and Unity's own render rate, which is typically higher and not locked to the sender. Unity therefore always renders the most recently received stable record. The subtleties this introduces for the live system, where the sender is a real sensor rather than a paced replay, are treated in Chapter 7."),

(H3, "2.2.3 Unity Humanoid Rig Fundamentals"),

(P, "On the Unity side, the person is represented by a humanoid rig: a hierarchy of bones (hips, spine, shoulders, upper arms, forearms, hands) in which each bone's rotation is expressed relative to its parent. This structure motivates the kinematic modeling of Chapter 3. The rig is not driven by placing points in space; it is driven by rotating joints. Feeding it the eight landmark positions directly would do nothing sensible, so the pipeline must first resolve the relative rotations of the body segments from the measured positions, and the packets of Section 2.2.1 ultimately carry those angles (the integrated packet of Chapter 5 streams 13 angle values plus the object pose)."),

(P, "Two properties of the rig matter for later chapters. First, Unity's coordinate frame is left-handed with y up, while the camera frame of the sensor (Appendix B) is right-handed with y down; the conversion is a fixed axis flip applied to every point, developed in Chapter 3. Second, the rig's proportions are those of the imported character model, not of the recorded person; the forearm of the rig used here is about 1.6 times the person's forearm length in proportion to the upper arm. Joint angles transfer between differently proportioned bodies, but positions do not, which is a second reason the system streams angles. The measured rig dimensions and the scale calibration that reconciles rig space with the metric scene are part of the integration procedure of Chapter 5."),
]

references = {
26: 'F. Zhang et al., "MediaPipe Hands: On-device real-time hand tracking," arXiv:2006.10214, 2020.',
27: 'M. Kalaitzakis, B. Cain, S. Carroll, A. Ambrosi, C. Whitehead, and N. Vitzilaios, "Fiducial markers for pose estimation: Overview, applications and experimental comparison," Journal of Intelligent and Robotic Systems, vol. 101, art. 71, 2021.',
40: 'G. Casiez, N. Roussel, and D. Vogel, "1 euro filter: A simple speed-based low-pass filter for noisy input in interactive systems," in Proc. SIGCHI Conf. Human Factors in Computing Systems (CHI), 2012, pp. 2527-2530.',
}

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
    elif kind == LIN:
        p = doc.add_paragraph(item[1])
        p.paragraph_format.left_indent = Inches(0.3)
    elif kind == IMG:
        doc.add_picture(item[1], width=Inches(item[2]))
    elif kind == CAP:
        p = doc.add_paragraph(item[1])
        p.runs[0].font.size = Pt(10)
        p.runs[0].font.italic = True
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

out = "/home/luo/Desktop/New_SandBox/writing/v5/Chapter_2_Background.docx"
doc.save(out)
print("saved", out)
