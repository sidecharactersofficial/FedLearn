# Changelog

All notable changes to this project are documented here.

## [Unreleased]

### Added
- ADR-0003 (no notebooks; Python scripts only); `notebooks/` removed.
- Fixed sh-sourceability of `.env.example` (smoke path sourced it with errors).

### Fixed
- Regenerated Python protobuf bindings pinned to the runtime (`protobuf` 6.x)
  instead of the shipped mismatched gencode 7.x.

### Added
- Project skeleton: Rust orchestrator, Python worker, R analysis.
- Protocol Buffers contracts (`fedids.v1`): `RunConfig`, `RunResult`, `RoundMetric`, `Observation`.
- Fail-fast environment and config validation in the orchestrator and worker.
- ADR-0001 (language split) and ADR-0002 (protobuf contracts).
- Euro S&P 2027 paper template in `paper/`.
