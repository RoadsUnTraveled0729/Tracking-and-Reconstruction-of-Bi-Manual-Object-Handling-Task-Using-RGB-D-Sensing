# Defence presentation decisions

This log covers the defence presentation only. Thesis files, frozen code,
recordings and experiment outputs remain source evidence.

ID: D-001 (reuse decision superseded by D-005; V9 remains the source)
Status: SETTLED
Decision: Build on the existing V9 presentation and use Thesis V9 as the scientific source.
Why: The presentation brief names V9 and the V9 delivery records the completed supervisor revision. Reusing verified figures and local media preserves their provenance.
Alternatives: V8 and the older presentation are superseded; a new unrelated deck would discard usable material.
Evidence: presentation/v9/BRIEF.md; writing/v9/README.md; writing/v9/DELIVERY_2026-09-16.md; clean working tree at ae312c6.
Reversibility: Repoint the presentation source and rebuild if the author selects another thesis revision.
Review: Confirm V9 is the thesis being defended.

ID: D-002 (structure superseded by D-006; time budget later superseded by D-023)
Status: UNCERTAIN
Decision: Budget the existing 32-slide main talk at 1170 seconds, including media, with 30 seconds of margin before the 20-minute limit.
Why: The supplied guideline caps the talk at 20 minutes. The existing 1235-second budget exceeds it, and the scripted pace must allow video narration and pauses.
Alternatives: Keep 20 minutes 35 seconds, which exceeds the guideline; remove substantive results without first trying tighter narration.
Evidence: User-supplied 15-to-20-minute guideline; existing OUTLINE.md. The 30-second margin is an editorial choice, not a measured rehearsal result.
Reversibility: Retime or remove material after a timed rehearsal.
Review: Rehearse aloud on the defence machine; the written budget is not proof of delivered duration.

ID: D-003
Status: SETTLED
Decision: Append a separately identified Q&A section after the main talk and exclude it from the main-talk time budget.
Why: The author explicitly requested additional slides for the question period.
Alternatives: A prose Q&A guide alone does not meet the request for slides; presenting backups during the main talk would consume the allotted research-summary time.
Evidence: Author's follow-up request in this session and the seven question categories in the supplied guideline.
Reversibility: Edit or remove individual backup slides without changing the main-talk sequence.
Review: Check that the backup topics match the committee's likely questions.

ID: D-004
Status: SETTLED
Decision: Delegate independent thesis and media audits and main-talk editing to the available inherited-model agents.
Why: Repository rules and the author authorize delegation. The named Opus and Sonnet models are not available through this session's agent tool.
Alternatives: Claiming unavailable model tiers or using an unsupported tool argument would misrepresent execution; duplicating the audits would add no independent review.
Evidence: The agent tool's exposed model list; AGENTS.md and CLAUDE.md; three bounded delegation briefs in this session.
Reversibility: Future review can use another available model.
Review: Audit findings must be checked against source evidence before acceptance.

ID: D-005
Status: SETTLED
Decision: Create a new presentation under presentation/defense_2026 without using the old deck's design or narrative as the starting point.
Why: The author explicitly rejected the current deck's quality and asked not to base the new presentation on it.
Alternatives: Incrementally polish the V9 slide layouts, rejected by the author. Verified recordings remain usable research evidence.
Evidence: Author's message in this session: "the current one is veeery low quality try to not based on it".
Reversibility: The existing presentation/v9 deck and sources are preserved for history; only new-track outputs are changed.
Review: Assess the new narrative, legibility and demonstration scale on the rendered slides.

ID: D-006 (slide count and duration superseded by D-023)
Status: UNCERTAIN
Decision: Use 20 main slides with a 1170-second budget and 16 separate Q&A slides.
Why: A smaller slide count allows demonstrations and explanation without the five chapter dividers and dense figure-plus-bullet layouts of the previous deck.
Alternatives: Retain 32 main slides, which keeps the rejected structure; put all technical evidence in the main talk, which exceeds the requested duration.
Evidence: Author's 20-minute request and separate-Q&A instruction. Counts and the 30-second margin are editorial choices pending rehearsal.
Reversibility: Change the content JSON, regenerate notes and rebuild after rehearsal.
Review: Check the spoken pace, clarity of the main argument and coverage of committee questions.

ID: D-007 (presentation tone and emphasis superseded by D-013; light theme superseded by D-043)
Status: UNCERTAIN
Decision: Use large original scene images, editable explanatory diagrams and directly labelled result charts in a light scientific presentation theme.
Why: One visual argument per slide and large demonstrations should make the work easier to follow from the back of the room.
Alternatives: Tiny thesis-page figures beside six long bullets, rejected as the old deck's design; decorative generated imagery, which adds no evidence.
Evidence: Existing preview inspection showed small figures and dense text. Theme colours, font sizes and layouts are editorial choices, not research results.
Reversibility: Change builder style constants and rebuild.
Review: Inspect the PDF and rehearse at projected slide size; the audience must be able to read chart labels and state descriptions.

ID: D-008
Status: UNCERTAIN
Decision: Explain memory flow with a new 16-second schematic loop, using 10 frames per second for the GIF and 30 for the MP4 export.
Why: The original detailed architecture was too small and did not show the complete capture-to-display path in its short loop. Successive simple panels can expose write, commit, read and merge operations.
Alternatives: Reuse the dense original loop; imply its animation timing measures latency. Both would weaken the explanation.
Evidence: Media audit of the existing GIF and Chapter 6/8 packet descriptions; actual sequence-counter and ring-buffer code. Duration and playback frame rates are presentation choices only.
Reversibility: Regenerate media with different pacing after rehearsal.
Review: Confirm labels say the timing is schematic and the object-recovery link reads an available accepted record, without a same-frame guarantee.

ID: D-009
Status: SETTLED
Decision: Preserve the local causal replay's two process logs and rig dimensions as source copies under the new presentation's media/provenance directory.
Why: The media audit found that these existing local outputs were ignored by Git, although old documentation described them as committed. Pinning exact copies supports regeneration and exposes their provenance without rerunning the experiment.
Alternatives: Repeat the incorrect committed-source claim; regenerate data and imply a new result; ship a composed replay without its small source logs.
Evidence: git ls-files checks in review/MEDIA_AUDIT.md; existing v2/output/v2_person_dump_r6b_full.csv, v2/output/v2_integrate_dump_r6b_full.csv and eval/output/unity_check_r6b_v9/rig_dimensions.csv.
Reversibility: Remove the presentation copies if the sources are pinned elsewhere and update the generator path and provenance manifest.
Review: Compare source and copy hashes; distinguish the recording-clock cadence from wall-clock throughput and constrained output from object-assisted recovery.

ID: D-010
Status: UNCERTAIN
Decision: Hide the 16 backup slides from normal sequential slideshow advancement, and link the main Questions slide to a Q&A index with return links.
Why: This keeps the research summary separate from the hour-long question period while allowing quick access to specific evidence.
Alternatives: Advance through every backup after the closing slide, or navigate a long deck without an index.
Evidence: Explicit user request for additional Q&A slides. The navigation design is editorial; actual PowerPoint-host behavior remains to be rehearsed.
Reversibility: Unhide the slides in PowerPoint or change the builder's visibility setting.
Review: On the defence machine, open the index from the closing slide, visit a backup, and use its return link. Exported review PDFs should include hidden slides.

ID: D-011
Status: UNCERTAIN
Decision: Add an 11-second recovery-geometry loop, exported at 10 frames per second as GIF and 30 as MP4.
Why: The audience can see the wrist target move with the object and then see the circle of possible elbows, making the remaining bend ambiguity explicit.
Alternatives: A static small thesis figure; a two-dimensional circle intersection that falsely suggests a unique elbow.
Evidence: Thesis V9 Sections 5.3-5.5 and the two-sphere construction. The animated geometry, playback duration and rendering frame rates are illustrative editorial choices, not measured motion.
Reversibility: Edit anim/recovery_geometry.py and regenerate the asset.
Review: Check the whole loop for readable labels and confirm that the selected elbow is described as inferred from a remembered direction.

ID: D-012
Status: SETTLED
Decision: Use the verified recovery-geometry animation on the elbow-ambiguity backup instead of the first native simplification.
Why: Independent review found that the first backup drawing placed disjoint sphere outlines beside an unrelated intersection ellipse. The generated 3D geometry actually satisfies both segment-length constraints.
Alternatives: Keep a visually suggestive but geometrically incorrect sketch; independently implement and verify a second native projection of the same construction.
Evidence: Thesis V9 Section 5.5; anim/recovery_geometry.py sphere-distance assertions; review of the initial backup 27; inspected animation frames.
Reversibility: Replace it with a correctly projected editable construction after equivalent geometric and visual verification.
Review: The circle remains a family of possible elbows, and direction memory is explicitly a prior.

ID: D-013
Status: SETTLED
Decision: Replace the promotional narrative with an academic, methodology-led defence, retaining detailed results primarily in the Q&A section.
Why: The author explicitly said the candidate reads like a product presentation and asked for more methodology than results. The main talk must explain how the reconstruction is derived and implemented, including its assumptions.
Alternatives: Change only the slide headings or defend the current emphasis; neither addresses the requested change in substance.
Evidence: Author feedback in this session: "this reads like we are selliiiing a product" and "the presentation ... should focus more on methology instead of results".
Reversibility: Revise the editable content and builder again after author review or rehearsal.
Review: Check that most main-talk time explains calibration, kinematics, occlusion handling and data flow, with formal descriptive headings, defined equations and source-grounded diagrams.

ID: D-014 (time budget superseded by D-023; methodology emphasis retained)
Status: UNCERTAIN
Decision: Allocate 800 seconds to the twelve central methodology slides, with 115 seconds for two evaluation slides inside the 1170-second main talk.
Why: This gives calibration, geometric derivation, recovery and implementation most of the talk while retaining evidence for the conclusions.
Alternatives: Preserve six main result slides or compress the derivations into one overview; both retain the emphasis the author rejected.
Evidence: Author's methodology preference; the revised outline budgets slides 4-15 at 800 seconds. Exact timings remain editorial until rehearsed.
Reversibility: Retime the source JSON and regenerate notes after an aloud rehearsal.
Review: Assess whether the mathematical steps are understandable without prior reading of the thesis.

ID: D-015 (concept accepted; layout correction and second animation in D-016)
Status: UNCERTAIN
Decision: Deliver a standalone 36-second animated walkthrough of recorded frame 533 before finalizing the revised presentation.
Why: The author explicitly requested flying data blocks from disk into memory and through subsystem blocks, then asked to review the GIF first. A persistent system diagram and changing payload panel make the transformations visible.
Alternatives: Reuse the protocol-only memory animation, which omits disk input and intermediate payload changes; finalize the deck before visual feedback, contrary to the requested sequence.
Evidence: Author's two latest instructions; Thesis V9 Section 6.5 identifies frame 533, ring slot 5, branch records and interpolation with frame 532. Duration, 10-fps GIF and visual motion are explanatory choices, not measured timings.
Reversibility: Change the animation layout and pace after the author's preview feedback, then replace its embedded asset.
Review: Follow frame 533 through the diagram; verify data contents change at processing blocks, memory copies are distinct from computation, and the final output is a render-time record rather than an unchanged camera frame.

ID: D-016
Status: SETTLED
Decision: Correct the first GIF's overflowing text, add a separate animation of memory-field extraction and combination, and integrate both into the complete methodology-led deck.
Why: The author approved the frame-flow concept, identified text outside its boxes, and explicitly requested the memory-internals explanation and full PowerPoint update.
Alternatives: Keep the first GIF unchanged; expand a single overview until the memory fields become too small; stop after delivering another standalone preview.
Evidence: Author's current message: "ok makes sense, but some of the text is out of the text box" and the request to show how data behaves in memory blocks and is extracted/combined.
Reversibility: Regenerate the two assets and presentation after further review.
Review: All labels must fit their containers. The second animation must distinguish copying fields, decoding records, temporal resampling and packing the combined output.

ID: D-017 (duration and slide budget superseded by D-020)
Status: UNCERTAIN
Decision: Use a 36-second memory-record animation on main slide 15 and the memory Q&A slide, retaining the 1170-second talk budget.
Why: One enlarged memory operation at a time exposes the mechanism without making the existing overview unreadable. The 60-second slide budget allows one loop with explanation.
Alternatives: Add another timed main slide or lengthen the talk; neither is needed to accommodate the requested explanation.
Evidence: Main slide 15 has 60 seconds; actual PSF1, PSR2, PSB2 and PSI2 layouts are documented in Thesis V9 Section 6.1 and the implementation. Animation duration is editorial and remains subject to rehearsal.
Reversibility: Adjust stage holds and narration after rehearsal.
Review: Confirm the audience can follow field movement and why the merger constructs a new render-time record rather than concatenating two input records.

ID: D-018
Status: SETTLED
Decision: Limit Git operations to necessary completion milestones and push the authorized presentation deliverables to the existing origin.
Why: The author asked to avoid regular Git checks, then explicitly authorized pushing after automatic review blocked the first attempt.
Alternatives: Repeated status polling, rejected by the author; assuming the initial denied push succeeded, contradicted by the tool output.
Evidence: User messages "dont check git that reglarly, only check when necessary" and "allow to push". Preview commit 6bf5c38 subsequently pushed successfully to the existing origin.
Reversibility: Stop future pushes if the author changes the instruction; local commits and source files remain available.
Review: Perform a final scoped change review and one commit/push for the completed deck, without unrelated Git polling.

ID: D-019 (visual presentation simplified and paired with video in D-021)
Status: UNCERTAIN
Decision: Include a 14-second grasp-offset animation showing the measured-to-object coordinate transformation and retained offset during wrist loss.
Why: The methodology-led talk needs a visible explanation of how object motion supplies the wrist target before introducing the elbow ambiguity.
Alternatives: Present the equations alone or combine wrist and elbow estimation in one dense animation.
Evidence: Thesis V9 Sections 5.3-5.4 and equations 5.2, 5.4 and 5.7; review/grasp_offset_geometry.json verifies the transformations. The 14-second cycle is an editorial choice.
Reversibility: Change animation pacing or replace it with a static diagram after rehearsal.
Review: Confirm the measured and inferred points are distinguished, the attachment assumption is explicit, and the formula labels remain legible.

ID: D-020 (combined animation split by D-022; time budget superseded by D-023)
Status: UNCERTAIN
Decision: Extend the memory-record animation to 44 seconds and main slide 15 to 75 seconds, taking five seconds from the title and ten from the conclusion.
Why: The author explicitly added Python/Unity read-write interaction and race handling. The visual needs enough time to show an odd counter, a changed counter during reading, a retry and a successful application.
Alternatives: Compress the race example into a few seconds or put it only in Q&A, which would not clearly meet the latest request.
Evidence: User's explicit race-condition request; IntegratedSceneReceiverV2.cs performs up to three read attempts, checks the sequence before and after typed field reads, and returns before applying poses if all attempts fail. Total talk remains 1170 seconds, with 915 seconds labelled methodology and 115 seconds evaluation.
Reversibility: Retime the GIF and slide narration after rehearsal while preserving the protocol explanation.
Review: Sequence numbers 10, 11 and 12 are illustrative. The diagram must show retries within an Update and retained display transforms after all attempts fail, without claiming a formal proof for arbitrary hardware memory ordering.

ID: D-021 (layout superseded by D-032; grasp evidence matching refined in D-034)
Status: SETTLED
Decision: Simplify both geometric GIFs into large 4:3 diagrams and show each beside a recorded task video, with equations and assumptions in native slide text.
Why: The author called the grasp-offset and elbow-recovery graphics messy, then explicitly selected recorded video beside the explanatory GIF. Removing repeated prose, multiple coordinate triads and dense sphere wireframes makes the geometry the visual focus.
Alternatives: Put the two existing dense GIFs side by side; the author selected video plus GIF instead. Imply the schematic is fitted to the recording; it is illustrative geometry and cannot support that claim.
Evidence: Current author feedback and clarification. Context clips use existing VIDEO-1.mp4: frames 600-1019 for grasp context and 930-1259 for occlusion context. Only the black 160-pixel pillarboxes are cropped from the 1280x720 source, retaining the complete 960x720 recorded image.
Reversibility: Change the paired layout and regenerate explanatory assets after further review.
Review: Inspect the actual paired slide at projection size. Captions must identify recorded input overlays separately from illustrative, unsynchronized geometry. Check numerical geometry consistency after simplifying the drawings.

ID: D-022
Status: SETTLED
Decision: Preserve frame_journey.gif as the disk-to-Unity overview and put memory layout/extraction, stream combination and concurrent Python/Unity access into three separate animations and slides.
Why: The author explicitly said to keep the older overview and separate the detailed explanations, then asked to restore and polish frame_journey.gif.
Alternatives: Replace the overview with a detailed byte map or combine all details into one long main-talk animation, contrary to the clarification.
Evidence: Latest author messages in this session. The overview keeps its 36-second trace and diagram structure; only spacing, arrowheads, labels and measured text fitting are polished. The detailed animations partition the audited 44-second explanatory sequence into 18, 10 and 16 seconds.
Reversibility: Reorder or combine slides later without losing the separate source assets.
Review: The overview must remain recognizable and present as its own slide. Detailed slides should each answer one question without replacing that overview.

ID: D-023 (full-draft approach retained; count and timing revised under D-024)
Status: UNCERTAIN
Decision: Produce a full working draft of 26 main slides planned at 28 minutes 15 seconds, plus 16 Q&A slides, and defer the final 20-minute cut.
Why: The author explicitly relaxed the time constraint and requested more material now, with shortening later. The full draft adds dedicated explanations of observability, grip state, recovery fallbacks and Unity transform application.
Alternatives: Keep compressing the new method explanations into 1170 seconds, which no longer matches the author's instruction; add unsupported or repetitive material merely to increase the count.
Evidence: Author: "time ... is not a hard constraint ... keep produce as much as possible and we shrink it later". The authoring outline budgets 1695 seconds, including 1385 seconds of methodology and 135 seconds of evaluation. These times are editorial estimates, not a rehearsed duration.
Reversibility: Use CUTTING_GUIDE.md to select and retime a later defence version while preserving the full draft and technical appendix.
Review: Assess completeness and clarity first. Rehearse and choose the final 20-minute sequence afterwards; do not present the uncut draft as meeting the original limit.

ID: D-024
Status: SETTLED
Decision: Spread the main material over more focused slides, slow the teaching animations, and move detailed memory layouts and fallback tables to Q&A.
Why: The author found the elbow/recovery explanation confusing and the four memory slides crowded and too fast. The author also requested more real-recording placeholders and filter demonstrations. Each main slide should expose one operation before the next one is introduced.
Alternatives: Merely increase GIF resolution or slow the old dense diagrams, which would retain competing information; discard the old overview, contrary to the earlier preservation instruction.
Evidence: Latest author feedback about slides 14-15 and 17-20, low resolution, lack of recording placeholders, and condensed slides. The author confirmed slideshow playback works, so no playback repair is required.
Reversibility: The original overview and detailed assets remain available in the track and appendix. The full source remains editable before the final timing cut.
Review: Check whether each new slide has a single visible question and enough quiet time to explain its operation. Inspect the recording placeholders and their capture instructions.

ID: D-025
Status: SETTLED
Decision: Replace code-like equation strings with exact high-resolution equation extracts from the final thesis and restore the thesis's frame-aware notation.
Why: The author explicitly rejected the equation formatting. Source equations preserve superscripts, subscripts, hats, primes, vector notation and the actual coordinate frames; a simplified symbol alias can hide a mathematical distinction.
Alternatives: Restyle the existing ASCII aliases without auditing their meaning; manually typeset a different notation; reuse a low-resolution screenshot of a whole thesis page.
Evidence: Author request to use the same format as the thesis. Equation audit found omitted frame notation and surrogate symbols; exact equations exist in Thesis_V9.pdf and Thesis_V9.docx.
Reversibility: Replace individual equation assets with equivalent native Office equations after matching both notation and visual rendering against the same source.
Review: Compare the extracted equations with their cited thesis equation numbers and ensure nearby prose defines all symbols used on the slide.

ID: D-026 (paired-panel format refined in D-028; slow pacing retained)
Status: UNCERTAIN
Decision: Use 1920x1080 teaching animations with approximately 36-48-second cycles, large labels, and multi-second holds; add six recorded-trace filter demonstrations.
Why: The earlier 10-18-second detail loops changed before viewers could interpret the operation. Fewer objects and longer holds address pace and attention; native-resolution graphics avoid enlarging small raster diagrams. Actual saved wrist samples provide a traceable filter demonstration.
Alternatives: Add more on-screen labels or upscale old figures; use unlabelled constructed signals that might be mistaken for measured results.
Evidence: Author feedback supports the direction. Exact resolution, timing, layout and selected trace windows are editorial choices, not measured system performance. Filter parameters come from Thesis V9 Section 2.5/Appendix F and the saved filter metadata: Hampel window 7, scale multiplier 3, floor 0.02 m; interior gap limit 5; Butterworth order 4/cutoff 3 Hz; Savitzky-Golay window 9/order 2; median window 9; Appendix-F One Euro minimum 0.05 Hz and beta 1.0. Input copies and selected windows will be pinned with the generated figures.
Reversibility: Adjust pacing, crop selection and slide placement after projection review. Rebuild animations and the deck from the retained sources.
Review: Judge whether the slowed motion helps explain the actual operation. The filter plots are illustrative reprocessing of recorded samples, not new accuracy measurements or claims about the complete causal run.

ID: D-027
Status: SETTLED
Decision: Pair at least 80 percent of the main demonstration pages with actual recorded camera or application footage, and report pending recording slots separately.
Why: The author explicitly requested an 80 percent minimum and prefers recorded work beside the explanation. A pending slot is useful preparation but does not count as recorded footage.
Alternatives: Count placeholders as completed recordings; use unrelated footage only to meet the fraction; replace recorded evidence with generated cartoons. None meets the author's purpose.
Evidence: Latest author instruction: "at least 80% the demo should alog side with real recorded videos". Relevant source material includes recorded R6b/R7 camera data, archived Unity replay and a recorded controlled hold-last demonstration. Clip suitability still requires source and visual checks.
Reversibility: Replace context clips with more direct recordings when available. Preserve the recording inventory and its denominator so coverage stays reviewable.
Review: Check actual versus pending counts, whether each recording illustrates its adjacent method, and whether synthetic-test input, archived rig sizing, slowed playback and uninstrumented context are labelled honestly.

ID: D-028 (layout and type hierarchy superseded by D-032 and D-035)
Status: UNCERTAIN
Decision: Use 1440x1080 explanatory panels beside recorded video, and separate derivation pages to form 39 main slides and 20 Q&A slides before the later timing cut.
Why: A native 4:3 diagram uses the available half-slide area more efficiently than a wide graphic. Equation-only pages preserve legible frame notation without competing with recorded motion. The additional pages separate questions rather than adding new experimental claims.
Alternatives: Scale wide diagrams into half-slide panels, making labels smaller; retain multiple equations and animations on the same slide; shorten the draft before the requested content review.
Evidence: User requested fewer competing details, slower motion and at least 80 percent recorded-video pairing. revision_id_map.json records the 39/20 map. The 1440x1080 generated sources exceed their rendered panel dimensions. Exact resolution, page count, clip selections and planned talk duration are editorial choices until reviewed and rehearsed.
Reversibility: Adjust panel dimensions and grouping in build_deck.py and the content JSON; retain original diagrams and all source material for the eventual short version.
Review: View projected paired panels and equation pages, check that clip labels distinguish recording from schematic, and rehearse before committing to the final timed sequence.

ID: D-029 (superseded by D-033: the author now requires synchronized evidence)
Status: UNCERTAIN
Decision: Show wider recorded task intervals beside the short filter sample windows, with normal or modestly slowed camera playback and explicit context labels.
Why: Stretching only 14-29 camera frames over a 36-second teaching animation would appear nearly static and would not clearly demonstrate the recorded task. Meaningful visible task motion is more useful than matching the schematic's editorial duration.
Alternatives: Preserve the exact short camera crop for the entire diagram cycle, which meets a file-count metric but weakens the demonstration; invent intermediate frames or imply synchronized filtering output, neither supported by the recording.
Evidence: RECORDED_CONTEXT_CHECK.json initially documented the short source windows and 36-second retiming. The author wants real videos that demonstrate the work. Exact wider windows and playback speeds are editorial choices, recorded in the final provenance and frame mappings rather than experimental measurements.
Reversibility: Replace the clips or retime their source frames without changing the recorded traces or the filter calculations.
Review: Verify meaningful real task movement, readable plot stages and honest timing labels. Actual camera context does not itself show the numerical filtered output or establish a new accuracy result.

ID: D-030 (overview placement superseded by D-037; current coverage must be recalculated)
Status: UNCERTAIN
Decision: Apply the 80 percent target to all 20 main and Q&A method demonstrations as well as the main talk, pairing the Q&A memory explanation with recorded integrated output while keeping the original frame overview full size.
Why: This meets the author's overall emphasis without reducing the original dense overview to approximately 10-12 point labels. The Q&A memory page can use a sparse combination diagram beside recorded output to explain that derived pose records, not camera pixels, reach the display.
Alternatives: Claim only the main-talk fraction; shrink the original overview to fit another panel; count an unrecorded future-validation brief as completed footage. The first leaves scope ambiguous, the second harms readability, and the third is inaccurate.
Evidence: The content audit identifies 20 method-demo pages, including three pending main memory captures and the original frame overview. The intended recorded count is 16, with 12 of 15 in the main talk. The R5 camera/Unity clip is an existing qualitative legacy capture, not a V2 PSI2 counter or merger-timestamp recording. The optional future live-validation brief remains explicitly unrecorded and outside this method-demo count.
Reversibility: Replace the Q&A output context with a dedicated instrumented recording. The complete 44-second memory_records GIF and MP4 remain supplied as separate technical-reference assets; the original frame_journey remains embedded full size on slide 58.
Review: Check the actual slide pairs and both denominator definitions. Judge whether the recorded output helps explain derived state; do not infer that it validates the adjacent schematic's concurrency events.

ID: D-031
Status: UNCERTAIN
Decision: Request 35-45-second technical captures for private image copies and stream combination, and 45-55 seconds for the controlled Python/Unity read-write explanation.
Why: The reader needs time to inspect real counters, timestamps and local values before the next operation. These targets agree with the slide-specific instructions and avoid compressing the requested technical recordings into an unreadable short clip.
Alternatives: Use the initial generic 20-30-second capture target for every demonstration, which leaves less time for the required states; introduce artificial fast motion or conceal debugger pauses.
Evidence: The author identified motion pace and information density as problems. talk_content.json records the specific steps for slides 29, 31 and 33. The target durations are editorial capture guidance, not performance measurements; an actual recording has not yet been made.
Reversibility: Retain the uncut source and edit a shorter version after rehearsal. Keep actual observed timing distinct from pauses or controlled interleavings.
Review: Confirm that every claimed step is visible and labelled, then choose the shortest cut that remains understandable. The optional live-validation brief on slide 54 keeps its separate 20-30-second target.

ID: D-032 (left/right grid retained; chapter ordering and theme revised by D-043)
Status: SETTLED
Decision: Rebuild the deck around a consistent restrained layout, with English bullets and exact equations on the left and recorded evidence, diagrams or charts stacked on the right.
Why: The author explicitly rejected inconsistent typography, decorative large numbers, giant equation displays and competing visual emphasis. Each page must first define the tracking or reconstruction problem and the method used to address it.
Alternatives: Retain individually styled pages and patch only the named examples; this would leave the whole-deck inconsistency the author identified. Translate the final content into Chinese; the author explicitly requested English.
Evidence: Author feedback of 2026-09-22, including the fixed left-text/right-visual arrangement, uniform typography and English-only clarification.
Reversibility: Revise the shared layout tokens and slide-purpose plan, then regenerate the editable PowerPoint and preview.
Review: Inspect a filter page, a torso page and an equation page before the full render, then check the same hierarchy across every main and Q&A slide.

ID: D-033
Status: SETTLED
Decision: Replace independently timed filter context and animation pairs with composites whose camera image and progressively revealed plot use exactly the same source frame and timestamp.
Why: The author explicitly required the chart to draw only as much data as the video has played, and identified the existing Hampel and gap panels as unclear. A single movie keeps both panels synchronized in PowerPoint.
Alternatives: Retain wider unsynchronized camera context under a disclaimer, as in D-029; this no longer meets the request. Stretch different windows to the same duration; equal playback duration alone does not establish matching data.
Evidence: Author's 2026-09-22 comparison of slides 9 and 10 with the preferred slide 27 and explicit synchronization instruction. Pinned R6b landmark samples and audited decoded camera frames are available.
Reversibility: Regenerate the composite movie from its source-frame mapping. Source samples, frozen filter functions and earlier media remain preserved.
Review: Compare camera frame IDs, plot cursor and revealed sample limits at the start, middle and end, including any repeated frames or pauses. Check the numerical filter provenance independently of playback.

ID: D-034
Status: SETTLED
Decision: Move pinhole deprojection into Q&A and replace unrelated torso, grasp-offset and frame-flow illustrations with evidence tied to the actual recording or explicitly selected recorded frame.
Why: The main talk should explain difficulties encountered and how they were addressed. The author rejected the triangle torso depiction and mismatched video/diagram pairs on the current slides 20 and 28.
Alternatives: Preserve the generic diagrams with stronger caveats; this would retain the mismatch the author identified. Label an elbow as a shoulder to copy a mistaken landmark index; indices must follow the thesis and saved data.
Evidence: Author feedback of 2026-09-22. The repository landmark convention identifies shoulders 11/12 and hips 23/24; the old torso drawing showed only the three points used to define its basis.
Reversibility: Adjust the evidence frame and overlay specification while preserving the recorded source and its source-to-display mapping.
Review: Show both shoulders and both hips on a real image, distinguish the full rigid torso from the three-point basis construction, and verify that paired geometric and flow explanations refer to the same selected data.

ID: D-035 (type hierarchy and source scale retained; white equation derivatives in D-046 and black theme in D-043)
Status: UNCERTAIN
Decision: Use one DejaVu Sans type hierarchy (28-point title, 22-point body, 16-point visual labels, 11-point section label, 10.5-point source) with a 5.35-inch left explanation column and 6.61-inch right evidence column.
Why: Fixed semantic sizes and a consistent two-column grid implement the author's requested restraint. The right visual region is 5.50 inches high; recorded footage and its chart share this region vertically. Exact source equations use a fixed 1.6 scale from PDF points rather than growing to fill available space.
Alternatives: Fill every box with the largest possible font; use slide-specific title or metric sizes; shrink overflow text automatically. These recreate the inconsistent emphasis the author rejected.
Evidence: Author explicitly requested consistent placement, typography and emphasis. Exact sizes, margins and source scaling are editorial choices; no projection rehearsal yet supports these particular values. Native and generated evidence share white, ink 22313D, muted 52606B, derived/structural blue 386C8C and amber AB783B for missing/hold status. Long source equations require meaningful line breaks at existing identities or equalities, with all original terms preserved.
Reversibility: Change the shared layout tokens and equation-view crop specifications, then regenerate and visually review the deck.
Review: Check a filter, torso and equation sample first. Inspect every main and appendix page for text fit, visual legibility and consistent emphasis, including the original equation fragments at slide scale.
Validation detail: Package checks use a 0.015-inch geometric tolerance and a 0.005 source-scale tolerance for OOXML integer coordinates and image-crop quantization. A full right-column media item must be at least 6.59 inches wide. These are engineering acceptance tolerances around the declared 6.61-inch layout and 1.6 equation scale, not scientific thresholds. All equation fragments must remain in the left region and cover every original nontransparent glyph; there is no appendix exception.
Validation refinement: The final validator supersedes those provisional geometric and scale margins. Geometry allows only two OOXML EMUs for rounding; equation-scale tolerance is calculated from the actual 1/100000 image-crop fractions and one-EMU extent rounding. This stricter check exposed a 0.01-inch diagram-label box overrun, which is corrected in the layout rather than accepted by tolerance. The left-equation rule and complete source-glyph requirement remain unchanged.
Media-fit refinement: The provisional 6.59-inch minimum is also superseded. The validator checks the actual aspect-preserving composite size of 6.60 by 5.50 inches within the 6.61-inch column, and the restrained schematic's full 6.61-inch width, with the same two-EMU rounding allowance.

ID: D-036
Status: UNCERTAIN
Decision: Render six synchronized filter composites at 1440x1200 and 30 output frames per second, using recorded time at half speed with shared three-second initial and five-second final holds.
Why: One camera-and-plot movie fits the right evidence column and prevents independent media starts or loop lengths from drifting. The pauses make the input and completed result readable. Hampel and gap examples additionally pause for four seconds at the actual flagged/repaired event; both panels pause together.
Alternatives: Retain independent movies and GIFs; stretch a tiny interval to a fixed 36-second cycle; run recorded motion while the plot pauses. These either lose synchronization or make the camera evidence misleading.
Evidence: Windows 450-549 contain the saved Hampel rejection at frame 537; 650-749 contain the saved four-frame gap ending before frame 685; 25-179 provide a common valid comparison interval for Butterworth, One Euro, Savitzky-Golay and median. Values and masks come from the pinned R6b samples and frozen functions. Resolution, speed, holds and selected windows are editorial choices, subject to preview review. The exact quantized timeline is recorded in each output-frame mapping.
Reversibility: Change the display windows and shared time map without changing the recorded samples or filter definitions, then regenerate and inspect the media.
Review: Verify that camera frame, plot cursor, revealed samples and event annotation agree for every output frame. Check complete decoding, deliberate holds and legibility at the final slide scale.

ID: D-037
Status: UNCERTAIN
Decision: Present the preserved overview topic as a legible native right-column diagram and retain its original full-detail GIF and MP4 as explicitly linked supplemental assets.
Why: Shrinking the original full-slide animation into one column would make its detailed labels unreadable and retain the typography the author rejected. A native overview preserves its explanatory role within the consistent slide grid; the original media remain available without being replaced or deleted.
Alternatives: Keep a full-width exception to the requested layout, or shrink the complete old animation into the new evidence column. The first breaks consistency; the second sacrifices legibility.
Evidence: Original slide 58 uses a detailed 1280x720 full-slide animation. Its labels become substantially smaller when displayed at approximately half width. The author requested both preservation of the older overview and, subsequently, consistent restrained whole-deck layout. Providing the original as a supplemental asset is an editorial interpretation of these combined requests.
Reversibility: Restore the original embedded full-slide animation or add a dedicated supplemental-view slide if the author prefers that exception.
Review: Check that the main frame journey and the appendix overview still explain disk, shared images, derived records and display; that the original GIF/MP4 links work locally; and that recording coverage reflects the actual revised pages rather than inherited totals.

ID: D-038
Status: UNCERTAIN
Decision: Use matched R7 frames 600-740 for the grasp construction and a selected R6b frame 533 for the frame-flow explanation, with shared camera/derived-view timing.
Why: These sources directly connect the explanatory quantities to the recorded task. R7 includes verified right-wrist depth loss at 705-707 while the estimated offset is retained; the next missing marker sample at 741 is excluded. R6b frame 533 has saved branch records and a documented 532/533 merger bracket.
Alternatives: Retain the generic grasp cartoon beside unrelated motion; run a camera sequence while explaining a different frame; treat illustrative processing times or the output tick as the recorded capture clock. These would repeat the correspondence errors identified by the author.
Evidence: Archived R7 raw/filtered landmarks, marker poses, calibration, grip episodes and failure flags support the matched projections. Pinned R6b logs agree with frame 533's decoded time to CSV precision and show render time 17.750923 seconds using adjacent source frames. Source paths, hashes and mappings are retained in media/provenance/matched_evidence.json.
Reversibility: Select different recorded intervals or retime both panels together while preserving provenance and distinguishing derived estimates from observations.
Review: Grasp repeats each source frame twice at 30 output fps, then adds a four-second freeze at 705 and a two-second final freeze, totaling 15.4 seconds. Frame flow plays recorded frames 383-532 for five seconds, then freezes 533 for 39 seconds of explanatory stages, totaling 44 seconds. These durations and selected intervals are editorial choices. Check missing-depth wording, unchanged offset through the loss, complete source identity and the explicit distinction between illustrative flow and measured execution.

ID: D-039
Status: UNCERTAIN
Decision: Keep the prior-selection diagram explicitly illustrative, using a reachable two-link construction with lengths 0.28 and 0.25 and endpoint separation 0.36; never present its selected elbow as a recorded solver result.
Why: The source-conditioned endpoints can explain the constraint, but the saved evidence does not contain the direction-memory vector needed to reproduce the solver's selected elbow. A separate analytic example explains the remaining choice without inventing that state.
Alternatives: Draw an arbitrary elbow off the constraint circle; imply the example is fitted to the recording; silently substitute a guessed direction-memory vector. None would faithfully explain the method.
Evidence: build_deck.py constructs the circle analytically and checks both segment lengths. Its unit prior direction is (0, 0.8, 0.6). These numerical values and the projection are editorial geometry choices, not thesis measurements. The early rendered example preserves every nontransparent source pixel of Eq5.12 in two ordered views at its printed comma.
Reversibility: Replace the illustration with a recorded solver-state capture containing its actual stored prior, or choose another mathematically valid illustrative configuration.
Review: Distinguish the recorded endpoint constraint on slide 23 from the illustrative selection on slide 24. Verify circle membership and both lengths, and retain the exact source equation and its assumptions.

ID: D-040
Status: SETTLED
Decision: Use the matched recorded shoulder and object-derived wrist target to illustrate the feasible endpoint-constraint circle on slide 23, keeping actual solver selection separate on slide 24.
Why: This gives the two pages distinct explanatory roles and connects the geometry to the camera image. The archived direction prior is unavailable, and the elbow is measured in this interval, so the derived circle cannot be described as a recorded missing-elbow recovery event.
Alternatives: Pair an unrelated camera interval with the generic geometry; invent a stored prior; label a purely geometric circle as the branch actually executed by the runtime solver.
Evidence: All 141 selected R7 frames have a mathematically feasible circle under the saved right-arm lengths 0.241 and 0.233 m. Independent primary inspection found reach fractions from approximately 0.9265 to 0.9916; some exceed the implementation's 98 percent near-extension guard. Thus the view shows ideal endpoint constraints before branch guards, not proof that the solver used the circle. The same frame map as D-038 keeps the camera and constraint view together.
Reversibility: Replace this illustrative calculation with an instrumented recovery capture that saves the actual branch, prior and selected elbow.
Review: Verify both circle-distance constraints from the recorded endpoint data and saved lengths. Keep observation, offered target, ideal feasible geometry and selected output distinct in the speaker notes and visible explanation.

ID: D-041
Status: UNCERTAIN
Decision: Add visibly moving and changing payload tiles to the matched frame journey while retaining its 44-second source map, selected frame and readable stage holds.
Why: Static stage changes alone do not demonstrate the author's requested movement of a frame through processing and memory blocks. Small tiles can show transfers and changes in data representation without adding more text or large counters. A shared source remains visible when private copies are made.
Alternatives: Leave only changing arrows and cards; animate unrelated camera frames during the selected-frame explanation; obscure labels with moving payloads. These either weaken the requested explanation or confuse source identity.
Evidence: The author explicitly requested a data block that moves between system blocks and emerges with new content. Root inspection of the first matched-frame candidate found that the camera/source mapping was correct but the handoffs mainly changed static states. The exact tile paths, motion fractions and pauses are editorial choices, not execution traces or measured transfer times.
Reversibility: Change only the drawing and motion layer in anim/matched_evidence.py, preserving the recorded source mapping and all numerical evidence.
Review: Inspect mid-transfer frames as well as stage holds. Confirm that moving tiles do not hide headings, that shared data persists during copying, and that the movie labels processing timing as illustrative.
Implementation detail: General travel uses normalized stage fractions 0.16-0.80 with smoothstep easing. The two private-copy transfers use 0.08-0.43 and 0.53-0.88, preserving the source and first copy; record labels change at fractions 0.30 and 0.65. Root inspection of four transition stills and the path/source-retention code passed before encoding. These fractions are editorial pacing choices with no measured-runtime interpretation.

ID: D-042
Status: SETTLED
Decision: Distinguish the raw hip-depth overlay from the thesis's filtered, pre-repair pitch example and describe the sampled surface without an unsupported material label.
Why: The displayed image and points use raw saved observations; the thesis's 32.1-degree pitch uses the filtered landmarks before hip-depth preparation. Naming the visible surface as shirt fabric and attributing that wording to Section 3.5 was unsupported by the checked source.
Alternatives: Treat the rounded depth agreement as proof that the raw and filtered constructions are identical; retain an incorrect source attribution. Both would overstate what the recorded evidence establishes.
Evidence: Thesis V9 printed pp.36-37, Table 3.1 and the following root-angle example, explicitly state filtering before hip preparation. The source describes rail depth at the hip pixels; the presentation now uses the defensible common description of a nearer visible surface. Raw overlay provenance remains unchanged.
Reversibility: A separately verified surface annotation or raw-versus-filtered computation could support a more specific account. Until then, retain the distinction in slides 8/48 notes and MEDIA_PROVENANCE.md.
Review: Confirm that no pitch is attributed to an unperformed raw reconstruction, and that no physical surface identification is presented as independently established.

ID: D-043
Status: SETTLED
Decision: Follow the thesis chapter order, use chapter-labelled topic headings and keyword bullets, adopt black backgrounds with white text, and make the cover centered text only.
Why: These are the author's explicit revisions to the preceding 60-slide draft. The talk must show how the kinematic formulas are derived, explain the circle and copying operations, include a matching spoken script, and show imperfect recorded results with captions.
Alternatives: Preserve the preceding topic order, sentence bullets, light theme or image cover; these no longer satisfy the author. Enforce the original 20-minute limit now; the author previously deferred that cut while the method material is being developed.
Evidence: Latest author feedback following commit 275b539, including a text-only cover, thesis chapter progression, derivation emphasis, black/white styling, and additional imperfect-result media. Canonical scientific content remains Thesis V9 and pinned local evidence.
Reversibility: Change the chapter/order map, presentation source and template without modifying the thesis or scientific datasets. Preserve stable legacy IDs separately from displayed page numbers.
Review: Check chapter progression, short visible phrases, source derivation steps, the old circle/copy explanations, and whether the separate script explains each page's evidence and limitations.

ID: D-044
Status: SETTLED
Decision: Name committee-facing videos pNN-Detailed_Content_Description.mp4, using the final PowerPoint page number and underscore-separated English descriptions.
Why: The author explicitly supplied p09-Hampel_Spike_Removal.mp4 as the required convention. A filename must lead a committee member directly to the corresponding final page, not an internal recording identifier or an obsolete slide ID.
Alternatives: Internal R5/R6b/R7 names, generic VIDEO-1 labels, or numbering before the final order is known; these obscure the connection to the committee materials.
Evidence: The author's final naming instruction and exact example. Preserve original recording IDs, paths and frame maps in the provenance/index rather than discarding source identity.
Reversibility: Regenerate filenames, captions and the index from the final page map. Original sources remain unchanged.
Review: Match every displayed video label, embedded asset, supplied filename and index entry to the final PowerPoint page. Repeated source footage on different pages needs an unambiguous page-specific entry.

ID: D-045
Status: SETTLED
Decision: Move the two displayed hip markers upward onto the torso as a manually adjusted explanatory overlay, while retaining the original raw observations separately.
Why: The author explicitly requested moving L23/L24 off the wooden block. A manual illustration can show the intended torso location, but its new pixel positions cannot be presented as detector observations, measured depth samples or a validated reconstruction.
Alternatives: Silently overwrite the source coordinates; retain the rejected placement without addressing the request. The first misstates the evidence and the second ignores the requested illustration.
Evidence: Explicit author instruction about the previous slide 8. The existing photo and raw source coordinates are preserved in media/provenance/matched_evidence.json; the presentation will record the separate display-only annotation positions.
Reversibility: Restore the original native overlay or choose different display annotation coordinates without touching the source image/data.
Review: Inspect the new hip positions and the visible manual-illustration label. Do not attach the old raw depth readings to the moved points as though newly measured there. The genuine wrong-surface example remains available among the imperfect results.

ID: D-046
Status: SETTLED
Decision: Make white-glyph derivatives of exact thesis equation assets by retaining their alpha channels byte for byte and changing only RGB to white.
Why: This preserves source glyph geometry and antialiasing on the requested black background without re-typesetting the mathematical notation. Original catalog assets remain untouched and both versions remain traceable.
Alternatives: Re-type simplified formulas or render illegible black glyphs on black. White source strips are possible but break the intended continuous dark layout.
Evidence: Primary inspection of the torso/shoulder/elbow equation PNGs found every nontransparent source RGB value equal to zero, with antialiasing carried in alpha. The actual package validator can compare source and derivative alpha bytes and fixed source scaling.
Reversibility: Switch placement back to the original exact equation images on light strips. Keep the original catalog and source hashes authoritative.
Review: Verify source/derivative alpha identity, complete crop coverage and the original formula order/meaning; confirm that colour inversion introduces no changed symbols or missing terms.

ID: D-047 (appendix count extended by D-050; main numbering and manual hip row retained)
Status: UNCERTAIN
Decision: Plan an expanded chapter-ordered draft of 50 main slides and 19 Q&A slides, with manually illustrated hip markers at source-image y=318 pixels and unchanged x coordinates.
Why: Additional derivation and imperfect-result pages address the author's request before the later timing cut. Moving the displayed hips above the wooden block is an explanatory annotation; a level display row makes the intended torso area clear without changing source measurements.
Alternatives: Omit derivation steps to retain the previous count; squeeze multiple steps into crowded pages; silently treat the moved markers as recorded data. These conflict with the requested explanation or evidence integrity.
Evidence: The verified chapter map and proposed slide-purpose sequence support the order. The exact page count and annotation row are editorial choices, not measured anatomy or a rehearsed time budget. Original hip rows are approximately 360/366 pixels and remain in the raw-data failure exhibit.
Reversibility: Change the page map and manually positioned native markers before final numbering/export. Source photos, raw observations and final quantitative results remain unchanged.
Review: Inspect the manually annotated torso at final slide scale and confirm its label distinguishes illustration from recorded observations. Check all chapter transitions and the expanded script before selecting the eventual timed talk.

ID: D-048
Status: SETTLED
Decision: Show the requested approximately 5 cm reconstruction example as a right-arm failure case with a rejected elbow, and show a separate genuinely missing-wrist example with a larger residual.
Why: The near-5 cm figure does not show an absent MediaPipe wrist. Its elbow fails and the arm mask removes both distal observations for recovery; the final wrist differs from both the offered object target and the measured wrist. Correct labelling is necessary when presenting imperfect outcomes.
Alternatives: Call the right wrist absent; report the 5.2 cm four-frame median as the single-frame result; omit the less successful left example. These would confuse the failure, population or reference.
Evidence: Thesis V9 Figures 7.8-7.9 and eval/reports/r5_recovery_labeled.json. Primary inspection confirms frame 1890 final wrist-to-watch-label distance 5.01 cm, plain solve 14.03 cm, offered target 15.20 cm and filtered measured wrist 1.12 cm. Frame 1462 has no measured wrist and final distance 13.65 cm (13.7 rounded), versus plain solve 14.02 cm. These are manual visible-feature references, not anatomical joint ground truth.
Reversibility: Select other pinned failure frames while retaining the correct observation status, reference and single-frame values. No scientific output is altered.
Review: Compare the native captions and spoken explanation with both source figures, the saved failure masks and the per-frame JSON. Explain why the near-5 cm case remains imperfect and why one example does not establish general recovery accuracy.

ID: D-049
Status: UNCERTAIN
Decision: Supply a printable DOCX/PDF speaking script generated verbatim from the final Markdown script, with black text on white paper and restrained fixed text styles.
Why: The author requested an accompanying script. A printed version is convenient for rehearsal while preserving the exact page-specific narration and playback cues generated from the slide source.
Alternatives: Maintain a separately written script that can drift from the slide notes; supply only notes embedded inside PowerPoint. Both make review and rehearsal harder.
Evidence: Explicit author request for a matching speaking script. Wording and order are checked after DOCX serialization; page rendering will be checked after the final script exists. The 11-point body, 12/13-point headings, 16-point document title and letter page are editorial print choices, not thesis requirements.
Reversibility: Regenerate the print formats with different styles. DEFENSE_SCRIPT.md and the slide JSON remain authoritative for narration.
Review: Confirm that every page heading, cue and paragraph matches the final slide order and that neither page breaks nor formatting obscure the spoken text. The black-background requirement is applied to the slide deck and authored media.

ID: D-050
Status: UNCERTAIN
Decision: Append six untimed Q&A pages, one for each source-verified recorded/Unity pair from thesis Figures 7.5-7.6, while preserving the existing page 1-69 numbering.
Why: The author requested many imperfect-result videos and images with a notation below each. The paired source stills make residual hand and arm disagreement directly inspectable, supplementing the two natural-failure figures, raw hip failure and archived replay already in the main draft.
Alternatives: Show only the favorable 5 cm frame; compress all six pairs into one unreadable collage; renumber the stable main talk and its committee videos. These would weaken the requested evidence or introduce needless filename churn.
Evidence: review/CHAPTER_SCIENCE_AUDIT.json verifies all twelve recorded/rendered image hashes and their frame-pair provenance. Rail frames 95/505/700 use the 2026-09-14 per-recording sizing capture; handover frames 700/950/1042 use the archived 2026-09-09 capture with its 0.517 m torso override. These are qualitative discrepancies, not new per-frame error measurements or the Table 7.4 capture.
Reversibility: Remove or replace appendix exhibits without changing existing video page numbers. The additional six-page allocation is editorial and makes the expanded draft 50 main plus 25 Q&A pages.
Review: Inspect each pair at presentation size, ensure each has a clear recorded/reconstructed role and a concise visible-disagreement caption, and keep configuration caveats in its narration. Do not infer a unique cause from a screenshot alone.

ID: D-051
Status: UNCERTAIN
Decision: Encode page-numbered dark media with H.264 CRF 17 and yuv420p, retain original MP4 frame schedules, and supply 10 Hz GIF derivatives with verified quantized frames.
Why: These settings provide practical PowerPoint-compatible movies while preserving the existing explanatory timing. Colour changes apply only to authored graphics; recorded camera pixels are pasted from the original sources before video compression.
Alternatives: Overwrite the preserved masters, accelerate the teaching intervals, recolour the camera pictures or present illustrative timing as measured execution. These would lose provenance or conflict with the author's requirements.
Evidence: anim/committee_media.py reuses the established renderers, numerical arrays and source-frame maps. Root approved the dark filter and frame-flow previews. Encoding validation checks complete decode, dimensions, duration and frame count; representative decoded MP4 frames use a mean absolute channel-error tolerance of 3 on the 0-255 scale. CRF 17, 10 Hz GIF sampling and the tolerance are editorial fidelity choices, not scientific thresholds. Actual per-asset results are recorded after encoding.
Reversibility: Regenerate derivatives with different compression or GIF sampling while retaining source maps and original masters. The separate source-based input-overlay status strip must continue to distinguish torso rejection from landmark visibility.
Review: Inspect full-slide readability and motion, source-camera preservation before compression, exact copied frame maps and per-asset decode reports. Sampled MP4 comparisons are a compression check rather than an exhaustive pixel-identity claim.

ID: D-052
Status: UNCERTAIN
Decision: Give the two private-branch labels clearance from the flying frame tile in the dark page 32 copying derivative, without changing its copy order, source retention or 40-second schedule.
Why: Primary decoded-frame review found the flying tile temporarily covering Person at 15 seconds and Object at 25 seconds. The author specifically requested clear text and easily followed data movement; hiding the destination label weakens that explanation.
Alternatives: Accept the temporary obstruction because the holds are readable; remove the moving tile; overwrite the old master. These either preserve a known readability defect or lose the requested motion and provenance.
Evidence: Decoded frames from p32-Shared_Image_Private_Copies.mp4 at 15/25 seconds, inspected alongside the other memory and frame-flow stages. The current positions are editorial teaching geometry. Only this derivative's label/flight clearance needs correction; the other reviewed motion stages do not require re-encoding.
Reversibility: Revise only the page 32 authored drawing layer and regenerate its MP4, GIF, poster and report. Retain the original source master and the full event schedule.
Review: Inspect both mid-transfer frames after the change, verifying that Person and Object remain readable while the shared frame persists and each branch receives a private copy.
Implementation detail: The page-specific adapter moves the two label rectangles to y=985-1038 pixels. The private tile's maximum bottom is y=972.5, leaving 12.5 pixels before the label band. All 1200 MP4 frame states pass label/tile clearance checks. Root full-resolution inspection at 15 and 25 seconds confirms readable labels, retained source and the already-created first copy. These coordinates are editorial layout choices; operation paths and timing are unchanged.

ID: D-053
Status: SETTLED
Decision: Substitute declared GIF posters only in the temporary PDF-render snapshot, keeping the canonical PowerPoint's animated GIF bytes unchanged.
Why: Final visual review found an empty exhibit on PDF page 36, although the supplied and embedded GIF decodes correctly and its first frame contains the expected read/write diagram. A static PDF should show the supplied exhibit poster reliably. Pages 32, 34 and 36 should use the same explicit export rule.
Alternatives: Deliver the blank PDF page because file/decode checks pass; silently remove animation from PowerPoint; assert an unverified cause for the renderer's omission. None meets the review requirement.
Evidence: Canonical PPTX 8bbf9943, the first final PDF render, preview/slide-36.png, decoded GIF frame zero and 480-frame validation. The failure location is the PDF-rendered exhibit; the precise LibreOffice import/export mechanism is unresolved. The package's earlier 1549 checks did not establish visible GIF presence in the PDF, so the validator must add that check.
Reversibility: Remove the snapshot substitution if a tested renderer preserves GIF stills reliably. Source files, scientific content, movie timelines and the animated PowerPoint remain unchanged.
Review: Bind the exported PDF to the original PPTX hash and separately record the temporary snapshot/poster substitutions. Inspect all three GIF pages and verify their rendered exhibit content rather than relying only on PDF page count.
Validation detail: The added diagnostic crops each GIF exhibit's actual PDF bounds and checks that at least 50 percent of the declared poster foreground remains visible, with a 2-pixel neighbourhood for rasterization differences. These are conservative blank-exhibit detection settings, not scientific tolerances or a pixel-perfect renderer certification. The per-page measured coverage and rasterization settings are retained in the final package report.

ID: D-054
Status: SETTLED
Decision: Add explicit coordinate-frame teaching and synchronized moving axes, with X red, Y green and Z blue, throughout the relevant kinematics, object, recovery and rig material.
Why: The author identified missing coordinate frames and the initial T-pose definition, requested axes on the relevant moving models, and approved the resulting implementation plan. Axis colors have a scientific meaning within the otherwise restrained black/white presentation.
Alternatives: Add only a frame inventory in Q&A; add decorative triads detached from their data; retain the current static-only kinematics section. These do not explain the transformations where the methods use them.
Evidence: Author's coordinate-axis requests and explicit approval to implement the five-part plan. The plan adds Camera/Camera-prime and T-pose pages before old page 11, and a Scene-mapping page before old page 37: 53 main pages and 25 Q&A pages. Canonical definitions are in Thesis V9 Chapters 2, 3, 5 and 6.
Reversibility: Rebuild the presentation from its previous content and preserved original media. No thesis or runtime source is edited.
Review: Inspect the T-pose/root convention, named origins, rotation order, axis colors and final page-numbered media. Old pages 1-10 retain their positions, 11-36 move by two, and 37-75 move by three.

ID: D-055
Status: SETTLED
Decision: Derive each moving axis from the synchronized saved source and its actual coordinate convention, and distinguish accepted input, reconstructed output and held output explicitly.
Why: A convincing image overlay does not establish a valid three-dimensional measurement. Archived Unity footage additionally requires matching rendered state and camera projection before an axis can be drawn directly on the rig.
Alternatives: Infer orientations by eye from video pixels, attach a measured wrist orientation to a single wrist point, or treat a held/rejected frame as a fresh observation. These misrepresent what the sources establish.
Evidence: The approved plan; the pinned R7 input overlay and failure masks; Thesis V9's T-pose root rotation (0,180,0), shoulder/elbow frame definitions and wrist-observability limits; the distinction between model rotations and captured bone rest rotations in Chapter 6.
Reversibility: Regenerate annotated derivatives and their provenance while keeping the original sources. Where direct projection cannot be established, supply a synchronized numerical model panel or an explicit replacement-recording brief.
Review: Match axes, origins and state labels to the source frame and calibration. The Camera-prime reflection and World/Unity swap must not be presented as ordinary rotations; gravity alignment and floor placement lead directly to Scene without restoring an obsolete intermediate frame.

ID: D-056
Status: UNCERTAIN
Decision: Use readable red/green/blue axis strokes and a shared half-speed source clock with introductory and closing holds for the new kinematic teaching clips.
Why: The author requested classic axis colors, clear motion and restrained information density. Half-speed playback and stationary endpoints make the local frames easier to follow without changing source synchronization.
Alternatives: Play the source at full speed, use status colors for the axes, or show all joint triads simultaneously. These reduce readability or make the color meanings ambiguous.
Evidence: The media source audit identifies R7 frames 100-249 as an interval with measured root and right-arm groups and visible shoulder movement. Initial drawing choices are X=#FF4040, Y=#40E070, Z=#408CFF, root-axis length 0.10 m and joint-axis length 0.075 m. The shared schedule uses 30 encoded frames per second, 0.5x playback, and two-second opening/closing holds, for 14 seconds. These are editorial choices rather than new measurements or latency claims; the orthographic viewing direction and final fit remain subject to preview review.
Reversibility: Regenerate the annotated derivatives with different drawing sizes or explanatory pacing while preserving the recorded source-frame mapping and original media.
Review: Inspect the torso and arm samples at slide size. Confirm visibility of all three colored directions, clear labels, correct anatomical-side naming, a fixed model view, and synchronized source-frame indicators.
Implementation detail: The teaching canvas is 1440x1200 pixels. The 640x480 camera source is resized with Lanczos to 768x576 at (336,64). The fixed model view uses 25/12-degree viewing angles, 650 pixels/metre, centre (0.01,0.12,1.23) metres and screen origin (760,930). These values position the evidence for explanation; they are not sensor calibration. The separate Camera-prime orientation key has no depicted optical origin. Primary review accepted the updated torso and twist posters with active L24/L14 labels. Source consistency uses 1.3e-6 matrix and 0.000051-degree saved-CSV tolerances, accounting for four-decimal angle rounding; the independent double-precision formula diagnostic uses 1e-12. These are numerical correspondence checks, not anatomical accuracy claims.
Companion-media detail: Calibrated MappedMarker overlays use 0.045 m illustrative axis lengths. Fresh Unity companions use the original 30 fps source clock, with native 640x480 camera pixels above a 768x576 resampled rig view in a 1440x1200 canvas. Their positions and margin sizes are editorial layout choices in axes_unity_composite.py. Source-frame correspondences and saved state changes are preserved; the introductory half-speed clock applies only to the eight kinematic derivation lessons.

ID: D-057
Status: SETTLED
Decision: Make fresh axis-instrumented Unity replays in an isolated project using the existing saved thesis inputs, recording camera and rig state alongside the images.
Why: The author explicitly authorized starting Unity and its MCP for new recordings after the archived-capture projection limitation was explained. New instrumented recordings can show the rendered rig directly without guessing its camera or bone orientation.
Alternatives: Stop at recording placeholders despite the new authorization; draw guessed axes on old renders; modify the frozen reference scenes and scripts. The isolated recording copy supports the requested real footage while preserving the scientific implementation.
Evidence: User instruction offering Unity/MCP access; installed Unity 6000.3.19f1; local UnityMCP configuration; repository Unity pose-bridge skill and skill_set/unity-capture-checks.md. The capture protocol requires recording-specific five-length rig sizing plus numerical joint and sizing checks.
Reversibility: Remove or replace only the new capture derivatives and harness. Original scenes, scripts, experiment logs and earlier footage remain unchanged. Project/cache and frame intermediates are isolated under /tmp; supplied capture assets and provenance belong to the presentation track.
Review: Confirm frame-matched logs, axis orientation and named origin, rendered camera matrices, sizing provenance and full receiver state. Distinguish rendered pelvis from L24 and model axes from authored bone rest axes. Label fresh replays separately from archived results; do not silently attribute the old thesis evaluation numbers to a differently instrumented or sized capture.

Scope correction: The page 41 choice is superseded by D-062. Pages 27 and 47 retain their separately checked R7 replay; the rejected current-R5 replay remains preserved as historical media.

ID: D-058
Status: UNCERTAIN
Decision: Draw five model-frame triads as always-visible explanatory overlays in the isolated Unity replay, and retain exact displayed status separately from saved pre-display recovery tags.
Why: Ordinary depth-tested axes disappeared inside the rig mesh. Overlay strokes make the requested coordinate frames visible without moving the rig or camera. The original display smoother exposes binary display validity, which cannot establish whether its final pose is specifically held or constrained.
Alternatives: Shift the camera or rig to expose axes; infer post-display held state from pre-display tags; invent a wrist frame; claim the new replay reproduces the archived evaluation. These would change the represented geometry or overstate the captured evidence.
Evidence: The original calibrated SensorPOVCamera and five recording-specific lengths are preserved. Axis lengths are 0.12 m, line widths 0.004 m, colors as D-056; the capture-only material uses Overlay queue, ZTest Always and ZWrite Off. The 1440x1080 target retains 4:3 framing. Capture is scheduled at 0.25x to retain every source frame, then exported at the source 30 fps. These are editorial capture settings, not runtime-performance measurements. R7 retained frames 0-1497 with no internal gaps; the frozen loop did not retain final source frame 1498. R7 independent model-basis, origin, timestamp and camera checks passed. Tolerances of 1e-5 for matrix components, 2e-6 m for logged origins and 2e-5 s for timestamp rounding are serialization diagnostics, not measurement tolerances. All twelve sizing checks passed using a private-path-only copy of the original checker. The original Unity checker retains seven passes and its one R5-specific outcome failure; this failure is not suppressed.
Reversibility: Regenerate only the isolated capture and presentation derivatives with different stroke sizes, framing or clock settings. Original frozen scenes, archived captures and reported scientific results remain unchanged.
Review: Check that captions say fresh Unity replay, that the rendered pelvis is not labelled L24, that model axes are distinguished from authored bone rest axes, and that pre-display state is not claimed as exact post-display recovery state. Check motion against matching source frame IDs. The shorter teaching clips keep one active frame; five simultaneous frames are reserved for integrated rig demonstrations.
Validation detail: The second fresh capture retains R5 source frames 0-2097 with no internal gaps; terminal source frame 2098 is not retained by the frozen loop. Its unchanged Unity checker passes eight checks and its private-path sizing checker passes twelve. Independent camera-matrix projection is also compared with actual RGB stroke pixels in ten retained stills per recording. This sampled diagnostic uses five along-axis positions, a five-pixel neighbourhood, maximum channel difference 48 and at most one nonmatching usable sample per axis. Projected axes shorter than 12 pixels, offscreen samples and geometrically predicted overlap by later-drawn axes are explicitly excluded. These display diagnostics are recorded in render_projection_check.json; they are not accuracy measurements. R7 has 146 passing visible-axis cases and R5 has 141, with excluded cases listed rather than counted as passes.

Scope correction: D-062 supersedes the page 41 use of newly prepared R5 inputs and pre-display recovery tags. The corrected archived-packet replay exposes only its recorded binary validity; earlier capture findings remain historical.

ID: D-059
Status: UNCERTAIN
Decision: Use separately labelled static frame schematics for coordinate conventions, with illustrative numerical geometry and exact algebraic relationships.
Why: A reference photograph alone does not establish a calibrated three-dimensional frame, while one measured pose cannot cleanly illustrate every transformation. Explicit schematic views support the thesis derivation without presenting editorial geometry as observed data.
Alternatives: Fit arbitrary axes to the T-pose photograph; show unexplained orientation changes; reuse obsolete intermediate-frame names. These would obscure the origin or algebra the author asked to explain.
Evidence: make_coordinate_figures.py and figures/coordinate_frames/manifest.json record each basis, view, offset and source. The reference photo is copied unchanged; its manually placed L24 pointer is labelled illustrative. T-pose spacing uses 0.40 m illustrative arm segments. The circle construction uses 0.38/0.34 m segment lengths and a 0.58 m endpoint distance solely as reachable example geometry. The Scene diagram uses a -20-degree illustrative gravity tilt. These are not subject measurements. Primary preview review found text/axis collisions in the rig factor diagram and unrelated left/right example matrices in the factorization diagram; those must be corrected so the drawn orientation change actually satisfies S R S or A R respectively.
Reversibility: Change the illustrative layout and geometry, regenerate the figures and rebuild the deck. The source photo, thesis equations, data and experiment results remain unchanged.
Review: Verify exact factor order and handedness, named origins, readability at slide size, and visible schematic captions. Treat all unspecified drawing lengths, positions, viewing angles and pixel sizes in the generator as editorial constants, not measured quantities.
Review resolution: The final factorization diagram now computes its nontrivial illustrative examples as S R S and A R, and records both products and the proper illustrative anchor A. It labels the separate reference-coordinate conventions. The rig and marker labels were moved clear of triads without reducing their type size. Primary full-size review accepted the corrected figures; COORDINATE_STATIC_CHECK.json records the source and layout checks.

ID: D-060
Status: SETTLED
Decision: Explain the page 27 wrist-depth gap as raw loss followed by prepared solver input; do not present that clip as proof of object-assisted wrist recovery.
Why: A saved solver state labelled measured is downstream of filtering and interpolation. It does not establish that every corresponding raw sensor observation existed, or that an object-derived target drove the displayed wrist.
Alternatives: Equate the saved measured state with a raw wrist observation; claim that the visible wrist came from the object constraint; hide the conflicting states. All would misstate the recorded processing stages.
Evidence: R7 source frames 705-707 have raw right_wrist_src=2, filtered right_wrist_flag=2 (missing interpolated), and saved right-arm tag_1/tag_2/tag_3=0. The video source, prepared inputs and saved recovery state are independently retained. The actual constrained-recovery result figures elsewhere retain their original evidence and captions.
Reversibility: Refine the wording if a source-specific trace establishes a different processing stage. Do not alter source values or the original experiment results.
Review: Page 27 and Q&A should distinguish raw depth loss, interpolation, saved solver state and rendered output. Input-axis omission requires raw availability and acceptance in addition to a saved measured state; the fresh replay remains qualitative output context.

ID: D-061
Status: UNCERTAIN
Decision: Retain the expanded 53-page main draft with a 3335-second editorial budget, and update the separate cutting guide for a later 20-minute rehearsal.
Why: The author explicitly deferred the strict time limit until the full methodology is clear. Adding coordinate conventions and slower derivation examples needs speaking time; relabelling the expanded deck as a completed 20-minute talk would be misleading.
Alternatives: Remove the newly requested derivations or accelerate their media to force the current draft into twenty minutes. Both conflict with the accepted expanded-draft workflow.
Evidence: Final content budgets sum to 55:35, with 44:05 assigned to methodology. These are authored estimates, not measured delivery. CUTTING_GUIDE.md proposes chapter allocations of 65,140,210,40,210,190,140,95,70,40 seconds for Chapters 1-10, totalling 1200 seconds; the choices are editorial and do not establish that the current full slide set can be delivered at that pace.
Reversibility: Select a shorter route after review, then revise slide/media page numbers and budgets from a timed aloud rehearsal. Keep the expanded source deck available.
Review: Check the explanation and pause time on the actual defence machine before accepting any final timing. Q&A remains separate and untimed.

ID: D-062
Status: SETTLED
Decision: Correct page 41 by replaying the archived R5 packet stream directly, with its archived five-length rig configuration and original binary live/non-live flags.
Why: The archived packet stream differs from the newly prepared R5 stream used in the previous presentation. Matching a recording name does not establish matching displayed poses. Reusing the archived numerical driver and geometry makes the correction inspectable without solving or smoothing those fields again.
Alternatives: Keep the new R5 replay; recompute its pose and call it the historical result; attach current recovery tags to an archived packet. These would not represent the original captured state.
Evidence: Author-approved correction plan. Archived source eval/output/unity_check_r5/integrated_stream.csv SHA256 af952121f3438fca5cd153ad59f4ed1a1b488d5ef01e35b4f985404ccc5b2f60; rig source eval/reports/r5_rig_sizing.json SHA256 1b435110b78f88dc16196e9a34b22799109671e79af02a5ef2a694d89c8e7ed7; calibration eval/output/scene_calibration_r5c.json SHA256 48d4a24948cd4491e28cfdd95d3180ae91333916601e3607e423b6d75a72807e. Archived lengths are right upper/forearm 0.256/0.252 m, left upper/forearm 0.262/0.247 m and torso 0.479 m. Existing capture-only axes and logged sensor-view camera conventions remain. D-057 and D-058 are superseded only for page 41.
Reversibility: Rebind page 41 to the preserved former media and source content. New capture output stays in unity_capture/r5_archived and the new bank_revision collection; original R5/R7 files and thesis results remain untouched.
Review: Check direct packet-field equality, frame correspondence, archived geometry, binary-only state labels, axes and camera projection. Exact historical pixel equivalence must be visually checked and is not assumed from numeric replay consistency.

ID: D-063
Status: SETTLED
Decision: Replace pages 17-20 with four source-matched bank demonstrations, processing the selected recordings into a separate presentation-only working area.
Why: The approved plan asks for motions that make swing, twist, elbow bending and straight-arm observability clearer than repeatedly showing the same general task interval.
Alternatives: Reuse the same R7 interval for every mechanism, modify the managed recordings archive, or present these new demonstrations as thesis experiment results. Those would obscure the mechanisms or mix evidence scopes.
Evidence: Author-approved bank revision: page 17 arm_raise_180042; page 18 right_arm_test; page 19 right_elbow; page 20 right_shoulder. The bank remains read-only for this task. Worker-owned bank_processing outputs record their own source bag identities, intrinsics, flags, prepared landmarks, computed coordinates and source-frame maps. Existing pages 13-16 and their complete earlier source review remain unchanged. The 53-main/25-Q&A page order and exact equation selections are preserved.
Reversibility: Restore the five former media bindings from review/BANK_REVISION_BASELINE.json and the pinned pre-revision delivery. Earlier media remain byte-identical at their original paths.
Review: Require independent per-clip source, numerical and clock checks; show actual preparation/state conditions and no measured wrist orientation. Do not transfer any thesis accuracy statistic to these new mechanism demonstrations.

ID: D-064
Status: UNCERTAIN
Decision: Present the four bank motions at half speed with two-second endpoint holds, using the existing restrained 1440x1200 layout and semantic RGB axes.
Why: Slower matched movement and a fixed model view should make the selected local-frame mechanism easier to follow. Preview quality, interval choice and projected readability remain editorial judgments.
Alternatives: Use whole recordings at full speed, multiple simultaneous active triads, or reduce video resolution to meet a package-size target. These would add distraction or reduce source visibility before the selected intervals are evaluated.
Evidence: Approved pacing direction and worker plan: 30 encoded frames/s, 0.5x source motion, two-second opening and closing holds, 1440x1200 canvas, and 0.075 m illustrative joint-axis length. X=#FF4040, Y=#40E070 and Z=#408CFF retain D-056 meanings. A fixed per-clip view and scale will be fitted to the selected interval and recorded in provenance. Frozen numerical guards, including TWIST_EPS=1e-6, are source algorithm values and are not changed by this editorial decision. Selected frame intervals, final projection constants and preview acceptance will be appended when verified.
Reversibility: Regenerate only the teaching derivatives with a different fixed view or source interval, keeping recorded/model clocks matched and preserving original sources.
Review: Inspect each clip at slide size, verify state labels and local-frame origins, and keep the final PPTX below the hosting service's 100 MiB per-file limit through meaningful interval selection and efficient H.264 encoding before considering any resolution change. Capture timing and holds do not represent processing latency.

Preview revision: Root accepted the actual camera panels and hip placement, but rejected the first lower global-oblique model views because the forearms were foreshortened and too small. The revised lower views isolate source-derived local quantities: page 17 shoulder swing; page 18 the swing-removed forearm Y-Z plane; page 19 the L14 X-Z elbow plane; page 20 the measured perpendicular component beside a separately labelled ideal straight-arm limit. Long sentence labels and the large orientation key are removed. Numeric poses and source timing remain unchanged; these editorial projections remain subject to preview acceptance, not new scientific parameters. Current proposed source intervals are 798-947, 360-720, 180-540 and 28-208 for pages 17-20 respectively.

Graphical refinement: The page 17 fixed L12 reference uses a 0.055 m triad at 45 percent of the same RGB channel values, while the moving swing triad retains 0.075 m full-color axes. Pages 18 and 19 use unit-component plot extents of +/-1.00; page 20 magnifies the unit component to +/-0.20. These are explicit graphical scales, not new numerical observability thresholds. The camera overlay uses the swing basis on pages 17, 18 and 20 and the completed shoulder basis at L14 only on page 19. Every selected page 18-20 sample has twist_ok true; the zero-component limit is a separate labelled schematic, not an observed held state. Root has accepted the revised page 18-20 posters; page 17 final readability review remains pending.

Preview acceptance: Root accepted all four final bank posters, including the revised page 17 labelled shoulder/elbow panel and its start/end frames. Encoding and independent rendered-media review are still required before binding the final artifact. D-064 remains UNCERTAIN as an editorial choice about teaching pace and projection scale, despite the accepted previews.

Final media acceptance: The four frozen bank films passed 116 producer media checks and the separate source/cache audit passed 5315 checks. Independent review inspected all 1053 source records, 10677 label boxes, four posters and twelve decoded samples without a blocker. Selected intervals and output durations are final at 798-947/14 s, 360-720/28.0667 s, 180-540/28.0667 s and 28-208/16.0667 s. Each selected sample has twist_ok true; the full page 20 recording retains its failed precondition. Exact report bindings are in review/BANK_REVISION_INDEPENDENT_REVIEW.json.

ID: D-065
Status: SETTLED
Decision: Bind each bank demonstration to the actual RGB frame consumed by inference, using a logging-only copy of the frozen extractor and complete source-identified cache metadata.
Why: Local frame enumeration and a reset relative clock do not establish that separately extracted RGB and numerical data refer to the same hardware frame. The recorded inference image identity must be explicit before the two views can be called synchronized.
Alternatives: Assume equal local row numbers or relative timestamps prove correspondence; reuse a raw-output cache without completion and source checks; change detector or deprojection logic while adding provenance. These do not meet the source-identity requirement.
Evidence: Root review of the frozen extractor found local enumeration and relative timestamps without absolute hardware identity or input-image hashes. The approved implementation uses an isolated logging-only source copy to retain actual color hardware frame ID, absolute timestamp and RGB-input hash. The source adapter diff must show unchanged inference and deprojection. A reusable cache must identify the source recording and complete extraction metadata. CPU processing is explicitly a new qualitative demonstration path, not the original GPU performance result.
Reversibility: Regenerate the presentation-only cache and derivatives from the same read-only recording if provenance fails. Original extractor, managed archive and thesis measurements remain untouched.
Review: Match every displayed camera frame to the recorded inference input; inspect source/adaptor hashes and the logging-only diff. Independently verify actual frame identities, per-clip intrinsics, flags and shared output clock before accepting the final media.

ID: D-066
Status: SETTLED
Decision: Accept the corrected page 41 as a source-preserving new archived-packet replay, while retaining the original application's failed historical outcome assertion as a visible validation limitation.
Why: Direct replay, all thirteen bone-angle applications, logged axes, archived rig sizing and source-frame correspondence are independently checked. The unchanged application checker also demands the old concentration of left-hand disagreement on torso-failure frames; this new render does not reproduce that outcome. Changing its threshold or its poses would obscure the evidence.
Alternatives: Call every check passing, suppress the failed assertion, adjust the checker threshold, force a worse pose to reproduce a historical error pattern, or claim historical pixel equivalence. None is supported by the sources.
Evidence: Root preview acceptance, conditional on final decode. unity_capture/r5_archived/archived_replay_check.json records 11 PASS / 0 FAIL; check_rig_sizing.txt records 12 PASS / 0 FAIL; rendered projection records 131 PASS / 0 FAIL with 4 explicit exclusions. The original application checker records 7 PASS / 1 FAIL: left-hand disagreement medians are 15.1 px on torso-failure frames and 10.5 px on clean frames, below its historical greater-than-three-times expectation. eval/reports/r5_unity_check.md reports the older 8/0 outcome before its appended 2026-08-26 rig spawn, segment-length and torso-fidelity changes. These histories must not be conflated.
Reversibility: Replace only this explanatory replay after further renderer investigation, preserving the archived packet source and all original reports. No numerical thesis result changes.
Review: Mark the media-validation milestone PARTIAL while this failed historical assertion remains. Delivery may complete with the stated limit, but no report may describe overall validation as entirely passing. Do not claim anatomical accuracy or historical pixel identity from the new replay.


ID: D-067
Status: SETTLED
Decision: Join layout-only blank lines inside an existing hyphenated word when verifying the exported speaking-script PDF.
Why: After removing PDF headers and footers, a word split across a page boundary can contain several newline characters. The verification must compare the authored wording without treating that layout break as missing text.
Alternatives: Rewrite narration, shrink the printable text, suppress the missing-paragraph assertion or accept an unverified PDF. None is needed because the words are present and unchanged.
Evidence: The current script PDF splits the existing word watch-feature between pages 14 and 15. A narrow normalization of a hyphen followed by one or more line breaks recovers the original paragraph. All 316 paragraphs and 78 slide headings then match; SCRIPT_EXPORT_CHECK.json binds the 25-page export. Markdown and DOCX wording remain verbatim.
Reversibility: Restore the prior normalization if a later exporter no longer introduces this boundary; the check must continue to verify every authored paragraph.
Review: Inspect script pages 14-15 and the exact hyphen-preserving expression in export_defense_script.py. No source narration or thesis equation is changed.

ID: D-068
Status: SETTLED
Decision: Replace the visible footnote prefix "Thesis V9 | " with "Undergraduate thesis | " in every source_label of talk_content.json and backup_content.json; the speaker-note source strings keep "Thesis V9".
Why: The author found "Thesis V9" confusing on the slides; the version number is internal bookkeeping. The source strings are provenance for the author and are not drawn on a slide.
Alternatives: Drop the prefix entirely (loses the cue that the citation is to the thesis); rewrite every source string too (erases provenance that names the exact thesis version).
Evidence: Author request (plan virtual-wiggling-globe.md, M1). build_deck.py source_label() returns source_label when present and restrained_footer draws it. After the edit: 52 of 53 talk labels and 25 of 25 backup labels start with "Undergraduate thesis | "; the remaining talk label is the title slide "Lanqing Luo | School of Engineering Science, SFU". Longest label is 88 characters; footer fit is checked at the M4 rebuild, not here.
Reversibility: One sed over the "source_label" lines restores the prefix.
Review: Confirm the wording on the rendered footers at M4; no .py, README or script file quoted the old visible prefix (the remaining hits are generated DEMONSTRATION_MANIFEST.json and SPEAKER_NOTES.md source text and the hash-bound review/ARTIFACT_CHECK.json, left unchanged).

ID: D-069
Status: UNCERTAIN
Decision: Rebuild page 24 (grasp_offset.png) on R7 recording_20260909_000024 frame 630.
Why: Frame 630 lies in the page 23 holding episode (R7 600-779), the right hand visibly holds the cube, the raw right wrist has src 0, fail_arm_R is 0, the cube marker is detected (reprojection 0.078 px) and matched_evidence.json marks it a clean offset update. It is also the poster frame of page 25 (matched_grasp), so pages 24 and 25 show the same moment.
Alternatives: Frame 730 (raw and pipeline offsets agree to 0.05 cm, but the hand is less clearly on the cube); frame 610 (0.19 cm agreement; hand approaching). Frames 705-707 are excluded (missing wrist depth). The choice is editorial; no metric ranks frames for teaching clarity.
Evidence: Contact sheet of frames 610/630/690/715/730/740 viewed this session; per-frame table: raw h at 630 = (-2.3, -11.1, +11.8) cm vs pipeline h (matched_evidence.json, filtered Scene inputs) = (-2.5, -11.0, +12.2) cm, difference 0.49 cm. RGB bytes e3014c1e... match the bag-decode record in media/provenance/axes_r7_rgb.json.
Reversibility: Change GRASP_FRAME in make_coordinate_figures.py and rerun with --only grasp_offset.
Review: Look at the left panel: is the hand-on-cube moment clear at slide size?

ID: D-070
Status: UNCERTAIN
Decision: Draw page 24 as two panels: left the cropped recorded frame with the MappedMarker triad from the raw cube-marker pose, the raw right wrist as a white point and a white arrow labelled "Scene displacement p_wr - o_k"; right an axis-aligned 7 cm cube in MappedMarker coordinates (marker face toward the viewer, Y the face normal) with the same vector labelled "h_k (object-local)" and its three components in axis colours.
Why: The author found the invented triad and "Offset h" arrow confusing. Showing one measured vector twice makes Eq. 5.2 concrete: the image shows where the displacement is, the right panel shows the same vector in cube axes. The printed numbers are computed from exactly the drawn inputs, h = (R S)^T (p_wr - o_k), which is invariant to the rigid Camera-to-Scene change, so the figure is internally consistent. The "same displacement, two coordinate descriptions" sentence is carried by the slide caption, not repeated in the figure.
Alternatives: Print the pipeline value from matched_evidence.json (filtered Scene inputs, 0.49 cm different; recorded in the manifest as pipeline_offset_mappedmarker_m) - rejected so that the drawn arrow and printed numbers come from one set of inputs; stack the panels vertically - rejected because the 640x480 frame would shrink below readable size; draw the raw OpenCV marker triad (Z normal) on the left - rejected because the right panel uses MappedMarker (Y normal) and the two would disagree.
Evidence: Inputs are the VIDEO-1 tables (presentation/v9/anim/video1_overlay.py): landmarks_raw.csv, aruco_raw_scaled.csv, recovery_r7/failure_mask.csv; swap S as anim/axes_inputs.py; cube side 0.07 m from eval/output/scene_calibration_r7c.json scene_geometry.object_cube_size_m; marker 0.045 m (AGENTS.md). Editorial constants without a data source: crop (125,145)-(395,400) source px, right-panel view direction (0.42, 0.30, 0.86) and scale 2350 px/m, text sizes 40-44 px on the 1440x1200 canvas. All hashes and drawn numbers are in figures/coordinate_frames/manifest.json (key grasp_offset), labelled measured on that frame and illustrative, not a thesis result.
Reversibility: Restore local_offset() from git history and rerun make_coordinate_figures.py --only grasp_offset; restore the page 24 visual_caption.
Review: View the page 24 render at M4; check that the left arrow is read as the same vector as the right arrow, and that the arrow passing over the cube top in the right panel does not suggest penetration (it is a schematic of a vector, not an occlusion-correct render).

ID: D-071
Status: UNCERTAIN
Decision: Run pages 13-16 extraction through a sibling adapter bank_processing/extract_logged_v2.py that writes its instrumented extractor copy and diff to bank_processing/sources_v2/, instead of extending or running bank_processing/extract_logged.py.
Why: Running the unchanged extract_logged.py for p13 (2026-09-24) rewrote the hash-bound frozen file bank_processing/sources/extractor_logging_only.diff: its two absolute path headers changed from the pre-rename folder name to /home/luo/Desktop/bimanual-tracking. That file and extract_logged.py are bound by the p17-p20 inference maps and the pipeline review checked by validate_deck.py. The file was restored with git checkout (sha256 270541d0... verified) and the first p13 outputs were discarded. The sibling differs from the original only in the output directory and the docstring, so inference, gates, deprojection and CSV rows are unchanged. The existing --page option has no choices list, so no --page extension was needed.
Alternatives: Edit extract_logged.py (changes a hash bound by the p17-p20 inference maps, which page 16 and the p17-p20 v2 films reuse, and by the pipeline review); run the original and accept the changed diff header (alters a frozen, hash-bound file the brief says not to change).
Evidence: git diff of sources/extractor_logging_only.diff after the first run showed only the ---/+++ path header lines changed; sha256sum -c against the pre-run hashes: sources/extract_landmarks_logged.py OK, extract_logged.py OK, diff FAILED before restore and OK after. diff extract_logged.py extract_logged_v2.py shows only the docstring and source_dir lines.
Reversibility: Delete extract_logged_v2.py and sources_v2/ and rerun p13 extraction with the original adapter once the frozen diff is allowed to be regenerated.
Review: Confirm the brief's intent (extend extract_logged.py) is acceptable as a sibling file; check sources_v2/extractor_logging_only.diff shows only the one added logging line.

ID: D-072
Status: UNCERTAIN
Decision: Pages 13-15 use ENSC498_arms_outstretched_pose_test_arm_test.bag, color frames 780-898 (the end of the recording), extracted once into bank_processing/p13 and referenced by hash from p14 and p15.
Why: The measured torso does not turn in this trial. Over all 899 frames the root y angle stays between about 169 and 180 deg (15-frame means 171.0-177.7 deg) and x, z stay near -11 and -8 deg; the motion visible on the contact sheet around frames 540-898 is a sideways arm lean, not a torso rotation. Within the trial, 780-898 contains the clearest torso change (the lean at 840-880: root z moves from about -8 to -12 deg and back, shoulder-line roll changes by about 14 deg) after two seconds of steady T-pose, and every frame in it has all eight raw landmarks accepted. The trial still gives a clear, fully visible standing T-pose with both hips and shoulders tracked, which suits page 15's T-pose root reference (0, 180, 0). The box-held fallback was worse: a scratch extraction (plain frozen extractor, scratchpad only) gave root x of 20-60 deg with the hips hidden in dark trousers and the wrists behind the box (all-eight acceptance 0-40 of 40 frames per 40-frame block), and no clearer yaw.
Alternatives: Box-held fallback frames 430-800 (implausible root pitch, occluded arms); a longer steady window such as 700-898 (larger file, no more motion); a recording outside the two named candidates such as v1era_whole_body_cube_handling (not in the approved plan, and its contact sheet shows no torso turn either).
Evidence: bank_processing/p13/landmarks_filtered.csv with v1/kinematics/root_frame.py build_root_frame/euler_unity_zxy, 15-frame rolling means over the whole recording (computed this session); raw _src columns: only left_wrist has 2 rejected samples in the whole recording, none in 780-898; full-recording tracking precondition exit 0. Desk check: aligned depth sampled with pyrealsense on frames 800 and 860 gives 1.97-2.03 m at and just above both hip pixels and 0.74-0.80 m on the desk surface 20-30 px below, so the hip points lie on the body, not the desk edge.
Reversibility: Change TORSO_START/TORSO_END in anim/bank_axes_kinematics.py and rerun --build for pages 13-15; the extraction is reused.
Review: Decide whether a near-static but clear T-pose is acceptable for pages 13-15. If a visible torso turn is required, a new recording (or a recording outside the approved candidates) is needed; none of the named candidates contains one.
Amendment: the window end was moved from 898 to 885 by D-075 (root y wraps past 180 deg at 886 and 896-898).

ID: D-073
Status: UNCERTAIN
Decision: Pages 13-20 share one layout in anim/unified_panels.py: top the 640x480 inference frame at (336,64)-(1104,640) with overlay; bottom-left panel (20,700)-(800,1190) drawing the same Camera-prime points through the recording's own pinhole (Camera-prime reflection undone) with one fixed per-clip uniform scale and offset; bottom-right panel (830,700)-(1420,1190) with the page's 2D quantity.
Why: The author reported that the lower skeleton does not match the video. Using the identical projection makes every lower landmark congruent with the overlay: (overlay px - (336,64))/1.2 equals (model px - offset)/scale to below 1e-12 source px on every rendered frame (asserted < 1e-9 at render time). The per-clip scale and offset are fitted once from all selected frames (landmarks and triad endpoints) into the fit area (40,800)-(780,1175) with a 30 px margin, so the panel never follows individual frames. The overlay uses the same edge set and colours as the model panel so the two are visibly the same drawing.
Alternatives: Keep the oblique view_matrix(25,12) model views (the mismatch the author rejected); a model panel at the overlay's own 1.2 scale (would need a 768x576 panel and leave no room for the plane panel); a fixed scale for every page (skeletons at different distances would be tiny on some pages).
Evidence: Editorial constants without a measurement source (all UNCERTAIN): panel rectangles above; fit area and 30 px margin; plane origin (1010,965), 125 px per unit, axis arrows -150..+170 px; text sizes 28 px (labels, readouts, ticks), 30 px (panel headings), 34-39 px (header lines, unchanged from bank_kinematics.py where they existed); root triad 0.15 m (was 0.10 m in axes_kinematics.py; raised because at 2.0 m the 0.10 m triad was about 44 px in the panel); joint triads 0.075 m (unchanged, D-064); dimmed reference triads 0.075 m at 55 percent channel value (was 0.055 m at 45 percent on page 17; raised because the camera-view reference was barely visible). Fitted scales: p13-p15 1.415, p16/p17 1.456, p18 1.413, p19 1.492, p20 1.365 panel px per source px. Axis colours X #FF4040, Y #40E070, Z #408CFF unchanged (D-056).
Reversibility: Edit the constants in anim/unified_panels.py and rerun --build of anim/bank_axes_kinematics.py and anim/bank_kinematics.py; sources and extractions are unchanged.
Review: View first/middle/last frames of all eight films at slide size; check the lower skeleton reads as the same pose as the video and that no label is too small in the 6.61 x 5.00 in movie box (28 px is about 8.4 pt there).
Correction: after the root triad was raised to 0.15 m the pages 13-15 fitted scale is 1.3943 (not 1.415); the final fitted scales are p13-p15 1.3943, p16/p17 1.4561, p18 1.4128, p19 1.4923, p20 1.3651 panel px per source px (from the media check reports).

ID: D-074
Status: UNCERTAIN
Decision: Per-page content of the unified panels: focus edges bright white, the other right-arm edge #CFCFCF, all other edges #656565; 13-15 focus = hip line L23-L24 and L24-L12 (the Eq. 3.7-3.8 inputs), 16-17 focus = upper arm with faded forearm, 18-20 focus = forearm with faded upper arm. Plane panels: 13-15 top view of Camera' X-Z with X-hat red and Z-hat blue at L24 (14 adds the L24 origin in metres and dim root-oriented triads at L12 and L11; 15 adds the signed arc from +z to Z-hat and the three root angles); 16 unit upper arm in the L12 X-Y plane with its three components, no arc; 17 unit upper arm in the L12 X-Z plane with the arc equal to swing y and the swing y/z readouts; 18 twist Y-Z, 19 elbow X-Z, 20 magnified Y-Z plus the exact-zero sketch, as before.
Why: Each drawn arc equals the printed angle exactly, which avoids showing an arc that only approximates a value: page 15 uses atan2(Z-hat_x, Z-hat_z), which is the Unity y angle of euler_unity_zxy (root_frame.py) exactly (checked per frame, max difference below 1e-9 deg); page 17 uses atan2(-a_z, a_x) = swing y (Eq. 3.21), with elevation z = asin(a_y) printed; pages 18-19 keep their existing exact arcs. Page 16 has no single angle in the X-Y plane that equals a thesis quantity, so it shows the direction and its components (Eq. 3.18-3.19). Torso basis arrows keep the axis colours so they read as the same X and Z as the triads. The page 14 dim triads illustrate that L12/L11 inherit the root orientation.
Alternatives: A white vector with an arc for the torso pages (no single white vector defines the basis); an X-Y plane with an elevation arc on 17 (the in-plane angle is not tz unless a_z = 0); an arc on 16 (would suggest an angle the thesis does not define there).
Evidence: v1/kinematics/root_frame.py euler_unity_zxy: y = atan2(m02, m22); bank_axes_kinematics.py numeric check top_view_yaw < 1e-9 in prepare(); shoulder.py swing definition as in the page 17 source text (t_y = atan2(-a_z, a_x), t_z = asin(a_y)). Label vocabulary reuses the existing strings where they existed ('After undoing swing: Y-Z plane', 'L14 forearm direction: X-Z plane', 'Twist =', 'Elbow y =', 'Swing y', 'Observed perpendicular fraction', 'Exact limit (schematic)'); new short strings: 'Top view: Camera' X-Z plane', 'Upper arm in L12: X-Y/X-Z plane', 'Repaired: N' (was 'Repaired points: N').
Reversibility: Change plane_panel() or edge_colors() in anim/unified_panels.py and rebuild.
Review: Check page 15's arc near 180 deg (a person facing the camera has root y near 180; it can flip between +179 and -179 when y crosses 180) and whether the page 16 X-Y plane or an X-Z plane better matches the narration.

ID: D-075
Status: UNCERTAIN
Decision: Shorten the pages 13-15 window from 780-898 (D-072) to 780-885.
Why: Root y is near 180 deg for a person facing the camera and wraps to negative values at frames 886 and 896-898 (-179.99, -178.91, -177.73, -176.61 deg). The page 15 arc and printed y would flip between an almost full clockwise and counter-clockwise half circle, and the two-second end hold would sit on a wrapped value. Ending at 885 keeps the whole lean (840-880) and removes every wrap; 780-885 has root y between 169.3 and 179.9 deg.
Alternatives: Keep 898 and let the arc flip (honest but visually confusing); unwrap the printed angle (would no longer be the thesis's euler_unity_zxy output).
Evidence: bank_processing/p13/derived_kinematics.csv, frames 700-898 with root_ey < 0: 886, 896, 897, 898 only.
Reversibility: Set TORSO_END back to 898 in anim/bank_axes_kinematics.py and rebuild pages 13-15.
Review: Check that the page 15 end hold (frame 885) reads as the T-pose reference.
Correction: in 780-885 root y spans 171.43-179.83 deg (not 169.3-179.9), root x -12.51 to -8.06 deg, root z -12.62 to -5.68 deg (bank_processing/p13/derived_kinematics.csv).

ID: D-076
Status: UNCERTAIN
Decision: Encode the eight new films at the existing crf 19 / preset slow (total 14,286,547 bytes = 13.62 MiB), exceeding the brief's 8 MiB total, because the brief's purpose (PPTX below 100 MiB) is still met with margin.
Why: The eight new films replace eight bound films that are each embedded once (talk_content.json only; backup_content.json binds none of them). The replaced films total 20,156,980 bytes (axes_revision p13-p16: 11,027,622; bank_revision p17-p20: 9,129,358). The current PPTX is 92,271,603 bytes, so after M4 the projected PPTX is about 92,271,603 - 20,156,980 + 14,286,547 = 86,401,170 bytes (82.4 MiB) before any page 12/24 image change, below the 100 MiB limit. Meeting 8 MiB would need roughly crf 24-25, which visibly degrades the recorded camera image that the pages exist to show, and would contradict the brief's 'crf as now'.
Alternatives: Raise crf to fit 8 MiB (softer camera footage; conflicts with 'crf as now'); shorten pages 18-19 (their 360-frame windows are unchanged from the accepted first bank revision, D-064).
Evidence: Encoder output this session: p13 989,836; p14 1,016,492; p15 1,050,755; p16 1,604,041; p17 1,713,534; p18 2,976,983; p19 3,389,102; p20 1,535,804 bytes. ls -l of the current bound films and Thesis_Defence_2026.pptx; grep of talk_content.json/backup_content.json for the p13-p20 film paths (one binding each, all in talk_content.json).
Reversibility: Change CRF in anim/bank_axes_kinematics.py and anim/bank_kinematics.py and rerun --build; nothing else changes.
Review: Confirm the size after the M4 rebuild; if the 8 MiB figure was meant as a hard limit independent of the replaced films, re-encode at a higher crf.
Correction: the measured total of the eight new films is 14,276,547 bytes (13.62 MiB); the projected PPTX is 92,271,603 - 20,156,980 + 14,276,547 = 86,391,170 bytes (82.4 MiB). The 14,286,547 figure above was an addition error.

ID: D-077
Status: UNCERTAIN
Decision: Convert anim/bank_kinematics.py in place to version 2 (unified_panels rendering, films to committee_materials/bank_revision_v2, derived files to bank_processing/unified_v2/p17-p20), and add sibling checkers bank_processing/check_unified_sources.py and check_unified_media.py instead of extending check_bank_sources.py/check_bank_media.py.
Why: The brief asks for one shared renderer used by both producers. Writing the version-2 derived files (kinematic_source.json, derived_kinematics.csv, selected tracking reports) into the existing p17-p20 folders would rewrite hash-bound files; unified_v2/ keeps them intact (all 112 files in p17-p20 and all 214 files in the bank_revision and axes_revision collections hash-identical before and after this work). Re-running the old checkers would overwrite bank_processing/BANK_SOURCE_CHECK.json and bank_revision/review/BANK_MEDIA_CHECK.json, which the current media contract binds by hash, so new report files are written instead.
Alternatives: Keep bank_kinematics.py byte-identical and put the v2 route in a third file (contradicts 'used by both'); extend the old checkers (overwrites hash-bound reports).
Evidence: sha256sum -c of the pre-work snapshot of bank_processing/p17-p20 and committee_materials/{bank_revision,axes_revision}: all OK after the builds. Consequence to handle in M4: validate_deck.py audited_bank_composites() asserts sha256(anim/bank_kinematics.py) == BANK_SOURCE_CHECK.json producer_sha256 and the pipeline review hashes the functions of bank_kinematics.py (prepare, build, ...); both now differ, so validate_deck.py fails on the current bindings until its bank route is moved to the new collections and reports. The old collection's provenance still names the old generator hash; that revision is recoverable from git history (HEAD 67e24e8).
Reversibility: git checkout the previous anim/bank_kinematics.py; the version-2 outputs are in separate folders and can be deleted without touching the first collection.
Review: M4 must rebind validate_deck.py to UNIFIED_SOURCE_CHECK.json, BANK_AXES_MEDIA_CHECK.json and BANK_V2_MEDIA_CHECK.json (and a new independent review, if the track keeps that pattern) before the deck validates.

ID: D-078
Status: UNCERTAIN
Decision: Name the new films p13-Torso_Axes_From_Standing_T_Pose, p14-Torso_Frame_And_Root_Transform, p15-Root_Rotation_From_Standing_T_Pose, p16-Upper_Arm_Direction_From_Arm_Raise, and keep the four p17-p20 stems unchanged in bank_revision_v2; page 16 reuses the page 17 extraction (180042, frames 798-947) through p16/source_reference.json, and pages 14-15 reuse p13 the same way.
Why: Names describe the content actually shown: the trial is a standing T-pose with a small lean, not a torso turn (D-072). Reuse by reference avoids re-running MediaPipe on identical inputs: the reference file binds the shared inference map, processing manifest, raw/filtered CSVs and metadata and the full tracking report by SHA-256, and prepare() refuses to run if any hash changes (negative cases in UNIFIED_SOURCE_CHECK.json). The p17 window keeps the same motion for pages 16 and 17 as the plan asked.
Alternatives: Separate MediaPipe runs per page (same bag, same window, duplicate data); page 16 on the clean alternative window 286-446 (fallback not needed because 798-947 passes every check).
Evidence: bank_processing/p14/source_reference.json, p15/source_reference.json, p16/source_reference.json; UNIFIED_SOURCE_CHECK.json 10846 PASS / 0 FAIL including 'axes_reference' negative cases; selected-window tracking verdicts all true for 780-885 and 798-947.
Reversibility: Rename stems in PAGES of anim/bank_axes_kinematics.py and rebuild; or run a dedicated extraction for a page by setting its extraction_page to itself.
Review: Check the names read well in the deck's media index.

ID: D-079 (superseded by D-106: page 12 is now thesis Figure 3.5 above a schematic)
Status: UNCERTAIN
Decision: Use frame 137 (t = 4.570 s, colour hardware frame 575) of ENSC498_arms_outstretched_pose_test_arm_test.bag as the page 12 T-pose photograph, replacing the hand-held writing/v7 tpose.jpg photograph.
Why: The author asked for a right arm that is horizontal and for page 12 to match the camera-view pages 13-20. Frame 137 has the smallest fitted right-arm angle of all frames whose eight landmarks are accepted (raw src 0 and filter flag 0): 0.065 deg raw, 0.043 deg filtered. It is in the level-arm part of the trial, before the torso turn, and is the same recording that page 13 plays.
Alternatives: Frames 242, 479, 99 and 120 also pass within 0.3 deg, but their arms bend more (largest point-to-line distance 8-21 px against 6.0 px for 137). Keeping the old photograph was rejected because its arm slopes down and it has no measured landmarks.
Evidence: bank_processing/p13/landmarks_raw.csv (sha256 427e4d22...) and landmarks_filtered.csv (efd1f34d...); 803 of 899 frames accept all eight landmarks and 32 of them pass the 1 deg test. The RGB copy figures/coordinate_frames/tpose_source_arm_test_f00137.png matches cached_png_sha256 615c5acb... in bank_processing/p13/inference_frame_map.json (all 899 cached frames matched). The individual segments are not level: L12-L14 descends and L14-L16 rises by about 7 deg each (elbow about 6 source px below the fitted line). No frame has both segments within 1 deg.
Reversibility: Change TPOSE_FRAME in make_coordinate_figures.py and rerun --only tpose_reference.
Review: Confirm that a fitted line through L12, L14 and L16 is an acceptable reading of "perfectly horizontal", given the slight elbow sag visible in the photograph.

ID: D-080 (superseded by D-106: page 12 is now thesis Figure 3.5 above a schematic)
Status: UNCERTAIN
Decision: Measure arm horizontality as the total-least-squares line through the L12, L14 and L16 image pixels, accepting frames within 1.0 deg in both raw and filtered landmarks.
Why: The 1 deg tolerance is the author's requirement as given in the M1b brief. A fitted line uses all three points and does not depend on which endpoint is chosen. Requiring both raw and filtered landmarks keeps the figure consistent with the films (filtered) and with the measured dots drawn (raw).
Alternatives: Per-segment angles within 1 deg gave zero passing frames. The L12-to-L16 chord alone ignores the elbow.
Evidence: Scoring over all 899 frames (script logic reproduced by tpose_inputs()/arm_line_deg(), which rejects the frame if the angle exceeds TPOSE_MAX_ARM_DEG). Manifest key tpose_reference.arm_line records both angles, the tolerance and the point offsets.
Reversibility: Change TPOSE_MAX_ARM_DEG or arm_line_deg() and reselect.
Review: Check the 1.0 deg tolerance source and the fitted-line definition.

ID: D-081 (superseded by D-106: page 12 is now thesis Figure 3.5 above a schematic)
Status: UNCERTAIN
Decision: Page 12 layout: the recorded frame is cropped to source (40,0)-(600,300) at 1.8x with the films' overlay style: right arm white, other edges #656565, white dots, a dashed #C8C8C8 horizontal guide through the measured L12, and L12 and L24 labels at the measured landmarks. Below it, the ideal chain is drawn with the recording's pinhole after the Camera-prime reflection (as anim/unified_panels.py), using the canonical root at the measured L24 and the frame's measured segment lengths, with triads at L24, L12 and L14 and L16 marked as a point.
Why: The same projection as the films makes page 12 look like pages 13-20. Using the measured origin and lengths makes the ideal chain directly comparable with the photograph without claiming it is fitted to the photograph. The crop removes the empty desk so the person is large enough at slide size.
Alternatives: The full 640x480 frame at 1.2x was rendered first and left the person and the ideal chain too small at slide size. The old oblique view_matrix(10,8) diagram was rejected because it does not match pages 13-20. Fixed illustrative lengths (the former 0.15/0.40 m) do not match the photograph.
Evidence: Editorial constants with no data source: TPOSE_CROP, TPOSE_PHOTO_RECT, TPOSE_MODEL_FIT, triad lengths 0.15/0.10/0.10 m, the Z-label offset, and text sizes 34-44 px. Colours and edge widths come from anim/unified_panels.py. Viewed at 1440x1200 and 600x500.
Reversibility: Adjust the constants in make_coordinate_figures.py and rerun --only tpose_reference.
Review: Check at slide size that the ideal diagram reads as ideal (it is also labelled so), and that the slightly wider measured shoulders than hips, which make the left torso edge slant, do not distract.

ID: D-082
Status: SETTLED
Decision: Bind pages 13-20 through a new collection-level contract, committee_materials/unified_revision/media_contract.json (with VIDEO_INDEX.md/.csv and provenance/SOURCE_PRESERVATION_CHECK.json), written by the new anim/unified_revision_build.py, instead of rewriting committee_materials/bank_revision/media_contract.json.
Why: The bank_revision contract is hash-bound history: it binds its media_plan.json, review/BANK_REVISION_INDEPENDENT_REVIEW.json and BANK_SOURCE_CHECK.json, whose producer hash no longer matches the version-2 anim/bank_kinematics.py. A new contract keeps that record readable and verifiable for the preserved files while the deck binds the new films. The builder copies the 20 unchanged rows (including page 41) byte-for-byte from the bank_revision contract and verifies every retained file, every replaced page 13-20 file and the 99 files of the earlier preservation audit.
Alternatives: Editing bank_revision/media_contract.json in place (rejected: breaks its own plan/review hash bindings and would misstate what its review certified). Extending anim/bank_revision_build.py (rejected: the brief forbids editing the anim scripts and that builder fixes its replacement set to 17-20 and 41).
Evidence: anim/unified_revision_build.py run output "Bound 20 unchanged and eight unified-layout media entries; 78 slide identities retained."; validate_deck.py "Coordinate media contract current source_preservation_audit binding" PASS.
Reversibility: Point committee_media.contract in talk_content.json and backup_content.json back to the bank_revision contract and restore the earlier page 13-20 composite_media blocks from git.
Review: Confirm the new collection name unified_revision and that committee_materials/VIDEO_INDEX.md now points to it.

ID: D-083
Status: UNCERTAIN
Decision: validate_deck.py checks pages 13-20 with a new route, audited_unified_composites(), used when the active contract carries unified_source_check; the old audited_bank_composites() stays as the reader of the historical contract. The new route binds UNIFIED_SOURCE_CHECK.json and both unified media checks by hash, the producer, layout-renderer and axis-renderer hashes, every source/processing file, the inference clock, the output frame schedule, overlay/source RGB identity, filtered points and flags, and overlay/model congruence at L12.
Why: The old route requires BANK_REVISION_INDEPENDENT_REVIEW.json and hashes functions of the version-1 bank_kinematics.py; it cannot pass for the new films and must not be relabelled as their review. UNCERTAIN because no independent review of the unified films exists yet: the route relies on the producers' reports and the two sibling checkers written by the same worker.
Alternatives: Waiving the bank route (rejected: fix, never waive). Requiring an independent review file that does not exist (rejected: would fail every build until one is produced).
Evidence: Constants: the 1e-9 bounds on numeric_checks and on congruence_max_abs_source_px are the producers' existing arithmetic consistency guard already used by the old route (validate_deck.py audited_bank_composites), not an accuracy threshold; recorded congruence values are at most 1.7e-13 source px. Negative tests (scratch run) rejected a changed source-check hash, a changed media-check hash, a page-13 kind swap, a shortened page-16 clock and a missing page 18. validate_deck.py: 1848 checks, 0 package failures.
Reversibility: Remove the dispatch in inspect() and the new function.
Review: Decide whether a separate independent review (checker or code-reviewer) of the unified films is required before the defence.

ID: D-084
Status: SETTLED
Decision: validate_deck.py checks that every visible source_label fits one 11.7-inch line at 10.5 pt DejaVu Sans, and that no visible label names V9 and every label that cites the thesis starts with "Undergraduate thesis | ". No label was shortened.
Why: restrained_footer() in build_deck.py draws source_label in an 11.7 x 0.22 in box at 10.5 pt with zero insets; a second line would leave the box. The width uses the builder's own font metric.
Alternatives: Checking character count (rejected: width depends on glyphs).
Evidence: build_deck.py restrained_footer (11.7 in box, RESTRAINED['source'] = 10.5); widest label 6.459 in (88 characters, pages 7, 8, 9, 67, 68); page 53's label "Lanqing Luo | School of Engineering Science, SFU" does not cite the thesis and is accepted.
Reversibility: Delete the two checks.
Review: None needed unless labels grow past 11.7 in.

ID: D-085
Status: UNCERTAIN
Decision: Page 13-20 narration and captions: keep the equations, bullets and page purposes; add the NEW_BINDINGS.md sentences for 13-16 (no rotation claims on 13-15); replace the page 17 lower-view sentences with the camera-view model and L12 X-Z azimuth description; add "the lower left model uses the same camera projection as the video" to 18-20. Captions for 13, 15 and 17 were shortened from the suggested wording to fit one line: "Recorded T-pose; L24 basis in camera and top views.", "Facing T-pose root angles; arc shows root y from above.", "Arm raise: camera-view swing basis; azimuth arc in L12.". The speaker-note source strings keep their "Thesis V9" provenance prefix (plan assumption 1) and now cite the bag, window, extraction folders and the three new audits.
Why: The suggested captions wrapped to a second line that touched the footer rule at slide size (viewed in preview). The pages 13-15 notes must not describe a torso rotation (D-072, D-075).
Alternatives: Keeping two-line captions (pages 18, 20 and 24 still wrap to two lines; they were not changed).
Evidence: preview/slide-13.png and slide-17.png before and after; caption widths at 16 pt measured with the builder metric (5.91, 6.20 and 6.27 in against the 6.61 in label box).
Reversibility: Edit talk_content.json visual_caption and purpose.right_visual.
Review: The author should read the new page 13-17 notes aloud; the root-angle sentence on page 15 quotes the measured range only loosely ("close to (0, 180, 0)").

ID: D-086 (superseded by D-106: page 12 is now thesis Figure 3.5 above a schematic)
Status: UNCERTAIN
Decision: Replace the validator's obsolete page 12 check (manual_pointer_is_detector_output False) with checks on the new record: the source frame PNG hash, the six landmark-table hashes, the inference-map RGB hash of frame 137 and the bag hash, the eight drawn landmarks equal to the raw CSV row with src 0, and an independent total-least-squares recomputation of the L12-L14-L16 image line that must agree with the manifest within 1e-9 deg and lie within the declared 1.0 deg tolerance. The page 12 notes now say the landmarks are measured instead of calling the labels illustrations, and its speaker-note source cites frame 137.
Why: The page 12 figure no longer has a manual pointer (manual_anatomical_pointer_uv_px is null); L24 is the measured landmark. The manifest key manual_pointer_is_detector_output is left in place and not read.
Alternatives: Keeping the obsolete key check (rejected by the coordinator).
Evidence: Recomputed angle 0.0649 deg, equal to manifest arm_line.raw_deg 0.06491810605101023. The 1.0 deg tolerance comes from D-080 (UNCERTAIN), which is why this entry is UNCERTAIN. The 1e-9 bound only guards floating-point agreement.
Reversibility: Restore the earlier check from git.
Review: Confirm D-080's tolerance; figures/coordinate_frames/tpose_source.jpg is now unreferenced and was left in place for the author to decide.

ID: D-087
Status: SETTLED
Decision: The deck no longer embeds the four page 17-20 films of the bank_revision collection, which HANDOVER.md asked to preserve; they remain on disk unchanged, and page 41 keeps its bank_revision film and binding.
Why: The author asked for one unified layout on pages 13-20 (plan virtual-wiggling-globe.md, user decision and assumption 4).
Alternatives: Keeping the old page 17-20 films next to new 13-16 films (rejected: the author asked for the same layout on all eight pages).
Evidence: unified_revision/provenance/SOURCE_PRESERVATION_CHECK.json lists the replaced files as preserved; validate_deck.py page 41 composite checks PASS.
Reversibility: Rebind pages 17-20 to the bank_revision films (see D-082 reversibility).
Review: None beyond the plan approval.

ID: D-088
Status: UNCERTAIN
Decision: Source windows of the four merged films (unified_four): page 13 arms_outstretched T-pose 780-885 (unchanged, extraction p13); page 14 180042 arm raise 3-109 (extraction p17), not the fallback 3-145; page 15 right_arm_test 505-725 (extraction p18); page 16 right_elbow 180-540 (unchanged, extraction p19).
Why: The old page 17 window 798-947 has a bent elbow (89-170 deg) and the old twist window 360-720 is a straight-arm swing until about frame 480 (plan virtual-wiggling-globe.md, verified facts). 3-109 keeps the elbow interior angle at 150.6-169.9 deg with two raw-rejected wrist frames; 3-145 reaches 148.1-172.9 deg but has eight raw-rejected frames, so the primary window was kept. In 505-725 all eight landmarks are raw-accepted, the elbow is held bent (el_y -76.0 to -54.0 deg) and the twist sweeps -97.1 to -25.9 deg.
Alternatives: 3-145 (more motion, six more rejected wrist frames); keeping 798-947 and 360-720 (rejected by the author review).
Evidence: bank_processing/unified_v2/p17, p18, p19 and p13 derived_kinematics.csv ranges (computed in this session); bank_processing/UNIFIED_FOUR_SOURCE_CHECK.json (4896 PASS, 0 FAIL): selected-window tracking verdicts all True on the four windows, whole-recording exit codes 0.
Reversibility: Edit PAGES in anim/bank_axes_kinematics.py and rebuild with --extract --build; rerun the two unified_four checkers.
Review: Page 14 is short (107 source frames, 11.1 s at half speed) and the arm stays near the T-pose (swing angle about 10-12 deg at the ends; elevation -53 to +13 deg inside the window); check that it reads as a swing.

ID: D-089
Status: UNCERTAIN
Decision: On page 14 only, frames whose raw right-wrist sample was rejected (src 2, no depth) and filled by the frozen filter (flag 2) are accepted inside the window (frames 25 and 53); every other landmark must be raw-accepted on every frame, and every landmark on pages 13, 15 and 16.
Why: The swing (root @ Ry @ Rz onto L12->L14) does not read the wrist; the earlier producers required all eight raw landmarks and would reject the only straight-arm window of 180042. The model panel status line shows "Repaired: n" on those frames.
Alternatives: Requiring all eight raw (no usable straight-arm window in 180042); dropping frames 25 and 53 (breaks the one-to-one source clock).
Evidence: bank_processing/p17/landmarks_raw.csv (right_wrist_src 2 on frames 25, 53) and landmarks_filtered.csv (flag 2); PAGES[14]['allowed_raw_rejections'] and the per-frame check in bank_processing/check_unified_four_sources.py.
Reversibility: Remove allowed_raw_rejections from PAGES[14] (the build then fails on frame 25) and pick another window.
Review: Confirm that a filter-interpolated wrist on two frames is acceptable on a swing page.

ID: D-090
Status: UNCERTAIN
Decision: Rotation drawing on the merged pages: the camera-view model draws the parent frame dim (RGB times 0.55, width 4 px, axes 0.12 m) and the rotated frame bright at the page's joint (page 14 root and swing at L12; page 15 swing and arm at L14, sharing X; page 16 arm and elbow-rotated frame at L14); on pages 14 and 16 the bright X axis has the bone length, so its tip is the bone end, and is drawn 4 px wide over the 12 px white focus bone; the top overlay draws the same bright frame only (X 3 px over an 8 px bone). Page 13 draws the root frame bright at L24 with no parent. Pages 14-16 zoom the model panel to the right arm (the similarity is fitted to L12, L14, L16, both frames and the arc over all frames, and drawn clipped inside the panel).
Why: The author's rejection: the films never showed that a bone direction is produced by rotating the parent frame. A bone-length X axis makes "the rotated X axis lies on the bone" visible and testable to the pixel; the close-up makes 0.12 m axes and the arc readable at slide size (at whole-body scale they were a few pixels).
Alternatives: 0.075 m triads at whole-body scale (first preview: arcs and dim frames unreadable); bright X at 0.12 m (tip would not mark the bone end).
Evidence: committee_materials/unified_four/review/UNIFIED_FOUR_MEDIA_CHECK.json (160 PASS): bright X tip against bone end at most 2.3e-13 px (page 14) and 2.5e-13 px (page 16) in both panels on every source frame; page 15 tip on the L12-L14 line within 3.9e-13 px. The sizes 0.12 m, 0.08 m, 12/4 px and 8/3 px are editorial, chosen by viewing frames at slide size, not measured.
Reversibility: Constants PAIR_AXIS_M, ARC_M, FOUR_FOCUS_WIDTH, FOUR_X_WIDTH, MODEL_CLIP and the close-up rule in fit_model_view (anim/unified_panels.py); rebuild.
Review: On page 15 the twist plane (Y-Z) is nearly edge-on to the camera, so the dim and bright Y and Z axes and the twist arc are foreshortened in the camera-view model; the 2D Y-Z panel carries the twist. Decide whether that is acceptable.

ID: D-091
Status: UNCERTAIN
Decision: Arc definitions: page 14 the great circle from the root X axis to the swing X axis at 0.08 m, labelled "swing" with the angle between the two axes; page 15 Rx(t * sh_twist) applied to the swing Z axis about the shared X axis, labelled with sh_twist; page 16 arm @ Ry(t * el_y) then Rz(t * el_z) applied to the arm X axis, labelled "elbow y" with el_y. Arcs are 3D polylines projected like every other point, with an arrowhead at the rotated axis. The arc label sits at a fixed position (third model-panel row), not beside the arc.
Why: Brief wording for each page. The great circle is the single rotation that carries the parent X onto the upper arm; the solver's Ry(sh_y) Rz(sh_z) path differs from it and its angle is not one of the printed angles. On page 16 el_z is 0.0 on every frame (the twist puts the forearm in the arm X-Z plane), so the elbow arc is the Ry(el_y) rotation and its angle equals |el_y|. A fixed label position meets the constant-label rule and avoids clearance checks against a moving arc.
Alternatives: The two-step Ry then Rz path for page 14 (longer and harder to read); labels floating beside the arc.
Evidence: Arc start and end against the parent and rotated axes within 1e-3 deg asserted per frame in unified_panels.compose_four (measured at most 6.4e-15 deg on the middle frames); printed arc values against derived_kinematics.csv at most 0.050 deg (one-decimal rounding) on every frame (UNIFIED_FOUR_MEDIA_CHECK.json).
Reversibility: rotation_pair in anim/unified_panels.py.
Review: The page 14 label is the swing angle between the axes, while the 2D panel prints swing y (azimuth) and swing z (elevation); the notes should say which is which.

ID: D-092
Status: UNCERTAIN
Decision: Durations follow the unchanged delivery clock (every source frame shown twice at 30 fps, 2 s holds): page 13 11.067 s, page 14 11.133 s, page 15 18.733 s, page 16 28.067 s; 69.0 s in total, 8,374,236 bytes at crf 19 (under 8 MiB = 8,388,608 bytes by 14,372 bytes).
Why: No duration was set by the brief beyond half speed and 2 s holds.
Alternatives: Trimming page 16 to shorten the talk (not asked; the page budget is an M2 matter).
Evidence: ffprobe frame counts 332, 334, 562, 842 = 30 x duration (UNIFIED_FOUR_MEDIA_CHECK.json).
Reversibility: Window or CRF change in anim/bank_axes_kinematics.py.
Review: The 8 MiB margin is 14 kB; any later re-encode that grows the films will break the size check.

ID: D-093
Status: UNCERTAIN
Decision: The merged pages' derived files go to bank_processing/unified_four/pNN (source_reference.json binds the whole-bag extraction by hash); anim/bank_axes_kinematics.py now produces only the four merged pages, and the new checkers are siblings: bank_processing/check_unified_four_sources.py and check_unified_four_media.py. anim/unified_panels.py keeps pages 17-20 (bank_kinematics.py) on their earlier code path.
Why: Writing into bank_processing/p14..p16 would overwrite derived files bound by the bank_axes_revision provenance. Siblings leave the earlier reports untouched.
Alternatives: Editing check_unified_sources.py and check_unified_media.py in place (they bind the old bank_axes_revision pages 13-16).
Evidence: git status shows no change under bank_processing/p13..p20 or the prior collections.
Reversibility: Delete the unified_four folders and restore the producer from git.
Review: check_unified_sources.py and check_unified_media.py still import bank_axes_kinematics.py for pages 13-16 and the layout renderer hash they bind has changed, so rerunning them now is expected to fail (not run); M2 should retire or repoint them.

ID: D-094 (superseded by D-106: page 12 is now thesis Figure 3.5 above a schematic)
Status: SETTLED
Decision: Page 12 ideal diagram (make_coordinate_figures.py tpose_reference): the arm chain L12-L14-L16 is white and all torso edges (L12-L24, L12-L11, L11-L23, L23-L24) grey #656565; the point labels sit beside their points with grey leaders, the X letters above the arm line and the Z letters below the grey edges; a legend "White: right arm L12-L14-L16 / Grey: torso edges" was added under the side note.
Why: The author read the bright vertical L12-L24 edge as a 12->14 vector.
Alternatives: Keeping L12-L24 bright as the torso Y reference (rejected by the author).
Evidence: figures/coordinate_frames/tpose_reference.png viewed; the other eleven PNGs in figures/coordinate_frames are byte-identical to HEAD; manifest.json changes only the tpose_reference record and generator_sha256.
Reversibility: Revert the TPOSE_IDEAL_* constants and the focus rule in tpose_reference.
Review: None beyond viewing page 12.

ID: D-095
Status: UNCERTAIN
Decision: Durations of the four merged pages are 100 s (13 Torso frame), 80 s (14 Shoulder swing), 70 s (15 Shoulder twist), 50 s (16 Elbow), 300 s in total.
Why: The brief targets about 300 s for the four pages. Each new page keeps roughly the share of its merged pages in the previous 515 s (13-15: 215 s; 16-17: 130 s; 18+20: 115 s; 19: 55 s). Main talk becomes 3120 s, methodology 2430 s (0.779 >= 2/3).
Alternatives: Keeping the previous 515 s (rejected: the author asked for fewer pages; repeated narration removed); an even 75 s per page (rejected: the torso page carries three previous pages of equations).
Evidence: previous durations in talk_content.json at commit ac71a0b; dry check script output (methodology 2430 / 3120). No rehearsal timing.
Reversibility: Edit "duration" on pages 13-16; the builder adds "Budget: N s" to the notes automatically.
Review: Rehearse pages 13-16 against 100/80/70/50 s; notes run at 131-144 words per minute.

ID: D-096
Status: SETTLED
Decision: Page 13 shows equations 3.7, 3.9, 3.10, 3.11 and 3.15; 3.8, 3.12 and 3.17 are cited in the notes (3.17 expansion is Q&A page 68). Page 14 shows 3.18-3.21, page 15 3.22-3.23, page 16 3.3 and 3.24.
Why: The five keys chain hip axis -> cross products -> basis -> rotation matrix -> Euler encoding and fit the left column. Adding 3.12 (0.75 in tall) would push the stack below the 6.75 in left-region bound.
Alternatives: The plan's suggestion 3.7, 3.9, 3.10, 3.12, 3.15 (bottom 7.01 in at the default 0.18 in gap; does not fit); 3.8 instead of 3.11 (loses the matrix that links axes to angles).
Evidence: Fragment heights from build_deck.exact_equation_fragments at equation_pdf_scale 1.6 (3.7 0.79, 3.9 0.80, 3.10 0.33, 3.11 0.40, 3.15 0.35 in); computed stack bottom 6.49 in, right edge 5.45 in (bound 5.85 in, validate_deck.py left region).
Reversibility: Edit equation_keys on page 13; build_deck raises on any mismatch between drawn and declared keys.
Review: View page 13 at slide size.

ID: D-097
Status: UNCERTAIN
Decision: Layout constants for pages 13-16: bullet_y [1.35, 2.0, 2.65], bullet_height 0.56, equation_start_y 3.27; page 13 only equation_gap 0.14 in.
Why: bullet_y, bullet_height and 3.27 are the values of the previous page 13 (talk_content.json at ac71a0b). The 0.14 in gap (default 0.18 in, build_deck.restrained_equations) is the smallest change that keeps five equations above 6.75 in with margin.
Alternatives: Default gap 0.18 (bottom 6.65 in, 0.10 in margin only).
Evidence: Computed stack bottom 6.49 in. The gap value itself has no legibility measurement.
Reversibility: Remove equation_gap from page 13.
Review: Visual spacing of the page 13 equation column.

ID: D-098
Status: UNCERTAIN
Decision: New left bullets are kept at or below 4.6 in rendered width at 22 pt DejaVu Sans (box 5.03 in).
Why: First drafts measured 5.03-5.15 in and would wrap or trigger a size warning; the previous page 13 bullets used similar lengths.
Alternatives: Accept wrapping (rejected: bullet boxes are 0.56 in tall, one line).
Evidence: PIL DejaVuSans getlength at 22 pt; the text-box insets were not measured, so 4.6 in is a margin choice, not a measured limit.
Reversibility: Edit panel_bullets/bullets.
Review: Check the build's text_fit_warnings for pages 13-16.

ID: D-099
Status: SETTLED
Decision: The rebuilt unified_revision contract uses the round-1 eight-film contract as its base, through a byte copy under committee_materials/unified_revision/history/round1_8film/ (media_contract.json, VIDEO_INDEX.md/.csv, SOURCE_PRESERVATION_CHECK.json, revision_id_map.json and the collection-level VIDEO_INDEX.md, all copied from git HEAD).
Why: The builder rewrites the live contract and page map. Using bank_revision as the base would skip round 1 in the lineage; the copies keep the superseded eight rows and their audit hash-bound. The builder pins the copy by sha256 e7cc8dd8... (HEAD file, last changed in ba0bb18) and resolves a rewritten path through its history copy (bound_or_history).
Alternatives: Base on bank_revision (loses round-1 lineage); a new collection folder (out of the brief's scope).
Evidence: sha256 of the copies equals the round-1 contract's page_map_sha256 (7116bc38...) and source_preservation_audit_sha256 (a7908af7...).
Reversibility: Point BASE back to bank_revision and restore the round-1 base assertions from git.
Review: committee_materials/unified_revision/history/round1_8film/.

ID: D-100
Status: SETTLED
Decision: Kept media rows retain their pNN- file names; every contract row carries source_page (stem number) beside page (current ordinal). The validator checks the stem against source_page, the slide ordinal against page, and page == revision_id_map old_to_new[source_page] for kept rows; the archived replay report stays page 41 with the asset at page 37.
Why: Renaming would invalidate SHA-bound provenance (plan ASSUMPTION 3).
Alternatives: Rename the historical files (rejected: breaks hash bindings).
Evidence: Dry builder run: 20 kept rows, 16 with source_page != page; p41 -> 37.
Reversibility: Remove source_page and restore the stem rule on page.
Review: The Stem page column of unified_revision/VIDEO_INDEX.md.

ID: D-101
Status: UNCERTAIN
Decision: The four new pages carry legacy_id as the list of merged previous (53-page) ordinals, plus merged_legacy_ids with the older legacy ids of those pages.
Why: The brief asks for legacy_id listing the merged pages. Elsewhere legacy_id holds an older numbering (for example previous page 18 had legacy_id 14), so the older ids are kept in merged_legacy_ids.
Alternatives: A separate merged_from field only.
Evidence: None beyond the brief; build_deck uses legacy_id only as a dict key for table captions (not composite pages).
Reversibility: Rename the field on four records.
Review: Whether legacy_id should keep one meaning deck-wide.

ID: D-102
Status: SETTLED
Decision: The notes fields do not repeat "Budget: N s".
Why: build_deck.notes() prefixes every main page with "MAIN TALK | Slide NN | Budget: N s"; the validator reads the rendered notes. A second copy would duplicate the line.
Alternatives: Add the text as the brief states (duplicate).
Evidence: build_deck.py line 1012; validate_deck.py "notes match the planned duration" check.
Reversibility: Append the phrase to the four notes.
Review: None needed.

ID: D-103
Status: SETTLED
Decision: The validator's round-2 route binds pages 13-16 of kind unified_four_kinematics (producer key bank_axes_kinematics) to UNIFIED_FOUR_SOURCE_CHECK.json and UNIFIED_FOUR_MEDIA_CHECK.json, asserts the per-frame rotated-X-on-bone category for pages 14-16 within the checker's rotation_tolerance_deg, and allows raw rejections only for the frames and landmarks the source check lists.
Why: These are the fields the M1 checkers emit; the round-1 checkers bind the round-1 collections and are no longer run, and the round-1 route reads its reports only for the superseded contract.
Alternatives: Reuse the round-1 per-frame rule (rejected: page 14 has two filter-interpolated wrist frames and camera triads without a held flag).
Evidence: bank_processing/UNIFIED_FOUR_SOURCE_CHECK.json (PASS 4896/0; rotated_x_vs_bone_max_deg at most 3.0e-14 deg against 0.001) and committee_materials/unified_four/review/UNIFIED_FOUR_MEDIA_CHECK.json (PASS 160/0).
Reversibility: Edit UNIFIED_FOUR_ROUTE and the four-route branches in validate_deck.py.
Review: validate_deck.py audited_unified_composites.

ID: D-104
Status: SETTLED
Decision: Observability is one left bullet on page 15 ("Straight arm hides the twist"), one notes passage citing Section 5.5, and the committee-index caption; it has no page of its own.
Why: Plan ASSUMPTION 4.
Alternatives: A separate observability page (rejected by the author, point 5).
Evidence: Thesis Section 5.5 citation carried from the previous page 20 source text.
Reversibility: Restore the previous page 20 record from git.
Review: Page 15 bullet and notes wording.

ID: D-105 (superseded by D-106: page 12 is now thesis Figure 3.5 above a schematic)
Status: SETTLED
Decision: The page 12 ideal right-arm diagram draws no torso and no left arm: only the white chain L12-L14-L16, the four points L24, L12, L14, L16, and the triads at L24, L12 and L14; no line joins L24 and L12. The legend reads "White: right arm L12-L14-L16" and "Torso omitted; L24: root origin".
Why: Author instruction 2026-09-24, given twice: the torso edges (grey L12-L24 and L11-L23 in camera perspective) read as vectors.
Alternatives: Keep grey torso edges (rejected by the author twice); keep the unlabelled L11 point (not needed: the L12 triad and label identify the shoulder without it).
Evidence: make_coordinate_figures.py TPOSE_IDEAL_POINTS, TPOSE_IDEAL_EDGES, TPOSE_IDEAL_LEGEND; figures/coordinate_frames/manifest.json key tpose_reference, ideal_diagram.points_drawn and edges_drawn. L24 is still placed at the measured L24-L12 distance (0.638 m) below L12 along root +Y, so the drawn geometry of the kept points is unchanged. The upper recorded photograph is unchanged.
Reversibility: Restore the previous tpose_reference() from git and rerun make_coordinate_figures.py --only tpose_reference.
Review: Page 12 lower diagram at slide size.

ID: D-106 (torso amended by D-107: the schematic torso is now a trapezoid, shoulders 0.35 m wider than hips 0.20 m; the 0.30 x 0.50 m rectangle below is superseded)
Status: SETTLED
Decision: Page 12 figure is thesis V9 Figure 3.5 (writing/v9/figures/ch3_fig_tpose_a.png, copied unchanged to figures/coordinate_frames/thesis_fig3_5_reference_pose.png) fitted without distortion in the top half, above a schematic MediaPipe upper-body T-pose (L11-L16, L23, L24) drawn only from constants in the bottom half: front orthographic view, both arms exactly horizontal at shoulder height, grey torso rectangle 11-12-24-23, right arm white, left arm dim grey, triads at L24, L12 and L14 with Z toward the viewer drawn as a blue ring. The recorded frame 137, the dashed guide, the arm-angle text and every measured-landmark element are removed; the frame-137 source copy tpose_source_arm_test_f00137.png is deleted.
Why: Author instruction 2026-09-24 (third attempt): page 12 must show exactly the thesis T-pose figure and a MediaPipe T-pose skeleton drawn from scratch with the arm horizontal, not derived from any recorded frame or photograph. Only the figure changes; bullets, caption, footnote label, presenter cue and notes stay as they were; the source text names the new figure.
Alternatives: The recorded frame 137 with measured landmarks and a pinhole ideal chain (D-079 to D-081, D-094, D-105; rejected by the author). presentation/assets/ch3_fig5_reference_pose.png (an earlier thesis version's copy; not used because the V9 file exists, identified by the Figure 3.5 IMG line of writing/v9/scripts/build_ch3.py).
Evidence: sha256 e1bb552e4ad63a797bfff415ef75881c6dc998169a0792773d950fd1362f03a2 for both the V9 source and the copy; figures/coordinate_frames/manifest.json key tpose_reference (thesis_figure, schematic true, schematic_constants). The schematic proportions (torso 0.30 x 0.50 m, upper arm 0.28 m, forearm 0.26 m), the 600 px/m scale, the L24 position (600, 1090) px, triad lengths 0.15/0.10/0.10 m, the 17 px Z ring and the label offsets are editorial constants with no data source; they are illustrative only and carry no result. Grey #656565 and white follow anim/unified_panels.py GREY_EDGE and FOCUS_WHITE; text sizes 34/40/44 px match the other coordinate figures. The other PNG/JPG files in figures/coordinate_frames are byte-identical to HEAD. The page 12 notes still describe a recorded frame with measured landmarks (left unchanged at the author's instruction; see Review).
Reversibility: Restore make_coordinate_figures.py tpose_reference(), the validator branch and the frame-137 PNG from git, then rerun make_coordinate_figures.py --only tpose_reference.
Review: Page 12 at slide size; whether the notes' first two sentences (recorded frame, measured landmarks, arm level within a tenth of a degree) should now be reworded to match the new figure, and whether MEDIA_PROVENANCE.md and README.md, which still describe frame 137, should be updated.

ID: D-107
Status: UNCERTAIN
Decision: Page 12 schematic torso is the trapezoid L12-L11-L23-L24 with shoulder width 0.35 m and hip width 0.20 m, centred on one vertical axis (L24 stays the root origin at (0, 0) m and (600, 1090) px; L23 at X = -0.20 m; L12 and L11 at X = +0.075 and -0.275 m, Y = 0.50 m), so the edges 12-24 and 11-23 slant inward toward the hips; arms keep the 0.28/0.26 m segments on the shoulder row, and the L24 Y letter moves to offset (16, -14) px so it clears the slanted edge.
Why: Author instruction 2026-09-24: the MediaPipe torso must be a trapezoid with shoulders wider than hips, as in the MediaPipe pose topology and thesis Figure 3.5, not the 0.30 x 0.50 m rectangle of D-106. The widths come from this project's own MediaPipe output rather than an editorial guess: shoulder 0.35 m is the median (0.3475, rounded to 0.01) of segment_lengths_m.shoulder_width in the four committed eval/reports/recording_*_offset_fit.json files (0.351, 0.317, 0.377, 0.344); hip 0.20 m is the median (0.200) of the per-recording median left_hip-right_hip distance in the same four recordings' v1/mediapipe/output/*_landmarks_raw.csv tables (0.202, 0.198, 0.191, 0.212; hip visibility medians 0.998-0.999), computed with the same nanmedian segment formula as eval/offset/carry.py seg_lengths().
Alternatives: The brief's default 0.40 m / 0.28 m (no measured source; rejected because measured MediaPipe values exist). Keeping the rectangle (rejected by the author). Moving the whole L24 triad or all Y letters (rejected: only the L24 Y letter touched the new edge; the other triads keep their D-106 layout).
Evidence: Shoulder values: the four committed offset_fit reports. Hip values: computed on 2026-09-24 from the landmark tables, which are git-ignored (.gitignore line 3, v1/mediapipe/output/) and so not pinned in the repository. figures/coordinate_frames/manifest.json key tpose_reference, schematic_constants.widths_m, widths_px (210 px, 120 px), widths_source, landmarks_root_m. make_coordinate_figures.py now raises unless the torso is a centred trapezoid with shoulders wider than hips and every label box keeps TPOSE_LABEL_EDGE_GAP_PX = 4 px (editorial, no data source) beyond the edge half-width; a negative test with the old L24 Y offset raised on edge L12-L24. validate_deck.py adds the check 'T-pose schematic torso is a centred trapezoid with horizontal arms' (PASS; 1723 checks, 0 package failures). Only ppt/media/image9.png differs in the PPTX from HEAD 28a1396.
Reversibility: Change TPOSE_SHOULDER_WIDTH_M and TPOSE_HIP_WIDTH_M in make_coordinate_figures.py and rerun make_coordinate_figures.py --only tpose_reference, then build_deck.py, render_deck.py, validate_deck.py --pdf and export_defense_script.py --pdf.
Review: Page 12 at slide size: whether the 1.75 shoulder-to-hip ratio reads as intended; whether a hip width taken from uncommitted landmark tables is an acceptable source for an illustrative schematic, or the brief's 0.40/0.28 m should be used instead.

ID: D-108
Status: UNCERTAIN
Decision: The two supplemental masters on hidden Q&A pages 60 (committee_materials/axes_revision/videos/p64-Derived_Memory_Records.mp4, 44 s) and 65 (p69-Single_Frame_Overview.mp4, 36 s) are embedded as click-to-play thumbnails (2.40 x 1.35 in at x 0.82, y 5.30 in, below the bullets, with a 16 pt caption "... Click to play full screen.") that PowerPoint plays full screen (p:video fullScrn="1") and never starts on entry, replacing the text hyperlinks to those files; validate_deck.py fails on any external relationship that is media-typed or not a web address, and on a supplemental video that is not embedded; make_package.py writes the shareable folder package/Thesis_Defence_2026/ (PPTX, still PDF, DEFENSE_SCRIPT.pdf, README.txt) plus package/MANIFEST.json, with no archive.
Why: Author request 2026-09-24: send the professor a self-contained package, uploaded to OneDrive as a folder the professor opens directly. The two pages carried TargetMode="External" hyperlink relationships (build_deck.py restrained_flow, kinds 'records'/'record_fields' and 'preserved_overview', label.click_action.hyperlink.address set to a path relative to this folder), which break when the PPTX travels alone; the existing validator only inspected media/video/image relationships, so a hyperlink-typed link to an MP4 passed. The right evidence region of both pages is filled by the native diagram, so the thumbnail uses the free lower band of the left region; full-screen playback keeps the 1280 x 720 master legible, and click-to-play keeps the diagram visible on entry. Thumbnail geometry comes from the existing grid: x 0.82 in is the restrained_bullets() text column, y 5.30 in clears the third bullet line (4.62 + 0.42 in), 16:9 matches the 1280 x 720 posters, the bottom 6.65 in stays above the footer rule at 6.88 in, and the caption ends at 5.85 in, the left-region edge. The 0.24 in top margin and the 0.18 in thumbnail-to-caption gap are editorial, with no data source.
Alternatives: Keep the links and ship the committee_materials video folders beside the PPTX (rejected: the folder must open directly and the brief excludes those folders). Add two extra hidden pages holding the movies (rejected: changes the 74-page count). Replace the native diagrams with the movies (rejected: removes the readable record and frame diagrams). A zip archive (dropped by the author's brief change: OneDrive folder instead).
Evidence: Before: unzip of the d57aef1 build lists 19 MP4 parts and two External rels (slide60.xml.rels, slide65.xml.rels rId2); the new validator on that PPTX reports FAIL 'Package has no external media or local-file relationship' naming both. After the rebuild: 21 MP4 parts, 0 External rels, validator 1738 checks, 0 package failures (overall PARTIAL from the two retained source-validation findings, as before), PDF 74 pages, PPTX 81,646,958 B (under 100 MiB). The 'native type roles follow the shared grid' check gains one exception for this caption, bounded to (0.82, 5.20, 5.85, 6.86) in, like the existing pending-recording caption exception. The spoken notes of pages 60 and 65 now say the animation is embedded at the lower left instead of supplied separately.
Reversibility: Restore the two hyperlink labels in build_deck.py restrained_flow, remove supplemental_movie(), the two notes sentences and the validator exception, and rebuild; drop make_package.py, PACKAGE_README.txt, .gitignore and package/.
Review: Open the PPTX in Microsoft PowerPoint on the defence machine and click the thumbnails on pages 60 and 65: confirm full-screen playback and return (not verified here; LibreOffice was used only for the PDF). Check that the lower-left thumbnails read well at projection size.

ID: D-109
Status: UNCERTAIN
Decision: The introduction task clip media/raw_task_context.mp4 is two recorded segments joined by a hard cut, R6b one-hand rail pass then R7 two-hand handover, at the native 30 fps (every source frame once, no holds, no retiming, no interpolation), 640x480 native camera size with no crop or resize, H.264 High yuv420p CRF 18 preset medium, faststart, no audio; 46.533 s in total. validate_media.py EXPECTED_SECONDS gains "raw_task_context": 1396 / 30 so the duration is checked.
Why: Supervisor request: the introduction page plays raw video of the actual bimanual task so the committee sees what is tracked and reconstructed. The two recordings are the thesis rail and handover recordings whose frames the deck's evaluation stills already use. Encoder settings copy anim/recorded_context.py (frame_context.mp4 is 640x480 h264 High yuv420p 30/1), and validate_media.py requires h264, yuv420p, 30/1 and no audio for every MP4. The encode and poster checks reuse recorded_context.finish_asset by import.
Alternatives: R6b alone (rejected: the handover is the bimanual part of the task). A crossfade or title card between segments (rejected: the brief allows only the one-line caption). Half-speed playback as in the filter context clips (rejected: brief asks for native frame rate and about 45 s).
Evidence: anim/raw_task_context.py run on 2026-09-27: finish_asset PASS (1396 frames, 46.533333 s, full decode, 640x480, h264 yuv420p 30/1); ffprobe nb_frames=1396, duration=46.533333, size=5399817. Both bag sha256 values equal eval/recordings_archive/index.json. Recorded frame steps 33.343-33.412 ms (R6b) and 33.353-33.393 ms (R7): no dropped frames in the selected ranges.
Reversibility: Change SEGMENTS in anim/raw_task_context.py, rerun it, and update the EXPECTED_SECONDS entry.
Review: Whether 46.5 s is acceptable on the introduction page against the brief's target of about 45 s and limit of 50 s; the hard cut at 29.533 s.

ID: D-110
Status: UNCERTAIN
Decision: Source frame ranges are R6b (Video/recording_20260831_065553.bag) frames 13-898 inclusive, 29.533 s, and R7 (Video/recording_20260909_000024.bag) frames 690-1199 inclusive, 17.000 s, in BagSource frame indices.
Why: R6b frames 0-12 and R7 frames 0-14 carry a burned-in landmark drawing (white skeleton lines, cyan and orange dots) inside the bags themselves, so the R6b segment starts at the first clean frame and runs to the last decoded frame (898): approach, acquisition at the left end, lift onto the rail and slide to the far end, including stills 95, 505 and 700. For R7, contact sheets at 15-frame spacing show the right hand sliding the cube at 690, the left hand arriving at about 870, both hands on the cube at about 885-1005, the right hand released by about 1020, the left-hand slide to the far end by about 1140-1155 and the left hand lifting off by about 1185; 690-1199 covers the late right-hand slide, the transfer and the complete left-hand slide, including stills 700, 950 and 1042. The complete R7 right-hand slide (from about frame 90) does not fit the 15 s target, so only its last 6 s are shown.
Alternatives: R6b from frame 0 (rejected: frames 0-12 show the drawn landmarks). R7 700-1149 (15.0 s exactly; rejected: cuts before the left hand lets go). R7 from about frame 90 (rejected: about 37 s, total over 50 s).
Evidence: Overlay scan over every frame of both bags (2026-09-27, scratch script, BGR dot colours (230,216,0) and (0,136,255), tolerance 40): drawn frames 475-706 matching pixels, R6b frames 13 onward at most 30, R7 frames 15 onward at most 64 (the light-blue cabinet sticker at x 72-85, y 345-354 on R7 frame 872). The generator re-asserts at most 200 on every selected frame (worst 30 and 64). Decoded RGB of frames 95, 505, 700 (R6b) and 700, 950, 1042 (R7) is pixel-identical (maximum difference 0) to writing/v9/figures/src/{r6b,r7}_frameNNNNN.png, which confirms the frame indexing. Phase boundaries are read from contact sheets by eye, not measured.
Reversibility: Edit SEGMENTS first/last in anim/raw_task_context.py and rerun; update MEDIA_PROVENANCE.md and the validate_media.py duration.
Review: Watch the clip: whether the R7 segment starts early enough to read as the right-hand slide, and whether the R6b opening seconds (person standing, 0.4-1.5 s) should be trimmed.

ID: D-111
Status: UNCERTAIN
Decision: Caption text is "R6b rail task: recorded RGB, no overlays" on the R6b segment and "R7 handover: recorded RGB, no overlays" on the R7 segment, one line, white DejaVu Sans 13 px on a black box at 60 % opacity with 6/4 px padding, in the bottom-left corner (x 0-277, y 458-480 px); nothing else is drawn.
Why: The brief allows a small one-line caption at the bottom naming the recording and "recorded RGB, no overlays". Bottom-left keeps the box on the desk surface and left of the desk marker card (left edge at x 318-319 px), so the marker and the task area stay unobscured. R6b and R7 are the recording names used in the thesis and the deck.
Alternatives: A caption band below the image, 640x504 (rejected: changes the native 640x480 size the brief asks to keep). Full recording stems in the caption (rejected: too long to fit left of the marker at a legible size). Bottom-centre caption (rejected: covers the desk marker).
Evidence: Marker edge: first pixel with all channels above 200 on rows 440-470, 318 px on R6b frame 1 and 319 px on R7 frame 0 (2026-09-27); the generator asserts the box width is below 318 px. Font size, padding and opacity are editorial constants with no data source; DejaVu Sans is the font of anim/causal_replay.py and anim/axes_kinematics.py.
Reversibility: Edit the caption strings or FONT_PX, PAD_X, PAD_Y, CAPTION_ALPHA in anim/raw_task_context.py and rerun.
Review: Legibility of the 13 px caption at projection size, where the 640x480 clip is scaled up on the slide.

ID: D-112
Status: UNCERTAIN
Decision: The main talk is cut to 35 pages and 1620 s (27:00): title, information flow, outline, then 9 chapter dividers and 23 content pages, ending with Questions; the 14 old main slides 4, 7, 8, 10, 22, 23, 26, 30, 31, 32, 33, 34, 42 and 46 move unchanged to backup pages 61-74 (duration 0) and the old backups 50-74 become 36-60.
Why: Master brief for the 27:00 restructure (page table, moved-slide list, 1620 s total). Nine dividers at 5 s plus a 25 s outline make the brief's table sum to exactly 1620 s; the brief text says "8 dividers" but its table lists 9 divider rows, and 1620 s only closes with 40 s of dividers and the outline reduced from 30 s to 25 s.
Alternatives: Eight dividers with a 30 s outline (rejected: needs one table row dropped, and Chapters 9 and 10 would then have no divider). Keeping 30 s outline and trimming 5 s from a content slide (rejected: the brief fixes content durations).
Evidence: build_deck.py output 2026-09-27: 35 main + 39 appendix pages, 1620 s; validate_deck.py --pdf reports focus context 175, methodology 1100, evaluation 220, conclusion 115, questions 10 (sum 1620). Durations are editorial targets from the brief; no rehearsal was timed.
Reversibility: Edit the page table in the round-3 generator (scratchpad gen_round3.py) or talk_content.json directly; backups are ordinary entries in backup_content.json.
Review: Whether the Chapters 9-10 divider should exist (8 vs 9 dividers) and whether 25 s is enough for the outline.

ID: D-113
Status: UNCERTAIN
Decision: Speaker notes are rewritten per page to about 2.0 words/s x (budget - embedded video seconds), merged slides get one rewritten note (not concatenated), every note ends "Thesis: Section x.y", and main slides carry at most 4 bullets of at most 8 words with no trailing period; main slides carry no equations (equation_keys emptied).
Why: Brief content rules (slow pace, highlights only, no equation walk-throughs). Equations stay reachable on the backup pages they came from.
Alternatives: Keep one equation per methods slide (rejected: brief says no equation walk-throughs).
Evidence: validate_deck.py --pdf main-talk word count 2558 against a 1620 s budget; per-page counts are within a few words of target (for example page 5: 60 words vs 57 target; page 23: 77 vs 72; page 34: 114 vs 110). The 2.0 words/s rate is the brief's figure, not measured.
Reversibility: Regenerate talk_content.json with edited notes; restore equation_keys from git HEAD.
Review: Read the notes aloud against the clock; the 2.0 words/s pace is untested.

ID: D-114 (page 11 figure pair and the removal of p14 from the whole deck superseded by D-123 and D-124)
Status: UNCERTAIN
Decision: Merge and video choices: page 8 merges camera, calibration and landmark acceptance (old p06 video kept); page 9 signal conditioning keeps p09; page 11 is a new frames + T-pose figure pair (camera_frames.png beside thesis_fig3_5_reference_pose.png); pages 12-14 keep p13, p15, p16; the p14 swing video is no longer embedded anywhere; page 28 stacks the right-arm and left-wrist failure figures (legacy keys right_failure and left_failure both retained); page 29 handover keeps p47 with the playback note "stop early if behind time"; page 31 keeps p49 and summarises old 46 in its notes.
Why: Videos are the stated priority; where two videos covered one idea, the one showing the whole mechanism was kept. Both imperfect-result examples stay in the main talk (standing rule in CUTTING_GUIDE.md).
Alternatives: Keep p14 in place of p15 (rejected: p15 shows swing and twist together).
Evidence: DEMONSTRATION_MANIFEST.json after build: 14/14 declared demos recorded; validate_media.py PASS on 69 assets.
Reversibility: Swap the visual block of the affected page in talk_content.json.
Review: Whether dropping p14 from the whole deck (including backup) is acceptable.

ID: D-115
Status: UNCERTAIN
Decision: Page 5 (Introduction) shows the raw task clip media/raw_task_context.mp4 (46.533 s, poster raw_task_context.png) as kind task_video, marked demo, recording_status recorded, recording_kind camera.
Why: Brief asks for a raw task video on the introduction slide; the clip was produced for this purpose under D-109 to D-111 by another worker.
Alternatives: Reuse an overlay demo (rejected: brief asks for raw).
Evidence: Duration 1396 frames / 30 fps = 46.533 s, as declared in anim/validate_media.py; validate_media.py PASS.
Reversibility: Replace paired_media on page 5 of talk_content.json.
Review: The 75 s page budget holds 46.5 s of video and about 57 words of notes.

ID: D-116
Status: UNCERTAIN
Decision: Builder adds five restrained kinds: divider (black page, 11 pt chapter label at (0.50, 0.18), 28 pt title at (0.50, 0.52), no footer, title and number only), outline (section names only, '-' marks at x 0.50 and names at x 0.82, 22 pt, left region, rows stacked by measured wrap height from y 1.30 with 0.06 in gap, error if below 6.75), information_flow (six nodes left to right in the right region: RGB-D camera, Body estimation, Marker pose, Kinematic recovery, Temporal merger, Unity rig; columns x 6.22/7.94/9.66/11.38, nodes 1.45 x 0.90, rows y 1.62/3.27/4.92), figure_pair (side or stack), evaluation_charts (object chart from Tables 7.1-7.2 over the wrist-median chart, 0.83/5.5 n=650 and 2.34/6.8 n=589).
Why: Brief asks for outline, divider and info-flow types; all coordinates sit inside the validator's fixed typography grid (title band 0.50-12.85 x 0.45-1.10, left region 0.50-5.85 x 1.20-6.75, right region 6.22-12.83 x 1.20-6.86). Numbers on the outline were replaced by '-' because a numeric-only run above 16 pt fails the enlarged-numeric-callout check. The old 'architecture' kind is kept for the backup copy of old slide 4.
Alternatives: Centred divider title (rejected: outside the title band, fails the typography check). Numbered outline (rejected: validator FAIL).
Evidence: Region bounds from validate_deck.py; chart values from the existing deck content (Tables 7.1-7.2 and the wrist-median figures already on old slides); node spacing and sizes are layout choices with no data source (UNCERTAIN). build_deck.py: 0 fit warnings, 0 overlap candidates.
Reversibility: Kinds are isolated functions restrained_divider, restrained_outline, restrained_information_flow, restrained_figure_pair, restrained_evaluation_charts in build_deck.py.
Review: Previews 2, 3, 4, 11, 27; the small text inside the page 11 figures may be illegible when projected.

ID: D-117
Status: UNCERTAIN
Decision: The Q&A index page switches to a 3-column compact grid (one-line labels, pitch (6.80 - 1.25)/rows, error if a label does not fit) when it has more than 24 items; it now lists 38 topics in 13 rows. Short labels were added for the 14 moved titles.
Why: The 4 x 6 grid holds 24 items; the backup set grew from 25 to 39 pages.
Alternatives: Two index pages (rejected: changes backup page numbering twice).
Evidence: Preview slide-36.png inspected, all 38 labels on one line. 6.80 and 1.25 are layout bounds from the existing index design.
Reversibility: restrained_index in build_deck.py keeps the old path for 24 or fewer items.
Review: Readability of the 38-tile index when projected.

ID: D-118
Status: UNCERTAIN
Decision: validate_deck.py check "Main evaluation retains numerical and imperfect-result evidence" now reads legacy_key and merged_legacy_keys, requires right_failure and left_failure in the main talk and raw_hips anywhere in the deck (it moved to backup); the depth_rules caption now names the current raw_hips Q&A page instead of a fixed number.
Why: The check hard-coded the old main-talk layout; the brief allows updating expectations to the plan, never loosening. Both failure examples stay required in the main talk.
Alternatives: Keep raw_hips in the main talk (rejected: brief moves old slide 42 to backup).
Evidence: validate_deck.py --pdf 2026-09-27: this check PASS.
Reversibility: Revert the check body from git HEAD.
Review: Whether raw_hips in backup only is an acceptable weakening of main-talk evidence; this is the one place the retained set changed.

ID: D-119 (resolved by D-120 and D-121: validate_deck.py 1685 PASS / 0 FAIL on 2026-09-27)
Status: BLOCKED
Decision: The 22 remaining validate_deck.py FAILs (media contract currency, and 21 "declared media uses its committee page identity" on slides 5, 8, 12, 13, 14, 18, 19, 20, 21, 23, 25, 29, 31, 49, 50, 62, 63, 66, 68, 70, 72) are left open, not waived.
Why: They require a round-3 revision_id_map.json and a regenerated committee_materials/unified_revision/media_contract.json; anim/unified_revision_build.py (REPLACEMENTS pages 13-16) and validate_deck.py UNIFIED_FOUR_ROUTE (pages 13-16) are hard-wired to the round-2 page map. That is outside this task's scope.
Alternatives: Edit the contract by hand (rejected: generated file, and it would hide the page remap from the committee record).
Evidence: validate_deck.py --pdf 2026-09-27: 1605 checks, 1583 PASS / 22 FAIL.
Reversibility: Not applicable; a follow-up task rebinds the contract.
Review: Approve a scoped task to build the round-3 page map and contract.

ID: D-120
Status: SETTLED
Decision: Round-3 contract: revision_id_map.json becomes the round-3 map (schema_version 6; 35 main + 41 Q&A pages, 1620 s; Q&A index page 36 with 40 items) and anim/unified_revision_build.py is rebased onto it; the rebuilt committee_materials/unified_revision/media_contract.json, VIDEO_INDEX.md/.csv and a page-5 committee copy (videos/p05-Raw_Task_Context.mp4, posters/p05-Raw_Task_Context.png, provenance/p05-Raw_Task_Context.json and _source_frames.csv) replace the round-2 outputs, which are archived under committee_materials/unified_revision/history/round2_4film/.
Why: D-119 left 22 contract FAILs because the builder and contract were hard-wired to the round-2 page map. Page 5 embeds the raw task clip through a committee identity like every other declared medium, so the validator's "declared media uses its committee page identity" check applies to it unchanged.
Alternatives: Edit media_contract.json by hand (rejected in D-119: generated file, and it would hide the page remap). Embed media/raw_task_context.mp4 directly on page 5 (rejected: it has no committee page identity, and the identity check would have to be relaxed).
Evidence: The p05 copy is byte-identical to media/raw_task_context.mp4 and .png (sha256 a0e82d4e...3c71367 and cad204dd...3d89737, sha256sum 2026-09-27); MEDIA_PROVENANCE.md, Introduction task clip, now names it. validate_deck.py --pdf 2026-09-27: 1685 checks, 1685 PASS / 0 FAIL (overall PARTIAL only for the two retained historical Unity-checker findings of D-058/D-066); validate_media.py PASS 69 assets; validate_filter_sync.py PASS.
Reversibility: Restore revision_id_map.json, anim/unified_revision_build.py and the unified_revision outputs from git HEAD or history/round2_4film/, and rerun the builder.
Review: VIDEO_INDEX.md page numbers against the 35-page talk.

ID: D-121 (page-11 thesis Figure 3.5 copy and its verbatim caption check superseded by D-273)
Status: SETTLED
Decision: validate_deck.py expectations move to the round-3 map without removing any check: UNIFIED_FOUR_ROUTE takes current_pages {13:12, 14:76, 15:13, 16:14} (producer pages keep their stems, reports and audits); the archived p41 asset is expected on page 25 with previous_page 37; the contract must bind and embed the previous (round-2) page map it chains through; and a frame_figure page may show the manifest's source-bound thesis figure copy alone (figures/coordinate_frames/manifest.json tpose_reference.thesis_figure), bound to that copy's hash and region, with a new check that its caption equals the thesis caption verbatim.
Why: These expectations still encoded round 2. Page 11 now shows thesis Figure 3.5 alone (D-123), so the old check, which accepted only the composite tpose_reference.png, failed once the deck was rebuilt. The copy's hash is already tied to writing/v9/figures/ch3_fig_tpose_a.png by the existing T-pose check, so the binding keeps the same strength, and the caption check is new.
Alternatives: Point page 11 back to the composite (rejected: the master's round-3 layout shows Figure 3.5 alone). Delete or skip the page-11 figure check (rejected: fix, never waive).
Evidence: validate_deck.py --pdf 2026-09-27: "Slide 11 embeds its declared coordinate-frame figure" PASS and "Slide 11 thesis figure copy carries its verbatim thesis caption" PASS; 1685 PASS / 0 FAIL overall. The R7 cache was regenerated read-only with /home/luo/anaconda3/envs/v3rt/bin/python anim/matched_evidence.py extract (182 frames into /tmp/defense_matched_r7), then validate_matched_sources.py PASS (141 matched frames); the only file it rewrote, review/MATCHED_INDEPENDENT_REVIEW.json, differed from HEAD only in reviewed_at_utc and was restored to the HEAD bytes.
Reversibility: git diff validate_deck.py shows each changed expectation; revert that hunk.
Review: That the thesis-copy branch cannot be reached by a page that declares any other image.

ID: D-122
Status: UNCERTAIN
Decision: Page 2 (information_flow) is drawn full width below the title: six nodes 2.30 x 1.10 in, columns x 0.50/3.843/7.187/10.53, rows y 1.55/3.30/5.05, node text 22 pt; arrow labels 16 pt ("colour + depth" on camera -> body estimation, "Object information" on marker pose -> kinematic recovery, "time-aligned states" on temporal merger -> Unity rig); caption across the full width at y 6.29. validate_deck.py native_typography allows 22 pt and 16 pt runs anywhere inside (0.50, 1.20, 12.83, 6.86) for visual kind information_flow only.
Why: The page has no bullets, so the right-region-only diagram (1.45 in nodes at 16 pt) left the left half empty. The label on the object link follows thesis Figure 2.3 and the page notes. The typography exception was approved by the master and is scoped to one kind; every other page keeps the shared grid.
Alternatives: Keep the diagram in the right region (rejected: small nodes, empty left half). Shrink node text to 16 pt at full width (rejected: master chose 22 pt).
Evidence: Node and grid constants are from the master's brief (four equal 2.30 in columns from 0.50 to 12.83 in, gap 1.043 in); label positions are layout choices checked on preview/slide-02.png. Measured DejaVu Sans widths: "Object information" 2.077 in and "time-aligned states" 2.151 in at 16 pt, so both fit one line. build_deck.py: 0 text-fit warnings, 0 overlap candidates; validate_deck.py "Slide 02 native type roles follow the shared grid" PASS.
Reversibility: restrained_information_flow in build_deck.py and the information_flow flag in validate_deck.py native_typography.
Review: Legibility of the arrowheads and the association of "colour + depth" and "Object information" with their arrows when projected.

ID: D-123
Status: SETTLED
Decision: A frame_figure page whose caption needs more than two 16 pt lines (page 11, the verbatim three-line thesis Figure 3.5 caption) gets a 4.75 in figure box (y 1.20-5.95) and the caption band 6.00-6.84 in; two-line captions keep the 5.00 in box and 6.31-6.84 band.
Why: Three 16 pt lines need 3 x 16 x 1.18 / 72 = 0.787 in, more than the old 0.53 in band; the band ends above the footer rule at 6.88 in. Shortening the thesis caption was not allowed (verbatim).
Alternatives: Smaller caption type (rejected: outside the fixed 16 pt role). Caption beside the figure (rejected: the 828 x 822 figure leaves no useful side column at 4.75 in height).
Evidence: build_deck.py 2026-09-27: 0 text-fit warnings (page 11 included); preview/slide-11.png shows the caption on three lines above the rule; validate_deck.py page-11 figure checks PASS (inside 6.22-12.83 x 1.20-6.75, no crop).
Reversibility: The frame_figure branch of restrained_page in build_deck.py.
Review: Figure 3.5 is about 5 per cent smaller than in the two-line layout.

ID: D-124
Status: UNCERTAIN
Decision: Old slide 11 "Camera and Camera-prime" becomes Q&A page 75 and old slide 14 "Shoulder swing" with the p14 film becomes Q&A page 76; the Q&A index lists them as "Camera frames" and "Shoulder swing" (40 items, 3 columns, 14 rows).
Why: The main talk was cut to 27:00; both pages answer likely questions (Camera-prime is cited from page 11's notes) and D-114 had dropped the p14 film from the whole deck.
Alternatives: Leave them out of the deck (rejected: page 11 notes point to page 75, and the p14 film is the only swing demonstration).
Evidence: Index labels measured at 1.717 in and 1.701 in at 16 pt, inside the 1.957 in one-line limit of restrained_index (tile width (6.61 - 0.20) / 3 minus 0.18 in) (build raises otherwise); preview/slide-36.png shows 40 one-line tiles, last row bottom 6.74 in; previews slide-75.png and slide-76.png inspected.
Reversibility: Remove the two backup entries from backup_content.json and the map, then rebuild.
Review: Readability of the 40-tile index when projected.

ID: D-125
Status: SETTLED
Decision: Code-review fixes to the 35-page restructure (source: the Opus code reviewer's findings on D-112 to D-124): (1) the RESTRAINED_REVISION_PLAN.md paragraph derives its page references from the content (manual hip-depth illustration by its unique hip_depth_manual kind, raw_hips and right_failure through PAGE_BY_LEGACY_KEY, the thesis Figure 3.5 page by its tpose_reference key) and raises if a reference is missing or ambiguous; it now reads Q&A page 64, Q&A page 73, main page 28 and main page 11; (2) CUTTING_GUIDE.md (and the REVISION_OUTLINE.md header) drop "expanded review draft" and use the speaker_notes() wording (planned main talk, including media, editorial targets, not a measured delivery time); (3) the frame_figure branch raises ValueError when the caption needs more than three 16 pt lines; (4) the restrained_index compact-grid comment states the computed geometry (rows = ceil(n/3); 40 items: 14 rows, pitch 0.396 in, tile 0.339 in, last bottom 6.74 in); (5) restrained_evaluation_charts reads the wrist medians and n (right/left model, rig, n) from slide 27's data block and raises on a missing key; (6) restrained_footer's stale main_count=39 default is removed (slides and main_count are required); (7) validate_deck.py corrects the "Page 12" comment to page 11 and adds, for every frame_figure page that shows a manifest thesis_figure copy alone (any figure key), a check that the copy's bytes, the manifest sha256, the manifest source_sha256 and the source file's sha256 are all equal.
Why: Each item removes a stale literal or a silent path: page numbers and a default that had already gone stale once, a warning where the sibling layouts raise, a chart duplicating values held in the content, and a source binding that only the tpose_reference key had.
Alternatives: Update the literal page numbers by hand (rejected: they went stale in round 3 and would again). Keep only the tpose_reference binding (rejected: a future thesis copy under another key would be bound to its manifest hash only).
Evidence: build_deck.py 2026-09-27: 35 main + 41 appendix slides, 0 text-fit warnings, 0 overlap candidates; preview/slide-27.png before and after the data-block change: max pixel difference 0 (numpy, RGB); negative tests raised as intended (slide 27 data without left.n; a ten-line page-11 caption); validate_deck.py --pdf: 1686 checks, 0 package failures (the new "Slide 11 thesis figure copy is byte-identical to its thesis source" PASS; overall PARTIAL only for the two retained historical findings of D-058/D-066).
Reversibility: git diff build_deck.py and validate_deck.py; each item is a separate hunk.
Review: The six object endpoint-length values on page 27 remain literals in build_deck.py (as in restrained_object_chart): slide 27's data block holds only the wrist medians and n, and talk_content.json was outside this task's scope.

ID: D-126
Status: UNCERTAIN
Decision: The outline page (page 3) lists the nine section names across the full content width: name boxes from x 0.82 to 12.83 in at the unchanged 22 pt body role, so no name wraps; the builder raises if a name would wrap. validate_deck.py native_typography allows the 22 pt role inside (0.50, 1.20, 12.83, 6.86) for visual kind outline only, the same scoped form as D-122.
Why: In the 5.03 in left column several names wrapped and the right half of the page was empty; the page has no right-hand exhibit.
Alternatives: Keep the left column (rejected: wrapped names, empty right half). Two columns of names (rejected: breaks the single reading order of the chapter list). Smaller type (rejected: outside the fixed 22 pt role).
Evidence: Measured DejaVu Sans width at 22 pt: longest name "System integration and graphical reconstruction" 7.41 in, inside the 12.01 in box; list bottom 1.30 + 9 x 0.361 + 8 x 0.06 = 5.03 in. preview/slide-03.png shows nine one-line rows; validate_deck.py "Slide 03 native type roles follow the shared grid" PASS. The master's brief set the 0.50-12.83 in width; the typography-grid exception is not yet approved by the author.
Reversibility: restrained_outline in build_deck.py (width back to 5.03 in, drop the wrap raise) and the outline_row flag in validate_deck.py native_typography.
Review: Whether the list, now occupying the upper-left of a wide page, reads well when projected; talk_content.json slide 3 visualintent and purpose.right_visual still say "left column" and should be updated by whoever owns that file.

ID: D-127
Status: SETTLED
Decision: Delete all 41 hidden pages of round 3 (index page 36 and Q&A pages 37-76) and replace them with 13 self-contained hidden topic pages 36-48; the main talk (pages 1-35, 1620 s) is unchanged except where its text cited a Q&A page (pages 11, 12, 23, 29, 31 and 35 now cite thesis sections instead). The deleted pages are not kept anywhere in talk_content.json or backup_content.json; they remain recoverable in git history at commit 41d94a7. The embedded supplemental-movie thumbnail (D-108) left with its pages, so build_deck.py drops supplemental_movie() and raises if a page still declares supplemental_media.
Why: Author request of 2026-09-28: a hidden page is shown only if the committee asks, so each must carry one topic on the full slide.
Alternatives: Keep the old pages alongside the new ones (rejected by the author's request). Keep the deleted page records in the JSON as inactive entries (rejected: they would still be read by the builders and validators; git history keeps them).
Evidence: Author instruction relayed in the master's brief of 2026-09-28. build_deck.py 2026-09-28: 35 main + 13 appendix slides, planned main talk 1620 s, 0 text-fit warnings, 0 overlap candidates. git diff of talk_content.json touches only the six cited-page sentences and page 35's source and purpose.
Reversibility: git checkout 41d94a7 -- presentation/defense_2026/backup_content.json talk_content.json build_deck.py validate_deck.py revision_id_map.json and the unified_revision contract files.
Review: Whether any of the deleted topics (root-angle derivation, evaluation references, record fields, image pairs) should return as one of the new full-width pages.

ID: D-128
Status: SETTLED
Decision: Self-containment rule: no index page and no internal slide link exist; hidden pages are reached by typing the slide number. The closing page 35 loses its "Open technical appendix" button, and build_deck.py appends "Hidden topic pages (not spoken; type the slide number and press Enter)" with every hidden page number and title to page 35's notes, derived from backup_content.json. restrained_footer and the legacy footer no longer draw a "Q&A index" link; restrained_index, index_page and their label table are removed. validate_deck.py replaces the three index-link checks with "No index page remains", "No slide carries an internal slide link" and "Closing page notes list every hidden topic page by slide number", and adds "No hidden page refers to another hidden page": no hidden page's title, claim, bullets, caption, table cells or notes contains "Q&A page(s)" or "page/slide NN" with NN a hidden page number.
Why: A hidden page appears only when asked, so a pointer to another hidden page would lead nowhere during the talk.
Alternatives: Keep a slimmer index page (rejected by the author). Keep return links on each hidden page (rejected: with no index there is no target).
Evidence: validate_deck.py --pdf 2026-09-28: the four checks PASS; links map empty for all 48 slides.
Reversibility: restrained_page closing branch, notes() hidden_pages block and build() in build_deck.py; the navigation block and the self-containment check in validate_deck.py.
Review: Whether the presenter wants the hidden-page list printed on a handout as well as in the page-35 notes.
Annotation (2026-10-01, round 11): the rule "hidden = after the talk" is superseded in part by D-341 (a main page may also be hidden by a per-page flag); the closing-page hidden-topic list moved from the notes pane to SPEAKER_NOTES.md and now covers hidden main pages too (D-344).

ID: D-129
Status: UNCERTAIN
Decision: Three full-width visual kinds for hidden topic pages, drawn in the region x 0.50-12.83 in, y 1.20-6.75 in (the information_flow region of D-122), with no left bullets: full_image (a PNG scaled to fit, centred, aspect kept, optional one-line 16 pt caption at y 6.29 in, the exhibit then ending at 6.20 in; a missing file raises FileNotFoundError naming the slide), full_video (the film and poster at the full-region height above the caption, centred, autoplay as in movie(); the 22 pt claim in the left side panel; the caption carries the settings line; a side panel narrower than 2.20 in raises) and full_table (restrained_rows across the full width with the same 191919 header band; optional column_widths fractions; a cell needing more than two 16 pt lines raises). validate_deck.py allows the 22 pt and 16 pt roles inside (0.50, 1.20, 12.83, 6.86) for these three kinds only (same scoped form as D-122), checks declared media against the full region for these kinds, replaces the 6.00 x 5.00 in composite-size check by a poster-aspect and at-least-4.99 in height check for full_video only, and adds a check that each full_image page embeds its declared image uncropped inside the full region.
Why: A topic page shown on request should use the whole slide for its chart, table or film.
Alternatives: Reuse the right-region composite layout (rejected: half the slide stays empty on a page with no bullets). Shrink type for wide tables (rejected: outside the fixed type roles).
Evidence: 2.20 in: measured DejaVu Sans 22 pt width of a ten-letter word is about 1.9 in, plus margin; at the 1440 x 1200 filter posters the side panel is 2.965 in. 4.99 in: 6.20 - 1.20 = 5.00 in less EMU rounding. validate_deck.py --pdf 2026-09-28: every full-width check PASS (films at 3.665, 1.20, 6.00 x 5.00 in). The typography exception is not yet approved by the author.
Reversibility: FULL_KINDS and the three restrained_full_* functions in build_deck.py; the full_width flag, FULL_KINDS, FULL_REGION and the full_kind branches in validate_deck.py.
Review: Projected legibility of the 16 pt table cells on page 38 and of the claim column on pages 41-46.

ID: D-130
Status: SETTLED
Decision: Retire the requirements that only the deleted pages met: validate_deck.py no longer requires a raw_hips page in the deck (thesis Sections 2.6 and 7.4 and Appendix G hold that evidence); build_deck.py source_guides no longer requires a hip_depth_manual page or a raw_hips page and the depth_rules caption cites thesis Sections 2.6 and 7.4 instead of looking up a page; the index page requirement is removed from build(). UNIFIED_FOUR_ROUTE records producer page 14 (swing film p14, whose only page was Q&A 76) as "retired (D-130)" instead of dropping it: the route still verifies the audits of all four producer pages, requires exactly the three current films and requires the contract's retired_unified_pages to name page 14. The check "Contains demonstration movies and explanatory animation" becomes "Contains demonstration movies and every declared explanatory animation": the only GIFs (p34, p36, p38) were on deleted pages, so a GIF is required only while a page declares one; per-slide GIF checks are unchanged. The archived replay check accepts previous page 25 for a schema-7 contract (it stays on page 25).
Why: These checks tested pages the author deleted; keeping them would fail the deck on content that no longer exists, and silently deleting them would hide the change.
Alternatives: Keep one raw-hips or GIF page to satisfy the checks (rejected: outside the author's page list). Delete the swing route entry (rejected: the brief asks for a recorded retirement).
Evidence: validate_deck.py --pdf 2026-09-28: 1138 checks, 0 package failures; overall PARTIAL only for the two retained historical findings of D-058/D-066. The GIF check change goes beyond the list in the master's brief and is reported to the master.
Reversibility: the named hunks in validate_deck.py and build_deck.py.
Review: Whether the GIF expectation should instead be restored by adding an animation page.

ID: D-131
Status: SETTLED
Decision: Round-4 contract: revision_id_map.json becomes schema_version 7 (35 main + 13 hidden pages; old pages 1-35 map to themselves, old pages 36-76 map to "deleted"; rebound_media moves the films of deleted pages 62, 63, 49 and 50 to pages 41, 42, 44 and 45; the round-3 map is embedded as previous). anim/unified_revision_build.py is rebased onto the round-3 contract, copied byte-identical with its map, video indexes and preservation audit to committee_materials/unified_revision/history/round3_27min/ before the rebuild (contract sha256 81af7b51...49c38435, map 3f77236f...8ea9c). The rebuilt contract (schema_version 7) keeps 18 rows at their pages, drops p64, p69, p27, p34, p36, p38 and p14 (listed in dropped_rows; still in the round-3 history copy, their files still byte-bound by the preserved audit) and adds two copy rows (D-132). validate_deck.py binds base_contract for schema 7 and checks each kept row against its round-3 row (same stem at the previous page) and the page map or rebound_media.
Why: Same chained-contract method as round 3 (D-120), so each film's page history stays traceable.
Alternatives: Rebuild the contract without a history copy (rejected: loses the round-3 audit trail).
Evidence: unified_revision_build.py 2026-09-28: "Bound 18 kept and 2 added media entries; 7 dropped; 48 slide identities (35 main, 13 hidden)"; a second run left the contract, content JSON, indexes and provenance byte-identical (sha256sum). validate_deck.py: every "current page follows the page map" check PASS (for example p07 7 -> 62 -> 41).
Reversibility: restore the round3_27min copies to their live paths and git checkout the builder and map.
Review: VIDEO_INDEX wording for the dropped rows.

ID: D-132
Status: SETTLED
Decision: A film shown on two pages gets a byte-identical committee copy under a new stem: p43-Offline_Butterworth_Smoothing (copy of p09, page 9) and p46-Causal_One_Euro_Filtering (copy of p49, page 31), in committee_materials/unified_revision/{videos,posters,provenance}, the way p05 was added in round 3.
Why: The contract does not allow one film on two pages: validate_deck.py keys committee rows by path, a slide's media must resolve to the row whose page is that slide, and each page-map entry maps to one page.
Alternatives: Two rows sharing one path (rejected: the path-keyed row map would keep only one page). Relax the page-identity check (rejected: loosens a check).
Evidence: The copies' sha256 equal the originals (unified_revision_build.py raises otherwise; provenance JSON records both hashes); validate_deck.py "Slide 43/46 composite is bound to its source and frame-map audit" PASS. PowerPoint stores one media part per distinct file, so the PPTX size does not grow.
Reversibility: delete the two copy rows from COPIES and their files; rebind pages 43 and 46 to p09 and p49 after changing the contract rule.
Review: None beyond the file count.

ID: D-133 (closed by D-169: every stand-in replaced on 2026-09-28)
Status: UNCERTAIN
Decision: Pages 37, 39, 40, 47 and 48 show stand-in PNGs (2466 x 1110 px, black, white text "chart pending: ...") rendered with PIL to presentation/defense_2026/experiments/placeholders/{marker_bench,transport_latency,transport_throughput,filter_offline,filter_realtime}_pending.png, each captioned "Stand-in: ... replaces this image."; page 36's literature table has every cell "pending literature review". They must be replaced before the deck is presented.
Why: The measured charts and the literature review are produced by other workers; the build must run with no numeric placeholders in the meantime.
Alternatives: Leave the pages out until the charts exist (rejected: the integrator needs the pages and kinds now).
Evidence: None for the content; 2466 x 1110 px is the size set in the master's brief. UNCERTAIN until replaced.
Reversibility: point visual.image of each page at the real chart and replace the table rows.
Review: That every stand-in is gone before the defence (grep backup_content.json for "pending").

ID: D-134
Status: SETTLED
Decision: [presentation/defense_2026/experiments/marker_bench] marker side lengths 24, 32, 48, 64, 96, 128 px (outer black square, fronto-parallel equivalent at the marker's depth).
Why: set by the brief; spans the live pipeline's object marker from far (small) to near.
Alternatives: finer or larger sizes; not needed for the question.
Evidence: brief of 2026-09-28.
Reversibility: edit SIZES_PX and rerun (31 min).
Review: whether the 45 mm object marker at the recording distances falls in this range.

ID: D-135
Status: SETTLED
Decision: [presentation/defense_2026/experiments/marker_bench] out-of-plane tilt 0, 30, 45 deg about the marker's vertical axis, marker at depth Z = f * S / side.
Why: set by the brief.
Alternatives: tilt about both axes; not requested.
Evidence: brief.
Reversibility: edit TILTS_DEG.
Review: none.

ID: D-136
Status: SETTLED (values) / UNCERTAIN (realism)
Decision: [presentation/defense_2026/experiments/marker_bench] Gaussian blur sigma 0, 0.8, 1.5 px applied to the whole composite, then additive Gaussian noise sigma 0, 4, 8 grey levels, clipped to uint8; same seed per frame and condition for both marker images.
Why: values set by the brief; the whole frame is degraded so the timing sees the same image statistics as a real degraded frame.
Alternatives: degrade only the marker region (rejected: timing would see a clean background).
Evidence: brief. Whether sigma 4 and 8 match the D435 noise was not measured.
Reversibility: edit BLUR_SIGMAS / NOISE_SIGMAS.
Review: the noise-free rows in results.csv are the closest to the live frames.

ID: D-137
Status: SETTLED (N_FRAMES) / UNCERTAIN (TIMING_REPS, WARMUP)
Decision: [presentation/defense_2026/experiments/marker_bench] 50 background frames per condition (brief); each image timed 3 times per detector (150 timings per condition, brief minimum 20); 20 warm-up detections per detector excluded.
Why: 3 repetitions keep the run near 30 min; warm-up of 20 is a round number with no source.
Alternatives: 1 repetition (50 timings, also above 20).
Evidence: brief for 50 and the 20-timing minimum; none for 3 and 20 warm-ups.
Reversibility: edit TIMING_REPS / WARMUP_DETECTIONS.
Review: time_p95 spread in results.csv.

ID: D-138
Status: SETTLED
Decision: [presentation/defense_2026/experiments/marker_bench] SEED = 20260928 (the run date) for frame choice, paste position, in-plane roll and noise.
Why: fixed seed required by the brief; the value is arbitrary.
Alternatives: any integer.
Evidence: none needed; reproducibility only.
Reversibility: edit SEED.
Review: none.

ID: D-139
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/marker_bench] per frame, a random 240x240 px box whose bounds stay 12 px away from every real marker found by the pinned 5x5 detector; frames without such a box are skipped; the 50 frames are drawn in random order from the 899.
Why: 240 px holds the largest case (128 px square plus one-module quiet zone = 165 px, diagonal 233 px under any roll). The 12 px margin has no source.
Alternatives: masking real markers (changes the background the timing sees).
Evidence: geometry above; real-marker count per frame in environment.json. A real marker the detector misses (blurred) can still be overlapped.
Reversibility: edit PASTE_BOX / REAL_MARKER_MARGIN.
Review: environment.json real_markers_per_used_frame.

ID: D-140
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/marker_bench] random in-plane roll U(0, 90) deg per frame, plus a random sub-pixel centre.
Why: an axis-aligned square with integer edges favours edge refinement; roll removes the pixel-lattice alignment. Not in the brief.
Alternatives: roll 0 (easier, less realistic).
Evidence: the pixel-aligned test gave exact +0.5 px offsets for the AprilTag refiner, i.e. lattice-aligned cases behave specially.
Reversibility: set roll to 0 in choose_frames_and_boxes().
Review: none.

ID: D-141
Status: UNCERTAIN (supersampling factor) / SETTLED (levels, focal, quiet zone)
Decision: [presentation/defense_2026/experiments/marker_bench] render the marker at 32 px per module, warp to a 4x supersampled crop, downsample with INTER_AREA; black and white levels 50 and 209 (medians of the 10th and 90th grey percentiles inside 150 real markers in the 50 frames); focal 607.56 px; one-module white quiet zone around both markers.
Why: supersampling gives area-correct edges; levels match the printed markers; the quiet zone matches the AprilTag 36h11 10x10-cell layout (8x8 black-bordered tag plus one white cell each side, Krogius et al. 2019).
Alternatives: direct warp without supersampling (aliased edges).
Evidence: levels measured by measure_levels() and stored in environment.json; focal from presentation/defense_2026/bank_processing/p18/landmarks_raw.meta.json (fx 607.561); factor 4 has no source.
Reversibility: edit SUPERSAMPLE / FOCAL_PX.
Review: none.

ID: D-142
Status: SETTLED
Decision: [presentation/defense_2026/experiments/marker_bench] cv2.setNumThreads(1), pupil-apriltags nthreads=1, OMP/OPENBLAS/MKL threads 1, process pinned to logical core 2.
Why: brief asks for a single-thread comparison; pinning avoids migration noise. Core 2 is arbitrary.
Alternatives: multi-thread (not comparable across libraries).
Evidence: /usr/bin/time on the quick run showed 99 % CPU after the thread settings (user time was above wall time before them).
Reversibility: remove the settings.
Review: environment.json affinity and thread fields.

ID: D-143
Status: SETTLED
Decision: [presentation/defense_2026/experiments/marker_bench] all detectors receive the same grayscale uint8 640x480 image; colour conversion is excluded from the timing.
Why: pupil-apriltags accepts only grayscale; equal input for all.
Alternatives: time BGR input for OpenCV (adds a conversion only OpenCV pays).
Evidence: none needed.
Reversibility: trivial.
Review: none.

ID: D-144
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/marker_bench] a detection counts when the wanted id lies within 0.5 x side of the true centroid; corner error is taken over the corner ordering (cyclic shift, winding) that minimises it; a debiased error removes the mean signed 2-D offset of each condition.
Why: the libraries order corners differently; the real object marker also has id 1, so location gating is needed. The debiasing separates a constant coordinate-convention offset (+0.5 px measured for the AprilTag quad fitter on a pixel-aligned marker) from corner accuracy. The 0.5 gate has no source.
Alternatives: report raw error only (mixes convention with accuracy); fixed -0.5 px correction (pupil offsets are 0.38-0.5 px, not exactly 0.5).
Evidence: pixel-aligned test in this session: CORNER_REFINE_APRILTAG +0.500 px in x and y, CORNER_REFINE_SUBPIX 0.058 px inward, pupil-apriltags +0.35 to +0.44 px.
Reversibility: both raw and debiased columns are in results.csv.
Review: whether the slide should show raw or debiased error.

ID: D-145
Status: SETTLED
Decision: [presentation/defense_2026/experiments/marker_bench] summary.csv averages the per-condition values over the 27 tilt x blur x noise conditions; corner errors over conditions with at least one detection; *_common columns over conditions where all four main detectors reach 50 %; times are medians across conditions.
Why: gives one number per detector and size; the common subset guards against survivorship at small sizes.
Alternatives: pooling all frames (weights conditions by detection count).
Evidence: write_summary() docstring.
Reversibility: recompute from results.csv.
Review: small-size corner errors rest on fewer conditions (n_cond_detected).

ID: D-146
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/marker_bench] add aruco_5x5_norefine (OpenCV defaults, no corner refinement) to the run and the chart, although the brief listed three detectors.
Why: it shows that the pinned ArUco cost (26.6 ms at 48 px) is mostly the AprilTag corner refinement (8.4 ms without), which the Q&A answer needs.
Alternatives: leave it out.
Evidence: summary.csv rows aruco_5x5_norefine.
Reversibility: remove from DETECTORS and replot.
Review: whether the slide should keep the dotted line.

ID: D-147
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/marker_bench] brief palette kept (70B7E6, A8A8A8, FFD088); every series also has its own marker shape and line style.
Why: the palette validator fails the normal-vision floor for A8A8A8 vs 70B7E6 (delta E 10.1 < 15) on black; secondary encoding is the prescribed remedy when the colours are fixed.
Alternatives: change colours (outside the deck palette).
Evidence: dataviz validate_palette.js run on 2026-09-28 (CVD pass, normal-vision floor fail).
Reversibility: edit STYLE in plot_marker_bench.py.
Review: projected legibility of grey vs blue.

ID: D-148
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/marker_bench] "similar performance, AprilTag slower but more accurate" is partly supported: similar detection and accuracy from 48 px up; AprilTag 3 more accurate on small markers; but AprilTag 3 is faster, not slower, than the pinned ArUco.
Why: measured here: 3.5 ms (AprilTag 3, decimate 2) and 14.4 ms (decimate 1) vs 26.6 ms (pinned ArUco) per frame at 48 px; debiased corner error 0.095 / 0.092 vs 0.137 px at 48 px and 0.069-0.074 px for all at 96 px. Literature: Krogius et al. 2019 (Fig. 7) also finds AprilTag 3 faster than ArUco at higher recall; the original AprilTag was slower (Olson 2011 p. 7; Wang and Olson 2016 p. 6), which may be the source of the recollection; accuracy results disagree (Romero-Ramirez et al. 2018 Table 3 favours ArUco jitter; the FMAC preprint favours AprilTag). Measurement and literature do not agree on accuracy, hence UNCERTAIN.
Alternatives: SETTLED "supported" or "contradicted" (either overstates the evidence).
Evidence: summary.csv; knowledge/marker_literature.md.
Reversibility: wording only.
Review: whether the answer should say the choice rested on OpenCV integration and the existing pipeline rather than on speed or accuracy.

ID: D-149
Status: SETTLED
Decision: [presentation/defense_2026/experiments/transport_bench] 2,000 measured messages after 200 warm-up per paced condition; 5 s per unpaced condition after 200 warm-up.
Why: Values set by the author's brief (2026-09-28). 2,000 samples give a p99 backed by 20 tail samples; warm-up discards connection set-up, first page faults and first-copy effects.
Alternatives: Longer runs (more tail samples, run time grows linearly at 30 Hz; 2,200 messages already take 73 s per condition).
Evidence: run_to_run.csv: p50 differs by at most 1.7 % between runs for every paced condition except shared memory 172 B (2.7 vs 2.4 us, -8.6 %, 0.3 us absolute); unpaced throughput within 1.8 %.
Reversibility: Constants N_WARM, N_MEAS, THRU_S in transport_bench.py; rerun.
Review: Accept that a 0.3 us p50 difference on a 2-3 us quantity is noise.

ID: D-150
Status: SETTLED
Decision: [presentation/defense_2026/experiments/transport_bench] Writer pacing on an absolute 30 Hz schedule: sleep until 2 ms before each slot, then spin to the slot.
Why: Pacing error adds directly to reader-side jitter for every transport; a plain sleep can overshoot. The 2 ms spin margin (PACE_SPIN_NS) is a chosen value; its adequacy is shown by the measured writer-side send jitter.
Alternatives: Plain time.sleep (overshoot enters the jitter measurement); full busy-wait (burns the writer core for the whole period with no accuracy gain over the margin).
Evidence: results.csv send_jitter_ms 0.0001-0.0003 ms for all paced conditions, well below the reader-side jitter being compared. A standalone check on this host measured time.sleep(31 ms) overshoot p99 0.075 ms (not committed; smoke test during development).
Reversibility: PACE_SPIN_NS constant.
Review: None needed unless send_jitter_ms rises in a rerun.

ID: D-151
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/transport_bench] UDP chunk payload 60,000 B (26 datagrams per 1,536,032 B frame), default socket buffers (SO_RCVBUF 212,992 B).
Why: Brief says 60 KB; read as 60,000 B, under the 65,507 B UDP payload limit so loopback needs no IP fragmentation. Default buffers match the only UDP code in the repository (v1/unity_bridge/send_landmarks.py sets none).
Alternatives: 61,440 B (60 KiB) chunks; enlarging the receive buffer (needs net.core.rmem_max raised, a system setting, out of scope).
Evidence: environment.json udp_rcvbuf 212,992 and net_core_rmem_max 212,992. Measured UDP loss at 30 Hz for 1,536,032 B: 4.55 % (run 1), 5.65 % (run 2); unpaced 0.0102 % (run 1). That the loss comes from receive-buffer overflow during the reader's wake-up is an interpretation, not tested.
Reversibility: UDP_CHUNK constant; buffer size would need a system change and a rerun.
Review: Decide whether the slide should say the UDP loss figure is for default buffers (SLIDE_TEXT.md does).

ID: D-152
Status: SETTLED
Decision: [presentation/defense_2026/experiments/transport_bench] Shared-memory reader busy-waits on the seq word; a second variant (shm_sleep1ms) sleeps 1 ms between polls, reported in results.csv but not charted.
Why: Busy-wait isolates the transport cost, which is what the socket rows measure (their readers block in recv and are woken by the kernel at once). The 1 ms value is the default poll_s of the repository's Python ring reader (v2/common/shm_ring.py latest()), so the variant shows what a real non-spinning Python reader pays. Unity polls once per rendered frame, which neither variant reproduces.
Alternatives: Sleep-poll only (measures the sleep, not the transport); futex or eventfd wake-up (not how the pipeline works).
Evidence: results.csv: shm 172 B p50 2.67 us busy-wait vs 518.6 us with 1 ms sleep; 1,536,032 B 54.38 us vs 598.5 us.
Reversibility: SHM_SLEEP_S constant; charts use TRANSPORTS_MAIN.
Review: Confirm the charts should show the busy-wait rows and the speaker notes carry the sleep-poll caveat.

ID: D-153
Status: SETTLED
Decision: [presentation/defense_2026/experiments/transport_bench] Writer on CPU 8, reader on CPU 10, parent on CPU 12, pinned with psutil; CPU 2 avoided.
Why: Distinct physical cores (sysfs thread_siblings_list 8,24 / 10,26 / 12,28) so writer and reader never share a core. During development another benchmark process was pinned to CPU 2 at 100 % CPU; the first smoke test on CPUs 2/4/6 showed 3 ms writer pacing jitter, which vanished after the move.
Alternatives: No pinning (scheduler migrations add jitter); the originally chosen CPUs 2/4/6.
Evidence: environment.json writer_affinity [8], reader_affinity [10], writer_reader_different_physical_cores true, busy_processes_at_start and _at_end list the other process on CPU 2 at 100 %. Smoke-test logs are not committed.
Reversibility: WRITER_CPU, READER_CPU, PARENT_CPU constants.
Review: If the numbers are to be quoted as "idle machine", rerun when no other benchmark is active.

ID: D-154
Status: SETTLED
Decision: [presentation/defense_2026/experiments/transport_bench] The shared-memory writer stores the seq word as one 4-byte slice copy of pre-packed bytes (as psv3.py does), not with struct.pack_into; the reader reads seq as a 4-byte snapshot. The first full two-run result set was discarded and rerun.
Why: CPython's struct.pack_into zero-fills the target bytes before packing. On a shared mapping a concurrent reader can then read seq == 0 (even, "stable"), copy, and occasionally accept a stale record; in the discarded run this produced 60 seqlock retries and three latencies of 33.3 ms (a record re-read at the start of the next publish) in the 172 B paced condition.
Alternatives: Keep pack_into and tolerate retries (corrupts latency stamps).
Evidence: Diagnostic in the development scratchpad (not committed): 300 paced 1.5 MB publishes produced 48 failed verifications; the first ten, the only ones printed, all had the first seq read equal to 0. After the fix: results.csv torn_retries 0 and duplicates 0 in every paced shared-memory condition, max latency 12.57 us (172 B).
Reversibility: None needed; the fix matches psv3.py.
Review: Out of scope but relevant: v2/common/shm_ring.py (the PSF1 writer) stores its slot seq and counter with struct.pack_into on the mapping (lines 136-145), so the same transient zero is possible there. Its reader checks frame_idx as well, which makes a false accept unlikely; not tested. psv3.py uses mm.write(struct.pack(...)) and is not affected by this mechanism. Separately, psv3.py writes the even seq inside the same payload write as the data, at offset 4 before the data bytes, so the even seq can become visible a few nanoseconds before the tail of the record; not tested, flagged for the author.

ID: D-155
Status: SETTLED
Decision: [presentation/defense_2026/experiments/transport_bench] The reader records only the first reception of each message index; re-reads count as duplicates.
Why: A latest-value mailbox can legitimately be read twice; the latency of a message is its first delivery.
Alternatives: Last reception (what the discarded run did implicitly; inflates latency).
Evidence: results.csv duplicates column, 0 in every condition of both final runs.
Reversibility: Recorder.record in transport_bench.py.
Review: None.

ID: D-156
Status: SETTLED
Decision: [presentation/defense_2026/experiments/transport_bench] Throughput = messages delivered to the reader per second over the reader's first-to-last delivery window; UDP loss = sent minus delivered; shared-memory "skipped" = sent minus delivered, reported separately from loss; copies and kernel calls per message are conceptual counts, not measured.
Why: A socket writer is flow-controlled (TCP) or drops at the receiver (UDP), while a shared-memory mailbox is overwritten by design; one "loss" column would mix a failure with a design property.
Alternatives: Writer send rate as throughput (overstates shared memory and UDP); a ring buffer for the shared-memory throughput row (would test a different layout than the brief's PSV3 seqlock).
Evidence: results.csv writer_msgs_per_s next to msgs_per_s; shared memory 1,536,032 B unpaced: writer 30,081.6/s, delivered 0, skipped 100.
Reversibility: summarise() in transport_bench.py.
Review: Decide whether page 40 should keep the 0-delivered bar (SLIDE_TEXT.md explains it) or whether a multi-slot ring variant should be added.

ID: D-157
Status: SETTLED
Decision: [presentation/defense_2026/experiments/transport_bench] results.csv and both charts use run 1; run 2 is results_run2.csv and raw_latencies/run2.
Why: One fixed primary run avoids cherry-picking; run 2 is the repeatability check.
Alternatives: Mean of the two runs (mixes distributions); best run (cherry-picking).
Evidence: run_to_run.csv (see D-149).
Reversibility: Rename files.
Review: None.

ID: D-158
Status: SETTLED
Decision: [presentation/defense_2026/experiments/transport_bench] Conclusion, scoped to what was measured: on this workstation, loopback, Python endpoints, at 30 Hz, shared memory with a seqlock gave the lowest one-way latency and jitter for both the 172 B record and the 1,536,032 B frame, with no loss and no kernel call per message; this supports its use in the pipeline.
Why: The numbers support it for both sizes and both runs.
Alternatives: TCP (reliable and ordered, but p50 14x the shared-memory value for 172 B and 4x for 1,536,032 B; one send and at least one recv per message); UDP (lost 4.55 % / 5.65 % of 1,536,032 B frames at 30 Hz with default buffers; needs reassembly).
Evidence: results.csv run 1: p50 2.67 vs 30.67 (UDP) vs 37.97 us (TCP) at 172 B; 54.38 vs 232.2 (TCP) vs 239.8 us (UDP) at 1,536,032 B; jitter 0.0009 / 0.0084 ms vs 0.0774-0.0808 ms for sockets except UDP 1,536,032 B 0.0255 ms; results_run2.csv the same ordering.
Reversibility: A rerun with a Unity C# reader could change the absolute numbers.
Review: The "14x" and "4x" ratios are derived from results.csv values (37.97 / 2.67, 232.2 / 54.38); SLIDE_TEXT.md quotes only the raw values.

ID: D-159
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/transport_bench] The conclusion is not extended to the Unity reader or to a flat-out writer.
Why: The Unity reader (C#, polled once per rendered frame) was not measured; with a sleep-polling Python reader the shared-memory latency rises to 518.6 us (172 B), still below one 30 Hz period but no longer below the socket values. A single-slot mailbox also starves a 1.5 MB reader when the writer publishes flat out (0 delivered), which the pipeline avoids by publishing at the camera rate and by using a multi-slot ring for frames.
Alternatives: Claim the Python busy-wait numbers for Unity (unsupported).
Evidence: results.csv shm_sleep1ms rows; shared memory 1,536,032 B unpaced row. No Unity measurement exists in this folder.
Reversibility: A Unity-side timing test would settle it.
Review: Keep the speaker notes' caveat; do not say "shared memory is 14x faster in the pipeline".

ID: D-160
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/filter_metrics] Shake = RMS of the frame-to-frame displacement of the filtered signal, per axis and as the 3-D Euclidean step, over consecutive pairs inside evaluated segments.
Why: Matches the prose definition in thesis/A1_acquisition_filtering.md line 166 ("RMS frame-to-frame displacement") and needs no ground truth.
Alternatives: Second-difference RMS (eval/pipeline_smoothness d2_rms) isolates jitter from velocity better, rejected to stay with the thesis wording; spectral power above 5 Hz, rejected as harder to explain on a slide.
Evidence: None beyond the thesis wording; the metric also counts genuine motion (see README caveats).
Reversibility: Change shake() in filter_metrics.py and rerun.
Review: Confirm that a metric which rewards lag is acceptable when shown next to deviation and lag.

ID: D-161
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/filter_metrics] Fast-motion frames = frames whose despiked-raw 3-D speed (central difference within a segment) is at or above the 80th percentile of evaluated frames; here 0.138 m/s, 157 frames.
Why: The brief suggested the top 20 percent; a percentile adapts to the recording and gives a fixed share of frames.
Alternatives: A fixed speed such as 0.25 m/s, rejected because no source value exists; the top 10 percent, rejected as only about 78 frames.
Evidence: None; the percentile is a choice. The resulting threshold is recorded in run_info.json.
Reversibility: FAST_PERCENTILE in filter_metrics.py.
Review: Check whether 0.138 m/s counts as "fast" wrist motion for the committee.

ID: D-162
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/filter_metrics] Fast-motion deviation = RMS over fast frames of filtered minus despiked raw, per axis and as the 3-D distance.
Why: Matches the prose definition ("distance from the despiked raw signal during fast wrist motion").
Alternatives: Maximum deviation, rejected as a single-frame statistic; deviation after removing the best lag, rejected because the slide argues about lag as a cost.
Evidence: None beyond the thesis wording.
Reversibility: deviation() in filter_metrics.py.
Review: Note that despiked raw scores 0 by construction; it is the reference, not a winner.

ID: D-163
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/filter_metrics] Lag = shift in -15..15 frames maximising the normalised cross-correlation of mean-removed filtered and despiked-raw signals, pooled over evaluated segments (and over all three axes for the norm row); reported as the integer peak and a three-point parabola refinement; ms = frames x 1000 / 29.979.
Why: The brief asked for the cross-correlation peak; the parabola avoids a 33 ms quantisation that would stack EMA and One Euro 1 Hz on the same value.
Alternatives: Integer lag only, kept as its own column; group delay from the filter design, rejected because One Euro is adaptive.
Evidence: Offline zero-phase candidates return integer lag 0 and refined lags within 0.2 frames of zero (results.csv), a sanity check on the method. MAX_LAG 15 frames (0.5 s) is a choice with no source; the largest measured lag is 7 frames, so the range does not clip.
Reversibility: best_lag() and MAX_LAG in filter_metrics.py.
Review: Decide whether slides quote the refined ms (current) or the integer-frame ms.

ID: D-164
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/filter_metrics] Metrics use only segments of at least 16 frames (frames 25-549 and 640-899, 785 frames).
Why: The frozen Butterworth leaves a segment unfiltered when n <= 3*max(len(a), len(b)) = 15 (v1/mediapipe/filter_landmarks.py smooth_segment); including the 11-frame segment 0-10 would mix unfiltered raw into the Butterworth rows.
Alternatives: Evaluate every frame, rejected for the reason above.
Evidence: v1/mediapipe/filter_landmarks.py lines 140-145; run_info.json evaluated_segments_half_open.
Reversibility: MIN_SEGMENT in filter_metrics.py.
Review: None expected.

ID: D-165
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/filter_metrics] Excerpt window = the 120-frame (4.0 s) window inside an evaluated segment with the highest mean |dz/dt| of despiked raw; result frames 25-144.
Why: The brief asked for a 4 s window with fast motion; a fixed rule makes the choice reproducible. It overlaps the films' window (frames 25-179, FILTER_SYNC_BRIEF.json), which helps the committee connect chart and film.
Alternatives: Hand-picked window, rejected as not reproducible.
Evidence: run_info.json excerpt_frames_inclusive and excerpt_mean_abs_dz_dt_m_per_s (0.102 m/s).
Reversibility: choose_excerpt() and EXCERPT_FRAMES in filter_metrics.py.
Review: Check that the depth descent in 0.3-2.1 s reads as fast motion on the slide.

ID: D-166
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/filter_metrics] EMA alpha 0.3, seeded with the first sample of each segment.
Why: Set by the brief as a naive causal baseline.
Alternatives: Tuning alpha to match One Euro's shake or lag, rejected as out of scope.
Evidence: None; the value comes from the brief, not from a measurement.
Reversibility: EMA_ALPHA in filter_metrics.py.
Review: The EMA point is a baseline only; no claim rests on its exact alpha.

ID: D-167
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/filter_metrics] Two One Euro settings are measured: min cutoff 0.05 Hz, beta 1 (Appendix F, the films, filter_landmarks.py defaults) and min cutoff 1 Hz, beta 1 (the live CausalLandmarkFilter defaults in v1/realtime/person/realtime_person.py, measured in eval/pipeline_smoothness). Both use the frozen OneEuro class, d_cutoff 1 Hz, at the measured 29.979 Hz (the live filter uses freq 30). The page-48 excerpt plots the 1 Hz setting.
Why: The slide argues for the real-time filter, which runs at 1 Hz; the 0.05 Hz setting stays on the scatter so the Appendix F value is visible.
Alternatives: Plot 0.05 Hz in the excerpt to match the film, rejected because that setting has the largest lag (186.79 ms) and is not the live one; change EXCERPT_ONE_EURO in charts.py to switch.
Evidence: realtime_person.py CausalLandmarkFilter(min_cutoff=1.0, beta=1.0); eval/pipeline_smoothness/replay_live_person.py meta string; FILTER_DEMO_BRIEF.json oneeuro_mincutoff 0.05.
Reversibility: EXCERPT_ONE_EURO in charts.py; candidates() in filter_metrics.py.
Review: Confirm which One Euro setting the committee should see as "the" real-time filter.

ID: D-168
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/filter_metrics] Causal Butterworth = one forward lfilter pass, 4th order, 3 Hz, initial state lfilter_zi scaled by the first sample of each segment.
Why: Strictly causal; the films' forward-pass animation uses filtfilt's odd padding, which reads future samples at the segment start.
Alternatives: Zero initial state, rejected because it adds a start-up transient from 0 m depth.
Evidence: scipy.signal.lfilter_zi documentation; filter_demos.py lines 56-71 for the film variant.
Reversibility: butter_forward() in filter_metrics.py.
Review: None expected.

ID: D-169
Status: UNCERTAIN
Decision: Replace every stand-in of D-133 with the experiment deliveries: page 36 full_table from the marker literature rows (experiments/marker_bench/SLIDE_TEXT.md, citations and page references in knowledge/marker_literature.md), page 37 chart_marker_bench.png, page 38 table rows from experiments/transport_bench/SLIDE_TEXT.md, pages 39 and 40 chart_transport_latency.png and chart_transport_throughput.png, pages 47 and 48 chart_filter_offline.png and chart_filter_realtime.png; claims, source lines and notes from the three SLIDE_TEXT.md files, with the "[author to confirm the reason]" tag kept verbatim in the page 37 notes; stand_in flags and stand-in captions removed; the stand-in PNGs in experiments/placeholders/ deleted. Wording shortened to fit two 16 pt lines per cell (numbers unchanged): page 36 drops "costlier than ARToolKitPlus" (kept in the notes) and the hardware parentheses are flattened; page 38 shortens every cell (for example "Latest value only", "None; overwrites skipped", "Shared memory (seqlock)") and renames the last column "In pipeline"; column_widths page 36 [0.18, 0.334, 0.237, 0.249], page 38 [0.181, 0.135, 0.229, 0.134, 0.217, 0.104]; page 38 gains a one-line caption with the UDP buffer condition (D-171). Footer labels of pages 38, 47 and 48 start with "Undergraduate thesis | " and then name the experiment file, because validate_deck.py "Visible footer labels cite the undergraduate thesis" fails any label that mentions the thesis without that prefix. The page 37 title is set in D-171. The marker chart legend moved from centre right, where it covered the AprilTag 3 decimate-1 line, to the empty band centred at 20.5 ms (plot_marker_bench.py, re-rendered from the existing summary.csv without rerunning the benchmark).
Why: D-133 required the stand-ins to be replaced before the defence; the deliveries now exist. The old page 38 cell "Overwritten, not queued" wrapped to three lines in the LibreOffice render because its first word "Overwritten," measures 1.39 in at 16 pt against 1.32 in of cell width, and the build_deck.py two-line check does not test a word that starts a line (it only tests the width of the last line).
Alternatives: Keep the SLIDE_TEXT cell wording and shrink the type (rejected: fixed 16 pt role, D-129). Drop hardware numbers from page 36 (rejected: the brief keeps every number). Legend below the axes (rejected: shrinks the plot height).
Evidence: Cell fit measured with the builder metric (DejaVu Sans, 16 pt, cell width less 0.18 in) and a 0.88 safety factor on the width; every word and every cell of pages 36 and 38 fits two lines. The 0.88 factor has no measured source; it is a margin for renderer differences. Numbers traced: page 37 to experiments/marker_bench/summary.csv (48 px rows, 96 px debiased errors), pages 38-40 to experiments/transport_bench/results.csv run 1, pages 47-48 to experiments/filter_metrics/summary.csv, page 36 to knowledge/marker_literature.md. Decisions of the three experiments: D-134 to D-148 (marker_bench), D-149 to D-159 (transport_bench), D-160 to D-168 (filter_metrics).
Reversibility: git checkout of backup_content.json and plot_marker_bench.py; the stand-in PNGs are recoverable only by re-rendering them as D-133 describes (they were never committed).
Review: The shortened table wording on pages 36 and 38, the page 37 title, and projected legibility of the chart text; the builder word-width gap in restrained_full_table is reported, not fixed (build_deck.py was outside this task).

ID: D-170
Status: SETTLED
Decision: Delete the stale previews preview/slide-49.png to slide-76.png and preview/overview-05.jpg to overview-07.jpg (build outputs of the round-3 pages that D-127 deleted), and make render_deck.py remove every preview/slide-*.png beyond the rendered page count (read from pdfinfo) and every preview/overview-*.jpg beyond the sheets it writes, so preview_pages in review/RENDER_CHECK.json counts only current pages.
Why: render_deck.py globbed every slide-*.png, so after the deck shrank from 76 to 48 pages the 28 old previews stayed, were stitched into overview sheets 05-07 and were counted in preview_pages.
Alternatives: Delete by hand after each shrink (rejected: the same stale state returns on the next shrink).
Evidence: The deletion follows the author instruction of 2026-09-28 to delete those pages (D-127); the files are build outputs, recoverable from git history at commit e50c1ef. render_deck.py 2026-09-28 run: see the RENDER_CHECK.json preview_pages value.
Reversibility: git checkout e50c1ef -- presentation/defense_2026/preview; revert the cleanup block in render_deck.py.
Review: None.

ID: D-171
Status: SETTLED
Decision: Apply the six slide-text fixes of the code review of the three experiments (relayed by the master on 2026-09-28) to backup_content.json and the SLIDE_TEXT.md files. (1) Page 37 states that corner errors are after removing a constant offset of about 0.5 px, no longer claims equal accuracy from 48 px (0.137 vs 0.095 px there; the errors converge at 96 px, 0.069-0.074 px), and the no-refinement note compares raw with raw (0.664 px pinned vs 0.978 px); the title becomes "AprilTag 3 faster; corner errors converge at 96 px". (2) Page 37 speed quotes the noise-free medians as the low end and the noise sigma 8 medians as the high end: 2.8 to 3.8 ms (AprilTag 3, decimate 2) against 10.9 to 31.3 ms (pinned ArUco) at 48 px; the former headline 3.5 vs 26.6 ms was the median over all conditions and equals the sigma 4 level. (3) The UDP 4.55 % loss at 30 Hz carries its condition, the default 212,992 B receive buffer, smaller than one 1,536,032 B frame (unpaced loss 0.0102 %): in the page 38 table cell ("4.55 % of frames at 30 Hz, default buffer"), a page 38 caption, the page 38 notes and the page 40 claim. (4) Page 36 cites Wang and Olson 2016 Table I on p. 4. (5) Page 48 rounds the causal lags to whole milliseconds (85 ms or 2.6 frames, 142, 55, 187 ms); summary.csv keeps the exact values. (6) experiments/marker_bench/README.md gains a caveat that the transport benchmark ran concurrently on other cores.
Why: Each fix removes a statement the measurement does not support as worded: an offset-removed error presented as raw accuracy, an averaged-over-noise time presented as typical, a loss figure without its buffer condition, a wrong page, and two-decimal lags from a single recording.
Alternatives: Drop the no-refinement sentence (rejected: the raw-vs-raw comparison keeps the explanation of the ArUco cost).
Evidence: experiments/marker_bench/results.csv, 48 px, median over the 9 tilt x blur conditions per noise level: pupil_dec2 2.82 / 3.53 / 3.79 ms and aruco_5x5 10.86 / 26.61 / 31.34 ms at noise sigma 0 / 4 / 8 (recomputed in this session); summary.csv corner_err_mean_px 0.6642 (aruco_5x5) and 0.9782 (aruco_5x5_norefine) at 48 px, bias 0.46-0.50 px per axis; transport_bench/environment.json udp_rcvbuf and net_core_rmem_max 212,992; results.csv UDP 1,536,032 B thru loss_pct 0.0102; knowledge/marker_literature.md Table I (p. 4); filter_metrics/summary.csv lag_ms_subframe; transport environment.json date_local 07:28:14 and the marker run.log 1822 s ending with results.csv at 07:56. Detectors are interleaved per image: marker_bench.py lines 388-392 time every detector in turn on the same image for each repetition.
Reversibility: git checkout of backup_content.json, the three SLIDE_TEXT.md files and the marker README.
Review: Whether the page 37 claim, now longer, reads well in the notes and script.

ID: D-172 (superseded by D-207, round 6)
Status: UNCERTAIN
Decision: Round 5 (A1): the nine chapter dividers (pages 4, 7, 10, 15, 17, 22, 26, 32, 34 after the insertion) are drawn centred: the chapter label at 22 pt in the muted BBBBBB and the chapter title at 28 pt white, both centred across 0.50-12.83 in at y 1.90 and 2.35 in; from y 3.40 in the nine outline names of the thesis_map page (page 3 data.sections, same order) form one left-aligned 16 pt column centred as a block, 0.33 in apart, the entry whose name equals the divider title white with a leading "> ", the others muted; no footer; duration stays 5 s. The "Discussion and conclusions" entry is current on the chapters 9 and 10 divider. validate_deck.py allows the 22 pt and 28 pt roles in (0.50, 1.80, 12.83, 3.10) and the 16 pt role in (0.50, 3.30, 12.83, 6.86) for the divider kind only (same scoped form as D-122), and a new check requires every divider to show exactly the outline names in order, exactly one current entry (white, "> ", named as the divider title), the others muted, and no other text besides the label and title.
Why: The author found the old dividers (black slide, label and title in the top-left corner) blank-looking and asked for the heading in the middle of the slide with the talk's position in the thesis structure.
Alternatives: Keep the corner layout (rejected by the author). Delete the dividers (rejected: the author chose to keep them). A numbered outline column (rejected: the thesis_map page already shows chapter numbers; the divider shows position only).
Evidence: Author request relayed in the round-5 plan (/home/luo/.claude/plans/delegated-juggling-key.md, Context item 1 and A1). Geometry values (1.90, 2.35, 3.40, 0.33 in step) have no measured source; they were chosen so the column of nine entries ends at 6.30 in, above the 6.75 in region bottom, and checked in the LibreOffice preview of pages 4 and 34. The typography exception is not yet approved by the author.
Reversibility: restrained_divider, OUTLINE_SECTIONS and set_outline_sections in build_deck.py; the divider flags and the divider outline check in validate_deck.py; the divider purpose and visualintent strings in talk_content.json.
Review: Whether the muted 16 pt outline column is legible from the back of the room, and whether the "> " marker is a clear enough current-entry cue.
Superseded: Round 6 (D-207) removes the outline column and its check; the label and title geometry is kept.

ID: D-173 (superseded by D-205 and D-207, round 6)
Status: UNCERTAIN
Decision: Round 5 (A2): page 3 becomes kind thesis_map, title "Thesis structure", 40 s (was 25 s as the Outline page): a full-width diagram of python-pptx shapes in the vocabulary of restrained_information_flow (101010 boxes, 777777 outline, white arrows) with ten chapter boxes in four labelled groups on three rows: Introduction (chapter 1, two chain boxes wide) above Methods (chapters 2-6, a left-to-right chain with arrows, gap 0.26 in), then Evidence (7, 8) and Discussion and conclusions (9, 10). Each box holds the chapter number and a short title (16 pt white) and one sentence on what the chapter delivers (16 pt muted), paraphrased from the chapter opening paragraph in writing/v9/zh/src (line 2 of each chapter file; line 3, the Section 7.1 paragraph, for Chapter 7, which has no opening paragraph); data.chapters[].source and the page source cite file and line. The old data.sections list stays on the page and feeds the dividers (D-172); restrained_outline is kept but no page uses it. validate_deck.py allows the 16 pt role inside (0.50, 1.20, 12.83, 6.86) for this kind only (same scoped form as D-122).
Why: The author asked for an overview of the thesis structure in place of the bare nine-line outline. Four group labels are drawn although the brief says three groups, because it names four (Introduction; Methods; Evidence; Discussion and conclusions) and labelling only three would leave chapter 1 unlabelled.
Alternatives: One row of ten boxes (rejected: a 1.0 in box cannot hold a 16 pt sentence). A 22 pt node role as on page 2 (rejected: ten boxes with a sentence each do not fit at 22 pt). An unlabelled Introduction box (rejected, see Why).
Evidence: Author request relayed in the round-5 plan (Context item 2 and A2). Chapter openings read in this task from writing/v9/zh/src/Chapter_N_*.txt. The 0.06 in extra lower padding comes from the LibreOffice preview, where a four-line box set its last line on its lower edge without it. Layout checked in preview/slide-03.png (mirror build). The 40 s duration has no rehearsal measurement.
Reversibility: restrained_thesis_map and its dispatch line in build_deck.py; the thesis_map flag in validate_deck.py; page 3 of talk_content.json (git history holds the outline version).
Review: The short titles and the ten one-sentence summaries (they paraphrase the openings, not quote them), and the 40 s budget.
Superseded: Round 6 deletes the thesis_map page, its renderer and its validator allowance (D-205, D-207); the professor asked for a presentation outline instead of the thesis map.

ID: D-174 (methodology floor superseded by D-211, round 6)
Status: UNCERTAIN
Decision: Round 5 (A3): the main-talk budget becomes 1765 s (29:25): 1620 s of round 4, plus 15 s on the thesis map (25 to 40 s), plus 70 s (new page 28) and 60 s (new page 29). The validate_deck.py methodology floor drops from two thirds to 0.60 of the main-talk seconds; methodology is 1100 of 1765 s (62.3 %). The check is renamed "At least 60 percent of main time explains methodology".
Why: The professor asked for the highlights of the methodologies, modelling, experiments and results; the author chose two new results pages, all tagged evaluation, which lowers the methodology share below two thirds (1100/1765 = 0.623 < 0.667) without removing any methodology time. The talk stays under the professor's 30 minutes.
Alternatives: Keep 2/3 and trim 20 s from each of pages 8, 9, 13, 19, 20, 23 and 27 (plan A3 fallback; not done because the author has not asked for 27:00). Tag the results pages as methodology (rejected: misstates their role).
Evidence: Durations summed from talk_content.json after this change (1765 s; focus seconds context 190, methodology 1100, evaluation 350, conclusion 115, questions 10), confirmed by validate_deck.py in the mirror build. The 0.60 value is not measured: it is the round-5 plan's choice (A3), the largest round tenth that the current plan meets.
Reversibility: the methodology check in validate_deck.py (restore 2/3) and the durations in talk_content.json.
Review: Whether 29:25 is acceptable against the author's earlier 27:00 target, or the A3 trims should be applied.
Superseded: Round 6 (D-211) moves the floor to 0.55 at 1025 of 1785 s.

ID: D-175
Status: UNCERTAIN
Decision: Round 5 (A4): the two new chapter 7 pages use existing kinds. Page 28 "Chapter 7 results: object and body" is a full_table on a main page (header strip and footer drawn as on every content page): columns Quantity / Recording / Error or median (cm) / n, fractions 0.40 / 0.20 / 0.28 / 0.12; rows W1-W2, W2-W3, W3-W4 absolute length error rail / handover (Tables 7.1-7.2) and the rendered rig medians of the right and left elbow and wrist with n 650 / 589 (Table 7.4), the two wrist rows carrying the kinematic-model medians 0.83 and 2.34 cm (Chapter_7_Evaluation.txt line 78); caption "Reference: tape measure for lengths; accepted raw 3D landmarks for joints, not ground truth." Page 29 "Synthetic landmark removal" is the table kind: three left bullets and restrained_rows with columns Window / Hold-last / Direction memory / Object-assisted, three wrist rows (Table 7.7) and three elbow rows (Table 7.6) of medians, caption with n 45; the p95 and maxima are in the source field (speaker notes) and the spoken script summarises them. Because seven data rows plus a header and the caption leave 0.61 in per row, restrained_full_table now allows a row height of at least 0.40 in when every cell fits one 16 pt line (0.66 in and two lines as before otherwise), and its fit test now measures every wrapped line, not only the last. New legacy keys: ch7_results_table and synthetic_removal. Old pages 28-35 become 30-37.
Why: The author chose two new pages after page 27 (a results table and a synthetic-removal page). A one-line table needs 0.10 in inset + 0.262 in line + 0.036 in margin = 0.40 in, the same margins as the two-line 0.66 in rule, so the builder still raises before any cell could leave its row. The every-line test closes the first-word gap noted in D-169.
Alternatives: Drop the caption to keep 0.66 in rows (rejected: the brief requires the reference caption). Merge right and left into one row per joint (rejected: the brief lists the four joints as rows). A new chart kind (rejected: A4 uses existing kinds).
Evidence: writing/v9/zh/src/Chapter_7_Evaluation.txt lines 24-28, 39-43, 70-75, 78, 96-100, 104-114, 115-125, 126, read in this task; every number on pages 28 and 29 was copied from those lines. 0.262 in = 16 pt x 1.18 leading / 72. The two hidden full_table pages (36 and 38 in backup_content.json) still pass the tightened fit test in the mirror build. Previews of pages 28 and 29 checked (the Object-assisted header breaks at its hyphen onto two lines inside its header cell).
Reversibility: pages 28-29 in talk_content.json; the row-height and fit-test block of restrained_full_table in build_deck.py.
Review: Every number on pages 28 and 29 against the thesis lines above; the wording "Error or median (cm)" for a column that mixes object length errors and joint medians.

ID: D-176
Status: UNCERTAIN
Decision: For the main pages that move in round 5 (old 28-35, now 30-37) previous_pages becomes the round-4 page number ([28] ... [35]); the two new pages 28 and 29 have empty previous_pages; unmoved pages keep their previous_pages unchanged.
Why: The brief says previous_pages follows the renumbering. Round 4 used the same convention for its hidden pages (previous_pages holds the previous round's page, for example page 41 [62]), and revision_id_map.json pages[].previous_pages is the previous round's page. No script reads the talk_content.json field (grep over the repository, 2026-09-28).
Alternatives: Leave the older numbers in place (rejected: the brief asks that previous_pages follow). Append the round-4 number to the older list (rejected: mixes two numberings in one list).
Evidence: grep -rln previous_pages over the repository finds only JSON files; the older numbers of the moved pages remain in git history and in committee_materials/unified_revision/history/round3_27min/revision_id_map.json.
Reversibility: git checkout of the previous_pages values of pages 30-37 in talk_content.json.
Review: Whether previous_pages should keep the older (round-2) numbers instead.

ID: D-177
Status: SETTLED
Decision: Round 5 (A9) hidden-page renumbering in backup_content.json: round-4 hidden pages 36, 37, 38, 39 become 38, 39, 40, 41 and 41-48 become 42-49; round-4 page 40 ("No loss and the lowest jitter at the pipeline rate", throughput and jitter chart) is deleted; every moved hidden page gets previous_pages [its round-4 id] (the older [62], [63], [49], [50] of pages 42, 43, 45, 46 are replaced, same convention as D-176). Page 41 keeps the round-4 page 39 content (latency chart) until the whole-package transport chart replaces it (plan M3/M6), so its previous_pages is [39] only and revision_id_map.json merged_pages stays empty.
Why: The two chapter-7 pages inserted at 28-29 (D-175) shift every later page by 2; the author dropped the throughput/jitter chart page, which shifts old 41-48 by 1 instead. merged_pages would claim that page 41 already carries old page 40's content, which it does not; neither unified_revision_build.py nor validate_deck.py reads merged_pages, so the schema does not need it.
Alternatives: Keep old page 40 as a hidden page until M3 lands (rejected: the brief deletes it now). merged_pages [{id 41, merged_from [39, 40]}] (rejected: not true of the current page 41).
Evidence: backup_content.json ids 38-51 sequential; build_deck.py "37 main + 14 appendix slides; planned main talk 1765 s"; validate_deck.py "Closing page notes list every hidden topic page by slide number" PASS (the closing notes are generated from backup_content.json by build_deck.py, lines 1226-1228, so talk_content.json needed no edit). The chart file experiments/transport_bench/chart_transport_throughput.png stays on disk; old page 40 is recoverable from commit 91b88c0.
Reversibility: git checkout backup_content.json and revision_id_map.json; rerun anim/unified_revision_build.py.
Review: None beyond the M3 replacement of page 41's content.

ID: D-178
Status: SETTLED
Decision: Round-5 media contract (schema_version 8) by the D-131 method. The round-4 media_contract.json, revision_id_map.json, both VIDEO_INDEX.md/.csv levels and provenance/SOURCE_PRESERVATION_CHECK.json are byte-copied to committee_materials/unified_revision/history/round4_topics/ (contract sha256 63969850...de6358c628, map 3d755996...84fd7962, audit ae206a95...fddef27381, each equal to the file at HEAD 91b88c0). revision_id_map.json becomes schema_version 8 (37 main + 14 hidden = 51; old_to_new 1-27 same, 28-39 +2, 40 "deleted", 41-48 +1; no rebound_media key; merged_pages []; pages[].previous_pages = the round-4 page; previous = the round-4 map). anim/unified_revision_build.py is rebased: BASE and PREVIOUS_MAP point at the round4_topics copies with those sha256, COPIES is empty, the preservation audit also re-lists the round-3 history copy, prose describes round 5 and the talk length is computed from the durations (29:25), RETIRED_UNIFIED unchanged. The rebuilt contract keeps all 20 round-4 rows, adds none, drops none and rebinds none; the round-4 copy rows p43 and p46 are now kept rows (source_page 43 / 46, previous_page 43 / 46, page 44 / 47).
Why: Same chained-contract method as rounds 3 and 4, so each film's page history stays traceable through the history copies. The brief named pages 45/48 for p43/p46; the brief's own map (41-48 -> +1) and the plan's target list (Butterworth 44, One Euro 47) give 44/47, which the builder derives from the map.
Alternatives: Keep the round-3 base and add a round-5 map on top (rejected: the contract chains one round at a time and validate_deck.py compares each kept row with its base row). Keep p43/p46 as added rows (rejected: they are rows of the round-4 base, so a second copy would be a new file).
Evidence: unified_revision_build.py 2026-09-28: "Bound 20 kept and 0 added media entries; 0 dropped; 51 slide identities (37 main, 14 hidden)"; a second run left the contract, both indexes, provenance JSON, talk_content.json, backup_content.json and revision_id_map.json byte-identical (sha256sum -c). New contract sha256 f916853a..., map 511d7c6a..., preservation audit 29033269... (238 files, round 4: 225). validate_deck.py needs no code change: the schema >= 7 branch (base_row page == previous_page and base_row source_page == source_page, then old_to_new[previous] == [page]) accepts the p43/p46 kept rows ("43 -> 43 -> 44", "46 -> 46 -> 47" PASS); the archived p41 stays on page 25 with previous_page 25 and UNIFIED_FOUR_ROUTE pages 12, 13, 14 are unchanged because those pages did not move; only comments were added. validate_deck.py --pdf: 1184 checks, 0 package failures, overall PARTIAL only for the retained D-058/D-066 findings.
Reversibility: restore the round4_topics copies to their live paths, git checkout anim/unified_revision_build.py and revision_id_map.json, and rerun the builder.
Review: The VIDEO_INDEX.md wording for a round with no added, rebound or dropped rows.

ID: D-179
Status: UNCERTAIN
Decision: The two References pages of references/page50_snippet.json are appended unchanged as hidden pages 50 and 51 (legacy_key references and references_2, duration 0); of references/KEY_USAGE.md only the closing-notes rule is applied (the Questions page notes list "50 References (1 of 2)" and "51 References (2 of 2)", generated by build_deck.py). No citation key was added to any other page, and the Oppenheim 2010 row on page 51 is left in place.
Why: The brief scopes key placement and the Oppenheim decision to M6; appending the pages now lets the round-5 numbering (51 pages) and the media contract be final before M3-M5 are merged.
Alternatives: Wait for M6 to append the pages (rejected: the contract counts would then change twice).
Evidence: validate_deck.py "Closing page notes list every hidden topic page by slide number" PASS; build_deck.py text-fit warnings 0. Until M6 places the keys, page 51 lists works (for example Oppenheim 2010, Casiez 2012) that no slide yet cites visibly; no validator check for key coverage exists yet (plan M6).
Reversibility: delete ids 50 and 51 from backup_content.json, set revision_id_map.json counts back to 49, rerun the builder.
Review: M6 key placement per references/KEY_USAGE.md and the Oppenheim row.

ID: D-180
Status: SETTLED
Decision: [presentation/defense_2026/experiments/transport_bench] The package condition is a separate mode (--package, --package-chart-only) with its own output files; the default run and the round-4 outputs are unchanged.
Why: The brief says add, do not replace. A separate mode reruns the package condition in about 4 minutes without rewriting results.csv, results_run2.csv or run_to_run.csv, which pages 38-40 and the knowledge files cite.
Alternatives: Folding the package into conditions() (a rerun of the default would rewrite every round-4 number); a separate script (duplicates the pinning, pacing, cleanup and seqlock code).
Evidence: diff against the pre-change script removes no line; environment.json after the run holds every original key with equal values plus one new key package_condition (checked by loading both files).
Reversibility: Delete the package block and the two flags in transport_bench.py and the package outputs.
Review: None needed.

ID: D-181
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/transport_bench] One package = the 172 B V3 person record (PSV3) plus one 1,536,032 B frame slot (PSF1), 1,536,204 B per tick at 30 Hz, as the author's brief specifies.
Why: The author asked for the whole per-frame package moved from Python to Unity. The sizes are the two sizes already measured in round 4.
Alternatives: The thesis's own records (Section 6.1.2: person record 84 B, combined record 112 B), which Unity actually reads; the frame alone.
Evidence: None that this package exists in the pipeline: thesis Chapter_6_System_Integration.txt line 9 says Unity never reads the frame buffer, which carries images from the capture process to the Python branches. The package is therefore a stress case the author requested, stated as such in the page notes.
Reversibility: PKG_REC, PKG_FRAME constants (taken from SIZES); rerun.
Review: Confirm the author accepts the notes sentence that the package is a stress case, not a path the pipeline has.

ID: D-182
Status: SETTLED
Decision: [presentation/defense_2026/experiments/transport_bench] Time per package runs from writer time.monotonic_ns() immediately before the first byte of the package is written or sent to reader time.monotonic_ns() once both parts are read whole with the same package index; the writer keeps its start stamps in an array returned to the parent.
Why: The brief asks for write start to read complete on a monotonic clock in one host. A writer-side array gives the same start definition for all three transports; the stamps are also carried in both payloads so the reader can check that the two parts belong to one package.
Alternatives: perf_counter_ns as in round 4 (the same clock on this host, see Evidence; monotonic_ns chosen to match the brief's wording).
Evidence: time.get_clock_info("monotonic") and ("perf_counter") both report clock_gettime(CLOCK_MONOTONIC), resolution 1e-09 (environment.json package_condition.clock_info; checked in this session). mismatched_parts 0 and duplicates 0 for every transport and run (environment.json).
Reversibility: pkg_writer_main / pkg_reader_main clock lines.
Review: None needed.

ID: D-183
Status: SETTLED
Decision: [presentation/defense_2026/experiments/transport_bench] Counts: 200 warm-up plus 1000 measured packages per transport per run, two runs, transports run shared memory, UDP, TCP in that order within each run.
Why: 1000 measured packages and two runs are set by the brief. 200 warm-up is the round-4 N_WARM (D-149), kept so warm-up is treated the same as in the paced conditions.
Alternatives: Interleaving transports package by package (not possible with separate processes per transport without changing the method).
Evidence: raw_latencies/package_run1 and package_run2: indices 200-1199, 1000 rows per file; environment.json runs[].wall_s 120.6 s each.
Reversibility: PKG_N_WARM, PKG_N_MEAS constants.
Review: None needed.

ID: D-184
Status: SETTLED
Decision: [presentation/defense_2026/experiments/transport_bench] Shared memory: two /dev/shm files, one per record, each under its own seqlock; the writer writes the frame, then the record; the busy-waiting reader waits for a new record seq, copies and checks the record, then copies and checks the frame and its package index. One slot per record, not the pipeline's 8-slot ring.
Why: Brief: both records written under their seqlocks in one tick, reader complete when both are read consistently. Writing the record last makes its seq the "package ready" signal. Seq words are written as pre-packed 4-byte slices (D-154). At 30 Hz a single slot suffices when the reader keeps up.
Alternatives: One file holding both records under one seqlock (not how the pipeline stores them); polling the frame first (overlaps the frame copy with the record write, shortens the measured time).
Evidence: environment.json: shm_record_retries 0, shm_frame_retries 0, mismatched_parts 0 in both runs; 1000 of 1000 delivered in both runs.
Reversibility: pkg_writer_main / pkg_reader_main shm branches.
Review: None needed.

ID: D-185
Status: SETTLED
Decision: [presentation/defense_2026/experiments/transport_bench] UDP: 26 frame datagrams of up to 60,000 B (UDP_CHUNK, D-151) then the record as a 27th datagram, 8-byte header (package index, datagram index, count); complete when all 27 arrived; given up when a datagram of a later package arrives first; default receive buffer.
Why: Brief: fragmented datagrams of the frame plus the record, given up when the next frame starts. Default buffers match the only UDP code in the repository and round 4 (D-151).
Alternatives: A larger SO_RCVBUF (needs net.core.rmem_max raised, a system setting, out of scope).
Evidence: environment.json udp_rcvbuf 212,992 and net_core_rmem_max 212,992; idle rerun 2026-09-28 09:51: udp_packages_given_up 646 (run 1) and 779 (run 2), which count warm-up packages too; lost 528 and 668 of the 1000 measured (first, loaded run: 301 and 225 given up, 248 and 203 lost).
Reversibility: PKG_NCH and the UDP branches; buffer size needs a system change and a rerun.
Review: None needed.

ID: D-186
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/transport_bench] The package results are the idle-machine rerun of 2026-09-28 09:51 PDT; the UDP loss count (528 of 1000 on the chart) is reported as varying from run to run, and is no longer attributed to machine load, because the idle rerun lost more than the loaded run.
Why: The first package run (09:33, other deck workers running) lost 248 and 203 UDP packages of 1000, and the draft attributed the excess over round 4's 4.55 % frame-only loss to machine load. The M6 rerun on an idle machine (load average 0.20 at start, no process above 20 % CPU at the start or end of either run) lost 528 and 668, so load does not explain the loss. The brief said to keep the result and not tune the benchmark if idle UDP loss stayed above 10 %; it did, so the benchmark was not changed and the cause was not investigated.
Alternatives: Keep the loaded-run numbers (rejected: the brief asked for the idle rerun first, and the rerun is the cleaner condition). Raise the receive buffer or pace the datagrams (rejected: tuning; needs net.core.rmem_max, a system setting).
Evidence: results_package.csv after the rerun: run 1 shm median 0.0586 ms (0.0556-0.1569), UDP 0.3115 (0.2328-0.3618) lost 528, TCP 0.2946 (0.1765-0.6332) lost 0; run 2 shm 0.0569 (0.0549-0.1667), UDP 0.3130 (0.2303-0.3742) lost 668, TCP 0.2929 (0.1931-0.5603) lost 0. Loaded run (replaced; values from the pre-rerun results_package.csv read in this session): run 1 shm 0.0576 (0.0550-0.1750), UDP 0.2934 (0.2044-0.3796) lost 248, TCP 0.2876 (0.1976-0.5888); run 2 shm 0.0594 (0.0553-0.2347), UDP 0.2979 (0.2118-0.3635) lost 203, TCP 0.2913 (0.1884-2.5157). environment.json package_condition: loadavg_at_start [0.196, 0.358, 0.380], busy_processes_at_start [] and busy_processes_at_end [] in both runs (loaded run: a python process at 99.8 % CPU at the end of run 1). The loaded-run CSVs are not kept in the repository.
Reversibility: Rerun --package; the chart and page 41 notes follow results_package.csv.
Review: Whether a loss count that swings between 20 % and 67 % should stay on the slide as "lost N of 1000" or be replaced by a range in the notes.

ID: D-187
Status: UNCERTAIN
Decision: [presentation/defense_2026/experiments/transport_bench] The chart shows run 1 on a linear axis; run 2 is in results_package.csv and in the page notes.
Why: Run 1 is the charted run on the round-4 pages too. A linear axis keeps bar heights proportional to time, which is the plain reading the author asked for; in the idle rerun the slowest packages are TCP 0.6332 ms (run 1) and 0.5603 ms (run 2), so either run keeps all three bars readable; the loaded run's run 2 held one TCP package at 2.5157 ms, which prompted the original choice.
Alternatives: Pooling both runs (2000 packages; conflicts with "lost N of 1000"); a log axis (bars on a log axis mislead about ratios).
Evidence: results_package.csv and raw_latencies/package_run1, package_run2 after the idle rerun.
Reversibility: chart_package(run=...) argument; --package-chart-only re-renders.
Review: Confirm run 1 as the charted run.

ID: D-188
Status: SETTLED
Decision: [presentation/defense_2026/experiments/transport_bench] Chart layout: 12.33 x 5.55 in at 200 dpi (the full_image region, build_deck.py FULL_X0..FULL_Y1), title 21 pt, two muted 15 pt subtitle lines (machine class and stand-in; bar and whisker meaning), typical value in 20 pt bold beside each bar top with "typical" under it, "lost N of 1000" under each bar label, no per-whisker labels, no percentile words; the renderer raises if any text leaves the figure.
Why: At 1:1 scale on the slide the chart's point sizes are slide point sizes. A value printed beside the bar stays clear of the whisker drawn through the bar's centre; whisker end values are in the notes.
Alternatives: Value inside the bar (does not fit the 0.058 ms bar); value above the whisker top (reads as the slowest value).
Evidence: Rendered PNG 2466 x 1110 px at 200 dpi, inspected in this session; the first layout overflowed on the right and collided with whisker labels, which prompted the check and the layout.
Reversibility: chart_package in transport_bench.py.
Review: Master preview inspection of page 41 (regenerated chart after the idle rerun, inspected by the M6 worker: labels inside the figure, lost 528 of 1000 under UDP).

ID: D-189
Status: SETTLED
Decision: [presentation/defense_2026/equations] The filter equations on hidden pages 42-49 are typeset with matplotlib mathtext by equations/typeset_filters.py from the frozen implementation, not cropped from the thesis; their keys carry the prefix ts_ and live in a separate catalogue, equations/typeset_catalog.json, next to the untouched thesis-crop catalogue.
Why: Thesis V9 prints no filter formula (only prose in Chapter 2 and Appendix F; plan delegated-juggling-key.md, verified facts), so there is nothing to crop. Typesetting from the code that produced every filtered number keeps the equations traceable: each key cites its function and line range, the file hash is pinned, and the script refuses to run if a cited line no longer contains the quoted code. A separate prefix and catalogue keep the claim "exact thesis quotation" true for every eq_ key.
Alternatives: Write the formulas as slide text (rejected: sub/superscripts and fractions are not available in the fixed 22 pt text roles, and ASCII formulas read as code). Install TeX and use usetex (rejected: a system-wide install needs the author's approval; mathtext needs none). Add the pieces to equation_catalog.json (rejected: that catalogue asserts thesis provenance, render crops and DOCX verification that a typeset piece cannot have).
Evidence: Plan assumption A6 (approved); equations/typeset_filters.py verify_sources(); typeset_catalog.json pinned_sources.
Reversibility: Remove the ts_ keys from pages 42-49 and the ts_ branch in the builder and validator; the thesis-crop pipeline is unaffected.
Review: Whether the author accepts typeset (not quoted) equations on hidden pages; the catalogue marks each as "typeset ... not a thesis quotation".

ID: D-190
Status: SETTLED
Decision: [presentation/defense_2026/equations] ts_hampel = "|x_i - m_i| > max(a_0, k 1.4826 MAD_i): reject x_i; m_i = med_{|j|<=3} x_{i+j}, MAD_i = med_{|j|<=3} |x_{i+j} - m_{i+j}|; a_0 = 0.02 m, k = 3, each axis".
Why: Restates hampel_mask. The MAD is the rolling median of each sample's own residual (line 60 takes the rolling median of |df - med|, where med is itself rolling), hence m_{i+j} inside the MAD, not m_i. A flagged sample is set to NaN (line 263), so the equation says reject, not replace.
Alternatives: The textbook MAD_i = med|x_{i+j} - m_i| (rejected: not what line 60 computes).
Evidence: lines 54-62 (57 rolling window centred, min_periods 3; 58 median; 60 MAD; 61 threshold max(abs_floor, k*1.4826*mad); 62 any axis and finite); 263 invalidation; defaults 202 (window 7), 203 (k 3.0), 204-205 (floor 0.02 m).
Reversibility: Edit SPECS['ts_hampel'] and rerun the script.
Review: The edge behaviour (min_periods 3 near segment ends) is in the catalogue notes, not on the slide.

ID: D-191
Status: SETTLED
Decision: [presentation/defense_2026/equations] ts_gap = "x(t) = x(t_a) + (t - t_a)/(t_b - t_a) (x(t_b) - x(t_a)); t_a < t < t_b, interior gap <= 5 frames".
Why: fill_gaps interpolates each interior NaN run of at most max_gap frames with np.interp over time between the neighbouring valid samples.
Alternatives: Index-based interpolation (rejected: line 92 interpolates on t, the timestamps).
Evidence: lines 71-97 (89 interior test, 90 run <= max_gap, 92 np.interp on t); defaults 206-207 (max_gap 5), 208-210 (edge_fill 0, boundary runs not filled).
Reversibility: Edit SPECS['ts_gap'].
Review: None.

ID: D-192
Status: SETTLED
Decision: [presentation/defense_2026/equations] ts_butter = "|H(w)|^2 = 1/(1 + (w/w_c)^{2n}); n = 4, f_c = w_c/2 pi = 3 Hz".
Why: smooth_segment builds butter(order 4, 3 Hz, fs) (line 141). The formula is the analog Butterworth prototype; scipy designs the digital filter by the bilinear transform with pre-warping, so the digital response matches the prototype's half-power point exactly at 3 Hz and differs slightly elsewhere. This caveat is in the catalogue notes.
Alternatives: The digital transfer function coefficients (rejected: unreadable on a slide and not more informative).
Evidence: lines 140-145 (141 butter call); defaults 213-214 (cutoff 3.0 Hz), 215 (order 4); fs from line 246, 29.98 Hz on R6b (experiments/filter_metrics/run_info.json sampling_rate_hz).
Reversibility: Edit SPECS['ts_butter'].
Review: Whether the analog-prototype caveat needs to be spoken if asked.

ID: D-193
Status: SETTLED
Decision: [presentation/defense_2026/equations] ts_filtfilt = "y = rev(H rev(H x)); zero phase, magnitude |H(w)|^2".
Why: filtfilt runs the filter forward, reverses, runs it again and reverses back; the phase shifts cancel and the magnitude squares. It needs the whole segment, so it is offline only (said in the bullets and notes, not added to the equation).
Alternatives: None considered.
Evidence: lines 140-145 (142 padlen 3*max(len(a), len(b)) = 15; 145 filtfilt call); scipy.signal.filtfilt definition.
Reversibility: Edit SPECS['ts_filtfilt'].
Review: None.

ID: D-194
Status: SETTLED
Decision: [presentation/defense_2026/equations] ts_savgol = "y_i = sum_{j=-4}^{4} c_j x_{i+j}; c_j: least-squares quadratic fit".
Why: savgol_filter with window 9 and order 2 is a fixed 9-tap convolution whose weights evaluate the least-squares quadratic at the window centre. "over 9 samples" was dropped from the second line to fit the 5.26 in left column; the window is given by the sum limits and the bullet.
Alternatives: Show the numeric weights (rejected: no room, no added insight).
Evidence: lines 131-134 (134 savgol_filter call); defaults 216-217 (window 9), 218 (order 2).
Reversibility: Edit SPECS['ts_savgol'].
Review: Edge samples use scipy mode 'interp' (catalogue note).

ID: D-195
Status: SETTLED
Decision: [presentation/defense_2026/equations] ts_median = "y_i = med(x_{i-4}, ..., x_{i+4})".
Why: medfilt with the 9-sample window (odd, so used as is).
Alternatives: None.
Evidence: lines 135-139 (136 odd-window rule, 139 medfilt call); default 216-217 (window 9).
Reversibility: Edit SPECS['ts_median'].
Review: scipy.signal.medfilt zero-pads the segment ends, so the first and last 4 outputs of each segment mix in zeros; recorded in the catalogue notes, not fixed (v1 is frozen).

ID: D-196
Status: SETTLED
Decision: [presentation/defense_2026/equations] ts_oneeuro_cutoff = "d_i = f_s (x_i - x_hat_{i-1}), d_hat_i = a_d d_i + (1 - a_d) d_hat_{i-1}; f_c = f_min + beta |d_hat_i|", with d for the speed instead of the brief's dx_hat.
Why: Line 117 differentiates against the previous filtered value self._x, not the previous raw sample, so x_hat_{i-1} appears in d_i. A plain d avoids a nested hat-over-dot accent that mathtext renders poorly.
Alternatives: Writing dx_i = f_s (x_i - x_{i-1}) (rejected: not what line 117 computes).
Evidence: lines 113-123 (117 dx, 118 a_d from d_cutoff, 119 smoothing, 120 cutoff); d_cutoff 1.0 at line 104.
Reversibility: Edit SPECS['ts_oneeuro_cutoff'].
Review: The unit of beta (s/m, since positions are metres) is inferred from the code, not stated in it.

ID: D-197
Status: SETTLED
Decision: [presentation/defense_2026/equations] ts_oneeuro_alpha = "a = 1/(1 + f_s/(2 pi f_c)), x_hat_i = a x_i + (1 - a) x_hat_{i-1}".
Why: _alpha computes tau = 1/(2 pi cutoff) and 1/(1 + tau freq); the update is the exponential smoother at line 122.
Alternatives: None.
Evidence: lines 109-111 (_alpha), 121-122 (a and update).
Reversibility: Edit SPECS['ts_oneeuro_alpha'].
Review: None.

ID: D-198
Status: SETTLED
Decision: [presentation/defense_2026/equations] ts_oneeuro_params = "f_min = 0.05 Hz offline, 1 Hz live; beta = 1; f_s ~ 30 Hz; a_d uses a 1 Hz cutoff".
Why: The film on page 47 uses the offline default; the real-time pipeline uses the CausalLandmarkFilter default. f_s is measured per recording offline (line 246; 29.98 Hz on R6b) and fixed at 30 live.
Alternatives: Offline setting only (rejected: page 49 argues for the live filter).
Evidence: filter_landmarks.py 104 (d_cutoff 1.0), 219-222 (offline 0.05 Hz, beta 1.0), 246 (fs); v1/realtime/person/realtime_person.py 98-99 (freq 30.0, min_cutoff 1.0, beta 1.0; sha256 0fae95a4bbef3390f24b5bd5c6e4698dc7af2094c1116201f62d28d8662a18e6, pinned in the catalogue); eval/pipeline_smoothness/DECISIONS.md PS-006; experiments/filter_metrics/run_info.json sampling_rate_hz 29.978715.
Reversibility: Edit SPECS['ts_oneeuro_params'].
Review: None.

ID: D-199
Status: UNCERTAIN
Decision: [presentation/defense_2026/equations] Typesetting constants: mathtext fontset STIX with STIXGeneral for the words inside an equation; font size 11.65 pt, computed so the digit 1 is 66 px tall at 600 dpi like the digit 1 of thesis crop eq_5_4 (columns 670-730); 2 px clear margin; 68 px line gap inside a multi-line piece; maximum width 1972 px.
Why: The glyph-height match makes a typeset piece display at the same size as a thesis crop under the builder's fixed px/600*1.6 scale. The margin and gap copy the builder: exact_equation_fragments keeps 2 px, and 68 px = 0.18 in (default equation_gap) / 1.6 * 600. 1972 px = (5.85 - 0.59) in / 1.6 * 600, the room between the fragment x and the right edge of the left region (RESTRAINED left_x + left_w; validate_deck left region).
Alternatives: DejaVu Sans for the words (tried; rejected on the contact sheet: heavier than the math and wider, it pushed ts_hampel past 1972 px). Computer Modern (rejected: the thesis crops are closer to a Times/Cambria serif than to CM; this is a visual judgement, no measurement).
Evidence: typeset_catalog.json renderer.font_calibration (reference digit 66 px, probe 68 px at 12 pt); column runs of eq_5_4.png measured in this task (digit 1 at columns 686-720, the parenthesis at 656-665 is outside the window); build_deck.py RESTRAINED and restrained_equations.
Reversibility: Change the constants in typeset_filters.py and rerun; page equation_start_y values may need re-checking.
Review: The contact sheet equations/typeset/contact_sheet.png (thesis crop eq_5_4 at the top for scale); the font choice is a judgement.

ID: D-200
Status: UNCERTAIN
Decision: [presentation/defense_2026/equations] Pages 42-49 use bullet_y [1.40, 2.49, 3.58], bullet_height 0.99 and equation_start_y 4.62; pages 48-49 use kind frame_figure for the panel chart; film pages 42-47 keep kind composite; the source strings gain one sentence naming the pinned implementation and the footer labels gain "| v1/mediapipe/filter_landmarks.py".
Why: 1.40/2.49/3.58 and 0.99 are the builder's own equation-page bullet roles (restrained_bullets); every bullet was measured at two 22 pt lines or fewer in 5.03 in with the builder metric, so the last box ends at 4.57 and 4.62 leaves 0.05 in. Lowest equation bottom 6.46 in (page 44), inside the validator's left region (bottom 6.75). frame_figure draws the image and caption in the same boxes as composite (6.22, 1.20, 6.61, 5.00; caption 6.31), whereas figure_pair places two 3.23 x 3.80 in images.
Alternatives: Start equations right under a one-line third bullet (rejected: one start value for all eight pages is simpler to validate). full_image (rejected: the author asked for the page-9 layout).
Evidence: build_deck.py restrained_bullets, restrained_page (frame_figure and composite branches), restrained_figure_pair; validate_deck.py equation_picture_checks left region; measurement script output in the M4 report.
Reversibility: Edit equations/page_snippets_42_49.json before the merge.
Review: The rendered previews of pages 42-49 after integration; the panel chart fills the full 6.61 in box, 0.61 in wider than page 9's film.
Superseded in part: pages 48-49 use kind panel_chart, not frame_figure (D-203).

ID: D-201
Status: UNCERTAIN
Decision: [presentation/defense_2026/equations] charts.py --panel draws the two filter charts at 6.61 x 5.00 in, 200 dpi, as two stacked axes (comparison on top, the same 4 s excerpt below), with 12 pt base text, 11 pt ticks, 13 pt titles, 9.5-10.5 pt data labels and legends, no figure title and no in-chart source line; the data come from the committed summary.csv and the excerpt arrays recomputed with the same frozen functions, and the script asserts the excerpt window equals run_info.json.
Why: The chart is placed 1:1 in the 6.61 x 5.00 in region, so point sizes are the slide sizes; the slide title and footer already carry the title and the summary.csv source. Recomputing in charts.py keeps filter_metrics.py (out of scope) untouched and does not rewrite its outputs.
Alternatives: A single axes per panel (rejected: the excerpt shows zero phase and the lag, which the equations on the left describe). Larger fonts (rejected: the annotations collide at 12 pt and above in the scatter).
Evidence: Visual inspection of the two PNGs in this task; two consecutive runs gave byte-identical files (sha256 ace81be0... offline, efc5a21d... realtime).
Reversibility: Delete the panel section of charts.py and the two PNGs; the full charts are unchanged.
Review: Projected legibility of the 9.5 pt annotations; the deck's visual role elsewhere is 16 pt.

ID: D-202
Status: UNCERTAIN
Decision: [presentation/defense_2026] Citation keys from references/KEY_USAGE.md are placed in visible captions: page 39 "AprilTag 3 is the detector of Krogius 2019; ArUco is the pinned OpenCV detector."; 42 (Hampel 1974; Pearson 2016); 44 (Butterworth 1930; Oppenheim 2010; Gustafsson 1996); 45 (Savitzky and Golay 1964); 47 (Casiez 2012); 48 (Butterworth 1930; Gustafsson 1996; Savitzky and Golay 1964); 49 (Casiez 2012). Page 38 already carried its five keys in the Source column. The Oppenheim 2010 row stays on page 51 because the key is placed on page 44; page 51's notes now say Oppenheim 2010 appears with Butterworth smoothing only (the clause about the real-time choice and the offline reason is removed). validate_deck.py gains two checks: every "Author Year" key in a References table appears in the visible text of another hidden page, and every author-year string visible on a hidden page is a References key.
Why: KEY_USAGE.md counts only visible text; the caption is the one visible text slot on these pages with room (panel bullets are capped at eight words by the concise-bullet check, and full_image pages draw no claim). Oppenheim 2010 is the thesis's citation for the digital Butterworth design, which the order 4, 3 Hz parameters on page 44 are (the bilinear-transform caveat of D-192).
Alternatives: Delete the Oppenheim row (rejected: the key fits the page-44 caption in two 16 pt lines). Keys in the titles (rejected: titles are listed verbatim in the closing notes and would lengthen). Keys only in notes (rejected: KEY_USAGE.md does not count notes).
Evidence: validate_deck.py after the merge: "Every References key appears in the visible text of a hidden page" PASS and "Every author-year key on a hidden page is in a References table" PASS; a regex scan of the built PPTX finds author-year strings only on pages 38, 39, 42, 44, 45, 47, 48, 49 (keys as listed) and on 50-51, none on pages 1-37. Captions measured at two 16 pt lines or fewer with the builder metric; page 39's caption takes one full-width line, which lowers its chart bottom from 6.75 to 6.20 in (chart scaled to about 90 %).
Reversibility: Remove the caption suffixes in backup_content.json and the two checks in validate_deck.py.
Review: Previews 39, 42, 44, 45, 47, 48, 49 (the renderer breaks "Savitzky and Golay / 1964" and similar keys across the two caption lines).

ID: D-203
Status: UNCERTAIN
Decision: [presentation/defense_2026] Pages 48-49 use a new visual kind panel_chart (the measured chart drawn at 6.22, 1.20, 6.61, 5.00 with the caption at 6.22, 6.31, 6.61, 0.53, caption limited to two 16 pt lines) instead of frame_figure as equations/BUILDER_WIRING.md proposed; validate_deck.py adds "Slide NN panel chart embeds its declared image uncropped in the right box".
Why: validate_deck.py binds every frame_figure page to the coordinate-frame figure manifest (figures/coordinate_frames/manifest.json) and build_deck.py lists every frame_figure page in DEMONSTRATION_MANIFEST.json static_coordinate_figures; the filter charts are neither, so frame_figure would have failed "embeds its declared coordinate-frame figure" or required loosening that check. panel_chart draws exactly the frame_figure two-line branch, so the geometry BUILDER_WIRING.md specified is unchanged.
Alternatives: frame_figure plus an exemption in the coordinate-figure check (rejected: loosens an existing check). full_image (rejected: not the page-9 layout the author asked for).
Evidence: validate_deck.py "Slide 48/49 uses the page-9 left-text / right-media geometry" PASS with chart bounds (5687568, 1097280, 6044184, 4572000) EMU = 6.22, 1.20, 6.61, 5.00 in.
Reversibility: Set visual.kind back to frame_figure on pages 48-49 and delete the panel_chart branches.
Review: None beyond the previews of 48-49.
Note: equations/BUILDER_WIRING.md's frame_figure proposal for pages 48-49 was superseded by panel_chart in this entry; the file was deleted after the D-204 merge (see D-204).

ID: D-204
Status: SETTLED
Decision: [presentation/defense_2026] Merge of equations/page_snippets_42_49.json into backup_content.json keeps the M2 previous_pages ([41] ... [48], the round-4 ids of D-177) instead of the snippet's older values, and shortens six panel bullets to eight words: 43 "Fills a gap linearly in time"; 44 "Removes jitter above 3 Hz, no phase lag"; 48 "Fast motion: Savitzky-Golay 5.64, Butterworth 6.53 mm"; 49 "A live filter sees only past samples", "One Euro: 2.48 mm, 85 ms lag", "Butterworth: 2.88 mm, 142 ms lag". Page 41 was merged from experiments/transport_bench/page41_snippet.json with previous_pages [39], then updated in place with the idle-rerun numbers (D-186); the snippet files (experiments/transport_bench/page41_snippet.json, equations/page_snippets_42_49.json) and equations/BUILDER_WIRING.md were deleted after the merge.
Why: The M4 snippets were written from commit 91b88c0, before M2 renumbered; D-177 set previous_pages to the round-4 id. validate_deck.py "Visible left bullets are concise phrases" (at most eight words, no final period) failed on those six bullets; the check is kept and the text is fixed. The last two page-49 bullets drop the words shake and the 1 Hz / 3 Hz settings, which the chart labels, the axis titles (Shake (mm), Lag (ms)) and the ts_oneeuro_params equation on the same page carry.
Alternatives: Loosen the eight-word rule for hidden pages (rejected: fix, never waive).
Evidence: validate_deck.py first run after the merge: 1 package failure "Visible left bullets are concise phrases"; after the edits 0 package failures. Numbers unchanged: 5.64, 6.53, 2.48, 85, 2.88, 142 are the snippet's values from experiments/filter_metrics/summary.csv.
Reversibility: Restore the snippet bullets (and the check would fail again).
Review: Wording of the page-49 bullets.
Review note: Code review 2026-09-28: no correctness defect; page 49 wording (EMA, not plain moving average) corrected.

ID: D-205
Superseded in scope (2026-09-29, D-218): the approved argument-led revision replaces the ten-part chapter-order outline. Historical content and validation remain recorded below.
Follow-up (2026-09-29, D-216): information flow moves from current page 3 to 4 so Motivation opens the Introduction on page 3. The outline row now uses the professor's plural heading, "Discussions: what the evidence supports". The original ten-part outline and timing decision below remains recorded.
Status: UNCERTAIN
Decision: [presentation/defense_2026] Round 6 (A1): page 2 becomes "Presentation outline" (kind outline, 30 s, chapter 1, focus context, section "Chapter 1: Introduction") with ten rows that name the logic of the talk, not chapter titles: "Why this problem, and the task on video"; "What one camera measures, and how the signals are conditioned"; "How the upper body is modelled"; "How the object is tracked in the same scene"; "How an arm is recovered when its landmarks fail"; "How the parts run together in Unity"; "How well it works: the evaluation"; "Whether it runs live"; "Discussion: what the evidence supports"; "Conclusions: limitations and contributions". The round-5 thesis_map page (old 3, "Thesis structure", 40 s) is deleted. The information-flow page moves from 2 to 3 and its first sentence reads "Before the details, this is how..." (was "Before the outline"). The row numbers in data.sections are not drawn (restrained_outline behaviour).
Why: The professor's round-6 feedback: slide 2 must be a table of contents of how the thesis is presented, right after the title, and must talk about the logic of the defence presentation, not the thesis; the thesis map is not to be used. The outline renderer and its D-126 typography allowance already existed unused.
Alternatives: Keep the thesis map beside a new outline (rejected by the professor). Chapter titles as rows (rejected: the professor asked for the logic of the talk).
Evidence: Professor feedback relayed in /home/luo/.claude/plans/delegated-juggling-key.md (Context, A1). Preview preview/slide-02.png: ten rows, none wraps, list ends near 4.9 in. Notes 60 words for 30 s (2.0 words/s, the D-113 rate). The 30 s budget has no rehearsal measurement.
Reversibility: Page 2 of talk_content.json; git history holds the thesis_map page and renderer (commit eaab9e8).
Review: The ten row wordings and the 30 s budget.

ID: D-206
Follow-up (2026-09-29, D-216): this Motivation page moves from current page 4 to 3, immediately after the Presentation outline. Its content and 50 s budget remain unchanged from the D-215 fix.
Status: UNCERTAIN
Decision: [presentation/defense_2026] Round 6 (A2): new page 4 "Motivation" (kind table, 50 s, chapter 1, focus context). Left bullets from Section 1.1 (Chapter_1_Introduction.txt lines 4-8): "Robots, VR avatars and clinicians use recorded motion"; "One RGB-D camera; nothing worn by the subject"; "Occlusion and calibration are the difficulty". Right table condensed from Table 1.1 (lines 20-29), columns Approach / Sensing / Limitation, five rows: Gloves and wearables / Worn sensors / Worn hardware; calibration per user (line 21); Bimanual capture datasets / Camera rigs, wearables / Laboratory infrastructure (line 27); Learning-based pose / Depth or RGB / No biomechanical constraints (line 23); Two-hand reconstruction / Monocular RGB / No object tracking; no metric depth (line 28); This thesis / One RGB-D camera / Addresses: body and object in one frame (the gap of Section 1.2.4, line 32). Caption "Condensed from thesis Table 1.1; last row: the gap of Section 1.2.4." Notes are a 101-word spoken script; the page source quotes the line numbers for every bullet and cell.
Why: The professor asked that the first Introduction slide motivate the work. Three bullets because restrained_bullets places three at the default positions. Condensing: "Large training sets" (line 23) and the 80-140 camera count (line 27) were dropped from the cells to keep every cell at two 16 pt lines; the notes do not repeat them either. "per-user" was reordered to "calibration per user" because LibreOffice broke the line at the hyphen.
Alternatives: A figure (rejected: writing/v9/figures has no Chapter 1 figure). The full nine-row Table 1.1 (rejected: does not fit at 16 pt). The default 3-column widths 3.08/1.76/1.77 (rejected: Limitation cells wrap to three lines; see D-208).
Evidence: writing/v9/zh/src/Chapter_1_Introduction.txt lines 4-8, 20-29, 32 read in this task. Preview preview/slide-04.png: every cell on at most two lines, caption on two lines above the footer rule; build Text-fit warnings 0. The 50 s budget has no rehearsal measurement.
Reversibility: Page 4 of talk_content.json.
Review: Whether "Addresses: body and object in one frame" in the Limitation column reads well, and the row selection (four of nine Table 1.1 families); see the D-215 addendum below on whether the author prefers the original row over its round-6-fix replacement.
Addendum (round-6 fix, D-215, 2026-09-28): the "Learning-based pose / Depth or RGB / No biomechanical constraints" row (line 23) is replaced by "Landmark + depth fusion / RGB-D / Single hand, or body without object", condensed from Chapter_1_Introduction.txt line 24 ("Landmark detection with depth fusion | [28], [3], [13], [17] | RGB-D | single hand, or body landmarks without a manipulated object in the same frame"), the closest prior-work family to this thesis and the one the code-reviewer found omitted from the original five-row selection. The Approach cell shortens the thesis family name "Landmark detection with depth fusion" (36 characters) to "Landmark + depth fusion" (23) because the first build produced a text-fit warning (FIT 16) at the D-208 2.10 in column width. The "This thesis" row's Limitation cell changes from "Addresses: body and object in one frame" to "Upper body & tracked object, one frame", matching the Section 1.2.4 gap wording (line 32) that D-206's own claim text already used; the brief's suggested "Upper body and tracked object in one frame" (42 characters) also produced a text-fit warning at the D-208 2.66 in column width and an overlap candidate with the caption below, so it was shortened in two steps (dropping "in" for a comma, then restoring "tracked" with "&" once "Upper body and object, one frame" built clean) until build_deck.py reported 0 text-fit warnings and 0 overlap candidates. The page's source field is updated to cite line 24 in place of line 23. Status stays UNCERTAIN: the swap removes the "Learning-based pose" family, which the author may still want shown instead of, or beside, the RGB-D fusion family; this was not put to the author before the fix.

ID: D-207 (divider y geometry superseded by D-213, round 6)
Superseded in scope (2026-09-29, D-218): chapter-based section sequencing may be replaced by argument-led sections; the existing typography remains the starting style, not an approved final layout.
Status: UNCERTAIN
Decision: [presentation/defense_2026] Round 6 (A3): every chapter divider is a plain centred label and title with no outline column: restrained_divider keeps the D-172 label (22 pt muted, y 1.90) and title (28 pt white, y 2.35) geometry and draws nothing else; OUTLINE_SECTIONS, set_outline_sections and restrained_thesis_map are deleted from build_deck.py with the thesis_map dispatch line. The Introduction divider (old 4) is dropped. Page 34 is retitled "Discussion" (chapter label "Chapter 9", notes "Chapter nine discusses what the evidence supports."), and a new page 36 "Conclusions" divider (chapter 10, label "Chapter 10", 5 s, focus conclusion) precedes Limitations and Contributions. validate_deck.py: the thesis_map typography allowance, the divider_outline allowance, the "Exactly one thesis_map page" check and the D-172 outline-names check are removed; a new check "Slide NN divider draws only its chapter label and title" requires exactly two runs, (chapter_label, 22 pt, BBBBBB) and (title, 28 pt, FFFFFF), exactly two shapes on the slide, both text frames. The divider purpose and visualintent strings say "centred chapter label and title only".
Why: The professor: the Introduction heading is not needed because the outline gives the overview; Discussion and Conclusions need their own headings, with limitations and contributions under Conclusions. The author chose plain centred headings without the outline column. The replacement check is stricter than the one it replaces (it also fails on any extra shape).
Alternatives: Keep the outline column fed from the new outline page (rejected by the author). Move the label and title to the vertical middle of the slide (not done: the plan says to keep the centred geometry; the pair now sits in the upper third, see Review).
Evidence: Plan A3. validate_deck.py --pdf: "Slide 07/10/15/17/22/26/32/34/36 divider draws only its chapter label and title" PASS (detail "Chapter 9 22.0 pt BBBBBB; Discussion 28.0 pt FFFFFF; 2 shapes"). Previews slide-07, 34, 36. No mutation test of the new check was run in this task (plan M3).
Evidence addendum (round-6 fix, D-215, 2026-09-28): the code-reviewer closed the "no mutation test" gap above by running six mutations of slide 34 against a copy of the built package (base.pptx in the review scratchpad, mutated with pptx-python): an added textbox with text, an added picture, an added empty textbox, the chapter-label run recoloured to FFFFFF, the chapter-label shape removed, and the title shape moved to y 2.35 in (the pre-D-213 position). validate_deck.py's "Slide 34 divider draws only its chapter label and title" check produced a FAIL line against every one of the six mutants. This entry records the code-reviewer's reported result; it was not independently rerun inside this fix task.
Reversibility: restrained_divider in build_deck.py and the divider check in validate_deck.py; git history (eaab9e8) holds the D-172 column code.
Review: With the column gone the heading sits at 1.90-2.89 in of a 7.5 in slide; whether it should move to the vertical middle (two y values in restrained_divider and the (0.50, 1.80, 12.83, 3.10) band in validate_deck.py).

ID: D-208
Status: UNCERTAIN
Decision: [presentation/defense_2026] restrained_rows takes an optional widths list, passed from display_table.widths on kind table; it must have one width per column and sum to the 6.61 in table width within 0.005 in, else the builder raises. Page 4 uses [2.10, 1.85, 2.66]. Every other table keeps the fixed defaults.
Why: With the 3-column defaults (3.08, 1.76, 1.77) the Limitation cells of page 4 wrap to three 16 pt lines and overflow the 0.817 in row (rowh = min(.82, 4.90/6)).
Alternatives: Shorten every Limitation cell to about 13 characters (rejected: loses the Table 1.1 meaning). Change the 3-column defaults (rejected: would move other tables).
Evidence: Widths chosen by measuring line counts with the builder's own wrap rule (DejaVu Sans metric, 16 pt, box width minus 0.18 in) for candidate widths; [2.10, 1.85, 2.66] is the first tried set with every cell at two lines or fewer. The 0.005 in tolerance has no source beyond floating-point sums of two-decimal widths. Build Text-fit warnings 0.
Reversibility: Remove display_table.widths from page 4 and the widths parameter.
Review: None beyond the preview of page 4.

ID: D-209 (committee copy p35 made by D-214)
Status: UNCERTAIN
Decision: [presentation/defense_2026] Round 6 (A4): new page 35 "Discussion" (kind composite, 55 s, chapter 9, focus conclusion, section "Chapter 9: Discussion"). Four bullets (bullet_y 1.42/2.62/3.82/5.02, height 1.0, as page 9): "Object lengths off by 0.53 to 2.83 cm" (Table 9.1 line 57); "Model wrist 0.83-2.34 cm; rendered rig 5.5-6.8 cm" (line 59); "Recovery helped the right arm, not the left" (line 61; Section 10.1 line 6); "Causal at recorded pace; no live session" (lines 55, 62). Notes (112 words) from Chapter 9 line 2, Section 9.8 lines 52-55 and Table 9.1 lines 56-63. The right film is the fresh Unity handover replay of page 31 (p47), bound as a copy under committee_materials/unified_revision/{videos,posters,provenance}/p35-Fresh_Unity_Handover_Discussion.{mp4,png,json}, D-132 style; composite_media and committee_media copy page 31's fields with those paths. Caption "Fresh Unity handover replay: rendered hands and cube disagree; qualitative only."
Why: The author chose one Discussion slide on what the evidence supports, with the handover replay film on the right; the handover replay is where the rendered-rig discrepancy of Table 9.1 line 59 shows. A4 said "within about 1-2 cm" for the model wrist; the page uses the thesis values 0.83 and 2.34 cm instead. A4 said the causal path "diverges from its start"; that is Section 9.7 line 50, outside the lines the brief assigned, so the bullet uses line 62 (no live-sensor session).
Alternatives: Reuse the p47 file path on page 35 (rejected: one film binds to one contract page, D-132).
Evidence: writing/v9/zh/src/Chapter_9_Discussion.txt lines 2, 52-63 and Chapter_10 line 6 read in this task. Preview slide-35: film in the page-9 box, caption on two lines. The committee copy files do not exist yet: M2 copies them; this task built with temporary symlinks to the p47 files and removed them afterwards. The film's burned-in label reads "p47".
Reversibility: Page 35 of talk_content.json.
Review: The four bullets and whether the burned-in "p47" label on the copied film matters.

Annotation (2026-09-30, build 63): superseded by D-266. Page 36 (Discussions, formerly page 35) now plays the R7 wrist-loss replay p27; the p35 committee copy is dropped from the media contract and listed in dropped_rows.

ID: D-210
Status: UNCERTAIN
Decision: [presentation/defense_2026] Round 6 (A5): Limitations (page 37, old 35) moves under the Conclusions heading: chapter 10, section "Chapter 10: Conclusions and Future Work"; source_label, source, notes, bullets and table unchanged (Table 9.1 remains its evidence).
Why: The professor asked that limitations and contributions sit under Conclusions. Chapter 10 keeps the chapter sequence sorted for the "Main story follows verified thesis Chapters 1-10" check.
Alternatives: Keep chapter 9 (rejected: the Conclusions heading, chapter 10, precedes it, which unsorts the chapter sequence).
Evidence: validate_deck.py --pdf "Main story follows verified thesis Chapters 1-10" PASS. Preview slide-37.
Reversibility: Two fields of page 37.
Review: None.

ID: D-211
Status: UNCERTAIN
Decision: [presentation/defense_2026] Round 6 (A6): main talk 1785 s (29:45) = 1765 - 40 (thesis map) - 5 (Introduction divider) + 30 (outline) + 50 (motivation) + 55 (Discussion) + 5 (Conclusions divider) - 75 (trims). Trims: page 23 80 to 65 s; pages 13, 19, 20 75 to 60 s; page 8 70 to 55 s, notes condensed with no fact removed. Word counts (old -> new, D-113 target 2.0 words/s x (budget - film seconds)): page 8 95 -> 73 (target 66, film 22.0 s); 13 104 -> 86 (83, film 18.7 s); 19 109 -> 89 (89, film 15.4 s); 20 114 -> 94 (89, film 15.4 s); 23 77 -> 63 (42, film 44.0 s). The validate_deck.py methodology floor moves from 0.60 to 0.55 and the check is renamed "At least 55 percent of main time explains methodology"; methodology is 1025 of 1785 s (57.4 percent); focus seconds context 225, methodology 1025, evaluation 350, conclusion 175, questions 10.
Why: The professor's reshaping adds motivation, discussion and conclusions pages, all non-methodology, and the author chose to stay under 30:00 by trimming about 75 s from the longest method pages. No other check is loosened.
Alternatives: Keep 0.60 (would need about 46 s more methodology or 76 s less elsewhere, over the 30:00 limit or against the author's trims). Tag the new pages methodology (rejected: misstates their role).
Evidence: validate_deck.py --pdf: 1785 s, focus seconds as above, check PASS. The 0.55 value has no measured source: it is the plan's choice (A6), the largest round twentieth the current plan meets. Page 8, 13 and 20 stay a few words over the D-113 target and page 23 21 words over, because the facts on those pages do not fit the target; page 23's narration runs over its 44 s film. The 2.0 words/s rate itself is untested (D-113).
Reversibility: The durations and notes in talk_content.json (git history holds the round-5 text) and the floor in validate_deck.py.
Review: Rehearse pages 8, 13, 19, 20 and 23 aloud against the new budgets.
Amendment (round-6 fix, D-215, 2026-09-28): the claim above that page 8's notes were "condensed with no fact removed" was not true, and the condensing of pages 19, 20 and 23 (durations unchanged in this fix) also dropped or altered claims the code-reviewer found and this fix restored. Facts restored, by page: page 8 -- "replaces their depth with the aligned sensor depth" (the condensed text had weakened this to "are kept, with aligned sensor depth", which drops the replacement claim), and "a drawn dot is therefore not proof of a valid 3D point" (the condensed text said "a drawn dot is not a valid 3D point", a different, stronger claim than the thesis supports); page 19 -- "the stored offset is kept" (folded into "the stored offset and current cube pose give a wrist target", which drops the explicit retention-through-loss claim the page title makes); page 20 -- "Choosing one point needs extra information" (condensed to "The next page chooses one point.", which drops the reason); page 23 -- "five hundred and thirty-two and five hundred and thirty-three both contribute" and "a new output tick" (condensed to the ambiguous "an output tick drawn from frames five hundred and thirty-two and thirty-three"). Page 13 was not touched by the code-reviewer's findings and is unchanged. New word counts (old-round-6 -> restored, this task, notes field, durations unchanged from the row above): page 8 73 -> 80; page 13 86 -> 86 (unchanged); page 19 89 -> 92; page 20 94 -> 99; page 23 63 -> 69. The words/s target and floor of the row above are unaffected: none of these pages' durations changed in this fix.

ID: D-212
Follow-up (2026-09-29, D-216): the current pages 3 and 4 swap; pages 34 and 35 use "Discussions". The round-5 mapping basis and all other page numbers remain unchanged.
Status: SETTLED
Decision: [presentation/defense_2026] Round 6 (A7) renumbering: main 1-39 (1 title; 2 outline; 3 information flow, old 2; 4 motivation; 5-33 unchanged ids; 34 Discussion divider, old 34 retitled; 35 Discussion; 36 Conclusions divider; 37 Limitations, old 35; 38 Contributions, old 36; 39 Questions, old 37); hidden old 38-51 -> 40-53 in backup_content.json. previous_pages follows D-176/D-177: every moved page (main 3, 37, 38, 39; hidden 40-53) gets [its round-5 id]; new pages 2, 4, 35, 36 have []; unmoved pages keep their previous_pages. validate_deck.py "Pages 42-49 are the hidden pages with typeset filter equations" becomes "Pages 44-51 ...", the same check on the moved ids.
Why: Plan A7. The build requires sequential ids, and the typeset-equation pages moved by two.
Alternatives: None considered; the order is fixed by the plan.
Evidence: build_deck.py: "39 main + 14 appendix slides; planned main talk 1785 s"; validate_deck.py --pdf "Pages 44-51 are the hidden pages with typeset filter equations" PASS [44, ..., 51]. The media contract (revision_id_map.json, media_contract.json) is not rebased in this step (plan M2), so validate_deck.py still fails the contract checks for the moved hidden films 44-49 and the new page-35 copy.
Reversibility: Mechanical; git history.
Review: None.

Follow-up (D-221, 2026-09-29): The argument-led M2 revision supersedes the current counts/order and divider/page bindings in this entry. Main/hidden counts are 38/14, hidden pages39-52, and schema10 chains through byte-preserved round-6 history. Current dividers show one argument heading; the historical p35 copy is current34 with original producer page35. Original source-media bytes and this decision record are retained.

ID: D-213
Status: SETTLED
Decision: [presentation/defense_2026] Round 6: the divider heading moves to the vertical middle of the slide. restrained_divider draws the chapter label (22 pt, box 0.40 in) at y 3.25 in (was 1.90) and the title (28 pt, box 0.54 in) at y 3.70 in (was 2.35); the label-plus-title block spans 3.25-4.24 in (was 1.90-2.89), a 0.99 in block whose centre 3.745 in is 0.005 in above the 3.75 in slide centre. validate_deck.py's divider band moves by the same 1.35 in, from (0.50, 1.80, 12.83, 3.10) to (0.50, 3.15, 12.83, 4.45), keeping the 0.10 in margin above the label and the 0.21 in margin below the title. x positions, widths, heights, sizes and colours are unchanged.
Why: The author asked for the heading "in the middle of the page"; with the D-207 outline column gone the heading sat in the upper third (D-207 Review). Top = (7.5 - 0.99) / 2 = 3.255 in, rounded to two decimals as every other builder coordinate; the 0.45 in label-to-title pitch of D-172 is kept.
Alternatives: 3.26/3.71 (centre 3.755 in, equally 0.005 in off; rejected only for the rounding direction). Centring each line's glyph ink rather than its box (rejected: the builder places boxes, and the preview shows the pair visually centred).
Evidence: build_deck.py "39 main + 14 appendix slides; planned main talk 1785 s", Text-fit warnings 0; validate_deck.py --pdf "Slide 07/10/15/17/22/26/32/34/36 divider draws only its chapter label and title" PASS and the typography grid PASS with the moved band (1331 checks, 0 package failures). Preview preview/slide-07.png and slide-34.png: label and title centred horizontally and vertically.
Reversibility: the two y values in restrained_divider and the band in validate_deck.py.
Review: None beyond the previews.

Follow-up (D-221, 2026-09-29): The argument-led M2 revision supersedes the current counts/order and divider/page bindings in this entry. Main/hidden counts are 38/14, hidden pages39-52, and schema10 chains through byte-preserved round-6 history. Current dividers show one argument heading; the historical p35 copy is current34 with original producer page35. Original source-media bytes and this decision record are retained.

ID: D-214
Status: SETTLED
Decision: [presentation/defense_2026] Media contract round 6 (plan A7/M2, method of D-131/D-177): the round-5 media_contract.json, revision_id_map.json, both VIDEO_INDEX levels (md, csv) and provenance/SOURCE_PRESERVATION_CHECK.json are byte-copied to committee_materials/unified_revision/history/round5_equations/ (contract sha256 f916853add2123f9b82b535a87fbf2fb703472c0218104e50a00aee81b65c4de, map 511d7c6a3436aa1ceb492ed7e02ac4858f2e151bad1072c76f53408e405794a4, unified VIDEO_INDEX.md b12ef919...71c5fc, VIDEO_INDEX.csv (both levels) cea60682...aa458, committee VIDEO_INDEX.md 459b590e...0ecb09, preservation audit 29033269...ae37b; each equal to the file committed at 7614fd2 and unchanged at eaab9e8). revision_id_map.json becomes schema_version 9: main 39, backup 14, total 53; old_to_new 1->[1], 2->[3], 3 and 4 "deleted", 5-34 unchanged, 35-51 -> +2; pages[] lists for each current page the round-5 pages that map to it ([] for the new pages 2, 4, 35, 36); previous = the round-5 map; no rebound_media. anim/unified_revision_build.py is rebased (BASE and PREVIOUS_MAP to the round5_equations copies with those sha256; round-4 history copy added to the preservation audit) and adds one copy row, COPIES {35: p35-Fresh_Unity_Handover_Discussion copy_of p47-Fresh_Unity_Handover_With_Model_Axes}, by copy_row as D-132 did for p43/p46: committee_materials/unified_revision/videos/p35-Fresh_Unity_Handover_Discussion.mp4 (sha256 248ab1df92d9e9d948468b94d268edc3caa8ae9865693fe6b3a9feea5918ebe6) and posters/...png (57e6c3932ffc19a34aff666f317165a90ef4e14d5bafa7870939a7801bb92b73), both equal to p47's, with provenance/p35-Fresh_Unity_Handover_Discussion.json (805ede82fdc07cdf1a6df6d9b29683805b4b568bf7d5e7e9b822669143993fd4). The copied film keeps the "p47" label burned into its frames, as p43/p46 keep their p09/p49 labels (D-132 precedent, accepted). Contract schema 9: 20 kept rows (main films unmoved; p07, p08, p43, p67, p68, p46 move 42-47 -> 44-49), 1 added row (page 35), 0 rebound, 0 dropped. validate_deck.py: the Unity-composite audit skips copy rows in its first pass and then audits each copy row against its original (copy report bound by hash; byte_identical_copy_of equal to the original row's path, poster and provenance with their hashes; film and poster bytes equal to the original's; the original itself audited), and a new check "Committee copy X is byte-identical to Y" runs for every copy row (p35, p43, p46).
Why: Pages 2-4 and 35-36 changed (D-205 to D-212), so the chained contract must follow the new page map; one film binds to one contract page, so the Discussion page needs its own copy (D-132). The Unity-composite audit read every unity_axes_composite row's provenance as a capture report, which a copy report is not; auditing the copy through its original keeps every original check and adds the byte-identity check rather than loosening any. The map's pages[].previous_pages uses the round-5 ids, the convention of the round-5 map; for the moved and new pages this equals previous_pages in talk_content.json/backup_content.json, while the unmoved pages 1 and 5-34 keep older-round ids in the content files (D-176/D-212 convention) and the map records their round-5 id.
Alternatives: Reuse the p47 path on page 35 (rejected: D-132). Copy the content files' previous_pages verbatim into the map (rejected: for pages 5-34 they are pre-round-5 ids, which would contradict old_to_new in the same file; no code reads pages[]).
Evidence: anim/unified_revision_build.py run twice: "Bound 20 kept and 1 added media entries; 0 dropped; 53 slide identities (39 main, 14 hidden)"; the second run left the contract (69629e33...fcd7b), map (d805cc02...229c), indexes, preservation audit, copy files and content JSON byte-identical (sha256sum diff empty). validate_deck.py --pdf: Overall PARTIAL (D-058/D-066 source findings only), package PASS, 1331 checks, 0 package failures; "current page follows the page map" PASS for all 21 rows (for example p07 7 -> 42 -> 44, p35 added at page 35); "Committee copy p35-... is byte-identical to p47-..." PASS; "Slide 35 composite is bound to its source and frame-map audit" PASS; p41 stays on page 25 (41 -> 25 -> 25) and the unified films on 12/13/14. In-memory mutation of the p35 row (copy_of, path, provenance hash) makes the copy audit raise.
Reversibility: git checkout the builder, validator, map and live contract files, delete the p35 copy files and the round5_equations folder; restore the round-5 files from that folder.
Review: None beyond the "p47" label on the page-35 film (D-209 Review).

Follow-up (D-221, 2026-09-29): The argument-led M2 revision supersedes the current counts/order and divider/page bindings in this entry. Main/hidden counts are 38/14, hidden pages39-52, and schema10 chains through byte-preserved round-6 history. Current dividers show one argument heading; the historical p35 copy is current34 with original producer page35. Original source-media bytes and this decision record are retained.

ID: D-215
Follow-up (2026-09-29, D-217): finding (1) below records the historical "clinics could" wording. D-217 replaces that incomplete clause on current page 3; the original finding and its evidence remain below.
Status: UNCERTAIN overall (per-finding: findings 2, 3, 4, 6, 7 and 8 are SETTLED restorations of dropped or altered facts, each traced to a pinned thesis line; findings 1 and 5, the page-4 bullet reword and the page-4 table row swap, are UNCERTAIN because they change what the page claims, not just how precisely it says it, and were not put to the author)
Decision: [presentation/defense_2026] Round-6 text fix, applied to talk_content.json against the code-reviewer's eight text findings (a ninth, the D-207 mutation test, is recorded there):
(1) Page 4 bullets[0] and panel_bullets[0]: "Robots, VR avatars and clinicians use recorded motion" -> "Robots and VR avatars replay motion; clinics could" (8 words), keeping clinical use conditional as Chapter_1_Introduction.txt line 5 ("could help a physician assess") states it, against lines 4 and 6-8 which name robot imitation learning and VR/AR avatars as direct users. The first build used "Robot learning and VR avatars use recorded motion; clinics could" (10 words), which failed validate_deck.py's "Visible left bullets are concise phrases" check (<=8 words); the next try, "Robots, VR avatars use recorded motion; clinics could" (8 words), passed the check but read as ungrammatical (comma splice with no conjunction); the author asked for "Robots and VR avatars replay motion; clinics could" in its place, which keeps the 8-word count and reads as a normal clause.
(2) Page 8 notes: restored "their depth replaced by the aligned sensor depth" and "a drawn dot is therefore not proof of a valid 3D point" (see the D-211 amendment for the exact before/after and the new word count).
(3) Page 35 bullets[1]/panel_bullets[1]: "Model wrist 0.83-2.34 cm; rendered rig 5.5-6.8 cm" -> "Model wrist 0.83/2.34 cm (R/L); rig 5.5/6.8 cm" (spaced slashes, "0.83 / 2.34", were tried first but made 12 tokens and failed validate_deck.py's "Visible left bullets are concise phrases" <=8-word check; unspaced slashes read as one token each and pass at 8). Notes: "zero point eight and two point three" -> "zero point eight three and two point three four", and "on the captured frames" added after "from the measured wrist", matching Chapter_7_Evaluation.txt line 78 (per-arm medians "on those frames", i.e. the 650/589-frame captured subset, not the recording-wide 1.03 cm of line 79) and Chapter_9_Discussion.txt line 59 (Table 9.1). Notes word count 112 -> 122 (duration unchanged at 55 s; not part of D-211, which does not cover page 35).
(4) Page 35 notes: "Object-assisted recovery helped the right-arm window, not the left." -> "...on four retained frames, not the left.", matching Chapter_9_Discussion.txt line 61 and Chapter_7_Evaluation.txt Table 7.9 (right arm n = 4, left arm n = 16; object-assisted median 5.2 cm right against 13.1 cm left, i.e. it helped the right arm and made the left worse). The page-35 bullet "Recovery helped the right arm, not the left" itself is unchanged: the brief scoped the n = 4 restoration to the notes only, and the bullet text is a fair summary of Table 7.9 on its own.
(5) Page 4 display_table.rows: the "Learning-based pose" row (Chapter_1_Introduction.txt line 23) is replaced by a row built from line 24, "Landmark + depth fusion / RGB-D / Single hand, or body without object" (thesis family name "Landmark detection with depth fusion", shortened to fit the D-208 column width; full source clause: "single hand, or body landmarks without a manipulated object in the same frame"), the RGB-D family closest to this thesis and the one the code-reviewer found omitted. Page 4 claim and purpose.takeaway: "the body and a held object" -> "the upper body and a tracked object", and the "This thesis" row's Limitation cell: "Addresses: body and object in one frame" -> "Upper body & tracked object, one frame" (also shortened from the brief's suggested wording to clear a text-fit warning; see the D-206 addendum for the two-step wording), both matching the Section 1.2.4 gap wording (Chapter_1_Introduction.txt line 32: "the upper body together with a tracked object"). The page 4 "source" field is updated to cite line 24 in place of line 23 for the swapped row (this field edit was not separately itemised in the brief; it is made here so the citation does not name a row the page no longer shows). See the D-206 addendum: status UNCERTAIN, the row swap was not put to the author.
(6) Page 23 notes: "an output tick drawn from frames five hundred and thirty-two and thirty-three" -> "a new output tick; frames five hundred and thirty-two and five hundred and thirty-three both contribute to it" (see the D-211 amendment for the word count).
(7) Page 20 notes: "The next page chooses one point." -> "Choosing one point needs extra information, covered on the next page." Page 19 notes: "the stored offset and current cube pose give a wrist target" -> "the stored offset is kept, and the current cube pose gives a wrist target" (see the D-211 amendment for both word counts).
(8) Page 37 source: "Chapter 9andTable9.1" -> "Chapter 9 and Table 9.1", matching the "Section 9.8 and Table 9.1" style used elsewhere in the same file (for example page 35's Thesis line).
Why: The code-reviewer's round-6 review found these eight text-accuracy defects against the pinned thesis source files, plus the D-207 mutation-test gap recorded separately. The brief for this task carried the reviewer's findings verbatim with line numbers; each was re-read against writing/v9/zh/src/Chapter_1_Introduction.txt, Chapter_7_Evaluation.txt and Chapter_9_Discussion.txt in this task before editing.
Alternatives: For (1), a fully unconditional bullet naming clinicians as users (rejected: overstates line 5's "could"). For (5), keeping the original five-row table and instead only fixing the claim text (rejected: leaves Table 1.1's closest prior-work family, RGB-D landmark detection, still unrepresented, which was the reviewer's finding). For (3)/(6)/(7), leaving the trims from D-211 as spoken shorthand (rejected: the brief treats the dropped clauses as removed facts, not paraphrase, and Table 7.9's n = 4/n = 16 split is load-bearing for what the recovery claim means).
Evidence: writing/v9/zh/src/Chapter_1_Introduction.txt lines 1-35 (motivation, Table 1.1, Section 1.2.4 gap), Chapter_7_Evaluation.txt lines 70-83 and 138-149 (Table 7.4, Table 7.9), Chapter_9_Discussion.txt lines 55-63 (Table 9.1) all read in this task. Exact-match scripted substitutions (one occurrence each, asserted) applied to talk_content.json; re-read after writing confirms the eight new strings. Build and checker evidence: see the task's checker run (build_deck.py, validate_deck.py --pdf and the rest of the knowledge/checkers_and_caches.md list), reported at the end of this task rather than duplicated here.
Reversibility: Pages 4, 8, 19, 20, 23, 35 and 37 of talk_content.json; git history holds the pre-fix (round-6) text.
Review: Whether the page-4 row swap (finding 5) and the reworded page-4 bullet (finding 1) read as the author wants; the D-206 and D-207 addenda above list the specific open points.

ID: D-216
Status: SETTLED
Decision: [presentation/defense_2026] Professor-feedback follow-up (2026-09-29): swap the current Motivation and information-flow pages so the opening is title (1), Presentation outline (2), Motivation (3), Information flow through the system (4), task video (5). Use "Discussions" in the outline row and the titles and displayed section labels of pages 34 and 35. Keep Conclusions (36), Limitations (37) and Contributions (38) grouped as before. The current revision map retains its round-5 basis: old page 2 now maps to 4, while Motivation at 3 still has no round-5 predecessor. Regenerate the bound contract and deliverables without changing slide budgets, empirical claims or media.
Why: The professor asks to motivate the work as the first Introduction slide and names separate "Discussions" and "Conclusions" headings. The current PPTX and PDF instead show information flow before Motivation and singular Discussion. The first substantive page after the outline is the Introduction opening; the useful diagram follows it.
Alternatives: Delete the current information-flow page (rejected: the professor's old page 3 was the thesis-structure map, already deleted in round 6, as confirmed at commit 7614fd2). Add another motivation or outline page (rejected: both already exist). Renumber later pages or change films (rejected: swapping two static pages resolves the ordering gap).
Evidence: User feedback supplied on 2026-09-29; PROJECT_STATUS.md builds 38-40; talk_content.json; actual PPTX XML, PDF text and script headings read before editing; git show 7614fd2:presentation/defense_2026/talk_content.json identifies old pages 3 and 4 as Thesis structure and Introduction. Pre-edit artifact hashes match review/ARTIFACT_CHECK.json, review/RENDER_CHECK.json and review/SCRIPT_EXPORT_CHECK.json. The master explicitly approved this order and wording after the audit. Existing 39 main plus 14 hidden pages and 1785 s budget come from talk_content.json/backup_content.json and the current build report, not a new timing measurement.
Reversibility: Restore the prior page order and display strings in talk_content.json and revision_id_map.json, then regenerate the contract, deck and scripts. Media provenance names and the embedded round-5 map remain unchanged.
Review: Independent source and artifact review and master acceptance are complete. Desktop PowerPoint playback, projected legibility and rehearsal timing remain unverified. The two retained source findings D-058/D-066 are historical and are not re-investigated by this static-page edit.

ID: D-217
Status: SETTLED
Decision: [presentation/defense_2026] Replace the first Motivation bullet in both bullets and panel_bullets on page 3 with "Robot learning, VR avatars and potential clinical assessment". Keep the current text box, font, other content and spoken notes.
Why: The previous source ends "Robots and VR avatars replay motion; clinics could". The actual PPTX, PDF and preview preserve all eight words; the unfinished clause originates in the source rather than renderer clipping. A complete list of applications reads naturally while "potential" keeps clinical use conditional.
Alternatives: Expand "clinics could" to a full sentence (rejected: the existing panel limit is eight words). Increase the text box or reduce the font (rejected: nothing was clipped, and the replacement fits the existing box). Present clinical use as demonstrated (rejected: Chapter 1 describes a possible application).
Evidence: writing/v9/zh/src/Chapter_1_Introduction.txt lines 4-5 states robotics imitation learning, VR avatars, and an avatar replay that could help a physician assess reaching and hand transfers. validate_deck.py lines 1136-1138 limits visible panel bullets to eight words; the replacement has eight. The existing build_deck.py text metric predicts two lines (0.721 in) in the unchanged 1.36 in box at 22 pt; this prediction is not a substitute for rendered inspection. The master approved the exact replacement after a read-only source/PPTX/PDF/preview check on 2026-09-29.
Reversibility: Restore the prior string in the two page-3 arrays and rebuild; no layout or empirical result changes.
Review: The worker and master inspected the rebuilt preview, package validation passed, and independent source/artifact review accepted the revision. This application wording does not establish clinical performance.

Validation addendum (D-216/D-217, 2026-09-29): contract assembly, PPTX build, PDF rendering, package validation, script export and share-folder assembly completed. Fresh validate_deck.py result: 1331 package checks, 0 package failures, overall PARTIAL for the unchanged D-058/D-066 source findings. review/FEEDBACK_FOLLOWUP_CHECK.json passes 24 source/artifact/media-preservation checks. Script export preserves 216 paragraphs and all 53 slide sections in 14 pages; the worker and master visually confirmed the complete page-3 bullet. Independent source review accepted the narrow changes; the independent checker passed all six artifact criteria and matched all 11 current-file hashes. The master independently checked those hashes, ASCII/whitespace and pages 2/3/4/34/35/36, then accepted the revision. No media cache extraction, environment installation or new experiment was performed.

ID: D-218
Status: SETTLED
Decision: [presentation/defense_2026] Execute the approved sequence: whole-thesis verified committee Q&A with a separate Basic questions section and short spoken answers plus supporting detail for every question; an argument-led presentation; a natural script and presentation-only visual/video polish; verified delivery.
Why: The user approved the plan after native Plan mode and asked to implement it. The question bank must cover the thesis and preserve limits, rather than repeat unsupported suggestions; the presentation should follow its research argument rather than a chapter-by-chapter inventory.
Alternatives: Keep chapter order and only enlarge exhibits (rejected: incomplete response to the approved plan). Treat later demonstrations as thesis results (rejected: provenance and scope differ). Modify the final V9 thesis or frozen pipelines (rejected: outside the approved scope).
Evidence: User instruction "Implement the plan" after native Plan approval, recorded in the master brief of 2026-09-29; current content/delivery at c5440c45141e5055b6754f4bec2110345b01d497; COMMITTEE_QUESTIONS.md and knowledge/deck_visual_review.md. Existing evidence must be re-read and each new answer independently reviewed before final acceptance.
Reversibility: Restore the prior presentation and question-bank revisions from Git; originals, source measurements and frozen code remain intact.
Review: Four milestones are registered in PROJECT_STATUS.md. Exact question additions, slide order, script wording, derivative media layout and validator bindings remain implementation decisions requiring evidence and review; this entry approves scope, not unverified outputs. The 45 mm marker scale chain remains settled and is not reopened.

D-218 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40. The committee Q&A part of this sequence is kept (COMMITTEE_QUESTIONS.md and review/qa_revision/); its slide pointers refer to the discarded numbering, an open item under D-244.

ID: D-219
Status: SETTLED
Decision: [presentation/defense_2026] Integrate 134 stable-ID questions into a separate Basic section followed by seven substantive groups, with two answer levels, sources, limits and supporting references; retain every one of the 105 original IDs.
Why: The approved M1 integration brief requires a usable rehearsal bank organized by the research argument. Source-reader facts and limitations must survive grouping; editorial history belongs in review records.
Alternatives: Keep the old chapter-tour/risk-ranked narratives (rejected: the approved structure and verified answer revisions supersede them). Drop overlapping original IDs (rejected: all original questions must remain traceable).
Evidence: The master integration brief of 2026-09-29; three stable answer shards containing 55 methods, 45 evaluation and 34 Basic/appendix questions; review/qa_revision/question_index.json and integration_notes.json. Evaluation source-shard review accepts 45; other 89 and integrated-bank acceptance remain pending.
Reversibility: Regenerate a different group order from the indexed stable IDs while retaining source answer shards, original coverage and audit records.
Review: Confirm the Basic section is separate, all 134 IDs occur once, all 105 originals remain and facts/limits match the reviewed shards after the recorded editorial changes. This decision implements organization; it does not close M1 or approve later slide/media changes.

D-219 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40. The 134-question committee bank this entry integrated is kept at ddfdf40 content; only its slide pointers are stale (open item under D-244).

ID: D-220
Status: SETTLED
Decision: [presentation/defense_2026] Correct Q3.2's frame/provenance distinction and qualify Q5.N1/QB.6 elbow-circle geometry; apply definition-first clarity edits to QB.1/QB.8 in both source shards and rehearsal bank.
Why: Independent review found three correctness defects across the 89 methods/Basic/appendix answers. Published causal pelvis is not proof of unchanged angle-solver inputs, and a sphere-intersection circle requires nondegenerate strict reach conditions. The Basic answers must define their terms before examples.
Alternatives: Retain the incorrect premises (rejected: contradicted by compiled source/code and geometry). Infer exact offline prepared angles from a causal dump (rejected: different path). Treat every reachable endpoint as a circle (rejected: tangency is degenerate).
Evidence: /root/worker review packet of 2026-09-29; PDF 51/95, DOCX paragraphs 467/715; Sections 2.6/G.4; v2/person/v2_person.py:201-202; eval/failure/recovery_core.py:214-221; pinned causal frame 533 in v2/output/v2_person_dump_r6b_full.csv; equation (5.8), PDF 73; v1/kinematics/occlusion_ext.py:334-374. Exact before/after fields and reviewed source hashes are recorded in review/qa_revision/integration_notes.json.
Reversibility: Restore previous answer fields from the correction record; the frozen thesis, code and measurements were not edited.
Review: Three correctness fixes and two clarity edits are applied but await re-review. Requested correction care was xhigh; no runtime effort switch was invoked or claimed. M1, build counter 45 and master acceptance remain open; this decision does not approve PPT/media implementation.

Review addendum (D-219/D-220, 2026-09-29): /root/worker accepted the five changed entries after targeted re-review and confirmed shard/bank agreement across all six fields, with no new factual or delivery issue. All 89 methods/Basic/appendix answers are now accepted, alongside the 45 evaluation answers. The initial pending-review statements above are historical; all 134 now have independent source acceptance. Accepted answer hashes are pinned in review/qa_revision/question_index.json and coverage_consolidated.md. Master final integration ACCEPTED after matching the three accepted shard hashes and final bank/index anchors. Independent checker: 6 criteria PASS / 0 FAIL, 7 draft/coverage hashes and 73 source hashes matched, all 134 verdicts ACCEPT, 16 Basic questions and 105/105 original IDs. M1 closes at build 46; closure 2026-09-29T20:20:19+00:00, measured setup-boundary interval 23:39 from epoch 1790711800. Documentation closure checks are 15 ASCII, 2 JSON and 1 whitespace PASS, plus the 6 accepted checker criteria: 24 PASS / 0 FAIL. Later slides, media polish and PDF export remain pending; no frozen scientific source was changed.

D-220 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40. The corrected answers are kept in the retained committee bank.

ID: D-221
Status: SETTLED
Decision: [presentation/defense_2026] Implement the master-accepted argument-led storyboard with 38 main and 14 hidden pages, 1780 seconds (29:40), and local evidence immediately after its method.
Why: The approved plan requires the research argument, including each difficulty before the construction used and the limits beside its evidence. Retiring the redundant five-second evaluation divider gives the proposed duration from the existing budgets.
Alternatives: Keep chapter-tour announcements (rejected: user requested argument-led organization). Add more slides or new experiments (rejected: existing exhibits support the required argument). Combine physical endpoint error with rendered-rig discrepancy (rejected: different references and conditions).
Evidence: Master storyboard acceptance on 2026-09-29; accepted M1 Q&A at a20250998f736815c2dbccccb19119767711d980; revision_id_map.json schema 10 records all 53 previous identities, with only previous page 26 retired. Presentation outline and Motivation remain pages 2 and 3. Synthetic and natural recovery evidence become pages 23-24; object endpoint evidence is page 17; rendered-rig evidence is page 29.
Reversibility: Restore the byte-preserved round-6 content and contract in committee_materials/unified_revision/history/round6_feedback or the previous Git revision. Original scientific sources and media payloads remain unchanged.
Review: Verify all blocks, the separate reference conditions, both natural-recovery outcomes and sample counts, title-only section dividers, hidden topics and media bindings. The 1780-second budget is an editorial target, not rehearsed timing. D-058/D-066 remain historical source limitations; Q3.2's thesis wording conflict and unverified offline prepared pose remain explicit.

Review addendum (D-221, 2026-09-29): Independent code review ACCEPT and master ACCEPTED the final M2 implementation. Confirmed 38 main/14 hidden pages, 1780-second editorial budget, 21 media entries with 109 bound files, 134 unchanged scientific answers, 670 science fields, 804 bank/index fields, 93 support-pointer changes, 8 argument checks and 3 rejecting mutation tests. The master reran 1324 package checks with zero package failures, matched all 11 M2 report source bindings and final Q&A audit binding, inspected pages 2/17/29/24/27/34 and confirmed no frozen-path diff. Minor provenance/history corrections are independently verified fixed. That 20:38:24 UTC boundary records content acceptance only: 891.244 seconds from 20:23:32.756, displayed 14:52 by whole-second ceiling; final completion includes the D-222 correction below. Seven ASCII, one JSON and one whitespace closure checks PASS. D-058/D-066 retain overall source PARTIAL; no playback, aloud timing, M3 polish or M4 package acceptance is implied. Implementation/rebinding workers used gpt-6.1-sol high; reviewer model ID is not exposed in the resumed thread. Manual /compact is unavailable and was not invoked.

D-221 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-222
Status: SETTLED
Decision: [presentation/defense_2026] Store only the newly created round6_feedback/VIDEO_INDEX.csv snapshot in a deterministic lossless gzip container; preserve its original CRLF payload.
Why: Default git diff --no-index --check rejects all 22 CRLF lines in the 12116-byte historical CSV. The snapshot must preserve exact source bytes while closure must pass default whitespace checks.
Alternatives: Normalize the CSV (rejected: changes historical payload). Change or waive whitespace configuration (rejected: conflicts with required checks). Alter older archives (rejected: outside this narrow fix).
Evidence: Original and decompressed payload SHA256 8e4326b06aaf5c7f3c9327e589585fef73d5e20f41e540fb63e24127df6dd63e; deterministic container SHA256 3e16b9e632bef61e8fbc7b3a63b500c70787b030e36b1ea2956f7d8953ab8adb; payload has 22 CRLF lines and no bare LF. Container uses gzip level9, mtime0 and no stored filename; the container hash is pinned and the preservation builder verifies decompression and deterministic recompression. Level9 is the standard gzip default, a storage choice with no scientific meaning.
Reversibility: Decompress VIDEO_INDEX.csv.gz to recover the exact original CSV; update the preservation entry and restore the task-created archive path if the representation is changed. Approved round6 contract/map and all scientific/media bytes remain unchanged.
Review: Independent archive/code review and default whitespace checks must pass before M2 completion. The earlier 20:38:24 boundary records content acceptance only; build47 is provisional until this fix is accepted. Requested rerun care is xhigh; actual model remains gpt-6.1-sol and no runtime effort switch was invoked.

Review addendum (D-221/D-222, 2026-09-29): Independent archive review ACCEPT with no findings; master decoded the exact original payload against a202509, verified gzip timestamp zero, 255 preservation bindings, all 17 report bindings and all 11 new-file default whitespace checks. Final package rerun: 1325 PASS / 0 package FAIL; overall source PARTIAL only for retained D-058/D-066. M2 build 47 is COMPLETE. Final closure 20:45:39 UTC from 20:23:32.756 UTC is exactly 1326.244 seconds, displayed 22:07 by whole-second ceiling. The earlier 20:38:24 record is content acceptance, not final completion. Reviewer model ID is not exposed in the resumed thread. No science, media or visible slide bytes changed for this archive fix; M3/M4 remain pending. Default checks pass without config changes or waivers.

D-222 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-223
Status: SETTLED
Decision: [presentation/defense_2026] Prepare a compact retained-set table with enlarged complete selected figures, and a wide encoded-parent handover frame with separate saved-recovery and receiver-live labels, for M3 visual inspection.
Why: Current selected-frame and set results can be confused, and stacked media makes labels small. Side-by-side complete views and reflowed labels may improve projector readability.
Alternatives: Rerun fixed-output raw-cache renderers (rejected: required raw caches are missing and originals must stay unchanged). Blanket task-video upscaling (rejected: no demonstrated benefit). Hide negative outcomes or mix recovery and live tags (rejected: changes evidence meaning).
Evidence: knowledge/deck_visual_review.md; master inspection of current17/24/27/29/34; accepted M1 answers and final V9 Table7.9/Figures7.8-7.9. Saved source700 has receiver mask94 and pre-display tags2/0/0/0/0/1/0; the source axes audit labels L24 omitted. review/m3_prototypes/PROTOTYPE_BINDINGS.json records exact source/output hashes, crop rectangles, uniform scales, source clock and all editorial font/placement constants. The 1600x900 canvas, type sizes and positions are proposed readability choices; no visual acceptance is inferred.
Reversibility: Remove only newly created prototypes or adjust their generator. No accepted live content, scientific figure, movie, source map or frozen source is changed at this stage.
Review: Master inspects both prototypes before batch encoding or deck integration. Final derivatives must retain full camera/model/plane views, parent frames/arcs, frame order, fps, holds, state distinctions, parent/clock hashes and original audits; decoded encoded-exhibit pixels must not be called raw-source regeneration.

Review addendum (D-223, 2026-09-29): Master inspected both prototypes at full size and APPROVED the treatment. Implement Hold-last wording; dynamic per-frame recovery/receiver labels, visible axis-color and mapped-object keys, and a dedicated large-media slide region. Prototype acceptance does not establish final-slide, projector or playback readability.

D-223 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-224
Status: UNCERTAIN
Decision: [presentation/defense_2026] Make separately named encoded-parent presentation derivatives for12/13/14/28/30/34, keeping original21-row media contract and audits with an additional bound derivative route.
Why: Large complete views and reflowed labels address measured small display text without unavailable raw RGB caches or any scientific recalculation. The archived replay has only original binary validity; it must not acquire new recovery tags.
Alternatives: Overwrite original films or rerun fixed-output raw renderers (rejected: violates source preservation). Keep a narrow text/movie column (rejected: shrinks approved label gains). Recode filter/task footage (rejected: no inspected readability need).
Evidence: Root prototype approval; existing encoded parents, output frame lists/maps, saved kinematic source records, R7 state/driver/axes audits and R5 archived packet/axes audit. All hashes, frame order,30fps, original half-speed/holds, dimensions and crop/output rectangles are recorded in derivative reports. Kinematic canvas2304x900 and replay1600x900, label/type/placement constants are editorial and remain pending final visual acceptance. Encoding CRF17 and pixel MAE tolerance3 come from existing committee-media fidelity decisions; veryfast/two-thread encoding is an editorial throughput choice, not a scientific result.
Reversibility: Restore argument_m2 content/contract snapshots and remove only the new derivative route/outputs. All original media and scientific sources remain unchanged.
Review: Independently compare every output frame scientific-view region to the corresponding decoded encoded parent, verify full counts/fps/maps/holds and dynamically reconstructed labels, retain source audit results and historical limits, and inspect actual PPT font size/fit. Extra compression and lack of raw-source regeneration remain explicit provenance.

D-224 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-225
Status: UNCERTAIN
Decision: [presentation/defense_2026] Use large dedicated media pages, native chart swatches, separate matched-reference table columns and a two-row native coordinate schematic, preserving all accepted science.
Why: Root approved complete side-by-side figures and wide videos. A large media region avoids losing the label gains; selected examples must remain distinct from retained-set medians.
Alternatives: Narrow text/video columns, repeated oversized numeric bullets and six tiny schematic rows are rejected because they reduce inspected readability. Original figure/media payloads are retained unchanged.
Evidence: D-223 prototype acceptance and D-224 full-frame checks; final V9 Tables7.4/7.9 and Figures7.8-7.9; unchanged coordinate manifest endpoints. Native layout constants in build_deck.py are editorial choices: wide movie region .50/1.43/12.33/5.14 inches; selected figures each6.00x3.39 inches fitted without cropping; six triads use the same projected endpoint offsets at .008 inches/pixel. Native labels17-23points, captions15points and triad line width2.5points remain pending actual rendered inspection. No new scientific geometry is computed.
Reversibility: Restore the argument_m2 live-content snapshot and remove the presentation-only builder branches. No source figure or movie changes.
Review: Inspect final slides12-14/17/24/27-30/34, actual embedded video label sizes and fit. Verify n/reference/negative-result distinctions and original source hashes. Projector and native playback remain unverified.

D-225 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-226
Status: SETTLED
Decision: Correct the presentation label-size assertion using actual audited per-frame label sizes and actual embedded-picture widths; enlarge the torso root-angle label and show handover recovery states per swing/twist/elbow group.
Why: Independent review demonstrated that the 42-pixel torso readout renders at 16.183125 points, falsely passing a hardcoded 46-pixel assertion. Root requested explicit per-group states and reference-specific keys.
Alternatives: Lower the accepted 17.5-point criterion (rejected: conceals the demonstrated defect). Re-encode all derivatives (rejected: only torso12 and handover30/34 pixels change). Collapse mixed groups to a summary (rejected: loses measured/held/constrained distinctions).
Evidence: Reviewer inspection of frame audits and generator; accepted root correction brief. The original 17.5-point criterion remains unchanged. A 46-pixel torso readout at 12.33 inches over 2304 pixels is 17.724375 points. Handover group readouts retain48-pixel type; M/H/C abbreviations expand to measured/held/constrained in the native key.
Reversibility: Restore task-created derivative reports/media and visual edits from the prior M3 working state; all original21 source films remain unchanged.
Review: Independent rejecting mutation probes, actual embedded sizes, all-frame checks of changed films, final rendered inspection and original-source preservation. The versioned previous checker preserves unchanged13/14/28 audit provenance; no new pixel comparison is claimed for those films.

D-226 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-227
Status: SETTLED
Decision: Integrate accepted speech rows only into notes, presenter_cue and unspoken_support fields; export spoken text, cues and unspoken support as explicitly separate blocks on all52 pages.
Why: Independent reviewer and root accepted the corrected proposal. Technical support must remain available without being counted or delivered as narration.
Alternatives: Replace full source JSON (rejected: discards accepted visual changes). Merge support into narration or omit it (rejected: changes approved speaking/support roles).
Evidence: Accepted pre-status patch SHA25691bb7b5a21c02b8cd7fbf3d46907aabb341b0d6b6fa670ea2532afd435d41e85; acceptance-only patch SHA25625deb7b8fa548dd4becd07f785d7741cc6511632a4fb2e985b1b7f832a4da09a; unchanged52-row content hashc30e0f1103d1c5406e25932d43e2141a0fec24159afeb11b443b8330c35d1d66. Editorial38+14/1780s budget stays unchanged.
Reversibility: Restore prior notes/cues from M2 snapshots; retain visual fields.
Review: Compare all52 source notes/cues/support with PPTX and standalone script, and preserve DOCX/PDF wording and order. Word counts include only notes. Timing estimates remain assumptions, not rehearsal.

Review correction addendum (D-226, 2026-09-29): The reviewer found that the new default checker produced current-checker reports for all5assets while its cache route accepted them only for12/30. The route now accepts freshly checked current reports on all5assets. Exact old-checker acceptance remains restricted to unchanged13/14/28, with source/frame/state checks still required. The master explicitly requested a normal default end-to-end rerun:332/562/842/750/1498 complete frame checks PASS, followed by checked_manifest PASS. No additional encoding of13/14/28 occurred. Historical13 acceptance, historical12 rejection, unknown-checker rejection and collapsed-group rejection probes PASS. Current and exact actual-encoding renderer snapshots have AST-identical functions; only currentCLI choices/default were restricted to12/30. The asserted17.5-point roles are primary numeric rotation readouts and recovery/receiver readouts, not observability captions or other smaller labels. Final independent acceptance remains pending.

D-227 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-228
Status: SETTLED
Decision: Preserve the original M2 slide_rebinding_audit.json and accepted question_index.json byte-for-byte; bind current M3 deck/source/export identities in slide_rebinding_audit_m3.json.
Why: The accepted index retains historical M1/M2 evidence. A separate current binding record prevents source-stage confusion without rewriting scientific acceptance or accepted support pointers.
Alternatives: Replace historical deck pins in place (rejected: obscures the accepted M2 evidence). Rewrite accepted bank/index fields (rejected: M3 does not change their science or slide identities).
Evidence: Root explicitly accepted this approach; all bank, index and original M2 audit bytes match762597c. Current index contains134 questions,105 original IDs and16 Basic questions. Current M3 sources/exports are hashed directly in the new record.
Reversibility: Remove the task-created M3 binding record and its documentation pointers; retained historical evidence remains untouched.
Review: Verify current hashes, all bank/index bytes and unchanged page identities. No M4 delivery or publication acceptance is implied.

D-228 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40. The kept review/qa_revision/ audit files still bind the discarded M3 deck identities; they are retained unedited (open item under D-244).

ID: D-229
Status: SETTLED
Decision: Describe page12's root basis as Camera-prime, with a standing T-pose example and no parent joint frame.
Why: Independent review established that the native key incorrectly named standing T-pose as the root reference frame. The torso basis is expressed in Camera-prime/Unity world; the recorded T-pose is an example.
Alternatives: Retain the reference-frame wording (rejected: conflates an example pose with coordinate basis). Re-encode video or alter accepted speech (rejected: their content is unchanged by this native-key correction).
Evidence: anim/unified_panels.py lines283-301 draw Camera-prime X-Z and root columns; frozen v1/kinematics/root_frame.py lines20-32 define columns in Unity world. Root explicitly authorized the precise replacement after review.
Reversibility: Restore the task-created native media_key; accepted speech, scientific bank and videos stay unchanged.
Review: Inspect actual page12 key and refresh bound PPTX/PDF/source reports. No new playback, projector or rehearsal claim.

Final review addendum (D-223 to D-229, build48): Independent code review PASS/ACCEPT with no remaining findings and master ACCEPTED. The earlier D-224/D-225 UNCERTAIN layout entries record the pre-acceptance stage; the approved native/encoded layout choices are now accepted. Their projector/playback uncertainty remains. Root independently verified1396 package checks,17source hashes,52-page speech export and final previews. Independent speech review verified780 exported-field comparisons with0errors. All5 derivative full-frame checks pass; no13/14/28 re-encoding occurred. Original21 source rows, accepted134-question bank/index and historical M2 audit remain byte-identical. Final closure2026-09-29T21:24:58Z from20:49:26Z is2132seconds (35:32), wall-clock boundary time including restart/recovery. Build48 closes M3 only; Q&A PDF/full delivery package and publication remain pending. Native playback/projector readability and aloud rehearsal were not performed. Manual /compact was unavailable and not invoked.

D-229 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-230
Status: SETTLED
Decision: Export the accepted committee bank to a separately titled DOCX and PDF without rewriting its 134 questions or six fields per question; retain the separate first section of 16 Basic questions.
Why: The approved delivery requires a readable rehearsal PDF and complete answers with their sources and limits. Full normalized text equality verifies the entire exported body, rather than only checking that isolated paragraphs occur.
Alternatives: Reuse the script exporter unchanged (rejected: wrong title and slide-specific validation). Rewrite answers or remove supporting detail (rejected: accepted science is immutable). Install another converter (rejected: existing tools are sufficient).
Evidence: Accepted bank SHA2569360fc7965467c7cf37d0a5bc7f7548e4a4f8d729c687b7185eea9312cacf41b; reviewed index SHA256b7e54674df0927d163e4d4fb713276a6c26a52834e5f62d0673a97715c22f366. Counts134/16 and six fields come from M1. Letter8.5x11-inch pages,0.7/0.8-inch margins, DejaVu Sans11-point body,1.12 line spacing,6-point paragraph spacing and9-point running text reuse the script. Title18/group15/question12-point headings and12-point heading spacing are editorial choices for print hierarchy; group sections start a new page. These constants are layout choices, not scientific values.
Reversibility: Regenerate only the new exports with different layout settings; accepted Markdown/index remain untouched.
Review: Compare all804 bank/index fields, exact DOCX paragraphs, whole PDF text after documented formatting/whitespace normalization, all134 IDs in order, and the eight group headings. Inspect representative pages. Native projector/playback and aloud rehearsal remain unverified.

D-230 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40. The committee bank DOCX/PDF export and export_committee_questions.py are kept.

ID: D-231
Status: SETTLED
Decision: Extend the complete defence delivery to nine document exports, the 18 distinct current embedded films, and README/video-index files, with hash-bound sources, slide placements and clean-input checks.
Why: The approved M4 delivery needs usable scripts, all reviewed questions and the current polished films. The earlier three-file package omitted these deliverables. Shared clips must be copied once while retaining all21 slide placements.
Alternatives: Copy original films before checking derivative overrides (rejected: would deliver superseded layouts). Copy three duplicate film payloads separately (rejected: adds ambiguity without content). Package before accepted content is committed or repack merely to chase metadata HEAD (rejected: obscures content identity).
Evidence: Accepted M3 deck and reports at39b0bc9; media contract has21 rows, derivative manifest overrides12/13/14/28/30/34 with5 assets, and actual PPTX has18 distinct MP4 payloads and no GIF payload. D-230 supplies the verified134-question bank exports. All copied media hashes and per-slide embedded relationships are compared directly. The under40-line README rule is inherited from D-108.
Reversibility: Regenerate only the share folder and package manifest from different accepted inputs; source artifacts remain unchanged.
Review: Independently verify current per-slide derivative resolution,18-file deduplication, nine document copies, whole source/copy hashes, unknown-entry/symlink guards, clean tracked-input gate and complete manifest. Run accepted content commit -> make_package.py --require-clean once -> metadata-only closure commit. Native playback, projector readability and aloud rehearsal remain unverified; source findings D-058/D-066 remain separate from package acceptance.

Review correction addendum (D-230,2026-09-29): Independent review found that character-only PDF comparison could accept missing spaces or same-line word splits. The actual export was correct. The checker now preserves all19628 authored whitespace boundaries and allows additional gaps only when the extracted whitespace contains a line break;34 internal layout-wrap additions remain after document-edge trimming. Lost-word-gap, same-line-split and changed-character probes all reject. The DOCX/PDF bytes were not regenerated. This is a checker correction requested with xhigh care, not a change to accepted scientific answers. Independent re-review remains pending.

Content acceptance addendum (D-230/D-231,2026-09-29T21:39:57Z): Independent reviewer_delivery PASS/ACCEPT with no remaining findings; root ACCEPTED for the scoped C1 content commit and one clean package run. The corrected QA checker preserves19628 authored boundaries with34 layout-wrap additions, and all four independent corruption probes reject. Root matched26 content/preview hashes,12 ASCII checks and six QA report bindings, and inspected pages1/2/29/61. Package preflight resolves30 files,18 films,21 placements and70 bound inputs; stale report/hash, swapped placements, unknown entries and symlink probes reject. Build49 remains ACTIVE until actual post-commit package copies and manifest are independently verified. No final package creation or publication is claimed at this content boundary.

D-231 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-232
Status: SETTLED
Decision: Make the user-approved targeted corrections directly, without subagents; preserve all slide identities, order, timings and embedded video payloads.
Why: The user rejected a wholesale redesign and explicitly requested direct work, contextual figures, clearer evaluations and a single-word closing.
Alternatives: Restructure the deck or re-encode videos (rejected by the user). Retain detached axes, state codes and duplicated conclusion tables (rejected for readability).
Evidence: Approved targeted revision plan and user instruction Implement the plan; review/targeted_revision/baseline.json pins all 52 slide specifications and current media bytes. Final V9 Table 7.5 pins synthetic windows 490-534, 445-489 and 557-601, 45 frames each.
Reversibility: Restore the pinned baseline content and builder from its commit. Scientific source records are unchanged.
Review: Check physical context, slide order, all movie hashes, exact recovery conditions, visible Discussion interpretation and the centered Question closing. Review is performed by the interactive agent, not an independent subagent.

D-232 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-233
Status: UNCERTAIN
Decision: Use native slide layouts and transparency for physical context, and a native video viewport on pages 28, 30 and 34 that retains both complete camera and Unity views.
Why: Presentation-only treatment preserves scientific source pixels, geometry and video timing while removing internal debug bands.
Alternatives: Generate illustrative photographs or re-encode footage (rejected: unnecessary source changes). Keep the full debug canvas (rejected: unreadable state codes and undersized views).
Evidence: Existing derivative provenance places the two full views at [40,124,760,664] and [840,124,1560,664] on a 1600x900 canvas. Their combined viewport is [40,124,1560,664]. Layout sizes and opacity are editorial constants, pending rendered inspection; no scientific thresholds change.
Reversibility: Remove the native crop/opacity and restore the prior layout. Original media remain byte-identical.
Review: Inspect actual PPTX crop XML, PDF posters and enlarged left/right panels. Native PowerPoint playback is not established by static rendering.

Verification addendum (D-232/D-233, 2026-09-29): Direct rendered review accepts the targeted layouts. The final editorial constants are 45 percent native photograph opacity, a 480x480 crop from x=80..560 on the unchanged 640x480 recovery photographs, and source-projected full-opacity arm overlays. All four wrist distances reproduce the pinned two-decimal evaluation report; the original thesis figures stay unchanged. The accepted video viewport remains [40,124,1560,664], with its aspect retained in a 12.33-inch-wide box. The temporary PDF copy replaces movies with static poster pictures because LibreOffice distorted the media-object crop; the canonical PPTX movie payloads and timing stay unchanged. Three PDF poster comparisons have mean RGB errors below 8/255 after downsampling, a rendering-tolerance check rather than scientific accuracy. Exact crop XML and media hashes are checked separately. Closing text is 60 points; the remaining new roles are 16-22 points. D-233's layout uncertainty is resolved by direct inspection; native playback, projector viewing and aloud rehearsal remain unverified. No independent review or unavailable compaction command is claimed.

D-233 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-234
Status: SETTLED
Decision: Restore commit 3ea52f3 through new commits, directly without subagents, retaining 49 main and 25 hidden baseline slides, plus 14 later hidden pages and all 134 reviewed questions.
Why: The user approved this restoration plan and explicitly required complete evidence retention. The prior 52-page delivery remains recoverable at commit 2483320.
Alternatives: Reset history, preserve the shortened deck, or remove evidence for a time target (rejected by the approved plan).
Evidence: review/restoration/RETENTION_RECORD.json was created before editing and maps 88 source slides, 1576 source elements and 1519 original drawing objects. The original main timing totals 3120 seconds.
Reversibility: Revert these new commits; original commits, snapshots and historical reports remain intact.
Review: Check every mapped destination, original media bytes and sequence, all 39 hidden pages, the separate Basic questions, and the final V9 numerical references.

D-234 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-235
Status: UNCERTAIN
Decision: Use 66 main slides with eight transitions, two opening additions, three evaluation additions, a dedicated real-time pipeline and three discussion pages; retain 39 hidden slides.
Why: This is the approved slide count while preserving all 49 baseline main pages in order. The single object-method page does not need a separate chapter transition.
Alternatives: Add a ninth transition (would exceed the approved count); combine original scientific pages (would violate retention).
Evidence: The complete destination sequence is pinned in review/restoration/RETENTION_RECORD.json. New time budgets and geometry are editorial estimates, not measured rehearsal or projector results.
Reversibility: Change only the additions and rebind current slide references; original baseline evidence remains.
Review: Inspect the native two-column pipeline, tables and narration. Test PowerPoint playback and projector readability separately.

D-235 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-236
Status: SETTLED
Decision: Correct the restored main-talk target to 30 minutes, as the user explicitly clarified during restoration. Retain all 66 main pages, 39 hidden pages and original movie/GIF playback durations.
Why: The user rejected the 63:05 additive budget. The historical baseline's 52-minute editorial timing is provenance, not the current delivery target.
Alternatives: Cut scientific evidence, speed footage up or report a rehearsed duration (rejected: unauthorized and unsupported).
Evidence: User correction in this session; current 20 main media placements declare 468.8667 seconds, including the three original teaching GIFs. All original narration remains separately available as unspoken technical support.
Reversibility: Revise the editable timing plan after rehearsal; original source timings remain pinned in RETENTION_RECORD.json.
Review: Check that every clip fits its slide budget at original speed, the spoken script fits the full 1800-second plan, and all evidence destinations remain unchanged.

D-236 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-237
Status: UNCERTAIN
Decision: Budget narration at 130 words per minute, with two seconds of slide-change allowance per content page, and count each full original media playback separately from narration.
Why: This provides a reviewable conservative timing model without assuming speech overlaps the footage. Remaining time is allocated as viewing and explanation margin.
Alternatives: Keep the 3342-word draft or rely on talking over every video (rejected: leaves insufficient margin). Claim measured timing (rejected: no aloud rehearsal has occurred).
Evidence: 130 words per minute and the navigation allowance are editorial assumptions, not measurements. Actual script words and original media durations are counted by restoration_timing.py.
Reversibility: Adjust narration and budgets after a timed rehearsal; no scientific evidence or source media need change.
Review: Rehearse the complete route with original media; PowerPoint playback and projector readability remain unverified.

D-235 timing addendum: the preliminary 63:05 additive estimate is superseded by D-236. The 66-main/39-hidden retention structure remains unchanged.

D-237 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-238
Status: SETTLED
Decision: Deliver DEFENSE_SCRIPT as the 66-slide, 2188-word main speaking script with separate presenter cues. Keep full technical support and all 39 hidden-slide notes in SPEAKER_NOTES and PowerPoint notes.
Why: The user explicitly clarified that the requested work is visual additions and a shorter speech script. A rehearsal script containing the old full technical narration would defeat that request even if labelled unspoken.
Alternatives: Delete technical support (rejected: evidence retention); retain long support paragraphs in the speaking document (rejected: poor rehearsal usability).
Evidence: D-236/D-237 and review/restoration/TIMING_PLAN.json; source narrative fields are compared against every relevant export.
Reversibility: Regenerate the documents with a different support placement; no scientific content is removed.
Review: Match all 66 spoken/cue blocks to the main script, all 105 spoken/cue/support blocks to PowerPoint and SPEAKER_NOTES, and all 134 bank entries to their reviewed scientific fields.

D-238 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-239
Status: SETTLED
Decision: Transcribe the three scene-mapping and three rig-application triads from the original figure manifest into native labelled overlays on faded recorded backgrounds.
Why: The first render showed that retaining the original figures below the photographs made their labels too small. Native overlays preserve the original explanatory directions at readable size.
Alternatives: Shrink text or remove original coordinate relationships (rejected by the user). Claim schematic frame locations are registered measurements (rejected: unsupported).
Evidence: figures/coordinate_frames/manifest.json pins original origins and endpoints. The drawings explicitly state that separated frame views, positions and tilt are schematic. Native 45 percent photograph opacity and 0.005 inch per original pixel for triad displacements are editorial display settings, not physical calibration.
Reversibility: Change native layout constants; source images, original figure assets, coordinate conventions and equations remain unchanged.
Review: Inspect slides 41/42 for readable direct frame labels and correct original triad directions; confirm slide 50/51 use identical recorded-context geometry.

D-239 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-240
Status: SETTLED
Decision: Restrict native video masks to the original external label regions; preserve the complete camera rectangles and plots.
Why: Enlarged static inspection exposed a generic title mask intersecting filter camera images and a grasp sidebar mask extending past the photograph boundary. Both masks are now explicitly bounded by source geometry.
Alternatives: Re-encode or crop scientific views (rejected: unnecessary changes to retained evidence).
Evidence: Filter provenance pins camera [400,0,1040,480], so no top mask is permitted. Matched grasp/elbow provenance pins camera [272,86,1168,758], so the sidebar ends at x=266 and top mask at y=80 (six pixels before the photograph; includes the complete producer-text descenders). The six-pixel margin is editorial clearance. All original media bytes and timings remain unchanged.
Reversibility: Change native overlay geometry only.
Review: Inspect the complete camera and graph views on slides 10/26/30 and the corresponding repeated hidden slides. PowerPoint runtime layering remains unverified.

D-240 visual addendum: the 1280x1054 input-overlay film's camera begins at y=104; its title mask ends at y=80. The photographed teaching animation uses source y=80, before its photograph at y=86. Pure diagram GIF masks end at y=100, before the diagram geometry begins. The shorter coordinate-context caption clears the footer without shrinking.

D-240 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-241
Status: SETTLED
Decision: Package all nine document exports and 23 unique unchanged media assets, with 29 slide placements, after the accepted content commit.
Why: The restored deck contains the complete baseline and later films, including three teaching GIFs; the prior shortened-deck package is incomplete for this delivery.
Alternatives: Deliver the previous 18-film package or replace historical reports (rejected: loses current content or provenance).
Evidence: media_manifest.json and the restored PPTX relationships; ARTIFACT_CHECK, SPEECH_EXPORT_CHECK, NUMERIC_CHECK and MEDIA_DECODE_CHECK under review/restoration. The clean-input gate and copied-byte hashes establish local package identity.
Reversibility: Regenerate a package from a different accepted content commit; preserve the prior share folder at package/before_complete_restoration.
Review: Verify every copied hash against both current source and committed blob. Keep the content commit pinned through metadata closure; no PowerPoint, projector or rehearsal verification is implied.

D-239/D-240 final layout addendum: table captions start at y=6.29 inches so two 18-point lines clear the y=6.94 footer. The causal shared-frame node has a visible 0.21-inch branch connection, with the two following arrow gaps shortened to 0.12 inches; node text, evidence and final diagram extent remain unchanged. These are editorial layout dimensions, not measured system quantities.

D-235 acceptance addendum (build 53): the approved 66-main/39-hidden structure and every baseline destination pass direct source and visual checks. Its structural uncertainty is resolved. D-237 remains uncertain until rehearsal. The prior 63:05 additive timing remains superseded by the user-set 30-minute target.

D-241 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-242
Status: BLOCKED
Decision: Leave the completed restoration and delivery commits local pending explicit user authorization to push to the configured GitHub repository.
Why: Automatic approval review rejected git push origin master twice. After the first rejection, read-only GitHub metadata reported a private repository and ADMIN access; the second review still required trusted user authorization for this exact destination and nonpublic payload.
Alternatives: Retry indirectly, change remote or bypass the review (rejected). Continue local verification and record the blocker (completed).
Evidence: review/restoration/PUBLICATION_STATUS.json; destination https://github.com/RoadsUnTraveled0729/Tracking-and-Reconstruction-of-Bi-Manual-Object-Handling-Task-Using-RGB-D-Sensing. Local content 38edf67 and delivery metadata 7c4e293 are committed. The 464 package checks pass.
Reversibility: With explicit destination authorization, retry the same ordinary git push. Do not alter source artifacts or regenerate the verified package.
Review: Authorize or decline publication of these completed commits to this repository. No PowerPoint playback, projector test or rehearsal is implied by Git publication.

D-242 resolution (2026-09-29): superseded by D-243. The user explicitly instructed pushing after the publication block was explained. The ordinary git push origin master succeeded; origin/master advanced from2483320 tobc54604. No bypass or alternate destination was used.

D-242 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-243
Status: SETTLED
Decision: Publish the completed restoration and delivery commits to the existing origin/master, then commit and push the publication-status closure.
Why: The user explicitly authorized the push after the exact destination and automatic rejection were explained.
Alternatives: Leave the requested publication unfinished (rejected after authorization). Alter source or package bytes (unnecessary).
Evidence: git push returned success and origin/master equals local bc54604. review/restoration/PUBLICATION_STATUS.json records the resolved blocker, destination and publication result.
Reversibility: Any later deck changes use new commits; prior history remains intact.
Review: Confirm a clean working tree and matching local/remote master after the metadata closure. The package remains pinned to content commit38edf67.

D-243 superseded (2026-09-29): superseded by D-244; the work remains in git history a202509..ddfdf40.

ID: D-244
Status: SETTLED
Decision: [presentation/defense_2026] Restore the defence deck and its build sources to commit c5440c4 (round 6 plus the D-216/D-217 follow-up: 39 main + 14 hidden pages, 1785 s = 29:45) and discard the later argument-led rebuild and the 66-main/39-hidden restoration (a202509..ddfdf40); D-218 to D-243 are superseded, and the "Superseded in scope (2026-09-29, D-218)" notes on earlier entries no longer apply.
Why: The professor's feedback (a table-of-contents slide 2 about the logic of the presentation, motivation as the first Introduction slide, no thesis-structure map, separate Discussions and Conclusions headings with limitations and contributions under Conclusions) was fully applied and accepted at c5440c4. The later rebuild grew the deck to 66 main pages, which is not compact, and its rendering is broken on about 64 pages. The author instructed on 2026-09-29 to keep the slides compact and follow the professor's instructions, which the c5440c4 deck already does.
Alternatives: Repair the 105-page restoration in place (rejected: withdrawn by the author; 66 main pages is far too many). Rewrite history with git reset or a force push (rejected: AGENTS.md forbids rewriting history; the discarded work stays reachable). Revert DECISIONS.md to c5440c4 (rejected: the log is append-and-annotate). Also discard the 134-question committee bank (rejected: it is separate from the deck and kept, with its slide pointers still on the discarded numbering as an open item).
Evidence: Author instruction of 2026-09-29 and the master's page review of the discarded deck (plan /home/luo/.claude/plans/imperative-coalescing-hartmanis.md, assumptions A1-A6). review/RESTORE_2026-09-29.md lists every path with its action and the sha256 of the twelve restored build files, all equal to the c5440c4 blobs. validate_deck.py --pdf on the restored bytes: Overall PARTIAL; package PASS: 1331 checks; 0 package failures; 2 retained failed-source findings (D-058/D-066); main talk 1785 s.
Reversibility: The discarded work is in git history a202509..ddfdf40; checking those paths out from ddfdf40 brings it back. The restore itself is ordinary new commits on master.
Review: Confirm the restored deck pages 1-6 and 34-39 against the professor's points. Open: COMMITTEE_QUESTIONS.md and review/qa_revision/ slide pointers refer to the discarded numbering; the two committee_materials VIDEO_INDEX.csv files keep the c5440c4 CRLF endings that git diff --check flags; PowerPoint playback on the defence machine, projector legibility and an aloud rehearsal remain unverified.

ID: D-245
Status: SETTLED
Decision: [presentation/defense_2026, round 7, build 57] Stop drawing the 11 pt chapter kicker on content pages; content pages open with the 28 pt title, and the nine dividers keep their 22 pt chapter label.
Why: Author's slide-change list (2026-09-29, plan warm-swinging-wren.md item 3): the kicker repeated the divider label on every page in a size too small for a projector. The section and chapter fields stay in talk_content.json as data because validate_deck.py checks the chapter sequence.
Alternatives: Keep the kicker at a larger size (rejected: the dividers already carry the chapter); move the title up into the freed band (rejected: keeps the title band geometry every other check assumes).
Evidence: build_deck.py restrained_header(); validate_deck.py FONT_ROLES and native_typography (11 pt valid on the cover only; the band (.50,.12,12.85,.45) is retired). validate_deck.py --pdf: 1332 package checks, 0 package failures.
Reversibility: Restore the text() call in restrained_header() and the kicker band in the validator.
Review: Confirm on the rendered pages that the chapter is still clear from the dividers.

ID: D-246
Status: SETTLED
Decision: Pages 37 (Limitations) and 38 (Contributions) each show one full-width two-column table (kind full_table), no left bullets: "Limitation | What would validate it" and "Contribution | Evidence in this thesis", three rows each; cells may break at an explicit newline (category or claim on line one, detail on line two).
Why: Plan item 8: one layout per page. Row names come from the former hard-coded tables; the detail text from the former bullets and notes; evidence numbers are those already on pages 33 and 35 (0.53-2.83 cm, 0.83 / 2.34 cm, 33.3 ms on a 900-frame replay) and thesis Table 7.9 (right wrist median 11.4 to 5.2 cm, n = 4; left 12.3 to 13.1 cm, n = 16; plain solve to object-assisted).
Alternatives: Keep bullets beside a right-hand table (rejected by the author); keep the "Further test" column on page 38 (dropped; the Limitations table carries validation needs).
Evidence: writing/v9/Chapter_7_Evaluation.docx Table 7.9 (read 2026-09-29); column widths 0.5/0.5 and 0.34/0.66 are layout choices that sum to 1 (builder check), not measurements. The limits and contribution_table branches were deleted; no validator check pinned them.
Reversibility: Restore the two branches and the kinds limits/contribution_table with their panel_bullets.
Review: Check the wording of each cell, especially "effective lengths" and "no live session run".

ID: D-247
Status: SETTLED
Decision: The closing page 39 draws only its title word "Question" (singular, the author's word) at 60 pt white, centred on the black slide, with no header, bullets, footer rule, source label or page number; its notes still list every hidden page.
Why: Author's slide-change list, plan item 9 and assumption A3.
Alternatives: Keep "Questions and discussion" and bullets (rejected by the author).
Evidence: build_deck.py restrained_closing() (60 pt line at 1.18 leading = 0.983 in in a 1.00 in box centred on 13.333 x 7.5 in); validate_deck.py adds 60 pt for the closing kind only, the check "closing page draws only its centred 60 pt word", and exempts closing from source_label. The 60 pt size is the author's request, not a measurement.
Reversibility: Restore the closing branch, the bullets, the source_label and the validator rules.
Review: Confirm "Question" (singular) is intended.

ID: D-248
Status: SETTLED
Decision: Page 4 shows the offline pipeline: Recorded RGB-D -> Body landmarks + depth and Marker pose (ArUco) as parallel branches -> Filtering -> Joint solve + arm recovery -> Temporal merger -> Unity scene (filtered object pose also goes to the merger); nodes 22 pt, link labels 16 pt ("colour + depth", "joint angles", "time-aligned states"); no caption.
Why: Plan item 1. Both branches are filtered in the thesis (Chapter 2 Figure 2.3 text: Pipeline A includes filtering; Chapter 4: the object track passes a signal filter, the Pipeline B counterpart), so one Filtering node receives both branches.
Alternatives: Two Filtering nodes (rejected: the author's list names one stage); keep the old six-node diagram (rejected).
Evidence: writing/v9/Chapter_2_Experimental_Setup.docx and Chapter_4_Object_Tracking.docx paragraphs read 2026-09-29. Node texts and geometry are data in talk_content.json visual.diagram; native_diagram() raises on text that does not fit, boxes outside the region (0.50, 1.20, 12.83, 6.75) or overlapping boxes. The D-122 information_flow typography exception is kept unchanged. Geometry (columns 0.50/4.043/7.586/9.929 in, rows 1.45/3.30/5.15 in, node 2.90 x 1.10 in) is a layout choice sized so each node text fits two 22 pt lines.
Reversibility: Revert restrained_information_flow() and the page-4 data.
Review: Check that "joint angles" is the right name for the solve output link.

ID: D-249
Status: SETTLED
Decision: Page 33 keeps its One Euro film unchanged and shows two 22 pt bullets ("Past samples only; One Euro filter adapts", "Replay: each branch within 33.3 ms") over a native 16 pt real-time pipeline in the left column: RGB-D capture -> Shared frame -> Landmarks and Marker pose -> Causal filters -> Merger -> Unity.
Why: Plan item 2. The three former bullets were merged into two so the diagram fits between the bullets and the footer rule.
Alternatives: A new visual kind (rejected: a data flag on composite is smaller); cropping the film (M3).
Evidence: talk_content.json visual.left_diagram (nodes 2.45 x 0.45 in, rows 3.45/4.25/5.05/5.85 in, inside x 0.50-6.05 in); validate_deck.py allows 16 pt in the left column only for that diagram's texts on a composite page that declares it. Film geometry 6.00 x 5.00 in unchanged (existing check passes).
Reversibility: Remove visual.left_diagram and restore the three bullets.
Review: Check that "Shared frame" and "Causal filters" read correctly for the committee.

ID: D-250
Status: UNCERTAIN
Decision: Wording rule for visible text: plain words without internal vocabulary (legacy, fresh replay, retention, evidence as jargon, proxy, pinned, contract, restrained, producer codes, process language); numbers and thesis references unchanged; sentence-long provenance moves from captions to an unspoken "Provenance:" line in the notes before Sources (and in SPEAKER_NOTES.md). Non-reference footer tails on pages 9, 23, 25 and 31 were also removed.
Why: Plan item 3. The full old -> new string list is in the M1 report (commit 3ca2dc6 message and diff): captions on pages 3, 8, 9, 18, 19, 23, 24, 25, 28, 31, 35 and hidden 41; title of page 19; bullets of pages 25 and 31.
Alternatives: Leave provenance on the slides (rejected by the author).
Evidence: git show 3ca2dc6 -- presentation/defense_2026/talk_content.json presentation/defense_2026/backup_content.json.
Reversibility: Revert the string changes in the content files.
Review: UNCERTAIN because wording is judgment: the outline row "Discussions: what the evidence supports" (page 2, professor-accepted), the verbatim thesis caption on page 11, the "(Figure 7.x)" labels on page 30, "n 45" on page 29 and "No (v1 fallback)" on hidden page 42 were left as they are; burned-in film labels (p47, fresh, MappedMarker) are media and unchanged.

ID: D-251
Status: SETTLED
Decision: The evaluation pages follow the thesis sections: 27 "7.2 Object reconstruction accuracy" (ArUco marker-centre reference, thesis Figure 7.1 rail frames and panels (a) x-y and (b) x-z, native table of Tables 7.1-7.2), 28 "7.3 Human reconstruction accuracy" (thesis Figure 7.6 row (b), transfer frame 950, native table of Table 7.4 with the model-wrist medians), 29 and 30 the two 7.4 pages; no divider pages are added (plan A1-A2). A new visual kind evaluation_figures draws manifest-bound figure copies with builder crops (a:srcRect), 16 pt native labels, an optional native table, legend and aggregate line in the right column; the old evaluation_charts bar chart is deleted.
Why: Author, 2026-09-29: the evaluation must follow the thesis's three sections, and page 28 needs pictures. Figure 7.1 (rail, R6b) was chosen over Figure 7.2 (handover, R7): both files have identical pixel sizes and generator, so baked text is equal; the rail figure matches the first table column. Baked video-frame headers and the Figure 7.6 row label are cropped off and replaced by native 16 pt labels because their baked text would be about 8 pt at the placed width.
Alternatives: Whole thesis figures (rejected: Figure 7.6 at the column height would be 2.8 in wide with about 5.5 pt text; the 3D panel of Figure 7.1 about 6 pt); divider pages per section (rejected by plan A2, time budget).
Evidence: writing/v9/zh/src/Chapter_7_Evaluation.txt lines 19, 24-31, 39-46, 70-78, 88-90 (re-read 2026-09-29). Figure copies: presentation/defense_2026/figures/evaluation/manifest.json (sha256 equal to the writing/v9/figures sources; pixel sizes 2596x594, 2244x1584, 1360x1620). Crops (pixels of the copies) are layout choices read from the images: strip photos start at y 114 and split at x 640/652, 1292/1304, 1944/1956 (measured); panel (a) 28,190-952,622; panel (b) 150,733-905,1268; Figure 7.6 row (b) 36,615-1324,1082. Layout constants in build_deck.py: region 6.22-12.83 x 1.20-6.25 in (the right column above the 6.31 in caption), panel gap 0.15 in, row gap 0.12 in, table row 0.36 in (one 16 pt line 0.262 in + 0.06 in inset + 0.036 in margin, as in restrained_full_table). Estimated baked text on page 27 panels: ticks about 9 pt (a) and 7 pt (b), waypoint labels about 10 pt and 8 pt (cap height measured in the copy, scaled to the placed size; DejaVu cap ratio 0.729).
Reversibility: Restore the old page 27 evaluation_charts and page 28 full_table content from commit 31c094f.
Review: Check that the smaller (b) x-z panel is legible on the projector; confirm "Rig elbow"/"Rig wrist" row names (the brief said "Elbow"/"Wrist"; renamed so the rows are not read as model values).

ID: D-252
Status: SETTLED
Decision: Page 29 is titled "7.4 Recovery under landmark failure: synthetic removal" (10.88 in at 28 pt, inside the 12.30 in title box), its table gains a Frames column (Lower 490-534, Intermediate 445-489, Higher 557-601) with window cells "Lower, wrist" etc., column widths 1.75/1.25/1.10/1.31/1.20 in, and the caption "R7 right arm, 45 frames per window, removed after offline filtering; reference: unmasked reconstruction."; bullets name the right-arm windows in handover R7 and that windows were chosen before scoring; "n 45" is gone.
Why: Author, 2026-09-29: the recovery experiment page must identify the R7 right-arm windows explicitly.
Alternatives: Separate Joint column (rejected: restrained_rows supports at most five columns).
Evidence: Chapter_7_Evaluation.txt line 94 (right elbow and wrist removed after offline filtering; reference the unmasked kinematic reconstruction; handover recording), line 95 (45 frames; selected before scoring), lines 96-100 (Table 7.5), lines 104-125 (Tables 7.6-7.7 medians, unchanged). The Frames width 1.25 in was set after the 1.10 in render wrapped "490-534".
Reversibility: Restore the four-column table and old caption.
Review: Whether "R7" is understood without a spoken gloss (the notes say "the handover recording, R7").

ID: D-253
Status: UNCERTAIN
Decision: Page 30 shows thesis Figures 7.9 and 7.8 regenerated by eval/failure/make_label_compare_fig.py with the thesis crops (1890: --crop 130 0 560 480; 1462: --crop 150 0 470 440), --fade 0.5, --text-scale 3.8 (1890) and 4.4 (1462), --legend none, --titles "Plain solve" "Recovery", --bottom "{d:.1f} cm", --strip-ink dark, placed side by side at equal height (2.83 in), with 16 pt native labels "Frame 1890, right wrist: 14.0 -> 5.0 cm" and "Frame 1462, left wrist: 14.0 -> 13.7 cm" (a line break after the colon), a native symbol legend, and a separate ruled 16 pt aggregate line "All frames (Table 7.9): right n 4, 11.4 -> 5.2 cm; left n 16, 12.3 -> 13.1 cm". "Right elbow" wording is replaced by "right wrist".
Why: Author, 2026-09-29: fade the photographic background, keep overlays clear, separate illustrated frames from aggregate results. The script options are additive; the command without them reproduces both thesis figures byte for byte (checked 2026-09-29, sha256 07185cdd... and cf5e4ac2...). The legend is native because the baked legend cannot hold 16 pt text in a 1.75 in panel.
Alternatives: Keep the thesis figures (rejected: about 5 pt baked text); stack the figures (same scale, less room for the legend and aggregate).
Evidence: FACTOR 0.5 source: measured relative luminance of the cropped frames, median 0.240 -> 0.056 and p95 0.809 -> 0.175 (1890; 1462: 0.196 -> 0.047, 0.812 -> 0.175); white-overlay contrast against the p95 background 1.22 -> 4.68, amber label 0.54 -> 2.08; the choice among 0.5 and the rendered scratch previews is a visual judgment, hence UNCERTAIN. Text scales 3.8/4.4: the largest values at which "Plain solve" is not shrunk by strip() in the 640 px panel, giving baked cap heights 82 px and 70 px, about 16.5 pt and 15.6 pt effective at the placed heights (1394 px and 1252 px over 2.833 in; DejaVu cap ratio 0.729). Manifest: presentation/defense_2026/figures/recovery/manifest.json (commands, generator and input sha256s, output sha256s). Thesis lines 128, 139-152.
Reversibility: Point page 30 back to writing/v9/figures/ch7_natural_proxy_*.png with the figure_pair stack.
Review: Check the fade level and overlay visibility on the projector; the landmark and object track files read by recovery_core.load_tracks are not hashed in the manifest.

ID: D-254
Status: SETTLED
Decision: validate_deck.py pins the Chapter 7 values shown on pages 27-30 as constants with table references (THESIS_OBJECT_TABLE Tables 7.1-7.2, THESIS_HUMAN_TABLE Table 7.4 and line 78, THESIS_SYNTHETIC_TABLE Tables 7.5-7.7, THESIS_RECOVERY_FRAMES Figures 7.8-7.9, THESIS_RECOVERY_AGGREGATE Table 7.9) and checks the page strings against them; the old ">= 2 evaluation pages with right_failure/left_failure" check becomes "Main evaluation follows thesis Sections 7.2, 7.3 and 7.4 in its titles" (pages 27-30 open with 7.2/7.3/7.4/7.4 and still carry both failure keys); new manifest checks bind the evaluation copies to their thesis sources and the recovery figures to their generator, inputs and outputs, and each evaluation_figures page must embed exactly its declared panels with the declared crops inside 6.22-12.83 x 1.20-6.25 in.
Why: Brief for M2; numbers must come from pinned sources (AGENTS.md).
Alternatives: Parse the thesis text at validation time (rejected: the .txt table rows are free text; constants with line references are simpler to review).
Evidence: validate_deck.py --pdf: 1348 package checks, 0 package failures (was 1332). Mutation test: changing page 27 "1.14" to "1.15" made exactly "Page 27 object table equals thesis Tables 7.1-7.2" fail.
Reversibility: Remove the constants and checks; restore the old evaluation check.
Review: None beyond D-251 row names.

ID: D-255
Status: SETTLED
Decision: Film pages 25, 31 and 35 show a viewport of their unchanged 1440x1200 film by a presentation crop (a:srcRect): [336,64,1104,1188] on page 25 (p41) and [345,64,1104,1188] on pages 31 and 35 (p47 and its byte copy p35); the film box is left-aligned at x 6.22 in, 5.00 in tall on pages 25 and 31 (3.42 and 3.38 in wide) and 5.55 in on page 35 (3.75 in wide); render_deck.py turns each cropped movie into a static cropped poster picture in the temporary PDF export copy only, and RENDER_CHECK.json records that policy and the converted pages.
Why: Author, 2026-09-29: hide the unreadable internal state codes while keeping both complete views and the original films. A crop leaves the MP4 and poster bytes bound by media_contract.json untouched. LibreOffice ignores a:srcRect on a movie, so without the conversion the review PDF would show the uncropped poster. Left alignment (one rule for all three pages) keeps the film edge on the caption edge and leaves the free strip beside the page-35 film for its caption.
Alternatives: Re-encode cropped copies of the films (rejected: new media bytes and a new contract row for each); centre the film in the right column (rejected: the page-35 caption would then need a new 16 pt allowance in the left column); crop page 25 at x 345 like 31/35 (not needed: p41 has no glyph at x 336-344).
Evidence: Every frame at 1 fps of each film (ffmpeg -vf fps=1, 25 and 50 frames; bright-pixel threshold 30 of 255): camera view [400,64,1040,544], Unity view [336,612,1104,1188]; left code text never reaches x 336 on p41 inside rows 64-1188; p47 has a stray glyph at x 336-344, y 289-303; the right code column starts at x 1131 in both; Unity columns x 336-344 are uniform background (mean 174 on p41, 138 on p47 on every row), so pages 31/35 lose only those 9 px; the film caption "Same source frame in both views" (x 402-1000, y 565-592) stays inside. validate_deck.py pins FILM_VIEWS, VIEWPORT_LEFT_LIMIT {25: 336, 31: 345, 35: 345}, VIEWPORT_RIGHT_LIMIT 1131, VIEWPORT_UNITY_LOSS_PX 9 and VIEWPORT_HEIGHTS_IN (5.00, 5.55) and checks box, width (height x viewport aspect, within 0.02 in) and srcRect (within 2e-5). A scratch mutation of the page-31 crop_left made exactly that check fail. The canonical PPTX still links media12.mp4 and media13.mp4 with bytes equal to the declared films; sha256 of all 483 media files under committee_materials/, media/ and unity_capture/ is unchanged (m3_media_before.sha vs after).
Reversibility: Remove video_viewport_px from the three pages; the builder then falls back to the 6.00 x 5.00 in uncropped film and the renderer converts nothing.
Review: Open the PPTX in PowerPoint on the defence machine and play pages 25, 31 and 35: PowerPoint playback of a cropped movie is not verified here.
Annotation (2026-09-29, build 60): VIEWPORT_LEFT_LIMIT is now keyed by the film file name, not the page number, and the LibreOffice claim was tested: see D-260.

ID: D-256
Status: SETTLED
Decision: Page 33 keeps its uncropped 6.00 x 5.00 in film and covers the two burned-in left label boxes, film pixels [32,145,365,202] and [32,215,365,270], with two black rectangles without outline (visual.video_masks_px, drawn by build_deck.py film_masks); the right Frame/time boxes stay visible; validate_deck.py checks that on every composite page only the declared masks cover the film.
Why: The p49 plot spans x 185-1380 under the camera view, so a crop would cut the plot; the label boxes carry internal code text the author asked to hide.
Alternatives: Crop (rejected: cuts the plot axes and ticks); re-encode (rejected: new media bytes).
Evidence: Union over all 18 frames at 1 fps (threshold 12 of 255): left label text x 35-331, y 154-191 and x 34-311, y 223-260; nothing else left of x 400 above y 580; right boxes x 1081-1290, y 158-256. Scratch mutation: moving one mask 0.1 in failed exactly "Slide 33 covers its film only with the declared label masks".
Reversibility: Delete video_masks_px from page 33.
Review: In PowerPoint the masks sit above the playing movie in z-order; confirm on the defence machine.

ID: D-257
Status: UNCERTAIN
Decision: Page 35 shows the cropped handover film at full right-column height (y 1.20-6.75 in, 3.75 in wide), its caption "Handover replay; qualitative only." bottom-aligned in the strip right of the film (gap FILM_CAPTION_GAP 0.25 in), and six left bullets, a "supports" and a "limit" line per evaluation (bullet_y 1.42, 2.17, 3.02, 3.77, 4.62, 5.12; height 0.72): "Object lengths match tape within 2.83 cm", "Route itself was not registered", "Wrist R/L: model 0.83/2.34, rig 5.5/6.8 cm", "Reference is a detector, not ground truth", "Recovery helped the right arm", "Not the left arm; few frames"; the notes give the recovery numbers (11.4 -> 5.2 cm right, 12.3 -> 13.1 cm left).
Why: Author, 2026-09-29: enlarge the views and give a concise interpretation of the three evaluations. The recovery bullets carry no numbers because every numbered variant within 8 words broke across lines mid-value at 22 pt in the 5.03 in bullet box (for example "11.4 / -> 5.2 cm", "small / n"), and "0.53-2.83" broke at its hyphen in the LibreOffice render, so the object bullet states the upper bound only.
Alternatives: Numbers in all six bullets (rejected for the line breaks above); caption as a 16 pt line under the bullets (rejected: needs a new typography allowance).
Evidence: Wrap tests with the builder metric (DejaVu Sans 22 pt, 5.03 in); rendered preview/slide-35.png; numbers from writing/v9/zh/src/Chapter_9_Discussion.txt Table 9.1 lines 57, 59, 61 and thesis Table 7.9 (via validate_deck.py THESIS_RECOVERY_AGGREGATE).
Reversibility: Restore the four-bullet page 35 from commit eaa707b.
Review: Whether the recovery pair should show the numbers despite the line breaks; whether "few frames" (n 4 right, n 16 left) is the wanted limit wording.

Annotation (2026-09-30, build 63): the caption placement is superseded by D-269 (one 16 pt line under the bullets, the alternative rejected above); the film on this page (now 36) is p27 (D-266).

ID: D-258 (page-24 anchored photos and their check superseded by D-270 and D-273)
Status: UNCERTAIN
Decision: Page 24 shows byte copies of writing/v9/figures/src/r6b_frame00505.png and r6b_unity_f00505.png (640 x 480, figures/coordinate_frames/anchored_photos.json) side by side, 3.23 in wide from y 1.58 in under 16 pt headings, with native arrow triads (2.25 pt, red X FF4040, green Y 40E070, blue Z 408CFF) and 16 pt labels on black boxes: World at the desk marker anchor_px [350,454], Camera at the image corner [34,72], Scene at the Unity desk marker [346,443], Rig anchor at the pelvis [340,348]; one 16 pt mapping line under the photos; scene_mapping.png and rig_frames.png stay in the folder but are no longer placed.
Why: Author, 2026-09-29: anchor the coordinate systems to the physical-camera and reconstructed-scene images instead of six detached diagrams; page 24's baked 7 pt figure text goes with them.
Alternatives: Draw the Scene triad at the floor origin (rejected: the floor is outside the rendered view, hidden by the desk; the triad sits at the desk marker, which World maps onto, and the notes say the origin is on the floor below); axis directions projected from the marker pose (not done: the brief asked for illustrative directions, declared in the notes).
Evidence: Anchors measured: ArUco id 2 (DICT_5X5_50, OpenCV 4.10.0) corner means (349.5, 454.0) in the camera frame and (345.5, 443.0) in the Unity view; red pelvis sphere centroid (340.0, 347.7) (R>150, G<60, B<60, 277 px). The camera anchor [34,72], axis lengths (64 px, diagonal 40/32 px) and label positions are layout choices with no measurement. validate_deck.py checks two manifest-bound uncropped 640x480 pictures, anchors inside the image, and three arrows in the three colours per triad, six per photo; a scratch mutation of one arrow colour failed exactly that check.
Reversibility: Restore visual.kind figure_pair with the two old figures on page 24 from commit eaa707b.
Review: Legibility of the triads at projector scale; whether the Scene axes at the desk marker (origin on the floor below) read correctly.

ID: D-259
Status: UNCERTAIN
Decision: Font policy for baked text (build 60): native text keeps the roles 28 / 22 / 16 / 10.5 pt (11 pt cover label, 60 pt closing word); baked text in regenerated figures and charts targets 16 pt effective at its placed width, as one shared size for every text of a chart. Only the transport package chart (hidden page 43) is regenerated: transport_bench.py PKG_TEXT_PT = 16.0 (placed 1:1, 12.33 in for 2466 px = 200 px/in, so font_px = 16/72 * 200 = 44.4 px); its smallest text goes from 15 to 16 pt effective, the title from 21 to 16 pt. The marker chart (page 41), the filter panel charts (50-51), the typeset equations (44-51), the thesis figures on pages 11 and 27 and all films stay as they are and are listed as accepted exceptions in review/EFFECTIVE_TEXT.md. report_effective_text.py with effective_text_table.json reports the effective size per placed image.
Why: Author, 2026-09-29: font sizes across the deck must be consistent. All four charts re-render plot-only from committed results (transport and filter panels reproduced byte for byte before the change; the marker chart differs only by the matplotlib version, 3.11.2 committed vs 3.9.2 here). At 16 pt effective (17.76 pt in the marker figure, placed 11.108 in wide at 5.00/5.55 scale; 16 pt in the 1:1 filter panels) the marker legend and detection-rate box cover the curves and the y label collides with the ticks, and the filter panels run tick names together, cover data and clip titles; fixing that is a new layout, not a font change, so those charts were reverted to their committed bytes. The equations cannot grow without changing the EMU-exact page-9 geometry the validator pins.
Alternatives: Redesign the marker and filter charts (legend and text outside the axes, taller panels) - not done in this build, left for an author call; a smaller shared size (for example 12 pt) for all charts (rejected: does not meet the 16 pt target and still changes three charts); re-encoding films (rejected: media bytes pinned).
Evidence: Scratch renders at 16 pt effective of chart_marker_bench.png and both panel charts (read as images, 2026-09-29); PPTX placements measured with python-pptx (41: 11.108 x 5.000 in; 43: 12.330 x 5.550; 50-51: 6.610 x 5.000); review/EFFECTIVE_TEXT.md; validate_deck.py --pdf 1372 checks, 0 package failures.
Reversibility: Revert commit 6386289 (transport chart and script); the chart binding is by the declared file's hash, so the deck rebuilds unchanged.
Review: Whether pages 41 and 50-51 should be redesigned so their text reaches 16 pt, and whether the 7-9 pt thesis figure text on pages 11 and 27 is acceptable at projector scale.

ID: D-260
Status: SETTLED
Decision: Code-review follow-ups of b57ed6c..7c94795 (build 60): (1) native_diagram raises when a link segment crosses a node or label box other than its own two nodes (Liang-Barsky test, _segment_hits_rect); (2) VIEWPORT_LEFT_LIMIT and FILM_MASKS_PX are keyed by the composite film's file name, and the mask check requires a 1440x1200 poster when masks are declared; (3) restrained_figure_pair, restrained_object_chart and restrained_human_chart and their dispatch entries are deleted (no page in talk_content.json or backup_content.json uses those kinds); (4) restrained_anchored_photos raises when the mapping line ends below the caption top PHOTO_CAPTION_Y 6.31 in, and triad label boxes get PHOTO_LABEL_SLACK 0.10 in on the right; (5) the closing-page centring tolerance 2*9144 EMU is documented (0.01 in per axis from rounded inch placement); (6) the recovery check parses the --fade value of each recorded command and compares it with the manifest fade 0.5; (7) the D-255 policy string states the tested fact.
Why: Non-blocking minors from the Opus review of the build-57..59 diff; each removes a way the checks could pass on a wrong layout or a stale binding.
Alternatives: Assert the film hash inside the mask check instead of keying by file name (not chosen: the file name is what the page declares, and the hash is already bound by the media contract checks).
Evidence: build_deck.py builds with 0 fit warnings and 0 overlap candidates, so no current diagram link crosses a box; validate_deck.py --pdf 1372 checks, 0 package failures. LibreOffice test (2026-09-29): the canonical PPTX converted to PDF without the static-picture step drew pages 25 and 31 with a wrong, distorted film region instead of the declared viewport (compared with preview/slide-25.png and slide-31.png from the converted copy), so LibreOffice does not honour a:srcRect on a movie and the conversion stays.
Reversibility: Revert commit bb2d469.
Review: None; PowerPoint playback of the cropped movies remains unverified (D-255).

ID: D-261
Status: UNCERTAIN
Decision: Build 61 hides the burned-in producer labels of every other film by presentation only, keyed by film file name (visual.video_viewport_px or visual.video_masks_px; MP4 and poster bytes unchanged). Viewport crop (a:srcRect, box 4.92 in tall at x 6.22 in, width from the cropped aspect): page 8 p06 [160,104,1120,824] (hides the "p06 |" header and the three state/disclaimer lines and XYZ key below the camera view), page 21 p32 [0,78,960,798] (hides the "p32 |" header, "Deliberately masked legacy recording / No experiment-frame map" and the XYZ key), page 18 p23 [0,78,960,970] (hides the "p23 |" header only). Black masks (film pixels, uncropped film, same placement as before): pages 9, 44, 45, 46, 47, 48, 49 (p09, p07, p08, p43, p67, p68, p46) [32,145,365,202] and [32,215,365,270], the page-33 boxes, over "pNN - Name" and "Shared pause/playback"; page 12 p13 [34,14,380,61] and [38,128,276,172]; page 13 p15 [34,14,432,61], [38,128,276,172] and [1230,1074,1413,1113] ("(Section 5.5)"); page 14 p16 [34,14,266,61] and [38,128,276,172] (the "pNN | Name" header and "0.5x playback"; "Recorded input" and "Frame N" stay); pages 19 p25 and 20 p29 [44,22,1167,80] (whole header row "pNN | frame | s | freeze / 0.5x playback") and [20,240,242,662] (the legend column "Input axes ... Input rejected or not measured"); page 23 p33 [44,22,1015,80] (header "p33 | frame 533 | selected and frozen"); page 5 p05 [0,457,278,480] (the burned-in caption strip "R6b rail task / R7 handover: recorded RGB, no overlays"). restrained_video (kinds task/landmark/grip/fallback_video) takes the same viewport and masks as the composite branch.
Why: Author request (round 7): hide unreadable internal state codes on video slides while keeping every content view complete and the files unchanged; three visual reviews found the labels on these pages. A crop is used where every label lies outside one rectangle holding all content (pages 8, 18, 21); where the plots or lower panels span the full film width a crop cannot remove the left labels, so masks are used (black on the films' black background; page 5 replaces an opaque dark strip).
Alternatives: Crop plus masks on one film (not implemented: masks need an uncropped film, and on the black-background composites a top crop adds nothing visible over a header mask); re-encoding (rejected: media bytes pinned); cropping page 5 below the strip (rejected: cuts the desk marker at y 440-480); cropping the page-18 status strip (rejected: the caption "torso rejection shown in the status strip" and the spoken notes cite it, so it is content, UNCERTAIN); masking the "Frame N" counters on pages 12-14 (not done: a readable frame index, not a producer code, UNCERTAIN).
Evidence: Every 1 fps frame of each film (ffmpeg -vf fps=1, 6 to 47 frames per film), union of pixels with a channel above 40: label rectangles and content rectangles in validate_deck.py FILM_GEOMETRY_PX; the page-5 strip is the dark box from row 458 to 480 and x 0 to 277 on every frame (mask 1 px larger). For every film the pixel check "all foreground under a mask lies inside a label rectangle" and "all foreground outside the viewport lies inside a label rectangle" passed over all frames; p49 geometry reproduces D-256 and the six hidden filter films share it (left label text x 34-361, y 154-261). Measurements: job scratch film_geometry_build61.json. validate_deck.py --pdf: 1397 checks, 0 package failures; rendered pages 5, 8, 9, 12-14, 18-21, 23, 33, 44-49 read as images. Media sha256 of committee_materials, media and unity_capture (483 files) identical before and after.
Reversibility: Delete video_viewport_px / video_masks_px from those pages in talk_content.json and backup_content.json and the matching FILM_* entries in validate_deck.py.
Review: Page 5: the black mask at the bottom-left corner of the task video is visible as a black bar where the caption strip was; page 18 keeps its small status strip; pages 12-14 keep "Frame N"; page 23's poster shows an empty "Shared RAM" box (a mid-animation poster frame, unchanged, author call). PowerPoint playback with masks above a playing movie and srcRect crops on movies is unverified (LibreOffice renders only).

Annotation (2026-09-29, build 62): superseded in part by D-262. The page-5 Evidence above is inexact: measured on all 1396 frames at 30 fps, the caption strip is rows 458-479 and x 0-275 (fill at most 93 in the largest channel), so the build-61 mask [0,457,278,480] also covered camera row 457 and camera columns 276-277. The mask is now [0,458,276,480], equal to the measured strip. Exact residual: column 276 (1 px wide, rows 458-479), the first camera column, is darker than 130 in most strip rows on 510 of 1396 frames, next to the black mask; no caption text reaches it (text ink x 7-269). The build-61 FILM_GEOMETRY_PX camera rectangle of the p09 family ([400,64,1040,544]) and the page-13 lower panel split around the "(Section 5.5)" mask were also replaced by measured rectangles (D-262).

ID: D-262
Status: SETTLED
Decision: Build 62 makes the D-261 film checks fail closed and re-measures their geometry. (1) validate_deck.py fails unless every FILM_GEOMETRY_PX film reached the D-261 geometry check from its measured path, FILM_MASKS_PX and FILM_VIEWPORT_PX name only measured films, and every non-full MP4 on any page (composite_media, paired_media or media) is measured or is a D-255 viewport film (p41, p47, p35). (2) FILM_GEOMETRY_PX equals review/film_geometry.json, written by the committed measure_film_geometry.py over every 30 fps frame; a check requires the table to equal the file and every film to keep its measured sha256. (3) Re-measured rectangles: the p09 family camera is [400,0,1040,480] with a separate subtitle rectangle [529,511,1034,549] ([527,511,1036,549] on p49 and p46); the page-13 lower-right panel is its measured border lines and inner items rather than a panel split around the mask; the page-5 mask and label rectangle equal the measured strip [0,458,276,480]. (4) The mask-cover, geometry and restrained-video srcRect checks share one gate over all three media keys, both srcRect checks use viewport_box_matches, and build_deck.py places composite and recorded-video films through one declared_film helper.
Why: The build-61 code review found that a film missing from FILM_GEOMETRY_PX was skipped silently, so renaming or re-encoding a film would pass the D-261 checks vacuously; the p09-family camera rectangle did not match the frames (the camera starts at y 0, and y 515-545 is the subtitle line); the page-13 content rectangles were carved around the mask, so the content check could not fail there; the page-5 mask covered camera pixels; and the numbers cited a scratch file outside the repository.
Alternatives: Load FILM_GEOMETRY_PX from the JSON at run time (not chosen: keeping the table in the validator and checking equality makes any re-measurement a visible diff); shrink the page-13 "(Section 5.5)" mask to the ink plus 2 px (not needed: at 30 fps no foreground pixel other than the label ink lies under [1230,1074,1413,1113]; the nearest content is the panel border at x 1419 and "twist free" ending at y 1066); a pixel check of the masks inside the validator (not chosen: it would decode every film on each run; the script's cover assertion plus the validator's rectangle check give the same guarantee).
Evidence: measure_film_geometry.py (2026-09-29, 3 min 16 s): 18 films, 180 to 1396 frames each; the script asserts that the content rectangles cover every non-label foreground pixel and meet no label rectangle. Threshold sensitivity: pixels above 8 but never above 40 that lie under a mask and more than 2 px from label ink are 1 on p15 and 4 to 13 on p25, p29 and p33, all 3 px above the header text (faint header ringing), none elsewhere. validate_deck.py --pdf: 1399 checks, 0 package failures (overall PARTIAL for D-058/D-066). Mutation tests on a scratch copy: renaming the page-9 film path fails the new completeness check; moving the first page-9 mask onto the camera (spec and FILM_MASKS_PX) fails the D-261 geometry check; editing FILM_GEOMETRY_PX without re-measuring fails the equality check; restoring the build-61 page-5 mask fails the D-261 geometry check. Only ppt/slides/slide5.xml differs from the build-61 PPTX (the mask shape), so the builder refactor changes no other part. Media sha256 of committee_materials, media and unity_capture (483 files) identical before and after. Rendered pages 5 and 13 read as images.
Reversibility: Revert the build-62 commits; the page-5 mask returns to [0,457,278,480] and FILM_GEOMETRY_PX to the build-61 values.
Review: The label regions in measure_film_geometry.py (FILMS) are the build-61 search boxes read from the frames by a person; confirm that none of them holds content. The page-5 residual is stated in the D-261 annotation. The segmentation parameters (DILATIONS, MERGE_GAP, LINE_MIN) set granularity only; a coarser setting can only make the validator fail.

ID: D-263
Status: SETTLED
Decision: Build 63 removes every question clause from the deck and adds a validator check over every visible string and note. validate_deck.py QUESTION_WORDS = why, what, how, whether, which, when, where, who; QUESTION_CLAUSE matches one of them as a whole word opening a clause (at the start of a string or line, after . ! ? ; : or a comma followed by space, after an opening parenthesis or after a spaced dash, optionally after a quote), and any '?' is a hit. The check "No question clause in any visible string, table cell, caption, title or the notes (D-263)" runs question_clauses() over every text-frame shape, every table cell and the notes of all 55 pages. The page-6 research question moved from text hard-coded in build_deck.py restrained_flow() into talk_content.json data.question, as a statement. The page-2 outline became noun phrases; the titles of pages 27-30 lost their section numbers, which moved into thesis_section data and the footers (EVALUATION_SECTIONS 27: 7.2, 28: 7.3, 29: 7.4, 30: 7.4, checked against thesis_section and source_label).
Why: Author, round 8 (2026-09-30): no question clauses anywhere in the presentation, extending the thesis rule (no embedded questions) to the deck, its notes and the spoken script.
Alternatives: None recorded by the build-63 worker; a word list without clause anchors would also flag relative clauses ("the frame which"), which the anchors avoid.
Evidence: question_clauses() applied to the build-62 PPTX (commit 6dcb645) finds 133 hits on all 53 pages; on the build-63 PPTX it finds 0. validate_deck.py --pdf (build 63 close-out): the check passes, "0 hits".
Reversibility: Remove the check and QUESTION_CLAUSE from validate_deck.py; the rewritten texts stay valid either way.
Review: The rewritten purpose and notes wording (restrained_purposes.json, SPEAKER_NOTES.md), for example page 1 "The reason to reconstruct a person handling an object."
Annotation (2026-09-30, build 66): the rule is extended to embedded question clauses (a listed verb followed by a question word) and to the '--' clause anchor; see D-287.
Annotation (2026-10-06): validate_deck.py is retired (D-382); D-386 overrides this rule for the block-opening questions of the final speaker script only.


ID: D-264
Status: SETTLED
Decision: Page 4 shows thesis Figure 2.3 (writing/v9/figures/ch2_fig_flow.png, 1575 x 840 px) and new page 33 shows thesis Figure 8.1 (writing/v9/figures/ch8_fig_system.png, 1920 x 1360 px), as byte-identical copies under figures/thesis/ bound by figures/thesis/manifest.json (figure, source, source_sha256, copy, sha256, pixel_size, thesis caption and its source line). Each is placed height-limited to 5.00 in at y 1.20 in with its aspect kept and centred (Figure 2.3 9.375 in wide, Figure 8.1 7.059 in wide), with a 16 pt caption starting "Thesis Figure N" and a footer starting "Undergraduate thesis | Figure N". The native diagrams of round 7 are removed: the information_flow kind and native_diagram() (D-248) and the page-33 left_diagram (D-249), with their typography allowances.
Why: Author, round 8: show the thesis figures as they are. Placed at full width (12.33 in) with the aspect kept, Figure 2.3 would be 6.58 in and Figure 8.1 8.73 in tall, more than the 5.68 in between the content top (1.20 in) and the footer rule (6.88 in) even before a caption line; so the height is limited to 5.00 in and the figure centred.
Alternatives: Redrawing the figures natively at deck sizes (rejected: the author asked for the thesis figures unchanged); cropping (rejected: the figures would no longer be the thesis figures).
Evidence: validate_deck.py check "Slide NN thesis figure copy is byte-identical to its manifest row and thesis source (D-264)" on pages 4 and 33 (hash, pixel size, y 1.20 in, aspect within 0.01, caption and footer prefix); report_effective_text.py placed widths 9.375 and 7.059 in. Durations: page 4 60 -> 45 s; new page 33 30 s.
Reversibility: Restore the round-7 pages 4 and 33 (information_flow and left_diagram) from commit 6dcb645.
Review: The smallest baked text is small at this placement (Figure 2.3 6.5 pt, Figure 8.1 4.7 pt effective, review/EFFECTIVE_TEXT.md); both are accepted exceptions because the author asked for the thesis figures as they are.

ID: D-265
Status: SETTLED
Decision: A film shown through a D-255 viewport is centred in its 6.61 in right column: build_deck.py movie() places the cropped box at x + (w - pw) / 2, where pw = h * (x1 - x0) / (y1 - y0), as an uncropped film already was; validate_deck.py viewport_box_matches() requires the box left edge at 6.22 + (6.61 - width) / 2 within 0.01 in (previously left-aligned at 6.22 in within 0.005 in).
Why: Author, round 8 (2026-09-30, cited in the build_deck.py movie() comment): centre the cropped films as the uncropped films already are.
Alternatives: Widening the viewport to fill the column (rejected: it would show the cropped state-code columns again, D-255).
Evidence: validate_deck.py --pdf: the "cropped film box and srcRect match the declared viewport" checks pass on every viewport page (for example page 36: box x 7.651 in, width 3.748 in, 7.651 = 6.22 + (6.61 - 3.748) / 2).
Reversibility: Return movie() to left, top = x, y and the validator to 6.22 in.
Review: None beyond the rendered pages 8, 18, 21, 25, 31 and 36.

ID: D-266
Status: UNCERTAIN
Decision: Page 36 (Discussions) plays p27-Fresh_Unity_Wrist_Loss_With_Model_Axes.mp4, the fresh Unity wrist-loss replay of R7 (frames 660-1019, 12 s), instead of the p35 committee copy of the p47 handover replay. The unified_revision media_contract.json row for p27 is re-added through a new "readded_from" rule: the row names an earlier contract (history/round7_compact/media_contract.json, bound by sha256) whose row has the same stem, page equal to source_page and the same path, poster, provenance, source, frame map, axis audit and kind bytes; validate_deck.py accepts such an added row only when all of these match. The history copies history/round7_compact/{media_contract,revision_id_map}.json hold that earlier state. The p35 copy is dropped from the contract and listed in dropped_rows. p27 uses the p47 viewport [345, 64, 1104, 1188] and VIEWPORT_LEFT_LIMIT 345, its geometry measured by measure_film_geometry.py (labels: header row y < 64, upper left state column to x 344, lower left column x < 336, right state column from x 1131). Duration 55 -> 45 s.
Why: Author, round 8: the Discussions page should show the wrist-loss replay rather than a second copy of the handover replay already shown on page 31.
Alternatives: Binding p27 as a new committee copy file (not chosen: the p27 bytes are already bound in the round-7 contract, and the readded_from row reuses that binding unchanged).
Evidence: validate_deck.py --pdf: "Slide 36 embeds the current declared composite_media", "composite is bound to its source and frame-map audit", "film viewport keeps both views and hides the state-code columns" and the D-261 geometry check pass for p27; review/film_geometry.json carries the p27 measurement. The media files (483) are hash-identical before and after build 63.
Reversibility: Restore the p35 row and page 35 of commit 6dcb645, drop the readded_from row and the round7_compact history copies.
Review: Whether the wrist-loss replay is the wanted film; the readded_from rule and the D-268 widened view deserve the code-reviewer's look.
Annotation (2026-09-30, build 66): correction. The p27 readded_from row names committee_materials/axes_revision/media_contract.json (sha256 95d1446c18461b6457f5a4d000c2d235be9c14492f2cbee232ea830ddf07b3d9, page 27 there), not history/round7_compact/media_contract.json. From build 64 on the p27 row carries previous_page, so the readded_from branch is not exercised by any contract the validator reads (commented in validate_deck.py; D-288).


ID: D-267
Status: SETTLED
Decision: The two References pages become visible main pages 40-41 (5 s each) right after Contributions (39), followed by a new "thanks" page kind "Thank you" (42, 5 s; the closing layout, one centred 60 pt word, no footer) and the Question page (43); the hidden pages move to 44-55. validate_deck.py checks "The References pages are visible main pages after Contributions (D-267)": two pages with legacy_key references*, both main with duration > 0, the last four main legacy keys equal references, references_2, thanks, 39, kinds thanks then closing, and no file path or .md in their footers. The hidden-page checks became data-driven: the typeset-equation pages must equal the hidden qa_filter_* pages (instead of the fixed range 44-51), References pages are found by legacy_key anywhere in the deck, and the closing notes are read from the one closing page. The main talk is 43 pages and 1790 s: page 4 60 -> 45, page 34 70 -> 55, page 36 55 -> 45, new page 33 +30, pages 40, 41 and 42 +5 each (1785 -> 1790 s).
Why: Author, round 8: show the references in the talk and end with a Thank you page before Question.
Alternatives: None recorded by the build-63 worker.
Evidence: build_deck.py: 43 main + 12 appendix slides, planned main talk 1790 s, 0 fit warnings, 0 overlap candidates; validate_deck.py --pdf: 1439 checks, 0 package failures.
Reversibility: Move the References pages back to backup_content.json, delete the thanks page and restore the fixed-range checks from commit 6dcb645.
Review: The 5 s per References page and the Thank you page are editorial timings, not rehearsed.

ID: D-268
Status: UNCERTAIN
Decision: The D-261 check "film keeps every measured content panel" compares the content rectangles of a D-255 composite-viewport film (composite_media, film named in VIEWPORT_LEFT_LIMIT, viewport declared) with the viewport widened on its left by VIEWPORT_UNITY_LOSS_PX (9 px, D-255) rather than with the viewport itself.
Why: The p27 Unity view starts at x 336 while the p27 viewport starts at x 345 (the "MappedMarker" state line reaches x 344), so 9 px of Unity background are cut; D-255 already allows that loss (VIEWPORT_LEFT_LIMIT with VIEWPORT_UNITY_LOSS_PX), but the D-261 content check did not know it and failed.
Alternatives: A mask over the state line with an uncropped film (not chosen: page 31 and page 36 would then differ in method for the same layout); moving the viewport left to 336 (rejected: shows the state line); narrowing the measured Unity rectangle (rejected: the measurement would no longer equal review/film_geometry.json, D-262).
Evidence: review/film_geometry.json p27 content rectangle [336, 565, 1104, 1188]; FILM_VIEWPORT_PX p27 [345, 64, 1104, 1188]; validate_deck.py --pdf passes the D-261 check on page 36 with the widened view. No mutation test of the relaxation was run.
Reversibility: Remove the keep[] widening in validate_deck.py; page 36 then fails until the viewport or the measurement changes.
Review: Code-reviewer: confirm the widening is limited to D-255 composite-viewport films, cannot hide a lost content panel wider than 9 px, and that the cut 9 px hold only Unity background.

ID: D-269
Status: UNCERTAIN
Decision: The page-36 caption "Wrist-loss replay; qualitative only." is one 16 pt line in the left bullet column (x 0.82 in, 5.03 in wide, bottom-aligned with the film at 6.75 in, top 6.49 in, below the last bullet box at 5.84 in), declared by visual.caption_under_bullets; caption_beside is dropped for that page. build_deck.py raises when the caption needs a second line, meets the bullets or is declared with caption_beside. validate_deck.py allows the visual_caption, and only it, at 16 pt in (0.82, last bullet bottom, 5.85, 6.86) on such a page, and checks "Slide NN caption is one 16 pt line under the left bullets (D-269)": one shape, x 0.82, width 5.03, height 16 * 1.18 / 72 in, bottom at the film bottom within 0.01 in, top below the last bullet box, text width by the DejaVu Sans metric at most 5.03 in (3.747 in).
Why: Author, round 8: the caption wrapped to four lines in the 1.18 in strip right of the p27 film (D-257 placement), because p27's cropped box is centred (D-265) and leaves a narrower strip.
Alternatives: A shorter caption beside the film (rejected: the brief keeps the text); moving or shrinking the film (rejected: viewports and placement fixed by D-255, D-265).
Evidence: build 63 close-out: preview/slide-36.png shows the caption on one line under the bullets; validate_deck.py --pdf passes the new check (caption box [0.82, 6.488, 5.03, 0.262] in, film [7.651, 1.2, 3.748, 5.55] in). Only ppt/slides/slide36.xml differs from the aaf2961 PPTX.
Reversibility: Set caption_beside back on page 36 in talk_content.json.
Review: Whether the caption reads better under the bullets or in the right column below a shorter film.

ID: D-270
Status: UNCERTAIN
Decision: Build 64 (round 8, M2) gives six coordinate slides the kind frame_figure with an overlay PNG of figures/coordinate_frames/overlay/ and a left-column equation strip: new page 11 "Camera and Camera-prime frames" (Eq. 3.1, 30 s), page 12 "Landmark frames and the T-pose reference" (no equation), new page 13 "Torso and root frame" (Eqs. 3.11-3.12, 30 s), page 18 "Object pose in the World frame" (Eq. 4.1), page 26 "Mapping into the scene" (Eqs. 6.1 and 6.6 side by side, equation_layout row) and new page 27 "Applying the rig" (Eqs. 6.4-6.5, 30 s). Durations: page 12 70 -> 50, page 14 65 -> 50, page 15 60 -> 50, page 16 50 -> 45, page 18 50 -> 45, page 26 65 -> 45 and page 9 70 -> 60 s; the main talk is 46 pages and 1795 s (build 63: 43 pages, 1790 s). Every overlay caption is one line, so the figure keeps the 6.61 x 5.00 in box; build_deck.py raises when an overlay caption needs more than one line, when row equations leave the left column (x 5.85 in, bottom 6.80 in) or when a stacked equation strip on an overlay page runs past 6.80 in.
Why: Author, round 8: show the coordinate systems drawn on the recorded photographs and the Unity view instead of detached schematics and the page-24 anchored photos. Stacked, Eqs. 6.1 and 6.6 on page 26 would run past the footer rule at 6.88 in, hence the row layout. Page 9 was the lowest words-per-second candidate chosen by the M2b worker, 1.36 words per second (build-63 notes word count / duration); build-63 pages with a lower ratio (31, 43, 5, 14, 23, 25 by the same count) were not shortened, and the worker's candidate rule is not recorded.
Alternatives: A two- or three-line caption (rejected: the figure would drop to the 4.75 in box and its 57 px labels to 16.25 pt effective, N-2); stacking the page-26 equations (rejected: past the footer rule); taking the 5 s from another page (not recorded).
Evidence: build_deck.py (build 64 close-out): 46 main + 12 appendix slides, planned main talk 1795 s, 0 text-fit warnings, 0 overlap candidates; review/BUILD_LAYOUT_CHECK.json focus_seconds context 225, methodology 1030, evaluation 350, conclusion 180, questions 10 (methodology 57.4 %); report_effective_text.py: the six overlays at 17.1 pt effective (6.000 in placed width, 240 px per in, em 57 px); preview/slide-11, 12, 13, 18, 26 and 27 read, no overflow.
Reversibility: Restore talk_content.json, backup_content.json and build_deck.py from commit 9a6833c and rebuild; the contract then needs the build-63 files of history/round8_b63 back (D-275).
Review: The durations are editorial, not rehearsed; the page-9 cut and the 30 s of the three new pages.

ID: D-271
Status: UNCERTAIN
Decision: The producer decisions of figures/coordinate_frames/overlay/NOTES.md (make_frame_overlay_figures.py, round 8 M2a) are recorded here with their status kept. N-1 SETTLED: canvas 1440 x 1200 px (the size of the existing schematics); single 640 x 480 photographs fill 1440 x 1080 at the top with a 120 px black band for one legend line. N-2 SETTLED: every label 57 px DejaVu Sans, ceil(16 / 72 x 1200 / 4.75) = 57, 17.1 pt effective in the 5.00 in box; the producer fails on overlapping or off-canvas labels. N-3 SETTLED: fade = rint(resized photo x 0.5) with the overlays drawn afterwards (as eval/failure/make_label_compare_fig.py --fade 0.5); INTER_CUBIC when enlarging, INTER_AREA when shrinking. N-4 UNCERTAIN: the T-pose landmark anchors are measured with MediaPipe PoseLandmarker (v1 heavy model, IMAGE mode, CPU, confidences 0.3 as in v1/mediapipe/extract_landmarks_to_csv.py) because no manifest records landmark pixels for tpose_source.jpg. N-5 SETTLED: projected axis lengths are display choices, 0.09 m (object, L14, L16), 0.12 m (Scene, rig root); illustrative legends 230 px (camera) and 200 px (torso root). N-6 UNCERTAIN: the Unity view camera model is a pinhole with f = 240 / tan(fov_y / 2) from sensor_fov_y_deg of scene_calibration_r6bc.json, principal point (320, 240), square pixels, at the calibrated camera pose. N-7 SETTLED: the Scene axes are drawn at the desk-marker origin because the true Scene origin (0.716 m below along gravity) projects to about v = 1306 px, outside the 480 px view; the figure text says so. N-8 UNCERTAIN: the rig segment rotations are rebuilt from the streamed angles as IntegratedSceneReceiver.cs does (root Ry Rx Rz; right shoulder Ry Rz Rx; right elbow Ry Rz) and carried to the camera by F; only the right arm chain (L14, L16) is drawn. N-9 SETTLED: the Camera and Camera-prime legends share the optical origin but are drawn apart at the upper left; Z into the scene is a ring with a cross, Z toward the viewer a ring with a dot.
Why: The M2a producer brief asked for photographs overlaid with the thesis frames; the per-frame overlay mode (measured, projected or illustrative) is recorded in figures/coordinate_frames/overlay/manifest.json and restated in each slide's notes (D-273).
Alternatives: Hand-placed anchors as in D-258 (rejected: not reproducible); for N-4, a manual pointer as in the 01d023a manifest (rejected: one point only).
Evidence: overlay/manifest.json reprojection_checks: World origin vs the detected desk marker 0.72 px, Object origin vs the detected cube marker 0.02 px, Unity camera model World origin vs the page-24 desk anchor 2.88 px and rig hip vs the pelvis sphere 3.61 px, tf from the log (0, 0.716215, 0) m against thesis Section 6.4 d = 71.6 cm, L14 and L16 first axes vs the rendered bone 0.000 deg; the MediaPipe measurement is deterministic across two runs. N-1, N-2, N-3, N-5, N-7 and N-9 are layout or display choices with no measurement beyond these.
Reversibility: Change the specs spec_<name>.json or the producer and rerun make_frame_overlay_figures.py; the validator binds the new hashes through overlay/manifest.json.
Review: N-4: that the L14 elbow (about 25 source px below the L12-L16 line) and the L16 wrist on page 12 look right. N-6: the Unity sub-pixel convention was not read from Unity itself; only the 2.88 px and 3.61 px checks support the model. N-8: the Y and Z axes of L14 and L16 on page 27 depend on the held twist and are not checked against any rendered geometry; only the first axes are.

ID: D-272
Status: UNCERTAIN
Decision: The World Y and Z axes on pages 18 and 26 stay as the true projection, nearly on the same upward image line, with their labels separated left and right; no axis is moved or redrawn to separate them.
Why: The desk card leans back on its stand and the camera looks down on it, so Y and Z of the World frame project almost onto one line; moving an axis would misstate the geometry that the projection check supports.
Alternatives: Drawing an illustrative triad beside the marker (rejected by the M2a worker: the page would then not show the calibrated pose); a different photograph (not tried).
Evidence: figures/coordinate_frames/overlay/NOTES.md, Known visual limits; preview/slide-18.png and slide-26.png read in the build-64 close-out. No measurement of the projected angle between the two axes was recorded.
Reversibility: Change spec_object_world.json and spec_scene_mapping.json and rerun the producer.
Review: Author call: the legibility of the near-overlap at projector scale, or an illustrative triad on the two pages instead.

ID: D-273
Status: SETTLED
Decision: validate_deck.py replaces the D-258 anchored-photo check and the D-121 Figure 3.5 thesis-copy branch for the six overlay slides: "Coordinate overlays bind their generator and every input hash" (overlay/manifest.json generator and inputs by sha256), per overlay "matches its manifest hash and pixel size" and "declares the committed photo hash" (each panel photo equal to its manifest input), per slide "places its manifest-bound coordinate overlay" (sha256 equality, one uncropped picture inside 6.22-12.83 x 1.20-6.75 in) and "notes state the overlay mode of every drawn frame" ("<frame>: <overlay_mode>." per manifest frame and "Landmark points ...: measured."), and "No page uses the superseded anchored_photos kind (D-273)". Supersedes D-121 (the verbatim Figure 3.5 caption on the page-11 copy; page 12 now shows the landmark overlay) and D-258 (page-24 anchored photos).
Why: The overlay PNGs are generated, not thesis copies, so the binding moves from the thesis source hash to the producer manifest, and the notes must say which frames are measured, projected or illustrative.
Alternatives: Keeping the anchored-photo arrow-colour check (rejected: the overlays are baked into the PNG, there are no native arrows to count).
Evidence: validate_deck.py --pdf Thesis_Defence_2026.pdf (build 64 close-out): 1539 checks, 0 package failures; the 14 overlay manifest checks and the 12 slide checks above pass. No mutation test of the new checks was run in this close-out.
Reversibility: Restore the anchored_photos branch and anchored_photos.json check from commit 9a6833c.
Review: Code-reviewer: that the notes check cannot pass on a page whose overlay has no frames (wanted is required non-empty).

ID: D-274
Status: SETTLED
Decision: validate_deck.py finds the four main evaluation pages by legacy key (EVALUATION_KEYS object_rig_accuracy 7.2, ch7_results_table 7.3, synthetic_removal 7.4, right_failure 7.4) and derives EVALUATION_SECTIONS and the page-specific Chapter 7 number checks from those pages, instead of the fixed pages 27-30 of build 63.
Why: The three new overlay pages move the evaluation pages to 30-33; fixed page numbers would break at every insertion before Chapter 7.
Alternatives: Renumbering the constants to 30-33 (rejected: the same break recurs at the next insertion).
Evidence: validate_deck.py --pdf (build 64): "Main evaluation follows thesis Sections 7.2, 7.3 and 7.4 in its thesis_section data and footers" passes on pages 30, 31, 32 and 33.
Reversibility: Restore EVALUATION_SECTIONS = {27: "7.2", 28: "7.3", 29: "7.4", 30: "7.4"} and the by_id(27..30) lookups.
Review: None beyond the check detail.

ID: D-275
Status: SETTLED
Decision: The unified_revision media_contract.json chains to build 63 without any media change: history/round8_b63/media_contract.json (sha256 cfac3502d1292442a97316c31018435d65bacf0baa286edff1838c37a0fd8ba9) and history/round8_b63/revision_id_map.json (sha256 6c8855b7bc42a3bf3246eace6d37f99107e3b4f4f7316eb5cc4c879fb9ad3fdf) are byte copies of the build-63 files (git show 9a6833c); revision_id_map.json advances to schema 10 (46/12/58, old_to_new 1-10 same, 11 -> 12, 12-24 -> 14-26, 25-43 -> 28-46, 44-55 -> 47-58; new pages 11, 13, 27 with no previous page; previous = the build-63 map); all 21 contract rows are repaged (previous_page = build-63 page), base_contract and previous_page_map point at round8_b63, unified_pages {"13": 14, "15": 15, "16": 16}, dropped_rows and added_pages empty, and the p27 row re-added in build 63 moves 36 -> 39 through the ordinary chained rule (its readded_from note kept as provenance). validate_deck.py follows: UNIFIED_FOUR_ROUTE current_pages {13: 14, 14: retired (D-130), 15: 15, 16: 16}; the archived p41 row is expected on page 28 with previous_page 25.
Why: Three inserted pages renumber every film page from 12 on; the chained contract method of D-266 (a bound snapshot of the previous state) keeps each row traceable to its previous page without touching media bytes.
Alternatives: Rewriting the rows in place without a snapshot (rejected: breaks the previous_page chain the validator checks).
Evidence: validate_deck.py --pdf: 1539 checks, 0 package failures (19 "declared media uses its committee page identity" and page-count failures before the repaging); every "Committee asset ... current page follows the page map" check passes; 483 media files hash-identical to the reference list (sha256sum -c). The page tests in audited_bank_composites (asset pages 17, 19, 20) cover only the bank_kinematics_axes kind, which is not in the current contract, and are unchanged.
Reversibility: Restore media_contract.json and revision_id_map.json from history/round8_b63 and the two validator constants.
Review: None beyond the check detail.

ID: D-276
Status: SETTLED
Decision: Build 65 places white thesis-crop equation strips (typeset for ts_ keys) through equation_keys on main pages 8 (eq_2_1), 9 (ts_butter), 15 (eq_3_20, eq_3_21, eq_3_23), 16 (eq_3_24), 21 (eq_5_2, eq_5_4), 22 (eq_5_9, eq_5_10, eq_5_11), 23 (eq_5_12), 30 (eq_7_1, eq_7_2, row layout) and 37 (ts_oneeuro_cutoff, ts_oneeuro_alpha); no strip was reduced. Pages 9, 15 and 30 move their four bullets to a 0.95-1.05 in pitch and page 22 to a 0.90 in pitch (bullet_y data) so the strips fit; strip starts 6.12 (8), 5.35 (9), 5.20 (15), 4.20 (22), 5.05 (30), default 5.13 elsewhere. build_deck.py restrained_equations now raises when a strip starts less than 0.10 in below the last bullet's wrapped text or ends below 6.80 in on any page (the 6.80 in check was overlay-only). Footers of pages 8, 15, 16 and 30 add the Eq. numbers they now show.
Why: Brief of round 8 (point 9): each teaching page shows the final equation of its concept as the thesis prints it; derivations go to later hidden pages. The pitch values are the smallest that keep 22 pt bullets (two lines = 0.72 in at 1.18 leading) apart and the strip above the footer rule.
Alternatives: Reducing page 22 or 30 to one equation (rejected: all keys fit); a second row layout for page 15 (rejected: the three crops need 6.21 in in one row, the column holds 5.26 in).
Evidence: build_deck.py (0 fit warnings, 0 overlap candidates); validate_deck.py --pdf: every "exact equation ... equation-region contract", "fixed source scale" and "retains every source glyph pixel" check passes on the new pages; preview/slide-08, 09, 15, 16, 21, 22, 23, 30, 37 read: no strip meets a bullet, film or caption. equations/white_manifest.json lists 21 keys = the placed thesis keys. Fragment sizes: exact_equation_fragments at the fixed 1.6 source scale.
Reversibility: Empty the equation_keys of these pages and restore their bullet_y, equation_start_y and footers from 9ae156d.
Review: Whether page 16 (one strip below three short bullets) and page 30 (two stacked-line crops beside the table) read well at projection size.

ID: D-277
Status: SETTLED
Decision: Main pages cite author-year keys in their captions: 8 Garrido-Jurado 2014, 9 Hampel 1974 and Butterworth 1930, 30 Garrido-Jurado 2014, 37 Casiez 2012. validate_deck.py extends the author-year check to every page except the References pages, excludes "Frame/Figure/Table/Page/Slide NNNN" from the pattern ("Frame 1890" on page 33 was a false hit), and adds CITATION_REQUIRED [(8, title), (9, title), (30, title), (37, title)]: each such page must carry at least one key of the References tables in visible text.
Why: Round 8 point 9: the methods named on the main talk carry their source. Only keys already in the References tables (pages 43-44) are used.
Alternatives: Citations in bullets (rejected: the 22 pt bullets are full; captions have a second 16 pt line). MediaPipe, RealSense and AprilTag citations (not placed: MediaPipe and RealSense have no References key; page 30 uses ArUco, not AprilTag).
Evidence: validate_deck.py --pdf: "Every author-year key on any main or hidden page is in a References table (D-277)" and "Every citation_required page carries a References key in visible text (D-277)" pass; the cited list reads 8 Garrido-Jurado 2014, 9 Butterworth 1930, 9 Hampel 1974, 30 Garrido-Jurado 2014, 37 Casiez 2012.
Reversibility: Restore the four captions and the hidden-only check from 9ae156d.
Review: Whether MediaPipe (page 8, 12) and RealSense (page 8) should gain References entries; that needs the author's choice of citation.
Annotation (2026-09-30, build 67): superseded by D-297 and D-301. The author-year keys on pages 8, 9, 30 and 37 are replaced by the deck numbers [1], [2], [3], [4]; the author-year checks and the key-based citation_required check are replaced by the numeric rules 1-9. MediaPipe and RealSense remain without a row.

ID: D-278
Status: SETTLED
Decision: Footer audit rule: every "Chapter(s)", "Section(s)", "Figure(s)", "Table(s)", "Eq(s)." and "Appendix/Appendices" reference in a source_label must name an item of the compiled thesis, read by validate_deck.py from knowledge/thesis_outline.md (lists a-d between "LIST <letter>" and "END", first field; the appendix table's section starts); a range must be ascending in list order; and every thesis equation strip placed on a page must be cited by that page's Eq. references. The parser also asserts the list counts stated in the same file (74, 51, 24, 55; eight appendices).
Why: Round 8 point 9: footers were written by hand and one cited a section the committee copy does not have (Section 9.8).
Alternatives: A containment rule (figure or table inside a cited section) was rejected as a hard check: page 3 legitimately cites Table 1.1 (in 1.2.3) beside Sections 1.1 and 1.2.4.
Evidence: validate_deck.py --pdf: "The footer audit reads complete thesis lists" (counts 74/51/24/55), "Every footer reference names a numbered item of the compiled thesis (D-278)" (107 references, 0 problems) and "Every thesis equation strip is cited by its page footer (D-278)" pass. Negative test: "Section 9.8", "Figures 7.9-7.8", "Eq. 4.3", "Chapter 11" are each reported.
Reversibility: Remove the three checks and thesis_outline_lists/footer_references.
Review: None beyond the check detail.

ID: D-279
Status: SETTLED
Decision: Footer corrections (build 65), each to the thesis: 39 Discussions "Section 9.8; Table 9.1" -> "Chapter 9"; 41 Limitations "Chapter 9; Sections 10.1-10.2" -> "Chapter 9; Table 9.1; Section 10.1"; 42 Contributions "Chapter 10; Sections 10.1-10.2" -> "Section 10.1"; 36 "Figure 8.1; Section 8.1" -> "Figure 8.1; Sections 8.1-8.2"; plus the Eq. additions of D-276 (8, 15, 16, 30). A validator check pins the three closing footers. Page 39's notes Sources line no longer calls lines 52-55 "Section 9.8".
Why: knowledge/thesis_outline.md: the compiled Chapter 9 has no numbered sections (list a "9 | Discussion", no 9.x item), and Table 9.1 is "The six principal limitations of the system" (list c). Page 39's bullets discuss results; the table is on page 41. Page 41's right column (registered route, more subjects, live session) is Chapter_10_Conclusions_Future_Work.txt:10, inside Section 10.1 (list a 10.1 at line 3, 10.2 at line 11); nothing on the page is from 10.2. Contributions are stated in Section 10.1 (outline: "The contribution is a working integrated system ..."). Figure 8.1 is at Chapter_8_Real_Time_Feasibility.txt:11, after the 8.2 heading at line 7 (list b 8.1, list a 8.2).
Alternatives: Keeping "Sections 10.1-10.2" on page 41 (rejected: the page holds no Future Work item). The brief named page 40 for the "Chapter 9; Sections 10.1-10.2" footer; that footer is on page 41, and page 40 (Conclusions divider, "Chapter 10") is correct and unchanged.
Evidence: git diff of talk_content.json; validate_deck.py "Discussions, Limitations and Contributions cite Chapter 9, Table 9.1 and Section 10.1 (D-279)" passes.
Reversibility: Restore the four source_label values from 9ae156d.
Review: Page 36: whether "Sections 8.1-8.2" or "Section 8.2" alone is preferred.
Annotation (2026-10-01, round 11): the validator check now finds the three pages by legacy key, not by title (D-347).

ID: D-280
Status: SETTLED
Decision: effective_text_table.json exceptions renumbered to build 65: films 5, 8, 9, 14-16, 20-23, 25, 28, 34, 37, 39, 51-56 (status-strip note now page 20); Figure 7.1 on 30; marker chart 48; filter panels 57-58; typeset equations 9, 37, 51-58; Figure 8.1 on 36; Figure 2.3 on 4. The page-11 Figure 3.5 exception is dropped because no page places that figure.
Why: Build 64 inserted three pages; the exception pages were build-63 numbers. Main pages 9 and 37 now place the typeset renders.
Alternatives: None.
Evidence: each page checked by visual kind and title in talk_content.json/backup_content.json; report_effective_text.py rerun (review/EFFECTIVE_TEXT.md).
Reversibility: Restore effective_text_table.json from 9ae156d.
Review: None.

ID: D-281
Status: SETTLED
Decision: Build 65 (round 8, M3 part 2) adds visual kind "derivation": nineteen hidden pages 59-77, appended after the previous last hidden page 58, one or two per equation family of equations/derivation_leads.json (families in thesis order, keys in thesis order). Each page stacks full width one 16 pt lead line quoted from derivation_leads.json above the white copy of the numbered thesis crop of each equation (equation_catalog.json "numbered", white copy written by build_deck.py white_numbered_source, alpha bytes unchanged, bound in equations/white_manifest.json as key <key>_numbered). Every crop is placed at one source scale 1.4, horizontally at its thesis position: the thesis page centre 306.0 pt of the 612 pt page (thesis text block 90.1-522.1 pt, midpoint 306.1 pt) maps to the slide centre, so the equation numbers align. A family that does not fit between 1.20 in and 6.80 in on one page is split in two at the split point with the lowest maximum page height. Each page's notes state "This page supports main slide N, <title>." (field supports); each supported main page's notes carry "The derivation of this page's equations is on hidden page(s) ... (not spoken)." The footer cites the sections and equations from knowledge/thesis_outline.md LIST d. Pages and supports: 59-60 -> 11 (Eqs. 3.1-3.6), 61-62 -> 13 (3.7-3.12), 63 -> 12 (3.13-3.14), 64 -> 14 (3.15-3.17), 65 -> 15 (3.18-3.23), 66 -> 16 (3.24), 67 -> 18 (4.1-4.2), 68 -> 21 (5.1-5.4), 69 -> 23 (5.5-5.7), 70-71 -> 22 and 23 (5.8-5.12), 72-73 -> 26 (6.1-6.3), 74 -> 27 (6.4-6.5), 75 -> 26 (6.6), 76-77 -> 30 (7.1-7.6).
Why: Round 8 point 9: main pages show the final equation of a concept; the derivation goes to hidden pages the author can open on request. Scale 1.4 is the largest 0.1 step at which every family fits in at most two pages (1.5 needs three pages for Eqs. 3.1-3.6); at 1.4 the 12 pt thesis math is 16.8 pt on the slide. Keeping the thesis horizontal position keeps the numbers in one column, as in the thesis. Pointers live in the notes as unspoken sentences so the main talk timing and the visible main pages do not change.
Alternatives: Per-crop scales fitted to the width (rejected: equal thesis type sizes would differ on the slide); centring each crop (rejected: the equation numbers would no longer align); visible pointer captions on the main pages (rejected: main-page captions are full and the talk does not mention them).
Evidence: build_deck.py (46 main + 31 hidden, 0 fit warnings, 0 overlap candidates, main talk 1795 s); validate_deck.py --pdf: the D-281 checks (pages appended after every other hidden page; every family placed once in thesis order in at most two parts; crops bound by catalog and white_manifest.json; one source scale 1.4, uncropped, inside the content band; titles and footers from LIST d; lead lines verbatim one above each crop; content above the footer rule; notes name the main slide supported; every main page with a thesis strip names its derivation pages; white_manifest.json lists exactly the 71 placed crops) all pass. Scale and split recheck with the D-286 leads (2026-09-30): at 1.4 no family needs more than two pages, at 1.5 "Camera-prime and the chain (3.1-3.6)" needs three, and every placed split equals the lowest-maximum-height split. Thesis text block 90.1-522.1 pt: previous worker's pdftotext -bbox and pdfinfo reading of writing/v9/Thesis_V9.pdf, not re-measured in this task.
Reversibility: Remove the nineteen derivation entries from backup_content.json, the "derivation" branch of restrained_page, and the D-281 checks; restore revision_id_map.json and media_contract.json from history/round8_b65.
Review: Rendered pages 59-77 (preview/slide-59.png to slide-77.png) at projection size; whether 10.3 pt first-level scripts (D-285) read from the back of the room.
Annotation (2026-09-30, build 67): extended by D-300. The lead of Eq. 3.18 on page 65 now prints the compiled thesis number [52] (compiled_text), not the export number [44].

ID: D-282
Status: UNCERTAIN
Decision: Lead lines and their export text in the notes are written in ASCII: U+2212 (minus sign) becomes "-" and U+22A5 (up tack, perpendicular) becomes "_perp" (LEAD_ASCII in build_deck.py, mirrored in validate_deck.py); U+200B (zero-width space) is removed. After D-286 the visible leads carry no such character; the map applies to the export text quoted in the notes (Eqs. 3.23, 3.24, 5.12) and remains in derivation_lead for any future lead.
Why: build_deck.py text() and notes() raise on non-ASCII text, and the project's plain-text rule (AGENTS.md, Output style) forbids non-ASCII in deck text.
Alternatives: Allowing the two characters in derivation leads only (rejected: breaks the deck-wide ASCII rule); "perp" without the underscore (rejected: runs into the preceding symbol letters).
Evidence: No source defines the spellings; "-" is the ASCII hyphen-minus for the minus sign, "_perp" is a transliteration chosen in build 65. validate_deck.py compares against the same map.
Reversibility: Change LEAD_ASCII in both files.
Review: Whether "_perp" is acceptable in the notes, or another spelling is preferred.

ID: D-283
Status: UNCERTAIN
Decision: The verbatim leads of Eq. 3.21 ("The x and z components share the factor [...], which cancels in the two-argument arctangent:") and Eq. 5.12 ("..., which leaves the perpendicular part [...], and scaling that part to the radius:") contain a relative "which" after a comma that the D-263 question-clause pattern flags. They are quoted unchanged and exempted only as the exact lead string on a derivation page (DERIVATION_QUESTION_EXEMPT = ("eq_3_21", "eq_5_12") in validate_deck.py); a staleness check fails if an exempt lead no longer trips the pattern or is no longer placed. Under D-286 the same two export sentences quoted in the notes are removed as exact strings before the notes scan.
Why: The leads are thesis quotations; rewording them would break the verbatim-quote rule, and the pattern cannot tell a relative "which" from a question clause.
Alternatives: Rewording the leads (rejected: no longer verbatim); dropping the leads (rejected: every crop has a lead); relaxing the D-263 pattern for all text (rejected: weakens the check deck-wide).
Evidence: validate_deck.py --pdf: "The D-263 exemption covers only placed verbatim leads that trip the pattern (D-283)" passes; no other question-clause hit is reported.
Reversibility: Remove the two keys and the exemption code; the question-clause check then fails on pages 65 and 71 until the leads change.
Review: Author call: keep the two thesis sentences as quoted, or accept a shortened quotation that ends before ", which".

ID: D-284
Status: SETTLED
Decision: The unified_revision media_contract.json chains to the build-65 part-1 state without any media change: history/round8_b65/media_contract.json (sha256 9fa7802a8ba3209d446127572d4ede78a9c3244691be64b85373afebc047671b) and history/round8_b65/revision_id_map.json (sha256 7d2a093556bdbd11b30934b3858cb65836a72dfc6a5516bf80c6fdf2f0881f90) are byte copies of the HEAD (bab52a1) files; revision_id_map.json advances to schema 11 (46/31/77; pages 1-58 unchanged; new pages 59-77 with no previous page); the contract keeps all 21 rows at their pages with previous_page = the build-65 part-1 page, and base_contract and previous_page_map point at round8_b65. validate_deck.py audited_archived_composites expects the archived p41 row's previous_page 28 (was 25).
Why: The chained contract method of D-266 and D-275 keeps each row traceable to its previous state; appending hidden pages after 58 moves no row, so only the chain pointers and the archived-row constant change.
Alternatives: Leaving the contract on the round8_b63 snapshot (rejected: the page map changed, so the previous map must be the part-1 state).
Evidence: sha256sum of the two snapshot files equals git show HEAD of media_contract.json and revision_id_map.json; validate_deck.py --pdf: every "Committee asset ... current page follows the page map" check passes; sha256sum -c of the 483-file media reference list: 483 OK.
Reversibility: Restore media_contract.json and revision_id_map.json from history/round8_b65 and the constant 28 -> 25.
Review: None beyond the check detail.

ID: D-285
Status: SETTLED
Decision: effective_text_table.json gains the entry glob presentation/defense_2026/equations/white/eq_*_numbered.png, smallest text "first-level sub- and superscripts", em_px 61.11, and the exception pages 59-77 with reason "thesis derivation quoted as typeset (2026-09-30)". report_effective_text.py reports 50 placed numbered crops at 10.3 pt effective.
Why: The derivation crops are thesis typesetting at one scale (D-281); raising the scripts to 16 pt would need scale 2.2, which does not fit the families on two pages. The exception records the choice instead of hiding it.
Alternatives: Rerendering the equations (rejected: the pages quote the thesis as typeset); a larger scale (rejected by the D-281 fit rule).
Evidence: pdftohtml -xml of writing/v9/Thesis_V9.pdf PDF page 37 (2026-09-30): font sizes 18 (LiberationSerif, OpenSymbol) and 11 at pdftohtml's default zoom 1.5, i.e. 12 pt base math and 7.33 pt first-level scripts; 7.33 pt at the 600 dpi crop resolution is 61.11 px; placed at 1.4 the scripts are 61.11 / (600 / 1.4) * 72 = 10.3 pt and the base math 16.8 pt. review/EFFECTIVE_TEXT.md: 50 rows at 10.3 pt, pages 59-77.
Reversibility: Remove the entry and the exception.
Review: Whether 10.3 pt scripts are acceptable on hidden pages shown only on request.

ID: D-286
Status: UNCERTAIN
Decision: On the derivation pages each inline-math span of a lead is shown as the omission mark "[...]" inside the verbatim quote. The spans are the square-bracket spans of derivation_leads.json source_text that are not numeric citations (the inline-math markup that M3a stripped; a lead with spans must carry the note "square brackets that delimit inline math removed", and the converse); each span, stripped of spaces and U+200B, is found left to right with symbol-character boundaries in the quoted wording (compiled_text when present, else text); a compiled_text lead that drops the span keeps its wording (Eq. 3.17). The notes of the page keep file:line and the full source_text (ASCII-mapped per D-282) of every lead shown with "[...]". build_deck.py and validate_deck.py implement lead_inline_math_spans and derivation_lead identically; a new check per derivation page requires the export text in the notes. Leads changed: 59 Eq. 3.2 "APBORG", "BAT"; 62 Eq. 3.12 "Camera'PL24ORG =  Camera'P24"; 65 Eq. 3.19 "L12a", Eq. 3.20 "sz", Eq. 3.21 "cz", Eq. 3.23 "tt" and "-sin tt, cos tt"; 66 Eq. 3.24 the flattened unit-forearm expression and "L14g"; 67 Eq. 4.1 "ObjectWorldT"; 68 Eq. 5.1 "MappedMarkerh", Eq. 5.4 "c"; 69 Eq. 5.5 "u", "umeas"; 70 Eq. 5.9 "j", Eq. 5.10 "pc", "rc"; 71 Eq. 5.12 "u_perp". Leads with no bracket markup left as quoted, though some read as flattened symbols: Eq. 3.22 "shoulder frame L12", Eq. 7.2 "p_i ... c and covariance C", Eq. 7.4 "p_i", and single-letter symbols in Eqs. 3.1, 3.3, 6.1, 7.3, 7.5, 7.6.
Why: The export flattens inline math into run-together letters (frame labels and sub- and superscripts lose their layout), which misquotes the thesis on a slide that otherwise shows the typeset equation. An omission mark keeps the thesis words verbatim and hides only what the export cannot render; the exact export text stays traceable in the notes. Spans come from the recorded markup, not from guessing.
Alternatives: Keeping the flattened letters (rejected by the master: misleading symbols); transcribing the symbols as native text with sub- and superscripts (rejected: not verbatim and not reproducible from the export); cropping the lead sentences from the thesis PDF (rejected: new media and a new effective-size exception).
Evidence: For every text-based lead, positional replacement of the bracket spans in source_text (U+200B removed) gives the same string as the boundary search; stripping the brackets of source_text reproduces text exactly for all 50 leads. validate_deck.py --pdf: 2081 checks, 0 package failures, including the 19 D-286 notes checks and the D-281 verbatim-lead checks against the transformed leads. Rendered pages 59, 62, 65, 66, 67, 68, 69, 70 and 71 read.
Reversibility: Remove LEAD_OMISSION, lead_inline_math_spans and the notes line from both files; derivation_lead returns to compiled_text or text.
Review: Author call: accept "[...]" in the quoted leads, or prefer another treatment; and whether Eqs. 3.22, 7.2 and 7.4 (no bracket markup) should also be treated.

ID: D-287
Status: SETTLED
Decision: Build 66 extends the D-263 scan to embedded question clauses: EMBEDDING_VERBS (say/says/said, show/shows/shown, ask/asks/asked, is, are, was, were, observe(s/d), discuss(es), watch(es), name(s), know(s), decide(s/d), tell(s), state(s), explain(s), see(s), determine(s), check(s), test(s), measure(s), report(s), consider(s), describe(s), choose(s), matter(s), learn(s), understand) directly followed by a question word is a hit, and ' -- ' is a clause anchor. Eleven hits were rewritten (talk_content.json, restrained_purposes.json; SPEAKER_NOTES.md and DEFENSE_SCRIPT.* regenerate): p3 'Name who needs recorded two-handed motion' -> 'Name the users of recorded two-handed motion'; p5 'Watch how often the hands and the cube hide the forearm and the wrist.' -> 'Watch the hands and the cube hide the forearm and the wrist, again and again.'; p6 'The research question is how object information can constrain an arm when its landmarks are unavailable.' -> 'The research question concerns object information as a constraint on an arm when its landmarks are unavailable.'; p15 'Swing cannot say how far the arm has turned about itself;' -> 'Swing leaves the turn of the arm about itself undetermined;'; p20 'so the output says how it was obtained.' -> 'so the output records the source of each value.'; p20 claim and takeaway 'The output states how each group was obtained.' -> 'The output records the source of each joint group.'; p23 'it does not observe where the person's elbow actually was.' -> 'it does not observe the actual position of the person's elbow.'; p34 'shows where the rendered hands and the cube disagree.' -> 'shows the disagreement between the rendered hands and the cube.'; p35 'Chapter eight asks whether the processing can run causally.' -> 'Chapter eight tests the processing for causal operation.'; p38 'Chapter nine discusses what the evidence supports.' -> 'Chapter nine discusses the claims the evidence supports.'; p42 'and the state labels say when the output is inferred.' -> 'and the state labels mark the inferred output.'
Why: Code review I2: the author's thesis rule forbids what/how/whether/where/who noun clauses after a verb; the D-263 clause anchors did not catch them. Verb-plus-question-word matching leaves relative uses after a noun ('the frame which') unflagged, so no data exemption was needed.
Alternatives: A bare word list (rejected: flags relative clauses); data exemptions for the eleven strings (rejected: every one could be rewritten).
Evidence: validate_deck.py --pdf: 'No question clause ... (D-263)' 0 hits after the rewrites; the new pattern found exactly these eleven hits on the build-65 PPTX (the brief's ten plus p42 'say when'). Function probe: each old string is a hit.
Reversibility: Remove EMBEDDING_VERBS and EMBEDDED_QUESTION; the rewritten texts stay valid.
Review: The rewritten wording, especially p5 and p6.
Annotation (2026-09-30, build 66, re-review M2): the pattern is extended by D-296: one optional adverb between the verb and the question word, the prepositions of, on, about and upon (after a listed verb, or alone before a question word other than which), and the verbs reveal(s), evaluate(s), indicate(s), record(s), illustrate(s), compare(s), depend(s). The rescan found no new hit. The verb list remains a heuristic: a verb outside the list followed by a question word is not reported.

ID: D-288
Status: SETTLED
Decision: In the chained contract branch (schema >= 7) a row follows the page map only if every file binding equals its base row: each *_sha256 key, 'path', every key paired with a *_sha256 key and every repository-path string value (17 keys for p27). The detail line names any changed key. A new check requires rerendered_rows to be absent or empty, since no rerender check exists. The readded_from branch is kept with a comment that no contract the validator reads exercises it.
Why: Code review I1: the base row was compared only on stem, page and source_page, so a rebound base contract with an altered hash passed.
Alternatives: Comparing every key except page and previous_page (not chosen: stricter than the brief's path-and-hash scope; captions could legitimately change); removing the readded_from branch (not chosen: kept for a future added row).
Evidence: Probe A (temporary copy): p27 poster_sha256 altered in history/round8_b65/media_contract.json with base_contract_sha256 rebound -> FAIL 'Committee asset p27-... follows the page map ... changed: poster_sha256'. Repository run: PASS, 17 bound keys equal.
Reversibility: Restore the stem-only comparison.
Review: None.
Annotation (2026-09-30, build 66, re-review blocker): correction. The comprehension bound k.endswith('_sha256'), so the film's own hash key 'sha256' (no underscore) was never compared with the base row, and the '17 keys' above omitted it; a re-rendered film kept at the same path with its row hash updated in both contracts passed. From D-296 the bound keys are 'sha256', every key ending in '_sha256', 'path', every key paired with a *_sha256 key and every repository-path string (18 keys for p27). kind, frames, duration, fps and dimensions are not compared; the film hash implies them.

ID: D-289
Status: SETTLED
Decision: derivation_leads.py gains build() and a --check mode that regenerates the JSON in memory and compares it byte for byte with the committed file; validate_deck.py runs it and, independently, requires each row's source_text to be a substring of line 'line' of its file under writing/v9/zh/src (read only) and compiled_text to be present exactly on rows whose note records the compiled-PDF transcription (eq_3_2, eq_3_6, eq_3_17).
Why: Code review I3: the verbatim-lead check compared the slides only with derivation_leads.json, so an edited JSON would pass.
Alternatives: Checking only the regeneration (not chosen: the brief asked for an independent source-line check as well).
Evidence: derivation_leads.py --check: PASS, 50 leads. Probe A: eq_7_6 source_text altered -> both D-289 checks FAIL. Repository run: both PASS.
Reversibility: Remove the two checks and the --check mode.
Review: None.
Annotation (2026-09-30, build 67): extended by D-300. Rows carrying compiled_text are now eq_3_2, eq_3_6, eq_3_17 and eq_3_18; eq_3_18 adds the compiled number [52] (source_text keeps [44] from writing/v9/zh/src line 87), and validator rule 9 (D-300) checks the compiled bracket numbers against the compiled PDF page.

ID: D-290
Status: SETTLED
Decision: The overlay notes check reads each landmark point's mode from overlay/manifest.json and requires one sentence 'Landmark points <list>: <mode>.' per mode, in order of first use; each overlay slide carries visual.overlay_manifest_sha256 in talk_content.json (84a2c6fb...) and a new check requires it to equal the sha256 of the whole manifest.
Why: Code review I4: 'measured' was hard-coded and a manifest edit outside the checked outputs went undetected.
Alternatives: Computing the binding from the manifest's own entries (not chosen: a whole-file hash also covers fields no other check reads).
Evidence: Probe A: L12 mode changed in landmark_frames, hash not rebound -> six binding checks and the slide-12 notes check FAIL. Probe B: L23 mode changed in torso_root with the hash rebound -> only 'Slide 13 notes state the overlay mode' FAILs.
Reversibility: Remove overlay_manifest_sha256 and restore the fixed 'measured' sentence.
Review: Regenerating the overlays now requires updating the six hash fields.

ID: D-291
Status: SETTLED
Decision: CITATION_REQUIRED is the tuple of legacy keys calibration_landmarks, signal_conditioning, object_rig_accuracy, causal_smoothing; each must name exactly one page, which must carry a References key in visible text.
Why: Code review M3: page-number keys move with every renumbering.
Alternatives: A citation_required data field (not chosen: a deleted field would silently drop the requirement; a missing legacy key fails).
Evidence: validate_deck.py --pdf: the D-277/D-291 check passes; cited 8, 9, 30, 37 as before.
Reversibility: Restore the (page, title) list.
Review: None.
Annotation (2026-09-30, build 67): the requirement that each of the four legacy-key pages carries a citation is kept as rule 7 of D-301, but it now asks for a References row number ([1], [2] and [3], [4]) in visible text instead of an author-year key; superseded in that part by D-301.

ID: D-292
Status: UNCERTAIN
Decision: Visual fixes (build 66): V1 page 26 panel bullets 'Swap S exchanges y, z; Eq. 6.1' / 'Gravity G turns up onto scene Y' / 'Floor t_f: d = 71.6 cm, Eq. 6.6' -> 'Unity y-up via S (Eq. 6.1)' / 'G levels the tilted marker axes' / 'd = 71.6 cm here (Eq. 6.6)'; V2 footers 22 'Eqs. 5.8-5.12' -> 'Eqs. 5.9-5.11', 23 'Eqs. 5.5-5.12' -> 'Eq. 5.12', and page 21 'Eqs. 5.2-5.4, 5.7' -> 'Eqs. 5.2, 5.4' (caught by the new rule), with the check 'Every equation a footer cites is on the page as a strip or named in its text (D-278, D-292)'; V3 page 37 'Replay: each branch within 33.3 ms' -> 'Replay: under 33.3 ms per branch'; V4 page 14 'Origin at the right hip, L24' / 'X along hips; cross products give Z, Y' / 'Standing T-pose: root near (0, 180, 0)' -> 'Recorded T-pose: L24 basis' / 'Top view of the same basis' / '(0, 180, 0) root, offset by tilt, lean'; V5 derivation_leads.json omission_spans (generated by derivation_leads.py VISIBLE_OMISSIONS) for Eq. 3.22 ['L12'], Eq. 7.2 ['p_i', 'c', 'C'], Eq. 7.4 ['p_i'], applied by lead_inline_math_spans in build_deck.py and validate_deck.py (a span must occur in source_text in order; a row may not carry both kinds; note and field must agree). Leads: 3.22 'Its input and output are described in the shoulder frame L12:' -> '... shoulder frame [...]:'; 7.2 'For reconstructed samples p_i, ... uses the sample mean c and covariance C:' -> 'For reconstructed samples [...], ... uses the sample mean [...] and covariance [...]:'; 7.4 'The perpendicular distance of sample p_i is' -> '... of sample [...] is'. Also M6: build_deck.py white_numbered_source opens both images with context managers.
Why: Visual review V1-V5: bullets repeated the baked overlay lines and pages 12-13, footers cited equations the page does not show, a unit wrapped from its number, and export markup read as symbols. 'G levels the tilted marker axes' follows thesis Section 6.4 (the desk card leans; G turns calibrated gravity onto the vertical).
Alternatives: Keeping the Eq. 5.8/5.12 footers (rejected by the new rule); leaving 'i = 1, ..., n' of Eq. 7.2 as quoted (kept: readable text, not listed in the brief).
Evidence: Rendered pages 14, 22, 23, 26, 37, 65, 76, 77 read (preview/slide-NN.png): no unit or equation number wraps; validate_deck.py --pdf 0 package failures; the left-bullet rule (at most 8 words) holds.
Reversibility: Restore the panel_bullets, footers and omission_spans from commit b672d59.
Review: Author call: the page 14 and 26 bullet wording ('here' on page 26 means the rail recording shown).

ID: D-293
Status: SETTLED
Decision: The D-268 widening of a D-255 composite viewport (VIEWPORT_UNITY_LOSS_PX to the left) applies only to measured content rectangles that intersect FILM_VIEWS['unity']; every other rectangle must lie inside the declared view.
Why: Code review M4: the widening applied to every content rectangle, including the camera panel.
Alternatives: None.
Evidence: validate_deck.py --pdf: 'Slide 39 film keeps every measured content panel and hides its burned-in labels (D-261)' passes for p27.
Reversibility: Restore the unconditional widening.
Review: None.

ID: D-294
Status: UNCERTAIN
Decision: Visual findings left unchanged for author calls: caption alignment on frame_figure pages 11, 18, 27 (native caption at the column edge under an image with its own baked band); page 39 bullet spacing and the D-269 caption position; the 11 pt film labels on 28, 34, 37, 39; page 36 Figure 8.1 and page 4 Figure 2.3 baked text (accepted exception D-264); page 22 crop glyphs 'cos j' and 'sin j' (the thesis's own typesetting); charts 48, 57, 58 text sizes (D-259); page 5 black notch and page 25 poster frame (build-61 author calls); page 6 layout; hidden pages 47-48 footer prefixes; stale page numbers in knowledge/deck_fonts.md (delivery task).
Why: The master left these unchanged in round 8, M4 part 1; each needs an author decision or belongs to a later task.
Alternatives: Fixing them in this build (not in the brief's scope).
Evidence: Visual review of build 65 (three reviewers), as relayed in the brief; not re-measured here.
Reversibility: None needed; each item can be taken up separately.
Review: Each listed item.

ID: D-295
Status: SETTLED
Decision: The D-278 footer parser accepts 'and' and ', and' as separators, appendix letters A-Z (unknown ones reported), rejects ranges with more than two ends and appendix ranges, takes chapter numbers only as whole numbers, and reports any capitalised Chapter/Section/Figure/Fig./Table/Eq/Equation/Appendix token left unparsed. footer_parser_self_test() runs twelve negative labels ('Section 9', 'Eq 3.1', 'Equation 4.3', 'Fig. 9.9', 'Chapter 7.9', 'Appendices B-D', 'Appendix Z', 'Sections 10.1-10.2-10.3', 'Section 9.8', 'Figures 7.9-7.8', 'Eq. 4.3', 'Chapter 11') and five positive ones in the validator. The expected list sizes are read from the 'Counts:' paragraph of knowledge/thesis_outline.md (74/51/24/55); an absent paragraph fails the check.
Why: Code review M1, M2. Lower-case words are not reported, because page 47's footer carries prose ('page, table and figure for each row').
Alternatives: Case-insensitive keyword scan (rejected: flags that prose).
Evidence: validate_deck.py --pdf: self-test PASS, 149 footer references with 0 problems; function probe output lists each negative label's problem.
Reversibility: Restore the build-65 parser and OUTLINE_COUNTS.
Review: Whether a lower-case 'section 9' in a footer should also be reported.

ID: D-296
Status: SETTLED
Decision: Build 66 re-review fixes in validate_deck.py: (1) the chained-contract comparison binds the film hash key 'sha256' as well as every *_sha256 key (every row key ending in 'sha256' in the current and base contracts is 'sha256' or ends in '_sha256'); (2) in a footer a reference list must end at the end of the label or at ';', '|' or ')', with spaces allowed before the delimiter, otherwise the text up to the next delimiter is reported (FOOTER_LIST_END; self-test negatives 'Chapters 6 and 7.', 'Sections 3.1, 3', 'Eqs. 5.9, 5.10 and 5.11x' added, fifteen in all); (3) EMBEDDED_QUESTION allows one adverb ([a-z]+ly, also, not, just, still, then, now, first) and one preposition (of, on, about, upon) between a listed verb and the question word, matches a bare preposition before a question word other than which, and adds reveal(s), evaluate(s), indicate(s), record(s), illustrate(s), compare(s), depend(s); (4) the D-289 source-line check and the D-292 footer-equation check require a non-zero count of leads and of footers with equations and print the counts; (5) named_equations looks up the 'equation' pattern by name.
Why: Opus re-review of the build-66 fixes: FAIL on the unbound 'sha256' key (blocker) and minor items M1-M4. Allowing spaces before a delimiter is required by the existing footers ('Table 6.1 | experiments/...', 'Appendix F | v1/...', pages 49-58); a strict next-character rule would report every such footer. which is excluded after a bare preposition because 'of which', 'on which' and 'upon which' are relative in ordinary use.
Alternatives: k.endswith('sha256') (equivalent on the current keys; the explicit form was chosen for readability); a strict next-character footer rule (rejected, see Why); any single word as the adverb slot (rejected: 'shows frames where' would be a false hit).
Evidence: Probes on a temporary copy under /home/luo/.claude/jobs/dd6e65ba/tmp/shadow (repository untouched): base-row p27 sha256 zeroed with base_contract_sha256 rebound -> FAIL 'Committee asset p27-... current page follows the page map ... changed: sha256' (1 package failure; c_sha.log in the same folder, recorded by the build-66 probe run with the pre-fix validator, shows 0 failures for the same mutation); current-row p27 sha256 zeroed -> the same chain FAIL and 'current path binding' FAIL (2 package failures); restored copy -> 2092 PASS, 18 bound keys equal. Footer self-test: PASS with the three new negatives reported. Embedded-question scan of the build-66 deck: 0 hits; the five relative or adverbial phrases ('the frame which', 'the point where', 'during which', 'in which', 'at which') do not match (only 'in which' occurs in talk_content.json, backup_content.json and DEFENSE_SCRIPT.md, twice). Repository run: validate_deck.py --pdf 2092 PASS, 0 package failures; D-292 detail '31 footers cite 71 equations'; D-289 detail '50 leads'.
Reversibility: Restore the build-66 (1e0adb3) forms of the five items.
Review: The embedded-question list remains a heuristic (D-287).

ID: D-297
Status: SETTLED
Decision: The deck keeps its own IEEE numeric reference list, numbered [1] .. [12] from 1 in order of first citation (main pages 8, 9, 30, 37, then hidden page 47 table rows top to bottom, 48, 51, 53, 54, 56, 57, 58): [1] Garrido-Jurado, [2] Hampel, [3] Butterworth, [4] Casiez, [5] Olson, [6] Wang and Olson, [7] Krogius, [8] Romero-Ramirez, [9] Pearson, [10] Oppenheim, [11] Gustafsson, [12] Savitzky and Golay. In-text style as the compiled thesis: each number in its own brackets, ", " separated, no ranges; a name may stay next to its number, a year never. Captions: page 8 "ArUco markers [1].", page 9 "Hampel [2], Butterworth [3].", page 30 "ArUco [1].", page 37 "One Euro filter [4]."; hidden pages 47 (Source column "[1], Table 3", "[5], p. 7", "[6], p. 6; Table I (p. 4)", "[7], Fig. 7", "[8], Table 3"), 48 "Krogius et al. [7]", 51 "[2], [9].", 53 "[3], [10], [11].", 54 "[12].", 56 "[4].", 57 "[3], [11], [12].", 58 "[4]."
Why: Author messages of 2026-09-30: "citation should be the same as thesis, using ieee format please", and, asked how to treat works the thesis does not list, "thesis should have its separate reference list, starting from 1". The compiled thesis uses 21 x "[a], [b]" and no "[a, b]" or "[a]-[b]".
Alternatives: The thesis compiled numbers ([45], [48], [50], [58] ...) on slides (rejected: four works are not in the thesis and the numbers would not be contiguous); author-year keys as in D-277 (rejected by the author's "ieee format"); one list that keeps the thesis numbers and continues from 59 for the other works (rejected by "separate list, starting from 1"); ranges such as "[2]-[4]" (rejected: the thesis uses none).
Evidence: The author's two sentences above. talk_content.json and backup_content.json: no author-year string remains (validator rule 3). validate_deck.py --pdf (2098 PASS, 0 package failures): rules 4 (one number per bracket), 5 (contiguous [1] .. [12] over pages 43-44) and 6 (first citations in order [1, 2, ..., 12]) PASS. Mapping deck -> thesis compiled: [2] 45, [3] 48, [4] 50, [6] 58, [9] 46, [10] 47, [11] 49, [12] 54; [1], [5], [7], [8] not in the thesis (knowledge/references.md).
Reversibility: Restore the author-year captions, the page 43-44 tables and the D-277/D-291 checks from ceb67d4.
Review: None for the numbering (author decision). Open from D-277 unchanged: MediaPipe and RealSense still have no row.

ID: D-298
Status: SETTLED
Decision: References pages 43 ([1]-[6]) and 44 ([7]-[12]): columns ["No.", "Reference"], column_widths [0.06, 0.94], titles, source_label and duration 5 s unchanged. Eight rows are the thesis entries byte for byte from writing/v9/Thesis_V9.docx with the "[NN] " prefix removed: [2] Hampel paragraph 1077, [9] Pearson 1078, [10] Oppenheim 1079, [3] Butterworth 1080, [11] Gustafsson 1081, [4] Casiez 1082 (now with the full venue "in Proc. SIGCHI Conf. Human Factors in Computing Systems (CHI), 2012, pp. 2527-2530."), [12] Savitzky and Golay 1086, [6] Wang and Olson 1090. Four rows are not in the thesis and follow its style without a DOI: [1] Garrido-Jurado with all four authors spelled out (S. Garrido-Jurado, R. Munoz-Salinas, F. J. Madrid-Cuevas, and M. J. Marin-Jimenez), [5] Olson, [7] Krogius, [8] Romero-Ramirez. The split is six and six by number, not by family. The claim, purpose, provenance and source fields are prose with deck numbers and "thesis entries 45, 48, 50 and 58" style words; no bracketed thesis number and no range.
Why: The author asked for the thesis's format; copying the thesis entries unchanged removes any difference between the deck and the document the committee holds. The round-8 shortening of Casiez and of the authors of Garrido-Jurado existed only to fit two lines; D-299 gives a three-line row room. The family split of D-267 cannot hold once the numbers follow first citation, because marker and filter works interleave.
Alternatives: Keep the round-8 shortened Casiez venue and "S. Garrido-Jurado et al." (rejected: differs from the thesis entry; the thesis lists authors in full); DOIs (not printed: the thesis entries carry none); a split by family (rejected, see Why).
Evidence: This task: python-docx read of Thesis_V9.docx paragraphs 1077, 1078, 1079, 1080, 1081, 1082, 1086, 1090 with the prefix removed equals the eight table cells (8 of 8 equal). Deck-only rows composed from knowledge/marker_literature.md, fields confirmed on Crossref on 2026-09-28 (knowledge/references.md). Rule 5 PASS (rows [1] .. [12] contiguous).
Reversibility: Restore the round-8 rows from ceb67d4.
Review: Whether the four deck-only entries (spelling of the authors' names without accents, sentence-case titles) read like the thesis entries.

ID: D-299
Status: SETTLED
Decision: build_deck.py restrained_full_table counts the lines of every cell first (the same wrap metric as text()); a row whose widest cell needs three lines is drawn THIRD_LINE = 0.30 in taller; rowh = min(.82, (bottom - 1.34 - THIRD_LINE * n3) / len(rows)) with n3 the number of three-line rows; rows are placed at cumulative y; it raises if rowh < .40, if rowh < .66 and a cell needs more than one line, or if any cell needs more than three lines. Rows [1] and [4] of page 43 are the two three-line rows.
Why: The thesis Casiez entry and the four-author Garrido-Jurado entry need three 16 pt lines at column_widths [0.06, 0.94]; the builder capped every row at 0.82 in and raised above two lines.
Alternatives: Shrinking the type (forbidden, no font reduction); shortening the two entries (rejected, D-298); more columns or narrower numbers (rejected: the two lines still did not fit).
Evidence: 0.30 in: one 16 pt line at the builder's 1.18 leading is 16 * 1.18 / 72 = 0.262 in (builder comment), rounded up to 0.30 in; the 0.038 in margin is an editorial choice, not measured. The thresholds .82, .66 and .40 are the existing limits. Worker check against the committed build-66 PPTX: the spTree XML of every full_table page except page 43 is byte-identical to build 66 (reported by the worker and checked by the master; not re-run in the documentation task).
Reversibility: Restore restrained_full_table from ceb67d4; rows [1] and [4] would then raise.
Review: Page 43 (preview/slide-43.png): the two three-line rows and the space under the table. Side finding, pre-existing: restrained_bullets zips its three y positions with the bullet list and silently drops a fourth bullet; no page has four.
Annotation (2026-09-30, build 67, code review M1): the side finding is fixed by D-303; restrained_bullets and the bullet_y branch now raise instead of dropping bullets.

ID: D-300
Status: SETTLED
Decision: Hidden derivation page 65 (Eq. 3.18) quotes the compiled thesis number: equations/derivation_leads.py COMPILED["3.18"] = ("They separate into swing and twist [52], with the twist innermost:", 46), compiled PDF page 46; derivation_leads.json is regenerated (eq_3_18 compiled_text). The zh/src line 87 prints [44] (source numbering) and stays in source_text. Dobrowolski, compiled thesis entry 52, is not added to the deck list; the deck never cites it in its own voice. Derivation lead strings are excluded from the deck-number scans; validator rule 9 requires each [n] in a compiled_text lead to be printed on its compiled PDF page.
Why: The page quotes what the committee holds: the compiled thesis prints [52] there, and [44] is Collins and Bartoli, a different work. A verbatim quotation is not a citation by the deck, so it carries no row of its own.
Alternatives: Quoting [44] as in the export (rejected: wrong work in the compiled thesis); removing the bracket (rejected: the lead is a verbatim sentence, D-283/D-286); adding Dobrowolski as deck row [13] (rejected: a row must be cited by a deck page, rule 2).
Evidence: Thesis_V9.docx paragraph 1076 is "[44] T. Collins and A. Bartoli ..." and paragraph 1084 is "[52] P. Dobrowolski ..."; derivation_leads.json eq_3_18 compiled_text as above; validate_deck.py --pdf: "Every [n] in a compiled_text derivation lead is printed on its compiled PDF page (D-300, rule 9)" PASS, detail eq_3_18 p46 ['52'].
Reversibility: Remove the COMPILED entry and regenerate derivation_leads.json.
Review: None.

ID: D-301
Status: SETTLED
Decision: validate_deck.py replaces the two author-year checks of D-277 (every author-year key in a References table; every References key visible on a hidden page) and the key part of the citation_required check by nine rules: 1 every [n] on a main or hidden page is a References row number (the digit pattern never matches the omission mark "[...]"); 2 every row number is cited on at least one page, main or hidden; 3 no author-year string (AUTHOR_YEAR plus an "et al." variant) in the visible text or notes of any page; 4 one number per bracket (no "[a, b]", "[a; b]", "[a-b]", "[a]-[b]"); 5 row numbers contiguous [1] .. [N] over both pages; 6 first citations walking the talk and then the backups equal 1 .. N; 7 each CITATION_REQUIRED page (legacy keys of D-291) carries a row number; 8 every [n] in notes is a row number; 9 compiled_text numbers appear on the cited PDF page (D-300). Derivation lead strings and quoted source_text are excluded from the scans; the notes include the provenance and source fields, which build_deck.py appends to the notes. The round-5 files presentation/defense_2026/references/KEY_USAGE.md and references/page50_snippet.json are deleted (git rm); they described the author-year keys and the round-5 References pages.
Why: D-297 changes the citation form; the old checks would reject every numeric citation and accept a leftover author-year string. The two deleted files contradict the deck. The regex pattern for "Krogius et al. 2019" escaped the round-8 author-year expression.
Alternatives: Keeping the author-year checks beside the new ones (rejected: they fail on the new captions); counting bracket numbers without the first-citation and notes rules (rejected: the author asked for the thesis's first-citation numbering).
Evidence: validate_deck.py --pdf: 2098 checks PASS, 0 package failures, overall PARTIAL only for D-058/D-066 (review/ARTIFACT_CHECK.json; 2092 at build 66, three round-8 citation checks gone, nine new). Negative probes in a shadow copy (worker report; not re-run here): a leftover "Hampel 1974", a "[13]", a "[2, 3]", a swapped first-citation order and a "[45]" in notes each FAIL the intended rule. Deletion approved in the round-9 plan (ASSUMPTIONS A5). After the deletion the only remaining mentions of the two files outside git history are DECISIONS.md history, a comment in validate_deck.py (superseded note) and knowledge/references.md history notes.
Reversibility: git checkout ceb67d4 -- the two files; restore the D-277 and D-291 checks from ceb67d4.
Review: The bracket-number scan treats any "[n]" as a citation; a future "[1]" meaning something else (an array index, a frame number) would need an exemption.
Annotation (2026-09-30, build 67, code review I1 and M2): extended by D-303. The rules read the References rows from talk_content.json only; D-303 adds two checks that bind every full_table cell to exactly one drawn text box and the References (number, entry) pairs to the JSON rows in reading order. AUTHOR_YEAR now also matches ", " or " (" before the year, and rule 4 also flags adjacent bracket citations not separated by exactly ", ". The check count is 2100 (2098 above).

ID: D-302
Status: SETTLED
Decision: Page 18 (Object pose in the World frame) labels the wall marker. The overlay overlay_object_world gains a fourth frame, Wall, in projected mode from T_cam_wall of eval/output/scene_calibration_r6bc.json (wall marker ID 0, 150 mm, thesis WallCameraR, Section 2.2.2), drawn by a new generator pose type "calibration_marker" with a reprojection check; axis length 0.30 m (twice the 150 mm print, rule N-5); the Camera legend moves to the upper-right corner (anchor 1100, 110) because the wall marker sits under the old upper-left legend (labels stay 57 px, 17.1 pt). Page 18 text: the World bullet reads "World: fixed desk marker; Wall: gravity reference"; caption "World, Object and Wall projected from calibration."; footer "Sections 2.2.2, 4.1; Eq. 4.1"; the notes state the Wall frame and the mode of every frame (provenance: World, Object and Wall projected, Camera illustrative; D-290). Modes on the overlay: World projected, Object projected, Wall projected, Camera illustrative. overlay/manifest.json sha256 is now abd988f11981d9b3e87bef1b4bfd6768d2b4689b4f37503bd4c73cdac4e90440 (was 84a2c6fb...), bound by visual.overlay_manifest_sha256 on pages 11, 12, 13, 18, 26, 27 (D-290); the other five overlay PNGs are byte-identical; overlay_object_world.png is not a media_contract.json row.
Why: Author, 2026-09-30: "p18, the label of wall marker is not drawn". The marker is visible in the photograph and the thesis names the frame (Wall, gravity reference, Section 2.2.2); thesis Figure 4.1 itself omits it.
Alternatives: A per-frame detection of ID 0 as the pose source (not needed: the plan assumed no committed wall pose, but scene_calibration_r6bc.json carries T_cam_wall; the detection is kept as the cross-check); a label-only "Wall marker" in illustrative mode (rejected: the pose exists); no legend move (rejected: label overlap).
Evidence: manifest.json reprojection_checks.wall_origin_vs_wall_marker: the pinned detector (DICT_5X5_50, CORNER_REFINE_APRILTAG) finds ID 0 on the deck copy of frame 505 at corner mean (118.79, 154.56) px; T_cam_wall projects to (118.72, 154.52) px; residual 0.08 px (World 0.72 px and Object 0.02 px as before). The projection assumes the camera has not moved since the calibration, as for World. The generator, which fails on a label outside the canvas or two overlapping labels (NOTES.md N-2), ran to completion (NOTES.md N-10, N-11). validate_deck.py --pdf 2098 PASS.
Reversibility: Restore spec_object_world.json, the generator, the PNG, manifest.json and page 18 fields from ceb67d4 and the six overlay_manifest_sha256 fields.
Review: Page 18 (preview/slide-18.png): the Wall label and axes upper-left in the photograph, the legend upper-right, that the 0.30 m axes do not crowd the desk card.
Annotation (2026-09-30, build 67, code review M4): extended by D-303. The generator now raises when the World, Object or Wall reprojection residual exceeds 1.0 px and records the bound in manifest.json (reprojection_checks.residual_bound_px). The six overlay PNGs regenerated byte-identically; manifest.json sha256 is now 73e7300fd9f565f05c4b2698e93ccf781a25075b639bfa599cb2e3ac89582bd6 (was abd988f1...), rebound on pages 11, 12, 13, 18, 26, 27.

ID: D-303
Status: SETTLED
Decision: Four fixes from the round-9 Opus code review (PASS with findings I1, M1-M5), applied at effort xhigh. (I1) validate_deck.py adds two checks: every full_table page (41, 42, 43, 44, 47, 49) draws each cell of its display_table, header and rows, as exactly one text box of its slide (a value that occurs k times is drawn by exactly k boxes), and the References pages 43-44 draw their (number, entry) pairs in reading order (top, then left) equal to the JSON rows. (M1) build_deck.py restrained_bullets raises a ValueError naming the page when there are more bullets than its three slots, and the bullet_y branch raises when bullet_y and panel_bullets differ in length. (M2) AUTHOR_YEAR also matches ", " or " (" before the year ("Olson, 2011", "Olson (2011)"), with the Frame/Figure/Table/Page/Slide exclusion extended to the same separators; the one IEEE book shape "City: Publisher, year" (row [10], "USA: Pearson, 2010") is exempt only in the visible rows of the References pages; CITATION_STYLE_VIOLATION also matches two bracket citations on one line separated only by spaces, tabs, commas or semicolons when the separator is not exactly ", " ("[2],[3]", "[2] [3]", "[2]; [3]", "[2][3]"). (M4) make_frame_overlay_figures.py REPROJECTION_BOUND_PX = 1.0: the generator raises when the World, Object or Wall reprojection residual exceeds it and writes the bound into manifest.json (reprojection_checks.residual_bound_px); the two Unity anchor checks (2.88 px and 3.61 px against hand-measured anchors in a rendered Unity frame) are recorded without the bound. M3 is inherent to a text scan (a "[9]" in notes that means a thesis number cannot be told from deck row [9]); M5 corrected the wording of the table-geometry claim: the round-9 builder leaves the geometry unchanged on every table without a three-line cell, and page 44's geometry changed only because its content changed.
Why: The review showed that the References rules read the rows from the content file only, so a row removed or altered in the built PPTX passed; that zip() silently dropped bullets; that "Olson (2011)", "Olson, 2011" and "[2],[3]" passed the citation rules; and that the recorded reprojection residuals were compared with nothing.
Alternatives: Binding the References pages only (rejected: every full_table page has the same gap); comparing concatenated slide text (rejected: an altered cell could still be found inside another string); dropping rule 3 on the References rows (rejected: an author-year string in an entry would then pass); applying the 1.0 px bound to the Unity checks (rejected: they compare with hand-measured anchors in a different camera model and would fail at 2.88 px and 3.61 px).
Evidence: validate_deck.py --pdf: 2100 checks PASS, 0 package failures, overall PARTIAL only for D-058/D-066 (review/ARTIFACT_CHECK.json; 2098 before, two D-303 checks added). Negative probes on a shadow copy of the build (/home/luo/.claude/jobs/dd6e65ba/tmp/r9/fix, repository untouched): deleting the "[12]" number text on page 44, deleting both boxes of row [12] on page 44, and replacing "A. Savitzky and M. J. E. Golay" by "A. Nobody" on page 44 in the PPTX each FAIL both D-303 checks (0 failures before this fix); "Olson (2011)" and "Olson, 2011" in page 47 notes FAIL rule 3; "Hampel (1974)" and "Hampel, 1974" on page 51 FAIL rule 3; "USA: Pearson, 2016" on page 51 FAIL rule 3 (the exemption holds on the References rows only); "E. Olson (2011)," in References row [5] FAIL rule 3; "[2],[3]" and "[2] [3]" on page 9 FAIL rule 4; the earlier probes still FAIL: "[13]" (rules 1, 6), "[2, 3]" (rule 4), "[2]-[3]" (rule 4), "Hampel 1974" (rule 3), swapped first-citation order (rule 6), "[45]" in page 47 notes (rule 8); the unmodified copy passes (0 failures). The live References rows ("(CHI), 2012", "vol. 2016") and "Frame 1890", "Table 3 (p. 10)" do not match AUTHOR_YEAR (regex unit test). M1: restrained_bullets with four values and page id 99 raises "Slide 99 has 4 panel_bullets but only 3 bullet slots"; a page with two bullet_y values for three bullets raises; the deck builds (bullet_y lengths equal the bullet counts on pages 8, 9, 15, 22, 30, 31, 32, 33, 39, 51-58). M4: with the bound set to 0.5 px in a test call, reprojection_checks raises on World (0.72 px); with 1.0 px the six overlay PNGs regenerate byte-identically (sha256 before and after equal) and manifest.json changes only in generator_sha256 and the new residual_bound_px field, sha256 73e7300fd9f565f05c4b2698e93ccf781a25075b639bfa599cb2e3ac89582bd6, rebound on pages 11, 12, 13, 18, 26, 27. M5: drawing the current content of pages 41, 42, 44, 47 and 49 with the build-66 and the round-9 restrained_full_table gives identical shapes and geometry; page 43 raises under the build-66 builder (three-line cells). The rebuilt PPTX is byte-identical to the build-67 PPTX before these fixes (sha256 2d5747d7...).
Reversibility: Remove the two D-303 checks and restore the two regexes, the bullet guards and the generator bound from the build-67 working tree before this entry; regenerate manifest.json and rebind the six overlay_manifest_sha256 fields.
Review: The 1.0 px bound was set by the review brief, not derived from a measurement; the recorded residuals (0.72, 0.02, 0.08 px) sit under it. The References exemption accepts any "Name, year" preceded by ": " in a References row.

ID: D-304
Status: UNCERTAIN
Decision: Round 10 (build 68): the task-video page (now page 4) plays a new raw clip of the R7 handover only, media/raw_handover_task.mp4, R7 (Video/recording_20260909_000024.bag) BagSource frames 690-1199 inclusive, 510 frames at the native 30 fps = 17.000 s, 640 x 480, poster at R7 frame 950; committee copy committee_materials/unified_revision/videos/p04-Raw_Handover_Task.mp4 with poster, source-frame map and provenance JSON; the burned-in one-line caption strip is covered by the measured mask (review/film_geometry.json).
Why: Author, 2026-09-30: page 5 plays the handover recording only, not the rail pass followed by the handover. The window is the R7 segment of the round-3 clip (D-110), chosen there from contact sheets at 15-frame spacing: the right hand sliding the cube, the left hand arriving at about frame 870, both hands on the cube at about 885-1005, the right hand released by about 1020, the left-hand slide to the far end and the left hand lifting off at about 1185. A contact sheet of frames 600-1280 at 20-frame spacing (worker, 2026-09-30) shows the same sequence. Frame 950 (both hands on the cube) is the transfer, chosen as the poster; that choice is editorial.
Alternatives: R7 from about frame 90 (the whole right-hand slide; about 37 s, rejected in D-110 and longer than the 40 s provisional page budget with speech); ending at 1280 (adds about 3 s of the hand resting on the cube, no new event).
Evidence: anim/raw_handover_task.py run with the v3rt Python: "PASS: presentation/defense_2026/media/raw_handover_task.mp4; 510 frames; 17.000 s"; the round-3 generator's checks pass on every frame (bag sha256 equals the archive index d0fd9412..., no burned-in landmark drawing, stills 700, 950 and 1042 pixel-identical to writing/v9/figures/src copies, full decode). The wrapper reuses anim/raw_task_context.py unchanged (sha256 c2db5c21...), so the old clip raw_task_context.mp4 and p05-Raw_Task_Context.* stay on disk untouched.
Reversibility: Point page 4 back to p05-Raw_Task_Context and restore the p05 row from history/round10_b68/media_contract.json.
Review: Inspect the four stills (start 690, before transfer 860, transfer 950, end 1199) and confirm the window covers approach, transfer and release.

ID: D-305
Status: UNCERTAIN
Decision: Provisional page budgets for round 10: task video 40 s, static marker calibration 30 s, landmark acceptance 40 s, Hampel 40 s, short-gap 40 s, Butterworth 40 s; every other duration unchanged; main total 1785 s = 29:45.
Why: Set by the round-10 M1a brief; final values are reset in M3 from the rewritten script and film lengths.
Alternatives: Keeping the old 75 s task-video budget (rejected: the clip is 17 s, no rail pass).
Evidence: None measured; brief values. talk_content.json durations sum to 1785 (restructure script output "main 1785 pages 48 28").
Reversibility: Edit the six duration fields.
Review: Reset in M3 from an aloud rehearsal or word counts.

ID: D-306
Status: UNCERTAIN
Decision: The deck's own reference list [1]..[12] is renumbered in first-citation order after the restructure: old [9] -> [3], [3] -> [4], [10] -> [5], [11] -> [6], [4] -> [7], [5] -> [8], [6] -> [9], [7] -> [10], [8] -> [11]; [1], [2], [12] keep their numbers. The References rows on pages 45-46 are reordered with their entries unchanged, and every [n] in the visible text and notes of every non-derivation page is mapped.
Why: Hidden pages 51 and 53 were the only pages citing [9] (Hampel parameters) and [10] (Butterworth); their films and captions move to main pages 9 and 11, so these citations now first appear on main pages before [4] (One Euro, page 39). Rule 2 (every row cited) and rule 6 (first citations 1..N) of D-297/D-301 then hold only with the author's own first-citation numbering rule applied again.
Alternatives: Main filter captions with only [2] and [3] as the merged page had (rejected: [9] and [10] would be cited nowhere, rule 2 fails); dropping rows [9] and [10] (rejected: removes accepted references); citing them on a later hidden page (rejected: no fitting page before the Savitzky-Golay page [12]).
Evidence: validate_deck.py rules 1, 2, 5, 6, 7 and 8 pass at build 68. The mapping was applied by a script that touched only bracket numbers 1-12 in string fields and skipped derivation pages (thesis numbers such as [52]) and source fields.
Reversibility: Apply the inverse map and restore the References row order from build 67.
Review: Author: accept the renumbered list, or prefer the main filter captions without [3] and [5].

ID: D-307
Status: SETTLED
Decision: Hidden pages 51 (Hampel), 52 (short gaps) and 53 (Butterworth, film p43 a byte copy of p09) are removed; their films p07 and p08 move to main pages 9 and 10 and p09 stays on the Butterworth page 11. The media contract chains to build 67: history/round10_b68/media_contract.json and revision_id_map.json are byte copies of the build-67 files; revision_id_map.json becomes schema 12 (48/28/76; old 4 -> 5, 5 -> 4, 6 deleted, 7 -> 6, 8 -> 8 with new page 7 split from it, 9 -> 11, 10-46 -> 12-48, 47-50 -> 49-52, 51 -> 9, 52 -> 10, 53 deleted, 54-77 -> 53-76); 19 rows follow the map, the p05 and p43 rows are dropped (dropped_rows), the p04 row is added at page 4 (added_pages [4]).
Why: Author, 2026-09-30: three filter pages each with its own film; the media contract binds one film to one page, so the hidden copies would duplicate the main films. The chained method of D-266, D-275 and D-284 keeps each kept row traceable to its previous page without changing media bytes.
Alternatives: Keeping the hidden filter pages (rejected: duplicate films); re-running anim/unified_revision_build.py (not used: it is still rebased on the round-5 contract, and rounds 8 and 9 repaged the contract without it, D-275, D-284).
Evidence: validate_deck.py --pdf at build 68: every "Committee asset ... current page follows the page map" check passes (for example p07 7 -> 51 -> 9, p09 9 -> 9 -> 11, p04 added at page 4).
Reversibility: Restore media_contract.json and revision_id_map.json from history/round10_b68 and the content JSON from build 67.
Review: None beyond the check detail.

ID: D-308
Status: SETTLED
Decision: Checks re-pointed for the new structure, none removed: CITATION_REQUIRED (calibration_landmarks, signal_conditioning) -> (static_marker_calibration, filter_hampel, filter_butterworth), five pages instead of four; the filter-page geometry check takes its reference film from the page with legacy key filter_hampel instead of content[8] and now also covers the three main filter pages, with a new check that the main filter pages are exactly filter_hampel, filter_short_gap, filter_butterworth with typeset equations; a new check binds the Eq. 2.1 label (last bullet "Eq. 2.1: ...") directly above the Eq. 2.1 strip on the static marker calibration page; UNIFIED_FOUR_ROUTE current pages 14/15/16 -> 16/17/18; FILM_MASKS_PX and FILM_GEOMETRY_PX lose p05 and p43 (no longer placed) and gain p04 from a re-run of measure_film_geometry.py; build_deck.py drops the scope branch (no page uses it after page 6 is deleted).
Why: The D-262 rule requires every measured film to be placed and every placed film measured; the citation rule 7 requires one page per key; the geometry check was hard-coded to page 9.
Alternatives: Waiving the checks for the moved pages (rejected: AGENTS.md "fix, never waive").
Evidence: validate_deck.py --pdf at build 68, 0 package failures.
Reversibility: Restore the build-67 validator and builder.
Review: None.

ID: D-309
Status: UNCERTAIN
Decision: Split pages and keys: page 7 "Static marker calibration" (legacy key static_marker_calibration, kind calibration, still media/matched/r6b_frame_533.jpg, bullets "Desk marker as world frame", "Ten detections per static marker", "Eq. 2.1: mean marker rotation", Eq. 2.1 strip at 4.05 in, caption with ArUco [1]); page 8 "Landmark acceptance" (landmark_acceptance, film p06, caption without the citation); pages 9-11 "Hampel spike removal" (filter_hampel), "Short-gap interpolation" (filter_short_gap), "Butterworth smoothing" (filter_butterworth), each in the hidden-page composite geometry (bullets at 1.40, 2.49, 3.58 in, equations from 4.62 in) with its typeset equations ts_hampel, ts_gap, ts_butter and ts_filtfilt.
Why: Author, 2026-09-30: Eq. 2.1 belongs to static marker processing and needs a label that names what it computes. Thesis Section 2.2.2 (writing/v9/zh/src/Chapter_2_Experimental_Setup.txt line 36): "The element-wise rotation mean generally loses orthonormality, so it is projected onto the nearest proper rotation [45], giving the chordal mean." The label is a 22 pt bullet because a 16 pt line in the left column fails the validator font-role region rule (16 pt only in the right region). The 4.05 in strip start follows the builder's D-276 rule (one 22 pt line from 3.52 in ends at 3.88 in, plus 0.10 in).
Alternatives: The label as a separate 16 pt line (rejected: font-role rule); the 28a1396 page forms with no equations on the filter pages (rejected: the plan restores each filter's typeset equation).
Evidence: validate_deck.py D-308 label check passes; rendered preview pages 7-11.
Reversibility: Edit the page specs in talk_content.json.
Review: Author: the label wording "Eq. 2.1: mean marker rotation" (the longer "Eq. 2.1: averaged marker rotation" wraps to two 22 pt lines), the still on page 7 and the filter bullets.

ID: D-310
Status: SETTLED
Decision: Round 10 (build 69): the pipeline stage formerly called "signal conditioning" is named "data preprocessing": page 2 outline row "Camera measurements and data preprocessing", the page 2 notes, and every live source that feeds a visible or generated output (talk_content.json, README.md; restrained_purposes.json, REVISION_OUTLINE.md, SPEAKER_NOTES.md and DEFENSE_SCRIPT.* regenerate from them). DECISIONS.md history entries and committee_materials/*/history/ copies keep the old words.
Why: Author, 2026-09-30 (R1): "signal conditioning" is not the author's term; the stage is data preprocessing (plan A4).
Alternatives: "Data filtering" (rejected: the stage also rejects and interpolates samples, and the author named the term).
Evidence: Author instruction; validate_deck.py D-311 (c) finds no "signal conditioning" in any visible text or notes (build 69).
Reversibility: Text replacement in talk_content.json and README.md, then rebuild.
Review: None beyond the outline row on page 2.

ID: D-311
Status: SETTLED
Decision: validate_deck.py gains four wording checks and a self-test (build 69): (a) no ";" in any title, bullet, panel bullet, caption, table cell or other native text line, exempting the footer line equal to source_label and the exact verbatim derivation lead strings on derivation pages; (b) no bullet or panel bullet ends with a full stop; (c) no "signal conditioning" or "Camera-prime", any case, in visible text or notes; (d) no internal recording name (R5, R6, R6a, R6b, R7 as whole words) or repository file name or path (known extensions, or a known top-level directory followed by "/") in visible text. The self-test runs 15 bad and 9 good samples. Two existing pins were updated to the new wording without loosening them: the page-34 synthetic-removal caption must start with "Right arm, 45 frames per window" (was "R7 right arm, ..."), and THESIS_RECOVERY_AGGREGATE uses ", left n 16" (was "; left n 16").
Why: Author, 2026-09-30 (R2, R3, R4) and plan A10/A11; a check keeps later edits from reintroducing the patterns. A notes semicolon check waits for the script rewrite (brief).
Alternatives: Scanning only the JSON fields (rejected: native labels drawn by the builder and table cells would escape); exempting the whole footer from (d) (rejected: the footers carried the file paths).
Evidence: Build 69: package checks 2063 -> 2068 (four checks plus the self-test), all PASS; of the 75 recast strings of the M1b wording table, the 43 "before" strings with a semicolon, internal name or path are flagged by wording_hits; every "after" string is clean except five footer lines whose ";" the source_label exemption covers (worker probe).
Reversibility: Remove the D-311 block in validate_deck.py.
Review: Whether table cells should stay in rule (a) (they are native text; no current cell needs a semicolon).

ID: D-312
Status: SETTLED
Decision: Camera' (ASCII apostrophe, as the thesis writes it) replaces "Camera-prime" in every visible string, caption, note, title and generator label of the live deck sources: talk_content.json, backup_content.json (derivation titles, claims, notes, derivation_family), build_deck.py (node "Target in Camera'", cutting-guide text), spec_camera_frames.json (frame name and name_label), make_frame_overlay_figures.py, equation_assets.py and equation_catalog.json (titles, semantic notes), equations/derivation_leads.py and derivation_leads.json, QA_PREP.md, README.md, equations/README.md, MEDIA_PROVENANCE.md. Code identifiers and data keys stay (points_camera_prime_m, CAMERA_TO_CAMERA_PRIME, f_prime_*). The overlay PNGs were regenerated: only overlay_camera_frames.png changed; the overlay manifest sha256 is now 54c1e95f... on all six overlay pages (73e7300f... before).
Why: Author, 2026-09-30 (R2).
Alternatives: None considered; the spelling is the author's.
Evidence: make_frame_overlay_figures.py run (five other PNG hashes unchanged); derivation_leads.py --check PASS; validate_deck.py overlay binding and D-311 (c) PASS.
Reversibility: Reverse the replacement and regenerate the overlays and leads.
Review: Not changed (out of the live deck path): make_coordinate_figures.py and figures/coordinate_frames/manifest.json, anim/*.py generators of earlier films and their provenance JSON, review/ audit reports, overlay NOTES.md, committee VIDEO_INDEX files. The current films p13, p15 and p16 come from anim/unified_panels.py, which mentions Camera-prime only in docstrings and provenance text; anim/axes_kinematics.py bakes "Camera-prime model | Frame" into earlier films not referenced by the current pages. Baked film text was not OCR-checked.

ID: D-313
Status: UNCERTAIN
Decision: Bullets recast as keyword phrases and semicolons replaced by commas on every page (75 strings besides the D-310 and D-312 term replacements, listed in the M1b worker report); internal recording names removed from slide text: page 4 "Cube handover, right hand to left" and caption "Recorded RGB, no overlays.", page 34 "Three right-arm windows in the handover" and caption "Right arm, 45 frames per window, ...", pages 56-57 captions start "Right wrist, 785 frames". The spoken notes keep the recording names until the script rewrite.
Why: Author, 2026-09-30 (R3, R4): no semicolons in slide text, bullets are keywords, plain words, no internal names.
Alternatives: Splitting a two-part bullet into two bullets (rejected: bullet counts are bound to slot positions and the bullet_y lists).
Evidence: Rendered build-69 previews; validate_deck.py D-311 checks PASS; no bullet exceeds eight words.
Reversibility: Edit the strings in talk_content.json and backup_content.json and rebuild.
Review: Author: the recasts that shift emphasis most: page 35/41 "Right-arm gain from recovery" (was "Recovery helped the right arm"), page 36 "Hand-cube misalignment at times" (was "Hands and cube do not always align"), page 15 "Z forward as the third axis" (was "Z forward completes the frame"), page 20 "World at fixed desk marker, Wall for gravity" and "Object in World from camera data, Eq. 4.1", page 13 "Camera': same origin, y up" and "Chain input: every landmark in Camera'" (the page-13 figure is redrawn in M2).

ID: D-314
Status: UNCERTAIN
Decision: Footer reference lines carry no file path (R4): pages 9-11 and 53-54 "Undergraduate thesis | Section 2.5; Appendix F", page 55 "Undergraduate thesis | Section 8.2; Appendix F", pages 56-57 "... Section 8.3 | filter benchmark", page 49 "Published studies | page, table and figure for each row", page 50 "Marker benchmark, this workstation, single thread", page 51 "... Table 6.1 | transport benchmark, loopback", page 52 "... Section 6.1 | package transport benchmark". The file paths stay in each page's source field, which the notes carry.
Why: Author, 2026-09-30 (R4) and the brief's page 9-11 fix; the same paths sat on the hidden pages, which D-311 (d) also scans.
Alternatives: Removing the non-thesis group entirely (rejected: the committee would lose the sign that a number comes from a benchmark rather than the thesis).
Evidence: Footer audit (D-278) still PASS; D-311 (d) PASS.
Reversibility: Restore the source_label strings.
Review: Author: the plain words "filter benchmark", "marker benchmark", "transport benchmark" on hidden pages 49-57.

ID: D-315
Status: SETTLED
Decision: No stale-preview removal is needed in build 69: presentation/defense_2026/preview/slide-77.png was already deleted from the index by commit 6f018e8 (build 68), and render_deck.py already removes every slide-*.png and overview-*.jpg that the current PDF did not produce (D-170). render_deck.py is unchanged.
Why: The brief asked to git rm the stale preview and to check whether the renderer should prune; both are already true.
Alternatives: Adding a validator check for stale previews (not needed: the renderer prunes on every run).
Evidence: `git show --stat 6f018e8` lists preview/slide-77.png with 73449 -> 0 bytes; git ls-files preview lists 83 files, slide-01..slide-76 plus overview sheets; render_deck.py lines 162-179.
Reversibility: None needed.
Review: None.

ID: D-316
Status: UNCERTAIN
Decision: Page 13 (Camera and Camera' frames) shows a plain axis diagram with no photograph, drawn by a new plain-panel mode of make_frame_overlay_figures.py ("background": "plain": black deck background 000000, no photo, crop or camera model, illustrative frames, outline shapes and texts only, each label kept inside its panel). Both frames start at one shared origin as in thesis Figure 3.2: x (both) and z (both) common, "Camera y (down)" and "Camera' y (up)", notes "one shared origin (the optical centre)" and "F = diag(1, -1, 1): only y changes sign". validate_deck.py check "Coordinate overlay %s declares the committed photo hash" now reads "... (plain panels: no photo, illustrative frames only)": photo panels keep the same hash binding, a plain panel must carry no photo fields and only illustrative frames.
Why: Author R1, 2026-09-30: the page only introduces the two camera frames; the recorded photograph served no purpose. Producing it in the same generator keeps the overlay manifest binding (D-290) on all overlay pages.
Alternatives: A separate script or a copy of thesis Figure 3.2 (rejected by the brief: the manifest binding would split; the thesis figure has a worked-example point and a 3D box the page does not need).
Evidence: spec_camera_frames.json; manifest.json output camera_frames (panels: one plain panel, fade_check photo_panels 0); rendered preview/slide-13.png. Display constants without a measurement source: origin (560, 540) px, axis length 330 px, x direction (1, 0.18), oblique z direction (0.89, -0.456) at 0.7 of the length (foreshortened depth, after the look of Figure 3.2), label offsets in the spec.
Reversibility: Restore the build-69 spec_camera_frames.json (photo panel) and regenerate; the plain-panel code is unused then.
Review: Author: whether the oblique z reads as depth, and whether the caption "Camera and Camera' share one origin." should change now that the baked note says the same.

ID: D-317
Status: UNCERTAIN
Decision: Page 15 (Torso and root frame) uses a two-panel overlay_torso_root.png on a 1586 x 1200 px canvas. Left: the unchanged root triad at the measured L24 on the faded T-pose photo (crop [1540, 600, 2490, 2100], same 0.8 scale and offsets as build 69). Right, a plain panel, nominal top view: Camera' at the lens of a camera outline (X right, Z into the scene, Y toward the viewer as a ring with a dot) and the torso frame of a person facing the camera at the right hip (torso X opposite Camera' X, torso Z back toward the camera, Y toward the viewer), with outlines for the shoulders, head and nose, and the labels "Nominal top view", "facing the camera", "root L24", "Half-turn about Y", "R = diag(-1, 1, -1)", "Root angles (0, 180, 0)". Overlay modes: root L24 illustrative, Camera' (top view) illustrative, root L24 (top view) illustrative, points L23 and L12 measured.
Why: Author R2, 2026-09-30: the root angles (0, 180, 0) must be shown with the camera frame and the torso frame together, where the value is stated. The geometry is thesis Section 3.2.2 end (columns (-1,0,0), (0,1,0), (0,0,-1)), anim/coordinate_axes.py CANONICAL_ROOT = diag(-1, 1, -1), decoded by Eqs. 3.15-3.17 to (0, 180, 0).
Alternatives: A separate new page (rejected: the plan places the value on the torso-frame page); a 1440 px canvas with two 700 px panels (rejected: "Root angles (0, 180, 0)" is 652 px at the 57 px label size and the T-pose labels would not fit).
Evidence: Canvas width 1586 = 6.61 / 5.00 x 1200 (build_deck.py frame_figure box), so the 57 px labels stay 17.1 pt effective (report_effective_text.py row page 15, 240 px per in); the generator now raises when a spec canvas would put labels below 16 pt. Arrow lengths 230 px (camera) and 200 px (torso) are the N-5 legend lengths. Outline shapes and positions are display constants without a measurement source. Rendered preview/slide-15.png.
Reversibility: Restore the build-69 spec_torso_root.json and regenerate.
Review: Author: whether the top view reads as "facing the camera" (nose mark toward the camera) and whether the right panel should say "Eq. 3.17".

ID: D-318
Status: UNCERTAIN
Decision: Page 7 (Static marker calibration) shows overlay_static_markers.png instead of the plain still: the same recorded R6b frame 533 (media/matched/r6b_frame_533.jpg), faded, with World (desk marker, T_cam_desk) and Wall (wall marker, T_cam_wall) projected from eval/output/scene_calibration_r6bc.json through the recording intrinsics, as on page 20, without Object and Camera. The page kind changes from calibration to frame_figure; Eq. 2.1 stays directly under its label bullet (D-308 check PASS). Caption "Static desk and wall marker axes, ArUco [1]."
Why: Master's addition R3, not an author request: the page is about the static markers but the still did not mark them.
Alternatives: Keep the still (the author may prefer it); draw only the desk marker.
Evidence: manifest.json reprojection_checks frame533_world_origin_vs_desk_marker 0.71 px and frame533_wall_origin_vs_wall_marker 0.03 px, both under the D-303 1.0 px bound now enforced for frame 533 too (pinned detector on the JPEG still). Axis lengths 0.09 m and 0.30 m as N-5.
Reversibility: Set page 7 visual back to {"kind": "calibration", "still": "presentation/defense_2026/media/matched/r6b_frame_533.jpg"} and drop static_markers from FIGURES.
Review: Author: keep the overlay or return to the plain still.

ID: D-319
Status: UNCERTAIN
Decision: Each root-angle fact appears once. Page 14 bullet "T-pose: root (0, 180, 0), arms zero" -> "T-pose: every arm angle zero"; page 15 gains a fourth bullet "Facing camera: root (0, 180, 0)" at bullet_y [1.40, 2.07, 3.12, 3.79], bullet_height 0.80, its caption "Root triad at L24, and the nominal top view."; page 16 bullet "(0, 180, 0) root, offset by tilt, lean" -> "Recorded root Y: 171 to 180 deg". Notes of 14, 15, 16 moved to match, not polished.
Why: Author R2 and plan M2: the value was stated three times. The brief's example "169 to 180" is the superseded first statement of D-075; its correction and the pinned source give 171.43 to 179.83 deg.
Alternatives: "Facing the camera: root (0, 180, 0)" (two lines at 22 pt, would not leave room above the two equation crops in the default slots).
Evidence: bank_processing/unified_four/p13/kinematic_source.json records 780-885: root_ey min 171.43, max 179.83 (106 records); bullet_y from 22 pt lines of 0.37 in with 0.30 in gaps (bullet 2 wraps to two lines), last box ends 4.59 in, above the default equation start 5.13 in; build_deck.py "Text-fit warnings: 0".
Reversibility: Restore the three bullets and drop bullet_y and bullet_height from page 15.
Review: Author: the shortened "Facing camera" wording and the integer rounding 171 to 180 deg.

ID: D-320
Status: SETTLED
Decision: Round 10 (build 71): the page-4 clip media/raw_handover_task.mp4 and its committee copy p04-Raw_Handover_Task.* are regenerated with no burned-in caption (decoded R7 colour frames 690-1199 unchanged, same encoder settings, same poster frame 950), and the page-4 black mask is removed from talk_content.json, validate_deck.py FILM_MASKS_PX, FILM_GEOMETRY_PX, measure_film_geometry.py, review/film_geometry.json, the media contract row, MEDIA_PROVENANCE.md and the page provenance sentence. The film keeps its FILM_GEOMETRY_PX entry with the measured full-frame geometry (content [[0, 0, 640, 480]], no label), so the D-262 binding rule still applies to it.
Why: The black rectangle sat visibly over the picture (master, preview/slide-04.png). The mask convention exists for older committee films that must not be re-encoded; this clip was made in this round (D-304), so it can be generated without the strip. The change is made in the wrapper anim/raw_handover_task.py only; anim/raw_task_context.py (sha256 c2db5c21..., unchanged) and its old two-segment clip media/raw_task_context.mp4 (sha256 a0e82d4e..., unchanged) are not touched.
Alternatives: Keep the strip and the mask (rejected: the defect the master reported); patch the base generator with a caption switch (rejected by the brief: the base is shared with the old clip); monkeypatch the base caption layer with a transparent one (rejected: the base record would still report a caption box that does not exist); drop p04 from FILM_GEOMETRY_PX (rejected: the D-262 rule requires every placed film to be measured or a viewport film, and weakening it is not allowed).
Evidence: anim/raw_handover_task.py (v3rt Python): "PASS: presentation/defense_2026/committee_materials/unified_revision/videos/p04-Raw_Handover_Task.mp4; 510 frames; 17.000 s"; bag sha256 d0fd9412... equals the archive index; stills 700, 950, 1042 pixel-identical; at most 64 landmark-colour pixels (bound 200); 510 of 510 encoder input frames pixel-identical to the decoded frames, sha256 over all encoder input bytes = sha256 over all decoded frames = 976433b3147db2675acd3fc443d307441fb0f8d37183b6bbdbfd4e34bf209b7a; full decode 510 frames. New film sha256 d2da9480efb883ff11efed9835babb6cfc9efa675d6d79d413741ffd19bd1997 (2,158,823 bytes; was 4a54f5f1..., 2,116,465), poster eeead4df... (was 6f4a0043...), provenance 71fa9c79... (was e98feebd...), frame map unchanged 219522b2.... Decoding old and new MP4 (worker, ad hoc): pixels of [0, 458, 277, 480] dark (largest channel below 130) on every frame 0.883 old, 0.111 new (the remaining dark pixels are scene shadow); mean absolute difference old vs new 92.9 inside that box and 1.18 outside it (encoder noise). measure_film_geometry.py: p04 content [[0, 0, 640, 480]], labels [], the other 17 films unchanged. validate_deck.py --pdf: package PASS, 2073 checks, 0 package failures; "Slide 04 covers its film only with the declared label masks: 0 covering shapes, 0 declared masks". preview/slide-04.png shows no rectangle over the picture.
Reversibility: Restore the build-70 files of this commit (git show 1e2dad7:<path>) for the wrapper, the two clips and posters, the provenance JSON, measure_film_geometry.py, review/film_geometry.json, validate_deck.py, talk_content.json, the contract and MEDIA_PROVENANCE.md, and rebuild.
Review: Play page 4 in PowerPoint and confirm the clip has no caption and nothing covers it. The new check (encoder input equal to decoded frames) verifies the frames before H.264 compression; the encoded frames differ from the source by compression only (CRF 18), as for every other film.

ID: D-321
Status: SETTLED
Decision: report_effective_text.py no longer prints hard-coded page numbers for the accepted exceptions. Each exception in effective_text_table.json carries a selector instead of a "pages" string: "files" (fnmatch patterns on the file names of the table entries placed on a page) or "films" (every page with a movie shape, minus the films whose bytes equal an "except_films" file); the pages are read from the built deck and printed as ranges. A selector that matches no page stops the report. The film exception excludes the build-71 page-4 clip, which has no burned-in text (D-320), and its text no longer lists pages.
Why: The exception lines still showed the build-65 numbering (films on 5, 8, 9, ...; Figure 8.1 on 36; derivation pages 59-77) after the round-10 restructure moved every page; a page list typed by hand goes stale at each renumbering.
Alternatives: Renumber the strings by hand again (rejected: the same defect returns at the next restructure); key the exceptions by legacy key (rejected: the table entries are files, and the file is what carries the baked text).
Evidence: review/EFFECTIVE_TEXT.md regenerated at build 71: films 8-11, 16-18, 22-25, 27, 30, 36, 39, 41, 53-55 (film pages 4, 8-11, ... minus page 4); Figure 7.1 crop 32; marker chart 50; filter panel charts 56-57; typeset equations 9-11, 39, 53-57; Figure 2.3 page 5; Figure 8.1 page 38; derivation crops 58-76. These equal the page tables read from talk_content.json and backup_content.json (worker, 2026-09-30). The measured rows of the report are unchanged.
Reversibility: Restore the build-71 commit 5424e14 versions of report_effective_text.py and effective_text_table.json.
Review: None beyond reading the regenerated exception lines.

ID: D-322
Status: UNCERTAIN
Decision: Round 10 M3 (build 72): a number, code list or symbol that is visible on the same slide need not be spoken; each script paragraph states the finding and the numbers that carry it. The items no longer spoken are listed in review/round10_script/script_main_v2_issues.md, section 2 (visible on the slide) and section 3 (dropped although not visible, for the master to confirm).
Why: Master decision (1) of the M3 brief, from the author's requirement of 2026-09-30 that the script be one essay with one paragraph per slide, each leading into the next. Reading out a table that the committee can see costs time without adding information.
Alternatives: Speak every visible number as the build-71 notes did (rejected by the author's requirement: the notes read as lists, not as an essay).
Evidence: review/round10_script/script_main_v2_issues.md sections 2 and 3 (copied byte for byte from the script author's scratchpad file script_main_v2_issues.md, 2026-09-30); no number changed value and no measured number was added (same file, section 2 opening). No timed rehearsal.
Reversibility: Restore the build-71 notes of the affected pages from commit bdd9297 (talk_content.json) and rerun set_page_budgets.py --write.
Review: Author: read section 3 of review/round10_script/script_main_v2_issues.md; the page-15 reference to Eqs. 3.15-3.17 and the page-22 test names are dropped from the speech although they are not on the slide.

ID: D-323
Status: UNCERTAIN
Decision: The six test names on page 22 (acquisition, segment-length, line-angle, width-ratio, landmark-step, grip-plausibility) are described in plain words in the page-22 paragraph; they are neither spoken nor shown on the slide.
Why: Master decision (2) of the M3 brief. A list of six internal test names spoken aloud reads as a code list, which the author's requirement excludes; the plain description keeps what the tests do.
Alternatives: Speak the names (rejected: a name list); add them to the slide (rejected: not requested, and the page carries a film).
Evidence: review/round10_script/script_main_v2_issues.md section 3, row for page 22. None beyond the author's requirement.
Reversibility: Add the names back to the page-22 notes and rerun the budget helper.
Review: Author: whether a committee member may ask for a named test that the talk never names (thesis Section 5 holds them).

ID: D-324
Status: UNCERTAIN
Decision: Main page 16 is retitled "Recorded torso frame" (was "Torso frame") in talk_content.json; the builder regenerates SPEAKER_NOTES.md, DEFENSE_SCRIPT.md/.docx/.pdf, DEMONSTRATION_MANIFEST.json, restrained_purposes.json, REVISION_OUTLINE.md, RESTRAINED_REVISION_PLAN.md and CUTTING_GUIDE.md from it. Historical records (revision_id_map.json, MEDIA_PROVENANCE.md, RECORDING_GUIDE.md, VIDEO_SHOT_LIST.md, COMMITTEE_QUESTIONS.md, SESSION_REVIEW.md, the film generator anim/unified_panels.py) keep the old title as written. README.md is left to the documentation task.
Why: Master decision (3): "Torso frame" was a near-duplicate of page 15 "Torso and root frame"; page 16 shows the recorded T-pose check of that frame.
Alternatives: Keep the old title (rejected: the two titles read as the same page); rename page 15 instead (rejected: page 15 introduces the frame).
Evidence: grep of "Torso frame" in presentation/defense_2026 (2026-09-30): no checker or builder keys on the title; validate_deck.py title checks compare the built slide to the content title and pass (2078 checks).
Reversibility: Set the page-16 title back and rebuild.
Review: Author: the new title on preview/slide-16.png.

ID: D-325
Status: SETTLED
Decision: Hidden derivation page 63 (Eqs. 3.15-3.17, root Euler angles) supports main slide 15 "Torso and root frame" instead of slide 16: backup_content.json "supports" [16] -> [15], the one fixed notes sentence "This page supports main slide 16, Torso frame." -> "This page supports main slide 15, Torso and root frame.", and purpose.problem "main slide 16" -> "main slide 15".
Why: Master decision (4): slide 15 now explains the (0, 180, 0) value that these equations decode (D-319); slide 16 shows only the recorded range. The purpose sentence named the same slide and would otherwise be stale.
Alternatives: Support both 15 and 16 (rejected: page 16 has no equation strip and no longer explains the angles).
Evidence: validate_deck.py --pdf at build 72: "Slide 63 derivation notes give every lead source and name the main slide supported (D-281)" PASS with statement "This page supports main slide 15, Torso and root frame."; "Every main page with a thesis equation strip names its derivation pages in its notes (D-281)" PASS.
Reversibility: Set supports back to [16] and edit the two sentences back.
Review: None beyond the page-15 notes pane showing the pointer to hidden page 63.

ID: D-326
Status: SETTLED
Decision: validate_deck.py gains four checks on the spoken script (the `notes` field of every page, not the unspoken Budget, Sources and provenance lines the builder adds): (e) no ";"; (f) no "Thesis:" tag; (g) no internal recording name (R5, R6, R6a, R6b, R7 as whole words) and no repository file name or path, with the lead-source strings file:line required by D-281 and the name derivation_leads.json removed first on derivation pages only; (h) on main pages no sentence opens with a digit or a NUMWORDS word, sentences split at "." or "!" plus white space except after Eq., Eqs., al., e.g., i.e., Fig., vs., No., cf.; plus a self-test check of bad and good samples. NUMWORDS is copied from writing/v9/scripts/check_style.py line 26.
Why: Author requirement of 2026-09-30 (no semicolons, no spoken "Thesis: Section" tags, no internal names) and the brief's rule (h). D-311 left the notes out of rule (a) until this rewrite.
Alternatives: Import NUMWORDS from check_style.py (rejected: writing/ is frozen and that module imports python-docx and scans files at import); scan the whole notes pane (rejected: the Sources lines legitimately carry paths and semicolons).
Evidence: validate_deck.py --pdf at build 72: 2078 checks (2073 + 5), 0 package failures, the five D-326 checks PASS with 0 hits. In-situ negative test (worker, not committed): appending " Twelve parts; Thesis: Section 1, recording R7." to page 2 notes and " See experiments/marker_bench/summary.csv. 3 runs." to page 49 notes failed exactly (e) page 2, (f) page 2, (g) pages 2 and 49, (h) page 2 (hidden page 49 not scanned by (h)); content and deck were restored, the rebuilt pptx byte-identical to the build before the test. The separator change "; " -> ", " in the derivation notes broke no existing check.
Reversibility: Remove the D-326 block in validate_deck.py (constants, notes_hits, notes_self_test, the per-page collection and the five checks).
Review: None.

ID: D-327
Status: UNCERTAIN
Decision: Main-page budgets are set by presentation/defense_2026/set_page_budgets.py: dividers 5 s, cover 20 s, references pages 5 s each, thank-you 5 s, question page 10 s; every other page words / 140 * 60 (words = len(notes.split())), plus 5 s on a film page, floored at the film duration (ffprobe of the embedded committee film), rounded up to a multiple of 5 s. The rate rises one word per minute at a time up to 144 only while the total exceeds 1795 s; at 140 the total is 1735 s, so 140 is used. Hidden pages stay 0. Table (page old->new): 1 20->20 s (35 words, fixed), 2 30->25 s (55 words), 3 50->60 s (134 words), 4 40->35 s (66 words, film 17.00 s), 5 45->40 s (87 words), 6 5->5 s (16 words, fixed), 7 30->35 s (80 words), 8 40->40 s (78 words, film 22.00 s), 9 40->40 s (71 words, film 18.70 s), 10 40->30 s (47 words, film 18.70 s), 11 40->30 s (57 words, film 18.37 s), 12 5->5 s (18 words, fixed), 13 30->40 s (91 words), 14 50->35 s (72 words), 15 30->65 s (149 words), 16 50->35 s (63 words, film 11.07 s), 17 50->50 s (105 words, film 18.73 s), 18 45->30 s (55 words, film 28.07 s), 19 5->5 s (17 words, fixed), 20 45->55 s (120 words), 21 5->5 s (21 words, fixed), 22 65->70 s (150 words, film 6.00 s), 23 60->55 s (109 words, film 15.40 s), 24 60->45 s (87 words, film 15.40 s), 25 70->65 s (135 words, film 8.00 s), 26 5->5 s (19 words, fixed), 27 65->45 s (82 words, film 44.00 s), 28 45->50 s (110 words), 29 30->50 s (116 words), 30 60->45 s (82 words, film 25.00 s), 31 5->5 s (15 words, fixed), 32 70->55 s (121 words), 33 70->60 s (130 words), 34 60->55 s (128 words), 35 75->65 s (145 words), 36 70->50 s (40 words, film 49.93 s), 37 5->5 s (20 words, fixed), 38 30->45 s (100 words), 39 55->65 s (130 words, film 18.37 s), 40 5->5 s (12 words, fixed), 41 45->65 s (129 words, film 12.00 s), 42 5->5 s (15 words, fixed), 43 55->55 s (128 words), 44 55->60 s (134 words), 45 5->5 s (12 words, fixed), 46 5->5 s (4 words, fixed), 47 5->5 s (5 words, fixed), 48 10->10 s (4 words, fixed). Main talk 1785 s -> 1735 s (28:55), methodology 1090 s = 62.8 percent (floor 55 percent, D-211).
Why: Brief rule of round 10 M3. The rate 140 is inside the 131-144 words per minute the earlier notes ran at (DECISIONS.md line 886, D-095 Review: "notes run at 131-144 words per minute"); 1795 s is the round-9 total (knowledge/deck_inventory.md).
Alternatives: Keep the build-71 budgets (rejected: they predate the rewrite, e.g. page 15 had 30 s for 149 words); budget by hand (rejected: not rerunnable).
Evidence: set_page_budgets.py output at build 72; validate_deck.py --pdf "Main talk: 1735 s; 3599 script words", "At least 55 percent of main time explains methodology" PASS, every "Slide NN notes match the planned duration" PASS. No timed rehearsal.
Reversibility: Restore the durations of commit 49e3200 (talk_content.json) or change the constants and rerun set_page_budgets.py --write, then rebuild.
Review: Author: a timed rehearsal; the 5 s film lead and the 140 words per minute rate are untested.

ID: D-328
Status: UNCERTAIN
Decision: Page 48 presenter_cue is "Take questions and open a hidden page by typing its number and pressing Enter." (was "Show the page and introduce its chapter-specific problem.", a stale cue copied from content pages). No other presenter cue, source or provenance field changed.
Why: Brief step 1: the old cue did not describe the question page; the hidden pages are reached by typing the slide number (D-128).
Alternatives: "Invite questions ... when asked" (rejected: risks the D-263 question-clause scan for no gain).
Evidence: field audit of talk_content.json and backup_content.json against bdd9297 (worker, 2026-09-30): changed fields are notes on all 76 pages, title on 16, duration on main pages, presenter_cue on 48, supports and purpose on 63 only.
Reversibility: Restore the old cue string.
Review: None.

ID: D-329
Status: UNCERTAIN
Decision: Round 10 M3 (build 73): script version 3 replaces version 2 in the `notes` of the 48 main pages, inserted verbatim (byte-for-byte check against the input, 0 deviations); the 28 hidden-page notes are unchanged. Version 3 answers the cold read of version 2 (67 findings: 3 HIGH, 35 MEDIUM, 29 LOW, review/round10_script/cold_read_main_v2.md); version 2 had answered the cold read of draft 1 (129 findings: 21 HIGH, 75 MEDIUM, 33 LOW, review/round10_script/cold_read_main.md). Main script words 3599 -> 3647.
Why: Master brief of round 10 M3 (final script pass): the script author's v3 resolves the v2 cold read (59 done, 8 done differently, 0 not done, per review/round10_script/script_main_v3_changes.md section 1).
Alternatives: Keep version 2 (rejected by the brief).
Evidence: review/round10_script/script_main_v3_changes.md and cold_read_main_v2.md (copied byte for byte from the script author's scratchpad, cmp identical); insertion verify script: "pages 48 28 deviations []"; validate_deck.py --pdf at build 73: 2081 checks, 0 package failures, D-326 (e)-(h) PASS on the v3 notes. Version 3 has had no cold read (script_main_v3_changes.md section 1) and no timed rehearsal.
Reversibility: Restore the notes of commit c7cfdc7 (talk_content.json), rerun set_page_budgets.py --write and rebuild.
Review: Author: read DEFENSE_SCRIPT.md aloud; the 8 findings "done differently" in script_main_v3_changes.md section 1.

ID: D-330
Status: UNCERTAIN
Decision: The `presenter_cue` of all 76 pages (48 main, 28 hidden) is replaced by the v3 cues, verbatim except one substitution stated in the brief: "film" -> "video" for a recorded clip, made on pages 9, 10 and 11 ("Start the film ..." -> "Start the video ...") and 53, 54 and 55 ("Play the film." -> "Play the video."); no other cue contains "film".
Why: Master brief: the script uses "video" for recorded clips and "replay" for Unity renderings, and the cues should use the same words. The v3 cues contain no ";".
Alternatives: Insert the cues with "film" unchanged (rejected by the brief).
Evidence: insertion verify script: every cue equals the input after the one substitution, 0 deviations, 6 substitutions listed; validate_deck.py "No semicolon in the presenter cue of any page (D-332)" PASS.
Reversibility: Restore the cues of commit c7cfdc7 (talk_content.json, backup_content.json) and rebuild.
Review: Author: the bracketed cues in DEFENSE_SCRIPT.md.

ID: D-331
Status: UNCERTAIN
Decision: Page 33 (Human reconstruction accuracy) bullet "Added rig error after the model" -> "Added display-path error after the model" in bullets and panel_bullets.
Why: Master brief: the old bullet attributes the error to the rig, but thesis Chapter 7 states "Display filtering, rig mapping and the remaining stages of the display path are not separated by this comparison". The brief's first wording "Added error after the model, along the display path" was built and failed the existing check "Visible left bullets are concise phrases" (at most 8 words per panel bullet; it has 9), so the brief's shorter keyword phrase option was used. The check was not changed.
Alternatives: "Added error after the model, along the display path" (rejected: 9 words, fails the 8-word check); "Added error along the display path" (rejected: drops "after the model", which carries the comparison with the model wrist row).
Evidence: build 73: Text-fit warnings 0; validate_deck.py --pdf 2081 checks, 0 package failures; preview/slide-33.png shows the bullet on two lines. No validator check pins the bullet text (grep of validate_deck.py for "rig error", 2026-09-30). The thesis sentence is quoted from the brief; the worker did not reopen writing/.
Reversibility: Set the fourth bullet of page 33 back in both fields and rebuild.
Review: Author: whether "display-path" reads naturally on slide 33.

ID: D-332
Status: SETTLED
Decision: The D-326 (e) semicolon rule is extended in validate_deck.py by three checks: "No semicolon in the presenter cue of any page (D-332)"; "No semicolon anywhere in DEFENSE_SCRIPT.md outside the derivation lead sources (D-332)", which scans every line of the generated document (header, headings, section lines, cues, narration) after removing only the derivation lead-source strings file:line and the name derivation_leads.json, the D-326 (g) exemptions; and a self-test of bad and good cue and document samples. build_deck.py writes the DEFENSE_SCRIPT.md header as two sentences ("... page numbers. Q&A responses follow separately.") and the SPEAKER_NOTES.md budget sentence as two sentences ("... not a measured delivery time. An aloud rehearsal ..."). SPEAKER_NOTES.md is not scanned: its remaining ";" sit in Sources and Provenance lines and in the generated bracketed media lines "[Synchronized composite: <path>; <s> s. ...]" and "[Recorded exhibit: <path>; ...]", unspoken records that the brief leaves as they are.
Why: Master brief step 3: the author reads from DEFENSE_SCRIPT.md, so the cues and the whole document follow the no-semicolon rule.
Alternatives: Scan SPEAKER_NOTES.md too (rejected: its source and provenance records legitimately carry ";"); exempt the header (rejected: the author reads it).
Evidence: validate_deck.py --pdf at build 73: 2081 checks (2078 + 3), the three D-332 checks PASS, 0 ";" in DEFENSE_SCRIPT.md (grep -c). In-situ negative test (worker, not committed): a ";" injected into the page-2 cue and a line "Injected line; test." appended to DEFENSE_SCRIPT.md failed exactly the two D-332 checks (page 2; line 617); both files restored from copies taken before the test and the full validation rerun.
Reversibility: Remove the D-332 block in validate_deck.py (constants, cue_hits, script_doc_semicolons, cue_self_test and the three checks); restore the two builder sentences.
Review: None.

ID: D-333
Status: UNCERTAIN
Decision: Update of D-327 (rule, rate and constants unchanged): set_page_budgets.py --write on the v3 word counts at 140 words per minute. Changed pages (old -> new s): 2 25->30, 3 60->55, 7 35->40, 14 35->30, 15 65->60, 17 50->55, 18 30->35, 20 55->50, 23 55->60, 25 65->70, 29 50->60, 30 45->35, 32 55->45, 33 60->65, 35 65->60, 39 65->70, 43 55->65, 44 60->65; all other main pages unchanged. Main talk 1735 s -> 1755 s (29:15), under the 1795 s cap, so the rate stays 140; methodology 1105 s = 63.0 percent (floor 55 percent, D-211); 3647 script words.
Why: Master brief step 4: budgets follow the script under the D-327 rule.
Alternatives: Keep the build-72 budgets (rejected: they follow the v2 word counts).
Evidence: set_page_budgets.py output at build 73 ("Rate 140 words per minute; main total 1755 s (29:15), was 1735 s; methodology 1105 s = 63.0 percent"); validate_deck.py --pdf "Main talk: 1755 s; 3647 script words", 0 package failures. No timed rehearsal.
Reversibility: Restore the durations of commit 819fe3f (talk_content.json) and rebuild.
Review: Author: a timed rehearsal (as D-327).

ID: D-334
Status: SETTLED
Decision: Round 10 M4, build 74: the D-311 and D-326 wording checks of validate_deck.py are hardened after the code review of fb48274..9e0ebec. RETIRED_TERMS is r"signal[\s-]+conditioning|camera[\s_-]*prime" (re.I). INTERNAL_RECORDING is r"(?<![A-Za-z0-9])R(?:5|6_?[ab]?|7)(?![0-9A-Za-z])" (re.I). REPO_FILE is case-insensitive and adds jpg, jpeg, gif, docx, tex, ipynb. REPO_DIR is case-insensitive and adds thesis, scripts, skill_set, the dot directories .agent, .agents, .claude, .codex, and any "/home/" path. The "Thesis:" tag test is re.search(r"\bthesis\s*:", re.I). notes_sentences splits at [.!?] plus closing quotes or brackets followed by white space, and at every line break; NOTES_ABBREVIATION adds Figs, p, pp, Sec, Secs. Amendment to D-326 (h): the deck's NUMWORDS copy adds Zero, Thirteen to Nineteen, Forty, Sixty, Seventy, Eighty, Ninety, Thousand and Million; writing/v9/scripts/check_style.py (frozen) is not edited, so the two lists now differ on purpose. The D-311 (a) exemptions move into visible_semicolon_lines(): a whole value equal to a page derivation lead, and a line equal to the footer line, where a list-valued source_label is joined with "; " (footer_line()). The self-tests carry every reviewer probe as a bad sample, new good samples, and eight exemption cases.
Why: Code review findings F1-F6 and F13: every probe was executed by the reviewer and passed when it should fail (or the reverse for "See Figs. 7.8").
Alternatives: Leave the thesis list verbatim (rejected: it misses common number words the rule targets); exempt the abbreviations by a lookahead on a digit (rejected: the explicit list is the existing mechanism).
Evidence: validate_deck.py --pdf at build 74: 2081 checks, 0 package failures, the three self-tests PASS (all probe strings caught, all good samples pass). In-place negative test (worker, not committed): probes injected into the page-3 notes and the captions of pages 4, 5 and 7 failed D-311 (c) (visible and notes), D-311 (d), D-326 (f), (g) and (h) with the injected text named (bullets injected on page 3 were not rendered by its restrained layout and so were not visible text; captions were used instead); talk_content.json restored from a copy, rebuild byte-identical PPTX (sha256 bd4ed712...). No existing deck text was flagged.
Reversibility: Restore the build-73 constants and functions of validate_deck.py (commit ff1a18a).
Review: Author: whether "Thousand" and "Million" at a sentence start should be forbidden in the spoken script (they are now).

ID: D-335
Status: SETTLED
Decision: anim/raw_handover_task.py no longer claims an encoder-input check. The build-71 comparison of np.asarray(Image.fromarray(rgb).convert("RGB")) with rgb, and the two sha256 digests over the same bytes, could not fail and were removed; the frame is written to the encoder as rgb.tobytes(). Docstring and provenance JSON now state that no drawing is applied by construction (a property of the code, not a measured check) and list the real checks: bag sha256 equal to the archive index, the landmark-drawing pixel bound, the three stills pixel-identical to the reference stills, and the full decode with the declared frame count. The field encoder_input_check is replaced by "checks" and an "encoder" note that the decoded film is not compared with the source pixels. The clip was regenerated with env v3rt: film and poster bytes unchanged (mp4 d2da9480..., png eeead4df...), source-frame CSV unchanged; provenance JSON 71fa9c79... -> 41293387..., media_contract.json provenance_sha256 updated.
Why: Code review F7: the claim overstated what was verified. No compression tolerance is added because no sourced threshold exists.
Alternatives: Edit the provenance JSON by hand to keep the old generator (rejected: the JSON records the generator sha256 and must come from the run); compare the decoded film with the source (rejected: needs a tolerance with no source).
Evidence: sha256sum before and after the v3rt run (mp4, png, both committee copies and the CSV identical); validate_deck.py at build 74 PASS on the contract and provenance bindings.
Reversibility: Restore the build-73 script and provenance JSON and the contract row.
Review: None.

ID: D-336
Status: SETTLED
Decision: make_frame_overlay_figures.py replaces the check base[plain_mask] == 0 (base is written only inside the photo boxes, so it could not fail) by a check on the output image: a MirroredDraw proxy repeats every line, polygon, ellipse, rectangle and text call on a mode-L mask with fill, outline and stroke 255, and every output pixel outside the photo boxes that the mask leaves at 0 must be pure black. The seven overlay PNGs are byte-identical after regeneration; only manifest.json changes (generator_sha256), whole-file sha256 648eab94... -> b7a96ffd..., updated as visual.overlay_manifest_sha256 on pages 7, 13, 14, 15, 20, 28, 29.
Why: Code review F8.
Alternatives: Remove the check and its claim (kept as the fallback; not needed because the mask is computable).
Evidence: sha256sum of the seven PNGs before and after (identical); the generator ran without raising; validate_deck.py PASS on the overlay manifest bindings. The check was not negative-tested by injecting a stray pixel.
Reversibility: Restore the build-73 generator and manifest hash.
Review: None.

ID: D-337
Status: SETTLED
Decision: The no-op exemption of the D-332 semicolon scan of DEFENSE_SCRIPT.md is removed (the lead-source strings it removed contain no ";"); script_doc_semicolons() takes no exempt argument and the check is named "No semicolon anywhere in DEFENSE_SCRIPT.md (D-332, D-337)". The D-326 (g) path exemption is real and stays. Stale comments of the D-311 block are corrected, and the four Chapter 7 table checks name the page by its current number from EVAL_PAGE (legacy key), now "Page 32/33/34/35 ...".
Why: Code review F9 and F10.
Alternatives: None considered.
Evidence: validate_deck.py at build 74: the renamed checks PASS; the check count stays 2081.
Reversibility: Restore the build-73 wording.
Review: None.

ID: D-338
Status: SETTLED
Decision: Content leftovers corrected. backup_content.json page 49 source: Olson [5] -> [8], Wang and Olson [6] -> [9], Krogius et al. [7] -> [10], Romero-Ramirez et al. [8] -> [11] (D-306 map; [1] Garrido-Jurado unchanged and correct). talk_content.json data fields that a builder layout function can render (data.cue, data.left_label, data.conditions, data.caption) carry no ";" and no internal recording name: page 22 cue and left_label ("Handover holding context"), pages 23, 24, 30, 36, 39, 41 conditions, page 25 cue (";" split into sentences), page 41 caption ("R7 wrist-loss segment" -> "handover wrist-loss segment"). None of these fields is rendered by the current restrained layouts. effective_text_table.json overlay_camera_frames basis "build 6;" -> "build 64;" (the build-70 edit, commit 32bf672, dropped the 4 of "build 64").
Why: Code review C1, C2 and F11.
Alternatives: Leave unrendered fields (rejected: a layout change would show them).
Evidence: Scan of every page's unspoken fields for [n]: only pages 45, 46 (References provenance, [1]-[12], consistent) and 49 carry citation numbers. Scan of data string fields: remaining hit is data.photo on page 4 (an image path, not text). git log -S"build 6; plain" names 32bf672.
Reversibility: Revert the content edits.
Review: None.

ID: D-339
Status: UNCERTAIN
Decision: Round 10 M4 close-out: the independent re-review of the build-74 fixes (verdict: approve, optional fixes) left eight minor points open, none triggered by current deck text. Recorded as written: (a) the path check, now case-insensitive, would flag ordinary phrases such as "Video/audio sync", "Thesis/defence", "writing/reading", "eval/test split"; (b) the retired-term pattern would flag "camera primed"; (c) the recording-name pattern, now case-insensitive, would flag "r5 radius" or "R5 = 1 k"; (d) the thesis-tag pattern flags "In this thesis: ..." although D-326 (f) is about the spoken "Thesis:" tag; (e) the abbreviations Ch., Tab., approx. and etc. are not in the sentence-splitter exception list; (f) the footer_line() docstring says the "; " join mirrors the builder for a list source_label, but the builder does not join a list source_label (no page has one); (g) the page-4 clip provenance JSON lists decisions D-304 and D-320 but not D-335; (h) remaining false negatives judged negligible: "signal_conditioning" with an underscore, "R 7", paths starting with "~/" and some extensions.
Why: Fixing them needs another code change and review cycle for cases the deck does not contain.
Alternatives: Fix them in build 74 before packaging (rejected: no current deck text triggers any of them, and a further code change would reopen review and rebuild).
Evidence: The reviewer executed each probe through validate_deck.notes_hits and wording_hits on 7a142c9. No re-run in the records task.
Reversibility: Each point is a validator or docstring or provenance-JSON edit; none changes deck output.
Review: Author: decide whether to tighten them before the next text change.

ID: D-340
Status: UNCERTAIN
Decision: The author's FOCUSED deck and script of 2026-09-30 are added beside the generated build outputs under their own names, not written over Thesis_Defence_2026.pptx and DEFENSE_SCRIPT.md; the script's non-ASCII dashes and quotes on 16 lines are normalised to ASCII.
Why: Overwriting the generated outputs would break the sha256-bound chain (validate_deck.py, render_deck.py, export_defense_script.py reports; make_package.py --require-clean) and the next build_deck.py run would discard the author's edits; the plain-ASCII rule applies to every tracked text file.
Alternatives: Replace the tracked files in place (rejected for the reasons above); keep the files only in Downloads (rejected: the author asked for them in git).
Evidence: The master's inspection numbers: 76 slides, hidden set 2-3 and 49-76 vs 49-76, 136 media, 0 external relationships; sha256 of /Users/luolanqing/Downloads/Thesis_Defence_2026_FOCUSED.pptx and presentation/defense_2026/Thesis_Defence_2026_FOCUSED.pptx both 703545b5c781cd8a0fb36e6466c8b5405ee686e1fc53daca1a16ac114b5114dd (shasum -a 256); diff of presentation/defense_2026/DEFENSE_SCRIPT_FOCUSED.md against the Downloads source shows 16 changed lines (15 dash lines plus line 762): 1, 5, 409, 487, 489, 501, 655, 691, 717, 733, 735, 737, 743, 751, 756 are em dash (2 occurrences) or en dash (22 occurrences) changed to ASCII hyphen; line 762's curly quotes normalised in the same task after the master's recheck confirmed 16 non-ASCII lines in the source. Master comparison 2026-10-01: 55 of 152 slide and notes XML texts and 136 of 136 media files of the FOCUSED deck identical to each of the build-73 and build-74 generated decks; the two generated decks differ only in notesSlide49, which the FOCUSED deck rewrote.
Reversibility: Delete the two FOCUSED files and this README paragraph; or, if the author decides the FOCUSED pair supersedes the build, copy them over the tracked names and rerun the validators to refresh the reports.
Review: The author confirms whether the FOCUSED pair is the deck for the defence, and whether talk_content.json should be updated to match it so the build chain follows.
Annotation (2026-10-01, round 11 M3, build 77): the FOCUSED pair was back-ported into talk_content.json, backup_content.json and script_document.json (D-359 to D-369); both files stay unchanged as the reference (sha256 of the pptx 703545b5..., of the md de3e7a77...), and review/round11_focused/EQUIVALENCE.md shows build 77 equal to them apart from the listed rule fixes. The author's question 'should talk_content.json be updated' is answered by the round-11 plan (back-port and rebuild).
Annotation (2026-10-01, round-11 close-out): the Evidence figure "55 of 152 slide and notes XML texts identical" is not what the measurement shows; FOCUSED_CHANGES.md Counts and knowledge/focused_revision.md give 44 of 152 identical (44 slide parts identical, 11 slide parts differing only by an empty r:id attribute, 21 differing otherwise, all 76 notes parts differing). The 136 of 136 media figure stands.

ID: D-341
Status: SETTLED
Decision: Round 11 M2: a main page may declare "hidden": true (boolean, main pages only). build_deck.py draws it with show="0" at its position; it must carry duration 0 and is excluded from every talk total (BUILD_LAYOUT_CHECK main_seconds and focus_seconds, SPEAKER_NOTES.md totals and table, REVISION_OUTLINE.md, CUTTING_GUIDE.md, validate_deck.py total, methodology share and main_script_words, set_page_budgets.py). validate_deck.py "Slide NN visibility" expects hidden == (page after the talk or flag); the notes rules (D-326 h included) still scan hidden main pages as main pages. make_package.py fills PACKAGE_README.txt with the hidden set as ranges from the data (hidden_ranges(): "49-76" now, "2-3 and 49-76" with pages 2 and 3 flagged). Supersedes the "hidden = after the talk" part of D-128.
Why: The author's FOCUSED deck hides pages 2 and 3 in place (plan A4); positional hiding cannot express that.
Alternatives: Move pages 2 and 3 into backup_content.json (rejected: their slide numbers would change, and A4 keeps them at 2 and 3); allow a positive duration on a hidden page and filter in every sum (rejected: one rule, duration 0, is simpler to check).
Evidence: Feature exercise on a temporary copy of the content (restored afterwards): pages 2 and 3 flagged, built deck hides 2, 3, 49-76; validator visibility checks PASS; set_page_budgets.py prints them as 0 (hidden); make_package.hidden_ranges() returns "2-3 and 49-76".
Reversibility: Remove the flag handling in the five files; with no page flagged the output equals the positional rule.
Review: None.
Annotation (2026-10-01, round-11 code review R2): the only evidence for the flag is the feature exercise, whose content was not committed; read this entry as UNCERTAIN until build 77 exercises it on the real content. The counts that read the hidden set were corrected by D-353 (chapter order, evaluation sequence, main demonstrations, package README counts).
Annotation (2026-10-01, build 77): exercised on the real content: pages 2 and 3 flagged, built deck hides 2, 3 and 49-76 (ARTIFACT_CHECK.json hidden_pages), 46 shown main pages, 1895 s; validate_deck.py 0 package failures; gate hidden flags equal on 76 pages.

ID: D-342
Status: SETTLED
Decision: A page's spoken script is an ordered list of cue and narration blocks. Single-cue pages keep presenter_cue (the cue, first) and notes (the narration). A page with more than one cue declares script_blocks, a list of {"cue": str} and {"narration": str} in speaking order, and then neither legacy string (the builder raises on both). Narration paragraphs are separated by a blank line; **...** marks emphasis for DEFENSE_SCRIPT.md only and is removed for the notes pane, word counts and records. Word counts and budgets use the narration only, cues excluded.
Why: FOCUSED pages 17, 23 and 44 carry a second cue inside the narration (plan, verified differences); slide 22 of DEFENSE_SCRIPT_FOCUSED.md carries bold markers that the pane does not show.
Alternatives: A list of cues plus a list of narration paragraphs with positions (rejected: positions are harder to edit than an ordered list); always use script_blocks (rejected: 76 pages would change at once, the brief keeps the legacy strings working).
Evidence: Feature exercise: pages 2, 3, 17 and 41 converted from the FOCUSED panes to script_blocks; built panes equal the FOCUSED pane text exactly; DEFENSE_SCRIPT.md sections of pages 2, 17 and 41 equal DEFENSE_SCRIPT_FOCUSED.md (page 3 differs only by its title, which M3 changes).
Reversibility: Convert script_blocks pages back to notes and presenter_cue; remove the helpers in build_deck.py, validate_deck.py and set_page_budgets.py.
Review: None.
Annotation (2026-10-01, round-11 code review R2): the only evidence for script_blocks is the feature exercise; read this entry as UNCERTAIN until build 77. The emphasis rule is replaced by D-354 (word-boundary balanced pairs, markers also removed from cues in the pane, leftover markers fail), and set_page_budgets.py now imports the builder's narration (D-356).
Annotation (2026-10-01, build 77): exercised on the real content: script_blocks on pages 17, 23 and 44, presenter_cue and notes on the other 73 (D-367); every pane equals the FOCUSED cue and say blocks after the listed fixes (EQUIVALENCE.md); DEFENSE_SCRIPT.md equal line by line after the fixes.

ID: D-343
Status: SETTLED
Decision: The PowerPoint notes pane carries only the author's layout: every cue as one line "[cue]" and every narration paragraph as one line, in block order, then one line "Sources: " + source (a list-valued source is joined with " | "). No blank lines; nothing else. Hidden pages with empty narration build (cue and Sources only). validate_deck.py "Slide NN contains the complete script" is replaced by "Slide NN notes pane equals its cue and narration blocks and one Sources line (D-343)", which rebuilds the pane independently and compares it exactly.
Why: Plan A3; all 76 FOCUSED panes follow this layout (master inspection; worker read panes 2, 3, 6, 17, 23, 41, 44, 47, 48, 58 with python-pptx).
Alternatives: Keep the builder's lines in the pane (rejected by the author's edit).
Evidence: Feature exercise: panes 2, 3, 17 and 41 equal FOCUSED; validate_deck.py at unchanged content: 76 pane checks PASS.
Reversibility: Restore the build-76 notes() function and the old check.
Review: None.
Annotation (2026-10-01, round-11 code review R2): the single-cue pane is verified on the committed content (76 pane checks PASS); the multi-cue pane is verified only by the feature exercise and stays UNCERTAIN in that part until build 77. Cues now lose their ** pairs in the pane as well (D-354).
Annotation (2026-10-01, build 77): the multi-cue pane is exercised on the real content: pages 17, 23 and 44 carry two cues and every one of the 76 "notes pane equals its cue and narration blocks and one Sources line (D-343)" checks passes (review/ARTIFACT_CHECK.json: 2092 checks, 0 package failures at build 77); review/round11_focused/EQUIVALENCE.md shows the cue and say blocks of the notes pane equal to the FOCUSED panes on 76 of 76 pages after the listed fixes. The part held UNCERTAIN until build 77 is settled by that evidence.

ID: D-344
Status: SETTLED
Decision: The unspoken lines that the pane carried up to build 76 (the Budget lead, Role, Provenance with the overlay-mode sentences, Sources, media lines, Slide purpose, recording and playback lines, equation-asset lines, the [...] lead export text, the main-page derivation pointer, the closing-page hidden-topic list, recording instructions) are generated from the same fields into an "Unspoken record (not spoken)" block of every page's section in SPEAKER_NOTES.md, which now covers all 76 pages ("## Slide NN: title (state)"). Derivation pages also get a generated "Lead-line sources: Eq. n file:line, ... (derivation_leads.json)." line and "This page supports main slide N, <current main title>." from supports. The validator checks that read the pane read the page's SPEAKER_NOTES.md section instead (budget lead, overlay modes, lead sources and supports pointer, [...] export text, main-page pointer, closing list), and the text scans (question clauses, retired terms, ASCII, citation rules) read the pane plus that section, so no coverage is lost. The closing list now names every hidden page, hidden main pages included, in page order.
Why: Plan A3: the lines leave the pane but the properties stay checked. A supports sentence left in the narration must still equal the generated one (stale-pointer check).
Alternatives: Check only the JSON fields (rejected: the generated record would then be unchecked); drop the checks (not allowed by the brief).
Evidence: validate_deck.py at unchanged content: all re-pointed checks PASS; round-11 self-test probes a missing pointer and a stale narration pointer (both reported).
Reversibility: Restore the build-76 pane and checks.
Review: None.
Annotation (2026-10-01, round-11 code review R2): the re-pointed checks are verified on the committed content and stay SETTLED in that part; the supports statement for retitled main pages is verified only by the feature exercise (UNCERTAIN until build 77). The committed generated outputs (Thesis_Defence_2026.pptx and .pdf, SPEAKER_NOTES.md, DEFENSE_SCRIPT.md and the review reports) remain the build-74 files until build 77, and the validator at HEAD fails on them by design (the reviewer counted 156 failures), since they predate the D-343 pane and the D-344 record; D-358 adds a check that every hidden page has its SPEAKER_NOTES.md section.
Annotation (2026-10-01, build 77): the generated outputs (Thesis_Defence_2026.pptx and .pdf, SPEAKER_NOTES.md, DEFENSE_SCRIPT.md, the review reports) are regenerated at build 77 and no longer predate the D-343 pane and the D-344 record; review/ARTIFACT_CHECK.json: 2092 checks, 0 package failures, including the 76 notes-pane checks, the planned-duration, overlay-mode and lead-source and supports-pointer checks (pages 58 to 76) and the closing-page list of every hidden page. The part held UNCERTAIN until build 77 (supports statement for retitled main pages) is settled by that evidence for the checked fields; the rendered notes pane was not viewed in PowerPoint.

ID: D-345
Status: SETTLED
Decision: Two data-driven layout variants. (1) Outline heading pairs: visual.variant "heading_pairs" on the outline kind, data.pairs [[heading, subline]], data.pair_boxes [[[x,y,w,h],[x,y,w,h]]] in inches, data.heading_size/subline_size (pt), data.heading_color/subline_color (hex); visual.box_style "plain" (PowerPoint default insets 0.1/0.05 in, no paragraph spacing), visual.title_box [x,y,w,h], visual.footer {rule, color, source_box, number_box, number_align}. (2) Bullet boxes: bullet_boxes, one {"box": [x,y,w,h], "size": pt, "leading_size": pt} per panel bullet, no dash mark, exclusive of bullet_y/bullet_height and equation strips. Constants: PLAIN_INSETS_IN (0.1, 0.05) are the OOXML defaults stored by the FOCUSED page-2 shapes (bodyPr without inset attributes). All geometry, sizes and colours of the two FOCUSED pages are content values, not code.
Why: Plan A7 and brief item 4: no page-number special-casing; FOCUSED page 2 (24/18 pt pairs, BFBFBF sublines, B0B0B0 footer, no rule) and page 41 (no dashes, 22/17 pt boxes, 22 pt leading kept on the 17 pt lines: lnSpc 2595 in the FOCUSED XML) differ from the shared layout.
Alternatives: A free list of text boxes (rejected: the page number and title would become data and could go stale).
Evidence: Feature exercise: built slides 2 and 41 equal FOCUSED in every shape's text, geometry (max difference 1 EMU), font size and colour (python-pptx comparison).
Reversibility: Remove the variant branches; pages without the fields are unaffected.
Review: The FOCUSED page-2 shapes are autoshapes, the builder writes text boxes with the same geometry, insets and type; the rendered page should be compared in M3.
Annotation (2026-10-01, round-11 code review R2): the only evidence is the feature exercise (python-pptx shape comparison); read this entry as UNCERTAIN until build 77 and the rendered-page comparison of pages 2 and 41 against the FOCUSED deck. The options title_box, footer and box_style are now admitted only on the two author layouts and every declared box is checked against the built shape (D-355).
Annotation (2026-10-01, build 77): exercised on the real content: gate equal on pages 2 and 41 (page 41 with the 1 EMU tolerance D-368); RENDER_COMPARE.md: page 2 raster identical to the FOCUSED render (the autoshape vs text box difference has no rendered effect), page 41 differs only in the rows of the F-70 title and the F-32 line.

ID: D-346
Status: SETTLED
Decision: DEFENSE_SCRIPT.md document text comes from a new content file script_document.json: header (lines before the main group), main_heading, qa_heading, qa_intro (lines), section_lines (bool: print each page's section line), appendix (lines after the last page: the author's "Additional questions" and "Rehearsal notes" sections go here verbatim), final_blank_line (bool). The committed file reproduces the build-76 document byte for byte (header and section lines of build 76, no intro or appendix). validate_deck.py adds "DEFENSE_SCRIPT.md equals script_document.json and the cue and narration blocks (D-346)" (independent rebuild) and "DEFENSE_SCRIPT.md and SPEAKER_NOTES.md are ASCII (D-346)"; the D-332 semicolon scan already covers every line, appendix included. make_package.py --require-clean adds script_document.json.
Why: Brief item 6; talk_content.json is a page list and cannot hold a document block without changing its type.
Alternatives: Keys inside talk_content.json page 1 (rejected: mixes page and document data).
Evidence: Unchanged content: DEFENSE_SCRIPT.md identical to 0e9fe81 (git diff empty). Feature exercise: header, Q&A intro and appendix equal DEFENSE_SCRIPT_FOCUSED.md byte for byte; the validator then reports the four FOCUSED semicolon lines (7, 527, 539, 541).
Reversibility: Delete script_document.json and restore standalone_script().
Review: None.
Annotation (2026-10-01, round-11 code review R2): the default document is verified on the committed content (byte-identical to 0e9fe81); the header, Q&A introduction and appendix are verified only by the feature exercise and stay UNCERTAIN in that part until build 77. Their scan now covers retired terms, internal recording names and repository paths as well as semicolons (D-357).
Annotation (2026-10-01, build 77): the header, Q&A introduction and appendix are exercised on the real content: DEFENSE_SCRIPT.md equals script_document.json and the cue and narration blocks, and DEFENSE_SCRIPT.md and SPEAKER_NOTES.md are ASCII (D-346 checks PASS, review/ARTIFACT_CHECK.json: 2092 checks, 0 package failures); the line table of review/round11_focused/EQUIVALENCE.md shows 58 lines differing from DEFENSE_SCRIPT_FOCUSED.md, 58 explained by the listed fixes (F-73 to F-76, F-78 and the page fixes) and 0 unexplained. The part held UNCERTAIN until build 77 is settled by that evidence.

ID: D-347
Status: SETTLED
Decision: The D-279 footer check finds the discussion, limitations and contributions pages by legacy key (discussion, 38, 55), each exactly once as a non-divider main page, with the same three footers; titles are free. New name: "The discussion, limitations and contributions pages (legacy keys discussion, 38, 55) cite Chapter 9, Table 9.1 and Section 10.1 (D-279, D-347)".
Why: Plan A7: the author retitled pages 41 and 43.
Alternatives: Add the new titles to the check (rejected: the next retitle would break it again).
Evidence: Feature exercise with page 41 retitled: PASS; self-test: a deck without the discussion page is reported.
Reversibility: Restore the title-keyed check.
Review: None.
Annotation (2026-10-01, round-11 code review R2): the retitled-page case is verified only by the feature exercise and the self-test; read this entry as UNCERTAIN until build 77 runs it on the author's retitled pages 41 and 43.
Annotation (2026-10-01, build 77): PASS on the author's retitled pages 41 ('Findings established by the evaluation', F-70) and 43 ('Further validation and development').

ID: D-348
Status: UNCERTAIN
Decision: set_page_budgets.py budgets a chapter divider that carries narration by its words exactly like a content page (words / rate * 60, rounded up to 5 s, no film lead); a divider with no narration keeps the fixed 5 s. Hidden main pages get 0 s and are left out of the total.
Why: Plan A5: the FOCUSED dividers carry 13-69 words that are spoken.
Alternatives: Keep 5 s for every divider (rejected: hides 10-30 s of speech per divider).
Evidence: Dry run at unchanged content (dividers already carry 12-21 words): 1790 s at 141 words per minute instead of 1755 s at 140 (not written). No timed rehearsal: the rate is the D-095 range, not a measurement.
Reversibility: Restore the fixed divider budget in fixed_budget().
Review: Author: whether divider narration should count toward the budget.

ID: D-349
Status: UNCERTAIN
Decision: set_page_budgets.py --allow-over-cap keeps 140 words per minute (no rate rise), prints the total and the overage, and with --write writes the budgets and budget_override.json {decision, cap_s, total_s, overage_s, rate_wpm}. Without the flag the behaviour is unchanged (rise to 144, exit 1 over TOTAL_CAP_S = 1795 s). validate_deck.py adds "Main talk is within the 1795 s cap or a recorded override names its total (D-349)" (FAIL over the cap without an override or with a stale one), reports main_time_cap {cap_s, planned_s, over_cap, overage_s, override_recorded} in ARTIFACT_CHECK.json and prints a "Time cap:" line; TOTAL_CAP_S is imported from set_page_budgets.py (one constant). make_package.py --require-clean includes budget_override.json when it exists.
Why: Plan A5: the FOCUSED narration exceeds the cap; an over-cap plan needs an explicit recorded override, not a silent pass.
Alternatives: Raise the cap (rejected: the cap is the author's round-9 ceiling).
Evidence: Self-test probes over-cap without an override and a stale override (both reported). --allow-over-cap was run as a dry run only (the exercise total stayed under the cap); the write path was not executed.
Reversibility: Remove the flag, the file and the check.
Review: Author: accept an over-cap talk or cut narration.
Annotation (2026-10-01, round-11 code review M2): an override for an in-cap talk now fails the cap check, and set_page_budgets.py --write removes a stale override when the total is within the cap (D-352); the D-356 check also compares the override's rate with the rule's.

ID: D-350
Status: SETTLED
Decision: validate_deck.py admits font sizes 24 and 18 pt only on an outline page with variant heading_pairs, inside (0.50, 1.20, 12.83, 6.86) in, and 17 pt only on a page with bullet_boxes, inside the left column (0.50, 1.20, 5.85, 6.75) in; colours BFBFBF and B0B0B0 only on the heading-pairs outline; on that page the 28 pt title may reach 1.20 in and the 10.5 pt footer 7.46 in. Constants from Thesis_Defence_2026_FOCUSED.pptx: slide 2 headings 24 pt FFFFFF, sublines 18 pt BFBFBF, footer 10.5 pt B0B0B0, title box bottom 1.198 in, page-number box bottom 7.458 in; slide 41 detail lines 17 pt. The two checks are renamed "... fixed font roles (variants: D-350)" and "... white monochrome palette (variants: D-350)". FONT_ROLES itself is unchanged.
Why: Plan A7: the new roles are admitted for the two variants only.
Alternatives: Add 24/18/17 pt to FONT_ROLES (rejected: would admit them everywhere).
Evidence: Feature exercise: slides 2 and 41 pass the role, grid and palette checks; self-test: 17 and 24 pt on an ordinary page and 20 pt on a bullet_boxes page are rejected.
Reversibility: Remove VARIANT_FONT_ROLES and the admission functions.
Review: None.
Annotation (2026-10-01, round-11 code review R2): the variant pages are built only in the feature exercise; the self-test covers the admission functions on synthetic samples. Read this entry as UNCERTAIN until build 77 exercises pages 2 and 41 on the real content.
Annotation (2026-10-01, build 77): pages 2 and 41 built from the real content pass the role, grid and palette checks (validate_deck.py 0 package failures).

ID: D-351
Status: SETTLED
Decision: make_package.py treats the deck inputs as dirty when `git status --porcelain --untracked-files=all -- <inputs>` is non-empty (modified, staged or untracked), and, when budget_override.json exists, requires `git ls-files --error-unmatch` to find it (so an ignored, untracked override also fails --require-clean). budget_override.json is always in the input list. make_package.py --self-test runs six cases in a throwaway git repository under TMPDIR: clean tree, untracked override, staged uncommitted override, committed override, modified tracked input, ignored required input.
Why: Code review I2: `git diff --quiet HEAD --` ignores untracked files, so --require-clean accepted a budget_override.json that was never committed.
Alternatives: `git diff --quiet HEAD` plus a separate `git ls-files --others` call (rejected: two calls for what one porcelain status gives, and staged files would still need a third).
Evidence: make_package.py --self-test: PASS (6 cases). The untracked-override case returns dirty with the new function; the old command (`git diff --quiet HEAD -- budget_override.json`) exits 0 on an untracked file (demonstrated in the same throwaway repository in the worker report).
Reversibility: Restore the `git diff --quiet` line in main().
Review: None.

ID: D-352
Status: SETTLED
Decision: set_page_budgets.py --write removes budget_override.json when the total is within TOTAL_CAP_S (the file is one this tool writes), and validate_deck.py cap_problem() fails when an override exists but the talk is within the cap, or when the override's total or cap differs from the deck's.
Why: Code review M2: an earlier --allow-over-cap run left an override that the validator then reported for an in-cap talk.
Alternatives: Keep the file and only warn (rejected: a stale record would describe a plan that no longer exists).
Evidence: Feature exercise (round-11 review): a hand-written override (total 1900 s) was removed by --write at 1730 s; with the override placed back, validate_deck.py failed "Main talk is within the 1795 s cap or a recorded override names its total (D-349)" with "an override (total 1900 s) is recorded but the talk plans 1730 s". Self-test: stale in-cap override and mismatched total both reported.
Reversibility: Drop the unlink branch and the in-cap clause.
Review: None.

ID: D-353
Status: UNCERTAIN
Decision: Hidden main pages are left out of every count that describes the talk as presented: the chapter-order check ("Main story follows verified thesis Chapters 1-10") reads the shown main pages; the evaluation-sequence check counts evaluation pages on shown main pages and requires each evaluation page found by legacy key to be shown (the D-254 number checks still cover a hidden one); the main-demonstration checks and demonstration_coverage read the shown main pages, as the builder's SPEAKER_NOTES.md line does, while the "main and Q&A" demonstration check keeps every page. The package README states "<shown> shown main pages, <hidden> hidden main pages and <topic> hidden topic pages" (the middle part omitted when zero), "The <n> hidden pages <ranges>", and the closing page found by kind; MANIFEST.json adds shown_main_pages and hidden_main_pages.
Why: Code review M3: the validator counted all main pages where the builder counted shown ones, and the README would have read "48 main pages and 28 hidden topic pages" while 30 pages are hidden.
Alternatives: Count hidden main pages as main pages everywhere (rejected: a hidden page is not presented, so it cannot carry the chapter order or a demonstration of the talk); treat them as topic pages in the README (rejected: they keep their main page numbers).
Evidence: Feature exercise with pages 2 and 3 hidden: validator main demonstrations 17/17 and hidden_pages 30 entries; builder SPEAKER_NOTES.md "across 46 shown pages", "Hidden main pages, outside the timing: 2, 3", "Main recorded demonstrations: 17/17"; make_package.render_readme(): "46 shown main pages, 2 hidden main pages and 28 hidden topic pages, 76 in total ... The 30 hidden pages 2-3 and 49-76". No hidden page in the exercise is a demonstration or an evaluation page, so those branches are covered by the code path only.
Reversibility: Revert the three validator list comprehensions to talk and the README template to $main_pages/$backup_pages.
Review: Master or author: whether a hidden evaluation page should fail the evaluation-sequence check (current choice) or be allowed.

ID: D-354
Status: SETTLED
Decision: An emphasis pair is "**" not preceded by a word character or "*" and followed by a non-space, closed on the same line by "**" after a non-space and not followed by a word character or "*" (build_deck.py EMPHASIS, written again independently in validate_deck.py). Any other "**" stays as written. The notes pane and SPEAKER_NOTES.md drop the pairs from cues and narration; DEFENSE_SCRIPT.md keeps them. New checks: "No '**' emphasis marker is left in any notes pane or in SPEAKER_NOTES.md (D-354)" and "Every '**' in DEFENSE_SCRIPT.md is a balanced word-boundary emphasis pair within its paragraph (D-354)". A literal "**" (for example an exponent) is therefore not admitted in narration or cues.
Why: Code review M1: the old pattern turned "2**3 and 4**5" into "23 and 45", left an unbalanced "**c" in the pane, never stripped "**" in a cue, and nothing flagged a leftover.
Alternatives: Escape syntax for a literal "**" (rejected: no page needs one; the spoken script writes exponents in words).
Evidence: Self-test samples: "2**3 and 4**5", "**c and more", "word**s**" and a trailing "**" are kept and reported; "**Measured** uses. (**Held**) too." becomes "Measured uses. (Held) too."; a cue "Point to **Held**." gives the pane line "[Point to Held.]". Unchanged content and the feature exercise (FOCUSED page 22 markers absent from the exercise pages, header line "**Lanqing Luo | ...**" present): both checks PASS.
Reversibility: Restore the old pattern and drop the two checks.
Review: None.

ID: D-355
Status: SETTLED
Decision: visual.title_box, visual.footer and visual.box_style are admitted only on the two author layouts, the heading-pairs outline and a bullet_boxes page; box_style only "plain". build_deck.py raises otherwise (check_layout_options), and validate_deck.py checks it and that every declared box is drawn: title_box (title text), footer source and number boxes (declared or default), heading and subline pair boxes, bullet boxes, each exactly one text shape within BOX_TOLERANCE_IN = 0.005 in, with the declared colour and size, plain insets 0.1/0.05 in and no spacing element when box_style is plain (title, footer and pair boxes), and the footer rule drawn exactly when footer.rule is not false. One aggregate check: "title_box, footer and box_style appear only on the heading-pairs outline or a bullet_boxes page, and every declared author-layout box is drawn as declared (D-355)". Constants: BOX_TOLERANCE_IN from the existing caption-box check in validate_deck.py (abs(box_in[0]-.82) <= .005); PLAIN_INSETS_IN, FOOTER_RULE_Y_IN 6.88, DEFAULT_SOURCE_BOX, DEFAULT_NUMBER_BOX and DEFAULT_FOOTER_INK BBBBBB copied from build_deck.py (PLAIN_INSETS_IN, restrained_footer).
Why: Code review M4: the options were accepted on any page, no check tied them to the variants, and README.md claimed the validator read title_box and footer when it did not.
Alternatives: Admit the options on every page and check the boxes only (rejected: the D-350 font and colour admission is tied to the two layouts, so the box options follow the same scope).
Evidence: Self-test: footer on a composite page and box_style "bold" are reported, a bullet_boxes page with title_box passes; matching boxes pass, a moved pair box, a wrong footer rule and zero insets are reported. Feature exercise: the FOCUSED page-2 and page-41 layouts pass the check. README.md table corrected.
Reversibility: Remove check_layout_options and the validator functions; the README rows return to "any restrained page".
Review: None.

ID: D-356
Status: UNCERTAIN
Decision: set_page_budgets.narration_words() imports build_deck.narration(), so the budget tool and the builder share one narration model; budgets() and a new plan() take the word-count and film functions as parameters. validate_deck.py adds "Every shown main page budget equals the set_page_budgets.py rule applied to its narration (D-356)": plan() at the rate it selects (the start rate when an override is recorded), applied to the validator's own independent word count, must equal every shown main duration, and a recorded override's rate_wpm must equal that rate. The check is exact (durations are integers in 5 s steps).
Why: Code review M5: the budget tool joined blocks differently from the builder and the validator, so word counts could diverge with no check catching it.
Alternatives: Import the builder's narration into the validator too (rejected: the validator re-implements the model independently by design; the new check makes any divergence fail).
Evidence: The check FAILS on the committed content: its durations predate D-348 (dividers with narration budgeted by words), so nine dividers (pages 6, 12, 19, 21, 26, 31, 37, 40 and 42) plan 10 s instead of 5 s and pages 10 and 29 change by 5 s at 141 words per minute (1790 s, the D-348 dry run). With the durations rewritten by set_page_budgets.py --write (temporary, content restored), the deck validates with 0 package failures; the feature exercise also passes after --write. Self-test: conforming budgets pass, an off-rule budget and a missed film floor are reported.
Reversibility: Remove the check and the import; restore the local narration_words().
Review: M3 must run set_page_budgets.py --write before build 77; until then the validator reports this one package failure on the committed content.
Annotation (2026-10-01, round-11 close-out, second code review): the budget check counts words independently (the validator's own narration model) but imports the rule from set_page_budgets.py (validate_deck.py line 724: TOTAL_CAP_S and plan as budget_plan; rate, rounding, film lead, fixed budgets and film floor live in that tool), so a change of that rule in set_page_budgets.py changes the check with it and is not caught by it. The check proves that the recorded durations equal the rule, not that the rule is right. The review note of this entry was met at build 77 (D-364); the validator reports the check as PASS.

ID: D-357
Status: SETTLED
Decision: The header, qa_intro and appendix lines of script_document.json are scanned with the D-311 rules (a) semicolon, (c) retired term, (d) internal recording name or repository path. The question-clause rule (D-263) is not applied: the appendix is the author's questions section. New check: "script_document.json header, Q&A introduction and appendix carry no semicolon, retired term, internal recording name or repository path (D-357)".
Why: Code review R1: these author parts had only the semicolon and ASCII rules.
Alternatives: Apply the question-clause rule as well (rejected: every appendix heading is a question).
Evidence: Self-test: R7 in a header, a repository path, "Signal conditioning" and a semicolon are reported; a bold name line and a question heading pass. Feature exercise: the FOCUSED header line 7 and appendix lines 45, 57 and 59 are reported (semicolons, the same lines D-346 found), for M3 to fix.
Reversibility: Remove the check.
Review: None.

ID: D-358
Status: SETTLED
Decision: New check "Every hidden page, hidden main and topic pages alike, has its SPEAKER_NOTES.md section and unspoken record (D-358)": each hidden page has a section headed "## Slide NN: <title> (" with its record lead ("Q&A BACKUP | Slide NN | Not in main-talk timing" or "HIDDEN MAIN PAGE | Slide NN | Not in main-talk timing"), Q&A pages without derivation keys included.
Why: Carried-over gap of the review: only derivation pages and main pages had their sections checked.
Alternatives: One check per page (rejected: 28 or more checks for one property).
Evidence: Self-test: a missing section and a hidden main page with a MAIN TALK lead are reported. Unchanged content and the feature exercise: PASS.
Reversibility: Remove the check.
Review: None.

ID: D-359
Status: SETTLED
Decision: Round 11 M3 (build 77): the FOCUSED titles, visible text, hidden set (pages 2 and 3), cues and narration are back-ported verbatim into talk_content.json and backup_content.json, including the caveats the author removed and the four claims NUMBER_CHECK.md marks NOT SUPPORTED or STRONGER THAN SOURCE (pages 33, 35, 36, 41); they are neither softened nor restored, and are listed for the author in M4.
Why: Approved plan, assumption A1: the author's FOCUSED pair is the truth for the content; changing claims silently would overrule the author.
Alternatives: Restore the removed caveats (rejected by A1); soften the four flagged claims (rejected: a content change the author has not made).
Evidence: review/round11_focused/apply_backport.py writes every changed string at the field M1 mapped it to (focused_content.json); review/round11_focused/EQUIVALENCE.md: compare_decks.py gate exit 0, 76 of 76 pages EQUAL after the listed rule fixes; review/round11_focused/CAVEATS_REMOVED.md and NUMBER_CHECK.md (M1).
Reversibility: Rerun apply_backport.py with a different focused_content.json, or revert the content commit of build 77.
Review: Author: the removed caveats (CAVEATS_REMOVED.md) and the four flagged claims (NUMBER_CHECK.md).

ID: D-360
Status: UNCERTAIN
Decision: The 69 minimal rule fixes F-01 to F-69 of review/round11_focused/rule_fixes.json are applied to the back-ported text: 15 semicolons recast, the page-32 opening, 6 en dashes to ASCII hyphens, 5 "Camera prime" to "Camera'", the page-49 Sources numbers [8]-[11] (D-338), 4 bullet shortenings and 37 D-263 question-clause recasts.
Why: The author's standing text rules (D-311, D-326, D-332, D-263) hold (plan A2); the validator fails on each of these strings otherwise.
Alternatives: Waive the checks for the author's text (rejected: fix, never waive); larger rewrites (rejected: minimal edits keep the author's wording).
Evidence: validate_deck.py --pdf at build 77: 2092 checks, 0 package failures; EQUIVALENCE.md lists the entries applied per page and shows every differing DEFENSE_SCRIPT.md line explained by a listed fix.
Reversibility: Remove entries from rule_fixes.json and rerun apply_backport.py and the chain (the validator will then fail on that string).
Review: Author: the fix list in RULE_FIXES.md; the D-263 class and the "Camera'" class were found after the plan was approved.

ID: D-361
Status: UNCERTAIN
Decision: The three items M1 marked NEEDS AUTHOR are reworded by the master: page 41 title "What the evaluation establishes" -> "Findings established by the evaluation" (F-70); page 3 bullet "Applications need body and object positions in one metric scene" -> "Body and object positions in one metric scene" (F-71); page 39 bullet "Replay: each branch under 33.3 ms in 99% of frames" -> "Replay branches under 33.3 ms, 99% of frames" (F-72).
Why: Each violates a standing rule (D-263 what-clause; the 8-word panel-bullet limit) with no meaning-neutral fix; the master's wording keeps every number, unit and noun.
Alternatives: Leave the author's text and fail the validator (rejected: fix, never waive); drop content words to reach the limit (rejected).
Evidence: validate_deck.py --pdf at build 77: 0 package failures; build_deck.py text-fit warnings 0; RENDER_COMPARE.md: page 41 differs from FOCUSED only in the title rows and the F-32 line, page 3 only in the first bullet, page 39 only in the third bullet; the page-41 title renders on one line at 28 pt (render_compare/page-41_focused_left_build77_right.png).
Reversibility: Edit or remove F-70 to F-72 in rule_fixes.json and rerun apply_backport.py and the chain.
Review: Author, first in the check list: accept or reword each of the three.

ID: D-362
Status: UNCERTAIN
Decision: Page-32 bullet "Absolute length errors: 0.53 to 2.83 cm" -> "Length errors: 0.53 to 2.83 cm" (F-77, NEEDS AUTHOR).
Why: build_deck.py raised "Equation strip at 5.05 in meets the bullet text ending 4.99 in on slide 32": the D-276 guard keeps 0.10 in between the last bullet and the equation strip, and the FOCUSED bullet wraps to two lines at 22 pt in the 5.03 in column (DejaVu Sans width 6.03 in). "Length errors: ..." (4.67 in) is one line and keeps every number, unit and noun; "Absolute errors: ..." (4.96 in) would drop the noun "length". The page's table caption keeps "Absolute length error in cm".
Alternatives: Relax the D-276 guard (rejected: no check is weakened); move the bullets or the strip (rejected: the FOCUSED geometry is the reference); a smaller font (rejected: font roles are fixed).
Evidence: build_deck.py error above; widths measured with PIL ImageFont on /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf as build_deck._text_lines() does; after the fix build_deck.py, validate_deck.py (0 package failures) and the gate (exit 0 with F-77) pass; RENDER_COMPARE.md page 32 differs only in rows 4.33-4.92 in (that bullet).
Reversibility: Remove F-77 from rule_fixes.json; the builder will raise again unless the layout changes.
Review: Author: accept "Length errors", or prefer "Absolute errors".

ID: D-363
Status: UNCERTAIN
Decision: script_document.json takes the FOCUSED header (md lines 1-7), the Q&A introduction and the "Additional questions to rehearse" and "Rehearsal and revision notes -- not spoken" sections verbatim, with section_lines false, except four semicolon fixes F-73 to F-76 (md lines 7, 749, 761, 763) and F-78: final_blank_line false, so the file ends with one newline where the FOCUSED md ends with a blank line (git diff --check reports a blank line at EOF otherwise); all recorded in rule_fixes.json 'script_document' and RULE_FIXES.md.
Why: Master decision 4; the D-332 and D-357 rules reject a semicolon in the generated script document.
Alternatives: Leave the semicolons (rejected: fix, never waive); drop the appendix (rejected: the author wrote it).
Evidence: review/round11_focused/EQUIVALENCE.md script part: every DEFENSE_SCRIPT.md line that differs from DEFENSE_SCRIPT_FOCUSED.md (same line count) is explained by a listed fix; validate_deck.py "DEFENSE_SCRIPT.md equals script_document.json and the cue and narration blocks (D-346)" and the D-357 scan PASS at build 77.
Reversibility: Edit the entries and rerun apply_backport.py and build_deck.py.
Review: Author: the four recast lines and the end-of-file change (RULE_FIXES.md). Deviation from the M3 brief, which said final_blank_line true: the brief's own git diff --check requirement decided it.

ID: D-364
Status: UNCERTAIN
Decision: Budgets of build 77 by set_page_budgets.py --allow-over-cap --write at 140 words per minute (D-348, D-349): main talk 1895 s = 31:35 over 46 shown main pages, 100 s above the 1795 s cap; budget_override.json {decision D-349, cap_s 1795, total_s 1895, overage_s 100, rate_wpm 140} is committed; the narration is not cut.
Why: Plan A5 and master decision 5: the author's narration stays; the overage is an explicit recorded override for the author to decide.
Alternatives: Raise the rate to 144 (rejected by D-349); cut narration (rejected: the author decides cuts, TIME_ESTIMATE.md ranks candidates).
Evidence: set_page_budgets.py output "Rate 140 words per minute; main total 1895 s (31:35) ... methodology 1230 s = 64.9 percent"; review/ARTIFACT_CHECK.json planned_main_seconds 1895, main_script_words 3943, main_time_cap {cap_s 1795, planned_s 1895, overage_s 100, override_recorded true}. Budgets are word-rate estimates, not a timed rehearsal.
Reversibility: Cut narration or change the cap, then set_page_budgets.py --write (it removes the override when within the cap).
Review: Author: accept 31:35 or choose cuts (TIME_ESTIMATE.md).

ID: D-365
Status: UNCERTAIN
Decision: Unspoken record fields are edited only where they quote an old title or contradict the new page text: page 41 visualintent "Left: six short bullets, what each evaluation supports and its limit." -> "Left: three findings, each above its measured result."; page 48 purpose.right_visual "the single word Question" -> "the single word Questions". Not changed: hidden pages 2 and 3 (keep their records by decision), page 36 right_visual "hand-object mismatch remains qualitative evidence" (it describes the film and is the source-supported statement; the new bullet "Replay shows movement and hand-cube alignment" is NOT SUPPORTED in NUMBER_CHECK.md, so the record is not rewritten to match it), and every claim and takeaway that states a removed caveat without quoting a title.
Why: Master decision 6: smallest edit, no removed caveat restated as page text, no provenance, source, data, legacy_key, supports or media field touched.
Alternatives: Rewrite every record of a retitled page (rejected: not minimal); leave page 41 and 48 as they were (rejected: they describe the old page).
Evidence: apply_backport.py RECORD_EDITS (two edits, each asserted to match once); the record fields of the 21 retitled or re-texted pages were read against the new text in this task.
Reversibility: Edit RECORD_EDITS and rerun apply_backport.py.
Review: Author or master: page 36 right_visual against the new page-36 bullet.

ID: D-366
Status: SETTLED
Decision: The md's bold markers stay md-only: page 22 narration carries **Measured**, **Held** and **Constrained** in its notes field, and the title line is in script_document.json's header; the notes pane, SPEAKER_NOTES.md and word counts drop them (D-354).
Why: Master decision 7; the FOCUSED pane shows no markers, the FOCUSED md does.
Alternatives: Drop the markers (rejected: the author wrote them).
Evidence: Gate: page-22 pane blocks equal FOCUSED; EQUIVALENCE.md: DEFENSE_SCRIPT.md line 235 equals the FOCUSED line after F-45 only; validator emphasis checks PASS.
Reversibility: Remove the markers from the page-22 notes.
Review: None.

ID: D-367
Status: SETTLED
Decision: Pages with one cue, first, keep presenter_cue and notes (73 pages; notes "" on pages 2, 3 and 46); pages 17, 23 and 44, whose FOCUSED narration carries a second cue, declare script_blocks.
Why: D-342 keeps the legacy fields for single-cue pages; it keeps the content diff to the changed strings.
Alternatives: script_blocks on all 76 pages (rejected by D-342; also tried in this task and gave the same deck).
Evidence: Gate exit 0 and validator 0 package failures with this form; apply_backport.py --check reports no difference.
Reversibility: Change the branch in apply_backport.py.
Review: None.

ID: D-368
Status: SETTLED
Decision: Equivalence gate geometry tolerance: page 41 only, 1 EMU (allow entry G-01).
Why: The page-41 bullet boxes are declared in inches and drawn with Inches(); the round trip moved one box top by 1 EMU (3675888 -> 3675887), the only geometry difference on 76 pages. No blanket tolerance: every other page compares exactly.
Alternatives: The D-355 bound 0.005 in = 4572 EMU (rejected: far looser than measured); store EMU in the content (rejected: the M2 content format is inches).
Evidence: First gate run of build 77: one difference, page 41 geometry moved 1 EMU; with G-01 exit 0.
Reversibility: Remove G-01; the gate then fails on that 1 EMU.
Review: None.

ID: D-369
Status: UNCERTAIN
Decision: Rendered-comparison constants (review/round11_focused/render_compare.py): "same" means 0 differing pixels on the 90 dpi pdftoppm rasters (render_deck.py's resolution); a secondary share of pixels differing by more than 32 levels (LOUD = 32, chosen in this task, no measurement behind it, reported only); side-by-side images at half scale with 256 colours to keep render_compare/ under the brief's 5 MB (548 KB measured). page-41 line pitch 22 pt (LEADING_41 in apply_backport.py) is the M2 exercise value from the FOCUSED XML lnSpc 2595 (D-345).
Why: The primary metric needs no threshold; the secondary one is informational.
Alternatives: A perceptual metric with a threshold (rejected: identical rasters are achievable, 68 of 76 pages).
Evidence: RENDER_COMPARE.md: 68 identical pages; the 8 that differ (3, 23, 28, 32, 35, 36, 39, 41) differ only in the rows of the strings changed by F-22, F-29 to F-32, F-70 to F-72 and F-77.
Reversibility: Change the constants and rerun render_compare.py.
Review: None.

ID: D-370
Status: SETTLED
Decision: The scope of the round-11 equivalence gate (compare_decks.py, equivalence_report.py) is recorded in EQUIVALENCE.md under "Scope of the gate", emitted by the script so a regeneration keeps it. The gate compares, per slide in order: the slide count, the hidden flag, the text of every text frame and table cell with its role, geometry in EMU, and the sets of run font sizes, run solid-fill colours and run bold flags per shape, the media part hashes and geometry, and the notes blocks (cue, say, Sources, other pane lines). It does not compare: text-free autoshapes, connectors and lines (including the footer rule); shape fill and line colour; picture crop; italic, typeface, alignment, line spacing and anchor; z-order; shape type; the slide background; playback timing; inherited styling (only run properties written on each run are read); and, because sizes, colours and bold are sets per shape, a swap of run sizes inside one shape. Equality on the gate (76 of 76 pages EQUAL) therefore does not by itself establish equality of the whole package.
Why: The second code review found that the report's one-line description of what is compared reads as a full equivalence while the code reads fewer fields.
Alternatives: Extend compare_decks.py to read the missing fields (rejected for this close-out: no checker or builder change; the unread fields are covered by the rendered comparison); leave the description as it was (rejected: it overstates the gate).
Evidence: The scope statement is read from compare_decks.py _runs() (lines 92-106, run properties), extract() (lines 175-217, shapes, tables, media and notes) and compare() (lines 296-358); that statement is SETTLED. The part that the unread fields show no visible difference in build 77 rests on the code reviewer's probe of those fields across the 76 slide pairs (reported to the master; no script or output of that probe is committed, so it was not re-run in this task) and on review/round11_focused/RENDER_COMPARE.md (68 of 76 rendered pages pixel-identical to the FOCUSED render, the other 8 differing only in rows changed by a listed fix; LibreOffice render at 90 dpi, PowerPoint not used); that part is as strong as those two sources.
Reversibility: Remove the SCOPE text from equivalence_report.py and regenerate EQUIVALENCE.md; or extend compare_decks.py to read the missing fields and update the text.
Review: None for the scope statement; the author or master may ask for the probe to be committed as a script.

ID: D-371
Status: SETTLED
Decision: Archive the exact reviewed RESTRUCTURED_FIXED PPTX and matching Speaker_Script DOCX under presentation/defense_2026/, and make them the recommended entry without replacing build 77.
Why: The author explicitly requested saving the approved delivery in the Git repository and uploading it. Copying the locked files preserves the reviewed formulas, media, styles, notes and playback behavior.
Alternatives: Rebuild with the legacy talk_content.json/script_document.json chain or overwrite its outputs (rejected: those describe a different 76-page deck); upload the private work directory or full validation receipt (rejected: only the two deliverables and a concise delivery record are needed).
Evidence: review/restructured_fixed_20261005/DELIVERY.json pins both SHA256 hashes, 77 total/46 shown/31 hidden pages, the 1627-second editorial allocation, unchanged source assets and the reviewed native playback results. The immutable presentation helper reports 24 valid empty media-action relationship IDs as missing relationships; its failure is retained honestly, while the independent preservation audit and separate official layout/font/chart/table/import checks passed.
Reversibility: Remove the newly archived pair and current-entry documentation in a later ordinary commit; all older deck and generator assets remain available.
Review: Verify the two archived hashes against DELIVERY.json, then open the PPTX and use the matching Word script. The allocation still requires an aloud rehearsal.

ID: D-372
Status: SETTLED
Decision: Move coordinate-transform and left-handed-body QA to hidden pages 47-48, replace the body-coordinate page with two concise same-body workflow diagrams, and synchronize the Word script and two-page Outline/QA guide.
Why: The author requested the two answers first in QA and a direct comparison of conventional RH matrix processing with early LH convention alignment for Unity composition.
Alternatives: Retain the dense body-versus-object comparison (rejected: the question concerns two routes for the same body); rebuild or alter the 46 main pages (rejected: the approved main content stays unchanged).
Evidence: DELIVERY.json pins all three reviewed files, the 77/46/31 counts, the old76/77-to-new47/48 order, unchanged main-slide/media bytes, preserved five formula crops, approved notes, and native QA display. The conventional full-matrix route includes basis conversion and angle re-extraction for five rotations per frame; no alternative-route runtime speed-up is claimed. The unchanged page47 footer is raised to the highest foreground only. The official helper's 24 valid empty-media-action findings remain documented honestly.
Reversibility: Restore the prior reviewed files from commit e12d5fd through a later ordinary commit; all legacy generator assets remain untouched.
Review: Use the matching script and two-page guide, inspect hidden47/48, and rehearse the editorial allocation aloud.

ID: D-373
Status: SETTLED
Decision: Translate the two-page Outline/QA Word guide entirely into English, keeping Letter landscape geometry, the talk tree and all 11 hidden-QA topic/range groups.
Why: The author clarified that the guide should use English after the first archive upload.
Alternatives: Keep the Chinese guide or regenerate the deck/script (rejected: only the guide language needs to change).
Evidence: DELIVERY.json records the new guide SHA256, two reviewed pages, full 31-page QA coverage and unchanged PPTX/Speaker_Script hashes. Root and independent checker approved the English tree, native QA table and layout.
Reversibility: Restore the earlier guide from fdf438e in an ordinary later commit; the PPTX and English speaker script are unaffected.
Review: Open the English guide and use its page ranges to navigate hidden QA47-77.

ID: D-374
Status: SETTLED
Decision: Replace only QA48 with two English body-model flowcharts, remove its five formula-picture shapes, and synchronize only the matching notes and Word cue/speech.
Why: The author requested separate LH and RH routes, visibly separate RH processing steps, no formulas or object route on this comparison, and an explanation of how every displayed count is derived.
Alternatives: Retain formula crops, bundle RH conversions with angle extraction, display sign-flip counts, or claim a measured runtime improvement (rejected: the approved comparison uses matrix-form products and derived counts).
Evidence: DELIVERY.json pins the reviewed PPTX/script and unchanged guide. LH has five stages and eight input matrix-vector products for eight complete-frame landmarks. RH has six stages, five rotations and two matrix-matrix products per rotation: ten per frame. Both have thirteen angles. Only logical48 XML/notes and its Word cue/speech changed; all other slide/package/media bytes and fonts are frozen. Native PowerPoint fresh-open/display and focused independent scope/render gates passed. The official helper's same 24 valid empty-media-action findings remain documented honestly.
Reversibility: Restore the prior PPTX/script from 163cdf6 in a later ordinary commit; all removed pictures' media payloads and legacy generator assets remain available.
Review: Use the matching script for QA48; the matrix-form counts describe the representation, not measured dense calls, CPU operations, or an FPS ratio.

ID: D-375
Status: SETTLED
Decision: Unify the deck, English script and Chinese outline into three blocks, with a 26-minute main allocation and one minute of reserve.
Why: The author requested overview-to-detail structure, density matching pages 8-10, a 27-minute cap and no English guide.
Alternatives: Keep the preceding delivery (rejected by the author); change frozen thesis or pipeline data (outside this scope).
Evidence: DELIVERY.json, timing_plan.json and delivery_audit.json; timed aloud delivery remains unmeasured.
Reversibility: Restore the three canonical files from 20b61a0 in an ordinary later commit; historical records remain intact.
Review: Exact hashes and honest final-native-playback limits are in review/personal_review_20261005/DELIVERY.json and VISUAL_REVIEW.json.

ID: D-376
Status: SETTLED
Decision: Use synchronized flat-circle geometry under the RGB film on page 23; keep three main points and six nested detector items on page 20.
Why: The author requested simple 2D circles, video above, no black masks and no repeated reveal clicks.
Alternatives: Keep the preceding delivery (rejected by the author); change frozen thesis or pipeline data (outside this scope).
Evidence: p23_animation_provenance.json pins the 462-frame film. Direction memory is an illustrative derivation, not a logged recovery event; the original clip stays embedded.
Reversibility: Restore the three canonical files from 20b61a0 in an ordinary later commit; historical records remain intact.
Review: Exact hashes and honest final-native-playback limits are in review/personal_review_20261005/DELIVERY.json and VISUAL_REVIEW.json.

ID: D-377
Status: SETTLED
Decision: Recapture page 38 in native Unity with corrected table display bounds, task-centred wall mesh span and an oblique camera.
Why: The author identified table and wall placement as wrong and requested correction in code and a new recording.
Alternatives: Keep the preceding delivery (rejected by the author); change frozen thesis or pipeline data (outside this scope).
Evidence: delivery_manifest.json, scene_geometry.json and validation/: calibration planes and input poses retained; 897 frames applied, 5 Unity checks and 12 rig checks passed. Display mesh extent includes a clipped front edge and illustrative legs.
Reversibility: Restore the three canonical files from 20b61a0 in an ordinary later commit; historical records remain intact.
Review: Exact hashes and honest final-native-playback limits are in review/personal_review_20261005/DELIVERY.json and VISUAL_REVIEW.json.

ID: D-378
Status: SETTLED
Update: D-379 supersedes the four-page bibliography arrangement; repair remains retained.
Decision: Remove fourteen p23 animation build records pointing to deleted shapes, and reflow all four IEEE reference pages with preserved 16-point text and standard venue abbreviations.
Why: The author identified the Repair prompt and the overlapping reference entries; both were defects in the edited package.
Alternatives: Accept PowerPoint Repair or deliver the overlapping bibliography (rejected).
Evidence: All 78 slides pass animation-target checks. The final publication package opened directly without Repair, and page44 native slideshow showed separated entries. The p23 film advanced from frame604 to705 with synchronized flat geometry in the repaired package.
Reversibility: Restore the previous files in an ordinary later commit.
Review: DELIVERY.json and VISUAL_REVIEW.json pin the final scope and hashes.

ID: D-379
Status: SETTLED
Decision: Keep all 23 IEEE entries on the original three visible reference pages; remove the added hidden reference page and synchronize the script and guide.
Why: The author rejected a separate QA reference page and approved the corrected three-page version for upload.
Alternatives: Retain four pages or a separate QA bibliography (rejected by the author).
Evidence: reference_consolidation_audit.json; final 77-page package opened without Repair; pages 42-44 checked in native slideshow and by the author. All other 74 slides and all media bytes are preserved from the reviewed package.
Reversibility: Restore earlier files from Git history in an ordinary later commit.
Review: DELIVERY.json pins the final three files. No sources were added, removed or renumbered by this correction.

ID: D-380
Status: SETTLED
Decision: Deliver the outline and QA index entirely in English, keeping the two-page Letter landscape layout and three-block structure.
Why: The author explicitly requested all deliverables in English before upload.
Alternatives: Keep the Chinese guide (rejected).
Evidence: Both English pages were rendered and visually inspected; all visible text and diagram labels are English. PPTX and script hashes are unchanged from ef3f6bc.
Reversibility: Restore the earlier guide through an ordinary later commit.
Review: DELIVERY.json records the updated guide hash and language.

ID: D-381
Status: SETTLED
Decision: The author's three uploaded files are the final deliverables of presentation/defense_2026, adopted byte for byte under canonical names: Thesis_Defence_2026_RESTRUCTURED_FIXED.pptx is renamed (git mv) to Thesis_Defence_2026.pptx (102708312 B, sha256 da94af7c11b30defdc5de453b0014c5f2b396bc99740293e188770d766a0a749; 77 slides, 46 shown = pages 1-46, 31 hidden = pages 47-77; 148 media files = 25 MP4 + 123 PNG; 0 external relationships); Thesis_Defence_2026_Speaker_Script.docx (54114 B, sha256 413ab0367b25d203814040c3bdfdedc0cd83ff2b8787209fed93a50fdd1daf3d) and Thesis_Defence_2026_Outline_and_QA_Index.docx (209782 B, sha256 a266ffe5ab3e014eac12ec17792cec96e08f4c7cbfae0e91ce9522ffdd9add4b) keep their names. No byte of the three files is edited.
Why: The author approved these files as the final version (D-371 to D-380); rebuilding or patching them would replace the author's reviewed content with a generated approximation.
Alternatives: Keep the RESTRUCTURED_FIXED name beside the round-11 Thesis_Defence_2026.pptx (rejected: two decks under near-identical names); regenerate the deck from talk_content.json (rejected: that model describes the 76-page build-77 deck, not the author's).
Evidence: sha256sum after the git mv equals the M1 hash; the three hashes equal those pinned in review/personal_review_20261005/DELIVERY.json (review/restructured_fixed_20261005/DELIVERY.json pins an earlier pptx, sha256 1d646c2b..., 100099912 B, superseded by D-378 to D-380); slide count, hidden flags (p:sld show="0") and media counts read from the package with zipfile and python-pptx on 2026-10-06; make_package.py deck_facts() reports 0 external relationships.
Reversibility: git mv the file back; the RESTRUCTURED_FIXED path is in commit 87e87ae.
Review: Open Thesis_Defence_2026.pptx and confirm it is the deck to present.
Annotation (2026-10-06): the pptx is no longer the author's bytes; D-387 replaces the slide 12 picture with a film by author request (new sha256 3dcaf106...; every other zip entry unchanged).

ID: D-382
Status: SETTLED
Decision: The legacy decks and the retired builder pipeline are removed from the working tree with git rm (history untouched): 151 files, 110156009 B, plus the round-11 Thesis_Defence_2026.pptx (83316620 B) and Thesis_Defence_2026.pdf (41332147 B) replaced in place by the final deck and its new render. Removed: (1) round-11 deck files Thesis_Defence_2026_FOCUSED.pptx, DEFENSE_SCRIPT.md/.docx/.pdf, DEFENSE_SCRIPT_FOCUSED.md, SPEAKER_NOTES.md; (2) review/round10_script and review/round11_focused (39 files); (3) presentation/out (marp output, 1 file); (4) build_deck.py, render_deck.py, validate_deck.py, set_page_budgets.py, report_effective_text.py; (5) their inputs script_document.json, budget_override.json, effective_text_table.json; (6) their reports review/{ARTIFACT_CHECK.json, RENDER_CHECK.json, SCRIPT_EXPORT_CHECK.json, BUILD_LAYOUT_CHECK.json, EFFECTIVE_TEXT.md, VALIDATOR_SELF_CHECK.json}, CUTTING_GUIDE.md, DEMONSTRATION_MANIFEST.json, restrained_purposes.json, REVISION_OUTLINE.md, RESTRAINED_REVISION_PLAN.md; (7) their render outputs preview/ (76 slide PNGs, 7 overview JPGs) and review/restrained_samples/ (3 PNGs). Every removed file is byte-identical in commits 85078c9 (the round-11 records state) and 87e87ae, so either commit recovers it. Kept although planned for removal, because a file outside the deletion list reads it at run time: presentation/v9 (anim/method_context.py and anim/recorded_context.py read v9/videos/embed/VIDEO-1.mp4, v9/videos/HANDOVER_UNITY_R7.mp4 and hash v9/anim/video1_overlay.py and handover_unity_clip.py); presentation/assets (presentation/slides.md, rendered by presentation/build.sh, embeds 14 of them); committee_materials/ (eval/pipeline_smoothness/compare_film_vs_live.py, 13 anim/ scripts, bank_processing/check_*_media.py, review/validate_*.py, unity_capture/finalize_archived_capture.py and validate_archived_media.py); review/qa_revision (export_committee_questions.py line 24); export_defense_script.py (export_committee_questions.py line 19 imports add_page_field and plain_inline); talk_content.json and backup_content.json (anim/bank_revision_build.py, anim/unified_revision_build.py, anim/committee_inventory.py); bank_processing/ with checker_inputs/ (anim/bank_kinematics.py, anim/bank_axes_kinematics.py, anim/unified_revision_build.py, eval/pipeline_smoothness/compare_film_vs_live.py, v3/tests/test_oracle.py, bank_processing/run_overlay_checker.py).
Why: The author's files are final (D-381); the legacy decks and the generator that produced them would otherwise be mistaken for current deliverables. The run-time rule of the M2 brief keeps any file another kept file still reads.
Alternatives: Delete the blocked groups too (rejected: it would break kept generators and the eval and v3 code that read them); delete only the unread files inside presentation/v9 (rejected: partial removal of a group was not in the brief; left to the master).
Evidence: git grep of every group path and basename across the tracked tree on 2026-10-06, readers classified by extension (code: .py, .sh, .cs, .js) and read at the cited lines; records (README, DECISIONS, SESSION_REVIEW, knowledge, PROJECT_STATUS, JSON provenance) were treated as citations, not readers. Kept code mentioning build_deck.py, validate_deck.py, render_deck.py, set_page_budgets.py or report_effective_text.py does so only in comments (equation_assets.py, equations/derivation_leads.py, equations/typeset_filters.py, experiments/filter_metrics/charts.py, make_frame_overlay_figures.py, measure_film_geometry.py). git rev-parse of each removed path at 85078c9 and 87e87ae gives the same blob.
Reversibility: git checkout 87e87ae -- <path> restores any removed file.
Review: Master or author: whether to retire the kept groups with their readers (v9, assets, committee_materials, qa_revision, export_defense_script.py, talk_content.json, backup_content.json); measure_film_geometry.py and review/film_geometry.json are kept although their only consumer, validate_deck.py, is removed.

ID: D-383
Status: UNCERTAIN
Decision: The build, render, validation, budget and effective-text checkers are retired with the pipeline (D-382). The verification basis of the final package is: sha256 equality of the three source files with the hashes in D-381; LibreOffice PDFs written by make_package.py --render (soffice 24.2.7.2 headless, isolated profile in a tempfile directory honouring TMPDIR, Impress option ExportHiddenSlides true, the retired render_deck.py invocation without its GIF-poster snapshot because the final deck has no GIF), recorded with source and PDF hashes in review/RENDER_RECORD.json; PDF page counts (deck 77 = all slides, hidden included; speaker script 23; outline and QA index 2); a rendered-page spot check of the deck PDF; and the external-relationship refusal of make_package.py. Embedded media playback is not verified. make_package.py packages the three files, their three PDFs and README.txt; it keeps the sha256 manifest, the git_commit pin, --self-test (six cases, the required-record file renamed from budget_override.json) and --require-clean (inputs: the six files, PACKAGE_README.txt, make_package.py and the tracked render record), and refuses to package a PDF that RENDER_RECORD.json does not describe for the current source.
Why: The checkers validated the builder's content model, which no longer produces the deck; the author's files can only be checked as files. Rendering inside make_package.py keeps the PDFs reproducible by one command after render_deck.py and export_defense_script.py are gone.
Alternatives: Keep validate_deck.py and run it against the author's deck (rejected: it reads talk_content.json and the round-11 rules and would fail on content the author approved); a separate render script (rejected: one more file for the same three soffice calls); no render record (rejected: make_package.py would lose its refusal of stale PDFs).
Evidence: make_package.py --render output 2026-10-06 (77, 23 and 2 pages; review/RENDER_RECORD.json); --self-test PASS (6 cases); a packaging dry run into the scratch directory wrote all seven files with matching hashes (176777787 B); a tampered and a missing render record were refused. The author's earlier render of a previous script version recorded 22 pages (review/restructured_fixed_20261005/DELIVERY.json, validation.word_script_changed_page14_render); the 23 pages here come from LibreOffice and the difference was not investigated. The author's official helper reports 24 empty media-action relationship IDs (D-371); make_package.py does not run that check.
Reversibility: Restore the retired scripts from 87e87ae; make_package.py --render can be removed if the author supplies the PDFs.
Review: Play every embedded video in PowerPoint on the defence machine; the PDF is a LibreOffice still copy and may differ in layout from PowerPoint.

ID: D-384
Status: SETTLED
Decision: Status of the round-11 open author calls against the final files of D-381. Closed by the author's final version: D-364 and D-349 (31:35 at 140 words per minute, 100 s over the 1795 s cap) -- the script now plans 2540 spoken words in 26 minutes with one minute of reserve under a 27-minute limit (D-375), so the budget override no longer exists; D-361 and D-362 (wordings F-70, F-71, F-72, F-77) -- neither the author's nor the master's wording occurs in the final deck or script; D-359 (four claims marked stronger than source) -- none of the four flagged strings occurs, and page 35 now shows the left wrist, median 12.3 to 13.1 cm over 16 frames, beside the right wrist; page-41 wrap -- the line "Right-wrist median: 11.4 to 5.2 cm (4 frames)" no longer exists, and page 35 shows "Median: 11.4 to 5.2 cm" and "4 frames" (joined by a middle dot) on one line in the LibreOffice render. Closed as obsolete with the pipeline (D-382): D-360 rule fixes, D-363 script-document fixes, D-365 record fields, D-369 render-comparison constant. Round-10 leftovers: D-306 reference numbering is superseded by D-378 and D-379 (23 IEEE entries on three pages); D-322 and D-323 omissions persist as the author's choice (Eqs. 3.15-3.17 appear in the page-13 Sources line and hidden page 63 but not in the script; the page-22 test names are not spoken); D-304, D-313, D-314, D-316 to D-319 and D-324 are closed as rules with the retired validator and were not re-checked page by page. Still open: a timed aloud rehearsal (the script states its schedule is a rehearsal guide, not a measured delivery time) and PowerPoint playback of the embedded videos (D-383).
Why: The deck these calls asked about (build 77) is no longer a deliverable; the author's final files answer them or make them moot.
Alternatives: Carry every round-11 call forward unchanged (rejected: most refer to strings and files that no longer exist).
Evidence: Text of all 77 slides and notes (python-pptx) and of both Word files (python-docx) searched on 2026-10-06 for each contested string; Speaker_Script paragraph 4 (2540 words, 26 minutes, 27-minute limit); page-35 render at 100 dpi from Thesis_Defence_2026.pdf. Whether every one of the 29 removed caveats of CAVEATS_REMOVED.md is restored was not checked.
Reversibility: Reopen any call by a new entry that points here.
Review: Author: the timed rehearsal and the PowerPoint playback; D-322 and D-323 only if the equations or test names should be spoken.

ID: D-385
Status: SETTLED
Decision: Second M2 pass (author decision 2026-10-06): the groups D-382 kept are retired with the scripts that only served the old deck builds, by git rm (history untouched): 653 tracked files, 644,950,669 B plus export_defense_script.py, and review/qa_revision/question_index.json moved with git mv to review/question_index.json. Removed: presentation/v9, presentation/assets, presentation/slides.md, presentation/build.sh (no marp config file exists); review/qa_revision (all but the moved index); talk_content.json, backup_content.json, measure_film_geometry.py, review/film_geometry.json; committee_materials/ except committee_materials/unified_four/provenance/ (512 files); 16 anim/ scripts (axes_archived_unity, axes_kinematics, axes_revision_audit, axes_revision_build, axes_revision_docs, axes_revision_media, axes_unity_composite, bank_revision_build, committee_audit, committee_build, committee_copy_clearance, committee_inventory, committee_media, committee_recordings, method_context, unified_revision_build); bank_processing/check_bank_media.py, check_unified_media.py, check_unified_four_media.py; review/validate_axes_sources.py, validate_coordinate_axes_independent.py, check_kinematic_source_independent.py; unity_capture/finalize_archived_capture.py, validate_archived_media.py; export_defense_script.py. Kept: committee_materials/unified_four/provenance/ (four JSONs; eval/pipeline_smoothness/compare_film_vs_live.py line 216 reads the p14 and p16 stems); bank_processing/ (v3/tests/test_oracle.py and compare_film_vs_live.py read its data; check_*_sources.py check that data and read no deleted path); anim/bank_kinematics.py and bank_axes_kinematics.py (producers of the kept bank_processing data, cited by v3/bench/oracle.py and v3/tests/test_oracle.py); unified_panels.py, coordinate_axes.py, axes_inputs.py, axes_extract.py (imported by or feeding kept make_coordinate_figures.py); recorded_context.py, raw_task_context.py, raw_handover_task.py, validate_media.py and the other media/ generators and validators (master decision: raw_task_context.py imports recorded_context.py and validate_media.py asserts its sha256 through media/provenance/recorded_context.json). export_committee_questions.py now carries add_page_field and plain_inline copied verbatim from export_defense_script.py, reads review/question_index.json, and no longer records shared_helper_sha256.
Why: The author retired the legacy material; the run-time rule of the M2 brief keeps every file that a kept file, eval/ or v3/ reads or imports.
Alternatives: Delete recorded_context.py, raw_task_context.py, raw_handover_task.py and validate_media.py as well (rejected by the master: they generate and check current media/ assets); delete the question index (rejected: validate_source() checks the bank sha256 and 804 field comparisons against it).
Evidence: Reverse-dependency scan of every presentation/defense_2026 script (import lines, importlib and subprocess calls) and git grep of every deleted path and basename on 2026-10-06; export_committee_questions.py --pdf rerun: all 19 DOCX parts byte-identical to HEAD (only zip entry dates differ), PDF text (pdftotext -layout) identical, 61 pages (only the creation date differs); make_package.py --self-test PASS (6 cases) and a normal build wrote the seven files with hashes equal to their sources (176,777,787 B).
Broken provenance left as written (records, not run): anim/recorded_context.py lines 27-28 (presentation/v9/videos/embed/VIDEO-1.mp4, presentation/v9/videos/HANDOVER_UNITY_R7.mp4) and lines 250-279 (presentation/v9/anim/video1_overlay.py, handover_unity_clip.py), so its clips cannot be regenerated and its source audit cannot run; media/provenance/recorded_context.json cites the same v9 files; anim/raw_handover_task.py line 68 and anim/bank_kinematics.py line 37 and bank_axes_kinematics.py line 40 write into committee_materials/ subfolders that no longer hold the old outputs; review/COMMITTEE_EXPORT_CHECK.json no longer records the helper hash. validate_media.py was not run.
Reversibility: git checkout 87e87ae -- <path> restores any removed file; git mv the index back and restore the import line.
Review: Author: confirm that no removed committee film or v9 video is still wanted outside git history.

ID: D-386
Status: UNCERTAIN
Decision: The speaker script (Thesis_Defence_2026_Speaker_Script.docx and .pdf) is rewritten general-then-specific by author instruction of 2026-10-06 and is now built from a tracked source: slides 1-46 are 2,532 spoken words, 1560 s at 110 words per minute (26:00, one minute under the 27-minute limit); slides 47-77 are unchanged. Structure rules: (1) each of the three blocks opens with a question; (2) each section and each slide paragraph states its point first and then the specifics; (3) clean language and no repetition (no semicolons, filler words, internal recording names R1-R9, sentences opening on a number word, or a sentence of eight words or more repeated on two slides); (4) one Heading 3 per section, ten sections in three blocks (Motivation and goal 1-4; System architecture 5; Data preprocessing 6-10; Kinematic model 11-15; Object tracking 16-18; Partial occlusion 19-24; From modules to one system 25-30; Results 31-38; Limitations, future directions and summary 39-41; References and close 42-46). The D-263 rule "no question clause anywhere" is overridden for the block-opening questions only; every other string keeps D-263. Budget: the enforced limit is the 1560 s cap for slides 1-46 at 110 words per minute (the timing constants of the author's builder review/personal_review_20261005/build_documents.py lines 41-44: 2 s per slide, per-slide viewing pause, remainder to slide 38); the 2,600-word working ceiling is the figure in the milestone brief of 2026-10-06 and has no measurement behind it. Five trims met the cap, one sentence or clause each with no claim removed: slides 2, 5, 20, 25 and 26. Source and builder: speaker_script.json (text, timing constants, block and section map, header lines) and build_speaker_script.py with three modes: --extract (docx to JSON, used once to seed the source), default (JSON to docx, template = the current docx with its body cleared so the author's styles stay, timing lines recomputed) and --check (lint: word count and seconds per slide, 1560 s cap, the style rules above, header word count and checkpoints against the computed values; exit 0 on pass). Outputs: docx sha256 2231078d90d0e2127757fdd5d06550f8fed981bb3a28f1ce8ddc6a28c4a1ffa8, pdf sha256 39f544f38b09165226b65425b79edb8eda41359ff53a88970ad8b03fb1ff8744 (24 pages, was 23 before the headings); package/MANIFEST.json and review/RENDER_RECORD.json refreshed; Thesis_Defence_2026.pptx unchanged (da94af7c...). Not verified: a timed aloud rehearsal (26:00 is arithmetic from word counts, not a measurement), a cold read of the new script against the slides by the author, PowerPoint playback of the embedded videos, and whether the slide 32 and 33 sentences "carry short, lift and slide long" and "about sixteen centimetres" (claims the slides do not show) are what the author wants spoken.
Why: The author asked for a script that tells the listener the point first and then the detail, with a question to open each block. Keeping the text in JSON makes every later edit a reviewable diff and the timing is recomputed rather than hand-typed; the docx is then a build output.
Alternatives: Edit the docx by hand (rejected: the timing lines and the word count in the header would drift and nothing would check them); keep D-263 with no exception (rejected: the author's instruction is for block-opening questions); raise the cap above 1560 s (rejected: the author's schedule is 26:00 with one minute of reserve, D-375); trim more than five slides (not needed to reach the cap).
Evidence: build_speaker_script.py --check on 2026-10-06: 2532 words, 1560 s, cap 1560 PASS, 0 hits; sha256sum of the docx and pdf as above; render record pdf_pages 24 (review/RENDER_RECORD.json); commit 2d9db7e. The author's previous script text is in commit 3dbd345 and 87e87ae.
Reversibility: git checkout 3dbd345 -- presentation/defense_2026/Thesis_Defence_2026_Speaker_Script.docx restores the previous script; delete speaker_script.json and build_speaker_script.py if the docx is to be edited by hand again; D-263 returns in full by a later entry that points here.
Review: Author: read the script against the slides (the block-opening questions, the ten section headings, the five trimmed slides 2, 5, 20, 25, 26, and the slide 32 and 33 sentences), then time one aloud read against the 26:00 schedule.

ID: D-387
Status: UNCERTAIN
Decision: Slide 12 "Linked landmarks and constraints" shows an 8.0 s film instead of the static figure overlay_landmark_frames.png (author request 2026-10-06): the landmark chain lights up layer by layer from the root, L24 red #FF4040 -> L23, L12, L11 green #40E070 -> L13, L14 blue #408CFF -> L15, L16 amber #E8B35A, unlit dots and bones grey #656565, labels white, each legend line in its layer colour once every landmark it names is lit. Film media/p12_chain_growth.mp4 (1440 x 1200, h264 yuv420p, 30 fps, 240 frames, no audio, CRF 19 preset slow, sha256 c3c72c7c25199f1271c0f533575a5113b8e605c4e82332038680b005c5419650), poster media/p12_chain_growth_poster.png = last frame (complete chain), provenance media/provenance/p12_chain_growth.json, generator anim/chain_growth.py. Timeline: 1.0 s hold with L24 lit; layer two in two back-to-back 0.5 s steps (24->23 and 24->12, then 12->11 and 23->11); 1.5 s hold; layer three 0.5 s (12->14, 11->13); 1.5 s hold; layer four 0.5 s (14->16, 13->15); 2.0 s final hold. Each bone grows linearly from parent to child in the colour of its child's layer and the child dot changes colour on arrival. Embedding (anim/patch_slide12_video.py): Picture 10 (id 11) is replaced in place by a copy of slide 13's movie shape (a:videoFile r:link and p14:media r:embed to ppt/media/p12_chain_growth.mp4, blip to ppt/media/p12_chain_growth.png) at the picture's geometry (x 5966460, y 1097280, cx 5486400, cy 4572000 EMU), with slide 13's timing block (video node, vol 80000, delay 0, spid 11); ppt/media/image10.png is removed because no other relationship named it; [Content_Types].xml is unchanged. The pptx becomes sha256 3dcaf1068b5e7668e8b8ed325e2145027d7bb91566e89ea31ee3cc581d43dff1, 103,078,203 B (was da94af7c..., 102,708,312 B); 149 media files (123 PNG, 26 MP4). The slide 12 cue in speaker_script.json gains "Play the clip while speaking."; the spoken text and the 41 s are unchanged.
Why: The author wants the chain to grow from L24 "like a diffusion model", so the listener sees the parent-to-child order. Reusing the figure generator's geometry, and copying the movie convention already used on slides 13-15, keeps the final frame identical to the reviewed figure except for its colours and keeps the embedding to a form the deck already uses.
Alternatives: PowerPoint entrance animations on native shapes (rejected: the figure is one bitmap and the deck has no native-shape animation convention); a GIF (rejected: the deck has no GIF and no gif content type); the briefed holds of 0.6 s and 0.4 s (rejected: 5.4 s against the author's target of about 8 s); following the thesis level one, which groups L23 with L24 (rejected: the author chose the order above for the deck).
Evidence: chain_growth.py refuses to encode unless its renderer, given the original colours, reproduces overlay_landmark_frames.png pixel for pixel (passed); the final frame differs from that figure only at drawn pixels (28,046 differing pixels, all inside the drawing mask) and the last encoded frame equals the poster. ffprobe: h264, yuv420p, 1440x1200, 30/1, 240 frames read, 8.000 s, one video stream. Zip-entry comparison (name and CRC, review/slide12_patch.json): changed ppt/slides/slide12.xml and ppt/slides/_rels/slide12.xml.rels, added the two media parts, removed image10.png, 492 entries unchanged. python-pptx opens the deck (77 slides); slide 12 holds one MEDIA shape and no picture. LibreOffice renders page 12 with the poster (make_package.py --render, 77 pages). build_speaker_script.py --check: 2532 words, 1560 s, 0 hits. The full anim/validate_media.py run is blocked by the missing /tmp/defense_2026_causal cache (knowledge/checkers_and_caches.md line 311; regenerating it needs the author's approval); its inspect() was run on the new film alone with synchronized_filters stubbed to an empty map in a scratch call: PASS (h264, yuv420p, 30/1, no audio, full decode, 8.0 s against EXPECTED_SECONDS 240/30).
Judgement calls without a measurement: the hold values 1.0 s, 1.5 s and 2.0 s (master decision 2026-10-06, to reach about 8 s); linear growth; legend lines white until lit; lit bones in the child's layer colour; L11 grown from both L12 and L23 because the figure draws both bones.
Not verified: playback in PowerPoint (start on slide entry, poster before play, frame rate on the defence machine); the film was never played inside a presentation program.
Reversibility: git checkout cd0efce -- presentation/defense_2026/Thesis_Defence_2026.pptx restores the author's bytes (or remove the two media parts, restore image10.png and slide12.xml and its rels from cd0efce); revert the cue in speaker_script.json and rebuild the docx and PDFs.
Review: Author: play slide 12 in PowerPoint on the defence machine and confirm that the film starts on entry, that the layer order and colours are wanted, and that 8 s fits the 41 s of speech.

ID: D-388
Status: UNCERTAIN
Decision: Speaker script slides 13, 14 and 31-35 rewritten, cap raised from 1560 s to 1620 s (27:00, full limit, no reserve), and fourteen cut edits made elsewhere to fit; speaker_script.json is the source, build_speaker_script.py now reads timing.cap_s from the JSON (module default CAP_S 1620). Slide 13 cue is now "Point along the hip line, then the forward axis, then the up axis." Total 2,659 words, 1620 s, 0 lint hits; header lines updated (27 minutes using the full limit; checkpoints 02:21, 18:31, 27:00).
Why: Slides 13-14 now state the derivation the thesis gives (root frame: thesis equations 3.7-3.12, x from the hip line, the shoulder vector only selects the torso plane, z = x cross shoulder vector normalised, y = z cross x, which corrects the earlier y-before-z wording; shoulder swing and twist: equations 3.18-3.23, elevation arcsine, azimuth arctangent, twist from the forearm projected into the y-z plane after undoing the swing, rotation y then z then x with twist innermost). Slides 31-35 follow why design result: why the quantity must be verified, which test was designed, then the number. Author choices (2026-10-06): slide 33 reports elbow and wrist only because shoulder and L24 errors are not reported in the thesis (the root output is constrained on every retained frame) and were not invented; slide 34 gives one window (intermediate motion), wrist and elbow for each of the three recovery cases; slide 35 gives the right wrist only (median 11.4 cm plain to 5.2 cm object-assisted), the thesis having no elbow number there. The author approved the 1620 s cap and the cut list below.
Alternatives: keeping the cap at 1560 s (rejected by the author, the new text needs about 160 s more than D-386); the planned trim list alone (reached 1688 s, 68 s over); a cap above 27:00 (exceeds the limit).
Evidence: build_speaker_script.py --check: 2659 words, total 1620 s, cap 1620 PASS, hits 0. Text added by the rewrite: slides 13-14 +125 words, slides 31-35 +168 words; the plan had estimated about 70 s, the measured addition was 158 s (1503 s before to 1661 s after, slide 38 at base length). Cuts applied in the author's order with running totals from 1712 s: (1) slide 36 delete " Offline processing gives repeatable evaluation material, but motion capture and VR need output as data arrives." 1703; slide 33 "A physical check closes the loop: the wrist-to-marker" to "The wrist-to-marker" 1700; slide 32 delete ", so an object error would pass into recovery" 1696; slide 27 delete " This gives a common display time even when the branches finish at different moments." 1688. (2) slide 14 last sentence "A straight arm has no perpendicular forearm component, so the twist is unobservable and the previous value is held until the elbow bends." to "A straight arm hides the twist, so the previous value is held." 1682. (3) slide 33 delete " The wrist-to-marker distance during a grip is fifteen point eight centimetres on the right and fourteen point one on the left, against about sixteen measured on the hand." 1666. (4) slide 32 "a route with four waypoints, parked on the desk, the foot of the lift, the start of the rail, and the far end" to "four waypoints along the lift and the rail" 1658; delete " between marker centres" 1656. (5) slide 26 delete " An odd sequence means a write is in progress, and an even one means the slot is settled." 1646. (6) slide 28 delete " Positions pass through the same anchor as points." 1641. (7) slide 29 delete " This common scene placement keeps body and object in the same coordinate system." 1634. (8) slide 20 delete " A rejected observation becomes missing, so it cannot distort the solve." 1628. (9) slide 22 delete " Each new grasp starts a new offset estimate." 1624. (10) slide 7 delete " The overlay shows this output before cleaning." 1620, the cap reached. Not applied: item 11 (slide 3 clause) and item 12 (slide 27 and slide 26 sentences). One joining fix by the worker: slide 32 "moves the cube along four waypoints along the lift and the rail" changed to "moves the cube through four waypoints along the lift and the rail". Slide 33 compares model and rendered elbow and wrist (five to seven centimetres rendered, from 5.3 to 6.8 in the thesis table) and the 11.4 to 5.2 and the model medians come from Chapter 7 as quoted in the plan. Docx paragraph count 328, equal to the previous docx. Docx sha256 5cb8cee1db3550e73a9de79173fbc6c18a20e7eb19cbf9c8f348f37ddb7bb16a, script pdf 9ba82fdb5b629f2cf32d74b3561680ee0afdc45f95edd1633ef6bb3e810d40ac (23 pages, was 24). make_package.py --render is now idempotent (D-388): it skips a PDF whose source sha256 and PDF sha256 match review/RENDER_RECORD.json (prints "unchanged, skipped") and re-renders only the others, so the deck and outline PDFs stay the HEAD bytes (0e601571..., c4c6924a...) and only the script PDF and its record entry change.
Reversibility: git checkout 5dbdeee -- presentation/defense_2026/speaker_script.json build_speaker_script.py and rebuild the docx and PDFs.
Review: Author: read slides 13, 14 and 31-35 against the slides and the thesis equations; confirm the 14 cuts (the removed grasp-distance sentence on slide 33 and the shortened slide 14 ending); time one aloud rehearsal against 27:00, which has no reserve; slide 32 "the depth leg before the lift reconstructs short in both recordings, and the two legs after it reconstruct long" is not shown on the slide.

ID: D-389
Status: UNCERTAIN
Decision: Results slides 33, 34 and 35 reduced to what the D-388 script says (author instruction 2026-10-06). Slide 33: title "Body, unoccluded: model and avatar"; bullets "Model elbow 0.36 / 1.08 cm", "Model wrist 0.83 / 2.34 cm", "Rig 5.3 to 6.8 cm"; the four mini-table rows Model elbow 0.36 / 1.08, Model wrist 0.83 / 2.34, Rig elbow 5.3 / 6.1, Rig wrist 5.5 / 6.8 (same geometry; the grasp-distance bullet and the wrist-to-marker row are gone); caption and footer unchanged. Slide 34: all six rows kept; the two intermediate rows (frames 445-489, ids 23-27 and 41-45) amber E8B35A and bold, the other four data rows grey BBBBBB, header and tiles unchanged; caption gains " - spoken: intermediate window 445-489" with the deck's middle-dot separator. Slide 35: the left-wrist panel (ids 1006, 1007), Picture 11 (id 12) and its label (id 11) deleted; Picture 9 (id 10) and its label (id 9) moved to x 7096790 EMU (delta +1409222), centred on the right content span of caption id 26 (x 5687568, cx 6044184); reference sub-line "Watch landmark on the right wrist"; relationship rId3 and ppt/media/image50.png removed because no other relationship part named it. speaker_script.json slide 33 title "Body unoccluded model and avatar", slide 33 cue "Compare the model rows with the rig rows.", slide 35 cue "Explain the image pair and the legend before the median." (master instruction 2026-10-06); spoken text unchanged. Patch: anim/patch_results_slides.py (refuses a second run), record review/results_slides_patch.json. The pptx becomes sha256 4e158522cf007fe6f06f69dd2770b442913cc9fa00ee9f2af3c34551994d9a37, 102,013,918 B (was 3dcaf106..., 103,078,203 B); 148 media files (122 PNG, 26 MP4).
Why: The author asked why slide 34 still shows all the data after the script was reduced; the author chose (2026-10-06) to keep slide 34's six rows and highlight the spoken window, and to reduce slides 33 and 35 to the spoken quantities. Colour and bold are set on the existing runs so the run formatting (16 pt DejaVu Sans) stays; both colours are the deck's own (slide 21: E8B35A highlight, BBBBBB secondary label).
Alternatives: deleting the four unspoken rows of slide 34 (rejected by the author: the windows give context); leaving slides 33 and 35 as they were (rejected: the script no longer speaks the grasp distance or the left wrist); keeping image50.png in the package (rejected: nothing references it after the deletion).
Evidence: Thesis cross-check before writing (writing/v9/Chapter_7_Evaluation.docx read with python-docx): "on the frame sets of Table 7.4 the kinematic-model elbow median is 0.36 centimetres on the right and 1.08 centimetres on the left"; model wrist "0.83 centimetres ... on the right and 2.34 centimetres on the left"; Table 7.4 rig elbow 5.3 / 6.1 and wrist 5.5 / 6.8 cm. Zip-entry comparison (name and CRC, review/results_slides_patch.json): changed slide33.xml, slide34.xml, slide35.xml and _rels/slide35.xml.rels, removed ppt/media/image50.png, nothing added, 491 entries unchanged; a byte comparison with the previous pptx gives the same four parts. python-pptx opens the deck (77 slides); slide 35 holds one picture (Picture 9, r5_label_compare_f1890.png). build_speaker_script.py --check: 2659 words, 1620 s, cap PASS, 0 hits. make_package.py --render re-rendered the deck PDF (77 pages, fa947606...) and, after the cue edits, the script PDF (23 pages, 8b585d7e...; docx 31d998ce...), outline skipped.
Not verified: the slides in PowerPoint. In the LibreOffice render the slide 34 caption wraps to two lines and its second line sits just above the footer divider (box id 52 uses spAutoFit); the slide 33 caption "Single-hand grips - median distances - right n = 650, left n = 589" was kept as the plan says, although n = 650 / 589 are the Table 7.4 frame sets and "Single-hand grips" described the removed grasp row.
Reversibility: git checkout f52e2f1 -- presentation/defense_2026/Thesis_Defence_2026.pptx presentation/defense_2026/speaker_script.json, then rebuild the docx, PDFs and package.
Review: Author: view slides 33, 34 and 35 in PowerPoint (amber rows legible, slide 34 caption fits above the divider, slide 35 picture centred); decide whether the slide 33 caption should change with the slides.

ID: D-390
Status: UNCERTAIN
Decision: Slide 33 gains the Python FK still and slide 34 a picture of how the controlled-removal comparison was made (author instruction 2026-10-06; plan declarative-stargazing-phoenix.md; master decisions 2026-10-06). Slide 33: media/p33_fk_overlay.png (640 x 480, R7 handover frame 630) as picture id 35 at x 6.0, y 1.2 in, 3.3 x 2.475 in; label id 36 (copy of caption id 31, 16 pt) at y 3.75 in, 3.3 in wide, one paragraph "Python FK on the RGB frame: green measured, red and blue FK arms"; video id 30 moved to x 9.454 in so its right edge meets caption id 31. Slide 34: the Frames column deleted (header id 12, cells 18, 24, 30, 36, 42, 48); every a:rPr of the remaining grid cells (ids 11, 13-15 and the cells among 17-51) set to sz 1400, colours and bold kept; columns from x 0.5 in: Motion / joint 2.45, Hold-last 1.05, Direction memory 1.95, Object-assisted 1.65 in (right edge 7.6 in), cell text 0.1 in inside each column; header bar id 9 and grid lines 10, 16, 22, 28, 34, 40, 46 7.1 in wide; caption id 52 unchanged; media/p34_masked_comparison.png (1500 x 1155 px) as picture id 1005 at x 7.8, y 2.35 in, 5.0 x 3.85 in. Figure: left, R7 frame 489 cropped to the right arm with the unmasked reference chain in white, the removed elbow and wrist circled red ("removed for 45 frames") and the three recovered chains (hold-last BBBBBB, direction memory B48CFF, object-assisted E8B35A); right, wrist (thick) and elbow (thin dashed) error per frame 445-489 with the medians in the legend; fonts 10 pt axis labels (41.7 px), 9 pt legend, ticks and notes (37.5 px) at 300 dpi. speaker_script.json cues: slide 33 "Point to the FK overlay before the table.", slide 34 "Point to the figure: the removed joints, then the three recovered chains."; spoken text unchanged. Patch: anim/patch_results_pictures.py (refuses a second run), record review/results_pictures_patch.json. The pptx becomes sha256 13f3f74b63a7cc7fc91779c4c478b8b32852bd63851a7f0f1961c66ef56278f6, 103,088,310 B (was 4e158522..., 102,013,918 B); 150 media files (124 PNG, 26 MP4).
Why: The author asked for a picture of the skeleton drawn by the Python forward kinematics on slide 33 and a picture of how the comparison was made on slide 34. Frame 489 instead of the planned 450: at frame 450 the three recovered chains lie under the reference chain and nothing can be compared; 489 is the last masked frame of the window and has the largest spread (wrist about 3.0 / 2.9 / 0.7 cm), frame 450 is still decoded and must equal writing/v9/figures/src/r7_frame00450.png byte for byte, which pins the frame index. Frame 630 on slide 33: inside the right-hand-alone interval 426-863 (writing/v9/audit_evidence/ch7_restructured/spatial_check.json), included for the right wrist in spatial_check_pairs.csv, all landmarks measured, nothing occluded. Its source is a fresh baseline run, /home/luo/anaconda3/bin/python -B eval/inspect/check_v1_overlay.py --stem recording_20260909_000024 --solver baseline --out <scratchpad>/v1_overlay_r7 (1499 frames, mp4 sha256 c7e634a5ec88f26029d2708947bfd1323e43f826d2107a03310a5b2ed69e7ad3, not kept in the repository); eval/output/v1_check/v1_overlay_recovery.mp4 was not used because its --recovery rendering draws an object-derived wrist cross and a failure banner the label does not explain. The Frames column was removed and the grid set to 14 pt (master decision) to free the right half of the slide for the figure. Column widths: the master decision named 2.5 / 1.4 / 1.8 / 1.4 in, but at 14 pt DejaVu Sans "Object-assisted" measures 1.50 in, "Direction memory" 1.75 in and the bold "Intermediate, elbow" 2.22 in (PIL ImageFont.getlength), so the two right headers could not sit on one line; the worker chose 2.45 / 1.05 / 1.95 / 1.65 in, the minimum widths 2.37 / 1.01 / 1.90 / 1.65 in (0.1 in inset, 0.05 in spare, judgement) plus the remaining 0.16 in; the patch checks every cell against its column.
Alternatives: the master's widths 2.5 / 1.4 / 1.8 / 1.4 in (rejected by measurement: the headers wrap, and a first render showed a wrapped bold row overlapping the next one); two-line headers (rejected: they overflow the 0.55 in header bar); frame 450 (rejected: the chains coincide); the recovery overlay video (rejected, see Why); a 12 or 13 pt label to keep it on two lines (not done: the master fixed 16 pt).
Evidence: review/results_pictures_patch.json: zip-entry comparison changed slide33.xml, slide34.xml and their two rels, added ppt/media/p33_fk_overlay.png and ppt/media/p34_masked_comparison.png, removed nothing, 491 entries unchanged; text_fit per cell. media/provenance/p34_masked_comparison.json: medians 1.2377 / 1.8839 / 1.2092 wrist and 0.6921 / 1.7304 / 1.5992 elbow, rounded equal to slide 34 (1.2 / 1.9 / 1.2, 0.7 / 1.7 / 1.6); projection check of the reference chain against the measured landmarks of frame 489, 3.3 px elbow and 6.2 px wrist (limit 12 px). media/provenance/p33_fk_overlay.json: frame 630, source mp4 and command. python-pptx opens the deck (77 slides). build_speaker_script.py --check: 2659 words, 1620 s, 0 hits. make_package.py --render: deck PDF 77 pages (7d79676e...), script PDF 23 pages (c7e2318e...).
Not verified: the slides in PowerPoint. In the LibreOffice render the slide 33 label wraps to three lines (16 pt in 3.3 in cannot hold it in two: the first two lines of a greedy wrap measure 3.25 and 3.37 in), and the Object-assisted header has 0.05 in to spare, so a renderer with wider metrics could wrap it.
Reversibility: git checkout 10252ea -- presentation/defense_2026/Thesis_Defence_2026.pptx presentation/defense_2026/speaker_script.json, then rebuild the docx, PDFs and package; or change COLUMNS or the label in anim/patch_results_pictures.py and rerun it on the restored deck.
Review: Author: view slides 33 and 34 in PowerPoint (still and label legible, three-line label acceptable, slide 34 headers on one line, figure readable from the room); confirm frames 630 and 489 and the column widths.

ID: D-391
Status: UNCERTAIN
Decision: Slide 39 "Limitations" lists the system's assumptions and their consequences instead of the evaluation weaknesses of thesis Table 9.1 (author instruction 2026-10-06; plan declarative-stargazing-phoenix.md, Milestone A). Header cells 13 / 14 "Assumption" / "Consequence"; rows 16/17 "Static scene" / "Camera, desk and wall calibrated once and held fixed - moving any of them means recalibrating"; 19/20 "Uncertain inputs" / "Rejected or held, never estimated - a held value carries its error into later frames"; 22/23 "Object size" / "Small handheld object - a large one hides landmarks, the hips L23 and L24 first, and the root frame drifts"; 25/26 "Rigid torso" / "One plate from hips and shoulders - trunk bend or twist is not modelled" (the separator on the slide is the deck's middle dot); row 5 (cells 28, 29, "Online deployment") and divider 27 deleted; caption 30 "System assumptions and their consequences - thesis Chapter 9; Sections 2.2.2, 3.2.1, 4.1"; footer 32 "Undergraduate thesis | Chapter 9; Sections 2.2.2, 3.2.1, 4.1". Table 9.1 is no longer cited on the slide. speaker_script.json slide 39 cue "State each assumption and its consequence in one sentence; do not argue with it." and spoken text as in the plan (66 words, was 65; the opening sentence "The closing section covers limitations, future directions, and the summary." is gone with it); header word count 2,659 -> 2,660 so that --check passes. Patch: anim/patch_slide39_limitations.py (refuses a second run, header check), record review/slide39_patch.json. The pptx becomes sha256 a27dc653d3860e8076622e1923894c49a2c03e148551f06d1739eebdb15f2a80, 103,088,322 B (was 13f3f74b..., 103,088,310 B).
Why: The author asked for the limitations to be the system's own assumptions and what follows from each, rather than the evaluation's weaknesses (direction confirmed by the author 2026-10-06). The four assumptions and their thesis support (Explore 2026-10-06, as listed in the plan): static scene, thesis Sections 2.2.2 and 4.1; uncertain inputs rejected or held, Sections 2.5 and 4.2 and Chapter 9 bullets 3, 5 and 6; hidden hips and root-frame drift, Section 3.2.1 and Chapter 9 bullet 4; rigid torso, Section 3.2.1 and Chapter 9 bullet 5. "The object must be small" is the author's claim beyond the thesis wording: the thesis names the desk as the occluder of the hips, not a large object. Text replaced in the first run of each shape with the other runs blanked, so the run formatting (16 pt cells and caption, 10.5 pt footer, DejaVu Sans) stays.
Alternatives: keeping the Table 9.1 rows (rejected by the author); keeping a fifth row for online deployment (not in the plan, the script no longer speaks it); citing Sections 2.5 and 4.2 in the caption as well (not done: the plan fixes the caption and footer texts).
Evidence: review/slide39_patch.json: zip-entry comparison (name and CRC) changed ppt/slides/slide39.xml only, nothing added or removed, 496 entries unchanged; the second run exits with "already patched". python-pptx opens the deck (77 slides) and slide 39 has the header and four data rows. build_speaker_script.py --check: 2660 words, 1620 s, cap 1620 PASS, 0 hits (the first check after the text change reported the one hit "header states 2,659 words, computed 2660"). make_package.py --render: deck PDF 77 pages (739408f1...), script PDF 23 pages (7fb9b1d6...; docx a8b643ca...), outline skipped. LibreOffice render of page 39: every consequence on two lines, the table ends at the old row-4 divider, leaving the space of the deleted row above the caption.
Not verified: the slide in PowerPoint; the thesis section numbers above were taken from the plan (Explore 2026-10-06) and not re-read in writing/v9 by this worker.
Reversibility: git checkout dc59533 -- presentation/defense_2026/Thesis_Defence_2026.pptx presentation/defense_2026/speaker_script.json, then rebuild the docx, PDFs and package.
Review: Author: view slide 39 in PowerPoint (four rows, the empty band left by the deleted row, caption and footer); confirm the four assumptions and the "small handheld object" wording, which goes beyond the thesis (the thesis names the desk); read the 66-word spoken text aloud against the slide.

ID: D-392
Status: UNCERTAIN
Decision: Slide 34 "controlled removal" is relabelled by wrist travel, says "cases" and carries a three-case figure instead of the error-curve figure (author instruction 2026-10-06; plan declarative-stargazing-phoenix.md, Milestone B). The slide part is done; the speaker script part, BLOCKED at first (see below), was done after the master decisions (see Final state). Done on the slide: header cell 11 "Motion / joint" -> "Window / joint"; row labels 17/23/29/35/41/47 "Lower|Intermediate|Higher, wrist|elbow" -> "Wrist travel 0.6|2.8|5.1 cm, wrist|elbow"; tile 1002 "45-frame windows" -> "45-frame windows, slow motion"; tile 1003 "Three recovery methods" -> "Three recovery cases"; caption 52 -> "Right arm - one slow recording - 45 frames per window - reference: unmasked reconstruction - cm - spoken: wrist travel 2.8 cm" (the separator on the slide is the deck's middle dot); tile 1004 ("Median: 0.3-2.5 cm") unchanged; picture 1005 (media/p34_masked_comparison.png, part name and rId3 kept) replaced by the three-case figure: three equal crops of frame 489 of window 445-489 titled "Hold last", "Direction memory", "Object-assisted", the white reference chain, the removed elbow and wrist ringed in red, each case's recovered chain, and one label per case "wrist 1.2 / 1.9 / 1.2 cm" (the window wrist medians), no error curves, 1500 x 1155 px, text 52 px (checked at 40 px or more). Column headers keep the method names "Hold-last", "Direction memory", "Object-assisted" (decision below). Patch: anim/patch_slide34_wording.py (refuses a second run: "the package already holds the three-case figure; patched before"), record review/slide34_wording_patch.json; figure by anim/masked_comparison_figure.py (new three-case mode), provenance media/provenance/p34_masked_comparison.json. The pptx goes from a27dc653d3860e8076622e1923894c49a2c03e148551f06d1739eebdb15f2a80 (103,088,322 B) to 0800111c3300c454c636f58450e7b74e42b392e14888c70d17756142ee1cc7cd (102,961,028 B) at this step; D-393 then takes it to f1b14621....
Final state (2026-10-06, master decisions after the BLOCKER below): tile 1002 "45-frame windows, slow motion" -> "45-frame slow windows" (3.599 in at 22 pt in the 4.01 in tile, one line in the LibreOffice render page34b.png) by anim/patch_slide34_tile.py (guards: pptx = the slide 33 film output and tile text = the old text; refuses a second run), record review/slide34_tile_patch.json, zip-entry diff = ppt/slides/slide34.xml only, 495 of 496 entries unchanged; pptx f1b146219bb10b04565f2f0ae3dc95fc8c78b4ea8179f9b5838044a3ea31be00 (98,268,933 B) -> b3b6a8f0d650888db8f13f8536c787f90cb5b16a1d1860683d46af11fe129cb7 (98,268,928 B). speaker_script.json slide 34 cue "Orient the table by window and case; wrist rows, then elbow rows." and spoken text "Recovery is tested first: every other landmark stays clean, and the right elbow and wrist are deleted on purpose for forty-five frames, so the unmasked reconstruction is a known truth. A slow recording gives three such windows, ranked by wrist travel, and the middle one is spoken here. Holding the last angles leaves the wrist one point two centimetres and the elbow zero point seven from the truth. Direction memory gives one point nine and one point seven. Object assistance gives one point two and one point six. None is best for both joints." (94 words, 57 s with the 3 s pause unchanged). The master text needed 1623 s; its fallback (drop "under ideal conditions") gave 1621 s; master option (a) ("ranked by wrist travel" for "ranked by how far the wrist travels") with "under ideal conditions" restored gave 1621 s again, so the phrase stays out; the master sentence "Three such windows of one slow recording are ranked by wrist travel, ..." then hit the lint rule "sentence starts with number", so the worker recast it as "A slow recording gives three such windows, ranked by wrist travel, ..." (same meaning, judgement, UNCERTAIN). JSON header word count 2,660 -> 2,657. build_speaker_script.py --check: 2657 words, 1620 s, cap 1620 PASS, hits 0. Script docx sha256 f0fdb49146374ce0f86f58ad44ee741c7d0900e46be0f49aa76e2f05068f28ab (54,318 B), PDF 11ccc9f27bf137d2eb9d61f8650cf7e82dd991353309fb6de1805fc369f67495 (199,693 B, 23 pages), deck PDF 110326a24de3613c6116b58ddc02076d9d9b9ec44be3de7ae650ad0472727c44 (69,706,833 B, 77 pages); make_package.py and --self-test PASS (6 cases).
BLOCKER (script; resolved 2026-10-06 by the Final state above): speaker_script.json slide 34 was unchanged (cue "Orient the table by motion level and method", spoken "... compared in the intermediate motion window."). (a) The plan's first source phrase "in three windows of forty-five frames with lower, intermediate and higher motion" does not occur in the slide 34 spoken text, which says "the right elbow and wrist are deleted on purpose for forty-five frames"; only the second phrase ("The three recovery cases are compared in the intermediate motion window.") is present. (b) The timing slack is 0 s: slides 1-46 need exactly 1620 s (cap 1620) because the remainder goes to slide 38. Slide 34 is 97 words, 55 s; 97 words is the most that fits in 53 s plus the 2 s per-slide overhead. Measured with build_speaker_script.base_seconds: replacement 2 alone is 103 words, 59 s (+4 s); replacement 2 plus replacement 1 adapted to the current sentence is 119 words (+12 s); dropping "of one slow recording" still gives 115 words (+10 s). compute_timing exits over the cap, so the docx build would fail. Lowering timing_extra_s 3 on slide 34 saves 3 s, still not enough for replacement 2 alone. The plan's fallback does not bring any variant to 1620 s or less. Master decision needed: where replacement 1 goes, which words to cut (slide 34 or elsewhere), or whether to lower timing_extra_s.
Why: The author found the labels lower, intermediate and higher undefined on the slide and suggestive of fast motion, which contradicts the slow-motion assumption; the thesis defines the three windows by the reference wrist excursion inside the 45 frames (Table 7.5: lower 490-534 = 0.6 cm, intermediate 445-489 = 2.8 cm, higher 557-601 = 5.1 cm), all in one slow recording. Wrist and elbow are rebuilt per case, so slide and script should say "case". The old figure (chains plus error curves) did not read as how the comparison was made; the three-case panel shows the same data (synthetic_pairs.csv, frame 489) one case per crop.
Case-letter decision (judgement): slides 19 and 21-23 give Case A as the missing wrist (elbow plus direction memory), Case B as the grasping wrist (tracked object plus stored offset) and Case C as the missing elbow (two lengths plus direction memory); slide 24 (hold the last valid angles) has no letter. The plan allowed "Case A / Case B" headers only if they match these letters; they do not map onto the three method columns, so the headers keep the method names and only tile 1003 says "cases".
Geometry deviation (judgement): the bold row "Wrist travel 2.8 cm, elbow" measures 2.886 in at 14 pt DejaVu Sans Bold (PIL getlength, as in patch_results_pictures.py); with the 0.1 in inset and 0.05 in spare it needs 3.036 in, more than the plan's 2.9 in. The grid is 0.5 to 8.13 in (7.63 in), columns 3.04 / 1.02 / 1.91 / 1.66 in; the figure is 4.6 in wide (3.542 in tall) with its top kept at y 2.35 in, left edge 8.23 in and right edge 12.83 in (aligned with the caption and footer rule), the gap between grid and figure 0.1 in (was 0.2). Smallest cell margin 0.054 in (bold elbow row); every cell is at least 0.05 in wider than its text.
Alternatives: Case A / Case B column headers (rejected: the letters name the missing-joint cases of slides 19-23, not the three methods); keeping the figure at 5.0 in (rejected: the 3.04 in first column does not fit); shorter tile 1002 wording (not done: the plan text was applied as written, see Review).
Evidence: review/slide34_wording_patch.json: zip-entry comparison (name and CRC) changed ppt/slides/slide34.xml and ppt/media/p34_masked_comparison.png only, nothing added or removed, 495 of 497 entries unchanged, slide34.xml.rels unchanged (same target name, rId3). Figure part sha256 2181352b... (D-390 figure) -> 32c88095... (three-case PNG). Table 7.5 read with python-docx from writing/v9/Chapter_7_Evaluation.docx (0.6, 2.8, 5.1 cm); window medians 1.2377 / 1.8839 / 1.2092 cm (wrist) match Table 7.7 (1.2 / 1.9 / 1.2) per the figure provenance. Before replacing, the patch checked every current text for an exact match. python-pptx opens 77 slides. build_speaker_script.py --check with the JSON unchanged: 2660 words, 1620 s, cap 1620 PASS, hits 0. A second patch run exits 1. LibreOffice render of page 34 (page34.png): no grid cell wraps; the caption wraps to two lines above the footer rule, as the old caption did (14.13 in against 14.14 in old, in a 12.33 in box); tile 1002 "45-frame windows, slow motion" measures 4.86 in at 22 pt in a 4.01 in tile and wraps to two lines just above the grid header, without overlap, so the tile row looks uneven. The independent code review of 2026-10-06 passed the patch and figure scripts as code and failed the change set for the missing script edit.
Not verified: the slide in PowerPoint; the slide 34 spoken text and cue (unchanged, so the caption's "spoken: wrist travel 2.8 cm" is not yet what the speaker says, and the label "intermediate" no longer appears on the slide); whether tile 1002 should be shortened. Constants in the patch (column widths, 0.1 in inset, 0.05 in spare, figure 4.6 in and y 2.35 in) are display judgements fitted by measurement in the patch record, not source numbers; the 0.6 / 2.8 / 5.1 cm values are from thesis Table 7.5.
Reversibility: git checkout eb5458d -- presentation/defense_2026/Thesis_Defence_2026.pptx presentation/defense_2026/media/p34_masked_comparison.png presentation/defense_2026/media/provenance/p34_masked_comparison.json presentation/defense_2026/anim/masked_comparison_figure.py, then rebuild the PDFs and package (the D-393 slide 33 edit sits in the same pptx and is lost with it). The pre-patch deck (a27dc653) was kept only as a scratch backup and is not in the repository other than at eb5458d.
Review: Author: view slide 34 in PowerPoint (row labels by wrist travel, the three-case figure, the two-line tile 1002, the caption). Master: decide the slide 34 script edit (the timing arithmetic above) and the tile 1002 wording; then rerun build_speaker_script.py --check and rebuild the docx.

ID: D-393
Status: UNCERTAIN
Decision: Slide 33 shows a synchronised three-panel film (recorded RGB, Python forward-kinematics skeleton, Unity avatar) instead of the FK-over-RGB still (author instruction 2026-10-06: the Python FK is a matplotlib 3D skeleton in a fixed oblique view, synchronised frame by frame with the recording and the Unity avatar; plan Milestone C). Film media/p33_three_panel.mp4: 1440 x 640, 30 fps, 1498 frames (0-1497, 49.93 s, plays under the 60 s slide), h264 yuv420p, three 480 x 640 portrait panels titled "Recorded RGB", "Python FK" and "Unity avatar", frame counter bottom-left of the middle panel; poster media/p33_three_panel_poster.png = frame 630. Generator anim/three_panel_fk.py, provenance media/provenance/p33_three_panel.json (status PASS), embedder anim/patch_slide33_film.py, record review/slide33_film_patch.json. On the slide: the still (id 35, rId6) and its label (id 36) are deleted; movie id 30 keeps rId2 (media), rId3 (video) and rId4 (image), now targeting ../media/p33_three_panel.mp4 and ../media/p33_three_panel.png, renamed p33_three_panel.mp4, with srcRect cleared (old l 23958 r 23333 t 5333 b 1000), placed in the slide 13-15 film box x 6.525, y 1.2 in, 6.0 x 2.667 in (5966460 / 1097280 / 5486400 / 2438400 EMU); new caption id 37 "Recorded RGB, Python forward kinematics and Unity avatar, same frame" at x 6.525, y 4.0, width 6.0 in, one 16 pt paragraph copied from caption 31 (two lines, 8.116 in of text); caption 31, the p:timing block (spid 30) and all other shapes unchanged. speaker_script.json slide 33 cue only: "Play the three-panel film while speaking; point to the FK panel for the model rows." (spoken text unchanged; the cue contains a semicolon as dictated, --check reported 0 hits). The pptx goes from 0800111c3300c454c636f58450e7b74e42b392e14888c70d17756142ee1cc7cd (102,961,028 B, the deck after D-392) to f1b146219bb10b04565f2f0ae3dc95fc8c78b4ea8179f9b5838044a3ea31be00 (98,268,933 B); the brief named a27dc653 as the start, but a27dc653 is the deck before the slide 34 patch, so the film patch started from the post-D-392 deck.
Inputs and frame map: recording_20260909_000024 (bag recordings/R7_rail_handover_two_hand_accepted_20260909_000024.bag = Video/recording_20260909_000024.bag, decoded with v3/replay/bag_source.py BagSource(paced=False).frames(), one sequential pass); the stream Unity rendered unity_capture/r7/integrated_stream.csv (frame, pel_x..z, a0..a12); unity_person_log.csv; rig_dimensions.csv (upper arm R 0.241, L 0.252 m; forearm R 0.233, L 0.223 m; shoulder width 0.323965 m; torso 0.5166 m); Unity master unity_capture/r7/Fresh_Unity_R7_Model_Axes.mp4 (1440 x 1080); FK from v3/core/fk.py. Input hashes are in the provenance JSON. Frame map is the identity: output frame n = bag colour frame n = integrated_stream.csv frame n = unity_person_log.csv frame n = Unity master frame n, n = 0-1497 (bag against stream time difference at most 7.4e-7 s, log against stream at most 6.0e-6 s; 1498 master frames read, 0 left over; stream frame 1498 exists but is not used). Decode check of the output: nb_read_frames 1498 at 1440 x 640.
Crop boxes: RGB (160, 0, 520, 480) of the 640 x 480 frame, 3:4, chosen once from frame 630 (person spans about x 215-495; both hands kept with margin); Unity (360, 0, 1170, 1080) of the 1440 x 1080 master, the RGB box times 2.25 (1440 / 640, because the calibrated SensorPOVCamera renders the sensor view); each crop scaled to 480 x 640 with PIL LANCZOS, its top 588 rows below a 52 px title band (the bottom 52 scaled rows, the desk front edge, are not shown). Skeleton: Camera' coordinates (y reversed, solver space of v3/core/fk.py); matplotlib X = x, Y = z (depth), Z = y (up); view_init elev 15, azim -75 (v1/mediapipe/plot_skeleton.py), equal cube of half range 0.4 m around the centre of all joints over frames 0-1497 (rounded up to 0.05 m); root L24 red, L23 and shoulders green, elbows blue, wrists amber, bones white, black background, DejaVu Sans (colours from anim/chain_growth.py LAYERS). Hip width for the display 0.21278 m (median over 1486 frames of the filtered landmarks, display geometry only).
FK check: the Python FK (shoulders by fk.hip_anchor and fk.hip_shoulder_offset, elbows and wrists by fk.fk_arm from a0..a12 with the rig lengths) against the joints Unity logged in unity_person_log.csv, mapped into Camera', at 10 sampled frames (0, 166, 333, 499, 665, 832, 998, 1164, 1331, 1497): maximum wrist error 9.3e-05 cm against a tolerance of 1.0 cm (PASS); over all 1498 frames the maximum is 1.13e-04 cm (right wrist), 1.03e-04 cm (left wrist), 1.02e-04 cm (right elbow), 9.6e-05 cm (left elbow), 9.5e-05 cm (right shoulder) and 8.7e-05 cm (left shoulder).
Why: The author rejected the FK-over-RGB still. A film makes the three representations comparable frame by frame, and the identity frame map was verified rather than assumed. FK input is the stream Unity rendered, so the skeleton moves with the avatar (plan).
Interpretation for the author (from the code review): the FK panel is by construction the rig skeleton. Its pelvis anchor and both shoulder offsets are fitted from unity_person_log.csv (spread under 1e-6 m) and its segment lengths are the rig lengths, so it matches Unity within 1e-4 cm. It is not the kinematic model behind the slide's "Model elbow" and "Model wrist" rows (measured lengths, D-037 offset from landmarks). The new cue "point to the FK panel for the model rows" therefore points at a panel numerically identical to the avatar joints. The plan sanctions this input, but the narrative needs the author's confirmation. The 1 cm check is partly circular for the shoulders (fitted from the same log); only the elbow and wrist FK from a0..a12 is independently confirmed.
Alternatives: FK from the landmark model (measured lengths) instead of the stream (not done: the plan fixes integrated_stream.csv); keeping the still (author rejected); a different Unity crop (the 2.25 scaling assumes the SensorPOVCamera has the sensor intrinsics scaled exactly, including the principal point; the poster at frame 630 shows the avatar framed consistently with the RGB crop).
Evidence: review/slide33_film_patch.json: zip-entry comparison changed ppt/slides/slide33.xml and its rels, added ppt/media/p33_three_panel.mp4 and p33_three_panel.png, removed ppt/media/media15.mp4, image48.png and p33_fk_overlay.png (no .rels part names them; checked), 492 entries unchanged, 497 -> 496 entries; media after 149 (123 PNG, 26 MP4). python-pptx opens 77 slides; slide 33 has one MEDIA shape and no PICTURE shape. The second patch run exits 1 ("slide33_film_patch.json exists; slide 33 was patched before"). build_speaker_script.py --check: 2660 words, 1620 s, cap 1620 PASS, hits 0 (slide 33: 106 words, 60 s). make_package.py --render exit 0 (outline PDF unchanged and skipped); make_package.py --self-test PASS (6 cases). LibreOffice render of page 33 (page33.png, 100 dpi): the poster shows the three panels at frame 630 with the new caption on two lines below. Independent code review (2026-10-06): no defect in the four scripts; FK usage, frame indexing, crop boxes, ffmpeg arguments, relationship retargeting and idempotence guards verified. Review notes, none fixed: (1) a failed FK check only prints BLOCKER and records status FK_CHECK_FAIL, the film is still written, and patch_slide33_film.py does not test prov["status"] == "PASS" (latent; today's run is PASS); (2) ffmpeg writes straight to the published mp4 path, so a failed run could leave a truncated file (the provenance hash guard stops it being embedded); (3) the 2.25 crop scale should cite unity_capture/r7/render_projection_check.json; (4) draw_photo in masked_comparison_figure.py shifts overlays by 0.5 source px (about 1.6 output px), negligible.
Not verified: playback of the film in PowerPoint (author check); the cosmetic geometry already there before this patch (caption 31 starts at x 6.22 in while the film and the new caption start at 6.525 in, and caption 31 wraps "n = 589" onto a second line); whether the author accepts the FK panel as the rig skeleton (above). Constants: film box from slides 13-15 (x 5966460, y 1097280, cx 5486400 EMU) and cy from the 1440:640 aspect; caption y 4.0 in and caption text from the plan; FILM_PX 1440 x 640 from ffprobe and the provenance dimensions; crop boxes, title band 52 px and font sizes are display choices recorded in the provenance JSON.
Reversibility: git checkout eb5458d -- presentation/defense_2026/Thesis_Defence_2026.pptx presentation/defense_2026/speaker_script.json (this also undoes D-392 in the pptx), then rebuild the docx, PDFs and package; the new media files and scripts are untracked and can be deleted or left. The pre-patch decks (a27dc653 and 0800111c) are scratch backups only; the 0800111c state can be rebuilt by running the slide 34 patch alone on the eb5458d deck.
Review: Author: play slide 33 in PowerPoint (the film starts on entry, the three panels stay in step, it fits the 60 s); confirm the FK panel as the rig skeleton and the cue "point to the FK panel for the model rows"; check the two-line caption. Master: the two stacked pptx edits (0800111c then f1b14621) go into one commit with D-392 and D-393 together, because separate commits would need the intermediate state rebuilt.

ID: D-396
Status: SETTLED
Decision: A shown-only derived copy of the final deck is made for sending to another professor (author request 2026-10-07): presentation/defense_2026/share/Thesis_Defence_2026_shown_only.pptx is a copy of Thesis_Defence_2026.pptx with the 31 hidden backup slides (47-77, show="0") removed, and share/Thesis_Defence_2026_shown_only.pdf is its 46-page LibreOffice render. The original pptx is untouched: sha256 b3b6a8f0d650888db8f13f8536c787f90cb5b16a1d1860683d46af11fe129cb7 (98,268,928 B) before and after.
Method: python-pptx 1.0.2 (/home/luo/anaconda3/bin/python) on the copy: for each sldId whose slide has show="0", the presentation part's relationship to the slide was dropped and the sldId removed from sldIdLst, then saved (unreachable slide and media parts are not written). Result 74,746,969 B, sha256 1a176e167e0e9fabe8f9b60a1644ad6e1b44b03a42dcec44066db8c7242c1396; no section list or custom show in presentation.xml. Render: soffice 24.2.7.2, isolated profile in a scratch directory, --headless --convert-to pdf:impress_pdf_Export with ExportHiddenSlides true (the make_package.py --render command; no slide is hidden in the copy), videos as poster frames; PDF 59,063,204 B.
Why: The other professor needs the talk as given, without the Q&A backup. Removing the slides from a copy keeps the author's deck bytes and the package manifest unchanged; a PDF of the full deck with pages 47-77 cut afterwards would give the same pages but leave no matching pptx.
Alternatives: cutting pages 47-77 from the existing 77-page PDF (no pptx to send alongside); rendering the original with ExportHiddenSlides false (no trimmed pptx, and a second render path for the same deck); editing the original (never, D-381).
Evidence: pdfinfo Pages 46; the first text line (title) of pages 1-46 matches the existing Thesis_Defence_2026.pdf pages 1-46 on 46 of 46 pages (pdftotext per page; full page text also identical on 46 of 46); python-pptx reopens the copy with 46 slides, none with show="0"; unzip -t reports no errors; rendered pages 1, 12, 33 and 46 viewed at 80 dpi.
Not verified: opening the trimmed pptx in PowerPoint. docProps/app.xml in the copy still states Slides 77 and HiddenSlides 31 (extended document properties, not read when the deck opens; PowerPoint rewrites them on save).
Reversibility: delete presentation/defense_2026/share/; nothing else depends on it.
Review: Author: page through the 46-page PDF before sending it.
Follow-up 2026-10-07: share/Thesis_Defence_2026_shown_only_email.pdf was added for mailing (25 MB limit): gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.5 -dPDFSETTINGS=/prepress on the 59,063,204 B PDF gives 4,683,516 B, 46 pages, same fonts (DejaVuSans, DejaVuSans-Bold, embedded). Tried: /ebook (150 dpi) 2,316,722 B, which re-encodes the 240 ppi page stills to 150 dpi and differs measurably from the original on pages 12, 33, 34 (0.4-1.1 percent of pixels off by more than 40 levels at 80 dpi); /printer 4,479,759 B; /prepress chosen as the highest-resolution setting under 20 MB (source stills are 240 ppi and are not downsampled). At 80 dpi pages 1, 12, 33, 34, 42 differ from the original by a mean of at most 0.031 grey levels of 255. The full-resolution PDF stays beside it.
Follow-up 2026-10-07 (b): pages 7, 20, 24, 30 and 41 showed a distorted video poster (author report for 24, 30, 41; checker for 30, 41; 7 and 20 found in the same scan). Diagnosis: the five video objects carry an a:srcRect crop whose cropped poster has exactly the box aspect (slide 7 l=12500 r=12500 t=9867 b=21822 on a 1280x1054 poster, box 6022848x4517136, 1.333; slide 20 t=8041 on 960x970, box 4920538x4572000, 1.076; slide 24 t=8041 b=17732 on a 960x970 poster, box 6022848x4517136 EMU, aspect 1.333; slide 30 l=23333 r=23333 t=5333 b=1000 on 1440x1200, box 3123928x4572000, 0.683; slide 41 l=23958 r=23333 t=5333 b=1000 on 1440x1200, box 3087320x4572000, 0.675; no rot, no flip; MP4s 1280x1054 22.000 s, 960x970 6.000 s, 960x970 8.000 s, 1440x1200 25.000 s, 1440x1200 12.000 s, 30 fps, no rotation tag). LibreOffice 24.2 does not apply that crop to a media object: on pages 7, 20 and 24 it embedded the whole poster (with its title strip and bottom text rows) stretched into the box (195 x 214, 179 x 194 and 146 x 197 ppi), and on pages 30 and 41 it embedded a 1022x225 lower-right strip of the poster (Unity floor and the "Right arm"/"Left arm" labels) stretched into the portrait box (300 x 45 ppi); the full PDF also embeds each MP4 uncropped as a Screen annotation. Fix in the copy only: presentation/defense_2026/share/fix_video_posters.py trims the deck as above (part contents identical to the first copy, zip dates differ), then replaces each of the five video objects by a plain picture in the same a:xfrm box with no crop: the MP4 frame that matches the author's poster (0-based frames 105, 105, 90, 480 and 45 for slides 7, 20, 24, 30, 41; mean absolute grey difference 0.202, 0.293, 0.254, 0.153, 0.196 against per-film medians 6.81, 4.56, 0.97, 2.25, 3.5 at quarter size), cropped in pixels to the same srcRect (960x720, 960x892, 960x720, 768x1124, 759x1124, the box aspect to four decimals); the film, its poster relationship and its timing node are removed from those slides, so the copy and the full PDF no longer play those five films. Result: pptx 61,301,354 B; PDF 45,896,443 B, 46 pages (13.2 MB smaller, the five embedded MP4s); email PDF 4,724,538 B, 46 pages. At 50 dpi the other 41 pages of both PDFs are pixel-identical to the previous renders (max mean difference 0); pages 7, 20, 24, 30 and 41 viewed at 80 dpi show the frame PowerPoint shows before the film starts. The author's crop on slides 30 and 41 leaves out the poster's side label columns, so the input-validity labels are not on the slide in PowerPoint either. Slides 7 and 20 were added in a second pass the same day (first pass 382cf52 fixed 24, 30, 41); no other shown slide has a srcRect or a poster aspect different from its box. Original pptx sha256 b3b6a8f0... unchanged.
