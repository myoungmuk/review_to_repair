from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip("\n")
            if not line.strip():
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return out


def write_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def find_codereview_new(input_path: str | Path) -> Path:
    p = Path(input_path)
    if p.is_file():
        return p
    matches = list(p.rglob("codereview_new.jsonl"))
    if not matches:
        raise FileNotFoundError(
            f"Could not find codereview_new.jsonl under {p}. "
            "Download/extract CodeReview-New first, or pass a direct JSONL path."
        )
    return matches[0]


def normalize_newlines(s: Any) -> str:
    if s is None:
        return ""
    return str(s).replace("\r\n", "\n").replace("\r", "\n")


def trim_outer(s: str) -> str:
    return normalize_newlines(s).strip()


def trim_line_ends(s: str) -> str:
    return "\n".join(line.rstrip() for line in trim_outer(s).split("\n"))


def extract_code_from_markdown(text: str) -> str:
    """Remove a single fenced Markdown code block when the model returned one."""
    text = normalize_newlines(text).strip()
    # If the whole answer is one fenced code block, extract its contents.
    m = re.fullmatch(r"```(?:[A-Za-z0-9_+.#-]+)?\n(.*?)\n```", text, flags=re.DOTALL)
    if m:
        return m.group(1).strip("\n")
    # Otherwise, if there is exactly one fenced block, use it.
    blocks = re.findall(r"```(?:[A-Za-z0-9_+.#-]+)?\n(.*?)\n```", text, flags=re.DOTALL)
    if len(blocks) == 1:
        return blocks[0].strip("\n")
    return text


@dataclass(frozen=True)
class Span:
    start: int  # inclusive, 0-based old-line index
    end: int    # exclusive, 0-based old-line index; may equal start for insertion point
    tag: str

    def to_dict(self) -> dict[str, Any]:
        return {"start": self.start, "end": self.end, "tag": self.tag}


def changed_spans_old(old: str, new: str) -> list[Span]:
    old_lines = normalize_newlines(old).splitlines()
    new_lines = normalize_newlines(new).splitlines()
    sm = SequenceMatcher(a=old_lines, b=new_lines, autojunk=False)
    spans: list[Span] = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if tag == "insert":
            # For pure insertion, mark a zero-width insertion point after the previous old line.
            # start=end=0 means before the first line.
            spans.append(Span(start=i1, end=i1, tag=tag))
        else:
            spans.append(Span(start=i1, end=i2, tag=tag))
    return merge_adjacent_spans(spans)


def merge_adjacent_spans(spans: Sequence[Span]) -> list[Span]:
    if not spans:
        return []
    sorted_spans = sorted(spans, key=lambda s: (s.start, s.end))
    merged: list[Span] = [sorted_spans[0]]
    for span in sorted_spans[1:]:
        prev = merged[-1]
        # Merge overlapping or directly adjacent non-zero spans.
        if span.start <= prev.end:
            merged[-1] = Span(prev.start, max(prev.end, span.end), prev.tag + "+" + span.tag)
        else:
            merged.append(span)
    return merged


def changed_line_set_old(old: str, revised: str) -> set[int]:
    lines = normalize_newlines(old).splitlines()
    spans = changed_spans_old(old, revised)
    out: set[int] = set()
    for span in spans:
        if span.start == span.end:
            # Insertion: anchor to the previous line if available, otherwise the first line.
            if len(lines) == 0:
                out.add(0)
            elif span.start > 0:
                out.add(span.start - 1)
            else:
                out.add(0)
        else:
            out.update(range(span.start, span.end))
    return out


def mark_gold_locations(old: str, spans: Sequence[Span]) -> str:
    lines = normalize_newlines(old).splitlines()
    if not spans:
        return normalize_newlines(old)
    events_start: dict[int, list[str]] = {}
    events_end: dict[int, list[str]] = {}
    insertion_events: dict[int, list[str]] = {}
    for idx, span in enumerate(spans, 1):
        if span.start == span.end:
            insertion_events.setdefault(span.start, []).append(
                f'<GOLD_INSERTION_POINT id="{idx}" />'
            )
        else:
            events_start.setdefault(span.start, []).append(
                f'<GOLD_LOCATION_START id="{idx}" tag="{span.tag}">'
            )
            events_end.setdefault(span.end, []).append(f'</GOLD_LOCATION_END id="{idx}">')
    out: list[str] = []
    for i in range(0, len(lines) + 1):
        for marker in insertion_events.get(i, []):
            out.append(marker)
        for marker in events_start.get(i, []):
            out.append(marker)
        if i < len(lines):
            out.append(lines[i])
        for marker in events_end.get(i + 1, []):
            out.append(marker)
    return "\n".join(out)


def location_f1(old: str, prediction: str, gold: str) -> float:
    pred_lines = changed_line_set_old(old, prediction)
    gold_lines = changed_line_set_old(old, gold)
    if not pred_lines and not gold_lines:
        return 1.0
    if not pred_lines or not gold_lines:
        return 0.0
    inter = len(pred_lines & gold_lines)
    return (2.0 * inter) / (len(pred_lines) + len(gold_lines))


def compact_id(row: dict[str, Any], idx: int) -> str:
    for key in ("id", "idx", "original_id", "Original_id"):
        if key in row and str(row[key]).strip():
            return str(row[key])
    return f"crn-{idx:06d}"


def ensure_required(row: dict[str, Any], required: Sequence[str]) -> bool:
    return all(str(row.get(k, "")).strip() for k in required)
