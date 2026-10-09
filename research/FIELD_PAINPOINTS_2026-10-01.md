# Field pain points, step 2b: what the datasets, benchmarks, surveys, position papers and challenge reports say the field cannot do (2026-10-01)

Source: full-text reading of the group-A rows of the inventory (type dataset, benchmark, survey or position, plus challenge reports and workshop papers; 292 rows) and 4 group-B rows that shared the last batch, by workflows wf_103bef28-969 and wf_3fc525c6-ac8 (37 agents, 8 papers each). Papers: 296; full text read for 284, partial for 4, abstract only for 8. Items: 1286 stated limitations with verbatim quotes, 1761 listed open problems, 713 benchmark gaps, 1255 restrictive assumptions. The JSON companion field_painpoints_2026-10-01.json holds every item with its quote and section. Method and system papers of the core subfields (group B, 940 rows) were not read in full at the author's decision of 2026-10-01 (cost); their abstracts and contributions remain in the inventory.

Each entry: the paper, the source read, the one-sentence capability the paper implies the field lacks, then its stated limitations (paraphrase; the quote and section are in the JSON), listed open problems and benchmark gaps.

## [1] 3D Human Pose Perception from Egocentric Stereo Videos (CVPR 2024, method, S4)
Source: https://arxiv.org/html/2401.00889; confidence HIGH.
Field cannot yet: Estimate accurate lower-body 3D pose from real head-mounted egocentric stereo under heavy self-occlusion; real-world errors stay near 7 to 10 cm.
Stated limitations:
- With eyeglasses-based cameras, the 3D scene and camera poses cannot always be estimated because of severe self-occlusion, leaving invalid depth values. [1 Introduction]
- When the body fills most of the egocentric video, scene reconstruction or camera pose estimation fails. [4.3 3D Scene Reconstruction]
- Naively adding depth to a CNN 3D module does not help, likely because invalid depth values corrupt it. [5.3 Ablation Study]
- Synthetic pre-training helps despite fisheye distortion differences and syn-to-real domain gaps between synthetic and real setups. [5.3 Synthetic Data for Pre-training]
Benchmark gaps:
- UnrealEgo-RW (real world) / device-relative MPJPE (mm): 104.14 mm when trained from scratch (72.89 mm with UnrealEgo2 pre-training) versus 30.53 mm on synthetic UnrealEgo2, a large synthetic-to-real gap.
- UnrealEgo-RW / per-part MPJPE (mm): Foot MPJPE 155.86 mm and lower-body 130.97 mm versus upper-body 77.85 mm.
Restrictive assumptions: Head-mounted stereo fisheye cameras with known 12 cm baseline; SfM over 4 s windows of frames (Metashape) to obtain scene depth, i.e. windowed offline processing; Real-world data captured in a multi-view motion capture studio for ground truth; Virtual character animation used ground-truth camera poses; Large-scale synthetic training data (UnrealEgo2) for pre-training

## [3] 6D-Diff: A Keypoint Diffusion Framework for 6D Object Pose Estimation (CVPR 2024, method, S5)
Source: https://arxiv.org/html/2401.00029 (arXiv id found via title; row had none); confidence HIGH.
Field cannot yet: Estimate 6D pose of small, heavily occluded objects from RGB without a known CAD model at high accuracy.
Stated limitations:
- Occlusion, clutter and changing environments persist as challenges that introduce noise and indeterminacy into pose estimation. [1 Introduction]
- Directly applying diffusion models to pose is difficult because they start denoising from random Gaussian noise. [1 Introduction]
Benchmark gaps:
- LM-O / ADD(-S): Mean 79.6; ape 60.6, cat 63.2, duck 67.2 remain low under heavy occlusion.
- YCB-V / ADD(-S) / AUC of ADD-S: ADD(-S) 83.8; AUC of ADD-S 91.5 is only comparable to, not above, the best prior (GDR-Net 91.6).
Restrictive assumptions: Object 3D CAD model known; 128 3D keypoints pre-selected on it; Single RGB image; external 2D detector (Faster RCNN / FCOS from CDPNv2) supplies the object bounding box; Training uses real plus physically-based rendered (pbr) images of the specific objects; Iterative diffusion inference (10 DDIM steps, 5 sampled sets) plus PnP solver; no runtime reported; Rigid objects only

## [4] A Simple Baseline for Efficient Hand Mesh Reconstruction (CVPR 2024, method, S1)
Source: https://arxiv.org/html/2403.01813; confidence HIGH.
Field cannot yet: Reconstruct hand meshes robustly under object occlusion, self-occlusion and hand interactions with an efficient single-hand model.
Stated limitations:
- No targeted optimization was performed, so failure cases from previous work, concentrated in self-occlusion and object occlusion, remain challenging. [4 Experiments, Limits and Failure cases]
- The method is designed for single-hand gestures; extreme lighting, occlusion, interactions and out-of-distribution cases show no improvement. [5 Conclusion and Future Work]
- Some failures come from very small visible hand area, others from ambiguity caused by occlusion. [Figure 8 caption]
Benchmark gaps:
- DexYCB / MPJPE vs PA-MPJPE (mm): Root-relative MPJPE 12.4 mm and MPVPE 12.1 mm remain more than double the Procrustes-aligned 5.5 mm, showing remaining global pose and scale error under object occlusion.
Restrictive assumptions: Single RGB image of a single hand (cropped); No temporal information; No object or two-hand interaction modelling; Speed measured on a 2080 Ti GPU at batch size one

## [5] A Unified Diffusion Framework for Scene-aware Human Motion Estimation from Sparse Signals (CVPR 2024, method, S4 S7)
Source: https://arxiv.org/html/2404.04890; confidence HIGH.
Field cannot yet: Estimate full-body motion including fine hand-object interaction from sparse AR/VR signals, and without a pre-scanned scene.
Stated limitations:
- The method fails to capture fine-grained hand-object interactions such as picking up clothes or wiping a blackboard. [Appendix, Failure cases and analysis]
- Scene-penetration and phase-matching guidance losses improve accuracy but can introduce jitter. [4.3 Ablation Study]
- Limited volume of paired motion-scene data makes generated motion less diverse and unrealistic with a plain conditional diffusion model. [3 Method]
- Tracking signals come only from the upper body, so correlated lower-body motion is hard to generate. [3 Method]
Benchmark gaps:
- GIMO / MPJPE (mm) / lower-body PE (mm): MPJPE 57.8 mm and lower-body PE 107.9 mm, versus 19.2 mm MPJPE on CIRCLE.
- CIRCLE / lower-body PE (mm): Lower-body PE 57.3 mm versus hand PE 8.8 mm.
Restrictive assumptions: Pre-acquired 3D scene geometry (scene point cloud or mesh) is available; Global translation from the HMD used to crop the scene around the person; Three 6D trackers (head and both hands) providing accurate translation and rotation; Only the first 22 SMPL joints are modelled (no hand articulation); Trained and evaluated on CIRCLE (mocap in artist-created virtual scenes) and GIMO

## [8] BOTH2Hands: Inferring 3D Hands from Both Text Prompts and Body Dynamics (CVPR 2024, dataset, S3 S2)
Source: https://arxiv.org/html/2312.07937; confidence HIGH.
Field cannot yet: The field cannot yet generate or evaluate temporally controlled, contact-aware two-hand interaction motion with metrics that reflect hand-specific alignment.
Stated limitations:
- Text control gives spatial detail but has no temporal alignment with the motion. [Appendix D Limitation]
- The body is treated as a whole; the separate influence of individual body parts on the hands is not modelled. [Appendix D Limitation]
- Metrics that capture alignment between hand, body, text and other conditions are missing. [Appendix D Limitation]
- The method cannot reliably decide whether a two-hand interaction gesture is produced when the wrists come close. [Appendix D Limitation]
- Standard single-condition metrics such as R-precision are insensitive to multi-condition hand generation; improvements look marginal. [5.1 Methods Evaluation]
- Dataset ground truth comes from off-the-shelf markerless multi-view capture with measurable error against triangulated manual labels. [Appendix A Data quality]
- Data scarcity for two-hand motion generation persists and multimodal annotation is a barrier. [1 Introduction]
Open problems listed:
- Temporal alignment of text control with hand motion.
- Per-body-part influence on hands.
- Hand-to-hand interaction detection and generation when wrists are close.
- Metrics for multi-condition (hand, body, text) alignment.
- Data scarcity and annotation cost for two-hand motion with multimodal labels.
- Improving tracking quality of the released raw captures.
Benchmark gaps:
- BOTH57M test / R-Precision Top-3: All methods cluster near the real-data value (0.104-0.115 vs Real 0.109), so the metric cannot separate methods; authors call the improvements marginal.
- BOTH57M annotation subset / MPJPE: Ground-truth annotation error 31.4 mm overall and 6.51 mm for hands against triangulated manual 2D labels.
Restrictive assumptions: 32-camera RGB dome (some zoomed on hands) at 3840x2160, 59.97 FPS, with three 5500 W fill lights to capture hands.; Ground truth from off-the-shelf multi-view markerless mocap, not markers.; Gestures from a gesture dictionary without manipulated objects; no hand-object interaction.; Generation requires the full body motion sequence as input; offline diffusion.

## [20] DiVa-360: The Dynamic Visual Dataset for Immersive Neural Fields (CVPR 2024, dataset, S1 S7)
Source: https://arxiv.org/html/2307.16897; confidence HIGH.
Field cannot yet: The field cannot yet reconstruct long-duration hand-object interaction scenes with dynamic neural fields that are fast, temporally consistent, and accurate on hands and fine detail.
Stated limitations:
- Evaluation covers images only; audio and text are not evaluated. [6 Conclusion, Limitations and Future Work]
- The capture system is limited to table-scale scenes. [6 Conclusion, Limitations and Future Work]
- Slow training of state-of-the-art methods prevents more baselines or longer-video metrics. [6 Conclusion, Limitations and Future Work]
- Radiance fields cannot handle reflections from the glass panel, so 12 views are dropped. [5.1 Benchmark Comparisons]
- Dynamic methods appear unable to exploit high-resolution images. [5.2 Experimental Analysis]
- Foreground segmentation misses small, transparent, highly reflective or white objects. [Supplementary 5, Failure Cases]
- Text descriptions come from one annotator; bias acknowledged. [Supplementary 7]
Open problems listed:
- Training and rendering speed of dynamic neural fields.
- Hardware requirements.
- Imbalanced capacity between static and dynamic components.
- Use of temporal information.
- Use of spatial (high-resolution) information.
- Long-duration (minutes to hours) dynamic scene capture.
- Reflections and transparent or thin objects.
- Modelling complex hand dynamics and hand occlusion in hand-object interaction.
- Capture beyond table scale.
- Evaluation beyond images (audio, text).
Benchmark gaps:
- DiVa-360 dynamic / PSNR / train time: PF I-NGP 28.31 dB, MixVoxels 27.68 dB, K-Planes 26.39 dB; training 48-58 s per frame.
- DiVa-360 interaction vs object / PSNR: Interaction sequences lower than object sequences by 2.73 dB (PF I-NGP), 1.98 dB (MixVoxels), 0.44 dB (K-Planes).
- DiVa-360 resolution study / PSNR: Training at higher resolution does not improve MixVoxels or K-Planes (K-Planes 25.38 dB at 1160x550 vs 26.03 dB at 464x220).
Restrictive assumptions: 53 synchronized RGB cameras in a 360-degree enclosure.; Table-scale scenes only, objects centred in the capture volume.; Per-scene optimization over 5-second chunks; over 500 GPU-days for the benchmark.; Segmentation relies on objects being near the centre of the rig.

## [23] EgoExoLearn: A Dataset for Bridging Asynchronous Ego- and Exo-centric View of Procedural Activities in Real World (CVPR 2024, dataset, S6)
Source: https://arxiv.org/html/2403.16182; confidence HIGH.
Field cannot yet: The field cannot yet transfer procedural knowledge from an exocentric demonstration to an egocentric execution recorded elsewhere and at another time.
Stated limitations:
- Current models are limited at associating activities across views. [4.2.1 Cross-view association]
- Adding exocentric reference gives only marginal gains in skill assessment. [4.2.3 Cross-view referenced skill assessment]
- No paired training data is provided for association; unpaired modelling left open. [4.2.1 Cross-view association]
- Zero-shot recognition is worse on egocentric than exocentric video. [S6.6.3 Zero-shot action recognition]
- Egocentric gaze glasses recorded variable frame rates due to overheating, requiring resampling to 25 fps. [Supplementary, data processing]
Open problems listed:
- Cross-view association of asynchronous ego and exo activities.
- Cross-view association from unpaired training samples.
- Cross-view action anticipation and planning across different environments.
- Cross-view referenced skill assessment.
- Cross-view referenced video captioning.
- Cross-view action segmentation.
- Zero-shot cross-view action recognition (ego worse than exo).
- How to leverage gaze and hand-associated annotations.
- Length mismatch between edited demonstrations and full egocentric executions.
- Sim-to-real generalization; combined multiview datasets of inferior quality or scale (intro).
Benchmark gaps:
- EgoExoLearn test / Cross-view association accuracy: Best co-trained model with gaze reaches 55.3 (Ego2Exo) and 51.1 (Exo2Ego); zero-shot models 21.7-33.3 vs random 13-14.
- EgoExoLearn test / Cross-view anticipation Top-5 recall: Cross-view results mostly 25-56; zero-shot transfer across views is the lowest.
- EgoExoLearn / Skill assessment ranking accuracy: Adding exo reference yields only marginal gains (about 79-84%).
Restrictive assumptions: Gaze cue requires eye-tracking glasses worn by the participant.; Videos only; no 3D pose or object annotations used in the benchmarks.; Demonstration videos are edited and shorter than the egocentric executions.

## [29] FreeMan: Towards Benchmarking 3D Human Pose Estimation under Real-World Conditions (CVPR 2024, dataset, S4)
Source: https://arxiv.org/html/2309.05073; confidence HIGH.
Field cannot yet: The field cannot yet produce 3D human pose estimators and annotation pipelines that generalize from lab capture to varied real-world scenes and moving cameras.
Stated limitations:
- Error-pose detection depends on image generation models and prompt tuning. [7 Conclusion, Limitations]
- Annotations are 17 COCO body keypoints, not whole body. [Supplementary 2 Limitations and Future Work]
- The dataset size is limited and many real-world conditions remain unexplored. [Supplementary 2 Limitations and Future Work]
- Aligning and annotating data from movable cameras is unsolved. [1 Introduction]
- Chessboard calibration alone is not accurate enough and needs dense-matching refinement. [4.1 Hardware Setup]
Open problems listed:
- Insufficient scene diversity in existing datasets (lighting, background).
- Limited actions and body scales from fixed cameras.
- Restricted scalability of manual annotation.
- Aligning and annotating data from movable cameras.
- Whole-body keypoint annotation.
- Human rendering under natural lighting; dynamic 3D Gaussian splatting.
- Further real-world variables beyond those captured.
Benchmark gaps:
- FreeMan in-domain / MPJPE (SimpleBaseline): 79.22 mm on FreeMan vs 53.4 mm on Human3.6M.
- FreeMan cross-domain / MPJPE@500mm (VoxelPose trained on Human3.6M): Zero AP below 100 mm; 103.02 mm even with ground-truth root.
- FreeMan neural rendering / PSNR (HumanNeRF): Ranges from 30.11 dB down to 23.86 dB across 10 scenes.
Restrictive assumptions: 8 synchronized smartphone views with chessboard calibration per session.; Ground truth from triangulated 2D detector keypoints (HRNet) plus smoothing, not marker mocap.; Body keypoints only (17 COCO joints), no hands or objects.; Synchronization error under one frame (33 ms at 30 FPS).

## [37] HOI-M^3: Capture Multiple Humans and Objects Interaction within Contextual Environment (CVPR 2024, dataset, S2)
Source: https://arxiv.org/html/2404.00299; confidence HIGH.
Field cannot yet: The field cannot yet capture several humans manipulating several objects accurately in 3D without dense camera domes, object-mounted IMUs and manual correction.
Stated limitations:
- Indoor only due to hardware cost; outdoor and in-the-wild extension is non-trivial. [5.3 Limitations]
- Only five scenes because of human effort. [5.3 Limitations]
- Fixed illumination and few backgrounds limit generalization. [5.3 Limitations]
- No tracking-specific ground truth; tracking evaluation is qualitative. [Appendix, tracking ablation]
- IMU drift and calibration errors degrade object tracking over time. [3.5 Inertial-aid Multi-object Tracking]
- No strong object keypoint detectors; masks are the main object evidence. [3.5 Inertial-aid Multi-object Tracking]
- Accurate capture is still out of reach even with dense multimodal input. [1 Introduction]
Open problems listed:
- Multi-person pose and shape estimation under object occlusion.
- Monocular multiple HOI capture (limited progress to date).
- Multi-view multiple HOI capture.
- Multiple human motion generation.
- Multiple interaction generation.
- Outdoor and in-the-wild capture.
- Scene and illumination diversity.
- Accurate capture without dense cameras, IMUs and manual correction.
Benchmark gaps:
- HOI-M3 monocular multi-HOI capture / PCKabs / PCKrel: Proposed baseline reaches only 5.9% PCKabs (3.3% matched) vs 68.5% PCKrel; object V2V 297.8 and Chamfer 235.0.
- HOI-M3 monocular HPS / MPJPE: All tested methods (HMR, SPIN, HybrIK, PARE, CLIFF) have MPJPE of 309-332 mm.
- HOI-M3 generation / Penetration: Joint generation has 9.265% penetration vs 1.452% for people alone.
Restrictive assumptions: 42 cinema cameras in a 7.8 m dome plus IMUs embedded in each pre-scanned object.; Known object templates (rigid, pre-scanned).; Manual sync by a controlled jump and manual IMU-camera offset calibration.; Indoor, fixed illumination, white backdrops; offline optimization.

## [56] MMVP: A Multimodal MoCap Dataset with Vision and Pressure Sensors (CVPR 2024, dataset, S4)
Source: https://arxiv.org/html/2403.17610; confidence HIGH.
Field cannot yet: The field cannot yet estimate accurate dense contact and drift-free global motion from monocular video under fast motion and moving cameras.
Stated limitations:
- Designed for static viewpoints; moving cameras remain hard. [6 Conclusion, Limitations and future work]
- Scenes are homogeneous, preventing scene generalization. [6 Conclusion, Limitations and future work]
- Insole and camera cannot be synchronized automatically. [3.1 Data Collection]
- Single-frame contact perception is hard. [5.2 Comparison of Foot Contact Estimation]
- Visual threshold contact labels inherit pose, shape and scene-scan errors. [1 Introduction]
Open problems listed:
- Accurate dense contact annotation without visual thresholding errors.
- Vision-pressure data for large-range fast motion.
- Handling moving cameras.
- Scene generalization beyond homogeneous scenes.
- Learning dynamics from pressure alone.
Benchmark gaps:
- MMVP test / Foot contact F1 / IoU: Best method reaches only 0.532 F1 and 0.522 IoU.
- MMVP / MPJPE / Traj: Best MPJPE 83.0 mm; trajectory error 129.3 mm vs 211.4-679.7 mm for CLIFF, TRACE and SMPLer-X.
Restrictive assumptions: Single static Azure Kinect RGB-D camera at 30 Hz.; Subjects wear pressure insoles (242 sensors each).; Manual synchronization of pressure and video.; Single person on a ground plane; ground estimated by ZoeDepth at test time.; Mostly teenage subjects in homogeneous indoor scenes.

## [67] OAKINK2: A Dataset of Bimanual Hands-Object Manipulation in Complex Task Completion (CVPR 2024, dataset, S1 S3 S2 S6)
Source: https://arxiv.org/pdf/2403.19417; confidence HIGH.
Field cannot yet: The field cannot yet plan and generate long-horizon bimanual manipulation from language, nor capture it without markers and manual cleaning.
Stated limitations:
- Marker mocap fails under extreme occlusion and needs manual cleaning. [Appendix A.2 Data Cleaning]
- Close markers get mislabelled or merged. [Appendix A.2 Data Cleaning]
- No framework for end-to-end text-to-motion complex task completion; task decomposed into stages. [5.3 Complex Task Completion]
- LLM planner fails on complex tasks with many primitives. [Supplementary, Evaluations of Primitive Planning]
Open problems listed:
- End-to-end text-to-manipulation generation for complex tasks.
- Planning long-horizon tasks with many dependent primitives.
- Vision-language-action pretraining on manipulation data.
- Retargeting demonstrations to other embodiments.
- Transfer to simulation for embodied learning.
- Robust capture under marker occlusion without manual cleaning.
Benchmark gaps:
- OAKINK2 HMR single-view / RR-MPJPE: 13.08-17.56 mm; no world-space result reported for monocular methods.
- OAKINK2 HMR multi-view / MPJPE (world): POEM 9.17 mm, keypoint-based fit 19.30 mm.
- OAKINK2 Complex Tasks / Planning success rate: 36% overall; 0% for tasks with more than 5 primitives.
Restrictive assumptions: 12 OptiTrack cameras with reflective markers on upper body, both hands and objects.; Known object geometry; TaMF assumes object trajectories given or retrieved from demonstrations by an oracle.; 4 RGB views (1 egocentric, 3 allocentric); 9 subjects, 75 objects.; Manual cleaning of mocap data by three annotators.

## [75] RELI11D: A Comprehensive Multimodal Human Motion Dataset and Method (CVPR 2024, dataset, S4)
Source: https://arxiv.org/html/2403.19501; confidence HIGH.
Field cannot yet: The field cannot yet estimate fast, complex human motion with accurate global position from a single affordable sensor.
Stated limitations:
- Existing methods cannot handle rapid complex motion that needs precise location. [1 Introduction]
- All tested methods perform poorly, even multi-dataset ones. [5.2.1 Human Pose Estimation]
- Monocular methods fail on 3D global motion. [5.2.2 Global HPE]
- RGB-D has limited range; IMUs must be worn and drift. [1 Introduction]
- IMU drift over long captures forces optimization for labels. [3.2 Data Annotation Pipeline]
Open problems listed:
- Capturing rapid, complex motions with precise global localization.
- Global 3D motion from monocular RGB.
- Fusing heterogeneous sensors (RGB, LiDAR, event, IMU).
- Sensor limits: RGB light-sensitive and no depth; RGB-D short range; LiDAR sparse and low frame rate; IMU worn and drifting; event no appearance.
Benchmark gaps:
- RELI11D / MPJPE: RGB methods 171.97-249.34 mm; FusionPose (RGB+LiDAR) 136.15 mm.
- RELI11D / G-MPJPE / T-Error: GLAMR and TRACE: G-MPJPE 489-495 mm, T-Error 582-590 mm; LEIR 115.36 / 146.13 mm.
Restrictive assumptions: Ground truth requires a 17-IMU Xsens suit, LiDAR, and a laser scan of each scene.; Body shape from handheld scanning.; Sync via a jump at sequence start.; LEIR needs LiDAR, event and RGB sensors.

## [79] Scaling Up Dynamic Human-Scene Interaction Modeling (CVPR 2024, dataset, S2)
Source: https://arxiv.org/html/2403.08629; confidence HIGH.
Field cannot yet: The field cannot yet capture scalable, real-sensor human-object interaction data with mocap-level pose, object tracking and contact quality, nor generate interactions beyond the training distribution.
Stated limitations:
- The motion generator cannot produce human-object interactions outside the training distribution; unfamiliar actions yield unrealistic interactions or object intersections. [Limitation]
- Example given: climbing off a table is not generated realistically. [Limitation]
- In the introduction the authors say RGB-D recorded datasets scale better but give lower-quality human pose and object tracking than mocap. [1 Introduction]
Open problems listed:
- High-quality HSI datasets are scarce; prior datasets constrained in scalability and data quality
- Mocap datasets lack diverse and immersive HSI
- RGB-D recorded datasets have lower-quality human pose and object tracking
- Synthetic datasets fail to capture dynamic 3D contacts and object tracking
- Generating HOI behaviours beyond the training set remains unsolved
Benchmark gaps:
- PROX / Penetration / contact / discriminator success (static setting): On PROX the method's discriminator success rate is 0.903, the same as Wang et al.; contact 0.723 vs 0.992 on TRUMANS, showing much weaker results on real scanned scenes
- GRAB / Penetration (dynamic setting): GRAB-trained models show high penetration (e.g. 34.41 for the method, 44.09 GOAL), which the paper attributes to GRAB's limitation for scene-adherent HOI
- DAMON + TRUMANS / Contact recall / F1: Adding TRUMANS at 1:1 lowers DECO recall from 0.5232 to 0.4806 and F1 from 0.5115 to 0.4972, despite lower geodesic error
Restrictive assumptions: Optical VICON mocap with markers on all movable objects in a dedicated capture area; Physical placeholders manually aligned to virtual 3D-FRONT/BlenderKit scenes; RGB-D video, masks and egocentric views are synthetic renderings, not real camera footage; Only 7 actors; actors trained on placeholders and prompted with actions from a predefined pool; Generator needs scene occupancy and frame-wise action labels as input; Objects represented by known watertight meshes and URDF for articulated objects

## [88] TACO: Benchmarking Generalizable Bimanual Tool-ACtion-Object Understanding (CVPR 2024, dataset, S1 S3 S5 S6)
Source: https://arxiv.org/html/2401.08399; confidence HIGH.
Field cannot yet: The field cannot yet generalize bimanual tool-object perception, forecasting and grasp synthesis to unseen tool geometries and novel action compositions, nor capture marker-free ground truth for diverse scenes and articulated objects.
Stated limitations:
- TACO does not include articulated objects. [6 Limitations and Conclusion]
- Lacks scene diversity, which the authors note is crucial for understanding manipulation. [6 Limitations and Conclusion]
- Marker removal uses generative inpainting, so true object appearance cannot be perfectly recovered. [6 Limitations and Conclusion]
- Existing dual-hand 2D keypoint approaches can fail under severe occlusion or when the hands are far apart, requiring a custom per-hand detection pipeline. [3.2 Data Annotating]
- Markers on objects widen the appearance gap to in-the-wild objects; a tracker could learn to track markers instead of the object. [3.2 Data Annotating]
Open problems listed:
- Generalizing bimanual HOI understanding to novel object geometries, categories and unseen tool-action-object triplets
- Compositional action recognition under novel interaction contexts
- Forecasting fast, complex hand-object motion, especially for the dominant hand and tool
- Synthesizing physically plausible, cooperative grasps in multi-object scenarios for unseen geometries
- Articulated objects not covered
- Scene diversity lacking
- Realistic marker-free object appearance in mocap-annotated data
Benchmark gaps:
- TACO S4 (compound generalization) / Top-1 action recognition accuracy: AIM 39.33% and CACNF 44.00% on S4 versus 83.08% and 86.15% on S1
- TACO S1-S4 / Forecasting MPJPE (right hand) and tool rotation error: Generative baselines reach 54.9-70.5 mm right-hand MPJPE and 52.8-88.2 deg tool rotation error; best predictive models still 28.8-36.6 mm
- TACO S2/S4 (unseen tool geometry) / Grasp synthesis collision ratio: ContactGen collision ratio rises from 10.40 to 17.56 and HALO-VAE from 2.39 to 11.11 on unseen geometries
- DexYCB -> TACO cross-dataset / MPJPE (mm): CMR trained on DexYCB gives 39.54 mm MPJPE on TACO; trained on TACO gives 76.20 mm on DexYCB
Restrictive assumptions: 12 synchronized industrial cameras plus a NOKOV optical mocap system with 6 IR cameras; four markers on each object; Rigid objects only, each pre-scanned with an industrial 3D scanner (up to 100K faces); Egocentric camera is a helmet-mounted RealSense L515 tracked by mocap; Lab capture with limited scene diversity; Forecasting benchmark assumes known object point clouds and past poses; grasp synthesis assumes known meshes of both objects and the left hand

## [98] EgoPressure: A Dataset for Hand Pressure and Pose Estimation in Egocentric Vision (CVPR 2025, dataset, S1)
Source: https://arxiv.org/html/2409.02224; confidence HIGH.
Field cannot yet: The field cannot yet obtain or estimate hand contact pressure during natural manipulation of arbitrary 3D objects, especially with both hands, from egocentric cameras.
Stated limitations:
- Pressure sensing is confined to flat surfaces; arbitrary object surfaces would need hand instrumentation that hinders natural interaction and adds visible artifacts. [10 Limitations]
- Data captured only indoors; green screen overlays are used for background replacement to improve generalization. [10 Limitations]
- Only single-hand interactions are captured; bimanual use is left as an extension. [10 Limitations]
- Instrumenting objects for pressure remains open, with recent progress mostly limited to basic contact detection. [10 Limitations]
- HaMeR single-image predictions look plausible from the top but reveal inaccuracies and scale ambiguity from side views. [8.2.2 Comparison to learning-based model]
Open problems listed:
- Measuring pressure while interacting with general (non-flat) objects without instrumenting hands
- Instrumenting objects for pressure sensing
- Generalizing beyond indoor capture settings to real-world environments
- Bimanual pressure interactions
- Joint high-accuracy hand pose and pressure estimation from egocentric RGB
Benchmark gaps:
- EgoPressure unseen exocentric views (1,6,7) / Contact IoU / Volumetric IoU: PressureVisionNet drops to 36.82% contact IoU and 25.05% volumetric IoU, versus 62.11% / 44.73% on seen views; GT pose only raises it to 43.04%
- EgoPressure egocentric / Contact IoU: Egocentric contact IoU is 55.73% (RGB only), 58.80% even with ground-truth pose
- EgoPressure / Contact IoU (PressureFormer, hand-projected): Best contact IoU 43.04%; volumetric IoU 31.57%, below the HaMeR-pose baseline's 35.40%
Restrictive assumptions: Seven static calibrated Azure Kinect RGB-D cameras plus one head-mounted camera for annotation; Pressure ground truth only from a flat Sensel Morph touchpad (240 x 169.5 mm); Head-camera pose from active IR markers around the pad; Per-participant MANO shape calibration sequence; Single hand at a time, lab setting with green screen, black hand stockings up to wrist; Scripted gestures (touch, press, drag, pinch) rather than object manipulation

## [101] GigaHands: A Massive Annotated Dataset of Bimanual Hand Activities (CVPR 2025, dataset, S3 S1 S6)
Source: https://arxiv.org/html/2412.04244; confidence HIGH.
Field cannot yet: The field cannot yet automatically track articulated or non-rigid objects, or rigid objects under fast motion and heavy hand occlusion, without a dense multi-camera studio.
Stated limitations:
- The studio confines capture to a limited space, so motions needing larger environments are hard to capture. [6 Conclusion (Limitations and Future Directions)]
- Fully automatic tracking of articulated and non-rigid objects is not solved. [6 Conclusion (Limitations and Future Directions)]
- Object tracking loses track under fast motion or severe occlusion during manipulation, accumulating errors. [Supp. 8 Object Motion Tracking]
- Off-the-shelf hand and object pose estimators did not work well enough; HaMeR meshes lack accurate depth. [4.5 Object Motion Estimation]
- Hand-object motion forecasting remains challenging due to rapid, complex motion patterns. [Supp. 6 Experiments on Hand-Object Interaction]
Open problems listed:
- Capturing motions that require larger environments than a studio
- Fully automatic tracking of articulated and non-rigid objects
- Using large hand datasets to improve robotic manipulation and HCI
- Hand-object motion forecasting with fast, complex motion
- In-the-wild data is sparse, hard to calibrate and noisy, limiting 3D accuracy especially for objects
- Marker-based tracking inhibits natural interaction
Benchmark gaps:
- GigaHands / Object mask coverage rate: Coarse pose initialization achieves 45.2% mask coverage; sequence refinement 78.5%, below 91.1% on the first frame
- GigaHands / TACO / Forecasting MPJPE right/left, object translation and rotation error: GigaHands-trained MDM: 69.3/62.3 mm hand MPJPE, 47.6 mm translation, 67.5 deg rotation; TACO 71.7/58.4, 52.8, 73.2
- GigaHands / Text-to-motion R-Precision Top-1: 27.2% versus a ground-truth upper bound of 77.4%
Restrictive assumptions: Dense 51-camera RGB studio cube with LED lighting and a glass table, 1280x720 at 30 fps; Pre-scanned or single-view-generated template meshes needed for object 6DoF tracking; Subjects instructed to keep both hands inside the capture area; detector takes the two most confident hand boxes; Tabletop activities only, no real-world context; Rigid objects for pose; non-rigid objects only get segmentation masks

## [103] HOT3D: Hand and Object Tracking in 3D from Egocentric Multi-View Videos (CVPR 2025, dataset, S1 S5 S3 S6)
Source: https://arxiv.org/html/2411.19167; confidence HIGH.
Field cannot yet: The field cannot yet estimate 6DoF poses of hand-held objects accurately from egocentric views (about one third recall at 5 cm, 5 deg even multi-view with ground-truth masks).
Stated limitations:
- No dedicated limitations section; the paper states some annotations are missing or of lower quality, with 1.16M of 1.5M frames fully annotated and passing visual inspection. [3 HOT3D dataset]
- Motivating gap: existing methods are not accurate or fast enough to support target applications. [1 Introduction]
- Hand tracker overfits to the camera configuration seen at training, so two-view mode degrades across headsets. [4.1 3D hand pose tracking]
- Monocular depth lifting errors lie mostly along the optical axis, caused by inaccurate depth predictions. [4.4 3D lifting of in-hand objects]
- Ground-truth poses for dynamic onboarding sequences are given only for the first frame, reflecting that poses are hard to obtain when objects are hand-manipulated. [3 HOT3D dataset]
Open problems listed:
- Accuracy and speed of hand-object interaction understanding insufficient for AR/VR and robotics applications
- Model-free (CAD-free) object tracking from few-shot onboarding
- Obtaining object poses during dynamic hand manipulation
- Cross-headset generalization of multi-view hand trackers
- Leveraging eye gaze for intent prediction and foveated sensing
Benchmark gaps:
- HOT3D-Aria / FoundPose recall at 5 cm, 5 deg: 25.2% single-view and 33.8% multi-view, even with ground-truth masks
- HOT3D-Quest3 / FoundPose recall at 5 cm, 5 deg: 28.9% single-view, 36.9% multi-view
- HOT3D-Quest3 / In-hand object segmentation mIoU: EgoHOS 33.1% (either hand) and 13.5-14.4% for left/right; best MRCNN-DA 54.7%
- HOT3D-Aria / 3D lifting recall at 5 cm (predicted masks): StereoMatch 42.6%, MonoDepth 11.1%
- HOT3D-Quest3 / Hand MKPE (mm): UmeTrack-trained tracker: 24.2 mm single-view, 25.6 mm two-view; 10.9 mm only after joint training
Restrictive assumptions: Ground truth from OptiTrack marker mocap: 19 markers per hand, about 10 per object, objects with distinct marker constellations; 33 rigid objects with in-house scanned meshes and PBR materials; Single capture lab with scenario furniture (randomized lighting and decor); Benchmarks provide ground-truth hand shape and 2D boxes (hand tracking), ground-truth object masks (pose estimation, lifting); Multi-view headsets (Aria, Quest 3) with known calibration; MonoDepth needs SLAM points

## [113] TASTE-Rob: Advancing Video Generation of Task-Oriented Hand-Object Interaction for Generalizable Robotic Manipulation (CVPR 2025, dataset, S6 S1)
Source: https://arxiv.org/html/2503.11423; confidence HIGH.
Field cannot yet: The field cannot yet generate hand-object videos with temporally stable, physically consistent grasps for objects that rotate or articulate.
Stated limitations:
- Generation quality drops when objects undergo large transformations such as rotation or opening. [6 Discussion and Conclusion, Limitations]
- Fine-tuned video model produces unnatural grip changes during manipulation, which is critical for imitation learning. [1 Introduction]
- Imitation learning robots need nearly identical environments to the demonstration, limiting generalization. [1 Introduction]
- Pose refinement has a trade-off: more denoising improves pose consistency but degrades spatial awareness. [5.4 Ablation Study]
Open problems listed:
- Ego-centric HOI datasets have inconsistent viewpoints and clip-instruction misalignment
- General video diffusion models cannot generate task-accurate HOI videos
- Temporally consistent grasp poses in generated HOI videos
- Handling objects with large transformations (rotation, articulation)
Benchmark gaps:
- TASTE-Rob test / Grasp Type Classification Error / Hand Movement Direction Accuracy: Coarse model GTCE 67.8% and HMDA 26.4 deg; refined model still 9.7% and 11.3 deg
- Mujoco simulation / Robot manipulation success rate: 84% with coarse videos, 96% with refined videos; real-robot results not reported
Restrictive assumptions: Fixed, static egocentric camera viewpoint for every clip; Each clip under 8 s with exactly one action aligned to the instruction; All collectors right-handed; Hand poses extracted with HaMeR (2D/monocular estimation); Robot evaluation only in Mujoco simulation with the Im2Flow2Act policy

## [119] Reconstructing In-the-Wild Open-Vocabulary Human-Object Interactions (CVPR 2025, dataset, S2)
Source: https://arxiv.org/html/2503.15898; confidence HIGH.
Field cannot yet: The field cannot yet reconstruct metrically accurate 3D human-object arrangements for arbitrary objects from single in-the-wild images without manual annotation.
Stated limitations:
- The annotation pipeline depends on the quality of existing 3D human and object reconstruction tools. [7 Discussion]
- Only 17% of source images passed, indicating most 2D HOI images are hard to reconstruct in 3D. [B.2.4 Discussion]
- Coarse reconstruction has collisions, wrong scales and positions, and inaccurate object pose, so manual annotation is needed. [3.1 Coarse Reconstruction Annotation]
- The optimizer fails when body parts severely occlude each other and the object lies between them, making contact assignment ambiguous. [C.2 Failure Cases]
- Existing 3D general models are poor at 3D HOI understanding. [7 Discussion]
- No ground-truth objects exist, so object reconstruction quality cannot be evaluated with standard metrics. [B.2.3 Dataset quality]
Open problems listed:
- Lack of 3D open-world HOI data; existing 3D HOI datasets indoors with few objects
- In-the-wild 3D HOI benchmarks limited to few categories with fixed CAD models
- Training-free methods limited and reliant on manual annotation; training-based methods fail in open world
- 3D HOI understanding by large 3D/LLM models is poor
- Reliable object reconstruction from occluded in-the-wild images
- Efficient filtering of reconstructions
Benchmark gaps:
- Open3DHOI / Object translation error / Chamfer distance: Best method still has 38.44 cm translation error and 19.3 cm Chamfer distance; PHOSA 77.79 cm and 49.1 cm
- Open3DHOI / PointLLM Top-1 action/object recognition: Top-1 between 0.20 and 0.47 depending on prompt
- Open3DHOI / ChatPose MPJPE / MPVPE: About 103 mm MPJPE and 131 mm MPVPE
- Open3DHOI / Projection IoU: Object mesh projection IoU after fine annotation only 0.48
Restrictive assumptions: Single RGB image; monocular depth estimate for coarse placement; Object meshes from single-image generation (InstantMesh) with inpainting; Heavy manual annotation in Blender and a web tool; Single-person annotation per image; part-level (34 regions) contact rather than vertex-level; Benchmark initializes human parameters from dataset annotations and gives object meshes

## [120] PICO: Reconstructing 3D People In Contact with Objects (CVPR 2025, dataset, S2)
Source: https://arxiv.org/html/2504.17695; confidence HIGH.
Field cannot yet: The field cannot yet infer dense body-object 3D contact and object pose from single natural images reliably enough to recover object placement without ground-truth contact.
Stated limitations:
- May fail on interactions that differ significantly from those in PICO-db. [S.3.5 Failure cases]
- No single statistical object shape model exists and foundation models have limited 3D reasoning. [1 Introduction]
- Learning 3D HOI directly is described as intractable given the lack of 3D HOI datasets, motivating optimization. [4 PICO-fit Method]
- Existing regression HOI methods work on their training datasets but fail out of domain. [5 Experiments]
Open problems listed:
- No robust single-image 3D object shape recovery; no statistical object shape model
- No robust recovery of 3D human-object pose and arrangement
- Contact regressors infer only 2D contact, only body contact, or train on synthetic data
- Generalization of HOI reconstruction to OOD and in-the-wild images
- Scaling to novel object classes and interactions beyond finite datasets
Benchmark gaps:
- InterCap (OOD) / PA Chamfer distance, object (cm): PICO-fit without GT contact 21.85 cm object error vs 13.34 cm with GT contact; baselines 14.12-24.30 cm
- InterCap (OOD) / PA Chamfer distance, human+object (cm): 10.33 cm without GT contact; 8.36 cm with GT contact
- DAMON perceptual study / Preference rate vs PICO-fit*: PHOSA preferred 37.3% of the time; HDM comparison limited to 30 images of its 9 trained classes
Restrictive assumptions: Single RGB image; Object shape via retrieval from Objaverse (OpenShape), so the object is approximated by a retrieved mesh; Nearest-neighbour contact lookup from PICO-db for unlabeled images; Depends on OSX body initialization, DECO body contact and SAM masks; Static single-frame (no temporal) reconstruction

## [121] CORE4D: A 4D Human-Object-Human Interaction Dataset for Collaborative Object REarrangement (CVPR 2025, dataset, S2 S3)
Source: https://arxiv.org/html/2406.19353; confidence HIGH.
Field cannot yet: Vision-only methods cannot yet track multi-person collaborative object manipulation at mocap fidelity under severe occlusion, so data still depends on studio mocap.
Stated limitations:
- Real capture is indoor only because it depends on a mocap system. [6 Conclusion and Limitations]
- The synthetic (retargeted) part of the dataset has no visual signals. [6 Conclusion and Limitations]
- Vision-based human-object tracking is still too low-fidelity under multi-person occlusion to scale HOI data, motivating mocap plus retargeting. [1 Introduction]
- Prior contact-based interaction retargeting only works between objects of similar topology and scale. [2 Related Work (interaction retargeting)]
Open problems listed:
- Outdoor collaborative HOI capture not covered (mocap dependence).
- Synthetic collaboration data lacks visual signals; video transfer onto synthetic motion is open.
- Generalizing human collaborative motion to novel object shapes.
- Motion naturalness of synthesized multi-human interaction (FID gap).
- Avoiding inter-penetration and unnatural contact in generated collaboration.
- Low-fidelity vision-based HOI tracking under severe multi-person occlusion.
- Cost of scaling mocap to many objects.
Benchmark gaps:
- CORE4D motion forecasting S2 (unseen objects) / human joint position error (mm): MDM 186.4 and InterDiff 186.4 on unseen objects vs 170.8 on seen objects (S1); object rotation error about 10-11 degrees for all methods.
- CORE4D interaction synthesis / FID / contact: Synthesized results have higher FID than real motion; qualitative inter-penetration and unnatural contact persist for all baselines.
Restrictive assumptions: Real data captured with 12 infrared cameras, inertial-optical mocap suits, two data gloves per person and object markers (indoor studio).; Rigid objects with industrial-scanner 3D models (37 real objects, six categories).; Benchmarks take the object's 3D model and past poses as given.; Synthetic augmentation relies on category-level spatial homogeneity of human-object relations.

## [122] ParaHome: Parameterizing Everyday Home Activities Towards 3D Generative Modeling of Human-Object Interactions (CVPR 2025, dataset, S2 S1 S3)
Source: https://arxiv.org/html/2401.10232; confidence HIGH.
Field cannot yet: The field cannot yet capture body, finger and multi-object motion in natural home activity without markers, wearables and a dense camera rig.
Stated limitations:
- The system depends on artificial markers; authors plan a markerless approach. [6 Discussion]
- Captured in a single room with a limited object set; generalization needs other rooms and objects. [6 Discussion]
- ArUco markers corrupt the RGB data and may influence natural motion; RGB is not a target modality. [Supplementary (capture system)]
- Object tracking can still fail under severe occlusion despite 70 cameras. [3 (post-processing)]
- Wearable mocap drifts in global root position and uses imperfect skeleton scale assumptions. [3 (system alignment)]
Open problems listed:
- Markerless capture of body, hands and objects in natural home settings.
- Generalization to other rooms and more diverse objects.
- Occlusion-robust tracking of hands and objects during multi-object interaction.
- Combining heterogeneous capture systems (camera rig and wearable IMUs) without drift and skeleton-scale error.
- Learning spatio-temporal relations between human motion and object movement (object-from-body, fingers-from-object, forecasting, text-conditioned synthesis).
Benchmark gaps:
- ParaHome synthetic RGB (ControlNet renders) / 6D object pose and 3D hand pose error: Performance lower than on ROPE, FreiHAND and HO3D, attributed to complex HOI with mutual occlusion (numbers in supplementary).
Restrictive assumptions: 70 synchronized RGB industrial cameras covering one room.; Xsens IMU suit and Manus gloves worn by the participant.; ArUco 3D marker cubes attached to every object and body part.; Pre-modeled rigid and articulated object models.; Object assumed near-rigidly attached to nearby joints when filling tracking gaps.

## [131] ClimbingCap: Multi-Modal Dataset and Method for Rock Climbing in World Coordinate (CVPR 2025, dataset, S4)
Source: https://arxiv.org/html/2503.21268; confidence HIGH.
Field cannot yet: The field cannot yet recover off-ground, scene-contact-rich human motion in world coordinates from RGB alone without LiDAR and pre-scanned scenes.
Stated limitations:
- IMU-derived labels are inaccurate and translation drifts over long captures, requiring global optimization and manual repair. [4.2 Annotation Pipeline]
- Existing global HMR accumulates errors over long sequences, especially for climbing. [1 Introduction]
- RGB-only variant of ClimbingCap performs worst because LiDAR global position is required for post-processing. [5.3 Ablation]
Open problems listed:
- Few public 3D climbing datasets (only SPEED21 and CIMI4D before this).
- Global HMR ambiguity between camera and world coordinates.
- Error accumulation of global HMR in long sequences.
- Off-ground motion not handled by ground-based global HMR priors.
- IMU drift in long-duration capture.
Benchmark gaps:
- AscendMotion vertical scenes / W-MPJPE (mm): Best method ClimbingCap 106.95 vs 78.99 horizontal; GVHMR 1442.50 and WHAM 1499.85 in vertical scenes.
- AscendMotion vertical scenes / MPJPE (mm): ClimbingCap 88.92 vertical vs 75.45 horizontal.
- CIMI4D / WA-MPJPE: ClimbingCap is not best on WA-MPJPE in zero-shot transfer to CIMI4D.
Restrictive assumptions: Requires LiDAR (Ouster 128-beam) plus RGB; RGB-only performs much worse.; Pre-scanned high-resolution scene point cloud (Trimble X7) for each wall.; PTP hardware time synchronization and LiDAR-scene registration.; Labeled data requires Xsens IMU suit and manual annotation repair.; Static sensor placement per climbing scene.

## [136] FRAME: Floor-aligned Representation for Avatar Motion from Egocentric Video (CVPR 2025, dataset, S4 S7)
Source: https://arxiv.org/html/2503.23094; confidence HIGH.
Field cannot yet: Egocentric body capture still cannot resolve heavy self-occlusion and self-contact reliably from head-mounted cameras.
Stated limitations:
- The method does not exploit other headset modalities such as environment meshes, forward cameras, eye gaze or controller hand poses. [6 Discussion and Conclusion, Limitations]
- Struggles with significant occlusion and self-contact. [6 Discussion and Conclusion, Limitations]
- Prior egocentric work suffers synthetic-to-real gap and artifacts. [1 Introduction]
Open problems listed:
- Scarcity of real-world annotated ego-facing data and synthetic-to-real gap.
- Impractical prior rigs (protruding cameras, head-mounted checkerboards).
- Accurate device pose tracking during dataset collection.
- Occlusion and self-contact in egocentric body capture.
- Physical plausibility (floor penetration, foot skating).
Benchmark gaps:
- FRAME real-world ego dataset / MPJPE (mm): Best full model still 47.53 mm; left-view-only variant 87.94 mm.
Restrictive assumptions: Requires on-device 6D head pose (Quest SLAM) at inference.; Downward-facing stereo fisheye camera rig mounted on the headset.; Ground truth from a 120-camera 4K markerless studio and an ArUco board during collection.; Floor-aligned frame assumes a known floor / gravity alignment from the device.

## [146] MotionPRO: Exploring the Role of Pressure in Human MoCap and Beyond (CVPR 2025, dataset, S4)
Source: https://arxiv.org/html/2504.05046; confidence HIGH.
Field cannot yet: Vision-only mocap cannot yet supply the physical contact and force cues needed for drift-free, penetration-free global motion without dedicated pressure sensors.
Stated limitations:
- Dependence on specialized pressure sensors; inferring pressure from vision is the key next step. [11 Future Work (supplementary)]
- All motion must stay within the pressure mat area. [3 Dataset (capture system)]
- Without pressure-RGB fusion, global accuracy drops while local MPJPE improves, showing a trade-off between 2D alignment and physical plausibility. [5 Ablation]
- Pressure-only estimation yields plausible lower-body pose and trajectory (benefit stated for lower body). [1 Introduction]
Open problems listed:
- Inferring pressure from vision to remove specialized sensors.
- Physical plausibility of mocap (drift, jitter, sliding, floating, penetration).
- Whole-body contact (hips, hands, knees) beyond foot contact in global trajectory estimation.
- Lower-body robot motion tracking remains unstable from vision alone.
- Relationships between base-of-support contact, CoM-CoP distance and demographics.
Restrictive assumptions: Pressure mat under the subject; motion confined to the mat.; Four RGB cameras and a 12-camera optical mocap system for ground truth.; Ground contact is the interaction modelled (no hand-object contact).; Static, calibrated indoor capture.

## [183] HandX: Scaling Bimanual Motion and Interaction Generation (CVPR 2026, dataset, S3)
Source: https://arxiv.org/html/2603.28766; confidence HIGH.
Field cannot yet: The field still lacks enough clean, high-fidelity bimanual finger-level data to cover the full range of human dexterity.
Stated limitations:
- Dataset is finite and cannot cover the full range of dexterity and interactions. [Supplementary, Limitations]
- Aggregated public data keeps residual quality problems. [Supplementary, Limitations]
- Model scaling saturates; an ultra-large variant performs worse on all metrics. [6.3 Quantitative Evaluation]
Open problems listed:
- Finite volume and diversity of bimanual motion data.
- Residual jitter and kinematic implausibility in aggregated public datasets.
- Mismatched skeletons, frame rates and annotation protocols across hand datasets.
- Lack of fine-grained text supervision for hand motion.
- Saturation of model scaling beyond a regime.
Restrictive assumptions: New data from a 36-camera OptiTrack studio with 25 hand markers per hand.; Hand-only joint-position representation (no object geometry in the generated output).; Constant bone length assumption in skeleton reconstruction.; Text annotations produced automatically by kinematic features plus LLM.

## [190] Glove2Hand: Synthesizing Natural Hand-Object Interaction from Multi-Modal Sensing Gloves (CVPR 2026, dataset, S1)
Source: https://arxiv.org/html/2603.20850; confidence HIGH.
Field cannot yet: The field cannot yet obtain contact force and occluded-hand pose ground truth from bare-hand video without instrumented gloves or studios.
Stated limitations:
- Synthesis quality degrades in unseen in-the-wild settings. [Supplementary, Human Evaluation]
- Naive hand render overlay causes penetration, floating and wrist artifacts, needing a diffusion restorer. [3 Method (diffusion restorer)]
- Mocap ground truth can be inaccurate due to marker occlusion or sync latency. [Supplementary (pose optimization)]
- Prior contact methods need pre-scanned rigid objects; multi-camera studios are impractical in the wild. [1 Introduction]
Open problems listed:
- Vision-only HOI lacks force and contact signals.
- Hand occlusion makes robust tracking hard; occluded ground truth is hard to obtain.
- Contact estimation from vision lacks large accurately labeled data; prior work limited to planar surfaces.
- Temporal and multi-view consistency for generative hand video.
- Interactions with non-rigid, unknown-shape objects.
- In-the-wild domain gap for synthesized data.
Benchmark gaps:
- HandSense human evaluation, In-the-Wild / Mean Opinion Score / gap to real: Video hand realism 2.69 (gap 1.65); motion stability 2.54 (gap 1.60); visual artifacts 2.19 (gap 1.53).
- HandSense hand tracking / MKPE occlusion (mm): UmeTrack 19.2 mm on occluded frames; fine-tuned 16.6 mm, still higher than non-occluded MKPE.T values near 10 mm.
- HandSense contact estimation / Contact IoU: PressureVision++ reaches 0.8% IoU on dexterous HOI; best model 88.2%.
Restrictive assumptions: Per-subject 3D Gaussian hand model must be optimized; same-subject translation.; Paired glove and bare-hand sessions with identical object configurations.; Mocap markers on gloves and hands for 3D pose.; Egocentric grayscale headset stereo cameras.; Tactile sensors only at fingertips (binary fingertip contact).

## [192] Detecting Precise Hand Touch Moments in Egocentric Video (CVPR 2026, dataset, S1)
Source: https://openaccess.thecvf.com/content/CVPR2026F/papers/Nguyen_Detecting_Precise_Hand_Touch_Moments_in_Egocentric_Video_CVPRF_2026_paper.pdf; confidence HIGH.
Field cannot yet: Vision models cannot yet localize the exact frame of hand-object contact onset reliably in egocentric video.
Stated limitations:
- Existing contact methods lack temporal granularity to find contact onset. [2 Related Works]
- Only intentional, visually unambiguous touches are annotated; unobservable contacts are excluded. [3.2 Touch Annotation]
- HOI4D training labels come from an automatic tool that differs from manual labels by 1.94 frames on average. [3.2 Touch Annotation]
- MixUp augmentation degrades performance by 7.37% mAP due to noise in hand-object regions. [5.1 Implementation Details]
Open problems listed:
- No large-scale frame-level egocentric touch dataset existed.
- Frame-precise contact onset detection under egomotion, occlusion and motion blur.
- Distinguishing near-touch from actual-contact frames.
- Closely spaced bimanual touch events.
Benchmark gaps:
- TouchMoment HOI4D / AP at delta=0 (no NMS): Best 14.25; mAP 32.89.
- TouchMoment TACO / AP at delta=0 (no NMS): Best 24.25; mAP 41.08; with SNMS delta=0 only 16.78.
Restrictive assumptions: Hand boxes from off-the-shelf detectors (ground-truth boxes in training).; Grasp pseudo-labels from an external model (Hands23).; Segments selected where the hand-object interface is visible and contact is discernible.; Monocular egocentric RGB; data sourced from HOI4D and TACO only.

## [201] EgoXtreme: A Dataset for Robust Object Pose Estimation in Egocentric Views under Extreme Conditions (CVPR 2026, dataset, S5)
Source: https://arxiv.org/html/2603.25135; confidence HIGH.
Field cannot yet: The field cannot yet estimate or track the 6D pose of hand-held objects from egocentric RGB under fast motion, low light or smoke with usable accuracy.
Stated limitations:
- Ground truth relies on an OptiTrack mocap system, which confines capture to specialised indoor spaces and prevents evaluating true outdoor robustness. [5 Conclusion, Limitations and future works]
- No 3D hand pose annotations are provided; labelling hand articulation under extreme blur and speed is itself an unsolved problem. [5 Conclusion, Limitations and future works]
- Image restoration preprocessing (deblur, dehaze, low-light enhancement) does not help pose estimation and often hurts it. [4.2 Object pose estimation with pre-processing]
Open problems listed:
- Robust 6D object pose under severe motion blur, dynamic or low light and smoke in egocentric view.
- Outdoor evaluation of egocentric object pose (mocap restricts to indoor).
- Accurate 3D hand pose labelling under extreme blur and speed.
- Temporal modelling and tracking that survives large inter-frame displacement.
- Restoration methods whose output actually helps downstream pose estimation rather than adding artifacts.
Benchmark gaps:
- EgoXtreme sports (all conditions) / ADD(-S) recall @0.1d/0.2d/0.3d, PicoPose: 2.81 / 8.80 / 23.02 without preprocessing; preprocessing lowers it further (e.g. 2.58/8.22/20.99 with two methods).
- EgoXtreme emergency / ADD(-S) recall @0.1d, PicoPose with dehazing: Drops from 15.12 to 4.74 with dehazing.
- EgoXtreme sports normal light, golf club and pingpong / ADD(-S) recall @0.1d, GigaPose tracking variants: Per-frame 0.08 (golf) and 0.53 (pingpong); best temporal strategy stays below 1.6 percent at 0.1d.
- EgoXtreme maintenance / ADD(-S) recall @0.3d, PicoPose: 63.32 with no preprocessing, falling to 53.28 with combined preprocessing.
Restrictive assumptions: Evaluated methods require object CAD models (13 objects with CAD).; Baseline evaluation uses ground-truth bounding boxes to decouple detection errors (end-to-end with CNOS only in appendix).; RGB-only, since smart glasses lack depth; RGB-D methods such as FoundationPose excluded.; Ground truth needs OptiTrack markers on objects and headset, indoor capture only.; Single egocentric head-mounted camera (Aria glasses).

## [224] Teleoperation, Simulation, or Human Video? Data Utilization Law for Robot Manipulation (CVPR 2026, benchmark, S6)
Source: https://openaccess.thecvf.com/content/CVPR2026F/papers/Shi_Teleoperation_Simulation_or_Human_Video_Data_Utilization_Law_for_Robot_CVPRF_2026_paper.pdf; confidence HIGH.
Field cannot yet: The field cannot yet turn human manipulation video into robot training data that reliably helps rather than hurts in-domain policy performance.
Stated limitations:
- Naively added human video degrades in-domain policy performance due to embodiment and viewpoint mismatch. [1 Introduction (findings)]
- Simulation data hurts simple in-domain tasks, attributed to sim-to-real artifacts. [4.2 Teleoperation vs. Simulation Utilization]
- Utilization ratios are task- and goal-dependent rather than universal; data mixing must be tailored per task. [1 Introduction]
- Scope limited to three rigid-object dual-arm tasks; deformable and long-horizon tasks left to future work. [6 Conclusion]
Open problems listed:
- Principled valuation of heterogeneous robot data sources (exchange rates) across tasks.
- Embodiment and viewpoint gap that makes unaligned human video harmful.
- Sim-to-real gap that harms in-domain performance on simple tasks.
- Extending data utilization laws to deformable, high-dimensional and long-horizon manipulation.
Benchmark gaps:
- Real Aloha-Agilex-2.0, Rank RGB Blocks unseen background / success rate: Teleoperation only 0.13; with simulation 0.20.
- Real Aloha-Agilex-2.0, Rank RGB Blocks unseen position / success rate: Teleoperation 0.17, drops to 0.13 with human video.
- Real Aloha-Agilex-2.0, Pick Dual Bottles unseen background / success rate: 0.20 teleoperation-only; 0.30 with budget-aware sim mix.
Restrictive assumptions: Locally linear performance model near a chosen teleoperation count to define local ratios.; Optimality gap assumed to follow a power law in teleoperation count.; Human video recorded with a chest-mounted camera in the same environment as teleoperation; hand actions from MediaPipe landmarks and estimated gripper state.; Human-video action space (end-effector deltas) differs from robot joint-angle action space; pretrain then fine-tune protocol.; Only 10 real trials per scenario per policy; three tabletop rigid-object bimanual tasks.

## [225] Hoi! - A Multimodal Dataset for Force-Grounded, Cross-View Articulated Manipulation (CVPR 2026, dataset, S6 S1)
Source: https://arxiv.org/html/2512.04884; confidence HIGH.
Field cannot yet: The field cannot yet estimate articulation and interaction forces from in-the-wild egocentric video with clutter, hands and no reliable depth.
Stated limitations:
- Hoi! gripper demonstrations are still human-operated, so they do not capture the kinematic and dynamic constraints of real manipulators. [5 Limitations & Future Work]
- Generalization across full-body morphology remains open. [5 Limitations & Future Work]
- Does not cover the full range of mechanical complexities or rare edge-case mechanisms. [5 Limitations & Future Work]
- Benchmarks are object-centric perception tasks, not end-to-end policy learning. [5 Limitations & Future Work]
- Hand keypoints come from Aria MPS automatic estimates, not manual or mocap labels, so the hand benchmark is exploratory only. [D.5 Hand Pose Estimation]
Open problems listed:
- Transfer of interaction understanding between human and robot embodiments and viewpoints.
- Generalization across full-body morphology.
- Coverage of complex and rare articulation mechanisms.
- End-to-end policy learning combining perception and action.
- Articulation estimation robust to clutter, hands and noisy monocular depth.
- Tactile and visual force estimation that generalizes beyond lab indenters and to force-demanding mechanisms.
Benchmark gaps:
- Hoi! / ArtiPoint articulation type recall / axis angle error (deg): Type recall 26.9 percent; axis angle errors 47.06 and 63.76 deg versus 14.54 and 17.14 on Arti4D.
- Hoi! / ArtGS revolute distance error (m): 0.321 m with 0 percent recall on one type.
- Hoi! / Sparsh tactile force RMSE (N): Combined 3.86 N (DINO) and 4.11 N (DINOv2).
- Hoi! kitchen_7 / ForceSight RMSE (N): 3.53 projected, 3.64 raw versus 0.40 on the ForceSight dataset.
- Hoi! kitchen_7 / HaMeR hand PCK@0.15: 0.535 versus 0.844 to 0.893 on Ego4D, VISOR, New Days.
Restrictive assumptions: Aria glasses provide no dense depth; depth for articulation baselines comes from MapAnything scaled using scanned scene meshes.; Scenes laser-scanned before and after manipulation for ground truth.; Force and tactile ground truth only available for the instrumented gripper embodiments, not bare hands.; Hand keypoints derived from Aria MPS, not ground truth.

## [226] Ego-1K: A Large-Scale Multiview Video Dataset for Egocentric Vision (CVPR 2026, dataset, S1 S7)
Source: https://arxiv.org/html/2603.13741; confidence HIGH.
Field cannot yet: The field cannot yet reconstruct dynamic egocentric scenes with close-range moving hands and objects from a moving head without strong stereo depth priors.
Stated limitations:
- iToF depth streams were not used because depth is unreliable under motion and phase ambiguity. [3 Dataset, Multi-camera rig]
- No ground-truth depth; stereo is evaluated only by cross-pair consistency. [4.1 Evaluating pairwise stereo methods]
- Rig weighs about 6 kg and needs a backpack-mounted crane. [3 Dataset]
- Online calibration assumes calibration is constant over a recording; 1-3 pixel shifts from lens movement and temperature affect reconstruction. [3 Dataset, Calibration]
Open problems listed:
- Egocentric dynamic 4D novel view synthesis with ego-motion and near-field hands.
- Ground-truth or pseudo-ground-truth depth for egocentric dynamic scenes.
- Robustness to stereo baseline changes and temporal stability.
- HOI-focused evaluation on egocentric multiview data.
- Reliable active depth (iToF) under motion.
Benchmark gaps:
- Ego-1K (96 recordings) / PSNR on held-out pair: K-Planes 16.46, per-frame 3DGS 21.22, Spacetime Gaussians 24.76; stereo-guided 3DGS 29.12.
- Ego-1K / Stereo cross-pair MAD within 1 mm: Selective-Stereo 0.0 percent, BiDAStereo 3.1 percent; FoundationStereo 74.0 percent.
Restrictive assumptions: 12 hardware-synchronized global-shutter cameras on a head rig (not deployable glasses).; Rig poses from headset VIO.; Short recordings of 8-10 s.; Stereo-guided baseline requires calibrated rectified stereo pairs.

## [242] HUMOTO: A 4D Dataset of Mocap Human Object Interactions (ICCV 2025, dataset, S2 S1 S3)
Source: https://arxiv.org/html/2504.10414; confidence HIGH.
Field cannot yet: The field cannot yet capture clean multi-object full-body and hand interaction data without heavy manual artist cleanup.
Stated limitations:
- Only a single performer due to mocap suit size constraints, biasing body shape and movement style. [6 Conclusion and Limitations]
- Considerable manual cleaning by artists was required; more robust automatic pose estimation is needed. [6 Conclusion and Limitations]
- Quantitative quality metrics depend on motion and interaction complexity and should not be read in isolation. [4.2 Qualitative Evaluation]
Open problems listed:
- Capturing multi-object interaction with full-body and detailed hand motion at scale.
- Reducing manual cleanup cost for high-fidelity HOI data.
- Body-shape and style diversity in HOI mocap.
- Generating detailed multi-object HOI motion from text.
- Pose estimation under object occlusion including hands.
Restrictive assumptions: Inertial Rokoko suit and gloves (EMF), requiring a custom wooden stage to avoid magnetic interference.; Object 6DoF from dual Kinect RGB-D with FoundationPose, needing artist-built object models.; Calibration stance at a fixed position to align mocap and camera frames.; Extensive manual artist cleanup.; Single performer, scripted tasks.

## [251] Perceiving and Acting in First-Person: A Dataset and Benchmark for Egocentric Human-Object-Human Interactions (ICCV 2025, dataset, S2 S6)
Source: https://arxiv.org/html/2508.04681; confidence HIGH.
Field cannot yet: The field cannot yet recover world-grounded human and hand motion from a moving egocentric camera when people leave and re-enter the view.
Stated limitations:
- Limited to indoor scenes with 50 daily objects; indoor capture lacks some realism. [Appendix G Limitations]
- Building the dataset is time-consuming; around 10 hours is still insufficient for large generalist models. [Appendix G Limitations]
- Inertial gloves discarded to preserve RGB realism; finger poses not captured by mocap. [Appendix C Hand Pose Results]
Open problems listed:
- Egocentric world-grounded motion estimation of another person under rapid head motion and re-entry.
- Natural multi-human multi-object interaction synthesis.
- Interaction prediction from egocentric vision and language.
- Sparse-view 4D scene reconstruction.
- Egocentric hand-object reconstruction with multiple objects.
- Outdoor and larger-scale capture; finger ground truth without compromising RGB.
Benchmark gaps:
- InterVLA head-mounted egocentric / MPJPE (mm): Best WHAM 333.6; TRACE 720.1, TRAM 684.1, GLAMR 589.9.
- InterVLA / Motion-based interaction prediction human MPJPE (mm): Best CAHMP 172.5; object translation error 115.6 mm.
- InterVLA / Vision-language interaction prediction ADE/FDE (m): Best USST 0.24 / 0.32.
Restrictive assumptions: 20-camera optical mocap with glued markers on skin and clothes.; Objects as rigid bodies with at least four markers and scanned meshes.; Hands tracked only by three wrist markers (no finger ground truth).; Indoor mocap venue.

## [257] DexH2R: A Benchmark for Dynamic Dexterous Grasping in Human-to-Robot Handover (ICCV 2025, dataset, S3 S5 S6)
Source: https://arxiv.org/html/2506.23152; confidence HIGH.
Field cannot yet: The field cannot yet make a dexterous robot hand safely and reliably grasp an object a human is moving during handover.
Stated limitations:
- RGB-only diffusion policy cannot handle occlusions and depth ambiguity. [4.2.2 Diffusion-Policy Approach]
- MotionNet's aggressive strategy neglects collision avoidance, lowering safety. [5.4.1 Model Performance Comparison and Analysis]
- DP's conservative approach often fails to grasp within the frame limit. [5.4.1 Model Performance Comparison and Analysis]
Open problems listed:
- Real-world dynamic dexterous handover data for five-finger hands.
- Balancing grasp success and collision safety near a human hand.
- Fine-grained pose alignment in close proximity to a moving object.
Benchmark gaps:
- DexH2R test (unseen objects/subjects) / Hard Mode success / safety rate (percent): MotionNet 26.6/15.4, DP 8.3/38.5, DP3 27.1/33.7.
- DexH2R test / Easy Mode success (percent): MotionNet 71.1, DP 39.4, DP3 66.3.
- DexH2R / Grasp generation succ6 (percent): cVAE 35.0; DexGraspAnything 52.81.
Restrictive assumptions: Single right ShadowHand on UR10e controlled by low-latency teleoperation.; Object annotation by SAM2, depth fusion, global registration with manual correction, frame-by-frame ICP; requires object point clouds.; Hand pose via MediaPipe 2D keypoints and off-the-shelf MANO fitting.; Large fixed multi-camera setup: 12 RGB cameras, 4 Azure Kinects, 2 wrist RealSense.; Linear motion assumed over short horizon during goal pose alignment.

## [259] VOccl3D: A Video Benchmark Dataset for 3D Human Pose and Shape Estimation under real Occlusions (ICCV 2025, dataset, S4)
Source: https://arxiv.org/html/2508.06757; confidence HIGH.
Field cannot yet: The field cannot yet estimate 3D human pose and shape accurately when most of the body is occluded, especially without ground-truth detection boxes.
Stated limitations:
- Visual quality limited by lack of open high-fidelity assets; motions constrained by AMASS. [D Limitations and Future Work]
- Rendering relies on predefined camera poses to produce occlusions. [D Limitations and Future Work]
- A noticeable synthetic-to-real gap remains. [D Limitations and Future Work]
- Improvements on real datasets with minimal occlusion are marginal. [4.1 Human Pose and Shape Estimation]
Open problems listed:
- Robust HPS under heavy realistic occlusion.
- Occlusion-robust person detection.
- Sim-to-real gap for synthetic occlusion data.
- Automatic generation of occlusion-rich sequences.
- Higher-fidelity open human assets and more diverse motions.
Benchmark gaps:
- VOccl3D hard occlusion / MPJPE / PVE (mm): Best fine-tuned VOccl3D-B-CLIFF 136.34 / 175.92; CLIFF 192.22 / 247.41.
- 3DPW / MPJPE (mm), VOccl3D-CLIFF: 71.10 with GT boxes versus 116.52 with YOLO11 and 114.85 with fine-tuned detector.
Restrictive assumptions: Synthetic rendered humans on 3DGS-reconstructed backgrounds.; Main benchmark uses ground-truth bounding boxes.; Real occlusion evaluation relies on artificial black patches over 3DPW keypoints.; Monocular single-person HPS.

## [273] LDPose: Towards Inclusive Human Pose Estimation for Limb-Deficient Individuals in the Wild (ICCV 2025, dataset, S4 S7)
Source: https://openaccess.thecvf.com/content/ICCV2025/papers/Ying_LDPose_Towards_Inclusive_Human_Pose_Estimation_for_Limb-Deficient_Individuals_in_ICCV_2025_paper.pdf; confidence HIGH.
Field cannot yet: Pose estimators cannot yet reliably handle bodies that deviate from the complete-limb template, including residual limbs and prostheses, especially in 3D.
Stated limitations:
- Demographic skew: mostly young adults and 67% Caucasian. [7. Future Work and Discussion]
- Over half the data is competitive para-sport, limiting transfer to everyday movement. [7. Future Work and Discussion]
- Only 2D image annotations; no depth or 3D joint relations. [7. Future Work and Discussion]
- Prosthetic limbs are not annotated even though they define the pose. [7. Future Work and Discussion]
- Privacy: real-world images need automated face anonymization and identity protection. [7. Future Work and Discussion]
- Standard COCO metrics do not penalize predicted keypoints on missing limbs. [6.2 Limb-Deficient Metrics]
- LDLoss trades COCO accuracy for better residual/intact discrimination. [6.3 Benchmark Results]
Open problems listed:
- Distinguishing residual-limb from intact-limb keypoints (existing methods struggle)
- Demographic and activity diversity beyond young para-athletes
- 3D limb-deficient pose estimation with multi-view or mocap data
- Prosthetic-aware keypoint annotation
- Privacy and face anonymization for real-world imagery
- Evaluation metrics that penalize anatomically inconsistent predictions
Benchmark gaps:
- LDPose / COCO AP: YOLO-Pose without fine-tuning reaches AP 42.6 (49.8 after fine-tuning), the lowest of benchmarked methods.
- LDPose / COCO AP vs LD Metrics: Best COCO AP 82.6 (ViTPose ViT-l fine-tuned) coexists with anatomically impossible predictions; COCO metrics fail to reflect this.
Restrictive assumptions: Single 2D RGB images only; no 3D or temporal annotation; Frames with severe motion blur removed during curation; Prostheses excluded from the keypoint definition; Data sourced largely from Paralympic sport footage and web images

## [274] ProGait: A Multi-Purpose Video Dataset and Benchmark for Transfemoral Prosthesis Users (ICCV 2025, dataset, S7 S4)
Source: https://arxiv.org/pdf/2507.10223; confidence HIGH.
Field cannot yet: Off-the-shelf vision models cannot yet segment, track and pose prosthesis users in clinical video, or classify their gait deviations, without population-specific fine-tuning.
Stated limitations:
- Only four subjects, due to recruitment cost of a vulnerable population. [3.1 Video Data Collection]
- Pose ground truth, including test set, comes largely from a fine-tuned RTMW model with manual correction. [4.2 Baseline Models]
- Pretrained pose models miss prosthetic knee and foot keypoints. [3.2 Data Annotation]
- Grounded SAM2 loses track of the prosthetic leg even at high mIoU. [5.2 Video Object Segmentation]
- YOLO11 cannot represent a single subject made of discrete parts. [5.2 Video Object Segmentation]
- Gait classification only uses the primary deviation, though deviations co-occur clinically. [4.1 Benchmark Tasks and Metrics]
- Fusing frontal and sagittal views reduces classification accuracy. [5.4 Gait Classification]
Open problems listed:
- Precisely detecting the prosthesis as part of the human body
- Correctly distinguishing the subject from healthcare staff
- Ensuring consistent tracking despite occlusions
- Small sample size; need broader demographic and prosthetic diversity
- Multiple co-occurring gait deviations (benchmark uses primary only)
- Using textual gait reasoning with LLMs for clinical assessment
Benchmark gaps:
- ProGait / Top-1 / balanced accuracy (LSTM, 23 keypoints): Gait classification on the whole dataset with both views reaches only 0.384 top-1 and 0.413 balanced accuracy; inside parallel bars 0.364 top-1.
- ProGait / mIoU: Fine-tuned YOLO11-ProGait reaches 0.847 mIoU; Grounded SAM2 'a person.' 0.358.
- ProGait / AP@[.5,.95]: Pretrained HRNet 0.750, ViPNAS 0.761, ViTPose 0.830 versus fine-tuned RTMPose-ProGait 0.947.
Restrictive assumptions: Two fixed cameras (frontal and sagittal) at 1080p 30 fps in a clinical indoor setting; Four middle-aged or elderly vascular-cause transfemoral amputees; 2D keypoints only; no 3D; Single subject of interest per clip

## [302] Benchmarks and Challenges in Pose Estimation for Egocentric Hand Interactions with Objects (ECCV 2024, benchmark, S1 S3 S5)
Source: https://arxiv.org/pdf/2403.16428; confidence HIGH.
Field cannot yet: The field cannot yet reconstruct objects and hand-object contact accurately from moving egocentric views under fast motion and close bimanual contact.
Stated limitations:
- Several scenarios remain intractable for state-of-the-art methods. [Abstract]
- Most hand-object methods require a known object template. [2. Related Work]
- Egocentric object reconstruction is harder than allocentric. [5. Analysis, Egocentric-allocentric comparison]
- Object pose estimation suffers from arm/hand occlusion and changing views. [5. Analysis]
- Fisheye distortion at image edges degrades hand estimates. [5. Analysis, Bias of hand position]
- Articulated microwave is hardest due to global rotation sensitivity. [5. Analysis, Object-wise evaluation]
- Upper headset cameras often miss hands, creating unbalanced views. [5. Analysis, Effect of multi-view fusion]
Open problems listed:
- Fast hand motion
- Object reconstruction from narrow and moving egocentric views
- Close contact between two hands and objects
- Egocentric camera distortion near image edges
- Object occlusion by hands and arms and objects at image boundaries
- High diversity of camera-view object 6D poses in egocentric video
- Uneven multi-view sample distribution in headset cameras
- Efficient multi-view egocentric training
- 3D foundation priors for template-free hand-object reconstruction
- More expressive representations (heatmap-based)
- Temporal and motion modelling
- More diverse egocentric interaction scenarios
- Action recognition from hand poses
- Robot grasp learning from reconstructed sequences
Benchmark gaps:
- AssemblyHands / MPJPE (mm): Best method JHands reaches 12.21 mm overall but 16.27 mm on 'inspect'; baseline 20.69 mm.
- ARCTIC egocentric / CDev (mm): Best CDev 32.56 mm (JointTransformer) versus 27.97 mm allocentric; contact remains centimetres off.
- ARCTIC egocentric / Success Rate (%): Best object success rate 74.07% egocentric; baseline ArcticNet-SF 53.89%.
- ARCTIC allocentric val / CDev (mm): JointTransformer with ViT-G still has 29.0 mm contact deviation.
Restrictive assumptions: ARCTIC task assumes a known articulated object model (template); Known camera intrinsics and extrinsics provided at test time; Single RGB image input for ARCTIC methods (no temporal modelling); Monochrome multi-view headset images for AssemblyHands; Best AssemblyHands method uses offline Savitzky-Golay smoothing over full sequences

## [305] Dense Hand-Object(HO) GraspNet with Full Grasping Taxonomy and Dynamics (ECCV 2024, dataset, S1 S5)
Source: https://arxiv.org/pdf/2409.04033; confidence HIGH.
Field cannot yet: Hand-object pose estimation is not yet robust across the full grasp taxonomy for small, heavily occluded, articulated or deformable objects.
Stated limitations:
- Compound and articulated objects are treated as rigid; articulation not annotated. [Limitations and Future Work]
- No non-grasping actions or deformable objects. [Limitations and Future Work]
- Smaller object set than MOW and OakInk. [3.2 Object Categories and Grasp Taxonomy]
- Object markers can constrain hand poses. [3.3 Hardware Setup]
- Single right-hand grasps only. [3.3 Data acquisition]
- Initial keypoints are noisy under high hand-object occlusion. [3.5 MANO and Object Annotation]
- HALO captures less hand shape variation than MANO. [3.6 HALO fitting]
Open problems listed:
- Annotation of articulated and compound object articulation
- Non-grasping actions (pushing, throwing, squeezing)
- Deformable, non-rigid objects
- Synthetic augmentation beyond grasp areas
- Simulation environments for grasp-agent learning
- Extension to human-object and human-human interaction
- Small heavily occluded objects remain ill-posed for pose estimation
Benchmark gaps:
- HOGraspNet S0 / ADD-0.1D: Dice 2.44, small_marker 28.29, credit_card 34.06 with HFL-Net.
- DexYCB (cross-dataset) / MPJPE / PA-MPJPE (mm): HFL-Net trained on HOGraspNet gets 42.65 / 9.36 mm on DexYCB; trained on HO3D gets 57.31 / 10.31 mm.
- HOGraspNet S0 / PA-MPJPE (mm): Mean 5.67 mm, but errors highest for grasp classes missing from existing datasets.
Restrictive assumptions: Pre-scanned object meshes and optical mocap markers on objects; Four static, calibrated Azure Kinect RGB-D cameras in a studio; Single right hand per grasp; Objects treated as rigid; Manual LED-based synchronization; frames downsampled to 10 fps

## [306] Are Synthetic Data Useful for Egocentric Hand-Object Interaction Detection? (ECCV 2024, benchmark, S1)
Source: https://arxiv.org/pdf/2312.02672; confidence HIGH.
Field cannot yet: Egocentric hand-object detectors cannot yet be trained from synthetic data alone, and active-object segmentation remains weak even with full real supervision.
Stated limitations:
- Synthetic data cannot replace real data. [Discussion]
- A large synth-to-real gap of about 30-40% AP persists. [1. Introduction]
- Gap attributed to photorealism, grasp accuracy and limited diversity. [1. Introduction]
- Benefit of synthetic data shrinks as real labels increase. [Discussion]
- In-domain synthetic data helps little when some real labels exist. [1. Introduction]
- Domain adaptation models limited to batch size 4. [4. Experimental Analysis (footnote)]
Open problems listed:
- Synth-to-real domain gap of about 30-40% AP
- Photorealism of generated hand-object images
- Accuracy of synthesized grasps
- Diversity of environments and objects in synthetic data
- Synthetic data cannot replace real labeled data
- Scale of synthetic data needed (plateau at 22k-30k images on VISOR)
- Value of in-domain versus out-domain synthetic data
- Domain adaptation methods do not dominate all breakdown metrics
Benchmark gaps:
- EPIC-KITCHENS VISOR / Overall Mask AP: Synthetic-only 9.88; UDA 33.33; best fully supervised 46.48.
- EPIC-KITCHENS VISOR / Object Mask AP: Fully supervised Object AP 24.03-27.77, far below Hand AP of about 92.
- EgoHOS / Overall Mask AP: Synthetic-only 7.16; best fully supervised 39.61.
- ENIGMA-51 / Overall Mask AP: Out-domain synthetic-only 0.21; in-domain synthetic-only 12.85.
Restrictive assumptions: 2D detection and segmentation only (no 3D pose); Static grasps sampled from DexGraspNet; single frames, no motion; In-domain generation requires 3D models of the target environment and objects; Unity rendering in HM3D environments

## [308] 3D Hand Sequence Recovery from Real Blurry Images and Event Stream (ECCV 2024, dataset, S4)
Source: https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/07674.pdf; confidence HIGH.
Field cannot yet: The field cannot yet recover accurate 3D hand sequences from real motion-blurred RGB alone, without an auxiliary event sensor, across diverse hand shapes.
Stated limitations:
- Ten subjects only; shape diversity may be lacking. [6 Limitations]
- Event-only input fails on static hands. [5 Experiments, Various input combinations]
- A blurry image is temporally ambiguous. [1 Introduction]
- Deblurring before recovery does not work. [5 Experiments, Comparison with deblurring]
- 3D ground truth is produced by a self-supervised network annotator, not mocap. [3 EBH Dataset]
Open problems listed:
- Research gap on fast-moving hands despite prevalence
- Domain gap between synthetic and real motion blur
- Temporal ambiguity of blurry single images
- Event data lacks information for static hands
- Limited hand shape diversity in real blur datasets
Benchmark gaps:
- EBH / MPJPE (mm): Event-only methods: EventHands 28.80-30.97, EBHNet 28.59-30.80.
- EBH / MPJPE (mm), novel time step: Image plus events at unseen t=1.0 reaches 16.76 mm.
- BlurHand / MPJPE (mm): Best image-only EBHNet 16.45-17.23 mm; I2L-MeshNet 24.32 mm at mid step.
Restrictive assumptions: Lab capture with seven synchronized Kinects plus a calibrated, trigger-synchronized event camera; Hand gestures without object interaction; Root-aligned metrics; absolute hand position not evaluated; Pseudo ground truth from a network annotator trained on the same data; 80 ms exposure blur setting

## [322] F-HOI: Toward Fine-grained Semantic-Aligned 3D Human-Object Interactions (ECCV 2024, dataset, S2)
Source: https://arxiv.org/pdf/2407.12435; confidence HIGH.
Field cannot yet: Models cannot yet recover full HOI states (object pose and hand detail) from images with physically plausible contact while aligning to fine-grained language.
Stated limitations:
- Tasks require 3D object mesh, 3D HOI pose and text as input. [Limitations]
- Closed-set only; no open-set generalization. [Limitations]
- State-by-state sequence generation accumulates error and lacks smooth transitions. [Limitations]
- May underperform prior methods on generation and reconstruction. [Limitations]
- Hand detail poorly captured. [Limitations]
- LLM-based understanding and reasoning errors. [Limitations]
- Direct object pose output from images is too hard; reconstruction is object-conditioned. [4. Problem Definitions]
Open problems listed:
- Reducing strict input modality requirements (mesh, HOI pose, text)
- Open-set generalization to unseen objects and interactions
- Smooth transitions and error accumulation in state-by-state generation
- Hand-detail modelling
- LLM reasoning errors on interactions and spatial relations
- Interpenetration and lack of physical constraints
- Complex, long object trajectories
- Data scale and richer text
- Lightweight architectures
Benchmark gaps:
- Semantic-HOI / Chamfer distance (hands): Authors report the model underperforms in capturing hand details; no hand parameters predicted.
Restrictive assumptions: Known 3D object mesh as input; Object pose given for reconstruction (object-conditioned); Average body shape (beta set to zero); Fine-grained text generated by GPT-4V from images; Closed-set evaluation on GRAB, CHAIRS and BEHAVE; Large MLLM (Vicuna-7B) trained on 8 A100 GPUs

## [323] HIMO: A New Benchmark for Full-Body Human Interacting with Multiple Objects (ECCV 2024, dataset, S2)
Source: https://arxiv.org/pdf/2407.12371; confidence HIGH.
Field cannot yet: The field cannot yet capture or synthesize multi-object full-body interactions with natural, marker-free appearance and large objects.
Stated limitations:
- No large objects. [Limitations]
- RGB appearance unnatural due to mocap suits and markers. [Limitations]
- Facial expressions ignored. [Limitations]
- 4D HOI capture is hard. [1 Introduction]
- Naive dual-branch generation misaligns motions and produces implausible contacts. [1 Introduction]
Open problems listed:
- Interaction with large objects
- Natural RGB appearance without suits and markers
- Facial expressions
- Spatio-temporal alignment between generated human and object motions
- Implausible human-object and object-object contacts
- Smooth transitions between generated HOI segments
- Subtle finger motion capture under severe occlusion
Benchmark gaps:
- HIMO 3-objects / R-precision, MM-Dist, FID, Diversity: Proposed method outperforms baselines only on R-precision and MM-Dist in the 3-object setting.
Restrictive assumptions: Optical mocap with 20 infrared cameras and 41-marker suits plus inertial gloves; 3D-printed objects with known geometry and attached reflective markers; Objects on a 74 cm table; 2 or 3 small household objects per sequence; Generation conditioned on known initial human and object states and object geometry

## [328] Revisit Human-Scene Interaction via Space Occupancy (ECCV 2024, dataset, S2)
Source: https://arxiv.org/html/2312.02700 (arXiv id found via export.arxiv.org API); confidence HIGH.
Field cannot yet: The field cannot yet obtain large-scale, diverse paired human-scene interaction data, or generate collision-free interaction in dynamic and cramped scenes.
Stated limitations:
- In dynamic scenes the controller can produce slight collisions, attributed to a gap in occupancy change rate between training (human motion only) and test scenes (moving occupancy). [6 Discussion, Limitations]
- Foot sliding artifacts occur, and the foot-sliding metric is a simple heuristic that differs from real foot sliding. [6 Discussion, Limitations]
- MOB focuses on static HSI; the space-occupancy view of human-object interaction is left unexplored. [6 Discussion, Limitations]
- The controller only accepts target poses, space occupancy and joint trajectories as control signals. [6 Discussion, Limitations]
- Failure cases: turning around in narrow space, and keeping arms at a proper height to pass through narrow gaps. [Appendix D.3 Failure Cases]
Open problems listed:
- Limited scale and diversity of paired human-scene capture data (simultaneous human and 3D scene capture is expensive)
- Dynamic-scene interaction: gap between training occupancy change rate and moving-scene occupancy causes collisions
- Foot-sliding evaluation relies on heuristics that differ from real foot sliding
- Space-occupancy formulation of human-object interaction is unexplored
- Controllers accept only a narrow set of control signals
- Locomotion-interaction decomposition with rigid-cylinder path finding fails in cramped scenes
- Motion in narrow spaces (turning, upper-limb clearance)
Benchmark gaps:
- MOB (goal reaching, 30k 3-second clips) / Success rate (%): Best method 77.91% vs 100% for GT; prior methods NSM 11.76%, SAMP 13.94%, DIMOS 15.73%.
- MOB / Penetration (voxels per frame): Ours 15.21 vs GT 0.00; without occupancy 46.05; DIMOS 123.12.
- MOB / Foot sliding (% frames): Ours 8.13% vs GT 3.36%.
- MOB / Path-finding failure rate of baselines: NavMesh (DIMOS) fails on 69.43% of samples; A* (SAMP) on 70.29%.
Restrictive assumptions: Static HSI: the scene is not changed by the interaction; Pseudo-scenes are derived from motion-only mocap data (SMPL/SMPL-X), not from real scene scans or sensor observations; Object interaction requires fine-tuning on OMOMO plus given initial pose and hand trajectories; A target end-effector pose is supplied as the goal; Generation, not perception: no visual input is used

## [329] EgoBody3M: Egocentric Body Tracking on a VR Headset using a Diverse Dataset (ECCV 2024, dataset, S4 S7)
Source: https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/10261.pdf; confidence HIGH.
Field cannot yet: The field cannot yet track the full body reliably from product-form-factor headset cameras when limbs are out of view or the body is occluded by near-field objects or furniture.
Stated limitations:
- Near-field objects such as long hair or hats occluding the headset cameras cause problems. [7 Conclusion and Future Work]
- Strong occlusions, such as a tabletop covering both legs, increase prediction error considerably. [7 Conclusion and Future Work]
- The body network does not predict hand pose; an external hand tracker supplies wrist constraints. [6 Demonstration on a VR headset]
- No attempt is made to estimate body shape under clothing. [6 Demonstration on a VR headset]
- Off-the-shelf 2D keypoint detectors were unreliable in cluttered capture environments, requiring multi-detector fusion, outlier rejection and manual filtering of ground truth. [3.3 Ground truth]
Open problems listed:
- Under-constrained body tracking from headset and controller poses alone
- Impractical camera setups placed far from the face in academic work
- No single or stereo surface-mounted camera pair covers the full body region; blind spots remain
- Reasoning about occluded and out-of-view body parts
- Leveraging temporal information for plausible, smooth motion
- Scarcity of real egocentric body tracking data with practical camera placement (EgoCap largest at 60k images)
- Significant domain gap between synthetic and real egocentric body data
- Synthetic motion datasets focus on rare athletic motions rather than subtle social motions
- Near-field camera occlusion (hair, hats) and strong scene occlusion (tabletops)
- Hand pose and body shape are not estimated by the body network
Benchmark gaps:
- EgoBody3M / Out-of-view wrist MPJPE (cm): Best method 12.2 cm vs 5.18 cm overall MPJPE; UnrealEgo 23.7 cm; 2D-keypoint lifting 62.5 cm.
- EgoBody3M / Overall MPJPE (cm): Best 5.18 cm; 2D keypoints plus MLP lifting 17.5 cm.
- UnrealEgo (synthetic) / MPJPE (cm): Best 6.70 cm.
Restrictive assumptions: A specific headset with four synchronized monochrome SLAM cameras; Indoor environments only (primary use case VR); Ground truth requires 8 outside-in Azure Kinects plus Optitrack headset tracking in a mocked-up capture space; Body only: 26 keypoints, no hand keypoints; hands come from a separate tracker; Frames annotated very inaccurate or wrong (more than 5 cm joint error) are excluded from training and metrics

## [333] Nymeria: A Massive Collection of Egocentric Multi-modal Human Motion in the Wild (ECCV 2024, dataset, S4 S6 S7)
Source: https://arxiv.org/html/2406.09905; confidence HIGH.
Field cannot yet: The field cannot yet capture accurate, drift-free, long-duration full-body ground truth in the wild without instrumenting the subject in ways that alter appearance and motion.
Stated limitations:
- The mocap suit and wristbands make video appearance unnatural and restrict range of motion. [5 Conclusions and Discussions, Limitations]
- XSens inertial mocap quality depends on calibration and body measurements. [5 Conclusions and Discussions, Limitations]
- Coverage of daily activities is partial; common public scenarios are not included. [5 Conclusions and Discussions, Limitations]
- Non-rigid mounting of the Aria glasses is the main source of inaccuracy in aligning body motion with the device trajectory. [3.2 Data processing]
Open problems listed:
- Obtaining long-term ground-truth motion in the wild: optical systems are limited by line of sight and capture volume; inertial systems drift
- Multi-device temporal and spatial alignment with off-the-shelf hardware lacking universal sync; clock drift in long recordings
- Data processing and in-context natural-language annotation at scale
- Egocentric motion datasets are sparse, lack ground truth or parametric body motion, or are limited in scale, diversity and modality
- Full-body motion from egocentric headsets is ill-posed given insufficient observation
- Sensor inputs simulated from mocap lack real noise characteristics
- Research opportunities: full-body tracking, motion synthesis, forecasting, path planning, action recognition, behavior analysis
- Gaze-conditioned motion prediction; action recognition from headset and wristbands; interaction generation from language
- Multimodal spatial reasoning, scene reconstruction with rich dynamics, video understanding, image retrieval and relocalization
- Simulation of characters, 3D scenes and sensors
- Mocap suit appearance and motion restriction; XSens calibration sensitivity; no public scenarios
Benchmark gaps:
- Nymeria (3-point tracking, AvatarPoser) / MPJPE (cm): 7.97 cm with real inputs (lower body 16.74 cm) vs 4.20 cm when trained/tested on AMASS.
- Nymeria (1-point synthesis, EgoEgo) / MPJPE (cm): 13.22 cm (lower body 19.03 cm).
- Nymeria (BoDiffusion) / MPJPE (cm): 7.98 cm vs 3.63 cm on AMASS.
- Nymeria motion-to-text (30 h subset) / BLEU@4: MotionGPT 10.31, TM2T 8.99; worse than original HumanML3D/KIT results.
Restrictive assumptions: Ground truth from a full-body inertial mocap suit (XSens), not optical markers; Constant rigid transform between the XSens head segment and Aria glasses; Participants wear Aria glasses, two wristbands and a sync device; Device localization from Project Aria MPS SLAM

## [334] AddBiomechanics Dataset: Capturing the Physics of Human Motion at Scale (ECCV 2024, dataset, S4 S7)
Source: https://arxiv.org/html/2406.18537 (arXiv id found via export.arxiv.org API); confidence HIGH.
Field cannot yet: The field cannot yet estimate external forces and joint torques accurately from motion alone outside an instrumented lab, across diverse activities.
Stated limitations:
- The dataset is biased toward walking and running. [6 Conclusion and Future Work]
- Only about a fifth of the data meets clinical-grade dynamics thresholds; mean angular residual 0.11 BW*h exceeds the 0.1 threshold. [3.2 Evaluating Dataset Quality]
- Frames where subjects step off force plates cannot be used in the final dataset. [1 Introduction]
- External force measurement outside motion capture labs is unreliable, and existing force-from-motion models are not real-time or not validated against measurements. [1 Introduction]
Open problems listed:
- Quantifying dynamics (joint torques, external forces) from inexpensive sensors
- External force measurement outside mocap labs is unreliable
- Force-from-motion models are intractable for real time or not evaluated against measured data
- Lack of combined motion and force datasets across diverse subjects and activities
- Offline trajectory optimization is slow (about 0.001x real time), handles only seconds of data, errs about 10% body weight, and needs task-specific objectives
- Task-specific deep models do not generalize; out-of-distribution multi-activity models exceed 25% body weight error
- Lack of standard evaluation metrics; ground reaction moment often neglected
- Dataset bias toward walking and running
- Foot sliding artifact removal, real-to-sim contact modeling, physical motion auto-encoders
Benchmark gaps:
- AddBiomechanics test set / GRF error (N/kg): Best baseline GroundLinkNet 1.17 N/kg, MLP 1.29, analytical 2.79.
- AddBiomechanics test set / Joint torque error (Nm/kg): MLP 1.33, GroundLinkNet 1.34, analytical 2.77.
- AddBiomechanics dataset quality / Fraction meeting clinical thresholds: 21.2% (12.1 hours) clinical-grade; angular residual 0.11 BW*h vs 0.1 threshold.
Restrictive assumptions: Lab capture with optical marker mocap and in-ground force plates; Manual frame-by-frame review to mark steps off force plates; Benchmark task assumes an off-the-shelf mocap model supplies joint angles and a correctly scaled body model is available; Rajagopal musculoskeletal model

## [345] SignAvatars: A Large-scale 3D Sign Language Holistic Motion Dataset and Benchmark (ECCV 2024, dataset, S4)
Source: https://arxiv.org/html/2310.20436 (arXiv id found via export.arxiv.org API); confidence HIGH.
Field cannot yet: The field cannot yet reconstruct and evaluate accurate 3D two-hand articulation from monocular video for continuous signing without manual annotation or a reliable 3D back-translation metric.
Stated limitations:
- No sophisticated, generic 3D back-translation method exists, which limits evaluation. [6 Conclusion, Limitations and future work]
- No assessed model reaches the desired accuracy on the benchmark. [1 Introduction]
- HamNoSys-prompted production remains far from ideal. [5.2]
- There is no standard metric for 3D sign language production; BLEU/ROUGE do not generalize to HamNoSys or glosses, and MPJPE is unsuited for length mismatch. [5.2 Evaluation metrics]
Open problems listed:
- Manual, labour-intensive 3D sign language annotation
- Existing sign language datasets are 2D and suffer depth ambiguity
- No unified large-scale multi-prompt 3D holistic dataset with accurate hand meshes
- Lack of robust methods for continuous, co-articulated sign videos with complex hand interactions
- No de-facto evaluation standard for 3D sign language production
- Lack of a generic 3D back-translation method
- Production from spoken language is harder
- Combining 3D SLT and SLP; large 3D SL motion models for AR/VR
Benchmark gaps:
- SignAvatars HamNoSys subset / DTW-MJE rank top-1: Best 0.516 (SignVAE); Ham2Pose-3d 0.253.
- SignAvatars ASL (spoken language) / R-precision top-1 / FID: Generated 0.265 vs real motion 0.375; FID 4.359.
Restrictive assumptions: Annotations from monocular RGB online videos via optimization against 2D keypoints (ViTPose, MediaPipe); Body shape fixed per video (signer assumed unchanged); Lower body excluded from evaluation; Pseudo ground truth: annotation accuracy validated only on EHF

## [347] Omni6DPose: A Benchmark and Model for Universal 6D Object Pose Estimation and Tracking (ECCV 2024, benchmark, S5)
Source: https://arxiv.org/html/2406.04316; confidence HIGH.
Field cannot yet: The field cannot yet estimate or track category-level 6D pose accurately and in real time across hundreds of real categories, especially transparent, reflective or textureless objects.
Stated limitations:
- GenPose++ leaves substantial room for improvement and is slowed by diffusion iterative refinement. [6 Conclusions and Discussion]
- Large real datasets are too expensive to collect at sufficient diversity, so training relies on simulated SOPE. [3.3 SOPE Synthesis]
- Evaluation assumes ground-truth instance segmentation is known. [5.1 Metric]
- BundleTrack fails on weak textures and on transparent or specular objects with depth noise. [5.3 Results and Analysis]
Open problems listed:
- Lack of large-scale 6D pose datasets limits evaluation
- Few instances or categories restrict applicability
- Real data collection at scale is prohibitively expensive
- Semantic and geometric sim-to-real gaps
- Depth noise on transparent and specular materials
- Ambiguity from symmetry and partial observation
- Slow diffusion inference
- Integration into downstream tasks
Benchmark gaps:
- ROPE (estimation) / VUS@5deg2cm / AUC@IoU75: Best GenPose++ 10.0 / 2.0; NOCS 0.0 on all.
- ROPE (tracking) / 5deg5cm / Rerr: Best 15.9 (GenPose++, CATRE); GenPose++ Rerr 17.6 deg; BundleTrack 1.3, Rerr 46.9 deg.
- ROPE (tracking) / Speed (FPS): GenPose++ 17.8 FPS vs CATRE 38.5.
Restrictive assumptions: Ground-truth instance masks for estimation; Tracking initialized from perturbed ground-truth pose; Training only on simulated data (SOPE), tested on real ROPE; RealSense D415 structured-light RGB-D; Annotation by SfM and manual keypoint alignment over keyframes

## [348] PACE: Pose Annotations in Cluttered Environments (ECCV 2024, benchmark, S5)
Source: https://arxiv.org/html/2312.15130 (arXiv id verified via export.arxiv.org API); confidence HIGH.
Field cannot yet: The field cannot yet track rigid and articulated objects robustly in cluttered, occluded real scenes, or recover tracking once it is lost.
Stated limitations:
- PACE lacks large and valuable objects such as tables, cameras and laptops. [6 Conclusions and Limitations]
- Markers compromise realism and cannot annotate moving objects, needing inpainting and extra tools. [3.3 Annotation of Pose Ground-Truths]
- Moving-object annotation with BundleTrack drifts and needs manual correction every ten frames. [3.3 Annotation of Moving Object Poses]
- Depth-input methods struggle with real depth noise across the sim-to-real gap. [5.1 Result Analysis and Discussions]
Open problems listed:
- Poor real-world performance hidden by constrained benchmarks
- Sim-to-real gap, especially depth noise
- Scalability to many instances and categories
- Articulated objects
- Tracking robustness and recovery after loss
- Markers reduce realism and cannot annotate moving objects
- Missing large and valuable object classes
Benchmark gaps:
- PACE (model-based tracking) / AUC ADD(-S): Best ICG 38.1% rigid, 10.1% articulated.
- PACE (model-free tracking) / 5deg5cm: Best under 13% (CAPTRA 12.9 rigid, 4.4 articulated).
- PACE (category-level) / AP@0:20deg,0:5cm: Best CPPF++ 9.9 rigid, 1.1 articulated.
- PACE (Real2Real all categories) / AR% / AP%: Drops of 57-78 points vs single-instance fitting.
Restrictive assumptions: Ground-truth detections and masks for baselines; Ground-truth bounding-box sizes for tracking; Model-based tracking needs a CAD model; model-free needs first-frame pose; Training on synthetic PBR data only; Annotation needs a calibrated 3-camera rig with markers and manual correction

## [350] Omni6D: Large-Vocabulary 3D Object Dataset for Category-Level 6D Object Pose Estimation (ECCV 2024, dataset, S5)
Source: https://arxiv.org/html/2409.18261 (arXiv id found via export.arxiv.org API); confidence HIGH.
Field cannot yet: The field cannot yet estimate object rotation reliably across large vocabularies or unseen categories, nor annotate such data in the real world at scale.
Stated limitations:
- The dataset does not cover all real-world challenges. [5 Conclusion, Limitations]
- The fine-tuning strategy may lose efficacy as category diversity grows. [5 Conclusion, Limitations]
- Omni6D is rendered; real large-vocabulary annotation is described as monumental. [4.5 Visual Realism]
- Ground-truth masks are used because large-vocabulary semantic classification is unreliable. [4.1 Details]
Open problems listed:
- Too few categories limit practical use
- Occlusion and complex scenes overlooked
- Rotation generalization is a considerable challenge in large vocabularies
- Accuracy declines as category count grows
- Scarce well-annotated real large-vocabulary data
- Multi-axis rotational symmetry handling
- More object types and scenes; real video annotation; new training strategies
Benchmark gaps:
- Omni6D test (166 categories) / 5deg2cm (%): Best 8.28 (DualPoseNet); HS-Pose 4.26; GPV-Pose 0.10.
- Omni6Dout (unseen categories) / 5deg2cm (%): Best 3.24 (DualPoseNet); SPD 0.18.
- Omni6D fine-tuning cls3 to cls48 / 5deg2cm (%): HS-Pose falls from 62.52% to 14.42%.
Restrictive assumptions: Synthetic rendered RGB-D in Replica rooms; real set only 1k images, 73 instances; Ground-truth instance masks; Canonical poses and symmetry labels per instance; Real-set annotation via ICP plus manual 3D boxes

## [368] FEEL (Force-Enhanced Egocentric Learning): A Dataset for Physical Action Understanding (ECCV 2026, dataset, S1 S6)
Source: https://arxiv.org/html/2603.15847; confidence HIGH.
Field cannot yet: The field cannot yet obtain scalable, unobtrusive ground-truth hand force and contact for natural egocentric manipulation, including contact with stationary objects.
Stated limitations:
- Glove hardware is uncomfortable and sensors are unreliable over time. [5 Discussion, Limitations]
- Fingertip sensors interfere with fine dexterous manipulation. [5 Discussion, Limitations]
- Contacted-object pseudolabels depend on object motion, so stationary contacted objects cannot be segmented. [5 Discussion, Limitations]
- Raw force signals need heavy filtering; frames with intermediate force are discarded as ambiguous rather than labeled. [3.2 Contact Understanding]
- Force pretraining is done as fine-tuning from existing weights, not joint pretraining, due to compute. [4.2 Action Representation Learning]
Open problems listed:
- Force is absent from existing egocentric datasets because it cannot be reliably manually labeled.
- Annotating making and breaking of contact from RGB is difficult and noisy, including hand-side (handedness) labels.
- Real-world force data are scarce; most vision force work relies on simulation, and robotics force datasets are limited to simple pick-and-place.
- Wearable force sensors are uncomfortable, drift, and obstruct fingertips; better form-factor sensing (e.g., wrist EMG) is needed.
- Segmenting stationary contacted objects requires cues beyond motion.
- Scaling force-video datasets to close the gap between physical interaction and what video shows.
Benchmark gaps:
- HOI4D / Binary contact (BC) accuracy: Force-supervised model 82.2 vs fully supervised 100DOH 90.0; the paper's model trails on this zero-shot transfer.
- EPIC-VISOR / Contact segmentation IoU: Ours 0.399 vs 100DOH+SAM 0.443; all methods remain below 0.45 IoU.
- FEEL / Contact segmentation IoU: SAM3 concept prompting reaches 0.030 and VISOR model 0.111; best (ours) 0.625.
- FEEL / Binary signed contact (BSC): Existing supervised detectors drop to 40.0-57.2 BSC on FEEL, showing poor transfer of manual-label contact detectors.
Restrictive assumptions: Custom glove with six piezoresistive sensors (five fingertips plus palm), each up to 45 N, worn by the subject.; Meta Project Aria glasses plus Meta MPS for camera trajectories and 3D hand tracking.; Kitchen-only, natural unscripted manipulation.; Weak noun labels per 2-minute window are required for SAM3 concept prompting in pseudolabel generation.; Contacted object must move and lie within a 3D distance threshold of the hand centroid (monocular DepthPro depth).; Force is collapsed to a single geometric-mean signal with dual thresholds; ambiguous frames excluded.; Hand must be visible (at least 50% of frames for video pretraining clips).

## [389] Prosthesis-Aware 3D Human Pose Estimation: A Dataset and Benchmark for RSP Users (ECCV 2026, dataset, S4 S7)
Source: https://arxiv.org/html/2609.18406; confidence HIGH.
Field cannot yet: The field cannot yet jointly recover body joints and the geometry of an attached non-anatomical rigid object from monocular video with consistent global alignment.
Stated limitations:
- Dataset too small to train on; only usable for zero-shot benchmarking. [Limitation and Future Work]
- Capture is marker-based in a lab; markerless in-the-wild remains open. [Limitation and Future Work]
- Hybrid baseline needs manually assigned amputation site labels. [Limitation and Future Work]
- Global alignment of prosthesis to body in root-aligned space is sensitive to depth error. [5.2 Hybrid Baseline]
- Hybrid baseline is only a zero-shot reference; evaluation thresholds not yet comprehensive. [Limitation and Future Work]
Open problems listed:
- Dataset scale insufficient for training.
- Markerless, in-the-wild capture of prosthesis users.
- Leveraging synthetic data and biomechanical/RSP consistency constraints in optimization.
- Automatic amputation-site prediction from temporal cues.
- Global body-to-prosthesis alignment sensitive to depth estimation.
- 2D detection and segmentation for prosthesis users as a bottleneck.
- Stricter thresholds and more comprehensive RSP shape and pose evaluation.
Benchmark gaps:
- RSP3D / Chamfer Distance (root-aligned RSP): Hybrid baseline CD 288.44 with 2D detection, worse than STv2-Pointmap 277.15; F@50 only 19.92.
- RSP3D / MPJPE: Model-free STv2-Tracking 174.84 mm and STv2-Pointmap 159.64 mm with 2D detections; best model-based SAM3D Body 78.35 mm.
- RSP3D bilateral subset / Chamfer Distance: Hybrid CD 342.22 for bilateral vs 256.64 for unilateral amputees; F@50 13.80.
Restrictive assumptions: Ground truth from 16 GoPro cameras plus marker-based motion capture in an indoor lab.; Hybrid baseline requires ground-truth amputation site labels.; Model-free evaluation resolves scale using ground-truth first-frame bounding box size.; SAM2 RSP mask tracking initialized from ground-truth RSP bounding box in first frame and restarted every 10 s.; A single camera view with moderate occlusion is hand-selected per action segment.; Video is chunked into 1 s segments (T=60) for SpatialTrackerV2.

## [402] XYZ-IBD: Benchmarking Robust 6D Object Pose Estimation under Real-World Industrial Complexity (ECCV 2026, benchmark, S5)
Source: https://arxiv.org/html/2506.00599; confidence HIGH.
Field cannot yet: The field cannot yet estimate 6D pose of reflective, symmetric, densely stacked rigid objects with the sub-millimeter reliability manipulation needs.
Stated limitations:
- Commodity depth sensing breaks down on specular metal, so the dataset needs anti-reflection spray to obtain ground truth. [1 Introduction]
- All benchmarked methods struggle on the dataset. [4.5 Evaluation of Object 6D Detection]
- Seen-object methods trained on synthetic data fail on real scenes. [4.5 Evaluation of Object 6D Detection]
- Unseen-object methods depend on an upstream segmentation or detection prior. [4.5 Evaluation of Object 6D Detection]
- Object categories and conditions are limited; expansion left to future work. [5 Conclusion]
Open problems listed:
- Household benchmarks are near saturation and do not reflect industrial complexity.
- Highly reflective, texture-less, geometrically symmetric parts.
- High-density stochastic stacking with multi-instance ambiguity and heavy occlusion.
- Accurate ground truth for specular objects; depth sensors are biased on specular surfaces.
- Sub-millimeter accuracy required for industrial grasping.
- Sim-to-real gap for methods trained on synthetic data.
- Dependence of unseen-object pose estimation on segmentation priors.
- Expanding object categories and working conditions.
Benchmark gaps:
- XYZ-IBD / 6D detection AP (BOP): GDRN 0.827 on BOP-Core5 falls to 0.266; SurfEmb 0.758 to 0.247.
- XYZ-IBD / 6D detection AP (unseen objects): Best SAM6D 0.578, FoundationPose 0.564, MatchU 0.529, below their BOP-Core5 scores (0.70-0.73).
- XYZ-IBD / Unseen 2D detection AP: CNOS 0.275, SAM-6D 0.296, NIDS-Net 0.258, versus 0.36-0.49 on BOP-Core5.
Restrictive assumptions: CAD models of every part (micron-level accuracy) are available.; Ground truth needs temporary anti-reflective coating and robot-arm repeated viewpoints (FANUC, 0.06 mm repeatability) over 50 calibrated views.; Static bins of rigid objects; no hands or manipulation in the scenes.; Seen-object baselines trained only on synthetic data.; Unseen-object 6D baselines use SAM-6D masks as given segmentation prior.

## [405] MessyKitchens: Contact-rich object-level 3D scene reconstruction (ECCV 2026, dataset, S5)
Source: https://arxiv.org/html/2603.16868; confidence HIGH.
Field cannot yet: The field cannot yet reconstruct cluttered real scenes from a single image into accurate, contact-consistent object-level 3D without penetrations or floating objects.
Stated limitations:
- Object-level scene decomposition is hard due to variety, occlusion and object relations. [Abstract]
- Prior benchmarks have inaccurate registration and penetrations. [1 Introduction]
- SAM 3D treats objects independently, giving inconsistent layouts. [2 Related Works]
- MOD corrects only pose and scale; geometry comes unchanged from SAM 3D. [5.3 3D object-based reconstruction]
- Evaluation requires Sim(3) ICP alignment because predictions are not in the ground-truth frame. [5.3 3D object-based reconstruction]
Open problems listed:
- Large variety of object shapes and frequent occlusions in object-level scene reconstruction.
- Physically plausible reconstruction: non-penetration, correct contacts, deformations and other physical parameters.
- Existing benchmarks: limited annotation and registration accuracy, inaccurate contacts, insufficient scene complexity, or poor scalability (mocap or robot-based capture).
- Generative scene methods (MIDI, PartCrafter) trained on synthetic data fail to generalize to real captures.
- Retrieval and feed-forward methods limited by scarce 3D supervision and database diversity.
- Single-object reconstruction lacks reasoning about inter-object spatial dependencies.
Benchmark gaps:
- MessyKitchens / Object-level IoU: Best MOD 0.445; SAM 3D 0.409; PartCrafter 0.071, MIDI 0.186.
- GraspClutter6D / Object-level IoU: MOD 0.340 vs SAM 3D 0.328 on the out-of-distribution high-clutter set.
- MessyKitchens / Contact F1 (PhySIC contact graph): Best MOD 66.1; SAM 3D 55.8; PartCrafter 21.2.
Restrictive assumptions: Single RGB image input with object segmentation masks from SAM 3.; Static, rigid tabletop kitchenware scenes without hands or dynamics.; MOD trained only on synthetic scenes built from 42 GSO objects.; Ground truth needs pre-scanned object meshes (6-10 min each) and scene scans (up to 20 min) with manual coarse alignment.; Evaluation aligns prediction to ground truth with Sim(3) ICP, best of three runs.

## [418] emg2pose: A Large and Diverse Benchmark for Surface Electromyographic Hand Pose Estimation (NeurIPS 2024, dataset, S4)
Source: https://arxiv.org/html/2412.02725; confidence HIGH.
Field cannot yet: The field cannot yet infer accurate, physically plausible hand pose from wearable non-visual sensing that generalizes to new users and movements without an initial pose.
Stated limitations:
- sEMG models remain less accurate than vision methods. [5 Limitations and Future Work]
- Predictions can be physically infeasible and metrics do not capture plausibility. [5 Limitations and Future Work]
- Test sets omit real-world signal aggressors. [5 Limitations and Future Work]
- Mocap labels suffer occlusion and lose frames. [3.2 Dataset]
- No wrist motion is recorded. [B.4 Dataset Limitations]
- Hardware access limits human-in-the-loop testing. [5 Limitations and Future Work]
Open problems listed:
- Generalization across users, sensor placements and kinematics; sEMG models are data-hungry.
- sEMG encodes muscle activity closer to motion than pose, making direct pose regression partially observable.
- Accuracy gap to computer-vision hand pose estimation.
- Physical plausibility of predictions and metrics capturing it.
- Bias of default hand model in landmark metrics.
- Real-world signal aggressors: electrode-skin artifacts, sweat, interference, muscle fatigue.
- Mocap labels degraded by occlusion (e.g., fist clenching); wrist movement not tracked.
- Dataset smaller than proprietary ones, may limit generalization.
- Limited access to sEMG hardware prevents human-in-the-loop testing.
- Fusing camera and sEMG where camera tracking fails.
Benchmark gaps:
- emg2pose (held-out user, stage) / Regression landmark distance / angular error: Best vemg2pose 21.6 mm and 15.8 deg; SensingDynamics 27.2 mm.
- emg2pose (held-out stage) / Tracking landmark distance: vemg2pose 15.2 mm even with ground-truth initial pose, vs 10.3 mm for held-out users only.
Restrictive assumptions: Labels from a 26-camera marker mocap rig in a lab; participants stand in the capture array.; Proprietary sEMG-RD wristband not broadly available.; Tracking task requires the ground-truth initial hand pose.; Wrist does not move and wrist angles are not estimated.; Landmarks derived from joint angles via a default hand model, not user anatomy.; Prompted gesture stages rather than free object manipulation for most data.

## [432] A Benchmark Dataset for Event-Guided Human Pose Estimation and Tracking in Extreme Conditions (NeurIPS 2024, dataset, S4)
Source: https://papers.nips.cc/paper_files/paper/2024/file/f304e427cfe6bb762fe1bf18516c8a87-Paper-Datasets_and_Benchmarks_Track.pdf; confidence HIGH.
Field cannot yet: The field cannot yet track multiple people's poses with stable identities under real low light and heavy motion blur.
Stated limitations:
- Only a simple fusion baseline is offered; better fusion is left open. [6 Conclusion and Future Work]
- Annotating poses directly on degraded frames is unreliable, requiring a sharp reference camera. [2.2]
- RGB-only tracking misses people in extreme conditions. [5.2 Multi-Person Pose Tracking]
- Adding events raises false positives. [5.2 Multi-Person Pose Tracking]
Open problems listed:
- Existing pose and tracking datasets cover only well-lit, blur-free conditions.
- Low-light human datasets are small and hard to collect due to privacy and annotation difficulty.
- Synthetic blur differs from real blur; real-blur annotation is very hard.
- No prior event-based multi-person pose or multi-object tracking dataset.
- Better RGB-event fusion methods.
- Trade-off between missed detections (RGB) and false positives (events) in tracking.
Benchmark gaps:
- EHPT-XC / mAP@0.5:0.95: RGB-only 22.7-25.1; best RGB+event (DEKR, proposed fusion) 37.3.
- EHPT-XC / MOTA / IDF1: Best MOTA 47.37 (ByteTrack, RGB+event); IDF1 at most 22.72; RGB-only MOTA 33.19.
Restrictive assumptions: Custom triplet camera rig with two beam splitters and hardware-synchronized trigger to obtain sharp reference frames.; Low light created deliberately with ND filters and aperture adjustment; blur via 16x exposure.; 2D keypoints only (14 joints), no 3D.; Bottom-up pose models and tracking-by-detection evaluated after training on this dataset.

## [433] Pedestrian-Centric 3D Pre-collision Pose and Shape Estimation from Dashcam Perspective (NeurIPS 2024, dataset, S4)
Source: https://papers.nips.cc/paper_files/paper/2024/file/2c428bb07062012236519b589db63f34-Paper-Conference.pdf; confidence HIGH.
Field cannot yet: The field cannot yet recover metrically grounded 3D human pose and global position from uncalibrated in-the-wild monocular video of rare dynamic events.
Stated limitations:
- Small dataset lacking camera and scene metadata. [6 Conclusion, Limitations]
- Two-stage design propagates 2D errors. [6 Conclusion, Limitations]
- Not real-time; needs pre-selected boxes. [6 Conclusion, Limitations]
- No 3D scene layout, so absolute errors are large. [5.4 Comparison with the state-of-the-art]
- True in-the-wild 3D ground truth is infeasible. [1 Introduction]
Open problems listed:
- Scarce in-the-wild data of pre-collision poses; dashcam or surveillance the only source.
- No real 3D ground truth in the wild.
- Missing camera parameters, vehicle speed, global pedestrian position and direction.
- Lower-limb occlusion and dynamic backgrounds.
- Generic pose datasets do not transfer to emergency poses.
Benchmark gaps:
- PVCP / MPVE / MPJPE_14j (mm): PPSENet MPVE 257.75, MPJPE_14j 218.61; one-stage PARE has lower MPJPE_14j (191.97).
- PVCP / MPVE (mm): VIBE with official weights reaches 849.09 mm, showing poor transfer of generic models.
Restrictive assumptions: Pre-selected bounding-box sequences of the colliding pedestrian.; Offline processing of monocular dashcam video.; 3D labels are semi-automatic pseudo ground truth from existing estimators corrected with an SMPL annotation tool, not measured 3D.; No camera intrinsics or global trajectory.

## [434] Muscles in Time: Learning to Understand Human Motion In-Depth by Simulating Muscle Activations (NeurIPS 2024, dataset, S4)
Source: https://arxiv.org/html/2411.00128; confidence HIGH.
Field cannot yet: The field cannot yet estimate muscle activations for whole-body motion involving object interaction with unknown external forces.
Stated limitations:
- Simulated data carry an unavoidable sim-to-real gap. [6 Discussion, Limitations]
- Object interactions mostly excluded for lack of reaction forces. [6 Discussion, Limitations]
- Included object motions assume weightless objects. [6 Discussion, Limitations]
- Discarded non-converging simulations bias category distribution. [6 Discussion, Limitations]
- Generic musculoskeletal models, not subject-specific. [3 The Muscles In Time dataset]
Open problems listed:
- Scarcity of real EMG and muscle activation data.
- Sim-to-real gap of simulated muscle activations.
- Lack of reaction forces for non-foot contact and object interaction.
- Unknown object mass in manipulation motions.
- Simulation non-convergence and compute cost.
- Unequal ethnicity and body-weight representation.
Benchmark gaps:
- MinT lower body / Pearson correlation (all motions): Best transformer PCC 0.54; VQ-VAE 0.40.
- MinT upper body / SMAPE / PCC (all motions): Best transformer SMAPE 107.7 and PCC 0.55.
Restrictive assumptions: Input motion from marker-based mocap (AMASS subsets) converted to SMPL.; Generic validated OpenSim models; height and weight approximated from SMPL shape.; Ground reaction forces estimated, no measured external or object forces.; Manual subject-specific marker adjustments (semi-automatic pipeline).; Offline, compute-intensive simulation.

## [436] Text to Blind Motion (NeurIPS 2024, dataset, S4)
Source: https://arxiv.org/pdf/2412.05277; confidence HIGH.
Field cannot yet: The field cannot reliably capture or predict atypical, object-mediated human motion (e.g., cane use) in the wild without expensive wearable mocap.
Stated limitations:
- Small participant pool; more diverse participants needed to expose further biases. [5 Limitations]
- Capture hardware is expensive, limiting scale. [5 Limitations]
- In-the-wild motion capture is not solved; IMU suit needs frequent recalibration and manual filtering of tracking failures. [2 Related Work]
- Vision-based 3D keypoint inference was unreliable in their setting; AlphaPose failed frequently. [2 Related Work]
- Pre-training on a large general dataset gives mixed results because of bias and domain shift. [4 Experiments]
- Rare motion scenarios remain challenging for current models. [4 Experiments]
Open problems listed:
- Motion capture in the wild remains an open challenge
- No 3D motion dataset includes people with disabilities; motion models do not model pedestrians with disabilities
- Vision-based 3D keypoint inference unreliable in dense, occluded, object-interacting scenes
- Generalization of motion-language models to rare and diverse human attributes
- Pre-training on general datasets introduces bias and domain shift with mixed results
- Generalization to rare motion scenarios such as obstacle interactions and varying terrain
- Larger and more diverse participant pools
- Lower-cost scalable capture to replace expensive mocap suits
Benchmark gaps:
- BlindWays / R Top1 (text-to-motion): Best model reaches 0.060 vs 0.106 for real data; Motion-X-trained models only 0.041-0.046.
- BlindWays / FID (text-to-motion): Motion-X-trained models score 11.203 (HumanML3D) and 15.002 (MotionGPT) vs 3.340 when trained on BlindWays.
- BlindWays / Arm and aid FDE: Motion-X pretrain + BlindWays finetune gives worse arm FDE (0.99/1.07) than BlindWays-only (0.77/0.81).
- BlindWays / ADE (motion prediction): MotionGPT ADE 3.01 vs about 0.45 for CVAE/DLow/MDN; paper calls this only an initial step.
Restrictive assumptions: Wearable Xsens IMU suit (18 sensors, one on the mobility aid) with frequent recalibration along each route; Manual inspection to remove tracking-failure skeletons; 11 participants on 8 pre-engineered routes in one urban area; Researchers following participants with chest-mounted phone; chest GoPro for egocentric video; Prediction setting of 0.5 s past motion to 9.5 s future

## [438] Codec Avatar Studio: Paired Human Captures for Complete, Driveable, and Generalizable Avatars (NeurIPS 2024, dataset, S7)
Source: https://proceedings.neurips.cc/paper_files/paper/2024/file/9712b78386cebdc3db7f1a48c2d20edb-Paper-Datasets_and_Benchmarks_Track.pdf; confidence HIGH.
Field cannot yet: The field cannot yet build high-fidelity, generalizable full-body and hand avatars from lightweight sensors without studio-scale paired capture.
Stated limitations:
- Release unlikely to support multi-identity relightable head decoders. [4 Limitations and Potential Negative Impact]
- Datasets miss the long tail of human expressivity. [4 Limitations and Potential Negative Impact]
- Goliath-4 has only four subjects. [4 Limitations and Potential Negative Impact]
- Raw data size forces lossy compression plus spatial, camera and temporal downsampling for release. [2.1 Ava-256]
- No assets for full-body phone data. [2.2 Goliath-4]
- Clothing complicates body reconstruction. [2.2 Goliath-4]
Open problems listed:
- Paired captures are unavailable to researchers outside industrial labs
- Multi-identity relightable head decoders remain hard with the release
- Long tail of human expressivity (sweat, tiredness, blood flow) not captured
- Converting low-quality capture (phone, full-body) into high-quality heads and hands is limited by four subjects
- Clothed full-body reconstruction is hard since body models come from tight-fit clothing
- Storage and distribution of petabyte-scale capture data
- Reliable pseudo ground truth from headset images to face deformations
- Misuse risk: impersonation and disinformation
Restrictive assumptions: About 170-camera 2.4 m head dome and about 230-camera 5.5 m full-body dome; Quest Pro headset IR cameras, with an augmented 10-camera headset for ground truth; Person-specific (personalized) avatar models for relightable heads, hands and bodies; Hands captured separately (left and right) in a relightable dome; no object interaction; Released data downsampled to about 80 cameras, 7.5-15 fps, reduced resolution, AVIF compression

## [444] TAPVid-3D: A Benchmark for Tracking Any Point in 3D (NeurIPS 2024, benchmark, S5)
Source: https://arxiv.org/pdf/2407.05921; confidence HIGH.
Field cannot yet: The field cannot yet recover metrically consistent long-range 3D point tracks from monocular video, even where 2D tracking is accurate.
Stated limitations:
- Limited domain coverage and imperfect automatic annotations. [4 Limitations and Responsible Usage]
- Only solid, opaque objects are evaluated. [4 Limitations and Responsible Usage]
- Ground-truth noise from source data: ADT misalignment, LIDAR noise, under-constrained Gaussian splats, numerical error. [3 Dataset]
- 3D tracking is far worse than 2D tracking for all baselines. [4 Results]
- Model-based 3D pose tracking needs known 3D models. [1 Introduction]
- SfM fails on dynamic content. [4 Results]
Open problems listed:
- No real-world benchmark for 3D point tracking prior to this work
- Synthetic 3D benchmarks have a significant domain gap
- Depth noise, temporal scale drift and spatial scale inconsistency in monocular 3D tracking
- SfM pipelines fail on moving content
- Monocular depth struggles in complex outdoor scenes
- Scale consistency across trajectories
- Only solid opaque objects can be evaluated
- Domain coverage is incomplete
- Automatic annotations can be noisy
- Biases inherited from lab participants and six US cities
Benchmark gaps:
- TAPVid-3D full_eval / 3D-AJ (median scaling): Best average 3D-AJ is 9.3 (CoTracker or BootsTAPIR + COLMAP) vs static baseline 4.9, while the same trackers reach 2D-AJ up to 59.1.
- TAPVid-3D DriveTrack / 3D-AJ: ZoeDepth-based methods score 5.0-5.4, near the static baseline 3.9.
- TAPVid-3D PStudio / 3D-AJ: COLMAP-based methods score 6.1-8.1 because moving content is not reconstructed.
- TAPVid-3D full_eval / 3D-AJ (per-trajectory scaling): Best average still only 20.6 (BootsTAPIR + COLMAP).
- TAPVid-3D / 3D-AJ: TAPIR-3D, trained only on synthetic video, averages 3.1, below the static baseline.
Restrictive assumptions: Monocular RGB input with scale ambiguity resolved by rescaling predictions to ground truth (global median or per-trajectory); Ground truth from multi-sensor sources: Aria Digital Twin replicas, Waymo LIDAR plus box tracks, Panoptic Studio multi-view Gaussian reconstructions; DriveTrack ground truth assumes vehicle rigidity; Operator hands are not modelled in ADT digital replicas and are masked for visibility; Evaluation at 256x256 resolution

## [460] OctoNet: A Large-Scale Multi-Modal Dataset for Human Activity Understanding Grounded in Motion-Captured 3D Pose Labels (NeurIPS 2025, dataset, S4)
Source: https://proceedings.neurips.cc/paper_files/paper/2025/file/14950adea25005f89545688fe97fe5ea-Paper-Datasets_and_Benchmarks_Track.pdf; confidence HIGH.
Field cannot yet: The field cannot yet produce 3D human pose from any single sensing modality that holds up across unseen scenes and users.
Stated limitations:
- Mocap requires standardized garments, which attenuate thermal signals. [Limitations and future work]
- Uniform attire reduces RGB appearance diversity. [Limitations and future work]
- Lab-only capture. [Limitations and future work]
- LiDAR not included. [Limitations and future work]
- Some modalities lack established models. [Experiments]
- Vision models collapse under scene shift. [Experiments, HAR]
Open problems listed:
- Multi-modal fusion beyond vision-language models
- Cross-modal understanding without extensive aligned data
- Sensing foundation models for non-visual sensors
- Cross-modal data generation and modality translation
- Robust perception under varying environmental and sensory configurations
- Domain shift across scenes and users, especially for vision and RF
- Underexplored modalities (IRA, ToF) lacking established models
- Mocap garments limiting thermal and RGB realism
- Lab-only data limiting in-the-wild generalization
- LiDAR not covered
Benchmark gaps:
- OctoNet / MPJPE (3D HPE): Best in-domain errors are 131.4 mm (depth) and 133.3 mm (RGB); RGB reaches 473.9 mm cross-scene.
- OctoNet / HAR top-1 cross-scene: RGB Swin-T falls to 12.1% (10-class); best fusion keeps 52.7% cross-scene.
- OctoNet / MPJPE IRA and acoustic: 244.0-398.0 mm and 243.6-441.4 mm respectively.
Restrictive assumptions: OptiTrack optical mocap ground truth with standardized mocap garments; Laboratory capture in three scenes; Common architectures trained from scratch, not modality-specific state of the art; No person cropping for vision inputs; Single-person full-body activities; no object pose labels mentioned

## [461] EPFL-Smart-Kitchen: An Ego-Exo Multi-Modal Dataset for Challenging Action and Motion Understanding in Video-Language Models (NeurIPS 2025, dataset, S1 S2 S4)
Source: https://arxiv.org/pdf/2506.01608; confidence HIGH.
Field cannot yet: The field cannot yet derive precise hand and body kinematics, or reason about them, from natural ego-exo video without heavy multi-camera instrumentation.
Stated limitations:
- VLMs fail on context, distances, timings and kinematics. [4.1 Lemonade results]
- Vision plus language is insufficient for precise kinematics. [4.1 Lemonade results]
- Hand detectors fail on small, occluded hands in the exocentric views. [Supp. C, 2D keypoint estimation]
- Pseudo ground-truth 3D pose has centimetre-level error vs triangulated manual 2D annotations: about 6.22 cm body, 3.30 cm hand. [3 Dataset, pose estimation]
- Action segmentation remains weak. [4.3 Action segmentation]
- Single kitchen; demographic coverage limited. [Discussion]
Open problems listed:
- Fragmentation of datasets: body without hands, hands without body context
- Missing goal-directed action and eye-movement data
- VLMs cannot infer distances, timings or kinematics from video
- Fine-grained, long-tailed action recognition
- Pose-based action segmentation
- Situated full-body (body, hands, gaze) motion generation
- Demographic representation including patients
- Using additional modalities (IMU, depth)
Benchmark gaps:
- EPFL-Smart-Kitchen-30 / Action recognition top-1 (all classes): Best action top-1 is 40.03%; tail-class action top-1 at most 19.44%.
- EPFL-Smart-Kitchen-30 / Action segmentation F1: About 35.2% (verbs) and 35.0% (nouns).
- Lemonade / QA accuracy: VLMs perform poorly on distances, timings, and body kinematics questions.
Restrictive assumptions: One instrumented kitchen with nine static Azure Kinect RGB-D cameras, calibrated and audio-synchronized; HoloLens 2 headset for egocentric video and gaze; IMUs on kitchen equipment (fridge, cupboards, knife, spatula), not on the body; 3D pose is pseudo ground truth from RTMPose, Kinect body tracking and HoloLens hand tracking fused with SMPL/MANO fitting; 16 healthy subjects, four recipes

## [462] Intend to Move: A Multimodal Dataset for Intention-Aware Human Motion Understanding (NeurIPS 2025, dataset, S4 S2)
Source: https://proceedings.neurips.cc/paper_files/paper/2025/file/0743b22dad0ac0ffe0d194153568f641-Paper-Datasets_and_Benchmarks_Track.pdf; confidence HIGH.
Field cannot yet: The field cannot yet generate or predict scene-aware human motion that actually accomplishes a stated goal, nor measure whether it does.
Stated limitations:
- No hand or finger articulation. [5 Limitations and Future Directions]
- No egocentric vision, gaze, or conversational audio. [5 Limitations and Future Directions]
- Limited scope: two people, indoors. [5 Limitations and Future Directions]
- No metric checks whether intention is fulfilled. [4.5 Discussion]
- Models cannot ground semantic goals into kinematics. [4.5 Discussion]
- Capture trade-offs across methods. [2.2 Related work]
Open problems listed:
- Grounding high-level intentions into physically and socially coherent motion
- Pre-trained encoders (CLIP, ResNet) not compatible with physically plausible motion generation
- Absence of intention-fulfillment metrics; ADE/FDE and MCE insufficient
- Physically implausible outputs (penetration, floating)
- Accuracy vs visual realism trade-off in capture methods
- Missing hand and finger articulation, egocentric vision, gaze, conversational audio
- Behavioral diversity across age and personality
- Outdoor and larger-group interactions
Benchmark gaps:
- I2M / ADE@1: Intention-text conditioning 1.573 and Pair Multimodal 1.220 vs Pair Trajectory 1.013.
- I2M / MMADE@20: Self Intention Text 1.140 and RGB 1.159 vs Pair Trajectory 0.709; semantic inputs do not improve coverage of plausible futures.
- I2M / Contact@1: Intention-text conditioning 0.672 vs 0.858 for Self Trajectory.
Restrictive assumptions: 12-camera OptiTrack optical mocap with small markers on everyday clothing; Four Kinect RGB-D cameras at room corners; Indoor home-like environment, two participants; Scripted textual instructions drive intentions; Body-only kinematics, no hand pose

## [469] HumanoidGen: Data Generation for Bimanual Dexterous Manipulation via LLM Reasoning (NeurIPS 2025, benchmark, S3)
Source: https://arxiv.org/pdf/2507.00833; confidence HIGH.
Field cannot yet: The field cannot yet produce bimanual dexterous demonstration data for long-horizon, deformable or contact-rich tasks without human annotation or teleoperation.
Stated limitations:
- Human annotation still needed for new asset categories. [Appendix D Limitations]
- Simulator cannot handle deformables or fluids. [Appendix D Limitations]
- Motion-planner control cannot handle continuous-adjustment tasks. [Appendix D Limitations]
- Policies decline on long-horizon tasks with limited data. [5 Experiments]
- LLM planning fails without sufficient prompts or annotations, motivating MCTS. [3 Method]
Open problems listed:
- Lack of bimanual dexterous humanoid simulation tasks and demonstrations
- Cross-embodiment adaptation of real-world data remains open
- Large-scale real-world data collection remains costly
- Fully automatic annotation of new asset categories
- Deformable and fluid object simulation
- Tasks with ambiguous or dynamic objectives (push-T, cloth flattening)
- Long-horizon bimanual tasks with limited data
Benchmark gaps:
- HGen-Bench / Policy success rate: Blocks Stack Hard and Handover and Storage: 0% for both DP and DP3 with 20-100 demonstrations.
- HGen-Bench / Policy success rate: Blocks Stack Easy: DP3 22.8% at 100 demos, 0% below; Empty Cup Place DP3 at most 33.3%.
- HGen-Bench / Demonstration generation success: Average over 50%; bimanual long-horizon tasks below 75%.
Restrictive assumptions: Simulation only (ManiSkill3) for task generation; Manual spatial annotations of asset keypoints and axes and hand atomic operations; Rigid and articulated objects only; Low-level motion planner toward target poses; LLM planner (e.g., DeepSeek-R1) with MCTS

## [470] DexGarmentLab: Dexterous Garment Manipulation Environment with Generalizable Policy (NeurIPS 2025, benchmark, S3)
Source: https://arxiv.org/pdf/2505.11032; confidence HIGH.
Field cannot yet: The field cannot yet simulate or perceive deformable objects under bimanual dexterous contact accurately enough to transfer policies without real data.
Stated limitations:
- PBD garment simulation is unstable. [Appendix I.1.1 PBD]
- FEM does not capture garment deformation. [Appendix I.1.2 FEM]
- Single-garment, fixed-base tasks only. [Appendix I.2]
- Affordance model fails on occluded or highly deformed regions. [Appendix I.3]
- Non-standard garments break the policy. [Appendix I.3]
- Sim-to-real gap; sensitivity to point cloud noise. [6.3.2 Real-World Experiments (Way 2)]
Open problems listed:
- Realistic simulation of fabric and of deformable-dexterous-hand interaction
- PBD instability and penetration; FEM cannot deform
- Multi-garment tasks
- Mobile dual-arm platforms for household use
- Grasp-point prediction under occlusion and heavy deformation
- Generalization to non-standard garment geometries
- Sim-to-real gap and point-cloud noise sensitivity
- Efficient RL for long-horizon deformable tasks
Benchmark gaps:
- DexGarmentLab sim / Success rate: Baselines DP/DP3 at 0.41-0.67; HALO best on Wear Bowlhat only 0.72, Fold Dress 0.76.
- Real world (Way 1) / Success count: HALO Wear Scarf 11/15; DP3 7/15.
- Real world (Way 2) / Success rate sim-only: 53.3% Hang Trousers, 60.0% Wear Hat without real data.
Restrictive assumptions: Isaac Sim with PBD/FEM garment models and tuned parameters; A single expert demonstration per task, transferred via garment structural correspondence; Fixed-base dual UR10e + ShadowHand in simulation; Garment and object segmentation with SAM2 from a single RGB-D camera; Single garment per task

## [475] From Pose to Muscle: Multimodal Learning for Piano Hand Muscle Electromyography (NeurIPS 2025, dataset, S4 S7)
Source: https://proceedings.neurips.cc/paper_files/paper/2025/file/a7d80c990c77ae2570087243ec802314-Paper-Conference.pdf; confidence HIGH.
Field cannot yet: Infer fine hand-muscle activation from video-based hand pose in a way that generalizes to unseen users and unseen tasks.
Stated limitations:
- Dataset contains only expert pianists, so it does not generalize to broader populations; wrist-forearm muscles are not covered. [6 Limitations and Future Work]
- Seven tasks are insufficient for complex bimanual coordination in advanced repertoire. [6 Limitations and Future Work]
- With keystroke input only, the CodeTalker baseline beats PianoKPM Net. [6 Limitations and Future Work]
- Generalization across users and tasks remains an open challenge. [6 Limitations and Future Work]
- Single-frame vision-based 3D hand annotations (HaMeR) are jittery and erroneous, and occlusion and low light are hard to overcome. [Appendix B.3 Dataset Limitations]
- Only 21 hand joint positions are captured; no hand mesh, elbow, shoulder or upper body. [Appendix B.3 Dataset Limitations]
- EMG sensors detach due to perspiration, so sensor placement varies and affects fidelity. [Appendix B.3 Dataset Limitations]
- HaMeR depth (Z) estimates were not accurate enough, so 2D keypoints from a second view replace depth cues. [Appendix (hand pose annotation)]
Open problems listed:
- Inferring EMG from posture is underexplored because there is no one-to-one pose-to-muscle mapping.
- Generalization across users and tasks under electrode placement, anatomy and kinematics variation.
- Dataset bias toward professional pianists; need evaluation across ages, expertise and physical conditions.
- Vision-based hand pose is limited by occlusion, low light and jitter.
- Covering upper-body and wrist-forearm muscle synergies.
- Biometric privacy risk of combined EMG, motion and keystroke data.
Benchmark gaps:
- PianoKPM (Cross-Task held-out) / RMSE / OTD: 0.264 / 0.152, versus 0.134 / 0.031 in-distribution
- PianoKPM (Cross-User held-out) / RMSE / OTD: 0.209 / 0.095, worse than in-distribution
- PianoMotion10M / qualitative: Pretrained pose-to-EMG prior gives unsatisfactory synthetic EMG; no paired EMG, so no quantitative evaluation
Restrictive assumptions: Expert pianists only, on a fixed piano setup; Surface EMG electrodes on six hand muscles needed for ground truth; 3D hand pose comes from monocular HaMeR per frame, with no multi-camera calibration; Keystroke sensing hardware for the multimodal variant; Single domain (piano), with 7 tasks

## [476] IndEgo: A Dataset of Industrial Scenarios and Collaborative Work for Egocentric Assistants (NeurIPS 2025, dataset, S6 S3)
Source: https://arxiv.org/pdf/2511.19684; confidence HIGH.
Field cannot yet: Reliably understand two-person collaborative industrial manipulation from egocentric video, including who does what when hands are close.
Stated limitations:
- Focused only on industrial tasks in lab-like workshops, which limits generalization to household, healthcare or everyday scenes. [Appendix O Limitations]
- Only 20 participants (15 male, 5 female); the sample is small. [Appendix O Limitations]
- Constrained tools and few lab environments; may not reflect factory floors, heavy machinery or chaotic scenes. [Appendix O Limitations]
- Single wearable device (Project Aria); static exo cameras with known occlusions; sync and alignment errors possible. [Appendix O Limitations]
- Baselines are simple zero-shot prompting with small 7B/8B VLMs and are not upper bounds. [Appendix O Limitations]
- Annotation granularity and consistency vary across participants; self-annotation may be subjective. [Appendix O Limitations]
- Data collection was not extended to other industrial sites because of privacy, data protection and IP. [Appendix A]
Open problems listed:
- Recognizing actions and gestures in real time in industrial settings.
- Identifying and localizing tools and parts under visual occlusion.
- Adapting to varying lighting and environmental conditions.
- Recognizing small or domain-specific tools.
- Distinguishing the wearer's actions from a collaborator's in two-person work.
- Temporal reasoning for visually similar opposite actions.
- Long-video summarization and understanding (up to 68 min).
- Cross-view and cross-modal alignment between ego, exo, gaze and audio.
- Context-dependent usefulness of audio and gaze modalities.
- Privacy, consent and worker-surveillance concerns for always-on egocentric AI.
Benchmark gaps:
- IndEgo Mistake Detection (ego, zero-shot) / F1: 24.8 to 41.1 across VLMs; best GFT 41.1
- IndEgo reasoning QA (singular actions) / accuracy: VLMs 57.6 to 64.1% versus humans 90.0%
- IndEgo collaborative task understanding / accuracy: Zero-shot 35.2% (GFT); fine-tuned baseline 42.1%
- IndEgo action recognition (top 100 verbs) / accuracy: 57.6 to 64.1%, with frequent attach/detach and open/close confusion
- IndEgo mistake detection ego+exo (10 tasks) / F1: Best 0.44 (GFT zero-shot)
Restrictive assumptions: Single headset type (Meta Project Aria) for egocentric capture; Hand pose and point clouds come from Meta MPS processing, not ground truth; Controlled lab facility with scripted or semi-scripted tasks; Static exocentric cameras, absent in some environments

## [477] Don't call it privacy-preserving or human-centric pose estimation if you don't measure privacy (NeurIPS 2025, position, S4)
Source: https://proceedings.neurips.cc/paper_files/paper/2025/file/bd20ff18345f0ded89242bf9ef58e46c-Paper-Position_Paper_Track.pdf; confidence HIGH.
Field cannot yet: Report a standardized, measurable privacy score alongside accuracy for pose estimation systems, including depth-based ones.
Stated limitations:
- The proposed risk levels are illustrative and are not a metric. [3.2 A risk-based view based on regulations]
- Risk levels alone are insufficient to compare models in practice; proposed indicators are not definitive. [3.3 Toward practical privacy indicators]
- Privacy labels highlight legal exposure but do not measure privacy. [3.3.3]
Open problems listed:
- No standard metric to compare privacy levels across sensing modalities.
- Non-RGB sensing is not inherently privacy-preserving; skeletons and motion are biometric identifiers.
- Anonymization (low resolution, blur, pixelation) is not a guarantee and degrades keypoint accuracy.
- Hardware alternatives (event, IR, low-res depth) have cost and residual physiological leakage.
- Hybrid pipelines still expose partially informative raw data.
- Federated learning can leak via gradients or weights.
- Volumetric mesh representations encode gender, age and health even without RGB.
- Distributed edge-fog-cloud deployments add transmission and storage risk not considered in evaluation.
- Privacy-accuracy trade-offs are rarely measured or reported.
- Synthetic data can memorize and replicate sensitive patterns.
- Not storing data is not sufficient; live streams, APIs and side channels leak.
- Lack of standardized benchmarks, community incentives and shared deployment-grounded vision.
Benchmark gaps:
- HPE benchmarks generally (COCO, Human3.6M, etc.) / privacy score: No privacy score is ever reported; benchmarks evaluate clean RGB input in ideal conditions
Restrictive assumptions: Position paper, no method; it critiques the assumption that accurate HPE needs detailed visual input

## [483] Do Egocentric Video-Language Models Truly Understand Hand-Object Interactions? (ICLR 2025, benchmark, S1)
Source: https://arxiv.org/pdf/2405.17719; confidence HIGH.
Field cannot yet: Reliably distinguish fine-grained hand-object interaction verbs from egocentric video.
Stated limitations:
- Method targets HOI; egocentric scenarios include broader actions such as observation, dancing or sports. [Appendix A Limitations]
- Object recognition cannot be enhanced well through text supervision alone. [Appendix A Limitations]
- Models are continually pretrained, not trained from scratch, due to compute limits. [4.1 Experimental Settings]
- On LaViLa-Large, overall performance still falls short of HelpingHands. [Appendix C.3.1]
Open problems listed:
- Fine-grained HOI understanding: distinguishing verb and noun changes in descriptions.
- Verb recognition is harder than noun recognition; feature spaces are object-centric.
- Existing contrastive objectives lack fine-grained negative supervision; EgoNCE positive expansion blurs fine HOI distinctions.
- Open-vocabulary egocentric HOI efforts limited to kitchens or labs, or to easy recognition.
- Generalizing to non-HOI egocentric activities.
- Improving object recognition beyond text supervision.
- Privacy concerns of egocentric video; risk of misrecognizing unsafe actions.
Benchmark gaps:
- EgoHOIBench / action accuracy (zero-shot): Baselines 26.40% (EgoVLPv2), 30.16% (EgoVLP), 36.85% (LaViLa); best after EgoNCE++ 63.17% (LaViLa++)
- EgoHOIBench / verb accuracy: 36.10 to 46.61% for baselines, versus 63.40 to 74.33% noun accuracy
- EK100-CLS zero-shot / action top-1: LaViLa++ 14.67% (LaViLa 10.14%)
- ActionBench / accuracy: LaViLa 79.89%, LaViLa++ 91.18% vs human 92.0%
Restrictive assumptions: Video-text matching over short (about 1 s) Ego4D clips with 4 sampled frames; Negatives generated by an LLM (LLaMA3-8B), which may introduce vocabulary bias; No 3D or geometric HOI reasoning; recognition only

## [487] VTDexManip: A Dataset and Benchmark for Visual-tactile Pretraining and Dexterous Manipulation with Reinforcement Learning (ICLR 2025, dataset, S6 S1)
Source: https://proceedings.iclr.cc/paper_files/paper/2025/file/e19b6f65791e350347bcff8a3955cb5b-Paper-Conference.pdf; confidence HIGH.
Field cannot yet: Learn bimanual dexterous manipulation from human visual-tactile data with high success, or use rich non-binary tactile signals across sim and real.
Stated limitations:
- Vision information does not transfer to the tactile modality after joint pretraining; exploiting discrete tactile signals is open. [5.5 Discussion, Limitation and Future Work]
- Only binary tactile signals are studied; pressure, shear, sensor variation and sim-to-real remain. [5.5]
- High-fidelity simulation of object-sensor interaction is a major unsolved challenge. [5.5]
- Pretraining methods cannot handle raw tactile signals; they rely on thresholding. [5.5 Adaptation to Various Tactile Sensors]
- Masking vision after joint pretraining gives a small drop; tactile does not absorb visual knowledge. [5.3]
Open problems listed:
- Exploiting the discrete nature of tactile signals in pretraining.
- Using pressure values, shear forces and sensor sensitivity variation.
- Simulation-to-reality gap for tactile sensing.
- High-speed, high-fidelity simulation of object-sensor contact.
- Integrating large vision-language models with tactile data.
- Policy learning across tactile sensors with different physical principles.
- Robustness to tactile noise.
- Large-scale dexterous data collection beyond parallel grippers.
Benchmark gaps:
- VTDexManip benchmark, Bimanual Hand-over / success rate: Best method 45.5% seen, 26.6% unseen objects
- VTDexManip benchmark, In-hand Reorientation / success rate: Best 62.2% seen, 55.1% unseen
- VTDexManip benchmark, all tasks / mean success rate: Best VT-JointPretrain 74.3% seen, 65.7% unseen; vision-only non-pretrained 24.0 / 22.2%
Restrictive assumptions: Binary thresholded tactile signals only; Wearable tactile glove plus HoloLens2 egocentric video for human data; 5 subjects; Downstream policies are trained with RL in simulation (Isaac Gym) with a frozen encoder; Real deployment uses a Shadow Hand with 20 piezoresistive sensors and teacher-student distillation with domain randomization; No hand or object 3D pose reconstruction from the human data

## [495] ImDy: Human Inverse Dynamics from Imitated Observations (ICLR 2025, dataset, S4)
Source: https://arxiv.org/pdf/2410.17610; confidence HIGH.
Field cannot yet: Estimate human joint torques and interaction forces during contact with objects or other people from kinematics alone.
Stated limitations:
- Simulated data can be unnaturally jittery, and the humanoid's physical properties differ from real humans (sim2real). [6 Discussion]
- Only ground reaction forces are modelled; other external forces and interaction with other entities are absent. [6 Discussion]
- ImDyS is only a first-step baseline. [6 Discussion]
- Poor performance on non-gait data because real non-gait training data are scarce. [Appendix B]
- Performance degrades with ground-truth data quality. [Appendix B, Figure 14]
Open problems listed:
- Dynamic factors such as torques and GRF are overlooked by vision-based motion understanding.
- Inverse dynamics cannot be measured non-intrusively; needs GRF measurement and lab setups.
- Sim2real gap of simulated dynamics data.
- External forces beyond GRF and interaction with other entities.
- Real data scarcity and quality for non-gait motions.
Benchmark gaps:
- AddBiomechanics / mPJE torque (Nm/kg): ImDyS 0.1626 vs baseline 0.1699; jumping motion fails
- GroundLink / mPJE GRF (N/kg), per foot: ImDyS 0.986 left / 1.149 right; zero-shot
Restrictive assumptions: Kinematic input from mocap (AMASS-derived SMPL/markers), not video; Physics simulator humanoid (SMPL, joint-actuated) differs from human anatomy; Only ground contact external forces; no hand-object or human-object forces; 30 FPS motion input

## [498] Pedestrian Motion Reconstruction: A Large-scale Benchmark via Mixed Reality Rendering with Multiple Perspectives and Modalities (ICLR 2025, dataset, S4 S2)
Source: https://proceedings.iclr.cc/paper_files/paper/2025/file/f3342358d0792ea201dc86d69570946b-Paper-Conference.pdf; confidence HIGH.
Field cannot yet: Reconstruct accurate global human motion from moving cameras or arbitrary multi-view setups without data-hungry optimization.
Stated limitations:
- Domain gap between mixed-reality simulated data and real-world data is a concern. [4.4 Domain Gap Evaluation]
- Egocentric videos are captured with VR glasses in virtual environments, introducing a domain gap. [4.2 Egocentric Perspective]
- Egocentric ground truth is uncertain, so the metrics are only references. [4.2 Egocentric Perspective]
Open problems listed:
- Precise pedestrian motion annotation in a global coordinate system from real-world capture.
- Capturing rare, safety-critical scenarios such as collisions.
- Disentangling human and camera motion from moving cameras.
- Fusing multi-view video from arbitrary static and moving cameras.
- Paired LiDAR-RGB capture with accurate 3D pose annotation; long-tail poses.
- Real-synthetic domain gap.
Benchmark gaps:
- PMR third-person RGB / W-MPJPE (mm): Best RGB world-space SLAHMR 378.4; camera-space HybrIK 2084.0
- PMR egocentric / MPJPE (mm) / Thead: EgoEgo 192.3 / 587.5, worse than on ARES, Kinpoly-MoCap and GIMO
- PMR LiDAR+RGB / W-MPJPE (mm): LPFormer* 71.3, but fails on long-tail poses
- nuScenes pedestrian detection / AP: 0.088 with nuScenes only, 0.094 with 40% PMR
Restrictive assumptions: Mixed reality: real MoCap human in a VR headset inside a CARLA virtual scene; Sensor data (RGB, LiDAR) rendered in simulation; Ground truth from optical MoCap

## [511] EgoDex: Learning Dexterous Manipulation from Large-Scale Egocentric Video (ICLR 2026, dataset, S6 S1 S3)
Source: https://arxiv.org/pdf/2505.11709; confidence HIGH.
Field cannot yet: Obtain accurate hand tracking under heavy occlusion and fast motion at scale, together with object pose, in diverse scenes.
Stated limitations:
- Limited background and scene diversity (tabletop only). [7 Conclusion]
- Hand annotations are model predictions and can be imperfect under heavy occlusion or fast motion. [7 Conclusion]
- Test set is in-distribution only; OOD tasks are evaluated separately. [5 Experiments]
- A prohibitive embodiment gap remains between humans and robots. [6 Research Use Cases]
Open problems listed:
- Unclear what data to collect and how to collect it at scale for robot manipulation.
- Embodiment gap between humans and robots.
- Scene and background diversity.
- Annotation quality under heavy occlusion and fast motion.
- Multimodality of human motion for trajectory prediction.
- Egocentric video generation and world modeling: viewpoint variability, temporal and spatial consistency.
Benchmark gaps:
- EgoDex trajectory prediction (2 s) / avg distance (m): Best 0.038 (EncDec+FM, K=10); BC 0.044 to 0.045
- EgoDex OOD tasks / avg / final distance (m): Stamp Paper 0.099 / 0.162; Blowdry Hair 0.083 / 0.118
- EgoDex horizon 3 s / avg distance (m): 0.053 (Dec+BC)
Restrictive assumptions: Apple Vision Pro with ARKit on-device tracking; annotations are model predictions, not ground truth; Tabletop scenes only; No object pose or object geometry annotation; hands and upper body only; Benchmarks predict hand trajectories, not object state

## [521] InclusiveVidPose: Bridging the Pose Estimation Gap for Individuals with Limb Deficiencies in Video-Based Motion (ICLR 2026, dataset, S4 S7)
Source: https://proceedings.iclr.cc/paper_files/paper/2026/file/6034a661584af6c28fd97a6f23e56c0a-Paper-Conference.pdf; confidence HIGH.
Field cannot yet: Pose estimators cannot yet represent bodies whose skeleton differs from the fixed template, so residual limbs and prostheses are mislocalized or hallucinated as intact limbs.
Stated limitations:
- Distinguishing an occluded limb from an absent limb remains ambiguous even with video and multiple annotators, adding label noise. [Appendix F, Discussion and Future Work]
- Current pose models give unreliable confidence for missing or prosthetic limbs on this data. [Appendix F, Discussion and Future Work]
- The keypoint schema covers human anatomy only and does not include prosthesis-tip joints. [Appendix F, Opportunities for prosthesis-aware modeling]
- Main benchmark is single-frame; multi-frame estimation is left to future extensions. [4.1 Experiment Details]
Open problems listed:
- Pose models that reason about absent joints and residual endpoints rather than assuming a full skeleton.
- Confidence calibration for missing or prosthetic limbs (LiCC low across methods).
- Temporal pose models that represent structural (not temporary) limb absence without propagating hallucinated limbs.
- Prosthesis-aware modeling, including prosthesis end-effectors for contact with the environment.
- Scarcity of data for rare amputation levels and prosthesis designs; privacy constraints on real video.
- Ambiguity between occluded and absent limbs in annotation.
Benchmark gaps:
- InclusiveVidPose (video, PoseTrack-style) / keypoint AP, residual-limb groups: ArmUp and ArmLow AP is almost zero for DCPose and DSTA; LegUp and LegLow AP in the low to mid teens; mean AP 43.2 (DCPose) and 43.7 (DSTA).
- InclusiveVidPose (single frame) / LiCC: LiCC about 60% for many methods; DEKR and ViPNAS have good COCO AP but low LiCC.
- InclusiveVidPose (video) / head AP: About 28 AP for both video models.
Restrictive assumptions: 2D keypoints only; no 3D pose or shape.; Fixed 25-keypoint schema (17 COCO plus 8 residual endpoints); no prosthesis-tip joints.; Videos from YouTube and IPC archives; videos are not redistributed (links only).

## [531] BANZ-FS: BANZSL Fingerspelling Dataset (ICLR 2026, dataset, S3)
Source: https://proceedings.iclr.cc/paper_files/paper/2026/file/3d4c0a618d0acd7921493e4f30395c22-Paper-Conference.pdf; confidence HIGH.
Field cannot yet: Recognition cannot yet reliably resolve fast two-handed handshapes with mutual occlusion and fingertip contacts in uncontrolled video.
Stated limitations:
- Letter frequency imbalance: frequent letters dominate while X and J are underrepresented. [Appendix B, Limitation and Future Work]
- Dialect imbalance: data are heavily skewed toward Auslan, with limited BSL and NZSL. [Appendix B, Limitation and Future Work]
- Benchmark uses only RGB front-view video; the recorded multi-view RGB-D lab streams are not used in experiments. [Appendix B, Limitation and Future Work]
Open problems listed:
- Handshape coarticulation in two-handed fingerspelling.
- Self-occlusion between the two hands.
- Intra-letter variation.
- Rapid inter-letter transitions at fast signing speed.
- Cross-domain generalization (Lab to News and Web).
- Long-tail letter frequency and dialect imbalance.
- Detection that preserves recognizability of segments.
- Recognizing fingerspelling within continuous signing and translation.
Benchmark gaps:
- BANZ-FS Web / IFSR letter accuracy: Best model trained on Full reaches 71.8% on Web; training on Web only gives 55.0% at best.
- BANZ-FS Web / FSD-R AP@Acc0.5: Best (SL-Seg, Full) reaches 30.2% on Web versus 76.3% on Lab.
- Expanded Auslan News / FSR-Context letter accuracy: Gloss-free SLT model 16.4%; ByT5 25.8%; T5 10.2%.
- BANZ-FS / per-letter accuracy: Rare letters X and J about 54% and 41% versus about 83% and 80% for N and A.
Restrictive assumptions: Benchmarks use monocular RGB front-view video only.; Web and broadcast videos are released as URLs only, not redistributed.

## [573] TopoCap: Learning Topology-Agnostic Motion Priors for Monocular Video-to-Animation (SIGGRAPH 2026, dataset, S4)
Source: https://arxiv.org/pdf/2606.12153; confidence HIGH.
Field cannot yet: Template-free video motion capture cannot yet produce physically grounded, globally placed motion for arbitrary or rare skeletons from real footage.
Stated limitations:
- Performance degrades on highly uncommon topologies. [7 Conclusion, Limitations and future work]
- Sensitive to input video quality and to domain gaps in real-world footage. [7 Conclusion, Limitations and future work]
- Needs a predefined skeleton; works in camera space without global trajectory or physical constraints such as foot contact. [7 Conclusion, Limitations and future work]
Benchmark gaps:
- Mobjaverse (video-to-motion) / MPJPE: 179.61 on seen and 192.04 on unseen topologies, versus 52.05 and 62.54 on Truebones Zoo.
- Mobjaverse (reconstruction) / MPJPE: 20.53 versus 5.44 on HumanML3D and 6.88 on Truebones Zoo.
Restrictive assumptions: Target character must be rigged with a predefined skeleton.; Trained and quantitatively evaluated on synthetically rendered videos from Mobjaverse; real-world video shown only qualitatively.; Camera-space output; no global trajectory.; No physical or contact constraints.; Single character; no objects or interaction.

## [578] FurElise: Capturing and Physically Synthesizing Hand Motion of Piano Performance (SIGGRAPH Asia 2024, dataset, S3 S1 S6)
Source: https://arxiv.org/pdf/2410.05791; confidence HIGH.
Field cannot yet: Markerless capture cannot yet produce contact-accurate 3D finger motion without an instrumented object supplying contact ground truth.
Stated limitations:
- A significant gap remains between the model's skill and human pianists. [Discussion/limitations paragraph (end of Sec. 5)]
- Sound amplitude is ignored, so music is generated at constant amplitude. [Limitations paragraph]
- Model-chosen fingering means policies may struggle with basic skills such as finger crossover. [Limitations paragraph]
- Per-frame F1 may not match human auditory perception (broken chords, tempo). [Limitations paragraph]
- Simulated hands can exert unnaturally large torques or infeasible accelerations. [Limitations paragraph]
Open problems listed:
- Gap between simulated and elite human pianist skill.
- Modeling dynamics (amplitude) in performance.
- Fingering strategies such as finger crossover.
- Perceptually aligned evaluation of performance.
- Biomechanically realistic actuation.
Benchmark gaps:
- FurElise reconstruction / key-press F1 vs MIDI: F1 86.49 for the refined capture over the whole dataset.
- Sleep Away (test piece) / F1: Full method 83.75, lowest of the four tested pieces; ablations 49-64.
Restrictive assumptions: 5 calibrated, synchronized 4K multi-view cameras.; Instrumented Yamaha Disklavier giving MIDI key states for refinement.; Assumes the fingertip stays in contact with the key for the note duration.; Per-subject hand shape from extra calibration videos.; Fixed, known object (the keyboard); no free-moving object.; RANSAC to reject occluded keypoints; Butterworth smoothing since HaMeR is per-frame.

## [629] RP1M: A Large-Scale Motion Dataset for Piano Playing with Bi-Manual Dexterous Robot Hands (CoRL 2024, dataset, S3)
Source: https://raw.githubusercontent.com/mlresearch/v270/main/assets/zhao25d/zhao25d.pdf (PMLR v270; arXiv 2408.11048); confidence HIGH.
Field cannot yet: Learned bimanual dexterous policies cannot yet generalize across many fast contact tasks or transfer to real hands that need precise fingertip state tracking.
Stated limitations:
- Fails on challenging songs due to fast rhythms and robot hand mechanical limits. [6 Limitations & Conclusion]
- F1 may not capture musical performance; position controller missing target velocity hurts. [6 Limitations & Conclusion]
- Dataset contains only proprioceptive observations, no vision, touch or hearing. [6 Limitations & Conclusion]
- Real-robot deployment is hard: state estimation incl. precise fingertip tracking, high-speed control, sim-to-real gap. [6 Limitations & Conclusion]
- Gap remains between best multi-task agent and RL specialists. [6 Limitations & Conclusion]
Open problems listed:
- Generalist multi-song piano agents matching RL specialists.
- Fast-rhythm songs beyond robot hand mechanics.
- Musically meaningful evaluation beyond F1.
- Multimodal sensing for piano playing.
- Real-world deployment: piano and hand state estimation incl. fingertip tracking, high-speed precise control, sim-to-real.
Benchmark gaps:
- RP1M, 20 out-of-distribution songs / F1: Best zero-shot F1 is 0.316 (DP-T trained on 150 songs).
- RP1M, 12 in-distribution songs / F1: Best multi-task F1 about 0.546 (DP-U), below RL specialists (79% of which exceed 0.75).
Restrictive assumptions: Simulation only (Shadow hands in RoboPianist); no real-robot data.; Proprioceptive state only; perfect state access in simulation.; Position-based control.

## [649] GLOVER++: Unleashing the Potential of Affordance Learning from Human Behaviors for Robotic Manipulation (CoRL 2025, dataset, S6 S1)
Source: https://arxiv.org/pdf/2505.11865; confidence HIGH.
Field cannot yet: Affordance learning from human video cannot yet supply time-resolved 3D contact, trajectory or force information, only static 2D contact points.
Stated limitations:
- Annotations come mainly from static images, missing dynamic interactions such as tool-use trajectories and force-sensitive affordances. [7 Limitations]
- Reliance on VLMs may inherit their biases, giving over-generalized predictions for novel object-action combinations. [7 Limitations]
- Cannot plan grasp pose and trajectories itself; needs imitation learning or a VLM planner. [7 Limitations]
Open problems listed:
- Lack of large-scale datasets with precise affordance annotations.
- Insufficient exploration of affordances across diverse manipulation contexts.
- Dynamic and force-sensitive affordances beyond static images.
- Linking affordance prediction to grasp pose and trajectory planning.
Benchmark gaps:
- IsaacGym GAPartNet zero-shot manipulation / success rate: Average 46.9%; Pickup and some Open tasks at 32-44%.
- RLBench (RVT-AFF) / success rate: Insert peg 8%, stack cups 8%, place cups 4% with RVT backbone.
- HOVA-500K benchmark / SIM: Best SIM 0.141.
Restrictive assumptions: Single affordance point per object predicted in 2D, lifted to 3D via camera intrinsics and depth.; Contact-point labels from hand-object box overlap, skin segmentation and inter-frame homography, assuming near-planar scene motion.; Static images; no temporal or force information.

## [650] Humanoid Policy ~ Human Policy (CoRL 2025, dataset, S6 S3)
Source: https://arxiv.org/pdf/2503.13441; confidence HIGH.
Field cannot yet: Scalable human demonstration capture cannot yet provide reliable hand tracking under heavy occlusion without specialized hardware.
Stated limitations:
- Uses a relatively simple policy architecture; large language-conditioned policy left for future work. [6 Limitations]
- Human data relies on consumer VR hand-tracking SDKs that can fail under heavy occlusion. [6 Limitations]
- Evaluations only on robots with dexterous hands. [6 Limitations]
Benchmark gaps:
- Vertical grasping 3x3 grid / successes: Robot-only 28/90 versus co-trained 35/90.
- Vertical grasping state-action ablation / successes: Full design 4/10; without unified state 1/10; without slow-down 0/10.
Restrictive assumptions: Wearable VR headset (Apple Vision Pro or Meta Quest 3, optional ZED Mini) for 3D head and hand pose.; Operators sit upright and minimize whole-body movement.; Fixed slow-down factor of 4 for human actions.; Task-oriented demonstrations aligned with robot tasks.; Humanoids with actuated necks, no wrist cameras, 6-DoF Inspire hands.

## [692] emg2tendon: From sEMG Signals to Tendon Control in Musculoskeletal Hands (RSS 2025, dataset, S6 S4)
Source: https://arxiv.org/pdf/2508.08269; confidence HIGH.
Field cannot yet: Wearable hand sensing cannot yet produce validated actuation-level control for hands manipulating objects, because its labels still depend on occlusion-prone mocap and simulation.
Stated limitations:
- Heavy reliance on accurate pose and inverse dynamics; emg2pose already has 12.7% inverse-dynamics failure from marker occlusion and infeasible joints. [VII Limitations]
- Tendon signals come from a simulated musculoskeletal hand, so the dataset is synthetic; real tendon-driven hand testing is required. [VII Limitations]
- Simplified MyoHand omits secondary muscles, possibly misestimating tendon forces. [VII Limitations]
Open problems listed:
- Mapping sEMG to tendon control for dexterous hands.
- Occlusion-robust hand tracking for labels.
- Sim-to-real for tendon-driven hands.
- Hand-object interaction data for EMG-based control.
Benchmark gaps:
- emg2tendon held-out user and stage / mean angular error: Best sEMG-to-pose 14.7 deg; two-step 16.9 deg.
- emg2tendon held-out user and stage / tendon RMSE / MAE: Best 0.253 / 0.159.
Restrictive assumptions: Ground truth from marker-based mocap via inverse dynamics.; Simulated MyoHand model; no real tendon measurements.; No objects; free-hand gestures only.; Wrist joints not modeled.

## [696] EgoVerse: An Egocentric Human Dataset for Robot Learning from Around the World (RSS 2026, dataset, S6)
Source: https://arxiv.org/html/2604.07607; confidence HIGH.
Field cannot yet: The field cannot yet turn diverse, unaligned egocentric human data into robot policy gains without task- and scene-aligned human-robot anchor data.
Stated limitations:
- The study covers only human-and-robot co-training; other paradigms such as pre-training followed by fine-tuning are left for future work. [V Limitations]
- Scene and demonstrator diversity findings rest only on offline action-prediction error, not on robot rollouts. [V Limitations]
- Robot rollouts are still needed to confirm that the diversity effects carry over to robot manipulation. [V Limitations]
- Scaling with diverse human data works only when task- and scene-aligned human-robot data is included in training. [I Introduction (Key Findings)]
- Co-training hurt one robot on one task, which the authors attribute to that robot's embodiment forcing a different strategy from the human one. [IV-E]
Open problems listed:
- Effective human-robot transfer remains open, with unresolved questions about the embodiment gap and scaling behaviour.
- Most human datasets are one-off, static releases that are hard to scale or extend.
- Large human activity datasets (Ego4D, HOI4D, EgoExo4D, Epic-Kitchens) lack manipulation-relevant annotations such as precise hand poses or object interactions, and include tasks beyond robot capability.
- When pre-training on human data yields transferable structure, and how embodiment-specific design decisions affect transfer, is still an open question.
- Methods that use weakly aligned or unaligned human data, grounded through limited aligned supervision, are needed.
- Embodiment factors (kinematics, sensing, control) need deeper analysis to guide data selection, curriculum and architectures.
- Offline diversity effects still need validation through robot rollouts.
Benchmark gaps:
- EgoVerse-A co-training, bag-grocery task / robot task success: Performance decreased for Robot B with human co-training, while Robots A and C improved; overall gains were up to 30% elsewhere.
- EgoVerse-A diversity experiments (fold-clothes) / offline Avg-MSE: Diversity effects are measured only with offline action-prediction error; the paper says this does not directly measure robot performance.
Restrictive assumptions: Human action is represented only by 21 3D hand keypoints per hand plus SLAM head pose; these are used as proxies for end-effector motion.; Aligned human-robot data (same task semantics and scene context) is needed to anchor transfer.; Demonstrators were told to keep hands visible, and manual quality control kept only manipulation-dense segments.; Tasks are limited to 'bounded diversity': tasks feasible for typical bimanual mobile manipulators.; Academic data relies on Project Aria glasses and Meta MPS for hand tracking and egomotion.

## [697] High Fidelity Capture, Reconstruction, and Transfer of Human Demonstrations for Robot-Assisted Bathing (RSS 2026, dataset, S6 S2)
Source: https://arxiv.org/html/2608.09127; confidence HIGH.
Field cannot yet: The field cannot yet estimate human body pose and shape online, at sub-frame latency, during sustained physical contact, so robots can react to a moving person.
Stated limitations:
- Standard marker-based fitting (MoSh++) of gloved hands produces contorted fingers and hand-body gaps. [III-B]
- Closed-loop force control uses summed pressure only, not the per-taxel distribution. [V-C]
- The sim-to-real gap is large because of mannequin-vs-SMPL-X and MANO-vs-robot-hand mismatches. [V-C]
- Compliance of the robot hand and of the reconstructed body and hand is not modelled. [V-C]
- The capacitive gloves cannot separate normal from shear force. [V-C]
- The system cannot be used on humans; perception is the main bottleneck, and online pose and shape estimation fast enough for live interaction does not exist. [V-C]
- The method assumes the bathed body is static, which does not hold for a human subject. [V-C]
- Mild-pressure tactile signals fall below sensor sensitivity and are indistinguishable from noise. [V-A]
- Tactile data alone cannot tell which bodies are in contact or why forces change; all three channels together are needed. [V-B]
Open problems listed:
- No comprehensive data exists on how caregivers actually bathe people; existing systems use idealized definitions and coarse metrics.
- Point, instantaneous or simple-constraint contact models cannot represent sustained bathing contact; surface- or volume-based contact models are needed.
- Low-pressure tactile acquisition needs higher sensor sensitivity.
- Patient movement (voluntary and reactive) must be handled; systems must account for constant body repositioning.
- Distributed force control is blocked by the mismatch between human and robot hand responses; calibration-based fixes are brittle.
- Normal and shear forces must be measured.
- Online low-latency human pose and shape estimation is the main perception bottleneck.
Benchmark gaps:
- own bathing captures (10 sample demonstrations) / contact distance between body contacts and glove taxels (cm): Ours: median 0.536, mean 0.837, st.dev. 0.842, against MoSh++ at median 1.714 and mean 2.067; the residual error stays below 1 cm on average.
- back bathing on mannequin / glove pressure (absolute, normalized, median per taxel): Closed-loop pressure tracks the human signal on a normalized scale but deviates in absolute pressure and spatial distribution; open-loop pressure is significantly higher than the human signal.
Restrictive assumptions: 20-camera Vicon optical motion capture with 52 body markers and 23 markers per glove.; Tactile gloves with 65 capacitive taxels; all forces are assumed normal to each taxel.; Subjects are able-bodied and seated upright on a stool; markers that block bathing are temporarily removed.; Robot transfer assumes a static mannequin body.; The human demonstration was slowed 20x (120 Hz to 6 Hz) for robot execution.; One-time calibration of hand taxel positions; SMPL-X/MANO shapes are fitted from range-of-motion tests.

## [709] A Systematic Study of Data Modalities and Strategies for Co-training Large Behavior Models for Robot Manipulation (RSS 2026, benchmark, S6)
Source: https://arxiv.org/html/2602.01067; confidence HIGH.
Field cannot yet: The field cannot yet extract accurate, fine-grained hand action labels from large-scale human video that measurably improve generalist robot policies.
Stated limitations:
- The impact of vision-language data is not broken down by task type. [V Discussion, Limitations, And Future Work]
- Human videos are used only through coarse latent actions and language annotations, not fine-grained hand motion. [V]
- Chain-of-thought exploration is limited to low-level action abstractions present in the co-training data. [V]
- Only imitation learning is studied; world models and RL are not explored. [V]
- The link between backbone vision-language ability and policy generalization is not rigorously characterized. [V]
- No discrete-token variant, including latent actions from human video, gave statistically significant gains. [III-B summary]
Open problems listed:
- Fine-grained dexterous motion labels from human video are not yet used as a co-training signal.
- Obtaining accurate action labels from human video often needs extra sensing such as VR devices or wearable exoskeletons.
- Latent-action approaches have been validated only in low target-robot-data regimes.
- Which vision-language task categories drive which policy capabilities is unknown.
- The relation between VLM backbone understanding and policy generalization needs rigorous characterization.
- Richer CoT formulations for complex decision-making remain to be studied.
- Co-training within world modeling or reinforcement learning is an open frontier.
Benchmark gaps:
- simulation benchmark (TRI-Ramen tasks) / task success under seen/unseen tasks and distribution shift: Latent actions, FAST and VQ-VAE tokens gave no statistically significant improvement; FAST lowered unseen-task success.
- VLM benchmarks (VQA, spatial and multimodal reasoning) / benchmark scores: The no-co-training baseline lost all language generation ability and performed poorly across nearly all benchmarks.
Restrictive assumptions: Human videos have no ground-truth actions, so action reconstruction is omitted for them.; Policies use a pretrained PaliGemma2 VLM backbone and roughly 4,000 hours of robot and human data plus 50M VL samples.; Human video annotations are generated by GPT-5 from frames sampled at 1 s intervals.; A 9:1 robot to co-training data ratio was chosen empirically.

## [734] Towards Unifying Human Likeness: Evaluating Metrics for Human-Like Motion Retargeting on Bimanual Manipulation Tasks (ICRA 2024, benchmark, S3 S6)
Source: https://h2t.iar.kit.edu/pdf/Meixner2024.pdf; confidence HIGH.
Field cannot yet: The field has no validated, robot-independent standard for scoring how human-like a retargeted bimanual robot motion is.
Stated limitations:
- The unified metric depends on the generated retargeting dataset, which in turn depends on the chosen metrics and joint mapping. [VI Conclusion and Future Work]
- Metric and optimizer parameters were set empirically. [VI]
- All evaluation is on simulated robots; real-robot evaluation is planned. [VI]
- The closed-form joint mapping does not align rotation-axis centres. [III-A]
- Metric correlations vary across motions and robots (MAD 0.1 and 0.126). [IV-B]
- Adding several criteria can hurt functional constraint satisfaction. [V-A]
- Unimanual metrics are applied to bimanual motion by averaging the left- and right-arm values. [III]
Open problems listed:
- Guidelines for choosing a human-likeness metric for a given setting are missing.
- Several metrics were introduced without comprehensive assessment, or are evaluated by high-effort user studies.
- Optimizing a trajectory for one metric biases evaluation with that metric.
- Few human-likeness approaches address bimanual manipulation.
- Learning-based retargeting still has difficulty explicitly considering task constraints.
- Metrics were developed independently, without regard to transferability and compatibility.
Benchmark gaps:
- KIT Bimanual Manipulation Dataset retargeted to 3 robots / mean absolute deviation of Spearman correlation coefficients: MAD across robots 0.126 and across motions 0.1, so metric relationships are not invariant across robots or motions.
Restrictive assumptions: Human motion comes from marker-based capture in the MMM reference model (KIT Bimanual Manipulation Dataset, two subjects for correlation analysis).; The one-to-one joint mapping requires kinematic structures similar to the human arm, and default poses are adjusted perceptually by hand.; Motions are mirrored to compensate for missing left-handed subjects.; Evaluation is in simulation on ARMAR-III, ARMAR-6 and a dual Panda setup.; Robot placement uses reachability maps of the human hand trajectories.

## [758] TWIN: Two-handed Intelligent Benchmark for Bimanual Manipulation (ICRA 2025, benchmark, S3 S6)
Source: https://arxiv.org/html/2407.00278 (PerAct2 arXiv preprint by the same authors; Semantic Scholar ICRA abstract matches; ICRA version itself not accessed); confidence MEDIUM.
Field cannot yet: The field cannot yet learn tightly coordinated bimanual skills such as handovers and joint lifts with reliable success, even in noiseless simulation.
Stated limitations:
- No method reaches a sufficiently high success rate. [Limitations and Future Work]
- Discretized-action methods need a sampling-based motion planner to execute. [Limitations and Future Work]
- Real-world results are hard to reproduce. [4.3 Real-World]
- Simulated cameras are idealized, without noise. [4.1 Simulation]
- Image-based methods confuse the two identical arms. [4.1 Simulation]
- The real-world voxel size was coarsened for training speed at the cost of accuracy. [4.3 Real-World]
Open problems listed:
- There is a lack of simulated bimanual benchmarks with large task diversity.
- Real-world bimanual evaluation suffers from reproducibility and variability.
- Running two separate agents is insufficient; coordination between arms is crucial.
- Bimanual success rates are not sufficiently high for any current method.
- More sophisticated motion planning is needed for bimanual scene interaction.
- Discretized-action methods depend on sampling-based planners.
- Mobile bimanual manipulation is not yet covered.
Benchmark gaps:
- TWIN/RLBench2 13 tasks / average task success rate: ACT 5.9%, RVT-LF 10.5%, PerAct-LF 17.5%, PerAct2 16.8%.
- TWIN/RLBench2 put bottle in fridge / task success: All methods scored 0 to 3%.
- TWIN/RLBench2 handover an item / task success: ACT, RVT-LF and PerAct-LF scored 0%; PerAct2 11%.
- TWIN/RLBench2 pick up plate, lift tray, sweep dustpan / task success: Plate at most 4% for any method; PerAct2 1% on tray and 0% on dustpan.
Restrictive assumptions: Simulation with four noiseless RGB-D cameras (front, both shoulders, wrist).; Two identical Franka Panda arms with parallel grippers.; Demonstrations generated automatically via motion planning, 100 per task, single-task training.; Real-world tests use a single Azure Kinect, one kinesthetic demonstration per task, and qualitative evaluation only.

## [767] HelmetPoser: A Helmet-Mounted IMU Dataset for Data-Driven Estimation of Human Head Motion in Diverse Conditions (ICRA 2025, dataset, S4)
Source: https://arxiv.org/html/2409.05006; confidence HIGH.
Field cannot yet: The field cannot yet provide drift-free, sensor-independent head pose from helmet IMUs alone outside the lab when cameras and LiDAR fail.
Stated limitations:
- IMU-only estimation suffers from accumulating drift. [I Introduction]
- Head motion is hard to model with data-driven IMU estimation. [I Introduction]
- Performance drops when models are transferred to a different IMU. [IV-D]
Open problems listed:
- LiDAR degrades in dust, smoke, moisture, narrow spaces and feature-poor areas such as tunnels and mines.
- Visual sensors fail with low light, motion blur, occlusion or smoke, and worse under rapid, intense motion.
- IMU drift makes long-term IMU-only localization problematic.
- Data-driven IMU datasets come from vehicles, robots or the body; few capture high-frequency head motion from helmets.
Benchmark gaps:
- HelmetPoser, VectorNav IMU (cross-sensor) / percentage reduction in final integration error: 52.55% to 60.22%, against 90.53% to 92.29% on the training sensor (Livox Mid-360 IMU).
Restrictive assumptions: Data is collected only in a VICON-equipped laboratory, which provides ground truth.; Only three motions: walking, running and stair climbing; ten participants, three sessions of about five minutes each.; Ground-truth IMU bias is derived by pre-integration against VICON poses.; A single participant (D) serves as the validation set.

## [782] How to Train Your Robots? The Impact of Demonstration Modality on Imitation Learning (ICRA 2025, benchmark, S6)
Source: https://arxiv.org/html/2503.07017; confidence HIGH.
Field cannot yet: The field cannot yet collect demonstrations that are both clean in contact force and low in effort at scale without force sensing during demonstration.
Stated limitations:
- Kinesthetic replay fails on contact-force tasks. [V Results]
- No force sensor is available, so force-induced control error is compensated only after the fact. [IV Experimental Design]
- The compensation heuristic doubles replay time on force tasks. [IV Experimental Design]
- Non-expert data was excluded from the data-quality analysis. [V Results]
- Kinesthetic teaching is too physically demanding for large-scale collection. [Abstract]
Open problems listed:
- The relative effects of demonstration modalities on policy performance, data quality and user experience remain insufficiently explored.
- Kinesthetic teaching cannot recover actions under contact forces without force profile recording and replay.
- Users prefer teleoperation for large-scale data collection despite its lower data quality.
- The optimal mix of modalities is unknown and should be determined automatically.
Benchmark gaps:
- Push Sanitizer task / policy success rate: Kinesthetic data underperforms the teleoperation modalities, and the task was excluded from the mixed-data scheme because kinesthetic data quality was low.
- Flip Glass task, mixed data / policy success rate: 75% with 100 mixed demonstrations, 5% above the best single-modality model.
Restrictive assumptions: A single 7-DoF Franka arm with a Cartesian impedance controller.; Policy training data comes from a single demonstrator to control confounds; diffusion policy is fixed.; Three tabletop tasks; 12 university-student participants.; No force sensing; kinesthetic demonstrations need replay to obtain actions.

## [813] HHI-Assist: A Dataset and Benchmark of Human-Human Interaction in Physical Assistance Scenario (ICRA 2026, dataset, S4)
Source: https://arxiv.org/html/2509.10096; confidence HIGH.
Field cannot yet: The field cannot yet predict coupled two-person motion during physical assistance accurately beyond about one second or across unseen assistance tasks.
Stated limitations:
- Motions are performed by lab participants and are not validated as ergonomic or clinically safe. [III-A Data Collection]
- Heavily occluded takes were dropped after manual inspection. [III-A Data Collection]
- Participants had no caregiving or care-receiving experience requirement. [III-A Data Collection]
- Transfer to physical human-robot interaction is not tested. [I Introduction]
- Generalization to unseen tasks degrades. [V-E1 Generalization]
- Prediction uses only past pose, with no action class or other modalities. [II Related Work]
- Joint-position prediction does not preserve link lengths. [V-E3]
Open problems listed:
- Physical HRI data is scarce.
- Coupled dynamics in physical interaction add complexity to motion prediction.
- Assistance scenarios and human dynamics vary widely.
- Prediction degrades under distribution shift to unseen tasks.
- Angle representations have discontinuities, and position representations violate link lengths.
- Using predictions for robot control (MPC, policy observations) is untested.
- Metrics for assistive tasks (contact sequences, force ranges, kinematic limits) are still needed.
Benchmark gaps:
- HHI-Assist / MPJPE (mm), caregiver: Best model (IDD) has 94.0 mm at the longest horizon and 50.4 mm on average.
- HHI-Assist, unseen Task 3 / MPJPE (mm): Caregiver: 89.3 average and 154.8 at 1000 ms; care receiver: 62.5 average and 113.8 at 1000 ms.
Restrictive assumptions: Marker-based OptiTrack capture with 20 cameras and 50-marker suits; 21-joint skeleton.; Healthy lab participants role-play the caregiver and care-receiver roles.; Only joint positions are released: no video, no contact or force data.; 1 s observation predicts 1 s future at 24 fps.

## [825] DynOPETs: A Versatile Benchmark for Dynamic Object Pose Estimation and Tracking in Moving Camera Scenarios (ICRA 2026, dataset, S5)
Source: https://arxiv.org/html/2503.19625; confidence HIGH.
Field cannot yet: Marker-free, scalable and accurate 6D pose annotation and tracking of moving objects from moving cameras, especially for symmetric or textureless objects, without CAD models or mocap.
Stated limitations:
- After EKF/RTS refinement, FoundationPose pseudo-labels remain poor for symmetric or textureless objects such as bowls. [III-D1]
- The point-tracking relative pose branch drifts over time. [III-D2]
- The pipeline still needs manual removal of bad absolute pose estimates. [III-D3]
- SAM6D's built-in segmentation and fixed thresholds do not generalize to the cluttered backgrounds. [IV-E]
- FoundationPose fails on some sequences and underperforms BundleTrack/BundleSDF on ADD(S)-0.1d. [IV-F]
Open problems listed:
- Most real-world pose datasets assume either a static camera or stationary objects, unlike real use with ego-motion plus object dynamics.
- Pose annotation in dynamic scenes relies on labor-intensive manual work or expensive mocap in controlled environments.
- State-of-the-art pseudo-labelers struggle with symmetric, transparent, reflective, or sparse/repetitive-pattern objects, so many labels still need manual refinement.
- HOT3D-type egocentric hand-object datasets have limited object variety and constrained scenes.
- Future: deploy acquisition on a robot platform for grasping/manipulation.
- Future: add human hand pose annotations for AR/MR interaction.
Benchmark gaps:
- DynOPETs COPE-119 / 5deg2cm (%): Best off-the-shelf COPE method AGPose reaches 61.61; NOCS only 11.57; DiffusionNOCS IoU75 only 4.57.
- DynOPETs UOPE-56 / AR / FPS: RGB-only FoundPose (coarse) AR 60.46; all UOPE methods run below 4 FPS, FoundationPose 0.98 FPS.
- DynOPETs (175 seq) / ATE (m): MaskFusion 0.320 and DROID-SLAM 0.173 versus FoundationPose 0.037; MaskFusion ADD AUC 12.23.
Restrictive assumptions: Scanned CAD model required for every object (FoundationPose model-based labeling).; Camera pose supplied by a motion capture system with hand-eye calibration.; Scenes on typical desktop backgrounds with sufficient visual features.; One dynamic object per sequence; no hands annotated.; Annotation accuracy validated against mocap on only 10 additional sequences.; Manual removal of poor absolute pose edges.

## [836] Benchmarking the Effects of Object Pose Estimation and Reconstruction on Robotic Grasping Success (ICRA 2026, benchmark, S5)
Source: https://arxiv.org/html/2602.17101; confidence HIGH.
Field cannot yet: Evaluate perception (pose and reconstruction) by its real-world functional effect on manipulation rather than by geometric metrics alone.
Stated limitations:
- The whole study is in simulation (PyBullet); physical validation is pending. [VI Conclusion]
- A perfect pose cannot rescue grasps planned on a badly flawed reconstructed mesh. [VI Conclusion]
- Standard 2D projection and pure rotation error metrics poorly predict grasp success. [V-B]
Open problems listed:
- Decoupled evaluation: unknown how pose and reconstruction errors compound into manipulation failure.
- Geometric metrics (ADD, MSPD, Chamfer) do not reflect functional manipulation success; 2D and rotation metrics poorly predict grasp outcome.
- Reconstructed meshes with low geometric error can still have artifacts (smoothed edges, filled holes) critical for grasping.
- Grasping methods often assume high-quality point clouds or object models.
- Need validation on physical robots.
- Need extension to placement and assembly primitives and perception-to-action benchmarks.
Benchmark gaps:
- YCB-V (BOP) in PyBullet / Estimated Success Rate: MegaPose poses give 59.4% average grasp success versus 89.9% for FoundationPose.
- YCB-V reconstructed meshes / Grasp Generation Success Rate: Most reconstructions yield clearly fewer viable grasps than GT CAD, dominated by collision failures (Instant-NGP worst).
Restrictive assumptions: Physics simulation only (PyBullet), floating objects with no ground plane, gravity enabled only after closing, fixed friction 0.5.; YCB-Video's 21 objects only; meshes from a prior reconstruction benchmark.; Only two pose estimators evaluated (MegaPose, FoundationPose), both model-based.; Pre-computed antipodal grasp library on known object model; open-loop grasp execution.

## [837] IndustryShapes: An RGB-D Benchmark Dataset for 6D Object Pose Estimation of Industrial Assembly Components and Tools (ICRA 2026, dataset, S5)
Source: https://arxiv.org/html/2602.05555; confidence HIGH.
Field cannot yet: Reliably estimate 6D pose of reflective, thin, textureless industrial parts in cluttered real workcells, especially model-free from onboarding sequences.
Stated limitations:
- Uneven test scene lengths give uneven object representation. [V Conclusions]
- Unequal training scene complexity across objects biases instance-level results. [V Conclusions]
- Train/test domain shift persists. [IV-C]
Open problems listed:
- Industrial objects are textureless, metallic or reflective; symmetric, thin and similar objects cause pose ambiguity.
- Occlusion, clutter and variable, unconstrained lighting degrade performance.
- Without realistic data, deep models fail to generalize beyond clean controlled environments; dataset/deployment complexity mismatch.
- Exhaustive annotation of all object configurations in complex scenes is impractical.
- Existing datasets are limited to labs, bin-picking or household items and optimized for instance-level methods.
- Novel-object pose estimation and onboarding-sequence modalities are underrepresented.
- Train/test domain shift persists.
- Accurate localization in cluttered industrial scenes remains challenging.
- Uneven test scenes, unequal training complexity, incomplete pose coverage.
Benchmark gaps:
- IndustryShapes Classic / BOP AR: Best FoundationPose (model-based) 0.67; EPOS 0.51, ZebraPose 0.50, FoundPose 0.30, DOPE 0.08.
- IndustryShapes Extended / BOP AR: FoundationPose model-free 0.33; FoundPose 0.28.
- IndustryShapes Classic / Segmentation mAP: CNOS 0.203, SAM-6D 0.345.
Restrictive assumptions: Five objects only, all with CAD models.; Static scenes without hands; annotation via ArUco markers or SfM with manually defined CAD anchor points.; Mostly single-object training scenes; RealSense D455 minimum depth 0.52 m.; Annotation depth error under 12 mm (classic) and about 5 mm (extended).

## [839] GraspClutter6D: A Large-Scale Real-World Dataset for Robust Perception and Grasping in Cluttered Scenes (ICRA 2026, dataset, S5)
Source: https://arxiv.org/html/2504.06866; confidence HIGH.
Field cannot yet: Perceive and grasp reliably under heavy occlusion in dense real-world clutter.
Stated limitations:
- Robust grasping in highly cluttered scenes is still unsolved even with their training data. [IV-A]
- All pose methods degrade as occlusion increases. [IV-D]
- Simple approach trajectories cause grasp failures even with correct grasp poses. [V Conclusion]
- Foundation segmentation (Grounded-SAM) separates instances poorly in clutter. [IV-C]
Open problems listed:
- Robust grasping in dense clutter with unknown poses and varied backgrounds is open.
- Existing benchmarks are simplistic, lightly occluded and low diversity.
- Synthetic grasp datasets suffer sim-to-real gaps (inaccurate sensor noise and contact dynamics).
- Occlusion handling in 6D pose estimation remains a persistent challenge.
- Foundation segmentation models struggle with instance boundaries in clutter.
- Simple approach trajectories fail; need gripper-aware reactive grasping.
- Reflective/transparent objects produce depth sensor artifacts.
Benchmark gaps:
- GraspClutter6D / ADD(-S) high occlusion: FoundationPose 55.0, MegaPose 42.3, GDR-Net 27.7, FFB6D 13.2.
- GraspClutter6D / Grasp AP: EconomicGrasp drops from 51.63 on GraspNet-1B to 21.67 (29.96 drop); best is 22.69.
- Real-world 15-object pile / Grasp success rate: Best 67.9% (trained on GraspClutter6D); AnyGrasp 59.6%.
- GraspClutter6D / Instance segmentation AP: Grounded-SAM 16.2 AP; best Mask2Former 43.5.
Restrictive assumptions: Static scenes with no humans or hands; 4 RGB-D cameras on a UR5, ChArUco/ArUco calibration.; Reflective and transparent objects sprayed gray for scanning; CAD meshes for all 200 objects.; Annotations aligned on fused Zivid point clouds from 13 views with crowd-sourced manual alignment.; Parallel-jaw gripper grasps rated by analytic force closure.

## [843] Towards Exploratory and Focused Manipulation with Bimanual Active Perception: A New Problem, Benchmark and Strategy (ICRA 2026, benchmark, S3)
Source: https://arxiv.org/html/2602.01939; confidence HIGH.
Field cannot yet: Actively choose viewpoints and use force to perform fine-grained bimanual manipulation under self-occlusion.
Stated limitations:
- All tested policies fail on extremely fine-grained insertion tasks. [V-B]
- Delicate-task failures come from weak spatial perception and reasoning. [V-D]
- Policies fail when the active view misses the manipulated area or end effector. [V-A]
- Combining BAP with neck-based active vision, and active perception when both arms are busy, is left open. [I Introduction]
Open problems listed:
- Frequent visual occlusion with head-mounted main cameras.
- The Exploratory and Focused Manipulation problem: actively gathering task-relevant information.
- Active perception when both arms are busy, and combining arm-based with neck-based active vision.
- Semantic conditioning of actions on explored context.
- Spatial perception and reasoning for fine-grained contact.
- Optimal active viewpoint search.
- Extremely fine-grained insertion (Light-Plug, Charger-Plug) remains unsolved.
Benchmark gaps:
- EFM-10 / Success rate (%): Charger-Plug best 23.3 (GR-MG); Light-Plug best 23.3; ACT without BAP 0.0 on Charger-Plug.
- EFM-10 / Success rate (%): Force sensing lifts GR-MG on Light-Plug only from 20.0 to 36.7.
Restrictive assumptions: A free non-operating arm is available to carry the active camera.; A single bimanual platform (JAKA K-1) with built-in F/T sensors and VR teleop demos.; Imitation learning from 1810-1850 expert demonstrations; force tested on two tasks only.; Real-world evaluation of 30 trials per task.

## [854] Influence of Gripper Design on Human Demonstration Quality for Robot Learning (ICRA 2026, benchmark, S6)
Source: https://arxiv.org/html/2603.17189; confidence HIGH.
Field cannot yet: Capture fast, natural bimanual demonstrations of fine manipulation of flexible objects with handheld tools that match bare-hand performance.
Stated limitations:
- Grippers lacked the sensors/markers of a full pipeline, so no robot learning was evaluated. [V Discussion]
- Findings do not generalize directly to the whole LfD pipeline. [V Discussion]
- Original UMI hardware could not do the task at all. [II-B]
- Demonstration collection stays slow even with improved grippers. [V Discussion]
Open problems listed:
- Demonstrations are time-consuming: at least 200 per task, roughly twice hand time.
- Gripper weight (about 780 g) causes fatigue.
- Mechanical design and ergonomics of handheld gripper tools are underexplored.
- Tools built for rigid pick-and-place fail on thin, flexible materials.
- Gripper hardware limits cannot be overcome by learning algorithms alone.
- Full demonstration-to-robot pipeline evaluation in healthcare tasks is still missing.
Benchmark gaps:
- Bandage-opening user study / Bandages opened (%): Distributed-load grippers 65.8% vs 100% for hands and concentrated-load grippers.
- Bandage-opening user study / Time to open: Hands significantly faster than both gripper designs.
Restrictive assumptions: Cameras removed from the grippers during testing.; Eight non-expert participants (no healthcare workers), one task (bandage opening), 15 trials per condition.; Two-minute trial cap.

## [869] Scalable Vision-Language-Action Model Pretraining for Robotic Dexterous Manipulation with Real-Life Human Activity Videos (ICRA 2026, dataset, S6 S1)
Source: https://arxiv.org/html/2510.21571; confidence HIGH.
Field cannot yet: Recover accurate metric 3D hand (and object) motion from in-the-wild monocular video well enough to supervise bimanual, long-horizon robot learning.
Stated limitations:
- Pretraining data contains errors from 3D reconstruction and VLM captioning. [6 Discussion and Future Work]
- Only short-horizon atomic skills are targeted. [6 Discussion and Future Work]
- Robot experiments are mostly single-handed; bimanual shown only by a simple hand-over. [6 Discussion and Future Work]
- Speed-minima segmentation can over-segment repetitive actions. [3.2]
- Metric 3D hand motion recovery is hard from monocular video. [1 Introduction]
Open problems listed:
- Teleoperated VLA data is costly and limited in scale and diversity.
- No large-scale dexterous hand action datasets exist for pretraining.
- Human videos are unscripted, unsegmented, noisy and lack language and 3D action labels.
- Temporal action segmentation from video remains open; no method meets the need.
- Accurate metric 3D hand motion from single, uncalibrated, moving cameras is difficult.
- Video-input VLMs have poor action localization accuracy.
- Human-to-robot hand action space mapping remains open.
- Data inaccuracies from reconstruction and VLM limits.
- Long-horizon tasks, bimanual scenarios, multi-view and tactile integration remain open.
Benchmark gaps:
- Real robot unseen tasks / Success rate (%): Ours averages 64.6; OXE pretrain 7.8, VPP 5.2, latent-action pretrain 0.0.
- Unseen-environment grasp benchmark / Hand-object distance (cm): Best average 8.8 cm from a 20 cm start; Being-H0 19.1 cm.
Restrictive assumptions: Monocular egocentric RGB; 3D hands from HaWoR/MANO, cameras from MegaSAM with MoGe-2 depth.; No ground-truth 3D labels; noise accepted for pretraining.; Robot joints mapped to nearest human joint, unmapped dimensions zero-padded.; Fine-tuning needs 1.2K teleoperated trajectories on one Realman plus XHand platform.; Language labels from GPT-4.1 on 8 sampled frames.

## [889] Kaiwu: A Multimodal Manipulation Dataset and Framework for Robot Learning and Human-Robot Interaction (ICRA 2026, dataset, S6 S1 S4)
Source: https://arxiv.org/html/2503.05231; confidence HIGH.
Field cannot yet: Provide synchronized vision, force, muscle and gaze data with fine labels at scale for dexterous bimanual assembly learning.
Stated limitations:
- Action units are not subdivided because glove tactile sensors cannot register small parts; small parts were pre-assembled. [IV-B2]
- The release has missing data, partly patched by a supplement. [VII]
Open problems listed:
- Large, high-quality multimodal datasets are a bottleneck for robot learning and foundation models.
- Datasets rely on video and lack dynamics such as force, leading to superficial learning.
- No universal, intuitive human-level perception framework for open settings with humans.
- Limited understanding of the neural mechanisms of human manipulation; video alone cannot reveal how humans do complex tasks.
- Existing robot datasets suffer data homogenization.
- ARIO lacks dynamic kinematic information and has labeling generality issues.
- Human activity datasets lack assembly scenarios, modality balance, cross-modal temporal consistency and task causality analysis.
- Shift from short-term tasks to long-term autonomy.
Benchmark gaps:
- Kaiwu / none reported: No baseline method evaluation is reported; the paper presents data, platform and annotations only.
Restrictive assumptions: Heavy wearable instrumentation: data gloves, 16 EMG sensors, eye tracker, 37 mocap markers.; Lab assembly of one robot arm with 15 action links; small parts pre-assembled.; 20 young participants; one front RGB-D camera.; Listed annotations are action/gesture segmentation, gesture classes, AOIs and 2D semantic segmentation sampled at one-second intervals.

## [891] UniFucGrasp: Human-Hand-Inspired Unified Functional Grasp Annotation Strategy and Dataset for Diverse Dexterous Hands (ICRA 2026, dataset, S6)
Source: https://arxiv.org/html/2508.03339; confidence HIGH.
Field cannot yet: The field cannot yet transfer functional, task-aligned grasps reliably across heterogeneous dexterous hands to unseen real objects.
Stated limitations:
- Real-world tests show functional grasps on unseen instances but differences between robot hands limit broader generalization. [V Conclusion]
- Mug and drill grasp success stays low for all methods, attributed to handle shapes and narrow gaps. [IV-B Comparison of Grasping Performance]
- Overall real-world success is limited by the complexity of dexterous hands. [IV-C Real-World Experiments]
- Generalization to unseen instances is claimed only within some categories. [I Introduction]
Open problems listed:
- Lack of large-scale annotated functional grasp datasets because high-DoF hands make annotation costly and complex.
- Existing functional datasets support only ShadowHand, a fully-actuated, high-cost hand, hindering generalization to real-world use.
- MANO-based synthesis lacks physical embodiment and must be post-processed to map to real robot hands.
- Learned human-to-robot capture tied to one hand type shows strong hand-type dependency and poor generalization to other hands.
- Lack of systematic grasp-stability evaluation leads to unreliable generated gestures.
- Human-to-robot mapping methods are designed for a single hand and a single mapping paradigm.
- Hand differences pose challenges for broader generalization of functional grasps.
Benchmark gaps:
- UFG test split (IsaacSim) / grasp success rate: Mean 0.6955 overall; mug and drill 0.6667; flashlight 0.7037 vs DFG 0.9103.
- Real-world UR5 + InspireHand/HnuHand / success count: 37/70 and 39/70 total; press button 4/10 and 2/10; pour water 4/10 and 5/10.
Restrictive assumptions: Known object mesh: real objects are 3D-scanned (FreeScan X3) and posed with FoundationPose.; Robot hand URDF and a per-hand mapping matrix calibrated by fingertip-alignment experiments; InspireHand coupling matrix measured manually.; Human hand input from a single RGB-D camera with MediaPipe keypoints, one hand at a time.; Grasps annotated in MuJoCo simulation with rigid hand and object, a fixed friction coefficient and geometry-based force closure.; Joint-angle model calibrated from 60 sets from six volunteers with a goniometer.; Dataset limited to 21 daily-object categories; simulation and real tests on five categories.

## [907] Multi-task real-robot data with gaze attention for dual-arm fine manipulation (IROS 2024, dataset, S6 S3)
Source: https://arxiv.org/html/2401.07603; confidence HIGH.
Field cannot yet: The field cannot yet learn fine dual-arm manipulation data-efficiently across embodiments, especially for large deformables that exceed the attended view.
Stated limitations:
- Data come from only one robot framework, so adaptability to new robot frameworks is relatively low. [VIII Conclusions and Discussion]
- Semantic reasoning was not addressed; it would need large vision-language models, language-action pairs and compute. [VIII Conclusions and Discussion]
- Fine manipulation skills remain hard to acquire and require large amounts of data. [VIII Conclusions and Discussion]
- Multi-task pretraining gave no gain for needle-threading, suggesting it does not help with completely novel skills. [VII-E Challenging tasks]
- T-shirt folding failed because the large garment reached the image edges, causing eye-tracker errors and wrong gaze prediction. [VII-A Multi-Task Performance of DAA]
- Gaze prediction with a mixture density network was hard in multi-object scenes; predicting both gazes independently picked different objects. [V Model, gaze predictor]
Open problems listed:
- No publicly available at-scale dataset of dual-arm fine manipulation (sub-centimeter objects, thin objects, zippers).
- Existing fine-manipulation imitation work is specialized for one task, leaving versatility unassessed.
- Single-robot data limits transfer to other robot frameworks.
- Semantic reasoning for fine manipulation may require large language-action pairs and computational power.
- Fine manipulation skill acquisition remains data hungry.
- Multi-task training may not help learn completely novel skills.
Benchmark gaps:
- DAA real-robot tests (142 tasks, 7,815 trials) / success rate: Multi-task model 69.6% overall and 61.5% on new objects; task-specific models 12.2%.
- Needle-threading / success rate: 85.71% from scratch, 85.19% pretrained; no gain from multi-task pretraining.
- T-shirt folding / success: Task failed and was excluded from results due to eye-tracker errors.
Restrictive assumptions: Single platform: two UR5 arms with custom grippers, teleoperated through a kinematically matched master controller and HMD with eye tracker.; Requires human gaze recorded during teleoperation to train the visual attention.; Assumes the end-effector/object interaction happens inside the gaze-selected foveated region.; Dual-action labels auto-annotated by a network trained on about 6,000 manually labeled episodes.; Evaluation uses a uniform green background; foam tiles on the table to avoid emergency stops.

## [919] Is a Simulation better than Teleoperation for Acquiring Human Manipulation Data? (IROS 2024, benchmark, S6)
Source: abstract only; confidence LOW.
Field cannot yet: The field cannot yet capture subtle force-rich human manipulation skills through teleoperation without delay and transparency losses.
Open problems listed:
- Teleoperation-based data collection cannot readily capture subtle force-involved interaction skills because of dynamic delays and feedback transparency (abstract).
Restrictive assumptions: Evaluation restricted to three tasks named in the abstract: plane cutting, tight peg-in-hole and deformable pipe plugging.; Simulation interface excludes physical robots and relies on rendering high stiffness to the operator.

## [929] Exploring 3D Human Pose Estimation and Forecasting from the Robot's Perspective: The HARPER Dataset (IROS 2024, dataset, S4)
Source: https://arxiv.org/html/2403.14447; confidence HIGH.
Field cannot yet: The field cannot yet estimate and forecast full 3D human pose accurately from close-range, partial, robot-mounted views.
Stated limitations:
- Depth-based 3D lifting is limited by depth-map noise, especially for distant participants. [IV-A 3D Human Pose Estimation]
- Reconstructing the full 3D skeleton from only a partial 2D view is left open. [V Conclusions]
- Incomplete pose sequences cannot be handled by existing forecasting methods; an imputation model was needed. [IV-B 3D Human Pose Forecasting]
- Punches and kicks are hardest to predict as collisions, likely due to speed and energy. [IV-C Collision Prediction]
- Some participants left the capture area and occlusions caused missing markers in up to 3% of frames, filled by linear interpolation. [III-B Actions and Annotations]
- Depth sensor field of view is narrower than the cameras; joints outside it are treated as not visible. [IV-A 3D Human Pose Estimation]
Open problems listed:
- 3D human pose estimation when the robot sees users only partially at close range.
- Reconstructing the full 3D skeleton from a partial 2D image of the user.
- Forecasting from incomplete pose sequences, which existing forecasting approaches cannot process.
- Predicting fast, high-energy contacts (kicks, punches) between humans and a mobile robot.
- Collision prediction from robot sensors requires approaches beyond simple depth extrapolation.
- Further problems enabled by the data: proxemic behavior and action recognition.
Benchmark gaps:
- HARPER 3D-HPE (robot view) / MPJPE / PCK: PCK 82.2% in 2D, but 168 mm MPJPE in 3D.
- HARPER 3D-HPF / MPJPE at 400/1000 ms: Best HRNet+D+R about 309 mm (400 ms) and 332 mm (1000 ms); GT input EqMotion 43/70 mm.
- HARPER collision prediction / accuracy/sensitivity: EqMotion on HRNet+D+R: unintended 0.76 acc, 0.65 sensitivity; kick 0.52 sensitivity; depth baseline 0.49 acc on unintended.
Restrictive assumptions: Ground truth requires a 6-camera OptiTrack system and a 37-marker suit in a lab capture area.; Single user interacting with the robot at a time; 17 university-student participants; collisions are acted.; Robot future poses are assumed known because the robot plans in advance.; Spot cameras run at roughly 10 FPS with limited overlap between views.

## [954] EHoA: A Benchmark for Task-Oriented Hand-Object Action Recognition Via Event Vision (IROS 2025, dataset, S1)
Source: abstract only; confidence LOW.
Field cannot yet: The field cannot yet recognize hand-object actions robustly under fast motion and high dynamic range with conventional frame cameras.
Open problems listed:
- Event-vision analysis of hand-object actions in dynamic environments is still lacking (abstract, per search snippet).
- Regular CMOS cameras cannot handle hand-object action analysis in highly dynamic conditions (abstract claim).
Restrictive assumptions: Requires an event-based camera system (asynchronous event streams).; Recognition task is classification of task-oriented hand-object action categories, not 3D tracking or reconstruction.

## [958] A Multi-Modal Hand Imitation Dataset for Dexterous Hand (IROS 2025, dataset, S6 S1)
Source: abstract only; confidence LOW.
Field cannot yet: The field cannot yet transfer human hand demonstrations to dexterous robot hands with geometrically consistent multimodal grounding at scale.
Open problems listed:
- Single-modality (RGB) dexterous imitation datasets cannot capture spatial and temporal dynamics needed for human-like dexterity (abstract, per search snippet).
- Geometrically consistent human-to-robot hand skill transfer requires aligning human and robot hand poses (abstract).
Restrictive assumptions: Human and robot hand poses are aligned in a shared canonical space using neural rendering and kinematic optimization (method requirement per abstract).; Requires synchronized RGB, point cloud and hand kinematic modalities.

## [998] Extraction of Robotic Surface Processing Strategies from Human Demonstrations (IROS 2025, dataset, S6)
Source: https://elib.dlr.de/215557/1/eiband2025extraction.pdf; confidence HIGH.
Field cannot yet: The field cannot yet capture robust, vibration-tolerant motion and contact force of hand-held powered tool use during real material processing.
Stated limitations:
- Vive motion tracking was interrupted by occlusions and tool vibrations, reducing sampling rate. [Discussion]
- A low-cost, robust and portable capture system still needs further hardware work. [Discussion]
- Optical marker tracking is suggested but not guaranteed to solve vibration problems. [Discussion]
- Human strategies are optimized for human anatomy and ergonomics, not robot performance, e.g. box working direction produces many turns. [Discussion]
- Real material removal was not performed; a guide coat substituted because real processing changes the workpiece. [Dataset]
- Robot reproduction on the half-cylinder left small unprocessed patches near edges, caused by the finishing disk radius. [Robot experiments]
Open problems listed:
- No known powered sanding tool designs with integrated force sensing; adding an FTS would impair grasp ergonomics.
- Force-sensing surface tools mounted on robots bias human demonstrations via inertia and kinematic limits.
- Robust, low-cost, portable motion capture under tool vibration and occlusion remains unsolved.
- Deciding when to learn strategies from humans versus using pre-programmed expert strategies suited to robot capabilities.
- Extending to more shapes and techniques such as edge following and fine-structure smoothing.
- Capturing strategies under realistic material removal and material properties.
Benchmark gaps:
- SURP (21 users, 4 workpieces) / coverage: Highest coverage on the simplest box workpiece; more complex shapes lower (values in figure only).
- Robot half-cylinder reproduction / coverage: Near-full coverage, small patches unprocessed near base-plate edges.
Restrictive assumptions: Force/torque sensor placed under a fixed workpiece fixture, so only workpieces mounted on the sensor can be measured.; Workpiece geometry known as a point cloud from a 3D model or depth camera.; Guide-coat removal instead of real sanding; four simple primitive workpieces.; Single customized powered sander with a mounted Vive tracker and damper.; Robot skills defined only for two primitive shapes (plane, half-cylinder) with mean demonstrated normal force.

## [999] OpenRoboCare: A Multi-Modal Multi-Task Expert Demonstration Dataset for Robot Caregiving (IROS 2025, dataset, S6 S4)
Source: https://arxiv.org/html/2511.13707; confidence HIGH.
Field cannot yet: The field cannot yet estimate multi-body human pose under heavy contact occlusion in caregiving or recognize long-horizon caregiving procedures.
Stated limitations:
- The dataset covers only fully passive care recipients; partially mobile individuals are left for future work. [VII Conclusion]
- Clothing and slings occluded markers, causing motion-capture tracking failures for manikin pose and caregiver hands. [IV-B Pose tracking]
- Occlusion workaround uses triangulation from only three calibrated views. [IV-B Pose tracking]
- Manikins lack agency or resistance and represent only passive full-assistance scenarios. [IV-A Environment]
- Sensors run at different rates due to hardware limits; all modalities are aligned to the 15 Hz RGB-D stream. [IV-D Sensor Synchronization]
- Off-the-shelf pose estimation performs poorly on caregiving scenes. [VI-A Perception]
- Long-horizon caregiving procedures are hard to recognize for current models. [VI-B Planning]
Open problems listed:
- Accurate perception of human state under occlusions in caregiving.
- Bimanual and mobile manipulation of human limbs under critical safety constraints.
- Long-horizon planning under uncertainty.
- Personalization to users' physical function and preferences.
- Adaptation in response to human feedback.
- Caregiving datasets are task-specific, often simulated, limited in modality, and rarely expert-collected.
- Heavy occlusion from close physical interaction and assistive devices makes pose estimation hard.
- Distribution shift from general pose datasets: multi-body pose, unusual postures, camera placements that do not minimize occlusion.
- Multimodal variability in task plans originating from expert strategies.
- Long-horizon task recognition and decomposition; lack of caregiving-domain training data and terminology.
- Robots need both delicate (0.1-2 N) and high-force (20-30 N) contact, requiring compliant, backdrivable actuators and wide-range force sensing.
- Whole-arm contact requires distributed sensing and compliance along the entire arm.
- Extending to partially mobile care recipients who actively participate.
Benchmark gaps:
- OpenRoboCare 2D pose / mAP: Pretrained YOLOv11 0.0244 bathing, 0.0259 dressing, 0.0218 transfer; fine-tuned on 5 OTs still 0.6648 on transfer.
- OpenRoboCare 3D pose / MPJPE: Best RTMOPose3D 119.9 mm; MHFormer 162.7 mm.
- OpenRoboCare task recognition (VidChapters-7M, 21 videos) / qualitative: Significant gap remains; full long-horizon procedures not recognized.
Restrictive assumptions: Manikins instead of real care recipients (passive, no resistance).; 12-camera OptiTrack with marker gloves and hat plus three fixed RealSense D435i cameras in one enclosed room.; Custom tactile skin on manikins; eye-tracking glasses on caregivers.; 21 female participants, 19 of them final-year OT students; one trial per task.; Feeding excluded; 15 tasks across 5 ADLs.

## [1006] AgiBot World Colosseo: Large-Scale Manipulation Platform for Scalable and Intelligent Embodied Systems (IROS 2025, dataset, S6 S3)
Source: https://arxiv.org/html/2503.06669 (arXiv id found via export.arxiv.org API; v4 = IROS camera-ready per change log); confidence HIGH.
Field cannot yet: Train generalist manipulation policies that handle long-horizon, dexterous, open-world tasks without expensive verified teleoperation data and per-task fine-tuning.
Stated limitations:
- The VR teleoperation interface limits dexterous-hand demonstrations to a few predefined gestures; a motion-capture system was added to overcome this. [III-A Hardware]
- The pre-trained GO-1 has only basic competency and is fine-tuned with task-specific demonstrations before evaluation on new tasks. [V-A 2 Implementation Details]
- Action-labeled robot data remains limited relative to web-scale data, motivating latent actions learned from unlabeled human video. [IV-A Latent Action Model]
- More data alone does not help: unverified demonstrations performed worse than a smaller human-verified set (0.18 completion-score gap). [V-E How does data quality impact policy learning?]
Open problems listed:
- Open-set real-world tasks (fine-grained object interaction, mobile manipulation, collaborative tasks) remain a formidable challenge.
- Existing datasets are limited to short-horizon tasks in controlled labs and lack quality assurance.
- Limited action-labeled robot data relative to web-scale data.
- Generalization across diverse environments and scenarios is beyond current robotic systems.
Benchmark gaps:
- AgiBot World eval tasks (Restock Bag, Table Bussing, Pour Water) / normalized task completion score, OOD: AgiBot-pretrained RDT reaches 0.67 OOD vs 0.77 in-distribution; OXE-pretrained only 0.38 OOD.
- Wipe Table / completion score: Unverified data (482 traj.) yields 0.18 lower score than 528 verified trajectories.
- GO-1 complex tasks / success rate: Abstract reports over 60% success on complex tasks, i.e. roughly 40% of complex-task trials still fail.
Restrictive assumptions: Single homogeneous robot embodiment (AgiBot G1, dual 7-DoF arms) across all 100 robots.; Expert human teleoperation (VR or whole-body motion capture) required for every demonstration.; Human-in-the-loop verification and manual annotation of every episode.; Evaluation after task-specific fine-tuning on high-quality demonstrations.; Purpose-built 4,000 square meter collection facility with staged scenes.

## [1020] Challenges for Monocular 6D Object Pose Estimation in Robotics (T-RO 2024, survey, S5)
Source: https://arxiv.org/html/2307.12172; confidence HIGH.
Field cannot yet: Estimate accurate 6D poses from monocular RGB for unknown, non-rigid, transparent or reflective objects in naturally cluttered scenes without CAD models or per-object training.
Stated limitations:
- Claims that domain shift is solved hold only for standard datasets with limited variance in shapes, support planes, textures and illumination. [II-B 1 Domain Shift]
- No systematic study exists of how specific occlusion patterns and part visibility affect pose accuracy. [II-B 2 Occlusion Handling]
- Category-level comparison uses inconsistent train-test splits and possibly faulty published results. [II-B 7 Category-level Training, Table VI]
- Multi-object pose estimators still trail single-object estimators trained per object. [II-B 4 Multi-object and End-to-end Training]
- Render-and-compare refinement depends on textured 3D models and realistic rendering, which fails for novel and reflective or refractive objects. [II-B 5 Refinement]
Open problems listed:
- Domain shift beyond closed-world industrial/household data (underwater, space, medical).
- Occlusion handling: systematic analysis of occlusion patterns missing.
- Unambiguous yet compact pose representations.
- Multi-object training with data imbalance; trails single-object models.
- Refinement without depth and without textured models.
- Symmetry handling for keypoint-based approaches; symmetries must be known a priori.
- Category-level pose: closing the monocular vs RGB-D gap; category taxonomies.
- Novel object pose: accuracy, runtime, non-opaque objects, mobile robotics.
- Challenging materials: metallic and transparent objects.
- Learning beyond supervision (self-supervised, RL).
- Uncertainty estimation for downstream robot decisions.
- Object ontology for truly unknown objects and part-of relations.
- Deformable and articulated objects: no common pose definition or metric.
- Scene-level consistency of multi-object pose.
- Benchmark realism: clutter, backgrounds, object variation, natural annotation.
- Environmental impact of per-object training and template matching.
- Relation to generalist manipulation policies that act without explicit poses.
Benchmark gaps:
- BOP core datasets / material coverage: Six of seven core datasets contain only opaque, diffusely reflecting objects; only one includes specular metallic surfaces.
- CAMERA25 / REAL275 (NOCS) / category-level pose accuracy: Huge performance gap of RGB-only vs RGB-D approaches, apparently widening.
- NOCS, DREDS / intra-category variation: Little intra-category variation and overlapping categories, limiting tests of category generalization.
- LM vs LM-O / ADD/S: Occlusion-specific methods do not outperform general methods; occlusion handling correlates with general accuracy.
Restrictive assumptions: Most methods and datasets assume rigid objects.; Instance-level methods need a CAD model and per-object retraining.; Novel and category-level methods assume prior information about the object origin.; Standard datasets: opaque, diffuse, hand-sized objects on a single support plane, centered in view, marker-board annotation.

## [1028] A Survey on Deep Generative Models for Robot Learning From Multimodal Demonstrations (T-RO 2026, survey, S6)
Source: https://arxiv.org/html/2408.04380 (arXiv title: Deep Generative Models in Robotics: A Survey on Learning from Multimodal Demonstrations; first author Julen Urain confirmed); confidence HIGH.
Field cannot yet: Learn policies from offline demonstrations that generalize to novel goals and scenes and solve arbitrary long-horizon tasks.
Stated limitations:
- Survey scope is restricted to offline data and offline supervision, excluding interactively collected data. [I Introduction]
- Current generative policies have not shown strong generalization. [VI Future Research Directions]
- Density-estimation training objective mismatches task-success evaluation objective. [I-A Challenges in Learning from Offline Demonstrations]
Open problems listed:
- Demonstration diversity (multiple modes from different demonstrators).
- Heterogeneous action and state spaces across robots and datasets.
- Partially observable demonstrations.
- Temporal dependencies, compounding error and long-horizon planning.
- Mismatch between training (density estimation) and evaluation (task success) objectives.
- Distribution shifts and generalization to unseen contexts.
- Solving arbitrary long-horizon tasks; grounding language commands in robot actions.
- Learning from human video: embodiment mismatch, lack of action data, train-test environment mismatch.
- Sim-to-real gap for policies trained on synthetic data.
- Efficient exploration when learning online in the deployment environment.
- Structured priors, internet knowledge and 3D feature fields for generalization.
Restrictive assumptions: Offline expert demonstrations with expert action labels.; Teleoperation data, which is costly to collect at scale.

## [1035] Bi-DexHands: Towards Human-Level Bimanual Dexterous Manipulation (TPAMI 2024, benchmark, S3 S6)
Source: https://arxiv.org/html/2206.08686 (arXiv version titled 'Towards Human-Level Bimanual Dexterous Manipulation with Reinforcement Learning'; TPAMI version text not read); confidence MEDIUM.
Field cannot yet: Learn bimanual dexterous policies that generalize across many tasks from realistic (visual) observations and transfer to real hands.
Stated limitations:
- No deformable-object tasks; only articulated rigid bodies are covered. [6 Conclusion and Future Work]
- Policies use state-based observations unavailable in the real world, which hinders sim-to-real transfer. [6 Conclusion and Future Work]
- Isaac Gym cameras render serially, so visual (point cloud) RL runs at about 200 fps vs 30000+ for state input, limiting visual baselines. [Appendix (point cloud experiment)]
Open problems listed:
- Cross-task generalization of bimanual dexterous skills under multi-task/meta RL.
- Learning from demonstration for bimanual dexterous hands.
- Deformable object manipulation and simulation.
- Sim-to-real transfer of RL-learned dexterous skills.
- RL algorithm design for high-sampling-efficiency regimes.
- Offline RL under large state/action spaces and distribution shift.
Benchmark gaps:
- Bi-DexHands MT1/ML1/MT4/ML4/MT20/ML20 / average reward: Multi-task PPO does not perform well; ProMP shows tiny improvement over random policy.
- Bi-DexHands offline (Hand Over, Door Open Outward) / normalized score: IQL improves only on several datasets due to larger out-of-distribution action problem.
- Bi-DexHands 20 tasks / learning curves: SAC does not work on almost all tasks.
Restrictive assumptions: Simulation only (Isaac Gym) with Shadow Hands.; Full privileged state observations.; Rigid and articulated objects only.; Massive parallel sampling (2048 environments) on GPU.

## [1036] HiSC4D: Human-Centered Interaction and 4D Scene Capture in Large-Scale Space Using Wearable IMUs and LiDAR (TPAMI 2024, dataset, S2 S4)
Source: https://arxiv.org/html/2409.04398; confidence HIGH.
Field cannot yet: Capture multi-person interaction and scene in large spaces in real time with fine detail (texture, hands) and robustness to occlusion from wearable sensors alone.
Stated limitations:
- LiDAR vertical field of view causes body truncation and joint occlusion of the second person. [V-E Limitations]
- Low LiDAR resolution prevents reconstruction of human texture. [V-E Limitations]
- Scene-aware optimization is computationally heavy, hindering real-time and large-scale use. [V-E Limitations]
- SLAM has limits in extreme situations such as long-duration occlusions. [V-E Limitations]
Open problems listed:
- Drift-free motion capture in large capture areas with IMUs.
- Capturing human-human interaction from an egocentric view in large scenes with 3D ground truth.
- Truncation and occlusion of the second person due to sensor field of view.
- Real-time capture with scene-aware optimization.
- SLAM robustness under long-duration occlusion.
Benchmark gaps:
- HiSC4D S3 mapping / Chamfer distance: Mean 6.5 cm; larger errors near trees and untraversed high-floor buildings.
- HiSC4D / pose-to-point-cloud distance: IMU-only 569.7 mm, IMU+ICP 65.1 mm, reduced a further 47.7% by full optimization.
- HiSC4D S4 / runtime: Optimization takes 0.73 h (first person) and 2.80 h (second person) for 7725 frames.
Restrictive assumptions: Both people wear 17-IMU suits; first person wears a head-mounted LiDAR and backpack.; Rigid LiDAR-to-head transformation.; Calibration at start: A-pose facing a planar marker, second person 5 m ahead, jump-in-place for synchronization.; Offline batch optimization (0.73 h and 2.80 h for one 7725-frame sequence).; Pre-scanned subject body models and only two people per sequence.

## [1038] Playing for 3D Human Recovery (TPAMI 2024, dataset, S4)
Source: https://arxiv.org/html/2110.07588; confidence HIGH.
Field cannot yet: Obtain accurate in-the-wild 3D human ground truth at scale without synthetic-to-real gaps, especially for rare viewpoints, poses and occlusions.
Stated limitations:
- Domain gaps between synthetic GTA-Human and real data persist. [IV-B Better 3D Human Recovery with Data Mixture]
- Gains on indoor benchmarks Human3.6M and MPI-INF-3DHP are smaller than on 3DPW, attributed to indoor-outdoor domain gaps. [IV-C, Table V]
- Annotation captures bone lengths but not full body shape from subject meshes. [V Conclusion]
- Manual inspection of all examples is impractical; GTA-V content may carry stereotypes and biases. [Appendix A-C Stereotypes and Biases]
Open problems listed:
- Scarcity and cost of 3D parametric ground truth in the wild.
- Synthetic-to-real domain gap.
- Data remains a critical bottleneck for accurate human pose and shape estimation.
- Full body shape annotation from synthetic meshes.
Benchmark gaps:
- Human3.6M, MPI-INF-3DHP / PA-MPJPE: Gains from GTA-Human are smaller than on 3DPW, attributed to indoor-outdoor gap.
- GTA-Human eval by factor / error vs data density: Errors rise drastically in sparse regions of camera angle, pose and occlusion.
- EgoBody / error vs elevation angle: Real-only models have large errors at high camera elevation angles.
Restrictive assumptions: Synthetic game-engine data (GTA-V) with non-commercial license.; Single-person monocular RGB human recovery; no hand or object interaction focus.; Mixing with real data still needed (blended training or fine-tuning).

## [1060] Reconstructing Three-Dimensional Models of Interacting Humans (TPAMI 2025, dataset, S4)
Source: https://arxiv.org/html/2308.01854; confidence HIGH.
Field cannot yet: Reconstruct close physical contact between people from monocular images with contact-accurate geometry and errors well below 50 mm.
Stated limitations:
- Only one subject per video is motion-tracked, a limitation inherited from the Vicon mocap system. [I Introduction]
- Marker placement does not allow tracking most hand articulation. [IV-D 3D Reconstruction in a Controlled Setup]
- Current mocap fails for multiple people in close proximity and occlusion. [IV-D]
- Reconstruction of interactions remains hard with errors above 50 mm. [V-C Evaluation Protocol and Benchmark]
- Contact distance not driven to zero because parameters are tuned for pose error. [V-B, Table III caption]
Open problems listed:
- Accurate 3D reconstruction of close physical contact between people from monocular images.
- Capturing ground truth for multiple people in contact with mocap.
- Hand articulation during interactions.
Benchmark gaps:
- CHI3D public benchmark / MPJPE (contact frames): Best method (Cliff) 88.66 mm; ours 106.15 mm; translation errors 676-3158 mm.
- FlickrCI3D / contact signature IoU_75: 0.082 vs human 0.226; segmentation IoU_75 0.318 vs human 0.456.
- FlickrCI3D / contact classification accuracy: 0.846 average accuracy.
Restrictive assumptions: Two people only.; Ground-truth contact annotations used in the contact-consistent optimization and in CHI3D ground-truth fitting.; Lab mocap plus multi-view RGB plus 3D body scans for ground truth.; Monocular test protocol with one camera view.

## [1072] Ego4D: Around the World in 3,600 Hours of Egocentric Video (TPAMI 2025, dataset, S6 S1)
Source: https://arxiv.org/html/2110.07058 (arXiv CVPR-era version titled '3,000 Hours'; TPAMI text not read); confidence MEDIUM.
Field cannot yet: Reliably localize and anticipate hand-object interactions and object state changes in long, uncurated egocentric video.
Stated limitations:
- Geographic coverage incomplete; wearers mostly urban or college-town. [3.5 Possible sources of bias]
- COVID-19 skewed footage toward stay-at-home activities; battery life biases toward active portions of the day. [3.5 Possible sources of bias]
- Narrations from annotators at two African sites may carry local word choice bias. [3.5 Possible sources of bias]
- Dataset scale is an accessibility obstacle. [3.6 Dataset accessibility]
- Head-up cameras miss interactions close to the body. [3.3 Cameras and modalities]
Open problems listed:
- Long-form egocentric video understanding without manual temporal curation.
- Spatial reasoning in static 3D environments combined with dynamic video of a moving person.
- Object state change understanding generalizing over tools, grasps and methods.
- Joint spatio-temporal modelling of manipulation and its effect on objects.
- Audio-visual diarization with overlapping speech and head-motion blur.
- Social attention (looking/talking to me) under blur and fast head motion.
- Forecasting locomotion, hand motion, next active objects and long-term actions.
- Domain gap between third-person pretraining and egocentric video.
- Annotating 'stuff' categories and objects of change with large tools.
- Geographic and demographic coverage.
Benchmark gaps:
- Ego4D Hands and Objects / state change object detection AP: All baselines 8-14% AP with single frame input.
- Ego4D Hands and Objects / state change classification accuracy: Just over 60% vs naive near 50%.
- Ego4D Forecasting / short-term anticipation Top-5 mAP: 2.07% val, 2.45% test.
- Ego4D Episodic Memory MQ / average mAP: 5.96%.
- Ego4D Social / mAP: LAM 78.07, TTM 55.06.
- Ego4D AV Diarization / DER / WER: DER above 80%, WER above 60%.
Restrictive assumptions: Monocular head-worn RGB for most data; 3D scans, gaze, stereo only for subsets.; Annotations limited to subsets (48-1,000 hours per benchmark).

## [1080] A Comparative Assessment of Accuracy in Video-Based Monocular Human Pose Estimation Frameworks (TPAMI 2026, benchmark, S4 S7)
Source: abstract only (PubMed abstract via https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=41805522; IEEE PDF returned HTTP 418, no arXiv version found); confidence LOW.
Field cannot yet: From the abstract only: the field lacks a standard, mocap-referenced comparison of off-the-shelf monocular pose frameworks on joint-angle accuracy; the abstract reports MeTRAbs best overall but gives no error values.
Restrictive assumptions: Evaluation dataset is existing and unpublished: nine individuals performing eight exercises; Monocular RGB video from two camera views with different planar angles; Reference is synchronized gold-standard motion capture; accuracy is assessed on joint angles only (weighted MAE and weighted ICC); Framework selection limited to frameworks since 2019 meeting predefined inclusion criteria (16 frameworks)

## [1088] Deep Learning-Based Object Pose Estimation: A Comprehensive Survey (IJCV 2026, survey, S5)
Source: https://arxiv.org/pdf/2405.07801; confidence HIGH.
Field cannot yet: Estimate object pose robustly under severe occlusion for unseen objects without a CAD model or annotated reference views.
Stated limitations:
- Instance-level methods are precise but generalize poorly and many require CAD models. [1 Introduction]
- Category-level methods cannot generalize to unseen categories and need retraining with new data. [4.2 Brief Discussion]
- Unseen-object methods still need CAD models or annotated reference views. [7.1 Emerging Trends]
- No method handles severe occlusion. [7.1 Emerging Trends]
- Hand-object interaction pose methods depend on object CAD models that are hard to obtain in daily scenes. [6.4 Hand-Object Interaction]
- Template matching methods are slow, occlusion-sensitive and affected by complex backgrounds and lighting. [5.1 CAD Model-Based Methods]
- Models output a single deterministic pose, limiting robustness in ambiguous or occluded conditions. [7.2 Future Directions]
Open problems listed:
- Reliance on labor-intensive real-world labeled training data
- LLM/LVM-guided weak and self-supervised learning
- Synthetic-to-real domain gap
- Novel-view-reconstruction priors: preserving geometric fidelity under intra-class variation, generative artifacts, view inconsistency, real-time on robots
- Deployment complexity of detection-then-pose pipelines; need end-to-end methods
- High-precision unseen object pose from a single RGB image without depth
- Large models with inefficient runtime; lightweighting for mobile and robots
- Articulated object pose estimation (multiple DoF, self-occlusion)
- Transparent object pose estimation (no texture, color or depth)
- Robustness to severe occlusion
- Few-shot generalization of category-level methods to unseen categories
- CAD-model-free and sparse-reference-view unseen object pose estimation
- Open-vocabulary strong generalization
- Generalization to intra-class unknown and category-unseen objects
- Foundation-model-based pose representation and adaptation (geometry-aware adapters, SE(3)-equivariant heads)
- Label-efficient learning to remove dependence on dense 6D annotations
- Uncertainty modeling and temporal consistency for symmetric, transparent, reflective objects and dynamic scenes
- Cross-modal and physically grounded estimation using tactile, inertial, contact and force cues
- Scalable benchmarks and realistic physics-aware simulation
Benchmark gaps:
- object pose benchmarks (general) / scale and diversity: Survey states most benchmarks remain limited in scale, diversity, or realism; calls for real-world datasets with fine-grained annotations for rigid and articulated objects.
Restrictive assumptions: Survey: reviewed instance-level methods need per-object training and often CAD models; Category-level methods need category-level training data and shape priors (CAD libraries); Unseen-object methods need CAD models or annotated reference views; SOTA pipelines need a separate pre-trained detector or segmenter before pose estimation

## [1091] An Outlook into the Future of Egocentric Vision (IJCV 2024, survey, S1 S6)
Source: https://arxiv.org/html/2308.07123; confidence HIGH.
Field cannot yet: Estimate hand pose and hand-object interaction robustly in egocentric video across arbitrary objects and environments when hands manipulate objects.
Stated limitations:
- Hand pose methods typically fail when hands interact with objects in complex scenarios. [4.8 Hand and Hand-Object Interactions, For the future]
- No robust HOI methods generalising across objects and environments. [4.8 Hand and Hand-Object Interactions, For the future]
- Egocentric full-body pose is far below third-person accuracy. [4.7 Full-body Pose Estimation, For the future]
- 3D reconstruction struggles with dynamic content in egocentric video. [4.2 3D Scene Understanding, For the future]
- Lack of HOI-labelled data; synthetic data lacks photorealism; object transformations under manipulation barely studied. [4.8 Hand and Hand-Object Interactions, For the future]
- Full-body estimation is not integrated with action, forecasting or hand-object estimation. [4.7 Full-body Pose Estimation, For the future]
Open problems listed:
- Localisation robustness in dynamic, changing wearable environments; limited compute; benchmarks with low scene diversity and navigation-only sequences
- 3D understanding of dynamic phenomena under motion blur and unusual viewpoints; ego-exo combination with limited applicability
- Action recognition: few ego-specific architectures, low fine-grained accuracy, long temporal dependencies, long-tail data, missing gaze annotations, modality-specific labels, reliance on labelled data
- Anticipation: limited performance and unrealistic trimmed-video assumption
- Gaze: large annotated datasets, individual bias, blinks, occlusion and illumination
- Social behaviour understanding far from human level; needs interdisciplinary research
- Egocentric full-body pose far below third-person; natural-activity poses missing from datasets; not integrated with hand-object and action tasks
- Hand pose fails during object interaction; HOI methods do not generalise across objects and environments; lack of HOI-labelled data; synthetic data lacks realism; object transformations under manipulation
- Gesture recognition with larger gesture vocabularies
- Egocentric person re-identification lagging (about 65% mAP); need larger egocentric Re-ID benchmarks
- Summarisation of day-long video and query-focused summarisation far from solved
- Egocentric VQA: indoor-only testbeds, audio cues, long-form video reasoning
- Adapting vision-language models to egocentric data
- Privacy: non-systematic studies, small demographics, few privacy-preserving solutions
- Combining tasks into a holistic multi-task assistant
- Open-set settings, real-time efficiency, always-connected yet privacy-preserving devices
- Bridging egocentric and third-person approaches
Benchmark gaps:
- AssemblyHands / MPJPE: State-of-the-art 3D hand pose reaches 23.46 mm MPJPE on the test set; survey says room for further advancement.
- EPIC-KITCHENS VISOR / Active Object AP: Hand-object segmentation: hand mask AP 95.6% but active object AP only 25.7%.
- Ego4D / Object state change AP: Object state change accuracy 67.6% and AP 15.5%.
- EgoBody / World PA-First MPJPE: Pose of other people from egocentric view: 141.1 mm, versus about 20 mm on Human3.6M third-person.
- egocentric body pose (various) / MPJPE: Body-oriented camera 118.5 mm; outward-looking 121.1 to 152.1 mm.
- LaMAR / single-frame localisation recall: 45.6% / 61.3% at (1 deg, 10 cm)/(5 deg, 1 m).
- EPIC-KITCHENS-100 / action classification accuracy: State of the art 51.0%; papers improve by 0.5-1%.
- EgoSchema / QA accuracy: Models under 33% versus about 76% for humans.
Restrictive assumptions: Survey scope: focus on cameras and visual cues though future devices need multimodality; Most anticipation methods assume trimmed video sampled a fixed time before the action; Wearable devices have limited compute

## [1097] Towards Dynamic 3D Reconstruction of Hand-Instrument Interaction in Ophthalmic Surgery (NeurIPS 2025, dataset, S1 S3 S7 S5)
Source: https://arxiv.org/html/2505.17677; confidence HIGH.
Field cannot yet: Reconstruct two hands and multiple thin, articulated instruments accurately from monocular input in real clinical settings across centers and lighting conditions.
Stated limitations:
- Data from a single surgical procedure at a single center; generalizability to other workflows, habits and illumination is limited. [Appendix E Discussion]
- Microscope illumination overexposes instrument tips in RGB, affecting pose estimation. [Appendix E Discussion]
- Microscope view not integrated for joint reconstruction of ocular surface, hands and instruments. [Appendix E Discussion]
Open problems listed:
- Generalization beyond single-center, single-procedure data (workflows, surgeon habits, illumination)
- Instrument-tip overexposure under microscope light
- Joint reconstruction of ocular surface, hands and instruments using microscope view
- Most surgical systems remain passive monitoring rather than real-time assistance
- Synthetic medical hand datasets lack clinical realism
Benchmark gaps:
- OphNet-3D bimanual hand / MPJPE / MRRTE (mm): Best RGB model H-Net: 17.66 mm MPJPE and 31.89 mm MRRTE on test; RGB-D H-Net-D 15.97 / 26.59 mm.
- OphNet-3D hand-instrument / ADD-S (%): Best RGB OH-Net 70.79% on test; RGB-D OH-Net-D 76.31%; prior HOI methods 56.89 to 61.32%.
- OphNet-3D hand-instrument / MAE articulation (%): Articulation error 11.17% (RGB) and 9.62% (RGB-D) on test.
Restrictive assumptions: Annotation uses eight calibrated, synchronized RGB-D cameras; Instruments laser-scanned to CAD meshes; articulated instruments scanned in parts with known articulation range; SAM2 masks require manual correction; Offline multi-stage optimization with motion prior and biomechanical constraints; Single procedure type (cataract surgery), single center, surgeons wearing gloves

## [1099] SHOW3D: Capturing Scenes of 3D Hands and Objects in the Wild (CVPR 2026, dataset, S1 S3 S5)
Source: https://arxiv.org/html/2603.28760; confidence HIGH.
Field cannot yet: Produce accurate 3D hand and object pose in unconstrained outdoor or in-the-wild scenes without CAD models, multi-camera rigs, or confidence filtering that discards hard frames.
Stated limitations:
- Annotation yield is imperfect in the wild; automated filtering discards frames. [5 Experiments, 3D hand pose estimation]
- Hands missed entirely under heavy occlusion by object or other hand. [Appendix, Figure 14 failure cases]
- Slight hand pose errors cause hand-object interpenetration. [Appendix, Failure Modes]
- DINOv2-based object tracking misses objects under severe occlusion or strong sunlight. [Appendix, Failure Modes]
- Rotation ambiguity on near-symmetric objects (mug handle hallucinated). [Appendix, Figure 16]
- Work focuses on vision only; other modalities left for future. [6 Conclusion]
Open problems listed:
- Trade-off between environmental realism and 3D annotation accuracy
- Studio-trained hand-object models generalize poorly outside controlled indoor environments
- Marker-based mocap alters natural hand and object appearance
- In-the-wild datasets (Ego-Exo4D, Nymeria) lack dense accurate 3D hand and object ground truth
- Annotation failures under heavy occlusion, strong sunlight and symmetric objects
- Integration of tactile and range modalities
- Use for embodied applications such as teleoperation
Benchmark gaps:
- SHOW3D (trained on HOT3D) / Interaction field ADE (mm): 22.57 mm when training on HOT3D and testing on SHOW3D versus 13.82 mm in-domain.
- SHOW3D (trained on UmeTrack / HOT3D) / MKPE (mm): 3D hand pose error 22.2 mm (UmeTrack) and 19.6 mm (HOT3D) versus 14.3 mm with all three training sets.
- SHOW3D / 6DoF forecasting translation error (mm): Mean 30.4 mm at 30 frames and 35.0 mm at 60 frames even with text; 42.7 / 46.7 mm without.
- SHOW3D annotation vs manual labels / P90 MPJPE (mm): Hand annotation P90 error 16.48 mm for hand-object interaction against manual annotation (median 6.36 mm).
Restrictive assumptions: Object pose annotation requires a CAD model per object (subset of HOT3D objects); At most one instance of each object class assumed present; Backpack rig of about 8 kg with ten synchronized cameras plus five MoCap cameras tracking the headset; Workstation on a mobile cart moved by an operator; Personalized hand model derived from a high-resolution hand scan; Offline annotation with confidence filtering

## [1103] NVS-HO: A Benchmark for Novel View Synthesis of Handheld Objects (arXiv 2026, benchmark, S1)
Source: https://arxiv.org/html/2602.05822; confidence HIGH.
Field cannot yet: Recover accurate object poses and full-appearance novel views of an object rotated in hand from RGB only.
Stated limitations:
- Current NVS pipelines struggle in handheld scenarios because hand occlusions hamper learning full appearance. [Conclusion]
- Feed-forward NVS models excluded because they do not scale to 100+ input images; left for future. [2 Related Work]
- Absolute rendering quality low even for best baseline. [5 Results]
- VGGT struggles with large uniformly colored backgrounds; required token pruning. [4 Baselines]
Open problems listed:
- Robust pose estimation for objects manipulated in hand in front of a static camera
- Handling hand-induced partial occlusion in NVS
- Scaling feed-forward pose-free NVS to 100+ image sequences
- Annotating object poses under hand occlusion and low texture, and when rotated about its own axis
- Lack of HOI datasets with ground-truth views and protocols for NVS
Benchmark gaps:
- NVS-HO / PSNR (foreground): Median PSNR about 16 for best baseline (Splatfacto with COLMAP poses); NeRF and VGGT-pose variants worse.
- NVS-HO / PSNR/SSIM/LPIPS variance: Large variance across objects; COLMAP beats VGGT on all metrics.
Restrictive assumptions: Static camera with object rotated by hand; Controlled indoor lighting; Rigid objects (grocery items and toys); Ground truth requires a second sequence with the object fixed on a ChArUco board; Grounded SAM2 masks with object-specific prompts; COLMAP overlap tuned per object; Calibrated intrinsics

## [1112] HOSt3R: Keypoint-free Hand-Object 3D Reconstruction from RGB images (ICCV Workshops 2025, method, S1)
Source: https://arxiv.org/html/2508.16465; confidence HIGH.
Field cannot yet: Reconstruct hand-object shape from monocular RGB when the grasp changes over time, or recover fine finger geometry under sparse views.
Stated limitations:
- Fingers not fully recovered due to insufficient viewpoint coverage. [Experiments, HO3D generalization]
- Fine finger details under sparse viewpoints remain a limitation. [Conclusion]
- Specular objects degrade pointmaps, causing pose errors and artifacts. [Supplementary, Figure 8]
- Pointmaps assume one surface per camera ray; translucent surfaces not considered. [Method, Pointmap]
- Slightly underperforms COLMAP on some metrics. [Experiments]
Benchmark gaps:
- SHOWMe / Rotation error (deg): 18.2 deg rotation error; COLMAP 15.9 on recovered frames only.
- SHOWMe / % frames within 15cm&15deg: Only 50.5% of frames under 15 cm and 15 deg; 86.3% under 30 cm and 30 deg.
- SHOWMe / F-score @5mm (%): 56.4% with estimated transforms versus 82.3% using ground-truth transforms (HHOR).
Restrictive assumptions: Rigid hand-object motion: hand grasp fixed while hand and object move together; Hand-object masks required (loss and graph over hand-object pixels); Offline: 60 evenly sampled frames, pose averaging and implicit neural reconstruction per sequence; Pointmap network fine-tuned on synthetic multi-view ObMan data; Monocular RGB, no camera intrinsics or templates required

## [1118] Hand-Object Interaction in the Age of Large Foundation Models: Reconstruction, Generation, and Embodied Transfer (arXiv 2026, survey, S1 S6)
Source: https://arxiv.org/html/2607.28394; confidence HIGH.
Field cannot yet: Jointly recover hand, object, contact and camera motion in one world frame over long manipulations with grasp changes, and verify interaction and physical correctness.
Stated limitations:
- No single prior family resolves HOI; each can fail. [8.1]
- Evaluation dominated by geometric metrics; contact, function, physics and state transitions rarely assessed together. [8.2]
- Joint world-frame recovery of ego-motion, contact and long-horizon hand-object state is unsolved. [8.3]
- Grounding errors propagate downstream, worst at fingertips, transparent, reflective and occluded regions. [4.2.4]
- Appearance features carry no metric scale, articulation or contact information. [5.2.4]
- Geometric metrics do not establish correct contact or function. [7.2.1]
Open problems listed:
- Integrated, verifiable HOI systems composing geometric, semantic and visual priors
- Moving from geometric to interaction correctness; distinguishing proximity from force-transmitting contact
- Long-horizon, dynamic-camera, world-space HOI across grasp, manipulation, release and re-grasp
- Prior reliability, routing and conflict resolution
- Dynamic embodied memory reconciling pre-grasp estimates with later evidence under self-occlusion
- Robot-centric understanding of human HOI including intent, part identity, contact and state change
- Retrieval failure reporting separate from pose-fitting errors
- Evaluating camera pose, depth, alignment, temporal drift and contact consistency for spatial priors
- Grounding evaluation by downstream effect; errors at fingertips, transparent, reflective, occluded regions
- Language priors lack geometric and physical validity (force closure, collision-free placement)
- Evaluating visual priors on unseen categories rather than benchmark splits
- Image and video generation fidelity not ensuring anatomy, contact, physics
- Metric blind spots: geometric, visual and contact metrics do not verify function, task success or physical dynamics
Benchmark gaps:
- HOI benchmarks (ContactDB, ContactPose, GRAB, ARCTIC, EPIC-Contact) / contact and function evaluation: Contact annotations exist but protocols rarely assess contact with function, physical plausibility and object-state transitions.
- PA-MPJPE / PA-MPVPE protocols / Procrustes-aligned errors: Alignment conceals errors in absolute position, orientation and metric scale.
Restrictive assumptions: Survey: retrieval priors need a suitable asset in a library; Geometry metrics need paired 3D ground truth; ADD needs object model points; Contact metrics need contact annotations or registered surfaces; physical metrics depend on mesh quality and simulators

## [1119] HOI4D: A 4D Egocentric Dataset for Category-Level Human-Object Interaction (CVPR 2022, dataset, S1 S5 S6)
Source: https://arxiv.org/html/2203.01577; confidence HIGH.
Field cannot yet: The field cannot yet track category-level object pose reliably while a hand is occluding and moving the object, let alone for two cooperating hands.
Stated limitations:
- Two-handed manipulation is not covered; the authors consider single-hand manipulation still unsolved and leave hand cooperation for future study. [7 Limitations and Future Work]
- Hand pose annotation by optimization fails on some frames (ambiguous poses, bad initialization) and these frames are corrected manually. [3 Data annotation (hand pose)]
- Only 1 of every 10 frames gets manual object pose labels; the rest are propagated, and human 3D pose labels are not fully reliable. [3.5 Object pose annotation]
- Scanning large objects with complex topology and materials remains hard for the mesh reconstruction step. [3.5 Object mesh reconstruction]
Open problems listed:
- Two-handed manipulation and cooperation of hands (not covered).
- Single-hand manipulation perception itself remains challenging.
- Category-level object and part pose tracking under hand occlusion, sensor noise, clutter and fast motion.
- Simulating natural human motion and functional grasping for generic objects (synthetic data realism for sim-to-real).
- Indoor 4D dynamic point cloud segmentation of small, moving, occluded objects.
- Fine-grained egocentric action segmentation that perceives the current action rather than action order.
- Scanning large objects with complex topology and materials.
- Category-level dexterous robot manipulation from human demonstrations (low success rates).
Benchmark gaps:
- HOI4D (category-level rigid pose tracking) / 5deg5cm accuracy, BundleTrack: toy car 9.7, mug 12.9, bottle 19.3, bowl 22.6; bottle is 86.5 on NOCS without hand occlusion.
- HOI4D (laptop part pose tracking) / 5deg5cm accuracy: ICP 0.9/1.5 and BundleTrack 24.2/12.2 for keyboard/display parts.
- HOI4D (4D point cloud semantic segmentation) / mIoU objects vs background: PSTNet 31.4 vs 72.6; P4Transformer 44.6 vs 77.7.
- HOI4D (fine-grained action segmentation) / accuracy: Asformer 46.8 on HOI4D vs 85.6 on 50Salads.
- HOI4D-derived robot imitation / success rate: Both RL and IL success rates are low for category-level dexterous manipulation.
Restrictive assumptions: Single hand only; no bimanual sequences.; Egocentric head-mounted single RGB-D camera.; Object meshes from scanning or category CAD pipeline; manual keyframe pose labels every 10th frame plus propagation.; 16 categories of household objects; 9 participants (abstract says 4).

## [1120] OakInk: A Large-scale Knowledge Repository for Understanding Hand-Object Interaction (CVPR 2022, dataset, S1)
Source: https://arxiv.org/html/2203.15709; confidence HIGH.
Field cannot yet: The field cannot yet capture or model dynamic hand interactions with moving parts of articulated objects at the scale available for static rigid grasps.
Stated limitations:
- Does not record dynamic hand interaction with movable parts of articulated objects, and does not address transfer to multi-finger robot hands. [5 Discussion]
- Benchmarked only on computer vision and graphics tasks; robotics use is future work. [5 Discussion]
- MANO and rigid object models cannot represent contact deformation, so a contactness heuristic imitates it. [3.2 Contactness]
- Direct copying of hand poses to other objects fails in most cases, so a transfer optimization is needed. [3.3 Interaction transfer]
Open problems listed:
- Real-world datasets contain few objects and few distinct interactions.
- Synthetic grasps do not reflect human interaction distributions or object affordance.
- Intent-agnostic grasp generation; need intent-based and handover generation.
- Dynamic interaction with articulated object movable parts.
- Transfer of human interaction knowledge to multi-finger robot hands.
- Modeling contact deformation of hand and object.
Benchmark gaps:
- OakInk-Image SP1 (subject split) / MPJPE (mm): I2L-MeshNet 18.04, HandTailor 15.72 versus 12.10/11.20 on view split.
- OakInk-Image SP2 (object split) / MPJPE (mm): I2L-MeshNet 15.79, HandTailor 14.14.
- OakInk-Image (HOPE) / MPCPE (mm): Hasson et al. 56.09 and Tekin et al. 52.16 object corner error overall; mug and knife up to 60-68 mm.
- OakInk-Shape (GraspGen) / penetration / sim displacement: GrabNet penetration 0.67 cm, sim displacement 1.21 cm; handover generation on some objects up to 1.57 cm penetration and 2.88 cm displacement.
Restrictive assumptions: Objects selected for single-hand manipulation.; Multi-view RGB with optical MoCap reflective markers on objects for annotation.; Static single steady grasp pose chosen per sequence for the Shape subset.; HOPE benchmark trained and tested on the same object instances with known models.

## [1121] ARCTIC: A Dataset for Dexterous Bimanual Hand-Object Manipulation (CVPR 2023, dataset, S1 S3 S6 S5)
Source: https://arxiv.org/html/2204.13662; confidence HIGH.
Field cannot yet: The field cannot yet reconstruct two hands and an unknown articulated object from monocular video with spatio-temporally consistent contact.
Stated limitations:
- Baselines assume known object models; articulated shape estimation of unknown objects is treated as an orthogonal problem. [6 Discussions and Limitations (SupMat)]
- Some objects are toys, not to scale, with less visual complexity than real objects. [6 Discussions and Limitations (SupMat)]
- SMPL-X/MANO hands do not capture skin deformation during contact. [6 Discussions and Limitations (SupMat)]
- Optical markers on hands may introduce label noise in the images. [6 Discussions and Limitations (SupMat)]
- All objects have only one articulation degree of freedom. [6 Discussions and Limitations (SupMat)]
Open problems listed:
- Generating dexterous bimanual manipulation motion with articulated objects (prior work does not).
- Consistent motion reconstruction of two hands and an articulated object from video.
- Interaction field estimation and its use for contact-aware pose estimation.
- Articulated object pose estimators that account for humans in the scene.
- Articulated 3D shape estimation of unknown objects (known-template assumption).
- Deformable hand/body models for true contact.
- Objects with more DoF and more complexity; depth ambiguity and occlusion.
Benchmark gaps:
- ARCTIC egocentric test / object success rate (%): ArcticNet-SF 53.9, ArcticNet-LSTM 53.5.
- ARCTIC allocentric test / CDev hand-object (mm): ArcticNet-SF 41.6, LSTM 38.9; MRRPE right-to-left 49-52 mm.
- ARCTIC egocentric test / CDev hand-object (mm): ArcticNet-SF 44.7, LSTM 43.3.
- ARCTIC / MPJPE hand (mm): 19.2-23.8 mm root-relative across splits.
- ARCTIC / interaction field distance error (mm): 8.0-10.0 mm average distance error.
Restrictive assumptions: Known object template (scanned mesh and articulation axis) at test time for baselines.; Marker-based motion capture for ground truth in a lab with 8 static views plus 1 egocentric.; Objects with a single articulation DoF; 11 objects, 10 subjects.; Monocular RGB input to baselines with root-relative evaluation.

## [1122] AssemblyHands: Towards Egocentric Activity Understanding via 3D Hand Pose Estimation (CVPR 2023, dataset, S1 S3)
Source: https://arxiv.org/html/2304.12301; confidence HIGH.
Field cannot yet: The field cannot yet estimate accurate 3D hand pose from egocentric views alone under heavy hand-object occlusion, nor annotate pose of small manipulated parts.
Stated limitations:
- Work covers hand pose and action classification only; object pose annotation is not provided because small assembly parts make it hard. [6 Conclusion, Limitations and future work]
- Egocentric-only tracking has severe failures under heavy hand-object occlusion and narrow stereo overlap. [3 AssemblyHands dataset]
- Iterative refinement accumulates error when left/right hand identity is wrong at initialization. [Supplementary]
Open problems listed:
- Object pose annotation with many small object parts.
- Accurate egocentric 3D hand pose under heavy hand-object occlusion.
- Depth accuracy for hands away from the narrow egocentric stereo area.
- Joint modeling of hands, objects and actions.
- Scaling accurate annotation across full Assembly101 at higher frame rates.
Benchmark gaps:
- AssemblyHands Eval-M / MPJPE (mm), single-view egocentric: Best SVEgoNet 21.92 mm; UmeTrack about 33% higher.
- AssemblyHands / verb accuracy (%): SVEgoNet poses 54.7 vs upper bound 60.0 from annotated poses; UmeTrack 50.3.
- AssemblyHands annotation / MPJPE (mm): Egocentric-only annotation 27.55 mm.
Restrictive assumptions: High-quality labels require 8 static exocentric RGB cameras plus calibrated headset; egocentric-only is not accurate enough.; Manual annotations to bootstrap the automatic annotator.; Single domain: toy assembly on a table.

## [1123] AffordPose: A Large-scale Dataset of Hand-Object Interactions with Affordance-driven Hand Pose (ICCV 2023, dataset, S1)
Source: https://arxiv.org/html/2309.08942; confidence HIGH.
Field cannot yet: The field cannot yet produce affordance-correct hand contacts on small functional parts or scale such annotation to dynamic and bimanual interactions.
Stated limitations:
- Dataset is static grasps; affordance-driven dynamic interactions (washing face, pouring) are left for future expansion. [6 Conclusions]
- Bimanual and human-robot cooperation not covered. [6 Conclusions]
- Manual pose annotation is costly; efficient semi-automatic methods are needed to scale. [6 Conclusions]
- Generated hand poses can contact the wrong region, giving unrealistic interactions. [5 Experiments, challenging cases]
Open problems listed:
- Affordance-driven dynamic interactions for complex tasks.
- Bimanual hand-hand cooperation and human-robot cooperation with affordance assignment.
- Efficient semi-automatic hand pose annotation for large high-quality data.
- Accurate contact on small functional parts in generation.
Benchmark gaps:
- AffordPose (interaction generation) / affordance accuracy: Particularly low for pull and twist affordances.
- AffordPose (affordance understanding) / accuracy / IoU: Pull affordance worst in all experiments except intrinsic-parameter classification.
Restrictive assumptions: No camera sensing: hand poses manually adjusted in GraspIt on PartNet object models.; Fixed MANO shape parameter; single right hand.; Objects scaled to human-hand size; 641 objects from 13 categories.

## [1124] SHOWMe: Benchmarking Object-agnostic Hand-Object 3D Reconstruction (ICCV Workshops (ACVR) 2023, benchmark, S1 S5)
Source: https://arxiv.org/html/2309.10748; confidence HIGH.
Field cannot yet: The field cannot yet reliably reconstruct an unknown hand-held object from monocular video without accurate camera/object registration, even under a rigid-grasp assumption.
Stated limitations:
- Assumes a rigid hand-object configuration with a static camera throughout the video, a simplification of dynamic interaction. [1 Introduction]
- Reconstruction quality depends on initial rigid transformations, hard to get for texture-less objects or heavy hand occlusion. [6 Conclusion]
- Arm is masked out by sleeve colour because it violates the rigidity assumption. [3 Dataset acquisition]
Open problems listed:
- Object-agnostic hand-object reconstruction without a known template.
- Robust rigid registration for texture-less objects and heavy hand occlusion.
- Reconstruction of small objects with few visual features.
- Moving beyond rigid grasps to dynamic interaction.
- Avoiding MANO prior limits for detailed hand shape.
Benchmark gaps:
- SHOWMe / F-score @5mm (%): FDR drops from 73.5 with GT transforms to 37.6 with COLMAP and 20 with DOPE.
- SHOWMe small objects / F-score @5mm (%): COLMAP+FDR 30.23 small vs 47.93 larger; DOPE+FDR 23.43 vs 17.85.
Restrictive assumptions: Rigid grasp: hand pose relative to object constant over the sequence.; Static camera; single hand.; Ground truth requires 3D scanner and RGB-D ICP registration.

## [1125] HOH: Markerless Multimodal Human-Object-Human Handover Dataset with Large Object Count (NeurIPS (Datasets and Benchmarks) 2023, dataset, S3 S1 S6 S2)
Source: https://arxiv.org/html/2310.00723; confidence HIGH.
Field cannot yet: The field cannot yet automatically annotate or track hand poses of two interacting people around a handed-over object in markerless multi-view RGB-D.
Stated limitations:
- No grip force data because of the instrumentation-free setup. [5 Discussion, Limitations]
- No ground-truth hand pose; manual hand pose annotation in markerless data under occlusion and motion is daunting. [5 Discussion, Limitations]
- Participants cover a narrow range of age and ability. [5 Discussion, Limitations]
- Shiny or dark objects give poor Kinect ToF depth and were spray painted or taped. [Supplementary, object dataset]
- Markerless capture makes dense ground truth such as object pose costly in manual effort. [Datasheet]
Open problems listed:
- Small object counts in handover datasets.
- Marker-based capture limits clothing diversity and lacks hand geometry and object structure.
- Single-person HOI findings, even bimanual, do not transfer to two-person handovers (non-mirrored hands, larger translations, 3+ hands).
- Egocentric setups infeasible for handover due to limited field of view.
- Object segmentation and tracking under multi-person occlusions.
- Ground-truth hand pose annotation in markerless multi-person data.
- Grip force measurement without constraining grasps.
- Participant diversity.
Benchmark gaps:
- HOH / MEAE (o2or), GT: 0.851 complete and 0.843 partial clouds.
- HOH / %OLGO (o2gg): 17.39% complete vs 58.12% partial.
Restrictive assumptions: 4 Azure Kinect RGB-D plus 4 FLIR cameras in a green-screened 1.7 m rig, calibrated by checkerboard with manual extrinsic fine-tuning.; Object pose from scanned meshes via ICP, keyframe-annotated SAM masks tracked with Track Anything.; Matte-painted objects; objects under 2.5 kg graspable unimanually.

## [1126] ContactArt: Learning 3D Interaction Priors for Category-level Articulated Object and Hand Poses Estimation (3DV 2024, dataset, S1 S5)
Source: https://arxiv.org/html/2305.01618; confidence HIGH.
Field cannot yet: The field cannot yet estimate hand and articulated-object poses jointly for novel categories or small objects without category-specific priors and depth.
Stated limitations:
- Cannot generalize to novel categories because articulation priors are object-specific. [6 Conclusion, Limitation]
- Relies more on depth than visual texture. [6 Conclusion, Limitation]
- Simulator struggles with objects smaller than hands such as scissors. [6 Conclusion, Limitation]
- Collection fails by accidental touch, hand leaving bounds, or failed initialization; such sequences are re-collected. [3 Dataset collection]
Open problems listed:
- High annotation cost for real articulated objects.
- Sim2real gap from synthetic data.
- Accurate hand-object contact labels from images.
- Mutual occlusion between hands and articulated objects.
- HOI4D is egocentric-only and its labels are not accurate enough for contact.
Benchmark gaps:
- HOI4D articulated objects / 5deg5cm (%) average: Best 35.99; baselines 3.17-7.69.
- HOI4D articulated objects / rotation / translation error: Best average 5.51 deg / 6.68 cm.
- HOI4D hand pose / MPJPE / MPVPE (mm): Best 41.9 / 49.9; FrankMocap 64.3 / 71.6.
Restrictive assumptions: Category-specific priors; requires depth (partial point clouds).; Training data from simulator teleoperation where the hand is unoccluded.; Evaluated on 5 articulated categories.

## [1127] HMDO: Markerless Multi-view Hand Manipulation Capture with Deformable Objects (arXiv 2023, dataset, S1)
Source: https://arxiv.org/html/2301.07652; confidence HIGH.
Field cannot yet: Reconstruct hands manipulating deformable objects with large non-rigid deformation, especially without a dense multi-camera studio and per-object scanned templates.
Stated limitations:
- The dataset contains only small contact deformations; large deformations such as twisting or bending are absent. [6 Conclusion, Limitations and Future Work]
- The reconstruction method requires uniform object material; otherwise the deformation diffusion strategy may fail. [6 Conclusion, Limitations and Future Work]
- Prior fusion-based deformable reconstruction relies on extra depth cameras and slow motion, lacks explicit object models, and usually handles only a single hand-object pair. [1 Introduction]
Open problems listed:
- No datasets of hands interacting with deformable objects.
- Mutual occlusion makes the interaction area difficult to observe.
- Visual features of hand and object are entangled.
- Reconstructing deformation of the contact region is difficult.
- Fusion-based methods depend on depth, need slow motion, do not model objects explicitly and cannot give time-invariant topology.
- Template-based methods have difficulty with closely interacting hands and objects.
- Large deformations (twisting, bending) and non-uniform materials are not covered.
Benchmark gaps:
- HMDO (manually annotated frames) / mean hand joint error (mm): 14.75 mm (std 6.81) with 4 views; only 10-view setting reaches 5.58 mm.
- HMDO (2 annotated sequences, rigid frames) / object mask mIoU: Best initial-frame object pose reaches 86.91 mIoU; 5 iterations give only 58.36.
- HMDO / deformed object mIoU / intersection volume: All terms give 87.53 mIoU and 3.27 intersection volume; before deformation 78.54 and 15.10.
Restrictive assumptions: 10 hardware-synchronized high-speed industrial cameras (multi-view studio).; Pre-scanned, manually repaired watertight genus-0 template mesh per object.; Uniform object material and similar stuffing elasticity; no plastic deformation allowed during capture.; Subject-specific hand shape pre-optimized in the multi-view system; only pose optimized during tracking.; Per-object segmentation network trained on masks from depth thresholding and manual processing.; 2D hand keypoint model fine-tuned on manually corrected poses from the same rig.; High frame rate (up to 110 FPS) so that inter-frame motion is small and one optimization iteration suffices for non-initial frames.; Offline optimization (first-frame pose search about 82.70 time units for 500 samples x 20 iterations).

## [1128] POV-Surgery: A Dataset for Egocentric Hand and Tool Pose Estimation During Surgical Activities (MICCAI 2023, dataset, S1)
Source: https://arxiv.org/html/2307.10387; confidence HIGH.
Field cannot yet: Obtain accurate real-world 3D hand and instrument pose annotation in surgical egocentric settings, so real 3D evaluation is not available.
Stated limitations:
- Only three orthopedic instruments are covered. [2 Method]
- Some generated grasp poses remain unrealistic after refinement and need post-selection. [2.2 Hand-object manipulation sequence generation]
- Depth maps are clean; real sensor artifacts are left to external simulation. [2.4 Rendering and POV-Surgery dataset statistics]
- The real-life test set has only 2D hand ground truth, from manually selected frames with accurate multi-view predictions. [3 Experiment]
Open problems listed:
- Lack of egocentric hand-object datasets, especially surgical.
- Constant self-occlusion and mutual hand-object occlusion in egocentric view.
- Magnetic sensor datasets pollute RGB frames.
- Annotation pipelines for everyday objects do not transfer to the surgical domain gap.
- Bloody gloves defeat hand keypoint detectors.
- Small, featureless, reflective metallic tools give noisy incomplete RGB-D point clouds.
- Single-image datasets ignore temporal context crucial in surgical tasks.
- Prior synthetic surgical dataset lacks diversity (one glove, one instrument, low resolution).
Benchmark gaps:
- POV-Surgery test / MPJPE (mm), no fine-tuning: HandOccNet 95.19, METRO 77.46, SEMI 115.67; fine-tuning brings MPJPE to about 14-15 mm.
- POV-Surgery test / object control point error (px): Baseline after fine-tuning SEMI is 41.56 px.
- POV-Surgery test / 2D joint reprojection error (px), no fine-tuning: 64.70 to 95.11 px across methods.
Restrictive assumptions: Synthetic training data only; real evaluation is 2D only.; Known 3D CAD models of three instruments.; Right hand only (MANO right hand merged into SMPL-X).; Grasp key poses from GrabNet with manual template selection and interpolation between key poses.; Body motion captured with four synchronized ZED stereo cameras in simulated surgeries.; Single synthetic operating-room scene in training (one scanned scene held out for test).; Clean rendered depth without sensor noise.

## [1129] Efficient Annotation and Learning for 3D Hand Pose Estimation: A Survey (IJCV 2023, survey, S1 S3)
Source: https://arxiv.org/html/2206.02257; confidence HIGH.
Field cannot yet: Produce accurate, verifiable 3D hand annotations for diverse, natural hand-object activities outside static multi-camera labs.
Stated limitations:
- No established methodology exists for efficient annotation and learning from imperfect labels. [1 Introduction]
- Marker, depth and multi-view setups need controlled environments, limiting scenarios. [1 Introduction]
- Synthetic data does not model motion of the hand approaching the object. [4.2 Synthetic-model-based annotation]
- Computational annotation quality is hard to assess and depends on camera count, arrangement and 2D detection accuracy. [4.4 Computational annotation]
- Existing datasets cover narrow tasks and objects, often relying on pre-registered object models and simple pick-and-place. [6.2 Various types of activities]
- Models trained on existing datasets generalize poorly to other datasets. [6.4 Generalization and adaptation]
Open problems listed:
- Annotating 3D joints from a single RGB image is ill-posed.
- Hand-marker, mocap and glove setups are expensive and need calibration.
- Depth sensor noise, missing values, ghost shadows and range limits.
- Occlusion from articulation, viewpoint and grasped objects.
- Dataset bias toward the conditions imposed by the annotation method.
- Manual annotation: labor intensive, cannot handle occlusion.
- Synthetic: sim-to-real gap, hard to simulate motion, especially hand approaching object.
- Hand markers: change visual modality and prevent natural motion.
- Computational: lacks diversity, hard to evaluate quality, needs multi-camera setups.
- Label-space domain gap not assumed by typical adversarial domain adaptation.
- Static multi-camera setups unsuitable for dynamic user behavior; first-person benchmarks limited by occlusion, blur and narrow FOV.
- Narrow task and object variation; reliance on known object models; simple actions.
- Human-in-the-loop checking is a bottleneck; active learning restricted to triangulation.
- Poor cross-dataset generalization; indoor-to-outdoor transfer where multi-camera rigs are unavailable.
Benchmark gaps:
- Assembly101 / AssemblyHands / keypoint error: Original Assembly101 annotations had error about 85% higher than the 4.20 mm feature-level triangulation result, showing sparse-camera annotation weakness.
- First-person benchmarks (Table 1) / variety: Existing first-person benchmarks have very limited variety due to heavy occlusion, motion blur and narrow field of view.
Restrictive assumptions: Reviewed hand-object datasets (HO-3D, DexYCB, ObMan) use pre-registered 3D object models such as YCB.; Multi-camera studios are static and not portable, so backgrounds and objects are limited.; Hand-marker annotation needs special sensors and user-specific bone lengths measured beforehand.; Triangulation works well only with many cameras (30+).

## [1130] AnyHand: A Large-Scale Synthetic Dataset for RGB(-D) Hand Pose Estimation (arXiv 2026, dataset, S1)
Source: https://arxiv.org/html/2603.25726; confidence HIGH.
Field cannot yet: Generate physically consistent full-scene RGB-D hand-object training data at scale that can replace, not just complement, real captured data.
Stated limitations:
- Poses come from a learned prior trained on finite real data; implausible poses can pass the biomechanical filter. [Appendix F Limitations]
- Hands are composited onto 2D backgrounds with estimated depth rather than placed in full 3D scenes, so boundary depth may be inconsistent. [Appendix F Limitations]
- Aligned depth is not perfect ground truth because of intrinsics mismatch and noisy estimated background depth. [3.1 Dataset creation]
- Synthetic data alone is insufficient; it must complement real data. [4.3 Ablations]
- The dataset integrates existing tools rather than new generation methods. [Appendix F Limitations]
Open problems listed:
- Real captured datasets are constrained by capture setup scale and have noisy 3D labels under heavy occlusion.
- Large datasets with well-aligned depth and reliable 3D labels remain scarce for RGB-D learning.
- Synthetic-to-real gap depends on forearm context, interaction realism, occlusion and rendering variation.
- Full 3D scene rendering at scale is too costly in assets and compute.
Benchmark gaps:
- HO-3D v2 / PA-MPJPE (mm): Baselines remain at 7.5-7.7 mm versus 5.5-6.0 mm on FreiHAND; AnyHand reduces it only by about 2-3%.
- AnyHand-Single test (EnvMap) / MPJPE (mm, unaligned) / F@5: Even with AnyHand training, MPJPE 14.29-14.98 mm and pre-alignment F@5 about 0.14.
- HO-3D v2 (RGB-D) / STA-MPJPE (cm): Prior RGB-D Keypoint-Fusion 1.87 cm; AnyHandNet-D 1.09 cm.
Restrictive assumptions: Single-image, single-hand estimation (no two-hand or temporal setting in the evaluated models).; Hand-object branch inherits GraspXL physics-simulated grasps rather than real manipulation.; Assumes tightly cropped hand regions in downstream pipelines.; Camera-to-hand distance kept within set bounds and hand kept well framed to avoid truncation.; RGB-D evaluation only on HO-3D v2; RGB-D baselines trained dataset-specifically.; Training needs 8 H100 GPUs for 5-7 days per run.

## [1131] HRDexDB: A Large-Scale Dataset of Dexterous Human and Robotic Hand Grasps (arXiv 2026, dataset, S1 S6)
Source: https://arxiv.org/html/2604.14944; confidence HIGH.
Field cannot yet: Track hands and objects robustly under dexterous-grasp occlusion without dense multi-camera rigs and CAD models, or define functional correspondence between human and robot grasps.
Stated limitations:
- Tactile data exist only for robot hands, with varying sensor specifications that complicate unified analysis. [6 Limitations]
- Human and robot grasps are paired only semantically; functional equivalence across morphologies is undefined. [6 Limitations]
- Severe occlusion in dexterous manipulation makes markerless hand reconstruction and object tracking difficult. [1 Introduction]
Open problems listed:
- How robots should learn from human manipulation and transfer grasp strategies across embodiments remains open.
- Defining functionally equivalent motions across hand morphologies.
- Tactile heterogeneity across robot hands.
- Severe occlusion in dexterous manipulation for markerless capture.
- Existing human-robot datasets are gripper-based, task-level aligned, or occlusion-vulnerable (DexWild).
Benchmark gaps:
- HRDexDB / object ADD (cm), robot grasp: FoundPose 8.74 cm, GigaPose 13.80 cm, PicoPose 8.39 cm; best refined 4.40 cm.
- HRDexDB / AR MSSD (%): Drops by 2.4 to 10.8 points from human to robot grasps; FoundPose 33.30% under robot grasp.
- HRDexDB / cross-embodiment retrieval R@1: Inspire to Allegro 8.18%, Human to Allegro 24.24%.
- HRDexDB vs FreiHAND / PA-MPVPE (mm): WiLoR 6.09 vs 5.27; FrankMocap 12.48.
Restrictive assumptions: 21 calibrated exocentric RGB cameras plus 2 egocentric cameras on a fixed three-sided frame.; Scanned object CAD models for model-based 6D tracking (FoundationPose).; Grasping trials, not long or bimanual manipulation.; Robot data via teleoperation with Xsens suit and MANUS gloves.; Subject-specific hand shape calibration from silhouettes; HaMeR 2D keypoints triangulated.

## [1134] InterAct: Advancing Large-Scale Versatile 3D Human-Object Interaction Generation (CVPR 2025, dataset, S2)
Source: https://arxiv.org/html/2509.09555; confidence HIGH.
Field cannot yet: Capture or curate artifact-free whole-body human-object interaction data, including accurate hands, at a scale covering in-the-wild objects.
Stated limitations:
- Despite 217 objects, the dataset does not cover in-the-wild object diversity; broader unseen-object generalization needs more data. [E Discussion, Limitations]
- Correction fails on severe source noise; large human-object gaps are classified as no contact and stay uncorrected. [E Discussion, Limitations]
- Unified hyper-parameters across all data mean some artifacts remain. [E Discussion, Limitations]
Open problems listed:
- Limited and inconsistent HOI datasets (representations, object types, coordinate systems, annotations).
- Coarse and incomplete text annotations.
- Prevalent MoCap artifacts: penetration, floating contacts, inaccurate hand poses, jitter.
- HOI generation methods suffer floating contacts and interpenetration due to data shortage.
- Full-body interaction methods have narrow action repertoires and depend on static objects.
- Physics-based RL methods produce rigid interaction patterns from limited datasets.
- HOI evaluation feature extractors are trained on very limited data, degrading evaluation.
- Scale insufficient for in-the-wild object diversity.
Benchmark gaps:
- InterAct interaction prediction / Global MPMPE (m) / Rot.Err.: Best 0.091 m global MPMPE and 0.264 rotation error with largest model.
- InterAct imitation (PhysHOI, 4 sequences) / success rate: 84.4% raw versus 90.7% corrected.
Restrictive assumptions: Built from existing MoCap HOI datasets (GRAB, BEHAVE, InterCap, Chairs, HODome, OMOMO, IMHD); no new capture.; Single human with rigid or dynamic objects; known object meshes.; Marker-based representation consistent across SMPL-H and SMPL-X.; Text annotations augmented by a language model.; Generation task, not perception from sensors.

## [1150] BEHAVE: Dataset and Method for Tracking Human Object Interactions (CVPR 2022, dataset, S2)
Source: https://arxiv.org/html/2204.06950 and https://openaccess.thecvf.com/content/CVPR2022/supplemental/Bhatnagar_BEHAVE_Dataset_and_CVPR_2022_supplemental.pdf; confidence HIGH.
Field cannot yet: Track full-body human, object and contact accurately from sparse consumer RGB-D, including hand-level grasps, symmetric and deformable objects.
Stated limitations:
- Network sometimes predicts wrong orientation for symmetric objects such as a square suitcase. [Supplementary 7 Limitations and Future Works]
- Kinect noise prevents modeling fine hand interactions, causing interpenetration and unrealistic grasps. [Supplementary 7 Limitations and Future Works]
- Objects are assumed rigid; deformable parts like backpack straps are not registered. [Supplementary 7 Limitations and Future Works]
- Contact prediction has no significant quantitative effect, only qualitative. [Table 3 caption]
Open problems listed:
- Tracking human-object interaction from multi-view RGB without depth, and from a single camera.
- Joint 3D human and object reconstruction from a single RGB image, with no prior benchmark.
- Pose and shape estimation under heavy occlusion by the interacting object.
- Depth is noisy and incomplete; mutual occlusion during interaction.
- Contacts are small image regions close to the resolution limit.
- Symmetric object orientation ambiguity.
- Fine-grained hand interactions from noisy consumer depth.
- Non-rigid objects with rigid templates.
Benchmark gaps:
- BEHAVE / object v2v (cm): Proposed method still 21.20 cm object error; PHOSA 34.73 cm.
- BEHAVE / SMPL v2v (cm): Proposed 4.99 cm; PHOSA 13.73 cm; LoopReg 9.12 cm.
- BEHAVE annotation / Chamfer error of pseudo-GT (cm): SMPL fits 1.80 cm and object fits 2.42 cm from Kinect point cloud.
Restrictive assumptions: Four calibrated, synchronized Azure Kinects at corners of a square volume (the method is multi-view RGB-D, not single camera).; Pre-scanned rigid object templates; only rotation and translation estimated.; Segmented human and object point clouds as input.; Pseudo ground truth from instance-specific fitting with manual mask correction and AMT keypoints; subject shape from 3D scans.; Contacts defined by a 2 cm distance threshold on pseudo-GT.; Single person, 20 objects, indoor locations; per-frame registration.

## [1151] COUCH: Towards Controllable Human-Chair Interactions (ECCV 2022, dataset, S2)
Source: https://arxiv.org/html/2205.00541; confidence HIGH.
Field cannot yet: Synthesize or capture contact-accurate whole-body interactions with moving objects across body shapes and object geometries.
Stated limitations:
- Synthesized motion can slightly intersect the chair. [Appendix 4 Limitations and Future Direction]
- Generalizing to more chair shapes needs better scene encoding without overfitting. [Appendix 4 Limitations and Future Direction]
- Subject-variant, body-shape-conditioned synthesis is not tackled. [Appendix 4 Limitations and Future Direction]
- Only static objects; non-static objects such as lifting a box or opening a door are left for future work. [Appendix 4 Limitations and Future Direction]
- Kinect-fitted motion is jittery under occlusion and drastic movement; IMUs are smooth but miss contacts. [Appendix 1.2 Data Processing]
Open problems listed:
- Fine-grained contact-conditioned motion synthesis is largely unexplored.
- Datasets are hands-only, static-pose, or low motion variation.
- Generating dynamic human-scene interaction is less explored.
- Body-shape-dependent interaction synthesis.
- Non-static objects (box lifting, door opening).
Benchmark gaps:
- COUCH test (120 sequences) / average contact error (ACE): COUCH 4.73 versus 10.52 to 12.09 for NSM/SAMP variants.
- COUCH dataset / fitting Chamfer error: SMPL 3.12 cm and chair 1.70 cm to Kinect point clouds.
- COUCH test / APD diversity: Sit 6.02 versus ground truth 6.30; contact APD 11.82 cm vs 14.07 cm.
Restrictive assumptions: Static chairs: chair 6D pose averaged over each capture session.; 17 XSens IMUs combined with multiple Kinects; scanned chair meshes.; Subject-specific models trained per subject.; Chairs and a sofa only; contacts for two hands.; Four indoor scenes, six subjects.

## [1152] Full-Body Articulated Human-Object Interaction (ICCV 2023, dataset, S2)
Source: https://arxiv.org/html/2212.10621; confidence HIGH.
Field cannot yet: The field cannot yet estimate articulated object pose and shape during whole-body interaction without a known object structure, nor handle symmetric parts or non-interacting frames.
Stated limitations:
- The SMPL-X body model used for annotation has no clothing, so 3D annotations misalign with images and pixel-aligned features may be compromised. [7 Conclusion, Limitations]
- Part orientation is ambiguous for rotation-symmetric parts (round seats, stool bases); handling it would need per-object symmetry classification. [5.2 Failure cases]
- Performance drops when there is no interaction (human far from the object), since the method relies on the interaction prior. [5.2 Failure cases]
- Captured data still contain unrealistic contacts and penetrations because of limited sensor count and limb-length discrepancies, requiring post-hoc penetration removal. [3.3 Post-processing]
Open problems listed:
- Lack of comprehensive full-body articulated HOI datasets; existing ones assume rigid objects or specific body parts
- Diverse kinematic structures within the same object category; prevailing methods assume uniform structures
- Complex interactions with occlusion and dense contact defeat point-cloud template matching; slight errors yield implausible contacts
- Articulated object pose estimation in full-body interaction remains largely unaddressed
- Clothing is not modelled by the parametric body, causing annotation-image misalignment
Benchmark gaps:
- CHAIRS test / part rotation error (deg): Best method still has 19.35 deg mean rotation error and 66.23 mm translation error with known object structure
- CHAIRS test / Chamfer distance (mm) / IoU (%): Ours w/o opt. (unknown object) CD 160.2 mm, IoU 11.03%; w/ opt. CD 72.30 mm, IoU 21.57%
- Internet images / qualitative only: In-the-wild generalization shown only qualitatively on a limited set of images
Restrictive assumptions: Best setting (w/ opt.) requires the object CAD model and URDF kinematic structure; Requires an estimated SMPL-X human pose as input (off-the-shelf estimator, PARE fine-tuned); Single person interacting with one sittable object; Data captured only in a controlled 5 m x 4 m lab with four front-facing Azure Kinects plus inertial-optical hybrid mocap with trackers on every movable part; Single image input, no temporal reasoning

## [1153] NeuralDome: A Neural Modeling Pipeline on Multi-View Human-Object Interactions (CVPR 2023, dataset, S2)
Source: https://arxiv.org/html/2212.07626; confidence HIGH.
Field cannot yet: The field cannot yet reconstruct and render human-object interaction faithfully from sparse views without markers and accurate object poses.
Stated limitations:
- Only single-person interaction with objects; extending to multi-person or crowd scenes is non-trivial. [5.3 Limitations]
- Holistic 3D scene reconstruction is not covered; joint modeling of humans, objects and scene is left to future work. [5.3 Limitations]
- Data were collected under fixed illumination with little background variance, limiting generalization to other environments. [5.3 Limitations]
- Marker-based object tracking retains bias from camera alignment error, requiring a silhouette refinement term. [C.2 Joint optimization for human-object tracking]
- Tracking components could only be evaluated qualitatively because no tracking ground truth exists. [E More Experiment Results]
- Even when trained on HODome, PIFu leaves much room for improvement in human-object geometry reconstruction. [5.2 Task and benchmark]
Open problems listed:
- Interaction capturing for monocular and multi-view settings
- Joint human-object geometry reconstruction; existing data cannot benchmark or train it
- Object-occluded human pose and shape estimation
- Neural rendering in HOI: sparse views, no accurate object poses
- Generalizable neural rendering under inevitable occlusion
- Neural avatars with object-aware deformation
- Multi-person and crowd interaction
- Joint human-object-scene modeling
- Generalization beyond fixed illumination and backgrounds
Benchmark gaps:
- HODome / Object Chamfer (separated evaluation): All monocular capture methods have large object errors: PHOSA 77.62, CHORE 86.58, fit-to-input 86.66 (units per Tab. 3)
- HODome / PSNR (sparse-view rendering): Best sparse-view HOI rendering only about 23.3 dB PSNR (NeuRay 23.34, NeuralHOIFVV 23.10)
- HODome / P2S / Chamfer (geometry): Monocular PIFu trained on HODome P2S 14.653, Chamfer 14.483 versus 3.376 / 4.901 for 6-view
Restrictive assumptions: 76 synchronized 4K RGB cameras in a dome plus 16 OptiTrack mocap cameras; Objects treated as rigid with a pre-scanned template; At least 4 hemispherical markers glued on each object to track its pose; Single person, single object, fixed illumination, static calibrated cameras; Manual start-frame labelling for RGB-mocap synchronization and annotated correspondences for calibration; Offline per-sequence neural optimization

## [1154] Object Motion Guided Human Motion Synthesis (SIGGRAPH Asia 2023, dataset, S2)
Source: https://arxiv.org/html/2309.16237; confidence HIGH.
Field cannot yet: The field cannot yet synthesize or recover physically plausible full-body manipulation with dexterous hands and intermittent contact from object motion alone.
Stated limitations:
- The dataset does not accurately represent dexterous hand movements, often yielding implausible hand motions. [7 Conclusion, Limitations]
- Contact constraints cannot handle intermittent contact; hands fixed on the object cause penetrating, implausible motion. [7 Conclusion, Limitations]
- The method is purely kinematic and produces artifacts such as penetration; physics components are suggested. [7 Conclusion, Limitations]
- Single forward pass without optimization or post-processing can produce penetration; ground truth preferred in 69% of comparisons. [5.2 Human Perceptual Study]
Open problems listed:
- Scarcity of full-body interaction datasets with moving objects
- Dexterous hand motion during full-body manipulation
- Intermittent contact and contact-state prediction for long-term manipulation
- Physical plausibility of kinematic generation
Benchmark gaps:
- FullBodyManip (OMOMO), unseen objects / MPJPE / contact F1: OMOMO MPJPE 13.06 cm and F1 0.61 on unseen objects; GT hands reduce MPJPE to 7.73
- FullBodyManip (OMOMO) / human perceptual study: Only 31% preferred OMOMO over ground truth (upper bound 50%)
Restrictive assumptions: Requires full object motion trajectory and object geometry (reconstructed mesh / SDF) as input; Training data from 12-camera Vicon mocap with 5 markers per object; Objects rigid, large-sized, 15 categories; Continuous hand-object contact assumed by the contact constraint; Single person, offline sequence-level generation; Smartphone application needs a phone rigidly mounted on the object and a pre-reconstructed object mesh

## [1155] DECO: Dense Estimation of 3D Human-Scene Contact In The Wild (ICCV 2023, dataset, S2)
Source: https://arxiv.org/html/2309.15273; confidence HIGH.
Field cannot yet: The field cannot yet infer accurate dense 3D human-object contact out of domain, nor derive it reliably from reconstructed human and object geometry.
Stated limitations:
- DECO reasons about contact for a single person with scene and objects only; human-human, human-animal and self-contact are left for extension. [7 Conclusion, Future work]
- Most methods, DECO included, struggle on out-of-domain BEHAVE, partly because BEHAVE annotates only single-object contact. [5.1 3D Contact Estimation]
- DAMON has no ground-truth 3D meshes; pseudo ground-truth bodies come from CLIFF. [5 Experiments]
- Geometry-based contact from current 3D human and object reconstruction is very poor, so contact is inferred directly instead. [5.3 Inferred versus geometric contact]
Open problems listed:
- 3D contact datasets limited in interaction complexity, size and paired HOI images
- Synthetic contact data has a domain gap to real images
- Contact areas are inherently occluded in images
- Extending dense contact to human-human, human-animal and self-contact
- Using language captions to scale contact supervision
Benchmark gaps:
- BEHAVE (out of domain) / F1 / geodesic error (cm): DECO F1 0.18, geo 46.33 cm; BSTRO F1 0.04, geo 50.45 cm
- DAMON test / F1 / geodesic error (cm): Best F1 only 0.55 with geodesic error about 21 cm
- DAMON subsets (PHOSA / CHORE objects) / F1: Geometric contact from CHORE 0.08 and PHOSA 0.18 vs DECO 0.48 / 0.60
Restrictive assumptions: Single RGB image, single person (multi-person images filtered); Contact on SMPL body vertices only; object geometry and pose not recovered; Pseudo ground truth from crowd-sourced painting and CLIFF meshes; Body-part and scene segmentation pseudo-labels from Mask2Former

## [1156] RHOBIN Challenge: Reconstruction of Human Object Interaction (arXiv 2024, benchmark, S2)
Source: https://arxiv.org/html/2401.04143; confidence HIGH.
Field cannot yet: The field cannot yet jointly reconstruct humans and unknown objects from monocular video robustly under long-term occlusion, fast motion, or multiple people and objects.
Stated limitations:
- Joint reconstruction remains challenging and requires further innovation in accuracy and speed. [1 Introduction]
- Current approaches use single images; video methods help but struggle with long-term occlusion and fast motion. [4 Future Directions]
- Approaches assume a known category-level object template and do not generalize to new object geometry. [4 Future Directions]
- Challenge is limited to one person interacting with one object. [4 Future Directions]
- Joint reconstruction still needs an optimization layer beyond direct regression. [1 Introduction]
Open problems listed:
- Extend from single images to video; handle long-term occlusion and fast motion with motion priors
- Remove the known category-level template assumption; generalize to new object geometry
- Joint template-free human-object reconstruction, lacking data
- Build object templates on the fly from video in full-body interaction
- Full-body interaction from monocular RGB video (only one RGB-D video method handles heavy occlusion)
- Capture and reconstruct human and object appearance during interaction
- Multi-person and multi-object interaction datasets and methods
- Improve speed and accuracy of joint reconstruction
Benchmark gaps:
- BEHAVE / Object 6DoF AR-all: Winner G2DR reaches 0.6 (from CHORE 0.3)
- BEHAVE / joint reconstruction SMPL / object error (mm): Winner KHOR 45.1 mm SMPL and 87.2 mm object, versus human-only MPJPE-PA 18.4
Restrictive assumptions: Single RGB image input; Known category-level object template; BEHAVE pseudo ground truth from 4 RGB-D cameras; Single person, single object

## [1158] A Survey on Human Interaction Motion Generation (arXiv 2025, survey, S2)
Source: https://arxiv.org/html/2503.12763; confidence HIGH.
Field cannot yet: The field cannot yet generate physically plausible, controllable interaction motion at real-world diversity because interaction data are scarce and costly to capture.
Stated limitations:
- Interaction data are costly; datasets from controlled settings do not cover real-world interaction diversity. [7 Conclusion and Outlook, Data]
- Physics-simulator methods are action-specific, generalize poorly and fit poorly with diffusion models. [7 Conclusion and Outlook, Physical Plausibility]
- Single-person editing and control techniques are not yet adapted to interaction scenarios. [7 Conclusion and Outlook, Editing and Controllability]
Open problems listed:
- Data: high cost of capturing interaction data; controlled-environment datasets miss real-world diversity
- Physical plausibility: gravity, forces, texture responses; simulator methods action-specific and incompatible with diffusion
- Representation: interaction-aware features of motion, objects and scenes; unordered points and intractable scene scale
- Editing and controllability of interaction generation
- Stochastic interaction must remain spatially and temporally coherent with intentions
- Environmental awareness: scene layouts, affordances, physical constraints, penetration

## [1159] 3D Human Interaction Generation: A Survey (arXiv 2025, survey, S2)
Source: https://arxiv.org/html/2503.13120; confidence HIGH.
Field cannot yet: The field cannot yet capture or generate large-scale, physically plausible interactions with multiple people, deformable objects and fine finger motion.
Stated limitations:
- Few approachable datasets limit interactive entities to a few categories, and datasets lack natural-language intent annotations. [I Introduction]
- Data-driven methods ignore physical properties and produce sliding, penetration and floating. [I Introduction]
- Markerless capture is less robust to lighting and occlusion; marker systems need controlled environments. [III-B Motion Capture]
- Hybrid optical-inertial mocap still struggles with cross-modal alignment and synchronization; inertial mocap drifts. [III-B Motion Capture]
Open problems listed:
- Large-scale real-world 3D interaction data is resource-intensive to capture with human and entity simultaneously
- Lack of natural-language intent annotations
- Physical plausibility and contact accuracy (sliding, penetration, floating)
- Controllability under diverse conditioning signals
- Multi-person and multi-object interactions requiring spatial-temporal coordination
- Non-rigid, articulated and deformable objects (cloth, ropes, soft tissue) underexplored
- Face and finger motion requiring high-resolution capture
- Unified human-scene-object-human interaction in open environments
- Markerless capture robustness to lighting and occlusion
- Alignment and synchronization in hybrid mocap; IMU drift

## [1160] RoboTwin: Dual-Arm Robot Benchmark with Generative Digital Twins (CVPR 2025, benchmark, S3 S6)
Source: https://arxiv.org/html/2504.13059; confidence HIGH.
Field cannot yet: The field cannot yet learn reliable tightly coordinated bimanual manipulation policies, even with large generated simulation data.
Stated limitations:
- Imitation policies perform poorly on tasks requiring complex bimanual coordination, below 15% on Dual Shoes Place. [5.2 Experimental Results]
- Adding RGB to point clouds helps inconsistently; better RGB-point cloud fusion is needed. [5.2 Experimental Results]
- Real dual-arm bottle rearrangement stays suboptimal even with simulation data. [5.3 Real World Experiment]
- Code generation needs minimal human oversight for complex cases. [3.3 Expert Data Generation]
Open problems listed:
- Scarcity of diverse demonstrations and real-world-aligned benchmarks for dual-arm manipulation
- Teleoperation costly; algorithmic generators task-specific
- MimicGen-style generators limited to fixed scenarios and fixed 3D objects
- Existing benchmarks single-arm or separated-arm
- Imitation learning weak at tight dual-arm coordination
- RGB and point cloud fusion inconsistent
- Sim-to-real gap for dual-arm tasks with diverse initial states
Benchmark gaps:
- RoboTwin sim (14 tasks) / success rate (%): Dual Shoes Place max 12.0% (DP3 XYZ, 100 demos)
- RoboTwin sim / success rate (%): Mug Hanging Easy/Hard best 15.3%
- RoboTwin real, dual-arm / success rate: Average 62% with 300 sim + 20 real; Dual bottle Pick (Hard) 11/50
Restrictive assumptions: Simulation in ManiSkill3/SAPIEN with assets generated from single images by a commercial 3D model (Rodin); Physics parameters assigned by GPT-4V material classification; Per-class manual spatial annotations transferred by feature matching; Real hardware matched exactly to simulation (COBOT Magic, RealSense D435); Rigid tabletop objects; random initial poses within bounds

## [1161] PianoMotion10M: Dataset and Benchmark for Hand Motion Generation in Piano Performance (ICLR 2025, dataset, S3)
Source: https://arxiv.org/html/2406.09326; confidence HIGH.
Field cannot yet: The field cannot yet produce keyboard-registered, accurate 3D two-hand motion for fast piano playing from monocular video or audio without pseudo-labels.
Stated limitations:
- Dataset comes from only 14 subjects and is imbalanced across performers. [Appendix D Limitation and Future Work]
- Baseline produces incorrect hand transitions in extreme, out-of-distribution performances such as very fast music. [Appendix D Limitation and Future Work]
- Piano key positions are not spatially aligned across videos, so hand poses are not registered to the keyboard. [Appendix D Limitation and Future Work]
- Not all videos meet data-quality standards; variance in piano tone across recordings may affect baseline performance. [Appendix D Limitation and Future Work]
- Hand pose labels are pseudo-labels from MediaPipe plus HaMeR, which give inferior results under rapid motion and blur, requiring outlier filtering and interpolation. [3.2 Data Annotations]
Open problems listed:
- Dataset imbalance across only 14 subjects.
- Out-of-distribution performance on rapid, multi-hand or non-human piano audio.
- Missing spatial alignment of piano key positions across videos.
- Variable data quality and piano tone across recordings.
- Need for more diverse sources beyond Bilibili.
Benchmark gaps:
- PianoMotion10M validation / FID (two-hand motion quality): Best baseline (Our-Large HuBERT TF) reaches FID 3.281 versus 4.645 for re-implemented EmoTalk; no ground-truth-level fidelity reported.
- PianoMotion10M validation / FGD / WGD per hand: Best left-hand FGD 0.372 and right-hand FGD 0.351; gains over baselines are modest and WGD stays around 0.21-0.24 for all methods.
Restrictive assumptions: Single performer only; videos with multiple players excluded.; Bird's-eye (top-down) camera view chosen to minimise hand occlusion; videos with hands obstructed in more than 20% of frames removed.; Monocular RGB video with pseudo-ground-truth from HaMeR, not mocap or multi-view ground truth.; Pure piano audio without vocals or other instruments.; No piano/keyboard geometry registration; no object model.

## [1163] BiGym: A Demo-Driven Mobile Bi-Manual Manipulation Benchmark (CoRL 2024, benchmark, S3 S6)
Source: https://arxiv.org/html/2407.07788; confidence HIGH.
Field cannot yet: Current imitation and demo-driven RL policies cannot reliably solve precise or long-horizon mobile bimanual manipulation from noisy human demonstrations.
Stated limitations:
- All baseline algorithms fail on long-horizon tasks; model-free baselines cannot do task-level reasoning. [Appendix C.2 Results and Discussions]
- Mobile manipulation of articulated or rigid objects is hard because grasp poses are hard to measure while moving and POMDP belief estimation is difficult. [Appendix C.2 Results and Discussions]
- Demo-driven RL fails on nearly all tasks, succeeding only on simple tasks with little object interaction. [Appendix C.2 Results and Discussions]
- 3D next-best-pose agents are not benchmarked because their keyframe extraction applies only to single fixed arms. [4 Experiments]
- Baselines are reported with common hyperparameters, not tuned per task. [4 Experiments]
Open problems listed:
- Partial observability: learning belief over states from history in a POMDP.
- Complex, highly multi-modal task space from dual arms plus mobility.
- Long task horizon with sparse rewards requiring task and motion planning.
- Learning from realistic noisy multi-modal human demonstrations.
- Network architectures for multi-modal noisy demonstrations.
- Belief estimation for mobile manipulation POMDPs.
- Inter-arm collaboration modes on mobile platforms.
- Whole-body motion planning in clutter.
- Combined locomotion and manipulation control for humanoids.
Benchmark gaps:
- BiGym 40 tasks / Average success rate (%): Best method ACT averages 46.3%; BC 18.0, DiffPolicy 20.8, DrQV2 13.9, AWAC 13.0, IQL 12.4, CQN 10.5.
- BiGym stack_blocks / Success rate (%): 0.0% for all IL and RL methods.
- BiGym long-horizon tasks / Success rate (%): All algorithms fail on dishwasher_unload_cups_long and put_cups.
Restrictive assumptions: Simulation only (Unitree H1 in simulation); no real-robot evaluation.; Demonstrations from VR teleoperation of the simulated robot, 50 per task.; Sparse rewards only.; Bi-manual mode uses a predefined lower-body controller.

## [1165] A Multimodal Handover Failure Detection Dataset and Baselines (ICRA 2024, dataset, S3 S6)
Source: https://arxiv.org/html/2402.18319; confidence HIGH.
Field cannot yet: The field cannot yet detect human-caused handover failures online and reliably across robots from natural, non-acted interactions.
Stated limitations:
- Failures are acted on instruction and may not represent natural handovers or failures. [VI Limitations]
- Baselines classify the outcome only after the complete trial, not online. [VI Limitations]
- Human action boundary annotations by a single annotator may be ambiguous. [III-E Annotations (footnote)]
- Using predicted human actions to interpret failures needs further investigation. [V-D Summary]
- Failure datasets are rare and hard to collect; natural failures are rare and some could cause harm. [I Introduction]
Open problems listed:
- Capturing naturally occurring (not acted) handover failures.
- Online, early failure detection during the trial rather than after it.
- Interpreting failure reasons from predicted human actions.
- Generalization to new robot platforms (viewpoint, appearance, motion).
- Generating large-scale realistic simulated failure data with full simulated humans.
- Collecting failure data is hard, rare and potentially unsafe.
Benchmark gaps:
- HFD / Outcome classification accuracy (%): Best model MSTCN-A with video+F-T+gripper reaches 71.4 +/- 1.8%; video-only I3D 64.8%.
- HFD / Human action segmentation F1@50: Best F1@50 is 57.1 (MSTCN-A multimodal); video-only 51.1.
- HFD cross-robot / Accuracy (%): All train-on-one-robot results fall below full-data training; K-to-T MSTCN-B 44.7%.
Restrictive assumptions: Failures induced by instruction rather than occurring naturally.; 17 participants, all students familiar with robots.; Two specific robots (Toyota HSR, Kinova Gen3) with force-torque sensing.; Robot actions assumed known from joint states or state machine.; Offline classification over complete trials.

## [1170] AssemblyHands-X: Modeling 3D Hand-Body Coordination for Understanding Bimanual Human Activities (ICCV Workshops (HANDS 2025 extended abstract) 2025, benchmark, S3 S2 S4)
Source: https://arxiv.org/html/2509.23888; confidence HIGH.
Field cannot yet: The field cannot yet recover accurate joint 3D hand-body pose from a single view during bimanual activity at the quality multi-view triangulation provides.
Stated limitations:
- Body pose estimation during bimanual activity faces body truncation from limited camera viewpoints, requiring a dedicated triangulation pipeline. [2.1 Overview]
- Single-view hand-body estimators give noisier poses and lower action recognition accuracy than the 8-view annotations. [3.3 Effect of 3D pose annotation quality]
- Prior marker-based mocap introduces visual artifacts that limit generalization to natural markerless videos. [1 Introduction]
Open problems listed:
- Lack of datasets with kinematic-level annotations for both hands and body in bimanual activities.
- Marker-based capture artifacts limit generalization to markerless video.
- Body truncation under limited viewpoints during bimanual tasks.
- Single-view hand-body estimators remain noisy relative to multi-view annotation.
Benchmark gaps:
- AssemblyHands-X / Action recognition accuracy (%): Best model FreqMixFormer with hand+body pose reaches 78.7% on six verbs; body-only 57.5%.
- AssemblyHands-X / PA-MPJPE (mm) vs multi-view annotation: Single-view SMPLer-X: 43.78 mm all, 15.43 mm hand; with HaMeR hands 45.47 mm all, 10.62 mm hand.
Restrictive assumptions: Synchronized, calibrated 8-view static camera rig (Assembly101) for annotation.; Only upper body and hands annotated; no object pose.; Only six coarse verb classes evaluated.; Pose sequences fixed-length padded; video baseline from a single view (View 3).

## [1176] RoboTwin 2.0: A Scalable Data Generator and Benchmark with Strong Domain Randomization for Robust Bimanual Robotic Manipulation (arXiv 2025, benchmark, S3 S6)
Source: https://arxiv.org/html/2506.18088; confidence HIGH.
Field cannot yet: Bimanual policies cannot yet stay robust under realistic visual domain shift without perfect simulated perception.
Stated limitations:
- Policies lose much success from clean to randomized settings; robustness under domain shift remains a key challenge. [4.5 RoboTwin 2.0 Benchmark]
- DP3's strong few-shot results partly rely on perfect point clouds and clean segmentation available only in simulation. [4.5 RoboTwin 2.0 Benchmark]
- VLM observer has low accuracy at detecting failures and localizing failure steps. [G.4 Multimodal Observation and Error Localization]
- VLM observer hallucinates success, misses subtle orientation errors, and cannot diagnose invisible failure causes. [G.4 Failure Modes]
- Future work is needed on real-world deployment and multi-object task complexity. [6 Conclusion]
Open problems listed:
- Robustness of policies under domain shift (clutter, lighting, texture, height).
- Limited diversity in VLA pretraining data.
- Reliable automatic failure detection and attribution in generated trajectories.
- Sim-to-real transfer; real-world deployment.
- Multi-object task complexity.
- Cross-embodiment transfer of task-specific policies.
Benchmark gaps:
- RoboTwin 2.0 benchmark (50 tasks, Aloha AgileX) / Average success rate Easy/Hard (%): RDT 34.5/13.7, Pi0 46.4/16.3, ACT 29.7/1.7, DP 28.0/0.6, DP3 55.2/5.0.
- Code generation (10 tasks) / ASR: Best configuration R2.0 + MM FB reaches 71.3% average success; vanilla 62.1%.
- Real world (4 tasks, RDT) / Success rate (%): Unseen cluttered background remains low; e.g., averages reported around 9.0-14.0% in cluttered or unseen settings for some training configurations.
Restrictive assumptions: Simulation with annotated object asset library (731 objects with manipulation labels) and known object models.; Perfect point clouds and segmentation available in simulation.; Expert trajectories generated by LLM-written code, not human demonstrations.; Parallel-gripper dual-arm robots; real evaluation on one platform (COBOT-Magic) with four tasks.

## [1180] EgoEMG: A Multimodal Egocentric Dataset with Bilateral EMG and Vision for Hand Pose Estimation (arXiv 2026, dataset, S3 S4)
Source: https://arxiv.org/html/2605.05712; confidence HIGH.
Field cannot yet: The field cannot yet estimate hand pose robustly across unseen users or during object contact by fusing EMG with vision.
Stated limitations:
- 41 participants is still limited for modeling inter-subject EMG variability. [Limitations and future work]
- Vision benchmark limited to single-frame models. [Limitations and future work]
- No rich hand-object interaction with instrumented or annotated objects. [Limitations and future work]
- Fusion baselines are simple and only tested with lightweight generic visual branches; WiLoR alone beats them. [Limitations and future work]
- Cross-user generalization remains the central challenge; larger models do not close it. [5.1 EMG Baseline Results]
Open problems listed:
- Inter-subject EMG variability and cross-user generalization.
- Temporal, multi-view and RGB-D vision baselines.
- Hand-object interaction with contact-induced occlusion and pose ambiguity.
- Whether EMG complements strong specialized vision models.
- More expressive fusion: cross-attention, uncertainty-aware fusion, temporal alignment.
- Large-scale EMG pretraining and cross-dataset transfer.
- When physiological signals add information beyond vision under self-occlusion and fast motion.
Benchmark gaps:
- EgoEMG / Joint-angle MAE (degrees), vision-only: Best standalone vision WiLoR 4.7 deg avg; generic ResNet-18 5.9, fusion F-RN18+S 5.4.
- EgoEMG / EMG-to-pose MAE, user/both splits: Cross-user and combined splits remain harder than gesture split for all models.
- Label reconstruction / Invalid-frame rate / marker-to-mesh error: 3.6% invalid frames and 4.3 mm mean alignment error remain in the pseudo-ground-truth.
Restrictive assumptions: Optical mocap with 21 reflective markers per hand for labels.; Wearable bilateral EMG wristbands required.; Controlled gestures (60 classes), not object manipulation.; Soft synchronization via host timestamps and interpolation.

## [1183] RGB-D Video Generation for Improving Human-to-Robot Object Handover Prediction (arXiv 2026, dataset, S3 S6)
Source: https://arxiv.org/html/2608.13028; confidence HIGH.
Field cannot yet: The field cannot yet generate diverse, physically validated RGB-D handover data or reliably anticipate handover intention for unseen irregular objects.
Stated limitations:
- Generation re-injects segmented people into static backgrounds, limiting environmental diversity. [Appendix C Discussions and Limitations]
- No formal user study; evidence covers perception, not user comfort. [Appendix C Discussions and Limitations]
- Depth noise model is a heuristic approximation, not a validated physical sensor-noise model. [3.2 Stage II]
- Object term fails on irregular geometries, and some objects are physically hard to grasp. [5.4.2 Results Analysis]
- Gains on unseen objects are small and not statistically validated. [B.2 Downstream Utility]
Open problems listed:
- Environmental diversity of generated data (static backgrounds).
- Subjective user comfort and naturalness evaluation.
- Physically validated depth sensor noise modelling.
- Intention estimation for irregular and unseen objects.
- Grasping objects with complex surfaces.
Benchmark gaps:
- Real UR5e handover / Intention success rate: Overall 54/60; unseen objects 7/10, irregular 8/10.
- Hand2Bot-Real subset / Mean accuracy / FPR: Full module 90.0% accuracy with 13.6% FPR; real-only training 87.5% and 22.8%.
- Hand2Bot-Real test (250 clips) / FVD: Best PassGen FVD 337.59, PSNR 25.12.
Restrictive assumptions: Single RealSense L515 at robot base with face visible; gaze cues required.; Generated sequences on static backgrounds.; Parallel-jaw gripper on UR5e; GraspNet grasp candidates.; Real tests with 10 objects and small trial counts (60 positive, 30 negative).

## [1184] Assembly101: A Large-Scale Multi-View Video Dataset for Understanding Procedural Activities (CVPR 2022, dataset, S3)
Source: https://arxiv.org/html/2203.14712; confidence HIGH.
Field cannot yet: The field cannot yet recognize fine-grained hand-object actions and mistakes in free-form assembly with joint 3D hand and object understanding.
Stated limitations:
- Existing methods are far from solving the defined challenges, even with oracle inputs. [6 Conclusion]
- Large domain gap between egocentric and fixed views. [5.2 Camera viewpoints]
- Hand poses carry little object information; joint 3D object and hand pose modelling is left to future work. [5.5 3D pose-based action recognition]
- Mistake detection is hard; recall stays low even with ground-truth coarse labels. [5.7 Mistake detection]
- Long-tail classes perform poorly. [5.3 Head vs. tail classes]
Open problems listed:
- Fine-grained action recognition from egocentric views.
- Action anticipation.
- Temporal action segmentation of free-form procedures.
- Mistake detection.
- Cross-view domain gap.
- Long-tail recognition.
- Generalization to unseen toys.
- Joint 3D object and hand pose modelling.
- Domain gap from pretrained video features.
Benchmark gaps:
- Assembly101 / Temporal segmentation MoF / F1@50: C2F-TCN reaches 39.2 MoF and 21.3 F1@50.
- Assembly101 / 3D-pose action recognition Top-1: MS-G3D with context 28.7% action vs 33.8% video; object 36.3%.
- Assembly101 / Mistake detection recall: TSM mistake recall 46.6%, correction 29.6%; early prediction 35.0% and 26.4%.
Restrictive assumptions: Desk rig with 8 calibrated static cameras plus 4-camera headset.; 3D hand poses from a modified MegATrack egocentric tracker, not mocap ground truth.; No 6D object pose annotations.; Take-apart toy vehicles on a desk.

## [1185] A Dataset of Relighted 3D Interacting Hands (NeurIPS 2023, dataset, S3)
Source: https://arxiv.org/html/2310.17768; confidence HIGH.
Field cannot yet: The field cannot yet obtain accurate 3D ground truth for interacting hands under realistic in-the-wild appearance without a dense multi-camera studio plus synthetic relighting.
Stated limitations:
- Rendered images are cut at the forearm because the relighting network only takes hand geometry, not a whole body. [6 Conclusion, Limitations]
- Relighted images sometimes contain artifacts because the relighting network is trained on single-hand data and applied to two-hand data. [6 Conclusion, Limitations]
- Natural datasets captured with few cameras (e.g. a single RGB-D camera) cannot provide accurate annotations for complicated interacting hands, so they contain only simple poses. [1.2 Natural datasets]
- RANSAC triangulation of multi-view 2D detections (as in InterHand2.6M) gives temporally inconsistent 3D joints and hand collisions. [3.1 Capture stage]
Open problems listed:
- Two-hand analysis is hard due to self-similarity, complicated articulation, small size and inter-hand occlusion, especially from a single image.
- True 3D data is not obtainable from a single 2D observation (scale and depth ambiguity).
- Lab datasets have monotonous appearance (color, background, illumination).
- Natural datasets are limited in diversity and scale and provide only simple poses.
- Composited datasets have unrealistic appearance from lighting inconsistency.
- Relighting must generalize from single-hand to two-hand poses.
- Rendered data lacks forearm and body context.
Benchmark gaps:
- HIC / RRVE (mm): IntagHand 67.11 mm and InterWild 23.59 mm, versus about 19.7-20 mm on InterHand2.6M: large gap on natural images.
- Re:InterHand (3rd-person split) / RRVE (mm): InterWild 37.59 mm and IntagHand 52.91 mm before training on Re:InterHand; 20.07 mm after.
- Re:InterHand (egocentric split) / RRVE (mm): InterWild 28.89 mm even after training on the egocentric split.
Restrictive assumptions: Ground truth requires a studio with 170 calibrated synchronized cameras and 469 lights.; Hands only, no objects; no hand-object interaction.; Images rendered without forearm/body; downstream systems assumed to use cropped hand images from a separate hand detector.; 10 subjects; per-subject relighting networks and per-subject NeuralAnnot fitting.; IntagHand baseline assumes ground-truth hand boxes.

## [1186] RenderIH: A Large-scale Synthetic Dataset for 3D Interacting Hand Pose Estimation (ICCV 2023, dataset, S3)
Source: https://arxiv.org/html/2309.09301; confidence HIGH.
Field cannot yet: The field cannot yet train interacting-hand pose estimators on synthetic data alone that match real-data training on real images.
Stated limitations:
- Pose-optimization hyperparameters (attraction factors, loss weights) were chosen empirically rather than learned. [Supp. 4 Broader impacts and limitations]
- Training on RenderIH alone performs worse than training on real IH2.6M; the synthetic data is meant to reduce, not replace, real data. [Supp. 3.2 Impact of synthetic data]
- Interhand attraction can hurt when hand parts overlap seriously, because anchor pairs conflict and meshes are hard to separate. [Supp. 2 Optimization details]
- Real IH datasets are annotated by a machine annotator, which may be inaccurate, and are limited in amount. [Abstract]
Open problems listed:
- Obtaining real 3D interacting hand annotations is challenging and time-consuming due to severe self-occlusion.
- Validity of generated 3D hand poses (interpenetration, anatomical plausibility, naturalness).
- Diversity and realism of generated images (backgrounds, lighting, textures).
- Close-contact interacting hands are hard to annotate in reality and available close-contact data are limited.
- Reducing dependency on real data; synthetic data alone does not yet replace it.
Benchmark gaps:
- Tzionas (real) / error (reported triplet): Training on RenderIH only gives 22.11/25.8/47.7 versus 11.38/11.1/19.9 for IH2.6M-only training.
- InterHand2.6M / PA-MPJPE (mm, wrist root): RenderIH-only 13.50 mm versus IH2.6M-only 6.76 mm; mixed training 5.79 mm.
- InterHand2.6M / MRRPE (mm): Relative root position error remains 14.15 mm even with mixed training.
Restrictive assumptions: Hands only (MANO/A-MANO), no objects or forearm/body context.; Synthetic rendered monocular RGB; raw poses derived and augmented from InterHand2.6M.; Joint angle limits from a fixed anatomical table; naturalness judged by a discriminator trained on existing datasets.; Rendering cost over 200 hours on 4 A100 GPUs.

## [1188] HandoverSim: A Simulation Framework and Benchmark for Human-to-Robot Object Handovers (ICRA 2022, benchmark, S3 S6)
Source: https://arxiv.org/html/2205.09747; confidence HIGH.
Field cannot yet: The field cannot yet simulate an adaptive, physically interacting human giver for handovers, so evaluation still relies on replayed non-reactive motion or costly real users.
Stated limitations:
- The simulated human giver does not adapt to the robot's actions; the authors call this assumption naive. [III Simulating Handovers, Remarks]
- Realistic human hand motion during and after object release is not simulated because such data is lacking. [III Simulating Handovers, Remarks]
- Hand-object collision is disabled because motion-capture noise causes interpenetration; the object is moved by extra actuators rather than physically by the hand. [III Simulating Handovers]
- Baselines assume perfect perception (ground-truth hand and object states), so reported times exclude perception latency. [V Experiments]
- Simulation and real results are offset: real success rates are higher (cooperative users) and real efficiency lower (perception and control latency). [V Experiments, Correlation with Real-World Evaluation]
Open problems listed:
- Handover evaluation requires a real human in the loop, which is expensive and hard to reproduce.
- Different studies adopt different settings and metrics, making cross-study comparison difficult.
- Simulating a realistic human agent and its interaction with the robot during handover.
- Contact-rich hand-object interaction needs high-fidelity physics, including soft-body dynamics.
- Learning to control a dexterous simulated human hand to manipulate objects is notoriously hard.
- Human motion that adapts to the robot is not modelled.
- No data exists for human hand motion during release and post-release.
- Sim-to-real offset in success rate and timing.
Benchmark gaps:
- HandoverSim S0 / success rate: Best baseline 64.58 percent (Yang et al.); OMG Planner 62.50 percent; GA-DDPG w/o hold 36.81 percent.
- HandoverSim S1 vs real user study / success rate: GA-DDPG 55.00 percent in sim versus 80 percent real; offset attributed to cooperative real users.
- HandoverSim S1 vs real user study / time: Yang et al. 4.758 s accumulated in sim versus 10.7 s real approach time, sim excludes perception latency.
Restrictive assumptions: Human giver motion replayed from DexYCB mocap; single hand (right or left), 20 YCB rigid objects with known meshes.; Giver and robot face each other across a table; giver waits still at the end pose.; Ground-truth hand and object states given to policies; ground-truth segmentation for point-cloud baseline.; Franka Panda parallel-jaw gripper; simple PD controller; rigid-body PyBullet physics, no soft-body hand.

## [1189] ATTACH Dataset: Annotated Two-Handed Assembly Actions for Human Action Understanding (ICRA 2023, dataset, S3)
Source: https://arxiv.org/html/2304.08210; confidence HIGH.
Field cannot yet: The field cannot yet recognize overlapping two-handed assembly actions robustly across unseen viewpoints, nor capture finger-level detail from body-tracking skeletons.
Stated limitations:
- Azure Kinect skeletons represent fingers only very roughly, limiting finger-focused action perception; hand pose estimation is left as future work. [VI Conclusion, Future directions]
- In at least one view the person and action are always partially obscured by furniture parts, making the view split a major challenge. [III-C Dataset splits]
- Offline detection uses future frames, which is not practical for a cobot that must detect live. [V-A Robotic application scenario]
Open problems listed:
- Recognizing simultaneous, overlapping fine-grained actions of both hands during assembly.
- Generalization across camera viewpoints (mobile cobot sees new perspectives); view split is a major challenge.
- Background-independent action understanding, since training data for the target environment often cannot be recorded.
- Online, low-latency action detection on embedded hardware for cobots.
- Finger-level action perception, as body skeletons only roughly represent fingers.
- Large variance in action duration (0.2 s to minutes) and execution across skill levels.
Benchmark gaps:
- ATTACH view split / mean class accuracy (recognition): Best 33.2 percent (VA-CNN) and 30.4 percent (Swin) versus 57.4 percent on person split.
- ATTACH / frame-based mAP (detection): Best 29.5 percent offline person split; only 10.7-11.3 percent on view split.
Restrictive assumptions: Three static calibrated Azure Kinect cameras around a single worktable; ArUco cube calibration.; Single worker per recording, IKEA cabinet assembly only.; Body skeletons from the Azure Kinect body tracking SDK, without finger detail.; No 3D object poses or hand-object geometry annotated; only action labels.

## [1190] Ego-Exo4D: Understanding Skilled Human Activity from First- and Third-Person Perspectives (CVPR 2024, dataset, S3 S4 S1 S6 S2 S7)
Source: https://arxiv.org/html/2311.18259; confidence HIGH.
Field cannot yet: The field cannot yet estimate hand and body pose robustly from egocentric or sparse real-world views under occlusion, nor relate objects reliably across ego and exo views.
Stated limitations:
- Exo camera placement is hard to optimize; the action is often occluded by the person in most static exo cameras, affecting annotation. [6 Conclusions]
- Data are long-tailed due to natural activity durations (9x more cooking than soccer), which may challenge model training. [6 Conclusions]
- Only 70 percent of captures achieved frame-accurate automatic sync; the rest were manually synced with lower accuracy. [7.1 Time sync, Challenges and workarounds]
- Real-world capture with five or fewer cameras brings more occlusion and limited hand view and resolution from distant cameras. [5.4 Ego pose, Annotations]
- Lower body pose and temporal consistency need further refinement. [5.4 Ego pose, Results]
Open problems listed:
- Ego-exo object correspondence under extreme viewpoint change, heavy occlusion and many small objects.
- Exo-to-ego translation: predicting object location, shape and visibility in the ego view.
- View-invariant learning and harnessing exo views for ego keystep recognition.
- Energy-efficient multimodal online keystep recognition.
- Procedure understanding, especially future keystep prediction.
- Skill proficiency estimation (demonstrator and demonstration level), including effective ego-exo fusion.
- Ego body pose from monocular ego video or IMU, especially lower body and temporal consistency.
- Ego hand pose under occlusion, out-of-view hands and subtle skilled motion.
- Joint hand pose, hand-object interaction and full body pose in real-world recordings.
- Optimizing exo camera placement to avoid self-occlusion.
- Long-tailed activity distribution and differing skill challenge across domains.
- Robust time synchronization across heterogeneous cameras.
Benchmark gaps:
- Ego-Exo4D ego hand pose / MPJPE / PA-MPJPE (mm): Best baseline POTTER 30.57 MPJPE / 11.14 PA-MPJPE (manual GT); THOR-net 51.24 MPJPE.
- Ego-Exo4D ego body pose / MPJPE (cm): Best test MPJPE 18.51 cm (location-based); EgoEgo 26.38 cm.
- Ego-Exo4D exo-to-ego translation / visibility accuracy: pix2pix-mask 56.2 percent and GNT-mask 50.0 percent, near random guess.
- Ego-Exo4D keystep recognition / top-1 accuracy: Best test accuracy 41.53 percent (VI Encoder).
- Ego-Exo4D demonstration proficiency / mAP: ActionFormer absolute mAP fairly low; task described as very challenging.
Restrictive assumptions: Single-person skilled activities only.; Aria glasses plus 4-5 static exocentric GoPros, synchronized with QR-code timers.; Hand pose evaluation restricted to joints visible in at least 3 cameras.; Ego pose benchmark excludes exo video and other modalities at test time.

## [1191] Towards Human-Level Bimanual Dexterous Manipulation with Reinforcement Learning (NeurIPS 2022, benchmark, S3 S6)
Source: https://arxiv.org/html/2206.08686; confidence HIGH.
Field cannot yet: The field cannot yet learn generalizable bimanual dexterous skills from realistic (visual) observations that transfer from simulation to real hands.
Stated limitations:
- The benchmark does not support deformable object manipulation; tasks only cover articulated rigid bodies. [6 Conclusion and Future Work]
- Policies use state-based observations unavailable in the real world, hindering sim-to-real transfer. [6 Conclusion and Future Work]
- Multi-task and meta RL largely fail across tasks. [Abstract]
- Point-cloud visual input is very slow in Isaac Gym (200+ fps vs 30000+ for state), limiting environments to 256, so visual baselines were not used. [Appendix E]
Open problems listed:
- Multi-task and meta RL generalization across bimanual dexterous tasks.
- Learning from demonstration for dexterous bimanual manipulation.
- Simulation of soft bodies and deformable objects.
- Sim-to-real transfer of learned dexterous skills.
- Visual (point cloud or image) observations at high simulation throughput.
- Off-policy RL instability with high-dimensional action spaces and massive parallelism.
- Offline RL under severe distribution shift in large state/action spaces.
Benchmark gaps:
- Bi-DexHands MT20 / average reward: Multi-task PPO 8.9 versus per-task ground truth 32.5.
- Bi-DexHands ML20 / average reward (train/test): ProMP 0.02/0.36 versus ground truth 33.7/26.1; random 0.27 on test.
Restrictive assumptions: Simulation only (Isaac Gym) with two Shadow Hands.; Full ground-truth state observations.; Rigid and articulated objects only.; Requires thousands of parallel environments for sample efficiency.

## [1192] ADL4D: Towards A Contextually Rich Dataset for 4D Activities of Daily Living (arXiv 2024, dataset, S3 S1)
Source: https://arxiv.org/html/2402.17758; confidence HIGH.
Field cannot yet: The field cannot yet automatically and completely annotate 3D hands of multiple people handling multiple objects over long sequences without mocap for objects and manual intervention.
Stated limitations:
- Keypoints from aggregated 2D estimators are triangulated with SVD; learnable triangulation or epipolar transformers could improve results. [5.1 Limitations and Future Work]
- Deep-learning annotation methods generalize poorly across datasets early in data collection and need similar training data. [5.1 Limitations and Future Work]
- Dynamic Matching needs a hand detected in at least 3 views and often failed to isolate all hands in early annotation due to weak detectors. [3.6 3D Pose Subspace Clustering]
- A fixed clustering threshold fails when hand speed varies, e.g. two hands close together moving slowly versus sudden motion. [3.6 3D Pose Subspace Clustering]
- Search criteria are inconsistent across datasets and must be tuned per multi-camera system. [4.3 Tracking Evaluation Across Multiple Datasets]
Open problems listed:
- Existing 4D HOI datasets limited to one subject and one object, restricting generalization.
- Maintaining consistent 3D hand tracking over long activity sequences.
- Marker-free annotation methods rely on 60-90 fps, short sequences and at most two hands.
- Very large camera rigs add cost, synchronization and hardware burden.
- Hands are visually similar with fine articulation, weakening trajectory continuity.
- Marker-based hand capture biases detectors toward markers.
- Multi-view annotation systems are prone to failure with multiple actively moving objects.
- Generative action-based HOI animation limited to pick-up, grasp or handover.
- Bad cross-dataset generalization of learned annotators and HMR models.
Benchmark gaps:
- Cross-dataset HMR (I2L-MeshNet) / root-relative MPJPE (mm): Within-dataset about 12-14 mm but cross-dataset 33.34-54.76 mm.
- ADL4D hand action segmentation / frame accuracy / F1@50: Best 55.04 percent accuracy and F1@50 33.78 with pose features; I3D 32.77 and 7.12.
- ADL4D annotation / skipped frames: Best tracking mode still skips 226 frames and has 5.94 mm MPJPE versus manual labels.
Restrictive assumptions: 8 calibrated RealSense D435 RGB-D cameras plus 8 OptiTrack mocap cameras with markers on objects.; 12 pre-scanned rigid object meshes with markers.; Hands tracked marker-free but need detection in at least 2-3 views.; Extra spotlights required to avoid motion blur; 20 fps synchronized capture.; Software synchronization; up to two subjects.

## [1193] HardMo: A Large-Scale Hardcase Dataset for Motion Capture (CVPR 2024, dataset, S4)
Source: https://openaccess.thecvf.com/content/CVPR2024/papers/Liao_HardMo_A_Large-Scale_Hardcase_Dataset_for_Motion_Capture_CVPR_2024_paper.pdf; confidence HIGH.
Field cannot yet: The field cannot yet recover correct hand-wrist and foot-ankle articulation in unusual poses from monocular video without targeted pseudo-labelled hardcase data.
Stated limitations:
- The work only addresses hand and foot misalignment; other challenges such as self-occlusion remain. [6 Conclusion, Limitation and Future Works]
- Automatic SMPL annotations from 4DHumans fail on extreme hand and foot postures and require mining and refinement. [4.2 Hardcase Annotation]
- Hand hardcase handling targets wrist rotation only, not precise finger postures. [4.2 Hardcase Annotation]
- Optimization-based label correction (SMPLify, EFT) damages other parts and can produce implausible poses. [4.2 Hardcase Annotation]
Open problems listed:
- Domain gap between standard mocap datasets and unusual real-world motions.
- Limited diversity of hand and foot postures in synthetic datasets.
- Incorrect hand and foot SMPL annotations in real datasets.
- Common keypoint formats lack hand and foot keypoints.
- Self-occlusion in hard poses.
- Marker or markerless capture of skilled dance and martial arts is prohibitively expensive.
Benchmark gaps:
- HardMo / MPJPE (mm): ProHMR 113.8 mm and HMR (InstaVariety) 61.1 mm versus HardMo-HMR 36.0 mm.
- HardMo-Foot P1 / foot MPJPE (mm): ProHMR 213.6 mm and 4DHumans-b 88.1 mm versus HardMo-HMR 34.9 mm.
Restrictive assumptions: Pseudo 3D labels from 4DHumans plus RTM-pose keypoints and learned refinement, not marker or multi-view mocap; test labels are optimized pseudo labels.; SMPL body model without articulated fingers or face.; Single-person monocular internet video of dance and martial arts.; Samples filtered by keypoint confidence thresholds (0.5, 0.65).

## [1197] WorldPose: A World Cup Dataset for Global 3D Human Pose Estimation (ECCV 2024, dataset, S4)
Source: https://arxiv.org/html/2501.02771; confidence HIGH.
Field cannot yet: Monocular global pose methods cannot yet recover accurate world-frame trajectories and relative positions of many people over large areas from a moving, zooming camera.
Stated limitations:
- Annotation pipeline depends on 2D detection quality and static camera layout. [Limitations and Future work]
- Costly manual correction was needed for poorly covered or blurry players. [Limitations and Future work]
- Only male matches, so gender representation is unequal. [Limitations and Future work]
- Fitting SMPL to triangulated 3D joints lacks a pose prior and can yield unrealistic poses with low reprojection error. [Supplementary 1.5 SMPL Fitting]
- Commercial broadcast calibration normally needs a pre-game scan that was unavailable, so 3D poses were used as extra constraints. [1 Introduction]
- Pipeline accuracy against Vicon is about 8 cm G-MPJPE and 6.6 cm PA-MPJPE, measured only in the penalty box with 6 players. [4.2 Comparison with Vicon]
Open problems listed:
- Global methods struggle when the area of movement expands.
- Determining relative positions between multiple people, even with a shared ground plane.
- Degraded performance when SLAM camera poses are unreliable due to texture-less backgrounds or changing focal length.
- Marker-based capture is impractical over vast areas; body-worn sensors drift under dynamic motion.
- Calibrating fast-moving broadcast cameras with few distinctive pitch features.
- Low player resolution, fast motion and frequent occlusion degrade SOTA 2D detectors.
- Unequal gender representation in the dataset.
Benchmark gaps:
- WorldPose / G-MPJPE (mm): GLAMR 18888.9, SLAHMR 8334.1, SLAHMR with GT cameras 5837.2; per-person alignment still 3749.7 to 4699.5.
- WorldPose / Per-Meter Drift (cm/m): GLAMR 53.3, SLAHMR 17.6, SLAHMR with GT cameras 10.7.
- WorldPose / PA-MPJPE (mm): SLAHMR 163.9 and GLAMR 85.2 are worse than their initializers 4DHuman 116.5 and HybrIK 78.8.
Restrictive assumptions: Ground truth requires a calibrated multi-view static stadium camera system (VAR-style infrastructure).; Thorough manual review and correction of 2D detections and associations.; Soccer field markings and planar-field prior for calibration.; Broadcast camera calibration relies on commercial software plus triangulated player poses.; Validation against Vicon only in a small sub-area (penalty box) at night.

## [1206] Systematic Comparison of Projection Methods for Monocular 3D Human Pose Estimation on Fisheye Images (ICRA 2025, benchmark, S4)
Source: https://arxiv.org/html/2506.19747; confidence HIGH.
Field cannot yet: Monocular 3D pose estimators cannot yet deliver accurate absolute 3D pose for people very close to a wide-FOV robot camera without known intrinsics and hand-chosen projections.
Stated limitations:
- All experiments use ground-truth bounding boxes; a real detector would be needed in deployment. [VI Metrics & Experiments]
- Method requires known intrinsics of the physical fisheye camera. [Fig. 2 caption]
- No projection is best for relative pose estimation overall. [VII-B]
- Pinhole projection is weakest for absolute pose regardless of FOV. [VII-C]
- Ground truth is pseudo-GT from multi-view triangulation of 2D detector outputs, not marker-based. [II-C]
- Skeleton format differs from training data; a linear mapping had to be trained on a held-out FISHnCHIPS subset. [V Implementation & Training]
Open problems listed:
- No systematic comparison of fisheye handling methods for 3D HPE existed.
- Upward-facing (robot-height) fisheye views have not been addressed in any study.
- Existing fisheye HPE datasets focus on egocentric AR/VR or downward surveillance; horizontal third-person datasets are not public.
- Pinhole projection becomes infeasible for subjects close to the camera.
- No single best projection for relative pose; choice depends on FOV covered by the person.
- Research on 3D HPE using fisheye images is limited.
Benchmark gaps:
- FISHnCHIPS / A-MPJPE (mm): Best absolute error still about 204-205 mm (EC 204.4, DS 205.2); PH 219.4.
- FISHnCHIPS / A-PCK150 (%): Best only 45.5% (DS, EF); PH 41.5%.
- FISHnCHIPS / MPJPE vs MPJA: Relative MPJPE exceeds 250 mm at 150 degree MPJA; hybrid heuristic improves MPJPE by only 2 mm.
Restrictive assumptions: Calibrated fisheye intrinsics (double sphere model) must be known.; Ground-truth bounding boxes instead of a detector.; Single-frame, non-temporal MeTRAbs trained only on pinhole data.; Indoor household scenes only, 7 subjects, 3 setups, data downsampled to 5 Hz.; Pseudo-GT from 10-camera triangulation including Kinects.

## [1229] Benchmarking 3D Human Pose Estimation Models Under Occlusions (arXiv 2025, benchmark, S4)
Source: https://arxiv.org/html/2504.10350; confidence HIGH.
Field cannot yet: 3D pose lifters cannot yet keep accurate wrist and other distal-joint estimates under realistic, prolonged occlusion while also staying accurate on clean input.
Stated limitations:
- All lifting models degrade under occlusion; diffusion models underperform. [Abstract]
- No model is robust across the whole occlusion range. [6 Conclusion]
- Occlusion-aware DTF is robust under severe noise but worse on clean input. [6 Conclusion]
- Distal, high-DoF joints are error-prone even when visible. [6 Conclusion]
- Diffusion lifters are too slow for real time. [4.2.1]
- Current models are not ready for real-world deployment. [6 Conclusion]
- Only one dataset with keypoint-level occlusion labels exists, so the benchmark relies on synthetic BlendMimic3D. [1 Introduction]
Open problems listed:
- Lifting models lack explicit occlusion modeling; existing training strategies are insufficient for real-world occlusions.
- Diffusion-based lifters need alternative conditioning, uncertainty-aware denoisers or hybrid formulations.
- Interpolation-based occlusion handling fails for prolonged realistic occlusions.
- Masking-trained models do not generalize across occlusion counts and patterns.
- Distal joints (wrists, feet) are inherently hard even when visible.
- Camera-related distribution shift (close distances, unseen viewpoints) harms generalization.
- Evaluation inconsistencies: hip keypoint normalization and skeleton format mismatches.
- Standard benchmarks (Human3.6M, MPI-INF-3DHP) and global metrics do not reflect real-world complexity.
- Diffusion models are computationally expensive for real-time use.
Benchmark gaps:
- BlendMimic3D / MPJPE (mm): MixSTE rises from 69.46 (GT 2D) to 175.21 at sigma 0.05; DiffuPose reaches 223.32; FinePose 183.86.
- BlendMimic3D / MPJPE (mm): Original DTF-GT outputs 301.91 mm at all noise levels; DTF variant best at sigma 0.05 with 95.70 but 93.37 at low noise versus 69.46 best clean.
Restrictive assumptions: Occlusion simulated as zero-mean Gaussian noise added to ground-truth 2D keypoints using ground-truth occlusion labels.; Evaluation on synthetic BlendMimic3D only (test subject S2).; All models trained on Human3.6M and not retrained.; Single-person 2D-to-3D lifting only; no image-based or multi-view methods.

## [1231] Validation of Human Pose Estimation and Human Mesh Recovery for Extracting Clinically Relevant Motion Data from Videos (arXiv 2025, benchmark, S4 S7)
Source: https://arxiv.org/html/2503.14760; confidence HIGH.
Field cannot yet: Off-the-shelf monocular markerless capture cannot yet match marker or IMU accuracy and frequency for fine, clinically meaningful joint kinematics beyond simple low-speed 1D metrics.
Stated limitations:
- Markerless errors remain high relative to IMU and MoCap. [4 Discussion]
- Only simple 1D knee metrics were validated; complex biomechanics metrics need further study. [4 Discussion]
- MoCap and IMUs remain preferred for maximum accuracy due to higher frequency and accuracy. [4 Discussion]
- Modalities could not be hardware-synchronized; curves were aligned manually. [2.5.1 Individual-Level Analysis]
- Data quality still needs improvement; claim limited to low-speed clinical actions. [Abstract]
Open problems listed:
- Self-occlusion leads to incorrect landmark estimation or frame-to-frame jitter.
- Clothing choice affects predicted pose and needs further testing.
- Lighting affects pose accuracy.
- Few studies validate markerless methods against biomechanics gold standards for clinical use.
- Markerless capture lacks the recording frequency to detect small pathology-relevant changes.
- Synchronizing heterogeneous capture modalities is difficult due to hardware limitations.
- Complex sports-biomechanics metrics remain unvalidated.
Benchmark gaps:
- Own 10-participant clinical capture / Knee angle vs IMU/MoCap: MediaPipe offset of roughly 15 degrees at start and end of squat-to-box; VIBE range of motion deviates from other modalities.
Restrictive assumptions: 10 healthy adult participants without knee conditions.; Low-speed, well-defined actions (sit-to-stand, squat-to-box) chosen for consistent peaks.; Two fixed tripod cameras at 30 Hz, frontal and sagittal views.; Knee flexion only; IMU treated as reference in Bland-Altman analysis.; Manual temporal alignment of modalities.

## [1237] A Dataset and Evaluation for Complex 4D Markerless Human Motion Capture (arXiv 2026, dataset, S4)
Source: https://arxiv.org/html/2604.12765; confidence HIGH.
Field cannot yet: Markerless capture cannot yet reconstruct closely interacting, mutually occluding people with stable identities; errors roughly double to triple outside standard benchmarks.
Stated limitations:
- Dataset captured with only three male actors. [3 (ii) 4D Acquisition]
- D455 depth accuracy limits capture volume and activity design. [3 (i) Capture Environment and Hardware Setup]
- Evaluated baselines are frame-based and ignore interaction and time. [4.2.1 C]
- Marker tracking suffers dropout in tight multi-person interactions; extra marker clusters were added. [3 (ii) 4D Acquisition]
Open problems listed:
- Lack of interaction-aware modeling for multi-person scenes.
- Insufficient robustness to severe occlusion and body overlap.
- Limited exploitation of multi-view and temporal cues.
- Standard datasets (Human3.6M, CMU Panoptic, HUMAN4D) are approaching saturation.
- No dataset combines synchronized multi-view RGB-D, marker-based ground truth and interactions of more than two people.
- Hardware-level sync across RGB-D sensors is often missing; small misalignments cause artifacts.
- Generalization of HMR in tightly coupled social interactions remains unclear.
- Identity switching and rapid position exchanges between similarly dressed people.
Benchmark gaps:
- HUM4D / PA-MPJPE (mm): SPIN, PARE, HMR2.0, PersPose rise from about 39-82 on 3DPW to 151-180 on HUM4D; PersPose best.
Restrictive assumptions: Professional 44-camera Vicon studio and 56-marker MoCap suits for ground truth.; Six hardware-synced RealSense D455 at 720p, 15 fps, within about 3 m optimal depth range.; Evaluation uses PA-MPJPE only with off-the-shelf weights, no fine-tuning.; Ground truth retargeted to SMPL 24-joint via Maya IK.

## [1238] EMDB: The Electromagnetic Database of Global 3D Human Pose and Shape in the Wild (ICCV 2023, dataset, S4)
Source: https://arxiv.org/html/2308.16894; confidence HIGH.
Field cannot yet: Monocular methods cannot yet recover drift-free world-frame human trajectories and accurate limb rotations from a moving hand-held camera in the wild.
Stated limitations:
- No multi-person sequences because multiple EM systems interfere. [8 Conclusion, Limitations]
- No foot sensors since metal in floors disturbs EM readings. [8 Conclusion, Limitations]
- Camera trajectory quality bounded by ARKit. [8 Conclusion, Limitations]
- In-the-wild global trajectories drift: 23.4 cm over 81 m indoors, 73.0 cm over 112 m outdoors. [6.2 Global Trajectories]
Open problems listed:
- Little work on global pose estimation due to lack of in-the-wild datasets with global trajectories.
- Camera-relative weak-perspective settings are too restrictive for moving-camera applications.
- Static multi-camera systems restrict outdoor use; egocentric systems have self-occlusion or fixed volumes.
- IMU drift and lack of positional measurements constrain pose diversity and accuracy (3DPW).
- Multi-person EM capture needs handling of cross-talk.
- MPJPE-PA is forgiving; angular error, jitter and standard deviation are neglected.
- Monocular RGB methods have ample room for improvement in pose and global trajectory.
Benchmark gaps:
- EMDB 1 / MPJPE-PA (mm): Best method HybrIK exceeds 65 mm despite GT bounding boxes.
- EMDB 1 / MPJAE (deg): All methods exceed 23 degrees mean angular error.
- EMDB 2 / G-MPJPE (mm): GLAMR 3193 mm, G-MVE 3203 mm.
Restrictive assumptions: Up to 12 body-worn wireless EM sensors with source on the lower back.; Per-subject minimal-clothing scan in a multi-view volumetric studio and calibration sequence for skin-to-sensor offsets.; Hand-held iPhone RGB-D with ARKit poses; clap-based synchronization.; Single person; baselines given ground-truth bounding boxes; fully occluded frames excluded.

## [1239] BEDLAM: A Synthetic Dataset of Bodies Exhibiting Detailed Lifelike Animated Motion (CVPR 2023, dataset, S4)
Source: https://arxiv.org/html/2306.16940; confidence HIGH.
Field cannot yet: Synthetic human data cannot yet realistically render people interacting with objects or each other, especially hands manipulating objects.
Stated limitations:
- Licensing blocks use of many high-quality commercial assets. [5 Limitations and Future Work]
- Motions are random, uncorrelated with clothing and scene, and lack interactions. [5 Limitations and Future Work]
- Few sitting, lying, complex sports poses. [5 Limitations and Future Work]
- Hands interacting with objects largely missing. [5 Limitations and Future Work]
- No facial motion and no evaluation datasets for body plus face. [5 Limitations and Future Work]
- Hair lacks physics and diversity; hair cards cause artifacts. [5 Limitations and Future Work]
- Cloth simulation fails for high-BMI bodies. [5 Limitations and Future Work]
- Bodies are barefoot; textures lack realistic reflectance. [5 Limitations and Future Work]
- Accuracy still depends on real-image backbone pre-training. [6 Discussion and Conclusions]
Open problems listed:
- Licence restrictions on commercial assets impede research; more open-source assets needed.
- Synthesizing realistic human-human and human-object interactions automatically.
- Correlating motions with clothing and scenes.
- Few sitting, lying and sports poses due to cloth simulation difficulty.
- Hair physics, long hair and hair color diversity.
- Body-shape diversity: children, scoliosis, amputees; high-BMI draping and retargeting.
- Realistic skin textures and reflectance.
- Shoes that change posture and gait.
- Very little mocap with full body plus hands interacting with objects.
- No datasets evaluating full body and facial motion.
- Estimating humans in world coordinates; exploiting temporal information and action semantics.
- Removing dependence on real-image backbone pre-training.
Benchmark gaps:
- 3DPW / RICH / SSP-3D / HBW / MPJPE, PVE, shape error: Table numbers not extracted; paper states methods trained on BEDLAM do not estimate world coordinates or use temporal information.
Restrictive assumptions: Motions randomly sampled from AMASS with GRAB hand motions pasted on; no object contact.; Mostly static cameras with randomized extrinsics.; Multiple people placed to avoid collision rather than interact.; Evaluation of single-frame regressors (HMR, CLIFF).

## [1240] BEDLAM2.0: Synthetic humans and cameras in motion (NeurIPS 2025, dataset, S4)
Source: https://arxiv.org/html/2511.14394; confidence HIGH.
Field cannot yet: Synthetic training data cannot yet supply realistic human-object contact and manipulation, so world-frame methods are trained without object interaction.
Stated limitations:
- Only human-ground interaction; no objects. [6.1 Limitations]
- Realistic synthetic human-object and human-human interaction remains open. [6.1 Limitations]
- Non-foot body-scene contacts may be inaccurate (e.g. hands in cartwheels). [6.1 Limitations]
- Motions not semantically meaningful in scene or relative to other people. [6.1 Limitations]
- Visual domain gap to real video remains. [6.1 Limitations]
- No facial motion or audio. [6.1 Limitations]
- Removing unsupported motions (sitting, stairs) hurts accuracy on such scenes. [5 Experiments]
Open problems listed:
- General human-object and human-human interaction synthesis is open.
- Body-scene contact beyond feet is inaccurate.
- Motions lack semantic meaning relative to scene and other people.
- No children, amputees or atypical morphologies; no impaired motion or assistive devices.
- Visual domain gap to real videos.
- Facial motion and audio absent.
- Lack of ground-truth sequences limits 4D point tracking, non-rigid SfM, depth, flow and dynamic reconstruction.
Benchmark gaps:
- EMDB (24) / W-MPJPE100 (mm): Best is PromptHMR trained on B1+B2 at 193.7; GVHMR on B2 284.4.
- EMDB (24) / WA-MPJPE100 (mm): GVHMR on B2 alone 113.7, slightly worse than on B1 112.4.
Restrictive assumptions: Motions exclude actions depending on external objects (sitting) or non-ground support (stairs).; Hand motions randomly sampled from ARCTIC and attached to AMASS bodies, not coordinated with objects.; Only flat-soled shoes.; 3D environments cannot be redistributed.

## [1241] SLOPER4D: A Scene-Aware Dataset for Global 4D Human Pose Estimation in Urban Environments (CVPR 2023, dataset, S4)
Source: https://arxiv.org/html/2303.09095; confidence HIGH.
Field cannot yet: The field cannot yet estimate globally accurate human trajectories and poses for fast, large-area activities from a moving monocular or LiDAR viewpoint.
Stated limitations:
- Single-person capture only, although multiple people appear in the data. [5 Discussions, Limitations]
- Camera and LiDAR are not synchronized online, so frame drops cause tedious offline work. [5 Discussions, Limitations]
- Camera texture is not used for color or texture reconstruction of scenes and humans. [5 Discussions, Limitations]
Open problems listed:
- Single-person limitation; multi-person urban capture is open.
- Online synchronization of camera and LiDAR.
- Exploiting camera texture for colored and textured reconstruction of scenes and humans.
- Global human pose estimation in large outdoor scenes with high-dynamic activities.
- Domain gap between different LiDAR sensors for LiDAR-based HPE.
Benchmark gaps:
- SLOPER4D Running001 / ATE RMSE / G-MPJPE (GLAMR): 29.48 m ATE and 32329.3 mm G-MPJPE; global trajectories of high-dynamic activity remain far from solved.
- SLOPER4D Football / MPJPE (GLAMR): 264.6 mm MPJPE and PA-MPJPE 118.5 mm on dynamic football training.
- SLOPER4D Garden001 / PA-MPJPE (GLAMR): Best case 86.3 mm on daily walking; still G-MPJPE 4407.0 mm.
Restrictive assumptions: Subject wears a full IMU mocap suit while a second operator carries the head-mounted LiDAR plus camera.; Offline joint optimization with LiDAR SLAM, IMU poses and scene constraints to build ground truth.; Offline camera-LiDAR synchronization and per-frame calibration fine-tuning.; Single tracked subject per sequence.

## [1242] HSC4D: Human-Centered 4D Scene Capture in Large-Scale Indoor-Outdoor Space Using Wearable IMUs and LiDAR (CVPR 2022, dataset, S4)
Source: https://arxiv.org/html/2203.09215; confidence HIGH.
Field cannot yet: The field cannot yet capture drift-free human motion and scene from wearable sensors alone in crowded, narrow or self-occluding conditions.
Stated limitations:
- Depends on LiDAR SLAM for initial localization, so fails where LiDAR mapping fails. [6 Discussions, Limitations]
- Activities that occlude the body-mounted LiDAR are excluded. [6 Discussions, Limitations]
- Hand-crafted optimization losses; rock climbing does not always work. [6 Discussions, Limitations]
Open problems listed:
- Robust capture when LiDAR mapping fails (crowded or narrow spaces).
- Capture of activities that occlude the body-worn LiDAR.
- Replacing hand-crafted losses for difficult motions such as climbing.
Benchmark gaps:
- HSC4D sequences (Building, Gym, Road) / global localization error: Error increases linearly with distance for all methods; HSC4D improves 25.4% over LiDAR-only baseline but does not remove growth.
Restrictive assumptions: Subject wears 17 Noitom IMUs plus body-mounted 64-beam LiDAR and mini-computer.; Body shape parameter assumed constant per recording.; A-pose start for coordinate calibration; offline synchronization and calibration.; Offline graph-based and joint optimization.; Static scene map from LiDAR SLAM.

## [1243] LiDARCap: Long-range Markerless 3D Human Motion Capture with LiDAR Point Clouds (CVPR 2022, dataset, S4)
Source: https://arxiv.org/html/2203.14698; confidence HIGH.
Field cannot yet: The field cannot yet recover detailed human motion from sparse, density-varying depth points under occlusion and interaction.
Stated limitations:
- Dataset scenes are flat, open and unobstructed, unlike real applications. [5 Discussion, Limitation]
- Dataset lacks shape parameters, occlusion-heavy scenes and multi-person interaction. [5 Discussion, Limitation]
- Baseline not robust to varying point density across distances and devices. [5 Discussion, Limitation]
- Sparse-point mocap remains open. [5 Discussion, Limitation]
Open problems listed:
- Realistic, cluttered, occluded scenes for LiDAR mocap.
- Shape estimation from LiDAR.
- Multi-person interactions and occlusions.
- Robustness to varying point density across distances and sensors.
- Accurate mocap on sparse LiDAR point clouds.
Benchmark gaps:
- LiDARHuman26M (15-28 m sequence) / per-frame accuracy vs distance: Error rises sharply with distance; under 30 points per person at the farthest range.
Restrictive assumptions: Single static LiDAR; person point cloud pre-segmented and resampled to 512 points.; Flat, open, unobstructed scenes without occluders.; Single performer per sequence.; IMU-suit ground truth; no shape parameters.

## [1244] LiDAR-aid Inertial Poser: Large-scale Human Motion Capture by Sparse Inertial and LiDAR Sensors (TVCG 2023, dataset, S4)
Source: https://arxiv.org/html/2205.15410; confidence HIGH.
Field cannot yet: The field cannot yet fuse sparse depth and inertial sensing to capture fast motion and human-object interaction across sensor domains.
Stated limitations:
- 10 fps LiDAR yields unsmooth results for extremely fast motions. [4.3 Discussion]
- Domain gaps between LiDAR sensors with different point distributions and ranges remain, needing larger datasets. [4.3 Discussion]
- Two open challenges named for the dataset task. [3.3 Challenge]
Open problems listed:
- Extracting features from sparsity-varying LiDAR point clouds with few points beyond 20 m.
- Effective LiDAR-IMU fusion so both sensors complement each other.
- Recovering high-frequency motion at low LiDAR frame rate.
- Cross-LiDAR domain gaps.
- Multi-person and human-object interaction capture.
Restrictive assumptions: Subject wears 4 IMUs plus a single LiDAR observes them.; Large part of training data is synthesized LiDAR-IMU data from AMASS, DIP-IMU, AIST++ and LiDARHuman26M.; Single person; no human-object interaction.

## [1245] Human-M3: A Multi-view Multi-modal Dataset for 3D Human Pose Estimation in Outdoor Scenes (arXiv 2023, dataset, S4)
Source: https://arxiv.org/html/2308.00628; confidence HIGH.
Field cannot yet: The field cannot yet separate and pose closely interacting or occluded people from merged sparse point clouds without manual review.
Stated limitations:
- Multi-view configuration and calibration are unwieldy and time-intensive. [5 Limitations]
- Annotation still needs manual intervention and screening. [5 Limitations]
- Limited range of scenes and motion patterns. [5 Limitations]
- More advanced fusion techniques needed. [5 Limitations]
Open problems listed:
- Cumbersome multi-view configuration and calibration.
- Annotation still needs manual review.
- Limited scene and motion diversity.
- Need for more advanced multi-modal fusion.
- Distant, heavily occluded people and close-proximity people with merged point clouds.
Benchmark gaps:
- Human-M3 intersection scene / MPJPE / recall (MMVP): 22.62 cm MPJPE and 77.39% recall.
- Human-M3 / MPJPE: Best multimodal MMVP 0.079 m; RGB-only methods 0.099-0.14 m.
Restrictive assumptions: Multiple static capture units (RGB plus LiDAR) with manual camera-LiDAR extrinsic calibration.; Manual review of annotations (about 25 person-hours) and manual test-set annotation.; Pedestrian detection and tracking via PointPillars and AB3DMOT.

## [1246] EgoBody: Human Body Shape and Motion of Interacting People from Head-Mounted Devices (ECCV 2022, dataset, S4 S7)
Source: https://arxiv.org/html/2112.07642; confidence HIGH.
Field cannot yet: The field cannot yet reliably reconstruct truncated, blurred bodies and accurate wrists and hands of an interaction partner from a head-mounted camera.
Stated limitations:
- No hardware synchronization between HoloLens2 and Kinect; software alignment via flashlight. [Appendix F Limitations]
- Small temporal misalignment visible on fast motions such as hand movements. [Appendix F Limitations]
- Factory depth calibration of HoloLens2 is inaccurate, requiring keypoint refinement. [Sec. 3 capture]
- OpenPose fails under body-body, body-scene and self-occlusion; detections manually cleaned. [Supplementary]
Open problems listed:
- Severe body truncation in egocentric view.
- Motion blur from wearer motion.
- People entering and exiting the field of view.
- High errors on extremities (wrists).
- Hardware synchronization of HMD and external cameras.
- Need more participants and modalities (audio, language).
Benchmark gaps:
- EgoBody test / PA-MPJPE: Methods average 77% higher error than on 3DPW; performance varies widely across SOTA methods.
- EgoBody test / per-joint MPJPE: Extremities, especially wrists, remain high error.
- You2Me / PA-MPJPE: Off-the-shelf SPIN 152.8 mm, METRO 117.7 mm before fine-tuning.
Restrictive assumptions: Ground truth requires a five-Kinect static multi-view rig calibrated to the HMD.; Indoor scenes only (15 indoor scenes).; Offline SMPL-X fitting with manual cleaning of 2D detections.

## [1247] NymeriaPlus: Enriching Nymeria Dataset with Additional Annotations and Data (arXiv 2026, dataset, S4 S7)
Source: https://arxiv.org/html/2603.18496; confidence HIGH.
Field cannot yet: The field cannot yet provide in-the-wild egocentric ground truth that tracks moved, manipulated objects together with accurate body motion.
Stated limitations:
- Foot sliding is hard to mitigate because foot contact labels are unreliable and lower-body signals are weak. [3.2.4 Metrics and Evaluations]
- Annotation tool cannot label dynamic objects; moved objects annotated sparsely per recording. [3.3.5 Open Set Taxonomy]
- Floor annotations accurate only to 1-2 cm indoors and unavailable outdoors; XSens contacts unreliable on stairs. [3.2.2 Motion Optimization]
- Device placement on body known only up to calibration error and may drift. [3.2.2 Motion Optimization]
Open problems listed:
- Reliable foot contact and lower-body motion from head and wrist signals.
- Annotation of dynamic, moved objects.
- Floor and contact ground truth outdoors.
- Most HOI datasets limited to tabletop manipulation.
- Egocentric datasets lacking reliable motion ground truth or rich scene context.
Benchmark gaps:
- NymeriaPlus / foot sliding (% contact frames): 9.81% of contact frames still slide.
- NymeriaPlus / wrist distance error: 5.07 cm including constant offset (from 14.32 cm).
Restrictive assumptions: Inertial XSens suit plus Aria glasses and wristbands.; Scene assumed largely static across 2-4 days per venue; boxes only for static objects.; Object meshes generated by ShapeR and manually rated.

## [1248] EgoHumans: An Egocentric 3D Multi-Human Benchmark (ICCV 2023, benchmark, S4)
Source: https://arxiv.org/html/2305.16487; confidence HIGH.
Field cannot yet: The field cannot yet track and reconstruct multiple people consistently from fast-moving wearable cameras without dense static rigs for ground truth.
Stated limitations:
- Trades 3D keypoint accuracy for in-the-wild capture; gap to static indoor wired systems from sync and calibration errors. [6 Discussion, Limitations]
- Existing methods unsuited to rapid wearable camera motion. [6 Discussion]
Open problems listed:
- Tracking under rapid egocentric camera motion.
- Person-id switching under occlusion and unconstrained activity.
- Accuracy gap of in-the-wild capture vs static wired rigs due to sync and calibration.
- Lack of diverse outdoor multi-human 3D ground truth.
Benchmark gaps:
- EgoHumans test / IDF1 / ID switches: Off-the-shelf 2D trackers show many identity switches; EgoFormer gains 13.6% IDF1, still reports 741 ID switches.
- EgoHumans / Chamfer to LiDAR GT: Annotation error decreases with more secondary cameras; accuracy below static wired systems.
Restrictive assumptions: EgoFormer assumes 3D camera poses reliably estimated from VIO.; Ground truth needs 8-15 static secondary GoPro cameras plus Aria glasses.; EgoFormer uses three egocentric images (RGB plus grayscale) per step.

## [1249] Harmony4D: A Video Dataset for In-The-Wild Close Human Interactions (NeurIPS 2024, dataset, S4)
Source: https://arxiv.org/pdf/2410.20294; confidence HIGH.
Field cannot yet: The field cannot yet recover accurate, mutually consistent 3D meshes of closely interacting people from monocular in-the-wild video, nor obtain high-precision contact GT outside static studio rigs.
Stated limitations:
- The annotation pipeline trades pose and shape accuracy under contact for the ability to capture in the wild with a mobile camera rig. [5 Conclusion, Limitations]
- Existing monocular mesh methods fail on the dataset, attributed to lack of human-human contact data in training. [5 Conclusion]
Open problems listed:
- Monocular mesh regression under close human-human contact and severe occlusion remains poor for all evaluated methods.
- Human-human contact interactions are underrepresented in training data; authors argue the gap is data, not methods.
- Accurate 3D GT for in-the-wild close contact without static dense wired capture systems.
Benchmark gaps:
- Harmony4D test / MPJPE (mm): Off-the-shelf Multi-HMR 93.8 mm vs 61.4 mm on 3DPW; best top-down HMR2.0 108.2 mm; BUDDI (contact-specific) 126.35 mm.
- Harmony4D test / N-PVE: Very high normalized per-vertex error for all baselines due to inconsistent meshes under occlusion.
Restrictive assumptions: Annotation needs 20+ synchronized calibrated cameras (dense mobile rig).; Pre-contact frames where subjects are completely visible from most views are used to initialize tracking.; Per-subject Kalman-filter motion model trained for forecasting occluded keypoints.; Baselines evaluated with ground-truth bounding boxes for top-down methods.; Two-person body-only interactions (SMPL); no objects or hands-object interactions.

## [1250] Hi4D: 4D Instance Segmentation of Close Human Interaction (CVPR 2023, dataset, S4)
Source: https://arxiv.org/pdf/2303.15380; confidence HIGH.
Field cannot yet: The field cannot yet reconstruct separated, contact-consistent detailed geometry and pose of closely interacting people from monocular or sparse-view input.
Stated limitations:
- Method does not model hands or facial expressions explicitly. [Limitations]
- The optimization is computationally slow. [Limitations]
Open problems listed:
- Monocular and multi-view SMPL estimation under close human-human contact (depth ordering, contact, interpenetration).
- Monocular detailed geometry reconstruction of closely interacting humans; single-person methods do not extend.
- Multi-view detailed reconstruction still shows artifacts at extremities.
- Modelling hands and faces during close interaction.
Benchmark gaps:
- Hi4D / MPJPE (mm), monocular: PARE 87.6, ROMP 93.0, BEV 92.5; contact distance CD 295.8-338.0 mm.
- Hi4D / Contact distance CD (mm), multi-view: MVPose 8-view still 166.8 mm CD, 4-view 234.8 mm.
Restrictive assumptions: Multi-view volumetric capture studio producing fused 4D textured scans.; Per-subject personalized implicit avatars learned from separate 4D scans of each subject before interaction.; Frames without contact available to fit individual avatars.; Two-person interactions only; offline optimization.

## [1251] 3D Human Pose Estimation via Intuitive Physics (CVPR 2023, dataset, S4 S7)
Source: https://arxiv.org/pdf/2303.18246; confidence HIGH.
Field cannot yet: The field cannot yet enforce physical plausibility for bodies supported by arbitrary, non-planar scene surfaces or in dynamic and multi-person settings from images.
Stated limitations:
- Only body-floor contact is addressed; general scene contact and other supporting surfaces are future work. [5 Conclusion]
- IP terms are designed for static poses; dynamic motions not specifically handled. [5 Conclusion]
- 3DPW violates core assumptions: inconsistent ground planes and dynamic poses. [Sup. Mat. G]
- Only relative pressure is recovered since body mass is not assumed known. [Sup. Mat. E]
Open problems listed:
- General body-scene contact beyond the floor.
- Physics-aware estimation for dynamic motion.
- Multi-person physical plausibility.
- Datasets with rich floor interaction and pressure ground truth were lacking.
Benchmark gaps:
- MoYo / Pressure IoU / CoP error / CoM error: Estimated pressure mIoU 0.32, CoP error 57.3 mm, CoM error 53.3 mm vs ground truth.
- RICH / MPJPE (mm): IPMAN-O* 240.9 mm vs SMPLify-X 268.6 mm; errors remain large.
Restrictive assumptions: Single flat ground plane with gravity perpendicular to it.; Single person.; IPMAN-O uses a known reference ground plane at test time.; Mostly static poses.; MoYo captured with one trained yoga professional, 8 static calibrated cameras, Vicon mocap and pressure mat.

## [1252] Capturing and Inferring Dense Full-Body Human-Scene Contact (CVPR 2022, dataset, S4 S2)
Source: https://arxiv.org/pdf/2206.09553; confidence HIGH.
Field cannot yet: The field cannot yet infer dense 3D contact with moving or hand-held objects jointly with body and object pose from a single image.
Stated limitations:
- Dataset covers only contact with static scenes, not hand-held objects or human-human interaction. [Limitations and future work]
- Training data for BSTRO is limited. [6.3]
Open problems listed:
- Contact with dynamic scenes and hand-held objects.
- Human-human contact.
- Joint object pose estimation and hand/body reconstruction.
- Joint single-network estimation of pose, shape and scene contact.
- Monocular HPS under scene-contact occlusion.
Benchmark gaps:
- RICH-test / TR-MPJPE / TR-V2V (mm): PIXIE 214.0/172.81 mm on frames with scene contact vs 161.81/121.71 mm without.
- RICH-test moving camera / PA-MPJPE (mm): 84.15 mm with contact vs 63.67 mm without.
Restrictive assumptions: Static pre-scanned 3D scenes (laser scanner).; 6-8 static calibrated cameras for pseudo-GT; minimal-clothing body scans of each subject.; Pseudo-ground-truth from markerless fitting, not mocap.; Contact defined against rigid static geometry only.

## [1253] mRI: Multi-modal 3D Human Pose Estimation Dataset using mmWave, RGB-D, and Inertial Sensors (NeurIPS 2022, dataset, S4 S7)
Source: https://arxiv.org/pdf/2210.08394; confidence HIGH.
Field cannot yet: The field cannot yet achieve accurate, subject-independent 3D pose from privacy-preserving mmWave sensing alone.
Stated limitations:
- All algorithms reported are only baselines. [Checklist]
- RGB model evaluated without fine-tuning on mRI; fine-tuning left as future work. [4.1 Results and discussion]
- mmWave results are worse than RGB or IMUs. [4.2]
- Data from healthy subjects only; patient studies are future work. [1 Introduction]
Open problems listed:
- Privacy-preserving pose estimation with mmWave at accuracy comparable to RGB/IMU.
- Generalization to unseen subjects.
- Multi-modal fusion for pose and action detection.
- Extension to patient populations.
Benchmark gaps:
- mRI / MPJPE (mm), P1 S1: mmWave 163.3, RGB 116.9 (no fine-tune), IMU 80.2.
- mRI / mAP at tIoU 0.95: mmWave 29.0, RGB 44.8, IMU 53.6, all-modal 60.6 under P1.
Restrictive assumptions: GT from 2D detection, two-camera triangulation and optimization refinement, not marker mocap.; Single subject, prescribed rehabilitation movements, indoor.; Six body-worn IMUs for the IMU modality.

## [1254] Simultaneously-Collected Multimodal Lying Pose Dataset: Towards In-Bed Human Pose Monitoring under Adverse Vision Conditions (TPAMI 2022, dataset, S4 S7)
Source: https://arxiv.org/pdf/2008.08735 (arXiv v1, 2020 preprint of the TPAMI paper); confidence HIGH.
Field cannot yet: The field cannot yet estimate accurate 3D pose of a fully covered, resting person, with no 3D ground truth to train or evaluate on.
Stated limitations:
- SLP has no 3D pose ground truth. [4 Exploring 3D In-Bed Pose Estimation]
- Heat residue in LWIR cannot be fully eliminated during collection, causing labeling ambiguity. [3.1 Guideline II]
Open problems listed:
- Pose estimation when RGB is ineffective (darkness, covers).
- 3D in-bed pose estimation without 3D ground truth.
- Domain adaptation and transfer learning across modalities.
- Patient action recognition and behavior monitoring.
Benchmark gaps:
- SLP / Qualitative 3D pose: Depth-based pretrained 3D model fails most of the time; no 3D GT to quantify.
Restrictive assumptions: Single viewpoint above the bed, single person.; Labels for covered images obtained from uncovered images of the same held pose (subject remains still).; 2D pose labels only.

## [1255] AthletePose3D: A Benchmark Dataset for 3D Human Pose Estimation and Kinematic Validation in Athletic Movements (CVPRW 2025, dataset, S4 S7)
Source: https://arxiv.org/pdf/2503.07499 (v3); confidence HIGH.
Field cannot yet: The field cannot yet produce monocular kinematics (especially velocities) accurate enough to replace motion capture for fast athletic movement.
Stated limitations:
- Velocity estimation remains a challenge despite good joint-angle correlation. [6 Conclusion]
- All waveforms differ significantly from mocap GT. [5.3]
Open problems listed:
- Monocular pose for high-speed, high-acceleration sports motion.
- Accurate velocity estimation from monocular pose.
- Waveform-level agreement with mocap for biomechanics.
Benchmark gaps:
- AthletePose3D val / MPJPE (mm): TCPFormer 234.20 mm trained on H3.6M; 98.26 mm after H3.6M+AP3D training.
- AthletePose3D / Velocity correlation r: 3D model upper 0.28, lower 0.11; significant waveform differences.
Restrictive assumptions: 3D lifting evaluated with ground-truth 2D pose input.; Multi-camera (4/8/12) hardware-synced calibrated capture for GT, markerless per Table 1.; Single athlete per sequence.

## [1256] UnrealEgo: A New Dataset for Robust Egocentric 3D Human Motion Capture (ECCV 2022, dataset, S4)
Source: https://arxiv.org/pdf/2208.01633; confidence HIGH.
Field cannot yet: The field cannot yet robustly estimate self-occluded lower-body pose from head-mounted egocentric cameras.
Stated limitations:
- Failure cases remain due to occlusions and complex motions. [6 Conclusions]
- Even stereo methods do not perform well on some common daily motions. [5.3]
Open problems listed:
- Egocentric pose under self-occlusion (crouching, bending).
- Complex motions such as breakdance and backflip.
- Using explicit 3D stereo geometry.
- Lack of large-scale stereo egocentric data with in-the-wild imagery.
Benchmark gaps:
- UnrealEgo / MPJPE (mm): Best method 79.06 mm (pretrained) vs EgoGlass 91.44; crouching motions worst.
Restrictive assumptions: Fully synthetic (Unreal Engine, 17 RenderPeople models, Mixamo motions); no real-image evaluation reported.; Stereo fisheye cameras fixed on eyeglasses.; Baselines re-implemented since source code unavailable.

## [1257] Scene-aware Egocentric 3D Human Pose Estimation (CVPR 2023, dataset, S4)
Source: https://arxiv.org/html/2212.11684; confidence HIGH.
Field cannot yet: The field cannot yet produce accurate, physically plausible egocentric full-body pose from one head-worn camera when the body occludes the scene it interacts with.
Stated limitations:
- Pose accuracy is bounded by the estimated scene depth, especially behind the body where the scene is occluded. [5 Conclusion (Limitations)]
- The method works per single frame; temporal extension is left for future work. [5 Conclusion]
- The EgoPW-Scene training set is smaller than EgoPW because SfM reconstruction fails on some sequences. [3.1.2 EgoPW-Scene Dataset]
- Existing egocentric datasets lack camera pose and scene geometry, so human-scene interaction cannot be evaluated on them. [4.1 Evaluation Datasets]
Open problems listed:
- Recovering scene depth behind the body for egocentric views
- Lack of egocentric datasets with scene geometry and camera pose labels
- Temporal egocentric motion with physical plausibility
Benchmark gaps:
- SceneEgo test set (new) / MPJPE / PA-MPJPE (mm): Best result is still 118.5 / 92.75 mm; with ground-truth depth it drops only to 109.9 / 88.8 mm.
- SceneEgo test set (new) / MPJPE (mm): Prior methods Mo2Cap2, xR-egopose, EgoPW score 200.3, 241.3, 189.6 mm.
Restrictive assumptions: Single head-mounted downward-facing fisheye camera; Real test set needs multi-view SfM scene scan and a calibration board rigidly attached to the egocentric camera for ground truth; Method is fine-tuned on the training split of the new test dataset before evaluation; Real-data scene labels come from SfM with scale recovered from known objects (laptops, chairs); Static scene; no object manipulation modelled

## [1258] EgoSim: An Egocentric Multi-view Simulator and Real Dataset for Body-worn Cameras during Motion and Activity (NeurIPS 2024, dataset, S4)
Source: https://arxiv.org/html/2502.18373; confidence HIGH.
Field cannot yet: The field cannot yet estimate drift-free global body pose from body-worn cameras, nor simulate body-worn views of people interacting with objects.
Stated limitations:
- Simulated avatars are animated independently from AMASS, so interactions with other humans or objects are not modelled. [7 Discussion (Limitations of EgoSim)]
- Only four scenes are simulated, limiting generalisation. [7 Discussion (Limitations of EgoSim)]
- A sim-to-real rendering gap remains. [7 Discussion (Limitations of EgoSim)]
- Global root position and orientation remain weak, with cumulative drift on long sequences. [7 Discussion (Future research)]
- Experiments use RGB only. [7 Discussion (Future research)]
Open problems listed:
- Simulated interactions between humans and with objects
- More and more diverse scenes for generalisation
- Sim-to-real rendering gap
- Drift-free global root position and orientation over long sequences
- Using non-RGB modalities: inertial-based pose, depth estimation, semantic scene classification
- Cross-participant generalisation needing more subject diversity
Benchmark gaps:
- MultiEgoView real / Global MPJPE (m): Even best fine-tuned model has 0.33 m global MPJPE and 0.31 m root translation error versus 0.044 m PA-MPJPE.
- MultiEgoView synthetic cross-scene / PA-MPJPE (m): Training on scenes (1)(2) and testing on (3)(4) gives 0.148 vs 0.041 in-scene.
- MultiEgoView real cross-participant / PA-MPJPE / MJAE: 0.060 m and 16.6 deg versus 0.044 m and 10.2 deg on random split.
Restrictive assumptions: Six body-worn cameras at head, pelvis, wrists and knees; Real data captured in one university courtyard that was also scanned for simulation; Ground truth from Xsens IMU suit, synchronised by a clap; Pretraining on 119 h synthetic data required before fine-tuning on real data; Offline 5-second clips at 10 fps and 224x224

## [1259] SynBody: Synthetic Dataset with Layered Human Models for 3D Human Perception and Modeling (ICCV 2023, dataset, S4)
Source: https://arxiv.org/html/2303.17368; confidence HIGH.
Field cannot yet: The field cannot yet obtain accurate layered body, clothing and contact annotations for real images at scale.
Stated limitations:
- Asset balance for body shapes and clothing is not guaranteed, risking bias. [6 Conclusion (Societal Impacts)]
- SMPL annotations cannot be derived directly from SMPL-XL and must be refit. [3.2 Motion Retargeting]
- Loose garments and diverse motions remain challenging for human NeRF methods. [5.2 Human NeRF]
- Contact labels for human-scene interaction are not yet included. [6 Conclusion]
Open problems listed:
- Joint prediction of body and clothing
- Contact labels for human-scene interaction
- Neural rendering of loose garments and diverse motions
- Dataset asset balance and bias in body shapes and clothing
- Accurate SMPL-X annotations for real images are difficult to obtain
Benchmark gaps:
- AGORA validation / MPJPE (mm): Even with SynBody, PARE remains at 169.93 mm MPJPE and HMR at 199.51 mm.
- SynBody NeRF novel identity / PSNR: Generalizable NHP reaches only 22.46 on novel identity versus 25-29 for person-specific views.
Restrictive assumptions: Synthetic monocular RGB only; used as complement to real data, not alone; Motions retargeted from AMASS without object interaction; Procedural clothing attached to SMPL-X surface

## [1260] Putting People in their Place: Monocular Regression of 3D People in Depth (CVPR 2022, dataset, S4)
Source: https://arxiv.org/html/2112.08274; confidence HIGH.
Field cannot yet: The field cannot yet recover metric depth and contact-consistent 3D meshes for many overlapping people from one image without camera intrinsics.
Stated limitations:
- Not trained for diverse weights, gender or ethnicity. [5 Conclusion, Limitations]
- Assumes a constant focal length. [5 Conclusion, Limitations]
- Not designed for large crowds. [5 Conclusion, Limitations]
- No modelling of contact between people; mesh intersections and missed contact occur. [Supp. 5.3 Qualitative Results]
- Fails with heavy occlusion and dense small subjects. [Supp. 5.3 Qualitative Results]
- Weak depth/age labels are inconsistent across annotators and needed trained offline labellers. [Supp. 3 Relative Human Dataset]
Open problems listed:
- Lack of multi-person in-the-wild data with accurate 3D translation annotations
- Depth-height ambiguity across ages
- Modelling contact between multiple people
- Heavy occlusion and dense crowds
- Diversity in weight, gender, ethnicity
Benchmark gaps:
- Relative Human / PCDR0.2 (%): Best method reaches 68.27 overall and only 60.77 for babies, so about a third of depth relations are still wrong.
- Relative Human / PCDR0.2 (%) prior methods: Prior methods score 41.6-57.5 overall and 30-39 for babies.
Restrictive assumptions: Standard camera without radial distortion and fixed field of view (constant focal length); Single RGB image; Relative depth layers and age groups as weak labels rather than metric depth; Moderate numbers of people, not crowds of hundreds

## [1261] TRACE: 5D Temporal Regression of Avatars with Dynamic Cameras in 3D Environments (CVPR 2023, dataset, S4)
Source: https://arxiv.org/html/2306.02850; confidence HIGH.
Field cannot yet: The field cannot yet recover metric-accurate world-coordinate human trajectories from moving monocular cameras with real camera-motion ground truth.
Stated limitations:
- DynaCam videos only approximate real dynamic-camera videos because camera motion is simulated by crops and panorama projection. [3.4 DynaCam Dataset (Limitations)]
- Camera motion is not explicitly estimated; only implied by a world motion map. [4.2 Comparisons]
- Corrected 3DPW results are worse than reported; an evaluation bug in a widely used PA-MPJPE function was found. [6 Erratum]
- Metric accuracy in world coordinates is left as future work. [5 Conclusions]
Open problems listed:
- Disentangling human and camera motion in dynamic-camera videos
- Lack of in-the-wild training data with global trajectories and camera poses
- Tracking through long occlusions in multi-person video
- Metric-scale world-coordinate human motion
- Evaluation-code bugs in widely used PA-MPJPE functions
Benchmark gaps:
- DynaCam / ATE (m): Best ATE is 0.334 m (translating) and 0.475 m (rotating) even after similarity alignment.
- 3DPW test / PA-MPJPE (mm): Corrected TRACE 50.8 mm versus 42.7 mm for D&D and 43.0 mm for CLIFF.
- MuPoTS-3D / HOTA: Best HOTA is only 65.3.
Restrictive assumptions: Monocular RGB video; Training camera motion simulated from static or panoramic videos; DynaCam ground truth is pseudo-labels from 2D pose fitting plus PnP; Global trajectory evaluated after similarity alignment, not metric; GPU memory limits clips to 10 frames in training

## [1262] Benchmarking 3D Pose and Shape Estimation Beyond Algorithms (NeurIPS 2022, benchmark, S4)
Source: https://arxiv.org/html/2209.10529; confidence HIGH.
Field cannot yet: The field cannot yet fairly compare mesh-recovery algorithms because data mixes and noisy pseudo-labels dominate results and accurate diverse test sets are scarce.
Stated limitations:
- Benchmarks are mainly run on HMR only. [7 Conclusion (Future works)]
- Dataset selection and partitions are chosen manually using prior knowledge. [7 Conclusion (Future works)]
- Findings are empirical and not yet explained. [7 Conclusion (Future works)]
- Pseudo-annotated test sets contain visible SMPL errors. [Appendix A]
Open problems listed:
- Automatic selection of training datasets and their contributions
- Fair comparison requires fixed dataset combination, backbone and initialisation
- Need test sets with accurate mocap or simulation SMPL ground truth and large diversity
- Suitability of pseudo-annotated datasets as test benchmarks
- H36M not indicative of generalisation
- Effect of augmentation depends on training-set characteristics
- Explaining why the findings hold
Benchmark gaps:
- 3DPW test / PA-MPJPE (mm): Saturation noted: benchmark is in 50+ mm range; best here 47.3 mm.
- 3DPW / test-set availability: 3DPW is the only large-scale real outdoor dataset with accurate SMPL ground truth.
Restrictive assumptions: Monocular RGB single-person crops; 3DPW-test as main benchmark; SMPL body model only

## [1264] Recovering 3D Human Mesh from Monocular Images: A Survey (TPAMI 2023, survey, S4)
Source: https://arxiv.org/html/2203.01923; confidence HIGH.
Field cannot yet: The field cannot yet reconstruct robust, jitter-free, scene-consistent whole-body meshes with hands under heavy occlusion from monocular input.
Stated limitations:
- Synthetic data lack realism; mocap data are confined to constrained settings. [VIII-A Acquisition of Mesh Annotations]
- Benchmark comparisons are inconsistent across configurations. [IX-B Benchmark Leaderboards]
- Whole-body recovery error rises sharply with hands and face. [IX-B Benchmark Leaderboards]
- Interaction methods depend on pre-defined contact vertices, limiting generalization. [VI Human-Scene Interactions]
Open problems listed:
- Robustness under heavy occlusions; multiple plausible reconstructions or pose distributions
- Long-term motion jitter in video reconstruction
- Reconstruction with scene constraints beyond flat floors
- Learning beyond full supervision with unlabeled data
- Grouped person reconstruction over space and time
- Whole-body mesh recovery with scarce whole-body data and hand occlusion, blur, interaction
- Detailed clothed shape beyond parametric models; over-smoothed and not robust to novel poses
- Lack of realism in synthetic data and limited diversity in mocap data
- Inconsistent evaluation standards across methods
- Interaction methods relying on pre-defined contacts
Benchmark gaps:
- AGORA and EHF / full-body vs body-only error: Errors become much higher when face and hands are included.
Restrictive assumptions: Scope limited to monocular RGB images and videos; Parametric body models SMPL/SMPL-X represent minimally clothed bodies; Scene-aware methods typically assume flat floors or pre-scanned static scenes

## [1265] Deep Learning for 3D Human Pose Estimation and Mesh Recovery: A Survey (Neurocomputing 2024, survey, S4)
Source: https://arxiv.org/html/2402.18844; confidence HIGH.
Field cannot yet: The field cannot yet reconstruct detailed humans together with interacting objects in real time on edge devices under crowding and occlusion.
Stated limitations:
- Top-down methods depend on detection; bottom-up methods struggle with small figures. [4.3 Summary of 3D pose estimation]
- Explicit models lack detail; implicit models lack stability. [5.3 Summary of human mesh recovery]
- Object interaction reconstruction faces pose initialisation and sparse SfM observation problems. [8 Challenges and Conclusion]
Open problems listed:
- Speed: real-time processing on edge and ARM platforms
- Crowding and occlusion in open-world scenes
- Using large models for 3D human tasks
- Detailed reconstruction combining robust pose with fine surface detail
- Reconstructing with the environment and objects: pose initialisation and sparse object observation
- Controllability and animatability of avatars
- Flexibility versus robustness trade-off between implicit and explicit models
- Detection dependence of top-down multi-person methods and small-figure failure of bottom-up methods
Restrictive assumptions: Survey scope 2019-2023 deep learning methods; Mostly RGB monocular and multi-view inputs

## [1266] Deep Learning-Based Human Pose Estimation: A Survey (ACM Computing Surveys 2023, survey, S4)
Source: https://arxiv.org/html/2012.13392; confidence HIGH.
Field cannot yet: Estimate accurate, temporally smooth 3D human pose in the wild under heavy occlusion and scene interaction without lab-captured ground truth.
Stated limitations:
- Survey states 3D HPE ground truth depends on mocap, so datasets are constrained and methods degrade in the wild. [3.3 (3D HPE summary)]
- Performance of 3D HPE drops in crowded scenes due to mutual occlusion and low resolution per person. [3.3]
- Depth and other sensors alleviate ambiguity but need special hardware and are not cost-effective. [1 Introduction]
- Most methods ignore human interaction with 3D scenes. [6 Conclusion and Future Directions]
Open problems listed:
- 2D HPE: reliable detection of individuals under significant occlusion (crowds), and keypoint association in occluded scenes
- 2D HPE: computational efficiency on resource-constrained devices for gaming, AR, VR
- 2D HPE: limited data for rare poses causing model bias
- 3D HPE: model generalization beyond constrained mocap scenes; sim-to-real gap of synthetic data
- 3D HPE: robustness to occlusion in crowded scenes
- 3D HPE: computational cost, including of 2D-to-3D lifting pipelines
- 3D HPE in the wild with unusual poses and occlusions
- Monocular depth ambiguity; multi-view viewpoint association
- Domain adaptation for HPE
- Compact and more expressive human body models
- Human-scene interaction constraints ignored by most methods
- Temporal consistency and smoothness metrics for video 3D HPE
- Resolution mismatch between training and test data
- Adversarial robustness
- Architecture search for heterogeneous body parts and efficiency
Benchmark gaps:
- in-the-wild 3D HPE data / MPJPE (qualitative): Survey states 3D HPE for in-the-wild data with unusual poses and occlusions is still a challenge; SOTA performance degrades off constrained datasets.
- temporal 3D HPE benchmarks / MPJPE: MPJPE cannot evaluate smoothness or realism, so jitter in video 3D HPE is not measured by current benchmarks.
Restrictive assumptions: Most surveyed 3D methods train on mocap-annotated lab datasets with selected common motions; Monocular RGB 3D HPE inherits depth ambiguity; multi-view methods require viewpoint association and calibrated setups

## [1286] OmniPose6D: Towards Short-Term Object Pose Tracking in Dynamic Scenes from Monocular RGB (IROS 2025, dataset, S5)
Source: https://arxiv.org/html/2410.06694; confidence HIGH.
Field cannot yet: Track the 6-DoF pose of an unknown, textureless or occluded hand-held object online from monocular RGB with little motion or large out-of-plane rotation.
Stated limitations:
- Robust tracking in dynamic settings remains challenging, with representative failure cases shown. [H Limitations]
- Pipeline runs offline and keypoint selection needs further work. [H Limitations]
- The pipeline depends on existing segmentation, keypoint tracking and bundle adjustment modules. [VI Conclusion]
- Method assumes rigidity and an initial-frame 2D mask, and only targets a short-term window of a few keyframes. [I Introduction]
Open problems listed:
- Lack of large-scale precise ground truth for dynamic object pose tracking; real datasets focus on hands with little object variety
- Synthetic datasets lack realistic out-of-plane rotation and occlusion
- RGB-only monocular object pose tracking in dynamic scenes is scarce and limited
- No dedicated evaluation metric for short-term object pose tracking (KITTI odometry metrics adopted)
Benchmark gaps:
- YCBInEOAT / ATE/RPE and 5deg/5cm-style accuracy: Noticeable performance decline versus HO3D; straight-line robot motion with little rotation challenges the SfM assumptions.
- DexYCB (S3, subject 0) / pose tracking metrics: Average performance does not match HO3D, attributed to heavy hand occlusion and distant objects.
Restrictive assumptions: Rigid objects only; Manual or given 2D object mask in the first frame; Short-term windows (8 frames), not long-term tracking; Offline processing; Requires sufficient object motion (stationary frames filtered) for SfM; Trained on synthetic data only (OmniPose6D); HO3D evaluation discards depth and downsamples sequences

## [1312] BOP Challenge 2024 on Model-Based and Model-Free 6D Object Pose Estimation (arXiv 2025, benchmark, S5)
Source: https://arxiv.org/html/2504.02812; confidence HIGH.
Field cannot yet: Detect and estimate 6D pose of novel hand-held objects onboarded only from a casual video, accurately and in real time.
Stated limitations:
- Participation on BOP-H3 and model-free tracks was limited; no submissions for model-free 6D detection. [4.1 Experimental setup]
- 2D detection of unseen objects is the main bottleneck of 6D pipelines. [1 Introduction]
- Even sub-second methods need further speed-up for real-time use. [6 Conclusions]
- VSD omitted because HOT3D and HANDAL lack depth. [3.4 Evaluation methodology]
Open problems listed:
- Model-free onboarding of new objects from reference videos (static or dynamic hand-manipulation) remains largely unaddressed
- 2D detection of unseen objects is noticeably behind seen objects and is the main pipeline bottleneck
- Run time: further speed-up needed for real-time applications
- Harder real-world egocentric/AR-VR data (BOP-H3) lowers accuracy
- Adoption effort for new datasets and model-free methods limits participation
Benchmark gaps:
- BOP-Classic-Core / AP (2D detection, unseen): Best 2024 MUSE 52.0 AP vs 79.8 AP for seen-object GDet2023.
- BOP-H3 / AP (model-based 6D detection): GigaPose+GenFlow 31.2 AP on BOP-H3 vs 50.4 on BOP-Classic-Core; BOP-H3 harder.
- BOP-H3 / AP (2D detection): MUSE 39.0 AP on BOP-H3 vs 52.0 on BOP-Classic-Core.
- BOP-Classic-Core / AR and run time (6D localization, unseen): FreeZeV2.1 82.1 AR, near seen-object 85.6, but 24.9 s vs 2.7 s per image.
- BOP-H3 / model-free 6D detection: No submissions for Track 6.
Restrictive assumptions: Onboarding within 5 minutes on one GPU; onboarded representation frozen at test time; Dynamic onboarding provides ground-truth pose only for first frame; static onboarding gives poses for all frames; Rigid objects only; Per-image evaluation, not temporal tracking

## [1313] BOP Challenge 2023 on Detection, Segmentation and Pose Estimation of Seen and Unseen Rigid Objects (arXiv 2024, benchmark, S5)
Source: https://arxiv.org/html/2403.09799; confidence HIGH.
Field cannot yet: Detect occluded novel objects and estimate their 6D pose quickly without a provided CAD model.
Stated limitations:
- Seen-object accuracy saturates but efficiency must improve for real-time use. [6 Conclusions]
- Large gap remains between unseen and seen object detection, especially amodal detection of occluded instances. [4.5]
- Unseen-object methods were given 3D mesh models for onboarding. [6 Conclusions]
Open problems listed:
- Efficiency of top methods for real-time applications
- Detection of occluded objects, especially amodal detection for unseen objects
- Efficiency of unseen-object pose estimation
- Onboarding from reference images only, without 3D models
Benchmark gaps:
- BOP core (7 datasets) / mAP (2D detection, unseen): CNOS-FastSAM 42.8 mAP detection and 41.2 mAP segmentation of unseen objects; 37 mAP gap to GDet2023.
- BOP core / AR and time (6D localization, unseen): GenFlow-MultiHypo16 is best but takes 34.58 s per image; SAM6D fastest at 3.87 s with 61.6 AR.
- BOP core / AR (6D, unseen with seen detections): With seen-object detections, GenFlow reaches 79.2 AR, 5.9 behind GPose2023, showing detection is the limiting stage.
Restrictive assumptions: 3D CAD mesh of each target object available; Onboarding within 5 minutes on 1 GPU; Single RGB or RGB-D image, rigid objects, no temporal tracking; Symmetry transformations not available for MegaPose training objects

## [1314] HANDAL: A Dataset of Real-World Manipulable Object Categories with Pose Annotations, Affordances, and Reconstructions (IROS 2023, dataset, S5 S6)
Source: https://arxiv.org/html/2308.01477; confidence HIGH.
Field cannot yet: Automatically annotate category-level 6D pose of hand-manipulated objects at scale without manual intervention.
Stated limitations:
- Pipeline still has manual bottlenecks: mesh alignment by oriented bounding box and XMem segmentation supervision. [VI Discussion]
- Instant NGP meshes have poor texture and baked lighting, precluding realistic synthetic data. [VI Discussion]
- Articulated objects treated as rigid in a fixed default state. [III-A]
- Dynamic-scene object pose is extremely hard to annotate; uses BundleSDF plus ICP averaged and manual inspection. [IV-C]
Open problems listed:
- Category-level object pose estimation lacks real annotated datasets
- Learning functional affordances (handles) for task-oriented grasping
- Scalable annotation without manual mesh alignment or segmentation supervision
- Annotating object pose in dynamic (hand-manipulated) scenes
- Generating realistic synthetic data from reconstructions (texture, baked lighting, material editing)
- Handling reflective, perforated, thin objects and extreme lighting
- Functional grasps may need anthropomorphic hands; some objects too heavy for robots
- Articulated objects
Benchmark gaps:
- HANDAL (all categories) / 3D IoU>50% and ADD AUC (CenterPose): Total 3D IoU 0.340 RGB-only vs 0.670 with single ground-truth depth; ADD AUC 0.407 vs 0.588.
Restrictive assumptions: Static scenes annotated via camera localization (COLMAP); only some objects have dynamic RGB-D videos; Dynamic annotation relies on BundleSDF and depth ICP; Single object category at a time, rigid default state; Baseline evaluation assumes known object dimensions

## [1315] 6-DoF Pose Estimation of Household Objects for Robotic Manipulation: An Accessible Dataset and Benchmark (IROS 2022, dataset, S5)
Source: https://arxiv.org/html/2203.05701; confidence HIGH.
Field cannot yet: Reliably detect and grasp-accurately localize all known objects in clutter from RGB alone, with about 20% still undetected.
Stated limitations:
- Scanner could not handle objects larger than about 20 cm, limiting object size and materials. [II-B]
- Depth-annotation tool may suffer depth noise or bias; PnP tool error-prone along the projection ray. [II-D]
- Errors along the projection ray are a significant source of error for RGB-only methods. [III-C]
- CosyPose-LS misses nearly 20% of objects; better detection needed. [III-D]
Open problems listed:
- Many open research problems remain in 6-DoF pose estimation though basics are in place
- Benchmark objects are not physically available to most researchers; product appearance changes
- Some benchmark items unsuitable in size, shape, weight for grippers
- Pose metrics: ADD and ADD-S mis-estimate error for symmetric objects; BOP symmetry definition requires visual similarity
Benchmark gaps:
- HOPE test / BOP AR (MSSD/VSD/MSPD): Best CosyPose-LS AR about 0.59-0.69; DOPE variants about 0.23-0.50.
- HOPE test / recall within 2 cm / 10 cm (MeanSSD): CosyPose-LS 72% within 2 cm and 83% within 10 cm; nearly 20% not detected.
Restrictive assumptions: Static scenes (single annotation per scene across lighting variations); Known textured 3D models of 28 specific objects; Objects at 0.5-1.0 m from a single RealSense D415; Training on synthetic images only

## [1316] PACE: A Large-Scale Dataset with Pose Annotations in Cluttered Environments (ECCV 2024, dataset, S5)
Source: https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/06837.pdf; confidence HIGH.
Field cannot yet: Track rigid and articulated objects robustly through heavy clutter and occlusion in real scenes, recovering after loss.
Stated limitations:
- Dataset lacks large and valuable objects due to resource limits. [6 Conclusions and Limitations]
- Marker-based annotation inapplicable to moving objects; BundleTrack used but drifts, needing manual fixes every ten frames. [3.3]
- Notable real-world performance gap, especially for articulated objects, robustness and scalability. [6 Conclusions]
Open problems listed:
- Sim-to-real gap, especially for depth-dependent methods
- Scalability to many instances/categories (underfitting)
- Articulated object pose estimation and tracking
- Robust tracking in clutter and occlusion, recovery after loss
- Annotating moving objects without markers and without drift
- Marker artifacts in data (addressed by inpainting)
- Coverage of large and valuable objects
Benchmark gaps:
- PACE / AR (instance-level): PPF 52.2 AR; CosyPose 4.4, SurfEmb 9.0, GDRNPP 7.0 with ground-truth detections.
- PACE / ADD(-S) AUC (model-based tracking): Best ICG 38.1 rigid and 10.1 articulated; RBOT 7.4/0.5.
- PACE / 5deg 5cm (model-free tracking): Best under 13% (CAPTRA 12.9 rigid); BundleTrack 6.4 rigid.
- PACE / category-level AP: Articulated objects near 0 on most strict metrics.
Restrictive assumptions: Calibrated 3-camera RealSense rig with ArUco markers for annotation; Ground-truth detections/masks and bounding box sizes given to baselines; Initial-frame pose given for tracking; Moving-object annotation semi-manual

## [1317] ClearPose: Large-scale Transparent Object Dataset and Benchmark (ECCV 2022, benchmark, S5)
Source: https://arxiv.org/html/2203.03890; confidence HIGH.
Field cannot yet: Estimate pose of transparent objects in clutter or under covers with accuracy close to opaque objects.
Stated limitations:
- Benchmark omits many SOTA methods due to compute and time limits. [5 Discussions]
- Dataset excludes colored transparent, labelled, or mixed opaque-transparent objects. [5 Discussions]
- Labeling assumes static scenes and textured backgrounds for visual SLAM. [2.1]
- Pose accuracy far below opaque objects. [4.2]
Open problems listed:
- Inconsistent RGB features of transparent objects
- Inaccurate RGB-D depth on transparent materials
- Real-world transparent datasets are small, low clutter, few categories, limited lighting
- Synthetic transparent datasets lack realistic artifacts (syn-to-real gap)
- Heavy clutter, liquid-filled objects, translucent covers
- Multi-layer transparent appearance in detection and segmentation
- Category-level transparent pose
- Transparent object grasping and manipulation
Benchmark gaps:
- ClearPose Opaque Distractor / accuracy (ADD<10cm): FFB6D variants 0.5-2.4%; Xu et al. 42.6%.
- ClearPose Translucent Cover / accuracy: All methods 4.5-14.4%.
- ClearPose New Background / ADD(-S): Best about 58 vs about 90 on opaque datasets.
Restrictive assumptions: Static scenes for annotation; Instance-level CAD models; Single RealSense L515 RGB-D

## [1318] Digital Twin Tracking Dataset (DTTD): A New RGB+Depth 3D Dataset for Longer-Range Object Tracking Applications (CVPR Workshops 2023, dataset, S5 S7)
Source: https://arxiv.org/html/2302.05991; confidence HIGH.
Field cannot yet: The field cannot yet deliver millimetre-accurate RGB-D object pose tracking at room-scale distances under dark or varying lighting.
Stated limitations:
- Dataset scope is limited; authors plan more objects, scenes, backgrounds and newer sensors. [6 Conclusion]
- Scenes are static object arrangements on a flat surface; only the camera moves. [3.1 Scenes]
- Hole filling designed for stereo depth adds interpolation error at longer range and gives unstable FFB6D results. [5.3 Experimental Results and Dataset Analysis]
- Camera-mocap synchronisation relies on ArUco/mocap pose matching, interpolation and Kalman smoothing, described only as generally good. [4.2 Sensor Timestamp Synchronization]
Open problems listed:
- Millimetre-accurate 3D object tracking at 1-2 m observation distance for AR, versus centimetre accuracy sufficient for grasping.
- Robustness to varied and dark lighting conditions.
- Older depth sensors (stereo, structured light) are noisy beyond one metre and leave holes requiring slow hole filling.
- Real-time pose estimation when depth is sparse.
- Existing datasets tolerate annotation errors up to a centimetre without per-frame refinement.
- Synthetic-to-real domain transfer for models trained on synthetic data.
- Learning low-level features of objects at longer range with wider field of view.
Benchmark gaps:
- DTTD / ADD AUC (average): FFB6D 14.33, FFB6D without hole filling 11.56, DenseFusion 51.45, DenseFusion+abc loss 54.54.
- DTTD / ADD-S AUC per object: FFB6D on black_expo_marker 6.67 (0.70 without hole filling); pop-tarts_box ADD AUC 17.46 for DenseFusion.
- DTTD vs YCB-Video / ADD AUC (DenseFusion, overlapping objects): spam_can 38.83 on DTTD vs 79.94 on YCB-V; tomato_can 38.62 vs 87.76; mustard 57.62 vs 94.92.
Restrictive assumptions: Known textured 3D object models (scanned with iPhone Polycam and repaired in Blender).; Static rigid objects; only the camera moves.; OptiTrack motion capture room (10 cameras) plus ArUco marker for ground-truth camera pose.; Single RGB-D camera (Azure Kinect) pushed on a cart to minimise shake.; Ground-truth segmentation masks supplied to DenseFusion at evaluation.; Manual plus ICP per-frame annotation refinement.

## [1319] DTTDNet: Robust 6DoF Pose Estimation Against Depth Noise and a Comprehensive Evaluation on a Mobile Dataset (CVPR Workshops 2025, dataset, S5 S7)
Source: https://arxiv.org/html/2309.13570; confidence HIGH.
Field cannot yet: The field cannot yet estimate object pose to centimetre-level reliability from noisy, low-resolution consumer mobile depth.
Stated limitations:
- Existing methods suffer large accuracy drops from depth noise, which the paper frames as the core gap. [Abstract]
- iPhone LiDAR depth maps are low resolution with large errors; mean depth error is around 0.25 m across objects. [4 iPhone LiDAR data analysis]
- iPhone LiDAR produces long-tail noise at object projection edges when RGB and depth are interpolated. [4 iPhone LiDAR data analysis]
- Dynamic AR object tracking raises new complexities the paper only brings to light. [6 Conclusion]
- BundleSDF fails to reconstruct objects at large distance, low resolution or with too few frames per viewpoint. [5.2 Experimental Results]
Open problems listed:
- Pose estimation robust to low-resolution, non-Gaussian, long-tail mobile LiDAR depth noise.
- Datasets reflecting mobile AR conditions rather than robotic grasping with dedicated depth cameras.
- Robustness under occlusion, varied lighting and geometrically similar objects with distinct textures.
- Finding solutions compatible with inexpensive, widely used depth sensors.
- Object tracking in dynamic AR environments.
Benchmark gaps:
- DTTD-Mobile / ADD AUC (average): ES6D 13.25, BundleSDF 46.86, MegaPose-RGBD 49.02, DenseFusion 69.67, DTTDNet 73.99.
- DTTD-Mobile / ADD AUC per object: DTTDNet black_marker 44.08, pear 47.83, blue_marker 50.88; BundleSDF 0.00 on cereal_box and all three markers.
- DTTD-Mobile / ADD (1cm): Best configuration reaches 25.85 percent ADD(1cm).
- YCB-Video vs DTTD-Mobile / ADD-S AUC on overlapping objects: ES6D drops from 85.67 to 45.20; MegaPose from 88.18 to 63.99; tuna_can MegaPose 91.03 to 22.11.
Restrictive assumptions: Known object with CAD model; CAD point clouds used as Chamfer reference during training.; Input is pre-segmented depth and cropped RGB (segmentation given).; Ground truth from OptiTrack motion capture of the iPhone plus the DTTD annotation pipeline.; Per-object training on a closed set of 18 rigid objects.; iPhone auto-focus disabled to keep intrinsics fixed; depth resized to RGB by nearest neighbour.

## [1320] YCB-Ev 1.1: Event-Vision Dataset for 6DoF Object Pose Estimation (ECCV Workshops 2025, dataset, S5)
Source: https://arxiv.org/html/2309.08482; confidence HIGH.
Field cannot yet: The field cannot yet estimate or even accurately annotate 6DoF object pose directly from event streams under fast motion and low light.
Stated limitations:
- Annotation accuracy is the main limitation, from object model, synchronisation and calibration errors. [5 Conclusion and future work]
- Blinking-counter synchronisation limits RGB-event alignment accuracy to 33 ms. [2.3 RGB and Event data synchronization]
- Camera tracking used for annotation degrades with motion blur and sometimes fails. [2.2 Pose annotations]
- Not all frames have valid ground truth; whitelisting is required. [3.3 Sequences]
- Passive depth mode was forced because the active IR pattern corrupts events, reducing depth resolution. [2 Data capturing and labelling]
- Evaluation excludes pose estimation on event data. [4 Dataset bias experiments]
- RGB-D frame drops create gaps not handled by the supplied programs when transferring poses to events. [3.4 Frame-drops of RGB-D camera]
Open problems listed:
- No established algorithms for object pose estimation on event data.
- Narrowing the synthetic-to-real domain gap does not reduce dataset bias to a satisfactory level; BOP gains may reflect dataset-specific domain randomisation.
- Annotation accuracy limited by object model inaccuracy, event-color synchronisation and camera calibration uncertainty.
- Synchronising asynchronous event streams with frame cameras (hardware triggers not applicable).
- Active depth sensors interfere with event cameras.
- Lack of a standard event data storage format.
- Fast camera motion and low light defeat RGB-based annotation.
Benchmark gaps:
- YCB-Ev (12 YCB-V-matching sequences) / Average recall, 2 cm translation threshold: GDRNPP 8.9 vs 76.4 on YCB-V; CosyPose 41.4 vs 82.5.
- YCB-Ev / YOLOX detection average recall: 50.1 vs 89.8 on YCB-V.
- YCB-Ev / Per-object recall (GDRNPP): 025_mug 0.005, 009_gelatin_box 0.02, 004_sugar_box 0.035.
Restrictive assumptions: Ground truth derived from RGB (CosyPose plus ICG refinement) and transferred to events via stereo calibration.; Fiducial marker board for global camera tracking.; Static object composition per sequence.; Known YCB object meshes.; Passive stereo depth only, because active IR interferes with the event camera.

## [1321] HouseCat6D - A Large-Scale Multi-Modal Category Level 6D Object Perception Dataset with Household Objects in Realistic Scenarios (CVPR 2024, dataset, S5)
Source: https://arxiv.org/html/2212.10428; confidence HIGH.
Field cannot yet: The field cannot yet estimate category-level 6D pose reliably for occluded and photometrically challenging household objects from real sensor depth.
Stated limitations:
- Annotation quality is lower than robot-based acquisition. [Table 2 caption]
- Motion-induced camera pose error remains after time synchronisation; bundle adjustment post-processing is needed. [3.3 Pose Refinement]
- Occlusion handling by current methods is weak; considerable room for improvement. [4 Benchmark and Experiments]
- Sensor depth makes 2D-to-3D lifting inaccurate even with perfect NOCS maps; glass and tube suffer most. [4 Benchmark and Experiments]
- Grasp labels cover only 16 of 41 scenes. [3.6 Scene Statistics]
Open problems listed:
- Lack of datasets that are simultaneously large-scale, accurate and realistic for category-level pose.
- Instance-level methods require object meshes and per-instance networks.
- High intra-class variance for category-level generalisation.
- Occlusion and clutter largely overlooked by current methods.
- Sensor depth errors on photometrically challenging objects corrupt 2D-to-3D lifting.
- Limited viewpoint coverage (upper hemisphere bias) in existing datasets.
- Checkerboards visible in images and annotation bound to depth sensor quality in prior datasets.
- Robot-based annotation limits viewpoints and backgrounds.
- Timestamp offset and motion blur in freely moving camera rigs.
- Real-world grasp generalisation to unseen objects, backgrounds and sensors.
Benchmark gaps:
- HouseCat6D test / 3D IoU25/IoU50 (overall): NOCS 50.0/21.2, FS-Net 74.9/48.0, GPV-Pose 74.9/50.7, VI-Net 80.7/56.4.
- HouseCat6D test / 3D IoU50 per category: VI-Net box 12.7, remote 17.1, tube 36.0; NOCS teapot 0.1, cup 2.0.
- HouseCat6D test / 10 deg 5 cm accuracy: Best baseline VI-Net 29.1; NOCS 4.8.
- HouseCat6D test / Mean IoU75 with GT NOCS and sensor depth: Declines to 22.6 percent.
- Real-world grasping (Franka) / Grasp success rate: Remote 53.3/33.3, unknown objects 53.3/60.0 percent.
Restrictive assumptions: Infrared external tracking system (ARTTRACK2) plus pivot-calibrated tip for object annotation.; Pre-scanned object meshes with structured-light scanner, using vanishing spray for transparent and reflective items.; Static scenes; handheld camera rig with hardware-triggered polarisation and active-stereo cameras.; Benchmarks use ground-truth detection masks for geometry-guided methods.; Ten fixed household categories.

## [1322] PhoCaL: A Multi-Modal Dataset for Category-Level Object Pose Estimation with Photometrically Challenging Objects (CVPR 2022, dataset, S5)
Source: https://arxiv.org/html/2205.08811; confidence HIGH.
Field cannot yet: The field cannot yet estimate category-level pose of transparent and reflective objects, because depth-based lifting breaks on them.
Stated limitations:
- Deformable surfaces such as empty boxes degrade tip-based surface measurement and ICP refinement. [4.3 Limitations]
- Robot workspace limits camera view angles. [4.3 Limitations]
- Low camera resolution makes hand-eye calibration need many more images. [4.3 Limitations]
Open problems listed:
- Annotating 6D pose of textureless, reflective and transparent objects where keypoints cannot be found.
- Commodity depth sensors (structured light, stereo, ToF) fail on reflection and refraction, so RGB-D methods are unreliable.
- Category-level generalisation to novel instances, especially for monocular methods that need large synthetic pretraining.
- Annotation error accumulation across sequences in marker or depth-based pipelines.
- Synthetic training data introduces a domain gap.
- Limited viewpoints in robotic acquisition setups.
- Annotating deformable objects.
Benchmark gaps:
- PhoCaL (seen objects) / 3D IoU25/IoU50 mean: NOCS 43.34/13.91; CPS 61.30/28.69.
- PhoCaL (seen objects) / 3D IoU25/IoU50 per category (NOCS): Teapot 0.00/0.00, glassware 4.00/0.06, cutlery 4.89/0.01.
- PhoCaL (mostly unseen objects) / 3D IoU25/IoU50 mean: NOCS 22.70/0.17; CPS IoU25 4.3.
Restrictive assumptions: KUKA robot arm with mechanical tip for annotation and camera trajectory; stop-and-go capture to avoid motion blur.; Static tabletop scenes of 5-8 objects.; Pre-scanned object models, with vanishing spray for transparent and reflective items.; Robot workspace bounds viewpoints.; Only 12 scenes (24 trajectories).

## [1323] Category-Level 6D Object Pose Estimation in the Wild: A Semi-Supervised Learning Approach and A New Dataset (NeurIPS 2022, dataset, S5)
Source: https://arxiv.org/html/2206.15436; confidence HIGH.
Field cannot yet: The field cannot yet estimate category-level object pose for unseen categories in the wild without per-category shape priors or dense real annotations.
Stated limitations:
- RePoNet may not generalise to unseen categories. [6 Discussion, Limitations]
- Dependence on a pre-defined categorical mesh prior fixes the deformation model per category. [6 Discussion, Limitations]
- Prior models trained on limited real data fail to generalise in the wild. [5.3 Comparison with State-of-the-art Methods]
Open problems listed:
- Limited number and diversity of annotated real data restricts category-level generalisation.
- Annotating 6D object pose is challenging and costly.
- Large-scale video datasets without depth (Objectron, CO3D) leave pose ambiguities; COLMAP depth too erroneous.
- Existing RGB-D scan datasets (3DScan) have objects heavily occluded by hands or only partially visible.
- Generalisation to unseen categories beyond a fixed shape prior.
- Domain gap between synthetic and real data.
Benchmark gaps:
- Wild6D test / 5 deg 2 cm / 5 deg 5 cm / 10 deg 5 cm: Best RePoNet-semi 29.5 / 34.4 / 42.5; Shape-Prior 2.6 / 3.5 / 13.9; CASS 0 / 0 / 0.
- REAL275 / 5 deg 2 cm: RePoNet-semi 30.7 vs SGPA 35.9 (fully supervised).
Restrictive assumptions: Pre-defined category mesh prior for each of 5 categories.; Foreground masks from pre-trained Mask R-CNN for real-data silhouette loss.; Fully annotated synthetic data (CAMERA25) for supervision.; RGB-D input from iPhone front camera.; Test annotations via keyframes every 50 frames propagated with TEASER++ and colored ICP.

## [1324] OnePose: One-Shot Object Pose Estimation without CAD Models (CVPR 2022, dataset, S5)
Source: https://arxiv.org/html/2205.12257; confidence HIGH.
Field cannot yet: The field cannot yet estimate CAD-free object pose for textureless objects or under extreme scale change from a casual video scan.
Stated limitations:
- Reliance on local feature matching causes failure on textureless objects. [5 Conclusion, Limitations]
- Extreme scale change between scan video and test sequence is hard to handle. [5 Conclusion, Limitations]
- A known 2D bounding box is assumed at localization time. [4.2 Implementation Details]
Open problems listed:
- High-quality CAD models of everyday objects are often inaccessible.
- Category-level methods need many annotated samples per category and generalise poorly to instances with very different shape or appearance.
- Training and deploying a network per category is unaffordable for mobile AR.
- Visual localization pipelines take seconds per frame and cannot track moving objects in real time.
- Obtaining masks for instance-level training requires time-consuming dense reconstruction.
Benchmark gaps:
- OnePose / 1cm-1deg success: Large objects 0.471, medium 0.629, small 0.405.
- OnePose / Runtime: HLoc (SPP+SPG) 618 ms vs OnePose 58 ms per frame for matching.
- OnePose (selected objects) / 5cm-5deg: PVNet 0.042-0.253.
Restrictive assumptions: A pose-annotated video scan of each object is available to build a sparse SfM model.; Known 2D object bounding box from an external detector.; Static rigid objects; reference poses from ARKit plus manual 3D box and bundle adjustment.; Monocular RGB, textured objects.

## [1325] OnePose++: Keypoint-Free One-Shot Object Pose Estimation without CAD Models (NeurIPS 2022, dataset, S5)
Source: https://arxiv.org/html/2301.07673; confidence HIGH.
Field cannot yet: The field cannot yet perform detector-free, CAD-free object pose estimation that holds up under low resolution and extreme viewpoint or scale change.
Stated limitations:
- Local feature matching suffers on very low-resolution images and extreme scale and viewpoint changes. [5 Conclusion, Limitations]
- A separate object detector is still required for regions of interest. [5 Conclusion, Limitations]
Open problems listed:
- Pose estimation of low-textured objects without CAD models.
- Inconsistent keypoints and fragmentary tracks from detector-free matchers do not suit SfM.
- Most methods rely on CAD models or per-category training.
- Gen6D-style methods need accurate bounding boxes, hard under poor image quality and occlusion.
- Instance-level methods are susceptible to domain gaps from synthetic training.
Benchmark gaps:
- OnePose-LowTexture / 1cm-1deg / 3cm-3deg / 5cm-5deg: Best method 16.8 / 57.7 / 72.1; OnePose 12.4 / 35.7 / 45.4.
- LINEMOD / ADD(S)-0.1d average: OnePose++ 76.9 vs CDPN 91.4 (instance-level); OnePose 63.6.
- OnePose-LowTexture (CAD subset) / ADD(S)-0.1d: Object 0740: 57.6 vs PVNet 61.3.
Restrictive assumptions: Reference video (about 200 images) with annotated object poses per object.; Separate 2D detector (YOLOv5) for rough bounding boxes.; Static rigid objects.; Monocular RGB.

## [1326] Gen6D: Generalizable Model-Free 6-DoF Object Pose Estimation from RGB Images (ECCV 2022, dataset, S5)
Source: https://arxiv.org/html/2204.10776; confidence HIGH.
Field cannot yet: Estimate accurate 6-DoF pose of an unseen object from RGB alone under severe occlusion or from viewpoints its reference capture did not cover.
Stated limitations:
- Generalization relies on learned image matching, so performance drops with limited training data. [4.6 Analysis, Limitations]
- Not designed for occlusion; accuracy may degrade under severe occlusion. [4.6 Analysis, Limitations]
- Without training on the object, depth (translation along the viewing ray) is poorly estimated for small, far objects, so it trails instance-specific methods trained on real data on LINEMOD. [4.4 Results on LINEMOD]
- Poses from viewpoints not covered by the reference images cannot be predicted accurately. [Supplementary 0.E.3]
Open problems listed:
- Model-free pose for unseen objects needs diverse training data for general image matching.
- Occlusion handling in model-free generalizable pose estimation.
- Accurate depth/scale estimation for unseen objects from RGB only.
- Pose estimation from viewpoints not covered by reference images.
Benchmark gaps:
- GenMOP / ADD-0.1d: Average 50.39; PlugEN only 19.63 and Scissors 32.76, below instance-specific PVNet on Piggy and Scissors.
- LINEMOD / ADD-0.1d: Performs worse than instance-specific estimators trained on real data; matches them only with ground-truth bounding boxes.
- GenMOP (partial reference views) / Prj-5: 35.56 with references in one half-space versus 82.64 with even coverage.
Restrictive assumptions: Requires a set of posed reference images of the object (poses from COLMAP plus manual keypoint alignment in GenMOP).; Reference images should be distributed evenly around the object.; Rigid object; single object per query detection.; Large diverse synthetic and real training corpus (ShapeNet, GSO renders) for the matching networks.; Static per-frame estimation; no temporal tracking or hand-object interaction modeled.

## [1327] Unseen Object 6D Pose Estimation: A Benchmark and Baselines (arXiv 2022, benchmark, S5)
Source: https://arxiv.org/html/2206.11808; confidence HIGH.
Field cannot yet: Reliably estimate 6D pose of novel objects from a single RGB-D view, even with a mesh supplied, especially for small objects.
Stated limitations:
- Benchmark training set built on GraspNet-1Billion has only 40 real objects, judged too few for learning model-agnostic features, so synthetic data are added. [5 Implementation Details]
- IADD for objects with infinite rotational ambiguity is computed by sampling, a precision-efficiency trade-off; for infinite axes it falls back to center distance. [6.1 Metric]
- Registration-based baselines fail when a partial-view scene cloud must be aligned to a full object mesh (low overlap). [2.1 Related Works]
Open problems listed:
- Estimating 6D pose of novel objects without retraining given only their mesh.
- A unified metric for objects with finite and infinite pose ambiguity (ADD-S not comparable to ADD; ACPD/MCPD fail with infinite ambiguity).
- Registering a partial-view scene point cloud to a full object mesh with low overlap.
- Learning model-agnostic correspondence features from limited real object diversity.
Benchmark gaps:
- GraspNet-1Billion novel subset / IADD AUC: Best method reaches only 23.7, versus 36.3 on seen objects.
- YCB-Video (no retraining) / IADD AUC: Best method reaches 19.0; ADD AUC 17.8.
- GraspNet-1Billion all subsets / ADD AUC: Conventional and learned registration baselines score 1.5-13.5 AUC.
Restrictive assumptions: Requires the object's mesh model at test time (no retraining).; Single-view RGB-D colored point cloud input from depth sensors.; Rigid table-top objects; static single frames, no tracking.; Heavy synthetic training data (BlenderProc, Google Scanned Objects).

## [1328] Open Challenges for Monocular Single-shot 6D Object Pose Estimation (arXiv 2023, position, S5)
Source: https://arxiv.org/pdf/2302.11827v1 (v2 is withdrawn by the author; v1 PDF read); confidence HIGH.
Field cannot yet: Estimate monocular 6D pose of novel, transparent, metallic, deformable or articulated objects reliably in open-world robotic settings.
Stated limitations:
- The occlusion-handling conclusion rests on few data points. [II-B Occlusion Handling]
- Domain shift conclusions are tentative. [II-A Domain Shift]
- Benchmarks exclude open-world robotics problems. [III Future Research Trends]
- Paper v2 was withdrawn by its author on 20 Jul 2023. [arXiv abstract page]
Open problems listed:
- Domain shift (largely alleviated but needs confirmation).
- Occlusion handling as a general property of good methods.
- Replacing standard correspondence-based pose representations.
- End-to-end training to replace PnP and refinement.
- Monocular pose refinement without depth/ICP.
- Symmetry handling without known symmetries.
- Category-level generalization.
- Novel object pose estimation.
- Multi-object learning and data imbalance.
- Challenging materials: metallic and transparent objects.
- Beyond supervised learning to cut annotation effort.
- Geometric representations and physical plausibility.
- Deformable and articulated objects, needing canonical poses and metrics.
Benchmark gaps:
- BOP T-LESS / TUD-L / YCB-V / AR (PBR-only vs PBR+real): PBR-only training trails PBR+real by up to 19.6% on YCB-V and TUD-L for selected methods.
- BOP core datasets / coverage: Six of seven core datasets are opaque and diffuse; only one includes metallic surfaces.
Restrictive assumptions: Review scope limited to single-shot monocular RGB, 2021-2022 publications from selected venues (34 papers).; Reviewed methods mostly assume rigid objects with known models and known symmetries.

## [1359] MINT / EgoPipeline: world-space camera and hand pseudo-labels from public videos (arXiv 2026, dataset, S6 S1)
Source: https://arxiv.org/html/2609.04958; confidence HIGH.
Field cannot yet: Recover drift-free, metrically scaled world-space hand trajectories from monocular egocentric video over long sequences without dedicated sensors.
Stated limitations:
- Scale drift from monocular reconstruction in the pseudo-label pipeline persists. [Limitations and future work]
- The 32-frame training window leaves long-horizon drift unsolved. [Limitations and future work]
- Without loop closure or global optimization, absolute trajectory error accumulates; dedicated systems stay ahead. [V-C Camera Trajectory]
- EgoPipeline's multi-model cascade is costly and propagates errors. [III EgoPipeline]
Open problems listed:
- Metric-scale world-space hand and camera trajectories from monocular egocentric video.
- Long-horizon drift beyond short windows.
- Scarcity of accurate world-space hand supervision outside lab captures.
- Error propagation in cascaded egocentric pipelines.
- Lab datasets (DexYCB, HOT3D, ARCTIC) have limited motion, interaction and scene coverage.
Benchmark gaps:
- HOT3D (zero-shot) / CT-p (hand translation): 0.196 m, versus 0.069 m on ARCTIC.
- HOT3D / Arc-length ratio: 0.466 without stage 2; 1.094 with it.
- HOT3D / RPE-T: 4.690 mm, second to MegaSaM.
- ARCTIC / MPJPE-p: Behind WiLoR on millimetre metrics.
Restrictive assumptions: Monocular egocentric RGB; scale from monocular depth priors.; Needs a small in-house metric camera-trajectory corpus from a single rig for scale.; Hands only (MANO); objects not reconstructed.; Clips filtered to at most two hands.; 32-frame windows; no loop closure.

## [1363] ACE-Data-0: synchronized ego/exo full-body, hand, object-pose, audio and tactile episodes (arXiv 2026, dataset, S6 S2 S3 S1)
Source: https://arxiv.org/html/2607.28625; confidence HIGH.
Field cannot yet: Recover drift-free world-space hand, body and object motion with contact in long, cluttered real-home activities from video alone.
Stated limitations:
- Only two sites, limiting variation in layout, furnishing and lighting. [6 Conclusion, Limitations]
- Ground truth only for instrumented, pre-scanned, marker-fitted objects; no annotation of articulated, fluid or deformable state changes. [6 Conclusion, Limitations]
- Mocap suit, gloves, headset and markers are visible and may give dataset-specific cues. [6 Conclusion, Limitations]
- Object pose estimation not benchmarked; too few applicable methods. [5.2 Scene Components]
Open problems listed:
- Fragmented modalities across datasets (no ego plus body plus object plus audio plus touch).
- Unnatural lab environments lacking real occlusions and clutter.
- Short-horizon HOI clips versus minutes-long household activities.
- Tactile pressure distribution from vision under occlusion.
- Global body trajectory drift in long home sequences.
- Egomotion as the main error source for egocentric world-space hands.
- Exocentric hand occlusion by body and objects.
- Too few methods for object pose in home scenes.
- Fusing ego and exo views.
- Annotating articulated, fluid and deformable state changes.
- Site diversity and visible capture equipment.
Benchmark gaps:
- ACE-Data-0 ego-view tactile / C-IoU / V-IoU / CoP: PressureVision near-zero overlap; best (TouchAnything) still modest.
- ACE-Data-0 ego-view hands / World trajectory error: Dyn-HaMR and HaWoR about 98-102 mm.
- ACE-Data-0 exo-view hands / PA-MPJPE / trajectory error: 9.1-10.8 mm PA-MPJPE; best trajectory error 63 mm (HaPTIC).
- ACE-Data-0 room-scale body / WA-MPJPE vs PA-MPJPE: Global trajectory errors much higher than local pose errors; multi-view does not beat best single-view.
Restrictive assumptions: Optical mocap (12-16 cameras), marker suits, Manus gloves, tactile gloves, multi-camera rigs.; Objects pre-scanned and marker-fitted.; Table-scale hand GT from multi-view triangulation plus manual refinement.; Evaluated baselines use released checkpoints without fine-tuning.

## [1369] FastUMI-100K: Advancing Data-driven Robotic Manipulation with a Large-scale UMI-style Dataset (arXiv 2025, dataset, S6)
Source: https://arxiv.org/html/2510.08022; confidence HIGH.
Field cannot yet: Train policies that complete long-horizon multi-stage tasks from wrist-only handheld demonstrations without stage confusion and drift.
Stated limitations:
- T265 tracking can show sudden jumps or global scale distortion; such trajectories are auto-flagged and deleted. [III-B3 Post-Data Collection]
- Human-collected data may exceed small robot workspaces; Wash Clothes is fully outside the Xarm6 workspace. [V-B Cross-platform Deployment]
- No fixed third-person view, so similar wrist observations across stages confuse long-horizon inference. [V-C Fine-tuning on VLA]
- Diffusion Policy cannot handle long-horizon tasks, so tasks were split into subtasks. [V-A Single-task Imitation Learning]
Open problems listed:
- Scalable collection of complex, fine-grained, dual-arm, long-horizon data.
- Vision-driven demonstrations lack robot actions and force/contact data.
- Teleoperation is costly and hardware-coupled.
- SLAM/VIO drift and scale distortion in handheld capture.
- Workspace mismatch between human demos and robots.
- Long-horizon inference under ambiguous wrist-only observations.
Benchmark gaps:
- FastUMI-100K Heat Food (Flexiv Rizon4, pi0) / Stage success rate: Put bread into microwave 0.00% and close door 0.00% after 100% door opening.
- FastUMI-100K Wash Clothes / Stage success rate: Close washer door 60.00%.
- FastUMI-100K short-horizon (Xarm6, pi0) / Success rate: Open Container 73.33%, lowest of nine.
Restrictive assumptions: Pose from RealSense T265 VIO initialized from fixed 3D-printed slots at known spacing to get relative arm poses.; Wrist fisheye views only; no third-person or depth view.; Gripper end-effector trajectories, not human hand or object poses.; Approximate ROS time sync.

## [1370] HiFi-UMI: Learning Deployable Manipulation Policies from High-Fidelity UMI Data Alone (arXiv 2026, dataset, S6 S3)
Source: https://arxiv.org/html/2607.25895; confidence HIGH.
Field cannot yet: Specify what tracking fidelity robot-free demonstrations need, or capture drift-free long-horizon poses during manipulation without the static-world assumption.
Stated limitations:
- Evidence covers only four tabletop bimanual tasks and three backbones; generality untested. [7 Discussion, Limitations and Future Work]
- 40 rollouts per task-policy pair limits task-level resolution. [7 Discussion, Limitations and Future Work]
- Fidelity factors are not isolated; required fidelity per factor is unknown. [7 Discussion, Limitations and Future Work]
- Parity is not sample-matched: UMI uses about ten times more demonstrations. [7 Discussion, Limitations and Future Work]
- Manipulation breaks the static-world assumption, so no loop closure; global drift is bounded only to centimetre level. [3.3.2 Trajectory Reconstruction]
Open problems listed:
- How much trajectory accuracy, inter-gripper pose, synchronization and FoV a deployable policy needs.
- Which interaction dynamics matter and when coverage saturates.
- Whether pre-training gains saturate.
- Whether UMI pre-training helps teleoperation post-training.
- Generality across tasks, embodiments and distribution shifts.
- Recovery and regrasp coverage for contact-rich tasks.
- Deformable-object supervision for transfer.
Benchmark gaps:
- Four-task real-robot suite (StarVLA-QwenPI, OpenPI-pi0.5) / Success rate: UMI-only post-training Shirt Folding 52.5% (StarVLA); Remote Insertion 52.5%.
- Four-task real-robot suite (LingBot-VA WAM) / Aggregate success: 56.9% UMI vs 57.5% teleop; Remote Insertion 42.5%.
- Ten unseen tasks (offline) / Action error: Garment folding remains the most difficult.
Restrictive assumptions: Head-mounted stereo-inertial SLAM with marker cubes on each gripper visible to the head cameras.; Offline SLAM processing, not real-time.; Parallel-jaw glove grippers, not human finger articulation.; Tabletop bimanual tasks for evaluation.

## [1371] YUBI: Yielding Universal Bidigital Interface for Bimanual Dexterous Manipulation at Scale (arXiv 2026, dataset, S6 S3)
Source: https://arxiv.org/html/2606.10244; confidence HIGH.
Field cannot yet: Capture and learn sub-millimeter, contact- and force-sensitive bimanual manipulation from handheld demonstrations.
Stated limitations:
- Sub-millimeter precision and tactile-sensitive tasks remain challenging. [7 Limitations and Discussion]
- How to combine YUBI data with in-the-wild and real-robot data is open. [7 Limitations and Discussion]
- Full 8434-hour corpus not yet used for large-scale VLA pretraining. [7 Limitations and Discussion]
- Robot velocity and acceleration limits are tighter than human demonstrations, so commands are downsampled. [6 Robot Policy Deployment]
Open problems listed:
- Sub-millimeter precision tasks such as tight cable insertion.
- Tactile-sensitive and fragile material handling.
- Optimal mixing of handheld, in-the-wild and real-robot data.
- Large-scale VLA pretraining on handheld data.
- SLAM drift, scale ambiguity and failure under fast motion or low texture.
- Head-worn VR fatigue for long sessions.
- Lightweight portable capture for whole-body tasks.
Benchmark gaps:
- YUBI nut dexterity test / Single-attempt success (M3): YUBI 44%, UMI 14%.
- Bimanual UR deployment / Success over 20 rollouts: Unfold glasses 9/20; stack cup pyramid 13/20.
- Robot deployment (Franka/ELEY) / Success over 20 rollouts: Lowest task 11/20 (cup placement).
Restrictive assumptions: Meta Quest 3S controller tracking from a fixed rig-mounted headset (stationary tabletop primary mode).; Two-finger parallel-jaw gripper, not human hand articulation.; Same YUBI gripper must be fitted to the robot as end-effector.; No object pose or contact force recorded; vision plus gripper trajectories.

## [1372] UMI-Bench 1.0: An Open and Reproducible Real-World Benchmark for Tabletop Robotic Manipulation with UMI Data (arXiv 2026, benchmark, S6)
Source: https://arxiv.org/html/2606.10382; confidence HIGH.
Field cannot yet: Current UMI-trained policies cannot reliably complete long-horizon or tight-placement manipulation or generalize to geometric and dynamics shifts in the real world.
Stated limitations:
- Tabletop only; no mobile manipulation, large workspaces or complex long-horizon scenarios. [6 Limitation]
- Data scale is small relative to large robot datasets. [6 Limitation]
- Real-world evaluation still subject to reset, calibration, lighting and timing noise. [6 Limitation]
- Domain-transfer explanation for DreamZero weakness is an untested hypothesis. [Appendix E (DreamZero's mixed profile)]
Open problems listed:
- Long-horizon stage estimation from a single ambiguous wrist view
- Tight final-placement accuracy under error accumulation
- Generalization to changes in task-relevant geometry or dynamics (policies rely on demonstration-aligned motion priors)
- Mobile manipulation, large workspaces and complex long-horizon scenarios not covered
- Limited data scale versus large robot datasets
- Residual evaluation noise from operator reset, calibration drift, lighting and hardware timing
Benchmark gaps:
- UMI-Bench 1.0 T3 (tool-mediated stamping) / Full Success Rate: 0% FSR for all three models; best progress score 34.30 (DreamZero).
- UMI-Bench 1.0 T9 (long-horizon rearrangement) / Full Success Rate: 0% FSR for all models; overall progress scores 10.6-26.4.
- UMI-Bench 1.0 (all tasks) / Progress Score under combined unseen object and position: Mean drops from 59.62 (seen/seen) to 40.19 under combined shifts.
- UMI-Bench 1.0 overall / Overall Score: Best model averages 55.84 of 100 across ten tasks.
Restrictive assumptions: UMI-style wrist-view fisheye observation interface and standardized hardware platform; Tabletop scenes with operator-performed scene reset; Local-first evaluation on fixed workstations

## [1374] OpenEgo: A Large-Scale Multimodal Egocentric Dataset for Dexterous Manipulation (arXiv 2025, dataset, S6 S1)
Source: https://arxiv.org/html/2509.05513; confidence HIGH.
Field cannot yet: The field lacks a fully verified, occlusion-complete, unified egocentric hand-pose and language corpus, and long-horizon dexterous hand-trajectory prediction remains inaccurate.
Stated limitations:
- Hand joints missing in some frames due to occlusion or absent labels. [5 Conclusion (Limitations)]
- Language annotations auto-generated and only partially verified; temporal drift possible. [5 Conclusion (Limitations)]
- For sources without dexterous labels, 3D joint quality depends on landmark estimator and depth. [5 Conclusion (Limitations)]
- Experiments use only 0.1% of the data and one architecture. [5 Conclusion (Limitations)]
Open problems listed:
- Missing hand joints under occlusion
- Unverified automatically generated language annotations with temporal drift
- 3D joint quality for sources without native dexterous labels
- Lack of upper-bound results at full data scale or with other architectures
- Privacy and surveillance misuse risk of egocentric video
Benchmark gaps:
- OpenEgo held-out split / AED / FED / DTW (3D hand trajectory, 15 fps): At 4.0 s horizon AED 0.1045, FED 0.1076, DTW 6.7975; errors rise steadily with horizon.
Restrictive assumptions: Aggregates six existing datasets; inherits their sensing and annotation quality; Hand poses expressed in camera frame only; no object pose annotations; Training on a 0.1% subset due to compute limits

## [1375] DexCanvas: Bridging Human Demonstrations and Robot Learning for Dexterous Manipulation (arXiv 2025, dataset, S6 S1)
Source: https://arxiv.org/html/2510.15786; confidence HIGH.
Field cannot yet: The field cannot obtain physically grounded hand-object contact forces at scale from vision alone, without markers, CAD objects and per-sequence simulation policies.
Stated limitations:
- Coverage restricted to basic geometric objects and fundamental primitives. [6 Discussion and Conclusion]
- Per-object-manipulation RL policy training does not scale. [6 Discussion and Conclusion]
- Only human hand data released; no robot retargeting yet. [6 Discussion and Conclusion]
- RGB-D streams unexplored; language annotations minimal. [6 Discussion and Conclusion]
- Cross-dataset and downstream experiments not yet provided. [5 Experiments]
- Force estimation from observation alone is under-constrained. [A.2.3]
Open problems listed:
- Scaling beyond basic geometric objects and primitives to real-world assets and composed skills
- Unified policy replacing thousands of per-object policies
- Cross-morphology retargeting preserving contact dynamics
- Exploiting RGB-D for perception; minimal language annotation
- Force estimation from vision is under-constrained; sensors alter contact mechanics; distributed whole-hand contact capture infeasible
Benchmark gaps:
- DexCanvas 32 representative object-manipulation pairs / Simulation reproduction success rate: 80.15% nominal; 62.54% with 20% object-size pose perturbation.
Restrictive assumptions: Room-scale optical mocap with 22 infrared cameras and reflective markers on hand and objects; Right hand only (14 markers on right hand); Objects 3D-printed from CAD models with carved marker mounts (known object geometry); Forces derived from physics simulation (IsaacGym), exact only up to simulation accuracy, not measured; Per-participant hand calibration sequences

## [1376] World In Your Hands: A Large-Scale and Open-Source Ecosystem for Learning Human-Centric Manipulation in the Wild (arXiv 2025, dataset, S6)
Source: https://arxiv.org/html/2512.24310; confidence HIGH.
Field cannot yet: The field cannot yet obtain verified, accurate 3D hand action labels from in-the-wild egocentric capture without instrumented gloves, mocap validation and manual review.
Stated limitations:
- No tactile sensing; limited embodiment and category coverage in policy evaluation. [5 Conclusion and Limitations]
- In-the-wild data lacks motion-capture ground truth; quality is checked by reprojection consistency only. [3.3 Data Validation and Quality Control]
- Unverified ego data gives little gain; noisy labels offset scale. [4.2 Results and Analysis]
Open problems listed:
- Limited scenario diversity in lab-collected datasets
- Missing aligned supervision (calibration, accurate 3D hand/wrist motion, masks, task language)
- Insufficient policy-level evaluation of egocentric datasets
- Annotation quality control: unverified labels erase the benefit of scale
- No tactile sensing
- Fine-grained embodied spatial understanding and progress modeling in VLMs
Benchmark gaps:
- WIYH Human-centric Vision-Language benchmark / Spatial Referring / Completion Verification: Spatial referring remains difficult for all VLMs; completion verification only slightly above 50% random.
- Task-matched co-training (real robot) / Success rate: Single-object with 200 robot clips plus 800 ego clips reaches only 23.3%.
- Real-robot transfer (rose insertion, gift packing) / Success rate: With pretraining 70% average; unseen bottle 3/6.
Restrictive assumptions: Custom wearable Oracle Suite: chest-mounted multi-camera module, Manus data gloves with IMUs and fisheye cameras, backpack compute; Gloved hands (glove appearance differs from bare hands); Wrist accuracy (<5 mm) validated only in a mocap room; offline SfM refinement; Atomic segmentation needs human verification

## [1377] Open-AoE: An Open Egocentric Manipulation Dataset and Toolchain for Embodied Learning (arXiv 2026, dataset, S6)
Source: https://arxiv.org/html/2607.14183; confidence HIGH.
Field cannot yet: The field cannot yet verify the accuracy of hand and camera annotations recovered at scale from commodity monocular smartphone video.
Stated limitations:
- Distribution statistics computed from a 100-hour sample; diversity benefit unvalidated. [3.6 Data Distribution Analysis (Scope and claim boundary)]
- Annotation-consistency comparison is not a controlled accuracy benchmark. [5.3 Image-Annotation Consistency]
Open problems listed:
- Fragmented dataset-specific processing pipelines lacking unified infrastructure
- Specialized capture hardware limits accessibility
- Passive video lacks hand motion, camera trajectory, action boundaries and physical structure
- Unvalidated benefit of camera-domain diversity
- No controlled benchmark of annotation accuracy across datasets
Restrictive assumptions: Monocular consumer smartphone RGB; hand poses estimated (HaWoR, MANO), not measured; Metric scale from SLAM; no depth sensor; No released object pose annotation; object 6-DoF must come from downstream tools; Both hands must remain clearly visible

## [1378] HumanNet: Scaling Human-centric Video Learning to One Million Hours (arXiv 2026, dataset, S6)
Source: https://arxiv.org/html/2605.06747; confidence HIGH.
Field cannot yet: The field cannot yet convert internet-scale human video into reliable, accurately annotated robot supervision that closes the embodiment gap.
Stated limitations:
- Embodiment gap remains despite scale. [6 Limitations, Ethics, and Broader Impact]
- Scale introduces label, boundary, metadata and quality noise; automated annotations carry errors. [6 Limitations, Ethics, and Broader Impact]
- Coverage is uneven and biased. [6 Limitations, Ethics, and Broader Impact]
- Privacy and safety issues from bystanders, interiors and documents. [6 Limitations, Ethics, and Broader Impact]
- No new human-to-robot transfer experiments reported. [4 Downstream Relevance]
Open problems listed:
- Embodiment gap between human and robot control spaces
- Noise from ambiguous labels, inconsistent task boundaries, missing metadata, viewpoint imbalance and variable quality
- Errors in automated captions, pose estimates and motion annotations
- Uneven coverage and geographic, socioeconomic and body-type bias
- Privacy, safety and licensing of human-centric video
- Dual-use and surveillance risk
Benchmark gaps:
- LingBot-VLA post-training, five held-out task groups / Validation loss: 1,000 h egocentric pretraining only matches or slightly surpasses 100 h real-robot data; does not match the 20,000 h robot baseline.
Restrictive assumptions: Internet and self-collected monocular RGB video; 3D hand/body pose estimated, not measured; Validation only by VLA validation loss, not task success

## [1379] EgoLive: A Large-Scale Egocentric Dataset from Real-World Human Tasks (arXiv 2026, dataset, S6)
Source: https://arxiv.org/html/2604.23570; confidence HIGH.
Field cannot yet: The field lacks quantitatively validated 3D hand and object annotation for in-the-wild egocentric capture at scale.
Stated limitations:
- Depth error grows with distance; low error claimed only within typical human operation range. [4.2 Depth Reconstruction]
Open problems listed:
- Restricted environmental diversity of existing robot datasets
- Poor extensibility of teleoperation and UMI collection
- Gap between human behavior and robot action
Benchmark gaps:
- EgoLive calibration room / Depth mean error (mm): 3.06 mm at 500 mm but 13-18 mm beyond 1700 mm; under 80% of points within the tightest threshold beyond 900 mm.
Restrictive assumptions: Custom head-mounted stereo RGB device with IMU (JoyEgoCam); Hand pose from HaMeR monocular estimation refined by stereo optimization (no ground truth); No object pose annotation; objects get masks only; Depth from learned stereo (FoundationStereo)

## [1380] SABER: A Scalable Action-Based Embodied Dataset for Real-World VLA Adaptation (arXiv 2026, dataset, S6 S2)
Source: https://arxiv.org/html/2605.09613; confidence HIGH.
Field cannot yet: The field cannot yet convert human retail demonstrations into robot policies that reliably succeed at precise grasps of small packaged items, even in simulation.
Stated limitations:
- Evaluation in simulation only. [8 Discussion (Limitations)]
- Body-pose stream is small. [8 Discussion (Limitations)]
- Stream-type conditioning is one design choice; alternatives untested. [8 Discussion (Limitations)]
- Frozen vision encoder limits domain-specific perception. [9.1 Future Work]
- No per-stream ablation. [8 Discussion]
Open problems listed:
- Domain-specific data gap for retail deployment
- Real-robot validation absent
- Small whole-body pose stream
- Gradient conflict and negative transfer between streams
- Frozen vision encoder limits domain perception
Benchmark gaps:
- RoboBenchMart (10 tasks) / Success rate: SABER-MM mean 29.3%; non-fridge mean 13.8%; Nestle 2%, Duff 10%, Vanish 11%.
- RoboBenchMart non-fridge tasks / Task Progress P (full success): Mean 0.146 after post-training.
Restrictive assumptions: Hand landmarks require frame-by-frame manual correction by trained annotators; Whole-body SMPL needs a fixed 360-degree exocentric camera and manual correction; Evaluation only in RoboBenchMart simulation; Robot-native anchor data needed

## [1381] HuRo: Robotizing Human Videos for Scalable VLA Pretraining (CoRL 2026, dataset, S6)
Source: https://arxiv.org/html/2609.10706; confidence HIGH.
Field cannot yet: Convert in-the-wild human video into physically valid, contact-aware, occlusion-consistent robot demonstrations rather than kinematic pretraining hints.
Stated limitations:
- Robotized observation fidelity is bounded by reconstruction and visual conversion quality; the robot overlay ignores occlusion with scene geometry and leaves inpainting/rendering artifacts. [6 Limitations]
- The effect of robotization fidelity on downstream policy learning is not characterized. [6 Limitations]
- No force or tactile signals are captured, only visual and kinematic action supervision. [6 Limitations]
- Kinematic retargeting models neither self-collision nor physical contact; only 55.2% of audited trajectories were free of non-grasp self-contact, so outputs are not executable demonstrations. [6 Limitations]
Open problems listed:
- Robotized observation fidelity limited by reconstruction and visual conversion (no robot-scene occlusion modelling, inpainting artifacts).
- Unknown relationship between robotization fidelity and downstream policy learning.
- No force/tactile supervision for contact-rich manipulation from human video.
- Kinematic retargeting without self-collision or physical contact modelling yields non-executable trajectories.
Benchmark gaps:
- ALLEX real-world four tasks / OOD completion: Even with full HuRo pretraining, OOD completion is 72.2% (from 34.9% without), versus 80.3% overall completion.
- HuRo pipeline diagnostics (EgoDex rerun) / hand keypoint error: Median root-relative 21-keypoint hand error 20.4 mm; camera ATE median 4.47 mm.
- HuRo five-source audit (288 trajectories) / self-contact free fraction: Only 55.2% of trajectories free of non-grasp self-contact.
Restrictive assumptions: Monocular egocentric RGB; metric scale recovered from MoGe-2 monocular depth, camera from masked DROID-SLAM.; 3D hand pose from HaWoR (MANO) estimates; median root-relative 21-keypoint error 20.4 mm vs EgoDex annotations.; Retargeting is kinematic only (fingertip and structure cues), no object pose or physics.; Background behind the human arm is unobserved and must be inpainted.; Actions derived as next retargeted state (a_t = s_{t+1}); trajectories used as pretraining supervision, not executable demos.

## [1382] RoboEdit: Turning Human Manipulation Videos into Scalable Robot Experience (arXiv 2026, dataset, S6)
Source: https://arxiv.org/html/2608.18948; confidence HIGH.
Field cannot yet: Recover metrically accurate, contact-consistent 3D hand-object interaction from monocular video without heavy depth and physics correction.
Stated limitations:
- Monocular hand reconstruction (HaMeR) has depth and scale ambiguity that misplaces hands in 3D, causing missed contacts, penetration or instability after retargeting; depth correction is needed. [3.1 RoboEdit-ADC]
- Without depth regularization and physics refinement the retargeted robot hand is displaced or has floating/penetrating fingers. [4.4 Ablation Study]
- Background SSIM is slightly lower because robot and human hands differ in spatial extent near the edit-mask boundary. [4.3 Quantitative Comparison]
Open problems listed:
- Faithfully transforming human videos into robot interaction videos while preserving scene context, interaction dynamics and temporal consistency across embodiments.
- Depth and scale ambiguity of monocular hand reconstruction harming contact geometry.
- Penetration, floating contacts and temporal jitter in reconstructed hand-object interactions.
Benchmark gaps:
- RoboEdit 300-case benchmark / 3D robot-state decoder wrist / fingertip error: Full model wrist 42.03 mm, fingertip 43.26 mm, rotation 23.28 degrees.
- Genesis simulation, 512 environments / trajectory-reproduction success: 71% with Panda gripper and 62% with XHand.
Restrictive assumptions: Rigid object mesh reconstructed by TRELLIS and 6D-tracked by FoundationPose (model-based tracking of a reconstructed template).; Camera intrinsics, extrinsics and depth from VGGT on monocular RGB.; Source videos from lab HOI datasets (DexYCB, HOT3D, H2O, GigaHands, TACO).; Contacts defined by fingertip-to-surface distance thresholds consistent across frames.; Slow offline curation: about 20 minutes per clip for ADC and 8 minutes for Trans inference on an H100.

## [1385] Human-Centric Transferable Tactile Pre-Training for Dexterous Robotic Manipulation (arXiv 2026, dataset, S6)
Source: https://arxiv.org/html/2607.01067; confidence HIGH.
Field cannot yet: Obtain measured, scalable full-hand contact force for natural human manipulation without gloves, MoCap or mesh-distance proxies.
Stated limitations:
- Existing tactile datasets remain small and narrow in contact coverage because of hardware and collection systems. [Abstract]
- Standard VLA policies ignore tactile information, degrading performance in contact-intensive tasks. [1 Introduction]
- Simulation benchmarks have no tactile modality, so a proprioceptive proxy replaces tactile input there. [5.2 Simulation Environment Experiments]
Open problems listed:
- Scarcity of large-scale tactile data with broad contact coverage.
- Tactile sensors on robot hands are non-unified in hardware integration.
- Teleoperation for contact-rich tasks is labor-intensive and hard to scale.
- Human demonstration datasets largely omit tactile modality.
- Pre-train/post-train distribution mismatch in tactile VLA training.
Benchmark gaps:
- Real robot PlugIn (Gripper/DexBotic) / success rate: In-distribution 20% and 10%; OOD 20% and 20%; all baselines 0%.
- LIBERO-plus / zero-shot success, camera perturbation: TTP 48.9%, below OpenVLA-OFT 56.4% and pi0-Fast 65.1%.
- RoboCasa / average success: TTP average 55.1%; Pick and Place only 35%.
Restrictive assumptions: HOI-Tac tactile labels are binary per-vertex contact from hand-object mesh distance thresholding, not measured force.; DeskTask-Tac requires three calibrated RealSense cameras plus tactile glove, and for the AprilTag pipeline a MoCap glove and scene AprilTags.; Tactile from simulation InternData-Tac is projected onto a shared MANO surface.; Unified 351-D tactile space on MANO UV assumed across embodiments.

## [1386] Human Universal Grasping (arXiv 2026, dataset, S6 S1)
Source: https://arxiv.org/html/2606.17054; confidence HIGH.
Field cannot yet: Learn bimanual, closed-loop, occlusion-robust grasp-and-manipulate behaviour from egocentric human capture at scale.
Stated limitations:
- Trained on right-hand grasps only with fixed MANO shape; left-handed, bimanual and hand-specific morphology are not modeled. [7 Limitations]
- Retargeting fails when robot hand cannot reach a feasible analog of the MANO pose. [7 Limitations]
- Open-loop execution without visual feedback fails on objects that shift or articulate. [7 Limitations]
- Hand tracking degrades under occlusion, making grasp labels too loose or tight. [7 Limitations]
- Accuracy drops on very small objects (224x224 input) and on large or far objects rare in egocentric data. [7 Limitations]
- Only one grasp predicted per trial; evaluation indoor only. [7 Limitations]
Open problems listed:
- Bimanual and left-hand grasping not modeled.
- Hand-specific morphology not modeled.
- Retargeting infeasibility across robot hands.
- Open-loop execution failures on shifting or articulated objects.
- Grasp label noise when the hand is occluded.
- Small, large and far objects poorly handled.
- Outdoor evaluation absent.
Benchmark gaps:
- HUG-Bench test (simulation) / success rate: Full model 73.0% vs human-grasp oracle 94.0%, a ~20-point gap.
- HUG-Bench test (real world, 30 objects) / success rate: 66.7% tabletop and 62.0% in-the-wild.
- Data scaling study / test SR vs data size: Neither SR nor FC error saturates at 1M frames; model still data-bound.
Restrictive assumptions: Stereo RGB-D input with a user-specified query point on the object.; Static scene: grasp propagated back to no-hand frames using Aria SLAM camera poses.; Right-hand, single-hand grasps, canonical MANO shape.; Grasp only (pre-grasp, grasp, lift); no post-grasp manipulation.; Aria Gen 2 hand tracking provides 21 landmarks used as labels.

## [1387] EgoTactile: Learning Grasp Pressure for Everyday Objects from Egocentric Video (ICML 2026, dataset, S6 S1)
Source: https://arxiv.org/html/2606.09243; confidence HIGH.
Field cannot yet: Infer accurate full-hand contact pressure from egocentric video under occlusion without explicit hand and object 6D pose estimates.
Stated limitations:
- Main supervised split is in a controlled environment; broader real-world coverage remains future work. [7 Limitations and Future Work]
- Bare-hand subset gives weakly paired supervision, not exact force labels for the visible hand. [7 Limitations and Future Work]
- RGB-conditioned models fail on rare interaction patterns without explicit hand pose and object 6D pose. [7 Limitations and Future Work]
- Diffusion model slower than discriminative baselines. [7 Limitations and Future Work]
Open problems listed:
- Scarce synchronized full-hand pressure data on 3D objects.
- Occlusion and incomplete observation break pixel-to-pressure alignment in egocentric grasping.
- Physical ambiguity: visually identical objects with different weight or fill state.
- Broader real-world coverage beyond controlled capture.
- Exact force labels for bare hands unavailable.
- Rare interaction patterns need explicit hand and object 6D pose.
- Inference speed of diffusion models.
Benchmark gaps:
- EgoTactile unseen interaction patterns (40 clips) / C-IoU: EgoPressureDiff 31.8% vs 56.3% on natural grasps.
- EgoTactile realistic scenes / C-IoU / V-IoU: EgoPressureDiff 49.6 / 33.7; baselines fall to 13.4-23.7 C-IoU.
- EgoTactile Object-Held-Out / V-IoU: Best method 38.9% volumetric IoU.
Restrictive assumptions: Green-screen controlled capture for the main split.; Tactile glove with 162 taxels on the grasping hand (visible in gloved split).; Single grasping hand per clip; 12 participants, 63 objects.; Object and subject metadata (weight, stiffness, fill state) supplied as text conditioning.; Bare-hand labels from a synchronized off-camera gloved hand under a metronome protocol.

## [1388] RH20T: A Comprehensive Robotic Dataset for Learning Diverse Skills in One-Shot (ICRA 2024, dataset, S6)
Source: https://arxiv.org/pdf/2307.00595; confidence HIGH.
Field cannot yet: Scale contact-rich multimodal manipulation data to dual-arm and dexterous hands while exploiting paired human demonstrations for one-shot transfer.
Stated limitations:
- Data collection is expensive. [V. Discussion and Conclusion]
- Robotic foundation models not evaluated on the dataset; attempts failed due to compute limits. [V. Discussion and Conclusion]
- Training a one-shot large model is beyond the authors' compute; experiments only show few-shot transfer with ACT. [IV. Experiments]
Open problems listed:
- Lack of large diverse robot manipulation datasets due to data acquisition barriers.
- Over-reliance on visual guidance; need for multi-modal (tactile, force, audio) perception.
- Teleoperation interfaces without force feedback are inefficient and unsafe in contact-rich tasks.
- Evaluating robotic foundation models for one-shot skill transfer.
- Dual-arm and multi-finger dexterous manipulation data.
Restrictive assumptions: Single-arm robots with parallel grippers only.; Fixed calibrated platform with 8-10 global cameras plus in-hand cameras.; Haptic teleoperation device with force rendering and a force-torque sensor.; Human demonstrations recorded on the same lab platform, not in the wild.; Experiments use only robot sequences (ACT) on a block pick-and-place task; paired human videos not exploited.

## [1389] RoboTube: Learning Household Manipulation from Human Videos with Simulated Twin Environments (CoRL 2022, benchmark, S6)
Source: https://proceedings.mlr.press/v205/xiong23a/xiong23a.pdf; confidence HIGH.
Field cannot yet: Translate human video, especially bimanual and deformable manipulation, into robot demonstrations via explicit 3D hand-object pose estimation.
Stated limitations:
- Dataset still falls short of in-the-wild settings where internet videos are less structured or relevant. [Limitations]
- Reward learning remains hard on bimanual pot-lifting and cloth folding when tested on RT-sim videos. [Experiments]
- Balancing dataset diversity and relevance is an open problem. [1 Introduction]
Open problems listed:
- Scaling task complexity beyond grasp, push, relocate.
- Balancing data diversity and relevance in robot-oriented video datasets.
- Lack of standard test environments for reproducible comparison.
- In-the-wild human-to-robot imitation.
- Leveraging negative demonstrations and multi-view video for self-supervised learning.
- Explicit pose estimation plus 3D vision to translate human videos into robot demonstrations.
- Learning to simulate objects from human videos.
Benchmark gaps:
- RT-sim bimanual pot-lifting and cloth folding / success rate / reward prediction: Hardest tasks; learned rewards poorly predicted on RT-sim test videos and RL success lowest.
Restrictive assumptions: Two RealSense D435 views (head FPV and tripod TPV) at 640x480.; Five fixed task families, 60 objects scanned for digital twins.; Policies in RT-sim use low-level state input; only reward models use images.; Real-robot evaluation with structured mode and fixed third-person camera.

## [1390] CosmoH2G: A Hand-to-Gripper Transfer Dataset and Baseline Method for Object Manipulation with Complex Spatial Movements (SIGGRAPH Asia 2026, dataset, S6)
Source: https://arxiv.org/html/2609.07498; confidence HIGH.
Field cannot yet: Track a hand-held object's 6D pose through large rotations under heavy hand occlusion without rigid-grasp priors or occlusion-free keyframes.
Stated limitations:
- Framework operates open-loop with no real-time error correction or explicit collision avoidance. [7. Limitations and Future Work]
- Evaluation only on pick-and-place with unseen hand motions; broader task types left to future work. [5.1 Experimental Setups]
- Real-robot performance lower because objects slip during large rotations or are dragged before full lift. [5.2 Experimental Results]
- Object visual tracking is infeasible during manipulation due to persistent hand occlusion; object pose is induced from the hand under a rigid-grasp prior. [Appendix C]
Open problems listed:
- Transfer of complex spatial movements (rotations, flips) from human hand to gripper.
- Reliable extraction of object-centric trajectories in cluttered environments.
- Encoding fine-grained hand-pose dynamics for manipulation.
- Point tracking failure under self-occlusion during large rotations.
- Open-loop execution without collision avoidance.
Benchmark gaps:
- CosmoH2G real-robot test (186 cases, 40 unseen objects) / success rate: 70.43% for the proposed method; best baseline Track2Act 60.22%.
- CosmoH2G real-robot test / TOPA (orientation placement error): 19.34 degrees for the proposed method vs 10.27 in simulation.
Restrictive assumptions: Object meshes reconstructed from multi-view captures and tracked with FoundationPose++ (template-based).; Registration uses first and last frames assumed free of hand/gripper occlusion.; Manual annotation of start/terminal frames and click-based SAM2 masks for UMI.; Stable-grasp rigid hand-object relation assumed for pose induction.; Single-hand to single-gripper transfer; monocular RGB-D input.; Paired data needs UMI handheld gripper re-enactment of each human demo.

## [1391] Mimicking-Bench: A Benchmark for Generalizable Humanoid-Scene Interaction Learning via Human Mimicking (arXiv 2024, benchmark, S6 S2)
Source: https://arxiv.org/html/2412.17730; confidence HIGH.
Field cannot yet: Learn humanoid skills that involve precise hand contact with movable objects from human references; success on box lifting stays near 5 percent even in simulation.
Stated limitations:
- The humanoid model has no dexterous hands; the benchmark targets torso-level interaction, so fine-grained manipulation is not studied. [6 Limitation and Conclusion]
- All existing pipelines struggle on the touching-points and box-lifting tasks because of unstable hand control and dynamic object manipulation. [5.1 Skill Learning Pipelines]
- Raw multi-view egocentric RGB-D input performs far worse than an elevation map, attributed to irrelevant or noisy information in egocentric images. [5.5 Egocentric Visual Perception Modalities]
- Energy thresholds required for sim-to-real transfer are unknown, so success is averaged over four guessed values. [3.2 Task Formulations and Evaluations]
Open problems listed:
- Bridging discrepancies between human and humanoid body models (retargeting).
- Translating skill animations into executable humanoid control signals (motion tracking).
- Deriving generalized policies from diverse skill references (imitation learning).
- Stable hand control and manipulation of dynamic objects (touching and lifting tasks).
- Interpreting noisy egocentric visual input versus structured elevation maps.
- Unknown energy thresholds for sim-to-real transfer.
- Extending to dexterous hands for fine-grained manipulation.
Benchmark gaps:
- Mimicking-Bench task L (lifting a box) / kinematic / energy-averaged success rate (%): Best combination 6/5; PPO and OmniH2O 0/0; HumanPlus 4/3.
- Mimicking-Bench task T (touching points near an object) / kinematic / energy-averaged success rate (%): Best combination 11/10; HumanPlus 46/32 is highest; PPO and OmniH2O 0/0.
- Mimicking-Bench, multi-view RGB-D input / mean success rate (%): 4/4 mean versus 54/51 with elevation map.
Restrictive assumptions: Simulation only (Isaac Gym, Unitree H1); no real-robot evaluation.; Human references are largely synthesized (UniHSI, ROAM) or clipped from mocap (CORE4D), not captured from video.; Best policy uses a structured elevation map rather than raw egocentric images.; No dexterous hands; torso-level contact only.; Sim-to-real energy thresholds unknown.

## [1392] TeleOpBench: A Simulator-Centric Benchmark for Dual-Arm Dexterous Teleoperation (arXiv 2025, benchmark, S6 S3)
Source: https://arxiv.org/html/2505.12748; confidence HIGH.
Field cannot yet: Track two interacting hands from cameras robustly enough to teleoperate bimanual handovers; vision and VR interfaces both score 0 percent when hands occlude each other.
Stated limitations:
- Benchmark covers only upper-body teleoperation in mostly tabletop settings; whole-body loco-manipulation is not covered. [6 Limitations]
- No evaluated modality provides tactile or haptic feedback, limiting assessment of force-controlled tasks. [6 Limitations]
- Monocular vision teleoperation is limited to easy tasks by low frame rate, coarse wrist orientation and occlusion. [4 Experiments]
- VR hand tracking fails entirely on a bimanual handover because hand-over-hand occlusion breaks pose estimation. [4 Experiments]
- The best-performing Xsens MoCap system is the most expensive of the four. [4 Experiments]
Open problems listed:
- No standardized benchmark for fair comparison of dual-arm dexterous teleoperation systems.
- Vision-only teleoperation lags MoCap in precision and update rate.
- Hand-hand occlusion breaks vision and VR hand pose estimation in bimanual tasks.
- Whole-body loco-manipulation teleoperation is not benchmarked.
- Lack of haptic or tactile feedback in teleoperation interfaces.
Benchmark gaps:
- TeleOpBench sim, task 7 ball_bimanual / success rate (%): Vision 0, VR 0, exoskeleton 80, Xsens 100.
- TeleOpBench sim, task 10 pen_brushpot / success rate (%): Vision-based 0; task 9 pot_tomato_plate vision-based 10.
- TeleOpBench real-world, task 7 ball_bimanual / success rate (%): Vision 0, VR 0; vision 20 on ball_mug, 0 on pen_brushpot.
Restrictive assumptions: Robot lower body immobilized; upper-body tabletop tasks only.; User study with four participants.; MoCap requires Xsens suit and Manus gloves with calibration; exoskeleton is custom per robot.; Per-operator body scaling from a T-pose (vision) or finger-length measurement (VR).; Sim-real validity shown on 10 tasks only.

## [1393] H2R-Bench: Benchmarking Human-to-Robot Manipulation Video Generation in World Models (arXiv 2026, benchmark, S6)
Source: https://arxiv.org/html/2608.13049; confidence HIGH.
Field cannot yet: Generate robot manipulation videos from human demonstrations that reliably preserve hand-object contact and correct embodiment, nor verify them physically.
Stated limitations:
- Evaluates only visible evidence of transfer, not physical executability or downstream policy performance. [Appendix D Limitations]
- Only 120 EgoDex sources and two target embodiments, covering part of manipulation variation. [Appendix D Limitations]
- Limited to short clips. [Appendix D Limitations]
- Model capability is confounded with source-conditioning interface differences. [Appendix D Limitations]
- MLLM judgments over sampled frames are uncertain under occlusion, subtle contact or severe artifacts. [Appendix D Limitations]
Open problems listed:
- Preserving task goal, action events and functional contact while replacing human with robot embodiment.
- Generic video quality metrics do not reflect valid robot transfer.
- Actor leakage, unsupported contact and incorrect morphology in generated videos.
- Physical executability and downstream policy value of generated videos remain unevaluated.
- Extending to long demonstrations and more embodiments.
- Reliable automatic judgment under occlusion and subtle contact.
Benchmark gaps:
- H2R-Bench (240 transfer cases) / H2RCore (0-100): Scores span 30.0 to 84.6 across 11 models while video quality spans only 0.73 to 0.81; weak rank association.
- H2R-Bench / M4 embodiment correctness: HunyuanVideo 1.5-I2V embodiment score near zero despite highest video quality; contact score near 0.185.
Restrictive assumptions: Egocentric human source videos from EgoDex only.; Evaluation by MLLM judges on 25 uniformly sampled frames.; Target embodiment specified by text; no physical execution.

## [1394] HandEdit: A Unified Benchmark for Egocentric Human-to-Robot Dexterous Hand Image Editing (arXiv 2026, benchmark, S6)
Source: https://arxiv.org/html/2608.12122; confidence HIGH.
Field cannot yet: Retarget human hand-object interaction to arbitrary robot hands reliably enough to automate data conversion; retargeting is the dominant failure in pseudo-GT construction.
Stated limitations:
- Pixel-aligned human-robot image pairs cannot be physically captured, so the dataset relies on edited pseudo-references. [G Limitations and Broader Impacts]
- Pseudo-references keep a gap from real-robot observations in appearance and contact dynamics. [G Limitations and Broader Impacts]
- Data are intended for pre-training and do not replace real-robot demonstrations. [G Limitations and Broader Impacts]
- VLM-based judgment captures semantic consistency and perceptual quality but not fine-grained morphology or contact. [4.2 Benchmark Results and In-depth Analysis]
- Failure breakdown covers only rejected ARCTIC frames, not residual errors in retained samples or other sources. [B.2 Failure Breakdown]
Open problems listed:
- Embodiment gap between human and robotic dexterous hands in appearance, geometry, articulation and kinematics.
- Hand-arm consistency with target morphology and camera viewpoint.
- Preserving scene, object state, task semantics and hand-object contact during editing.
- Existing robotization methods tied to grippers or single platforms.
- Generic image-quality and VLM metrics miss embodiment and contact fidelity.
- No physically captured aligned human-robot pairs.
Benchmark gaps:
- HandEdit pseudo-GT curation (ARCTIC) / non-kept rate: About 33 percent of candidates rejected; retargeting dominant cause at 63.46 percent of sampled rejections.
Restrictive assumptions: Requires source datasets with MANO or 3D hand pose annotations (EgoDex, ARCTIC, OakInk2, HOI4D, HO-Cap).; Assumes fixed upright robot mounting and a camera-relative virtual base fixed per sequence.; Pseudo-GT from segmentation, inpainting, retargeting and compositing with human screening.

## [1395] TactiDex: A Real-World Tactile-Guided Benchmark for Human-Like Dexterous Manipulation (arXiv 2026, benchmark, S6 S3)
Source: https://arxiv.org/html/2607.09190; confidence HIGH.
Field cannot yet: Capture hand-object interaction with physically valid contact without mocap plus tactile gloves and post-hoc contact correction, or transfer it with closed-loop tactile control.
Stated limitations:
- Sim-to-real discrepancies in sensor noise, resolution and compliance can degrade learned force interactions. [6 Conclusion and Discussion]
- Real deployment is open-loop; tactile sensing on the robot hands is not fed back to the policy. [C.3 Command Mapping and Open-Loop Execution]
- Kinematic fitting leaves floating or penetration artifacts during object interaction that require tactile-constrained post-optimization. [3.2 Data Collection and Processing]
- Naive contact force matching in RL causes unstable optimization or reward exploitation. [1 Introduction]
Open problems listed:
- Trajectory-centric transfer ignores contact formation and force distribution.
- Lack of strictly synchronized tactile-kinematic demonstrations and contact-aware metrics.
- Unstable optimization when tactile signals are used directly as RL rewards.
- Sim-to-real gaps in tactile sensor noise, resolution and compliance.
- Closed-loop tactile feedback on real hardware not yet achieved.
Benchmark gaps:
- TactiDex evaluation split (73 sequences) / tactile-aware success rate (%): Kinematic baseline 39.35; full TactiSkill 64.64.
- TactiDex evaluation split / Contact F1: Baseline 0.5569; best 0.7384.
- TactiDex evaluation split / SafeTac@3N (%): Baseline 35.84; best 53.57.
Restrictive assumptions: OptiTrack 8-camera mocap in a 1.2 m by 1.8 m volume, plus IMU-optical mocap glove and worn tactile glove.; Objects 3D scanned and individually calibrated in the mocap system (49 objects).; Tactile glove at 17 Hz with 162 sensing elements.; Policy learned in simulation with privileged contact forces for the critic.; Evaluation on 73 selected sequences.

## [1396] HT-Bench: Benchmarking and Learning Dexterous Full-Hand Tactile Representations with Egocentric Vision (arXiv 2026, benchmark, S6 S1)
Source: https://arxiv.org/html/2606.19161; confidence HIGH.
Field cannot yet: Predict contact pressure from egocentric vision reliably on unseen tasks; OOD contact IoU stays below 0.46.
Stated limitations:
- Covers only egocentric vision with full-hand tactile sensing, not fingertip optical sensors, force/torque sensors, taxel skins or non-hand embodiments. [6 Conclusion and Limitation]
- A universal benchmark accommodating all tactile heterogeneity is considered impractical; the paper does not attempt it. [1 Introduction]
- Precise reconstruction of severely corrupted local tactile regions in unseen tasks remains challenging. [5.1 Comparison with Baseline Encoders]
Open problems listed:
- Heterogeneous tactile sensors, layouts, formats and embodiments prevent a universal benchmark.
- Task-specific tactile features may not be transferable representations.
- Tactile signals are sparse, locally structured and coupled with dynamics, complicating masked and VQ learning.
- Generalization of vision-to-touch prediction to unseen tasks.
- Coverage of other sensing paradigms and non-hand embodiments.
Benchmark gaps:
- HT-Bench OOD split, vision-to-tactile / cIoU: Best 0.457 (RMSE 0.080).
- HT-Bench real-world water pouring / success rate (%): Best 53.3 over 15 trials.
Restrictive assumptions: Requires a full-hand tactile glove paired with egocentric RGB.; Task-level OOD split holds out only one interaction task.; Real-world evaluation on four tasks with 15 trials each.

## [1397] HoloAssist: an Egocentric Human Interaction Dataset for Interactive AI Assistants in the Real World (ICCV 2023, dataset, S6)
Source: https://arxiv.org/html/2309.17024; confidence HIGH.
Field cannot yet: Provide object pose ground truth alongside egocentric hand tracking at scale, so object-centric manipulation models for assistance remain unbenchmarked.
Stated limitations:
- Object poses are not annotated; object-centric affordance and manipulation models are left to future work. [6 Conclusion and Future Work]
- Simply concatenating more modalities such as depth and head pose does not necessarily help; specialized encoders may be needed. [5 Experiments]
- 3D hand pose forecasting is hard because hands move quickly; error grows with horizon. [5 Experiments]
- Mistake detection is difficult due to highly skewed classes (about 6 percent mistakes). [4.2 Benchmark Tasks]
Open problems listed:
- Mistake detection under heavily skewed class distribution.
- Intervention type prediction.
- 3D hand pose forecasting for action guidance.
- Grounding instructions in the 3D environment (spatial deictics).
- Fusing multiple sensor modalities effectively.
- Object pose annotation and object-centric affordance models.
- Transferring simulated assistant agents to real-world human interaction.
Benchmark gaps:
- HoloAssist 3D hand pose forecasting / MPJPE (cm): 9.80 / 10.68 / 11.25 cm at 0.5 / 1.0 / 1.5 s with hand-only Seq2Seq.
- HoloAssist fine-grained action recognition / top-1 accuracy: Around 35 percent.
- HoloAssist mistake detection / score: Best 40.19 (hands only); RGB 35.11.
Restrictive assumptions: HoloLens 2 headset capture with device-provided hand tracking.; Hands only; no object pose ground truth.; Two-person instructor-performer setup.

## [1398] HD-EPIC: A Highly-Detailed Egocentric Video Dataset (CVPR 2025, dataset, S6 S1)
Source: https://arxiv.org/html/2502.04144; confidence HIGH.
Field cannot yet: Track manipulated objects over long egocentric videos and reason about their 3D motion; object VOS J&F is 27 to 35 and VLM object-motion accuracy 20.8 percent.
Stated limitations:
- Egocentric video brings camera motion, subtle actions, occlusion during manipulation and objects leaving view. [1 Introduction]
- VOS evaluation passes only memory and evaluation frames, which the authors acknowledge is limited. [D.4 Long-Term VOS Benchmark]
- Objects are harder than hands for long-term segmentation due to perspective, lighting, location and occlusion. [5.3 Long-Term VOS Benchmark]
- Audio models are not robust to new scenes or devices. [5.2 Recognition Benchmarks]
Open problems listed:
- Fine-grained to hour-long video understanding remains out of reach for foundational and specialised models.
- 3D perception and object itinerary reasoning relative to fixtures.
- Gaze-based anticipation of next object movement.
- Long-term segmentation of manipulated objects under occlusion and out-of-view.
- Robustness of audio recognition to new scenes and devices.
- Long-video (over 1 minute) and multi-video question answering.
- Recognising fine-grained actions in unscripted in-the-wild settings.
Benchmark gaps:
- HD-EPIC VQA / accuracy (%): Gemini Pro: 3D perception 32.5, object motion 20.8, gaze 28.7; human 93.8, 92.7, 75.0.
- HD-EPIC long-term VOS (objects) / J&F: SAM2 27.0, Cutie 34.6, static 6.6.
- HD-EPIC action recognition / top-1 accuracy: Best 51 verb, 37 noun, 24 action.
- HD-EPIC sound recognition / top-1 accuracy drop vs EPIC-Sounds: -28.4 (SSAST), -25.9 (ASF), -26.4 (TIM).
Restrictive assumptions: Project Aria glasses with MPS SLAM and gaze.; Digital twins manually curated in Blender from SLAM point clouds.; Object 3D locations from masks lifted with monocular metric depth aligned to sparse SLAM points; 3D boxes, not 6D object poses.; Validation-only dataset in 9 kitchens.

## [1399] Robot Learning from Human Videos: A Survey (arXiv 2026, survey, S6)
Source: https://arxiv.org/html/2604.27621; confidence HIGH.
Field cannot yet: The field cannot yet extract physically grounded, robot-executable interaction signals (contacts, object motion, multi-agent coordination) reliably from occluded, unconstrained human video.
Stated limitations:
- Nearly all learning-from-human-video methods assume one human demonstrator and one robot; collaborative, multi-agent tasks are not supported. [5.4 Multi-Agent Interaction]
- Even with RGB-D or metric depth, vision-only human video remains vulnerable to occlusion and ambiguous interaction states. [5.5 Multimodal Signals Accompanying Human Videos]
- Action-near methods fail by mis-grounding: extracted trajectories or contact cues look plausible in video but violate robot kinematics, control or contact dynamics. [3.5 Route Selection]
- Current pipelines depend on curated or aggressively filtered data, discarding low-quality, occluded or blurred videos and long-tail interactions. [5.6 Utilization of Low-Quality Human Videos]
- Benchmarking is fragmented across robots, tasks and video sources, and most methods cannot be benchmarked in simulation alone. [5.7 Standardized Benchmarking]
- Affordance extraction is limited to visually observable geometric traces (contact regions, hand trajectories, object poses, flow) without function or physical constraints. [5.2 Physics-Aware Functional Affordance Extraction]
- Human-video world models emphasise visual similarity and do not impose physical constraints, producing physically invalid rollouts in contact-rich, long-horizon tasks. [5.1 Physically Grounded World Models]
- Human videos are used as a fixed offline corpus with no mechanism to absorb new videos after initial training. [5.3 Continual Learning with Human Video Data]
Open problems listed:
- Physically grounded world models that capture long-horizon causal dependencies and physical consistency.
- Physics-aware functional affordance extraction beyond geometric HOI traces.
- Continual learning with newly available human video data.
- Multi-agent interaction: agent correspondence, overlapping motions, cross-agent contact tracking, and coupled feasible action spaces.
- Multimodal signals (audio, gaze, tactile) accompanying human videos, and their integration despite differing rates and noise.
- Use of low-quality human videos (blur, occlusion, camera shake, failed executions, passive observation).
- Standardized benchmarking, including evaluation not reducible to simulation.
- Egocentric data ecosystems with shared protocols, annotations and access interfaces.
Benchmark gaps:
- LfHV literature as a whole / cross-method comparability: Methods are evaluated on different robots, tasks and human video sources, so which transfer choices cause better performance remains unclear.
Restrictive assumptions: Most methods assume a single human demonstrator and a single robot.; Most rely on curated or filtered video rather than raw in-the-wild footage.; Affordance pipelines assume hand, object pose and contact cues are visually observable from the camera view.

## [1400] Data Pyramid for Embodied Manipulation: A Survey (arXiv 2026, survey, S6)
Source: https://arxiv.org/html/2607.24744; confidence HIGH.
Field cannot yet: The field cannot yet capture accurate, calibrated hand-object geometry and contact at scale from wearable or egocentric sensing without heavy calibration and participant burden.
Stated limitations:
- Egocentric human data is not equivalent to robot experience and suffers from occlusion, blur, camera motion and device-dependent viewpoints. [4.4 Advantages and Limitations]
- Wearable head and hand tracking is not mature for large-scale deployment; gloves, tactile sensors and EMG need fitting, calibration and synchronisation. [8.3 Scalable Data Collection Across Pyramid Layers]
- Instrumented capture trades accuracy under occlusion against calibration effort and participant burden. [4.3.2 Geometric Supervision]
- Object pose labels in HOI datasets can be ambiguous under occlusion and object symmetry. [4.3.2 Geometric Supervision]
- UMI-style data quality depends on pose tracking and synchronisation that degrade in hard visual conditions. [3.4 Advantages and Limitations]
- Tactile sensing is not a standard modality in robot datasets, leaving a missing contact layer. [8.1 Tactile Data for Contact-Rich Robot Learning]
- Failure and recovery data are scarce and poorly organised; binary success labels are insufficient. [8.2 Failure Data and Recovery-Centric Robot Learning]
- Retargeted human hand motions can look plausible yet fail on real robot hands. [8.5 Egocentric Priors for Dexterous Hand Policy Learning]
- Optimal data mixtures across pyramid layers are unknown and compute-matched ablations are limited. [8.6 Data Recipes]
Open problems listed:
- Building large-scale tactile datasets for contact-rich learning.
- Collecting and structuring failure and recovery data.
- Scalable data collection across pyramid layers, including mature wearable sensing with automatic calibration and on-device hand-object reconstruction.
- Cross-embodiment state-action alignment with consistent geometric semantics.
- Leveraging egocentric priors for dexterous hand policy learning across the kinematic, morphological and physical gap.
- Principled data recipes for mixing data sources.
- Data quality assessment, multimodal and action-space standardisation, human-to-robot and sim-to-real transfer (conclusion list).
Benchmark gaps:
- InternData-A1 (simulation) / action keypoint spatial spread: Skill-constrained generation produced many trajectories whose action keypoints concentrate in a small region, indicating repetition despite scale.
Restrictive assumptions: Dense geometric and multimodal egocentric supervision requires extra hardware, calibration, synchronisation and reconstruction.; Optical mocap ground truth (e.g. HOT3D) requires markers and a controlled calibrated workspace.; Object pose annotation often relies on CAD-model registration.

## [1401] Vision-Language-Action in Robotics: A Survey of Datasets, Benchmarks, and Data Engines (arXiv 2026, survey, S6)
Source: https://arxiv.org/html/2604.23001; confidence HIGH.
Field cannot yet: The field cannot yet turn human or robot video into physically valid, low-error action labels, because pose and depth reconstruction errors propagate into policies.
Stated limitations:
- Datasets trade fidelity against scale; aggregated corpora gain volume at the cost of interface consistency. [6.1 Dataset Limitations]
- Contact-rich behaviours with force or tactile signals are underrepresented. [6.1 Dataset Limitations]
- Video-to-data engines inherit perception errors from grounding, pose and depth estimation. [6.3 Data Engine Limitations]
- Video-to-data engines still struggle with reconstruction noise and action error. [5.1 Video-to-Data Engine]
- Generation scales faster than grounding and verification. [6.3 Data Engine Limitations]
- Benchmarks report overall success without diagnosing whether failures come from planning, memory, composition or recovery. [6.2 Benchmark Limitations]
Open problems listed:
- Fidelity-cost trade-off in datasets; interface consistency vs scale.
- Underrepresentation of force and tactile, contact-rich data.
- Grounding semantics into physically valid closed-loop control.
- Benchmarks that diagnose temporal and compositional reasoning, memory, and recovery.
- Evaluation under compounded variability across perception, embodiment and semantics, and cross-embodiment transfer.
- Grounding reliability of data engines: perception noise, physical plausibility, feasibility checks, calibration, reward specification.
- Limited temporal context, compute cost and sim-to-real discrepancy of interactive world models.
- Bridging the sim-to-real fidelity gap via high-fidelity real-scene reconstruction in simulation.
Benchmark gaps:
- CALVIN / success rate, five sequential instructions: Success drops to 0.08 percent for five sequential instructions, as cited by the survey.
- THE COLOSSEUM / success under combined perturbations: Substantial degradation under combined perturbations (no number given).
- VLABench / multi-step logical tasks: Systematic failures reported (no number given).
Restrictive assumptions: Video-to-data engines assume reliable hand pose, object mesh and 6D pose and depth reconstruction from video.; Trajectory-reuse generators assume known subtask structure.

## [1402] Robots Need More than VLA and World Models (arXiv 2026, position, S6)
Source: https://arxiv.org/html/2606.06556; confidence HIGH.
Field cannot yet: The field cannot yet automatically infer aligned contact events, object-state changes and task phases from multimodal human demonstrations as robot-usable supervision.
Stated limitations:
- Robot-native supervision does not scale because most real-world behaviour lacks robot action labels. [2.1 The Robot-Native Regime]
- Learning from passive video does not solve grounding; latent actions, progress signals and representations still miss contact dynamics and force constraints. [2.2 Learning from Weakly Grounded Physical Observations]
- Multimodal streams (video, mocap, tactile, logs) are asynchronous; aligning them to physical events is itself unsolved. [3.1 Physical Data Engines and Embodied Autolabelling]
- Inferring events, contacts and object states from episodes that carry only partial supervision is an open question. [3.1 Physical Data Engines and Embodied Autolabelling]
- Pose-matching retargeting is insufficient; the effect on the object must be preserved. [3.2 Task-preserving Retargeting across Embodiments]
- Object-centric world models depend on reliable perception and tracking; 3D representations struggle with contact and force. [3.3 Beyond Physics-Grounded World Models]
- Without component-level credit assignment, deployment failures cannot be routed to the faulty component. [3.4 Self-Improving Deployment Loops]
Open problems listed:
- Physical data engines and embodied autolabelling from heterogeneous, asynchronous, partially labelled episodes.
- Temporal alignment of video, motion capture, tactile and robot logs to a common event timeline.
- Joint inference of coupled labels: task phase, contact, object state, action and reward.
- Task-preserving retargeting across embodiments (moving from pose to contact to object-state to intent preservation).
- Choice of world-model representation for consequence prediction (pixel, object-centric, 3D, mechanics, hybrid).
- Task-conditioned reward grounding distinguishing progress, failure, recovery and success.
- Self-improving deployment loops with component-level credit assignment.
- New evaluation questions: can a system infer contacts, object-state changes and task phases from human behaviour?
Restrictive assumptions: Current robot learning assumes observations, actions, task labels, rewards and success metrics are specified in advance.; Object-centric world models assume reliable perception and tracking of objects.

## [1424] TULIP: Multi-camera 3D Precision Assessment of Parkinson's Disease (CVPR 2024, dataset, S7)
Source: https://openaccess.thecvf.com/content/CVPR2024/papers/Kim_TULIP_Multi-camera_3D_Precision_Assessment_of_Parkinsons_Disease_CVPR_2024_paper.pdf; confidence HIGH.
Field cannot yet: The field cannot yet obtain precise markerless 3D hand and body kinematics in compact clinical rooms without a large multi-camera calibrated capture space.
Stated limitations:
- The cohort is small relative to the heterogeneity of PD. [7 Conclusion (limitations)]
- Low demographic diversity may limit generalisation. [7 Conclusion (limitations)]
- Baselines use only finger tapping and gait, not all 25 recorded activities. [7 Conclusion (limitations)]
- Capture used a large room unlike a typical clinical exam space. [6 Discussion]
- A deep pose-sequence classifier underperformed, attributed to small dataset size. [5.2.2 Index finger tapping]
Open problems listed:
- Small cohort relative to PD heterogeneity.
- Low demographic diversity.
- Baselines covering only two of 25 activities.
- Recording in a large room rather than a typical clinical space; need for hardware adapted to small rooms.
- Need for activities aligned with daily living and for unsupervised PD signatures beyond UPDRS.
- Inter-rater variability of UPDRS component scores.
Benchmark gaps:
- TULIP finger tapping / UPDRS weighted F1: Best model (MLP, 3D features) reached 0.69 F1, commensurate only with the least accurate clinician rater.
- TULIP gait / UPDRS weighted F1: Best model (Random Forest, 3D features) reached 0.72 F1; 2D features underperformed.
- TULIP pose tracking / mean error vs manual annotation: 21 mm for finger tapping and 56 mm for gait (reprojection 22 and 16 px).
- TULIP clinician labels / ICC: Kinetic tremor right hand ICC 0.1 and left hand 0.4.
Restrictive assumptions: Six synchronised (GPIO-triggered), calibrated cameras at 80 fps in a 6.3 x 3 m hexagonal capture space.; Intrinsics and extrinsics fit before and after each session.; Off-the-shelf MediaPipe and MMPose without fine-tuning, triangulated by DLT with outlier interpolation and smoothing.; Hand-crafted features and small-sample leave-one-subject-out evaluation.

## [1425] Care-PD: A Multi-Site Anonymized Clinical Dataset for Parkinson's Disease Gait Assessment (NeurIPS 2025, dataset, S7 S4)
Source: https://arxiv.org/html/2510.04312; confidence HIGH.
Field cannot yet: The field cannot yet produce clinical motion models that generalise across sites and capture setups, especially for rare severe cases, from monocular reconstructions.
Stated limitations:
- Severe gait impairment (UPDRS-gait 3) is underrepresented. [Appendix F Limitations]
- Monocular RGB mesh recovery (WHAM) adds depth and distal-joint error. [Appendix F Limitations]
- Mixing UPDRS and MDS-UPDRS rubrics and per-session labels adds label noise. [Appendix F Limitations]
- No outdoor or in-home data. [Appendix F Limitations]
- Fine-grained symptom estimation is not addressed. [Appendix F Limitations]
- Mostly short single-task walks; little multi-visit temporal context. [Appendix F Limitations]
- Encoders collapse under cross-site distribution shift. [6 Conclusions]
Open problems listed:
- Imbalance and scarcity of severe gait impairment (UPDRS-gait 3).
- Noise from monocular RGB reconstruction (depth and distal joints).
- Lack of wearable sensor modalities.
- Label variability from UPDRS vs MDS-UPDRS rubrics and per-session labels; high inter-rater variability of gait score.
- Absence of outdoor and in-home walking.
- Fine-grained symptom estimation (stride irregularity, freezing episodes).
- Temporal context across visits and activities; most data are short single-task walks.
- Cross-site generalisation and domain adaptation.
- Demographic imbalance (underrepresentation of women in severe FoG cohorts).
Benchmark gaps:
- Care-PD cross-dataset / macro-F1 (UPDRS-gait): Transfer to unseen datasets typically reduces F1 by 0.2 to 0.4; best in-site up to 0.73 on PD-GaM.
- Care-PD pretext (2D-to-3D lifting) / MPJPE: Zero-shot MotionAGFormer 60.7 mm vs 7.5 mm after Care-PD fine-tuning; MoMask 22.5 mm vs 8.7 mm.
- TOAGA (WHAM validation) / root-relative MPJPE vs Xsens: Mean 39 mm error for monocular WHAM meshes.
- Care-PD class 3 / macro-F1 including severe class: Including class 3 lowers scores by 5 to 10 pp for models trained on cohorts without class 3.
Restrictive assumptions: Only textureless SMPL meshes are released; no video frames, so video-based methods cannot be benchmarked end-to-end.; RGB cohorts depend on monocular WHAM mesh recovery and manual verification of the target person.; Only clean walking segments retained; non-walking behaviour removed.; Lab or clinical corridor recording only.

## [1426] Markerless Motion Capture in Routine Clinical Upper Limb Assessments: Validity and Insights Beyond Ordinal Scoring (arXiv 2026, benchmark, S7)
Source: https://arxiv.org/html/2607.23608; confidence HIGH.
Field cannot yet: The field cannot yet capture reliable finger and hand-object kinematics during routine clinical grasp tasks with a minimal, ad-hoc camera setup.
Stated limitations:
- Longitudinal evidence comes from two case studies only. [Discussion]
- The minimal clinically important difference is borrowed, not estimated for this measure. [Discussion]
- No inter-rater reliability data for the ARAT reference scores. [Discussion]
- Hand-crafted metrics assigned to one domain across all tasks break down for some tasks (e.g. Water Pouring). [Discussion]
- The three-camera clinical setup lacks reliable finger kinematics and has more occlusion than a five-camera lab setup. [Discussion]
Open problems listed:
- Cohort-level longitudinal validation (only two case studies).
- Measure-specific MCID and reliability bounds.
- Quantifying clinician subjectivity in reference scores.
- Task-specific domain assignment of kinematic metrics.
- Population-scale able-bodied and patient reference data.
- Finger kinematics and occlusion in clinical camera setups.
Benchmark gaps:
- Clinical ARAT recordings (20 patients, 1,174 tasks) / reprojection error: 12.5 +/- 3.0 px, above the 5-10 px lab standard.
- Clinical ARAT recordings, Tier 2 (Score 2 vs 3) / combined-feature AUC: 0.70-0.84; compensation-only AUC 0.59-0.68.
- Clinical ARAT recordings, Water Pouring / Tier 1 combined-feature AUC: 0.75, the lowest of seven task groups.
Restrictive assumptions: Three synchronised calibrated webcams (1280x720, 60 Hz) placed around the assessment table.; Therapist marks trial start and stop on a tablet in real time.; Upper-limb body kinematics only; no reliable finger or object tracking.; Score 3 used as a proxy for normal motor performance instead of measured able-bodied references.

## [1427] Monocular Markerless Motion Capture Enables Quantitative Assessment of Upper Extremity Reachable Workspace (arXiv 2026, benchmark, S7)
Source: https://arxiv.org/html/2602.13176; confidence HIGH.
Field cannot yet: The field cannot yet resolve monocular depth ambiguity and self-occlusion of the hand during cross-body and out-of-plane reaching.
Stated limitations:
- Cohort of healthy adults only; validity in patients unknown. [IV Discussion]
- Analysis was offline, post-hoc. [IV Discussion]
- Large per-octant errors, especially contralateral. [IV Discussion]
- Not precise enough for individual superior or contralateral octants. [IV Discussion]
- Monocular depth ambiguity along the optical axis is unresolved. [IV Discussion]
Open problems listed:
- Validation in patients with atypical kinematics (tremor, compensatory trunk motion).
- Real-time point-of-care processing.
- Monocular depth ambiguity and self-occlusion in posterior and contralateral workspace.
- No single viewpoint is optimal for dynamic multi-planar motion.
Benchmark gaps:
- Nine-participant UERW recordings / average percent error per octant: Up to 15.45% (frontal) and 50.21% (offset) in contralateral octants.
- Nine-participant UERW recordings / octant agreement: Offset camera under 40% agreement in the superior-anterior contralateral octant.
Restrictive assumptions: Static camera with known calibrated intrinsics.; Healthy adults, nine participants, VR-headset-displayed targets.; Offline GPU optimisation of a MuJoCo biomechanical model per trial.; Post-hoc alignment of MMC coordinates to the marker-based system.

## [1430] Codec Avatar Studio: Paired Human Captures for Complete, Driveable, and Generalizable Avatars (Ava-256 and Goliath datasets) (NeurIPS 2024, dataset, S7)
Source: https://proceedings.neurips.cc/paper_files/paper/2024/file/9712b78386cebdc3db7f1a48c2d20edb-Paper-Datasets_and_Benchmarks_Track.pdf; confidence HIGH.
Field cannot yet: The field cannot yet build relightable, multi-identity, full-body driveable avatars from commodity sensors without per-subject high-end dome captures.
Stated limitations:
- The release is unlikely to support multi-identity relightable head decoders, since relightable data exist only for the four Goliath subjects. [4 Limitations and Potential Negative Impact]
- The datasets miss the long tail of human expressivity. [4 Limitations and Potential Negative Impact]
- Low-quality-to-high-quality conversion research (phone or full-body to head and hands) is limited by only four Goliath subjects. [4 Limitations and Potential Negative Impact]
- Full-resolution data (over 10 TB per dome capture, over 3 PB total) cannot be distributed; released data is downsampled in resolution, camera count (about 80) and frame rate (7.5 or 15 fps) and lossy AVIF compressed. [2.1 Ava-256, Data distribution and compression]
- No annotation assets are released for full-body phone captures. [2.2 Goliath-4, Assets]
Open problems listed:
- Complete avatars covering full body, not only faces and hands
- Driveable avatars tracked from lightweight sensors with little interference
- Generalizable avatars built quickly for new users without expensive capture
- Multi-identity relightable head decoders
- Capturing the long tail of human expressivity (sweat, tiredness, blood flow)
- Converting low-quality (mobile, full-body) captures into high-quality head and hand outputs at more than four subjects
- Distribution of petabyte-scale capture data to academic labs
- Misuse mitigation: authentication, watermarking, disclosure interfaces
Benchmark gaps:
- Goliath-4 / number of subjects: Only 4 subjects carry the full 8-modality paired capture, which the authors say restricts low-to-high quality conversion research.
- Ava-256 / released image quality: Released at 2x or 4x downsampled resolution, about 80 of about 170 cameras, 7.5 or 15 fps instead of 30 fps, to fit 4 to 32 TB releases.
Restrictive assumptions: High-resolution multi-view dome with about 170 synchronized cameras (head) or about 230 cameras in a 5.5 m dome (body) to build avatars; Uniform illumination in Ava-256; time-multiplexed group-light illumination needed for relightable Goliath captures; Headset driver relies on pseudo ground truth from cycle consistency with personalized avatars built from dome captures; Personalized head, hand and body models are trained per subject; Hands captured separately (left and right) in the head scanner, not during whole-body activity

## [1431] Multiface: A Dataset for Neural Face Rendering (arXiv 2022, dataset, S7)
Source: https://arxiv.org/html/2207.11243; confidence HIGH.
Field cannot yet: The field cannot yet synthesize unseen expressions from unseen viewpoints with fine detail without dense multi-view studio capture of that identity.
Stated limitations:
- Relighting is excluded; data captured under uniform diffuse illumination. [1 Introduction]
- The baseline model fails on high-frequency details. [5.2 Results and Analysis, Qualitative Results]
- Sequential mesh tracking is too costly to run on all data; sentences are not processed by it. [3.4 Data Processing]
- Joint novel view and novel expression synthesis is harder than either alone. [5.2 Results and Analysis]
- Camera failures reduce available views in some captures. [3.2 Capture Studio]
Open problems listed:
- Novel view synthesis when cameras cannot be placed everywhere
- Novel expression synthesis for expressions not enacted during capture
- Relighting under unseen lighting configurations
- Data-hungry neural face models need dense high-resolution captures
- High-frequency details such as teeth and eyelashes
Benchmark gaps:
- Multiface (identity m-20180227) / screen-space reconstruction error: Baseline joint novel view plus expression error 1.272 at 17 training cameras and 1.088 at 37, versus 0.770 for novel view only at 37 cameras.
Restrictive assumptions: Dense multi-view dome of 40 to 160 synchronized cameras at 1.2 m radius; Uniform, diffused illumination; Tracked mesh and average texture across all views as model input; Per-identity training of about one day on eight V100 GPUs; Only 13 identities; ablation on a single identity

## [1432] RenderMe-360: A Large Digital Asset Library and Benchmarks Towards High-fidelity Head Avatars (NeurIPS 2023, benchmark, S7)
Source: https://arxiv.org/html/2305.13353; confidence HIGH.
Field cannot yet: The field cannot yet reconstruct and animate full human heads robustly across accessories, curly hair, unseen identities and out-of-distribution expressions.
Stated limitations:
- State-of-the-art head avatar methods still face real-world obstacles. [Abstract]
- No robust paradigm exists for case-specific multi-view head reconstruction as accessory complexity increases. [4.1.1 Single-ID NVS]
- All novel-expression methods fail on out-of-distribution expressions. [4.2 Novel Expression Synthesis]
- Hair rendering degrades sharply for curly hair. [4.3 Hair Rendering]
- Benchmark coverage is incomplete. [5 Discussion]
- Generalizable methods learn mean-head priors but fail on long-tail cases. [4.1.2 Generalizable NVS]
Open problems listed:
- Robust case-specific multi-view head reconstruction with accessories
- Generalizing to unseen identities (appearance and geometry jointly)
- Long-tail appearance distributions in generalizable NVS
- Out-of-distribution expression synthesis (tongue out) and subtle motions
- Thin structures and hair strand rendering, especially curly hair
- Temporally sharp dynamic hair performance capture
- OOD hair editing with accessories and full hair-region completeness
- Lack of unified data and criteria for talking-head benchmarking
- Gap between saturated standard datasets and real-world scenarios
- Long-tail matting for hairstyles and accessories
Benchmark gaps:
- RenderMe-360 Single-ID NVS / PSNR/SSIM/LPIPS: All four methods (Instant-NGP, NeuS, NV, MVP) drop with deformable and complex accessories.
- RenderMe-360 Generalizable NVS / PSNR/SSIM/LPIPS: Unseen-ID protocol shows larger drop than unseen-expression for IBRNet, VisionNeRF, KeypointNeRF.
- RenderMe-360 Hair Rendering / PSNR/SSIM/LPIPS: Curls subset causes sharp drops under all metrics for static and dynamic NVS methods.
- RenderMe-360 Novel Expression / PSNR/SSIM/LPIPS/L1: NeRFace, IM Avatar, PointAvatar all fail on OOD expressions such as tongue out.
Restrictive assumptions: 60 synchronized 2448x2048 cameras at 30 fps in a studio rig; Background captured before each recording for matting; Chessboard calibration before every recording round; FLAME fitting uses scans only on keyframes; shape fixed per subject from neutral frames; Studio lighting; head-only capture

## [1433] DNA-Rendering: A Diverse Neural Actor Repository for High-Fidelity Human-centric Rendering (ICCV 2023, dataset, S7 S2)
Source: https://arxiv.org/html/2307.10173; confidence HIGH.
Field cannot yet: The field cannot yet animate human avatars that hold or interact with objects, or wear loose garments, in novel poses without objects stretching or vanishing.
Stated limitations:
- Current animatable avatar methods fail on loose-clothing deformation and object interaction in novel poses. [Appendix C.2.2 Novel Pose Animation]
- Interactive objects cannot be modelled by skinning-based avatars. [4.3 Benchmark Results]
- Capture constrained to uniform lighting and 15 fps; FOV set for one actor. [Appendix A.5 Limitations on Data Collection]
- Capture failures from motion leaving the FOV and data-transmission frame loss. [Appendix A.5, Failure Cases]
- Matting refinement remains imperfect; only sequences without major artifacts are released. [Appendix E Future Work]
- High texture and non-rigidity remain hard even for seen poses. [4.3 Benchmark Results (NVS)]
Open problems listed:
- Modeling loose-clothing non-rigid deformation in animatable avatars
- Modeling interactive objects and out-of-body motion while keeping explicit body representations
- Robust human-centric matting at scale
- Capture under varied lighting, multi-person scenes, high-speed subtle motion, and multi-sensory data
- Unified cross-institution benchmarking and leaderboards for human rendering
- Garment modeling and animation, human shape completion benchmarks
- Generalization to novel identities with large pose and appearance variation
Benchmark gaps:
- DNA-Rendering novel pose split / PSNR/SSIM/LPIPS: Deformation-Hard and Interaction-Medium/Hard splits are described as insurmountable for current methods in novel poses.
- DNA-Rendering NVS split / PSNR/SSIM/LPIPS: Texture-Hard and Deformation-Hard remain challenging even in seen poses.
Restrictive assumptions: 68-camera dome (60 RGB plus 8 Azure Kinect RGB-D) of 3 m radius; Single actor per capture (with at most the interacted object) inside a constrained FOV; Uniform invariant illumination; 15 fps; SMPLX fitting from multi-view keypoints; Methods benchmarked assume SMPL-based skinning or bone coordinates for animation

## [1434] MVHumanNet: A Large-scale Dataset of Multi-view Daily Dressing Human Captures (CVPR 2024, dataset, S7)
Source: https://arxiv.org/html/2312.02963; confidence HIGH.
Field cannot yet: The field cannot yet collect human capture data at scale that includes complex clothing and human-object interaction.
Stated limitations:
- Experiments use only part of the data due to scale, hardware and annotation constraints. [4 Experiments]
- Dataset focuses on everyday clothing because complex clothing and human-object interaction hinder scaling. [1 Introduction]
- Human generalizable NeRFs still perform poorly on diverse cases. [4.2 NeRF Reconstruction]
- Models trained only on MVHumanNet suffer domain gap on other datasets. [Figure 6 caption]
- Reliance on SMPL in generalizable NeRFs may hurt generalization. [5 Conclusion, Future Work]
Open problems listed:
- Lack of large-scale 3D human data comparable to Objaverse or MVImgNet
- Scaling datasets that include complex clothing and human-object interaction
- Generalizable human NeRF beyond SMPL priors
- Domain gap across human capture datasets
- Acquiring 3D skeletons in everyday settings
Benchmark gaps:
- HuMMan (cross-dataset) / PSNR/SSIM/LPIPS: Models trained only on MVHumanNet show a domain gap; finetuning needed to beat HuMMan-only training.
Restrictive assumptions: Indoor 360-degree multi-view RGB rigs (48 cameras 12MP and 24 cameras 5MP); Everyday casual clothing only; no deliberate human-object interaction; Annotations from off-the-shelf tools (RVM plus SAM masks, OpenPose, triangulation, SMPL/SMPLX fitting); Studio controlled lighting and CharuCo calibration

## [1435] MVHumanNet++: A Large-scale Dataset of Multi-view Daily Dressing Human Captures with Richer Annotations for 3D Human Digitization (arXiv 2025, dataset, S7)
Source: https://arxiv.org/html/2505.01838; confidence HIGH.
Field cannot yet: The field cannot yet obtain measured geometry ground truth (depth, normals) at the scale of large real multi-view human datasets.
Stated limitations:
- No ground-truth normals; normals are pseudo labels from Sapiens. [III-C Data Annotation, Normal Maps]
- No depth sensor; depth maps are rendered from normal-refined 2DGS. [III-C Data Annotation, Depth Maps]
- Experiments use 62% of the data due to size, hardware and annotation constraints. [IV Experiments]
- Faces distort in latent-diffusion multi-view generation. [IV-F Human Generative Model]
- Off-the-shelf 3D reconstruction is poor on humans without human training data. [IV-G Reconstruction from Unconstraint Human Images]
Open problems listed:
- Absence of large-scale real human 3D datasets
- Missing ground-truth normals and depth for real multi-view human captures
- Scaling capture to complex clothing and human-object interaction
- Generalizable feed-forward human reconstruction under large view baselines
- Face fidelity in multi-view human generation
- Human-specific unconstrained reconstruction (DUSt3R-style) depth ambiguity
Benchmark gaps:
- HuMMan (cross-dataset) / PSNR/SSIM/LPIPS: Models trained only on MVHumanNet++ suffer domain gap until finetuned.
Restrictive assumptions: RGB-only multi-view studio rigs (48 and 24 cameras); Pseudo-label normal and depth maps rather than measured geometry; Everyday clothing; complex clothing and human-object interaction de-emphasized for scalability; Per-subject Animatable Gaussians evaluation uses 16 views

## [1436] NeRSemble: Multi-View Radiance Field Reconstruction of Human Heads (SIGGRAPH 2023, dataset, S7)
Source: https://arxiv.org/html/2305.03027; confidence HIGH.
Field cannot yet: The field cannot yet reconstruct dynamic heads with fast hair motion and occluded mouth interiors from sparse or monocular input with a generalizable prior.
Stated limitations:
- Deformation field cannot capture fast hair motion. [5.8 Limitations]
- Per-sequence optimization; no cross-sequence prior. [5.8 Limitations]
- Occluded mouth interior produces hollow-face artifacts. [Figure 11 Failure cases]
- Inherits Instant NGP weakness: no refraction modelling. [5.6 Comparison on Neural 3D Video Dataset]
- Eye specular reflections cause artifacts. [Figure 11 Failure cases]
Open problems listed:
- Fast hair motion in dynamic head reconstruction
- Generalization over identities and expressions instead of per-sequence fitting
- Monocular dynamic head capture via learned 4D priors
- Reconstruction of occluded regions such as mouth interior
- Complex hair, varied reflectance and non-rigid skin in NVS
- Comparable benchmarks for human head NVS
Benchmark gaps:
- NeRSemble (10 sequences, 4 held-out views) / PSNR/SSIM/LPIPS: NeRSemble 31.8 / 0.875 / 0.212 versus DyNeRF 30.6 / 0.860 / 0.254; extreme evaluation viewing angles.
- Neural 3D Video / PSNR: Cannot perfectly capture refraction effects of window panes and glass bottles.
Restrictive assumptions: 16 calibrated, PTP-synchronized 7.1 MP cameras at 73 fps; Strong diffused LED lighting and white-wall background captured beforehand for matting; COLMAP depth supervision from 12 training views; Per-sequence optimization; head only; Color checker calibration across cameras

## [1437] HumanRF: High-Fidelity Neural Radiance Fields for Humans in Motion (ActorsHQ dataset) (SIGGRAPH 2023, dataset, S7)
Source: https://arxiv.org/html/2305.06356; confidence HIGH.
Field cannot yet: The field cannot yet produce controllable, real-time, production-quality free-viewpoint humans from anything less than dense high-resolution multi-view capture.
Stated limitations:
- Requires the high-end ActorsHQ capture and per-sequence optimization. [5.6 Limitations and Future Work]
- No articulation control outside training poses. [5.6 Limitations and Future Work]
- Rendering is slow. [5.6 Limitations and Future Work]
- Per-frame masks cause silhouette flicker. [5.6 Limitations and Future Work]
- Comparisons run at 4x downscaled resolution because baselines fail at full resolution. [5.1 Evaluation Protocol]
Open problems listed:
- Modeling fast and complex motion photo-realistically at high resolution
- Scaling dynamic representations to long sequences under memory budgets
- Driving high-quality avatars from monocular input
- Articulation control outside training poses
- Real-time rendering
- Temporally consistent matting
Benchmark gaps:
- ActorsHQ (4x downscaled, 8 actors) / PSNR / LPIPS: HumanRF PSNR falls from 30.30 at 20 frames to 29.05 at 1000 frames; LPIPS rises from 0.095 to 0.107.
Restrictive assumptions: 160 synchronized 12MP cameras at 25 fps with 420-LED synchronized lighting; Capture volume 1.6 m diameter by 2.2 m height, single actor; Per-frame MVS meshes (RealityCapture) for foreground masks; Per-sequence optimization, offline; 8 actors, 16 sequences of choreographed actions in everyday clothing

## [1438] HuMMan: Multi-Modal 4D Human Dataset for Versatile Sensing and Modeling (ECCV 2022, dataset, S7 S4)
Source: https://arxiv.org/html/2204.13686; confidence HIGH.
Field cannot yet: The field cannot yet recover accurate parametric humans from real, sparse consumer depth point clouds or transfer models across depth sensors.
Stated limitations:
- Point-cloud-based parametric human recovery performs poorly on real commercial RGB-D point clouds because existing methods depend on synthetic data. [Experiments: 3D Parametric Human Recovery]
- Large domain gap across devices (Kinect to iPhone), especially for point-cloud methods because the mobile depth is much sparser. [Experiments: Mobile Device]
- The mesh reconstruction toolchain produces shrunk or dilated geometry under self-occlusion in complicated poses. [Toolchain: Textured Mesh Reconstruction]
- Kinect depth is noisy at subject boundaries, requiring aggressive boundary removal and outlier filtering. [Toolchain: Point Cloud]
- The iPhone cannot be hardware-synchronized; software TCP synchronization leaves errors up to one Kinect frame. [Hardware Setup: Synchronization]
- iPhone LiDAR point clouds are sparser and noisier than Kinect's, and the device reports no accuracy figure. [Supplementary: Point clouds from Kinect and iPhone]
- Cross-view and cross-action generalization of 3D keypoint detection and HMR degrades sharply. [Supplementary: Additional benchmarks (P2, P3)]
Open problems listed:
- Fine-grained action recognition among similar intra-action variants
- Point cloud-based parametric human recovery on real (not synthetic) RGB-D point clouds
- Dynamic human mesh sequence reconstruction
- Cross-device domain gap (regular RGB-D to mobile LiDAR), especially for point-cloud methods
- Multi-task joint training across sensing and modeling tasks
- Cross-view generalization for 3D keypoint detection and parametric recovery
- Cross-action generalization to unseen poses
Benchmark gaps:
- HuMMan / Action recognition Top-1 (2s-AGCN): 74.1% on HuMMan versus 88.9% (NTU RGB+D 60) and 82.9% (NTU 120); about 30% Top-1/Top-5 gap from fine-grained intra-actions.
- HuMMan / MPJPE / PA-MPJPE (mm), parametric human recovery: VoteHMR (point cloud input) 144.99 / 106.32 versus HMR 54.78 / 36.14.
- HuMMan iPhone test set / MPJPE / PA-MPJPE (mm): Kinect-trained VoteHMR 255.71 / 162.00 versus iPhone-trained 83.18 / 61.69; Kinect-trained HMR 97.81 versus 72.62.
- AIST++ (cross-dataset) / MPJPE (mm), 3D keypoint lifting: FCN trained on H36M 133.9, on HuMMan 116.4; Video3D 128.5 and 109.2, versus 78.5/73.1 in-domain.
- HuMMan / Chamfer distance, geometry reconstruction: PIFu 7.92 and PIFuHD 7.73 versus Function4D 1.80.
Restrictive assumptions: 10 synchronized Kinect RGB-D cameras plus one iPhone in a fixed indoor capture studio; Custom light-absorbent chessboard needed for Kinect IR calibration; Single subject performing anatomically designed atomic body movements, not daily-activity tasks; Pseudo ground truth from multi-view triangulated 2D keypoints and SMPL fitting with high-resolution per-subject scans

## [1439] HumanOLAT: A Large-Scale Dataset for Full-Body Human Relighting and Novel-View Synthesis (ICCV 2025, dataset, S7)
Source: https://arxiv.org/html/2508.09137; confidence HIGH.
Field cannot yet: The field cannot yet relight full-body humans photo-realistically, including skin subsurface scattering, self-shadowing, and fine hand and face detail.
Stated limitations:
- Subjects sway during the 11-second OLAT capture, blurring image-based relighting and requiring optical-flow motion compensation. [3.3.3 Motion compensation]
- Lights mounted on the moving entry hatch have uncertain 3D positions and should be ignored. [3.3 Calibration]
- Dataset covers static humans only: 21 subjects in three static poses each. [2 Related Work]
- Evaluated Gaussian inverse-rendering methods stay blurry with hand and face artifacts and miss specular highlights and sharp shadows. [4.1 Inverse Rendering from OLAT Illuminations]
- Current methods do not reproduce complex human lighting effects. [5 Conclusion]
Open problems listed:
- Photo-realistic full-body relighting under complex light transport from intricate geometry and diverse materials (skin, hair, clothing)
- Subsurface scattering and self-shadowing in human relighting
- Specular highlights and sharp shadows not captured
- Hand and face region quality in relightable Gaussian avatars
- Scarcity of public full-body OLAT data; reliance on synthetic data or learned priors yields artifacts
- Full-body OLAT capture of moving subjects (involuntary motion artifacts during long captures)
- Illumination harmonization methods lacking full-body OLAT training data
Benchmark gaps:
- HumanOLAT / PSNR / LPIPS / SSIM (novel view plus novel light): Methods that do well on object-centric scenes face challenges on human captures; renderings blurry with hand/face artifacts (Table 2, six captures).
- HumanOLAT / Qualitative illumination harmonization: IC-Light lacks subsurface scattering and self-shadowing and loses facial details.
Restrictive assumptions: Specialized, costly lightstage with calibrated multi-view cameras and controllable LEDs; Static subjects holding poses; evaluated methods assume static objects and need motion compensation; Calibration via proprietary Metashape plus marker-based canonical frame; Images downsampled to 1K for baseline training

## [1440] A Survey on 3D Human Avatar Modeling -- From Reconstruction to Generation (arXiv 2024, survey, S7)
Source: https://arxiv.org/html/2406.04253; confidence HIGH.
Field cannot yet: The field cannot yet generate or reconstruct detailed, animatable humans with loose clothing and human-object interaction from sparse inputs efficiently.
Stated limitations:
- Survey cannot be complete given the volume of publications and excludes human mesh recovery. [2 Scope of This Survey]
- PIFu-style single-view methods struggle with complex poses, self-occlusion and depth ambiguity. [3.1 Pixel-aligned Implicit Function]
- PaMIR fails when hands and clothes are close together in dynamic motion. [3.3 Incorporation of 3D Priors]
- 3D-aware GANs show artifacts and cannot generate beyond training data. [6.4 Discussion and Limitations of GAN-based Methods]
- Text-to-3D methods cannot control motion and often miss hands or feet. [7.2 Diffusion Model-based 3D Human Generation]
- Human-object interaction motion generation is open. [8.1.3 3D Human Animation]
Open problems listed:
- Training efficiency and stability of text-to-avatar optimization (hours per model; SDS stochasticity; initialization)
- Geometric quality: noisy geometry from SDS, worse for Gaussian-based generation
- Reliance on SMPL/SMPL-X priors limits loose clothing generation and animation
- Single image plus text: reconstructing unseen areas and correct pose remains a challenge
- Multi-view plus text: efficient multi-view feature fusion and consistency between views and prompts; dense consistent multi-view human generation
- Automatic local 3D human editing without changing other parts
- Realistic text-driven human motion generation and avatar animation
- Human-object interaction motion sequence generation is a hard open problem
- 4D animation of complex poses and large movements
- Building a 3D feature space from generated multi-view images; capturing human pose and clothing topology in 3D foundation models
- Large reconstruction models fail to capture human detail and dynamics
- Non-structural nature of 3DGS hampers geometric optimization
- Incorporating 2D Gaussian parameter maps into generative pipelines for real-time 3D generation
- GAN-based: artifacts and dependence on training data
- Scarcity of high-quality 3D human training data
Restrictive assumptions: Covers RGB-based neural methods; human mesh recovery explicitly out of scope; Many surveyed methods rely on SMPL/SMPL-X priors and scarce 3D scan training data

## [1442] SmartPortraits: Depth Powered Handheld Smartphone Dataset of Human Portraits for State Estimation, Reconstruction and Synthesis (arXiv 2022, dataset, S7)
Source: https://arxiv.org/html/2204.10211; confidence HIGH.
Field cannot yet: The field cannot yet turn casual handheld smartphone captures of slightly moving people into high-quality 3D reconstructions reliably.
Stated limitations:
- Volunteers cannot stay perfectly still, making the nominally static capture non-static. [1 Introduction]
- MoCap ground truth exists only in the lab; other locations rely on pseudo ground truth with a no-reference error bound. [5.2 Eval Generalization]
- Rolling-shutter smartphone camera is calibrated with a global-shutter model. [3 Calibration]
- Independent smartphone and depth camera make time synchronization hard; small offsets degrade pose estimation. [3 Data acquisition]
- Trajectory accuracy does not translate directly into downstream reconstruction/synthesis quality. [7 Discussion]
Open problems listed:
- Whether handheld in-the-wild trajectories can be converted into 3D portraits of people
- Non-static humans during supposedly static capture
- Computational cost of reconstruction and rendering remains prohibitive
- Mismatch between trajectory accuracy and downstream reconstruction/synthesis quality
- VI initialization without a static start
- Ground truth unavailable outside the lab
Benchmark gaps:
- SmartPortraits / ATE/RPE (full-reference vs pseudo GT): Real-time VI methods less accurate than V methods; only LDSO, OKVIS, PVIO, SVO2, VINS can be ordered given pseudo-GT bound.
- SmartPortraits / MOM (no-reference map metric): Up to about 2 cm for most locations, comparable to depth sensor noise.
Restrictive assumptions: Subjects asked to stay as still as possible (near-static human); Rig with smartphone plus external Azure Kinect DK depth camera; Semicircular handheld trajectories; MoCap ground truth only in one lab location

## [1443] MVP-Human Dataset for 3D Human Avatar Reconstruction from Unconstrained Frames (arXiv 2022, dataset, S7)
Source: https://arxiv.org/html/2204.11184; confidence HIGH.
Field cannot yet: The field cannot yet reconstruct detailed clothed avatars from unconstrained frames when body pose fitting is inaccurate.
Stated limitations:
- Inaccurate pose estimation maps 3D points to wrong image locations, fusing irrelevant features. [V Experiments]
- Local features are unreliable under misalignment across free poses and views, yielding overly smooth results. [I Introduction]
- Training requires multi-view-and-pose images with T-pose shapes, which is not publicly available otherwise. [I Introduction]
Open problems listed:
- Reconstructing avatars from frames without camera calibration, capture-space or action constraints
- Fusing snapshots in diverse views and poses into one reconstruction
- Back-side artifacts in single-image reconstruction
- Lack of public multi-pose scan datasets with skinning weights
Benchmark gaps:
- MVP-Human / Chamfer / P2S (cm), canonical shape: Best (Ours) 1.72 / 1.34 cm; PIFu 4.96 / 6.19; ICON 3.96 / 3.96.
Restrictive assumptions: Per-frame SMPL fitting provides camera and body pose; Single clothed person, rigid clothing reposed via linear blend skinning; Target is a canonical T-pose shape; Training on renderings of 3D scans captured in a multi-camera scanner studio

## [1444] REHAB24-6: Physical Therapy Dataset for Analyzing Pose Estimation Methods (unknown (listed-venue publication not confirmed) 2024, dataset, S7 S4)
Source: https://zenodo.org/api/records/13305825 (dataset record description only; paper full text on Springer not accessible); confidence LOW.
Field cannot yet: Not determinable from the dataset record alone.
Stated limitations:
- 2D ground truth is derived by projecting mocap data with a simplified pinhole model and tape-measured camera positions. [Zenodo record: Recording Conditions]
- Some videos were shot in natural evening light with worse visibility. [Zenodo record: Recording Conditions]
Restrictive assumptions: Subjects wear motion capture body suits with 41 markers; 16 OptiTrack cameras in an 8.2 x 7 m lab, 2 RGB cameras; Single subject, 10 subjects total, six exercises

## [1456] OakInk2: A Dataset of Embodied Hands-Object Manipulation in Long-Horizon Complex Task Completion (CVPR 2024, dataset, S3 S1 S6)
Source: https://arxiv.org/pdf/2403.19417; confidence HIGH.
Field cannot yet: The field cannot yet generate or plan bimanual long-horizon manipulation end-to-end from text, nor capture it without marker-based MoCap and manual cleaning.
Stated limitations:
- MoCap marker data contain errors requiring manual cleaning by annotators. [Supp. A.2 Data Cleaning]
- No end-to-end framework exists for text-to-motion complex task completion; they decompose into three stages. [5.3 Complex Task Completion]
- LLM primitive planning succeeds only 36% overall and fails for tasks with more than five primitives. [Supp. Evaluations of Primitive Planning]
Open problems listed:
- Decomposing long-horizon complex tasks into dependent primitives
- End-to-end text-to-manipulation generation
- Task-aware hand motion fulfilling object trajectories
- LLM reasoning about affordance dependencies for complex tasks
Benchmark gaps:
- OakInk2 / Primitive planning success rate (GPT-4): 36% overall; 44% for three or fewer primitives; 20% for 3-5; 0% above five.
- OakInk2 / Perceptual score (TaMF): Generated motions 3.64 +/- 0.85 versus dataset 4.66 +/- 0.48.
Restrictive assumptions: Optical MoCap (12 OptiTrack cameras) with markers on upper body, both hands and objects; Object geometries and object trajectories known for motion fulfillment (TaMF); Object trajectories retrieved and re-targeted from expert demonstrations via an oracle; Multi-view benchmark uses camera calibration; 9 subjects, 75 objects

## [1463] Gaze-guided Hand-Object Interaction Synthesis: Dataset and Method (IEEE TMM 2026, dataset, S1 S3)
Source: https://arxiv.org/html/2403.16169; confidence HIGH.
Field cannot yet: The field cannot yet capture or synthesize gaze-aligned bimanual manipulation of articulated objects without marker-based object tracking.
Stated limitations:
- Dataset excludes articulated objects. [VII Conclusion]
- Gaze is sparse and noisy, hard to interpret for intention. [I Introduction]
- Diffusion alone does not ensure contact or avoid penetration; guidance needed. [IV-B 2 Hand Kinematic Synthesis]
Open problems listed:
- Articulated objects in gaze-guided HOI
- Encoding sparse noisy gaze
- Physical plausibility of synthesized motion
- Multi-modal conditioning (text, EMG)
Benchmark gaps:
- GazeHOI / Success Rate (reconstruction, test): ArcticNet-SF 29.7, ArcticNet-LSTM 33.0, Keypoint Transformer 44.9.
- GazeHOI / MPVPE / FOL (mm), synthesis, unseen objects: Best method 118.7 / 150.2 mm.
Restrictive assumptions: Rigid objects only, tracked with at least eight reflective markers via OptiTrack and scanned meshes; 12 hardware-synchronized RGB cameras; hand pose from MediaPipe triangulation and MANO fitting; Head-mounted eye tracker with marker-based ego calibration; Reconstruction task assumes known object mesh

## [1482] Wh0: Generative World Models as Scalable Sources of Egocentric Human Hand Manipulation Data (arXiv 2026, dataset, S6)
Source: https://arxiv.org/html/2606.22136; confidence HIGH.
Field cannot yet: Generate physically plausible, occlusion-robust, bimanual hand-object interaction data whose reconstructed finger poses are accurate enough to supervise robots without real teleoperation data.
Stated limitations:
- Limited by video generation quality, hand reconstruction accuracy, human-robot morphology mismatch, dependence on strong pretraining, and task scope. [6 Conclusion and Limitations]
- The generator can produce physically implausible interactions, unexpected objects, or inconsistent long-horizon videos. [6 Conclusion and Limitations]
- Hand-object occlusion degrades reconstructed finger poses and yields noisy action supervision. [6 Conclusion and Limitations]
- The robot hand is larger than the human hand and can disturb objects during execution. [6 Conclusion and Limitations]
- WM-H gives little benefit without a human-video-pretrained backbone; it complements rather than replaces large-scale pretraining. [6 Conclusion and Limitations]
- Experiments cover only single-arm pick-and-place; bimanual, tool-use and long-horizon tasks are left for future work. [6 Conclusion and Limitations]
- The policy action space handles only the right hand. [4 Policy Architecture]
Open problems listed:
- Physically plausible, temporally consistent long-horizon generated manipulation video.
- Accurate finger reconstruction under hand-object occlusion for generated data.
- Human-robot morphology mismatch (robot hand size).
- Dependence on large-scale human-video pretraining.
- Bimanual, tool-use and long-horizon tasks.
- Instruction validity and embodiment-alignment editing fidelity in synthetic data pipelines.
Benchmark gaps:
- 18 real-world dexterous tasks, Unitree G1 (zero-shot unseen tasks) / success rate: Best result is 38.9% zero-shot success (VITRA robot-only baseline 8.3%), so most unseen-task trials still fail.
- WM-H user study (72 AI practitioners) / perceived realism: Only 37.7% of generated videos (134/355 trials) were judged as real; participants mainly used physics, layout and contact cues to spot fakes.
Restrictive assumptions: Requires background images captured by the deployment camera at the same viewpoint and resolution, with a human hand placed as a scale anchor.; Hand action labels come from monocular reconstruction (HaWoR) of generated video, which is noisy under hand-object occlusion.; Requires a large human-video-pretrained VLA backbone (VITRA).; Still needs 400 real teleoperated robot demonstrations for co-training.; Right hand only; single-arm pick-and-place tasks.; Static, single deployment camera on one robot platform (Unitree G1 with Inspire hands).

## [1483] HandsOnWorld: Unconstrained Egocentric Video Generation with Camera-Disentangled Hand Control (arXiv 2026, dataset, S1 S6)
Source: https://arxiv.org/html/2607.02075; confidence HIGH.
Field cannot yet: Obtain accurate, finger-level 3D hand annotations for unconstrained moving-camera egocentric video without instrumented capture, especially under self-occlusion and missed detections.
Stated limitations:
- Control signal rasterizes only the visible hand surface, so self-occluded hand pose changes are not encoded. [Appendix F Limitations and Future Work (Occlusion)]
- The pipeline cannot tell whether a missing detection means the hand left the image or the detector missed it. [Appendix F Limitations and Future Work (Missing detections)]
- Clips with long uncertain detection gaps are discarded rather than used. [Appendix F Limitations and Future Work (Missing detections)]
- On ARCTIC (tabletop, little ego-motion) the method only matches the strongest baselines rather than surpassing them. [6.3 Comparison of Control Signals]
- Plucker hand moment becomes numerically sensitive when the surface normal is nearly parallel to the viewing ray. [5 Normal-degeneration corner case]
Open problems listed:
- Encoding self-occluded hand regions in control signals.
- Handling missing or ambiguous hand detections in in-the-wild video.
- Protagonist hand identification among bystander hands.
- Disentangling camera ego-motion from hand motion in control signals.
- Scaling 3D hand annotation beyond instrumented tabletop capture (data annotation pyramid trade-off between label fidelity and scene diversity).
Benchmark gaps:
- ARCTIC / W-JPE (world-space joint error): Best method still has W-JPE 114.00 and WA-JPE 46.91; gains over Hand2World (118.45) are small.
- EgoVid-Pro validation / PSNR / FVD: Best PSNR is 17.42 and FVD 274.51, indicating generated videos remain far from pixel-faithful.
Restrictive assumptions: Annotations come from monocular reconstruction (WiLoR + HaWoR), filtered heavily; undetected frames are linearly interpolated.; Requires first frame plus a target 3D camera and hand trajectory as input.; Protagonist identification relies on fitting a single SMPL body anchored at the egocentric camera.; Evaluation of hand accuracy uses HaWoR re-reconstruction of generated video, except on H2O.; Training subset restricted to 34,078 clips with complete bimanual annotations over 81 frames.

## [1489] Scalable vision-language-action model pretraining for robotic manipulation with real-life human activity videos (arXiv 2025, dataset, S6)
Source: https://arxiv.org/html/2510.21571; confidence HIGH.
Field cannot yet: Recover accurate metric 3D hand motion and well-segmented actions from unconstrained monocular video at scale without label noise.
Stated limitations:
- Constructed pretraining data still contains inaccuracies due to limits of current 3D reconstruction and VLM capability. [6 Discussion and Future Work]
- Data construction and training target only short-horizon atomic skills. [6 Discussion and Future Work]
- Robot experiments are primarily single-handed; bimanual shown only by a simple hand-over demo. [6 Discussion and Future Work]
- Recovering metric 3D hand motion is difficult with single, uncalibrated, moving cameras; noisy labels are accepted for pretraining. [1 Introduction]
- Temporal action segmentation remains an open problem with no existing methods meeting their needs. [1 Introduction]
Open problems listed:
- Accurate metric 3D hand and camera motion from uncalibrated moving monocular video.
- Temporal atomic action segmentation of unscripted video.
- Long-horizon task structure from human video.
- Bimanual manipulation transfer.
- Multi-view and tactile integration.
Benchmark gaps:
- Unseen-environment grasping benchmark (47 environments, 396 objects) / predicted finger-object distance avg/median (cm): Best model still ends 8.8 / 6.2 cm from the target object.
- Real-robot unseen objects and categories (Table 4) / success rate: Baselines such as VPP, latent-action and OXE pretraining reach 0 to 8.3% on unseen settings.
Restrictive assumptions: Monocular egocentric video with estimated intrinsics, SLAM camera pose and MANO hand reconstruction as action labels.; Human hand treated as robot end-effector with a simple nearest-joint mapping to the robot hand, no direct pose transfer.; Requires teleoperated robot fine-tuning data (1.2K trajectories).; Grasp benchmark renders synthetic hands onto RGB-D images rather than using real hand observations.

## [1495] Human2Robot: Learning Robot Actions from Paired Human-Robot Videos (arXiv 2025, dataset, S6)
Source: https://arxiv.org/html/2502.16587; confidence HIGH.
Field cannot yet: Collect precisely aligned human-robot demonstrations for dexterous, contact-rich tasks beyond pick-and-place.
Stated limitations:
- The human-hand to gripper embodiment gap remains unsolved for teleoperation and is left for future work. [3.1 Coordinate Alignment for Teleoperation]
- Paired-video teleoperation cannot collect difficult tasks such as screwing, so training and testing focus on pick-and-place. [5.1 Experimental Setups]
- KNN inference without human video loses 10-20% success compared with full Human2Robot. [5.2 Main results]
Open problems listed:
- Human-to-robot embodiment gap for paired data collection.
- Collecting paired data for dexterous tasks such as screwing.
- Fine-grained frame-level human-robot alignment datasets.
Benchmark gaps:
- H&R real-robot generalization (20 trials each) / success rate: Instance generalization 70%, position and background 80%; baselines XSkill and VPP fail on instance and background.
Restrictive assumptions: Paired data requires VR teleoperation (Meta Quest 3) with anchor-based coordinate alignment and two mirrored workspaces.; Third-person static RealSense cameras with identical viewpoints.; Right-hand demonstrations with a parallel-gripper xArm.; Mostly pick-and-place and simple tasks; 2,600 episodes in one lab setup.; Requires a human video demonstration at test time, unless KNN retrieval is used.

## [1499] AVI-HT: Adaptive Vision-IMU Fusion for 3D Hand Tracking (arXiv 2026, dataset, S1 S4)
Source: https://arxiv.org/html/2605.21714; confidence HIGH.
Field cannot yet: Track fingers accurately under heavy object occlusion from vision alone, without instrumenting the hand with a specific sensor glove.
Stated limitations:
- The sensing glove changes hand appearance, creating a domain gap for downstream pipelines expecting bare hands. [6 Conclusion (Limitations)]
- Generalization to other gloves with different sensor layouts or IMU specs is unvalidated. [6 Conclusion (Limitations)]
- Performance degrades at higher IMU noise; MKPE rises from 10.335 mm to 12.344 mm. [5.3 Sensitivity Study]
- Temporal alignment between vision and IMU is critical; error curves form a V-shape around zero shift. [5.3 Sensitivity Study]
- IMU-only tracker cannot estimate global wrist position with 6-DoF IMUs. [5.1 3D Hand Tracking Accuracy]
Open problems listed:
- Lack of datasets pairing egocentric vision, IMU and 3D ground truth under HOI occlusion.
- Existing 3D hand datasets are vision-only, studio-captured, and limited in pose range.
- Glove appearance domain gap.
- Glove-agnostic, cross-device vision-IMU fusion.
Benchmark gaps:
- DexGloveHOI / MKPE (UMETrack): Best MKPE 10.359 mm and fingertip MKPE 13.253 mm remain.
- DexGloveHOI / PA-MPJPE (MANO): Best PA-MPJPE 10.519 mm; F@5 only 0.628.
Restrictive assumptions: Requires wearing a specific 12-IMU data glove.; Meta Quest monochrome egocentric cameras; UME variant uses two camera views with known intrinsics and extrinsics.; Ground truth from marker-based mocap with per-session calibration of markers and IMU orientation.; Dataset has only 4 participants and 3.5 hours; single gloved hand.; Wrist assumed largely visible to provide global anchor.

## [1526] PCIE_Pose Solution for EgoExo4D Pose and Proficiency Estimation Challenge (arXiv 2025, method, S4 S1)
Source: https://arxiv.org/html/2505.24411; confidence HIGH.
Field cannot yet: Estimate egocentric 3D hand pose with low absolute (non-Procrustes) error under occlusion; root-relative errors near 25 mm persist.
Open problems listed:
- Occlusion and subtle movement in egocentric 3D hand pose estimation.
- Body pose estimation when the body is largely outside the egocentric view.
- Skill proficiency classification from egocentric video (accuracy 0.53).
Benchmark gaps:
- Ego-Exo4D Hand Pose (test) / MPJPE (mm): Winning entry still has 24.80 mm MPJPE (8.31 mm PA-MPJPE).
- Ego-Exo4D Body Pose (test) / MPJPE (cm): Winning entry 11.25 cm MPJPE.
- Ego-Exo4D Demonstrator Proficiency / top-1 accuracy: Best top-1 accuracy is only 0.53 across four proficiency classes.
Restrictive assumptions: Hand bounding boxes provided by the challenge annotations.; Body pose uses camera (head) pose from the device plus monocular depth estimates.; Results depend on ensembles of large backbones (ViT-Huge, ConvNeXt-V2-Huge) tuned on the validation set.; Proficiency estimation uses egocentric video only.

## [1528] 3DGS-based Bimanual Category-agnostic Interaction Reconstruction (HANDS 2024 ARCTIC challenge technical report, team UVHANDS) (ECCV Workshops (HANDS 2024 challenge report) 2024, method, S1 S3)
Source: https://hands-workshop.org/files/2024/UVHANDS.pdf; confidence HIGH.
Field cannot yet: Reconstruct two hands and an unknown object with correct 3D relative placement and contact from monocular video without curated clear-view frames.
Stated limitations:
- HOLD baseline is accurate in 2D contact from the camera view but poor in 3D contact from other viewpoints. [Figure 1 caption]
- Existing bimanual category-agnostic methods ignore 3D hand-object contact or consider it only in limited cases. [2.3 Joint Train]
- The task is hard because of significant occlusion and dynamic contact during bimanual manipulation. [Abstract]
Open problems listed:
- Template-free reconstruction of two hands and an object under occlusion.
- Accurate 3D hand-object contact and relative distance from monocular video.
- Extending category-agnostic methods beyond single-hand, always-in-contact settings.
Benchmark gaps:
- ARCTIC (HANDS 2024 bimanual category-agnostic track) / CDh (cm^2): Winning result 38.69 remains far above HOLD single-hand HO3D level (11.3).
- ARCTIC / F10 (%): Best object F10 is 81.78%.
Restrictive assumptions: Monocular video from a single camera (subject 3, camera index 1) of ARCTIC.; Uses 9 objects, grab actions only, with 300 frames selected where hand and object were most clearly visible.; Per-sequence offline optimization (45K iterations on an A6000).; Depends on off-the-shelf HOLD outputs for initial hand and object meshes and SAM2 masks.; Rigid object; contact loss simply pulls hand translation toward object translation.

## [1529] 2nd Place Solution Technical Report for Hands'24 ARCTIC Challenge from Team ACE (ECCV Workshops (HANDS 2024 challenge report) 2024, method, S1 S3)
Source: https://hands-workshop.org/files/2024/ACE.pdf; confidence HIGH.
Field cannot yet: Reliably detect and track both hands through heavy occlusion in monocular bimanual video for template-free hand-object reconstruction.
Stated limitations:
- Interpolating several consecutive missing frames gives inaccurate hand poses due to no direct observation and cumulative error. [2.3 Self Boost MANO Registration]
- Under heavy occlusion HaMeR estimates in adjacent frames are inaccurate, compounding interpolation errors. [2.3 Self Boost MANO Registration]
- HaMeR estimates left and right hands independently, limiting bimanual performance. [2.2 Relation-aware Two-Hand Tokenization]
Open problems listed:
- Hand detection under heavy occlusion in bimanual HOI.
- Left/right hand identity confusion in segmentation tracking.
- Temporal consistency when frames are missing.
- Bimanual extension of category-agnostic HOI reconstruction.
Benchmark gaps:
- ARCTIC (HANDS 2024 bimanual category-agnostic track) / CDh: CDh 100.33 versus baseline 114.73, only 12.6% better; still very high.
- ARCTIC / MPJPE: MPJPE 25.29 versus baseline 25.91, nearly unchanged.
Restrictive assumptions: Monocular video, offline per-sequence pipeline built on HOLD preprocessing.; Two-hand tokenizer trained mainly on H2O3D.; Rigid objects in ARCTIC; implemented in about one month for the challenge.

## [1530] Solution of Multiview Egocentric Hand Tracking Challenge ECCV2024 (team JVHANDS; cited elsewhere as 1st Place Solution) (ECCV Workshops (HANDS 2024 challenge report) 2024, method, S3 S7)
Source: https://hands-workshop.org/files/2024/JVHANDS.pdf; confidence HIGH.
Field cannot yet: Generalize egocentric multi-view hand tracking across headset camera layouts with accurate absolute 3D position in real time, without offline sequence smoothing.
Stated limitations:
- The temporal refinement (Neural Smooth) is an offline post-processing step, not real-time. [4. Conclusion]
- A large distribution gap in camera parameters, particularly translation, between UmeTrack and HOT3D makes position prediction hard. [2. Method (Neural Smooth)]
- 3D estimates (position, pose) are less accurate than 2D landmark estimates. [1. Introduction]
- No additional optimization was done for shape estimation. [3. Experiments]
Benchmark gaps:
- HOT3D (challenge test) / MPJPE (mm): Final 21.66 mm on HOT3D vs 13.92 mm on UmeTrack; baseline without extrinsic augmentation was 184.27 mm on HOT3D.
- UmeTrack (challenge test) / MPJPE (mm): 13.92 mm only after offline neural smoothing; 17.91 mm without it.
Restrictive assumptions: Calibrated multi-view egocentric headset cameras with known extrinsics; Hand crops from a provided perspective-cropping toolkit (hand already localized); Offline whole-sequence optimization (Neural Smooth, 500 iterations) at test time; Hand-only tracking; no object modeled; Trained only on UmeTrack and HOT3D

## [1531] Technical report of HCB team for Multiview Egocentric Hand Tracking Challenge on HANDS 2024 Challenge (ECCV Workshops (HANDS 2024 challenge report) 2024, method, S3)
Source: https://hands-workshop.org/files/2024/HCB.pdf; confidence HIGH.
Field cannot yet: Produce temporally stable, accurate fingertip-level 3D hand tracking from stereo headset video within a single causal network without post-hoc smoothing.
Stated limitations:
- The network has no temporal modelling; triangulated joints are temporally unstable and need an external smoothing filter. [3. Experiment]
- Triangulated 2D joints are temporally unstable because 2D prediction ignores video context. [2. Method (Postprocess)]
- A gap exists between MANO-parameter accuracy and joint-coordinate accuracy, requiring post-optimization. [3. Experiment]
- Prior weak-perspective approaches lose depth and fail at world localization (stated gap motivating the work). [1. Introduction]
Benchmark gaps:
- UmeTrack (HANDS 2024 task 4 test) / FINGERTIP PCK AUC / MPJPE: Winning fingertip PCK AUC is 70.81%, notably below overall PCK AUC 75.66%; MPJPE 12.87 mm. Temporal smoothing plus optimization adds only 0.5 AUC.
Restrictive assumptions: Synchronized calibrated stereo (dual-view) inputs with known projection matrices for triangulation; Pre-calibrated hand shape provided by the challenge; Offline temporal Gaussian smoothing over neighboring frames (non-causal) and post-optimization; Test-time augmentation with flipped images; Hand-only; objects not modeled; Trained only on UmeTrack and HOT3D

## [1532] GHOST: Gaussian Hand-Object Surface Reconstruction with Geometric Priors (ICCV Workshops (HANDS 2025 challenge report) 2025, method, S1 S3)
Source: https://hands-workshop.org/files/2025/DFKI-AV.pdf; confidence HIGH.
Field cannot yet: Reconstruct complete, accurate object geometry under heavy bimanual occlusion from monocular video without retrieving an external 3D shape prior.
Stated limitations:
- Hand-occluded object regions remain unseen and incomplete, motivating retrieval of external 3D priors. [2.1.1 Object Geometric Prior]
- SfM-derived object point clouds and HaMeR hand translations are misaligned due to scale inconsistency and drift. [2.2 HO Alignment]
- Off-the-shelf hand reconstructions are jittery or unreliable under occlusion; low-confidence frames are discarded and interpolated. [2.1.2 Hand Reconstruction Initialization]
Benchmark gaps:
- ARCTIC (HANDS 2025 template-free track) / CD_ICP (cm^2), F10mm, F5mm: Ours CD_ICP 2.26, F10mm 60.88%, F5mm 34.67%, all worse than BIGS (1.36, 81.78%, 56.41%) despite better hand MPJPE.
- ARCTIC / MPJPE_RA (mm): Hand MPJPE remains about 22.7-25.4 mm per hand.
Restrictive assumptions: Offline per-sequence optimization over the whole video (SfM, SAM2 tracking, Gaussian Splatting); A matching 3D model must exist in Objaverse and be retrievable from a text description of the object; Rigid object; camera trajectory from SfM on the object; Grasp detection by heuristic motion thresholds (cosine similarity > 0.5); Relies on HaMeR, RTMPose, SAM2, VGGSfM, InternVL, OpenShape components

## [1533] Technical Report of HCB-Hand Team for Dexterous HO Tracker Challenge on HANDS 2025 Challenge (ICCV Workshops (HANDS 2025 challenge report) 2025, method, S6 S3)
Source: https://hands-workshop.org/files/2025/HCB-Hand.pdf; confidence HIGH.
Field cannot yet: Reliably transfer bimanual human hand-object manipulation to dexterous robot hands, even in simulation with mocap references.
Stated limitations:
- Large performance gap between single-hand and bimanual tasks; the MoE has no specialized bimanual coordination design. [4. Conclusion]
- The framework is generic and lacks bimanual-specific design. [4. Conclusion]
- A single policy network is argued to struggle with complex observations (motivating gap). [1. Introduction]
Benchmark gaps:
- HANDS@ICCV2025 HO-Tracker evaluation sequences / Success rate: Bimanual success 52.8% vs single-hand 76.2% (left 85.2%, right 73.1%).
- HANDS@ICCV2025 HO-Tracker evaluation sequences / Object translation error Et: Bimanual 0.728 vs left 0.220 and right 0.323.
Restrictive assumptions: Reference hand and object trajectories from mocap (OakInk2, GigaHands) are given; Simulation only (Isaac Gym), no real robot; Pre-trained hand imitator from ManipTrans; Policy trained directly on the official evaluation samples (36 single-hand, 39 bimanual tasks)

## [1534] Egocentric 3D Hand-Object Tracking in the Wild with Mobile Multi-Camera Rig (ICCV Workshops (HANDS 2025 extended abstract) 2025, system, S1 S5)
Source: https://hands-workshop.org/files/2025/Egocentric.pdf (PDF title: Ego-Exo 3D Hand Tracking in the Wild with a Mobile Multi-Camera Rig); confidence HIGH.
Field cannot yet: Capture accurate 3D hand and object ground truth in unconstrained, mobile, outdoor settings without heavy wearable hardware, or generalize lab-trained hand trackers to such data.
Stated limitations:
- The extended abstract covers only 3D hand pose annotation; object pose, segmentation, contact and text annotations are not yet provided. [4. Conclusion and Future Work]
- Accuracy degrades during hand-object interaction relative to no interaction. [3.3 Quantitative Evaluation, Table 1]
- Models trained on existing datasets generalize much worse to in-the-wild data. [3.3, Table 2]
- The rig still uses OptiTrack mocap with a marker tree on the headset, and the reference frame moves with the participant. [3.1 Mobile Capture Rig]
Open problems listed:
- Trade-off between environmental realism/mobility and 3D ground-truth accuracy in hand-object capture
- Lack of in-the-wild datasets with dense accurate 3D hand and object annotations
- Poor generalization of hand pose estimators trained on lab datasets to in-the-wild data
- Missing 6DoF object pose, segmentation, contact and text annotations in the wild (future work)
Benchmark gaps:
- EgoExo-Hands (approx. 30,000 frames, 3 subjects) / MKPE (mm): UmeTrack tracker trained on UmeTrack+HOT3D gets 16.28 mm vs 9.48/10.95 mm in-domain; single-source training 22.59-24.78 mm.
- Dome validation (30-camera) / MPJPE median/P90 (mm): Hand-object interaction: median 7.90, P90 12.53, worst of the three conditions.
Restrictive assumptions: 8 kg backpack rig with eight exocentric fisheye cameras plus a Meta Quest 3 headset; Five OptiTrack cameras and a marker tree on the headset for headset tracking; Workstation on a mobile cart streaming data; Personalized hand model from a high-resolution hand scan system; Proprietary fine-tuned Sapiens and InterNet keypoint detectors; Offline annotation pipeline

## [1535] DyTact: Capturing Dynamic Contacts in Hand-Object Manipulation (ICCV Workshops (HANDS 2025) 2025, method, S1)
Source: https://arxiv.org/pdf/2506.03103 (v2); confidence HIGH.
Field cannot yet: Measure or estimate per-frame hand-object contact accurately, and validate it against instantaneous ground truth, outside dense multi-view studio capture.
Stated limitations:
- Existing real-world datasets lack contact ground truth; evaluating dynamic contact remains hard and the new benchmark only has accumulated contact GT. [5.1 DyTact-21 Dynamic Contact Benchmark]
- MANO annotations in major datasets misalign with real hands, degrading contact estimation. [1. Introduction]
- MANO pose estimation is not robust under occlusion and rapid motion. [1. Introduction]
- Thermal sensing only gives accumulated contact, not instantaneous contact. [1. Introduction]
Benchmark gaps:
- DyTact-21 (21 sequences, 6 bimanual) / mIoU / F1 of accumulated contact: Best method reaches only mIoU 0.226 and F1 0.378; MANO baseline 0.168 / 0.279.
- DyTact-21 / Instantaneous contact: No ground truth for per-frame contact; only accumulated contacts are benchmarked.
Restrictive assumptions: Dense calibrated multi-view RGB video (about 30 views per sequence in evaluation); Per-sequence offline optimization; MANO initialization from an automated multi-view pipeline (GigaHands); Object point cloud from offline scans or first-frame reconstruction; SAM2 foreground masks; Tabletop manipulation scenes; Contact evaluated only against accumulated (wet-paint residue) ground truth

## [1536] DF-Mamba: Deformable State Space Modeling for 3D Hand Pose Estimation in Interactions (ICCV Workshops (HANDS 2025 extended abstract) 2025, method, S1 S3)
Source: https://hands-workshop.org/files/2025/DF-Mamba.pdf; confidence HIGH.
Field cannot yet: Estimate 3D hand pose under hand-object and egocentric occlusion to well below centimetre error from a single image.
Stated limitations:
- Fixed-grid Mamba scans limit capture of hand pose variation (motivating gap). [1. Introduction]
- ViT-based backbones are an inference-speed bottleneck for real-time use. [3. Experiments]
- Occlusion such as overlapping hands makes reconstruction hard. [Abstract]
Benchmark gaps:
- AssemblyHands (egocentric) / MPJPE (mm): Best is 18.78 mm (ResNet50 19.35).
- DexYCB (hand-object) / MPJPE (mm): Best is 17.80 mm (ResNet50 19.36).
- InterHand2.6M / MPJPE two-hand (mm): 10.53 mm for two hands vs 7.94 mm single hand.
Restrictive assumptions: Single-frame inference, no temporal modelling; Plugged into existing frameworks (A2J-Transformer, Zhou et al.), backbone change only; Hand-only pose; objects not reconstructed; Supervised training on each benchmark

## [1537] Get a Grip: Reconstructing Hand-Object Stable Grasps in Egocentric Videos (ECCV Workshops (HANDS 2024 extended abstract) 2024, method, S1)
Source: https://hands-workshop.org/files/2024/HANDS_2024_Workshop__Get_a_Grip.pdf; confidence HIGH.
Field cannot yet: Reconstruct temporally consistent hand-held object poses in unscripted egocentric video without known CAD models and validate them against 3D ground truth.
Stated limitations:
- Evaluation is restricted to objects with known category CAD models. [1. Introduction]
- No 3D ground truth in the wild; only 2D mask proxies and stable contact area are measured. [Abstract]
- The method assumes the category-level CAD model is known. [3.2 Reconstructing Object Poses in a Stable Grasp]
- The static-object assumption has non-negligible error; 1-DoF still has about 3 degrees off-axis error. [3.1 Stable Grasp Study]
Open problems listed:
- Hand-object reconstruction in unscripted in-the-wild video lacks 3D ground truth; only 2D mask proxies are available
- Reconstruction beyond known-category CAD models is not evaluated
Benchmark gaps:
- ARCTIC-Grasps / ADD % / SCA-ADD %: 1-DoF 57.3 ADD and 38.5 SCA-ADD overall; scissors SCA-IOU 2.7.
- EPIC-Grasps (2.4K clips, 9 categories) / IOU / SCA@0.8 / SCA@0.6: 1-DoF reaches 59.9 IOU, 14.1 SCA@0.8, 32.9 SCA@0.6; Dynamic has higher IOU (61.7).
Restrictive assumptions: Known category-level object CAD model; Stable grasp start-end segment given (labelled clips); Object motion relative to hand restricted to 1-DoF within the grasp; Object masks provided as supervision (from VISOR annotations); HaMeR hand outputs kept fixed; Offline joint optimisation over all frames of the grasp

## [1538] Generative Hierarchical Temporal Transformer for Hand Pose and Action Modeling (ECCV Workshops (HANDS 2024) 2024, method, S1 S3)
Source: https://hands-workshop.org/files/2024/GHTT_ECCVW_final%20(1).pdf; confidence HIGH.
Field cannot yet: Jointly recognize and forecast bimanual hand pose and action under a freely moving (egocentric) camera with reliable object recognition in cluttered, occluded scenes.
Stated limitations:
- The method assumes a fixed camera viewpoint; drastic camera motion such as egocentric head motion would need explicit hand/camera motion decomposition, left as future work. [5 Conclusion, Limitations and Future Work]
- On AssemblyHands the object input uses ground-truth labels because objects cannot be recognized reliably in cluttered, occluded scenes. [4.3 Joint Modeling of Recognition and Prediction]
- Evaluation on Assembly data was restricted to six fixed views without severe hand occlusion and to the validation split, since the test split lacks object labels. [4.1 Datasets]
- Action-block training assumes the same action label holds over the observed and predicted parts of a sequence. [3.3 / training details]
Benchmark gaps:
- AssemblyHands-Val (views v1, v3, v8) / Action top-1 accuracy: G-HTT reaches only 36.01, 34.79, 36.74% on 1380 fine-grained classes even with GT object labels.
- AssemblyHands-Val v1 / MPJPE-RA (mm, left/right): 35.1/22.4 mm for G-HTT, barely better than the ResNet-18 per-frame input (35.4/22.7).
- H2O-Test cam0 / Action accuracy: G-HTT 59.92% versus 85.12% for HTT trained on that view; HTT collapses to 2.89% on unseen egocentric cam4.
- H2O-Test / FID (motion prediction): FID 8.19 on unseen subjects versus 5.32 on trained-subject val split.
Restrictive assumptions: Fixed (static) camera viewpoint per input video; Input is a per-frame 3D hand pose sequence from an external image-based estimator; Ground-truth object labels used on AssemblyHands for action recognition and prediction; Same action shared across observed and predicted window during training; Evaluation limited to views without severe hand occlusion on Assembly data; Thumb CMC joint excluded (20 joints) due to annotation availability

## [1539] ChildPlay-Hand: A Dataset of Hand Manipulations in the Wild (ECCV Workshops (HANDS 2024) 2024, dataset, S1)
Source: https://hands-workshop.org/files/2024/childplay-hand.pdf; confidence HIGH.
Field cannot yet: Reliably segment hand manipulation stages, especially grasp and release, in uncontrolled multi-person third-person video.
Stated limitations:
- Annotations are 2D boxes and coarse manipulation-stage labels; the authors call the granularity crude, though a necessary first level of analysis. [1 Introduction]
- Object-in-hand detection remains hard due to self-occlusion, hands occluding objects, and small, varied objects. [4 Tasks (T1)]
- Transitional stages grasp and release remain challenging even for the best network. [5.1 Recognition Results]
- Hold vs operate differ by intention, not only motion, making them hard to separate even during annotation. [Supplementary 4]
- Hand boxes are pseudo-boxes from wrist/elbow keypoints because hand detection and association are hard and hand keypoints are noisy under occlusion. [Supplementary 3]
Open problems listed:
- Third-person, in-the-wild hand-object interaction lacks datasets compared with egocentric settings.
- Detecting object-in-hand under self-occlusion, hand-object occlusion, small and varied objects.
- Segmenting transitional manipulation stages (grasp, release).
- Disambiguating hold vs operate, which depends on intention.
- Hand movements beyond manipulation (e.g., pointing) confuse models.
- Multiple people interacting with the same object or in close proximity.
- Detecting and associating hands with persons in unconstrained scenes.
- Joint modeling of manipulation and gaze from a third-person view is unexplored.
- Combining hand-focused and full-body context.
Benchmark gaps:
- ChildPlay-Hand ManiS / macro F1 (recognition): Best model Hiera-Hand reaches 73.2% accuracy but only 51.2% macro F1.
- ChildPlay-Hand ManiS / macro segmental F1 / Edit: Best TAS method MS-TCN m-S-F1 49.6, Edit 66.1.
- ChildPlay-Hand OiH / F1 / segmental F1: Best recognition F1 74.3%; segmental F1 65.3 with MS-TCN, sliding window only 30.5.
Restrictive assumptions: Third-person RGB video only; no 3D hand or object pose annotation; Hand crops from body-pose wrist/elbow keypoints rather than hand detection

## [1540] Pre-Training for 3D Hand Pose Estimation with Contrastive Learning on Large-Scale Hand Images in the Wild (ECCV Workshops (HANDS 2024 extended abstract) 2024, method, S1)
Source: https://hands-workshop.org/files/2024/Nie_Lin_HANDS@Workshop_ECCV24_HandCLR_Camera-ready_Submission.pdf; confidence HIGH.
Field cannot yet: Exploit unlabeled in-the-wild hand video to close the accuracy gap for egocentric 3D hand pose without large labeled 3D datasets.
Stated limitations:
- Labeled 3D hand pose datasets are limited and mostly built in controlled lab settings, motivating pre-training. [2 Related Work]
- Temporal-adjacency positives fail in the wild because hands are hard to track, especially egocentric views where hands leave the frame. [1 Introduction]
- Positive mining relies on noisy off-the-shelf 2D keypoints, mitigated with PCA projection. [3.2 Mining similar hands]
Benchmark gaps:
- AssemblyHands (Ego) / MPJPE: Best HandCLR 18.23 mm versus PeCLR 19.12 mm; smallest improvement of the three datasets.
- FreiHand with 10% labels / MPJPE: Even with 1M pre-training images error stays 23.68 mm, versus 15.79 mm with full labels.
Restrictive assumptions: Off-the-shelf hand detector and 2D pose estimator for crop extraction and positive mining; Single-image, right-hand-normalized crops (left hands flipped); Fine-tuning still needs labeled 3D datasets

## [1541] Diffusion-based Interacting Hand Pose Transfer (ECCV Workshops (HANDS 2024 extended abstract) 2024, method, S3)
Source: https://hands-workshop.org/files/2024/IHPT__ECCVW_2024_.pdf; confidence HIGH.
Field cannot yet: Supply quantitatively validated in-the-wild 3D interacting-hand training data that closes the lab-to-wild domain gap.
Stated limitations:
- Motivation: Stable Diffusion renders hands badly and links between foundation models and hand research are weak. [1 Introduction]
- Lack of in-the-wild 3D hand datasets and indoor-outdoor domain gap are named as the problem IHPT data aims to alleviate. [Abstract]
Restrictive assumptions: Source images need MANO-based 3D labels to build the mesh mask (InterHand2.6M, Re:InterHand); Training requires paired source and ground-truth target images with poses; Downstream gain shown only qualitatively on MSCOCO

## [1542] Learn 2D, Solve 3D: UA-Fit, an Uncertainty-Weighted Analytical Solver for Multi-view Hand Mesh Recovery (ECCV Workshops (HANDS/DexHAND 2026) 2026, method, S3 S4)
Source: not found; confidence LOW.
Field cannot yet: Not determinable: full text was not accessible.
Restrictive assumptions: Calibrated multi-view RGB (from inventory row)

## [1543] Cascaded Diffusion Framework for Probabilistic Coarse-to-Fine Hand Pose Estimation (ECCV Workshops (HANDS/DexHAND 2026) 2026, method, S1 S4)
Source: https://arxiv.org/html/2510.00527; confidence HIGH.
Field cannot yet: Jointly reconstruct two hands and the manipulated object probabilistically under extreme occlusion.
Stated limitations:
- Stage-1 joint lifting errors are higher on hand-object datasets where object occlusion makes 2D-to-3D lifting harder, and joint quality directly limits the final mesh. [4.4 Ablation, Performance of the joint diffusion model]
- Accuracy degrades sharply under extreme object occlusion (beyond roughly 80% of the hand region). [4.3 Robustness to Occlusion]
- Averaging more hypotheses does not improve a single prediction; best-of-N gains are oracle upper bounds requiring ground truth. [4.4 Number of sampling]
- The 10-step sampler is slower than existing regressors (140 ms vs 40-50 ms). [B.4 Inference speed]
Benchmark gaps:
- HO3Dv2 / P-MPJPE / P-MPVPE (mm), AUC: 7.5/7.5 mm, tying Hamba and WiLoR; joint AUC 0.633 below HaMeR (0.635) and Hamba (0.648).
- HO3Dv2 / Stage-1 P-MPJPE (mm): 7.89 averaged versus 5.01 on FreiHAND, showing object occlusion harms lifting.
- DexYCB / P-MPJPE (mm): Best at 4.5 mm; stage-1 joints 7.59 mm averaged.
Restrictive assumptions: Single hand, single frame (sequence length set to 1); Relies on off-the-shelf 2D keypoint estimator (WiLoR) as input; No object reconstruction; Mesh autoencoder trained per dataset

## [1544] Observe, Retarget, and Distill: Grounding Human Demonstrations in Robot Experience for Dexterous Grasping (ECCV Workshops (HANDS/DexHAND 2026) 2026, method, S6)
Source: not found; confidence LOW.
Field cannot yet: Not determinable: full text was not accessible.
Restrictive assumptions: Human demonstration video (from inventory row; details not available)

## [1545] Joint-Query Spatial Attention for Egocentric Interaction Fields: Second Place in the SHOW3D Challenge at HANDS 2026 (ECCV Workshops (HANDS 2026 challenge report) 2026, method, S1)
Source: not found; confidence LOW.
Field cannot yet: Not determinable: full text was not accessible.
Restrictive assumptions: Egocentric images, single- or multi-view (from inventory row)

## [1546] GOLF: Global Observation with Local Focus for Calibration-Aware Stereo Interaction Field Estimation (ECCV Workshops (HANDS 2026 challenge report) 2026, method, S1 S3)
Source: https://arxiv.org/html/2609.08607 (arXiv 2609.08607v2); confidence HIGH.
Field cannot yet: Predict hand-to-object-surface interaction fields from egocentric stereo to well below a few centimetres of error for unseen subjects.
Stated limitations:
- The official ranking score is a hidden server-side metric whose formula is not public, so the reported score cannot be decomposed. [3 Experiments, Setup]
- The adapter comparison rows come from successive training stages, so they show capacity effects and are not a strict one-variable ablation. [3 Experiments, Backbone adaptation]
- The test-set table traces submissions rather than controlled ablations. [3 Experiments, Challenge results]
- The image-space versus feature-space crop comparison was run in a different setting and supports only that paired comparison. [3 Experiments, Feature-space versus image-space crops]
Benchmark gaps:
- SHOW3D hidden test set (3 unseen subjects) / mean ADE (mm), joint-to-nearest-object-surface vectors: Even the first-place ensemble keeps a mean ADE of 27.82 mm (official score 27.47); the official ResNet-50 InterField baseline is 59.38 mm.
- SHOW3D development split (2 held-out subjects) / locator center error (px): Hand/object region center error stays near 10 pixels (10.04 px best).
Restrictive assumptions: Synchronized, calibrated egocentric stereo pair with per-frame calibration available at test time; Object category provided as input to condition the object-region query; Large pretrained backbone (DINOv3 ViT-H+/16) adapted with LoRA; final result is a two-model ensemble with HFlip test-time augmentation; Offline per-frame prediction on challenge data; no runtime or real-time figures reported

## [1547] Joint-Conditioned Stereo Surface Reasoning for Interaction Field Estimation (ECCV Workshops (HANDS 2026 challenge report) 2026, method, S1)
Source: https://arxiv.org/html/2609.06955 (arXiv 2609.06955v1); confidence HIGH.
Field cannot yet: Reliably verify hand-to-surface endpoints by stereo correspondence when hands and objects are occluded or blurred.
Stated limitations:
- Stereo matching can fail under occlusion or motion blur, so the surface estimate is only applied as a gated correction to a direct prediction. [2.3 Evidence-Gated Field Refinement]
- Image evidence can remain ambiguous, which motivates the learned residual gate. [1 Introduction]
- Independent per-joint rays may select unrelated surfaces. [2.2 Joint-Conditioned Stereo Surface Reasoning]
- Leaderboard scores come from historical submissions with different training settings and are not scores of the ablation checkpoints. [3 Experiments, Table 1 note]
Benchmark gaps:
- SHOW3D clip-held-out internal split / mean ADE (mm) / Acc@10 (%): Full JSSR reaches 15.740 mm mean ADE but only 51.23% of predictions within 10 mm.
- SHOW3D challenge leaderboard / official LB score: Best single model scored 33.59; best ensemble with object-specific fine-tuning 32.61 (third place), versus 58.00 for the official ResNet-50 baseline.
Restrictive assumptions: Calibrated synchronized stereo, using seven consecutive stereo pairs per prediction (temporal window); Training data cleaned by removing 535 geometrically inconsistent annotations; Best leaderboard result uses object-specific fine-tuning and an ensemble of two expert systems; No CAD model or object pose required (stated as a design property)

## [1562] Muscles in Time: Learning to Understand Human Motion by Simulating Muscle Activations (NeurIPS 2024, dataset, S4 S7)
Source: https://arxiv.org/html/2411.00128; confidence HIGH.
Field cannot yet: Obtain muscle-level ground truth for human-object manipulation, since simulation lacks object mass and contact forces.
Stated limitations:
- As a simulation dataset, a synthetic-to-real domain gap is unavoidable; models need real-world validation. [6 Discussion, Limitations]
- Samples that do not converge within the iteration limit are discarded, potentially shifting the motion category distribution relative to AMASS. [6 Discussion, Limitations]
- Motions with contact by body parts other than feet, or with external objects, were mostly excluded because reaction forces are unknown. [6 Discussion, Limitations]
- Object-related motions such as lifting and throwing assume negligible object mass because mass is unknown. [6 Discussion, Limitations]
- Ethnicity and some body-weight types are under-represented. [6 Discussion, Societal Impact]
- Simulation is computationally heavy and fails on some segments, so released data contains gaps; longer sequences are more prone to gaps. [Appendix, data format]
Open problems listed:
- Synthetic-to-real domain gap for simulated muscle activations; real-world validation needed
- Simulating muscle activations for motions with non-foot environment contact or object interaction requires unknown reaction forces
- Unknown object mass prevents faithful simulation of object-handling motions
- Convergence failures bias which motion categories are represented
- Real EMG/sEMG datasets remain small, invasive to collect and not representative of motion variety
- Dataset diversity in ethnicity and body-weight types
Benchmark gaps:
- MinT validation set, motion type dance / PCC (motion-to-muscle activation prediction): Dance is the hardest motion type; PCC ranges 0.29 to 0.59 across models versus up to 0.71 for jog.
- MinT, all 402 muscles / RMSE vs SMAPE: Most muscles are rarely activated, so RMSE looks small while SMAPE stays high; the authors note RMSE differences between models are marginal.
Restrictive assumptions: Synthetic labels from OpenSim musculoskeletal simulation driven by AMASS mocap, not measured EMG; Foot-ground contact only; other contacts and object interactions mostly excluded; Object mass assumed negligible for lifting and throwing motions; Restricted to AMASS subsets EyesJapan, BMLrub, KIT, BMLmovi, TotalCapture; Vertebral range of motion constrained to approximate natural degrees of freedom

## [1563] InterCap: Joint Markerless 3D Tracking of Humans and Objects in Interaction from Multi-view RGB-D Images (IJCV 2024, dataset, S2 S4)
Source: https://arxiv.org/html/2209.12354 (GCPR 2022 conference version; IJCV 2024 extended version at link.springer.com was blocked by the network proxy); confidence MEDIUM.
Field cannot yet: Capture whole-body plus hand-object interaction markerlessly without manual contact labels, known object meshes, and with low hand jitter for small objects.
Stated limitations:
- Contact frames and likely contact vertices are annotated manually; automatic contact detection is left open. [3 Method]
- Per-frame separate fitting yields jitter and heavy body-object penetration; OpenPose struggles when the object occludes the body or hands. [3 Method]
- Object segmentation with PointRend struggles significantly for small objects such as bottles or cups due to occlusion. [3.2 Sequential Object-Only Tracking]
- Residual jitter remains, from detector sensitivity to occlusion and illumination and from small inter-camera delays of Azure Kinects; it is worse for hands. [4 Experiments, Discussion on Jitter]
- Fitting error is bounded from below by Kinect synchronization imperfections and wrong correspondences for occluded regions. [4 Experiments, Fitting Accuracy]
- Very fast interactions were avoided because of motion blur and RGB-depth misalignment limits of the sensor. [4 Dataset capture protocol]
- Some false contact appears on the dorsal side of the hand due to camera setup and reconstruction jitter. [4 Experiments, Contact heatmaps]
Open problems listed:
- Automatic detection of human-object contact (stated open problem)
- Jitter from detector sensitivity to occlusion and illumination and from multi-Kinect timing offsets
- Capturing interactions with smaller objects and dexterous manipulation
- Reconstruction under occlusion between body and object, motion blur, depth/scale ambiguity and low hand resolution
Benchmark gaps:
- InterCap / mean vertex-to-point-cloud distance: 20.29 mm for the body and 18.50 mm for objects, worse than PROX-D's 13.02 mm body error because a single body shape is used per sequence.
- InterCap / contact heatmaps: Interactions mainly involve the right hand; false contacts appear on the dorsal hand.
Restrictive assumptions: Known, pre-scanned rigid object mesh; Subject interacts with a single object; Multi-view calibrated and synchronized Azure Kinect RGB-D rig (static cameras); Manual annotation of contact frames and contact vertices; Offline whole-sequence optimization; Single body shape per sequence; Pseudo ground truth only; no independent mocap ground truth for evaluation
