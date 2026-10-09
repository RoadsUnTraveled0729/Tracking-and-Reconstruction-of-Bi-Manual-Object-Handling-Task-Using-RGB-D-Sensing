#!/usr/bin/env python3
"""Typeset the landmark-filter equations as white-on-transparent PNGs.

The final thesis (V9) prints no filter formula, only prose (Chapter 2 and
Appendix F), so these pieces cannot be cropped from the thesis PDF the way
equation_assets.py crops Eq2.1-EqD.2. They are typeset here with matplotlib
mathtext (no TeX install) directly from the frozen implementation
v1/mediapipe/filter_landmarks.py, whose SHA-256 is pinned below. Every key
cites the function and line range it restates, and the script refuses to run
if the pinned file changed or a cited line no longer holds the quoted code.

Output (repository-relative):
  presentation/defense_2026/equations/typeset/<key>.png   white glyphs, alpha
  presentation/defense_2026/equations/typeset_catalog.json
  presentation/defense_2026/equations/typeset/contact_sheet.png   review only

Sizing contract (build_deck.py, restrained_equations and
source_equation_fragment): each piece is placed at x 0.59 in with width
px / 600 * 1.6 in, stacked downward from equation_start_y. The math font size
is calibrated so a digit '1' has the same pixel height as the digit '1' in the
thesis crop eq_5_4.png (600 dpi), so typeset and cropped equations share one
glyph scale on the slide.

Usage (repository root):
  /home/luo/anaconda3/bin/python presentation/defense_2026/equations/typeset_filters.py
  /home/luo/anaconda3/bin/python presentation/defense_2026/equations/typeset_filters.py --check
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent            # .../defense_2026/equations
DECK = HERE.parent
ROOT = HERE.parents[2]
OUT = HERE / "typeset"
CATALOG = HERE / "typeset_catalog.json"

FILTER_SOURCE = "v1/mediapipe/filter_landmarks.py"
FILTER_SHA256 = "7bdde9b75c352dffe2375244a2ac34f9820dd9622ccbaa661f52680dc92fb5ec"
LIVE_SOURCE = "v1/realtime/person/realtime_person.py"
LIVE_SHA256 = "0fae95a4bbef3390f24b5bd5c6e4698dc7af2094c1116201f62d28d8662a18e6"
RUN_INFO = "presentation/defense_2026/experiments/filter_metrics/run_info.json"

# Calibration reference: thesis crop eq_5_4 (equation_catalog.json pins its
# SHA-256). Columns 670-730 of that 600 dpi crop hold only the printed digit 1.
CALIBRATION_KEY = "eq_5_4"
CALIBRATION_COLUMNS = (670, 730)
PROBE_PT = 12.0

# Builder constants (build_deck.py RESTRAINED and restrained_equations):
RENDER_DPI = 600                 # equation_catalog.json render_dpi
DISPLAY_SCALE = 1.6              # RESTRAINED['equation_pdf_scale']
FRAGMENT_X_IN = 0.59             # restrained_equations x
LEFT_REGION_RIGHT_IN = 5.85      # RESTRAINED left_x 0.50 + left_w 5.35; validate_deck left region
MAX_WIDTH_PX = int((LEFT_REGION_RIGHT_IN - FRAGMENT_X_IN) / DISPLAY_SCALE * RENDER_DPI)
# Line gap inside one multi-line piece equals the builder's default gap
# between pieces (equation_gap 0.18 in) converted to source pixels.
LINE_GAP_PX = round(0.18 / DISPLAY_SCALE * RENDER_DPI)
MARGIN_PX = 2                    # same 2 px clear margin as exact_equation_fragments
FONTSET = "stix"

F = FILTER_SOURCE
SPECS = {
    "ts_hampel": {
        "title": "Hampel spike test",
        "lines": [
            r"$|x_i - m_i| > \max(a_0,\, k \cdot 1.4826\,\mathrm{MAD}_i)$:  reject $x_i$",
            r"$m_i = \mathrm{med}_{|j| \leq 3}\, x_{i+j},\;\; \mathrm{MAD}_i = \mathrm{med}_{|j| \leq 3}\, |x_{i+j} - m_{i+j}|$",
            r"$a_0 = 0.02$ m,  $k = 3$,  each axis",
        ],
        "derived_from": {"file": F, "function": "hampel_mask", "lines": [54, 62]},
        "anchors": [(57, "df.rolling(window, center=True, min_periods=3)"),
                    (58, "med = roll.median()"),
                    (60, "mad = (df - med).abs().rolling(window, center=True, min_periods=3).median()"),
                    (61, "thresh = np.maximum(abs_floor, k * 1.4826 * mad)"),
                    (62, "(resid > thresh).any(axis=1)"),
                    (263, "work[spikes] = np.nan")],
        "parameters": [
            {"name": "window", "value": 7, "unit": "frames", "symbol": "|j| <= 3",
             "source": F + ":202 (--hampel-window default 7), centred rolling window line 57"},
            {"name": "k", "value": 3.0, "unit": "", "symbol": "k",
             "source": F + ":203 (--hampel-k default 3.0)"},
            {"name": "abs_floor", "value": 0.02, "unit": "m", "symbol": "a_0",
             "source": F + ":204-205 (--hampel-floor default 0.02)"},
            {"name": "MAD scale", "value": 1.4826, "unit": "", "symbol": "1.4826",
             "source": F + ":61"},
        ],
        "notes": [
            "MAD_i is the rolling median of each sample's own residual |x_{i+j} - m_{i+j}| (line 60), not of |x_{i+j} - m_i|.",
            "A frame is flagged when the test holds on any of the three axes and the sample is finite (line 62); flagged samples become NaN (line 263), they are not replaced by the median.",
            "Near segment ends the rolling medians use as few as 3 samples (min_periods=3, lines 57 and 60).",
        ],
    },
    "ts_gap": {
        "title": "Short-gap linear interpolation",
        "lines": [
            r"$x(t) = x(t_a) + \dfrac{t - t_a}{t_b - t_a}\,\left(x(t_b) - x(t_a)\right)$",
            r"$t_a < t < t_b$,  interior gap $\leq 5$ frames",
        ],
        "derived_from": {"file": F, "function": "fill_gaps", "lines": [71, 97]},
        "anchors": [(89, "interior = start > valid_idx[0] and stop <= valid_idx[-1]"),
                    (90, "if interior and run <= max_gap:"),
                    (92, "np.interp(t[start:stop], t[~missing], pos[~missing, ax])")],
        "parameters": [
            {"name": "max_gap", "value": 5, "unit": "frames", "symbol": "5",
             "source": F + ":206-207 (--max-gap default 5)"},
            {"name": "edge_fill", "value": 0, "unit": "frames", "symbol": "",
             "source": F + ":208-210 (--edge-fill default 0 = off); boundary runs are not filled"},
        ],
        "notes": [
            "t_a and t_b are the timestamps of the nearest valid samples before and after the gap; np.interp interpolates in time (t = time_s), per axis (line 92).",
            "Longer runs and runs touching either end stay NaN with the default edge_fill 0.",
        ],
    },
    "ts_butter": {
        "title": "Butterworth low-pass magnitude",
        "lines": [
            r"$|H(\omega)|^2 = \dfrac{1}{1 + (\omega/\omega_c)^{2n}}$",
            r"$n = 4,\quad f_c = \omega_c / 2\pi = 3$ Hz",
        ],
        "derived_from": {"file": F, "function": "smooth_segment", "lines": [140, 145]},
        "anchors": [(141, "b, a = butter(args.butter_order, args.cutoff_hz, fs=fs)")],
        "parameters": [
            {"name": "butter_order", "value": 4, "unit": "", "symbol": "n",
             "source": F + ":215 (--butter-order default 4)"},
            {"name": "cutoff_hz", "value": 3.0, "unit": "Hz", "symbol": "f_c",
             "source": F + ":213-214 (--cutoff-hz default 3.0)"},
        ],
        "notes": [
            "This is the analog Butterworth prototype magnitude. scipy.signal.butter(4, 3.0, fs=fs) designs the digital filter by the bilinear transform with the cutoff pre-warped, so the digital response equals 1/2 in power at exactly f_c = 3 Hz; away from f_c it differs slightly from the analog curve.",
            "fs is measured per recording from the timestamps (line 246); 29.98 Hz on R6b (" + RUN_INFO + " sampling_rate_hz).",
        ],
    },
    "ts_filtfilt": {
        "title": "Forward-backward (zero-phase) filtering",
        "lines": [
            r"$y = \mathrm{rev}\,\left(H\,\mathrm{rev}\,(H\,x)\right)$",
            r"zero phase,  magnitude $|H(\omega)|^2$",
        ],
        "derived_from": {"file": F, "function": "smooth_segment", "lines": [140, 145]},
        "anchors": [(142, "padlen = 3 * max(len(a), len(b))"),
                    (145, "out[:, ax] = filtfilt(b, a, seg[:, ax])")],
        "parameters": [
            {"name": "butter_order", "value": 4, "unit": "", "symbol": "H",
             "source": F + ":215"},
            {"name": "cutoff_hz", "value": 3.0, "unit": "Hz", "symbol": "H",
             "source": F + ":213-214"},
        ],
        "notes": [
            "rev is time reversal. scipy.signal.filtfilt filters forward, reverses, filters again and reverses back, so the phase shifts cancel and the effective magnitude is |H|^2 (amplitude 1/2, -6 dB, at f_c).",
            "filtfilt pads each segment by odd extension (default padlen 3*max(len(a), len(b)) = 15 samples); segments not longer than padlen are left unsmoothed (lines 142-143).",
            "It needs the whole segment, including future samples, so it is an offline operation.",
        ],
    },
    "ts_savgol": {
        "title": "Savitzky-Golay smoothing",
        "lines": [
            r"$y_i = \sum_{j=-4}^{4} c_j\, x_{i+j}$",
            r"$c_j$:  least-squares quadratic fit",
        ],
        "derived_from": {"file": F, "function": "smooth_segment", "lines": [131, 134]},
        "anchors": [(134, "savgol_filter(seg[:, ax], args.smooth_window, args.smooth_polyorder)")],
        "parameters": [
            {"name": "smooth_window", "value": 9, "unit": "samples", "symbol": "j = -4..4",
             "source": F + ":216-217 (--smooth-window default 9)"},
            {"name": "smooth_polyorder", "value": 2, "unit": "", "symbol": "quadratic",
             "source": F + ":218 (--smooth-polyorder default 2)"},
        ],
        "notes": [
            "The fixed weights c_j evaluate, at the window centre, the least-squares quadratic through the 9 samples. scipy's default mode 'interp' fits the polynomial to the first and last 9 samples for the 4 edge samples at each segment end.",
        ],
    },
    "ts_median": {
        "title": "Rolling median",
        "lines": [
            r"$y_i = \mathrm{med}\,(x_{i-4},\, \ldots,\, x_{i+4})$",
        ],
        "derived_from": {"file": F, "function": "smooth_segment", "lines": [135, 139]},
        "anchors": [(136, "w = args.smooth_window if args.smooth_window % 2 else args.smooth_window + 1"),
                    (139, "out[:, ax] = medfilt(seg[:, ax], w)")],
        "parameters": [
            {"name": "smooth_window", "value": 9, "unit": "samples", "symbol": "i-4..i+4",
             "source": F + ":216-217 (--smooth-window default 9, odd so used as is, line 136)"},
        ],
        "notes": [
            "scipy.signal.medfilt pads each segment with zeros, so the first and last 4 outputs of a segment include zero-valued padding samples; the formula holds for interior samples.",
        ],
    },
    "ts_oneeuro_cutoff": {
        "title": "One Euro adaptive cutoff",
        "lines": [
            r"$d_i = f_s\,(x_i - \hat{x}_{i-1}),\quad \hat{d}_i = a_d\, d_i + (1 - a_d)\,\hat{d}_{i-1}$",
            r"$f_c = f_{\min} + \beta\, |\hat{d}_i|$",
        ],
        "derived_from": {"file": F, "function": "OneEuro.__call__", "lines": [113, 123]},
        "anchors": [(117, "dx = (x - self._x) * self.freq"),
                    (118, "a_d = self._alpha(self.d_cutoff, self.freq)"),
                    (119, "self._dx = a_d * dx + (1 - a_d) * self._dx"),
                    (120, "cutoff = self.min_cutoff + self.beta * abs(self._dx)")],
        "parameters": [
            {"name": "d_cutoff", "value": 1.0, "unit": "Hz", "symbol": "a_d = a(1 Hz)",
             "source": F + ":104 (OneEuro d_cutoff default 1.0)"},
            {"name": "min_cutoff", "value": "0.05 offline / 1.0 live", "unit": "Hz", "symbol": "f_min",
             "source": F + ":219-220 (offline default 0.05); " + LIVE_SOURCE + ":98-99 (CausalLandmarkFilter min_cutoff 1.0)"},
            {"name": "beta", "value": 1.0, "unit": "s/m", "symbol": "beta",
             "source": F + ":221-222 (offline default 1.0); " + LIVE_SOURCE + ":98-99 (beta 1.0)"},
        ],
        "notes": [
            "The speed d_i is taken against the previous filtered value x_hat_{i-1}, not the previous raw sample (line 117: self._x holds the filtered output).",
            "The first sample initialises x_hat = x and d_hat = 0 and is passed through unchanged (lines 114-116).",
            "Units: positions are in metres, so |d_hat| is in m/s and beta = 1 converts it to Hz (unit s/m is implied by the code, not stated in it).",
        ],
    },
    "ts_oneeuro_alpha": {
        "title": "One Euro smoothing factor and update",
        "lines": [
            r"$a = \dfrac{1}{1 + f_s / (2\pi f_c)},\quad \hat{x}_i = a\, x_i + (1 - a)\,\hat{x}_{i-1}$",
        ],
        "derived_from": {"file": F, "function": "OneEuro._alpha, OneEuro.__call__", "lines": [109, 122]},
        "anchors": [(110, "tau = 1.0 / (2 * np.pi * cutoff)"),
                    (111, "return 1.0 / (1.0 + tau * freq)"),
                    (121, "a = self._alpha(cutoff, self.freq)"),
                    (122, "self._x = a * x + (1 - a) * self._x")],
        "parameters": [
            {"name": "freq", "value": "measured per recording offline (29.98 Hz on R6b); 30 live", "unit": "Hz",
             "symbol": "f_s",
             "source": F + ":246 (fs from median timestamp step), " + RUN_INFO + " sampling_rate_hz 29.978715; " + LIVE_SOURCE + ":98 (freq=30.0)"},
        ],
        "notes": [
            "a = 1/(1 + tau f_s) with tau = 1/(2 pi f_c) (lines 110-111), rewritten with f_s/(2 pi f_c).",
        ],
    },
    "ts_oneeuro_params": {
        "title": "One Euro settings",
        "lines": [
            r"$f_{\min} = 0.05$ Hz offline,  $1$ Hz live;   $\beta = 1$",
            r"$f_s \approx 30$ Hz;   $a_d$ uses a $1$ Hz cutoff",
        ],
        "derived_from": {"file": F, "function": "OneEuro.__init__, main (argparse)", "lines": [104, 222]},
        "anchors": [(104, "def __init__(self, freq, min_cutoff, beta, d_cutoff=1.0):"),
                    (219, 'ap.add_argument("--oneeuro-mincutoff", type=float, default=0.05,'),
                    (221, 'ap.add_argument("--oneeuro-beta", type=float, default=1.0,'),
                    (246, "fs = 1.0 / float(np.median(np.diff(t))) if len(t) > 1 else 30.0")],
        "live_anchors": [(98, "def __init__(self, freq=30.0, window=11, k=3.0, abs_floor=0.035,"),
                         (99, "min_cutoff=1.0, beta=1.0):")],
        "parameters": [
            {"name": "min_cutoff offline", "value": 0.05, "unit": "Hz", "symbol": "f_min",
             "source": F + ":219-220"},
            {"name": "min_cutoff live", "value": 1.0, "unit": "Hz", "symbol": "f_min",
             "source": LIVE_SOURCE + ":99; eval/pipeline_smoothness/DECISIONS.md PS-006"},
            {"name": "beta", "value": 1.0, "unit": "s/m", "symbol": "beta",
             "source": F + ":221-222; " + LIVE_SOURCE + ":99"},
            {"name": "sampling rate", "value": "29.98 offline (R6b), 30 live", "unit": "Hz", "symbol": "f_s",
             "source": F + ":246; " + RUN_INFO + " sampling_rate_hz; " + LIVE_SOURCE + ":98"},
            {"name": "d_cutoff", "value": 1.0, "unit": "Hz", "symbol": "a_d",
             "source": F + ":104"},
        ],
        "notes": [
            "The offline setting (0.05 Hz) drives the One Euro demonstration film; the live setting (1 Hz) is the CausalLandmarkFilter default used by the real-time pipeline.",
        ],
    },
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def verify_sources() -> None:
    """Refuse to typeset from a changed implementation or a stale line cite."""
    problems = []
    for rel, pinned in ((FILTER_SOURCE, FILTER_SHA256), (LIVE_SOURCE, LIVE_SHA256)):
        actual = sha256_file(ROOT / rel)
        if actual != pinned:
            problems.append(f"{rel}: sha256 {actual} != pinned {pinned}")
    filt = (ROOT / FILTER_SOURCE).read_text().splitlines()
    live = (ROOT / LIVE_SOURCE).read_text().splitlines()
    for key, spec in SPECS.items():
        for lines, anchors in ((filt, spec["anchors"]), (live, spec.get("live_anchors", []))):
            for number, needle in anchors:
                if needle not in lines[number - 1]:
                    problems.append(f"{key}: line {number} lacks {needle!r}")
    if problems:
        sys.exit("[ERROR] Source check failed:\n  " + "\n  ".join(problems))


def calibration_font_pt() -> tuple[float, dict]:
    """Font size whose digit '1' height equals the thesis crop's digit '1'."""
    catalog = json.loads((DECK / "equation_catalog.json").read_text())
    item = catalog["equations"][CALIBRATION_KEY]
    crop = ROOT / item["path"]
    if sha256_file(crop) != item["sha256"]:
        sys.exit(f"[ERROR] {item['path']} does not match equation_catalog.json")
    alpha = np.asarray(Image.open(crop).convert("RGBA"))[:, :, 3]
    rows = np.flatnonzero(alpha[:, CALIBRATION_COLUMNS[0]:CALIBRATION_COLUMNS[1]].max(axis=1) > 128)
    thesis_px = int(rows.max() - rows.min() + 1)
    probe = render_line(r"$1$", PROBE_PT)
    probe_rows = np.flatnonzero(np.asarray(probe)[:, :, 3].max(axis=1) > 128)
    probe_px = int(probe_rows.max() - probe_rows.min() + 1)
    font_pt = round(PROBE_PT * thesis_px / probe_px, 2)
    return font_pt, {"reference": item["path"], "reference_sha256": item["sha256"],
                     "reference_columns_px": list(CALIBRATION_COLUMNS),
                     "reference_digit_1_height_px": thesis_px,
                     "probe_pt": PROBE_PT, "probe_digit_1_height_px": probe_px,
                     "alpha_threshold": 128}


