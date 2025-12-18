#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

export PYTHONPATH="src"

echo "== compileall =="
python -m compileall -q src tests

echo "== unittest =="
python -m unittest discover -s tests -v

