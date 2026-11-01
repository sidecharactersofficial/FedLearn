"""Phase 1: Zero-Day Injection Hook.

Configures round-by-round training sets and zero-day attack injection:
1. For rounds t < t0: site i trains strictly on baseline data Di^base.
2. At round t >= t0: origin site o injects D_f* into its training split at intensity gamma in [0.05, 0.15].
3. Non-origin sites (i != o) train strictly on Di^base.
4. All non-origin sites evaluate their global model test recall on held-out test samples of f*.
"""

from __future__ import annotations

import logging
from typing import Tuple

import numpy as np
from fedids_worker.federation.partition import ClientSplit

logger = logging.getLogger("fedids_worker.federation.injection")


class ZeroDayInjectionHook:
    def __init__(
        self,
        origin_site: int,
        injection_round: int,
        intensity: float = 0.10,
        label_delay_rounds: int = 0,
        seed: int = 42,
    ):
        self.origin_site = origin_site
        self.injection_round = injection_round
        self.intensity = max(0.01, min(0.50, intensity))
        self.label_delay_rounds = label_delay_rounds
        self.rng = np.random.default_rng(seed)

    def get_client_train_batch(
        self,
        client: ClientSplit,
        current_round: int,
        batch_size: int = 256,
        subsample_per_round: int = 2048,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Returns the training features and labels for this client in the given round."""
        n_train = len(client.train_y)
        # Select baseline sample indices for this round
        sample_size = min(n_train, subsample_per_round)
        indices = self.rng.choice(n_train, size=sample_size, replace=False)
        X = client.train_X[indices].copy()
        y = client.train_y[indices].copy()

        # Check if client is the origin site and round is at or after injection
        effective_round = current_round
        if (client.client_id == self.origin_site) and (effective_round >= self.injection_round):
            # Injection occurs
            n_zd_inject = max(16, int(sample_size * self.intensity))
            n_zd_avail = len(client.zero_day_train_y)
            zd_indices = self.rng.choice(n_zd_avail, size=n_zd_inject, replace=(n_zd_inject > n_zd_avail))

            zd_X = client.zero_day_train_X[zd_indices]
            # Handle SOC label delay
            if current_round < (self.injection_round + self.label_delay_rounds):
                # Traffic arrives physically, but SOC analysts haven't labeled it yet -> label as benign (0) or withheld
                zd_y = np.zeros(n_zd_inject, dtype=np.int64)
            else:
                zd_y = np.ones(n_zd_inject, dtype=np.int64)

            # Replace end of batch with zero-day attack flows
            X[-n_zd_inject:] = zd_X
            y[-n_zd_inject:] = zd_y

        return X, y
