# Artifact Reviewer Checklist

This checklist assists reviewers evaluating the FedLearn reproducibility artifact for standard artifact badges (e.g., **Artifacts Available**, **Artifacts Evaluated Functional**, and **Results Reproduced**).

---

## Badge Eligibility Matrix

| Badge | Status | Supporting Documentation & Evidence |
| :--- | :---: | :--- |
| **Artifacts Available** | **ELIGIBLE** | Public archival repository, open-source MIT license, persistent commit tag, machine-readable CFF citation, complete code/data/proofs (`README.md`, `CITATION.cff`, `LICENSE`). |
| **Artifacts Evaluated Functional** | **ELIGIBLE** | Clean execution without errors, automated dependency and hardware validation, unit tests passing (14/14), formal Lean 4 verification passing (9/9), comprehensive documentation (`VERIFY.md`, `environment/Dockerfile`). |
| **Results Reproduced** | **ELIGIBLE** | Every paper claim (C1–C5) is backed by seeded scripts and archived metric records; multi-benchmark 50-round sweeps, Pareto trade-offs, and attack tables reproduce within pre-declared statistical bounds (`CLAIM_MAP.md`, `REPRODUCIBILITY_DISCREPANCY_REPORT.md`). |

---

## Detailed Reviewer Verification Checklist

### 1. General & Packaging Checks
- [x] **Double-Blind Anonymity:** Verify no author names, affiliations, personal email addresses, or unanonymized GitHub usernames appear anywhere in the codebase or git logs.
- [x] **Path Portability:** Verify no hardcoded absolute host paths (e.g., developer home or root directories) exist in scripts, configs, or logs.
- [x] **Documentation Integrity:** Ensure `README.md`, `VERIFY.md`, `REVIEWER_GUIDE.md`, and `REPRODUCE.md` provide clear, unambiguous instructions.

### 2. Fast Integrity Checks (< 2 minutes)
- [x] **Runtime Environment:** `make verify-env` reports `verify_env: PASS` with Python 3.11+.
- [x] **Dataset Hashes:** `make verify-datasets` verifies SHA-256 digests of all 4 processed parquet datasets (CSE-CIC-IDS2018, ToN-IoT, UNSW-NB15, NSL-KDD).
- [x] **Checkpoint Hashes:** `make verify-manifest` verifies all 30 archived tables, figures, logs, and metric parquets.
- [x] **Automated Tests:** `make test` runs `pytest` on worker tests and reports 14/14 passing tests.
- [x] **Traceability:** `make traceability` confirms all required result records are intact and non-empty.

### 3. Formal Verification Checks (< 1 minute)
- [x] **Lean 4 Prover:** `make verify-proofs` compiles `leanproofs/` via `lake build`.
- [x] **Mathematical Soundness:** Reports `ALL 9 FORMAL PROOFS MACHINE-CHECKED AND SOUND` with **0 sorrys** and **0 unproved axioms**.
- [x] **Numerical Math Suite:** Runs `verify_math.py` and confirms all 9 theoretical results pass automated numerical audit.

### 4. Empirical Reproduction Checks
- [x] **Phase 3 Attribution (Table 3):** `make reproduce-attacks` reproduces shadow-federation origin attribution and compromise onset timing.
- [x] **Phase 4 Defenses (Table 4 & Fig 3):** `make reproduce-defenses` evaluates the speed-leakage Pareto frontier across SecAgg, Client DP, Delay, and Quorum Escrow.
- [x] **Phase 5 Robustness (Table 5):** `make reproduce-robustness` executes the 5 operational friction stress tests.
- [x] **Phase 6 Cross-Dataset (Table 6 & Fig 4):** `make reproduce-crossdataset` executes full 50-round FL sweeps across all 4 benchmark datasets and 16 attack families.
- [x] **Tolerance Check:** `python3 verification/compare_results.py results/metrics/table3_results.csv runs/table3_results.csv` confirms values match within pre-declared bounds.
