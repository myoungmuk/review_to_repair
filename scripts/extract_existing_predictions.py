#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from common import read_jsonl, write_jsonl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Prepared subset JSONL")
    ap.add_argument("--output", required=True, help="Output predictions JSONL")
    args = ap.parse_args()

    rows = read_jsonl(args.input)
    preds = []
    for row in rows:
        if row.get("gpt_code"):
            preds.append({"id": row["id"], "baseline": "published_chatgpt_direct", "prediction": row["gpt_code"]})
        if row.get("model_code"):
            preds.append({"id": row["id"], "baseline": "published_codereviewer", "prediction": row["model_code"]})
    write_jsonl(args.output, preds)
    print(f"wrote {args.output} ({len(preds)} predictions)")


if __name__ == "__main__":
    main()
