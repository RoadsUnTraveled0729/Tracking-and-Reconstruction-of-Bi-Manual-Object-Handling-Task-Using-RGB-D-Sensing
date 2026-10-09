# A1. Pipeline A — acquisition and landmark filtering

From a RealSense `.bag` recording to a clean per-frame 3-D landmark
time series. Stages: (1) depth-registered landmark measurement,
(2) validity gating that converts *wrong* data into *missing* data,
(3) an offline glitch filter that repairs what can be repaired honestly.
The raw measurement CSV is never modified — the filter writes a separate
file, so the strict baseline remains available for every later
comparison.

Implementation: `mediapipe/extract_landmarks_to_csv.py`,
`mediapipe/filter_landmarks.py`.

## 1. Sensor model and deprojection

Each frame provides a color image and a depth image aligned into the
color camera's geometry. The color camera is modeled as a pinhole with
intrinsics $f_x, f_y$ (focal lengths, px) and $c_x, c_y$ (principal
point, px), plus lens distortion; librealsense's deprojection inverts
the full model. For the ideal pinhole part, a pixel $(u,v)$ with depth
$z$ (meters, along the optical axis) maps to the camera-frame point

$$
p_\mathcal{C} \;=\; z
\begin{bmatrix}
(u - c_x)/f_x \\
(v - c_y)/f_y \\
1
\end{bmatrix}
\;=\; z\,K^{-1}\begin{bmatrix}u\\v\\1\end{bmatrix},
\qquad
K = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1\end{bmatrix}.
$$

Consequence used repeatedly later: **lateral position error scales with
$z$** — one pixel of image error at range $z$ is $\approx z/f_x$ meters
($\approx 1.6$ mm/px at $z=1$ m for these intrinsics), and stereo depth
error itself grows as $z^2$ (D1 §4). The intrinsics are recorded in the
extractor's `.meta.json` for downstream stages.

### 1.1 Depth sampling: 5×5 nonzero median

Depth at a single pixel (`get_distance(u,v)`) fails two ways: the pixel
can be a **hole** (0 return: occluder edges, dark or specular surfaces)
and it can carry single-pixel speckle noise. The extractor instead takes
the **median of the nonzero depths in a 5×5 window** centered on the
landmark pixel:

$$
z(u,v) = \mathrm{median}\{\, D(u', v') \neq 0 \;:\; |u'-u|\le 2,\ |v'-v|\le 2 \,\}.
$$

The median is robust to up to half the window being outliers, and
restricting to nonzero returns treats holes as absent samples rather
than zeros. Measured regression on a full recording: valid landmarks
move a **median 0.00 mm** (p99 ≤ 7.5 mm, within depth noise) while
landmarks previously lost to single-pixel holes are recovered — strictly
better than the single-pixel read. A window with **no** nonzero return
still yields "no depth" (an honest gap, handled below).

## 2. Landmark measurement and validity gating

MediaPipe `PoseLandmarker` (heavy model, VIDEO mode) runs on each color
frame and returns image coordinates plus a per-landmark `visibility`
score $v_i \in [0,1]$. Two technical constraints:

- VIDEO mode requires strictly increasing integer-millisecond
  timestamps; bag playback timestamps can repeat or jitter, so each
  timestamp is clamped to $\max(t_{prev}+1,\ t)$ ms.
- Only the 8 upper-body landmarks of §0.3 are exported.

**The critical property: MediaPipe always outputs coordinates for all
landmarks, occluded or not.** An occluded wrist still gets a
(hallucinated) position; the visibility score is the *only* signal that
the position is a guess. Concrete evidence: on the evaluation recording,
frames 0–9 carry left elbow/wrist positions up to ~2 m from plausible
while visibility ramps 0.001 → 0.5 (model warm-up).

The extractor therefore **gates on visibility**:

$$
v_i < v_{min} = 0.5 \;\Rightarrow\; \text{landmark } i \text{ is written as empty cells,}
$$

and likewise when the 5×5 depth window is empty. Every landmark carries
a provenance column `_src` ∈ {0 ok, 1 low-visibility, 2 no-depth}, and
every frame gets a CSV row regardless (frame indexing stays aligned
across all pipeline stages). This is the design rule that recurs through
the whole system: **convert "wrong" into "missing," then handle
"missing" explicitly** (A3).

The 2-D landmark pixel and the median depth are then deprojected (§1)
to give $p_{\mathcal{C},i}(t)$ in meters.

## 3. The glitch filter

`filter_landmarks.py` reads the raw CSV and writes
`*_landmarks_filtered.csv`. Three steps per landmark, in order. Each
sample keeps a provenance flag (0 raw kept, 1 glitch-interpolated,
2 missing-interpolated, 3 left missing) so the filtered file remains
auditable.

### 3.1 Despike — Hampel identifier

Over a centered rolling window (11 frames), let $m_i$ be the per-axis
rolling median and $\mathrm{MAD}_i = \mathrm{median}\,|x_j - m_i|$ the
median absolute deviation within the window. Sample $x_i$ is a glitch
when, on **any** axis,

