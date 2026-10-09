"""Chapter 7 figures.

fig1 real-time architecture (3 processes + unchanged Unity receiver,
     start barrier, packet names and sizes)
fig2 copy of the pinned solver benchmark figure (bench_solver.png)
fig3 copy of the pinned live-demo still (rt_still.png)
"""
import shutil

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = "/home/luo/Desktop/New_SandBox"
OUT = f"{ROOT}/writing/v2/figures"


def box(ax, x, y, w, h, text, fc="#eef3fb", ec="#3a5a8c", fs=8.6, lw=1.2):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25",
                                fc=fc, ec=ec, lw=lw, mutation_scale=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)


def arrow(ax, p, q, color="#3a5a8c", lw=1.4, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, color=color,
                                 lw=lw, linestyle=ls, mutation_scale=13,
                                 shrinkA=2, shrinkB=2))


fig, ax = plt.subplots(figsize=(10.8, 6.0))
ax.set_xlim(0, 100); ax.set_ylim(0, 60); ax.axis("off")

# source
box(ax, 2, 36, 15, 12,
    "recorded bag\nplayed at\nrecorded pacing\n(live-camera\nstand-in)",
    fc="#f4f4f4", ec="#555555")

# start barrier
box(ax, 2, 22, 15, 8, "start barrier\n(sync file)", fc="#fdeaea",
    ec="#b03030", fs=8.4)
ax.text(9.5, 18.6,
        "unsynchronized start:\n567 ms skew; with the\nbarrier: p50 0 ms,\nmax 33.4 ms (one frame)",
        fontsize=7.6, ha="center", va="top", color="#b03030")

# the two pipelines
box(ax, 26, 44, 26, 11,
    "process A: person\nalign, MediaPipe, deproject,\ncausal filter, 13-angle solve",
    fc="#eef7ee", ec="#2e7d32")
box(ax, 26, 27, 26, 11,
    "process B: object\ndetect + corner refine, IPPE,\ncausal filter, world map",
    fc="#fff8e8", ec="#b26a00")

# shm channels
box(ax, 58, 45.5, 18, 8, "/dev/shm/rt_person\nPSR1, 84 B per frame",
    fc="#eef7ee", ec="#2e7d32", fs=8.2)
box(ax, 58, 28.5, 18, 8, "/dev/shm/rt_object\nPSB2, 44 B per frame",
    fc="#fff8e8", ec="#b26a00", fs=8.2)

# merger
box(ax, 40, 8, 26, 11,
    "process I: merger\n(the only layer reading both)\npairs person + object by frame",
    fc="#f0e8f8", ec="#6a3a8c")

# unity
box(ax, 74, 8, 24, 11,
    "Unity\nIntegratedSceneReceiver\nUNCHANGED from Chapter 5",
    fc="#eef3fb", ec="#3a5a8c")

# arrows
arrow(ax, (17.6, 44), (25.4, 48), color="#2e7d32")
arrow(ax, (17.6, 40), (25.4, 34), color="#b26a00")
arrow(ax, (9.5, 30.6), (9.5, 35.4), color="#b03030", lw=1.1, ls=":")
arrow(ax, (52.6, 49.5), (57.4, 49.5), color="#2e7d32")
arrow(ax, (52.6, 32.5), (57.4, 32.5), color="#b26a00")
arrow(ax, (67, 44.9), (55, 19.6), color="#2e7d32")
arrow(ax, (67, 27.9), (57, 19.6), color="#b26a00")
arrow(ax, (66.6, 13.5), (73.4, 13.5), color="#6a3a8c")
ax.text(86, 20.5, "PSB3 100 B once + PSI1 108 B per frame", fontsize=7.8,
        ha="center", va="bottom", color="#6a3a8c")

ax.text(50, 2.5,
        "processes A and B share no code and no data; the same seqlock "
        "shared-memory transport and packet contract as the offline replay",
        fontsize=8.2, ha="center", style="italic", color="#444444")

fig.savefig(f"{OUT}/ch7_fig1_rt_arch.png", dpi=200, bbox_inches="tight")
plt.close(fig)

shutil.copy(f"{ROOT}/realtime/dataset/bench_solver.png",
            f"{OUT}/ch7_fig2_bench.png")
shutil.copy(f"{ROOT}/realtime/dataset/rt_still.png",
            f"{OUT}/ch7_fig3_rt_still.png")
print("ch7 figures written")
