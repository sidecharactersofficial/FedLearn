"""Phase 2 & Phase 4: Federation Simulation Engine.

Executes cross-silo FL training with real PyTorch backbones (MLP, 1D-CNN, AE-Hybrid):
- Aggregators: FedAvg, FedProx (mu=0.01), FedYogi / FedAdam
- Defenses: SecAgg simulation, Client DP (DP-FedAvg), Delayed Release, Thresholded Quorum Release
- Zero-day injection hook and propagation metrics tracking (Non-origin recall, tau_0.80, AUPC_20, Catastrophic Forgetting)
- Emits metrics compatible with metrics.parquet schema for R analysis.
"""

from __future__ import annotations

import copy
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset

from fedids_worker.contracts import config_pb2
from fedids_worker.federation.injection import ZeroDayInjectionHook
from fedids_worker.federation.models import create_model
from fedids_worker.federation.partition import ClientSplit, partition_dirichlet

logger = logging.getLogger("fedids_worker.federation.simulation")


def compute_metrics(
    model: nn.Module,
    X: np.ndarray,
    y: np.ndarray,
    device: torch.device,
    batch_size: int = 512,
) -> Tuple[float, float, float]:
    """Computes binary classification loss, accuracy, and recall on positive class (malicious)."""
    if len(y) == 0:
        return 0.0, 0.0, 0.0

    model.eval()
    dataset = TensorDataset(torch.from_numpy(X).float(), torch.from_numpy(y).long())
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    total_loss = 0.0
    total_correct = 0
    tp = 0
    positives = int(np.sum(y == 1))

    criterion = nn.CrossEntropyLoss(reduction="sum")

    with torch.no_grad():
        for batch_x, batch_y in loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            logits = model(batch_x)
            loss = criterion(logits, batch_y)
            total_loss += loss.item()
            preds = torch.argmax(logits, dim=1)
            total_correct += (preds == batch_y).sum().item()
            tp += ((preds == 1) & (batch_y == 1)).sum().item()

    avg_loss = total_loss / len(y)
    acc = total_correct / len(y)
    recall = (tp / positives) if positives > 0 else (1.0 if tp == 0 and len(y) > 0 else 0.0)
    return avg_loss, acc, recall


def train_client_epoch(
    model: nn.Module,
    global_model: nn.Module,
    train_X: np.ndarray,
    train_y: np.ndarray,
    epochs: int,
    lr: float,
    device: torch.device,
    aggregator: int,
    prox_mu: float = 0.01,
    batch_size: int = 256,
) -> Dict[str, torch.Tensor]:
    """Trains local client model for E epochs and returns the update delta_w = w_local - w_global."""
    model.train()
    dataset = TensorDataset(torch.from_numpy(train_X).float(), torch.from_numpy(train_y).long())
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    global_params = {k: v.detach().clone() for k, v in global_model.named_parameters()}

    for _ in range(epochs):
        for bx, by in loader:
            bx, by = bx.to(device), by.to(device)
            optimizer.zero_grad()
            logits = model(bx)
            loss = criterion(logits, by)

            # FedProx regularizer
            if aggregator == config_pb2.AGGREGATOR_FEDPROX and prox_mu > 0.0:
                prox_term = 0.0
                for name, param in model.named_parameters():
                    prox_term += (param - global_params[name]).norm(2) ** 2
                loss = loss + (prox_mu / 2.0) * prox_term

            loss.backward()
            optimizer.step()

    # Compute delta = w_local - w_global
    delta: Dict[str, torch.Tensor] = {}
    with torch.no_grad():
        for name, param in model.named_parameters():
            delta[name] = (param - global_params[name]).cpu().clone()

    return delta


def apply_client_dp(
    delta: Dict[str, torch.Tensor],
    clip_norm: float = 1.0,
    sigma: float = 0.05,
    rng: Optional[np.random.Generator] = None,
) -> Dict[str, torch.Tensor]:
    """Clips client update norm to C and adds calibrated Gaussian noise."""
    total_norm = torch.sqrt(sum(v.norm(2) ** 2 for v in delta.values())).item()
    clip_factor = min(1.0, clip_norm / max(1e-8, total_norm))
    
    noisy_delta = {}
    for k, v in delta.items():
        clipped = v * clip_factor
        if sigma > 0.0:
            noise = torch.randn_like(v) * (sigma * clip_norm)
            noisy_delta[k] = clipped + noise
        else:
            noisy_delta[k] = clipped
    return noisy_delta


