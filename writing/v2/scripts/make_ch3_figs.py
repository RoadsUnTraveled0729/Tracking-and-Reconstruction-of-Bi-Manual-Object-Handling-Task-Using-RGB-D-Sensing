"""Generate Chapter 3 figures into writing/v2/figures/."""
import csv, shutil
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrow, FancyBboxPatch, Circle, FancyArrowPatch
from mpl_toolkits.mplot3d import proj3d
import cv2

OUT = "/home/luo/Desktop/New_SandBox/writing/v2/figures/"
KD = "/home/luo/Desktop/New_SandBox/kinematics/dataset/"
FX, FY, CX, CY = 607.5626, 607.0234, 323.9403, 248.0233
F = np.array([1.0, -1.0, 1.0])

# ---- frame-100 camera-space landmarks (pinned CSV) ----
CSVF = "/home/luo/Desktop/New_SandBox/kinematics/dataset/real_20260224/recording_20260224_083945_landmarks_filtered.csv"
names = ["left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
         "left_wrist", "right_wrist", "left_hip", "right_hip"]
with open(CSVF) as f:
    for row in csv.DictReader(f):
        if int(row["frame"]) == 100:
            break
P_cam = {n: np.array([float(row[n + "_x"]), float(row[n + "_y"]), float(row[n + "_z"])]) for n in names}
P = {n: F * P_cam[n] for n in names}


def px(p_cam):
    return (int(round(FX * p_cam[0] / p_cam[2] + CX)), int(round(FY * p_cam[1] / p_cam[2] + CY)))


def axes3d_clean(ax, lim=1.0):
    ax.set_xlim(-lim, lim); ax.set_ylim(-lim, lim); ax.set_zlim(-lim, lim)
    ax.set_box_aspect([1, 1, 1])
    ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
    ax.xaxis.pane.fill = ax.yaxis.pane.fill = ax.zaxis.pane.fill = False


def arrow3(ax, o, d, color, label=None, lw=2.2, ls="-", fs=13):
    ax.quiver(o[0], o[1], o[2], d[0], d[1], d[2], color=color, lw=lw,
              arrow_length_ratio=0.12, linestyle=ls)
    if label:
        e = np.asarray(o) + np.asarray(d) * 1.18
        ax.text(e[0], e[1], e[2], label, color=color, fontsize=fs)

# =====================================================================
# Fig 3.1  (a) sensor schematic with camera frame  (b) Unity still with axes
# =====================================================================
fig = plt.figure(figsize=(11, 4.4))
ax = fig.add_subplot(1, 2, 1)
# D435 front view schematic
body = FancyBboxPatch((-4.5, -0.9), 9.0, 1.8, boxstyle="round,pad=0.25,rounding_size=0.8",
                      fc="#2b2b2b", ec="black")
ax.add_patch(body)
for cx_, r, fc, lbl in [(-3.2, 0.42, "#556", "left imager"), (-1.1, 0.42, "#556", "IR projector"),
                        (1.0, 0.42, "#556", "right imager"), (3.1, 0.5, "#334", "RGB")]:
    ax.add_patch(Circle((cx_, 0), r, fc=fc, ec="#99a"))
    ax.annotate(lbl, (cx_, -0.55), ha="center", va="top", fontsize=8, color="#333",
                xytext=(cx_, -2.0), textcoords="data",
                arrowprops=dict(arrowstyle="-", color="#888", lw=0.7))
