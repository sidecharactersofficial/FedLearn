mod runner;
mod settings;
mod sweep;

/// Generated protobuf bindings (see build.rs).
pub mod pb {
    pub mod fedids {
        pub mod v1 {
            include!(concat!(env!("OUT_DIR"), "/fedids.v1.rs"));
        }
    }
}

use std::path::PathBuf;

use anyhow::Result;
use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "fedids-orchestrator", version, about = "Experiment orchestrator")]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand)]
enum Command {
    /// Expand a sweep spec into runs and execute them.
    Run {
        #[arg(long)]
        sweep: PathBuf,
    },
    /// Expand a sweep spec and print the run ids without executing.
    Plan {
        #[arg(long)]
        sweep: PathBuf,
    },
}

fn main() -> Result<()> {
    // Fail fast on bad environment before doing anything else.
    let settings = settings::Settings::from_env()?;
    tracing_subscriber::fmt()
        .with_env_filter(settings.log_level.as_str())
        .init();

    let cli = Cli::parse();
    match cli.command {
        Command::Run { sweep } => {
            let spec = sweep::SweepSpec::load(&sweep)?;
            let configs = spec.expand(&settings.runs_dir, &settings.datasets_dir)?;
            tracing::info!(runs = configs.len(), "expanded sweep");
            runner::run_all(&settings, configs)
        }
        Command::Plan { sweep } => {
            let spec = sweep::SweepSpec::load(&sweep)?;
            for cfg in spec.expand(&settings.runs_dir, &settings.datasets_dir)? {
                println!("{}", cfg.run_id);
            }
            Ok(())
        }
    }
}
