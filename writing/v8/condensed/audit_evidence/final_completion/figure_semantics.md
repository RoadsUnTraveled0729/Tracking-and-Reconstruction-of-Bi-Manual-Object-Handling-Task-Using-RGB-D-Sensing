# Figure frame semantics verification, 2026-09-12

STATUS: COMPLETE for four regenerated source figures; assembled PDF inspection is recorded separately.
GOAL: Verify Camera/Camera' terminology, parent/local frame identities and directions in Figures 2.5, 3.1, 3.2 and 6.4.
KEY FINDING: The figures now distinguish the optical-origin Camera' basis from the moving root frame L24; no coordinate, matrix or experimental value changed.
VERIFIED: All four generated PNGs were opened and visually inspected after generation. The current Chapter 3 frame constructors and equations 3.5, 3.13 and 3.14 agree with the diagram's reference/child labels.
ASSUMPTIONS/UNRESOLVED: Word-only OMML rendering and final document pagination are outside this source-figure check. The spawn-axis assumption remains unchanged.
DECISION: Apply D-073 naming and D-075 parent/local clarification using condensed-local assets.
NEXT: Inspect their placement and captions in the final assembled PDF.

## Figure 2.5: scene frame relationships

Generator: scripts/make_ch2_frames_craig_fig.py.
Image inspected: figures/ch2_fig_frames_craig.png.

The four labelled matrices are Camera/Wall T, Camera/Object T,
Camera/World T and World/Object T, using Craig left reference and described
frame indices. Their orientation blocks and marker-origin meanings agree
with build_ch2.py Table 2.2 and the Chapter 4 world chain. Raw camera input
is Camera, not Camera'. World, Object and Wall retain their own origins.
The top view applies the existing swap and levelling to positions and axis
directions only for drawing. The marker detections and source photograph
are unchanged by this naming pass. The earlier scaled metric glyph correction
is retained.

The arrows run from the reference frame's origin to the described frame's
origin, e.g. World to Object. They illustrate the pose relationship. The
labelled matrix converts point coordinates in the opposite direction,
e.g. Object coordinates to World coordinates. This distinction was sent to
the builder owner for an explicit caption statement; no arrow or matrix
was reversed to confuse these two uses.

## Figure 3.1: parent/local construction

Generator: scripts/make_ch3_flow_final_fig.py, a local copy of the V8 generator.
Image inspected: figures/ch3_fig_flow.png.

The root pose is Camera'/L24 T and its rotation is Camera'/L24 R.
L24 is the right hip, and its axes follow the hip line and torso construction
in v1/kinematics/root_frame.py:build_root_frame. The shoulder frame at L12
has the same orientation and a new origin at the right shoulder; the diagram
therefore uses L24/L12 T, matching equation 3.13. The elbow frame at L14 has
the solved shoulder rotation and the elbow origin; L12/L14 T matches equation
3.14. Root-frame expression of the upper-arm difference vector is valid
because L24 and L12 share their basis; vector expression does not require
shared origins. Points and homogeneous transformations retain their own
origins. The wrist enters the L14 frame before the elbow solve, matching
v1/kinematics/shoulder.py:solve_right_arm.

The worked chain is explicitly the right side L12/L14/L16. It does not
relabel left landmarks L11/L13/L15 or turn the model's sagittal reflection
into a proper rotation. The stale T_root, R_root, T_sh,r, T_el,r and v_local
figure labels were removed or replaced with their already-defined frame
relations. No joint angle convention was changed.

## Figure 3.2: shared camera origin

Generator: scripts/make_ch3_colocated_final_fig.py, a local copy of the
read-only V7 generator.
Image inspected: figures/ch3_fig_colocated.png.

The raw and y-up readings use the same frame-533 wrist from the existing
rail landmark CSV: Camera (-0.20, +0.11, 1.06) m and Camera'
(-0.20, -0.11, 1.06) m, rounded as before. The physical point, viewpoint,
axes and visual geometry are unchanged. Shorter x/z labels and axes-relative
text remove the original image's clipped right labels and text/axis overlap.

The figure states that Camera' is not person-centred and has the same
optical origin. F = diag(1,-1,1) changes only y, exactly as
v1/kinematics/root_frame.py:unity_from_sensor. An exact integer-matrix
check confirmed F*0 = 0, F*F = I, F.T*F = I, S*S = I; F and S each have
determinant -1. These are algebra checks, not experimental accuracy claims.

## Figure 6.4: pre-levelling conversion

Generator: scripts/make_ch6_frames_final_fig.py.
Image inspected after final wording correction: figures/ch6_fig_frames.png.

The four boxes remain Camera, Camera', World and pre-levelling Unity.
Camera' and Camera have the same optical origin and opposite y; Unity is
still reached from World by swapping coordinates 2 and 3. Camera' to Unity
undoes the flip, applies the calibrated camera pose including rotation and
translation, and applies the swap, agreeing with equation 6.2. Camera' is
not labelled as the body's L24 root, and neither Unity nor Camera' is
renamed Scene. The existing levelled/floor-translated distinction remains
in Chapter 6.

The old image banner called the whole anchor a plain rotation. Its label
now says the anchor has a proper rotation block, and the arrow explanation
explicitly includes calibrated translation. This removes a misleading
quantity description without changing the homogeneous transform. The
caption owner was informed before the final build.

## Reproduction

Run from the repository root using the thesis Python:

    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/make_ch2_frames_craig_fig.py
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/make_ch3_flow_final_fig.py
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/make_ch3_colocated_final_fig.py
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/make_ch6_frames_final_fig.py

All four commands exited zero. Shared writing/v8/figures and frozen
writing/v7 sources were not edited by this delegated figure work. The current
condensed figure generators contain no Person/Sensor frame names or
person-space terms. carry.P in the Figure 2.5 generator remains the numerical
axis-swap matrix and is not a frame symbol.

## D-076 rendered follow-up

Figures 5.1 and 5.3 received condensed-local corrections after actual PDF
review exposed shared-source labels that still named World/R_obj. See
visual_figures.md for the changes, source-image inspections and outstanding
final PDF confirmation. Both use Levelled/MappedMarker semantics from the
current Chapter 5 equations; no geometric data changed.
