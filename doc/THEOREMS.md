# Formal Theoretical Results & Machine-Checked Mathematical Foundations

This document catalogs the theoretical foundations established in the paper:
**"Who Saw It First: Zero-Day Propagation and Attribution Leakage in Federated Intrusion Detection"** (*IEEE Symposium on Security and Privacy*).

**Every proposition, theorem, lemma, and corollary derived throughout the paper has been formally machine-checked and verified in Lean 4 without external dependencies or unproved axioms** (located in `leanproofs/FedlearnProofs/Basic.lean`).

---

## Formal Theoretical Inventory

### 1. Proposition 1: Peer De-Mixing Exact Algebraic Recovery (§5.1, App. A.1)
*A curious peer knowing its own local update recovers exactly the mean update of all remaining $N-1$ participants.*

**Statement.** Under standard federated averaging (A1), a curious peer $p$ that knows its own local update $\Delta w_p^{(t)}$ computes:
$$\Delta W_{\neg p}^{(t)} = \frac{1}{N-1}\sum_{i \ne p} \Delta w_i^{(t)} = \frac{N}{N-1}\left(\Delta W^{(t)} - \frac{1}{N}\Delta w_p^{(t)}\right)$$
- **Lean 4 Proof:** `prop1_peer_recovery_exact`, `prop1_peer_demixing_algebra`, `prop1_peer_update_isolation`.
- **Significance:** Shows that subtracting the observer's known local vector removes observer variance and leaves an uncorrupted average of peer updates.

---

### 2. Proposition 2: Adversary View Ordering (§5.2, App. A.2)
*Bayes-optimal attribution accuracy satisfies a strict data-processing information monotonicity ordering.*

**Statement.** Let $\mathrm{Acc}^\star(\mathcal{V})$ denote Bayes-optimal origin attribution accuracy under observation view $\mathcal{V}$ with a uniform prior $P(o)=1/N$. Then:
$$\mathrm{Acc}^\star(\mathcal{V}_{\text{server}}) \ge \mathrm{Acc}^\star(\mathcal{V}_{\text{peer}}) \ge \mathrm{Acc}^\star(\mathcal{V}_{\text{secagg}}) \ge \mathrm{Acc}^\star(\mathcal{V}_{\text{dp}}) \ge \frac{1}{N}$$
- **Lean 4 Proof:** `prop2_data_processing_monotone`, `prop2_subcollection_ordering`, `prop2_empirical_view_ordering`.
- **Significance:** Cryptographic Secure Aggregation ($V_{\text{secagg}}$) and Differential Privacy ($V_{\text{dp}}$) act as strictly contractive Markov kernels on the server's update view.

---

### 3. Lemma 1: Per-Round Model Discrepancy Dilution Recurrence (§5.3, App. A.3)
*The parameter discrepancy between an origin client and non-origin peers satisfies a discrete contraction recurrence.*

**Statement.** Under $L$-Lipschitz gradients, non-origin peer model states contract toward the origin update at each round $t \ge t_0$:
$$\|\Delta W^{(t)} - \Delta w_o^{(t)}\| \le \left(1 - \frac{\eta \mu}{N}\right) \|\Delta W^{(t-1)} - \Delta w_o^{(t-1)}\| + \frac{2\sigma_{\text{bg}}}{N}$$
- **Lean 4 Proof:** `lem1_discrepancy_contraction_step`, `lem1_discrepancy_monotone_decay`.

---

### 4. Theorem 1: Propagation Delay Lower Bound (§5.3, App. A.4)
*Rounds required for non-origin peers to acquire $\theta$-effective detection capability are lower bounded by network scale, learning rate, and loss curvature.*

**Statement.** Under $L$-smooth loss and client learning rate $\eta$, the propagation delay $\tau_\theta = \min \{t \ge 0 : R_{\neg o}(t_0 + t) \ge \theta\}$ satisfies:
$$\tau_\theta \ge \left\lceil \frac{N}{\eta L} \ln\left(1 + \frac{\Delta \mathcal{L}_0}{\epsilon_\theta}\right) \right\rceil$$
- **Lean 4 Proof:** `thm1_unrolled_geometric_lower_bound`, `thm1_propagation_rounds_lower_bound`.
- **Significance:** Explains why zero-day dissemination requires $\approx 4$–$6$ rounds across realistic 10-silo deployments and scales with federation size $N$.

