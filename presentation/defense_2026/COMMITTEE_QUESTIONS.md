# Committee questions for rehearsal

Currency note (2026-10-08): The questions and their source review below
are preserved from 2026-09-29. Their PDF, printed-page and supporting-slide
pointers refer to the artifacts reviewed then, before the post-defence V9
revision and adoption of the author's final deck. The old 66-main/39-hidden
numbering and review/qa_revision/ paths are historical; that review folder
was retired under D-385. Use [the final deck guide](README.md) for current
slide navigation and [the V9 README](../../writing/v9/README.md) for the
current compiled thesis. This notice does not re-audit or remap the 134
questions or their citations.

Date: 2026-09-29. Independent source review is complete for all 134 questions.

Use the short answer first. Read the supporting detail when a follow-up needs
it, and keep the stated limits attached to the claim. The Basic questions
are separate from the specialist questions below.

PDF page means the 1-based physical page in the final 168-page
writing/v9/Thesis_V9.pdf. Printed thesis pages are labelled separately where
given. The final compiled PDF and DOCX are authoritative; English exports
are reading aids. Later demonstrations and benchmarks are supplementary
and are explicitly distinguished from final-thesis results.

Start here: [task and scope](#q11), [model degrees of freedom](#q310),
[elbow ambiguity](#q5n1), [evaluation references](#q71),
[conditional recovery](#q94), and [causal feasibility](#q81).
This is a rehearsal route, not a prediction of question likelihood.

Supporting-slide numbers refer to the restored 66-main/39-hidden deck.
The 30-minute spoken route retains the full evidence; technical notes are unspoken.
The audit and complete question index are in review/qa_revision/.

## Basic questions

### QB.1

Question: What does RGB-D mean, and what does each image provide?

Short answer: RGB-D means red, green and blue colour plus depth. The colour image tells the detector where a body landmark appears. The aligned depth image supplies its metric depth. Together with the camera calibration, they give a 3D position.

Supporting detail: RGB records appearance in red, green and blue channels. The D435 estimates depth by stereo triangulation with infrared texture assistance. This pipeline discards MediaPipe's appearance-derived depth and samples the aligned sensor depth at each landmark pixel.

Sources: Sections 2.3, D.1-D.3; printed 14, D1-D3; PDF 28, 145-147.

Limits and evidence: Depth can belong to the cube or desk in front of the body. A metric sample is still an imperfect surface measurement.

Supporting slide: Main slides 9; Hidden slides 84. 9 Landmark acceptance; 84 RGB-D back-projection

### QB.2

Question: What is the difference between tracking and reconstruction here?

Short answer: Tracking extracts body landmarks and object poses from successive images. Reconstruction uses those measurements, the body geometry and the scene calibration to place an avatar and cube in a shared 3 D scene.

Supporting detail: The detector supplies eight body points; the kinematic solve turns them into a root pose and arm angles. Unity composes those rotations on the rig. When observations fail, reconstruction may use constraints or hold earlier values, so rendered motion is not always newly observed motion.

Sources: Abstract; Chapter 3 opening; Section 6.3; printed iii-iv, 21, 74-75; PDF 3-4, 35, 88-89.

Limits and evidence: A convincing replay does not establish anatomical accuracy.

Supporting slide: Main slides 17, 42. 17 Torso frame; 42 Rig application

### QB.3

Question: How do position, orientation and six degrees of freedom differ?

Short answer: Position says where a point is. Orientation says how a frame is turned. A rigid object's pose contains three translation coordinates and three rotational degrees of freedom; a wrist landmark alone supplies only position.

Supporting detail: A marker supplies four known corners, allowing the solver to estimate its frame's rotation and translation. Body landmarks are points without attached orientations. The model derives segment frames from their geometry, but this does not make every anatomical rotation observable.

Sources: Chapter 3 opening; Sections 2.2.1, E.2; printed 21, 11-12, E3-E4; PDF 35, 25-26, 151-152.

Limits and evidence: Six degrees of freedom do not mean six independent reliable measurements; a planar marker can admit two competing poses.

Supporting slide: Main slides 15, 21. 15 Camera and Camera-prime; 21 Object pose

### QB.4

Question: What are camera, world and local frames?

Short answer: A frame is an origin and three axes used to describe coordinates. The camera frame starts at the colour camera. The world frame is fixed to the desk marker. A local frame moves with a body segment or the object.

Supporting detail: The raw camera has x right, y down and z forward. Camera-prime flips y and shares the optical origin. The Unity convention retains the desk origin; gravity alignment and floor placement produce Scene. Body-segment frames describe rotations along the arm chain.

Sources: Section 2.2.1 and 3.1; printed 10-12, 21-22; PDF 24-26, 35-36.

Limits and evidence: Changing coordinates does not change the physical motion. Axis flips and swaps reverse handedness and must not be treated as proper rotations.

Supporting slide: Main slides 15, 21, 41. 15 Camera and Camera-prime; 21 Object pose; 41 Mapping into Scene

### QB.5

Question: How is calibration different from filtering?

Short answer: Calibration establishes the camera geometry, scene frames and body lengths used to interpret measurements. Filtering reduces spikes and rapid variation in the measurements over time. Smoother data can still have calibration bias.

Supporting detail: Factory intrinsics map pixels and depth into camera coordinates. The first ten static-marker detections establish frozen scene anchors. Temporal filtering then despikes, bridges short interior gaps and smooths valid runs. The frozen anchor avoids repeated anchor wobble but can preserve an initial bias.

Sources: Sections 2.2.2, D.1, F; printed 13-14, D1-D2, F1-F3; PDF 27-28, 145-146, 156-158.

Limits and evidence: Filtering does not prove or repair an incorrect metric scale or gravity reference.

Supporting slide: Main slides 10-12; Hidden slides 96-98. Use the stated comparison references and conditions. Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### QB.6

Question: What are forward and inverse kinematics in this project?

Short answer: Forward kinematics reconstructs the arm from joint rotations and link geometry. Inverse kinematics finds a compatible configuration from observed endpoints. The shoulder and wrist leave a circle of possible elbows only when their separation is strictly between the folded and fully extended limits.

Supporting detail: With link lengths L1 and L2 and shoulder-to-wrist distance r, a nondegenerate circle requires abs(L1-L2) < r < L1+L2. For separated endpoints at either boundary, the spheres touch at one point. Outside reach they have no exact intersection; coincident endpoints are another degenerate case. For a circle, direction memory selects a point before the rotations are composed for display.

Sources: Sections 5.5, 6.3, H.1; printed 58-59, 74-75, H1; PDF 72-73, 88-89, 162; equation (5.8), PDF 73; v1/kinematics/occlusion_ext.py:334-374.

Limits and evidence: The endpoints and remembered direction do not generally determine the true hidden elbow. Not every reachable configuration yields a circle.

Supporting slide: Main slides 29, 31; Hidden slides 73, 78. 29 Two segment-length constraints; 31 Deriving the elbow circle; 73 Two-link reconstruction; 78 Solver verification

### QB.7

Question: What do measured, held and constrained outputs mean?

Short answer: Measured means the solve uses accepted current observations. Held means the required geometry is unavailable and the joint group keeps its last solved value. Constrained means the solve uses a repaired point or recovery constraint.

Supporting detail: These states describe the evidence behind an output, rather than its accuracy. Hip or shoulder preparation can make the root constrained as well as the arms. A successfully solved group consuming a repaired point loses its live bit; a group that cannot be solved is held.

Sources: Abstract; Appendix G.4; printed iii-iv, G3; PDF 3-4, 161.

Limits and evidence: Measured does not mean independently validated. Smooth held or constrained output can be wrong.

Supporting slide: Main slides 18-19, 23. 18 Shoulder swing; 19 Shoulder twist; 23 Output states

### QB.8

Question: What is ground truth, and what references do your errors use?

Short answer: Ground truth is an independently known reference for the quantity being estimated. Here the exact injected synthetic trajectories are known by construction. The recording comparisons use more limited references: tape lengths, accepted raw landmarks, manual wrist labels and the unmasked reconstruction. Each supports a different claim.

Supporting detail: Tape lengths test endpoint separation, not the complete path in world coordinates. Raw landmark comparisons test agreement with the sensor input. Synthetic removal compares recovery with the valid unmasked model, and natural occlusion compares with manual wrist labels. None is independent full-body anatomical ground truth.

Sources: Section 7.1; Appendix H.1, H.3; printed 85, H1-H2; PDF 99, 162-163.

Limits and evidence: The physical route was not registered into the world frame, so point-to-path error is unavailable.

Supporting slide: Hidden slides 68. 68 Evaluation references

### QB.9

Question: How are accuracy and precision different?

Short answer: Accuracy concerns agreement with the true quantity; precision concerns agreement between repeated measurements under stated conditions. A stable estimate can be consistently biased. I report errors against each named reference rather than calling small scatter proof of accuracy.

Supporting detail: The thesis uses physical length errors and positional differences against stated references. Marker corners repeatedly landing on whole pixels can look stable because of quantization. The metrology definition also treats accuracy as a concept, not a numerical quantity with its own unit.

Sources: Section 7.1, E.1; printed 85, E2; PDF 99, 150; [JCGM VIM accuracy](https://jcgm.bipm.org/vim/en/2.13.html), [precision](https://jcgm.bipm.org/vim/en/2.15.html), read 2026-09-29.

Limits and evidence: Trajectory scatter along a moving task is not automatically a repeatability experiment.

Supporting slide: Main slides 8, 21. 8 Calibration; 21 Object pose

### QB.10

Question: How do throughput and latency differ in your real-time claim?

Short answer: Throughput is how many frames the system processes per second. Latency is how long an individual frame takes to reach the displayed result. Replay kept up at about 29 frames per second, but sensor-to-screen latency was not measured.

Supporting detail: The thesis separates the configured two-frame buffering delay, motion-dependent filter lag and the five-frame alignment of two angle series. The branch processing times fit the frame budget on the stated workstation. Those facts do not measure or bound the complete sensor-to-screen delay.

Sources: Sections 8.4-8.5; printed 114-115; PDF 128-129.

Limits and evidence: The later transport-package benchmark is a separate presentation experiment, not a thesis end-to-end latency measurement.

Supporting slide: Main slides 36; Hidden slides 94-95. 36 One capture, two readers; 94 Transport candidates; 95 Moving one frame package from Python to Unity Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### QB.11

Question: What does bimanual mean, and what task did you actually evaluate?

Short answer: Bimanual means involving both hands. The system reconstructs both arms and a marked object in one scene. The evaluation includes a single-hand rail task, a handover and a loop recording with natural occlusion.

Supporting detail: The rail task supplies worked examples and physical segment comparisons. The handover tests the object and two arms during transfer. The loop supplies natural landmark failures. These are desk tasks with one subject, a fixed sensor and a marked cube.

Sources: Chapter 1 opening; Section 7.1; Abstract; printed 1, 85, iii-iv; PDF 15, 99, 3-4.

Limits and evidence: This sample does not establish performance for general two-handed manipulation or a wider participant population.

Supporting slide: Main slides 3-4. 3 Motivation; 4 Task and observations

### QB.12

Question: Why use one camera, and what can it never directly see?

Short answer: One RGB-D camera gives colour and metric depth without a camera array or sensors attached to the subject. It still has one viewpoint. A wrist hidden behind the object has no direct visible-surface depth observation.

Supporting detail: The detector can predict a landmark even when it is hidden. Alignment puts colour and depth on a shared ray, but the returned depth belongs to the visible surface. The recovery layer therefore uses remembered geometry and object constraints when observations fail.

Sources: Abstract; Appendix C.2, D.2, G.4; printed iii-iv, C3, D2-D3, G3; PDF 3-4, 143, 146-147, 161.

Limits and evidence: Recovery cannot turn an occluded point into an independently measured point.

Supporting slide: Hidden slides 84. 84 RGB-D back-projection

### QB.13

Question: Why combine body landmarks with object markers?

Short answer: The landmarks locate the person. The markers establish a fixed scene frame and measure the object pose. If the hand is holding the cube and its wrist measurement fails, the object pose supplies another geometric constraint.

Supporting detail: The held hand uses a learned hand-to-object offset, carried by the current object pose; the arm still depends on calibrated lengths and direction memory. Desk and object markers are printed 45 mm squares. The pinned detector-size correction places all thesis translations on that settled 45 mm scale.

Sources: Abstract; Section 5.4; Appendix E.4; printed iii-iv, 58, E5-E6; PDF 3-4, 72, 153-154; AGENTS.md marker-size chain.

Limits and evidence: The object marker can itself be occluded, and a grip offset can be wrong. This is additional sensing information, not independent wrist ground truth.

Supporting slide: Hidden slides 92-93. 92 ArUco vs AprilTag: what the literature reports; 93 AprilTag 3 faster; corner errors converge at 96 px Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### QB.14

Question: Why can you locate the wrist without knowing its full orientation?

Short answer: A wrist landmark is one point. It does not show how the hand rotates around the forearm. The model can reconstruct an arm ending at that point without claiming a measured wrist orientation.

Supporting detail: Segment geometry gives the directions between landmarks and supports the solved arm angles. Rotating the hand around an unchanged wrist point does not change those point coordinates. The thesis explicitly treats the wrist as a tracked point.

Sources: Abstract; Chapter 3 opening and Section 3.4.4; printed iii, 21, 35; PDF 3, 35, 49.

Limits and evidence: The avatar hand's displayed orientation should not be interpreted as a separately validated hand-pose estimate.

Supporting slide: Main slides 19. 19 Shoulder twist

### QB.15

Question: How do offline and causal processing differ?

Short answer: Offline processing can read later frames. Causal processing uses only samples already received. Forward-backward filtering and interior-gap interpolation use future observations, so the real-time structure needs different operations.

Supporting detail: A trailing despiker and One Euro filter replace the centred offline stages. The merger can interpolate between samples already in its buffer by displaying an older time. A replay using this causal structure is different from retrospective offline smoothing.

Sources: Appendix F; Sections 8.1-8.2, 8.4-8.5; printed F1-F3, 107-110, 114-115; PDF 156-158, 121-124, 128-129.

Limits and evidence: Causality does not mean zero lag. A complete live-camera session was not validated.

Supporting slide: Main slides 57; Hidden slides 101, 103. 57 One Euro adaptive smoothing; 101 One Euro filtering; 103 Why One Euro in real time Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### QB.16

Question: What does digital-twin playback mean here, and is this ready for clinical use?

Short answer: Here it means replaying the reconstructed person and object in a metric virtual scene. Clinical assessment, imitation learning and avatar animation motivate the work. I did not validate a clinical tool or a general live capture product.

Supporting detail: The abstract reports desk-task reconstruction, limited physical checks and causal replay feasibility. Object assistance helped one natural occlusion interval but not another. The result is a systems demonstration with named sensing and evaluation limits.

Sources: Abstract; Section 8.5; printed iii-iv, 114-115; PDF 3-4, 128-129.

Limits and evidence: No clinical participants, diagnostic performance or full live-camera validation is established by this thesis.

Supporting slide: Main slides 64-65. 64 Limitations; 65 Contributions

## Research rationale

### Q1.1

Question: What exactly does the thesis establish about bimanual handling?

Short answer: I reconstruct both arms and a marked object in one scene. I evaluate controlled rail and handover tasks and selected failures from a two-hand loop. I do not establish accuracy for general bimanual manipulation.

Supporting detail: The capability of the pipeline and the breadth of its validation are different claims. The rail task is one-handed; the handover adds the second arm; the loop supplies secondary two-hand and failure evidence. None is a broad task or population benchmark.

Sources: V9 Chapter 1 opening and Section 1.3, PDF pages 15, 19-20; Section 2.1, PDF page 21.

Limits and evidence: V9 statement; limited external validity.

Supporting slide: Main slides 5. 5 Research question

### Q1.4

Question: Why combine MediaPipe image landmarks with sensor depth rather than use a depth body tracker?

Short answer: MediaPipe supplies a fixed set of image landmarks, and the RealSense supplies metric depth at those locations. That is the measurement architecture I used; I did not compare alternative body detectors.

Supporting detail: The system selects the shoulders, elbows, wrists and hips from 33 Pose landmarks, discards the appearance-derived depth and deprojects using registered sensor depth. This gives metric points but preserves errors in the image location and in the sampled surface. Avoid claiming detector superiority from this design choice.

Sources: V9 Sections 1.2.1 and 2.3, PDF pages 16, 28-29; Figure 2.6, PDF page 29.

Limits and evidence: V9 statement; no detector comparison.

Supporting slide: Main slides 8-9. 8 Calibration; 9 Landmark acceptance

### Q1.5

Question: How does a marked cube limit the applications motivating this work?

Short answer: Nothing is attached to the person, but the object and scene need visible markers. The thesis therefore evaluates marked-object reconstruction in a calibrated setup.

Supporting detail: A marker supplies identity and a pose from its known square geometry. Hiding the marker removes that measurement. A replacement tracker could supply the same pose interface, but compatibility at an interface does not prove the replacement would achieve the same accuracy or recovery behavior.

Sources: V9 Table 1.1, PDF page 18; Table 2.1, PDF page 22; Section 4.2, PDF pages 56-58.

Limits and evidence: V9 statement; marker requirement.

Supporting slide: Main slides 64; Hidden slides 92. 64 Limitations; 92 ArUco vs AprilTag: what the literature reports Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q1.6

Question: Why mention transistor scaling in this tracking thesis?

Short answer: It frames the systems question of what the algorithms and pipeline can do on existing hardware. It is not a premise of the kinematic derivation.

Supporting detail: The relevant evidence is the actual reconstruction and causal feasibility work, rather than the broad hardware motivation. The thesis does not derive any tracking requirement from transistor scaling.

Sources: V9 Section 1.1, PDF page 15; Chapter 8, causal feasibility discussion.

Limits and evidence: V9 framing statement.

Supporting slide: Main slides 55-58. 55 Real-time pipeline; 56 Causal processing; 57 One Euro adaptive smoothing; 58 Replay timing

### Q1.7

Question: How strong is the literature gap claim?

Short answer: It is scoped to the work reviewed in the thesis. The combination I investigate is upper-body and object reconstruction in one metric frame, with an explicit account of failures and object-assisted recovery.

Supporting detail: Table 1.1 summarizes nine approach families. It is not an exhaustive proof that no other system exists. A hand-object or interacting-hand method should be compared on tracked anatomy, metric sensing, shared coordinates, recovery and validation, rather than excluded by its title.

Sources: V9 Section 1.2.4 and Table 1.1, PDF pages 18-19.

Limits and evidence: V9 statement; bounded literature review.

Supporting slide: Main slides 65. 65 Contributions

### QA.10

Question: Why is one short single-hand take the detailed worked example?

Short answer: The primary rail take is one continuous recording of 29.99 seconds with 900 colour and 900 depth frames. The thesis also evaluates a handover and natural-occlusion loop. It does not give a tested rationale for choosing this duration or the single-hand task as primary.

Supporting detail: Appendix A preserves approach, manipulation and retreat. Reusing frame 533 across the appendices makes the measurement steps traceable. Chapter 7 states which recording and reference support each comparison, rather than treating the primary take as all the experimental evidence.

Sources: Appendix A.1-A.3, Table A.1; Section 7.1; printed A1-A3, 85; PDF 137-139, 99.

Limits and evidence: Short duration does not establish static-marker validity or manual-reference accuracy. Generalization beyond these desk tasks remains limited.

Supporting slide: Hidden slides 68. 68 Evaluation references

## Sensing and calibration

### Q2.1

Question: How is the printed marker size carried consistently into the measurements?

Short answer: The small printed markers are 45 mm. The frozen extractor declares 50 mm, so the pinned evaluation multiplies their translations by 0.9 before calibration. The thesis measurements use the corrected 45 mm scale.

Supporting detail: Marker size scales PnP translation linearly. The wall marker remains 150 mm. The correction leaves rotation, image corners and reprojection error unchanged. The user's confirmed print size is settled; an old code comment calling it an assumption does not reopen that decision. Do not promise a post-print precision measurement that is not recorded.

Sources: V9 Table 2.1, PDF page 22; AGENTS.md Standing project constraints; v1/aruco/frames.py MARKERS; eval/common/marker_size.py SCALE; eval/gt/scale_correction.py translation rescale.

Limits and evidence: Implementation verified; settled physical size; metrology precision not established here.

Supporting slide: Main slides 8-9. 8 Calibration; 9 Landmark acceptance

### Q2.2

Question: How is the gravity direction established, and how well is its error bounded?

Short answer: I use the printed up direction of the wall marker, assuming the wall is plumb and the marker is mounted upright. Its mounting angle was not measured, so I cannot give a verified angular error bound.

Supporting detail: A plumb wall fixes the plane normal but permits rotation within the plane. A plane fitted around the desk card helps settle direction and planar ambiguity; it is not an independent calibrated gravity reference. The wall marker's weak planar geometry is a separate source of pose uncertainty, not a measured mounting error.

Sources: V9 Section 2.2.2, PDF pages 27-28; Appendix E.2, PDF page 151.

Limits and evidence: V9 assumption; unmeasured gravity uncertainty.

Supporting slide: Main slides 8-9. 8 Calibration; 9 Landmark acceptance

### Q2.3

Question: Why average ten initial detections and then freeze the anchors?

Short answer: Averaging reduces initial noise, and freezing prevents later marker jitter from moving the whole scene. Ten detections is the design window used here; I do not have a sensitivity study that establishes it as optimal.

Supporting detail: Translation uses a mean. Rotation uses an element-wise mean followed by SVD projection onto a proper rotation. Small changes at printed precision are not a statistical spread estimate. Freezing also freezes initial bias, and movement of the camera or anchors afterwards invalidates the calibration.

Sources: V9 Section 2.2.2 and Equation (2.1), PDF page 27; Section 4.3, PDF page 59.

Limits and evidence: V9 method; unmeasured window sensitivity.

Supporting slide: Main slides 8-9, 21. 8 Calibration; 9 Landmark acceptance; 21 Object pose

### Q2.4

Question: What does the 0.50 landmark visibility gate actually protect against?

Short answer: It rejects detections that MediaPipe itself marks as poorly visible. It cannot certify that a visible landmark is on the correct body point or that its sampled depth belongs to the body.

Supporting detail: Wrong surface depth and confident mislocalization are silent failures. The geometry detectors look for implausible lengths, torso geometry and steps afterwards. The thesis reports no visibility-threshold sweep or calibrated false-positive/false-negative rate.

Sources: V9 Section 2.3, PDF page 28; Section 5.2, PDF pages 64-66; Chapter 9 and Figure 9.2, PDF page 132.

Limits and evidence: V9 statement; heuristic confidence gate.

Supporting slide: Main slides 8-9. 8 Calibration; 9 Landmark acceptance

### Q2.5

Question: How can a 2.9 cm spike be rejected with a 2 cm Hampel floor?

Short answer: The 2 cm floor is on the rejection threshold. The test rejects a residual above the larger of 2 cm and three times the robust scale, so a 2.9 cm residual can be rejected.

Supporting detail: Code computes threshold=max(abs_floor, k*1.4826*MAD), with k=3 and abs_floor=0.02 m. MAD is a centred rolling median of each sample's residual from its own centred rolling median, rather than all deviations from one common window median. The rejected point becomes missing before gap interpolation.

Sources: V9 Section 2.5 and Figure 2.7, PDF pages 30-31; v1/mediapipe/filter_landmarks.py hampel_mask.

Limits and evidence: Implementation verified.

Supporting slide: Hidden slides 96. 96 Hampel spike removal Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q2.6

Question: What justifies fourth-order Butterworth smoothing at 3 Hz, and what does the double pass cost?

Short answer: It is the offline design used to reduce jitter in this slow task. Forward and backward filtering cancels phase delay but increases attenuation near the cutoff. The thesis does not establish the cutoff from a measured motion spectrum.

Supporting detail: The magnitude gains multiply; this is not lossless smoothing. A later defence comparison on the R6b right wrist measures the shake/deviation trade-off among candidates. It is supplementary evidence, not a result originally reported by V9, and deviation from a measured trace is not error against independent truth.

Sources: V9 Section 2.5, PDF page 32; v1/mediapipe/filter_landmarks.py butter branch; presentation/defense_2026/experiments/filter_metrics/summary.csv and README.md.

Limits and evidence: V9 design choice; later defence supplement; no measured spectral cutoff justification.

Supporting slide: Hidden slides 98, 102. 98 Butterworth smoothing; 102 Why Butterworth offline Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q2.7

Question: Why bridge five landmark frames but eight object frames?

Short answer: Those are different design limits in the two branches. I can explain their behavior, but the thesis does not demonstrate that five and eight are optimal or establish a tested reason for their difference.

Supporting detail: Landmark interpolation fills short interior gaps before recovery. Object interpolation also bridges rotation along the shortest turn. Crucially, object detection provenance stays false on an unseen marker row, and cleaning subsequently blanks it, so an interpolated pose is not admitted as a measured recovery constraint.

Sources: V9 Section 2.5, PDF page 31; Section 4.2, PDF pages 56-58; v1/aruco/filter_object_track.py max_gap and detection-flag handling; eval/common/clean_object_track.py.

Limits and evidence: Implementation verified; parameter rationale unmeasured.

Supporting slide: Main slides 21; Hidden slides 97. 21 Object pose; 97 Short-gap interpolation Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q2.9

Question: Why use a 640 by 480 recording profile when corner resolution limits the distant wall marker?

Short answer: That is the recorded profile evaluated in the thesis. The wall marker is larger because it is farther away, but the thesis does not compare alternative recording resolutions or prove this profile is optimal.

Supporting detail: The small projected wall square makes its pose poorly conditioned. A higher-resolution profile would need a new calibration and a measured detector/processing comparison. Do not claim that alignment requires this resolution or that the full live pipeline was validated at capture time.

Sources: V9 Section 2.1, PDF page 22; Appendix A.1 recording profile; Appendix E.2, PDF page 151.

Limits and evidence: V9 recording condition; no profile comparison.

Supporting slide: Hidden slides 92-93. 92 ArUco vs AprilTag: what the literature reports; 93 AprilTag 3 faster; corner errors converge at 96 px Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q2.10

Question: Does matching frame indices establish simultaneous colour and depth exposure?

Short answer: No. It associates the two branches with the same recorded frame set. The thesis does not measure the colour-to-depth exposure offset or its effect on reconstruction.

Supporting detail: Alignment places depth on the colour image grid; it is not a latency measurement. Metadata could support an audit, but no timestamp audit or measured within-frame displacement bound is established here.

Sources: V9 Section 2.1, PDF page 23; Appendix A recording and metadata descriptions.

Limits and evidence: V9 frame association; unmeasured sensor synchronization error.

Supporting slide: Hidden slides 95. 95 Moving one frame package from Python to Unity Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q4.1

Question: What are the object-cleaning rate bounds, and how were they chosen?

Short answer: The implementation uses 1.0 m/s and 400 degrees/s. They are fixed guards derived from clean data, rather than parameter-free physical laws or values independently validated for every task.

Supporting detail: clean_object_track.py records clean maxima from R1 and R5 of 0.26/0.41 m/s and 82/179 degrees/s. It compares each candidate with the last kept sample using actual elapsed time. The code states the bounds and identifies two recordings as their provenance.

Sources: V9 Section 4.2 and final Equation (4.2), PDF page 58; eval/common/clean_object_track.py constants and provenance comments.

Limits and evidence: Implementation verified; recorded derivation comments, not a newly rerun maxima study.

Supporting slide: Main slides 21. 21 Object pose

### Q4.2

Question: How do eleven bridged rows coexist with 899 detections in 900 frames?

Short answer: Ten detected poses were removed by despiking, and one frame had no detection. The filter bridges all eleven, while preserving the original detection flag.

Supporting detail: The final thesis already says this explicitly in Figure 4.2 and the following paragraph. The pinned R6b filter metadata confirms 900 frames, 899 detected, ten despiked and eleven bridged. Cleaning subsequently blanks the unseen row; interpolated values are not proof of a measurement on that frame.

Sources: V9 Figure 4.2 and Section 4.2, PDF page 57; eval/output/recording_20260831_065553_scaled_object_world_filtered.meta.json; v1/aruco/filter_object_track.py.

Limits and evidence: V9 statement and pinned metadata.

Supporting slide: Hidden slides 97. 97 Short-gap interpolation Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q4.3

Question: Was camera-placement invariance experimentally tested?

Short answer: It follows from the transformation chain when both poses share the same camera placement and the scene is recalibrated. V9 does not report a moved-camera experiment.

Supporting detail: World-to-camera inverse times object-to-camera gives object-to-world. A frozen anchor permits a different placement before calibration, but camera movement afterwards breaks the assumption. Algebraic cancellation does not eliminate pose-estimation or calibration error.

Sources: V9 Equation (4.1), PDF page 55; Section 4.1, PDF page 56.

Limits and evidence: Verified mathematical property; unmeasured placement robustness.

Supporting slide: Main slides 21. 21 Object pose

### Q4.4

Question: How should the marker-pose and stereo-depth disagreement in Table E.1 be interpreted?

Short answer: They are different measurement chains, and their disagreement does not identify its cause. The small markers were printed at 45 mm, and their translations were corrected by 0.9 before calibration. I would not diagnose a printing error from these three samples.

Supporting detail: Range is the norm of the translation, whereas depth is optical-axis z; only translation z is directly comparable to the centre depth sample. Table E.1 gives small-marker z values of about 1.02/0.55 m versus depth samples of 0.99/0.53 m, and wall z of 3.05 m versus 3.19 m. Neither chain is declared independent ground truth here, and the disagreement does not explain the height discrepancy by itself.

Sources: V9 Table E.1, PDF page 154; Section 4.3, PDF pages 59-60; eval/common/marker_size.py; eval/gt/scale_correction.py; AGENTS.md settled marker constraint.

Limits and evidence: V9 measurements; cause unestablished; scale correction implementation verified.

Supporting slide: Main slides 21. 21 Object pose

### Q4.5

Question: What causes the 6.3 versus 7.3 cm height discrepancy?

Short answer: The thesis does not isolate a cause. It compares a reconstructed marker-centre height with a tape-derived cube-centre height, with calibration and measurement uncertainty also present.

Supporting detail: The comparison substitutes one physical point for another at the stated mounting and orientation. Gravity uses an unmeasured wall mounting, and the tabletop comes from calibrated scene geometry. Marker pose, stereo surface sampling and tape references have different uncertainties. Listing these possibilities does not rank them or prove any produces the observed discrepancy.

Sources: V9 Section 4.3, PDF page 60; Section 2.2.2, PDF pages 27-28.

Limits and evidence: V9 discrepancy; root cause and uncertainty budget unestablished.

Supporting slide: Main slides 21. 21 Object pose

### Q4.6

Question: Why use different position smoothers for body landmarks and the object?

Short answer: That is the implemented design: Butterworth for offline landmarks and Savitzky-Golay for object position, with a separate chordal mean for object rotation. V9 does not give a comparative object-track experiment establishing that choice.

Supporting detail: Savitzky-Golay fits a local polynomial, while Butterworth attenuates frequencies. Their general properties can explain the options but do not establish why one is best on this object's motion. The later filter benchmark uses a wrist trace, so it cannot validate the object-branch choice.

Sources: V9 Section 2.5, PDF page 32; Section 4.2, PDF page 56; v1/aruco/filter_object_track.py defaults and smoothing branches.

Limits and evidence: Implementation verified; object-specific choice untested.

Supporting slide: Hidden slides 98-99, 102. 98 Butterworth smoothing; 99 Savitzky-Golay filtering; 102 Why Butterworth offline Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q4.7

Question: How long is the object rotation smoothing window, and what does it do at transitions?

Short answer: The pinned filter uses a centred five-frame chordal mean for rotation, and a nine-frame quadratic Savitzky-Golay position window. The thesis has no independent orientation reference for measuring transition error.

Supporting detail: Chordal smoothing averages rotation matrices and projects the result back to a proper rotation. Its centred window reads future samples offline. Smooth output alone cannot establish correct orientation, especially beside missing-marker or held intervals.

Sources: V9 Section 4.2, PDF page 56; Equation (2.1), PDF page 27; v1/aruco/filter_object_track.py rot_window; pinned R6b filtered metadata.

Limits and evidence: Implementation and pinned settings verified; orientation accuracy unmeasured.

Supporting slide: Main slides 21. 21 Object pose

### Q4.9

Question: Why tilt the desk card and use another marker for gravity?

Short answer: The setup has a tilted desk card, so its normal cannot define vertical. The wall marker supplies the gravity reference under an upright-mounting assumption. The thesis does not report a tested reason for choosing this mounting.

Supporting detail: It is reasonable to consider visibility and corner conditioning when designing a setup, but the thesis does not compare tilted and flat cards. Do not turn that possible explanation into an established historical design decision. The measured card-to-gravity angle is about 32 degrees in the worked example.

Sources: V9 Section 2.2.2, PDF pages 27-28; Section 4.3, PDF page 59; Figures 2.1-2.2, PDF pages 21, 23.

Limits and evidence: V9 geometry; mounting rationale unverified.

Supporting slide: Main slides 8-9. 8 Calibration; 9 Landmark acceptance

### Q4.10

Question: Can the rate guard reject genuine fast motion or lock out a returning marker?

Short answer: It can reject motion above its design rates. Because the allowance grows with elapsed time from the last accepted pose, it does not impose one fixed maximum displacement across an occlusion. That still is not a guarantee of correct reacquisition.

Supporting detail: The first finite detected pose is accepted. Later candidates must satisfy both linear and angular rate limits; a rejected candidate does not reset the reference. With a fixed previous point and continuing time, a stationary displaced candidate can eventually fall within the allowance. Arbitrary fast motion or bad timestamps are outside that guarantee.

Sources: V9 Section 4.2 and Equation (4.2), PDF page 58; eval/common/clean_object_track.py main loop.

Limits and evidence: Implementation verified; fast-task behavior not validated.

Supporting slide: Main slides 21. 21 Object pose

### Q6.10

Question: What does the desk-marker versus depth disagreement establish about calibration?

Short answer: It shows that the marker-pose and depth-derived geometry do not coincide exactly in that example. The thesis describes the discrepancy as compatible with marker-pose error, but does not separate the contributions. It does not establish a printed-marker-size mistake or a unique calibration cause.

Supporting detail: The calibrated card centre is 0.4 cm below the model tabletop, while nearby depth places it above the desk. The worked cube example has a 3.8 cm pose-depth difference. These compare different measurement chains and have no independently established truth for assigning the error. Drawing the card above the slab prevents visual intersection; it does not correct the measurement. The settled 45 mm scale chain is unchanged.

Sources: Thesis Section 6.4, p. 79 (PDF 93), and Section 6.5, pp. 82-83 (PDF 96-97); AGENTS.md standing marker-size constraint.

Limits and evidence: Observed discrepancy and bounded interpretation. Root cause remains unisolated.

Supporting slide: Hidden slides 92. 92 ArUco vs AprilTag: what the literature reports Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### QA.1

Question: Why reject any missing desk-marker frame if the anchor is frozen after ten detections?

Short answer: Appendix A states that rejection policy, while Section 2.2.2 freezes the anchor. The thesis does not explain why later losses still reject a recording. I can identify the stricter policy without claiming a historical reason or an audited exemption.

Supporting detail: The calibrated desk frame is held constant, so later detections do not update the anchor. The inventory rule is an acceptance condition, separate from the frozen transformation. Relaxing it would be a new processing-policy decision needing an explicit audit.

Sources: Appendix A.3; Section 2.2.2; printed A3, 13; PDF 139, 27.

Limits and evidence: No evidence here establishes that none of the three recordings triggered the rule or why it was introduced.

Supporting slide: Hidden slides 68. 68 Evaluation references

### QA.2

Question: How often does the 5 by 5 depth median select the wrong surface, and why use it?

Short answer: The thesis does not report that rate. The nonzero median handles missing returns and isolated speckle, but it cannot reliably separate a hidden wrist from the cube in front. The geometric failure checks address the resulting inconsistency.

Supporting detail: The normalized landmark coordinate is truncated to a pixel. The aligned depth window then contains whatever surfaces are visible there. A low-visibility landmark or an empty valid-depth window becomes missing; a plausible but wrong depth can survive extraction.

Sources: Appendix C.2, D.2-D.3; printed C1, C3, D2-D4; PDF 141, 143, 146-148.

Limits and evidence: No smaller-window or surface-aware sampling comparison was evaluated here.

Supporting slide: Hidden slides 84. 84 RGB-D back-projection

### QA.3

Question: Did you independently check factory intrinsics and the recorded zero distortion coefficients?

Short answer: No independent checkerboard calibration is reported. I used the factory colour intrinsics stored in the recording. The zero coefficients are recorded stream values; I cannot use them alone to claim the physical lens has no distortion.

Supporting detail: Table D.1 gives fx 607.56, fy 607.02, cx 323.94, cy 248.02 pixels and inverse Brown-Conrady with zero coefficients. For these values the deprojection reduces to the printed pinhole form. That documents the model used, not its independently measured residual error.

Sources: Appendix D.1, Table D.1; printed D1-D2; PDF 145-146.

Limits and evidence: The thesis does not establish why the recorded distortion coefficients are zero.

Supporting slide: Hidden slides 84. 84 RGB-D back-projection

### QA.4

Question: What supports the planar-ambiguity thresholds, and what if the initial lobe is wrong?

Short answer: The thesis describes a heuristic policy rather than a tuned guarantee. It uses gravity agreement to seed the ambiguous pose, then a temporal reference. An incorrect seed could bias the reference; I have no independently graded initial-lobe failure rate to report.

Supporting detail: The policy uses 40 degrees lobe separation, a 30 degree reference-update gate, an approximately 10 degree gravity seed tolerance and reseeding after five distant frames. The worked wall detection has normals 36.4 degrees apart but a maximum corner gap of only 0.22 pixels. Angular separation alone does not establish image distinguishability.

Sources: Appendix E.2 and Figure E.2; printed E3-E5; PDF 151-153.

Limits and evidence: A per-frame resolution flag records the chosen method; it does not independently establish the correct lobe.

Supporting slide: Main slides 21. 21 Object pose

### QA.5

Question: Why not use recorded marker-centre stereo depth to validate marker translation scale?

Short answer: The depth was recorded but no thesis analysis uses it. It could support a consistency comparison, but that comparison was not completed. The table's range and depth columns cannot be directly subtracted because they describe different quantities.

Supporting detail: Marker translation comes from corners and printed size; the depth sample comes from stereo. Radial range is the length of the translation vector, whereas depth is its optical-axis coordinate. A comparison would use marker z and sampled depth with matched points and account for both measurements' errors.

Sources: Appendix E.1, E.4, Table E.1; printed E2-E3, E5-E7; PDF 150-151, 153-155.

Limits and evidence: The purpose for retaining unused depth is not documented. All thesis translations use the settled 45 mm scale.

Supporting slide: Main slides 21. 21 Object pose

### QA.6

Question: Does Appendix F prove the chosen filter is best on recorded motion, and were parameters optimized?

Short answer: No. Its comparison uses a constructed signal to explain filter behaviour. The parameters are the recorded run settings, with no reported sweep. Butterworth supports the offline choice; One Euro supplies a causal alternative with lag.

Supporting detail: The appendix uses fourth-order Butterworth at 3 Hz, Savitzky-Golay order 2/window 9, median window 9 and One Euro minimum 0.05 Hz/coefficient 1.0. Two Butterworth passes cancel phase delay while multiplying amplitude attenuation. Chapter 8 separately compares offline and causal outputs on the recording.

Sources: Appendix F, Figure F.1, Table F.1; printed F1-F3; PDF 156-158.

Limits and evidence: Neither the synthetic illustration nor later presentation filter experiments establish a universal optimum; do not silently transfer these settings to every later demo.

Supporting slide: Hidden slides 96-103. Use the stated comparison references and conditions. Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### QA.11

Question: Does a high MediaPipe visibility score guarantee an anatomically correct landmark?

Short answer: No. It is a detector score, not an independent correctness measurement. The extractor rejects scores below 0.50, but a score above that gate can still accompany the wrong pixel or depth surface.

Supporting detail: The heavy BlazePose model runs in video mode for one person. Detection, presence and tracking thresholds are 0.30; the per-landmark visibility gate is 0.50. These controls have different roles. The detector can output coordinates for hidden points, and later geometry checks can reject implausible results.

Sources: Appendix C.1-C.3; printed C1-C4; PDF 141-144.

Limits and evidence: No score-calibration study or false-acceptance probability is supplied.

Supporting slide: Main slides 9. 9 Landmark acceptance

### QA.12

Question: Is sensor depth radial distance, and does reprojection prove measurement accuracy?

Short answer: Depth is the optical-axis z coordinate, not the distance from the camera centre. Deprojection uses that depth to scale a pixel ray. Reprojecting the result checks that the two formulas agree; it does not prove that the depth or pixel is correct.

Supporting detail: Equation D.2 gives x=z(u-cx)/fx and y=z(v-cy)/fy. Radial distance is sqrt(x*x+y*y+z*z). The frame 533 object-centre example uses 0.99 m depth to obtain approximately (-0.20, 0.15, 0.99) m. The forward calculation returns the starting pixel.

Sources: Appendix D.3-D.4, E.4; printed D3-D4, E6; PDF 147-148, 154.

Limits and evidence: A mathematically consistent projection can use biased calibration or the wrong visible surface.

Supporting slide: Main slides 21; Hidden slides 84. 21 Object pose; 84 RGB-D back-projection

### QA.13

Question: What do subpixel corner refinement and Rodrigues conversion contribute?

Short answer: Corner refinement estimates edge intersections below the pixel grid, so pose inputs are less quantized. Rodrigues conversion changes the representation of the recovered rotation. Neither step alone validates the marker pose against an independent reference.

Supporting detail: This is ArUco detection with corner refinement based on the AprilTag method, not an AprilTag marker detector. The Rodrigues vector has unit-axis direction and angle magnitude; equation E.1 converts it to a rotation matrix. The worked recomposition agrees only to the displayed rounding.

Sources: Appendix E.1, E.3-E.4; printed E1-E2, E5-E7; PDF 149-150, 153-155.

Limits and evidence: Detection is standard, not a new contribution. The numerical rotation check is not pose-accuracy evidence.

Supporting slide: Hidden slides 92-93. 92 ArUco vs AprilTag: what the literature reports; 93 AprilTag 3 faster; corner errors converge at 96 px Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### QA.18

Question: What makes the capture reproducible, and what happens if the negotiated streams differ?

Short answer: Capture requests 640 by 480 colour and depth at 30 frames per second, verifies the negotiated profiles and stops if they differ. The bag stores calibration, sensor settings, image messages and frame metadata so replay retains the recorded configuration.

Supporting detail: Colour uses bgr8 and depth z16. Table A.1 reports 900 frames per stream over 29.99 seconds, with 1.38 GB raw pixel payload and 0.82 GB stored file size. The complete take includes approach and retreat as well as manipulation.

Sources: Appendix A.1-A.3, Figure A.1, Table A.1; printed A1-A3; PDF 137-139.

Limits and evidence: Recorded configuration supports traceability; it does not establish repeatability across subjects, tasks or other cameras.

Supporting slide: Main slides 4; Hidden slides 68. 4 Task and observations; 68 Evaluation references

## Modelling and observability

### Q2.8

Question: How do you know the repaired hip depth is anatomical?

Short answer: I do not establish that. The preparation rejects several implausible configurations and remembers accepted depth, but a wrong sample can still seed memory. Every downstream angle depends on that root reference.

Supporting detail: Width and line checks precede depth-memory and shoulder-depth checks. A repaired point does not update memory, which has no expiry. This is a practical preparation for reconstruction, not an independently validated pelvis measurement. Calling the root only a display reference would understate its influence on the arm angles.

Sources: V9 Section 2.6, PDF pages 33-34; Section 3.5, PDF page 51; Appendix G branching and limits.

Limits and evidence: V9 method and explicit anatomical limit.

Supporting slide: Main slides 13, 17, 52; Hidden slides 75. 13 Hip-depth ambiguity; 17 Torso frame; 52 Landmarks on an occluding surface; 75 Torso preparation

### Q3.1

Question: Why build the torso frame from two hips and the right shoulder, and what happens when the shoulder moves independently?

Short answer: The torso frame uses three points to define its plane. The choice gives a simple frame, but it treats the torso as one rigid plate, so independent shoulder motion can change the reference for both arms.

Supporting detail: The hip line sets x; a hip-to-right-shoulder vector selects the plane; cross products complete the orthonormal axes. This is not a separate pelvis-plus-thorax or shoulder-girdle model. The thesis gives no comparison with a shoulder midpoint or four-point fit.

Sources: V9 Sections 3.2.1-3.2.2 and Equations (3.7)-(3.11), PDF pages 39-41; Figure 3.4, PDF page 40.

Limits and evidence: V9 model simplification; untested alternative.

Supporting slide: Main slides 17. 17 Torso frame

### Q3.2

Question: Why does the worked example show a pitched torso caused by rail depth, and is it the pipeline's final pose?

Short answer: Chapter 3 calculates frame 533 before hip preparation. Chapter 6 presents a separate causal trace with conflicting wording that the midpoint was left unchanged. The original published pelvis does not establish unchanged solver inputs. The exact offline post-preparation pose is not verified here.

Supporting detail: Chapter 3 uses 0.99 m hip depth and prints root angles (-32.1, 179.5, -3.3) degrees before replacement. Live code solves first, then publishes the original hip midpoint; offline evaluation instead reads the solver's prepared hips. The pinned causal dump for frame 533 publishes pelvis z=0.99001175 m with root state 2, constrained, and angles (-13.2193, 176.4714, -2.3740) degrees. This separates published translation from solved orientation; it does not resolve every intermediate in Chapter 6's account.

Sources: V9 Section 3.5, PDF page 51 (printed 37); Section 6.5, PDF page 95 (printed 81); Sections 2.6 and G.4, PDF pages 33-34, 161; compiled DOCX paragraphs 467/715 (zero-based extraction); v2/person/v2_person.py:201-202; eval/failure/recovery_core.py:214-221; v2/output/v2_person_dump_r6b_full.csv, frame 533.

Limits and evidence: The Chapter 6 wording conflict is acknowledged, not resolved by treating published pelvis translation as the solver input. Exact offline post-preparation angles and a complete internal frame trace remain unverified.

Supporting slide: Main slides 17. 17 Torso frame

### Q3.3

Question: Are the approximately 32-degree torso pitch and desk-marker tilt the same error?

Short answer: They are different quantities calculated from different measurements. Similar values do not establish a common cause.

Supporting detail: The torso pitch comes from the hip/shoulder geometry in Camera'. The card tilt is the angle between the desk-marker axis and calibrated gravity in World. Both belong to the same setup, but the thesis does not establish a causal coupling between their numerical similarity.

Sources: V9 Section 3.5, PDF page 51; Section 4.3, PDF page 59.

Limits and evidence: Verified distinction; common-cause claim unestablished.

Supporting slide: Main slides 15, 17, 21; Hidden slides 76. 15 Camera and Camera-prime; 17 Torso frame; 21 Object pose; 76 Coordinate transforms

### Q3.4

Question: How is the geometric T-pose zero matched to the avatar?

Short answer: The zero is defined by the frame and rotation convention, rather than measured by zeroing the subject's joints. The avatar must use a matching reference pose and apply the shoulder factors in the stated order.

Supporting detail: The right upper arm lies along local +x at zero; the left solver mirrors the corresponding geometry. Figure 3.5 shows the subject in a T-pose. A reference illustration does not itself demonstrate a per-subject angle-zero calibration.

Sources: V9 Figure 3.5 and Section 3.3.3, PDF pages 42, 44; Equation (3.18), PDF page 46; Chapter 6 Section 6.3 rig mapping.

Limits and evidence: V9 convention.

Supporting slide: Main slides 15, 41-42; Hidden slides 76. 15 Camera and Camera-prime; 41 Mapping into Scene; 42 Rig application; 76 Coordinate transforms

### Q3.5

Question: Why do calibrated segment lengths differ for the same arm across recordings?

Short answer: They are lengths between detected landmarks, not direct anatomical bone measurements. A shifted elbow changes the upper-arm/forearm split, even when the overall reach is similar.

Supporting detail: The rail worked example uses 31.7 and 20.5 cm. The thesis calls these effective lengths and compares them with body measurements in Section 6.3. This supports a landmark-consistent reconstruction; it does not independently locate the anatomical elbow. Calibration cannot turn a biased landmark into ground truth.

Sources: V9 Section 3.3.1, PDF pages 42-43; Section 5.6, PDF page 77; Chapter 6 Section 6.3; final Chapter 9 person/object bullet, PDF page 131.

Limits and evidence: V9 statement; anatomical accuracy unverified.

Supporting slide: Main slides 41-42, 64. 41 Mapping into Scene; 42 Rig application; 64 Limitations

### Q3.6

Question: Is the algebraic twist-observability check the same as the 15/25-degree hold?

Short answer: No. The algebraic solver detects an essentially vanishing perpendicular forearm component. The recovery layer separately holds noisy measured twist below 15 degrees of flexion and releases it above 25 degrees.

Supporting detail: shoulder.py uses TWIST_EPS=1e-6 of forearm length. That numerical degeneracy check is much tighter than the stabilization rule. In occlusion_ext.py the hold acts on a measured/live twist group; a rebuilt constrained arm is instead subject to the rate limiter. Do not describe these as one threshold in two units.

Sources: V9 Section 3.4.3, PDF page 49; Section 5.5, PDF page 75; v1/kinematics/shoulder.py TWIST_EPS and solve_right_shoulder; v1/kinematics/occlusion_ext.py angle stabilization.

Limits and evidence: Implementation verified.

Supporting slide: Main slides 18-19, 32-33. 18 Shoulder swing; 19 Shoulder twist; 32 Selecting one elbow; 33 Direction-memory fallback

### Q3.7

Question: What does landmark noise do to the angles, beyond the exact synthetic verification?

Short answer: Exact synthetic checks verify the algebra, not noisy sensing. A short segment is sensitive to endpoint error, and twist becomes especially sensitive when the elbow is nearly straight. The thesis gives no full noise-propagation study.

Supporting detail: For a fixed endpoint and small perpendicular perturbation, direction error scales approximately as perturbation divided by segment length. This local explanation is not a measured whole-chain angle error: both endpoints, the torso basis and depth may be wrong together. Avoid quoting a centimetre-to-degree conversion as experimental evidence.

Sources: V9 Sections 3.4.3 and 3.5, PDF pages 49-53; Appendix H.3, PDF page 163.

Limits and evidence: Mathematical explanation; unmeasured sensing uncertainty.

Supporting slide: Main slides 18-20, 64. 18 Shoulder swing; 19 Shoulder twist; 20 Elbow; 64 Limitations

### Q3.8

Question: Why use a per-frame closed-form solve rather than temporal optimization?

Short answer: The closed-form solve makes each angle traceable to the current geometry and permits exact checks of the mathematics. Filtering and recovery add temporal behavior around it. V9 does not compare it with a temporal optimization baseline.

Supporting detail: The core solve has no optimization or carried state. The surrounding pipeline does carry directions, offsets, depth and held angles, so the full system is not stateless. A later optimization method would need its own reference and comparison; interpretability alone is not proof of superior accuracy.

Sources: V9 Chapter 3 opening, PDF page 35; Sections 5.3 and 5.5, PDF pages 69-75; Appendix H, PDF pages 162-163.

Limits and evidence: V9 method; no optimization baseline.

Supporting slide: Main slides 15-20, 23-26, 29-33. Use the stated comparison references and conditions.

### Q3.9

Question: Does the mirrored left-arm solver preserve the meaning of twist?

Short answer: In the model's convention, a mirror-symmetric pose gives equal angles with the same internal-rotation meaning on both sides. The left inputs are mirrored before applying the right-arm equations.

Supporting detail: Both segment vectors are expressed in the torso basis, then x is flipped by diag(-1,1,1). Appendix H includes a both-arms synthetic check. This verifies the convention, not that every reported angle is a clinically calibrated anatomical angle. The printed left twist is not independent physical validation of its sign.

Sources: V9 Section 3.4.2, PDF page 48; Section 3.5, PDF page 53; Appendix H.1 and Table H.1, PDF page 162; v1/kinematics/shoulder.py left solver.

Limits and evidence: V9 convention; synthetic mathematical verification.

Supporting slide: Main slides 18-19. 18 Shoulder swing; 19 Shoulder twist

### Q3.10

Question: Why store thirteen angles when only eleven are independent?

Short answer: The two elbow elevation fields are retained for generality in the interface, although they contain no independent motion in this model. Each arm contributes four independent angles, and the root contributes three.

Supporting detail: Solving shoulder twist aligns the forearm's perpendicular component with local +z, so elbow elevation is zero. The redundant fields are a representation choice. Do not say they cost nothing; they occupy fields even though they add no observable degree of freedom.

Sources: V9 Equations (3.18)-(3.24), PDF pages 46-49; Section 3.5, PDF page 53.

Limits and evidence: V9 mathematical dimension count and interface choice.

Supporting slide: Main slides 18-20, 35-38. Use the stated comparison references and conditions.

### Q3.N1

Question: What happens when the torso or shoulder swing reaches a singular configuration?

Short answer: Some angle coordinates cease to be unique even when the physical orientation remains meaningful. The solver uses a convention at the singularity; that should not be interpreted as measuring an otherwise unobservable angle.

Supporting detail: Root Euler gimbal lock leaves only a combined y/z rotation, so z is set to zero. An upper arm straight up or down leaves shoulder azimuth undefined, so it is set to zero and axial rotation folds into twist. Nearly singular inputs can still make angle series sensitive, which exact synthetic checks alone do not quantify.

Sources: V9 Equations (3.15)-(3.17), PDF page 45; Equations (3.20)-(3.21), PDF page 47; Appendix H.1, PDF page 162.

Limits and evidence: Verified parameter singularity; sensing sensitivity unmeasured.

Supporting slide: Main slides 18-19. 18 Shoulder swing; 19 Shoulder twist

## Recovery and retained state

### Q5.1

Question: How does the mostly-clean assumption fit the 77 fully measured frames out of 900?

Short answer: Those counts describe different conditions. Appendix H requires all eight points together for its solver check. The recovery assumption is a working assumption, and preparation can make the torso usable without making it independently measured or anatomically correct.

Supporting detail: Do not relabel 77 as the number of frames unflagged after every later recovery test without checking the validator's exact selection. The final appendix says all eight landmarks are measured and the selected frames lie inside the slide. A repaired root remains constrained. The low all-point count and persistent left-arm problems limit how literally the mostly-clean assumption can be applied to the whole recording.

Sources: V9 Section 5.1, PDF pages 63-64; Section 2.6, PDF pages 33-34; Appendix H.2, PDF pages 162-163; Section 5.6, PDF page 79.

Limits and evidence: V9 assumption and solver selection; exact intersection definition beyond appendix wording unverified here.

Supporting slide: Main slides 23-24, 64. 23 Output states; 24 Holding context; 64 Limitations

### Q5.2

Question: Which reference recording supports the geometry thresholds, and what is the safety margin?

Short answer: The pinned detector report names recording_20260224_083945, called R1. It documents the four thresholds, the reference headroom and the left-arm defect. It does not provide a single uniform percentage margin for all tests.

Supporting detail: r5_failure_mask.md says thresholds were derived plot-first from R1 and R5 distributions, with reference clean percentiles and project precedents. It reports threshold-minus-reference-maximum headroom, which is not the same as threshold-minus-clean-p99. Widening the segment tolerance to hide the defective reference left arm loses corruption windows. Do not invent a same-subject provenance assertion or exact percentile margin.

Sources: V9 Section 5.2, PDF pages 65-66; eval/failure/detect_failures.py constants; eval/reports/r5_failure_mask.md Threshold derivation and reference headroom.

Limits and evidence: Pinned report and implementation verified; exact per-test clean-p99 margin and subject identity not established here.

Supporting slide: Main slides 8-9. 8 Calibration; 9 Landmark acceptance

### Q5.3

Question: Can the broad hold and release radii confuse proximity with contact?

Short answer: Yes. Holding is an inferred state, not a measured contact. The radii and confirmation runs reduce unstable decisions, but a nearby hand can still satisfy the tests without gripping the cube.

Supporting detail: Entry needs a measured marker, an object away from rest, a measured unflagged nearby wrist and plausible forearm, confirmed for five frames. The hold radius is 25 cm; release is 35 cm; accepted offset magnitude is at most 30 cm. None measures fingers or force. A resting hand beside a moving cube is not excluded merely because the object-rest condition exists.

Sources: V9 Section 5.3 and Figure 5.4, PDF pages 69-70; Section 5.4, PDF page 72; eval/failure/grip_state.py and eval/failure/recovery_core.py.

Limits and evidence: V9 heuristic; contact accuracy unvalidated.

Supporting slide: Main slides 23-24. 23 Output states; 24 Holding context

### Q5.4

Question: What does the object constraint provide when the grasp is not rigid?

Short answer: It predicts a wrist from the current object pose and the retained offset. If the actual grip changes, that prediction can be wrong even when the marker pose is good. The natural-failure results show that it can help or hurt.

Supporting detail: The loop offset observations scatter by 7.0, 2.7 and 6.3 cm across axes. That is observation scatter, which includes measurement errors as well as possible grip changes; it is not a direct measurement of physical sliding. The 7 cm offset in Section 5.6 belongs to a rail example, so do not present it as the mean loop offset. A recursive average smooths observations but does not prove the frozen offset matches a later grip.

Sources: V9 Section 5.3, PDF page 69; Section 5.6, PDF page 77; eval/reports/r5_recovery_labeled.md natural failure table.

Limits and evidence: V9 scatter; pinned conditional outcome; causal attribution limited.

Supporting slide: Main slides 25-26, 50-51; Hidden slides 72. Use the stated comparison references and conditions.

### Q5.5

Question: How much does joint hand/marker occlusion restrict object-assisted recovery?

Short answer: Case B is available only when that hand is classified as holding, an offset is usable and the marker is measured on that frame. If the marker is lost as well, the object contributes no fresh wrist constraint.

Supporting detail: The loop has 2099 frames and 2058 marker detections. Forty of its 41 misses lie in the desk transfer and one near the edge. Every labelled failure frame has a detected marker, but detection alone does not prove that the accepted pose or offset is accurate. Those labelled comparisons are not a whole-recording Case-B availability rate, which requires the intersection of failure, holding, marker validity and offset validity.

Sources: V9 Sections 5.1 and 5.4, PDF pages 63-64, 71-72; Section 5.6 and Figure 5.6, PDF page 76; Section 7.4.2, PDF pages 116-117, checked against the final compiled pages; eval/failure/recovery_core.py.

Limits and evidence: V9 prerequisites; whole-recording intersection count not verified here.

Supporting slide: Main slides 25-26, 32-33. 25 Grasp offset; 26 Offset retention; 32 Selecting one elbow; 33 Direction-memory fallback

### Q5.6

Question: How sensitive is recovery to gains 0.02 and 0.30?

Short answer: They are the design gains used here, and V9 does not report a sensitivity sweep. A smaller gain retains older state longer; a larger one follows new measurements faster and passes more measurement variation.

Supporting detail: The offset update weights new observations by 0.02; the direction update uses 0.30 and renormalizes. These are exponential memories, not fixed fifty-frame and few-frame windows, and their effective time in seconds depends on how often clean observations arrive. During a failure they may receive no updates at all.

Sources: V9 Equations (5.4)-(5.5), PDF pages 69, 71.

Limits and evidence: V9 design parameters; mathematical behavior; sensitivity unmeasured.

Supporting slide: Main slides 25-26, 32-33. 25 Grasp offset; 26 Offset retention; 32 Selecting one elbow; 33 Direction-memory fallback

### Q5.7

Question: What is the 15-degree-per-frame rate limit for, and how often does it bind?

Short answer: It limits abrupt arm-angle changes and marks the result constrained. It is a guard, not a maximum human-motion claim. I do not have a verified binding count for each final evaluated recording.

Supporting detail: The code wraps angle differences and clips excessive changes relative to the previous output. Fifteen degrees per frame corresponds to 450 degrees/s only at exactly 30 frames/s; it is not a timestamp-scaled bound. It can act after ordinary landmark errors or a return from unobservable twist. A constrained tag alone does not isolate which guard acted.

Sources: V9 Section 5.5, PDF page 75; v1/kinematics/occlusion_ext.py angle stabilization and _stab counters.

Limits and evidence: Implementation verified; usage frequency unverified here.

Supporting slide: Main slides 32-33. 32 Selecting one elbow; 33 Direction-memory fallback

### Q5.8

Question: Near full reach, what does a 1 cm wrist error do to the elbow?

Short answer: The elbow solution becomes sensitive near full reach, and a small wrist change can also cross the 98 percent switch into the direction-memory branch. V9 does not report the requested perturbation result.

Supporting detail: The worked example has 50.7 cm reach for links totaling 52.2 cm and a circle radius about 6 cm. That circle is the feasible set for fixed endpoints, not a universal bound on error after changing the wrist. Changing the wrist changes the centre, radius, remembered-direction projection and possibly the solver branch.

Sources: V9 Equations (5.9)-(5.12), PDF pages 73-74; Section 5.5 guard, PDF page 75; worked example, PDF page 78.

Limits and evidence: Verified mathematical sensitivity; no perturbation experiment.

Supporting slide: Main slides 29-32; Hidden slides 73. Use the stated comparison references and conditions.

### Q5.9

Question: Does dropping failure runs shorter than five frames ignore genuine errors?

Short answer: It can suppress a short geometry alarm. That is a detector design choice, and it can create false negatives. It is not guaranteed that the earlier gap filter already repaired every short silent error.

Supporting detail: Declared missing samples remain missing at acquisition even if an event mask is shortened. A finite wrong point with adequate visibility is different: if its geometry alarm is removed, the assembled arm mask may not remove it. Closing gaps and removing short events affect masks; linear interpolation affects missing position samples. Those operations are not interchangeable.

Sources: V9 Section 5.2, PDF page 66; Section 2.5, PDF pages 30-32; eval/failure/detect_failures.py BRIDGE_GAP and MIN_EVENT.

Limits and evidence: V9 detector behavior; false-negative trade-off unquantified.

Supporting slide: Hidden slides 97. 97 Short-gap interpolation Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q5.10

Question: What stops a stale object offset from pulling the rebuilt arm to the wrong place?

Short answer: The offset bound, reach handling and angle limit provide guards, but none certifies that the offset is current. A stale accepted offset can produce a wrong wrist and arm.

Supporting detail: Case B takes priority over direction-memory wrist recovery. Above the reach guard the elbow can come from memory while the object still anchors the wrist, leaving the forearm length inconsistent. A proposed agreement check between the two wrist predictions is future work, not an implemented safeguard. The natural-label comparison grades the resulting arm, not just the object-derived point.

Sources: V9 Sections 5.3-5.5, PDF pages 69-75; eval/failure/recovery_core.py; eval/reports/r5_recovery_labeled.md.

Limits and evidence: V9 explicit limit; pinned conditional results; no stale-offset certification.

Supporting slide: Main slides 25-26, 29-33, 50-51; Hidden slides 72. Use the stated comparison references and conditions.

### Q5.N1

Question: Does the object-derived wrist uniquely determine the elbow?

Short answer: Generally, no. With separated endpoints strictly within reach, the shoulder, wrist and two lengths define a circle of possible elbows. Direction memory selects one point. At tangency the geometry collapses to a point; outside reach there is no exact intersection.

Supporting detail: A nondegenerate circle requires abs(L1-L2) < r < L1+L2, where r is shoulder-to-wrist distance. With separated endpoints, equality at either bound gives tangency. Coincident endpoints are a separate degenerate case; the implemented helper returns no elbow there. On a circle, projecting the remembered upper-arm direction selects the closest feasible elbow. Fallback directions provide a choice rather than a new observation.

Sources: V9 equation (5.8) and equations (5.9)-(5.12), Figure 5.5, PDF pages 73-74; v1/kinematics/occlusion_ext.py:334-374.

Limits and evidence: Mathematical geometry subject to reach and degeneracy conditions. A selected feasible elbow is not an independently measured hidden elbow.

Supporting slide: Main slides 29-31; Hidden slides 73. 29 Two segment-length constraints; 30 The circle of possible elbows; 31 Deriving the elbow circle; 73 Two-link reconstruction

### Q5.N2

Question: Do reach clipping and the near-full-reach fallback preserve both arm lengths?

Short answer: Not always. An unreachable wrist has no exact two-link solution, and the implemented clipping can preserve the upper-arm length while leaving the forearm too long or too short. The near-reach memory branch can also break the forearm-length condition.

Supporting detail: The thesis explicitly qualifies the exact sphere construction. With links 0.317/0.205 m and reach 0.600 m, the pinned diagnostic gives actual lengths 0.317/0.283 m after clipping. That is a deterministic diagnostic example, not a measured anatomical result. It prevents a false claim that every constrained output satisfies both equalities.

Sources: V9 Section 5.5, PDF pages 74-75; writing/v9/audit_evidence/final_completion/recovery_diagnostic.txt UNREACHABLE cases.

Limits and evidence: V9 limit and pinned implementation diagnostic.

Supporting slide: Main slides 32-33. 32 Selecting one elbow; 33 Direction-memory fallback

### Q5.N4

Question: Does measured mean the reconstructed joint is anatomically correct?

Short answer: No. It is a provenance state: the required landmarks were measured and unflagged for that group. A confident wrong landmark or wrong surface depth can still be inaccurate.

Supporting detail: Held means retaining a previous angle. Constrained means rebuilt landmarks or a limited change. These states explain where an output came from; they are not calibrated confidence probabilities or independent accuracy labels. A repaired root is constrained even if a complete pose is available.

Sources: V9 Chapter 5 opening, PDF page 62; Section 5.2, PDF pages 64-66; worked example group states, PDF page 79.

Limits and evidence: V9 state definitions; no confidence calibration.

Supporting slide: Main slides 23-24. 23 Output states; 24 Holding context

### Q6.9

Question: What remains available when the object record is stale or the marker is hidden?

Short answer: An unacceptable object record cannot provide the object-assisted wrist constraint. The system must use whatever accepted body measurements and retained-state fallbacks remain. If both the arm and marker are unavailable, it has no new object information with which to recover the arm.

Supporting detail: The link rejects records more than three frames from the person frame. The loop recording has 41 frames without a detected object marker, concentrated in the transfer. The natural-failure label set does not cover that marker-loss stretch: every labelled frame has a detected marker. A processing-time p99 alone cannot establish the probability of stale records or the success of a particular fallback.

Sources: Thesis Section 6.1.2, p. 71 (PDF 85); Section 8.2, pp. 110-111 (PDF 124-125); Section 7.4.2, pp. 102-103 (PDF 116-117); loop_detection.json under writing/v9/audit_evidence/ch7_restructured/.

Limits and evidence: Availability condition and recorded coverage. No guarantee about grip recovery after an arbitrary missing-record sequence.

Supporting slide: Main slides 23-24. 23 Output states; 24 Holding context

### Q9.4

Question: Is the stored hand-object offset useful when the grip changes?

Short answer: It is a conditional constraint. It can help while the stored offset still represents the grip and the object pose is available. A changing grip or an outdated offset can make it misleading, which is consistent with the different left- and right-arm results.

Supporting detail: The left natural-failure set has worse median distance with assistance, while the four right frames improve relative to both baselines. The synthetic test is also mixed. These results do not establish reliability for a class of rigid grips or demonstrate that non-rigid grips always fail. A closer wrist label does not establish the full arm configuration.

Sources: Thesis Tables 7.6-7.9, pp. 101-105 (PDF 115-119); Chapter 9 recovery bullet, p. 117 (PDF 131); Section 10.1, p. 121 (PDF 135); synthetic.json and natural.json.

Limits and evidence: Conditional recovery on small recorded samples.

Supporting slide: Main slides 25-26, 50-51; Hidden slides 72. Use the stated comparison references and conditions.

### QA.7

Question: Why do hip preparation and Chapter 5 use different thresholds, and where do the constants come from?

Short answer: They are different stages: preparation rejects and repairs torso inputs before solving, while Chapter 5 reports tracking failures and recovery conditions. The thesis explicitly states the differing thresholds but gives no calibration study establishing that these constants are optimal.

Supporting detail: Preparation uses 30 percent width tolerance, 20/10 degree line hysteresis, 10 cm depth change, 15 cm hip-to-input-shoulder depth separation, 70/30 memories, 60 available calibration observations and a 45 frame single-endpoint fallback. The Chapter 5 offline torso detectors use 20 percent and 22 degrees. Each number is a stated implementation setting.

Sources: Appendix G.1-G.4; printed G1-G3; PDF 159-161.

Limits and evidence: No measured false-rejection tradeoff is established as the reason for these values. The 45 frame limit is not a depth-memory expiry.

Supporting slide: Main slides 23; Hidden slides 75, 83. 23 Output states; 75 Torso preparation; 83 Recovery guards

### QA.14

Question: Can a stale or wrong hip depth remain in memory indefinitely?

Short answer: Yes. Accepted depth memory has no expiry, and repaired samples do not update it. A bad initial depth can survive if it passes the checks. The 45 frame limit applies only to one missing-endpoint fallback.

Supporting detail: After rejection, surviving torso samples seed or update depth with 70 percent previous and 30 percent current. Persistent rejection can therefore continue to use old depth. Starting with hidden hips was not evaluated, and genuine lean or translation can trigger the depth rules.

Sources: Appendix G.1-G.4; printed G1-G3; PDF 159-161.

Limits and evidence: No general guarantee establishes correct initialization or recovery from a biased memory seed.

Supporting slide: Main slides 26; Hidden slides 74, 83. 26 Offset retention; 74 Grasp-offset update; 83 Recovery guards

### QA.15

Question: Do all torso repairs preserve the measured camera ray?

Short answer: No. A single-point depth replacement preserves its usable ray. A whole-pair repair also enforces pair width and direction, so its final endpoints can leave their original rays.

Supporting detail: Equation G.1 scales p by replacement-depth/p_z when p_z is above 5 cm. Whole-pair repair first places two rays at remembered depths, forms a midpoint, then places endpoints half a calibrated width around it. If that construction fails, a fallback keeps the input midpoint with remembered direction.

Sources: Appendix G.1, G.3; printed G1-G3; PDF 159-161.

Limits and evidence: The fallback cannot remove a shared wrong depth in that midpoint. A missing point or unusable ray cannot receive the single-point ray repair.

Supporting slide: Main slides 23-24; Hidden slides 83. 23 Output states; 24 Holding context; 83 Recovery guards

## Integration and causal processing

### Q4.8

Question: How does a viewer know a frozen cube is held rather than measured?

Short answer: The thesis documents the cube turning red when its live bit drops. The last pose can remain on screen, while the colour marks that it is no longer a current measurement.

Supporting detail: Cleaning clears unseen or rejected rows, and the receiver can retain the last pose with its live bit off. Section 6.4 documents the red indicator. That establishes the described receiver behavior, but it does not prove every later committee replay used or visibly displayed that same indicator. A static cube alone is insufficient evidence of a measured pose.

Sources: V9 Section 4.2, PDF page 58; Section 6.4, PDF page 93, checked against the final compiled page; Chapter 9 marker-loss discussion and Figure 9.1, PDF pages 130-131.

Limits and evidence: V9 documented receiver behavior; indicator use in each later replay unverified here.

Supporting slide: Main slides 43. 43 Integrated reconstruction

### Q5.N3

Question: Is the offline grip and offset preparation causal?

Short answer: No. Offline confirmation can label earlier frames of a grip, and its initial offset fallback may use observations from the whole episode. The causal version cannot use those future observations.

Supporting detail: Offline entry starts at the first frame of the five-frame confirmation run, and a confirmed exit clears the whole exit run. Before local initialization, episode or recording-wide means can provide the offset. A replay that uses these offline products cannot be called causal merely because it is shown at recorded pace.

Sources: V9 Section 5.3, PDF pages 69-70; Chapter 8 Section 8.2 causal initialization; eval/failure/grip_state.py; pinned recovery_diagnostic.txt PREFIX example.

Limits and evidence: V9 offline/causal distinction; implementation diagnostic.

Supporting slide: Main slides 55-58; Hidden slides 101. Use the stated comparison references and conditions. Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q6.1

Question: Why use shared memory rather than sockets, and how would a remote display work?

Short answer: The evaluated processes run on one workstation, so shared memory fits that deployment. The thesis does not compare transports experimentally. Later defence benchmarks support the local choice under their tested conditions; a remote display would require a separate network transport.

Supporting detail: Section 6.1 separates the large image buffer from the small pose records. Unity reads scene and combined records, not the image buffer. Later TCP, UDP and shared-memory tests use Python endpoints on this workstation, so their times do not measure the Unity receiver or a network deployment. A network bridge is a possible extension, not an implemented or costed thesis result.

Sources: Thesis Section 6.1, Table 6.1 and Figures 6.1-6.3, pp. 66-71 (PDF 80-85); presentation/defense_2026/experiments/transport_bench/README.md and results.csv; knowledge/transport_facts.md.

Limits and evidence: Final-thesis architecture plus separately dated supplementary benchmark. No universal transport ranking or claim that a bridge is a trivial change.

Supporting slide: Main slides 36, 39-40; Hidden slides 94. 36 One capture, two readers; 39 Python publication; 40 Unity read verification; 94 Transport candidates Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q6.2

Question: Which receiver produced Tables 7.3 and 7.4, and were those results obtained from the merger-fed causal renderer?

Short answer: The evaluation captures used recording-specific rig lengths and the start-up corrections described in Chapter 6. The merger-fed receiver described in the thesis differs: it does not apply the forced T-pose or supplied segment lengths. The tables do not validate that receiver's rendering.

Supporting detail: Section 6.3 explicitly distinguishes the two receivers. Section 7.3 requires capture checks against the lengths requested for each recording. A later presentation replay has its own packet and rig provenance and cannot inherit the thesis table values. Combining receiver features would need implementation and validation; its difficulty was not measured.

Sources: Thesis Section 6.3, pp. 75-78 (PDF 89-92), and Section 7.3, pp. 93-97 (PDF 107-111); writing/v9/audit_evidence/ch7_restructured/human.json; presentation/defense_2026/DECISIONS.md D-058 and D-066.

Limits and evidence: Final-thesis capture configuration and historical presentation diagnostics. D-058/D-066 source-validation limitations remain; no renderer root cause is inferred from them.

Supporting slide: Main slides 43. 43 Integrated reconstruction

### Q6.3

Question: How was the rest-pose assumption in equation (6.5) checked, and what would a mismatched rig mean?

Short answer: The evaluation setup forces a T-pose and records the rest rotations, but the thesis still treats the rig's axis alignment as an assumption. Its worked example checks one resulting direction. That is useful consistency evidence, not a proof for every rig or pose.

Supporting detail: Equation (6.5) composes the scene anchor, the solved segment rotation and a fixed bone-rest rotation. The worked example reports 0.4 degrees between the upper-arm direction and its measured direction, and 10.0 degrees for the forearm while twist is held. The latter includes solver state. Neither observation isolates rig-authoring error or proves that a wrong rest rotation could never produce local agreement.

Sources: Thesis Section 6.3, equation (6.5), pp. 75-76 (PDF 89-90); Section 6.5 and Table 6.2, pp. 83-84 (PDF 97-98).

Limits and evidence: Stated model assumption and one worked example, not independent anatomical validation.

Supporting slide: Main slides 41; Hidden slides 76. 41 Mapping into Scene; 76 Coordinate transforms

### Q6.4

Question: Why use landmark-derived arm lengths when they differ from the approximately 25 cm anatomical measurements?

Short answer: The rig reproduces the segment lengths used by the reconstruction, so the display and solver use the same geometry. Those are effective landmark lengths, not anatomical lengths. Their disagreement with the physical measurements is a limitation, not evidence that the body changed.

Supporting detail: The rail right arm uses 31.7 and 20.5 cm, whereas the loop uses 25.6 and 25.2 cm. The independent measurement of about 25 cm per segment was not used to calibrate either model or rig. Changing only the avatar lengths would change the displayed endpoints without recalibrating the reconstruction. The thesis does not isolate how much rendered error each source contributes.

Sources: Thesis Section 6.3, pp. 76-77 (PDF 90-91); Section 7.3, pp. 93-97 (PDF 107-111); Table 9.1, p. 120 (PDF 134).

Limits and evidence: Final-thesis geometry and physical comparison. Do not identify the elbow landmark or rig lengths as the sole cause of rendered error.

Supporting slide: Main slides 47-48. 47 Model and rendered rig; 48 Body and rig: joint-results table

### Q6.5

Question: What supports the merger's two-frame delay, three-frame interpolation gap, two-tick blend and half-second object timeout?

Short answer: They are the configured operating choices of this implementation. The thesis explains what they do, but does not establish optimal values through a parameter sweep. The two-frame delay provides room for pairing samples; it is not a guarantee that both branches always arrive in time.

Supporting detail: At 30 ticks per second the configured delay is about 66.7 ms. A longer gap causes holding, followed by blending when measurements return. Object staleness changes the live flag. These mechanisms trade freshness against continuity.

Sources: Thesis Section 6.1.2, p. 71 (PDF 85), and Section 8.4, p. 114 (PDF 128); v2/integration/v2_integrate.py; v2/dataset/r6b_probe_baseline.txt.

Limits and evidence: Documented configuration, not optimized constants or a latency bound.

Supporting slide: Main slides 38; Hidden slides 77. 38 A common render time; 77 Record fields

### Q6.6

Question: Did either branch drop frames in the recorded replay, and how is that distinguished from a timing guarantee?

Short answer: The archived run reports all 900 frames consumed by each branch and zero frames skipped by the latest-value policy. Frame indices and counters make that check possible. This is evidence about that replay; it does not guarantee that a branch can never fall behind.

Supporting detail: The eight-slot buffer provides finite retention. The person and marker compute p99 values are 13.03 and 16.73 ms, but p99 is not a maximum: the same log gives a 34.26 ms person maximum. The sequence-counter design is described in the thesis; later transport work records unverified implementation-level concerns, so this answer does not claim a formal proof against torn reads.

Sources: Thesis Section 6.1.1, pp. 67-68 (PDF 81-82), and Section 8.4, p. 114 (PDF 128); v2/dataset/r6b_probe_baseline.txt; knowledge/transport_facts.md, D-154 observations.

Limits and evidence: Recorded count and timing evidence. No new concurrency test was run for this answer.

Supporting slide: Main slides 39-40; Hidden slides 94. 39 Python publication; 40 Unity read verification; 94 Transport candidates Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q6.7

Question: Are the Chapter 7 values measured before or after display smoothing?

Short answer: The chapter reports two different quantities. Kinematic-model error is computed before Unity mapping and display filtering. Rendered-rig error uses logged Unity joint positions after the display path. Tables 7.3 and 7.4 are the rendered quantity.

Supporting detail: Both compare with accepted raw MediaPipe-plus-depth landmarks. The same-frame handover comparison gives model wrist medians of 0.83 and 2.34 cm, versus rendered medians of 5.5 and 6.8 cm. The statement about analysis tables before smoothing must not be applied to the separately captured Unity positions. The stages contributing to the rendered discrepancy were not isolated.

Sources: Thesis Section 6.3, p. 77 (PDF 91); Section 7.3 and equation (7.5), pp. 93-97 (PDF 107-111); human.json and bare_model.json under writing/v9/audit_evidence/ch7_restructured/.

Limits and evidence: Final-thesis definitions and paired-frame comparisons, not an ablation of smoothing.

Supporting slide: Main slides 47-48. 47 Model and rendered rig; 48 Body and rig: joint-results table

### Q6.8

Question: Which parts of the Unity room are measured and which are scenery?

Short answer: The calibrated marker poses, depth-derived tabletop plane, camera pose and measured cube size anchor the scene. Desk width, slab thicknesses, legs and floor are display geometry. The thesis does not claim that the whole room is a surveyed reconstruction.

Supporting detail: Equation (6.6) applies gravity alignment and a recording-specific floor translation. Those rigid operations preserve Euclidean distances, but they do not turn arbitrary furniture dimensions into measurements. The scene does not draw the rail. The offset d locates the drawn floor relative to the marker; it is not an independently measured floor-height result.

Sources: Thesis Section 6.4 and equation (6.6), pp. 78-79 (PDF 92-93); Section 7.2.2, p. 92 (PDF 106).

Limits and evidence: Calibrated geometry plus explicitly illustrative scenery.

Supporting slide: Main slides 41-42. 41 Mapping into Scene; 42 Rig application

### Q8.1

Question: What does the thesis establish about real-time operation, given that its evaluation used a recording?

Short answer: It establishes causal processing and sustained recorded replay on the tested workstation. It does not validate a complete live-camera session or sensor-to-screen latency. Later defence footage and fresh Unity replays are supplementary demonstrations; they do not turn the thesis replay into a measured end-to-end live system.

Supporting detail: The archived run consumes 900 frames without latest-value skips and has branch p99 compute times within the 33.3 ms nominal budget. The corrected validator also retains failures for five-frame lag and the worst-group p95 angle difference. Its passing timing checks must not be presented as all checks passing or as causal output accuracy against independent truth.

Sources: Thesis Sections 8.3-8.5, pp. 111-115 (PDF 125-129); v2/dataset/r6b_probe_baseline.txt; v2/dataset/m03_rail_corrected.txt; presentation/defense_2026/README.md, Evidence and results and Limitations and navigation; MEDIA_PROVENANCE.md.

Limits and evidence: Final-thesis replay performance versus later qualitative media. Full live-camera validation and sensor-to-screen latency remain unmeasured.

Supporting slide: Hidden slides 103. 103 Why One Euro in real time Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q8.2

Question: How can the replay consume every frame while reporting about 29 fps rather than the nominal 30 fps?

Short answer: Frame coverage and average wall-clock throughput are different measurements. The log reports 900 frames published and consumed over about 31.0 seconds, which gives about 29 fps. It separately records hardware frame intervals near 33.36 ms and no latest-value skips.

Supporting detail: The person log reports 29.1 fps and the source and object logs 29.0, with their rounded elapsed times. This is not simply 30 rounded down. The record does not partition the difference into start-up, waiting and other overhead, so I would not assign a cause. The count proves coverage for the run, not exact 30 Hz end-to-end delivery.

Sources: Thesis Section 8.4, p. 114 (PDF 128); v2/dataset/r6b_probe_baseline.txt, source, person, object, clock and jitter summaries.

Limits and evidence: Recorded throughput and hardware-clock intervals; overhead attribution unresolved.

Supporting slide: Hidden slides 94. 94 Transport candidates Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q8.3

Question: What has been established about causal output correctness when it differs substantially from the offline path?

Short answer: Chapter 8 compares two processing paths, neither of which is independent truth. It identifies conditional agreement and substantial differences caused by their filtering and retained state. It does not establish the causal path's anatomical accuracy by showing agreement with the offline path.

Supporting detail: After selecting a five-frame alignment and retaining 174 paired clean-arm frames, median differences are 0.4 degrees for elbow flexion, 1.4 for elevation and 7.0 for twist. The 16.4-degree azimuth median and the 12.0 cm wrist separation at frame 18 must remain visible. Small elbow disagreement alone cannot establish a correct full arm.

Sources: Thesis Section 8.3, Figures 8.2-8.3, pp. 111-113 (PDF 125-127); v2/dataset/m03_rail_corrected.json; writing/v9/figures/ch8_compare.json.

Limits and evidence: Within-recording path comparison. Re-evaluating causal outputs against physical or manual references is proposed work, not an already completed validation.

Supporting slide: Hidden slides 103. 103 Why One Euro in real time Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q8.4

Question: Does selecting the best five-frame alignment make the 0.4-degree elbow result optimistic?

Short answer: It is explicitly a best-aligned comparison on a selected clean-arm subset. It answers how closely those series agree after shifting them, not how accurately the live path follows motion without delay. The shift and the retained sample count must accompany the number.

Supporting detail: The comparison keeps 174 of 900 frames with cleanly measured arms on both sides. Rebuilt intervals are shown separately in Figures 8.2 and 8.3. The validator reports the lag criterion as failed. The shift also reflects processing-path and state differences; it should not automatically be equated with pure filter lag or sensor-to-screen latency.

Sources: Thesis Sections 8.3-8.4, pp. 113-114 (PDF 127-128); v2/dataset/m03_rail_corrected.txt and .json.

Limits and evidence: Best-aligned, gated comparison, not unbiased whole-run accuracy. An unaligned comparison is additional analysis, not a result asserted here.

Supporting slide: Hidden slides 103. 103 Why One Euro in real time Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q8.5

Question: Which One Euro parameters were used in the causal path, and what is known about faster motion?

Short answer: The causal landmark filter uses a 1 Hz minimum cutoff and beta 1. The 0.05 Hz setting shown in Appendix F is a different filter instance and should not be quoted as the causal setting. Neither establishes performance on fast clinical tasks.

Supporting detail: The causal implementation increases cutoff with estimated coordinate speed to trade smoothing for responsiveness. The thesis does not report a parameter sweep or a law relating its lag to arbitrary faster motion. Later defence filter benchmarks compare both settings on one recorded right-wrist series; those are supplementary measurements, not clinical validation or end-to-end latency.

Sources: Thesis Section 8.2, p. 109 (PDF 123); v1/realtime/person/realtime_person.py:98 and v2/person/v2_person.py; knowledge/filter_facts.md; presentation/defense_2026/experiments/filter_metrics/summary.csv and README.md.

Limits and evidence: Implementation-verified settings plus separately dated filter benchmark. No extrapolated fast-motion result.

Supporting slide: Hidden slides 101, 103. 101 One Euro filtering; 103 Why One Euro in real time Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q8.6

Question: What start-up conditions does the grip tracker need, and is starting with the cube already held validated?

Short answer: The thesis's causal tracker takes its initial object samples as a rest reference and learns the offset from the first clean observations of a grip. It calls for a defined start with the object at rest and visible. An arbitrary already-held start was not validated.

Supporting detail: The offline and causal paths can preserve different early twist and offset states after observations return. The thesis identifies initialization as a deployment issue, but does not establish that every in-hand start must permanently fail or that a particular warm-up protocol guarantees success. A proposed start-up acceptance procedure would need its own test.

Sources: Thesis Section 8.2, p. 109 (PDF 123); Sections 8.3-8.5, pp. 112-115 (PDF 126-129); Chapter 9 causal-processing bullet, p. 119 (PDF 133).

Limits and evidence: Documented mechanism and unvalidated starting condition.

Supporting slide: Main slides 23-24. 23 Output states; 24 Holding context

### Q8.7

Question: Does workstation timing establish feasibility on a clinical laptop or with a lighter detector?

Short answer: No. The measured budget is specific to the reported Ryzen 9 7950X and RTX 3080 workstation. The thesis identifies a lighter detector as an option, but does not report a laptop experiment or demonstrate that changing detector size preserves the same accuracy.

Supporting detail: Detection dominates the recorded branch compute time. The statement that no added stage exceeds 0.63 ms at p99 applies per stage; it is not the sum of all added work and not a worst-case bound. A different device needs measurements of the whole configuration, including timing and reconstruction quality.

Sources: Thesis Section 8.4, p. 114 (PDF 128); Appendix B, Table B.1; v2/dataset/r6b_probe_baseline.txt.

Limits and evidence: Hardware-specific measured performance. No cost estimate or promised one-parameter deployment fix.

Supporting slide: Hidden slides 94. 94 Transport candidates Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q8.8

Question: Why is timestamp difference not already a sensor-to-screen latency measurement?

Short answer: The records describe capture-session and render times, not the instant pixels appear on the screen. The worked example interpolates between two input frames at an earlier render time. Its timestamps do not constitute a measured end-to-end latency distribution.

Supporting detail: The tick is at 17.82 s and targets 17.75 s; frame 533 is published at 17.78 s and is one interpolation endpoint. Subtracting that endpoint from the tick gives about 40 ms, but then adding the two-frame delay counts related timing twice and misidentifies the displayed sample. The configured delay, filter lag and best-alignment shift are separate quantities.

Sources: Thesis Section 6.5 and Table 6.2, pp. 80-84 (PDF 94-98); Section 8.4, p. 114 (PDF 128).

Limits and evidence: Timestamp interpretation, not a new latency result. Display scheduling and actual presentation time remain unmeasured.

Supporting slide: Hidden slides 94. 94 Transport candidates Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q8.9

Question: Were the causal despiking reset and reordered object-cleaning rules validated beyond the rail experiment?

Short answer: Chapter 8 evaluates the causal exchange on the rail recording. It does not isolate the accuracy effect of either rule or validate them over a wider set of tasks. Later demonstration and filter-comparison work has a different scope and does not supply that missing controlled test.

Supporting detail: The trailing despiker accepts the next sample after three consecutive rejections so its history can restart. Object cleaning moves before causal filtering. Both are documented mechanisms. Demonstrating that the entire path runs and comparing two outputs is different from an ablation showing that each added rule improves results.

Sources: Thesis Sections 8.1-8.3, Table 8.1, pp. 107-113 (PDF 121-127); knowledge/filter_facts.md and eval/pipeline_smoothness/README.md for later replay scope.

Limits and evidence: One-recording thesis comparison. No claim that no other related replay ever existed.

Supporting slide: Hidden slides 96-97. 96 Hampel spike removal; 97 Short-gap interpolation Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### QA.9

Question: Why is non-neural processing single-threaded, and does that weaken real-time feasibility?

Short answer: Appendix B states that configuration but does not document why it was selected. The feasibility measurements apply to that workstation and configuration. They show the causal replay kept pace; they do not predict a benefit from adding threads.

Supporting detail: The workstation has a 16 core Ryzen 7950X and an RTX 3080. Detector inference uses the GPU delegate; other processing runs on CPU in a single thread as reported. Chapter 8 gives branch timing and replay throughput under these conditions.

Sources: Appendix B, Table B.1; Section 8.4; printed B1, 114; PDF 140, 128.

Limits and evidence: Parallelization can add synchronization costs; no scaling experiment or live end-to-end latency measurement is reported.

Supporting slide: Hidden slides 94-95. 94 Transport candidates; 95 Moving one frame package from Python to Unity Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### QA.16

Question: Does the live path use the same repaired pelvis translation as offline evaluation?

Short answer: No. Both paths run preparation before solving, but offline translation uses the repaired hip midpoint while the live path publishes the original midpoint. I should not claim every repaired torso input reaches the live displayed root position.

Supporting detail: Prepared hips and the tilt-reference shoulder can make the solved root constrained. That state concerns the solve; it does not change the separate fact that the live published pelvis translation uses the original hips. The distinction is explicit in Appendix G.4.

Sources: Appendix G.4; Section 8.5; printed G3, 114-115; PDF 161, 128-129.

Limits and evidence: This difference and replay feasibility do not establish a validated complete live-camera session.

Supporting slide: Main slides 23; Hidden slides 83. 23 Output states; 83 Recovery guards

## Validation and references

### Q7.1

Question: Is there independent anatomical ground truth for the reconstructed person?

Short answer: There is no independent dynamic anatomical joint reference. The human reconstruction is compared with accepted raw landmarks from the same sensing chain. Manual bracelet and watch labels provide a different visible reference, but they are not joint centres. Approximate physical arm lengths and wrist-to-marker distance are separate limited checks.

Supporting detail: The raw wrist reference precedes temporal filtering; validity checks do not establish anatomical correctness. Synthetic removal uses the unmasked model output. Natural-occlusion labels share the RGB-D measurement chain and have unquantified annotation and depth uncertainty. Calling all of these ground truth would overstate what was evaluated.

Sources: Thesis Sections 7.1, 7.3 and 7.4, pp. 85, 93, 100-106 (PDF 99, 107, 114-120); Section 6.3, p. 77 (PDF 91).

Limits and evidence: Measurement-relative reconstruction, synthetic consistency and visible-feature references; no population-level anatomical accuracy claim.

Supporting slide: Main slides 45-51; Hidden slides 68. Use the stated comparison references and conditions.

### Q7.2

Question: What do the tape-measured object segments establish about tracking accuracy?

Short answer: They compare reconstructed endpoint separations with three physical separations on two recordings. Absolute differences range from 0.53 to 2.83 cm under those conditions. They do not establish point-to-path accuracy, because the physical route is not registered into the reconstruction frame.

Supporting detail: Tables 7.1 and 7.2 include a short 3.5 cm lift, whose relative error is 15.25 and 24.18 percent. Its endpoints are single transition samples. The stated sensitivity ranges retain the sign pattern, but the wider ten-sample boundary sweep reverses one sign in each recording. Scatter about a fitted line is a different, internal consistency statistic.

Sources: Thesis equation (7.1), Tables 7.1-7.2 and Section 7.2, pp. 86-92 (PDF 100-106); writing/v9/audit_evidence/ch7_restructured/object.json.

Limits and evidence: Physical scalar-length comparison, not a universal centimetre-level tracking bound. Tape resolution is not a complete uncertainty budget.

Supporting slide: Main slides 45-46; Hidden slides 69. 45 Object reconstruction; 46 Object tracking: endpoint reference table; 69 Object endpoint lengths

### Q7.3

Question: How were the 102 rail frames selected, and what does their rendered error represent?

Short answer: They are the intersection of the saved Unity capture and the valid-landmark conditions. The pinned evidence contains 487 captured rail frames, of which 102 qualify for this comparison. The result describes that incomplete subset, including its constrained root and held twist.

Supporting detail: human.json lists the retained frame IDs and their root state. The thesis specifies observed, finite, positive-depth inputs with no filling or rejection and accepted landmark checks. It does not establish why the capture lacks other times. The handover likewise has 938 captured frames, with separate retained sets of 650 right and 589 left frames.

Sources: Thesis Sections 7.3-7.3.2, pp. 92-97 (PDF 106-111); writing/v9/audit_evidence/ch7_restructured/human.json, captured_frames and joints.*.frames.

Limits and evidence: Captured subset, not a complete or uniform task sample. Do not infer whole-recording performance from it.

Supporting slide: Main slides 47-48; Hidden slides 70. 47 Model and rendered rig; 48 Body and rig: joint-results table; 70 Matched model and rig

### Q7.4

Question: What explains the difference between the kinematic wrist and the rendered wrist errors?

Short answer: The matched-frame comparison places the additional discrepancy after the kinematic model, somewhere in the display and rig path. The thesis does not isolate an individual cause. It would be incorrect to blame one stage or subtract the reported medians to estimate its error contribution.

Supporting detail: On the same handover frame sets the model medians are 0.83 and 2.34 cm and the rig medians are 5.5 and 6.8 cm. The rail's 11.4 cm rendered median has different frames and output states, so it is not another matched model-versus-rig pair. A staged comparison could investigate mapping and display effects, but no such ablation is reported.

Sources: Thesis Sections 7.3.1-7.3.2, pp. 94-97 (PDF 108-111); Table 9.1, p. 120 (PDF 134); human.json and bare_model.json.

Limits and evidence: Failure location established; root cause unresolved. Historical D-058/D-066 diagnostics are not a decomposition of these thesis errors.

Supporting slide: Main slides 47-48; Hidden slides 70. 47 Model and rendered rig; 48 Body and rig: joint-results table; 70 Matched model and rig

### Q7.5

Question: Is the approximately 1 cm model-wrist agreement with its own landmark input an independent accuracy result?

Short answer: No. It measures consistency of the reconstructed chain with the accepted raw wrist from the same sensing system. The model imposes calibrated lengths and state rules, so agreement is not automatic, but it still does not measure anatomical accuracy.

Supporting detail: Across the full valid-landmark handover populations, the median is 1.03 cm for each arm, with 1156 right and 1095 left frames. The captured subset has different medians and different held-twist coverage. Appendix H verifies the solver against exact constructed references; it does not supply independent human ground truth for these recordings.

Sources: Thesis Section 7.3.2, p. 97 (PDF 111); writing/v9/audit_evidence/ch7_restructured/bare_model.json, recording_wide_accepted/vs_raw_measured.

Limits and evidence: Model consistency against a shared measurement chain. Do not attribute every residual difference solely to one hold rule.

Supporting slide: Main slides 47-48; Hidden slides 70. 47 Model and rendered rig; 48 Body and rig: joint-results table; 70 Matched model and rig

### Q7.6

Question: What statistical weight does the natural-occlusion comparison carry with 16 left and four right labelled frames?

Short answer: It is a descriptive comparison on small, selectively visible samples. Object assistance is closer to the right-wrist labels on those four frames and is worse on the left set. The results do not establish a general method ranking or statistical significance.

Supporting detail: Table 7.9 reports right-arm medians of 5.2 cm for assistance, 11.4 for the plain solve and 17.6 for hold-last; left-arm medians are 13.1, 12.3 and 12.7 cm. The clean-label samples are only three left and four right frames. Their separations are not uncertainty bounds that can be subtracted from, or used to declare significance for, the failure results.

Sources: Thesis Tables 7.8-7.9 and closing limitations, pp. 103-106 (PDF 117-120); writing/v9/audit_evidence/ch7_restructured/natural.json.

Limits and evidence: Manual visible-feature reference; repeated-click and depth uncertainty unquantified. Frames are not independent subjects or trials.

Supporting slide: Main slides 50-51; Hidden slides 72. 50 Right-arm recovery: selected frame and aggregate; 51 Left-arm recovery: selected frame and aggregate; 72 Natural tracking failures

### Q7.7

Question: What does the synthetic-removal experiment establish when no method wins all three windows?

Short answer: It shows a window-dependent trade-off under a controlled removal of solver inputs. No method is best for every joint and motion window. The three windows are portions of one recording, so this is not evidence for a population ranking.

Supporting detail: The windows each contain 45 frames and were selected by wrist excursion before scoring. Removal occurs after offline filtering, with a measured shoulder and torso and an established frozen grasp offset. Object assistance lowers the maximum wrist deviation in the two more active windows but increases elbow deviation in the most active one. Preselection limits choosing by outcome; it does not remove eligibility or sampling bias.

Sources: Thesis Section 7.4.1, equation (7.6), Tables 7.5-7.7, pp. 100-102 (PDF 114-116); writing/v9/audit_evidence/ch7_restructured/synthetic.json.

Limits and evidence: Deviation from an unmasked model reference, not anatomical error or raw-sensor dropout performance. No inferential significance claim is made.

Supporting slide: Main slides 49; Hidden slides 71. 49 Recovery evaluation: controlled landmark removal; 71 Controlled removal

### Q7.8

Question: Could frame exclusions make the recovery evidence look more favourable than all real occlusions?

Short answer: Yes, the retained samples limit the scope of the result. Natural failures must leave the bracelet or watch visible for labelling, and every labelled frame has a detected marker. The comparison therefore does not cover failures in which both the wrist feature and marker disappear.

Supporting detail: The object-route comparisons exclude 11 rail and 12 handover frames for missing, filled or non-finite observations, not for large error. The loop's 41 undetected-marker frames are concentrated in the transfer. The thesis states these coverage limits; that transparency does not establish that the samples are representative or free of selection effects.

Sources: Thesis Sections 7.2.1-7.2.2 and 7.4.2, pp. 87, 90, 102-106 (PDF 101, 104, 116-120); object.json, loop_detection.json and natural.json.

Limits and evidence: Conditional recorded coverage. Do not generalize the labelled comparison to all occlusion frames.

Supporting slide: Main slides 50-51; Hidden slides 72. 50 Right-arm recovery: selected frame and aggregate; 51 Left-arm recovery: selected frame and aggregate; 72 Natural tracking failures

### Q7.9

Question: What can the approximately 16 cm wrist-to-marker tape check validate?

Short answer: It is an approximate check of one scalar separation during a normal single-hand grip. It supports the reported separation being of a similar magnitude. It does not validate the direction of the offset, each frame, anatomical wrist location or the full scene placement.

Supporting detail: The reconstructed single-hand medians are 15.77 cm on the right and 14.08 cm on the left. Transfer values are not judged against the same reference because the grip geometry changes. Agreement of one norm can coexist with errors in direction or with errors shared by both positions, so it cannot rule out every gross placement problem.

Sources: Thesis Section 7.3.3, pp. 97-100 (PDF 111-114).

Limits and evidence: Approximate physical scalar check, not independent validation of the three-dimensional recovery offset.

Supporting slide: Main slides 25-26. 25 Grasp offset; 26 Offset retention

### Q7.10

Question: How much recovery error comes from the object's unvalidated orientation?

Short answer: The thesis does not quantify that share. Orientation rotates the stored hand-object offset, so an orientation error can move the derived wrist. Without an independent orientation reference, I cannot say that this contribution is small or that another source dominates it.

Supporting detail: The wrist target depends jointly on object translation, object orientation and the stored offset. A controlled orientation reference would be needed to assess this input separately. The settled 45 mm marker scale does not provide that orientation validation.

Sources: Thesis Section 7.4.2, pp. 102-106 (PDF 116-120); Chapter 9's reference limitations, p. 119 (PDF 133); Chapter 10.1, pp. 121-122 (PDF 135-136).

Limits and evidence: Known dependence, unknown quantitative attribution. No fabricated angular error or dominance claim.

Supporting slide: Hidden slides 92. 92 ArUco vs AprilTag: what the literature reports Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q7.11

Question: What does the constrained root mean for the rail reconstruction results?

Short answer: Every retained rail frame in Table 7.3 includes a constrained root, and the right twist is held. The table evaluates that complete output state. It does not isolate a body reconstruction with a fully measured root or prove that the repaired pelvis is anatomically correct.

Supporting detail: The 858-of-900 hip rejection count comes from the causal replay and describes that run; it should not substitute for the table's own state counts. Root changes alter the frame in which arm angles are solved. The thesis has no independent pelvis reference and does not quantify the switch-on or switch-off step. A changed camera position is a proposed comparison, not a demonstrated fix.

Sources: Thesis Section 7.3.1, p. 94 (PDF 108); Section 8.3, p. 113 (PDF 127); Chapter 9 torso bullet, p. 118 (PDF 132); human.json and v2/dataset/r6b_probe_baseline.txt.

Limits and evidence: State-conditioned reconstruction and a separate causal count. Do not describe all 900 frames as identically repaired.

Supporting slide: Main slides 64. 64 Limitations

### Q9.2

Question: What experiment could help separate object sensing and calibration errors from waypoint selection, and why was it not run?

Short answer: A proposed first control is to measure fixed marker positions independently in the calibrated frame and compare repeated reconstructions at those positions. That removes moving-waypoint selection from that test. The thesis does not give a verified reason it was not performed, and this one test would not separate every source.

Supporting detail: Static trials could characterize combined sensing and calibration disagreement; controlled motion and varied calibration would still be needed to investigate the other terms. Subtracting errors from different experiments is not automatically a valid decomposition. No duration estimate or claim that a ruler alone supplies adequate registration is justified by the existing records.

Sources: Thesis Section 7.2, pp. 86-92 (PDF 100-106); final Chapter 9 first bullet and Table 9.1, pp. 116 and 120 (PDF 130 and 134).

Limits and evidence: Explicitly proposed experiment grounded in a documented missing reference. Its outcomes and author scheduling reason are unknown.

Supporting slide: Main slides 45-46. 45 Object reconstruction; 46 Object tracking: endpoint reference table

### QA.8

Question: What do exact synthetic checks and 77 measured frames establish, and why no noise Monte Carlo?

Short answer: They verify the tested kinematic mathematics. They do not establish noise robustness or anatomical accuracy. The thesis reports no Monte Carlo noise test, its cost, or a documented reason for omitting it.

Supporting detail: Six exact synthetic trajectory families are inverted to floating-point precision. The measured check uses 77 of 900 rail frames with all eight landmarks measured, all in the slide. Reconstruction agrees with measured upper-arm directions on those frames; that agreement still depends on the same imperfect inputs.

Sources: Appendix H.1-H.3, Table H.1; printed H1-H2; PDF 162-163.

Limits and evidence: The cost of realistic-noise validation and its input noise model remain unverified.

Supporting slide: Hidden slides 78. 78 Solver verification

### QA.17

Question: Do 77 clean frames and exact singular cases validate every angle or pose?

Short answer: They establish consistency only for the tested trajectories and clean measured subset. At a gimbal-lock singularity, different angle numbers can describe the same physical pose. Exact arithmetic agreement is therefore different from independent anatomical validation.

Supporting detail: Table H.1 covers root, shoulder, shoulder with torso, elbow, full arm and both arms. The measured subset checks upper-arm reconstruction and elbow-flexion ranges: right -30.8 to -14.8 degrees and left -40.4 to -15.5 degrees. It excludes frames lacking any of the eight measurements.

Sources: Appendix H.1-H.3; printed H1-H2; PDF 162-163.

Limits and evidence: No detector, depth, marker or missing-observation accuracy follows from Appendix H alone; Chapter 7 grades recovery separately.

Supporting slide: Hidden slides 78. 78 Solver verification

## Limitations and contributions

### Q1.2

Question: Which results should transfer to another subject or setup?

Short answer: The frame transformations and kinematic equations can be reused. The measured accuracy cannot be assumed to transfer. A new subject and setup require calibration and another evaluation.

Supporting detail: Segment lengths are effective landmark lengths, and the scene needs its own fixed calibration. The hip repair, visibility gate and recovery parameters have limited validation. Do not assert that all detector thresholds must be retuned; the thesis uses fixed values and has no cross-subject sensitivity study.

Sources: V9 Sections 2.2.2, 2.6 and 3.3.1, PDF pages 27-28, 33-34, 42-43; Chapter 9 final limitations bullet, PDF page 133.

Limits and evidence: V9 statement; unmeasured generalization.

Supporting slide: Main slides 64. 64 Limitations

### Q1.3

Question: Is the system accurate enough for clinical assessment?

Short answer: I have not validated that. Clinical assessment motivates the work, but this thesis does not define or test a clinical accuracy requirement.

Supporting detail: The study evaluates reconstruction of one person's desk task. A clinical claim would require application-specific requirements, an independent motion reference and a clinical validation study. Neither the object distance checks nor the manual wrist labels establish clinical suitability.

Sources: V9 Section 1.1, PDF page 15; Chapter 9 final limitations bullet, PDF page 133.

Limits and evidence: Unmeasured limit; motivation is not validation.

Supporting slide: Main slides 3. 3 Motivation

### Q1.8

Question: Why is the streamed object orientation not independently checked?

Short answer: I estimate and stream it, but the thesis has no independent orientation reference. The depth sample at a marker centre is a translation diagnostic, not an orientation measurement.

Supporting detail: Cube edges or an independently tracked rigid body could support a future check, but no such evaluation was performed. A visually plausible replay and a smooth orientation series do not establish orientation accuracy.

Sources: V9 Section 1.3 Objective 3, PDF page 19; Chapter 4 closing, PDF page 61; Appendix E.1, PDF page 151; Table E.1, PDF page 154.

Limits and evidence: V9 statement; absent independent reference.

Supporting slide: Main slides 64. 64 Limitations

### Q1.9

Question: What is new relative to the laboratory's earlier hand work?

Short answer: I extend the reconstruction to the torso and both arms, track an object independently in the same scene, and test what the object contributes when arm landmarks fail. I also integrate the streams into Unity.

Supporting detail: Earlier hand-model and Bayesian-estimation work motivate the project. The Chapter 3 model here is a closed-form geometric solve, rather than reuse of the earlier Bayesian estimator. The strongest contribution claim is the implemented combination and its measured limits, not that every component is newly invented.

Sources: V9 Section 1.1, PDF pages 15-16; Section 1.3, PDF page 19; Chapter 3 opening, PDF page 35.

Limits and evidence: V9 statement; inherited components must be acknowledged.

Supporting slide: Main slides 65. 65 Contributions

### Q1.10

Question: Why leave learned temporal recovery to future work?

Short answer: This thesis builds and evaluates an explicit geometric reconstruction. It proposes learned temporal estimation as a later addition; it does not test a learned recovery baseline.

Supporting detail: The compact temporal model is described as working alongside the kinematic chain. Three recordings of one subject provide limited independent training and evaluation material. That is a defensible scope limitation, but it does not prove learning would fail or establish the author's historical reason for deferral.

Sources: V9 Section 1.3 Objective 4, PDF page 19; Chapter 10 Section 10.2.

Limits and evidence: V9 future work; no learned-model experiment.

Supporting slide: Main slides 65. 65 Contributions

### Q9.1

Question: What positive claim remains after acknowledging the limitations?

Short answer: One calibrated RGB-D view supported an integrated upper-body and object reconstruction, with explicit states for inferred output and a causal implementation tested on recorded replay. Object information improved some missing-wrist cases and failed to improve others. The contribution includes documenting those conditions and limits.

Supporting detail: The thesis contains physical length comparisons and measurement-relative reconstruction results, so it is too broad to say it contains no accuracy evidence at all. What it does not establish is general anatomical accuracy across people and tasks. The integrated architecture and the conditional recovery result should be stated together.

Sources: Final Chapter 9, pp. 116-120 (PDF 130-134); Section 10.1, pp. 121-122 (PDF 135-136).

Limits and evidence: Feasibility on tested recordings plus condition-specific evaluation.

Supporting slide: Main slides 65. 65 Contributions

### Q9.3

Question: Why not replace the effective landmark lengths with anatomical lengths or correct the elbow position?

Short answer: That would change the calibration and model being evaluated. The thesis deliberately uses each recording's landmark geometry and reports its difference from anatomical measurements. A revised anatomical model could be tested, but these results do not show its effect or justify a fixed-ratio elbow correction.

Supporting detail: Table 9.1 records the different segment split and an elbow landmark 5.9 cm farther along the arm on the rail recording. That is not a measured change in the person's anatomy. Reachability depends on the shoulder-wrist distance and the full model, not one observed segment alone.

Sources: Thesis Section 6.3, pp. 76-77 (PDF 90-91); final Chapter 9 person-object bullet and Table 9.1, pp. 117 and 120 (PDF 131 and 134).

Limits and evidence: Effective-length design choice; untested anatomical recalibration.

Supporting slide: Main slides 47-48. 47 Model and rendered rig; 48 Body and rig: joint-results table

### Q9.5

Question: Was the rail-induced hip occlusion avoidable by raising the camera, and why was the task not repeated that way?

Short answer: The recording shows the hips taking depth from an occluding surface, and the reconstruction repairs that input. The thesis does not test a raised-camera comparison or document why one was not recorded. I cannot claim that a camera move would eliminate the problem without measuring it.

Supporting detail: Changing viewpoint could alter visibility but also the other body and marker observations. A measured-root comparison would be useful proposed work. The existing result concerns the controlled setup and its constrained output, with no independent pelvis reference. The 858 right-hip rejections are from the archived causal replay, not a universal count for every pipeline.

Sources: Thesis Section 7.3.1, p. 94 (PDF 108); Section 8.3, p. 113 (PDF 127); Chapter 9 torso bullet, p. 118 (PDF 132); v2/dataset/r6b_probe_baseline.txt.

Limits and evidence: Observed occlusion; alternative camera placement and the author's reason remain unverified.

Supporting slide: Main slides 64. 64 Limitations

### Q9.6

Question: Which error group dominates: observability, measurement quality or retained state?

Short answer: The thesis does not quantify a general ranking of those groups. It identifies mechanisms and a larger rendered discrepancy on matched handover frames, but it does not decompose that discrepancy or the natural-failure errors into independent contributions.

Supporting detail: The paired model-versus-rig comparison locates an additional discrepancy downstream of the solve. It does not show that display error dominates all recordings or that state estimation dominates every failure. Missing anatomical and orientation references, coupled stages and different frame sets prevent a verified numerical attribution.

Sources: Thesis Section 7.3.2, pp. 96-97 (PDF 110-111); Chapter 9 model-limits bullet and Table 9.1, pp. 118 and 120 (PDF 132 and 134).

Limits and evidence: Mechanism taxonomy and localized discrepancy, not a measured error budget.

Supporting slide: Main slides 60-62. 60 Object tracking: results and limits; 61 Body and rig: results and limits; 62 Recovery: results and limits

### Q9.7

Question: Why was the causal path not evaluated using the same physical and manual references as Chapter 7?

Short answer: That is a remaining evaluation gap. Chapter 8 establishes replay performance and compares processing paths, while Chapter 7 evaluates the offline reconstruction. The thesis does not document a reason for omitting the corresponding causal accuracy evaluation, so I should not invent one.

Supporting detail: A proposed follow-up would define comparable frame sets, references, receiver configuration and timing before evaluating causal output. It is not necessarily a simple rerun because causal filtering, initialization, output states and renderer configuration differ. Later qualitative replay films do not fill the missing matched evaluation.

Sources: Thesis Sections 7.1 and 8.3-8.5, pp. 85 and 111-115 (PDF 99 and 125-129); Section 6.3, pp. 77-78 (PDF 91-92); presentation/defense_2026/MEDIA_PROVENANCE.md.

Limits and evidence: Verified separation of experiment scopes; future comparison not performed here.

Supporting slide: Main slides 55-58. 55 Real-time pipeline; 56 Causal processing; 57 One Euro adaptive smoothing; 58 Replay timing

### Q9.8

Question: What clinical use has been established by the current system?

Short answer: No clinical use or clinical measurement accuracy was established. Clinical assessment motivates the work, but the evaluation uses one person performing controlled tasks. The system provides research reconstructions and visible output states, which are not clinical confidence or validity guarantees.

Supporting detail: A clinician-facing application would need an appropriate reference, relevant participants and tasks, validated error tolerances and a complete deployment study. The object segment results cannot be turned into a general promise to read clinical trajectories within a few centimetres. The present demonstrations show the reconstruction and its limitations.

Sources: Thesis Chapter 9 scope bullet, p. 119 (PDF 133); Section 10.1, pp. 121-122 (PDF 135-136); Chapter 1 motivation (read by the methods shard).

Limits and evidence: Potential application, not a tested clinical result.

Supporting slide: Main slides 3. 3 Motivation

### Q10.1

Question: Is experimental characterization justified with one person and three recordings?

Short answer: It is a characterization of the tested tasks and references, not of the population or every bimanual task. The thesis documents an integrated system, condition-specific results and failure cases. The contribution should be stated with that scope attached.

Supporting detail: The conclusion explicitly limits the evaluation to one person, three controlled recordings, an unregistered physical route and a causal replay. Later presentation footage is separate evidence and does not increase the subject count of the thesis experiment. The claim should remain feasibility and identified conditions, not general anatomical accuracy.

Sources: Thesis Section 10.1, pp. 121-122 (PDF 135-136); final Chapter 9, pp. 119-120 (PDF 133-134).

Limits and evidence: Scoped contribution.

Supporting slide: Main slides 65. 65 Contributions

### Q10.2

Question: In what sense is a recovery layer needed when the only view loses required measurements?

Short answer: If the system must keep producing a pose after required measurements disappear, it has to infer, retain or otherwise supply the missing information. It could instead report that pose as unavailable. This argument does not prove that the particular object-assisted method is necessary or always effective.

Supporting detail: The thesis compares several options, including hold-last, direction memory and object assistance. Their mixed results show why continuity and accurate reconstruction are separate goals. The final conclusion calls recovery a needed part of this system.

Sources: Thesis Section 10.1, p. 121 (PDF 135); Sections 7.4.1-7.4.2, pp. 100-106 (PDF 114-120).

Limits and evidence: Conditional architectural reasoning, not a universal experimental necessity proof.

Supporting slide: Main slides 23-24. 23 Output states; 24 Holding context

### Q10.3

Question: Which proposed improvement would help most: extra views, a stronger detector or learned recovery?

Short answer: The thesis does not test those alternatives, so it cannot rank their gains. They target different limitations: visibility, measurement quality and the use of retained state. Choosing among them requires a comparison under the same task and reference conditions.

Supporting detail: Section 10.2 proposes all three without measured improvements. The thesis leaves display-path discrepancies unisolated and does not establish which upgrade would reduce the largest human-side error. No scheduling explanation for the omitted experiments is established by the thesis.

Sources: Thesis Section 10.2, p. 122 (PDF 136); Chapter 9 model-limits bullet and Table 9.1, pp. 118 and 120 (PDF 132 and 134).

Limits and evidence: Future-work proposals, not comparative results or a verified priority ranking.

Supporting slide: Main slides 65. 65 Contributions

### Q10.4

Question: Would RTMPose fix the high-confidence elbow-on-hand failure?

Short answer: That is an untested possibility, not an established improvement. A stronger detector could reduce some misplaced landmarks, but it does not create a direct measurement of a body part hidden from the only camera. The geometric checks would still have a role.

Supporting detail: Figure 9.2 shows a usable-confidence landmark on the wrong body part. Section 10.2 proposes RTMPose-m with COCO-17 and ONNX Runtime. This work does not provide a detector comparison for that example or prove that a replacement integrates without changes to landmark mapping, thresholds or timing.

Sources: Thesis Figure 9.2 and surrounding bullet, p. 118 (PDF 132); Section 10.2, p. 122 (PDF 136).

Limits and evidence: Observed failure plus proposed replacement. No external model-performance claim is added.

Supporting slide: Main slides 64. 64 Limitations

### Q10.5

Question: What supports the statement that a better detector or more views alone would not remove every error?

Short answer: The argument is based on the different mechanisms, not on a detector or multi-camera ablation. A detector still lacks direct observations behind an occluder, while a system may retain outdated offsets or held states even with additional inputs. The thesis does not quantify either proposed upgrade.

Supporting detail: Chapter 8 shows initialization-dependent states persisting after observations return; Chapter 7 shows mixed recovery outcomes. Extra views might help prevent or correct some state errors, so it would be too strong to say they can never help. The defensible claim is that adding observations does not itself validate or redesign every state-update rule.

Sources: Thesis Section 8.3, pp. 112-113 (PDF 126-127); Chapter 9 limits bullet, p. 118 (PDF 132); Section 10.1, p. 121 (PDF 135).

Limits and evidence: Mechanistic interpretation with explicit limits; no causal effect size for an untested upgrade.

Supporting slide: Main slides 64. 64 Limitations

### Q10.6

Question: Are the claims of smooth playback and operation near the recorded frame rate supported?

Short answer: The replay frame-rate claim is supported on the stated workstation. Chapter 8 does not provide a perceptual smoothness score or sensor-to-screen latency. A configured display smoother and a regular merger cadence do not by themselves establish smooth or accurate motion.

Supporting detail: The archived run reports frame coverage, compute times and merger cadence; its output is still a recorded replay. Later filter and pipeline-smoothness studies quantify specific recorded signal properties under their own conditions, not the complete thesis avatar's perceived motion. Those supplementary results must not be presented as if they were the thesis's missing smoothness measurement.

Sources: Thesis Section 8.4, p. 114 (PDF 128), and Section 10.1, pp. 121-122 (PDF 135-136); v2/dataset/r6b_probe_baseline.txt; eval/pipeline_smoothness/README.md; presentation/defense_2026/experiments/filter_metrics/README.md.

Limits and evidence: Measured replay performance; qualitative display language; separate later signal metrics.

Supporting slide: Hidden slides 102-103. 102 Why Butterworth offline; 103 Why One Euro in real time Later demonstrations, literature and benchmarks are supplementary; they do not replace final-thesis evidence.

### Q10.7

Question: What concrete result illustrates the value of integrating the body and object branches?

Short answer: On the four retained right-wrist failure frames, the object-assisted reconstruction is closer to the manual wrist label than the plain solve or hold-last. That illustrates how object information can help when body landmarks fail. The left-wrist result shows that the benefit is conditional.

Supporting detail: Table 7.9 gives medians of 5.2, 11.4 and 17.6 cm for object assistance, plain solve and hold-last on the right. The same method is worse on the left set. The integration also puts both outputs in one scene and carries measured, held and constrained states. This is a concrete systems example, not proof that integration always improves accuracy.

Sources: Thesis Table 7.9, p. 105 (PDF 119); Section 10.1, p. 121 (PDF 135); writing/v9/audit_evidence/ch7_restructured/natural.json.

Limits and evidence: Small visible-feature comparison and demonstrated architecture.

Supporting slide: Main slides 50-51; Hidden slides 72. 50 Right-arm recovery: selected frame and aggregate; 51 Left-arm recovery: selected frame and aggregate; 72 Natural tracking failures
