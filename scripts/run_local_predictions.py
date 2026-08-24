#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

sys.path.append(str(Path(__file__).resolve().parent))
from common import read_jsonl


DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_CHAT_COMPLETIONS_URL = "http://127.0.0.1:1234/v1/chat/completions"
RETRY_DELAYS_SECONDS = [1.0, 2.0, 4.0]


class BackendRequestError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None, retryable: bool = False):
        super().__init__(message)
        self.status_code = status_code
        self.retryable = retryable


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Prompt JSONL produced by scripts/make_prompts.py")
    ap.add_argument("--output", required=True, help="Prediction JSONL output path")
    ap.add_argument("--model", required=True, help="Local model name exposed by the selected backend")
    ap.add_argument(
        "--backend",
        choices=["ollama", "chat_completions"],
        default="ollama",
        help="Local inference backend. 'chat_completions' is for local servers such as LM Studio, llama.cpp, or vLLM.",
    )
    ap.add_argument(
        "--base-url",
        default=None,
        help="Optional local endpoint override. Defaults depend on the backend.",
    )
    ap.add_argument("--temperature", type=float, default=0.0, help="Sampling temperature")
    ap.add_argument("--seed", type=int, default=42, help="Seed to request when the backend supports it")
    ap.add_argument("--num-predict", type=int, default=None, help="Optional Ollama max generated tokens")
    ap.add_argument("--timeout-seconds", type=float, default=300.0, help="Per-request timeout")
    ap.add_argument("--limit", type=int, default=None, help="Optional max number of prompts to process")
    ap.add_argument(
        "--continue-on-error",
        action="store_true",
        help="On unrecoverable per-example failures, write an empty prediction and continue.",
    )
    ap.add_argument(
        "--error-log",
        default=None,
        help="Optional JSONL file to append per-example backend errors.",
    )
    ap.add_argument(
        "--resume",
        action="store_true",
        help="Skip rows already present in the output file by (id, baseline)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not call the backend. Write placeholder predictions to validate file format.",
    )
    return ap.parse_args()


def backend_url(backend: str, base_url: str | None) -> str:
    if base_url:
        return base_url
    if backend == "ollama":
        return DEFAULT_OLLAMA_URL
    return DEFAULT_CHAT_COMPLETIONS_URL


def load_existing_keys(path: Path) -> set[tuple[str, str]]:
    if not path.exists():
        return set()
    keys: set[tuple[str, str]] = set()
    for row in read_jsonl(path):
        keys.add((str(row.get("id", "")), str(row.get("baseline", ""))))
    return keys


def iter_rows(
    rows: list[dict[str, Any]],
    existing_keys: set[tuple[str, str]],
    resume: bool,
    limit: int | None,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for row in rows:
        key = (str(row.get("id", "")), str(row.get("baseline", "")))
        if resume and key in existing_keys:
            continue
        selected.append(row)
        if limit is not None and len(selected) >= limit:
            break
    return selected


def get_messages(row: dict[str, Any]) -> list[dict[str, str]]:
    messages = row.get("messages")
    if isinstance(messages, list) and messages:
        cleaned: list[dict[str, str]] = []
        for msg in messages:
            cleaned.append(
                {
                    "role": str(msg.get("role", "user")),
                    "content": str(msg.get("content", "")),
                }
            )
        return cleaned
    prompt = str(row.get("prompt", "")).strip()
    if prompt:
        return [{"role": "user", "content": prompt}]
    raise ValueError(f"Row {row.get('id', '<missing-id>')} has no usable messages or prompt")


def make_dry_run_prediction(row: dict[str, Any]) -> str:
    return f"DRY_RUN_PLACEHOLDER {row.get('baseline', 'unknown')} {row.get('id', 'unknown')}"


def request_json(url: str, payload: dict[str, Any], timeout_seconds: float) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace").strip()
        retryable = exc.code in {408, 409, 429} or exc.code >= 500
        raise BackendRequestError(
            f"HTTP {exc.code} from local backend: {details or exc.reason}",
            status_code=exc.code,
            retryable=retryable,
        ) from exc
    except urllib.error.URLError as exc:
        raise BackendRequestError(
            f"Could not reach local backend at {url}: {exc.reason}",
            retryable=True,
        ) from exc
    except TimeoutError as exc:
        raise BackendRequestError("Timed out while waiting for the local backend", retryable=True) from exc
    except json.JSONDecodeError as exc:
        raise BackendRequestError(f"Local backend returned invalid JSON: {exc}") from exc


def request_ollama(
    url: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    seed: int | None,
    num_predict: int | None,
    timeout_seconds: float,
) -> tuple[str, str | None, str]:
    options: dict[str, Any] = {"temperature": temperature}
    if seed is not None:
        options["seed"] = seed
    if num_predict is not None:
        options["num_predict"] = num_predict
    num_ctx = os.environ.get("OLLAMA_NUM_CTX")
    if num_ctx:
        options["num_ctx"] = int(num_ctx)
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": options,
    }
    response = request_json(url, payload, timeout_seconds)
    prediction = str(response.get("message", {}).get("content", ""))
    if not prediction:
        raise BackendRequestError(f"Ollama response did not include message.content: {response}")
    response_id = str(response.get("created_at", "")) or None
    return prediction, response_id, f"backend=ollama temperature={temperature} seed={seed} num_predict={num_predict}"


