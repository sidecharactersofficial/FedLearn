#!/usr/bin/env python3
"""Verify processed dataset integrity against manifest/dataset_sha256.txt.

Recomputes SHA-256 of the 4 processed benchmark parquet files and compares them
against the pinned hashes. Exits non-zero on any mismatch.

Usage:
  python3 verification/verify_datasets.py
"""

from __future__ import annotations

import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "manifest", "dataset_sha256.txt")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    if not os.path.exists(MANIFEST):
        print(f"ERROR: Manifest missing at {MANIFEST}")
        return 1

    expected = []
    with open(MANIFEST) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                # support both 'digest path' (standard sha256sum) and 'path digest'
                if len(parts[0]) == 64 and all(c in "0123456789abcdefABCDEF" for c in parts[0]):
                    digest, path = parts[0], parts[1]
                else:
                    path, digest = parts[0], parts[1]
                expected.append((path, digest.lower()))

    status = "PASS"
    print("=" * 68)
    print("  FedLearn: Dataset Integrity Verification (SHA-256)")
    print("=" * 68)
    for path, digest in expected:
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            print(f"[MISSING] {path}")
            status = "FAIL"
            continue
        actual = sha256(full).lower()
        ok = (actual == digest)
        if not ok:
            status = "FAIL"
            print(f"[FAIL]    {path}")
            print(f"          Expected: {digest}")
            print(f"          Actual:   {actual}")
        else:
            print(f"[OK]      {path}")

    print("=" * 68)
    print(f"verify_datasets: {status} ({len(expected)}/4 datasets verified)")
    print("=" * 68)
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
