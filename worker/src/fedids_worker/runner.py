"""Worker entry point: RunConfig in, RunResult + metrics.parquet out."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from fedids_worker.config import load_run_config
from fedids_worker.contracts import result_pb2
from fedids_worker.federation.simulation import run_federation
from fedids_worker.io import write_meta, write_metrics, write_result
from fedids_worker.settings import load_settings

log = logging.getLogger("fedids_worker")


def run(config_path: Path) -> int:
    settings = load_settings()  # fail fast on bad environment
    logging.basicConfig(level=settings.log_level.upper().replace("WARN", "WARNING"))

    cfg = load_run_config(config_path)  # fail fast on bad config
    out = Path(cfg.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    result = result_pb2.RunResult(
        run_id=cfg.run_id,
        git_commit=settings.git_commit,
        image_digest=settings.image_digest,
    )
    try:
        rows = run_federation(cfg)
        metrics_path = out / "metrics.parquet"
        write_metrics(metrics_path, rows)
        meta_path = out / "meta.parquet"
        write_meta(meta_path, cfg)
        result.meta_path = str(meta_path)
        result.status = result_pb2.RUN_STATUS_SUCCEEDED
        result.metrics_path = str(metrics_path)
        result.summary["rows"] = float(len(rows))
    except Exception as exc:  # recorded in the contract, then re-raised as exit code
        log.exception("run failed")
        result.status = result_pb2.RUN_STATUS_FAILED
        result.error_message = str(exc)

    write_result(out / "result.pb", result)
    return 0 if result.status == result_pb2.RUN_STATUS_SUCCEEDED else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fedids_worker")
    parser.add_argument("--config", required=True, type=Path, help="path to RunConfig (.pb)")
    args = parser.parse_args(argv)
    return run(args.config)


if __name__ == "__main__":
    sys.exit(main())
