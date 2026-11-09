# CEVG independent dynamic-scene simulation — executed exploratory results

**Evidence tier:** executed synthetic scenario model, NOT real ESP32/phone
observations, NOT real Wi-Fi fault-injection, NOT human mobility results.
This model does not drive the production navigation/audio code. It separately
implements three speech-warning policies with a motion-derived *independent*
ground truth and tests the specific hypothesis that receiver-arrival timestamp
freshness misses delays accumulated before the receiver.

## Reproduction

```bash
python -m research.independent_scene_simulation \
  --runs 30 --frames 2000 --seed 20261109 \
  --out evidence/independent_scene_simulation.csv
```

60,000 independent synthetic scenes per network scenario; 180,000 overall;
each scene evaluated with three policies, for 540,000 policy decisions.
The reported results were executed from the same deterministic simulation
source with default parameters.

## Independently constructed physical-state oracle

Each simulated object has an image-capture-time lateral location `x`,
velocity `v`, and independently sampled capture/inference noise.
A warning claiming left/center/right is supported only if the object exists,
remains within the modeled corridor at the time of **warning emission**, and
its current lateral direction agrees with the announced direction.
The oracle uses `x_decision = x_capture + v * (sender_wait + receiver_delay)`.
It does *not* consult the warning policy, confidence threshold, capture-time
verification flag or gate decision. It therefore avoids defining truth as
"whatever the proposed gate accepts."

Generated detection scores and motion are probabilistic and simplified.
The model omits depth geometry, pedestrian behavior, visual occlusions,
frame correlation, Wi-Fi hardware queues and actual ESP oscillator drift.

## Three policies

- Confidence: emit if detection and score >=0.5 (proxy for original UDP
  warning behavior, not the entire original Android/navigation pipeline).
- Receiver-fresh: confidence plus receiver-only processing time <=0.5 s.
- Capture-bound: confidence plus independently modeled source-to-decision
  age and conservative clock-offset error <=0.5 s, with occasional clock
  verification failures. All policies see identical synthetic scenes.

The receiver delay is always 0.025–0.18 s in this simulation, so the
receiver-fresh baseline deliberately cannot detect upstream buffering;
it is identical to confidence-only at this threshold. This is a
**designed stress test**, not broad evidence receiver freshness never helps.

## Executed mean results (30 independently seeded runs per scenario)

| Scenario | Policy | Unsupported/issued | Valid warning recall | Abstention | Unsupported/frame |
|---|---|---:|---:|---:|---:|
| Nominal | Receiver-fresh | 14.595% | 94.628% | 32.977% | 9.782% |
| Nominal | Capture-bound | 14.603% | 91.102% | 35.468% | 9.423% |
| Mixed upstream buffering | Receiver-fresh | 29.061% | 94.632% | 32.948% | 19.485% |
| Mixed upstream buffering | Capture-bound | 14.173% | 77.600% | 54.552% | 6.445% |
| Burst upstream buffering | Receiver-fresh | 42.139% | 94.480% | 32.875% | 28.288% |
| Burst upstream buffering | Capture-bound | 14.251% | 60.975% | 70.773% | 4.168% |

The *reduction in unsupported emissions* comes at a substantial cost in
*valid warnings withheld*. For nominal conditions the unsupported/issued
fraction does not meaningfully improve; the method imposes an unnecessary
recall cost under the chosen thresholds. A "better in all conditions" or
"safe for independent navigation" claim would contradict these results.

## Paired run-level uncertainty (capture-bound minus receiver-fresh)

Independent-run bootstrap: 4,000 resamples, fixed seed 515, 30 independent
runs per scenario; frame-level independence is NOT assumed for headline
intervals. Intervals are descriptive of this simulator, not real-device CIs.

| Scenario | Unsupported/frame difference (95% interval) | Valid recall difference (95% interval) |
|---|---:|---:|
| Nominal | -0.358 pp [-0.402, -0.318] | -3.526 pp [-3.702, -3.345] |
| Mixed | -13.040 pp [-13.317, -12.777] | -17.032 pp [-17.388, -16.700] |
| Burst | -24.120 pp [-24.472, -23.757] | -33.505 pp [-34.131, -32.884] |

**Interpretation:** these are policy-consistency and simulated-world behavioral
results for a specific generative scenario, not independently established
physical-device performance, user outcome superiority, or general novelty.

## Scientific boundaries

1. Source-clock proof is modeled as a probability and bounded offset error,
   not simulated cryptographic timing of a real radio/ESP board.
2. The simulator does not invoke the live UDP `_process_frame`, so measured
   model output cannot be called actual WVAB end-to-end latency.
3. A corridor's independent geometric warning criterion does not establish
   user-facing navigation correctness or actual safety.
4. Independent real camera video, annotated action labels, synchronized
   firmware traces and real acoustic TTS completion times remain necessary.
5. Prior-art review is ongoing; generic selective abstention, secure edge
   transmission and freshness gates are not individually novel.

**Publication implication:** viable preliminary **simulation-study evidence**
and a testable cross-layer hypothesis now exist, but a convincing original
research contribution still needs comparison against strong alternatives,
sensitivity analysis, independent data, and validated timing assumptions.
