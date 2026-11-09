# CEVG — preregistered physical-device research protocol

Status: **experimental protocol only; no physical trials or user outcomes claimed**.

## Scope and research questions

RQ1: Does the proposed evidence gate reduce unsupported actionable guidance
relative to the original WVAB navigation policy on identical real observations?

RQ2: What fraction of independently valid actions does the gate unnecessarily
withhold? Report guidance availability/retention, not safety alone.

RQ3: Under controlled delay, reordering, packet loss, sender restart, receiver
restart, failed calibration, and uncertain perception, how do error and
abstention rates change?

RQ4: What are the p50, p95 and p99 capture-to-decision and capture-to-feedback
latencies and the energy/CPU/memory overhead on named hardware?

## Required instrumentation

- Record Raspberry Pi model, firmware, OS/kernel, CPU governor, power supply,
  ESP32-CAM variant, flash/PSRAM, Wi-Fi AP model/channel, phone model if used.
- Record repository SHA, firmware binary hash, model hash, calibration procedure,
  camera resolution/FPS, inference confidence, and all experimental thresholds.
- Use authenticated per-frame camera capture ticks and document an independently
  verified sender/receiver clock-offset interval. If no verified synchronization
  exists, report **capture age unknown**.
- For local USB path use monotonic receiver `cap.read` completion time and label
  this **receiver-frame-processing latency**, not true exposure-to-guidance age.
- Record actual end-of-audio-playback timing; TTS call commencement alone cannot
  establish user-facing guidance delay.
- Keep physical trial clips and subject identifiers private. Raw images must
  not be committed to GitHub.

## Protocol and replicates

1. Freeze one commit, reference model and threshold set before collecting data.
2. Evaluate normal Wi-Fi, constrained bandwidth, fixed-delay, random-loss,
   burst-loss, reordering, duplication, sender reboot, receiver reboot,
   calibration loss and model-uncertainty scenarios, using an actual impairment
   emulator or repeatable fault injection. Record emulator configuration.
3. Compare baseline and CEVG on the exact same replayed real observations.
   Randomize scenario order where field conditions can drift.
4. Repeat with independent trials/runs and distinct seeds. Treat frames
   from one scene or trial as correlated rather than independent samples.
5. Separately label whether a specific directional instruction was physically
   justified. Labels must come from independent measurement/annotation, not
   the CEVG eligibility predicates. Use two independent annotators and adjudicate
   disagreements, or independent obstacle-position ground truth.
6. Preserve **STOP**, **DEGRADED**, and **GUIDANCE_AVAILABLE** distinctions.
   A policy that always abstains is not a successful assistive system.

## Prespecified primary metrics

- Unsupported issued guidance rate = unsupported issued / all issued.
- Valid guidance recall = supported issued / all ground-truth actionable cases.
- Abstention fraction = withheld cases / all evaluated cases.
- Frame-level paired discordance comparing existing WVAB and CEVG errors.
- Capture-to-decision latency and capture-to-feedback latency distributions;
  p50/p95/p99 and worst-case with finite observation counts.
- Fault recovery time, decoding failure, successful inference FPS, CPU/RSS,
  temperature, and power draw if calibrated instruments are present.

## Statistical analysis

Report absolute denominators, trial counts and per-scenario outcomes.
Use trial/scene clustered bootstrap confidence intervals for headline
rate differences; Wilson intervals from the replay tool are *descriptive
independent-trial approximations only*. Report both reduction in unsupported
actions and cost in lost valid actions. Show ablations removing authentication,
freshness, localization and confidence independently. No repeated
random-seed synthetic experiment can substitute for independent field data.

## Stop criteria / safeguards

This system is a research prototype, not a certified mobility aid.
Use controlled static scenes, stationary tests or supervised laboratory
evaluation. No unsupervised walking trials or unapproved participant studies.
Stop immediately if guidance is unstable, timing cannot be established,
protocol authentication fails, or the radio/device enters an unknown state.
Preserve existing release fail-closed safeguards.

## Research readiness matrix

| Evidence | Current status |
| --- | --- |
| Pure CEVG model and local navigation adapter | Implemented |
| Deterministic code tests | Present; current SHA CI must pass |
| Existing navigation baseline in replay comparator | Implemented |
| Privacy-minimal local decision logging | Implemented |
| Versioned timestamp metadata codec | Implemented, research-only |
| ESP32/receiver wire-format integration | Not implemented |
| Authenticated clock synchronization | Not implemented |
| Independent real-world labeled trace and metrics | Not provided |
| Physical-device and audio latency results | Not verified |
| Human-study ethics and outcomes | Not provided |
| Demonstrated original scientific novelty | Not established |

Do not describe this protocol as an executed study or produce numerical
physical results until the underlying evidence is captured.


## Reproducible evaluation of actually emitted local decisions

Collect local receiver-side rows using `WVAB_RESEARCH_TRACE_PATH` as documented
in `research/CEVG_METHOD.md`. Independently prepare a separate file with:

```csv
run_id,frame_number,ground_truth_actionable
trial_001,1,1
trial_001,2,0
```

The above lines show **schema only**, not real trial labels or results.
Annotations must be created from independent evidence and aligned by
`(run_id, frame_number)`. Then run:

```bash
python -m research.evaluate_recorded_decisions \
  --decisions evidence/local-decision-run.csv \
  --labels evidence/independent-annotations.csv \
  --output evidence/paired-evaluation.json
```

This script rejects missing/duplicate/mismatched frame labels and outputs
confusion matrices and paired unsupported-guidance counts for recorded
existing-WVAB versus CEVG decisions. It does not verify whether a left/right
instruction was correct, nor does it verify audio delivery; both need
additional independently labeled outputs before making directional-accuracy
or user-outcome claims.


