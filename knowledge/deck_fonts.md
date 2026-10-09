# Defence deck fonts

## Final deck (Verified 2026-10-08)

Source: presentation/defense_2026/Thesis_Defence_2026.pptx read with python-pptx on
2026-10-08 (explicit run sizes of every text-frame run on slides 1-46; sizes
inherited from the theme were not read, shapes inside groups and table cells
were not visited).
All inspected runs explicitly set DejaVu Sans (17,856 characters, no other
font name); none lacks an explicit size. Explicit sizes by character count:

| Size | Characters |
|---:|---:|
| 10.5 pt | 4,625 |
| 11 pt | 14 |
| 14 pt | 264 |
| 16 pt | 9,646 |
| 22 pt | 2,000 |
| 28 pt | 1,289 |
| 60 pt | 18 |

The retired validator (validate_deck.py FONT_ROLES) and report_effective_text.py
were deleted in 3dbd345 (D-382); the placement of each role on the final slides and
the effective size of baked text in the final media were not re-measured.

## RETIRED (history): font roles of the generated build-77 deck

The role table, the page-2 and page-41 variant roles (24/18/17 pt and the grey
shades), the effective-size table and the commands below describe the generated
decks and the retired builder (recover at 85078c9). They are kept as record and are
not checked against the final deck.


Verified: 2026-10-01 (build 77, master 88878cd): the variant roles section
below is new, and the effective-text table was re-read against
review/EFFECTIVE_TEXT.md of build 77 (80 rows): unchanged at build 77 (same
pages, files and sizes as the build-71 table; every page number below is
still correct). Earlier: 2026-09-30 (build 71, commit 5424e14 plus D-321; build
66, HEAD aed90fe, D-294).
Re-checked 2026-09-30 for build 67: no size in the table changed (the
overlay labels, including the new Wall label on page 18, are still one size,
em 57 px = 17.1 pt, per figures/coordinate_frames/overlay/manifest.json
label_size; the References rows on pages 43-44 are native 16 pt table text).
Sources: presentation/defense_2026/{validate_deck.py (FONT_ROLES,
native_typography), build_deck.py (RESTRAINED sizes, DERIVATION),
report_effective_text.py, effective_text_table.json,
review/EFFECTIVE_TEXT.md}, DECISIONS.md D-129, D-245, D-247, D-259, D-264,
D-269, D-271, D-280, D-281, D-285.
Answers: the native font sizes of the deck and the placement each allows,
the size of text baked into images on the slide, the accepted exceptions
and the command that regenerates the report.

## Native text roles (validate_deck.py FONT_ROLES)

| Size | Role | Allowed placement |
|---:|---|---|
| 60 pt | closing word | kinds closing and thanks (pages 47-48), the title text (D-247, D-267) |
| 28 pt | title | title band; dividers and cover |
| 22 pt | explanation | left column (bullets); divider chapter label; outline and full-width kinds |
| 16 pt | visual | right column (captions, tables, labels); full-width captions (D-129); derivation lead lines across the content band 0.50-12.83 x 1.20-6.80 in (D-281); the page-41 caption under the bullets, one line at x 0.82-5.85 in below the last bullet box (D-269) |
| 11 pt | cover label | cover only |
| 10.5 pt | source/navigation | footer source label and page number |

No run is bold (validate_deck.py forbids bold).

## Variant roles admitted only on the two author layouts (build 77; D-345, D-350, D-355)

Sources: presentation/defense_2026/validate_deck.py (VARIANT_FONT_ROLES line
728, VARIANT_COLOURS 729, PAIRS_TITLE_REGION 733, PAIRS_FOOTER_REGION 734,
outline_pairs_variant 840, font_role_admitted 845, palette_admitted 857, role
geometry in native_typography about lines 1275-1310), talk_content.json pages 2
and 41, review/ARTIFACT_CHECK.json (per-slide "fixed font roles" and "palette"
check details, read 2026-10-01), DECISIONS.md D-345, D-350, D-355.
FONT_ROLES itself is unchanged; the extra sizes are not in the table above.

| Size / colour | Role | Admitted only | Region (inches) | Constants from |
|---|---|---|---|---|
| 24 pt FFFFFF | outline heading | outline page with visual.variant "heading_pairs" (page 2) | inside (0.50, 1.20, 12.83, 6.86) | FOCUSED slide 2 (D-350) |
| 18 pt BFBFBF | outline subline | same | same | FOCUSED slide 2 |
| 17 pt | bullet detail line | a page that declares bullet_boxes (page 41) | left column (0.50, 1.20, 5.85, 6.75) | FOCUSED slide 41; 22 pt leading kept (lnSpc 2595 in the FOCUSED XML, D-345) |
| 28 pt title (existing role) | title | on the heading-pairs page the title box may reach down to 1.20 in | (0.50, 0.45, 12.85, 1.20) | FOCUSED title box bottom 1.198 in |
| 10.5 pt B0B0B0 | footer | on the heading-pairs page only (no rule) | (0.50, 6.94, 12.85, 7.46) | FOCUSED page-number box bottom 7.458 in |

