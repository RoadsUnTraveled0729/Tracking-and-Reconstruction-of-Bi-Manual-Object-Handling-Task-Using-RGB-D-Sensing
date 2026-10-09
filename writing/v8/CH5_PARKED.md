# Parked Chapter 5 material (V7 to V8)

Sentences, equations and figures removed from Chapter 5 in the V8 rewrite
(2026-09-06, supervisor round 4 and the user's plan: the torso is assumed
measured on every frame, so the torso repair leaves the chapter; decision D1
of writing/v8/PROF_COMMENTS_ROUND4.md). Nothing here is deleted from the
repository: each item is kept verbatim as the source item of
writing/v7/scripts/build_ch5.py (commit b59af8e) so it can return if the
decision is reversed. Chapters 7 and 9 still refer to this material in
writing/v7 and are updated when they enter V8.

## Section 5.5 Torso Repair on Camera Rays (whole section, V7 equations 5.12-5.23, V7 Figure 5.4)

```python
(H2, "5.5 Torso Repair on Camera Rays"),
```

```python
(P, "Section 5.3 showed that the object cannot fix a torso, but the torso corruption has a shape of its own that supplies the missing anchor. It is the silent failure of Section 5.1: the landmark detector finds the hip and the shoulder pixels correctly even while a hand, the carried cube, or the desk in front of the person sits between the camera and the trunk, and the depth sample behind the correct pixel is the part that fails. This section states that failure as a model, derives the repair it permits, sets out the three gates that decide when the repair runs, and closes with what the repair cannot do."),
```

```python
(H3, "5.5.1 The Failure Model"),
```

```python
(PM, [T("Appendix D lifts a landmark from its pixel (u, v) and the depth sample d behind that pixel through the inverse of the colour intrinsics K,")]),
```

```python
(EQ, r("p") + r(" = ") + r("d") + r(" ") + sup(r("K"), r("−1")) + r(" ") + sup(d(r("u, v, 1")), r("T")), "5.12"),
```

```python
(PM, [T("so that the third coordinate of "), X(r("p")), T(" is the depth d itself. The two factors of equation (5.12) come from different sensors and fail independently. The pixel comes from the landmark detector, which reads the colour image and infers the hip from the outline of the body even when the hip itself is hidden. The depth comes from the depth image at that pixel, which reports the nearest surface along that line of sight, whatever it is. When a hand, the cube or the desk edge occupies the pixel, the pixel stays right and d is the depth of the occluder. The corrupt point is therefore")]),
```

```python
(EQ, sup(r("p"), r("′")) + r(" = ") + frac(sup(r("d"), r("′")), r("d")) + r(" ") + r("p"), "5.13"),
```

```python
(PM, [T("a scaling of the true point along the ray from the camera origin through it, with "), X(sup(r("d"), r("′"))), T(" smaller than d for a surface in front of the body. Nothing else about the point moves. This is the whole content of the model, and it also explains why a confidence score cannot see the failure: the detector's confidence describes the pixel, and the pixel is correct.")]),
```

```python
(PM, [T("The effect on the root frame is not small. Section 3.2 builds the trunk from the hip midpoint h and the shoulder midpoint s, and the pitch of the root frame is set by the direction of s − h. A depth error "), X(r("δ")), T(" common to both hips, taken positive toward the camera, leaves the shoulders where they are and moves the hip midpoint by "), X(r("δ")), T(" along the depth axis, so a trunk of height "), X(sub(r("L"), nor("t"))), T(" that stood upright is read as pitched by")]),
```

```python
(EQ, nor("arctan") + r(" ") + d(frac(r("δ"), sub(r("L"), nor("t")))), "5.14"),
```

```python
(PM, [T("toward the camera. A hip depth sample taken on a desk edge a few tens of centimetres in front of the pelvis, on a trunk half a metre long, produces a pitch of tens of degrees on a participant who is standing straight. The worked example of Chapter 3 shows exactly this on its frame, and the arm angles of that frame are read against the pitched root. Any arm angle that leaves the layer inherits the error of the frame it is expressed in, so the torso is repaired first.")]),
```

