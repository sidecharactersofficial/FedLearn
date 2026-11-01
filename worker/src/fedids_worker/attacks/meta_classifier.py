"""Phase 3: Meta-Attack Classifiers & Table 3 Evaluation Suite.

Trains:
- Head 1: Origin Classifier (Multi-class XGBoost over {0..N-1} -> Top-1 and Top-3 accuracy)
- Head 2: Timing Regressor (Huber loss XGBoost regressor -> MAE = |t_hat - t0|)

Evaluates across 10 seeds:
- Forensic Mode (f* known)
- Real-Time Surrogate Mode (f* unseen)
Across Server (No SecAgg), Server (SecAgg), and Curious Peer.
Outputs exact numbers for Table 3.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from fedids_worker.attacks.feature_extractor import (
    extract_features_server_secagg,
    extract_features_server_unprotected,
)
from fedids_worker.attacks.shadow_generator import ShadowTrace, generate_single_shadow_run
from xgboost import XGBClassifier, XGBRegressor

logger = logging.getLogger("fedids_worker.attacks.meta_classifier")


def evaluate_table3_suite(
    dataset_path: Path | str = "datasets/processed/cleaned_cic2018.parquet",
    num_shadow_runs: int = 40,
    rounds: int = 50,
    num_sites: int = 10,
    seeds: int = 10,
    output_dir: Path = Path("runs"),
) -> pd.DataFrame:
    """Executes the full evaluation matrix for Table 3 across 10 seeds."""
    logger.info(f"Generating shadow traces and evaluating Table 3 suite across {seeds} seeds...")

    families = ["Infiltration", "Botnet", "FTP-BruteForce", "DoS/DDoS"]
    held_out_target = "Infiltration"
    surrogate_families = [f for f in families if f != held_out_target]

    # Pre-generate shadow pool traces
    shadow_traces_forensic: List[ShadowTrace] = []
    shadow_traces_surrogate: List[ShadowTrace] = []

    logger.info(f"Generating {num_shadow_runs} shadow runs for Forensic mode (family={held_out_target})...")
    for k in range(num_shadow_runs):
        trace = generate_single_shadow_run(
            run_id=f"shadow-forensic-{k}",
            dataset_path=dataset_path,
            num_sites=num_sites,
            rounds=rounds,
            zero_day_family=held_out_target,
            origin_site=k % num_sites,
            seed=1000 + k,
        )
        shadow_traces_forensic.append(trace)

    logger.info(f"Generating {num_shadow_runs} shadow runs for Surrogate mode (surrogate families)...")
    for k in range(num_shadow_runs):
        surr_fam = surrogate_families[k % len(surrogate_families)]
        trace = generate_single_shadow_run(
            run_id=f"shadow-surrogate-{k}",
            dataset_path=dataset_path,
            num_sites=num_sites,
            rounds=rounds,
            zero_day_family=surr_fam,
            origin_site=k % num_sites,
            seed=2000 + k,
        )
        shadow_traces_surrogate.append(trace)

    # Pre-generate target test traces
    target_test_traces: List[ShadowTrace] = []
    for s in range(seeds):
        trace = generate_single_shadow_run(
            run_id=f"target-test-{s}",
            dataset_path=dataset_path,
            num_sites=num_sites,
            rounds=rounds,
            zero_day_family=held_out_target,
            origin_site=s % num_sites,
            seed=5000 + s,
        )
        target_test_traces.append(trace)

    regimes = [
        ("Server (No SecAgg)", "unprotected"),
        ("Server (SecAgg)", "secagg"),
        ("Peer Client", "peer"),
    ]

    modes = [
        ("Forensic", shadow_traces_forensic),
        ("Surrogate", shadow_traces_surrogate),
    ]

    results_records = []

    for regime_name, regime_type in regimes:
        for mode_name, shadow_pool in modes:
            # Extract features for training pool
            train_X_origin, train_y_origin = [], []
            train_X_timing, train_y_timing = [], []

            for trace in shadow_pool:
                if regime_type == "unprotected":
                    c_feat, t_feat, orig, onset = extract_features_server_unprotected(trace)
                    # For origin classification: flatten client features (N * feat_dim)
                    train_X_origin.append(c_feat.flatten())
                    train_y_origin.append(orig)
                    train_X_timing.append(t_feat)
                    train_y_timing.append(onset)
                elif regime_type == "secagg":
                    c_feat, t_feat, orig, onset = extract_features_server_secagg(trace, peer_client_id=None)
                    train_X_origin.append(c_feat.flatten())
                    train_y_origin.append(orig)
                    train_X_timing.append(t_feat)
                    train_y_timing.append(onset)
                else:  # Peer Client
                    peer_id = (trace.origin_site + 1) % trace.num_sites
                    c_feat, t_feat, orig, onset = extract_features_server_secagg(trace, peer_client_id=peer_id)
                    train_X_origin.append(c_feat.flatten())
                    train_y_origin.append(orig)
                    train_X_timing.append(t_feat)
                    train_y_timing.append(onset)

            X_tr_orig = np.array(train_X_origin, dtype=np.float32)
            y_tr_orig = np.array(train_y_origin, dtype=np.int64)
            X_tr_time = np.array(train_X_timing, dtype=np.float32)
            y_tr_time = np.array(train_y_timing, dtype=np.float32)

            # Train Head 1 (Origin Classifier)
            clf = XGBClassifier(
                n_estimators=50,
                max_depth=4,
                learning_rate=0.1,
                random_state=42,
                eval_metric="mlogloss",
                objective="multi:softprob",
                num_class=num_sites,
            )
            clf.fit(X_tr_orig, y_tr_orig)


            # Train Head 2 (Timing Regressor)
            reg = XGBRegressor(
                n_estimators=50,
                max_depth=4,
                learning_rate=0.1,
                random_state=42,
                objective="reg:squarederror",
            )
            reg.fit(X_tr_time, y_tr_time)

            # Evaluate on 10 target evaluation runs
            top1_list = []
            top3_list = []
            timing_mae_list = []

            for s_idx, test_trace in enumerate(target_test_traces):
                if regime_type == "unprotected":
                    c_feat, t_feat, true_orig, true_onset = extract_features_server_unprotected(test_trace)
                elif regime_type == "secagg":
                    c_feat, t_feat, true_orig, true_onset = extract_features_server_secagg(test_trace, peer_client_id=None)
                else:
                    peer_id = (test_trace.origin_site + 1) % test_trace.num_sites
                    c_feat, t_feat, true_orig, true_onset = extract_features_server_secagg(test_trace, peer_client_id=peer_id)

                prob = clf.predict_proba(c_feat.flatten().reshape(1, -1))[0]
                pred_top1 = int(np.argmax(prob))
                # Top-3 predictions
                top3_preds = np.argsort(prob)[-3:]

                pred_onset = float(reg.predict(t_feat.reshape(1, -1))[0])
                mae = abs(pred_onset - true_onset)

                top1_hit = 100.0 if pred_top1 == true_orig else 0.0
                top3_hit = 100.0 if true_orig in top3_preds else 0.0

                top1_list.append(top1_hit)
                top3_list.append(top3_hit)
                timing_mae_list.append(mae)

                results_records.append({
                    "regime": regime_name,
                    "mode": mode_name,
                    "seed": s_idx,
                    "top1_acc": top1_hit,
                    "top3_acc": top3_hit,
                    "timing_mae": mae,
                })

            mean_top1 = np.mean(top1_list)
            mean_top3 = np.mean(top3_list)
            mean_mae = np.mean(timing_mae_list)
            logger.info(f"{regime_name} ({mode_name}) -> Top-1: {mean_top1:.1f}%, Top-3: {mean_top3:.1f}%, Timing MAE: {mean_mae:.2f}")

    # Add Analytical Random Guess Baseline
    for s_idx in range(seeds):
        results_records.append({
            "regime": "Random Guess Baseline",
            "mode": "Theoretical",
            "seed": s_idx,
            "top1_acc": 10.0,
            "top3_acc": 30.0,
            "timing_mae": 12.50,
        })

    df_results = pd.DataFrame(results_records)
    output_dir.mkdir(parents=True, exist_ok=True)
    table_path = output_dir / "table3_results.parquet"
    csv_path = output_dir / "table3_results.csv"

    pq.write_table(pa.Table.from_pandas(df_results), table_path)
    df_results.to_csv(csv_path, index=False)
    logger.info(f"Saved Table 3 evaluation metrics to {table_path} and {csv_path}")
    return df_results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate Attack Suite for Table 3")
    parser.add_argument("--dataset", type=Path, default=Path("datasets/processed/cleaned_cic2018.parquet"))
    parser.add_argument("--shadow-runs", type=int, default=20, help="Shadow runs per mode")
    parser.add_argument("--rounds", type=int, default=30)
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--output-dir", type=Path, default=Path("runs"))
    args = parser.parse_args()

    evaluate_table3_suite(
        dataset_path=args.dataset,
        num_shadow_runs=args.shadow_runs,
        rounds=args.rounds,
        seeds=args.seeds,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
