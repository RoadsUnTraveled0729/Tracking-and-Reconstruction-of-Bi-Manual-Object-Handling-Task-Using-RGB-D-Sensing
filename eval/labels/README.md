# Manual wrist labels (Section 7.3.3)

Frames extracted for the manual wrist labelling of the natural failure
windows, tracked in git so that a machine without the recordings (the
.bag files are not in the repository) can do the labelling.

- frames_r6b/: the rail recording (recording_20260831_065553, the thesis
  recording). 21 frames, right wrist only: frames 550 to 684 every fifth
  frame, the natural right-wrist gap while the hand slides the cube along
  the rail (Chapter 7 Section 7.1.3; the worked example of Chapter 5 uses
  frame 560 of this window), plus 5 clean frames (500, 520, 540, 700,
  720; clean_frames in meta.json) for the reference check. All 26
  labelled (cuff-seam convention) and graded.
- frames_r5/: the loop recording (recording_20260825_222315, the
  occlusion scenario). 78 frames between 1427 and 1890, left wrist on 54
  and right wrist on 24 (the set Chapter 7 Section 7.3.3 describes), plus
  7 clean frames outside the failure mask (1380, 1400, 1420 left; 1740,
  1760, 1900, 1920 right; listed under clean_frames in meta.json). The
  clean frames check the reference: on them the label is compared with
  the wrist MediaPipe measured while it was trusted, and with the object
  estimate before the failure began.

Each folder holds fNNNNN.png (colour frame), fNNNNN_depth.npy (aligned
depth, uint16, metres = value * depth_scale) and meta.json (stem, step,
depth scale, colour intrinsics, the wanted side per frame). Extracted by
eval/failure/extract_label_frames.py --stem <stem>.

Labelling: python eval/failure/label_wrists.py --dir eval/labels/frames_r6b
(then frames_r5). Left click places the wrist for the side shown, n or
space next frame, b back, s skip, u undo, j jumps to the next frame
that still needs a label, q or Esc saves and quits. The committed rail
labels are complete, including the five clean reference frames;
progress is saved after every click into labels.json in the same folder.
Needs opencv-python and numpy with a display. Commit labels.json when
done. Every label is placed by the user; no label is generated.

Where to click, one fixed mark per set, the same on every frame:
- frames_r6b: the cuff seam of the jacket sleeve, centred across the arm
  (done, 21 of 21).
- frames_r5: the wrist jewellery, the bead bracelet on the left wrist
  and the watch on the right, centred where it crosses the arm. In the
  loop task the hand wraps behind the cube, so the wrist crease itself is
  usually hidden while the jewellery on the near side of the arm stays
  in view. Skip (s) only where the cube hides the jewellery completely.
  The depth under a click on the arm edge can mix the arm with the
  background or the cube; the tool then keeps the nearest surface, marks
  the label mixed_surface and prints a warning, so re-click a few pixels
  inside the arm when the printed depth looks wrong.

Grading: python eval/failure/eval_labeled_recovery.py --stem <stem> reads
eval/labels/frames_<alias>/labels.json (or --labels FILE) plus the
pipeline inputs (landmark and object CSVs, scene calibration, the angle
CSVs of eval/output/recovery_<alias>/) that live in gitignored output
folders, so it runs on the machine that holds the recordings and their
outputs, and writes eval/reports/<alias>_recovery_labeled.{md,json}: per
frame and side the distance from the label to the object-derived wrist
estimate, MediaPipe's wrist, the held wrist, and the wrist the angles of
the plain, hold-last and recovery solves place; failure-window frames
and clean frames in separate tables.
