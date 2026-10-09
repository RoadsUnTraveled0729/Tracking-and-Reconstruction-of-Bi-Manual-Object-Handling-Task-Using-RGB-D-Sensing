#!/usr/bin/env python3
"""Verify saved assembly citations against unchanged, frozen-number sources."""
import json
from pathlib import Path

from docx import Document

import assembly_citations as citations
import build_thesis as assembly


def main():
    paths = [assembly.ROOT / filename for _, filename in assembly.PARTS + [assembly.APPENDIX_PART]]
    plan = citations.make_plan(paths, assembly.fm.parse_references())
    result = citations.verify_assembly(Document(assembly.OUT), plan)
    citations.write_audit(assembly.OUT_CITATIONS, plan, result, assembly.OUT)
    print(json.dumps(result, indent=2))
    print(f"saved {assembly.OUT_CITATIONS}")


if __name__ == "__main__":
    main()
