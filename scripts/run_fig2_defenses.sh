#!/usr/bin/env bash
# Phase 4: Run defense evaluations and render Pareto frontier via R
set -eu
cd "$(dirname "$0")/.."

[ -f .env ] || cp .env.example .env
set -a; . ./.env; set +a

mkdir -p results/logs results/metrics results/figures results/tables
LOG_FILE="results/logs/phase4_defenses.log"

run_defenses() {
    echo "================================================================="
    echo "Phase 4: Evaluating Defenses & Speed-Leakage Pareto Frontier"
    echo "================================================================="

    python3 worker/src/fedids_worker/defenses/defense_suite.py --rounds 30 --seeds 5 --output-dir runs

    if [ -f runs/defense_pareto_results.parquet ]; then
        cp runs/defense_pareto_results.parquet results/metrics/
        cp runs/defense_pareto_results.csv results/metrics/
    fi

    echo "Invoking R statistical analysis & Pareto plot generation..."
    Rscript analysis/R/fig2_pareto.R
    echo "Phase 4 completed successfully."
}

run_defenses 2>&1 | tee "$LOG_FILE"

