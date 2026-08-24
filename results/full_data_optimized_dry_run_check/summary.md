# Multi-Model Review-to-Repair Seed42

## Run
- Started UTC: 2026-04-29T07:08:52.289912+00:00
- Completed UTC: 2026-04-29T07:08:53.008413+00:00
- Data: data/processed/crn_all.jsonl (2 examples from the seed=42 CodeReview-New pilot subset)
- Conditions: no_review, direct, gold_location
- Metrics: exact_match_line_trim, location_overlap_f1
- Models: qwen2.5-coder:7b, deepseek-coder:6.7b, codegemma:7b
- Installed Ollama models observed: (not checked)
- Output root: /home/selab/2026/review_to_repair_crn/results/full_data_optimized_dry_run_check
- Workers per model/condition: 2
- Legacy prediction reuse: disabled

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
- Smoke test: `python scripts/run_multi_model_r2r.py --limit 10 --output-root results/multi_model_r2r_seed42_smoke10 --resume --continue-on-error --num-predict 1024 --workers 2`
- Full run after approval: `python scripts/run_multi_model_r2r.py --output-root results/multi_model_r2r_seed42 --resume --continue-on-error --num-predict 1024 --workers 2`

## Generation Accounting
| model | condition | selected_examples | existing_rows_reused | legacy_predictions_reused | backend_generations | errors |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 2 | 0 | 0 | 2 | 0 |
| qwen2.5-coder:7b | direct | 2 | 0 | 0 | 2 | 0 |
| qwen2.5-coder:7b | gold_location | 2 | 0 | 0 | 2 | 0 |
| deepseek-coder:6.7b | no_review | 2 | 0 | 0 | 2 | 0 |
| deepseek-coder:6.7b | direct | 2 | 0 | 0 | 2 | 0 |
| deepseek-coder:6.7b | gold_location | 2 | 0 | 0 | 2 | 0 |
| codegemma:7b | no_review | 2 | 0 | 0 | 2 | 0 |
| codegemma:7b | direct | 2 | 0 | 0 | 2 | 0 |
| codegemma:7b | gold_location | 2 | 0 | 0 | 2 | 0 |

## Metrics By Model And Condition
| model | condition | n_valid | exact_match_line_trim | location_overlap_f1 |
| --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 2 | 0.000 | 0.333 |
| qwen2.5-coder:7b | direct | 2 | 0.000 | 0.333 |
| qwen2.5-coder:7b | gold_location | 2 | 0.000 | 0.333 |
| deepseek-coder:6.7b | no_review | 2 | 0.000 | 0.333 |
| deepseek-coder:6.7b | direct | 2 | 0.000 | 0.333 |
| deepseek-coder:6.7b | gold_location | 2 | 0.000 | 0.333 |
| codegemma:7b | no_review | 2 | 0.000 | 0.333 |
| codegemma:7b | direct | 2 | 0.000 | 0.333 |
| codegemma:7b | gold_location | 2 | 0.000 | 0.333 |

## Gains With Paired Bootstrap 95% CI
| model | comparison | metric | paired_n | gain | ci95_low | ci95_high |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | direct - no_review | exact_match_line_trim | 2 | 0.000 | 0.000 | 0.000 |
| qwen2.5-coder:7b | direct - no_review | location_overlap_f1 | 2 | 0.000 | 0.000 | 0.000 |
| qwen2.5-coder:7b | gold_location - direct | exact_match_line_trim | 2 | 0.000 | 0.000 | 0.000 |
| qwen2.5-coder:7b | gold_location - direct | location_overlap_f1 | 2 | 0.000 | 0.000 | 0.000 |
| deepseek-coder:6.7b | direct - no_review | exact_match_line_trim | 2 | 0.000 | 0.000 | 0.000 |
| deepseek-coder:6.7b | direct - no_review | location_overlap_f1 | 2 | 0.000 | 0.000 | 0.000 |
| deepseek-coder:6.7b | gold_location - direct | exact_match_line_trim | 2 | 0.000 | 0.000 | 0.000 |
| deepseek-coder:6.7b | gold_location - direct | location_overlap_f1 | 2 | 0.000 | 0.000 | 0.000 |
| codegemma:7b | direct - no_review | exact_match_line_trim | 2 | 0.000 | 0.000 | 0.000 |
| codegemma:7b | direct - no_review | location_overlap_f1 | 2 | 0.000 | 0.000 | 0.000 |
| codegemma:7b | gold_location - direct | exact_match_line_trim | 2 | 0.000 | 0.000 | 0.000 |
| codegemma:7b | gold_location - direct | location_overlap_f1 | 2 | 0.000 | 0.000 | 0.000 |
| macro_average | direct - no_review | exact_match_line_trim | 2 | 0.000 | 0.000 | 0.000 |
| macro_average | direct - no_review | location_overlap_f1 | 2 | 0.000 | 0.000 | 0.000 |
| macro_average | gold_location - direct | exact_match_line_trim | 2 | 0.000 | 0.000 | 0.000 |
| macro_average | gold_location - direct | location_overlap_f1 | 2 | 0.000 | 0.000 | 0.000 |

