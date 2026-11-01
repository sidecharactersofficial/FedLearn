#!/usr/bin/env python3
"""Generate LaTeX table from fl50_4datasets_summary.csv."""

import pandas as pd
from pathlib import Path

csv_path = Path("results/metrics/fl50_4datasets_summary.csv")
out_tex = Path("results/tables/table_fl50_4datasets.tex")
out_tex.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(csv_path)

tex_lines = [
    r"\begin{table*}[t]",
    r"\caption{Comprehensive 50-Round Federated Learning Evaluation Across All 4 Intrusion Datasets and Constituent Attack Families ($N=10, \alpha=0.5, t_0=20, R=50$).}",
    r"\label{tab:fl50_4datasets}",
    r"\begin{center}",
    r"\small\setlength{\tabcolsep}{6pt}",
    r"\begin{tabular}{@{}llccccc@{}}",
    r"\toprule",
    r"\textbf{Dataset} & \textbf{Held-Out Zero-Day ($f^\star$)} & \textbf{$\tau_{0.80}$ (Rds)} & \textbf{Peak Recall} & \textbf{Final Recall ($R=50$)} & \textbf{AUPC$_{20}$} & \textbf{Catastrophic Forgetting} \\",
    r"\midrule",
]

current_ds = None
for _, r in df.iterrows():
    ds = r["dataset"]
    fam = r["macro_family"]
    tau = f"{r['tau_0.80_rounds']:.1f}" if r["tau_0.80_rounds"] >= 0 else ">30"
    pk = f"{r['peak_non_origin_recall']:.3f}"
    fn = f"{r['final_non_origin_recall']:.3f}"
    aupc = f"{r['aupc_20']:.3f}"
    cf = f"{r['catastrophic_forgetting']:.4f}"

    if current_ds is not None and current_ds != ds:
        tex_lines.append(r"\midrule")
    current_ds = ds
    tex_lines.append(f"{ds} & {fam} & {tau} & {pk} & {fn} & {aupc} & {cf} \\\\")

tex_lines.extend([
    r"\bottomrule",
    r"\end{tabular}",
    r"\end{center}",
    r"\end{table*}",
    "",
])

out_tex.write_text("\n".join(tex_lines))
print(f"Generated {out_tex}")
