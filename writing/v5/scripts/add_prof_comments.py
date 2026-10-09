"""Restore the supervisor's Part 1 review comments into the built docx, each
followed by a short reply stating what changed.

Source of the comments: writing/v5/PROF_COMMENTS_PART1.md (the 65 PDF
annotations of Thesis_V4_Part1_Ch13_1_1sp.pdf, extracted verbatim). Adjacent
highlight/strikeout + text-popup pairs that marked the same passage are merged
into one site, giving 48 comment sites. Each site carries:
  anchor : a substring of the CURRENT revised text at the spot the fix landed
           (deleted passages anchor at their replacement text)
  prof   : the supervisor's annotation, verbatim; text-less highlights and
           strikeouts are restored as [Highlighted: ...] / [Struck out: ...]
  reply  : what changed, one or two short sentences

Comments are authored "Shahram Payandeh"; replies "Lanqing Luo". Replies are
threaded under the professor's comment through a commentsExtended part
(w15:paraIdParent), the mechanism Word itself uses.

Run from writing/v5/scripts after build_thesis.py. Produces
Thesis_V5_Part1_commented.docx and Thesis_V5_commented.docx (the clean builds
are not modified) plus PROF_REPLIES_PART1.md.
"""
from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE as RT
from docx.opc.packuri import PackURI
from docx.opc.part import Part
from docx.oxml.ns import qn

BASE = "/home/luo/Desktop/New_SandBox/writing/v5/"

PROF = "Shahram Payandeh"
ME = "Lanqing Luo"

