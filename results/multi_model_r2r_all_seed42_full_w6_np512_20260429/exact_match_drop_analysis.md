# Exact Match Drop Analysis

- Comparison: `gold_location - direct`
- Metric: `exact_match_line_trim`
- Scope: paired valid evaluations only.
- Interpretation: these are diagnostic correlates of 1->0 exact-match regressions, not causal proof.

## Exact-Match Transitions
| model | paired_n | both_exact | direct_only_exact | gold_location_only_exact | neither_exact | net_exact_delta_count | net_exact_delta_pct | regression_count | regression_pct_of_pairs |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deepseek-coder:6.7b | 14855 | 19 | 87 | 73 | 14676 | -14 | -0.094 | 87 | 0.586 |
| qwen2.5-coder:7b | 14855 | 413 | 933 | 577 | 12932 | -356 | -2.396 | 933 | 6.281 |

## Regression Breakdown: location_delta_bin
| model | value | n | pct_of_regressions |
| --- | --- | --- | --- |
| deepseek-coder:6.7b | location_unchanged | 44 | 50.575 |
| deepseek-coder:6.7b | location_worsened | 42 | 48.276 |
| deepseek-coder:6.7b | location_improved | 1 | 1.149 |
| qwen2.5-coder:7b | location_unchanged | 754 | 80.815 |
| qwen2.5-coder:7b | location_worsened | 162 | 17.363 |
| qwen2.5-coder:7b | location_improved | 17 | 1.822 |

## Regression Breakdown: gold_location_f1_bin
| model | value | n | pct_of_regressions |
| --- | --- | --- | --- |
| deepseek-coder:6.7b | perfect_location_f1 | 39 | 44.828 |
| deepseek-coder:6.7b | medium_location_f1 | 30 | 34.483 |
| deepseek-coder:6.7b | low_location_f1 | 13 | 14.943 |
| deepseek-coder:6.7b | high_location_f1 | 3 | 3.448 |
| deepseek-coder:6.7b | zero_location_f1 | 2 | 2.299 |
| qwen2.5-coder:7b | perfect_location_f1 | 611 | 65.488 |
| qwen2.5-coder:7b | medium_location_f1 | 216 | 23.151 |
| qwen2.5-coder:7b | low_location_f1 | 72 | 7.717 |
| qwen2.5-coder:7b | high_location_f1 | 27 | 2.894 |
| qwen2.5-coder:7b | zero_location_f1 | 7 | 0.750 |

## Regression Breakdown: changed_line_relation
| model | value | n | pct_of_regressions |
| --- | --- | --- | --- |
| deepseek-coder:6.7b | over_edit_superset_of_gold_lines | 45 | 51.724 |
| deepseek-coder:6.7b | right_location_wrong_content | 39 | 44.828 |
| deepseek-coder:6.7b | no_change_from_old | 1 | 1.149 |
| deepseek-coder:6.7b | partial_overlap_wrong_or_missing_lines | 1 | 1.149 |
| deepseek-coder:6.7b | wrong_changed_lines | 1 | 1.149 |
| qwen2.5-coder:7b | right_location_wrong_content | 611 | 65.488 |
| qwen2.5-coder:7b | over_edit_superset_of_gold_lines | 298 | 31.940 |
| qwen2.5-coder:7b | partial_overlap_wrong_or_missing_lines | 9 | 0.965 |
| qwen2.5-coder:7b | under_edit_subset_of_gold_lines | 8 | 0.857 |
| qwen2.5-coder:7b | no_change_from_old | 5 | 0.536 |
| qwen2.5-coder:7b | wrong_changed_lines | 2 | 0.214 |

