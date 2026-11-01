#!/usr/bin/env python3
"""Verify checkpoint and artifact integrity against manifest/checkpoint_sha256.json.

Recomputes SHA-256 for all shipped metrics, tables, figures, and logs.
Exits non-zero on any mismatch or missing file.

Usage:
  python3 verification/verify_manifest.py
  python3 verification/verify_manifest.py --quiet
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "manifest", "checkpoint_sha256.json")


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify artifact checksums.")
    parser.add_argument("--quiet", action="store_true", help="only print failures")
    args = parser.parse_args()

    if not os.path.exists(MANIFEST):
        print(f"ERROR: Manifest missing at {MANIFEST}")
        return 1

    with open(MANIFEST) as f:
        manifest_data = json.load(f)

    expected = manifest_data.get("checkpoints", {})
    if not expected:
        print("ERROR: No checkpoints defined in manifest.")
        return 1

    missing, mismatched, passed = [], [], []

    if not args.quiet:
        print("=" * 68)
        print("  FedLearn: Artifact & Checkpoint Integrity Verification")
        print("=" * 68)

    for rel_path, expected_hash in sorted(expected.items()):
        full_path = os.path.join(ROOT, rel_path)
        if not os.path.exists(full_path):
            missing.append(rel_path)
            if not args.quiet:
                print(f"[MISSING] {rel_path}")
            continue

        actual_hash = sha256(full_path).lower()
        if actual_hash != expected_hash.lower():
            mismatched.append((rel_path, expected_hash, actual_hash))
            if not args.quiet:
                print(f"[FAIL]    {rel_path}")
        else:
            passed.append(rel_path)
            if not args.quiet:
                print(f"[OK]      {rel_path}")

    ok = (len(missing) == 0 and len(mismatched) == 0)
    status = "PASS" if ok else "FAIL"

    if not args.quiet:
        print("=" * 68)
    print(f"verify_manifest: {status} ({len(passed)}/{len(expected)} checkpoints verified)")
    if not ok:
        if missing:
            print(f"  Missing files ({len(missing)}):")
            for m in missing:
                print(f"    - {m}")
        if mismatched:
            print(f"  Checksum mismatches ({len(mismatched)}):")
            for rel, exp_h, act_h in mismatched:
                print(f"    - {rel}: expected {exp_h[:12]}..., got {act_h[:12]}...")
    if not args.quiet:
        print("=" * 68)

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
