"""Writers for the worker's outputs (Parquet metrics + RunResult proto)."""

from __future__ import annotations

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from fedids_worker.contracts import result_pb2

METRICS_SCHEMA = pa.schema(
    [
        ("run_id", pa.string()),
        ("round", pa.uint32()),
        ("site", pa.int32()),  # -1 = global
        ("metric", pa.string()),
        ("value", pa.float64()),
    ]
)


def write_metrics(path: Path, rows: list[dict]) -> None:
    table = pa.Table.from_pylist(rows, schema=METRICS_SCHEMA)
    pq.write_table(table, path)


def write_result(path: Path, result: "result_pb2.RunResult") -> None:
    Path(path).write_bytes(result.SerializeToString())


def write_meta(path: Path, cfg) -> None:
    """Flatten RunConfig into one Parquet row so R needs no protobuf dependency."""
    row = {
        "run_id": cfg.run_id,
        "seed": int(cfg.seed),
        "dataset": cfg.dataset.name,
        "skew": float(cfg.dataset.skew),
        "num_sites": int(cfg.federation.num_sites),
        "rounds": int(cfg.federation.rounds),
        "local_epochs": int(cfg.federation.local_epochs),
        "client_sampling_rate": float(cfg.federation.client_sampling_rate),
        "aggregator": int(cfg.federation.aggregator),
        "zero_day_family": cfg.zero_day.family,
        "origin_site": int(cfg.zero_day.origin_site),
        "injection_round": int(cfg.zero_day.injection_round),
        "label_delay_rounds": int(cfg.zero_day.label_delay_rounds),
        "defense_kind": int(cfg.defense.kind),
        "epsilon": float(cfg.defense.epsilon),
    }
    pq.write_table(pa.Table.from_pylist([row]), path)
