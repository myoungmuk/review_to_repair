#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
import random
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Iterable

from common import changed_line_set_old, changed_spans_old, normalize_newlines, read_jsonl


REPO_ROOT = Path(__file__).resolve().parent.parent
RUN_ROOT = REPO_ROOT / "results" / "multi_model_r2r_all_seed42_full_3models_qwen32b_ctx8192_20260525"
ALL_GENERATIONS = RUN_ROOT / "generations" / "all_generations.jsonl"
GOLD_PATH = REPO_ROOT / "data" / "processed" / "crn_all.jsonl"
BOOTSTRAP_PATH = RUN_ROOT / "bootstrap_gains_by_model.csv"
NUM_PREDICT = 512
NEAR_CAP_CHAR_THRESHOLD = int(NUM_PREDICT * 3.5)
MODELS = ["qwen2.5-coder:7b", "deepseek-coder:6.7b", "qwen2.5-coder:32b"]
CONDITIONS = ["no_review", "direct", "gold_location"]
RNG_SEED = 42


@dataclass(frozen=True)
class PairRows:
    direct: dict[str, Any]
    gold: dict[str, Any]


def ensure_dirs() -> None:
    for rel in [
        "results/tables",
        "results/analysis",
        "results/manual_audit",
        "reports",
    ]:
        (REPO_ROOT / rel).mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        keys: list[str] = []
        seen: set[str] = set()
        for row in rows:
            for key in row:
                if key not in seen:
                    seen.add(key)
                    keys.append(key)
        fieldnames = keys
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def fmt_dec(value: float) -> str:
    return f"{value:.6f}"


def fmt_pct(value: float) -> str:
    return f"{100.0 * value:.2f}"


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        vals = []
        for col in columns:
            value = row.get(col, "")
            if isinstance(value, float):
                vals.append(f"{value:.4f}")
            else:
                vals.append(str(value))
        lines.append("| " + " | ".join(vals) + " |")
    return "\n".join(lines)


def safe_float(value: Any) -> float:
    if value == "" or value is None:
        return 0.0
    return float(value)


def exact(row: dict[str, Any]) -> int:
    return int(float(row.get("exact_match_line_trim", 0) or 0))


def loc_f1(row: dict[str, Any]) -> float:
    return safe_float(row.get("location_overlap_f1", 0.0))


def mean(values: Iterable[float]) -> float:
    xs = list(values)
    return sum(xs) / len(xs) if xs else 0.0


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", normalize_newlines(text)))


def line_count(text: str) -> int:
    text = normalize_newlines(text)
    return len(text.splitlines())


def changed_tags(old: str, new: str) -> list[str]:
    old_lines = normalize_newlines(old).splitlines()
    new_lines = normalize_newlines(new).splitlines()
    sm = SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)
    return [tag for tag, *_ in sm.get_opcodes() if tag != "equal"]


def diff_type(old: str, new: str) -> str:
    tags = changed_tags(old, new)
    if not tags:
        return "no_change"
    uniq = set(tags)
    if uniq == {"replace"}:
        return "replace_only"
    if uniq == {"insert"}:
        return "insert_only"
    if uniq == {"delete"}:
        return "delete_only"
    return "mixed"


WRAPPER_RE = re.compile(
    r"(?i)\b(revised|updated|corrected)\s+(code|snippet)\b|"
    r"\bhere(?:'s| is)\s+(?:the\s+)?(?:revised|updated|corrected)?\s*code\b"
)


def output_flags(row: dict[str, Any]) -> dict[str, bool]:
    raw = normalize_newlines(row.get("raw_output", ""))
    extracted = normalize_newlines(row.get("extracted_code", row.get("prediction", "")))
    warning = str(row.get("warning", ""))
    target = normalize_newlines(row.get("target_code", ""))
    raw_len = len(raw)
    target_len = len(target)
    suspicious_long = raw_len >= 3000 or (target_len > 0 and raw_len >= max(1000, 3 * target_len))
    flags = {
        "unclosed_code_fence": raw.count("```") % 2 == 1,
        "near_generation_cap": raw_len >= NEAR_CAP_CHAR_THRESHOLD,
        "marker_echo": bool(re.search(r"GOLD_(?:LOCATION|INSERTION)", raw)),
        "wrapper_text": bool(WRAPPER_RE.search(raw)),
        "extraction_by_fenced_code_block": "code_fence" in warning,
        "extraction_by_raw_output": "code_fence" not in warning,
        "empty_extracted_output": not extracted.strip(),
        "suspiciously_long_output": suspicious_long,
        "suspiciously_short_output": bool(extracted.strip()) and len(extracted.strip()) < 20,
    }
    flags["any_suspicious_output_flag"] = any(
        flags[name]
        for name in [
            "unclosed_code_fence",
            "near_generation_cap",
            "marker_echo",
            "wrapper_text",
            "empty_extracted_output",
            "suspiciously_long_output",
            "suspiciously_short_output",
        ]
    )
    return flags


def flag_string(row: dict[str, Any]) -> str:
    flags = output_flags(row)
    names = [name for name, value in flags.items() if value and name != "any_suspicious_output_flag"]
    return ";".join(names)


def load_inputs() -> tuple[dict[str, dict[str, Any]], dict[tuple[str, str, str], dict[str, Any]]]:
    gold_rows = {str(row["id"]): row for row in read_jsonl(GOLD_PATH)}
    records = read_jsonl(ALL_GENERATIONS)
    by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in records:
        by_key[(str(row["model"]), str(row["condition"]), str(row["example_id"]))] = row
    return gold_rows, by_key


def rows_for_model_condition(
    by_key: dict[tuple[str, str, str], dict[str, Any]],
    model: str,
    condition: str,
) -> list[dict[str, Any]]:
    return [row for (m, c, _), row in by_key.items() if m == model and c == condition]


def paired_direct_gold(
    by_key: dict[tuple[str, str, str], dict[str, Any]],
    model: str,
    example_ids: Iterable[str],
) -> dict[str, PairRows]:
    out: dict[str, PairRows] = {}
    for ex_id in example_ids:
        d = by_key.get((model, "direct", ex_id))
        g = by_key.get((model, "gold_location", ex_id))
        if d is not None and g is not None:
            out[ex_id] = PairRows(direct=d, gold=g)
    return out


