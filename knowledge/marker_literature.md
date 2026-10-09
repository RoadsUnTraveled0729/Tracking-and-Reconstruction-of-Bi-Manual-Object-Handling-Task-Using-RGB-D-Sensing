# ArUco vs AprilTag: what the published comparisons say

Verified: 2026-09-28
Sources:
- https://april.eecs.umich.edu/pdfs/olson2011tags.pdf
- https://april.eecs.umich.edu/pdfs/wang2016iros.pdf
- https://april.eecs.umich.edu/pdfs/krogius2019iros.pdf
- https://cs-courses.mines.edu/csci507/schedule/24/ArUco.pdf (publisher PDF of Garrido-Jurado et al. 2014)
- https://burjcdigital.urjc.es/bitstreams/925296d8-26e6-4833-a7f3-09f9bb77fa01/download (accepted manuscript of Romero-Ramirez et al. 2018)
- https://doi.org/10.1007/s10846-020-01307-9 (Kalaitzakis et al. 2021; paywalled, not read)
- https://doi.org/10.1109/ICUAS48674.2020.9213977 (Kalaitzakis et al. 2020 conference version; abstract only via api.semanticscholar.org)
- https://doi.org/10.1007/s10055-023-00772-5 (Jurado-Rodriguez et al. 2023; abstract only)
- https://arxiv.org/pdf/2601.07723v1 (Laurent and Sandoz 2026, preprint)
Answers: what published comparisons say about ArUco vs AprilTag speed and accuracy

Reading status: 5 primary sources read in full (Olson 2011, Wang and Olson
2016, Krogius et al. 2019, Garrido-Jurado et al. 2014, Romero-Ramirez et
al. 2018), plus 1 preprint read in full (Laurent and Sandoz 2026).
Abstract or metadata only: Kalaitzakis et al. 2021 and its 2020 conference
version, Jurado-Rodriguez et al. 2023. Not located: Sagitov et al. 2017.
Page numbers are PDF pages of the file listed under Sources unless a
journal page is given.

## 1. Primary sources

### Garrido-Jurado, Munoz-Salinas, Madrid-Cuevas, Marin-Jimenez (2014)
"Automatic generation and detection of highly reliable fiducial markers
under occlusion", Pattern Recognition 47(6), 2280-2292.
DOI 10.1016/j.patcog.2014.01.005. Read in full.
- Compared: the ArUco dictionary and detector against ARToolKitPlus and
  ARTag. AprilTag is not in the experiments (the word does not occur in
  the text).
- Speed (Table 3, journal p. 2287): candidate detection 8.17 ms/image,
  marker identification 0.17 ms/candidate, error correction 0.71
  ms/candidate, total 11.08 ms/image for a dictionary of 24 markers;
  one core of an Intel Core 2 Quad 2.40 GHz, 6000 images of 640x480.
- Accuracy: vertex jitter (standard deviation of static corners) shown as
  box plots only, Fig. 12 (journal p. 2289); no ArUco vs AprilTag number.
- False positives: "no false positives have been detected by any method in
  the video sequences tested" (Section 6.4).

### Romero-Ramirez, Munoz-Salinas, Medina-Carnicer (2018)
"Speeded up detection of squared fiducial markers", Image and Vision
Computing 76, 38-47. DOI 10.1016/j.imavis.2018.05.004. Accepted
manuscript read in full (13 pages; page numbers below are manuscript
pages).
- Compared: ArUco3 (the proposal), ArUco in OpenCV, AprilTags (reference
  [18] = Olson 2011, i.e. the original AprilTag), ChiliTags, ArToolKit+.
  Intel Core i7-4700HQ, one thread; 4K phone video, evaluated at 480p to
  2160p.
- Speed: Fig. 5 (p. 7) gives speed-ups of ArUco3 over every other system,
  AprilTags included, as plots only (no AprilTag ms value printed).
  ArUco3 Table 1 (p. 8): 0.903 ms total at 480p, 2.755 ms at 2160p.
  "Compared to ArUco implementation in the OpenCV library, the proposed
  method is significantly faster, achieving a minimum speedup of 17 in 4K
  resolutions, up to 40 in the best case" (p. 8).
