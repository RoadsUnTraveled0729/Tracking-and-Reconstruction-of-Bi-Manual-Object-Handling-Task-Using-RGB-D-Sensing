#!/usr/bin/env python3
"""Paginate the Word thesis, cache its three navigation lists, and export PDF.

Run with /usr/bin/python3 (LibreOffice UNO). The cache helper uses the thesis
Python, preserving original OMML and all non-navigation content in the DOCX.
An isolated temporary LibreOffice profile leaves interactive sessions alone.

The appendices and the references restart their page numbers behind a
letter (A1, B1, R1; supervisor, 2026-09-14). LibreOffice's own refreshed
indexes print the bare restarted numbers, so the delivered PDF is exported
from the cached document, whose navigation rows carry the labels; the
refreshed render is kept only to prove that the pagination is the same.
"""
import json
import re
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import uno
from com.sun.star.beans import PropertyValue
from com.sun.star.connection import NoConnectException

REPO = Path(__file__).resolve().parents[3]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / 'writing/v9/Thesis_V9.docx'
DST = Path(sys.argv[2]) if len(sys.argv) > 2 else SRC.with_suffix('.pdf')
THESIS_PYTHON = '/home/luo/anaconda3/bin/python'


def prop(name, value):
    p = PropertyValue()
    p.Name, p.Value = name, value
    return p


def indexes(doc):
    result = []
    collection = doc.getDocumentIndexes()
    for i in range(collection.getCount()):
        index = collection.getByIndex(i)
        paragraphs = index.Anchor.createEnumeration()
        rows = []
        while paragraphs.hasMoreElements():
            paragraph = paragraphs.nextElement()
            if paragraph.String.strip():
                rows.append({'text': paragraph.String,
                             'style': paragraph.ParaStyleName})
        result.append({'kind': 'contents' if i == 0 else 'list', 'rows': rows})
    return result


def check_part_labels(text):
    """The delivered PDF must show the part labels where the supervisor
    asked for them: in the contents and the lists, and in the footers."""
    pages = text.split('\f')
    lines = [re.sub(r'\s+', ' ', line).strip() for page in pages for line in page.splitlines()]
    joined = '\n'.join(lines)
    def has(pattern):
        return any(re.search(pattern, line) for line in lines)
    def has_row(kind):
        # A list row may wrap; its page token then ends a later line.
        return re.search(r'^' + kind + r' ([A-H])\.\d+\.(?:.*\n){0,3}?.*\b\1\d+$', joined, re.M) is not None
    problems = []
    if not has(r'^Appendix A:.*\bA1$'):
        problems.append('contents row of Appendix A does not end in A1')
    if not has(r'^Appendix H:.*\bH1$'):
        problems.append('contents row of Appendix H does not end in H1')
    if not has(r'^References.*\bR1$'):
        problems.append('contents row of References does not end in R1')
    if not has_row('Figure'):
        problems.append('no list-of-figures row of an appendix ends in a letter label')
    if not has_row('Table'):
        problems.append('no list-of-tables row of an appendix ends in a letter label')
    for label, head in (('A1', 'Appendix A:'), ('R1', 'References')):
        # The first page that OPENS with the heading and is not a contents
        # page: a contents row can also start a page (it did once the
        # Chapter 9 subsections went, 2026-09-16), so pages with dot
        # leaders are skipped.
        candidates = [p for p in pages if p.strip().startswith(head)]
        page = next((p for p in candidates if not re.search(r'\.{5,}', p)), None)
        if page is None:
            problems.append(f'no page opens with {head!r}')
            continue
        last = [l.strip() for l in page.splitlines() if l.strip()][-1]
        if last != label:
            problems.append(f'footer of the first {head!r} page reads {last!r}, wanted {label!r}')
    if problems:
        raise RuntimeError('Part labels: ' + '; '.join(problems))


