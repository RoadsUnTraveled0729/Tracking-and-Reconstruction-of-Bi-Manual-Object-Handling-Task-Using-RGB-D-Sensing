"""Probe every RealSense rosbag in a directory and write metadata + thumbnails.

For each DIR/*.bag this opens the file read-only with pyrealsense2
playback (non-real-time, no repeat; same open pattern as
eval/inspect/check_v1_overlay.py), reads device info, stream profiles
and playback duration, iterates every frameset to count colour and
depth frames (unique frame numbers) and record first/last timestamps,
and grabs colour frames evenly spaced in time for a contact sheet
(3 columns, ceil(tiles / 3) rows). Optionally hashes each file with
sha256. Bag files are only ever opened for reading.

Usage (from the repo root):
    /home/luo/anaconda3/bin/python eval/inspect/probe_bags.py
        [--dir DIR] [--out PATH] [--tiles N] [--dense STEM,STEM,...]
        [--only STEM,STEM,...] [--no-sha256]

    --dir     directory of .bag files (default: paths.VIDEO)
    --out     index path (default: DIR/index.json)
    --tiles   contact-sheet tiles per bag (default 6)
    --dense   stems that get DENSE_TILES (12) tiles instead of --tiles
    --only    re-probe only these stems; every other record already in
              the existing index at --out is kept unchanged

Outputs:
    <out>                                  (default DIR/index.json)
    DIR/thumbnails/<stem>_contact.png      (path stored relative to DIR)

A bag that fails to open or play gets an "error" field
("<ExceptionType>: <message>"), null frame counts, and still its size
and sha256. A bag whose timestamp span differs from its playback
duration by more than TRUNCATION_TOL_S gets a "warning" field.

Symbolic links matching DIR/*.bag (legacy names pointing at renamed
files) are skipped with a NOTE, so the index has one record per real
file.

Curated fields (CURATED_KEYS) already present in an existing index at
--out are copied onto the matching new record when the new record
does not have them, so a rerun only refreshes the probe fields and
thumbnails. The old record is found by stem first and, failing that,
by sha256, so curated fields survive a file rename. The old index
header field "curated_by" is carried into the new header when present.
If that existing index does not parse, the script refuses to overwrite
it and exits with status 2.

capture_stamp_from_name is parsed from a trailing _YYYYMMDD_HHMMSS at
the end of the stem (e.g. recording_20260909_000024 or
R7_rail_handover_two_hand_accepted_20260909_000024); stems without one
give null.
"""

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import pyrealsense2 as rs

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
import paths

CURATED_KEYS = ("new_name", "old_name", "session", "take_status",
                "scene_summary", "provenance_note", "renamed_on")
DEFAULT_TILES = 6
DENSE_TILES = 12
SHEET_COLS = 3
SHEET_WIDTH = 1440
WAIT_MS = 5000
TRUNCATION_TOL_S = 0.5

ROLE = {
    paths.R1_STEM: "R1_STEM",
    paths.R4_STEM: "R4_STEM",
    paths.R4_BACKUP_STEM: "R4_BACKUP_STEM",
    paths.R5_STEM: "R5_STEM",
    paths.R6A_STEM: "R6A_STEM",
    paths.R6B_STEM: "R6B_STEM",
    paths.R7_STEM: "R7_STEM",
}


def stamp_from_name(stem):
    m = re.search(r"(\d{8})_(\d{6})$", stem)
    if not m:
        return None
    return dt.datetime.strptime(m.group(1) + m.group(2),
                                "%Y%m%d%H%M%S").isoformat()


def sha256_of(path, chunk=16 * 1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def dev_info(dev, key):
    try:
        return dev.get_info(key) if dev.supports(key) else None
    except RuntimeError:
        return None


def to_bgr(frame):
    img = np.asanyarray(frame.get_data())
    fmt = frame.get_profile().format()
    if fmt == rs.format.rgb8:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    elif fmt == rs.format.rgba8:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    elif fmt == rs.format.bgra8:
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    elif fmt == rs.format.yuyv:
        img = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_YUYV)
    return np.ascontiguousarray(img)


