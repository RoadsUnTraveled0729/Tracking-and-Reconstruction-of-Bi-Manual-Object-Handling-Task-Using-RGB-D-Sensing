"""Vendored v1 oracles must stay verbatim (isolation guarantee 2).

MANIFEST.sha256 was written at copy time (master ee7079f). If a hash
check fails, the copy was edited: restore the file, never update the
manifest to match an edit.
"""
import hashlib
import sys
from pathlib import Path

import pytest

from bench import metrics as m

VENDOR = Path(__file__).resolve().parents[1] / "vendor" / "v1"


def manifest_entries():
    out = []
    for line in (VENDOR / "MANIFEST.sha256").read_text().splitlines():
        digest, name = line.split()
        out.append((name, digest))
    return out


def test_manifest_covers_expected_files():
    names = {n for n, _ in manifest_entries()}
    assert names == {"root_frame.py", "shoulder.py", "occlusion.py"}


@pytest.mark.parametrize("name,digest", manifest_entries())
def test_vendored_file_unmodified(name, digest):
    data = (VENDOR / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == digest, (
        f"vendor/v1/{name} differs from the verbatim copy; restore it")


def test_vendored_oracle_imports_and_matches_metrics_vocabulary():
    """The metric group order IS the v1 live-mask bit order; catch any
    drift between bench/metrics.py and the vendored oracle."""
    sys.path.insert(0, str(VENDOR))
    try:
        import occlusion  # vendored, flat imports resolve within VENDOR
    finally:
        sys.path.remove(str(VENDOR))
    assert tuple(occlusion.BIT_NAMES) == m.GROUP_NAMES
    assert occlusion.MASK_ALL == (1 << len(m.GROUP_NAMES)) - 1

    solver = occlusion.ChainFallbackSolver()
    angles, mask = solver.solve({})
    assert angles.shape == (len(m.ANGLE_NAMES),)
    assert mask == 0
    # rest pose before any valid sample: root (0, 180, 0), arms 0
    assert list(angles[:3]) == [0.0, 180.0, 0.0]
    assert not angles[3:].any()
