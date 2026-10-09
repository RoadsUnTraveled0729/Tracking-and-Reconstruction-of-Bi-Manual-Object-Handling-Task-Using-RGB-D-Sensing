# Camera-frame terminology and equation verification

D-073 implements the author's latest specific naming: {Camera} is the raw
camera optical frame and {Camera'} is the y-up camera frame. The two share
one optical origin; Camera' differs only by F = diag(1,-1,1). It is not
person-centred. {World}, {Object}, {Unity}, {Levelled}, {Scene} and the
landmark-named local frames retain their distinct identities.

## Prerequisite verified before editing

Independent inspection of Chapters 2, 3, 5 and 6, the delivered DOCX, and
v1/kinematics/root_frame.py found no conflicting frame-P meaning. The body
solver's initial coordinate conversion flips y and applies no translation.
Chapter 5 reverses this flip before applying the camera calibration; the
Unity anchor does the same. The moving torso frame is {L24}, not Camera'.

Unrelated P symbols include Craig position vectors, the swap matrix in
carry.py, code paragraph tags and other local variables. They were not
renamed. Raw files, frozen implementations and old decision records remain
unchanged as provenance.

## Parent and local coordinates

A proper relation written with A as its left superscript and B as its left
subscript describes B relative to A. Multiplying its rotation by vector
components in B gives components in A. A point between different origins
requires the translation as well: the 4 by 4 transform multiplies [P; 1].
Inversion reverses this direction. Equal orientations do not imply equal
origins: the torso and shoulder frames can share axes while remaining
separate frames at different landmarks.

The independent equation audit is
[audit_evidence/final_completion/parent_local_review.md](audit_evidence/final_completion/parent_local_review.md).
It checks the equations and actual source paths, not merely symbol spelling.
The full-precision Chapter 3 chain reproduces the pinned elbow to numerical
precision. The final frame verifier also checks the Chapter 5 swap/levelling
chain and its inverse against stored data.

F and S are handedness-changing maps, not Craig proper rotations. The marker
conjugation changes both reference and marker bases; levelling and the rig
anchor change the reference basis alone. Rotation operators such as the
un-swing retain their operator classification. Equation 6.5 still depends on
the explicitly stated spawn-axis assumption; no inspection here proves it.

## Changed current sources

Chapters 2, 3, 4, 5, 6, 7 and 8, Appendix camera notation, and the front-matter
glossary use Camera/Camera'. Chapter 3 equation 3.1 shows both point frames
explicitly. Chapter 2's introductory homogeneous point equation now includes
the fourth coordinate. Captions, tables, coordinate origins and Craig frame
slots were updated together. Chapter 10 remains the approved text.

The current figures use condensed-local generators; old shared figures remain
available for their separate non-condensed builds. Figure labels and captions
are checked together. See figure_semantics.md and the final visual review
records under audit_evidence/final_completion.

## Whole-repository search and retained occurrences

verify_camera_frame_terminology.py checks the assembled DOCX, actual embedded
figure hashes and all repository py/md/cs/txt files, including ignored old
thesis drafts. It classifies hits instead of erasing historical evidence.
The exact exclusions and matching file/line records are in
[audit_evidence/final_completion/stale_repository_terms.txt](audit_evidence/final_completion/stale_repository_terms.txt).

Remaining old vocabulary belongs to frozen v1/shared Unity, archived drafts,
non-condensed builds, historical review/decision records and diagnostic
implementation names. The three current-builder matches are historical
revision docstrings in build_ch3.py and build_ch5.py, superseded by their D-073
notes. The current ch6_numbers diagnostic labels were updated. Search-pattern
literals in the verifier deliberately contain the old words they detect.
These are reported exclusions, not a claim that the whole repository contains
zero old text. No remaining current printed frame-P meaning is accepted.

## Remaining QA

Native Word upright rendering needs the author's Word installation. The PDF
is checked separately using rendered pages, including Camera' primes, long
semantic frame names and parent/local transformation chains. The approval
date remains an administrative placeholder until the actual date is known.
