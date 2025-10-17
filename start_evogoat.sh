#!/data/data/com.termux/files/usr/bin/bash
set -e
VENV="$HOME/.venvs/evogoat"
WORKDIR="$HOME/projects/evogoat"

# Create virtualenv if missing
if [ ! -d "$VENV" ]; then
  python -m venv "$VENV"
fi

source "$VENV/bin/activate"

# Install requirements
python -m pip install --upgrade pip setuptools wheel
pip install -r "$WORKDIR/requirements.txt" --quiet

# Launch API//
