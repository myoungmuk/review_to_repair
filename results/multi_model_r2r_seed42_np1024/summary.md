# Multi-Model Review-to-Repair Seed42

## Run
- Started UTC: 2026-04-27T11:07:15.160830+00:00
- Completed UTC: 2026-04-27T11:07:36.939078+00:00
- Data: data/processed/crn_pilot100.jsonl (100 examples from the seed=42 CodeReview-New pilot subset)
- Conditions: no_review, direct, gold_location
- Metrics: exact_match_line_trim, location_overlap_f1
- Models: qwen2.5-coder:7b, deepseek-coder:6.7b, codegemma:7b
- Installed Ollama models observed: codegemma:7b, starcoder2:7b, deepseek-coder:6.7b, qwen2.5-coder:3b, qwen2.5-coder:7b, devstral:24b
- Output root: /home/selab/kmm/review_to_repair_crn/results/multi_model_r2r_seed42_np1024
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
| deepseek-coder:6.7b | direct | 100 | 100 | 0 | 0 | 0 |
| deepseek-coder:6.7b | gold_location | 100 | 100 | 0 | 0 | 0 |
| codegemma:7b | no_review | 100 | 100 | 0 | 0 | 0 |
| codegemma:7b | direct | 100 | 100 | 0 | 0 | 0 |
| codegemma:7b | gold_location | 100 | 80 | 0 | 20 | 0 |

## Metrics By Model And Condition
| model | condition | n_valid | exact_match_line_trim | location_overlap_f1 |
| --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 100 | 0.000 | 0.503 |
| qwen2.5-coder:7b | direct | 100 | 0.070 | 0.567 |
| qwen2.5-coder:7b | gold_location | 100 | 0.090 | 0.748 |
| deepseek-coder:6.7b | no_review | 100 | 0.000 | 0.480 |
| deepseek-coder:6.7b | direct | 100 | 0.020 | 0.550 |
| deepseek-coder:6.7b | gold_location | 100 | 0.010 | 0.558 |
| codegemma:7b | no_review | 100 | 0.000 | 0.622 |
| codegemma:7b | direct | 100 | 0.050 | 0.689 |
| codegemma:7b | gold_location | 100 | 0.060 | 0.804 |

## Gains With Paired Bootstrap 95% CI
| model | comparison | metric | paired_n | gain | ci95_low | ci95_high |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | direct - no_review | exact_match_line_trim | 100 | 0.070 | 0.020 | 0.120 |
| qwen2.5-coder:7b | direct - no_review | location_overlap_f1 | 100 | 0.064 | -0.007 | 0.140 |
| qwen2.5-coder:7b | gold_location - direct | exact_match_line_trim | 100 | 0.020 | -0.050 | 0.090 |
| qwen2.5-coder:7b | gold_location - direct | location_overlap_f1 | 100 | 0.181 | 0.106 | 0.253 |
| deepseek-coder:6.7b | direct - no_review | exact_match_line_trim | 100 | 0.020 | 0.000 | 0.050 |
| deepseek-coder:6.7b | direct - no_review | location_overlap_f1 | 100 | 0.070 | 0.036 | 0.104 |
| deepseek-coder:6.7b | gold_location - direct | exact_match_line_trim | 100 | -0.010 | -0.030 | 0.000 |
| deepseek-coder:6.7b | gold_location - direct | location_overlap_f1 | 100 | 0.008 | -0.029 | 0.046 |
| codegemma:7b | direct - no_review | exact_match_line_trim | 100 | 0.050 | 0.010 | 0.090 |
| codegemma:7b | direct - no_review | location_overlap_f1 | 100 | 0.067 | -0.006 | 0.136 |
| codegemma:7b | gold_location - direct | exact_match_line_trim | 100 | 0.010 | -0.040 | 0.060 |
| codegemma:7b | gold_location - direct | location_overlap_f1 | 100 | 0.116 | 0.053 | 0.177 |
| macro_average | direct - no_review | exact_match_line_trim | 100 | 0.047 | 0.023 | 0.073 |
| macro_average | direct - no_review | location_overlap_f1 | 100 | 0.067 | 0.026 | 0.109 |
| macro_average | gold_location - direct | exact_match_line_trim | 100 | 0.007 | -0.027 | 0.043 |
| macro_average | gold_location - direct | location_overlap_f1 | 100 | 0.102 | 0.064 | 0.139 |

