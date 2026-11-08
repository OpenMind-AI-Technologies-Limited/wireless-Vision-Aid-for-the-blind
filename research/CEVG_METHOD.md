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
