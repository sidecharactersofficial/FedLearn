#!/usr/bin/env bash
# Phase 5: Run Section 5.5 operational perturbation sweeps and format via R
set -eu
cd "$(dirname "$0")/.."

[ -f .env ] || cp .env.example .env
set -a; . ./.env; set +a

mkdir -p results/logs results/metrics results/tables
LOG_FILE="results/logs/phase5_robustness.log"

run_robustness() {
    echo "================================================================="
    echo "Phase 5: Section 5.5 Operational Perturbations & Robustness"
    echo "================================================================="

    python3 worker/src/fedids_worker/robustness/operational.py --rounds 30 --seeds 5 --output-dir runs

    if [ -f runs/sec5_5_robustness_results.parquet ]; then
        cp runs/sec5_5_robustness_results.parquet results/metrics/
        cp runs/sec5_5_robustness_results.csv results/metrics/
    fi

    echo "Invoking R statistical analysis & LaTeX table generation..."
    Rscript analysis/R/sec5_5_robustness.R
    echo "Phase 5 completed successfully."
}

run_robustness 2>&1 | tee "$LOG_FILE"

