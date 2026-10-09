# Repeated material map (main body, Chapters 1 to 9)

Purpose: let nine chapter editors cut in parallel without contradicting each
other. Every explanation that appears in more than one place is listed once
below, with a single primary location. An editor working outside a topic's
primary location may keep at most the referring sentence named in the "other
locations" column, and may not restore the full explanation.

Line numbers refer to the plain-text dumps in
`scratchpad/dumps/` (`Chapter_N_*.txt`, `Appendices.txt`, `FrontMatter_V7.txt`).
The dump line numbers are printed in the files themselves, so `Ch7 L88` is the
paragraph that begins "Table 7.4 reports, for each window".

Word counts exclude `[FIGURE]` and `[MATH]` marker lines and include captions
and `TABLE |` rows. Current main body: 44,791 words.

Rule for choosing a primary location, applied throughout: the place where the
thesis first needs the full explanation for its own argument. In practice this
is the method chapter (2, 3, 4, 5, 6), not the introduction and not the
evaluation. Chapter 1 previews, Chapter 7 measures, Chapter 8 adapts and
Chapter 9 recalls; none of those four owns an explanation.

---

## 0. Standing hazard for every editor: stale section numbers

Chapter 5 was rewritten today. Its V7 sections 5.5 (Torso Repair on Camera
Rays) and 5.6 (Output States of the Solver) no longer exist; the torso repair
is parked in `writing/v8/CH5_PARKED.md` and the output states moved into the
Chapter 5 opening (Ch5 L5). V8 Chapter 2 also renumbered its filtering section
from 2.4 to 2.5. Chapters 6 to 9 and the appendices still carry the V7 numbers,
and the front matter file is entirely V7. These are dangling now, before any
cut, and they are listed again in section 6 below. No editor should "fix" them
locally by inventing a section that does not exist.

| Stale reference | Where it appears | What it should point at in V8 |
|---|---|---|
| Section 5.6 (twist hold, rate limit) | Ch6 L59; Ch7 L80 (twice); Ch7 L88 | Ch5 Section 5.5, final paragraph (Ch5 L94) |
| Section 5.6 (output state tags) | Ch6 L51 reads "the tags of Section 6.1", correct; but Ch6 L59 uses 5.6 for the twist | Ch5 chapter opening (Ch5 L5) for the three states |
| Section 5.5 (torso repair) | Ch7 L129, Ch7 L142, Ch9 L16 | No V8 location. Decision needed: restore from `CH5_PARKED.md` or rewrite these three sentences to describe the repair without a pointer |
| Section 2.4 (landmark filtering) | Ch7 L79; Appendices L95, L167 | Ch2 Section 2.5 |
| Section 2.2 (visibility gate 0.50) | Ch9 L7, Figure 9.1 caption | Ch2 Section 2.3 |
| Figure and table numbers | `FrontMatter_V7.txt` L146 to L226 in full | Regenerate against the V8 build; V8 Chapter 2 now has Figures 2.1 to 2.11 and Tables 2.1 to 2.3, V7 had Figures 2.1 to 2.8 and Table 2.1 only |

---

## 1. Repeated explanations

Each entry gives: the topic; every location with line numbers and approximate
word count; the primary location; what each other location keeps.

### 1.1 The person-space flip (F = diag(1, -1, 1))

| Location | Lines | Words |
|---|---|---|
| Ch2 2.2.1, "Person space P is the camera frame with the y axis flipped" | L29 | 59 |
| Ch2 Table 2.2, row F | L40 | 22 |
| Ch3 3.1, handedness and determinant discussion | L10 | 214 |
| Ch3 3.1, the flip itself, equation (3.1) and its reading | L11, L13 | 247 |
| Ch3 3.1, Figure 3.2 caption | L15 | 55 |
| Ch3 3.1, why points are flipped and not rotations | L16 | 122 |
| Ch6 6.2, the flip re-entering the anchor composition | L28, L30, L31 to L36 | 93 + 104 + 366 |
| Appendix D.3, closing sentence | Appendices L120 | ~20 |

Primary: **Ch3 Section 3.1, L11 to L16** (equation 3.1, the reflection sign, the
worked wrist in both frames, and the reason the flip acts on points only).

Other locations keep:
- Ch2 L29: one sentence naming person space and pointing at equation (3.1). Cut
  the explanation of why heights read upward (about 30 words).
