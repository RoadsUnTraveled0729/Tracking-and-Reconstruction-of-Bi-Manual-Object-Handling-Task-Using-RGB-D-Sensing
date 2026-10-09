# Defence deck references: deck number -> work -> thesis number -> where cited

## Final deck list (Verified 2026-10-06)

Source: presentation/defense_2026/Thesis_Defence_2026.pptx slides 42-44
(python-pptx), D-378, D-379. The author consolidated the references onto three
visible pages with the deck's own IEEE numbering [1]..[23]; the round-10 list
[1]..[12] below is retired. Page 42 (1 of 3) holds [1]-[8], page 43 (2 of 3)
[9]-[16], page 44 (3 of 3) [17]-[23]:

[1] Diaz and Payandeh 2017 (multimodal sensing interface); [2] Zhan et al.
OakInk2; [3] Dong and Payandeh (hand kinematic model from tracked landmarks, Appl.
Sci., vol. 15); [4] Dill et al. (3D pose reconstruction accuracy); [5] Wang et al.
RGB2Hands; [6] Bazarevsky et al. BlazePose; [7] Hampel 1974; [8] Pearson et al.
generalized Hampel filters; [9] Butterworth 1930; [10] Oppenheim and Schafer,
Discrete-Time Signal Processing; [11] Gustafsson, initial states in forward-backward
filtering; [12] Dobrowolski, swing-twist decomposition (arXiv:1506.05481); [13]
Garrido-Jurado et al. ArUco; [14] Unity scripting reference, Transform and
Quaternion; [15] Casiez, Roussel and Vogel, 1 euro filter; [16] Kwok, Koenig and Hu,
arm kinematic correction; [17] Dong and Payandeh (Bayesian estimation of hand
kinematics); [18] Craig, Introduction to Robotics; [19] Olson, AprilTag; [20] Wang
and Olson, AprilTag 2; [21] Krogius et al., flexible tag layouts; [22]
Romero-Ramirez et al., speeded-up detection of squared fiducial markers; [23]
Savitzky and Golay (Anal. Chem.).

