#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import random
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parent))
from common import location_f1, normalize_newlines, read_jsonl, trim_line_ends
from run_local_predictions import backend_url, get_messages, make_dry_run_prediction, request_with_retry


REPO_ROOT = Path(__file__).resolve().parent.parent
FIXED_CONDITIONS = ("no_review", "direct", "gold_location")
METRICS = ("exact_match_line_trim", "location_overlap_f1")


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def repo_path(path: str | Path) -> Path:
    p = Path(path)
    if p.is_absolute():
        return p
    return REPO_ROOT / p


def read_json(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


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


def slugify_model(model: str) -> str:
    slug = model.lower().strip()
    slug = slug.replace(":", "-")
    slug = re.sub(r"[^a-z0-9._-]+", "-", slug)
    slug = slug.strip("-")
    return slug or "unknown-model"


def load_installed_ollama_models() -> tuple[list[str], str, str]:
    try:
        proc = subprocess.run(["ollama", "list"], cwd=REPO_ROOT, text=True, capture_output=True)
    except FileNotFoundError as exc:
        raise RuntimeError("Could not run `ollama list`; Ollama is not on PATH.") from exc
    if proc.returncode != 0:
        details = (proc.stderr or proc.stdout).strip()
        raise RuntimeError(f"`ollama list` failed: {details}")
    models: list[str] = []
    for idx, line in enumerate(proc.stdout.splitlines()):
        if idx == 0 or not line.strip():
            continue
        models.append(line.split()[0])
    return models, proc.stdout, proc.stderr


def select_default_models(config: dict[str, Any], installed: set[str]) -> tuple[list[str], list[dict[str, Any]]]:
    selected: list[str] = []
    missing: list[dict[str, Any]] = []
    for family in config.get("default_model_selection", []):
        candidates = [str(item) for item in family.get("candidates", [])]
        hit = next((model for model in candidates if model in installed), None)
        if hit:
            selected.append(hit)
            continue
        if family.get("required", True):
            missing.append(
                {
                    "label": family.get("label", "unknown_family"),
                    "candidates": candidates,
                    "install_hint": family.get("install_hint", ""),
                }
            )
    return selected, missing


def validate_conditions(config: dict[str, Any]) -> list[str]:
    conditions = [str(item) for item in config.get("conditions", FIXED_CONDITIONS)]
    if tuple(conditions) != FIXED_CONDITIONS:
        raise ValueError(
            "This runner intentionally supports only the original conditions: "
            f"{', '.join(FIXED_CONDITIONS)}. Got: {conditions}"
        )
    return conditions


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Run the seed=42 CodeReview-New Review-to-Repair diagnostic across multiple local code LLMs."
    )
    ap.add_argument("--config", default="configs/multi_model_r2r_seed42.json")
    ap.add_argument("--output-root", default=None, help="Defaults to results/<run_name> from the config")
    ap.add_argument("--models", nargs="+", default=None, help="Explicit model tags. Overrides default family selection.")
    ap.add_argument("--limit", type=int, default=None, help="Optional number of examples, e.g. 10 for smoke test.")
    ap.add_argument("--backend", choices=["ollama", "chat_completions"], default=None)
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--temperature", type=float, default=None)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--num-predict", type=int, default=None, help="Optional Ollama max generated tokens")
    ap.add_argument("--bootstrap-iters", type=int, default=None)
    ap.add_argument("--timeout-seconds", type=float, default=900.0)
    ap.add_argument(
        "--workers",
        type=int,
        default=1,
        help=(
            "Parallel backend requests per model/condition. Default 1 preserves the "
            "original sequential behavior; use 2-4 after a smoke test on large-GPU local servers."
        ),
    )
    ap.add_argument("--resume", action="store_true", help="Reuse rows already present in the generation files.")
    ap.add_argument(
        "--reuse-legacy-predictions",
        action="store_true",
        help="Allow reuse from config.existing_predictions. Off by default when the config disables it.",
    )
    ap.add_argument("--continue-on-error", action="store_true", help="Write an error row and continue after a generation failure.")
    ap.add_argument("--dry-run", action="store_true", help="Write placeholder generations without calling the backend.")
    ap.add_argument(
        "--skip-model-check",
        action="store_true",
        help="Skip installed-model validation. Intended only for dry-run schema checks or non-Ollama local servers.",
    )
    ap.add_argument("--check-models", action="store_true", help="Only check default/explicit model availability, then exit.")
    return ap.parse_args()


def error_message_for_missing_models(
    installed_models: list[str],
    selected: list[str],
    missing: list[dict[str, Any]],
) -> str:
    lines = [
        "Required Ollama model families are not installed; no generations were run.",
        f"Installed Ollama models: {', '.join(installed_models) if installed_models else '(none)'}",
        f"Selected models so far: {', '.join(selected) if selected else '(none)'}",
        "Missing required families:",
    ]
    for item in missing:
        lines.append(f"- {item['label']}: candidates={', '.join(item['candidates'])}")
        if item.get("install_hint"):
            lines.append(f"  suggested pull: {item['install_hint']}")
    return "\n".join(lines)