# camera frame at the RGB imager: x right, y down, z out of the sensor (toward scene)
o = np.array([3.1, 0.0])
ax.add_patch(FancyArrow(o[0], o[1], 2.2, 0, width=0.03, head_width=0.22, color="crimson"))
ax.text(5.5, 0.12, "x (image right)", color="crimson", fontsize=11)
ax.add_patch(FancyArrow(o[0], o[1], 0, -2.2, width=0.03, head_width=0.22, color="green"))
ax.text(3.25, -2.5, "y (image down)", color="green", fontsize=11)
ax.add_patch(Circle((o[0], o[1]), 0.16, fc="royalblue", ec="royalblue"))
ax.add_patch(Circle((o[0], o[1]), 0.05, fc="white", ec="white"))
ax.text(1.8, 1.05, "z (depth, out of the page toward the scene)", color="royalblue", fontsize=11)
ax.set_xlim(-6, 9.5); ax.set_ylim(-3.6, 2.2); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("(a) D435 camera frame $\\mathcal{C}$ (right-handed)", fontsize=11)

ax = fig.add_subplot(1, 2, 2)
img = plt.imread(KD + "pose_reference.png")
ax.imshow(img)
h, w = img.shape[0], img.shape[1]
ox, oy = int(w * 0.50), int(h * 0.86)
L = int(h * 0.28)
ax.annotate("", xy=(ox + L, oy), xytext=(ox, oy),
            arrowprops=dict(arrowstyle="-|>", color="crimson", lw=2.4))
ax.text(ox + L + 8, oy + 6, "x", color="crimson", fontsize=14, weight="bold")
ax.annotate("", xy=(ox, oy - L), xytext=(ox, oy),
            arrowprops=dict(arrowstyle="-|>", color="lime", lw=2.4))
ax.text(ox + 8, oy - L - 8, "y (up)", color="lime", fontsize=14, weight="bold")
ax.annotate("", xy=(ox - int(L * 0.62), oy - int(L * 0.40)), xytext=(ox, oy),
            arrowprops=dict(arrowstyle="-|>", color="deepskyblue", lw=2.4))
ax.text(ox - int(L * 0.62) - 10, oy - int(L * 0.40) - 10, "z (forward)",
        color="deepskyblue", fontsize=13, weight="bold", ha="right")
ax.axis("off")
ax.set_title("(b) Unity frame $\\mathcal{U}$ (left-handed, y up)", fontsize=11)
plt.tight_layout()
plt.savefig(OUT + "ch3_fig1_sensor_unity.png", dpi=150, bbox_inches="tight")
plt.close()

# =====================================================================
# Fig 3.2  co-located origins: camera frame vs person frame + sample point
# =====================================================================
fig = plt.figure(figsize=(7.2, 6.0))
ax = fig.add_subplot(projection="3d")
axes3d_clean(ax, 1.05)
# draw with matplotlib's default 3D orientation; label semantics only
arrow3(ax, [0, 0, 0], [0.95, 0, 0], "crimson", "x  (shared)")
arrow3(ax, [0, 0, 0], [0, 0.95, 0], "royalblue", "z  (shared, depth)")
arrow3(ax, [0, 0, 0], [0, 0, -0.95], "green", "y  camera (down)")
arrow3(ax, [0, 0, 0], [0, 0, 0.95], "darkorange", "y  person (up)", ls="--")
w_cam = np.array([-0.0718, -0.1638, 0.9938])
pt = np.array([w_cam[0], w_cam[2], -w_cam[1]])       # plot basis: (x, z, physical up)
ax.scatter(*pt, color="purple", s=55)
ax.text(pt[0] - 1.15, pt[1], pt[2] + 0.12,
        "ONE physical wrist point (frame 100):\n"
        "read in $\\mathcal{C}$: (-0.072, -0.164, 0.994)\n"
        "read in $\\mathcal{P}$: (-0.072, +0.164, 0.994)",
        color="purple", fontsize=10)
ax.plot([pt[0], pt[0]], [pt[1], pt[1]], [0, pt[2]], color="gray", ls=":", lw=1.2)
ax.scatter([0], [0], [0], color="black", s=40)
ax.text(0.05, 0.02, -0.22, "one shared origin\n(the optical center)", fontsize=10)
ax.set_title("Camera frame $\\mathcal{C}$ and person space $\\mathcal{P}=F\\,\\mathcal{C}$,"
             " $F=\\mathrm{diag}(1,-1,1)$: only y flips", fontsize=11)
