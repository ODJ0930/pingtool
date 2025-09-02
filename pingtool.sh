#!/usr/bin/env bash
# Simple bootstrap script to run pingtool directly from GitHub.
# Usage:
#   bash <(curl -fsSL https://raw.githubusercontent.com/ODJ0930/pingtool/main/pingtool.sh) --country cn

set -e

RAW_URL="${PINGTOOL_RAW_URL:-https://raw.githubusercontent.com/ODJ0930/pingtool/main}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# If pingtool.py exists locally, use it. Otherwise fetch from GitHub.
if [[ -f "$SCRIPT_DIR/pingtool.py" ]]; then
    PY_PATH="$SCRIPT_DIR/pingtool.py"
else
    TMP_DIR="$(mktemp -d)"
    if ! curl -fsSL "$RAW_URL/pingtool.py" -o "$TMP_DIR/pingtool.py"; then
        echo "Failed to download pingtool.py from $RAW_URL" >&2
        exit 1
    fi
    mkdir -p "$TMP_DIR/data"
    if ! curl -fsSL "$RAW_URL/data/nameservers.sample.json" -o "$TMP_DIR/data/nameservers.sample.json"; then
        echo "Failed to download sample dataset from $RAW_URL" >&2
        exit 1
    fi
    PY_PATH="$TMP_DIR/pingtool.py"
    SCRIPT_DIR="$TMP_DIR"
fi

python3 "$PY_PATH" "$@"
