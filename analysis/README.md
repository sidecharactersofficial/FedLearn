# analysis/ (R)

Statistics, plots, and paper tables. Decoupled from the experiment code:
it reads only `runs/*/metrics.parquet` and `runs/*/meta.parquet`.

## Setup

```r
install.packages("renv")
renv::init()                       # creates renv.lock; commit it
renv::install(c("arrow", "dplyr", "ggplot2"))
renv::snapshot()
```

## Run

```sh
Rscript analysis/run_analysis.R    # from the repo root
```

Outputs go to `analysis/output/` (gitignored). Do not claim the decoupling is
"for performance" in the paper unless you benchmarked it; the defensible reasons
are statistical tooling, plotting, and a clean reproducible interface.
