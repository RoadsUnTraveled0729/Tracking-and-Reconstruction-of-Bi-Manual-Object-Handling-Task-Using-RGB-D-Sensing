#!/usr/bin/env python3
"""Build writing/v3/Appendix.docx.

Per writing/v3/STRUCTURE.md the Appendix sits after References and holds the
perception-layer detail moved out of the main body:
  Appendix A: v2 Chapter 2 section 2.1 (RGB-D sensing, calibration, alignment,
              deprojection, worked example).
  Appendix B: v2 Chapter 2 section 2.2 (MediaPipe BlazePose, extraction,
              worked example).
  Appendix C: v2 Chapter 2 section 2.3 merged with v2 Chapter 4 sections
              4.2.1, 4.2.2, 4.2.5 (detection, sub-pixel corners, planar pose,
              two-solution ambiguity, frame-100 example), plus the
              Rodrigues-to-matrix conversion (from the pinned math notes;
              formula exp([w]x) = I + sin(theta) [w]x + (1-cos(theta)) [w]x^2).
Duplicated passages between the ch2 and ch4 versions were merged, keeping the
fuller ch4 wording. Figure/table labels renumbered A.1, B.1, C.1, ...
Internal cross-references re-pointed (Chapter 2/4 section numbers no longer
exist here). No numbers changed; all values as pinned in v2.
"""
from docx import Document
from docx.shared import Pt, Inches

FIG = "/home/luo/Desktop/New_SandBox/writing/v2/figures/"
H1, H2, H3, P, IMG, CAP, TBL = "h1", "h2", "h3", "p", "img", "cap", "tbl"