def render_line(source: str, font_pt: float) -> Image.Image:
    """Render one mathtext line; return a tight white RGBA image."""
    with plt.rc_context({"mathtext.fontset": FONTSET, "font.family": "STIXGeneral",
                         "text.usetex": False}):
        fig = plt.figure(figsize=(12, 2), dpi=RENDER_DPI)
        fig.text(0.01, 0.5, source, fontsize=font_pt, color="white", va="center", ha="left")
        buf = io.BytesIO()
        fig.savefig(buf, dpi=RENDER_DPI, transparent=True, format="png",
                    metadata={"Software": None})
        plt.close(fig)
    buf.seek(0)
    rgba = Image.open(buf).convert("RGBA")
    alpha = rgba.getchannel("A")
    box = alpha.getbbox()
    if box is None:
        raise ValueError("Empty render: " + source)
    x0, y0, x1, y1 = box
    if x0 == 0 or y0 == 0 or x1 == rgba.width or y1 == rgba.height:
        raise ValueError("Render touches the canvas edge: " + source)
    alpha = alpha.crop((x0 - MARGIN_PX, y0 - MARGIN_PX, x1 + MARGIN_PX, y1 + MARGIN_PX))
    out = Image.new("RGBA", alpha.size, (255, 255, 255, 255))
    out.putalpha(alpha)
    return out


