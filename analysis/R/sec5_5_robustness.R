#!/usr/bin/env Rscript
# Section 5.5: Operational Perturbations & Robustness Statistical Analysis
# Adheres strictly to ADR-0001 (R performs statistics and tables)

source("analysis/R/01_load.R")
suppressPackageStartupMessages({
  library(dplyr)
})

robustness_path <- file.path(Sys.getenv("RUNS_DIR", "runs"), "sec5_5_robustness_results.parquet")
if (!file.exists(robustness_path)) {
  csv_path <- file.path(Sys.getenv("RUNS_DIR", "runs"), "sec5_5_robustness_results.csv")
  if (file.exists(csv_path)) {
    df <- read.csv(csv_path)
  } else {
    stop("No sec5_5_robustness_results found in runs/. Run robustness evaluation first.")
  }
} else {
  df <- read_parquet_compat(robustness_path)
}

# 1. Statistical Aggregation (Mean and 95% Confidence Interval across seeds)
robustness_summary <- df |>
  group_by(perturbation, setting) |>
  summarise(
    n             = n(),
    mean_tau      = mean(tau_0.80),
    se_tau        = ifelse(n() > 1, sd(tau_0.80) / sqrt(n()), 0),
    mean_top1     = mean(top1_origin_acc),
    se_top1       = ifelse(n() > 1, sd(top1_origin_acc) / sqrt(n()), 0),
    mean_mae      = mean(timing_mae),
    se_mae        = ifelse(n() > 1, sd(timing_mae) / sqrt(n()), 0),
    mean_f1       = mean(known_family_f1),
    se_f1         = ifelse(n() > 1, sd(known_family_f1) / sqrt(n()), 0),
    .groups       = "drop"
  ) |>
  mutate(
    ci_tau        = qt(0.975, pmax(n - 1, 1)) * se_tau,
    ci_top1       = qt(0.975, pmax(n - 1, 1)) * se_top1,
    ci_mae        = qt(0.975, pmax(n - 1, 1)) * se_mae,
    ci_f1         = qt(0.975, pmax(n - 1, 1)) * se_f1,
    Tau_Formatted  = sprintf("%.1f ± %.1f", mean_tau, ci_tau),
    Top1_Formatted = sprintf("%.1f ± %.1f", mean_top1, ci_top1),
    MAE_Formatted  = sprintf("%.2f ± %.2f", mean_mae, ci_mae),
    F1_Formatted   = sprintf("%.3f ± %.3f", mean_f1, ci_f1)
  )

cat("\n========================================================================================\n")
cat("Section 5.5: Operational Perturbations & Robustness Table (Mean ± 95% CI)\n")
cat("========================================================================================\n")
print(as.data.frame(robustness_summary |> select(perturbation, setting, Tau_Formatted, Top1_Formatted, MAE_Formatted, F1_Formatted)))
cat("========================================================================================\n")

dir.create("analysis/output", showWarnings = FALSE, recursive = TRUE)
dir.create("results/tables", showWarnings = FALSE, recursive = TRUE)

# 2. Emit LaTeX Table for Paper
latex_file <- "analysis/output/table_sec5_5_robustness.tex"
results_latex_file <- "results/tables/table_sec5_5_robustness.tex"

write_robustness_table <- function(f) {
  sink(f)
  cat("\\begin{table}[t]\n\\centering\n\\small\n")
  cat("\\caption{Robustness under operational perturbations (Section 5.5): propagation speed ($\\tau_{0.80}$), origin attribution accuracy (Top-1 \\%), timing error (MAE), and utility ($F_1$). Mean $\\pm$ 95\\% CI.}\n")
  cat("\\label{tab:robustness}\n")
  cat("\\begin{tabular}{llcccc}\n\\toprule\n")
  cat("Operational Perturbation & Setting & $\\tau_{0.80}$ (rnd) & Top-1 Acc (\\%) & Timing MAE (rnd) & Known $F_1$ \\\\\n\\midrule\n")
  for (i in 1:nrow(robustness_summary)) {
    r <- robustness_summary[i, ]
    clean_setting <- gsub("Delta t_SOC", "$\\\\Delta t_{\\\\text{SOC}}$", r$setting)
    cat(sprintf("%s & %s & %s & %s & %s & %s \\\\\n",
                r$perturbation, clean_setting, r$Tau_Formatted, r$Top1_Formatted, r$MAE_Formatted, r$F1_Formatted))
  }

  cat("\\bottomrule\n\\end{tabular}\n\\end{table}\n")
  sink()
}

write_robustness_table(latex_file)
write_robustness_table(results_latex_file)
message(paste("Wrote LaTeX robustness table to", latex_file, "and", results_latex_file))

