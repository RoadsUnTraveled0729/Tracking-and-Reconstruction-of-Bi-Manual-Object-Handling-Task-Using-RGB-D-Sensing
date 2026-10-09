#!/usr/bin/env python3
"""Build writing/v4/Chapter_1_Introduction.docx from the revised Chapter 1 text.

Supervisor round of 2026-08-03: chapter shortened; literature review condensed
with a summary table (Table 1.1); research gaps and objectives itemized; new
Section 1.4 Organization of the Thesis (roadmap material moved from the old
Chapter 2 opener). Citation first-appearance order is deliberately preserved
so the consolidated numbering of build_thesis.py does not shift.
"""
from docx import Document
from docx.shared import Pt, Inches

H1, H2, H3, P = "h1", "h2", "h3", "p"
CAP, TBL, LIN = "cap", "tbl", "lin"

content = [
(H1, "Chapter 1: Introduction"),

(P, "The ability to observe, interpret, and reconstruct human motion in three dimensions has become a foundational capability across a growing range of engineering and clinical disciplines. Robotic systems learn manipulation skills by watching people. Clinicians want objective records of how a patient moves. In both cases the demand is the same: accurate motion capture that does not require a laboratory to run. This thesis addresses one of the most technically demanding instances of this problem, the tracking and graphical reconstruction of bimanual object manipulation using a single consumer-grade RGB-D camera."),

(H2, "1.1 Motivation"),

(P, "Human hands are the primary means through which people interact with the physical world. Coordinated two-handed tasks such as lifting, rotating, transferring, and assembling objects appear in nearly every part of daily life. Capturing these interactions in three dimensions has direct uses in several fields. In robotics, recorded human demonstrations serve as training data for imitation learning [1], [2]. In virtual and augmented reality, skeletal and object pose data drive avatar animation and the simulation of physical tasks [3], [4]."),

(P, "The clinical potential is particularly significant. A vision-based system that records and reconstructs a patient's upper-body motion in three dimensions would let a physician review, at any convenient time, how the patient reaches for an object, transfers it between hands, or completes a routine daily task. An objective and repeatable record of this kind could assist in assessing progressive conditions such as Parkinson's disease, stroke-related upper-limb deficits, or age-related decline in motor coordination, where brief clinical observations may miss intermittent abnormalities [5], [6]. Reconstruction also protects patient privacy. The recorded motion is played back on a graphical avatar, so the patient's face, body, and home environment never leave the capture device."),

(P, "A practical sensing question follows from these requirements. A standard RGB camera provides only two-dimensional information, so metric 3D measurement requires either a depth camera or multiple synchronized viewpoints, such as the two-camera arrangement of FreeMoCap [38]. Multi-camera motion capture systems are accurate, but they demand calibrated camera arrays, physical infrastructure, and expert operation [7]. Wearable sensors avoid the cameras, but they must be attached and calibrated for each participant, they restrict natural movement, and they raise hygiene concerns in patient-facing settings [8]. A single consumer-grade RGB-D camera avoids both drawbacks: it is inexpensive, places no hardware on the participant, and captures registered colour and metric depth from one fixed viewpoint [9]."),

(P, "Reconstructing bimanual motion from that single sensor is genuinely difficult. When the two hands occlude each other or the object, landmark detectors fail at exactly the moments that matter most clinically [10], [11]. When landmarks overlap in the image or approach the edge of the reliable depth range, direct depth readings become ambiguous or invalid [12]. Keeping all tracked segments and objects in one consistent coordinate frame requires careful calibration, and prior single-camera systems address this only partially [13]. The torso also moves slowly while the hands move fast, so one shared filter over-smooths some segments and under-smooths others [14]. These problems are not solved by better sensor resolution alone. They call for a structured kinematic framework that encodes the relationships between body segments and stays physically consistent when measurements are missing or unreliable. A wider trend in computing supports this route: as transistor scaling reaches its physical limits, future capability is expected to come from algorithms and system organization rather than from faster parts [39]. This thesis, written within a systems engineering program, takes that premise as a working assumption and returns to it in Chapter 9."),

(P, "The Networked Robotics and Sensing Laboratory at Simon Fraser University has produced foundational work directly relevant to this objective. A hierarchical kinematic model of the human hand, constructed from spatially tracked RGB-D landmarks, was developed in [15]. A subsequent study [16] formulated hand joint estimation as a Gaussian Bayesian Network problem, recovering anatomically consistent joint configurations when landmark measurements are occluded or corrupted by noise. The present thesis builds on both contributions, extending the scope from a single hand to the full bimanual upper body with concurrent object tracking and Unity-based visualization."),

(H2, "1.2 Problem Statement and Literature Review"),

(P, "Each challenge identified in Section 1.1 reflects a broader research problem. This section reviews the literature in three areas: hand and object tracking approaches, bimanual manipulation in motion analysis, and graphical reconstruction in robotics and virtual reality. Table 1.1 at the end of the section summarizes the reviewed work and the limitation of each approach family for the setting of this thesis."),

(H3, "1.2.1 Hand and Object Tracking Approaches"),

(P, "Hand tracking research has produced two broad families of methods: appearance-based approaches, which learn a direct mapping from image features to pose, and model-based approaches, which fit a parameterized hand model to sensor observations [17]. Early wearable systems encoded finger configuration directly in the sensor signal, through instrumented colour gloves [18] and, in earlier work in our laboratory, marker-based visual tracking combined with a vibrotactile glove [19]. The hardware these systems place on the user makes them impractical for clinical use. Consumer depth cameras then shifted the field toward markerless tracking: full-hand articulation was demonstrated with Particle Swarm Optimization over a geometric hand model [20], with an articulated Iterative Closest Point solver [21], and with a sphere-based model fitted to depth point clouds [22]. These methods established depth-based hand tracking, but they target a single hand and need explicit geometric models with per-user initialization."),

(P, "Deep learning replaced hand-crafted models with learned representations, from multi-view convolutional networks over depth images [23] to transformer-based mesh recovery from monocular RGB [24] and graph-guided state space models [25]. These methods reach strong benchmark accuracy, but they need large annotated training sets, they do not encode biomechanical constraints on joint motion, and they can behave unpredictably on data unlike their training distribution. MediaPipe [26] represents the current mainstream for lightweight landmark detection without specialized hardware: a two-stage pipeline that first detects a body region and then regresses keypoint positions within it. Its per-landmark depth is inferred from image appearance and carries substantial uncertainty during fast motion, contact, and occlusion [3]. Back-projecting the 2D detections through a calibrated depth camera resolves this ambiguity, an approach formalized in the hierarchical hand framework of [15] and independently validated in [12]. This thesis adopts the same fusion strategy."),

(P, "For object tracking, fiducial markers give reliable pose estimation without appearance models or training data. A comparative evaluation of marker systems concluded that ArUco markers balance robustness and efficiency well for single-camera setups [27], and the relationship between marker size, viewing distance, and pose error is documented in [28]. Each marker also encodes an integer identity, so a single detection resolves both which object is seen and where it is. Occlusion between the hand and the object remains the most persistent failure mode for single-camera systems. One line of work restores each occluded hand with an inpainting framework before estimating its pose [10]; another models hand and object jointly through mutual attention [11]. Both show that occlusion needs either explicit recovery or contextual constraints, and this observation motivates the interpolation-based occlusion recovery strategy of this thesis."),

(H3, "1.2.2 Bimanual Manipulation in Motion Analysis"),

(P, "Bimanual manipulation goes beyond running two hand trackers in parallel. The hands overlap in the image, they interact with the same object, and they are kinematically coupled through whatever they hold, so an error in one hand propagates inconsistencies into the reconstructed scene [17]. A formalization of bimanual task categories distinguishes symmetric coordination from asymmetric coordination, and the two produce different patterns of landmark dropout [29]. The infrastructure behind large bimanual datasets shows how demanding the capture problem is: InterHand2.6M was collected with between 80 and 140 synchronized cameras [30], and OakInk2 combined multi-camera rigs with wearable sensors [7]. On the reconstruction side, RGB2Hands recovers two strongly interacting hands from a single RGB video [31], but it does not track objects, and it relies on a learned model that is hard to interpret in terms of physical joint constraints."),

(P, "In clinical practice, objective kinematic measures of hand motion asymmetry capture deficits that observation scores may underrate [5], and a structured review of upper-limb assessment in amyotrophic lateral sclerosis found existing clinical tools too insensitive to track gradual functional change [6]. Both findings support a low-overhead, marker-free reconstruction system. Both also make physical plausibility of the output a requirement, since clinical assessment depends on anatomically consistent motion even when sensor data is incomplete."),

(H3, "1.2.3 Graphical Reconstruction in Robotics and VR"),

(P, "Unity has become the dominant platform for avatar-driven motion replay. Human motion has been reconstructed in Unity from a monocular camera using kinematic retargeting [32], a Kinect-based rehabilitation system showed that avatar-driven feedback supports clinical assessment of exercise quality [33], and the RePose system streams MediaPipe-derived joint angles to a Unity patient avatar for rehabilitation monitoring [34], the same end-to-end architecture adopted here. A persistent engineering issue in such systems is the coordinate mismatch between sensor and engine. The RealSense frame is right-handed with the y axis pointing down, Unity's frame is left-handed with the y axis pointing up, and without an explicit conversion the streamed poses accumulate systematic spatial error [13]."),

(P, "Moving landmark positions between the two environments is the easy part; a single fixed change of coordinates does it. The avatar, however, is not driven by points in space. It is driven kinematically, joint by joint, through rotations, so the real problem is resolving the relative rotation angles of the body segments from the measured landmark positions. That problem is the modeling core of this thesis, and its foundations come from the laboratory's hand kinematics work: the hierarchical RGB-D hand model of [15] and its Bayesian estimation extension [16], with the RealSense depth noise characterized as Gaussian consistent with [35], [36]."),

(TBL, [["Approach family", "Representative work", "Sensing", "Limitation for this setting"],
       ["Instrumented gloves and wearables", "[18], [19]", "worn sensors", "hardware on the user; per-user calibration; hygiene"],
       ["Model-based depth tracking", "[20], [21], [22]", "one depth camera", "single hand; explicit geometric models; per-user initialization"],
       ["Learning-based pose estimation", "[23], [24], [25]", "depth or RGB", "large training sets; no biomechanical constraints"],
       ["Landmark detection with depth fusion", "[26], [3], [12], [15]", "RGB-D", "prior work covers a single hand, not the bimanual upper body"],
       ["Fiducial object tracking", "[27], [28]", "RGB", "tracks marked objects only; no body tracking"],
       ["Hand-object occlusion handling", "[10], [11]", "RGB, depth", "single hand and object; learned models"],
       ["Bimanual capture datasets", "[30], [7]", "80+ camera rigs, wearables", "laboratory infrastructure far beyond clinical settings"],
       ["Two-hand reconstruction", "[31]", "monocular RGB", "no object tracking; no metric depth"],
       ["Avatar replay in Unity", "[32], [33], [34]", "monocular or Kinect", "single tracked stream; no concurrent object in a shared frame"]]),
(CAP, "Table 1.1. Summary of the reviewed literature: each approach family, its representative work, its sensing arrangement, and its limitation for single-sensor bimanual capture."),

(H3, "1.2.4 Gap Analysis and Motivation for This Work"),

(P, "The reviewed work shows substantial progress in hand tracking, object pose estimation, bimanual motion analysis, and graphical reconstruction taken individually. No single-sensor system combines these capabilities while remaining physically consistent under real bimanual manipulation. Five gaps define the scope of this thesis."),

(LIN, "1. Existing single-camera systems either fail silently when landmark confidence drops or smooth all joints uniformly, without a recovery strategy that respects the different kinematics of the torso, upper arm, forearm, and hand [17]."),
(LIN, "2. MediaPipe's monocular depth estimates are unreliable during manipulation [3]. Depth fusion with a calibrated sensor resolves this, but its integration with a full upper-body kinematic chain in a bimanual context has not been reported."),
(LIN, "3. No published single-camera system reconstructs two hands and a manipulated object simultaneously in one calibrated world frame. Bimanual methods omit the object [31], and hand-object methods cover only one hand [37]."),
(LIN, "4. The sensor-to-Unity coordinate transformation is documented for the single-hand case [13], but a calibration that keeps a full upper-body system and a concurrently tracked object in one world frame has not been addressed."),
(LIN, "5. A kinematic framework whose value is physical consistency and recoverability under occlusion, dropout, and noisy depth, rather than raw accuracy under ideal unoccluded conditions, has not been established for this setting."),

(P, "The kinematic and Bayesian estimation foundations developed in [15], [16] provide the mathematical basis for such a framework at the level of a single hand. The present thesis extends and integrates these foundations into a system that addresses all five gaps together, and this integration lays the groundwork for future systems in which better sensors, denser landmark sets, and stronger estimation methods can be incorporated without architectural redesign."),

(H2, "1.3 Research Objectives"),

(P, "The overarching goal of this thesis is to develop and evaluate a structured framework for tracking and reconstructing bimanual object manipulation from a single RGB-D sensor, with particular attention to physical consistency under the occlusion and measurement noise conditions that arise in practice. Five objectives serve this goal."),

(LIN, "1. Design and implement a calibrated RGB-D sensing pipeline on the Intel RealSense D435 that aligns the depth and colour streams, establishes the camera intrinsics, and expresses all observations in a consistent world coordinate frame."),
(LIN, "2. Develop an upper-body pose estimation module that fuses MediaPipe Pose landmark detections with registered depth data, producing metric 3D joint positions for the torso, arms, and hands from a single fixed viewpoint."),
(LIN, "3. Implement concurrent object tracking from ArUco fiducial markers, synchronized frame by frame with the skeletal stream in the same world frame. The object's orientation is recovered and carried through filtering, streaming, and evaluation, but no second measurement chain validates it; robust orientation tracking through all attitudes of the object remains an extension of this framework."),
(LIN, "4. Recover occluded or low-confidence landmarks through interpolation, and validate the reconstructed trajectories of the left wrist, the right wrist, and the manipulated object against ground-truth references on a common footing. A chain-level Bayesian recovery scheme following [16] is discussed as future work in Chapter 8."),
(LIN, "5. Integrate the complete pipeline with a Unity-based visualization environment and evaluate the reconstruction qualitatively against the original recordings across representative bimanual tasks, including lifting, rotation, and transfer between hands."),

(H2, "1.4 Organization of the Thesis"),

(P, "Chapter 2 describes the experimental environment: the capture setup and recorded data, the three sensing tools (the RGB-D camera, the pose landmark detector, and the fiducial markers), the preprocessing applied before any modeling, and the mechanisms by which processed results reach Unity. Chapter 3 develops the kinematic model of the person. It constructs the torso and arm coordinate frames from measured landmarks, computes the torso orientation and arm joint angles with worked numerical examples, and maps the computed angles onto the Unity avatar. Chapter 4 develops the independent marker branch: scene calibration, object tracking, and the anchoring of every measurement in a world frame fixed to the desk. Chapter 5 integrates the two branches and streams the fused person and object record into the Unity reconstruction."),

(P, "Chapter 6 evaluates the system by comparing the landmark branch against the marker branch on the same recording. Chapter 7 converts both branches to run in real time and measures the cost of doing so. Chapter 8 states the limitations of the delivered system and the work that should follow, and Chapter 9 concludes. The Appendix collects the supporting internals: the acquisition of the RGB-D recordings and the structure of the recorded bag file in Appendix A, depth sensing and deprojection in Appendix B, pose landmark detection in Appendix C, fiducial marker detection and pose recovery in Appendix D, and the hardware and software platform in Appendix E."),

]