def resolve_models(args: argparse.Namespace, config: dict[str, Any], backend: str) -> tuple[list[str], list[str], str]:
    installed_models: list[str] = []
    ollama_stdout = ""
    if backend == "ollama" and not args.skip_model_check:
        installed_models, ollama_stdout, _ = load_installed_ollama_models()
    installed = set(installed_models)

    if args.models:
        models = list(dict.fromkeys(args.models))
        missing_explicit = [model for model in models if backend == "ollama" and not args.skip_model_check and model not in installed]
        if missing_explicit:
            raise RuntimeError(
                "Explicit model tag(s) are not installed in Ollama: "
                f"{', '.join(missing_explicit)}\n"
                f"Installed Ollama models: {', '.join(installed_models) if installed_models else '(none)'}"
            )
        return models, installed_models, ollama_stdout

    if backend == "ollama" and not args.skip_model_check:
        selected, missing = select_default_models(config, installed)
        if missing:
            raise RuntimeError(error_message_for_missing_models(installed_models, selected, missing))
        return selected, installed_models, ollama_stdout

    selected, missing = select_default_models(config, installed)
    if selected:
        return selected, installed_models, ollama_stdout
    configured: list[str] = []
    for family in config.get("default_model_selection", []):
        candidates = [str(item) for item in family.get("candidates", [])]
        if candidates:
            configured.append(candidates[0])
    return configured, installed_models, ollama_stdout


def select_rows(rows: list[dict[str, Any]], limit: int | None) -> list[dict[str, Any]]:
    if limit is None:
        return rows
    if limit < 0:
        raise ValueError("--limit must be non-negative")
    return rows[:limit]


def rows_by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("id", row.get("example_id", ""))): row for row in rows}


def load_existing_generation_rows(path: Path, selected_ids: set[str]) -> tuple[dict[str, dict[str, Any]], int]:
    if not path.exists():
        return {}, 0
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in read_jsonl(path):
        ex_id = str(row.get("example_id", row.get("id", "")))
        if ex_id in selected_ids:
            grouped[ex_id].append(row)
    duplicates = sum(1 for values in grouped.values() if len(values) > 1)
    return {ex_id: values[-1] for ex_id, values in grouped.items()}, duplicates


def load_reusable_predictions(config: dict[str, Any], model: str, condition: str) -> dict[str, str]:
    mapping = config.get("existing_predictions", {}).get(model, {})
    path_text = mapping.get(condition)
    if not path_text:
        return {}
    path = repo_path(path_text)
    if not path.exists():
        return {}
    out: dict[str, str] = {}
    for row in read_jsonl(path):
        if str(row.get("baseline", condition)) != condition:
            continue
        raw = row.get("prediction", row.get("raw_output", ""))
        out[str(row.get("id", row.get("example_id", "")))] = normalize_newlines(raw)
    return out


FENCE_RE = re.compile(r"```[ \t]*([A-Za-z0-9_+.#-]+)?[ \t]*\n(.*?)\n?[ \t]*```", re.DOTALL)
LABEL_RE = re.compile(
    r"^(?:here(?:'s| is)\s+(?:the\s+)?(?:revised|updated|corrected)?\s*code:?|"
    r"(?:revised|updated|corrected)\s+code:?|"
    r"the\s+(?:revised|updated|corrected)\s+code\s+is:?)\s*$",
    re.IGNORECASE,
)


def strip_gold_markers(text: str) -> str:
    text = re.sub(r"</?GOLD_LOCATION_(?:START|END)[^>]*>", "", text)
    text = re.sub(r"<GOLD_INSERTION_POINT[^>]*/>", "", text)
    return text


def extract_revised_code(raw_output: str) -> tuple[str, str]:
    """Apply one post-processing rule set uniformly across all models."""
    text = normalize_newlines(raw_output).strip()
    if not text:
        return "", "empty_raw_output"

    blocks = [block.strip("\n") for _, block in FENCE_RE.findall(text)]
    blocks = [strip_gold_markers(block).strip("\n") for block in blocks if block.strip()]
    if blocks:
        chosen = max(blocks, key=lambda item: (item.count("\n"), len(item)))
        warning = "extracted_from_code_fence"
        if len(blocks) > 1:
            warning = "multiple_code_fences_used_longest"
        return chosen, warning

    lines = text.splitlines()
    while lines and (LABEL_RE.match(lines[0].strip()) or not lines[0].strip()):
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    extracted = strip_gold_markers("\n".join(lines)).strip("\n")
    if not extracted:
        return "", "extraction_empty_after_label_cleanup"
    if extracted != text:
        return extracted, "removed_wrapper_text_or_gold_markers"
    return extracted, "no_code_fence_used_raw_text"


def exact_match_line_trim(prediction: str, target: str) -> int:
    return int(trim_line_ends(prediction) == trim_line_ends(target))


def evaluate_extraction(gold_row: dict[str, Any], extracted: str) -> tuple[int | None, float | None, str]:
    try:
        target = str(gold_row.get("new", ""))
        old = str(gold_row.get("old", ""))
        return exact_match_line_trim(extracted, target), location_f1(old, extracted, target), ""
    except Exception as exc:
        return None, None, f"{exc.__class__.__name__}: {exc}"


def build_output_record(
    *,
    gold_row: dict[str, Any],
    model: str,
    condition: str,
    raw_output: str,
    generation_source: str,
    generation_error: str = "",
) -> dict[str, Any]:
    extracted, extraction_warning = extract_revised_code(raw_output)
    extraction_failure = int(not extracted.strip())
    exact_value: int | None = None
    loc_value: float | None = None
    evaluation_error = ""

    if not generation_error and not extraction_failure:
        exact_value, loc_value, evaluation_error = evaluate_extraction(gold_row, extracted)

    evaluation_failure = int(bool(evaluation_error))
    valid_evaluation = int(not generation_error and not extraction_failure and not evaluation_failure)
    warning_parts = [part for part in [extraction_warning] if part]
    return {
        "id": gold_row["id"],
        "example_id": gold_row["id"],
        "model": model,
        "condition": condition,
        "baseline": condition,
        "language": gold_row.get("language", "unknown"),
        "old_snippet": gold_row.get("old", ""),
        "review_comment": gold_row.get("review", ""),
        "target_code": gold_row.get("new", ""),
        "raw_output": raw_output,
        "prediction": extracted,
        "extracted_code": extracted,
        "exact_match_line_trim": exact_value if exact_value is not None else "",
        "location_overlap_f1": loc_value if loc_value is not None else "",
        "generation_source": generation_source,
        "generation_error": generation_error,
        "extraction_failure": extraction_failure,
        "evaluation_failure": evaluation_failure,
        "valid_evaluation": valid_evaluation,
        "error": generation_error or evaluation_error,
        "warning": ";".join(warning_parts),
    }


