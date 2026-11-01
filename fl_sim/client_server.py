"""Client and Server Routines for Federated Learning Simulation (Phase 2 & Phase 4)."""

import sys
from pathlib import Path

# Add worker src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "worker" / "src"))

from fedids_worker.federation.simulation import (
    apply_client_dp,
    compute_metrics,
    run_federation,
    train_client_epoch,
)

__all__ = [
    "run_federation",
    "compute_metrics",
    "train_client_epoch",
    "apply_client_dp",
]
