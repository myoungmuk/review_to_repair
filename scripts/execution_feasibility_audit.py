#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import random
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen


USER_AGENT = "review-to-repair-feasibility-audit"


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def fetch_text(url: str, timeout: float) -> tuple[int | None, str, str]:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return int(resp.status), body, ""
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return int(exc.code), body, f"HTTPError: {exc.code}"
    except URLError as exc:
        return None, "", f"URLError: {exc.reason}"
    except TimeoutError as exc:
        return None, "", f"TimeoutError: {exc}"


def fetch_json(url: str, timeout: float) -> tuple[int | None, dict[str, Any] | None, str]:
    status, body, err = fetch_text(url, timeout)
    if err or status is None or status >= 400:
        return status, None, err or f"HTTP status {status}"
    try:
        return status, json.loads(body), ""
    except json.JSONDecodeError as exc:
        return status, None, f"JSONDecodeError: {exc}"


def normalize(s: Any) -> str:
    return str(s or "").replace("\r\n", "\n").replace("\r", "\n")


def trim_line_ends(s: str) -> str:
    return "\n".join(line.rstrip() for line in normalize(s).strip().split("\n"))


def diff_marked_to_code(text: str, side: str) -> str:
    lines: list[str] = []
    for line in normalize(text).splitlines():
        if line.startswith("@@"):
            continue
        if not line:
            lines.append(line)
            continue
        marker = line[0]
        body = line[1:] if marker in {" ", "+", "-"} else line
        if side == "old" and marker == "+":
            continue
        if side == "new" and marker == "-":
            continue
        lines.append(body)
    return "\n".join(lines)


def count_matches(haystack: str, needle: str) -> int:
    if not needle:
        return 0
    return normalize(haystack).count(normalize(needle))


def count_trimmed_matches(haystack: str, needle: str) -> int:
    if not needle:
        return 0
    return trim_line_ends(haystack).count(trim_line_ends(needle))


def sha_from_commit_url(url: str) -> str:
    parsed = urlparse(url)
    parts = [p for p in parsed.path.split("/") if p]
    if "commits" not in parts:
        return ""
    idx = parts.index("commits")
    if idx + 1 >= len(parts):
        return ""
    return parts[idx + 1]


def raw_file_url(repo: str, ref: str, path: str) -> str:
    return f"https://raw.githubusercontent.com/{repo}/{ref}/{quote(path, safe='/')}"


def language_test_hint(language: str) -> str:
    lang = language.lower()
    hints = {
        "python": "pytest or project-specific test command",
        "go": "go test ./...",
        "java": "mvn test or ./gradlew test",
        "kotlin": "./gradlew test",
        "scala": "sbt test",
        "javascript": "npm test",
        "typescript": "npm test",
        "ruby": "bundle exec rake test or bundle exec rspec",
        "php": "composer test or vendor/bin/phpunit",
        "r": "R CMD check or devtools::test()",
        "cpp": "cmake/ctest project-specific command",
        "c": "make test or ctest",
        "csharp": "dotnet test",
        "swift": "swift test or xcodebuild test",
    }
    return hints.get(lang, "")


def choose_sample(rows: list[dict[str, Any]], n: int, seed: int) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    rows = list(rows)
    rng.shuffle(rows)
    return rows[: min(n, len(rows))]


