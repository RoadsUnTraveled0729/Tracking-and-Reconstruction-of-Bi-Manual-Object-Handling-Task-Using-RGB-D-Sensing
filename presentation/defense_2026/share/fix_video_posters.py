"""Regenerate the shown-only shared copy of the defence deck and its two PDFs.

D-396 and its follow-up (b), 2026-10-07. Steps:

1. trim: copy presentation/defense_2026/Thesis_Defence_2026.pptx and remove the
   hidden backup slides (show="0"): the presentation relationship to each such
   slide is dropped and its sldId removed (D-396 method, python-pptx 1.0.2).
2. fix: on the slides listed in FIXES the video object is replaced by a plain
   picture. LibreOffice 24.2 applies the a:srcRect crop of these video objects
   wrongly when it exports the poster, so the PDF shows a squashed strip
   (pages 30 and 41) or the whole uncropped poster stretched into the box
   (pages 7, 20 and 24).
   The picture is the film frame that the author's poster shows, decoded from
   the linked MP4 with ffmpeg, cropped in pixels to the same a:srcRect and
   placed in the same a:xfrm box with no crop attribute, so every renderer
   draws exactly what PowerPoint shows before the film starts. The film, its
   poster relationship and its timing node are removed from those slides of
   the copy only.
3. render: soffice --headless --convert-to pdf with the make_package.py
   --render Impress export option, then the email PDF with Ghostscript
   pdfwrite /prepress (D-396 follow-up).

The author's deck is only read; its sha256 is checked before and after.

Run (repository root):
    /home/luo/anaconda3/bin/python presentation/defense_2026/share/fix_video_posters.py
Options: --no-render writes only the pptx.
"""

import argparse
import hashlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image
from pptx import Presentation

HERE = Path(__file__).resolve().parent
DECK_DIR = HERE.parent
ORIGINAL = DECK_DIR / "Thesis_Defence_2026.pptx"
# Author's final deck bytes (D-396, D-381); the script refuses any other input.
ORIGINAL_SHA256 = "b3b6a8f0d650888db8f13f8536c787f90cb5b16a1d1860683d46af11fe129cb7"
OUT_PPTX = HERE / "Thesis_Defence_2026_shown_only.pptx"
OUT_PDF = HERE / "Thesis_Defence_2026_shown_only.pdf"
OUT_EMAIL = HERE / "Thesis_Defence_2026_shown_only_email.pdf"
# Same export option as make_package.py IMPRESS_EXPORT (D-383).
IMPRESS_EXPORT = json.dumps({"ExportHiddenSlides": {"type": "boolean", "value": "true"}})
# Same Ghostscript call as the D-396 follow-up (email copy).
GS_ARGS = ["-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.5", "-dPDFSETTINGS=/prepress",
           "-dNOPAUSE", "-dBATCH", "-dQUIET"]

# Shown-deck slide number -> (video object name, poster frame index in the MP4).
# The frame index is the 0-based decoded frame whose pixels match the author's
# poster image best (mean absolute grey difference at quarter resolution:
# slide 7 frame 105 0.202, slide 20 frame 105 0.293, slide 24 frame 90 0.254,
# slide 30 frame 480 0.153, slide 41 frame 45 0.196, against medians 6.81,
# 4.56, 0.97, 2.25 and 3.5 over all frames; measured 2026-10-07).
# The script recomputes the best frame and stops if it differs.
FIXES = {
    7: ("p06-Accepted_Body_Landmarks_With_Axes.mp4", 105),
    20: ("p23-Holding_Input_And_Torso_Rejection_With_Axes.mp4", 105),
    24: ("p32-Controlled_Held_Joint_Fallback.mp4", 90),
    30: ("p41-Archived_Pose_Replay_With_Model_Axes.mp4", 480),
    41: ("p27-Fresh_Unity_Wrist_Loss_With_Model_Axes.mp4", 45),
}

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main",
      "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
      "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
