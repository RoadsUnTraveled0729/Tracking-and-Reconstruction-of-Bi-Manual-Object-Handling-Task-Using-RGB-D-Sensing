#!/usr/bin/env python3
"""Paginate the Word thesis, cache its four navigation lists, and export PDF.

Run with /usr/bin/python3 (LibreOffice UNO). The cache helper uses the thesis
Python, preserving original OMML and all non-navigation content in the DOCX.
An isolated temporary LibreOffice profile leaves interactive sessions alone.
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

REPO = Path(__file__).resolve().parents[4]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / 'writing/v8/Thesis_V8_Condensed.docx'
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
            doc.storeToURL(uno.systemPathToFileUrl(str(DST.resolve())),
                           (prop('FilterName', 'writer_pdf_Export'),))
            manifest = SRC.parent / 'condensed/audit_evidence/submission_checklist_2026-09-13/navigation.json'
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text(json.dumps({'passes': pass_number, 'indexes': current}, indent=2)+'\n')
            doc.close(True)
            doc = None
            subprocess.run([THESIS_PYTHON, str(Path(__file__).with_name('cache_navigation.py')),
                            str(SRC), str(manifest)], check=True)
            # Reopen with updates disabled. The saved field results must
            # reproduce the PDF pagination without an F9/index refresh.
            doc = desktop.loadComponentFromURL(uno.systemPathToFileUrl(str(SRC.resolve())),
                '_blank', 0, (prop('Hidden', True), prop('UpdateDocMode', 0)))
            cached_pdf = Path(temp, 'cached.pdf')
            doc.storeToURL(uno.systemPathToFileUrl(str(cached_pdf)),
                           (prop('FilterName', 'writer_pdf_Export'),))
            doc.close(True)
            doc = None
            rendered_text = subprocess.check_output(['pdftotext', '-layout', str(DST), '-'])
            cached_text = subprocess.check_output(['pdftotext', '-layout', str(cached_pdf), '-'])
            def page_lines(text):
                # PDF extraction can add one leader dot or whitespace where
                # the final dot meets a digit. Retain every page and line
                # boundary, comparing all substantive text at that location.
                return [[re.sub(r'\s+', ' ', re.sub(r'\.{2,}', ' ', line)).strip()
                         for line in page.splitlines()]
                        for page in text.decode('utf-8').split('\f')]
            if page_lines(rendered_text) != page_lines(cached_text):
                # Keep evidence of the failed comparison for investigation.
                manifest.with_name('cached_layout.txt').write_bytes(cached_text)
                manifest.with_name('rendered_layout.txt').write_bytes(rendered_text)
                raise RuntimeError('Cached DOCX pagination differs from the refreshed PDF')
            metadata = json.loads(manifest.read_text())
            metadata['cached_reopen_check'] = 'PASS: identical substantive text by page and line; leader-dot counts and extraction whitespace ignored'
            manifest.write_text(json.dumps(metadata, indent=2)+'\n')
            # The final citation audit must identify the delivered bytes.
            subprocess.run([THESIS_PYTHON, str(Path(__file__).with_name('verify_assembly_citations.py'))],
                           check=True)
            print(f'rendered {DST}; four indexes converged in {pass_number} updates')
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
