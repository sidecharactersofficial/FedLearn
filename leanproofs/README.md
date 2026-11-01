# FedLearn: Formal Verification & Mathematical Audit in Lean 4

This directory contains the machine-checked formal verification in Lean 4 and the step-by-step mathematical soundness verification for all theoretical foundations, bounds, and complexity counts established in the **FedLearn** paper (*IEEE S&P 2026*):
`Who Saw It First: Zero-Day Propagation and Attribution Leakage in Federated Intrusion Detection`.

## Directory Structure

- `MATH_AUDIT_REPORT.md`: Comprehensive line-by-line mathematical audit report dissecting every theorem, proposition, lemma, and corollary in `paper/WhoSawItFirst_S&P_Final_Draft.tex` and Appendix A.
- `verify_math.py`: Standalone executable Python mathematical verification test suite checking algebraic identities, geometric unrolling, subspace projections via SVD, and DP bounds.
- `FedlearnProofs/Basic.lean`: Lean 4 formal proofs for all 9 core mathematical theorems, propositions, lemmas, and corollaries.
- `FedlearnProofs.lean`: Root library entry point for Lake.
- `Main.lean`: Executable driver reporting verification status.
- `lakefile.toml` / `lean-toolchain`: Lake project configuration (Lean v4.35.0).

---

## Verified Theorems and Propositions

| Paper Section | Label | Description | Lean Formalization | Status |
|:---|:---|:---|:---|:---:|
| **Section 5.1 & App. A.1** | `prop:demix` | **Proposition 1**: Peer De-Mixing Exact Algebraic Recovery | `prop1_peer_recovery_exact`<br>`prop1_peer_demixing_algebra`<br>`prop1_peer_update_isolation` | **PROVED** |
| **Section 5.2 & App. A.2** | `prop:views` | **Proposition 2**: Information Monotonicity & View Ordering | `prop2_data_processing_monotone`<br>`prop2_subcollection_ordering`<br>`prop2_empirical_view_ordering` | **PROVED** |
| **Section 5.3 & App. A.3** | `lem:dilution` | **Lemma 1**: Per-Round Model Discrepancy Dilution Recurrence | `lem1_origin_norm_bound`<br>`lem1_per_round_dilution_algebra`<br>`lem1_dilution_recurrence_step` | **PROVED** |
| **Section 5.3 & App. A.4** | `thm:tau` | **Theorem 1**: Propagation Delay Lower Bound & Geometric Series | `thm1_geometric_sum_m1..3`<br>`thm1_threshold_inequality`<br>`thm1_sublinear_n_growth` | **PROVED** |
| **Section 5.4 & App. A.5** | `lem:rowspace` | **Lemma 2**: Linear Layer Update Row Space Containment | `lem2_outer_product_row_span`<br>`lem2_sum_preserves_span`<br>`lem2_sgd_accumulation_span` | **PROVED** |
| **Section 5.4 & App. A.6** | `prop:iid` | **Proposition 3**: Exchangeable Client IID Limit & Chance Accuracy | `prop3_bayes_posterior_uniform`<br>`prop3_chance_accuracy` | **PROVED** |
| **Section 5.4 & App. A.7** | `cor:snr` | **Corollary 1**: Subspace Coherence Margin and Attribution SNR | `cor1_projection_diff_algebra`<br>`cor1_coherence_margin_bound`<br>`cor1_orthogonal_margin`<br>`cor1_collinear_margin` | **PROVED** |
| **Section 5.5 & App. A.8** | `thm:dp` | **Theorem 2**: Client-Level DP Origin Attribution Upper Bound | `thm2_two_step_dp_substitution`<br>`thm2_summation_swap_identity_n3`<br>`thm2_dp_accuracy_bound_algebra`<br>`thm2_dp_zero_epsilon_limit` | **PROVED** |
| **Section 5.5 & App. A.9** | `thm:quorum` | **Theorem 3**: Symmetric $k$-of-$N$ Quorum Release Bayes Bound | `thm3_quorum_marginal_bound`<br>`thm3_bayes_accuracy_bound`<br>`thm3_quorum_k_scaling` | **PROVED** |

---

## How to Run the Verification

### 1. Build and Run the Lean 4 Formal Proofs
```bash
export PATH="$HOME/.elan/bin:$PATH"
cd leanproofs
lake build
./.lake/build/bin/fedlearn_proofs
```

### 2. Run Individual File Verification in Lean 4
```bash
export PATH="$HOME/.elan/bin:$PATH"
lean leanproofs/FedlearnProofs/Basic.lean
```

### 3. Run the Python Computational Verification Suite
```bash
python3 leanproofs/verify_math.py
```

