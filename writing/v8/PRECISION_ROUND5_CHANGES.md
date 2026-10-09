# Round 5 (C48): every number to at most two decimals, old -> new

Supervisor comment on Chapter 4, 2026-09-07: "In the value of the
matrices, do not go beyond two decimals. For example, if it is 0.0014
just write 0.0. Same comments for all the numerical values." Applied
to the whole thesis at the user's direction. Each pair below is an
exact find/replace on the built text of writing/v8/Thesis_V8_Condensed.docx
(for hand-syncing a copy); everything not listed is unchanged. The
builders keep the full-precision values as source comments. Rounding
is from the full-precision sources, half away from zero.

Conventions: rotation entries and unit vectors two decimals, near-zero
0.00; vectors in equations in metres with two decimals; prose
distances in centimetres or millimetres with one decimal; angles to
0.1 degree; session-clock times in seconds with two decimals, offsets
in whole milliseconds; where the rounded operands no longer give the
printed result, the intermediate value is dropped or only the result
is stated.

## Chapter 2, Section 2.5 (the user's own sentence; also recorded in condensed/notes_followup_ch2.md)

1. "multiplied by 1.4826 (Appendix F)" -> "multiplied by about 1.48 (Appendix F)"

## Chapter 4, Section 4.3 Worked Example

1. Matrix M-bar: 0.9997, −0.0014, −0.0243 / −0.0219, −0.4832, −0.8752 / −0.0105, 0.8755, −0.4831 -> 1.00, 0.00, −0.02 / −0.02, −0.48, −0.88 / −0.01, 0.88, −0.48
2. "Equation (2.1) projects it back, moving no entry by more than 0.000002, since the ten input rotations disagree so little." -> "Equation (2.1) projects it back onto the nearest rotation, and at the precision printed here no entry changes, because the ten input rotations disagree so little."
3. "With the mean of the ten translations, (0.0235, 0.1874, 0.5525) m, the projected rotation forms the frozen anchor T_CW, which puts" -> "With the mean of the ten translations, the projected rotation forms the frozen anchor T_CW. That anchor puts" (the vector is dropped: at two decimals it no longer gives the 55.3 and 18.7 cm that follow; the worked example now opens with the sentence "Vectors and matrices are printed to two decimals and every distance is computed at full precision.")
4. "reads (-0.0212, 0.5300, 0.8477) in world coordinates" -> "reads (−0.02, 0.53, 0.85) in world coordinates"
5. Display: "−R^T t = (−0.0135, −0.3931, 0.4315) m" -> "−R^T t = (−0.01, −0.39, 0.43) m"
6. Display: "t_CO = (−0.2095, 0.1560, 1.0229) m" -> "t_CO = (−0.21, 0.16, 1.02) m"
7. "Adding the camera position to the first product, (−0.2236, 0.8204, −0.6256) m, gives the world translation, with the rotation product beside it:" -> "Adding the camera position to the first product gives the world translation, with the rotation product beside it:"
8. Display: "t_WO = (−0.2371, 0.4273, −0.1941) m" -> "t_WO = (−0.24, 0.43, −0.19) m"
9. Matrix R_WO: 0.9975, 0.0133, 0.0697 / 0.0528, 0.5178, −0.8539 / −0.0475, 0.8554, 0.5158 -> 1.00, 0.01, 0.07 / 0.05, 0.52, −0.85 / −0.05, 0.86, 0.52
10. "at world x 0.0304 m and 0.0341 m" -> "at world x 3.0 cm and 3.4 cm"
11. "3.3 mm and 1.18 degrees" -> "3.3 mm and 1.2 degrees"

(C49, same chapter: new Figure 4.1 and its introducing paragraph in
Section 4.1; the track plot and its one reference become Figure 4.2.)

## Chapter 5, Section 5.6 Worked Example

1. Display: "L1 = 0.317 m,        L2 = 0.205 m" -> "L1 = 31.7 cm,        L2 = 20.5 cm"
2. Display, law of cosines: "(0.317² + 0.507² − 0.205²) / (2 · 0.317 · 0.507) = 0.98" -> "(31.7² + 50.7² − 20.5²) / (2 · 31.7 · 50.7) = 0.98"
3. "the elbow lies 0.317 m from the shoulder and 0.205 m from the wrist." -> "the elbow lies 31.7 cm from the shoulder and 20.5 cm from the wrist."

