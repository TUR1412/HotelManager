#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "== ruff format (check) =="
python -m ruff format --check .

echo "== ruff check =="
python -m ruff check .
