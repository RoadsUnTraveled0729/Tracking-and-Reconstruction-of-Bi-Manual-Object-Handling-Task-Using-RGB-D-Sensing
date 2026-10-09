Chapter 7 recommendations, 2026-09-07

Status: Advisory review complete. Supervisor D7-D10 remain open.
Baseline: 2bcaad660281ceb2fbd2fdc03a29bf2534e276a6.
Scope: Handover, current condensed Chapter 7, supervisor comments,
pinned evaluation reports, and Unity capture prerequisites. No manuscript,
experiment, scene or recording was changed; no message was sent.

Current state

V7 is frozen as sent; the current assembled deliverable is
writing/v8/Thesis_V8_Condensed.docx. Its Chapter 7 includes the completed
manual labels, corrected eligibility disclosure, and sensor-scale display
precision. Older supervisor notes describe the labels as pending and
must not determine their present status. The Chapter 6 round 4 and
Chapters 7-9 round 3 prose findings in HANDOVER.md remain unapplied.

D7 recommendation: keep the loop only for the label evaluation

Keep the rail task as the main experiment. Retain the loop as a short,
explicitly secondary natural-failure case study, with minimal recording
context and both favourable and adverse results. Remove its wire/path
diagram, trajectory comparison, full synthetic-masking discussion and
torso analysis from the main Chapter 7. Preserve the source evidence.

The labels are already completed. The rail set has 21 failure labels and
five clean reference-check labels. The loop has 20 failure labels, 16
left and four right, plus seven clean labels; 58 hidden-mark frames were
skipped. These are small, selected visible subsets of the failure windows.

On the four right-side loop labels, the recovery solve's median distance
to the label is 5.2 cm, against 11.4 cm for the plain solve and 17.6 cm
for the hold-last solve. On the 16 left-side labels, the corresponding
medians are 13.1, 12.3 and 12.7 cm. Compare solve-to-solve FK positions;
the held-landmark baseline is a different quantity. This evidence supports
a limited case study, not general recovery superiority or bimanual accuracy.

Sources: eval/labels/README.md; eval/reports/r5_recovery_labeled.md;
eval/reports/r6b_recovery_labeled.md; current build_ch7.py Section 7.3.3.

If all loop material is removed, the rail labels can still support a
natural-failure evaluation without new labelling. Dropping the loop from
Chapter 7 would not automatically remove its use in Chapter 8 or its
calibration role in Chapter 6; those need a separate scope decision.

D8 recommendation: compact recovery evidence, no standalone 7.4

Keep one short rail-masking result and one compact natural-label table,
including sample counts, clean reference checks and adverse outcomes.
Retain the finding that recovery does not consistently outperform a held
pose on the slow rail task. Across five 45-frame right-arm masked windows
with about 3 to 6 degrees of arm motion, every method's window median is
below 3 cm, but recovery reaches 14.9 cm on its worst onset frame while
holding stays below 5 cm in each window. Source:
eval/reports/r6b_recovery_eligible.md and build_ch7.py Table 7.4.

Move the detailed window tables and exploratory moving-outage analysis
to a concise appendix only if still cited; otherwise park them in V8.
Keep their negative findings in the main summary. The eligible-only rerun
provides no moving outage under the existing protocol, so the manually
selected overlapping outages must not become a headline accuracy claim.

Remove 7.4 as a standalone section. Retain a brief statement that the
reported arm results use hip-depth preparation from Section 2.6 and
Appendix G, with the occluded-start limitation. Place detailed torso
diagnostics with their evidence outside the main Chapter 7, and discuss
their implications in Chapter 9. Keep numerical evaluation out of the
method chapters under skill_set/thesis-structure-rules.md.

Use "reference disagreement" for the clean label check, not a proved
accuracy floor: cuff/jewellery clicks and sensor depth do not establish
the anatomical wrist centre or a hard lower error bound.

D9 recommendation: make the shared-frame figure and clarify trails

Prepare the rail reference, cube centre and kinematic wrist trajectory
on common world axes with one distance unit. Ask whether "same Unity"
also requires trails inside the Unity scene. Prioritize the working right
wrist; if the idle left wrist is shown, distinguish measured, recovered
and held intervals. Do not grade it against the rail as a holding hand.

The rail line is fitted from the object track, and the recovery can use
that same object track. The holding wrist also has an offset from the
cube centre. The combined figure therefore shows trajectory consistency;
it cannot by itself establish independent wrist accuracy. Keep the manual
label comparison separate. Sources: build_ch7.py Section 7.2;
MATH_LOGIC_REVIEW.md M01; supervisor comment C35.

D10 proposed reply, for the user to send

"I agree that Chapter 7 should focus on the task schematics, the object
and wrist trajectories in the same world frame, and matched Unity
reconstructions. I propose removing the wire-path analysis and keeping
only a short labelled recovery comparison, including both its successful
and unsuccessful cases, to support Chapter 5. The rail recording uses
one hand throughout and contains no handover; the system represents both
arms, but this experiment does not evaluate a two-handed handover. If a
handover is required, I would need to record and evaluate a new trial.
When you say 'in the same Unity', do you mean the same units in one plot,
or trajectories displayed together inside the Unity scene?"

Unity capture recommendation and verified status

Use matched RGB/Unity panels at the parked start or grasp, lift or rail
placement, mid-slide and far end. Inspect the RGB frames before choosing
exact indices. Do not label the final frame as release without evidence
that release occurs before the recording ends.

Existing committed assets, viewed during this review:
writing/v7/figures/ch6_fig_unity.png, assembled from
writing/v7/figures/src/r6b_unity_f00114.png and r6b_unity_f00700.png.
These cover the desk move and slide, not a complete station strip.
Their provenance is writing/v7/scripts/make_ch6_unity_fig.py.

The local bag, calibration, landmark/object CSVs, recovery CSV and Unity
binary exist. Required capture input:
eval/output/recovery_r6b/angles_recovery.csv.

Host-level read-only probes on 2026-09-07 found no reachable MCP endpoint
at http://127.0.0.1:8080/mcp: the status helper returned DOWN/NOT attached,
and a direct HTTP attempt returned Errno 111, Connection refused.
The first sandbox-only probe returned Errno 1, Operation not permitted;
that earlier result alone could not establish host state. No editor was
started or stopped. No new captures were produced. This session also has
no exposed Unity MCP tool; starting the server alone does not establish
client access.

Existing workstation startup and attachment check, from the repo root:

python3 scripts/start_unity_mcp.py
python3 scripts/start_unity_mcp.py --status

The existing alternate capture script is eval/unity_check/run_unity_capture.py.
It manages its own editor/publisher and clears a scratch capture directory;
it was inspected, not run. Check active editor state before using it.

Validation

Read both the current chapter builder and built DOCX, checked pinned label
reports and dataset counts with an independent reviewer, inspected capture
provenance with a second read-only reviewer, viewed the existing composite,
and checked the MCP connection outside the restricted sandbox. No experiment
was rerun. Advisory documentation needs no manuscript rebuild.
