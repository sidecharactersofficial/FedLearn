"""Phase 3: Spatio-Temporal Feature Extractor.

Extracts feature vectors for Origin Classifier (Head 1) and Timing Regressor (Head 2):
1. Regime 1: Unprotected Server (observing per-client updates {Delta w_i^(t)})
2. Regime 2: SecAgg Server (observing Delta W^(t) only) & Curious Peer (observing Delta W_\\neg peer^(t))
"""

from __future__ import annotations

import numpy as np
from fedids_worker.attacks.shadow_generator import ShadowTrace


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a < 1e-9 or norm_b < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def extract_features_server_unprotected(trace: ShadowTrace) -> Tuple[np.ndarray, np.ndarray, int, int]:
    """Regime 1: Unprotected Server observing per-client updates."""
    N = trace.num_sites
    R = trace.total_rounds

    # Client-level features across rounds: shape (N, feature_dim)
    # Features per client:
    # - Mean and max L2, L1 norm of penultimate and final layers
    # - Temporal self-cosine mean and min
    # - Peer cosine mean and min
    # - Within-round z-scores peak and mean
    # - Final layer bias variance
    client_features = []

    for cid in range(N):
        l2_pen, l1_pen = [], []
        l2_fin, l1_fin = [], []
        self_cos_pen = []
        peer_cos_pen = []
        bias_vars = []

        for rnd in range(1, R + 1):
            upd = trace.client_updates[rnd][cid]
            g_delta = trace.global_deltas[rnd]

            pen = upd["penultimate"]
            fin_w = upd["final_weight"]
            fin_b = upd["final_bias"]

            l2_pen.append(np.linalg.norm(pen))
            l1_pen.append(np.sum(np.abs(pen)))
            l2_fin.append(np.linalg.norm(fin_w))
            l1_fin.append(np.sum(np.abs(fin_w)))
            bias_vars.append(np.var(fin_b))

            # Temporal self-cosine
            if rnd > 1:
                prev_pen = trace.client_updates[rnd - 1][cid]["penultimate"]
                self_cos_pen.append(cosine_sim(pen, prev_pen))

            # Peer cosine
            peer_cos_pen.append(cosine_sim(pen, g_delta["penultimate"]))

        # Aggregate across rounds
        feat = [
            float(np.mean(l2_pen)), float(np.max(l2_pen)), float(np.std(l2_pen)),
            float(np.mean(l1_pen)), float(np.max(l1_pen)),
            float(np.mean(l2_fin)), float(np.max(l2_fin)),
            float(np.mean(l1_fin)), float(np.max(l1_fin)),
            float(np.mean(self_cos_pen)) if self_cos_pen else 0.0,
            float(np.min(self_cos_pen)) if self_cos_pen else 0.0,
            float(np.mean(peer_cos_pen)), float(np.min(peer_cos_pen)),
            float(np.mean(bias_vars)), float(np.max(bias_vars)),
        ]
        client_features.append(feat)

    # Compute within-round cross-client z-scores for L2 norm
    client_features = np.array(client_features, dtype=np.float32)

    # Global timing features (across all rounds): shape (R,) -> onset round regressor
    # Peak norm difference across rounds
    round_max_l2_diff = []
    for rnd in range(1, R + 1):
        norms = [np.linalg.norm(trace.client_updates[rnd][i]["penultimate"]) for i in range(N)]
        round_max_l2_diff.append(np.max(norms) - np.median(norms))
    timing_feat = np.array(round_max_l2_diff, dtype=np.float32)

    return client_features, timing_feat, trace.origin_site, trace.onset_round


def extract_features_server_secagg(
    trace: ShadowTrace,
    peer_client_id: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray, int, int]:
    """Regime 2: SecAgg Server (peer_client_id=None) or Curious Peer."""
    N = trace.num_sites
    R = trace.total_rounds

    # Calculate observed global update Delta W
    observed_deltas = {}
    for rnd in range(1, R + 1):
        g = trace.global_deltas[rnd]
        if peer_client_id is None:
            # Server with SecAgg sees exact global delta Delta W
            observed_deltas[rnd] = g["penultimate"]
        else:
            # Curious Peer subtracts own contribution: Delta W_neg_peer = N/(N-1) * (Delta W - 1/N * Delta w_peer)
            p_pen = trace.client_updates[rnd][peer_client_id]["penultimate"]
            observed_deltas[rnd] = (N / (N - 1)) * (g["penultimate"] - (1.0 / N) * p_pen)

    # Client Fingerprint Alignment:
    # 1. Compute warm-up reference gradient template g_bar_i for each candidate site i during t < 15
    warmup_rounds = min(15, trace.onset_round - 1)
    client_templates = {}
    for cid in range(N):
        warmup_updates = [trace.client_updates[r][cid]["penultimate"] for r in range(1, warmup_rounds + 1)]
        client_templates[cid] = np.mean(warmup_updates, axis=0) if warmup_updates else np.zeros_like(observed_deltas[1])

    # 2. Compute inner-product alignment <Delta W^(t) - Delta W^(t-1), g_bar_i> across candidate sites
    client_alignments = {cid: [] for cid in range(N)}
    trajectory_inflections = []
    consecutive_cosines = []

    for rnd in range(2, R + 1):
        diff = observed_deltas[rnd] - observed_deltas[rnd - 1]
        trajectory_inflections.append(float(np.linalg.norm(diff)))
        consecutive_cosines.append(cosine_sim(observed_deltas[rnd], observed_deltas[rnd - 1]))

        for cid in range(N):
            align = float(np.dot(diff, client_templates[cid]))
            client_alignments[cid].append(align)

    # Summary feature vector per client candidate
    candidate_features = []
    for cid in range(N):
        arr = np.array(client_alignments[cid])
        feat = [
            float(np.mean(arr)),
            float(np.max(arr)),
            float(np.std(arr)),
            float(np.percentile(arr, 90)),
            float(np.sum(np.abs(arr))),
        ]
        candidate_features.append(feat)

    candidate_features = np.array(candidate_features, dtype=np.float32)
    timing_feat = np.array(trajectory_inflections, dtype=np.float32)

    return candidate_features, timing_feat, trace.origin_site, trace.onset_round
