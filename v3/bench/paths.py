"""Path resolution for manifests and configs.

A relative path in a manifest or config (for example the M3 manifests'
base_csv, D-028) is repository-relative and resolves against the
repository root, never against the caller's working directory. An
absolute path is used as written: the recorded /home/luo/Desktop/
New_SandBox/... paths in older manifests are provenance and resolve
through the standing symlink (AGENTS.md, Standing project
constraints); they are never rewritten.
"""
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def repo_path(p):
    """Absolute Path for a manifest or config path."""
    p = Path(p)
    return p if p.is_absolute() else REPO_ROOT / p


def repo_rel(p):
    """Repository-relative string for a path under the repository root
    (as given, symlinks not resolved); other paths are returned
    unchanged as strings."""
    p = Path(p).absolute()
    try:
        return str(p.relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


def apply_overrides(cfg, sets):
    """Return a deep copy of cfg with dotted-key JSON overrides applied,
    e.g. ["strategy.s2_quat_prediction.warm_start=true"] (bench CLIs'
    repeatable --set; values are parsed as JSON, else kept as str)."""
    import copy
    import json
    cfg = copy.deepcopy(cfg)
    for item in sets or []:
        key, _, val = item.partition("=")
        try:
            val = json.loads(val)
        except json.JSONDecodeError:
            pass
        node = cfg
        parts = key.split(".")
        for k in parts[:-1]:
            node = node[k]
        if parts[-1] not in node:
            raise KeyError(f"--set {key}: no such config key")
        node[parts[-1]] = val
    return cfg