def write_bootstrap_ci() -> None:
    source_rows = read_csv_dicts(BOOTSTRAP_PATH)
    rows: list[dict[str, Any]] = []
    keep_models = set(MODELS + ["macro_average"])
    comparisons = {
        ("direct - no_review", "exact_match_line_trim"),
        ("direct - no_review", "location_overlap_f1"),
        ("gold_location - direct", "exact_match_line_trim"),
        ("gold_location - direct", "location_overlap_f1"),
    }
    for row in source_rows:
        key = (row["comparison"], row["metric"])
        if row["model"] not in keep_models or key not in comparisons:
            continue
        gain = float(row["gain"])
        lo = float(row["ci95_low"])
        hi = float(row["ci95_high"])
        rows.append(
            {
                "model": row["model"],
                "comparison": row["comparison"],
                "metric": row["metric"],
                "paired_n": int(row["paired_n"]),
                "gain_decimal": gain,
                "ci95_low_decimal": lo,
                "ci95_high_decimal": hi,
                "gain_percentage_points": 100.0 * gain,
                "ci95_low_percentage_points": 100.0 * lo,
                "ci95_high_percentage_points": 100.0 * hi,
            }
        )

    write_csv(REPO_ROOT / "results" / "tables" / "table_bootstrap_ci_3model_final.csv", rows)
    md_rows = [
        {
            "model": row["model"],
            "comparison": row["comparison"],
            "metric": row["metric"],
            "n": row["paired_n"],
            "gain": fmt_dec(row["gain_decimal"]),
            "95% CI": f"[{fmt_dec(row['ci95_low_decimal'])}, {fmt_dec(row['ci95_high_decimal'])}]",
            "gain pp": f"{row['gain_percentage_points']:.2f}",
            "95% CI pp": f"[{row['ci95_low_percentage_points']:.2f}, {row['ci95_high_percentage_points']:.2f}]",
        }
        for row in rows
    ]
    text = "\n".join(
        [
            "# Bootstrap CI Final",
            "",
            "- Source: completed 3-model full-data run.",
            "- Bootstrap: paired percentile bootstrap, iterations=1000, seed=42.",
            "- This table includes three models plus the 3-model macro average. No 2-model macro rows are included.",
            "",
            markdown_table(md_rows, ["model", "comparison", "metric", "n", "gain", "95% CI", "gain pp", "95% CI pp"]),
        ]
    )
    write_md(REPO_ROOT / "reports" / "10_bootstrap_ci_final.md", text)


def flip_summary_for_model(
    model: str,
    gold_rows: dict[str, dict[str, Any]],
    by_key: dict[tuple[str, str, str], dict[str, Any]],
) -> dict[str, Any]:
    pairs = paired_direct_gold(by_key, model, gold_rows.keys())
    dc_gw: list[tuple[str, PairRows]] = []
    dw_gc: list[tuple[str, PairRows]] = []
    dc_gc = 0
    dw_gw = 0
    over_edit = 0
    under_edit = 0
    loc_eq_1 = 0
    loc_ge_08 = 0
    flag_counts: dict[str, int] = defaultdict(int)
    degraded_flag_counts: dict[str, int] = defaultdict(int)

    for ex_id, pair in pairs.items():
        d_ok = exact(pair.direct) == 1
        g_ok = exact(pair.gold) == 1
        for prefix, row in [("direct", pair.direct), ("gold_location", pair.gold)]:
            for name, value in output_flags(row).items():
                if value:
                    flag_counts[f"{prefix}_{name}_count"] += 1
        if d_ok and not g_ok:
            dc_gw.append((ex_id, pair))
            if loc_f1(pair.gold) == 1.0:
                loc_eq_1 += 1
            if loc_f1(pair.gold) >= 0.8:
                loc_ge_08 += 1
            old = str(pair.gold.get("old_snippet", ""))
            target = str(pair.gold.get("target_code", ""))
            pred = str(pair.gold.get("extracted_code", pair.gold.get("prediction", "")))
            gold_changed = changed_line_set_old(old, target)
            pred_changed = changed_line_set_old(old, pred)
            if gold_changed and gold_changed.issubset(pred_changed) and len(pred_changed) > len(gold_changed):
                over_edit += 1
            if pred_changed and pred_changed.issubset(gold_changed) and len(pred_changed) < len(gold_changed):
                under_edit += 1
            for prefix, row in [("direct", pair.direct), ("gold_location", pair.gold)]:
                for name, value in output_flags(row).items():
                    if value:
                        degraded_flag_counts[f"degraded_{prefix}_{name}_count"] += 1
        elif not d_ok and g_ok:
            dw_gc.append((ex_id, pair))
        elif d_ok and g_ok:
            dc_gc += 1
        else:
            dw_gw += 1

    total = len(pairs)
    degraded_n = len(dc_gw)
    improved_n = len(dw_gc)
    row: dict[str, Any] = {
        "model": model,
        "total_pairs": total,
        "direct_correct_gold_wrong": degraded_n,
        "direct_wrong_gold_correct": improved_n,
        "direct_correct_gold_correct": dc_gc,
        "direct_wrong_gold_wrong": dw_gw,
        "direct_exact_rate": degraded_n / total + dc_gc / total if total else 0.0,
        "gold_location_exact_rate": improved_n / total + dc_gc / total if total else 0.0,
        "net_exact_change_count": improved_n - degraded_n,
        "net_exact_change_rate": (improved_n - degraded_n) / total if total else 0.0,
        "dc_gw_gold_loc_f1_eq_1_count": loc_eq_1,
        "dc_gw_gold_loc_f1_eq_1_rate_among_dc_gw": loc_eq_1 / degraded_n if degraded_n else 0.0,
        "dc_gw_gold_loc_f1_ge_0_8_count": loc_ge_08,
        "dc_gw_gold_loc_f1_ge_0_8_rate_among_dc_gw": loc_ge_08 / degraded_n if degraded_n else 0.0,
        "dc_gw_over_edit_suspect_count": over_edit,
        "dc_gw_over_edit_suspect_rate": over_edit / degraded_n if degraded_n else 0.0,
        "dc_gw_under_edit_suspect_count": under_edit,
        "dc_gw_under_edit_suspect_rate": under_edit / degraded_n if degraded_n else 0.0,
    }
    row.update(flag_counts)
    row.update(degraded_flag_counts)
    return row


