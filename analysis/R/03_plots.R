# Plots. Axis labels use words, with units in parentheses (venue style).
suppressPackageStartupMessages(library(ggplot2))

plot_propagation <- function(summary_df) {
  ggplot(summary_df, aes(x = round, y = mean)) +
    geom_ribbon(aes(ymin = lower, ymax = upper), alpha = 0.2, na.rm = TRUE) +
    geom_line(color = "#1f77b4", linewidth = 0.8) +
    labs(
      x = "Training round",
      y = "Recall on zero-day attack at non-origin sites"
    ) +
    theme_bw(base_size = 8)   # 8 point figure labels
}

plot_skew_vs_tau <- function(skew_tau_df) {
  ggplot(skew_tau_df, aes(x = factor(skew), y = mean_tau, group = factor(num_sites), color = factor(num_sites))) +
    geom_line(linewidth = 0.8) +
    geom_point(size = 2) +
    geom_errorbar(aes(ymin = lower, ymax = upper), width = 0.15) +
    labs(
      x = "Dirichlet skew parameter (alpha)",
      y = "Rounds to 80% recall (tau_0.80)",
      color = "Consortium sites (N)"
    ) +
    theme_bw(base_size = 8)
}

