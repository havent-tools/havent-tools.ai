#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

# Optional: start in a separate tmux session
if [ "${1:-}" = "tmux" ]; then
  tmux new -d -s havent-tools "python3 src/main.py"
  echo "Agent started in tmux session: havent-tools"
  echo "Attach with: tmux attach -t havent-tools"
  exit 0
fi

exec python3 src/main.py