def write_flip_analysis(gold_rows: dict[str, dict[str, Any]], by_key: dict[tuple[str, str, str], dict[str, Any]]) -> None:
    rows = [flip_summary_for_model(model, gold_rows, by_key) for model in MODELS]
    qwen32 = [row for row in rows if row["model"] == "qwen2.5-coder:32b"]
    write_csv(REPO_ROOT / "results" / "analysis" / "qwen32b_flip_analysis.csv", qwen32)
    write_csv(REPO_ROOT / "results" / "tables" / "table_flip_analysis_all_models_final.csv", rows)

    q = qwen32[0]
    md = "\n".join(
        [
            "# Qwen 32B Flip Analysis",
            "",
            "Scope: paired `direct` vs `gold_location` rows for `qwen2.5-coder:32b`.",
            "",
            f"- Total pairs: {q['total_pairs']}",
            f"- direct correct -> gold_location wrong: {q['direct_correct_gold_wrong']} ({fmt_pct(q['direct_correct_gold_wrong'] / q['total_pairs'])}%)",
            f"- direct wrong -> gold_location correct: {q['direct_wrong_gold_correct']} ({fmt_pct(q['direct_wrong_gold_correct'] / q['total_pairs'])}%)",
            f"- both correct: {q['direct_correct_gold_correct']}",
            f"- both wrong: {q['direct_wrong_gold_wrong']}",
            f"- Net exact change: {q['net_exact_change_count']} examples ({fmt_pct(q['net_exact_change_rate'])} pp)",
            "",
            "Among direct-correct -> gold-location-wrong cases:",
            f"- gold_location location F1 = 1.0: {q['dc_gw_gold_loc_f1_eq_1_count']} ({fmt_pct(q['dc_gw_gold_loc_f1_eq_1_rate_among_dc_gw'])}%)",
            f"- gold_location location F1 >= 0.8: {q['dc_gw_gold_loc_f1_ge_0_8_count']} ({fmt_pct(q['dc_gw_gold_loc_f1_ge_0_8_rate_among_dc_gw'])}%)",
            f"- Over-edit suspect: {q['dc_gw_over_edit_suspect_count']} ({fmt_pct(q['dc_gw_over_edit_suspect_rate'])}%)",
            f"- Under-edit suspect: {q['dc_gw_under_edit_suspect_count']} ({fmt_pct(q['dc_gw_under_edit_suspect_rate'])}%)",
            "",
            "All-model flip table:",
            "",
            markdown_table(
                rows,
                [
                    "model",
                    "total_pairs",
                    "direct_correct_gold_wrong",
                    "direct_wrong_gold_correct",
                    "direct_correct_gold_correct",
                    "direct_wrong_gold_wrong",
                    "net_exact_change_count",
                    "net_exact_change_rate",
                    "dc_gw_gold_loc_f1_eq_1_count",
                    "dc_gw_gold_loc_f1_ge_0_8_count",
                    "dc_gw_over_edit_suspect_count",
                    "dc_gw_under_edit_suspect_count",
                ],
            ),
        ]
    )
    write_md(REPO_ROOT / "reports" / "11_qwen32b_flip_analysis.md", md)


