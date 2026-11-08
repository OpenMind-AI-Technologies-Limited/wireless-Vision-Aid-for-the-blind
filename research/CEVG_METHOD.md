# Experimental CEVG evidence gate

This branch adds a cross-layer **eligibility gate** for actionable, metric/directional
navigation guidance. It is **not** a new detector, cryptographic primitive,
calibrated confidence estimator, or certified mobility safety controller.

## Problem definition

Given a candidate guidance action and evidence tuple
`E=(t_obs,t_eval,c,origin,auth,localization_fresh,metric_calibrated,path_available)`,
admit guidance only if evidence satisfies all preconditions:

`G(E)=1[valid origin] 1[remote => authenticated] 1[0<=t_eval-t_obs<=tau] 1[c>=theta] 1[localization fresh] 1[metric calibrated] 1[path available]`.

The choice is binary GUIDE/ABSTAIN; safe warnings and non-actionable
descriptions should be designed and validated separately. This rule is
conservative by construction, so a lower unsupported-guidance rate alone
cannot establish scientific novelty. Always report valid-guidance retention and
abstention cost alongside it.

## Time and provenance constraints

Monotonic process timestamps measure **receiver-side observation age** only.
They do NOT measure remote camera capture-to-feedback delay. A future protocol
extension must supply authenticated capture timestamp/sequence metadata and
validated clock-domain mapping; otherwise remote end-to-end freshness remains
**unknown**, not proven. Authentication must be set exclusively by a verified
transport adapter. Local camera data are trusted only inside the local process.

## Evidence tiers

- Unit tests: deterministic policy correctness; not mobility outcomes.
- Offline replay: real timestamped sensor traces with ground-truth hazard labels.
- Device trial: Raspberry Pi + ESP32-CAM, synchronized age-of-information,
  measured FPS/p50/p95/p99, communication faults, and TTS behavior.
- Accessibility trial: ethics-approved user evaluation where applicable.

## Limitations

The gate reuses existing WVAB calibration and navigation constraints; it does
not assert that those constraints are novel. The initial integration is optional
and applies only to the local-camera navigation path. Do not interpret
`observed_at_monotonic` as a camera-exposure timestamp. Without an independent
dataset and independent ground truth, a synthetic oracle that uses the same
gating conditions can demonstrate consistency but **cannot prove superiority**.


## Opt-in navigation integration

The navigation pipeline uses the original behavior unless
`WVAB_RESEARCH_CEVG_ENABLED=1` is explicitly configured.

For an isolated local USB-camera experimental run:

```bash
WVAB_RESEARCH_CEVG_ENABLED=1 \
WVAB_RESEARCH_CEVG_MAX_AGE_S=0.5 \
WVAB_RESEARCH_CEVG_MIN_CONFIDENCE=0.5 \
python navigation_pipeline.py
```

The camera source in `config/config.yaml` must be an integer OpenCV device
index for this adapter. URL sources are **not** granted remote authentication
by implication and will yield `DEGRADED` for existing planned paths. The
integration measures age from the Python `cap.read()` completion to the
decision; it does not measure camera exposure age or audio delivery latency.
Zero detections are conservatively classified as abstention: this may increase
false abstention on clear scenes and is an experimental limitation, not evidence
of improved navigational safety.

The existing `STOP` path for no camera, no localization or no path is retained.
A CEVG failure with an otherwise available path yields `DEGRADED` with a
`cevg_reason` field, not a motor-stop command. No production users should
enable this setting until real hardware and user-impact testing is complete.

## Labeled trace comparison

```bash
python -m research.replay_comparison path/to/independently-labeled.csv \
  --max-age-s 0.5 --min-confidence 0.5 --out research-result.json
```

A trace must include columns described in `research/replay_comparison.py`.
The ground-truth label must be created independently of the eligibility
conditions; otherwise evaluation is circular. The comparison tool does not
currently replay original Flutter `GuidanceEngine` outputs, so results from
confidence/auth/freshness baselines cannot be described as a head-to-head
comparison against the fully deployed WVAB baseline. No empirical improvement
is claimed by this branch.


## Remote capture-time proof research module

`core/remote_capture_proof.py` computes a **conservative upper bound** on
camera capture age using an authenticated frame/session match and an externally
verified clock-offset interval. The proof must originate from a trusted
synchronization/transport adapter, **not** a user-supplied packet field or
CSV label. This is a pure, executable model; ESP32 firmware does not yet emit
trusted capture metadata and the receiver does not yet independently establish
clock-offset intervals. Therefore remote frame freshness is **not currently
proved by the production data path**.

The offline replay CSV now includes `capture_time_verified`; this represents
an externally validated label for analysis, not authentication by itself.

Until a complete authenticated sender-timestamp, session/frame binding and
clock synchronization path has been implemented, do not set remote
`capture_time_verified=True` in production. The gate otherwise abstains.


## Real local navigation decision capture (no fabricated observations)

The opt-in receiver-side research recorder saves one row per processed local
frame, including both the existing navigation policy decision and the
experimental CEVG decision. It does **not** store camera images, location, object
names, secrets, or any independent ground truth.

```bash
export WVAB_RESEARCH_CEVG_ENABLED=1
export WVAB_RESEARCH_TRACE_PATH="evidence/local-decision-run.csv"
export WVAB_RESEARCH_RUN_ID="trial_001"
python navigation_pipeline.py
```

Trace rows contain receiver-side frame age, maximum detector score,
calibration/localization booleans, path existence and the policy decisions.
The output is suitable for diagnostic **paired comparison**, not yet for
validating false-positive guidance. Independently annotated ground-truth hazard
and capture-time evidence are still required to establish accuracy.

The offline replay module now includes `existing_navigation` as a baseline
that matches the published navigation state gate for path existence, calibrated
metric map, metric localization, and localization freshness. It does **not**
emulate the entire audio or Flutter guidance engine. Report both unsupported
guidance and valid-guidance recall, not only abstention counts.

## Release gates before calling the article experimentally validated

1. Record the exact source commit, hardware, model checksum, camera calibration,
   firmware, network environment, and protocol revision.
2. Establish capture-to-decision timing with authenticated per-frame metadata
   and a verified offset-uncertainty interval, or mark capture age unknown.
3. Collect timestamped physical camera/radio traces with reproducible fault
   injection, plus independent annotations or a documented ground-truth oracle.
4. Compare the existing navigation output and the proposed policy on identical
   traces. Include valid-guidance retention, unsupported-issued fraction,
   abstention, workload/latency and paired uncertainty intervals.
5. Test with human participants only under an appropriate ethical and
   accessibility review protocol. Do not claim medical or mobility safety based
   on unit tests.
