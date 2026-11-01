# Fast Verification Guide

Fast verification of the FedLearn artifact **without** re-running full multi-day federated sweeps.
Verification confirms that the shipped files, code, datasets, and proofs support every claim of the paper.
Full regeneration from scratch is covered in `REPRODUCE.md`.

---

## Prerequisites

```bash
# Clone/unpack repository and enter directory
cd who-saw-it-first-artifact

# Ensure Python 3.11+ is active
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e worker --no-deps
```

---

## Step 1: Verify Environment & Toolchain

```bash
make verify-env
# or
python3 scripts/verify_environment.py
```
**Expected Output:** `verify_env: PASS (Python 3.x, all 12 dependencies satisfied)`

---

## Step 2: Verify Processed Dataset Integrity

```bash
make verify-datasets
# or
python3 verification/verify_datasets.py
# or
sha256sum -c manifest/dataset_sha256.txt
```
**Expected Output:** `verify_datasets: PASS (4/4 datasets verified)`

---

## Step 3: Verify Artifact & Checkpoint Integrity

```bash
make verify-manifest
# or
python3 verification/verify_manifest.py
```
**Expected Output:** `verify_manifest: PASS (30/30 checkpoints verified)`

---

## Step 4: Machine-Check Formal Lean 4 Proofs & Math Audit

```bash
make verify-proofs
# or
cd leanproofs && lake build && .lake/build/bin/fedlearn_proofs && python3 verify_math.py && cd ..
```
**Expected Output:**
- `Status: ALL 9 FORMAL PROOFS MACHINE-CHECKED AND SOUND (0 sorrys, 0 axioms)`
- `ALL 9 THEORETICAL RESULTS MATHEMATICALLY AUDITED & VERIFIED!`

---

## Step 5: Run Automated Unit Tests

```bash
make test
# or
python3 -m pytest worker/tests/ -q
```
**Expected Output:** `14 passed in < 15s`

---

## Step 6: Verify Result Traceability

```bash
make traceability
# or
python3 scripts/check_traceability.py
```
**Expected Output:** `traceability: PASS (All 18 records verified)`

---

## One-Command Fast Smoke Check (< 1 minute)

```bash
make smoke
```
This runs `verify-env`, `verify-datasets`, `verify-manifest`, `traceability`, and `test` in a single pass.
