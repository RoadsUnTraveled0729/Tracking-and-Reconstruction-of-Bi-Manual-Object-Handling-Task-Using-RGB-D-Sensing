# Video shot list

Currency note (2026-10-08): This is the original three-video proposal for
the retired 20-minute presentation. Its placeholders and slide references
are historical. The delivered deck and current playback/rehearsal limits
are documented in [the final presentation README](defense_2026/README.md).

Three videos, all placeholders in the deck. Each under 30 seconds; videos
count toward the 20-minute budget. Record at 1920x1080 or the source's
native size; no titles, no transitions, no music.

## VIDEO 1: the recorded session, raw camera view

- Slide: after "Experimental setup" (deck page 11).
- What to film: screen recording of the evaluation recording's colour
  stream playing back (realsense-viewer 2D view, or a plain player over
  exported frames). No overlays.
- Target duration: 20 to 25 s. Play the recording at normal speed from the
  first lift through the first hand-over; cut before the parked stretch.
- MUST be visible in frame: the person, the desk surface, the carried cube
  with its marker, both hands, the wall marker in the background.
- Purpose: the committee sees the actual raw input once before any
  processing claims are made.

## VIDEO 2: real video beside the Unity reconstruction

- Slide: after "Results II: the bimanual task" (deck page 14).
- What to film: screen recording, side by side and time-synchronized: the
  real colour video on one half, the integrated Unity reconstruction on
  the other (the scene of thesis Figure 5.7, with the sensor-view inset).
- Target duration: 25 to 30 s. Must include: one lift off the desk, a
  carry with visible turning, one hand-over, and the parking on the desk.
- MUST be visible in frame: the avatar tracking the person, the cube at
  the avatar's hand, the desk and wall in the reconstruction, and the
  same events in the real video half.
- Purpose: the qualitative fidelity claim of Chapter 6.6, shown moving.

## VIDEO 3: occlusion in action

- Slide: after "Failure cases I: what breaks" (deck page 17).
- What to film: screen recording of the Unity scene during (a) one
  synthetic occlusion scenario replay (red marker spheres appear on
  exactly the held joints while the rest keeps tracking), and (b) the
  trailing marker gap of the evaluation recording (cube tinted red while
  its pose is held).
- Target duration: 15 to 20 s total (about 10 s per case, hard cut
  between them).
- MUST be visible in frame: the red held-joint spheres appearing and
  disappearing; the cube turning red while the hand covers the marker,
  and returning to normal on re-acquisition.
- Purpose: failure shown honestly, in the system's own vocabulary.