## Chapter 6, Section 6.5 Worked Example and Table 6.2

1. "published the frame at 18.280 seconds" -> "published the frame at 18.28 seconds"
2. "The merger's tick at 18.318 seconds on the session clock, with frame 549 just published, rendered the world as of 18.251 seconds, two frame intervals earlier. Samples of the person stream at 18.247 and 18.280 seconds lay on either side of that render time, so the merger interpolated between frames 547 and 548." -> "The merger's tick at 18.32 seconds on the session clock, with frame 549 just published, rendered the world as of 18.25 seconds, two frame intervals earlier. The person samples of frames 547 and 548 lay on either side of that render time, 4 milliseconds before it and 29 milliseconds after it, so the merger interpolated between them."
3. Table 6.2: "18.280 s on the session clock" -> "18.28 s on the session clock"; "tick at 18.318 s, render time 18.251 s" -> "tick at 18.32 s, render time 18.25 s"; Link row "(−20.7, 15.1, 102.1) cm" -> "(−20.6, 15.1, 102.1) cm"
4. Two double-rounding corrections found by the new number source (condensed/scripts/ch6_numbers.py; V7 had rounded four-decimal values a second time): the camera "(−1.4, 43.2, −39.3)" -> "(−1.4, 43.1, −39.3)" (0.431492 m); the cube in the camera frame "(−20.7, 15.1, 102.1)" -> "(−20.6, 15.1, 102.1)" (−0.206489 m), in the prose and in Table 6.2.

(U2, same section: the pelvis paragraph is replaced by the calculation
of equation (6.2) with its numbers, R_cam, t_cam, A = S R_cam F, S t_cam,
q and p_U, then the levelling rotation L and the raise to the floor,
and the object paragraph gains the inverse path R = R_cam^T, t, p_W = S
p_U and p_C = R p_W + t. The surrounding sentences and every result
are unchanged apart from the two corrections above.)

## Appendix C.3 and Table C.2

1. "visibility of 0.5778, above the 0.50 gate. The extractor stores the sampled pixel rather than the normalized pair, so the normalized coordinates are given here as the interval that truncates to the stored pixel:" -> "visibility of 0.58, above the 0.50 gate. The extractor stores the sampled pixel rather than the normalized pair: the normalized coordinates multiplied by the image width and height, 640 and 480, truncate to the stored pixel (209, 308)."
2. Display "x_n ∈ [0.3266, 0.3281) → u = 209 / y_n ∈ [0.6417, 0.6438) → v = 308" -> deleted.
3. "is 1.060 metres" -> "is 1.06 metres"
4. Display "x = 1.060 · (209 − 323.93756)/607.56128 = −0.201 / y = 1.060 · (308 − 248.01741)/607.01508 = +0.105" -> "x = 1.06 · (209 − 323.94)/607.56 = −0.20 / y = 1.06 · (308 − 248.02)/607.02 = +0.10"
5. "(-0.201, 0.105, 1.060) metres" -> "(−0.20, 0.10, 1.06) metres"
6. Table C.2 rows: "0.9987 | 1.311 | (-0.164, -0.335, 1.311)" -> "1.00 | 1.31 | (−0.16, −0.33, 1.31)"; "0.7031 | 1.196 | (-0.201, -0.045, 1.196)" -> "0.70 | 1.20 | (−0.20, −0.05, 1.20)"; "0.5778 | 1.060 | (-0.201, 0.105, 1.060)" -> "0.58 | 1.06 | (−0.20, 0.10, 1.06)"

## Table D.1 and Appendix D.4

