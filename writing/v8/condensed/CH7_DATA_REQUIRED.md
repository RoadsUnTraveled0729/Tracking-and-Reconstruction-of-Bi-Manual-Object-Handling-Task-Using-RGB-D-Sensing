# Chapter 7: Data Required

Status of 2026-09-12: the Section 7.2 blocker recorded as D-030 is
RESOLVED. The author supplied the missing measurement definitions in
D-035 and corrected the waypoint definitions in D-036. No further
object data is required from the author unless the analysis escalates
a specific ambiguity.

What the author supplied:

- The ArUco marker centre is the physical and reconstructed endpoint
  reference in both recordings, not the cube centre and not an edge.
- Physical lengths W1 to W2 of 25.5 cm, W2 to W3 of 3.5 cm and W3 to W4
  of 37.5 cm, at 1 mm resolution, applying to both recordings because
  the physical setup is identical.
- W1 to W4 are physical task phase boundaries, not arbitrary stationary
  points. W2 and W3 are single transition frames and are not required
  to contain a stationary dwell. W1 and W4 may use the mean of a clear
  stationary interval.
- Waypoint frames are determined independently for each recording from
  its own marker centre trajectory, because their frame timing differs.

The superseded request for waypoint identity, frame correspondence and
physical lengths is retained below D-036 in DECISIONS.md as provenance.
The sections that follow remain open requests; they are not blockers for
the results now being written.

## Optional data for broader human claims

These are not blockers for the captured-subset results already written:

- Complete-task statistics require a complete Unity replay export for
  each task, with frame, time_s, actual left/right elbow and wrist world
  XYZ, coordinate calibration, and synchronized raw landmark XYZ/source
  and filtered validity flags. Existing saved captures are incomplete.
- An evaluation without any root recovery requires a single-hand
  recording or reconstruction interval with trusted torso depth and
  wholly measured root output. Every retained single-hand capture frame
  currently has constrained root output. The chapter discloses this;
  it does not claim recovery-free reconstruction.

## Optional data for stronger natural-occlusion claims

The existing bracelet/watch labels support distances to those proxies.
Repeated independent clicks, repeated depth measurements and clean
proxy-to-wrist observations across orientations would be needed to
quantify reference uncertainty. A trusted anatomical reference would
be needed for anatomical accuracy. Neither is inferred from the
current proxy distances.