Gating (validate_deck.py): font_role_admitted(pt, spec) admits 24 and 18 pt
only when outline_pairs_variant(spec) (visual.kind outline and variant
heading_pairs) and 17 pt only when spec has bullet_boxes; palette_admitted
admits BFBFBF and B0B0B0 only on the heading-pairs outline (FFFFFF and BBBBBB
everywhere). Read from ARTIFACT_CHECK.json at build 77: slide 02 uses sizes
10.5, 18, 24, 28 pt and colours B0B0B0, BFBFBF, FFFFFF; slide 41 uses 10.5, 16,
17, 22, 28 pt and BBBBBB, FFFFFF; no other slide uses 17, 18 or 24 pt. The
self-test rejects 17 and 24 pt on an ordinary page and 20 pt on a bullet_boxes
page. Content values (not code): page 2 heading_size 24, subline_size 18,
heading_color FFFFFF, subline_color BFBFBF, footer colour B0B0B0, box_style
plain; page 41 bullet_boxes sizes alternate 22 and 17 pt, six boxes, leading 22
pt. The options title_box, footer and box_style and each declared box (within
BOX_TOLERANCE_IN 0.005 in) are checked by the D-355 aggregate check. No run is
bold.

## Baked text (review/EFFECTIVE_TEXT.md, build 71 numbers, unchanged at build 77)

Effective size = em_px / (visible source px per placed inch) * 72, from
report_effective_text.py. Target for regenerated images: 16 pt effective.
Page numbers are build-71 numbers, read from review/EFFECTIVE_TEXT.md
(regenerated 2026-09-30); the exception pages are selected from the deck by
file or film since D-321.

| Page | Image | Smallest baked text | Basis |
|---|---|---:|---|
| 7, 13, 14, 15, 20, 28, 29 | overlay_*.png (coordinate overlays) | 17.1 pt (every label, em 57 px) | producer label size (D-271 N-2); 6.000 in placed width, page 15 6.608 in on its 1586 px two-panel canvas (240 px per in either way); meets the target |
| 35 | r5_label_compare_f1890.png / f1462.png | 16.5 / 15.6 pt | measured (M2, build 58) |
| 52 | chart_transport_package.png | 16.0 pt (all text) | producer font size, build 60 |
| 50 | chart_marker_bench.png | 10.4 pt (legend) | producer font size; exception |
| 56-57 | chart_filter_{offline,realtime}_panel.png | 9.5 pt | producer font size; exception |
| 9-11, 39, 53-57 | equations/typeset/ts_*.png | 18.6 pt | producer font size (11.65 pt at 600 dpi); exception |
| 32 | ch7_object_waypoints_r6b.png crops | 8.9 / 7.2 pt | estimate; exception |
| 5 | ch2_fig_flow.png (thesis Figure 2.3) | 6.5 pt (arrow labels) | producer font size; accepted 2026-09-30 (D-264) |
| 38 | ch8_fig_system.png (thesis Figure 8.1) | 4.7 pt (arrow labels) | producer font size; accepted 2026-09-30 (D-264) |
| 58-76 | equations/white/eq_*_numbered.png (50 derivation crops) | 10.3 pt (first-level scripts); base math 16.8 pt | measured from the thesis PDF (7.33 pt scripts = 61.11 px at 600 dpi, placed at scale 1.4); accepted (D-281, D-285) |
| 8-11, 16-18, 22-25, 27, 30, 36, 39, 41, 53-55 | films | about 7.5-14.8 pt | 2026-09-29 font inventory; exception. The page-4 clip has no burned-in text since build 71 (D-320) |

Round-10 changes to the overlays (all still 17.1 pt): overlay_static_markers.png
is new on page 7 (D-318); overlay_camera_frames.png on page 13 is a plain
diagram panel without a photograph (D-316); overlay_torso_root.png on page 15
has two panels on a 1586 x 1200 px canvas (D-317).

## Accepted exceptions and reasons

- Films: media bytes pinned by media_contract.json; not re-encoded (D-259).
- Pages 5 and 38: the author asked for the thesis figures as they are
  (2026-09-30); byte copies bound to figures/thesis/manifest.json (D-264).
- Page 32: byte-identical thesis figure crops bound to figures/evaluation/manifest.json.
- Pages 50 and 56-57: plot-only regeneration at 16 pt overlaps the data
  (legend and text box over curves, tick names run together, clipped
  titles); reaching 16 pt needs a chart redesign (author call, D-259).
- Pages 9-11, 39 and 53-57 typeset equations: a larger render changes the
  EMU-exact geometry that the validator pins for the hidden filter pages (D-259).
- Pages 58-76: thesis derivations quoted as typeset at one scale; raising
  the scripts to 16 pt needs scale 2.2, and that scale does not fit the families on
  two pages (D-281, D-285).

## Commands (from presentation/defense_2026, thesis Python)

    python report_effective_text.py            # writes review/EFFECTIVE_TEXT.md
    cd experiments/transport_bench && python transport_bench.py --package-chart-only
    cd experiments/marker_bench && python plot_marker_bench.py      # plot-only, from summary.csv
    cd experiments/filter_metrics && python charts.py --panel       # plot-only, from summary.csv and run_info.json

The committed marker chart was made with matplotlib 3.11.2; a rerun with
the thesis Python (3.9.2) differs in pixels only.
