#!/usr/bin/env python3
"""Check reproducibility traceability of archived result files.

Walks ``results/metrics/`` and ``results/logs/`` and verifies that all
required experiment records and tables are present, non-empty, and valid.

Usage:
  python3 scripts/check_traceability.py
"""

from __future__ import annotations

import os
import sys
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS = os.path.join(PROJECT_ROOT, "results")

REQUIRED_METRICS = [
    "results/metrics/table3_results.csv",
    "results/metrics/table3_results.parquet",
    "results/metrics/defense_pareto_results.csv",
    "results/metrics/defense_pareto_results.parquet",
    "results/metrics/sec5_5_robustness_results.csv",
    "results/metrics/sec5_5_robustness_results.parquet",
    "results/metrics/fl50_4datasets_summary.csv",
    "results/metrics/scalability_results.csv",
]

REQUIRED_TABLES = [
    "results/tables/table1_related_work.tex",
    "results/tables/table2_experimental_parameters.tex",
    "results/tables/table3_attack_success.tex",
    "results/tables/table_defense_tradeoff.tex",
    "results/tables/table_sec5_5_robustness.tex",
    "results/tables/table_fl50_4datasets.tex",
]

REQUIRED_LOGS = [
    "results/logs/phase3_table3.log",
    "results/logs/phase4_defenses.log",
    "results/logs/phase5_robustness.log",
    "results/logs/fl50_4datasets.log",
]


def main() -> int:
    print("=" * 68)
    print("  FedLearn: Reproducibility Traceability Audit")
    print("=" * 68)

    missing = []
    
    print("Checking canonical metric archives...")
    for rel in REQUIRED_METRICS:
        p = os.path.join(PROJECT_ROOT, rel)
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            print(f"[MISSING] {rel}")
            missing.append(rel)
        else:
            try:
                df = pd.read_parquet(p) if p.endswith(".parquet") else pd.read_csv(p)
                print(f"[OK]      {rel:45s} ({len(df)} rows, {len(df.columns)} cols)")
            except Exception as e:
                print(f"[CORRUPT] {rel} ({e})")
                missing.append(rel)

    print("\nChecking generated LaTeX tables...")
    for rel in REQUIRED_TABLES:
        p = os.path.join(PROJECT_ROOT, rel)
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            print(f"[MISSING] {rel}")
            missing.append(rel)
        else:
            print(f"[OK]      {rel:45s} ({os.path.getsize(p)} bytes)")

    print("\nChecking execution logs...")
    for rel in REQUIRED_LOGS:
        p = os.path.join(PROJECT_ROOT, rel)
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            print(f"[MISSING] {rel}")
            missing.append(rel)
        else:
            print(f"[OK]      {rel:45s} ({os.path.getsize(p)} bytes)")

    print("=" * 68)
    if missing:
        print(f"traceability: FAIL ({len(missing)} missing or corrupted files)")
        return 1
    print(f"traceability: PASS (All {len(REQUIRED_METRICS) + len(REQUIRED_TABLES) + len(REQUIRED_LOGS)} records verified)")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())
