# Multi-Model Review-to-Repair Seed42

## Run
- Started UTC: 2026-05-11T02:56:15.618327+00:00
- Completed UTC: 2026-05-11T03:17:54.596729+00:00
- Data: data/processed/crn_pilot100.jsonl (100 examples from the seed=42 CodeReview-New pilot subset)
- Conditions: no_review, direct, gold_location
- Metrics: exact_match_line_trim, location_overlap_f1
- Models: qwen2.5-coder:7b, deepseek-coder:6.7b, codegemma:7b
- Installed Ollama models observed: codegemma:7b, deepseek-coder:6.7b, qwen2.5-coder:7b
- Output root: /cephfs/lab/2022810001_강명묵/results/multi_model_r2r_seed42_pilot100_gpu0
- Workers per model/condition: 1
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
- Smoke test: `python scripts/run_multi_model_r2r.py --limit 10 --output-root results/multi_model_r2r_seed42_smoke10 --resume --continue-on-error --num-predict 1024`
- Full run after approval: `python scripts/run_multi_model_r2r.py --output-root results/multi_model_r2r_seed42 --resume --continue-on-error --num-predict 1024`

## Generation Accounting
| model | condition | selected_examples | existing_rows_reused | legacy_predictions_reused | backend_generations | errors |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 100 | 100 | 0 | 0 | 0 |
| qwen2.5-coder:7b | direct | 100 | 100 | 0 | 0 | 0 |
| qwen2.5-coder:7b | gold_location | 100 | 100 | 0 | 0 | 0 |
| deepseek-coder:6.7b | no_review | 100 | 100 | 0 | 0 | 0 |
| deepseek-coder:6.7b | direct | 100 | 65 | 0 | 35 | 0 |
| deepseek-coder:6.7b | gold_location | 100 | 0 | 0 | 100 | 0 |
| codegemma:7b | no_review | 100 | 0 | 0 | 100 | 0 |
| codegemma:7b | direct | 100 | 0 | 0 | 100 | 0 |
| codegemma:7b | gold_location | 100 | 0 | 0 | 100 | 0 |

## Metrics By Model And Condition
| model | condition | n_valid | exact_match_line_trim | location_overlap_f1 |
| --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 44 | 0.023 | 0.434 |
| qwen2.5-coder:7b | direct | 20 | 0.100 | 0.669 |
| qwen2.5-coder:7b | gold_location | 45 | 0.044 | 0.832 |
| deepseek-coder:6.7b | no_review | 199 | 0.000 | 0.553 |
| deepseek-coder:6.7b | direct | 164 | 0.012 | 0.536 |
| deepseek-coder:6.7b | gold_location | 100 | 0.000 | 0.568 |
| codegemma:7b | no_review | 100 | 0.000 | 0.462 |
| codegemma:7b | direct | 100 | 0.000 | 0.461 |
| codegemma:7b | gold_location | 100 | 0.000 | 0.461 |

## Gains With Paired Bootstrap 95% CI
| model | comparison | metric | paired_n | gain | ci95_low | ci95_high |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | direct - no_review | exact_match_line_trim | 4 | 0.000 | 0.000 | 0.000 |
| qwen2.5-coder:7b | direct - no_review | location_overlap_f1 | 4 | -0.016 | -0.167 | 0.120 |
| qwen2.5-coder:7b | gold_location - direct | exact_match_line_trim | 6 | 0.000 | 0.000 | 0.000 |
| qwen2.5-coder:7b | gold_location - direct | location_overlap_f1 | 6 | 0.353 | -0.007 | 0.733 |
| deepseek-coder:6.7b | direct - no_review | exact_match_line_trim | 100 | 0.010 | 0.000 | 0.030 |
| deepseek-coder:6.7b | direct - no_review | location_overlap_f1 | 100 | -0.024 | -0.074 | 0.021 |
| deepseek-coder:6.7b | gold_location - direct | exact_match_line_trim | 100 | -0.010 | -0.030 | 0.000 |
| deepseek-coder:6.7b | gold_location - direct | location_overlap_f1 | 100 | 0.038 | -0.002 | 0.079 |
| codegemma:7b | direct - no_review | exact_match_line_trim | 100 | 0.000 | 0.000 | 0.000 |
| codegemma:7b | direct - no_review | location_overlap_f1 | 100 | -0.001 | -0.002 | 0.000 |
| codegemma:7b | gold_location - direct | exact_match_line_trim | 100 | 0.000 | 0.000 | 0.000 |
| codegemma:7b | gold_location - direct | location_overlap_f1 | 100 | 0.000 | 0.000 | 0.001 |
| macro_average | direct - no_review | exact_match_line_trim | 4 | 0.003 | 0.000 | 0.010 |
| macro_average | direct - no_review | location_overlap_f1 | 4 | -0.013 | -0.062 | 0.031 |
| macro_average | gold_location - direct | exact_match_line_trim | 6 | -0.003 | -0.010 | 0.000 |
| macro_average | gold_location - direct | location_overlap_f1 | 6 | 0.131 | 0.007 | 0.259 |

