#!/usr/bin/env python3
"""Offline checks of exact release inventory, accounting and copied bytes."""
import collections
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
from zipfile import BadZipFile, ZipFile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ACCOUNTING = {
    'release/source_summary.json', 'release/source_manifest.jsonl',
    'release/source_tree.jsonl', 'release/release_files.json',
}
AUTHORED = {
    'README.md', '.gitignore', 'Video/README.md', 'release/prepare_snapshot.py',
    'release/reviewer_smoke.py', 'release/SELECTION.md', 'release/REPRODUCTION.md',
    'release/THIRD_PARTY_NOTICES.md', 'release/system.svg',
}
MODES = {'100644', '100755', '120000'}


def safe_path(value):
    if not isinstance(value, str) or not value or '\x00' in value or '\\' in value:
        raise ValueError('Unsafe path: ' + repr(value))
    path = PurePosixPath(value)
    if path.is_absolute() or '..' in path.parts or str(path) != value or '.git' in path.parts:
        raise ValueError('Unsafe path: ' + repr(value))
    if value == '.':
        raise ValueError('Unsafe path: ' + repr(value))
    return value


def digest(value, length):
    return isinstance(value, str) and len(value) == length and all(c in '0123456789abcdef' for c in value)


def blob_id(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def payload(path, mode):
    if mode not in MODES:
        raise ValueError('Unsupported Git mode: ' + str(mode))
    for parent in path.relative_to(ROOT).parents:
        if (ROOT / parent).is_symlink():
            raise ValueError('Payload parent is a symlink')
    info = path.lstat()
    if mode == '120000':
        if not stat.S_ISLNK(info.st_mode):
            raise ValueError('Missing symlink')
        data = os.fsencode(os.readlink(path))
        if not path.exists():
            raise ValueError('Broken symlink')
    else:
        if not stat.S_ISREG(info.st_mode):
            raise ValueError('Expected regular file')
        if bool(info.st_mode & 0o111) != (mode == '100755'):
            raise ValueError('Executable mode mismatch')
        data = path.read_bytes()
    return data


def inventory():
    files = set()
    pending = [ROOT]
    while pending:
        directory = pending.pop()
        for path in directory.iterdir():
            if path == ROOT / '.git':
                continue
            if path.is_dir() and not path.is_symlink():
                pending.append(path)
            else:
                files.add(path.relative_to(ROOT).as_posix())
    return files


def accounting(summary, rows, tree, release_rows, errors):
    commit = summary['source_commit']
    if not digest(commit, 40) or not digest(summary['source_tree'], 40):
        errors.append('Invalid source commit/tree identifier')
    prefix = summary['source_thesis_prefix']
    if prefix != 'ug_thesis_2026/':
        errors.append('Unexpected source thesis prefix')
    expected_tree = {}
    for row in tree:
        source = safe_path(row['path'])
        if source in expected_tree:
            errors.append('Duplicate source tree path: ' + source)
        if row['mode'] not in MODES or not digest(row['blob'], 40):
            errors.append('Invalid source tree mode/blob: ' + source)
        expected_tree[source] = (row['mode'], row['blob'])
    tracked = []
    supplements = []
    seen_sources = set()
    expected = {}
    included = []
    for row in rows:
        source = safe_path(row['source_path'])
        if source in seen_sources:
            errors.append('Duplicate source manifest path: ' + source)
        seen_sources.add(source)
        if row['source_commit'] != commit:
            errors.append('Source commit mismatch: ' + source)
        if row['git_mode'] not in MODES or not digest(row['git_blob'], 40):
            errors.append('Invalid source manifest mode/blob: ' + source)
        if not digest(row['sha256'], 64) or type(row['size']) is not int or row['size'] < 0:
            errors.append('Invalid source manifest hash/size: ' + source)
        kind = row.get('source_kind')
        if kind == 'local_ignored_supplement':
            supplements.append(row)
            archive = row['archive_blob']
            if archive is not None and not digest(archive, 40):
                errors.append('Invalid supplemental archive blob: ' + source)
            if type(row['archive_matches']) is not bool or row['archive_matches'] != (archive is not None and archive == row['git_blob']):
                errors.append('Supplemental archive match inconsistency: ' + source)
            if row['archive_tag'] != 'archive/writing-v1-v7':
                errors.append('Unexpected supplemental archive tag: ' + source)
        elif kind is None:
            tracked.append(row)
        else:
            errors.append('Unexpected source kind: ' + source)
        if row['selection'] == 'include':
            dest = safe_path(row['destination_path'])
            if not source.startswith(prefix) or dest != source[len(prefix):]:
                errors.append('Source/destination mapping mismatch: ' + source)
            if dest in expected or dest in ACCOUNTING or dest in AUTHORED:
                errors.append('Duplicate or reserved destination: ' + dest)
            expected[dest] = row['git_mode']
            included.append(row)
        elif row['selection'] != 'exclude' or row['destination_path'] is not None:
            errors.append('Invalid selection/destination: ' + source)
    actual_tree = {r['source_path']: (r['git_mode'], r['git_blob']) for r in tracked}
    if actual_tree != expected_tree:
        errors.append('Source accounting differs from independently recorded Git tree')
    counts = {
        'tracked_entries': len(tracked),
        'included_tracked': sum(r['selection'] == 'include' for r in tracked),
        'excluded_tracked': sum(r['selection'] == 'exclude' for r in tracked),
        'supplemental_entries': len(supplements),
        'supplemental_included': sum(r['selection'] == 'include' for r in supplements),
        'supplemental_archive_matches': sum(r['archive_matches'] for r in supplements),
        'included_bytes': sum(r['size'] for r in included),
    }
    for key, value in counts.items():
        if summary[key] != value:
            errors.append('Source summary count mismatch: ' + key)
    if summary['selection_reasons'] != dict(collections.Counter(r['reason'] for r in rows)):
        errors.append('Source summary selection reasons mismatch')
    seen_authored = set()
    for row in release_rows:
        dest = safe_path(row['path'])
        if dest in seen_authored or dest in expected or dest in ACCOUNTING:
            errors.append('Duplicate or reserved release-authored path: ' + dest)
        seen_authored.add(dest)
        if row['source_kind'] != 'release_authored' or not digest(row['sha256'], 64) or type(row['size']) is not int or row['size'] < 0:
            errors.append('Invalid release-authored accounting: ' + dest)
        expected[dest] = '100644'
    if seen_authored != AUTHORED:
        errors.append('Release-authored inventory differs from required release entrypoints')
    expected.update({path: '100644' for path in ACCOUNTING})
    for path in expected:
        if any(str(parent) in expected for parent in PurePosixPath(path).parents):
            errors.append('Payload path conflicts with a parent: ' + path)
    if summary['snapshot_copied'] is not True or summary['schema_version'] != 1:
        errors.append('Manifest does not describe a supported copied snapshot')
    return tracked, included, expected


def git_index(expected, actual_blobs, errors):
    if not (ROOT / '.git').exists():
        print('INFO: No .git metadata; exported payload checked without Git index verification')
        return
    try:
        output = subprocess.check_output(['git', '-C', str(ROOT), 'ls-files', '--stage', '-z'], stderr=subprocess.PIPE)
        indexed = {}
        for record in output.split(b'\0'):
            if not record:
                continue
            meta, path = record.split(b'\t', 1)
            mode, blob, stage = meta.decode('ascii').split()
            rel = os.fsdecode(path)
            if rel in indexed or stage != '0':
                errors.append('Duplicate or unmerged Git index entry: ' + rel)
            indexed[rel] = (mode, blob)
        if set(indexed) != set(expected):
            errors.append('Git index inventory mismatch; missing=%r; unexpected=%r' % (sorted(set(expected) - set(indexed)), sorted(set(indexed) - set(expected))))
        for rel in set(indexed) & set(expected) & set(actual_blobs):
            if indexed[rel] != (expected[rel], actual_blobs[rel]):
                errors.append('Git index mode/blob differs from actual payload: ' + rel)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        errors.append('Git index check: ' + str(exc))


def main():
    errors = []
    try:
        summary = json.loads(payload(ROOT / 'release/source_summary.json', '100644'))
        rows = [json.loads(line) for line in payload(ROOT / 'release/source_manifest.jsonl', '100644').splitlines()]
        tree = [json.loads(line) for line in payload(ROOT / 'release/source_tree.jsonl', '100644').splitlines()]
        release_rows = json.loads(payload(ROOT / 'release/release_files.json', '100644'))
        tracked, included, expected = accounting(summary, rows, tree, release_rows, errors)
        found = inventory()
        if found != set(expected):
            errors.append('Filesystem inventory mismatch; missing=%r; unexpected=%r' % (sorted(set(expected) - found), sorted(found - set(expected))))
        records = {r['destination_path']: r for r in included}
        records.update({r['path']: r for r in release_rows})
        actual_blobs = {}
        for rel, mode in expected.items():
            try:
                data = payload(ROOT / rel, mode)
                actual_blobs[rel] = blob_id(data)
                row = records.get(rel)
                if row is not None:
                    if len(data) != row['size'] or hashlib.sha256(data).hexdigest() != row['sha256']:
                        raise ValueError('Byte hash mismatch')
                    if 'git_blob' in row and actual_blobs[rel] != row['git_blob']:
                        raise ValueError('Raw Git blob mismatch')
                    if row.get('archive_matches') and actual_blobs[rel] != row['archive_blob']:
                        raise ValueError('Archive Git blob mismatch')
            except (OSError, ValueError) as exc:
                errors.append(rel + ': ' + str(exc))
        git_index(expected, actual_blobs, errors)
        code_ext = {'.py', '.cs', '.shader', '.sh', '.bash', '.ps1', '.m', '.cpp', '.c', '.h', '.js', '.ts'}
        omitted = [r['source_path'] for r in tracked if r['source_path'].startswith('ug_thesis_2026/') and Path(r['source_path']).suffix.lower() in code_ext and r['selection'] != 'include' and r['source_path'] != 'ug_thesis_2026/scripts/claude_usage_profile.py']
        if omitted:
            errors.append('Omitted scientific source: ' + ', '.join(omitted))
        for top in ('v1', 'v2', 'v3', 'eval', 'thesis', 'journal'):
            unexpected = [r['source_path'] for r in tracked if r['source_path'].startswith('ug_thesis_2026/' + top + '/') and r['selection'] == 'exclude' and Path(r['source_path']).name not in {'RULES.md', 'SESSION_REVIEW.md', 'BRIEF.md', 'STATE.md', 'HANDOVER.md', 'PROJECT_STATUS.md', 'AGENTS.md', 'CLAUDE.md', 'CHAPTER_REVIEW.md'}]
            if unexpected:
                errors.append('Incomplete scientific track ' + top)
        deck_error_count = len(errors)
        with ZipFile(ROOT / 'presentation/defense_2026/Thesis_Defence_2026.pptx') as archive:
            corrupt = archive.testzip()
            if corrupt:
                errors.append('Corrupt deck member: ' + corrupt)
            slides = [n for n in archive.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')]
            external = []
            for name in archive.namelist():
                if name.endswith('.rels'):
                    external.extend((name, e.get('Target')) for e in ET.fromstring(archive.read(name)) if e.get('TargetMode') == 'External' and e.get('Type', '').rsplit('/', 1)[-1] in {'video', 'media', 'audio', 'image'})
            if external:
                errors.append('Deck has external media relationships')
            if len(errors) == deck_error_count:
                print('PASS: defence package integrity; %d slide XML files; %d external media links' % (len(slides), len(external)))
    except (OSError, ValueError, KeyError, TypeError, AttributeError, BadZipFile, ET.ParseError) as exc:
        errors.append('Release check: ' + str(exc))
    for error in errors:
        print('FAIL:', error)
    if errors:
        return 1
    print('PASS: %d tracked source entries accounted; %d copied source files/symlinks match SHA-256 and Git blobs' % (len(tracked), len(included)))
    print('PASS: exact %d-file payload inventory and Git modes; Git index checked when present' % len(expected))
    print('Source commit:', summary['source_commit'])
    print('Reference implementation: v1 (frozen); v2 development paused; v3 exploratory')
    print('Scope: static evidence/package checks. Hardware, full recording replay, figure regeneration, and native Word/PowerPoint playback are not tested.')
    print('Trust limit: source commit identity is recorded; offline accounting alone does not authenticate the source Git commit.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
