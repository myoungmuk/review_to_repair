# Multi-Model Review-to-Repair Seed42

## Run
- Started UTC: 2026-04-30T03:16:59.232009+00:00
- Completed UTC: 2026-04-30T06:50:37.059043+00:00
- Data: data/processed/crn_all.jsonl (14855 examples from the seed=42 CodeReview-New pilot subset)
- Conditions: no_review, direct, gold_location
- Metrics: exact_match_line_trim, location_overlap_f1
- Models: qwen2.5-coder:7b, deepseek-coder:6.7b
- Installed Ollama models observed: codegemma:7b, starcoder2:7b, deepseek-coder:6.7b, qwen2.5-coder:3b, qwen2.5-coder:7b
- Output root: /home/selab/2026/review_to_repair_crn/results/multi_model_r2r_all_seed42_full_w6_np512_20260429
- Workers per model/condition: 6
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
- Smoke test: `python scripts/run_multi_model_r2r.py --limit 10 --output-root results/multi_model_r2r_seed42_smoke10 --resume --continue-on-error --num-predict 512 --workers 6`
- Full run after approval: `python scripts/run_multi_model_r2r.py --output-root results/multi_model_r2r_seed42 --resume --continue-on-error --num-predict 512 --workers 6`

## Generation Accounting
| model | condition | selected_examples | existing_rows_reused | legacy_predictions_reused | backend_generations | errors |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 14855 | 14855 | 0 | 0 | 0 |
| qwen2.5-coder:7b | direct | 14855 | 14855 | 0 | 0 | 0 |
| qwen2.5-coder:7b | gold_location | 14855 | 14855 | 0 | 0 | 0 |
| deepseek-coder:6.7b | no_review | 14855 | 6872 | 0 | 7983 | 0 |
| deepseek-coder:6.7b | direct | 14855 | 0 | 0 | 14855 | 0 |
| deepseek-coder:6.7b | gold_location | 14855 | 0 | 0 | 14855 | 0 |

## Metrics By Model And Condition
| model | condition | n_valid | exact_match_line_trim | location_overlap_f1 |
| --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 14855 | 0.006 | 0.381 |
| qwen2.5-coder:7b | direct | 14855 | 0.091 | 0.531 |
| qwen2.5-coder:7b | gold_location | 14855 | 0.067 | 0.697 |
| deepseek-coder:6.7b | no_review | 14855 | 0.000 | 0.345 |
| deepseek-coder:6.7b | direct | 14855 | 0.007 | 0.407 |
| deepseek-coder:6.7b | gold_location | 14855 | 0.006 | 0.452 |

## Gains With Paired Bootstrap 95% CI
| model | comparison | metric | paired_n | gain | ci95_low | ci95_high |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | direct - no_review | exact_match_line_trim | 14855 | 0.084 | 0.080 | 0.089 |
| qwen2.5-coder:7b | direct - no_review | location_overlap_f1 | 14855 | 0.151 | 0.145 | 0.157 |
| qwen2.5-coder:7b | gold_location - direct | exact_match_line_trim | 14855 | -0.024 | -0.029 | -0.019 |
| qwen2.5-coder:7b | gold_location - direct | location_overlap_f1 | 14855 | 0.166 | 0.160 | 0.172 |
| deepseek-coder:6.7b | direct - no_review | exact_match_line_trim | 14855 | 0.007 | 0.006 | 0.008 |
| deepseek-coder:6.7b | direct - no_review | location_overlap_f1 | 14855 | 0.062 | 0.059 | 0.065 |
| deepseek-coder:6.7b | gold_location - direct | exact_match_line_trim | 14855 | -0.001 | -0.003 | 0.001 |
| deepseek-coder:6.7b | gold_location - direct | location_overlap_f1 | 14855 | 0.045 | 0.041 | 0.048 |
| macro_average | direct - no_review | exact_match_line_trim | 14855 | 0.046 | 0.043 | 0.048 |
| macro_average | direct - no_review | location_overlap_f1 | 14855 | 0.106 | 0.103 | 0.110 |
| macro_average | gold_location - direct | exact_match_line_trim | 14855 | -0.012 | -0.015 | -0.010 |
| macro_average | gold_location - direct | location_overlap_f1 | 14855 | 0.105 | 0.102 | 0.109 |

## Paper-Ready Summary Table
| model | no_review_exact | direct_exact | gold_location_exact | no_review_loc_f1 | direct_loc_f1 | gold_location_loc_f1 | direct_minus_no_review_exact | direct_minus_no_review_loc_f1 | gold_location_minus_direct_exact | gold_location_minus_direct_loc_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | 0.006 | 0.091 | 0.067 | 0.381 | 0.531 | 0.697 | 0.084 | 0.151 | -0.024 | 0.166 |
| deepseek-coder:6.7b | 0.000 | 0.007 | 0.006 | 0.345 | 0.407 | 0.452 | 0.007 | 0.062 | -0.001 | 0.045 |
| macro_average | 0.003 | 0.049 | 0.036 | 0.363 | 0.469 | 0.575 | 0.046 | 0.106 | -0.012 | 0.105 |