```python
(H3, "5.5.2 The Ray Repair and the Depth Memory"),
```

```python
(PM, [T("The model says which part of the measurement to keep. Every point with the pixel (u, v) lies on one ray through the camera origin, with direction "),
      X(frac(r("p"), p_z)), T(", where "), X(p_z),
      T(" is the depth coordinate of the point. Scaling the point by any positive factor leaves its pixel unchanged, because the projection u = f x / z + c divides x by z and the factor cancels; the same holds for v. The flip of equation (3.1) touches only the vertical axis, so the depth coordinate and the ray are the same in camera coordinates and in person space. The repair therefore keeps the ray and replaces only the depth: sliding the point along its ray until its depth equals a chosen value z* gives")]),
```

```python
(EQ, sub(r("p"), nor("fixed")) + r(" = ") + frac(sup(r("z"), r("*")), p_z) + r(" ") + r("p"), "5.15"),
```

```python
(PM, [T("which is the unique point with the measured pixel and the depth z*. The construction needs a positive measured depth, and a landmark whose depth sample places it at the camera is left missing. Equation (5.15) undoes equation (5.13) exactly when z* equals the true depth d, so everything below is about choosing z* and about deciding on which frames the substitution is made at all. The three gates of Sections 5.5.3 to 5.5.5 make that decision, and each supplies its own z*.")]),
```

```python
(PM, [T("The first two gates draw z* from a depth memory. For each torso landmark the layer keeps "), X(z_mem),
      T(", the running average of that landmark's own depth,")]),
```

```python
(EQ, sub(r("z"), nor("mem,") + r("k")) + r(" = ") + r("(1 − α) ") + sub(r("z"), nor("mem,") + r("k−1")) + r(" + α ") + sub(r("p"), r("z,k")), "5.16"),
```

```python
(PM, [T("with the same gain α = 0.30 as the direction memories of equation (5.4), seeded with the first measured depth and updated only on frames where the landmark was measured and not gated. How the repair behaves follows from two properties of this memory. It is not updated from repaired values, so once a gate closes on a landmark the memory freezes at the last depth the gate accepted, and the repair holds the landmark at that depth for as long as the gate stays closed. Nor does the staleness limit of Section 5.2 apply to it: a standing trunk keeps its depth for the length of a take, while a limb direction does not, so the depth memory has no horizon. The repair keeps the part of the measurement that survived, the pixel, and replaces the part that failed, the depth. Figure 5.4 draws it.")]),
```

```python
(IMG, FIG / "ch5_fig_torso.png", 6.3),
```

```python
(CAP, "Figure 5.4. (a) The torso repair, seen from above: the corrupt hip is pulled toward the camera along its ray, and sliding it back to its remembered depth restores the point and the hip line with it. (b) The depth-jump gate, drawn as a schematic illustration; Figure 7.9 shows what this gate does to the pelvis depth of the loop recording. While the measured depth stays inside a band about the remembered value the landmark is used as measured, and a departure beyond the band, here toward the camera, gates it into the repair. The shoulder-depth gate of Section 5.5.5 needs no panel: it is one threshold on the depth difference between a hip and the shoulder midpoint."),
```

```python
(H3, "5.5.3 Gate One: Rigidity of the Torso"),
```

```python
(PM, [T("The first gate applies the rigidity of the trunk inside the solve, in two tests, the width test and the line-consistency check. Both blame an endpoint by lengths calibrated per recording: the widths of the two pairs, hip to hip and shoulder to shoulder, and the four torso diagonals from each landmark to the midpoint of the opposite pair, each taken as the median over the first sixty frames on which both endpoints are measured. Until those sixty frames have been collected there is no calibrated length to blame an endpoint against, so neither test can gate a landmark, and over the opening of a take the torso is protected by the two gates below alone. Where the lengths are already known from an earlier calibration they are supplied instead, and the gate is live from the first frame.")]),
```

