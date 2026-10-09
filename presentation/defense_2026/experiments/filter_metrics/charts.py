"""Two full-slide Q&A charts for filter_metrics.py (2466x1110 px, black background).

Every plotted number is read from the summary table or the filtered arrays that
filter_metrics.py computed in the same run; nothing is typed in by hand.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

W_PX, H_PX, DPI = 2466, 1110, 100
BG, INK, MUTED, GRID = "#000000", "#FFFFFF", "#C8C8C8", "#666666"
RAW_C, BLUE, AMBER = "#A8A8A8", "#70B7E6", "#FFD088"
EXCERPT_ONE_EURO = "oneeuro_1hz"     # live setting (eval/pipeline_smoothness); see DECISIONS.md D-167

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 24,
    "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG,
    "text.color": INK, "axes.labelcolor": INK, "axes.edgecolor": MUTED,
    "xtick.color": INK, "ytick.color": INK, "xtick.labelsize": 24, "ytick.labelsize": 24,
    "axes.labelsize": 28, "axes.titlesize": 30, "axes.titlecolor": INK,
    "grid.color": GRID, "grid.linewidth": 1.0, "legend.fontsize": 22,
    "legend.facecolor": BG, "legend.edgecolor": GRID, "legend.labelcolor": INK,
    "svg.hashsalt": "filter_metrics", "path.simplify": False,
})


def _figure(title):
    fig = plt.figure(figsize=(W_PX/DPI, H_PX/DPI), dpi=DPI)
    fig.suptitle(title, fontsize=42, fontweight="bold", color=INK, x=0.5, y=0.965)
    gs = fig.add_gridspec(1, 2, left=0.06, right=0.985, bottom=0.13, top=0.83,
                          wspace=0.2, width_ratios=[1.0, 1.08])
    return fig, fig.add_subplot(gs[0]), fig.add_subplot(gs[1])


def _style(ax):
    ax.grid(True, axis="y")
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)


def _row(summ, key):
    return summ.set_index("candidate").loc[key]


def _excerpt(ax, times, base, cands, start, n, curves, fs):
    sl = slice(start, start+n)
    t = times[sl]-times[start]
    ax.plot(t, base[sl, 2], color=RAW_C, lw=2.2, marker="o", ms=5, label="Despiked raw", zorder=2)
    for key, color, style, label in curves:
        ax.plot(t, cands[key][2][sl, 2], color=color, lw=4.5, ls=style, label=label, zorder=3)
    ax.set_xlabel("Time in excerpt (s)")
    ax.set_ylabel("Wrist depth z (m)")
    ax.set_xlim(0, (n-1)/fs)
    _style(ax); ax.grid(True, axis="x")
    return t


def _save(fig, path):
    fig.savefig(path, dpi=DPI, facecolor=BG, metadata={"Software": None})
    plt.close(fig)


def offline_chart(out, times, base, cands, summ, start, n, fs):
    fig, left, right = _figure("Offline candidates on the R6b right wrist")
    keys = ["despiked_raw", "savgol_9_2", "median_9", "butter_3hz_filtfilt", "butter_2hz_filtfilt"]
    names = ["Despiked\nraw", "Savitzky-\nGolay 9/2", "Median\n9", "Butterworth\n3 Hz (chosen)", "Butterworth\n2 Hz"]
    shake = [float(_row(summ, k)["shake_mm"]) for k in keys]
    dev = [float(_row(summ, k)["fast_deviation_mm"]) for k in keys]
    x = np.arange(len(keys)); w = 0.38
    b1 = left.bar(x-w/2-0.01, shake, w, color=BLUE, label="Shake (RMS frame-to-frame step)")
    b2 = left.bar(x+w/2+0.01, dev, w, color=AMBER, label="Fast-motion deviation from despiked raw")
    for bars, vals in ((b1, shake), (b2, dev)):
        for bar, v in zip(bars, vals):
            txt = "ref." if v == 0 else f"{v:.1f}"
            left.text(bar.get_x()+bar.get_width()/2, v+0.15, txt, ha="center", va="bottom",
                      fontsize=22, color=INK)
    left.set_xticks(x, names, fontsize=21)
    left.set_ylabel("mm (3-D norm)")
    left.set_ylim(0, max(shake+dev)*1.28)
    left.legend(loc="upper right", frameon=True)
    lags0 = {int(_row(summ, k)["lag_frames"]) for k in keys}
    assert lags0 == {0}, lags0
    left.set_title("All zero phase: lag 0 frames", pad=14)
    _style(left)

    _excerpt(right, times, base, cands, start, n,
             [("butter_3hz_filtfilt", BLUE, "-", "Butterworth 3 Hz filtfilt"),
              ("savgol_9_2", AMBER, "--", "Savitzky-Golay 9/2")], fs)
    right.set_title(f"4 s excerpt, frames {start}-{start+n-1}", pad=14)
    right.legend(loc="lower left", frameon=True)
    right.text(0.98, 0.96, "zero phase: uses future samples", transform=right.transAxes,
               ha="right", va="top", fontsize=26, color=INK,
               bbox=dict(boxstyle="round,pad=0.5", fc=BG, ec=BLUE, lw=2))
    fig.text(0.5, 0.025,
             "R6b right wrist; cross-correlation lag is 0 frames for every offline candidate. "
             "Source: experiments/filter_metrics/summary.csv",
             ha="center", fontsize=20, color=MUTED)
    _save(fig, out/"chart_filter_offline.png")


def realtime_chart(out, times, base, cands, summ, start, n, fs):
    fig, left, right = _figure("Causal candidates: smoothing against lag")
    pts = [("butter_3hz_forward", AMBER, "s", "Butterworth 3 Hz forward"),
           ("oneeuro_0p05hz", BLUE, "o", "One Euro 0.05 Hz"),
           ("oneeuro_1hz", BLUE, "D", "One Euro 1 Hz (live)"),
           ("ema_0p3", RAW_C, "^", "EMA alpha 0.3")]
    # Label anchors in data units (lag ms, shake mm), placed by hand to avoid overlap.
    anchors = {"butter_3hz_forward": (152, 3.55, "center"), "oneeuro_0p05hz": (206, 1.0, "right"),
               "oneeuro_1hz": (70, 1.55, "center"), "ema_0p3": (46, 4.35, "left")}
    for key, color, marker, label in pts:
        r = _row(summ, key)
        lx, ly = float(r["lag_ms_subframe"]), float(r["shake_mm"])
        left.scatter([lx], [ly], s=420, color=color, marker=marker, edgecolors=BG, linewidths=2, zorder=3)
        tx, ty, ha = anchors[key]
        left.annotate(f"{label}\n{ly:.2f} mm, {lx:.0f} ms", (lx, ly), xytext=(tx, ty),
                      textcoords="data", ha=ha, va="center", fontsize=21, color=INK,
                      arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.2, shrinkA=4, shrinkB=12))
    ref = _row(summ, "butter_3hz_filtfilt")
    assert int(ref["lag_frames"]) == 0
    left.scatter([0], [float(ref["shake_mm"])], s=420, facecolors="none", edgecolors=INK,
                 linewidths=3, zorder=3)
    left.annotate(f"Offline Butterworth 3 Hz (reference)\n{float(ref['shake_mm']):.2f} mm, 0 ms",
                  (0, float(ref["shake_mm"])), xytext=(3, 5.3), textcoords="data",
                  ha="left", va="center", fontsize=21, color=MUTED,
                  arrowprops=dict(arrowstyle="-", color=MUTED, lw=1.2, shrinkA=4, shrinkB=12))
    raw = float(_row(summ, "despiked_raw")["shake_mm"])
    left.axhline(raw, color=RAW_C, ls=":", lw=2)
    left.text(4, raw-0.08, f"despiked raw {raw:.2f} mm", va="top", fontsize=21, color=MUTED)
    lags = [float(_row(summ, k)["lag_ms_subframe"]) for k, *_ in pts]
    left.set_xlim(-12, max(lags)*1.18)
    left.set_ylim(0, raw*1.12)
    left.set_xlabel("Lag behind despiked raw (ms, cross-correlation)")
    left.set_ylabel("Shake (mm, 3-D RMS step)")
    left.set_title("Lower-left is better", pad=14)
    _style(left); left.grid(True, axis="x")

    oe, bf = _row(summ, EXCERPT_ONE_EURO), _row(summ, "butter_3hz_forward")
    oe_label = dict((k, l) for k, _, _, l in pts)[EXCERPT_ONE_EURO]
    t = _excerpt(right, times, base, cands, start, n,
                 [(EXCERPT_ONE_EURO, BLUE, "-", f"{oe_label}, lag {float(oe['lag_ms_subframe']):.0f} ms"),
                  ("butter_3hz_forward", AMBER, "--",
                   f"Butterworth 3 Hz forward, lag {float(bf['lag_ms_subframe']):.0f} ms")], fs)
    # Lag arrows: each starts where the despiked raw first crosses a depth level
    # on the descent and has the measured cross-correlation lag as its length, so
    # a pure delay would end on the filtered curve.
    z = base[start:start+n, 2]
    top, span = float(np.nanmax(z)), float(np.nanmax(z)-np.nanmin(z))
    for frac, (row, color) in zip((0.40, 0.58), ((oe, BLUE), (bf, AMBER))):
        level = top-frac*span
        j = int(np.flatnonzero(z <= level)[0])
        tc = t[j-1]+(z[j-1]-level)/(z[j-1]-z[j])*(t[j]-t[j-1])
        lag_s = float(row["lag_ms_subframe"])/1000.0
        right.annotate("", xy=(tc+lag_s, level), xytext=(tc, level),
                       arrowprops=dict(arrowstyle="-|>", color=color, lw=4, mutation_scale=28))
        right.plot([tc], [level], marker="o", ms=10, color=color, zorder=4)
        right.text(tc+lag_s+0.06, level, f"{lag_s*1000:.0f} ms", va="center", fontsize=24,
                   color=INK, bbox=dict(boxstyle="round,pad=0.2", fc=BG, ec="none"))
    right.set_title(f"4 s excerpt, frames {start}-{start+n-1}: output trails input", pad=14)
    right.legend(loc="lower left", frameon=True)
    fig.text(0.5, 0.025,
             "R6b right wrist; lag = shift maximising cross-correlation with despiked raw. "
             "Source: experiments/filter_metrics/summary.csv",
             ha="center", fontsize=20, color=MUTED)
    _save(fig, out/"chart_filter_realtime.png")


def render(out, times, base, cands, summ, start, n, fs):
    offline_chart(out, times, base, cands, summ, start, n, fs)
    realtime_chart(out, times, base, cands, summ, start, n, fs)


# --- Panel mode (deck pages with left text and a right-hand chart) ---------
# The right evidence region of the restrained layout is 6.61 x 5.00 in
# (build_deck.py frame_figure / composite geometry), so the panel charts are
# drawn at that physical size and 200 dpi and placed 1:1: a 12 pt label here
# is a 12 pt label on the slide. The full two-panel charts above are unchanged.
PANEL_IN, PANEL_DPI = (6.61, 5.00), 200
PANEL_RC = {"font.size": 12, "xtick.labelsize": 11, "ytick.labelsize": 11,
            "axes.labelsize": 12, "axes.titlesize": 13, "legend.fontsize": 10.5,
            "grid.linewidth": 0.6, "axes.linewidth": 0.8}


def _panel_figure():
    fig = plt.figure(figsize=PANEL_IN, dpi=PANEL_DPI)
    gs = fig.add_gridspec(2, 1, left=0.12, right=0.985, bottom=0.095, top=0.93,
                          hspace=0.52, height_ratios=[1.12, 1.0])
    return fig, fig.add_subplot(gs[0]), fig.add_subplot(gs[1])


def _panel_excerpt(ax, times, base, cands, start, n, curves, fs):
    sl = slice(start, start+n)
    t = times[sl]-times[start]
    ax.plot(t, base[sl, 2], color=RAW_C, lw=1.0, marker="o", ms=2.2, label="Despiked raw", zorder=2)
    for key, color, style, label in curves:
        ax.plot(t, cands[key][2][sl, 2], color=color, lw=2.0, ls=style, label=label, zorder=3)
    ax.set_xlabel("Time in excerpt (s)", labelpad=2)
    ax.set_ylabel("Wrist depth z (m)")
    ax.set_xlim(0, (n-1)/fs)
    ax.locator_params(axis="y", nbins=4)
    _style(ax); ax.grid(True, axis="x")
    return t


def offline_panel(out, times, base, cands, summ, start, n, fs):
    with plt.rc_context(PANEL_RC):
        fig, top, bottom = _panel_figure()
        keys = ["despiked_raw", "savgol_9_2", "median_9", "butter_3hz_filtfilt", "butter_2hz_filtfilt"]
        names = ["Despiked\nraw", "Savitzky-\nGolay 9/2", "Median\n9", "Butterworth\n3 Hz (chosen)", "Butterworth\n2 Hz"]
        shake = [float(_row(summ, k)["shake_mm"]) for k in keys]
        dev = [float(_row(summ, k)["fast_deviation_mm"]) for k in keys]
        assert {int(_row(summ, k)["lag_frames"]) for k in keys} == {0}
        x = np.arange(len(keys)); w = 0.38
        b1 = top.bar(x-w/2-0.01, shake, w, color=BLUE, label="Shake (RMS step)")
        b2 = top.bar(x+w/2+0.01, dev, w, color=AMBER, label="Fast-motion deviation")
        for bars, vals in ((b1, shake), (b2, dev)):
            for bar, v in zip(bars, vals):
                top.text(bar.get_x()+bar.get_width()/2, v+0.12, "ref." if v == 0 else f"{v:.2f}",
                         ha="center", va="bottom", fontsize=9.5, color=INK)
        top.set_xticks(x, names, fontsize=10)
        top.set_ylabel("mm (3-D norm)")
        top.set_ylim(0, max(shake+dev)*1.42)
        top.locator_params(axis="y", nbins=5)
        top.legend(loc="upper left", ncol=2, frameon=False, borderaxespad=0.2)
        top.set_title("Offline candidates, all at lag 0 frames", pad=6)
        _style(top)
        _panel_excerpt(bottom, times, base, cands, start, n,
                       [("butter_3hz_filtfilt", BLUE, "-", "Butterworth 3 Hz filtfilt"),
                        ("savgol_9_2", AMBER, "--", "Savitzky-Golay 9/2")], fs)
        bottom.set_title(f"4 s excerpt, frames {start}-{start+n-1}", pad=6)
        bottom.legend(loc="upper right", frameon=True, borderaxespad=0.3)
        _save_panel(fig, out/"chart_filter_offline_panel.png")


def realtime_panel(out, times, base, cands, summ, start, n, fs):
    with plt.rc_context(PANEL_RC):
        fig, top, bottom = _panel_figure()
        pts = [("butter_3hz_forward", AMBER, "s", "Butterworth 3 Hz forward"),
               ("oneeuro_0p05hz", BLUE, "o", "One Euro 0.05 Hz"),
               ("oneeuro_1hz", BLUE, "D", "One Euro 1 Hz (live)"),
               ("ema_0p3", RAW_C, "^", "EMA alpha 0.3")]
        # Label anchors in data units (lag ms, shake mm), placed by hand for this size.
        anchors = {"butter_3hz_forward": (142, 4.35, "center"), "oneeuro_0p05hz": (186, 0.75, "center"),
                   "oneeuro_1hz": (95, 1.05, "center"), "ema_0p3": (40, 4.35, "center")}
        for key, color, marker, label in pts:
            r = _row(summ, key)
            lx, ly = float(r["lag_ms_subframe"]), float(r["shake_mm"])
            top.scatter([lx], [ly], s=70, color=color, marker=marker, edgecolors=BG, linewidths=1, zorder=3)
            tx, ty, ha = anchors[key]
            top.annotate(f"{label}\n{ly:.2f} mm, {lx:.0f} ms", (lx, ly), xytext=(tx, ty),
                         textcoords="data", ha=ha, va="center", fontsize=9.5, color=INK,
                         arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.8, shrinkA=2, shrinkB=5))
        raw = float(_row(summ, "despiked_raw")["shake_mm"])
        top.axhline(raw, color=RAW_C, ls=":", lw=1.2)
        top.text(max(float(_row(summ, k)["lag_ms_subframe"]) for k, *_ in pts)*1.16, raw-0.12,
                 f"despiked raw {raw:.2f} mm", va="top", ha="right", fontsize=9.5, color=MUTED)
        lags = [float(_row(summ, k)["lag_ms_subframe"]) for k, *_ in pts]
        top.set_xlim(0, max(lags)*1.18)
        top.set_ylim(0, raw*1.12)
        top.locator_params(axis="both", nbins=5)
        top.set_xlabel("Lag behind despiked raw (ms)", labelpad=2)
        top.set_ylabel("Shake (mm)")
        top.set_title("Causal candidates: lower-left is better", pad=6)
        _style(top); top.grid(True, axis="x")

        oe, bf = _row(summ, EXCERPT_ONE_EURO), _row(summ, "butter_3hz_forward")
        t = _panel_excerpt(bottom, times, base, cands, start, n,
                           [(EXCERPT_ONE_EURO, BLUE, "-", "One Euro 1 Hz (live)"),
                            ("butter_3hz_forward", AMBER, "--", "Butterworth 3 Hz forward")], fs)
        # Same lag-arrow construction as realtime_chart.
        z = base[start:start+n, 2]
        zmax, span = float(np.nanmax(z)), float(np.nanmax(z)-np.nanmin(z))
        for frac, (row, color) in zip((0.40, 0.58), ((oe, BLUE), (bf, AMBER))):
            level = zmax-frac*span
            j = int(np.flatnonzero(z <= level)[0])
            tc = t[j-1]+(z[j-1]-level)/(z[j-1]-z[j])*(t[j]-t[j-1])
            lag_s = float(row["lag_ms_subframe"])/1000.0
            bottom.annotate("", xy=(tc+lag_s, level), xytext=(tc, level),
                            arrowprops=dict(arrowstyle="-|>", color=color, lw=1.8, mutation_scale=12))
            bottom.plot([tc], [level], marker="o", ms=4, color=color, zorder=4)
            bottom.text(tc+lag_s+0.05, level, f"{lag_s*1000:.0f} ms", va="center", fontsize=10.5,
                        color=INK, bbox=dict(boxstyle="round,pad=0.15", fc=BG, ec="none"))
        bottom.set_title(f"4 s excerpt, frames {start}-{start+n-1}: output trails input", pad=6)
        bottom.legend(loc="upper right", frameon=True, borderaxespad=0.3)
        _save_panel(fig, out/"chart_filter_realtime_panel.png")


def _save_panel(fig, path):
    fig.savefig(path, dpi=PANEL_DPI, facecolor=BG, metadata={"Software": None})
    plt.close(fig)


def panel_inputs():
    """Recompute the arrays filter_metrics.main() plots, without rewriting its outputs.

    The plotted numbers come from the committed summary.csv; the excerpt
    arrays are recomputed with the same frozen functions, and the excerpt
    window must equal the one recorded in run_info.json.
    """
    import json
    import sys
    from pathlib import Path
    import pandas as pd
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    import filter_metrics as fm
    frames, times, pos, fs = fm.load_data()
    a = fm.base_args()
    mask = fm.FROZEN.hampel_mask(pos, a.hampel_window, a.hampel_k, a.hampel_floor)
    work = pos.copy(); work[mask] = np.nan
    base, _ = fm.FROZEN.fill_gaps(work, times, a.max_gap, a.edge_fill)
    cands = fm.candidates(base, fs)
    start, _ = fm.choose_excerpt(base, fm.eval_segments(base), fs)
    info = json.loads((here/"run_info.json").read_text())
    assert [int(start), int(start+fm.EXCERPT_FRAMES-1)] == info["excerpt_frames_inclusive"], \
        "excerpt differs from run_info.json; rerun filter_metrics.py first"
    summ = pd.read_csv(here/"summary.csv")
    return here, times, base, cands, summ, int(start), fm.EXCERPT_FRAMES, fs


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Render the filter_metrics charts.")
    parser.add_argument("--panel", action="store_true",
                        help="Write chart_filter_offline_panel.png and chart_filter_realtime_panel.png "
                             "(6.61 x 5.00 in, 200 dpi) for the left-text / right-chart deck layout")
    args = parser.parse_args()
    if not args.panel:
        parser.error("the full charts are written by filter_metrics.py; use --panel here")
    inputs = panel_inputs()
    offline_panel(*inputs)
    realtime_panel(*inputs)
    print("Wrote chart_filter_offline_panel.png and chart_filter_realtime_panel.png")
