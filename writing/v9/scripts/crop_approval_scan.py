#!/usr/bin/env python3
"""Crop the signed Approval page scan to its signature block.

Input:  writing/v9/figures/src/IMG_2688.jpeg, the author's photograph of
        the signed page ii (post-defence revision, 2026-10-06).
Output: writing/v9/figures/approval_signed_block.png, the region from just
        above the "Name:" row to just below the Scratchley block. The
        "Approval" heading, the "Date Approved" line and the page number
        are left out; build_frontmatter.py prints those as text.

The scan is only rotated by its EXIF orientation and cropped. Nothing is
drawn, cleaned or retouched.

Crop box source: ink-row and ink-column profile of the transposed scan
(pixels darker than 120 of 255), measured 2026-10-06:
  heading "Approval"         rows 170-202
  "Name:" row                rows 241-263   -> top edge 225 (22 px clear)
  Scratchley block, last ink rows 1104-1105 -> bottom edge 1120 (15 px clear)
  "Date Approved" line       rows 1199-1222 (excluded)
  text columns start at x about 180 ("Name:"), rules end at x about 1120;
  two stray paper marks at x about 93 and 1255 near y 505-515 lie outside
  the box -> left edge 150, right edge 1180.

Run with /usr/bin/python3 (it has PIL; the thesis interpreter does not):
  /usr/bin/python3 writing/v9/scripts/crop_approval_scan.py
"""
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "figures" / "src" / "IMG_2688.jpeg"
OUT = ROOT / "figures" / "approval_signed_block.png"

# (left, top, right, bottom) in pixels of the EXIF-transposed scan; see the
# module docstring for the measurement each edge comes from.
CROP_BOX = (150, 225, 1180, 1120)


def main():
    image = ImageOps.exif_transpose(Image.open(SRC)).convert("RGB")
    width, height = image.size
    left, top, right, bottom = CROP_BOX
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise SystemExit(f"ERROR: crop box {CROP_BOX} outside the scan "
                         f"{width}x{height}")
    block = image.crop(CROP_BOX)
    block.save(OUT, optimize=True)
    print(f"source: {SRC} ({width}x{height})")
    print(f"crop box (left, top, right, bottom): {CROP_BOX}")
    print(f"saved {OUT} ({block.size[0]}x{block.size[1]})")


if __name__ == "__main__":
    main()
