# Length And Complexity Analysis

Rows are quartile bins per model and feature. Delta columns are `gold_location - direct`.

## Qwen 32B Focus Features
| model | feature | bin | n | value_min | value_max | direct_exact | gold_location_exact | gold_minus_direct_exact | direct_location_f1 | gold_location_location_f1 | gold_minus_direct_location_f1 | direct_correct_gold_wrong_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qwen2.5-coder:32b | old_snippet_line_count | q4_gt_11 | 3383 | 12 | 44 | 0.0544 | 0.0417 | -0.0127 | 0.6362 | 0.7270 | 0.0908 | 0.0296 |
| qwen2.5-coder:32b | old_snippet_line_count | q3_8_to_11 | 3176 | 9 | 11 | 0.0853 | 0.0542 | -0.0312 | 0.6546 | 0.7315 | 0.0770 | 0.0532 |
| qwen2.5-coder:32b | old_snippet_line_count | q1_le_8 | 8296 | 3 | 8 | 0.1615 | 0.0371 | -0.1244 | 0.6593 | 0.6782 | 0.0189 | 0.1393 |
| qwen2.5-coder:32b | number_changed_spans | q4_gt_1 | 3613 | 2.0000 | 10.0000 | 0.0246 | 0.0122 | -0.0125 | 0.5957 | 0.6762 | 0.0805 | 0.0172 |
| qwen2.5-coder:32b | number_changed_spans | q1_le_1 | 11242 | 1.0000 | 1.0000 | 0.1518 | 0.0513 | -0.1004 | 0.6714 | 0.7086 | 0.0371 | 0.1212 |
| qwen2.5-coder:32b | number_changed_lines | q4_gt_3 | 2831 | 4.0000 | 20.0000 | 0.0650 | 0.0555 | -0.0095 | 0.6612 | 0.7618 | 0.1006 | 0.0325 |
| qwen2.5-coder:32b | number_changed_lines | q3_1_to_3 | 3947 | 2.0000 | 3.0000 | 0.0697 | 0.0418 | -0.0279 | 0.6310 | 0.7018 | 0.0707 | 0.0456 |
| qwen2.5-coder:32b | number_changed_lines | q1_le_1 | 8077 | 1.0000 | 1.0000 | 0.1654 | 0.0370 | -0.1284 | 0.6609 | 0.6788 | 0.0178 | 0.1428 |
| qwen2.5-coder:32b | gold_location_output_line_count | q4_gt_10 | 3669 | 11 | 74 | 0.0218 | 0.0055 | -0.0164 | 0.5934 | 0.6841 | 0.0907 | 0.0183 |
| qwen2.5-coder:32b | gold_location_output_line_count | q3_8_to_10 | 2490 | 9 | 10 | 0.0482 | 0.0052 | -0.0430 | 0.6227 | 0.6986 | 0.0758 | 0.0454 |
| qwen2.5-coder:32b | gold_location_output_line_count | q1_le_8 | 8696 | 1 | 8 | 0.1834 | 0.0676 | -0.1158 | 0.6869 | 0.7083 | 0.0214 | 0.1432 |
| qwen2.5-coder:32b | gold_location_output_char_count | q4_gt_473 | 3700 | 474 | 2097 | 0.0554 | 0.0097 | -0.0457 | 0.6345 | 0.7371 | 0.1026 | 0.0492 |
| qwen2.5-coder:32b | gold_location_output_char_count | q1_le_262 | 3754 | 5 | 262 | 0.1641 | 0.0836 | -0.0804 | 0.6145 | 0.6301 | 0.0156 | 0.1188 |
| qwen2.5-coder:32b | gold_location_output_char_count | q3_353_to_473 | 3717 | 354 | 473 | 0.1103 | 0.0261 | -0.0842 | 0.6817 | 0.7363 | 0.0546 | 0.0936 |
| qwen2.5-coder:32b | gold_location_output_char_count | q2_262_to_353 | 3684 | 263 | 353 | 0.1531 | 0.0472 | -0.1059 | 0.6821 | 0.7002 | 0.0181 | 0.1219 |

Full table: `results/tables/table_length_complexity_analysis.csv`.
