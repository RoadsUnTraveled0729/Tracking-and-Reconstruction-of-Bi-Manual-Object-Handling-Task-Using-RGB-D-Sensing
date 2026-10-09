# Chapter 7 restructure: thesis-wide integration fix list

Read-only audit, 2026-09-12. Scope: every reference in the condensed V8
builders (Chapters 1-10, front matter, appendices, assembly tooling) that
still describes the **pre-D-029 Chapter 7** and is now wrong.

Nothing in this file has been applied. No builder, .docx, figure or
DECISIONS.md was modified.

---

## 1. What Chapter 7 now contains (source of truth: scripts/build_ch7.py)

Sections
- 7.1 Evaluation Method
- 7.2 Object Reconstruction Accuracy -> 7.2.1 Single-Hand Rail Task, 7.2.2 Handover Task
- 7.3 Human Reconstruction Accuracy under Valid Landmark Measurements -> 7.3.1 Single-Hand Rail Task, 7.3.2 Handover Task
- 7.4 Reconstruction during Landmark Failure -> 7.4.1 Synthetic Landmark Removal, 7.4.2 Natural Occlusion

There is **no Section 7.5**, no 7.6, no 7.7, no 7.8, no 7.3.3.

Figures: **7.1, 7.2 only** (ch7_valid_joints_r6b.png, ch7_valid_joints_r7.png).
Old Figures 7.3 - 7.15 no longer exist.

Tables: **7.1 - 7.7**, all with new meanings:
| new | content |
|---|---|
| 7.1 | Single-hand rendered elbow/wrist error vs measured landmarks (right arm, n=100) |
| 7.2 | Handover rendered elbow/wrist error vs measured landmarks, per arm (n=650 / 589) |
| 7.3 | Synthetic removal window selection (handover recording, 3 windows x 45 frames) |
| 7.4 | Synthetic elbow error by window and method |
| 7.5 | Synthetic wrist error by window and method |
| 7.6 | Clean-frame proxy-to-measured-wrist distance (loop, bracelet/watch) |
| 7.7 | Natural-occlusion reconstructed wrist to manual proxy, per arm and method |

Equations 7.1 - 7.6 (all new; none is cited from outside Chapter 7).

Old numbering, for decoding stale references:
old 7.1 Evaluation Framework and References / 7.2 Object Reconstruction /
7.3 Human-Object Reconstruction and Handover / 7.4 Landmark Failure and
Wrist Recovery / 7.5 Kinematic Solver Verification; old Tables 7.1 handover
tracking scatter, 7.2 synthetic-mask wrist deviations, 7.3 label-vs-wrist on
failure frames, 7.4 the same on clean frames, 7.5 the six synthetic solver
datasets.

---

## 2. Summary: counts by severity

| severity | count | meaning |
|---|---|---|
| **Broken reference** | **1** | printed prose points at a section/figure/table that no longer exists; the checker catches it |
| **Silently-wrong reference** | **36** | printed prose still resolves, but the target now holds different content (or contradicts the sentence). The checker cannot catch any of these. |
| **Stale claim** | **6** | prose summarizing Chapter 7 with no section number, describing results that were removed or changed |
| Non-printed / tooling | 9 groups | stale source comments and docstrings, one build_thesis.py help string, and the front matter's auto-generated lists |

Project checker (`cd writing/v8/condensed/scripts && python check_refs.py`), exact output:

```
defined: figures 43, tables 24, equations 51, sections 70, appendices ['A', 'B', 'C', 'D', 'E', 'F', 'G']
references checked: 551
UNRESOLVED (1):
  Chapter_3_Kinematic_Modeling: sec 7.5  <- The same equations run on every frame and on both arms. The chapter ha
never referenced eq: ['3.15', '3.16', '3.18', '3.19', '4.3', '6.3', '7.1', '7.2', '7.3', '7.4', '7.5', '7.6']
```

Exit status 1. It reports **one** problem. That is the point of this
document: 36 further references still resolve and are therefore invisible
to the checker.

### Most dangerous items (silently wrong and numerically contradicted)

1. `build_ch9.py:222` - "The worst frames of **Table 7.2**" now sends the
   reader to the handover rendered-joint-error table instead of the
   synthetic-mask deviation table.
2. `build_ch9.py:150` - claims Section 7.3 shows the model wrist "about a
   centimetre from the measured wrist on both arms of the handover
   recording". Section 7.3's Table 7.2 now prints 5.7 cm and 6.9 cm.
3. `build_ch9.py:227` and `build_ch9.py:346` - describe Section 7.4.1 as
   five slow windows on the **rail** recording with 342 eligible frames.
   Section 7.4.1 is now three windows on the **handover** recording and
   states in terms that the single-hand recording provides no such window.
4. `build_ch10.py:81` - "The synthetic masking of Section 7.4.1 adds only
   slow windows, where a held angle is nearly right." Section 7.4.1 now
   reports a window-dependent comparison over low/intermediate/high motion.
5. `build_ch10.py:72` and `build_ch9.py:140` - the wrist-to-marker physical
   reference cited to Section 7.3, which no longer contains any
   wrist-to-marker quantity. This sentence carries Chapter 10's answer to
   the central question of Chapter 1.

---

## 3. Fix list by builder

Severity codes: **[B]** broken, **[S]** silently wrong, **[C]** stale claim,
**[N]** non-printed (comment/docstring/tooling).
Fix codes: **(mech)** mechanical number/name change, **(judg)** needs an
author or writer decision about what the thesis now claims.

