# Marker side stays simple; the focus is the rig

User rule 2026-08-26: "we don't want to robust the aruco marker, we
want to filter it if possible, so we make the whole setup simple,
and have focus - our focus is our rig model."

- Object/ArUco problems are handled by FILTERING the track (one
  cleaning step producing one clean CSV that every consumer reads
  through the paths accessor), never by adding robustness layers,
  gates, or per-consumer logic around the marker.
- Engineering effort, new mechanisms and thesis narrative go to the
  PERSON side: the kinematic model, the solver layer, the rig
  transfer.

**Why:** the marker is a commodity input; complexity spent there
dilutes the project's actual contribution.
**How to apply:** before adding any marker-side mechanism, ask
whether a filter rule on the track achieves it; put it in
eval/common/clean_object_track.py if so.
