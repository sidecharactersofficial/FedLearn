# Open Science, Deterministic Reproducibility & Artifact Inventory

This document provides the complete open science inventory for:
**"Who Saw It First: Zero-Day Propagation and Attribution Leakage in Federated Intrusion Detection"** (*IEEE Symposium on Security and Privacy*).

---

## 1. Open Science Commitments

1. **Public Repository:** The complete source code, configurations, proofs, and preprocessed telemetry benchmarks are publicly archived at:
   `https://anonymous.4open.science/r/who-saw-it-first-flids`
2. **Double-Blind Anonymity:** All artifacts, code comments, commit logs, configurations, and documentation have been scrubbed of author identities, affiliations, and local path references.
3. **Machine-Checked Formal Rigor:** All 9 mathematical theorems, propositions, lemmas, and corollaries are formalized in Lean 4 without external axioms (`leanproofs/`).

---

## 2. Deterministic Reproducibility Parameters

All empirical sweeps utilize fixed random seeds:
- **Partitioning & Initialization Seed:** `seed=42` across Dirichlet data splitting, neural weight initialization, and client scheduling.
- **Statistical Replication Seeds:** 10 independent seeds (`seeds = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]`) for tabular meta-classifier evaluation (Table 3, Table 4, Table 5) with 95% bootstrap confidence intervals.
- **Federated Training Parameters:**
  - Silo count: $N = 10$ (scaled to $N = 50, 100$ in Section 6.5)
  - Non-IID Dirichlet parameter: $\alpha \in \{0.1, 0.5, 1.0, 10.0\}$ (default $\alpha = 0.5$)
  - Local SGD epochs: $E = 3$
  - Local batch size: $B = 64$
  - Client learning rate: $\eta = 0.001$ with Adam optimizer
  - Outbreak injection round: $t_0 = 20$
  - Total simulation rounds: $R = 50$
  - Zero-day volume fraction: $\gamma = 0.15$

---

## 3. Complete Experiment & Claim Inventory

| Manifest | Paper Claim | Target Metric / Finding | Generating Script | Output Artifact |
| :--- | :--- | :--- | :--- | :--- |
| `E-EXP01` | C1 (§6.1) | Zero-day propagation speed $\tau_{0.80} \le 4.5$ rounds; skew scaling | `scripts/smoke.sh` | `results/figures/fig_propagation.pdf` |
| `E-EXP02` | C2 (§6.3) | Table 3: Origin Top-1 (96.4% Server, 61.4% SecAgg); Timing MAE (0.61 rds) | `scripts/run_table3_suite.sh` | `results/metrics/table3_results.csv`, `results/tables/table3_attack_success.tex` |
| `E-EXP03` | C3 (§6.4) | Table 4, Fig 3: Pareto trade-offs (DP delays $\tau_{0.80}$ to $12.4$, Quorum caps at $1/k$) | `scripts/run_fig2_defenses.sh` | `results/metrics/defense_pareto_results.csv`, `results/figures/fig_tradeoff.pdf` |
| `E-EXP04` | C4 (§6.5) | Table 5: Operational stress tests (SOC delay, Unlabeled AE, Concurrent outbreaks) | `scripts/run_sec5_5_robustness.sh` | `results/metrics/sec5_5_robustness_results.csv`, `results/tables/table_sec5_5_robustness.tex` |
| `E-EXP05` | C1/C4 (§6.2, App. B) | Table 6, Fig 4: Multi-benchmark 50-round FL across 16 attack families | `scripts/run_50fl_4datasets.py` | `results/metrics/fl50_4datasets_summary.csv`, `results/tables/table_fl50_4datasets.tex` |
| `E-EXP06` | C4 (§6.5) | Federation scale expansion to $N=50, 100$ sites | `scripts/run_sec5_5_robustness.sh` | `results/metrics/scalability_results.csv`, `results/tables/table_scalability.tex` |
| `E-EXP07` | C5 (§5, App. A) | 9 machine-checked formal proofs in Lean 4 (0 sorrys, 0 axioms) | `make verify-proofs` | `leanproofs/MATH_AUDIT_REPORT.md` |
