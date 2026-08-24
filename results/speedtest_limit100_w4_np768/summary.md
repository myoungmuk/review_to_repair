# Multi-Model Review-to-Repair Seed42

## Run
- Started UTC: 2026-04-29T07:48:43.630706+00:00
- Completed UTC: 2026-04-29T07:54:14.514995+00:00
- Data: data/processed/crn_all.jsonl (100 examples from the seed=42 CodeReview-New pilot subset)
- Conditions: no_review, direct, gold_location
- Metrics: exact_match_line_trim, location_overlap_f1
- Models: qwen2.5-coder:7b, deepseek-coder:6.7b, codegemma:7b
- Installed Ollama models observed: codegemma:7b, starcoder2:7b, deepseek-coder:6.7b, qwen2.5-coder:3b, qwen2.5-coder:7b
- Output root: /home/selab/2026/review_to_repair_crn/results/speedtest_limit100_w4_np768
- Workers per model/condition: 4
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
- Smoke test: `python scripts/run_multi_model_r2r.py --limit 10 --output-root results/multi_model_r2r_seed42_smoke10 --resume --continue-on-error --num-predict 768 --workers 4`
- Full run after approval: `python scripts/run_multi_model_r2r.py --output-root results/multi_model_r2r_seed42 --resume --continue-on-error --num-predict 768 --workers 4`

## Generation Accounting
| model | condition | selected_examples | existing_rows_reused | legacy_predictions_reused | backend_generations | errors |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 100 | 0 | 0 | 100 | 0 |
| qwen2.5-coder:7b | direct | 100 | 0 | 0 | 100 | 0 |
| qwen2.5-coder:7b | gold_location | 100 | 0 | 0 | 100 | 0 |
| deepseek-coder:6.7b | no_review | 100 | 0 | 0 | 100 | 0 |
| deepseek-coder:6.7b | direct | 100 | 0 | 0 | 100 | 0 |
| deepseek-coder:6.7b | gold_location | 100 | 0 | 0 | 100 | 0 |
| codegemma:7b | no_review | 100 | 0 | 0 | 100 | 0 |
| codegemma:7b | direct | 100 | 0 | 0 | 100 | 0 |
| codegemma:7b | gold_location | 100 | 0 | 0 | 100 | 0 |

## Metrics By Model And Condition
| model | condition | n_valid | exact_match_line_trim | location_overlap_f1 |
| --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 100 | 0.010 | 0.395 |
| qwen2.5-coder:7b | direct | 100 | 0.090 | 0.553 |
| qwen2.5-coder:7b | gold_location | 100 | 0.030 | 0.671 |
| deepseek-coder:6.7b | no_review | 100 | 0.000 | 0.378 |
| deepseek-coder:6.7b | direct | 100 | 0.000 | 0.432 |
| deepseek-coder:6.7b | gold_location | 100 | 0.000 | 0.470 |
| codegemma:7b | no_review | 100 | 0.010 | 0.623 |
| codegemma:7b | direct | 100 | 0.080 | 0.659 |
| codegemma:7b | gold_location | 100 | 0.030 | 0.727 |

## Gains With Paired Bootstrap 95% CI
| model | comparison | metric | paired_n | gain | ci95_low | ci95_high |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | direct - no_review | exact_match_line_trim | 100 | 0.080 | 0.030 | 0.130 |
| qwen2.5-coder:7b | direct - no_review | location_overlap_f1 | 100 | 0.157 | 0.092 | 0.217 |
| qwen2.5-coder:7b | gold_location - direct | exact_match_line_trim | 100 | -0.060 | -0.110 | -0.010 |
| qwen2.5-coder:7b | gold_location - direct | location_overlap_f1 | 100 | 0.119 | 0.047 | 0.185 |
| deepseek-coder:6.7b | direct - no_review | exact_match_line_trim | 100 | 0.000 | 0.000 | 0.000 |
| deepseek-coder:6.7b | direct - no_review | location_overlap_f1 | 100 | 0.054 | 0.028 | 0.081 |
| deepseek-coder:6.7b | gold_location - direct | exact_match_line_trim | 100 | 0.000 | 0.000 | 0.000 |
| deepseek-coder:6.7b | gold_location - direct | location_overlap_f1 | 100 | 0.038 | 0.004 | 0.077 |
| codegemma:7b | direct - no_review | exact_match_line_trim | 100 | 0.070 | 0.020 | 0.130 |
| codegemma:7b | direct - no_review | location_overlap_f1 | 100 | 0.035 | -0.030 | 0.104 |
| codegemma:7b | gold_location - direct | exact_match_line_trim | 100 | -0.050 | -0.110 | 0.000 |
| codegemma:7b | gold_location - direct | location_overlap_f1 | 100 | 0.068 | 0.008 | 0.132 |
| macro_average | direct - no_review | exact_match_line_trim | 100 | 0.050 | 0.027 | 0.077 |
| macro_average | direct - no_review | location_overlap_f1 | 100 | 0.082 | 0.048 | 0.118 |
| macro_average | gold_location - direct | exact_match_line_trim | 100 | -0.037 | -0.063 | -0.010 |
| macro_average | gold_location - direct | location_overlap_f1 | 100 | 0.075 | 0.040 | 0.109 |

