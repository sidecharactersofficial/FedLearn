# Reviewer Guide

This artifact accompanies the paper:
**"Who Saw It First: Zero-Day Propagation and Attribution Leakage in Federated Intrusion Detection"** (*IEEE Symposium on Security and Privacy*).

Reviewers do not need to read the repository linearly. This guide provides concise, structured pathways tailored to different evaluation budgets.

---

## Artifact Navigation Matrix

| If you are reviewing... | Start here |
| :--- | :--- |
| **Claim-to-evidence mapping** | `CLAIM_MAP.md` |
| **Reviewer evaluation checklist** | `REVIEW_CHECKLIST.md` |
| **Fast verification (< 2 mins)** | `VERIFY.md` |
| **Full experiment reproduction** | `REPRODUCE.md` |
| **Reproducibility guarantees (R1–R4)** | `REPRODUCIBILITY_LEVELS.md` |
| **Numerical discrepancy report** | `REPRODUCIBILITY_DISCREPANCY_REPORT.md` |
| **Expected outputs & formats** | `EXPECTED_OUTPUTS.md` |
| **Known limitations & scope** | `LIMITATIONS.md` |
| **Dataset links & SHA-256 anchors** | `dataset_links.md` |
| **Threat model & observation views** | `doc/THREAT_MODEL.md` |
| **Theoretical inventory & Lean 4 proofs**| `doc/THEOREMS.md`, `leanproofs/` |
| **Open science & experiment manifests**| `doc/OPEN_SCIENCE.md`, `experiment_manifests/` |
| **Hardware & container specs** | `environment/` (`Dockerfile`, `hardware.md`) |
| **Citation & license** | `CITATION_TO_ARTIFACT.md`, `CITATION.cff`, `LICENSE` |

---

## Suggested Review Pathways

### Pathway 1: 15-Minute Scientific Sanity Check
1. **Overview & Key Results:** Read `README.md` to review the headline results (Server attribution up to 96.4%, Peer SecAgg up to 61.4%, Onset Timing MAE 0.61 rounds, Client DP Trade-off $\tau_{0.80} \to \infty$).
2. **Claim Map:** Inspect `CLAIM_MAP.md` to see how each contribution links directly to archived data and generating scripts.
3. **One-Command Smoke Test:**
   ```bash
   make smoke
   ```
   Validates dependencies, dataset hashes (4/4), checkpoint hashes (30/30), traceability, and unit tests in under 60 seconds.
4. **Machine-Checked Formal Proofs:**
   ```bash
   make verify-proofs
   ```
   Verifies all 9 Lean 4 proofs and runs the 9-test numerical oracle.

---

### Pathway 2: 30-Minute Methodology & Attack Review
1. **Threat Model:** Review `doc/THREAT_MODEL.md` to inspect the 5 observation views ($V_{\text{server}}, V_{\text{peer}}, V_{\text{secagg}}, V_{\text{dp}}, V_{\text{quorum}}$).
2. **Theoretical Rigor:** Review `doc/THEOREMS.md` and `leanproofs/MATH_AUDIT_REPORT.md` for the proof sketches of Theorems 1–3, Lemmas 1–2, and Propositions 1–3.
3. **Attack Implementation:** Inspect `attack/feature_extractor.py` and `attack/meta_classifier.py` to examine how shadow meta-classifiers exploit gradient row-space containment (Lemma 2) and de-mixing algebra (Proposition 1).
4. **Defense Suite:** Inspect `worker/src/fedids_worker/defenses/` to examine Secure Aggregation, Client DP, Delayed Buffering, and Quorum Escrow.
5. **Numerical Consistency:** Run `python3 verification/compare_results.py results/metrics/table3_results.csv runs/table3_results.csv` to confirm exact alignment.

---

### Pathway 3: 2-Hour Empirical Reproduction Review
1. Complete Pathway 1 and Pathway 2.
2. Follow `REPRODUCE.md` to execute:
   - `make reproduce-attacks` (Phase 3: Table 3 shadow-federation attribution)
   - `make reproduce-defenses` (Phase 4: Table 4 / Figure 3 defense Pareto frontier)
   - `make reproduce-robustness` (Phase 5: Table 5 operational stress tests)
   - `make reproduce-crossdataset` (Phase 6: Table 6 / Figure 4 50-round multi-benchmark sweeps)
3. Regenerate all publication figures via `python3 plots/generate_paper_plots.py` and inspect `results/figures/`.
