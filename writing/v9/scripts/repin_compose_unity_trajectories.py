#!/usr/bin/env python3
"""Regenerate the pins of audit_evidence/ch7_visual_restoration/compose_unity_trajectories.py.

That composer refuses to run unless every input it names still carries the
sha256 written into its own source, and unless human.json still reports the
Table 7.3 and 7.4 sample counts it recorded. The pins are a tamper check on
the inputs, not a result: when the inputs legitimately change, the pins must
be recomputed from the new inputs, never hand-typed and never widened.

E-036 and E-037 replaced the three Unity captures with per-recording avatar
sizing, so the capture manifests, the view configurations, the native
compositions and the accepted r6b frame count all moved. This script exists
because the composer ships no --repin option and no companion re-pinning
script; it recomputes every pinned constant from the files on disk and
rewrites the literals in place, printing old and new for each one.

It never invents a value: every sha256 comes from hashing the file the
composer itself names, every sample count comes from human.json, and the
expected output dimensions come from running the composer's own compose()
on the re-pinned inputs. Nothing is relaxed: a pin that already matches is
left untouched, and the checks themselves are not removed.

Run from the repository root, AFTER regenerating human.json
(evaluate_ch7_restructured.py) and the native compositions
(make_ch7_trails_fig.py for r6b and r7):
    /home/luo/anaconda3/bin/python writing/v9/scripts/repin_compose_unity_trajectories.py
Then run compose_unity_trajectories.py, which must now pass.
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
COMPOSER = REPO / 'writing/v9/audit_evidence/ch7_visual_restoration/compose_unity_trajectories.py'
# Keys the composer verifies in verify_sources(), in its own order.
HASHED = ('layout_reference', 'compose', 'capture', 'view', 'trails',
          'intervals', 'historical_states', 'handover_intervals')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_header(text):
    """Execute the composer's constant block only (everything before its
    first function), so ASSETS and the module-level pins are available
    without importing the composer and running its checks."""
    namespace = {'__file__': str(COMPOSER)}
    exec(compile(text.split('\ndef digest(')[0], str(COMPOSER), 'exec'), namespace)
    return namespace


def replace_once(text, old, new, label):
    if old == new:
        print(f'  keep   {label}: {old}')
        return text, False
    if text.count(old) != 1:
        raise SystemExit(f'{label}: {text.count(old)} occurrences of {old!r}, '
                         'refusing to guess which literal to rewrite')
    print(f'  repin  {label}: {old} -> {new}')
    return text.replace(old, new), True


def main():
    text = COMPOSER.read_text()
    namespace = load_header(text)
    changed = 0

    print('sha256 pins')
    for label, path, pinned in (
            ('NATIVE_COMPOSER_SHA256', namespace['NATIVE_COMPOSER'],
             namespace['NATIVE_COMPOSER_SHA256']),
            ('TABLE_SCOPE_SHA256', namespace['TABLE_SCOPE'],
             namespace['TABLE_SCOPE_SHA256'])):
        text, hit = replace_once(text, pinned, digest(path), label)
        changed += hit
    for alias, spec in namespace['ASSETS'].items():
        for key in HASHED:
            if key not in spec:
                continue
            path = spec[key]
            if not Path(path).exists():
                print(f'  absent {alias}.{key}: {path} (optional source, pin left)')
                continue
            text, hit = replace_once(text, spec[f'{key}_sha256'], digest(path),
                                     f'{alias}.{key}_sha256')
            changed += hit

    print('table sample counts (from human.json, Decisions D-031 and D-032)')
    scope = json.loads(Path(namespace['TABLE_SCOPE']).read_text())
    for alias, spec in namespace['ASSETS'].items():
        pinned = spec['table_samples']
        actual = {name: scope[alias]['joints'][name]['n'] for name in pinned}
        if actual == pinned:
            print(f'  keep   {alias}.table_samples: {actual}')
            continue
        old_literal = '{' + ', '.join(f'"{k}": {v}' for k, v in pinned.items()) + '}'
        new_literal = '{' + ', '.join(f'"{k}": {v}' for k, v in actual.items()) + '}'
        text, hit = replace_once(text, old_literal, new_literal,
                                 f'{alias}.table_samples')
        changed += hit

    if changed:
        COMPOSER.write_text(text)
        print(f'wrote {COMPOSER.relative_to(REPO)} ({changed} pins regenerated)')
    else:
        print('every pin already matched; file untouched')

    # The output dimensions are a property of the composition the re-pinned
    # inputs produce, so they are measured by running the composer's own
    # compose() rather than asserted. This reloads the file just written.
    print('expected output dimensions (measured by the composer itself)')
    spec_module = importlib.util.spec_from_file_location('ch7_compose', COMPOSER)
    module = importlib.util.module_from_spec(spec_module)
    sys.modules['ch7_compose'] = module
    spec_module.loader.exec_module(module)
    text = COMPOSER.read_text()
    changed_dims = 0
    for alias, spec in module.ASSETS.items():
        module.verify_sources(alias, spec)
        try:
            _, dimensions = module.compose(alias, spec)
        except RuntimeError as error:
            message = str(error)
            if 'Unexpected output dimensions' not in message:
                raise
            dimensions = json.loads(message.split(': ', 1)[1])
        pinned = spec['expected_dimensions_px']
        text, hit = replace_once(text, json.dumps(pinned), json.dumps(dimensions),
                                 f'{alias}.expected_dimensions_px')
        changed_dims += hit
    if changed_dims:
        COMPOSER.write_text(text)
        print(f'wrote {COMPOSER.relative_to(REPO)} ({changed_dims} dimension pins regenerated)')
    print('PASS: pins regenerated from the files on disk; run '
          'compose_unity_trajectories.py now')


if __name__ == '__main__':
    main()
