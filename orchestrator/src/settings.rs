//! Environment settings with fail-fast validation (Design Dungeons: env standards).

use std::{env, path::PathBuf};

use anyhow::{bail, Context, Result};

#[derive(Debug, Clone)]
pub struct Settings {
    pub app_environment: String,
    pub log_level: String,
    pub runs_dir: PathBuf,
    pub datasets_dir: PathBuf,
    pub worker_command: String,
    pub max_parallel_runs: usize,
}

fn required(key: &str) -> Result<String> {
    let value = env::var(key).with_context(|| format!("Missing required environment variable: {key}"))?;
    if value.is_empty() {
        bail!("Missing required environment variable: {key}");
    }
    Ok(value)
}

impl Settings {
    pub fn from_env() -> Result<Self> {
        let app_environment = required("APP_ENVIRONMENT")?;
        if !["development", "staging", "production"].contains(&app_environment.as_str()) {
            bail!("APP_ENVIRONMENT must be development, staging, or production");
        }
        let log_level = required("LOG_LEVEL")?;
        if !["debug", "info", "warn", "error"].contains(&log_level.as_str()) {
            bail!("LOG_LEVEL must be debug, info, warn, or error");
        }
        let max_parallel_runs: usize = required("MAX_PARALLEL_RUNS")?
            .parse()
            .context("MAX_PARALLEL_RUNS must be a positive integer")?;
        if max_parallel_runs == 0 {
            bail!("MAX_PARALLEL_RUNS must be a positive integer");
        }
        Ok(Self {
            app_environment,
            log_level,
            runs_dir: PathBuf::from(required("RUNS_DIR")?),
            datasets_dir: PathBuf::from(required("DATASETS_DIR")?),
            worker_command: required("WORKER_COMMAND")?,
            max_parallel_runs,
        })
    }
}
