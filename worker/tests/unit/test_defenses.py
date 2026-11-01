"""Unit tests for Phase 4 defenses: DP-FedAvg, Delayed Release, and Quorum Escrow."""

import torch
from fedids_worker.defenses.dp import clip_and_noise, compute_dp_sigma


def test_dp_sigma_computation():
    # Lower epsilon must produce strictly higher noise scale sigma
    sigma_eps10 = compute_dp_sigma(epsilon=10.0, delta=1e-5, rounds=50)
    sigma_eps1 = compute_dp_sigma(epsilon=1.0, delta=1e-5, rounds=50)
    assert sigma_eps1 > sigma_eps10 > 0.0


def test_dp_norm_clipping():
    # Create large parameter update
    delta = {
        "fc1.weight": torch.ones(10, 10) * 5.0,  # norm = 5 * 10 = 50.0
        "fc1.bias": torch.zeros(10),
    }
    clip_norm = 1.0
    clipped, original_norm = clip_and_noise(delta, clip_norm=clip_norm, sigma=0.0)

    # Total clipped norm should be <= clip_norm
    new_norm = torch.sqrt(sum(v.norm(2) ** 2 for v in clipped.values())).item()
    assert abs(new_norm - clip_norm) < 1e-4
    assert original_norm > clip_norm


def test_dp_noise_addition():
    torch.manual_seed(42)
    delta = {"fc1.weight": torch.zeros(5, 5)}
    noisy, _ = clip_and_noise(delta, clip_norm=1.0, sigma=2.0)
    assert not torch.allclose(noisy["fc1.weight"], torch.zeros(5, 5))
