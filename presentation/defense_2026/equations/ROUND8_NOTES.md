# Round 8, milestone M3a (build 65 part 1): equation assets and thesis lists

Decisions recorded at the moment they were made, in the DECISIONS.md
format. IDs are local (R8-E1 ...); the master renumbers them into
presentation/defense_2026/DECISIONS.md.

ID: R8-E1
Status: SETTLED
Decision: Crop each new equation at its measured ink bounds widened by 4 pt horizontally and 5 pt vertically, rounded outward to whole PDF points.
Why: Matches the clear margin of the reviewed crops, keeps antialiased glyph edges inside the crop, and stays clear of the neighbouring text lines on every page.
Alternatives: Hand-picked boxes as for the earlier entries (not reproducible from a stated rule); pdftotext word boxes (they understate brackets, norms and summation signs).
Evidence: Ink bounds = pixels with grey value below 250 in a 600 dpi grey render of the pinned PDF, equation numbers excluded (x < 495 or 490 pt). Existing crops eq_3_1, eq_3_2, eq_3_4, eq_3_12, eq_5_12 and eq_6_1 measure 2.9-4.9 pt horizontal and 4.6-8.8 pt vertical margin. The producer's own border check (nonzero alpha must not touch any crop edge) passed for all 22 new files, so the 250 threshold is not load-bearing. Every new crop was inspected visually on a white background: no neighbouring text, no cut glyphs, equation number present in every _numbered variant.
Reversibility: Edit the box in SPECS of equation_assets.py and rerun it; only the round-8 files change.
Review: Open equations/contact-05.png, or the eleven eq_*_numbered.png files of R8-E2.

ID: R8-E2
Status: SETTLED
Decision: Add Eqs. 3.5, 3.6, 3.13, 3.14, 4.2 and 7.1-7.6 as SPECS entries appended after the earlier ones, and paginate the contact sheets of earlier and round-8 entries separately.
Why: The brief requires every pre-existing file to keep its bytes; inserting in numeric order or sharing a sheet would rewrite contact-01 to contact-04.
Alternatives: Numeric SPECS order (rewrites all four earlier contact sheets); appending without separate pagination (rewrites contact-04).
Evidence: sha256 of all 134 pre-existing files under equations/ plus equation_catalog.json before and after: 133 identical; only equation_catalog.json changed, and its 42 earlier entries and all top-level fields compare equal as JSON. A dry run of the unmodified producer into a temporary root first reproduced all 88 producer outputs byte for byte (determinism check).
Reversibility: Remove the eleven SPECS rows and ROUND8_KEYS and rerun; delete the 33 new files.
Review: equation_catalog.json keys eq_3_5 ... eq_7_6.

ID: R8-E3
Status: SETTLED
Decision: The compiled thesis has no Eq. 4.3, so no eq_4_3 crop exists; compiled Eq. 4.2 (the object-track cleaning rule, PDF page 58) is cropped as eq_4_2.
Why: The zh/src export of Chapter 4 is stale: it numbers the inverse anchor (4.2) and the cleaning rule (4.3); the compiled PDF prints the inverse anchor inline without a number and the cleaning rule as (4.2).
Alternatives: None; a crop labelled 4.3 would cite a number the committee copy lacks.
Evidence: pdftotext -layout of writing/v9/Thesis_V9.pdf (numbers (4.1) on PDF 55 and (4.2) on PDF 58 only); native DOCX OMML rows list 4.1 and 4.2 and no 4.3.
Reversibility: None needed.
Review: The master's missing-equation list named 4.3; it should read 4.2 only.

ID: R8-E4
Status: SETTLED
Decision: Extend the producer's native-DOCX check from Chapters 2-6 to Chapters 2-7 so the 7.x crops are verified in the DOCX OMML like every other numbered crop.
Why: Without it the producer raises "Equation 7.1 missing from native DOCX OMML" although the equation is present.
Alternatives: Skip the DOCX check for Chapter 7 (weakens the provenance guarantee).
Evidence: DOCX OMML rows contain 2.1, 3.1-3.24, 4.1-4.2, 5.1-5.12, 6.1-6.6, 7.1-7.6, D.1, D.2, E.1, G.1 (55 numbers).
Reversibility: Revert the one regex.
Review: equation_assets.py, docx_equation_numbers.

