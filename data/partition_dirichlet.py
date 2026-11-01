"""Phase 1 CLI: Non-IID Dirichlet Partitioner & Zero-Day Holdout Generator.

Usage:
    python data/partition_dirichlet.py --alpha 0.5 --num_clients 10 --zero_day Infiltration
"""

import argparse
import sys
from pathlib import Path

# Add worker src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "worker" / "src"))

from fedids_worker.federation.partition import MACRO_FAMILIES, partition_dirichlet


def main():
    parser = argparse.ArgumentParser(description="Dirichlet Partitioner for FL-IDS")
    parser.add_argument("--dataset", type=Path, default=Path("datasets/processed/cleaned_cic2018.parquet"))
    parser.add_argument("--num_clients", type=int, default=10, help="Number of consortium clients N")
    parser.add_argument("--alpha", type=float, default=0.5, help="Dirichlet concentration parameter alpha")
    parser.add_argument(
        "--zero_day",
        type=str,
        default="Infiltration",
        choices=MACRO_FAMILIES,
        help="Held-out zero-day attack family f*",
    )
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print(f"Partitioning {args.dataset} across {args.num_clients} sites with alpha={args.alpha}, zero_day={args.zero_day}")
    splits = partition_dirichlet(
        dataset_path=args.dataset,
        num_sites=args.num_clients,
        skew=args.alpha,
        zero_day_family=args.zero_day,
        seed=args.seed,
    )

    print("\nPartition Summary:")
    print(f"{'Site':<6} | {'Train Samples':<14} | {'Test Samples':<14} | {'Zero-Day Pool':<14}")
    print("-" * 55)
    for site_id, split in splits.items():
        print(
            f"{site_id:<6} | {len(split.train_y):<14} | {len(split.test_y):<14} | {len(split.zero_day_train_y):<14}"
        )
    print("\nDeterministic partition completed successfully.")


if __name__ == "__main__":
    main()