```python
(PM, [T("Under the width test a pair whose measured width departs from its calibrated value by more than 30 percent is suspect. The test is on each width against its own median, not on the shoulder-to-hip ratio the detector of Table 5.1 watches, so the two carry different tolerances. Each endpoint of a suspect pair is then checked by its diagonal, the distance from the endpoint to the midpoint of the other pair, against the calibrated diagonal with the same 30 percent tolerance. Where exactly one endpoint fails its diagonal, that endpoint is gated and repaired on its ray. Where both fail or neither does, the width test alone cannot say which point moved, and the layer keeps both rather than guess. The line-consistency check can still take the pair, but only if the same corruption has also turned one of the two lines.")]),
```

```python
(PM, [T("The line-consistency check is the rigidity statement of the torso line-angle detector. With the hip line "), X(r("h")), T(" from the left hip to the right hip and the shoulder line "), X(r("s")), T(" from the left shoulder to the right shoulder, the disagreement between the two lines is")]),
```

```python
(EQ, r("θ") + r(" = ") + nor("arccos") + r(" ") + d(frac(r("h · s"), nrm(r("h")) + r(" ") + nrm(r("s")))), "5.17"),
```

```python
(PM, [T("Where the two lines disagree by more than 20 degrees, one of them is corrupt, because a rigid trunk keeps them near parallel. The detector of Table 5.1 uses 22 degrees; both figures sit above the largest disagreement the clean frames of the reference recording show, 18.9 degrees. The corrupt line is the one whose direction has moved further from its own direction memory. With the two deviations")]),
```

```python
(EQ, sub(r("Δ"), r("h")) + r(" = ") + nor("arccos") + r(" ") + d(hat(r("h")) + r(" · ") + sub(hat(r("h")), nor("mem")))
     + r(",      ") + sub(r("Δ"), r("s")) + r(" = ") + nor("arccos") + r(" ") + d(hat(r("s")) + r(" · ") + sub(hat(r("s")), nor("mem"))), "5.18"),
```

```python
(PM, [T("the corrupt line is the one with the larger deviation, since corruption pulls one line away from its history while a real turn of the body moves both lines together and never opens a disagreement. The check needs both direction memories and cannot trip before they exist. The comparison is made once, on the frame the gate trips, and the line it blames stays the blamed line until the gate releases. Each endpoint of the corrupt line is then checked by its diagonal as above. Where exactly one endpoint fails, only that endpoint is gated. Otherwise the whole line is gated, and both endpoints are placed on their rays at their remembered depths by the pair rebuild of Section 5.5.6.")]),
```

```python
(PM, [T("The gate has hysteresis: it trips above 20 degrees and releases only when the disagreement falls back under 10 degrees, so a corruption that settles just under 20 degrees does not release the constraint on the frame after it started. While the whole line is gated its direction memory is also mixed each frame with the direction of the surviving line, so a real turn of the trunk still reaches the gated pair.")]),
```

```python
(H3, "5.5.4 Gate Two: Depth Jump"),
```

```python
(PM, [T("The first gate cannot see one kind of corruption. Corruption that takes both endpoints of one line together, a hand across the whole pelvis or a desk edge under both hips, scales the two endpoints by nearly the same factor, so that line keeps its direction and goes on agreeing with the other. A test built on their disagreement cannot see it. The width test misses it as well: a common scaling shrinks the pair's measured width in proportion to the depth, and an occluder a few tens of centimetres in front of the trunk moves it by less than the 30 percent that test allows. Such a landmark gives itself away in depth instead. Its measured depth is compared with its memory,")]),
```

```python
(EQ, nrm(sub(r("p"), r("z,k")) + r(" − ") + sub(r("z"), nor("mem,") + r("k−1"))) + r(" > 0.10 m"), "5.19"),
```

