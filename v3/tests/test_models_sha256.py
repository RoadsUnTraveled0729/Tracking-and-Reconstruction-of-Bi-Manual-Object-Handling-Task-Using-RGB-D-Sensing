"""Model file pinning (D-023): every end2end.onnx referenced by
configs/default.json or configs/model_variants.json is listed in
configs/models.sha256 with the same hash as the variant table, and
every file listed there that is on disk hashes to its pinned value.

A file that is absent is skipped with its path in the reason (models
are not in git); a file that is present with a wrong hash always
FAILS.
"""
import json
from pathlib import Path

import pytest

from detector.factory import sha256_file

V3_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = V3_ROOT.parent
CONFIGS = V3_ROOT / "configs"
MODELS_DIR = V3_ROOT / "models"   # models.sha256 paths are relative to it


def _pinned():
    out = {}
    for line in (CONFIGS / "models.sha256").read_text().splitlines():
        if not line.strip():
            continue
        digest, rel = line.split(None, 1)
        out[rel.strip()] = digest
    return out


def _variants():
    with open(CONFIGS / "model_variants.json") as f:
        return json.load(f)["variants"]


def _referenced():
    """{models-dir-relative path: expected sha256 or None}."""
    refs = {}
    with open(CONFIGS / "default.json") as f:
        mo = json.load(f)["model"]
    for key in ("pose_onnx", "det_onnx"):
        if mo.get(key):
            refs.setdefault(mo[key], None)
    for name, v in _variants().items():
        for role in ("pose", "det"):
            if v[f"{role}_onnx"]:
                refs[v[f"{role}_onnx"]] = v[f"{role}_sha256"]
    prefix = "v3/models/"
    out = {}
    for path, digest in refs.items():
        assert path.startswith(prefix), f"onnx outside v3/models: {path}"
        out[path[len(prefix):]] = digest
    return out


def test_every_referenced_onnx_is_pinned():
    pinned = _pinned()
    for rel, digest in _referenced().items():
        assert rel in pinned, f"{rel} has no line in models.sha256"
        if digest is not None:
            assert pinned[rel] == digest, (
                f"{rel}: model_variants.json and models.sha256 disagree")


def test_table_sizes_match_disk_when_present():
    for name, v in _variants().items():
        for role in ("pose", "det"):
            rel = v[f"{role}_onnx"]
            if rel and (REPO_ROOT / rel).exists():
                assert (REPO_ROOT / rel).stat().st_size == \
                    v[f"{role}_size_bytes"], f"{name} {role} size"


@pytest.mark.parametrize("rel", sorted(_pinned()))
def test_pinned_file_hash(rel):
    path = MODELS_DIR / rel
    if not path.exists():
        pytest.skip(f"model file absent: {path}")
    assert sha256_file(path) == _pinned()[rel], (
        f"sha256 mismatch for {path}")