def write_output_format_and_sensitivity(
    gold_rows: dict[str, dict[str, Any]],
    by_key: dict[tuple[str, str, str], dict[str, Any]],
) -> None:
    flag_names = [
        "unclosed_code_fence",
        "near_generation_cap",
        "marker_echo",
        "wrapper_text",
        "extraction_by_fenced_code_block",
        "extraction_by_raw_output",
        "empty_extracted_output",
        "suspiciously_long_output",
        "suspiciously_short_output",
        "any_suspicious_output_flag",
    ]
    flag_rows: list[dict[str, Any]] = []
    for model in MODELS:
        for condition in CONDITIONS:
            rows = rows_for_model_condition(by_key, model, condition)
            out = {"model": model, "condition": condition, "n_output": len(rows)}
            for name in flag_names:
                out[f"{name}_count"] = sum(1 for row in rows if output_flags(row)[name])
                out[f"{name}_rate"] = out[f"{name}_count"] / len(rows) if rows else 0.0
            flag_rows.append(out)
    write_csv(REPO_ROOT / "results" / "tables" / "table_output_format_flags.csv", flag_rows)

    scenarios = [
        ("all_cases", None),
        ("without_unclosed_code_fence", "unclosed_code_fence"),
        ("without_near_generation_cap", "near_generation_cap"),
        ("without_marker_echo", "marker_echo"),
        ("without_any_suspicious_output_flag", "any_suspicious_output_flag"),
    ]
    sensitivity_rows: list[dict[str, Any]] = []
    for scenario, flag in scenarios:
        model_rows: list[dict[str, Any]] = []
        for model in MODELS:
            pairs = paired_direct_gold(by_key, model, gold_rows.keys())
            kept: list[PairRows] = []
            removed = 0
            for pair in pairs.values():
                if flag and (output_flags(pair.direct)[flag] or output_flags(pair.gold)[flag]):
                    removed += 1
                    continue
                kept.append(pair)
            d_exact = mean(exact(pair.direct) for pair in kept)
            g_exact = mean(exact(pair.gold) for pair in kept)
            d_f1 = mean(loc_f1(pair.direct) for pair in kept)
            g_f1 = mean(loc_f1(pair.gold) for pair in kept)
            row = {
                "scenario": scenario,
                "model": model,
                "paired_n": len(kept),
                "removed_pair_count": removed,
                "direct_exact": d_exact,
                "gold_location_exact": g_exact,
                "gold_minus_direct_exact": g_exact - d_exact,
                "direct_location_f1": d_f1,
                "gold_location_f1": g_f1,
                "gold_minus_direct_location_f1": g_f1 - d_f1,
            }
            sensitivity_rows.append(row)
            model_rows.append(row)
        sensitivity_rows.append(
            {
                "scenario": scenario,
                "model": "macro_average",
                "paired_n": min(int(row["paired_n"]) for row in model_rows),
                "removed_pair_count": sum(int(row["removed_pair_count"]) for row in model_rows),
                "direct_exact": mean(float(row["direct_exact"]) for row in model_rows),
                "gold_location_exact": mean(float(row["gold_location_exact"]) for row in model_rows),
                "gold_minus_direct_exact": mean(float(row["gold_minus_direct_exact"]) for row in model_rows),
                "direct_location_f1": mean(float(row["direct_location_f1"]) for row in model_rows),
                "gold_location_f1": mean(float(row["gold_location_f1"]) for row in model_rows),
                "gold_minus_direct_location_f1": mean(float(row["gold_minus_direct_location_f1"]) for row in model_rows),
            }
        )
    write_csv(REPO_ROOT / "results" / "tables" / "table_sensitivity_without_flagged_cases.csv", sensitivity_rows)

    qwen32_rows = [row for row in sensitivity_rows if row["model"] == "qwen2.5-coder:32b"]
    md = "\n".join(
        [
            "# Output Format And Truncation Sensitivity",
            "",
            f"Near generation cap is defined as `raw_output` length >= {NEAR_CAP_CHAR_THRESHOLD} characters, matching the existing run diagnostic heuristic (`num_predict * 3.5`).",
            "`any_suspicious_output_flag` removes pairs where either direct or gold_location has unclosed fence, near-cap output, marker echo, wrapper text, empty extracted output, suspiciously long output, or suspiciously short output. Extraction method flags are reported but are not treated as suspicious by themselves.",
            "",
            "## Flag Counts",
            markdown_table(
                flag_rows,
                [
                    "model",
                    "condition",
                    "n_output",
                    "unclosed_code_fence_count",
                    "near_generation_cap_count",
                    "marker_echo_count",
                    "wrapper_text_count",
                    "extraction_by_fenced_code_block_count",
                    "extraction_by_raw_output_count",
                    "empty_extracted_output_count",
                    "suspiciously_long_output_count",
                    "suspiciously_short_output_count",
                    "any_suspicious_output_flag_count",
                ],
            ),
            "",
            "## Qwen 32B Sensitivity",
            markdown_table(
                qwen32_rows,
                [
                    "scenario",
                    "paired_n",
                    "removed_pair_count",
                    "direct_exact",
                    "gold_location_exact",
                    "gold_minus_direct_exact",
                    "direct_location_f1",
                    "gold_location_f1",
                    "gold_minus_direct_location_f1",
                ],
            ),
            "",
            "## All Models",
            markdown_table(
                sensitivity_rows,
                [
                    "scenario",
                    "model",
                    "paired_n",
                    "removed_pair_count",
                    "gold_minus_direct_exact",
                    "gold_minus_direct_location_f1",
                ],
            ),
        ]
    )
    write_md(REPO_ROOT / "reports" / "12_output_format_sensitivity.md", md)


def metrics_for_rows(rows_by_condition: dict[str, list[dict[str, Any]]]) -> dict[str, float]:
    out: dict[str, float] = {}
    for condition in CONDITIONS:
        rows = rows_by_condition.get(condition, [])
        out[f"{condition}_exact"] = mean(exact(row) for row in rows)
        out[f"{condition}_location_f1"] = mean(loc_f1(row) for row in rows)
    out["direct_minus_no_review_exact"] = out["direct_exact"] - out["no_review_exact"]
    out["gold_location_minus_direct_exact"] = out["gold_location_exact"] - out["direct_exact"]
    out["direct_minus_no_review_location_f1"] = out["direct_location_f1"] - out["no_review_location_f1"]
    out["gold_location_minus_direct_location_f1"] = out["gold_location_location_f1"] - out["direct_location_f1"]
    return out


def write_diff_type_analysis(gold_rows: dict[str, dict[str, Any]], by_key: dict[tuple[str, str, str], dict[str, Any]]) -> None:
    diff_by_id = {ex_id: diff_type(str(row.get("old", "")), str(row.get("new", ""))) for ex_id, row in gold_rows.items()}
    diff_types = ["replace_only", "insert_only", "delete_only", "mixed", "no_change"]
    rows: list[dict[str, Any]] = []
    for model in MODELS:
        for dtype in diff_types:
            ids = [ex_id for ex_id, dt in diff_by_id.items() if dt == dtype]
            if not ids:
                continue
            by_condition: dict[str, list[dict[str, Any]]] = {}
            for condition in CONDITIONS:
                by_condition[condition] = [
                    by_key[(model, condition, ex_id)]
                    for ex_id in ids
                    if (model, condition, ex_id) in by_key
                ]
            metric = metrics_for_rows(by_condition)
            rows.append({"model": model, "diff_type": dtype, "example_count": len(ids), **metric})

    for dtype in diff_types:
        model_rows = [row for row in rows if row["diff_type"] == dtype and row["model"] in MODELS]
        if not model_rows:
            continue
        macro = {
            "model": "macro_average",
            "diff_type": dtype,
            "example_count": int(mean(float(row["example_count"]) for row in model_rows)),
        }
        for key in [
            "no_review_exact",
            "direct_exact",
            "gold_location_exact",
            "direct_minus_no_review_exact",
            "gold_location_minus_direct_exact",
            "no_review_location_f1",
            "direct_location_f1",
            "gold_location_location_f1",
            "direct_minus_no_review_location_f1",
            "gold_location_minus_direct_location_f1",
        ]:
            macro[key] = mean(float(row[key]) for row in model_rows)
        rows.append(macro)

    write_csv(REPO_ROOT / "results" / "tables" / "table_diff_type_analysis_3model_final.csv", rows)
    md = "\n".join(
        [
            "# Diff-Type Analysis",
            "",
            "Diff type is computed from the gold `old` -> `new` snippet using line-level `SequenceMatcher` opcodes.",
            "",
            markdown_table(
                rows,
                [
                    "model",
                    "diff_type",
                    "example_count",
                    "no_review_exact",
                    "direct_exact",
                    "gold_location_exact",
                    "direct_minus_no_review_exact",
                    "gold_location_minus_direct_exact",
                    "no_review_location_f1",
                    "direct_location_f1",
                    "gold_location_location_f1",
                    "direct_minus_no_review_location_f1",
                    "gold_location_minus_direct_location_f1",
                ],
            ),
        ]
    )
    write_md(REPO_ROOT / "reports" / "13_diff_type_analysis.md", md)


