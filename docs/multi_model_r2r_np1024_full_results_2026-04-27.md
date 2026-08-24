# Multi-Model R2R np1024 Full Results

Date: 2026-04-27

This document records the completed 100-example multi-model Review-to-Repair
run with `num_predict=1024`.

## Command

Primary command:

```bash
python scripts/run_multi_model_r2r.py \
  --output-root results/multi_model_r2r_seed42_np1024 \
  --num-predict 1024 \
  --resume \
  --continue-on-error
```

During the final CodeGemma recovery pass, the runner was resumed without
`--continue-on-error` and with explicit Ollama context:

```bash
OLLAMA_NUM_CTX=8192 python scripts/run_multi_model_r2r.py \
  --output-root results/multi_model_r2r_seed42_np1024 \
  --num-predict 1024 \
  --resume
```

`OLLAMA_NUM_CTX=8192` was used to avoid Ollama's oversized default context
request for CodeGemma. CodeGemma's logged trained context is 8192, so this
matches the model's effective context limit rather than changing the task.

## Scope

- Data: `data/processed/crn_pilot100.jsonl`
- Prompt directory: `prompts/crn_pilot100`
- Examples: 100
- Conditions: `no_review`, `direct`, `gold_location`
- Metrics: `exact_match_line_trim`, `location_overlap_f1`
- Models:
  - `qwen2.5-coder:7b`
  - `deepseek-coder:6.7b`
  - `codegemma:7b`
- Excluded from metrics:
  - `starcoder2:7b`, due to empty outputs under the current Ollama chat backend.

## Output Files

- Output root: `results/multi_model_r2r_seed42_np1024`
- Combined generations: `results/multi_model_r2r_seed42_np1024/generations/all_generations.jsonl`
- Summary: `results/multi_model_r2r_seed42_np1024/summary.md`
- Paper table: `results/multi_model_r2r_seed42_np1024/paper_results_table.csv`
- Metrics: `results/multi_model_r2r_seed42_np1024/metrics_by_model_condition.csv`
- Bootstrap gains: `results/multi_model_r2r_seed42_np1024/bootstrap_gains_by_model.csv`
- Integrity: `results/multi_model_r2r_seed42_np1024/integrity_report.csv`
- Length diagnostics: `results/multi_model_r2r_seed42_np1024/output_length_diagnostics.csv`
- Truncation flags: `results/multi_model_r2r_seed42_np1024/truncation_risk_cases.csv`

## Integrity

The final combined JSONL has 900 rows.

| check | value |
| --- | ---: |
| expected outputs | 900 |
| actual outputs | 900 |
| backend-generated rows | 900 |
| generation errors | 0 |
| extraction failures | 0 |
| evaluation failures | 0 |
| valid evaluations | 900 |

All model-condition cells have exactly 100 outputs and 100 valid evaluations.

## Main Metrics

| model | no_review exact | direct exact | gold_location exact | no_review loc F1 | direct loc F1 | gold_location loc F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen2.5-coder:7b | 0.000 | 0.070 | 0.090 | 0.503 | 0.567 | 0.748 |
| deepseek-coder:6.7b | 0.000 | 0.020 | 0.010 | 0.480 | 0.550 | 0.558 |
| codegemma:7b | 0.000 | 0.050 | 0.060 | 0.622 | 0.689 | 0.804 |
| macro_average | 0.000 | 0.047 | 0.053 | 0.535 | 0.602 | 0.703 |

## Paper-Ready Gain Summary

| model | direct - no_review exact | direct - no_review loc F1 | gold_location - direct exact | gold_location - direct loc F1 |
| --- | ---: | ---: | ---: | ---: |
| qwen2.5-coder:7b | 0.070 | 0.064 | 0.020 | 0.181 |
| deepseek-coder:6.7b | 0.020 | 0.070 | -0.010 | 0.008 |
| codegemma:7b | 0.050 | 0.067 | 0.010 | 0.116 |
| macro_average | 0.047 | 0.067 | 0.007 | 0.102 |

## Bootstrap Gain Summary