ax.view_init(elev=18, azim=-55)
plt.tight_layout()
plt.savefig(OUT + "ch3_fig2_colocated.png", dpi=150, bbox_inches="tight")
plt.close()

# =====================================================================
# Fig 3.3  mannequin chain schematic with co-located triads (robotics style)
# =====================================================================
fig, ax = plt.subplots(figsize=(7.6, 6.4))
# stick mannequin, front view, subject facing the viewer => subject's RIGHT is viewer's LEFT
hipR, hipL = np.array([-0.9, 0.0]), np.array([0.9, 0.0])
shR, shL = np.array([-1.05, 2.6]), np.array([1.05, 2.6])
elR = np.array([-2.05, 1.9]); wrR = np.array([-1.75, 0.9])
elL = np.array([2.05, 1.9]); wrL = np.array([1.75, 0.9])
head = np.array([0.0, 3.45])
ax.add_patch(Circle(head, 0.42, fc="none", ec="#444", lw=2))
for a, b in [(hipR, hipL), (hipR, shR), (hipL, shL), (shR, shL),
             (shR, elR), (elR, wrR), (shL, elL), (elL, wrL)]:
    ax.plot([a[0], b[0]], [a[1], b[1]], color="#444", lw=2.5, solid_capstyle="round")
for p, lbl, dx, dy in [(hipR, "L24 right hip", -0.15, -0.42), (hipL, "L23 left hip", 0.1, -0.42),
                       (shR, "L12", 0.12, 0.22), (shL, "L11", -0.32, 0.22),
                       (elR, "L14", -0.05, 0.25), (wrR, "L16", -0.55, -0.05),
                       (elL, "L13", 0.08, 0.25), (wrL, "L15", 0.15, -0.05)]:
    ax.add_patch(Circle(p, 0.09, fc="black"))
    ax.text(p[0] + dx, p[1] + dy, lbl, fontsize=10)


def triad(ax, o, scale, lbls=("x", "y", "z"), lw=2.0, zdir=1):
    # x toward subject's right (viewer's left), y up, z out of chest (toward viewer, drawn oblique)
    ax.annotate("", xy=(o[0] - scale, o[1]), xytext=o,
                arrowprops=dict(arrowstyle="-|>", color="crimson", lw=lw))
    ax.text(o[0] - scale - 0.28, o[1] - 0.06, lbls[0], color="crimson", fontsize=11)
    ax.annotate("", xy=(o[0], o[1] + scale), xytext=o,
                arrowprops=dict(arrowstyle="-|>", color="green", lw=lw))
    ax.text(o[0] + 0.06, o[1] + scale + 0.07, lbls[1], color="green", fontsize=11)
    ax.annotate("", xy=(o[0] - scale * 0.5 * zdir, o[1] - scale * 0.5), xytext=o,
                arrowprops=dict(arrowstyle="-|>", color="royalblue", lw=lw))
    ax.text(o[0] - scale * 0.5 * zdir - 0.1, o[1] - scale * 0.5 - 0.28, lbls[2],
            color="royalblue", fontsize=11)


triad(ax, hipR, 0.75)
ax.text(-1.15, -1.05, "root frame $R_{root}$ at L24\n(columns: right, up, forward)",
        fontsize=10, ha="center")
triad(ax, shR, 0.6)
ax.text(-2.75, 3.45, "L12 shoulder frame:\nsame orientation as the root,\norigin moved to L12",
        fontsize=10, ha="center")
# elbow triad rotated so x continues the upper-arm axis (fully rotated arm frame)
ua_dir = (elR - shR) / np.linalg.norm(elR - shR)
perp = np.array([-ua_dir[1], ua_dir[0]])
sc = 0.55
ax.annotate("", xy=tuple(elR + sc * ua_dir), xytext=tuple(elR),
            arrowprops=dict(arrowstyle="-|>", color="crimson", lw=2.0))
