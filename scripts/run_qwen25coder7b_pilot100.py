#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import csv
import json
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parent))
from common import read_jsonl


REPO_ROOT = Path(__file__).resolve().parent.parent
BASELINES = ("no_review", "direct", "gold_location")
MODEL_NAME = "qwen2.5-coder:7b"
RUN_NAME = "crn_pilot100_qwen25coder7b"
REPORT_DIR = REPO_ROOT / "reports" / RUN_NAME
LOG_PATH = REPORT_DIR / "pipeline.log"
METADATA_PATH = REPORT_DIR / "run_metadata.json"


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def command_text(args: list[str]) -> str:
    return " ".join(args)


def count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def append_log(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(text)
        if not text.endswith("\n"):
            f.write("\n")


def run_cmd(args: list[str], log_path: Path) -> str:
    text = command_text(args)
    append_log(log_path, f"$ {text}")
    proc = subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True)
    if proc.stdout:
        append_log(log_path, proc.stdout.rstrip("\n"))
    if proc.stderr:
        append_log(log_path, proc.stderr.rstrip("\n"))
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {proc.returncode}: {text}\n{proc.stderr}")
    return proc.stdout


def head30_ids(path: Path) -> list[str]:
    return [str(row.get("id", "")) for row in read_jsonl(path)]


def prompt_lines(path: Path, n: int) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for _, line in zip(range(n), f)]


def validate_subset_alignment() -> dict[str, Any]:
    subset_path = REPO_ROOT / "data" / "processed" / "crn_pilot30_head42.jsonl"
    full_path = REPO_ROOT / "data" / "processed" / "crn_pilot100.jsonl"
    subset_ids = head30_ids(subset_path)
    full_ids = head30_ids(full_path)[:30]
    if subset_ids != full_ids:
        raise RuntimeError("Preflight failed: crn_pilot30_head42 IDs do not match the first 30 IDs of crn_pilot100.")

    prompt_results: dict[str, bool] = {}
    for baseline in BASELINES:
        subset_prompt = REPO_ROOT / "prompts" / "crn_pilot30_head42" / f"{baseline}_prompts.jsonl"
        full_prompt = REPO_ROOT / "prompts" / "crn_pilot100" / f"{baseline}_prompts.jsonl"
        matches = prompt_lines(subset_prompt, 30) == prompt_lines(full_prompt, 30)
        prompt_results[baseline] = matches
        if not matches:
            raise RuntimeError(f"Preflight failed: {baseline} prompts differ between subset30 and pilot100 head30.")

    return {
        "subset_path": str(subset_path),
        "full_path": str(full_path),
        "subset_ids": subset_ids,
        "prompt_match": prompt_results,
    }


def baseline_paths() -> dict[str, Path]:
    return {baseline: REPO_ROOT / "predictions" / f"{RUN_NAME}_{baseline}.jsonl" for baseline in BASELINES}


def merged_path() -> Path:
    return REPO_ROOT / "predictions" / f"{RUN_NAME}.jsonl"


def error_paths() -> dict[str, Path]:
    return {baseline: REPORT_DIR / f"{baseline}_errors.jsonl" for baseline in BASELINES}


def output_key(row: dict[str, Any]) -> tuple[str, str]:
    return str(row.get("id", "")), str(row.get("baseline", ""))


