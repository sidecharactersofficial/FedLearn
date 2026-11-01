"""Phase 3: Shadow Federation Generator.

Simulates K shadow federation runs on auxiliary data split D_aux:
- Random origin site o ~ Uniform(0, N-1)
- Random onset round t0 ~ Uniform(15, 35)
- Compactly records parameter updates for penultimate layer (L-1) and classification layer (L)
  for both individual client updates {Delta w_i^(t)} and global updates Delta W^(t).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
from fedids_worker.contracts import config_pb2
from fedids_worker.federation.injection import ZeroDayInjectionHook
from fedids_worker.federation.models import create_model
from fedids_worker.federation.partition import partition_dirichlet
from fedids_worker.federation.simulation import apply_client_dp, train_client_epoch

logger = logging.getLogger("fedids_worker.attacks.shadow_generator")


@dataclass
class ShadowTrace:
    run_id: str
    origin_site: int
    onset_round: int
    zero_day_family: str
    num_sites: int
    total_rounds: int
    # Compact per-round updates: round -> client_id -> {'penultimate': np.ndarray, 'final_weight': np.ndarray, 'final_bias': np.ndarray}
    client_updates: Dict[int, Dict[int, Dict[str, np.ndarray]]]
    # Compact per-round global delta: round -> {'penultimate': np.ndarray, 'final_weight': np.ndarray, 'final_bias': np.ndarray}
    global_deltas: Dict[int, Dict[str, np.ndarray]]


def extract_compact_layers(delta: Dict[str, torch.Tensor]) -> Dict[str, np.ndarray]:
    """Extracts weights of penultimate layer and final layer for attack feature extraction."""
    keys = list(delta.keys())
    # Identify classification layer (last weight and bias)
    weight_keys = [k for k in keys if "weight" in k]
    bias_keys = [k for k in keys if "bias" in k]

    final_weight_key = weight_keys[-1] if weight_keys else None
    penultimate_weight_key = weight_keys[-2] if len(weight_keys) >= 2 else final_weight_key
    final_bias_key = bias_keys[-1] if bias_keys else None

    return {
        "penultimate": delta[penultimate_weight_key].numpy().flatten() if penultimate_weight_key else np.zeros(64),
        "final_weight": delta[final_weight_key].numpy().flatten() if final_weight_key else np.zeros(64),
        "final_bias": delta[final_bias_key].numpy().flatten() if final_bias_key else np.zeros(2),
    }


def generate_single_shadow_run(
    run_id: str,
    dataset_path: Path | str,
    num_sites: int = 10,
    rounds: int = 50,
    zero_day_family: str = "Infiltration",
    origin_site: Optional[int] = None,
    onset_round: Optional[int] = None,
    skew: float = 0.5,
    seed: int = 42,
) -> ShadowTrace:
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    if origin_site is None:
        origin_site = int(rng.integers(0, num_sites))
    if onset_round is None:
        onset_round = int(rng.integers(15, min(36, rounds - 5)))

    # Partition dataset
    client_splits = partition_dirichlet(
        dataset_path=dataset_path,
        num_sites=num_sites,
        skew=skew,
        zero_day_family=zero_day_family,
        seed=seed,
    )

    global_model = create_model("mlp", in_features=66, num_classes=2).to(device)

    injection_hook = ZeroDayInjectionHook(
        origin_site=origin_site,
        injection_round=onset_round,
        intensity=0.10,
        label_delay_rounds=0,
        seed=seed,
    )

    recorded_client_updates: Dict[int, Dict[int, Dict[str, np.ndarray]]] = {}
    recorded_global_deltas: Dict[int, Dict[str, np.ndarray]] = {}

    for rnd in range(1, rounds + 1):
        round_updates: Dict[int, Dict[str, torch.Tensor]] = {}
        compact_round_client_updates: Dict[int, Dict[str, np.ndarray]] = {}

        for client_id in range(num_sites):
            client = client_splits[client_id]
            train_X, train_y = injection_hook.get_client_train_batch(client, current_round=rnd)

            local_model = copy_model(global_model).to(device)
            delta = train_client_epoch(
                model=local_model,
                global_model=global_model,
                train_X=train_X,
                train_y=train_y,
                epochs=1,
                lr=1e-3,
                device=device,
                aggregator=config_pb2.AGGREGATOR_FEDAVG,
            )
            round_updates[client_id] = delta
            compact_round_client_updates[client_id] = extract_compact_layers(delta)

        # Aggregate global delta
        global_delta: Dict[str, torch.Tensor] = {}
        for k in global_model.state_dict().keys():
            if any(k in upd for upd in round_updates.values()):
                stacked = torch.stack([round_updates[cid][k] for cid in round_updates if k in round_updates[cid]])
                global_delta[k] = torch.mean(stacked, dim=0)

        recorded_client_updates[rnd] = compact_round_client_updates
        recorded_global_deltas[rnd] = extract_compact_layers(global_delta)

        # Apply global update
        with torch.no_grad():
            for name, param in global_model.named_parameters():
                if name in global_delta:
                    param.add_(global_delta[name].to(device))

    return ShadowTrace(
        run_id=run_id,
        origin_site=origin_site,
        onset_round=onset_round,
        zero_day_family=zero_day_family,
        num_sites=num_sites,
        total_rounds=rounds,
        client_updates=recorded_client_updates,
        global_deltas=recorded_global_deltas,
    )


def copy_model(model: nn.Module) -> nn.Module:
    import copy
    return copy.deepcopy(model)
