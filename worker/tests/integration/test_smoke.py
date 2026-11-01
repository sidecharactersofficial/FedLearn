"""End-to-end smoke test: RunConfig.pb -> worker -> result.pb + metrics.parquet."""

import pyarrow.parquet as pq

from fedids_worker.contracts import config_pb2, result_pb2
from fedids_worker.runner import run


def test_worker_smoke(tmp_path, monkeypatch):
    for k, v in {
        "APP_ENVIRONMENT": "development",
        "APP_DEBUG": "true",
        "LOG_LEVEL": "info",
        "DATASETS_DIR": str(tmp_path / "datasets"),
        "RUNS_DIR": str(tmp_path / "runs"),
    }.items():
        monkeypatch.setenv(k, v)

    out = tmp_path / "runs" / "smoke"
    cfg = config_pb2.RunConfig(run_id="smoke", seed=7, output_dir=str(out))
    cfg.federation.num_sites = 4
    cfg.federation.rounds = 8
    cfg.federation.client_sampling_rate = 1.0
    cfg.zero_day.origin_site = 0
    cfg.zero_day.injection_round = 2
    cfg_path = tmp_path / "config.pb"
    cfg_path.write_bytes(cfg.SerializeToString())

    assert run(cfg_path) == 0

    result = result_pb2.RunResult()
    result.ParseFromString((out / "result.pb").read_bytes())
    assert result.status == result_pb2.RUN_STATUS_SUCCEEDED

    meta = pq.read_table(out / "meta.parquet")
    assert meta.num_rows == 1 and meta.column("seed")[0].as_py() == 7

    table = pq.read_table(out / "metrics.parquet")
    assert table.num_rows >= 4 * 8
    assert set(table.column_names) == {"run_id", "round", "site", "metric", "value"}