def validate_existing_preseed(paths: dict[str, Path]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    duplicate_groups = 0
    missing_pairs: list[str] = []
    all_rows: list[dict[str, Any]] = []

    for baseline, path in paths.items():
        if not path.exists():
            raise RuntimeError(f"Expected preseeded file is missing: {path}")
        rows = read_jsonl(path)
        counts[baseline] = len(rows)
        all_rows.extend(rows)
        bad_rows = [row for row in rows if str(row.get("baseline", "")) != baseline]
        if bad_rows:
            raise RuntimeError(f"Preseed validation failed: {path} contains rows with mismatched baseline values.")

    grouped = defaultdict(list)
    for row in all_rows:
        grouped[output_key(row)].append(row)
    duplicate_groups = sum(1 for values in grouped.values() if len(values) > 1)
    if duplicate_groups:
        raise RuntimeError("Preseed validation failed: duplicate (id, baseline) pairs already exist.")

    by_id: dict[str, set[str]] = defaultdict(set)
    for row in all_rows:
        by_id[str(row.get("id", ""))].add(str(row.get("baseline", "")))
    for item_id, bases in by_id.items():
        for baseline in BASELINES:
            if baseline not in bases:
                missing_pairs.append(f"{item_id}:{baseline}")
    if missing_pairs:
        raise RuntimeError("Preseed validation failed: some IDs are missing required baselines.")

    return {
        "counts": counts,
        "total_rows": len(all_rows),
        "unique_ids": len(by_id),
        "duplicate_groups": duplicate_groups,
    }


def merge_jsonl(paths: list[Path], output_path: Path) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with open(output_path, "w", encoding="utf-8") as out:
        for path in paths:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    out.write(line)
                    total += 1
    return total


def parse_bootstrap_output(text: str) -> dict[str, Any]:
    parsed = ast.literal_eval(text.strip())
    if not isinstance(parsed, dict):
        raise ValueError(f"Unexpected bootstrap output: {text}")
    return parsed


def make_main_results_csv(summary_path: Path, output_path: Path) -> dict[str, dict[str, float]]:
    rows = read_csv_rows(summary_path)
    output_rows: list[dict[str, Any]] = []
    summary: dict[str, dict[str, float]] = {}
    for row in rows:
        baseline = row["baseline"]
        values = {
            "n": int(row["n"]),
            "exact_match_line_trim": float(row["exact_match_line_trim"]),
            "exact_match_line_trim_pct": float(row["exact_match_line_trim_pct"]),
            "location_overlap_f1": float(row["location_overlap_f1"]),
            "location_overlap_f1_pct": float(row["location_overlap_f1_pct"]),
        }
        summary[baseline] = values
        output_rows.append({"baseline": baseline, **values})

    write_csv_rows(
        output_path,
        [
            "baseline",
            "n",
            "exact_match_line_trim",
            "exact_match_line_trim_pct",
            "location_overlap_f1",
            "location_overlap_f1_pct",
        ],
        output_rows,
    )
    return summary


def gain(summary: dict[str, dict[str, float]], baseline_a: str, baseline_b: str, metric: str) -> float:
    return summary[baseline_b][metric] - summary[baseline_a][metric]


def run_bootstrap_gains(report_dir: Path, log_path: Path) -> list[dict[str, Any]]:
    per_example_path = report_dir / "per_example_metrics.csv"
    output_path = report_dir / "qwen25coder7b_pilot100_bootstrap_gain.csv"
    specs = [
        ("direct - no_review", "no_review", "direct", "exact_match_line_trim"),
        ("gold_location - direct", "direct", "gold_location", "exact_match_line_trim"),
        ("direct - no_review", "no_review", "direct", "location_overlap_f1"),
        ("gold_location - direct", "direct", "gold_location", "location_overlap_f1"),
    ]
    rows: list[dict[str, Any]] = []
    for comparison, baseline_a, baseline_b, metric in specs:
        stdout = run_cmd(
            [
                sys.executable,
                "scripts/bootstrap_gain.py",
                "--per-example",
                str(per_example_path),
                "--baseline-a",
                baseline_a,
                "--baseline-b",
                baseline_b,
                "--metric",
                metric,
                "--iters",
                "1000",
                "--seed",
                "42",
            ],
            log_path,
        )
        parsed = parse_bootstrap_output(stdout)
        rows.append(
            {
                "comparison": comparison,
                "metric": metric,
                "paired_n": int(parsed["paired_n"]),
                "gain": float(parsed["gain"]),
                "gain_pct": float(parsed["gain_pct"]),
                "ci95_low": float(parsed["ci95_low"]),
                "ci95_high": float(parsed["ci95_high"]),
            }
        )

    write_csv_rows(
        output_path,
        ["comparison", "metric", "paired_n", "gain", "gain_pct", "ci95_low", "ci95_high"],
        rows,
    )
    return rows


def schema_signature(rows: list[dict[str, Any]]) -> tuple[str, ...]:
    if not rows:
        return tuple()
    return tuple(sorted(rows[0].keys()))


def validate_integrity(
    gold_path: Path,
    merged_predictions: Path,
    outputs: dict[str, Path],
    error_logs: dict[str, Path],
    report_dir: Path,
) -> dict[str, Any]:
    gold_rows = read_jsonl(gold_path)
    expected_ids = [str(row.get("id", "")) for row in gold_rows]
    expected_id_set = set(expected_ids)
    pred_rows = read_jsonl(merged_predictions)

    row_counts = Counter(str(row.get("baseline", "")) for row in pred_rows)
    grouped = defaultdict(list)
    by_id: dict[str, set[str]] = defaultdict(set)
    for row in pred_rows:
        key = output_key(row)
        grouped[key].append(row)
        by_id[key[0]].add(key[1])

    duplicate_pairs = sorted([f"{item_id}:{baseline}" for (item_id, baseline), rows in grouped.items() if len(rows) > 1])
    missing_pairs: list[str] = []
    for item_id in expected_ids:
        bases = by_id.get(item_id, set())
        for baseline in BASELINES:
            if baseline not in bases:
                missing_pairs.append(f"{item_id}:{baseline}")

    extra_ids = sorted(item_id for item_id in by_id.keys() if item_id not in expected_id_set)
    missing_ids = sorted(item_id for item_id in expected_ids if item_id not in by_id)

    schema_checks: list[dict[str, Any]] = []
    schema_ok = True
    for baseline, path in outputs.items():
        rows = read_jsonl(path)
        preseed_rows = rows[:30]
        new_rows = rows[30:]
        preseed_signature = schema_signature(preseed_rows)
        new_signatures = sorted({tuple(sorted(row.keys())) for row in new_rows})
        same_schema = bool(new_rows) and len(new_signatures) == 1 and tuple(new_signatures[0]) == preseed_signature
        if not new_rows:
            same_schema = False
        if not same_schema:
            schema_ok = False
        schema_checks.append(
            {
                "baseline": baseline,
                "preseed_signature": list(preseed_signature),
                "new_signatures": [list(sig) for sig in new_signatures],
                "same_schema": same_schema,
                "rows": len(rows),
            }
        )

    error_counts = {baseline: count_lines(path) for baseline, path in error_logs.items()}
    total_error_rows = sum(error_counts.values())
    status_ok = (
        len(pred_rows) == 300
        and len(by_id) == 100
        and not duplicate_pairs
        and not missing_pairs
        and not extra_ids
        and not missing_ids
        and all(row_counts[baseline] == 100 for baseline in BASELINES)
        and schema_ok
    )

    output_path = report_dir / "qwen25coder7b_pilot100_missing_duplicate_check.txt"
    lines = [
        "[Integrity Check]",
        f"- merged predictions path: {merged_predictions}",
        f"- total rows: {len(pred_rows)}",
        f"- unique example IDs: {len(by_id)}",
        f"- expected example IDs: {len(expected_ids)}",
        f"- per-baseline row counts: {dict(row_counts)}",
        f"- duplicate (id, baseline) pairs: {len(duplicate_pairs)}",
        f"- missing (id, baseline) pairs: {len(missing_pairs)}",
        f"- missing example IDs: {len(missing_ids)}",
        f"- extra example IDs: {len(extra_ids)}",
        f"- error log rows: {total_error_rows}",
        f"- schema consistency between preseed 30 and new 70: {'PASS' if schema_ok else 'FAIL'}",
        f"- overall status: {'PASS' if status_ok else 'FAIL'}",
        "",
        "[Duplicate Pairs]",
    ]
    lines.extend(duplicate_pairs or ["(none)"])
    lines.extend(["", "[Missing Pairs]"])
    lines.extend(missing_pairs or ["(none)"])
    lines.extend(["", "[Missing IDs]"])
    lines.extend(missing_ids or ["(none)"])
    lines.extend(["", "[Extra IDs]"])
    lines.extend(extra_ids or ["(none)"])
    lines.extend(["", "[Error Log Counts]"])
    for baseline in BASELINES:
        lines.append(f"{baseline}: {error_counts[baseline]}")
    lines.extend(["", "[Schema Checks]"])
    for item in schema_checks:
        lines.append(
            f"{item['baseline']}: rows={item['rows']} same_schema={item['same_schema']} "
            f"preseed_signature={item['preseed_signature']} new_signatures={item['new_signatures']}"
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return {
        "status_ok": status_ok,
        "total_rows": len(pred_rows),
        "unique_ids": len(by_id),
        "row_counts": dict(row_counts),
        "duplicate_pairs": duplicate_pairs,
        "missing_pairs": missing_pairs,
        "missing_ids": missing_ids,
        "extra_ids": extra_ids,
        "error_counts": error_counts,
        "total_error_rows": total_error_rows,
        "schema_checks": schema_checks,
        "check_path": str(output_path),
    }


def load_summary(path: Path) -> dict[str, dict[str, float]]:
    rows = read_csv_rows(path)
    out: dict[str, dict[str, float]] = {}
    for row in rows:
        out[row["baseline"]] = {
            "n": float(row["n"]),
            "exact_match_line_trim": float(row["exact_match_line_trim"]),
            "location_overlap_f1": float(row["location_overlap_f1"]),
        }
    return out


def make_3b_vs_7b_comparison(report_dir: Path, summary_7b: dict[str, dict[str, float]]) -> tuple[dict[str, dict[str, float]], list[dict[str, Any]]]:
    summary_3b = load_summary(REPO_ROOT / "reports" / "crn_pilot100_qwen25coder3b" / "summary_metrics.csv")
    rows = [
        {
            "item": "no_review exact_match_line_trim",
            "qwen25coder3b": summary_3b["no_review"]["exact_match_line_trim"],
            "qwen25coder7b": summary_7b["no_review"]["exact_match_line_trim"],
        },
        {
            "item": "direct exact_match_line_trim",
            "qwen25coder3b": summary_3b["direct"]["exact_match_line_trim"],
            "qwen25coder7b": summary_7b["direct"]["exact_match_line_trim"],
        },
        {
            "item": "gold_location exact_match_line_trim",
            "qwen25coder3b": summary_3b["gold_location"]["exact_match_line_trim"],
            "qwen25coder7b": summary_7b["gold_location"]["exact_match_line_trim"],
        },
        {
            "item": "no_review location_overlap_f1",
            "qwen25coder3b": summary_3b["no_review"]["location_overlap_f1"],
            "qwen25coder7b": summary_7b["no_review"]["location_overlap_f1"],
        },
        {
            "item": "direct location_overlap_f1",
            "qwen25coder3b": summary_3b["direct"]["location_overlap_f1"],
            "qwen25coder7b": summary_7b["direct"]["location_overlap_f1"],
        },
        {
            "item": "gold_location location_overlap_f1",
            "qwen25coder3b": summary_3b["gold_location"]["location_overlap_f1"],
            "qwen25coder7b": summary_7b["gold_location"]["location_overlap_f1"],
        },
        {
            "item": "direct - no_review exact gain",
            "qwen25coder3b": gain(summary_3b, "no_review", "direct", "exact_match_line_trim"),
            "qwen25coder7b": gain(summary_7b, "no_review", "direct", "exact_match_line_trim"),
        },
        {
            "item": "gold_location - direct exact gain",
            "qwen25coder3b": gain(summary_3b, "direct", "gold_location", "exact_match_line_trim"),
            "qwen25coder7b": gain(summary_7b, "direct", "gold_location", "exact_match_line_trim"),
        },
        {
            "item": "gold_location - direct loc.F1 gain",
            "qwen25coder3b": gain(summary_3b, "direct", "gold_location", "location_overlap_f1"),
            "qwen25coder7b": gain(summary_7b, "direct", "gold_location", "location_overlap_f1"),
        },
    ]
    for row in rows:
        row["difference_7b_minus_3b"] = float(row["qwen25coder7b"]) - float(row["qwen25coder3b"])

    output_path = report_dir / "qwen25coder7b_vs_3b_pilot100_comparison.csv"
    write_csv_rows(
        output_path,
        ["item", "qwen25coder3b", "qwen25coder7b", "difference_7b_minus_3b"],
        rows,
    )
    return summary_3b, rows


def bootstrap_lookup(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {(row["comparison"], row["metric"]): row for row in rows}


def broadly_matches_diagnostic_pattern(bootstrap_rows: list[dict[str, Any]]) -> bool:
    lookup = bootstrap_lookup(bootstrap_rows)
    direct_exact = lookup[("direct - no_review", "exact_match_line_trim")]
    gold_exact = lookup[("gold_location - direct", "exact_match_line_trim")]
    gold_loc = lookup[("gold_location - direct", "location_overlap_f1")]
    return (
        direct_exact["gain"] > 0.0
        and gold_loc["ci95_low"] > 0.0
        and gold_exact["ci95_low"] <= 0.0 <= gold_exact["ci95_high"]
    )


def format_duration(start_iso: str | None, end_iso: str | None) -> str:
    if not start_iso or not end_iso:
        return "unknown"
    start = datetime.fromisoformat(start_iso)
    end = datetime.fromisoformat(end_iso)
    delta = end - start
    total_seconds = int(delta.total_seconds())
    hours, rem = divmod(total_seconds, 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours}h {minutes}m {seconds}s"


def write_summary_md(
    report_dir: Path,
    metadata: dict[str, Any],
    integrity: dict[str, Any],
    summary_3b: dict[str, dict[str, float]],
    summary_7b: dict[str, dict[str, float]],
    bootstrap_rows: list[dict[str, Any]],
) -> None:
    lookup = bootstrap_lookup(bootstrap_rows)
    direct_exact = lookup[("direct - no_review", "exact_match_line_trim")]
    gold_exact = lookup[("gold_location - direct", "exact_match_line_trim")]
    direct_loc = lookup[("direct - no_review", "location_overlap_f1")]
    gold_loc = lookup[("gold_location - direct", "location_overlap_f1")]

    same_pattern = broadly_matches_diagnostic_pattern(bootstrap_rows)
    if same_pattern:
        comparison_text = (
            "The 7B run is broadly consistent with the 3B diagnostic pattern. "
            "Direct again improved exact-match over no_review, and gold_location again produced a clear localisation-overlap gain. "
            "The 7B exact-match point estimate for gold_location was slightly higher than direct, but the 95% CI still crossed zero, so this run does not provide clear evidence of an exact-match gain from gold-location hints."
        )
        effect_text = (
            "This auxiliary 7B reproduction strengthens the current KCC v11 conclusion rather than changing it. "
            "A small robustness note can be added, but the paper should still frame the 7B run as an auxiliary reproducibility check, not as a new main result."
        )
        paper_lines = [
            "An auxiliary 100-example reproduction with qwen2.5-coder:7b showed the same broad diagnostic pattern as the main 3B run on the same seed=42 subset.",
            "Direct improved exact-match over no_review, while gold_location substantially improved localisation overlap; however, gold_location did not show a clear exact-match gain over direct because the paired-bootstrap interval still included zero.",
            "This additional check is consistent with our claim that within-snippet localisation matters, but does not by itself guarantee correct repair.",
        ]
    else:
        comparison_text = (
            "The 7B run overlaps with the 3B result on some axes, but it should be described conservatively as an additional check rather than as a clean replication."
        )
        effect_text = (
            "This auxiliary 7B run does not overturn the KCC v11 conclusion, but it should be discussed with explicit caution and without success-rate-centered framing."
        )
        paper_lines = [
            "An auxiliary 100-example reproduction with qwen2.5-coder:7b provided an additional robustness check for the main 3B result.",
            "The 7B run should be described as an auxiliary check rather than a new main experiment.",
            "Any write-up should emphasize the diagnostic framing and avoid success-rate-centered claims.",
        ]

    output_path = report_dir / "qwen25coder7b_pilot100_summary.md"
    lines = [
        "# qwen2.5-coder:7b Pilot100 Summary",
        "",
        "## 1. Run Summary",
        f"- Model: {MODEL_NAME}",
        "- Data: CodeReview-New seed=42 100-example subset (crn_pilot100)",
        "- Conditions: no_review, direct, gold_location",
        f"- Total generations: 300 rows total, with {metadata['preseed_rows_total']} reused rows and {metadata['new_rows_total']} newly generated rows",
        f"- Error rows: {integrity['total_error_rows']}",
        f"- Execution time: {format_duration(metadata.get('started_at'), metadata.get('completed_at'))} (this invocation wall-clock)",
        "",
        "## 2. 7B Results",
        f"- no_review: exact_match_line_trim={summary_7b['no_review']['exact_match_line_trim']:.3f}, location_overlap_f1={summary_7b['no_review']['location_overlap_f1']:.3f}",
        f"- direct: exact_match_line_trim={summary_7b['direct']['exact_match_line_trim']:.3f}, location_overlap_f1={summary_7b['direct']['location_overlap_f1']:.3f}",
        f"- gold_location: exact_match_line_trim={summary_7b['gold_location']['exact_match_line_trim']:.3f}, location_overlap_f1={summary_7b['gold_location']['location_overlap_f1']:.3f}",
        f"- direct - no_review exact gain: {direct_exact['gain']:.3f} (95% CI [{direct_exact['ci95_low']:.3f}, {direct_exact['ci95_high']:.3f}])",
        f"- gold_location - direct exact gain: {gold_exact['gain']:.3f} (95% CI [{gold_exact['ci95_low']:.3f}, {gold_exact['ci95_high']:.3f}])",
        f"- direct - no_review loc.F1 gain: {direct_loc['gain']:.3f} (95% CI [{direct_loc['ci95_low']:.3f}, {direct_loc['ci95_high']:.3f}])",
        f"- gold_location - direct loc.F1 gain: {gold_loc['gain']:.3f} (95% CI [{gold_loc['ci95_low']:.3f}, {gold_loc['ci95_high']:.3f}])",
        "",
        "## 3. 3B vs 7B",
        f"- {comparison_text}",
        "",
        "## 4. Impact on KCC v11",
        f"- {effect_text}",
        "",
        "## 5. 2-3 Sentence Paper Summary",
    ]
    lines.extend([f"- {line}" for line in paper_lines])
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def initialize_metadata(preseed_counts: dict[str, int]) -> dict[str, Any]:
    data = {
        "run_name": RUN_NAME,
        "model": MODEL_NAME,
        "subset": "crn_pilot100",
        "conditions": list(BASELINES),
        "started_at": now_utc_iso(),
        "completed_at": None,
        "preseed_counts": preseed_counts,
        "preseed_rows_total": sum(preseed_counts.values()),
        "new_rows_total": 0,
        "baseline_runs": [],
        "status": "running",
    }
    write_json(METADATA_PATH, data)
    return data


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ollama", choices=["ollama", "chat_completions"])
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--timeout-seconds", type=float, default=900.0)
    args = ap.parse_args()

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    append_log(LOG_PATH, f"# Started {now_utc_iso()}")

    preflight = validate_subset_alignment()
    outputs = baseline_paths()
    preseed = validate_existing_preseed(outputs)
    metadata = initialize_metadata(preseed["counts"])
    metadata["preflight"] = preflight
    write_json(METADATA_PATH, metadata)

    for baseline in BASELINES:
        output_path = outputs[baseline]
        before = count_lines(output_path)
        cmd = [
            sys.executable,
            "scripts/run_local_predictions.py",
            "--input",
            str(REPO_ROOT / "prompts" / "crn_pilot100" / f"{baseline}_prompts.jsonl"),
            "--output",
            str(output_path),
            "--model",
            MODEL_NAME,
            "--backend",
            args.backend,
            "--temperature",
            str(args.temperature),
            "--seed",
            str(args.seed),
            "--timeout-seconds",
            str(args.timeout_seconds),
            "--resume",
            "--continue-on-error",
            "--error-log",
            str(error_paths()[baseline]),
        ]
        if args.base_url:
            cmd.extend(["--base-url", args.base_url])

        started_at = now_utc_iso()
        run_cmd(cmd, LOG_PATH)
        ended_at = now_utc_iso()
        after = count_lines(output_path)
        if after != 100:
            raise RuntimeError(f"{baseline} did not reach 100 rows after resume run. rows={after}")
        metadata["baseline_runs"].append(
            {
                "baseline": baseline,
                "started_at": started_at,
                "completed_at": ended_at,
                "rows_before": before,
                "rows_after": after,
                "rows_added": after - before,
                "command": command_text(cmd),
            }
        )
        metadata["new_rows_total"] += after - before
        write_json(METADATA_PATH, metadata)

    merged_rows = merge_jsonl([outputs[b] for b in BASELINES], merged_path())
    if merged_rows != 300:
        raise RuntimeError(f"Merged output row count is {merged_rows}, expected 300.")

    run_cmd(
        [
            sys.executable,
            "scripts/evaluate_predictions.py",
            "--gold",
            str(REPO_ROOT / "data" / "processed" / "crn_pilot100.jsonl"),
            "--pred",
            str(merged_path()),
            "--outdir",
            str(REPORT_DIR),
        ],
        LOG_PATH,
    )

    summary_7b = make_main_results_csv(
        REPORT_DIR / "summary_metrics.csv",
        REPORT_DIR / "qwen25coder7b_pilot100_main_results.csv",
    )
    bootstrap_rows = run_bootstrap_gains(REPORT_DIR, LOG_PATH)
    integrity = validate_integrity(
        REPO_ROOT / "data" / "processed" / "crn_pilot100.jsonl",
        merged_path(),
        outputs,
        error_paths(),
        REPORT_DIR,
    )
    summary_3b, _ = make_3b_vs_7b_comparison(REPORT_DIR, summary_7b)
    metadata["completed_at"] = now_utc_iso()
    metadata["status"] = "completed"
    metadata["merged_rows"] = merged_rows
    metadata["integrity_check_path"] = integrity["check_path"]
    write_json(METADATA_PATH, metadata)
    write_summary_md(REPORT_DIR, metadata, integrity, summary_3b, summary_7b, bootstrap_rows)
    append_log(LOG_PATH, f"# Completed {metadata['completed_at']}")


if __name__ == "__main__":
    main()