```python
(PM, [T("and a departure beyond 10 centimetres gates the landmark into the ray repair of equation (5.15) with z* set to the remembered depth. The band is read against the running average rather than against the previous frame. At thirty frames per second a landmark that leaves its own average by 10 centimetres has moved at 3 metres per second or has stopped being the landmark, and no torso in a desk task does the first. The clean frames of the reference recording deviate from their memory by a few centimetres at most. When both landmarks of a pair are gated on the same frame and the pair's width and direction memory are already calibrated, the pair rebuild of Section 5.5.6 repairs them together. A single gated landmark, and either landmark of a pair before that calibration completes, is repaired on its own ray.")]),
```

```python
(H3, "5.5.5 Gate Three: Shoulder Depth"),
```

```python
(PM, [T("The first two gates compare a measurement with its own history, so a hip whose depth is wrong from the very first frame passes both: the memory it is compared against was seeded from the same wrong depth, by equation (5.16), and nothing ever jumps. A surface that stays in front of the pelvis can produce that. In the recording of Chapter 2 the rail on the desk sits between the camera and the pelvis for almost the whole task. The depth sample behind each hip pixel lands on the rail, at least 20 centimetres nearer the camera than the shoulders for as long as both hips read it. The hips are measured on the body only at the opening of the take, before the participant settles over the desk, and again over the closing frames Section 7.4 describes. A take that began one second later would carry the wrong depth from its first frame. The third gate covers that case with a comparison that needs no history. It compares each hip with the shoulder midpoint "), X(sub(r("s"), nor("mid"))), T(" of the same frame:")]),
```

```python
(EQ, sub(r("p"), nor("z,hip")) + r(" − ") + sub(r("s"), nor("mid,z")) + r(" < −0.15 m"), "5.20"),
```

```python
(PM, [T("A hip that satisfies equation (5.20) is gated, and the repair places it on its ray at the depth of the shoulder midpoint, z* = "), X(sub(r("s"), nor("mid,z"))), T(", the depth an upright trunk gives it. The midpoint is the one the shoulders measure at the top of the frame, before any gate has run, so the gate reads the trunk as the sensor reported it. It is evaluated only when both shoulders are reported, and it is tested only on a hip the first two gates have left in place. Intersecting the hip's ray with a sphere of the calibrated diagonal about the shoulder midpoint would fix the depth without reference to a lean, and it is not used here. The diagonal is nearly vertical and the ray nearly horizontal, so the sphere meets the ray almost tangentially, and the depth the intersection returns swings by tens of centimetres under a centimetre of noise.")]),
```

```python
(PM, [T("The tolerance follows from the geometry of a lean. Here the trunk turns about the hip and keeps its own length, so the angle is measured from the vertical of an upright trunk rather than by the small-offset form of equation (5.14). A trunk of length "), X(sub(r("L"), nor("t"))), T(" leaning by an angle "), X(r("φ")), T(" in the depth direction separates the hip depth from the shoulder depth by")]),
```

```python
(EQ, r("Δz") + r(" = ") + sub(r("L"), nor("t")) + r(" sin ") + r("φ"), "5.21"),
```

```python
(PM, [T("so with the participant's trunk length of about 0.48 metres, the value Section 6.3 quotes, the 15 centimetre threshold corresponds to a trunk leaning 18 degrees back from the camera, which a participant working over a desk does not produce. On the clean torso frames of the loop recording, where the hips are measured on the body, the hip-to-shoulder depth difference stays inside 10 centimetres either way over all but the extreme percentile, a lean of 12 degrees. The rail puts the corrupt hips at least 20 centimetres nearer. The threshold sits between the two. The sensor's optical axis is close to horizontal, its tilt being part of the scene calibration of Chapter 4, so an upright trunk puts the two depths within a few centimetres of each other and equation (5.20) reads the lean almost directly.")]),
```

