"""Chapter 6 scenario numbers from the pinned filtered object track.

Everything already pinned (offset stats, grip vectors, residuals, validator
checks) is quoted from analyze_object_offset_output.txt /
validate_*_output.txt. This script computes only the scenario TIMELINE
facts for 6.1 that are not printed anywhere: height above the tabletop,
the parked interval, speed vs the motion gate, cumulative rotation, and
hand-passing counts implied by the pinned nearest-wrist fractions are NOT
recomputed (no wrist data here). All from
aruco/dataset/recording_20260224_083945_object_world_filtered.csv +
scene_calibration.json.
"""
import json

import numpy as np
import pandas as pd

ROOT = "/home/luo/Desktop/New_SandBox"

calib = json.load(open(f"{ROOT}/aruco/dataset/scene_calibration.json"))
sg = calib["scene_geometry"]
df = pd.read_csv(
    f"{ROOT}/aruco/dataset/recording_20260224_083945_object_world_filtered.csv")

p0 = np.asarray(sg["tabletop_point_world"], float)     # a point on the tabletop
P = df[["tx", "ty", "tz"]].to_numpy()
t = df["time_s"].to_numpy()

# the tabletop is perpendicular to the desk marker normal (world z), NOT to
# gravity (the desk stand is tilted 4.75 deg) -> height along world z
h = (P - p0)[:, 2]
print(f"frames {len(df)}, duration {t[-1]:.1f} s at "
      f"{1/np.median(np.diff(t)):.1f} fps")
print(f"marker height above tabletop: min {100*h.min():.1f} cm, "
      f"max {100*h.max():.1f} cm")

rest = h < 0.06                                        # same 6 cm split as the offset analysis
print(f"resting (h < 6 cm): {rest.sum()} frames; "
      f"resting-height median {100*np.median(h[rest]):.1f} cm "
      f"(half cube edge = 3.5 cm)")
print(f"carried-height band (h >= 6 cm): p5 {100*np.percentile(h[~rest],5):.0f} "
      f"cm, p95 {100*np.percentile(h[~rest],95):.0f} cm")

# the single parked stretch: the longest contiguous resting run
runs, s = [], None
for i, r in enumerate(rest):
    if r and s is None:
        s = i
    elif not r and s is not None:
        runs.append((s, i - 1)); s = None
if s is not None:
    runs.append((s, len(rest) - 1))
a, b = max(runs, key=lambda ab: ab[1] - ab[0])
print(f"longest parked stretch: frames {a}..{b}, "
      f"t = {t[a]:.1f}..{t[b]:.1f} s ({t[b]-t[a]:.1f} s)")

# travel + speed vs the 3 cm / 7-frame motion gate
step = np.linalg.norm(np.diff(P, axis=0), axis=1)
print(f"total path length {step.sum():.2f} m")
W = 7
disp = np.linalg.norm(P[W - 1:] - P[:-(W - 1)], axis=1)
moving = disp > 0.03
print(f"motion gate (>3 cm over {W} frames = 0.23 s): "
      f"{moving.sum()} windows flagged in motion")

# cumulative rotation along the track (geodesic between successive R)
R = df[[f"r{i}{j}" for i in (1, 2, 3) for j in (1, 2, 3)]].to_numpy()
R = R.reshape(-1, 3, 3)
ang = []
for i in range(1, len(R)):
    d = R[i - 1].T @ R[i]
    ang.append(np.degrees(np.arccos(np.clip((np.trace(d) - 1) / 2, -1, 1))))
ang = np.array(ang)
print(f"cumulative rotation along the track: {ang.sum():.0f} deg "
      f"(max single step {ang.max():.2f} deg)")

# net orientation change start -> end
d = R[0].T @ R[-1]
net = np.degrees(np.arccos(np.clip((np.trace(d) - 1) / 2, -1, 1)))
print(f"net orientation change first->last frame: {net:.0f} deg")

print(f"\nheld frames (detected=0, bridged or trailing): "
      f"{(df.detected == 0).sum()} of {len(df)}")
