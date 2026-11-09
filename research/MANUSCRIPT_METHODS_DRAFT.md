# Manuscript working draft — research protocol and methods (not submission ready)

**Proposed title:** Evidence-Valid Offline Wearable Vision Guidance Under Authenticated Sensor Delay and Perception Uncertainty

**Article type:** Original research *candidate*. This is a preregistered methodological draft, **not a completed experimental study**. Do not submit until validated device data, an independent related-work review, and complete results are included.

## Abstract — structured working text

**Background:** Wearable vision assistants rely on camera inference and actionable audio/navigation cues. A camera object-detection result cannot establish that its source is authenticated, timely, geometrically calibrated, or suitable for issuing a directional instruction.

**Method:** We formulate an evidence-eligibility policy that admits actionable metric/directional guidance only if sender provenance, observation freshness, minimum detector confidence, localization validity, metric calibration, and path availability satisfy explicit gates. An opt-in implementation extends WVAB's existing navigation state policy and preserves the original policy as a baseline. We provide an authenticated camera-frame capture-tick envelope, conservative offset-interval models, run-level paired comparison and a protocol for independently annotated real-device trials.

**Results:** An independent dynamic-scene simulator was executed on three network-buffering regimes with 30 runs each. Under mixed buffering the capture-bound policy reduced unsupported issued warnings from 29.06% to 14.17%, but valid-warning recall dropped from 94.63% to 77.60%. Physical-device results remain pending. Do not insert simulated effect sizes as real results.

**Conclusion:** Within the defined simulator, verified capture-age gating changes the unsupported-warning/availability trade-off; independently calibrated hardware and user validation remain necessary.

## 1. Introduction

The methodological question is whether conditioning actionable guidance on **cross-layer evidence validity** reduces unsupported instructions while retaining acceptable valid guidance and end-to-end timeliness. Stronger abstention alone is insufficient: a policy that never speaks cannot be considered a useful assistant. Existing WVAB already provides encrypted authenticated transport, replay resistance, object ranking, calibration gates and STOP/DEGRADED states. The investigation focuses on the *coupling* of these mechanisms at the decision boundary, not claiming any individual mechanism as invented here.

### Research questions

- **RQ1:** Relative to the existing WVAB navigation decision rule, does additional evidence gating reduce independently labeled unsupported actionable guidance?
- **RQ2:** How much valid guidance is lost and how often does the policy abstain, overall and for each failure class?
- **RQ3:** How do capture-to-decision delay and end-to-audio delivery time change with packet loss/reordering, localization invalidity, confidence variation and sender/receiver restart?
- **RQ4:** Which conditions (authentication provenance, freshness, confidence, localization, calibration) causally contribute to observed changes under matched ablation trials?

### Originality criterion

An editorially defensible contribution requires a rigorous demonstrated trade-off or novel design beyond known secure transmission and conventional confidence/age gating. **No broad novelty conclusion is asserted until a systematic, cited comparison with current work is completed.**

## 2. Related work — evidence gathering required

Compare secure wearable camera-to-edge systems; time-bounded authenticated sensor messaging; uncertainty calibration and selective prediction; age-of-information; and assistive navigation human factors. Build a table of whether each prior study already integrates authenticated camera capture time, clock uncertainty, perception/localization uncertainty and validated directional action outcomes. Verify every DOI and in-text citation before journal submission.

## 3. Formal model

Let frame `i` belong to authenticated source session `s_i` and frame identifier `f_i`, with sender capture tick `t_i^S` and receiver decision tick `t_i^R`. An independently authenticated clock exchange bounds receiver-minus-sender clock offset by `[o_i^-,o_i^+]`. With drift expansion, conservative capture age is `A_i^+ = t_i^R - (t_i^S+o_i^-)`.

Set `E_i=1` only when (1) transport provenance/session and capture tick are authenticated, (2) the exchange is valid, recent and its offset uncertainty bounded, (3) `0 <= A_i^+ <= tau`, (4) confidence `c_i >= theta`, (5) fresh metric localization, (6) calibrated geometry, and (7) a path exists. Local USB-camera mode uses receiver read-completion age, which is **not true camera capture age**, and must be analyzed separately from remote mode.

The policy chooses `GUIDE` when `E_i=1`, otherwise `ABSTAIN`/a non-actionable degraded state. These are not physiological or certified safety outcomes.

The empirical objective is to reduce unsupported issued instructions while protecting valid-guidance recall and latency. Prespecify scenario-specific constraints rather than optimizing post hoc thresholds on test outcomes.

## 4. Algorithm

