"""Chapter 8 figure.

fig1: the two verified conditioning laws from thesis/D1_limitations.md,
drawn from their formulas with D1's numerically verified points marked:
(a) shoulder-twist noise amplification 1/|sin e_y| vs elbow flexion
    (verified 1.41x at 45 deg, 4.13x at 14 deg, 11.3x at 5 deg);
(b) ZXY Euler extraction sensitivity 1/cos x vs pitch
    (verified ~34x at 89 deg, ~345x at 89.9 deg).
No data is invented: curves are the derived laws, points are D1's pins.
"""
import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = "/home/luo/Desktop/New_SandBox/writing/v2/figures"

fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.6, 4.2))

ey = np.linspace(2, 90, 500)
a1.semilogy(ey, 1 / np.sin(np.radians(ey)), color="#2e5e8c", lw=1.6)
pts = [(45, 1.41), (14, 4.13), (5, 11.3)]
a1.plot(*zip(*pts), "o", color="#b03030", ms=6)
for x, y in pts:
    a1.annotate(f"{y}x at {x} deg", (x, y), textcoords="offset points",
                xytext=(8, 4), fontsize=8.5, color="#b03030")
a1.set_xlabel("elbow flexion magnitude (deg)")
a1.set_ylabel("twist noise amplification (x)")
a1.set_title("shoulder twist: amplification 1 / |sin(elbow flexion)|",
             fontsize=10)
a1.grid(alpha=0.3, which="both")
a1.text(88, 15, "straight elbow: twist exactly\nunobservable "
        "(any 3-landmark arm)", fontsize=8.5, color="#555555", ha="right")

x = np.linspace(0, 89.95, 500)
a2.semilogy(x, 1 / np.cos(np.radians(x)), color="#2e5e8c", lw=1.6)
pts2 = [(89, 34), (89.9, 345)]
a2.plot(*zip(*pts2), "o", color="#b03030", ms=6)
a2.annotate("34x at 89 deg", pts2[0], textcoords="offset points",
            xytext=(-78, 0), fontsize=8.5, color="#b03030")
a2.annotate("345x at 89.9 deg", pts2[1], textcoords="offset points",
            xytext=(-95, -4), fontsize=8.5, color="#b03030")
a2.set_xlabel("pitch angle x (deg)")
a2.set_ylabel("Euler extraction sensitivity (x)")
a2.set_title("ZXY Euler angles: sensitivity 1 / cos(pitch)", fontsize=10)
a2.grid(alpha=0.3, which="both")
a2.text(4, 100, "computation stays on matrices;\nEuler only at the "
        "display interface", fontsize=8.5, color="#555555")

fig.tight_layout()
fig.savefig(f"{OUT}/ch8_fig1_conditioning.png", dpi=200)
plt.close(fig)
print("ch8 figure written")
