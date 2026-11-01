"""Load and validate a RunConfig contract."""

from __future__ import annotations

from pathlib import Path

from fedids_worker.contracts import config_pb2


class ConfigError(ValueError):
    pass


def load_run_config(path: Path) -> "config_pb2.RunConfig":
    cfg = config_pb2.RunConfig()
    cfg.ParseFromString(Path(path).read_bytes())
    validate_run_config(cfg)
    return cfg


def validate_run_config(cfg: "config_pb2.RunConfig") -> None:
    fed, zd = cfg.federation, cfg.zero_day
    problems: list[str] = []
    if not cfg.run_id:
        problems.append("run_id is empty")
    if fed.num_sites < 2:
        problems.append("federation.num_sites must be >= 2")
    if fed.rounds < 1:
        problems.append("federation.rounds must be >= 1")
    if not (0.0 < fed.client_sampling_rate <= 1.0):
        problems.append("federation.client_sampling_rate must be in (0, 1]")
    if zd.origin_site >= fed.num_sites:
        problems.append("zero_day.origin_site must be < federation.num_sites")
    if zd.injection_round >= fed.rounds:
        problems.append("zero_day.injection_round must be < federation.rounds")
    if cfg.defense.kind == config_pb2.DEFENSE_KIND_CLIENT_DP and cfg.defense.epsilon <= 0:
        problems.append("defense.epsilon must be > 0 for client DP")
    if not cfg.output_dir:
        problems.append("output_dir is empty")
    if problems:
        raise ConfigError("; ".join(problems))
