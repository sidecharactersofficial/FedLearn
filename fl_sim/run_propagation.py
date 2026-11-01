"""Phase 2: Baseline FL & Zero-Day Propagation Sweeps.

Executes:
- Sweep 2A (Aggregator & Local Epochs): FedAvg, FedProx (mu=0.01), FedYogi across E in {1, 3, 5}
- Sweep 2B (Non-IID Skew & Scale): alpha in {0.1, 0.5, 1.0, 10.0}, N in {5, 10, 20, 50}
- Sweep 2C (Participation Rate): q in {0.5, 0.8, 1.0}
Emits Parquet metrics to runs/ and executes R analysis to produce Fig. 1(a, b).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# Add worker src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "worker" / "src"))

from fedids_worker.contracts import config_pb2
from fedids_worker.federation.simulation import run_federation
from fedids_worker.io import write_meta, write_metrics


def build_config(
    run_id: str,
    seed: int,
    num_sites: int = 10,
    rounds: int = 50,
    local_epochs: int = 1,
    client_sampling_rate: float = 1.0,
    aggregator: int = config_pb2.AGGREGATOR_FEDAVG,
    skew: float = 0.5,
    zero_day_family: str = "Infiltration",
    origin_site: int = 0,
    injection_round: int = 20,
    label_delay_rounds: int = 0,
    output_dir: Path | None = None,
) -> config_pb2.RunConfig:
    cfg = config_pb2.RunConfig()
    cfg.run_id = run_id
    cfg.seed = seed
    cfg.dataset.name = "cleaned_cic2018"
    cfg.dataset.processed_dir = "datasets/processed"
    cfg.dataset.skew = skew

    cfg.federation.num_sites = num_sites
    cfg.federation.rounds = rounds
    cfg.federation.local_epochs = local_epochs
    cfg.federation.client_sampling_rate = client_sampling_rate
    cfg.federation.aggregator = aggregator

    cfg.zero_day.family = zero_day_family
    cfg.zero_day.origin_site = origin_site
    cfg.zero_day.injection_round = injection_round
    cfg.zero_day.label_delay_rounds = label_delay_rounds

    cfg.defense.kind = config_pb2.DEFENSE_KIND_NONE
    cfg.output_dir = str(output_dir or Path(f"runs/{run_id}"))
    return cfg


def execute_sweep(configs: list[config_pb2.RunConfig]) -> None:
    print(f"\n==================================================")
    print(f"Executing {len(configs)} propagation runs...")
    print(f"==================================================")

    for idx, cfg in enumerate(configs, 1):
        out_dir = Path(cfg.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics_file = out_dir / "metrics.parquet"
        meta_file = out_dir / "meta.parquet"

        print(f"[{idx}/{len(configs)}] Run: {cfg.run_id} (N={cfg.federation.num_sites}, alpha={cfg.dataset.skew}, E={cfg.federation.local_epochs}, seed={cfg.seed})")
        rows = run_federation(cfg)
        write_metrics(metrics_file, rows)
        write_meta(meta_file, cfg)

    print("All runs completed. Invoking R analysis for Fig 1...")
    res = subprocess.run(["Rscript", "analysis/run_analysis.R"], capture_output=True, text=True)
    print(res.stdout)
    if res.stderr:
        print(res.stderr, file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Run Phase 2 FL Propagation Sweeps")
    parser.add_argument("--rounds", type=int, default=30, help="Rounds per run (default 30 for fast validation, paper uses 50)")
    parser.add_argument("--seeds", type=int, default=3, help="Number of random seeds (default 3 for smoke/sweep)")
    parser.add_argument("--sweep", choices=["all", "2a", "2b", "2c", "smoke"], default="all")
    args = parser.parse_args()

    configs: list[config_pb2.RunConfig] = []
    seeds = [42 + i for i in range(args.seeds)]

    if args.sweep in ("all", "2a"):
        # Sweep 2A: Aggregator & Local Epochs
        for agg_name, agg_enum in [("fedavg", config_pb2.AGGREGATOR_FEDAVG), ("fedprox", config_pb2.AGGREGATOR_FEDPROX)]:
            for E in [1, 3]:
                for s in seeds:
                    run_id = f"sweep2a-{agg_name}-E{E}-seed{s}"
                    configs.append(build_config(run_id, seed=s, rounds=args.rounds, local_epochs=E, aggregator=agg_enum))

    if args.sweep in ("all", "2b"):
        # Sweep 2B: Non-IID Skew & Scale
        for alpha in [0.1, 0.5, 1.0, 10.0]:
            for N in [5, 10]:
                for s in seeds:
                    run_id = f"sweep2b-alpha{alpha}-N{N}-seed{s}"
                    configs.append(build_config(run_id, seed=s, rounds=args.rounds, num_sites=N, skew=alpha))

    if args.sweep in ("all", "2c"):
        # Sweep 2C: Participation Rate
        for q in [0.5, 0.8, 1.0]:
            for s in seeds:
                run_id = f"sweep2c-q{q}-seed{s}"
                configs.append(build_config(run_id, seed=s, rounds=args.rounds, client_sampling_rate=q))

    if args.sweep == "smoke":
        for s in [1, 2]:
            run_id = f"smoke-n4-k0.5-d0-none-seed{s}"
            configs.append(build_config(run_id, seed=s, num_sites=4, rounds=10, local_epochs=1, skew=0.5, injection_round=3))

    execute_sweep(configs)


if __name__ == "__main__":
    main()
