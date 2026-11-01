# Formal Threat Model & Adversary Capabilities

This document formalizes the threat model, adversary goals, observation views, and operational trust assumptions evaluated in:
**"Who Saw It First: Zero-Day Propagation and Attribution Leakage in Federated Intrusion Detection"** (*IEEE Symposium on Security and Privacy*).

---

## 1. System Architecture & Federated Setting

We consider a cross-silo federated learning consortium of $N$ sovereign institutions (e.g., regional hospital health systems, commercial banking networks, critical utility operators, or Information Sharing and Analysis Centers [ISACs]).
- **Local Network Detectors:** Each site $i \in \{1, \dots, N\}$ continuously monitors ingress/egress network flows and trains a local deep neural Network Intrusion Detection System (NIDS) parametrized by weights $w_i^{(t)}$.
- **Non-IID Traffic Skew:** Participating institutions experience distinct, heterogeneous baseline traffic profiles modeled via Dirichlet distribution $\mathbf{p}_k \sim \mathrm{Dir}(\alpha \cdot \mathbf{1}_K)$ with concentration parameter $\alpha \in \{0.1, 0.5, 1.0, 10.0\}$.
- **Zero-Day Incursion:** At physical outbreak round $t_0$, a novel out-of-distribution (OOD) attack family $f^\star$ strikes a single origin site $o \in \{1, \dots, N\}$. The origin site detects anomalous flows via automated security triage (or autoencoder reconstruction) and incorporates positive labels into its local SGD training.

---

## 2. Adversary Objectives

The adversary's goal is passive inference without compromising model integrity or disrupting protocol execution:
1. **Origin Site Attribution ($\hat{o}$):** Identify which specific member institution was the initial Patient Zero that observed and responded to attack family $f^\star$.
2. **Onset Timing Localization ($\hat{t}_0$):** Pinpoint the exact federated communication round $t_0$ during which the compromise first manifested in the physical network.
3. **Forensic vs. Online Inference:**
   - *Forensic Regime:* The adversary has access to isolated post-incident attack signatures or samples from family $f^\star$.
   - *Online / Zero-Day Regime:* The adversary has no prior exposure to family $f^\star$ and must infer attribution and timing in real time.

---

## 3. Adversary Observation Views

We analyze five rigorous, progressively constrained adversary observation views:

| View | Adversary Identity | Mathematical Observation $\mathcal{V}$ | Defense In Place |
| :--- | :--- | :--- | :--- |
| $\mathcal{V}_{\text{server}}$ | Curious Central Server | $\{\Delta w_i^{(t)}\}_{i=1, t=1}^{N, T}$ | Unprotected FedAvg (plain individual updates) |
| $\mathcal{V}_{\text{peer}}$ | Curious Consortium Peer $p$ | $\{\Delta W^{(t)}\}_{t=1}^T \cup \{\Delta w_p^{(t)}\}_{t=1}^T$ | Global model updates + Peer's own local update |
| $\mathcal{V}_{\text{secagg}}$ | Peer or SecAgg Server | $\{\Delta W^{(t)}\}_{t=1}^T = \left\{\frac{1}{N}\sum_{i=1}^N \Delta w_i^{(t)}\right\}_{t=1}^T$ | Cryptographic Secure Aggregation (SecAgg) |
| $\mathcal{V}_{\text{dp}}$ | Consortium Observer | $\{\Delta W_{\text{dp}}^{(t)}\}_{t=1}^T = \left\{\frac{1}{N}\sum_{i=1}^N \Delta \bar{w}_i^{(t)} + \mathcal{N}(0, \sigma^2 I)\right\}$ | Client-Level DP-FedAvg ($\varepsilon \in \{1, 2, 5, 10\}$) |
| $\mathcal{V}_{\text{quorum}}$ | Quorum Escrow Peer | Escrowed updates released only when $\|K\| \ge k$ | Thresholded $k$-of-$N$ Quorum Escrow ($k \in \{2, 3\}$) |

---

## 4. Trust Boundaries & Behavioral Constraints

1. **Protocol Adherence (Semi-Honest / Honest-but-Curious):** All federation participants, including the adversary, faithfully execute protocol steps (local gradient computation, parameter broadcasting, aggregation). The adversary does not inject poisoned weights, backdoors, or sybil identities.
2. **Data Locality:** The adversary cannot access private raw packet captures, netflow records, or local training batches from any peer site.
3. **Cryptographic Masking:** Under Secure Aggregation ($\mathcal{V}_{\text{secagg}}$), individual client vectors are cryptographically unrecoverable; the adversary only observes the exact vector sum $\sum_{i=1}^N \Delta w_i^{(t)}$.