- Detection: Fig. 7 (p. 9) true positive ratio; "AprilTags, however, has
  very poor behavior in all resolutions, especially as the marker or the
  image sizes increases" (p. 8). False positive rate zero for ArUco3 in all
  cases tested.
- Corner precision, Table 3 (p. 10), vertex jitter standard deviation:
  ArUco 0.140 px, ArUco3 0.161 px, Chilitags 0.174 px, AprilTags 0.225 px,
  ArToolKit+ 0.432 px. This is repeatability of a static camera, not
  accuracy against ground truth.

### Olson (2011)
"AprilTag: A robust and flexible visual fiducial system", IEEE ICRA 2011,
pp. 3400-3407. DOI 10.1109/ICRA.2011.5979561. Read in full.
- Compared: AprilTag against ARToolKitPlus and ARTag (codes) and against
  the ARToolKitPlus detector (localisation). No ArUco (it did not yet
  exist).
- Speed (p. 7): "our Java implementation runs at interactive rates (30
  fps) on VGA resolution images (Intel Core2 CPU at 2.6GHz)", and "our
  methods are generally more computationally expensive than those used by
  ARToolkitPlus".
- Accuracy (p. 7, Figs. 9-10, ray-traced 400x400 images, focal 400 px):
  "our detector works reliably to 50 m, while the ARToolkitPlus detector's
  detection rate drops to under 50% at around 25 m".
- False positives: Fig. 7 (LabelMe, 180,829 images) shows the 36h10 code
  below ARTag and ARToolKitPlus-BCH.

### Wang and Olson (2016)
"AprilTag 2: Efficient and robust fiducial detection", IEEE/RSJ IROS
2016, pp. 4193-4198. DOI 10.1109/IROS.2016.7759617. Read in full.
- Compared: AprilTag 2 against the original AprilTag detector only.
- Speed (p. 6): single thread, Intel Xeon E5-2640 2.5 GHz, "about 78 ms
  and 115 ms, respectively, for a 640 x 480 image" (new, old); "With
  decimation by a factor of 2, the new detector only takes 0.072
  microseconds per pixel, or about 22 ms for a 640 x 480 image". The
  authors add that "the absolute times are not meant to be
  representative".
- False positives, Table I (p. 4), LabelMe 421,049 images, 36h11 with up
  to 2 bits corrected: old 145 false detections (0.000284 %), new 6
  (0.000044 %).

### Krogius, Haggenmiller, Olson (2019)
"Flexible Layouts for Fiducial Tags", IEEE/RSJ IROS 2019, pp. 1898-1903.
DOI 10.1109/IROS40897.2019.8967787. Read in full.
- Compared: AprilTag 3, AprilTag 2 and "ArUco 3 - 36h11" (the ArUco
  detector in DM_FAST mode run on 36h11 tags), 160 images, 1296x964,
  tags 4 cm, 20-160 cm, face-on and 45 degrees; Intel Core i7-7600U 2.80
  GHz (p. 4).
- Result: Fig. 7 (p. 6), recall versus frames per second over a parameter
  sweep (AprilTag decimation, ArUco minMarkerSize): "We can see that the
  AprilTag 3 detector is faster and has higher recall than both the
  AprilTag 2 and ArUco detectors" (p. 5). Values are plotted only; no
  numbers are printed, and corner or pose accuracy is not compared.

### Kalaitzakis, Cain, Carroll, Ambrosi, Whitehead, Vitzilaios (2021)
"Fiducial Markers for Pose Estimation: Overview, Applications and
Experimental Comparison of the ARTag, AprilTag, ArUco and STag Markers",
Journal of Intelligent and Robotic Systems 101(4), article 71.
DOI 10.1007/s10846-020-01307-9. PAYWALLED: full text and abstract could
not be retrieved (Springer and ResearchGate refused, Crossref and
Semantic Scholar carry no abstract). No number from this paper is
recorded here. A web-search summary said AprilTag was more accurate and
ArUco competitive in detection rate; that summary is not a verified
source and is not used.
Conference version: Kalaitzakis, Carroll, Ambrosi, Whitehead, Vitzilaios,
"Experimental Comparison of Fiducial Markers for Pose Estimation", ICUAS
2020, pp. 781-789, DOI 10.1109/ICUAS48674.2020.9213977. Abstract only:
it compares ARTag, AprilTag, ArUco and STag "based on their localization
capabilities as well as their computational efficiency"; the abstract
gives no numbers.