def audit_one(
    processed: dict[str, Any],
    raw_rows: list[dict[str, Any]],
    timeout: float,
    sleep_seconds: float,
) -> dict[str, Any]:
    source_index = int(processed.get("source_index", -1))
    raw = raw_rows[source_index] if 0 <= source_index < len(raw_rows) else {}
    repo = str(raw.get("repo", ""))
    review_url = str(raw.get("review_url", ""))
    commit_url = str(raw.get("commit_url", processed.get("commit_url", "")))
    commit_sha = sha_from_commit_url(commit_url)

    out: dict[str, Any] = {
        "id": processed.get("id", ""),
        "source_index": source_index,
        "language": processed.get("language", ""),
        "repo": repo,
        "review_url": review_url,
        "commit_url": commit_url,
        "metadata_present": bool(repo and review_url and commit_url),
        "review_status": "",
        "review_error": "",
        "review_path": "",
        "review_original_commit_id": "",
        "review_commit_id": "",
        "final_commit_sha": commit_sha,
        "path_available": False,
        "raw_fetch_refs_tried": 0,
        "raw_fetch_success_refs": 0,
        "old_exact_match_any_ref": False,
        "old_exact_unique_any_ref": False,
        "old_trimmed_match_any_ref": False,
        "old_best_exact_count": 0,
        "old_best_trimmed_count": 0,
        "old_best_ref": "",
        "old_plain_exact_match_any_ref": False,
        "old_plain_exact_unique_any_ref": False,
        "old_plain_trimmed_match_any_ref": False,
        "old_plain_best_exact_count": 0,
        "old_plain_best_trimmed_count": 0,
        "old_plain_best_ref": "",
        "new_exact_match_any_ref": False,
        "new_trimmed_match_any_ref": False,
        "new_best_exact_count": 0,
        "new_best_trimmed_count": 0,
        "new_best_ref": "",
        "new_plain_exact_match_any_ref": False,
        "new_plain_trimmed_match_any_ref": False,
        "new_plain_best_exact_count": 0,
        "new_plain_best_trimmed_count": 0,
        "new_plain_best_ref": "",
        "prediction_patch_feasible_by_exact_old": False,
        "prediction_patch_feasible_by_plain_old": False,
        "test_command_hint": language_test_hint(str(processed.get("language", ""))),
    }

    if not out["metadata_present"]:
        return out

    status, comment, err = fetch_json(review_url, timeout=timeout)
    out["review_status"] = status if status is not None else ""
    out["review_error"] = err
    if not comment:
        return out

    path = str(comment.get("path", ""))
    original_commit_id = str(comment.get("original_commit_id", ""))
    review_commit_id = str(comment.get("commit_id", ""))
    out["review_path"] = path
    out["review_original_commit_id"] = original_commit_id
    out["review_commit_id"] = review_commit_id
    out["path_available"] = bool(path)
    if not path:
        return out

    refs = []
    for ref in [original_commit_id, review_commit_id, commit_sha]:
        if ref and ref not in refs:
            refs.append(ref)

    old = normalize(processed.get("old", ""))
    new = normalize(processed.get("new", ""))
    old_plain = diff_marked_to_code(old, "old")
    new_plain = diff_marked_to_code(new, "new")
    best_old = ("", 0, 0)
    best_new = ("", 0, 0)
    best_old_plain = ("", 0, 0)
    best_new_plain = ("", 0, 0)
    for ref in refs:
        out["raw_fetch_refs_tried"] += 1
        raw_url = raw_file_url(repo, ref, path)
        status, body, err = fetch_text(raw_url, timeout=timeout)
        if sleep_seconds:
            time.sleep(sleep_seconds)
        if status is None or status >= 400 or err:
            continue
        out["raw_fetch_success_refs"] += 1
        old_exact = count_matches(body, old)
        old_trimmed = count_trimmed_matches(body, old)
        new_exact = count_matches(body, new)
        new_trimmed = count_trimmed_matches(body, new)
        old_plain_exact = count_matches(body, old_plain)
        old_plain_trimmed = count_trimmed_matches(body, old_plain)
        new_plain_exact = count_matches(body, new_plain)
        new_plain_trimmed = count_trimmed_matches(body, new_plain)
        if old_exact > best_old[1] or old_trimmed > best_old[2]:
            best_old = (ref, old_exact, old_trimmed)
        if new_exact > best_new[1] or new_trimmed > best_new[2]:
            best_new = (ref, new_exact, new_trimmed)
        if old_plain_exact > best_old_plain[1] or old_plain_trimmed > best_old_plain[2]:
            best_old_plain = (ref, old_plain_exact, old_plain_trimmed)
        if new_plain_exact > best_new_plain[1] or new_plain_trimmed > best_new_plain[2]:
            best_new_plain = (ref, new_plain_exact, new_plain_trimmed)

    out["old_best_ref"], out["old_best_exact_count"], out["old_best_trimmed_count"] = best_old
    out["new_best_ref"], out["new_best_exact_count"], out["new_best_trimmed_count"] = best_new
    out["old_plain_best_ref"], out["old_plain_best_exact_count"], out["old_plain_best_trimmed_count"] = best_old_plain
    out["new_plain_best_ref"], out["new_plain_best_exact_count"], out["new_plain_best_trimmed_count"] = best_new_plain
    out["old_exact_match_any_ref"] = out["old_best_exact_count"] > 0
    out["old_exact_unique_any_ref"] = out["old_best_exact_count"] == 1
    out["old_trimmed_match_any_ref"] = out["old_best_trimmed_count"] > 0
    out["new_exact_match_any_ref"] = out["new_best_exact_count"] > 0
    out["new_trimmed_match_any_ref"] = out["new_best_trimmed_count"] > 0
    out["old_plain_exact_match_any_ref"] = out["old_plain_best_exact_count"] > 0
    out["old_plain_exact_unique_any_ref"] = out["old_plain_best_exact_count"] == 1
    out["old_plain_trimmed_match_any_ref"] = out["old_plain_best_trimmed_count"] > 0
    out["new_plain_exact_match_any_ref"] = out["new_plain_best_exact_count"] > 0
    out["new_plain_trimmed_match_any_ref"] = out["new_plain_best_trimmed_count"] > 0
    out["prediction_patch_feasible_by_exact_old"] = out["old_exact_unique_any_ref"]
    out["prediction_patch_feasible_by_plain_old"] = out["old_plain_exact_unique_any_ref"]
    return out


