# Reproducibility Discrepancy & Verification Audit Report

This report documents a comprehensive numerical comparison between the numbers reported in the paper **"Who Saw It First: Zero-Day Propagation and Attribution Leakage in Federated Intrusion Detection"** and the metrics archived in `results/metrics/`.

---

## 1. Table 3: Origin Attribution and Timing Estimation Audit (§6.3)

| View | Regime | Paper Top-1 Acc (%) | Archived Top-1 Acc (%) | $\Delta$ | Paper Timing MAE (Rds) | Archived Timing MAE (Rds) | $\Delta$ | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Server ($V_{\text{server}}$)** | Forensic | 96.4% | 96.4% | 0.0% | 0.61 | 0.61 | 0.00 | **EXACT MATCH** |
| **Server ($V_{\text{server}}$)** | Online (Zero-Day) | 84.1% | 84.1% | 0.0% | 1.15 | 1.15 | 0.00 | **EXACT MATCH** |
| **Peer ($V_{\text{peer}}$)** | Forensic | 89.2% | 89.2% | 0.0% | 0.84 | 0.84 | 0.00 | **EXACT MATCH** |
| **Peer ($V_{\text{peer}}$)** | Online (Zero-Day) | 71.5% | 71.5% | 0.0% | 1.42 | 1.42 | 0.00 | **EXACT MATCH** |
| **SecAgg ($V_{\text{secagg}}$)**| Forensic | 61.4% | 61.4% | 0.0% | 1.18 | 1.18 | 0.00 | **EXACT MATCH** |
| **SecAgg ($V_{\text{secagg}}$)**| Online (Zero-Day) | 58.2% | 58.2% | 0.0% | 1.65 | 1.65 | 0.00 | **EXACT MATCH** |
| **Random Baseline** | Analytic | 10.0% | 10.0% | 0.0% | 7.08 | 7.08 | 0.00 | **EXACT MATCH** |

---

## 2. Table 4: Defense Trade-Offs & Pareto Frontier Audit (§6.4)

| Defense Mechanism | Parameter | Paper $\tau_{0.80}$ (Rds) | Archived $\tau_{0.80}$ (Rds) | $\Delta$ | Paper Origin Top-1 (%) | Archived Origin Top-1 (%) | $\Delta$ | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **None (Unprotected FedAvg)** | — | 4.5 | 4.5 | 0.0 | 96.4% | 96.4% | 0.0% | **EXACT MATCH** |
| **Secure Aggregation** | SecAgg | 4.5 | 4.5 | 0.0 | 58.2% | 58.2% | 0.0% | **EXACT MATCH** |
| **Client DP + SecAgg** | $\varepsilon = 10.0$ | 5.2 | 5.2 | 0.0 | 44.8% | 44.8% | 0.0% | **EXACT MATCH** |
| **Client DP + SecAgg** | $\varepsilon = 5.0$ | 7.1 | 7.1 | 0.0 | 31.2% | 31.2% | 0.0% | **EXACT MATCH** |
| **Client DP + SecAgg** | $\varepsilon = 2.0$ | 12.4 | 12.4 | 0.0 | 16.5% | 16.5% | 0.0% | **EXACT MATCH** |
| **Client DP + SecAgg** | $\varepsilon = 1.0$ | $\infty$ (>50) | $\infty$ | 0.0 | 11.2% | 11.2% | 0.0% | **EXACT MATCH** |
| **Temporal Buffering** | $d = 3$ rounds | 7.5 | 7.5 | 0.0 | 54.6% | 54.6% | 0.0% | **EXACT MATCH** |
| **Thresholded Quorum** | $k = 2$ | 6.2 | 6.2 | 0.0 | 28.5% | 28.5% | 0.0% | **EXACT MATCH** |
| **Thresholded Quorum** | $k = 3$ | 8.4 | 8.4 | 0.0 | 19.2% | 19.2% | 0.0% | **EXACT MATCH** |

---

## 3. Table 5: Operational Friction & Robustness Stress Tests Audit (§6.5)

| Operational Condition | Paper Metric Value | Archived Metric Value | $\Delta$ | Status |
| :--- | :---: | :---: | :---: | :---: |
| **SOC Delay ($\Delta t_{\text{SOC}} = 2$) Peer Top-1** | $47.4\% \pm 1.7\%$ | 47.4% | 0.0% | **EXACT MATCH** |
| **SOC Delay ($\Delta t_{\text{SOC}} = 5$) Peer Top-1** | $39.0\% \pm 2.8\%$ | 39.0% | 0.0% | **EXACT MATCH** |
| **SOC Delay ($\Delta t_{\text{SOC}} = 2$) Timing MAE**| $3.61 \pm 0.38$ | 3.61 | 0.00 | **EXACT MATCH** |
| **SOC Delay ($\Delta t_{\text{SOC}} = 5$) Timing MAE**| $6.21 \pm 0.45$ | 6.21 | 0.00 | **EXACT MATCH** |
| **Unlabeled Autoencoder Peer Top-1** | $60.7\% \pm 1.9\%$ | 60.7% | 0.0% | **EXACT MATCH** |
| **Unlabeled Autoencoder Timing MAE** | $1.23 \pm 0.18$ | 1.23 | 0.00 | **EXACT MATCH** |
| **Concurrent Outbreaks ($m=3$) Peer Top-1** | $21.7\% \pm 2.6\%$ | 21.7% | 0.0% | **EXACT MATCH** |
| **Concurrent Outbreaks ($m=3$) Timing MAE** | $0.22 \pm 0.04$ | 0.22 | 0.00 | **EXACT MATCH** |
| **Background Concept Drift Peer Top-1** | $46.8\% \pm 2.1\%$ | 46.8% | 0.0% | **EXACT MATCH** |
| **Background Concept Drift Timing MAE** | $2.88 \pm 0.61$ | 2.88 | 0.00 | **EXACT MATCH** |
| **Large Federation ($N=50$) Server Top-1** | $88.4\% \pm 2.1\%$ | 88.4% | 0.0% | **EXACT MATCH** |
| **Large Federation ($N=50$) Peer Top-1** | $19.6\% \pm 2.4\%$ | 19.6% | 0.0% | **EXACT MATCH** |
| **Large Federation ($N=100$) Peer Top-1** | $11.4\% \pm 2.1\%$ | 11.4% | 0.0% | **EXACT MATCH** |

---

## 4. Table 6: Cross-Dataset 50-Round FL Evaluation Audit (Appendix B)

Across all 16 held-out zero-day macro-families spanning CSE-CIC-IDS2018, ToN-IoT, UNSW-NB15, and NSL-KDD, the metrics in `results/metrics/fl50_4datasets_summary.csv` match Table 6 in the manuscript to 3 decimal places for $\tau_{0.80}$, peak recall, final recall, $\text{AUPC}_{20}$, and catastrophic forgetting.

**Overall Discrepancy Assessment:** ZERO discrepancies identified ($\Delta = 0.000$ across all primary tables).
