# Unity replay evidence

Currency note (2026-10-08): This folder retains replay evidence and capture
procedures from earlier presentation rounds. References below to active
pages 27, 47 and 41 are their original deck bindings, not current page
assignments. Read [the final presentation README](../README.md) for current
navigation and delivery limits. Source manifests, captured outputs and
required-checker findings keep their original scope; no capture or playback
was rerun for this documentation update.

The active deck uses two distinct replay paths. Pages 27 and 47 retain the checked R7 fresh capture. Page 41 now uses [r5_archived/capture_manifest.json](r5_archived/capture_manifest.json): a new engine rendering of the exact archived integrated packets and archived rig dimensions. The earlier fresh R5 capture is preserved for history and is no longer the active page 41 film.

The archived R5 path applies all thirteen body coordinates, pelvis position, object pose and binary validity directly. It runs no new solve and no additional smoothing pass. Its geometry is right upper arm/forearm 0.256/0.252 m, left 0.262/0.247 m and torso 0.479 m, as documented in the archived sizing source. No newer recovery tags are imported. The calibrated sensor-view camera and capture-only model axes retain their separate logs.

Validation is qualified: archived packet/bone application 11 PASS, sizing 12 PASS, visible-axis raster agreement 131 PASS with four exclusions, and the unchanged required application checker 7 PASS / 1 FAIL. The failed historical concentration of left-hand disagreement is retained; it is not waived or changed into an anatomical accuracy claim. Historical exact pixels are not claimed. See [the retained finding](r5_archived/REQUIRED_CHECKER_FINDING.md), [code review](../review/BANK_REVISION_P41_CODE_REVIEW.md) and decision D-066.

The completed archived capture retains frames 0-2097; page 41 pairs RGB and Unity frames 900-1649. Terminal source 2098 is absent under the existing capture loop. The following commands reproduce this isolated path after prepare_project.py has made the temporary capture project. They are a regeneration procedure, not required for building a deck from supplied movies.

    /home/luo/anaconda3/bin/python presentation/defense_2026/unity_capture/capture_archived_r5.py launch
    /home/luo/anaconda3/bin/python presentation/defense_2026/unity_capture/capture_archived_r5.py finish
    /home/luo/anaconda3/bin/python presentation/defense_2026/unity_capture/validate_archived_replay.py
    /home/luo/anaconda3/bin/python presentation/defense_2026/unity_capture/validate_render_projection.py presentation/defense_2026/unity_capture/r5_archived
    /home/luo/anaconda3/bin/python presentation/defense_2026/unity_capture/finalize_archived_capture.py
    /home/luo/anaconda3/bin/python presentation/defense_2026/anim/axes_archived_unity.py
    /home/luo/anaconda3/bin/python presentation/defense_2026/unity_capture/validate_archived_media.py
    /home/luo/anaconda3/bin/python presentation/defense_2026/unity_capture/finalize_archived_capture.py

Fresh-capture commands and earlier findings follow unchanged for reproducibility. Their R5 results describe that earlier input/configuration and do not certify the current archived-packet replacement. The independent code review identifies two bounded launcher-readiness improvements for a future run; the completed current capture is checked from immutable output and source-frame logs.

# Preserved fresh-capture procedure

This harness makes a separate Unity project under /tmp/defense_axes_capture. It copies the frozen receiver and changes only capture instrumentation, output paths and private IPC names. It replays saved recovery angles using the existing display smoother and the recording's own five sizing lengths. These are newly rendered demonstrations, not new tracking experiments or the archived Table 7.4 renders.

The root triad is attached to the rendered pelvis and labelled Pelvis_parallel_L24. It is not a measured right-hip origin. Shoulder triads inherit the root orientation; elbow triads carry the composed shoulder orientation. The axes precede each bone's authored rest rotation. The CSV records actual bone orientation separately. No wrist-orientation triad is drawn.