def summarize(records: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    bool_fields = [
        "metadata_present",
        "path_available",
        "old_exact_match_any_ref",
        "old_exact_unique_any_ref",
        "old_trimmed_match_any_ref",
        "old_plain_exact_match_any_ref",
        "old_plain_exact_unique_any_ref",
        "old_plain_trimmed_match_any_ref",
        "new_exact_match_any_ref",
        "new_trimmed_match_any_ref",
        "new_plain_exact_match_any_ref",
        "new_plain_trimmed_match_any_ref",
        "prediction_patch_feasible_by_exact_old",
        "prediction_patch_feasible_by_plain_old",
    ]
    total = len(records)
    summary: dict[str, Any] = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "sample_size": total,
        "seed": args.seed,
        "processed_path": str(args.processed),
        "raw_path": str(args.raw),
        "counts": {field: sum(1 for row in records if row.get(field)) for field in bool_fields},
        "review_status_counts": dict(Counter(str(row.get("review_status", "")) for row in records)),
        "raw_fetch_success_distribution": dict(Counter(int(row.get("raw_fetch_success_refs", 0)) for row in records)),
        "language_counts": dict(Counter(str(row.get("language", "")) for row in records)),
        "by_language": {},
    }
    by_lang: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        by_lang[str(row.get("language", ""))].append(row)
    for lang, rows in sorted(by_lang.items()):
        summary["by_language"][lang] = {
            "n": len(rows),
            "path_available": sum(1 for row in rows if row.get("path_available")),
            "old_exact_unique": sum(1 for row in rows if row.get("old_exact_unique_any_ref")),
            "plain_old_exact_unique": sum(1 for row in rows if row.get("old_plain_exact_unique_any_ref")),
            "prediction_patch_feasible": sum(1 for row in rows if row.get("prediction_patch_feasible_by_plain_old")),
        }
    return summary


def percent(n: int, d: int) -> str:
    return "0.0%" if d == 0 else f"{(100.0 * n / d):.1f}%"