## Regression Breakdown: prediction_length_bin
| model | value | n | pct_of_regressions |
| --- | --- | --- | --- |
| deepseek-coder:6.7b | similar_0.8x_1.2x | 81 | 93.103 |
| deepseek-coder:6.7b | longer_1.2x_1.5x | 3 | 3.448 |
| deepseek-coder:6.7b | shorter_0.5x_0.8x | 2 | 2.299 |
| deepseek-coder:6.7b | much_longer_gt_1.5x | 1 | 1.149 |
| qwen2.5-coder:7b | similar_0.8x_1.2x | 840 | 90.032 |
| qwen2.5-coder:7b | longer_1.2x_1.5x | 46 | 4.930 |
| qwen2.5-coder:7b | much_shorter_lt_0.5x | 24 | 2.572 |
| qwen2.5-coder:7b | shorter_0.5x_0.8x | 17 | 1.822 |
| qwen2.5-coder:7b | much_longer_gt_1.5x | 6 | 0.643 |

## Regression Breakdown: gold_output_warning
| model | value | n | pct_of_regressions |
| --- | --- | --- | --- |
| deepseek-coder:6.7b | extracted_from_code_fence | 86 | 98.851 |
| deepseek-coder:6.7b | no_code_fence_used_raw_text | 1 | 1.149 |
| qwen2.5-coder:7b | extracted_from_code_fence | 933 | 100.000 |

## Regression Breakdown: change_complexity
| model | value | n | pct_of_regressions |
| --- | --- | --- | --- |
| deepseek-coder:6.7b | tiny_1_line | 76 | 87.356 |
| deepseek-coder:6.7b | small_2_3_lines | 8 | 9.195 |
| deepseek-coder:6.7b | medium_4_8_lines | 3 | 3.448 |
| qwen2.5-coder:7b | tiny_1_line | 812 | 87.031 |
| qwen2.5-coder:7b | small_2_3_lines | 96 | 10.289 |
| qwen2.5-coder:7b | medium_4_8_lines | 21 | 2.251 |
| qwen2.5-coder:7b | large_9plus_lines | 4 | 0.429 |

## Regression Breakdown: language
| model | value | n | pct_of_regressions |
| --- | --- | --- | --- |
| deepseek-coder:6.7b | python | 19 | 21.839 |
| deepseek-coder:6.7b | go | 18 | 20.690 |
| deepseek-coder:6.7b | kotlin | 11 | 12.644 |
| deepseek-coder:6.7b | csharp | 7 | 8.046 |
| deepseek-coder:6.7b | ruby | 7 | 8.046 |
| deepseek-coder:6.7b | javascript | 5 | 5.747 |
| deepseek-coder:6.7b | scala | 5 | 5.747 |
| deepseek-coder:6.7b | swift | 5 | 5.747 |
| deepseek-coder:6.7b | java | 3 | 3.448 |
| deepseek-coder:6.7b | c | 2 | 2.299 |
| deepseek-coder:6.7b | perl | 2 | 2.299 |
| deepseek-coder:6.7b | r | 2 | 2.299 |
| deepseek-coder:6.7b | cpp | 1 | 1.149 |
| qwen2.5-coder:7b | python | 156 | 16.720 |
| qwen2.5-coder:7b | go | 148 | 15.863 |
| qwen2.5-coder:7b | java | 112 | 12.004 |
| qwen2.5-coder:7b | kotlin | 106 | 11.361 |
| qwen2.5-coder:7b | r | 70 | 7.503 |
| qwen2.5-coder:7b | scala | 69 | 7.395 |
| qwen2.5-coder:7b | csharp | 46 | 4.930 |
| qwen2.5-coder:7b | swift | 44 | 4.716 |
| qwen2.5-coder:7b | cpp | 43 | 4.609 |
| qwen2.5-coder:7b | php | 41 | 4.394 |
| qwen2.5-coder:7b | ruby | 31 | 3.323 |
| qwen2.5-coder:7b | c | 28 | 3.001 |
| qwen2.5-coder:7b | javascript | 24 | 2.572 |
| qwen2.5-coder:7b | perl | 9 | 0.965 |
| qwen2.5-coder:7b | objective-c | 3 | 0.322 |
| qwen2.5-coder:7b | sql | 3 | 0.322 |
