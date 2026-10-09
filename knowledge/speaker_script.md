# Defence speaker script: source, builder and rules

Verified: 2026-10-06 (HEAD eb5458d plus the D-392 and D-393 working tree). Sources:
presentation/defense_2026/{speaker_script.json, build_speaker_script.py,
Thesis_Defence_2026_Speaker_Script.docx, .pdf}, DECISIONS.md D-386, D-388,
review/RENDER_RECORD.json.

Answers: where the spoken script lives, how it is rebuilt and what is checked.

- Source of truth: speaker_script.json (text and cue of slides 1-46 in "slides",
  header lines, "blocks" with ten sections, "timing"). The docx is a build output.
- Builder: build_speaker_script.py. `--extract` docx to JSON (seeding only, it
  overwrites the JSON); default mode builds the docx (template = the current docx
  with its body cleared, one Heading 3 per section, timing lines recomputed);
  `--check` lints and exits 0 on pass.
- Timing constants (source: review/personal_review_20261005/build_documents.py
  lines 41-44): 110 words per minute, 2 s per slide, per-slide viewing pause,
  remainder to the cap on slide 38, cap 1620 s for slides 1-46, read from timing.cap_s of the JSON (D-388).
- Result 2026-10-06 (D-388): 2,659 spoken words, 1620 s = 27:00, 0 lint hits. D-391 (slide 39
  text) made it 2,660 words, still 1620 s (the JSON header states 2,660). D-393 changed
  the slide 33 cue only. Current after the D-392 slide 34 text and cue (Final state):
  `--check` 2657 words, 1620 s, cap 1620 PASS, hits 0; docx sha256
  f0fdb49146374ce0f86f58ad44ee741c7d0900e46be0f49aa76e2f05068f28ab (54,318 B), pdf
  11ccc9f27bf137d2eb9d61f8650cf7e82dd991353309fb6de1805fc369f67495 (199,693 B, 23 pages).
  Slack is 0 s: slide 34 is now 94 words, 57 s; "under ideal conditions" was dropped to
  stay at the cap and one dictated sentence was recast to avoid opening on "Three"
  (D-392 Final state). D-386 was
  2,532 words, 1560 s. D-388 rewrote slides 13, 14 and 31-35 and made 14 cut edits (slides 7, 14, 20, 22, 26-29, 32, 33, 36) to stay under the cap.
- Style rules (D-386): each block opens with a question (the only exception to
  D-263); each section and paragraph states its point first; no semicolons, filler
  words, internal recording names, sentences opening on a number word or repeated
  sentences. Slides 47-77 have no spoken script in this file.
- Unverified: a timed aloud rehearsal and a cold read against the slides. The slide 32
  sentence "The depth leg before the lift reconstructs short in both recordings, and the
  two legs after it reconstruct long" is a claim the slide does not show (D-388).
  The slide 33 sixteen-centimetre grasp sentence was cut in D-388.
- Rebuild: see presentation/defense_2026/README.md (Speaker script section).
