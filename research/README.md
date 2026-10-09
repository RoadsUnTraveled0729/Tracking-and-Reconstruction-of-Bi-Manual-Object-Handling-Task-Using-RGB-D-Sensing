# research/

Research-direction memos written after the thesis was delivered. They are
advice for the author, not thesis content: nothing here feeds writing/v9,
the defence deck or the code tracks without an explicit decision.

- RESEARCH_DIRECTIONS_2026-10-01.md: ranked directions for follow-up
  publications starting from the thesis (Chinese; paper titles, methods and
  dataset names in English), with a first-paper plan and a verified
  reference list.
- RESEARCH_DIRECTIONS_2026-10-01_verdicts.md: the nineteen candidate topics
  behind that memo and the three skeptic verdicts (novelty, feasibility,
  venue fit) recorded for each, with the prior work the skeptics found.

Field-first study (started 2026-10-01 at the author's request, superseding the
thesis-first starting point of the memo above):

- FIELD_PAPERS_2026-10-01.md and field_papers_2026-10-01.json: step 1, the
  1563-paper inventory of what the listed venues published in 2024-2026, with
  per-scout coverage notes.
- FIELD_THEMES_2026-10-01.md and field_themes_maps_2026-10-01.json: step 2a,
  what the venues are doing: twelve research lines with momentum, seven
  subfield maps, sensing and dataset shifts, community differences, crowded
  and rare areas.
- FIELD_PAINPOINTS_2026-10-01.md and field_painpoints_2026-10-01.json: step 2b,
  the stated limitations, open problems and benchmark gaps of 296 dataset,
  benchmark, survey and challenge papers read in full text, with verbatim
  quotes in the JSON.
- field_painpoint_clusters_2026-10-01.json (110 group clusters),
  field_painpoints_merged_2026-10-01.json (40 field-level pain points) and
  field_painpoints_verified_2026-10-01.json (web evidence, three skeptic
  verdicts and the small-lab fit per pain point): steps 3a-3c.
- field_painpoint_cards/P01.md to P40.md: one traceable Chinese card per pain
  point (step 3d).
- FIELD_MAP_2026-10-02.md: the ranked field map, the study's final deliverable:
  eight directions worth pursuing with go/no-go pilots, the full pain-point
  table, per-pain-point evidence, the relation to the earlier memo, and the
  coverage limits.

## Evidence sheets (2026-10-07)

Written after the author asked for evidence instead of judgments. Every
statement carries a verbatim quote, a source and a URL, and the sheets
mark which statements remain judgments.

- CVPR_BAR_AND_BERKELEY_2026-10-07.md: what the CVPR 2025 and 2026
  reviewer and author guidelines ask for; the experimental content of
  five accepted 2025 CVPR and ICCV hand-object and body-object papers
  (datasets, baselines, ablations, code, pages); what six current PhD
  students of the Berkeley Kanazawa and Malik groups had published
  before applying (individual cases, not a sample); the Berkeley EECS
  PhD application package for Fall 2027.
- EVIDENCE_CHECK_2026-10-07.md: twenty-five claims made to the author in
  conversation (the field's stated occlusion problem, the Berkeley models
  and their weaknesses, the novelty of the proposed paper and the known
  swivel-angle redundancy, venue acceptance rates, Berkeley admissions
  and people, the advisor and the committee precedent, the thesis's own
  limitations), each with verbatim evidence, a skeptic's objection and
  a corrected statement; section 3 lists what remains a judgment and
  section 4 what the evidence changes in the proposed paper. Six claims
  were refuted or narrowed, among them "the authors admit it" for HaMeR
  and 4D Humans, "HMR was the first", "Berkeley has no MS-only
  programme", and the broad reading of the novelty claim.
