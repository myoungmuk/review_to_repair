#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames or [])
    return rows, fieldnames


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Original error-analysis sample CSV")
    ap.add_argument("--labels", required=True, help="CSV with id, manual_label, notes")
    ap.add_argument("--output", required=True, help="Output labeled CSV")
    args = ap.parse_args()

    input_path = Path(args.input)
    labels_path = Path(args.labels)
    output_path = Path(args.output)

    rows, fieldnames = read_csv(input_path)
    label_rows, _ = read_csv(labels_path)
    labels_by_id = {row["id"]: row for row in label_rows}

    if "manual_label" not in fieldnames:
        fieldnames.append("manual_label")
    if "notes" not in fieldnames:
        fieldnames.append("notes")

    updated = 0
    missing = []
    for row in rows:
        label_row = labels_by_id.get(row.get("id", ""))
        if not label_row:
            missing.append(row.get("id", ""))
            continue
        row["manual_label"] = label_row.get("manual_label", "")
        row["notes"] = label_row.get("notes", "")
        updated += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"input={input_path}")
    print(f"labels={labels_path}")
    print(f"output={output_path}")
    print(f"updated={updated}")
    if missing:
        print(f"missing_labels={len(missing)}")


if __name__ == "__main__":
    main()