- Ch2 Table 2.2 row F: unchanged, it is the index.
- Ch3 L10: keep the statement that person space is camera-anchored and the Unity
  world is desk-anchored. Move the determinant argument ("both reflections
  compose to +1, so no net mirror reaches the rendered scene") out of Chapter 3
  and into Ch6 L30, which is the only place both reflections exist at once.
  Saving about 70 words.
- Ch6 L30: gains the determinant argument, so it says it once for the pair.
  Cut its own repetition of "the flip F of Chapter 3 has determinant minus one
  for the same reason" (about 20 words).
- Appendix D L120: one clause, already minimal.

### 1.2 The world frame on the desk marker, and camera-placement invariance

| Location | Lines | Words |
|---|---|---|
| Ch1 1.2.4, gap 4 | L38 | 34 |
| Ch2 2.2.1, "The world frame W sits on the desk marker" | L26 | 79 |
| Ch2 Table 2.2, rows TCW and TWC | L35, L39 | 46 |
| Ch2 2.2.2, the three markers and the frozen anchor | L46 | 90 |
| Ch2 2.2.2, why the anchor is frozen (noise argument) | L50 | 116 |
| Ch2 2.4, "The desk marker (ID 2) is the world origin ... does not depend on where the camera stands" | L74 (part) | ~35 of 125 |
| Ch4 4.1, the two-corner thought experiment and the chain | L5 | 172 |
| Ch4 4.1, the cancellation argument | L11 | 168 |
| Ch9 9.3, objective 1 | L43 | 58 |
| Abstract, front matter | FrontMatter L36 | ~25 |

Primary: **Ch4 Section 4.1, L5 to L11** (the invariance argument, equation 4.1,
and the camera pose falling out of the inverse anchor).

Other locations keep:
- Ch2 L26: two sentences, W sits on the desk marker and every object pose ends
  up in W. Cut "The reconstruction then does not depend on where the camera
  stands" (Ch4 owns it).
- Ch2 L74: cut the invariance clause entirely (about 35 words); it is the third
  statement of it inside Chapter 2 alone.
- Ch2 L50: this stays. The freezing rationale is a noise argument, not an
  invariance argument, and Chapter 2 owns it. Ch4 L11's closing sentence
  ("The camera cancels whether or not the anchor is frozen; the anchor is
  frozen for the noise reason of Section 2.2.2") restates it and can go to a
  half sentence, saving about 35 words.
- Ch1 L38 and Ch9 L43: one clause each.

### 1.3 Depth sampling from the registered stream instead of MediaPipe depth

| Location | Lines | Words |
|---|---|---|
| Ch1 1.2.1, "Back-projecting the 2D detections through a calibrated depth camera" | L14 (part) | ~45 |
| Ch1 1.2.4, gap 2 | L36 | 34 |
| Ch2 2.3, "the pipeline discards those values" | L69 | 100 |
| Ch5 5.2, the silent failure: correct pixel, wrong depth | L14 | 144 |
| Ch7 7.1.3, geometry detectors catch what visibility cannot | L49 (part) | ~60 |
| Ch9 9.1, "The cause sits one step earlier, in a choice made in Chapter 2" | L17 | 101 |
| Ch9 9.3, objective 2 | L44 | 87 |
| Appendix C.1, appearance depth not used | Appendices L70 (part) | ~35 |
| Appendix C.2, the gate and the three source codes | Appendices L84 | 105 |
| Appendix D.3, the 5 by 5 median rule | Appendices L121 | ~110 |

Primary for the choice: **Ch2 Section 2.3, L69.**
Primary for the consequence (a correct pixel over a wrong surface): **Ch5
Section 5.2, L14.** These are two different claims and both stay; do not merge.

Other locations keep:
- Ch1 L14 and L36: one clause each, no mechanism.
- Ch7 L49: keep the counts and the sentence that the geometry detectors fire
  before the tracker declines. Cut the re-explanation of why the tracker cannot
  see it (about 60 words); Ch5 L14 owns it.
- Ch9 L17: one sentence, pointing at Ch2 2.3 and Ch5 5.2. Saving about 70 words.
- Appendix C L84: keep. It is the only statement of the three source codes.

### 1.4 The Hampel test, gap bridging, and the zero-phase smoother

| Location | Lines | Words |
|---|---|---|
| Ch2 2.5, the three error cases A, B, C | L78 to L82 | 119 |
| Ch2 2.5, Hampel (case A) | L83 | 152 |
| Ch2 2.5, interpolation (case B) | L86 | 80 |
| Ch2 2.5, Butterworth and the One Euro preview (case C) | L89 | 197 |
| Ch2 2.5, the raw baseline and the repair flags | L92 | 80 |
| Ch4 4.2, the same three cases with rotation added | L15 | 286 |
| Ch8 8.1, what the despiking test does offline | L8 (part) | ~50 of 126 |
| Ch8 8.1, what gap bridging does offline | L9 (part) | ~40 of 113 |
| Ch8 8.1, what the Butterworth does offline | L10 (part) | ~35 of 89 |
| Ch8 Table 8.1, left column | L15 to L21 | ~65 |
| Appendix F, all four candidates in full | Appendices L167 to L182 | ~950 |

Primary: **Ch2 Section 2.5, L78 to L92**, with Appendix F holding the
comparison of the four candidate smoothers.

Other locations keep:
- Ch4 L15: keep only what is new for a pose track, namely that a spiked pose is
  dropped as a whole, that rotation bridges along the shortest turn, that a run
  at either end holds a fixed pose, and that rotation smoothing is the chordal
  mean of equation (2.1) over a short window. Cut the re-explanation of what a
  Hampel test and a Savitzky-Golay filter compute (about 110 words).
- Ch8 L8 to L10: cut the offline restatements; Table 8.1's left column already
  names each offline stage. Keep the causal replacement and the reason it is
  needed. Saving about 100 words.
- Ch2 L89: cut the side-by-side list of the four candidates and their
  mechanics (about 55 words). Table F.1 carries it. Keep the sentence that the
  backward pass forces offline operation and that Chapter 8 measures the
  exchange.

### 1.5 The failure detectors

| Location | Lines | Words |
|---|---|---|
| Ch5 5.2, declared versus silent failure | L14 | 144 |
| Ch5 5.2, the rigid-body statements | L15 | 86 |
| Ch5 5.2, Figure 5.2 caption | L17 | 91 |
| Ch5 5.2, the six detectors and their thresholds | L18, L19 | 346 |
| Ch5 5.2, mask combination and cleaning | L20, L21 | 256 |
| Ch7 7.1.3, run over the rail recording | L30 | 199 |
| Ch7 7.1.3, run over the loop recording | L33, L36 | 113 |
| Ch7 Table 7.2 and its caption | L37 to L48 | 232 |
| Ch7 7.1.3, "Two kinds of failure sit behind the counts" | L49 | 194 |
| Ch8 8.1, the recovery machinery enumerated again | L7 (part) | ~70 of 160 |
| Ch9 9.1, the same silent-failure argument with the same numbers | L5, L8 | 193 |

Primary: **Ch5 Section 5.2, L14 to L21.**

Other locations keep:
- Ch7 L30, L33, L36, Table 7.2: keep in full. These are measurements, not
  explanations.
- Ch7 L49: keep the counts (537 and 439 frames), the 31.30 centimetre hip split,
  and the two forearm and upper-arm lengths before each blackout. Cut the
  restatement of what an acquisition detector is against what a geometry
  detector is (about 70 words).
- Ch8 L7: replace the enumeration of the recovery steps with one sentence
  saying that every step of Chapter 5 is closed form and reads no future frame.
  Saving about 70 words.
- Ch9 L5 and L8: keep Figure 9.1 and one sentence. The 47.2 against 25.8 and
  3.0 against 25.5 centimetre pair also appears at Ch7 L49 and in Table 9.1
  row 1; state it once, in Table 9.1. Saving about 120 words.

### 1.6 The hand-object offset h

| Location | Lines | Words |
|---|---|---|
| Ch5 5.3, the offset is not known and is fitted | L43 | 151 |
| Ch5 5.3, equations (5.1) to (5.3) and their reading | L44 to L55 | 226 |
| Ch5 5.3, the recursive update and its four rules | L56, L58 | 274 |
| Ch5 5.4, the estimate w and why it does not age | L70 to L74 | 329 |
| Ch5 Table 5.1 rows h, hk, N, c | L28 to L31 | 70 |
| Ch7 7.3.2, "The first input is the hand-object offset" | L101 | 131 |
| Ch8 8.1, the online form of the offset | L12 (part) | ~80 of 154 |
| Ch9 9.1, the regrasp limitation with the same numbers | L19 | 140 |
| Ch9 Table 9.1, regrasp row | L29 | 37 |
| Ch9 9.2, "It would also give the hand-object offset a measured origin" | L38 (part) | ~15 |

Primary: **Ch5 Sections 5.3 and 5.4, L43 to L74.**

Other locations keep:
- Ch7 L101: keep the measurement (12.86 centimetres or more away from the
  episode fit, 13.09 on the left, 0.86 on the good right window, wrist error
  median 13.98 against 2.16) and one clause of cause. Cut the re-derivation of
  why the estimate is only as good as the offset (about 45 words).
- Ch8 L12: keep the live form only. Cut the restatement of the offline fit
  (about 40 words).
- Ch9 L19: cut to one sentence plus the Table 9.1 row. The numbers 12.86, 13.98
  and 1.18 belong to Ch7 L101 and Ch7 L102; quote at most one of them.
  Saving about 100 words.

### 1.7 The holding state and the grip episode

| Location | Lines | Words |
|---|---|---|
| Ch5 opening, Case B priority over Case A | L4 (part) | ~45 |
| Ch5 5.1, the grasp is rigid within one episode | L11 (part) | ~40 |
| Ch5 5.3, the five instantaneous conditions | L59 | 151 |
| Ch5 5.3, entry, persistence, exit, hold and release radii | L60 | 148 |
| Ch5 5.3, Figure 5.4 caption | L62 | 32 |
| Ch5 5.4, the guard at both ends of the offset | L73 | 93 |
| Ch7 7.3.1, eligibility rule (a hand must hold the object) | L79 (part) | ~60 |
| Ch8 8.1, the online episode tracker and the exit cost | L12, L13 | 240 |
| Ch8 8.3, live episode coverage | L71 (part) | ~50 |
| Ch9 9.1, the rest reference assumption | L20 | 90 |

Primary: **Ch5 Section 5.3, L59 to L62.**

Other locations keep:
- Ch7 L79: one clause inside the eligibility rule, no restatement of entry and
  exit.
- Ch8 L12 and L13: keep. The bounded exit delay is a real-time result, not a
  repetition.
- Ch9 L20: fold into the Table 9.1 row for the live-sensor session and keep one
  sentence in the prose. Saving about 60 words.

### 1.8 The three output states (measured, held, constrained)

| Location | Lines | Words |
|---|---|---|
| Ch5 opening, the seven joint groups and the three states | L5 | 129 |
| Ch5 5.5, constrained versus held after a two-link failure | L92 (part), L94 (part) | ~80 |
| Ch6 6.1, the person record and its state tags | L20 | 113 |
| Ch6 6.1, the merger's four states | L22 | 181 |
| Ch6 6.1, the tag ordering through the delay buffer | L23 | 117 |
| Ch6 6.3, the coloured spheres | L51 | 177 |
| Ch7 7.3.2, "each joint group that consumed a removed landmark reported itself as recovered" | L117 (part) | ~35 |
| Ch8 Table 8.4, per-joint output states row | L60 | 29 |
| Ch8 8.3, the second new-wiring item | L68 (part) | ~40 |
| Ch9 9.3, "every quantity the system reports is marked" | L51 (part) | ~35 |

Primary for the three solver states: **Ch5 chapter opening, L5.**
Primary for the four merger states: **Ch6 Section 6.1, L22.**

These are two different state sets. Chapter 5 emits three per joint group;
the merger emits four per stream. An editor merging them would create an
error. Keep both definitions and keep the sentence in Ch6 L23 that says how
the joint-group tags travel through the merger's own states.

Other locations keep:
- Ch6 L20: one sentence naming the tags and pointing at Ch5. Cut the
  re-definition of the seven groups (about 50 words); Ch5 L5 has it.
- Ch6 L51: keep the colour mapping only, which is new. Cut the restatement of
  what held and constrained mean (about 40 words).
- Ch9 L51: one clause.

### 1.9 The rail reference path and the task

| Location | Lines | Words |
|---|---|---|
| Ch2 2.1, "The subject moves a cube along the desk and then along a wooden rail" | L4 (part) | ~55 of 102 |
| Ch7 7.1, the two recordings inventory | L4 | 154 |
| Ch7 7.1.1, the three legs, W1, W2, W3 | L8 | 209 |
| Ch7 7.1.1, the rail as the one physical ground truth | L9 | 114 |
| Ch7 7.1.1, the loop task and its eight stations | L14 | 224 |
| Ch8 8.1 opening, the rail recording re-described | L3 (part) | ~55 of 135 |
| Ch9 9.1, both recordings re-described | L13 (part) | ~110 of 258 |
| Appendix A.1, the take as performed | Appendices L29 | ~95 |

Primary: **Ch7 Section 7.1.1, L8 and L9** for the reference path;
**Ch7 Section 7.1, L4** for the two-recording inventory.

Other locations keep:
- Ch2 L4: two sentences, the task and the pointer to Chapter 7. Cut the
  restatement of what the reference path is (about 30 words).
- Ch8 L3: one clause, "the rail recording of Chapter 7 replayed at its recorded
  pacing". Saving about 55 words.
- Ch9 L13: cut the re-description of frame counts and durations (about 110
  words). Keep the claim that two takes support no statement about body sizes,
  grips or working habits, and keep the eligible-frame counts, which are the
  argument.
- Appendix A L29: keep. It is the acquisition record, not an evaluation claim.

### 1.10 Synthetic masking as a reference, against manual labels

| Location | Lines | Words |
|---|---|---|
| Ch7 7.1, the accuracy rule and its two satisfying situations | L5 | 186 |
| Ch7 7.3 opening, the two references named again | L76 | 118 |
| Ch7 7.3.1, the eligibility rule | L79 | 220 |
| Ch7 7.3.3, the label protocol | L119 to L122 | 359 |
| Ch7 7.3.3, Table 7.7 placeholder and its two paragraphs | L123 to L127 | 240 |
| Ch7 7.5, "Until the manual labels of Section 7.3.3 exist" | L146 (part) | ~30 |
| Ch9 9.1, the whole protocol restated | L14 | 176 |
| Ch9 9.3, objective 4, the split by what the arm is doing | L46 (part) | ~70 |

Primary: **Ch7 Section 7.1, L5** for the rule; **Ch7 Section 7.3.3, L119 to
L122** for the protocol.

Other locations keep:
- Ch7 L76: two sentences. Cut the re-naming of the two references (about 45
  words); L5 has just given them.
- Ch7 L79: keep the rule. It is the eligibility condition, specific to 7.3.1.
- Ch9 L14: cut to two sentences. The protocol belongs to Ch7 7.3.3. Keep the
  claim that the two recordings do not close the gap between them, which is the
  limitation and appears nowhere else. Saving about 120 words.
- The pending status of Table 7.7 must survive every cut, in Ch7 and in Ch9.

### 1.11 Seven rotations against four solved

| Location | Lines | Words |
|---|---|---|
| Ch3 3.3.1, the seven-rotation description and the four solved | L65 | 112 |
| Ch3 3.3.1, Figure 3.6 caption | L67 | 61 |
| Ch3 3.3.1, the four labels | L68, L71 | 188 |
| Ch3 3.4.4, pronation is unobservable | L128 | 129 |
| Ch5 5.5, "Chapter 3 met the same freedom from the other side" | L85 (part) | ~25 |
| Ch9 9.1, the whole argument again | L22 (part) | ~65 of 129 |
| Ch9 Table 9.1, no wrist or hand pose row | L31 | 24 |
| Ch9 9.3, objective 2's narrower scope | L44 (part) | ~35 |
| Ch9 9.2, the hand model direction | L38 (part) | ~40 |

Primary: **Ch3 Section 3.3.1, L65** for the seven against four split;
**Ch3 Section 3.4.4, L128** for why pronation cannot be seen.

Other locations keep:
- Ch9 L22: one sentence plus the Table 9.1 row. Cut the re-derivation of
  pronation (about 65 words).
- Ch9 L44 and L38: one clause each.

### 1.12 The desk and hip depth problem (the pitched root frame)

| Location | Lines | Words |
|---|---|---|
| Ch3 3.5, the 32.08 degree pitch explained | L166 (part) | ~90 of 182 |
| Ch5 5.1, the torso is assumed measured on every frame | L10 (part) | ~55 |
| Ch6 6.3, the red sphere at the hip on both rendered frames | L58 (part) | ~45 of 149 |
| Ch7 7.1.3, the 19.40 centimetre split on the rail recording | L30 (part) | ~55 |
| Ch7 7.1.3, the 31.30 centimetre split on the loop recording | L49 (part) | ~35 |
| Ch7 7.4, the whole measured account | L129, L141 to L144 | 576 |
| Ch9 9.1, the argument restated with the same numbers | L15 | 280 |
| Ch9 9.1, the cost of the repair | L16 | 136 |
| Ch9 Table 9.1, two rows | L26, L27 | 115 |
| Ch9 9.3, the repair result restated | L49 | 68 |

Primary: **Ch7 Section 7.4, L141 to L144** for the measured account of the
rail recording and the synthetic check.
Secondary primary that must stay: **Ch3 L166**, because the worked example
decodes the pitch and the reader needs the cause on the spot. Cut Ch3 L166 to
about 90 words: the pitch, its cause in the hip depth, and one forward pointer.

Other locations keep:
- Ch6 L58: one clause. Cut the re-explanation of why the hips read the rail
  (about 45 words).
- Ch9 L15: two sentences plus the two Table 9.1 rows. The 30.7, 31.3, 43.2 and
  24.3 percentages and degrees all appear in Ch7; quote at most two of them.
  Saving about 190 words.
- Ch9 L16: keep. The seeding limitation and the untested shoulder-depth gate are
  claims Chapter 7 does not make.
- Ch9 L49: keep the 57.4 to 15.3 and 21.9 to 0.5 figures, which are the
  conclusion's evidence, and cut the explanatory sentence around them.

Warning for the Chapter 7 and Chapter 9 editors: the repair these paragraphs
describe has no V8 home (see section 0). Do not delete the description while
the pointer problem is open, and do not add a new derivation of the repair
into Chapter 7.

### 1.13 The marker-blocked failure and the held object pose

| Location | Lines | Words |
|---|---|---|
| Ch4 4.2, the held case and its physical cause | L18 | 80 |
| Ch4 4.2, drift beside a held run, and a partly covered marker | L19 | 110 |
| Ch4 4.2, the single cleaning step and why it is the only one | L20 | 109 |
| Ch4 4.2, the rule, its bounds and its guard character | L21, L23, L24 | 322 |
| Ch7 7.2, the marker seen on 899 of 900 frames | L55 (part) | ~15 |
| Ch9 9.1, the marker loss with Figure 9.2 | L9 | 103 |
| Ch9 9.1, "A blocked marker costs more than a missing object sample" | L12 | 189 |
| Ch9 Table 9.1, object marker blocked row | L25 | 37 |
| Ch9 9.3, objective 3 | L45 | 87 |

Primary: **Ch4 Section 4.2, L18 to L24** for the mechanism;
**Ch9 Section 9.1, L9 with Figure 9.2** for the evidence that a finger crossing
the border is enough.

Other locations keep:
- Ch9 L12: keep the one claim that is new, that a marker gap falling inside a
  landmark failure window leaves the recovery nothing to anchor on and that the
  two did not overlap on the loop recording. Cut the re-description of holding,
  bridging and the cleaning rule (about 90 words); Ch4 owns those.
- Ch9 L45: one sentence with the counts.

### 1.14 Real-time replay against a live camera

| Location | Lines | Words |
|---|---|---|
| Ch2 2.5, the One Euro preview | L89 (part) | ~35 |
| Ch6 6.1, the source choice sits inside one process | L10 (part) | ~30 |
| Ch8 opening, replay defined | L3 | 135 |
| Ch8 8.3, the three open items for a live session | L72 | 176 |
| Ch8 8.3, closing statement | L73 | 103 |
| Ch9 9.1, replay is not a camera | L21 | 98 |
| Ch9 9.2, the live-sensor session as the first direction | L36 | 91 |
| Ch9 Table 9.1, no live-sensor session row | L32 | 28 |
| Ch9 9.3, the real-time result restated | L48 | 89 |

Primary: **Ch8 Section 8.3, L72** for the three open items.

Other locations keep:
- Ch9 L21: one sentence plus the Table 9.1 row. Cut the re-derivation that
  everything downstream of capture is source independent (about 60 words);
  Ch6 L10 and Ch8 L3 both already say it.
- Ch9 L36: two sentences. Cut the restatement of the two preconditions
  (about 40 words); Ch8 L72 lists three.
- Ch8 L73: keep, it is the chapter recap, cut to about 40 words (see section 2).

### 1.15 The streaming record layout

| Location | Lines | Words |
|---|---|---|
| Ch2 2.1, "a shared frame index says which person and object measurements belong to the same moment" | L16 (part) | ~25 |
| Ch6 6.1, the four processes and the frame buffer | L6, L9 | 194 |
| Ch6 6.1, the two branches as processes | L11 | 97 |
| Ch6 6.1, record layout, four-character code, sequence counter | L12 | 139 |
| Ch6 Table 6.1 and caption | L13 to L19 | 222 |
| Ch6 6.1, the person record's extra fields | L20 | 113 |
| Ch6 6.1, the cross-branch link and its three-step inverse | L21 | 174 |
| Ch6 6.1, the merger and its delay | L22, L23 | 298 |
| Ch6 6.1, startup ordering | L24 | 78 |
| Ch8 opening, the capture process re-described | L3 (part) | ~40 |
| Ch8 8.3, the cross-branch link re-described | L68 (part) | ~90 of 169 |
| Ch8 Table 8.4, two new-wiring rows | L59, L60 | 75 |

Primary: **Ch6 Section 6.1, L6 to L24.**

This is the section the brief marks for compaction. Concretely: keep the four
processes, the shared frame index argument at L10 (which is the synchronisation
claim the whole thesis rests on), the merger's render delay and its four
states, and Table 6.1. Compact the sequence-counter protocol at L12 to two
sentences, the three-step object-pose inversion at L21 to one sentence plus a
pointer to Ch4 equation (4.2), and startup ordering at L24 to one sentence.
Saving about 250 words inside Chapter 6.

Other locations keep:
- Ch8 L3: one clause. Saving about 40 words.
- Ch8 L68: keep the two "new wiring" claims and the guard of three frames. Cut
  the re-description of the inversion (about 90 words); it is Ch6 L21 verbatim
  in substance.

### 1.16 The chordal mean and the SVD projection

| Location | Lines | Words |
|---|---|---|
| Ch2 2.2.2, the derivation and equation (2.1) | L47, L49 | 222 |
| Ch4 4.2, rolling chordal mean as a smoother | L15 (part) | ~25 |
| Ch4 4.3, the numeric projection on the calibration window | L29 to L33 | 138 |

Primary: **Ch2 Section 2.2.2, L47 and L49.**

Ch4 L29 to L33 keeps the mean translation and the frozen anchor in one
sentence. The two printed 3 by 3 matrices differ only past the sixth decimal,
which the text itself states; print one and say the projection moved no entry
by more than 0.000002. Saving about 70 words.

### 1.17 Homogeneous transformations and the inverse of a rigid transform

| Location | Lines | Words |
|---|---|---|
| Ch3 3.1, rotation blocks, the 4 by 4 form, equations (3.2) to (3.4) | L17 to L24 | 574 |
| Ch4 4.1, the same inverse derived again, equation (4.2) | L6, L8 | 228 |
| Ch6 6.2, "the standard chaining of homogeneous transformations" | L33 (part) | ~20 |

Primary: **Ch3 Section 3.1, L17 to L24**, which owns equation (3.4).

Ch4 L8 and equation (4.2) duplicate equation (3.4). Cut the two-line derivation
and keep one sentence: the inverse is a transpose and one matrix-vector
product, by equation (3.4). Keep equation (4.2) only if Chapter 4 needs its own
numbered form for the worked example at L35; if it does, cut the derivation
prose instead. Saving about 110 words.

### 1.18 The Euler convention (z, then x, then y)

| Location | Lines | Words |
|---|---|---|
| Ch3 3.4, the convention, the multiplied-out matrix, the read-back | L88 to L98 | 436 |
| Ch6 6.2, "Orientations travel as Euler angles ... in the fixed order" | L38 | 79 |
| Ch6 6.3, the thirteen angles reassembled | L41 (part) | ~50 |

Primary: **Ch3 Section 3.4, L88 to L98.**

Ch6 L38 keeps one sentence: the receiver reassembles each rotation from the
three numbers because Chapter 3 solved in the animation system's own order.
Saving about 50 words.

### 1.19 The T-pose reference configuration

| Location | Lines | Words |
|---|---|---|
| Ch2 Figure 2.4(b) caption, the avatar in the T-pose | L25 (part) | ~30 |
| Ch3 3.2.2, the reference-pose check and the (0, 180, 0) decode | L60 | 270 |
| Ch3 Figure 3.5 caption | L62 | 128 |
| Ch6 6.3, why the captured rest pose must be the T-pose | L47 | 191 |

Primary: **Ch3 Section 3.2.2, L60** for the reference-configuration check.

Ch6 L47 keeps the rig-setup consequence, that the setup forces the T-pose
before capturing the five rest rotations, and equation (6.5). Cut the
re-argument that a droop would be added silently to every solved angle
(about 55 words), which is Ch3 L60's point in different words.

### 1.20 The straight-arm degeneracy and the unobservable twist

| Location | Lines | Words |
|---|---|---|
| Ch3 3.4.3, ez is always zero, the dimension count | L124 | 111 |
| Ch3 3.4.3, the collinear-segment breakdown | L125 | 126 |
| Ch5 5.5, ill conditioning near full extension | L93 | 102 |
| Ch5 5.5, the twist hold and the rate limit | L94 | 166 |
| Ch6 6.3, frame 114 and the held twist | L59 (part) | ~70 of 129 |
| Ch7 7.3.1, the reference twist is a held value | L80 (part) | ~90 of 155 |
| Ch7 7.3.1, the 80 degree twist walk and the rate limit | L88 (part) | ~110 of 307 |
| Ch7 7.3.2, the same degeneracy on the loop windows | L102 (part) | ~50 |
| Ch8 8.3, the azimuth near its degenerate configuration | L70 (part) | ~55 |

Primary: **Ch3 Section 3.4.3, L125** for the geometry;
**Ch5 Section 5.5, L93 and L94** for the conditioning rule and the two angle
rules that follow from it.

Other locations keep:
- Ch6 L59: one sentence. Cut the explanation of why a held twist swings a nearly
  straight forearm (about 50 words).
- Ch7 L80: keep the statement that the reference twist is held and that the two
  recovery methods do not inherit it, which is an evaluation fact. Cut the
  re-derivation (about 50 words).
- Ch7 L88: keep the numbers and the shape of the curve (worst frames are the
  first frames, error falls about 2 centimetres a frame, from the eighth frame
  no window exceeds 2.55 or 3.77). Cut the re-derivation of why the twist
  differs by 80 degrees (about 60 words).
- Ch8 L70: keep, it is the reason a check fails and it names Section 3.4.2.

### 1.21 Marker size 45 against the declared 50

Update 2026-09-12: the depth-implied marker size diagnostic (43.4 to 43.8
millimetres, earlier written here as 43.5 and 43.8) was removed from the thesis
by the author's instruction of that date, with its Chapter 9 discussion and its
Chapter 9 Table 9.1 row. Chapter 9 now prints no marker size at all, so the two
Ch9 rows below are historical and the Ch9 entry in "other locations keep" is
replaced. No editor may restore the cross-check, restore a limitation row for
it, or compute a replacement for it; see the retirement note under locked fact
1 of REVISION_2026-09-11_BRIEF.md. Chapter 2 Table 2.1 stays the location of
the 45 millimetre size, and no location may present a 45 against 50 correction.

| Location | Lines | Words |
|---|---|---|
| Ch2 Table 2.1 caption | L12 (part) | ~40 of 74 |
| Ch7 7.1, the object scale paragraph | L6 | 92 |
| Ch8 8.3, the first open item for a live session | L72 (part) | ~65 |
| Ch9 9.1, the metric scale limitation (removed 2026-09-12) | L18 | 134 |
| Ch9 Table 9.1, metric scale row (removed 2026-09-12) | L28 | 32 |
| Appendix E.4, the same scaling before Table E.1 | Appendices L147 (part) | ~55 |

Primary: **Ch2, Table 2.1 caption L12** for the scaling rule.

Other locations keep:
- Ch7 L6: one sentence saying which quantities carry the printed size and which
  do not. Cut the restatement of the 45 against 50 arithmetic (about 40 words).
- Ch8 L72: keep. A live calibration needs the true size, which is a real-time
  claim, not a repetition.
- Ch9 L18: nothing about marker size. The depth cross-check and the metric
  scale limitation are gone (2026-09-12) and nothing replaced them. The
  rebuilt Section 9.1 reads the object results against the physical route
  references of Section 7.2, and it keeps the distinction between a comparison
  made inside the recording and a distance quoted against a physical
  reference. That distinction is not marker-size material and this entry does
  not govern it.

### 1.22 The two-branch architecture

| Location | Lines | Words |
|---|---|---|
| Ch2 2.1, Pipeline A and Pipeline B and Figure 2.3 | L17, L19 | 180 |
| Ch4 opening, the marker branch's raw product | L2 (part) | ~60 |
| Ch5 opening, the two branches meeting | L2 (part) | ~55 |
| Ch6 opening, both branches complete and separate | L2 | 94 |
| Ch9 9.3, "two measurement chains that share only the recorded frames" | L50 (part) | ~40 |
| Abstract | FrontMatter L36 | ~90 |

Primary: **Ch2 Section 2.1, L17 with Figure 2.3.**

Chapter openings 4, 5 and 6 each re-state the branch structure as a transition.
Section 2 below treats these as previews and gives the combined budget.

### 1.23 Depth noise growing with the square of distance

| Location | Lines | Words |
|---|---|---|
| Ch1 1.1, sensor choice | L7 (part) | ~20 |
| Ch2 2.1, the 2 metre working distance | L13 (part) | ~30 |
| Appendix D opening | Appendices L97 (part) | ~40 |

Primary: **Appendix D opening.** Ch2 L13 keeps the clause with the citation,
Ch1 drops it.

---

## 2. Chapter previews and recaps

| Chapter | Preview lines | Preview words | Recap lines | Recap words | Recommendation |
|---|---|---|---|---|---|
| 1 | L2 (opening) and L48 to L50 (1.4 Organization) | 66 + 265 | none | 0 | Keep L2. Cut Section 1.4 from 265 to about 90 words, one paragraph naming the method chapters, the evaluation and the appendices. Saving about 175 |
| 2 | L2 | 52 | L92 | 80 | Preview to about 30. Recap to about 25, keeping only the raw-baseline sentence and the pointer to Chapters 3, 4 and 5. Saving about 77 |
| 3 | L2, L3, L4 | 174 + 120 + 65 | L190 | 25 | Cut hardest here. L2 repeats the end of Chapter 2 and the start of Chapter 6; L3 lists model properties that Sections 3.1 to 3.4 each prove in place. Reduce L2 to L4 from 359 to about 150. Keep L190 as is. Saving about 210 |
| 4 | L2, L3 | 118 + 92 | L47 | 91 | Preview to about 90 (drop the section-by-section listing at L3, which duplicates the headings). Recap to about 35, keeping the two products and the three consumers. Saving about 175 |
| 5 | L2 (transition), L3, L6 | 135 + 64 + 85 | none | 0 | Light touch. Reduce L2 to about 60. L4 and L5 are content (cases A to C and the three states) and stay. L6 is the Figure 5.1 lead and stays. Saving about 75 |
| 6 | L2, L3 | 94 + 119 | L62 | 45 | Preview to about 90 (L3's section-by-section listing goes). Keep the recap. Saving about 125 |
| 7 | L2 | 100 | L152 | 100 | Preview to about 50. Recap to about 40, keeping the four-part summary sentence and dropping the re-quoted "about a centimetre" and "a few centimetres". Saving about 110 |
| 8 | L2, L3, L4 | 94 + 135 + 59 | L73 | 103 | Preview to about 110 (L4's section listing goes, and L3's re-description of the rail recording goes to one clause). Recap to about 40. Saving about 240 |
| 9 | L2 | 71 | Section 9.3, L41 to L51 | 1096 | Keep the preview at about 60. The conclusion is the required cut: 1096 to 400 to 600 words. See section 5 for how |

Total preview and recap words now: about 2,829. Target: about 1,150.

Priority order if an editor has to choose: cut recaps before previews, and cut
the section-by-section listings (Ch4 L3, Ch6 L3, Ch7 L2, Ch8 L4) first of all,
since the headings themselves carry that information.

---

## 3. Long captions (over 60 words)

| Caption | Location | Words | What it repeats from the prose | Action |
|---|---|---|---|---|
| Figure 2.1 | Ch2 L6 | 62 | The scene inventory of Table 2.1 and the layout sentence at L4 | Cut to about 35: name the three panels, drop the item list |
| Table 2.1 | Ch2 L12 | 74 | The printed-against-declared scaling, restated at Ch7 L6 and Ch9 L18 | Keep. This is the primary location for the 0.90 factor (1.21) |
| Figure 2.4 | Ch2 L25 | 126 | The camera-frame axis convention of L23, and the T-pose of Ch3 L60 | Cut to about 55. The "defined from behind the camera" explanation and the module-name aside belong in Appendix D if anywhere |
| Figure 2.5 | Ch2 L33 | 106 | The frame list of L23 to L30 and the transformation table at L34 to L44 | Cut to about 50 after the Figure 2.5 and 2.6 merge in section 4 |
| Figure 2.6 | Ch2 L66 | 92 | The scene description of Table 2.3 and L51 to L53 | Cut to about 45; the levelling explanation duplicates Ch6 L54 |
| Figure 3.1 | Ch3 L6 | 81 | The chapter preview at L2 and L4 | Cut to about 40; it currently narrates the whole chapter |
| Figure 3.4 | Ch3 L40 | 97 | The construction at L41 to L54 and the pitch at L166 | Cut to about 50 |
| Figure 3.5 | Ch3 L62 | 128 | The reference-configuration argument at L60 | Cut to about 55 after dropping panel (b), see section 4 |
| Figure 3.6 | Ch3 L67 | 61 | The seven-rotation description at L65 | Removed with the figure, see section 4 |
| Figure 3.7 | Ch3 L70 | 90 | The four labels at L68 and L71 | Cut to about 45 |
| Figure 4.1 | Ch4 L17 | 85 | The filter description at L15 and the detection counts at L18 | Cut to about 45 |
| Figure 4.2 | Ch4 L26 | 98 | The worked example at L45 and L46 in full | Removed or merged, see section 4 |
| Figure 5.1 | Ch5 L8 | 69 | The chapter opening at L6 | Cut to about 40 |
| Figure 5.2 | Ch5 L17 | 91 | The six detectors at L18 and L19 | Cut to about 45 |
| Figure 5.5 | Ch5 L90 | 91 | The construction at L79 to L88 | Cut to about 50 |
| Figure 6.3 | Ch6 L61 | 116 | The reading of both frames at L58 and L59 | Cut to about 50 |
| Table 7.2 | Ch7 L48 | 60 | The overlap and closing-step rules of Ch5 L20 | Cut to about 35 |
| Figure 7.10 | Ch7 L149 | 67 | The panel description at L147 | Cut to about 40 |
| Figure 9.1 | Ch9 L7 | 83 | The failure description at L5 and L8 | Cut to about 45. Also carries a stale "Section 2.2" pointer, see section 0 |
| Figure 9.2 | Ch9 L11 | 74 | The marker-loss description at L9 | Cut to about 40 |
| Figure E.2 | Appendices L138 | 88 | The lobe argument at L136 and L139 | Appendix, cut to about 50 |
| Table E.1 | Appendices L152 | 72 | The scaling paragraph at L147 | Appendix, cut to about 40 |
| Figure F.1 | Appendices L175 | 75 | The paragraph at L173, which describes the same panel | Appendix, cut the L173 paragraph instead and keep the caption |

Main-body caption saving at these targets: about 700 words.

---

## 4. Candidate figures and tables for removal or merging

| Item | Location | Reason | Cross-references to repair |
|---|---|---|---|
| Figure 2.4(a), camera frame on the sensor photograph | Ch2 L24, caption L25 | Duplicates Figure 3.2, which draws the same convention against person space where it is needed | Ch2 L23 ("Figure 2.4(a) shows this frame"), Ch3 L9. Panel (b) survives as a single-panel Figure 2.4, so Ch3 L10 and Ch6 L47 still resolve |
| Figure 2.5 and Figure 2.6 | Ch2 L32 and L65 | Both draw the world origin, the camera position and the Chapter 4 object track; merge into one two-panel figure | Ch2 L31, L33, L64, L66; Ch3 L9; Ch4 L5, L37 ("Figure 2.5 shows that low viewpoint") |
| Figure 2.8, ArUco detections | Ch2 L75 | Duplicates Figure E.1 panel for panel, on the same frame | Ch2 L74. Redirect to Figure E.1 |
| Figures 2.9, 2.10, 2.11 | Ch2 L84, L87, L90 | Three single-panel figures on the same right-wrist signal, one per filter stage; merge into one three-panel figure | Ch2 L83, L86, L89 |
| Figure 3.6, seven-DoF arm and PUMA chain | Ch3 L66 | Explains a standard robotics description, cited to [42]; Figure 3.7 carries the four angles this thesis solves | Ch3 L65, L67, L68 (the q1 to q7 labelling), Figure 3.7 caption L70. If it goes, L68 must name the four angles without the q numbering |
| Figure 3.9, the Euler convention built one rotation at a time | Ch3 L94 | Explains a standard convention that equation (3.16) already states | Ch3 L90 |
| Figure 3.3 and Figure 3.8 | Ch3 L25 and L74 | Two drawings on the same worked-example image, one showing the chain frames and one the four segments; merge into one two-panel figure | Ch3 L24, L26, L27, L73, L75, L130, L171 |
| Figure 3.5 panel (b), the avatar in the T-pose | Ch3 L61 | Duplicates Figure 2.4(b); keep panel (a), the laboratory reference pose | Ch3 L60, L62; Ch6 L47 (points at the T-pose requirement, not the figure) |
| Figure 4.2, the cleaning step around one undetected frame | Ch4 L25 | The recording holds a single undetected frame and the rule rejects nothing, so both panels differ over one row; the worked example at L45 and L46 states it in numbers | Ch4 L24, L26, L46. Fold into Figure 4.1 as a third panel or drop |
| Figure 7.2, the rail measured with a tape | Ch7 L12 | Decorative; 38.7 and 3.8 centimetres appear at Ch7 L9 and are compared against 40.90 and 3.90 at L55 | Ch7 L9 |
| Figure 7.4 and Figure 7.5, rejection timelines | Ch7 L31 and L34 | Same figure type, one per recording; merge into one two-panel figure | Ch7 L30, L33, L35, L50 |
| Table 7.8, root yaw spread per window | Ch7 L133 to L137 | Three rows, two of which report no change; Figure 7.9 and the prose at L139 carry the result | Ch7 L137, L138, L139. If the table goes, L139's "Table 7.8 shows" becomes "Figure 7.9 shows" |
| Table 7.7, the pending label table | Ch7 L123 to L125 | Placeholder with no values | Ch7 L122, L125, L126; Ch9 L14. If it goes, the pending status must move into the prose at L126 and stay explicit |
| Figure 8.1, per-stage cost bars | Ch8 L38 | Duplicates Table 8.2 row for row | Ch8 L27 ("Table 8.2 and Figure 8.1 come from the run"), L37, L39 |
| Table 8.1 and Table 8.4 | Ch8 L14 to L22 and L54 to L67 | Table 8.4's four "unchanged" rows and three "adapted" rows restate Table 8.1; merge into one table with a relation column | Ch8 L13, L22, L53, L67 ("the adapted rows are the replacements of Table 8.1") |
| Figure 6.2, four frames and three maps | Ch6 L26 | Restates Table 2.2 plus equations (6.1) to (6.3) | Ch6 L27, L28 |

Two items to leave alone: Table 5.1 (the Chapter 5 symbol table, added today and
the only index of that chapter's notation) and Table 2.2 (the transformation
index, which is what makes the Chapter 2 frame prose cuttable in 1.1 and 1.2).

---

## 5. Per-chapter word budget

Counted from the dumps, excluding `[FIGURE]` and `[MATH]` marker lines,
including captions and `TABLE |` rows.

| Chapter | Current | Target | Cut | Weighting |
|---|---|---|---|---|
| 1 Introduction | 2,649 | 1,700 | 36 percent | Carries no primary location. Literature review overlaps Ch9 9.2; Section 1.4 (265 words) is a preview of nine chapters; the five gaps at L35 to L39 and the five objectives at L43 to L47 say the same things twice, 274 plus 279 words |
| 2 Experimental Setup | 4,060 | 2,700 | 33 percent | Primary for the frames, the calibration, the chordal mean and all three filtering stages, so its method content is protected. The cuts come from 2.2.1 (932 words of prose that Table 2.2 indexes), the four long captions, and the invariance and reference-path sentences that belong to Ch4 and Ch7 |
| 3 Kinematic Modeling | 7,907 | 4,700 | 41 percent | Keeps the coordinate conventions, the model-specific equations (3.7) to (3.24), the observability limits at L124, L125 and L128, and the two numeric checks at L188. Condenses 3.1 (1,760 words, of which the homogeneous-transform and chaining explanations are standard) and 3.5 (1,668 words of printed arithmetic, where the intermediate vectors can be summarised in prose) |
| 4 Object Tracking | 3,076 | 1,850 | 40 percent | Drops the filtering re-explanation at L15, the duplicate inverse derivation at L8, and about half the worked example at L28 to L46 (1,009 words) |
| 5 Pose Recovery | 5,562 | 5,100 | 8 percent | Rewritten today. Light cut only: the transition at L2, the three long captions, and the restatement of Section 5.3's memory inside L68 and L92 |
| 6 System Integration | 4,844 | 3,050 | 37 percent | Keeps 6.1's four processes and the shared frame index, all of 6.2, and the avatar mapping of 6.3 including equations (6.4) and (6.5). Compacts the sequence-counter protocol, the cross-branch inversion, startup ordering, and the scene-building detail of 6.4 (979 words, of which the wall slab, desk slab and marker plate paragraphs are construction detail) |
| 7 Evaluation | 8,385 | 4,900 | 42 percent | Keeps every experimental condition, the reference definitions of 7.1.1, the three baselines, every quantitative finding, the negative result of 7.3.2 and the pending status of 7.3.3. Stops restating table values in prose: L88 (307 words), L71 (220 words) and L79 (220 words) each walk through numbers the tables already carry |
| 8 Real-Time Feasibility | 4,006 | 2,350 | 41 percent | Keeps the causality argument, Table 8.1, Table 8.2, Table 8.3 and the check-suite result. Drops the offline restatements at L7 to L10, the merged Table 8.4, and the re-description of the Ch6 link at L68 |
| 9 Discussion and Conclusion | 4,302 | 2,300 | 47 percent | Section 9.1 (2,633 words) is the largest single block of restated material in the thesis; it keeps its two figures, Table 9.1, and the claims that appear nowhere else (the repair's seeding dependence at L16, the depth cross-check at L18, the coverage gap between the two recordings at L14). Section 9.2 to about 400. Section 9.3 from 1,096 to 500 |
| **Total** | **44,791** | **28,650** | **36 percent** | |

How Section 9.3 reaches 500 words: keep one sentence per objective (five
sentences, about 200 words) carrying only the numbers that are the thesis's
headline results (0.97 and 2.36 centimetres on the rail line; 1.67 and 1.65
against 15.39 and 21.39 centimetres on the moving outages; 57.4 to 15.3
degrees on the torso window), keep the real-time sentence at L48 in one line,
keep the arrangement paragraph at L50 in about 120 words, and keep the closing
portability paragraph at L51 in about 90 words. Cut the per-segment loop
analysis at L47, which is Ch7 L71 restated, and the industry aside at L50.

---

## 6. Cross-chapter dependencies

A cut in the source must not leave the target unsupported, and a cut in the
target must not leave the source promising something that is gone. Listed as
(source location, target location, what is promised).

### 6.1 Forward promises from Chapters 1 and 2

| Source | Target | Promise |
|---|---|---|
| Ch1 L8 | Ch9 | That the algorithms-over-hardware assumption returns in Chapter 9. Ch9 L50 pays it. If Ch9 L50's industry aside is cut, cut this sentence too |
| Ch1 L46 (objective 4) | Ch9 9.2 | That chain-level Bayesian recovery is discussed as future work. Ch9 L39 pays it |
| Ch1 L49, L50 | Chapters 2 to 9 and Appendices A to F | The whole organization paragraph. Every chapter and appendix named must still exist under that name after the cuts |
| Ch2 L4 | Ch7 7.1.1 | That Chapter 7 defines the reference path and compares the tracked trajectory against it |
| Ch2 L17 | Ch3, Ch4, Ch5, Ch6, Ch7 | Names the chapter that develops each block of Figure 2.3. Figure 2.3's own caption repeats the promise |
| Ch2 L21 | Ch3, Ch4 | That Chapters 3 and 4 derive the transformations in full |
| Ch2 L26, L30, L43, L64 | Ch6 | That Chapter 6 brings the body into W, converts into U, and builds the scene from the calibration |
| Ch2 L29, L31, L40, L41, L42 | Ch3 | That Chapter 3 defines person space, the root frame, the shoulder and elbow frames, and gives the 4 by 4 form as equation (3.2) |
| Ch2 L49 | Ch3, Ch4 | That rotations stay matrices as in Chapter 3, and that equation (2.1) returns in Chapter 4 as a smoothing filter. Ch4 L15 pays the second half |
| Ch2 L86 | Ch5 | That gaps longer than five frames are handled by the pose recovery of Chapter 5 |
| Ch2 L89 | Ch8 | That Chapter 8 measures the lag and the angle cost of the causal filter. Ch8 L70 pays it (five frames, 0.42 to 16.07 degrees) |
| Ch2 L92 | Ch3, Ch4, Ch5, Ch7 | That the unfiltered baseline stays available for Chapter 7. Nothing in Ch7 currently uses it; either Ch7 adds a sentence or Ch2 drops the promise |

### 6.2 Forward promises from Chapter 3

| Source | Target | Promise |
|---|---|---|
| Ch3 L2, L4, L88, L106 | Ch6 6.3 | That Chapter 6 maps the thirteen angles onto the avatar and composes the shoulder matrix to read the Euler angles back |
| Ch3 L6 (Figure 3.1 caption) | Ch5 | That the recovery of Chapter 5 has already replaced failed landmarks before the solve |
| Ch3 L10 | Ch4, Ch6 | That the Unity world is anchored at the desk marker of Chapter 4 and that Chapter 6 composes the calibrated camera pose once per frame |
| Ch3 L16 | Ch4 | That Chapter 4 makes the opposite handedness choice for the object track |
| Ch3 L36, L125 | Ch9 9.1 | That the rigid-torso simplification and the nearly straight elbow return as limitations. Ch9 L22 and L16 pay them |
| Ch3 L128 | Ch5 | That the pose recovery restores the wrist from the object pose |
| Ch3 L130 | Ch5 | That no failure detector of Chapter 5 fires on the worked-example frame |
| Ch3 L166 | Ch5 and Ch7 | That the torso repair puts the hips back on their rays and that Chapter 7 reports the repaired root. **The Chapter 5 half of this promise is unpayable in V8** (section 0). Ch7 L141 to L143 pays the Chapter 7 half |
| Ch3 L190 | Ch7 | That Chapter 7 evaluates the accuracy of the angles. Ch7 7.1.2 pays it |

### 6.3 Forward promises from Chapters 4, 5 and 6

| Source | Target | Promise |
|---|---|---|
| Ch4 L10, L12 | Ch6 6.2, 6.4 | That Chapter 6 places the sensor at the calibrated pose and converts world poses into Unity axes |
| Ch4 L18 | Ch7 | That the occlusion scenario of Chapter 7 contains held runs |
| Ch4 L20 | Ch5, Ch6, Ch7 | That the recovery, the streaming and the evaluation all read the same cleaned track and carry no marker logic of their own |
| Ch4 L47 | Ch5, Ch6, Ch7 7.1 | That Chapter 5 uses the track as the independent measurement, Chapter 6 streams both products, and Chapter 7 compares against the reference path of Section 7.1 |
| Ch5 L5, L6, L8 | Ch6 and Ch7 | That Chapter 6 draws held and rebuilt joints in different colours and Chapter 7 separates measured from reconstructed frames. Ch6 L51 and Ch7 L117 pay them |
| Ch5 L10 | Ch7 and Ch9 | That Chapter 7 shows where the two torso detectors fire and Chapter 9 lists what happens when an assumption fails. Ch7 7.1.3 and Ch9 Table 9.1 pay them |
| Ch5 L43 | Ch7 | That Chapter 7 reads the accuracy of a wrist reconstructed from the offset, comparing the wrist trajectory with the reference path together with the marker trajectory. **Ch7 does not currently make that comparison**; 7.3 compares against the unmasked solve and against pending manual labels. Either Ch5 L43 softens to "Chapter 7 grades the recovered wrist" or Ch7 adds the comparison |
| Ch6 L3 | Ch7 and Ch8 | That accuracy is measured in Chapter 7 and cost in Chapter 8 |
| Ch6 L48 | Ch7 | That Chapter 7 quotes clean-frame medians for two segments, differing by at most 0.30 centimetres. Ch7 L49 quotes 24.70 and 25.80; if those numbers are cut, cut this sentence |
| Ch6 L59 | Ch7 7.3.1 | That Section 7.3.1 measures what a nearly straight arm costs the recovery. Ch7 L79 and L88 pay it |

### 6.4 Backward references that a cut could break

| Source | Target | What is relied on |
|---|---|---|
| Ch7 L79 | Ch2 Section 2.5 (written as "Section 2.4") | That the filter repairs a wrist sample at the end of the eligible run |
| Ch7 L80, L88 | Ch5 Section 5.5 final paragraph (written as "Section 5.6") | The 15 degree twist hold, the 25 degree release and the 15 degree per frame rate limit. If Ch5's L94 is trimmed, these three numbers must survive |
| Ch7 L129, L141, L142 | Ch5 (written as "Section 5.5"), parked | The ray repair, the depth memory, the depth-jump gate at 10 centimetres and the shoulder-depth gate at 15 centimetres. No V8 source |
| Ch7 L141 | Ch3 L166 | "as the worked example states on frame 533", the 32 degree pitch. If Ch3 L166 is cut below the pitch value, this breaks |
| Ch7 L144 | Ch5 L19 | The reference recording that set the failure thresholds |
| Ch8 L69, L70 | Ch7 7.4 and Ch3 3.4.2 | That the live torso repair gates the hips for the reason Section 7.4 gives, and that the azimuth is near its undefined configuration for the reason Section 3.4.2 states (Ch3 L113) |
| Ch8 L72 | Ch2 Table 2.1 | The 50 against 45 millimetre declaration |
| Ch9 L7 | Ch2 Section 2.3 (written as "Section 2.2") | The 0.50 visibility gate |
| Ch9 L13 | Ch7 7.3.1, 7.3.2 and Ch5 L19 | The 342, 154 and 304 eligible-frame counts and the reference recording's left-arm defect |
| Ch9 L15 | Ch3 L166, Ch7 7.1.3, Ch7 7.4 | The 32 degree pitch, the 30.7 and 31.3 percentages, the 24.3 degree median and the frame 632 split |
| Ch9 L16 | Ch5 (parked "Section 5.5") | The shoulder-depth gate firing on two frames of the rail recording |
| Ch9 L19 | Ch7 L101 and L102 | 12.86, 13.98 and 1.18 centimetres |
| Ch9 L46, L47, L48, L49 | Ch7 Tables 7.4 to 7.6, Ch7 7.2, Ch7 7.4, Ch8 8.2 | Every number in the conclusion. Cutting a table value in Chapter 7 or 8 without telling the Chapter 9 editor leaves an unsupported figure in the conclusion |
| Appendices L90, L95 | Ch3 3.5 and Ch2 2.5 (written as "Section 2.4") | That the filtered form of the appendix numbers appears in Table 3.1 |
| Appendices L120 | Ch3 3.1 | The axis flip |
| Appendices L133 | none since 2026-09-12 | Formerly that Chapter 9 uses the depth sample recorded beside each marker pose, paid by the Ch9 L18 cross-check. That cross-check was removed from the thesis on 2026-09-12, so nothing pays the pointer. The Appendix E.1 sentence was rewritten the same day: it now records that the branch stores the depth sample, that the pose recovery never reads it and that no analysis of the thesis reads it, and it points only to Table E.1. Do not restore a Chapter 9 target for it |
| Appendices L167 | Ch2 2.5 (written as "Section 2.4") and Ch8 | That the choice made in Chapter 2 and the real-time comparison of Chapter 8 read against Appendix F |

### 6.5 Numbers that appear in more than one chapter

An editor who changes or removes one of these must notify the others. Each is
quoted at two or more locations.

| Number | Locations |
|---|---|
| 0.97 and 2.36 centimetres, rail line | Ch7 L55, Ch7 L74, Ch9 L47, Abstract |
| 0.79 and 9.32 centimetres, designed loop | Ch7 L60, Ch7 L74, Ch9 L47 |
| 1.67 and 1.65 against 15.39 and 21.39 centimetres | Ch7 Table 7.6, Ch7 L115, Ch9 L46 |
| 57.4 to 15.3 degrees, 21.9 to 0.5 centimetres | Ch7 Table 7.8, Ch7 L139, Ch9 L49 |
| 899 of 900 frames | Ch4 L17, Ch7 L55, Ch9 L9, Ch9 L45 |
| 41 missing frames of 2099 | Ch9 L9, Ch9 L12, Ch9 L45 |
| 30.7 and 31.3 percent torso rejection | Ch7 L30, Ch7 L36, Ch9 L15, Ch9 Table 9.1 |
| 47.2 against 25.8 centimetres, upper arm | Ch7 L49, Ch9 L5, Ch9 Table 9.1 |
| 24.3 degrees measured against under 10 repaired | Ch7 L141, Ch7 L143, Ch9 L15, Ch9 Table 9.1 |
| 12.86, 13.98 and 1.18 centimetres, offset | Ch7 L101, Ch7 L102, Ch9 L19, Ch9 Table 9.1 |
| 0.23 milliseconds, recovery layer | Ch8 L41, Ch8 L73, Ch9 L48 |
| 16.7 milliseconds against a 33.3 budget | Ch8 L42, Ch8 Table 8.3, Ch9 L48 |
| 29.0 frames per second | Ch8 L42, Ch9 L48. The abstract at FrontMatter L37 says 29.6; one of the two is wrong |
| 32 degree root pitch on frame 533 | Ch3 L166, Ch6 L58 (as a pointer), Ch7 L141, Ch9 L15, Ch9 Table 9.1 |
| 342, 154 and 304 eligible frames | Ch7 L79, Ch7 L91, Ch9 L13 |
| 45 against 50 millimetres, factor 0.90 | Ch2 L12, Ch7 L6, Ch8 L72, Appendices L147. Ch9 L18 dropped 2026-09-12 with the depth cross-check; Chapter 9 prints no marker size |
