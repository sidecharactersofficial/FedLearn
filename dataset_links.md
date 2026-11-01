# Benchmark Dataset Links & Integrity Anchors

This document provides external references, download origins, and authoritative cryptographic anchors for the four network intrusion detection benchmarks evaluated in the paper.

---

## Authoritative Dataset Checksums (SHA-256)

All experimental sweeps read the preprocessed parquet tensors located under `datasets/processed/`:

| Dataset | Preprocessed Tensor Path | Rows | Features | SHA-256 Digest |
| :--- | :--- | :---: | :---: | :--- |
| **CSE-CIC-IDS2018** | `datasets/processed/cleaned_cic2018.parquet` | 100,000 | 66 | `4cac41d9ecfc0088aeca6304ba70ac3f92fb7fcae4cbfbc67f9f1f9d8304ec11` |
| **ToN-IoT** | `datasets/processed/cleaned_ton_iot.parquet` | 60,000 | 41 | `444c76152c81cdaae7ebc18c16be40b3930aa68294c3dba2c14884e4022c3655` |
| **UNSW-NB15** | `datasets/processed/cleaned_unsw_nb15.parquet` | 82,332 | 39 | `efcb21679a32e10be9d7efe6f7265509b23d2ac181ffab053ae54c1e0e821ed1` |
| **NSL-KDD** | `datasets/processed/cleaned_nsl_kdd.parquet` | 125,973 | 38 | `ab3abf9d8753a8616d808c9de077627caca44e4b23f4b92b58a0428593a53d95` |

### Integrity Verification Command

```bash
sha256sum -c manifest/dataset_sha256.txt
# or
python3 verification/verify_datasets.py
```

---

## Dataset Descriptions & Public Sources

### 1. CSE-CIC-IDS2018
- **Source:** Canadian Institute for Cybersecurity (UNB / AWS Collaborative Security).
- **URL:** [https://www.unb.ca/cic/datasets/ids-2018.html](https://www.unb.ca/cic/datasets/ids-2018.html)
- **Attack Macro-Families:** `FTP-BruteForce`, `Botnet`, `DoS/DDoS`, `Infiltration`.
- **Schema:** 66 bidirectional flow statistical features; IP/port 5-tuples removed to prevent trivial shortcut learning; MinMax normalized to $[0, 1]$.

### 2. ToN-IoT
- **Source:** Cyber Range Lab, UNSW Canberra at the Australian Defence Force Academy.
- **URL:** [https://research.unsw.edu.au/projects/toniot-datasets](https://research.unsw.edu.au/projects/toniot-datasets)
- **Attack Macro-Families:** `DoS / DDoS`, `Scanning / Recon`, `Ransomware / Backdoor`.
- **Schema:** 41 telemetry features covering industrial protocols, network socket state, and packet entropy.

### 3. UNSW-NB15
- **Source:** Cyber Range Lab, Australian Centre for Cyber Security (ACCS).
- **URL:** [https://research.unsw.edu.au/projects/unsw-nb15-dataset](https://research.unsw.edu.au/projects/unsw-nb15-dataset)
- **Attack Macro-Families:** `Generic`, `DoS`, `Reconnaissance`, `Fuzzers`, `Exploits`.
- **Schema:** 39 numeric features; flow duration, TTL, packet timing dynamics; MinMax scaled.

### 4. NSL-KDD
- **Source:** University of New Brunswick (refined DARPA/KDD Cup 99).
- **URL:** [https://www.unb.ca/cic/datasets/nsl.html](https://www.unb.ca/cic/datasets/nsl.html)
- **Attack Macro-Families:** `DoS`, `Probe`, `U2R`, `R2L`.
- **Schema:** 38 continuous and discrete connection metrics.
