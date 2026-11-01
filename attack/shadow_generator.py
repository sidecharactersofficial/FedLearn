"""Attack Suite: Shadow Generator CLI wrapper (Phase 3)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "worker" / "src"))

from fedids_worker.attacks.shadow_generator import (
    ShadowTrace,
    generate_single_shadow_run,
)

__all__ = ["ShadowTrace", "generate_single_shadow_run"]
