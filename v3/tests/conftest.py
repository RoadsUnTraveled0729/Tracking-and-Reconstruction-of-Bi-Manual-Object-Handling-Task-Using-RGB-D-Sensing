import importlib.util
import json
import sys
from pathlib import Path

import pytest

V3_ROOT = Path(__file__).resolve().parents[1]
if str(V3_ROOT) not in sys.path:
    sys.path.insert(0, str(V3_ROOT))


def _have_ort():
    return importlib.util.find_spec("onnxruntime") is not None


def _have_gpu():
    if not _have_ort():
        return False
    import onnxruntime as ort
    return "CUDAExecutionProvider" in ort.get_available_providers()


def _have_bag():
    try:
        with open(V3_ROOT / "configs" / "default.json") as f:
            bag = json.load(f)["paths"]["bag"]
        return Path(bag).exists()
    except Exception:
        return False


def pytest_collection_modifyitems(config, items):
    """Marker-based auto-skip: the default run needs no onnxruntime,
    no network, no bag, no GPU (V3_PLAN.md Testing)."""
    skips = {}
    if not _have_ort():
        skips["ort"] = pytest.mark.skip(reason="onnxruntime not installed"
                                               " (run under env v3rt)")
    if not _have_gpu():
        skips["gpu"] = pytest.mark.skip(reason="CUDAExecutionProvider "
                                               "unavailable")
    if not _have_bag():
        skips["bag"] = pytest.mark.skip(reason="pinned bag not on disk")
    for item in items:
        for name, mark in skips.items():
            if name in item.keywords:
                item.add_marker(mark)
