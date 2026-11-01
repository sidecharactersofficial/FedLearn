# ADR-0003: No notebooks; Python scripts only

- **Status:** Accepted
- **Date:** 2026-10-26

## Context
Exploratory work in Jupyter notebooks drifts untracked: notebook state is not
reproducible from disk, outputs leak into version control, and every analysis
ends up re-implemented as a script anyway. The paper deadline (Euro S&P 2027,
2 Dec 2026 submission) leaves no room for duplicated analysis layers.

## Decision
All data processing, analysis, and test orchestration is done via Python
scripts (R handles statistics/plots through `analysis/`). The `notebooks/`
directory is removed from the repo. EDA lives in short, numbered scripts
(`scripts/`), and anything that must appear in the paper is produced by a
committed script, never by interactive cell state.

## Consequences
- Lighter repo; every analysis step is diffable, reviewable, and CI-runnable.
- No "restart-and-run-all" produce-the-figure affordance; each script must be
  self-contained with explicit inputs/outputs.
- If genuinely needed later (e.g. debugging a training loss visually), a
  notebook may be added temporarily and never shipped with the artifact.

## Alternatives considered
- Keep `notebooks/01_data_exploration.ipynb` from the skeleton: lost — it
  contradicts the working rule and adds an unreproducible path before any real
  dataset work exists.

## Revisit when
A task cannot be reasonably performed in a script (this is expected to be rare
and, per the decision, never committed as canonical methodology).
