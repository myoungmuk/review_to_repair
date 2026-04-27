# AGENTS.md

## Project goal
This repository is for a preparatory Review-to-Repair study.
The main experiment is Pilot 1 on CodeReview-New.
The goal is to compare no_review, direct, and gold_location baselines to diagnose whether change localisation is a bottleneck.

## Research constraints
- Do not claim that direct comment-to-patch is the novelty.
- Do not change the definitions of no_review, direct, or gold_location without explicit instruction.
- Do not change evaluation metrics to make results look better.
- Do not invent experiment results.
- Treat CodeReview-New as snippet-level/hunk-level data, not full-file localisation data.

## Important commands
Run the tiny demo:
```bash
python3 scripts/prepare_crn_subset.py --input demo_data/demo_crn_tiny.jsonl --output data/processed/demo_subset.jsonl --n 2
python3 scripts/make_prompts.py --input data/processed/demo_subset.jsonl --outdir prompts/demo
python3 scripts/extract_existing_predictions.py --input data/processed/demo_subset.jsonl --output predictions/demo_existing.jsonl
python3 scripts/evaluate_predictions.py --gold data/processed/demo_subset.jsonl --pred predictions/demo_existing.jsonl --outdir reports/demo
```

Run Pilot 1 existing-result pipeline:
```bash
bash run_pilot1_existing.sh 100 42
```

Evaluate new predictions:
```bash
python3 scripts/evaluate_predictions.py --gold data/processed/crn_pilot100.jsonl --pred predictions/crn_pilot100_your_llm.jsonl --outdir reports/crn_pilot100_your_llm
```

Generate local LLM predictions:
```bash
python3 scripts/run_local_predictions.py --input prompts/crn_pilot100/no_review_prompts.jsonl --output predictions/crn_pilot100_no_review.jsonl --model YOUR_LOCAL_MODEL --backend ollama --resume
python3 scripts/run_local_predictions.py --input prompts/crn_pilot100/direct_prompts.jsonl --output predictions/crn_pilot100_direct.jsonl --model YOUR_LOCAL_MODEL --backend ollama --resume
python3 scripts/run_local_predictions.py --input prompts/crn_pilot100/gold_location_prompts.jsonl --output predictions/crn_pilot100_gold_location.jsonl --model YOUR_LOCAL_MODEL --backend ollama --resume
```

Compute gains:
```bash
python3 scripts/bootstrap_gain.py --per-example reports/crn_pilot100_your_llm/per_example_metrics.csv --baseline-a no_review --baseline-b direct --metric exact_match_line_trim --iters 1000 --seed 42
python3 scripts/bootstrap_gain.py --per-example reports/crn_pilot100_your_llm/per_example_metrics.csv --baseline-a direct --baseline-b gold_location --metric exact_match_line_trim --iters 1000 --seed 42
```

## Coding rules
- Prefer small, high-confidence changes.
- Keep scripts runnable from the repository root.
- Do not require heavy dependencies unless necessary.
- Preserve JSONL formats.
- Do not commit raw datasets, API keys, or large prediction files.
- Prefer local LLM backends over hosted APIs for this repo unless explicitly requested.

## Done means
- The command requested by the user runs successfully.
- The generated files are listed.
- Any limitations are documented.
- No research result is fabricated.
