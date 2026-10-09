STATUS: COMPLETE

GOAL:
Replace Figure 3.4 with the author-requested illustrative torso schematic.

KEY FINDING:
The new two-panel image shows the input vectors and root frame at L24
without suggesting that photographic hip detections were corrected.

VERIFIED:
The final PNG was visually inspected. The figure-only Chapter 3 build
preserved all 128 OMML expressions byte-for-byte and passed check_style
with zero hits. Its new PNG was embedded byte-for-byte.

ASSUMPTIONS/UNRESOLVED:
Page layout of the assembled thesis remains an integration check. The
Figure 3.4 image paragraph keeps with its caption. Illustration coordinates
are layout choices under D-080, not anatomical measurements.

DECISION:
Use a front view with the subject's right on the viewer's left and retain
the root frame identity established in Section 3.2.

NEXT:
Integrate the figure and continue the separately authorized D-083 equation
corrections. ch3_schematic_verification.json pins the figure-only stage
before those equation corrections.

Reason:
The requested image demonstrates a construction. A diagram can show its
origins and axis directions directly without modifying captured data.

Evidence:
- Panel (a): L24 right hip and L12 right shoulder on the viewer's left;
  L23 left hip on the viewer's right; red vector L23 -> L24 and yellow
  vector s = L12 - L24.
- Panel (b): all axes originate at L24; x points viewer-left, y up the
  trunk, and z toward the viewer, drawn as a dot in a circle with a legend.
- The generator loads no photograph, depth track or landmark measurement.
- The builder changes the image route/caption and two prose references.
  Frame 533 now points to Figure 3.3, while Figure 3.4 is called schematic.
- ch3_schematic_verification.json records source, asset and chapter hashes
  together with the unchanged-mathematics comparison to e69dfa6.

Therefore:
The replacement supplies the requested explanation while preserving
experimental values and the mathematical identity of the torso frame.

Reproduce, from the repository root:

    MPLCONFIGDIR=/tmp/ch3_torso_matplotlib /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/make_ch3_torso_schematic_fig.py
    MPLCONFIGDIR=/tmp/ch3_torso_matplotlib /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/build_ch3.py
    /home/luo/anaconda3/bin/python writing/v8/condensed/scripts/check_style.py Chapter_3_Kinematic_Modeling

The final correctness audit changes some Chapter 3 formulas afterward;
the 128-expression equality is explicitly a figure-stage result, not a
claim that those later corrections preserve every original expression.
No assembly, PDF generation or Git operations were performed by this worker.