ax.text(*(elR + sc * ua_dir + np.array([-0.28, -0.15])), "x", color="crimson", fontsize=11)
ax.annotate("", xy=tuple(elR + sc * perp), xytext=tuple(elR),
            arrowprops=dict(arrowstyle="-|>", color="green", lw=2.0))
ax.text(*(elR + sc * perp + np.array([0.08, 0.08])), "y", color="green", fontsize=11)
ax.annotate("", xy=tuple(elR + sc * 0.55 * np.array([-0.85, -0.55])), xytext=tuple(elR),
            arrowprops=dict(arrowstyle="-|>", color="royalblue", lw=2.0))
ax.text(*(elR + sc * 0.55 * np.array([-0.85, -0.55]) + np.array([-0.24, -0.24])), "z",
        color="royalblue", fontsize=11)
ax.text(-3.55, 0.9, "L14 elbow frame:\nfully rotated arm frame\n$R_{root}R_y R_z R_x$\n"
        "(x continues the arm axis)", fontsize=10, ha="center")
ax.annotate("", xy=(shR[0] - 0.03, shR[1] - 0.35), xytext=(hipR[0] - 0.25, hipR[1] + 0.35),
            arrowprops=dict(arrowstyle="-|>", color="#999", lw=1.6,
                            connectionstyle="arc3,rad=0.25"))
ax.annotate("", xy=(elR[0] + 0.15, elR[1] + 0.25), xytext=(shR[0] - 0.3, shR[1] - 0.1),
            arrowprops=dict(arrowstyle="-|>", color="#999", lw=1.6,
                            connectionstyle="arc3,rad=0.2"))
ax.text(-2.15, 2.75, "parent\nchain", fontsize=9, color="#777", ha="center")
ax.text(0.0, -1.7, "front view: the subject faces the sensor, so the subject's RIGHT side\n"
        "appears on the LEFT of the image; x points to the subject's right",
        fontsize=10, ha="center", style="italic")
ax.set_xlim(-4.6, 3.4); ax.set_ylim(-2.1, 4.1); ax.set_aspect("equal"); ax.axis("off")
plt.tight_layout()
plt.savefig(OUT + "ch3_fig3_chain_mannequin.png", dpi=150, bbox_inches="tight")
plt.close()

# =====================================================================
# Fig 3.4  torso frame on the real photo: (a) input vectors, (b) axes
# =====================================================================
img0 = cv2.imread("/home/luo/Desktop/New_SandBox/integration/dataset/real_color_frame100.png")

