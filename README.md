# Who Saw It First: Zero-Day Propagation and Attribution Leakage in Federated Intrusion Detection

**Reproducibility Artifact for the IEEE Symposium on Security and Privacy (S&P)**

Everything required to verify and reproduce every theorem, table, and figure of the paper from the shipped preprocessed benchmark tensors, simulation scripts, machine-checked Lean 4 formal proofs, and archived result records.

---

## Artifact Navigation

| If you are reviewing... | Start here | Description |
| :--- | :--- | :--- |
| **Claim-to-evidence mapping** | `CLAIM_MAP.md` | Stable claim IDs (C1–C5) $\to$ manifests, tables, and evidence |
| **Reviewer guide & evaluation paths** | `REVIEWER_GUIDE.md` | 15-min, 30-min, and 2-hour structured evaluation workflows |
| **Reviewer badge checklist** | `REVIEW_CHECKLIST.md` | Bounded checklist for Artifacts Available, Functional, Reproduced |
| **Fast verification (< 2 mins)** | `VERIFY.md` | Step-by-step verification commands without long sweeps |
| **Full reproduction** | `REPRODUCE.md` | End-to-end instructions to re-execute sweeps and attacks |
| **Reproducibility guarantees (R1–R4)**| `REPRODUCIBILITY_LEVELS.md` | Taxonomy of reproducibility tiers across all components |
| **Numerical discrepancy audit** | `REPRODUCIBILITY_DISCREPANCY_REPORT.md` | Numerical diff ($\Delta$) comparing paper vs archived metrics |
| **Expected outputs & schemas** | `EXPECTED_OUTPUTS.md` | Column schemas, shapes, and target values per experiment |
| **Known limitations & scope** | `LIMITATIONS.md` | Realism considerations, adversary scope, and hardware limits |
| **Methodological history** | `PROVENANCE.md` | Research timeline from observation to formal proofs |
| **Experiment manifests** | `experiment_manifests/` | Machine-readable JSON specifications per experiment |
| **Theorems & formal mapping** | `doc/THEOREMS.md` | Theorem statements, proof sketches, and Lean 4 identifiers |
| **Formal Lean 4 proofs & audit** | `leanproofs/` | Self-contained formalization (0 sorrys, 0 axioms) + math suite |
| **Threat model & observation views** | `doc/THREAT_MODEL.md` | Formal capabilities across $V_{\text{server}}, V_{\text{peer}}, V_{\text{secagg}}, V_{\text{dp}}, V_{\text{quorum}}$ |
| **Dataset links & SHA-256 anchors** | `dataset_links.md` | Sources and cryptographic anchors for all 4 intrusion datasets |
| **Checkpoint & dataset integrity** | `manifest/`, `verification/` | Python verification scripts and pinned SHA-256 manifests |
| **Hardware, Docker & environment** | `environment/` | Dockerfile, hardware specifications, and locked dependencies |
| **Citation & license** | `CITATION_TO_ARTIFACT.md`, `LICENSE` | Anonymized citation formats and MIT license |

**Reproducibility Status:**
- All 9 formal mathematical results (Theorems 1–3, Lemmas 1–2, Propositions 1–3, Corollary 1) are formally machine-checked and verified in Lean 4 without external dependencies or unproved axioms (**Level R4**).
- All empirical evaluations (Table 3 attacks, Table 4 Pareto defenses, Table 5 robustness stress tests, Table 6 50-round cross-dataset sweeps) are fully machine-traceable via seeded scripts and archived metric records (**Level R3**). Re-runs reproduce paper metrics within pre-declared statistical tolerance bounds with **zero discrepancies** ($\Delta = 0.000$; see `REPRODUCIBILITY_DISCREPANCY_REPORT.md`).

---

## What This Artifact Is

This repository contains the complete empirical and formal verification suite for **Who Saw It First**. It investigates the fundamental tension between out-of-distribution (OOD) zero-day propagation speed and institutional privacy leakage in cross-silo federated network intrusion detection:

- **The Promise:** When an origin institution observes an emerging zero-day attack family (e.g., ransomware infiltration or volumetric DoS), collaborative model updates rapidly immunize peer detectors before lateral spread across the sector ($\tau_{0.80} \le 4.4$ rounds).
- **The Vulnerability:** Because participating institutions have heterogeneous (non-IID) background traffic distributions, local SGD updates entangle the novel attack features with the origin site's characteristic background subspace (Lemma 2).
- **The Finding:** A curious consortium peer or coordinator observing shared parameter updates can infer **which** organization detected the threat first (origin attribution) and **when** the compromise occurred (onset timing inference) — even when individual updates are cryptographically hidden behind Secure Aggregation (SecAgg).

---

## Key Empirical Findings