```python
(PM, [T("Two consequences of the placement should be stated plainly. The repaired hip sits where an upright trunk would put it, so any real lean the participant has is lost on the frames this gate carries. That is the price of a comparison without history, and it is no larger than the lean the loop recording shows, about 10 centimetres. The precedence between the gates then decides which depth a hip receives when more than one would fire. Because the shoulder-depth gate is tested only on hips the first two gates passed, once a hip's measured depth has left a memory seeded on the body the depth-jump gate settles the repair at the remembered depth, and the shoulder depth is not used. Only while that memory still matches the measurement can the shoulder comparison decide anything, and that is the case of a take that begins with the pelvis already occluded.")]),
```

```python
(H3, "5.5.6 Rebuilding the Pair"),
```

```python
(PM, [T("A landmark the shoulder-depth gate takes is placed by equation (5.15) and nothing else, whether one hip or both. A single landmark the first two gates take is placed by equation (5.15) as well; where it has no depth memory to place it at, it is left missing and is rebuilt from its partner by the rule at the end of this section. Behind the rebuild of a pair the first two gates take together, both hips or both shoulders, are two sources of different reliability, and position and orientation are taken from different ones. Let "), X(sub(r("q"), r("a"))), T(" and "), X(sub(r("q"), r("b"))), T(" be the two endpoints after each has been slid to its remembered depth. The position of the pair is their midpoint,")]),
```

```python
(EQ, r("m") + r(" = ") + frac(r("1"), r("2")) + r(" ") + d(sub(r("q"), r("a")) + r(" + ") + sub(r("q"), r("b"))), "5.22"),
```

```python
(PM, [T("and taking the midpoint of two ray-repaired points stops the depth of the pelvis from wandering. The orientation comes from the pair's direction memory "), X(sub(hat(r("u")), nor("pair"))), T(", updated by the rule of equation (5.4) with the direction from "), X(sub(r("q"), r("a"))), T(" to "), X(sub(r("q"), r("b"))), T(". Raw per-frame ray directions carry the sideways wobble of the pixels while a hand crosses the trunk; the memory attenuates that wobble while still following a real turn. The two landmarks are then placed symmetrically about the midpoint at the calibrated width w of the pair,")]),
```

```python
(EQ, sub(r("p"), r("a")) + r(" = ") + r("m") + r(" − ") + frac(r("w"), r("2")) + r(" ") + sub(hat(r("u")), nor("pair"))
     + r(",      ") + sub(r("p"), r("b")) + r(" = ") + r("m") + r(" + ") + frac(r("w"), r("2")) + r(" ") + sub(hat(r("u")), nor("pair")), "5.23"),
```

```python
(PM, [T("That width is the physical separation of the pair, which the pose of the trunk does not change. Its projection into the image does change, so a single repaired landmark is not pushed to the calibrated width against a measured partner, and rigidity is used there as a test and not as a construction. Before the depth memories exist, in the first frames of a take, the pair is rebuilt about its measured midpoint along the direction memory instead. When neither a ray nor a depth memory is available, the torso frame holds its last value.")]),
```

```python
(P, "The same pair mechanism serves the case where a torso landmark is missing rather than corrupt. A missing hip is placed at the calibrated hip width from the other hip, along the direction memory of the hip line, and a missing shoulder likewise. Here the staleness limit of Section 5.2 does apply, because a missing landmark is rebuilt from its neighbour by the recovery rule of that section and inherits the horizon that comes with it. The rebuild of a gated pair above is this section's own and carries no horizon, since the depth memory it rests on has none. Rebuilding the shoulder matters beyond the torso, because the shoulder is where each arm chain is anchored: a shoulder that is restored keeps that arm solving instead of freezing it. The root frame of Section 3.2 is then built from the repaired points exactly as from measured ones, and the arm angles are read against it."),
```