- BERKELEY_LITREVIEW_2026-10-07.md: literature review written from the
  Berkeley groups outward, not from the thesis: what the Kanazawa, Malik
  and human-video-to-robot groups published in 2025-2026 (42, 82 and 56
  papers, overlapping), the fifteen open problems they state in their
  own limitation sections with verbatim quotes, nine candidate paper
  directions proposed through three lenses, each judged by two skeptics
  (already done; no result in reach), the two survivors (an executability
  error budget for human-video robot data; carrier-hand inference through
  occlusion and handover) with their nearest prior work, and the seven
  refuted candidates with the decisive reason each.
- GPU_RENTAL_2026-10-07.md: where and how a student in Canada rents one
  GPU for the pilot (days) and the full experiment (weeks): provider
  comparison with prices quoted from the providers' own pages on
  2026-10-07 (RunPod, Vast.ai, Lambda, DigitalOcean, Paperspace, Colab,
  Hyperstack, Denvr, OVHcloud, the Alliance and PAICE free routes), the
  recommended card per phase with cost estimates, the step-by-step
  RunPod procedure, and the tax, egress and idle-charge caveats.
- C3_NOVELTY_2026-10-07.md: thorough novelty check of the narrowed C3
  claim (carrier-hand inference through occlusion and handover, causal,
  per-frame provenance, downstream robot benefit): six search angles,
  70 unique candidates, 16 deep-read with a four-filter table, judge
  verdict PARTLY_COVERED (Object Permanence Filter ICRA 2024 and the
  KAIST hand-guided tracker APMAR 2025 already hold three and two of the
  four ingredients), the surviving claim, and what would kill it.
- C3_SETUP_2026-10-07.md: audit of the public code (SPIDER, Do as I Do,
  FoundationPose, HaMeR, WiLoR, HaWoR, SAM 3D, MuJoCo Warp) and datasets
  (HOT3D, HO-Cap, OakInk2, DexYCB, ARCTIC, SPIDER reference packs):
  licences, gating, environment, memory, what runs on one rented
  24 to 32 GB GPU this week, which registrations the author must do.
- UBC_ADMISSIONS_2026-10-07.md: UBC, Toronto, Waterloo and Alberta research master's rules side by side
  (CS MSc, ECE MASc, Mechanical MASc, Biomedical Engineering MASc):
  supervisor rule in each department's own words, deadlines for
  September 2027 entry, materials, funding guarantees, thesis, direct
  PhD entry, MEng in one line; plus Xue Bin Peng's recruiting statement.
- CANADA_LABS_2026-10-07.md: Canadian university labs and industry groups
  publishing in 2024-2026 on 3D humans and hands, hand-object
  interaction, robot learning from human video and humanoids: 82 lab
  entries scouted by region and by venue, skeptic-checked, three ranked
  HIGH (Peng, Herzig, Li Cheng) with recruiting statements quoted, the
  engineering-department options listed separately, industry paths,
  and the funding and deadline facts the pages state.
- ENGINEERING_ROUTE_2026-10-07.md: the engineering route: Berkeley
  College of Engineering robotics groups outside the CS side (Sreenath,
  Tomizuka, Abbeel, Goldberg, Sastry, Stuart) with 2025-2026 topics,
  whether they use human video, hardware, admitting programme and
  deadline; Canadian engineering-department groups in the direction
  (35 scouted, ranked after a skeptic pass); the difference between the
  engineering and CS routes in venues and readers.
- UBC_ENGINEERING_FACULTY_2026-10-07.md: UBC engineering faculty in the
  direction, enumerated from the official Mechanical, ECE and Biomedical
  Engineering directories and verified one by one (status, 2024-2026
  papers, human data from cameras, hardware, US links, recruiting
  statement, admitting programme), ranked, with the people who left or
  retired and the differences from the two earlier surveys.
- FINAL_ENGINEERING_SHORTLIST_2026-10-07.md: the engineering-route
  shortlist across UBC, Waterloo, Alberta and SFU (Toronto excluded by
  the author), ranked by direction fit, US ties, recruiting statement
  and the department's supervisor rule; one line per excluded person
  with the deciding quote; per-school first step; a frank assessment of
  the gap between the author's aim and what Canadian engineering
  departments offer.
