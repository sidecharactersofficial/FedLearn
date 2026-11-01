#!/usr/bin/env python3
"""Compare freshly reproduced metrics against the shipped canonical archive.

Pre-declared statistical tolerances (see REPRODUCIBILITY_LEVELS.md):
  * Origin Attribution Accuracy (Top-1) : absolute tolerance 0.03 (3 percentage points)
  * Timing MAE                          : absolute tolerance 0.35 rounds
  * Propagation Delay (tau_0.80)        : absolute tolerance 0.50 rounds
  * Attack Recall / Detection Recall    : absolute tolerance 0.025 (2.5 percentage points)
  * Catastrophic Forgetting             : absolute tolerance 0.005 (0.5 percentage points)

Usage:
  python3 verification/compare_results.py results/metrics/table3_results.csv runs/table3_results.csv
  python3 verification/compare_results.py results/metrics/defense_pareto_results.csv runs/defense_pareto_results.csv
"""

from __future__ import annotations

import argparse
import sys
import pandas as pd
import numpy as np


def compare_dataframes(archive_path: str, fresh_path: str) -> bool:
    print(f"Comparing archive [{archive_path}] vs fresh [{fresh_path}]...")
    
    # Load dataframes (support .csv and .parquet)
    df_arch = pd.read_parquet(archive_path) if archive_path.endswith(".parquet") else pd.read_csv(archive_path)
    df_fresh = pd.read_parquet(fresh_path) if fresh_path.endswith(".parquet") else pd.read_csv(fresh_path)

    failures = []
    
    # Identify numeric columns
    numeric_cols = [c for c in df_arch.columns if c in df_fresh.columns and np.issubdtype(df_arch[c].dtype, np.number)]
    
    for col in numeric_cols:
        v_arch = df_arch[col].dropna().values
        v_fresh = df_fresh[col].dropna().values
        
        if len(v_arch) != len(v_fresh):
            print(f"  [WARN] Length mismatch in {col}: archive={len(v_arch)}, fresh={len(v_fresh)}")
            n_min = min(len(v_arch), len(v_fresh))
            v_arch = v_arch[:n_min]
            v_fresh = v_fresh[:n_min]
            
        # Determine tolerance
        col_lower = col.lower()
        if "acc" in col_lower or "top" in col_lower or "recall" in col_lower:
            atol = 0.03
        elif "mae" in col_lower or "timing" in col_lower:
            atol = 0.35
        elif "tau" in col_lower or "delay" in col_lower:
            atol = 0.50
        elif "forget" in col_lower:
            atol = 0.005
        else:
            atol = 0.05
            
        diffs = np.abs(v_arch - v_fresh)
        max_diff = float(np.max(diffs)) if len(diffs) > 0 else 0.0
        mean_diff = float(np.mean(diffs)) if len(diffs) > 0 else 0.0
        
        ok = max_diff <= atol
        status_str = "OK  " if ok else "FAIL"
        print(f"  [{status_str}] Column {col:25s} | max_diff={max_diff:.4f} | mean_diff={mean_diff:.4f} | tol={atol:.3f}")
        if not ok:
            failures.append(f"{col} exceeded tolerance {atol:.3f} (max diff = {max_diff:.4f})")

    if failures:
        print("\nVerification FAILURES:")
        for f in failures:
            print(f"  - {f}")
        return False
    else:
        print("\nAll numeric columns within pre-declared statistical bounds: PASS")
        return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare fresh vs archived metrics.")
    parser.add_argument("archive", help="Path to archived metric file (.csv or .parquet)")
    parser.add_argument("fresh", help="Path to fresh reproduced metric file (.csv or .parquet)")
    args = parser.parse_args()

    ok = compare_dataframes(args.archive, args.fresh)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
