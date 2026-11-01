//! Sweep spec (human-authored TOML) -> RunConfig protobuf messages.

use std::{fs, path::Path};

use anyhow::{bail, Context, Result};
use serde::Deserialize;

use crate::pb::fedids::v1::{
    Aggregator, DatasetConfig, DefenseConfig, DefenseKind, FederationConfig, RunConfig,
    ZeroDayConfig,
};

#[derive(Debug, Deserialize)]
pub struct DefenseSpec {
    pub kind: String,
    #[serde(default)]
    pub epsilon: f64,
    #[serde(default)]
    pub delta: f64,
    #[serde(default)]
    pub clip_norm: f64,
    #[serde(default)]
    pub release_delay_rounds: u32,
    #[serde(default)]
    pub release_threshold_sites: u32,
}

#[derive(Debug, Deserialize)]
pub struct SweepSpec {
    pub name: String,
    pub dataset: String,
    pub rounds: u32,
    pub local_epochs: u32,
    pub client_sampling_rate: f64,
    pub aggregator: String,
    pub zero_day_family: String,
    pub origin_site: u32,
    pub injection_round: u32,
    pub label_delay_rounds: u32,
    pub seeds: Vec<u64>,
    pub num_sites: Vec<u32>,
    pub skew: Vec<f64>,
    pub defenses: Vec<DefenseSpec>,
}

fn parse_aggregator(s: &str) -> Result<Aggregator> {
    Ok(match s {
        "fedavg" => Aggregator::Fedavg,
        "fedprox" => Aggregator::Fedprox,
        "fedadam" => Aggregator::Fedadam,
        "fedyogi" => Aggregator::Fedyogi,
        other => bail!("unknown aggregator: {other}"),
    })
}


fn parse_defense(s: &str) -> Result<DefenseKind> {
    Ok(match s {
        "none" => DefenseKind::None,
        "secure_aggregation" => DefenseKind::SecureAggregation,
        "client_dp" => DefenseKind::ClientDp,
        "delayed_release" => DefenseKind::DelayedRelease,
        "thresholded_release" => DefenseKind::ThresholdedRelease,
        other => bail!("unknown defense kind: {other}"),
    })
}

impl SweepSpec {
    pub fn load(path: &Path) -> Result<Self> {
        let text = fs::read_to_string(path).with_context(|| format!("reading {}", path.display()))?;
        toml::from_str(&text).with_context(|| format!("parsing {}", path.display()))
    }

    /// Cartesian product: seeds x num_sites x skew x defenses.
    pub fn expand(&self, runs_dir: &Path, datasets_dir: &Path) -> Result<Vec<RunConfig>> {
        let aggregator = parse_aggregator(&self.aggregator)?;
        let mut configs = Vec::new();

        for &seed in &self.seeds {
            for &n in &self.num_sites {
                if self.origin_site >= n {
                    bail!("origin_site {} must be < num_sites {}", self.origin_site, n);
                }
                for &skew in &self.skew {
                    for (i, d) in self.defenses.iter().enumerate() {
                        let kind = parse_defense(&d.kind)?;
                        let run_id = format!("{}-n{}-k{}-d{}-{}-seed{}", self.name, n, skew, i, d.kind, seed);
                        configs.push(RunConfig {
                            run_id: run_id.clone(),
                            seed,
                            dataset: Some(DatasetConfig {
                                name: self.dataset.clone(),
                                raw_dir: datasets_dir.join("raw").to_string_lossy().into_owned(),
                                processed_dir: datasets_dir.join("processed").to_string_lossy().into_owned(),
                                skew,
                            }),
                            federation: Some(FederationConfig {
                                num_sites: n,
                                rounds: self.rounds,
                                local_epochs: self.local_epochs,
                                client_sampling_rate: self.client_sampling_rate,
                                aggregator: aggregator as i32,
                            }),
                            zero_day: Some(ZeroDayConfig {
                                family: self.zero_day_family.clone(),
                                origin_site: self.origin_site,
                                injection_round: self.injection_round,
                                label_delay_rounds: self.label_delay_rounds,
                            }),
                            defense: Some(DefenseConfig {
                                kind: kind as i32,
                                epsilon: d.epsilon,
                                delta: d.delta,
                                clip_norm: d.clip_norm,
                                release_delay_rounds: d.release_delay_rounds,
                                release_threshold_sites: d.release_threshold_sites,
                            }),
                            output_dir: runs_dir.join(&run_id).to_string_lossy().into_owned(),
                        });
                    }
                }
            }
        }
        Ok(configs)
    }
}