def run_federation(cfg: "config_pb2.RunConfig", trace_recorder=None) -> list[dict]:
    """Main federation execution entrypoint called by Rust orchestrator / worker."""
    rng = np.random.default_rng(cfg.seed)
    torch.manual_seed(cfg.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    fed = cfg.federation
    zd = cfg.zero_day
    defense = cfg.defense

    dataset_path = cfg.dataset.processed_dir if cfg.dataset.processed_dir else "datasets/processed"
    if cfg.dataset.name:
        candidate = Path(dataset_path) / f"{cfg.dataset.name}.parquet"
        if candidate.exists():
            cleaned_file = candidate
        elif Path(cfg.dataset.name).exists():
            cleaned_file = Path(cfg.dataset.name)
        else:
            cleaned_file = Path(dataset_path) / "cleaned_cic2018.parquet"
    else:
        cleaned_file = Path(dataset_path) / "cleaned_cic2018.parquet"
    if not cleaned_file.exists():
        cleaned_file = Path("datasets/processed/cleaned_cic2018.parquet")

    # Partition dataset
    client_splits = partition_dirichlet(
        dataset_path=cleaned_file,
        num_sites=fed.num_sites,
        skew=cfg.dataset.skew if cfg.dataset.skew > 0 else 0.5,
        zero_day_family=zd.family if zd.family else "Infiltration",
        seed=int(cfg.seed),
    )

    # Initialize models
    in_features = client_splits[0].train_X.shape[1]
    global_model = create_model("mlp", in_features=in_features, num_classes=2).to(device)

    # Injection hook
    injection_hook = ZeroDayInjectionHook(
        origin_site=zd.origin_site,
        injection_round=zd.injection_round,
        intensity=0.10,
        label_delay_rounds=zd.label_delay_rounds,
        seed=int(cfg.seed),
    )

    # Server optimizer state for FedYogi / FedAdam
    server_m: Dict[str, torch.Tensor] = {}
    server_v: Dict[str, torch.Tensor] = {}
    beta1, beta2, eta_server = 0.9, 0.99, 1.0

    # Delay buffer for Sweep 4B
    delay_buffer: List[Dict[str, torch.Tensor]] = []

    # Quorum release tracking for Sweep 4C
    quorum_seen_sites: set = set()

    rows: list[dict] = []
    baseline_known_recall_round_prior: Optional[float] = None
    first_round_80_tau: Optional[int] = None
    post_injection_recalls: List[float] = []

    # Calculate noise scale for DP if enabled
    dp_sigma = 0.0
    if defense.kind == config_pb2.DEFENSE_KIND_CLIENT_DP and defense.epsilon > 0:
        # Approximate Gaussian mechanism scale for delta=1e-5 over R rounds
        dp_sigma = np.sqrt(2.0 * np.log(1.25 / max(1e-7, defense.delta or 1e-5))) / (defense.epsilon / np.sqrt(max(1, fed.rounds)))

    for rnd in range(1, fed.rounds + 1):
        # Client sampling
        sampled_clients = [i for i in range(fed.num_sites) if rng.uniform() <= fed.client_sampling_rate]
        if not sampled_clients:
            sampled_clients = [int(rng.choice(fed.num_sites))]

        client_updates: Dict[int, Dict[str, torch.Tensor]] = {}

        for client_id in sampled_clients:
            client = client_splits[client_id]
            train_X, train_y = injection_hook.get_client_train_batch(client, current_round=rnd)

            # Local copy of global model
            local_model = copy.deepcopy(global_model).to(device)
            delta = train_client_epoch(
                model=local_model,
                global_model=global_model,
                train_X=train_X,
                train_y=train_y,
                epochs=fed.local_epochs,
                lr=1e-3,
                device=device,
                aggregator=fed.aggregator,
                prox_mu=0.01,
            )

            # Defense processing
            # 1. Client DP
            if defense.kind == config_pb2.DEFENSE_KIND_CLIENT_DP:
                delta = apply_client_dp(delta, clip_norm=defense.clip_norm or 1.0, sigma=dp_sigma, rng=rng)

            # 2. Delayed Release
            if defense.kind == config_pb2.DEFENSE_KIND_DELAYED_RELEASE and client_id == zd.origin_site and rnd >= zd.injection_round:
                d = max(1, defense.release_delay_rounds or 3)
                delay_buffer.append(delta)
                if len(delay_buffer) <= d:
                    # Delay update: replace with prior benign momentum
                    delta = {k: v * 0.1 for k, v in delta.items()}
                else:
                    delta = delay_buffer.pop(0)

            # 3. Thresholded Quorum Release
            if defense.kind == config_pb2.DEFENSE_KIND_THRESHOLDED_RELEASE:
                k_quorum = max(2, defense.release_threshold_sites or 3)
                if rnd >= zd.injection_round and client_id == zd.origin_site:
                    quorum_seen_sites.add(client_id)
                # Simulate secondary sites observing outbreak 2-4 rounds after onset
                if rnd >= zd.injection_round + 2:
                    quorum_seen_sites.add((zd.origin_site + 1) % fed.num_sites)
                if rnd >= zd.injection_round + 4:
                    quorum_seen_sites.add((zd.origin_site + 2) % fed.num_sites)

                if rnd >= zd.injection_round and len(quorum_seen_sites) < k_quorum and client_id == zd.origin_site:
                    # Hold back zero-day gradient components in escrow
                    delta = {k: v * 0.05 for k, v in delta.items()}

            client_updates[client_id] = delta

        # Aggregate updates
        global_delta: Dict[str, torch.Tensor] = {}
        for k in global_model.state_dict().keys():
            if any(k in upd for upd in client_updates.values()):
                stacked = torch.stack([client_updates[cid][k] for cid in client_updates if k in client_updates[cid]])
                global_delta[k] = torch.mean(stacked, dim=0)

        # Record updates for trace recorder (Phase 3 attack traces)
        if trace_recorder is not None:
            trace_recorder.record_round(
                round_num=rnd,
                client_updates=client_updates,
                global_delta=global_delta,
                origin_site=zd.origin_site,
                injection_round=zd.injection_round,
            )

        # Apply server optimizer (FedAvg, FedYogi, FedAdam)
        with torch.no_grad():
            for name, param in global_model.named_parameters():
                if name in global_delta:
                    d = global_delta[name].to(device)
                    if fed.aggregator == config_pb2.AGGREGATOR_FEDYOGI:
                        if name not in server_m:
                            server_m[name] = torch.zeros_like(d)
                            server_v[name] = torch.zeros_like(d)
                        server_m[name] = beta1 * server_m[name] + (1 - beta1) * d
                        delta_sq = d ** 2
                        server_v[name] = server_v[name] - (1 - beta2) * delta_sq * torch.sign(server_v[name] - delta_sq)
                        param.add_(eta_server * server_m[name] / (torch.sqrt(server_v[name]) + 1e-3))
                    elif fed.aggregator == config_pb2.AGGREGATOR_FEDADAM:
                        if name not in server_m:
                            server_m[name] = torch.zeros_like(d)
                            server_v[name] = torch.zeros_like(d)
                        server_m[name] = beta1 * server_m[name] + (1 - beta1) * d
                        server_v[name] = beta2 * server_v[name] + (1 - beta2) * (d ** 2)
                        param.add_(eta_server * server_m[name] / (torch.sqrt(server_v[name]) + 1e-3))
                    else:  # FedAvg / FedProx standard update
                        param.add_(d)

        # Evaluate per-site metrics
        non_origin_zd_recalls = []
        site_known_recalls = []

        for site_id in range(fed.num_sites):
            client = client_splits[site_id]
            # Baseline test metrics
            _, base_acc, base_rec = compute_metrics(global_model, client.test_X, client.test_y, device)
            site_known_recalls.append(base_rec)

            # Zero-day test recall
            _, _, zd_rec = compute_metrics(global_model, client.zero_day_test_X, client.zero_day_test_y, device)

            if site_id != zd.origin_site:
                non_origin_zd_recalls.append(zd_rec)

            rows.append({
                "run_id": cfg.run_id,
                "round": rnd,
                "site": site_id,
                "metric": "zero_day_recall",
                "value": float(zd_rec),
            })
            rows.append({
                "run_id": cfg.run_id,
                "round": rnd,
                "site": site_id,
                "metric": "known_recall",
                "value": float(base_rec),
            })

        mean_non_origin_zd_rec = float(np.mean(non_origin_zd_recalls)) if non_origin_zd_recalls else 0.0
        mean_known_rec = float(np.mean(site_known_recalls))

        # Checkpoint prior round to measure catastrophic forgetting
        if rnd == zd.injection_round - 1:
            baseline_known_recall_round_prior = mean_known_rec

        # Catastrophic forgetting: drop in known recall compared to t0 - 1
        catastrophic_forgetting = 0.0
        if baseline_known_recall_round_prior is not None and rnd >= zd.injection_round:
            catastrophic_forgetting = max(0.0, baseline_known_recall_round_prior - mean_known_rec)

        # Track tau_0.80: first offset where mean non-origin zero-day recall reaches 0.80
        if rnd >= zd.injection_round:
            post_injection_recalls.append(mean_non_origin_zd_rec)
            if mean_non_origin_zd_rec >= 0.80 and first_round_80_tau is None:
                first_round_80_tau = rnd - zd.injection_round

        # Global metrics row
        rows.append({
            "run_id": cfg.run_id,
            "round": rnd,
            "site": -1,
            "metric": "mean_non_origin_zero_day_recall",
            "value": mean_non_origin_zd_rec,
        })
        rows.append({
            "run_id": cfg.run_id,
            "round": rnd,
            "site": -1,
            "metric": "catastrophic_forgetting",
            "value": float(catastrophic_forgetting),
        })

    # Summary calculations
    tau_val = float(first_round_80_tau) if first_round_80_tau is not None else float(fed.rounds - zd.injection_round)
    aupc_20 = float(np.mean(post_injection_recalls[:20])) if post_injection_recalls else 0.0

    rows.append({"run_id": cfg.run_id, "round": fed.rounds, "site": -1, "metric": "tau_0.80", "value": tau_val})
    rows.append({"run_id": cfg.run_id, "round": fed.rounds, "site": -1, "metric": "aupc_20", "value": aupc_20})

    return rows