---

### scripts/build_ch3.py

**3-1 [B] line 555** (mech + judg)
> "The same equations run on every frame and on both arms. ... **Section 7.5 verifies that mathematics against synthetic exact references.** The solve needs every landmark of its chain measured on the frame, ..."

Wrong: Section 7.5 does not exist. Solver verification was removed
entirely under D-029, together with old Table 7.5 (the six synthetic
datasets). There is now **no** place in the thesis where the kinematic
solver is verified against an exact reference.
Fix: the number cannot simply be repointed - nothing in the new Chapter 7
does this. Author decision needed between (a) deleting the sentence and
closing the paragraph on "the wrist still a point"; (b) moving the six
synthetic datasets into an appendix and pointing there; (c) reinstating a
solver-verification subsection. The sentence is the *only* printed
dangling reference in the thesis, so whichever option is chosen also
clears check_refs.

---

### scripts/build_ch4.py

**4-1 [S] line 233** (judg)
> "... and **Chapter 7 reports the physically measured route and describes the reconstructed track against a line fitted to its own slide samples (Section 7.2).**"

Wrong on both halves. Section 7.2 now defines endpoint-length error and
PCA line fitting but prints **no numbers**: 7.2.1 and 7.2.2 are
"Data Required" paragraphs, and 7.2.1 states that segment-length errors
"cannot be calculated from that construction". The route is not reported,
and no fitted-line scatter value is printed.
Fix: coordinate with the in-flight Section 7.2 work (D-035 supplies the
tape lengths 25.5 / 3.5 / 37.5 cm and the marker-centre endpoint rule).
Either defer the promise ("Chapter 7 evaluates the object track against
the physically measured route, Section 7.2") or restate once 7.2 is
populated. Do not leave a promise of a reported route while 7.2 is blocked.

**4-2 [N] lines 56, 59-60, 65** (mech)
Docstring bullets assert "the chapter prints no marker size at all and
Section 7.1 states it" and "the physical route ... reported in Section
7.2". New Section 7.1 states no marker size. Update the docstring when
4-1 is fixed, and see 9-4 which is the printed instance of the same error.

---

### scripts/build_ch5.py

No printed fix required. Verified correct against the new chapter:
- line 252: "(Section 7.4.1)" for the unmasked-solve comparison and
  "(Section 7.4.2)" for manual wrist labels - both still point at the right
  content.
- line 306: "Section 7.4.2 reports what they cost on the natural failure
  windows" - still 7.4.2, still the natural-occlusion set.
- line 536: "Section 7.4 grades it, against the unmasked solve under
  synthetic masking and against the manual wrist labels" - still correct.

**5-1 [N] lines 75-83** (mech, optional)
Docstring records the repointing "the two old Section 7.8 references become
Section 7.4.2"; it now describes a superseded revision. Wording only.

**5-2 [C] line 252** (mech, cosmetic)
"manually labelled wrist positions" - Section 7.4.2 now calls these
"manual wrist proxies" (bead bracelet / watch) and is explicit that they
are not the wrist the landmark defines. Aligning the vocabulary across
Chapters 5, 8, 9 and 10 is worth one pass.

---

### scripts/build_ch6.py

**6-1 [S] line 337 (figure caption)** (judg)
> "Figure 6.{F_SCENE}. The reconstruction as Unity draws it ... (b) Frame 700, during the slide. **Section 7.1 describes the task and its phases.**"

Wrong: the new Section 7.1 (Evaluation Method) names the three recordings
and the error definitions. It contains no task protocol, no phases, and
old Figure 7.1 (the four-step protocol drawing) and old Figure 7.2 (the
colour frame strip) are gone. The waypoint route W1-W4 is now described in
Section 7.2, and the phases are described nowhere.
Fix: repoint to Section 2.x (Chapter 2 describes the rail setup and the
task) or to Section 7.2 for the waypoint roles - author's choice, because
Chapter 2's description is of the rail recording only.

**6-2 [S] line 327** (judg)
> "... **Section 7.4.1 measures on synthetic windows what a nearly straight arm costs the recovery.** On frame 700 the elbow is bent by 31.0 degrees, ..."

Wrong: Section 7.4.1 no longer characterizes arm straightness at all. The
old subsection reported "the wrist at 99 to 100 percent of the combined
upper-arm and forearm length and the elbow bent by 14 to 17 degrees"; the
new one selects windows by **reference wrist excursion** (0.6, 2.8,
5.1 cm) on the **handover** recording. Nothing there measures the cost of a
nearly straight arm.
Fix: delete the sentence, or replace it with what 7.4.1 does show (a
window-dependent comparison at three motion magnitudes). The nearly
straight arm / held twist mechanism survives only in Section 5.5 and
Section 9.3.

**6-3 [S] line 301** (mech)
> "Each is the median of that segment over the whole landmark track of the loop recording **(Section 7.1)**."

Weakened, not fully broken: the new 7.1 does name "the loop recording for
natural occlusion" but no longer describes it (old 7.1 gave 2099 frames,
about 70 s, the two-hand loop with two passes). A reader following the
pointer learns nothing about the recording.
Fix: either drop the cross-reference or point at Section 7.4.2, which is
where the loop recording is actually used.

**6-4 [C] line 440** (judg)
> "**Chapter 7 evaluates the reconstruction offline against physical, manual and synthetic references** and against within-recording comparisons, and Chapter 8 asks whether the same architecture runs causally."