content = [
(H1, "Appendix A: Depth Sensing and Deprojection"),

(P, "The Intel RealSense D435 is a stereo-depth camera that produces per-pixel depth measurements alongside a colour image [9]. Depth is computed by triangulating between two infrared imagers separated by a known baseline, assisted by an infrared projector that adds texture to surfaces that would otherwise be too uniform for stereo matching. In this work both streams are recorded at 640 by 480 pixels and 30 frames per second. The subject stands at a working distance of roughly 1.5 to 2 metres, and the measured scene spans depths from 0.65 metres (the desk marker) to 3.4 metres (the wall marker), all comfortably inside the sensor's reliable operating range. Two properties of stereo depth matter for everything in the main body: the depth error grows roughly with the square of the distance, and one pixel of image error corresponds to a lateral position error that grows linearly with distance, about 1.6 millimetres per pixel at 1 metre for the intrinsics used here."),

(H2, "A.1 RGB Camera Calibration"),

(P, "Camera calibration establishes the mathematical relationship between 3D points in the scene and their 2D projections in the image. The standard pinhole model describes this relationship through the intrinsic matrix K, which contains four numbers: the focal lengths fx and fy in pixels along the horizontal and vertical image axes, and the principal point (cx, cy), the pixel where the optical axis meets the image [38]. A 3D point p = (x, y, z) expressed in the camera frame projects to the pixel"),
(P, "u = fx * x / z + cx,        v = fy * y / z + cy."),
(P, "Reading the first equation in words: the point's horizontal offset x is divided by its depth z, which captures the fact that the same offset appears smaller when it is farther away; the ratio is scaled by the focal length fx to convert from a geometric angle to a pixel count; and the principal point cx shifts the result from optics-centred coordinates to the pixel grid, whose origin is the top-left corner. The vertical equation works the same way."),

(P, "Calibration normally estimates these parameters by imaging a planar checkerboard from multiple viewpoints and minimising the reprojection error, following Zhang's method [38]. In this work no manual calibration was performed. The RealSense SDK exposes the factory calibration of each individual device, and these factory intrinsics are used directly. For the colour camera of the sensor used in all recordings, at 640 by 480 resolution, the values are:"),
(TBL, [["Parameter", "Value", "Meaning"],
       ["fx", "607.56 px", "horizontal focal length"],
       ["fy", "607.02 px", "vertical focal length"],
       ["cx", "323.94 px", "principal point, horizontal (near the image centre 320)"],
       ["cy", "248.02 px", "principal point, vertical (near the image centre 240)"]]),
(CAP, "Table A.1. Factory colour-camera intrinsics of the RealSense D435 used in this work, recorded in the extraction metadata of every recording."),
(P, "Two observations connect these numbers to the model. The two focal lengths agree within 0.1 percent, meaning the pixels are very nearly square. And the principal point sits within 9 pixels of the geometric image centre, a typical manufacturing offset that the model absorbs exactly. The factory calibration proved sufficient for the positional accuracy targets of this system, which the worked example in Section A.4 confirms against an independent measurement."),

(H2, "A.2 Depth-to-RGB Alignment"),

(P, "The depth imager and the colour camera are physically offset by a small baseline inside the D435 housing, and each has its own intrinsics [9]. A raw depth pixel at location (u, v) therefore does not observe the same scene point as the colour pixel at the same location. The RealSense SDK resolves this with a depth-to-colour alignment step: each depth pixel is lifted to a 3D point using the depth camera's intrinsics, moved into the colour camera's frame through the known transformation between the two imagers, and reprojected onto the colour image grid using the colour intrinsics of Table A.1. Figure A.1(b) illustrates the arrangement."),

(P, "In this work both buffers are 640 by 480, so the alignment produces a depth image on exactly the same pixel grid as the colour image. After alignment, the colour value and the depth value at any pixel (u, v) refer to the same physical point. This aligned pair is the only input the rest of the pipeline ever sees. Every landmark detection and every marker detection happens in colour pixel coordinates, and the same coordinates index the aligned depth buffer directly, with no further correspondence step."),

(IMG, FIG + "fig5_alignment_schematic.png", 6.3),
(CAP, "Figure A.1. (a) Pinhole projection geometry of the colour camera: a scene point projects to the pixel where the ray to the camera centre crosses the image plane. (b) Depth-to-colour alignment: the depth buffer is reprojected into the colour camera's geometry so both buffers share one pixel grid."),

(H2, "A.3 Pixel-to-World Mapping"),

(P, "Given the aligned depth image and the colour intrinsics, any pixel (u, v) with a valid depth z can be lifted to a 3D point in the camera frame by inverting the pinhole projection:"),
(P, "x = z * (u - cx) / fx,        y = z * (v - cy) / fy,        p = (x, y, z)."),
(P, "This is the projection of Section A.1 run backwards, and it is exact because the depth supplies the one piece of information the forward projection discards. The resulting camera frame is right-handed: x points right in the image, y points down, and z points forward into the scene along the optical axis [13]. The depth measurement itself is the z coordinate in this frame. The conversion of these camera-frame points into Unity's left-handed convention is a fixed axis flip, developed in Chapter 3."),

(P, "One practical detail matters more than the equations. Reading depth at a single pixel fails in two ways: the pixel can be a hole (a zero return, common at object edges and on dark or reflective surfaces), and it can carry single-pixel speckle noise. The system therefore never samples one pixel. Instead it takes the median of the nonzero depths in a 5 by 5 window centred on the target pixel. The median tolerates up to half the window being outliers, and excluding zero returns treats holes as absent samples rather than as fake zero depths. Measured over a full recording, this windowed median moves validly measured landmarks by 0.0 millimetres at the median (99th percentile below 7.5 millimetres, within depth noise) while recovering landmarks that a single-pixel read would have lost to holes. If the entire window has no valid return, the sample is honestly reported as missing rather than guessed."),

(H2, "A.4 Work Example"),

(P, "Consider frame 100 of the evaluation recording, the running example frame of the thesis. The marker detector of Appendix C locates the centre of the object marker at pixel (u, v) = (368, 175), and the 5 by 5 median depth at that pixel is z = 0.929 m. Substituting into the back-projection equations with the intrinsics of Table A.1:"),
(P, "x = 0.929 * (368 - 323.94) / 607.56 = 0.929 * 0.0725 = 0.0674 m"),
(P, "y = 0.929 * (175 - 248.02) / 607.02 = 0.929 * (-0.1203) = -0.1118 m"),
(P, "so the marker centre sits at (0.067, -0.112, 0.929) in the camera frame: about 7 centimetres right of the optical axis, 11 centimetres above it (y is negative because the camera y-axis points down), at just under a metre of depth."),

(P, "This example was chosen because it comes with an independent check. The same marker's pose is also computed by the completely separate Perspective-n-Point method of Appendix C, which infers position from the marker's corner geometry alone, without using the depth buffer at all. PnP places the marker centre at (0.0675, -0.1111, 0.9268). The two estimates, one from stereo depth and one from marker geometry, agree within 1 millimetre in x, 0.7 millimetres in y, and 2.2 millimetres in z. Two unrelated measurement principles landing on the same point at millimetre level is the concrete justification for trusting the factory calibration in Section A.1."),

(H1, "Appendix B: Pose Landmark Detection"),

(H2, "B.1 MediaPipe BlazePose Overview"),

(P, "Modern learning-based pose detectors share a common structure: a detector network first localises the person (or a region of interest) in the image, and a regression network then predicts a fixed set of landmark coordinates within that region. Systems differ mainly in the backbone networks, the training data, and whether they output 2D points, 3D points, or full body meshes. For this thesis the requirements are specific: per-joint image coordinates that can be fused with a depth buffer, a per-joint confidence signal for occlusion handling, and real-time operation on consumer hardware. MediaPipe's BlazePose model [39], deployed through the MediaPipe framework [26], meets all three. It runs on-device, it outputs individual landmarks rather than an opaque mesh, and it attaches to every landmark a visibility score that the occlusion handling of the main body uses as the primary occlusion signal."),

(P, "BlazePose follows the two-stage pattern: a lightweight person detector localises a region of interest, and a landmark network regresses 33 anatomical keypoints within it, covering the face, torso, arms, and legs [39]. For each landmark the model outputs normalised image coordinates (xn, yn) in the range 0 to 1, a monocular depth estimate inferred from appearance, and a visibility score v between 0 and 1 expressing the model's confidence that the landmark is present and unoccluded. The monocular depth estimate is not used in this system. As noted in [3] and demonstrated empirically in [12], it carries substantial uncertainty during fast motion and object interaction, precisely the conditions of bimanual manipulation. Metric depth comes instead from the aligned depth buffer of Appendix A, which is a measurement rather than an inference. The heavy variant of the pose model is used, in video mode, which tracks the person across frames rather than re-detecting from scratch."),

(H2, "B.2 Landmark Coordinate Extraction"),

(P, "Of the 33 landmarks, this thesis uses exactly eight, covering the torso and the two arms:"),
(TBL, [["ID", "Landmark", "ID", "Landmark"],
       ["L11", "left shoulder", "L12", "right shoulder"],
       ["L13", "left elbow", "L14", "right elbow"],
       ["L15", "left wrist", "L16", "right wrist"],
       ["L23", "left hip", "L24", "right hip"]]),
(CAP, "Table B.1. The eight MediaPipe landmarks used in this work. Left and right refer to the subject's own left and right; the subject faces the sensor."),

(P, "Per frame, the extraction proceeds in three steps. First, the normalised coordinates are scaled to pixels: u = xn * 640 and v = yn * 480. Second, the 5 by 5 median depth of Appendix A is sampled at that pixel. Third, the pixel and depth are back-projected to a metric 3D position in the camera frame. Figure B.1 shows the result on a real frame, and Figure B.2 visualises the same eight positions as vectors from the sensor origin, which is exactly what the back-projection produces: a position vector for each landmark, expressed in the camera frame."),

(IMG, FIG + "fig2_landmarks_frame100.png", 5.2),
(CAP, "Figure B.1. The eight upper-body landmarks detected on frame 100 of the evaluation recording. The subject is holding the marked cube in the right hand (L16)."),

(IMG, FIG + "fig3_landmark_vectors.png", 6.3),
(CAP, "Figure B.2. (a) The detected landmarks of Figure B.1. (b) The same landmarks as 3D position vectors from the sensor origin in the camera frame, after depth fusion. The camera axes are drawn at the origin: x right, y down, z forward."),

(P, "A critical property of MediaPipe shapes the whole extraction design: the model always outputs coordinates for all 33 landmarks, whether they are visible or not. An occluded wrist still receives a position, and that position is a guess. The visibility score is the only signal separating measurement from hallucination. The evaluation recording provides concrete evidence: during the first ten frames, while the model warms up, it reports left elbow and wrist positions up to two metres away from any plausible location, with visibility scores climbing from 0.001 toward 0.5."),

(P, "The extractor therefore gates on visibility. A landmark with v below 0.5 is written as an empty record, not as a coordinate. The same applies when the 5 by 5 depth window contains no valid return. Every exported landmark carries a provenance flag recording which of three cases produced it: measured, blocked by low visibility, or blocked by missing depth. On the evaluation recording this gate blocks 9 left-elbow frames and 10 left-wrist frames (the warm-up period) and nothing else; all eight landmarks are otherwise measured on all 899 frames. This design rule, convert wrong data into missing data and then handle missing data explicitly, recurs throughout the system: the occlusion handling of Chapter 3 and the marker gap handling of Chapter 4 both rely on gaps being honest."),

(H2, "B.3 Work Example"),

(P, "Take the right wrist (L16) on frame 100, the frame of Figure B.1, where the subject holds the cube in the right hand. MediaPipe reports the landmark at normalised coordinates (0.4375, 0.3083) with visibility 0.995, well above the 0.5 gate. Scaling to pixels: u = 0.4375 * 640 = 280.0 and v = 0.3083 * 480 = 148.0. The 5 by 5 median depth at pixel (280, 148) is z = 0.991 m. Back-projection with the intrinsics of Table A.1 gives"),
(P, "x = 0.991 * (280 - 323.94) / 607.56 = -0.0717 m"),
(P, "y = 0.991 * (148 - 248.02) / 607.02 = -0.1633 m"),
(P, "so the right wrist is at (-0.072, -0.163, 0.991) in the camera frame. Comparing with the object marker position from the example of Appendix A, (0.067, -0.112, 0.929), the wrist-to-marker distance is about 16 centimetres, consistent with a hand gripping a 7 centimetre cube whose marked face points away from the palm. The other seven landmarks of the frame are processed identically, producing the eight position vectors of Figure B.2(b)."),

(H1, "Appendix C: Fiducial Marker Detection and Pose Recovery"),

(P, "The landmark detections of Appendix B measure the person, but the research objectives of Chapter 1 require more: an independent measurement of the manipulated object, expressed in a frame that does not move with the camera, that can serve as the reference against which the reconstructed motion is judged. No external ground truth exists for the person's joints in this setup. Fiducial markers fill that gap at the object level. They are printed patterns whose geometry is known exactly, so their pose can be computed from a single image without training data or appearance models, and with accuracy that can be verified independently. In this thesis the markers play a double role: two static markers define the world coordinate frame and the ground-truth scene geometry, and one marker rides on the manipulated object, providing the independent object trajectory used in the evaluation of Chapter 6."),

(P, "Among the available fiducial systems, ArUco markers offer a favourable combination of detection robustness, computational cost, and built-in identity encoding [27]. Each marker encodes an integer identifier in a grid of black and white cells, so a single detection resolves both which marker it is and where it is. The markers used here are drawn from the 5 by 5 OpenCV dictionary. Experimental characterisation of ArUco pose accuracy as a function of marker size and viewing distance is given in [28], and it informed the marker sizes chosen in the setup of Chapter 2."),

(H2, "C.1 Detection and Sub-Pixel Corners"),

(P, "Detection proceeds through four stages. First, adaptive thresholding turns the image into binary regions by comparing each pixel to its local neighbourhood mean, which makes the detector robust to uneven lighting. Second, contour extraction finds candidate quadrilaterals. Third, the interior of each candidate is perspective-corrected and its cell pattern matched against the dictionary, which either rejects the candidate or yields a marker identity. Fourth, the four corner positions are refined to sub-pixel accuracy. Figure C.1 shows the result on frame 100: all three markers of the setup are detected, each with its identity and its coordinate axes drawn from the estimated pose."),

(IMG, FIG + "fig4_aruco_frame100.png", 5.2),
(CAP, "Figure C.1. ArUco detection on frame 100. The wall marker (id 0, top right), the object marker on the carried cube (id 1, centre), and the desk marker (id 2, bottom) are detected, each with its estimated coordinate axes drawn at its centre."),

(P, "Detection itself is standard and is not a contribution of this work [27]. What is a design decision, and one that measurement forced, is the corner refinement step. The pose mathematics of the next section consumes exactly four corner positions per marker, so the precision of those corners bounds the precision of everything downstream."),

(P, "With the detector's default settings, corner coordinates lock onto integer pixel positions. On this data the effect produced a diagnostic trap rather than an obvious failure: the desk marker, close to the camera and nearly motionless in the image, was reported at identical corner pixels frame after frame, a scatter of exactly 0.00 mm. That number looks like superb stability. It is actually the detector re-snapping to the same integer pixels and hiding the true measurement noise. Enabling subpixel corner refinement based on the AprilTag method [46] reveals the genuine scatter, 0.4 mm and 0.17 degrees for the desk marker, and at the same time improves the far wall marker's position estimate from 37 mm of scatter to 7 mm. All results in this thesis use the refined corners."),

(P, "One more per-frame quantity is recorded at detection time: the median of a 5 by 5 patch of aligned depth values at each marker's center pixel. The pose estimate of the next section never uses this number. It is kept precisely because it is independent, and the worked example at the end of this appendix uses it as a cross-check of the estimated ranges. Frames on which a marker is not detected are written as empty records, never interpolated at this stage; the same honest-gap convention as the landmark branch."),

(H2, "C.2 Planar Pose Recovery and the Two-Solution Ambiguity"),

(P, "A detected marker gives four corner points in the image, and the printed marker gives the same four points in the marker's own frame: for side length L they sit at (L/2, L/2, 0), (L/2, -L/2, 0), (-L/2, -L/2, 0), and (-L/2, L/2, 0), all in the marker plane z = 0. Finding the marker's pose means finding the rotation R and translation t that map these four known points onto the four detected pixels through the projection model of Appendix A. Since the detected corners carry noise, no pose reproduces them exactly, and the problem is posed as a minimisation: choose (R, t) to minimise the sum, over the four corners, of the squared image distance between the detected corner and the projection of the corresponding marker-frame corner, where projecting means applying R and t, dividing by depth, and applying the intrinsic matrix K [38]. Counting degrees of freedom shows why four corners suffice: the pose has six unknowns, and each corner contributes two pixel equations, giving eight constraints for six unknowns with two left over to average down the noise."),

(P, "For a planar target this minimisation has a structural weakness that a general 3D target does not have, and the weakness shaped the pipeline, so it is developed here in full. Because all four corners lie in one plane, the image observation constrains only the homography between that plane and the image, which pins down the first two columns of R and the translation, up to scale. A plane seen nearly face-on can be tilted slightly toward the camera or slightly away by the same amount and produce almost exactly the same four pixels; the two interpretations are mirror images of the marker normal about the viewing ray. The solver used here, the infinitesimal plane-based pose method IPPE [43], makes this concrete: it returns both locally optimal poses, called lobes here, each with its reprojection error, rather than silently picking one. Figure C.2(a) illustrates the geometry."),

(IMG, FIG + "ch4_fig4_lobes.png", 6.3),
(CAP, "Figure C.2. (a) A nearly fronto-parallel plane admits two pose interpretations, tilted toward or away from the camera, that reproject almost identically. (b) The measured angular separation between the two returned solutions for each marker, with the ranges at frame 100; the 40 degree line is the policy threshold that separates the well-conditioned markers from the wall."),

(P, "How far apart the two lobes sit is itself a conditioning signal. When the perspective cues are strong, the two candidate poses are far apart and the wrong one reprojects visibly worse; when the marker subtends only a few pixels, the lobes collapse toward each other and the image genuinely almost cannot tell them apart. The measured separations in this scene, shown in Figure C.2(b), split cleanly: about 64 degrees for the desk marker and 62 degrees for the object marker, both close to the camera, but only about 23 degrees for the wall marker, whose 150 mm print subtends roughly 32 pixels at its 3.4 m range."),

(P, "The pipeline's policy switches on this separation, at a threshold of 40 degrees, and not on the reprojection errors themselves. For the desk and object markers the geometry is well conditioned and the reprojection ratio between the two lobes is decisive, with measured ratios between 2.15 and 3.9, so the lower-error lobe is taken. For the wall marker the reprojection error turns out to be not merely noisy but systematically biased: in the analysis of this recording it preferred the physically wrong lobe, the one leaning away from plumb, on 815 of 837 wall detections, with error ratios reaching 2.18, squarely inside the range where the well-conditioned markers are genuinely decisive. No threshold on the ratio can separate the two situations; the discriminator itself has to change, not its tuning."),

(P, "For the wall, the discriminator is physical and temporal instead. On the first frame, the lobe is chosen by plumbness: the wall is vertical, so the lobe whose in-plane up axis better agrees with an independent, depth-based estimate of gravity is taken. That gravity seed, part of the scene calibration developed in Chapter 4, only needs to be accurate to about 10 degrees, because the wrong lobe sits about 23 degrees away. On every later frame the lobe closest to a reference pose is kept, with the reference updated only when the new pose lies within 30 degrees of it, so that one corrupted detection, for example the person's arm clipping the marker's edge, cannot poison the frames that follow; after five consecutive misses the tracker re-seeds. The result on the evaluation recording: all 841 wall detections resolved, none flagged unresolved, and the chosen orientation agrees with the independent depth-based gravity to about 5 degrees, where the wrong lobe would disagree by about 23. A per-frame flag records how each pose was resolved, so downstream stages can distinguish a cleanly decided pose from a continuity-resolved one."),

(P, "One rejected alternative deserves its paragraph, because its failure is instructive. This alternative breaks the tie by comparing each lobe's normal against a plane fitted to the local depth image. For a 32 pixel quad at 3 m the depth patch is simply too small and too noisy: the fitted normal was biased by more than 30 degrees, and it consistently endorsed the same wrong lobe. Every per-column statistic of that design looked healthy; the scatter was small, the tracks were smooth, and the validation of individual numbers passed. What exposed the bug was rendering the implied geometry: the reconstructed wall landed in the plane of the desk. The lesson, that physical-consistency rendering catches error classes that per-column statistics cannot, recurs in Chapter 5, where it is applied to the person as well."),

(H2, "C.3 From the Rodrigues Form to a Rotation Matrix"),

(P, "The pose solver returns its rotation in the compact Rodrigues form: a single 3-vector omega whose direction is the rotation axis and whose length is the rotation angle theta in radians. The main body works exclusively in rotation matrices, so this vector is converted to a 3 by 3 matrix immediately on receipt, and the conversion is spelled out here because the same formula reappears in the object-track filtering of Chapter 4 as the exponential in the geodesic interpolation."),

(P, "Write w for the unit axis, so omega = theta * w. The first ingredient is the skew-symmetric matrix of w, written [w]x, built from the components w = (w1, w2, w3) as the matrix with rows (0, -w3, w2), (w3, 0, -w1), (-w2, w1, 0). This matrix implements the cross product: for any vector v, the product [w]x v equals w cross v. Applying it twice, [w]x [w]x v, removes from v its component along the axis and negates the rest, which is the second ingredient the formula needs."),

(P, "The conversion is Rodrigues' rotation formula:"),
(P, "R = I + sin(theta) [w]x + (1 - cos(theta)) [w]x^2."),
(P, "Reading the three terms in words: the identity term starts from the vector unchanged; the sin(theta) term adds the component perpendicular to the axis rotated a quarter turn, scaled by the sine of the angle, which produces the circular sweep; and the (1 - cos(theta)) term pulls the perpendicular component toward its rotated position while leaving the along-axis component untouched, so points on the axis do not move at all. At theta = 0 the sine and one-minus-cosine factors both vanish and R is the identity, as it must be. The formula is exact for every angle, involves no small-angle approximation, and produces a proper rotation matrix by construction. Its inverse, recovering axis and angle from a matrix, is the matrix logarithm used by the geodesic gap bridging of Chapter 4; the two together let the pipeline move between the compact form and the matrix form without ever introducing quaternions."),

(H2, "C.4 Work Example: Frame 100 Detections"),

(P, "Frame 100 of the evaluation recording once more, object marker (id 1), side length L = 50 mm. The four marker-frame corners are (plus or minus 0.025, plus or minus 0.025, 0) m. From the four detected corner pixels, IPPE returns the pose with translation t = (0.0675, -0.1111, 0.9268) m and rotation matrix"),
(P, "R = [ 0.951, -0.060, 0.303 ;  -0.097, -0.989, 0.108 ;  0.293, -0.132, -0.947 ]"),
(P, "with a reprojection error of 0.16 pixels, meaning the recovered pose re-projects the corners onto the image within a sixth of a pixel of where they were detected. Reading the pose: the translation places the marker centre 6.7 cm right of the optical axis, 11.1 cm above it, at 0.93 m depth. The third column of R is the direction of the marker's z-axis (the outward normal of the marked face) expressed in the camera frame: (0.303, 0.108, -0.947), a vector pointing mostly back toward the camera (negative z) and tilted right and slightly down, matching the visible orientation of the cube in Figure C.1."),

(P, "Table C.1 collects the raw marker-branch measurements for all three markers on the same frame. The reprojection errors are far below a pixel, the desk and object poses were decided directly by reprojection error, and the wall pose was resolved by the continuity tracker of Section C.2, as its flag records."),

(TBL, [["marker", "center pixel", "reprojection", "PnP range", "depth median", "difference"],
       ["wall id 0", "(516, 70)", "0.052 px", "3.384 m", "3.374 m", "+9.9 mm"],
       ["desk id 2", "(336, 376)", "0.151 px", "0.579 m", "0.574 m", "+4.6 mm"],
       ["object id 1", "(368, 175)", "0.158 px", "0.927 m", "0.929 m", "-2.2 mm"]]),
(CAP, "Table C.1. Frame 100 detections. The last two columns compare the range inferred by the pose solver against the independent 5 by 5 median of aligned depth at the marker center."),

(P, "The last column is the promised cross-check, and it is worth reading closely because the two numbers come from unrelated physics. The pose solver infers range monocularly, from the apparent size of the marker in the color image and its known printed size; the depth median comes from the stereo depth stream. They agree to within 10 mm at 3.4 m and to within 5 mm nearby, in every case within half a percent of the range. The check also guards a configuration error that would otherwise be invisible: had a marker's physical size been entered wrongly, the solver's range would scale in proportion while the depth reading stayed put, and this column would flag it immediately."),

(P, "Two further checks are available on this single frame. The static markers show the method's precision: the wall marker (id 0) is recovered with 0.05 pixels of reprojection error at 3.4 m distance. Averaged over both full recordings, the mean reprojection errors are 0.20 pixels (wall), 0.42 pixels (desk), and 0.08 pixels (object). And the object pose just recovered, with determinant 1.000000000, is the input that the object tracking of Chapter 4 pushes through the world-anchoring chain."),
]

