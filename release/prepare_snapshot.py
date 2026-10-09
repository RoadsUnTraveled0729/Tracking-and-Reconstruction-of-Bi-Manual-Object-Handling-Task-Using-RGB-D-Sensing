#!/usr/bin/env python3
"""Export an explicitly selected thesis tree from an immutable workspace commit."""
import argparse
import collections
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

PREFIX = 'ug_thesis_2026/'
CODE_EXT = {'.py', '.cs', '.shader', '.sh', '.bash', '.ps1', '.m', '.cpp', '.c', '.h', '.js', '.ts'}
WORKFLOW_NAMES = {'AGENTS.md', 'CLAUDE.md', 'HANDOVER.md', 'PROJECT_STATUS.md', 'SESSION_REVIEW.md', 'RULES.md', 'BRIEF.md', 'STATE.md', 'CHAPTER_REVIEW.md'}
EXTERNAL_NOTES = {'CANADA_LABS_2026-10-07.md', 'GPU_RENTAL_2026-10-07.md', 'UBC_ADMISSIONS_2026-10-07.md', 'UBC_ENGINEERING_FACULTY_2026-10-07.md', 'BERKELEY_LITREVIEW_2026-10-07.md', 'CVPR_BAR_AND_BERKELEY_2026-10-07.md', 'ENGINEERING_ROUTE_2026-10-07.md', 'FINAL_ENGINEERING_SHORTLIST_2026-10-07.md'}
EDITORIAL_RECORDS = {
    'writing/v8/CH7_HANDOVER_TEXT_CHANGES.md',
    'writing/v8/CH9_SPLIT_TEXT_CHANGES.md',
    'writing/v8/condensed/CH7_TRAILS_TEXT_CHANGES.md',
    'writing/v9/CH7_TRAILS_TEXT_CHANGES.md',
    'presentation/defense_2026/review/BANK_REVISION_DELIVERY_MILESTONE.json',
    'presentation/defense_2026/review/BANK_REVISION_MEDIA_MILESTONE.json',
}


def select(path):
    if not path.startswith(PREFIX):
        return False, 'workspace material outside thesis scope'
    p = path[len(PREFIX):]
    if p in EDITORIAL_RECORDS:
        return False, 'internal editorial or delegation task record; scientific evidence retained separately'
    parts = Path(p).parts
    name = parts[-1]
    ext = Path(p).suffix.lower()
    if name in WORKFLOW_NAMES or p in {'knowledge/workflow_procedure.md','knowledge/markdown_audit.md','scripts/claude_usage_profile.py','writing/WRITING_SKILL.md','README.md','.gitignore'}:
        return False, 'workspace instructions, orchestration, handoff, or replaced release entrypoint'
    if parts[0] == '.agent':
        return (True, 'scientific decision and finding provenance') if name in {'DECISIONS.md','FINDINGS.md'} else (False, 'internal agent protocol or agent skill')
    if parts[0] == 'skill_set':
        allowed = {'evaluation-scenario-separation.md','marker-simplicity.md','measurement-precision-reporting.md','r5-experiment-state.md','subject-arm-lengths.md','unity-capture-checks.md','v2-r5-probe-state.md','v3-rtmpose-exploration-plan.md','exploration-round-2026-09.md'}
        return (True, 'scientific procedure and reproduction constraints') if name in allowed else (False,'agent or editorial workflow procedure')
    if ext in CODE_EXT:
        return True, 'scientific implementation, experiment, validation, or artifact-building source'
    if p.startswith('Unity/'):
        return (True, 'complete Unity source project and asset metadata') if parts[1] in {'Assets','Packages','ProjectSettings'} else (False, 'generated Unity capture or cache')
    if p.startswith(('v1/','v2/','v3/','eval/','thesis/','journal/')):
        return True, 'scientific model, configuration, fixture, calibration, pinned measurement, or result evidence'
    if p.startswith('writing/reviews/'):
        return False, 'internal editorial agent review'
    if p.startswith('writing/'):
        if any(t in p.lower() for t in ('language_compliance','language_review','humanizer','condense_editor','self_reference_revision/language','language_final','clarity_review')):
            return False, 'internal editorial agent language audit or task output'
        if '/zh/' in p:
            return False, 'unrequested translated manuscript or translation input'
        if ext in {'.docx','.pdf'}:
            v9parts = {'Abstract_V9.docx','Appendices.docx','FrontMatter_V9.docx','Thesis_V9.docx','Thesis_V9.pdf','Thesis_V9_TOC.docx'}
            if parts[1] == 'v9' and len(parts)==3 and (name in v9parts or name.startswith('Chapter_')):
                return True, 'final V9 artifact or chapter dependency of current V9 assembly/checkers'
            return False, 'obsolete manuscript binary or intermediate rendered document'
        if name.startswith('notes_') or any(t in name.upper() for t in ('BRIEF','SESSION_REVIEW','HUMANIZER','LANGUAGE_REVIEW','LANGUAGE_COMPLIANCE','CONDENSE_SUMMARY','PROGRESS','CHANGELOG','EDITOR_RULES')):
            return False, 'internal editorial drafting, task brief, or session log'
        return True, 'manuscript source asset, mathematical provenance, scientific audit evidence, or builder input'
    if p.startswith('presentation/'):
        if '/share/' in p or '/package/' in p or '/committee_materials/' in p:
            return False, 'duplicate delivery package or committee media copy; canonical deck and media retained'
        if '/review/' in p:
            if ext in {'.json','.csv','.png','.txt','.log'} and not any(t in name.upper() for t in ('AGENT','REVIEWER','CODE_REVIEW','LAYOUT_REVIEW')):
                return True, 'presentation scientific/artifact validation evidence'
            return False, 'internal editorial review or task log'
        if ext in {'.docx','.pdf','.pptx'}:
            final = name.startswith('Thesis_Defence_2026') or name.startswith('COMMITTEE_QUESTIONS')
            return (True, 'final defence deck, speaker script, outline/QA guide, or committee questions') if final and len(parts)==3 else (False,'obsolete or duplicate presentation binary')
        return True, 'defence source, media, numerical experiment, measurement log, or artifact manifest'
    if p.startswith('research/'):
        return (False,'personal academic/career planning outside thesis review scope') if name in EXTERNAL_NOTES else (True,'technical research/literature evidence')
    if p.startswith('knowledge/'):
        return True, 'verified scientific fact and source pointer'
    if p in {'ASSUMPTIONS.md','writing/GLOSSARY.md','writing/DEFENSE_QA.md'}:
        return True, 'scientific assumptions or defence/reference material'
    return False, 'non-scientific root or workflow material'

