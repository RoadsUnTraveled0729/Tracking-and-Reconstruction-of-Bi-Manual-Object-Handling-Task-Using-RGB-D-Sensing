# Recording protocol: two-hand rail take (R7, hand-over on the rail)

STATUS (2026-09-09): RECORDED AND ACCEPTED. The user recorded eight
takes on the night of 2026-09-08/09 with
~/Desktop/ENSC498/record_realsense_bag_pose.py (the recorder with a
MediaPipe and hip-depth preview) and named the last one,
recording_20260909_000024 (1499 frames, 50 s), as the one to use.
Precondition: torso PASS, both wrists PASS (right 99.3 percent, gap
0.2 s). One deviation from the setup below: the wall card had shifted
(7 cm nearer, tilted 44 deg), so the calibration carries the gravity of
the 2026-08-31 take (E-034). Analysis: eval/reports/r7_handover.md;
thesis Section 7.7. The right hand slid the cube about 30 cm of the
42 cm slide before the left hand took over, farther than the "about the
middle" of step 3 below; reported as recorded.

Purpose (supervisor comment C50, 2026-09-08): add the second arm to
the rail task. The right hand slides the cube to about the middle of
the rail, the left hand takes it over and slides it to the far end.
The take becomes a second recording in Chapter 7; the one-hand
recording of 2026-08-31 stays the thesis recording everywhere else
(writing/v8/PROF_COMMENTS_ROUND6.md).

## Setup (the same as 2026-08-31)

- Working area on grid paper on the desk; rail inside it, lying flat,
  levelled with the spirit level; desk marker (id 2) at the world
  origin on the desk; wall marker (id 0) on the wall behind; object
  marker on the cube face turned to the sensor.
- Camera on its support at the desk edge, chest height, aimed so that
  the subject, the desk, the rail and all three markers stay in view.
  Both arms must stay inside the frame for the whole take; on the
  one-hand take the idle left arm hung partly out of frame and was
  rejected on 94 percent of the frames.
- Cube parked at its start position on the desk, marker facing the
  sensor, before the recording starts. The scene calibration averages
  the first ten detections of the static markers and seeds the tabletop
  from the desk card and the parked object card.
- Same clothing convention if possible (jacket sleeve with a cuff seam
  on the right; bracelet on the left), in case wrist labels are wanted
  later.

## The task (slow, about 40 s)

1. Stand still with both hands away from the cube for about three
   seconds (the parked stretch).
2. Right hand: grasp the cube, carry it straight back to the foot of
   the rail, lift it onto the rail.
3. Right hand: slide it along the rail to about the middle (the rail
   is 38.7 cm long, so about 19 cm in), then hold it still.
4. Left hand: grasp the cube from the other side. Right hand: let go
   and move away. Keep the marker face uncovered as far as the grip
   allows; if a finger covers it, that is a result, not a fault.
5. Left hand: slide the cube to the far end of the rail, release, move
   the hand away, stand still for two seconds.

## Record

The recorder is the one used for every earlier take:
~/Desktop/ENSC498/record_realsense_bag.py (10 s preview, then it
records for RECORD_TIME seconds, currently 50; q stops early). It writes
recordings/recording_<date>_<time>.bag in the folder it is run from.

    cd ~/Desktop/ENSC498
    python record_realsense_bag.py

Start the task when the red REC text appears. Press q after the final
still stretch if the 50 s have not run out.

Then copy the bag into the repository video folder (gitignored):

    cp ~/Desktop/ENSC498/recordings/recording_<date>_<time>.bag \
       ~/Desktop/New_SandBox/Video/

Note (2026-09-23): existing archive files were renamed to descriptive
names; see eval/recordings_archive/README.md.

## Check before leaving the room

    cd ~/Desktop/New_SandBox
    python v1/mediapipe/extract_landmarks_to_csv.py --bag Video/<stem>.bag
    python eval/inspect/check_tracking_precondition.py --stem <stem>

Read the output as follows:
- The first line must report about 30 fps and a person-present span
  covering the whole take. Pose on far fewer frames than the take
  holds (the rejected take of 2026-08-31 had 661 of 900) means retake.
- Torso must be PASS (left_hip, right_hip, left_shoulder,
  right_shoulder).
- The wrist lines will not reach 95 percent, because each hand rests
  for half the take; that FAIL is expected. What matters is that each
  wrist was seen while it worked: coverage well above the 12 percent
  of the idle arm on the one-hand take, roughly 40 percent or more
  each, and no single gap longer than a few seconds.
- If the torso fails or a working wrist is barely seen, record again.

Report the stem (recording_<date>_<time>) when done. The rest of the
chain (eval/README.md, pinned chain, plus the hand-over analysis and
the Chapter 7 section) runs from the workstation afterwards.
