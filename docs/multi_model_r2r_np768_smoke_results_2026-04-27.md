# Multi-Model R2R np768 Smoke Results

Date: 2026-04-27

This note records the clean `--num-predict 768` smoke result for the
multi-model Review-to-Repair experiment. It is not the full 100-example result.

## Run

Clean smoke output root:

```text
results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab_retry1
```

Command:

```bash
python scripts/run_multi_model_r2r.py \
  --limit 10 \
  --output-root results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab_retry1 \
  --num-predict 768 \
  --resume \
  --continue-on-error
```

Main models:

- `qwen2.5-coder:7b`
- `deepseek-coder:6.7b`
- `codegemma:7b`

Installed but excluded from main metrics:

- `starcoder2:7b`
- `qwen2.5-coder:3b`
- `devstral:24b`

`starcoder2:7b` remains excluded because earlier smoke tests produced mostly
empty outputs under the Ollama chat backend.

## Integrity

The clean retry produced the expected 90 outputs:

```text
3 models x 3 conditions x 10 examples = 90 outputs
```

All 90 rows were confirmed as backend generations in
`generations/all_generations.jsonl`.

| model | condition | output count | generation errors | extraction failures | evaluation failures | valid evaluations |
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

These are smoke-test metrics on only 10 examples. Do not present them as final
paper results.

| model | condition | n valid | exact_match_line_trim | location_overlap_f1 |
| --- | --- | ---: | ---: | ---: |
| qwen2.5-coder:7b | no_review | 10 | 0.000 | 0.460 |
| qwen2.5-coder:7b | direct | 10 | 0.100 | 0.439 |
| qwen2.5-coder:7b | gold_location | 10 | 0.000 | 0.943 |
| deepseek-coder:6.7b | no_review | 10 | 0.000 | 0.457 |
| deepseek-coder:6.7b | direct | 10 | 0.000 | 0.500 |
| deepseek-coder:6.7b | gold_location | 10 | 0.000 | 0.483 |
| codegemma:7b | no_review | 10 | 0.000 | 0.776 |
| codegemma:7b | direct | 10 | 0.100 | 0.641 |
| codegemma:7b | gold_location | 10 | 0.000 | 0.873 |

Paper-ready smoke table:

| model | no_review_exact | direct_exact | gold_location_exact | no_review_loc_f1 | direct_loc_f1 | gold_location_loc_f1 | direct_minus_no_review_exact | direct_minus_no_review_loc_f1 | gold_location_minus_direct_exact | gold_location_minus_direct_loc_f1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| qwen2.5-coder:7b | 0.000 | 0.100 | 0.000 | 0.460 | 0.439 | 0.943 | 0.100 | -0.021 | -0.100 | 0.504 |
| deepseek-coder:6.7b | 0.000 | 0.000 | 0.000 | 0.457 | 0.500 | 0.483 | 0.000 | 0.043 | 0.000 | -0.017 |
| codegemma:7b | 0.000 | 0.100 | 0.000 | 0.776 | 0.641 | 0.873 | 0.100 | -0.135 | -0.100 | 0.231 |
| macro_average | 0.000 | 0.067 | 0.000 | 0.564 | 0.527 | 0.766 | 0.067 | -0.037 | -0.067 | 0.239 |

## Bootstrap Gain Summary

| model | comparison | metric | gain | 95% CI |
| --- | --- | --- | ---: | --- |
| qwen2.5-coder:7b | direct - no_review | exact_match_line_trim | 0.100 | [0.000, 0.300] |
| qwen2.5-coder:7b | direct - no_review | location_overlap_f1 | -0.021 | [-0.260, 0.213] |
| qwen2.5-coder:7b | gold_location - direct | exact_match_line_trim | -0.100 | [-0.300, 0.000] |
| qwen2.5-coder:7b | gold_location - direct | location_overlap_f1 | 0.504 | [0.274, 0.724] |
| deepseek-coder:6.7b | direct - no_review | exact_match_line_trim | 0.000 | [0.000, 0.000] |
| deepseek-coder:6.7b | direct - no_review | location_overlap_f1 | 0.043 | [-0.121, 0.239] |
| deepseek-coder:6.7b | gold_location - direct | exact_match_line_trim | 0.000 | [0.000, 0.000] |
| deepseek-coder:6.7b | gold_location - direct | location_overlap_f1 | -0.017 | [-0.147, 0.106] |
| codegemma:7b | direct - no_review | exact_match_line_trim | 0.100 | [0.000, 0.300] |
| codegemma:7b | direct - no_review | location_overlap_f1 | -0.135 | [-0.435, 0.172] |
| codegemma:7b | gold_location - direct | exact_match_line_trim | -0.100 | [-0.300, 0.000] |
| codegemma:7b | gold_location - direct | location_overlap_f1 | 0.231 | [-0.039, 0.507] |
| macro_average | direct - no_review | exact_match_line_trim | 0.067 | [0.000, 0.200] |
| macro_average | direct - no_review | location_overlap_f1 | -0.037 | [-0.210, 0.150] |
| macro_average | gold_location - direct | exact_match_line_trim | -0.067 | [-0.200, 0.000] |
| macro_average | gold_location - direct | location_overlap_f1 | 0.239 | [0.069, 0.417] |

## Truncation And Formatting Risk

The retry smoke has no empty outputs, no near generation cap flags, and no
generation/evaluation failures.

One short formatting flag remains:

| model | condition | example_id | raw chars | extracted chars | flags |
| --- | --- | --- | ---: | ---: | --- |
| deepseek-coder:6.7b | gold_location | `crn-008823` | 216 | 216 | `unclosed_code_fence` |

This appears to be a short formatting artifact rather than a generation-cap
truncation case because it is not near the output length cap.

## Interpretation

The smoke supports continuing with `--num-predict 768`:

- All model-condition cells produced 10 valid evaluations.
- The generation source was backend for all 90 outputs.
- The earlier `np512` near-cap deepseek risk disappeared.
- The only remaining flag is a short unclosed code fence in one deepseek
  gold-location output.

Research-wise, the 10-example smoke is consistent with the paper's intended
message:

- Gold-location information can strongly increase changed-line overlap for
  some models, especially qwen in this smoke.
- Exact-match success does not rise with that location-overlap increase in the
  smoke; macro exact is lower for gold_location than direct.
- Model-specific behavior matters: deepseek shows little gold-location benefit
  here, while qwen and codegemma show larger location-overlap changes.

Because this is only a 10-example smoke, these are diagnostic signals only. The
full 100-example run is still required before updating the paper's quantitative
claims.

## Next Step

Recommended full-run command after explicit user approval:

```bash
python scripts/run_multi_model_r2r.py \
  --output-root results/multi_model_r2r_seed42_np768 \
  --num-predict 768 \
  --resume \
  --continue-on-error
```

Expected full-run output count:

```text
3 models x 3 conditions x 100 examples = 900 outputs
```

Do not run the full experiment without explicit user approval.
