# Multi-Model Review-to-Repair Seed42

## Run
- Started UTC: 2026-04-26T05:52:07.017536+00:00
- Completed UTC: 2026-04-26T05:52:07.167994+00:00
- Data: data/processed/crn_pilot100.jsonl (10 examples from the seed=42 CodeReview-New pilot subset)
- Conditions: no_review, direct, gold_location
- Metrics: exact_match_line_trim, location_overlap_f1
- Models: qwen2.5-coder:7b, deepseek-coder:6.7b
- Installed Ollama models observed: starcoder2:7b, deepseek-coder:6.7b, qwen2.5-coder:3b, qwen2.5-coder:7b
- Output root: C:\Users\myoun\Desktop\review_to_repair_crn\results\multi_model_r2r_seed42_smoke10

## Excluded Models
- starcoder2:7b: excluded due to empty outputs under current Ollama chat backend
- Excluded models are not included in paper-ready metrics or macro averages.

## Fallback Candidates
- fallback_if_codegemma_unavailable: qwen2.5-coder:3b. Installed fallback candidate only. Do not use in the main full run unless explicitly approved.

## Post-Processing Rule
- The same extraction rule is applied to every model and condition.
- If one or more fenced Markdown code blocks are present, the longest non-empty block is used as the revised snippet.
- If no code fence is present, leading wrapper labels such as revised-code introductions are removed and the remaining raw text is evaluated.
- Gold-location marker tags are stripped if a model echoes them.

## Execution Commands
- Smoke test: `python scripts/run_multi_model_r2r.py --limit 10 --output-root results/multi_model_r2r_seed42_smoke10 --resume --continue-on-error --num-predict 1024`
- Full run after approval: `python scripts/run_multi_model_r2r.py --output-root results/multi_model_r2r_seed42 --resume --continue-on-error --num-predict 1024`

## Generation Accounting
| model | condition | selected_examples | existing_rows_reused | legacy_predictions_reused | backend_generations | errors |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 10 | 10 | 0 | 0 | 0 |
| qwen2.5-coder:7b | direct | 10 | 10 | 0 | 0 | 0 |
| qwen2.5-coder:7b | gold_location | 10 | 10 | 0 | 0 | 0 |
| deepseek-coder:6.7b | no_review | 10 | 10 | 0 | 0 | 0 |
| deepseek-coder:6.7b | direct | 10 | 10 | 0 | 0 | 0 |
| deepseek-coder:6.7b | gold_location | 10 | 10 | 0 | 0 | 0 |

## Metrics By Model And Condition
| model | condition | n_valid | exact_match_line_trim | location_overlap_f1 |
| --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 10 | 0.000 | 0.460 |
| qwen2.5-coder:7b | direct | 10 | 0.100 | 0.539 |
| qwen2.5-coder:7b | gold_location | 10 | 0.000 | 0.913 |
| deepseek-coder:6.7b | no_review | 10 | 0.000 | 0.447 |
| deepseek-coder:6.7b | direct | 10 | 0.000 | 0.500 |
| deepseek-coder:6.7b | gold_location | 10 | 0.000 | 0.483 |

## Gains With Paired Bootstrap 95% CI
| model | comparison | metric | paired_n | gain | ci95_low | ci95_high |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | direct - no_review | exact_match_line_trim | 10 | 0.100 | 0.000 | 0.300 |
| qwen2.5-coder:7b | direct - no_review | location_overlap_f1 | 10 | 0.079 | -0.140 | 0.308 |
| qwen2.5-coder:7b | gold_location - direct | exact_match_line_trim | 10 | -0.100 | -0.300 | 0.000 |
| qwen2.5-coder:7b | gold_location - direct | location_overlap_f1 | 10 | 0.374 | 0.163 | 0.615 |
| deepseek-coder:6.7b | direct - no_review | exact_match_line_trim | 10 | 0.000 | 0.000 | 0.000 |
| deepseek-coder:6.7b | direct - no_review | location_overlap_f1 | 10 | 0.053 | -0.105 | 0.260 |
| deepseek-coder:6.7b | gold_location - direct | exact_match_line_trim | 10 | 0.000 | 0.000 | 0.000 |
| deepseek-coder:6.7b | gold_location - direct | location_overlap_f1 | 10 | -0.017 | -0.147 | 0.106 |
| macro_average | direct - no_review | exact_match_line_trim | 10 | 0.050 | 0.000 | 0.150 |
| macro_average | direct - no_review | location_overlap_f1 | 10 | 0.066 | -0.068 | 0.250 |
| macro_average | gold_location - direct | exact_match_line_trim | 10 | -0.050 | -0.150 | 0.000 |
| macro_average | gold_location - direct | location_overlap_f1 | 10 | 0.179 | 0.020 | 0.344 |

## Paper-Ready Summary Table
| model | no_review_exact | direct_exact | gold_location_exact | no_review_loc_f1 | direct_loc_f1 | gold_location_loc_f1 | direct_minus_no_review_exact | direct_minus_no_review_loc_f1 | gold_location_minus_direct_exact | gold_location_minus_direct_loc_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | 0.000 | 0.100 | 0.000 | 0.460 | 0.539 | 0.913 | 0.100 | 0.079 | -0.100 | 0.374 |
| deepseek-coder:6.7b | 0.000 | 0.000 | 0.000 | 0.447 | 0.500 | 0.483 | 0.000 | 0.053 | 0.000 | -0.017 |
| macro_average | 0.000 | 0.050 | 0.000 | 0.454 | 0.520 | 0.698 | 0.050 | 0.066 | -0.050 | 0.179 |

## Integrity
| model | condition | expected_count | output_count | missing_example_id_count | duplicate_example_id_count | generation_error_count | extraction_failure_count | evaluation_failure_count | valid_evaluation_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| qwen2.5-coder:7b | direct | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| qwen2.5-coder:7b | gold_location | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| deepseek-coder:6.7b | no_review | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| deepseek-coder:6.7b | direct | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| deepseek-coder:6.7b | gold_location | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |

## Research Message
Review comments and gold location information can change model repair behavior, but improvements in location overlap do not necessarily convert into exact repair success. The tables above therefore keep model-specific condition comparisons and gain estimates together.
