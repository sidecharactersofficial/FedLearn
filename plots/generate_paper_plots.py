#!/usr/bin/env python3
"""Master Paper Plot & Table Generator.

Adheres strictly to ADR-0001: delegates statistical summarization,
confidence interval computation, and publication graphics generation
to the decoupled R analysis engine under `analysis/`.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "analysis" / "output"
PLOTS_DIR = ROOT / "plots"


def run_r_script(script_relpath: str) -> None:
    print(f"\n[R Analysis] Executing {script_relpath}...")
    cmd = ["Rscript", script_relpath]
    res = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    if res.stdout:
        print(res.stdout)
    if res.returncode != 0:
        print(f"Error executing {script_relpath}:", file=sys.stderr)
        print(res.stderr, file=sys.stderr)
        sys.exit(res.returncode)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=================================================================")
    print("Generating EuroS&P Paper Figures and Tables via R (ADR-0001)")
    print("=================================================================")

    # 1. Fig 1: Propagation trajectory & skew impact
    run_r_script("analysis/run_analysis.R")

    # 2. Table 3: Attack success under server & peer adversaries
    if (ROOT / "runs" / "table3_results.parquet").exists() or (ROOT / "runs" / "table3_results.csv").exists():
        run_r_script("analysis/R/table3_analysis.R")
    else:
        print("[Notice] runs/table3_results not found yet. Run scripts/run_table3_suite.sh first.")

    # 3. Fig 2 & Table 4: Speed-Leakage Pareto Frontier across defenses
    if (ROOT / "runs" / "defense_pareto_results.parquet").exists() or (ROOT / "runs" / "defense_pareto_results.csv").exists():
        run_r_script("analysis/R/fig2_pareto.R")
    else:
        print("[Notice] runs/defense_pareto_results not found yet. Run scripts/run_fig2_defenses.sh first.")

    # 4. Section 5.5 Robustness Table under operational perturbations
    if (ROOT / "runs" / "sec5_5_robustness_results.parquet").exists() or (ROOT / "runs" / "sec5_5_robustness_results.csv").exists():
        run_r_script("analysis/R/sec5_5_robustness.R")
    else:
        print("[Notice] runs/sec5_5_robustness_results not found yet. Run scripts/run_sec5_5_robustness.sh first.")

    RESULTS_DIR = ROOT / "results"
    FIGURES_DIR = RESULTS_DIR / "figures"
    TABLES_DIR = RESULTS_DIR / "tables"
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    TABLES_DIR.mkdir(parents=True, exist_ok=True)

    # Mirror generated PDF figures into results/figures/ and plots/
    for pdf in OUTPUT_DIR.glob("*.pdf"):
        shutil.copy2(pdf, FIGURES_DIR / pdf.name)
        shutil.copy2(pdf, PLOTS_DIR / pdf.name)
        print(f"Mirrored {pdf.name} -> results/figures/{pdf.name} and plots/{pdf.name}")

    # Mirror generated LaTeX tables into results/tables/
    for tex in OUTPUT_DIR.glob("*.tex"):
        shutil.copy2(tex, TABLES_DIR / tex.name)
        print(f"Mirrored {tex.name} -> results/tables/{tex.name}")

    print("\nAll paper figures and tables successfully processed in results/figures/, results/tables/, and analysis/output/.")



if __name__ == "__main__":
    main()
