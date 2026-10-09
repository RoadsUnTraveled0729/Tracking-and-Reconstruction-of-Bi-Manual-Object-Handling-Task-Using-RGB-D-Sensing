#!/usr/bin/env python3
"""Build writing/v2/Chapter_2_Background.docx."""
from docx import Document
from docx.shared import Pt, Inches

FIG = "/home/luo/Desktop/New_SandBox/writing/v2/figures/"
H1, H2, H3, P, IMG, CAP, TBL = "h1", "h2", "h3", "p", "img", "cap", "tbl"

content = [
(H1, "Chapter 2: Background"),

(P, "This chapter introduces the technical foundations of the system developed in this thesis and the experimental environment in which it operates. Three sensing components contribute a distinct layer of information each: the RGB-D sensor supplies registered colour and metric depth, the pose landmark detector locates the body joints in the image, and the fiducial markers provide an independent measurement of the scene and the manipulated object. The chapter also covers the data acquisition procedure, the preprocessing applied before any modeling, and the basic mechanisms by which the processed data reaches the Unity environment. Each component is presented with the actual configuration and calibration values used in this work, so that the later chapters can build on concrete numbers rather than abstract descriptions."),

(P, "Figure 2.1 shows the overall data flow. A recorded RealSense session feeds two parallel processing branches. Branch A tracks the person: landmark detection, depth fusion, filtering, and the kinematic solver of Chapter 3. Branch B tracks the scene and the object: marker detection, scene calibration, and world anchoring, developed in Chapter 4. The two branches share nothing except the recording itself, and this independence is deliberate. Branch B serves as the measurement source against which Branch A is evaluated in Chapter 6, so any shared processing would compromise the comparison. The branches converge only at the data fusion stage, which pairs their outputs frame by frame and streams the combined record to Unity (Chapter 5)."),

(IMG, FIG + "fig1_system_flow.png", 6.3),
(CAP, "Figure 2.1. Overall data flow of the system. Pipeline A (top) tracks the person, Pipeline B (bottom) tracks the scene and object, and the two meet only at the data fusion stage."),

(H2, "2.1 RGB-D Sensing"),

(P, "The Intel RealSense D435 is a stereo-depth camera that produces per-pixel depth measurements alongside a colour image [9]. Depth is computed by triangulating between two infrared imagers separated by a known baseline, assisted by an infrared projector that adds texture to surfaces that would otherwise be too uniform for stereo matching. In this work both streams are recorded at 640 by 480 pixels and 30 frames per second. The subject stands at a working distance of roughly 1.5 to 2 metres, and the measured scene spans depths from 0.65 metres (the desk marker) to 3.4 metres (the wall marker), all comfortably inside the sensor's reliable operating range. Two properties of stereo depth matter for everything that follows: the depth error grows roughly with the square of the distance, and one pixel of image error corresponds to a lateral position error that grows linearly with distance, about 1.6 millimetres per pixel at 1 metre for the intrinsics used here. Detailed technical specifications of the sensor beyond what is used in this work are collected in Appendix A."),

(H3, "2.1.1 RGB Camera Calibration"),

(P, "Camera calibration establishes the mathematical relationship between 3D points in the scene and their 2D projections in the image. The standard pinhole model describes this relationship through the intrinsic matrix K, which contains four numbers: the focal lengths fx and fy in pixels along the horizontal and vertical image axes, and the principal point (cx, cy), the pixel where the optical axis meets the image [38]. A 3D point p = (x, y, z) expressed in the camera frame projects to the pixel"),
(P, "u = fx * x / z + cx,        v = fy * y / z + cy."),
(P, "Reading the first equation in words: the point's horizontal offset x is divided by its depth z, which captures the fact that the same offset appears smaller when it is farther away; the ratio is scaled by the focal length fx to convert from a geometric angle to a pixel count; and the principal point cx shifts the result from optics-centred coordinates to the pixel grid, whose origin is the top-left corner. The vertical equation works the same way."),

(P, "Calibration normally estimates these parameters by imaging a planar checkerboard from multiple viewpoints and minimising the reprojection error, following Zhang's method [38]. In this work no manual calibration was performed. The RealSense SDK exposes the factory calibration of each individual device, and these factory intrinsics are used directly. For the colour camera of the sensor used in all recordings, at 640 by 480 resolution, the values are:"),
(TBL, [["Parameter", "Value", "Meaning"],
       ["fx", "607.56 px", "horizontal focal length"],
       ["fy", "607.02 px", "vertical focal length"],
       ["cx", "323.94 px", "principal point, horizontal (near the image centre 320)"],
       ["cy", "248.02 px", "principal point, vertical (near the image centre 240)"]]),
(CAP, "Table 2.1. Factory colour-camera intrinsics of the RealSense D435 used in this work, recorded in the extraction metadata of every recording."),
(P, "Two observations connect these numbers to the model. The two focal lengths agree within 0.1 percent, meaning the pixels are very nearly square. And the principal point sits within 9 pixels of the geometric image centre, a typical manufacturing offset that the model absorbs exactly. The factory calibration proved sufficient for the positional accuracy targets of this system, which the worked example in Section 2.1.4 confirms against an independent measurement."),

(H3, "2.1.2 Depth-to-RGB Alignment and Camera Intrinsics"),

(P, "The depth imager and the colour camera are physically offset by a small baseline inside the D435 housing, and each has its own intrinsics [9]. A raw depth pixel at location (u, v) therefore does not observe the same scene point as the colour pixel at the same location. The RealSense SDK resolves this with a depth-to-colour alignment step: each depth pixel is lifted to a 3D point using the depth camera's intrinsics, moved into the colour camera's frame through the known transformation between the two imagers, and reprojected onto the colour image grid using the colour intrinsics of Table 2.1. Figure 2.2(b) illustrates the arrangement."),

(P, "In this work both buffers are 640 by 480, so the alignment produces a depth image on exactly the same pixel grid as the colour image. After alignment, the colour value and the depth value at any pixel (u, v) refer to the same physical point. This aligned pair is the only input the rest of the pipeline ever sees. Every landmark detection and every marker detection happens in colour pixel coordinates, and the same coordinates index the aligned depth buffer directly, with no further correspondence step."),

(IMG, FIG + "fig5_alignment_schematic.png", 6.3),
(CAP, "Figure 2.2. (a) Pinhole projection geometry of the colour camera: a scene point projects to the pixel where the ray to the camera centre crosses the image plane. (b) Depth-to-colour alignment: the depth buffer is reprojected into the colour camera's geometry so both buffers share one pixel grid."),

(H3, "2.1.3 Pixel-to-World Mapping"),

(P, "Given the aligned depth image and the colour intrinsics, any pixel (u, v) with a valid depth z can be lifted to a 3D point in the camera frame by inverting the pinhole projection:"),
(P, "x = z * (u - cx) / fx,        y = z * (v - cy) / fy,        p = (x, y, z)."),
(P, "This is the projection of Section 2.1.1 run backwards, and it is exact because the depth supplies the one piece of information the forward projection discards. The resulting camera frame is right-handed: x points right in the image, y points down, and z points forward into the scene along the optical axis [13]. The depth measurement itself is the z coordinate in this frame. The conversion of these camera-frame points into Unity's left-handed convention is a fixed axis flip, developed in Chapter 3."),

(P, "One practical detail matters more than the equations. Reading depth at a single pixel fails in two ways: the pixel can be a hole (a zero return, common at object edges and on dark or reflective surfaces), and it can carry single-pixel speckle noise. The system therefore never samples one pixel. Instead it takes the median of the nonzero depths in a 5 by 5 window centred on the target pixel. The median tolerates up to half the window being outliers, and excluding zero returns treats holes as absent samples rather than as fake zero depths. Measured over a full recording, this windowed median moves validly measured landmarks by 0.0 millimetres at the median (99th percentile below 7.5 millimetres, within depth noise) while recovering landmarks that a single-pixel read would have lost to holes. If the entire window has no valid return, the sample is honestly reported as missing rather than guessed."),

(H3, "2.1.4 Work Example"),

(P, "Consider frame 100 of the evaluation recording, the frame shown throughout this chapter. The ArUco detector (Section 2.3) locates the centre of the object marker at pixel (u, v) = (368, 175), and the 5 by 5 median depth at that pixel is z = 0.929 m. Substituting into the back-projection equations with the intrinsics of Table 2.1:"),
(P, "x = 0.929 * (368 - 323.94) / 607.56 = 0.929 * 0.0725 = 0.0674 m"),
(P, "y = 0.929 * (175 - 248.02) / 607.02 = 0.929 * (-0.1203) = -0.1118 m"),
(P, "so the marker centre sits at (0.067, -0.112, 0.929) in the camera frame: about 7 centimetres right of the optical axis, 11 centimetres above it (y is negative because the camera y-axis points down), at just under a metre of depth."),

(P, "This example was chosen because it comes with an independent check. The same marker's pose is also computed by the completely separate Perspective-n-Point method of Section 2.3.2, which infers position from the marker's corner geometry alone, without using the depth buffer at all. PnP places the marker centre at (0.0675, -0.1111, 0.9268). The two estimates, one from stereo depth and one from marker geometry, agree within 1 millimetre in x, 0.7 millimetres in y, and 2.2 millimetres in z. Two unrelated measurement principles landing on the same point at millimetre level is the concrete justification for trusting the factory calibration in Section 2.1.1."),

(H2, "2.2 Pose Landmark Detection"),

(H3, "2.2.1 MediaPipe BlazePose Overview"),

(P, "Modern learning-based pose detectors share a common structure: a detector network first localises the person (or a region of interest) in the image, and a regression network then predicts a fixed set of landmark coordinates within that region. Systems differ mainly in the backbone networks, the training data, and whether they output 2D points, 3D points, or full body meshes. For this thesis the requirements are specific: per-joint image coordinates that can be fused with a depth buffer, a per-joint confidence signal for occlusion handling, and real-time operation on consumer hardware. MediaPipe's BlazePose model [39], deployed through the MediaPipe framework [26], meets all three. It runs on-device, it outputs individual landmarks rather than an opaque mesh, and it attaches to every landmark a visibility score that later chapters use as the primary occlusion signal."),

(P, "BlazePose follows the two-stage pattern: a lightweight person detector localises a region of interest, and a landmark network regresses 33 anatomical keypoints within it, covering the face, torso, arms, and legs [39]. For each landmark the model outputs normalised image coordinates (xn, yn) in the range 0 to 1, a monocular depth estimate inferred from appearance, and a visibility score v between 0 and 1 expressing the model's confidence that the landmark is present and unoccluded. The monocular depth estimate is not used in this system. As noted in [3] and demonstrated empirically in [12], it carries substantial uncertainty during fast motion and object interaction, precisely the conditions of bimanual manipulation. Metric depth comes instead from the aligned depth buffer of Section 2.1.2, which is a measurement rather than an inference. The heavy variant of the pose model is used, in video mode, which tracks the person across frames rather than re-detecting from scratch."),

(H3, "2.2.2 Landmark Coordinate Extraction"),

(P, "Of the 33 landmarks, this thesis uses exactly eight, covering the torso and the two arms:"),
(TBL, [["ID", "Landmark", "ID", "Landmark"],
       ["L11", "left shoulder", "L12", "right shoulder"],
       ["L13", "left elbow", "L14", "right elbow"],
       ["L15", "left wrist", "L16", "right wrist"],
       ["L23", "left hip", "L24", "right hip"]]),
(CAP, "Table 2.2. The eight MediaPipe landmarks used in this work. Left and right refer to the subject's own left and right; the subject faces the sensor."),

(P, "Per frame, the extraction proceeds in three steps. First, the normalised coordinates are scaled to pixels: u = xn * 640 and v = yn * 480. Second, the 5 by 5 median depth of Section 2.1.3 is sampled at that pixel. Third, the pixel and depth are back-projected to a metric 3D position in the camera frame. Figure 2.3 shows the result on a real frame, and Figure 2.4 visualises the same eight positions as vectors from the sensor origin, which is exactly what the back-projection produces: a position vector for each landmark, expressed in the camera frame."),

(IMG, FIG + "fig2_landmarks_frame100.png", 5.2),
(CAP, "Figure 2.3. The eight upper-body landmarks detected on frame 100 of the evaluation recording. The subject is holding the marked cube in the right hand (L16)."),

(IMG, FIG + "fig3_landmark_vectors.png", 6.3),
(CAP, "Figure 2.4. (a) The detected landmarks of Figure 2.3. (b) The same landmarks as 3D position vectors from the sensor origin in the camera frame, after depth fusion. The camera axes are drawn at the origin: x right, y down, z forward."),

(P, "A critical property of MediaPipe shapes the whole extraction design: the model always outputs coordinates for all 33 landmarks, whether they are visible or not. An occluded wrist still receives a position, and that position is a guess. The visibility score is the only signal separating measurement from hallucination. The evaluation recording provides concrete evidence: during the first ten frames, while the model warms up, it reports left elbow and wrist positions up to two metres away from any plausible location, with visibility scores climbing from 0.001 toward 0.5."),

(P, "The extractor therefore gates on visibility. A landmark with v below 0.5 is written as an empty cell, not as a coordinate. The same applies when the 5 by 5 depth window contains no valid return. Every exported landmark carries a provenance flag recording which of three cases produced it: measured, blocked by low visibility, or blocked by missing depth. On the evaluation recording this gate blocks 9 left-elbow frames and 10 left-wrist frames (the warm-up period) and nothing else; all eight landmarks are otherwise measured on all 899 frames. This design rule, convert wrong data into missing data and then handle missing data explicitly, recurs throughout the system: the occlusion handling of Chapter 3 and the marker gap handling of Chapter 4 both rely on gaps being honest."),

(H3, "2.2.3 Work Example"),

(P, "Take the right wrist (L16) on frame 100, the frame of Figure 2.3, where the subject holds the cube in the right hand. MediaPipe reports the landmark at normalised coordinates (0.4375, 0.3083) with visibility 0.995, well above the 0.5 gate. Scaling to pixels: u = 0.4375 * 640 = 280.0 and v = 0.3083 * 480 = 148.0. The 5 by 5 median depth at pixel (280, 148) is z = 0.991 m. Back-projection with the Table 2.1 intrinsics gives"),
(P, "x = 0.991 * (280 - 323.94) / 607.56 = -0.0717 m"),
(P, "y = 0.991 * (148 - 248.02) / 607.02 = -0.1633 m"),
(P, "so the right wrist is at (-0.072, -0.163, 0.991) in the camera frame. Comparing with the object marker position from the example of Section 2.1.4, (0.067, -0.112, 0.929), the wrist-to-marker distance is about 16 centimetres, consistent with a hand gripping a 7 centimetre cube whose marked face points away from the palm. The other seven landmarks of the frame are processed identically, producing the eight position vectors of Figure 2.4(b)."),

(H2, "2.3 Fiducial Marker Tracking"),

(P, "The landmark detections of Section 2.2 measure the person, but the research objectives of Chapter 1 require more: an independent measurement of the manipulated object, expressed in a frame that does not move with the camera, that can serve as the reference against which the reconstructed motion is judged. No external ground truth exists for the person's joints in this setup. Fiducial markers fill that gap at the object level. They are printed patterns whose geometry is known exactly, so their pose can be computed from a single image without training data or appearance models, and with accuracy that can be verified independently. In this thesis the markers play a double role: two static markers define the world coordinate frame and the ground-truth scene geometry, and one marker rides on the manipulated object, providing the independent object trajectory used in the evaluation of Chapter 6."),

(P, "Among the available fiducial systems, ArUco markers offer a favourable combination of detection robustness, computational cost, and built-in identity encoding [27]. Each marker encodes an integer identifier in a grid of black and white cells, so a single detection resolves both which marker it is and where it is. The markers used here are drawn from the 5 by 5 OpenCV dictionary. Experimental characterisation of ArUco pose accuracy as a function of marker size and viewing distance is given in [28], and it informed the marker sizes chosen in Section 2.4.1."),

(H3, "2.3.1 ArUco Marker Detection"),

(P, "Detection proceeds through four stages. First, adaptive thresholding turns the image into binary regions by comparing each pixel to its local neighbourhood mean, which makes the detector robust to uneven lighting. Second, contour extraction finds candidate quadrilaterals. Third, the interior of each candidate is perspective-corrected and its cell pattern matched against the dictionary, which either rejects the candidate or yields a marker identity. Fourth, the four corner positions are refined to sub-pixel accuracy. Figure 2.5 shows the result on frame 100: all three markers of the setup are detected, each with its identity and its coordinate axes drawn from the estimated pose."),

(IMG, FIG + "fig4_aruco_frame100.png", 5.2),
(CAP, "Figure 2.5. ArUco detection on frame 100. The wall marker (id 0, top right), the object marker on the carried cube (id 1, centre), and the desk marker (id 2, bottom) are detected, each with its estimated coordinate axes drawn at its centre."),

(P, "The sub-pixel refinement stage deserves emphasis, because this work surfaced a subtle trap in it. With the default detector settings, corner coordinates lock onto integer pixels. The nearby desk marker then showed 0.00 millimetres of frame-to-frame scatter, which looks like perfect stability but is actually the detector snapping to the same pixels every frame, hiding the true measurement noise. Enabling the AprilTag sub-pixel refinement reveals the real scatter (0.4 millimetres for the desk marker) and, more importantly, improves the far wall marker's position estimate from 37 millimetres to 7 millimetres of scatter. All detections in this work use this refinement. Frames where a marker is not detected are recorded as empty cells, the same honest-gap convention as the landmark extraction."),

(H3, "2.3.2 Pose Estimation from Markers"),

(P, "A detected marker gives four corner pixels, and the marker's physical geometry gives the same four corners in the marker's own frame: for side length L, the corners sit at (±L/2, ±L/2, 0), in the marker plane with the origin at the centre. Finding the marker's pose means finding the rotation R and translation t that map these known 3D corners onto the four detected pixels through the camera projection of Section 2.1.1. Because the detected corners carry noise, no pose reproduces them exactly, so the problem is posed as a minimisation of the reprojection error: the sum over the four corners of the squared pixel distance between the detected corner and the projection of the corresponding 3D corner under the candidate pose."),

(P, "This is the Perspective-n-Point (PnP) problem, and the counting works out as follows. The unknown pose has six degrees of freedom, three for rotation and three for translation. Each corner correspondence supplies two constraints, one per pixel coordinate, so four corners supply eight constraints for six unknowns. The pose is over-determined, and the two spare constraints provide robustness against corner noise. Because all four corners of a flat marker lie in one plane, the specialised planar solver IPPE is used. A planar marker viewed nearly face-on admits two pose interpretations, tilted toward or away from the camera by the same amount, that project almost identically; IPPE returns both candidates with their reprojection errors, and the disambiguation policy between them is part of the scene reconstruction method of Chapter 4. The solver returns the rotation in the compact Rodrigues form, which is converted immediately to a 3 by 3 rotation matrix; the conversion is given in Appendix B. Deeper detail of the ArUco pipeline internals, which are used here as a tool rather than contributed, is also collected in Appendix B."),

(H3, "2.3.3 Work Example"),

(P, "Frame 100 again, object marker (id 1), side length L = 50 mm. The four marker-frame corners are (±0.025, ±0.025, 0) m. From the four detected corner pixels, IPPE returns the pose with translation t = (0.0675, -0.1111, 0.9268) m and rotation matrix"),
(P, "R = [ 0.951, -0.060, 0.303 ;  -0.097, -0.989, 0.108 ;  0.293, -0.132, -0.947 ]"),
(P, "with a reprojection error of 0.16 pixels, meaning the recovered pose re-projects the corners onto the image within a sixth of a pixel of where they were detected. Reading the pose: the translation places the marker centre 6.7 cm right of the optical axis, 11.1 cm above it, at 0.93 m depth. The third column of R is the direction of the marker's z-axis (the outward normal of the marked face) expressed in the camera frame: (0.303, 0.108, -0.947), a vector pointing mostly back toward the camera (negative z) and tilted right and slightly down, matching the visible orientation of the cube in Figure 2.5."),

(P, "Two independent checks are available for this single detection. The depth cross-check: the PnP depth of 0.9268 m against the stereo depth of 0.929 m from Section 2.1.4 agree within 2.2 mm. This also confirms the configured marker size, because PnP infers distance from apparent size, so a wrongly configured side length would scale the PnP depth in proportion. And the static markers in the same frame show the method's precision: the wall marker (id 0) is recovered with 0.05 pixels of reprojection error at 3.4 m distance. Averaged over both full recordings, the mean reprojection errors are 0.20 pixels (wall), 0.42 pixels (desk), and 0.08 pixels (object)."),

(H2, "2.4 Data Acquisition and Preprocessing"),

(H3, "2.4.1 Sensor Placement and Calibration Setup"),

(P, "The physical test environment is a desk against a wall. The subject stands at the desk and performs the manipulation tasks with a 70 millimetre cube. The camera is mounted on a fixed support at the desk edge at approximately chest height, facing the subject at a working distance of 1.5 to 2 metres. This distance is a compromise. Moving closer improves both the pixel resolution on the landmarks and the depth accuracy, since depth noise grows with distance squared, but it risks the extended arms leaving the field of view (measured 55.6 by 43.1 degrees from the colour intrinsics). The chosen distance keeps the whole upper body and the working surface in view throughout the tasks."),

(P, "Three ArUco markers define the measured scene:"),
(TBL, [["ID", "Size (mm)", "Location", "Role"],
       ["0", "150", "wall", "static; assumed plumb; defines the gravity direction"],
       ["2", "50", "desk", "static; world anchor: origin of the world frame"],
       ["1", "50", "object (one face of the 70 mm cube)", "dynamic; the tracked object"]]),
(CAP, "Table 2.3. ArUco marker configuration. All markers are from the OpenCV 5 by 5 dictionary."),

(P, "The roles encode the ground-truth definition of this thesis. The world coordinate frame is anchored at the desk marker: every pose in the reconstruction, including the camera's own, is ultimately expressed in the desk marker's frame, which makes the reconstruction invariant to where the camera stands. The wall marker carries the single physical assumption in the entire setup: the wall is plumb, so the wall marker's in-plane up axis defines the gravity direction. Everything else is measured rather than assumed. The wall marker's larger size is deliberate; at 3.4 metres it subtends only about 32 pixels even at 150 millimetres, and pose accuracy degrades with apparent size. Scene calibration, in which the static marker poses are averaged over the first ten detections and frozen, is developed in Chapter 4. One empirical placement finding from comparing the two recording setups is worth stating here: the desk-edge camera position outperformed a higher camera mount on every stability metric measured (for example, wall pose stability of 0.54 versus 2.4 degrees at the 95th percentile), so camera placement matters more than marker size at these scales."),

(P, "Three recordings are used in this thesis, each 899 frames (about 30 seconds) at 640 by 480 and 30 frames per second:"),
(TBL, [["Recording", "Setup", "Use"],
       ["20260224_083945", "standing subject carries the cube (1.94 m of travel), parking it on the desk mid-recording; camera at desk edge", "primary evaluation recording"],
       ["20260225_230607", "standing subject, arms moving, object untouched", "kinematic validation on real data"],
       ["20260328_021733", "seated subject, object untouched, camera mounted high, desk marker on a tilted stand", "cross-validation of the marker pipeline"]]),
(CAP, "Table 2.4. The three recordings. Frame 100 of the first recording is the running example of this chapter."),

(H3, "2.4.2 Bag File Replay and Frame Extraction"),

(P, "Each capture session is stored as a bag file, the RealSense container format that holds the synchronized colour and depth streams together with timestamps and the calibration metadata, including the intrinsics of Table 2.1. The offline pipeline replays the bag one frame at a time. Because processing is offline, replay does not need to keep pace with the original 30 frames per second; each frame is read, aligned, processed completely by both branches, and only then is the next frame requested. This removes all time pressure and makes every result exactly repeatable, which is what allows the strict validation methodology of the later chapters. The real-time variant of the system, where this luxury disappears, is the subject of Chapter 7."),

(P, "One implementation detail of the replay affects correctness. MediaPipe's video mode requires strictly increasing timestamps in integer milliseconds, while bag playback timestamps can repeat or jitter. Each timestamp is therefore clamped to be at least one millisecond after its predecessor before being handed to the detector."),

(H3, "2.4.3 Signal Smoothing"),

(P, "The raw 3D landmark trajectories carry three distinct kinds of error, and the preprocessing treats each with a dedicated stage rather than one catch-all filter. Consider the three cases on a concrete trajectory. Case A: an isolated sample jumps far off the local path for one frame (a depth speckle or a momentary mis-detection). Case B: a few consecutive samples are missing entirely (the gate of Section 2.2.2 blocked them). Case C: every sample carries small broadband jitter from detection and depth noise. These require different treatments, because a smoother that is strong enough to flatten case A would also distort genuine fast motion, and no smoother can fill case B."),

(P, "Stage one handles case A with a Hampel despike: over a rolling 11-frame window, a sample is flagged as a glitch when it departs from the local median by more than three robust standard deviations (estimated from the median absolute deviation), with an absolute floor of 2 centimetres so that noise-level wiggle at rest is never flagged. Because the threshold adapts to the local motion, fast genuine movement raises it and is not flagged. Flagged samples are invalidated and join the missing data of case B. Stage two fills case B: interior gaps of at most 5 frames (167 milliseconds) are linearly interpolated between their valid endpoints, which is an honest bound over a short occlusion; longer gaps stay missing, because inventing positions across long gaps is the job of the occlusion handling in Chapter 3, in angle space rather than point space. Gaps at the recording boundary are backfilled with the nearest valid sample, which removed a 60.3 degree single-frame snap that the warm-up gap otherwise produced in the streamed output. Stage three smooths case C with a low-pass Butterworth filter, cutoff 3 Hz, applied forward and backward so the net phase shift is exactly zero and motion peaks stay where they happened."),

(P, "The choice of the final smoother was measured, not assumed. Five candidates were compared on the evaluation recording using two numbers: residual shake (mean frame-to-frame displacement at rest) and fast-motion deviation (departure from the despiked raw signal during fast wrist motion, where any lag shows up as error):"),
(TBL, [["Method", "Shake (mm)", "Fast-motion deviation (mm)"],
       ["raw (no smoothing)", "10.2", ""],
       ["Savitzky-Golay, window 9, order 2", "2.8", "4.8"],
       ["rolling median, window 9", "2.9", "3.9"],
       ["Butterworth 3 Hz, zero phase (chosen)", "1.9", "4.8"],
       ["Butterworth 2 Hz, zero phase", "1.5", "5.3"],
       ["One Euro filter (causal)", "1.1", "28.4"]]),
(CAP, "Table 2.5. Measured smoother comparison on the evaluation recording. The chosen zero-phase Butterworth at 3 Hz gives five times less shake than raw at the same motion fidelity as Savitzky-Golay."),

(P, "The table explains a choice that would otherwise look surprising. The One Euro filter [40] is a popular adaptive filter for interactive tracking, and it produces the least shake of all candidates. But its 28.4 millimetres of fast-motion deviation is pure causal lag: as a real-time filter it can only look backward, so during fast motion it trails the true position. The offline pipeline has no reason to accept that lag, because zero-phase filtering (running the filter forward and then backward over the recorded data) is available offline and eliminates lag exactly. The One Euro filter is therefore excluded here but returns as the natural candidate in the real-time system of Chapter 7, where causality is unavoidable and its adaptive cutoff (smooth when slow, responsive when fast) is exactly the right trade-off. Figure 2.6 shows the filter chain's effect on the evaluation recording."),

(IMG, FIG + "fig6_filter_qc.png", 6.3),
(CAP, "Figure 2.6. Filter quality-control plot for the evaluation recording: per-axis raw and filtered trajectories with flagged glitches and repaired gaps."),

(P, "The stage is bound by an explicit honesty contract, enforced by the validators of later chapters. The raw file is never modified; the filter writes a separate file. Every repaired sample carries a provenance flag, so downstream consumers can always distinguish measured data from repaired data. And smoothing must not invent geometry: the filter is asserted to move measured samples by less than the raw measurement jitter."),

(H3, "2.4.4 Sampling Rate Overview"),

(P, "All streams run at the sensor's 30 frames per second, giving a frame interval of 33.3 milliseconds and 899 frames over each 30-second recording. Voluntary human upper-body motion lives below roughly 5 Hz, so 30 Hz sampling sits comfortably above the Nyquist requirement, and the 3 Hz smoothing cutoff of Section 2.4.3 preserves the full motion band while removing broadband noise. Both processing branches consume the same frame sequence from the same bag, so a single frame index identifies simultaneous person and object measurements throughout the system; this shared index is what makes the data fusion of Chapter 4 a pairing operation rather than a resampling problem. The rendering side runs at its own rate, and the consequences of that mismatch, including the temporal alignment issues it can cause, are examined in Chapters 7 and 8."),

(H2, "2.5 Unity-Python Communication Preliminaries"),

(H3, "2.5.1 UDP Protocol Basics and Packet Structure"),

(P, "The processing pipeline runs in Python; the graphical reconstruction runs in Unity. The two are separate processes, so the per-frame results must cross a process boundary. The bridge supports two transports that share one packet format. The first is UDP, the connectionless datagram protocol: the sender transmits each frame's record as one datagram to a local port, and the receiver reads whole datagrams as they arrive. UDP is simple and has the right semantics for pose streaming, because each packet is a complete self-contained state and a lost or reordered packet should simply be superseded by the next one rather than retransmitted. The second transport is shared memory: the sender writes the same record into a small file in memory (/dev/shm), guarded by a sequence counter that is odd while a write is in progress and even when the record is stable, so the reader can detect and retry a torn read. Shared memory is the default in this work because it has lower latency and lets the newest frame overwrite the previous one with no queueing."),

(P, "The landmark packet is a fixed 180-byte little-endian record: a four-byte magic identifier, a sequence counter (used by the shared-memory transport), the frame index, the frame time in seconds, the landmark count, and then eight landmark blocks of {landmark id, x, y, z, valid flag}. The valid flag carries the honest-gap convention of Section 2.2.2 across the process boundary, so Unity knows which landmarks are measured and which are missing in each frame. The integrated system of Chapter 5 extends this pattern with a packet that carries the person state and the object state together in a single record, which makes desynchronization between them structurally impossible."),

(H3, "2.5.2 Frame Synchronization Overview"),

(P, "During offline replay the sender paces packets to the recorded timestamps, so Unity receives frames at the original 30 frames per second regardless of how fast the offline processing ran. Synchronization between the person data and the object data requires no clock at all: both branches are indexed by the same frame number from the same bag, so fusion is exact pairing by construction. The remaining synchronization concern is between the sender's 30 Hz update rate and Unity's own render rate, which is typically higher and not locked to the sender. Unity therefore always renders the most recently received stable record. The subtleties this introduces for the live system, where the sender is a real sensor rather than a paced replay, are treated in Chapter 7."),

(H3, "2.5.3 Unity Humanoid Rig Fundamentals"),

(P, "On the Unity side, the person is represented by a humanoid rig: a hierarchy of bones (hips, spine, shoulders, upper arms, forearms, hands) in which each bone's rotation is expressed relative to its parent. This structure is why the kinematic modeling of Chapter 3 exists. The rig is not driven by placing points in space; it is driven by rotating joints. Feeding it the eight landmark positions directly would do nothing sensible, so the pipeline must first resolve the relative rotations of the body segments from the measured positions, and those angles are what the packets of Section 2.5.1 ultimately carry (the integrated packet of Chapter 5 streams 13 angle values plus the object pose)."),

(P, "Two properties of the rig matter for later chapters. First, Unity's coordinate frame is left-handed with y up, while the camera frame of Section 2.1.3 is right-handed with y down; the conversion is a fixed axis flip applied to every point, developed in Chapter 3. Second, the rig's proportions are those of the imported character model, not of the recorded person; the forearm of the rig used here is about 1.6 times the person's forearm length in proportion to the upper arm. Joint angles transfer between differently proportioned bodies, but positions do not, which is a second reason the system streams angles. The measured rig dimensions and the scale calibration that reconciles rig space with the metric scene are part of the integration procedure of Chapter 5."),

(H2, "References"),
(P, "Reference numbering continues from Chapter 1; entries cited in this chapter:"),
]