def quantile_bounds(values: list[float]) -> tuple[float, float, float]:
    xs = sorted(values)
    if not xs:
        return 0.0, 0.0, 0.0

    def q(p: float) -> float:
        idx = int((len(xs) - 1) * p)
        return xs[idx]

    return q(0.25), q(0.50), q(0.75)


def bin_label(value: float, bounds: tuple[float, float, float]) -> str:
    q1, q2, q3 = bounds
    if value <= q1:
        return f"q1_le_{q1:g}"
    if value <= q2:
        return f"q2_{q1:g}_to_{q2:g}"
    if value <= q3:
        return f"q3_{q2:g}_to_{q3:g}"
    return f"q4_gt_{q3:g}"


def feature_values_for_model(
    model: str,
    gold_rows: dict[str, dict[str, Any]],
    by_key: dict[tuple[str, str, str], dict[str, Any]],
) -> dict[str, dict[str, float]]:
    values: dict[str, dict[str, float]] = defaultdict(dict)
    for ex_id, gold in gold_rows.items():
        old = str(gold.get("old", ""))
        new = str(gold.get("new", ""))
        values["old_snippet_line_count"][ex_id] = line_count(old)
        values["review_word_count"][ex_id] = word_count(str(gold.get("review", "")))
        values["gold_new_line_count"][ex_id] = line_count(new)
        values["number_changed_spans"][ex_id] = float(gold.get("num_gold_spans", len(changed_spans_old(old, new))))
        values["number_changed_lines"][ex_id] = float(
            gold.get("num_gold_changed_old_lines", len(changed_line_set_old(old, new)))
        )
        for condition in ["direct", "gold_location"]:
            row = by_key.get((model, condition, ex_id))
            if row is None:
                continue
            output = str(row.get("extracted_code", row.get("prediction", "")))
            values[f"{condition}_output_line_count"][ex_id] = line_count(output)
            values[f"{condition}_output_word_count"][ex_id] = word_count(output)
            values[f"{condition}_output_char_count"][ex_id] = len(normalize_newlines(output))
    return values


def write_length_complexity_analysis(
    gold_rows: dict[str, dict[str, Any]],
    by_key: dict[tuple[str, str, str], dict[str, Any]],
) -> None:
    rows: list[dict[str, Any]] = []
    for model in MODELS:
        pairs = paired_direct_gold(by_key, model, gold_rows.keys())
        feature_values = feature_values_for_model(model, gold_rows, by_key)
        for feature, by_id in feature_values.items():
            ids = [ex_id for ex_id in pairs if ex_id in by_id]
            if not ids:
                continue
            bounds = quantile_bounds([by_id[ex_id] for ex_id in ids])
            grouped: dict[str, list[str]] = defaultdict(list)
            for ex_id in ids:
                grouped[bin_label(by_id[ex_id], bounds)].append(ex_id)
            for label, group_ids in grouped.items():
                pair_list = [pairs[ex_id] for ex_id in group_ids]
                d_exact = mean(exact(pair.direct) for pair in pair_list)
                g_exact = mean(exact(pair.gold) for pair in pair_list)
                d_f1 = mean(loc_f1(pair.direct) for pair in pair_list)
                g_f1 = mean(loc_f1(pair.gold) for pair in pair_list)
                rows.append(
                    {
                        "model": model,
                        "feature": feature,
                        "bin": label,
                        "n": len(pair_list),
                        "value_min": min(by_id[ex_id] for ex_id in group_ids),
                        "value_max": max(by_id[ex_id] for ex_id in group_ids),
                        "direct_exact": d_exact,
                        "gold_location_exact": g_exact,
                        "gold_minus_direct_exact": g_exact - d_exact,
                        "direct_location_f1": d_f1,
                        "gold_location_location_f1": g_f1,
                        "gold_minus_direct_location_f1": g_f1 - d_f1,
                        "direct_correct_gold_wrong_rate": mean(
                            1.0 if exact(pair.direct) == 1 and exact(pair.gold) == 0 else 0.0 for pair in pair_list
                        ),
                    }
                )
    write_csv(REPO_ROOT / "results" / "tables" / "table_length_complexity_analysis.csv", rows)

    q32_focus = [
        row
        for row in rows
        if row["model"] == "qwen2.5-coder:32b"
        and row["feature"]
        in {
            "old_snippet_line_count",
            "number_changed_spans",
            "number_changed_lines",
            "gold_location_output_char_count",
            "gold_location_output_line_count",
        }
    ]
    md = "\n".join(
        [
            "# Length And Complexity Analysis",
            "",
            "Rows are quartile bins per model and feature. Delta columns are `gold_location - direct`.",
            "",
            "## Qwen 32B Focus Features",
            markdown_table(
                q32_focus,
                [
                    "model",
                    "feature",
                    "bin",
                    "n",
                    "value_min",
                    "value_max",
                    "direct_exact",
                    "gold_location_exact",
                    "gold_minus_direct_exact",
                    "direct_location_f1",
                    "gold_location_location_f1",
                    "gold_minus_direct_location_f1",
                    "direct_correct_gold_wrong_rate",
                ],
            ),
            "",
            "Full table: `results/tables/table_length_complexity_analysis.csv`.",
        ]
    )
    write_md(REPO_ROOT / "reports" / "14_length_complexity_analysis.md", md)


