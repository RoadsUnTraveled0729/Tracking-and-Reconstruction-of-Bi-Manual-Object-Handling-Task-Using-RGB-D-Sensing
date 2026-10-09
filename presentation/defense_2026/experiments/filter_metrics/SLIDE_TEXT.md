# Slide text for pages 47 and 48

Numbers are from summary.csv (3-D norm rows), rounded to two decimals for
mm and ms; no other numbers are used. Chart files are in this folder.

## Page 47

Title: Why Butterworth offline

Chart: chart_filter_offline.png

Claim: With zero lag, Butterworth 3 Hz filtfilt cuts shake from 6.38 to
2.86 mm, below Savitzky-Golay (3.29 mm) and median (3.51 mm); Savitzky-Golay
stays closer to fast motion (5.64 against 6.53 mm).

Source: experiments/filter_metrics/summary.csv; thesis Section 2.5, Appendix F, Section 8.3

Speaker notes:
1. On the R6b right wrist, after the same despike and gap fill, every
   offline candidate has zero lag, and Butterworth 3 Hz leaves the least
   shake of the 9-frame and 3 Hz options, 2.86 mm against 6.38 mm for the
   despiked raw.
2. It is a trade-off rather than a free win: Savitzky-Golay follows fast
   motion more closely (5.64 against 6.53 mm), the median filter is worse
   on both measures, and dropping to 2 Hz lowers shake to 2.54 mm but moves
   the fast-motion deviation to 7.73 mm.
3. The zero lag comes from running the filter forward and backward over
   the whole recording, which reads future samples, so it is available
   only offline.

## Page 48

Title: Why One Euro in real time

Chart: chart_filter_realtime.png

Claim: At the live 1 Hz setting, One Euro leaves less shake than a causal
3 Hz Butterworth (2.48 against 2.88 mm) with less lag (85 against
142 ms). Lags are rounded to whole milliseconds because they come from
one recording; the exact values stay in summary.csv.

Source: experiments/filter_metrics/summary.csv; thesis Section 2.5, Appendix F, Section 8.3

Speaker notes:
1. A live filter cannot read future samples, so every causal candidate
   trails the wrist, and the lag is the price of the smoothing.
2. One Euro at 1 Hz beats the forward Butterworth on both counts, 2.48 mm
   at 85 ms (2.6 frames) against 2.88 mm at 142 ms; a plain moving
   average lags less, 55 ms, but keeps 2.86 mm of shake, about the same as the
   Butterworth.
3. The Appendix F setting of 0.05 Hz smooths hardest, 2.08 mm, but lags
   187 ms; the live filter in the real-time pipeline runs the 1 Hz
   setting.
