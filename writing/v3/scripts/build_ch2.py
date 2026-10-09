#!/usr/bin/env python3
"""Build writing/v3/Chapter_2_Background.docx.

v3 restructuring of the v2 chapter per writing/v3/STRUCTURE.md: the
perception-layer sections (v2 2.1 RGB-D sensing, 2.2 pose landmark detection,
2.3 fiducial marker tracking) moved to the Appendix. What remains is the
capture setup, preprocessing, and communication preliminaries (v2 2.4 and 2.5,
renumbered 2.1 and 2.2), preceded by a rewritten introduction that summarizes
what the sensing layer delivers and points to the Appendix for internals.
Rule-11 fixes: /dev/shm reworded; recording IDs replaced by plain labels.
Figure/table renumbering: v2 Figure 2.6 -> 2.2; v2 Tables 2.3/2.4/2.5 ->
2.1/2.2/2.3. Per-chapter References section dropped (skill rule 12).
"""
from docx import Document
from docx.shared import Pt, Inches

FIG = "/home/luo/Desktop/New_SandBox/writing/v2/figures/"
H1, H2, H3, P, IMG, CAP, TBL = "h1", "h2", "h3", "p", "img", "cap", "tbl"

content = [
(H1, "Chapter 2: Background"),

(P, "This chapter sets up the experimental environment of the thesis and the conventions that every later chapter relies on. It describes the physical capture setup, the recorded data, the preprocessing applied before any modeling, and the basic mechanisms by which processed results reach the Unity environment. The system is built on three sensing components: an RGB-D sensor that supplies registered colour and metric depth, a pose landmark detector that locates the body joints in the image, and printed fiducial markers that provide an independent measurement of the scene and the manipulated object. How each of these components works internally is a matter of perception machinery rather than of the kinematic model or the system design, so that material is collected in the Appendix. This chapter states only what each component delivers to the rest of the system."),

(P, "Figure 2.1 shows the overall data flow. A recorded RealSense session feeds two parallel processing branches. Branch A tracks the person: landmark detection, depth fusion, filtering, and the kinematic solver of Chapter 3. Branch B tracks the scene and the object: marker detection, scene calibration, and world anchoring, developed in Chapter 4. The two branches share nothing except the recording itself, and this independence is deliberate. Branch B serves as the measurement source against which Branch A is evaluated in Chapter 6, so any shared processing would compromise the comparison. The branches converge only at the data fusion stage, which pairs their outputs frame by frame and streams the combined record to Unity (Chapter 5)."),

(IMG, FIG + "fig1_system_flow.png", 6.3),
(CAP, "Figure 2.1. Overall data flow of the system. Pipeline A (top) tracks the person, Pipeline B (bottom) tracks the scene and object, and the two meet only at the data fusion stage."),

(P, "Three facts about the sensing layer are used throughout the thesis. First, every frame consists of a colour image and a depth image on the same 640 by 480 pixel grid, aligned so that a single pixel location indexes both, and any pixel with a valid depth can be lifted to a metric 3D point in the camera frame; the projection model, the factory calibration, and the depth sampling procedure are detailed in Appendix A. Second, the landmark detector reports eight upper-body landmarks per frame, each with a visibility score, and the extraction converts unreliable detections into honestly missing values rather than passing guesses forward; the detector and the gating rules are detailed in Appendix B. Third, three ArUco markers are detected with sub-pixel corner accuracy, and each detection yields both the marker's identity and its pose relative to the camera; the detection and pose recovery machinery is detailed in Appendix C. The rest of this chapter covers the capture setup and the data handling that turn these raw measurements into the streams the later chapters consume."),

(H2, "2.1 Data Acquisition and Preprocessing"),

(H3, "2.1.1 Sensor Placement and Calibration Setup"),

(P, "The physical test environment is a desk against a wall. The subject stands at the desk and performs the manipulation tasks with a 70 millimetre cube. The camera is mounted on a fixed support at the desk edge at approximately chest height, facing the subject at a working distance of 1.5 to 2 metres. This distance is a compromise. Moving closer improves both the pixel resolution on the landmarks and the depth accuracy, since depth noise grows with distance squared, but it risks the extended arms leaving the field of view (measured 55.6 by 43.1 degrees from the colour intrinsics). The chosen distance keeps the whole upper body and the working surface in view throughout the tasks."),

(P, "Three ArUco markers define the measured scene:"),
(TBL, [["ID", "Size (mm)", "Location", "Role"],
       ["0", "150", "wall", "static; assumed plumb; defines the gravity direction"],
       ["2", "50", "desk", "static; world anchor: origin of the world frame"],
       ["1", "50", "object (one face of the 70 mm cube)", "dynamic; the tracked object"]]),
(CAP, "Table 2.1. ArUco marker configuration. All markers are from the OpenCV 5 by 5 dictionary."),

(P, "The roles encode the ground-truth definition of this thesis. The world coordinate frame is anchored at the desk marker: every pose in the reconstruction, including the camera's own, is ultimately expressed in the desk marker's frame, which makes the reconstruction invariant to where the camera stands. The wall marker carries the single physical assumption in the entire setup: the wall is plumb, so the wall marker's in-plane up axis defines the gravity direction. Everything else is measured rather than assumed. The wall marker's larger size is deliberate; at 3.4 metres it subtends only about 32 pixels even at 150 millimetres, and pose accuracy degrades with apparent size. Scene calibration, in which the static marker poses are averaged over the first ten detections and frozen, is developed in Chapter 4. One empirical placement finding from comparing the two recording setups is worth stating here: the desk-edge camera position outperformed a higher camera mount on every stability metric measured (for example, wall pose stability of 0.54 versus 2.4 degrees at the 95th percentile), so camera placement matters more than marker size at these scales."),

(P, "Three recordings are used in this thesis, each 899 frames (about 30 seconds) at 640 by 480 and 30 frames per second:"),
(TBL, [["Recording", "Setup", "Use"],
       ["Recording 1", "standing subject carries the cube (1.94 m of travel), parking it on the desk mid-recording; camera at desk edge", "primary evaluation recording"],
       ["Recording 2", "standing subject, arms moving, object untouched", "kinematic validation on real data"],
       ["Recording 3", "seated subject, object untouched, camera mounted high, desk marker on a tilted stand", "cross-validation of the marker pipeline"]]),
(CAP, "Table 2.2. The three recordings. Frame 100 of Recording 1, the evaluation recording, is the running example of this thesis."),

(H3, "2.1.2 Recorded Session Replay and Frame Extraction"),

(P, "Each capture session is stored as a recorded session file, the RealSense container format that holds the synchronized colour and depth streams together with timestamps and the calibration metadata, including the factory camera intrinsics listed in Appendix A. The offline pipeline replays the recording one frame at a time. Because processing is offline, replay does not need to keep pace with the original 30 frames per second; each frame is read, aligned, processed completely by both branches, and only then is the next frame requested. This removes all time pressure and makes every result exactly repeatable, which is what allows the strict validation methodology of the later chapters. The real-time variant of the system, where this luxury disappears, is the subject of Chapter 7."),

(P, "One implementation detail of the replay affects correctness. MediaPipe's video mode requires strictly increasing timestamps in integer milliseconds, while replay timestamps can repeat or jitter. Each timestamp is therefore clamped to be at least one millisecond after its predecessor before being handed to the detector."),

(H3, "2.1.3 Signal Smoothing"),

(P, "The raw 3D landmark trajectories carry three distinct kinds of error, and the preprocessing treats each with a dedicated stage rather than one catch-all filter. Consider the three cases on a concrete trajectory. Case A: an isolated sample jumps far off the local path for one frame (a depth speckle or a momentary mis-detection). Case B: a few consecutive samples are missing entirely (the visibility gate of Appendix B blocked them). Case C: every sample carries small broadband jitter from detection and depth noise. These require different treatments, because a smoother that is strong enough to flatten case A would also distort genuine fast motion, and no smoother can fill case B."),

(P, "Stage one handles case A with a Hampel despike: over a rolling 11-frame window, a sample is flagged as a glitch when it departs from the local median by more than three robust standard deviations (estimated from the median absolute deviation), with an absolute floor of 2 centimetres so that noise-level wiggle at rest is never flagged. Because the threshold adapts to the local motion, fast genuine movement raises it and is not flagged. Flagged samples are invalidated and join the missing data of case B. Stage two fills case B: interior gaps of at most 5 frames (167 milliseconds) are linearly interpolated between their valid endpoints, which is an honest bound over a short occlusion; longer gaps stay missing, because inventing positions across long gaps is the job of the occlusion handling in Chapter 3, in angle space rather than point space. Gaps at the recording boundary are backfilled with the nearest valid sample, which removed a 60.3 degree single-frame snap that the warm-up gap otherwise produced in the streamed output. Stage three smooths case C with a low-pass Butterworth filter, cutoff 3 Hz, applied forward and backward so the net phase shift is exactly zero and motion peaks stay where they happened."),

(P, "The choice of the final smoother was measured, not assumed. Five candidates were compared on the evaluation recording using two numbers: residual shake (mean frame-to-frame displacement at rest) and fast-motion deviation (departure from the despiked raw signal during fast wrist motion, where any lag shows up as error):"),
(TBL, [["Method", "Shake (mm)", "Fast-motion deviation (mm)"],
       ["raw (no smoothing)", "10.2", ""],
       ["Savitzky-Golay, window 9, order 2", "2.8", "4.8"],
       ["rolling median, window 9", "2.9", "3.9"],
       ["Butterworth 3 Hz, zero phase (chosen)", "1.9", "4.8"],
       ["Butterworth 2 Hz, zero phase", "1.5", "5.3"],
       ["One Euro filter (causal)", "1.1", "28.4"]]),
(CAP, "Table 2.3. Measured smoother comparison on the evaluation recording. The chosen zero-phase Butterworth at 3 Hz gives five times less shake than raw at the same motion fidelity as Savitzky-Golay."),

(P, "The table explains a choice that would otherwise look surprising. The One Euro filter [40] is a popular adaptive filter for interactive tracking, and it produces the least shake of all candidates. But its 28.4 millimetres of fast-motion deviation is pure causal lag: as a real-time filter it can only look backward, so during fast motion it trails the true position. The offline pipeline has no reason to accept that lag, because zero-phase filtering (running the filter forward and then backward over the recorded data) is available offline and eliminates lag exactly. The One Euro filter is therefore excluded here but returns as the natural candidate in the real-time system of Chapter 7, where causality is unavoidable and its adaptive cutoff (smooth when slow, responsive when fast) is exactly the right trade-off. Figure 2.2 shows the filter chain's effect on the evaluation recording."),

(IMG, FIG + "fig6_filter_qc.png", 6.3),
(CAP, "Figure 2.2. Filter quality-control plot for the evaluation recording: per-axis raw and filtered trajectories with flagged glitches and repaired gaps."),

(P, "The stage is bound by an explicit honesty contract, enforced by the validators of later chapters. The raw data is never modified; the filter writes a separate output. Every repaired sample carries a provenance flag, so downstream consumers can always distinguish measured data from repaired data. And smoothing must not invent geometry: the filter is asserted to move measured samples by less than the raw measurement jitter."),

(H3, "2.1.4 Sampling Rate Overview"),

(P, "All streams run at the sensor's 30 frames per second, giving a frame interval of 33.3 milliseconds and 899 frames over each 30-second recording. Voluntary human upper-body motion lives below roughly 5 Hz, so 30 Hz sampling sits comfortably above the Nyquist requirement, and the 3 Hz smoothing cutoff of Section 2.1.3 preserves the full motion band while removing broadband noise. Both processing branches consume the same frame sequence from the same recording, so a single frame index identifies simultaneous person and object measurements throughout the system; this shared index is what makes the data fusion of Chapter 4 a pairing operation rather than a resampling problem. The rendering side runs at its own rate, and the consequences of that mismatch, including the temporal alignment issues it can cause, are examined in Chapters 7 and 8."),

(H2, "2.2 Unity-Python Communication Preliminaries"),

(H3, "2.2.1 UDP Protocol Basics and Packet Structure"),

(P, "The processing pipeline runs in Python; the graphical reconstruction runs in Unity. The two are separate processes, so the per-frame results must cross a process boundary. The bridge supports two transports that share one packet format. The first is UDP, the connectionless datagram protocol: the sender transmits each frame's record as one datagram to a local port, and the receiver reads whole datagrams as they arrive. UDP is simple and has the right semantics for pose streaming, because each packet is a complete self-contained state and a lost or reordered packet should simply be superseded by the next one rather than retransmitted. The second transport is shared memory: the sender writes the same record into a small memory-backed region provided by the operating system, guarded by a sequence counter that is odd while a write is in progress and even when the record is stable, so the reader can detect and retry a torn read. Shared memory is the default in this work because it has lower latency and lets the newest frame overwrite the previous one with no queueing."),

(P, "The landmark packet is a fixed 180-byte little-endian record: a four-byte magic identifier, a sequence counter (used by the shared-memory transport), the frame index, the frame time in seconds, the landmark count, and then eight landmark blocks of {landmark id, x, y, z, valid flag}. The valid flag carries the honest-gap convention of the landmark extraction (Appendix B) across the process boundary, so Unity knows which landmarks are measured and which are missing in each frame. The integrated system of Chapter 5 extends this pattern with a packet that carries the person state and the object state together in a single record, which makes desynchronization between them structurally impossible."),

(H3, "2.2.2 Frame Synchronization Overview"),

(P, "During offline replay the sender paces packets to the recorded timestamps, so Unity receives frames at the original 30 frames per second regardless of how fast the offline processing ran. Synchronization between the person data and the object data requires no clock at all: both branches are indexed by the same frame number from the same recording, so fusion is exact pairing by construction. The remaining synchronization concern is between the sender's 30 Hz update rate and Unity's own render rate, which is typically higher and not locked to the sender. Unity therefore always renders the most recently received stable record. The subtleties this introduces for the live system, where the sender is a real sensor rather than a paced replay, are treated in Chapter 7."),

(H3, "2.2.3 Unity Humanoid Rig Fundamentals"),

(P, "On the Unity side, the person is represented by a humanoid rig: a hierarchy of bones (hips, spine, shoulders, upper arms, forearms, hands) in which each bone's rotation is expressed relative to its parent. This structure is why the kinematic modeling of Chapter 3 exists. The rig is not driven by placing points in space; it is driven by rotating joints. Feeding it the eight landmark positions directly would do nothing sensible, so the pipeline must first resolve the relative rotations of the body segments from the measured positions, and those angles are what the packets of Section 2.2.1 ultimately carry (the integrated packet of Chapter 5 streams 13 angle values plus the object pose)."),

(P, "Two properties of the rig matter for later chapters. First, Unity's coordinate frame is left-handed with y up, while the camera frame of the sensor (Appendix A) is right-handed with y down; the conversion is a fixed axis flip applied to every point, developed in Chapter 3. Second, the rig's proportions are those of the imported character model, not of the recorded person; the forearm of the rig used here is about 1.6 times the person's forearm length in proportion to the upper arm. Joint angles transfer between differently proportioned bodies, but positions do not, which is a second reason the system streams angles. The measured rig dimensions and the scale calibration that reconciles rig space with the metric scene are part of the integration procedure of Chapter 5."),
]

references = {
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

out = "/home/luo/Desktop/New_SandBox/writing/v3/Chapter_2_Background.docx"
doc.save(out)
print("saved", out)
