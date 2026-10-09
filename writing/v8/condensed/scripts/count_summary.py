#!/usr/bin/env python3
"""Before/after word counts for the condensed thesis.

Baseline = the chapters the condensed builders were copied from (v8 for
Chapters 2-5, v7 for the rest) and, for reference, V7 as sent. Counts by
count_words.py: prose paragraphs, captions, headings, table text.
Main body = Chapters 1-9 (prose + captions + tables, headings excluded);
total = main body + front matter (abstract and lists) + appendices.

Run: python3 writing/v8/condensed/scripts/count_summary.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from count_words import count
W = Path(__file__).resolve().parents[3]
C = W / "v8" / "condensed"
CH = [("1 Introduction", "Chapter_1_Introduction.docx", "v7"),
      ("2 Experimental Setup", "Chapter_2_Experimental_Setup.docx", "v8"),
      ("3 Kinematic Modelling", "Chapter_3_Kinematic_Modeling.docx", "v8"),
      ("4 Object Tracking", "Chapter_4_Object_Tracking.docx", "v8"),
      ("5 Pose Recovery", "Chapter_5_Pose_Recovery.docx", "v8"),
      ("6 System Integration", "Chapter_6_System_Integration.docx", "v7"),
      ("7 Evaluation", "Chapter_7_Evaluation.docx", "v7"),
      ("8 Real-Time Feasibility", "Chapter_8_Real_Time_Feasibility.docx", "v7"),
      ("9 Discussion", "Chapter_9_Discussion.docx", "v7", "Chapter_9_Discussion_Conclusion.docx"),
      ("10 Conclusions and Future Work", "Chapter_10_Conclusions_Future_Work.docx", "v7", None)]
def body(c): return c[0] + c[1] + c[3]
rows = []; tb = tv7 = ta = 0
print("| Chapter | V7 as sent | Baseline (source) | Condensed | Cut vs baseline |")
print("|---|---|---|---|---|")
for row in CH:
    # Since 2026-09-10 (D-022) the old Chapter 9 is split into Chapters 9
    # and 10; the V7 baseline of both is the old Chapter 9 file, counted
    # once against Chapter 9 and zero against Chapter 10.
    title, fn, src = row[:3]; v7fn = row[3] if len(row) > 3 else fn
    v7 = body(count(W / "v7" / v7fn)) if v7fn else 0
    base = body(count(W / src / v7fn)) if v7fn else 0
    after = body(count(C / fn))
    tv7 += v7; tb += base; ta += after
    cut = f"{100*(base-after)/base:.0f}%" if base else "n/a"
    print(f"| {title} | {v7:,} | {base:,} ({src}) | {after:,} | {cut} |")
print(f"| **Main body** | **{tv7:,}** | **{tb:,}** | **{ta:,}** | **{100*(tb-ta)/tb:.0f}%** (vs V7 as sent {100*(tv7-ta)/tv7:.0f}%) |")
ap7 = body(count(W / "v7" / "Appendices.docx")); apc = body(count(C / "Appendices.docx"))
fm7 = count(W / "v7" / "FrontMatter_V7.docx"); fmc = count(C / "FrontMatter_V8_Condensed.docx")
fm7b = fm7[0] + fm7[1]; fmcb = fmc[0] + fmc[1]
print(f"| Appendices | {ap7:,} | {ap7:,} (v7) | {apc:,} | {100*(ap7-apc)/ap7:.0f}% |")
print(f"| Front matter (abstract, lists) | {fm7b:,} | {fm7b:,} (v7) | {fmcb:,} | {100*(fm7b-fmcb)/fm7b:.0f}% |")
print(f"| **Total** | **{tv7+ap7+fm7b:,}** | **{tb+ap7+fm7b:,}** | **{ta+apc+fmcb:,}** | **{100*((tb+ap7+fm7b)-(ta+apc+fmcb))/(tb+ap7+fm7b):.0f}%** |")