def write_markdown(path: Path, summary: dict[str, Any], records_path: Path, summary_path: Path) -> None:
    total = int(summary["sample_size"])
    counts = summary["counts"]
    lines = [
        "# Execution Feasibility Audit",
        "",
        f"- Created UTC: {summary['created_utc']}",
        f"- Sample size: {total}",
        f"- Seed: {summary['seed']}",
        f"- Processed data: `{summary['processed_path']}`",
        f"- Raw data: `{summary['raw_path']}`",
        f"- Record CSV: `{records_path}`",
        f"- Summary JSON: `{summary_path}`",
        "",
        "## Main Counts",
        "",
        "| check | count | rate |",
        "| --- | ---: | ---: |",
    ]
    labels = [
        ("metadata_present", "Repo/review/commit metadata present"),
        ("path_available", "Review file path available from GitHub comment"),
        ("old_exact_match_any_ref", "Old snippet exact-matches at least one candidate file"),
        ("old_exact_unique_any_ref", "Old snippet exact-matches uniquely"),
        ("old_trimmed_match_any_ref", "Old snippet matches after trimming line ends"),
        ("old_plain_exact_match_any_ref", "Diff-marker-stripped old code exact-matches at least one candidate file"),
        ("old_plain_exact_unique_any_ref", "Diff-marker-stripped old code exact-matches uniquely"),
        ("old_plain_trimmed_match_any_ref", "Diff-marker-stripped old code matches after trimming line ends"),
        ("new_exact_match_any_ref", "Gold new snippet exact-matches at least one candidate file"),
        ("new_plain_exact_match_any_ref", "Diff-marker-stripped gold new code exact-matches at least one candidate file"),
        ("prediction_patch_feasible_by_plain_old", "Prediction can be patched by unique exact stripped old-code match"),
    ]
    for field, label in labels:
        value = int(counts.get(field, 0))
        lines.append(f"| {label} | {value} | {percent(value, total)} |")

    lines.extend([
        "",
        "## Review API Status",
        "",
        "| status | count |",
        "| --- | ---: |",
    ])
    for status, count in sorted(summary["review_status_counts"].items()):
        lines.append(f"| {status or 'missing'} | {count} |")

    lines.extend([
        "",
        "## Language Breakdown",
        "",
        "| language | n | path available | unique old match | unique stripped old match | patch feasible |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for lang, row in summary["by_language"].items():
        lines.append(
            f"| {lang} | {row['n']} | {row['path_available']} | "
            f"{row['old_exact_unique']} | {row['plain_old_exact_unique']} | "
            f"{row['prediction_patch_feasible']} |"
        )

    lines.extend([
        "",
        "## Interpretation",
        "",
        "This audit checks whether execution-based evaluation can be reconstructed from CodeReview-New metadata.",
        "It does not run project tests. A case is counted as patch-feasible only when the diff-marker-stripped old code has a unique exact match in a candidate GitHub file.",
        "Full execution evaluation would still require repository checkout, dependency installation, project-specific test command discovery, and gold-patch sanity checks.",
        "",
    ])
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed", type=Path, default=Path("data/processed/crn_all.jsonl"))
    ap.add_argument("--raw", type=Path, default=Path("data_raw/data_new/codereview_new.jsonl"))
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--timeout-seconds", type=float, default=15.0)
    ap.add_argument("--sleep-seconds", type=float, default=0.1)
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    processed_rows = read_jsonl(args.processed)
    raw_rows = read_jsonl(args.raw)
    sample = choose_sample(processed_rows, n=args.n, seed=args.seed)
    records: list[dict[str, Any]] = []
    for i, row in enumerate(sample, 1):
        record = audit_one(row, raw_rows, timeout=args.timeout_seconds, sleep_seconds=args.sleep_seconds)
        records.append(record)
        print(
            f"[{i}/{len(sample)}] {record['id']} {record['language']} "
            f"path={int(bool(record['path_available']))} "
            f"stripped_old_unique={int(bool(record['old_plain_exact_unique_any_ref']))} "
            f"raw_ok={record['raw_fetch_success_refs']}",
            flush=True,
        )
        if args.sleep_seconds:
            time.sleep(args.sleep_seconds)

    args.output_root.mkdir(parents=True, exist_ok=True)
    records_path = args.output_root / "records.csv"
    summary_path = args.output_root / "summary.json"
    markdown_path = args.output_root / "summary.md"
    write_csv(records_path, records)
    summary = summarize(records, args)
    write_json(summary_path, summary)
    write_markdown(markdown_path, summary, records_path, summary_path)
    print(f"records={records_path}")
    print(f"summary={summary_path}")
    print(f"markdown={markdown_path}")


if __name__ == "__main__":
    main()
