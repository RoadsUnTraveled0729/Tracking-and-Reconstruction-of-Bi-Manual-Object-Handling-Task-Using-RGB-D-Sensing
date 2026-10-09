"""Presentation-only plots; input arrays and evaluation statistics are unchanged."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
from PIL import Image
from ch7_trail_data import intervals, load

COLORS = {"measured": "tab:blue", "recovered": "tab:orange", "held": "0.45"}


def trim(path, pad=12):
    """Cut the white margin matplotlib leaves around a 3D axes box; the
    drawn content is untouched."""
    image = Image.open(path).convert("RGB")
    mask = (np.asarray(image) < 250).any(axis=2)
    rows, cols = np.where(mask.any(axis=1))[0], np.where(mask.any(axis=0))[0]
    image.crop((max(cols[0] - pad, 0), max(rows[0] - pad, 0),
                min(cols[-1] + pad + 1, image.width), min(rows[-1] + pad + 1, image.height))).save(path)


def settle_3d(fig, ax):
    """Centre the projected 3D content in its slot: mplot3d draws the box
    high in the axes and reports the whole slot as its bounding box, so the
    drawn rows are measured from the rendered pixels. Returns the content
    box in figure fractions after the shift. Display only."""
    fig.canvas.draw()
    fig.set_layout_engine("none")
    slot = ax.get_position()
    pixels = np.asarray(fig.canvas.buffer_rgba())[..., :3]
    height, width = pixels.shape[:2]
    left, right = int(slot.x0 * width), int(np.ceil(slot.x1 * width))
    top, bottom = int((1 - slot.y1) * height), int(np.ceil((1 - slot.y0) * height))
    drawn = np.where((pixels[top:bottom, left:right] < 250).any(axis=(1, 2)))[0]
    content_top, content_bottom = drawn[0] + top, drawn[-1] + top
    shift_rows = (top + bottom) / 2 - (content_top + content_bottom) / 2
    ax.set_position([slot.x0, slot.y0 - shift_rows / height, slot.width, slot.height])
    from matplotlib.transforms import Bbox
    return Bbox([[slot.x0, 1 - (content_bottom + shift_rows) / height],
                 [slot.x1, 1 - (content_top + shift_rows) / height]])


def segments(ax, points, frames, states, three_d=False):
    for i in range(len(points) - 1):
        if frames[i + 1] != frames[i] + 1 or not np.isfinite(points[i:i + 2]).all():
            continue
        q = points[i:i + 2]
        color = COLORS[states[i]]
        if three_d:
            ax.plot(q[:, 0], q[:, 2], q[:, 1], color=color, lw=1.1)
        else:
            ax.plot(q[:, 0], q[:, 1], color=color, lw=1.1)


def draw(output, wrist, marker, frames, states, reference, rail, rail_mask, task_first=None):
    """task_first: the first frame of the task (the carry after the parked
    span, eval/reports/r6b_waypoints.json track_turns, read through
    ch7_trail_data.load when not given); panel (a) of the wrist figure
    shows the frames from there on, so the startup excursion of frames
    0-25 does not set its scale, while panel (b) keeps every frame."""
    if task_first is None:
        task_first = load()["phases"][0]["first"]
    # Values arrive in metres, as in the original builder. Only units change.
    wrist, marker, reference, rail = [p * 100 for p in (wrist, marker, reference, rail)]
    handles = [Line2D([], [], color="0.2", ls="--", label="Waypoint reference"),
               Line2D([], [], color="tab:blue", label="Wrist: measured input"),
               Line2D([], [], color="tab:orange", label="Wrist: rebuilt")]
    fig = plt.figure(figsize=(9, 6.2), layout="constrained")
    grid = fig.add_gridspec(3, 2, width_ratios=[1.3, 1], wspace=0.3)
    ax = fig.add_subplot(grid[:, 0], projection="3d")
    ax.plot(reference[:, 0], reference[:, 2], reference[:, 1], "--", color="0.2", lw=1)
    task = frames >= task_first
    segments(ax, wrist[task], frames[task], states[task], three_d=True)
    ax.set(xlabel="x (cm)", ylabel="z (cm)", zlabel="height y (cm)")
    ax.tick_params(labelsize=10)
    ax.set_title(f"(a) Model wrist over the task, frames {task_first}-{frames.max()}", fontsize=12)
    all_points = np.vstack([wrist[task], reference])
    span = np.ptp(all_points[np.isfinite(all_points).all(axis=1)], axis=0)
    ax.set_box_aspect(span[[0, 2, 1]], zoom=1.12)
    ax.zaxis.set_major_locator(MaxNLocator(nbins=2))
    ax.view_init(elev=24, azim=-58)
    for name, point in zip(("Start", "W1", "W2", "W3"), reference):
        ax.scatter(point[0], point[2], point[1], color="0.2", s=14)
        ax.text(point[0], point[2], point[1], name, fontsize=10)
    for j, axis_name in enumerate(("x", "y", "z")):
        a = fig.add_subplot(grid[j, 1])
        a.plot(frames, wrist[:, j], color="tab:blue", lw=0.8)
        for first, last in intervals(frames, states == "recovered"):
            a.axvspan(first, last, color="tab:orange", alpha=0.16, lw=0)
        a.set_ylabel(f"{axis_name} (cm)", fontsize=12)
        a.tick_params(labelsize=11)
        a.grid(alpha=0.2)
        a.set_xlim(frames.min(), frames.max())
        if j == 0:
            a.set_title("(b) Wrist coordinates, every frame; shading marks recovery", fontsize=12)
        if j == 2:
            a.set_xlabel("Recorded frame", fontsize=12)
        else:
            a.tick_params(labelbottom=False)
    fig.legend(handles=handles, loc="outside lower center", ncol=3, fontsize=11, frameon=False)
    settle_3d(fig, ax)
    fig.savefig(output / "ch7_fig_wrist_traj.png", dpi=200, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    trim(output / "ch7_fig_wrist_traj.png")

    # The identical quantitative sample set used by the existing rail evaluation.
    # Excluded frames become NaNs so no line bridges an omitted sample.
    w = wrist.copy(); w[~rail_mask] = np.nan
    m = marker.copy(); m[~rail_mask] = np.nan
    # Panel heights follow the data spans: with equal aspect adjusted on the
    # box, each panel's width is then height * xspan / yspan, the same for
    # both, so the two panels stay equally wide under the shared x axis and
    # nothing is cut (the box mode never changes the data limits).
    spans = [np.nanmax(np.vstack([w[:, d], m[:, d]])) - np.nanmin(np.vstack([w[:, d], m[:, d]])) for d in (2, 1)]
    fig, axes = plt.subplots(2, 1, figsize=(8.8, 5.6), layout="constrained", sharex=True,
                             gridspec_kw={"height_ratios": spans})
    for ax, dimension, title in zip(axes, (2, 1), ("(a) Slide from above", "(b) Slide from the side")):
        ax.plot(rail[:, 0], rail[:, dimension], color="0.2", ls="--", lw=1)
        ax.plot(m[:, 0], m[:, dimension], color="tab:green", lw=1)
        segments(ax, w[:, [0, dimension]], frames, states)
        ax.set_title(title, loc="left", fontsize=12)
        ax.set_ylabel(("z" if dimension == 2 else "y") + " (cm)", fontsize=12)
        ax.tick_params(labelsize=11)
        if dimension == 1:
            ax.set_xlabel("x (cm)", fontsize=12)  # the x axis is shared; label it once
        ax.set_aspect("equal", adjustable="box")
        ax.grid(alpha=0.2)
    handles = [Line2D([], [], color="0.2", ls="--", label="Fitted rail line"),
               Line2D([], [], color="tab:green", label="Marker origin"),
               Line2D([], [], color="tab:blue", label="Wrist: measured input"),
               Line2D([], [], color="tab:orange", label="Wrist: rebuilt")]
    fig.legend(handles=handles, loc="outside lower center", ncol=2, fontsize=11, frameon=False)
    fig.savefig(output / "ch7_fig_combined.png", dpi=200, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