def generation_path(output_root: Path, model: str, condition: str) -> Path:
    return output_root / "generations" / slugify_model(model) / f"{condition}.jsonl"


def generate_condition(
    *,
    args: argparse.Namespace,
    config: dict[str, Any],
    output_root: Path,
    gold_rows: list[dict[str, Any]],
    prompt_rows: list[dict[str, Any]],
    model: str,
    condition: str,
    backend: str,
    url: str,
    temperature: float,
    seed: int,
    num_predict: int | None,
) -> dict[str, Any]:
    if args.workers < 1:
        raise ValueError("--workers must be >= 1")

    selected_ids = {str(row["id"]) for row in gold_rows}
    gold_by_id = rows_by_id(gold_rows)
    prompt_by_id = rows_by_id(prompt_rows)
    out_path = generation_path(output_root, model, condition)
    existing_rows, duplicate_existing = load_existing_generation_rows(out_path, selected_ids) if args.resume else ({}, 0)
    reuse_legacy_predictions = bool(config.get("reuse_existing_predictions", True)) or args.reuse_legacy_predictions
    reusable = load_reusable_predictions(config, model, condition) if reuse_legacy_predictions else {}

    processed = 0
    reused_existing_output = 0
    reused_legacy_prediction = 0
    generated = 0
    errors = 0
    rows_to_process: list[dict[str, Any]] = []

    for gold_row in gold_rows:
        ex_id = str(gold_row["id"])
        if args.resume and ex_id in existing_rows:
            reused_existing_output += 1
            continue
        rows_to_process.append(gold_row)

    def process_one(gold_row: dict[str, Any]) -> dict[str, Any]:
        ex_id = str(gold_row["id"])
        prompt_row = prompt_by_id.get(ex_id)
        if prompt_row is None:
            record = build_output_record(
                gold_row=gold_row,
                model=model,
                condition=condition,
                raw_output="",
                generation_source="missing_prompt",
                generation_error=f"Missing prompt row for {ex_id} condition={condition}",
            )
            if not args.continue_on_error:
                raise RuntimeError(record["generation_error"])
            return {
                "record": record,
                "generation_source": "missing_prompt",
                "generated": 0,
                "reused_legacy": 0,
                "errors": 1,
            }

        generation_source = "backend"
        generation_error = ""
        raw_output = ""
        generated_inc = 0
        reused_legacy_inc = 0
        errors_inc = 0
        try:
            if ex_id in reusable:
                raw_output = reusable[ex_id]
                generation_source = "reused_existing_prediction"
                reused_legacy_inc = 1
            elif args.dry_run:
                raw_output = make_dry_run_prediction({"id": ex_id, "baseline": condition})
                generation_source = "dry_run"
                generated_inc = 1
            else:
                raw_output, _, _ = request_with_retry(
                    backend=backend,
                    url=url,
                    model=model,
                    messages=get_messages(prompt_row),
                    temperature=temperature,
                    seed=seed,
                    num_predict=num_predict,
                    timeout_seconds=args.timeout_seconds,
                )
                generated_inc = 1
        except Exception as exc:
            generation_error = f"{exc.__class__.__name__}: {exc}"
            errors_inc = 1
            if not args.continue_on_error:
                raise

        record = build_output_record(
            gold_row=gold_row,
            model=model,
            condition=condition,
            raw_output=raw_output,
            generation_source=generation_source,
            generation_error=generation_error,
        )
        return {
            "record": record,
            "generation_source": generation_source,
            "generated": generated_inc,
            "reused_legacy": reused_legacy_inc,
            "errors": errors_inc,
        }

    def write_result(result: dict[str, Any], processed_count: int) -> None:
        nonlocal generated, reused_legacy_prediction, errors
        record = result["record"]
        generated += int(result["generated"])
        reused_legacy_prediction += int(result["reused_legacy"])
        errors += int(result["errors"])
        append_jsonl(out_path, record)
        print(
            f"[{model} {condition}] {processed_count}/{len(rows_to_process)} "
            f"{record.get('example_id', record.get('id', ''))} source={result['generation_source']}",
            file=sys.stderr,
        )

    if args.workers == 1 or len(rows_to_process) <= 1:
        for gold_row in rows_to_process:
            processed += 1
            write_result(process_one(gold_row), processed)
    else:
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = [executor.submit(process_one, gold_row) for gold_row in rows_to_process]
            for future in as_completed(futures):
                processed += 1
                write_result(future.result(), processed)

    return {
        "model": model,
        "condition": condition,
        "path": str(out_path),
        "selected_examples": len(gold_rows),
        "existing_rows_reused": reused_existing_output,
        "legacy_predictions_reused": reused_legacy_prediction,
        "backend_generations": generated,
        "errors": errors,
        "duplicate_existing_rows": duplicate_existing,
    }