"physical references" is currently unsupported - the object physical
comparison is the blocked Section 7.2. "synthetic references" now means
the unmasked reconstruction used by 7.4.1, not the synthetic exact
references of the removed solver verification. See 1-1 for the same
sentence in Chapter 1, which is worse.
Fix: hold until Section 7.2 is populated, then restate. Mechanical once
the author settles what Chapter 7 claims.

**6-5 [N] lines 112-114** (mech)
Docstring says "Cross-references repointed to the new Chapter 7 structure:
the nearly straight arm is Section 7.4.1 (was 7.8), the loop recording is
Section 7.1, the task phases are Section 7.1" - all three are now the
defects 6-1, 6-2, 6-3. Rewrite with the fix.

---

### scripts/build_ch8.py

**8-1 [C] line 133** (judg)
> "... **Chapter 7 grades the offline pass against physical, manual and synthetic references**, and against its own outputs where no independent reference exists; this section measures the distance between the two processing paths."

Same problem as 6-4: no physical object result is currently printed, and
"synthetic references" changed meaning. The "(Section 7.4)" pointer later
in the same paragraph ("the recovery solve of Section 7.4") is still
correct.
Fix: restate once 7.2 is populated; mechanical thereafter.

**8-2 [C] line 217** (mech, cosmetic)
> "The comparison against the unmasked solve, the synthetic masking of Section 7.4.1 and the manual labels of Section 7.4.2 all read a finished recording ..."

Both numbers resolve correctly. Only the vocabulary is stale: 7.4.1 is
"synthetic landmark removal" and 7.4.2's references are "manual wrist
proxies". See 5-2.

**8-3 [N] line 107** (mech)
Source comment "nothing registers the route into the world frame (Chapter
7 Section ...)" - refresh with the D-035 outcome.

---

### scripts/build_ch9.py

Chapter 9 is by far the worst affected: **27 silently-wrong printed
references**. Section 9.1 and Section 9.2 in particular recite Chapter 7
numbers that the rebuilt chapter no longer prints anywhere in the thesis.

#### 9.1 Object Reconstruction and Physical-Route Error Sources

**9-1 [S] line 85** (judg)
> "The object slides along a straight guide, so its output can be set against a line fitted to its own samples, and **Section 7.2 reports the spread of the marker origin about that line for each slide** as a within-recording comparison."

Section 7.2 defines the PCA fit (equations 7.2-7.4) but reports no spread.
The old values (rail median 1.0, p95 2.4, max 3.1 cm; handover 0.3, 1.6,
3.4 cm) are printed nowhere in the thesis now.
Fix: blocked on the Section 7.2 work in flight. Hold the sentence until
7.2 prints scatter, or drop the pointer.

**9-2 [S] line 92** (judg)
> "**The physically measured route is not registered into the calibrated world frame (Section 7.2)**, so no distance from the reconstructed track to the physical path is available."

Section 7.2 makes no such statement. Under D-035 the situation has also
changed: the marker centre is now the agreed physical and reconstructed
endpoint, so endpoint *lengths* are obtainable without a registered route.
Fix: author judgement - the claim itself may need rewriting, not just the
number.

**9-3 [S] line 106, first clause** (judg)
> "The two modes of the tracked height histogram put **the reconstructed rail level 0.2 and 0.6 centimetres above the 3.8 centimetres of the tape** on the two recordings (Section 7.2), a coarse check of the reconstructed vertical scale."

These are dropped results. Neither the height-histogram cross-check nor the
3.97 / 4.43 cm rail heights appear in the rebuilt Chapter 7. Chapter 9 is
now the only place the numbers exist, which violates the chapter's own rule
that every number is printed in Chapters 2 to 8.

**9-4 [S] line 106, second clause** (mech)
> "**The desk and object markers are 45 millimetres and the pipeline uses that size (Section 7.1)**, while the depth reading implies a side of 43.4 to 43.8 millimetres."

Section 7.1 states no marker size. Table 2.1 (Chapter 2) does.
Fix: repoint to Table 2.1 / Section 2.x. Mechanical.

**9-5 [S] line 128** (judg)
> "The marker is present on 2058 of that recording's 2099 frames, and **the handover recording misses one frame of 1499 (Section 7.2)**."

Detection counts were dropped from Chapter 7. Note the same paragraph's
"(Section 7.4)" for where a wrong-pose decode would appear is still fine.
Fix: either restore the counts to Section 7.2 or move them (they are a
Chapter 4 property as much as a Chapter 7 one).

#### 9.2 Human-Object Spatial Reconstruction

**9-6 [S] line 140** (judg) - HIGH
> "The physical distance from the MediaPipe wrist landmark location to the marker origin **was measured as about 16 centimetres for a normal single-hand grip (Section 7.3)**. ... The reconstructed median is 15.77 centimetres for the right hand alone and 14.08 for the left hand alone after the transfer. The transfer values, 17.91 and 15.85, ..."

Section 7.3 is now rendered-joint error against measured landmarks. It
contains no wrist-to-marker distance, no 16 cm reference and none of the
four medians. This paragraph is the whole of the thesis's only
physically-referenced human-object quantity (locked facts 4 and 5) and it
now cites a section that says nothing about it.
Fix: author decision. Either reinstate the wrist-to-marker comparison in
Chapter 7 or withdraw Section 9.2's opening claim and Chapter 10's use of
it (see 10-2).

