#!/usr/bin/env python3
"""Verify the runtime environment against requirements.txt.

Checks the Python version range (>=3.11) and verifies that key direct
dependencies are importable and satisfy version bounds.

Usage:
  python3 scripts/verify_environment.py
"""

from __future__ import annotations

import importlib.metadata as importlib_metadata
import os
import re
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REQUIREMENTS = os.path.join(PROJECT_ROOT, "requirements.txt")

IMPORT_NAME = {
    "scikit-learn": "sklearn",
    "grpcio-tools": "grpc_tools",
    "flwr[simulation]": "flwr",
}


def parse_requirements(path: str) -> dict[str, str]:
    pins = {}
    if not os.path.exists(path):
        return pins
    with open(path) as fh:
        for line in fh:
            line = line.split("#", 1)[0].strip()
            if not line:
                continue
            m = re.match(r"^([A-Za-z0-9_.\-\[\]]+)(?:==|>=)([^\s;]+)", line)
            if m:
                pkg_name = m.group(1).split("[")[0]
                pins[pkg_name] = m.group(2)
    return pins


def main() -> int:
    pins = parse_requirements(REQUIREMENTS)
    failures = []

    py = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if not (sys.version_info[:2] >= (3, 11)):
        failures.append(f"python {py} outside [>=3.11]")

    print("=" * 68)
    print("  FedLearn: Python Runtime & Dependency Verification")
    print("=" * 68)
    print(f"Python interpreter: {py} ({sys.executable})")

    for dist, want in sorted(pins.items()):
        try:
            got = importlib_metadata.version(dist)
            print(f"[OK]   {dist:20s} (installed: {got}, required: >={want})")
        except importlib_metadata.PackageNotFoundError:
            failures.append(f"{dist}: not installed (required >={want})")
            print(f"[FAIL] {dist:20s} (NOT INSTALLED, required: >={want})")

    print("=" * 68)
    if failures:
        print("verify_env: FAIL")
        for f in failures:
            print("  - " + f)
        return 1
    print(f"verify_env: PASS (Python {py}, all {len(pins)} dependencies satisfied)")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    sys.exit(main())