references = {
3:  'G. Buckingham, "Hand tracking for immersive virtual reality: Opportunities and challenges," Frontiers in Virtual Reality, vol. 2, p. 728461, 2021.',
9:  'L. Keselman, J. Iselin Woodfill, A. Grunnet-Jepsen, and A. Bhowmik, "Intel RealSense stereoscopic depth cameras," in Proc. IEEE Conf. Computer Vision and Pattern Recognition Workshops (CVPRW), 2017.',
12: 'S. Dill et al., "Accuracy evaluation of 3D pose reconstruction algorithms through stereo camera information fusion for physical exercises with MediaPipe Pose," Sensors, vol. 24, no. 23, art. 7772, 2024.',
13: 'Y. Dong, "Tracking and reconstruction of object grasping hand using a RGB-D sensor," M.A.Sc. thesis, Simon Fraser University, 2024.',
26: 'F. Zhang, V. Bazarevsky, A. Vakunov, A. Tkachenka, G. Sung, C.-L. Chang, and M. Grundmann, "MediaPipe Hands: On-device real-time hand tracking," arXiv:2006.10214, 2020.',
27: 'M. Kalaitzakis, B. Cain, S. Carroll, A. Ambrosi, C. Whitehead, and N. Vitzilaios, "Fiducial markers for pose estimation: Overview, applications and experimental comparison," Journal of Intelligent and Robotic Systems, vol. 101, art. 71, 2021.',
28: 'J. L. Pulloquinga, D. Corrata, V. Mata, A. Valera, and M. Valles, "Experimental analysis of pose estimation based on ArUco markers," in Innovations in Industrial Engineering III (Lecture Notes in Mechanical Engineering), Cham: Springer, 2024, pp. 138-149.',
38: 'Z. Zhang, "A flexible new technique for camera calibration," IEEE Transactions on Pattern Analysis and Machine Intelligence, vol. 22, no. 11, pp. 1330-1334, 2000.',
39: 'V. Bazarevsky, I. Grishchenko, K. Raveendran, T. Zhu, F. Zhang, and M. Grundmann, "BlazePose: On-device real-time body pose tracking," arXiv:2006.10204, 2020.',
43: 'T. Collins and A. Bartoli, "Infinitesimal plane-based pose estimation," International Journal of Computer Vision, vol. 109, no. 3, pp. 252-286, 2014.',
46: 'J. Wang and E. Olson, "AprilTag 2: Efficient and robust fiducial detection," in Proc. IEEE/RSJ Int. Conf. Intelligent Robots and Systems (IROS), 2016, pp. 4193-4198.',
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

out = "/home/luo/Desktop/New_SandBox/writing/v3/Appendix.docx"
doc.save(out)
print("saved", out)