```
Origin Attribution Accuracy (10 Sites, Random Baseline = 10.0%):
  Unprotected FedAvg (Server View, Forensic) : 96.4%  [Timing MAE: 0.61 rds]
  Unprotected FedAvg (Peer View, Forensic)   : 89.2%  [Timing MAE: 0.84 rds]
  Secure Aggregation (Peer View, Forensic)   : 61.4%  [Timing MAE: 1.18 rds]
  Secure Aggregation (Peer View, Online)     : 58.2%  [Timing MAE: 1.65 rds]

Defense Pareto Frontier (Speed vs. Privacy Leakage):
  Secure Aggregation (alone)                 : tau_0.80 = 4.5 rds  | Top-1 Acc = 58.2%
  Client-Level DP (eps = 2.0)                : tau_0.80 = 12.4 rds | Top-1 Acc = 16.5%
  Client-Level DP (eps = 1.0)                : tau_0.80 = inf      | Top-1 Acc = 11.2% (stalls zero-day defense)
  Thresholded Quorum Escrow (k = 2)          : tau_0.80 = 6.2 rds  | Top-1 Acc = 28.5%
  Thresholded Quorum Escrow (k = 3)          : tau_0.80 = 8.4 rds  | Top-1 Acc = 19.2% (Bayes bound <= 33.3%)
```

---

## Fast Verification (< 2 Minutes)

Reviewers can verify the entire artifact in under 2 minutes:

```bash
# 1. Activate environment
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e worker --no-deps

# 2. Run fast smoke suite (environment, datasets, checkpoints, traceability, unit tests)
make smoke

# 3. Machine-check formal Lean 4 proofs and numerical math audit
make verify-proofs
```

---

## Full Empirical Reproduction

To reproduce all experiments, figures, and tables from scratch:

```bash
# Phase 3: Table 3 Shadow-Federation Attribution & Timing Attacks
make reproduce-attacks

# Phase 4: Table 4 & Figure 3 Defense Pareto Sweeps
make reproduce-defenses

# Phase 5: Table 5 Operational Friction Stress Tests
make reproduce-robustness

# Phase 6: Table 6 & Figure 4 Extended 50-Round Cross-Dataset FL Sweeps
make reproduce-crossdataset

# Render all publication graphics (PDF & PNG)
make reproduce-plots
```
Or execute all targets in a single run: `make reproduce-all`.

---

## Machine-Checked Formal Verification in Lean 4

Every theoretical result in the manuscript is formalized in `leanproofs/`:
```bash
cd leanproofs
lake build
./.lake/build/bin/fedlearn_proofs
python3 verify_math.py
```
Outputs:
```
=================================================================
  FedLearn: Machine-Checked Formal Verification in Lean 4
=================================================================
All 9 core theorems, propositions, lemmas, and corollaries verified:
  [x] Proposition 1: Peer De-Mixing Exact Algebraic Recovery
  [x] Proposition 2: Information Monotonicity & View Ordering
  [x] Lemma 1: Per-Round Model Discrepancy Dilution Recurrence
  [x] Theorem 1: Propagation Delay Lower Bound & Geometric Recurrence
  [x] Lemma 2: Linear Layer Gradient Outer Product Row Span Containment
  [x] Proposition 3: Exchangeable Client IID Limit & Chance Attribution
  [x] Corollary 1: Subspace Coherence Margin & Attribution SNR
  [x] Theorem 2: Client-Level DP Origin Attribution Bound
  [x] Theorem 3: Symmetric k-of-N Quorum Release Bayes Bound
=================================================================
Status: ALL 9 FORMAL PROOFS MACHINE-CHECKED AND SOUND (0 sorrys, 0 axioms)
=================================================================
```

---

## Benchmarks & Datasets

Evaluations span four established network intrusion detection benchmarks:
1. **CSE-CIC-IDS2018:** 66-feature enterprise flow benchmark (`cleaned_cic2018.parquet`, 100,000 flows).
2. **ToN-IoT:** 41-feature heterogeneous IoT/IIoT telemetry (`cleaned_ton_iot.parquet`, 60,000 flows).
3. **UNSW-NB15:** 39-feature mixed synthetic and realistic network captures (`cleaned_unsw_nb15.parquet`, 82,332 flows).
4. **NSL-KDD:** 38-feature classic intrusion detection benchmark (`cleaned_nsl_kdd.parquet`, 125,973 flows).

All tensors are preprocessed and pinned by authoritative SHA-256 checksums in `manifest/dataset_sha256.txt`. Verify anytime with `make verify-datasets`.

---

## Double-Blind Anonymity Statement

In compliance with double-blind review policies, all identifying metadata (author names, institutional affiliations, contact emails, commit authors, and internal file paths) have been scrubbed from this repository and associated artifacts.
