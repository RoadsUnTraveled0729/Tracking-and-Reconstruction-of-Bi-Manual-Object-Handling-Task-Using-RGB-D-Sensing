# Chapter 7 supporting visual restoration

This package records five image groups in `writing/v8/condensed/figures/`,
ready for the Chapter 7 builder. The recommended section, insertion point, and
exact caption for every group are in `supporting_manifest.json`. The package
does not change Chapter 7 text, numbering, metrics, or existing figures.

The rail and handover strips restore the earlier four-frame task selections at
an aspect ratio suitable for a 6.1 inch-wide figure. Every header uses two
lines in a fixed 50 pixel font: the short phase name followed by the frame
number. At 6.1 inches wide this is approximately 8.46 points, and each strip is
approximately 1.396 inches tall. The rail wording uses "object acquisition" in
place of the older "grasp" label. The source-frame pixels are pasted without
resizing, cropping, or an overlaid border.

`ch7_failure_context.png` uses four real colour frames from
the retained natural-failure set, including the left-wrist observation gap at
frame 1462. It should appear in Section 7.4.2 and must not be presented as the
synthetic masking experiment of Section 7.4.1.

`ch7_natural_proxy_left.png` and
`ch7_natural_proxy_right.png` are the existing pinned natural-occlusion
diagnostics, copied without alteration for placement in Section 7.4.2.

Rebuild command:

    /home/luo/anaconda3/bin/python writing/v8/condensed/audit_evidence/ch7_visual_restoration/supporting_compose.py

The manifest records SHA256 hashes for every source and output. The diagnostic
copies retain the source hash exactly.
