# A3. Pipeline A — blocked-landmark handling (chain fallback)

Occlusion is the normal case in a bimanual task — the carried object,
the person's own arms, and the image border all block landmarks. This
stage guarantees that a blocked landmark costs exactly the joints it
carries information for, and nothing more, while every affected output
is *declared* rather than silently degraded.

Implementation: the extractor gate in
`mediapipe/extract_landmarks_to_csv.py`, the solver wrapper in
`kinematics/occlusion.py` (`ChainFallbackSolver`), the PSA5 stream
packet, and `kinematics/validate_occlusion.py`.

## 1. The three failure modes of a blocked landmark

1. **Hallucination.** MediaPipe outputs a position for every landmark,
   occluded or not; the per-landmark visibility score is the only
   signal that the position is a guess (A1 §2). Before this stage the
   score was written to the CSV and never read — a blocked wrist
   silently fed a wrong 3-D point into the solve.
2. **Depth holes.** The depth image returns 0 at the sampled pixel
   (occluder edges, dark/specular surfaces), killing an otherwise good
   landmark.
3. **Whole-frame loss.** The old policy dropped the entire frame when
   any of the 8 landmarks was missing: a blocked left wrist killed the
   root and the right arm too.

The design answer to (1) and (2) is A1's gating — **convert "wrong"
into "missing"** (visibility gate $v \ge 0.5$, 5×5 nonzero-median
depth, `_src` provenance column). The answer to (3) is the chain
fallback below. The landmark filter's bounded gap fill (A1 §3.2)
handles only short gaps (≤ 5 frames, both endpoints known); longer
gaps deliberately stay missing — they are the fallback's job, in angle
space, not data to invent in point space.

## 2. Chain fallback: hold the ANGLE, not the point

The kinematic chain is traceable — every landmark has a parent:

$$
\text{L23/L24 (hips)} \;\to\; \text{root frame} \;\to\;
\text{shoulders (11/12)} \;\to\; \text{elbows (13/14)} \;\to\; \text{wrists (15/16)}.
$$

**Rule: a joint whose landmarks are blocked holds its last valid
angle; every joint whose landmarks survive keeps solving live.**
Children of a held joint are implicitly reconstructed by the parent
chain's forward kinematics with fixed bone lengths.

Why hold the *angle* rather than the last valid 3-D *point*:

- A held angle keeps the reconstruction on the reachable manifold —
  bone lengths stay exact, and the held limb still **moves** with its
  live parents (if the torso turns while a wrist is blocked, the held
  elbow angle carries the forearm along). A held point does neither: it
  freezes a world position that immediately becomes inconsistent with
  the moving parent chain and corrupts every frame derived from it.
- The error of a held angle is bounded by the true joint motion during
  the block (joint angular velocity × hold duration, D1 §6) — the
  *unavoidable* information loss — whereas a held point adds geometric
  inconsistency on top of that same loss.

### 2.1 Observability accounting

What each blocked landmark costs (and nothing more):

| blocked landmark | joints that hold | joints that stay live |
|---|---|---|
| wrist (15/16) | that arm's twist + elbow (3 DOF) | root, both swings, other arm |
| elbow (13/14) | that whole arm (5 DOF) | root, other arm |
| one shoulder | that arm; root switches its tilt reference to the **other** shoulder | root, other arm |
| one hip | root (3 DOF) | both arms, solved against the held root |
| everything | all 13 angles | — |

The shoulder substitution works because the root construction (A2 §2)
uses the reference shoulder only to select the coronal plane — its
component along the hip line is discarded by the cross product — so the
left shoulder substitutes for the right with a measured deviation of
≤ 1.53° on real data (true shoulder-line asymmetry, not a construction
error).

The straight-elbow twist degeneracy (A2 §5.3) unifies with occlusion
under the same rule: *unobservable ⇒ hold last valid* — one mechanism
covers both geometric and visibility-driven information loss.

## 3. Honesty: the per-joint live mask

The PSA5 stream packet carries a per-joint live mask (root, R swing,
R twist, R elbow, L swing, L twist, L elbow). The Unity receiver keeps
posing held joints from the held angles but marks held bones with red
markers — the reconstruction never pretends a held joint is measured.
The same convention propagates to Pipeline B's object stream (held
frames carry `live=0`, B1 §8) and into every accuracy analysis, which
can therefore condition on measured-only frames.

## 4. Validation — 33/33 exact checks

Method: take the fully verified recording (A2 §9), **mask** landmarks
over known frame ranges (`make_masked_dataset.py`), rerun the full
pipeline, and compare against the unmasked solve — which is ground
truth for exactly what the fallback should reproduce:

| scenario (frames) | expected behavior | result |
|---|---|---|
| R wrist 3-frame gap in raw (300–302) | the *filter* repairs it; nothing holds | wrist within 0.30 mm, angles within 0.08° |
| R wrist 45 fr (400–444) | twist+elbow hold; swing/root/left live | live joints exact (0.0); hold constant; recovery exact |
| R elbow 45 fr (500–544) | whole right arm holds; rest live | exact |
| L hip 30 fr (600–629) | root holds; arms live **against the held root** | arms match an independent recompute exactly |
| R shoulder 30 fr (750–779) | root live via LEFT shoulder; R arm holds | root ≤ 1.53° dev; left arm exact vs the alternate root |
| whole pose 10 fr (700–709) | all 13 angles hold | exact hold + exact recovery |
| gate consistency | `_src`=1 ⟺ empty cells ∧ $v<0.5$ | 19/19 cells |

Every scenario outputs on **899/899 frames** (the old whole-frame-drop
policy lost frames). Held-joint "drift" during gaps (1.4–7.8°) equals
the true motion that occurred while blocked — the declared price of
holding, not an error. On the unmasked recording the fallback changes
nothing except the warm-up: frames 0–8 hold the left arm at rest (the
hallucinations of §1 removed), frame 9 recovers swing, frames 10+ are
fully live.

## 5. Reproduce

```bash
cd kinematics
python make_masked_dataset.py
python validate_occlusion.py    # 33 checks, all exact
```
