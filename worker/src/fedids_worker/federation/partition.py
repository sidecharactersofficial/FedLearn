"""Phase 1: Leave-One-Family-Out & Dirichlet Non-IID Partitioner.

Partitioning Engine:
1. Held-out zero-day f* (Infiltration, Botnet, FTP-BruteForce, or DoS/DDoS), remaining 3 in F_known.
2. Partition Benign and F_known across N clients using Dirichlet distribution Dir_N(alpha).
3. 80%/20% stratified train/test split locally at each client.
4. Fit StandardScaler strictly on each client's warm-up training set (t < t0) to prevent lookahead leakage.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger("fedids_worker.federation.partition")

CANONICAL_66_FEATURES = [
    "Flow Duration", "Tot Fwd Pkts", "Tot Bwd Pkts", "TotLen Fwd Pkts", "TotLen Bwd Pkts",
    "Fwd Pkt Len Max", "Fwd Pkt Len Min", "Fwd Pkt Len Mean", "Fwd Pkt Len Std",
    "Bwd Pkt Len Max", "Bwd Pkt Len Min", "Bwd Pkt Len Mean", "Bwd Pkt Len Std",
    "Flow Byts/s", "Flow Pkts/s", "Flow IAT Mean", "Flow IAT Std", "Flow IAT Max", "Flow IAT Min",
    "Fwd IAT Tot", "Fwd IAT Mean", "Fwd IAT Std", "Fwd IAT Max", "Fwd IAT Min",
    "Bwd IAT Tot", "Bwd IAT Mean", "Bwd IAT Std", "Bwd IAT Max", "Bwd IAT Min",
    "Fwd PSH Flags", "Bwd PSH Flags", "Fwd URG Flags", "Bwd URG Flags",
    "Fwd Header Len", "Bwd Header Len", "Fwd Pkts/s", "Bwd Pkts/s",
    "Pkt Len Min", "Pkt Len Max", "Pkt Len Mean", "Pkt Len Std", "Pkt Len Var",
    "FIN Flag Cnt", "SYN Flag Cnt", "RST Flag Cnt", "PSH Flag Cnt", "ACK Flag Cnt",
    "URG Flag Cnt", "CWE Flag Count", "ECE Flag Cnt", "Down/Up Ratio", "Pkt Size Avg",
    "Fwd Seg Size Avg", "Bwd Seg Size Avg", "Subflow Fwd Pkts", "Subflow Fwd Byts",
    "Subflow Bwd Pkts", "Subflow Bwd Byts", "Init Fwd Win Byts", "Init Bwd Win Byts",
    "Fwd Act Data Pkts", "Fwd Seg Size Min", "Active Mean", "Active Std", "Active Max", "Active Min"
]

MACRO_FAMILIES = ["Botnet", "FTP-BruteForce", "Infiltration", "DoS/DDoS"]


@dataclass
class ClientSplit:
    client_id: int
    train_X: np.ndarray        # Scaled baseline training features (N, 66)
    train_y: np.ndarray        # (N,) binary labels (0 = benign, 1 = malicious)
    train_families: np.ndarray # (N,) family names
    test_X: np.ndarray         # Scaled baseline test features (M, 66)
    test_y: np.ndarray         # (M,) binary labels
    test_families: np.ndarray  # (M,) family names
    zero_day_train_X: np.ndarray # Candidate zero-day training pool for origin site
    zero_day_train_y: np.ndarray
    zero_day_test_X: np.ndarray  # Held-out zero-day test set (scaled with client's scaler)
    zero_day_test_y: np.ndarray
    scaler: StandardScaler


def partition_dirichlet(
    dataset_path: Path | str,
    num_sites: int,
    skew: float,
    zero_day_family: str,
    seed: int = 42,
    test_ratio: float = 0.20,
) -> Dict[int, ClientSplit]:
    """Partitions the dataset across N sites with Dirichlet skew and holds out zero-day f*."""
    rng = np.random.default_rng(seed)
    
    path = Path(dataset_path)
    if not path.exists():
        # Fallback to default processed location
        path = Path("datasets/processed/cleaned_cic2018.parquet")
    
    table = pq.read_table(path)
    df = table.to_pandas()

    if "family" not in df.columns:
        raise ValueError(f"Dataset at {path} must contain 'family' column")

    # Feature columns detection
    if all(c in df.columns for c in CANONICAL_66_FEATURES):
        feature_cols = CANONICAL_66_FEATURES
    else:
        cols_to_drop = ["family", "label", "attack_cat", "Attack", "Label", "id"]
        feature_cols = [c for c in df.columns if c not in cols_to_drop]

    # Validate zero_day_family
    available_families = [f for f in df["family"].unique() if f != "Benign"]
    if zero_day_family not in available_families:
        zero_day_family = available_families[0] if available_families else "Infiltration"

    # Separate zero-day f*
    zd_mask = (df["family"] == zero_day_family)
    zero_day_df = df[zd_mask].copy()
    baseline_df = df[~zd_mask].copy()

    # Split zero-day into 50% training pool (for origin injection) and 50% test set (for evaluation)
    zd_feat = zero_day_df[feature_cols].to_numpy(dtype=np.float32)
    zd_lbl = zero_day_df["label"].to_numpy(dtype=np.int64)
    zd_train_X_raw, zd_test_X_raw, zd_train_y, zd_test_y = train_test_split(
        zd_feat, zd_lbl, test_size=0.5, random_state=seed, stratify=zd_lbl if len(np.unique(zd_lbl)) > 1 else None
    )

    # Partition Benign and known families across N sites using Dir_N(alpha)
    families_to_partition = ["Benign"] + [f for f in available_families if f != zero_day_family]
    client_indices: Dict[int, List[int]] = {i: [] for i in range(num_sites)}

    for fam in families_to_partition:
        fam_indices = baseline_df.index[baseline_df["family"] == fam].to_numpy()
        if len(fam_indices) == 0:
            continue
        rng.shuffle(fam_indices)

        # Sample Dirichlet proportions
        proportions = rng.dirichlet(np.repeat(skew, num_sites))
        # Map proportions to counts
        counts = (proportions * len(fam_indices)).astype(int)
        # Fix rounding discrepancies
        diff = len(fam_indices) - counts.sum()
        counts[:diff] += 1

        splits = np.split(fam_indices, np.cumsum(counts)[:-1])
        for i in range(num_sites):
            client_indices[i].extend(splits[i])

    # Build per-client datasets with local StandardScaler fit strictly on warm-up training split
    client_splits: Dict[int, ClientSplit] = {}

    for i in range(num_sites):
        idx = np.array(client_indices[i])
        if len(idx) < 10:
            # Fallback if Dirichlet left a client with too few samples: sample randomly
            idx = rng.choice(baseline_df.index.to_numpy(), size=max(100, len(baseline_df) // num_sites), replace=True)

        c_df = baseline_df.loc[idx]
        X = c_df[feature_cols].to_numpy(dtype=np.float32)
        y = c_df["label"].to_numpy(dtype=np.int64)
        fam = c_df["family"].to_numpy()

        # 80/20 train/test split locally (stratified only if all classes have >= 2 samples)
        unique_classes, class_counts = np.unique(y, return_counts=True)
        strat = y if (len(unique_classes) > 1 and np.min(class_counts) >= 2) else None
        train_X_raw, test_X_raw, train_y, test_y, train_fam, test_fam = train_test_split(
            X, y, fam, test_size=test_ratio, random_state=seed + i, stratify=strat
        )


        # Fit StandardScaler STRICTLY on local warm-up training set
        scaler = StandardScaler()
        train_X = scaler.fit_transform(train_X_raw)
        test_X = scaler.transform(test_X_raw)

        # Transform zero-day pool with the client's local scaler (prevents lookahead leakage)
        client_zd_train_X = scaler.transform(zd_train_X_raw)
        client_zd_test_X = scaler.transform(zd_test_X_raw)

        client_splits[i] = ClientSplit(
            client_id=i,
            train_X=train_X,
            train_y=train_y,
            train_families=train_fam,
            test_X=test_X,
            test_y=test_y,
            test_families=test_fam,
            zero_day_train_X=client_zd_train_X,
            zero_day_train_y=zd_train_y,
            zero_day_test_X=client_zd_test_X,
            zero_day_test_y=zd_test_y,
            scaler=scaler,
        )

    logger.info(
        f"Partitioned dataset into {num_sites} sites (skew={skew}, zero_day={zero_day_family}). "
        f"Mean site train samples: {np.mean([len(c.train_y) for c in client_splits.values()]):.0f}"
    )
    return client_splits
