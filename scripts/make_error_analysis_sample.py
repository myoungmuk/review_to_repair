#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import random
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from common import read_jsonl


def read_csv_rows(path: str | Path) -> list[dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def build_metric_index(rows: list[dict[str, str]]) -> dict[str, dict[str, dict[str, str]]]:
    out: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        ex_id = row["id"]
        baseline = row["baseline"]
        out.setdefault(ex_id, {})[baseline] = row
    return out


def build_prediction_index(rows: list[dict]) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    for row in rows:
        ex_id = str(row.get("id", ""))
        baseline = str(row.get("baseline", ""))
        out.setdefault(ex_id, {})[baseline] = str(row.get("prediction", ""))
    return out


def sample_group(
    group_name: str,
    candidate_ids: list[str],
    metric_index: dict[str, dict[str, dict[str, str]]],
    gold_index: dict[str, dict],
    pred_index: dict[str, dict[str, str]],
    rng: random.Random,
    max_cases: int,
) -> list[dict[str, str]]:
    picked = list(candidate_ids)
    rng.shuffle(picked)
    sampled_rows: list[dict[str, str]] = []
    for ex_id in picked[:max_cases]:
        gold = gold_index[ex_id]
        direct_metrics = metric_index[ex_id]["direct"]
        gold_metrics = metric_index[ex_id]["gold_location"]
        sampled_rows.append(
            {
                "case_group": group_name,
                "id": ex_id,
                "language": str(gold.get("language", "")),
                "review": str(gold.get("review", "")),
                "old": str(gold.get("old", "")),
                "new": str(gold.get("new", "")),
                "direct_prediction": pred_index.get(ex_id, {}).get("direct", ""),
                "gold_location_prediction": pred_index.get(ex_id, {}).get("gold_location", ""),
                "direct_location_overlap_f1": direct_metrics.get("location_overlap_f1", ""),
                "gold_location_overlap_f1": gold_metrics.get("location_overlap_f1", ""),
                "manual_label": "",
                "notes": "",
            }
        )
    return sampled_rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-example", required=True, help="per_example_metrics.csv from evaluate_predictions.py")
    ap.add_argument("--gold", required=True, help="Prepared subset JSONL")
    ap.add_argument("--pred", required=True, help="Predictions JSONL")
    ap.add_argument("--output", required=True, help="Output CSV path")
    ap.add_argument("--max-per-group", type=int, default=10)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    metric_rows = read_csv_rows(args.per_example)
    gold_rows = read_jsonl(args.gold)
    pred_rows = read_jsonl(args.pred)

    gold_index = {str(row["id"]): row for row in gold_rows}
    metric_index = build_metric_index(metric_rows)
    pred_index = build_prediction_index(pred_rows)

    groups: dict[str, list[str]] = {
        "direct_fail_gold_location_success": [],
        "direct_fail_gold_location_fail": [],
        "direct_success_gold_location_success": [],
    }

    for ex_id, by_baseline in metric_index.items():
        if ex_id not in gold_index:
            continue
        if "direct" not in by_baseline or "gold_location" not in by_baseline:
            continue

        direct_ok = int(float(by_baseline["direct"]["exact_match_line_trim"]))
        gold_ok = int(float(by_baseline["gold_location"]["exact_match_line_trim"]))

        if direct_ok == 0 and gold_ok == 1:
            groups["direct_fail_gold_location_success"].append(ex_id)
        elif direct_ok == 0 and gold_ok == 0:
            groups["direct_fail_gold_location_fail"].append(ex_id)
        elif direct_ok == 1 and gold_ok == 1:
            groups["direct_success_gold_location_success"].append(ex_id)

    rng = random.Random(args.seed)
    output_rows: list[dict[str, str]] = []
    counts: dict[str, int] = {}
    for group_name, candidate_ids in groups.items():
        sampled = sample_group(
            group_name=group_name,
            candidate_ids=candidate_ids,
            metric_index=metric_index,
            gold_index=gold_index,
            pred_index=pred_index,
            rng=rng,
            max_cases=args.max_per_group,
        )
        output_rows.extend(sampled)
        counts[group_name] = len(sampled)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "case_group",
        "id",
        "language",
        "review",
        "old",
        "new",
        "direct_prediction",
        "gold_location_prediction",
        "direct_location_overlap_f1",
        "gold_location_overlap_f1",
        "manual_label",
        "notes",
    ]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output_rows)

    print(
        {
            "output": str(output_path),
            "rows": len(output_rows),
            "counts": counts,
        }
    )


if __name__ == "__main__":
    main()
