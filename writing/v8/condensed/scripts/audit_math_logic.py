"""Reproduce analytical checks for MATH_LOGIC_REVIEW.md.

These are constructed mathematical examples, not new recording results.
Thesis constants: arm lengths 0.317/0.205 m (Section 5.6), Butterworth
order 4/cutoff 3 Hz (Section 2.5), and a nine-sample median (Appendix F).
The other numbers define counterexamples, not proposed tuning values.
This script only reads repository files and prints JSON.
"""

import ast
from collections import deque
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.ndimage import median_filter
from scipy.signal import butter, sosfiltfilt, sosfreqz
from scipy.spatial.transform import Rotation


ROOT = Path(__file__).resolve().parents[4]
THESIS = ROOT / "writing/v8/Thesis_V8_Condensed.docx"
results = {"thesis_sha256": hashlib.sha256(THESIS.read_bytes()).hexdigest()}

# A translated straight trajectory has no fitted-line residual even when
# its absolute position is wrong. The offset is deliberately one metre.
truth = np.column_stack((np.linspace(0, 1, 11), np.zeros((11, 2))))
observed = truth + [0, 1, 0]
centre = observed.mean(axis=0)
_, _, vt = np.linalg.svd(observed - centre, full_matrices=False)
perp = observed - centre - np.outer((observed - centre) @ vt[0], vt[0])
results["fitted_line_counterexample"] = {
    "maximum_line_residual_m": float(np.linalg.norm(perp, axis=1).max()),
    "absolute_error_m": float(np.linalg.norm(observed - truth, axis=1).min()),
}

# Clipping the cosine keeps an elbow finite but cannot create the missing
# intersection of two spheres for an unreachable wrist.
length1, length2 = 0.317, 0.205
reach_checks = []
for radius in [0.05, 0.5071, 0.6]:
    cosine = (length1**2 + radius**2 - length2**2) / (2 * length1 * radius)
    c = float(np.clip(cosine, -1, 1))
    elbow = length1 * np.array([c, np.sqrt(max(0, 1 - c*c)), 0])
    wrist = np.array([radius, 0, 0])
    reach_checks.append({
        "wrist_radius_m": radius,
        "unclipped_cosine": float(cosine),
        "clipped_cosine": c,
        "actual_forearm_m": float(np.linalg.norm(wrist - elbow)),
        "required_forearm_m": length2,
        "reachable": bool(abs(length1-length2) <= radius <= length1+length2),
    })
results["ik_reachability"] = reach_checks

# The exact digital response uses the appendix's 29.98 Hz sample rate.
sos = butter(4, 3, fs=29.98, output="sos")
freqs = np.array([1., 2., 3., 4., 5.])
_, response = sosfreqz(sos, worN=freqs, fs=29.98)
results["forward_backward_butterworth"] = [
    {"frequency_hz": float(f), "amplitude_gain": float(abs(h)**2),
     "gain_db": float(20*np.log10(abs(h)**2))}
    for f, h in zip(freqs, response)
]

# Zero phase does not preserve extrema when harmonics are attenuated
# differently. A long record keeps the selected central peak off edges.
t = (np.arange(1801)-900)/30
signal = np.cos(2*np.pi*t) + 0.5*np.sin(8*np.pi*t)
filtered = sosfiltfilt(butter(4, 3, fs=30, output="sos"), signal)
window = np.flatnonzero(abs(t) <= 0.2)
results["zero_phase_peak_counterexample"] = {
    "signal": "cos(2*pi*t) + 0.5*sin(8*pi*t)",
    "raw_local_peak_s": float(t[window[np.argmax(signal[window])]]),
    "filtered_local_peak_s": float(t[window[np.argmax(filtered[window])]]),
}

ramp = np.arange(21, dtype=float)
med = median_filter(ramp, size=9, mode="nearest")
clean_window = np.arange(9, dtype=float)
spiked_window = clean_window.copy()
spiked_window[0] = 1000
results["median_counterexamples"] = {
    "monotone_ramp_interior_unchanged": bool(np.array_equal(med[4:-4], ramp[4:-4])),
    "clean_window": clean_window.tolist(),
    "one_spike_window": spiked_window.tolist(),
    "clean_median": float(np.median(clean_window)),
    "spiked_median": float(np.median(spiked_window)),
}