def stack(lines: list[Image.Image]) -> Image.Image:
    width = max(im.width for im in lines)
    height = sum(im.height for im in lines) + LINE_GAP_PX * (len(lines) - 1)
    alpha = Image.new("L", (width, height), 0)
    y = 0
    for im in lines:
        alpha.paste(im.getchannel("A"), (0, y))
        y += im.height + LINE_GAP_PX
    out = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    out.putalpha(alpha)
    return out


def png_bytes(im: Image.Image) -> bytes:
    buf = io.BytesIO()
    im.save(buf, format="PNG", optimize=False, compress_level=9)
    return buf.getvalue()


def build() -> tuple[dict, dict[str, bytes], dict[str, Image.Image]]:
    verify_sources()
    font_pt, calibration = calibration_font_pt()
    entries, blobs, images = {}, {}, {}
    for key, spec in SPECS.items():
        im = stack([render_line(line, font_pt) for line in spec["lines"]])
        if im.width > MAX_WIDTH_PX:
            raise ValueError(f"{key}: width {im.width} px exceeds {MAX_WIDTH_PX} px left column")
        data = png_bytes(im)
        rel = f"presentation/defense_2026/equations/typeset/{key}.png"
        entries[key] = {
            "path": rel, "title": spec["title"],
            "width_px": im.width, "height_px": im.height,
            "display_in": [round(im.width / RENDER_DPI * DISPLAY_SCALE, 3),
                           round(im.height / RENDER_DPI * DISPLAY_SCALE, 3)],
            "sha256": sha256_bytes(data),
            "mathtext": spec["lines"],
            "derived_from": spec["derived_from"],
            "cited_lines": [{"file": FILTER_SOURCE, "line": n, "contains": s} for n, s in spec["anchors"]]
                           + [{"file": LIVE_SOURCE, "line": n, "contains": s} for n, s in spec.get("live_anchors", [])],
            "parameters": spec["parameters"],
            "notes": spec["notes"],
            "provenance": "typeset with matplotlib mathtext from the pinned implementation; not a thesis quotation",
            "colour": "white RGB on transparent alpha; no recolor step needed",
        }
        blobs[key] = data
        images[key] = im
    catalog = {
        "schema_version": 1,
        "kind": "typeset filter equations (not cropped from the thesis)",
        "generator": "presentation/defense_2026/equations/typeset_filters.py",
        "renderer": {"library": "matplotlib mathtext (no TeX)", "matplotlib_version": matplotlib.__version__,
                     "mathtext_fontset": FONTSET, "text_font": "STIXGeneral (matplotlib bundled)",
                     "font_pt": font_pt, "font_calibration": calibration},
        "render_dpi": RENDER_DPI,
        "display_scale": DISPLAY_SCALE,
        "max_width_px": MAX_WIDTH_PX,
        "line_gap_px": LINE_GAP_PX,
        "margin_px": MARGIN_PX,
        "pinned_sources": {FILTER_SOURCE: FILTER_SHA256, LIVE_SOURCE: LIVE_SHA256},
        "filter_source": FILTER_SOURCE,
        "filter_source_sha256": FILTER_SHA256,
        "equations": entries,
    }
    return catalog, blobs, images