def load_all_generation_records(output_root: Path, models: list[str], conditions: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for model in models:
        for condition in conditions:
            path = generation_path(output_root, model, condition)
            if path.exists():
                rows.extend(read_jsonl(path))
    return rows


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    xs = sorted(values)
    k = (len(xs) - 1) * p / 100.0
    lo = int(k)
    hi = min(lo + 1, len(xs) - 1)
    frac = k - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def metric_value(row: dict[str, Any], metric: str) -> float | None:
    value = row.get(metric, "")
    if value == "" or value is None:
        return None
    return float(value)


def metrics_by_model_condition(
    records: list[dict[str, Any]],
    models: list[str],
    conditions: list[str],
    expected_count: int,
) -> list[dict[str, Any]]:
    by_pair: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_pair[(str(row.get("model", "")), str(row.get("condition", "")))].append(row)

    out: list[dict[str, Any]] = []
    for model in models:
        for condition in conditions:
            rows = by_pair[(model, condition)]
            valid = [row for row in rows if int(row.get("valid_evaluation", 0)) == 1]
            exact_vals = [metric_value(row, "exact_match_line_trim") for row in valid]
            loc_vals = [metric_value(row, "location_overlap_f1") for row in valid]
            exact_clean = [v for v in exact_vals if v is not None]
            loc_clean = [v for v in loc_vals if v is not None]
            out.append(
                {
                    "model": model,
                    "condition": condition,
                    "n_expected": expected_count,
                    "n_output": len(rows),
                    "n_valid": len(valid),
                    "exact_match_line_trim": mean(exact_clean),
                    "location_overlap_f1": mean(loc_clean),
                    "exact_match_line_trim_pct": 100.0 * mean(exact_clean),
                    "location_overlap_f1_pct": 100.0 * mean(loc_clean),
                }
            )
    return out


def paired_values(
    records: list[dict[str, Any]],
    model: str,
    condition_a: str,
    condition_b: str,
    metric: str,
) -> list[tuple[float, float]]:
    by_id: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for row in records:
        if str(row.get("model", "")) != model:
            continue
        if int(row.get("valid_evaluation", 0)) != 1:
            continue
        ex_id = str(row.get("example_id", row.get("id", "")))
        by_id[ex_id][str(row.get("condition", ""))] = row

    out: list[tuple[float, float]] = []
    for conditions in by_id.values():
        if condition_a not in conditions or condition_b not in conditions:
            continue
        a = metric_value(conditions[condition_a], metric)
        b = metric_value(conditions[condition_b], metric)
        if a is None or b is None:
            continue
        out.append((a, b))
    return out


def bootstrap_paired_gain(
    paired: list[tuple[float, float]],
    iters: int,
    seed: int,
) -> tuple[float, float, float, list[float]]:
    if not paired:
        return 0.0, 0.0, 0.0, []
    point = mean([b - a for a, b in paired])
    rng = random.Random(seed)
    gains: list[float] = []
    for _ in range(iters):
        sample = [paired[rng.randrange(len(paired))] for _ in paired]
        gains.append(mean([b - a for a, b in sample]))
    return point, percentile(gains, 2.5), percentile(gains, 97.5), gains


def compute_bootstrap_gains(
    records: list[dict[str, Any]],
    models: list[str],
    iters: int,
    seed: int,
) -> list[dict[str, Any]]:
    specs = [
        ("direct - no_review", "no_review", "direct", "exact_match_line_trim"),
        ("direct - no_review", "no_review", "direct", "location_overlap_f1"),
        ("gold_location - direct", "direct", "gold_location", "exact_match_line_trim"),
        ("gold_location - direct", "direct", "gold_location", "location_overlap_f1"),
    ]
    rows: list[dict[str, Any]] = []
    boot_by_spec: dict[tuple[str, str], list[list[float]]] = defaultdict(list)
    for model in models:
        for comparison, condition_a, condition_b, metric in specs:
            paired = paired_values(records, model, condition_a, condition_b, metric)
            point, ci_low, ci_high, boot = bootstrap_paired_gain(paired, iters, seed)
            rows.append(
                {
                    "model": model,
                    "comparison": comparison,
                    "metric": metric,
                    "paired_n": len(paired),
                    "gain": point,
                    "gain_pct": 100.0 * point,
                    "ci95_low": ci_low,
                    "ci95_high": ci_high,
                    "ci95_low_pct": 100.0 * ci_low,
                    "ci95_high_pct": 100.0 * ci_high,
                }
            )
            if boot:
                boot_by_spec[(comparison, metric)].append(boot)

    for comparison, _, _, metric in specs:
        boots = boot_by_spec.get((comparison, metric), [])
        model_points = [
            row["gain"]
            for row in rows
            if row["model"] != "macro_average" and row["comparison"] == comparison and row["metric"] == metric
        ]
        paired_ns = [
            int(row["paired_n"])
            for row in rows
            if row["model"] != "macro_average" and row["comparison"] == comparison and row["metric"] == metric
        ]
        macro_boot = [mean([boot[i] for boot in boots]) for i in range(iters)] if boots else []
        macro_point = mean([float(value) for value in model_points])
        rows.append(
            {
                "model": "macro_average",
                "comparison": comparison,
                "metric": metric,
                "paired_n": min(paired_ns) if paired_ns else 0,
                "gain": macro_point,
                "gain_pct": 100.0 * macro_point,
                "ci95_low": percentile(macro_boot, 2.5) if macro_boot else 0.0,
                "ci95_high": percentile(macro_boot, 97.5) if macro_boot else 0.0,
                "ci95_low_pct": 100.0 * percentile(macro_boot, 2.5) if macro_boot else 0.0,
                "ci95_high_pct": 100.0 * percentile(macro_boot, 97.5) if macro_boot else 0.0,
            }
        )
    return rows


def compute_integrity(
    records: list[dict[str, Any]],
    models: list[str],
    conditions: list[str],
    expected_ids: list[str],
) -> list[dict[str, Any]]:
    expected_set = set(expected_ids)
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        grouped[(str(row.get("model", "")), str(row.get("condition", "")))].append(row)

    out: list[dict[str, Any]] = []
    for model in models:
        for condition in conditions:
            rows = grouped[(model, condition)]
            counts = Counter(str(row.get("example_id", row.get("id", ""))) for row in rows)
            present_ids = set(counts)
            missing = expected_set - present_ids
            duplicates = [ex_id for ex_id, count in counts.items() if count > 1]
            generation_errors = sum(1 for row in rows if str(row.get("generation_error", "")).strip())
            extraction_failures = sum(1 for row in rows if int(row.get("extraction_failure", 0)) == 1)
            evaluation_failures = sum(1 for row in rows if int(row.get("evaluation_failure", 0)) == 1)
            valid = sum(1 for row in rows if int(row.get("valid_evaluation", 0)) == 1)
            out.append(
                {
                    "model": model,
                    "condition": condition,
                    "expected_count": len(expected_ids),
                    "output_count": len(rows),
                    "missing_example_id_count": len(missing),
                    "duplicate_example_id_count": len(duplicates),
                    "generation_error_count": generation_errors,
                    "extraction_failure_count": extraction_failures,
                    "evaluation_failure_count": evaluation_failures,
                    "valid_evaluation_count": valid,
                }
            )
    return out


def median(values: list[float]) -> float:
    if not values:
        return 0.0
    xs = sorted(values)
    mid = len(xs) // 2
    if len(xs) % 2:
        return xs[mid]
    return (xs[mid - 1] + xs[mid]) / 2.0


def output_length_diagnostics(
    records: list[dict[str, Any]],
    models: list[str],
    conditions: list[str],
    num_predict: int | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        grouped[(str(row.get("model", "")), str(row.get("condition", "")))].append(row)

    summary_rows: list[dict[str, Any]] = []
    case_rows: list[dict[str, Any]] = []
    near_cap_char_threshold = int(num_predict * 3.5) if num_predict else None

    for model in models:
        for condition in conditions:
            rows = grouped[(model, condition)]
            raw_lengths = [len(str(row.get("raw_output", ""))) for row in rows]
            extracted_lengths = [len(str(row.get("extracted_code", row.get("prediction", "")))) for row in rows]
            empty_raw = 0
            empty_extracted = 0
            very_short = 0
            unclosed_fence = 0
            near_cap = 0
            suspicious = 0

            for row in rows:
                raw = str(row.get("raw_output", ""))
                extracted = str(row.get("extracted_code", row.get("prediction", "")))
                flags: list[str] = []
                if not raw.strip():
                    flags.append("empty_raw_output")
                    empty_raw += 1
                if not extracted.strip():
                    flags.append("empty_extracted_code")
                    empty_extracted += 1
                elif len(extracted.strip()) < 20:
                    flags.append("very_short_extracted_code")
                    very_short += 1
                if raw.count("```") % 2 == 1:
                    flags.append("unclosed_code_fence")
                    unclosed_fence += 1
                if near_cap_char_threshold is not None and len(raw) >= near_cap_char_threshold:
                    flags.append("near_num_predict_char_risk")
                    near_cap += 1

                if flags:
                    suspicious += 1
                    case_rows.append(
                        {
                            "model": model,
                            "condition": condition,
                            "example_id": row.get("example_id", row.get("id", "")),
                            "raw_output_len_chars": len(raw),
                            "extracted_code_len_chars": len(extracted),
                            "flags": ";".join(flags),
                            "warning": row.get("warning", ""),
                            "error": row.get("error", ""),
                        }
                    )

            summary_rows.append(
                {
                    "model": model,
                    "condition": condition,
                    "n_output": len(rows),
                    "raw_len_min": min(raw_lengths) if raw_lengths else 0,
                    "raw_len_mean": mean([float(v) for v in raw_lengths]),
                    "raw_len_median": median([float(v) for v in raw_lengths]),
                    "raw_len_max": max(raw_lengths) if raw_lengths else 0,
                    "extracted_len_min": min(extracted_lengths) if extracted_lengths else 0,
                    "extracted_len_mean": mean([float(v) for v in extracted_lengths]),
                    "extracted_len_median": median([float(v) for v in extracted_lengths]),
                    "extracted_len_max": max(extracted_lengths) if extracted_lengths else 0,
                    "empty_raw_count": empty_raw,
                    "empty_extracted_count": empty_extracted,
                    "very_short_extracted_count": very_short,
                    "unclosed_code_fence_count": unclosed_fence,
                    "near_num_predict_char_risk_count": near_cap,
                    "suspicious_case_count": suspicious,
                }
            )

    return summary_rows, case_rows


def metrics_lookup(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    return {(str(row["model"]), str(row["condition"])): row for row in rows}


def gains_lookup(rows: list[dict[str, Any]]) -> dict[tuple[str, str, str], dict[str, Any]]:
    return {(str(row["model"]), str(row["comparison"]), str(row["metric"])): row for row in rows}


def paper_table_rows(models: list[str], metrics_rows: list[dict[str, Any]], gains_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    model_names = models + ["macro_average"]
    m_lookup = metrics_lookup(metrics_rows)
    g_lookup = gains_lookup(gains_rows)
    rows: list[dict[str, Any]] = []
    for model in model_names:
        if model == "macro_average":
            metrics_for_model = [row for row in metrics_rows if row["model"] in models]
            by_condition: dict[str, dict[str, float]] = {}
            for condition in FIXED_CONDITIONS:
                condition_rows = [row for row in metrics_for_model if row["condition"] == condition]
                by_condition[condition] = {
                    "exact_match_line_trim": mean([float(row["exact_match_line_trim"]) for row in condition_rows]),
                    "location_overlap_f1": mean([float(row["location_overlap_f1"]) for row in condition_rows]),
                    "n_valid": int(mean([float(row["n_valid"]) for row in condition_rows])) if condition_rows else 0,
                }
        else:
            by_condition = {
                condition: {
                    "exact_match_line_trim": float(m_lookup.get((model, condition), {}).get("exact_match_line_trim", 0.0)),
                    "location_overlap_f1": float(m_lookup.get((model, condition), {}).get("location_overlap_f1", 0.0)),
                    "n_valid": int(m_lookup.get((model, condition), {}).get("n_valid", 0)),
                }
                for condition in FIXED_CONDITIONS
            }

        def gain_value(comparison: str, metric: str) -> float:
            return float(g_lookup.get((model, comparison, metric), {}).get("gain", 0.0))

        rows.append(
            {
                "model": model,
                "no_review_exact": by_condition["no_review"]["exact_match_line_trim"],
                "direct_exact": by_condition["direct"]["exact_match_line_trim"],
                "gold_location_exact": by_condition["gold_location"]["exact_match_line_trim"],
                "no_review_loc_f1": by_condition["no_review"]["location_overlap_f1"],
                "direct_loc_f1": by_condition["direct"]["location_overlap_f1"],
                "gold_location_loc_f1": by_condition["gold_location"]["location_overlap_f1"],
                "direct_minus_no_review_exact": gain_value("direct - no_review", "exact_match_line_trim"),
                "direct_minus_no_review_loc_f1": gain_value("direct - no_review", "location_overlap_f1"),
                "gold_location_minus_direct_exact": gain_value("gold_location - direct", "exact_match_line_trim"),
                "gold_location_minus_direct_loc_f1": gain_value("gold_location - direct", "location_overlap_f1"),
            }
        )
    return rows


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


def write_summary_md(
    *,
    output_root: Path,
    config: dict[str, Any],
    args: argparse.Namespace,
    models: list[str],
    installed_models: list[str],
    generation_runs: list[dict[str, Any]],
    metrics_rows: list[dict[str, Any]],
    gains_rows: list[dict[str, Any]],
    integrity_rows: list[dict[str, Any]],
    length_rows: list[dict[str, Any]],
    truncation_case_rows: list[dict[str, Any]],
    paper_rows: list[dict[str, Any]],
    started_at: str,
    completed_at: str,
) -> None:
    limit_text = str(args.limit) if args.limit is not None else str(config.get("subset_size", 100))
    num_predict_arg = f" --num-predict {args.num_predict}" if args.num_predict is not None else ""
    workers_arg = f" --workers {args.workers}" if args.workers != 1 else ""
    smoke_cmd = (
        "python scripts/run_multi_model_r2r.py --limit 10 "
        f"--output-root results/multi_model_r2r_seed42_smoke10 --resume --continue-on-error{num_predict_arg}{workers_arg}"
    )
    full_cmd = (
        "python scripts/run_multi_model_r2r.py --output-root results/multi_model_r2r_seed42 "
        f"--resume --continue-on-error{num_predict_arg}{workers_arg}"
    )

    lines = [
        "# Multi-Model Review-to-Repair Seed42",
        "",
        "## Run",
        f"- Started UTC: {started_at}",
        f"- Completed UTC: {completed_at}",
        f"- Data: {config.get('gold_path')} ({limit_text} examples from the seed=42 CodeReview-New pilot subset)",
        "- Conditions: no_review, direct, gold_location",
        "- Metrics: exact_match_line_trim, location_overlap_f1",
        f"- Models: {', '.join(models)}",
        f"- Installed Ollama models observed: {', '.join(installed_models) if installed_models else '(not checked)'}",
        f"- Output root: {output_root}",
        f"- Workers per model/condition: {args.workers}",
        f"- Legacy prediction reuse: {'enabled' if (bool(config.get('reuse_existing_predictions', True)) or args.reuse_legacy_predictions) else 'disabled'}",
    ]
    excluded_models = config.get("excluded_models", {})
    if excluded_models:
        lines.extend(["", "## Excluded Models"])
        for model, reason in sorted(excluded_models.items()):
            lines.append(f"- {model}: {reason}")
        lines.append("- Excluded models are not included in paper-ready metrics or macro averages.")
    fallback_families = config.get("fallback_candidates_not_for_main_full_run", [])
    if fallback_families:
        lines.extend(["", "## Fallback Candidates"])
        for family in fallback_families:
            candidates = ", ".join(str(item) for item in family.get("candidates", []))
            note = str(family.get("note", "")).strip()
            lines.append(f"- {family.get('label', 'fallback')}: {candidates}. {note}")
    lines.extend(
        [
        "",
        "## Post-Processing Rule",
        "- The same extraction rule is applied to every model and condition.",
        "- If one or more fenced Markdown code blocks are present, the longest non-empty block is used as the revised snippet.",
        "- If no code fence is present, leading wrapper labels such as revised-code introductions are removed and the remaining raw text is evaluated.",
        "- Gold-location marker tags are stripped if a model echoes them.",
        "",
        "## Execution Commands",
        f"- Smoke test: `{smoke_cmd}`",
        f"- Full run after approval: `{full_cmd}`",
        "",
        "## Generation Accounting",
        ]
    )
    lines.extend(
        markdown_table(
            generation_runs,
            [
                "model",
                "condition",
                "selected_examples",
                "existing_rows_reused",
                "legacy_predictions_reused",
                "backend_generations",
                "errors",
            ],
        )
    )
    lines.extend(["", "## Metrics By Model And Condition"])
    lines.extend(
        markdown_table(
            metrics_rows,
            ["model", "condition", "n_valid", "exact_match_line_trim", "location_overlap_f1"],
        )
    )
    lines.extend(["", "## Gains With Paired Bootstrap 95% CI"])
    lines.extend(
        markdown_table(
            gains_rows,
            ["model", "comparison", "metric", "paired_n", "gain", "ci95_low", "ci95_high"],
        )
    )
    lines.extend(["", "## Paper-Ready Summary Table"])
    lines.extend(
        markdown_table(
            paper_rows,
            [
                "model",
                "no_review_exact",
                "direct_exact",
                "gold_location_exact",
                "no_review_loc_f1",
                "direct_loc_f1",
                "gold_location_loc_f1",
                "direct_minus_no_review_exact",
                "direct_minus_no_review_loc_f1",
                "gold_location_minus_direct_exact",
                "gold_location_minus_direct_loc_f1",
            ],
        )
    )
    lines.extend(["", "## Integrity"])
    lines.extend(
        markdown_table(
            integrity_rows,
            [
                "model",
                "condition",
                "expected_count",
                "output_count",
                "missing_example_id_count",
                "duplicate_example_id_count",
                "generation_error_count",
                "extraction_failure_count",
                "evaluation_failure_count",
                "valid_evaluation_count",
            ],
        )
    )
    lines.extend(["", "## Output Length And Truncation Diagnostics"])
    lines.extend(
        markdown_table(
            length_rows,
            [
                "model",
                "condition",
                "n_output",
                "raw_len_min",
                "raw_len_mean",
                "raw_len_median",
                "raw_len_max",
                "extracted_len_min",
                "extracted_len_mean",
                "extracted_len_median",
                "extracted_len_max",
                "empty_raw_count",
                "empty_extracted_count",
                "very_short_extracted_count",
                "unclosed_code_fence_count",
                "near_num_predict_char_risk_count",
                "suspicious_case_count",
            ],
        )
    )
    if truncation_case_rows:
        lines.extend(
            [
                "",
                "## Truncation Or Empty-Output Flags",
                "- The cases below are heuristic flags based on empty outputs, empty or very short extracted code, unclosed Markdown fences, or raw outputs whose character length is near the generation cap.",
            ]
        )
        lines.extend(
            markdown_table(
                truncation_case_rows[:25],
                ["model", "condition", "example_id", "raw_output_len_chars", "extracted_code_len_chars", "flags"],
            )
        )
        if len(truncation_case_rows) > 25:
            lines.append(f"- Additional flagged cases omitted from this Markdown view: {len(truncation_case_rows) - 25}")
    else:
        lines.extend(["", "## Truncation Or Empty-Output Flags", "- No heuristic truncation or empty-output flags were found."])
    lines.extend(
        [
            "",
            "## Research Message",
            "Review comments and gold location information can change model repair behavior, but improvements in location overlap do not necessarily convert into exact repair success. The tables above therefore keep model-specific condition comparisons and gain estimates together.",
            "",
        ]
    )
    (output_root / "summary.md").write_text("\n".join(lines), encoding="utf-8")


def write_blocked_summary(
    output_root: Path,
    config: dict[str, Any],
    installed_models: list[str],
    error_text: str,
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "plots").mkdir(parents=True, exist_ok=True)
    lines = [
        "# Multi-Model Review-to-Repair Seed42",
        "",
        "## Model Check Blocked The Run",
        error_text,
        "",
        "No generation was started. Install one model from each missing family, then rerun:",
        "",
        "```bash",
        "python scripts/run_multi_model_r2r.py --limit 10 --output-root results/multi_model_r2r_seed42_smoke10 --resume --continue-on-error --num-predict 1024",
        "```",
        "",
        "Installed Ollama models observed:",
    ]
    lines.extend([f"- {model}" for model in installed_models] or ["- (none)"])
    lines.extend(["", "Configured candidate families:"])
    for family in config.get("default_model_selection", []):
        lines.append(f"- {family.get('label')}: {', '.join(family.get('candidates', []))}")
        if family.get("install_hint"):
            lines.append(f"  - suggested pull: `{family['install_hint']}`")
    excluded_models = config.get("excluded_models", {})
    if excluded_models:
        lines.extend(["", "Excluded models:"])
        for model, reason in sorted(excluded_models.items()):
            lines.append(f"- {model}: {reason}")
    fallback_families = config.get("fallback_candidates_not_for_main_full_run", [])
    if fallback_families:
        lines.extend(["", "Fallback candidates not for main full run:"])
        for family in fallback_families:
            candidates = ", ".join(str(item) for item in family.get("candidates", []))
            note = str(family.get("note", "")).strip()
            lines.append(f"- {family.get('label', 'fallback')}: {candidates}. {note}")
    (output_root / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    config_path = repo_path(args.config)
    config = read_json(config_path)
    conditions = validate_conditions(config)
    backend = args.backend or str(config.get("backend", "ollama"))
    temperature = args.temperature if args.temperature is not None else float(config.get("temperature", 0.0))
    seed = args.seed if args.seed is not None else int(config.get("seed", 42))
    num_predict = args.num_predict if args.num_predict is not None else config.get("num_predict")
    if num_predict is not None:
        num_predict = int(num_predict)
    bootstrap_iters = args.bootstrap_iters if args.bootstrap_iters is not None else int(config.get("bootstrap_iters", 1000))
    output_root = repo_path(args.output_root or Path("results") / str(config.get("run_name", "multi_model_r2r_seed42")))
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "plots").mkdir(parents=True, exist_ok=True)

    try:
        models, installed_models, ollama_stdout = resolve_models(args, config, backend)
    except RuntimeError as exc:
        installed_models: list[str] = []
        if backend == "ollama":
            try:
                installed_models, _, _ = load_installed_ollama_models()
            except RuntimeError:
                installed_models = []
        write_blocked_summary(output_root, config, installed_models, str(exc))
        print(str(exc), file=sys.stderr)
        sys.exit(2)

    if args.check_models:
        print(
            json.dumps(
                {
                    "models": models,
                    "installed_ollama_models": installed_models,
                    "ollama_list": ollama_stdout,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    gold_path = repo_path(config.get("gold_path", "data/processed/crn_pilot100.jsonl"))
    prompt_dir = repo_path(config.get("prompt_dir", "prompts/crn_pilot100"))
    gold_rows = select_rows(read_jsonl(gold_path), args.limit)
    expected_ids = [str(row["id"]) for row in gold_rows]
    url = backend_url(backend, args.base_url)
    started_at = now_utc_iso()
    run_metadata = {
        "started_at": started_at,
        "config": str(config_path),
        "output_root": str(output_root),
        "gold_path": str(gold_path),
        "prompt_dir": str(prompt_dir),
        "models": models,
        "conditions": conditions,
        "limit": args.limit,
        "backend": backend,
        "base_url": url,
        "temperature": temperature,
        "seed": seed,
        "num_predict": num_predict,
        "bootstrap_iters": bootstrap_iters,
        "workers": args.workers,
        "dry_run": args.dry_run,
        "resume": args.resume,
        "reuse_legacy_predictions": bool(config.get("reuse_existing_predictions", True)) or args.reuse_legacy_predictions,
    }
    write_json(output_root / "run_metadata.json", run_metadata)

    generation_runs: list[dict[str, Any]] = []
    for model in models:
        for condition in conditions:
            prompt_path = prompt_dir / f"{condition}_prompts.jsonl"
            prompt_rows = select_rows(read_jsonl(prompt_path), args.limit)
            generation_runs.append(
                generate_condition(
                    args=args,
                    config=config,
                    output_root=output_root,
                    gold_rows=gold_rows,
                    prompt_rows=prompt_rows,
                    model=model,
                    condition=condition,
                    backend=backend,
                    url=url,
                    temperature=temperature,
                    seed=seed,
                    num_predict=num_predict,
                )
            )

    records = load_all_generation_records(output_root, models, conditions)
    # Keep aggregate files limited to the selected example IDs for smoke/full reproducibility.
    selected_id_set = set(expected_ids)
    records = [row for row in records if str(row.get("example_id", row.get("id", ""))) in selected_id_set]
    combined_path = output_root / "generations" / "all_generations.jsonl"
    write_jsonl(combined_path, records)

    metrics_rows = metrics_by_model_condition(records, models, conditions, len(expected_ids))
    gains_rows = compute_bootstrap_gains(records, models, bootstrap_iters, seed)
    integrity_rows = compute_integrity(records, models, conditions, expected_ids)
    length_rows, truncation_case_rows = output_length_diagnostics(records, models, conditions, num_predict)
    paper_rows = paper_table_rows(models, metrics_rows, gains_rows)

    write_csv(output_root / "metrics_by_model_condition.csv", metrics_rows)
    write_csv(output_root / "bootstrap_gains_by_model.csv", gains_rows)
    write_csv(output_root / "integrity_report.csv", integrity_rows)
    write_csv(output_root / "output_length_diagnostics.csv", length_rows)
    write_csv(
        output_root / "truncation_risk_cases.csv",
        truncation_case_rows,
        [
            "model",
            "condition",
            "example_id",
            "raw_output_len_chars",
            "extracted_code_len_chars",
            "flags",
            "warning",
            "error",
        ],
    )
    write_csv(output_root / "paper_results_table.csv", paper_rows)

    completed_at = now_utc_iso()
    run_metadata["completed_at"] = completed_at
    run_metadata["generation_runs"] = generation_runs
    run_metadata["combined_generations"] = str(combined_path)
    write_json(output_root / "run_metadata.json", run_metadata)
    write_summary_md(
        output_root=output_root,
        config=config,
        args=args,
        models=models,
        installed_models=installed_models,
        generation_runs=generation_runs,
        metrics_rows=metrics_rows,
        gains_rows=gains_rows,
        integrity_rows=integrity_rows,
        length_rows=length_rows,
        truncation_case_rows=truncation_case_rows,
        paper_rows=paper_rows,
        started_at=started_at,
        completed_at=completed_at,
    )

    print(
        json.dumps(
            {
                "output_root": str(output_root),
                "models": models,
                "conditions": conditions,
                "examples": len(expected_ids),
                "expected_outputs": len(models) * len(conditions) * len(expected_ids),
                "combined_generations": str(combined_path),
                "summary": str(output_root / "summary.md"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
