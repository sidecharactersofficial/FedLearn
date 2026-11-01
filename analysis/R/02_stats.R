# Summaries across seeds: mean and 95% confidence interval per round.
suppressPackageStartupMessages(library(dplyr))

summarise_propagation <- function(runs) {
  runs |>
    filter(metric == "zero_day_recall", site != origin_site) |>
    group_by(num_sites, skew, defense_kind, round, run_id) |>
    summarise(recall = mean(value), .groups = "drop_last") |>   # average over non-origin sites
    summarise(
      n    = n(),
      mean = mean(recall),
      se   = ifelse(n() > 1, sd(recall) / sqrt(n()), 0),
      .groups = "drop"
    ) |>
    mutate(
      lower = pmax(0, mean - qt(0.975, pmax(n - 1, 1)) * se),
      upper = pmin(1, mean + qt(0.975, pmax(n - 1, 1)) * se)
    )
}

summarise_skew_tau <- function(runs) {
  runs |>
    filter(metric == "tau_0.80") |>
    group_by(num_sites, skew) |>
    summarise(
      n        = n(),
      mean_tau = mean(value),
      se_tau   = ifelse(n() > 1, sd(value) / sqrt(n()), 0),
      .groups  = "drop"
    ) |>
    mutate(
      lower = pmax(0, mean_tau - qt(0.975, pmax(n - 1, 1)) * se_tau),
      upper = mean_tau + qt(0.975, pmax(n - 1, 1)) * se_tau
    )
}

