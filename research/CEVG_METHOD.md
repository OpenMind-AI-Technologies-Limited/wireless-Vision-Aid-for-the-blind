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
