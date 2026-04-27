#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from common import read_jsonl, write_jsonl

SYSTEM = "You are a careful code editing assistant. Return only the revised code snippet, with no explanation."


def prompt_no_review(row):
    return f"""A code review has requested a minimal revision to the following code snippet, but the review comment is hidden.
Infer the most likely minimal correction if possible. If there is not enough information, make the smallest safe improvement and return only the revised code snippet.

Original code snippet:
```{row.get('language','')}
{row['old']}
```

Return only the revised code snippet."""


def prompt_direct(row):
    return f"""Apply the review comment to the original code snippet.
Make the minimal change needed to satisfy the review. Return only the revised code snippet.

Review comment:
{row['review']}

Original code snippet:
```{row.get('language','')}
{row['old']}
```

Return only the revised code snippet."""


def prompt_gold_location(row):
    return f"""Apply the review comment to the original code snippet.
The gold location markers show where the required revision is located in the original snippet.
Make the minimal change needed to satisfy the review. Prefer changes inside the marked region, unless a tiny surrounding change is necessary. Return only the revised code snippet.

Review comment:
{row['review']}

Original code snippet with gold location markers:
```{row.get('language','')}
{row['gold_old_marked']}
```

Return only the revised code snippet, without the gold markers."""


def build_prompt(row, baseline):
    if baseline == "no_review":
        user = prompt_no_review(row)
    elif baseline == "direct":
        user = prompt_direct(row)
    elif baseline == "gold_location":
        user = prompt_gold_location(row)
    else:
        raise ValueError(f"Unknown baseline: {baseline}")
    return {
        "id": row["id"],
        "baseline": baseline,
        "language": row.get("language", "unknown"),
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user},
        ],
        "prompt": SYSTEM + "\n\n" + user,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Prepared subset JSONL")
    ap.add_argument("--outdir", required=True, help="Prompt output directory")
    ap.add_argument("--baselines", nargs="+", default=["no_review", "direct", "gold_location"])
    args = ap.parse_args()

    rows = read_jsonl(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    for baseline in args.baselines:
        prompts = [build_prompt(row, baseline) for row in rows]
        out_path = outdir / f"{baseline}_prompts.jsonl"
        write_jsonl(out_path, prompts)
        print(f"wrote {out_path} ({len(prompts)} prompts)")


if __name__ == "__main__":
    main()
