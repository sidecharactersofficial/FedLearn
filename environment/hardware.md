# Hardware and Environment Specifications

## Reproduction Environment

The archived results under `results/` and the empirical evaluations reported in the paper were produced from the following baseline environment.

| Component | Specification |
| :--- | :--- |
| **Operating System** | Linux (Ubuntu / Debian x86_64), kernel 6.x |
| **Python Interpreter** | CPython 3.11+ (tested on CPython 3.12 and 3.14.6) |
| **Rust Toolchain** | `rustc` 1.75+ (used for the cross-silo sweep orchestrator) |
| **Lean 4 Prover** | Lean 4 toolchain `leanprover/lean4:v4.15.0` (managed via `elan`) |
| **Statistical Engine** | R 4.3+ (optional, for standalone `analysis/run_analysis.R` plotting) |
| **Host Architecture** | x86_64, 8+ logical CPU cores |
| **Host Memory (RAM)** | 8 GB minimum, 16 GB recommended |
| **GPU Acceleration** | Optional; all FL simulations execute deterministically on CPU |

> **Note on Hardware Invariance:** The analytical results, formal proofs, and spatio-temporal leakage dynamics do not depend on proprietary hardware acceleration or specific GPU models. Model parameter updates and shadow XGBoost meta-classifiers run natively on commodity multi-core CPUs.

## Software Dependencies

Exact package versions are declared in:
- `requirements.txt`: Direct Python dependencies (the canonical manifest).
- `environment/requirements.lock`: Full transitive dependency closure.
- `orchestrator/Cargo.lock`: Pinned Rust crates for the runner orchestrator.
- `leanproofs/lakefile.toml` & `leanproofs/lean-toolchain`: Pinned Lean 4 toolchain.

### Key Python Dependencies
- `torch>=2.2.0` (deep neural detector architectures)
- `flwr[simulation]>=1.8.0` (Flower federated learning framework)
- `xgboost>=2.0.0` (gradient boosted shadow meta-classifiers)
- `scikit-learn>=1.4.0` (Huber regressors and ROC/AUC metrics)
- `pyarrow>=15.0.0` & `pandas>=2.1.0` (high-performance columnar telemetry IO)
- `protobuf>=5.0.0` (typed cross-language contracts)
- `matplotlib>=3.8.0` (publication figure rendering)
- `pytest>=8.0.0` (fast automated unit test suite)

## Containerized Execution

A reproducible container definition is provided in `environment/Dockerfile`:
```bash
docker build -f environment/Dockerfile -t fedlearn-artifact .
docker run --rm -it fedlearn-artifact make smoke
```