## Integrity
| model | condition | expected_count | output_count | missing_example_id_count | duplicate_example_id_count | generation_error_count | extraction_failure_count | evaluation_failure_count | valid_evaluation_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 14855 | 14855 | 0 | 0 | 0 | 0 | 0 | 14855 |
| qwen2.5-coder:7b | direct | 14855 | 14855 | 0 | 0 | 0 | 0 | 0 | 14855 |
| qwen2.5-coder:7b | gold_location | 14855 | 14855 | 0 | 0 | 0 | 0 | 0 | 14855 |
| deepseek-coder:6.7b | no_review | 14855 | 14855 | 0 | 0 | 0 | 0 | 0 | 14855 |
| deepseek-coder:6.7b | direct | 14855 | 14855 | 0 | 0 | 0 | 0 | 0 | 14855 |
| deepseek-coder:6.7b | gold_location | 14855 | 14855 | 0 | 0 | 0 | 0 | 0 | 14855 |

## Output Length And Truncation Diagnostics
| model | condition | n_output | raw_len_min | raw_len_mean | raw_len_median | raw_len_max | extracted_len_min | extracted_len_mean | extracted_len_median | extracted_len_max | empty_raw_count | empty_extracted_count | very_short_extracted_count | unclosed_code_fence_count | near_num_predict_char_risk_count | suspicious_case_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 14855 | 15 | 402.319 | 365.000 | 1846 | 3 | 389.558 | 352.000 | 1846 | 0 | 0 | 8 | 29 | 2 | 37 |
| qwen2.5-coder:7b | direct | 14855 | 25 | 416.213 | 380.000 | 1834 | 12 | 403.370 | 367.000 | 1824 | 0 | 0 | 1 | 31 | 1 | 33 |
| qwen2.5-coder:7b | gold_location | 14855 | 26 | 423.833 | 392.000 | 2173 | 17 | 386.886 | 351.000 | 2172 | 0 | 0 | 5 | 31 | 4 | 38 |
| deepseek-coder:6.7b | no_review | 14855 | 61 | 883.794 | 863.000 | 2334 | 1 | 445.101 | 393.000 | 2334 | 0 | 0 | 3 | 242 | 280 | 447 |
| deepseek-coder:6.7b | direct | 14855 | 23 | 448.653 | 392.000 | 2094 | 12 | 390.562 | 352.000 | 1800 | 0 | 0 | 9 | 123 | 12 | 143 |
| deepseek-coder:6.7b | gold_location | 14855 | 25 | 416.825 | 379.000 | 1917 | 12 | 382.762 | 349.000 | 1867 | 0 | 0 | 9 | 189 | 2 | 200 |

## Truncation Or Empty-Output Flags
- The cases below are heuristic flags based on empty outputs, empty or very short extracted code, unclosed Markdown fences, or raw outputs whose character length is near the generation cap.
| model | condition | example_id | raw_output_len_chars | extracted_code_len_chars | flags |
| --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | crn-006057 | 704 | 704 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-010721 | 28 | 14 | very_short_extracted_code |
| qwen2.5-coder:7b | no_review | crn-008584 | 24 | 14 | very_short_extracted_code |
| qwen2.5-coder:7b | no_review | crn-001518 | 288 | 270 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-004812 | 15 | 3 | very_short_extracted_code |
| qwen2.5-coder:7b | no_review | crn-002282 | 268 | 232 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-012164 | 31 | 17 | very_short_extracted_code |
| qwen2.5-coder:7b | no_review | crn-006105 | 1462 | 1461 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-014606 | 429 | 429 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-011998 | 1846 | 1846 | unclosed_code_fence;near_num_predict_char_risk |
| qwen2.5-coder:7b | no_review | crn-002283 | 268 | 232 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-006911 | 265 | 265 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-013319 | 1097 | 1097 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-006104 | 1462 | 1461 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-007541 | 29 | 15 | very_short_extracted_code |
| qwen2.5-coder:7b | no_review | crn-001561 | 30 | 17 | very_short_extracted_code |
| qwen2.5-coder:7b | no_review | crn-001807 | 444 | 444 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-004177 | 1727 | 1727 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-004181 | 135 | 135 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-009238 | 22 | 12 | very_short_extracted_code |
| qwen2.5-coder:7b | no_review | crn-012722 | 185 | 185 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-003992 | 426 | 426 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-002350 | 342 | 326 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-014770 | 387 | 370 | unclosed_code_fence |
| qwen2.5-coder:7b | no_review | crn-011997 | 1846 | 1846 | unclosed_code_fence;near_num_predict_char_risk |
- Additional flagged cases omitted from this Markdown view: 873

## Research Message
Review comments and gold location information can change model repair behavior, but improvements in location overlap do not necessarily convert into exact repair success. The tables above therefore keep model-specific condition comparisons and gain estimates together.
