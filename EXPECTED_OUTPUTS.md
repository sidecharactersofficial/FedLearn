# Expected Outputs & Schema Inventory

This document defines the schema, shape, and file paths for all primary data outputs generated during evaluation.

---

## Output Files by Experiment

### 1. Phase 3: Origin Attribution & Timing Inference (Table 3)
- **Primary Metrics:** `results/metrics/table3_results.csv` and `table3_results.parquet`
- **Shape:** 70 rows $\times$ 6 columns (10 seeds across 7 condition regimes)
- **Schema:**
  - `seed` (int64): Random seed $\in \{1, \dots, 10\}$
  - `view` (str): Adversary observation view (`Server`, `Peer`, `SecAgg`, `Random`)
  - `regime` (str): Information regime (`Forensic`, `Online`)
  - `top1_acc` (float64): Top-1 institutional attribution accuracy $[0.0, 1.0]$
  - `top3_acc` (float64): Top-3 candidate attribution accuracy $[0.0, 1.0]$
  - `timing_mae` (float64): Mean Absolute Error in onset round estimation (rounds)
- **Formatted LaTeX Table:** `results/tables/table3_attack_success.tex`
- **Confusion Matrix Graphic:** `results/figures/fig_confusion_matrix_single.pdf`

---

### 2. Phase 4: Defense Pareto Trade-offs (Table 4 & Fig. 3)
- **Primary Metrics:** `results/metrics/defense_pareto_results.csv` and `defense_pareto_results.parquet`
- **Shape:** 60 rows $\times$ 7 columns (5 seeds across 12 defense configurations)
- **Schema:**
  - `seed` (int64): Random seed $\in \{1, \dots, 5\}$
  - `defense` (str): Defense family name
  - `param` (str): Hyperparameter setting ($\varepsilon, d, k$)
  - `tau_080` (float64): Zero-day propagation rounds to 0.80 recall
  - `top1_acc` (float64): Origin top-1 attribution accuracy
  - `final_recall` (float64): Round-30 detection recall
  - `f1_score` (float64): Macro F1 on known intrusion families
- **Formatted LaTeX Table:** `results/tables/table_defense_tradeoff.tex`
- **Pareto Graphic:** `results/figures/fig_tradeoff.pdf`

---

### 3. Phase 5: Operational Robustness Stress Tests (Table 5)
- **Primary Metrics:** `results/metrics/sec5_5_robustness_results.csv` and `sec5_5_robustness_results.parquet`
- **Shape:** 40 rows $\times$ 7 columns (5 seeds across 8 operational stress scenarios)
- **Schema:**
  - `seed` (int64): Random seed
  - `condition` (str): Stress test condition (e.g., `SOC_Delay_2`, `Unlabeled_AE`)
  - `timing_mae` (float64): Onset timing error (rounds)
  - `top1_acc` (float64): Origin attribution accuracy $[0.0, 1.0]$
  - `top3_acc` (float64): Top-3 localization accuracy
  - `propagation_tau` (float64): Zero-day propagation delay
  - `runtime_sec` (float64): Execution runtime in seconds
- **Formatted LaTeX Table:** `results/tables/table_sec5_5_robustness.tex`

---

### 4. Phase 6: Extended 50-Round FL Suite Across 4 Benchmarks (Table 6 & Fig. 4)
- **Primary Metrics:** `results/metrics/fl50_4datasets_summary.csv`
- **Shape:** 16 rows $\times$ 11 columns (16 zero-day macro-families across 4 datasets)
- **Schema:**
  - `dataset` (str): Benchmark dataset (`CSE-CIC-IDS2018`, `ToN-IoT`, `UNSW-NB15`, `NSL-KDD`)
  - `macro_family` (str): Held-out novel zero-day attack family $f^\star$
  - `seed` (int64): Fixed evaluation seed (`42`)
  - `rounds` (int64): Total communication rounds (`50`)
  - `injection_round` (int64): Onset round $t_0$ (`20`)
  - `tau_0.80_rounds` (float64): Rounds to reach $\ge 0.80$ non-origin recall
  - `final_non_origin_recall` (float64): Round-50 recall on $f^\star$
  - `peak_non_origin_recall` (float64): Maximum recall observed across rounds
  - `aupc_20` (float64): Post-injection Area Under Propagation Curve
  - `catastrophic_forgetting` (float64): Performance drop on historical attacks
  - `runtime_seconds` (float64): Wall-clock simulation duration
- **Formatted LaTeX Table:** `results/tables/table_fl50_4datasets.tex`
- **Cross-Dataset Trajectory Graphic:** `results/figures/fig_crossdataset_fl50.pdf`
