#!/usr/bin/env bash
#
# AI Orchestrator — one-command startup.
#
# Usage:
#   ./run.sh                 # launch the Streamlit dashboard (default)
#   ./run.sh web             # launch the Streamlit dashboard
#   ./run.sh cli "<goal>"    # run the pipeline from the command line
#
# On first run it creates a virtualenv, installs dependencies, and scaffolds
# .env from the template.

set -euo pipefail
cd "$(dirname "$0")"

VENV=".venv"
PYTHON="${PYTHON:-python3}"

# 1. Virtualenv
if [ ! -d "$VENV" ]; then
  echo "==> Creating virtualenv ($VENV)…"
  "$PYTHON" -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"

# 2. Dependencies (install once; delete .venv/.deps-installed to force reinstall)
if [ ! -f "$VENV/.deps-installed" ] || [ requirements.txt -nt "$VENV/.deps-installed" ]; then
  echo "==> Installing dependencies…"
  pip install -q -r requirements.txt
  touch "$VENV/.deps-installed"
fi

# 3. .env
if [ ! -f .env ]; then
  echo "==> Creating .env from template — edit it and add your ANTHROPIC_API_KEY."
  cp .env.example .env
fi
if grep -q "sk-ant-xxxx" .env 2>/dev/null; then
  echo "!!  Warning: .env still holds the placeholder ANTHROPIC_API_KEY."
  echo "!!  Edit .env before running a real pipeline."
fi

# 4. Launch
MODE="${1:-web}"
case "$MODE" in
  web)
    echo "==> Launching dashboard at http://localhost:8501"
    exec streamlit run app.py
    ;;
  cli)
    shift || true
    if [ "$#" -eq 0 ]; then
      echo "Usage: ./run.sh cli \"<your goal>\"" >&2
      exit 1
    fi
    exec python main.py "$@"
    ;;
  *)
    echo "Unknown mode: $MODE" >&2
    echo "Usage: ./run.sh [web | cli \"<goal>\"]" >&2
    exit 1
    ;;
esac