def main():
    with tempfile.TemporaryDirectory(prefix='thesis-render-') as temp:
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        profile = Path(temp, 'profile').as_uri()
        proc = subprocess.Popen([
            'soffice', f'-env:UserInstallation={profile}', '--headless',
            '--invisible', '--nologo', '--norestore',
            f'--accept=socket,host=127.0.0.1,port={port};urp;StarOffice.ComponentContext'],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        desktop = doc = None
        try:
            local = uno.getComponentContext()
            resolver = local.ServiceManager.createInstanceWithContext(
                'com.sun.star.bridge.UnoUrlResolver', local)
            deadline = time.monotonic() + 60  # Maximum connection budget, not a fixed wait.
            while True:
                try:
                    ctx = resolver.resolve(
                        f'uno:socket,host=127.0.0.1,port={port};urp;StarOffice.ComponentContext')
                    break
                except NoConnectException:
                    if proc.poll() is not None or time.monotonic() >= deadline:
                        raise RuntimeError('LibreOffice did not become ready')
                    time.sleep(0.1)
            desktop = ctx.ServiceManager.createInstanceWithContext('com.sun.star.frame.Desktop', ctx)
            doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(str(SRC.resolve())),
                                               '_blank', 0, (prop('Hidden', True),))
            if doc is None:
                raise RuntimeError('LibreOffice could not load the thesis')
            previous = None
            seen = set()
            for pass_number in range(1, 9):
                doc.getTextFields().refresh()
                collection = doc.getDocumentIndexes()
                for i in range(collection.getCount()):
                    collection.getByIndex(i).update()
                doc.refresh()
                current = indexes(doc)
                signature = json.dumps(current, sort_keys=True)
                if signature == previous:
                    break
                if signature in seen:
                    raise RuntimeError('Navigation pagination oscillates')
                seen.add(signature)
                previous = signature
            else:
                raise RuntimeError('Navigation did not converge within eight updates')
            refreshed_pdf = Path(temp, 'refreshed.pdf')
            doc.storeToURL(uno.systemPathToFileUrl(str(refreshed_pdf)),
                           (prop('FilterName', 'writer_pdf_Export'),))
            manifest = SRC.parent / 'audit_evidence/submission_checklist_v9/navigation.json'
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text(json.dumps({'passes': pass_number, 'indexes': current}, indent=2)+'\n')
            doc.close(True)
            doc = None
            subprocess.run([THESIS_PYTHON, str(Path(__file__).with_name('cache_navigation.py')),
                            str(SRC), str(manifest)], check=True)
            # Reopen with updates disabled. The saved field results must
            # reproduce the PDF pagination without an F9/index refresh, and
            # this export is the delivered PDF: its navigation rows carry the
            # part labels that a refresh would print as bare numbers.
            doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(str(SRC.resolve())),
                '_blank', 0, (prop('Hidden', True), prop('UpdateDocMode', 0)))
            doc.storeToURL(uno.systemPathToFileUrl(str(DST.resolve())),
                           (prop('FilterName', 'writer_pdf_Export'),))
            doc.close(True)
            doc = None
            rendered_text = subprocess.check_output(['pdftotext', '-layout', str(refreshed_pdf), '-'])
            cached_text = subprocess.check_output(['pdftotext', '-layout', str(DST), '-'])
            def page_lines(text):
                # PDF extraction can add one leader dot or whitespace where
                # the final dot meets a digit. Retain every page and line
                # boundary, comparing all substantive text at that location.
                # A navigation row of an appendix or the references ends in
                # its label (A1, R1) in the cached export and in the bare
                # restarted number in the refreshed one. The longer label
                # also changes how many leader dots survive extraction and
                # where a wrapped row's token lands, so a leader remnant
                # ahead of the token is normalised and the letter dropped
                # before comparing; the pagination itself is what must agree.
                def norm(line):
                    line = re.sub(r'\s+', ' ', re.sub(r'\.{2,}', ' ', line)).strip()
                    line = re.sub(r'\s*\.\s*(?=[A-HR]?\d+$)', '.', line)
                    return re.sub(r'(?<![A-Za-z0-9])[A-HR](?=\d+$)', '', line)
                return [[norm(line) for line in page.splitlines()]
                        for page in text.decode('utf-8').split('\f')]
            if page_lines(rendered_text) != page_lines(cached_text):
                # Keep evidence of the failed comparison for investigation.
                manifest.with_name('cached_layout.txt').write_bytes(cached_text)
                manifest.with_name('rendered_layout.txt').write_bytes(rendered_text)
                raise RuntimeError('Cached DOCX pagination differs from the refreshed PDF')
            check_part_labels(cached_text.decode('utf-8'))
            metadata = json.loads(manifest.read_text())
            metadata['cached_reopen_check'] = 'PASS: identical substantive text by page and line; leader-dot counts, extraction whitespace and part-label letters ignored'
            manifest.write_text(json.dumps(metadata, indent=2)+'\n')
            # The final citation audit must identify the delivered bytes.
            subprocess.run([THESIS_PYTHON, str(Path(__file__).with_name('verify_assembly_citations.py'))],
                           check=True)
            print(f'rendered {DST}; three indexes converged in {pass_number} updates')
        finally:
            if doc is not None:
                doc.close(True)
            if desktop is not None:
                desktop.terminate()
            if proc.poll() is None:
                proc.terminate()
            proc.wait(timeout=10)


if __name__ == '__main__':
    main()