## Paper-Ready Summary Table
| model | no_review_exact | direct_exact | gold_location_exact | no_review_loc_f1 | direct_loc_f1 | gold_location_loc_f1 | direct_minus_no_review_exact | direct_minus_no_review_loc_f1 | gold_location_minus_direct_exact | gold_location_minus_direct_loc_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | 0.010 | 0.090 | 0.030 | 0.395 | 0.553 | 0.671 | 0.080 | 0.157 | -0.060 | 0.119 |
| deepseek-coder:6.7b | 0.000 | 0.000 | 0.000 | 0.378 | 0.432 | 0.470 | 0.000 | 0.054 | 0.000 | 0.038 |
| codegemma:7b | 0.010 | 0.080 | 0.030 | 0.623 | 0.659 | 0.727 | 0.070 | 0.035 | -0.050 | 0.068 |
| macro_average | 0.007 | 0.057 | 0.020 | 0.465 | 0.548 | 0.623 | 0.050 | 0.082 | -0.037 | 0.075 |

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
| qwen2.5-coder:7b | no_review | 100 | 62 | 402.510 | 377.500 | 1201 | 53 | 390.230 | 363.500 | 1187 | 0 | 0 | 0 | 0 | 0 | 0 |
| qwen2.5-coder:7b | direct | 100 | 56 | 428.690 | 393.500 | 1399 | 47 | 416.420 | 380.500 | 1389 | 0 | 0 | 0 | 0 | 0 | 0 |
| qwen2.5-coder:7b | gold_location | 100 | 26 | 422.810 | 389.500 | 1361 | 17 | 386.710 | 371.500 | 1351 | 0 | 0 | 1 | 0 | 0 | 1 |
| deepseek-coder:6.7b | no_review | 100 | 239 | 937.070 | 934.500 | 2238 | 70 | 467.330 | 422.500 | 1529 | 0 | 0 | 0 | 3 | 0 | 3 |
| deepseek-coder:6.7b | direct | 100 | 30 | 472.940 | 414.000 | 1390 | 12 | 410.650 | 382.000 | 1379 | 0 | 0 | 1 | 1 | 0 | 2 |
| deepseek-coder:6.7b | gold_location | 100 | 42 | 423.980 | 386.500 | 1398 | 32 | 388.510 | 347.000 | 1387 | 0 | 0 | 0 | 3 | 0 | 3 |
| codegemma:7b | no_review | 100 | 55 | 441.840 | 432.500 | 1390 | 46 | 429.530 | 418.500 | 1380 | 0 | 0 | 0 | 0 | 0 | 0 |
| codegemma:7b | direct | 100 | 56 | 437.550 | 415.000 | 1382 | 47 | 425.260 | 401.000 | 1372 | 0 | 0 | 0 | 0 | 0 | 0 |
| codegemma:7b | gold_location | 100 | 28 | 392.670 | 385.500 | 1176 | 19 | 379.130 | 370.500 | 1096 | 0 | 0 | 1 | 1 | 0 | 2 |

## Truncation Or Empty-Output Flags
- The cases below are heuristic flags based on empty outputs, empty or very short extracted code, unclosed Markdown fences, or raw outputs whose character length is near the generation cap.
| model | condition | example_id | raw_output_len_chars | extracted_code_len_chars | flags |
| --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | gold_location | crn-002590 | 26 | 17 | very_short_extracted_code |
| deepseek-coder:6.7b | no_review | crn-007371 | 671 | 671 | unclosed_code_fence |
| deepseek-coder:6.7b | no_review | crn-012630 | 812 | 812 | unclosed_code_fence |
| deepseek-coder:6.7b | no_review | crn-012612 | 667 | 667 | unclosed_code_fence |
| deepseek-coder:6.7b | direct | crn-007371 | 526 | 526 | unclosed_code_fence |
| deepseek-coder:6.7b | direct | crn-010761 | 814 | 12 | very_short_extracted_code |
| deepseek-coder:6.7b | gold_location | crn-010297 | 358 | 358 | unclosed_code_fence |
| deepseek-coder:6.7b | gold_location | crn-004693 | 404 | 404 | unclosed_code_fence |
| deepseek-coder:6.7b | gold_location | crn-012612 | 510 | 510 | unclosed_code_fence |
| codegemma:7b | gold_location | crn-000985 | 484 | 483 | unclosed_code_fence |
| codegemma:7b | gold_location | crn-002590 | 28 | 19 | very_short_extracted_code |

## Research Message
Review comments and gold location information can change model repair behavior, but improvements in location overlap do not necessarily convert into exact repair success. The tables above therefore keep model-specific condition comparisons and gain estimates together.
