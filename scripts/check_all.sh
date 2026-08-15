#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python scripts/verify_project.py
python scripts/generate_screenshots.py
python scripts/generate_erd.py
git diff --check

echo "B5-1 CHECK ALL: PASS"
