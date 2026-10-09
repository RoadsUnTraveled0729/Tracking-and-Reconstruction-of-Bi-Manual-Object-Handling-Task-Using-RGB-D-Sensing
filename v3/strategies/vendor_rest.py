"""Rest-pose quaternions from the vendored v1 conventions."""
import sys
from pathlib import Path

_VENDOR = Path(__file__).resolve().parents[1] / "vendor" / "v1"
if str(_VENDOR) not in sys.path:
    sys.path.insert(0, str(_VENDOR))

from occlusion import ROOT_REST_DEG          # noqa: E402  vendored
from root_frame import recompose_zxy         # noqa: E402  vendored

from core.representation import quat_from_matrix  # noqa: E402


def root_rest_quat():
    """v1's pre-first-sample root rest (facing the camera)."""
    return quat_from_matrix(recompose_zxy(ROOT_REST_DEG))
