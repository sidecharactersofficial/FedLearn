# Reproduction Guide

This document provides instructions for executing full empirical reproductions from scratch.

---

## 1. Environment Setup

```bash
# Unpack artifact and enter project directory
cd who-saw-it-first-artifact

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies and local worker package
pip install -r requirements.txt
pip install -e worker --no-deps

# Verify environment
make verify-env
```

---

## 2. Fast Verification (< 2 minutes)

Before running long reproduction sweeps, confirm data, checkpoints, tests, and proofs pass:
```bash
make smoke
make verify-proofs
```

---

## 3. Empirical Reproduction Workflow

Each empirical evaluation can be run independently or via unified make targets:

### Step 3.1: Phase 3 — Origin Attribution & Timing Inference (Table 3 & Fig. 2)
Trains shadow federations and evaluates XGBoost meta-classifiers and Huber timing regressors across 10 independent seeds:
```bash
make reproduce-attacks
# or
./scripts/run_table3_suite.sh
```
- **Generated Outputs:**
  - `runs/table3_results.csv` and `runs/table3_results.parquet`
  - Formatted LaTeX table: `results/tables/table3_attack_success.tex`
- **Verification against Archive:**
  ```bash
  python3 verification/compare_results.py results/metrics/table3_results.csv runs/table3_results.csv
  ```

---

### Step 3.2: Phase 4 — Defense Evaluations & Speed-Leakage Pareto Frontier (Table 4 & Fig. 3)
Evaluates 8 defense configurations (SecAgg, Client DP with $\varepsilon \in \{10, 5, 2, 1\}$, Delayed Buffering $d=3$, Quorum Escrow $k \in \{2, 3\}$):
```bash
make reproduce-defenses
# or
./scripts/run_fig2_defenses.sh
```
- **Generated Outputs:**
  - `runs/defense_pareto_results.csv` and `runs/defense_pareto_results.parquet`
  - Formatted LaTeX table: `results/tables/table_defense_tradeoff.tex`
  - Pareto frontier plot: `results/figures/fig_tradeoff.pdf`
- **Verification against Archive:**
  ```bash
  python3 verification/compare_results.py results/metrics/defense_pareto_results.csv runs/defense_pareto_results.csv
  ```

---

### Step 3.3: Phase 5 — Operational Friction & Robustness Suite (Table 5)
Simulates SOC label delay ($\Delta t \in \{2, 5\}$), unlabeled autoencoder bottleneck, concurrent multi-site outbreaks, concept drift, and scale expansion ($N=50, 100$):
```bash
make reproduce-robustness
# or
./scripts/run_sec5_5_robustness.sh
```
- **Generated Outputs:**
  - `runs/sec5_5_robustness_results.csv` and `runs/sec5_5_robustness_results.parquet`
  - Formatted LaTeX table: `results/tables/table_sec5_5_robustness.tex`
- **Verification against Archive:**
  ```bash
  python3 verification/compare_results.py results/metrics/sec5_5_robustness_results.csv runs/sec5_5_robustness_results.csv
  ```

---

### Step 3.4: Phase 6 — Extended Cross-Dataset 50-Round Sweeps (Table 6 & Fig. 4)
Runs full 50-round FL sweeps ($R=50, t_0=20, N=10, \alpha=0.5$) across all 4 intrusion datasets and 16 attack families:
```bash
make reproduce-crossdataset
# or
python3 scripts/run_50fl_4datasets.py
python3 scripts/calibrate_fl50_data.py
```
- **Generated Outputs:**
  - `results/metrics/fl50_4datasets_summary.csv`
  - `results/tables/table_fl50_4datasets.tex`
  - `results/figures/fig_crossdataset_fl50.pdf`

---

### Step 3.5: Regenerate All Publication Figures
Render all PDF and PNG publication figures:
```bash
make reproduce-plots
# or
python3 plots/generate_paper_plots.py
```
- **Generated Outputs:**
  - `results/figures/fig1a_propagation.pdf`
  - `results/figures/fig1b_skew_vs_tau.pdf`
  - `results/figures/fig2_pareto_frontier.pdf`
  - `results/figures/fig_confusion_matrix_single.pdf`
  - `results/figures/fig_crossdataset_fl50.pdf`

---

## 4. Run Everything in a Single Command

```bash
make reproduce-all
```
This runs `smoke`, `verify-proofs`, `reproduce-attacks`, `reproduce-defenses`, `reproduce-robustness`, `reproduce-crossdataset`, and `reproduce-plots`.
