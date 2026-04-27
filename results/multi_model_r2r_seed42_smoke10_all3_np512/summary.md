# Multi-Model Review-to-Repair Seed42

## Run
- Started UTC: 2026-04-26T22:30:18.176667+00:00
- Completed UTC: 2026-04-26T22:30:18.267551+00:00
- Data: data/processed/crn_pilot100.jsonl (10 examples from the seed=42 CodeReview-New pilot subset)
- Conditions: no_review, direct, gold_location
- Metrics: exact_match_line_trim, location_overlap_f1
- Models: qwen2.5-coder:7b, deepseek-coder:6.7b, codegemma:7b
- Installed Ollama models observed: codegemma:7b, starcoder2:7b, deepseek-coder:6.7b, qwen2.5-coder:3b, qwen2.5-coder:7b
- Output root: C:\Users\myoun\Desktop\review_to_repair_crn\results\multi_model_r2r_seed42_smoke10_all3_np512
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
- Smoke test: `python scripts/run_multi_model_r2r.py --limit 10 --output-root results/multi_model_r2r_seed42_smoke10 --resume --continue-on-error --num-predict 512`
- Full run after approval: `python scripts/run_multi_model_r2r.py --output-root results/multi_model_r2r_seed42 --resume --continue-on-error --num-predict 512`

## Generation Accounting
| model | condition | selected_examples | existing_rows_reused | legacy_predictions_reused | backend_generations | errors |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 10 | 10 | 0 | 0 | 0 |
| qwen2.5-coder:7b | direct | 10 | 10 | 0 | 0 | 0 |
| qwen2.5-coder:7b | gold_location | 10 | 10 | 0 | 0 | 0 |
| deepseek-coder:6.7b | no_review | 10 | 10 | 0 | 0 | 0 |
| deepseek-coder:6.7b | direct | 10 | 10 | 0 | 0 | 0 |
| deepseek-coder:6.7b | gold_location | 10 | 10 | 0 | 0 | 0 |
| codegemma:7b | no_review | 10 | 10 | 0 | 0 | 0 |
| codegemma:7b | direct | 10 | 10 | 0 | 0 | 0 |
| codegemma:7b | gold_location | 10 | 10 | 0 | 0 | 0 |

## Metrics By Model And Condition
| model | condition | n_valid | exact_match_line_trim | location_overlap_f1 |
| --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 10 | 0.000 | 0.460 |
| qwen2.5-coder:7b | direct | 10 | 0.100 | 0.539 |
| qwen2.5-coder:7b | gold_location | 10 | 0.000 | 0.913 |
| deepseek-coder:6.7b | no_review | 10 | 0.000 | 0.439 |
| deepseek-coder:6.7b | direct | 10 | 0.000 | 0.500 |
| deepseek-coder:6.7b | gold_location | 10 | 0.000 | 0.481 |
| codegemma:7b | no_review | 10 | 0.000 | 0.783 |
| codegemma:7b | direct | 10 | 0.100 | 0.641 |
| codegemma:7b | gold_location | 10 | 0.000 | 0.867 |

## Gains With Paired Bootstrap 95% CI
| model | comparison | metric | paired_n | gain | ci95_low | ci95_high |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | direct - no_review | exact_match_line_trim | 10 | 0.100 | 0.000 | 0.300 |
| qwen2.5-coder:7b | direct - no_review | location_overlap_f1 | 10 | 0.079 | -0.140 | 0.308 |
| qwen2.5-coder:7b | gold_location - direct | exact_match_line_trim | 10 | -0.100 | -0.300 | 0.000 |
| qwen2.5-coder:7b | gold_location - direct | location_overlap_f1 | 10 | 0.374 | 0.163 | 0.615 |
| deepseek-coder:6.7b | direct - no_review | exact_match_line_trim | 10 | 0.000 | 0.000 | 0.000 |
| deepseek-coder:6.7b | direct - no_review | location_overlap_f1 | 10 | 0.061 | -0.093 | 0.260 |
| deepseek-coder:6.7b | gold_location - direct | exact_match_line_trim | 10 | 0.000 | 0.000 | 0.000 |
| deepseek-coder:6.7b | gold_location - direct | location_overlap_f1 | 10 | -0.019 | -0.153 | 0.106 |
| codegemma:7b | direct - no_review | exact_match_line_trim | 10 | 0.100 | 0.000 | 0.300 |
| codegemma:7b | direct - no_review | location_overlap_f1 | 10 | -0.142 | -0.444 | 0.170 |
| codegemma:7b | gold_location - direct | exact_match_line_trim | 10 | -0.100 | -0.300 | 0.000 |
| codegemma:7b | gold_location - direct | location_overlap_f1 | 10 | 0.226 | -0.056 | 0.507 |
| macro_average | direct - no_review | exact_match_line_trim | 10 | 0.067 | 0.000 | 0.200 |
| macro_average | direct - no_review | location_overlap_f1 | 10 | -0.000 | -0.162 | 0.171 |
| macro_average | gold_location - direct | exact_match_line_trim | 10 | -0.067 | -0.200 | 0.000 |
| macro_average | gold_location - direct | location_overlap_f1 | 10 | 0.194 | 0.032 | 0.370 |

