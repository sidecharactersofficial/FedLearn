import pytest

from fedids_worker.settings import SettingsError, load_settings

GOOD = {
    "APP_ENVIRONMENT": "development",
    "APP_DEBUG": "true",
    "LOG_LEVEL": "debug",
    "DATASETS_DIR": "./datasets",
    "RUNS_DIR": "./runs",
}


def test_valid_settings():
    s = load_settings(GOOD)
    assert s.app_debug is True and s.app_environment == "development"


def test_missing_variable_fails_fast():
    env = {k: v for k, v in GOOD.items() if k != "RUNS_DIR"}
    with pytest.raises(SettingsError, match="RUNS_DIR"):
        load_settings(env)


@pytest.mark.parametrize("bad", ["1", "yes", "on", "True"])
def test_boolean_accepts_only_true_false(bad):
    with pytest.raises(SettingsError):
        load_settings({**GOOD, "APP_DEBUG": bad})
