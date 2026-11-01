# Known Limitations & Research Boundaries

This document details the scientific scope boundaries, empirical assumptions, and practical limitations of the FedLearn evaluation harness.

---

## 1. Network Traffic Realism & Telemetry Fidelity
- **Testbed vs. Production Backbone:** The empirical evaluations are conducted on standard, multi-day benchmark telemetry (CSE-CIC-IDS2018, ToN-IoT, UNSW-NB15, and NSL-KDD). While these benchmarks exhibit diverse attack profiles and realistic feature dimensionality, testbed environments exhibit cleaner background stationarity than live multi-gigabit commercial backbones. On live backbones, high-rate unlabelled background traffic fluctuations could partially mask subtle inflection norms during early outbreak rounds.

## 2. Secure Aggregation Modeling
- **Synchronous vs. Packet-Dropout SecAgg:** In accordance with standard FL literature, Secure Aggregation is modeled mathematically as an exact vector summation $\sum_{i=1}^N \Delta w_i^{(t)}$ over synchronous rounds. In wide-area production networks with client dropouts, dynamic participation matrices could introduce additional side-channel leakage unless mitigated via structured threshold secret sharing.

## 3. Adversary Capability Scope
- **Semi-Honest vs. Malicious Server:** Our threat model restricts the adversary to passive honest-but-curious behavior (faithfully following the protocol while analyzing shared models). An active malicious server capable of distributing inconsistent global weights to isolate specific participants could bypass SecAgg directly.

## 4. Shadow Distribution Fidelity
- **Dirichlet Skew Alignment:** The shadow-federation attack assumes the adversary has an approximate estimate of the consortium's non-IID skew parameter $\alpha$. When the shadow distribution diverges drastically from the target consortium's traffic regime, peer-level attribution under SecAgg degrades toward timing-only inference.

## 5. Computational & Hardware Scope
- **CPU vs. GPU:** All simulation components execute deterministically on commodity multi-core CPUs. A full multi-seed re-execution of the 50-round FL sweeps requires approximately 45–60 minutes on an 8-core CPU; GPU acceleration is supported but optional.
