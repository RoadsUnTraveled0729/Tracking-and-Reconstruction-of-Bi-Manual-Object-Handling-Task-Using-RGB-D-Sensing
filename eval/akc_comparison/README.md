# AKC comparison (eval/akc_comparison)

## Purpose

Kwok, Koenig and Hu (arXiv 2606.19240, June 2026) recover occluded
elbow and shoulder positions from one RGB-D camera with a per-landmark
constant-velocity Kalman filter followed by Arm Kinematic Correction
(AKC): keeping the wrist, the elbow and shoulder depth are rebuilt from
fixed arm lengths and the most plausible of four configurations is
chosen by a weighted cost. They released no code. This folder
re-implements their method from the paper text (akc.py) and, in
milestone M2, runs it on our recordings next to our occlusion recovery
under their protocol and our Chapter 7 protocols. It answers one
question: how does their method compare with ours on the same data.

## Status

Exploratory. M1 (library and unit tests) and M2 (comparison runs,
results/) are done; the M3 review of akc.py and the run script is
pending, so treat the AKC numbers as provisional. Every gap the paper
leaves open is an UNCERTAIN entry in DECISIONS.md. Two of those gaps
are master decisions the author has not yet confirmed: the AKC output
is at the unscaled arm lengths, the shrink used for branch selection
only (AKC-053; the M2 shrunk output of AKC-051 is kept as a sweep row),
and m5's theta is the unsigned elbow angle, so the paper's stated
theta > 180 hyper-extension bound cannot fire (AKC-023, author to
confirm or supply the paper's convention). There is also no Vicon or
other independent ground truth in this comparison, unlike the paper:
every accuracy number here is against each method's own unmasked
output (R-self) or the unmasked filtered landmark (R-meas), or against
manual wrist labels on r5.

## Design decisions

- Paper values used as published: visibility gate 0.7, 5 % proximity
  rule, constant-velocity Kalman filter, EKF length constraint, the
  Pythagorean candidates with shrink and fallback, and weight sets
  W_a, W_b, W_c with w4 = w5 = 100 ([AKC-003](DECISIONS.md),
  AKC-004, AKC-007, AKC-014, AKC-017, AKC-020).
- The shrunk length l' = s l chooses the branch only; the chosen
  branch is then re-solved with the paper's relation at the unscaled
  lengths (same pixel ray or x, y, same sign), with a counted radial
  fallback that the full run never takes (AKC-053 to AKC-055).
- Kalman noise and covariances the paper does not give are fixed a
  priori and never tuned on scored data (AKC-009 to AKC-011, AKC-015).
- Two geometries: "literal" (the paper's fixed x, y) and "ray" (the
  pixel is kept and depth is solved on its camera ray) (AKC-018,
  AKC-019).
- The elbow angle for m5 is the unsigned angle at the elbow, so only
  over-flexion below 40 degrees is penalised (AKC-023).
- Correction every frame, no feedback into the filter, costs in
  metres (AKC-024, AKC-025, AKC-028).

## Results

All numbers come from results/*.csv, written by run_akc_comparison.py
(conditions and n in every row; decisions AKC-033 to AKC-056). There is
no ground truth: R-self is each method's own unmasked output (the
Chapter 7 protocol), R-meas the unmasked filtered MediaPipe landmark
(AKC-034). AKC reads the raw landmark CSV, ours the filtered one
(AKC-021, plan A4). Errors are 3-D, cm.

P1, their protocol (results/p1_synthetic_elbow.csv). r7 right arm, elbow
removed (M-E, MASK_ALL) for 45 frames in each of the three Chapter 7
windows, pooled n = 135:

| method | median R-self | RMSE R-self | median R-meas | RMSE R-meas |
| --- | --- | --- | --- | --- |
| hold-last | 0.80 | 1.41 | 0.80 | 1.92 |
| KF-only | 1.67 | 2.53 | 1.61 | 2.52 |
| AKC-literal | 1.27 | 2.54 | 1.72 | 2.86 |
| AKC-ray | 1.20 | 2.24 | 1.65 | 2.50 |
| AKC-EKF | 1.58 | 3.78 | 1.71 | 3.79 |
| ours-memory | 0.63 | 1.11 | 1.04 | 1.35 |
| ours-IK | 1.90 | 2.08 | 2.07 | 2.19 |

Unmasked, AKC-ray is 0.55 cm (elbow) and 1.77 cm (shoulder) from R-meas
(pooled median over the three windows, n = 135), AKC-literal 0.63 /
0.93 cm, the KF alone 0.11 / 0.14 cm. AKC fixes the arm lengths while
the measured forearm varies (r7 raw p5-p95 21.09 to 25.22 cm); on
perfect synthetic input it is exact (test (2), AKC-053). With the
shrunk M2 output the offsets were 2.62 / 5.47 cm (AKC-051). The three
weight sets give the same scored elbow in these windows (AKC-053).
With the pixel kept and only depth removed (MASK_Z), AKC-ray
reproduces its unmasked output exactly (0.00 cm), because ray mode does
not use the measured depth (AKC-038). With the shoulder also removed
(M-ES) the AKC elbow is unchanged and ours-memory rises to 0.97 cm
R-self. On shoulder rows, ours R-self equals R-meas and ours-memory
equals ours-IK by construction: the unmasked ours shoulder is the
filtered landmark, and both variants output the same pair-memory
shoulder while it is masked. Outage sweep (results/p1_outage_sweep.csv,
anchored at frame 445, R-self median, cm):

| frames | 15 | 30 | 45 | 60 | 75 | 90 |
| --- | --- | --- | --- | --- | --- | --- |
| KF-only | 1.01 | 1.77 | 2.39 | 2.65 | 2.80 | 3.36 |
| AKC-ray | 0.34 | 0.68 | 0.98 | 1.66 | 2.18 | 3.08 |
| ours-memory | 0.55 | 1.58 | 1.73 | 1.75 | 2.17 | 2.22 |
| ours-IK | 1.74 | 1.97 | 2.14 | 2.32 | 3.14 | 3.06 |

P2a, our synthetic protocol (results/p2a_wrist_synthetic.csv). r7 right,
elbow and wrist removed (S1_arm), wrist median R-self per window
490-534 / 445-489 / 557-601, n = 45 each: hold-last 0.70 / 1.24 / 1.48;
ours-memory 0.44 / 1.88 / 2.50; ours-object 1.17 / 1.21 / 1.90 (equal
to the pinned Chapter 7 values, asserted); AKC-ray with its
Kalman-predicted wrist 0.79 / 2.00 / 2.04; AKC-hybrid with our
object-derived wrist 1.43 / 1.36 / 1.37 (the same wrist as ours-object;
the difference is the R-self reference, R-meas is identical at 1.47 /
1.39 / 1.21, AKC-050).

P2b, our natural protocol (results/p2b_natural_labels.csv). r5,
distance from the manual wrist label on the labelled failure frames,
median cm, right n = 4 / left n = 16: ours recovery_fk 5.22 / 13.14,
plain_fk 11.38 / 12.31, hold_fk 17.60 / 12.66 (pinned, recomputed and
asserted); AKC-ray 13.57 / 10.20; AKC-ray with our failure mask applied
32.01 / 7.95; AKC-hybrid 13.67 / 13.14. On the clean labelled frames
AKC and the measured wrist agree (right 2.35 vs 2.09, n = 4). The vis0
and 0.5-gated inputs give identical AKC tracks (AKC-048). P2a and P2b
score the wrist, which AKC keeps and AKC-053 does not move; their wrist
numbers are unchanged from M2 (the P2a AKC elbow rows do change).

Arm-length variation (results/arm_length_range.csv, Table VI mirror),
r7 right, full unmasked run, range of forearm / upper-arm length, cm:
raw 7.59 / 6.41, KF-only 6.75 / 5.73, AKC-literal, AKC-ray and ours
0 / 0 (constant by construction). The AKC-ray forearm is 23.30 cm on
every frame, inside the raw p5-p95 band of 21.09 to 25.22 cm, so the
planned sanity check holds (with the M2 shrunk output it failed at a
20.97 cm minimum, AKC-051).

KF sweep (results/kf_sweep.csv, AKC-044): reported, not used to tune.
The AKC-EKF variant ties the elbow to the Kalman-filtered wrist
(AKC-056): R-self median 3.26 / 1.58 / 1.25 cm at sigma_l 5 / 20 / 50
mm. Tied to the raw measured wrist instead (the M2 reading, row
ekf_anchor=raw, sigma_l 20 mm) it gives 5.12 cm R-self, 5.22 cm R-meas:
during a mask the elbow covariance is narrow along the bone and wide
across it, so raw-wrist jitter slides the elbow sideways. The
output_shrunk=True row reproduces the M2 behaviour (1.23 cm R-self,
2.58 cm R-meas). The feedback=True row gives 1.00 / 1.29 cm
(R-self / R-meas). W_a, W_b and W_c rows are identical (1.20 / 1.65
cm) because the elbow branch agrees in the scored windows.

Timing (results/timing.csv, this workstation; the committed run gave
the values below, reruns vary by a few percent): AkcArm.step 104 / 130 /
150 microseconds per frame (literal / ray / EKF, one arm); our
run_variant 362 to 371 microseconds per frame (both arms and the body
chain, including pandas iteration). Not a like-for-like comparison
(AKC-046).

## Limitations

- A re-implementation from the text; unstated details are our choices
  (DECISIONS.md, UNCERTAIN entries). The reading of the length shrink
  (AKC-053, shrunk output in AKC-051) is the one that moves the numbers
  most.
- No Vicon or other ground truth: every accuracy number is against
  R-self or R-meas, and on r5 against manual wrist labels (n = 4 right).
- Our landmark CSVs carry no pixel columns, so pixels are projected
  from xyz (AKC-005); a depth-only mask has no natural counterpart in
  our data, and MASK_Z is extra information given to AKC only.
- AKC reads the raw CSV and ours the filtered one; one sweep row runs
  AKC on the filtered CSV (1.24 vs 1.20 cm R-self).
- The paper's hyper-extension bound (theta > 180 degrees) is not
  detectable with an unsigned angle (AKC-023).
- No T-pose calibration in our recordings; arm lengths come from our
  offset fit (AKC-030).
- r6b left: AKC produces nothing (the wrist never passes the 0.7 gate,
  AKC-052).

## How to run

    /home/luo/anaconda3/bin/python eval/akc_comparison/test_akc.py
    /home/luo/anaconda3/bin/python eval/akc_comparison/run_akc_comparison.py

The tests print PASS / FAIL per check and exit 1 on any failure. The run
script (about one minute) needs the gitignored v1 landmark CSVs, the r5
vis0 CSV and eval/output/recovery_<alias>/ on this workstation; it
asserts the Chapter 7 regressions and the mask-injection checks, writes
results/ (byte-identical on rerun except timing.csv), per-frame tracks
to eval/output/akc_comparison/, and calls charts.py. Flags: --quick (P1
only), --charts-only (redraw the PNGs from results/*.csv).