| model | comparison | metric | gain | 95% CI |
| --- | --- | --- | ---: | --- |
| qwen2.5-coder:7b | direct - no_review | exact_match_line_trim | 0.070 | [0.020, 0.120] |
| qwen2.5-coder:7b | direct - no_review | location_overlap_f1 | 0.064 | [-0.007, 0.140] |
| qwen2.5-coder:7b | gold_location - direct | exact_match_line_trim | 0.020 | [-0.050, 0.090] |
| qwen2.5-coder:7b | gold_location - direct | location_overlap_f1 | 0.181 | [0.106, 0.253] |
| deepseek-coder:6.7b | direct - no_review | exact_match_line_trim | 0.020 | [0.000, 0.050] |
| deepseek-coder:6.7b | direct - no_review | location_overlap_f1 | 0.070 | [0.036, 0.104] |
| deepseek-coder:6.7b | gold_location - direct | exact_match_line_trim | -0.010 | [-0.030, 0.000] |
| deepseek-coder:6.7b | gold_location - direct | location_overlap_f1 | 0.008 | [-0.029, 0.046] |
| codegemma:7b | direct - no_review | exact_match_line_trim | 0.050 | [0.010, 0.090] |
| codegemma:7b | direct - no_review | location_overlap_f1 | 0.067 | [-0.006, 0.136] |
| codegemma:7b | gold_location - direct | exact_match_line_trim | 0.010 | [-0.040, 0.060] |
| codegemma:7b | gold_location - direct | location_overlap_f1 | 0.116 | [0.053, 0.177] |
| macro_average | direct - no_review | exact_match_line_trim | 0.047 | [0.023, 0.073] |
| macro_average | direct - no_review | location_overlap_f1 | 0.067 | [0.026, 0.109] |
| macro_average | gold_location - direct | exact_match_line_trim | 0.007 | [-0.027, 0.043] |
| macro_average | gold_location - direct | location_overlap_f1 | 0.102 | [0.064, 0.139] |

## Truncation And Format Diagnostics

- Empty raw outputs: 0
- Empty extracted outputs: 0
- Near `num_predict` cap risk: 0
- Suspicious cases: 5

All suspicious cases are short `unclosed_code_fence` formatting flags from
DeepSeek. None are near-cap truncation cases.

| model | condition | example_id | raw chars | extracted chars | flags |
| --- | --- | --- | ---: | ---: | --- |
| deepseek-coder:6.7b | no_review | `crn-006672` | 697 | 697 | `unclosed_code_fence` |
| deepseek-coder:6.7b | no_review | `crn-012114` | 596 | 596 | `unclosed_code_fence` |
| deepseek-coder:6.7b | no_review | `crn-006483` | 814 | 814 | `unclosed_code_fence` |
| deepseek-coder:6.7b | gold_location | `crn-008823` | 216 | 216 | `unclosed_code_fence` |
| deepseek-coder:6.7b | gold_location | `crn-009938` | 714 | 714 | `unclosed_code_fence` |

## Backend Recovery Notes

The full run encountered transient Ollama backend failures during CodeGemma
generation. Some failed rows with empty outputs were written during the initial
`--continue-on-error` pass. Those failed rows were backed up and removed from
the active per-condition JSONL files before resuming.

Backups kept in the result directory:

- `results/multi_model_r2r_seed42_np1024/generations/codegemma-7b/no_review.jsonl.failed_before_resume_bak`
- `results/multi_model_r2r_seed42_np1024/generations/codegemma-7b/direct.jsonl.failed_before_resume_bak`
- `results/multi_model_r2r_seed42_np1024/generations/codegemma-7b/gold_location.jsonl.failed_before_resume2_bak`
- `results/multi_model_r2r_seed42_np1024/generations/codegemma-7b/gold_location.jsonl.failed_before_resume3_bak`

The final active JSONL files contain no generation errors, extraction failures,
or evaluation failures.

## Interpretation For The Paper

The multi-model full run strengthens the original single-model claim:

- Review comments improve exact repair over no-review in all three models.
- Gold location reliably improves location overlap, especially for qwen and codegemma.
- Gold location produces little or no additional exact-match gain over direct review.

Macro-level result:

- `direct - no_review` exact gain: `+0.047`, 95% CI `[0.023, 0.073]`.
- `gold_location - direct` exact gain: `+0.007`, 95% CI `[-0.027, 0.043]`.
- `gold_location - direct` location-F1 gain: `+0.102`, 95% CI `[0.064, 0.139]`.

This supports the paper's diagnostic message: location information helps models
touch more target lines, but this improvement does not reliably convert into
exact repair success.
