# Slide text draft (pages 36 and 37)

Every number below is either in summary.csv (this folder) or in
knowledge/marker_literature.md with its page, table or figure.

## Page 36: ArUco vs AprilTag in the literature

Claim: Published comparisons disagree; the answer depends on the
AprilTag version and the detector settings.

| Detector | Reported detection time | Reported accuracy | Source |
| --- | --- | --- | --- |
| ArUco (OpenCV) | 11.08 ms per 640x480 image, one core, Core 2 Quad 2.4 GHz | no false positives in the test videos | Garrido-Jurado et al. 2014, Table 3 |
| AprilTag (original) | 30 fps on VGA (Java, Core2 2.6 GHz); more expensive than ARToolKitPlus | reliable to 50 m in simulation | Olson 2011, p. 7 |
| AprilTag 2 | 78 ms per 640x480; 22 ms with decimation 2 (one thread, Xeon 2.5 GHz) | false positive rate 0.000044 % | Wang and Olson 2016, p. 6; Table I (p. 4) |
| AprilTag 3 vs ArUco 3 | AprilTag 3 faster at higher recall (parameter sweep) | not compared | Krogius et al. 2019, Fig. 7 |
| ArUco vs AprilTag (original) | ArUco3 faster than all tested systems | corner jitter 0.140 px (ArUco) vs 0.225 px (AprilTag) | Romero-Ramirez et al. 2018, Table 3 |

## Page 37: measured on this workstation

Title: AprilTag 3 faster; corner errors converge at 96 px

Claim: At 48 px, AprilTag 3 detects in 2.8 to 3.8 ms against 10.9 to
31.3 ms for our pinned ArUco, depending on added noise; after removing a
constant offset of about 0.5 px, its corner error is 0.095 px against
0.137 px, and at 96 px all detectors lie between 0.069 and 0.074 px.

Speed figures are medians over the 9 tilt x blur conditions at 48 px per
noise level (results.csv): noise-free 2.82 ms (AprilTag 3, decimate 2)
and 10.86 ms (ArUco pinned); noise sigma 8: 3.79 ms and 31.34 ms.

Source: experiments/marker_bench/summary.csv, this workstation, single thread

Speaker notes:
- The benchmark pastes a 5x5 ArUco and a 36h11 AprilTag with known
  corners onto 50 real frames of our recording and varies size, tilt,
  blur and noise, so every detector sees the same images.
- The times are medians at 48 px: 2.8 ms for AprilTag 3 and 10.9 ms
  for our ArUco without added noise, rising to 3.8 ms and 31.3 ms with
  the strongest added noise, which slows the OpenCV detector far more.
- The corner errors on the chart are after removing a constant offset
  of about 0.5 px per axis, a coordinate convention that differs between
  the libraries; they are 0.137 px for our ArUco and 0.095 px for
  AprilTag 3 at 48 px, and converge only at 96 px.
- Most of our ArUco time is the AprilTag corner refinement we pinned
  for sub-pixel corners: without it the same detector takes 8.4 ms at
  48 px over all conditions, but its raw corner error rises from
  0.664 px to 0.978 px.
- So my recollection that AprilTag was slower holds for the original
  AprilTag, not for AprilTag 3; [author to confirm the reason] ArUco
  was kept because it is built into OpenCV and already sub-pixel
  accurate at our marker sizes.