def contact_sheet(tiles, out_path):
    rows = (len(tiles) + SHEET_COLS - 1) // SHEET_COLS
    tw = SHEET_WIDTH // SHEET_COLS
    h0, w0 = tiles[0][0].shape[:2]
    th = int(round(h0 * tw / w0))
    sheet = np.zeros((rows * th, SHEET_COLS * tw, 3), np.uint8)
    for i, (img, idx, t) in enumerate(tiles):
        small = cv2.resize(img, (tw, th), interpolation=cv2.INTER_AREA)
        label = f"frame {idx}  t={t:.2f} s"
        cv2.putText(small, label, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 0, 0), 4, cv2.LINE_AA)
        cv2.putText(small, label, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (255, 255, 255), 1, cv2.LINE_AA)
        r, c = divmod(i, SHEET_COLS)
        sheet[r * th:(r + 1) * th, c * tw:(c + 1) * tw] = small
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(out_path), sheet)


def base_record(bag):
    st = bag.stat()
    return {
        "filename": bag.name,
        "stem": bag.stem,
        "size_bytes": st.st_size,
        "mtime_iso": dt.datetime.fromtimestamp(st.st_mtime).isoformat(),
        "capture_stamp_from_name": stamp_from_name(bag.stem),
        "role_stem_from_eval_paths": ROLE.get(bag.stem),
    }


def probe(bag, rec, n_tiles, bag_dir):
    """Fill rec with playback metadata; raises on open/play failure."""
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(str(bag), repeat_playback=False)
    profile = pipeline.start(config)
    try:
        dev = profile.get_device()
        pb = dev.as_playback()
        pb.set_real_time(False)
        duration = pb.get_duration().total_seconds()
        rec["duration_s"] = round(duration, 3)
        rec["device_name"] = dev_info(dev, rs.camera_info.name)
        rec["device_serial"] = dev_info(dev, rs.camera_info.serial_number)
        rec["firmware"] = dev_info(dev, rs.camera_info.firmware_version)
        streams = []
        for sp in profile.get_streams():
            vsp = (sp.as_video_stream_profile()
                   if sp.is_video_stream_profile() else None)
            streams.append({
                "stream": str(sp.stream_type()).split(".")[-1],
                "format": str(sp.format()).split(".")[-1],
                "width": vsp.width() if vsp else None,
                "height": vsp.height() if vsp else None,
                "fps": sp.fps(),
            })
        rec["streams"] = streams

        if n_tiles > 1:
            targets = [k / (n_tiles - 1) * duration for k in range(n_tiles)]
        else:
            targets = [0.0]
        targets[0] = 0.0
        tiles = []
        seen = {"color": set(), "depth": set()}
        ts = {"color": [], "depth": []}
        color_idx = -1
        last_color = None
        while True:
            try:
                fs = pipeline.wait_for_frames(WAIT_MS)
            except RuntimeError:
                break
            for kind, f in (("color", fs.get_color_frame()),
                            ("depth", fs.get_depth_frame())):
                if not f:
                    continue
                fn = f.get_frame_number()
                if fn in seen[kind]:
                    continue
                seen[kind].add(fn)
                ts[kind].append(f.get_timestamp())
                if kind == "color":
                    color_idx += 1
                    rel = (ts["color"][-1] - ts["color"][0]) / 1000.0
                    if len(tiles) < n_tiles and rel >= targets[len(tiles)]:
                        tiles.append((to_bgr(f), color_idx, rel))
                    elif len(tiles) == n_tiles - 1:
                        last_color = (to_bgr(f), color_idx, rel)
        if len(tiles) == n_tiles - 1 and last_color is not None:
            tiles.append(last_color)
        rec["frame_count_color"] = len(seen["color"])
        rec["frame_count_depth"] = len(seen["depth"])
        rec["frame_count_method"] = "iterated_all_framesets_unique_frame_number"
        for kind in ("color", "depth"):
            if seen[kind]:
                rec[f"{kind}_frame_number_min"] = min(seen[kind])
                rec[f"{kind}_frame_number_max"] = max(seen[kind])
        allts = ts["color"] + ts["depth"]
        first = min(allts) if allts else None
        last = max(allts) if allts else None
        rec["first_timestamp_ms"] = first
        rec["last_timestamp_ms"] = last
        if first is not None and last is not None:
            span = (last - first) / 1000.0
            if abs(span - duration) > TRUNCATION_TOL_S:
                rec["warning"] = (f"timestamp span {span:.3f} s differs from "
                                  f"playback duration {duration:.3f} s by more "
                                  f"than {TRUNCATION_TOL_S} s")
        if tiles:
            rel_path = Path("thumbnails") / f"{bag.stem}_contact.png"
            contact_sheet(tiles, bag_dir / rel_path)
            rec["thumbnail"] = rel_path.as_posix()
            rec["thumbnail_frames"] = [{"color_frame_index": i,
                                        "time_s": round(t, 3)}
                                       for _, i, t in tiles]
        else:
            rec["thumbnail"] = None
    finally:
        pipeline.stop()
    return rec