def audit_row(
    category: str,
    model: str,
    ex_id: str,
    pair: PairRows,
    gold: dict[str, Any],
) -> dict[str, Any]:
    return {
        "audit_category": category,
        "example_id": ex_id,
        "model": model,
        "condition": "direct_vs_gold_location",
        "language": gold.get("language", ""),
        "old_code": gold.get("old", ""),
        "review": gold.get("review", ""),
        "gold_new_code": gold.get("new", ""),
        "direct_output": pair.direct.get("extracted_code", pair.direct.get("prediction", "")),
        "gold_location_output": pair.gold.get("extracted_code", pair.gold.get("prediction", "")),
        "direct_exact_match": exact(pair.direct),
        "gold_location_exact_match": exact(pair.gold),
        "direct_location_overlap_f1": loc_f1(pair.direct),
        "gold_location_location_overlap_f1": loc_f1(pair.gold),
        "diff_type": diff_type(str(gold.get("old", "")), str(gold.get("new", ""))),
        "direct_output_flags": flag_string(pair.direct),
        "gold_location_output_flags": flag_string(pair.gold),
        "label_candidate_options": "semantically_equivalent;content_mismatch;over_edit;under_edit;wrong_location;output_format_issue;truncation_suspected;uncertain",
        "manual_label": "",
    }


def sample_items(
    rng: random.Random,
    candidates: list[tuple[str, str, PairRows]],
    n: int,
    used: set[tuple[str, str]],
) -> list[tuple[str, str, PairRows]]:
    fresh = [item for item in candidates if (item[0], item[1]) not in used]
    if len(fresh) < n:
        fresh = candidates
    chosen = rng.sample(fresh, min(n, len(fresh)))
    for model, ex_id, _ in chosen:
        used.add((model, ex_id))
    return chosen


def write_manual_audit_sample(
    gold_rows: dict[str, dict[str, Any]],
    by_key: dict[tuple[str, str, str], dict[str, Any]],
) -> None:
    rng = random.Random(RNG_SEED)
    used: set[tuple[str, str]] = set()
    rows: list[dict[str, Any]] = []

    def pairs_for(model: str) -> dict[str, PairRows]:
        return paired_direct_gold(by_key, model, gold_rows.keys())

    q32 = pairs_for("qwen2.5-coder:32b")
    q7 = pairs_for("qwen2.5-coder:7b")
    all_pairs = {model: pairs_for(model) for model in MODELS}

    categories: list[tuple[str, int, list[tuple[str, str, PairRows]]]] = []
    categories.append(
        (
            "qwen32b_direct_correct_to_gold_wrong",
            50,
            [("qwen2.5-coder:32b", ex_id, pair) for ex_id, pair in q32.items() if exact(pair.direct) == 1 and exact(pair.gold) == 0],
        )
    )
    categories.append(
        (
            "qwen7b_direct_correct_to_gold_wrong",
            30,
            [("qwen2.5-coder:7b", ex_id, pair) for ex_id, pair in q7.items() if exact(pair.direct) == 1 and exact(pair.gold) == 0],
        )
    )
    categories.append(
        (
            "gold_location_f1_1_exact_wrong",
            50,
            [
                (model, ex_id, pair)
                for model, pairs in all_pairs.items()
                for ex_id, pair in pairs.items()
                if exact(pair.gold) == 0 and loc_f1(pair.gold) == 1.0
            ],
        )
    )
    categories.append(
        (
            "direct_wrong_to_gold_correct",
            30,
            [
                (model, ex_id, pair)
                for model, pairs in all_pairs.items()
                for ex_id, pair in pairs.items()
                if exact(pair.direct) == 0 and exact(pair.gold) == 1
            ],
        )
    )
    categories.append(
        (
            "random_exact_wrong_pair",
            20,
            [
                (model, ex_id, pair)
                for model, pairs in all_pairs.items()
                for ex_id, pair in pairs.items()
                if exact(pair.direct) == 0 or exact(pair.gold) == 0
            ],
        )
    )

    for category, n, candidates in categories:
        chosen = sample_items(rng, candidates, n, used)
        for model, ex_id, pair in chosen:
            rows.append(audit_row(category, model, ex_id, pair, gold_rows[ex_id]))

    write_csv(REPO_ROOT / "results" / "manual_audit" / "manual_audit_sample_180.csv", rows)

    md_lines = [
        "# Manual Audit Sample",
        "",
        "No manual labels have been assigned. Use one of: `semantically_equivalent`, `content_mismatch`, `over_edit`, `under_edit`, `wrong_location`, `output_format_issue`, `truncation_suspected`, `uncertain`.",
        "",
        f"Total rows: {len(rows)}",
        "",
    ]
    for idx, row in enumerate(rows, 1):
        md_lines.extend(
            [
                f"## {idx}. {row['audit_category']} / {row['model']} / {row['example_id']}",
                "",
                f"- language: {row['language']}",
                f"- diff_type: {row['diff_type']}",
                f"- direct_exact: {row['direct_exact_match']}, gold_exact: {row['gold_location_exact_match']}",
                f"- direct_location_f1: {row['direct_location_overlap_f1']:.4f}, gold_location_f1: {row['gold_location_location_overlap_f1']:.4f}",
                f"- direct_flags: {row['direct_output_flags'] or '(none)'}",
                f"- gold_location_flags: {row['gold_location_output_flags'] or '(none)'}",
                "",
                "### Review",
                "",
                str(row["review"]),
                "",
                "### Old Code",
                "",
                "```text",
                str(row["old_code"]),
                "```",
                "",
                "### Gold New Code",
                "",
                "```text",
                str(row["gold_new_code"]),
                "```",
                "",
                "### Direct Output",
                "",
                "```text",
                str(row["direct_output"]),
                "```",
                "",
                "### Gold-Location Output",
                "",
                "```text",
                str(row["gold_location_output"]),
                "```",
                "",
                "### Manual Label",
                "",
                "- label: ",
                "- notes: ",
                "",
            ]
        )
    write_md(REPO_ROOT / "results" / "manual_audit" / "manual_audit_sample_180.md", "\n".join(md_lines))


