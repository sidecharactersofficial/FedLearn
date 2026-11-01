"""Import point for generated protobuf bindings.

Bindings are generated into ./gen by `make proto` (never edit them by hand).
The generated modules import each other as `fedids.v1...`, so ./gen must be
on sys.path.
"""

import sys
from pathlib import Path

_GEN = Path(__file__).parent / "gen"
if str(_GEN) not in sys.path:
    sys.path.insert(0, str(_GEN))

try:
    from fedids.v1 import config_pb2, observation_pb2, result_pb2  # noqa: E402
except ImportError as exc:  # fail fast with a clear message
    raise ImportError(
        "Protobuf bindings are missing. Run `make proto` from the repo root."
    ) from exc

__all__ = ["config_pb2", "observation_pb2", "result_pb2"]
