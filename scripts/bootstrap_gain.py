#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from pathlib import Path


def read_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def percentile(xs, p):
    if not xs:
        return 0.0
    xs = sorted(xs)
    k = (len(xs) - 1) * p / 100.0
    lo = int(k)
    hi = min(lo + 1, len(xs) - 1)
    frac = k - lo
    return xs[lo] * (1 - frac) + xs[hi] * frac


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-example", required=True, help="per_example_metrics.csv from evaluate_predictions.py")
    ap.add_argument("--baseline-a", required=True, help="Baseline subtrahend, e.g. no_review")
    ap.add_argument("--baseline-b", required=True, help="Baseline minuend, e.g. direct")
    ap.add_argument("--metric", default="exact_match_line_trim")
    ap.add_argument("--iters", type=int, default=1000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rows = read_csv(args.per_example)
    by_id = defaultdict(dict)
    for r in rows:
        by_id[r["id"]][r["baseline"]] = float(r[args.metric])
    paired = [(v[args.baseline_a], v[args.baseline_b]) for v in by_id.values() if args.baseline_a in v and args.baseline_b in v]
    rng = random.Random(args.seed)
    gains = []
    for _ in range(args.iters):
        sample = [paired[rng.randrange(len(paired))] for _ in paired]
        gains.append(mean([b - a for a, b in sample]))
    point = mean([b - a for a, b in paired]) if paired else 0.0
    print({
        "paired_n": len(paired),
        "gain": point,
        "gain_pct": point * 100,
        "ci95_low": percentile(gains, 2.5),
        "ci95_high": percentile(gains, 97.5),
        "metric": args.metric,
        "baseline_b_minus_a": f"{args.baseline_b} - {args.baseline_a}",
    })


if __name__ == "__main__":
    main()