**9-7 [S] line 150** (judg) - HIGH, numerically contradicted
> "**Section 7.3 adds two comparisons that describe the chain rather than its accuracy. The model wrist placed by the thirteen solved angles sits about a centimetre from the measured wrist on both arms of the handover recording**, so the chain reproduces the landmark it was given. On the rail recording the model wrist runs several centimetres above the line fitted to the slide, ..."

The new Section 7.3, Table 7.2, prints handover **wrist** medians of
5.7 cm (right) and 6.9 cm (left) against the measured landmarks. A reader
following the pointer finds a figure five to seven times the one Chapter 9
asserts. The two quantities are genuinely different - Chapter 9 means the
bare model wrist at the measured shoulder, Table 7.2 means the rendered
rig joint including display filtering and rig mapping - but the thesis
does not distinguish them at this point, and the 0.96 / 1.17 cm values are
no longer printed anywhere. The 6.5 cm wrist-to-rail-line median is also
gone.
Fix: author judgement. The distinction must be stated explicitly, or the
paragraph withdrawn.

**9-8 [S] line 165** (judg)
> "On the grasp and the lift of the rail recording the rendered Unity hand lands beside the cube, **15.2 and 12.1 centimetres from the measured wrist (Section 7.3)**."

Dropped. These came from old Figure 7.9 / old Section 7.3 and, per the
source comment at line 153, already had no surviving committed record
(decision G2). New Table 7.1 gives a single-hand wrist median of 12.0 cm
on a different frame set - close enough in magnitude to be mistaken for
the same quantity, which makes leaving it worse than removing it.

**9-9 [S] line 171** (judg)
> "Each recording calibrates its own pair, and the rail recording's 31.7 and 20.5 centimetres split about the same total very differently from the loop recording's 25.6 and 25.2, against about 25 centimetres for both segments measured on the subject **(Sections 6.3 and 7.3)**."

Section 7.3 no longer prints any segment length; the handover effective
lengths (24.1 / 23.3 right, 25.2 / 22.3 left) are gone.
Fix: drop "and 7.3"; Section 6.3 carries the rail and loop values. Largely
mechanical, but the handover pair loses its home.

#### 9.3 Landmark Failure and Object-Assisted Recovery

**9-10 [S] line 194** (judg)
> "**The object estimate itself is 13.2 centimetres from the label over those frames**, and no solve built on it does better than the held wrist (Section 7.4.2)."

The raw object-estimate column is not in the new Table 7.7, which lists only
plain / hold-last / object-assisted. Also verify the second half against the
new numbers: Table 7.7 left arm gives plain 12.3, hold-last 12.7,
object-assisted 13.1 cm - the *plain* solve now beats the held wrist.

**9-11 [S] line 199** (judg)
> "On frame 1462 the frozen offset places the wrist too close to the shoulder, and **the two-link solve bends the elbow by 64.4 degrees on a straight arm (Section 7.4.2)**."

Frame-level detail from the removed Figure 7.14. Section 7.4.2 now prints
only per-arm summary statistics; no frame is named.

**9-12 [S] line 205** (judg)
> "On frame 1890 of the loop recording the whole right arm is rejected. **The plain solve places the wrist 14.0 centimetres from the label ... the recovery places it at 5.0, and the object estimate itself is 15.2 centimetres off (Section 7.4.2).**"

Frame-level detail from the removed Figure 7.15. Section 7.4.2's right-arm
medians (plain 11.4, object-assisted 5.2, n=4) are close but not equal, so
the reader cannot reconcile the two.

**9-13 [S] line 222, first half** (judg)
> "**That frozen twist is why the recovery solve places the wrist 9.1 centimetres from the label on clean frames where the plain solve places it at 6.9 (Section 7.4.2).**"