## Paper-Ready Summary Table
| model | no_review_exact | direct_exact | gold_location_exact | no_review_loc_f1 | direct_loc_f1 | gold_location_loc_f1 | direct_minus_no_review_exact | direct_minus_no_review_loc_f1 | gold_location_minus_direct_exact | gold_location_minus_direct_loc_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | 0.000 | 0.070 | 0.090 | 0.503 | 0.567 | 0.748 | 0.070 | 0.064 | 0.020 | 0.181 |
| deepseek-coder:6.7b | 0.000 | 0.020 | 0.010 | 0.480 | 0.550 | 0.558 | 0.020 | 0.070 | -0.010 | 0.008 |
| codegemma:7b | 0.000 | 0.050 | 0.060 | 0.622 | 0.689 | 0.804 | 0.050 | 0.067 | 0.010 | 0.116 |
| macro_average | 0.000 | 0.047 | 0.053 | 0.535 | 0.602 | 0.703 | 0.047 | 0.067 | 0.007 | 0.102 |

## Integrity
| model | condition | expected_count | output_count | missing_example_id_count | duplicate_example_id_count | generation_error_count | extraction_failure_count | evaluation_failure_count | valid_evaluation_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 100 |
| qwen2.5-coder:7b | direct | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 100 |
| qwen2.5-coder:7b | gold_location | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 100 |
| deepseek-coder:6.7b | no_review | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 100 |
| deepseek-coder:6.7b | direct | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 100 |
| deepseek-coder:6.7b | gold_location | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 100 |
| codegemma:7b | no_review | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 100 |
| codegemma:7b | direct | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 100 |
| codegemma:7b | gold_location | 100 | 100 | 0 | 0 | 0 | 0 | 0 | 100 |

## Output Length And Truncation Diagnostics
| model | condition | n_output | raw_len_min | raw_len_mean | raw_len_median | raw_len_max | extracted_len_min | extracted_len_mean | extracted_len_median | extracted_len_max | empty_raw_count | empty_extracted_count | very_short_extracted_count | unclosed_code_fence_count | near_num_predict_char_risk_count | suspicious_case_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 100 | 79 | 513.520 | 414.500 | 1660 | 67 | 500.900 | 400.500 | 1649 | 0 | 0 | 0 | 0 | 0 | 0 |
| qwen2.5-coder:7b | direct | 100 | 65 | 514.440 | 432.000 | 1658 | 53 | 501.820 | 419.000 | 1647 | 0 | 0 | 0 | 0 | 0 | 0 |
| qwen2.5-coder:7b | gold_location | 100 | 63 | 506.100 | 404.000 | 1658 | 50 | 474.270 | 379.000 | 1647 | 0 | 0 | 0 | 0 | 0 | 0 |
| deepseek-coder:6.7b | no_review | 100 | 225 | 988.550 | 949.500 | 2960 | 48 | 555.090 | 547.000 | 1656 | 0 | 0 | 0 | 3 | 0 | 3 |
| deepseek-coder:6.7b | direct | 100 | 62 | 491.940 | 401.000 | 1718 | 49 | 452.320 | 387.000 | 1704 | 0 | 0 | 0 | 0 | 0 | 0 |
| deepseek-coder:6.7b | gold_location | 100 | 63 | 503.960 | 446.500 | 1745 | 49 | 468.340 | 387.000 | 1664 | 0 | 0 | 0 | 2 | 0 | 2 |
| codegemma:7b | no_review | 100 | 69 | 553.050 | 458.000 | 1672 | 57 | 540.400 | 444.500 | 1661 | 0 | 0 | 0 | 0 | 0 | 0 |
| codegemma:7b | direct | 100 | 127 | 526.640 | 427.000 | 1689 | 115 | 514.000 | 413.000 | 1678 | 0 | 0 | 0 | 0 | 0 | 0 |
| codegemma:7b | gold_location | 100 | 62 | 492.930 | 406.000 | 1680 | 49 | 478.590 | 394.500 | 1669 | 0 | 0 | 0 | 0 | 0 | 0 |

## Truncation Or Empty-Output Flags
- The cases below are heuristic flags based on empty outputs, empty or very short extracted code, unclosed Markdown fences, or raw outputs whose character length is near the generation cap.
| model | condition | example_id | raw_output_len_chars | extracted_code_len_chars | flags |
| --- | --- | --- | --- | --- | --- |
| deepseek-coder:6.7b | no_review | crn-006672 | 697 | 697 | unclosed_code_fence |
| deepseek-coder:6.7b | no_review | crn-012114 | 596 | 596 | unclosed_code_fence |
| deepseek-coder:6.7b | no_review | crn-006483 | 814 | 814 | unclosed_code_fence |
| deepseek-coder:6.7b | gold_location | crn-008823 | 216 | 216 | unclosed_code_fence |
| deepseek-coder:6.7b | gold_location | crn-009938 | 714 | 714 | unclosed_code_fence |

## Research Message
Review comments and gold location information can change model repair behavior, but improvements in location overlap do not necessarily convert into exact repair success. The tables above therefore keep model-specific condition comparisons and gain estimates together.