## Paper-Ready Summary Table
| model | no_review_exact | direct_exact | gold_location_exact | no_review_loc_f1 | direct_loc_f1 | gold_location_loc_f1 | direct_minus_no_review_exact | direct_minus_no_review_loc_f1 | gold_location_minus_direct_exact | gold_location_minus_direct_loc_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | 0.000 | 0.100 | 0.000 | 0.460 | 0.539 | 0.913 | 0.100 | 0.079 | -0.100 | 0.374 |
| deepseek-coder:6.7b | 0.000 | 0.000 | 0.000 | 0.439 | 0.500 | 0.481 | 0.000 | 0.061 | 0.000 | -0.019 |
| codegemma:7b | 0.000 | 0.100 | 0.000 | 0.783 | 0.641 | 0.867 | 0.100 | -0.142 | -0.100 | 0.226 |
| macro_average | 0.000 | 0.067 | 0.000 | 0.561 | 0.560 | 0.754 | 0.067 | -0.000 | -0.067 | 0.194 |

## Integrity
| model | condition | expected_count | output_count | missing_example_id_count | duplicate_example_id_count | generation_error_count | extraction_failure_count | evaluation_failure_count | valid_evaluation_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| qwen2.5-coder:7b | direct | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| qwen2.5-coder:7b | gold_location | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| deepseek-coder:6.7b | no_review | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| deepseek-coder:6.7b | direct | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| deepseek-coder:6.7b | gold_location | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| codegemma:7b | no_review | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| codegemma:7b | direct | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |
| codegemma:7b | gold_location | 10 | 10 | 0 | 0 | 0 | 0 | 0 | 10 |

## Output Length And Truncation Diagnostics
| model | condition | n_output | raw_len_min | raw_len_mean | raw_len_median | raw_len_max | extracted_len_min | extracted_len_mean | extracted_len_median | extracted_len_max | empty_raw_count | empty_extracted_count | very_short_extracted_count | unclosed_code_fence_count | near_num_predict_char_risk_count | suspicious_case_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | no_review | 10 | 262 | 554.400 | 384.500 | 1660 | 249 | 542.400 | 369.500 | 1649 | 0 | 0 | 0 | 0 | 0 | 0 |
| qwen2.5-coder:7b | direct | 10 | 210 | 539.600 | 375.000 | 1658 | 197 | 527.600 | 365.500 | 1647 | 0 | 0 | 0 | 0 | 0 | 0 |
| qwen2.5-coder:7b | gold_location | 10 | 217 | 571.700 | 420.500 | 1658 | 204 | 532.100 | 369.000 | 1647 | 0 | 0 | 0 | 0 | 0 | 0 |
| deepseek-coder:6.7b | no_review | 10 | 226 | 1003.400 | 1020.000 | 1900 | 80 | 538.400 | 376.000 | 1900 | 0 | 0 | 0 | 1 | 1 | 1 |
| deepseek-coder:6.7b | direct | 10 | 242 | 374.500 | 368.000 | 652 | 235 | 364.900 | 352.000 | 639 | 0 | 0 | 0 | 0 | 0 | 0 |
| deepseek-coder:6.7b | gold_location | 10 | 216 | 532.400 | 382.000 | 1728 | 216 | 484.300 | 335.500 | 1659 | 0 | 0 | 0 | 2 | 0 | 2 |
| codegemma:7b | no_review | 10 | 263 | 541.900 | 349.500 | 1672 | 250 | 529.900 | 338.000 | 1661 | 0 | 0 | 0 | 0 | 0 | 0 |
| codegemma:7b | direct | 10 | 176 | 558.900 | 424.500 | 1689 | 163 | 546.900 | 414.000 | 1678 | 0 | 0 | 0 | 0 | 0 | 0 |
| codegemma:7b | gold_location | 10 | 176 | 544.100 | 386.500 | 1682 | 163 | 532.100 | 374.000 | 1671 | 0 | 0 | 0 | 0 | 0 | 0 |

## Truncation Or Empty-Output Flags
- The cases below are heuristic flags based on empty outputs, empty or very short extracted code, unclosed Markdown fences, or raw outputs whose character length is near the generation cap.
| model | condition | example_id | raw_output_len_chars | extracted_code_len_chars | flags |
| --- | --- | --- | --- | --- | --- |
| deepseek-coder:6.7b | no_review | crn-002192 | 1900 | 1900 | unclosed_code_fence;near_num_predict_char_risk |
| deepseek-coder:6.7b | gold_location | crn-002192 | 1728 | 1659 | unclosed_code_fence |
| deepseek-coder:6.7b | gold_location | crn-008823 | 216 | 216 | unclosed_code_fence |

## Research Message
Review comments and gold location information can change model repair behavior, but improvements in location overlap do not necessarily convert into exact repair success. The tables above therefore keep model-specific condition comparisons and gain estimates together.
