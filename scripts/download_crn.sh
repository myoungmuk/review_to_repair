#!/usr/bin/env bash
set -euo pipefail

# CodeReview-New supplementary data is distributed by the authors as a Google Drive RAR file.
# File ID from the public project page:
FILE_ID="1f0hFmtUKWAHwlcDQXZZKlF5wdbBKaVWz"
OUT_DIR="${1:-data_raw}"
mkdir -p "$OUT_DIR"

if ! command -v gdown >/dev/null 2>&1; then
  echo "gdown is not installed. Install with: python3 -m pip install gdown"
  exit 1
fi

gdown "https://drive.google.com/uc?id=${FILE_ID}" -O "$OUT_DIR/data.rar"

if command -v 7z >/dev/null 2>&1; then
  7z x "$OUT_DIR/data.rar" -o"$OUT_DIR"
elif command -v unrar >/dev/null 2>&1; then
  unrar x "$OUT_DIR/data.rar" "$OUT_DIR/"
else
  echo "Downloaded $OUT_DIR/data.rar"
  echo "Please extract it manually with 7z or unrar, then ensure codereview_new.jsonl is under $OUT_DIR."
fi
