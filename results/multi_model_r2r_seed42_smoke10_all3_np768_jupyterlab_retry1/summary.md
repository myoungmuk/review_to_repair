# Multi-Model Review-to-Repair Seed42

## Run
- Started UTC: 2026-04-27T10:19:55.369667+00:00
- Completed UTC: 2026-04-27T10:19:55.406941+00:00
- Data: data/processed/crn_pilot100.jsonl (10 examples from the seed=42 CodeReview-New pilot subset)
- Conditions: no_review, direct, gold_location
- Metrics: exact_match_line_trim, location_overlap_f1
- Models: qwen2.5-coder:7b, deepseek-coder:6.7b, codegemma:7b
- Installed Ollama models observed: codegemma:7b, starcoder2:7b, deepseek-coder:6.7b, qwen2.5-coder:3b, qwen2.5-coder:7b, devstral:24b
- Output root: /home/selab/kmm/review_to_repair_crn/results/multi_model_r2r_seed42_smoke10_all3_np768_jupyterlab_retry1
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
- Smoke test: `python scripts/run_multi_model_r2r.py --limit 10 --output-root results/multi_model_r2r_seed42_smoke10 --resume --continue-on-error --num-predict 768`
- Full run after approval: `python scripts/run_multi_model_r2r.py --output-root results/multi_model_r2r_seed42 --resume --continue-on-error --num-predict 768`

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
| qwen2.5-coder:7b | direct | 10 | 0.100 | 0.439 |
| qwen2.5-coder:7b | gold_location | 10 | 0.000 | 0.943 |
| deepseek-coder:6.7b | no_review | 10 | 0.000 | 0.457 |
| deepseek-coder:6.7b | direct | 10 | 0.000 | 0.500 |
| deepseek-coder:6.7b | gold_location | 10 | 0.000 | 0.483 |
| codegemma:7b | no_review | 10 | 0.000 | 0.776 |
| codegemma:7b | direct | 10 | 0.100 | 0.641 |
| codegemma:7b | gold_location | 10 | 0.000 | 0.873 |

## Gains With Paired Bootstrap 95% CI
| model | comparison | metric | paired_n | gain | ci95_low | ci95_high |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | direct - no_review | exact_match_line_trim | 10 | 0.100 | 0.000 | 0.300 |
| qwen2.5-coder:7b | direct - no_review | location_overlap_f1 | 10 | -0.021 | -0.260 | 0.213 |
| qwen2.5-coder:7b | gold_location - direct | exact_match_line_trim | 10 | -0.100 | -0.300 | 0.000 |
| qwen2.5-coder:7b | gold_location - direct | location_overlap_f1 | 10 | 0.504 | 0.274 | 0.724 |
| deepseek-coder:6.7b | direct - no_review | exact_match_line_trim | 10 | 0.000 | 0.000 | 0.000 |
| deepseek-coder:6.7b | direct - no_review | location_overlap_f1 | 10 | 0.043 | -0.121 | 0.239 |
| deepseek-coder:6.7b | gold_location - direct | exact_match_line_trim | 10 | 0.000 | 0.000 | 0.000 |
| deepseek-coder:6.7b | gold_location - direct | location_overlap_f1 | 10 | -0.017 | -0.147 | 0.106 |
| codegemma:7b | direct - no_review | exact_match_line_trim | 10 | 0.100 | 0.000 | 0.300 |
| codegemma:7b | direct - no_review | location_overlap_f1 | 10 | -0.135 | -0.435 | 0.172 |
| codegemma:7b | gold_location - direct | exact_match_line_trim | 10 | -0.100 | -0.300 | 0.000 |
| codegemma:7b | gold_location - direct | location_overlap_f1 | 10 | 0.231 | -0.039 | 0.507 |
| macro_average | direct - no_review | exact_match_line_trim | 10 | 0.067 | 0.000 | 0.200 |
| macro_average | direct - no_review | location_overlap_f1 | 10 | -0.037 | -0.210 | 0.150 |
| macro_average | gold_location - direct | exact_match_line_trim | 10 | -0.067 | -0.200 | 0.000 |
| macro_average | gold_location - direct | location_overlap_f1 | 10 | 0.239 | 0.069 | 0.417 |