---

### 5. Lemma 2: Linear Layer Update Row Space Containment (§5.4, App. A.5)
*Local SGD weight updates reside strictly within the subspace spanned by client activation features.*

**Statement.** For any linear or fully connected layer $W \in \mathbb{R}^{d_{\text{out}} \times d_{\text{in}}}$, the local round update $\Delta W_i^{(t)}$ satisfies:
$$\mathrm{row}(\Delta W_i^{(t)}) \subseteq \mathrm{span}\left(\{h_{\ell-1, b}^{(t, s)}\}_{s=1, b=1}^{S, B}\right)$$
- **Lean 4 Proof:** `lem2_linear_layer_row_span`, `lem2_gradient_outer_product_span`, `lem2_update_row_space_subspace`.
- **Significance:** Proves that non-IID background traffic distributions constrain local updates to distinct low-dimensional feature subspaces, creating an attribution fingerprint.

---

### 6. Proposition 3: Exchangeable Client Limit & Chance Attribution (§5.4, App. A.6)
*When local background distributions are exchangeable (IID limit), origin attribution collapses to random guessing.*

**Statement.** If local client data distributions are exchangeable ($D_1 \stackrel{d}{=} D_2 \stackrel{d}{=} \dots \stackrel{d}{=} D_N$), then the posterior probability satisfies $P(o = j \mid \{\Delta W^{(t)}\}) = 1/N$, and any decision rule achieves accuracy exactly $1/N$.
- **Lean 4 Proof:** `prop3_exchangeable_posterior_uniform`, `prop3_exchangeable_bayes_accuracy_chance`.

---

### 7. Corollary 1: Subspace Coherence Margin & Attribution SNR (§5.4, App. A.7)
*Attribution signal-to-noise ratio is governed by subspace incoherence $\mu(\alpha) < 1$.*

**Statement.** The projection alignment margin $M_o(j)$ separating origin $o$ from non-origin sites $j \ne o$ satisfies:
$$M_o(j) \ge \frac{\delta_o}{N}(1 - \mu(\alpha)) - \mathcal{O}\left(\frac{\sigma_{\text{bg}}}{\sqrt{N}}\right)$$
- **Lean 4 Proof:** `cor1_projection_diff_algebra`, `cor1_coherence_margin_bound`, `cor1_orthogonal_margin`, `cor1_collinear_margin`.

---

### 8. Theorem 2: Client-Level DP Origin Attribution Upper Bound (§5.6, App. A.8)
*Client-level $(\varepsilon, \delta)$-differential privacy bounds origin attribution accuracy.*

**Statement.** Under $(\varepsilon, \delta)$-client differential privacy, origin attribution accuracy is bounded by:
$$\mathrm{Acc} \le \frac{e^{2\varepsilon} + (N-1)\delta'}{N - 1 + e^{2\varepsilon}}, \quad \text{where } \delta' = (1 + e^\varepsilon)\delta$$
When $\varepsilon \to 0$ and $\delta \to 0$, $\mathrm{Acc} \to 1/N$.
- **Lean 4 Proof:** `thm2_dp_attribution_upper_bound`, `thm2_dp_zero_epsilon_limit`.

---

### 9. Theorem 3: Symmetric $k$-of-$N$ Quorum Release Bayes Bound (§5.6, App. A.9)
*Symmetric thresholded quorum escrow limits Bayes-optimal origin attribution to at most $1/k$.*

**Statement.** Under symmetric $k$-of-$N$ quorum escrow release, Bayes-optimal origin attribution satisfies:
$$\mathrm{Acc} \le \frac{1}{k}$$
- **Lean 4 Proof:** `thm3_quorum_marginal_bound`, `thm3_bayes_accuracy_bound`, `thm3_quorum_k_scaling`.
- **Significance:** For $k=2$, origin attribution is capped at $50\%$; for $k=3$, capped at $33.3\%$, providing structural leakage reduction without injecting utility-destroying noise.
