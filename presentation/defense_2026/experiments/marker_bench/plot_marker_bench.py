"""Chart for marker_bench: two panels on a black background.

Left:  median detection time per 640x480 frame (ms) vs marker side (px),
       p95 as a lighter band (median-to-p95), one line per detector.
Right: mean corner error (px, constant convention offset removed) vs
       marker side; point area encodes detection rate, and the rates at
       24 and 32 px are printed in a text box. The no-refinement ArUco
       reference is off this scale and is stated in the text box.

Colours are the deck palette given in the brief; because two of them are
close in lightness, every series also has its own marker shape and line
style (secondary encoding).
"""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FixedLocator, NullLocator  # noqa: E402
from matplotlib.transforms import blended_transform_factory  # noqa: E402

STYLE = {
    # name: (colour, marker, linestyle, legend label)
    "aruco_5x5": ("#70B7E6", "o", "-",
                  "ArUco 5x5, OpenCV (pinned, AprilTag refine)"),
    "aruco_5x5_norefine": ("#70B7E6", "o", ":",
                           "ArUco 5x5, OpenCV default (no refine)"),
    "cv_apriltag36h11": ("#A8A8A8", "s", "-",
                         "AprilTag 36h11 dict., OpenCV ArUco detector"),
    "pupil_dec2": ("#FFD088", "^", "-",
                   "AprilTag 3 library, decimate 2 (default)"),
    "pupil_dec1": ("#FFD088", "D", "--",
                   "AprilTag 3 library, decimate 1"),
}
SHORT = {
    "aruco_5x5": "ArUco 5x5 pinned",
    "cv_apriltag36h11": "36h11 dict., ArUco detector",
    "pupil_dec2": "AprilTag 3, decimate 2",
    "pupil_dec1": "AprilTag 3, decimate 1",
}
ORDER = ["aruco_5x5", "aruco_5x5_norefine", "cv_apriltag36h11",
         "pupil_dec2", "pupil_dec1"]
BG = "#000000"
FG = "#FFFFFF"
GRID = "#666666"


def load(path):
    rows = list(csv.DictReader(open(path)))
    data = {}
    for r in rows:
        d = data.setdefault(r["detector"], dict(side=[], tmed=[], tp95=[],
                                                err=[], rate=[]))
        d["side"].append(int(r["side_px"]))
        d["tmed"].append(float(r["time_median_ms"]))
        d["tp95"].append(float(r["time_p95_ms"]))
        d["err"].append(float(r["corner_err_debiased_mean_px"]))
        d["rate"].append(float(r["detection_rate"]))
    return data


def style_axes(ax, sizes):
    ax.set_facecolor(BG)
    ax.set_xscale("log", base=2)
    ax.xaxis.set_major_locator(FixedLocator(sizes))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.set_xticklabels([str(s) for s in sizes])
    ax.set_xlim(sizes[0] / 1.15, sizes[-1] * 1.15)
    ax.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ax.spines.values():
        s.set_color(GRID)
    ax.tick_params(colors=FG, labelsize=15)
    ax.set_xlabel("Marker side in the image (px)", color=FG, fontsize=18)


def plot(summary_csv, out_png):
    plt.rcParams["font.family"] = "DejaVu Sans"
    data = load(summary_csv)
    sizes = sorted(data[ORDER[0]]["side"])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.33, 5.55), dpi=200,
                                 facecolor=BG)
    fig.subplots_adjust(left=0.065, right=0.99, top=0.9, bottom=0.14,
                        wspace=0.2)
    for ax in (a1, a2):
        style_axes(ax, sizes)

    handles, rates, norefine = [], [], None
    for name in ORDER:
        if name not in data:
            continue
        c, m, ls, lab = STYLE[name]
        d = data[name]
        a1.fill_between(d["side"], d["tmed"], d["tp95"], color=c,
                        alpha=0.22, linewidth=0)
        h, = a1.plot(d["side"], d["tmed"], color=c, marker=m, ls=ls, lw=2,
                     ms=7, label=lab)
        handles.append(h)
        if name == "aruco_5x5_norefine":
            # off the accuracy scale; stated as text instead
            norefine = d
            continue
        pts = [(s, e, r) for s, e, r in zip(d["side"], d["err"], d["rate"])
               if e == e]
        if pts:
            s_, e_, r_ = zip(*pts)
            a2.plot(s_, e_, color=c, ls=ls, lw=2)
            a2.scatter(s_, e_, s=[20 + 110 * r for r in r_], color=c,
                       marker=m, zorder=3, edgecolors=BG, linewidths=1)
            rates.append((SHORT[name], d["side"], d["rate"]))

    a1.set_ylabel("Detection time per frame (ms)", color=FG, fontsize=18)
    a1.set_ylim(bottom=0)
    a1.set_title("Speed: median, band to p95 (single thread)", color=FG,
                 fontsize=18, loc="left")
    lines = ["Detection rate at 24 / 32 px:"]
    for lab, sides, rr in rates:
        r24, r32 = rr[sides.index(24)], rr[sides.index(32)]
        lines.append(f"{lab}: {100 * r24:.0f}% / {100 * r32:.0f}%")
    lines.append("100% for all at 64 px and above")
    if norefine is not None:
        e = [x for x in norefine["err"] if x == x]
        lines.append(f"ArUco without refinement: {min(e):.2f}-{max(e):.2f} px"
                     " (off scale)")
    a2.text(0.97, 0.96, "\n".join(lines), transform=a2.transAxes,
            ha="right", va="top", color=FG, fontsize=12, linespacing=1.4,
            bbox=dict(facecolor=BG, edgecolor=GRID, boxstyle="square,pad=0.5"))
    a2.set_ylabel("Mean corner error (px)", color=FG, fontsize=18)
    a2.set_ylim(0, 0.55)   # headroom for the detection-rate text box
    a2.set_title("Corner error, constant offset removed", color=FG,
                 fontsize=18, loc="left")
    # Legend centred at 20.5 ms, in the empty band between the AprilTag 3
    # decimate-1 curve (p95 at most 15.3 ms) and the OpenCV curves (median
    # at least 25.7 ms, summary.csv), so it hides no line or band.
    leg = a1.legend(handles=handles, loc="center",
                    bbox_to_anchor=(0.5, 20.5),
                    bbox_transform=blended_transform_factory(a1.transAxes,
                                                             a1.transData),
                    fontsize=11.5, labelspacing=0.25, borderpad=0.35,
                    frameon=True, facecolor=BG, edgecolor=GRID,
                    labelcolor=FG)
    leg.get_frame().set_alpha(0.85)
    fig.savefig(out_png, dpi=200, facecolor=BG)
    plt.close(fig)


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    plot(here / "summary.csv", here / "chart_marker_bench.png")
