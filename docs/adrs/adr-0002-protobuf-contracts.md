# ADR-0002: Protocol Buffers for inter-component contracts

- **Status:** Accepted
- **Date:** 2026-10-26

## Context
The Rust orchestrator and Python worker must agree exactly on configs and
results. JSON would leave that agreement implicit and untyped.

## Decision
Define contracts in proto3 under `proto/fedids/v1/` (single source of truth).
Generate Rust (prost) and Python bindings. Large data goes to Parquet files
referenced by path. The worker also flattens `RunConfig` into `meta.parquet`
so R has no protobuf dependency. Sweep specs stay human-authored TOML; they are
an authoring format for the orchestrator, not a contract.

## Consequences
- Typed, versioned contracts shared by both languages; schema changes are explicit.
- Field numbers are never reused; breaking changes bump the package (`fedids.v2`).
- A code generation step (`make proto`); generated code is never edited or committed.

## Alternatives considered
- JSON: simpler to inspect, no type guarantees across languages.

## Revisit when
The contract surface grows enough that gRPC streaming between orchestrator and
workers is worth adopting.
