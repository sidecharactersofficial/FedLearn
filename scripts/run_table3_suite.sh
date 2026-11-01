#!/usr/bin/env bash
# Phase 3: Run Table 3 attack evaluation across 10 seeds and format via R
set -eu
cd "$(dirname "$0")/.."

[ -f .env ] || cp .env.example .env
set -a; . ./.env; set +a

mkdir -p results/logs results/metrics results/tables
LOG_FILE="results/logs/phase3_table3.log"

run_table3() {
    echo "=========================================================="
    echo "Phase 3: Shadow Federations & Origin Attribution Attacks"
    echo "=========================================================="

    python3 attack/meta_classifier.py --seeds 10 --shadow-runs 20 --rounds 25 --output-dir runs


    if [ -f runs/table3_results.parquet ]; then
        cp runs/table3_results.parquet results/metrics/
        cp runs/table3_results.csv results/metrics/
    fi

    echo "Invoking R statistical analysis for Table 3..."
    Rscript analysis/R/table3_analysis.R
    echo "Phase 3 Table 3 Suite completed successfully."
}

run_table3 2>&1 | tee "$LOG_FILE"

