# Measurement precision in reported numbers

Rule from the supervisor's Chapter 7 comments of 2026-09-05 (comment
C38 in writing/v7/PROF_COMMENTS_ROUND4.md): "if you want to talk about
the error, you do not need to go e-13. In engineering, or in our case
of precision, if you have units in mm, that should be fine since the
system cannot measure that precise."

- Positions: report in millimetres or centimetres with one decimal at
  most. Never finer than the sensor (the D435 depth noise is at the
  millimetre level at 1.3 m).
- Angles: report to 0.1 degree. A solver round-trip check is stated as
  "exact to floating-point precision" or "below 0.001 degree", not as
  an exponent table.
- No scientific notation in thesis prose or tables; if a value is
  effectively zero, say so in words.
- At most two decimals for ANY printed number, matrix entries and
  vector components included (supervisor round 5 on Chapter 4,
  2026-09-07, C48 in writing/v8/PROF_COMMENTS_ROUND5.md: "In the value
  of the matrices, do not go beyond two decimals. For example, if it is
  0.0014 just write 0.0. Same comments for all the numerical values.").
  Conventions used since then: rotation entries and unit vectors to two
  decimals, near-zero written 0.00 (never -0.00); vectors inside
  equations in metres with two decimals; prose distances in cm or mm
  with one decimal; session-clock times in seconds with two decimals
  and offsets in whole milliseconds; never display arithmetic whose
  rounded operands do not give the printed result (drop the
  intermediate or state the result only). Builder comments keep the
  full-precision values as the trace. check_style.py flags any three
  decimals in prose, captions, table cells or Word math.

**Why:** numbers finer than the measurement suggest a precision the
system does not have and distract from the engineering result.

**How to apply:** when writing or reviewing any thesis chapter or
report table, round to the sensor's precision; see also
[[thesis-statement-style]] (no number-led sentences) and
[[prof-comments-protocol]].
