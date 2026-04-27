#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def sanitize_name(s: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", s.strip())
    return cleaned.strip("._-") or "local_run"


def count_lines(path: Path) -> int:
    if not path.exists():
        return 0
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)


def run_cmd(args: list[str], log_path: Path | None = None) -> str:
    text = " ".join(args)
    print(f"$ {text}", flush=True)
    proc = subprocess.run(args, cwd=REPO_ROOT, text=True, capture_output=True)
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"$ {text}\n")
            if proc.stdout:
                f.write(proc.stdout)
                if not proc.stdout.endswith("\n"):
                    f.write("\n")
            if proc.stderr:
                f.write(proc.stderr)
                if not proc.stderr.endswith("\n"):
                    f.write("\n")
    if proc.returncode != 0:
        raise RuntimeError(f"Command failed with exit code {proc.returncode}: {text}\n{proc.stderr}")
    return proc.stdout


def merge_jsonl(paths: list[Path], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as out:
        for path in paths:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    out.write(line)


def write_gain_summary(report_dir: Path, sections: list[tuple[str, str]]) -> None:
    lines = ["# Gain Summary", ""]
    for title, body in sections:
        lines.append(f"## {title}")
        lines.append("")
        lines.append("```text")
        lines.append(body.strip())
        lines.append("```")
        lines.append("")
    lines.append("Interpretation should be cautious and snippet-level only.")
    lines.append("Use 'suggests' or 'is consistent with' rather than strong causal claims.")
    with open(report_dir / "gain_summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--backend", choices=["ollama", "chat_completions"], default="ollama")
    ap.add_argument("--base-url", default=None)
    ap.add_argument("--prefix", default=None, help="Run name prefix for predictions/reports")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--timeout-seconds", type=float, default=300.0)
    ap.add_argument("--subset", default="crn_pilot100")
    ap.add_argument("--max-per-group", type=int, default=10)
    args = ap.parse_args()

    run_name = args.prefix or sanitize_name(f"{args.subset}_{args.model}")
    prompts_dir = REPO_ROOT / "prompts" / args.subset
    gold_path = REPO_ROOT / "data" / "processed" / f"{args.subset}.jsonl"
    report_dir = REPO_ROOT / "reports" / run_name
    prediction_dir = REPO_ROOT / "predictions"
    log_path = report_dir / "pipeline.log"

    baselines = ["no_review", "direct", "gold_location"]
    prediction_paths: list[Path] = []

    for baseline in baselines:
        prompt_path = prompts_dir / f"{baseline}_prompts.jsonl"
        pred_path = prediction_dir / f"{run_name}_{baseline}.jsonl"
        err_path = report_dir / f"{baseline}_errors.jsonl"
        prediction_paths.append(pred_path)
        cmd = [
            sys.executable,
            "scripts/run_local_predictions.py",
            "--input",
            str(prompt_path),
            "--output",
            str(pred_path),
            "--model",
            args.model,
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
            str(err_path),
        ]
        if args.base_url:
            cmd.extend(["--base-url", args.base_url])
        run_cmd(cmd, log_path=log_path)
        print(f"{baseline}: {count_lines(pred_path)} predictions", flush=True)

    merged_path = prediction_dir / f"{run_name}.jsonl"
    merge_jsonl(prediction_paths, merged_path)
    print(f"merged predictions: {count_lines(merged_path)} lines", flush=True)

    run_cmd(
        [
            sys.executable,
            "scripts/evaluate_predictions.py",
            "--gold",
            str(gold_path),
            "--pred",
            str(merged_path),
            "--outdir",
            str(report_dir),
        ],
        log_path=log_path,
    )

    gain_sections: list[tuple[str, str]] = []
    gain_specs = [
        ("direct - no_review exact_match_line_trim", "no_review", "direct", "exact_match_line_trim"),
        ("gold_location - direct exact_match_line_trim", "direct", "gold_location", "exact_match_line_trim"),
        ("direct - no_review location_overlap_f1", "no_review", "direct", "location_overlap_f1"),
        ("gold_location - direct location_overlap_f1", "direct", "gold_location", "location_overlap_f1"),
    ]
    for title, baseline_a, baseline_b, metric in gain_specs:
        out = run_cmd(
            [
                sys.executable,
                "scripts/bootstrap_gain.py",
                "--per-example",
                str(report_dir / "per_example_metrics.csv"),
                "--baseline-a",
                baseline_a,
                "--baseline-b",
                baseline_b,
                "--metric",
                metric,
                "--iters",
                "1000",
                "--seed",
                str(args.seed),
            ],
            log_path=log_path,
        )
        gain_sections.append((title, out))
    write_gain_summary(report_dir, gain_sections)

    run_cmd(
        [
            sys.executable,
            "scripts/make_error_analysis_sample.py",
            "--per-example",
            str(report_dir / "per_example_metrics.csv"),
            "--gold",
            str(gold_path),
            "--pred",
            str(merged_path),
            "--output",
            str(report_dir / "error_analysis_sample.csv"),
            "--max-per-group",
            str(args.max_per_group),
            "--seed",
            str(args.seed),
        ],
        log_path=log_path,
    )

    summary = {
        "run_name": run_name,
        "model": args.model,
        "backend": args.backend,
        "merged_predictions": str(merged_path),
        "report_dir": str(report_dir),
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