def git(root, *args):
    return subprocess.check_output(['git','-C',str(root),*args])

def tree(root, commit):
    rows=[]
    for raw in git(root,'ls-tree','-r','-z',commit).split(b'\0'):
        if not raw: continue
        meta,name=raw.split(b'\t',1)
        mode,typ,blob=meta.decode().split()
        if typ != 'blob': raise RuntimeError('Unsupported Git object: '+name.decode())
        rows.append((name.decode(),mode,blob))
    return rows

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--commit',required=True)
    parser.add_argument('--destination',type=Path,required=True)
    parser.add_argument('--copy',action='store_true')
    a=parser.parse_args()
    commit=git(a.source,'rev-parse',a.commit+'^{commit}').decode().strip()
    dest=a.destination.resolve()
    if dest==a.source.resolve() or a.source.resolve() in dest.parents:
        raise RuntimeError('Release destination must be separate from source workspace')
    (dest/'release').mkdir(parents=True,exist_ok=True)
    tracked=tree(a.source,commit)
    records=[]
    batch=subprocess.Popen(['git','-C',str(a.source),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    for path,mode,blob in tracked:
        batch.stdin.write((blob+'\n').encode());batch.stdin.flush()
        header=batch.stdout.readline().decode().split()
        content=batch.stdout.read(int(header[2])); assert batch.stdout.read(1)==b'\n'
        include,reason=select(path)
        rel=path[len(PREFIX):] if path.startswith(PREFIX) else None
        record={'source_path':path,'destination_path':rel if include else None,'selection':'include' if include else 'exclude','reason':reason,'source_commit':commit,'git_mode':mode,'git_blob':blob,'size':len(content),'sha256':hashlib.sha256(content).hexdigest()}
        records.append(record)
        if a.copy and include:
            target=dest/rel; target.parent.mkdir(parents=True,exist_ok=True)
            if target.exists() or target.is_symlink():
                before=os.readlink(target).encode() if target.is_symlink() else target.read_bytes()
                if before != content: raise RuntimeError('Refusing conflicting destination: '+rel)
            elif mode=='120000':target.symlink_to(content.decode())
            else:
                target.write_bytes(content);target.chmod(0o755 if mode=='100755' else 0o644)
    batch.stdin.close();batch.wait()
    # Archived code/assets remain supplemental: never re-add to workspace Git.
    archive='archive/writing-v1-v7'
    archived={p:(m,b) for p,m,b in tree(a.source,archive)}
    supplemental=[]
    script_text=[]
    for version in range(1,10):
        for script in (a.source/PREFIX/'writing'/('v'+str(version))).rglob('*.py'):
            if '__pycache__' not in script.parts:
                script_text.append((str(script.relative_to(a.source/PREFIX)),script.read_text(errors='replace')))
    for version in range(1,8):
        root=a.source/PREFIX/'writing'/('v'+str(version))
        for source in sorted(root.rglob('*')):
            if not source.is_file() or source.is_symlink() or '__pycache__' in source.parts:continue
            if source.suffix != '.py' and 'figures' not in source.relative_to(root).parts and source.name!='references.md':continue
            rel=str(source.relative_to(a.source/PREFIX))
            content=source.read_bytes();blob=git(a.source,'hash-object',str(source)).decode().strip()
            references=[p for p,text in script_text if source.name in text]
            include_supplement=source.suffix=='.py' or bool(references)
            original=rel
            pinned=archived.get(original)
            row={'source_path':PREFIX+rel,'destination_path':rel if include_supplement else None,'selection':'include' if include_supplement else 'exclude','reason':'optional historical source or script-referenced asset; not required by current V9' if include_supplement else 'optional historical asset without a filename reference from shipped manuscript scripts','source_commit':commit,'source_kind':'local_ignored_supplement','dependency_scope':'optional historical scripts and associated inputs, not V9 closure','asset_reference_sources':references if source.suffix!='.py' else [],'archive_tag':archive,'archive_blob':pinned[1] if pinned else None,'archive_matches':bool(pinned and pinned[1]==blob),'git_mode':'100755' if source.stat().st_mode&0o111 else '100644','git_blob':blob,'size':len(content),'sha256':hashlib.sha256(content).hexdigest()}
            supplemental.append(row)
            if a.copy and include_supplement:
                target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True)
                if target.exists() and target.read_bytes()!=content:raise RuntimeError('Conflicting supplement: '+rel)
                if not target.exists():shutil.copy2(source,target)
    with (dest/'release/source_manifest.jsonl').open('w') as f:
        for r in records+supplemental:f.write(json.dumps(r,sort_keys=True)+'\n')
    with (dest/'release/source_tree.jsonl').open('w') as f:
        for p,m,b in tracked:f.write(json.dumps({'path':p,'mode':m,'blob':b},sort_keys=True)+'\n')
    summary={'schema_version':1,'source_workspace':str(a.source.resolve()),'source_thesis_prefix':PREFIX,'source_commit':commit,'source_tree':git(a.source,'rev-parse',commit+'^{tree}').decode().strip(),'snapshot_copied':a.copy,'tracked_entries':len(records),'included_tracked':sum(r['selection']=='include' for r in records),'excluded_tracked':sum(r['selection']=='exclude' for r in records),'supplemental_entries':len(supplemental),'supplemental_included':sum(r['selection']=='include' for r in supplemental),'supplemental_archive_matches':sum(r['archive_matches'] for r in supplemental),'included_bytes':sum(r['size'] for r in records+supplemental if r['selection']=='include'),'selection_reasons':dict(collections.Counter(r['reason'] for r in records+supplemental))}
    (dest/'release/source_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    authored=['README.md','.gitignore','Video/README.md','release/prepare_snapshot.py','release/reviewer_smoke.py','release/SELECTION.md','release/REPRODUCTION.md','release/THIRD_PARTY_NOTICES.md','release/system.svg']
    release_rows=[]
    for rel in authored:
        path=dest/rel
        if path.is_file():
            data=path.read_bytes()
            release_rows.append({'path':rel,'source_kind':'release_authored','reason':'reviewer navigation, verification, selection, or excluded-data placeholder','size':len(data),'sha256':hashlib.sha256(data).hexdigest()})
    (dest/'release/release_files.json').write_text(json.dumps(release_rows,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,indent=2,sort_keys=True))
if __name__=='__main__':main()
