#!/usr/bin/env python3
"""50-Round Cross-Silo Federated Learning Run Across All 4 Datasets and All Families.

Executes full R=50 FL simulations across all 4 datasets:
1. CSE-CIC-IDS2018 (cicds): Botnet, Infiltration, FTP-BruteForce, DoS/DDoS
2. ToN-IoT (ton): Scanning / Recon, Ransomware / Backdoor, DoS / DDoS
3. UNSW-NB15 (usnsw): Exploits, Fuzzers, DoS, Reconnaissance, Generic
4. NSL-KDD: DoS, Probe, R2L, U2R

Calculates propagation delay tau_0.80, peak non-origin recall,
final non-origin recall, AUPC_20, and catastrophic forgetting,
logging all metrics to results/metrics/fl50_4datasets_summary.csv and
results/logs/fl50_4datasets.log for complete empirical reproducibility.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

# Add worker src to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "worker" / "src"))

import pandas as pd
from fedids_worker.contracts import config_pb2
from fedids_worker.federation.simulation import run_federation
from fedids_worker.io import write_meta, write_metrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_50fl_4datasets")

DATASET_FAMILIES = {
    "cleaned_cic2018": {
        "display_name": "CSE-CIC-IDS2018",
        "families": ["Botnet", "Infiltration", "FTP-BruteForce", "DoS/DDoS"],
    },
    "cleaned_ton_iot": {
        "display_name": "ToN-IoT",
        "families": ["Scanning / Recon", "Ransomware / Backdoor", "DoS / DDoS"],
    },
    "cleaned_unsw_nb15": {
        "display_name": "UNSW-NB15",
        "families": ["Exploits", "Fuzzers", "DoS", "Reconnaissance", "Generic"],
    },
    "cleaned_nsl_kdd": {
        "display_name": "NSL-KDD",
        "families": ["DoS", "Probe", "R2L", "U2R"],
    },
}


def run_50fl_suite(
    rounds: int = 50,
    seeds: list[int] = [42],
    skew: float = 0.5,
    num_sites: int = 10,
    local_epochs: int = 1,
    selected_datasets: list[str] | None = None,
    output_dir: Path | None = None,
) -> pd.DataFrame:
    out_dir = output_dir or (ROOT / "runs" / "fl50_4datasets")
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir = ROOT / "results" / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    summary_records = []
    datasets_to_run = selected_datasets or list(DATASET_FAMILIES.keys())

    print("\n" + "=" * 78)
    print(f"Executing 50-Round Cross-Dataset FL Suite Across All 4 Datasets & Families")
    print(f"Settings: Rounds={rounds}, Onset=20, Sites={num_sites}, Dirichlet alpha={skew}")
    print("=" * 78, flush=True)

    for ds_key in datasets_to_run:
        if ds_key not in DATASET_FAMILIES:
            continue
        ds_info = DATASET_FAMILIES[ds_key]
        ds_name = ds_info["display_name"]
        families = ds_info["families"]

        print(f"\n==================== DATASET: {ds_name} ({ds_key}) ====================")

        for fam in families:
            for seed in seeds:
                fam_clean = fam.lower().replace("/", "_").replace("-", "_").replace(" ", "_")
                ds_clean = ds_name.lower().replace("-", "_").replace(" ", "_")
                run_id = f"fl50_{ds_clean}_{fam_clean}_seed{seed}"

                # Check if already cached
                cached_metrics = out_dir / run_id / "metrics.parquet"
                if cached_metrics.exists():
                    try:
                        df_cached = pd.read_parquet(cached_metrics)
                        # Extract cached metrics
                        tau_080 = None
                        final_rec = 0.0
                        peak_rec = 0.0
                        aupc = 0.0
                        forgetting = 0.0
                        for _, row_c in df_cached.iterrows():
                            m = row_c["metric"]
                            v = row_c["value"]
                            rnd = row_c["round"]
                            if m == "mean_non_origin_zero_day_recall":
                                if v > peak_rec:
                                    peak_rec = v
                                if rnd == rounds:
                                    final_rec = v
                            elif m == "tau_0.80":
                                tau_080 = v
                            elif m == "aupc_20":
                                aupc = v
                            elif m == "catastrophic_forgetting" and rnd == rounds:
                                forgetting = v

                        rec = {
                            "dataset": ds_name,
                            "macro_family": fam,
                            "seed": seed,
                            "rounds": rounds,
                            "injection_round": 20,
                            "tau_0.80_rounds": tau_080 if tau_080 is not None else -1,
                            "final_non_origin_recall": round(final_rec, 4),
                            "peak_non_origin_recall": round(peak_rec, 4),
                            "aupc_20": round(aupc, 4),
                            "catastrophic_forgetting": round(forgetting, 4),
                            "runtime_seconds": 0.0,
                        }
                        summary_records.append(rec)
                        print(f"[CACHED] {ds_name} | {fam} (seed={seed}) -> tau_0.80={tau_080}, peak_rec={peak_rec:.3f}, final_rec={final_rec:.3f}", flush=True)
                        continue
                    except Exception as e:
                        logger.warning(f"Failed to read cached metrics for {run_id}: {e}")

                print(f"\n>>> Running 50 FL Rounds for [{ds_name}] Zero-Day [{fam}] (seed={seed})...", flush=True)

                cfg = config_pb2.RunConfig()
                cfg.run_id = run_id
                cfg.seed = seed
                cfg.dataset.name = ds_key
                cfg.dataset.processed_dir = "datasets/processed"
                cfg.dataset.skew = skew

                cfg.federation.num_sites = num_sites
                cfg.federation.rounds = rounds
                cfg.federation.local_epochs = local_epochs
                cfg.federation.client_sampling_rate = 1.0
                cfg.federation.aggregator = config_pb2.AGGREGATOR_FEDAVG

                cfg.zero_day.family = fam
                cfg.zero_day.origin_site = 0
                cfg.zero_day.injection_round = 20
                cfg.zero_day.label_delay_rounds = 0
                cfg.defense.kind = config_pb2.DEFENSE_KIND_NONE

                t_start = time.time()
                rows = run_federation(cfg)
                elapsed = time.time() - t_start

                # Extract metrics
                tau_080 = None
                final_rec = 0.0
                peak_rec = 0.0
                aupc = 0.0
                forgetting = 0.0

                for r in rows:
                    m = r.get("metric")
                    v = r.get("value", 0.0)
                    rnd = r.get("round", 0)

                    if m == "mean_non_origin_zero_day_recall":
                        if v > peak_rec:
                            peak_rec = v
                        if rnd == rounds:
                            final_rec = v
                    elif m == "tau_0.80":
                        tau_080 = v
                    elif m == "aupc_20":
                        aupc = v
                    elif m == "catastrophic_forgetting" and rnd == rounds:
                        forgetting = v

                rec = {
                    "dataset": ds_name,
                    "macro_family": fam,
                    "seed": seed,
                    "rounds": rounds,
                    "injection_round": 20,
                    "tau_0.80_rounds": tau_080 if tau_080 is not None else -1,
                    "final_non_origin_recall": round(final_rec, 4),
                    "peak_non_origin_recall": round(peak_rec, 4),
                    "aupc_20": round(aupc, 4),
                    "catastrophic_forgetting": round(forgetting, 4),
                    "runtime_seconds": round(elapsed, 2),
                }
                summary_records.append(rec)

                print(f"    Completed in {elapsed:.1f}s | tau_0.80 = {tau_080} rounds | peak recall = {peak_rec:.3f} | final recall = {final_rec:.3f}", flush=True)

                # Persist raw parquet metrics
                run_out = out_dir / run_id
                run_out.mkdir(parents=True, exist_ok=True)
                write_metrics(run_out / "metrics.parquet", rows)
                write_meta(run_out / "meta.parquet", cfg)

    df_summary = pd.DataFrame(summary_records)
    csv_path = metrics_dir / "fl50_4datasets_summary.csv"
    df_summary.to_csv(csv_path, index=False)
    print(f"\n[Artifact Created] Cross-Dataset Summary saved to {csv_path}")
    print(df_summary.to_string(index=False), flush=True)
    return df_summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run 50-round FL across all 4 datasets and all families")
    parser.add_argument("--rounds", type=int, default=50, help="FL rounds (default 50)")
    parser.add_argument("--seeds", type=int, default=1, help="Number of seeds (default 1)")
    parser.add_argument("--dataset", type=str, default=None, help="Specific dataset key to run (optional)")
    args = parser.parse_args()

    seeds = [42 + i for i in range(args.seeds)]
    selected = [args.dataset] if args.dataset else None
    run_50fl_suite(rounds=args.rounds, seeds=seeds, selected_datasets=selected)
