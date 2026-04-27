#!/usr/bin/env bash
set -euo pipefail

N="${1:-100}"
SEED="${2:-42}"

python3 scripts/prepare_crn_subset.py --input data_raw --output "data/processed/crn_pilot${N}.jsonl" --n "$N" --seed "$SEED"
python3 scripts/make_prompts.py --input "data/processed/crn_pilot${N}.jsonl" --outdir "prompts/crn_pilot${N}"
python3 scripts/extract_existing_predictions.py --input "data/processed/crn_pilot${N}.jsonl" --output "predictions/crn_pilot${N}_existing.jsonl"
python3 scripts/evaluate_predictions.py --gold "data/processed/crn_pilot${N}.jsonl" --pred "predictions/crn_pilot${N}_existing.jsonl" --outdir "reports/crn_pilot${N}_existing"