def extract_chat_completion_text(response: dict[str, Any]) -> str:
    choices = response.get("choices")
    if not isinstance(choices, list) or not choices:
        raise BackendRequestError(f"Local chat-completions response did not include choices: {response}")
    message = choices[0].get("message", {})
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        out: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") in {"text", "output_text"}:
                out.append(str(block.get("text", "")))
        if out:
            return "".join(out)
    raise BackendRequestError(f"Could not extract text from local chat-completions response: {response}")


def request_chat_completions(
    url: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    seed: int | None,
    timeout_seconds: float,
) -> tuple[str, str | None, str]:
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if seed is not None:
        payload["seed"] = seed
    response = request_json(url, payload, timeout_seconds)
    prediction = extract_chat_completion_text(response)
    response_id = str(response.get("id", "")) or None
    return prediction, response_id, f"backend=chat_completions temperature={temperature} seed={seed}"


def request_prediction(
    backend: str,
    url: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    seed: int | None,
    num_predict: int | None,
    timeout_seconds: float,
) -> tuple[str, str | None, str]:
    if backend == "ollama":
        return request_ollama(url, model, messages, temperature, seed, num_predict, timeout_seconds)
    return request_chat_completions(url, model, messages, temperature, seed, timeout_seconds)


def request_with_retry(
    backend: str,
    url: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    seed: int | None,
    num_predict: int | None,
    timeout_seconds: float,
) -> tuple[str, str | None, str]:
    last_error: Exception | None = None
    for attempt in range(len(RETRY_DELAYS_SECONDS) + 1):
        try:
            return request_prediction(backend, url, model, messages, temperature, seed, num_predict, timeout_seconds)
        except BackendRequestError as exc:
            last_error = exc
            if attempt >= len(RETRY_DELAYS_SECONDS) or not exc.retryable:
                raise
            delay = RETRY_DELAYS_SECONDS[attempt]
            print(
                f"Transient local-backend error on attempt {attempt + 1}; retrying in {delay:.1f}s: {exc}",
                file=sys.stderr,
            )
            time.sleep(delay)
    assert last_error is not None
    raise last_error


def write_record(handle, record: dict[str, Any]) -> None:
    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    handle.flush()


def write_error(handle, record: dict[str, Any]) -> None:
    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    handle.flush()


def main() -> None:
    args = parse_args()
    rows = read_jsonl(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    url = backend_url(args.backend, args.base_url)

    existing_keys = load_existing_keys(output_path) if args.resume else set()
    selected_rows = iter_rows(rows, existing_keys, args.resume, args.limit)

    mode = "a" if args.resume and output_path.exists() else "w"
    error_handle = None
    if args.error_log:
        error_path = Path(args.error_log)
        error_path.parent.mkdir(parents=True, exist_ok=True)
        error_handle = open(error_path, "a", encoding="utf-8")

    with open(output_path, mode, encoding="utf-8") as out:
        for idx, row in enumerate(selected_rows, 1):
            messages = get_messages(row)
            try:
                if args.dry_run:
                    prediction = make_dry_run_prediction(row)
                    response_id = None
                    sampling_note = "dry_run placeholder; local backend not called"
                else:
                    prediction, response_id, sampling_note = request_with_retry(
                        backend=args.backend,
                        url=url,
                        model=args.model,
                        messages=messages,
                        temperature=args.temperature,
                        seed=args.seed,
                        num_predict=args.num_predict,
                        timeout_seconds=args.timeout_seconds,
                    )
            except Exception as exc:
                if not args.continue_on_error:
                    if error_handle is not None:
                        write_error(
                            error_handle,
                            {
                                "id": row.get("id", ""),
                                "baseline": row.get("baseline", ""),
                                "model": args.model,
                                "backend": args.backend,
                                "error_type": exc.__class__.__name__,
                                "error": str(exc),
                            },
                        )
                    raise
                prediction = ""
                response_id = None
                sampling_note = f"error: {exc.__class__.__name__}: {exc}"
                if error_handle is not None:
                    write_error(
                        error_handle,
                        {
                            "id": row.get("id", ""),
                            "baseline": row.get("baseline", ""),
                            "model": args.model,
                            "backend": args.backend,
                            "error_type": exc.__class__.__name__,
                            "error": str(exc),
                        },
                    )
                print(
                    f"[{idx}/{len(selected_rows)}] failed {row['id']} baseline={row['baseline']}: {exc}",
                    file=sys.stderr,
                )

            record: dict[str, Any] = {
                "id": row["id"],
                "baseline": row["baseline"],
                "prediction": prediction,
                "model": args.model,
                "backend": args.backend,
                "sampling_note": sampling_note,
            }
            if response_id is not None:
                record["response_id"] = response_id
            write_record(out, record)
            print(
                f"[{idx}/{len(selected_rows)}] wrote {row['id']} baseline={row['baseline']}",
                file=sys.stderr,
            )

    if error_handle is not None:
        error_handle.close()

    print(
        json.dumps(
            {
                "input": args.input,
                "output": args.output,
                "model": args.model,
                "backend": args.backend,
                "base_url": url,
                "processed": len(selected_rows),
                "resume": args.resume,
                "dry_run": args.dry_run,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
