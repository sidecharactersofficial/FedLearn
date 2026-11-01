"""Environment settings with fail-fast validation (Design Dungeons: env standards).

Rules: required variables must be present; booleans accept only true/false.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_TIERS = {"development", "staging", "production"}
_LEVELS = {"debug", "info", "warn", "error"}


class SettingsError(RuntimeError):
    pass


def _require(env: dict[str, str], key: str) -> str:
    value = env.get(key)
    if value is None or value == "":
        raise SettingsError(f"Missing required environment variable: {key}")
    return value


def _bool(env: dict[str, str], key: str) -> bool:
    value = _require(env, key)
    if value not in ("true", "false"):
        raise SettingsError(f"{key} must be 'true' or 'false', got {value!r}")
    return value == "true"


@dataclass(frozen=True)
class Settings:
    app_environment: str
    app_debug: bool
    log_level: str
    datasets_dir: Path
    runs_dir: Path
    git_commit: str
    image_digest: str


def load_settings(env: dict[str, str] | None = None) -> Settings:
    env = dict(os.environ) if env is None else env
    tier = _require(env, "APP_ENVIRONMENT")
    if tier not in _TIERS:
        raise SettingsError(f"APP_ENVIRONMENT must be one of {sorted(_TIERS)}, got {tier!r}")
    level = _require(env, "LOG_LEVEL")
    if level not in _LEVELS:
        raise SettingsError(f"LOG_LEVEL must be one of {sorted(_LEVELS)}, got {level!r}")
    return Settings(
        app_environment=tier,
        app_debug=_bool(env, "APP_DEBUG"),
        log_level=level,
        datasets_dir=Path(_require(env, "DATASETS_DIR")),
        runs_dir=Path(_require(env, "RUNS_DIR")),
        git_commit=env.get("GIT_COMMIT", "unknown"),
        image_digest=env.get("IMAGE_DIGEST", "unknown"),
    )