## Opt-in authenticated ESP32 frame capture-tick transport

The firmware now supports research-only packet content framing using
`WVAB_CAPTURE_METADATA_V3=1` at compile time. The server must have
`WVAB_RESEARCH_CAPTURE_METADATA_V3=1`; the two flags must be matched.
Both are **off by default** for v2 compatibility. V3 prepends exactly 21
bytes inside the AES-GCM-protected reassembled frame plaintext:
magic `WVC3`, version, sender session ID, frame ID and 64-bit capture-completion
uptime (microseconds). It increases the wire overhead and changes chunk
boundaries. The Python receiver verifies the embedded session/frame IDs after
GCM authentication and strips the metadata before JPEG decoding. An
incompatible sender is rejected, not silently interpreted as V3.

Research telemetry may be enabled with
`WVAB_RESEARCH_UDP_CAPTURE_TRACE_PATH=evidence/esp32_capture.csv`.
It records the authenticated sender's capture-completion uptime and receiver
decode/processing monotonic timestamps. **These clocks are different**:
subtracting them does not give capture-to-decision latency. An authenticated
offset-bound synchronization procedure and frame-to-guidance binding are
still required. No field hardware trial has been performed as part of this
source change. The metadata framing has compilation/codec test coverage, but
the new V3 firmware path requires real-device end-to-end validation before
being described as ready for assistive use.


## Clock-bound analysis

`core/clock_offset_bounds.py` derives a conservative receiver-minus-sender
offset interval from a **verified** four-timestamp request/reply exchange:
`[R1-S2, R4-S3]`, assuming nonnegative one-way network delays. The exchange
must be authenticated and linked to the same session/nonce. The composed
remote proof additionally rejects expired exchanges and widens offset bounds
for a configured maximum oscillator drift (default 50 ppm). The default
sync age budget is 5 seconds. These are **research configuration assumptions**,
not empirically calibrated ESP32 clock parameters.

The experimental V3 firmware and Python UDP receiver now implement a
nonce/session-bound four-timestamp challenge/response protected by AES-GCM.
The receiver binds successful timing exchanges to the same source/session as
AEAD-verified frame metadata, computes conservative clock-offset intervals,
enforces synchronization expiry and drift limits, and gates only **descriptive
obstacle warnings** after perception inference. This optional experimental
path requires physical interoperation tests and independently validated clock
behavior before its bounds can be treated as deployment guarantees.
It does NOT release calibrated move/turn/path directives.


## Experimental on-wire activation (both devices must match)

Firmware compile: `-DWVAB_CAPTURE_METADATA_V3=1`.

Server environment:

```bash
export WVAB_UDP_AUTH=1
export WVAB_UDP_ENCRYPT=1
export WVAB_RESEARCH_CAPTURE_METADATA_V3=1
export WVAB_RESEARCH_REMOTE_CEVG_ENABLED=1
export WVAB_RESEARCH_REMOTE_CEVG_MAX_AGE_S=0.5
export WVAB_RESEARCH_REMOTE_CEVG_MIN_CONFIDENCE=0.5
export WVAB_RESEARCH_UDP_CAPTURE_TRACE_PATH=evidence/esp32_capture.csv
python udp_streaming.py server --headless
```

Production server mode remains unchanged by default. Research mode rejects
unauthenticated/unencrypted UDP and requires the V3 metadata setting.

Clock request: control header with AUTH_FRAME_ID, total_chunks=0,
chunk_index=1, AEAD-GCM plaintext containing version, random 16-byte
challenge and R1 receiver monotonic tick. Device response: chunk_index=2,
same session and challenge, echoed R1, S2 receive tick, S3 response tick.
AEAD AAD binds the full 14-byte header; the receiver checks exact
challenge and session, rejects replays and inconsistent clock intervals.
Sender tick comes from ESP32 uptime, receiver tick from Python monotonic clock.
All offsets are conservative; synchronization drift budget is a configurable
research assumption, **not yet a calibrated oscillator measurement**.

The gate is applied just before obstacle speech scheduling, after detection.
No path directive or user-facing mobility safety claim follows from an
authenticated descriptive warning. Queued TTS may introduce additional
delivery delay; the current trace measures inference/decision processing but
not acoustic completion.

### Remaining mandatory physical evidence

Even with the working source-level handshake, a green cross-compile and unit
test cannot prove that a real ESP32 board processes every sync packet correctly
over Wi-Fi, that clock offsets remain bounded on actual hardware, or that
warning accuracy improves. Collect actual ESP32 + Raspberry Pi traces,
independently calibrated timing references, fault-injection conditions,
direction-specific ground truth and real audio-delivery timing.


## Frame-to-TTS engine timing instrumentation

With `WVAB_RESEARCH_TTS_TIMING_TRACE_PATH=evidence/esp32_tts.csv`,
the UDP vision receiver logs **per-frame** session/frame ID, authenticated
sender capture tick (when V3 is enabled), receiver speech queue entry,
synthesis start and time when `pyttsx3.runAndWait()` returns. The queue
retains session/frame identity across the asynchronous worker boundary,
including replacement of older queued warning messages.

These are **TTS engine timestamps**, not acoustic playback-completion proof.
The time of a sound arriving at a user's ear requires a microphone/audio
loopback measurement with synchronized clocks. End-to-end camera
exposure-to-physical-audio claims remain unavailable until that calibration
is performed.

When `WVAB_RESEARCH_REMOTE_CEVG_ENABLED=1`, the speech release gate
requires a valid authenticated sender-clock exchange and bounded capture
age before enqueuing a descriptive obstacle warning. It does not authorize
calibrated route/movement guidance.