These are the **rail** recording clean-frame values from old Table 7.4. Per
D-033 the rail label set is excluded from Section 7.4.2 entirely ("Rail
detector dropout does not establish physical occlusion and is omitted from
this subsection"). Section 7.4.2 is loop-only, and Table 7.6 gives clean
values of 4.5 cm (left) and 2.1 cm (right) for a different quantity.

**9-14 [S] line 222, second half** (mech) - MOST DANGEROUS
> "**The worst frames of Table 7.2 come from the same rules.** At the first masked frames of an outage the twist the rebuilt arm needs differs from the held one, and the rate limit of Section 5.5 walks it across at 15 degrees per frame."

Old Table 7.2 was the synthetic-mask wrist deviations. New Table 7.2 is
"Handover task: rendered joint error relative to accepted measured 3D
landmarks". The reference resolves, the checker passes it, and the reader
is sent to the wrong table.
Fix: repoint to Tables 7.4 and 7.5 (synthetic elbow / wrist error), then
re-verify the claim - the new tables' maxima are 1.0-3.0 cm (elbow) and
0.8-4.6 cm (wrist), so "worst frames" needs rechecking against the new
window set.

**9-15 [S] line 227** (judg) - HIGH, directly contradicted
> "The synthetic windows are the slow case. **The eligibility rule of Section 7.4.1 leaves five windows containing 3.0 to 6.0 degrees of arm travel**, so a held angle is nearly right in all of them, **and the rail recording holds no eligible outage during which the arm travels.**"

Section 7.4.1 is now: the **handover** recording, **three** windows of 45
frames selected by reference wrist excursion (0.6, 2.8, 5.1 cm), and it
states that "the single-hand recording does not provide a fully measured
root-and-arm reference window under these conditions". Every element of
this sentence is now false, and "the slow case" reading is contradicted by
Section 7.4.1's own conclusion ("a window-dependent comparison rather than
a general recovery ranking").

#### 9.4 Torso and Root Failure

**9-16 [S] line 250** (judg)
> "They fire from frame 632, where **the two hips read depths 19.4 centimetres apart against 0.8 on clean frames (Section 7.1)**."

The failure-coverage passage of old Section 7.1 is gone: 13.3 percent right
arm, 93.6 percent left, 31.3 percent torso, the 19.4 vs 0.8 cm hip split,
frames 550-639, 7-24, 674-684, and old Figure 7.3. None of this is in the
rebuilt chapter.

**9-17 [S] line 260** (judg)
> "**The left arm of the handover recording fails the same way after the release (Section 7.3).**"

The 63-frame left-arm rejection was an old Section 7.3 result. Section 7.3
now reports only accepted-frame counts (right 650, left 589) with no
rejection narrative.

**9-18 [S] line 273** (judg)
> "**The model wrist of the handover recording jumps by up to 23 centimetres between consecutive frames** at the three points where the hips enter and leave the repair of Section 2.6, frames 644 to 648, 892 to 894 and 1058 to 1061 **(Section 7.3)**."

Dropped result: the 23.24 cm FK wrist step trace and the 417 repaired
frames are no longer in Chapter 7. This paragraph is also load-bearing for
Chapter 10 (line 83: "which the wrist jumps of the handover recording
show").

**9-19 [S] line 282** (judg) - dropped result with downstream dependants
> "**Section 7.3 compares the preparation with a rule that holds the hips at their last accepted position** while a hand or the object covers them. Over the covered window of the handover recording the held hips are the steadier of the two on every measure it reports. ... On the rail recording, where the rail covers the hips from the fifth frame and the shoulders move 13.4 centimetres, the held root is the less steady of the two, spreading the yaw by 3.1 degrees against 2.3 and the pitch by 21.7 against 18.1."

The entire hip-hold comparison is gone from Chapter 7. Chapter 9 now prints
six numbers with no home, and Chapter 10's future-work paragraph (line 99)
rests on this comparison.

#### 9.7 Scope of the Evaluation, and Table 9.1

**9-20 [S] line 340** (mech)
> "The evaluation rests on one subject in one controlled setup, recorded three times: **the rail recording of about 30 seconds, the handover recording of about 50 seconds and the loop recording of about 70 seconds (Section 7.1)**."

Weakened: the new 7.1 names the three recordings but gives no durations.
Fix: drop the pointer, or add the durations to Section 7.1 (cheap, and it
would also repair 6-3 and 9-16 partially).

**9-21 [S] line 346, first half** (judg)
> "**The cuff seam of the rail recording sits 4.3 centimetres from the trusted wrist**, and the bracelet and the watch of the loop recording 4.5 and 2.1 centimetres (Section 7.4.2). ... **The label sets hold 21 and 20 frames**, so a single frame moves a 95th percentile ..."

The loop values 4.5 and 2.1 cm are still correct (new Table 7.6). The rail
cuff-seam set is excluded under D-033 and its 4.3 cm value no longer
exists in Chapter 7. "21 and 20 frames" matches nothing printed: Table 7.6
has n=3 and n=4, Table 7.7 has n=16 (left) and n=4 (right).
Fix: rewrite around the loop-only proxies and the new n values. Mechanical
once the author accepts dropping the rail label set.

**9-22 [S] line 346, second half** (judg) - HIGH, directly contradicted
> "... and **the synthetic comparison covers only the 342 eligible clean holding frames of the rail recording (Section 7.4.1)**."

Section 7.4.1 is handover-based, 3 x 45 = 135 frames per method, and
explicitly rules out the single-hand recording. Same defect as 9-15.

**9-23 [S] line 351** (judg)
Same claim as 9-2, in the closing of Section 9.7: "The physical route is
not registered into the calibrated world frame, so no point-to-path
distance exists (Section 7.2)".

**9-24 [S] line 367, Table 9.1 row "Hips behind the desk"** (judg)
> "Torso detector on 31.3 percent of the rail recording and on 326 frames of the handover recording **(Sections 7.1 and 7.3)**"

Both numbers were dropped with old Sections 7.1 and 7.3.

**9-25 [S] line 376, Table 9.1 row "Physical route not registered"** (judg)
> "**Section 7.2 reports the spread about a fitted line and no distance to the physical path**"

Section 7.2 currently reports no spread. Same as 9-1.

**9-26 [S] line 379, Table 9.1 row "Hand-object offset through a regrasp"** (judg)
> "Object estimate 13.2 cm from the label over the loop recording's labelled left failure frames **(Section 7.4.2)**"

The object-estimate column is not in Table 7.7. Same as 9-10.

**9-27 [S] line 382, Table 9.1 row "Recovery nearer the label ..."** (judg)
> "Loop recording, labelled left failure frames: recovery solve 13.1 cm from the label against 13.2 cm for the object estimate; frame 1462 bends the elbow of a straight arm **(Section 7.4.2)**"

The 13.1 cm survives (Table 7.7, left, object-assisted). The 13.2 cm
comparator and the frame-1462 detail do not. Same as 9-10, 9-11.

**9-28 [N] lines 17-51, 76, 84, 90, 96, 100, 116, 119, 139, 148, 153, 168, 185, 191, 197, 202-203, 210-213, 220, 225, 246-247, 259, 266, 272, 280, 339, 344-345, 348** (mech)
Source comments and the module docstring encode the *previous* mapping
("the object statistics are Section 7.2, the person and handover statistics
Section 7.3, the synthetic masking Section 7.4.1, the natural failure
labels Section 7.4.2"), and cite removed artefacts by number: **Figure
7.14** (line 197), **Figure 7.15** (line 203), **Figure 7.10** (line 247),
**Table 7.2** (lines 211, 222 comment) and **old Section 7.7** (line 272).
None is printed, so the checker is silent, but they will mislead whoever
performs the repairs above. Refresh with the fix.

---

### scripts/build_ch10.py

**10-1 [S] line 72, first citation** (judg)
> "**The marker branch detected the object on 899 of the 900 frames of the rail recording (Section 7.2).**"

Detection counts dropped from Chapter 7 (see 9-5). This sentence is part of
Chapter 10's direct answer to the central question of Chapter 1.

**10-2 [S] line 72, second citation** (judg) - HIGH
> "**The model wrist sits a median of 15.77 centimetres from the marker origin while the right hand holds the cube alone and 14.08 while the left hand does, against the physical distance of approximately 16 centimetres measured for a single-hand grip (Section 7.3).** The transfer medians of 17.91 and 15.85 describe a changed grip and are not graded against it."

Section 7.3 contains none of this (see 9-6). Chapter 10's headline
demonstration of integrated human-object reconstruction now rests on a
result the thesis no longer prints.
Fix: author decision, jointly with 9-6. If the wrist-to-marker comparison
is not reinstated in Chapter 7, Chapter 10 needs a different quantity for
this claim - the candidates in the rebuilt chapter are Tables 7.1 / 7.2
(rendered joint error, 5.7 to 12.0 cm medians), which support a weaker
statement.

**10-3 [S] line 81, label-set clause** (mech)
> "**The label sets contain 21 and 20 points selected manually on the colour image**, and the clean frames put each mark 2.1 to 4.5 centimetres from the wrist the landmark defines."

Same as 9-21. The "2.1 to 4.5 centimetres" range is still correct against
new Table 7.6; "21 and 20 points" is not.
Verified still correct in the same paragraph, no change needed: the
recovery 5.2 / plain 11.4 / hold-last 17.6 right-arm medians and the left
13.1 / 12.3 medians all match the new Table 7.7 exactly.

**10-4 [S] line 81, final sentence** (judg) - HIGH, directly contradicted
> "**The synthetic masking of Section 7.4.1 adds only slow windows, where a held angle is nearly right.**"

Section 7.4.1 now contrasts three motion magnitudes and concludes with a
window-dependent comparison. Its lower-motion window does favour direction
memory, but "only slow windows" is no longer true, and the claim's basis
(3.0-6.0 degrees of arm travel on the rail recording) is gone.

**10-5 [S] line 85** (judg)
> "**The physical route is not registered into the calibrated world frame, so no distance to the physical path exists (Section 7.2)**, and the causal result is a replay with no complete live-camera validation (Section 8.5)."

Same as 9-2 / 9-23. Under D-035 this limitation statement may no longer be
the right one.

**10-6 [S/C] line 99** (judg)
> "**The rule of Section 9.4, which holds the hips at their last accepted position, stays a documented option the reported results leave out.** Adopting it needs a recording in which the pelvis pose is measured independently ..."

The pointer to Section 9.4 resolves, but Section 9.4's hip-hold paragraph
is itself now unsupported (9-19). If 9-19 is resolved by deleting the
paragraph, this future-work item loses its evidence.

**10-7 [N] lines 24-45** (mech)
Docstring records the pre-D-029 mapping and the S2 decision "Section 7.4.2
labels three natural sets, the rail right side and the two loop sides" -
now two sets, both loop (D-033). Refresh.

---

### scripts/build_ch1.py

**1-1 [C] line 155** (judg)
> "... **Chapter 7 reports the offline experimental evaluation against physical references, manual wrist labels, synthetic exact references and within-recording comparisons, and states that the physical route is not yet registered into the world frame.** Chapter 8 examines real-time feasibility ..."

Three problems in one sentence:
- "**synthetic exact references**" was the removed solver verification
  (old Section 7.5, old Table 7.5). The new Section 7.4.1's reference is
  the unmasked *reconstruction*, which is not an exact reference. This is
  the roadmap-level survivor of the dropped result flagged in 3-1.
- "physical references" is currently unsupported (Section 7.2 blocked).
- "states that the physical route is not yet registered into the world
  frame" - Chapter 7 states no such thing.
Fix: rewrite the clause once the author settles 3-1 and Section 7.2.

**1-2 [C] line 151** (no change needed - verified)
"Chapter 7 covers the rail task one-handed and with a handover, and takes
its natural failure windows from the two-hand loop recording as well" is
still accurate against the rebuilt chapter.

**1-3 [N] lines 16, 49, 53, 55, 73** (mech)
Docstring claims "Chapter 7 no longer defines the reference path" and
describes the "references of Chapter 7 (the unmasked solve under synthetic
masking ...)" - a pre-D-029 description. Refresh.

---

### scripts/build_ch2.py

**2-1 [C] line 134** (judg)
> "... with a handover between the hands in the handover recording of Chapter 7. **Chapter 7 reports the physically measured route and the reconstructed trajectories.** Figure 2.{F_RAILS} shows the setup from three viewpoints, and Table 2.1 lists its objects."

Chapter 7 does not report the physically measured route; Sections 7.2.1 and
7.2.2 are "Data Required". Same defect class as 4-1.
Fix: blocked on the Section 7.2 work.

**2-2 [N] lines 23-53** (mech)
Docstring: "the waypoints of both recordings live at the start of Chapter
7", "the R5 loop recording appears only in Chapter 7's ..." - refresh.

**2-3 [C] line 301 and Appendices (build_appendix.py line 386)** (mech, low)
Both say "**The plain, masked and recovery solves of Chapter 7** all rest
on it, and the hold-last baseline does not." The three solves still exist
(7.4.1 hold-last / direction-memory / object-assisted; 7.4.2 plain /
hold-last / object-assisted), but Chapter 7's vocabulary changed - there is
no "masked solve" name any more, and hold-last is now one of the compared
methods rather than only a baseline. The claim "the hold-last baseline does
not [rest on the hip preparation]" should be re-verified against the
rebuilt 7.4.1 and 7.4.2 method definitions.
Same sentence appears in build_ch5.py line 195.

---

### scripts/build_frontmatter.py

**FM-1 [C] lines 161-171, abstract paragraph 4** (judg) - HIGH
> "The task slides the cube along a straight wooden rail. **About the line fitted to the slide, the reconstructed marker origin has a median spread of 1.0 centimetres and a 95th percentile of 2.4, and a handover recording gives 0.3 and 1.6.** The fit therefore describes the trajectory against itself, and the measured route is not yet registered into the calibrated world frame. **Through the rail wrist gap every method stays at about the uncertainty of the hand-placed wrist labels**, while the two natural loop windows give opposite outcomes, the constraint helping on one and not on the other. A causal version replayed the recording at its recorded pace, about 29 frames per second, with a display smoother on the output only; no complete live-camera session was validated."

Two abstract-level claims no longer supported by the body:
- the four fitted-line spread values (1.0 / 2.4 and 0.3 / 1.6 cm) are not
  printed anywhere in the rebuilt thesis;
- "through the rail wrist gap every method stays at about the uncertainty
  of the hand-placed wrist labels" was the rail label set (old Section
  7.4.2), which D-033 removed - Section 7.4.2 is now loop-only.
The final clause ("the two natural loop windows give opposite outcomes") is
still supported by Table 7.7 and needs no change.
Fix: author rewrite. An abstract must not carry results the body no longer
prints. Note the 350-word gate enforced later in the same builder.

**FM-2 [N] lines 128-137** (mech)
Source comment pins the abstract's numbers to "Section 7.2" and "Section
7.4.2" of the previous chapter. Refresh with FM-1.

**FM-3 [C] line 819, glossary** (no change needed - verified)
"the tables of Chapter 7 report both" (median, p95) is still true; the new
tables add a maximum column, so the entry could optionally mention it.

**FM-4 [N] generated lists** (mech - rebuild only)
`FrontMatter_V8_Condensed.docx` currently carries a List of Figures with
**Figures 7.1 - 7.15** and a List of Tables with **Tables 7.1 - 7.5**, all
with the old captions. These lists are scraped from the chapter .docx files
by this builder, so they are corrected by re-running it - no source edit.
The assembled `Thesis_V8_Condensed.docx` / `.pdf` are stale for the same
reason.

---

### scripts/build_thesis.py

**T-1 [N] lines 584-585** (mech, tooling only)
Placeholder help text:
> "[pending manual labels]": "Wrist labels on the natural failure windows, **Table 7.7**. Waiting on the manual labelling that **Section 7.3.3** describes."

Section 7.3.3 does not exist in either the old or the new numbering, and
Table 7.7 now means the natural-occlusion wrist-to-proxy table. Not printed
in the thesis; it is the help string the assembly script shows the author.
Fix: retarget or delete.

---

## 4. Results the restructure dropped that the rest of the thesis still depends on

Each of these is printed nowhere in the rebuilt Chapter 7, yet is still
asserted or relied on elsewhere. They need an author decision: reinstate in
Chapter 7 (or an appendix), or withdraw every dependent claim.

| dropped result | old home | still depended on by |
|---|---|---|
| Kinematic solver verification, six synthetic datasets | old 7.5, old Table 7.5 | Ch3 closing (3-1, the one broken reference), Ch1 roadmap "synthetic exact references" (1-1), Ch6 closing (6-4), Ch8 (8-1) |
| Wrist-to-marker physical reference (~16 cm) and the four medians 15.77 / 14.08 / 17.91 / 15.85 | old 7.3 | Ch9 §9.2 (9-6), **Ch10 §10.1 answer to the central question** (10-2) |
| Hip-hold vs hip-depth-preparation comparison (r7/r6b_hip_hold) | old 7.3 | Ch9 §9.4 (9-19), Ch10 §10.2 future work (10-6) |
| Rail-recording manual label set: 21 frames, cuff seam 4.3 cm, clean recovery 9.1 vs plain 6.9 cm | old 7.4.2, old Tables 7.3/7.4 | Ch9 §9.3 (9-13) and §9.7 (9-21), abstract (FM-1) |
| Rail-recording synthetic masking: 342 eligible frames, five windows, 3.0-6.0 deg arm travel, nearly straight arm | old 7.4.1, old Table 7.2 | Ch9 §9.3 (9-14, 9-15) and §9.7 (9-22), Ch10 §10.1 (10-4), Ch6 §6.4 (6-2) |
| Failure coverage: 13.3 / 93.6 / 31.3 percent, 326 handover torso frames, 19.4 vs 0.8 cm hip split, old Figure 7.3 | old 7.1 | Ch9 §9.4 (9-16) and Table 9.1 (9-24) |
| Object detection counts 899/900, 1498/1499, 2058/2099 | old 7.2 | Ch9 §9.1 (9-5), Ch10 §10.1 (10-1), Table 9.1 |
| Fitted-line scatter 1.0 / 2.4 / 3.1 cm rail and 0.3 / 1.6 / 3.4 cm handover; rail-height cross-check 0.2 and 0.6 cm above the 3.8 cm tape | old 7.2, old Table 7.1 | **abstract** (FM-1), Ch9 §9.1 (9-1, 9-3), Table 9.1 (9-25), Ch4 (4-1) |
| Handover effective segment lengths 24.1 / 23.3 and 25.2 / 22.3 cm | old 7.3 | Ch9 §9.2 (9-9) |
| Model-wrist to measured-wrist 0.96 / 1.17 cm and model wrist 6.5 cm above the rail line | old 7.3 | Ch9 §9.2 (9-7) - now contradicted by Table 7.2's 5.7 / 6.9 cm |
| Handover model-wrist jumps up to 23 cm at the hip-repair edges; 417 repaired frames | old 7.3 | Ch9 §9.4 (9-18), Ch10 §10.1 line 83 |
| Handover left arm rejected on 63 frames after the release | old 7.3 | Ch9 §9.4 (9-17) |
| Unity hand beside the cube, 15.2 and 12.1 cm | old 7.3, old Figure 7.9 | Ch9 §9.2 (9-8) |
| Frame-level natural-occlusion detail: frame 1462 (64.4 deg on a straight arm), frame 1890 (14.0 / 5.0 / 15.2 cm), the object-estimate column (13.2 cm) | old 7.4.2, old Figures 7.14 and 7.15 | Ch9 §9.3 (9-10, 9-11, 9-12), Table 9.1 (9-26, 9-27) |

Two of these are structural rather than cosmetic:
1. **Solver verification** has no remaining home anywhere in the thesis.
   Chapter 3 currently ends by promising a verification that does not
   exist.
2. **The wrist-to-marker physical reference** was the only human-object
   quantity with an external physical reference, and Chapter 10's headline
   conclusion is built on it. The rebuilt Chapter 7 offers no substitute
   with a physical reference for the human-object pair.

---

## 5. Ordering note

Items 4-1, 9-1, 9-2, 9-3, 9-5, 9-23, 9-25, 10-1, 10-5, 2-1 and FM-1 all
depend on what Section 7.2 ends up printing (D-035 is SETTLED and the
object results are being computed). Do not rewrite them before Section 7.2
is populated. Everything else can be repaired now.

After the repairs, `python check_refs.py` should again report
`UNRESOLVED: none`. A passing checker is necessary but not sufficient -
36 of the 43 defects above pass it today.


## 6. Final completion disposition, 2026-09-12

The preceding list records the transient state immediately after Chapter 7
restructuring. It is historical, not a request to restore the removed evaluation
structure. Current decisions D-035 to D-053, the delivered Chapter 7 builder and
its pinned audit_evidence/ch7_restructured outputs take precedence.

- D-035/D-036 settle physical marker-centre waypoints and their independently
  selected transition frames. Section 7.2 now carries endpoint-distance results
  and separate fitted-line scatter. D-045 keeps the coarse rail-height accuracy
  cross-check removed; the apparatus height is not an evaluation result.
- D-037 places solver verification in Appendix H. The old Section 7.5 promise
  does not require restoring that section inside Chapter 7.
- D-038/D-053 retain the approximate single-grip wrist-to-marker check in
  Section 7.3.3 with consistent marker-centre point identity. Transfer values
  are descriptive; the 16 cm reference is not anatomical or full 3D truth.
- D-039 to D-043 distinguish raw-reference bare-model and rendered-rig errors,
  recording-wide and capture-subset scopes, held/constrained rail states and
  actual rig dimensions. Old 0.96/1.17 cm and removed rig distances must not be
  copied from the historical list into the thesis.
- D-046/D-047/D-049 separate detected frames, accepted object samples and
  valid-landmark frames. The pinned 2058/2099 loop count is detection coverage.
- D-050 keeps the recorded marker depth patch as documentary content only.
  D-051 names the task phase object acquisition while preserving Chapter 5's
  technical grasp terminology. The Chapter 10 replacement remains approved.
- D-068/D-070 close the remaining Chapter 5 pose-chain gap and explain the
  floor mapping used by the already correct Chapter 7 evaluator. Figures
  7.3/7.4 and equation 7.5 report Scene coordinates. No Chapter 7 number changes.
- D-070 removes Chapter 9's unsupported proxy-resolution threshold and
  tape-to-line-scatter attribution and Chapter 6's additive causal allocation
  of rendered discrepancy. D-069 completes literature numbering at assembly
  while source chapter identifiers remain frozen under D-048.

DETERMINED_DEFECTS.md is the current supported-correction checklist.
UNRESOLVED_ITEMS.md preserves the actual evidence limits, including historical
loop live inputs and Word-only QA. Final automated checks and rendered review
are recorded in DELIVERY_2026-09-12.md; old counts and unresolved-reference
examples above describe their own historical builds only.
