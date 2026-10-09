#!/usr/bin/env python3
"""Slide 34 figure: how the controlled-removal comparison was made.

Two modes, both writing media/p34_masked_comparison.png and its provenance
JSON on a black background (the deck's slide background, 000000):

- three-case (default since 2026-10-06, plan declarative-stargazing-phoenix.md
  Milestone B, D-392): three equal crops of the right arm from R7 colour frame
  489, side by side, titled "Hold last", "Direction memory", "Object-assisted".
  Each crop shows the unmasked reference chain shoulder-elbow-wrist in white,
  the removed elbow and wrist marked by red rings, that case's recovered chain
  shoulder-elbow-wrist in its colour, and one label "wrist <median> cm" with
  the case's wrist median over the window 445-489 (synthetic_pairs.csv). No
  error curves. Before drawing, the window travel values of thesis Table 7.5
  (0.6 / 2.8 / 5.1 cm) and the intermediate wrist medians of Table 7.7
  (1.2 / 1.9 / 1.2 cm) are read from writing/v9/Chapter_7_Evaluation.docx
  and the script stops on any difference.
- two-panel (the D-390 figure, 2026-10-06 first version): left the same frame
  with all three recovered chains and the label "removed for 45 frames";
  right wrist error (thick) and elbow error (thin) in cm against frame
  445-489 for the three cases, medians in the legend.

Data: writing/v9/audit_evidence/ch7_restructured/synthetic_pairs.csv (written
by writing/v9/scripts/evaluate_ch7_restructured.py synthetic(); reference and
reconstructed points in metres, y-up Camera' frame = sensor frame with y
flipped). The shoulder is not in that CSV; synthetic() takes it from the
filtered landmark CSV with y flipped (line 217), which is repeated here.

Frame choice (deviation from plan A3, D-390): the plan named the existing
still writing/v9/figures/src/r7_frame00450.png, but at frame 450 the three
recovered chains lie within 1 cm of the reference (under 5 px) and are hidden
under it. Frame 489 has the largest spread of the window (wrist 3.0 / 2.9 /
0.7 cm), so the chains separate. The frame is decoded here from the R7 bag
(Video/recording_20260909_000024.bag, pyrealsense2, sequential, no real-time
playback, as eval/inspect/check_v1_overlay.py does); the same decode of frame
450 must equal r7_frame00450.png byte for byte, which pins the frame index.

The medians for window 445-489 are checked against the slide 34 intermediate
rows of the deck (wrist 1.2 / 1.9 / 1.2, elbow 0.7 / 1.7 / 1.6 cm) and the
script stops on any difference. The deck is only read, never written.

Projection: pinhole without distortion, solver point flipped back to the
sensor frame (y -> -y), u = fx x / z + ppx, v = fy y / z + ppy; copied from
eval/failure/make_label_compare_fig.py project() (SCALE and crop removed).
Intrinsics: color_intrinsics of
v1/mediapipe/output/recording_20260909_000024_landmarks_raw.meta.json (the
same source eval/inspect/check_v1_overlay.py uses). The projection is checked
against the measured MediaPipe right elbow and wrist of the shown frame (filtered
CSV, sensor frame): the reference chain must project within MAX_PX of them.

Run from the repository root with the thesis Python:

    MPLCONFIGDIR=<scratch> /home/luo/anaconda3/bin/python -B presentation/defense_2026/anim/masked_comparison_figure.py [--mode three-case|two-panel]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from zipfile import ZipFile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from lxml import etree as E  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parents[1]
ROOT = HERE.parents[1]
STEM = 'recording_20260909_000024'
PAIRS = ROOT / 'writing/v9/audit_evidence/ch7_restructured/synthetic_pairs.csv'
SELECTION = ROOT / 'writing/v9/audit_evidence/ch7_restructured/synthetic_selection.json'
FRAME_PNG = ROOT / 'writing/v9/figures/src/r7_frame00450.png'
FILTERED = ROOT / f'v1/mediapipe/output/{STEM}_landmarks_filtered.csv'
META = ROOT / f'v1/mediapipe/output/{STEM}_landmarks_raw.meta.json'
CH7 = ROOT / 'writing/v9/Chapter_7_Evaluation.docx'
PPTX = HERE / 'Thesis_Defence_2026.pptx'
OUT_PNG = HERE / 'media' / 'p34_masked_comparison.png'
OUT_JSON = HERE / 'media' / 'provenance' / 'p34_masked_comparison.json'

WINDOW = 'intermediate motion'
START, STOP = 445, 489            # synthetic_selection.json, intermediate window
FRAME = 489                       # shown frame: last masked frame, largest spread
CHECK_FRAME = 450                 # decoded too, must equal FRAME_PNG
BAG = ROOT / 'Video' / f'{STEM}.bag'
METHODS = ['hold-last', 'direction memory', 'object-assisted']
LABEL = {'hold-last': 'Hold-last', 'direction memory': 'Direction memory',
         'object-assisted': 'Object-assisted'}
# Three-case panel titles: plan Milestone B, verbatim.
TITLE = {'hold-last': 'Hold last', 'direction memory': 'Direction memory',
         'object-assisted': 'Object-assisted'}
# Colours: plan assumption A2 (the deck's own: white reference, BBBBBB grey,
# B48CFF violet, E8B35A amber highlight, FF4040 red as in the slide 12 film).
COLOUR = {'hold-last': '#BBBBBB', 'direction memory': '#B48CFF', 'object-assisted': '#E8B35A'}
REF, RED, BG, FG = '#FFFFFF', '#FF4040', '#000000', '#FFFFFF'
# Slide 34 intermediate rows (ids 25-27 wrist, 43-45 elbow; deck read below).
SLIDE_IDS = {'wrist': (25, 26, 27), 'elbow': (43, 44, 45)}
# Thesis Chapter 7 values the three-case mode re-reads from the docx before drawing:
# Table 7.5 reference wrist excursion per window (frame range -> cm) and Table 7.7
# intermediate-window wrist medians (method -> cm). Source: Chapter_7_Evaluation.docx.
TABLE75 = {'490 to 534': '0.6', '445 to 489': '2.8', '557 to 601': '5.1'}
TABLE77_WRIST = {'Hold-last': '1.2', 'Direction memory': '1.9', 'Object-assisted': '1.2'}
# Size: plan A2, 5.0 x 3.85 in on the slide, rendered at 300 dpi = 1500 x 1155 px.
FIG_IN, DPI = (5.0, 3.85), 300
# Two-panel font sizes in pt at 300 dpi (px = pt * 300 / 72). Master decision 5 (2026-10-06,
# after viewing the first render): legend at least 36 px (8.64 pt) and axis labels at least
# 40 px (9.6 pt) at the 1500 px output width. 9.0 pt = 37.5 px, 10.0 pt = 41.7 px.
FS_AXIS, FS_TICK, FS_LEG, FS_NOTE = 10.0, 9.0, 9.0, 9.0
CROP = (140, 70, 310, 380)        # two-panel: x0, y0, x1, y1 original pixels (judgement, viewed)
# Projection check tolerance: 2 cm at 1.27 m depth is 9.6 px (fx 607); the reference is
# the plain FK, whose right-wrist distance to the measured wrist has p95 1.9 cm on R7
# (check_v1_overlay.py baseline run 2026-10-06). 12 px rounds that up (judgement).
MAX_PX = 12.0

# Three-case layout (all in output pixels, 1500 x 1155).
# Minimum text size: Milestone B brief, every text at least 40 px tall. Checked two ways:
# the font size in px at 300 dpi (the two-panel font_px_at_dpi measure) and the rendered ink
# height of each text in the PNG (top of the tallest glyph to the lowest dark-free row). A first
# render at 11 pt (45.8 px) gave 36 px of ink for "Hold last" and "wrist 1.2 cm" (no
# descenders), so 12.5 pt = 52.1 px is used: measured ink 40 px for those texts (50 px with
# descenders), "Direction memory" 469 px wide in a 490 px panel, so the size cannot grow much.
MIN_TEXT_PX = 40.0
FS3_TITLE, FS3_LABEL = 12.5, 12.5
INK_LEVEL = 60                    # 8-bit level above which a band pixel counts as text ink (black band)
GAP3_PX = 15                      # gap between the three crops (judgement, viewed)
TITLE3_PX = 80                    # title band above each crop (judgement: 45.8 px font + margin)
# Crop of the right arm in original 640 x 480 pixels: x 150..300 contains the projected chain
# points of frame 489 (x 201..260, shoulder to wrist) with margin and the hand; y0 60 is above
# the shoulder (y 84); y1 follows from the panel aspect (computed in render_three_case).
CROP3_X, CROP3_Y0 = (150, 300), 60
# Line and marker sizes in pt (judgement, viewed at 1500 px).
LW3_CASE, LW3_REF, LW3_HALO = 3.2, 1.6, 3.0
MS3_RING, MEW3_RING, MS3_JOINT = 19, 2.2, 5.0


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def project(p_solver, K):
    """Solver-space point -> pixel (u, v); copied from make_label_compare_fig.project()."""
    x, y, z = float(p_solver[0]), -float(p_solver[1]), float(p_solver[2])
    if z <= 0.05:
        return None
    return K['fx'] * x / z + K['ppx'], K['fy'] * y / z + K['ppy']


def decode_bag(frames):
    """BGR colour frames of the R7 bag by 0-based index (sequential read)."""
    import cv2
    import pyrealsense2 as rs
    pipe, cfg = rs.pipeline(), rs.config()
    cfg.enable_device_from_file(str(BAG), repeat_playback=False)
    prof = pipe.start(cfg)
    prof.get_device().as_playback().set_real_time(False)
    fmt = prof.get_stream(rs.stream.color).format()
    out, i = {}, 0
    try:
        while i <= max(frames):
            cf = pipe.wait_for_frames(2000).get_color_frame()
            if not cf:
                continue
            if i in frames:
                img = np.asanyarray(cf.get_data()).copy()
                out[i] = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) if fmt == rs.format.rgb8 else img
            i += 1
    finally:
        pipe.stop()
    return out


def slide34_values():
    N = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
         'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
    with ZipFile(PPTX) as z:
        root = E.fromstring(z.read('ppt/slides/slide34.xml'))
    out = {}
    for sp in root.find('p:cSld/p:spTree', N):
        c = sp.find('.//p:cNvPr', N)
        if c is not None:
            out[int(c.get('id'))] = ''.join(t.text or '' for t in sp.findall('.//a:t', N))
    return {joint: [float(out[i]) for i in ids] for joint, ids in SLIDE_IDS.items()}


def thesis_tables():
    """Table 7.5 and Table 7.7 rows of Chapter 7 (read only), checked against TABLE75/TABLE77_WRIST.

    A caption in this docx follows its table, so each table is matched to the next caption.
    """
    import docx
    from docx.table import Table
    from docx.text.paragraph import Paragraph
    doc = docx.Document(str(CH7))
    pending, tables = None, {}
    for el in doc.element.body.iterchildren():
        tag = el.tag.split('}')[1]
        if tag == 'tbl':
            pending = [[c.text for c in r.cells] for r in Table(el, doc).rows]
        elif tag == 'p':
            text = Paragraph(el, doc).text
            for n in ('7.5', '7.7'):
                if text.startswith(f'Table {n}.') and pending is not None:
                    tables[n] = {'caption': text, 'rows': pending}
    for n in ('7.5', '7.7'):
        if n not in tables:
            raise SystemExit(f'ERROR: Table {n} not found in {CH7.name}')
    t75 = tables['7.5']['rows']
    if t75[0] != ['Window', 'Frame range', 'n', 'Reference wrist excursion (cm)']:
        raise SystemExit(f'ERROR: Table 7.5 header is {t75[0]}')
    got75 = {r[1]: r[3] for r in t75[1:]}
    if got75 != TABLE75:
        raise SystemExit(f'ERROR: Table 7.5 excursions {got75} differ from {TABLE75}')
    t77 = tables['7.7']['rows']
    got77 = {r[1]: r[3] for r in t77[1:] if r[0] == 'Intermediate motion'}
    if t77[0][3] != 'Median (cm)' or got77 != TABLE77_WRIST:
        raise SystemExit(f'ERROR: Table 7.7 intermediate wrist medians {got77} differ from {TABLE77_WRIST}')
    return {'table_7_5': {'caption': tables['7.5']['caption'], 'rows': t75},
            'table_7_7_intermediate_wrist_median_cm': got77,
            'table_7_7_caption': tables['7.7']['caption']}


def load():
    """Window data, medians, projection check and the decoded frame (shared by both modes)."""
    sel = json.loads(SELECTION.read_text())['selected']
    win = [w for w in sel if w['window'] == WINDOW]
    if len(win) != 1 or (win[0]['start'], win[0]['stop']) != (START, STOP):
        raise SystemExit(f'ERROR: selection for {WINDOW} is {win}')
    d = pd.read_csv(PAIRS)
    d = d[d.window == WINDOW]
    if sorted(d.frame.unique()) != list(range(START, STOP + 1)) or len(d) != 3 * 2 * 45:
        raise SystemExit('ERROR: synthetic_pairs.csv intermediate window is not 45 frames x 3 x 2')

    med = {j: {m: float(np.median(d[(d.method == m) & (d.joint == j)].error_cm)) for m in METHODS}
           for j in ('wrist', 'elbow')}
    slide = slide34_values()
    for j in ('wrist', 'elbow'):
        mine = [round(med[j][m], 1) for m in METHODS]
        if mine != slide[j]:
            raise SystemExit(f'ERROR: {j} medians {mine} differ from slide 34 {slide[j]}')

    K = json.loads(META.read_text())['color_intrinsics']
    lm = pd.read_csv(FILTERED).set_index('frame')
    sh_sensor = lm.loc[FRAME, ['right_shoulder_x', 'right_shoulder_y', 'right_shoulder_z']].to_numpy(float)
    shoulder = sh_sensor * [1.0, -1.0, 1.0]              # as synthetic() line 217
    f = d[d.frame == FRAME]

    def pt(method, joint, kind):
        r = f[(f.method == method) & (f.joint == joint)].iloc[0]
        return np.array([r[f'{kind}_x'], r[f'{kind}_y'], r[f'{kind}_z']], float)

    ref = {j: pt(METHODS[0], j, 'reference') for j in ('elbow', 'wrist')}
    for m in METHODS[1:]:
        for j in ('elbow', 'wrist'):
            if not np.allclose(pt(m, j, 'reference'), ref[j]):
                raise SystemExit('ERROR: reference differs between methods')
    # projection check: reference elbow / wrist against the measured landmarks of FRAME
    check = {}
    for j in ('elbow', 'wrist'):
        meas = lm.loc[FRAME, [f'right_{j}_x', f'right_{j}_y', f'right_{j}_z']].to_numpy(float)
        a = np.array(project(ref[j], K))
        b = np.array(project(meas * [1.0, -1.0, 1.0], K))
        check[j] = {'reference_px': [round(v, 1) for v in a], 'measured_px': [round(v, 1) for v in b],
                    'distance_px': round(float(np.linalg.norm(a - b)), 2)}
        if check[j]['distance_px'] > MAX_PX:
            raise SystemExit(f'ERROR: projection check failed for {j}: {check[j]}')

    import cv2
    frames = decode_bag({CHECK_FRAME, FRAME})
    if not np.array_equal(frames[CHECK_FRAME], cv2.imread(str(FRAME_PNG))):
        raise SystemExit('ERROR: bag frame 450 differs from r7_frame00450.png; frame index not pinned')
    P = {'shoulder': project(shoulder, K), 'elbow': project(ref['elbow'], K), 'wrist': project(ref['wrist'], K)}
    rec = {m: {j: project(pt(m, j, 'reconstructed'), K) for j in ('elbow', 'wrist')} for m in METHODS}
    err = {m: {j: float(f[(f.method == m) & (f.joint == j)].error_cm.iloc[0]) for j in ('elbow', 'wrist')}
           for m in METHODS}
    return dict(d=d, med=med, slide=slide, K=K, check=check, frames=frames, P=P, rec=rec, err=err)


def draw_photo(ax, img, crop):
    x0, y0, x1, y1 = crop
    ax.imshow(img[int(y0):int(np.ceil(y1)), x0:x1], extent=(x0, x0 + img[:, x0:x1].shape[1],
              int(np.ceil(y1)), y0), interpolation='lanczos')
    ax.set_xlim(x0, x1)
    ax.set_ylim(y1, y0)
    ax.axis('off')


def render_two_panel(L):
    d, med, P, rec = L['d'], L['med'], L['P'], L['rec']
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': FG, 'axes.labelcolor': FG,
                         'xtick.color': FG, 'ytick.color': FG, 'axes.edgecolor': '#808080'})
    fig = plt.figure(figsize=FIG_IN, dpi=DPI, facecolor=BG)
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.55], left=0.005, right=0.965, top=0.985,
                          bottom=0.13, wspace=0.17)

    # left panel: photo with chains
    ax = fig.add_subplot(gs[0])
    img = L['frames'][FRAME][:, :, ::-1]
    x0, y0, x1, y1 = CROP
    ax.imshow(img[y0:y1, x0:x1], extent=(x0, x1, y1, y0), interpolation='lanczos')
    ax.set_xlim(x0, x1)
    ax.set_ylim(y1, y0)
    ax.axis('off')
    for m in METHODS:
        e, w = rec[m]['elbow'], rec[m]['wrist']
        ax.plot([P['shoulder'][0], e[0], w[0]], [P['shoulder'][1], e[1], w[1]], '-', color=COLOUR[m],
                lw=2.2, solid_capstyle='round', zorder=3)
        ax.plot([e[0], w[0]], [e[1], w[1]], 'o', color=COLOUR[m], ms=3.6, zorder=3)
    xs = [P[k][0] for k in ('shoulder', 'elbow', 'wrist')]
    ys = [P[k][1] for k in ('shoulder', 'elbow', 'wrist')]
    ax.plot(xs, ys, '-', color='black', lw=1.9, zorder=4, alpha=0.6)
    ax.plot(xs, ys, '-', color=REF, lw=0.9, zorder=5)
    ax.plot(xs[1:], ys[1:], 'o', color=REF, ms=2.4, zorder=5)
    ax.plot(xs[:1], ys[:1], 'o', color=REF, ms=3.2, zorder=5)
    for k in ('elbow', 'wrist'):
        ax.plot(*P[k], 'o', ms=17, mfc='none', mec=RED, mew=1.6, zorder=6)
    ax.text(0.5, 0.015, 'removed for\n45 frames', transform=ax.transAxes, ha='center', va='bottom',
            color=RED, fontsize=FS_NOTE, fontweight='bold', linespacing=1.0,
            bbox=dict(boxstyle='square,pad=0.25', fc='black', ec='none', alpha=0.75))
    ax.text(0.5, 0.985, f'frame {FRAME}', transform=ax.transAxes, ha='center', va='top', color=FG,
            fontsize=FS_NOTE, bbox=dict(boxstyle='square,pad=0.2', fc='black', ec='none', alpha=0.75))

    # right panel: error against frame
    bx = fig.add_subplot(gs[1], facecolor=BG)
    for m in METHODS:
        for j, lw, ls in (('wrist', 1.8, '-'), ('elbow', 0.9, (0, (3, 1.5)))):
            s = d[(d.method == m) & (d.joint == j)].sort_values('frame')
            bx.plot(s.frame, s.error_cm, color=COLOUR[m], lw=lw, ls=ls)
    bx.axvline(FRAME, color='#808080', lw=0.6, ls=':')
    bx.set_xlim(START, STOP)
    bx.set_ylim(bottom=0)
    bx.set_xticks([445, 460, 475, 489])
    bx.set_xlabel('Masked frame', fontsize=FS_AXIS)
    bx.set_ylabel('Error to reference (cm)', fontsize=FS_AXIS, labelpad=2)
    bx.tick_params(labelsize=FS_TICK, length=2.5, pad=2)
    for side in ('top', 'right'):
        bx.spines[side].set_visible(False)
    handles = [Line2D([], [], color=COLOUR[m], lw=1.8,
                      label=f'{LABEL[m]}  {med["wrist"][m]:.1f} / {med["elbow"][m]:.1f}') for m in METHODS]
    handles += [Line2D([], [], color=FG, lw=1.8, label='wrist (thick)'),
                Line2D([], [], color=FG, lw=0.9, ls=(0, (3, 1.5)), label='elbow (thin)')]
    leg = bx.legend(handles=handles, loc='upper left', fontsize=FS_LEG, frameon=False, handlelength=1.6,
                    borderaxespad=0.2, labelspacing=0.3, title='median wrist / elbow (cm)',
                    title_fontsize=FS_LEG)
    leg.get_title().set_color(FG)
    ymax = max(d.error_cm.max(), 0.1)
    bx.set_ylim(0, ymax * 1.75)          # head room for the legend above the lines

    fig.savefig(OUT_PNG, dpi=DPI, facecolor=BG)
    plt.close(fig)
    return {
        'purpose': 'Slide 34: how the controlled-removal comparison was made, window 445-489 '
                   '(author request 2026-10-06, D-390).',
        'font_pt': {'axis_label': FS_AXIS, 'tick': FS_TICK, 'legend': FS_LEG, 'note': FS_NOTE},
        'font_px_at_dpi': {k: round(v * DPI / 72, 1) for k, v in
                           {'axis_label': FS_AXIS, 'tick': FS_TICK, 'legend': FS_LEG, 'note': FS_NOTE}.items()},
        'crop_px': list(CROP),
    }


def render_three_case(L):
    med, P, rec = L['med'], L['P'], L['rec']
    W, H = round(FIG_IN[0] * DPI), round(FIG_IN[1] * DPI)
    pw = (W - 2 * GAP3_PX) / 3.0                    # panel width in output px
    cx0, cx1 = CROP3_X
    scale = pw / (cx1 - cx0)                        # output px per original px
    # the photo fills the rest of the height under the title band, minus the label band
    label_px = TITLE3_PX
    ph = H - TITLE3_PX - label_px                   # photo height in output px
    cy0 = CROP3_Y0
    cy1 = cy0 + ph / scale
    if cy1 > 480:
        raise SystemExit(f'ERROR: three-case crop runs below the frame (y1 {cy1:.1f})')
    crop = (cx0, cy0, cx1, cy1)
    pts = [P['shoulder'], P['elbow'], P['wrist']] + [rec[m][j] for m in METHODS for j in ('elbow', 'wrist')]
    for u, v in pts:
        if not (cx0 + 5 <= u <= cx1 - 5 and cy0 + 5 <= v <= cy1 - 5):
            raise SystemExit(f'ERROR: chain point ({u:.1f}, {v:.1f}) outside the crop {crop}')

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': FG})
    fig = plt.figure(figsize=FIG_IN, dpi=DPI, facecolor=BG)
    img = L['frames'][FRAME][:, :, ::-1]
    texts = []
    xs = [P[k][0] for k in ('shoulder', 'elbow', 'wrist')]
    ys = [P[k][1] for k in ('shoulder', 'elbow', 'wrist')]
    panels = {}
    for i, m in enumerate(METHODS):
        left = i * (pw + GAP3_PX)
        rect = (left / W, label_px / H, pw / W, ph / H)           # figure fractions, origin bottom-left
        ax = fig.add_axes(rect)
        draw_photo(ax, img, crop)
        e, w = rec[m]['elbow'], rec[m]['wrist']
        # reference chain (white, with a dark halo) under the case chain
        ax.plot(xs, ys, '-', color='black', lw=LW3_HALO, alpha=0.6, zorder=3, solid_capstyle='round')
        ax.plot(xs, ys, '-', color=REF, lw=LW3_REF, zorder=4, solid_capstyle='round')
        ax.plot(xs, ys, 'o', color=REF, ms=MS3_JOINT * 0.8, zorder=4)
        # removed joints: red rings at the reference elbow and wrist
        for k in ('elbow', 'wrist'):
            ax.plot(*P[k], 'o', ms=MS3_RING, mfc='none', mec=RED, mew=MEW3_RING, zorder=5)
        # this case's recovered chain shoulder -> recovered elbow -> recovered wrist
        ax.plot([P['shoulder'][0], e[0], w[0]], [P['shoulder'][1], e[1], w[1]], '-', color=COLOUR[m],
                lw=LW3_CASE, solid_capstyle='round', zorder=6, alpha=0.95)
        ax.plot([e[0], w[0]], [e[1], w[1]], 'o', color=COLOUR[m], ms=MS3_JOINT, zorder=6)
        cx = (left + pw / 2) / W
        t = fig.text(cx, 1 - (TITLE3_PX / 2) / H, TITLE[m], ha='center', va='center', color=FG,
                     fontsize=FS3_TITLE)
        lab = f'wrist {med["wrist"][m]:.1f} cm'
        s = fig.text(cx, (label_px / 2) / H, lab, ha='center', va='center', color=COLOUR[m],
                     fontsize=FS3_LABEL, fontweight='bold')
        texts += [(t, left, pw), (s, left, pw)]
        panels[m] = {'title': TITLE[m], 'label': lab, 'colour': COLOUR[m],
                     'panel_px': [round(left, 1), 0, round(left + pw, 1), H],
                     'photo_px': [round(left, 1), TITLE3_PX, round(left + pw, 1), TITLE3_PX + ph],
                     'recovered_px': {j: [round(v, 1) for v in rec[m][j]] for j in ('elbow', 'wrist')},
                     'frame_error_cm': {j: round(L['err'][m][j], 4) for j in ('elbow', 'wrist')}}

    # text checks: font size in px and each text inside its panel
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    measured = []
    for t, left, width in texts:
        px = t.get_fontsize() * DPI / 72
        bb = t.get_window_extent(rend)
        measured.append({'text': t.get_text(), 'font_px': round(px, 1), 'bbox_w_px': round(bb.width, 1),
                         'bbox_h_px': round(bb.height, 1)})
        if px < MIN_TEXT_PX:
            raise SystemExit(f'ERROR: text "{t.get_text()}" is {px:.1f} px, under {MIN_TEXT_PX}')
        if bb.x0 < left or bb.x1 > left + width:
            raise SystemExit(f'ERROR: text "{t.get_text()}" runs outside its panel ({bb.x0:.0f}..{bb.x1:.0f})')
    fig.savefig(OUT_PNG, dpi=DPI, facecolor=BG)
    plt.close(fig)
    # ink check on the written PNG: each title and label band of each panel
    png = (plt.imread(str(OUT_PNG))[:, :, :3] * 255).round()
    for i, m in enumerate(METHODS):
        c0, c1 = int(round(i * (pw + GAP3_PX))), int(round(i * (pw + GAP3_PX) + pw))
        for kind, (r0, r1) in (('title', (0, TITLE3_PX)), ('label', (H - label_px, H))):
            rows = np.where((png[r0:r1, c0:c1].max(axis=2) > INK_LEVEL).any(axis=1))[0]
            ink = int(rows.max() - rows.min() + 1) if rows.size else 0
            panels[m][f'{kind}_ink_h_px'] = ink
            if ink < MIN_TEXT_PX:
                raise SystemExit(f'ERROR: {kind} of {m} has {ink} px of ink, under {MIN_TEXT_PX}')
    return {
        'purpose': 'Slide 34: the three recovery cases side by side at frame 489 of window 445-489, '
                   'each with its window wrist median (plan declarative-stargazing-phoenix.md '
                   'Milestone B, D-392; replaces the D-390 two-panel figure).',
        'font_pt': {'title': FS3_TITLE, 'label': FS3_LABEL},
        'font_px_at_dpi': {'title': round(FS3_TITLE * DPI / 72, 1), 'label': round(FS3_LABEL * DPI / 72, 1)},
        'min_text_px': MIN_TEXT_PX,
        'text_measured': measured,
        'layout_px': {'gap': GAP3_PX, 'title_band': TITLE3_PX, 'label_band': label_px,
                      'panel_w': round(pw, 2), 'photo_h': ph, 'scale_out_per_src_px': round(scale, 4)},
        'crop_px': [cx0, cy0, cx1, round(cy1, 2)],
        'line_pt': {'case': LW3_CASE, 'reference': LW3_REF, 'reference_halo': LW3_HALO},
        'marker_pt': {'ring': MS3_RING, 'ring_edge': MEW3_RING, 'joint': MS3_JOINT},
        'reference_px': {k: [round(v, 1) for v in P[k]] for k in ('shoulder', 'elbow', 'wrist')},
        'panels': panels,
        'labels': {m: panels[m]['label'] for m in METHODS},
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--mode', choices=('three-case', 'two-panel'), default='three-case')
    args = ap.parse_args()

    thesis = None
    if args.mode == 'three-case':
        thesis = thesis_tables()
    L = load()
    if args.mode == 'three-case':
        expect = [float(TABLE77_WRIST[LABEL[m]]) for m in METHODS]
        mine = [round(L['med']['wrist'][m], 1) for m in METHODS]
        if mine != expect:
            raise SystemExit(f'ERROR: wrist medians {mine} differ from Table 7.7 {expect}')
        extra = render_three_case(L)
    else:
        extra = render_two_panel(L)

    w, h = plt.imread(str(OUT_PNG)).shape[1::-1]
    if (w, h) != (round(FIG_IN[0] * DPI), round(FIG_IN[1] * DPI)):
        raise SystemExit(f'ERROR: output is {w} x {h}')
    # the bag is not hashed here (large); the decoded frame is pinned by still_source below.
    # PPTX is the deck the slide 34 values were read from (read only).
    inputs = [PAIRS, SELECTION, FRAME_PNG, FILTERED, META] + ([CH7] if thesis else []) + [PPTX]
    record = {
        'status': 'PASS',
        'slide': 34,
        'kind': 'masked_comparison_figure',
        'mode': args.mode,
        'purpose': extra.pop('purpose'),
        'asset': str(OUT_PNG.relative_to(ROOT)),
        'dimensions': [w, h], 'dpi': DPI, 'figure_in': list(FIG_IN),
        'font_family': 'DejaVu Sans',
        'background': BG,
        **{k: extra.pop(k) for k in ('font_pt', 'font_px_at_dpi')},
        'sha256': {'png': sha(OUT_PNG)},
        'bytes': {'png': OUT_PNG.stat().st_size},
        'window': {'name': WINDOW, 'frames': [START, STOP], 'source': str(SELECTION.relative_to(ROOT))},
        'medians_cm': {j: {m: round(L['med'][j][m], 4) for m in METHODS} for j in L['med']},
        'slide34_values_cm': L['slide'],
        'medians_match_slide34': True,
    }
    if thesis:
        record['thesis_check'] = {'source': str(CH7.relative_to(ROOT)), **thesis,
                                  'wrist_medians_match_table_7_7': True}
    record.update({
        'still_frame': FRAME,
        'still_source': {'bag': str(BAG.relative_to(ROOT)), 'decode': 'pyrealsense2 sequential, bgr8',
                         'frame_rgb_sha256': hashlib.sha256(
                             np.ascontiguousarray(L['frames'][FRAME]).tobytes()).hexdigest(),
                         'index_check': f'decoded frame {CHECK_FRAME} equals {FRAME_PNG.relative_to(ROOT)} byte for byte',
                         'plan_deviation': 'plan A3 named frame 450; at 450 the recovered chains lie under the reference'},
        **extra,
        'projection': {'model': 'pinhole, no distortion, y flipped back to the sensor frame',
                       'copied_from': 'eval/failure/make_label_compare_fig.py project()',
                       'intrinsics_source': str(META.relative_to(ROOT)) + ' color_intrinsics',
                       'intrinsics': {k: L['K'][k] for k in ('fx', 'fy', 'ppx', 'ppy', 'width', 'height')},
                       f'check_against_measured_landmarks_frame{FRAME}': L['check'], 'tolerance_px': MAX_PX},
        'shoulder_source': 'filtered right_shoulder landmark, y flipped (evaluate_ch7_restructured.py line 217)',
        'colours': {'reference': REF, 'removed': RED, **{m: COLOUR[m] for m in METHODS}},
        'inputs': {str(p.relative_to(ROOT)): sha(p) for p in inputs},
        'generator': str(Path(__file__).resolve().relative_to(ROOT)),
        'generator_sha256': sha(Path(__file__).resolve()),
    })
    OUT_JSON.write_text(json.dumps(record, indent=2, ensure_ascii=True) + '\n', encoding='ascii')
    print(json.dumps({'mode': args.mode, 'medians': record['medians_cm'], 'slide': L['slide'],
                      'check': L['check'], 'size': [w, h], 'png': record['sha256']['png']}))


if __name__ == '__main__':
    main()