# In the orthographic limit, opposite planar tilts have equal images but
# their normals can remain widely separated.
square = np.array([[-1,-1,0], [1,-1,0], [1,1,0], [-1,1,0]], dtype=float)
rp = Rotation.from_euler("y", 30, degrees=True).as_matrix()
rm = Rotation.from_euler("y", -30, degrees=True).as_matrix()
results["planar_ambiguity_counterexample"] = {
    "maximum_orthographic_image_difference": float(abs((square@rp.T)[:,:2]-(square@rm.T)[:,:2]).max()),
    "normal_separation_deg": float(np.degrees(np.arccos(np.clip(rp[:,2]@rm[:,2], -1, 1)))),
}

# Verify Chapter 6's anchor/factorization for deterministic rotations.
flip = np.diag([1., -1., 1.])
swap = np.array([[1.,0,0], [0,0,1], [0,1,0]])
rotations = Rotation.from_euler("xyz", [[0,0,0], [15,31,-42], [-80,20,179]], degrees=True).as_matrix()
anchor_errors = []
for rotation in rotations:
    anchor = swap@rotation@flip
    anchor_errors.append(float(abs(anchor-(swap@rotation@swap)@(swap@flip)).max()))
    assert np.allclose(anchor.T@anchor, np.eye(3))
    assert np.isclose(np.linalg.det(anchor), 1)
assert np.allclose(swap@flip, Rotation.from_euler("x", -90, degrees=True).as_matrix())
results["chapter6_anchor"] = {"factorization_max_residual": max(anchor_errors), "proper_rotation": True}

# Run the actual buffer class without importing launcher dependencies or
# opening shared memory. At one requested render time, sources can differ.
tree = ast.parse((ROOT / "v2/integration/v2_integrate.py").read_text())
definition = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "StreamBuffer")
namespace = {"deque": deque, "FRAME_S": 1/30, "MEASURED": 0, "INTERP": 1, "HELD": 2, "BLEND": 3}
exec(compile(ast.Module(body=[definition], type_ignores=[]), "StreamBuffer excerpt", "exec"), namespace)
buffer = namespace["StreamBuffer"]
person = buffer(0.1, 0, lambda a,b,s: (1-s)*a+s*b)
obj = buffer(0.1, 0, lambda a,b,s: (1-s)*a+s*b)
person.add(0., 0, 0.)
obj.add(1., 30, 1.)
p_out, o_out = person.emit(1.), obj.emit(1.)
results["same_render_time_different_source_times"] = {
    "requested_render_time_s": 1., "person_source_time_s": 0., "object_source_time_s": 1.,
    "person_state": p_out[0], "object_state": o_out[0],
    "person_source_frame": p_out[2], "object_source_frame": o_out[2],
}

# Printed appendix arithmetic, evaluated at its displayed precision.
fx, fy, cx, cy = 607.56128, 607.01508, 323.93756, 248.01741
results["appendix_deprojection_m"] = {
    "wrist": [1.060*(209-cx)/fx, 1.060*(308-cy)/fy, 1.060],
    "object_depth_point": [0.986*(200-cx)/fx, 0.986*(341-cy)/fy, 0.986],
}
skew = np.array([[0,-.029302,-.003507], [.029302,0,-.999564], [.003507,.999564,0]])
skew2 = np.array([[-.000871,-.003506,.029290], [-.003506,-.999988,-.000103], [.029290,-.000103,-.999141]])
printed = np.array([[.998259,-.008185,.058415], [-.005833,-.999171,-.040308], [.058697,.039897,-.997479]])
results["appendix_rounded_rodrigues"] = {
    "maximum_entry_discrepancy_from_printed_scalars": float(abs(np.eye(3)+.0401*skew+1.9992*skew2-printed).max()),
    "claimed_entry_bound": 0.00001,
}

print(json.dumps(results, indent=2, sort_keys=True))