references = {
3:  'G. Buckingham, "Hand tracking for immersive virtual reality: Opportunities and challenges," Frontiers in Virtual Reality, vol. 2, p. 728461, 2021.',
9:  'L. Keselman, J. Iselin Woodfill, A. Grunnet-Jepsen, and A. Bhowmik, "Intel RealSense stereoscopic depth cameras," in Proc. IEEE Conf. Computer Vision and Pattern Recognition Workshops (CVPRW), 2017.',
12: 'S. Dill et al., "Accuracy evaluation of 3D pose reconstruction algorithms through stereo camera information fusion for physical exercises with MediaPipe Pose," Sensors, vol. 24, no. 23, art. 7772, 2024.',
13: 'Y. Dong, "Tracking and reconstruction of object grasping hand using a RGB-D sensor," M.A.Sc. thesis, Simon Fraser University, 2024.',
26: 'F. Zhang et al., "MediaPipe Hands: On-device real-time hand tracking," arXiv:2006.10214, 2020.',
27: 'M. Kalaitzakis, B. Cain, S. Carroll, A. Ambrosi, C. Whitehead, and N. Vitzilaios, "Fiducial markers for pose estimation: Overview, applications and experimental comparison," Journal of Intelligent and Robotic Systems, vol. 101, art. 71, 2021.',
28: 'J. L. Pulloquinga, D. Corrata, V. Mata, A. Valera, and M. Valles, "Experimental analysis of pose estimation based on ArUco markers," in Innovations in Industrial Engineering III (Lecture Notes in Mechanical Engineering), Cham: Springer, 2024, pp. 138-149.',
38: 'Z. Zhang, "A flexible new technique for camera calibration," IEEE Transactions on Pattern Analysis and Machine Intelligence, vol. 22, no. 11, pp. 1330-1334, 2000.',
39: 'V. Bazarevsky, I. Grishchenko, K. Raveendran, T. Zhu, F. Zhang, and M. Grundmann, "BlazePose: On-device real-time body pose tracking," arXiv:2006.10204, 2020.',
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

for n in sorted(references):
    doc.add_paragraph(f"[{n}] {references[n]}")

out = "/home/luo/Desktop/New_SandBox/writing/v2/Chapter_2_Background.docx"
doc.save(out)
print("saved", out)
