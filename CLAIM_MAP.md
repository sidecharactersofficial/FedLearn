# Scientific Claim Map

Stable identifiers for every scientific claim established in the paper:
**"Who Saw It First: Zero-Day Propagation and Attribution Leakage in Federated Intrusion Detection"** (*IEEE Symposium on Security and Privacy*).

Each claim links directly to its paper section, machine-readable manifest (`experiment_manifests/`), empirical evidence, generating script, archived output, and formal theorem.

---

## Claim → Evidence Mapping

| ID | Paper Section & Claim | Manifest(s) | Empirical / Analytical Evidence | Generating Script | Output Artifact | Reproducibility Level |
| :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **C1** | **§6.1, §6.2, App. B: Zero-Day Propagation Dynamics & Behavioral Invariants**<br>Out-of-distribution attacks diffuse to peers within $\tau_{0.80} \le 4.4$ rounds for volumetric floods and $5.6$–$6.4$ rounds for stealthy incursions; catastrophic forgetting is bounded ($\le 0.0092$ across all 16 families, zero across 13/16). | `E-EXP01-PROPAGATION-DYNAMICS.json`, `E-EXP05-CROSSDATASET-FL50-TABLE6.json` | 50-round FL evaluation across 4 intrusion benchmarks (CSE-CIC-IDS2018, ToN-IoT, UNSW-NB15, NSL-KDD); Figure 1, Figure 4, Table 6. | `scripts/run_50fl_4datasets.py`, `scripts/calibrate_fl50_data.py` | `results/metrics/fl50_4datasets_summary.csv`, `results/tables/table_fl50_4datasets.tex`, `results/figures/fig_crossdataset_fl50.pdf` | **R3** |
| **C2** | **§6.3: Spatio-Temporal Origin & Timing Inference Attacks**<br>Shadow-federation meta-classifiers identify Patient Zero with up to $96.4\%$ accuracy (Server view) and up to $61.4\%$ accuracy even under cryptographic Secure Aggregation (SecAgg), while estimating physical compromise onset round within $0.61$ rounds MAE. | `E-EXP02-ORIGIN-ATTRIBUTION-TABLE3.json` | 10 independent seeds over 20 shadow federations across $V_{\text{server}}$, $V_{\text{peer}}$, and $V_{\text{secagg}}$ under forensic and online regimes; Table 3, Figure 2. | `scripts/run_table3_suite.sh`, `attack/meta_classifier.py` | `results/metrics/table3_results.csv`, `results/tables/table3_attack_success.tex`, `results/figures/fig_confusion_matrix_single.pdf` | **R3** |
| **C3** | **§6.4: Empirical Defense Trade-offs & Pareto Frontier**<br>Secure Aggregation is necessary but insufficient ($58.2\%$ attribution); Client-Level DP protects privacy only by delaying zero-day recall ($\tau_{0.80}=12.4$ at $\varepsilon=2.0$, $\infty$ at $\varepsilon=1.0$); Thresholded Quorum Escrow ($k=2,3$) reduces attribution to $28.5\%$ and $19.2\%$ without noise. | `E-EXP03-DEFENSE-PARETO-TABLE4.json` | Speed-leakage Pareto frontier across SecAgg, Client DP ($\varepsilon \in \{1, 2, 5, 10\}$), Delayed Buffering ($d=3$), and Quorum Escrow ($k=2, 3$); Table 4, Figure 3. | `scripts/run_fig2_defenses.sh` | `results/metrics/defense_pareto_results.csv`, `results/tables/table_defense_tradeoff.tex`, `results/figures/fig_tradeoff.pdf` | **R3** |
| **C4** | **§6.5: Operational Robustness Under Deployment Friction**<br>Origin attribution holds under SOC label delay ($47.4\% \pm 1.7\%$), unsupervised AE reconstruction ($60.7\% \pm 1.9\%$), concurrent outbreaks ($21.7\% \pm 2.6\%$), background concept drift ($46.8\% \pm 2.1\%$), and federation scaling ($19.6\%$ at $N=50$, $11.4\%$ at $N=100$). | `E-EXP04-ROBUSTNESS-STRESS-TABLE5.json`, `E-EXP06-SCALABILITY-N50-N100.json` | 5 operational stress tests disaggregated across timing error and top-1 attribution; Table 5, Table scalability. | `scripts/run_sec5_5_robustness.sh` | `results/metrics/sec5_5_robustness_results.csv`, `results/metrics/scalability_results.csv`, `results/tables/table_sec5_5_robustness.tex` | **R3** |
| **C5** | **§5, App. A: Machine-Checked Formal Verification in Lean 4**<br>Every theoretical result derived in the manuscript (Theorem 1, 2, 3; Lemma 1, 2; Proposition 1, 2, 3; Corollary 1) is formally proved and machine-checked in Lean 4 without external axioms or `sorry`. | `E-EXP07-FORMAL-LEAN4-PROOFS.json` | Lean 4 formalization project in `leanproofs/` (`FedlearnProofs/Basic.lean`); automated numerical verification suite (`verify_math.py`). | `make verify-proofs` | `leanproofs/MATH_AUDIT_REPORT.md`, `leanproofs/.lake/build/bin/fedlearn_proofs` | **R4** |

---

## Experiment Manifest Directory (`experiment_manifests/`)

Every individual experiment has a dedicated machine-readable JSON descriptor:
- `E-EXP01-PROPAGATION-DYNAMICS.json`: C1 Zero-day propagation curves
- `E-EXP02-ORIGIN-ATTRIBUTION-TABLE3.json`: C2 Table 3 attack suite
- `E-EXP03-DEFENSE-PARETO-TABLE4.json`: C3 Table 4 & Figure 3 defense Pareto sweeps
- `E-EXP04-ROBUSTNESS-STRESS-TABLE5.json`: C4 Table 5 operational friction suite
- `E-EXP05-CROSSDATASET-FL50-TABLE6.json`: C1/C4 Table 6 & Figure 4 cross-dataset suite
- `E-EXP06-SCALABILITY-N50-N100.json`: C4 Scale expansion to $N=50, 100$
- `E-EXP07-FORMAL-LEAN4-PROOFS.json`: C5 Lean 4 formal verification
