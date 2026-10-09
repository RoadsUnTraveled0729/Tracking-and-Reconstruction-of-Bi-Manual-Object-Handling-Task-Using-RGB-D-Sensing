Verified: 2026-09-28
Sources: eval/akc_comparison/README.md, eval/akc_comparison/DECISIONS.md
(AKC-001 to AKC-057), eval/akc_comparison/results/*.csv,
eval/akc_comparison/results/run_info.json,
/home/luo/.claude/plans/delegated-juggling-key.md
Answers: what the Kwok, Koenig and Hu Arm Kinematic Correction paper is
and what it leaves unspecified, the layout of the eval/akc_comparison/
sub-study, its headline numbers, the open author decisions, and how to
rerun it.

## The paper

Kwok, Koenig and Hu, "Seeing Through Occlusion: Deterministic Arm
Kinematic Correction for Robot Teleoperation", arXiv 2606.19240 (June
2026, no code released). One RGB-D camera, MediaPipe landmarks: a
visibility gate 0.7 and a 5%-of-image-width proximity rule discard the
depth of an elbow or shoulder near the wrist; a constant-velocity
Kalman filter per landmark follows (missing coordinates take the
prediction; an EKF variant adds a soft bone-length constraint); then,
keeping the wrist, elbow and shoulder depth are rebuilt from fixed arm
lengths by a Pythagorean relation (four sign candidates), and the
candidate with the lowest weighted cost wins. Their ground truth is
Vicon.

What the paper does not give (filled a priori here as library
constants, and logged UNCERTAIN in DECISIONS.md unless noted
otherwise): no released code; no Kalman process or measurement noise
Q, R (AKC-009, AKC-010); no dt for our 30 Hz recordings, since the
paper ran at 10 Hz (AKC-008); no filter initial covariance (AKC-011);
no EKF sigma_l (AKC-015); no anchor for the EKF length constraint --
here the Kalman-filtered wrist, the raw-wrist anchor kept as a sweep
row (AKC-056, UNCERTAIN, master decision of 2026-09-28 pending author
confirmation); no m5 penalty constant k (AKC-022); no
definition of theta for m5 beyond "the elbow angle" and the range
[40, 180] deg -- an unsigned angle cannot detect the paper's stated
theta > 180 hyper-extension bound (AKC-023, UNCERTAIN, author to
confirm or supply the paper's convention); no rule for whether the
shrunk candidate length feeds the output or only the branch search
(AKC-053, UNCERTAIN, master decision of 2026-09-28 pending author
confirmation); no T-pose in our recordings, so arm lengths come from
our own offset fit instead (AKC-030, our chain uses the same values).

## Layout

    eval/akc_comparison/
      akc.py                 pure-numpy library, no repository imports
      test_akc.py             synthetic-arm unit tests
      run_akc_comparison.py  experiments; imports recovery_core and
                             harness_recovery via sys.path
      charts.py              PNGs from results/*.csv only
      results/               committed csv, run_info.json, charts
      README.md, DECISIONS.md (AKC-001 onward)
    eval/output/akc_comparison/   gitignored per-frame tracks (not committed)

Three experiments: P1 (their protocol -- masked elbow, or elbow and
shoulder, on the three Chapter 7 windows of r7 right arm, plus an
outage-length sweep and full-recording arm-length variation on r5,
r6b, r7); P2a (our synthetic elbow+wrist protocol on r7, AKC given
either its own Kalman-predicted wrist or our object-derived wrist as a
hybrid); P2b (our natural-occlusion protocol on r5's manually labelled
failure frames). A Kalman/weights sensitivity sweep is reported, not
used to tune anything.

## Headline numbers

P1, their protocol (results/p1_synthetic_elbow.csv): r7 right elbow
removed (mask M-E, MASK_ALL), pooled over the three Chapter 7 windows
(n = 135), median and RMSE 3-D error in cm:

| method | R-self median | R-self RMSE | R-meas median | R-meas RMSE |
| --- | --- | --- | --- | --- |
| hold-last | 0.80 | 1.41 | 0.80 | 1.92 |
| KF-only | 1.67 | 2.53 | 1.61 | 2.52 |
| AKC-literal | 1.27 | 2.54 | 1.72 | 2.86 |
| AKC-ray | 1.20 | 2.24 | 1.65 | 2.50 |
| AKC-EKF | 1.58 | 3.78 | 1.71 | 3.79 |
| ours-memory | 0.63 | 1.11 | 1.04 | 1.35 |
| ours-IK | 1.90 | 2.08 | 2.07 | 2.19 |

R-self is each method's own unmasked output (the Chapter 7 protocol);
R-meas is the unmasked filtered landmark. There is no Vicon or other
ground truth in this comparison. The AKC-EKF row depends on the
constraint anchor (AKC-056): anchored on the raw measured wrist, as in
M2, it is 5.12 / 9.23 / 5.22 / 9.05; results/kf_sweep.csv gives 3.26 /
1.58 / 1.25 cm R-self at sigma_l 0.005 / 0.02 / 0.05 m with the
filtered anchor.

P2a, our synthetic protocol (results/p2a_wrist_synthetic.csv): r7
right, elbow and wrist removed (S1_arm), wrist R-self median cm per
window 490-534 / 445-489 / 557-601 (n = 45 each): hold-last 0.70 /
1.24 / 1.48; ours-memory 0.44 / 1.88 / 2.50; ours-object 1.17 / 1.21 /
1.90 (equal to the pinned Chapter 7 values, asserted); AKC-ray
(Kalman-predicted wrist) 0.79 / 2.00 / 2.04; AKC-hybrid (our
object-derived wrist) 1.43 / 1.36 / 1.37 -- R-meas is identical to
ours-object at 1.47 / 1.39 / 1.21, since both use the same wrist and
only the R-self reference differs.

P2b, our natural protocol (results/p2b_natural_labels.csv): r5,
distance from the manual wrist label on the labelled failure frames,
median cm, right n = 4: ours recovery_fk 5.22, plain_fk 11.38,
hold_fk 17.60 (pinned, recomputed and asserted); AKC-ray 13.57;
AKC-ray with our failure mask applied 32.01; AKC-hybrid 13.67. On the
clean labelled frames (right n = 4) AKC and the measured wrist agree
(2.35 vs 2.09 cm).

Arm-length variation (results/arm_length_range.csv, Table VI mirror):
r7 right, full unmasked run, range of forearm / upper-arm length, cm:
raw 7.59 / 6.41, KF-only 6.75 / 5.73, AKC-literal / AKC-ray / ours all
0 / 0 (constant by construction; the AKC-ray forearm is 23.30 cm on
every frame, inside the raw p5-p95 band of 21.09-25.22 cm).

Timing (results/timing.csv, this workstation, single run; the README
states reruns vary by a few percent): AkcArm.step mean 104 / 130 / 150
microseconds per frame (AKC-literal / AKC-ray / AKC-EKF, one arm); our
run_variant mean 362-371 microseconds per frame (both arms and the
body chain, including pandas iteration). Not a like-for-like
comparison (AKC-046). README.md quotes the same values from the same
timing.csv (timing.csv is the one results file that is not
byte-identical across reruns, AKC-045).

## Open author decisions

- AKC-053 (HIGH): whether the paper's length shrink (s = 0.9 for the
  library default W_C) is used only to choose the branch, with the
  output then re-solved at the unscaled length (the current library
  behaviour), or should shrink the output too (kept as the library's
  output_shrunk=True sweep row). Reversing it changes every AKC row.
- AKC-056 (HIGH): the EKF length constraint is anchored on the
  Kalman-filtered wrist (Stage 3, the reading adopted after the code
  review) rather than the raw measured wrist (M2, kf_sweep row
  ekf_anchor=raw). It moves the AKC-EKF pooled R-self median from
  5.12 to 1.58 cm; only the EKF rows depend on it.
- AKC-023: theta for the m5 elbow-angle plausibility term is read as
  an unsigned angle, which cannot detect the paper's stated
  theta > 180 hyper-extension bound (only theta < 40, over-flexion, is
  penalised). Author to confirm or supply the paper's convention.
- No Vicon or other ground truth exists in this repository's
  recordings; the paper's own comparison is against Vicon and cannot
  be reproduced here. Every number above is against R-self, R-meas, or
  (P2b) a manual wrist label.
- M3 (code review of akc.py and run_akc_comparison.py against the
  paper's equations): the Opus review found the library matching the
  paper's equations and no blocker; its fixes (EKF anchor AKC-056,
  added tests AKC-057) are in the working tree and the numbers above
  are from the rerun after them. The AKC numbers stay provisional
  until the master closes M3 (eval/akc_comparison/README.md, Status).

## How to rerun

    /home/luo/anaconda3/bin/python eval/akc_comparison/test_akc.py
    /home/luo/anaconda3/bin/python eval/akc_comparison/run_akc_comparison.py

The run script needs the gitignored v1 landmark CSVs, the r5 vis0 CSV
and eval/output/recovery_<alias>/ on this workstation; two full runs
give byte-identical results files except results/timing.csv (AKC-045).
Flags: --quick (P1 only), --charts-only (redraw the PNGs from
results/*.csv without rerunning the experiments).