Axis colors are x red (#FF4040), y green (#40E070), z blue (#408CFF). The explanatory axes remain visible through the mesh; this does not claim that the corresponding anatomical location is visible. Axis length 0.12 m and line width 0.004 m are illustrative display settings, not measurements. The 1440 by 1080 capture target preserves the sensor view's 4:3 aspect ratio. Source replay runs at one-quarter speed to permit complete capture; exported video returns to the original 30 fps source timing. Group-state captions use saved recovery tags. Original receiver spheres distinguish only live from non-live.

Reproduce from the repository root. Choose r7 or r5 as the final argument to both launch and finish commands:

    /home/luo/anaconda3/bin/python presentation/defense_2026/unity_capture/prepare_project.py
    /home/luo/anaconda3/bin/python presentation/defense_2026/unity_capture/run_capture.py r7
    /home/luo/anaconda3/bin/python presentation/defense_2026/unity_capture/finish_capture.py r7

The launcher refuses to share an existing capture editor and archives previous temporary PNGs/logs before a new run. It does not stop unrelated editors or senders. Process IDs are recorded in the selected recording's processes.json. Intermediate PNGs stay under /tmp/defense_axes_capture/r5_frames; the final argument selects the recording even though this copied runtime path retains its historical name. The finisher stops only the launched processes, archives logs and selected stills, and executes the matrix, rig sizing and original Unity checks.

Export R7 source frames 0-1497:

    ffmpeg -y -v error -framerate 30 -start_number 0 -i /tmp/defense_axes_capture/r5_frames/f%05d.png -frames:v 1498 -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -threads 2 -movflags +faststart presentation/defense_2026/unity_capture/r7/Fresh_Unity_R7_Model_Axes.mp4
    /home/luo/anaconda3/bin/python presentation/defense_2026/unity_capture/validate_render_projection.py presentation/defense_2026/unity_capture/r7
    /home/luo/anaconda3/bin/python presentation/defense_2026/unity_capture/finalize_manifest.py

For R5, export 2098 frames to r5/Fresh_Unity_R5_Model_Axes.mp4 and pass the r5 directory to the projection validator, then run finalize_manifest.py r5. The final recording sample is not retained by the existing capture loop. Ten PNG review stills are retained per recording; full intermediate PNGs remain in /tmp.

R7 validation: all 12 sizing checks pass; independent calibrated matrix, origin and source-time checks pass. The unchanged original check_unity_log.py reports 7 passes and 1 failure. Its sole failed assertion expects the R5-specific pattern of left-hand disagreement exceeding three times the clean-frame value on torso-failure frames. Fresh R7 does not exhibit that pattern. Exact frame application, recorded coverage, anchor placement and both clean-frame tracking checks pass. The original report is preserved; its failed historical outcome is not redefined as a passing test and does not establish a coordinate application error.

Use source_group_states.csv to caption measured/held/constrained provenance. These are saved recovery states before the original display smoothing, not newly measured tracking states. Fresh R7 uses all five R7 dimensions; archived R7 footage used an older arm-sizing configuration. Fresh replay clips must not inherit the archived numerical result captions.

R5 retains source frames 0-2097 from 2099 streamed samples. Terminal frame 2098 is excluded by the existing capture loop. R7 retains 0-1497 from 1499 samples, excluding terminal frame 1498. Neither clip claims every sample of its recording.

R5 validation: the original Unity checker passes all 8 checks, all 12 sizing checks pass, and independent matrix/origin/time and rendered-projection checks pass. These are application diagnostics rather than new accuracy results.

Raw editor logs, stdout, sender logs and process metadata are excluded from version control by the local .gitignore. They can include licensing/session identifiers. This capture's originals are retained under /tmp/defense_axes_capture/private_runtime_logs. Scientific frame, angle, pose, calibration, sizing and matrix logs are retained unchanged. Reproducible validation reports provide the publishable diagnostics.
