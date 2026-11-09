# CEVG prior-art and contribution boundary — verified source review (Nov 2026)

This is a focused *screen*, not a systematic review. The papers below were
checked against journal/publisher pages. Do not assert a global research gap
until related studies have been systematically searched and assessed.

| Work (verified DOI) | Evidence supported by published work | What WVAB cannot claim as novel |
|---|---|---|
| Bappy, Seppänen & Hoque (2026), *Scientific Reports*, doi:10.1038/s41598-026-51257-9 | Resource-aware edge vision system for visual disabilities with secure IoT communications, object detection and audio assistance | Secure offline/edge vision architecture or integrated communication and perception alone |
| Liu & Slade (2026), *Nature Biomedical Engineering*, doi:10.1038/s41551-026-01772-x | Mobilio navigation system with sensor fusion, audio guidance and real participant/obstacle-course evaluation | Obstacle-aware smartphone navigation and audio guidance by themselves |
| *A wearable obstacle avoidance device for visually impaired individuals with cross-modal learning* (2025), *Nature Communications*, doi:10.1038/s41467-025-58085-x | Cross-modal perception, low latency, wearable device testing and auditory/tactile feedback | Low-latency multimodal wearable warnings or real-time camera/depth perception alone |
| *Communicating AI Uncertainty in Assistive Navigation for People with Visual Impairments* (2026), doi:10.1177/10711813261484587 | Prototype maps uncertainty into auditory prosody for assistive guidance | Uncertainty-aware audio presentation as a new concept |
| *Uncertainty-Aware LiDAR-Camera Autonomy via Conformal Prediction and Principled Abstention* (2025), IEEE COINS, doi:10.1109/COINS65080.2025.11125785 | Selective perception and uncertainty-based abstention in camera/LiDAR settings | Abstention or uncertainty thresholding alone |

## Specific candidate question

On **identical independently annotated physical observations**, does binding
(1) frame AEAD provenance and session, (2) authenticated sender capture uptime,
(3) independently bounded receiver-minus-sender clock offset, and (4) perception
evidence improve the *paired unsupported-warning vs. retained-valid-warning*
trade-off relative to existing WVAB and tuned selective baselines?

This is a **hypothesis**, not an established absence in literature. It requires
a focused database search for authenticated real-time sensory freshness and
safety-aware selectivity in robotics, IoT and visual assistance.

## Essential distinction in measured outcomes

- Descriptive obstacle warning: a named obstacle with approximate left/right
  position. Can be evaluated on detection/action annotation without claiming
  that a path is safe.
- Actionable navigation: MOVE LEFT / MOVE RIGHT / FORWARD / STOP. Requires
  independent path/action correctness labels and stronger localization/metric
  assumptions. The present experimental UDP warning gate does not certify this.
- Correct authentication/clock mathematics: a **necessary systems property**,
  not evidence of lower collision rates or better user outcomes.

## Citation URLs

1. https://doi.org/10.1038/s41598-026-51257-9
2. https://doi.org/10.1038/s41551-026-01772-x
3. https://doi.org/10.1038/s41467-025-58085-x
4. https://doi.org/10.1177/10711813261484587
5. https://doi.org/10.1109/COINS65080.2025.11125785

## Claims still unsupported

A fully novel cross-layer method, real-world safety improvement, participant
benefit, capture-to-audio latency, ESP32 clock drift bound, statistically
significant field superiority, and journal submission-readiness have **not**
been established from the existing GitHub CI or synthetic benchmark.
