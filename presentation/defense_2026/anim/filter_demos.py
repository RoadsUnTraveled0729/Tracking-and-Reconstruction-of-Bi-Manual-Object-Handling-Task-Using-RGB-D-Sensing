#!/usr/bin/env python3
"""Readable filter demonstrations on pinned, recorded right-wrist samples.

Frozen V1 helper functions are imported read-only. Candidate smoothers are
applied to complete raw valid runs, then cropped for display; these are not
new accuracy results or a rerun of the complete despike/gap/smooth pipeline.
The passing cursors and 36-second pacing are explanatory, not runtime timing.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pandas as pd
from scipy.signal import butter, lfilter, lfilter_zi
from PIL import Image, ImageDraw

import teaching_flow as drawing

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
BRIEF = json.loads((ROOT/"FILTER_DEMO_BRIEF.json").read_text())
DURATION = 36
PLOT = (340, 335, 1330, 830)
RAW, RESULT, FOCUS = "#657486", "#087F83", "#A7680C"
PALE = "#FCF4E6"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_data():
    csv_path, implementation = REPO/BRIEF["source_csv"], REPO/BRIEF["implementation"]
    assert digest(csv_path) == BRIEF["source_sha256"]
    assert digest(implementation) == BRIEF["implementation_sha256"]
    spec = importlib.util.spec_from_file_location("frozen_filter_demo_source", implementation)
    frozen = importlib.util.module_from_spec(spec); spec.loader.exec_module(frozen)
    data = pd.read_csv(csv_path)
    frames = data["frame"].to_numpy(int); times = data["time_s"].to_numpy(float)
    assert np.array_equal(frames, np.arange(len(frames)))
    pos = data[[f"right_wrist_{axis}" for axis in "xyz"]].to_numpy(float)
    fs = 1.0/float(np.median(np.diff(times)))
    args = SimpleNamespace(**BRIEF["parameters"])
    outputs = {method: frozen.smooth_landmark(pos, method, fs, args)
               for method in ("butter", "oneeuro", "savgol", "median")}
    mask = frozen.hampel_mask(pos, args.hampel_window, args.hampel_k, args.hampel_floor)
    stripped = pos.copy(); stripped[mask] = np.nan
    filled, filled_mask = frozen.fill_gaps(pos, times, args.max_gap, args.edge_fill)

    # Reproduce the actual forward and backward passes of scipy.filtfilt's
    # default odd padding and steady-state initialization, then verify output.
    b, a = butter(args.butter_order, args.cutoff_hz, fs=fs)
    edge = 3*max(len(a), len(b)); zi = lfilter_zi(b, a)
    forward = pos.copy(); backward = pos.copy()
    valid_runs = frozen.nan_runs(np.isfinite(pos).all(axis=1))
    for start, stop in valid_runs:
        if stop-start <= edge: continue
        for axis in range(3):
            x = pos[start:stop, axis]
            extended = np.concatenate([2*x[0]-x[edge:0:-1], x,
                                       2*x[-1]-x[-2:-edge-2:-1]])
            first, _ = lfilter(b, a, extended, zi=zi*extended[0])
            reverse, _ = lfilter(b, a, first[::-1], zi=zi*first[-1])
            forward[start:stop, axis] = first[edge:-edge]
            backward[start:stop, axis] = reverse[::-1][edge:-edge]
    butter_error = float(np.nanmax(np.abs(backward-outputs["butter"])))
    assert butter_error < 1e-12

    med = pd.DataFrame(pos).rolling(7, center=True, min_periods=3).median()
    resid = (pd.DataFrame(pos)-med).abs()
    mad = resid.rolling(7, center=True, min_periods=3).median()
    threshold = np.maximum(args.hampel_floor, args.hampel_k*1.4826*mad.to_numpy())
    focus = 36
    assert mask[focus] and np.array_equal(np.flatnonzero(mask), [36, 537, 760])
    assert np.isnan(pos[681:685]).all() and filled_mask[681:685].all()
    expected_gap = np.column_stack([np.interp(times[681:685], times[[680, 685]], pos[[680, 685], ax])
                                     for ax in range(3)])
    assert np.max(np.abs(expected_gap-filled[681:685])) < 1e-12
    quadratic = np.polyfit(np.arange(-4, 5), pos[32:41, 2], 2)
    sg_error = abs(float(np.polyval(quadratic, 0)-outputs["savgol"][36, 2]))
    median_error = abs(float(np.median(pos[32:41, 2])-outputs["median"][36, 2]))
    assert sg_error < 1e-12 and median_error < 1e-12
    # Prefix invariance checks that the One-Euro output uses no future input.
    prefix = frozen.smooth_landmark(pos[:101], "oneeuro", fs, args)
    causal_error = float(np.nanmax(np.abs(prefix-outputs["oneeuro"][:101])))
    assert causal_error == 0
    checks = {"status": "PASS", "scope": "Numerical replay of frozen operations, not an accuracy experiment",
              "source_csv_sha256": digest(csv_path), "implementation_sha256": digest(implementation),
              "saved_metadata_sha256": digest(REPO/BRIEF["source_metadata"]),
              "sampling_rate_hz_from_median_time_difference": fs,
              "valid_runs_half_open": [[int(a), int(b)] for a, b in valid_runs],
              "hampel_flagged_source_frames": np.flatnonzero(mask).tolist(),
              "hampel_frame_36_depth_m": float(pos[36, 2]),
              "hampel_frame_36_local_depth_median_m": float(med.iloc[36, 2]),
              "hampel_frame_36_depth_residual_m": float(resid.iloc[36, 2]),
              "hampel_frame_36_depth_threshold_m": float(threshold[36, 2]),
              "hampel_scale": "Exact two rolling-median implementation, not a substituted MAD formula",
              "gap_source_frames": [681, 682, 683, 684], "gap_valid_endpoints": [680, 685],
              "gap_interpolation_max_error_m": float(np.max(np.abs(expected_gap-filled[681:685]))),
              "butterworth_backward_vs_frozen_max_error_m": butter_error,
              "savgol_quadratic_center_vs_frozen_error_m": sg_error,
              "median_window_vs_frozen_error_m": median_error,
              "one_euro_prefix_invariance_max_error_m": causal_error,
              "one_euro_parameters": {"min_cutoff_hz": .05, "beta": 1.0},
              "display_window_history": "Smoother window beginning at frame28 has prior valid-run samples25-27",
              "parameters": BRIEF["parameters"]}
    return {"frames": frames, "times": times, "pos": pos, "outputs": outputs,
            "hampel": stripped, "hampel_mask": mask, "median": med.to_numpy(),
            "gap": filled, "gap_mask": filled_mask, "forward": forward,
            "quadratic": quadratic, "checks": checks}


DATA = load_data()


class Plot:
    def __init__(self, spec):
        self.spec = spec; self.name = spec["name"]; self.axis = "xyz".index(spec["axis"])
        self.lo, self.hi = spec["frames_inclusive"]
        self.x = np.arange(self.lo, self.hi+1)
        self.raw = DATA["pos"][self.lo:self.hi+1, self.axis]
        if self.name == "filter_hampel": self.out = DATA["hampel"][self.lo:self.hi+1, self.axis]
        elif self.name == "filter_gap": self.out = DATA["gap"][self.lo:self.hi+1, self.axis]
        else: self.out = DATA["outputs"][spec["method"]][self.lo:self.hi+1, self.axis]
        low = min(float(np.nanmin(self.raw)), float(np.nanmin(self.out)))
        high = max(float(np.nanmax(self.raw)), float(np.nanmax(self.out)))
        margin = (high-low)*.13
        self.ymin, self.ymax = low-margin, high+margin
        self.short = len(self.x) <= 30

    def xy(self, x, y):
        a, b, c, d = PLOT
        return a+(np.asarray(x)-self.lo)/(self.hi-self.lo)*(c-a), d-(np.asarray(y)-self.ymin)/(self.ymax-self.ymin)*(d-b)

    def path(self, d, x, y, color, width=9, dots=False):
        x, y = np.asarray(x), np.asarray(y)
        ok = np.isfinite(y); changes = np.flatnonzero(np.diff(np.r_[False, ok, False]))
        for start, stop in zip(changes[::2], changes[1::2]):
            xp, yp = self.xy(x[start:stop], y[start:stop])
            pts = list(zip(xp, yp))
            if len(pts) > 1: d.line(pts, fill=color, width=width, joint="curve")
            if dots or len(pts) == 1:
                for px, py in pts: d.ellipse((px-11, py-11, px+11, py+11), fill=color)

    def mark(self, d, frame, y, color=FOCUS, radius=24):
        x, y = self.xy(frame, y)
        d.ellipse((x-radius, y-radius, x+radius, y+radius), fill=drawing.BG, outline=color, width=7)

    def window(self, d, left, right):
        x0, _ = self.xy(left, self.ymin); x1, _ = self.xy(right, self.ymin)
        d.rectangle((x0, PLOT[1], x1, PLOT[3]), fill=PALE)

    def axes(self, d):
        left, top, right, bottom = PLOT
        for value in np.linspace(self.ymin, self.ymax, 3):
            _, y = self.xy(self.lo, value)
            d.line((left, y, right, y), fill="#E0E5EA", width=3)
            label = f"{value:.3f}" if self.spec["axis"] == "x" else f"{value:.2f}"
            drawing.text(d, (5, y-53, 300, y+53), label, 84, drawing.MUTED)
        d.line((left, top, left, bottom, right, bottom), fill=drawing.INK, width=5)
        for value in [self.lo, (self.lo+self.hi)//2, self.hi]:
            x, _ = self.xy(value, self.ymin)
            d.line((x, bottom, x, bottom+15), fill=drawing.INK, width=4)
            drawing.text(d, (x-109, 855, x+109, 951), str(value), 84, drawing.MUTED)
        drawing.text(d, (360, 965, 1300, 1067), "Frame", 90, drawing.INK)

    def header(self, d, title, phase, output_label="Output", show_output=True):
        drawing.text(d, (55, 28, 1130, 143), title, 90, drawing.INK, True, align="left")
        drawing.text(d, (1180, 28, 1400, 143), f"{phase} / 4", 84, drawing.MUTED)
        drawing.text(d, (25, 186, 445, 286), self.spec["axis"]+" (m)", 84, drawing.MUTED)
        d.line((500, 236, 570, 236), fill=RAW, width=9)
        drawing.text(d, (595, 186, 865, 286), "Input", 84, RAW)
        if show_output:
            d.line((910, 236, 970, 236), fill=RESULT, width=9)
            drawing.text(d, (995, 186, 1410, 286), output_label, 84, RESULT)

    def __call__(self, t):
        drawing.TEXT.clear(); drawing.OBSCURERS.clear()
        im = Image.new("RGB", (drawing.W, drawing.H), drawing.BG); d = ImageDraw.Draw(im)
        phase = 1 if t < 6 else 2 if t < 14 else 3 if t < 28 else 4
        name = self.name; title = "Recorded input"; show_output = phase >= 3; out_label = "Output"
        if name == "filter_hampel":
            title = ["Recorded input", "7-frame window", "Flag the spike", "Leave a gap"][phase-1]
            show_output = False
            if phase in (2, 3): self.window(d, 33, 39)
        elif name == "filter_gap":
            title = ["Missing samples", "Two endpoints", "Interpolate", "Modelled values"][phase-1]
            out_label = "Filled"
            if phase in (2, 3): self.window(d, 680, 685)
        elif name == "filter_butterworth":
            title = ["Recorded input", "Forward pass", "Backward pass", "Smoothed result"][phase-1]
            show_output = phase >= 2
        elif name == "filter_one_euro":
            title = ["Received samples", "Causal update", "Received history", "Input and output"][phase-1]
            show_output = True
        elif name == "filter_savgol":
            title = ["Recorded input", "9-frame window", "Quadratic fit", "Smoothed result"][phase-1]
            if phase in (2, 3): self.window(d, 32, 40)
            if phase == 3: out_label = "Fit"
        elif name == "filter_median":
            title = ["Recorded input", "9-frame window", "Window median", "Median result"][phase-1]
            if phase in (2, 3): self.window(d, 32, 40)
            if phase == 3: out_label = "Median"
        self.axes(d); self.header(d, title, phase, out_label, show_output)

        if name == "filter_hampel":
            values = self.out if phase == 4 else self.raw
            self.path(d, self.x, values, RAW, dots=True)
            if phase == 3: self.mark(d, 36, DATA["pos"][36, self.axis])
        elif name == "filter_gap":
            self.path(d, self.x, self.raw, RAW, dots=True)
            if phase >= 2:
                for sample in (680, 685): self.mark(d, sample, DATA["pos"][sample, self.axis])
            if phase >= 3:
                progress = 1 if phase == 4 else drawing.smooth((t-18)/6)
                stop = 681+int(progress*4)
                x = np.arange(680, stop+1)
                self.path(d, x, DATA["gap"][x, self.axis], RESULT, dots=False)
                for sample in range(681, min(stop, 684)+1):
                    self.mark(d, sample, DATA["gap"][sample, self.axis], RESULT, 16)
        elif name == "filter_butterworth":
            self.path(d, self.x, self.raw, RAW, width=6)
            if phase == 2:
                u = drawing.smooth((t-6)/4); count = max(1, int(1+u*(len(self.x)-1)))
                self.path(d, self.x[:count], DATA["forward"][self.lo:self.lo+count, self.axis], RESULT)
                x, _ = self.xy(self.x[count-1], self.ymin)
                d.line((x, PLOT[1], x, PLOT[3]), fill=FOCUS, width=5)
            elif phase >= 3:
                u = 1 if phase == 4 else drawing.smooth((t-18)/6)
                first = int((1-u)*(len(self.x)-1))
                self.path(d, self.x[first:], self.out[first:], RESULT)
                if phase == 3:
                    x, _ = self.xy(self.x[first], self.ymin)
                    d.line((x, PLOT[1], x, PLOT[3]), fill=FOCUS, width=5)
        elif name == "filter_one_euro":
            u = 0 if t < 6 else 1 if t >= 24 else (t-6)/18
            count = max(1, int(1+u*(len(self.x)-1)))
            self.path(d, self.x[:count], self.raw[:count], RAW, width=6)
            self.path(d, self.x[:count], self.out[:count], RESULT)
            if phase < 4:
                x, _ = self.xy(self.x[count-1], self.ymin)
                d.line((x, PLOT[1], x, PLOT[3]), fill=FOCUS, width=5)
        elif name == "filter_savgol":
            self.path(d, self.x, self.raw, RAW, width=6, dots=self.short)
            if phase == 3:
                xs = np.linspace(32, 40, 121)
                self.path(d, xs, np.polyval(DATA["quadratic"], xs-36), RESULT)
                self.mark(d, 36, DATA["outputs"]["savgol"][36, self.axis], RESULT)
            elif phase == 4: self.path(d, self.x, self.out, RESULT)
        elif name == "filter_median":
            self.path(d, self.x, self.raw, RAW, width=6, dots=self.short)
            if phase == 3:
                value = DATA["outputs"]["median"][36, self.axis]
                self.path(d, [32, 40], [value, value], RESULT)
                self.mark(d, 36, value, RESULT)
            elif phase == 4: self.path(d, self.x, self.out, RESULT)
        return drawing.finish(im)


def main(preview_only=False, only=None):
    reports = []
    for spec in BRIEF["assets"]:
        if only and spec["name"] != only: continue
        plot = Plot(spec)
        report = drawing.export_asset(spec["name"], plot, DURATION, preview_only,
            {"sources": [BRIEF["source_csv"], BRIEF["source_metadata"], BRIEF["implementation"]],
             "source_csv_sha256": BRIEF["source_sha256"],
             "implementation_sha256": BRIEF["implementation_sha256"],
             "filter_generator_sha256": digest(__file__), "display": spec,
             "render_dimensions_override": "1440x1080 panel; supersedes initial1920wide brief",
             "trace_scope": "Saved input with isolated source-function replay; not independent accuracy",
             "numerical_checks": DATA["checks"]})
        reports.append(report)
    combined_path = drawing.REVIEW/"FILTER_DEMO_CHECK.json"
    existing = json.loads(combined_path.read_text()) if only and combined_path.exists() else {}
    assets = {r["name"]: r for r in existing.get("assets", [])}
    assets.update({r["name"]: r for r in reports})
    combined = {"status": "PREVIEW" if preview_only else "PASS", "numerical": DATA["checks"],
                "assets": list(assets.values()), "filter_generator_sha256": digest(__file__),
                "timing": "All36second editorial loops; final8seconds held; not pipeline latency",
                "pairing": "Camera clips use wider contiguous context from the same recording; exact plot crops are listed separately, and playback is not synchronized."}
    combined_path.write_text(json.dumps(combined, indent=2)+"\n")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--preview-only", action="store_true")
    ap.add_argument("--asset", choices=[s["name"] for s in BRIEF["assets"]]); args = ap.parse_args()
    main(args.preview_only, args.asset)
