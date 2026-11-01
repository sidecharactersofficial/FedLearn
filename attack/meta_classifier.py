"""Attack Suite: Meta-Attack Classifier & Table 3 Pipeline (Phase 3)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "worker" / "src"))

from fedids_worker.attacks.meta_classifier import evaluate_table3_suite, main

if __name__ == "__main__":
    main()
