import pytest

from fedids_worker.config import ConfigError, validate_run_config
from fedids_worker.contracts import config_pb2


def make_config(**overrides):
    cfg = config_pb2.RunConfig(run_id="t", seed=1, output_dir="/tmp/t")
    cfg.federation.num_sites = 5
    cfg.federation.rounds = 10
    cfg.federation.client_sampling_rate = 1.0
    cfg.zero_day.origin_site = 1
    cfg.zero_day.injection_round = 2
    for k, v in overrides.items():
        obj, field = k.split("__")
        setattr(getattr(cfg, obj), field, v)
    return cfg


def test_valid_config_passes():
    validate_run_config(make_config())


def test_origin_site_out_of_range():
    with pytest.raises(ConfigError, match="origin_site"):
        validate_run_config(make_config(zero_day__origin_site=9))


def test_sampling_rate_bounds():
    with pytest.raises(ConfigError, match="sampling"):
        validate_run_config(make_config(federation__client_sampling_rate=0.0))