$$
|x_i - m_i| \;>\; \max\bigl(a_0,\; k \cdot 1.4826 \cdot \mathrm{MAD}_i\bigr),
\qquad a_0 = 0.02\ \text{m},\ k = 3.
$$

The factor $1.4826$ makes the MAD a consistent estimator of the standard
deviation for Gaussian noise ($1/\Phi^{-1}(3/4)$), so the rule is the
robust analogue of a $3\sigma$ test. Because $\mathrm{MAD}_i$ is
computed *locally*, the threshold self-adapts: during fast genuine
motion the local deviations are large, the threshold rises, and real
motion is not flagged — only isolated departures from the local
trajectory are. The absolute floor $a_0$ prevents flagging noise-level
wiggle when the limb is at rest ($\mathrm{MAD}\to 0$). Flagged samples
are invalidated (set to NaN), joining the missing data.

### 3.2 Gap fill — interior interpolation + edge backfill

NaN runs are repaired by two distinct rules, matching two distinct
physical situations:

- **Interior runs** (valid data on both sides) of length ≤ `--max-gap`
  (5 frames ≈ 167 ms): linear interpolation *over time* between the
  bounding valid samples,
  $x(t) = x(t_a) + \frac{t-t_a}{t_b-t_a}\,\bigl(x(t_b)-x(t_a)\bigr)$.
  Both endpoints are known, so the interpolant is an honest bound on a
  short occlusion. Longer runs stay NaN — inventing 3-D positions
  across long gaps is the occlusion stage's job (A3), in angle space,
  not here in point space.
- **Edge runs** (leading/trailing, one-sided) of length ≤ `--edge-fill`
  (12 frames used): constant **backfill** with the nearest valid
  sample. There is nothing to interpolate toward at a recording
  boundary; without this, the warm-up gap of §2 left the solver holding
  the rest pose and then **snapping** to the first live pose — a 60.3°
  single-frame angle step in the streamed output, reduced to 11.8°
  (the true inter-frame motion) by the backfill.

### 3.3 Smooth — zero-phase Butterworth low-pass

Human upper-body motion lives below ~5 Hz; depth-derived landmark noise
is broadband. A low-pass with cutoff $f_c = 3$ Hz, order $n = 4$,
removes the noise band. The Butterworth magnitude response is maximally
flat in the passband:

$$
|H(\omega)|^2 = \frac{1}{1 + (\omega/\omega_c)^{2n}}.
$$

Causal filtering would delay the signal (group delay ≈ tens of ms —
a real spatial lag at limb speeds); since this stage is offline, the
filter is applied **forward and backward** (`filtfilt`). The composite
response is $|H(\omega)|^2$ — squared magnitude, **exactly zero phase**:
peaks stay where they happened. This is the standard biomechanics
practice, and it is only valid offline (a real-time variant must accept
a causal filter and its lag).

Applied per contiguous valid segment, per axis. Alternatives measured
(shake = mean RMS frame-to-frame displacement; fidelity = deviation
from despiked raw during fast wrist motion):

| method | shake (mm) | fast-motion deviation (mm) |
|---|---:|---:|
| raw | 10.2 | — |
| Savitzky–Golay 9/2 | 2.8 | 4.8 |
| rolling median 9 | 2.9 | 3.9 |
| **Butterworth 3 Hz (chosen)** | **1.9** | **4.8** |
| Butterworth 2 Hz | 1.5 | 5.3 |
| One-Euro (causal) | 1.1 | 28.4 (lag) |

Butterworth at 3 Hz gives ~5× less shake than raw at the same motion
fidelity as SavGol; One-Euro's 28 mm deviation is pure causal lag
(it remains the real-time candidate for the online variant, and is
excluded here for exactly that lag).

## 4. What the filter is *not allowed* to do

The stage's honesty contract, enforced downstream:

1. The raw CSV is untouched; every quantitative claim can be re-run on
   raw data.
2. Interpolated and backfilled samples are flagged; consumers can (and
   do) distinguish measured from repaired samples.
3. Smoothing must not invent geometry — the analogous object-track
   filter in Pipeline B is asserted to move measured frames by less
   than raw PnP jitter (B1 §8); the landmark filter's motion-fidelity
   column above plays the same role.

## 5. Reproduce

```bash
cd mediapipe
python extract_landmarks_to_csv.py --bag ../Video/recording_20260224_083945.bag
python filter_landmarks.py \
    --csv output/recording_20260224_083945_landmarks_raw_v2.csv \
    --out output/recording_20260224_083945_landmarks_filtered_v2.csv \
    --edge-fill 12 --plot
```

Numbers quoted here: `mediapipe/README.md` (filter comparison table,
performance), the filter's `.meta.json` per-landmark stats, and
`OBJECT_OFFSET.md` §0 (the 60.3° → 11.8° edge-fill result).