COMMENTS = [
# ---- p10-p11: chapter organization and Ch2 opening --------------------------
dict(page="p10",
     anchor="It describes the physical capture setup and the recorded data",
     prof='[Struck out: "How each of these components works internally is a matter of perception machinery rather than of the kinematic model or the system design, so that material is collected in the Appendix. This chapter states only what each component delivers to the rest of the system."] '
          "when you go over each subsections, you can refer the reader to the designated appendix. No need to say anything here.",
     reply="Removed that passage. Each subsection now just points to its own appendix."),
dict(page="p10",
     anchor="1.4 Organization of the Thesis",
     prof="you should add a subsection calling it Organization of the Thesis. Then, you can add the material which you present at the beginning of Chapter 2 here.",
     reply="Added Section 1.4 Organization of the Thesis and moved the chapter overview from the start of Chapter 2 into it."),
dict(page="p10",
     anchor="Chapter 2 describes the experimental environment",
     prof="you should also add some information about the Thesis organization at the end of Chapter 1 which gives an overview of what each Chapter is all about and how they are organized.",
     reply="Section 1.4 now goes through the chapters one by one and says how they fit together."),
dict(page="p11",
     anchor="Three recordings are used in this thesis",
     prof='[On: "synthetic operation."] you have not defined this yet.',
     reply="Removed the term. The three recordings are now described plainly here and in Table 2.1."),
dict(page="p11",
     anchor="Figure 2.1 shows the overall data flow.",
     prof="try to use simpler language at your level. This sounds like AI generated. Yo can ask it to rewrite in more at your level of English and educations.",
     reply="Rewrote this opening in simpler language and did the same pass over the rest of the chapter."),
# ---- p13-p15: replay, smoothing, data integrity -----------------------------
dict(page="p13",
     anchor="One replay detail affects correctness.",
     prof='[On: "One implementation detail of the replay affects correctness."] use simpler language. say things like sources of error.',
     reply="Reworded this in plainer terms."),
dict(page="p13",
     anchor="carry three distinct kinds of error",
     prof="what are these three sources of error?",
     reply="They are now listed right after this sentence as cases A, B and C: spikes, gaps and jitter."),
dict(page="p13",
     anchor="the preprocessing treats each with a dedicated stage",
     prof='[Struck out: "concrete"]',
     reply="Removed the word."),
dict(page="p13",
     anchor="Case A is handled by a Hampel despike",
     prof='[On: "Stage"] you called it Case. be consistent.',
     reply="Fixed, it is Case everywhere now."),
dict(page="p14",
     anchor="The three cases need different treatments",
     prof="same comment here, use a simpler language to explain things as oppose as a senior graduate student.",
     reply="Rewrote the smoothing section in simpler language."),
dict(page="p14",
     anchor="the filter is checked to move measured samples by less than the raw measurement jitter",
     prof='[On: "measured, not assumed."] what do you mean?',
     reply="Removed that phrase. The sentence now just states the check itself."),
dict(page="p14",
     anchor="Case C is smoothed with a low-pass Butterworth filter",
     prof="Have you studies these type of filter in your undergraduate studies. If not, I would suggest just use the one that you have studied. This type of comparison is not within the scope of the thesis.",
     reply="Removed the filter comparison, it was out of scope. The text now only describes the Butterworth filter I use and its settings."),
dict(page="p14",
     anchor="run forward and then backward over the recording",
     prof='[On: "The chosen zero-phase Butterworth at 3 Hz gives five times less shake"] is this for the recorded cases?',
     reply="That number did come from the evaluation recording, but it went out with the comparison table."),
dict(page="p15",
     anchor="The smoothing stage follows the Data Integrity rule.",
     prof='[On: "The stage is bound by an explicit data integrity contract,"] english',
     reply="Reworded it. Data Integrity is defined once at the start of the chapter now, and this sentence just applies the rule."),
dict(page="p15",
     anchor="Every repaired sample keeps a flag that marks it as repaired",
     prof='[Highlighted: "provenance flag,"]',
     reply="Changed it to plain wording, a flag that marks the sample as repaired."),
dict(page="p15",
     anchor="so later stages can always tell measured data from filled-in data",
     prof='[Highlighted: "so downstream consumers can always distinguish measured data from repaired data."] when I highlight things with no command means you need to revise the english to your level so it looks less like an AI generated.',
     reply="Understood. I went through every highlighted spot and rewrote it in my own words."),
# ---- p16-p18: sampling section, MediaPipe structure, Ch3 opening ------------
dict(page="p16",
     anchor="2.1.4 Recorded Session Replay and Frame Extraction",
     prof='[Struck out heading: "2.1.4 Sampling Rate Overview"]',
     reply="Deleted that section. The sampling details now sit in one line in 2.1.1 where the recordings are introduced."),
dict(page="p17",
     anchor="Those positions are labelled and arrive in a fixed order",
     prof='[On: "an unstructured"] there is some structure with Medippie data since we know the order based on their data structure.',
     reply="You are right. It now says the landmarks are labelled and arrive in a fixed order, here and in 2.1.2."),
dict(page="p18",
     anchor="This chapter introduces the kinematic model that gives the points that meaning.",
     prof='[Highlighted: "system consumes."]',
     reply="Reworded this opening."),
dict(page="p18",
     anchor="so validation can demand exact agreement rather than a close fit",
     prof='[Highlighted: "which turns validation into a strict test rather than a curve fit."]',
     reply="Reworded in plainer terms."),
dict(page="p18",
     anchor="every construction was first checked on synthetic recordings with known injected angles",
     prof='[On: "known injected angles before it was trusted on real data; those verification results appear alongside the derivations throughout the chapter."] not clear.',
     reply="Clarified. Every formula was first tested on synthetic recordings where the true angles are known, and the checks are reported next to the derivations."),
# ---- p20-p21: frames, flip, transforms --------------------------------------
dict(page="p20",
     anchor="each axis labelled with the frame it belongs to",
     prof='[On: "frame C and person space"] label which is which in the Figure.',
     reply="Redrew Figure 3.2 with every axis labelled with the frame it belongs to."),
dict(page="p20",
     anchor="The flip applies to points only, never to rotation matrices",
     prof='[Struck out: "One rule keeps the handedness bookkeeping trivial for the rest of the chapter:" and the determinant passage that followed] no need. it makes the presentation confusing. in equation 1.1 just say it applies to a point.',
     reply="Cut it. The text now just says the flip applies to points only."),
dict(page="p21",
     anchor="its transpose equals its inverse",
     prof='[On: "R^T R = I,"] use math mode',
     reply="It is in math mode now, along with every other inline formula."),
dict(page="p21",
     anchor="the convention throughout this chapter is that",
     prof='[On: "parent frame is"] why you change from p to v?',
     reply="Defined the convention right here: p is a measured landmark point and v is a segment vector between two points."),
dict(page="p21",
     anchor="with no numerical matrix inversion ever needed",
     prof="you already said this. Keep it short and to the point.",
     reply="Trimmed the repeat, it is said once and not again."),
# ---- p22-p25: torso construction and worked example -------------------------
dict(page="p22",
     anchor="The selection rests on three assumptions.",
     prof='[On: "considerations"] say assumptions',
     reply="Changed to assumptions."),
dict(page="p23",
     anchor="denote the person-space positions of the left hip, right hip, and right shoulder",
     prof='[On: "p23, p24,"] try to use math mode and subscript',
     reply="They are proper subscripts in math mode now, here and through the rest of the thesis."),
dict(page="p23",
     anchor="described as a rotation matrix and an origin",
     prof='[On: "packaged"] described',
     reply="Changed to described."),
dict(page="p24",
     anchor="among all the planes that contain the hip line",
     prof='[On: "the hip line is the torso plane."] not clear!',
     reply="Rewrote it. Among all planes that contain the hip line, the torso plane is the one that also contains the spine side vector."),
dict(page="p24",
     anchor="is perpendicular to both, with components",
     prof='[On: "(a_y b_z"] use mathmode',
     reply="The cross product components are displayed math now."),
dict(page="p25",
     anchor="A reference configuration pins down what the finished matrix means",
     prof="show an example of reference pose. an image or schematics.",
     reply="Added Figure 3.5, which shows the reference configuration on the avatar."),
dict(page="p25",
     anchor="since the filtered stream is what the solver consumes",
     prof='[Highlighted: "since the filtered stream is what the solver consumes;"]',
     reply="Tightened this paragraph and stated the printing convention for the worked numbers."),
dict(page="p25",
     anchor="the raw back-projection of the same frame",
     prof='[Highlighted: "raw back-projection of the same frame,"]',
     reply="Reworded the sentence to say plainly how the raw and filtered values differ."),
dict(page="p25",
     anchor="values are computed at full precision and printed rounded to two decimals",
     prof="you don't have to show so many decimals. just two is enough. use this all the way through the thesis when you show numerical examples.",
     reply="Done, two decimals everywhere now. The convention is stated once here and holds for the whole thesis."),
# ---- p28-p31: arm frames, angle computation, Unity mapping ------------------
dict(page="p28",
     anchor="A dimension count explains why this set of angles",
     prof='[On: "dimension count"] use math mode and subscript all the way through the thesis.',
     reply="Swept the whole thesis, symbols and subscripts are in math mode throughout."),
dict(page="p28",
     anchor="a second basis at the shoulder would add a shoulder-girdle degree of freedom",
     prof='[Highlighted: "basis at the shoulder would silently introduce a shoulder-girdle degree of freedom that the data cannot support."]',
     reply="Simplified the wording here."),
dict(page="p28",
     anchor="The rest configuration is the T-pose of Figure 3.5",
     prof='[Underlined: "T-pose:"] is T-pose a reference configuration?',
     reply="Yes. The T-pose is now defined as the reference configuration in 3.2.2 and shown in Figure 3.5."),
dict(page="p29",
     anchor="3.3.3 Worked Example",
     prof='[On: "Work Example"] Worked Example',
     reply="Renamed them all to Worked Example."),
dict(page="p29",
     anchor="The person-space upper arm vector is",
     prof="you should follow a consistent nomenclature. p is a point, v is a vector and what is u?",
     reply="Cleaned up the nomenclature: p is a point, v is a vector, and unit directions carry a hat."),
dict(page="p29",
     anchor="3.4 Joint Angle Computation",
     prof='[On: "Joint Angle Resolution"] what does this mean?',
     reply="Renamed the section to Joint Angle Computation."),
dict(page="p30",
     anchor="for the entry of a measured numerical matrix",
     prof='[On: "matrix m:"] not defined.',
     reply="Defined it now, right before its first use."),
dict(page="p30",
     anchor="in row i, column j",
     prof='[On: "1-based row and column indices."] what does this mean?',
     reply="Dropped that phrase and just said row i, column j."),
dict(page="p30",
     anchor="When x reaches either end of that range",
     prof='[On: "At the edges of that range"] what does this mean?',
     reply="Rewrote this. It now says plainly what happens at plus and minus 90 degrees and names it gimbal lock."),
dict(page="p30",
     anchor="z is set to zero and y carries the whole combined rotation",
     prof='[On: "The decode stays well defined there by convention: z is set to zero and y absorbs the combined rotation, read from the first row. On the real recording the decode and recompose round trip agrees to 3.6e-16, and it is exact at synthetic poses placed at the singularity itself."] not clear!',
     reply="Simplified the convention and the round trip check."),
dict(page="p31",
     anchor="How these angles drive the avatar root is shown numerically in Section 3.5.1.",
     prof="you should add numerical detailes here as oppose to the previous section which you talk about the Euler angles. use Torso orintation to show the results of the angle computation and then show how you have converted it in Unity.also,",
     reply="Added Section 3.5.1, which carries the frame 100 torso numbers into Unity."),
dict(page="p31",
     anchor="The full path from synthetic landmark input through the frame construction",
     prof='[Highlighted: "The full path, from synthetic landmark input through the frame construction,"]',
     reply="Reworded this sentence."),
dict(page="p31",
     anchor="3.5 Mapping to the Unity Avatar",
     prof="I think in this section, first show how you kinematic model computes the orientation and position of the torso coordinate frame.Then, in the next section show how your computed angles from your kinematic model is converted in UNity for visualization of the avatar.",
     reply="Restructured it exactly like this. Section 3.4 computes the angles and the new 3.5 shows how they are converted for the Unity avatar."),
]

