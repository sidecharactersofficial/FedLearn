# Testing Strategy & Automated Invariants

This document outlines the testing methodology and automated verification passes implemented in the artifact.

---

## 1. Test Suite Structure

The verification pipeline comprises four complementary layers:

| Layer | Command | Scope | Target Duration |
| :--- | :--- | :--- | :--- |
| **1. Dataset Integrity** | `python3 verification/verify_datasets.py` | SHA-256 validation of 4 benchmark parquet tensors | < 5 seconds |
| **2. Artifact Checkpoints** | `python3 verification/verify_manifest.py` | SHA-256 verification of 30 archived tables/metrics/figures | < 5 seconds |
| **3. Unit & Integration** | `make test` | 14 automated pytest cases (models, attacks, defenses, config) | < 15 seconds |
| **4. Formal Proofs** | `make verify-proofs` | Lean 4 machine-checked compilation + 9 math audit tests | < 20 seconds |

---

## 2. Invariants Tested

### A. Algorithmic Invariants
- **Gradient Row Space Containment (Lemma 2):** Tests confirm that linear layer updates lie strictly within the span of input activations ($\text{proj}_{\text{row}(H)}(\Delta W) = \Delta W$).
- **Peer De-Mixing Algebra (Proposition 1):** Tests verify exact algebraic inversion $\frac{N}{N-1}(\Delta W - \frac{1}{N}\Delta w_p) = \frac{1}{N-1}\sum_{i \ne p}\Delta w_i$ across arbitrary dimension $d$ and scale $N$.
- **Differential Privacy Attribution Bound (Theorem 2):** Tests check that empirical attribution under client DP does not exceed theoretical bound $\frac{e^{2\varepsilon} + (N-1)\delta'}{N - 1 + e^{2\varepsilon}}$.
- **Quorum Escrow Bayes Limit (Theorem 3):** Tests verify that $k$-of-$N$ quorum release caps accuracy at $\le 1/k$.

### B. Execution Commands

```bash
# Run all fast tests (< 1 minute total):
make smoke

# Run Python unit tests:
make test

# Run formal verification:
make verify-proofs
```
