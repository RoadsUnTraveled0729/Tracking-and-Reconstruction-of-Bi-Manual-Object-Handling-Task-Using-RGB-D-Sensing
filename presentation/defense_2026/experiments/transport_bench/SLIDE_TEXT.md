# Slide text: transport Q&A pages 38-40

All numbers are from experiments/transport_bench/results.csv (run 1).
Message sizes: 172 B (PSV3 person record) and 1,536,032 B (one PSF1
frame slot). Paced condition: 30 Hz.

## Page 38: Transport candidates

| Transport | Ordering | Loss | Copies per message | Unity-side reader | Used in this pipeline |
| --- | --- | --- | --- | --- | --- |
| TCP | Ordered byte stream | None (retransmits) | 2 (writer to kernel, kernel to reader) | Socket thread plus length-prefix framing | No |
| UDP | Not guaranteed | Possible: 4.55 % of 1,536,032 B frames lost at 30 Hz with the default 212,992 B receive buffer (smaller than one frame); 0.0102 % unpaced | 2, plus 1 for reassembly of multi-datagram frames | Socket thread plus chunk reassembly | No (an unmeasured v1 fallback only) |
| Shared memory (mmap + seqlock) | Latest value only | None; an overwritten record is skipped by design | 2 (writer into the mapping, reader copy-out), no kernel call | MemoryMappedFile read in Update(), no thread | Yes (person record and frame ring) |

Claim: Shared memory is the only candidate with no kernel call per
message and no loss, and Unity reads it without a socket thread.

## Page 39: One-way latency at 30 Hz

Title: Shared memory delivers a record in microseconds

Claim: At 30 Hz the 172 B record arrived at p50 2.67 us with shared
memory, against 30.67 us over UDP and 37.97 us over TCP; the
1,536,032 B frame at 54.38 us, against 232.2 us (TCP) and 239.8 us
(UDP).

Source: experiments/transport_bench/results.csv, loopback, this workstation

Speaker notes:
- Each curve is 2000 messages sent at 30 Hz between two Python processes on separate cores, timed from the writer's clock just before sending to the reader's clock when the whole record has been copied out.
- The tails keep the same order: at p99 shared memory reached 3.21 us for the record and 73.66 us for the frame, while TCP reached 120.8 us and 317.1 us.
- This shared-memory reader spins on the sequence counter; a reader that sleeps 1 ms between polls sees p50 518.6 us, which is still far below the 33.3333 ms frame interval, and Unity's own per-frame read was not measured here.

## Page 40: Throughput, jitter and loss

Title: No loss and the lowest jitter at the pipeline rate

Claim: At 30 Hz shared memory had inter-arrival jitter of 0.0009 ms
(172 B) and 0.0084 ms (1,536,032 B) with no loss, while UDP lost
4.55 % of the 1,536,032 B frames with the default 212,992 B receive
buffer, smaller than one frame.

Source: experiments/transport_bench/results.csv, loopback, this workstation

Speaker notes:
- Jitter is the 99th minus the 50th percentile of the time between consecutive arrivals at the reader; TCP measured 0.0803 ms and 0.0808 ms, and UDP 0.0774 ms and 0.0255 ms.
- Run flat out, the 172 B record reached 1,341,725 messages per second over shared memory against 307,629 over UDP and 246,799 over TCP, and the 1,536,032 B frame reached 5,514.6 per second over TCP and 5,859.7 over UDP.
- The shared-memory bar for the frame shows 0 because a single-slot mailbox rewritten 30,081.6 times per second never stays still long enough for a 1,536,032 B copy; the pipeline publishes frames at the camera rate into a multi-slot ring, so this regime does not occur in it.

## Page 41 (round 5): Moving one frame package from Python to Unity

Replaces the p50/p99 charts of pages 39-40 (round 4) with one plain
chart of the package condition. Numbers from
experiments/transport_bench/results_package.csv, run 1 unless stated.

Title: Moving one frame package from Python to Unity

Claim: Shared memory moved each 1.5 MB frame package in a typical 0.059 ms, about five times faster than TCP (0.295 ms) or UDP (0.311 ms), and lost none; UDP lost 528 of 1000 packages.

Chart: chart_transport_package.png (bar = typical package, thin line =
fastest to slowest delivered package, lost count under each bar).

Source: Undergraduate thesis | Section 6.1 | experiments/transport_bench/results_package.csv

Speaker notes:
- Each bar is 1000 packages sent at 30 Hz after 200 warm-up packages (run 1 of two).
- One package is the 172 B person record plus one 1,536,032 B frame slot, 1,536,204 B in all.
- The time runs from the writer's clock just before the first byte is written or sent to the reader's clock when both parts have been read whole; writer and reader are separate Python processes on separate cores of one desktop workstation (AMD Ryzen 9 7950X, Linux), over localhost, and the reader stands in for Unity.
- Typical (median) times: shared memory 0.0586 ms, TCP 0.2946 ms, UDP 0.3115 ms.
- Fastest to slowest: shared memory 0.0556 to 0.1569 ms, TCP 0.1765 to 0.6332 ms, UDP 0.2328 to 0.3618 ms.
- Run 2 gave 0.0569, 0.2929 and 0.3130 ms; every delivered package took far less than the 33.3 ms frame interval.
- UDP lost 528 of 1000 packages (668 in run 2) with the default 212,992 B receive buffer, about one seventh of one package; a package missing any of its 27 datagrams when the next package starts is given up.
- TCP and shared memory lost none.
- The UDP loss varied from run to run (an earlier run on a busier machine lost 248 and 203), so the count is an example, not a constant.
- This shared-memory reader spins on the sequence counter; Unity reads once per rendered frame, which adds waiting that was not measured here.
- In the pipeline itself Unity reads only the records, and the frame buffer feeds the Python branches (Section 6.1.1), so the package is a stress case.
