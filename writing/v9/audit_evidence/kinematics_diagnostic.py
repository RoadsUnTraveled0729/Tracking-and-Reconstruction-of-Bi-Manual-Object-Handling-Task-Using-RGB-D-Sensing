#!/usr/bin/env python3
"""Read-only numerical diagnostic; synthetic checks are not tracking accuracy.

Run with PYTHONDONTWRITEBYTECODE=1 /home/luo/anaconda3/bin/python
writing/v9/audit_evidence/kinematics_diagnostic.py from any directory.
"""
import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.signal import butter, freqz
from scipy.spatial.transform import Rotation

REPO = Path(__file__).resolve().parents[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / 'v1/kinematics'))
from shoulder import solve_right_arm, solve_left_arm
from root_frame import build_root_frame, euler_unity_zxy

SEED = 3117
CASES = 1000


def rot(axis, degrees):
    vector = np.zeros(3)
    vector[axis] = np.radians(degrees)
    return Rotation.from_rotvec(vector).as_matrix()


def main():
    print('SEED', SEED, 'CASES', CASES)
    meta_path = REPO / 'v1/mediapipe/output/recording_20260831_065553_landmarks_filtered.meta.json'
    with meta_path.open() as handle:
        params = json.load(handle)['params']
    print('FILTER_PARAMS', params['butter_order'], params['cutoff_hz'], params['fs_hz'])
    b, a = butter(params['butter_order'], params['cutoff_hz'], fs=params['fs_hz'])
    frequencies = np.array([1., 2., 3., 4., 5.])
    _, response = freqz(b, a, worN=frequencies, fs=params['fs_hz'])
    amplitudes = np.abs(response) ** 2
    for frequency, amplitude in zip(frequencies, amplitudes):
        print('FILTER_HZ_AMPLITUDE_DB', frequency, amplitude, 20 * np.log10(amplitude))

    rng = np.random.default_rng(SEED)
    max_upper = max_forearm = max_elbow_z = max_mirror = max_euler = 0.
    for _ in range(CASES):
        ty = rng.uniform(-179, 179)
        tz = rng.uniform(-89, 89)
        tt = rng.uniform(-179, 179)
        ey = rng.uniform(-179, -1)
        rotation = rot(1, ty) @ rot(2, tz) @ rot(0, tt)
        upper = rotation[:, 0]
        forearm = rotation @ rot(1, ey)[:, 0]
        shoulder, elbow, observable = solve_right_arm(np.zeros(3), upper, upper + forearm, np.eye(3))
        assert observable
        reconstructed = rot(1, shoulder[0]) @ rot(2, shoulder[1]) @ rot(0, shoulder[2])
        forearm_reconstructed = reconstructed @ rot(1, elbow[0]) @ rot(2, elbow[1])[:, 0]
        max_upper = max(max_upper, np.linalg.norm(reconstructed[:, 0] - upper))
        max_forearm = max(max_forearm, np.linalg.norm(forearm_reconstructed - forearm))
        max_elbow_z = max(max_elbow_z, abs(elbow[1]))
        mirror = np.diag([-1, 1, 1])
        left_shoulder, left_elbow, left_observable = solve_left_arm(
            np.zeros(3), mirror @ upper, mirror @ (upper + forearm), np.eye(3))
        assert left_observable
        max_mirror = max(max_mirror, np.max(abs(left_shoulder - shoulder)), np.max(abs(left_elbow - elbow)))
        root = Rotation.random(random_state=rng).as_matrix()
        euler = euler_unity_zxy(root)
        rebuilt = rot(1, euler[1]) @ rot(0, euler[0]) @ rot(2, euler[2])
        max_euler = max(max_euler, np.max(abs(root - rebuilt)))
    print('RANDOM_1000_MAX_ERR_upper_forearm_ez_mirror_euler',
          max_upper, max_forearm, max_elbow_z, max_mirror, max_euler)

    for x in [90., -90.]:
        rotation = rot(1, 40.) @ rot(0, x) @ rot(2, 25.)
        euler = euler_unity_zxy(rotation)
        rebuilt = rot(1, euler[1]) @ rot(0, euler[0]) @ rot(2, euler[2])
        print('GIMBAL_CORRECT', x, euler, np.max(abs(rotation - rebuilt)))
        # Represent exact gimbal-lock zeros, removing floating trigonometric remnants.
        rotation[np.abs(rotation) < 1e-14] = 0.
        printed_x = np.degrees(np.arcsin(-rotation[1, 2]))
        printed_y = np.degrees(np.arctan2(rotation[0, 2], rotation[2, 2]))
        incomplete = rot(1, printed_y) @ rot(0, printed_x)
        print('GIMBAL_EQ317_ZONLY', printed_x, printed_y, np.max(abs(rotation - incomplete)))

    up = np.array([0., 1., 0.])
    marker_up = rot(2, 30.) @ up
    print('PLUMB_WALL_MARKER_ROLL_DEG', np.degrees(np.arccos(up @ marker_up)))


if __name__ == '__main__':
    main()
