# Multi-Model R2R np1024 Smoke Results

Date: 2026-04-27

This document records the 10-example shared-cap smoke run with `num_predict=1024`.
It is a pre-full-run diagnostic, not a final paper result.

## Command

```bash
python scripts/run_multi_model_r2r.py \
  --limit 10 \
  --output-root results/multi_model_r2r_seed42_smoke10_all3_np1024_jupyterlab \
  --num-predict 1024 \
  --resume \
  --continue-on-error
```

## Run Scope

- Data: `data/processed/crn_pilot100.jsonl`
- Prompt directory: `prompts/crn_pilot100`
- Examples: 10
- Models:
  - `qwen2.5-coder:7b`
  - `deepseek-coder:6.7b`
  - `codegemma:7b`
- Conditions:
  - `no_review`
  - `direct`
  - `gold_location`
- Expected outputs: 90
- Actual outputs: 90
- Output root: `results/multi_model_r2r_seed42_smoke10_all3_np1024_jupyterlab`

## Integrity

All model-condition cells completed with valid evaluations.

| model | condition | output_count | generation_error_count | extraction_failure_count | evaluation_failure_count | valid_evaluation_count |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| qwen2.5-coder:7b | no_review | 10 | 0 | 0 | 0 | 10 |
| qwen2.5-coder:7b | direct | 10 | 0 | 0 | 0 | 10 |
| qwen2.5-coder:7b | gold_location | 10 | 0 | 0 | 0 | 10 |
| deepseek-coder:6.7b | no_review | 10 | 0 | 0 | 0 | 10 |
| deepseek-coder:6.7b | direct | 10 | 0 | 0 | 0 | 10 |
| deepseek-coder:6.7b | gold_location | 10 | 0 | 0 | 0 | 10 |
| codegemma:7b | no_review | 10 | 0 | 0 | 0 | 10 |
| codegemma:7b | direct | 10 | 0 | 0 | 0 | 10 |
| codegemma:7b | gold_location | 10 | 0 | 0 | 0 | 10 |

## Metrics

| model | no_review exact | direct exact | gold_location exact | no_review loc F1 | direct loc F1 | gold_location loc F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen2.5-coder:7b | 0.000 | 0.100 | 0.000 | 0.460 | 0.439 | 0.943 |
| deepseek-coder:6.7b | 0.000 | 0.000 | 0.000 | 0.457 | 0.500 | 0.483 |
| codegemma:7b | 0.000 | 0.100 | 0.000 | 0.776 | 0.641 | 0.873 |
| macro_average | 0.000 | 0.067 | 0.000 | 0.564 | 0.527 | 0.766 |

## Bootstrap Gain Summary

| model | comparison | metric | gain | 95% CI |
| --- | --- | --- | ---: | --- |
| macro_average | direct - no_review | exact_match_line_trim | 0.067 | [0.000, 0.200] |
| macro_average | direct - no_review | location_overlap_f1 | -0.037 | [-0.210, 0.150] |
| macro_average | gold_location - direct | exact_match_line_trim | -0.067 | [-0.200, 0.000] |
| macro_average | gold_location - direct | location_overlap_f1 | 0.239 | [0.069, 0.417] |

## Truncation And Format Diagnostics

- Empty raw outputs: 0
- Empty extracted outputs: 0
- Near generation cap risk: 0
- Suspicious cases: 1

The only flagged case was:

| model | condition | example_id | raw_output_len_chars | extracted_code_len_chars | flags |
| --- | --- | --- | ---: | ---: | --- |
| deepseek-coder:6.7b | gold_location | crn-008823 | 216 | 216 | `unclosed_code_fence` |

This is the same short formatting artifact observed in the clean `np768` smoke. It is not a near-cap truncation case.

## Interpretation

The `np1024` smoke passed the same structural checks as the clean `np768` smoke:

- 90/90 outputs were produced.
- No generation, extraction, or evaluation failures occurred.
- No near-cap truncation risk was observed.
- The metrics and output-length diagnostics are effectively identical to the `np768` smoke.

This means `num_predict=1024` is safe to use, but it does not provide evidence that `1024` is necessary. The `np768` cap remains sufficient for the full run based on smoke diagnostics. If the priority is maximum conservativeness against truncation concerns, `np1024` can be used for the full run at a modest runtime cost.
