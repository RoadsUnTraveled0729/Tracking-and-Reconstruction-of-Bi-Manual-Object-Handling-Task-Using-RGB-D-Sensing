Integration complete: CH7_VISUAL_RESTORATION_2026-09-13.md (two directories above) and pdf_layout.json record the delivered captions and placements. The suggested captions below preserve the source review.

# Chapter 7 Unity trajectory restoration

These two assets restore the existing Unity trajectory views as the proposed
replacements for Figures 7.3 and 7.4. They use the accepted native composition
and the same saved Unity screenshots. The outer legend changes `Waypoint
reference` to `Schematic scene guide` because the dashed guide was constructed
from the earlier tracked route and fitted rail line; it is not the physical
route later defined under D-035 and D-036. The outer Start/W1/W2/W3 annotations
are omitted because those earlier roles conflict with the current W1-W4
endpoint definitions. No recording was replayed, no experiment was rerun, no
trail was recomputed, and no saved Unity raster was changed.

## What the figures depict

`writing/v8/condensed/figures/ch7_unity_trajectories_r6b.png` is 1565 x 1468
pixels. It shows the saved
single-hand task intervals carry (frames 92-500), lift (501-528), and slide
(529-899). The colored trails are the object marker origin and the model wrist.
The Unity avatar and cube in each panel are posed at the last frame of that
interval. The wrist has a saved sample on all 808 displayed interval frames;
the marker origin has 807, with its one gap at frame 786.

`writing/v8/condensed/figures/ch7_unity_trajectories_r7.png` is 1511 x 1468
pixels. It shows the saved
handover intervals right hand (frames 137-863), hand-over (864-1022), and left
hand (1023-1498). The colored trails are the object marker origin and both
model wrists. The Unity avatar and cube are again posed at each interval's last
frame. Both wrists have saved samples on all 1362 displayed interval frames;
the marker origin has 1361, with its one gap at frame 741.

Neither figure contains an elbow trail. The wrist trails are model-wrist
positions classified by measured, rebuilt, or held solver state as shown by
the legends; they are not the final rendered hand-joint positions scored in
the tables.

The phase titles already use `Carry`, `Lift`, `Slide`, `Right hand`,
`Hand-over`, and `Left hand`. No panel says `grasp`, so no overlay or relabeling
was required. The captured pixels remain unchanged.

## Exact suggested captions

Figure 7.3. Single-hand rail task in the saved Unity trajectory view. The
panels show the saved marker-origin and model-wrist trails over the carry
(frames 92-500), lift (501-528) and slide (529-899) intervals; the avatar and
cube are posed at each interval's final frame. The dashed line is a schematic
scene guide, not a surveyed or registered physical path. These task-interval trails provide
qualitative context and are not the elbow and wrist samples used in Table 7.3.

Figure 7.4. Handover task in the saved Unity trajectory view. The panels show
the saved marker-origin and right- and left-model-wrist trails over the
right-hand (frames 137-863), hand-over (864-1022) and left-hand (1023-1498)
intervals; the avatar and cube are posed at each interval's final frame. The
dashed line is a schematic scene guide, not a surveyed or registered physical
path. These task-interval trails provide qualitative context and are not the arm-specific
elbow and wrist samples used in Table 7.4.

## Necessary prose scope correction

Any surrounding sentence that says Figure 7.3 plots the exact 100-frame
valid-landmark subset of Table 7.3 must be removed or replaced. Any sentence
that says Figure 7.4 plots exactly the 650 right-arm and 589 left-arm samples
of Table 7.4 must likewise be removed or replaced. A suitable shared sentence
is:

> Figures 7.3 and 7.4 provide qualitative Unity views of the saved task-interval trajectories; the rendered-error tables use separate valid-landmark frame subsets.

The Section 7.2 statement that no physical path or physical waypoint coordinate
is drawn should be scoped to the statistical object-trajectory plots. In these
restored Unity views, the dashed line remains only as a schematic scene guide.
The superseded outer waypoint labels are omitted. The physical endpoint results
remain in Tables 7.1 and 7.2. No table value or interpretation changes.

## Provenance and reproduction

`sources.json` records the output, source-composite, composition-manifest,
capture-manifest, trail, interval, and table-scope hashes. It retains the
recovery-angle CSV hashes as optional historical provenance, but those ignored
files are not required to reproduce the figures. Phase metadata and the
presence of the handover figure's held-state legend are explicit and checked
against the pinned capture records. The local composer retains the layout of
`writing/v8/condensed/scripts/make_ch7_trails_fig.py`, verifies that evidence
chain, and rebuilds the two figures from the saved screenshots under their
current names in `writing/v8/condensed/figures`:

```text
/home/luo/anaconda3/bin/python writing/v8/condensed/audit_evidence/ch7_visual_restoration/compose_unity_trajectories.py
```

Successful verification prints:

```text
PASS: composed and verified two Chapter 7 Unity trajectory figures
```
