# System Architecture & Technical Implementation

This document describes the architectural design and module composition of the FedLearn evaluation harness.

---

## 1. Multi-Language Modular Split

To ensure high-throughput execution, statistical rigor, and mathematical verification, the codebase employs a language-specialized modular design:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                             Orchestrator (Rust)                             │
│       High-throughput concurrent sweep execution, process supervision       │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Protobuf Contracts (.proto)
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Worker Runtime (Python)                          │
│   Flower FL simulation (PyTorch) ──► Attack Engine ──► Feature Extractor    │
│   (Dirichlet partitioning, SGD)      (Shadow XGBoost)  (Inflection norms)   │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ Parquet / CSV Telemetry
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Analysis & Formal Verification                       │
│    R / Python (Statistical bootstrap CIs, LaTeX tables, Pareto plots)       │
│    Lean 4 (Machine-checked formal proofs, 0 sorrys, 0 external axioms)      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Composition

### A. Python Worker Engine (`worker/src/fedids_worker/`)
- `federation/`: Flower-based cross-silo simulation. Implements client models, local SGD optimizers, and server aggregators (FedAvg, FedProx, FedYogi).
- `defenses/`: Implementations of defensive mechanisms:
  - Cryptographic Secure Aggregation (SecAgg exact summation)
  - Client-Level DP (`DP-FedAvg` with Gaussian noise $\sigma = \frac{C \sqrt{2 \ln(1.25/\delta)}}{N \varepsilon}$)
  - Delayed Temporal Buffering ($d=3$ rounds)
  - Thresholded Quorum Escrow ($k$-of-$N$ release policy)
- `robustness/`: Operational stress tests (SOC analyst delay, unsupervised autoencoder reconstruction, concurrent outbreaks, concept drift).
- `io.py` & `contracts/`: Strongly-typed Protobuf IPC serializers and Apache Parquet readers/writers.

### B. Attack & Attribution Suite (`attack/`)
- `shadow_generator.py`: Instantiates synthetic shadow federations sampled from auxiliary Dirichlet distributions $\alpha_{\text{shadow}}$.
- `feature_extractor.py`: Extracts spatio-temporal gradient features:
  - Weight difference norm inflection: $\|\Delta W^{(t)} - \Delta W^{(t-1)}\|$
  - Layer-wise cosine similarities with historical baselines
  - Probing loss shifts on auxiliary traffic probes
  - Subspace projection alignment coefficients
- `meta_classifier.py`: Trains gradient-boosted decision trees (XGBoost) for site attribution ($\hat{o} \in \{1,\dots,N\}$) and Huber regressors for compromise onset timing ($\hat{t}_0$).

### C. Formal Proof Suite (`leanproofs/`)
- Fully self-contained Lean 4 formalization of the 9 core mathematical results in `leanproofs/FedlearnProofs/Basic.lean`.
- Automated test harness (`verify_math.py`) verifying algebraic identities and bounds across $10^5$ numerical parameter configurations.

### D. Orchestrator (`orchestrator/`)
- High-concurrency Rust runner supervising Python worker processes over parallel parameter sweeps with TOML manifests (`orchestrator/sweeps/`).
