#!/usr/bin/env Rscript
# Run from the repo root: Rscript analysis/run_analysis.R
source("analysis/R/01_load.R")
source("analysis/R/02_stats.R")
source("analysis/R/03_plots.R")

runs    <- load_runs()
summary <- summarise_propagation(runs)
skew_tau <- summarise_skew_tau(runs)

dir.create("analysis/output", showWarnings = FALSE, recursive = TRUE)
dir.create("results/figures", showWarnings = FALSE, recursive = TRUE)

p_prop <- plot_propagation(summary)
ggsave("analysis/output/propagation.pdf", p_prop, width = 3.3, height = 2.4)
ggsave("analysis/output/fig1a_propagation.pdf", p_prop, width = 3.3, height = 2.4)
ggsave("results/figures/fig1a_propagation.pdf", p_prop, width = 3.3, height = 2.4)
message("wrote analysis/output/fig1a_propagation.pdf and results/figures/fig1a_propagation.pdf")

if (nrow(skew_tau) > 0) {
  p_skew <- plot_skew_vs_tau(skew_tau)
  ggsave("analysis/output/fig1b_skew_vs_tau.pdf", p_skew, width = 3.3, height = 2.4)
  ggsave("results/figures/fig1b_skew_vs_tau.pdf", p_skew, width = 3.3, height = 2.4)
  message("wrote analysis/output/fig1b_skew_vs_tau.pdf and results/figures/fig1b_skew_vs_tau.pdf")
}


