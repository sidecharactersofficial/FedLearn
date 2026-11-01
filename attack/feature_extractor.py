"""Attack Suite: Spatio-Temporal Feature Extractor CLI wrapper (Phase 3)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "worker" / "src"))

from fedids_worker.attacks.feature_extractor import (
    extract_features_server_secagg,
    extract_features_server_unprotected,
)

__all__ = [
    "extract_features_server_unprotected",
    "extract_features_server_secagg",
]
