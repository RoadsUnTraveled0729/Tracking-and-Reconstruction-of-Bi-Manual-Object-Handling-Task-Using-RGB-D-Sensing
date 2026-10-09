# Elbow joint-limit constants (E-020)

Derived from clean tracked frames of R5 and R1 (see json for full stats).

- TORSO_RADIUS_FRAC = 0.334 (elbow clearance from the pelvis->shoulder-mid axis, as a fraction of the measured shoulder width; strictest clean p1 across both recordings and sides with 20 percent slack) - the ONE implementable swivel limit, pinned in occlusion_ext.py.
- Shoulder-twist box: REJECTED by the data. R5's clean left arm carries real mass at -150..-120 deg (241 frames), beyond anatomical humeral rotation - the swing-twist tau does not map one-to-one onto humeral rotation, so a box on it would reject genuinely measured poses.
- Elbow-flexion box: unnecessary for swivel selection - flexion is identical at every point of the IK circle (cosine law), and the IK's cosine clip already bounds it by construction.