W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
W15 = "http://schemas.microsoft.com/office/word/2012/wordml"
CT_COMMENTS_EX = ("application/vnd.openxmlformats-officedocument"
                  ".wordprocessingml.commentsExtended+xml")
RT_COMMENTS_EX = "http://schemas.microsoft.com/office/2011/relationships/commentsExtended"


def find_anchor_runs(doc, anchor):
    """The paragraph runs covering `anchor`; asserts exactly one match."""
    hits = []
    for p in doc.paragraphs:
        joined = "".join(r.text for r in p.runs)
        if anchor in joined:
            hits.append(p)
    assert len(hits) == 1, f"anchor matched {len(hits)} paragraphs: {anchor!r}"
    p = hits[0]
    runs, texts = p.runs, [r.text for r in p.runs]
    joined = "".join(texts)
    i = joined.find(anchor)
    j = i + len(anchor)
    span, pos = [], 0
    for r, t in zip(runs, texts):
        if pos < j and pos + len(t) > i:
            span.append(r)
        pos += len(t)
    assert span, f"no runs cover anchor: {anchor!r}"
    return span


def thread_replies(doc, pairs):
    """Give every comment paragraph a w14:paraId and write a commentsExtended
    part that nests each reply under its professor comment, the same
    mechanism Word uses for threaded comments."""
    comments_part = doc.part.part_related_by(RT.COMMENTS)
    comments_el = comments_part._element
    para_id = {}
    counter = 0x1A2B0001
    for c in comments_el.findall(qn("w:comment")):
        cid = c.get(qn("w:id"))
        last_p = None
        for p in c.findall(qn("w:p")):
            p.set(f"{{{W14}}}paraId", f"{counter:08X}")
            last_p = p
            counter += 1
        para_id[cid] = last_p.get(f"{{{W14}}}paraId")

    lines = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
             f'<w15:commentsEx xmlns:w14="{W14}" xmlns:w15="{W15}" '
             'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
             'mc:Ignorable="w14">']
    for prof_id, reply_id in pairs:
        lines.append(f'<w15:commentEx w15:paraId="{para_id[prof_id]}" w15:done="0"/>')
        lines.append(f'<w15:commentEx w15:paraId="{para_id[reply_id]}" '
                     f'w15:paraIdParent="{para_id[prof_id]}" w15:done="0"/>')
    lines.append("</w15:commentsEx>")
    blob = "\n".join(lines).encode("utf-8")
    part = Part(PackURI("/word/commentsExtended.xml"), CT_COMMENTS_EX,
                blob, doc.part.package)
    doc.part.relate_to(part, RT_COMMENTS_EX)


