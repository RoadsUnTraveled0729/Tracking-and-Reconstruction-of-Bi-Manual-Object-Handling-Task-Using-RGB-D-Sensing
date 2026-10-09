#!/usr/bin/env python3
"""D-048/D-069: assembly-only first-appearance literature citation numbering.

Frozen chapter documents are inputs. Only copied w:t text is changed; runs,
OMML, tables and reference-entry text are preserved. The audit verifies each
source paragraph and reference identity against the saved assembly.
"""
import hashlib
import json
import re
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

CITATION_RE = re.compile(r"\[(\d+)\]")
ENTRY_RE = re.compile(r"^\[(\d+)\] (.+)$")


def paragraph_text(paragraph):
    return "".join(node.text or "" for node in paragraph.iter(qn("w:t")))


def paragraphs(element):
    return list(element.iter(qn("w:p")))


def remapped_text(text, mapping):
    return CITATION_RE.sub(lambda match: f"[{mapping[int(match[1])]}]", text)


def make_plan(paths, entries):
    references = dict(entries)
    assert len(references) == len(entries), "Duplicate source reference number"
    mapping, sources, occurrences = {}, [], []
    for path in paths:
        path = Path(path)
        texts = [paragraph_text(p) for p in paragraphs(Document(path).element.body)]
        sources.append({"file": path.name,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "paragraphs": texts})
        for index, text in enumerate(texts):
            for match in CITATION_RE.finditer(text):
                old = int(match[1])
                assert old in references, f"Unknown citation [{old}] in {path.name}"
                if old not in mapping:
                    mapping[old] = len(mapping) + 1
                occurrences.append({"source_file": path.name,
                                    "paragraph_index": index,
                                    "source_number": old,
                                    "final_number": mapping[old]})
    return {"mapping": mapping, "references": references,
            "sources": sources, "occurrences": occurrences}


def rewrite_element(element, mapping):
    """Replace split-run markers without recreating runs or touching OMML.

    Edits proceed right to left so all offsets refer to the original text.
    A replacement occupies the first text node of its marker; surrounding
    characters and every existing run property remain intact.
    """
    for paragraph in paragraphs(element):
        nodes = list(paragraph.iter(qn("w:t")))
        text = "".join(node.text or "" for node in nodes)
        spans, offset = [], 0
        for node in nodes:
            length = len(node.text or "")
            spans.append((offset, offset + length, node))
            offset += length
        for match in reversed(list(CITATION_RE.finditer(text))):
            old = int(match[1])
            assert old in mapping, f"Citation [{old}] missing from assembly plan"
            replacement = f"[{mapping[old]}]"
            first = True
            for start, end, node in spans:
                if end <= match.start() or start >= match.end():
                    continue
                left = max(match.start() - start, 0)
                right = min(match.end() - start, end - start)
                current = node.text or ""
                node.text = current[:left] + (replacement if first else "") + current[right:]
                node.set(qn("xml:space"), "preserve")
                first = False
        assert paragraph_text(paragraph) == remapped_text(text, mapping)


def final_entries(plan):
    return [(new, plan["references"][old])
            for old, new in plan["mapping"].items()]


def verify_assembly(doc, plan):
    """Independently compare all chapter text and each cited source identity."""
    all_paragraphs = paragraphs(doc.element.body)
    texts = [paragraph_text(p) for p in all_paragraphs]
    navigation_indices = set()
    for index, paragraph in enumerate(all_paragraphs):
        style = paragraph.find('./' + qn('w:pPr') + '/' + qn('w:pStyle'))
        if style is not None and style.get(qn('w:val')) in {
                'TOC1', 'TOC2', 'TOC3', 'TableofFigures'}:
            navigation_indices.add(index)
    mapping = plan["mapping"]
    final_bibliography = final_entries(plan)
    bibliography_texts = [f"[{number}] {text}" for number, text in final_bibliography]
    ref_indices = [i for i, text in enumerate(texts) if text == "References"]
    matches = [i for i in ref_indices
               if texts[i + 1:i + 1 + len(bibliography_texts)] == bibliography_texts]
    assert len(matches) == 1, "Final bibliography text or reference identity differs"
    ref_start = matches[0]
    ref_end = ref_start + 1 + len(bibliography_texts)
    assert ref_end == len(texts) or not ENTRY_RE.match(texts[ref_end]), "Unexpected bibliography entry"
    assert [number for number, _ in final_bibliography] == list(range(1, len(mapping) + 1))

    cursor, final_occurrences, checked = 0, [], 0
    for source in plan["sources"]:
        expected = [remapped_text(text, mapping) for text in source["paragraphs"]]
        # Sources occupy consecutive paragraph spans. The bibliography may
        # follow the appendices; it never enters first-appearance order.
        starts = [i for i in range(cursor, len(texts) - len(expected) + 1)
                  if texts[i:i + len(expected)] == expected]
        assert starts, f"Source text/citation mismatch: {source['file']}"
        start = starts[0]
        assert start + len(expected) <= ref_start or start >= ref_end, "Source overlaps bibliography"
        for index, (before, after) in enumerate(zip(source["paragraphs"], texts[start:start + len(expected)])):
            old_numbers = [int(m[1]) for m in CITATION_RE.finditer(before)]
            new_numbers = [int(m[1]) for m in CITATION_RE.finditer(after)]
            assert [mapping[old] for old in old_numbers] == new_numbers
            for old, new in zip(old_numbers, new_numbers):
                assert dict(final_bibliography)[new] == plan["references"][old]
                final_occurrences.append(new)
                checked += 1
        cursor = start + len(expected)
    assert list(dict.fromkeys(final_occurrences)) == list(range(1, len(mapping) + 1)), "Not global first-appearance order"
    # Catch extra literature markers introduced outside the copied sources.
    all_citations = [int(m[1]) for i, text in enumerate(texts)
                     if not ref_start <= i < ref_end and i not in navigation_indices
                     for m in CITATION_RE.finditer(text)]
    assert all_citations == final_occurrences, "Extra/missing citations outside source parts"
    for index in navigation_indices:
        assert all(int(m[1]) in mapping.values() for m in CITATION_RE.finditer(texts[index])), \
            "Unresolved literature citation in generated navigation"
    return {"status": "PASS", "citation_occurrences": checked,
            "cited_entries": len(mapping),
            "source_entries": len(plan["references"]),
            "removed_uncited_source_numbers": sorted(set(plan["references"]) - set(mapping)),
            "source_paragraphs_verified": sum(len(s["paragraphs"]) for s in plan["sources"]),
            "checks": ["every source paragraph preserves text except citation numbers",
                       "every final citation resolves to the exact source reference text",
                       "global first-appearance order includes appendices",
                       "final bibliography is contiguous and contains no uncited entries"]}


def write_audit(path, plan, result, assembled_path):
    audit = {"decision": "D-048 / D-069", "verification": result,
             "assembled_file": Path(assembled_path).name,
             "assembled_sha256": hashlib.sha256(Path(assembled_path).read_bytes()).hexdigest(),
             "source_parts": [{k: v for k, v in source.items() if k != "paragraphs"}
                              for source in plan["sources"]],
             "source_to_final": [{"source_number": old, "final_number": new,
                                  "reference_text": plan["references"][old]}
                                 for old, new in plan["mapping"].items()],
             "removed_uncited": [{"source_number": old, "reference_text": text}
                                 for old, text in plan["references"].items()
                                 if old not in plan["mapping"]],
             "occurrences": plan["occurrences"]}
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(audit, indent=2, ensure_ascii=True) + "\n")
