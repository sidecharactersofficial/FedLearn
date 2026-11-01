"""FL-IDS Detector Backbones (Phase 2)."""

import sys
from pathlib import Path

# Add worker src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "worker" / "src"))

from fedids_worker.federation.models import (
    FlowAEHybrid,
    FlowCNN1D,
    FlowMLP,
    create_model,
)

__all__ = ["FlowMLP", "FlowCNN1D", "FlowAEHybrid", "create_model"]
