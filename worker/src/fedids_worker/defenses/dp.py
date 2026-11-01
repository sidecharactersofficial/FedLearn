"""Phase 4: Client-Level Differential Privacy (DP-FedAvg).

1. Clips update norm to C = 1.0:
   \\tilde{Delta} w_i = Delta w_i * min(1, C / ||Delta w_i||_2)
2. Adds calibrated Gaussian noise N(0, sigma^2 C^2 I) calibrated for
   delta = 10^-5 across R rounds to hit privacy budget epsilon in {10.0, 5.0, 2.0, 1.0}.
"""

from __future__ import annotations

import math
from typing import Dict, Optional, Tuple

import numpy as np
import torch


def compute_dp_sigma(
    epsilon: float,
    delta: float = 1e-5,
    rounds: int = 50,
    sampling_rate: float = 1.0,
) -> float:
    """Computes Gaussian noise multiplier sigma for total (epsilon, delta) budget over R rounds."""
    if epsilon <= 0.0:
        return 0.0

    # Opacus RDP accountant approximation for Gaussian mechanism composition:
    # epsilon ≈ (2 * rounds * sampling_rate * log(1.25 / delta)) / sigma^2
    # sigma ≈ sqrt(2 * rounds * sampling_rate * log(1.25 / delta)) / epsilon
    term = 2.0 * rounds * sampling_rate * math.log(1.25 / max(1e-9, delta))
    sigma = math.sqrt(max(1e-4, term)) / epsilon
    return float(sigma)


def clip_and_noise(
    delta: Dict[str, torch.Tensor],
    clip_norm: float = 1.0,
    sigma: float = 0.0,
    device: Optional[torch.device] = None,
) -> Tuple[Dict[str, torch.Tensor], float]:
    """Clips the vector norm of parameter updates and adds calibrated Gaussian noise."""
    total_norm = torch.sqrt(sum(v.norm(2) ** 2 for v in delta.values())).item()
    clip_factor = min(1.0, clip_norm / max(1e-8, total_norm))

    noisy_delta: Dict[str, torch.Tensor] = {}
    for name, param in delta.items():
        clipped = param * clip_factor
        if sigma > 0.0:
            noise = torch.randn_like(param) * (sigma * clip_norm)
            if device:
                noise = noise.to(device)
            noisy_delta[name] = clipped + noise
        else:
            noisy_delta[name] = clipped

    return noisy_delta, total_norm