imgA = img0.copy()
p24px, p23px, p12px = px(P_cam["right_hip"]), px(P_cam["left_hip"]), px(P_cam["right_shoulder"])
cv2.arrowedLine(imgA, p23px, p24px, (0, 60, 230), 3, cv2.LINE_AA, tipLength=0.09)
cv2.arrowedLine(imgA, p24px, p12px, (30, 200, 255), 3, cv2.LINE_AA, tipLength=0.09)
for p, name in [(p24px, "L24"), (p23px, "L23"), (p12px, "L12")]:
    cv2.circle(imgA, p, 6, (255, 255, 255), -1, cv2.LINE_AA)
    cv2.circle(imgA, p, 6, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(imgA, name, (p[0] + 10, p[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(imgA, "hip line p24 - p23", (p24px[0] - 55, p24px[1] + 42),
            cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 60, 230), 2, cv2.LINE_AA)
cv2.putText(imgA, "s = p12 - p24", (p12px[0] - 190, p12px[1] - 12),
            cv2.FONT_HERSHEY_SIMPLEX, 0.62, (30, 200, 255), 2, cv2.LINE_AA)

imgB = img0.copy()
p23u, p24u, p12u = P["left_hip"], P["right_hip"], P["right_shoulder"]
r = (p24u - p23u) / np.linalg.norm(p24u - p23u)
s = p12u - p24u
fw = np.cross(r, s); fw /= np.linalg.norm(fw)
up = np.cross(fw, r)
o_cam = P_cam["right_hip"]
for a, col, lbl, dx, dy in [(r, (0, 0, 255), "x (right)", -95, 24), (up, (0, 200, 0), "y (up)", 8, -8),
                            (fw, (255, 80, 0), "z (forward)", 10, 22)]:
    tip_cam = o_cam + 0.30 * (F * a)
    cv2.arrowedLine(imgB, px(o_cam), px(tip_cam), col, 3, cv2.LINE_AA, tipLength=0.12)
    t = px(tip_cam)
    cv2.putText(imgB, lbl, (t[0] + dx, t[1] + dy), cv2.FONT_HERSHEY_SIMPLEX, 0.62, col, 2, cv2.LINE_AA)
cv2.circle(imgB, px(o_cam), 6, (255, 255, 255), -1, cv2.LINE_AA)
cv2.putText(imgB, "origin: L24", (px(o_cam)[0] - 40, px(o_cam)[1] + 46),
            cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)

fig, axs = plt.subplots(1, 2, figsize=(11, 4.3))
axs[0].imshow(cv2.cvtColor(imgA, cv2.COLOR_BGR2RGB)); axs[0].axis("off")
axs[0].set_title("(a) the two input vectors (frame 100)", fontsize=11)
axs[1].imshow(cv2.cvtColor(imgB, cv2.COLOR_BGR2RGB)); axs[1].axis("off")
axs[1].set_title("(b) the finished torso frame projected onto the image", fontsize=11)
plt.tight_layout()
plt.savefig(OUT + "ch3_fig4_torso_photo.png", dpi=150, bbox_inches="tight")
plt.close()

# =====================================================================
# Fig 3.5  arm segments drawn on the real photo (both arms)
# =====================================================================
imgC = img0.copy()
segs = [("right_shoulder", "right_elbow", (0, 140, 255), "R upper arm"),
        ("right_elbow", "right_wrist", (0, 60, 230), "R forearm"),
        ("left_shoulder", "left_elbow", (255, 180, 40), "L upper arm"),
        ("left_elbow", "left_wrist", (230, 90, 0), "L forearm")]
for a, b, col, lbl in segs:
    pa, pb = px(P_cam[a]), px(P_cam[b])
    cv2.arrowedLine(imgC, pa, pb, col, 3, cv2.LINE_AA, tipLength=0.1)
lm = {"right_shoulder": "L12", "right_elbow": "L14", "right_wrist": "L16",
      "left_shoulder": "L11", "left_elbow": "L13", "left_wrist": "L15"}
for n, lbl in lm.items():
    p = px(P_cam[n])
    cv2.circle(imgC, p, 5, (255, 255, 255), -1, cv2.LINE_AA)
    cv2.circle(imgC, p, 5, (0, 0, 0), 1, cv2.LINE_AA)
    dx = -58 if "right" in n else 10
    cv2.putText(imgC, lbl, (p[0] + dx, p[1] - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                (255, 255, 255), 2, cv2.LINE_AA)
cv2.putText(imgC, "subject's RIGHT arm", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
            (0, 140, 255), 2, cv2.LINE_AA)
cv2.putText(imgC, "subject's LEFT arm", (400, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.65,
            (255, 180, 40), 2, cv2.LINE_AA)
cv2.imwrite(OUT + "ch3_fig5_arm_photo.png", imgC)

# =====================================================================
# Fig 3.6  swing-twist schematic
# =====================================================================
fig = plt.figure(figsize=(11, 5.0))
ax = fig.add_subplot(1, 2, 1, projection="3d")
axes3d_clean(ax, 1.05)
arrow3(ax, [0, 0, 0], [1.0, 0, 0], "#bbb", None, lw=1.5)
ax.text(1.06, 0, -0.07, "rest arm $+\\hat{x}$", color="#888", fontsize=11)
arrow3(ax, [0, 0, 0], [0, 1.0, 0], "royalblue", "z", lw=1.5)
arrow3(ax, [0, 0, 0], [0, 0, 1.0], "green", "y", lw=1.5)
a_hat = np.array([0.1894, -0.8055, 0.5615])          # frame-100 local arm dir (x,y,z)
a_plot = np.array([a_hat[0], a_hat[2], a_hat[1]])    # plot basis (x, z, y-up)
arrow3(ax, [0, 0, 0], a_plot, "crimson", None, lw=2.6)
ax.text(a_plot[0] + 0.05, a_plot[1] + 0.05, a_plot[2] - 0.25,
        "$\\hat{a}$ observed\nupper arm", color="crimson", fontsize=11)
th = np.linspace(0, 1, 40)
arc = np.array([(1 - t) * np.array([0.55, 0, 0]) + t * 0.55 * a_plot for t in th])
arc = 0.55 * arc / np.linalg.norm(arc, axis=1, keepdims=True)
ax.plot(arc[:, 0], arc[:, 1], arc[:, 2], color="purple", lw=2, ls="--")
ax.text(0.42, 0.1, -0.42, "swing $R_y(\\theta_y)R_z(\\theta_z)$", color="purple", fontsize=11)
ax.set_title("(a) swing aims the arm; $\\hat{a}=(c_yc_z,\\ s_z,\\ -s_yc_z)$", fontsize=11)
ax.view_init(elev=16, azim=-48)

ax = fig.add_subplot(1, 2, 2, projection="3d")
axes3d_clean(ax, 1.05)
arrow3(ax, [-0.6, 0, 0], [1.5, 0, 0], "crimson", None, lw=2.6)
tt = np.linspace(0, 2 * np.pi, 60)
ax.plot(0.55 * np.ones_like(tt), 0.52 * np.cos(tt), 0.52 * np.sin(tt),
        color="purple", lw=1.6, ls=":")
arrow3(ax, [0.55, 0, 0], [0, 0.52, 0], "royalblue", None, lw=2.2)
tw = np.radians(38)
arrow3(ax, [0.55, 0, 0], [0, 0.52 * np.cos(tw), -0.52 * np.sin(tw)], "darkorange", None, lw=2.2)
ys, zs = np.meshgrid(np.linspace(-0.62, 0.62, 2), np.linspace(-0.62, 0.62, 2))
ax.plot_surface(0.55 * np.ones_like(ys), ys, zs, alpha=0.12, color="gray")
ax.view_init(elev=14, azim=-55)
ax.set_title("(b) twist $R_x(\\theta_\\tau)$ rolls about the arm axis", fontsize=11)
ax.text2D(0.02, 0.92, "arm axis (un-swung back to $+\\hat{x}$)", color="crimson",
          fontsize=10, transform=ax.transAxes)
ax.text2D(0.02, 0.84, "$+\\hat{z}$: zero-twist forearm direction\n(elbow flexes forward)",
          color="royalblue", fontsize=10, transform=ax.transAxes)
ax.text2D(0.02, 0.72, "twisted forearm $\\perp$ component", color="darkorange",
          fontsize=10, transform=ax.transAxes)
ax.text2D(0.02, 0.06, "gray: y-z plane $\\perp$ to the axis — twist is read here:\n"
          "$\\theta_\\tau=\\mathrm{atan2}(-f'_y,\\ f'_z)$", fontsize=10, transform=ax.transAxes)
plt.tight_layout()
plt.savefig(OUT + "ch3_fig6_swing_twist.png", dpi=150, bbox_inches="tight")
plt.close()

# =====================================================================
# Fig 3.7  ZXY-applied rotation order, 4 panels
# =====================================================================
def rz(d):
    c, s = np.cos(np.radians(d)), np.sin(np.radians(d))
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def rx(d):
    c, s = np.cos(np.radians(d)), np.sin(np.radians(d))
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def ry(d):
    c, s = np.cos(np.radians(d)), np.sin(np.radians(d))
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])

steps = [("start: identity", np.eye(3)),
         ("1) $R_z(z)$, z = 30$^\\circ$", rz(30)),
         ("2) $R_x(x)\\,R_z(z)$, x = 25$^\\circ$", rx(25) @ rz(30)),
         ("3) $R_y(y)\\,R_x(x)\\,R_z(z)$, y = 40$^\\circ$", ry(40) @ rx(25) @ rz(30))]
fig = plt.figure(figsize=(13, 3.6))
for i, (title, R) in enumerate(steps):
    ax = fig.add_subplot(1, 4, i + 1, projection="3d")
    axes3d_clean(ax, 1.0)
    for j, (col, lbl) in enumerate([("crimson", "x"), ("green", "y"), ("royalblue", "z")]):
        c = R[:, j]
        cp = np.array([c[0], c[2], c[1]])
        arrow3(ax, [0, 0, 0], cp * 0.9, col, lbl, lw=2.2)
    for j, col in enumerate(["#e8a", "#9c9", "#9ae"]):
        c = np.eye(3)[:, j]
        cp = np.array([c[0], c[2], c[1]])
        ax.plot([0, cp[0] * 0.9], [0, cp[1] * 0.9], [0, cp[2] * 0.9], color=col, lw=1, ls=":")
    ax.set_title(title, fontsize=10)
    ax.view_init(elev=18, azim=-60)
plt.suptitle("Unity Euler order: angles applied z first, then x, then y, about parent axes"
             "  $\\Rightarrow$  $R = R_y R_x R_z$", fontsize=11, y=1.04)
plt.tight_layout()
plt.savefig(OUT + "ch3_fig7_zxy_order.png", dpi=150, bbox_inches="tight")
plt.close()

# =====================================================================
# Fig 3.8  root-pose stills 2x2 ; Fig 3.9 twist stills 1x3
# =====================================================================
fig, axs = plt.subplots(2, 2, figsize=(10, 6.4))
for ax, (fn, ttl) in zip(axs.flat, [
        ("pose_reference.png", "(a) reference: sent Euler (0, 180, 0)"),
        ("pose_yaw_p30.png", "(b) yaw +30$^\\circ$: (0, 210, 0)"),
        ("pose_pitch_p20.png", "(c) pitch +20$^\\circ$ (bow): (20, 180, 0)"),
        ("pose_roll_p20.png", "(d) roll +20$^\\circ$ (lean): (0, 180, 20)")]):
    ax.imshow(plt.imread(KD + fn)); ax.axis("off"); ax.set_title(ttl, fontsize=10)
plt.tight_layout()
plt.savefig(OUT + "ch3_fig8_root_stills.png", dpi=150, bbox_inches="tight")
plt.close()

fig, axs = plt.subplots(1, 3, figsize=(12, 3.1))
for ax, (fn, ttl) in zip(axs, [
        ("arm_pose_reference.png", "(a) rest: arm out to the right,\nelbow bent, zero twist"),
        ("arm_twist_p90.png", "(b) twist +90$^\\circ$ (internal):\nforearm straight down"),
        ("arm_twist_m90.png", "(c) twist $-$90$^\\circ$ (external):\nforearm straight up")]):
    ax.imshow(plt.imread(KD + fn)); ax.axis("off"); ax.set_title(ttl, fontsize=10)
plt.tight_layout()
plt.savefig(OUT + "ch3_fig9_twist_stills.png", dpi=150, bbox_inches="tight")
plt.close()

# copies of single pinned stills used directly
shutil.copy(KD + "elbow_straight.png", OUT + "ch3_fig10_elbow_straight.png")
shutil.copy(KD + "arm_full_allangles.png", OUT + "ch3_fig11_arm_full.png")

print("done")