def add_comments(src, dst):
    doc = Document(src)
    pairs = []
    for entry in COMMENTS:
        span = find_anchor_runs(doc, entry["anchor"])
        c_prof = doc.add_comment(span, text=entry["prof"], author=PROF, initials="SP")
        c_reply = doc.add_comment(span, text=entry["reply"], author=ME, initials="LL")
        pairs.append((str(c_prof.comment_id), str(c_reply.comment_id)))
    thread_replies(doc, pairs)
    doc.save(dst)
    print(f"{dst}: {len(COMMENTS)} comment sites, {2 * len(COMMENTS)} comments")


def write_md():
    out = [
        "# Supervisor comments restored with replies (Part 1)",
        "",
        "Every annotation from the Part 1 review PDF (PROF_COMMENTS_PART1.md, 65",
        "annotations merged into 48 sites), restored as Word comments in",
        "Thesis_V5_Part1_commented.docx / Thesis_V5_commented.docx, each with a",
        "reply stating what changed. The anchor column is where the comment now",
        "sits in the revised text, for adding the same threads to the online copy.",
        "",
    ]
    for n, e in enumerate(COMMENTS, 1):
        out.append(f"## {n}. ({e['page']}) anchored at: \"{e['anchor']}\"")
        out.append(f"- **Comment (S.P.):** {e['prof']}")
        out.append(f"- **Reply (L.L.):** {e['reply']}")
        out.append("")
    with open(BASE + "PROF_REPLIES_PART1.md", "w") as f:
        f.write("\n".join(out))
    print(f"PROF_REPLIES_PART1.md: {len(COMMENTS)} sites")


if __name__ == "__main__":
    add_comments(BASE + "Thesis_V5_Part1_Ch1-3.docx",
                 BASE + "Thesis_V5_Part1_commented.docx")
    add_comments(BASE + "Thesis_V5.docx",
                 BASE + "Thesis_V5_commented.docx")
    write_md()