def load_old_records(index_path):
    """Return ({stem: record}, old header curated_by or None) from an
    existing index, ({}, None) if absent.
    Exit with status 2 if the file exists but does not parse."""
    if not index_path.exists():
        return {}, None
    try:
        old = json.loads(index_path.read_text())
        return ({r["stem"]: r for r in old.get("recordings", [])
                 if "stem" in r}, old.get("curated_by"))
    except (json.JSONDecodeError, OSError, AttributeError, TypeError):
        print(f"ERROR: {index_path} exists but does not parse; "
              f"refusing to overwrite")
        sys.exit(2)


def stem_list(text):
    return [s.strip() for s in text.split(",") if s.strip()] if text else []


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dir", type=Path, default=paths.VIDEO)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--tiles", type=int, default=DEFAULT_TILES)
    ap.add_argument("--dense", default="")
    ap.add_argument("--only", default="")
    ap.add_argument("--no-sha256", action="store_true")
    args = ap.parse_args()
    if args.tiles < 1:
        ap.error("--tiles must be >= 1")

    bag_dir = args.dir.resolve()
    out = (args.out or bag_dir / "index.json").resolve()
    dense = set(stem_list(args.dense))
    only = set(stem_list(args.only))

    all_bags = []
    for b in sorted(bag_dir.glob("*.bag")):
        if b.is_symlink():
            print(f"NOTE: skipping symlink {b.name} -> {b.readlink()}")
            continue
        all_bags.append(b)
    stems = {b.stem for b in all_bags}
    for s in sorted((dense | only) - stems):
        print(f"WARNING: stem {s} has no .bag in {bag_dir}")
    bags = [b for b in all_bags if not only or b.stem in only]

    old_records, curated_by = load_old_records(out)
    old_by_sha = {r["sha256"]: r for r in old_records.values()
                  if r.get("sha256")}
    new_records = {}
    t_start = time.time()
    for bag in bags:
        t0 = time.time()
        n_tiles = DENSE_TILES if bag.stem in dense else args.tiles
        rec = base_record(bag)
        try:
            probe(bag, rec, n_tiles, bag_dir)
        except Exception as e:  # record and continue
            rec["error"] = f"{type(e).__name__}: {e}"
            rec["frame_count_color"] = None
            rec["frame_count_depth"] = None
            rec.setdefault("thumbnail", None)
        if args.no_sha256:
            rec["sha256"] = None
            rec["sha256_note"] = "skipped (--no-sha256)"
        else:
            rec["sha256"] = sha256_of(bag)
        rec["probe_seconds"] = round(time.time() - t0, 1)
        old = (old_records.get(rec["stem"])
               or old_by_sha.get(rec.get("sha256")))
        if old:
            for key in CURATED_KEYS:
                if key in old and key not in rec:
                    rec[key] = old[key]
        status = ("ERROR" if "error" in rec
                  else "WARNING" if "warning" in rec else "OK")
        extra = rec.get("error") or rec.get("warning") or ""
        print(f"[{status}] {bag.name} {rec.get('duration_s')} s "
              f"color={rec.get('frame_count_color')} "
              f"depth={rec.get('frame_count_depth')} tiles={n_tiles} "
              f"({rec['probe_seconds']} s) {extra}".rstrip(), flush=True)
        new_records[rec["stem"]] = rec

    recs = dict(old_records) if only else {}
    recs.update(new_records)
    ordered = sorted(recs.values(),
                     key=lambda r: (r.get("capture_stamp_from_name")
                                    or r.get("mtime_iso") or "", r["stem"]))
    index = {
        "generated_by": "eval/inspect/probe_bags.py",
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "dir": str(bag_dir),
        "reader": "pyrealsense2",
        "python": sys.executable,
        "total_seconds": round(time.time() - t_start, 1),
    }
    if curated_by is not None:
        index["curated_by"] = curated_by
    index["recordings"] = ordered
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(index, indent=2) + "\n")
    print(f"[+] {out}")


if __name__ == "__main__":
    main()
