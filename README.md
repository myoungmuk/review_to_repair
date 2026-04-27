# Review-to-Repair Pilot 1 on CodeReview-New

This package sets up a small preparatory experiment for Review-to-Repair using CodeReview-New.

Goal: compare No-review, Direct, and Gold-location inputs, then measure whether gold location information helps.

## What this package can do

1. Prepare a CodeReview-New subset from `codereview_new.jsonl`.
2. Create prompts for three baselines:
   - `no_review`: original code only.
   - `direct`: original code + review comment.
   - `gold_location`: original code + review comment + gold changed location markers.
3. Extract the existing `gpt_code` and `model_code` predictions already distributed with CodeReview-New, so you can reproduce direct and CodeReviewer-style text-matching summaries.
4. Evaluate predictions using exact match and location overlap.

## Important caveat

CodeReview-New is a code-snippet/hunk-level benchmark. That means the `old` field is already the code snippet to modify. Therefore, the gold-location baseline here diagnoses *within-snippet localisation*, not full-file localisation. Full-file localisation requires reconstructing files from commit or pull-request metadata, which is a separate extension.

## Expected dataset

Download the CodeReview-New supplementary data from the authors' public project page and place `codereview_new.jsonl` anywhere under `data_raw/`.
The scripts search recursively for this filename.

Expected fields in `codereview_new.jsonl`:

- `old`: pre-review code snippet.
- `review`: review suggestion.
- `new`: post-review revised code snippet.
- `commit_url`: source URL.
- `gpt_code`: ChatGPT code output distributed by the authors.
- `model_code`: CodeReviewer model output distributed by the authors.
- `language`: programming language.

## Quick start with a tiny synthetic demo

```bash
cd review_to_repair_crn
python3 scripts/prepare_crn_subset.py --input demo_data/demo_crn_tiny.jsonl --output data/processed/demo_subset.jsonl --n 2
python3 scripts/make_prompts.py --input data/processed/demo_subset.jsonl --outdir prompts/demo
python3 scripts/extract_existing_predictions.py --input data/processed/demo_subset.jsonl --output predictions/demo_existing.jsonl
python3 scripts/evaluate_predictions.py --gold data/processed/demo_subset.jsonl --pred predictions/demo_existing.jsonl --outdir reports/demo
```

## Quick start with CodeReview-New

```bash
cd review_to_repair_crn
# Put codereview_new.jsonl under data_raw/ first.
python3 scripts/prepare_crn_subset.py --input data_raw --output data/processed/crn_pilot100.jsonl --n 100 --seed 42
python3 scripts/make_prompts.py --input data/processed/crn_pilot100.jsonl --outdir prompts/crn_pilot100
python3 scripts/extract_existing_predictions.py --input data/processed/crn_pilot100.jsonl --output predictions/crn_existing_gpt_codereviewer.jsonl
python3 scripts/evaluate_predictions.py --gold data/processed/crn_pilot100.jsonl --pred predictions/crn_existing_gpt_codereviewer.jsonl --outdir reports/crn_existing
```

## How to add new local LLM predictions

Run a local inference server first, then generate predictions from the prompt JSONL files.

Example with Ollama:

```bash
python3 scripts/run_local_predictions.py --input prompts/crn_pilot100/no_review_prompts.jsonl --output predictions/crn_pilot100_no_review.jsonl --model YOUR_LOCAL_MODEL --backend ollama --resume
python3 scripts/run_local_predictions.py --input prompts/crn_pilot100/direct_prompts.jsonl --output predictions/crn_pilot100_direct.jsonl --model YOUR_LOCAL_MODEL --backend ollama --resume
python3 scripts/run_local_predictions.py --input prompts/crn_pilot100/gold_location_prompts.jsonl --output predictions/crn_pilot100_gold_location.jsonl --model YOUR_LOCAL_MODEL --backend ollama --resume
```

Example with a local chat-completions server such as LM Studio, llama.cpp, or vLLM:

```bash
python3 scripts/run_local_predictions.py --input prompts/crn_pilot100/no_review_prompts.jsonl --output predictions/crn_pilot100_no_review.jsonl --model YOUR_LOCAL_MODEL --backend chat_completions --base-url http://127.0.0.1:1234/v1/chat/completions --resume
```

Then merge the three prediction files into one JSONL file with this format:

Create a JSONL file with this format:

```json
{"id": "example-id", "baseline": "direct", "prediction": "revised code snippet only"}
```

Then evaluate:

```bash
python3 scripts/evaluate_predictions.py --gold data/processed/crn_pilot100.jsonl --pred predictions/your_predictions.jsonl --outdir reports/your_run
```

## Suggested experiment order

1. Run existing `gpt_code` and `model_code` evaluation on the selected subset.
2. Generate `no_review`, `direct`, and `gold_location` outputs using the same LLM and deterministic decoding.
3. Evaluate exact match and location overlap.
4. Compute:
   - review gain = direct - no_review.
   - gold-location gain = gold_location - direct.

## Multi-model diagnostic run

The multi-model runner keeps the same seed=42 CodeReview-New 100-example subset, the same three conditions, and the same two reported metrics. It only varies the local code LLM.

The default config is `configs/multi_model_r2r_seed42.json`. It selects installed Ollama tags from these required families:

- `qwen2.5-coder:7b`
- one `deepseek-coder` 6.7B/7B tag
- `codegemma:7b`

The script checks `ollama list` first. If a required family is missing, it stops and prints suggested `ollama pull ...` commands without pulling large models automatically. `starcoder2:7b` is excluded from the main experiment because the smoke test returned mostly empty outputs under the current Ollama chat backend. `qwen2.5-coder:3b` is only a fallback candidate if `codegemma:7b` is unavailable, and should not be used in the main full run without explicit approval.

Smoke test after all three main model families are installed:

```bash
python scripts/run_multi_model_r2r.py --limit 10 --output-root results/multi_model_r2r_seed42_smoke10 --resume --continue-on-error --num-predict 1024
```

Full run after smoke test approval:

```bash
python scripts/run_multi_model_r2r.py --output-root results/multi_model_r2r_seed42 --resume --continue-on-error --num-predict 1024
```

CodeGemma-only smoke test after installing `codegemma:7b`:

```bash
python scripts/run_multi_model_r2r.py --models codegemma:7b --limit 10 --output-root results/multi_model_r2r_seed42_smoke10_codegemma --resume --continue-on-error --num-predict 1024
```

Outputs are written under `results/<run_name>/` with enriched generation JSONL files, per-model metrics, paired bootstrap gains, an integrity report, and a paper-ready Markdown/CSV summary table.