def extract_pdf_text(pdf_path: Path) -> tuple[str, str]:
    try:
        proc = subprocess.run(["pdftotext", str(pdf_path), "-"], text=True, capture_output=True, timeout=60)
    except Exception as exc:
        return "", f"pdftotext failed: {exc}"
    if proc.returncode != 0:
        return "", (proc.stderr or proc.stdout).strip()
    return proc.stdout, ""


def write_paper_update_checklist() -> None:
    shared = REPO_ROOT.parent / "gpt-shared"
    files = sorted(shared.rglob("*")) if shared.exists() else []
    text_parts: list[str] = []
    per_file_text: dict[str, str] = {}
    notes: list[str] = []
    inspected_files: list[str] = []
    editable_sources = [p for p in files if p.suffix.lower() in {".tex", ".md", ".txt", ".rtf", ".html"}]
    for path in editable_sources:
        try:
            file_text = path.read_text(encoding="utf-8", errors="ignore")
            text_parts.append(file_text)
            per_file_text[str(path)] = file_text
            inspected_files.append(str(path))
        except Exception as exc:
            notes.append(f"Could not read {path}: {exc}")
    if not editable_sources:
        notes.append("No editable text source (.tex/.md/.txt/.rtf/.html) found in gpt-shared; inspected PDF text instead.")
    for pdf in [p for p in files if p.suffix.lower() == ".pdf"]:
        text, err = extract_pdf_text(pdf)
        if text:
            text_parts.append(text)
            per_file_text[str(pdf)] = text
            inspected_files.append(str(pdf))
        elif err:
            notes.append(f"Could not extract PDF text from {pdf}: {err}")

    text = "\n".join(text_parts)
    normalized = re.sub(r"\s+", " ", text)
    stale_patterns = [
        "두 로컬 코드 LLM",
        "두 모델",
        "2모델 평균",
        "89,130개 출력",
        "7B 수준의 두 로컬 모델에 한정",
        "no_review exact 0.003",
        "direct exact 0.049",
        "gold_location exact 0.036",
        "direct F1 0.469",
        "gold F1 0.575",
        "0.003",
        "0.049",
        "0.036",
        "0.469",
        "0.575",
    ]
    replacement_patterns = [
        "세 로컬 코드 LLM",
        "두 7B급 모델과 하나의 32B 모델",
        "3모델 macro average",
        "133,695개 출력",
        "상용 폐쇄형 모델과 다른 모델 family로의 일반화는 추가 검증 필요",
    ]
    rows: list[dict[str, Any]] = []
    for pattern in stale_patterns:
        rows.append(
            {
                "type": "stale_expression",
                "pattern": pattern,
                "found": pattern in normalized,
                "count": normalized.count(pattern),
            }
        )
    for pattern in replacement_patterns:
        rows.append(
            {
                "type": "replacement_expression",
                "pattern": pattern,
                "found": pattern in normalized,
                "count": normalized.count(pattern),
            }
        )
    final_pdf_rows: list[dict[str, Any]] = []
    final_pdf_path = shared / "심사용 논문_최종.pdf"
    final_pdf_text = per_file_text.get(str(final_pdf_path), "")
    final_pdf_normalized = re.sub(r"\s+", " ", final_pdf_text)
    for pattern in stale_patterns + replacement_patterns:
        final_pdf_rows.append(
            {
                "pattern": pattern,
                "found_in_final_pdf": pattern in final_pdf_normalized,
                "final_pdf_count": final_pdf_normalized.count(pattern),
            }
        )

    md = "\n".join(
        [
            "# Paper Update Checklist",
            "",
            "This checklist scans the available `gpt-shared` paper files for stale 2-model wording and expected 3-model wording.",
            "",
            "## Inspected Files",
            "\n".join(f"- {path}" for path in inspected_files) if inspected_files else "- (none)",
            "",
            "## Notes",
            "\n".join(f"- {note}" for note in notes) if notes else "- No extraction notes.",
            "",
            "## Pattern Check",
            markdown_table(rows, ["type", "pattern", "found", "count"]),
            "",
            "## Final PDF Only",
            markdown_table(final_pdf_rows, ["pattern", "found_in_final_pdf", "final_pdf_count"]),
            "",
            "## Required Update Targets",
            "- Replace 2-model framing with 3-model framing.",
            "- Replace `89,130` outputs with `133,695` outputs.",
            "- Replace old 2-model macro-average numbers with the 3-model macro-average values from `results/tables/table_bootstrap_ci_3model_final.csv` and `results/tables/table_diff_type_analysis_3model_final.csv` as appropriate.",
            "- Add a limitation that generalization to commercial closed models and other model families still requires validation.",
        ]
    )
    write_md(REPO_ROOT / "reports" / "15_paper_update_checklist.md", md)


def load_table(path: Path) -> list[dict[str, str]]:
    return read_csv_dicts(path)


