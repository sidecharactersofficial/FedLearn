//! Run supervision: write config.pb, start the Python worker, read result.pb.

use std::{fs, path::Path, process::Command, thread};

use anyhow::{bail, Context, Result};
use prost::Message;

use crate::pb::fedids::v1::{RunConfig, RunResult, RunStatus};
use crate::settings::Settings;

pub fn run_all(settings: &Settings, configs: Vec<RunConfig>) -> Result<()> {
    let total = configs.len();
    let mut failed = 0usize;

    for chunk in configs.chunks(settings.max_parallel_runs) {
        let handles: Vec<_> = chunk
            .iter()
            .cloned()
            .map(|cfg| {
                let worker_command = settings.worker_command.clone();
                thread::spawn(move || run_one(&worker_command, &cfg))
            })
            .collect();

        for handle in handles {
            match handle.join() {
                Ok(Ok(())) => {}
                Ok(Err(e)) => {
                    tracing::error!("run failed: {e:#}");
                    failed += 1;
                }
                Err(_) => {
                    tracing::error!("run thread panicked");
                    failed += 1;
                }
            }
        }
    }

    if failed > 0 {
        bail!("{failed} of {total} runs failed");
    }
    tracing::info!(total, "all runs succeeded");
    Ok(())
}

fn run_one(worker_command: &str, cfg: &RunConfig) -> Result<()> {
    let out = Path::new(&cfg.output_dir);
    fs::create_dir_all(out)?;

    let config_path = out.join("config.pb");
    fs::write(&config_path, cfg.encode_to_vec())?;

    let mut parts = worker_command.split_whitespace();
    let program = parts.next().context("WORKER_COMMAND is empty")?;
    let status = Command::new(program)
        .args(parts)
        .arg("--config")
        .arg(&config_path)
        .status()
        .with_context(|| format!("failed to start worker for {}", cfg.run_id))?;

    let bytes = fs::read(out.join("result.pb"))
        .with_context(|| format!("worker wrote no result.pb for {}", cfg.run_id))?;
    let result = RunResult::decode(bytes.as_slice())?;

    if !status.success() || result.status != RunStatus::Succeeded as i32 {
        bail!("run {} failed: {}", cfg.run_id, result.error_message);
    }
    tracing::info!(run_id = %cfg.run_id, "run succeeded");
    Ok(())
}
