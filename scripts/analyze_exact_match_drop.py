#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parent))
from common import changed_line_set_old, read_jsonl, trim_line_ends


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with open(path, "w", encoding="utf-8", newline="") as f:
        if not fieldnames:
            f.write("")
            return
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_records(output_root: Path, generations_path: Path | None) -> list[dict[str, Any]]:
    if generations_path is not None:
        return read_jsonl(generations_path)
    all_path = output_root / "generations" / "all_generations.jsonl"
    if all_path.exists():
        return read_jsonl(all_path)
    rows: list[dict[str, Any]] = []
    for path in sorted((output_root / "generations").glob("*/*.jsonl")):
        rows.extend(read_jsonl(path))
    return rows


def infer_gold_path(output_root: Path) -> Path | None:
    metadata_path = output_root / "run_metadata.json"
    if not metadata_path.exists():
        return None
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    gold_path = str(metadata.get("gold_path", "")).strip()
    if not gold_path:
        return None
    path = Path(gold_path)
    return path if path.exists() else None


def read_gold_metadata(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None:
        return {}
    return {str(row.get("id", "")): row for row in read_jsonl(path)}


def fnum(value: Any, default: float = 0.0) -> float:
    if value in ("", None):
        return default
    return float(value)


def exact_value(row: dict[str, Any], metric: str) -> int:
    value = row.get(metric, "")
    if value in ("", None):
        return 0
    return int(float(value))


def len_ratio(prediction: str, target: str) -> float:
    target_len = max(len(trim_line_ends(target)), 1)
    return len(trim_line_ends(prediction)) / target_len


def length_bin(ratio: float) -> str:
    if ratio < 0.5:
        return "much_shorter_lt_0.5x"
    if ratio < 0.8:
        return "shorter_0.5x_0.8x"
    if ratio <= 1.2:
        return "similar_0.8x_1.2x"
    if ratio <= 1.5:
        return "longer_1.2x_1.5x"
    return "much_longer_gt_1.5x"


def loc_bin(value: float) -> str:
    if value >= 0.999:
        return "perfect_location_f1"
    if value >= 0.75:
        return "high_location_f1"
    if value >= 0.5:
        return "medium_location_f1"
    if value > 0.0:
        return "low_location_f1"
    return "zero_location_f1"


def delta_bin(delta: float) -> str:
    if delta > 1e-9:
        return "location_improved"
    if delta < -1e-9:
        return "location_worsened"
    return "location_unchanged"


def relation_to_gold_location(old: str, target: str, prediction: str, location_f1: float) -> str:
    old_norm = trim_line_ends(old)
    pred_norm = trim_line_ends(prediction)
    if pred_norm == old_norm:
        return "no_change_from_old"

    gold_lines = changed_line_set_old(old, target)
    pred_lines = changed_line_set_old(old, prediction)
    if not pred_lines:
        return "no_detected_old_line_change"
    if location_f1 >= 0.999:
        return "right_location_wrong_content"
    if pred_lines == gold_lines:
        return "same_changed_lines_wrong_content"
    if pred_lines < gold_lines:
        return "under_edit_subset_of_gold_lines"
    if pred_lines > gold_lines:
        return "over_edit_superset_of_gold_lines"
    if pred_lines & gold_lines:
        return "partial_overlap_wrong_or_missing_lines"
    return "wrong_changed_lines"


def short_text(value: Any, limit: int) -> str:
    text = str(value or "").replace("\n", "\\n")
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def percent(part: int, whole: int) -> float:
    return 100.0 * part / whole if whole else 0.0


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        values: list[str] = []
        for col in columns:
            value = row.get(col, "")
            if isinstance(value, float):
                values.append(f"{value:.3f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return lines


def build_analysis(
    records: list[dict[str, Any]],
    gold_by_id: dict[str, dict[str, Any]],
    condition_a: str,
    condition_b: str,
    metric: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    by_model_id: dict[tuple[str, str], dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in records:
        if int(row.get("valid_evaluation", 0)) != 1:
            continue
        model = str(row.get("model", ""))
        ex_id = str(row.get("example_id", row.get("id", "")))
        condition = str(row.get("condition", row.get("baseline", "")))
        by_model_id[(model, ex_id)][condition] = row

    transition_counts: dict[str, Counter[str]] = defaultdict(Counter)
    regression_rows: list[dict[str, Any]] = []
    category_counts: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)

    for (model, ex_id), conditions in by_model_id.items():
        if condition_a not in conditions or condition_b not in conditions:
            continue
        a = conditions[condition_a]
        b = conditions[condition_b]
        a_exact = exact_value(a, metric)
        b_exact = exact_value(b, metric)
        transition = {
            (1, 1): "both_exact",
            (1, 0): f"{condition_a}_only_exact",
            (0, 1): f"{condition_b}_only_exact",
            (0, 0): "neither_exact",
        }[(a_exact, b_exact)]
        transition_counts[model][transition] += 1

        if not (a_exact == 1 and b_exact == 0):
            continue

        old = str(b.get("old_snippet", ""))
        target = str(b.get("target_code", ""))
        prediction = str(b.get("prediction", b.get("extracted_code", "")))
        a_loc = fnum(a.get("location_overlap_f1"))
        b_loc = fnum(b.get("location_overlap_f1"))
        loc_delta = b_loc - a_loc
        ratio = len_ratio(prediction, target)
        relation = relation_to_gold_location(old, target, prediction, b_loc)
        warn = str(b.get("warning", "") or "none")
        gold_meta = gold_by_id.get(ex_id, {})
        complexity = str(b.get("change_complexity", "") or gold_meta.get("change_complexity", "") or "unknown")
        language = str(b.get("language", "") or gold_meta.get("language", "") or "unknown")

        category_counts[(model, "gold_location_f1_bin", loc_bin(b_loc))]["n"] += 1
        category_counts[(model, "location_delta_bin", delta_bin(loc_delta))]["n"] += 1
        category_counts[(model, "prediction_length_bin", length_bin(ratio))]["n"] += 1
        category_counts[(model, "changed_line_relation", relation)]["n"] += 1
        category_counts[(model, "gold_output_warning", warn)]["n"] += 1
        category_counts[(model, "change_complexity", complexity)]["n"] += 1
        category_counts[(model, "language", language)]["n"] += 1

        regression_rows.append(
            {
                "model": model,
                "example_id": ex_id,
                "language": language,
                "change_complexity": complexity,
                f"{condition_a}_{metric}": a_exact,
                f"{condition_b}_{metric}": b_exact,
                f"{condition_a}_location_overlap_f1": a_loc,
                f"{condition_b}_location_overlap_f1": b_loc,
                "location_f1_delta": loc_delta,
                "location_delta_bin": delta_bin(loc_delta),
                "gold_location_f1_bin": loc_bin(b_loc),
                "prediction_length_ratio": ratio,
                "prediction_length_bin": length_bin(ratio),
                "changed_line_relation": relation,
                "gold_output_warning": warn,
                "target_len_chars": len(trim_line_ends(target)),
                "gold_prediction_len_chars": len(trim_line_ends(prediction)),
                "review_comment_excerpt": short_text(b.get("review_comment", ""), 240),
                "direct_prediction_excerpt": short_text(a.get("prediction", a.get("extracted_code", "")), 240),
                "gold_prediction_excerpt": short_text(prediction, 240),
                "target_code_excerpt": short_text(target, 240),
            }
        )

    transition_rows: list[dict[str, Any]] = []
    for model, counts in sorted(transition_counts.items()):
        total = sum(counts.values())
        loss = counts[f"{condition_a}_only_exact"]
        gain = counts[f"{condition_b}_only_exact"]
        transition_rows.append(
            {
                "model": model,
                "paired_n": total,
                "both_exact": counts["both_exact"],
                f"{condition_a}_only_exact": loss,
                f"{condition_b}_only_exact": gain,
                "neither_exact": counts["neither_exact"],
                "net_exact_delta_count": gain - loss,
                "net_exact_delta_pct": percent(gain - loss, total),
                "regression_count": loss,
                "regression_pct_of_pairs": percent(loss, total),
            }
        )

    category_rows: list[dict[str, Any]] = []
    regressions_by_model = Counter(row["model"] for row in regression_rows)
    for (model, category, value), counts in sorted(category_counts.items()):
        n = counts["n"]
        category_rows.append(
            {
                "model": model,
                "category": category,
                "value": value,
                "n": n,
                "pct_of_regressions": percent(n, regressions_by_model[model]),
            }
        )

    return transition_rows, category_rows, regression_rows


def write_markdown(
    path: Path,
    condition_a: str,
    condition_b: str,
    metric: str,
    transition_rows: list[dict[str, Any]],
    category_rows: list[dict[str, Any]],
) -> None:
    lines = [
        "# Exact Match Drop Analysis",
        "",
        f"- Comparison: `{condition_b} - {condition_a}`",
        f"- Metric: `{metric}`",
        "- Scope: paired valid evaluations only.",
        "- Interpretation: these are diagnostic correlates of 1->0 exact-match regressions, not causal proof.",
        "",
        "## Exact-Match Transitions",
    ]
    lines.extend(
        markdown_table(
            transition_rows,
            [
                "model",
                "paired_n",
                "both_exact",
                f"{condition_a}_only_exact",
                f"{condition_b}_only_exact",
                "neither_exact",
                "net_exact_delta_count",
                "net_exact_delta_pct",
                "regression_count",
                "regression_pct_of_pairs",
            ],
        )
    )

    for category in [
        "location_delta_bin",
        "gold_location_f1_bin",
        "changed_line_relation",
        "prediction_length_bin",
        "gold_output_warning",
        "change_complexity",
        "language",
    ]:
        rows = [row for row in category_rows if row["category"] == category]
        rows = sorted(rows, key=lambda row: (str(row["model"]), -int(row["n"]), str(row["value"])))
        lines.extend(["", f"## Regression Breakdown: {category}"])
        lines.extend(markdown_table(rows, ["model", "value", "n", "pct_of_regressions"]))

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Diagnose paired exact-match regressions between two Review-to-Repair conditions."
    )
    ap.add_argument("--output-root", required=True, help="Run directory containing generations/all_generations.jsonl")
    ap.add_argument("--generations", default=None, help="Optional explicit all_generations JSONL path")
    ap.add_argument("--gold", default=None, help="Optional prepared gold JSONL; defaults to run_metadata.json gold_path")
    ap.add_argument("--condition-a", default="direct")
    ap.add_argument("--condition-b", default="gold_location")
    ap.add_argument("--metric", default="exact_match_line_trim")
    ap.add_argument("--out-prefix", default="exact_match_drop_analysis")
    args = ap.parse_args()
    if args.condition_a == args.condition_b:
        raise ValueError("--condition-a and --condition-b must differ")
    return args


def main() -> None:
    args = parse_args()
    output_root = Path(args.output_root)
    generations_path = Path(args.generations) if args.generations else None
    gold_path = Path(args.gold) if args.gold else infer_gold_path(output_root)
    records = read_records(output_root, generations_path)
    gold_by_id = read_gold_metadata(gold_path)
    transition_rows, category_rows, regression_rows = build_analysis(
        records=records,
        gold_by_id=gold_by_id,
        condition_a=args.condition_a,
        condition_b=args.condition_b,
        metric=args.metric,
    )

    transition_path = output_root / f"{args.out_prefix}_transitions.csv"
    categories_path = output_root / f"{args.out_prefix}_categories.csv"
    cases_path = output_root / f"{args.out_prefix}_regression_cases.csv"
    markdown_path = output_root / f"{args.out_prefix}.md"

    write_csv(transition_path, transition_rows)
    write_csv(categories_path, category_rows)
    write_csv(cases_path, regression_rows)
    write_markdown(
        markdown_path,
        args.condition_a,
        args.condition_b,
        args.metric,
        transition_rows,
        category_rows,
    )

    print(
        json.dumps(
            {
                "transitions": str(transition_path),
                "categories": str(categories_path),
                "regression_cases": str(cases_path),
                "markdown": str(markdown_path),
                "n_regression_cases": len(regression_rows),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