def write_final_report() -> None:
    bootstrap = load_table(REPO_ROOT / "results" / "tables" / "table_bootstrap_ci_3model_final.csv")
    flip = load_table(REPO_ROOT / "results" / "analysis" / "qwen32b_flip_analysis.csv")[0]
    sensitivity = load_table(REPO_ROOT / "results" / "tables" / "table_sensitivity_without_flagged_cases.csv")
    diff_rows = load_table(REPO_ROOT / "results" / "tables" / "table_diff_type_analysis_3model_final.csv")
    length_rows = load_table(REPO_ROOT / "results" / "tables" / "table_length_complexity_analysis.csv")
    audit_rows = load_table(REPO_ROOT / "results" / "manual_audit" / "manual_audit_sample_180.csv")

    q32_sens = [row for row in sensitivity if row["model"] == "qwen2.5-coder:32b"]
    macro_diff = [row for row in diff_rows if row["model"] == "macro_average"]
    q32_length_focus = [
        row
        for row in length_rows
        if row["model"] == "qwen2.5-coder:32b" and row["feature"] in {"old_snippet_line_count", "gold_location_output_char_count", "number_changed_spans"}
    ][:16]
    audit_counts: dict[str, int] = defaultdict(int)
    for row in audit_rows:
        audit_counts[row["audit_category"]] += 1

    recommended_wording = (
        "Across three local code LLMs and 14,855 CodeReview-New examples, review comments consistently improved both exact repair and "
        "location overlap over the no-review setting. In contrast, gold changed-location markers further improved location overlap but did not "
        "translate into higher exact repair accuracy; for the 32B Qwen model, exact match dropped from 12.08% in the direct condition to 4.18% "
        "with gold-location markers while location F1 increased from 65.30% to 70.07%. This suggests that, in snippet-level Review-to-Repair, "
        "knowing where to edit and generating the correct edit remain distinct capabilities."
    )
    claims_to_avoid = [
        "Do not claim gold location is harmful in all repair settings; this is snippet-level CodeReview-New with this prompt/post-processing setup.",
        "Do not claim full-file localization was solved or evaluated.",
        "Do not claim commercial closed models will show the same behavior.",
        "Do not treat location F1 gains as exact repair success.",
        "Do not hide output-format/truncation-risk sensitivity; report whether the exact drop persists after flagged-case removal.",
    ]

    md = "\n".join(
        [
            "# Final Post-analysis for Revision",
            "",
            "## 1. Main conclusion",
            "",
            "The completed 3-model run supports the central claim that review comments improve both exact repair and localization, while gold location markers improve localization but do not reliably improve exact repair. The strongest example is `qwen2.5-coder:32b`: direct exact is 12.08%, gold_location exact is 4.18%, direct location F1 is 65.30%, and gold_location location F1 is 70.07%.",
            "",
            "## 2. What the 32B result changes",
            "",
            f"For Qwen 32B, direct-correct -> gold-location-wrong cases are {flip['direct_correct_gold_wrong']} while direct-wrong -> gold-location-correct cases are {flip['direct_wrong_gold_correct']}. The net exact change is {flip['net_exact_change_count']} examples ({float(flip['net_exact_change_rate']) * 100:.2f} pp). This makes the location-vs-repair gap stronger than in the 7B-only framing.",
            "",
            "## 3. Bootstrap CI summary",
            "",
            markdown_table(
                bootstrap,
                [
                    "model",
                    "comparison",
                    "metric",
                    "paired_n",
                    "gain_decimal",
                    "ci95_low_decimal",
                    "ci95_high_decimal",
                    "gain_percentage_points",
                ],
            ),
            "",
            "## 4. Qwen 32B flip analysis",
            "",
            f"- direct correct -> gold wrong: {flip['direct_correct_gold_wrong']}",
            f"- direct wrong -> gold correct: {flip['direct_wrong_gold_correct']}",
            f"- both correct: {flip['direct_correct_gold_correct']}",
            f"- both wrong: {flip['direct_wrong_gold_wrong']}",
            f"- degraded cases with gold location F1 = 1.0: {flip['dc_gw_gold_loc_f1_eq_1_count']} ({float(flip['dc_gw_gold_loc_f1_eq_1_rate_among_dc_gw']) * 100:.2f}%)",
            f"- degraded cases with gold location F1 >= 0.8: {flip['dc_gw_gold_loc_f1_ge_0_8_count']} ({float(flip['dc_gw_gold_loc_f1_ge_0_8_rate_among_dc_gw']) * 100:.2f}%)",
            f"- over-edit suspects among degraded cases: {flip['dc_gw_over_edit_suspect_count']} ({float(flip['dc_gw_over_edit_suspect_rate']) * 100:.2f}%)",
            f"- under-edit suspects among degraded cases: {flip['dc_gw_under_edit_suspect_count']} ({float(flip['dc_gw_under_edit_suspect_rate']) * 100:.2f}%)",
            "",
            "## 5. Output-format sensitivity",
            "",
            markdown_table(
                q32_sens,
                [
                    "scenario",
                    "paired_n",
                    "removed_pair_count",
                    "direct_exact",
                    "gold_location_exact",
                    "gold_minus_direct_exact",
                    "direct_location_f1",
                    "gold_location_f1",
                    "gold_minus_direct_location_f1",
                ],
            ),
            "",
            "## 6. Diff-type analysis",
            "",
            markdown_table(
                macro_diff,
                [
                    "model",
                    "diff_type",
                    "example_count",
                    "direct_exact",
                    "gold_location_exact",
                    "gold_location_minus_direct_exact",
                    "direct_location_f1",
                    "gold_location_location_f1",
                    "gold_location_minus_direct_location_f1",
                ],
            ),
            "",
            "## 7. Length/complexity analysis",
            "",
            "The full length/complexity table is in `results/tables/table_length_complexity_analysis.csv`. A Qwen 32B subset is shown below for revision triage.",
            "",
            markdown_table(
                q32_length_focus,
                [
                    "model",
                    "feature",
                    "bin",
                    "n",
                    "direct_exact",
                    "gold_location_exact",
                    "gold_minus_direct_exact",
                    "direct_location_f1",
                    "gold_location_location_f1",
                    "gold_minus_direct_location_f1",
                ],
            ),
            "",
            "## 8. Manual audit sample summary",
            "",
            f"Manual audit sample generated: {len(audit_rows)} rows.",
            "",
            markdown_table(
                [{"audit_category": key, "count": value} for key, value in sorted(audit_counts.items())],
                ["audit_category", "count"],
            ),
            "",
            "## 9. Recommended paper wording",
            "",
            recommended_wording,
            "",
            "## 10. Claims to avoid",
            "",
            "\n".join(f"- {claim}" for claim in claims_to_avoid),
        ]
    )
    write_md(REPO_ROOT / "reports" / "16_final_post_analysis_for_revision.md", md)


def main() -> None:
    ensure_dirs()
    gold_rows, by_key = load_inputs()
    write_bootstrap_ci()
    write_flip_analysis(gold_rows, by_key)
    write_output_format_and_sensitivity(gold_rows, by_key)
    write_diff_type_analysis(gold_rows, by_key)
    write_length_complexity_analysis(gold_rows, by_key)
    write_manual_audit_sample(gold_rows, by_key)
    write_paper_update_checklist()
    write_final_report()
    print("post-analysis complete")


if __name__ == "__main__":
    main()