7. "607.56128 px" -> "607.56 px"; "607.01508 px" -> "607.02 px"; "323.93756 px" -> "323.94 px"; "248.01741 px" -> "248.02 px"
8. "median depth is 0.986 metres" -> "median depth is 0.99 metres"
9. Display "x = 0.986 · (200 − 323.93756)/607.56128 = 0.986 · (−0.20399) = −0.201 / y = 0.986 · (341 − 248.01741)/607.01508 = 0.986 · (+0.15318) = +0.151" -> "x = 0.99 · (200 − 323.94)/607.56 = −0.20 / y = 0.99 · (341 − 248.02)/607.02 = +0.15"
10. "(-0.201, 0.151, 0.986) metres" -> "(−0.20, 0.15, 0.99) metres"

## Table E.1 and Appendix E.4

11. Wall row "(-1.031, -0.470, 3.055) | 3.258 | 3.185" -> "(−1.03, −0.47, 3.05) | 3.26 | 3.19"; desk row "(0.023, 0.187, 0.552) | 0.583 | 0.532" -> "(0.02, 0.19, 0.55) | 0.58 | 0.53"; object row "(-0.209, 0.156, 1.023) | 1.056 | 0.986" -> "(−0.21, 0.16, 1.02) | 1.06 | 0.99"
12. Matrix R: 0.998259, −0.008185, 0.058415 / −0.005833, −0.999170, −0.040308 / 0.058697, 0.039897, −0.997478 -> 1.00, −0.01, 0.06 / −0.01, −1.00, −0.04 / 0.06, 0.04, −1.00
13. "The rotation is proper before display rounding. The matrix coefficients retain extra digits to show the calculation; the reported angle is rounded to a tenth of a degree. The angle follows from the trace:" -> "The entries are printed to two decimals and the angle to a tenth of a degree; both are computed from the unrounded matrix, which is a proper rotation. The angle follows from the trace:"
14. Display "tr R = 0.998259 − 0.999170 − 0.997478 = −0.998389 / θ = acos((−0.998389 − 1)/2) = 177.7°" -> "θ = acos((tr R − 1)/2) = 177.7°"
15. "w = (+0.9996, −0.0035, +0.0293)" -> "w = (1.00, 0.00, 0.03)"
16. Matrix [w]x: 0.000000, −0.029302, −0.003507 / 0.029302, 0.000000, −0.999564 / 0.003507, 0.999564, 0.000000 -> 0.00, −0.03, 0.00 / 0.03, 0.00, −1.00 / 0.00, 1.00, 0.00
17. Matrix [w]x²: −0.000871, −0.003506, 0.029290 / −0.003506, −0.999988, −0.000103 / 0.029290, −0.000103, −0.999141 -> 0.00, 0.00, 0.03 / 0.00, −1.00, 0.00 / 0.03, 0.00, −1.00
18. "the sine, 0.0401, and one minus the cosine, 1.9992" -> "the sine, 0.04, and one minus the cosine, 2.00"
19. Display "R = I + 0.0401 [w]x + 1.9992 [w]x² = (six-decimal matrix)" -> "R = I + 0.04 [w]x + 2.00 [w]x² = 1.00, −0.01, 0.06 / −0.01, −1.00, −0.04 / 0.06, 0.04, −1.00"
20. "(0.058, -0.040, -0.997)" -> "(0.06, −0.04, −1.00)"

## Appendix F

21. "Section 2.5 gives the two stages ahead of the smoothers: the rolling Hampel test, whose robust standard deviation is the median absolute deviation of the window scaled by the usual factor of 1.4826 [53], [54], and the linear interpolation of gaps up to 5 frames." -> "Section 2.5 gives the two stages ahead of the smoothers. The first is the rolling Hampel test, whose robust standard deviation is the median absolute deviation of the window scaled by the usual factor of about 1.48 [53], [54]. The second is the linear interpolation of gaps up to 5 frames."

## Parts checked and unchanged

Chapters 1, 3, 7, 8, 9 and the front matter carried no number with
three or more decimals before this round (check_style.py, decimals
check, 0 hits).

Addendum 2026-09-08 (D-020, found in code review): Chapter 7 Section 7.3, the rail level above the desk level of the parked marker origin: 3.9 -> 4.0 cm (r6b_rail_eval.json 0.0743 - 0.0346 = 0.0397 m; the 3.9 was the difference of the two rounded levels 7.4 and 3.5).
