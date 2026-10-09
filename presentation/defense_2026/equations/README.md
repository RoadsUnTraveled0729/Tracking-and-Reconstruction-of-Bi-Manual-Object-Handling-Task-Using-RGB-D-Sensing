# Exact thesis equation assets

Currency note (2026-10-08): These retained crops and equation_catalog.json
are pinned to the thesis PDF reviewed before the post-defence revision.
Their equation/page numbers, source hash and glyph geometry retain that
scope; they are not a new pagination map of the current V9 thesis.
The producer intentionally rejects a changed source PDF. build_deck.py
and validate_deck.py references below describe the retired pipeline
(D-385; recoverable at 85078c9 and 87e87ae). Do not regenerate or rebind
these historical assets as a documentation update. Current delivery and
current thesis status are in [the presentation README](../README.md) and
[the V9 README](../../../writing/v9/README.md).

These images quote final Thesis V9 directly. They preserve the thesis's font,
left frame labels, vector notation, hats, bars, primes, subscripts,
superscripts, fractions, matrices and punctuation. They are not AI-generated
or re-typeset approximations.

Read `../equation_catalog.json`. Its `equations` object maps keys such as
`eq_3_18`, `eq_5_2` and `eq_D_2` to repository-relative `path`, `aspect`,
pixel dimensions, printed/PDF page, equation number, crop coordinates and
SHA-256. The `numbered_path` alternative also includes the original right
equation number. The primary `path` has only the equation body and is better
suited to a slide with a separate citation.

Images have a transparent background and retain the original black glyphs.
Use them on a light background without recoloring or stretching. Place each
with its natural aspect ratio. A narrow source expression may be enlarged;
long expressions with repeated frame labels need a full-width strip or a
dedicated equation slide. In particular, do not compress Eq5.2 or Eq5.12 into
a small half-slide caption.

Source coordinates are PDF points measured from the page's top-left corner.
PDF page numbering is one-based. Main-text page p is PDF page p + 14.
Equation D.2 is on printed D3, PDF page147. The catalog fixes the source PDF
hash and records every crop hash. All numbered equations were also located
inside native OMML formula rows of the final DOCX.

Regenerate from the repository root:

```bash
/home/luo/anaconda3/bin/python presentation/defense_2026/equation_assets.py
```

The script requires Poppler's `pdftocairo` and Pillow. It fails if the pinned
PDF changes, a numbered equation disappears from the DOCX, a crop is empty,
or visible content touches a crop boundary. Contact sheets support visual
review; the source crop coordinates themselves are explicitly reviewed.

Mathematical qualifications and repairs to the former slide shorthand are
recorded in `../review/EQUATION_AUDIT.md`. Most importantly, Eq5.7 returns a
wrist target in Scene; the fixed inverse scene anchor must carry it into
Camera' before the arm solve of Eqs5.8-5.12.

## Round 8 additions (2026-09-30)

The catalog now covers every numbered equation of Chapters 2-7: Eqs. 3.5,
3.6, 3.13, 3.14, 4.2 and 7.1-7.6 were added (53 entries in all). The
compiled thesis has no Eq. 4.3; the stale zh/src export numbers the
Chapter 4 cleaning rule (4.3), which is compiled Eq. 4.2. The appendix
equations D.1, E.1 and G.1 are not cropped. The producer also writes the
white RGB-only copies of the new crops into `white/` with the same
operation as `build_deck.py`; `white_manifest.json` itself is rewritten by
`build_deck.py` for the keys a build uses. New crops appear on
`contact-05.png`; the earlier contact sheets are unchanged.

`derivation_leads.json` quotes, for each numbered equation of Chapters 3-7,
the sentence that introduces it in the zh/src export, with file and line,
and records whether that sentence matches the compiled PDF. Three do not
(Eqs. 3.2, 3.6 and 3.17); for those, `compiled_text` carries the compiled
wording, which is the one to quote. Regenerate with:

```bash
/home/luo/anaconda3/bin/python presentation/defense_2026/equations/derivation_leads.py
```

Decisions: `ROUND8_NOTES.md`.

Inline math in a lead. The export flattens inline math, so a lead is quoted on
a derivation slide with each inline-math span replaced by the omission mark
"[...]" (D-286). Spans come from two recorded sources in
`derivation_leads.json`: the square-bracket markup of `source_text` that is
not a numeric citation (the `note` field says "square brackets that delimit
inline math removed"), and the `omission_spans` list of a row, naming
symbols that the export prints without bracket markup (Eq. 3.22 `L12`,
Eq. 7.2 `p_i`, `c`, `C`, Eq. 7.4 `p_i`; D-292). `omission_spans` is written by
`derivation_leads.py` from `VISIBLE_OMISSIONS`; a span must occur in
`source_text` in order, a row may not carry both kinds, and note and field
must agree. `derivation_leads.py --check` regenerates the JSON in memory and
compares it byte for byte with the committed file (exit 1 on any difference,
nothing written); `validate_deck.py` runs it and also requires each
`source_text` to be a substring of its cited line under `writing/v9/zh/src`
(D-289):

```bash
/home/luo/anaconda3/bin/python presentation/defense_2026/equations/derivation_leads.py --check
```
