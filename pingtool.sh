#!/usr/bin/env bash
# Simple bootstrap script to run pingtool directly from GitHub.
# Usage:
#   bash <(curl -sSL https://raw.githubusercontent.com/<yourname>/pingtool/main/pingtool.sh) --country cn

set -e

RAW_URL="https://raw.githubusercontent.com/<yourname>/pingtool/main"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# If pingtool.py exists locally, use it. Otherwise fetch from GitHub.
if [[ -f "$SCRIPT_DIR/pingtool.py" ]]; then
    PY_PATH="$SCRIPT_DIR/pingtool.py"
else
    TMP_DIR="$(mktemp -d)"
    curl -sSL "$RAW_URL/pingtool.py" -o "$TMP_DIR/pingtool.py"
    mkdir -p "$TMP_DIR/data"
    curl -sSL "$RAW_URL/data/nameservers.sample.json" -o "$TMP_DIR/data/nameservers.sample.json"
    PY_PATH="$TMP_DIR/pingtool.py"
    SCRIPT_DIR="$TMP_DIR"
fi

python3 "$PY_PATH" "$@"
