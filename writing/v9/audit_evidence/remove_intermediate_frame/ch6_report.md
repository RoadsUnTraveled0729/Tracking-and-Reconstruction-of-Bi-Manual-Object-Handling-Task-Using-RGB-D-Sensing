STATUS: COMPLETE

GOAL:
Remove the intermediate Chapter 6 coordinate frame and clarify Figure 6.4.

KEY FINDING:
The five retained frame names and explicit G/t_f operations reproduce the
same final Scene mapping and numerical example.

VERIFIED:
PASS 71 checks in ch6_checks.json. Numbered equations 6.1-6.5 retain their
baseline OMML exactly. Equation 6.6 now includes G and t_f together. The
rebuilt DOCX embeds the new figure and has no removed-frame term. The
Chapter 6 style checker reports zero findings.

ASSUMPTIONS/UNRESOLVED:
The authored bone axes and full rig spawn-axis coincidence remain an
explicit assumption. Captured position logs do not provide complete bone
orientation matrices. Assembled page layout is the parent agent's check.

DECISION:
Apply D-082: G is a proper rotation operation, t_f=(0,d,0)^T is the
recording-specific floor placement, and T(Scene,Unity)=[G,t_f;0,1].

NEXT:
Integrate the Chapter 6 part and inspect the taller Figure 6.4 in the
assembled PDF, then resume the separately deferred correctness iteration.

Reason:
Removing a named intermediate frame does not remove its gravity operation.
The full homogeneous transform applies gravity and floor placement once.
Its inverse restores the original input point.

Evidence:
- Baseline numerical snapshots and source hashes are in ch6_values_before.json
  and ch6_baseline_manifest.json. Existing example values agree within
  1e-9 m; the final pelvis difference is 3.2526065174565133e-19 m.
- The frozen forward-kinematics function matches the right/left upper-arm
  and forearm frame chains over all 900 finite recorded angle rows.
- The full transform matches the global hip positions in the pinned rail
  and handover capture logs within the existing 2e-6 m storage tolerance:
  maximum component discrepancies 1.2092928349406035e-6 m and
  1.1685394189961916e-6 m respectively.
- Receiver source checks confirm global anchor/bone rotations and pelvis
  application, with object poses applied locally under the scene parent.
- The exact floor offsets from the calibration remain 0.716215 m and
  0.709312 m when reported to six decimals; Chapter 6 keeps its established
  centimetre precision.
- Figure 6.4 was visually inspected after regeneration. All five frame
  labels, operation boxes, arrows, handedness labels and shared origins are
  clear at the intended 6.4-inch width. No physical triad is invented.
- ch6_docx.txt was read end to end. Prose/caption/table count changed from
  5427/393/265 to 5377/404/262 words; numbering is unchanged.

Therefore:
The removal is a mathematical presentation refactor with the original
experimental data, receiver behavior, kinematic chain and final coordinates
preserved. It does not resolve the pre-existing authored-axis assumption.

Reproduction:
Run the five thesis-Python commands at the end of notes_revision_ch6.md.
The checks hash all read sources and write ch6_checks.json. Build and number
trace logs are stored beside this report.

Git:
No Git action or full-thesis assembly was performed by this chapter worker.