## Paper-Ready Summary Table
| model | no_review_exact | direct_exact | gold_location_exact | no_review_loc_f1 | direct_loc_f1 | gold_location_loc_f1 | direct_minus_no_review_exact | direct_minus_no_review_loc_f1 | gold_location_minus_direct_exact | gold_location_minus_direct_loc_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | 0.023 | 0.100 | 0.044 | 0.434 | 0.669 | 0.832 | 0.000 | -0.016 | 0.000 | 0.353 |
| deepseek-coder:6.7b | 0.000 | 0.012 | 0.000 | 0.553 | 0.536 | 0.568 | 0.010 | -0.024 | -0.010 | 0.038 |
| codegemma:7b | 0.000 | 0.000 | 0.000 | 0.462 | 0.461 | 0.461 | 0.000 | -0.001 | 0.000 | 0.000 |
| macro_average | 0.008 | 0.037 | 0.015 | 0.483 | 0.556 | 0.620 | 0.003 | -0.013 | -0.003 | 0.131 |

## Integrity
| model | condition | expected_count | output_count | missing_example_id_count | duplicate_example_id_count | generation_error_count | extraction_failure_count | evaluation_failure_count | valid_evaluation_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 100 | 123 | 0 | 23 | 79 | 79 | 0 | 44 |
| qwen2.5-coder:7b | direct | 100 | 198 | 0 | 98 | 178 | 178 | 0 | 20 |
| qwen2.5-coder:7b | gold_location | 100 | 200 | 0 | 100 | 155 | 155 | 0 | 45 |
| deepseek-coder:6.7b | no_review | 100 | 199 | 0 | 99 | 0 | 0 | 0 | 199 |
| deepseek-coder:6.7b | direct | 100 | 164 | 0 | 64 | 0 | 0 | 0 | 164 |
| deepseek-coder:6.7b | gold_location | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 100 |
| codegemma:7b | no_review | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 100 |
| codegemma:7b | direct | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 100 |
| codegemma:7b | gold_location | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 100 |

## Output Length And Truncation Diagnostics
| model | condition | n_output | raw_len_min | raw_len_mean | raw_len_median | raw_len_max | extracted_len_min | extracted_len_mean | extracted_len_median | extracted_len_max | empty_raw_count | empty_extracted_count | very_short_extracted_count | unclosed_code_fence_count | near_num_predict_char_risk_count | suspicious_case_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 123 | 0 | 151.016 | 0.000 | 1737 | 0 | 145.992 | 0.000 | 1671 | 79 | 79 | 1 | 0 | 0 | 80 |
| qwen2.5-coder:7b | direct | 198 | 0 | 33.192 | 0.000 | 514 | 0 | 32.040 | 0.000 | 504 | 178 | 178 | 0 | 0 | 0 | 178 |
| qwen2.5-coder:7b | gold_location | 200 | 0 | 87.200 | 0.000 | 854 | 0 | 75.905 | 0.000 | 703 | 155 | 155 | 0 | 0 | 0 | 155 |
| deepseek-coder:6.7b | no_review | 199 | 595 | 2341.573 | 2029.000 | 4687 | 62 | 539.809 | 465.000 | 1661 | 0 | 0 | 0 | 39 | 42 | 70 |
| deepseek-coder:6.7b | direct | 164 | 703 | 2989.659 | 3211.500 | 5098 | 45 | 546.829 | 434.000 | 2081 | 0 | 0 | 0 | 52 | 51 | 86 |
| deepseek-coder:6.7b | gold_location | 100 | 973 | 2955.400 | 3175.000 | 4597 | 86 | 531.050 | 435.000 | 1881 | 0 | 0 | 0 | 29 | 21 | 45 |
| codegemma:7b | no_review | 100 | 4 | 828.820 | 339.500 | 5270 | 4 | 812.960 | 334.000 | 5270 | 0 | 0 | 2 | 27 | 9 | 36 |
| codegemma:7b | direct | 100 | 4 | 534.930 | 235.000 | 5671 | 4 | 534.920 | 235.000 | 5671 | 0 | 0 | 5 | 9 | 5 | 17 |
| codegemma:7b | gold_location | 100 | 4 | 464.580 | 150.000 | 4677 | 4 | 464.530 | 150.000 | 4677 | 0 | 0 | 10 | 2 | 5 | 17 |

## Truncation Or Empty-Output Flags
- The cases below are heuristic flags based on empty outputs, empty or very short extracted code, unclosed Markdown fences, or raw outputs whose character length is near the generation cap.
| model | condition | example_id | raw_output_len_chars | extracted_code_len_chars | flags |
| --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | crn-011737 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-006232 | 11 | 10 | very_short_extracted_code |
| qwen2.5-coder:7b | no_review | crn-011391 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-002686 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-004518 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-003358 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-008823 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-006784 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-013905 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-002938 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-000862 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-006421 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-000801 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-009395 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-004543 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-006291 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-000798 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-000744 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-001241 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-009360 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-005359 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-002326 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-005332 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-009549 | 0 | 0 | empty_raw_output;empty_extracted_code |
| qwen2.5-coder:7b | no_review | crn-009507 | 0 | 0 | empty_raw_output;empty_extracted_code |
- Additional flagged cases omitted from this Markdown view: 659

## Research Message
Review comments and gold location information can change model repair behavior, but improvements in location overlap do not necessarily convert into exact repair success. The tables above therefore keep model-specific condition comparisons and gain estimates together.