## Paper-Ready Summary Table
| model | no_review_exact | direct_exact | gold_location_exact | no_review_loc_f1 | direct_loc_f1 | gold_location_loc_f1 | direct_minus_no_review_exact | direct_minus_no_review_loc_f1 | gold_location_minus_direct_exact | gold_location_minus_direct_loc_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:7b | 0.000 | 0.100 | 0.000 | 0.460 | 0.439 | 0.943 | 0.100 | -0.021 | -0.100 | 0.504 |
| deepseek-coder:6.7b | 0.000 | 0.000 | 0.000 | 0.457 | 0.500 | 0.483 | 0.000 | 0.043 | 0.000 | -0.017 |
| codegemma:7b | 0.000 | 0.100 | 0.000 | 0.776 | 0.641 | 0.873 | 0.100 | -0.135 | -0.100 | 0.231 |
| macro_average | 0.000 | 0.067 | 0.000 | 0.564 | 0.527 | 0.766 | 0.067 | -0.037 | -0.067 | 0.239 |

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
| qwen2.5-coder:7b | no_review | 10 | 257 | 546.400 | 374.500 | 1660 | 245 | 534.400 | 360.000 | 1649 | 0 | 0 | 0 | 0 | 0 | 0 |
| qwen2.5-coder:7b | direct | 10 | 210 | 538.200 | 375.000 | 1636 | 197 | 526.200 | 365.500 | 1625 | 0 | 0 | 0 | 0 | 0 | 0 |
| qwen2.5-coder:7b | gold_location | 10 | 217 | 586.500 | 420.500 | 1658 | 204 | 533.100 | 369.000 | 1647 | 0 | 0 | 0 | 0 | 0 | 0 |
| deepseek-coder:6.7b | no_review | 10 | 225 | 811.800 | 843.000 | 1369 | 80 | 486.600 | 430.000 | 995 | 0 | 0 | 0 | 0 | 0 | 0 |
| deepseek-coder:6.7b | direct | 10 | 242 | 374.500 | 367.000 | 652 | 235 | 364.900 | 351.000 | 639 | 0 | 0 | 0 | 0 | 0 | 0 |
| deepseek-coder:6.7b | gold_location | 10 | 216 | 517.300 | 347.500 | 1745 | 216 | 472.900 | 327.500 | 1664 | 0 | 0 | 0 | 1 | 0 | 1 |
| codegemma:7b | no_review | 10 | 263 | 566.900 | 370.500 | 1672 | 250 | 554.900 | 360.000 | 1661 | 0 | 0 | 0 | 0 | 0 | 0 |
| codegemma:7b | direct | 10 | 176 | 556.800 | 424.500 | 1689 | 163 | 544.800 | 414.000 | 1678 | 0 | 0 | 0 | 0 | 0 | 0 |
| codegemma:7b | gold_location | 10 | 176 | 543.000 | 386.500 | 1680 | 163 | 531.000 | 374.000 | 1669 | 0 | 0 | 0 | 0 | 0 | 0 |

## Truncation Or Empty-Output Flags
- The cases below are heuristic flags based on empty outputs, empty or very short extracted code, unclosed Markdown fences, or raw outputs whose character length is near the generation cap.
| model | condition | example_id | raw_output_len_chars | extracted_code_len_chars | flags |
| --- | --- | --- | --- | --- | --- |
| deepseek-coder:6.7b | gold_location | crn-008823 | 216 | 216 | unclosed_code_fence |

## Research Message
Review comments and gold location information can change model repair behavior, but improvements in location overlap do not necessarily convert into exact repair success. The tables above therefore keep model-specific condition comparisons and gain estimates together.
