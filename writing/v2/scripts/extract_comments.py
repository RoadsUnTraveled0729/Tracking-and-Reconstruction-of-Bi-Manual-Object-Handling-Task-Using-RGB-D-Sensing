#!/usr/bin/env python3
"""Extract Word review comments (author, date, anchored text, comment text) from .docx files."""
import sys, zipfile, re
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

def text_of(el):
    return "".join(t.text or "" for t in el.iter(W + "t"))

def extract(path):
    z = zipfile.ZipFile(path)
    # comments
    comments = {}
    try:
        root = ET.fromstring(z.read("word/comments.xml"))
    except KeyError:
        return []
    for c in root.findall(W + "comment"):
        cid = c.get(W + "id")
        comments[cid] = {
            "id": cid,
            "author": c.get(W + "author", "?"),
            "date": (c.get(W + "date") or "")[:10],
            "text": " ".join(text_of(p) for p in c.findall(W + "p")).strip(),
        }
    # anchored text from document.xml: text between commentRangeStart/End
    doc = z.read("word/document.xml").decode("utf-8", "replace")
    for cid in comments:
        m = re.search(
            r'<w:commentRangeStart[^>]*w:id="%s"[^>]*/>(.*?)<w:commentRangeEnd[^>]*w:id="%s"' % (cid, cid),
            doc, re.S)
        if m:
            anchor = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", m.group(1)))
            comments[cid]["anchor"] = anchor.strip()[:200]
        else:
            comments[cid]["anchor"] = ""
    return sorted(comments.values(), key=lambda c: int(c["id"]))

for path in sys.argv[1:]:
    cs = extract(path)
    print(f"\n{'='*80}\n{path}  ({len(cs)} comments)\n{'='*80}")
    for c in cs:
        print(f"\n[{c['id']}] {c['author']} ({c['date']})")
        if c["anchor"]:
            print(f"  ON: \"{c['anchor']}\"")
        print(f"  >> {c['text']}")
