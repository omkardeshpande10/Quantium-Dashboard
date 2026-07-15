#!/bin/bash
set -e

VENV_DIR="venv"

# ── Create virtual environment if it doesn't already exist ───────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# ── Activate virtual environment ─────────────────────────────────────────────
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# ── Install dependencies ──────────────────────────────────────────────────────
echo "Installing dependencies..."
pip install --quiet -r streamlit/requirements.txt

# ── Run test suite ────────────────────────────────────────────────────────────
echo "Running tests..."
pytest streamlit/test_sales_visualizer2.py -v

# ── Capture result and return appropriate exit code ───────────────────────────
if [ $? -eq 0 ]; then
    echo "All tests passed."
    exit 0
else
    echo "One or more tests failed."
    exit 1
fi