Bracket citations on shown slides 1-41 (regex scan of text frames, 2026-10-06):
slide 3 [1]-[5]; 7 [6]; 8 [7], [8]; 10 [9]-[11]; 14 [12]; 17 and 18 [13]; 28 [14]; 37
[15]; 40 [16], [17]. [18]-[23] have no bracket citation on slides 1-41 (hidden
slides were not scanned); they are listed on the reference pages. Full entry text
is on the slides; the thesis compiled numbering is unchanged (see the section "Two
thesis numberings" below).

## RETIRED (history): the round-10 and earlier lists

Everything below describes the generated decks (builds up to 77; recover at
85078c9) and their validator rules, which were deleted in 3dbd345 (D-382). The "Two
thesis numberings" section and the entry notes remain useful as thesis facts.


## Round-10 numbering (Verified 2026-09-30, build 73, HEAD 9e0ebec; re-verified 2026-10-01 at build 77; retired list)

Re-verified 2026-10-01 at build 77 (master 88878cd): the reference list [1]..[12]
(rows on pages 45-46 of talk_content.json) and the first-citation order are
unchanged (first uses [1] p7, [2] [3] p9, [4] [5] [6] p11, [7] p39, [8]-[11]
p49, [12] p53); the citing pages in the table below are the same, and the
captions of pages 7, 9, 11, 32, 39, 50, 53, 55, 56 and 57 are character for
character those listed below. Sources: talk_content.json, backup_content.json,
review/round11_focused/CITATIONS.md (FOCUSED against build 74, "No renumbering
is needed or proposed") and review/ARTIFACT_CHECK.json (2092 checks PASS,
including rules 1-8 and "Deck reference numbers are first cited in order 1 ..
N (D-297, rule 6)"). Differences at build 77: (1) the page-49 narration no
longer cites [8]-[11] (the author's text drops them, D-359); [8]-[11] stay in
the visible Source column of the page-49 table and in its Sources line (the
`source` field, carrying [1] and [8]-[11] since D-338, build 74), so the
"49 (notes/table cell)" entries read "table cell and Sources line" now;
(2) the page-49 stale source field note below is no longer true (corrected at
build 74, D-338); (3) the validator count 2081 below is the build-73 figure,
2092 at build 77.

The deck's own IEEE list [1] .. [12] was renumbered in build 68 so that the
numbers follow the order of first citation after the restructure (D-306,
UNCERTAIN; the author may instead prefer main filter captions without [3]
and [5]). Cause: the Hampel, Pearson (Generalized Hampel filters),
Butterworth, Oppenheim and Gustafsson works were first cited on the hidden
filter pages 51 and 53, whose films and captions moved to main pages 9-11
(D-307), so they are now first cited before Casiez (page 39). Old to new:
old [9] -> [3], [3] -> [4], [10] -> [5], [11] -> [6], [4] -> [7], [5] -> [8],
[6] -> [9], [7] -> [10], [8] -> [11]; [1], [2] and [12] keep their numbers.
The References rows were reordered with their entries unchanged (D-306).

References pages: main pages 45 (rows [1]-[6]) and 46 ([7]-[12]) of
talk_content.json (kind full_table, columns "No." and "Reference"); the rows
were read from display_table of those pages, 2026-09-30.

The table below was built by a script from talk_content.json and
backup_content.json: the rows come from pages 45-46; "Cited on pages" lists
every page whose visible text fields (title, bullets, panel_bullets,
visual_caption, display_table cells) or notes contain the token "[n]", with
the field in brackets. Pixel arrays, coordinate lists, equation keys, the
source and provenance fields and every field not named were not scanned, so
the numeric-array noise of the earlier attempt does not arise. The two
References pages themselves are excluded from the citing pages.

| Deck | Work | Old deck (round 9) | Thesis compiled | Cited on pages (field) |
| --- | --- | --- | --- | --- |
| [1] | Garrido-Jurado 2014 | [1] | not in thesis | 7 (caption), 32 (caption), 49 (table cell) |
| [2] | Hampel 1974 | [2] | [45] | 9 (caption) |
| [3] | Pearson 2016 | [9] | [46] | 9 (caption) |
| [4] | Butterworth 1930 | [3] | [48] | 11 (caption), 56 (caption) |
| [5] | Oppenheim 2010 | [10] | [47] | 11 (caption) |
| [6] | Gustafsson 1996 | [11] | [49] | 11 (caption), 56 (caption) |
| [7] | Casiez 2012 | [4] | [50] | 39 (caption), 55 (caption), 57 (caption) |
| [8] | Olson 2011 | [5] | not in thesis | 49 (notes/table cell) |
| [9] | Wang and Olson 2016 | [6] | [58] | 49 (notes/table cell) |
| [10] | Krogius 2019 | [7] | not in thesis | 49 (notes/table cell), 50 (caption) |
| [11] | Romero-Ramirez 2018 | [8] | not in thesis | 49 (notes/table cell) |
| [12] | Savitzky and Golay 1964 | [12] | [54] | 53 (caption), 56 (caption) |

First-citation order by this table: page 7 [1]; page 9 [2], [3]; page 11 [4],
[5], [6]; page 39 [7]; hidden page 49 [8]-[11]; hidden page 53 [12]. It is
contiguous, so validator rules 2, 5 and 6 hold (2081 checks pass at build
73, review/ARTIFACT_CHECK.json).

Exact caption strings (talk_content.json, backup_content.json): page 7
"Static desk and wall marker axes, ArUco [1]."; page 9 "Hampel window 7, k 3,
floor 0.02 m [2], [3]."; page 11 "Order 4, 3 Hz, forward-backward [4], [5],
[6]."; page 32 "Absolute length error in cm, figure from the rail recording,
ArUco [1]."; page 39 "Same recorded frame and causal filter output, One
Euro filter [7]."; page 50 "AprilTag 3 is the detector of Krogius et al.
[10], ArUco the OpenCV detector used in this thesis."; page 53
"Savitzky-Golay window 9, order 2 [12]."; page 55 "One Euro min cutoff 0.05
Hz, beta 1 [7]."; page 56 "Right wrist, 785 frames, all at lag 0 [4], [6],
[12]."; page 57 "Right wrist, 785 frames, lag from cross-correlation with
despiked raw [7]." Page 49 (literature table) cites [1] and [8]-[11] in its
Source column ("[1], Table 3", "[8], p. 7", "[9], p. 6, Table I (p. 4)",
"[10], Fig. 7", "[11], Table 3") and [8]-[11] in its notes.

Left out because a field scan could not confirm them: (1) Page 58 and the
other derivation pages: their visible text is the verbatim lead from
equations/derivation_leads.json, which the content fields do not hold, so no
citing page is listed for them; the one compiled-thesis bracket, "[52]" in
the Eq. 3.18 lead (compiled PDF page 46, Dobrowolski, not a deck row),
sits on derivation page 64 (Eqs. 3.18-3.23, previously page 65) by the
title and the lead file, and is not in this table (D-300, rule 9). (2) The
thesis compiled numbers in the table are carried unchanged from the round-9
table below; the docx paragraphs were not re-read in this task. (3) A
STALE FIELD FOUND: the unspoken `source` field of hidden page 49 still says
"Olson [5], p. 7; Wang and Olson [6], p. 6 and Table I (p. 4); Krogius et al.
[7], Fig. 7 (p. 6); Romero-Ramirez et al. [8], ..." (round-9 numbers). The
source field is not a visible text field and not part of the notes, so the
validator rules do not read it; the visible table and the notes of page 49
already carry the new numbers. Build 74 corrected the field to [8], [9],
[10] and [11] (D-338), so this note describes the state up to build 73.

In-text style, builder third-line rule (D-299), page-64 compiled "[52]" rule
(D-300) and the nine numeric validator rules (D-301, D-303) are unchanged
from the round-9 section below, with two differences at build 73: the
CITATION_REQUIRED pages are now the five pages with legacy keys
static_marker_calibration, filter_hampel, filter_butterworth,
object_rig_accuracy and causal_smoothing, that is pages 7, 9, 11, 32 and 39
(D-308; four pages 8, 9, 30, 37 in round 9), and the pages cited in the
round-9 rule texts shifted. MediaPipe and RealSense still have no row (D-277,
open author choice).

Verified: 2026-09-30. Sources: presentation/defense_2026/{talk_content.json
(pages 7, 9, 11, 32, 39, 45, 46), backup_content.json (pages 49, 50, 53, 55,
56, 57), DECISIONS.md D-297 to D-308, review/ARTIFACT_CHECK.json (2081
PASS)}.

## Round-9 numbering (history: build 67, working tree on HEAD ceb67d4; the numbers and pages below were replaced by the round-10 table above)

Author decisions 2026-09-30 (D-297): "citation should be the same as
thesis, using ieee format please"; asked about works the thesis does not
list, "thesis should have its separate reference list, starting from 1".
The deck therefore has its own IEEE numeric list [1] .. [12] in order of
first citation (main pages 8, 9, 30, 37, then the hidden pages 47 table
rows top to bottom, 48, 51, 53, 54, 56, 57, 58). The deck numbers are not
the thesis numbers; thesis numbers appear nowhere on a slide except the
verbatim quotation on hidden page 65 (below).

| Deck | Work | Thesis compiled | Cited on pages (visible text unless noted) |
| --- | --- | --- | --- |
| [1] | Garrido-Jurado 2014 | not in thesis | 8 (caption), 30 (caption), 47 (Source column, notes, source) |
| [2] | Hampel 1974 | [45] | 9 (caption), 51 (caption) |
| [3] | Butterworth 1930 | [48] | 9 (caption), 53 (caption), 57 (caption) |
| [4] | Casiez 2012 | [50] | 37 (caption), 56 (caption), 58 (caption) |
| [5] | Olson 2011 | not in thesis | 47 (Source column, notes, source) |
| [6] | Wang and Olson 2016 | [58] | 47 (Source column, notes, source) |
| [7] | Krogius 2019 | not in thesis | 47 (Source column, notes, source), 48 (caption) |
| [8] | Romero-Ramirez 2018 | not in thesis | 47 (Source column, notes, source) |
| [9] | Pearson 2016 | [46] | 51 (caption) |
| [10] | Oppenheim 2010 | [47] | 53 (caption) |
| [11] | Gustafsson 1996 | [49] | 53 (caption), 57 (caption) |
| [12] | Savitzky and Golay 1964 | [54] | 54 (caption), 57 (caption) |

Exact caption strings (talk_content.json, backup_content.json): page 8
"Detector dots on the recorded frame; ArUco markers [1]."; page 9
"Recorded right-wrist depth, filtered offline; Hampel [2], Butterworth
[3]."; page 30 "Absolute length error in cm; figure: rail recording; ArUco
[1]."; page 37 "Same recorded frame and causal filter output; One Euro
filter [4]."; page 47 Source column "[1], Table 3", "[5], p. 7", "[6], p. 6;
Table I (p. 4)", "[7], Fig. 7", "[8], Table 3"; page 48 "AprilTag 3 is the
detector of Krogius et al. [7]; ..."; page 51 "[2], [9]."; page 53 "[3],
[10], [11]."; page 54 "[12]."; page 56 "[4]."; page 57 "[3], [11], [12].";
page 58 "[4]." Pages 8, 9, 30 and 37 are the validator's CITATION_REQUIRED
pages (legacy keys calibration_landmarks, signal_conditioning,
object_rig_accuracy, causal_smoothing).

In-text style (as the compiled thesis: 21 occurrences of "[a], [b]", none of
"[a, b]" or "[a]-[b]"): one number per bracket, ", " separated, no ranges,
numbers before the final period. A name may stay next to its number ("Olson
[5]", "Krogius et al. [7]"); a year never follows a name anywhere in the
visible text or the notes of any page (D-297, D-301).

References pages: main pages 43 (rows [1]-[6]) and 44 ([7]-[12]), kind
full_table, columns ["No.", "Reference"], column_widths [0.06, 0.94], 5 s
each (D-298). The eight thesis entries are byte-identical to
writing/v9/Thesis_V9.docx paragraphs 1077 Hampel, 1078 Pearson, 1079
Oppenheim, 1080 Butterworth, 1081 Gustafsson, 1082 Casiez (full venue "in
Proc. SIGCHI Conf. Human Factors in Computing Systems (CHI), 2012, pp.
2527-2530."), 1086 Savitzky and Golay, 1090 Wang and Olson, with the "[NN] "
prefix removed. The four deck-only rows (Garrido-Jurado, Olson, Krogius,
Romero-Ramirez) follow the thesis style; Garrido-Jurado lists all four
authors. Rows [1] and [4] take three lines at 16 pt. The "Entries" section
below still gives the DOIs and the round-5 notes for reference; the slide
rows print no DOI.

Builder allowance (D-299): build_deck.py restrained_full_table draws a row
with a three-line cell THIRD_LINE = 0.30 in taller (rowh = min(.82, (bottom
- 1.34 - THIRD_LINE * n3) / len(rows))); it errors if rowh < .40, if rowh <
.66 with multi-line cells, or if a cell needs more than three lines. The slide
XML of every other full_table page is byte-identical to build 66.

Page 65 rule (D-300): hidden derivation page 65 (Eq. 3.18) quotes the
compiled thesis sentence "They separate into swing and twist [52], with the
twist innermost:" (equations/derivation_leads.py COMPILED["3.18"], compiled
PDF page 46). The zh/src export line 87 prints [44] (source numbering);
compiled [44] is Collins and Bartoli and compiled [52] is Dobrowolski.
Dobrowolski is not in the deck list because the deck never cites it in its
own voice; the bracket number is a verbatim quotation, excluded from the
deck-number scans and checked against the PDF page by validator rule 9.

Validator rules (D-297, D-300, D-301, D-303; validate_deck.py, 2100 checks at
build 67): 1 every [n] is a row number; 2 every row number is cited on a page;
3 no author-year string in visible text or notes (D-303: also "Olson, 2011"
and "Olson (2011)"; the IEEE "City: Publisher, year" shape is exempt in the
visible References rows only); 4 one number per bracket (D-303: also no
adjacent citations separated by anything but exactly ", ", e.g. "[2],[3]");
5 row numbers contiguous [1] .. [N] over both pages; 6 first-citation order
1 .. N; 7 citation_required pages carry a number; 8 every [n] in notes is a
row number; 9 compiled_text numbers appear on the cited PDF page. D-303 also
binds pages 43-44 as drawn: each cell is exactly one text box and the (number,
entry) pairs in reading order equal the JSON rows.

MediaPipe and RealSense still have no row (D-277, open author choice).

Verified: 2026-09-30. Sources: presentation/defense_2026/{talk_content.json
(pages 8, 9, 30, 37, 43, 44), backup_content.json (pages 47, 48, 51, 53, 54,
56, 57, 58), equations/derivation_leads.py and derivation_leads.json (eq_3_18),
build_deck.py restrained_full_table, validate_deck.py, DECISIONS.md D-297 to
D-301 and D-303, review/ARTIFACT_CHECK.json (2100 PASS)}, writing/v9/Thesis_V9.docx
paragraphs 1077-1082, 1086, 1090 (byte identity of the eight rows
re-checked with python-docx in the documentation task: 8 of 8 equal after
removing the "[NN] " prefix; docx paragraph 1076 is compiled [44] Collins and
Bartoli, paragraph 1084 is compiled [52] Dobrowolski).

## Round-8 placement (history, verified 2026-09-30 at HEAD aed90fe; superseded by the round-9 numbering above)

The two References tables are visible main pages 43 (1 of 2: the five
marker studies) and 44 (2 of 2: the filter works), 5 s each, between
Contributions (42) and Thank you (45) (D-267). The hidden pages shifted by
+7 (old 40-51 are now 47-58); the keys on them are unchanged: 47 all five
marker keys; 48 Krogius 2019; 51 Hampel 1974, Pearson 2016; 53 Butterworth
1930, Oppenheim 2010, Gustafsson 1996; 54 Savitzky and Golay 1964; 56 Casiez
2012; 57 Butterworth 1930, Gustafsson 1996, Savitzky and Golay 1964; 58
Casiez 2012.

Main-page citations added in build 65 (D-277), each in the 16 pt caption
and each a key of the References tables: page 8 Garrido-Jurado 2014; page 9
Hampel 1974 and Butterworth 1930; page 30 Garrido-Jurado 2014; page 37
Casiez 2012. validate_deck.py extends the author-year check to every page
except the References pages (the pattern excludes "Frame/Figure/Table/Page/
Slide NNNN") and requires a References key in visible text on the pages with
legacy keys calibration_landmarks, signal_conditioning, object_rig_accuracy
and causal_smoothing (D-277, D-291). Checked result: cited 8, 9, 30 and 37
as listed.

MediaPipe and RealSense have no References key. Pages 8 and 12 name MediaPipe
and page 8 names RealSense without a citation; adding entries needs the
author's choice of citation (D-277, open). Page 30 cites ArUco
(Garrido-Jurado 2014), not AprilTag.

Verified: 2026-09-30. Sources: presentation/defense_2026/{talk_content.json,
backup_content.json,DECISIONS.md D-267, D-277, D-291,
review/ARTIFACT_CHECK.json}. The author-year keys, the page-43/44 split by
family and the D-277/D-291 rules above were replaced in build 67 (D-297 to
D-301).

## Round-6 placement (verified 2026-09-28, built PPTX; history, superseded by the round-8 placement above)

Every round-5 hidden-page id shifts by +2; the two References pages
are now 52-53 (old 50-51). Keys are visible in captions (D-202,
unchanged content, D-212 renumbering): 40 all five marker keys
(Source column, old 38); 41 Krogius 2019 (old 39); 44 Hampel 1974,
Pearson 2016 (old 42); 46 Butterworth 1930, Oppenheim 2010, Gustafsson
1996 (old 44); 47 Savitzky and Golay 1964 (old 45); 49 Casiez 2012
(old 47); 50 Butterworth 1930, Gustafsson 1996, Savitzky and Golay
1964 (old 48); 51 Casiez 2012 (old 49). validate_deck.py checks both
directions (every References key visible on a hidden page; every
visible author-year string on a hidden page is a References key);
round-6 result 1331 checks, 0 package failures.

## Round-5 placement (verified 2026-09-28, built PPTX)

Keys are visible in captions (D-202): 38 all five marker keys (Source
column); 39 Krogius 2019; 42 Hampel 1974, Pearson 2016; 44 Butterworth
1930, Oppenheim 2010, Gustafsson 1996; 45 Savitzky and Golay 1964; 47
Casiez 2012; 48 Butterworth 1930, Gustafsson 1996, Savitzky and Golay
1964; 49 Casiez 2012. validate_deck.py checks both directions (every
References key visible on a hidden page; every visible author-year
string on a hidden page is a References key).

Verified: 2026-09-28
Sources:
- writing/v9/Thesis_V9.docx (compiled thesis, committee version
  e8b40b6), reference-list paragraphs read with python-docx
  (paragraph index given per entry); cross-checked against
  writing/v9/Thesis_V9.pdf via pdftotext (References, pp. R1-R4)
- writing/v9/references.md (frozen chapter-source numbering)
- writing/v9/zh/src/*.txt (citation sites, source numbering)
- knowledge/marker_literature.md (marker studies)
- api.crossref.org/works/<DOI> (author initials, venue, volume,
  issue, pages, year of the four marker studies not in the thesis)
- presentation/defense_2026/references/page50_snippet.json (the
  round-5 References pages 50 and 51 were built from this file; the file
  and references/KEY_USAGE.md were deleted in build 67, D-301; in git history)
Answers: the external works the defence deck cites, their full
citation, the short key used on the slides, and the thesis reference
number for each work the thesis cites.

## Two thesis numberings (read before quoting a thesis [n]; the deck's own numbers are in the round-10 table at the top)

Note (Verified 2026-10-06, D-394): post-defence revision 1 added source entries [60]-[62] (compiled [19], [28], [29]) and shifted later compiled numbers by +1/+2, so the compiled numbers in the table below that come after [19] may have moved; re-check against citation_mapping.json before quoting. 168 pages unchanged.

The compiled thesis renumbers citations by first appearance
(writing/v9/references.md, D-069 note;
writing/v9/audit_evidence/final_completion/citation_mapping.json).
The chapter exports in writing/v9/zh/src/*.txt and
writing/v9/references.md keep the frozen source numbers. The
committee's thesis (Thesis_V9.docx / .pdf) uses the compiled
numbers. Quote the compiled number to the committee.

| Work | Compiled (committee) | Source (zh/src, references.md) |
| --- | --- | --- |
| Hampel 1974 | [45] | [53] |
| Pearson 2016 | [46] | [54] |
| Oppenheim 2010 | [47] | [55] |
| Butterworth 1930 | [48] | [56] |
| Gustafsson 1996 | [49] | [57] |
| Casiez 2012 (One Euro) | [50] | [40] |
| Savitzky and Golay 1964 | [54] | [46] |
| Wang and Olson 2016 | [58] | [48] |
| Kalaitzakis 2021 (not on the deck) | [28] | [29] |

So source [57] is Gustafsson 1996 (forward-backward filtering), not
Butterworth; Butterworth 1930 is source [56] / compiled [48].

## Entries

Full citation text: thesis entries are copied byte-for-byte from
Thesis_V9.docx; marker entries are composed in the thesis's IEEE
style from knowledge/marker_literature.md, with fields confirmed on
Crossref. "Slide text" is what the round-5 page50_snippet.json (deleted in
build 67) printed when it differed from the full citation; the deck numbers are in the round-10 table at the top of this file (the round-9
numbers differ for nine works, see the old-to-new map there).

### Marker studies (References page 50)

- Garrido-Jurado 2014 -- S. Garrido-Jurado, R. Munoz-Salinas, F. J.
  Madrid-Cuevas, and M. J. Marin-Jimenez, "Automatic generation and
  detection of highly reliable fiducial markers under occlusion,"
  Pattern Recognition, vol. 47, no. 6, pp. 2280-2292, 2014, doi:
  10.1016/j.patcog.2014.01.005.
  Slide text: author list shortened to "S. Garrido-Jurado et al." and
  DOI omitted (two-line fit). Not in the thesis reference list.
  Cited on the deck: ArUco vs AprilTag literature table (detection
  time, no false positives).
  All fields confirmed (marker_literature.md + Crossref; accents
  dropped for plain ASCII).
- Olson 2011 -- E. Olson, "AprilTag: A robust and flexible visual
  fiducial system," in Proc. IEEE Int. Conf. Robotics and Automation
  (ICRA), 2011, pp. 3400-3407, doi: 10.1109/ICRA.2011.5979561.
  Slide text: DOI omitted. Not in the thesis reference list.
  Cited on the deck: literature table (original AprilTag speed and
  range). All fields confirmed.
- Wang and Olson 2016 -- J. Wang and E. Olson, "AprilTag 2: Efficient
  and robust fiducial detection," in Proc. IEEE/RSJ Int. Conf.
  Intelligent Robots and Systems (IROS), 2016, pp. 4193-4198.
  Thesis compiled [58] (docx paragraph 1090), source [48]; DOI
  10.1109/IROS.2016.7759617 (marker_literature.md, Crossref; not in
  the thesis entry). Thesis cites it in Appendix E (AprilTag corner
  refinement). Cited on the deck: literature table (AprilTag 2 time,
  false positive rate).
- Krogius 2019 -- M. Krogius, A. Haggenmiller, and E. Olson,
  "Flexible layouts for fiducial tags," in Proc. IEEE/RSJ Int. Conf.
  Intelligent Robots and Systems (IROS), 2019, pp. 1898-1903, doi:
  10.1109/IROS40897.2019.8967787.
  Slide text: DOI omitted; title in sentence case as in the thesis
  style (published title case: "Flexible Layouts for Fiducial Tags").
  Not in the thesis reference list. Cited on the deck: literature
  table (AprilTag 3 vs ArUco 3 recall and speed); marker benchmark
  (AprilTag 3 detector). All fields confirmed.
- Romero-Ramirez 2018 -- F. J. Romero-Ramirez, R. Munoz-Salinas, and
  R. Medina-Carnicer, "Speeded up detection of squared fiducial
  markers," Image and Vision Computing, vol. 76, pp. 38-47, 2018,
  doi: 10.1016/j.imavis.2018.05.004.
  Slide text: DOI omitted. Not in the thesis reference list. Cited
  on the deck: literature table (ArUco3 speed-up, corner jitter).
  All fields confirmed.

### Filter methods (References page 51)

- Hampel 1974 -- F. R. Hampel, "The influence curve and its role in
  robust estimation," Journal of the American Statistical
  Association, vol. 69, no. 346, pp. 383-393, 1974.
  Thesis compiled [45] (docx paragraph 1077), source [53]; cited in
  Section 2.5 and Appendix F (rolling Hampel test). Deck: Hampel
  spike removal.
- Pearson 2016 -- R. K. Pearson, Y. Neuvo, J. Astola, and M. Gabbouj,
  "Generalized Hampel filters," EURASIP Journal on Advances in Signal
  Processing, vol. 2016, art. 87, 2016.
  Thesis compiled [46] (docx paragraph 1078), source [54]; Section
  2.5, Appendix F. Deck: Hampel spike removal.
- Oppenheim 2010 -- A. V. Oppenheim and R. W. Schafer, Discrete-Time
  Signal Processing, 3rd ed. Upper Saddle River, NJ, USA: Pearson,
  2010.
  Thesis compiled [47] (docx paragraph 1079), source [55]; Section
  2.5 (Butterworth design procedure), Chapter 5 (source line
  Chapter_5_Pose_Recovery.txt:46), Section 8.1 (definition of a
  causal stage), Appendix F. Deck: hidden page 44, Butterworth
  smoothing (design), in the caption; not placed on page 49. Row kept
  (DECISIONS.md D-202, 2026-09-28).
- Butterworth 1930 -- S. Butterworth, "On the theory of filter
  amplifiers," Experimental Wireless and the Wireless Engineer, vol.
  7, pp. 536-541, 1930.
  Thesis compiled [48] (docx paragraph 1080), source [56]; Section
  2.5, Appendix F (flat passband). Deck: Butterworth smoothing; why
  Butterworth offline.
- Gustafsson 1996 -- F. Gustafsson, "Determining the initial states
  in forward-backward filtering," IEEE Transactions on Signal
  Processing, vol. 44, no. 4, pp. 988-992, 1996.
  Thesis compiled [49] (docx paragraph 1081), source [57]; Section
  2.5, Section 8.1, Appendix F (forward and backward pass). Deck:
  Butterworth smoothing; why Butterworth offline.
- Savitzky and Golay 1964 -- A. Savitzky and M. J. E. Golay,
  "Smoothing and differentiation of data by simplified least squares
  procedures," Analytical Chemistry, vol. 36, no. 8, pp. 1627-1639,
  1964.
  Thesis compiled [54] (docx paragraph 1086), source [46]; Section
  4.2 (object position smoothing), Appendix F. Deck: Savitzky-Golay
  filtering; why Butterworth offline (comparison).
- Casiez 2012 -- G. Casiez, N. Roussel, and D. Vogel, "1 euro filter:
  A simple speed-based low-pass filter for noisy input in interactive
  systems," in Proc. SIGCHI Conf. Human Factors in Computing Systems
  (CHI), 2012, pp. 2527-2530.
  Slide text: venue shortened to "in Proc. SIGCHI Conf. (CHI)" (the
  thesis entry wraps to three 16 pt lines).
  Thesis compiled [50] (docx paragraph 1082), source [40]; Section
  2.5, Section 8.2, Appendix F. Deck: One Euro filtering; why One
  Euro in real time.

## Not on the deck (for reference)

- Kalaitzakis 2021 (thesis compiled [28], source [29]): the thesis
  cites it in Chapter 1 for ArUco; no deck page cites it.
- Jurado-Rodriguez 2023, Laurent and Sandoz 2026 (preprint), Sagitov
  2017: in knowledge/marker_literature.md only; no deck page cites
  them.
- Software used by the benchmarks (OpenCV aruco, the AprilTag 3
  library through pupil-apriltags) is named on the marker pages but
  not given a literature citation; the AprilTag 3 detector is covered
  by Krogius 2019.
