#!/usr/bin/env Rscript
# Table 3 Statistical Analysis & Paper Formatting
# Computes Mean and 95% Confidence Intervals across seeds for Table 3.

source("analysis/R/01_load.R")
suppressPackageStartupMessages({
  library(dplyr)
})

table3_path <- file.path(Sys.getenv("RUNS_DIR", "runs"), "table3_results.parquet")
if (!file.exists(table3_path)) {
  csv_path <- file.path(Sys.getenv("RUNS_DIR", "runs"), "table3_results.csv")
  if (file.exists(csv_path)) {
    df <- read.csv(csv_path)
  } else {
    stop("No table3_results found in runs/. Run scripts/run_table3_suite.sh first.")
  }
} else {
  df <- read_parquet_compat(table3_path)
}

table3_summary <- df |>
  group_by(regime, mode) |>
  summarise(
    n = n(),
    mean_top1 = mean(top1_acc),
    se_top1   = ifelse(n() > 1, sd(top1_acc) / sqrt(n()), 0),
    mean_top3 = mean(top3_acc),
    se_top3   = ifelse(n() > 1, sd(top3_acc) / sqrt(n()), 0),
    mean_mae  = mean(timing_mae),
    se_mae    = ifelse(n() > 1, sd(timing_mae) / sqrt(n()), 0),
    .groups   = "drop"
  ) |>
  mutate(
    top1_ci = qt(0.975, pmax(n - 1, 1)) * se_top1,
    top3_ci = qt(0.975, pmax(n - 1, 1)) * se_top3,
    mae_ci  = qt(0.975, pmax(n - 1, 1)) * se_mae,
    Top1_Formatted = sprintf("%.1f ± %.1f", mean_top1, top1_ci),
    Top3_Formatted = sprintf("%.1f ± %.1f", mean_top3, top3_ci),
    MAE_Formatted  = sprintf("%.2f ± %.2f", mean_mae, mae_ci)
  )

# Desired order according to Table 3 specification
target_order <- data.frame(
  regime = c("Server (No SecAgg)", "Server (No SecAgg)", "Server (SecAgg)", "Server (SecAgg)", "Peer Client", "Peer Client", "Random Guess Baseline"),
  mode   = c("Forensic", "Surrogate", "Forensic", "Surrogate", "Forensic", "Surrogate", "Theoretical"),
  order  = 1:7
)

formatted_table <- target_order |>
  left_join(table3_summary, by = c("regime", "mode")) |>
  arrange(order) |>
  select(regime, mode, Top1_Formatted, Top3_Formatted, MAE_Formatted)

cat("\n========================================================================================\n")
cat("Table 3: Attack Success: Origin Attribution & Timing Error (Mean ± 95% CI)\n")
cat("========================================================================================\n")
print(as.data.frame(formatted_table))
cat("========================================================================================\n")

# Write out LaTeX table for paper
dir.create("analysis/output", showWarnings = FALSE, recursive = TRUE)
dir.create("results/tables", showWarnings = FALSE, recursive = TRUE)

latex_file <- "analysis/output/table3_attack_success.tex"
results_latex_file <- "results/tables/table3_attack_success.tex"

write_table3 <- function(f) {
  sink(f)
  cat("\\begin{table}[t]\n\\centering\n\\small\n")
  cat("\\caption{Origin attribution accuracy and timing error across operational modes (Mean $\\pm$ 95\\% CI).}\n")
  cat("\\label{tab:attack}\n")
  cat("\\begin{tabular}{llccc}\n\\toprule\n")
  cat("Adversary Setting & Mode & Top-1 Acc (\\%) & Top-3 Acc (\\%) & Timing MAE (rnd) \\\\\n\\midrule\n")
  for (i in 1:nrow(formatted_table)) {
    row <- formatted_table[i, ]
    cat(sprintf("%s & %s & %s & %s & %s \\\\\n",
                row$regime, row$mode, row$Top1_Formatted, row$Top3_Formatted, row$MAE_Formatted))
  }
  cat("\\bottomrule\n\\end{tabular}\n\\end{table}\n")
  sink()
}

write_table3(latex_file)
write_table3(results_latex_file)
message(paste("Wrote LaTeX table to", latex_file, "and", results_latex_file))

