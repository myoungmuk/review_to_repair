#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from common import (
    changed_line_set_old,
    changed_spans_old,
    compact_id,
    ensure_required,
    find_codereview_new,
    mark_gold_locations,
    normalize_newlines,
    read_jsonl,
    write_jsonl,
)


def complexity_bucket(n_changed: int) -> str:
    if n_changed <= 1:
        return "tiny_1_line"
    if n_changed <= 3:
        return "small_2_3_lines"
    if n_changed <= 8:
        return "medium_4_8_lines"
    return "large_9plus_lines"


def prepare_rows(rows, n: int, seed: int, language: str | None):
    cleaned = []
    for idx, row in enumerate(rows):
        if not ensure_required(row, ["old", "review", "new"]):
            continue
        if language and str(row.get("language", "")).lower() != language.lower():
            continue
        old = normalize_newlines(row.get("old", ""))
        new = normalize_newlines(row.get("new", ""))
        review = normalize_newlines(row.get("review", ""))
        spans = changed_spans_old(old, new)
        changed_lines = changed_line_set_old(old, new)
        prepared = {
            "id": compact_id(row, idx),
            "source_index": idx,
            "language": row.get("language", "unknown"),
            "old": old,
            "review": review,
            "new": new,
            "commit_url": row.get("commit_url", ""),
            "gpt_code": normalize_newlines(row.get("gpt_code", "")),
            "model_code": normalize_newlines(row.get("model_code", "")),
            "gpt_em": row.get("gpt_em", None),
            "gpt_em_trim": row.get("gpt_em_trim", None),
            "gold_spans_old": [s.to_dict() for s in spans],
            "gold_old_marked": mark_gold_locations(old, spans),
            "num_gold_spans": len(spans),
            "num_gold_changed_old_lines": len(changed_lines),
            "change_complexity": complexity_bucket(len(changed_lines)),
        }
        cleaned.append(prepared)

    rng = random.Random(seed)
    if n <= 0 or n >= len(cleaned):
        rng.shuffle(cleaned)
        return cleaned

    # Stratify by language and complexity where possible.
    strata = defaultdict(list)
    for row in cleaned:
        strata[(row["language"], row["change_complexity"])].append(row)
    for bucket_rows in strata.values():
        rng.shuffle(bucket_rows)

    selected = []
    keys = list(strata.keys())
    rng.shuffle(keys)
    while len(selected) < n and keys:
        next_keys = []
        for key in keys:
            if strata[key] and len(selected) < n:
                selected.append(strata[key].pop())
            if strata[key]:
                next_keys.append(key)
        keys = next_keys
    rng.shuffle(selected)
    return selected[:n]


def write_summary(rows, out_csv: Path):
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    langs = Counter(r["language"] for r in rows)
    complexities = Counter(r["change_complexity"] for r in rows)
    spans = Counter("single_span" if r["num_gold_spans"] == 1 else "multi_span" if r["num_gold_spans"] > 1 else "no_change" for r in rows)
    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["section", "key", "count"])
        writer.writerow(["total", "examples", len(rows)])
        for k, v in sorted(langs.items()):
            writer.writerow(["language", k, v])
        for k, v in sorted(complexities.items()):
            writer.writerow(["complexity", k, v])
        for k, v in sorted(spans.items()):
            writer.writerow(["span_count", k, v])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to codereview_new.jsonl or a directory containing it")
    ap.add_argument("--output", required=True, help="Output prepared subset JSONL")
    ap.add_argument("--n", type=int, default=100, help="Subset size. Use 0 for all examples")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--language", default=None, help="Optional language filter, e.g. Python")
    args = ap.parse_args()

    src = find_codereview_new(args.input)
    rows = read_jsonl(src)
    selected = prepare_rows(rows, n=args.n, seed=args.seed, language=args.language)
    write_jsonl(args.output, selected)
    summary_path = Path(args.output).with_suffix(".summary.csv")
    write_summary(selected, summary_path)
    print(f"source={src}")
    print(f"selected={len(selected)}")
    print(f"output={args.output}")
    print(f"summary={summary_path}")


if __name__ == "__main__":
    main()
