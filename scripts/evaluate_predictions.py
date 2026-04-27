#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from common import extract_code_from_markdown, location_f1, read_jsonl, trim_line_ends, trim_outer


def safe_mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def evaluate(gold_rows, pred_rows):
    gold = {row["id"]: row for row in gold_rows}
    detailed = []
    missing = []
    for pred in pred_rows:
        ex_id = pred.get("id")
        if ex_id not in gold:
            missing.append(ex_id)
            continue
        row = gold[ex_id]
        raw_prediction = str(pred.get("prediction", ""))
        prediction = extract_code_from_markdown(raw_prediction)
        target = str(row.get("new", ""))
        old = str(row.get("old", ""))
        detailed.append({
            "id": ex_id,
            "baseline": pred.get("baseline", "unknown"),
            "language": row.get("language", "unknown"),
            "exact_match": int(prediction == target),
            "exact_match_trim": int(trim_outer(prediction) == trim_outer(target)),
            "exact_match_line_trim": int(trim_line_ends(prediction) == trim_line_ends(target)),
            "location_overlap_f1": location_f1(old, prediction, target),
            "prediction_len_chars": len(prediction),
            "target_len_chars": len(target),
            "num_gold_spans": row.get("num_gold_spans", ""),
            "num_gold_changed_old_lines": row.get("num_gold_changed_old_lines", ""),
            "change_complexity": row.get("change_complexity", ""),
        })
    return detailed, missing


def summarise(detailed):
    by_baseline = defaultdict(list)
    for row in detailed:
        by_baseline[row["baseline"]].append(row)
    summary = []
    for baseline, rows in sorted(by_baseline.items()):
        item = {"baseline": baseline, "n": len(rows)}
        for metric in ["exact_match", "exact_match_trim", "exact_match_line_trim", "location_overlap_f1"]:
            vals = [float(r[metric]) for r in rows]
            item[metric] = safe_mean(vals)
            item[metric + "_pct"] = 100.0 * item[metric]
        summary.append(item)
    return summary


def write_csv(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write("")
        return
    fields = list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True, help="Prepared subset JSONL")
    ap.add_argument("--pred", required=True, help="Predictions JSONL with id, baseline, prediction")
    ap.add_argument("--outdir", required=True, help="Report output directory")
    args = ap.parse_args()

    gold_rows = read_jsonl(args.gold)
    pred_rows = read_jsonl(args.pred)
    detailed, missing = evaluate(gold_rows, pred_rows)
    summary = summarise(detailed)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    write_csv(outdir / "per_example_metrics.csv", detailed)
    write_csv(outdir / "summary_metrics.csv", summary)
    with open(outdir / "summary_metrics.json", "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "missing_prediction_ids": missing}, f, ensure_ascii=False, indent=2)
    print(json.dumps({"summary": summary, "missing": len(missing), "outdir": str(outdir)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
