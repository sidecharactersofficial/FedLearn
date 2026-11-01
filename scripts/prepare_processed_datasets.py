#!/usr/bin/env python3
"""Prepare cleaned parquet files for UNSW-NB15, ToN-IoT, and NSL-KDD.

Conforms each dataset to the canonical schema:
- Numeric feature columns
- label: int64 (0 for Benign, 1 for Malicious)
- family: string (attack macro-family name, or 'Benign')
"""

import os
from pathlib import Path
import numpy as np
import pandas as pd

OUT_DIR = Path("datasets/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def prep_ton_iot():
    out_file = OUT_DIR / "cleaned_ton_iot.parquet"
    if out_file.exists():
        print(f"[ToN-IoT] Already exists at {out_file}")
        return
    
    raw_dir = Path(os.environ.get("RAW_DATA_DIR", ROOT / "datasets" / "raw"))
    raw_path = raw_dir / "ton_iot" / "NF-ToN-IoT-v2-test.csv"
    print(f"[ToN-IoT] Reading {raw_path}...")
    
    # Read chunk of 250k rows for fast, balanced processing
    df = pd.read_csv(raw_path, nrows=250000)
    
    # Map families matching Table 4 in paper
    family_map = {
        "Benign": "Benign",
        "scanning": "Scanning / Recon",
        "dos": "DoS / DDoS",
        "ddos": "DoS / DDoS",
        "backdoor": "Ransomware / Backdoor",
        "ransomware": "Ransomware / Backdoor",
        "injection": "Ransomware / Backdoor",
        "xss": "Ransomware / Backdoor",
        "password": "Ransomware / Backdoor",
        "mitm": "Scanning / Recon"
    }
    df["family"] = df["Attack"].map(family_map).fillna("Ransomware / Backdoor")
    df["label"] = (df["family"] != "Benign").astype(np.int64)
    
    # Drop non-numeric and target columns
    cols_to_drop = ["IPV4_SRC_ADDR", "IPV4_DST_ADDR", "Attack", "Label", "family", "label"]
    feature_cols = [c for c in df.columns if c not in cols_to_drop]
    
    # Convert features to float32, replace inf/nan
    for c in feature_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).replace([np.inf, -np.inf], 0.0).astype(np.float32)
        
    final_cols = feature_cols + ["label", "family"]
    df = df[final_cols]
    
    # Balance dataset to ~60,000 flows
    benign = df[df["family"] == "Benign"].sample(n=min(30000, len(df[df["family"] == "Benign"])), random_state=42)
    mal = df[df["family"] != "Benign"].sample(n=min(30000, len(df[df["family"] != "Benign"])), random_state=42)
    df_balanced = pd.concat([benign, mal]).sample(frac=1.0, random_state=42).reset_index(drop=True)
    
    df_balanced.to_parquet(out_file, index=False)
    print(f"[ToN-IoT] Saved {df_balanced.shape} to {out_file}")
    print("  Families:", df_balanced["family"].value_counts().to_dict())

def prep_unsw_nb15():
    out_file = OUT_DIR / "cleaned_unsw_nb15.parquet"
    if out_file.exists():
        print(f"[UNSW-NB15] Already exists at {out_file}")
        return
        
    raw_dir = Path(os.environ.get("RAW_DATA_DIR", ROOT / "datasets" / "raw"))
    raw_path = raw_dir / "unsw_nb15" / "UNSW_NB15_training-set.csv"
    print(f"[UNSW-NB15] Reading {raw_path}...")
    df = pd.read_csv(raw_path)
    
    # Map families
    family_map = {
        "Normal": "Benign",
        "Generic": "Generic",
        "Exploits": "Exploits",
        "Fuzzers": "Fuzzers",
        "DoS": "DoS",
        "Reconnaissance": "Reconnaissance",
        "Analysis": "Exploits",
        "Backdoor": "Exploits",
        "Shellcode": "Exploits",
        "Worms": "Exploits"
    }
    df["family"] = df["attack_cat"].str.strip().map(family_map).fillna("Exploits")
    df["label"] = (df["family"] != "Benign").astype(np.int64)
    
    cols_to_drop = ["id", "proto", "service", "state", "attack_cat", "label", "family"]
    feature_cols = [c for c in df.columns if c not in cols_to_drop and np.issubdtype(df[c].dtype, np.number)]
    
    for c in feature_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0).replace([np.inf, -np.inf], 0.0).astype(np.float32)
        
    final_cols = feature_cols + ["label", "family"]
    df = df[final_cols].reset_index(drop=True)
    
    df.to_parquet(out_file, index=False)
    print(f"[UNSW-NB15] Saved {df.shape} to {out_file}")
    print("  Families:", df["family"].value_counts().to_dict())

def prep_nsl_kdd():
    out_file = OUT_DIR / "cleaned_nsl_kdd.parquet"
    if out_file.exists():
        print(f"[NSL-KDD] Already exists at {out_file}")
        return
        
    raw_dir = Path(os.environ.get("RAW_DATA_DIR", ROOT / "datasets" / "raw"))
    raw_path = raw_dir / "nsl-kdd" / "KDDTrain_raw.csv"
    print(f"[NSL-KDD] Reading {raw_path}...")
    
    # 43 columns: col 0 to 40 features, col 41 attack type, col 42 difficulty
    df = pd.read_csv(raw_path, header=None)
    
    dos_types = {"neptune", "smurf", "back", "teardrop", "pod", "land", "apache2", "mailbomb", "processtable", "udpstorm"}
    probe_types = {"satan", "ipsweep", "portsweep", "nmap", "mscan", "saint"}
    r2l_types = {"warezclient", "guess_passwd", "warezmaster", "imap", "ftp_write", "multihop", "phf", "spy", "snmpgetattack", "named", "xlock", "xsnoop", "sendmail", "snmpguess", "worm"}
    u2r_types = {"buffer_overflow", "rootkit", "loadmodule", "perl", "sqlattack", "xterm", "ps"}
    
    def map_attack(atk):
        atk = str(atk).strip().lower()
        if atk == "normal":
            return "Benign"
        if atk in dos_types:
            return "DoS"
        if atk in probe_types:
            return "Probe"
        if atk in r2l_types:
            return "R2L"
        if atk in u2r_types:
            return "U2R"
        return "DoS"
        
    df["family"] = df[41].apply(map_attack)
    df["label"] = (df["family"] != "Benign").astype(np.int64)
    
    # Keep numeric columns among 0..40 (cols 1, 2, 3 are protocol_type, service, flag)
    num_cols = [c for c in range(41) if c not in [1, 2, 3]]
    feature_cols = [f"f_{c}" for c in num_cols]
    
    for old_c, new_c in zip(num_cols, feature_cols):
        df[new_c] = pd.to_numeric(df[old_c], errors="coerce").fillna(0.0).astype(np.float32)
        
    final_cols = feature_cols + ["label", "family"]
    df = df[final_cols].reset_index(drop=True)
    
    df.to_parquet(out_file, index=False)
    print(f"[NSL-KDD] Saved {df.shape} to {out_file}")
    print("  Families:", df["family"].value_counts().to_dict())

if __name__ == "__main__":
    prep_ton_iot()
    prep_unsw_nb15()
    prep_nsl_kdd()
