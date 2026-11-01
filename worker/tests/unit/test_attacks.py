"""Unit tests for Phase 3 attacks: shadow generation and spatio-temporal features."""

import numpy as np
import pytest
from fedids_worker.attacks.feature_extractor import (
    extract_features_server_secagg,
    extract_features_server_unprotected,
)
from fedids_worker.attacks.shadow_generator import ShadowTrace


def test_feature_extraction_shapes():
    num_sites = 5
    total_rounds = 10
    client_updates = {}
    global_deltas = {}

    for r in range(1, total_rounds + 1):
        client_updates[r] = {}
        for c in range(num_sites):
            client_updates[r][c] = {
                "penultimate": np.random.randn(64).astype(np.float32),
                "final_weight": np.random.randn(2, 64).astype(np.float32),
                "final_bias": np.random.randn(2).astype(np.float32),
            }
        global_deltas[r] = {
            "penultimate": np.random.randn(64).astype(np.float32),
            "final_weight": np.random.randn(2, 64).astype(np.float32),
            "final_bias": np.random.randn(2).astype(np.float32),
        }

    trace = ShadowTrace(
        run_id="test-trace",
        origin_site=2,
        onset_round=5,
        zero_day_family="Infiltration",
        num_sites=num_sites,
        total_rounds=total_rounds,
        client_updates=client_updates,
        global_deltas=global_deltas,
    )

    # Test unprotected server feature extraction
    c_feat, t_feat, orig, onset = extract_features_server_unprotected(trace)
    assert orig == 2
    assert onset == 5
    assert c_feat.shape[0] == num_sites
    assert t_feat.ndim == 1

    # Test secagg feature extraction
    c_feat_sec, t_feat_sec, orig_sec, onset_sec = extract_features_server_secagg(trace, peer_client_id=None)
    assert orig_sec == 2
    assert onset_sec == 5
    assert c_feat_sec.shape[0] == num_sites
