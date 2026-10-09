#!/usr/bin/env python3
"""Slide 12 chain-growth film: the landmark chain lights up layer by layer from L24.

2026-10-06 (plan declarative-stargazing-phoenix.md, D-387). The final frame is
the slide 12 figure figures/coordinate_frames/overlay/overlay_landmark_frames.png
(make_frame_overlay_figures.py, spec_landmark_frames.json) with only its colours
changed. Geometry, faded photograph, dot radii, label offsets and the legend are
taken from that generator by import, and the drawing order is that of its
render_figure (bones in spec order, then dots with their labels, then legend).
Before encoding, the same renderer with the original colours must reproduce
overlay_landmark_frames.png pixel for pixel, otherwise the run stops.

Layer order (author, 2026-10-06): L24 -> L23, L12, L11 -> L13, L14 -> L15, L16.
Each bone is drawn grey until its child end is reached, grows from parent to
child over 0.5 s in the colour of the child's layer, and the child dot changes
to its layer colour on arrival. Labels stay white; a legend line takes its
layer colour once every landmark it names is lit.

Run from the repository root with the thesis Python:

    /home/luo/anaconda3/bin/python -B presentation/defense_2026/anim/chain_growth.py [--review-dir DIR]

Writes media/p12_chain_growth.mp4, media/p12_chain_growth_poster.png (last
frame) and media/provenance/p12_chain_growth.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402
import make_frame_overlay_figures as MF  # noqa: E402

SPEC = MF.OUT / 'spec_landmark_frames.json'
REFERENCE = MF.OUT / 'overlay_landmark_frames.png'
MOVIE = HERE / 'media' / 'p12_chain_growth.mp4'
POSTER = HERE / 'media' / 'p12_chain_growth_poster.png'
PROVENANCE = HERE / 'media' / 'provenance' / 'p12_chain_growth.json'

# Frame rate and encoder: anim/bank_axes_kinematics.py build() (FPS 30 from
# unified_panels.py, libx264 preset slow, CRF 19, yuv420p, faststart).
FPS = 30
CRF = 19

# Colours: L24 red and layers three/two follow the deck axis colours
# (anim/coordinate_axes.py AXIS_COLORS X/Y/Z); amber #E8B35A is the slide 21
# accent; unlit grey #656565 is GREY_EDGE of anim/unified_panels.py. The
# assignment of colour to layer is the author's (2026-10-06).
GREY = MF.hexrgb('#656565')
LAYERS = [
    {'name': 'layer one', 'colour': '#FF4040', 'landmarks': [24]},
    {'name': 'layer two', 'colour': '#40E070', 'landmarks': [23, 12, 11]},
    {'name': 'layer three', 'colour': '#408CFF', 'landmarks': [13, 14]},
    {'name': 'layer four', 'colour': '#E8B35A', 'landmarks': [15, 16]},
]
LAYER_OF = {lm: i for i, layer in enumerate(LAYERS) for lm in layer['landmarks']}
# Growth steps as (parent, child) bones (plan assumption A1: every bone of the
# current figure, assigned to the layer of its child end; L11 is reached from
# L12 and L23 after both are lit, so layer two has two back-to-back steps).
STEPS = [
    {'name': 'layer two a', 'bones': [(24, 23), (24, 12)]},
    {'name': 'layer two b', 'bones': [(12, 11), (23, 11)]},
    {'name': 'layer three', 'bones': [(12, 14), (11, 13)]},
    {'name': 'layer four', 'bones': [(14, 16), (13, 15)]},
]
# Timeline in frames at 30 fps. Growth 0.5 s per step (brief). Holds are a
# judgement call (master decision 2026-10-06, D-387): the brief's 0.6 s / 0.4 s
# holds gave 5.4 s against the author's target of about 8 s, so the first hold
# is 1.0 s, the holds after layers two and three 1.5 s, the final hold 2.0 s.
GROW = 15
TIMELINE = [('hold', 'start', 30),
            ('grow', 0, GROW), ('grow', 1, GROW), ('hold', 'after layer two', 45),
            ('grow', 2, GROW), ('hold', 'after layer three', 45),
            ('grow', 3, GROW), ('hold', 'final', 60)]
# Legend lines (spec texts, in order) and the landmarks each one names.
LEGEND = {'shoulder  L11, L12': [11, 12], 'elbow  L13, L14': [13, 14],
          'wrist  L15, L16': [15, 16], 'hip  L23': [23], 'root  L24': [24]}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(path):
    return str(Path(path).resolve().relative_to(ROOT))


def bone_key(a, b):
    return frozenset((a, b))


def frame_states():
    """One state per output frame: lit landmarks and partial bone progress."""
    lit = {24}
    done = set()
    states, marks = [], {}
    for kind, what, count in TIMELINE:
        for k in range(count):
            partial = {}
            if kind == 'grow':
                p = (k + 1) / count
                for parent, child in STEPS[what]['bones']:
                    partial[bone_key(parent, child)] = (parent, child, p)
                if k == count - 1:
                    for parent, child in STEPS[what]['bones']:
                        done.add(bone_key(parent, child))
                        lit.add(child)
                    partial = {}
            states.append({'lit': set(lit), 'done': set(done), 'partial': dict(partial)})
        marks[f'{kind} {STEPS[what]["name"] if kind == "grow" else what}'] = len(states) - 1
    return states, marks


class Scene:
    def __init__(self):
        self.spec = json.loads(SPEC.read_text())
        self.lm = json.loads(MF.LANDMARK_JSON.read_text())
        if self.lm['photo_sha256'] != MF.sha(MF.rp(self.lm['photo'])):
            raise ValueError('T-pose landmark measurement is stale')
        if len(self.spec['panels']) != 1:
            raise ValueError('expected one photo panel')
        self.panel = MF.Panel(self.spec['panels'][0], None)
        self.size = tuple(self.spec.get('canvas_px', MF.CANVAS))
        base = np.zeros((self.size[1], self.size[0], 3), np.uint8)
        faded, self.interp = self.panel.render()
        x0, y0, x1, y1 = self.spec['panels'][0]['box_px']
        base[y0:y1, x0:x1] = faded
        self.base = base
        self.px = {int(i): self.panel.to_canvas(MF.landmark_px(self.lm, int(i)))
                   for i in self.lm['landmarks']}
        keys = [bone_key(ln['from'], ln['to']) for ln in self.spec['lines']]
        bones = [bone_key(p, c) for s in STEPS for p, c in s['bones']]
        if sorted(map(sorted, keys)) != sorted(map(sorted, bones)) or len(set(keys)) != len(keys):
            raise ValueError('growth bones do not match the spec lines one to one')
        if set(LEGEND) != {t['text'] for t in self.spec['texts']}:
            raise ValueError('legend lines differ from the spec texts')

    def render(self, state, original=False):
        cv = MF.Canvas(self.size)
        cv.im = Image.fromarray(self.base.copy())
        cv.draw = MF.MirroredDraw(cv.im, cv.drawn)
        layer_rgb = {lm: MF.hexrgb(LAYERS[LAYER_OF[lm]]['colour']) for lm in LAYER_OF}
        # bones in spec order: lit colour when done, grey otherwise
        for ln in self.spec['lines']:
            a, b = self.px[ln['from']], self.px[ln['to']]
            key = bone_key(ln['from'], ln['to'])
            if original:
                colour = tuple(ln.get('rgb', MF.SOFT))
            elif key in state['done']:
                child = next(c for s in STEPS for p, c in s['bones'] if bone_key(p, c) == key)
                colour = layer_rgb[child]
            else:
                colour = GREY
            cv.line(a, b, colour, width=ln.get('width', 5), dashed=ln.get('dashed', False))
        # partial segments of the growing bones, on top
        for parent, child, p in state['partial'].values():
            a = self.px[parent]
            b = a + p * (self.px[child] - a)
            cv.line(a, b, layer_rgb[child], width=5)
        # dots with their labels, spec order; labels keep the spec colour (white)
        for pt in self.spec['points']:
            xy = self.px[pt['landmark']]
            if original:
                fill = tuple(pt.get('rgb', MF.WHITE))
            else:
                fill = layer_rgb[pt['landmark']] if pt['landmark'] in state['lit'] else GREY
            cv.dot(xy, r=pt.get('radius', 10), fill=fill)
            lab = pt['label']
            cv.text(lab['text'], xy + np.asarray(lab['offset'], float),
                    anchor=lab.get('anchor', 'mm'), fill=tuple(lab.get('rgb', MF.WHITE)))
        # legend lines: unlit white, layer colour once all named landmarks are lit
        for tx in self.spec['texts']:
            names = LEGEND[tx['text']]
            if original:
                fill = tuple(tx.get('rgb', MF.WHITE))
            elif all(n in state['lit'] for n in names):
                fill = layer_rgb[names[0]]
            else:
                fill = MF.WHITE
            cv.text(tx['text'], tx['xy'], anchor=tx.get('anchor', 'la'), fill=fill)
        return cv.im, np.asarray(cv.drawn)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--review-dir', type=Path, help='also save review frames (PNG) into this directory')
    args = ap.parse_args()
    for layer in LAYERS:
        if len({LAYER_OF[lm] for lm in layer['landmarks']}) != 1:
            raise ValueError('layer table')
    for names in LEGEND.values():
        if len({LAYER_OF[n] for n in names}) != 1:
            raise ValueError('a legend line spans two layers')
    scene = Scene()
    states, marks = frame_states()
    final_state = states[-1]
    if final_state['lit'] != set(LAYER_OF) or len(final_state['done']) != len(scene.spec['lines']):
        raise ValueError('the last frame is not the complete chain')

    # Stop condition 2 of the plan: same geometry as the slide 12 figure.
    reference = np.asarray(Image.open(REFERENCE).convert('RGB'))
    original, _ = scene.render(final_state, original=True)
    original = np.asarray(original)
    if original.shape != reference.shape or not np.array_equal(original, reference):
        diff = int(np.any(original != reference, axis=-1).sum()) if original.shape == reference.shape else -1
        raise ValueError(f'original-colour reproduction differs from {rel(REFERENCE)} in {diff} pixels')
    final_im, final_mask = scene.render(final_state)
    final = np.asarray(final_im)
    changed = np.any(final != reference, axis=-1)
    if np.any(changed & (final_mask == 0)):
        raise ValueError('final frame differs from the figure outside drawn pixels')
    colour_check = {'reference': rel(REFERENCE), 'reference_sha256': sha(REFERENCE),
                    'original_colour_reproduction': 'pixel-identical',
                    'final_frame_pixels_differing_from_reference': int(changed.sum()),
                    'differing_pixels_outside_drawn_mask': 0}

    MOVIE.parent.mkdir(parents=True, exist_ok=True)
    PROVENANCE.parent.mkdir(parents=True, exist_ok=True)
    W, H = scene.size
    command = ['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
               '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-an', '-c:v', 'libx264',
               '-preset', 'slow', '-crf', str(CRF), '-threads', '2', '-pix_fmt', 'yuv420p',
               '-movflags', '+faststart', str(MOVIE)]
    proc = subprocess.Popen(command, stdin=subprocess.PIPE)
    review = {}
    wanted = {marks['hold start']: 'end_layer_one', marks['hold after layer two']: 'end_layer_two',
              marks['hold after layer three']: 'end_layer_three',
              marks['grow layer four']: 'end_layer_four', len(states) - 1: 'final',
              marks['hold start'] + 8: 'growing_layer_two_a'}
    cache = None
    for i, state in enumerate(states):
        key = (frozenset(state['lit']), frozenset(state['done']),
               tuple(sorted((tuple(sorted(k)), v[2]) for k, v in state['partial'].items())))
        if cache is None or cache[0] != key:
            im, _ = scene.render(state)
            cache = (key, im)
        im = cache[1]
        proc.stdin.write(im.tobytes())
        if args.review_dir and i in wanted:
            args.review_dir.mkdir(parents=True, exist_ok=True)
            path = args.review_dir / f'p12_{wanted[i]}_frame{i:03d}.png'
            im.save(path)
            review[wanted[i]] = str(path)
    proc.stdin.close()
    if proc.wait() != 0:
        raise RuntimeError('ffmpeg failed')
    if not np.array_equal(np.asarray(cache[1]), final):
        raise ValueError('last encoded frame is not the final frame')
    final_im.save(POSTER, format='PNG')
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(MOVIE), '-f', 'null', '-'], check=True)
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames',
        '-select_streams', 'v:0', '-show_entries',
        'stream=codec_name,pix_fmt,width,height,nb_read_frames,r_frame_rate,duration',
        '-of', 'json', str(MOVIE)]))['streams'][0]
    if int(probe['nb_read_frames']) != len(states) or [probe['width'], probe['height']] != [W, H]:
        raise ValueError(f'decode check failed: {probe}')

    report = {
        'status': 'PASS', 'slide': 12, 'kind': 'chain_growth',
        'purpose': ('Slide 12 "Linked landmarks and constraints": the landmark chain of the T-pose '
                    'figure lights up layer by layer from the root L24 (author request 2026-10-06, D-387).'),
        'asset': rel(MOVIE), 'poster': rel(POSTER), 'poster_is': 'last frame (complete chain)',
        'duration_s': len(states) / FPS, 'frames': len(states), 'fps': FPS, 'dimensions': [W, H],
        'sha256': {'mp4': sha(MOVIE), 'png': sha(POSTER)}, 'bytes': {'mp4': MOVIE.stat().st_size,
                                                                       'png': POSTER.stat().st_size},
        'inputs': {rel(p): sha(p) for p in [SPEC, MF.LANDMARK_JSON, MF.rp(scene.spec['panels'][0]['photo']),
                                            REFERENCE, Path(MF.__file__)]},
        'layers': [{**layer, 'landmarks': layer['landmarks']} for layer in LAYERS],
        'layer_order_note': ('Author order 2026-10-06: L24 -> L23, L12, L11 -> L13, L14 -> L15, L16. '
                             'The thesis groups L23 with L24 in level one; the deck follows the author here.'),
        'growth_steps': [{'name': s['name'], 'bones_parent_to_child': [list(b) for b in s['bones']]}
                         for s in STEPS],
        'timeline_frames': [{'kind': k, 'what': (STEPS[w]['name'] if k == 'grow' else w), 'frames': n,
                             'seconds': n / FPS} for k, w, n in TIMELINE],
        'timeline_last_frame_index': marks,
        'timing_decision': ('Growth 0.5 s per step (brief). Holds are a judgement call (master decision '
                            '2026-10-06, D-387): first hold 1.0 s, 1.5 s after layers two and three, '
                            'final hold 2.0 s; the briefed 0.6 s / 0.4 s holds gave 5.4 s against the '
                            'author target of about 8 s.'),
        'colour_rules': {'unlit_dots_and_bones': '#656565 (anim/unified_panels.py GREY_EDGE)',
                         'lit_bone': 'colour of the layer of its child end',
                         'growth': 'linear, parent to child, partial segment drawn on top',
                         'dot': 'changes to its layer colour on the frame its bones arrive',
                         'labels': 'white throughout (spec colour)',
                         'legend': 'white until every landmark the line names is lit, then the layer colour; '
                                   'root L24 red from the first frame'},
        'geometry_check': colour_check,
        'drawing_reused_from': {'generator': rel(Path(MF.__file__)), 'fade': MF.FADE, 'label_px': MF.LABEL_PX,
                                'font': MF.FONT, 'resample': 'cv2.' + scene.interp},
        'decode_check': probe,
        'encoding': {'command': command[:-1] + ['<asset>'],
                     'source': 'anim/bank_axes_kinematics.py build() ffmpeg call'},
        'generator': rel(Path(__file__)), 'generator_sha256': sha(Path(__file__)),
        'command': '/home/luo/anaconda3/bin/python -B presentation/defense_2026/anim/chain_growth.py',
        'interpreter': sys.executable, 'python': platform.python_version(),
        'playback_in_powerpoint': 'not verified (author check)',
    }
    PROVENANCE.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n', encoding='ascii')
    print(f'PASS: {rel(MOVIE)} {len(states)} frames, {len(states) / FPS:.3f} s, {report["sha256"]["mp4"]}')
    for name, path in review.items():
        print(f'review {name}: {path}')


if __name__ == '__main__':
    main()
