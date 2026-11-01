# ADR-0001: Rust orchestrates, Python processes, R analyzes

- **Status:** Accepted
- **Date:** 2026-10-26

## Context
The project runs large sweeps of federated simulations (sites, skew, defenses,
seeds), then statistics over the results. The ML ecosystem (Flower, PyTorch)
lives in Python; statistical analysis and plotting are strongest in R.

## Decision
- **Rust** (`orchestrator/`): configs, sweeps, run supervision, result collection.
- **Python** (`worker/`): data processing, federation simulation, attacks, defenses.
- **R** (`analysis/`): statistics, plots, paper tables, decoupled from the rest.

## Consequences
- Each root directory is one deployable artifact with its own lockfile.
- Three toolchains to pin and document for artifact reviewers (Docker, one entry command).
- R can be re-run without re-running experiments.

## Alternatives considered
- Python only: simpler, but sweeps and supervision are less robust.
- Analysis in Python: fewer languages, weaker statistics tooling for this use.

## Revisit when
The orchestration needs outgrow a subprocess model (e.g. remote workers), or the
three-toolchain cost outweighs the benefits for artifact reproducibility.
