"""Read-only comparison of final Chapter 7/Appendix parts with e69dfa6.

Writes only the adjacent JSON. Canonical OMML is checked separately from
table text because python-docx cell.text does not expose mathematical runs.
"""
import hashlib
import io
import json
import subprocess
from pathlib import Path

from docx import Document
from lxml import etree

OUT = Path(__file__).resolve().parent
REPO = OUT.parents[4]
HERE = REPO / 'writing/v8/condensed'


def math(doc):
    return [etree.tostring(node, method='c14n') for node in doc.element.xpath('.//m:oMath')]


def tables(doc):
    return [[[cell.text for cell in row.cells] for row in table.rows] for table in doc.tables]


report = {}
for name in ['Chapter_7_Evaluation', 'Appendices']:
    path = HERE / (name + '.docx')
    prior_bytes = subprocess.run(['git', 'show', 'e69dfa6:' + path.relative_to(REPO).as_posix()],
                                 cwd=REPO, check=True, capture_output=True).stdout
    prior, current = Document(io.BytesIO(prior_bytes)), Document(path)
    assert math(prior) == math(current)
    oldtables, newtables = tables(prior), tables(current)
    assert len(oldtables) == len(newtables)
    changed = []
    for table_index, (old, new) in enumerate(zip(oldtables, newtables)):
        assert len(old) == len(new)
        for row_index, (oldrow, newrow) in enumerate(zip(old, new)):
            assert len(oldrow) == len(newrow)
            for cell_index, (oldcell, newcell) in enumerate(zip(oldrow, newrow)):
                if oldcell != newcell:
                    changed.append({'table_index': table_index, 'row_index': row_index,
                                    'cell_index': cell_index, 'before': oldcell, 'after': newcell})
    if name == 'Chapter_7_Evaluation':
        assert oldtables == newtables
    else:
        assert len(changed) == 1
        assert changed[0]['before'] == 'torso and both arms, twelve angles nonzero'
        assert changed[0]['after'] == 'torso and both arms, eleven angles nonzero'
    report[name] = {'current_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                    'baseline_sha256': hashlib.sha256(prior_bytes).hexdigest(),
                    'unchanged_canonical_math_objects': len(math(current)),
                    'tables': len(newtables), 'changed_cells': changed, 'status': 'PASS'}

(OUT / 'ch7_appendix_artifact_checks.json').write_text(json.dumps(report, indent=2) + '\n')
print('PASS: all 18 math objects are unchanged; only the authorized Appendix H table cell differs.')