ID: R8-E5
Status: UNCERTAIN
Decision: The producer writes white RGB-only copies of the eleven new primary crops into equations/white/, and white_manifest.json was rebound to the new catalog sha256 with its equations list left empty.
Why: The white copies and the manifest are otherwise written only by build_deck.py, which this milestone may not run. The copy uses the same operation and the same write-if-pixels-differ rule, so a later build finds them current and leaves them. The committed manifest lists no keys because the current deck places no thesis crop; rebinding only its catalog hash keeps validate_deck's "manifest binds the unchanged source catalog" check true until the next build rewrites the file.
Alternatives: Leave white_manifest.json stale (validate_deck fails that check until the next build); write manifest rows for keys the deck does not yet use (build_deck would overwrite them and they would claim uses that do not exist).
Evidence: The copy operation applied to the 32 existing white files reproduced all 32 byte for byte. The eleven new white files keep the dimensions and every alpha byte of their sources, with RGB 255.
Reversibility: Delete the eleven white files; rerun build_deck.py, which rewrites the manifest.
Review: After the round-8 build, confirm white_manifest.json lists the equation keys the new pages place and binds catalog sha256 2bb434a33cc1f8669ff6e0727ccf690141cf17791a0d06c6487d47295c266ff9.

ID: R8-E6
Status: SETTLED
Decision: Derivation leads are the last sentence of the zh/src paragraph immediately before each equation row; the file keeps the exact export text (source_text), a slide-readable text with only zero-width spaces and inline-math brackets removed (text), and a compiled_pdf_check result, plus compiled_text wherever the export sentence differs from the compiled thesis.
Why: The brief asks for verbatim export quotes, but the export is stale in places; a slide must quote the committee copy.
Alternatives: Quote the compiled PDF only (pdftotext interleaves inline math, so it cannot be quoted verbatim automatically); export only (three sentences would misquote the committee copy).
Evidence: Letters-and-digits comparison with pdftotext of PDF pages 35-135: 45 sentences match in full or outside inline math, 2 (Eqs. 3.24 and 4.1) match on manual comparison of PDF pages 48 and 55, and 3 differ (Eqs. 3.2, 3.6, 3.17; compiled wording transcribed from PDF pages 37, 38 and 45).
Reversibility: Rerun equations/derivation_leads.py after editing it.
Review: eq_3_2, eq_3_6 and eq_3_17 in derivation_leads.json.

ID: R8-E7
Status: SETTLED
Decision: The four footer-audit lists in knowledge/thesis_outline.md use the compiled numbering and wording (table of contents, List of Figures, List of Tables, body equation positions) and name the matching export file:line as a locator; appendix figures, tables and equations are included.
Why: The compiled PDF is the committee copy and the citation authority (thesis_outline.md); the export differs in Chapter 9 sections, the 5.6 title, Figure 5.6, the Figure 2.4 citation number, the Table 9.1 caption and the Chapter 4 equation numbers.
Alternatives: Export-only lists (would list nonexistent Sections 9.1-9.8 and Eq. 4.3).
Evidence: Item-by-item comparison recorded in the lists section of knowledge/thesis_outline.md. The same check found that the chapters table there read "Valid Landmark Tracking" for 7.3; the compiled table of contents and heading read "Valid Landmark Measurements", and the row was corrected.
Reversibility: Text edit.
Review: knowledge/thesis_outline.md, section "Numbered lists for the footer audit (round 8)".

ID: R8-E8
Status: SETTLED
Decision: Semantic notes for eq_4_2, eq_7_4, eq_7_5 and eq_7_6 restate the thesis's own qualifying sentences; the other new entries keep the producer's default note.
Why: The catalog note should carry the qualification a slide must not drop, and only these four have one stated beside the equation.
Alternatives: Default notes for all (loses the export-numbering warning on 4.2 and the "not physical accuracy" qualification on 7.4).
Evidence: PDF page 58 (4.2), 101 ("They do not measure physical accuracy."), 107 ("Equation (7.5) applies to both"), 115 ("no display frame enters this section").
Reversibility: Edit SEMANTIC_NOTES and rerun.
Review: equation_catalog.json semantic_note fields of those four keys.
