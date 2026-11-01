#!/usr/bin/env python3
"""Generate EuroS&P Publication-Grade Cross-Dataset 50-Round FL Trajectory Plot.

Reads raw round-by-round metrics from runs/fl50_4datasets/ across all 4 datasets:
- Panel (a): CSE-CIC-IDS2018 (Botnet, Infiltration, FTP-BruteForce, DoS/DDoS)
- Panel (b): ToN-IoT (Scanning / Recon, Ransomware / Backdoor, DoS / DDoS)
- Panel (c): UNSW-NB15 (Exploits, Fuzzers, DoS, Reconnaissance, Generic)
- Panel (d): NSL-KDD (DoS, Probe, R2L, U2R)

Exports vector PDF to paper/fig_crossdataset_fl50.pdf and results/figures/fig_crossdataset_fl50.pdf
with pad_inches=0.08 and bbox_inches='tight'.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch, Rectangle
import numpy as np
import pandas as pd
from pathlib import Path

# Configure publication typography matching IEEEtran
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif", "Times"],
    "mathtext.fontset": "stix",
    "font.size": 8.5,
    "axes.labelsize": 9,
    "axes.titlesize": 9.5,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 7.0,
    "figure.titlesize": 10.5,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})

ROOT = Path(__file__).resolve().parent.parent
RUNS_DIR = ROOT / "runs" / "fl50_4datasets"
PAPER_DIR = ROOT / "paper"
RESULTS_FIG = ROOT / "results" / "figures"
RESULTS_FIG.mkdir(parents=True, exist_ok=True)

# Dataset configs: title, runs, and zoom limits for the apex before plateau
DATASETS = [
    {
        "title": "(a) CSE-CIC-IDS2018 (Enterprise Flow Benchmark)",
        "runs": {
            "Botnet": ("fl50_cse_cic_ids2018_botnet_seed42", "#1f77b4", "-"),
            "Infiltration": ("fl50_cse_cic_ids2018_infiltration_seed42", "#2ca02c", "--"),
            "FTP-BruteForce": ("fl50_cse_cic_ids2018_ftp_bruteforce_seed42", "#d95f02", "-."),
            "DoS/DDoS": ("fl50_cse_cic_ids2018_dos_ddos_seed42", "#7570b3", ":"),
        },
        "x_zoom": (22.5, 28.5),
        "y_zoom": (0.70, 0.98),
    },
    {
        "title": "(b) ToN-IoT (IoT/IIoT Network Benchmark)",
        "runs": {
            "DoS / DDoS": ("fl50_ton_iot_dos___ddos_seed42", "#e41a1c", "-"),
            "Ransomware / Backdoor": ("fl50_ton_iot_ransomware___backdoor_seed42", "#377eb8", "--"),
            "Scanning / Recon": ("fl50_ton_iot_scanning___recon_seed42", "#4daf4a", "-."),
        },
        "x_zoom": (22.5, 28.5),
        "y_zoom": (0.70, 0.98),
    },
    {
        "title": "(c) UNSW-NB15 (Synthetic & Realistic Traffic)",
        "runs": {
            "Generic": ("fl50_unsw_nb15_generic_seed42", "#984ea3", "-"),
            "DoS": ("fl50_unsw_nb15_dos_seed42", "#ff7f00", "--"),
            "Reconnaissance": ("fl50_unsw_nb15_reconnaissance_seed42", "#377eb8", "-."),
            "Exploits": ("fl50_unsw_nb15_exploits_seed42", "#4daf4a", ":"),
            "Fuzzers": ("fl50_unsw_nb15_fuzzers_seed42", "#e41a1c", (0, (3, 1, 1, 1))),
        },
        "x_zoom": (22.5, 28.5),
        "y_zoom": (0.70, 0.98),
    },
    {
        "title": "(d) NSL-KDD (Classic Multi-Class Intrusion)",
        "runs": {
            "DoS": ("fl50_nsl_kdd_dos_seed42", "#e41a1c", "-"),
            "U2R": ("fl50_nsl_kdd_u2r_seed42", "#377eb8", "--"),
            "R2L": ("fl50_nsl_kdd_r2l_seed42", "#4daf4a", "-."),
            "Probe": ("fl50_nsl_kdd_probe_seed42", "#ff7f00", ":"),
        },
        "x_zoom": (22.5, 29.0),
        "y_zoom": (0.65, 0.98),
    },
]


def load_trajectory(run_id: str) -> tuple[np.ndarray, np.ndarray]:
    p = RUNS_DIR / run_id / "metrics.parquet"
    if not p.exists():
        # Fallback to alternate naming if needed
        alt_id = run_id.replace("cse_cic_ids2018_", "")
        p = RUNS_DIR / alt_id / "metrics.parquet"

    if not p.exists():
        return np.arange(1, 51), np.zeros(50)

    df = pd.read_parquet(p)
    df_sub = df[df["metric"] == "mean_non_origin_zero_day_recall"].sort_values("round")
    rounds = df_sub["round"].to_numpy()
    recalls = df_sub["value"].to_numpy()
    return rounds, recalls


def generate_plot():
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.0), dpi=300)
    axes = axes.flatten()

    for idx, ds_cfg in enumerate(DATASETS):
        ax = axes[idx]
        title = ds_cfg["title"]
        runs = ds_cfg["runs"]
        xz = ds_cfg["x_zoom"]
        yz = ds_cfg["y_zoom"]

        # Inset axes positioned in upper-left quadrant
        # [x0, y0, width, height] in axes fraction coordinates
        axins = ax.inset_axes([0.08, 0.46, 0.29, 0.42])

        for label, (run_id, color, style) in runs.items():
            rnds, vals = load_trajectory(run_id)
            # Main plot curve
            ax.plot(rnds, vals, label=label, color=color, linestyle=style, lw=1.6)
            # Inset curve with discrete round markers
            axins.plot(rnds, vals, color=color, linestyle=style, lw=1.3,
                       marker="o", markersize=2.8, alpha=0.9)

        # Main plot threshold and injection lines
        ax.axvline(20, color="gray", linestyle=":", lw=1.0, alpha=0.8)
        ax.axhline(0.80, color="crimson", linestyle="--", lw=0.9, alpha=0.7)

        # Inset threshold line
        axins.axhline(0.80, color="crimson", linestyle="--", lw=0.8, alpha=0.7)

        # Zoom limits and tick formatting
        axins.set_xlim(xz)
        axins.set_ylim(yz)
        axins.tick_params(axis="both", which="major", labelsize=6.2, pad=1)
        axins.xaxis.set_major_locator(plt.MultipleLocator(2))
        axins.yaxis.set_major_locator(plt.MultipleLocator(0.1))
        axins.grid(True, linestyle=":", alpha=0.45)

        # Style inset border matching the orange callout
        for spine in axins.spines.values():
            spine.set_edgecolor("#e66101")
            spine.set_linewidth(1.1)

        # Draw zoom rectangle on parent axes
        rect = Rectangle((xz[0], yz[0]), xz[1] - xz[0], yz[1] - yz[0],
                         edgecolor="#e66101", facecolor="none", lw=1.2, zorder=5)
        ax.add_patch(rect)

        # Callout connector lines connecting inset to parent zoom box
        cp1 = ConnectionPatch(xyA=(1.0, 1.0), coordsA=axins.transAxes,
                              xyB=(xz[0], yz[1]), coordsB=ax.transData,
                              color="#e66101", linestyle="--", linewidth=0.9, alpha=0.85)
        cp2 = ConnectionPatch(xyA=(1.0, 0.0), coordsA=axins.transAxes,
                              xyB=(xz[0], yz[0]), coordsB=ax.transData,
                              color="#e66101", linestyle="--", linewidth=0.9, alpha=0.85)
        ax.add_artist(cp1)
        ax.add_artist(cp2)

        ax.set_xlim(1, 50)
        ax.set_ylim(-0.02, 1.05)
        ax.set_title(title, fontsize=8.8, fontweight="bold", pad=4)
        ax.set_xlabel("Communication Round ($t$)", fontsize=8.2)
        ax.set_ylabel("Non-Origin Zero-Day Recall", fontsize=8.2)
        ax.grid(True, linestyle="--", alpha=0.35)
        ax.legend(loc="lower right", framealpha=0.92, fontsize=6.8, handlelength=1.6)

    plt.tight_layout()

    out_paper_pdf = PAPER_DIR / "fig_crossdataset_fl50.pdf"
    out_paper_png = PAPER_DIR / "fig_crossdataset_fl50.png"
    out_results_pdf = RESULTS_FIG / "fig_crossdataset_fl50.pdf"
    out_results_png = RESULTS_FIG / "fig_crossdataset_fl50.png"

    fig.savefig(out_paper_pdf, format="pdf", bbox_inches="tight", pad_inches=0.08)
    fig.savefig(out_paper_png, format="png", dpi=300, bbox_inches="tight", pad_inches=0.08)
    fig.savefig(out_results_pdf, format="pdf", bbox_inches="tight", pad_inches=0.08)
    fig.savefig(out_results_png, format="png", dpi=300, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)

    print(f"Exported publication plot with zoomed insets to {out_paper_pdf} and {out_paper_png}")


if __name__ == "__main__":
    generate_plot()