## Paper-Ready Summary Table
| model | no_review_exact | direct_exact | gold_location_exact | no_review_loc_f1 | direct_loc_f1 | gold_location_loc_f1 | direct_minus_no_review_exact | direct_minus_no_review_loc_f1 | gold_location_minus_direct_exact | gold_location_minus_direct_loc_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | 0.000 | 0.000 | 0.000 | 0.333 | 0.333 | 0.333 | 0.000 | 0.000 | 0.000 | 0.000 |
| deepseek-coder:6.7b | 0.000 | 0.000 | 0.000 | 0.333 | 0.333 | 0.333 | 0.000 | 0.000 | 0.000 | 0.000 |
| codegemma:7b | 0.000 | 0.000 | 0.000 | 0.333 | 0.333 | 0.333 | 0.000 | 0.000 | 0.000 | 0.000 |
| macro_average | 0.000 | 0.000 | 0.000 | 0.333 | 0.333 | 0.333 | 0.000 | 0.000 | 0.000 | 0.000 |

## Integrity
| model | condition | expected_count | output_count | missing_example_id_count | duplicate_example_id_count | generation_error_count | extraction_failure_count | evaluation_failure_count | valid_evaluation_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| qwen2.5-coder:7b | direct | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| qwen2.5-coder:7b | gold_location | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| deepseek-coder:6.7b | no_review | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| deepseek-coder:6.7b | direct | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| deepseek-coder:6.7b | gold_location | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| codegemma:7b | no_review | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| codegemma:7b | direct | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |
| codegemma:7b | gold_location | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 2 |

## Output Length And Truncation Diagnostics
| model | condition | n_output | raw_len_min | raw_len_mean | raw_len_median | raw_len_max | extracted_len_min | extracted_len_mean | extracted_len_median | extracted_len_max | empty_raw_count | empty_extracted_count | very_short_extracted_count | unclosed_code_fence_count | near_num_predict_char_risk_count | suspicious_case_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 2 | 40 | 40.000 | 40.000 | 40 | 40 | 40.000 | 40.000 | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| qwen2.5-coder:7b | direct | 2 | 37 | 37.000 | 37.000 | 37 | 37 | 37.000 | 37.000 | 37 | 0 | 0 | 0 | 0 | 0 | 0 |
| qwen2.5-coder:7b | gold_location | 2 | 44 | 44.000 | 44.000 | 44 | 44 | 44.000 | 44.000 | 44 | 0 | 0 | 0 | 0 | 0 | 0 |
| deepseek-coder:6.7b | no_review | 2 | 40 | 40.000 | 40.000 | 40 | 40 | 40.000 | 40.000 | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| deepseek-coder:6.7b | direct | 2 | 37 | 37.000 | 37.000 | 37 | 37 | 37.000 | 37.000 | 37 | 0 | 0 | 0 | 0 | 0 | 0 |
| deepseek-coder:6.7b | gold_location | 2 | 44 | 44.000 | 44.000 | 44 | 44 | 44.000 | 44.000 | 44 | 0 | 0 | 0 | 0 | 0 | 0 |
| codegemma:7b | no_review | 2 | 40 | 40.000 | 40.000 | 40 | 40 | 40.000 | 40.000 | 40 | 0 | 0 | 0 | 0 | 0 | 0 |
| codegemma:7b | direct | 2 | 37 | 37.000 | 37.000 | 37 | 37 | 37.000 | 37.000 | 37 | 0 | 0 | 0 | 0 | 0 | 0 |
| codegemma:7b | gold_location | 2 | 44 | 44.000 | 44.000 | 44 | 44 | 44.000 | 44.000 | 44 | 0 | 0 | 0 | 0 | 0 | 0 |

## Truncation Or Empty-Output Flags
- No heuristic truncation or empty-output flags were found.

## Research Message
Review comments and gold location information can change model repair behavior, but improvements in location overlap do not necessarily convert into exact repair success. The tables above therefore keep model-specific condition comparisons and gain estimates together.