```python
(H3, "5.5.7 What the Repair Cannot Do"),
```

```python
(P, "The repair rests on the failure model of Section 5.5.1, and it reaches exactly as far as that model holds. It corrects a right pixel over a wrong depth. It does nothing for a wrong pixel: a landmark the detector places on the occluder itself, or a hip it invents on the far side of a desk, keeps a wrong ray, and sliding along a wrong ray cannot recover the point. The first gate may still catch such a landmark through the width or the diagonal it breaks, but the repair that follows is then a repair along the wrong line. A shoulder pair whose own depths are wrong carries the hips to the same wrong depth through the third gate. Chapter 7 measures that case on the loop recording, against manually labelled landmarks."),
```

```python
(P, "The first two gates depend on a memory that was seeded correctly, and the memory is frozen for as long as the gate stays closed. A participant who steps back while both hips are gated is held at the depth the take began with, and nothing in the layer notices, because the frozen memory is exactly what the repair trusts. The calibration of Section 5.5.3 is open to the same steady offset. The pair widths are taken from the measurement as it arrives, so a take whose opening frames are already occluded calibrates its widths on the occluder, and the rebuild of equation (5.23) then holds the pair at a width learned from the wrong depth. The third gate has no memory to freeze, and pays for it by losing the lean. Chapter 7 reports how each gate behaved on the two recordings, and Chapter 9 states the cases that remain untested."),
```

## The reach inequality (V7 Section 5.3, equation 5.6)

```python
(PM, [T("The object cannot do more than this. Equation (5.1) ties the object to one point of the body, and one point does not determine a pose. For the shoulder, the wrist estimate says only that the arm must be able to reach it,")]),
```

```python
(EQ, nrm(r("w") + MINUS + p_sh) + r(" ≤ ") + L1 + r(" + ") + L2, "5.6"),
```

```python
(PM, [T("with "), X(L1), T(" and "), X(L2),
      T(" the calibrated upper-arm and forearm lengths. That is one scalar inequality against the six degrees of freedom of the torso. It can reject a torso hypothesis and it can never produce one, so a corrupt torso needs a different anchor, developed in Section 5.5.")]),
```

## Torso-repair sentences elsewhere in V7 Chapter 5

- Chapter opening: "taking the tracked object of Chapter 4 as the anchor for a hand that holds it and the camera geometry as the anchor for a corrupt torso point"; "Section 5.5 repairs a corrupt torso landmark on its camera ray."
- V7 Section 5.2 direction-memory paragraph: "Only the memory of a torso pair takes more than measurements, since the repair of Section 5.5 also steers it with the surviving line and with the direction between two repaired points."
- V7 Section 5.6: "a torso point from its camera ray by equation (5.15)" in the constrained-state list; "The root is exempt from the limiter, because the torso gates of Section 5.5 already govern it."
- V7 Figure 5.5 rebuild box: "torso landmark on its ray at the remembered depth", "shoulder or hip from its partner across the pair".

## Where the parked material is still referenced (writing/v7, to update when those chapters enter V8)

- Chapter 7 Section 7.4 (torso stability: Figure 7.9, Table 7.8, the rail trunk-pitch paragraphs, the synthetic-corruption check) and Section 7.3 ("the rule keeps the detectors quiet on the torso").
- Chapter 8 Table 8.1 row "Torso repair along camera rays, with the depth-jump test".
- Chapter 9: the desk-edge paragraph, the repair-cost paragraph, the limitation row on the hip depth, the loop-window paragraph.
- Chapter 3 Section 3.5: the worked frame's pitched root (hips at the rail's depth) is now a stated limitation, not a repaired case (decision D2 open).
- GLOSSARY.md keeps the torso-repair entries (depth memory, depth-jump gate, shoulder-depth gate, ray repair, width test, torso diagonal, pair rebuild, occluder, hysteresis, torso repair) for Chapters 7 and 9 until those are rewritten.