### Jurado-Rodriguez, Munoz-Salinas, Garrido-Jurado, Medina-Carnicer (2023)
"Planar fiducial markers: a comparative study", Virtual Reality 27,
1733-1749. DOI 10.1007/s10055-023-00772-5. Abstract only (a green open
copy is listed at http://hdl.handle.net/10396/33618 but could not be
fetched in this session). The abstract states the study compares marker
systems "in terms of sensitivity, specificity, accuracy, computational
cost, and performance under occlusion"; it gives no numbers.

### Sagitov et al. (2017), ARTag/AprilTag/CALTag comparison
Not located or read in this session. It does not include ArUco.

## 2. Preprints and informal sources (not peer reviewed)

### Laurent and Sandoz (2026), arXiv:2601.07723v1
"FMAC: a Fair Fiducial Marker Accuracy Comparison Software". Preprint,
read in full. 10,000 synthetic images rendered with Logitech C270
parameters (640x480), 50 mm markers, depth 500-1500 mm.
- ArUco (OpenCV 4.13.0; corner refinement setting not stated), p. 11:
  pose error standard deviation 5.4 mm in X, 3.8 mm in Y, 14.7 mm in Z;
  rotation standard deviation "in the order of a tens of degrees" because
  of pose ambiguity in fewer than 5 per thousand poses; detection rate
  100 %.
- AprilTag (3.4.5 release), p. 13: 99.74 % detected; "The errors in all
  degrees of freedom are significantly smaller"; "a systematic error in X
  and Y: the mean error is 0.62 mm in both directions. This error is
  equivalent to half a pixel".
- No timing.

## 3. What OpenCV's DICT_APRILTAG_36h11 is

OpenCV's aruco module ships AprilTag dictionaries (DICT_APRILTAG_16h5 ...
36h11). Detecting them with cv2.aruco.ArucoDetector runs the ArUco
pipeline (adaptive threshold, contours, bit sampling) on AprilTag bit
patterns. A comparison of DICT_5X5_50 and DICT_APRILTAG_36h11 through
that detector is therefore a comparison of dictionaries, not of
detectors. The AprilTag detector itself (quad fitting on the gradient
clusters, AprilTag 2/3 C library) is only exercised through the AprilTag
library (for example the pupil-apriltags binding). Separately, OpenCV's
CORNER_REFINE_APRILTAG option (the pinned setting in
v1/aruco/extract_aruco_poses.py) borrows the AprilTag quad-fitting step
for corner refinement inside the ArUco detector.

## 4. Verdict on "similar performance, AprilTag slower but more accurate"

Partly supported, partly contradicted. The accuracy half has some
support: the FMAC preprint reports AprilTag 3.4.5 pose errors
"significantly smaller" than OpenCV ArUco on identical synthetic images
(pp. 11 and 13), and Olson 2011 (p. 7) shows AprilTag localising more
accurately than ARToolKitPlus; but the only peer-reviewed table that
puts both side by side, Romero-Ramirez et al. 2018 Table 3 (p. 10),
shows the opposite for corner repeatability (ArUco 0.140 px vs original
AprilTags 0.225 px jitter), and the head-to-head accuracy study
(Kalaitzakis et al. 2021) could not be read. The speed half depends on
the AprilTag version: the original AprilTag was slower (Olson 2011 p. 7
calls it "more computationally expensive" than ARToolKitPlus; Wang and
Olson 2016 p. 6 report 78 ms per 640x480 frame for AprilTag 2 without
decimation, versus 11.08 ms for ArUco in Garrido-Jurado et al. 2014
Table 3 on older hardware), but the AprilTag 3 detector is reported
faster than ArUco at equal or higher recall (Krogius et al. 2019, Fig. 7,
p. 6). "Similar performance" in detection is not supported for the
original AprilTag (Romero-Ramirez et al. 2018 p. 8: "very poor behavior"
of AprilTags in their true positive tests) and is at most plausible for
AprilTag 3. The published record therefore does not support a single
"slower but more accurate" statement; the answer is version- and
setting-dependent, and the local measurement in
presentation/defense_2026/experiments/marker_bench/ is the more direct
evidence for this project's setting.
