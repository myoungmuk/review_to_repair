# Multi-Model Review-to-Repair Seed42

## Run
- Started UTC: 2026-05-25T10:27:16.432727+00:00
- Completed UTC: 2026-05-25T10:27:48.719694+00:00
- Data: data/processed/crn_all.jsonl (3 examples from the seed=42 CodeReview-New pilot subset)
- Conditions: no_review, direct, gold_location
- Metrics: exact_match_line_trim, location_overlap_f1
- Models: qwen2.5-coder:32b
- Installed Ollama models observed: qwen2.5-coder:32b, codegemma:7b, deepseek-coder:6.7b, qwen2.5-coder:7b
- Output root: /cephfs/lab/users/2022810001/review-to-repair01/results/multi_model_r2r_all_seed42_qwen32b_smoke3_ctx8192
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
- Smoke test: `python scripts/run_multi_model_r2r.py --limit 10 --output-root results/multi_model_r2r_seed42_smoke10 --resume --continue-on-error --num-predict 512`
- Full run after approval: `python scripts/run_multi_model_r2r.py --output-root results/multi_model_r2r_seed42 --resume --continue-on-error --num-predict 512`

## Generation Accounting
| model | condition | selected_examples | existing_rows_reused | legacy_predictions_reused | backend_generations | errors |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:32b | no_review | 3 | 0 | 0 | 3 | 0 |
| qwen2.5-coder:32b | direct | 3 | 0 | 0 | 3 | 0 |
| qwen2.5-coder:32b | gold_location | 3 | 0 | 0 | 3 | 0 |

## Metrics By Model And Condition
| model | condition | n_valid | exact_match_line_trim | location_overlap_f1 |
| --- | --- | --- | --- | --- |
| qwen2.5-coder:32b | no_review | 3 | 0.000 | 0.579 |
| qwen2.5-coder:32b | direct | 3 | 0.333 | 0.669 |
| qwen2.5-coder:32b | gold_location | 3 | 0.000 | 0.820 |

## Gains With Paired Bootstrap 95% CI
| model | comparison | metric | paired_n | gain | ci95_low | ci95_high |
| --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:32b | direct - no_review | exact_match_line_trim | 3 | 0.333 | 0.000 | 1.000 |
| qwen2.5-coder:32b | direct - no_review | location_overlap_f1 | 3 | 0.090 | -0.333 | 0.467 |
| qwen2.5-coder:32b | gold_location - direct | exact_match_line_trim | 3 | -0.333 | -1.000 | 0.000 |
| qwen2.5-coder:32b | gold_location - direct | location_overlap_f1 | 3 | 0.151 | 0.000 | 0.394 |
| macro_average | direct - no_review | exact_match_line_trim | 3 | 0.333 | 0.000 | 1.000 |
| macro_average | direct - no_review | location_overlap_f1 | 3 | 0.090 | -0.333 | 0.467 |
| macro_average | gold_location - direct | exact_match_line_trim | 3 | -0.333 | -1.000 | 0.000 |
| macro_average | gold_location - direct | location_overlap_f1 | 3 | 0.151 | 0.000 | 0.394 |

## Paper-Ready Summary Table
| model | no_review_exact | direct_exact | gold_location_exact | no_review_loc_f1 | direct_loc_f1 | gold_location_loc_f1 | direct_minus_no_review_exact | direct_minus_no_review_loc_f1 | gold_location_minus_direct_exact | gold_location_minus_direct_loc_f1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:32b | 0.000 | 0.333 | 0.000 | 0.579 | 0.669 | 0.820 | 0.333 | 0.090 | -0.333 | 0.151 |
| macro_average | 0.000 | 0.333 | 0.000 | 0.579 | 0.669 | 0.820 | 0.333 | 0.090 | -0.333 | 0.151 |

## Integrity
| model | condition | expected_count | output_count | missing_example_id_count | duplicate_example_id_count | generation_error_count | extraction_failure_count | evaluation_failure_count | valid_evaluation_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:32b | no_review | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 3 |
| qwen2.5-coder:32b | direct | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 3 |
| qwen2.5-coder:32b | gold_location | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 3 |

## Output Length And Truncation Diagnostics
| model | condition | n_output | raw_len_min | raw_len_mean | raw_len_median | raw_len_max | extracted_len_min | extracted_len_mean | extracted_len_median | extracted_len_max | empty_raw_count | empty_extracted_count | very_short_extracted_count | unclosed_code_fence_count | near_num_predict_char_risk_count | suspicious_case_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:32b | no_review | 3 | 250 | 987.000 | 954.000 | 1757 | 126 | 393.000 | 390.000 | 663 | 0 | 0 | 0 | 1 | 0 | 1 |
| qwen2.5-coder:32b | direct | 3 | 164 | 463.333 | 421.000 | 805 | 150 | 442.667 | 406.000 | 772 | 0 | 0 | 0 | 0 | 0 | 0 |
| qwen2.5-coder:32b | gold_location | 3 | 162 | 454.000 | 422.000 | 778 | 148 | 440.667 | 407.000 | 767 | 0 | 0 | 0 | 0 | 0 | 0 |

## Truncation Or Empty-Output Flags
- The cases below are heuristic flags based on empty outputs, empty or very short extracted code, unclosed Markdown fences, or raw outputs whose character length is near the generation cap.
| model | condition | example_id | raw_output_len_chars | extracted_code_len_chars | flags |
| --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:32b | no_review | crn-002324 | 1757 | 663 | unclosed_code_fence |

## Research Message
Review comments and gold location information can change model repair behavior, but improvements in location overlap do not necessarily convert into exact repair success. The tables above therefore keep model-specific condition comparisons and gain estimates together.
