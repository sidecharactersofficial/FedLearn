#!/usr/bin/env Rscript
# Phase 4: Defense Trade-Off & Speed-Leakage Pareto Frontier Analysis
# Adheres strictly to ADR-0001 (R performs statistics and plotting)

source("analysis/R/01_load.R")
suppressPackageStartupMessages({
  library(dplyr)
  library(ggplot2)
})

pareto_path <- file.path(Sys.getenv("RUNS_DIR", "runs"), "defense_pareto_results.parquet")
if (!file.exists(pareto_path)) {
  csv_path <- file.path(Sys.getenv("RUNS_DIR", "runs"), "defense_pareto_results.csv")
  if (file.exists(csv_path)) {
    df <- read.csv(csv_path)
  } else {
    stop("No defense_pareto_results found in runs/. Run defense evaluation first.")
  }
} else {
  df <- read_parquet_compat(pareto_path)
}

# 1. Statistical Aggregation (Mean and 95% Confidence Interval across seeds)
defense_summary <- df |>
  group_by(defense, category) |>
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
    tau_lower     = pmax(0, mean_tau - ci_tau),
    tau_upper     = mean_tau + ci_tau,
    ci_top1       = qt(0.975, pmax(n - 1, 1)) * se_top1,
    top1_lower    = pmax(0, mean_top1 - ci_top1),
    top1_upper    = pmin(100, mean_top1 + ci_top1),
    ci_mae        = qt(0.975, pmax(n - 1, 1)) * se_mae,
    ci_f1         = qt(0.975, pmax(n - 1, 1)) * se_f1,
    Tau_Formatted  = sprintf("%.1f ± %.1f", mean_tau, ci_tau),
    Top1_Formatted = sprintf("%.1f ± %.1f", mean_top1, ci_top1),
    MAE_Formatted  = sprintf("%.2f ± %.2f", mean_mae, ci_mae),
    F1_Formatted   = sprintf("%.3f ± %.3f", mean_f1, ci_f1)
  )

# Desired presentation ordering
desired_order <- c(
  "Undefended (SecAgg)",
  "DP (eps=10.0)", "DP (eps=5.0)", "DP (eps=2.0)", "DP (eps=1.0)",
  "Delay (d=1)", "Delay (d=3)", "Delay (d=5)", "Delay (d=10)",
  "Quorum (k=2)", "Quorum (k=3)", "Quorum (k=5)"
)

defense_summary <- defense_summary |>
  mutate(order = match(defense, desired_order)) |>
  arrange(order)

cat("\n========================================================================================\n")
cat("Defense Trade-Off Table: Speed vs. Attribution Leakage (Mean ± 95% CI)\n")
cat("========================================================================================\n")
print(as.data.frame(defense_summary |> select(defense, Tau_Formatted, Top1_Formatted, MAE_Formatted, F1_Formatted)))
cat("========================================================================================\n")

dir.create("analysis/output", showWarnings = FALSE, recursive = TRUE)
dir.create("results/figures", showWarnings = FALSE, recursive = TRUE)
dir.create("results/tables", showWarnings = FALSE, recursive = TRUE)

# 2. Emit LaTeX Table for Paper
latex_file <- "analysis/output/table_defense_tradeoff.tex"
results_latex_file <- "results/tables/table_defense_tradeoff.tex"

write_defense_table <- function(f) {
  sink(f)
  cat("\\begin{table}[t]\n\\centering\n\\small\n")
  cat("\\caption{Defense trade-off: propagation speed ($\\tau_{0.80}$ rounds), origin attribution leakage (Top-1 \\%), timing error (MAE), and utility on known attacks ($F_1$). Mean $\\pm$ 95\\% CI across seeds.}\n")
  cat("\\label{tab:defenses}\n")
  cat("\\begin{tabular}{lcccc}\n\\toprule\n")
  cat("Defense Mechanism & $\\tau_{0.80}$ (rounds) & Top-1 Acc (\\%) & Timing MAE (rnd) & Known Attack $F_1$ \\\\\n\\midrule\n")
  for (i in 1:nrow(defense_summary)) {
    row <- defense_summary[i, ]
    cat(sprintf("%s & %s & %s & %s & %s \\\\\n",
                row$defense, row$Tau_Formatted, row$Top1_Formatted, row$MAE_Formatted, row$F1_Formatted))
  }
  cat("\\bottomrule\n\\end{tabular}\n\\end{table}\n")
  sink()
}

write_defense_table(latex_file)
write_defense_table(results_latex_file)
message(paste("Wrote LaTeX defense table to", latex_file, "and", results_latex_file))

# 3. Publication Plot: Fig. 2 Speed-Leakage Pareto Frontier
p2 <- ggplot(defense_summary, aes(x = mean_tau, y = mean_top1, color = category, shape = category)) +
  geom_errorbar(aes(ymin = top1_lower, ymax = top1_upper), width = 0.3, alpha = 0.6) +
  geom_errorbarh(aes(xmin = tau_lower, xmax = tau_upper), height = 1.0, alpha = 0.6) +
  geom_point(size = 2.8) +
  geom_text(aes(label = gsub(".*\\((.*)\\)", "\\1", defense)),
            hjust = -0.2, vjust = 0.4, size = 2.4, show.legend = FALSE) +
  scale_color_manual(values = c(
    "Undefended" = "#d95f02",
    "DP"         = "#1f77b4",
    "Delay"      = "#2ca02c",
    "Quorum"     = "#9467bd"
  )) +
  labs(
    x = "Rounds to 80% zero-day recall at non-origin sites (tau_0.80)",
    y = "Origin site attribution accuracy (Top-1 %)",
    color = "Defense Category",
    shape = "Defense Category"
  ) +
  theme_bw(base_size = 8) +
  theme(
    legend.position = "bottom",
    legend.title = element_text(size = 7, face = "bold"),
    legend.text = element_text(size = 7),
    legend.box.margin = margin(t = -5)
  )

plot_file <- "analysis/output/fig2_pareto_frontier.pdf"
results_plot_file <- "results/figures/fig2_pareto_frontier.pdf"
ggsave(plot_file, p2, width = 4.2, height = 3.2)
ggsave(results_plot_file, p2, width = 4.2, height = 3.2)
message(paste("Wrote Pareto plot to", plot_file, "and", results_plot_file))