R_EMBED = "{%s}embed" % NS["r"]
R_LINK = "{%s}link" % NS["r"]
R_ID = "{%s}id" % NS["r"]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def trim(prs):
    """Remove the hidden slides (D-396 method)."""
    sld_id_lst = prs.slides._sldIdLst
    removed = 0
    for sld_id in list(sld_id_lst):
        rid = sld_id.get(R_ID)
        slide_part = prs.part.related_part(rid)
        if slide_part._element.get("show") == "0":
            prs.part.drop_rel(rid)
            sld_id_lst.remove(sld_id)
            removed += 1
    return removed


def decode_frames(mp4, width, height):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf",
                          "scale=%d:%d:flags=bilinear,format=gray" % (width, height),
                          "-f", "rawvideo", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, height, width).astype(np.float32)


def full_frame(mp4, index):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf",
                          "select=eq(n\\,%d)" % index, "-frames:v", "1", "-f", "image2pipe",
                          "-vcodec", "png", "-"], check=True, capture_output=True).stdout
    return Image.open(io.BytesIO(raw)).convert("RGB")


def fix_slide(slide, number, video_name, expected_frame, scratch):
    part = slide.part
    pics = [pic for pic in part._element.iter("{%s}pic" % NS["p"])
            if pic.find(".//a:videoFile", NS) is not None]
    if len(pics) != 1:
        raise SystemExit("ERROR: slide %d has %d video objects, expected 1" % (number, len(pics)))
    pic = pics[0]
    c_nv_pr = pic.find("p:nvPicPr/p:cNvPr", NS)
    if c_nv_pr.get("name") != video_name:
        raise SystemExit("ERROR: slide %d video is %r, expected %r" % (number, c_nv_pr.get("name"), video_name))
    shape_id = c_nv_pr.get("id")
    nv_pr = pic.find("p:nvPicPr/p:nvPr", NS)
    video_file = nv_pr.find("a:videoFile", NS)
    video_rid = video_file.get(R_LINK)
    media_rids = [video_rid] + [m.get(R_EMBED) for m in nv_pr.iter("{http://schemas.microsoft.com/office/powerpoint/2010/main}media")]
    mp4_part = part.related_part(video_rid)
    blip = pic.find("p:blipFill/a:blip", NS)
    poster_rid = blip.get(R_EMBED)
    poster = Image.open(io.BytesIO(part.related_part(poster_rid).blob)).convert("L")

    mp4 = scratch / ("slide%d.mp4" % number)
    mp4.write_bytes(mp4_part.blob)
    qw, qh = poster.width // 4, poster.height // 4
    reference = np.asarray(poster.resize((qw, qh), Image.BILINEAR), dtype=np.float32)
    diffs = np.abs(decode_frames(mp4, qw, qh) - reference).mean(axis=(1, 2))
    best = int(np.argmin(diffs))
    if best != expected_frame:
        raise SystemExit("ERROR: slide %d poster matches frame %d, recorded %d" % (number, best, expected_frame))
    frame = full_frame(mp4, best)
    if frame.size != poster.size:
        raise SystemExit("ERROR: slide %d frame %s differs from poster %s" % (number, frame.size, poster.size))

    src_rect = pic.find("p:blipFill/a:srcRect", NS)
    crop = {k: int(src_rect.get(k, "0")) / 100000.0 for k in "ltrb"} if src_rect is not None else dict.fromkeys("ltrb", 0.0)
    left = round(frame.width * crop["l"])
    right = frame.width - round(frame.width * crop["r"])
    top = round(frame.height * crop["t"])
    bottom = frame.height - round(frame.height * crop["b"])
    still = frame.crop((left, top, right, bottom))
    ext = pic.find("p:spPr/a:xfrm/a:ext", NS)
    box_aspect = int(ext.get("cx")) / int(ext.get("cy"))
    # Letterbox in black (the slide background) only if the crop does not
    # already have the box aspect to the nearest pixel.
    target_w = round(still.height * box_aspect)
    if abs(target_w - still.width) > 1:
        target_h = round(still.width / box_aspect)
        canvas = Image.new("RGB", (max(still.width, target_w), max(still.height, target_h)), (0, 0, 0))
        canvas.paste(still, ((canvas.width - still.width) // 2, (canvas.height - still.height) // 2))
        still = canvas
    still_path = scratch / ("slide%02d_frame%d.png" % (number, best))
    still.save(still_path)

    # Plain picture: same element, same xfrm, new blip, no crop, no media.
    _, new_rid = part.get_or_add_image_part(str(still_path))
    blip.set(R_EMBED, new_rid)
    if src_rect is not None:
        src_rect.getparent().remove(src_rect)
    for child in list(nv_pr):
        nv_pr.remove(child)
    for link in c_nv_pr.findall("a:hlinkClick", NS):
        c_nv_pr.remove(link)
    c_nv_pr.set("name", "%s still, frame %d" % (Path(video_name).stem, best))
    timing = part._element.find("p:timing", NS)
    if timing is not None:
        for target in list(timing.iter("{%s}spTgt" % NS["p"])):
            if target.get("spid") == shape_id:
                node = target
                while node.getparent().tag != "{%s}childTnLst" % NS["p"]:
                    node = node.getparent()
                node.getparent().remove(node)
        if not any(True for _ in timing.iter("{%s}spTgt" % NS["p"])):
            part._element.remove(timing)
    for rid in set(media_rids + [poster_rid]):
        if part._rel_ref_count(rid) == 0:
            part.rels.pop(rid)
    print("slide %d: %s -> frame %d (diff %.3f), crop x %d-%d y %d-%d, still %dx%d (aspect %.4f, box %.4f)"
          % (number, video_name, best, diffs[best], left, right, top, bottom, still.width, still.height,
             still.width / still.height, box_aspect))


def render(scratch):
    snapshot = scratch / OUT_PPTX.name
    shutil.copyfile(OUT_PPTX, snapshot)
    subprocess.run(["soffice", "-env:UserInstallation=" + (scratch / "office-profile").as_uri(),
                    "--headless", "--convert-to", "pdf:impress_pdf_Export:" + IMPRESS_EXPORT,
                    "--outdir", str(scratch), str(snapshot)], check=True, capture_output=True)
    rendered = scratch / (OUT_PPTX.stem + ".pdf")
    if not rendered.is_file():
        raise SystemExit("ERROR: LibreOffice did not produce " + rendered.name)
    shutil.copyfile(rendered, OUT_PDF)
    subprocess.run(["gs"] + GS_ARGS + ["-sOutputFile=" + str(OUT_EMAIL), str(OUT_PDF)], check=True)
    for pdf in (OUT_PDF, OUT_EMAIL):
        print("%s %d B sha256 %s" % (pdf.name, pdf.stat().st_size, sha256(pdf)))


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--no-render", action="store_true", help="write only the pptx")
    args = parser.parse_args()
    if sha256(ORIGINAL) != ORIGINAL_SHA256:
        raise SystemExit("ERROR: %s is not the author's final deck" % ORIGINAL.name)
    with tempfile.TemporaryDirectory(prefix="share-fix-") as scratch:
        scratch = Path(scratch)
        prs = Presentation(str(ORIGINAL))
        removed = trim(prs)
        slides = list(prs.slides)
        print("trim: %d hidden slides removed, %d left" % (removed, len(slides)))
        for number, (video_name, frame) in sorted(FIXES.items()):
            fix_slide(slides[number - 1], number, video_name, frame, scratch)
        prs.save(str(OUT_PPTX))
        print("%s %d B sha256 %s" % (OUT_PPTX.name, OUT_PPTX.stat().st_size, sha256(OUT_PPTX)))
        if not args.no_render:
            render(scratch)
    if sha256(ORIGINAL) != ORIGINAL_SHA256:
        raise SystemExit("ERROR: %s changed" % ORIGINAL.name)
    print("original unchanged: sha256 %s" % ORIGINAL_SHA256)
    return 0


if __name__ == "__main__":
    sys.exit(main())
