# Synchronized filter demonstrations

Currency note (2026-10-08): This is a retained source-asset description.
Its intervals, filter calculations, timing and provenance remain scoped to
the original demonstrations. References below to current demonstrations or
supplied supplementary assets describe that earlier delivery, rather than
certifying their placement in the final deck. Current delivery facts and
verification limits are in [README.md](README.md).

These six videos combine actual recorded R6b camera images with calculated right-wrist samples in a single MP4. Camera and plot use exactly the same source-frame mapping, including every pause. A curve never reveals a sample beyond the displayed camera frame. The earlier independent camera clips and staged GIFs remain supplied as historical supplementary assets; they are superseded for the current filter demonstrations.

| Media basename | Source frames, inclusive | Axis | Shared event pause | Output duration |
| --- | --- | --- | --- | --- |
| filter_hampel_sync | 450-549 | Depth z | Frame 537 | 18.700 s |
| filter_gap_sync | 650-749 | Camera x | Frame 685 | 18.700 s |
| filter_butterworth_sync | 25-179 | Depth z | None | 18.366667 s |
| filter_one_euro_sync | 25-179 | Depth z | None | 18.366667 s |
| filter_savgol_sync | 25-179 | Depth z | None | 18.366667 s |
| filter_median_sync | 25-179 | Depth z | None | 18.366667 s |

Each basename has an MP4 and PNG poster in media/. The 1440x1200 composite is designed for the 6.61x5.50-inch right evidence area. Camera images retain their complete native 640x480 pixels; no inferred wrist marker is added. Internal labels use normal-weight DejaVu Sans. Input is gray; output is muted blue; rejected inputs use amber crosses; interpolated samples use hollow blue markers. The poster shows the last source frame and the completed trace from that same interval.

The common playback rate is 0.5x the audited recording clock, quantized to 30 output frames per second. Both components share a three-second opening hold and five-second final hold. Hampel and interpolation also share a four-second event hold. These durations and holds are editorial choices under D-036, not measured computation times. A single encoded timeline removes drift between independently started PowerPoint media.

The calculations retain the saved parameters in FILTER_DEMO_BRIEF.json and the frozen functions in v1/mediapipe/filter_landmarks.py. They are isolated operations on recorded input, not a new validation of the complete preparation pipeline. Hampel removes the flagged sample rather than replacing it with a median. The interpolation window contains missing frames 674, 678 and 681-684; only the last group is the four-frame focus. Raw gaps remain disconnected. Explicit repaired output can span them and remains marked as inferred.

Butterworth, Savitzky-Golay and median process the complete valid run 25-549 before displaying 25-179. Their output is retrospective and can use samples later than the visible cursor. Progressive playback does not make those methods causal. The One Euro helper processes the recorded sequence and resets at frame 25 after missing frames 11-24. Its first displayed sample initializes that valid run; later outputs use the received prefix. It can still lag. None of these videos is a recording of a running filter GUI or a new accuracy experiment.

The camera cache was independently checked against the original bag in media/provenance/recorded_context_source.json. Every selected cached JPEG is hash-checked again. Each media/provenance/<basename>_frames.csv maps every output frame/time to the identical camera frame, plot endpoint and source timestamp. The corresponding _trace.csv records raw/output values and flags. The per-asset reports contain complete decoding results, source/media hashes, measured label bounds, every visible trace endpoint, and first/middle/last/event decoded-frame comparisons with the source composition. H.264 is lossy, so those comparisons report channel error rather than claiming byte-identical decoded pixels.

review/FILTER_SYNCHRONIZED_CHECK.json collects the generation checks. The separately implemented review/FILTER_SYNC_MAPPING_CHECK.json checks every mapping row, pause, progression timestamp and numerical trace against the original audit and frozen helper results. The earlier 53 media files were hash-checked and preserved.

From the repository root:

    /home/luo/anaconda3/bin/python presentation/defense_2026/anim/filter_synchronized.py preview
    /home/luo/anaconda3/bin/python presentation/defense_2026/anim/filter_synchronized.py build
    /home/luo/anaconda3/bin/python presentation/defense_2026/anim/validate_filter_sync.py

Building from supplied MP4s needs no original bag. Regeneration needs the documented camera cache. If that temporary cache is absent, the existing read-only extraction and audit require the local original bag and RealSense environment:

    /home/luo/anaconda3/envs/v3rt/bin/python presentation/defense_2026/anim/causal_replay.py extract --start-frame 0 --duration 30
    /home/luo/anaconda3/envs/v3rt/bin/python presentation/defense_2026/anim/recorded_context.py audit-source

The source audit reports 899 decoded image pairs; no new dropped-frame conclusion follows from that tail count. The displayed windows all lie within the audited cache. Do not replace missing source footage with fabricated camera imagery.
