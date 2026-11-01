# Methodological Provenance & Research Evolution

This document traces the development and scientific evolution of the FedLearn evaluation harness.

---

## Methodological Evolution Timeline

```
Initial Observation: Cross-silo NIDS updates leak client traffic fingerprints
       │
       ▼
Theoretical Foundation: Row-space containment & peer de-mixing
       ├── Lemma 2: Linear layer weight updates reside in client activation row-space
       ├── Proposition 1: Curious peer exact algebraic de-mixing
       ▼
Attack Synthesis: Shadow-Federation Meta-Classifiers
       ├── Spatio-temporal feature extraction (inflection norms, cosine shifts)
       ├── XGBoost site attribution & Huber regressor onset timing
       ▼
Defense Analysis & Pareto Trade-offs
       ├── Secure Aggregation is necessary but insufficient (58.2% attribution remains)
       ├── Client-Level DP causes extreme utility trade-offs (tau_0.80 -> inf at eps=1.0)
       ├── Thresholded Quorum Escrow yields optimal Pareto trade-off (bounded by 1/k)
       ▼
Multi-Benchmark Empirical Hardening
       ├── Extended to 4 intrusion benchmarks: CSE-CIC-IDS2018, ToN-IoT, UNSW-NB15, NSL-KDD
       ├── 50-round sweeps across 16 zero-day macro-families (Figure 4, Table 6)
       ▼
Formal Verification in Lean 4
       ├── Machine-checked formalization of all 9 theoretical results (Theorems 1–3, Lemmas 1–2, Props 1–3, Cor 1)
       └── 100% sound verification with 0 sorrys and 0 unproved axioms
```

---

## Key Milestone Decisions

1. **Protobuf Contracts for Cross-Language IPC:** Protocol Buffers (`proto/fedids/v1/`) decouple the Rust orchestration runner from the Python worker, ensuring reproducible, typed experiment definitions.
2. **Columnar Parquet Architecture:** All network flow tensors and evaluation runs are persisted in Apache Parquet format to prevent floating-point serialization artifacts and support streaming evaluation.
3. **Formal Machine-Checking in Lean 4:** To eliminate mathematical hand-waving and prove the bounds without hidden assumptions, all 9 core mathematical propositions and bounds were fully formalized in Lean 4 (`leanproofs/`).
