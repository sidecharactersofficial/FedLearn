# Related Work and Claim Map

> Stage 0 output. Honesty-first policy applies: **every claim below must trace to a
> real file produced by a real run before it appears in the paper** — no fabricating
> rates. Claim IDs (C1–C3) are stable and referenced from `CLAIM_MAP.md` in the
> artifact once experiments exist.

## The working claim (fixed, verbatim)

> In cross-silo federated intrusion detection, the update that teaches other sites
> about a new attack also reveals which site saw it and when. We measure this
> trade-off between propagation speed and attribution leakage, and evaluate
> defenses that move along the frontier.

## Contribution statements (testable, claim-map style)

| ID | Claim (testable statement) | Evidence (stage) | Reproducibility type |
| :- | :--- | :--- | :- |
| **C1** | A server-side adversary (individual updates) attributes the origin site of a held-out zero-day family above the 1/N baseline at measurable rate, and with-secure-aggregation leakage degrades but does not vanish for small N. | Stage 5 (E2) | R3, tolerance pre-registered in the comparator script |
| **C2** | Zero-day propagation speed (rounds until non-origin sites reach X % recall on the held-out family) is a monotone/characterizable function of sites N, partition skew, local epochs, and client sampling rate, consistent across seeds ≥ 5 and families ≥ 3. | Stage 4 (E1) | R3, tolerance pre-registered |
| **C3** | Defenses (client-level DP sweep ε, simulated SecAgg, delayed release, thresholded k-of-N release) trace a Pareto frontier: leakage falls only at a measured cost in zero-day recall / propagation rounds, and no tested defense dominates. | Stage 6 (E3) | R3 |

Pending numbers (rate Z in C1, exact settings) are deliberately left blank until
runs exist — see the gate table at the bottom.

## The two-sentence IDS difference

Federated IDS is `few sites, tabular flows, heavy class-level non-IID by
organization` — an update vector is nearly a membership/ownership vector over
attack families, and a *new* family (zero-day) is a temporally crisp event that
source-inference-style attacks can localize in time. Attribution here is not a
privacy-hygiene nicety: "site X trained on the new attack" is operationally equal
to "site X got attacked first, at round t", which is exactly the threat
intelligence a consortium must NOT disclose, and the small consortium size makes
the 1/N baseline trivially low and SecAgg anonymity weak.

## Comparison table (literature scan)

Posture: verified venues/years; per-row "does it do what we do?" column marks the gap.

| Paper (venue) | Domain | Attack goal | Adversary | Datasets | Defenses evaluated | Does OUR thing? |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Melis et al., *Exploiting Unintended Feature Leakage in Collaborative Learning*, IEEE S&P 2019 | collaborative learning (image faces, attributes) | property inference (batch/gender/face properties, group membership), membership inference | curious participant peering at others' gradients | adult, celeba, CASIA | gradient compression (insufficient); DP end-to-end | **No** — per-property leakage only; no source-site attribution, no timing of a new-class event, not IDS-tabular |
| Hu et al., *Source Inference Attacks in Federated Learning* (SIA), ICDM 2021 — closest prior | FL multi-client (synthetic + 5 real, non-IDS) | which client owns a training member (per-sample source) | honest-but-curious server using local models' prediction loss | synthetic + 5 real | none studied | **Partial** — source attribution exists but is (a) per-member static, not *event-level* (new attack family), (b) no timing inference, (c) no propagation-vs-leakage trade-off, (d) no IDS/security semantics, (e) no peer-adversary variant |
| Zhu, Liu, Han *Deep Leakage from Gradients*, NeurIPS 2019; Geiping et al., NeurIPS 2020 (gradient inversion) | vision | reconstruct exact images/labels from gradients | server (single gradient, DLG/iDLG family) | MNIST, ImageNet subsets | DP noise, gradient coding | **No** — data reconstruction, not attribution; per-client-single-batch; not event-level |
| Nasr et al., *Comprehensive Privacy Analysis of DL*, IEEE S&P 2019 (+ Suri et al., subject-MIA in FL, 2022) | classifiers incl. FL | membership / subject-membership | centralized & FL | standard ML | DP-SGD, amplification | **No** — member-in, member-out; not "who saw the new threat first, when" |
| Marchand et al., *SRATTA*, ICML 2023 | client re-identification of updates | reattributing client-specific signals *under secure aggregation* | server vs. SecAgg (censored-signal exploitation) | vision datasets | none (attack paper) | **Partial** — confirms SecAgg leaves traces, but not timing/origin-of-new-attack; we reuse as evidence for the small-N SecAgg leakage check |
| Popoola et al. (2022), Javeed et al. (2024), Buyuktanir et al. survey (2025), FLEX-IDS (2026) | federated IDS on CIC-IDS2017 / Edge-IIoTset etc. | none (defense/system papers) | assumed private by construction | IDS flow datasets | FL itself is the privacy mechanism | **No** — the whole FL-IDS line treats meta-leakage as solved by federation; zero-day focus is detection, not disclosure |
| Bonawitz et al., *Practical Secure Aggregation*, 2017; McMahan et al., client-level DP-RNN, ICLR 2019; Chen et al., *Fundamental Price of SecAgg in DP-FL*, ICML 2022 | FL training | — (defense primitives) | — | — | SecAgg protocol; client-level DP; distributed DP theory | These are our *defenses*; the cost side (propagation slowdown measured as detection capability-loss) is not studied for IDS event spread |

## The gap, stated for a reviewer

No prior work connects **(i) event-level attribution** (which site, when — not
which sample), **(ii) propagation dynamics** of a newly-seen attack family across
a cross-silo federation, and **(iii) the defense frontier** trading attribution
leakage against zero-day response speed, in a deployment that is realistic for
IDS consortia (small N, non-IID by organization, delayed labels). Melis gives us
property/timing intuition on gradients; SIA gives us source attribution; SRATTA
gives us residual leakage under SecAgg; FL-IDS literature gives us the
application and the naive "FL is private" assumption we falsify — none of them
joins all three.

## Reviewer-anticipation notes

- Predictor question A: *"This is Melis et al. on CIC-IDS2017."* → Counter: Melis
  does per-property leakage with data-group priors; we do event-level origin+time
  attribution bound to propagation measurement, with security semantics of the
  leaked statement, and a defense frontier covering the anti-leakage mechanisms.
- Predictor question B: *"This is SIA."* → Counter: per-member static vs
  event+timing dynamic; peer-adversary via global-model diffs is absent there; our
  adversary goals are operational-intel leakage, not generic source privacy.
- Self-gate (Stage 0 Gate): if attacked-by-compare work turns up between now and
  drafting, the fallback is narrowing to "attribution of the source site +
  propagation dynamics" or the SoK route — not silently editing the claim.

## Open items from this scan

- Pull exact CIC-IDS family lists from the raw dataset (the owner's other
  directories hold dataset + retrieval scripts; need the path confirmed — never
  tune on the test split once partitioning exists).
- Delta A: Melis's exact attack recipe must be reimplemented as a baseline (or our
  attack named as a superset of it) to defuse "just Melis" — assign to Stage 5.
- Verify Hu et al. (SIA) numbers only as baseline; we do not need their code.

_Generated with Codebuff (AI-scaffolded research notes; content to be
human-verified before paper drafting)._