1. Authenticate the incoming source/session and AEAD protected frame before decoding metadata.
2. Verify capture metadata session/frame match. Distinguish sender uptime from receiver clock time.
3. Accept clock-offset proof only from an authenticated nonce-bound exchange with a bounded age and drift assumption.
4. Evaluate frame age conservatively at the guidance decision boundary.
5. Combine calibrated perception/localization evidence with path validity for the specific **actionable** guidance mode.
6. Emit `GUIDE` only if all required checks pass. Otherwise emit `DEGRADED` or preserve existing `STOP` for missing camera/localization/path.
7. Record decisions and timestamps without storing private image content; attach independent action ground truth out-of-band for evaluation.

Current boundary: research code contains the authenticated metadata envelope and offset model, but there is **no live authenticated four-timestamp exchange or remote online CEVG guide-release integration**.

## 5. Experimental design (prespecified)

Hardware requirements: exact ESP32-CAM revision, Raspberry Pi revision, camera model, radio access point, software SHAs, inference model hashes, audio output device and calibration records.

Paired conditions: identical recorded visual scenes under normal link, packet loss, burst loss, reordering, duplicate packets, variable delay, camera restart, server restart, invalid calibration, stale localization and confidence shifts. Compare original navigation policy, confidence-only, freshness-only and full cross-layer policy, with component ablations.

Ground truth: independent geometric/safety action annotations made without consulting CEVG gate predicates. Record direction-specific action validity, not just whether a path existed. Predefined protocols must protect research participants; stationary controlled scenes can precede mobility studies.

Primary outcomes: (i) unsupported issued/actionable guidance, (ii) valid-guidance recall, (iii) abstention, (iv) per-scene trial paired differences, (v) capture-to-decision and end-to-audio p50/p95/p99, (vi) recovery time and resource overhead. Include all denominators, calibration validity and failure cases.

Statistical analysis: paired trial-level cluster bootstrap for headline rate differences with independent runs. Wilson intervals are descriptive and do not adjust for correlated frames. Thresholds, significance criteria, and minimum independent run counts must be preregistered with a justified power/sensitivity analysis before results are collected.

## 6. Results — executed simulator, physical-device results pending

A motion-derived, policy-independent scene oracle was evaluated in
`research/independent_scene_simulation.py` across 30 independent seeds,
2,000 synthetic scenes per seed and three upstream-buffering scenarios
(180,000 generated scenes; each evaluated with three policy alternatives).
Detailed reproducible methods, scenario priors, and paired run-bootstrap
intervals are in `research/EXECUTED_SIMULATION_RESULTS.md`.

Under the mixed sender-queue-delay scenario, unsupported warnings per issued
warning declined from 29.06% with receiver-age-only gating to 14.17%
with capture-bound gating; valid-warning recall simultaneously declined
from 94.63% to 77.60% and abstention increased. Under burst buffering,
unsupported warnings decreased from 42.14% to 14.25%, but recall
decreased from 94.48% to 60.98%. In nominal conditions there was almost
no unsupported-issued fraction difference, despite recall loss.

**Interpretation:** These data demonstrate a trade-off under the
specified generative simulator. They are **not physical evidence** of
ESP32/Raspberry Pi navigation safety or live camera/audio latency, and
do not establish that the policy is globally novel. Real-device results
and action-level annotations remain uncollected.

Suggested tables (populate from measured artifacts):
- T1: Hardware/software and link-condition settings.
- T2: Ground-truth action annotations, class/scenario counts and agreement.
- T3: Unsupported-issued guidance and valid-guidance recall for each baseline, with clustered intervals.
- T4: Capture-to-feedback latency, recovery and CPU/memory/power by scenario.
- T5: Component ablation and failure-mode breakdown.

## 7. Discussion

Interpret both sides of the safety–availability trade-off. Challenge optimistic interpretations: detector confidence is not calibrated path safety, no detections can indicate clear scene rather than failure, bounded timing requires synchronized clocks, and TTS output is not automatically delivered to the user. Discuss whether additional abstention is actually beneficial, including usability and accessibility implications.

## 8. Threats to validity

Software correctness tests do not demonstrate user safety. Simulated fault inputs differ from physical Wi-Fi behavior. The local USB read clock and remote ESP32 uptime are not interchangeable. Unverified clock synchronization invalidates capture-age conclusions. Frame-level independence assumptions can distort uncertainty. Outcome labels must be independent of the tested gating rule. A single device/model/setup limits external validity.

## 9. Conclusion

**Pending independent empirical results**. No acceptance, safety certification or novel algorithmic discovery is implied by green CI.

## Reproducibility and ethics

Link to an immutable GitHub commit/tag, released test scripts, hardware configurations and de-identified measured traces when permission allows. Preserve any sensitive video and participant information in controlled storage. Do not publish personal health/biometric details or perform uncontrolled mobility trials.
