"""Regression checks for validity pairing, source frame gaps and lag sign."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np
import pandas as pd

spec = importlib.util.spec_from_file_location(
    'validator', Path(__file__).resolve().parents[1] / 'integration/validate_v2_r5.py')
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def tracks(frames):
    live = pd.DataFrame({'frame': frames, 'mask': 127})
    ref = pd.DataFrame({'frame': frames, 'live_mask': 127})
    for i, name in enumerate(v.ANGLE_COLS):
        live[f'a{i}'] = np.asarray(frames) * (i+1)
        ref[name] = np.asarray(frames) * (i+1)
    for i in range(7):
        live[f'tag_{i}'] = 0
        ref[f'tag_{i}'] = 0
    return live, ref


class PairingTests(unittest.TestCase):
    def test_reference_validity_is_evaluated_at_shifted_frame(self):
        live, ref = tracks([0, 1, 2, 3])
        ref.loc[ref.frame == 1, 'tag_2'] = 1
        _, _, ids = v.paired_angles(live, ref, 1, 14, range(1, 4), [3,4,5,6,7])
        self.assertEqual(ids.tolist(), [1, 3])
        live.loc[live.frame == 3, 'mask'] = 0
        _, _, ids = v.paired_angles(live, ref, 1, 14, range(1, 4), [3,4,5,6,7])
        self.assertEqual(ids.tolist(), [1])

    def test_frame_gaps_do_not_turn_lag_into_row_offset(self):
        live, ref = tracks([0, 1, 3, 4, 7])
        a, b, ids = v.paired_angles(live, ref, 1, 127, range(7), list(range(13)))
        self.assertEqual(ids.tolist(), [1, 4])
        np.testing.assert_allclose(a[:,0]-b[:,0], 1)

    def test_both_lag_signs_recovered_with_missing_frames(self):
        for lag in (-3, 3):
            live, ref = tracks(np.arange(100))
            for i in range(13):
                live[f'a{i}'] = (live.frame-lag) * (i+1)
            live = live[~live.frame.isin([10, 11, 21, 55])]
            ref = ref[~ref.frame.isin([5, 32, 33])]
            result = v.compare_angles(live, ref)
            self.assertEqual(result['lag_frames'], lag)
            self.assertEqual(result['worst_group_median_deg'], 0)

    def test_no_measured_pairs_is_explicit(self):
        live, ref = tracks([0, 1, 2])
        ref['live_mask'] = 0
        self.assertIsNone(v.compare_angles(live, ref)['lag_frames'])

    def test_duplicate_source_frames_are_rejected(self):
        live, ref = tracks([0, 1, 1, 2])
        with self.assertRaises(pd.errors.MergeError):
            v.compare_angles(live, ref)

    def test_exact_ties_preserve_historical_ascending_order(self):
        live, ref = tracks(np.arange(30))
        for i, name in enumerate(v.ANGLE_COLS):
            live[f'a{i}'] = 0
            ref[name] = 0
        self.assertEqual(v.compare_angles(live, ref)['lag_frames'], -10)


if __name__ == '__main__':
    unittest.main()
