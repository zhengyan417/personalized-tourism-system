#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
VENV="$ROOT/.venv"
PYTHON_BIN="${PYTHON_BIN:-python3}"
SKIP_BACKEND="${SKIP_BACKEND:-0}"
SKIP_FRONTEND="${SKIP_FRONTEND:-0}"
BUILD_FRONTEND="${BUILD_FRONTEND:-1}"

if [[ "$SKIP_BACKEND" != "1" ]]; then
  if [[ ! -x "$VENV/bin/python" ]]; then
    echo "Creating virtual environment at $VENV"
    "$PYTHON_BIN" -m venv "$VENV"
  else
    echo "Using existing virtual environment at $VENV"
  fi
  "$VENV/bin/python" -m pip install --upgrade pip
  "$VENV/bin/python" -m pip install -r "$BACKEND/requirements.txt"
fi

if [[ "$SKIP_FRONTEND" != "1" ]]; then
  echo "Installing frontend dependencies"
  (cd "$FRONTEND" && npm install)
  if [[ "$BUILD_FRONTEND" == "1" ]]; then
    echo "Building frontend"
    (cd "$FRONTEND" && npm run build)
  fi
fi

echo "Deployment preparation complete."
echo "Activate backend venv with: source $VENV/bin/activate"
echo "Run backend via: python backend/app.py"
echo "Serve frontend dev via: cd frontend && npm run serve"