def contact_sheet(images: dict[str, Image.Image]) -> Image.Image:
    """Black review sheet at slide scale: 1 source px -> 1.6/600 in at 150 px/in."""
    per_in = 150
    factor = DISPLAY_SCALE / RENDER_DPI * per_in
    catalog = json.loads((DECK / "equation_catalog.json").read_text())["equations"]
    white_ref = DECK / "equations/white" / Path(catalog[CALIBRATION_KEY]["path"]).name
    ref_path = white_ref if white_ref.exists() else ROOT / catalog[CALIBRATION_KEY]["path"]
    ref = Image.open(ref_path).convert("RGBA")
    rows = [("thesis crop " + CALIBRATION_KEY + " (reference scale)", ref)] + list(images.items())
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    scaled = [(label, im.resize((max(1, round(im.width * factor)), max(1, round(im.height * factor))),
                                Image.LANCZOS)) for label, im in rows]
    width = int((LEFT_REGION_RIGHT_IN - FRAGMENT_X_IN) * per_in) + 40
    height = sum(im.height + 44 for _, im in scaled) + 20
    sheet = Image.new("RGB", (width, height), (0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    y = 10
    for label, im in scaled:
        draw.text((20, y), label, fill=(187, 187, 187), font=font)
        y += 26
        if im.mode == "RGBA" and label.startswith("thesis") and ref_path != white_ref:
            im = Image.merge("RGBA", (*[Image.new("L", im.size, 255)] * 3, im.getchannel("A")))
        sheet.paste(im, (20, y), im)
        y += im.height + 18
    # Right edge of the left column.
    draw.line([(20 + int((LEFT_REGION_RIGHT_IN - FRAGMENT_X_IN) * per_in), 0),
               (20 + int((LEFT_REGION_RIGHT_IN - FRAGMENT_X_IN) * per_in), height)], fill=(102, 102, 102))
    return sheet


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true",
                        help="Re-render in memory and compare with the committed PNGs and catalogue; write nothing")
    args = parser.parse_args()
    catalog, blobs, images = build()
    text = json.dumps(catalog, indent=2, ensure_ascii=True) + "\n"
    if args.check:
        failures = []
        if not CATALOG.exists() or CATALOG.read_text() != text:
            failures.append("typeset_catalog.json differs from a fresh render")
        for key, data in blobs.items():
            path = ROOT / catalog["equations"][key]["path"]
            if not path.exists() or path.read_bytes() != data:
                failures.append(f"{path.relative_to(ROOT)} differs from a fresh render")
        for line in failures:
            print("FAIL:", line)
        print("PASS" if not failures else f"FAIL ({len(failures)})")
        sys.exit(1 if failures else 0)
    OUT.mkdir(exist_ok=True)
    for key, data in blobs.items():
        (ROOT / catalog["equations"][key]["path"]).write_bytes(data)
    CATALOG.write_text(text)
    contact_sheet(images).save(OUT / "contact_sheet.png")
    print(f"Wrote {len(blobs)} pieces, {CATALOG.relative_to(ROOT)}, contact sheet; "
          f"font {catalog['renderer']['font_pt']} pt")
    for key, entry in catalog["equations"].items():
        print(f"  {key}: {entry['width_px']}x{entry['height_px']} px -> "
              f"{entry['display_in'][0]:.2f} x {entry['display_in'][1]:.2f} in")


if __name__ == "__main__":
    main()