references = {i + 1: s for i, s in enumerate([
'S. Sivakumar, K. Shaw, and D. Pathak, "Robotic telekinesis: Learning a robotic hand imitator by watching humans on YouTube," arXiv:2202.10448, 2022.',
'Y. Ye, P. Hebbar, A. Gupta, and S. Tulsiani, "Diffusion-guided reconstruction of everyday hand-object interaction clips," in Proc. IEEE/CVF Int. Conf. Computer Vision (ICCV), 2023.',
'G. Buckingham, "Hand tracking for immersive virtual reality: Opportunities and challenges," Frontiers in Virtual Reality, vol. 2, p. 728461, 2021.',
'M. Mangalam et al., "Enhancing hand-object interactions in virtual reality for precision manual tasks," Virtual Reality, vol. 28, no. 4, 2024.',
'R. J. Carey, L. T. Baxter, and P. R. Di Fabio, "Tracking control in the nonparetic hand of subjects with stroke," Archives of Physical Medicine and Rehabilitation, vol. 79, no. 4, pp. 435-441, 1998.',
'C. D. Hayden et al., "Measurement of upper limb function in ALS: A structured review of current methods and future directions," Journal of Neurology, vol. 269, no. 8, pp. 4089-4101, 2022.',
'X. Zhan et al., "OakInk2: A dataset of bimanual hands-object manipulation in complex task completion," in Proc. IEEE/CVF Conf. Computer Vision and Pattern Recognition (CVPR), 2024.',
'E. Theodoridou et al., "Hand tracking and gesture recognition by multiple contactless sensors: A survey," IEEE Transactions on Human-Machine Systems, vol. 53, no. 1, pp. 35-43, 2023.',
'L. Keselman, J. Iselin Woodfill, A. Grunnet-Jepsen, and A. Bhowmik, "Intel RealSense stereoscopic depth cameras," in Proc. IEEE Conf. Computer Vision and Pattern Recognition Workshops (CVPRW), 2017.',
'H. Meng et al., "3D interacting hand pose estimation by hand de-occlusion and removal," in Proc. European Conf. Computer Vision (ECCV), 2022.',
'R. Wang, W. Mao, and H. Li, "Interacting hand-object pose estimation via dense mutual attention," in Proc. IEEE/CVF Winter Conf. Applications of Computer Vision (WACV), 2023.',
'S. Dill et al., "Accuracy evaluation of 3D pose reconstruction algorithms through stereo camera information fusion for physical exercises with MediaPipe Pose," Sensors, vol. 24, no. 23, art. 7772, 2024.',
'Y. Dong, "Tracking and reconstruction of object grasping hand using a RGB-D sensor," M.A.Sc. thesis, Simon Fraser University, 2024.',
'A. Ahmad, C. Migniot, and A. Dipanda, "Hand pose estimation and tracking in real and virtual interaction: A review," Image and Vision Computing, vol. 89, pp. 35-49, 2019.',
'Y. Dong and S. Payandeh, "Hand kinematic model construction based on tracking landmarks," Applied Sciences, vol. 15, no. 16, p. 8921, 2025, doi: 10.3390/app15168921.',
'Y. Dong and S. Payandeh, "Bayesian estimation of hand kinematics from spatially tracked landmarks," Journal of Intelligent Systems and Control, vol. 4, no. 2, pp. 105-124, 2025, doi: 10.56578/jisc040203.',
'A. Ahmad, C. Migniot, and A. Dipanda, "Tracking hands in interaction with objects: A review," in Proc. Int. Conf. Signal-Image Technology and Internet-Based Systems (SITIS), 2017.',
'R. Y. Wang and J. Popovic, "Real-time hand-tracking with a color glove," ACM Transactions on Graphics, vol. 28, no. 3, pp. 1-8, 2009.',
'C. Diaz and S. Payandeh, "Multimodal sensing interface for haptic interaction," Journal of Sensors, vol. 2017, art. 2072951, pp. 1-24, 2017, doi: 10.1155/2017/2072951.',
'I. Oikonomidis, N. Kyriazis, and A. A. Argyros, "Efficient model-based 3D tracking of hand articulations using Kinect," in Proc. British Machine Vision Conf. (BMVC), 2011.',
'A. Tagliasacchi et al., "Robust articulated-ICP for real-time hand tracking," Computer Graphics Forum, vol. 34, no. 5, pp. 101-114, 2015.',
'C. Qian, X. Sun, Y. Wei, X. Tang, and J. Sun, "Realtime and robust hand tracking from depth," in Proc. IEEE Conf. Computer Vision and Pattern Recognition (CVPR), 2014.',
'L. Ge, H. Liang, J. Yuan, and D. Thalmann, "Robust 3D hand pose estimation from single depth images using multi-view CNNs," IEEE Transactions on Image Processing, vol. 27, no. 9, pp. 4422-4436, 2018.',
'G. Pavlakos, D. Shan, I. Radosavovic, A. Kanazawa, D. Fouhey, and J. Malik, "Reconstructing hands in 3D with transformers," in Proc. IEEE/CVF Conf. Computer Vision and Pattern Recognition (CVPR), 2024.',
'H. Dong et al., "Hamba: Single-view 3D hand reconstruction with graph-guided bi-scanning Mamba," in Advances in Neural Information Processing Systems, vol. 37, pp. 2127-2160, 2024.',
'F. Zhang et al., "MediaPipe Hands: On-device real-time hand tracking," arXiv:2006.10214, 2020.',
'M. Kalaitzakis, B. Cain, S. Carroll, A. Ambrosi, C. Whitehead, and N. Vitzilaios, "Fiducial markers for pose estimation: Overview, applications and experimental comparison," Journal of Intelligent and Robotic Systems, vol. 101, art. 71, 2021.',
'J. L. Pulloquinga, D. Corrata, V. Mata, A. Valera, and M. Valles, "Experimental analysis of pose estimation based on ArUco markers," in Innovations in Industrial Engineering III (Lecture Notes in Mechanical Engineering), Cham: Springer, 2024, pp. 138-149.',
'F. Krebs and T. Asfour, "Formalization of temporal and spatial constraints of bimanual manipulation categories," in Proc. IEEE/RSJ Int. Conf. Intelligent Robots and Systems (IROS), 2024.',
'G. Moon, S.-I. Yu, H. Wen, T. Shiratori, and K. M. Lee, "InterHand2.6M: A dataset and baseline for 3D interacting hand pose estimation from a single RGB image," in Proc. European Conf. Computer Vision (ECCV), 2020.',
'W. Wang et al., "RGB2Hands: Real-time tracking of 3D hand interactions from monocular RGB video," ACM Transactions on Graphics, vol. 39, no. 6, 2020.',
'T.-W. Chen and W.-L. Lin, "3D human motion reconstruction in Unity with monocular camera," in Proc. Int. SoC Design Conf. (ISOCC), 2020.',
'V. N. Dubey and S. K. Manna, "Design of a game-based rehabilitation system using Kinect sensor," in Proc. ASME Design of Medical Devices Conf. (DMD), 2019.',
'Y. Chen et al., "RePose: A real-time 3D human pose estimation and biomechanical analysis framework for rehabilitation," arXiv:2601.00625, 2026.',
'M. S. Ahn, H. Chae, D. Noh, H. Nam, and D. Hong, "Analysis and noise modeling of the Intel RealSense D435 for mobile robots," in Proc. Int. Conf. Ubiquitous Robots (UR), 2019.',
'E. Curto and H. Araujo, "Fitting a normal probability distribution to depth estimations of three RealSense RGB-D cameras tested in scenes with transparency," ISPRS Annals of the Photogrammetry, Remote Sensing and Spatial Information Sciences, 2022.',
'S. Hampali, M. Rad, M. Oberweger, and V. Lepetit, "HOnnotate: A method for 3D annotation of hand and object poses," in Proc. IEEE/CVF Conf. Computer Vision and Pattern Recognition (CVPR), 2020.',
'J. S. Matthis and A. Cherian, "FreeMoCap: A free, open source markerless motion capture system," ver. 0.0.54, Zenodo, 2022, doi: 10.5281/zenodo.7233714.',
'C. E. Leiserson, N. C. Thompson, J. S. Emer, B. C. Kuszmaul, B. W. Lampson, D. Sanchez, and T. B. Schardl, "There\'s plenty of room at the Top: What will drive computer performance after Moore\'s law?," Science, vol. 368, no. 6495, art. eaam9744, 2020.',
])}

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

out = "/home/luo/Desktop/New_SandBox/writing/v6/Chapter_1_Introduction.docx"
doc.save(out)
print("saved", out, "| paragraphs:", len(content), "| refs tracked:", len(references))
